from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'toolkit'))
from sprite_lab import History,project_hash,render_frame,validate_project

def a(p):return np.array(Image.open(p).convert('RGBA'))
def image(arr):return Image.fromarray(arr.astype('uint8'),'RGBA')
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def poly(points):
    m=Image.new('L',(128,128));ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ['masks','maps','se-pilot','rear-preview']:(ROOT/name).mkdir(exist_ok=True)

upper=a(ROOT/'inputs'/'se-upper-source.png')
armdonor=a(ROOT/'inputs'/'se-whole-arm-donor.png')
yy,xx=np.mgrid[:128,:128]
near=poly([(35,62),(47,63),(50,68),(49,74),(47,80),(45,85),(42,89),(34,89),(29,86),(27,81),(28,75),(31,68)])
far=poly([(80,62),(89,62),(95,66),(99,71),(100,77),(96,81),(88,83),(83,79),(80,74),(79,69)])
torso=(upper[:,:,3]>0)&~near&~far
# The legacy nominal upper contains a thin former waist/guard fragment here.
# It has explicit empty-space ownership, rather than being frozen as torso.
torso&=~((xx>=80)&(yy>=80))
for name,m in [('near-complete-forearm',near),('far-complete-forearm',far),('fixed-torso-shoulders',torso)]:Image.fromarray((m*255).astype('uint8')).save(ROOT/'masks'/f'{name}.png')

allcandidates=[];sources=[];maprecords=[]
def se_pilot(i):
    low=a(ROOT/'inputs'/'se'/f'lower-{i:02}.png')
    # Former raw guard fragments at the right waist belong to the old arm,
    # including transparent contour ownership. They are never a leg/accessory.
    c=low[:,:,:3].astype(int)
    oldremnant=(xx>=80)&(yy<=86)&(c[:,:,0]>c[:,:,1]+8)&(c[:,:,1]>c[:,:,2]+4)
    low[oldremnant]=0
    Image.fromarray((oldremnant*255).astype('uint8')).save(ROOT/'masks'/f'se-{i:02}-removed-old-waist-arm.png')
    canvas=np.zeros((128,128,4),dtype='uint8');owner=np.full((128,128),-1,dtype='int16');xy=np.full((128,128,2),-1,dtype='int16')
    # New cloth behind source-visible hip pockets. It does not repaint boots.
    cap=poly([(48,79),(76,79),(80,83),(80,87),(75,92),(66,93),(58,91),(49,88)])
    canvas[cap]=[40,40,42,255];owner[cap]=-2
    def over(arr,mask,sourceid,dx=0,dy=0,transparent_owner=False):
        ys,xs=np.where(mask if transparent_owner else mask&(arr[:,:,3]>0))
        for sy,sx in zip(ys,xs):
            tx,ty=int(sx)+dx,int(sy)+dy
            if 0<=tx<128 and 0<=ty<128:
                canvas[ty,tx]=arr[sy,sx];owner[ty,tx]=sourceid;xy[ty,tx]=[sx,sy]
    over(low,low[:,:,3]>0,i)
    bob=[0,1,1,0,0,1,1,0][i]
    dx=[1,1,0,-1,-1,-1,0,1][i]
    over(upper,torso,8,0,bob);over(armdonor,near,9,dx,bob,True);over(armdonor,far,9,-dx,bob,True)
    # Literal existing upper-arm rows under the moved socket. These are source
    # paint only; missing hidden cloth remains the explicit new gray cap above.
    for mask,move in [(near,dx),(far,-dx)]:
        for sy in range(63,68):
            for sx in range(28,101):
                tx,ty=sx+move,sy+bob
                if armdonor[sy,sx,3]>0 and mask[sy,sx] and 0<=tx<128 and canvas[ty,tx,3]==0:
                    canvas[ty,tx]=armdonor[sy,sx];owner[ty,tx]=9;xy[ty,tx]=[sx,sy]
    canvas[canvas[:,:,3]==0]=0
    np.savez_compressed(ROOT/'maps'/f'se-{i:02}.npz',source_id=owner,source_xy=xy)
    return canvas,{'phase':i,'upper_source':'inputs/se-upper-source.png','whole_arm_source':'inputs/se-whole-arm-donor.png','upper_view':'SE','shoulders_chest_fixed':True,'whole_forearm_dx':[dx,-dx],'whole_upper_dy':bob,'removed_old_waist_arm_pixels':int(oldremnant.sum()),'transparent_hand_contour_owned':True,'new_hidden_cloth':[[int(x),int(y)]for y,x in np.argwhere(owner==-2)],'lower_source':f'inputs/se/lower-{i:02}.png'}

# Orange hanging strip from actual Brann rear costume. NE references omitted
# it; this is a declared cardinal-rear paint donor, not a claimed NE source.
tabsource=a(ROOT/'inputs'/'rear-tabard-donor-north00.png')
tabmask=poly([(62,67),(69,67),(73,71),(75,76),(73,79),(67,80),(62,78),(60,74)])
rr,gg,bb=tabsource[:,:,:3].transpose(2,0,1).astype(float)
tabmask&=(rr>gg*1.12)&(gg>bb*1.12)&(tabsource[:,:,3]>0)
tabard=np.zeros((128,128,4),dtype='uint8');tabxy=np.full((128,128,2),-1,dtype='int16')
for ty in range(128):
 for tx in range(128):
    sx=int(np.floor((tx+1-64)/.8+64+.5));sy=ty-2
    if 0<=sx<128 and 0<=sy<128 and tabmask[sy,sx]:tabard[ty,tx]=tabsource[sy,sx];tabxy[ty,tx]=[sx,sy]
Image.fromarray((tabmask*255).astype('uint8')).save(ROOT/'masks'/'actual-tabard-donor-mask.png')
image(tabard).save(ROOT/'masks'/'transported-ne-tabard.png')
np.savez_compressed(ROOT/'maps'/'tabard.npz',source_xy=tabxy)

def rear_preview(i):
    original=a(ROOT/'inputs'/'ne'/f'{i:02}.png');low=a(ROOT/'inputs'/'ne'/f'lower-{i:02}.png')
    oldrgb=original[:,:,:3].astype(int)
    oldneutral=(oldrgb.max(2)-oldrgb.min(2)<18)&(oldrgb.max(2)<100)
    oldwarm=(oldrgb[:,:,0]>oldrgb[:,:,1]+5)&(oldrgb[:,:,1]>oldrgb[:,:,2]+3)
    out=original.copy();notes=[]
    # Accessory is above the existing tunic panel, behind both leg owners.
    tabvisible=(tabard[:,:,3]>0)&(low[:,:,3]==0)
    out[tabvisible]=tabard[tabvisible]
    if i==2:
        # Complete actual supporting lower leg from the good split pose00.
        donor=a(ROOT/'inputs'/'ne'/'00.png')
        sm=poly([(64,81),(78,81),(80,87),(87,92),(88,101),(79,107),(65,107)])
        sourcexy=np.full((128,128,2),-1,dtype='int16');support=np.zeros_like(out)
        for sy,sx in np.argwhere(sm&(donor[:,:,3]>0)):
            # The ENTIRE cuff/calf/boot starts at y88 and is one rigid plateau.
            # Only cloth above it tapers to the hip, avoiding a missing cuff row.
            t=np.clip((sy-80)/8,0,1);tx=int(np.floor(sx+t+.5));ty=int(np.floor(sy+3*t+.5))
            if 0<=tx<128 and 0<=ty<128:support[ty,tx]=donor[sy,sx];sourcexy[ty,tx]=[sx,sy]
        s=support[:,:,3]>0;out[s]=support[s]
        supportboot=s&(yy>=92)
        # Protect the complete original lifted sole/boot in foreground.
        boot=poly([(52,86),(64,86),(70,93),(68,104),(63,109),(54,109),(49,100)])&(original[:,:,3]>0)&(~oldneutral|(yy>=92)|oldwarm)
        out[boot]=original[boot]
        np.savez_compressed(ROOT/'maps'/'ne02-complete-support.npz',source_xy=sourcexy)
        image(support).save(ROOT/'masks'/'ne02-complete-support.png')
        notes.append('Complete same-view NE00 supporting leg copied with rigid +1,+3 boot and tapered proximal displacement; lifted sole restored in foreground.')
    else:
        boot=poly([(65,85),(73,85),(77,89),(78,94),(77,104),(71,108),(63,102),(59,93)])&(original[:,:,3]>0)&(~oldneutral|(yy>=92)|oldwarm)
        supportboot=poly([(49,92),(65,92),(66,108),(50,110)])&(original[:,:,3]>0)
    # Redraw rounded proximal cloth silhouette. Existing boots, warm leather,
    # navy tunic and gold trim remain outside this explicit cloth owner.
    if i==2:
        cloth=poly([(51,79),(64,80),(66,85),(63,91),(59,94),(52,93),(49,89),(49,84)])|poly([(64,80),(74,80),(77,82),(79,84),(80,87),(80,92),(78,95),(71,96),(68,92),(66,88)])
    else:
        cloth=poly([(50,80),(64,80),(66,86),(63,93),(62,98),(51,98),(50,92),(49,86)])|poly([(63,79),(73,79),(77,80),(79,82),(79,84),(78,86),(75,88),(70,90),(66,88)])
    rgb=out[:,:,:3].astype(int)
    neutral=(rgb.max(2)-rgb.min(2)<18)&(rgb.max(2)<100)
    warm=(rgb[:,:,0]>rgb[:,:,1]+8)&(rgb[:,:,1]>rgb[:,:,2]+4)
    # Complete geometric ownership: the former dark-blue tab is deliberately
    # removable. Both actual full boots and warm cuff/hem pixels are protected.
    edit=poly([(47,81),(86,81),(86,95),(47,95)])&~boot&~supportboot&~warm
    erase=edit&~cloth;out[erase]=0
    fill=edit&cloth
    newly_authored=fill&((out[:,:,3]==0)|~neutral)
    out[newly_authored]=[42,42,44,255]
    # Source-shaped subtle volume bands are authored, with stepped rounded ends.
    highlight=poly([(53,83),(59,82),(63,85),(61,90),(57,92),(53,90)]) if i==2 else poly([(67,82),(73,81),(77,83),(78,85),(75,88),(70,90),(67,88)])
    out[(newly_authored if i==2 else fill)&highlight]=[52,52,54,255]
    if i==6:
        small=poly([(68,81),(72,81),(75,82),(74,84),(69,85),(67,84)])
        out[fill&small]=[59,59,60,255]
    crease=poly([(64,84),(66,85),(66,89),(63,92),(62,90)])
    out[fill&crease]=[26,26,29,255]
    # A stepped one-pixel cloth outline follows the newly rounded contour.
    boundary=fill&(~np.roll(cloth,1,axis=1)|~np.roll(cloth,-1,axis=1))
    out[boundary]=[27,27,30,255]
    image(edit.astype('uint8')[:,:,None].repeat(4,axis=2)*255).save(ROOT/'masks'/f'ne{i:02}-proximal-owner.png')
    Image.fromarray((tabvisible*255).astype('uint8')).save(ROOT/'masks'/f'ne{i:02}-visible-tabard-owner.png')
    # Preserve complete foreground boot after cloth replacement.
    out[boot]=original[boot]
    return out,{'phase':i,'preview_only':True,'tabard_source':'actual north00 rear orange strip','tabard_transform':'x about64 scaled0.8 then -1; y+2','tabard_behind_leg_owners':True,'new_cloth_rgba':[[42,42,44,255],[52,52,54,255],[59,59,60,255],[26,26,29,255],[27,27,30,255]],'cloth_owner_points':int(fill.sum()),'actual_changed_rgba_pixels':int(np.count_nonzero(np.any(out!=original,axis=2))),'removed_squared_contour_points':[[int(x),int(y)]for y,x in np.argwhere(erase)],'complete_foreground_boot_preserved':True,'notes':notes}

for i in range(8):
    cand,rec=se_pilot(i);allcandidates.append(cand);sources.append(a(ROOT/'inputs'/'se'/f'{i:02}.png'));maprecords.append({'id':f'se{i}',**rec});image(cand).save(ROOT/'se-pilot'/f'{i:02}.png')
for i in [2,6]:
    cand,rec=rear_preview(i);allcandidates.append(cand);sources.append(a(ROOT/'inputs'/'ne'/f'{i:02}.png'));maprecords.append({'id':f'ne{i}',**rec});image(cand).save(ROOT/'rear-preview'/f'{i:02}.png')

palette=[[0,0,0,0]];idx={(0,0,0,0):0};cels={};frames=[]
for rec,src in zip(maprecords,sources):
    pixels=[]
    for c in src.reshape(-1,4):
        c=tuple(int(v) for v in c)
        if c not in idx:idx[c]=len(palette);palette.append(list(c))
        pixels.append(idx[c])
    k=rec['id'];cels[k]={'layer_id':'paint','pixels':pixels};frames.append({'id':k,'duration_ticks':9,'cels':{'paint':k},'landmarks':{}})
p={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Bounded SE upper pilot and rear defect previews','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'se-pilot','frames':[f'se{i}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'model_calls':0,'status':'pilot only, cold review pending','rear_previews_are_not_completed_loop':True}}
validate_project(p);save(ROOT/'initial-project.json',p);h=History(p)
for rec,src,cand in zip(maprecords,sources,allcandidates):
    operations=[];local={tuple(c):j for j,c in enumerate(h.project['palette'])};points=[]
    for y,x in np.argwhere(np.any(src!=cand,axis=2)):
        c=tuple(int(v) for v in cand[y,x])
        if c not in local:local[c]=len(local);operations.append({'op':'palette_add','rgba':list(c)})
        points.append([int(x),int(y),local[c]])
    operations.append({'op':'paint','cel_id':rec['id'],'points':points,'mask':[[x,y]for x,y,_ in points]})
    h.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(h.project),'reason':'Stable complete source-owned upper construction' if rec['id'].startswith('se') else 'Explicit actual tabard accessory, complete support donor and newly authored rounded proximal cloth','operations':operations})
save(ROOT/'project.json',h.project);save(ROOT/'journal.json',h.journal());save(ROOT/'recipe.json',maprecords)
replayed=History.replay(p,h.journal()).project
for rec,cand in zip(maprecords,allcandidates):assert render_frame(replayed,rec['id']).tobytes()==image(cand).tobytes()
save(ROOT/'receipt.json',{'frames':10,'SE_pilot':8,'rear_preview_only':[2,6],'model_calls':0,'journal_replay_RGBA_exact':True,'project_sha256':project_hash(h.project),'inputs':{p.relative_to(ROOT).as_posix():digest(p)for p in (ROOT/'inputs').rglob('*.png')},'no_art_rating_or_acceptance':True})
print('8 SE pilot frames and 2 rear defect previews, with literal journal replay.')

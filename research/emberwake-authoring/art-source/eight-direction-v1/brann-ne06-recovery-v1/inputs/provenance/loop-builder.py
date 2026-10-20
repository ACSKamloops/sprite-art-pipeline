from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'toolkit'))
from sprite_lab import History,project_hash,render_frame,validate_project
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def png(a,p):Image.fromarray(a.astype('uint8'),'RGBA').save(p)
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for d in ['se','ne','maps','masks']:(ROOT/d).mkdir(exist_ok=True)
tab=arr(ROOT/'inputs'/'transported-ne-tabard.png');nominal=tab[:,:,3]>0
records=[];baselines=[];finals=[]
yy,xx=np.mgrid[:128,:128]
for view in ['se','ne']:
 for i in range(8):
    original=arr(ROOT/'inputs'/view/f'{i:02}.png');out=original.copy()
    sourceid=np.zeros((128,128),dtype='int16');xy=np.stack([xx,yy],axis=-1).astype('int16')
    rec={'view':view,'phase':i,'baseline':f'inputs/{view}/{i:02}.png','baseline_sha256':sha(ROOT/'inputs'/view/f'{i:02}.png')}
    if view=='se':
        allowed=np.array(Image.open(ROOT/'masks'/f'se-{i:02}-extraneous-hem-owner.png'))>0
        removed=allowed&(original[:,:,3]>0)
        # This mask lies below the actual belt and to the right of the orange
        # hanging strip. It replaces only the demonstrated old hem extension.
        orange=(xx>=65)&(xx<=78)&(yy>=69)&(yy<=91)&(original[:,:,0]>100)&(original[:,:,0]>original[:,:,1]*1.3)
        assert not np.any(allowed&orange)
        out[allowed]=0;sourceid[allowed]=-1;xy[allowed]=-1
        assert np.array_equal(out[orange],original[orange])
        # Complete gloves from the pilot remain untouched by this mask.
        assert not np.any(allowed&(xx<50))
        rec.update({'mask':f'masks/se-{i:02}-extraneous-hem-owner.png','operation':'literal transparent contour at x80-89 in rows82-87; frames01-04 only','actual_removed_coordinates':[[int(x),int(y)]for y,x in np.argwhere(removed)],'hanging_orange_strip_exact':True,'contacts_and_boots_unchanged':True})
    else:
        lower=arr(ROOT/'inputs'/'ne'/f'lower-owner-source-{i:02}.png')
        if i in (2,6):
            out=arr(ROOT/'inputs'/f'ne-reviewed-preview-{i:02}.png')
            # Keep the reviewed preview itself, including only its existing
            # source support/cloth corrections; do not invent another pose.
            changed=np.any(out!=original,axis=2);sourceid[changed]=2
            visible=nominal&np.all(out==tab,axis=2)
            legowner=(lower[:,:,3]>0)&(out[:,:,3]>0)&~visible
            # Newly added support/cloth pixels in the preview own this lower
            # area too. This affects only accessory occlusion bookkeeping.
            legowner|=changed&(yy>=81)&(out[:,:,3]>0)&~visible
            rec['pose_source']=f'inputs/ne-reviewed-preview-{i:02}.png'
        else:
            legowner=lower[:,:,3]>0
            visible=nominal&~legowner
            out[visible]=tab[visible]
            assert np.array_equal(out[~visible],original[~visible])
            rec['original_pose_exact_outside_accessory_owner']=True
        sourceid[visible]=1
        tmap=np.load(ROOT/'inputs'/'tabard-source-map.npz')['source_xy'];xy[visible]=tmap[visible]
        for name,m in [('accessory-visible',visible),('accessory-occluded',nominal&~visible),('leg-foreground',legowner)]:Image.fromarray((m*255).astype('uint8')).save(ROOT/'masks'/f'ne-{i:02}-{name}.png')
        rec.update({'accessory_source':'inputs/rear-tabard-donor-north00.png','fixed_accessory_transport':'x about64 scaled0.8 then -1; y+2; unchanged from manual-pilot-v2','actual_visible_accessory_pixels':int(visible.sum()),'accessory_behind_leg_owners':True,'full_original_pose_retained_except_preview02_06_and_accessory':True})
    # All authoritative output transparent pixels use transparent black.
    out[out[:,:,3]==0]=0
    np.savez_compressed(ROOT/'maps'/f'{view}-{i:02}.npz',source_id=sourceid,source_xy=xy)
    changed=np.any(out!=original,axis=2)
    Image.fromarray((changed*255).astype('uint8')).save(ROOT/'masks'/f'{view}-{i:02}-actual-change.png')
    png(out,ROOT/view/f'{i:02}.png');rec.update({'actual_changed_rgba_pixels':int(changed.sum()),'final_sha256':sha(ROOT/view/f'{i:02}.png')})
    records.append(rec);baselines.append(original);finals.append(out)

palette=[[0,0,0,0]];idx={(0,0,0,0):0};cels={};frames=[]
for rec,src in zip(records,baselines):
    points=[]
    for color in src.reshape(-1,4):
        color=tuple(int(v)for v in color)
        if color not in idx:idx[color]=len(palette);palette.append(list(color))
        points.append(idx[color])
    k=f"{rec['view']}{rec['phase']}";cels[k]={'layer_id':'paint','pixels':points};frames.append({'id':k,'duration_ticks':9,'cels':{'paint':k},'landmarks':{}})
p={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Complete SE and NE review loops','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':v,'frames':[f'{v}{i}'for i in range(8)],'fps':160,'loop':True,'events':[]}for v in ['se','ne']],'provenance':{'status':'candidate for review, not selected','model_calls':0,'no_contact_coordinate_changes':True,'SE_source':'manual-pilot-v2 complete-glove loop plus explicit old hem cleanup','NE_source':'original loop with same actual tabard donor, only02/06 preview support/cloth corrections'}}
validate_project(p);save(ROOT/'initial-project.json',p);h=History(p)
for rec,src,out in zip(records,baselines,finals):
    diff=np.any(src!=out,axis=2);pts=np.argwhere(diff)
    if len(pts)==0:continue
    k=f"{rec['view']}{rec['phase']}"
    if rec['view']=='se':
        ops=[{'op':'erase','cel_id':k,'points':[[int(x),int(y)]for y,x in pts],'mask':[[int(x),int(y)]for y,x in pts]}]
        reason='Remove demonstrated old dark hem spur with explicit transparent ownership; belt, full gloves, orange strip, boot and contact coordinates unchanged'
    else:
        local={tuple(c):j for j,c in enumerate(h.project['palette'])};ops=[];points=[]
        for y,x in pts:
            color=tuple(int(v)for v in out[y,x])
            if color not in local:local[color]=len(local);ops.append({'op':'palette_add','rgba':list(color)})
            points.append([int(x),int(y),local[color]])
        ops.append({'op':'paint','cel_id':k,'points':points,'mask':[[x,y]for x,y,_ in points]})
        reason='Copy fixed actual Brann rear tabard behind this pose; apply only the existing source-owned preview02/06 corrections when applicable'
    h.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(h.project),'reason':reason,'operations':ops})
save(ROOT/'project.json',h.project);save(ROOT/'journal.json',h.journal());save(ROOT/'recipe.json',records)
rp=History.replay(p,h.journal()).project;assert project_hash(rp)==project_hash(h.project)
for rec,out in zip(records,finals):assert render_frame(rp,f"{rec['view']}{rec['phase']}").tobytes()==Image.fromarray(out).tobytes()
save(ROOT/'MANIFEST.json',{'status':'review candidate; no visual acceptance','frames':records,'stage':[128,128],'pivot':[64,112],'ticks_per_hold':9,'fps':160,'loop_duration':'9/20','project_sha256':project_hash(h.project),'model_calls':0,'input_hashes':{p.relative_to(ROOT).as_posix():sha(p)for p in (ROOT/'inputs').rglob('*')if p.is_file()}})
print('Complete SE/NE review loops written; sixteen-frame toolkit journal replay exact.')

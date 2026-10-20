#!/usr/bin/env python3
"""Bake explicit complete-leg source maps, then literal underpaint transactions.

This is a two-dimensional painted construction, not inferred anatomy. Native
registration is shared by every cel. Each branch keeps its new whole boot on
a rigid plateau and authors only the missing proximal cloth underneath it.
"""
from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'toolkit'))
from sprite_lab import project_hash,render_frame,History,validate_project,render_cel

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save_json(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def png(a,p):Image.fromarray(a.astype('uint8'),'RGBA').save(p)

# All branch source masks are full native coordinates, including transparent
# areas that remove the former position. They are retained as literal PNGs.
def branch_mask(side,cut=64,top=86,kind='flat'):
    yy,xx=np.mgrid[:128,:128]
    if kind=='se04':cut=np.where(yy<92,61,np.where(yy<97,65,64))
    return ((xx<cut) if side=='left' else (xx>=cut))&(yy>=top)

def inv_shift(mask,dx,dy,plateau,root_y=80):
    # Analytic row-wise inverse. All boot pixels at/below plateau have one
    # integer translation; proximal cloth transitions continuously to the hip.
    yy,xx=np.mgrid[:128,:128];ty=yy+3 # ONE common whole-lower placement: (0,-3).
    a=1+dy/(plateau-root_y)
    if a<=0:raise ValueError('Folded proximal map')
    sy=np.where(ty<root_y,ty,np.where(ty<plateau+dy,(ty+dy*root_y/(plateau-root_y))/a,ty-dy))
    t=np.clip((sy-root_y)/(plateau-root_y),0,1)
    sx=xx-dx*t
    sx=np.floor(sx+.5).astype('int16');sy=np.floor(sy+.5).astype('int16')
    good=(sx>=0)&(sx<128)&(sy>=0)&(sy<128)
    own=np.zeros((128,128),bool);own[good]=mask[sy[good],sx[good]]
    return own,np.stack([sx,sy],axis=-1)

def donor(v,name):return ROOT/'registered'/v/(name+'.png')

def semantic_mask(view,name,part):
    yy,xx=np.mgrid[:128,:128]
    def poly(points):
        im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255)
        return np.array(im)>0
    if view=='se' and name.startswith('corrected'):
        whole=(yy>=86)&(xx>=49)&(xx<=89)
        if part=='all':return whole
        if name=='corrected-04':
            cut=np.where(yy<92,61,np.where(yy<97,65,64))
            return whole&((xx<cut) if part.startswith('left') else (xx>=cut))
        return whole&((xx<64) if part.startswith('left') else (xx>=64))
    if view=='se' and name=='06' and part!='all':
        # Full bent right boot, excluding the planted boot's right edge.
        bent=poly([(67,84),(82,84),(82,92),(76,101),(67,101),(65,95)])
        whole=(yy>=86)&(xx>=47)&(xx<=86)
        return whole&(bent if part.startswith('right') else ~bent)
    if view=='se' and name=='03' and part=='all':
        return (yy>=86)&(xx>=47)&(xx<=90)
    if view=='ne' and name=='00' and part!='all':
        if part.startswith('left'):
            return poly([(47,84),(63,84),(61,95),(57,113),(38,116),(35,108),(40,98),(45,91)])
        return poly([(64,84),(78,84),(80,90),(87,95),(88,103),(79,108),(65,108)])
    if view=='ne' and name=='02' and part!='all':
        return poly([(52,84),(65,84),(70,92),(68,108),(61,115),(53,113),(49,104),(50,94)])
    if view=='ne' and name=='06' and part!='all':
        bent=poly([(63,84),(80,84),(82,94),(77,105),(66,105),(61,95)])
        whole=(yy>=86)&(xx>=46)&(xx<=86)
        return whole&(bent if part.startswith('right') else ~bent)
    return yy>=80

# Source donor, complete semantic branch, dx,dy and rigid-boot plateau start.
# Poses 02/04 in SE are the actual targeted full lower repaint, not a relabel.
SPEC={
 'se':{
  0:[('00','all',0,0,94)],1:[('01','all',0,0,94)],
  2:[('corrected-02','all',0,0,94)],
  3:[('corrected-02','right',-6,-1,96),('corrected-02','left',8,6,89)],
  4:[('corrected-04','all',0,0,94)],
  5:[('corrected-04','left04',8,-3,94),('corrected-04','right04',-10,-1,95)],
  6:[('06','all',0,0,94)],
  7:[('03','all',0,0,94)]},
 'ne':{
  0:[('00','all',0,0,94)],1:[('01','all',0,0,94)],2:[('02','all',0,0,94)],
  3:[('02','left68',2,-4,92),('00','right',-4,4,94)],
  4:[('00','left',11,-8,93),('00','right',-7,8,93)],
  5:[('00','left',8,-2,93),('00','right',-3,3,93)],
  6:[('06','all',0,0,94)],
  7:[('07','all',0,0,94)]}}

# Newly authored hidden cloth (native, before the common -3px lower placement).
# Polygons specify a full hip→knee→cuff branch, never a boot fragment.
CLOTH={
 'se':{
 0:[[(49,81),(62,81),(60,91),(56,96),(46,95),(49,87)],[(63,81),(77,81),(80,96),(68,98),(64,91)]],
 1:[[(49,82),(61,82),(59,91),(56,94),(47,94)],[(63,82),(77,82),(78,97),(66,98)]],
 2:[[(49,82),(61,82),(60,88),(58,91),(49,91)],[(63,82),(79,82),(80,98),(67,98)]],
 3:[[(50,82),(62,82),(67,91),(68,96),(58,97),(55,91)],[(64,82),(77,82),(76,96),(66,97),(65,91)]],
 4:[[(53,82),(67,82),(77,94),(77,99),(65,99),(60,90)],[(64,82),(78,82),(70,93),(64,97),(55,96),(60,89)]],
 5:[[(52,82),(66,82),(69,94),(69,98),(57,98),(56,91)],[(64,82),(78,82),(75,91),(72,95),(62,94),(64,89)]],
 6:[[(52,82),(66,82),(65,97),(52,98)],[(66,82),(80,82),(80,93),(72,96),(66,91)]],
 7:[[(49,82),(62,82),(60,92),(56,97),(46,96)],[(63,82),(77,82),(81,97),(69,99)]]},
 'ne':{
 0:[[(49,79),(64,79),(59,95),(46,96)],[(63,79),(77,79),(80,94),(67,96)]],
 1:[[(49,79),(64,79),(59,95),(47,95)],[(63,79),(77,79),(78,95),(66,97)]],
 2:[[(50,79),(64,79),(64,91),(55,96),(49,91)],[(64,79),(78,79),(75,96),(64,97)]],
 3:[[(50,79),(65,79),(66,87),(62,93),(52,92)],[(63,79),(77,79),(76,98),(64,100)]],
 4:[[(50,79),(65,79),(65,86),(54,88)],[(63,79),(77,79),(73,99),(60,101),(61,91)]],
 5:[[(50,79),(65,79),(62,93),(50,95)],[(63,79),(77,79),(77,96),(64,98)]],
 6:[[(50,79),(65,79),(63,98),(50,99)],[(63,79),(77,79),(81,92),(69,96)]],
 7:[[(49,79),(64,79),(59,95),(46,96)],[(63,79),(77,79),(80,94),(67,96)]]}}

def build_maps(view,out):
    maps=out/'maps';maps.mkdir(parents=True,exist_ok=True)
    initial=[];protected=[];records=[]
    for i in range(8):
        source=rgba(ROOT/'inputs'/view/f'{i:02}.png')
        up=rgba(ROOT/'inputs'/view/f'upper-{i:02}.png')
        yy,xx=np.mgrid[:128,:128]
        allowed=(yy>=80)&(up[:,:,3]==0)
        if view=='ne' and i==3:
            # v7's nominal upper layer included a tiny defective brown lower
            # flap at the left hip. It is now explicitly lower-owned.
            allowed|=(xx>=40)&(xx<=49)&(yy>=78)&(yy<=86)
        Image.fromarray((allowed*255).astype('uint8')).save(maps/f'{i:02}-allowed.png')
        body=source.copy();body[allowed]=0
        result=np.zeros((128,128,4),dtype='uint8')
        owner=np.full((128,128),-1,dtype='int16');xy=np.full((128,128,2),-1,dtype='int16')
        sources=[];branches=[]
        for j,(name,part,dx,dy,plateau) in enumerate(SPEC[view][i]):
            p=donor(view,name);a=rgba(p);sources.append(p.relative_to(ROOT).as_posix())
            sm=semantic_mask(view,name,part)
            own,mp=inv_shift(sm,dx,dy,plateau)
            own&=allowed
            # Transparent texels remain owned, but later foreground paint
            # only occludes earlier branches where its source has alpha.
            active=own.copy();active[own]&=a[mp[:,:,1][own],mp[:,:,0][own],3]>0
            result[active]=a[mp[:,:,1][active],mp[:,:,0][active]]
            owner[active]=j;xy[active]=mp[active]
            Image.fromarray((sm*255).astype('uint8')).save(maps/f'{i:02}-branch-{j}-source-mask.png')
            branches.append({'source':sources[-1],'source_sha256':sha(p),'source_mask':f'{i:02}-branch-{j}-source-mask.png','dx':dx,'dy':dy,'hip_y':80,'rigid_plateau_y':plateau,'order':j})
        np.savez_compressed(maps/f'{i:02}.npz',owner=owner,source_xy=xy)
        png(result,maps/f'{i:02}-mapped.png');png(body,maps/f'{i:02}-body.png')
        save_json(maps/f'{i:02}.json',{'sources':sources,'branches':branches,'common_lower_translation':[0,-3],'no_per_cel_registration':True})
        initial.append(result);protected.append(body);records.append({'phase':i,'map':f'maps/{i:02}.npz','recipe':f'maps/{i:02}.json','sources':sources})
    return initial,protected,records

def project(view,lowers,bodies):
    palette=[[0,0,0,0]];index={(0,0,0,0):0};cels={};frames=[]
    for i,(low,body) in enumerate(zip(lowers,bodies)):
        for layer,arr in [('paint',np.zeros_like(low)),('lower',low),('body',body)]:
            indices=[]
            for c in arr.reshape(-1,4):
                c=tuple(int(k) for k in c)
                if c not in index:index[c]=len(palette);palette.append(list(c))
                indices.append(index[c])
            cels[f'{layer}{i}']={'layer_id':layer,'pixels':indices}
        frames.append({'id':f'f{i}','duration_ticks':9,'cels':{x:f'{x}{i}' for x in ['paint','lower','body']},'landmarks':{}})
    return {'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'New authored hidden charcoal cloth','locked':False},{'id':'lower','name':'Complete generated lower paint and declared source maps','locked':False},{'id':'body','name':'Exact v7 upper/body outside lower ownership','locked':True}],'cels':cels,'frames':frames,'animations':[{'id':'walk','frames':[f'f{i}' for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'view':view,'method':'three built-in ImageGen calls; complete new boots, targeted opposing SE02/04, explicit complete-limb source maps and new literal cloth underpaint','registration':'whole raw sheet nearest grid, then one lower placement 0,-3 for every phase; no per-frame recenter','contact_roles_are_authored_not_certified':True}}

def finish(view,out,lowers,bodies):
    p=project(view,lowers,bodies);validate_project(p);save_json(out/'initial-project.json',p);h=History(p)
    allpts=[]
    # Actual sampled source shades are frozen as literal RGBA in palette ops.
    colors=[(35,35,37,255),(44,44,46,255),(52,52,54,255)]
    ops=[]
    for c in colors:
        if list(c) not in h.project['palette']:ops.append({'op':'palette_add','rgba':list(c)})
    if ops:h.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(h.project),'reason':'Declare three literal charcoal cloth shades for newly authored hidden proximal paint','operations':ops})
    for i in range(8):
        mask=np.array(Image.open(out/'maps'/f'{i:02}-allowed.png'))>0
        art=Image.new('RGBA',(128,128));d=ImageDraw.Draw(art)
        for b,poly in enumerate(CLOTH[view][i]):
            q=[(x,y-3) for x,y in poly]
            d.polygon(q,fill=colors[b%2])
            # One restrained central highlight, confined by the actual polygon.
        a=np.array(art);a[~mask]=0
        # Avoid hard new silhouettes outside complete visible generated paint;
        # only a narrow proximal region is newly authored here.
        a[np.mgrid[:128,:128][0]>=100]=0
        png(a,out/'maps'/f'{i:02}-authored-cloth.png')
        points=[]
        for y,x in zip(*np.where(a[:,:,3]>0)):
            points.append([int(x),int(y),h.project['palette'].index(a[y,x].tolist())])
        if points:
            rec=h.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(h.project),'reason':f'Author complete proximal cloth underpaint in {view}{i:02}: explicit hip/knee/cuff shapes beneath complete new boot paint; hidden cloth is new art','operations':[{'op':'paint','cel_id':f'paint{i}','points':points,'mask':[[x,y] for x,y,_ in points]}]})
        allpts.append({'phase':i,'points':len(points),'polygons_before_common_translation':CLOTH[view][i]})
    if view in ('se','ne'):
        # Literal new brown occlusion underpaint: the complete boots already
        # exist, but their transported anti-aliased boundaries left a light
        # seam. This intentionally overlaps the far boot behind the nearer.
        brown=(61,31,15,255)
        if list(brown) not in h.project['palette']:
            h.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(h.project),'reason':'Declare literal dark leather occlusion shade for full-boot overlap seams','operations':[{'op':'palette_add','rgba':list(brown)}]})
        index=h.project['palette'].index(list(brown))
        seams=({3:[(61,96),(62,98),(63,99),(63,100)]+[(62,y) for y in range(101,108)],4:[(58,y) for y in range(94,97)]+[(57,97),(58,100),(59,102),(60,103)],5:[(62,95),(63,97),(64,98),(64,99)]+[(63,y) for y in range(100,108)]} if view=='ne' else {3:[(68,96),(70,99),(70,100),(70,101),(68,103)],5:[(66,97),(66,98)]})
        for i,pts in seams.items():
            h.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(h.project),'reason':f'New leather underpaint at actual {view.upper()}{i:02} boot-overlap seam; closes source-edge alpha slivers without changing the full boot contour','operations':[{'op':'paint','cel_id':f'paint{i}','points':[[x,y,index] for x,y in pts],'mask':[[x,y] for x,y in pts]}]})
    # Remove faint model fringe only where it forms isolated lower-colored
    # islands; semantic silhouette corrections happen in a later literal pass.
    save_json(out/'cloth-geometry.json',allpts)
    journal=h.journal();save_json(out/'journal.json',journal);save_json(out/'project.json',h.project)
    final_hash=project_hash(h.project)
    for _ in range(h.cursor):h.undo()
    assert project_hash(h.project)==project_hash(p)
    for _ in range(len(h.records)):h.redo()
    assert project_hash(h.project)==final_hash
    replay=History.replay(p,journal);assert project_hash(replay.project)==final_hash
    frames=out/'frames';frames.mkdir(exist_ok=True)
    counts=[]
    for i in range(8):
        im=render_frame(h.project,f'f{i}');im.save(frames/f'{i:02}.png')
        a=np.array(im);old=rgba(ROOT/'inputs'/view/f'{i:02}.png');allowed=np.array(Image.open(out/'maps'/f'{i:02}-allowed.png'))>0
        assert np.array_equal(a[~allowed],old[~allowed])
        assert im.tobytes()==render_frame(replay.project,f'f{i}').tobytes()
        counts.append({'phase':i,'actual_changed_rgba_pixels':int(np.count_nonzero(np.any(a!=old,axis=2))),'outside_mask_exact':True,'frame_sha256':sha(frames/f'{i:02}.png')})
    save_json(out/'receipt.json',{'project_sha256':final_hash,'journal_sha256':sha(out/'journal.json'),'undo_redo_replay':True,'frames':counts,'clock':{'fps':160,'ticks_per_frame':9,'loop_seconds':'9/20'},'quality_status':'Producer candidate; independent cold review pending; no acceptance claimed'})

def main():
    views=sys.argv[1:] or ['se','ne']
    for v in views:
        out=ROOT/v;out.mkdir(exist_ok=True)
        lowers,bodies,rec=build_maps(v,out);save_json(out/'construction.json',rec);finish(v,out,lowers,bodies)
    print(f'Built {8*len(views)} frames; exact protected RGBA, undo/redo and journal replay verified.')
if __name__=='__main__':main()

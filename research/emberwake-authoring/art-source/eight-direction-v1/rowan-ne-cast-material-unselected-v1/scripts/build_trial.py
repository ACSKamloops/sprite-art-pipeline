#!/usr/bin/env python3
"""One frozen, source-colored cuff/elbow shading pass. No geometry operations."""
from pathlib import Path
import copy, hashlib, json, shutil, sys
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from sprite_lab import History, project_hash, render_frame, validate_project

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rawsha(im): return hashlib.sha256(im.tobytes()).hexdigest()
def write(p, obj):
    p.write_text(json.dumps(obj, indent=2) + '\n')

deps = json.loads((ROOT/'dependency-hashes.json').read_text())
for p, digest in deps.items():
    assert sha(p) == digest, f'Changed dependency: {p}'

# Literal source-coordinate sections of the current donor's metal only. The
# wrist/glove edge above row53 and warm wrist trim at source x99+ on row53 stay.
# This mask excludes the leather hand, fingers, outer alpha contour and body.
rows = {
    53:[94,98],54:[93,99],55:[92,100],56:[92,100],57:[91,100],
    58:[91,100],59:[91,99],60:[90,99],61:[89,98],62:[89,98],
    63:[89,98],64:[89,98],65:[89,97],66:[90,97],67:[91,96],68:[92,96],
}
material_source = {(x,y) for y,(a,b) in rows.items() for x in range(a,b+1)}
reference = Image.open(ROOT/'inputs/current/19.png').convert('RGBA')
donor = Image.open(ROOT/'inputs/00-cast-prep.png').convert('RGBA')
# Every output color is an actual unchanged release19 metal source texel.
swatch_xy = [(89,54),(84,52),(84,55),(84,54),(87,48),(87,49),(88,50),(88,51),(88,52)]
swatches = [reference.getpixel(xy) for xy in swatch_xy]
swatch_luma = [sum(c[:3])/3 for c in swatches]
plan = {'schema':'emberwake-source-color-material-pass/v1',
        'scope':'Only northeast17/18 donor metal cuff and elbow; no spatial operation',
        'material_source_rows_inclusive':rows,
        'source_swatch_file':'inputs/current/19.png',
        'source_swatch_png_sha256':sha(ROOT/'inputs/current/19.png'),
        'source_swatches':[{'at':list(xy),'rgba':list(c)} for xy,c in zip(swatch_xy,swatches)],
        'rules':'Within literal donor metal rows and current donor ownership: preserve alpha!=255; shade neutral pixels only above luma150; shade warm elbow pixels at source y>=60 and x<=97 with R-B>25 and G-B>15. Target luma neutral=0.78*old luma, warm elbow=0.78*old luma-5; nearest listed release19 grey source swatch. No edge, topology or position change.',
        'frames':[]}

images = {n:Image.open(ROOT/'inputs/current'/f'{n}.png').convert('RGBA') for n in [17,18,19]}
palette = [[0,0,0,0]]
index = {(0,0,0,0):0}
def pi(rgba):
    rgba=tuple(rgba)
    if rgba not in index:
        index[rgba]=len(palette);palette.append(list(rgba))
    return index[rgba]
for im in images.values():
    for rgba in im.getdata(): pi(rgba)
for c in swatches: pi(c)
project = {'schema':'sprite-edit-project/v1',
    'canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},
    'palette':palette,
    'layers':[{'id':'protected','name':'Exact current outside metal owner','locked':True},
              {'id':'metal','name':'Explicit current donor metal owner','locked':False}],
    'cels':{},'frames':[],
    'animations':[{'id':'ne-cast-17-18-19-excerpt','frames':['17','18','19'],
                   'fps':1000,'loop':False,'events':[]}],
    'provenance':{'scope':'Material experiment only; no editor, full bank, engine or art score',
                  'original_holds_ms':[80,100,80], 'dependency_hashes':'../dependency-hashes.json'}}
witnesses=[]
material_masks={}
ops=[]
for n,hold in [(17,80),(18,100),(19,80)]:
    src=np.array(images[n]); material=np.zeros((128,128),bool)
    points=[]; framew=[]
    if n != 19:
        z=np.load(ROOT/'inputs/maps'/f'northeast-{n}-source-map.npz')
        for y,x in np.argwhere(z['source_kind']==2):
            sx,sy=map(int,z['source_xy'][y,x])
            if (sx,sy) not in material_source: continue
            assert tuple(src[y,x]) == donor.getpixel((sx,sy))
            material[y,x]=True
            r,g,b,a=map(int,src[y,x]); lum=(r+g+b)/3
            warm=sy>=60 and sx<=97 and r-b>25 and g-b>15
            if a!=255 or not(warm or lum>150):continue
            target=.78*lum-(5 if warm else 0)
            k=min(range(len(swatches)),key=lambda i:abs(swatch_luma[i]-target))
            color=swatches[k]
            if tuple(src[y,x])==color:continue
            points.append([int(x),int(y),pi(color)])
            framew.append({'at':[int(x),int(y)],'before_rgba':list(map(int,src[y,x])),
                           'donor_source_xy':[sx,sy], 'source_at':list(swatch_xy[k]),
                           'source_rgba':list(color),'material':'gold elbow' if warm else 'pale cuff/elbow highlight'})
        Image.fromarray((material*255).astype('uint8')).save(ROOT/'masks'/f'{n}-metal-owner.png')
        changed=np.zeros((128,128),dtype=np.uint8)
        for x,y,c in points:changed[y,x]=255
        Image.fromarray(changed).save(ROOT/'masks'/f'{n}-actual-paint.png')
        Image.fromarray(((z['source_kind']==2)&~material).astype('uint8')*255).save(ROOT/'masks'/f'{n}-protected-donor-hand-and-other.png')
        ops.append({'op':'paint','cel_id':f'metal-{n}','mask':[[int(x),int(y)] for y,x in np.argwhere(material)],'points':points})
        witnesses.extend({'frame':n,**w} for w in framew)
        plan['frames'].append({'frame':n,'material_owner_pixels':int(material.sum()),'changed_pixels':len(points),'points':framew})
    protected=[];metal=[]
    for y in range(128):
        for x in range(128):
            p=pi(src[y,x]);protected.append(0 if material[y,x] else p);metal.append(p if material[y,x] else 0)
    project['cels'][f'protected-{n}']={'layer_id':'protected','pixels':protected}
    project['cels'][f'metal-{n}']={'layer_id':'metal','pixels':metal}
    project['frames'].append({'id':str(n),'duration_ticks':hold,'cels':{'protected':f'protected-{n}','metal':f'metal-{n}'},'landmarks':{}})
    material_masks[n]=material
validate_project(project)
for n in [17,18,19]:assert render_frame(project,str(n)).tobytes()==images[n].tobytes()
initial=copy.deepcopy(project); history=History(initial)
receipt=history.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(initial),
 'reason':'Single conservative source-colored grey shading pass on explicitly isolated current17/18 metal cuff/elbow to reduce donor material jump into unchanged release19. Geometry and leather hand remain exact.',
 'operations':ops})
after_hash=project_hash(history.project)
assert project_hash(history.undo())==project_hash(initial)
assert project_hash(history.redo())==after_hash
journal=history.journal()
assert project_hash(History.replay(initial,journal).project)==after_hash
write(ROOT/'editable/initial.json',initial);write(ROOT/'editable/project.json',history.project)
write(ROOT/'editable/receipt.json',receipt);write(ROOT/'editable/journal.json',journal)
write(ROOT/'source-color-plan.json',plan);write(ROOT/'source-color-witnesses.json',witnesses)
checks=[]
for n in [17,18,19]:
    trial=render_frame(history.project,str(n));old=np.array(images[n]);new=np.array(trial)
    diff=np.any(old!=new,axis=2);m=material_masks[n]
    assert np.array_equal(old[:,:,3],new[:,:,3])
    assert np.array_equal(old[~m],new[~m])
    assert np.all(new[diff,3]==255)
    if n==19:
        assert not diff.any();shutil.copy2(ROOT/'inputs/current/19.png',ROOT/'trial/19.png')
    else:trial.save(ROOT/'trial'/f'{n}.png')
    ys,xs=np.where(diff)
    checks.append({'frame':n,'actual_changed_rgba_pixels':int(diff.sum()),
      'bounds':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None,
      'alpha_exact':True,'outside_material_exact':True,
      'hand_fingers_and_donor_outside_material_exact':True,'body_exact':True,
      'before_png_sha256':sha(ROOT/'inputs/current'/f'{n}.png'),
      'trial_png_sha256':sha(ROOT/'trial'/f'{n}.png'),
      'before_rgba_sha256':rawsha(images[n]),'trial_rgba_sha256':rawsha(trial)})
write(ROOT/'MECHANICAL-CHECKS.json',{'frames':checks,'project_initial_sha256':project_hash(initial),
 'project_trial_sha256':after_hash,'undo_redo_exact':True,'journal_replay_exact':True,
 'all_dependencies_unchanged':True,'timing_ms':[80,100,80],'release19_png_bytes_exact':True,
 'geometry_operations':0,'new_colors':0,'model_calls':0,
 'limits':'Offline proof only. No full bank/editor/engine/browser integration or art score.'})
print(json.dumps(checks,indent=2))

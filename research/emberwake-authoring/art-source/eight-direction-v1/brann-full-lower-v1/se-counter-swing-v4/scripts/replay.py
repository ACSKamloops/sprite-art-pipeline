from pathlib import Path
import argparse, hashlib, json, sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'toolkit'))
from sprite_lab import History, project_hash, render_frame
def arr(p): return np.array(Image.open(p).convert('RGBA'))
def mask(p): return np.array(Image.open(p))>0
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
if args.output:
    if not args.output.is_absolute() or args.output.exists(): raise SystemExit('Output must be absolute and fresh')
    args.output.mkdir(parents=True)
initial=json.loads((ROOT/'initial-project.json').read_text())
target=json.loads((ROOT/'project.json').read_text())
journal=json.loads((ROOT/'journal.json').read_text())
history=History.replay(initial,journal)
assert project_hash(history.project)==project_hash(target)
donor=arr(ROOT/'inputs'/'whole-arm-donor.png');donor[donor[:,:,3]==0]=0
underpaint=json.loads((ROOT/'UNDERPAINT.json').read_text())
closed=json.loads((ROOT/'inputs'/'closed-slit-source-witnesses.json').read_text())
motion=json.loads((ROOT/'MOTION.json').read_text())
records=[]
for i in range(8):
    control=arr(ROOT/'inputs'/'control'/f'{i:02}.png')
    fixed=mask(ROOT/'masks'/f'{i:02}-fixed-head-pauldron.png')
    old=mask(ROOT/'masks'/f'{i:02}-old-visible-arm.png')
    body=control.copy();body[fixed|old]=0
    bodymap=np.load(ROOT/'maps'/f'{i:02}-body.npz')
    for w in underpaint[i]['literal_body_underpaint_before_arms']:
        x,y=w['destination'];sx,sy=w['source'];c=control[sy,sx]
        assert c.tolist()==w['rgba'] and max(map(int,c[:3]))<=105 and c[3]>=200
        assert body[y,x,3]==0 and not fixed[y,x]
        body[y,x]=c
    for w in closed[i]['literal_source_witnesses']:
        x,y=w['destination']
        if not fixed[y,x]: body[y,x]=control[y,x]
    for w in underpaint[i]['literal_inspected_join_underpaint_before_arms']:
        x,y=w['destination'];sx,sy=w['source'];c=control[sy,sx]
        assert c.tolist()==w['rgba'] and max(map(int,c[:3]))<=105 and c[3]>=200
        assert not fixed[y,x]
        body[y,x]=c
    assert np.array_equal(body,arr(ROOT/'layers'/f'{i:02}-body.png'))
    for y,x in np.argwhere(bodymap['source_role']==1):
        sx,sy=bodymap['source_xy'][y,x]
        assert np.array_equal(body[y,x],control[sy,sx])
    expected=Image.fromarray(body)
    for side in ['far','near']:
        data=np.load(ROOT/'maps'/f'{i:02}-{side}.npz');owner=data['owner'];xy=data['source_xy']
        assert np.array_equal(owner,mask(ROOT/'masks'/f'{i:02}-{side}-transparent-owner.png'))
        limb=np.zeros_like(donor);ys,xs=np.where(owner);sx=xy[ys,xs,0];sy=xy[ys,xs,1]
        assert ((sx>=0)&(sx<128)&(sy>=0)&(sy<128)).all()
        limb[ys,xs]=donor[sy,sx];limb[fixed]=0
        assert np.array_equal(limb,arr(ROOT/'layers'/f'{i:02}-{side}.png'))
        expected.alpha_composite(Image.fromarray(limb))
    foreground=np.zeros_like(control);foreground[fixed]=control[fixed]
    assert np.array_equal(foreground,arr(ROOT/'layers'/f'{i:02}-fixed.png'))
    expected.alpha_composite(Image.fromarray(foreground))
    actual=arr(ROOT/'frames'/f'{i:02}.png')
    assert expected.tobytes()==Image.fromarray(actual).tobytes()
    assert render_frame(initial,f'f{i}').tobytes()==Image.fromarray(control).tobytes()
    assert render_frame(history.project,f'f{i}').tobytes()==expected.tobytes()
    assert np.array_equal(actual[fixed],control[fixed])
    lower=arr(ROOT/'inputs'/f'lower-owner-{i:02}.png')[:,:,3]>0
    boot=lower & (control[:,:,3]>0);boot[:92]=False
    assert np.array_equal(actual[boot],control[boot])
    low_change=np.any(actual!=control,axis=2);low_change[:92]=False
    assert not (low_change & (control[:,:,3]>0)).any()
    low_fringe=[[int(x),int(y),actual[y,x].tolist()] for y,x in np.argwhere(low_change)]
    assert history.project['frames'][i]['duration_ticks']==9
    if args.output:
        expected.save(args.output/f'{i:02}.png')
        assert sha(args.output/f'{i:02}.png')==sha(ROOT/'frames'/f'{i:02}.png')
    records.append({'phase':i,'input_control_sha256':sha(ROOT/'inputs'/'control'/f'{i:02}.png'),'output_png_sha256':sha(ROOT/'frames'/f'{i:02}.png'),'source_maps_layer_recipe_RGBA_exact':True,'fixed_head_pauldron_RGBA_exact':True,'actual_source_boot_contact_RGBA_exact':True,'new_glove_fringe_in_previously_transparent_air_below_row_92':low_fringe,'same_material_hidden_underpaint_pixels':len(underpaint[i]['literal_body_underpaint_before_arms']),'literal_inspected_join_pixels':len(underpaint[i]['literal_inspected_join_underpaint_before_arms']),'lower_source_overlap_coordinates':motion[i]['original_lower_pixels_occluded_by_arms']})
final=project_hash(history.project)
for _ in range(len(history.records)): history.undo()
assert project_hash(history.project)==project_hash(initial)
for _ in range(len(history.records)): history.redo()
assert project_hash(history.project)==final
assert target['animations'][0]['fps']==160
receipt={'frames':records,'project_sha256':final,'undo_redo_replay_exact':True,'clock':'8 x 9/160 seconds; .45 seconds per loop','scope':'One unselected SE arm experiment. Source/layer/editor mechanics only; no anatomy score, continuous-motion acceptance or engine contact certification.'}
if args.output: (args.output/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS: 8/8 source-map and underpaint recipes, actual PNG bytes, fixed head/pauldrons, actual source boot/contact pixels and toolkit undo/redo/replay.')

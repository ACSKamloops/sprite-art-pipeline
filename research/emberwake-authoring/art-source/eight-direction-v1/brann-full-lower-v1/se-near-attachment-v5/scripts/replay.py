from pathlib import Path
import argparse,json,sys,math,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'toolkit'))
from sprite_lab import History,render_frame,project_hash
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p))>0
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source_over(dst,src):
    # Match the documented integer straight-RGBA editor blend exactly.
    # Pillow rounds four translucent cuff-edge red channels differently
    # by1; the guarded editor pixels are authoritative.
    d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);out=d.copy();use=sa>0
    for k in range(3):
        out[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
    out[:,:,3][use]=(n[use]+127)//255
    return out.astype('uint8')
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
if args.output:
    if not args.output.is_absolute()or args.output.exists():raise SystemExit('Output must be absolute and fresh')
    args.output.mkdir(parents=True)
initial=json.loads((ROOT/'initial-project.json').read_text());journal=json.loads((ROOT/'journal.json').read_text());target=json.loads((ROOT/'project.json').read_text());history=History.replay(initial,journal)
assert project_hash(history.project)==project_hash(target)
donor=arr(ROOT/'inputs/whole-arm-donor.png');donor[donor[:,:,3]==0]=0
source_owner=mask(ROOT/'inputs/near-source-owner.png');yy,xx=np.mgrid[:128,:128];source_owner&=yy>=67
records=json.loads((ROOT/'ATTACHMENT.json').read_text());witnesses=json.loads((ROOT/'LITERAL-SLEEVE.json').read_text());v4motion=json.loads((ROOT/'inputs/v4/MOTION.json').read_text())
results=[]
for i in range(8):
    old=arr(ROOT/'inputs/v4/frames'/f'{i:02}.png');fixed=mask(ROOT/'inputs/v4/masks'/f'{i:02}-fixed-head-pauldron.png')
    parts={layer:arr(ROOT/'inputs/v4/layers'/f'{i:02}-{layer}.png')for layer in ['body','far','near','fixed']};parts['sleeve']=np.zeros((128,128,4),dtype='uint8')
    if i in [5,6,7]:
        record=records[i];remove=mask(ROOT/'masks'/f'{i:02}-old-authored-socket-removal.png');oldmap=np.load(ROOT/'inputs/v4/maps'/f'{i:02}-body.npz')
        assert (oldmap['source_role'][remove]==1).all();assert not (remove&fixed).any();parts['body'][remove]=0
        for w in witnesses[i]['literal_sleeve_underpaint_before_complete_rigid_near_part']:
            x,y=w['destination'];sx,sy=w['source'];c=donor[sy,sx]
            assert c.tolist()==w['rgba']and max(map(int,c[:3]))<=105 and c[3]>=200
            assert parts['body'][y,x,3]==0 and not fixed[y,x]
            parts['sleeve'][y,x]=c
        data=np.load(ROOT/'maps'/f'{i:02}-rigid-near.npz');own=data['owner'];xy=data['source_xy'];rigid=np.zeros_like(donor)
        ys,xs=np.where(own);sx=xy[ys,xs,0];sy=xy[ys,xs,1];rigid[ys,xs]=donor[sy,sx];rigid[fixed]=0
        # Recompute the single rigid inverse transform independently from
        # its declared anchor/angle/path; no per-pixel fitting is accepted.
        px,py=record['source_palm_anchor'];dx,dy=record['anchor_translation_from_v4'];bob=record['unchanged_body_bob'];angle=math.radians(record['rotation_degrees_image_clockwise']);c,s=math.cos(angle),math.sin(angle)
        assert [dx,dy]==v4motion[i]['near_translation']and bob==v4motion[i]['body_bob_from_control']
        tx=xx-px-dx;ty=yy-py-dy-bob;sx2=np.floor(c*tx+s*ty+px+.5).astype('int16');sy2=np.floor(-s*tx+c*ty+py+.5).astype('int16')
        valid=(sx2>=0)&(sx2<128)&(sy2>=0)&(sy2<128);own2=np.zeros_like(own);own2[valid]=source_owner[sy2[valid],sx2[valid]]
        assert np.array_equal(own,own2);assert np.array_equal(xy[own],np.stack([sx2,sy2],axis=-1)[own])
        parts['near']=rigid
    expected_array=np.zeros((128,128,4),dtype='uint8')
    for layer in ['body','sleeve','far','near','fixed']:
        assert np.array_equal(parts[layer],arr(ROOT/'layers'/f'{i:02}-{layer}.png'))
        expected_array=source_over(expected_array,parts[layer])
    expected=Image.fromarray(expected_array)
    actual=arr(ROOT/'frames'/f'{i:02}.png');assert expected.tobytes()==Image.fromarray(actual).tobytes()
    assert render_frame(history.project,f'f{i}').tobytes()==expected.tobytes()
    assert render_frame(initial,f'f{i}').tobytes()==Image.fromarray(old).tobytes()
    assert np.array_equal(actual[fixed],old[fixed]);assert np.array_equal(actual[92:],old[92:])
    lower=arr(ROOT/'inputs/lower-owners'/f'{i:02}.png')[:,:,3]>0;assert np.array_equal(actual[lower],old[lower])
    torso=(xx>=51)&(xx<=77)&(yy<=88);assert np.array_equal(actual[torso],old[torso])
    if i not in [5,6,7]:assert np.array_equal(actual,old)
    assert target['frames'][i]['duration_ticks']==9
    if args.output:expected.save(args.output/f'{i:02}.png');assert sha(args.output/f'{i:02}.png')==sha(ROOT/'frames'/f'{i:02}.png')
    results.append({'phase':i,'PNG_sha256':sha(ROOT/'frames'/f'{i:02}.png'),'source_map_and_literal_sleeve_recipe_exact':True,'all_original_lower_owner_pixels_RGBA_exact_v4':True,'fixed_head_pauldron_and_central_torso_RGBA_exact_v4':True,'actual_RGBA_changes':int(np.any(actual!=old,axis=2).sum())})
final=project_hash(history.project)
for _ in range(len(history.records)):history.undo()
assert project_hash(history.project)==project_hash(initial)
for _ in range(len(history.records)):history.redo()
assert project_hash(history.project)==final
assert target['animations'][0]['fps']==160
receipt={'project_sha256':final,'frames':results,'actual_transactions':len(history.records),'guarded_journal_and_actual_undo_redo_exact':True,'clock':'8 x 9/160 seconds; .45 second loop','scope':'SE05–07 near-arm attachment trial only; source mechanics, no art score/acceptance or engine contact certification'}
if args.output:(args.output/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS:8/8 actual source/layer/PNG recipes, rigid palm-anchored maps, all original lower owners, fixed head/pauldrons/central torso, timing and toolkit undo/redo/replay.')

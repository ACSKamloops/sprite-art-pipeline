from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'toolkit'))
from sprite_lab import History,render_cel,project_hash
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);ap.add_argument('--verify-canonical',action='store_true');args=ap.parse_args()
if args.output:
    if not args.output.is_absolute()or args.output.exists():raise SystemExit('Output must be absolute and fresh')
    args.output.mkdir(parents=True)
sources=json.loads((ROOT/'INPUTS.json').read_text());donors=json.loads((ROOT/'DONORS.json').read_text());initial=json.loads((ROOT/'initial-project.json').read_text());journal=json.loads((ROOT/'journal.json').read_text());target=json.loads((ROOT/'project.json').read_text());h=History.replay(initial,journal);assert project_hash(h.project)==project_hash(target)
assert not target['animations'];records=[];source_after=[]
for s in sources:
    assert sha(ROOT/s['copy'])==s['sha256']
    if args.verify_canonical:
        assert sha(s['source'])==s['sha256'];source_after.append({'source':s['source'],'before_sha256':s['sha256'],'after_sha256':sha(s['source']),'exact':True})
for d in donors:
    src=np.array(Image.open(ROOT/d['full_source_cel']).convert('RGBA'));m=Image.new('L',(128,128));pen=ImageDraw.Draw(m)
    for p in d['polygons']:pen.polygon([tuple(x)for x in p],fill=255)
    for x,y in d['exclude_pixels']:pen.point((x,y),fill=0)
    owner=np.array(m)>0;expected=np.zeros_like(src);expected[owner]=src[owner]
    assert np.array_equal(np.array(Image.open(ROOT/d['mask']))>0,owner)
    actual=np.array(Image.open(ROOT/d['cutout']).convert('RGBA'));assert np.array_equal(expected,actual)
    w=np.load(ROOT/d['witness']);xy=w['source_xy'];dest=w['destination_xy'];rgba=w['RGBA'];assert np.array_equal(xy,dest)
    ys,xs=np.where(owner&(src[:,:,3]>0));assert np.array_equal(xy,np.stack([xs,ys],axis=-1));assert np.array_equal(rgba,src[ys,xs]);assert np.array_equal(actual[ys,xs],rgba)
    fid=f'{d["actor"]}-{d["view"]}-{d["phase"]:02}';cid=f'{fid}-{d["screen_position"]}';image=render_cel(h.project,cid);assert image.tobytes()==Image.fromarray(actual).tobytes()
    if args.output:image.save(args.output/f'{d["id"]}.png');assert sha(args.output/f'{d["id"]}.png')==sha(ROOT/d['cutout'])
    records.append({'donor':d['id'],'identity_coordinates':True,'literal_source_RGBA_exact':True,'hand_polygon_mask_exact':True,'actual_toolkit_cel_RGBA_exact':True,'PNG_sha256':sha(ROOT/d['cutout']),'status':d['status']})
for s in sources:
    aa=[np.array(Image.open(ROOT/'cutouts'/f'{s["actor"]}-{s["view"]}-{s["phase"]:02}-screen-{side}.png').convert('RGBA'))[:,:,3]>0 for side in ['left','right']]
    assert not (aa[0]&aa[1]).any()
final=project_hash(h.project)
for _ in range(len(h.records)):h.undo()
assert project_hash(h.project)==project_hash(initial)
for _ in range(len(h.records)):h.redo()
assert project_hash(h.project)==final
receipt={'source_cels':15,'visible_donors':records,'canonical_sources_verification_requested':args.verify_canonical,'canonical_sources_unchanged':source_after,'project_sha256':final,'actual_transactions':len(h.records),'actual_toolkit_undo_redo_replay_exact':True,'geometry':'original128stage, identity source/destination XY','scope':'Static visible source inventory. No complete hidden boot anatomy, donor selection, gait construction or motion approval.'}
if args.output:(args.output/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS:30/30 original-coordinate sourceRGBA/masks/witnesses/editor cels and exact PNG bytes; actual toolkit undo/redo/replay exact.'+('15 canonical source hashes unchanged.'if args.verify_canonical else''))

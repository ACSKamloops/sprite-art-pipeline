from pathlib import Path
from PIL import Image
from fractions import Fraction
from datetime import datetime,timezone
import sys,json,hashlib,numpy as np,importlib.util
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'toolkit'))
from sprite_lab import History,candidate_transaction,render_frame,validate_project,project_hash,canonical_json,export_project,export_ora,import_ora
EDIT=P/'editable';EDIT.mkdir(exist_ok=True);MEDIA=P/'media';MEDIA.mkdir(exist_ok=True);MIN=P/'media-inputs';MIN.mkdir(exist_ok=True)
configs=json.loads((P/'construction-spec.json').read_text())['configs'];holds=[60,80,100,80,80,100];ids=[22,17,18,19,20,22]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for v in ['southeast','northeast']:(P/'candidate'/v/'22.png').write_bytes((P/'inputs/registered'/v/'22.png').read_bytes())
# Editable two-layer project: original outside the union is locked; old/new owned arms occupy the second layer.
project={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':[[0,0,0,0]],'layers':[{'id':'protected','name':'Original protected body','locked':True},{'id':'arms','name':'Explicit owned arm union','locked':False}],'cels':{},'frames':[],'animations':[],'provenance':{'source':'input-hashes.json','spec':'construction-spec.json','maps':'maps/','note':'No invented hidden anatomy: source22 clothed torso underpaint only in explicit old-fist mask.'}}
palette={(0,0,0,0):0}
def indexes(a):
 out=[]
 for px in a.reshape(-1,4):
  t=tuple(int(x) for x in px)
  if t not in palette:palette[t]=len(project['palette']);project['palette'].append(list(t))
  out.append(palette[t])
 return out
masks={}
for v in ['southeast','northeast']:
 for n in [17,18,19,20,22]:
  a=np.array(Image.open(P/'inputs/registered'/v/f'{n:02}.png').convert('RGBA'));mask=np.array(Image.open(P/'maps'/f'{v}-{n:02}-union-mask.png'))>0 if n in [17,18,20] else np.zeros((128,128),bool);masks[v,n]=mask;body=a.copy();body[mask]=0;arm=np.zeros_like(a);arm[mask]=a[mask];key=f'{v}-{n:02}';project['cels'][key+'-body']={'layer_id':'protected','pixels':indexes(body)};project['cels'][key+'-arms']={'layer_id':'arms','pixels':indexes(arm)}
 seq=[]
 for j,(n,ms) in enumerate(zip(ids,holds)):
  fid=f'{v}-{j}';key=f'{v}-{n:02}';project['frames'].append({'id':fid,'duration_ticks':ms,'cels':{'protected':key+'-body','arms':key+'-arms'},'landmarks':{'root':[64,112]}});seq.append(fid)
 project['animations'].append({'id':v+'_cast','frames':seq,'fps':1000,'loop':False,'events':[]})
validate_project(project)
for f in project['frames']:
 v,j=f['id'].rsplit('-',1);n=ids[int(j)];assert render_frame(project,f['id']).tobytes()==Image.open(P/'inputs/registered'/v/f'{n:02}.png').convert('RGBA').tobytes()
(EDIT/'initial.json').write_text(canonical_json(project)+'\n');hist=History(project)
for c in configs:
 v,n=c['view'],c['frame'];mask=masks[v,n];candidate=np.array(Image.open(P/'candidate'/v/f'{n:02}.png').convert('RGBA'));patch=np.zeros_like(candidate);patch[mask]=candidate[mask];ys,xs=np.where(mask);points=[[int(x),int(y)] for x,y in zip(xs,ys)];tx=candidate_transaction(hist.project,f'{v}-{n:02}-arms',Image.fromarray(patch),points,reason=f'{v} source{n}: real donor hand/forearm plus declared source22 underpaint through literal arm union');hist.apply(tx)
finalhash=project_hash(hist.project);(EDIT/'project.json').write_text(canonical_json(hist.project)+'\n');journal=hist.journal();(EDIT/'journal.json').write_text(json.dumps(journal,indent=2)+'\n')
for _ in configs:hist.undo()
assert project_hash(hist.project)==project_hash(project)
for _ in configs:hist.redo()
assert project_hash(hist.project)==finalhash
replayed=History.replay(project,journal);assert project_hash(replayed.project)==finalhash
for f in hist.project['frames']:
 v,j=f['id'].rsplit('-',1);n=ids[int(j)];assert render_frame(hist.project,f['id']).tobytes()==Image.open(P/'candidate'/v/f'{n:02}.png').convert('RGBA').tobytes()
export_project(hist.project,EDIT/'exports',columns=6)
# Lossless layered exchange exercised through the real toolkit adapter; no external editor claim.
ora=EDIT/'northeast-prep17.ora';export_ora(hist.project,'northeast-1',ora);reopened=import_ora(ora);assert project_hash(reopened)==finalhash
(EDIT/'proof.json').write_text(json.dumps({'initial_render_all_original_frames_exact':True,'candidate_render_all_final_frames_exact':True,'all_six_masked_transactions_succeeded':True,'undo_to_initial_exact':True,'redo_to_final_exact':True,'journal_replay_exact':True,'ora_adapter_roundtrip_exact':True,'external_editor_opened':False,'manual_palette_seam_edits':0,'final_project_sha256':finalhash},indent=2)+'\n')
# Exact one-shot media use the existing clocks, with no added padded neutral holds.
spec=importlib.util.spec_from_file_location('exact_apng',P/'tools/exact_apng.py');apng=importlib.util.module_from_spec(spec);spec.loader.exec_module(apng);media=[]
for v in ['southeast','northeast']:
 for variant in ['control','hybrid']:
  fd=MIN/f'{v}-{variant}';fd.mkdir(exist_ok=True);frames=[]
  for j,(n,ms) in enumerate(zip(ids,holds)):
   source=P/('inputs/registered' if variant=='control' else 'candidate')/v/f'{n:02}.png';fp=fd/f'{j:02}.png';fp.write_bytes(source.read_bytes());hold=Fraction(ms,1000);frames.append({'file':fp.name,'sha256':sha(fp),'hold':[hold.numerator,hold.denominator]})
  manifest={'canvas':[128,128],'loop':False,'duration':[1,2],'frames':frames};mp=fd/'manifest.json';mp.write_text(json.dumps(manifest,indent=2)+'\n');dest=MEDIA/f'{v}-{variant}';receipt=apng.convert(mp,dest);media.append({'view':v,'variant':variant,'file':str((dest/'animation.apng.png').relative_to(P)),'receipt':str((dest/'receipt.json').relative_to(P)),'sha256':receipt['output_sha256'],'decoded_rgba_exact':True,'actual_fctl_holds':receipt['verification']['actual_fctl_holds']})
(P/'media-ledger.json').write_text(json.dumps(media,indent=2)+'\n')
# Qualify any progression count; the original17/18 body redraw differences are deliberately retained.
proof=json.loads((P/'proof.json').read_text())
for v,q in proof['prep_progression'].items():q['different_composited_pose_not_repeat']=q.pop('a_different_drawing_not_a_held_repeat');q['note']='Same real donor hand paint translated2px right/1px up with a proximal-map progression, on distinct original17/18 bodies. Full-frame difference count includes the retained original body redraw; it is not new art coverage.'
(P/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
sourceledger=json.loads((P/'input-hashes.json').read_text());alllive=all(sha(Path(x['source']))==x['sha256'] for x in sourceledger);assert alllive
report={'status':'unreviewed hybrid-cast candidate; root owns integration and fresh review','model_calls':0,'new_generated_paint':False,'candidate_frames':['southeast/17','southeast/18','southeast/20','northeast/17','northeast/18','northeast/20'],'release19':'original PNG bytes and old glove socket retained in both views','source22_role':'Explicit clothed torso/background underpaint only in old-fist ownership, never a hidden reconstruction claim.','stage':[128,128],'pivot':[64,112],'clocks_ms':holds,'duration_seconds':.50,'prep_progression':'The complete open hand moves2px right/1px up from17to18; main cuff/hand source texels remain rigid. Small source-mapped proximal changes connect it to the old arm. Recovery uses a relaxed donor glove while retaining the original forearm/body context.','proof':'proof.json','editable_proof':'editable/proof.json','raw_source_map_replay_script':'replay_frozen.py','manual_source_palette_seam_repairs':0,'all_37_live_input_hashes_match':alllive,'observed_limits':['Leading palms are visible outside the torso; the counter hand remains the original closed fist.','Bright donor cuff/gold joint treatment differs from the original; wrist/elbow volume and naturalness require fresh art review.','SE recovery hand overlaps the restored clothed torso/waist; NE recovery relaxes outward/down. This remains a trial, not acceptance.','No human normal-speed playback, game/browser rendering, VFX or controller test.'], 'failed_attempts':['Initial NE recovery proximal controls collapsed map triangles; rejected before that frame was promoted.','First recovery crop clipped the relaxed glove; replaced by a complete measured donor-hand mask.','Second NE recovery erasure left a4pixel old-fist edge at(85..88,60); those exact pixels were added to the old-fist union and restored from source22 transparency.','First SE preparation overlapped several outer hair/face-edge pixels; hand plateau moved3px right while preserving the old proximal anchors.'], 'media':media,'frozen_utc':datetime.now(timezone.utc).isoformat()};(P/'production.json').write_text(json.dumps(report,indent=2)+'\n')
(P/'DELIVERY.md').write_text('''# Rowan hybrid cast — unreviewed delivery

Six candidate frames are in `candidate/{southeast,northeast}/{17,18,20}.png`. Original19 release and22 neutral context are copied beside them without changing their PNG bytes. Root owns integration and the fresh art review; no score is assigned.

Original128-stage body/head/legs and pivot(64,112) remain. Only explicit old-fist and donor hand/forearm union masks change. Every pixel outside that union, including transparency, is exact; every pixel from y84 down through the boots is exact. Source22 supplies clothed torso/background only where an old fist occluded it. It is declared underpaint, not invented hidden anatomy. No model call or new paint was used.

Preparation17→18 moves the complete open donor hand2px right and1px up with a small proximal-map progression. The same real hand paint is reused rigidly, not redrawn; these are different composited poses on the respective original17/18 bodies. NE's palm projects outside the torso. Original release19/socket remain. Recovery20 uses a complete relaxed donor glove. Counter-arms retain their original fists.

`construction-spec.json` declares the literal donor polygons, old-fist polygons, hand/cuff plateaus, proximal controls and offsets. `maps/` retains source/target ownership, source coordinates, frozen triangles and masks. `inputs/` includes original registered bodies, exact raw model returns, native donor PNGs and their maps into those returns. `input-hashes.json` binds all37inputs. `replay_frozen.py` independently checks nested source maps back to raw return pixels and exact outside-mask preservation.

`editable/` contains the initial/final two-layer project, six actual masked-import transactions, receipts and replay journal. The body outside the union is locked; owned arm cells are editable. Undo, redo, journal replay, rendered PNGs and the toolkit ORA roundtrip passed. No external editor was opened. Zero manual source-palette seam edits were needed.

Compare `proofs/{southeast,northeast}-{light,dark}-chronology.png` at native,2x and.66. `media/` holds four exact one-shot control/hybrid APNGs with original60/80/100/80/80/100ms holds (total.50s), rational-delay receipts and decodedRGBA checks. No extra animation frames or timing changes were introduced.

Known limits: donor cuffs/gold elbow detail differ from old armor; SE's relaxed recovery crosses the torso/waist; natural wrist/elbow volume still needs independent review. Final alpha is connected and the source maps replay, which do not establish anatomy or motion quality. No human continuous playback, browser/game test, VFX-origin change or controller acceptance is claimed.

Failed trials are retained. Initial NE recovery controls collapsed a triangle; a first donor mask clipped glove fingers; a later erasure left4old-fist edge pixels; the first SE palm touched outer hair. These were corrected through explicit map/mask/plateau placement changes, with no hidden repaint.

Reproduce into a fresh folder:

```bash
python replay_frozen.py --output /absolute/fresh/replay-folder
```

Read-only verification:

```bash
python replay_frozen.py
sha256sum --check --quiet SHA256SUMS
```

`build_hybrid.py` retains the authoring recipe; frozen maps/triangles are the transport authority. `package_hybrid.py` retains editable/media packaging. Run those only in a disposable copy because their output paths are fixed. Root should provide anonymous paired images/clocks to the next reviewer and withhold this producer history until that report is frozen.
''')
print(json.dumps({'editable_project_sha256':finalhash,'media_count':len(media),'all_live_inputs_match':alllive,'production_json_sha256':sha(P/'production.json'),'delivery_sha256':sha(P/'DELIVERY.md')}))

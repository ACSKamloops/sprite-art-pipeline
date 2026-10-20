import json,hashlib,math
from pathlib import Path
from PIL import Image
B=Path('/home/astra/artifacts/copper-scout-bake-private/grounded-fall-review-v2/first');R=Path('/home/astra/projects/sprite-construction-lab-rig-pilot/pilot/rigged-character');O=Path(__file__).resolve().parent
m=json.loads((B/'manifest.json').read_text());ledger={};checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):ledger[str(p)]={'sha256':sha(p),'bytes':p.stat().st_size}
def check(ok,label):checks.append({'passed':bool(ok),'check':label})
bind(B/'manifest.json')
for n in ['design.json','clips.json','rig.gd']:
 bind(R/n);check(sha(R/n)==m['source_bindings'][n],n+' current rigsource bound to bake')
notes={
'knockdown':{'decision':'approved_prototype_only','observations':['Actual native and2x final pose now rests head/back/hip along the floor rather than suspending the torso behind boots.','Glove silhouettes reach the floor; scarf remains readable and does not visibly rotate belowground in sampled poses.','Fall progresses from supported ready through recoil/compression to grounded rest; prototype motion, not finalproduction biomechanics.'],'required_changes':[]},
'recover':{'decision':'approved_prototype_only','observations':['Opening actual RGBA is byteidentical to final groundedknockdown.','Sampled phases show palmbraced lift, crouched support and neutral settle; the oldunsupportedrest is gone.','Final actualRGBA matches initialneutralready in this same bake.'],'required_changes':[]}}

clips=[]
for name in ['knockdown','recover']:
 for view in ['right']:
  key=name+'/'+view;c=m['clips'][key];atlas=B/c['atlas'];bind(atlas);check(hashlib.sha256(Image.open(atlas).convert('RGBA').tobytes()).hexdigest()==c['atlas_pixel_sha256'],key+' atlas actual RGBA hash')
  frame_bindings=[];sole_rows=[]
  for i,f in enumerate(c['frames']):
   p=B/f['png'];im=Image.open(p).convert('RGBA');h=hashlib.sha256(im.tobytes()).hexdigest();check(h==f['pixel_sha256'],key+f' frame{i} exported actualpixel hash');frame_bindings.append({'frame':i,'png':str(p),'file_sha256':sha(p),'pixel_sha256':h,'phase':f['pose']['phase'],'duration_ticks':f['duration_ticks']});sole_rows.append(im.getchannel('A').getbbox()[3]-1)
  check(sum(f['duration_ticks']for f in c['frames'])==c['duration_ticks'],key+' source tick sum')
  timing=json.loads((O/'timing.json').read_text())[key]
  check(timing['actual_gif_duration_ms']==round(c['duration_ticks']/m['fps']*1000),key+' actual GIF total matches source clock')
  check(c['frames'][-1]['pose']['endpoint']==(not c['loop']),key+' actual lastframe endpoint policy')
  for suffix in ['contact.png','1x.gif','2x.gif']:bind(B/'review'/f'{name}-{view}-{suffix}')
  item={'clip_id':key,**notes[name],'view_scope':'Right authored motion' if view=='right' else 'Explicit mirrored left derivative; contact visually checked, not independent left anatomy/gear authoring.','atlas_sha256':sha(atlas),'atlas_pixel_sha256':c['atlas_pixel_sha256'],'frame_bindings':frame_bindings,'opaque_bottom_row_range':[min(sole_rows),max(sole_rows)],'ground_scope':'Compositeopaque pixels remain abovecontinuousgroundboundary170; finalrest visibly supports torso/hips/palms. Compositecheck does notattributeindividual layerownership.','timing_scope':'GIF time totals verified; eight exported right phases visually sampled and both facing contact strips viewed. No continuous browser playback claim.','collision_windows':None}
  clips.append(item)
fall=m['clips']['knockdown/right']['frames'];rise=m['clips']['recover/right']['frames']
def pixels(f):return Image.open(B/f['png']).convert('RGBA').tobytes()
check(pixels(fall[-1])==pixels(rise[0]),'actual groundedfallfinal equals recoveropening RGBA')
check(pixels(rise[-1])==pixels(fall[0]),'actual recoverneutral equals fallinitialready RGBA')
for c in clips:
    for f in c['frame_bindings']:
        im=Image.open(f['png']).convert('RGBA')
        check(im.getchannel('A').crop((0,170,192,192)).getbbox() is None,c['clip_id']+f' frame{f["frame"]} no belowgroundopaque')
rest=Image.open(B/fall[-1]['png']).convert('RGBA')
support_windows={'front_palm':(68,158,78,170),'pelvis_back':(93,150,105,170),'head_scarf':(52,156,66,170)}
for label,(x0,y0,x1,y1) in support_windows.items():
    check(any(rest.getpixel((x,169))[3] for x in range(x0,x1)),label+' finalrest opaque floorrow in authoredlocal window')
bind(Path(__file__))
bind(O/'timing.json')
for evidence in O.glob('*.png'):bind(evidence)
prior=Path(__file__).resolve().parent.parent/'full-pack/review.json'
bind(prior)
fingerprint=hashlib.sha256(json.dumps(ledger,sort_keys=True,separators=(',',':')).encode()).hexdigest()
r={'schema':'sprite-independent-visual-review/v1','reviewer':'som_animation_decoder independent reviewer','decision':'approved_prototype_only','input_fingerprint':fingerprint,'clip_ids':[c['clip_id']for c in clips],'observations':['Repaired actualgroundedrest and bracedrecovery resolve the fullpackreview supportblocker for these two rightclips.','Original newCopperScout polygons; not a faithful reconstruction of textured AI concept artwork.','Exactly two repaired right-view actions; not finalfull24review or independentleftapproval.','Timing totals and phase1one-shot endpoint verify, while geometry/contact/joint target scores remain separate from actual visual weight and seams.'],'clips':clips,'source_ledger':ledger,'production_quality_approved':False,'previous_review':{'path':str(prior),'sha256':sha(prior),'input_fingerprint':json.loads(prior.read_text())['input_fingerprint'],'decision':'changes_requested','same_hash_approval':False},'technical_binding_checks':checks,'technical_binding_passed':all(x['passed']for x in checks),'visual_sampling':'Fivecontactframes and eightnativephases for eachtwo-right clip; exact2x detail phases; original1xGIF duration metadata. GIF metadata actualdurations checked. No fullframe-by-frame humanview, real-time browser viewing, gameintegration or productionapproval claim.','timing':json.loads((O/'timing.json').read_text()),'limits':['Visual findings are reviewer judgments; quantitative knee/pelvis metadata supports description, not independently reconstructed anatomy.','Composite alpha bottom does not attribute individual boot/contact ownership.','Semantic strike/cast events are authored labels, not native discovered collision intervals.','Prototype approval is not production art approval, fullpack completion or gameplay acceptance.']}
(O/'review.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'decision':r['decision'],'input_fingerprint':fingerprint,'clip_ids':r['clip_ids'],'technical_checks':len(checks),'technical_passed':r['technical_binding_passed']}))

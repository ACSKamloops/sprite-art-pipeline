import json,hashlib,math
from pathlib import Path
from PIL import Image
B=Path('/home/astra/projects/sprite-construction-lab-bake-pilot/pilot/rigged-character/generated');R=Path('/home/astra/projects/sprite-construction-lab-rig-pilot/pilot/rigged-character');O=Path(__file__).resolve().parent
m=json.loads((B/'manifest.json').read_text());ledger={};checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):ledger[str(p)]={'sha256':sha(p),'bytes':p.stat().st_size}
def check(ok,label):checks.append({'passed':bool(ok),'check':label})
bind(B/'manifest.json')
for n in ['design.json','clips.json','rig.gd']:
 bind(R/n);check(sha(R/n)==m['source_bindings'][n],n+' current rigsource bound to bake')
notes={'cast': {'decision': 'approved_prototype_only',
          'observations': ['Two-arm preparation and body lean produce a distinct casting silhouette.',
                           'At revised frames24/48 torso cloth is continuous; the earlier distracting underarm/waist '
                           'pale wedges are no longer exposed. Rear cream glove being behind torso is intentional.',
                           'Frame71 includes phase1endpoint. Effects/emit timing and attack targets require separate '
                           'engine review.'],
          'required_changes': []},
 'hurt': {'decision': 'approved_prototype_only',
          'observations': ['Head, pelvis/support stance and protective arm response now recoil together and return '
                           'through deliberate recovery.',
                           'Readable as a light damage reaction in this pilot. It must not substitute for heavy hit, '
                           'knockdown or death.',
                           'Lastframe35 includes phase1endpoint; no damage collision causality is asserted.'],
          'required_changes': []},
 'idle': {'decision': 'approved_prototype_only',
          'observations': ['Neutral legs are more upright; copper shoulder, teal hood/cloth and gloves remain stable '
                           'in sampled rest poses.',
                           'Subtle breathing/rest is appropriate for this simplified vector prototype; final textured '
                           'identity/material polish remains unreviewed.'],
          'required_changes': []},
 'slash': {'decision': 'approved_prototype_only',
           'observations': ['Overhead preparation transitions into a visibly loaded torso/pelvis lunge and low blade '
                            'follow-through; revised support legs distinguish load from recovery.',
                            'Sampled grip/guard/blade follow the moving hand, and elbow fold remains continuous at '
                            'native and2x views.',
                            'Explicit phase1lastframe settles back to ready; authored strike event is not a collision '
                            'window.'],
           'required_changes': []},
 'walk': {'decision': 'approved_prototype_only',
          'observations': ['Eight native phase samples now separate upright support and bent passing/swing legs, '
                           'correcting the constant crouched shuffle.',
                           'Arms counter-swing near the hips and vary silhouette rather than holding the same forward '
                           'bent rest pose.',
                           'Passing boot overlap remains transient and readable; one-cycle endpoint is the last '
                           'pre-seam sample rather than a duplicate phase1.'],
          'required_changes': []}}
notes.update({
 'run':{'decision':'approved_prototype_only','observations':['Faster stride, higher passing foot and deeper transient compression distinguish run from walk in eight sampled native phases.','Opposed arms and stable materials remain readable at2x; root/world accumulation belongs to engine, not a recentered sprite.'],'required_changes':[]},
 'thrust':{'decision':'approved_prototype_only','observations':['Forward reach and loaded torso distinguish thrust from slash; guard follows hand through sampled extension and recovery.','Last phase1 returns to equipped ready; no collision interval inferred.'],'required_changes':[]},
 'shoot':{'decision':'approved_prototype_only','observations':['Raised orange blaster stays attached to hand and body aim/recoil returns to ready.','This is body/equipment aim-shoot-recovery only: muzzle/projectile/audio effects are separate and untested here.'],'required_changes':[]},
 'charge':{'decision':'approved_prototype_only','observations':['Stable sword-ready charge hold with small body movement; blade/grip and materials remain consistent.','Does not visually encode a rising chargelevel or threshold alone; UI/palette/effect state must provide those meanings separately.'],'required_changes':[]},
 'celebrate':{'decision':'approved_prototype_only','observations':['Raised-arm celebration hold reads clearly and retains stable joints/palette.','This is a restrained held gesture with subtle movement, not an energetic jumping celebration.'],'required_changes':[]},
 'knockdown':{'decision':'changes_requested','observations':['Final body/back and hands are suspended above the floor while only boots contact, so the resting fall lacks credible support.','Final front_hand[74,156]/rear_hand[111,155] end near158/157 while floorboundary170; nearlyhorizontal torso/head remain behind the feet.','Opaque boot-contact and zeroIKerrors do not prove a grounded body-rest pose.'],'required_changes':['Author grounded back/hip or palm support with actual raster contact; avoid fixing semantic torso float by translating only boot soles.','Retain continuity with recover opening and re-review native2x/motion after actual GPU rebake.']},
 'recover':{'decision':'changes_requested','observations':['Opening matches knockdown final pose exactly, preserving transition continuity but inheriting its unsupported torso/hands.','Rise toward neutral is readable in sampled phases; cannot approve recovery from a suspended rest pose.'],'required_changes':['Start from repaired supported knockdown rest; use a readable palm/knee/hip push and settle to neutral.']}
})

clips=[]
for name in ['idle','walk','run','slash','thrust','shoot','charge','cast','hurt','knockdown','recover','celebrate']:
 for view in ['right','left']:
  key=name+'/'+view;c=m['clips'][key];atlas=B/c['atlas'];bind(atlas);check(hashlib.sha256(Image.open(atlas).convert('RGBA').tobytes()).hexdigest()==c['atlas_pixel_sha256'],key+' atlas actual RGBA hash')
  frame_bindings=[];sole_rows=[]
  for i,f in enumerate(c['frames']):
   p=B/f['png'];im=Image.open(p).convert('RGBA');h=hashlib.sha256(im.tobytes()).hexdigest();check(h==f['pixel_sha256'],key+f' frame{i} exported actualpixel hash');frame_bindings.append({'frame':i,'png':str(p),'file_sha256':sha(p),'pixel_sha256':h,'phase':f['pose']['phase'],'duration_ticks':f['duration_ticks']});sole_rows.append(im.getchannel('A').getbbox()[3]-1)
  check(sum(f['duration_ticks']for f in c['frames'])==c['duration_ticks'],key+' source tick sum')
  timing=json.loads((O/'timing.json').read_text())[key]
  check(timing['actual_gif_duration_ms']==round(c['duration_ticks']/m['fps']*1000),key+' actual GIF total matches source clock')
  check(c['frames'][-1]['pose']['endpoint']==(not c['loop']),key+' actual lastframe endpoint policy')
  for suffix in ['contact.png','1x.gif','2x.gif']:bind(B/'review'/f'{name}-{view}-{suffix}')
  item={'clip_id':key,**notes[name],'view_scope':'Right authored motion' if view=='right' else 'Explicit mirrored left derivative; contact visually checked, not independent left anatomy/gear authoring.','atlas_sha256':sha(atlas),'atlas_pixel_sha256':c['atlas_pixel_sha256'],'frame_bindings':frame_bindings,'opaque_bottom_row_range':[min(sole_rows),max(sole_rows)],'ground_scope':'Composite bottom measured perclip; continuous ground boundary170 has planted opaque row169. Run includes airborne phases. Neither this bound nor bootcontact proves supported fallen torso/palms.','timing_scope':'GIF time totals verified; eight exported right phases visually sampled and both facing contact strips viewed. No continuous browser playback claim.','collision_windows':None}
  clips.append(item)
bind(Path(__file__))
bind(O/'timing.json')
for evidence in O.glob('*.png'):bind(evidence)
prior=Path(__file__).resolve().parent.parent/'revised-five/review.json'
bind(prior)
fingerprint=hashlib.sha256(json.dumps(ledger,sort_keys=True,separators=(',',':')).encode()).hexdigest()
r={'schema':'sprite-independent-visual-review/v1','nativeclock_effects_scope':'Authoredevents notnativecollisionwindows; shoot/projectile/castFX/chargelevels separate. Inplacebody loops do not themselves accumulateworld-root displacement.','reviewer':'som_animation_decoder independent reviewer','decision':'changes_requested','input_fingerprint':fingerprint,'clip_ids':[c['clip_id']for c in clips],'observations':['Priorfive repairs remain effective; fullpack exposes new knockdown/recover body-support blockers despite technical contact/IK success.','Original newCopperScout polygons; not a faithful reconstruction of textured AI concept artwork.','All12actions inright/mirroredleft bindings sampled; mirroredleft is not independently authored anatomy/equipment.','Timing totals and phase1one-shot endpoint verify, while geometry/contact/joint target scores remain separate from actual visual weight and seams.'],'clips':clips,'blocking_clip_ids':['knockdown/right','knockdown/left','recover/right','recover/left'],'sample_scope':'Not a claim of manually viewing all1536frames; metadata/hashchecks cover everyPNG while visualreview is bounded tocontacts/eightsteps/2x.','source_ledger':ledger,'production_quality_approved':False,'previous_review':{'path':str(prior),'sha256':sha(prior),'input_fingerprint':json.loads(prior.read_text())['input_fingerprint'],'decision':'approved_prototype_only','scope':'Previous5RIGHTonly; notfullpackapproval','same_hash_approval':False},'technical_binding_checks':checks,'technical_binding_passed':all(x['passed']for x in checks),'visual_sampling':'Contacts all24bindings; eight native-scale exported steps all12rightactions; exact2x details and mirroredleft contacts. Priorfive same-source visuallychecked in preservedrevised-five receipt. GIF metadata actualdurations checked. No fullframe-by-frame humanview, real-time browser viewing, gameintegration or productionapproval claim.','timing':json.loads((O/'timing.json').read_text()),'limits':['Visual findings are reviewer judgments; quantitative knee/pelvis metadata supports description, not independently reconstructed anatomy.','Composite alpha bottom does not attribute individual boot/contact ownership.','Semantic strike/cast events are authored labels, not native discovered collision intervals.','Prototype approval is not production art approval, fullpack completion or gameplay acceptance.']}
(O/'review.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'decision':r['decision'],'input_fingerprint':fingerprint,'clip_ids':r['clip_ids'],'technical_checks':len(checks),'technical_passed':r['technical_binding_passed']}))

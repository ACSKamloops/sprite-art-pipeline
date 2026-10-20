import json,hashlib,math
from pathlib import Path
from PIL import Image
B=Path('/home/astra/artifacts/copper-scout-bake-private/full-grounded-final-v1/first');R=Path('/home/astra/projects/sprite-construction-lab-rig-pilot/pilot/rigged-character');O=Path(__file__).resolve().parent
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

notes['knockdown']={'decision':'approved_prototype_only','observations':['Finalrest actualhead/back/hip lies alongground; gloves reachsupport ratherthan suspendedtorso behindboots.','Reflectedleft contact/eightsteps remain grounded/readable; scarf no longerpenetratesfloor in sampledviews.','Fall/rest is a simplifiedvectorprototype, notproductionart or biomechanicalsimulation.'],'required_changes':[]}
notes['recover']={'decision':'approved_prototype_only','observations':['Opening actualRGBA equals groundedfallfinal ineachview; palmbrace lift→crouch→neutral reads clearly.','FinalactualRGBA equals knockdowninitialready ineachview; endpointphase1 included.'],'required_changes':[]}

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
prior=Path(__file__).resolve().parent.parent/'full-pack/review.json'
bind(prior)
previous=json.loads(prior.read_text());prior_by={c['clip_id']:c for c in previous['clips']};unchanged=[]
for c in clips:
    if c['clip_id'].split('/')[0] in ['knockdown','recover']:continue
    old=prior_by[c['clip_id']]['frame_bindings'];now=c['frame_bindings']
    check(len(old)==len(now),c['clip_id']+' unchanged framecount')
    for a,b in zip(old,now):check(a['pixel_sha256']==b['pixel_sha256'],c['clip_id']+f' frame{b["frame"]} unchanged originalfullreview RGBA')
    unchanged.append({'clip_id':c['clip_id'],'frames':len(now),'all_actual_pixel_sha_unchanged':all(a['pixel_sha256']==b['pixel_sha256']for a,b in zip(old,now))})
repair=Path(__file__).resolve().parent.parent/'grounded-fall/review.json';bind(repair);repaired=json.loads(repair.read_text());repair_by={c['clip_id']:c for c in repaired['clips']}
for c in clips:
    if c['clip_id'] not in repair_by:continue
    for a,b in zip(repair_by[c['clip_id']]['frame_bindings'],c['frame_bindings']):check(a['pixel_sha256']==b['pixel_sha256'],c['clip_id']+f' frame{b["frame"]} equals inspectedprivategroundrepair')
mirror_stats=[]
for view in ['right','left']:
    fall=m['clips']['knockdown/'+view]['frames'];rise=m['clips']['recover/'+view]['frames']
    def rgba(f):return Image.open(B/f['png']).convert('RGBA')
    check(rgba(fall[-1]).tobytes()==rgba(rise[0]).tobytes(),view+' groundedfallfinal equals recoveropening actualRGBA')
    check(rgba(rise[-1]).tobytes()==rgba(fall[0]).tobytes(),view+' recoverneutral equals fallinitial actualRGBA')
    for clip in ['knockdown','recover']:
        for i,f in enumerate(m['clips'][clip+'/'+view]['frames']):check(rgba(f).getchannel('A').crop((0,170,192,192)).getbbox() is None,clip+'/'+view+f' frame{i} no belowgroundopaque')
    rest=rgba(fall[-1]);windows=[(68,78),(93,105),(52,66)]
    if view=='left':windows=[(192-hi,192-lo)for lo,hi in windows]
    for j,(lo,hi) in enumerate(windows):check(any(rest.getpixel((x,169))[3] for x in range(lo,hi)),view+f' finalrestsupportwindow{j} opaque floorrow')
for clip in ['knockdown','recover']:
    counts=[]
    for i,f in enumerate(m['clips'][clip+'/right']['frames']):
        a=rgba(f).transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes();b=rgba(m['clips'][clip+'/left']['frames'][i]).tobytes();counts.append(sum(a[j:j+4]!=b[j:j+4]for j in range(0,len(a),4)))
    mirror_stats.append({'clip':clip,'frames':len(counts),'exact_pixel_reflections':sum(n==0 for n in counts),'max_differing_pixels':max(counts),'scope':'Left is reflectedgeometryrender; vectorrasteredges are not asserted bitwisePNGflip. Actualleftsupport/transitions andvisuals checked separately.'})
proofs={}
for name in ['contact-lock-report.json','grounded-fall/report.json']:
    path=R/'contact-proof'/name;bind(path);proof=json.loads(path.read_text());check(all(proof['source_sha256'][n]==m['source_bindings'][n]for n in ['clips.json','design.json','rig.gd']),name+' existingengineeringproof current3sourceSHA')
    proofs[name]={'path':str(path),'sha256':sha(path),'scope':'ExistingactualGPUworker report hashbound; reviewer didnotrerun movingworld renderer and doesnotuse contactnumericpass as artapproval. Rightwalk/run worldlockonly; leftworldcontactnotproven here.'}
    if name=='contact-lock-report.json':proofs[name]['routes']=[{k:v for k,v in row.items()if not isinstance(v,(dict,list))}for row in proof['routes']]
fingerprint=hashlib.sha256(json.dumps(ledger,sort_keys=True,separators=(',',':')).encode()).hexdigest()
r={'schema':'sprite-independent-visual-review/v1','nativeclock_effects_scope':'Authoredevents notnativecollisionwindows; shoot/projectile/castFX/chargelevels separate. Inplacebody loops do not themselves accumulateworld-root displacement.','reviewer':'som_animation_decoder independent reviewer','decision':'approved_prototype_only','input_fingerprint':fingerprint,'clip_ids':[c['clip_id']for c in clips],'observations':['Groundedfall/recovery repairs resolve previousfullpackblockingbody-support findings. Other20bindings remain pixelidentical; final24ready asboundedvectorprototype only.','Original newCopperScout polygons; not a faithful reconstruction of textured AI concept artwork.','All12actions inright/mirroredleft bindings sampled; mirroredleft is not independently authored anatomy/equipment.','Timing totals and phase1one-shot endpoint verify, while geometry/contact/joint target scores remain separate from actual visual weight and seams.'],'clips':clips,'blocking_clip_ids':[],'sample_scope':'Not a claim of manually viewing all1536frames; metadata/hashchecks cover everyPNG while visualreview is bounded tocontacts/eightsteps/2x.','source_ledger':ledger,'production_quality_approved':False,'previous_review':{'path':str(prior),'sha256':sha(prior),'input_fingerprint':json.loads(prior.read_text())['input_fingerprint'],'decision':'changes_requested','scope':'Previousfull24revision containedunsupportedfall/recovery; frozenhistorical evidence','same_hash_approval':False},'unchanged_twenty_bindings':unchanged,'repaired_right_reference':{'path':str(repair),'sha256':sha(repair)},'mirrored_raster_observations':mirror_stats,'ancillary_engineering_proofs':proofs,'previous_full_review_is_stale_for_final_inputs':previous['input_fingerprint']!=fingerprint,'technical_binding_checks':checks,'technical_binding_passed':all(x['passed']for x in checks),'visual_sampling':'Contacts all24bindings; eight native-scale exported steps all12rightactions; exact2x details and mirroredleft contacts. Priorfive same-source visuallychecked in preservedrevised-five receipt. GIF metadata actualdurations checked. No fullframe-by-frame humanview, real-time browser viewing, gameintegration or productionapproval claim.','timing':json.loads((O/'timing.json').read_text()),'limits':['Visual findings are reviewer judgments; quantitative knee/pelvis metadata supports description, not independently reconstructed anatomy.','Composite alpha bottom does not attribute individual boot/contact ownership.','Semantic strike/cast events are authored labels, not native discovered collision intervals.','Prototype approval is not production art approval, fullpack completion or gameplay acceptance.']}
(O/'review.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'decision':r['decision'],'input_fingerprint':fingerprint,'clip_ids':r['clip_ids'],'technical_checks':len(checks),'technical_passed':r['technical_binding_passed']}))

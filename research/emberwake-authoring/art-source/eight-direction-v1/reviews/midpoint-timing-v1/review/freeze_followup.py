from pathlib import Path
from fractions import Fraction
import json,hashlib,datetime
ROOT=Path('/home/astra/artifacts/emberwake-midpoint-timing-review-v1/input');OUT=Path('/home/astra/artifacts/emberwake-midpoint-timing-review-v1/review');CONTROL=Path('/home/astra/artifacts/emberwake-source-legs-review-v2/review')
for n in ['report.md','report.json','SHA256SUMS']:
 assert not (OUT/n).exists(),f'Refusing to rewrite frozen {n}'
m=json.loads((ROOT/'INPUTS.json').read_text());old=json.loads((CONTROL/'report.json').read_text());oldhash=json.loads((CONTROL/'input-hashes-before.json').read_text());anchor=old['ratings']['B'];assert anchor=={'appearance':8.0,'identity':8.5,'motion_readability':7.0,'game_usefulness':7.4}
oldmap={e['path']:e['actual_sha256'] for e in oldhash['images']};anchorcheck=[]
for direction in ['southeast','southwest']:
 for i in range(8):
  p=f'A/{direction}/{i:02}.png';got=hashlib.sha256((ROOT/p).read_bytes()).hexdigest();anchorcheck.append({'path':p,'sha256':got,'matches_own_previous_B':got==oldmap[f'B/{direction}/{i:02}.png']})
assert all(e['matches_own_previous_B'] for e in anchorcheck)
entries=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context'];after=[]
for e in entries:
 got=hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest();after.append({'path':e['path'],'expected_sha256':e['sha256'],'actual_sha256':got,'verified':got==e['sha256']})
before=json.loads((OUT/'input-hashes-before.json').read_text());assert len(after)==99 and all(e['verified'] for e in after);assert {e['path']:e['actual_sha256'] for e in before['images']}=={e['path']:e['actual_sha256'] for e in after}
(OUT/'input-hashes-after.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':after},indent=2)+'\n')
tf=json.loads((OUT/'timing-facts.json').read_text());H={v:[Fraction(*h) for h in m.get('variant_holds',{}).get(v,m['holds'])] for v in m['variants']}
assert all(sum(x)==Fraction(9,20) for x in H.values());assert all(tf['verified_design'].values())
ratings={'A':dict(anchor),'B':{'appearance':8.0,'identity':8.5,'motion_readability':7.1,'game_usefulness':7.5},'C':{'appearance':8.0,'identity':8.5,'motion_readability':7.0,'game_usefulness':7.4},'D':{'appearance':8.0,'identity':8.5,'motion_readability':7.1,'game_usefulness':7.5}}
base_cels={c['cel']:c['observation'] for c in next(s for s in old['sequences'] if s['variant']=='B' and s['direction']=='southeast')['cels']}
base_pairs={p['pair']:(p['severity'],p['observation']) for p in next(s for s in old['sequences'] if s['variant']=='B' and s['direction']=='southeast')['cyclic_pairs']}
midnote='Actual new midpoint. Two boots remain separate; the raised boot turns through an intermediate outward/downward toe plane with continuous knee/cuff/shaft attachment. The low boot lifts/narrows somewhat but stays closer to04; much of its pitch and trouser change still occurs into the next endpoint. Brown material/highlight family remains compatible; a hard angular ankle/toe edge is visible under enlargement, without a clear disconnected join.'
midpairs={
 '04->05':('minor','04 endpoint to actual midpoint: the raised boot has a new projected toe/shaft orientation and moves toward the next endpoint. Low boot remains comparatively04-like. Cuff/shaft attachment stays readable.'),
 '05->06':('minor-to-moderate','Actual midpoint to original05 endpoint: the larger remaining low-boot pitch/breadth and pale-trouser change occurs here. The midpoint distributes part of the transition but does not resolve all shape rotation.')}
idxmap=[0,1,2,3,4,None,5,6,7];pairmap={'00->01':'00->01','01->02':'01->02','02->03':'02->03','03->04':'03->04','06->07':'05->06','07->08':'06->07','08->00':'07->00'}
sequences=[]
for v in ['A','B','C','D']:
 for direction in ['southeast','southwest']:
  n=len(m['variants'][v][direction]);is_mid=v in ['B','D'];cels=[];pairs=[]
  for i in range(n):
   k=f'{i:02}';source_i=idxmap[i] if is_mid else i;note=midnote if source_i is None else base_cels[f'{source_i:02}']
   cels.append({'exposure':k,'inspected':True,'source_role':'actual new midpoint' if source_i is None else f'unchanged A{source_i:02} endpoint','hold_rational':[H[v][i].numerator,H[v][i].denominator],'hold_ms':float(H[v][i]*1000),'start_ms':tf['timeline'][v][i]['start_ms'],'spatial_observation':note})
   j=(i+1)%n;p=f'{i:02}->{j:02}'
   sev,pnote=midpairs[p] if is_mid and p in midpairs else base_pairs[pairmap[p] if is_mid else p]
   schedule_note='Equal-hold control; spatial judgment retained from frozen anchor.' if v=='A' else ('Original endpoint starts remain exact. Only04 exposure is split into04/mid; no normal-speed improvement is established by this schedule.' if v=='B' else 'Changed holds: reduced opening/seam exposure and redistributed middle dwell. Cadence effect is an unverified timing hypothesis, not a spatial repair.')
   pairs.append({'pair':p,'inspected':True,'severity':sev,'spatial_observation':pnote,'outgoing_hold_ms':float(H[v][i]*1000),'incoming_hold_ms':float(H[v][j]*1000),'schedule_observation':schedule_note})
  alpha='screen right' if direction=='southeast' else 'screen left';beta='screen left' if direction=='southeast' else 'screen right'
  sequences.append({'variant':v,'direction':direction,'ratings':ratings[v],'rating_status':'unchanged retained anchor' if v=='A' else ('new static-spatial judgment; no exact-speed playback claim' if v=='B' else 'provisional motion/game; no timing benefit awarded'),
   'projected_roles':{'alpha':f'Low/forward boot on {alpha} in00; persistent projected role, not an anatomical label.','beta':f'Tucked/higher boot on {beta} in00.',
    'chronology':'Alpha low00-02; both converge03; beta is low from04 through the original05/06 poses; alpha returns low in original07 before00. The new midpoint preserves beta-low/alpha-raised identities through04-mid-05.',
    'finding':'No definite foot interchange or detached cuff demonstrated. Equal sole Y and fixed anatomical screen sides were not required.'},
   'cels':cels,'cyclic_pairs':pairs})
report={
 'status':'frozen single declared 2x2 midpoint/timing follow-up; not a new cold review',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':{'input_root':str(ROOT),'output_root':str(OUT),'input_manifest_sha256':hashlib.sha256((ROOT/'INPUTS.json').read_bytes()).hexdigest(),'input_images':99,
  'all_walk_exposures_inspected':68,'all_cyclic_pairs_inspected':68,'scales':['native128','nearest2x256','nearest84proxy'],'backgrounds':['light#e8e7db','dark#181e27','ground#576546'],
  'context_use':'Nominated identity/turn context matches the reviewer\'s previously inspected frozen control; hashes reverified here.',
  'outside_reads':'Only nominated input and this reviewer\'s own frozen control report/hash record; no producer docs, sibling source maps, parent mapping, skills or other-agent work.',
  'input_mutation':False,'canonical_repo_access':False,'target_score_supplied':False},
 'anchor':{'variant':'A','own_previous_variant':'source-legs B','prior_report':str(CONTROL/'report.json'),'prior_report_sha256':hashlib.sha256((CONTROL/'report.json').read_bytes()).hexdigest(),'ratings_retained_exactly':True,'rerated':False,'ratings':anchor,'image_identity_checks':anchorcheck},
 'verification':{'before_verified':99,'after_verified':99,'mismatches':0,'before_equals_after':True,'current_A_matches_own_control':16,'design_checks':tf['verified_design']},
 'comparison_conditions':m['comparison_conditions'],'variant_holds_rational':{v:[[h.numerator,h.denominator] for h in hs] for v,hs in H.items()},'timelines':tf['timeline'],
 'ratings':ratings,
 'rating_scale':'Absolute subjective0-10 for this compact RPG use:0 unusable,5 recognizable but visibly rough,10 exceptional finished art. Motion scores here include static transition legibility. Differences of0.1 are near-ties, not measured precision.',
 'rating_qualification':'A remains unchanged. C uses identical A art; its appearance/identity are carried and its motion/game scores are provisional neutral estimates with no timing bonus. D shares B art and is tied provisionally with B because the changed schedule has not been observed in continuous human playback. B/D\'s small gain reflects the actual visible intermediate projected surface, not extra frame count.',
 'uncertainty':{'appearance_identity':'Higher confidence from still sources at all requested scales/backgrounds.','B_local_spatial_change':'Moderate confidence in modest extra legibility; low-boot pitch change remains concentrated after midpoint.','C_D_timing_preference':'Unresolved. A vsC and B vsD cannot be ranked confidently for normal-speed cadence from this evidence.'},
 'preference':'B/D have a small spatial advantage over A/C at the new local transition. B is the conservative candidate for retaining original endpoint starts. D remains a plausible timing test, not a verified timing winner. No normal-speed cadence preference between A/C or B/D is claimed.',
 'new_midpoint_assessment':{
  'projected_surface':'A real intermediate raised-boot toe/shaft plane is visible. The low boot also shifts toward the next position, but remains closer to04 in pitch and broad mass.',
  'joins':'Pale trouser/cuff boundaries feed into brown shafts and both boots remain attached. No clear seam detachment or extra foot appears. Existing fuller proximal volumes are preserved.',
  'materials':'Brown leather, warm toe/shaft highlights and dark sole/edge treatment remain compatible. The raised ankle/toe edge is angular under enlargement; it is not a different material.',
  'boot_pitch_continuity':'04->mid helps describe the raised boot turn. Mid->original05 retains the stronger low-boot pitch/breadth/trouser change. Thus a useful partial bridge, not complete smoothing.',
  'game_scale':'At84px the stage still reads as two boots with a changed raised toe, while fine join detail is less visible. The28.125ms B exposure and34.375ms D exposure have not been observed at exact speed.'},
 'timing_only_assessment':{
  'authoritative_sources':'variant_holds and comparison_conditions in nominated INPUTS.json override the default holds for B/C/D.',
  'B':'04 hold is split28.125+28.125ms. All original endpoint starts, original05 at281.25ms, and450ms loop are retained.',
  'C':'Holds in ms:56.25,31.25,68.75,68.75,68.75,68.75,62.5,25. Original key starts change deliberately; each half remains225ms.',
  'D':'Same C allocation, but timed04 is split34.375+34.375ms. Original05 endpoint begins293.75ms, matching C rather than A/B. Both halves remain225ms.',
  'plausible_benefit':'The near-similar original07+00+01 exposure total reduces from168.75ms to112.5ms;00+01 reduces112.5 to87.5ms. This directly reduces allocated dwell around the flagged opening/seam arrangement.',
  'countervailing_risk':'Middle poses02-05 are each held68.75ms in C;06 is62.5ms and07 only25ms. More central dwell and a short recovery key may feel clearer or more hesitant/snapped. Positive holds and equal225ms halves do not prove a natural cadence.',
  'evidence_limit':'Still strips show identical spatial defects in A/C and identical spatial changes in B/D. Scheduled dwell changes can be quantified; their actual flow benefit remains unobserved.'},
 'sequences':sequences,
 'remaining_defects':['Mid->original05 still contains the stronger low-boot pitch/breadth and trouser-volume turn.','Original03->04 still broadens the newly low knee/boot.','Original00->01 retains a similar silhouette; timing allocation alone does not redraw its leg arc.','Original06->07 remains a rapid recovery-shape change, with its visibility especially uncertain at C/D25ms final exposure.'],
 'next_evidence':'Exact-time human viewing at game scale is required to rank the timing schedules. No further art, exposure ordering or timing variant was generated or rated in this pass.',
 'perception_limits':['Static exposure strips and every cyclic adjacent pair were inspected, including07->00 for A/C and08->00 for B/D.','No continuous human playback was observed. No inference from scheduled holds to normal-speed fluency is made.','No physical world-contact, planted-foot, friction or translation certification is made.','The84px nearest proxy approximates0.66 canvas scale; actual engine filtering/camera/terrain may alter the result.'],
 'artifacts':{'full_exposure_sheets':18,'dual_schedule_pair_sheets':4,'actual_midpoint_detail_sheets':1,'hash_ledger':'SHA256SUMS','timing_facts':'timing-facts.json'}}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# Midpoint and timing 2×2 follow-up — frozen','',
'The actual midpoint provides a small spatial gain at 04→mid→05. B/D are near-tied slightly ahead of A/C for that local transition. The changed C/D schedules plausibly address the flagged dwell, but normal-speed timing preference remains unresolved.','',
'This is a declared follow-up using my own frozen source-legs control, not a new cold review. Current A matches that previous B in all 16 walk images; its scores and judgment are unchanged.','',
'| Variant | Appearance | Identity | Motion readability | Game usefulness |','|---|---:|---:|---:|---:|']
for v in ['A','B','C','D']:
 r=ratings[v];label={'A':'A — retained anchor','B':'B — midpoint','C':'C — timing only, provisional','D':'D — midpoint + timing, provisional'}[v];lines.append(f"| {label} | {r['appearance']:.1f} | {r['identity']:.1f} | {r['motion_readability']:.1f} | {r['game_usefulness']:.1f} |")
lines+=['',
'Absolute subjective 0–10 ratings for this compact RPG use. Differences of 0.1 are near-ties. Motion scores include static transition legibility. C/D receive no timing bonus: their motion/game numbers are provisional neutral estimates tied with the matching-art control. C’s appearance/identity are carried from unchanged A art. No frame-count, source-exactness or uniqueness credit is applied. No target score was supplied.','',
'## New midpoint: projected surfaces and joins','',
'The raised boot has an actual intermediate toe/shaft orientation that helps describe its turn. Pale trouser/cuff boundaries continue into the brown shafts; two boots remain separate and attached. Brown leather, warm highlights and dark sole/edge treatment fit the surrounding art. An angular raised ankle/toe edge is visible under enlargement, with no clear detached seam or different material.','',
'The low boot moves somewhat toward the next position, but stays closer to 04 in pitch and mass. The stronger low-boot breadth/pitch and trouser change still occurs from the midpoint into original 05. This is a partial bridge. At 84px the intermediate raised toe remains legible, although small join detail recedes. Its actual visibility during a 28.125ms or 34.375ms exposure was not observed.','',
'## Verified 2×2 conditions','',
'`variant_holds` and `comparison_conditions` are authoritative.','',
'| Variant | Actual art | Holds in ms |','|---|---|---|',
'| A | 8 original drawings | 56.25 × 8 |',
'| B | A plus actual midpoint after 04 | 56.25,56.25,56.25,56.25,28.125,28.125,56.25,56.25,56.25 |',
'| C | Exact A PNGs | 56.25,31.25,68.75,68.75,68.75,68.75,62.5,25 |',
'| D | Exact B PNGs | 56.25,31.25,68.75,68.75,34.375,34.375,68.75,62.5,25 |','',
'Each loop is 450ms. B retains every original endpoint start, including original 05 at 281.25ms. C/D deliberately change key starts, retain two 225ms halves, and start original 05 at 293.75ms. These are verified schedule properties, not fluency claims.','',
'C/D reduce original 07+00+01 exposure from 168.75ms to 112.5ms, and 00+01 from 112.5ms to 87.5ms. That allocates less time to the previously flagged similar-pose region. They also hold central poses longer and shorten original 07 to 25ms, which could make the central action clearer or more hesitant and the return more abrupt. I cannot rank A versus C or B versus D for normal-speed cadence from still chronology.','',
'B is the conservative midpoint candidate because it preserves endpoint starts. D is a plausible timing test; the evidence does not establish it as a winner.','',
'## Persistent projected roles','',
'Alpha begins low/forward in 00: SE screen right, SW screen left. Beta is tucked/higher on the opposite side. These are projected roles, not anatomical labels. The roles converge visibly in original 03, beta is low in original 04–06, and alpha returns low in original 07. The new midpoint keeps beta low and alpha raised through 04→mid→05. No definite interchange, detached cuff or extra foot is demonstrated. Equal sole Y and fixed anatomical screen sides were not required.','',
'## Every exposure and cyclic pair','',
'All 68 nominated walk exposures and all 68 cyclic pairs were inspected for A/B/C/D in SE/SW, at native 128, nearest 2× and 84px, on light/dark/ground. Identical A/C images and B/D images have separate hold annotations. `report.json` records every exposure, start, hold, projected role and cyclic pair explicitly. A’s existing judgment was retained rather than rerated.','',
'| A/C pair | Spatial finding |','|---|---|']
for p,(sev,note) in base_pairs.items():lines.append(f'| {p.replace("->","→")} | {sev}: {note} |')
lines+=['','| B/D pair | Spatial finding |','|---|---|']
for i in range(9):
 p=f'{i:02}->{(i+1)%9:02}';sev,note=midpairs[p] if p in midpairs else base_pairs[pairmap[p]];lines.append(f'| {p.replace("->","→")} | {sev}: {note} |')
lines+=['',
'Unchanged remaining concerns are the breadth change into original 04, limited silhouette travel at 00→01, and rapid original 06→07 recovery. C/D change their allotted visibility; they do not redraw those spatial relationships. Identity, clothing volumes and arm/body response otherwise remain at the anchor level. Dark backgrounds soften the darkest boot edges while warm highlights preserve separation.','',
'## Verification and perception limits','',
'All 99 image hashes match before and after; both checks agree. A matches the frozen control in all 16 walk images. The equal-art A/C and B/D conditions, B endpoint starts, 450ms totals and C/D 225ms halves were verified. Inputs and canonical repo were not changed. Only nominated input and my own frozen control report/hash record were read; no producer docs, parent mapping, sibling source maps, skills or other agents’ work.','',
'No continuous human playback was observed. Static chronology cannot establish normal-speed flow or physical world contact, planted feet, friction or game translation. The 84px nearest proxy approximates the stated 0.66 canvas scale; engine sampling remains separate. Timing confidence is lower than confidence in appearance/identity and the visible local surface change.','',
'Artifacts include 18 whole-exposure sheets, four dual-schedule cyclic-pair sheets, `actual-04-mid-05-lower5x.png`, `timing-facts.json`, both input hash checks, `report.json` and the frozen output ledger `SHA256SUMS`.','']
(OUT/'report.md').write_text('\n'.join(lines))
ledger=[]
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS':ledger.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}')
(OUT/'SHA256SUMS').write_text('\n'.join(ledger)+'\n')
for p in OUT.rglob('*'):
 if p.is_file():p.chmod(0o444)
print(json.dumps({'status':'frozen declared2x2 follow-up','ratings':ratings,'before_verified':99,'after_verified':99,'A_control_images_verified':16,'all_exposures_and_pairs':68,'ledger_entries':len(ledger),'report_sha256':hashlib.sha256((OUT/'report.md').read_bytes()).hexdigest(),'json_sha256':hashlib.sha256((OUT/'report.json').read_bytes()).hexdigest(),'ledger_sha256':hashlib.sha256((OUT/'SHA256SUMS').read_bytes()).hexdigest()},indent=2))

from pathlib import Path
import json,hashlib,datetime
from fractions import Fraction
ROOT=Path('/home/astra/artifacts/emberwake-four-hold-review-v2/input');OUT=Path('/home/astra/artifacts/emberwake-four-hold-review-v2/review');CONTROL=Path('/home/astra/artifacts/emberwake-source-legs-review-v2/review')
for n in ['report.md','report.json','SHA256SUMS']:
 assert not (OUT/n).exists(),f'Refusing to rewrite frozen {n}'
m=json.loads((ROOT/'INPUTS.json').read_text());old=json.loads((CONTROL/'report.json').read_text());oldhash=json.loads((CONTROL/'input-hashes-before.json').read_text());anchor=old['ratings']['B']
assert anchor=={'appearance':8.0,'identity':8.5,'motion_readability':7.0,'game_usefulness':7.4}
oldmap={e['path']:e['actual_sha256'] for e in oldhash['images']};anchorcheck=[]
for direction in ['southeast','southwest']:
 for i in range(8):
  p=f'A/{direction}/{i:02}.png';actual=hashlib.sha256((ROOT/p).read_bytes()).hexdigest();anchorcheck.append({'path':p,'sha256':actual,'matches_own_previous_B':actual==oldmap[f'B/{direction}/{i:02}.png']})
assert len(anchorcheck)==16 and all(e['matches_own_previous_B'] for e in anchorcheck)
entries=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context'];after=[]
for e in entries:
 got=hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest();after.append({'path':e['path'],'expected_sha256':e['sha256'],'actual_sha256':got,'verified':got==e['sha256']})
before=json.loads((OUT/'input-hashes-before.json').read_text());assert len(after)==63 and all(e['verified'] for e in after);assert {e['path']:e['actual_sha256'] for e in before['images']}=={e['path']:e['actual_sha256'] for e in after}
(OUT/'input-hashes-after.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':after},indent=2)+'\n')
ratings={'A':dict(anchor),'B':{'appearance':8.0,'identity':8.5,'motion_readability':6.8,'game_usefulness':7.2}}
cels={
 '00':'A00 held: low/forward alpha boot, tucked beta boot. Clear materials and full trouser/boot volumes.',
 '01':'Exact continuation of 00, completing a deliberate 112.5ms visible hold.',
 '02':'A03 held: two whole boots converge visibly beneath rounded repaired trousers. A clear neutral/passing key.',
 '03':'Exact continuation of 02, completing its 112.5ms hold.',
 '04':'A04 held: beta low/forward and alpha raised/tucked. The broad low boot and pale knee remain conspicuous.',
 '05':'Exact continuation of 04, completing its 112.5ms hold.',
 '06':'A07 held: a distinct return with alpha lower/forward and beta tucked. Repaired fuller bent trousers preserve attachment.',
 '07':'Exact continuation of 06, completing its 112.5ms hold before the seam.'}
pairs={
 '00->01':('intentional hold','Exact duplicate. A deliberate contact-like hold; repetition alone earns neither credit nor penalty.'),
 '01->02':('minor-to-moderate','A00->A03: boots converge into the passing key in one image change. Readable roles, with a relatively abrupt low alpha toe/shaft and trouser adjustment.'),
 '02->03':('intentional hold','Exact duplicate. The rounded passing/neutral key stays legible for 112.5ms.'),
 '03->04':('minor-to-moderate','A03->A04: clear move toward beta-low/alpha-raised. The beta boot/knee broadens conspicuously and is held, exposing the existing local volume difference.'),
 '04->05':('intentional hold','Exact duplicate. Opposite-step key held for 112.5ms.'),
 '05->06':('moderate','A04->A07: the low role returns to alpha in a direct jump, skipping the drawn A05/A06 recovery. Both boots remain traceable, but this is the weakest new transition.'),
 '06->07':('intentional hold','Exact duplicate. Distinct return key held for 112.5ms; it is not the same passing key used earlier.'),
 '07->00':('minor-to-moderate','A07->A00: boots extend/tuck farther while retaining the alpha-low/beta-tucked arrangement. No gross loop reset, but adjacent similar-role holds across the seam can create a longer apparent plateau.')}
sourcekeys=['00','00','03','03','04','04','07','07'];facts=json.loads((OUT/'diagnostic-pixel-facts.json').read_text())
assert all(e['byte_identical_A_key']==sourcekeys[int(e['B_slot'])] for e in facts['nominated_pose_selection'])
sequences=[]
for direction in ['southeast','southwest']:
 side='screen right' if direction=='southeast' else 'screen left';opposite='screen left' if direction=='southeast' else 'screen right'
 sequences.append({'variant':'B','direction':direction,'ratings':ratings['B'],
  'projected_roles':{'alpha':f'Low/forward boot on {side} in00, followed through cuff/shaft rather than an anatomical label.',
   'beta':f'Tucked/higher boot on {opposite} in00.',
   'chronology':'00-01 alpha low/beta tucked;02-03 both converge visibly;04-05 beta low/alpha raised;06-07 alpha returns low/beta tucked, extending/tucking farther across07->00.',
   'finding':'Persistent roles remain readable. No definite foot interchange is demonstrated. Equal sole Y and fixed anatomical screen sides were not required.'},
  'cels':[{'cel':f'{i:02}','byte_identical_A_key':sourcekeys[i],'inspected':True,'observation':cels[f'{i:02}']} for i in range(8)],
  'cyclic_pairs':[{'pair':f'{i:02}->{(i+1)%8:02}','inspected':True,'severity':pairs[f'{i:02}->{(i+1)%8:02}'][0],'observation':pairs[f'{i:02}->{(i+1)%8:02}'][1]} for i in range(8)]})
report={
 'status':'frozen single declared pose-selection follow-up; not a new cold review',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':{'input_root':str(ROOT),'output_root':str(OUT),'input_manifest_sha256':hashlib.sha256((ROOT/'INPUTS.json').read_bytes()).hexdigest(),
  'input_images':63,'B_cels_inspected':16,'B_cyclic_pairs_inspected':16,'scales':['native128','nearest2x256','nearest84proxy'],'backgrounds':['light#e8e7db','dark#181e27','ground#576546'],
  'context_use':'Nominated cardinal/appearance context is identity/turn only. Same context was inspected in this reviewer\'s own frozen control, and its image hashes were reverified here.',
  'outside_reads':'Only nominated input and this reviewer\'s own frozen control report/hash record; no sibling source maps, producer docs, skills or other agents\' work.',
  'input_mutation':False,'canonical_repo_access':False,'target_score_supplied':False},
 'anchor':{'current_variant':'A','own_prior_variant':'B','prior_report':str(CONTROL/'report.json'),'prior_report_sha256':hashlib.sha256((CONTROL/'report.json').read_bytes()).hexdigest(),
  'ratings_retained_exactly':True,'rerated':False,'ratings':anchor,'image_identity_checks':anchorcheck,
  'judgment_retained':'Repaired rounded03/07 clothing is useful, with remaining00->01 plateau,04->05 whole-boot breadth/angle change and fast06->07 return. Overall A remains preferred for its fuller recovery arc.'},
 'verification':{'before_verified':63,'after_verified':63,'mismatches':0,'before_equals_after':True,'current_A_matches_own_frozen_control_images':16},
 'ratings':ratings,
 'rating_scale':'Absolute subjective0-10 for this compact RPG use:0 unusable,5 recognizable but visibly rough,10 exceptional finished art. Small decimal differences are judgments, not measured precision.',
 'art_credit_rules':'No credit for exactness, more/fewer drawings, duplicated slots or frame count. B appearance/identity remain tied with A because the actual selected drawings preserve the same art strengths. New motion/game scores assess changed order and holds.',
 'preference':'A by a modest margin for the walk. B is a usable compact four-key alternative and is more informative than the earlier same-neutral return test, but does not surpass A.',
 'actual_B_selection':{'slots':sourcekeys,'logical_keys':['A00','A03','A04','A07'],'slot_hold_seconds':float(Fraction(9,160)),'logical_hold_seconds':float(Fraction(9,80)),'loop_seconds':float(Fraction(9,20))},
 'what_improved_from_own_previous_C':'The second neutral reuse is gone. A07 supplies a distinct bent-leg return, so the latter half no longer simply reverses the first two image changes. This is a real sequence improvement and the reason for the modest motion/game improvement over that earlier test; no added-drawing bonus is applied.',
 'tradeoff_against_A':'The new B moves directly from A04 to A07 at05->06, omitting A05/A06\'s drawn lift/turn information. The two112.5ms holds around the seam use distinct but similar alpha-low/beta-tucked arrangements, totaling225ms in that broad arrangement. This may produce a longer perceived plateau. Equal hold durations do not by themselves establish equally developed step phases.',
 'appearance_identity':'Full rounded trousers/cuffs, readable whole boots and strong hair/face/costume identity survive the selection. The existing breadth change around A03->A04 remains exposed. Dark backgrounds soften the darkest boot edges, but warm highlights and two-boot separation preserve readability at84px.',
 'body_response':'The selected keys have a stable head/torso and small arm changes. Step information comes mostly from the leg shapes. A contains more intermediate recovery information; a forced bob or body fit is not required by this review.',
 'sequences':sequences,
 'exact_B_vs_A_changes':[{'B_slot':f'{i:02}','A_key':sourcekeys[i],'same_numbered_A_slot_unchanged':sourcekeys[i]==f'{i:02}'} for i in range(8)],
 'remaining_defects':['05->06 direct opposite-to-return jump is the most consequential new transition.','07->00 and the neighboring exact holds risk a prolonged similar-role plateau.','03->04 retains the broadening of the newly low knee/whole boot.'],
 'next_evidence':'Exact-time human playback at the intended game scale would resolve whether the longer holds feel crisp or hesitant. No further sequence was generated or rated in this pass.',
 'perception_limits':['All B cels and eight cyclic pairs in each direction were inspected at native/2x/84px on light/dark/ground. A was displayed only as the retained control, not rerated.',
  'Still chronology and pair perception do not establish continuous human playback at the exact holds.',
  'No physical-contact, planted-foot, friction or game-translation certification is made. Contact-like labels describe pose reading only.',
  'The84px nearest proxy approximates the0.66 canvas scale; engine filtering/camera/terrain may alter the result.'],
 'artifacts':{'whole_cel_sheets':9,'B_cyclic_pair_sheets':2,'hash_ledger':'SHA256SUMS','pixel_facts':'diagnostic-pixel-facts.json; byte/raw RGBA diagnostics, not quality measures'}}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# Four-hold pose-selection follow-up — frozen','',
'A remains preferred by a modest margin. B is a usable compact four-key walk: the distinct 07 return improves on the earlier same-neutral sequence, but its direct opposite-to-return jump and long similar-role stretch across the seam keep it below the retained A control.','',
'This is one declared follow-up of a new actual pose order/hold choice, not a new cold review. A byte-matches my own previous B in all 16 walk images. Its scores and judgment are carried unchanged.','',
'| Variant | Appearance | Identity | Motion readability | Game usefulness |','|---|---:|---:|---:|---:|']
for v in ['A','B']:
 r=ratings[v];label='A — retained anchor' if v=='A' else 'B — new sequence';lines.append(f"| {label} | {r['appearance']:.1f} | {r['identity']:.1f} | {r['motion_readability']:.1f} | {r['game_usefulness']:.1f} |")
lines+=['',
'Absolute subjective 0–10 ratings for this compact RPG use: 0 unusable, 5 recognizable but visibly rough, 10 exceptional finished art. Small decimal differences are judgments. Source exactness, frame count, uniqueness, and more/fewer drawings earn no art credit. No target number was supplied.','',
'## Actual selection and timing','',
'B verifies as A00,A00,A03,A03,A04,A04,A07,A07. Each logical drawing is held 112.5ms; the loop remains 0.45s. Adjacent duplicates are intentional holds, not automatically defects. Both SE and SW were inspected separately at native 128, nearest 2×, and an 84px proxy on light, dark and ground backgrounds.','',
'## What changed in the reading','',
'The distinct A07 return resolves the previous same-neutral reuse: the latter half no longer simply reverses the first two image changes. Its fuller bent trousers/cuffs remain attached to readable whole boots. This is a meaningful improvement in the actual sequence.','',
'Against A, B05→06 is now the direct A04→A07 transition. It skips the drawn A05/A06 lift/turn information and exchanges the low role more abruptly. B07→00 then connects two distinct but similar alpha-low/beta-tucked arrangements. The holds on those two keys total 225ms across the loop seam, so the broad role arrangement can appear to linger. This is a duration-and-pose concern; four equal clock holds do not by themselves establish four equally developed step phases.','',
'B retains the same strong appearance and identity. The existing knee/boot broadening at A03→A04 remains visible, particularly with the longer hold. Warm boot highlights preserve readability on dark ground although the darkest edges soften. The selected keys keep a stable torso/head and small arm response; most step information comes from the legs. The review does not require an invented bob or a body fit.','',
'## Persistent projected roles','',
'Alpha begins low/forward in 00: SE screen right, SW screen left. Beta begins tucked/higher on the opposite side. These are persistent projected roles, not anatomical labels. In B00/01 alpha is low, B02/03 converges both visible boots, B04/05 makes beta low and alpha raised, then B06/07 returns alpha low before further extension/tucking at the seam. No definite foot interchange is demonstrated. Equal sole Y and fixed anatomical screen sides were not required.','',
'## Every B cel','', '| Slot | Selected A key | Observation |','|---|---|---|']
for i in range(8):
 k=f'{i:02}';lines.append(f'| {k} | {sourcekeys[i]} | {cels[k]} |')
lines+=['','## Every cyclic adjacent pair','','The following notes apply to separately inspected SE and SW sequences with projected sides reversed. report.json contains explicit records for both directions.','','| B pair | Finding |','|---|---|']
for i in range(8):
 p=f'{i:02}->{(i+1)%8:02}';lines.append(f'| {p.replace("->","→")} | {pairs[p][0]}: {pairs[p][1]} |')
lines+=['','## Verification and limits','',
'All 63 nominated image hashes match before and after, and the checks agree. Current A also matches my frozen prior control in all 16 walk images. Nine whole-cel scale/background sheets and two lower-body cyclic-pair sheets are included. No nominated image or canonical repo was changed. Only nominated inputs and my own frozen control report/hash record were read; no sibling source maps, producer docs, skills or other agents’ work.','',
'This is still chronology and pair perception. Continuous human playback at the exact holds was not observed. Physical world contact, planted feet, friction and game translation remain unverified; contact-like labels describe pose reading. The 84px nearest proxy approximates the stated 0.66 canvas scale, with engine sampling still a separate consideration.','',
'Exact-time human playback at game scale would determine whether the longer holds feel crisp or hesitant. No further sequence was generated or rated in this pass.','',
'Artifacts: `report.json`, `input-hashes-before.json`, `input-hashes-after.json`, `diagnostic-pixel-facts.json`, `sheet-*.png`, `pairs-B-*.png` and `SHA256SUMS`.','']
(OUT/'report.md').write_text('\n'.join(lines))
ledger=[]
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS':ledger.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}')
(OUT/'SHA256SUMS').write_text('\n'.join(ledger)+'\n')
for p in OUT.rglob('*'):
 if p.is_file():p.chmod(0o444)
print(json.dumps({'status':'frozen declared four-hold follow-up','ratings':ratings,'before_verified':63,'after_verified':63,'A_anchor_images_verified':16,'ledger_entries':len(ledger),'report_sha256':hashlib.sha256((OUT/'report.md').read_bytes()).hexdigest(),'json_sha256':hashlib.sha256((OUT/'report.json').read_bytes()).hexdigest(),'ledger_sha256':hashlib.sha256((OUT/'SHA256SUMS').read_bytes()).hexdigest()},indent=2))

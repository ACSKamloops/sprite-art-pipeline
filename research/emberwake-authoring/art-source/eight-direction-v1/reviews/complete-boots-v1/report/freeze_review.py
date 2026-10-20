from pathlib import Path
from PIL import Image
from fractions import Fraction
import json, hashlib, datetime, os
ROOT=Path('/home/astra/artifacts/emberwake-complete-boots-review-v1/input')
OUT=Path('/home/astra/artifacts/emberwake-complete-boots-review-v1/review')
for n in ['report.md','report.json','SHA256SUMS']:
    assert not (OUT/n).exists(), f'Refusing to rewrite frozen output {n}'
m=json.loads((ROOT/'INPUTS.json').read_text())
entries=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context']
after=[]
for e in entries:
    actual=hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()
    after.append({'path':e['path'],'expected_sha256':e['sha256'],'actual_sha256':actual,'verified':actual==e['sha256']})
assert len(after)==63 and all(e['verified'] for e in after)
before=json.loads((OUT/'input-hashes-before.json').read_text())
assert {e['path']:e['actual_sha256'] for e in before['images']}=={e['path']:e['actual_sha256'] for e in after}
(OUT/'input-hashes-after.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':after},indent=2)+'\n')
ratings={
 'A':{'appearance':8.0,'identity':8.5,'motion_readability':6.1,'game_usefulness':6.8},
 'B':{'appearance':7.8,'identity':8.5,'motion_readability':6.8,'game_usefulness':7.2}}
common_cels={
 '00':'Readable low forward boot and tucked higher boot; full, rounded trouser and boot shapes.',
 '01':'Very similar leg silhouette to 00 despite the body bob and small reshaping. Early-cycle plateau risk.',
 '02':'Boots separate; the low boot straightens and its toe becomes narrower. Knee-to-ankle paths remain readable.',
 '05':'Opposite low/high arrangement reads as the other half of the walk; two cuffs and two boots are distinguishable.',
 '06':'Clear raised rounded knee and low opposite boot. Exaggerated knee volume is stylistic, with a visible cuff/boot attachment.'}
variant_cels={
 'A':{'03':'Near-complete projected boot overlap. The rear boot is mostly a dark sliver; broad foreground cuff dominates. Not proof of a missing foot.',
      '04':'Overlap persists with a diagonal pale shin and dark rear boot wedge. Which boot is taking the lead is harder to read at 84px.',
      '07':'Two boots are visible again, but the low-forward/tucked-back silhouette closely anticipates 00 and 01.'},
 'B':{'03':'Both whole boots remain visible. Narrower, straighter trouser columns and relatively tall boot shafts make this cel less round and plush than its neighbors.',
      '04':'A clear low opposite boot / raised starting-forward boot exchange. The low boot and pale knee become noticeably fuller than in 03.',
      '07':'Both whole boots remain visible. The raised boot is foreshortened sharply and the pale trouser joins pinch into small tapered shapes, restoring more volume at 00.'}}
common_pairs={
 '00->01':('minor','Low leg-silhouette change produces a perceptual plateau; the images are not duplicate holds.'),
 '01->02':('minor','Toe/shaft straightening is more conspicuous than a broad step arc, but the roles stay traceable.'),
 '05->06':('acceptable','Low/high roles persist, with readable lift. Large pale knee is attached to its boot; no definite interchange.')}
variant_pairs={
 'A':{
  '02->03':('moderate','Separated boots merge into an almost single boot silhouette, obscuring the rear role.'),
  '03->04':('moderate','Overlap remains while the foreground shin/boot changes angle. Lead exchange is ambiguous; this does not establish an anatomical swap.'),
  '04->05':('moderate','The rear role reappears as a separated boot; the exchange reads more as a shape reveal than a well-described passing action.'),
  '06->07':('moderate','The lifted/low arrangement returns quickly to the opening arrangement; a small recovery/cuff arc would help.'),
  '07->00':('minor','No gross whole-character reset, but another very similar forward/tucked pose extends the apparent opening plateau.')},
 'B':{
  '02->03':('minor','The boots remain separate, improving role tracking. The trousers narrow and the boot shafts become comparatively tall/straight.'),
  '03->04':('moderate','The role exchange is clear, but the newly low trouser/knee and boot grow abruptly while the other boot tucks up.'),
  '04->05':('minor','The newly low boot narrows/turns from its broad 04 shape. Still readable as the same projected role.'),
  '06->07':('moderate','Rapid return is accompanied by pinched trouser/cuff joins and a short raised-boot shaft; strongest remaining volume discontinuity.'),
  '07->00':('minor','Raised boot tucks inward and cuff/trouser volume restores. No gross loop reset; a local shape pulse remains.')}}
sequences=[]
for v in ['A','B']:
 for direction in ['southeast','southwest']:
  forward_side='screen right' if direction=='southeast' else 'screen left'
  rear_side='screen left' if direction=='southeast' else 'screen right'
  cels=[];pairs=[]
  for i in range(8):
   k=f'{i:02}';cels.append({'cel':k,'inspected':True,'observation':common_cels.get(k,variant_cels[v].get(k))})
   p=f'{i:02}->{(i+1)%8:02}';severity,note=common_pairs.get(p,variant_pairs[v].get(p));pairs.append({'pair':p,'inspected':True,'severity':severity,'observation':note})
  sequences.append({'variant':v,'direction':direction,'ratings':ratings[v],
   'projected_roles':{'alpha':f'Boot low/forward on {forward_side} in 00; followed through its cuff, not assigned anatomical left/right.',
    'beta':f'Boot higher/tucked on {rear_side} in 00; followed as the opposite projected role.',
    'tracking':'00-02: alpha low, beta tucked. 05-06: beta low, alpha raised. 07-00: alpha returns low, beta returns tucked. '+('03-04: overlap makes the exact exchange assignment uncertain; a consistent hidden-role reading remains possible.' if v=='A' else '03: both visible during convergence. 04: beta becomes low and alpha is raised; the separation makes the exchange legible.'),
    'interchange_finding':'No definite anatomical foot interchange demonstrated. A screen-side assumption or equal-sole-Y test was not used.'},
   'cels':cels,'cyclic_pairs':pairs})
report={
 'status':'frozen single-pass review of unchanged anonymous inputs',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':{'input_root':str(ROOT),'output_root':str(OUT),'input_manifest_sha256':hashlib.sha256((ROOT/'INPUTS.json').read_bytes()).hexdigest(),
  'input_images':63,'walk_cels':32,'cyclic_pairs':32,'canvas':[128,128],'game_scale':0.66,'proxy_canvas':[84,84],
  'holds_rational':m['holds'],'each_hold_seconds':float(Fraction(9,160)),'loop_seconds':float(Fraction(9,20)),
  'views':['native128','nearest2x256','nearest84px proxy'],'backgrounds':{'light':'#e8e7db','dark':'#181e27','ground':'#576546'},
  'context_use':'Identity and turn context only; appearance source also inspected at its native 768x256 size.',
  'outside_material_read':False,'input_mutation':False,'canonical_repo_access':False},
 'verification':{'before':{'verified':63,'mismatches':0},'after':{'verified':63,'mismatches':0},'before_equals_after':True,
  'art_credit_for_hashes_source_exactness_or_frame_count':False},
 'rating_scale':'Absolute subjective 0-10: 0 unusable, 5 recognizable but visibly rough, 10 exceptional finished art for this compact RPG use. Decimal differences are judgments, not measurements.',
 'ratings':ratings,'preferred_for_game':'B, by a modest margin for clearer two-boot exchange; neither is an unqualified polished-motion approval.',
 'comparison':'A has slightly more cohesive rounded lower-body rendering in individual cels. B improves separation in 03/04/07 but introduces visible trouser/cuff and whole-boot volume pulses. Identity and upper-body animation are effectively tied. The five identical cels per direction receive the same assessment.',
 'shared_findings':[
  'Strong hair, face, blue/gold tunic and silver shoulder identity at native and 84px. Directional reading is appropriate for three-quarter top-down RPG art.',
  'Both read as a compact walk through chronological poses. The low-motion 00->01 and quick 06->07 return make the cadence less even than a polished cycle.',
  'Arm/shoulder response is small and the torso/head are fairly rigid apart from bob. This supports subtle walking but provides little extra help during ambiguous leg phases.',
  'Brown boot boundaries lose some separation on dark ground; warm highlights preserve the outer forms. B retains the clearer two-boot gap at the central exchange.',
  'No adjacent pair is an exact duplicate. Unique frames do not by themselves prevent perceptual false holds.',
  'No equal sole-Y rule was applied: offset soles and foreshortening are appropriate to this projection.'],
 'sequences':sequences,
 'smallest_meaningful_next_repair':{'preferred_variant':'B','priority':'First repair 06->07->00 in both directions: redraw only the bent trouser/cuff and raised whole boot so the knee, cuff, shaft and toe keep compatible volumes through recovery. Preserve two-boot separation and existing upper body.',
  'secondary':'Then smooth 03->04->05 by keeping the newly low trouser and boot volume closer to neighboring poses. Do not obtain separation by making a narrow shin in 03 and an inflated one in 04.',
  'if_retaining_A':'Clarify the rear boot/cuff silhouette in 03 and 04, checking 02->03->04->05 as a unit. Preserve legitimate overlap rather than forcing both soles onto one horizontal line.',
  'deferred_shared':'Only after the local repairs, consider small leg/cuff travel in 00->01 to lessen the plateau; do not add frames solely to increase the count.'},
 'perception_limits':[
  'Viewed static source cels, ordered strips and all eight cyclic adjacent pairs. No continuous human playback was observed.',
  'Still chronology cannot establish continuous perceived cadence at the exact 56.25ms hold, nor certify physical world contact, planting, friction or gameplay translation.',
  'The 84px nearest-neighbor proxy approximates the stated 0.66 canvas scale; engine filtering, display scale, camera and actual terrain may differ.',
  'Projected roles can be followed with better confidence in B; A overlap prevents certainty at 03-04. This uncertainty is a readability finding, not proof of a foot swap.'],
 'artifacts':{'whole_cel_sheets':9,'context_sheet':1,'cyclic_pair_sheets':4,'pixel_counts':'diagnostic-pixel-counts.json; raw RGBA difference counts only, not aesthetic evidence','hash_ledger':'SHA256SUMS'}
}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# Anonymous complete-boots review — frozen','',
'B is the more useful game candidate by a modest margin. It keeps two boots legible through the central exchange; A has slightly more cohesive rounded rendering, but its overlap makes the step harder to read. Neither earns an unqualified polished-motion approval.','',
'| Variant | Appearance | Identity | Motion readability | Game usefulness |','|---|---:|---:|---:|---:|']
for v in ['A','B']:
 r=ratings[v];lines.append(f"| {v} | {r['appearance']:.1f} | {r['identity']:.1f} | {r['motion_readability']:.1f} | {r['game_usefulness']:.1f} |")
lines += ['', 'These are absolute subjective 0–10 ratings for this compact RPG use: 0 unusable, 5 recognizable but visibly rough, 10 exceptional finished work. SE and SW received the same ratings after separate inspection. Hash correctness, source exactness and frame count receive no art credit. No unchanged art was rerated.','',
'## Evidence and scope','',
'Only the nominated input directory was read. All 63 image SHA-256 values matched before and after review, and the two checks agree. All 32 walk cels and all 32 cyclic pairs were inspected, including 07→00 for A/B in SE/SW. Nine full-cel sheets show every cel at native 128px, nearest 2× and an 84px proxy, each on light, dark and ground backgrounds. Four additional lower-body pair sheets cover every cyclic transition. Context images establish identity/turn only; the appearance image was also viewed at native size. Inputs and the canonical repo were not changed.','',
'Timing supplied: eight holds of 9/160s = 56.25ms, loop 9/20s = 0.45s. The 84px nearest proxy approximates the 128×0.66 canvas; actual engine sampling can differ.','',
'## Findings','',
'- Both retain strong hair, face, costume and armor identity at game scale. The silhouette and material colors suit the requested stylized three-quarter RPG view.',
'- A 02→03→04→05: boots converge into a nearly single silhouette, the pale shin/cuff rotates across the overlap, and the rear role reappears abruptly. The larger round shapes are attractive in a still, but the exchange is hard to follow at 84px.',
'- B 02→03→04→05: separation gives a clearer role exchange. In 03 the trouser columns become narrow and straight; in 04 the newly low knee/boot becomes fuller, then narrows/turns in 05. Whole boots are visible, but the volumes do not yet feel fully stable.',
'- B 06→07→00: the recovery trouser/cuff joins pinch and the raised boot shaft foreshortens sharply in 07, then volume restores at 00. This is its most useful next repair.',
'- Shared 00→01 has little leg-silhouette travel and risks a perceived hold. A 07→00 extends that similar forward/tucked arrangement. No adjacent frames are exact duplicates; uniqueness is not motion quality.',
'- Shared 05→06 remains readable. The large lifted knee is stylized but attached. Arm/shoulder action is shallow and torso/head response is mostly bob, offering limited help during ambiguous leg phases.',
'- Dark backgrounds reduce separation of the darkest boot edges. Warm highlights preserve outer form; B keeps the more useful central two-boot separation. There is no broad background-dependent disappearance.','',
'## Persistent projected roles','',
'Alpha is the low/forward boot in 00 (SE screen right; SW screen left). Beta is the opposite higher/tucked boot. These are persistent projected roles, not anatomical left/right labels. Alpha is low in 00–02; beta is low in 05–06; alpha returns low through 07→00. In A, 03–04 hides enough of the exchange that assignment is uncertain, but a consistent hidden-role reading remains possible. In B both are visible in 03 and beta is clearly low while alpha is raised in 04. I do not find a demonstrated anatomical interchange. I did not require equal sole Y in this perspective.','',
'## Cel coverage','',
'Each note below was checked separately in both directions; the projected screen sides reverse.','',
'| Cel | A | B |','|---|---|---|']
for i in range(8):
 k=f'{i:02}';a=common_cels.get(k,variant_cels['A'].get(k));b=common_cels.get(k,variant_cels['B'].get(k));lines.append(f'| {k} | {a} | {b} |')
lines += ['', '## Every cyclic pair','', 'The following applies to each separately inspected SE and SW sequence, with mirrored projected sides. Full per-sequence records are in report.json.','', '| Pair | A | B |','|---|---|---|']
for i in range(8):
 p=f'{i:02}->{(i+1)%8:02}';a=common_pairs.get(p,variant_pairs['A'].get(p));b=common_pairs.get(p,variant_pairs['B'].get(p));lines.append(f'| {p.replace("->","→")} | {a[0]}: {a[1]} | {b[0]}: {b[1]} |')
lines += ['', '## Smallest meaningful next repair','', report['smallest_meaningful_next_repair']['priority'], '',report['smallest_meaningful_next_repair']['secondary'],'', report['smallest_meaningful_next_repair']['if_retaining_A'],'',
'After those local repairs, a small amount of leg/cuff travel in 00→01 could reduce the plateau. Increasing frame count alone would not address it.','',
'## Perception limits','',
'This is static-cel, ordered-strip and adjacent-pair perception. I did not observe continuous human playback at the exact holds. Still chronology cannot certify continuous cadence or physical world contact, planted feet, friction, or behavior while the game actor translates. The suggested repair is based on visible shape continuity and game-scale readability.','',
'## Artifacts','',
'- `sheet-{native,nearest2x,proxy84}-{light,dark,ground}.png`: every whole cel at all requested scales/backgrounds.',
'- `pairs-{A,B}-{southeast,southwest}-lower4x-ground.png`: all eight cyclic pairs per sequence, including the loop.',
'- `context-identity-turn-only.png`: identity/turn context only.',
'- `input-hashes-before.json`, `input-hashes-after.json`: 63/63 matches and unchanged inputs.',
'- `diagnostic-pixel-counts.json`: raw RGBA counts only; not art quality metrics.',
'- `report.json`: ratings, every cel/pair, role tracking and limits.',
'- `SHA256SUMS`: frozen output ledger, excluding itself.','']
(OUT/'report.md').write_text('\n'.join(lines))
# Freeze once: complete report and ledger are never rewritten by this script.
ledger=[]
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS':
  ledger.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}")
(OUT/'SHA256SUMS').write_text('\n'.join(ledger)+'\n')
for p in OUT.rglob('*'):
 if p.is_file():p.chmod(0o444)
print(json.dumps({'status':'frozen','before_verified':63,'after_verified':63,'walk_cels':32,'cyclic_pairs':32,'ratings':ratings,'ledger_entries':len(ledger),'report_sha256':hashlib.sha256((OUT/'report.md').read_bytes()).hexdigest(),'json_sha256':hashlib.sha256((OUT/'report.json').read_bytes()).hexdigest(),'ledger_sha256':hashlib.sha256((OUT/'SHA256SUMS').read_bytes()).hexdigest()},indent=2))

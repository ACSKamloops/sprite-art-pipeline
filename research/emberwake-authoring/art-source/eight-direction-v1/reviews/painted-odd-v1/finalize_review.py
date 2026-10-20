from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
BASE=Path('/home/astra/artifacts/emberwake-painted-odd-review/input-v1')
OUT=Path('/home/astra/artifacts/emberwake-painted-odd-review/review-v1')
assert not (OUT/'report.md').exists(), 'Final judgment already exists; do not rerate unchanged inputs.'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data): (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
m=json.loads((BASE/'INPUTS.json').read_text())
items=[x for v in m['variants'].values() for seq in v.values() for x in seq]+m['context']
before=json.loads((OUT/'input-hashes-before.json').read_text())
checks=[]
for x in items:
 h=sha(BASE/x['path'])
 checks.append({'path':x['path'],'expected_sha256':x['sha256'],'actual_sha256':h,'match':h==x['sha256']})
after={'inputs_json_sha256':sha(BASE/'INPUTS.json'),'count':len(checks),'inputs':checks}
assert len(checks)==63 and all(x['match'] for x in checks)
assert before['inputs_json_sha256']==after['inputs_json_sha256']
assert {x['path']:x['actual_sha256'] for x in before['inputs']}=={x['path']:x['actual_sha256'] for x in checks}
dump('input-hashes-after.json',after)
A={
 '00->01':'The forward/downscreen boot and tucked rear boot remain easy to recognize, but the stride silhouette advances very little. Cloth stays rounded and attached.',
 '01->02':'The boots draw into a narrower arrangement; their separate brown shapes remain legible. This is a modest progression rather than a strong opposing-leg beat.',
 '02->03':'Leg overlap increases. The exposed forward boot remains whole, while tracing the other calf through the overlap becomes harder.',
 '03->04':'The main pale thigh lengthens into the boot. Small pale side tabs at the upper leg in 04 break the otherwise rounded cloth contour.',
 '04->05':'The thighs and boots compress into a close overlap. The brown boot masses and large pale thigh do not clearly explain which leg is passing and which is supporting.',
 '05->06':'The raised pale knee and more open boot arrangement arrive in a conspicuous step. The bridge into this pose is weaker than its individual drawing.',
 '06->07':'The raised-knee arrangement returns rapidly toward the opening stride. This feels like a bigger silhouette release than the early links, based on still chronology.',
 '07->00':'Body placement and the main stride silhouette are close, so there is no conspicuous whole-body seam. The risk is a held-looking opening region rather than a clearly continuous through-step.'
}
B={
 '00->01':'The tucked leg gains an angular, hollow-looking cream cuff/fold. The exposed boot is still whole, but the material shape changes more clearly than the leg role.',
 '01->02':'The hollow/ring-like cream fold returns to a solid rounded thigh shape. That local material change distracts from the modest leg progression.',
 '02->03':'Cream folds flatten and sprout angular horizontal tabs near the pelvis. The thigh-to-boot route becomes harder to read through the overlap.',
 '03->04':'The angular cream edge in 03 resolves into a longer main thigh while side tabs remain visible in 04. The two leg roles remain crowded together.',
 '04->05':'The pale shape becomes a broad bent shelf across the pelvis while the boots form a narrow stack below it. This is the least convincing material/limb transition.',
 '05->06':'The horizontal pale shelf changes back into two rounded thigh masses and a raised-knee pose. The knee pose is readable alone, but the shape change is abrupt.',
 '06->07':'The open raised-knee arrangement returns to the tucked boot and hollow-looking cream fold. The short bridge and changing cuff construction weaken continuity.',
 '07->00':'The hollow-looking fold closes into the rounded cream construction of 00. Body placement remains close, but the local cuff shape still changes at the seam.'
}
ratings={
 'A':{'appearance':7.5,'identity':8.5,'motion_readability':5.5,'game_usefulness':6.5},
 'B':{'appearance':6.0,'identity':8.0,'motion_readability':4.5,'game_usefulness':5.5}
}
coverage={
 'nominated_images_inspected':63,
 'variant_walk_cels':32,
 'context_images':31,
 'source_appearance_viewed_directly':'context/appearance.png',
 'diagnostic_pngs_generated_and_viewed':sorted(p.name for p in OUT.glob('*.png')),
 'walk_review_conditions':{'directions':['southeast','southwest'],'variants':['A','B'],'stages_px':[128,256,84],'resampler':'nearest neighbor','backgrounds':{'dark':[24,28,35],'light':[235,231,219],'ground':[92,102,73]}},
 'all_cyclic_pairs_explicitly_inspected':['00->01','01->02','02->03','03->04','04->05','05->06','06->07','07->00'],
 'pair_coverage':'All eight cyclic links for each of the four variant/direction sequences, on each of the nine stage/background conditions. Chronology sheets append 00 after 07.',
 'supplementary_inspection':'Six lower-body crop sheets: source x38..94 and y72..122 at nearest 4x on all three backgrounds.',
 'context_coverage':'All south/east/west idle and walk images were inspected on the same three stage sizes and three backgrounds. Context walk rows also append walk 00 after 07.',
 'limits':['Still images and ordered adjacent-pair comparisons only.','No physical or continuous human playback claim.','No integrated game movement, camera, collision, or foot-contact validation.']
}
assert len(coverage['diagnostic_pngs_generated_and_viewed'])==33
dump('inspection-coverage.json',coverage)
review={
 'status':'FINAL_FROZEN_SINGLE_JUDGMENT',
 'blind_scope':'Only INPUTS.json and its 63 nominated images were read as source evidence. No mapping, project documents, history, skills, or other reviews/scores were read.',
 'target_score_supplied':False,
 'actor':m['actor'],
 'stage':[128,128],'pivot':[64,112],
 'nominal_game_scale':0.66,'proxy_stage':[84,84],'proxy_scale':84/128,
 'holds_seconds':[9/160]*8,'duration_seconds':9/20,
 'ratings_scale':'0 to 10. Separate editorial judgments; 10 means exceptionally resolved for the stated use, 5 means visibly compromised but partly usable. These are not measured performance scores.',
 'ratings_by_variant':ratings,
 'ratings_by_variant_and_direction':{v:{d:dict(ratings[v]) for d in ('southeast','southwest')} for v in ('A','B')},
 'direction_rating_note':'The two directions show the same substantive strengths and problems, with opposing screen-side orientation. There is no convincing visual basis for different numerical scores.',
 'preference':{'southeast':'A','southwest':'A','overall':'A','strength':'Clear at native/2x; smaller but still present at the game proxy. Neither is a fully resolved walk.'},
 'appearance_findings':{
  'A':'Appealing painted-pixel fantasy adventurer. Rounded cream trousers, brown boots, silver armor, gold-trimmed blue tunic, hair and face mostly retain a coherent construction. Upper-thigh tabs in 04 and crowded overlap in 03-05 remain rough.',
  'B':'The upper body remains appealing, but 01/07 have hollow/ring-like tucked-leg cream folds, 03 has angular horizontal tabs, and 05 has a broad bent cream shelf and a crowded brown boot stack. These read as changing cloth construction rather than a clearer knee arc.'
 },
 'identity_findings':'Both retain the appearance reference and cardinal identity: orange-brown spiky hair, blue eyes, blue/gold tunic, silver pauldrons/bracers, brown gloves/boots, cream trousers, chibi proportions. B loses some local costume consistency through trouser/cuff shapes; it does not become a different character.',
 'leg_joins_and_material':'A keeps more believable rounded thigh/cuff volumes. Both have visible pale side tabs in 04 and hard-to-trace leg overlap. B adds more angular and hollow-looking cream forms in 01/03/05/07, especially the 05 pelvis shelf. No bonus was given for a change being present.',
 'complete_boots':'The exposed boots retain toe/heel silhouettes and are not cut off at the stage edge. The problem is not an obvious missing boot. In overlaps, especially B 03/05 and both variants 04/05, two complete shin-to-foot paths cannot be confidently traced from the stills. B 05 reads as stacked/fused brown forms.',
 'gait_roles_and_cycle':'A is easier to parse because the materials remain steadier. Neither has a consistently clear alternating support/passing/swing presentation. The opening region progresses little; 04-05 compress; 06 gives a conspicuous raised-knee opening; 07 quickly returns toward 00. B increases local shape change without resolving those roles.',
 'entry_and_turn_context':'At the stated stage/pivot, both retain a compatible head/torso size and direction cue against the south/east/west context. A is the safer costume match. The diagonals have more compressed leg separation than the east/west walks. Starting at 00 requires a visible change from the broad cardinal idle stance; this is plausible as an entry but not validated as a continuous turn. Shared indices do not establish matching foot phases.',
 'scale_and_backgrounds':'Dark and ground backgrounds preserve the bright face/armor/cloth hierarchy. Light background exposes outlines and the odd cream notches more clearly. At 84px the face/armor and overall facing survive; fine cuff detail collapses, but B 03/05 still changes the pale waist/leg mass into a stripe/shelf. The background changes do not reverse the preference.',
 'pair_notes':{v:{d:dict(A if v=='A' else B) for d in ('southeast','southwest')} for v in ('A','B')},
 'smallest_justified_next_repair':{'base':'A','cels':['southeast/05','southwest/05'],'instruction':'Make one focused lower-body bridge repair in 05 per direction. Keep the costume and complete boot toe/heel shapes; make one leg visibly pass behind the other with connected rounded cream thigh-to-brown boot shafts. Judge 04->05->06 and the wrap at 84px before any wider redraw. Clean 04 side tabs only if the same join repair requires it.','why':'The 05 overlap is the smallest localized target that addresses the weak bridge into the raised-knee 06 pose without importing B\'s material-shape problems.'},
 'claims_not_made':['Smoothness at the prescribed 56.25 ms exposure has not been observed in continuous human playback.','No physical planting, weight transfer, sliding, or gameplay acceptance claim.','The 84px nearest-neighbor proxy is not an actual integrated 0.66-scale game capture.'],
 'judgment_basis':'Actual drawings and still chronology. No credit for changed pixels, exact maps, frame count, or metadata.',
 'input_binding':{'count':63,'all_expected_hashes_match_before':True,'all_expected_hashes_match_after':True,'all_before_after_hashes_identical':True,'inputs_json_sha256':after['inputs_json_sha256'],'before_manifest':'input-hashes-before.json','after_manifest':'input-hashes-after.json'},
 'coverage_file':'inspection-coverage.json',
 'finality':'This is the single final judgment for these unchanged inputs. Do not rerate them after finalization.'
}
dump('review.json',review)
report='''# Blind painted-walk review — final

**A is preferable for both southeast and southwest.** Its trousers and boots maintain a more coherent construction. B changes the leg shapes more, but the changes do not clarify the gait enough to offset angular cloth edges, hollow-looking cuffs, and the broad pale shape in cel 05. Neither version is a fully resolved walk.

| Variant | Appearance | Identity | Motion readability | Game usefulness |
|---|---:|---:|---:|---:|
| A | 7.5/10 | 8.5/10 | 5.5/10 | 6.5/10 |
| B | 6.0/10 | 8.0/10 | 4.5/10 | 5.5/10 |

The same scores apply separately to southeast and southwest: they show the same substantive strengths and defects in opposite screen-side orientations. These are editorial judgments, not measured performance scores. No target score was supplied.

## Appearance, identity, and joins

Both retain the reference character well: orange-brown spiky hair, blue eyes, silver pauldrons and bracers, blue tunic with gold trim, brown gloves and boots, cream trousers, and the same compact proportions. The head and upper body remain attractive and readable at the game proxy. A is the better local costume match; B's trouser construction changes do not destroy identity, but do weaken it.

A's cream thigh shapes are usually rounded and attached convincingly to brown boot shafts. It still has small pale side tabs at the upper leg in 04, and the 03–05 leg overlap is crowded. B's tucked-leg cream folds in 01 and 07 look hollow or ring-like; 03 adds sharp horizontal pale tabs; 05 flattens the pale thigh/fold into a broad bent shelf across the pelvis. The resulting material changes are more noticeable than a consistent knee or calf arc. This finding applies to both directions.

The exposed boots retain readable toes and heels; none is obviously clipped at the stage edge. I would not call these missing-boot drawings. The weakness is tracing two connected shin-to-foot paths through the overlap. In B 03/05, especially 05, the brown feet read as a narrow stack or fused shapes beneath the pale shelf. A is cleaner, though its 04/05 overlap is also hard to untangle.

## Gait and every cyclic link

The following notes apply independently to both directions. Each link was inspected in each variant at native 128, nearest 2x, and the rounded 84/128 game proxy, on dark, light, and ground backgrounds. Every chronology row repeats 00 after 07.

| Link | A | B |
|---|---|---|
| 00→01 | Very little silhouette progression; forward and tucked boots remain recognizable and cloth stays rounded. | A hollow-looking cream cuff/fold appears on the tucked leg without making its role clearer. |
| 01→02 | Boots narrow toward one another; separate boot shapes survive. | The hollow fold returns to solid rounded cloth, creating a material change alongside the small leg progression. |
| 02→03 | Overlap increases; the exposed boot is whole but the other calf becomes hard to trace. | Angular pale tabs and flattened folds make the thigh-to-boot path harder to follow. |
| 03→04 | Main thigh lengthens into the boot; pale upper-leg side tabs in 04 break the contour. | Longer thigh replaces the angular 03 form; side tabs remain and the leg roles stay crowded. |
| 04→05 | Thighs and boots compress together; passing versus supporting role is weak. | Broad pale shelf and narrow brown boot stack give the least convincing material/limb transition. |
| 05→06 | Raised pale knee and open boots arrive in a conspicuous step; the bridge is weak. | Pale shelf changes back into rounded thigh masses; the isolated knee pose is clearer than its approach. |
| 06→07 | Raised knee releases rapidly toward the opening stride. | Returns rapidly to tucked boot and hollow-looking cuff. |
| 07→00 | Close body/stride placement avoids a large whole-body seam; the opening region risks reading held. | Body placement is close, but the hollow cuff closes back into rounded cloth at the seam. |

A therefore reads as a walk more readily, but neither presents a reliably clear alternating support/passing/swing pattern. The early silhouette changes little, 04–05 compress, 06 opens into a pronounced raised-knee arrangement, then 07 returns quickly. At the prescribed 9/160-second exposures, that uneven distribution suggests a stutter or prancing risk; it is an inference from still chronology, not a witnessed playback result. B's additional local changes do not solve it.

## Scale, backgrounds, and context

A's advantage is clear at native and 2x. At 84px the fine cuff detail mostly collapses, so the advantage becomes smaller. B 03/05 still alters the pale waist/leg mass into a stripe or shelf, while the two boot roles remain compressed. Dark and ground backgrounds retain the bright face, armor, and cloth hierarchy. Light makes the outlines and pale notches more conspicuous. None reverses the preference.

All south/east/west idle and walk context images were inspected at the same three stage sizes and backgrounds, plus the appearance image directly. Both variants keep a compatible head/torso size and a recognizable diagonal direction cue. The diagonal legs are more compressed than the east/west walk context. Cel 00 changes visibly from the broad cardinal idle stance; it is a plausible entry drawing, but a continuous turn has not been validated. Matching frame numbers do not establish matching foot phases between directions.

## Smallest justified repair

Use **A** as the base and repair **05 in each direction** as one focused lower-body bridge into 06. Make one leg visibly pass behind the other, with rounded, connected cream thigh-to-brown boot shafts and preserved complete toe/heel silhouettes. Inspect 04→05→06 at 84px and the wrap before expanding the work. Clean 04's side tabs only if the same join repair requires it. This is a smaller and better-supported next step than adopting B's trouser changes wholesale.

## Scope, evidence, and finality

Only INPUTS.json and its 63 nominated images were source evidence. No parent mapping, project documents, history, skills, or other reviews/scores were read. I generated and viewed 33 bounded diagnostic PNGs, including the full walks, cardinal context, and lower-body crops. Coverage and all pair notes are recorded in inspection-coverage.json and review.json.

The intended stage is 128×128 with pivot (64,112). The nominal game scale is 0.66; the nearest-neighbor 84×84 proxy is 84/128 = 0.65625 after rounding. Each exposure is 9/160 seconds = 56.25 ms; eight exposures total 9/20 seconds = 0.45 s. No credit was given for changed pixels, exact maps, frame count, or metadata.

This is a still-chronology review. It makes no physical or continuous human playback claim, no confirmed foot planting or weight-transfer claim, and no integrated game/camera/collision acceptance claim.

All 63 image SHA-256 values matched INPUTS.json before and after review, and all before/after hashes—including INPUTS.json itself—are identical. The complete bindings are in input-hashes-before.json and input-hashes-after.json. OUTPUTS.sha256 freezes the report, review JSON, diagnostics, coverage, hash records, and generation scripts. FINALIZATION.json records the freeze digest. This is the single final judgment for these unchanged inputs; it is not to be rerated after finalization.
'''
(OUT/'report.md').write_text(report)
# Freeze all completed outputs except the manifest itself and its finalization receipt.
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name not in ('OUTPUTS.sha256','FINALIZATION.json'))
(OUT/'OUTPUTS.sha256').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
receipt={
 'status':'FROZEN','finalized_at_utc':datetime.now(timezone.utc).isoformat(),
 'report_sha256':sha(OUT/'report.md'),'review_json_sha256':sha(OUT/'review.json'),
 'output_manifest_sha256':sha(OUT/'OUTPUTS.sha256'),
 'manifest_file':'OUTPUTS.sha256','manifest_bound_files':len(files),
 'manifest_exclusions':['OUTPUTS.sha256 (cannot hash itself)','FINALIZATION.json (receipt created after manifest)'],
 'input_sha256_before_after_identical':True,'nominated_input_images':63,
 'unchanged_input_rerating_prohibited':True
}
dump('FINALIZATION.json',receipt)
# Read-only permissions express finality; hashes are the verifiable binding.
for p in OUT.iterdir():
 if p.is_file():p.chmod(0o444)
OUT.chmod(0o555)
print(json.dumps(receipt,indent=2))

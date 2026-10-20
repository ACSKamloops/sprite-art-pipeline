from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path('/home/astra/artifacts/emberwake-five-bridge-review/input-v1')
OUT=Path('/home/astra/artifacts/emberwake-five-bridge-review/review-v1')
D=json.loads((ROOT/'INPUTS.json').read_text())
entries=[e for ds in D['variants'].values() for es in ds.values() for e in es]+D['context']
before=json.loads((OUT/'input-hashes-before.json').read_text())
checks=[{'path':e['path'],'expected':e['sha256'],'actual':hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()} for e in entries]
for e in checks:e['match']=e['expected']==e['actual']
assert len(checks)==63 and all(e['match'] for e in checks)
assert {e['path']:e['actual'] for e in checks}=={e['path']:e['actual'] for e in before['files']}
meta_hash=hashlib.sha256((ROOT/'INPUTS.json').read_bytes()).hexdigest()
assert meta_hash==before['inputs_json_sha256']
stamp=datetime.now(timezone.utc).isoformat()
after={'verified_at_utc':stamp,'count':63,'all_match':True,'unchanged_since_before':True,'inputs_json_sha256':meta_hash,'files':checks}
(OUT/'input-hashes-after.json').write_text(json.dumps(after,indent=2)+'\n')
scores={'A':{'appearance':7.9,'identity':9.0,'motion_readability':5.4,'game_usefulness':6.1},'B':{'appearance':8.1,'identity':9.0,'motion_readability':6.1,'game_usefulness':6.7}}
pairs=[
{'pair':'00->01','shared':'The same extended/down leg remains dominant; small body and thigh changes make a readable but rather held first stride.'},
{'pair':'01->02','shared':'That down leg gathers under the body while the other boot remains tucked; connected enough to follow.'},
{'pair':'02->03','shared':'The legs compress/overlap sharply. Cream thigh volume becomes rounder and boot separation weakens; this is a visible phase/compression change.'},
{'pair':'03->04','shared':'The low boot re-extends on the same projected side. A sustained opposite-leg stance is still not established.'},
{'pair':'04->05','A':'The low boot stays on the dominant side, with the other thigh/boot crowded behind it. The shape is connected but the two roles are difficult to separate.','B':'Two connected cream thighs and two distinct boot cuffs appear; the lower boot moves toward the opposite projected side, anticipating 06. The lateral change from 04 remains noticeable.'},
{'pair':'05->06','A':'The opposite raised knee and lower boot appear abruptly; this is the worse local handoff.','B':'The separated legs already predict 06, so this handoff reads more coherently. Knee size and sole height still change visibly.'},
{'pair':'06->07','shared':'The clearest remaining reset: the opposite-leg configuration gives way immediately to the dominant extended-leg arrangement. The returning/swing boot has too little visible intermediate travel.'},
{'pair':'07->00','shared':'Leg silhouette and sole positions are comparatively close. Small upper-body/arm changes can still flick, but the wrap itself is not the principal break.'}
]
assessment={
'status':'frozen','frozen_at_utc':stamp,'independence':'Read only INPUTS.json, its 63 nominated PNGs, and files created in this fresh review directory. No project documents, parent mapping/history, other grades, or canonical art were read. No source/canonical edits.',
'inputs':{'root':str(ROOT),'png_count':63,'all_hashes_match_before_and_after':True,'unchanged':True,'inputs_json_sha256':meta_hash},
'presentation':{'stage':[128,128],'pivot':[64,112],'specified_game_scale':0.66,'proxy_stage':[84,84],'proxy_scale':84/128,'holds_rational_seconds':[[9,160]]*8,'loop_duration_rational_seconds':[9,20],'native_stage':128,'nearest_enlargement':2,'backgrounds':['dark','light','synthetic_ground'],'additional_closeups':'Nearest 3x all lower bodies and nearest 4x 04/05/06 lower bodies; source-aligned crop x40:91 y68:118.'},
'coverage':{'variant_cels':32,'identity_context_images':31,'cyclic_adjacent_pairs':32,'variant_overview_sheets':9,'cyclic_pair_sheets':4,'context_sheets':2,'lower_body_sheets':3,'all_generated_pngs_viewed':True},
'score_scale':'Subjective 0-10: 0 unusable, 5 serviceable with clear defects, 8 strong, 10 exceptional. Scores concern visible art and projected motion; no credit for hashes, export mechanics, frame count, or changed-pixel count.',
'scores':scores,
'overall_preference':'B, modest whole-loop preference; clear local preference at cel 05 in both facings.',
'local_changed_region':{'preferred':'B','confidence':'moderate-high for still appearance; moderate for chronological motion inference','southeast':'B05 separates the cream thighs and attaches each to a legible brown boot/cuff. The screen-left/lower boot and screen-right/higher boot form a clearer bridge into 06 than A05, whose rear leg is crowded behind the large forward thigh.','southwest':'The corresponding improvement is mirrored: lower screen-right boot and higher screen-left boot are easier to trace into 06.','material_and_connection':'Neither B05 thigh or boot appears detached. Cream fabric stays cream and the brown cuffs/creased shafts retain boot volume. The paired rounded knees are somewhat puffy relative to the narrower diagonal thigh at 04, so the repair is not invisible.','scope':'Only cel 05 differs. This locates the comparison and is not artistic merit.'},
'projected_roles':{'southeast':'In 00-04 the lower/extended boot is predominantly on screen right while the other is tucked/overlapped. B05 begins a clearer exchange to a lower screen-left boot and higher screen-right knee/boot, followed by 06. A05 makes that exchange harder to see. 07 returns immediately to the dominant screen-right-low arrangement.','southwest':'The same pattern is mirrored: screen-left-low dominates 00-04; B05 and 06 expose screen-right-low with the other knee/boot higher; 07 returns quickly to screen-left-low.','interpretation':'These are projected candidate support/recovery roles traced from hip-thigh-cuff continuity, relative knee heights, and soles. They do not establish a physically planted foot or anatomical left/right through every overlap.'},
'appearance_and_identity':{'strengths':['Distinct orange-brown spiky hair, blue eyes, navy tunic with gold edging, silver shoulder/forearm armor, cream trousers, and brown gloves/boots match the appearance and south/east/west context.','Head, chest, palette, and armor retain identity across every cel. Direction and two-leg silhouette remain readable at the 84-stage proxy on all three backgrounds.','Silvery armor and warm hair separate well; the cream thighs preserve lower-body readability when dark brown boots merge toward the dark/ground backgrounds.'], 'weaknesses':['Cream knee/thigh volume changes substantially at compressed poses, especially 03 and 06; the lower body can puff outward instead of rotating with stable volume.','A05 crowds the two legs. B05 is clearer but has rounded paired knee masses that remain slightly different from 04.','Arm cues are fairly restrained; they do not strongly clarify the ambiguous leg-role timing.']},
'cyclic_pair_findings_for_both_facings':pairs,
'whole_cycle_defects':['The step is asymmetric in visible role timing: one extended/down-leg configuration occupies most of the cycle, and the opposing configuration is brief.','06->07 remains an abrupt role/silhouette reset in both versions. B05 improves the preceding bridge but cannot repair this unchanged transition.','Soles rise and knee masses spread at 06, which permits a small hop/skip reading in still chronology. Actual airborne/contact states are unverified.','02->03 compression and 03->04 re-extension do not supply a clean opposite stance; stable lower-limb volume remains imperfect.'],
'game_usefulness':'B is usable for a prototype or a less scrutinized small NPC walk. For a featured player character, the repeated asymmetry/reset would still draw attention. The local B05 improvement survives the proxy, but does not make this a polished final walk.',
'smallest_justified_next_repair':{'target':'Lower body of cel 07 in each diagonal facing, using B05 as the retained local option.','action':'Make 07 a genuine intermediate from 06 to 00 instead of an almost-returned dominant stride: carry the candidate support boot from 06 on a shorter coherent projected path and advance the opposite swing boot toward 00 with connected hip-thigh-cuff shapes. Preserve upper-body identity, palette, holds, stage, and pivot.','reason':'This spreads the remaining 06->07 reset across 06->07->00 and addresses the most obvious unchanged break without reopening the whole sprite.','qualification':'One cel may reduce the snap without fully balancing the half-cycle. If the role path still cannot be followed, revise phase blocking before more surface polish.'},
'limits':['This is an AI still-image and chronological adjacent-pair assessment, not a continuous human playback evaluation.','The specified holds are 9/160 s per cel (56.25 ms), total 0.45 s, but I did not certify real-time playback or perceptual cadence at that speed.','The 84/128 nearest proxy approximates game scale 0.66; exact engine sampling, scaling alignment, motion translation, shadows, and game context were not exercised.','A synthetic ground background tests visual separation only. No world-space foot plant, contact timing, sliding, root-motion correspondence, or in-engine behavior is certified.','Scores are subjective, with lower confidence for motion than identity/appearance; no target score was supplied.'],
'diagnostic_outputs':sorted(p.name for p in OUT.glob('*.png')),
'freeze':'Written once after the final source-hash verification. Do not reread or rerate unchanged art after this freeze; OUTPUTS.sha256 covers every output file except itself.'
}
report=f'''# Independent blind A/B walk review — frozen

Frozen: {stamp}

**Prefer B modestly for the complete loops, and clearly at cel 05 locally, in both southeast and southwest.** B05 is a useful lower-body bridge; the whole cycle still has an uneven leg-role pattern and a conspicuous unchanged 06→07 reset. This is not a polished final walk.

| Visible-art score, 0–10 | A | B |
|---|---:|---:|
| Appearance | 7.9 | 8.1 |
| Identity | 9.0 | 9.0 |
| Motion readability | 5.4 | 6.1 |
| Game usefulness | 6.1 | 6.7 |

These are subjective whole-loop scores: 5 is serviceable with clear defects, 8 strong, and 10 exceptional. Motion is a chronological visual inference, with lower confidence than appearance/identity. Hashes, changed pixels, frame count, maps, and export mechanics receive no art credit. No target score was supplied.

## Local 04→05→06 finding

B05 gives each cream thigh a readable connection into its own brown cuff, shaft, and boot. In southeast, the lower screen-left boot and higher screen-right boot anticipate 06; southwest mirrors this arrangement. A05 keeps a large forward cream thigh with the other leg crowded behind it, so the opposite raised knee in 06 arrives less intelligibly. B's improvement remains visible at native size and the small 84-stage proxy on dark, light, and synthetic ground backgrounds.

The B limbs do not look detached. The boot cuffs remain creased volumes rather than floating feet, and the cream/brown material boundary survives the edit. B05 does introduce fairly rounded, paired knee masses relative to 04's narrow diagonal thigh; the volume change and 04→05 lateral foot shift are still visible. This is a better bridge, not an invisible or complete gait repair.

## Projected leg roles and every cyclic pair

In southeast 00–04, the lower/extended boot is predominantly screen right and the other boot is tucked or overlapped. B05 begins the exchange to a lower screen-left boot and a higher screen-right knee/boot, which 06 continues. A05 obscures that exchange. In southwest these positions are mirrored. By 07, both versions have already returned to the dominant down-leg arrangement.

I infer candidate support/recovery roles from relative sole/knee heights and continuous hip→thigh→cuff shapes. The images do not prove a planted support foot or permit confident anatomical left/right labeling through every overlap.

| Pair, both facings | Finding |
|---|---|
| 00→01 | Same extended/down leg dominates; small body/thigh changes create a somewhat held beginning. |
| 01→02 | Down leg gathers under the body; tucked opposite boot remains traceable. |
| 02→03 | Sharp compression/overlap; cream thigh becomes rounder and boot separation weakens. |
| 03→04 | The low boot re-extends on the same projected side, without a sustained opposite stance. |
| 04→05 | A keeps the legs crowded. B separates connected thighs/cuffs and starts the exchange toward 06, although the lateral movement remains noticeable. |
| 05→06 | A has the worse raised-knee/low-boot pop. B already predicts those roles, but knee size and sole height still change. |
| 06→07 | Strongest remaining reset: the brief opposite-leg configuration snaps back to the dominant extended leg with too little intermediate swing travel. |
| 07→00 | Leg silhouette and soles are comparatively close; small arm/body changes can flick, but the wrap is not the principal break. |

All eight pairs were inspected separately for A and B in each facing, including the cyclic wrap. B improves the changed region without changing the remaining six transitions.

## Appearance, identity, and whole-loop usefulness

Both versions preserve the appearance context very well: orange-brown spiky hair, blue eyes, navy and gold tunic, silver armor, cream trousers, and warm brown leather. The head/chest stay recognizable across the loop and align with the south/east/west idle and walk context. Armor and hair separate well on all backgrounds. Dark brown boot overlap is least clear on dark/ground; cream fabric keeps the lower body legible. Directions remain readable at the proxy.

The main residual defects are lower-body timing and volume. Most of the cycle favors one low/extended-leg arrangement, while the opposing arrangement is brief. The cream thigh/knee shapes inflate at compressed poses, especially 03 and 06. The soles are higher and knees spread in 06, permitting a small hop/skip reading in the still chronology. Relatively restrained arm cues do not strongly rescue the leg-role ambiguity. These observations are not contact or airborne-state certification.

B is useful for a prototype or less scrutinized small NPC. A featured player walk would still expose the recurring reset and asymmetric step. The local improvement justifies a modest whole-loop increase, not a large quality jump.

## Smallest justified next repair

Retain B05 and redraw only the lower body of 07 in both facings as a genuine intermediate between 06 and 00. Carry 06's candidate support boot along a shorter coherent projected path while the opposite swing boot advances toward 00, maintaining connected hip, thigh, cuff, and boot volumes. Keep the upper body, materials, stage, pivot, and holds. Judge the resulting 06→07→00 path; one cel may soften the reset without fully balancing the gait. If roles still cannot be traced, revise phase blocking before more surface polish.

## Coverage and limits

I read only INPUTS.json and its nominated PNGs, plus files I created in this fresh review directory. No parent mapping/history, project documents, skills, other grades, or canonical art were read. No source/canonical edits were made.

All 63 nominated PNG SHA-256 values matched before and after the review, with no changes. INPUTS.json also remained unchanged. Viewed coverage comprises all 32 variant cels, all 31 identity-context images, all 32 cyclic adjacent pairs, nine full-loop sheets spanning native128/nearest2x/proxy84 and dark/light/ground, four pair sheets, two context sheets, and three lower-body closeup sheets. Every generated diagnostic PNG was viewed.

The stage is 128×128 with pivot (64,112). Each of eight cels has a specified 9/160-second hold (56.25 ms), totaling 0.45 seconds. The 84/128 nearest proxy is 0.65625 scale, a close approximation to the specified 0.66 game scale.

This is an **AI still-chronology assessment**, not continuous human playback. I did not certify perceptual cadence at 0.45 seconds, engine sampling/alignment, world translation, shadows, foot plants, contact timing, sliding, root motion, or in-engine usefulness. Synthetic ground establishes contrast only. These limits apply especially to the motion scores and support/recovery inferences.

The report and JSON were written once after the final input-hash verification. Scores are frozen. OUTPUTS.sha256 hashes every output except itself; this self-exclusion is explicit. Do not reread or rerate unchanged art after this freeze.
'''
(OUT/'REPORT.md').write_text(report)
(OUT/'ASSESSMENT.json').write_text(json.dumps(assessment,indent=2,ensure_ascii=False)+'\n')
(OUT/'FREEZE.json').write_text(json.dumps({'status':'frozen','frozen_at_utc':stamp,'input_png_count':63,'all_input_hashes_match_before_and_after':True,'inputs_json_unchanged':True,'scores_frozen_once':True,'report':'REPORT.md','structured_report':'ASSESSMENT.json','output_hash_manifest':'OUTPUTS.sha256','hash_manifest_excludes_itself':True,'no_reread_or_rerating_after_freeze':True},indent=2)+'\n')
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='OUTPUTS.sha256')
manifest=''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files)
with (OUT/'OUTPUTS.sha256').open('x') as f:f.write(manifest)
print(json.dumps({'status':'frozen','frozen_at_utc':stamp,'input_pngs_verified_before_and_after':63,'diagnostic_pngs':len(list(OUT.glob('*.png'))),'hashed_outputs':len(files),'report':str(OUT/'REPORT.md'),'scores':scores},indent=2))

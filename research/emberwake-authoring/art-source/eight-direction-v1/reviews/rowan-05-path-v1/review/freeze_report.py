from pathlib import Path
import hashlib,json,datetime
ROOT=Path('/home/astra/artifacts/emberwake-rowan-05-path-review-v1');INP=ROOT/'input';OUT=ROOT/'review';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
before=json.loads((OUT/'input-hashes-before.json').read_text());m=json.loads((INP/'INPUTS.json').read_text());es=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context'];rs=[]
for e in es:
 h=hashlib.sha256((INP/e['path']).read_bytes()).hexdigest();assert h==e['sha256'];assert h==next(x['sha256'] for x in before['images'] if x['path']==e['path']);rs.append({'path':e['path'],'sha256':h})
assert len(rs)==63;mh=hashlib.sha256((INP/'INPUTS.json').read_bytes()).hexdigest();assert mh==before['manifest_sha256']
with (OUT/'input-hashes-after.json').open('x') as f:json.dump({'utc':now,'count':63,'all_match':True,'all_unchanged':True,'manifest_sha256':mh,'images':rs},f,indent=2);f.write('\n')
A={'appearance':8.0,'identity':9.0,'motion_readability':6.5,'game_usefulness':7.0};B={'appearance':8.0,'identity':9.0,'motion_readability':7.0,'game_usefulness':7.0}
common={
'00->01':'Unchanged coherent small extension/tuck; P stays lower/forward and Q bent behind.',
'01->02':'Unchanged P retracts/turns more vertical while Q stays tucked. Pants/cuff/boot remain attached.',
'02->03':'Unchanged feet approach beneath the hips into plausible pass/double-support. Unequal or similar sole Y is not itself a defect.',
'03->04':'Unchanged Q takes the lower/forward role while P lifts behind. Boot volume and distinct cream-thigh provenance hold.',
'06->07':'Unchanged angular exchange: P returns forward and Q recedes. Retained boot volume, but a substantial one-hold pose change remains.',
'07->00':'Unchanged P-forward/Q-rear closure with modest toe/cuff pitch change and no apparent cyclic identity inversion.'}
local={'A':{'04->05':'Carried prior concern: Q shifts toward the center relative to its04 and06 track; knee/cuff projection becomes cramped.','05->06':'Carried prior concern: Q corrects outward again, leaving a small projected jog. Boot volume itself is useful.'},'B':{'04->05':'Improved: Q cream thigh, cuff and boot sit closer to a continuous projected path from04, while the old heel/toe volume remains recognizable.','05->06':'Improved: smaller sideways correction into06; knee/cuff/boot attachment remains coherent. Existing boot-pitch/angular pose changes are not eliminated.'}}
pairs={v:{d:{f'{i:02}->{(i+1)%8:02}':common.get(f'{i:02}->{(i+1)%8:02}',local[v].get(f'{i:02}->{(i+1)%8:02}')) for i in range(8)} for d in ['southeast','southwest']} for v in ['A','B']}
report={
'actor':'rowan','review':'Changed05 foreleg-path follow-up, one frozen scoped judgment','frozen_utc':now,
'anchor':{'A_equals_own_prior_upper_trial_A':True,'verified_hash_matches':16,'source':'My earlier Rowan upper-trial A SHA256 values from manifest output already in this conversation. Baseline scores carried as instructed; no prior files/reports reopened and no other critic scores used.','A_scores_carried_without_rerating':A,'only05_changes_each_view':True,'other14_view_cels_equal':True,'evidence':'anchor-and-change-scope.json'},
'sources':'Only this packet\'s63 nominated PNGs, INPUTS.json and clock; prior own A hashes/scores already present in conversation. No producer docs/maps/history/source, project source, other reports or skills.',
'coverage':{'walk_cels':32,'cyclic_pairs':32,'all8_pairs_per_sequence':True,'includes07to00':True,'contexts_identity_only':31,'scales':['native128','nearest2x256','nearest84 proxy at0.66','extra bilinear84 ground row'],'grounds':['light','dark','diagnostic green grid'],'diagnostic_sheets':25,'local_checks':'04/05/06 path details at3x;05 joint/remnant light/dark/alpha at6x in both views.'},
'hashes':{'before63_match':True,'after63_match':True,'all63_unchanged':True,'INPUTS_json_unchanged':True},
'limits':['Static cels, chronological and cyclic-pair sheets only; no observed normal-speed continuous human playback is claimed.','Manifest timing9/160s=56.25ms per cel,0.45s per loop. No engine, world translation, root speed or physical foot-lock/contact test occurred.','Diagnostic grounds are contrast backgrounds, not certified contact planes. Depth overlap, unequal sole Y and compact stylized motion are accepted.','Local improvement confidence is moderate; actual-speed smoothness, perceived planted weight and world contacts remain unverified.','Context establishes identity/facing only, not a required diagonal gait.'],
'scores':{'A':A,'B':B},'score_delta_B_minus_A':{'appearance':0.0,'identity':0.0,'motion_readability':0.5,'game_usefulness':0.0},
'direction_scores':{'A':{d:A for d in ['southeast','southwest']},'B':{d:B for d in ['southeast','southwest']}},
'preference':{'variant':'B','strength':'slight, local path improvement','confidence':'moderate from static chronology','reason':'Changed05 places Q knee/cuff/heel-toe closer to its04-06 projected track, reducing the sideways correction while retaining the old drawing volume and attachment. No obvious old-foreleg remnant or new join/silhouette failure was found.','baseline_not_rerated':True,'why_game_score_stays7':'The change is modest at84 and does not alter the broader restrained weight response or remaining angular pose/pitch transitions; it improves a local path without establishing a different overall utility level.','no_points_for_separation_pixel_count_exactness':True},
'foot_key':{'P':'Forward/lower leg at00:screen-right in SE,screen-left in SW, followed through pants/cuff and cyclic role. It is raised behind in04-06.','Q':'Other leg bent behind at00-02 and lower/forward in04-06; the changed foreleg path.','occlusion':'Leg identity is traced through cream thigh/cuff/boot, not renamed by screen side. Normal overlap is accepted.'},
'local_findings':{'path':'B05 shifts Q toward a steadier04-06 knee/cuff/boot progression, reducing the inward-then-outward jog. Both entry and exit improve modestly.','volume':'Old recognizable cream-trouser, boot-shaft, flared cuff, heel and rounded toe volumes remain. The repair does not improve merely by shrinking the foot or carving a wide gap.','attachment':'Cream knee enters cuff/shaft coherently; boot and toe remain joined. P rear leg and its hem/glove overlap remain unchanged and readable.','old_foreleg_remnant':'No obvious duplicate toe, stray old calf/cream strip or ghost foreleg edge was visible in light/dark/alpha detail. This is a visual result, not proof from producer masks/maps.','silhouette_cost':'No clear material new silhouette cost found. Outer cuff/heel folds remain angular, but consistent with the retained boot drawing; no separate remnant is inferred from them.','game_size':'Placement improvement remains visible but small at84; identity, direction and overall class of utility stay the same.'},
'cyclic_pair_observations':pairs,
'remaining_limits':[
 {'id':'R_WEIGHT','finding':'Upper-body hip/shoulder weight response remains restrained;05 lower-body projection does not change that.','status':'unchanged'},
 {'id':'R_PITCH','finding':'Knee/cuff and boot pitch still change fairly angularly through the cycle, including06->07. The edit improves lateral path rather than redrawing all joint phasing.','status':'unchanged drawing characteristic/polish limit, not certified physical-contact fault'}
],
'minimum_next_action':'No additional05 art cleanup is compelled by this static comparison. Preserve the improved projection and existing boot volume. Actual observed timed playback and, separately, world translation would be needed before stronger contact/weight claims; no further art trial or rerating is performed here.',
'pixel_scope':'Only05 differs: SE bbox(45,85,69,113), SW(60,85,84,113). Other7 cels per view are identical. Technical scope does not itself earn artistic credit.',
'freeze_policy':'One final frozen comparison; no further trials or rerating.'}
md=f'''# Rowan changed-05 path follow-up

Frozen once at {now}. **Prefer B slightly.** The forward knee/cuff/boot sits on a steadier 04–06 projected path, retaining the old heel/toe volume and coherent attachment. The change is useful but small at game size.

| /10 | A: carried frozen baseline | B: changed 05 |
|---|---:|---:|
| Appearance | 8.0 | 8.0 |
| Identity | 9.0 | 9.0 |
| Motion readability | 6.5 | 7.0 |
| Game usefulness | 7.0 | 7.0 |

A was **not rerated**. All 16 A hashes match my earlier Rowan upper-trial A values from the manifest output already in this conversation. Only 05 changes in each view; the other 14 view/cels are identical. No other critic's scores were used. The local path gain warrants a modest motion increment; appearance/identity and overall game utility remain anchored. No points come from pixel count, exactness or separation alone.

## Scope and proof

Only the new packet's 63 PNGs/INPUTS.json and clock were read; own prior hashes/scores were already in the conversation. No previous files/reports, producer docs/maps/history/source, project source or skills were read. All 63 input hashes match before/after; inputs and INPUTS.json are unchanged. See anchor/change-scope and before/after proof JSONs.

All 32 cels and 32 cyclic pairs including 07→00 were inspected, SE/SW at native 128, nearest 2× and nearest 84 proxy of 0.66 scale on light/dark/diagnostic green grounds. Extra bilinear 84, 04/05/06 path detail and 05 light/dark/alpha checks are included in 25 bounded diagnostic PNGs. Context establishes identity/facing only.

**Static-cel/chronology perception only; no observed normal-speed continuous human playback.** Manifest timing: 9/160 s per cel (56.25 ms), 0.45 s per loop. No engine, world translation, root speed or foot-lock/contact test occurred. Contrast grounds are not contact planes. Normal overlap, unequal sole Y and compact motion are accepted. Confidence is moderate for the local drawing comparison; actual-speed smoothness, perceived weight and world contacts remain unverified.

## Local path, volume and remnants

P is forward/lower at 00 (screen-right in SE, screen-left in SW), followed by cream thigh/cuff and cyclic role. It is lifted behind in 04–06. Q starts bent back and becomes lower/forward in 04–06. Screen side alone does not relabel a leg.

A05 moves Q toward the middle before correcting outward at 06. B05 places the cream knee, cuff, boot shaft and heel/toe closer to the continuing 04–06 track. The sideways correction is reduced. Both entry and exit improve modestly; the edit does not redraw the whole cycle's pitch/weight response.

The retained cream-trouser mass, flared cuff, boot shaft, heel and rounded toe remain recognizable. Knee enters cuff/shaft coherently; boot and toe stay joined. P's rear leg and hem/glove overlap remain readable. There is **no obvious duplicate toe, stray old cream/calf strip, ghost foreleg edge or new material join/silhouette failure** in the light/dark/alpha details. This is a visual finding, not a claim based on unavailable producer masks. Angular outer cuff/heel folds remain consistent with the retained boot drawing, rather than clearly reading as leftovers.

At 84 pixels the placement benefit is visible but small. Overall usefulness stays 7 because restrained upper-body weight and remaining angular pose/pitch changes are unchanged; a local path repair does not establish stronger runtime contact or a different utility class.

## Every cyclic pair, both views

| Pair | Finding |
|---|---|
| 00→01 | Unchanged coherent extension/tuck; P forward, Q behind. |
| 01→02 | Unchanged P retraction/more vertical pitch; attachments hold. |
| 02→03 | Unchanged boots approach beneath hips in a plausible pass/double-support pose. |
| 03→04 | Unchanged readable Q-forward/P-raised exchange. |
| 04→05 | B keeps Q closer to the continuing knee/cuff/heel-toe track; A moves inward more. |
| 05→06 | B reduces the sideways correction into 06, retaining boot volume and attachment. |
| 06→07 | Unchanged angular return of P forward/Q rear; substantial one-hold pose change remains. |
| 07→00 | Unchanged coherent P-forward/Q-rear closure with modest pitch change. |

## Remaining limits and minimum action

The modest hip/shoulder weight response remains. Knee/cuff and boot-pitch changes through the cycle remain angular, including 06→07; these are polish limits, not demonstrated world-contact failure.

No additional 05 art cleanup is compelled by this static comparison. Preserve its better projection and existing boot volume. Actual observed timed playback and, separately, world translation would be required before stronger weight/contact claims. This is the final frozen comparison; no further art trials or rerating are performed.
'''
for name,content in [('report.md',md),('report.json',json.dumps(report,indent=2)+'\n')]:
 with (OUT/name).open('x') as f:f.write(content)
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (OUT/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for name in ['report.md','report.json','SHA256SUMS']:(OUT/name).chmod(0o444)
print('All63 inputs unchanged. Frozen once; ledger entries:',len(files))
for name in ['report.md','report.json','SHA256SUMS']:print(name,hashlib.sha256((OUT/name).read_bytes()).hexdigest())

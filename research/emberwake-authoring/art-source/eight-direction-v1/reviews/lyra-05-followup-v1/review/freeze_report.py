from pathlib import Path
import hashlib,json,datetime
ROOT=Path('/home/astra/artifacts/emberwake-lyra-05-followup-review-v1');INP=ROOT/'input';OUT=ROOT/'review';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
before=json.loads((OUT/'input-hashes-before.json').read_text());m=json.loads((INP/'INPUTS.json').read_text());es=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context'];rs=[]
for e in es:
 h=hashlib.sha256((INP/e['path']).read_bytes()).hexdigest();assert h==e['sha256'];assert h==next(x['sha256'] for x in before['images'] if x['path']==e['path']);rs.append({'path':e['path'],'sha256':h})
assert len(rs)==63;mh=hashlib.sha256((INP/'INPUTS.json').read_bytes()).hexdigest();assert mh==before['manifest_sha256']
with (OUT/'input-hashes-after.json').open('x') as f:json.dump({'utc':now,'count':63,'all_match':True,'all_unchanged':True,'manifest_sha256':mh,'images':rs},f,indent=2);f.write('\n')
A={'appearance':8.0,'identity':9.0,'motion_readability':6.5,'game_usefulness':7.0};B={'appearance':8.0,'identity':9.0,'motion_readability':7.0,'game_usefulness':7.5}
common={
'00->01':'Unchanged small coherent extension/tuck. P remains the lower/forward boot and Q bent behind.',
'01->02':'Unchanged P retraction/more vertical pitch while Q stays tucked. Attachments hold.',
'02->03':'Unchanged abrupt tucked-to-nearly-parallel lowered-leg recovery and standing-pose cue. Double support itself is legitimate. Short dark03 spur remains.',
'03->04':'Unchanged readable Q-forward/lower, P-lifted exchange, with distinct pants/cuff provenance.',
'06->07':'Unchanged angular return: P comes forward while Q recedes. Boot volume retained; less concerning than the former05 crossing.',
'07->00':'Unchanged coherent static closure: P forward/Q rear, modest boot/cuff pitch change and no apparent identity inversion.'}
local={'A':{'04->05':'Prior defect carried: Q boot moves inward into a tight crossed column, cuff/leg provenance becomes harder to follow at84.','05->06':'Prior defect carried: feet reopen and Q moves outward again; the inward/outward projected jog remains.'},'B':{'04->05':'Improved: Q knee, cuff and boot stay on a steadier projected track; P continues folded behind. Separation clarifies an anatomically connected path rather than being a gap for its own sake.','05->06':'Improved: Q boot/cuff continues toward the06 support pose without the old sideways reversal; P\'s bent rear boot remains attached and consistent. Boot/toe volume is retained.'}}
pairs={v:{d:{f'{i:02}->{(i+1)%8:02}':common.get(f'{i:02}->{(i+1)%8:02}',local[v].get(f'{i:02}->{(i+1)%8:02}')) for i in range(8)} for d in ['southeast','southwest']} for v in ['A','B']}
report={
'actor':'lyra','review':'Changed05 follow-up, not cold; one frozen scoped judgment','frozen_utc':now,
'anchor':{'A_equals_prior_Lyra_B':True,'verified_hash_matches':16,'source':'Previous Lyra B hash values from the earlier manifest tool output already in this conversation. No previous files/reports reopened. Baseline scores carried as instructed.','A_scores_carried_without_rerating':A,'only05_changes_in_each_view':True,'other14_view_cels_equal':True,'proof':'anchor-and-change-scope.json'},
'sources':'Only this packet\'s63 nominated PNGs, INPUTS.json and clock, plus the prior B hashes/scores already available in the conversation. No producer docs/history/source, other reports, project source or skills.',
'coverage':{'walk_cels':32,'cyclic_pairs':32,'all8_pairs_per_sequence':True,'includes07to00':True,'contexts_identity_only':31,'scales':['native128','nearest2x256','nearest84 proxy at0.66','extra bilinear84 ground row'],'grounds':['light','dark','diagnostic green grid'],'diagnostic_sheets':25,'local_detail':'04/05/06 nearest3x and05 light/dark/alpha nearest6x in both views.'},
'hashes':{'before63_match':True,'after63_match':True,'all63_unchanged':True,'INPUTS_json_unchanged':True},
'limits':['Static cels and chronological/cyclic pairs only. No observed normal-speed continuous human playback is claimed.','Manifest timing9/160s=56.25ms per cel,0.45s per loop. No engine, world translation, root velocity or foot-lock/contact testing occurred.','Grounds are diagnostic contrast backgrounds, not certified contact planes. Depth overlap and differing sole Y are legitimate.','Moderate confidence in local drawing/path improvement; actual-speed smoothness, world contacts and perceived foot sliding remain unverified.','Context supports identity/facing only, not a required diagonal gait.'],
'scores':{'A':A,'B':B},'score_delta_B_minus_A':{'appearance':0.0,'identity':0.0,'motion_readability':0.5,'game_usefulness':0.5},
'direction_scores':{'A':{d:A for d in ['southeast','southwest']},'B':{d:B for d in ['southeast','southwest']}},
'preference':{'variant':'B','strength':'clear local improvement, modest overall increment','confidence':'moderate from static chronology','reason':'Q follows a steadier knee/cuff/boot track through04-06 while P stays bent and attached behind. The old inward/outward jog and crossed-column reading are substantially reduced at84 without an obvious boot-volume or join penalty.','baseline_not_rerated':True,'no_separation_only_credit':True,'no_pixel_count_or_exactness_credit':True,'use_level':'Better small game walk; still has unchanged03 polish issues and unverified actual-speed/world-contact behavior.'},
'foot_key':{'P':'Forward/lower boot at00:screen-right in SE,screen-left in SW. Traced through pants/cuff and cycle rather than current screen side. P is tucked behind in04-06.','Q':'Other boot, bent back at00-02, lower/forward in04-06. Its projected path is the main comparison.','occlusion':'Normal overlap and sole-height differences are accepted; separation alone does not prove better gait.'},
'local_findings':{'path':'B05 places Q beneath the continuing thigh/cuff track between04 and06 rather than crossing inward and returning outward. Both entry and exit improve.','attachment':'P rear knee/cuff/boot remains connected; Q shin/cuff joins into the boot. No clear new detached segment, limb-layer reversal or background slit through a load-bearing join was found in the light/dark/alpha checks.','volume':'Q retains a recognizable calf, cuff, heel and rounded toe; P retains its smaller tucked boot. No material boot/pants volume loss or new foot-pitch snap was evident.','silhouette':'More open two-leg silhouette also survives84. The gain is not mere separation: it accompanies the steadier track and preserved joints. The04-06 movement remains compact, which suits this style.','cost':'No clear material new drawing/silhouette cost found. Whole-character appearance/identity scores stay anchored because this is a local lower-body repair.'},
'cyclic_pair_observations':pairs,
'remaining_defects_carried':[
 {'id':'C03_SPUR','severity':'low','finding':'Unchanged03 short dark horizontal spur beside the rear glove/hip remains; SE x44-50,y86, corresponding SW edge. Visible on enlarged light ground.'},
 {'id':'C02_03','severity':'low to medium','finding':'Unchanged02->03 tucked-to-nearly-parallel lowered boots remains abrupt in static chronology and gives a standing-pose cue. Double support is not inherently invalid.'},
 {'id':'C_WEIGHT','severity':'low','finding':'Upper-body hip/shoulder weight response remains modest, with dark scarf/rear-boot contrast loss on dark ground. Bright hair and face preserve identity.'}
],
'minimum_next_action':{'art':'Clean only the unchanged03 dark spur first. Do not keep widening the05 leg gap: the new projected path and joined volume are already better.','verification':'Observe an actual normal-speed comparison at supplied timing and, separately, world translation before claiming smooth planted contacts or deciding whether02->03 needs further drawing changes.'},
'pixel_scope':'Only05 differs, within SE bbox(44,79,82,114) and SW(47,79,85,114). Seven other cels per view are identical. This verifies scope, not quality.',
'freeze_policy':'One frozen scoped judgment; unchanged A not rerated, no target chasing.'}
md=f'''# Lyra changed-05 follow-up

Frozen once at {now}. **Prefer B.** The new 05 improves the actual knee→cuff→boot path through 04–06, not just the space between legs. It substantially reduces the old inward/outward jog and crossed-column reading without an obvious volume or join penalty.

| /10 | A: carried frozen baseline | B: changed 05 |
|---|---:|---:|
| Appearance | 8.0 | 8.0 |
| Identity | 9.0 | 9.0 |
| Motion readability | 6.5 | 7.0 |
| Game usefulness | 7.0 | 7.5 |

A was **not rerated**. All 16 A hashes match the previous Lyra B hashes from the earlier manifest output in this conversation. Only 05 differs in each view; the other 14 view/cels are identical. Score gains are a modest scoped judgment of a better path and game-size leg reading, not credit for separation, pixel count or technical exactness.

## Proof and qualification

Only the new packet's 63 PNGs/INPUTS.json and clock were read; prior hashes/scores were already available in the conversation. No earlier files/reports, producer docs/history/source, project source or skills were read. All 63 input hashes match before/after; inputs and INPUTS.json remain unchanged. See `anchor-and-change-scope.json` and before/after ledgers.

Coverage: all 32 cels and 32 cyclic pairs including 07→00, SE/SW at native 128, nearest 2× and nearest 84 proxy of 0.66 scale, on light/dark/diagnostic green grounds. Extra bilinear 84, 04/05/06 details and 05 alpha checks are included in 25 bounded diagnostic PNGs. Context was used only for identity/facing.

**Static-cel/chronology perception only; no observed normal-speed continuous human playback.** Manifest timing is 9/160 s per cel (56.25 ms), 0.45 s per loop. No engine, world translation, root speed or foot-lock/contact test occurred. Grounds are diagnostic backgrounds. Normal depth overlap and unequal sole Y are accepted. Local improvement confidence is moderate; actual-speed smoothness and world contacts remain unverified.

## Path, joints, volume and silhouette

P means the forward/lower boot at 00: screen-right in SE, screen-left in SW, followed by thigh/cuff and cyclic role. It is folded behind in 04–06. Q starts behind and is the lower/forward boot in 04–06. Screen position alone does not relabel either foot.

In A05, Q moves inward beneath the tunic, crossing into the other leg before opening outward at 06. B05 keeps Q beneath its continuing thigh/cuff track between 04 and 06. P remains bent behind with a connected knee/cuff/boot. Both entry and exit now read more continuously. This better track, combined with preserved joints, makes the separation useful rather than cosmetic.

Q retains a calf, cuff, heel and rounded toe; P retains the smaller tucked boot. I found no clear new detached segment, limb-layer reversal, material boot/pants volume loss or background slit through a joint in light/dark/alpha inspection. The two-leg silhouette survives 84 pixels. Movement across 04–06 is compact, which suits this style; a larger leg gap is not a further improvement by itself.

## All eight cyclic pairs, both views

| Pair | Finding |
|---|---|
| 00→01 | Unchanged coherent small extension/tuck; P forward, Q behind. |
| 01→02 | Unchanged P retraction/more vertical pitch; attachments hold. |
| 02→03 | **Unchanged concern:** abrupt tucked-to-nearly-parallel lowered legs and standing-pose cue; double support itself is legitimate. |
| 03→04 | Unchanged readable Q-forward/P-lifted exchange. |
| 04→05 | B preserves Q's thigh/cuff/boot track and P's bent rear attachment; A crosses inward. |
| 05→06 | B continues into 06 without the old outward correction; A reopens from the crossed column. |
| 06→07 | Unchanged angular but readable return with retained boot volume. |
| 07→00 | Unchanged coherent static closure; no apparent identity inversion. |

**The 03 spur remains unchanged:** short dark horizontal mark beside the rear glove/hip, SE x44–50,y86 and corresponding SW edge, clearest enlarged on light ground. Modest upper-body weight response and dark scarf/rear-boot contrast loss also remain. Face, hair and kit preserve the anchored identity; the local edit does not justify new appearance/identity ratings.

## Smallest next action

Clean the unchanged 03 spur. Preserve the new 05 path, attachment and boot volume; do not keep widening the gap. An actual observed normal-speed comparison, and separately world translation, should precede stronger contact claims or a decision that the unchanged 02→03 recovery needs more drawing work.

This is one frozen scoped judgment. The unchanged baseline stays fixed.
'''
for name,content in [('report.md',md),('report.json',json.dumps(report,indent=2)+'\n')]:
 with (OUT/name).open('x') as f:f.write(content)
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (OUT/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for name in ['report.md','report.json','SHA256SUMS']:(OUT/name).chmod(0o444)
print('All63 inputs unchanged. Frozen once. Ledger entries:',len(files))
for name in ['report.md','report.json','SHA256SUMS']:print(name,hashlib.sha256((OUT/name).read_bytes()).hexdigest())

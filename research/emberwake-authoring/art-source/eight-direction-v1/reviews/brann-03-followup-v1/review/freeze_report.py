from pathlib import Path
import json,hashlib,datetime
OUT=Path('/home/astra/artifacts/emberwake-brann-03-followup-review-v1/review');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
A={'appearance':7.5,'identity':8.5,'motion_readability':6.5,'game_usefulness':7.0};B={'appearance':7.5,'identity':8.5,'motion_readability':7.0,'game_usefulness':7.0}
common={
'00->01':'Unchanged: consistent small tuck/lift; P remains forward and Q bends behind.',
'01->02':'Unchanged: P retracts/narrows and Q stays tucked. Compact foreshortening and pitch change remain visible.',
'04->05':'Unchanged: Q retracts under the body and P remains visible behind; some brown boot masses merge.',
'05->06':'Unchanged: Q preserves broad lower-boot volume into the exit pose.',
'06->07':'Unchanged prior weakness: P expands from tucked/hidden into a long outward shin and strongly pitched boot in one hold. Kick/pop risk remains in static chronology; not certified playback/contact failure.',
'07->00':'Unchanged: P remains forward, Q rear. P rolls/flattens. Closure is less concerning than06->07; no requirement for identical endpoint drawings.'}
local={'A':{'02->03':'Carried prior concern: Q changes from a small tucked boot into a substantial pitched/sole-presenting boot abruptly; cuff and heel/toe plane do not bridge convincingly.','03->04':'Q advances into a broad lower/front form while P recedes. Support exchange is readable, but03 retains the excessive sole turn.'},'B':{'02->03':'Improved: Q comes through under its cuff with a rounder toe/upper and less sole-facing turn. Boot/calf volume reads coherent. Tucked-to-larger Q change is still fast, so the earlier defect is reduced, not erased.','03->04':'Improved continuity of cuff/upper/heel-toe form into the broad04 support boot. Two feet overlap legitimately; no new gross knee/cuff/boot detachment. Tiny partial-alpha seam remains inside the overlapping boot area.'}}
pairs={v:{d:{f'{i:02}->{(i+1)%8:02}':common.get(f'{i:02}->{(i+1)%8:02}',local[v].get(f'{i:02}->{(i+1)%8:02}')) for i in range(8)} for d in ['southeast','southwest']} for v in ['A','B']}
report={
'actor':'brann','review':'Changed-art follow-up, explicitly not cold','frozen_utc':now,
'anchor':{'A_equals_prior_packet_B':True,'verified_hash_matches':16,'hash_provenance':'First packet B SHA256 values from its earlier manifest tool output in this conversation. No earlier input files were reopened. Prior report.json was consulted only for the frozen scores and defects.','prior_report':'/home/astra/artifacts/emberwake-brann-three-pose-review-v1/review/report.json','A_scores_carried_without_rerating':A,'B_only03_changed_each_view':True,'other14_view_cels_equal':True,'evidence':'anchor-and-change-scope.json'},
'sources':'New nominated63 PNGs, INPUTS.json, clock, and own prior frozen report for anchor only. No producer docs/history/source, project source, skills or other-agent reviews.',
'coverage':{'walk_cels':32,'cyclic_pairs':32,'all_eight_pairs_per_sequence':True,'includes07to00':True,'contexts_identity_only':31,'scales':['native128','nearest2x256','nearest84 proxy at0.66','additional bilinear84 ground row'],'grounds':['light','dark','diagnostic green grid'],'diagnostic_sheets':25,'local_checks':'02/03/04 lower attachments at3x;03 light/dark and alpha at6x.'},
'hash_verification':{'before63_match':True,'after63_match':True,'all63_unchanged':True,'INPUTS_json_unchanged':True},
'limits':['Static cels/chronological and cyclic-pair sheets only. No observed normal-speed continuous human playback is claimed.','Manifest hold9/160s=56.25ms, loop0.45s. No engine, world translation, root velocity or physical foot-lock/contact testing occurred.','Diagnostic ground is a contrast background. Depth overlap and differing sole Y are accepted; neither is proof of failed contact.','Moderate confidence for the local drawing/chronology comparison; actual-speed smoothness and world contacts remain unverified.'],
'scale':'Absolute0-10, anchored to prior frozen baseline. No artistic credit for changed-pixel count, frame count, hashes or timing exactness.',
'scores':{'A':A,'B':B},'score_delta_B_minus_A':{'appearance':0.0,'identity':0.0,'motion_readability':0.5,'game_usefulness':0.0},
'direction_scores':{'A':{d:A for d in ['southeast','southwest']},'B':{d:B for d in ['southeast','southwest']}},
'preference':{'variant':'B','strength':'modest, scoped to02->03->04','confidence':'moderate from static chronology','reason':'Rounder Q boot/upper and less sudden sole-facing turn bridge cuff attachment and04 support more naturally. Tiny partial-alpha seam needs cleanup, and the unchanged06->07 defect prevents claiming the whole walk is repaired.','baseline_not_rerated':True,'why_game_score_unchanged':'Small game-usefulness category remains limited by the identical06->07 transition, weak weight response and dark-ground lower-body contrast; a local improvement does not establish a new overall utility level.'},
'persistent_foot_key':{'P':'Forward/lower leg at00:screen-right in SE,screen-left in SW, followed through cuff/return sequence rather than relabeling by screen side.','Q':'Other leg tucked at00-02, recovering through03 and lower/forward at04-06.','occlusion':'Two feet may overlap and differ in sole height. No anatomical side swap or full detachment is inferred.'},
'local_findings':{'attachment':'B03 Q calf/cuff/upper reads as a more coherent compact leg-to-boot form; pant and boot volume are retained rather than narrowed into a tube.','sole_turn':'The hard, pitched sole-presenting/block-like Q toe at A03 is moderated into a rounded toe/upper in B03. Transition to04 improves, though02 still changes quickly into the larger03 shape.','background_slits':'No full transparent split or detached boot was found. A tiny internal seam has reduced alpha and admits a little ground color; it is visible on enlarged light-ground/alpha views, much less consequential at84.','identity_and_upper_body':'Unchanged face, armor, hands and body response; context still matches identity/facing. No new whole-body appearance or identity score is warranted.'},
'partial_alpha_seam':{'SE_xy':[[67,96],[68,97],[68,98]],'SW_xy':[[61,96],[60,97],[60,98]],'B_alpha':[198,169,243],'A_alpha':[254,254,253],'severity':'minor contour/compositing cleanup, not a full gap','evidence':'partial-alpha-seam.json'},
'cyclic_pair_observations':pairs,
'unchanged_defects_carried':['06->07 P shin/boot expansion and pitch change remains the main whole-loop weakness;07->00 flattening remains secondary.','Upper-body hip/shoulder weight response remains modest; guarded fists-up posture is legitimate.','Dark hair/pants/rear-boot contrast remains weak on dark ground.'],
'smallest_meaningful_repair':{'local':'Restore near-neighbor opacity/shading across the tiny03 internal seam at the listed coordinates in both facings. Preserve the new rounded upper/toe and cuff form; do not restore the old sole block.','then':'Address the separate, unchanged06->07 P shin/boot pitch transition, checking07->00.','qualification':'The02->03 mass/position change is reduced but still brisk; actual observed playback is needed to assess how much it remains noticeable at the supplied timing.'},
'freeze_policy':'One frozen scoped judgment. No rerating of unchanged A or target chasing.'}
md=f'''# Brann changed-03 follow-up

Frozen once at {now}. **Prefer B modestly for 02→03→04.** The new rounded Q boot/upper connects more naturally beneath the cuff and reduces the abrupt sole-facing turn. It is a partial local repair, not a completed whole-loop fix.

| /10 | A: carried frozen baseline | B: changed 03 |
|---|---:|---:|
| Appearance | 7.5 | 7.5 |
| Identity | 8.5 | 8.5 |
| Motion readability | 6.5 | 7.0 |
| Game usefulness | 7.0 | 7.0 |

A was **not rerated**. All 16 A hashes match the first packet's B values from the earlier manifest tool output. Only 03 differs between A/B in each view; the other 14 view/cels are identical. Appearance/identity and game-usefulness scores do not rise: the edit improves a local transition while the unchanged 06→07 weakness still limits the whole walk. No credit comes from changed-pixel count, exactness or frame count.

## Scope and evidence

This is a follow-up, not a cold review. Sources were only the new packet's 63 PNGs/INPUTS.json, clock, and my prior frozen report for baseline scores/defects. No producer docs/history/source, project source, skills or other-agent reports were read. Earlier input files were not reopened; the anchor hash values came from the first packet's manifest output already in this conversation.

All 63 new input hashes match before and after; inputs and INPUTS.json remain unchanged. I inspected all 32 cels and all 32 cyclic pairs, including 07→00, in SE/SW at native 128, nearest 2× and 84-pixel proxy of 0.66 scale, on light/dark/diagnostic green grounds. Additional bilinear 84, 02/03/04 detail and alpha-mask checks are included in 25 bounded diagnostic PNGs. Context establishes identity/facing only.

**Static-cel/chronology perception only: no observed normal-speed continuous human playback.** Manifest timing is 9/160 s per cel (56.25 ms), 0.45 s per loop. No engine, world translation, root-speed or foot-lock/contact test occurred. Grounds are contrast diagnostics, not certified contact planes. Different sole Y and legitimate overlapping feet are accepted. Local comparison confidence is moderate; actual-speed smoothness and world contacts remain unverified.

## Changed attachment, turn and volume

P is the leg forward/lower at 00 (screen-right in SE, screen-left in SW), followed through its cuff/return sequence. Q is initially tucked behind and comes through 03 to the lower/front role at 04–06. These labels do not change merely because screen position changes.

A03's Q boot presents a strongly pitched, block-like sole/toe beside P. B03 rounds that form into a more convincing boot upper/toe beneath the calf/cuff. The boot and pants retain chunky volume; the leg does not become a skinny tube. Q still grows/moves quickly out of tucked 02, so that earlier concern is reduced rather than erased. Entry into the broad 04 support shape is more coherent. Face, armor, hands and upper response are unchanged.

**Background seam:** no full transparent split or detached boot is visible. B03 contains a tiny internal partial-alpha seam that admits some background color: SE (67,96), (68,97), (68,98); SW (61,96), (60,97), (60,98). B alpha values are 198/169/243 versus A's 254/254/253. It is easiest to see enlarged on light ground/alpha views and has little impact at 84, but should be cleaned. See `partial-alpha-seam.json` and the 03 alpha-gap sheets.

## Every cyclic pair, both facings

| Pair | Finding |
|---|---|
| 00→01 | Unchanged consistent tuck/lift; P forward, Q behind. |
| 01→02 | Unchanged P retraction/narrowing while Q stays tucked. |
| 02→03 | B improves cuff-to-upper continuity and moderates Q's sole turn; the small-tucked to larger-recovery change remains brisk. |
| 03→04 | B improves the shape bridge into Q's broad lower/front boot; overlap is legitimate, with the tiny alpha seam noted above. |
| 04→05 | Unchanged plausible Q retraction/P rear visibility; brown masses partly merge. |
| 05→06 | Unchanged retained broad Q boot volume. |
| 06→07 | **Unchanged main weakness:** P expands from tucked/hidden into a long outward shin and steep boot pitch in one hold; static kick/pop risk remains. |
| 07→00 | Unchanged P-forward/Q-rear closure; P flattens/rolls. Secondary to 06→07, not an identity inversion. |

The modest hip/shoulder weight response and dark-ground lower-body contrast limitations also carry unchanged. This local edit cannot be credited for fixing them.

## Smallest next repair

Restore coherent opacity/shading across the tiny 03 internal seam at the listed source coordinates, preserving the new rounded upper/toe and cuff. Then address the separate unchanged 06→07 P shin/boot-pitch transition, checking 07→00. The remaining brisk 02→03 entry needs actual observed playback at the supplied timing before stronger smoothness/contact claims.

This is one frozen scoped judgment; the unchanged baseline remains fixed.
'''
for name,content in [('report.md',md),('report.json',json.dumps(report,indent=2)+'\n')]:
 with (OUT/name).open('x') as f:f.write(content)
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (OUT/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for name in ['report.md','report.json','SHA256SUMS']:(OUT/name).chmod(0o444)
print('Frozen once. Ledger entries:',len(files))
for name in ['report.md','report.json','SHA256SUMS']:print(name,hashlib.sha256((OUT/name).read_bytes()).hexdigest())

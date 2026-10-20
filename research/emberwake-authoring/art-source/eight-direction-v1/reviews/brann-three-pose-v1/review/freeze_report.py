from pathlib import Path
import json,hashlib,datetime,os
OUT=Path('/home/astra/artifacts/emberwake-brann-three-pose-review-v1/review')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
scores={'A':{'appearance':7.0,'identity':8.5,'motion_readability':4.5,'game_usefulness':5.5},'B':{'appearance':7.5,'identity':8.5,'motion_readability':6.5,'game_usefulness':7.0}}
cel_common={
 '00':'P is the forward/lower, broad toe-profile boot; Q is bent back and higher. Both retain useful chunky proportions.',
 '01':'P remains forward while Q lifts/folds. The exchange has not happened yet; differing sole heights are appropriate depth/lift cues.',
 '02':'P draws beneath the body and narrows in projection. Q is the small, tucked boot behind. Both remain attached; this is the entry anchor for the recovery.',
 '06':'Q is the dominant lower boot beneath the torso; P is tucked behind on the other projected track. Body and hands respond modestly. This is the exit anchor for the changed middle.',
 '07':'P reappears forward/outward with a strongly pitched boot and long projected shin; Q is again folded back. Larger pose change than 07 to 00.'}
cel_middle={
 'A':{
 '03':'P remains a narrow front toe-profile boot; Q is crowded into the inner calf/cuff silhouette. No literal detachment, but calf and boot volume are markedly pinched.',
 '04':'The lower silhouette remains a narrow, crossing pair with the long toe dominant. A clean alternate support silhouette is weak; persistent P/Q attribution becomes uncertain in the overlap.',
 '05':'Feet stack into a nearly single narrow column. The smaller rear foot and its cuff are hard to parse at 84 pixels; Q becoming the clear lower foot at 06 is poorly prepared.'},
 'B':{
 '03':'Q comes through as a substantial, pitched boot adjacent to P. Both boots/cuffs can be parsed, but Q expands and turns abruptly from the small tucked 02 image.',
 '04':'Q is now the broad lower/front boot; P is the smaller rear boot. Different sole Y is legitimate. Overlap is coherent enough to read a support exchange, though the two brown boot masses nearly fuse.',
 '05':'Q remains the lower substantial boot and P remains visible behind. Better volume and continuity into 06 than A; the knee/cuff silhouette is still blocky and weight transfer is not strongly echoed above the belt.'}}
pairs_common={
 '00->01':'Small consistent tuck/lift; no leg identity flip inferred.',
 '01->02':'P retracts and narrows while Q stays tucked. Noticeable volume/pitch change, but within a plausible compact foreshortened pose.',
 '06->07':'Largest shared concern: P returns from the hidden/tucked position to a long outward shin and steeply pitched toe in one hold. Static chronology predicts a kick/pop impression, not proven actual-speed failure.',
 '07->00':'Cyclic identities close: P stays the forward boot and Q the rear boot. P rolls/flattens noticeably, but this is less severe than 06->07. No evidence that the loop requires identical endpoint cels.'}
pairs_mid={
 'A':{
 '02->03':'Q enters the overlap but loses a convincing boot/calf mass; P stays narrow. The pass is readable mainly by ordering, not a clear lifted-foot silhouette.',
 '03->04':'Crossing progresses but the dominant thin toe/ankle remains. Alternate support is weak and foot identity becomes visually uncertain.',
 '04->05':'Both legs compress into one column; separation and cuff provenance are weakest here, especially at 84 pixels.',
 '05->06':'The dominant lower boot regains a broad form suddenly. The support exchange can be inferred but is not well drawn through the preceding narrow pose.'},
 'B':{
 '02->03':'Main B defect: Q changes from small tucked boot to substantial pitched/sole-presenting boot abruptly; calf/cuff and heel/toe angle need a better intermediate drawing.',
 '03->04':'Q advances into the broad lower/front form while P recedes. This is a materially clearer exchange than A; touching/overlapping boots alone are not a defect.',
 '04->05':'Q retracts beneath the body and P stays visible behind. Plausible order and improved mass retention, with some merged brown silhouette.',
 '05->06':'Q keeps its broad lower-boot volume into the common exit pose; this is B\'s clearest continuity gain.'}}
observations={v:{d:{f'{i:02}':cel_common.get(f'{i:02}',cel_middle[v].get(f'{i:02}')) for i in range(8)} for d in ['southeast','southwest']} for v in ['A','B']}
pair_observations={v:{d:{f'{i:02}->{(i+1)%8:02}':pairs_common.get(f'{i:02}->{(i+1)%8:02}',pairs_mid[v].get(f'{i:02}->{(i+1)%8:02}')) for i in range(8)} for d in ['southeast','southwest']} for v in ['A','B']}
defects=[
 {'id':'A1','applies_to':['A/southeast','A/southwest'],'cels':['03','04','05'],'severity':'high for motion','finding':'Pinched calf/ankle and narrow toe forms, then nearly stacked feet, conceal the alternate support exchange. Occlusion prevents confident persistent-foot attribution in the middle; no literal detached boot is claimed.'},
 {'id':'B1','applies_to':['B/southeast','B/southwest'],'pairs':['02->03','03->04'],'severity':'medium','finding':'Q swings out of the tucked 02 shape into a much more substantial, pitched 03 boot with a sudden heel/toe-plane and cuff change. 04 restores a useful support silhouette, but the entry still reads abrupt from static chronology.'},
 {'id':'C1','applies_to':['A/southeast','A/southwest','B/southeast','B/southwest'],'pairs':['06->07','07->00'],'severity':'medium','finding':'P expands from its tucked position at 06 to a long outward shin and steeply pitched toe at 07, then flattens at 00. The internal 06->07 change is more concerning than closure; not a demonstrated world-contact fault.'},
 {'id':'C2','applies_to':['A/southeast','A/southwest','B/southeast','B/southwest'],'severity':'low to medium','finding':'Hands shift and the head bobs slightly, so the body is not frozen, but the hip/shoulder weight response is weak relative to the leg exchange. Guarded fists-up posture is a legitimate style choice.'},
 {'id':'C3','applies_to':['A/southeast','A/southwest','B/southeast','B/southwest'],'severity':'low, background dependent','finding':'Hair outline, dark pants and brown rear boot lose separation on the dark ground. Face, gold armor and general facing remain readable at 84 pixels.'}
]
report={
 'review':'Independent adversarial static-cel review, frozen once', 'frozen_utc':now,
 'allowed_sources':'Only the 63 nominated PNG images, INPUTS.json and clock. No parent mapping, producer docs, other agent reports, project source or skills were consulted.',
 'timing':{'canvas':[128,128],'pivot':[64,112],'game_scale':0.66,'proxy_canvas':[84,84],'cel_hold_seconds':0.05625,'loop_seconds':0.45},
 'coverage':{'walk_cels_inspected':32,'cyclic_pairs_inspected':32,'closure_included':True,'contexts':31,'scales':['128 native','nearest 256 (2x)','nearest 84 proxy','additional bilinear 84 ground check'],'backgrounds':['light','dark','diagnostic green ground grid'],'diagnostic_png_count':22},
 'hash_verification':{'before_images_matching_manifest':63,'after_images_matching_manifest':63,'images_unchanged':63,'INPUTS_json_unchanged':True,'before_file':'input-hashes-before.json','after_file':'input-hashes-after.json'},
 'limitations':['Rendered static cels, chronological strips and explicit cyclic-pair sheets were inspected. No normal-speed continuous human playback session occurred.','No engine, world translation, foot-lock/contact, root velocity, collision or turn interpolation test occurred. A diagnostic ground grid is not a world contact plane.','The 0.45-second loop is manifest timing. Motion scores describe static chronology and inferred readability, with moderate confidence; actual-speed smoothness and world contacts remain unverified.','Cardinal images were used only for identity and turn orientation, never to reward or penalize diagonal gait mechanics.'],
 'scoring_scale':'Absolute 0-10: 0 unusable, 5 mixed/requires repair, 7 useful with visible defects, 10 exceptional finished work. No art points for frame count, matching hashes, exact timing or changed-pixel count.',
 'scores':scores,
 'direction_scores':{v:{d:scores[v] for d in ['southeast','southwest']} for v in ['A','B']},
 'preference':{'variant':'B','strength':'clear but qualified','confidence':'moderate for static chronology; actual normal-speed performance unverified','reason':'03-05 preserve a recognizably chunky calf/boot and reveal Q taking over the lower/front role, improving support exchange and 84-pixel utility. The entry at 02->03 and shared 06->07 transition remain visible concerns.','use_level':'Useful draft small NPC walk; additional transition repair is warranted before treating it as polished hero movement.'},
 'persistent_foot_key':{'P':'The boot attached to the more forward/lower leg at 00: screen-right in southeast, screen-left in southwest. It is traced through the pant/cuff and return sequence, not relabeled by screen side.','Q':'The other boot, bent back/higher at 00. It folds at 01-02, comes through at 03-05, and is the dominant lower boot at 06.','uncertainty':'P/Q identity through A03-05 is partly occluded and visually ambiguous; this is disclosed rather than turned into a claim of anatomical inversion. Depth overlap and differing sole Y are accepted.'},
 'cel_observations':observations,'cyclic_pair_observations':pair_observations,'remaining_defects':defects,
 'smallest_meaningful_repair':{'base':'B','scope':'Redraw cel 03 lower-body attachment in both directions; keep 02 and 04 visible as anchors.','instruction':'Carry Q from its tucked 02 position into the forward/lower 04 position with one coherent knee-to-cuff-to-heel/toe path and stable boot volume. Reduce the sudden sole-plane turn in 03 while keeping P attached and separate by contour/value where overlap permits. Preserve B04-05 chunky support silhouette.','secondary_followup':'Then adjust the common 06->07 P shin/boot pitch transition; keep 07->00 in the check. This is a separate follow-up, not the minimum first repair.','no_retiming_or_new_frames_required_for_first_repair':True},
 'technical_scope_note':'A and B differ only below y86 in cels 03-05; other cels are byte-identical. This limits what an A/B preference can establish, and gives no artistic credit. See pixel-scope.json.'
}
md=f'''# Independent Brann three-quarter walk review

Frozen once at {now}. **Prefer B**, with moderate confidence from static chronology. B is a more useful small NPC walk; it still needs transition polish before being treated as finished hero movement.

| Variant | Appearance /10 | Identity /10 | Motion readability /10 | Game usefulness /10 |
|---|---:|---:|---:|---:|
| A | 7.0 | 8.5 | 4.5 | 5.5 |
| B | 7.5 | 8.5 | 6.5 | 7.0 |

These are absolute scores, applied equally to SE and SW because the same strengths and defects recur in both. Scale: 0 unusable; 5 mixed and requiring repair; 7 useful with visible defects; 10 exceptional finished work. No art credit is given for frame count, hashes, exact timing or amount of changed imagery.

## Evidence and limits

Only the nominated 63 PNGs, INPUTS.json and clock were used. No parent mapping, producer documents, project source, other-agent reports or skills were consulted. All 63 image hashes matched the manifest before and after review; all inputs and INPUTS.json remained unchanged. See `input-hashes-before.json` and `input-hashes-after.json`.

I inspected all 32 walk cels at native 128, nearest 2× and 84-pixel proxies on light, dark and a diagnostic green ground. Every one of the eight cyclic adjacent pairs was inspected in each of the four sequences, including 07→00. The 22 bounded diagnostic PNGs include chronological full-body sheets, explicit pair crops, one attachment detail, and identity/turn context. An additional bilinear 84-pixel ground row checks sampling sensitivity; the primary game proxy uses nearest sampling.

**This is static-cel and chronological-pair perception, not observed normal-speed continuous human playback.** The supplied hold is 9/160 s (56.25 ms) per cel, 0.45 s per loop. No engine, world translation, root-speed, foot-lock/contact or turn-interpolation test occurred. The drawn ground is a diagnostic background, not a certified contact plane. Motion scores infer readability from the drawings; actual-speed smoothness and world contacts remain unverified.

## Identity and appearance

The coiled hair, beard, warm brown skin, concentrated eyes, blue/navy tunic, gold round shoulders/bracers, orange belt detail and heavy brown boots preserve the character in both facings. Face, kit and diagonal direction survive the 84-pixel proxy. The cardinal images establish identity and facing only; their walk mechanics did not set the diagonal score.

A03–05 lose the otherwise appealing boot/calf mass. B restores a substantial boot and cuff through this section, so it looks more like the same compact armored person throughout. B03 still has an awkward pitched/sole-presenting boot against a relatively side-on companion boot. On dark ground, hair, pants and rear boot lose separation; the bright armor and face remain useful anchors.

## Persistent feet and each cel

P means the boot on the more forward/lower leg at 00: screen-right in SE and screen-left in SW. Q starts bent back/higher. The labels follow pant/cuff attachment and sequence, not screen-side assumptions. Genuine depth overlap and unequal sole Y are allowed. In A03–05, P/Q attribution becomes partly occluded and uncertain; I do not turn that uncertainty into a claim that anatomy literally swaps.

| Cel | Common reading or A | B change at the same cel |
|---|---|---|
| 00 | P broad and forward/lower; Q bent back. Good chunky proportions. | Same. |
| 01 | P remains forward; Q folds/lifts. Appropriate differing foot heights. | Same. |
| 02 | P retracts beneath the body; Q is the small tucked boot. Toe/calf narrowing is visible. | Same. |
| 03 | A retains a thin front boot and crowded inner boot/cuff. Connected pixels, but pinched volume. | Q is a substantial pitched boot beside P; clearer attachment, abrupt change from tucked 02. |
| 04 | A remains a narrow crossing pair with a dominant long toe; alternate support is weak. | Q reads as the broad lower/front foot, P as the smaller rear foot. A useful exchange, not invalid merely because boots overlap or soles differ in Y. |
| 05 | A nearly stacks both feet into one thin column; the second foot is difficult at 84. | Q stays substantial beneath the torso; P remains visible behind. Better preparation for 06. |
| 06 | Q is the dominant lower boot; P is tucked behind. Some hand/body response. | Same. |
| 07 | P reappears forward/outward with a long projected shin and strongly pitched boot; Q bends back. | Same. |

SE and SW show the same pattern with opposing projection; the companion sheets were both inspected.

## All cyclic pairs

| Pair | A | B |
|---|---|---|
| 00→01 | Consistent small tuck/lift; no inferred identity flip. | Same. |
| 01→02 | P retracts/narrows, Q stays tucked. Visible volume/pitch change, compatible with a compact foreshortened pose. | Same. |
| 02→03 | Q enters an overlap but calf/boot mass pinches. | Main B defect: Q suddenly becomes a substantial pitched boot; cuff and heel/toe plane need a better bridge. |
| 03→04 | Thin ankle/toe forms continue; alternate support remains weak. | Q takes the lower/front role while P recedes. Clearer support exchange. |
| 04→05 | Feet compress into one column; weakest separation and provenance. | Plausible retraction under the torso; touching brown masses still partly merge. |
| 05→06 | Broad lower boot returns abruptly after the narrow middle. | Q retains broad boot volume into the exit anchor; clearest continuity gain. |
| 06→07 | P jumps from tucked/hidden to long outward shin and steep toe pitch; possible kick/pop impression. | Same unresolved transition. |
| 07→00 | P remains forward and Q rear. P rolls/flattens; closure is less concerning than 06→07. | Same. |

The hands do shift and the head bobs slightly, so the upper body is not frozen. However, hip/shoulder weight response is modest relative to the legs. A guarded fists-up walk can be a deliberate style choice; a stronger weight cue would make the exchange easier to believe. No sole-height difference, overlap, or low body bob is itself proof of invalid locomotion.

## Remaining defects and minimum repair

1. **A03–05, both directions:** pinched calf/ankle, thin toe and stacked feet conceal the alternate support exchange. This is the main reason to reject A as the preferred motion set.
2. **B02→03→04, both directions:** Q's recovery changes boot mass/pitch and cuff relationship too abruptly, despite the much clearer 04–05 silhouette.
3. **Shared 06→07, then 07→00:** P expands and pitches sharply before flattening at closure. The internal transition deserves attention first. Static sheets predict a pop; they do not prove a playback or world-contact failure.
4. **Shared upper body and dark-ground separation:** limited weight response and disappearing dark edges reduce polish, but are secondary to the feet.

**Smallest meaningful repair:** use B and redraw only cel 03's lower-body attachment in each direction, with 02 and 04 beside it. Carry Q from the tucked 02 position into the lower/front 04 position along one clear knee→cuff→heel/toe path; preserve boot volume and moderate the sudden sole-plane turn. Keep P attached and distinguish the overlapping contours where possible. Preserve B04–05. No extra frames or timing change is needed for this first repair. A separate follow-up should soften P's 06→07 shin/boot pitch change and recheck 07→00.

A/B pixel inspection confirms that only cels 03–05 below y86 differ; the other cels are byte-identical. That constrains the comparison rather than increasing either score. This review is frozen once and will not be rerated without changed imagery or new playback/contact evidence.
'''
for name,content in [('report.md',md),('report.json',json.dumps(report,indent=2)+'\n')]:
 with (OUT/name).open('x') as f:f.write(content)
# The ledger is created once after all outputs exist and intentionally excludes itself.
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (OUT/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for name in ['report.md','report.json','SHA256SUMS']:(OUT/name).chmod(0o444)
print('Frozen report.md, report.json and SHA256SUMS once. Ledger entries:',len(files))
print('report.md sha256:',hashlib.sha256((OUT/'report.md').read_bytes()).hexdigest())
print('report.json sha256:',hashlib.sha256((OUT/'report.json').read_bytes()).hexdigest())
print('SHA256SUMS sha256:',hashlib.sha256((OUT/'SHA256SUMS').read_bytes()).hexdigest())

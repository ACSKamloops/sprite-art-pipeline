from pathlib import Path
import datetime,json,hashlib
OUT=Path('/home/astra/artifacts/emberwake-lyra-contact-review-v1/review');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
scores={'A':{'appearance':8.0,'identity':9.0,'motion_readability':6.0,'game_usefulness':6.5},'B':{'appearance':8.0,'identity':9.0,'motion_readability':6.5,'game_usefulness':7.0}}
common_cels={
'00':'P is the lower/forward boot, Q bent back and higher. Good recognizable cuff, heel and toe volumes.',
'01':'P extends forward/lower and Q remains tucked. Head lowers slightly, hands and scarf move modestly.',
'02':'P retracts/narrows below the visible thigh while Q remains the small tucked rear boot; both attachments are readable.',
'05':'Both variants compress the legs into a narrow crossing. The forward boot moves toward the center and then back outward at 06; persistent P/Q attribution is less confident through the overlap.',
'06':'Q is the lower/forward boot and P the lifted rear boot. Clearer two-leg silhouette returns, with connected thigh/cuff and a useful bent-knee cue.',
'07':'P returns to forward/lower and Q recedes. Feet are relatively separated; boot volume is maintained. Good preparation for closure.'}
mid={'A':{'03':'Boots nearly align behind one another under the tunic. Plausible depth overlap, but the recovery of Q is hard to see at 84 pixels. No detached foot is claimed.','04':'P remains the dominant projected forward boot and Q is still crowded behind it. Alternate support reads late/weakly before the crossed 05.'},'B':{'03':'Two boots are visible with distinct pants/cuff attachment, making Q recovery clearer. The nearly parallel lowered legs add a brief standing-pose cue; this can also be legitimate double support. Short dark horizontal spur beside the rear glove/hip is untidy.','04':'Q reads lower/forward and P lifted behind. Better alternate-support silhouette; depth overlap and different sole heights are appropriate. This new foot position does not flow cleanly into shared 05.'}}
common_pairs={
'00->01':'Small, coherent extension/tuck. P and Q retain their roles.',
'01->02':'P retracts and becomes more vertical while Q remains tucked. Visible pitch/width change, but coherent attachments.',
'05->06':'Crossed, nearly single-column feet open into a clear alternate-leg silhouette. The forward-foot path makes an outward jog; a more continuous middle drawing would help.',
'06->07':'Readable reversal toward the other stride: P returns forward while Q recedes. Angular expansion in one hold, but calf/boot volume is retained; not the main residual defect.',
'07->00':'P stays the forward foot and Q the rear foot. Toe/cuff pitch changes modestly and the body aligns; no obvious static closure jump or identity inversion.'}
midpairs={'A':{'02->03':'Q enters the same narrow projection as P; overlap hides its swing and briefly makes the legs read as one column.','03->04':'The visible front boot continues downward with a small rear boot; alternating support remains weak.','04->05':'Feet cross tightly as the alternate leg takes over. Boot/cuff provenance is harder to follow, especially at 84.'},'B':{'02->03':'Q drops into view beside P. Attachment is clearer, though tucked-to-nearly-parallel legs is a noticeable pose jump.','03->04':'Q becomes the lower/forward boot while P lifts/recedes. This is the main improvement in explicit support exchange.','04->05':'The clearly separated lower foot moves inward into the crossed common pose, before moving outward again at 06. A projected sideways wobble remains, not a proven world foot-slide.'}}
cel={v:{d:{f'{i:02}':common_cels.get(f'{i:02}',mid[v].get(f'{i:02}')) for i in range(8)} for d in ['southeast','southwest']} for v in ['A','B']}
pair={v:{d:{f'{i:02}->{(i+1)%8:02}':common_pairs.get(f'{i:02}->{(i+1)%8:02}',midpairs[v].get(f'{i:02}->{(i+1)%8:02}')) for i in range(8)} for d in ['southeast','southwest']} for v in ['A','B']}
report={
'actor':'lyra','review':'Independent frozen visual judgment','frozen_utc':now,
'sources':'Only the 63 nominated input PNGs, INPUTS.json and clock. No producer source/history, project source, other reviews or skills were consulted.',
'coverage':{'walk_cels':32,'cyclic_pairs':32,'all_eight_pairs_per_sequence':True,'includes_07_to_00':True,'identity_context_images':31,'scales':['native128','nearest2x256','nearest84 proxy of 0.66 scale','additional bilinear84 ground row'],'grounds':['light','dark','green diagnostic grid'],'diagnostic_sheets':22},
'hashes':{'before_all_63_match':True,'after_all_63_match':True,'all_63_unchanged':True,'INPUTS_json_unchanged':True,'ledgers':['input-hashes-before.json','input-hashes-after.json']},
'limits':['Static cels, chronological sheets and explicit cyclic pairs were inspected. No observed normal-speed continuous human playback is claimed.','Hold 9/160 s = 56.25 ms; loop 0.45 s, from INPUTS.json. No timed human playback, engine, world translation, root-velocity or ground-contact/foot-lock test occurred.','Diagnostic ground is a background, not a certified contact plane; differing sole Y and legitimate overlap are accepted.','Context establishes identity/facing only, not a required diagonal gait. Motion scores are judgments of static chronology, with moderate confidence.'],
'scale':'Absolute 0-10: 0 unusable, 5 mixed/requires repair, 7 useful with visible defects, 10 exceptional finished work. No points for frame count, exact timing, hashes or amount changed.',
'scores':scores,'direction_scores':{v:{d:scores[v] for d in ['southeast','southwest']} for v in ['A','B']},
'preference':{'variant':'B','strength':'modest','confidence':'moderate for static chronology; actual-speed motion and world contacts unverified','reason':'Distinct boots/cuffs at 03 and Q taking the lower/forward role at 04 improve readable alternation at 84 pixels. B does not fix the shared 05 crossing and resulting foot-path wobble. Appearance and identity are tied.','use_level':'Useful small NPC walk draft; further transition polish is warranted for prominent/player movement.'},
'foot_tracking':{'P':'Boot attached to forward/lower leg at00: screen-right in SE, screen-left in SW. Followed via pants/cuff and cyclic role, never renamed solely by current screen side.','Q':'Other boot, tucked at00-02. B reveals its recovery at03 and lower/forward role at04; it is lower/forward at06 in both variants.','uncertainty':'A03-05 and shared05 contain legitimate but visually ambiguous overlap. Persistent identity there is partly inferred, not an anatomical swap allegation.'},
'cel_observations':cel,'cyclic_pair_observations':pair,
'remaining_defects':[
 {'id':'A1','variant':'A','directions':['southeast','southwest'],'cels':['03','04'],'severity':'medium','finding':'Leg overlap conceals Q recovery and leaves the alternate support role visually late/weak; at84 this briefly reads as one leg column. Overlap alone is not invalid.'},
 {'id':'S1','variant':'both','directions':['southeast','southwest'],'pairs':['04->05','05->06'],'severity':'medium','finding':'Shared05 squeezes the feet/cuffs into a crossed column. In B, the newly clear forward boot moves inward and then outward across04-06, leaving a projected wobble. Root/world data is absent, so this is not certified sliding.'},
 {'id':'B1','variant':'B','directions':['southeast','southwest'],'pair':'02->03','severity':'low to medium','finding':'Tucked boot to nearly parallel lowered legs is abrupt and adds a standing-pose cue. Double support itself is legitimate.'},
 {'id':'B2','variant':'B','directions':['southeast','southwest'],'cel':'03','severity':'low','finding':'Short dark horizontal spur beside the rear glove/hip is untidy on light ground at2x; SE source x44-50,y86, mirrored counterpart in SW.'},
 {'id':'S2','variant':'both','directions':['southeast','southwest'],'severity':'low','finding':'Head, scarf and hands do move, but hip/shoulder weight response remains modest. Dark scarf/boot boundaries lose some contrast on dark ground; bright hair and face preserve identity.'}
],
'smallest_meaningful_repair':{'base':'B','scope':'Redraw only05 lower legs in both facings with04 and06 visible as anchors.','instruction':'Keep Q on a continuous projected path beneath its thigh/cuff instead of moving inward then outward; show P passing behind with a small contour/value distinction. Preserve boot/heel/toe volume and accept normal depth overlap.','tiny_cleanup':'Clean the B03 dark spur; it does not require a global redraw.','verification_next':'Recheck04->05->06 and the full cyclic sequence at the supplied timing with an actual observed playback/world-translation pass before claiming smooth contacts.'},
'pixel_scope':'Only03 and04 differ between A/B, all differences at or below y84. Other cels are byte-identical. Technical scope confers no artistic credit; see pixel-scope.json.',
'freeze_policy':'Single frozen judgment. No rerating of unchanged images or target chasing.'}
md=f'''# Independent Lyra SE/SW review

Frozen once at {now}. **Prefer B modestly.** Its clearer 03–04 leg exchange improves utility at game size, but the shared crossed pose at05 still limits motion polish.

| Absolute /10 | A | B |
|---|---:|---:|
| Appearance | 8.0 | 8.0 |
| Identity | 9.0 | 9.0 |
| Motion readability | 6.0 | 6.5 |
| Game usefulness | 6.5 | 7.0 |

The same scores apply to SE and SW: both were inspected and show the same strengths and defects in opposing projection. Scale:0 unusable,5 mixed/requires repair,7 useful with visible defects,10 exceptional finished work. No points for frame count, exactness, hashes or amount changed.

## Evidence and limits

Only the63 nominated PNGs, INPUTS.json and clock were used. No producer source/history, other reviews, project source or skills were consulted. All63 hashes match before/after; all images and INPUTS.json remain unchanged. Coverage:all32 cels, all32 cyclic pairs including07→00, at native128, nearest2× and nearest84 proxy (0.66 scale) on light/dark/diagnostic green grounds. An extra bilinear84 ground row checks sampling sensitivity. There are22 bounded diagnostic sheets.

**This is static-cel/chronology perception, not observed normal-speed human playback.** Timing is manifest-derived:9/160s per cel (56.25ms),0.45s per loop. No engine, world translation, root velocity, foot-lock or contact test occurred. The ground grid is a diagnostic background. Different sole heights and legitimate depth overlap are accepted; neither proves bad contact. Motion confidence is moderate and actual-speed/world-contact behavior remains unverified.

The silver layered hair, warm face, dark teal/green armor and scarf, gold trim, pale bracers and brown gloves/boots preserve Lyra consistently at84 pixels. White hair and the face anchor the silhouette on every ground. Dark scarf/rear-boot edges lose some contrast on dark ground. Context was used only for identity and facing, never as the diagonal gait standard.

## Feet, cels and all cyclic pairs

P is the boot on the forward/lower leg at00:screen-right in SE,screen-left in SW. Q starts tucked behind. Labels follow thigh/cuff attachment and cyclic role, not current screen side. A03–05 and shared05 partly obscure identity; I do not claim anatomical inversion or literal detachment from this ambiguity.

00–01 keep P forward while Q folds.02 retracts P while Q stays tucked. A03 nearly aligns both boots under the tunic; A04 still presents P most strongly. B03 reveals two boot/cuff attachments, and B04 makes Q lower/forward with P lifted behind. Shared05 crowds the feet into a crossing;06 restores a clear Q-forward/P-back pose;07 returns P forward and prepares closure. All eight individual cels in both facings were checked.

| Pair | A | B |
|---|---|---|
|00→01|Coherent small extension/tuck.|Same.|
|01→02|P retracts and turns more vertical; attachments hold.|Same.|
|02→03|Overlap hides Q recovery; near single-column legs.|Q becomes visible, but the tucked-to-parallel lowered-leg change is abrupt.|
|03→04|Alternate support remains late/weak.|Clearer Q-forward/P-back exchange; the main gain.|
|04→05|Tight crossing obscures boot/cuff provenance.|New clear forward boot moves inward into shared crossed05.|
|05→06|Crossed feet reopen; forward foot makes an outward jog.|Same; with04 this creates an inward-then-outward projected wobble.|
|06→07|Readable exchange with an angular opening; boot volume holds.|Same.|
|07→00|P stays forward and Q rear; modest pitch/body change, coherent static closure.|Same.|

B03's nearly parallel lowered boots briefly suggest a standing pose in chronology, although double support itself is legitimate. B03 also has a short untidy dark horizontal spur beside the rear glove/hip (SE x44–50,y86; corresponding SW edge), clearest on light ground at2×. It is a small cleanup. Head, hands and scarf respond modestly; stronger hip/shoulder weight response could help but is secondary to05.

## Minimum repair

Use B and redraw only05's lower legs in each facing with04 and06 as anchors. Keep Q on one continuous projected path under its thigh/cuff rather than moving inward then outward. Show P passing behind with a small contour/value distinction, preserving heel/toe and boot volume while allowing normal occlusion. Clean B03's short spur separately. No extra frames or timing change is needed for the first repair.

B is a useful small NPC walk draft; prominent/player movement would benefit from this transition polish. An actual observed timed playback and world-translation pass is still needed before claiming smooth contacts. A/B differences are confined to03–04 at/below y84; other cels are identical. This limits the comparison and grants no art credit. This is one frozen judgment, with no unchanged-image rerating.
'''
# Improve mechanical number spacing in the prose without altering the judgment.
import re
md=re.sub(r'\b(all|the|at|from|to|with|only|under|into|shared|crossed|forward|of|are|below|confined to|and|through|same|before|after|ground|pose|cell|cels|including)(?=\d)',r'\1 ',md)
for name,content in [('report.md',md),('report.json',json.dumps(report,indent=2)+'\n')]:
 with (OUT/name).open('x') as f:f.write(content)
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (OUT/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for name in ['report.md','report.json','SHA256SUMS']:(OUT/name).chmod(0o444)
print('Frozen report.md/report.json/SHA256SUMS once. Ledger entries:',len(files))
for name in ['report.md','report.json','SHA256SUMS']:print(name,hashlib.sha256((OUT/name).read_bytes()).hexdigest())

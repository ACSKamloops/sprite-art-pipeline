from pathlib import Path
import json,hashlib,datetime
OUT=Path('/home/astra/artifacts/emberwake-rowan-upper-weight-review-v1/review');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
scores={'A':{'drawing_appearance':8.0,'identity':9.0,'motion_readability':6.5,'game_usefulness':7.0},'B':{'drawing_appearance':8.0,'identity':9.0,'motion_readability':6.5,'game_usefulness':7.0}}
cels={
'00':'P is the lower/forward boot and Q bent back. Both upper bodies are coherent. B slightly changes opposing hand/forearm heights and belt/hem position; no shoulder detachment.',
'01':'P remains forward while Q lifts. Different cuff/hand placement in B preserves connection and glove volume; torso remains visually firm.',
'02':'P retracts toward the body; Q stays tucked. Both hands remain readable with metallic cuff between glove and shoulder. Different hand-height/tilt drawing is visible at2x but small at84.',
'03':'Both boots come beneath the hips in a near dual-support/pass pose. B slightly changes hem and cuff contour; no clear layering reversal or detached arm. Weight gain is inconclusive.',
'04':'Q reads lower/forward and P lifts behind. B\'s extra upper opposition is easiest to see around this alternate contact, but remains restrained and is not a decisive game-size improvement.',
'05':'Shared legs narrow/cross, and the projected lower boot moves inward. The cream thigh and blue/gold hem remain distinguishable in A/B; B does not fix the lower-path compression.',
'06':'Q is lower/forward and P raised. Large cream thigh and glove/hem edges remain intelligible; no clear new occlusion error in B. Foot path opens outward again.',
'07':'P returns forward and Q recedes. Both preserve pauldrons/cuffs/gloves. B\'s belt/hem contour differs slightly; upper-body identity and closure remain stable.'}
pairs={
'00->01':{'upper':'Coherent small hand/cuff and waist movement in A/B; B adds a little vertical opposition without a detached wrist.','lower':'P extends while Q tucks; same lower sequence.'},
'01->02':{'upper':'Shoulder-to-cuff-to-glove reads as one limb in both. B\'s altered contour does not make direction or support distinctly clearer at84.','lower':'P retracts and turns more vertical; Q stays tucked.'},
'02->03':{'upper':'Forearms reverse modestly; B\'s hem/belt changes are visible on magnification but do not prove more weight.','lower':'Feet approach beneath the hips. Plausible double support/pass, not invalid because soles are close in Y.'},
'03->04':{'upper':'B\'s opposition around the alternate contact is clearer at native/2x, with small waist/hem edge changes. Attachments remain coherent.','lower':'Q takes the lower/forward role while P lifts. Both sets share this readable exchange.'},
'04->05':{'upper':'Raised cream thigh approaches the blue/gold hem. No clear new sleeve/hem layering reversal in B.','lower':'Lower boot moves inward and feet crowd into a crossing; principal shared residual concern.'},
'05->06':{'upper':'Glove/hem and lifted-thigh edges remain distinguishable, with restrained shoulder response in both.','lower':'Forward foot moves outward again; the04-06 inward/outward jog is unchanged by upper edits.'},
'06->07':{'upper':'Opposing arms begin returning. No obvious arm teleport or lost cuff in either.','lower':'P returns forward as Q recedes; angular but readable exchange with retained boot volume.'},
'07->00':{'upper':'Upper phase and head identity close. B\'s small belt/hem position change is visible, but no decisive static seam.','lower':'P stays forward and Q rear; modest pitch change, no apparent identity inversion.'}}
report={
'actor':'rowan','review':'Independent upper-body trial comparison, one frozen judgment','frozen_utc':now,
'sources':'Only nominated input63 PNGs, INPUTS.json and clock. No other Rowan scores, producer source/history, other reviews, project source or skills were read.',
'coverage':{'walk_cels':32,'cyclic_pairs':32,'all_eight_pairs_per_sequence':True,'includes_07_to_00':True,'identity_context_images':31,'scales':['native128','nearest2x256','nearest84 proxy at0.66 scale','extra bilinear84 ground row'],'grounds':['light','dark','diagnostic green grid'],'diagnostic_sheets':27,'additional_inspection':'Separate upper/lower cyclic-pair sheets and bounded4x A/B upper-attachment comparisons in both views.'},
'hashes':{'before63_match':True,'after63_match':True,'all63_unchanged':True,'INPUTS_json_unchanged':True,'before':'input-hashes-before.json','after':'input-hashes-after.json'},
'limits':['Static cels, chronological strips and cyclic pairs only. No observed normal-speed continuous human playback is claimed.','Hold9/160s=56.25ms, loop0.45s, manifest-derived. No engine, world translation, root-velocity or physical foot-lock/contact test occurred.','Diagnostic ground is only a background. Normal depth overlap, unequal sole Y and a restrained stylized torso are legitimate.','Motion and weight judgments have moderate static-sequence confidence. Actual-speed weight, smoothness and world contacts remain unverified.','Context images were used only for identity and facing, not a required diagonal gait.'],
'scale':'Absolute0-10:0 unusable,5 mixed/requires repair,7 useful with visible defects,10 exceptional finished work. More counter-motion, frame count, hashes and exact timing do not earn points by themselves.',
'scores':scores,'direction_scores':{v:{d:scores[v] for d in ['southeast','southwest']} for v in ['A','B']},
'preference':{'result':'tie','confidence':'moderate for static chronology; actual normal-speed perception unverified','reason':'B adds subtle hand/forearm opposition and waist motion while keeping attachment coherent. At84 pixels this does not establish a useful improvement in weight, direction or support reading over already coherent A. Shared legs still dominate the residual limitation.','no_automatic_counter_motion_bonus':True,'use_level':'Both are useful small game-character walk drafts with good appearance/identity and remaining transition polish.'},
'identity':'Spiky warm brown hair, blue eyes, royal-blue/gold tunic, silver round pauldrons/cuffs, cream trousers and brown gloves/boots remain consistent. Light/dark/ground contrast is useful; small gold/hem detail softens at84 but the character remains distinct.',
'attachment_findings':{'shoulders':'No clear new detached pauldron or shoulder-volume collapse in B; highlights and round armor read consistently.','cuffs_and_wrists':'B varies cuff/hand height and angle. Metal-to-glove continuity remains readable in each cel; no literal floating hand is found.','hem':'Small belt/hem edge changes relative to fixed thighs are visible, especially03->04 and07->00. They do not become a decisive static seam; actual flicker was not observed.','occlusion':'Raised cream thighs at05-07 remain separable from blue/gold hem and gloves. No clear new limb-layer reversal is visible.','weight':'B is a valid small-motion candidate, but more opposition alone does not demonstrate better planted weight at game size.'},
'foot_key':{'P':'Forward/lower leg at00:screen-right in SE,screen-left in SW, followed by cuff/sequence rather than side naming.','Q':'Other leg tucked at00-02, lower/forward at04 and06.','uncertainty':'05 crossing partly obscures the leg identities; no anatomical-swap claim is made.'},
'cel_observations':{v:{d:cels for d in ['southeast','southwest']} for v in ['A','B']},
'cyclic_pair_observations':{v:{d:pairs for d in ['southeast','southwest']} for v in ['A','B']},
'remaining_defects':[
 {'id':'S1','variants':['A','B'],'directions':['southeast','southwest'],'pairs':['04->05','05->06'],'severity':'medium','finding':'Shared05 crowds feet/cuffs and moves the lower foot inward before it moves outward at06. This projected path jog, with a small knee/cuff pinch, remains the clearest repair target. Root/world data is absent, so this is not certified sliding.'},
 {'id':'S2','variants':['A','B'],'directions':['southeast','southwest'],'severity':'low/weight polish','finding':'Torso weight response remains restrained; B\'s additions do not make support transfer decisively clearer at84. This is a polish limitation, not a demand for more amplitude.'}
],
'minimum_repair':{'upper_body':'No specific upper-body redraw is compelled by these static images. Do not amplify B merely to make it more different. A normal-speed observed comparison would resolve the small weight question better than another speculative upper edit.','shared_lower_body':'If making an art repair, redraw only05 below the waist in both views, with04 and06 as anchors: continuous Q knee/cuff/heel-toe path, P passing behind, stable boot volume and a small separating contour where projection allows.','scope_note':'This lower fix lies outside the upper-only experiment, so the trial itself does not close the whole-walk limitation.'},
'pixel_scope':'All16 A/B view/cel pairs differ only in y58..86; rows87..127 are exactly unchanged. This is verified technical scope, not artistic credit. See pixel-scope.json.',
'process_correction':'An empty scratch .py was inadvertently created beside the artifact root, immediately checked empty and removed. No input/canonical file was mutated; all retained outputs are in this review directory.',
'freeze_policy':'Single frozen judgment; no unchanged-image rerating or target chasing.'}
md=f'''# Independent Rowan upper-body comparison

Frozen once at {now}. **A/B tie.** B adds subtle arm/waist opposition while preserving coherent attachments, but it does not establish a meaningful improvement in weight or game-size readability over A.

| Absolute /10 | A | B |
|---|---:|---:|
| Drawing / appearance | 8.0 | 8.0 |
| Identity | 9.0 | 9.0 |
| Motion readability | 6.5 | 6.5 |
| Game usefulness | 7.0 | 7.0 |

Scores apply equally to SE/SW; both views were inspected independently. Scale: 0 unusable, 5 mixed/requires repair, 7 useful with visible defects, 10 exceptional finished work. Extra counter-motion, frame count and technical exactness do not earn art points by themselves.

## Evidence and limits

Only the nominated 63 PNGs, INPUTS.json and clock were used. No other Rowan scores, producer source/history, other reviews, project source or skills were read. All 63 image hashes match before and after; all inputs and INPUTS.json remain unchanged.

Coverage: all 32 walk cels and 32 cyclic pairs including 07→00, at native 128, nearest 2× and nearest 84 proxy of 0.66 scale, on light/dark/diagnostic green grounds. An extra bilinear 84 ground row checks sampling sensitivity. The 27 bounded diagnostic PNGs include upper/lower cyclic pairs and additional 4× A/B attachment comparisons in both directions.

**This is static-cel/chronology perception, not observed normal-speed continuous human playback.** Manifest timing is 9/160 s per cel (56.25 ms), 0.45 s per loop. No engine, world translation, root speed or foot-lock/contact test occurred. Diagnostic ground is just a background. Unequal sole Y, normal depth overlap and restrained stylized torso movement are legitimate. Actual-speed weight, smoothness and world contacts remain unverified.

## Drawing and identity

Spiky warm brown hair, blue eyes, blue/gold tunic, silver pauldrons/cuffs, cream trousers and brown gloves/boots remain unmistakably consistent. Identity/facing context was used only for those purposes. Both retain useful contrast on all grounds; small gold/hem detail softens at 84 pixels without losing the character.

B changes hand/forearm height and angle and slightly moves belt/hem contours. No clear new detached shoulder, collapsed pauldron, floating hand, broken cuff or limb-layer reversal is visible. Metallic cuff remains between shoulder/upper arm and glove; the raised cream thigh stays separable from blue hem and gloves. Small hem-edge changes around 03→04 and 07→00 are visible in enlarged comparison, but do not constitute a decisive static seam. I did not observe playback flicker.

B's opposition around 00/04 is a plausible weight cue at native/2×. At 84 pixels, neither direction gains a clearly stronger planted-support impression or clearer travel direction. A already has modest, coherent arm motion. Increasing the amplitude is not an evidence-based repair from these images.

## Cels and every cyclic pair

P is the forward/lower leg at 00: screen-right in SE, screen-left in SW. Q is tucked behind. Labels follow thigh/cuff and sequence, not current screen side. Shared 05 partly obscures identity; no anatomical-swap allegation is made.

00–01 retain P forward/Q back; 02 retracts P; 03 brings the boots beneath the hips; 04 presents Q lower/forward with P lifted. Shared 05 crowds the legs into a crossing; 06 restores Q forward/P raised; 07 returns P forward. Every cel's shoulder/cuff/hem/glove/thigh relationship was checked in both variants and directions.

| Pair | Upper-body judgment in A/B | Shared lower sequence |
|---|---|---|
| 00→01 | Coherent modest hand/waist move; B adds some vertical opposition. | P extends, Q tucks. |
| 01→02 | Cuff/glove attachment holds; B adds no clear 84-pixel readability gain. | P retracts, Q remains tucked. |
| 02→03 | Modest forearm reversal; B's belt/hem movement is visible but not proof of weight. | Boots approach beneath hips; plausible pass/double support. |
| 03→04 | B's opposition is clearer enlarged; small hem shifts preserve attachment. | Q takes forward/lower role, P lifts. |
| 04→05 | Thigh/hem/glove layers remain intelligible in both. | Lower foot moves inward and cuffs crowd: principal residual defect. |
| 05→06 | No clear new occlusion error in B; restrained shoulders in both. | Lower foot moves outward again, leaving a projected path jog. |
| 06→07 | Arms return without a clear teleport or lost cuff. | Readable angular exchange with retained boot volume. |
| 07→00 | Head/upper phase close; small B hem difference, no decisive static seam. | P stays forward, Q rear; modest boot-pitch change. |

## Defects and minimum action

The main remaining defect is shared 04→05→06: the feet/cuffs compress and the projected lower boot moves inward then outward. B cannot solve it with upper edits. Torso weight remains restrained in both; B's additions do not clearly improve support reading at 84 pixels. These are useful small-character walk drafts with remaining motion polish.

No specific upper-body redraw is compelled by this evidence. An actual observed timed comparison would resolve the small weight question better than amplifying B. If repairing art, redraw only 05 below the waist in each view against 04/06: keep Q's knee→cuff→heel/toe on a continuous projected path, P passing behind, boot volume stable and a small separating contour where projection permits. This is outside the upper-only trial's scope.

Technical check: all 16 A/B view/cel pairs differ only within y58–86; rows 87–127 are identical. This limits what the upper trial can improve and confers no art credit. Reports are frozen once, with no unchanged-image rerating.

Process correction: an empty scratch file was accidentally created beside the artifact root and immediately verified empty and removed. No input/canonical file was changed; all retained outputs are in this review folder.
'''
for name,content in [('report.md',md),('report.json',json.dumps(report,indent=2)+'\n')]:
 with (OUT/name).open('x') as f:f.write(content)
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (OUT/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for name in ['report.md','report.json','SHA256SUMS']:(OUT/name).chmod(0o444)
print('Frozen once. Ledger entries:',len(files))
for name in ['report.md','report.json','SHA256SUMS']:print(name,hashlib.sha256((OUT/name).read_bytes()).hexdigest())

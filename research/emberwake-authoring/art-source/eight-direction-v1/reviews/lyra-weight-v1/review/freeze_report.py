from pathlib import Path
import hashlib,json,datetime
from fractions import Fraction
R=Path('/home/astra/artifacts/emberwake-lyra-weight-review-v1/review');I=R.parent/'input'
before=json.loads((R/'input-hashes-before.json').read_text());m=json.loads((I/'INPUTS.json').read_text());scope=json.loads((R/'pixel-scope.json').read_text())
rows=[]
for r in before['images']:
 h=hashlib.sha256((I/r['path']).read_bytes()).hexdigest();rows.append({'path':r['path'],'sha256':h,'unchanged':h==r['sha256']})
after={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'count':len(rows),'all_unchanged':all(r['unchanged'] for r in rows),'manifest_sha256':hashlib.sha256((I/'INPUTS.json').read_bytes()).hexdigest(),'images':rows}
after['manifest_unchanged']=after['manifest_sha256']==before['manifest_sha256']
assert before['all_match'] and after['all_unchanged'] and after['manifest_unchanged'] and len(rows)==63
assert all(x['size']==[128,128] for x in before['images'] if x['path'].startswith(('A/','B/')))
assert len(m['holds'])==8 and all(Fraction(*h)==Fraction(9,160) for h in m['holds']) and sum(Fraction(*h) for h in m['holds'])==Fraction(9,20)
with (R/'input-hashes-after.json').open('x') as f:json.dump(after,f,indent=2);f.write('\n')
scores={'A':{'appearance':8.0,'identity':9.0,'motion_readability':7.0,'game_usefulness':7.5},'B':{'appearance':8.0,'identity':9.0,'motion_readability':7.5,'game_usefulness':7.5}}
notesA=[
 'P, the prominent lower/forward boot in00, remains readable while Q stays tucked. Upper body gives little distinct loading response.',
 'P changes from the oblique reach toward a straighter stance; Q remains tucked. Boot volume and knee/cuff continuity survive the projection change.',
 'Q unfolds down beside P over one exposure change. Attachment is readable, but the recovery path changes position/pitch briskly.',
 'The close stance opens into the opposite knee lift. Cuffs remain connected and differing sole heights are plausible depth/pose effects.',
 'The lower foot supplies a support candidate while the other knee stays raised. Head/torso response remains restrained.',
 'Raised boot clearance and rounded calf/toe volumes persist. Upper-body change adds relatively little weight information.',
 'The raised boot returns quickly into an open stance. The descent/sole-pitch change is one of the remaining larger chronological steps.',
 'Closure returns P forward and Q bent without a new join defect or identity change. The torso stays comparatively quiet.'
]
notesB=[
 'P/Q follow the same leg chronology. A modest rise out of00 adds a plausible release from the lowered body pose.',
 'Torso/head rise toward02 as P straightens. Hem and thigh remain joined; the exposed gray band is shaded pants, not background.',
 'Body returns from its high02 pose into03. The Q boot recovery remains brisk, with no new broken cuff or loss of calf/toe volume.',
 'Body settles into lowered04 as the opposite knee lifts. The extra arm/hip clearance is small and plausible; no transverse undercoat cut found.',
 'Torso rises from04 toward05 while leg roles stay readable. Glove mass and raised boot remain coherent.',
 'The higher06 pose completes the second repeating rise. Raised knee/cuff join and round boot volume remain intact.',
 'Body returns from high06 into07 while the recovering boot opens the stance. The inherited brisk boot descent remains; no extra upper-body reversal appears.',
 'The modest descent into lowered00 closes the repeating body rhythm. No new silhouette snap or disconnected limb is visible in the static cyclic comparison.'
]
pairs=[]
for direction in ['southeast','southwest']:
 for v,notes in [('A',notesA),('B',notesB)]:
  for n,note in enumerate(notes):pairs.append({'direction':direction,'variant':v,'pair':f'{n:02}->{(n+1)%8:02}','finding':note})
assert len(pairs)==32
issues=[
 {'id':'M1','variants':['A','B'],'severity':'minor motion limit','finding':'Recovering boot descends/unfolds briskly across02->03 and06->07; the body change in B does not supply an intermediate leg pose.','coordinate_convention':'Approximate inclusive canvas regions identifying the moving limb, not individual faulty pixels.','coordinates':{'02->03':{'southeast':[47,82,66,110],'southwest':[62,82,81,110]},'06->07':{'southeast':[63,79,86,112],'southwest':[42,79,65,112]}},'repair':'If timed playback confirms this is conspicuous, refine the tucked recovering knee/cuff/boot trajectory in02/06 while preserving attached heel/toe volume.'},
 {'id':'W1','variants':['A'],'severity':'moderate weight-expression limit','finding':'Torso, head and belt largely accompany the leg changes without a distinct repeated loading/release cue. The gait reads, but its weight is restrained.','coordinates':{'southeast_approx_region':[35,16,92,86],'southwest_approx_region':[36,16,93,86]},'repair':'A restrained coherent rise/fall and hip/hem response can supply loading information; B provides a modest successful example within this packet.'},
 {'id':'W2','variants':['B'],'severity':'minor remaining weight-expression limit','finding':'B adds useful body rhythm, but much of the response is a coordinated upper-body shift. Independent shoulder/hip articulation stays restrained.','coordinates':{'southeast_approx_region':[41,51,85,88],'southwest_approx_region':[43,51,87,88]},'repair':'No extra amplitude is required by this review. Judge any further articulation against actual playback and attachment continuity.'},
 {'id':'C1','variants':['A','B'],'severity':'tiny finish roughness','finding':'A sharp diagonal edge notch remains beside the01 thigh/cuff overlap. It is an outside contour indentation, not an interior material hole or detached boot.','coordinates_exact':{'southeast':[71,90],'southwest':[57,90]},'repair':'Optional one-pixel boundary cleanup only if this notch is unintended; preserve real limb separation.'},
 {'id':'G1','variants':['A','B'],'severity':'minor game-size limit','finding':'The brown boots and dark pants have reduced separation on dark ground at84px; the large silver hair and teal/gold torso remain clear.','coordinates':{'southeast_approx_region':[47,84,84,113],'southwest_approx_region':[44,84,81,113]},'repair':'A very small value distinction at the cuff/boot overlap would be more relevant than additional texture if this loss is troublesome in actual game backgrounds.'}
]
report={
 'review':'Independent Lyra SE/SW whole-walk body-weight comparison',
 'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'verdict':'prefer B, slightly',
 'scores_absolute_0_to_10':scores,
 'score_scale':'5 substantial defects;7 competent with limits;8 strong;9 exceptional. Half-points express bounded differences. All four dimensions judged separately.',
 'fresh_scoring':'Fresh scores from this nominated packet only. No prior numerical Lyra grades, other critics\' scores or Brann grades were imported.',
 'score_basis':{
  'appearance':'Both8: strong compact drawing, silver-hair/teal/gold material separation and rounded glove/boot volumes; tiny contour notches and dark lower-body contrast remain. B preserves drawing quality rather than earning points for displacement.',
  'identity':'Both9: exceptionally clear match to the nominated Lyra appearance in hair, face, teal coat, scarf, gold trim and brown gloves/boots. Cardinal context informs identity/facing only.',
  'motion_readability':'A7: competent foot-role exchange with restrained body weight and brisk recovery transitions. B7.5: modest coherent body rise/fall improves inferred loading/readability while the same leg-path limits remain. This is a static-chronology inference.',
  'game_usefulness':'Both7.5: recognizable, compact and readable at84px, with dark lower-body contrast limits and untested world contact/runtime presentation. B is preferred within this utility tier.'
 },
 'main_finding':'B adds a small repeating body rise/fall: lower around00/04 and higher around02/06. In static chronology this reads as a credible modest weight cue without a new erratic reversal. Knee/cuff/boot chains, glove mass and coat attachment remain coherent.',
 'drawing_nonregression':[
  'No new transverse undercoat slit or material hole was found in the inspected hip/hem connections. The gray strip exposed under B02 is thigh shading, with opaque material continuity.',
  'Small new alpha0 components near B04 SE80..81,83 / SW47..48,83, B05 SE80,77 / SW48,77, and B06 SE83,80..81 / SW45,80..81 sit at arm/body or hip/limb separation. Enclosure in a4-neighbor alpha test alone is not a defect.',
  'B changes upper-body/hem projection in00/01/02/04/05/06;03/07 remain byte-identical acrossA/B. No art credit is assigned to pixel count or this exactness.',
  'Rounded knee/calf, boot cuff, heel and toe volumes survive. Different sole heights and legitimate depth overlaps are allowed; screen-left/right do not identify anatomical legs.',
  'The visible closure07->00 retains identity and attachment. B\'s lowered00 follows the preceding intermediate07 coherently in the static comparison.'
 ],
 'foot_tracking':'P denotes the projected boot prominent lower/forward in00; Q denotes the other projected boot. Track them across tuck, overlap and support/swing exchange. Support candidates are visual interpretations, not certified world contacts.',
 'issues':issues,
 'smallest_meaningful_next_repair':'The remaining useful motion target is the recovering boot trajectory around02->03 and06->07. A small existing-pose knee/cuff/pitch adjustment could reduce those jumps while preserving volume; actual normal-speed playback should establish whether it is needed. No additional body-bob amplitude is called for.',
 'coverage':{'input_pngs':63,'animation_cels':32,'cyclic_pairs':32,'pairs_per_view_per_variant':8,'views':['southeast','southwest'],'scales':['native128px','nearest-neighbor2x','nearest-neighbor84px game-size proxy'],'backgrounds':['light','dark','muted'],'context_images':31,'context_use':'Appearance plus30 cardinal images for identity/facing only.','own_diagnostic_pngs':25,'extra_diagnostics':['hip/knee/cuff/boot alpha sheets','6x undercoat continuity comparisons','6x notch/connection context'],'source_exclusions':'No producer docs, maps, source, skills, prior/other reports or canonical files were read.'},
 'pair_checks':pairs,
 'geometry_clock':{'canvas':[128,128],'pivot_nominated':m['pivot'],'game_scale_nominated':m['game_scale'],'exposures_per_variant':8,'hold_fraction':'9/160s','hold_ms':56.25,'loop_fraction':'9/20s','loop_ms':450.0,'credit':'Correct timing and exposure count establish comparison conditions and earn no art points.'},
 'preservation':{'manifest_sha256':before['manifest_sha256'],'png_count_before_after':63,'all_before_match_manifest':True,'all_after_match_before':True,'manifest_unchanged':True,'write_scope':str(R)},
 'perception_limits':{'observed':'Static individual cels, ordered full-loop strips, all adjacent cyclic pairs and attachment/alpha diagnostics.','not_observed':'Continuous normal-speed human playback or engine presentation of this packet.','motion_claim':'B looks more weighted in the static pose chronology; actual smoothness, lack of flicker/jitter, display cadence and subjective56.25ms exposure visibility are not certified.','world_contact':'No world translation, root registration, foot locking/skating or actual contact timing was tested. Flat backgrounds serve contrast only.','scores':'Motion and game scores remain bounded inferences from static art; appearance and identity are still-image judgments.'},
 'freeze':'Single frozen judgment and output SHA ledger; no unchanged-art rerating or score-target iteration.'
}
md='''Lyra whole-walk weight comparison: frozen independent review

**Slightly prefer B.** Its small repeating torso/hip rise and fall gives the ordered poses more weight while retaining the coat, knee/cuff and boot connections. The improvement is modest; the brisk recovering-foot paths remain.

| Variant | Appearance | Identity | Motion readability* | Game usefulness* |
|---|---:|---:|---:|---:|
| A | 8.0 | 9.0 | 7.0 | 7.5 |
| B | 8.0 | 9.0 | 7.5 | 7.5 |

Scores are fresh judgments from this packet. Scale anchors: 5 substantial defects, 7 competent with limits, 8 strong, 9 exceptional. No prior Lyra, other critic or Brann grades were imported. *Motion and game scores are static-chronology inferences.

B sits slightly lower around 00/04 and rises around 02/06. That repeated relationship is consistent with a restrained loading/release cue. It does not introduce an extra erratic reversal in the ordered cels. Much of the upper body still moves together, so this is a modest weight improvement rather than exceptional shoulder/hip articulation. At 84 px the effect stays small.

Both retain strong silver-hair/teal/gold drawing and a clear Lyra identity. Rounded glove, knee, calf, boot cuff, heel and toe volumes remain intact. The gray strip under B02 is pants shading, with opaque continuity beneath the coat. No new transverse undercoat seam or disconnected leg was found. Small transparent gaps at limb overlaps are legitimate depth clearance; their being enclosed in a four-neighbor alpha test does not make them fabric holes.

The main remaining limits are:

- Recovering-foot projection and sole pitch change briskly across 02→03 and 06→07 in both variants. Approximate SE limb regions are x47–66/y82–110 and x63–86/y79–112; SW mirrors are x62–81/y82–110 and x42–65/y79–112.
- A has limited body loading response; B improves this but keeps restrained independent shoulder/hip articulation.
- A tiny diagonal outside-edge notch remains at SE01 (71,90), SW01 (57,90), unchanged in B. This is contour roughness, not an interior hole or detached cuff.
- Dark pants and brown boots lose some separation on dark backgrounds at 84 px.

The smallest meaningful next motion target would be a small existing-pose knee/cuff/boot-pitch refinement around 02/06 if timed playback confirms the recovery jumps are conspicuous. No further body-bob amplitude is indicated by this review. The 07→00 wrap keeps coherent attachment and identity in both variants.

All 32 animation cels and all 32 cyclic pairs were inspected in SE/SW, including both wraps, at native 128 px, nearest 2× and nearest 84 px on light, dark and muted backgrounds. Twenty-five bounded diagnostic PNGs retain the coverage. Appearance and all 30 cardinal context images informed identity/facing only. Each exposure is 56.25 ms and each loop 450 ms. Pixel count, exposure count, hash equality and exact timing earn no art points.

All 63 PNG hashes match INPUTS.json before review and remain unchanged afterward; the manifest is unchanged. Source access stayed within this nominated input. All outputs are confined to this sibling review directory.

This review observed static cels, chronology and pair/alpha sheets. It did not observe continuous normal-speed human playback, actual engine display cadence or world-space contacts. B's modest weight advantage is inferred from poses; timed smoothness, absence of jitter, foot locking/skating and contact timing remain unverified.

See report.json for all 32 pair findings and coordinate-qualified limits; pixel-scope.json, alpha-components.json and gap-coordinate-checks.json for bounded diagnostics; input-hashes-before/after.json for exact preservation evidence. This judgment and output ledger are frozen once.
'''
for name,data in [('report.json',json.dumps(report,indent=2)+'\n'),('report.md',md)]:
 with (R/name).open('x') as f:f.write(data)
files=sorted(p for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (R/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for n in ['report.md','report.json','SHA256SUMS']:(R/n).chmod(0o444)
print(json.dumps({'scores':scores,'verdict':report['verdict'],'cyclic_pairs':len(pairs),'diagnostic_pngs':len(list(R.glob('*.png'))),'ledger_entries':len(files),'inputs_preserved':after['all_unchanged'] and after['manifest_unchanged']},indent=2))

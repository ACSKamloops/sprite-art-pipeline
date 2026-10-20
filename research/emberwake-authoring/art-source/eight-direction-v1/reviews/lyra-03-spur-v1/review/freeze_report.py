from pathlib import Path
import hashlib,json,datetime
from fractions import Fraction
R=Path('/home/astra/artifacts/emberwake-lyra-se03-spur-review-v1/review');I=R.parent/'input'
before=json.loads((R/'input-hashes-before.json').read_text());diffs=json.loads((R/'exact-differences.json').read_text());m=json.loads((I/'INPUTS.json').read_text())
rows=[]
for r in before['images']:
 h=hashlib.sha256((I/r['path']).read_bytes()).hexdigest();rows.append({'path':r['path'],'sha256':h,'unchanged':h==r['actual_sha256']})
after={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'count':len(rows),'all_unchanged':all(x['unchanged'] for x in rows),'manifest_sha256':hashlib.sha256((I/'INPUTS.json').read_bytes()).hexdigest(),'images':rows}
after['manifest_unchanged']=after['manifest_sha256']==before['manifest_sha256']
assert len(rows)==63 and before['all_match'] and after['all_unchanged'] and after['manifest_unchanged']
assert all(len(x['changed_pixels'])==17 if x['frame']==3 else len(x['changed_pixels'])==0 for x in diffs)
assert all(all(r['size']==[128,128] for r in before['images'] if r['path'].startswith(v+'/')) for v in ['A','B'])
holds=[Fraction(*x) for x in m['holds']];assert len(holds)==8 and all(x==Fraction(9,160) for x in holds) and sum(holds)==Fraction(9,20)
with (R/'input-hashes-after.json').open('x') as f:json.dump(after,f,indent=2);f.write('\n')
local=[
 {'direction':'southeast','removed_opaque':{'y':86,'x_inclusive':[44,49]},'removed_partial_alpha':{'y_inclusive':[87,88],'x_inclusive':[45,49]},'recolored_opaque':{'xy':[50,86],'A_RGBA':[8,4,4,255],'B_RGBA':[17,10,7,255]}},
 {'direction':'southwest','removed_opaque':{'y':86,'x_inclusive':[79,84]},'removed_partial_alpha':{'y_inclusive':[87,88],'x_inclusive':[79,83]},'recolored_opaque':{'xy':[78,86],'A_RGBA':[8,4,4,255],'B_RGBA':[17,10,7,255]}}
]
pairs=[]
for d in ['southeast','southwest']:
 for v in ['A','B']:
  for n in range(8):
   q=(n+1)%8
   if n==2:
    finding='A03 has a short horizontal dark tab below the glove; it is not supported by the adjacent glove contour.' if v=='A' else 'Entering cleaned03: glove/cuff remain full and attached; the upper-leg outline loses its isolated horizontal tab without a new notch in the palm.'
   elif n==3:
    finding='The A03 horizontal tab disappears by04, creating a one-cel contour accent.' if v=='A' else 'Leaving cleaned03: hand, tunic hem and rounded boot volumes remain consistent with04; no new cut-out or detached part found.'
   else:finding='Both endpoint drawings are byte-identical across A/B. Visual chronology check found no cleanup regression;07->00 closure is retained.' if n==7 else 'Both endpoint drawings are byte-identical across A/B. Visual chronology check found no cleanup regression.'
   pairs.append({'direction':d,'variant':v,'pair':f'{n:02}->{q:02}','finding':finding})
report={
 'review':'Independent Lyra frame03 spur cleanup nonregression review',
 'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'verdict':'prefer B',
 'scope':'Tiny drawing cleanup only; no numeric motion scores or whole-animation rerating.',
 'reason':'B removes a one-cel horizontal upper-leg-edge tab and faint fringe below the main glove while retaining the actual glove, cuff, cloth and boot. Improvement is clearest enlarged on light ground and subtle at84px.',
 'source_scope':'Only the nominated INPUTS.json and63 PNGs were read. No producer source, mappings, prior/other reports or skills were read; no prior character grades were imported.',
 'preservation':{'input_pngs':63,'all_match_manifest_before':True,'all_unchanged_after':True,'manifest_unchanged':True,'manifest_sha256':before['manifest_sha256'],'all_writes':'This sibling review directory only.'},
 'exact_edit':{'changed_frames':['southeast03','southwest03'],'unchanged_animation_cels':14,'changed_pixels_per_view':17,'opaque_pixels_removed_per_view':6,'partial_alpha_pixels_removed_per_view':10,'opaque_pixels_recolored_per_view':1,'coordinate_convention':'Zero-based x,y in128x128 input canvas; ranges inclusive.','coordinates':local,'full_pixel_values':'exact-differences.json'},
 'anatomy_adversarial_check':[
  'The brown glove mass and wrist/cuff highlight above the edit remain pixel-exact. The removed six opaque pixels form a horizontal tab at y86, below the main glove silhouette, rather than a supported finger contour.',
  'In A03, most of the tab lies below a transparent interval under the glove and attaches laterally to the upper-leg edge. The faint duplicate fringe at y87/88 extends this same stray ledge.',
  'B retains the leg-edge pixel at SE50,86 / SW78,86 with a compatible dark-brown recolor. The thigh/cloth mass, shin, boot cuff, heel and toe below are retained.',
  'Compared with02 and04, B03 keeps a full round glove and a plausible hand/hip overlap. No palm truncation, missing knuckle, torn hem, lost boot volume or detached part was found.',
  'This is a visual interpretation from nominated raster cels, not a semantic proof of the artist\'s intended anatomy. The source-free evidence supports cleanup acceptance.'
 ],
 'coverage':{'animation_cels':32,'cyclic_pairs':32,'pairs_per_variant_per_view':8,'views':['southeast','southwest'],'scales':['native128px','nearest-neighbor2x','nearest-neighbor84px game-size proxy'],'backgrounds':['light','dark'],'extra_diagnostics':'6x local03/02/04 edge and alpha comparison','diagnostic_pngs':19,'context':'All30 cardinal context PNGs plus appearance inspected for identity/facing only.'},
 'fixed_geometry_and_timing':{'animation_canvas':[128,128],'nominated_pivot':m['pivot'],'game_scale':m['game_scale'],'exposures_per_variant':8,'hold_fraction':'9/160s','hold_ms':56.25,'loop_fraction':'9/20s','loop_ms':450.0,'note':'Timing metadata is shared and unchanged within this A/B packet. Correct fractions earn no drawing credit.'},
 'pair_checks':pairs,
 'remaining_defects':'No further repair of the nominated spur region is required. Ordinary stepped pixel edges and tiny occlusion gaps remain, without evidence that filling or trimming them would improve anatomy. Broader gait quality is outside this cleanup verdict.',
 'perception_limits':{'observed':'Static cels, ordered strips, adjacent cyclic pairs and enlarged local/alpha diagnostics.','not_observed':'Continuous normal-speed human playback, actual engine presentation or world-space foot contacts.','claim_boundary':'The cleanup improves a local still-image contour and shows no observed static nonregression. No stronger timed smoothness, flicker, contact, foot-lock or engine claim is made. At84px the difference is small; visibility during the56.25ms exposure is not established.'},
 'freeze':'Single final cleanup judgment; report and output ledger written once.'
}
assert len(pairs)==32
md='''Lyra frame03 spur cleanup: frozen nonregression review

**Prefer B for this cleanup.** The removed tab reads as a stray upper-leg-edge ledge below the glove. B keeps the glove/cuff mass, tunic/hip shape and boot intact. No hand, cloth or boot damage was found. No numeric motion scores were assigned.

Only03 changes in each view:17 pixels per view, comprising six opaque pixels removed, ten faint fringe pixels removed and one opaque edge pixel recolored. The other14 animation cels are byte-identical acrossA/B.

Coordinates are zero-based on the128px canvas:

| View | Opaque tab removed | Faint fringe removed | Edge recolor retained |
|---|---|---|---|
| SE03 | x44–49,y86 | x45–49,y87–88 | (50,86) |
| SW03 | x79–84,y86 | x79–83,y87–88 | (78,86) |

The actual brown glove and highlighted wrist/cuff above this region remain exact. InA03 the ledge projects laterally from the upper-leg edge beneath a transparent interval under the main glove. Its one-cel horizontal shape and repeated faint fringe are poorly supported by02/04. B removes that accent without truncating the rounded palm, cutting the cloth mass or shaving the boot. This is a raster-based anatomical reading; the nominated images do not provide semantic layer proof.

All32 animation cels and all32 cyclic pairs were inspected, including07→00 for both variants in both views, at native128px, nearest2× and nearest84px on light/dark backgrounds. Nineteen bounded diagnostic PNGs include local6× and alpha comparisons. All30 cardinal context images and appearance were used for identity/facing only. All63 input hashes match INPUTS.json before review and remain exact afterward; the manifest is unchanged.

The improvement is clearest at2× on light ground and subtle at84px. Frame03 lasts56.25ms within the450ms loop. Only static cels, chronology and pair sheets were observed: normal-speed visibility, flicker, engine presentation and world contacts were not tested. This verdict accepts a local cleanup and makes no new motion-quality claim.

No additional repair in this region is indicated. Source access stayed within the nominated input; no producer files, mappings, prior/other reports, skills or prior character grades informed the verdict. See exact-differences.json for every edited RGBA value, report.json for32 pair findings and input-hashes-before/after.json for preservation proof. This report and output ledger are frozen once.
'''
for name,data in [('report.json',json.dumps(report,indent=2)+'\n'),('report.md',md)]:
 with (R/name).open('x') as f:f.write(data)
files=sorted(p for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (R/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for n in ['report.md','report.json','SHA256SUMS']:(R/n).chmod(0o444)
print(json.dumps({'verdict':report['verdict'],'input_pngs':63,'pairs':len(pairs),'diagnostic_pngs':19,'ledger_entries':len(files),'inputs_preserved':after['all_unchanged'] and after['manifest_unchanged']},indent=2))

from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
root=Path('/home/astra/artifacts/emberwake-brann-border-delta-review-v1')
src=Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1/brann-ne-gait-v1')
a=json.loads((root/'DATA-AUDIT.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Ensure report still binds the same source bytes after visual inspection.
assert sha(src/'BORDER-CLEANUP.json')==a['cleanup_ledger_sha256']
for r in a['rows']:
 assert sha(src/'frames'/r['file'])==r['raw_sha256']
 assert sha(src/'cleaned-frames'/r['file'])==r['cleaned_sha256']
report={
 'review_id':'emberwake-brann-border-delta-review-v1',
 'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
 'review_type':'data and visual delta audit only; not a new numerical art rating',
 'source_root':str(src),
 'sequence':'Started only after the anonymous Rowan report was frozen and its hashes delivered to the parent.',
 'source_files_read':['frames/00.png..07.png','cleaned-frames/00.png..07.png','BORDER-CLEANUP.json'],
 'source_fingerprints':[{'file':r['file'],'raw_sha256':r['raw_sha256'],'cleaned_sha256':r['cleaned_sha256']} for r in a['rows']],
 'cleanup_ledger_sha256':a['cleanup_ledger_sha256'],
 'data_evidence':{'file':'DATA-AUDIT.json','sha256':sha(root/'DATA-AUDIT.json')},
 'composite_evidence':{'file':'COMPOSITE-DELTA.json','sha256':sha(root/'COMPOSITE-DELTA.json')},
 'data_conclusion':{'exactly_11_literal_black_alpha1_border_texels_erased':True,'replacement_rgba':[0,0,0,0],'all_131061_other_rgba_texels_exact':True,'all_31480_alpha2plus_rgba_texels_exact':True,'declared_hashes_and_coordinates_match':True,'clean_ne_positive_alpha_border_count':0},
 'mirror':{'rule':'For each source (x,y), set destination (128-x,y) if 0<=128-x<128; initialize destination RGBA to zero. This is the declared pivot mirror, not x_new=127-x_old.',
 'raw_to_clean_delta_count':7,'per_frame_delta_counts':[r['mirror']['changed_texels'] for r in a['rows']],
 'reason_delta_less_than_11':'Four changed source texels have x=0 and map to x=128 outside the destination. The other seven map in range.',
 'clean_nw_positive_alpha_border_count':6,
 'remaining_clean_nw_border':[{'file':r['file'],'texels':r['mirror']['cleaned_positive_alpha_border']} for r in a['rows'] if r['mirror']['cleaned_positive_alpha_border']],
 'remaining_border_origin':'Clean NE x=1 at y=50,51,64 in frames 06 and 07 maps to NW x=127. All six values are (0,0,0,1).',
 'claim_limit':'Clean NE has no positive alpha at its border; clean NW under this declared derivation does not have an empty positive-alpha border. No runtime/baker acceptance claim is made.'},
 'visual_review':{'frames':'all eight raw and cleaned NE cels; all eight independently derived raw and cleaned NW cels','scales_px':[128,84],'resampling':'nearest neighbor','backgrounds_rgb':{'light':[224,224,216],'dark':[28,32,40],'game_like_flat':[71,82,61]},'native_stage_px':[128,128],'game_scale_limit':'84 px is a nominal game-size review presentation only; no runtime scale, scene or engine was inspected.',
 'new_visible_anatomy_difference_observed':False,'new_visible_material_difference_observed':False,'new_visible_silhouette_difference_observed':False,'new_visible_motion_difference_observed':False,
 'motion_limit':'Still chronology comparison only. No continuous playback perceived and no timing, gait, physical-contact or controller acceptance; unchanged non-border body pixels supply no evidence of a new drawn gait.',
 'composite_delta':'Ordinary 8-bit Pillow alpha composites: on light, NE has 11 changed display pixels at both 128 and 84, each at most one RGB code value; NW has 7 at 128 and 1 at 84, each at most one RGB code value. All tested dark and game-like composites are byte-identical raw vs clean. Rounding/resampling are specific to this presentation.',
 'visible_result':'No meaningful new character appearance/anatomy/material/motion difference was perceived in these actual-alpha composites. Mathematical image differences on light exist and are not described as byte-identical.'},
 'limits':['No new numerical art score or transfer of previous grade.','No claim about a changed generation or production method.','No source/canonical/runtime files were edited; outputs exist only in this new report folder.','Only the specified raw/cleaned 8-cel delta and explicitly derived mirror were checked.','The cleaned mirror retains six faint alpha1 border texels; this audit does not authorize deleting them.','Runtime, production baking, engine acceptance, source-provider behavior and continuous motion were outside scope.']}
(root/'REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
md='''# Brann border cleanup: frozen data and visual delta audit

**The NE cleanup is exact: 11 literal black alpha-1 border texels changed to transparent zero RGBA; all other RGBA values are unchanged.** No new visible character/anatomy/material/motion difference was found in the scoped still comparisons. This is a delta audit, not an art rerating, method change claim, or game/runtime acceptance.

The anonymous Rowan art review was frozen and its hashes delivered before this audit began. This report reads only the nominated `frames`, `cleaned-frames`, and `BORDER-CLEANUP.json`. No source or canonical files were written.

## Exact NE changes

All eight inputs and outputs are 128×128 RGBA. Independent array comparison agrees with the cleanup ledger's hashes and coordinate sets. Every listed change is **(0,0,0,1) → (0,0,0,0)**, and all are on the stage border.

| Cel | Changed NE coordinates (x,y) | Count |
|---|---|---:|
| 00 | (0,60), (127,67), (127,69) | 3 |
| 01 | (0,60), (127,67), (127,69) | 3 |
| 02 | (38,127) | 1 |
| 03 | none | 0 |
| 04 | (127,51) | 1 |
| 05 | (127,51) | 1 |
| 06 | (0,51) | 1 |
| 07 | (0,51) | 1 |
| **Total** | | **11** |

All **131,061 other texels** retain their complete RGBA, including hidden RGB under transparent alpha and every non-border texel. All **31,480 source texels with alpha ≥2** retain exact RGBA. The cleaned NE stage has **zero positive-alpha border texels**. Cel 03 is byte-identical as a PNG as well as decoded RGBA.

## Independent NE→NW derivation

Both raw and cleaned inputs were independently mapped using the declared rule **x_new = 128 − x_old**, with y unchanged, zero-initialized RGBA output and out-of-range destinations skipped. This differs from a conventional x_new = 127 − x_old flip.

| Cel | Raw→clean NW changed texels | Clean NW positive-alpha border texels |
|---|---:|---:|
| 00 | 2 | 0 |
| 01 | 2 | 0 |
| 02 | 1 | 0 |
| 03 | 0 | 0 |
| 04 | 1 | 0 |
| 05 | 1 | 0 |
| 06 | 0 | 3 |
| 07 | 0 | 3 |
| **Total** | **7** | **6** |

Four changed NE texels have x=0 and map to x=128, which is skipped in both derivations; the other seven changes survive. Independently derived raw/clean PNG and decoded-RGBA hashes are in DATA-AUDIT.json.

**The cleaned NW border is not empty.** In each of frames 06 and 07 it retains **(127,50), (127,51), (127,64)**, each exactly **(0,0,0,1)**. They originate at unchanged clean NE x=1. Thus the verified empty-border statement applies to NE; it does not extend to this NW derivation. This audit authorizes no additional removal and makes no production-baker claim.

## Visual delta

Inspected every raw/clean NE cel and every independently derived raw/clean NW cel at native **128 px** and nominal game-size **84 px**, nearest neighbor, against light `#e0e0d8`, dark `#1c2028` and muted game-like flat `#47523d` backgrounds. All six complete comparison sheets are in `evidence/`. Actual alpha was used, without amplification.

I perceived **no meaningful new character appearance, anatomy, material, silhouette or motion difference** attributable to the cleanup. The actor's drawn body pixels and their pose chronology are preserved. This does not rerate the original art, assert continuous motion perception, or grant previous acceptance to an untested derivative.

The light-background composites are mathematically different by at most **one 8-bit RGB code value** at sparse stage-edge display pixels: NE has 11 changed display pixels across all cels at both 128 and 84; NW has 7 at 128 and 1 at 84. The tested dark and game-like ordinary composites are byte-identical raw versus cleaned. These numbers depend on the specified nearest resampling and Pillow 8-bit alpha-compositing/rounding; they do not describe all possible renderers. COMPOSITE-DELTA.json records each frame/background/scale result.

Eighty-four pixels is a nominal review presentation, not a claim about this actor's actual engine scale. Game scenes, lighting, movement speed, animation timing, physical contact, controller feel, production baking and runtime acceptance were outside scope. Motion observations compare still chronology; no continuous playback was perceived. There is no new numerical art score and no changed-generation-method claim.

## Binding and reproducibility

`DATA-AUDIT.json` contains all 16 full source/output SHA-256 fingerprints, every changed coordinate/value, all remaining mirror border texels and both PNG/decoded-RGBA mirror fingerprints. `audit_delta.py` reproduces the data audit and ordinary contrast sheets in this report folder only. The source cleanup ledger SHA-256 is **f33a814ccbc479ee5401be0c160da7e42295bb67e1543bd21f117d4f77f67d70**. Source hashes were rechecked after visual inspection. `REVIEW.json` binds the data/composite evidence files; `SHA256SUMS` freezes the report and generated evidence. No game/runtime or provider files were changed.
'''
(root/'REVIEW.md').write_text(md)
files=sorted(p for p in root.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
(root/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(root)}\n' for p in files))
print('Frozen',len(files),'artifacts')
for name in ['REVIEW.md','REVIEW.json','DATA-AUDIT.json','SHA256SUMS']:print(sha(root/name),name)

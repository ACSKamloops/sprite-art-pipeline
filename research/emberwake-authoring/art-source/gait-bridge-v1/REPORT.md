# Emberwake source-pixel gait bridges v1

Candidate B creates clearer intermediate swing-foot travel while preserving its assigned visible boot pixels, standing-leg paint and original upper bodies. It is **changes required**, not a hole-free production result: thin inter-leg seams and several isolated alpha pinholes remain. Candidate A is rejected because protected standing-leg paint occludes 50 translated boot texels across its edited cels.

Only `/home/astra/artifacts/emberwake-gait-bridge-v1` was written. The production source files were read and copied, never edited. No generation, API, model, installed-skill edit or sub-agent was used.

## Inputs and frozen roles

`SOURCE-INPUTS.json` records the four original absolute paths and file SHA256s. Byte-identical snapshots are under `inputs/{lyra,brann}/{atlas.png,animations.json}`. Both input atlases are 1024x1920 with 128x128 cells and 8 columns. The source manifests, not the older skill example's frame order, are authoritative.

- Lyra south: `0,1,2,112,4,5,6,113`; north: `56,57,58,114,61,62,63,115`.
- Brann south: `0,1,2,112,5,6,7,113`; north: `56,56,58,114,61,62,63,115`.
- Only phases **1,2,5,6** change. Contact phases 0/4 and painted passing cels 112..115 remain original.
- Phases 1/2: screen-left visible leg swings; screen-right leg remains support. Phases 5/6: screen-right swings; screen-left remains support. These screen roles are fixed for every actor/view/job.
- Body context and visible limb donor are the exact same original target-phase cel. No donor crosses view, actor or phase. The upper body therefore keeps the original head, arms and costume at each phase.

All actual changes lie in native `[43,82,86,121)`; all decoded RGBA outside that rectangle is identical. Each job retains its explicit binary source owner and protected support mask. Visible nonowned paint inside the ROI is restored at identity. These are authored visible-part assignments on fused sprites, not recovered hidden anatomy. The right/left split, short-boot bottom and distal plateau were measured from the coordinate sheets and then frozen in each `spec.json`.

## Two bounded trials

A (`trial-a-down`) moves the assigned boot down 2px at phase 1/5 and 4px at phase 2/6, retaining its shape and using a connected proximal mesh. It changes 2,679 RGBA pixels in 16 cels, but some translated boot paint collides with original support paint and is occluded. It is mechanically rejected.

B (`trial-b-boot-preserved`) refines the visible part seam and adds only the least outward offset needed for zero assigned-boot occlusion. All right-side swings stay at dx=0; left-side swings use dx=-1 except Lyra north phase2 (-2) and Brann south phase2 (-3). Vertical travel remains +2/+4. Maximum displacement is 5px (Brann south phase2). It changes 2,789 RGBA pixels across 16 cels.

The boot plateau translates rigidly without rescaling or rotating; the connected proximal region between y82 and the per-job plateau is the only deformed part. A four-triangle strip mesh, explicit controls and binary ownership produce an inverse nearest source map. The original part location clears by copying that cel's exact transparent `[0,0]` source texel. Every changed output byte has an exact source-texel witness in the same original cel. No synthesized color, blend, dilation, hole fill or new paint was used.

B has zero boot occlusion and no disconnected whole-sprite alpha components. Assigned visible-part area grows 11.7% to 40.9% because the proximal leg extends; it does not collapse. Area preservation alone does not validate anatomy. The largest outward offset (Brann south p2) visibly widens the lower leg.

## Remaining gap and anatomy concerns

B fails the requested hole-free gate in 9 of 16 edited cels. Most new alpha0 pixels form thin enclosed spaces at the swing/support seam; the separation can read as an inter-leg opening, but its straight one-pixel edge is a visible construction artifact in the enlarged check. Brann also has small isolated pinholes next to support-boot edges.

- Lyra north p2: 21 new enclosed transparent pixels, main region `[60,85,62,99)`.
- Brann south p2: 26 additional enclosed pixels; main seam `[61,85,64,100)` plus small regions `[60,100,61,101)` and `[59,102,60,104)`.
- Brann north p6: isolated new alpha0 pixel `[67,101,68,102)`.

`previews/b-alpha-gaps-source-candidate-marked-2x.png` shows source, B and marked B for every edited cel. `verification/ALPHA-GAP-REGIONS.json` records all boxes. These marks exist only in the diagnostic sheet, never in the candidate atlas. No third trial or concealed repair was made.

Static visual review covered all four complete eight-pose gaits at native 2x, their 7->0 wrap, thighs and ankles at 2x, plus the marked alpha seams. The foot travel is more gradual than source and the equal-clock held control. The source's useful painted passing geometry is retained. Its differing boot volume/material remains a source property, not a reason to revert the passing keys. This worker did not make a real-time visual playback acceptance claim: exact-timed previews were generated and decoded mechanically; independent motion review remains the decision point.

## Portable application to later atlases

`apply_bridges.py` consumes frozen integer maps and validates **each edited target/donor cel's decoded RGBA SHA256** plus its phase assignment. It does not require the entire atlas to match v3. Unrelated changed action/waist/settle cells and their original manifest provenance can remain. It appends after the highest occupied or referenced cell, can use unused padding slots, and never overwrites existing occupied/referenced artwork. It preserves every prior manifest field and lineage record, replacing only the edited walk frame references and appending new lineage.

Python signature: `apply(atlas_path, manifest_path, actor, out, variant='b')`.

```bash
python3 /home/astra/artifacts/emberwake-gait-bridge-v1/apply_bridges.py \
  --atlas /path/to/later/lyra/atlas.png \
  --manifest /path/to/later/lyra/animations.json \
  --actor lyra --variant b --out /path/to/fresh/candidate/lyra
```

The output directory must not exist. Changed donors or phase assignments require a rebase; the helper rejects them before creating output. The helper is a candidate-building tool, not production approval.

Self-contained exact replay from the retained snapshot:

```bash
cd /home/astra/artifacts/emberwake-gait-bridge-v1
python3 apply_bridges.py --atlas inputs/lyra/atlas.png \
  --manifest inputs/lyra/animations.json --actor lyra --variant b \
  --out replay-lyra
```

Repeat with brann and a fresh directory. `verification/apply-baseline-*` already proves decoded candidate-atlas equality. `build_trial.py --variant a|b --out-name FRESH_CHILD_NAME` retains the original mesh producer; use the frozen integer maps for authoritative replay.

## Verification and clocks

`verification/SUMMARY.json` separates successful mechanics from the failed hole-free gate. Verification passed:

- All 32 A/B frozen maps reproduce their retained expected RGBA exactly; every changed-pixel journal is exhaustive and source-attached.
- Upper-body/outside-ROI and protected support RGBA equality; B's 16 rigid visible boot plateaus preserve every assigned texel at its integer translation.
- Independent batched geometry places every mapped sample within 0.50000001px per axis of the inverse mesh coordinate.
- Append-only application reproduces B on the original input and preserves an unrelated changed action cel, an appended settle cel, action metadata and all original provenance in a separate fixture.
- A stale donor rejects before output; an existing output sentinel is preserved.
- Original source hashes remain unchanged.
- APNG has eight exact delays of 9/160s, with decoded RGBA equal to the requested poses; MP4 contains 72 frames at 160fps, with nine identical decoded frames per authored pose and duration exactly 0.450000s.

The integer map is authoritative. A second floating-point linear solver resolves some exact geometric half-texel ties differently in five Brann A/B cels. Those alternative floating mesh rebakes are not byte-identical; coordinates still pass the independent nearest-geometry bound. Do not re-triangulate/re-warp as a substitute for replaying the retained source-xy arrays.

The equal-clock held control uses the source pose slots `0,0,0,3,4,4,4,7` at eight equal 9/160s holds. The actual original eight-pose walk is also shown separately. APNG is the exact RGBA authority; lossless H264 uses an opaque diagnostic backdrop and RGB-to-YUV444 conversion.

`previews/*-comparison-2x.apng` and `*-comparison-exact-450ms.mp4` show four columns: source, held contact/pass control, rejected A, B. Native APNGs, fullstage native/2x wrap sheets, fixed-crop 2x full-body sheets, 2x thighs/ankles and every adjacent contact pair including 7->0 are included. Open `index.html` for a local review page.

`ENVIRONMENT.json` records tool versions. `SHA256SUMS.json` covers all retained files except itself. `diagnostics/` preserves incomplete producer/test attempts and explains their corrections; these are not extra approved gait variants. No installed skill files were modified.

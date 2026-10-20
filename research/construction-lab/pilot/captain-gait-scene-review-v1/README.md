# Bounded actual-scene swing-pitch trial

**Mechanical trial and bounded renders pass. This is ready for independent visual review, not promotion or an art score.** The fixed `fb859cf` swing-pitch hypothesis transfers into the exact frozen crease scene without changing stance, upper-body/guard/root motion, geometry, paint, materials or cloth animation. No full65-frame render or video was produced.

Source: `/home/astra/projects/captain-3d-reference-paint-lab/artifacts/cape-cloth-volume-v1/crease/full-captain-diagnostic.blend`, SHA`bfbdbef0b2b0281b854746b05be8018484376d250c0ac2429a6a492c5011bbcd`. Source file SHA is unchanged after the trial. Candidate SHA`51fccef2f1d5899739b530a375b9db20181bc65271f477341cd1d5491faa67dc`.

## Mapping and action ownership

Before editing, all521 original physical hip/knee/ankle targets reproduce the frozen scene within1.475micrometers. **All vertices of the actual current rigid boot meshes** reproduce journal-predicted positions within0.830micrometers. Physical coordinates subtract the existing DrawRoot previewXY translation; its rotation is identity and no preview compensation is rebaked. The armature/action mapping is therefore measured, not guessed.

Only eight tracks change: `l/r thigh,shin,foot,toe`. Source action is copied, its original curves retained, and the copied matching `OBCaptain_BODY_mocap_prototype` **ActionSlot explicitly bound**. The isolated original action receives a retention/fake-user flag; its key curves remain exact, and the source file is untouched. All80 selected location/quaternion/scale channels have521 fractional keys through closed endpoint131, verified after packed reopen. This is not an integer-only131-key action.

During swing, original thigh/shin matrices swing-rotate to the fixed physical journal directions. Foot/toe matrices receive journal `Rnew*Rold^-1` about the original ankle plus journal ankle translation. Source twist/basis is retained rather than reconstructing new anatomical roll. During stance, source local location/quaternion/scale values are copied exactly rather than roundtripping matrices. At all521 evaluations:

* Nonleg pose matrices, **all object world matrices**, cloth/all shape values and stance leg matrices are exact, zero difference.
* Actual candidate joint origins match journal within1.475micrometers; all actual boot vertices within0.830micrometers.
* All raw mesh geometry/topology/UV/weights/stored normals/attributes/shape coordinates/material graphs/filters/material slots/packed source-image bytes are unchanged by fingerprint.
* All original action-key fingerprints remain exact. Those assets/actions also survive saved packed reopen exactly.

## Actual mesh gates

Source and candidate were evaluated on1041 eighth-interval samples using **all five actual rendered body meshes**, physical root coordinates, immutable articulated sole ownership IDs, and whole actual boot vertices. Both retain the source's small fractional interpolation residuals:

| Metric | Source | Candidate |
|---|---:|---:|
| All-five maximum floor penetration |58.67micrometers|58.67micrometers|
| Maximum stance sole floor gap |58.67micrometers|58.67micrometers|
| Flat heel/toe/sole material drift |16.84micrometers|16.84micrometers|
| Minimum reach marginL/R |1.286/5.517mm|1.286/5.517mm|
| Segment-length maximum error |0.320micrometers|0.544micrometers|
| Projected source-hinge unit-dot error |2.02e−7|2.02e−7|

The existing contact tolerance is1mm. Candidate swing whole-boot floor gap minimum17.50micrometers, maximum199.68mm; it remains a minimum-clearance constraint, not a swing force/contact assertion. Candidate heel-toe length variation≤0.287micrometers. A **newly evaluated** left boot shifted down50mm at unchanged flat stance penetrates49.999975mm and is rejected by the same guard. No pelvis/hip/root re-lowering or reach clamp is introduced.

Owner-based evaluated triangle intersections use the existing `audit_all_contacts.py` / `audit_cape521.py` geometry basis. Cape versus all-five body was checked at521 times, prop groups versus all-five body at65 source export times. Exact triangle-pair identities were compared between original and candidate; no permissive new allowlist was added.

* Cape/body pairs:0 at every sample.
* Body/sword blade, sword hardware, shield panel/rim and shield bracket pairs:0.
* Pre-existing body/backgear maximum658 and body/shield-grip maximum252 are retained as exposed raw attachment observations, not newly certified collision allowances.
* **New triangle pairs:0.** Every pair-set difference is in `contact-delta-proof.json`.

No body self-intersection, volume containment or intersection depth test was run. Finite1041/521/65 scopes do not certify all real times. The sourceC0 loop/velocity limitations from the skeleton trial remain; noC1 or loaded-force truth is claimed.

## Bounded matched renders

Mechanical gates passed before rendering. CPU6 threads,128 samples, seed19, denoise off; source/candidate whole native256 and384 canvases, same source camera/materials/lighting. Five keys were selected from numeric phases/worst cases, without image searching:

*35 and103: both feet in unchanged stance. Their source/candidate RGBA pixels are **exactly identical at both resolutions**.
*57: largest small left local flexion increase.
*75.25 and8.75: largest left/right local flexion reductions.

Initial recipe labels1/33 were corrected by the measured stance phase audit: those frames include one swing foot and cannot certify unchanged whole stance. `render-contract.json` records this selection-only correction; the frozen target/action recipe is unchanged.

See `whole-pair-384-source075.25.png`, `whole-pair-384-source008.75.png`, `whole-pair-384-source057.00.png`, and stance controls `whole-pair-384-source035.00.png` / `whole-pair-384-source103.00.png`. The256 pairs are also native, independently rendered canvases. Shadow/indirect-light pixels may change outside the animated lower-leg silhouette even though upper-body/object matrices and materials are exact.

At changed key75.25, `candidate-render-settings-packed.blend` reopens with exact geometry/assets/original actions and explicit slot; its freshly rendered384 RGBA pixels are **exact** to the prior candidate render. PNG file bytes differ only metadata(File/Date/render timings); the first overly strict file-byte assertion failed and was replaced with separately reported byte/pixel equality. `packed-verify.log` and `render-proof.json` record the independent pixel/asset verification. No extra full65 render or art score was used to resolve it.

## Reproduce

Run the scripts sequentially from the isolated worktree with Blender4.5.9,6 threads. `check_mapping.py` measures the original source gate; `build_scene.py` creates the isolated copied action; `audit_scene.py` measures actual floor/contact gates; `render_pairs.py` refuses to render unless those gates pass; `verify_render_result.py` independently verifies saved packed assets/action channels/pixels; `postprocess.py` makes whole-pair displays and verifies stance-control pixel equality. Source paths and fixed target commit are recorded in recipes/proofs. All script outputs belong to this case only.

The prior max-height ablation, fixed skeleton pitch trial and private original causal-audit artifacts are unchanged. No source preference, original blend, other checkout, body paint or front-value derivative was edited.

# Rejected upper-neck/shoulder carry residual

**Rejected; do not reuse as an approved improvement.** One bounded residual from immutable crease assembly creates new body/cape intersections and increases existing backgear contacts. No amplitude search, full65 bake, whole-motion quality score, or further upper repair is part of this task. Root has redirected production toward cape shape craft after independent baseline review.

Input: paint-lab `artifacts/cape-cloth-volume-v1/crease/full-captain-diagnostic.blend`, SHA256 `bfbdbef0b2b0281b854746b05be8018484376d250c0ac2429a6a492c5011bbcd`. Rejected packed output `captain-upper-carry-residual.blend`, SHA256 `d4522001b7188c3c9caf5da5ef1caca3568db3160b98b35e3d9daa2bd182aafb`.

There is no true chest bone in this rig. Spine influences11974 vertices including lower hanging surfaces and7 vertices shared with leg tracks; neck influences7518 upper-chest/neck vertices, with restZ minimum−.0235. The tested residual uses neck and both clavicles. It preserves spine and original root/hips/leg tracks. Every original action/fcurve value remains intact. Named target empties hold cached original authored matrices plus the residual; Copy Transforms constraints are an explicit removable layer. Original upper motion was retained as the base, not replaced with a generic animation.

One recipe: w=sin(2π*(sourceInterval−33)/130); yaw=−1.5°w about source +Z, roll=−1.0°w about source +Y, around the actual source spine-tail/chest pivot. Neck, clavicles and the four existing equipment/cape/backgear attachment roots share this transport. Arms and hands inherit the clavicle response. Head position follows the transported neck but original world orientation/gaze is counter-preserved to float precision. Targets parent to the source armature, so physical DrawRoot translation restoration transports the entire residual consistently. No prop was fitted separately to a rendered image.

Support phase comes from the actual immutable articulated ledger: right heel index33/stance78, left98/stance82 over130 intervals. These are inferred kinematic labels, not measured forces. Source103 is left heel/right toe transfer, not swing. Exact degrees, pivot metres and support labels for521 samples are in `build-proof.json`.

`failed-upper-torso-mask/` retains the first rejected ownership preflight. It incorrectly treated all spine-weighted upper torso as a lower surface and therefore found9.257 mm motion. The corrected owner inventory is explicit, with before/after vertex IDs and fixed source-rest bounds in `packed-reopen-owner-proof.json`: every actual root/hip/thigh/shin/foot/toe-owned body vertex plus all hanging body restZ≤−.1, and complete vertices of both rigid boots and both ankle joints. Mixed spine/neck/shoulder upper torso is an intentional deformation exception. No lower error tolerance was relaxed. Original hips/root/spine bone matrices and actual protected lower rendered world coordinates require and achieve **exact0 error at all521 times**, including packed reopen. Rest geometry, topology, UVs, weights, shape data, materials, filters and image bytes remain exact. Upper-body maximum displacement is25.946 mm; gaze matrix rounding error4.154e−7, common upper transport error5.365e−7, mount transport4.768e−7. These are float-precision limits, not byte-exact head matrices.

Fresh original/candidate contacts expose the failure:

- Body/Cape original0→13 triangle pairs, only at sampled source45.
- Body/Backgear maximum658→693, a35 increase in maxima. At source113 the matched counts are650→693(+43); largest same-phase increase is source75,561→628(+67). Do not describe35 as the worst matched-phase delta.
- Shield panel/rim/bracket, sword and cape/prop contacts remain0. Existing shield-grip252 remains unchanged and is an observational attachment count.

All65 actual geometry samples and521 actual palm/grip/cape-anchor checks are fresh. Grip error remains below.7µm; anchor geometry moves consistently. New intersections are not excused as intended inherited contacts. `contact-delta-proof.json` exposes every changed count and location. These are triangle intersection observations, not containment or continuous-time certification.

Matched original/rejected extrema source1/65 are actual native256/384 CPU renders. Whole and nearest3x upper-seam crops are provided. This limited rejected-attempt witness set replaces the conditional full key set; no full65 render was produced. Rendering reopens the immutable source and rejected packed candidate. AI still-image/source inspection is not continuous video ingestion or independent art approval.

Exact new surface/attachment owners are diagnosed separately in `../captain-upper-carry-contact-owner-v1/`. That report is read-only; no new geometry or carry variant is authorized or produced.

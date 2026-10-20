# Fixed-volume source-painted greave comparator

**Unapproved experiment.** This uses actual closed tapered shin shells, separately articulated knee shells, rigid boots and a femur-owned hidden tube. It preserves a single source-painted material/UV binding rather than fitting images per frame. It is not recovered3D armor, a complete character mesh or an accepted gait/art asset.

I personally viewed all eight fullbody keys of both corrected packs at2x. Original upright-master plate/boot paint retains segmented straps and identity better than the generated128px cell. Remaining appearance limits are substantial: the near shin is often a narrow strip below the tabard/shield, the head/chest/gear remain mostly a rigid carried illustration, and closed source-colored edges cannot supply genuine unseen armor art. These geometry/palette checks do not establish convincing anatomy or finished movement.

## Portable inputs and reproducible commands

Python + Pillow, NumPy, SciPy are needed. All source files required by the current builder are copied here; it does not need to write or import a live root checkout. Output must be a new directory. Original art is project-provided, not claimed CC0. Source UV/bone anchors are manually declared for this one fixed view.

```sh
python pilot/captain-greave-volume-binding-v1/build.py --source-mode original --output /path/to/new-canonical-pack
python pilot/captain-greave-volume-binding-v1/build.py --source-mode original --poses pilot/captain-greave-volume-binding-v1/source/poses-amplitude-70.json --output /path/to/new-amplitude-pack
python pilot/captain-greave-volume-binding-v1/verify.py pilot/captain-greave-volume-binding-v1/artifacts/original-underlap-v1
python pilot/captain-greave-volume-binding-v1/verify.py pilot/captain-greave-volume-binding-v1/artifacts/amplitude-underlap-v1
python pilot/captain-greave-volume-binding-v1/joint_basis_check.py
```

`build.py --poses NEW_PACKET` changes motion only. The fixed UV bind always comes from `source/poses.json` (canonical58%-stance packet). Greave/knee local vertices and UVs are exactly identical between the corrected44/70-stride packs. Any future packet requires a fresh render/evidence. Only the current camera/basis,42/48 bone lengths and verified forward-facing pose range are supported; arbitrary clips/directions are not validated by this experiment.

The archived root plane builder supplies the unchanged upper-body composition and old thigh-plane placement. Its global source paths are redirected to this private package; source constructors write only into the explicit new output. Frozen copied boot rasterizer/proxy are source inputs; the rasterizer has one declared adaptation from128-only UV limits to actual texture dimensions. No other worktree is mutated. Cell/original first builders are archived as historical source snapshots, not current scripts to run from their nested source directory.

## Corrected pack contract

- `artifacts/original-underlap-v1`: exact canonical v2 motion packet SHA`2b3dd986…`.
- `artifacts/amplitude-underlap-v1`: root's70-unit-stride trial-v2 packet SHA`1ed1d548…`. This packet passed geometry constraints only, **not art/gait acceptance**.
- `manifest.json` records `poses_sha256`, `fixed_UV_bind_poses_sha256`, actual source and builder hashes, localUV/3D meshes, triangles, perframe world/projected vertices, source ownership and all PNG hashes.
- Fullframe in-place256RGBA PNGs: `frames/NNN.png`.
- Drop-in layers: `integration-layers/NNN-far_shin.png`, `NNN-near_shin.png` include separately articulated knee shells; boot and thigh follow the same naming. Use these thigh layers too: they include the required hidden underlap. Do not place old kneepad/shin imagery underneath the replacement.
- Raw separate shells/caps and upper layers remain in `layers/`; source partitions and exposed extendedUV textures in `parts/`.
-72 endpoint-excluded samples,1200ms, unchanged declared16/17ms holds. GIF uses cumulative10ms quantization totaling1200ms. Same canvas/origin for every pose; no per-frame fitting.

## Source ownership and volume

The generated cell00 (`source/leg-master-128.png`) was the first control. Its shell version visibly retained the gold-disc-on-decorated-sleeve limitation; only its contact sheet/manifest are retained as an unapproved historical comparator. The preferred source is byte-identical `source/upper/source/native-256.png`, the upright construction master. Original inspected anchors: far hip113132/knee107166/ankle102211, near146138/153165/159215. They are source registrations, not recovered true3D anatomy.

Original source-owned leg pixels are disjointly partitioned into thigh, kneecap, shaft and boot. Source-only recomposition is byte-exact, with zero duplicate ownership. Thigh source ends before the hidden articulation: it previously left up to6px real alpha gaps. Corrected packs add an explicitly authored tapered femur tube, radius7..8/depth5, length44 along the fixed42-unit femur (2units distal underlap). Source-sampled dark-red/joint colors cover the hidden region; the source thigh plate stays above it. This is a fixed articulated component, not a per-pose patch. It is not claimed extracted source art.

Shin rings have fixed longitudinal/radial coordinates and tapered depth. The knee uses a separate ellipsoid following the averaged thigh/shin axis. UV coordinates are projected/calibrated **once** from the neutral source bind, stored and unchanged throughout both motion packets. Nearest sampling retains actual source colors. Unknown rear/side/underside texture is declared nearest-source-edge extrusion. Closed geometry prevents flat card collapse, but extrusion does not invent a valid unseen motif or correct physical relighting. The source paint carries its original baked light.

## What the checks establish

`joint-basis-report.json` checks actual thigh/combined-shin alpha near each projected knee in all72 poses, separately for both corrected packs. Maximum nearest alpha gap is0px. This closes the observed floating-kneepad construction gap; connectivity is not anatomical/art quality.

The same report audits raw normal orientation at1,441 phases. No camera-facing sign correction activates: minimum raw dot camera is0.460 canonical /0.399 amplitude. Normal versus neutral reference stays positive. Future poses outside this scope might cross the selector and need a material-frame implementation/review, not camera-dependent relabeling.

Canonical geometry generator copy exactly matches packet-declared builder. The copied current amplitude generator has SHA`9d6cee16…`, while its previously frozen packet declares`f6986e08…`; both are recorded. All72 world hip/knee/ankle positions match exactly. Continuous sample diagnostics use that explicitly identified current geometry copy; no claim that its bytes are the earlier archived generator.

`verification.json` proves source partition exactness, alpha0/255, no new lower-part opaque RGBA colors, and constant mesh neighbor distances. At the canonical neutral bind, every visible shin/cap pixel matches the declared neutral affineUV source-paint reference. **This is paint-coordinate fidelity, not original silhouette identity or art approval.** The amplitude pose differs; comparing its framezero to the canonical card would be invalid, so it is explicitly not evaluated as that neutral-paint test.

Fresh repeat renders compare frame/integration PNGs byte-for-byte. Neither palette, metric count, successful geometry, connected alpha nor a repeatable build constitutes artistic acceptance. Wholeloop native motion and all visible joints must still be adversarially reviewed.

# Seventy-two-frame Captain engine validator

This is a **separate rejected-v6 baseline**, not a replacement acceptance receipt. V6 art remains7.955/10 and its rendered-material stance has a known surrogate-witness defect. No contact-quality claim is made. The old twelve-frame lab and receipts remain unchanged.

```sh
godot --rendering-method gl_compatibility --path pilot/captain72-godot -- \
  --source=/home/astra/projects/sprite-construction-lab/pilot/space-marine-captain/assembled-v6

xvfb-run -a godot --display-driver x11 --rendering-method gl_compatibility \
  --audio-driver Dummy --path pilot/captain72-godot --script res://test_runtime.gd -- \
  --source=/absolute/frozen-72-frame-candidate \
  --output=/absolute/fresh-proof-directory
```

The loader accepts256×256 fullRGBA,72 ordered source-hashed PNGs, each1/60-second hold. SpriteFrames is saved and reopened, then actually rendered over light and dark opaque backgrounds. The player explicitly selects frame and progress from a continuous60Hz clock. Controls include pause/play, restart, single hold step, native1×/nearest2× and speed½×/1×/2×.

Current source manifest SHA `96fed23f2f1e75373363c1db923b9b8031bb5f701c206c28f5e43e15dd0e2207`. Fresh Godot4.7.2 GLCompatibility run passed **1384 checks**, with144 actual GPU frame composites exact0LSB. Counts of live samples vary with engine scheduling. All72 boundaries plus genuine early timestamps are checked across multiple cycles and speeds; accumulated72 scaled process steps wrap to0; pause, step and restart are exercised. Actual AnimatedSprite2D's own clock is additionally sampled after draw through two loops. The first run sampled before node processing and produced39 timing mismatches; it is preserved at `/home/astra/artifacts/captain72-v6-negative-engine-v1/`, not restamped. Post-draw fencing corrects this harness ordering. V2 and finalv3 runs remain separate.

Eight actual full-actor translated images span two cycles using the declared−36,+14 stride and fixed rounded draw origin. Their entire256×256 source rectangle matches renderedRGBA at that origin. This is a placement test, **not a material stance test**: physical root and source-image placement are recorded separately; no lowest-row-xmin witness is accepted as stable foot identity. Full evidence/resource/snapshots: `/home/astra/artifacts/captain72-v6-negative-engine-v3/`. Current source hashes bind the committed receipt.

Positive material-contact validation is pending producer source-bound stable material-anchor records, contact intervals and a whole-character draw-offset rule. A surrogate pixel extrema lock can pass while actual boot material skates. No old contact result, declared IK stance or rendered guide dot is inherited. Future candidate tests must write new outputs and receive a fresh independent art review.

## Fresh v9 and stronger material test

The separately frozen assembled-v9 manifest `ead3bb795c0da303253ed5b40c9cb0556079b29787ae4ea9fd76d6e29a6f1648` passed1392 fresh actual engine checks,144 exact dark/light composites. It still received **8.61/10, changes requested** in the independent visual review. No technical result adds points to that score.

```sh
xvfb-run -a godot --display-driver x11 --rendering-method gl_compatibility \
  --audio-driver Dummy --path pilot/captain72-godot --script res://test_material.gd -- \
  --legs=/absolute/frozen-dense-leg-pack --actor=/absolute/exact-assembled-pack \
  --output=/absolute/fresh-material-output
```

The optional actor manifest must bind the exact leg manifest. Actual transparent512×288 GPU readbacks cover both isolated boots and the full actor, two cycles with five fractional samples per tick. One global draw translation applies to both boots and the actor; physical root is separately continuous. Acceptance uses every colored/alpha pixel of the actual world-boot RGBA image, not the selected minimum-row witness used to compute the correction. Each stance episode must have one unique whole-boot GPU digest. Hidden/occluded boot material is not asserted visible in the assembled actor; heel/toe collision and art remain separate.

Dense-v20 + assembled-v9 passed221 assertions: each global stance episode had exactly one GPU whole-boot digest, max visual/physical correction0.914358px (actual engine Float32). Raw continuous physical drawroot failed material stability as expected. The stronger historical dense-v15 test (`--expect-unstable`, actor omitted) passed147 negative-control assertions by **detecting material instability**, not by approving v15: global episodes produced multiple distinct images. V15 lacks later source-attached identity metadata, explicitly accepted only in the historical-negative branch. All actual boot encoded hashes are retained in the report.

Hash-bound summaries are committed in `proof/`. Raw1440-context reports, individual GPU digests and actor snapshots remain at `/home/astra/artifacts/captain72-v9-material-gpu-v2/` and `/home/astra/artifacts/captain-v15-material-gpu-negative-v1/`. Current code/source hashes bind these fresh runs. Dense-v21 is a different later source; these v20/v9 results must not be restamped onto it.

## Fresh visually accepted v12 scope

Assembled-v12 manifest `847e859fffb80656e98ae8ae7582655edeffde409ee4dbbc402bc42c0886d9df` received independent visual9.045/10, every category≥8.9, for this oneviewWalk. Fresh actual Godot tests passed1406 clock/resource/pixel checks (144 exact light/dark composites) and221 material assertions. Dense-v22 leg manifest is `1350fe45ea3f53fc3be3b9b81d2f8177315a55a893ec8302b70a02c3fde2f1d9`; the actor binds it exactly. All tested globalstance episodes have one unique actual GPUwholebootRGBA digest; continuousphysicalroot negative still exposes displacement. These are fresh source-bound runs, not restampedv20 evidence.

Use the same launch/test commands with `--source=/home/astra/projects/sprite-construction-lab/pilot/space-marine-captain/assembled-v12`, and the material command with dense-v22 plus assembled-v12. Resource and actual screenshots: `/home/astra/artifacts/captain72-v12-engine-v1/`. Raw1440-context material record and actor screenshots: `/home/astra/artifacts/captain72-v12-material-gpu-v1/`. Current receipt/summary and renderedlab screenshot are committed in `proof/`; independent artdecision and later technical followup are separately bound under `pilot/captain-review/`.

The visual correction is explicit and physicsroot stays continuous. Isolatedwholeboot stability does not certify every hidden actor material pixel, heel/toe forces, terraincollision or everycontinuousinstant. No otherdirection/action approval or otherreviewer verdict is implied. Historicalfailed candidates and receipts remain unchanged.

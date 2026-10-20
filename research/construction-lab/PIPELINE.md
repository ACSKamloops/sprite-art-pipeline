# Repeatable sprite construction and refinement

This workbench supplies precise construction/editing tools and a real-game control. The current cutout character and localized AI knee candidate are **changes requested**, not finished art. The engine/editor evidence approves mechanics only.

The current [game-method learning system](learning/README.md) connects source bytes, executed methods, selected poses and independently decoded displayed pixels. Its controlled Sword intervention is independently reviewed; the broader case roster and family coverage remain partial. Read [current family/quality gates](qc/coverage/README.md), [clock tests](qc/engine/README.md) and [whole-timeline contact comparisons](qc/pixel_motion/dense_pilot/README.md).

## Work in stages

|Stage|Inputs and repeatable operation|Verification before progressing|Failure and retained evidence|
|---|---|---|---|
|1. Freeze the target|Design/reference images; intended game-scale canvas; actor/equipment/view/action list; contact phases, pose landmarks and material regions; palette/style and motion brief|Reference hash ledger; distinguish missing views, anatomy and hidden surfaces from observed facts|Missing poses remain missing; generation does not establish faithful reproduction|
|2. Discover a control|Decode source tables and capture consecutive emulator frames with inputs, clocks, OAM/VRAM/CGRAM/WRAM|Independent raw-data renderer; source bytes/coordinates/order/palette; real presentation delay and action transitions|Wrong flip/order/frame/hold/clock/event/pivot must fail; see native/audit-report.json|
|3. Construct editable art|Draw or select reference-informed key poses; separate real body/equipment layers; place sources explicitly in sprite-construction-spec/v1; run sprite_construct.py|Exact source RGBA, anchors, layer order, stable shared cel IDs; reject visible clipping/implicit resizing|Native OAM slots are hardware slots, not anatomical rig parts; fused pictures cannot yield trustworthy hidden anatomy|
|4. Build motion|Authored pose schedule or articulated 2D/3D rig; fixed world/render anchors, positive holds, explicit events|All action/view variants represented; complete loop/recovery; actual rendered attachment/contact pixels, not only IK targets|Keep old rig/spec, pixels and failed proof; correct the source anchor/art/pose responsible|
|5. Fine edit|Pencil, eraser, region-mask recolor, palette, cel/layer translation; expected-project hash and explicit reason|Atomic rejection, changed coordinates, outside-region and other-frame invariants; undo/replay before save|Stale preconditions reject; shared-cel edits affect all bindings and are reported; palette edits can affect many layers|
|6. Evaluate generated candidates|Saved prompt/reference/master/model receipt; explicit registration if needed; source-defined mask; candidate_patch transaction|Dimensions, transparency/silhouette, outside-mask exactness, material/anatomy and adjacent-pose review|Whole-frame AI edit changed 3,002 outside pixels; localized 341-pixel patch preserved mechanics but failed art review|
|7. Exchange and engine test|Editable JSON, ordered layers, PNG/atlas/manifests; ASE+sidecar or supported ORA; real Godot SpriteFrames|External LibreSprite save/reopen and exact renders; Godot resource reload, actual GPU output, loop and one-shot completion|Tool milliseconds are a quantized preview; original tick clock remains in sidecar. Reject unsupported external timing/structure changes|
|8. Visual review and repair|Current hashes, references, 1x/2x contact sheets, timed playback, movement/attack/interruption in game|Silhouette/identity/material boundaries; seams; feet/attachments; anticipation, contact and recovery; consistent scale|Reviewer lists exact clips/frames and defects. Passing mechanics cannot set approved. Changed assets invalidate the review|
|9. Deliver/reuse|Editable sources, spec, transactions/history, rejected attempts, exports, source/evidence ledger, installed skill|Fresh independent forward use; all handoff hashes current; documented unresolved conditions|Source discovery, file correctness, engine behavior, native fidelity and art acceptance have distinct status|

## Use the tools

Requires Python 3 and Pillow; a modern RGBA palette is supported with no 16-bit/16-color restriction. Run from this folder. Serve locally with `python3 -m http.server 8140 --bind 127.0.0.1`, then open `http://127.0.0.1:8140/editor/?project=../study/layered-cutout/project.json`. Open other project JSONs with the file picker. The tool has pencil/eraser, an explicit region mask, recoloring, layer/frame/palette selection, onion skins, diff/guides, undo/redo, saved journals and clock-based playback. Saves download a separate file; the source stays available.

```sh
python3 scripts/sprite_construct.py examples/construction/spec.json output/new-project.json
python3 scripts/sprite_edit.py validate output/new-project.json
python3 scripts/sprite_edit.py apply source.json edit.json --output edited.json --receipt receipt.json
python3 scripts/sprite_edit.py replay source.json journal.json replayed.json
python3 scripts/sprite_edit.py export edited.json exports
python3 scripts/sprite_edit.py ase-export edited.json edit.aseprite --animation walk
libresprite -b --list-layers edit.aseprite --save-as saved.aseprite --sheet tool.png --sheet-type horizontal
python3 scripts/sprite_edit.py ase-import saved.aseprite reopened.json --sidecar edit.aseprite.sprite-lab.json
python3 -m unittest discover -s tests -v
```

Create the output directory before using the constructor. [Precise editing contract](docs/editing-contract.md) defines operation fields, shared-cel/global-palette scope, hashes, timing and tool limits. [CONTRACT.md](CONTRACT.md) defines editable sources; [examples/construction/spec.json](examples/construction/spec.json) demonstrates layered placements and shared cels. These calibration blocks demonstrate construction, not finished game art.

Edits in rendered cels are explicit downstream overrides. Upstream texture/rig repairs should be rerendered and produce a new project hash; old journals must reject that changed base. Keep source-part pixels/anchors/transforms and downstream journals separately so regeneration cannot silently erase a repair. Repeated use should apply a source-art repair or explicitly rebase reviewed per-pose overrides.

## Reproduce the measured studies

```sh
python3 native/audit.py
python3 native/check_core.py
python3 native/check_exchange.py
python3 study/prepare_ai_candidate.py
godot --headless --editor --path study/layered-cutout --import
xvfb-run -a godot --audio-driver Dummy --path study/layered-cutout --script res://render_layers.gd
python3 study/build_layered_project.py
python3 study/prepare_godot.py
godot --headless --editor --path godot --import
xvfb-run -a godot --audio-driver Dummy --path godot --script res://check_import.gd
python3 study/check_godot_pixels.py
```

The independent native benchmark can run without the ROM. Native-rule script-byte verification and fresh captures require the private local ROM/core/checkpoint identified by hashes in native/sources.json and study/capture_native_calibration.py; see [native/README.md](native/README.md). No ROM is in this package. The capture setup is controlled native equipment preparation, not a claim of natural progression.

The native normal Sword selects three five-tick poses and completes after B release. Presentation lags WRAM selection by one tick. The near Sword capture records an actual enemy HP transition; it does not establish a general collision active interval. The captured walking cycle is at a collision boundary, so it cannot prove unobstructed world locomotion. Our authored 60fps/one-second walk is intentionally separate from native 60.098811862fps/six-five-tick walking holds.

The layered cutout study freezes eleven part PNGs and transforms; its 24 composites match actual Godot part renders. Measuring the boot layer exposed a one-pixel rear-foot ground gap that target-only IK checks missed. `construction-proof-before.json` retains the failure. The repaired source anchor is now y=2; the independent review checks actual sole pixels and marks remaining anatomy/choreography issues. Before-foot images cover the rear boot only; they do not prove historical invariance of all other layers.

Its earlier planted-world stance checks sample pose boundaries only. Whole-held-timeline tests reveal4pixel sliding; the denser60frame pilot improves actual raster sliding to1pixel, still failing its unchanged0.5pixel threshold. Continuously evaluated rig placement measures0pixels in the same sampled readbacks. Keep these motion findings separate from ground-contact, source-pixel and art-quality acceptance.

The AI experiment used built-in image_gen, **not Google Imagen**. Its changed canvas and geometry were recorded; an explicitly described global candidate registration and source-silhouette mask made the patch mechanically local, but the reviewer rejected pink material leakage and a weakened knee bend cue. A mechanical mask cannot make a generated pose anatomically correct.

## Parallel jobs and review records

Use one checkout/worktree/output directory per worker. With the installed sprite-animation-pipeline skill, the tested SQLite queue supports `claim-next`, lease heartbeat, stage receipts and revision. Freeze a source brief hash before output exists. Promote queued → authored → artifact_validated → engine_tested → visual_review using evidence from the applicable stages above. A rejected art review stays in visual_review/revision; never autoapprove from scores. The queue's approved stage additionally requires its portable animation manifest and explicit current clip coverage in an approved review. Read its references/review-and-queue.md before advancing jobs.

For this lab, review records bind `project_canonical_sha256` and all inspected PNG/rig/source hashes and state exact clip coverage. Native derived controls and authored projects retain their own scope. The two current authored clips are still changes_requested. Missing original design approval, polished hand-drawn joint transitions, extra directions/actions and in-game interruption tests remain future art/game work, not completed by this editor demonstration.

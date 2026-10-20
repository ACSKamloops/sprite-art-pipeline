# Reusable parts → motion → verified baked sprites

The commands and numerical contact evidence below describe the retained V1 two-view baseline. For the V2 authored depth views, reusable source paint and complete-clip editor, read [source-paint-and-clip-editing.md](source-paint-and-clip-editing.md); final pack and gameplay evidence is recorded separately from this historical baseline.

Use this route when a project needs reproducible animation without independent AI redraws. A 3D model is optional; this bundled example is an original 2D contour rig. Freeze reference/master hashes, native canvas and scale, supported views, materials, draw order, anchors, equipment, action matrix, contact/root/camera policy and events. A flattened reference lacks concealed anatomy; paint and review overlapping hidden parts and missing views before rigging.

## Choose a deformation route

Rigid parts work for weapons, armor and head pieces. Fabric and joint bends need contour deformation or weighted skinning; extreme silhouette changes need replacement drawings. The example uses two-bone IK and continuous polygon strips, **not** Skeleton2D skinning. Its right view is authored; left is a mirror. It does not supply top-down front/back views or a universal animal rig. Use AI for a master design, part candidates and masked corrections, retain prompt/model/references/raw candidates, then review material/anatomy preservation separately from pixel-mask preservation.

## Run the self-contained example

Copy `assets/toolkit` to a new Linux work folder. Requirements: Python3 + Pillow, Godot4.7.2 as `godot`, Xvfb and `xvfb-run` for real offscreen graphics, optionally LibreSprite and Chromium/Playwright for external editor tests. The recorded renderer was OpenGL llvmpipe; software rendering still exercises actual graphics. Do not treat headless import as a graphics result.

From the copied toolkit:

```sh
python3 -m unittest discover -s pilot/tools -p 'test_*.py' -v
python3 pilot/rigged-character/build_exports.py --private-output /absolute/fresh/bake --duplicate
xvfb-run -a godot --path pilot/rigged-character --rendering-method gl_compatibility --audio-driver Dummy --script test_runtime.gd
xvfb-run -a godot --path pilot/rigged-character --rendering-method gl_compatibility --audio-driver Dummy --script test_moving_world.gd
xvfb-run -a godot --path pilot/rigged-character --rendering-method gl_compatibility --audio-driver Dummy --script test_lab_effects.gd
python3 pilot/tools/build_editable_sample.py pilot/rigged-character --output /absolute/fresh/editable-sample
godot --path pilot/rigged-character
python3 -m http.server 8140 --bind 127.0.0.1
```

Load editable-sample/project.json into `/editor/`. The bridge constructs five representative 12-layer poses, independently reconstructs their GPU composites, and demonstrates a visible two-pixel masked candidate with exact undo/replay. These are five single-pose editing samples, not the complete animation library. The bridge does not propagate paint onto the deforming source rig. `pilot/tools/apply_baked_edit.py` maps a replay-verified journal to one explicit non-locomotion pose/view/tick in a fresh standalone candidate: PNG, atlas region, manifest and SpriteFrames are updated, all exports are checked, and old proof/review/isolation receipts are omitted. `pilot/tools/test_baked_edit.gd` verifies actual GPU playback equals the edited composite. Pixel-only metadata is enforced; changed timing/layers, stale inputs, locomotion edits and cumulative overrides reject. Locomotion painting requires new contact-cache measurement. The live original intentionally differs at edited pixels; use the dedicated candidate oracle, then perform fresh temporal art review.

```sh
python3 pilot/tools/verify_editor_exchange.py /path/sample/project.json --output /absolute/fresh/exchange
python3 pilot/tools/apply_baked_edit.py pilot/rigged-character /path/sample/project.json /path/sample/fine-edited-project.json /path/sample/fine-edit-journal.json --frame idle-0 --binding idle/right --tick 0 --output /absolute/fresh/candidate
xvfb-run -a godot --path /absolute/fresh/candidate --editor --import --rendering-method gl_compatibility
xvfb-run -a godot --path /absolute/fresh/candidate --script /absolute/copied/toolkit/pilot/tools/test_baked_edit.gd --rendering-method gl_compatibility --audio-driver Dummy
```

The source initializer is optional bootstrap code; do not overwrite edited design/clip JSON with forced initialization. The baker saves the previous generated folder privately before replacing its own derived output. Private output directories must be fresh. Generated files and proof dumps are intentionally omitted from the skill; the template renders them locally.

## Fine-edit the source or baked pixels

Use `pilot/tools/edit_rig_source.py apply source.json edit.json --output candidate.json --receipt receipt.json`, then `undo candidate.json receipt.json --output restored.json`. Edits require exact source SHA, reason, existing path, before/value and permitted geometry/material/track fields; receipts preserve original bytes. Approval metadata cannot be patched. This helper validates the bundled 192 px biped schema; adapt its validator explicitly for another resolution/species.

Keep source edits and cel journals separate. A changed source invalidates bakes, isolation snapshots, project hashes and dependent receipts/reviews. Re-render and explicitly rebase a downstream correction; never silently replay stale edits. The pixel editor also checks cel hashes/masks and rejects stale transactions. Validate visible final composites: a changed cel covered by a higher layer can look unchanged.

ASE/ORA tool exchange requires sidecars. Test actual external save/reopen and final pixels. Avoid printing entire multi-megabyte project/sidecar JSON into agent context; call the Python API or redirect command output to a file.

## Animation and contact verification

Encode anticipation, extension/contact, follow-through, recovery and interruption. Use one clock for body and event delivery. Loop samples use tick/N; one-shots use tick/(N−1), hold the endpoint for the final tick and complete at N. No per-pose recentering. GIF timing is quantized preview only.

The moving-world example distinguishes physical and visual roots. Continuous live walk/run passes contact checks; holding baked frames at a continuously moving root slips by 2 px. Generic floor/round/ceil snapping still fails. `foot_contact.gd` translates the **whole sprite** from actual cached held sole pixels to the continuous stance position, leaving physics unchanged. Right/fixed-camera/native-1x/two-cycle fractional-sample proof reaches 0 px sole drift. A -9 px sole offset, boundary170/opaque row169 and small integer-boundary numerical epsilon are explicit conventions, not transferable anatomical constants. Cache source/policy/all96 locomotion pixel hashes reject stale bindings. In a fresh isolated source copy, regenerate measurement with `xvfb-run -a godot --path pilot/rigged-character --script foot_contact.gd --rendering-method gl_compatibility --audio-driver Dummy`, then the same command with `--script contact-proof/contact_lock.gd`, then `python3 pilot/rigged-character/contact-proof/build_cache.py`. Back up prior contact-proof files first; these runners write their own derived proof folder. The packaged builder omits only the original study's optional historical cross-revision comparison. The current example retains explicit60/36tick,24/40px stride assumptions; adapt and validate these, sole dimensions and resolution together for a different gait. Left world motion, moving cameras, arbitrary scale and collision remain unverified.

Effects are independent authored visual objects at event-time attachment anchors; their ages use the same clock. Reset/replay clears tokens, pause freezes age, low-rate delivery respects original birth time. The optional checkbox defaults off for body RGBA comparisons. Bolts/rings do not implement combat collision or damage.

## Evidence and stopping points

Validate source freshness, action/view matrix, fixed canvas, alpha/clipping/floor, order/holds, loop/one-shot boundaries, pause/replay/speed, low-rate events, exact SpriteFrames save/reload and actual GPU rig-versus-bake pixels. Exercise deliberate stale source/cache, changed duration, reversed region and duplicate-event failures. Test actual soles during contact, both feet/handoffs/flight/recovery and fractional held-frame intervals. IK endpoints and alpha connectedness cannot establish art quality.

An independent reviewer must view affected native-scale/2x poses and correctly timed motion. Bind the receipt to source/export hashes and explicit covered clip/view samples. First-five repairs and grounded falling were accepted as bounded prototypes; full-pack review has its own receipt. Engineering passes never imply production-art acceptance or all-game coverage. Preserve rejected attempts. Deliver a local source/editable/export/proof folder and coverage gaps. Hosting is optional and requires a separately requested stage.

# Current four-view extension

The current source is `rigged-character-v2`, with 96 bindings/6,000 held frames. Follow [HANDOFF.md](HANDOFF.md) for current source hashes, actual review coverage, proof paths and launch commands. The repeatable four-view build/cache/fine-edit procedure is also packaged in `../skills/sprite-construction-editing/references/four-view-workflow.md`. The original two-view baseline below is retained as the historical foundation; its 24-binding counts and proof paths do not describe the current pack.

# Local rig, sprite bake and refinement workflow

This is an original modern vector-art animation pilot. Its authoritative inputs are named reusable shapes, material colors, anchors, limb dimensions and pose tracks. It does not require a 3D model. The character has an authored right view and an explicitly mirrored left view; front/back and independently authored handedness are unsupported. Source or engineering checks do not grant artistic approval.

## 1. Decide what is being built

Freeze the character design and style references, native game scale, supported directions, equipment, contact/root policy, action matrix and event semantics. A reference image is needed for faithful adaptation of an existing design. Complete concealed elbow/shoulder/hip regions and missing views before splitting that image; a single flattened image does not contain them. Our original vector pilot defines its own geometry instead of pretending to recover hidden anatomy.

Use AI for design proposals, missing part candidates, pose suggestions and carefully masked detail repairs. Keep the same approved identity reference, camera/view and palette/material brief. Preserve prompt, model/tool, inputs and raw output. Do not use a fresh unconditioned AI drawing for every frame. Research dated August/September 2026 and the actually exercised Sprite Studio renderer are in [the research folder](../research/ai-sprite-workflows-2026/README.md) and [renderer comparison](../research/sprite-studio-probe/README.md). Older papers remain labelled as older foundations; vendor demonstrations remain unverified quality claims.

## 2. Build an editable source rig

`rigged-character/design.json` stores reusable rigid polygons for hood/head, tunic, scarf, shoulder armor, boots, hands and equipment; it also stores limb widths, lengths and joint anchors. `rig.gd` evaluates a two-segment IK chain and draws continuous shaped strips along the arm/leg chain. This is authored contour deformation, **not Skeleton2D weighted skinning**. No per-frame semantic redraw is used.

Rigid parts preserve their material geometry. Deforming fabric needs sufficient contour overlap and a supported bend range; extreme views or bends may need a replacement drawing. Clip textures, z-order, attachments and effects belong to explicit named draw layers. Inspect actual poses rather than trusting the IK endpoint. The existing rejected textured cutout and the recent upstream extreme-fold test demonstrate why that distinction matters.

`author_data.py` initializes the example sources. It is not the routine build command; preserve edited JSON and do not force a fresh initialization over it.

## 3. Author the motion

`clips.json` defines 60 Hz durations, loops, equipment, keyframe tracks, gait settings and named visual events. The pilot has idle, walk, run, slash, thrust, shoot, charge, cast, hurt, knockdown, recover and celebrate. Semantic events such as `strike_pose` or projectile release are authored hooks, not measured Secret of Mana collision windows. The separate [measured ROM reference](motion-reference/README.md) supplies displayed hold times and verified selection/presentation distinctions; it does not supply a proven collision interval or unrestricted walk speed.

Use readable anticipation, contact/extension, follow-through and recovery. Locomotion needs support, passing and reach poses with opposing arm swing; declared contact phases and world root motion must be checked together. A rig at a fixed local origin and a foot target cannot establish absence of sliding in a moving game world. Keep the existing half-pixel motion gate; don't loosen it to make a new bake pass.

## 4. Render and export

From `rigged-character`, run `python3 build_exports.py --private-output /absolute/fresh/output-directory --duplicate`. A fresh directory preserves earlier candidates. The runner imports the project, uses a real Godot graphics renderer, waits for the viewport draw and snapshots each authored tick. It records source hashes, renderer, fixed canvas and sampling policy. Source-only headless import is a compile check, not a render result.

Loop samples use tick/N; one-shots use tick/(N-1), include the endpoint, hold that final pose for its final tick and complete at N. Each clip/view exports transparent frames, a bounded atlas and a real `SpriteFrames` resource. The manifest carries duration, loop, event and region data. No per-pose recentering is permitted. GIF review copies use cumulative 10 ms quantization; engine ticks remain authoritative.

Actual isolated draw-layer snapshots provide a small editable review sample. They are full-canvas transparent layers of representative poses, not automatic anatomical segmentation and not every frame of the animation set.

### Moving-world contact policy

The measured right-view walk/run test uses continuous physical displacement and a fixed camera. The continuous rig passes the half-pixel gate; a one-tick held sprite with the same physical root slips by two pixels. Generic floor/round/ceil snapping also fails. Do not hide that baseline.

`foot_contact.gd.contact_draw_root` compensates the **whole rendered sprite**, using its measured held-frame sole minimum and the continuous stance-foot position. The physical root stays unchanged. The policy uses an explicit -9 px sole offset, row-169 floor contact (boundary 170), a small numerical integer-boundary epsilon and front/rear contact declarations. Never correct boots independently. Actual GPU samples cover both feet, handoffs, flight and two complete loops; corrected sole drift is zero in that bounded test. Camera movement, left-view world locomotion, arbitrary scales, collision and locomotion blending remain unverified. The cache binds source hashes, policy hash and all 96 whole walk/run raster hashes; changed inputs require new measurements.

Use the local **World motion test** controls to compare live root, uncorrected baked root and corrected visual root. Its compensation is a visual child offset, not a change to gameplay velocity. The integer draw cadence and its visual smoothness still need review in each intended game scale.

### Effects are separate authored visuals

The lab's Effects checkbox defaults off so body comparisons stay meaningful. `effects.gd` owns muzzle flash, bolt, charge pulse/burst and cast ring lifetimes; all use the lab's shared 60 Hz clock and original event-time attachment anchors. Reset clears old effects/tokens; pause freezes age; dropped frame delivery preserves original birth time instead of spawning a fresh ghost projectile. Independent GPU tests and actual lab consumer tests verify those behaviors in right and mirrored left views. This is visual playback, not damage/collision or a combat system.

## 5. Make a source correction

Use `tools/edit_rig_source.py` for a palette, polygon vertex, joint/limb parameter or pose-track correction. The edit JSON declares `schema: rig-source-edit/v1`, exact `expected_sha256`, a reason and `operations` containing `op: set`, an existing JSON `path` array, `before` and `value`. Arbitrary approval metadata cannot be edited through this interface. Invalid edits fail before writing a new source; the receipt retains exact original bytes.

```sh
python3 pilot/tools/edit_rig_source.py apply pilot/rigged-character/design.json edit.json --output design-candidate.json --receipt source-receipt.json
python3 pilot/tools/edit_rig_source.py undo design-candidate.json source-receipt.json --output design-restored.json
```

Review and promote the source candidate before rebaking. A changed source invalidates the old bake, editable project and dependent pixel-edit journal. Preserve them as the previous candidate; never silently transfer an old review or patch to the new source. Run `python3 -m unittest discover -s pilot/tools -p 'test_*.py' -v` after integrating the pilot sources.

## 6. Make a fine pixel correction

```sh
python3 pilot/tools/build_editable_sample.py pilot/rigged-character --output /absolute/fresh/editable-sample
```

The bridge checks every isolated-source binding and PNG RGBA hash, copies portable inputs, constructs an editable layer stack and independently reconstructs the complete GPU poses. Its two-pixel material candidate proves exact mask preservation, undo and replay; it remains unapproved art. Load the resulting `project.json` in the existing `editor/` for pencil, eraser, masks, palette, onion skins and layer-specific corrections. Record an expected project hash and cel hash for AI patches; exact outside-mask preservation is necessary but does not establish correct anatomy or materials.

For external editing, use the existing ASE/ORA export-import commands in `scripts/sprite_edit.py` and retain their sidecars. Check actual editor save/reopen and pixels, not just whether a file was emitted. A downstream correction is tied to the clip/view/tick, source and project hashes; importing it into gameplay requires rebuilding the affected atlas/resource and a fresh runtime check. The sample bridge does not apply a correction to every animation or propagate paint onto the deforming source rig. For an explicitly selected non-locomotion sample, `tools/apply_baked_edit.py` projects a replay-verified pixel journal into a fresh standalone Godot candidate project, changes its PNG and atlas region, rebuilds the resource/manifest, checks every export and discards old proof/review/isolation receipts. The current tested example changes exactly two visible pixels in idle/right tick0 while retaining 1,535 other frames. `tools/test_baked_edit.gd` checks actual AnimatedSprite2D GPU pixels against the edited composite and verifies that the original live rig differs only at those coordinates. This candidate is unapproved art; the original rig-versus-bake oracle intentionally differs at the overridden tick.

```sh
python3 pilot/tools/apply_baked_edit.py pilot/rigged-character /path/sample/project.json /path/sample/fine-edited-project.json /path/sample/fine-edit-journal.json --frame idle-0 --binding idle/right --tick 0 --output /absolute/fresh/candidate-project
xvfb-run -a godot --path /absolute/fresh/candidate-project --editor --import --rendering-method gl_compatibility
xvfb-run -a godot --path /absolute/fresh/candidate-project --script /absolute/path/pilot/tools/test_baked_edit.gd --rendering-method gl_compatibility --audio-driver Dummy
```

Only pixel/palette edits are supported by this adapter; timing/layer changes, locomotion overrides and cumulative override projects reject. A walk/run repaint requires new measured sole/contact evidence. Each visible frame/view correction needs its own explicit mapping and fresh temporal art review; do not automatically mirror or propagate a paint correction.

## 7. Verify and review

Technical gates: source freshness, expected action/view matrix, fixed canvas, alpha/clipping, frame order and holds, complete loop/recovery, clock boundaries, event delivery under dropped frames, saved/reloaded engine resources, actual GPU rig-versus-bake pixels, and repeated renders within the declared renderer. Use deliberate failures (stale source, changed duration, duplicate events, reversed regions) to show that the gates reject broken output.

Motion gates: grounded knockdown/recovery support and no opaque pixels below the declared floor; actual sole and grip pixels throughout their contact intervals, including held frames, fractional clock samples, moving root/camera, loop wrap and transition boundaries. Report continuous live rig and held baked frames separately. Frame counts, bone endpoints or alpha-connectedness alone cannot pass this gate.

Art gates: view native 1x/2x frames, adjacent poses and correctly timed playback; check identity, material flow, silhouette, joints, anatomy, equipment grip, pose weight and action readability. Independent review records exact covered clip/view/source/export hashes and defects. Fix failures upstream when they recur across frames. Preserve failed candidates and rerun the affected checks/review after repair. Keep technical acceptance, artistic acceptance and full content coverage separate.

All work stays local. Site publishing is deferred until the pipeline is functional and the user resumes that part of the work.

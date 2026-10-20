# Reusable painting and complete editable clips

Choose the source edit when a detail should follow the character through motion. Choose a baked cel edit for an intentional one-frame cleanup. They are different authorities: changing a rig invalidates dependent bakes, caches, editable projects and reviews; editing one cel does not infer paint on every other frame.

The bundled V2 192px contour rig has authored front/back geometry in addition to authored right and mirrored left. Its optional `paint_layers[view][part]` applies small palette-bound strokes in local coordinates on rigid torso, hood, armor and equipment surfaces. Deforming cloth seams are contour-owned details. This is not arbitrary texture UV warping or a weighted skinning tool.

```sh
python3 pilot/tools/surface_paint.py apply /path/design.json /path/patch.json --output /path/design-candidate.json --receipt /path/receipt.json
python3 pilot/tools/surface_paint.py undo /path/design-candidate.json /path/receipt.json --output /path/restored.json
```

The patch has schema `rig-surface-paint/v1`, `expected_source_sha256`, a reason and strokes `{view,layer,at:[x,y],color:palette_name,size:1..4}`. Put the candidate design beside an exact copy of the rig scripts and clips before rendering. Patches append source strokes; they do not redraw frame images. Exact undo/replay and stale/tampered receipt rejection are tested.

```sh
xvfb-run -a godot --path /path/candidate-source --rendering-method gl_compatibility --audio-driver Dummy --script /path/toolkit/pilot/tools/paint_motion_probe.gd -- /path/candidate-source /absolute/fresh/proof 8
python3 pilot/tools/check_surface_paint.py /path/proof/report.json /path/candidate-source/design.json --output /path/proof/independent-uv-check.json
```

The probe renders clean/painted full poses and isolated torso in the **same viewport origin**. A previous side-by-side two-actor capture differed by single raster-edge pixels even without a valid paint explanation; that failure remains evidence. The independent check recomputes full/isolated deltas and alpha, inverse-transforms pixel centers into local UV, checks authored include/exclude polygons and material colors, and requires every action/view/phase sample. The demonstrated 8-phase grid covers all 12 actions in 4 views. Occlusion can hide valid paint; inspect the final composite and never call a hidden edit a successful visible repair. Godot JSON numbers may be floats even when JSON writes `2`; engine-side brush validation must accept finite integral numeric values. This bug originally made every serialized brush invisible.

For a whole animation in the fine editor, isolate **one complete binding per project**. This keeps memory bounded, preserves view-specific layer order and avoids loading thousands of animation cels into one browser document.

```sh
xvfb-run -a godot --path /path/source --rendering-method gl_compatibility --audio-driver Dummy --script /path/toolkit/pilot/tools/isolate_editable_clip.gd -- /path/source walk/front /absolute/fresh/isolation
python3 pilot/tools/build_editable_clip.py /path/source /path/isolation --output /absolute/fresh/editable
python3 -m http.server 8144 --bind 127.0.0.1
```

Open `/editor/` and load `editable/project.json`. Every tick retains its duration and named layers; the builder verifies each composited frame exactly equals the real GPU/baked PNG. Keep the source's explicit planar ground convention for depth views; a guide at y170 is not a universal horizontal floor. Equipped bindings retain their base action and persistent selection. The old five-pose bridge is still useful for small editing examples; it is not the complete-clip bridge.

Browser verification waits for a synchronous loaded-document predicate, then explicitly awaits/checks the expected project hash. An asynchronous polling predicate raced a larger file load and selected the calibration document. Test actual visible masked edit, exact canvas, stale rejection, undo/redo and the intended frame count before trusting a load receipt. Use ASE/ORA exchange sidecars for external tools. Source-paint candidates still need a fresh bake/contact cache and adversarial visual review before promotion.

Keep original manifest bytes as the authority. Godot JSON numeric parse/stringify changed tiny angles by about 1e-17; do not duplicate a complete float-heavy clip and expect a byte-exact numeric round trip. The v2 isolation header records only clip name, base clip, explicit gear, view, duration, loop and events, plus the original manifest byte hash. Actual GPU pixels must still exactly match every held baked frame. Validate the full editable project once, then render its requested frames in a bounded batch; revalidating all cel pixels before each frame makes complete-clip verification unnecessarily quadratic. Browser loads must reset the old document and await the intended project hash.

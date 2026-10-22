# Source-pixel bridges and fine edits

## Keep a rigid distal shape and a connected proximal surface

Use this only when source/destination views and nearby key poses are compatible. The complete donor arm must contain the required visible paint. A source-coordinate map can reuse texels; it cannot reveal hidden anatomy, rotate lighting realistically through a new view, or invent a missing opposing gait pose.

Choose a **body context** and **complete limb donor** separately. Fix the shoulder/body boundary. Place dense source/target controls over the full glove rectangle with the same integer translation; this creates a rigid plateau, protecting knuckles and shape. Intermediate elbow/bracer controls deform the connected proximal surface. Fixed canvas boundary controls keep the map covered. A whole-arm affine had flattened the fist in the earlier test; fragment rotations had exposed gaps.

For each triangle, use its source controls S and target controls T. At an output pixel q inside a target triangle, compute barycentric coordinates in T, map them to S, then sample the nearest source pixel with `floor(value+0.5)`. Reject collapsed/folded triangles and uncovered outputs. Freeze the actual triangle indices and integer source map for replay; triangulation ties or library versions can otherwise change a later rebake.

Body-owned output pixels copy body context at identity coordinates. Donor-owned pixels sample the complete donor, including transparent pixels that erase its old location. Record both ownership and source coordinates. A positive triangle, exact glove and connected alpha are mechanical checks; proximal cuff volume still needs art review.

## Standalone helper and proven fixture

Requirements: Python3, Pillow, NumPy; SciPy is needed only to create triangles when the spec does not already supply them. No model or API credential is used. The three bundled specs use two explicit control geometries and frozen source hashes.

From this skill folder:

```bash
python3 scripts/source_warp.py replay assets/source-hand-fixture/extension.json
python3 scripts/source_warp.py replay assets/source-hand-fixture/recoil.json
python3 scripts/source_warp.py replay assets/source-hand-fixture/recoil-finished.json
python3 scripts/source_warp.py bake assets/source-hand-fixture/extension.json /tmp/my-fresh-extension
python3 scripts/source_warp.py bake assets/source-hand-fixture/recoil-finished.json /tmp/my-fresh-finished-recoil
```

`replay` checks the frozen map against the retained expected RGBA and rigid glove rectangle without writing. `bake` reconstructs from explicit controls/triangles, compares to the expected result when supplied, and writes PNG, map and receipt into a fresh directory. Neither command mutates the fixture. Use a new output path for another run. The optional `pixel_edits` list copies literal `source_at` swatches from the unedited mapped cel into unique `at` destinations inside the donor ROI. The finished recoil spec contains all18 actual cuff edits and reproduces the selected final cel. Its receipt is a map/edit receipt, not a substitute for the companion's full layered project journal.

For another character, create a new spec with its actual input paths/hashes, canvas, donor-owned ROI, source/target control points and rigid-translation rectangles. Do not reuse the example's192px canvas, coordinates or mask as production defaults. `source_points[i]` and `target_points[i]` describe the same control; optional `triangles` freezes their connectivity. Rectangle bounds are integer `[left,top,right,bottom]`, right/bottom exclusive, and coordinates address pixel centers. A new spec can omit expected/map until producing the first reviewed map.

The additional80px `assets/source-settle-fixture/settle.json` replays a complete
source-owned upper-body settle with the entire lower body preserved from row53.
Only the waist band deforms. It is a **provisional art study**: an earlier
leg-deforming version had knee/cuff costs despite exact boot rectangles. A fresh
review narrowly preferred this lower-protected version, overall7.2 in that
packet. It demonstrates replay and a bounded preference, not an accepted finish.
Read its provenance and the [authored-motion case](authored-motion-guides.md).

```bash
python3 scripts/source_warp.py replay assets/source-settle-fixture/settle.json
python3 scripts/source_warp.py bake assets/source-settle-fixture/settle.json /tmp/my-fresh-settle
```

The frozen map and rebake both reproduce the expected RGBA and complete rigid
upper. The receipt's `actual_changed_RGBA_pixels` counts only optional downstream
pixel edits, not the warp's moved pixels. A zero there does not mean no movement.

## Literal, reversible pixel repairs

When the user asks for manual or programmatic refinement, keep source-owned layers/cels and use the construction companion's real `History`, `candidate_transaction`, palette and paint/erase operations. Do not invent an editor API. A masked import must first prove the candidate cel is identical outside the declared region.

For an exposure inserted between old keys, clone its body and limb cels before editing so shared original cels stay intact. Give the replacement ROI to the limb and clear the underlying body only there; preserve both layers outside it. Otherwise the renderer may blend against stale underlying paint.

A literal source-colored touch-up can use the companion toolkit like this:

```python
from sprite_lab import project_hash
from sprite_lab.history import History

# p, cel_id, x, y and color_index are measured from the current project.
h = History(p)
h.apply({
    'schema': 'sprite-edit-transaction/v1',
    'expected_project_sha256': project_hash(p),
    'reason': 'Describe the observed defect and this bounded repair',
    'operations': [{'op': 'paint', 'cel_id': cel_id,
                    'mask': [[x,y]], 'points': [[x,y,color_index]]}]
})
journal = h.journal()
assert project_hash(History.replay(p,journal).project) == project_hash(h.project)
```

Also verify actual changedRGBA pixels, outside-mask equality, undo and redo. Preserve the initial project alongside the journal. Changed upstream paint, source maps, palette or metadata changes preconditions: create a fresh downstream initial project instead of forcing a stale journal to apply.

Use source swatches and shaded contour rows where possible. A bright flat buckle repaint had lost the source's depth. The selected cuff finish used10 then8 literal source-colored pixels; it improved local material balance without moving the glove/path. Do not infer that18 pixels or a particular color is appropriate for another defect.

For interactive work, the actual fine editor supports onion skins, masks, pencil/eraser, diff, undo/replay and project export. The tested pipeline also used real LibreSprite batch save/reopen with a native timing sidecar. A browser-memory test stroke must be clearly labeled, fully undone and kept separate from production edits. Use the companion's current documented commands rather than treating a saved ASE or journal alone as proof an external editor ran.

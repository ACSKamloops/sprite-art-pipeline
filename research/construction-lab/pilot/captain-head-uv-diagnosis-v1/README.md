# Read-only head pixel → face → source UV diagnosis

**A persistent head repair must address multiple UV regions, not just the obvious frontal portrait island.** The front texture already contains a well-defined red mechanical lens and metal rim. Visible near-side eye/temple pixels in sources33/103 instead sample a separate, softer side-profile region. Hair and portions of the forehead sample a third projection. Strengthening only the front lens is therefore an incomplete repair proposal.

Input frozen camera12/ortho2.7 packed source SHA256 **9d9e2387496e4b46d148da7e274d080cc09d90714c6a034946f53609d52ef84c**. Three actual unsaved native384 renders: source1/33/103 (cels0/16/51). Fixed source camera, geometry, pose, materials, lights, packed images and render settings retained; CPU6. These are bounded pose diagnostics, not an animation review or V8 score. No source blend or texture was saved/edited.

## Mapping evidence

For each rendered pixel centre in ROI(168,76,212,124), cast the orthographic camera primary ray into the evaluated scene, retain CaptainArticulatedBody hits rigidly owned by head, locate its evaluated triangle, and barycentrically interpolate source UV. 4,391 visible head pixel rays were mapped across the three poses. Named-feature-rays.json contains15 manually selected visual feature proposals with screen pixel, evaluated/source polygon ID, exact source vertex IDs and weights, UV, texture texel and world-hit coordinates. The semantic point labels are visual proposals; they do not classify the entire feature outline. Annotations1–15 refer to those records.

All15 named samples have **head weight1.0 and no other vertex owner**. The body has a single ARMATURE modifier. An additional source/evaluated check confirms every polygon vertex order, polygon loop order and active UV value exactly agrees at source33. Thus polygon IDs are tied to actual original mesh faces, not inferred just from equal counts. Armature deformation changes coordinates without regenerating topology. Rays are geometric pixel-centre hits; rendered antialiasing/Linear texture sampling and lighting can mix a neighborhood, so this is not a claim that one shader output equals one texture texel.

Example traces, texture coordinates top-left origin on2048² Material_0-side-polish-UV.png:

| Source / proposed feature | Pixel | Polygon | Texture texel |
|---|---|---|---|
|1 / forehead|185,90|46234|1559,236|
|1 / cyber-eye|193,96|48861|1525,265|
|33 / cyber-eye|191,103|49535|37,1814|
|103 / cyber-eye|193,100|49535|36,1815|
|33 / temple plate|203,110|50722|105,1893|
|103 / hair|185,85|45682|1919,470|

The named ray hits sample UV neighborhoods roughly face(1490,210,1600,340), hair/forehead(1860,380,2020,530), side-eye/temple(0,1760,140,1950). These rectangles are **crop coordinates, never edit permissions**. Some contain nonhead or unoccupied texture regions, and other head regions exist outside these crops. Annotated-UV-feature-crops.png shows the distinct existing paint and ray points; annotated-source-head-crops.png shows which visible pixels were sampled.

## Proposed owned texel footprint

proposed-head-owned-edit-footprint.png is a2048² grayscale candidate mask, white allowed/black excluded. Rasterized9,709 source triangles whose every vertex is solely head weight1.0. Rasterized91,235 other/boundary triangles using the same image across CaptainArticulatedBody and the two rigid boot meshes. Their source face ownership order is retained in source-triangle-owners.json.gz; matching UV/head-flag arrays are source-uv-triangles.npz.

Head raster occupancy245,981 texels; nonhead occupancy2,229,882;1,184 occupied texels touch both classifications. This includes possible UV edge sharing/rasterization effects and does not alone establish an actual broad UV-island overlap. Subtract a two-texel expanded nonhead occupancy to guard Linear filtering and raster rounding, leaving240,497 candidate head-owned texels. All15 named samples are inside;25 of4,391 visible geometric ray samples fall outside and are excluded. Do not extend into those25 samples based on facial appearance. Do not paint whole UV rectangles or infer that all head texels form one coherent chart.

This mask is an approximate conservative raster diagnostic, not an exact continuous UV/filter proof. The edit author should restrict an explicit footprint to the white region, preserve all outside-mask bytes exactly, check actual proposed stroke neighborhoods against the triangle data, and render before/after nonhead witnesses to detect sampling leakage. Duplicate/mirrored use *within* the head is not excluded by this mask; every affected head region must still be inspected. It does not grant permission to reassign UVs/material slots or alter bone weights.

## Targeted repair implication and anatomy limit

A source-attached UV paint candidate can unify the mechanical eye/temple boundary and value hierarchy across the frontal and side charts, separate steel from skin, strengthen hairline/crest masses and reduce the broad pale hair glare. Preserve head anchors, look direction, neck, halo, packed image dimensions, UVs, topology, other body paint and animations. A per-frame screen mask cannot provide this persistent multi-pose ownership.

The source has an actual nose/jaw and scalp surface, but the rendered near-frontal profile and broad smooth blond volume remain different from the master's sharper profile/compact crest. This trace does not demonstrate a missing facial feature or recover unseen canonical head geometry. A UV edit cannot promise to change head silhouette, nose projection or scalp volume, and sharper texture does not guarantee the mechanical lens remains readable at256. If those limits survive paint, a separately scoped head-local geometry diagnosis is needed rather than inventing a stable identity from raster patches. No geometry repair is authorized or performed here.

Source-binding.json hashes the frozen input and three actual renders. All outputs are diagnostic copies in the review worktree. Scripts reproduce the read-only trace; footprint.py removes its bulky temporary float cache after exporting the packed texture for inspection (PNG is an inspection derivative, original packed image bytes remain untouched). Full frozen V8 review awaits its receipt and timed export evidence.

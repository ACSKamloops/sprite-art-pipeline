# Deterministic preparation and supplied-asset methods

These modules implement local-v1 methods. They do not emulate private neural services. Input rasters are `uint8[H,W,4]`. Pixel-space origins are `(x,y)` with x right and y down. Methods return new arrays; persistence uses the shared immutable `Store` and `save_sequence`. Publishing a head is a separate explicit compare-and-swap operation.

## Preparation

`prepare.prepare_request(adapter, images, options)` returns `arrays`, ordered `references`, binary `mask`, per-source `geometry`, ordered `operations`, and raw/PNG base64 `descriptors` with separate encoded and decoded SHA-256. With `options['store']`, it also returns raster/reference/mask IDs and an immutable preparation audit ID. The audit does not contain a credential or model call. Reference roles are explicit `style`, `subject` or `unspecified`; the method does not interpret their content.

Available profiles:

| Adapter | Hidden RGB | Encoding default | Reference max side |
|---|---|---|---|
| `local-rgba-v1` | preserve | raw | uncapped within pixel budget |
| `godot-raw-v1` | zero RGB only at alpha=0, including references | raw | uncapped within pixel budget |
| `lua-pro-reference-v1` | preserve | raw | 2048 |
| `web-rotation-reference-nearest-v1` | preserve | PNG | 1024 |

The cap/serialization conventions are source-bound. The resize sampler is a separately declared **local** left-cell nearest method: `floor(dst_index*source_size/destination_size)`. This is not an Aseprite host-resize byte-parity claim or a claim about ordinary browser style-reference smoothing. The Lua profile implements the individual max-side cap, not the caller's aggregate 5Mi pixel budget or tier/account validation. It must not stand in for the entire private caller.

Options execute in this order: requested `roi=[x,y,w,h]` crop/pad; `output_size=[w,h]` nearest resize; `pad_size=[w,h]` center pad; hidden-RGB normalization. `roi` may extend beyond the source; transparent zero fills its exterior and the original requested origin is retained. Padding rejects shrinking. The same operations transform `mask`: RGBA input uses alpha!=0; bool/scalar uint8 uses value!=0. Mask selection is independent of source pixel alpha, so explicitly selected alpha-zero pixels remain selected. `reference_limit` defaults to4 and is a local bounded slot policy; source callers have their own reachability/slot rules. References retain caller order. No bounding-box recentering occurs.

`palette_conditioner` returns distinct nonzero-alpha RGBA colors and frequencies. First-appearance ordering is local; Lua's unspecified `pairs` iteration is not reproduced. This does not quantize pixels. The exported `correction_strength` preserves Lua integer0..200→0..2, Godot widget .05..1/default .5, browser compatibility zero→.3, and an explicitly corrected browser zero-preserving adapter. `choose_unzoom` keeps Auto0, None-1 and Custom with no onchange as absent (`None`). Neither invokes the server's correction/unzoom algorithm.

`prepare_prompt` returns an inert typed local descriptor for Lua MiniMax, Lua V3 and Godot V3 source conventions. It preserves null/empty/Auto distinctions, Lua percent undoubling and nonblank whitespace edges, Godot trimming, Lua interpolation's required end frame versus Godot's optional end. Caller-provided allowed choices are validated. The returned record states `remote_transformation=unsupported`; it is not a private wire endpoint or caption implementation. Actual enhancement, captioning, generation, inpainting, background removal, correction and unzoom requests fail `UnsupportedCapability` through `prepare_request`.

## Pose

`pose.project_pose(joints, direction_degrees, tilt_degrees, profile)` accepts unique labels and finite normalized x/y/z. Missing coordinates use the source low-level defaults: Lua0 versus Godot.5. Both center about.5; yaw east0/north90 rotates x/z; tilt rotates y/z. Lua depth is `-(X*sin(a)+Z*cos(a))+Y*sin(t)`, Godot depth is `Y*sin(t)+(X*sin(a)+Z*cos(a))*cos(t)`. Lua floors `(depth+.5)*1000`; Godot truncates `depth*1000` toward zero. These formulas deliberately remain different.

Profiles are `lua-raw-v1`, `lua-ranked-v1` (ascending unique quantized depth bins1..K, equal bins share rank), `godot-raw-v1` and `godot-bridge64-v1` (x/y times64, truncate; square basis). This is point projection, not rendered anatomy. `view_tilt` distinguishes active Bridge/Lua side5/low20/high35 from Godot general side10/low25/high40.

`nearest_pose(template, reference, profile, canvas)` uses Lua's16 directions×9tilts and neck-aligned weighted **pixel** error or Godot's8directions×9tilts and weighted **normalized** error. Lua requires an explicit rectangular pixel canvas and NECK; Godot uses all shared labels. The listed-first tie rule is a declared local policy, not Lua `pairs` ordering parity. Projection helpers return unique list labels instead of overwriting duplicate dictionary keys; duplicate labels are rejected.

`project_frames` accepts a list of 3D frames. Optional Lua auto helpers in compatibility mode expose the source label-dictionary/`ipairs` consequence: direction east0, tilt-45, no matched terms. The corrected mode explicitly fits by labels through `nearest_pose`; it is named `corrected-label-lookup-local-v1`. The corrected search is a separate joint fit, not a parity claim for the old sequential auto helpers. `source_shape_compatibility` also records the Godot Bridge name/label mismatch; it never silently changes labels.

`flip_pose` supports catalog z-mirror with an exact finite limb/face swap map and Godot general x-mirror with prefix label swaps. `draw_depth_channels` preserves Lua shared ranks and Godot raw-depth ordinal plus duplicate-counter behavior, including ordinal collisions and alpha-based readback offset. It does not identify draw order with public optional camera-nearness depth or impose0..255 on raw z_index. List ordering is explicit; actual connected-bone rasterization, raster overwrite collisions and host scan lookup are not implemented by this helper.

`save_supplied_motion` persists actual supplied arrays, explicit durations, pivots, direction and optional joint lineage. Duplicate holds remain ordered. `generate_motion` raises a structured unsupported result; missing anatomy/hidden views are not generated.

## Terrain

`terrain.topology_indices(bool_grid, boundary='empty'|'wrap')` is an explicitly named local four-edge convention N1/E2/S4/W8; empty slots are-1. It is not vendor Wang/blob/connected-template ordering. `connectivity_sheet(cells, order, columns)` returns a sheet and explicit key→rect manifest. `render_map(cells, layout)` assembles supplied integer-keyed equal-size cells by exact RGBA overwrite, preserving alpha-zero RGB. Missing variants fail rather than borrowing another tile.

`reblit_regions(canvas, patches)` applies ordered supplied patches at integer origins with optional bool masks and full-region expected-byte guards. All work occurs on an unpublished copy: failure at any patch leaves the parent array unchanged. It is a deterministic replacement of supplied regions, not map-object inpainting. `save_terrain` persists supplied cells/layout and its one-frame composed sequence. `generate_tiles` is unsupported.

## UI, fonts and vocal assets

`assets.virtual_view(w,h)` derives the source512-long-axis virtual view. `layout_shapes` rescales explicit primitives by axes and radii by geometric mean, or by min-axis for the separate web example convention. Coordinates remain virtual. IDs/order are retained; snapping/clamping and preset ID lifetimes are not silently combined. There is no guessed provider virtual-to-raster transform.

`render_ui(store, pieces, canvas_size)` instead uses supplied rasters and explicit integer **pixel-space** rects, with declared local nearest stretch and ordered RGBA overwrite. This local supplied-art compositor does not infer styling or skin a geometric guide.

`build_glyph_atlas(store, glyphs, columns, gap)` consumes explicit Unicode-codepoint→raster/bearing/advance entries. Packing is local fixed-cell ordering; metrics are stored separately from alpha bounds. `rasterize_font(path, characters, size, color)` optionally uses an explicit installed font file through Pillow, records its SHA, and returns glyphs/metrics. It does not download, discover a font by style name or recreate a target-generated font. `render_text` honors bearings/advances and required coverage, with explicitly optional fallback, no implicit kerning/shaping or line wrapping. It uses local straight-alpha source-over; atlas rasters remain exact.

`save_viseme_timeline(store, text, visemes, letter_map, durations, fallback, direction)` creates one supplied frame per explicit Unicode codepoint, preserving whitespace, case, duplicate holds and rational durations. The letter mapping and clock are caller data. This is not phoneme inference, the browser's complete automatic remote timing plan, or a claim that mouths have been generated. `generate_asset` fails structured unsupported for learned assets.

## Tests and boundaries

`tests/test_methods_flows.py` covers ten discriminating local cases for the supported F03/F06/F07/F08 subsets: analytic projection/depth/rank, asymmetric fitting domains, valid18-joint compatibility/corrected wrappers, prepared ROI/mask/hiddenRGB/raw/PNG identity and widget dialects, ordered refs and immutable audits, topology/sheet/map/guarded replacement, virtual radii, supplied UI/glyph/viseme placement and explicit installed-font rasterization. Store reload and duplicate rational holds are checked. Negative cases verify missing variants/glyphs/frames, invalid shapes/masks/slots, failed expected-byte guards and unsupported learned branches. These are implementation tests, not private-service parity or visual acceptance.

Parent integration still owns F01–F11 end-to-end job/revision/export/engine flows. This commit does not claim their complete conformance, a9/10 sprite, private models, 105 prepared constructors, arbitrary target grammar or host codec affinity. Source bindings and deliberate local deviations are recorded in `METHODS-SOURCE-BINDINGS.json`.

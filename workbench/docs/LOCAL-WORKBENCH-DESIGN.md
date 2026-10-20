# Local workbench design and reconstruction boundaries

This preserves the original construction specification. The finite accessible-source gate and bounded local implementation now have separate evidence; see [COVERAGE.md](COVERAGE.md) and the latest verification receipt for implemented versus unsupported/unobserved behavior. This design document alone does not establish implementation, full-flow completion or visual acceptance.

## One workspace, shared data, versioned adapters

Build a single local project with an artifact store, job queue, immutable revision graph, raster/scene/pose/effect methods, model adapters, review packets and exporters. Its CLI and eventual editor must call the same services. Separate notebooks that create unrelated images are insufficient: importing an image, constructing owned parts, changing a pose, making a guarded pixel fix, reviewing the result and exporting for Godot must retain one traceable identity.

Every flow records the exact interface dialect. Public v2 base64 image requests, Lua per-caller raw-RGBA or encoded-image modes, Godot per-caller raw-RGBA or decoded-image modes, website factories, hosted MCP recipes and our local dialect are separate adapters. Base64 is a transport encoding and does not establish whether decoded bytes are a PNG or rawRGBA; inspected Lua callers use `image.bytes`, with skeletonV3 explicitly declaring `rgba_bytes`. Similar endpoint names do not authorize moving a mask convention, clock, frame index, reference order or default from one adapter to another. Preserve submitted values and normalized values independently. Archive legacy modes with explicit compatibility labels; do not silently normalize a source-defined mismatch into a claimed faithful reproduction.

Proposed local modules and their evidence obligations:

| Module | Concrete responsibility | Boundary |
| --- | --- | --- |
| `contracts` | Typed requests, discriminated outputs, constraints and adapter/version registry | Local types cannot be advertised as recovered private schemas. |
| `artifacts` | Immutable source bytes, decoded rasters, masks, owner maps, poses, recipes, revisions and evidence | Raw file identity, decoded RGBA identity and visible-pixel identity are distinct. |
| `acquisition` | Local files/clipboard, frame import, selected regions and explicit reference slots | Never silently flatten an animation or clear hidden RGB. |
| `prepare` | Per-adapter padding, cropping, scaling, palette/reference order, mask inversion and grid diagnostics | A client advisory detector is distinct from remote conversion/unzoom. |
| `raster` | Seven disclosed exact operation kinds, selectors and explicit local craft methods | Host crop hashes, private heuristics and protection internals remain separately unprovided. |
| `scene` | Ordered layers/nodes, parts, anchors, poses/tracks, source-preservation and underpaint | Attachments provide coordinates; they do not infer correct joint anatomy. |
| `pose` | Direction conventions, projected skeletons, template selection and animation clocks | Source-defined data-shape mismatches need a compatibility mode and a separately labeled repair. |
| `effects` | Recovered client renderer methods, palette/composition/time and explicit recipe construction |105 prepared names/settings do not supply105 recovered constructors. |
| `backends` | Explicit generation/edit/rotation/interpolation/outfit/conversion/font/tile/viseme capability adapters | Unavailable private models must return unsupported or use a named substitute. |
| `jobs` | Admission, immutable request snapshot, progress, cancellation, result ownership and stale-result guards | A source Promise/HTTP success is not durable persistence or completed generation. |
| `library` | Character states/directions, object candidates/promotion, tiles/maps, glyphs/UI and effect revisions | Preserve grouping/index/tag semantics by adapter; do not infer server ranking. |
| `review` | Exact diagnostics, ordered pairs, native/full-body views, correctly timed playback and adversarial decisions | Numeric discipline scores and successful rendering cannot award game-art9/10. |
| `export` | PNG/layered source/sheet/manifest/GIF/APNG/video/Godot adapters | Dimensions, frame order, transparency, pivot and each container clock need separate checks. |

## Artifact and coordinate contracts

Source records need file SHA256, media type, decoder/version, size, decoded frame count, frame dimensions, raw RGBA hashes, durations and loop metadata. Preserve alpha-zero RGB unless an explicitly named adapter requires normalization; record both hashes if it does. Body palette rules use a defined visible-color set and a defined alpha policy. No image-size-only or filename-only identity checks.

Indexed artwork is a separate artifact domain: retain index raster, palette snapshot/version and decode policy, rather than treating its displayedRGBA as all editable state. [The indexed-host closure](/home/astra/projects/pixellab-local-test-20261011/analysis-root/full-reconstruction/INDEXED-HOST-SOURCE-CLOSURE.md) traces a native progress/undo path that does not consume its compressedRGBA buffer when the target is indexed. This remains a design requirement: the current local Store uses RGBA, and does not implement native indexed-raster/palette undo. Exact source compatibility and a future corrected indexed method are separate modes.

A frame record contains a stable frame id, source index convention, ordered direction/view id, RGBA artifact reference, rational start/duration, body/effect layer references, pivot/anchor coordinates, tag/event references and owner provenance. Internal time uses rational ticks. Converting to native editor milliseconds, GIF centiseconds, VFX fps or engine holds is explicit and reports quantization. A loop's last-to-first edge and a one-shot's final hold are distinct.

Coordinate spaces must be named at every boundary: source pixel centers, source polygon corners, node-local positions, canvas centers, cropped-frame origin, atlas cell and engine world/anchor. Inclusive `[l,t,r,b]` raster rectangles are not half-open source-corner polygons. Store units and handedness with skeletons. Every reblit/crop/export retains its translation and source coordinate trace. Do not drop off-canvas parts merely because the review sheet was cropped tightly.

Parts are masks and owned source pixels, not just rectangular crops. Record intended exclusive owners, allowed overlap, unassigned visible pixels and each part's source coordinates. Include hidden surfaces and pose-specific redraw cels with separate authorship. The rejected Captain pilot shows why exclusive source coverage is insufficient: a stationary remainder can retain moving-arm fragments, and correct rigid rotation can still be an unconvincing action. Independent pose/direction artwork is an explicit input need when the source cannot supply it.

## Revision and policy semantics

Each revision has its parent, immutable source hashes, normalized scene/recipe, ordered changes, method versions and resulting artifacts. Branches are undo points. Revision commits are atomic under our local policy; no statement about PixelLab server atomicity follows. A failed guard returns failure evidence without changing parent arrays or publishing the candidate as accepted.

Keep trusted preservation/size/resource policy outside model-authored changes. Source bookends, protected regions, palette, clear border, intended partial alpha and body/effect membership are separate checks. Permit deliberate restyling only through an explicit job configuration captured in lineage. Keep per-check outcomes and affected coordinates; never infer acceptance from `isError:false`, a URL or an exported file.

For exact edits, validate every submitted coordinate and color even if a named selection excludes it. Build masks from current target pixels; retain initial snapshots for copy and outline geometry; apply mutations in order. A successful node-local paste can remain covered by an accumulated layer patch, so audit node raster and final composite independently. A guard binds the exact source/revision/region/domain, with our own versioned algorithm unless a target fingerprint is fully established.

## Job, model and result ownership

Our job state machine is an explicitly local design: `created → admitted → queued → running → candidate`, with named failure/cancel paths. A candidate then has independent technical and review states. Store remote/native raw states without replacing them with our terms. Rejected and technically failed candidates may be preserved as evidence but cannot be exported under an accepted-art label.

The request snapshot must be immutable. A result may update the library only if it still belongs to the admitted request/version; old requests finishing later cannot replace current output. A cancel request stops local work or quarantines a late external result, with the actual cancellation capability recorded. Retry policy distinguishes transport, validation, resource, provider and model errors. Preserve original failure responses with credentials removed.

Backend capabilities include image format, dimension limits, palette/alpha support, direction set, frame count/order, seed/control support, reference ordering, pose format, cancellation, costs and output durability. Unsupported capability requests fail explicitly before inference. A backend id includes model/weights digest when available, implementation/version, preparation adapter and sampling settings. Named PixelLab selectors are not sufficient to identify a checkpoint. H3 is deferred until the system and all preceding analyses/comparisons are ready.

## Full flows the build must support or explicitly bound

1. Import/reference acquisition → advisory diagnostics → preparation → create/convert/edit/inpaint → result placement → guarded refinement → artifact/library commit.
2. Existing sprite → partition and ownership review → hidden-surface/strong-pose authoring → directions/pose transforms → ordered animation → exact edits → technical checks → native-scale/key/adjacent/playback review → editable/Godot export.
3. Persistent character → supplied versus generated directions → state/animation grouping → independent per-direction frame clocks → tags/source reference retention → reload/export/delete contract.
4. Object creation/review → sorted candidates with exact candidate ids → selected promotion/dismissal → states/missing directions/animation expansion → library/export.
5. Tile guide/mask/projection → single/connected/Wang/sidescroller/isometric generation adapter → exact layout conversion → terrain/variant map placement → layer/export. Private8×8/8×16 and public layouts remain separate.
6. UI shapes/layout and documented font request/style controls → backend assets → glyph/atlas correspondence and retained naming → local preview/history → export. The examined target forms/request do not expose a subset selector; an explicit local glyph-coverage policy is our design, with unsupported target mapping stated. TTF download success does not establish font completeness or typography quality.
7. Source mouth/viseme preparation → vocal/letter timeline → available partial results → ordered frame plan/grid/GIF → clock verification and review. No inferred neural speech model from a local letter-to-mouth plan.
8. VFX sprite/recipe → validated layers/controls → recovered deterministic frame renderer → body/back/front composition → immutable step/revision → sheet/manifest/GIF/game pack → engine placement/playback. Preserve one-shot manifest versus looping GIF-preview differences.

REST/MCP library, job, upload, capabilities, map, sandbox/chat and agent operations belong in the same surface registry, but a local art workflow does not need to pretend it implements provider hosting or private cloud agents. Their contracts and unsupported boundaries must be accounted for individually.

## Comparison protocol after analysis and implementation

Every case has a question, exact interface/version, frozen inputs and source lineage, expected output or independent oracle, planned mutation/negative case, clock/placement policy, artifacts to inspect and explicit acceptance criteria. Source-derived equations can be checked against analytic oracles; matching UI/worker code alone shares the same possible defect. Reuse retained outputs before spending more credits. Keep malformed intended-positive cases separate from intentional negatives.

Compare file bytes only where codec/container identity is expected. Otherwise compare decoded RGBA, frame count/order, durations/loop, pivot/offset and manifest semantics, retaining encoded hashes separately. A color-palette or alpha-loss export requires an explicit policy; do not silently use it as a source-faithful artifact. Video review must bind decoded PTS to captured frame timestamps and account for terminal duplicate frames. Godot native import/render/resource reload needs actual exported placement metadata.

Visual review is independent of mechanical conformance. Require native-scale keys, all adjacent pairs, directional identity/equipment comparison and correctly timed playback. Review pose anatomy, readable intent, weight/contact, limb attachment, equipment handling, outline/cluster quality, hidden-surface gaps, flashes and seams. A reviewer names what they viewed and what remains unseen; no full-playback claim from a few sampled screenshots. The requested9/10 gate remains unachieved until reviewers inspect the actual complete result and the user can see it.

## Build order once the analysis gate is closed

First implement the data/revision/state core and source-bound raster/scene methods. Then integrate acquisition/preparation, recovered pose/effect methods, library/exports and editable exchange. Next add capability-constrained local backend substitutions, only with known inputs/outputs and explicit fidelity limits. Finally execute the predeclared complete-flow comparisons and art refinements, then H3. Each stage has executable admission checks and produces the same artifact/evidence types, so the next AI can reproduce and improve it without reconstructing scattered experiments.

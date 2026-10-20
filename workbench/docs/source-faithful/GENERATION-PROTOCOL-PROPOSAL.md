# Proposed interchangeable generation protocol

This is a preparation proposal, not implemented provider support or a recovered
PixelLab model algorithm. Read-only inspection used canonical runtime
`/home/astra/projects/pixellab-local-workbench` at `78bcd74` and the retained
research checkout `/home/astra/projects/pixellab-local-test-20261011`.
No provider/model calls, new art, runtime edits or new algorithms were performed.

The reusable boundary is **freeze supplied inputs → explicitly selected external
generator → retain raw output → validate observed output → review → publish**.
Interchangeability means the intersection of demonstrated task capabilities.
A still-image generator cannot silently stand in for temporal generation,
ordered joint conditioning, interpolation or exact-mask editing. An adapter that
cannot consume required conditioning must return unsupported before submission.
The unchanged PixelLab procedural renderer remains a separate source execution
path; externally generated art must not be classified as recovered PixelLab code.

## Evidence and limits

| Concern | Evidence actually available | Protocol consequence |
| --- | --- | --- |
| Image roles | Retained clients distinguish appearance/reference art, style slots, actual reference pose, ordered target poses, first/init and optional end frames. `prepare.py` currently accepts reference roles only `style`, `subject`, `unspecified`. | Preserve roles, order and hashes. Do not flatten every image into an interchangeable reference list. New pose/endpoint roles need explicit schema support; existing preparation does not already express them. |
| Skeleton conditioning | Frozen public `AnimateWithSkeletonV3Request` requires first image, its actual 18-joint pose, ordered target joint sets, appearance description, action and direction; template body controls missing depth. Private rendering is absent. | A rendered mannequin or text description of a pose does not satisfy joint conditioning. Reject this task on an adapter without demonstrated matching inputs. |
| Prompt ownership | `AnimatePixminimaxRequest` separates motion `description` from subject, direction, view and initial pose. Enhancement is optional and returns expanded text. `prepare_prompt` only normalizes source-selected text and explicitly marks learned transformations unsupported. | Retain user text, selected source preparation profile, normalized text, actual submitted text and any returned enhancement separately. No silent assistant rewrite, inferred style description or local imitation of enhancement. |
| Masks and preservation | Retained ProFlash and generic placement paths differ; mask/ROI and changes-only compositing are mode-specific. Reported outside-mask equality did not prevent opaque-white damage inside a repaired alpha region. | Record mask meaning, coordinate space, master raster/frame and exact intended preservation constraints. Verify returned pixels and placed pixels separately. Reject a failed invariant; do not introduce automatic cleanup or restoration as a claimed PixelLab technique. |
| Seeds | Public contracts describe seed 0 as random. Retained identical-seed TextV3 repeats differed; this does not establish every engine's behavior. | Store requested seed, effective/reported seed, engine/version and observed reproducibility independently. Cross-provider seed equality does not mean equal randomness or deterministic replay. Unsupported seed control stays unsupported/null. |
| Frame roles and clocks | Retained TextV3 requested 4/8 and returned 5/9 with redrawn first frames; native MiniMax requested 8 and returned 9 with an exact first frame, while conversion changed first-frame alpha. Public image arrays do not establish universal FPS. | Preserve every raw returned frame and original index. Require an explicit role map and source/provider/author timing origin. Never universally trim frame zero, coalesce repeats, infer motion from a variant grid, or treat inherited editor FPS as model timing. |
| Size and representation | Public PNG/JPEG contracts differ from private raw-RGBA paths; public/private style-grid size buckets disagree. Source crop, prepared pixels, returned crop and placed canvas are distinct. | Retain encoded bytes, decoded RGBA, dimensions and transforms per stage. Requested size, accepted size and observed size are separate facts. No silent resampling or native-pixel-size claim. |
| Model identity | Retained findings associate PixMiniMax with MiniMax H3, while deployed checkpoint, fine-tune and decoder remain unknown. Model-selector strings do not identify weights. | Record actual available provider/model/revision when known and retain unknowns. Public H3 execution would be a separate backend, not proven PixelLab server parity. |

The current session's built-in image-generation tool exposes a prompt,
transparency request, and reference-image mechanisms. Its declared call schema
does not expose an explicit seed, joint tensor, exact edit mask, native output
width/height, animation-frame clock, or reproducibility guarantee. These are
unverified/unsupported controls at this boundary. Describing a desired size or
mask in prose is not equivalent to a typed enforced control. The agent tool is
also not automatically a callable offline HTTP service in this repository.
An initial adapter can freeze a handoff and import its returned artifact; direct
service execution needs a real authorized callable transport. No H3 callable
transport, local weights, supported input controls or execution results were
established by this inspection.

## Minimal proposed local documents

These fields are local orchestration records, not a PixelLab wire schema. Keep
each task's original adapter payload alongside its projection into this envelope.

1. **Immutable request**: schema/version, task (`still`, `edit`, `animation`, or
   `interpolation`), user instruction and its hash, provenance/technique references,
   ordered input entries `{artifact_id, role, slot, coordinate_space}`, master and
   mask IDs plus polarity/meaning, typed pose/endpoint data only when genuinely
   supported, requested geometry/frame roles/timing, and explicit preservation
   invariants. Keep prompt fields separated by meaning. Unknown timing and
   unsupported conditioning cannot masquerade as defaults.
2. **Backend binding**: request ID, selected backend/transport and available model
   revision, capability evidence, mapping from each neutral requirement to an
   actual backend field, unsupported requirements, and requested/effective settings.
   Include prompt ownership and preprocessing decisions. Explicitly distinguish
   omitted settings from provider-default unknowns. Admission requires a complete
   mapping for every required input; never silently drop a mask, end frame or pose.
3. **Generation receipt**: frozen request/binding IDs; actual submitted prompt and
   image hashes/order; raw response and output-byte artifact IDs; reported engine,
   revision/seed/size and completion identifiers when present; execution timestamps
   and usage/cost only if observed; errors/cancellation and output disposition.
   Distinguish agent-tool execution, imported external results, recovered-source
   execution and local host utilities. Exclude credentials from durable receipts.
4. **Result manifest**: raw-index inventory, encoded and decoded hashes, observed
   canvas/channel/alpha characteristics, explicit frame roles and mapping to source
   inputs, transforms with owner/reason, timing/loop/pivot/direction values and
   their origin, and derived sequence ID only once those decisions are explicit.
   Original output is never overwritten by a normalized candidate.
5. **Comparison/review record**: paired request IDs, conditions actually shared,
   deliberately backend-specific fields, capability mismatches, explicit frame
   pairing and geometry policy, preservation/alpha checks, whole-frame diagnostics,
   and separate human visual decisions. Unequal canvases/counts remain visible;
   no automatic alignment or invented art score. Never turn missing conditioning
   into a nominally fair comparison by silently discarding it from both requests.

The user owns task instructions and requested changes. Source normalization owns
only the transformations actually recovered for its named adapter. A backend owns
its private inference and any explicitly requested enhancement. The host owns
immutable records, validation, admission, scheduling and reversible file handling.
Reviewers own visual acceptance. These ownership boundaries belong in receipts.

## Reuse and necessary gaps

Canonical runtime paths:

- `sprite_workbench/core.py`: content-addressed bytes/rasters/sequences, rational
  durations and immutable artifacts. New generation records can be JSON artifacts;
  their dependent-artifact closure is not currently implemented automatically.
- `sprite_workbench/prepare.py`: explicit supplied-raster ROI/size/pad/encoding,
  masks, reference slots and audit IDs; `prepare_prompt` provides inert source
  normalization. Its sampling and ordering policies are explicitly local where
  labelled; they are not universally unchanged original algorithms. Do not add
  learned shading, captioning, cleanup or animation to this module by analogy.
- `sprite_workbench/jobs.py`: request snapshots, durable status, progress,
  cancellation, retries, stale-head guards and quarantining. Registering a real
  external handler remains separate work; do not repurpose the source VFX handler.
- `sprite_workbench/acquisition.py`: original bytes and decoder identity;
  `import_image` currently assigns a local 1/12-second duration when absent.
  Generation result admission must preserve unknown timing in a manifest and
  require an explicit authored clock before treating a result as animation.
- `sprite_workbench/review.py` and `replication.py::compare_sequences`: all-frame,
  adjacency/loop and RGBA/alpha/hidden-RGB diagnostics, full-canvas comparisons
  without alignment. They are diagnostics, not anatomy/style or temporal quality
  judges. Frozen/masked invariants need explicitly selected masters and mappings.
- `sprite_workbench/export.py`, `library.py`, `construction_services.py`: portable
  supplied-art editing/export, reviewed candidates and guarded promotion. A new
  receipt's dependency fields must be added to export closure and tested in a
  fresh Store; arbitrary nested artifact IDs are not followed automatically.
- `sprite_workbench/capabilities.py` and `source_workflow.py`: honest separation
  of unsupported vendor interfaces and local services. Reuse the separation,
  not `deterministic-source` as a label for unrelated model inference. Current
  classification choices do not themselves establish external-generator support.

## Five source-backed next steps

1. Freeze the request/binding/result-manifest schemas above against two bounded
   task types: supplied-reference still generation and a declared edit. Use only
   existing supplied fixtures to test receipts and unsupported-capability admission.
   Keep joint-conditioned animation and interpolation blocked unless their actual
   backend controls are demonstrated.
2. Build the provider-neutral **handoff/import boundary**, not a substitute art
   algorithm: copy exact instructions, ordered source references and hashes into
   a reviewable immutable packet; import externally returned bytes with transport
   provenance and observed settings. Make seed/size/mask/clock unknowns explicit.
3. Extract/select only evidenced preparation and placement profiles from retained
   source traces; map supported backend fields one by one. Keep crop/ROI, alpha,
   master masks and prompt ownership visible. Require an explicit decision before
   any existing local conversion, resizing or clock default is applied.
4. Add mechanical admission/finalization gates using the existing Store and review
   utilities: geometry/channel/frame-role integrity, intended outside-mask/frozen
   equality against declared masters, preservation of raw bytes, and unreviewed
   candidate disposition. Round-trip new receipt closure through editable export
   and a fresh Store before any external generation is needed.
5. Predeclare a small comparison sheet with equal supplied conditioning, prompt
   ownership, per-backend supported controls and unknowns, raw/placed-frame maps,
   exact diagnostics, and human identity/style/alpha/motion review criteria. Run
   actual models only in a later explicitly authorized execution stage; count a
   task unsupported when a necessary conditioning channel is missing.

## Exact retained evidence paths

- Current authority: research `START-HERE.md` and runtime
  `docs/consolidation/CONSOLIDATED-FINDINGS.md`, especially appearance/motion,
  paid frame roles/seeds, masks, references/prompts, and models/training rows.
- Frozen field authority: runtime `sprite_workbench/contracts/openapi.json`,
  `/components/schemas/AnimatePixminimaxRequest`, `AnimateWithSkeletonV3Request`,
  `AnimateWithTextV3Request`, `InpaintImageProFlashRequest`, and
  `GenerateWithStyleV2Request`. Snapshot declarations are not measured guarantees.
- Research `analysis-contract/depth-round2/full-feature-gaps/FAMILY-STAGE-SPEC.json`,
  keys `image-edit-inpaint`, `text-template-wrapper-animation`,
  `skeleton-estimation-animation`, `style-reference-creation`, `prompt-caption`,
  and `interpolation`. Each retains named branches and source-trace paths.
- Research `RECONSTRUCTION-REQUIREMENTS.md` remains a labelled historical design
  record. Its stronger preservation proposals must not be presented as proved
  recovered behavior; current authority is the preceding START-HERE entrypoint.

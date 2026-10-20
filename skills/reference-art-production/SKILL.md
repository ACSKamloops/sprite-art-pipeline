---
name: reference-art-production
description: Create consistent raster art from visual references or an original art brief, including sprites, portraits, illustrations, icons, textures and asset collections. Use for reference selection, generation, fidelity review, targeted repairs, exports and a verified handoff; scale the workflow down for a single image.
---

# Reference Art Production

Produce usable art with traceable inputs and a truthful review state. Preserve the user's subject, medium, style and delivery choices. This workflow supports original designs as well as faithful adaptations; it does not require a particular franchise, model library, pixel size or engine.

## Establish the art brief

Recover the user's approved examples and project pipeline before experimenting. Record intended use, subjects, style, composition/view, background or transparency, dimensions, required text and delivery location. Distinguish static portraits from poses, animation frames, seamless textures, UI art and 3D assets. A reference image is enough to begin 2D art; a 3D-rendering route needs suitable geometry and, for animation, a rig or an explicit modelling task.

Ask only for material information that is unavailable. Continue independent work while optional preferences are pending. For an established style, use the approved result as the style reference and proceed. For a large collection without an approved style, create a small representative pilot including difficult shapes before committing the full batch. A single straightforward image needs no batch manifests or gallery unless useful to its consumer.

## Select and inspect references

Read [references/reference-inputs.md](references/reference-inputs.md) when collecting or assessing inputs. Assign each image an explicit role: identity/geometry, style, pose/composition, material/colour, or edit target. Inspect local images before using them. Separate photographed details from inference, reconstruction and deliberate design changes.

For faithful adaptations, obtain enough coverage to identify silhouette, appendages, accessories, text and distinguishing features. A cropped photo cannot establish hidden geometry. Look for an appropriate supplemental reference when an important area is missing; record its source and which gap it resolves. For original designs, a sufficiently concrete brief can replace identity photographs. Do not demand references merely to begin exploration.

## Generate, compare and repair

Use the available image-generation skill/tool for raster creation and semantic edits, following its current invocation rules. In this environment, built-in image generation is the default, including batches and transparency. Do not silently switch to a paid API/CLI fallback. Prefer the existing editable source for vector/native art when that is the requested medium.

Write a shared style specification and a subject-specific prompt. Label reference images by index and role; specify photographed or requested geometry, pose, palette, loadout, composition and exact lettering. For isolated assets, request actual transparency and enough framing margin for the entire subject. Do not impose a 16-bit palette, side view, ground shadow, display base or background unless the brief calls for it.

Save each actual prompt, ordered input paths, output path and tool result/error. Keep original references and generated masters. Inspect each delivered image alongside its identity and style references, at final display size. For large sets, use manageable comparison sheets, then open uncertain assets separately. Check silhouette, limbs/heads/wings, accessories, text, cropped extremities, unwanted stands/scenery, transparency and consistency. File checks cannot establish visual fidelity.

Repair a demonstrated defect with a targeted edit: identify what changes and what must stay. Reinspect the repaired result and its final export. Keep the previous master and edit receipt. A review applies to a specific export hash; changing the image invalidates that review. Describe authored substitutions plainly. If generation is blocked, preserve the failure and retry only with a meaningful permissible adaptation consistent with the task; do not repeatedly reword the same prohibited request or label an adaptation as an exact reproduction.

## Collections and resumable work

For batches, read [references/batches-and-handoff.md](references/batches-and-handoff.md). Freeze the requested inventory before generation and retain stable source IDs. Group only truly reusable representatives while keeping every original ID in the mapping. Similar names, different equipment or different paint schemes do not prove identity. Count requested entries, generated representatives and reviewed representatives separately.

For the concrete claim-next worker setup, read [references/batch-runbook.md](references/batch-runbook.md). It includes the runnable `scripts/claim_next.py` coordinator, source-review gating, exclusive worker tokens, per-attempt receipts/errors, interrupted-job recovery, pending-only comparison sheets, targeted repair attempts and final completion commands. The linked tool-worker example runs bounded windows through the available built-in image tool; it does not require subagents or an API fallback.

Use one writer for manifests and receipts, and resume from saved successes. Parallel generation, if supported and authorized, needs exclusive job ownership and separate receipt files. Never claim completion while jobs, failures or reviews remain unresolved. Independent adversarial review is useful when requested; it is not automatically required for ordinary art work.

## Export and verify

Read [references/exports-and-validation.md](references/exports-and-validation.md) for output profiles and the bundled helper. Use Python/image utilities only for mechanical exports, alpha checks, resizing, comparison-sheet layout and file management; use the image tool or requested art editor for semantic changes.

- **Pixel art:** preserve the high-resolution master; choose canonical canvas, fit region, anchor and alpha handling explicitly. Use nearest-neighbour resizing and exact integer enlargement. Do not infer common world scale from independently fitted portraits.
- **Other raster art:** retain intended gradients and soft alpha. Avoid pixel-sprite thresholding, palette limits or nearest filtering unless requested. The helper's raster profile copies the master at native resolution.
- **Textures/animation/native files:** validate the properties actually promised: tiling seams, frame order/pivots, continuity, layer editability or engine imports. A still image collection is not an animation pack or a rig.

Verify dimensions, decoding, alpha, framing, scale variants, hashes, source IDs and all handoff paths. For a gallery, check filters, missing images, links and intended viewing contexts; for game integration, test the actual engine import rather than claiming it from PNG checks. Preserve earlier approved assets unless replacement is in scope.

## Deliver

Provide the requested format and location. For another local AI, a folder with relative asset paths, a source-ID map and a concise `HANDOFF.md` is sufficient; do not introduce uploads, ZIPs or credentials. Include art specifications, source credits, actual prompts/repairs, limitations, review status and verification evidence. Point to full-resolution masters and editable sources when available. Mark complete only after the requested coverage and required checks pass. Report static/animated status and any material authored deviations accurately.

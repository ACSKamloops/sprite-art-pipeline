# Batch production and local handoff

For commands, the claim coordinator and the generation/review loop, use [batch-runbook.md](batch-runbook.md). This document explains the evidence and delivery conventions.

## Work state

Keep original inputs separate from working masters and final delivery. A practical layout is `source/`, `masters/`, `receipts/`, `review/` and `delivery/`; adapt it to the project. Do not reinitialize an existing successful collection or overwrite the source archive.

Freeze the requested inventory with stable IDs, names, categories and variants before generating. Preserve every requested ID in `target_ids` or the project's equivalent. A representative can cover several entries only when the required art is interchangeable; preserve aliases individually. Missing reference images are a source problem, not permission to omit a target.

Track useful states such as reference-needed, ready, generating, generated-awaiting-review, repair-needed, accepted and failed. Save each successful tool result immediately. When resuming, verify existing outputs and receipts before making calls. Save generation failures separately; clear an active failure only after a valid replacement exists, retaining the history. Avoid concurrent writes to the collection manifest.

Prompts and receipts need the actual executed text, tool used, ordered input images, returned image location and any deviations. For a repair, retain the old master, new master, reason, edit prompt and added references. Do not reconstruct an imagined prompt after the fact. Record the latest chosen master explicitly so an export refresh cannot resurrect the rejected original.

## Review evidence

Inspect references before generation and exports after it. In large collections, comparison sheets can present several labelled final-size subjects with their identity photographs; use small enough pages to notice details. A sheet successfully rendering is not a visual review. Open ambiguous subjects at useful resolution.

Accept the image hash that was actually inspected. After semantic edits or mechanical export changes, review the updated output, including its final display scale. Metadata-only updates can reuse the same image review. Human/user review, root-agent review and independent-agent review are different evidence; name the actual reviewer rather than claiming a review that never happened.

If an independent audit is requested, provide the brief, actual references and exports, without steering the reviewer toward the desired conclusion. The reviewer should report concrete differences, source ambiguity and severity. A changed master must be reinspected rather than approved solely from a textual repair report.

## Handoff contents

For a local consumer AI, deliver relative PNG/document paths and preserve full source IDs. Include:

- `HANDOFF.md`: how to consume the files, intended use, art specification, transparency/filtering/anchor rules, static or animated status, and relevant limitations.
- Manifest and source-ID map: representatives, all covered IDs, latest files, hashes, references and review state.
- References/credits and provenance: actual source images where appropriate, source URLs/hashes, prompts, repair history and authored substitutions.
- Verification report: checked coverage and file properties, plus runtime/browser evidence only when performed.
- Optional local gallery/comparison sheets when they make a large collection easier to review.

High-resolution masters or editable originals can be in the collection or linked by absolute local paths for a shared VM. Label absolute paths as machine-local; use paths relative to the delivery root for files that should move together. A UUID map must not depend on filename guessing or truncated IDs.

Generated interpretations are not extracted original assets. Document reconstructed hidden geometry, changed clothing/instruments, alternate paint schemes and simplified lettering where material. Do not describe a pose, lighting angle or relative size as consistent unless it was deliberately controlled and checked. Independent canvas fitting is appropriate for portraits, but does not establish unit scale for a game world.

Test a gallery's search, category filters, links, image decoding and intended screen sizes. If claiming it opens directly from disk, test `file://` rather than only an HTTP server. Preserve previously approved sets, and verify copied bytes if claiming they are unchanged. Declare complete only after the requested inventory, latest visual reviews and required verification all agree.

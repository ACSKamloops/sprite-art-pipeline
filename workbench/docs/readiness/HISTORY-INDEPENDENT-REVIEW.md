# Independent checkpoint-history review

Reviewed the new v2 checkpoint envelope and accelerated receipt engine separately
from their producer. This review reuses no producer fixtures or random
differential helpers. It addresses local editing integrity, repeatability and
bounded object retention. It does not establish complete vendor replication,
complete command grammar, character construction or artistic quality.

**Result: 13 independent cases passed against the integrated implementation. No
additional unresolved history defect was established in this review.** The
observed legacy-provenance migration defect was already corrected by the
producer's `4f9764d` change before final verification.

## Exact tested implementation

Repository HEAD at verification:
`d7e250280694b9097466b493545dbeff35e0c12d`.

| File | SHA256 |
|---|---|
| `sprite_workbench/construction.py` | `5dc9bad2b715c132bcc03cc3212f770c4dfaac03dfa24dc7ce5536ad236bb4ef` |
| `sprite_workbench/construction_engine.py` | `8c07039fa87799424f64cb98fe5a1ef8410329a144a96f8e7fae2255dc2d7c30` |
| `sprite_workbench/export.py` | `3467cc91114229d780e376713277a148f0e93b4000cf7e93804298c2949c3bfe` |
| `sprite_workbench/core.py` | `285aabb1c67fce891b77b9aceae10a3bd7166f787fa7d03466754b47c04e7824` |

Tests are in
[`tests/test_history_independent_review.py`](../../tests/test_history_independent_review.py).
From the integrated checkout after installing that file, run:

```bash
.venv/bin/python -m pytest tests/test_history_independent_review.py -q
```

During the independent worktree review, tests ran against the root checkout
with an explicit `-o pythonpath=/home/astra/projects/pixellab-local-workbench`.
That override matters: otherwise pytest's worktree configuration can import the
older reviewer checkout instead of the implementation being reviewed.

## Independent discriminators

- A hand-computed semitransparent red/blue pixel must be exactly
  `[85, 0, 170, 192]`. Painting a palette alias and a hidden alpha-zero color
  changes exact cel indices while leaving composited RGBA unchanged. Cold
  replay preserves those indices, hidden RGB, shared cel bindings, frame holds,
  pivots and animation events.
- Five separately rehashed checkpoint-envelope forgeries change kind, boolean
  version, floating version, project hash or extra fields. Each fails cold
  verification. These are correctly hashed new artifacts, rather than merely
  corrupted files rejected by SHA verification.
- An invalid receipt beyond an undone cursor still fails cold replay. The redo
  tail is part of the verified journal.
- An identical history copied to a different Store triggers four actual cold
  replays. A warm proof in the original Store conveys no cross-Store authority.
  Deleting an intermediate checkpoint after successful warm verification fails
  subsequent loading.
- Instrumented warm use reads the source sequence, raster envelope, raw raster
  bytes, project and history by artifact identity. Corrupting the raster
  envelope rejects a subsequent operation before it can move the cursor.
- Instrumenting an 18-edit cold replay records decoded checkpoint and generated
  project objects through weak references. At most five tracked project objects
  coexist, and none remain after loading returns. The proof cache retains IDs
  rather than decoded projects. This is a structural object-retention test, not
  a claim about all Python allocations or peak process RSS.
- Editing after undo excludes the abandoned checkpoint from the branch. An
  editable export copied into a fresh Store includes every retained checkpoint
  byte-for-byte. After proof-cache clearing, cold verification and every undo
  and redo succeed in that fresh Store. The original branch remains unchanged.
- Two legacy migration cases preserve read-only v1 compatibility but reject a
  source-provenance mismatch on both edit and cursor movement. No immutable
  blobs are written by the rejected migration.

## Defect discovered during baseline inspection, now resolved

The earlier `5c5261b` history baseline accepted a valid v1 document whose initial
project wrapper had no `source_sequence` and whose current wrapper referred to
a valid sequence. Raw project content and receipts still matched, so v1 loading
accepted it. Mutating that history created a v2 state that a warm proof accepted
but a cold replay rejected with `Construction history source sequence changed`.

The producer had independently added `4f9764d`: retain v1 read-only compatibility,
but compare initial and current source provenance before materializing any v2
checkpoints. The final two tests independently verify that policy and the
absence of writes on rejection. This report does not count the already-fixed
baseline defect as an unresolved finding.

## Remaining boundaries

This small fixture review supplements the producer's operation differentials,
all-alpha compositor coverage and measured multilayer benchmark. It does not
replace them. Cold verification remains linear in accepted history complexity.
Large exact receipt coordinate lists still consume memory within the document
and operation admission policy; bounded checkpoint object retention is not an
unlimited-memory claim. No image generation, original-art comparison, browser
animation-quality review or private backend execution occurred here.

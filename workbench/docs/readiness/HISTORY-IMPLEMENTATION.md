# Verified checkpoint history

The implemented editing model now creates `construction-history` version 2.
Its JSON journal remains `sprite-edit-journal/v1`, with the same exact receipts,
cursor, initial project hash and public method results. The envelope adds
`checkpoints`: ordered typed construction-project artifact IDs, one initial
snapshot followed by one after-snapshot per receipt. The current artifact must
be exactly `checkpoints[cursor]`.

A cold load verifies initial admission, every snapshot's Store SHA and toolkit
project hash, every operation's original stale/mask/lock checks, the exact
canonical receipt and the resulting project, including redo receipts past the
cursor. Only one adjacent pair is replayed at a time; full historical before and
after project objects are not retained. Undo and redo select verified immutable
snapshots. Editing after undo removes the abandoned checkpoint/receipt tail.
The parent history and its blobs remain untouched.

A process-local cache contains at most 128 proofs, consisting only of dependency
artifact IDs. Successful local edits extend the already verified parent proof.
Before any reuse, every recorded project, source sequence, raster envelope and
raw raster blob is read and SHA-verified again. File stats, timestamps and
persistent cache files do not confer trust. Mutable Store tampering therefore
fails even in an already-warm process. Clearing the proof cache or starting a
new Python process triggers full cold replay. There is no persisted trust
shortcut: cold loading remains linear in the number and complexity of edits.

Version 1 loads retain their original replay and eager-snapshot budget guards.
Read-only loading does not write artifacts. A successful old-history mutation
materializes v2 checkpoints after complete v1 verification; this is an explicit
migration, not a changed interpretation of old receipts.

## Exact compositor derivative

[HISTORY-ENGINE-ORIGIN.json](HISTORY-ENGINE-ORIGIN.json) records the unchanged
pinned scalar source and the separately authored accelerated helper. No vendored
module was changed. Operations and validation still use the pinned functions;
receipt diffs use NumPy int64 for exactly the original nonnegative alpha formula.
Integer temporaries cover at most 65,536 pixels at a time. Identical ordered cel
bindings render once rather than separately for every frame that shares them.
Cel index differences remain separate from composited RGBA differences, so
aliases and hidden colors retain their original behavior.

Independent differential checks compare exact canonical projects and receipts
for all ten operation kinds across 12 fixed random seeds. They include palette
aliases, alpha-zero hidden colors, semitransparency and partial layer bindings.
A separate exhaustive check compares all 65,536 source/destination alpha pairs
and crosses a compositor chunk boundary. All outputs match the pinned scalar
implementation. These are local editing semantics, not PixelLab model or host
runtime parity.

## Resource policy

Project, transaction and JSON admission caps are unchanged. V2 replaces the old
all-history eager snapshot budget with distinct limits:

* 256 receipts and the existing 16 MiB document cap;
* peak indexed working-set estimate of four current cel-index arrays, within the
  existing 33,554,432-value admission budget;
* at most 256 MiB of unique checkpoint and source-raster dependency bytes;
* at most 536,870,912 aggregate cold replay work units, counting deduplicated
  frame-layer pixel work, cell-index scanning and transaction operations;
* unchanged single-operation work admission.

Limits are checked on warm loads as well as cold loads. Repeated identical
snapshots consume byte budget once. They still consume receipt/replay work.
Candidates persisted before an I/O or later budget failure can leave immutable
unpublished blobs; no whole-Store rollback is claimed. No heads are published.

## Measured result and limits

The [performance gate](HISTORY-PERFORMANCE-GATE.md) was declared before running
the benchmark. [HISTORY-benchmark.py](HISTORY-benchmark.py) creates supplied
256x256 indexed marker projects with 24 frames, shared cels, unequal tick holds,
a fixed event, palette aliases, hidden color and a locked top layer. These are
mechanical fixtures, not humanoid artwork or a quality score.

[HISTORY-BENCHMARK.json](HISTORY-BENCHMARK.json) records the resource-accounted
second run. Both cases passed every declared timing and cold verification gate:

| Layers / cels | First edit | Twentieth edit | Slowest edit | Warm undo / redo | Fresh-process cold load |
|---|---:|---:|---:|---:|---:|
| 1 | 0.125 s | 0.135 s | 0.136 s | 0.073 / 0.070 s | 1.170 s |
| 11 | 1.235 s | 1.420 s | 1.420 s | 0.872 / 1.316 s | 13.802 s |

Each cold subprocess instrumented exactly 20 receipt replays and matched the
warm final project hash. This is stronger than constructing another Store object
inside a process that still holds proof-cache entries. The prior v1 observation
(0.904 s first edit, 18.123 s twentieth) used the same canvas/frame/one-shared-cel
scale; fixture content differs, so it is a workload-scale comparison rather
than a byte-identical A/B benchmark.

The process's `/proc/self/status` peak RSS rose from 51.1 MiB in the one-layer
case to 72.3 MiB in the 11-layer case. After the last multilayer edit its current
RSS was 50.9 MiB. The cold child reported about 80.6 MiB. The separately retained
`resource.ru_maxrss` parent reading was already 1.21 GiB at the first sample and
contradicted the current process's `/proc` high-water measurement; it is not
used as the current executable's working-set figure. The report retains both
raw metrics rather than hiding the disagreement.

Cold verification at 11 layers is about 14 seconds and can grow with additional
edits or distinct frame bindings. That remains visible loading cost; passing
warm timings does not establish instant load or unlimited project scale. The
new stage resolves the demonstrated repeated-replay editing slowdown for these
representative shared-cel mechanical fixtures. A representative humanoid edit
session and aesthetic animation acceptance remain separate future gates.

Reproduce from the repository root with an absent output folder:

```bash
PYTHONPATH=. .venv/bin/python docs/readiness/HISTORY-benchmark.py --output runs/history-recheck
.venv/bin/python -m pytest tests/test_history_scalability.py -q
```

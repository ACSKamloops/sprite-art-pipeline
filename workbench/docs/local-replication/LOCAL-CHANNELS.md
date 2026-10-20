# Local replication channels

Version 0.9.0 also exposes `local.parity.catalog`, `palette`, `pixels`, `footprints`, `paint` and `to_sequence` over CLI/JSONL/HTTP/plans. [Source-method grammar](../parity-20261014/README.md) defines exact input schemas, mask formats and provenance boundaries. These operations perform no provider requests. `to_sequence` requires an authored rational still hold and replays the original method before promotion.

Current native-video and Studio extensions use the same local CLI/JSONL/HTTP/plan channels; see [Motion operation and source boundaries](../motion-pipeline-20261014/README.md) and [current grammar](../COMMANDS.md). Add `--enable-motion-provider` only for explicitly authorized standalone native calls. Without that flag, generation execution is disabled; all plans disable paid execution regardless of host settings. The supplied diagnostic recipes below remain independent of provider execution or art approval.

Use `/home/astra/projects/pixellab-local-workbench` as the working checkout. The installed local command is `/home/astra/projects/pixellab-local-workbench/.venv/bin/sprite-workbench`. These channels execute the implemented mechanics on supplied artwork and deterministic fixtures. They do not provide the vendor's private generation models, complete its native editor, or certify art quality. The [completeness audit](COMPLETENESS-AUDIT.md) keeps those requirements separate.

## Environment and first replay

The setup script installs this checkout into its own `.venv` with hashed dependency pins from `requirements-local.lock`. The tested setup uses Python 3.14 on this WSL host. Node and Godot remain separately installed executables; `doctor` records their locations and versions. A successful version probe is not an engine or renderer test.

```bash
cd /home/astra/projects/pixellab-local-workbench
bash scripts/setup_local.sh
.venv/bin/sprite-workbench lab doctor
.venv/bin/sprite-workbench lab catalog
.venv/bin/sprite-workbench lab replay --output runs/my-first-local-replay
.venv/bin/sprite-workbench lab verify-run runs/my-first-local-replay
```

Output directories must be absent. Existing work is preserved. Open `runs/my-first-local-replay/index.html` locally for the receipts and frame/playback review links. No web host or account is required. Repeating the replay into a different directory creates fresh Stores; UUIDs, timestamps and file paths may change. Compare supplied sequence pixels and clocks rather than expecting all state database bytes to match.

Each run freezes package file hashes, environment probes and selected recipe IDs before execution. Each recipe records its input artifact identities, ordered operations, positive/negative checks, output identities and limitations. `RUN.json` summarizes only the selected diagnostic checks. `MANIFEST.json` binds the resulting files. `verify-run` detects missing, changed and extra files relative to that manifest; it does not authenticate a replaced manifest or rerun the checks.

Use repeated `--flow F01 --flow F07` arguments for a selected replay. The default runs all eleven bounded recipes. `completed` means that recipe's explicit checks passed. A required failed/missing engine check makes its recipe incomplete. The original F01–F11 comparison specifications remain broader than these diagnostics.

## Operational routes

| Family | Callable recipe | General local route for your own inputs |
|---|---|---|
| F01 import/refine | `replay_methods.run_flow('F01', store, output)` | CLI `import`, plan `prepare`, `edit`, `export`; guarded `crop`/`paste` |
| F02 parts/motion | `replay_geometry.run_flow('F02', store, output)` | Plan `scene`, `tracks`, `edit`; typed editable export/reload APIs |
| F03 pose | `replay_methods.run_flow('F03', store, output)` | Plan `pose`; Python `pose.project_pose`, `nearest_pose`, `save_supplied_motion` |
| F04 character library | `replay_state.run_flow('F04', store, output)` | Persistent channel `local.library.*` state/direction/animation methods |
| F05 candidates | `replay_state.run_flow('F05', store, output)` | Persistent channel create/review/select/promote, revision guards |
| F06 maps | `replay_methods.run_flow('F06', store, output)` | Plan `terrain`; Python `terrain` topology, reblit and persistence APIs |
| F07 preparation | `replay_methods.run_flow('F07', store, output)` | Plan `prepare`; Python `prepare.prepare_request` and versioned policies |
| F08 UI/font/vocal | `replay_methods.run_flow('F08', store, output)` | Plan `ui`, `font`, `text`, `visemes`; supplied glyph/metric APIs |
| F09 effects | `replay_geometry.run_flow('F09', store, output)` | Plan `effects`, `compose`, `edit`; pinned Node renderer |
| F10 exchange | `replay_geometry.run_flow('F10', store, output)` | CLI `export`, `review`, `lab compare`; editable import and Godot project |
| F11 state/jobs | `replay_state.run_flow('F11', store, output)` | Persistent channel `local.jobs.*`; offline `capabilities` definitions |

The recipes are readable Python routines, not tests hidden behind a pass count. Every one takes an explicit `Store` and absent output directory. They are frozen diagnostic examples; use the general APIs or plans to supply your own art. Nested argument grammar is in [COMMANDS](../COMMANDS.md), [METHODS-API](../METHODS-API.md), [STATE-SERVICES](../STATE-SERVICES.md) and [GEOMETRY-EXPORT-REVIEW](../GEOMETRY-EXPORT-REVIEW.md). Keep source-specific adapter names explicit.

## Persistent channel for another AI

Start this as a child process and keep stdin/stdout open:

```bash
.venv/bin/sprite-workbench --workspace workspaces/my-project channel \
  --base-dir /absolute/path/to/my/inputs --result-ref source.sequence --workers 2
```

This is local JSON Lines over standard input/output, not HTTP or an installed MCP server. The first output is a `ready` event. Then send one JSON object per line. Every response echoes the request `id` and separates channel dispatch status from the returned job/candidate status. A `completed` envelope does not mean a returned job finished successfully. Requests have a 4 MiB limit. The base directory resolves relative input/output paths; it is a working directory, **not a filesystem sandbox**. This is for trusted local orchestration.

```json
{"id":1,"method":"system.capabilities"}
{"id":2,"method":"local.jobs.submit","params":{"handler":"local.pipeline","request":{"plan":{"version":1,"steps":[{"id":"source","action":"import","path":"source.png"}]}}}}
{"id":3,"method":"local.jobs.get","params":{"job_id":"RETURNED_JOB_ID"}}
{"id":4,"method":"local.jobs.cancel","params":{"job_id":"RETURNED_JOB_ID"}}
{"id":5,"method":"system.shutdown"}
```

Supported system methods: `system.ping`, `system.capabilities`, `system.shutdown`, with no parameters. The capability reply enumerates bound `local.jobs.*` and `local.library.*` services. Frozen public/MCP schemas remain available through the separate `capabilities` CLI and are not remotely invoked by this channel.

The registered `local.pipeline` handler uses the startup `--result-ref` (for example `source.sequence` or `compose.sequence`) to select the candidate output. A queued plan cannot contain `publish` or `promote`. Submit with an optional `head` and `expected` revision for guarded publication; candidate promotion is a separate explicit library operation. Poll `get`/`list` to keep the channel responsive. `local.jobs.wait` blocks request dispatch for its bounded wait, so cancellation on that same channel must wait for the reply. Jobs continue in worker threads between requests.

Cancellation is cooperative. Shutdown/EOF uses a bounded worker drain; it does not force-kill subprocesses or roll back already written candidates. Retained job state survives restart. Interrupted jobs require inspection/retry; queued work resumes after its handler is registered again. Do not open two managers on the same Store concurrently.

Library operations include `create_candidate`, `record_review`, `select`, `promote`, `get`, `list`, `set_direction`, `remove_direction`, `set_state`, `set_animation`, `remove_state`, `remove_animation`, `archive`, `delete`, `restore`. Review metadata is caller-supplied evidence, not an automatic quality score. `select` requires actual source IDs, and revision-changing operations require the expected revision. Full parameter contracts follow the named `Library` methods and [STATE-SERVICES](../STATE-SERVICES.md).

A complete caller example handles returned IDs and checks the job result before promotion:

```bash
.venv/bin/python examples/local-channel/client.py \
  --image /absolute/path/to/source.png --output runs/my-channel-session
```

This saves a persistent Store and request/reply transcript. It imports the supplied art without rating or generating it.

## Your own artwork and fine edits

Use the [construction channel](../construction/README.md) for layered indexed cels, exact palette edits, guarded transactions, immutable history and bounded native LibreSprite exchange. It exposes twelve additional `local.construction.*` methods through this same persistent channel and through declarative plans. Its editor/metadata limits and verified scope are separate from native host parity and art quality.

Import an explicit PNG/APNG using `sprite-workbench --workspace STORE import FILE`, retain the returned sequence/raster IDs, then write a version-1 plan. Relative paths are resolved beside that plan when using `run`. Copy `examples/supplied-motion` to a fresh work area before editing its fixture/plan; the example is a mechanics demonstration.

Supply registered directions, owned part masks, anchors, hidden-surface artwork, strong action poses and rational timing. A still image does not supply its occluded surfaces or missing directions. Edit individual cels or masks as PNGs in an existing editor and import the replacement; use expected-source crop/paste or guarded pixel edits when exact changes must be proven. Plan frame indices and scene indices are zero-based; pixel-edit frame indices are one-based. Explicit local transforms interpolate supplied parts/keys; private pose-to-art synthesis is not implemented.

Typed editable exports preserve their supported artifact dependencies. Reopen them with `export.import_editable` into a fresh Store and rebuild the scene/sequence before accepting round-trip fidelity. PNG alone is not a rig or editable scene. Godot output is a playable local project with declared clocks; headless checks do not count as continuous visual review.

## Supplied baseline/candidate comparison

```bash
.venv/bin/sprite-workbench lab compare \
  --baseline-store /absolute/baseline/store --baseline FULL_SEQUENCE_SHA \
  --candidate-store /absolute/candidate/store --candidate FULL_SEQUENCE_SHA \
  --output runs/my-supplied-comparison
```

The comparison preserves ordered full canvases and checks decoded RGBA (including hidden RGB), alpha, frame count, rational duration, pivots, direction labels and play count. It performs no implicit alignment, coalescing, resizing or quantization. `status: completed` means the comparison was produced; inspect `exact_sequence_match` and per-frame differences. Different art is not automatically bad, and exact equality is not a quality judgment. The two review players retain their own clocks and are not claimed to be a synchronized playback comparison.

For two complete eleven-recipe runs, use `.venv/bin/python scripts/verify_replication_pair.py --baseline RUN_A --candidate RUN_B --output ABSENT_DIRECTORY`. It checks both retained file manifests before and after comparison, equal package-source hashes, declared recipe inputs, and every primary sequence's full pixels/clocks/registration. It deliberately excludes state UUIDs, timestamps and engine wall-time equality. This supports checkout-versus-installed-wheel reproduction; it is not a vendor output-quality comparison.

Before a generation comparison, freeze the question, source and expected behavior, exact adapter/model identity, seed/request policy, edit masks, registration, clocks, quality gates and negative controls. Preserve every output, including rejected candidates. Review all ordered pairs, loop seam and complete normal-speed playback; bind reviewer notes to exact artifacts. Private model recovery, full vendor flow parity and the requested 9/10 humanoid animation remain separate unfinished work. H3 remains after its prerequisites.

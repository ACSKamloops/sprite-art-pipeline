# Local CLI, plan, channel and HTTP grammar — v0.9.0

## Original client methods in v0.9.0

Use `sprite-workbench --workspace STORE parity METHOD REQUEST.json` for `catalog`, `palette`, `pixels`, `footprints`, `paint`, `to_sequence`. The equivalent JSONL/HTTP method is `local.parity.METHOD`, and the plan action is `parity` with `method` and `request`. [Exact schemas, examples and boundaries](parity-20261014/README.md) cover raw transport, three mask encodings, replay verification and cold-export evidence. No provider execution is involved.

These are implemented **local** transport dialects. The `pixellab-vfx` route executes recovered original browser functions; the editor and other local routes retain their own implementation contracts. Replication never substitutes invented heuristics or a local craft for an unavailable original method. These transports do not claim parity with the hosted PixelLab argv parser, its incomplete nested draw grammar or private model handlers. [Readiness](readiness/README.md) distinguishes supplied-art operations and setup diagnostics from held original-art/model comparisons.

```text
sprite-workbench [--workspace STORE] import PATH
sprite-workbench [--workspace STORE] inspect ARTIFACT_OR_HEAD
sprite-workbench [--workspace STORE] edit SEQUENCE_OR_HEAD CHANGES_JSON
sprite-workbench [--workspace STORE] run PLAN_JSON
sprite-workbench [--workspace STORE] export SEQUENCE_OR_HEAD DIRECTORY [--formats COMMA_LIST]
sprite-workbench [--workspace STORE] review SEQUENCE_OR_HEAD DIRECTORY
sprite-workbench [--workspace STORE] capabilities [--id ID] [--domain public|mcp|local]
sprite-workbench [--workspace STORE] pixellab-vfx describe|validate|controls|render REQUEST_JSON
sprite-workbench [--workspace STORE] construct METHOD REQUEST_JSON
sprite-workbench [--workspace STORE] models METHOD REQUEST_JSON
sprite-workbench [--workspace STORE] selection METHOD REQUEST_JSON
sprite-workbench [--workspace STORE] studio METHOD REQUEST_JSON
sprite-workbench [--workspace STORE] motion METHOD REQUEST_JSON [--enable-motion-provider]
sprite-workbench [--workspace STORE] crop RASTER_ID X0,Y0,X1,Y1 [--node NODE]
sprite-workbench [--workspace STORE] paste CROP_PACKET_JSON ROWS_JSON --expect CROP_GUARD [--stamp]
sprite-workbench [--workspace STORE] channel --base-dir DIRECTORY --result-ref STEP.FIELD [--workers 2] [--enable-motion-provider]
sprite-workbench [--workspace STORE] web --base-dir DIRECTORY [--port 8874] [--workers 2] [--enable-motion-provider]
sprite-workbench lab doctor
sprite-workbench lab catalog
sprite-workbench lab replay --output ABSENT_DIRECTORY [--flow F01 --flow F07]
sprite-workbench lab verify-run DIRECTORY
sprite-workbench lab compare --baseline-store STORE --baseline SHA --candidate-store STORE --candidate SHA --output ABSENT_DIRECTORY
```

`python -m sprite_workbench` invokes the same CLI. Responses are JSON. Exit 0 means the command completed; exit 2 means failed/validation/unsupported. A valid result can still have individual unsupported preview formats: inspect `formats`, do not equate exit 0 with every format or visual acceptance. Inputs are finite JSON with a 4MiB CLI budget. Capability definitions are frozen snapshots; invoking a vendor ID does not route to a local substitute or make a remote request.

`--workspace` selects the immutable Store and must precede the subcommand. `construct METHOD REQUEST_JSON` accepts `save`, `read`, `get`, `write`, `history`, `edit`, `undo`, `redo`, `from_sequence`, `render`, `ase_export`, or `ase_import`. Its request fields are listed in [construction](construction/README.md) and defined in `construction_services.SCHEMAS`. Construction filesystem paths resolve beside the request file. Use a small `read` request pointing to a project file for dense projects: the file reader accepts up to 16MiB, while the CLI request itself stays within 4MiB. `get` returns a compact summary; `write` exports the editable document to a new file.

`paste --expect` takes the crop packet's `guard`, not its source/cropped raster ID. `ROWS_JSON` is a rectangle of exact RGBA byte arrays `[row][column][channel]`. Replace writes every cell; `--stamp` writes only cells with nonzero alpha. This local dialect does not accept the hosted workbench's legend/text-row packet implicitly.

`motion` methods are `catalog`, `load_example`, `decode`, `sample`, `condition`, `retime`, `prepare`, `submit`, `poll`, `status`, `download`. They share the exact [Motion schemas](../sprite_workbench/motion_services.py) as `local.motion.*` in JSONL and HTTP. Preparation/status and supplied-video operations are local. Only explicitly enabled Submit/Poll/Download may execute native provider operations. Plans always disable paid execution even when their controller enables standalone calls. Reopening Prepare returns the actual retained attempt/task state and never resets a submitted packet. [Motion workflow, controls and limits](motion-pipeline-20261014/README.md).

Raw video HTTP upload uses `POST /api/motion/upload` with byte content, then an explicit `local.motion.decode` request. Download receipts must accompany decoding generated media; the browser retains their IDs across reload and detaches them when media changes. `GET /api/motion/media/EXTRACTION.mp4` serves only the admitted media for a typed extraction. Source PTS and authored sprite holds stay distinct.

The [local channel guide](local-replication/LOCAL-CHANNELS.md) defines persistent JSON Lines messages and replay/comparison evidence. `lab replay` also returns exit 2 for incomplete checks. `lab compare` can complete with unequal sequences or an unsupported review player; inspect `exact_sequence_match` and each side's `exports.formats`. A channel response envelope reports dispatch; its returned job has a separate status. `capabilities --domain local` without a bound host remains empty; use the running channel's `system.capabilities` to discover its actual local services.

Plans are `{ "version":1, "name":"optional", "steps":[...] }`. Each step has a unique bounded `id` and an `action`. References use `{"ref":"previous_step.result_field.0"}` and resolve only prior results. The plan is detached/frozen before execution. Artifact IDs are complete SHA256 values. Relative paths resolve beside the plan file. Durations are rational seconds `[numerator,denominator]`, indices are zero-based in sequence/scene data and **one-based** in pixel-edit `frames`. Crop coordinates are inclusive pixel bounds.

| Action | Arguments beyond `id`/`action` | Primary result |
|---|---|---|
| import | path | sequence, rasters, source_bytes, poster_raster |
| prepare | sequence **or** rasters, adapter, options | sequence, raster_ids, reference_ids, mask_id, audit_id, geometry |
| edit | sequence, changes | sequence, revision, audit |
| scene | scene | sequence |
| tracks | scene, tracks, frame_count, fps, direction, pivot | sequence, track_audit |
| effects | recipe, subject, images | sequence, streams, recipe |
| pixellab_vfx | recipe, values, subject, images, timeout | sequence, streams, recipe, control_receipt, control_hashes, provenance |
| compose | body, back, front, duration, loop | sequence |
| export | sequence, directory, formats, allow_unsupported_formats | format-specific report |
| review | sequence, directory | review packet report |
| pose | joints, direction_degrees, tilt_degrees, profile | pose, artifact |
| terrain | cells, layout | terrain, sequence |
| ui | pieces, canvas | sequence |
| font | path, characters, size, columns | atlas, font_info |
| text | atlas, text, canvas, baseline, fallback | sequence |
| visemes | text, visemes, letter_map, durations, fallback, direction | sequence |
| candidate | artifact, source_id | candidate |
| promote | candidates, name, entity_kind, directions | entity |
| publish | head, artifact, expected | published, artifact |
| construction | method, request | Method-specific project/history/sequence/exchange result |
| studio | method, request | Explicit supplied-sequence import, verification or checked export |
| selection | method, request | Recovered manual raster/cel mask, guarded edit or mask export |
| motion | method, request | Native admission, explicit sampling/conditioning/retiming or offline preparation/status; paid execution disabled in plans |

Optional arguments/defaults and nested grammars are defined in [methods](METHODS-API.md), [raster/effects](RASTER-AND-EFFECTS.md), [scene/export](GEOMETRY-EXPORT-REVIEW.md), [state services](STATE-SERVICES.md) and `examples/supplied-motion/plan.json`. Unknown step arguments fail. Trusted protection policy must use the explicit raster/scene API; an invented plan `protected` field is rejected rather than silently ignored. Tracks support linear/smoothstep/hold numeric transforms and hold-only discrete cels, masks, ownership, order and visibility. Endpoint art is supplied, not generated.

Direct plans execute sequentially. A successful explicit `publish` or `promote` step persists even if a later step fails; the whole plan is not one rollback transaction. Put publication after the checks when using direct plans. Candidate-only queued plans forbid these steps and use the manager's guarded completion instead. Immutable candidates/export files can remain for inspection after failure or cancellation.

`register_pipeline_job(manager, base_dir=..., result_ref='compose.sequence')` registers a trusted candidate-only runner. Submit `{'plan': plan}` using the durable JobManager. Host configuration chooses the base directory/result. The job runner checks cooperative cancellation/progress between steps and disallows `publish`/`promote` inside jobs; guarded manager publication happens only on eligible completion. An already-running subprocess cannot be force-canceled by this cooperative mechanism, and candidate files may remain for inspection. Explicit library promotion happens after completion. This is local scheduling policy, not a recovered vendor scheduler.

For example, this plan imports supplied pixels and renders the same supplied frame sequence through the construction model. It does not create motion:

```json
{
  "version": 1,
  "steps": [
    {"id":"source","action":"import","path":"source.png"},
    {"id":"project","action":"construction","method":"from_sequence",
     "request":{"sequence":{"ref":"source.sequence"}}},
    {"id":"render","action":"construction","method":"render",
     "request":{"project":{"ref":"project.project"},"animation_id":"clip"}}
  ]
}
```

## Original PixelLab VFX methods

`pixellab-vfx METHOD REQUEST_JSON` accepts a JSON request file and invokes the same four source services as the browser and JSONL. No provider credentials are needed. `describe` reads original family/common descriptor tables and ramps; the HTTP source catalog additionally includes the two authentic retained presets with provenance.

| Service | Request |
| --- | --- |
| `local.pixellab.vfx.describe` | `{}` |
| `local.pixellab.vfx.validate` | `{"recipe": {...}}` |
| `local.pixellab.vfx.controls` | `{"recipe": {...}, "values": {"declared_control_id": value}}`; values optional |
| `local.pixellab.vfx.render` | `{"recipe": {...}, "values": {...}, "subject": "RASTER_ID", "images": {"name": "RASTER_ID"}, "timeout": 60}`; only recipe required |

`controls` returns declared controls, raw declared recipe, normalized and applied previews, and recipe/control/value hashes. `render` returns stored sequence/stream IDs, original-source provenance and a control receipt linked into editable export. The original renderer applies controls once using the raw declared recipe. Normalized or applied previews must not be fed back as renderer input; source normalization inserts values its input validator can reject, and mul/add binds would apply twice.

For durable asynchronous rendering, submit `local.jobs.submit` with `{"handler":"local.pixellab.vfx.render","request":{"recipe":{...},"values":{...}}}`, then poll `local.jobs.get` using the returned job ID until terminal state. A completed output retains `metadata.source_result`. A plan step uses `{"id":"effect","action":"pixellab_vfx","recipe":{...},"values":{...}}` and accepts the same optional subject/images/timeout fields. Direct CLI and plan calls execute synchronously; the job service supplies background scheduling.

The source catalog at `GET /api/pixellab/source` contains `slash_arc` and `energy_orb`, their authentic retained response hashes and exact recipe objects. The dedicated browser panel exposes their sliders and ramps, recipe JSON loading/download, job status, frame playback/scrubbing, recent completed source results and handoff to the separate local editor. [Source workflow](source-faithful/SOURCE-UI.md) and [verification](source-faithful/VERIFICATION.json) record scope. Seventeen procedural families do not establish all prepared constructors, private models or full PixelLab parity.

## Persistent JSON Lines channel

The `channel` subcommand is a trusted child-process protocol over stdin/stdout. It emits a `ready` event, then accepts one JSON object per line:

```json
{"id":1,"method":"system.capabilities"}
{"id":2,"method":"local.construction.get","params":{"project":"FULL_64_HEX_PROJECT_ID"}}
{"id":3,"method":"local.jobs.submit","params":{"handler":"local.pipeline","request":{"plan":{"version":1,"steps":[{"id":"source","action":"import","path":"source.png"}]}}}}
{"id":4,"method":"local.jobs.get","params":{"job_id":"RETURNED_JOB_ID"}}
{"id":5,"method":"system.shutdown"}
```

`system.ping`, `system.capabilities` and `system.shutdown` accept no parameters. Bound `local.pixellab.vfx.*`, `local.jobs.*`, `local.library.*` and `local.construction.*` schemas are authoritative. Requests are limited to 4MiB. Relative paths resolve under `--base-dir`, but this trusted channel does not confine filesystem access to that folder. Its `--result-ref` selects the plan output, for example `render.sequence`. Use the [full caller example](../examples/local-channel/client.py) for returned-ID handling.

## Local browser and HTTP controls

```bash
.venv/bin/python -m sprite_workbench --workspace workspaces/web-control/store web \
  --base-dir workspaces/web-control/files --port 8874 --workers 2
```

The server binds `127.0.0.1` only; `--port 0` chooses an available local port and the ready event reports its URL. Workers must be 1..8. Start only one manager per Store. Open the printed URL to obtain same-origin controls. The server does not publish the project or invoke a vendor.

Unlike the trusted CLI/channel, browser file operations must remain under the configured base directory. Upload external inputs first. Path checks apply again after plan references are resolved and when persisted queued work resumes. These checks are a local controller boundary, not an operating-system sandbox or a promise about hostile concurrent filesystem changes.

| Method and route | Request or result |
| --- | --- |
| `GET /api/bootstrap` | Current session nonce, workspace paths, readiness and actually bound capability definitions |
| `GET /api/readiness` | `setup_ready`, `comparison_ready`, source fingerprint, checks, blockers and verification status |
| `GET /api/pixellab/source` | Original descriptor tables/ramps, two authentic retained preset recipes, source hashes and render job handler |
| `GET /api/catalog` | All reconciled requirements, feature/transport flows, commands, grammar, interfaces and current API drift |
| `GET /api/jobs` | Up to 100 recent durable job records |
| `GET /api/project/PROJECT_ID` | Full validated editable project and canonical project hash |
| `GET /api/artifact/ARTIFACT_ID` | Stored JSON artifact |
| `GET /api/raster/RASTER_ID.png` | Exact stored raster encoded as PNG |
| `POST /api/upload` | Raw PNG/APNG bytes up to 32MiB, or raw editable project JSON up to 16MiB; returns stored identities |
| `POST /api/invoke` | `{"method":"local.METHOD","params":{...}}`; dispatches only an implemented local service |
| `POST /api/plan` | `{"plan":{...}}`; structurally validates and stores the declaration without executing it; returns its artifact ID |
| `POST /api/verify` | `{}`; queues or returns the active `local.readiness.verify` setup job |
| `POST /api/compare` | Returns409 with blockers; no original-art/model comparison executor is configured |

POST control bodies are finite JSON objects up to 4MiB with `Content-Type: application/json`, except raw uploads. Mutating requests need the current `X-Workbench-Token` from bootstrap and an accepted loopback Host/Origin. The browser supplies this automatically. This temporary local nonce is not a PixelLab credential. No cross-origin control or vendor forwarding is provided.

To submit a stored plan in Jobs, the client first loads its artifact, extracts the `plan` object and calls `local.jobs.submit` with `handler:"local.pipeline"` and `request:{"plan":...}`. Sending only the artifact ID is not the handler's grammar. Without an explicit host result reference, the web runner selects the last returned sequence, or the run receipt if no step returns a sequence.

HTTP 200/`status:completed` acknowledges dispatch, not successful job completion. Inspect the returned job/candidate state and output classifications. Validation/unsupported inputs return 400, forbidden local requests 403, unresolved comparison 409, timeout 408, and exhausted request capacity 503. File outputs and immutable rejected candidates can remain after failure.

Source changes require a controller restart before setup verification or queued plan execution; the worker repeats that check during execution. A valid source-bound setup proof cannot erase any original analysis, grammar or implementation blocker. The separate CLI `lab compare` computes equality/differences between existing supplied artifacts; it does not authorize new experiments or contact a model.

Exports preserve existing directories. `play_count` is0..65536:0 infinite,1 once,N total plays; `loop` is true only for0. Exact rational manifests/PNGs remain valid when a preview cannot represent the clock. APNG requires16-bit fraction fields; browser/Godot playback requires finite positive float holds and non-collapsed boundaries. GIF requires binary alpha and at most255 visible colors, with explicit centisecond rounding/error. No default silent matte, quantization or frame coalescing is applied.

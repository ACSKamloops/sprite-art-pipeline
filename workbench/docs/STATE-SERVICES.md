# Local jobs, library and capability services

These are implemented local policies, not PixelLab cloud handlers. They preserve explicit supplied art and source/version metadata; there is no provider transport, credential loading, account accounting or implicit model availability.

## Jobs

```python
from sprite_workbench.jobs import JobManager, JobResult

with JobManager(store, workers=4, max_pending=256) as jobs:
    def supplied(request, context):
        context.check_cancel()
        context.progress(0.5, {"phase": "prepared"})
        artifact = context.store.put_json({"kind": "diagnostic", "input": request})
        return JobResult(artifact, result_status="candidate")

    jobs.register("supplied.diagnostic.v1", supplied)
    job_id = jobs.submit("supplied.diagnostic.v1", {"source_id": source_artifact},
                         head="accepted-diagnostic", expected=previous_revision)
    report = jobs.wait(job_id, timeout=30)
```

Requests must be finite JSON objects up to4MiB; image/sequence content belongs in immutable Store artifacts referenced by IDs. Known credential keys are rejected. At admission the canonical request envelope becomes a SHA256 artifact. The handler receives a detached JSON copy, so later caller mutations and handler-local mutations cannot alter the recorded input. Callers should include exact source/adapter versions in request or job metadata; the engine does not pretend that an arbitrary Python callable or its ambient globals are immutable.

`register(name, handler)` registers a trusted `(request, context)` callable. `context.store`, `check_cancel()` and `progress(fraction, detail_dict)` are available. Progress is finite0–1 and monotonic; durable events precede advisory callbacks. Callback exceptions are recorded by exception type and do not turn completed work into failure. Callbacks are process-local and are not replayed after restart.

`submit(name, request, *, head=None, expected=None, on_progress=None, metadata=None)` returns an opaque job ID. `get`, `request`, `events`, `list(status=None, limit=100, offset=0)`, `wait`, `cancel` and `retry` expose durable state. Job IDs are opaque UUID strings; request/result/revision IDs are SHA256 artifact identities. Queue admission includes queued/running/cancel-requested work. Each manager has1–32 bounded worker threads and one nonblocking Linux workspace lease. A second live manager for the same Store is rejected.

| Lifecycle | Meaning |
|---|---|
| queued / running / cancel_requested | Durable accepted local work, not cloud processing. |
| completed | Handler result was validated and committed; this does not mean visually approved. |
| stale | Head differs from the submission's expected revision; result remains quarantined. |
| cancelled | Queued cancellation or completed cooperative/late cancellation handling. |
| interrupted | Previous manager/process stopped before terminal commit; no automatic rerun. |
| validation_error / unsupported / technical_failure | Distinct terminal failures; no implicit successful candidate conversion. |

Results are an existing artifact ID or `JobResult(artifact_id, result_status="candidate", metadata={})`. Classifications are candidate, technically_verified, visual_unreviewed, visually_approved, visually_rejected, technical_failure or validation_error. They are explicit caller classifications, never inferred from a score. Technical/validation failures and visually rejected results retain their bytes in `outputs` with `disposition=quarantined`, and never update a head. Visual rejection can coexist with a technically completed job. Default success remains a candidate.

The final cancellation/ownership check, head compare-and-swap, output disposition and terminal job state commit in one SQLite transaction. Without a head a valid successful artifact is retained as a candidate. `library:entity:` heads are reserved for Library operations. Duplicate retry requests for one parent return its existing child, even after completion; retry a failed child for the next attempt. Retrying preserves the parent's immutable request and expected head. A stale retry does not silently adopt a newer revision: make a new explicit submission if that is intended.

`close(wait=True, timeout=5)` stops admission/claims and allows active handlers a bounded grace period. Remaining active work becomes interrupted before the lease is released. Cancellation cannot force-kill Python code. Ignoring cancellation can consume a worker until the handler returns; its late result is quarantined. After process death the OS releases the lease; a new manager marks abandoned active rows interrupted and resumes queued rows after their named handlers are registered. Artifact creation can leave safe orphan candidates; the Store deliberately preserves them.

Handlers must produce immutable artifacts and return them. Direct head/library mutations or other external side effects inside a handler bypass its guarded terminal publication and are outside this contract. Registered callables are trusted code, not a sandbox. The module itself performs no network/credential operations.

## Supplied-art library

```python
from sprite_workbench.library import Library

library = Library(store)
candidate = library.create_candidate(raster_id, source_id="frame_10")
entity_id = library.promote([candidate], name="supplied object",
                            directions={"south": candidate})
entry = library.get(entity_id)
revision = library.set_state(entity_id, "outfit", expected=entry["revision_id"])
revision = library.set_animation(entity_id, "outfit", "walk",
                                 {"south": sequence_candidate}, expected=revision)
```

`create_candidate` requires an explicit RGBA/sequence artifact for normal candidates. Validation, technical and visual status fields remain independent. Failure candidates may retain an artifact or no artifact. `record_review` creates a new immutable candidate document and retains its parent identity; it does not mutate the original. Failed/rejected candidates cannot be promoted. Sequence clocks, pivots, explicit labels and frame indexes are checked; no missing pose/direction is inferred.

`select(candidate_ids, source_ids)` resolves exact source identities such as `frame_2` versus `frame_10`, never array positions or lexical ordering. `promote` requires unique candidate artifact IDs and optional explicit direction-to-candidate mapping. Unlabeled output positions never become cardinal directions. A stable entity ID is its initial immutable document ID; the current revision is separate. `get` returns `{entity_id, revision_id, document, deleted}`. Direction records retain candidate, artifact, source and review identities.

Mutations require `expected=revision_id` and raise `StaleRevision` on conflict. `set_direction` changes an explicit source direction. `set_state` merges supplied direction records and preserves that state's animations. `set_animation` requires sequence candidates and merges supplied direction records; `replace=True` explicitly replaces the group's direction mapping. Each sequence retains its own frame count, duration, pivot, loop and duplicate frames. There is no common inferred FPS.

`remove_animation(..., direction=None)` removes a group or one direction; removing its last direction removes the empty group. `remove_state` removes its animations too, but leaves entity reference directions. `remove_direction` affects entity references only. `archive(..., archived=True)` filters ordinary listings without discarding art. `delete` publishes a tombstone, not blob deletion. `restore(entity_id, revision_id, expected=...)` restores a retained revision from that same entity. `list(entity_kind=None, include_archived=False, include_deleted=False, limit=100, offset=0)` reads one page's revision identities in a single query; separate pages do not promise a server-style snapshot. Individual entity reads use a SQLite read snapshot.

These local SQLite transactions do not claim vendor grouping, URL lifetime, cloud retention, promotion atomicity or remote undo behavior. Raw artifact bytes and immutable history remain in Store.

## Capability registry

`CapabilityRegistry(contract_dir=None)` checks the original OpenAPI hash and exact111-operation projection, and retains all101 captured MCP schemas and source identities. Default contracts are bundled at `sprite_workbench/contracts/`; `contract_dir` permits an explicit supplied snapshot. Bundled and repository snapshots are checked for byte identity. `describe(id)` and `list(domain=None)` return detached metadata. There are212 vendor definitions and zero implemented vendor handlers. Local analogue hints are pointers to separately named methods, not endpoint aliases.

`validate_request(id, request)` validates captured JSON body/tool schemas with jsonschema/referencing and an in-memory URN registry. It applies no defaults or coercion, performs no HTTP, and rejects external schema references. URL/path/query parameters and semantic provider validators are separate; a schema pass does not establish vendor acceptance. `invoke(vendor_id, request)` always raises structured `UnsupportedCapability`.

`bind_jobs(manager)` registers `local.jobs.submit/get/list/cancel/retry/wait`. `bind_library(library)` registers actual candidate/get/list/promote/direction/state/animation/removal/archive/delete/restore methods. `register_local(name, callable, classification=..., request_schema=None, evidence=None)` adds explicit trusted local functionality. Supported classifications are supplied-art, deterministic-source and local-substitute. Without a formal local request schema, the finite JSON boundary plus the called method's validation applies; this is not a claim of full schema validation. No local service is registered under a vendor ID.

## Verification

`python3 -m pytest -q tests/test_state_flows.py` passes13 cases. F04 covers supplied directions, sequence jobs with different clocks/counts, duplicates, state/group reload/removal, tombstone/restore and malformed clock/type guards. F05 covers actual suffix identities, explicit promotion, missing directions, stale revision rejection and independent failed/rejected candidate status. F11 covers immutable requests, bounded workers/admission, queued/in-flight cancel, late quarantine, CAS stale publication, downloadable technical failures, retry idempotence, callback errors, a real process interruption/restart and queued resume, manager exclusivity, exact212-definition accounting, offline schema validation and separately bound services.

These tests cover the implemented local state portion of F04/F05/F11. Root's integrated suites must still join preparation, inspection/export and UI paths. They do not test PixelLab account/poll403 behavior, cloud upload expiration, provider billing, browser workers, neural quality, art generation or visual acceptance.

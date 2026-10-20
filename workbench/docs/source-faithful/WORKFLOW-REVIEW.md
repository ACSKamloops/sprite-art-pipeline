# Adversarial review of recovered-source workflow integration

Reviewed backend snapshots: `50376cc`, then corrected `1316d73`. Review changes are confined to this report
and `tests/test_source_workflow_adversarial.py`; runtime files were not edited.
Source recipes used here are the two authenticated retained preset responses,
with bounded mechanical mutations solely for rejection tests. No providers,
paid requests, new character tests, or replacement generation algorithms ran.

## Corrected finding: source pipeline action was unreachable

At `50376cc`, `sprite_workbench/pipeline.py` contains the `pixellab_vfx` dispatch
branch and allowed arguments, but omits the action from `SUPPORTED`. Both plan
validation in `execute_plan` and HTTP `/api/plan` reject it before that branch.

Reproduction: submit a version-1 plan with one step containing
`{id: "source", action: "pixellab_vfx", recipe: <retained slash_arc recipe>}`.
`POST /api/plan` returns HTTP 400. The intended source rendering and associated
control receipt are never produced. This blocks the newly advertised pipeline
entry point; direct HTTP and CLI source rendering work.

Regression: `test_http_pipeline_action_uses_same_source_and_portable_receipt`.
The integration owner corrected this in `1316d73` by including `pixellab_vfx` in
`pipeline.SUPPORTED`. The full regression now passes through real HTTP plan
admission, queued execution, original rendering and source control receipt checks.
This review did not edit runtime code.

After merging `1316d73`, the full review suite passed:

```text
/home/astra/projects/pixellab-local-workbench/.venv/bin/python -m pytest \
  tests/test_source_workflow_adversarial.py -q
23 passed in 14.47s
```

## Read-only browser-script review at `1316d73`

One blocking UI defect was reported to the integration owner:
`source-vfx.js` assigns `this.job = job.job_id || job.id`, but the actual
`local.jobs.submit` response is a string ID (verified by the HTTP tests). The
assignment yields `undefined`, and JSON serialization drops the subsequent
`job_id` field from `local.jobs.get`; rendering cannot proceed to displayed
results even though the admitted backend job can complete. Existing `app.js`
submission code already handles the string case. The source UI needs the same
response-shape handling. This finding is independent of the now-green backend
suite; browser acceptance remains the integration owner's work.

Qualified resolution at `7bb25d9`: the reviewer inspected that commit's source
diff. It handles string job IDs directly, retains object-ID compatibility, and
rejects a missing ID before polling. The integration owner then ran the actual
browser. The reviewer read, but did not independently execute, that browser run's
retained `output/playwright/source-slash-result.log` in the root checkout. Its
SHA-256 is `9317661728124db23f7f7f9273ec77f6353bf7c6ef3724461ffea548aec89a7a`.
The recorded result says seven frames decoded at 96 × 96, with an empty error
and `errorVisible: false`. The sequence recorded in both the UI status and parsed
result is
`0e6102e68294db753681aa4b01159648c88c39c6c9dbf64708873dc152fa6873`.

The reviewer separately read the root Store's immutable files, without opening
or mutating its database. The sequence blob hashes to that ID, declares canvas
`[96, 96]` and seven frames, and retains `visual_approval: unreviewed`. All seven
referenced raster descriptors pass their content hashes. Its source-control
receipt hashes to
`3bb40c58a5660586c55f1f5263b8742e0ea3f57204c8eb66f0fb2e3c6f7086c0`,
matches the sequence metadata, and identifies declared recipe hash
`a10a04f31aa54c7ca79505f5542f0ab488f616e5ca1516d7afad0a09f7653f18`,
the pinned authentic `slash_arc` recipe. Thus source inspection and retained
browser evidence resolve the reported string-ID defect for this case. They do
not establish full visual approval, mobile acceptance, all control variations,
or playback/save behavior; those remain separate integration-owner checks.

Other inspected UI boundaries are faithful: rendering sends the raw editor recipe
and a separate values object; downloading uses backend `declared_recipe`; controls
are obtained from original declarations rather than invented sliders. The UI
passes values to the backend without implementing original bind expressions,
scaling, easing, RNG, or rendering algorithms. Playback arithmetic concerns only
the retained rational frame clock. `readControls` uses a settings epoch to ignore
stale responses; decoded previews use a separate preview epoch so later preview
requests supersede earlier ones. Render results retain the submitted job's output
and disclose settings edits that happened while it ran. Toggle/select controls
are explicitly labelled unexposed and directed to Methods; this UI is not a claim
that every original control widget has been reproduced.

## Verified behavior and evidence

The remaining 22 tests passed on the frozen snapshot in 13.89 seconds:

```text
/home/astra/projects/pixellab-local-workbench/.venv/bin/python -m pytest \
  tests/test_source_workflow_adversarial.py -q -k 'not pipeline'
22 passed, 1 deselected
```

Coverage includes:

- Real loopback HTTP describe, validate, controls, render; raw declared recipes
  stay raw, normalized `rng: null` remains a readonly preview, and render receipts
  match the declared input and original control application.
- Twelve malformed render request shapes, unknown arguments/controls/families,
  invalid timeout, source canvas exceeding the local render profile, invalid
  frame count, and missing subject. Every rejection leaves the blob inventory,
  heads and job inventory unchanged.
- Private and unregistered method calls return unsupported and create no jobs
  or artifacts; no fallback handler executes.
- Actual original-source job completion and invalid-source failure survive a
  controller restart. Cancelled queued jobs remain unpublished; retry after
  restart is durable and idempotent, runs the original source, and publishes only
  the successful retry's artifact.
- Drift after controller boot blocks synchronous source calls and the catalog;
  a queued job submitted through the generic jobs API fails its execution guard
  without generating artifacts beyond its explicitly retained request record.
- Running jobs paused immediately after real original rendering cannot publish
  after cancellation or source drift. Their already-computed immutable sequence
  may remain in Store; their job artifact, outputs and publication head stay empty.
  This is cooperative cancellation, not termination of an in-flight Node process.
- Editable export/import into a fresh Store preserves exact frames and the
  `pixellab_controls` receipt for all three streams. Recipe and renderer-manifest
  dependencies remain available after import.
- Both packaged preset recipes match the original retained response files,
  response hashes, exact decoded JSON-text hashes, canonical recipe hashes and
  existing captured recipes. Original request arguments contain no recipe input.
  The original raw-response check conditionally skips when the separate research
  checkout is unavailable; it executed successfully in this review.
- Actual CLI rendering of a retained recipe persists a source control receipt;
  an unsupported CLI method creates no additional Store blobs.

`git diff --exit-code 46257b3 -- sprite_workbench/vendor/vfx` produced no diff:
the recovered algorithm factories and their manifest remain unchanged from the
pre-integration baseline. Source hashes are also verified by the executing loader.

These checks concern local wrapper behavior and retained source provenance.
They do not establish visual approval, current private-server or MCP parity,
browser UI acceptance, or completion of broader source analysis.

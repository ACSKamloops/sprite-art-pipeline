# Read-only model handoff review

Reviewed `32ad1af` backend through UI snapshot `93646f4`. Runtime files were not
edited. Checks used synthetic 4×3 supplied pixels, temporary Stores, local HTTP,
and immutable export/import. No model, provider, agent, credential or art calls
ran. Prior review branches remain preserved.

## Blocker: comparison eligibility does not bind actual execution to its task

`model_handoff.py::audit_pair` considers selected task executor IDs sufficient to
establish different orchestrators. It ignores the attested `orchestrator_model`
and tool identity. It also has no actual submitted image inventory or settings
attestation to check against the frozen conditioning. Matching brief IDs and
prompt strings therefore establish intended inputs, not actual submitted inputs.

Concrete reproduction, executed in a temporary Store:

1. Prepare one still brief with a subject raster and both executor IDs.
2. Import one synthetic PNG without transformation.
3. Ingest it for each task as `external-generation`, explicitly supplying the same
   `orchestrator_model: "the-same-agent"`, the same unrelated tool name, exact
   per-packet prompt, and two different image providers/models.
4. Audit the two receipts with `scope: "orchestrator"`.

Observed: `comparison_eligible_by_attestation: true`, although the actual supplied
attestations name the same agent and confounded image backends. No false provider
execution occurred; these were intentionally synthetic contradictory attestations.

The existing receipt boundary correctly says execution metadata is unverified,
but eligibility should at least be internally consistent with that metadata.
Require explicit matching actual prompt and input bytes/order/roles, require an
actual executor/tool/orchestrator identity consistent with the selected task, and
surface settings mismatches. Unknown actual conditioning should be ineligible,
rather than assumed equal. For an isolated orchestrator comparison, require the
same known image provider/model and flag differing image parameters. If broader
route comparisons are desired, name that scope separately and expose its
confounds. The image-backend scope should likewise require known actual distinct
image identities, with shared conditioning; different orchestrator choices are
not proof of different image models.

These checks are consistency checks on caller-supplied evidence. They do not
authenticate private generation or prove a provider consumed its inputs.

## Exact prompt preservation defect

`web/model-lab.js::brief` trims the prompt before freezing it. Leading/trailing
spaces or blank lines are lost, contrary to the catalog's promise to retain exact
user text. The backend itself preserves these bytes and hashes the original
string. Keep the raw editor value; use a trimmed copy only to reject blank input.
No prompt enhancement or rewrite algorithm is otherwise present.

## Handoff download limitation

The UI's Download Packet emits only JSON, whose draft references relative
`inputs/*.png` files. Those files are emitted by `export_packet`, but the browser
download does not include them. Label this download as a manifest only and direct
the user to complete folder export, or provide the actual input files together.
The backend full-folder export works as a distinct preparation operation; neither
form authorizes or executes a model.

## Verified boundaries

- Nonempty typed hard controls are rejected before preparation writes; unsupported
  tasks/roles/unknown fields are closed by registry schemas. Masks, seeds, joints,
  clocks and enforced size are not silently converted into claimed model inputs.
  Desired size/transparency are explicitly inspectable requests, not guarantees.
- The prompt appendix is deterministic and visible, identical for both tasks.
  Input role/order survives the task and packet; edit target must occupy slot zero.
  Hermes separates it into `image_url`, with other images in reference slots.
- The Hermes profile distinguishes MiniMax chat orchestration from the unselected
  image provider. Preparation does not inspect credentials, configure a provider,
  launch an agent or invoke a model. Static source inspection found no such call
  path in this module or its UI; HTTP exposes preparation/import/audit only.
- External ingest requires a single-frame original encoded file and independently
  decodes it, checking frame count, canvas and exact decoded RGBA against admitted
  pixels. It retains the original bytes and acquisition metadata. Origin/model
  assertions remain explicitly caller supplied; diagnostic kind is separate.
  All results remain unreviewed. This is not generator-origin authentication.
- Fresh-Store editable export/import was exercised: candidate → model result →
  raw sequence, task, brief → input raster/PNG and original output bytes all remain
  readable with hash validation. Experiment/result SQL indexes are not part of
  this artifact closure; restoring evidence is distinct from reconstructing the
  original experiment listing in a new Store.
- Real local HTTP returned 200 for catalog, 400 for nonexistent model execution,
  400 for `../outside` export, `unsupported` for a required mask in hard controls,
  and 400 after simulated source drift. These rejected requests and catalog lookup
  produced no Store blobs. Existing session-token/origin checks and source-current
  guard apply to `local.models.*`; export paths stay under the configured base.

The implementation is useful held preparation and byte-preserving import. It
should not claim a fair attested comparison until the execution-binding gap is
closed. Model availability, actual auth, output quality, reference adherence and
cross-model results remain untested.

## Recheck at `3b2d8b1`

The original `93646f4` failure above is preserved as the baseline. Source
inspection of `3b2d8b1` and its bounded selected tests confirm substantial fixes:
actual tool, transport, orchestrator provider/model, ordered input roles/hashes,
submitted controls and exact prompt are now checked. Missing attestations remain
unknown, and contradictory records remain importable as evidence but cannot
qualify. Orchestrator scope holds a known image provider/model fixed and requires
different known actual orchestrators consistent with the frozen task. Image scope
requires known distinct image identities. The eight new contradictory-attestation
regressions pass. The entire selected module test file passed:

```text
/home/astra/projects/pixellab-local-workbench/.venv/bin/python -m pytest \
  tests/test_model_handoff.py -q
32 passed in 1.93s
```

The UI now preserves raw prompt whitespace, labels JSON downloads manifest-only,
and offers a complete folder export. These were checked by source diff, without
claiming browser interaction acceptance. No original art algorithm or learned
cleanup was added by these changes.

One residual binding mismatch was reproduced and reported before sign-off:
the Codex profile freezes `image_provider: "OpenAI"`, but an otherwise bound
synthetic receipt can attest `image_provider: "impossible-other-vendor"`. Pairing
it with the Hermes task's separately attested OpenAI output/different model returns
`task_bindings_match: true` and image-backend eligibility `true`. Actual image
provider identity is used for distinctness but is not compared with a known
frozen profile image provider. Add that consistency check wherever a provider
identity is actually evidenced; unknown identities must remain unknown, not
create a nominally supported new backend. This reproduction used only temporary
synthetic PNGs and attestations, not generation.

A future third backend must supply an actual capability/transport/conditioning
mapping and provenance. Loosening a profile ID or adding model-name strings is
not evidence that arbitrary models consume these inputs or support these controls.
All binding data remains executor-attested, not provider-authenticated; a passing
mechanical comparison does not authorize model execution or certify art quality.

## Narrow provider recheck at `e7a6a6c`

Source inspection confirms the impossible-vendor mismatch is now checked against
the known frozen vendor, including the Hermes plugin's explicitly configured
vendor. Missing actual/expected vendor remains unknown. The nine contradictory
attestation cases plus the positive/same-model case passed: 10 selected tests in
0.92 seconds, with 23 unrelated tests deselected. No broader suite was rerun by
this reviewer.

A final case-normalization inconsistency was reproduced: fully bound Codex and
Hermes records attesting `OpenAI` and `openai`, respectively, with the same image
model, pass vendor binding because it casefolds names. `audit_pair` still compares
raw vendor strings, incorrectly marking image-backend scope eligible and
orchestrator scope ineligible. Compare canonical vendor identities consistently
while retaining raw attested names for display; model-name case must follow the
provider's actual naming rules. This bounded synthetic counterexample was sent
to the integration owner before final closure.

## Final bounded closure at `f82b2f4`

The owner fixed the case-normalization inconsistency by comparing canonical
casefolded vendor identities for both same-model and distinct-model decisions,
while retaining raw attested identity strings for display. Model-name spelling
is preserved. The existing same-model regression now explicitly pairs `OpenAI`
with `openai`: image-backend scope is ineligible, while correctly bound distinct
orchestrators using that same known image model remain eligible by attestation.

The reviewer inspected the source diff and reran only the narrow positive and
counterexample selection on `f82b2f4`:

```text
/home/astra/projects/pixellab-local-workbench/.venv/bin/python -m pytest \
  tests/test_model_handoff.py -q \
  -k 'vendor_case or contradictory_or_missing_execution_attestations or diagnostics_and_unknown_or_same_image_models'
10 passed, 23 deselected in 0.88s
```

All reported comparison-binding, exact-prompt and manifest/folder-export findings
are resolved within this inspected scope. No additional runtime issue was found
in this final bounded recheck. These are consistency checks on supplied receipts,
not authenticated model execution, actual provider availability, visual approval,
or an assertion that arbitrary future image backends support this conditioning.
No broad suite, provider, agent, credential or model calls were run by the reviewer
in this closure. Runtime source was not edited in the reviewer checkout.

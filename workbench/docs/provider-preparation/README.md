# Interchangeable image-workflow preparation

Open the [local Model lab](http://127.0.0.1:8874/#models). It freezes the same
instruction, ordered reference pixels and requirements into two explicit task
handoffs: the built-in Codex image tool and the Hermes/MiniMax agent's separate
image tool. Preparing, exporting, importing and auditing make no model calls.
This is our host protocol, not recovered PixelLab inference code. The unchanged
[PixelLab procedural source workflow](../source-faithful/SOURCE-UI.md) stays separate.

The preparation layer is implemented and mechanically verified. Live model
execution, Hermes image-provider selection and quality comparisons remain held.
The built-in tool is available to this Codex session, but is not an HTTP service
the local web server can invoke. Hermes is configured for MiniMax chat, while
its image provider is unselected. An installed Codex-auth image plugin supplies
an explicit possible image route; its live availability/entitlement is untested.
[Hermes discovery](HERMES-READONLY.md). User shorthand “H3” means that agent setup.

## Operate the preparation layer

1. Import supplied reference files in Workspace or with `sprite-workbench import`.
   Retain the returned raster IDs and original file bytes. The Model lab input
   list uses existing **raster** IDs; returned result admission uses a **sequence** ID.
2. Choose still generation or semantic editing. Enter the exact instruction,
   desired size and transparency preference. Supply ordered roles `subject`,
   `style` or `edit_target`. An edit requires exactly one edit target in slot 0.
   Preparing tasks retains whitespace and the original prompt hash.
3. Prepare paired tasks. Both retain one brief ID. Inspect the complete draft
   prompt, including its visible output/role appendix, and the backend mappings.
   The same draft text is used for both routes; there is no hidden enhancement.
4. Download a JSON **manifest**, or use **Export inputs + manifest** to write a
   complete absent/empty folder inside the configured workspace. The folder
   contains `packet.json` and exact lossless reference PNGs. A manifest download
   alone does not include those files. Re-exporting never overwrites existing work.
5. Later, after experiment prerequisites are settled, an authorized agent can
   execute the selected handoff through the real tool. This UI does not launch
   either agent, forward provider requests, or authorize execution by itself.
6. Import the untouched returned image file; attach its sequence to the selected
   task with actual execution metadata. External results require original encoded
   image bytes that decode to the admitted pixels. Supplied diagnostics must be
   labelled `supplied-diagnostic` and cannot claim model execution.
7. Audit two receipts from the same frozen brief. Inspect native dimensions,
   alpha and exact pixel changes before any explicit editing or conversion.
   Outputs remain unreviewed. The audit supplies no aesthetic score or ranking.

The current shared contract covers **one still image or one semantic edit**.
Multi-frame output is rejected. Animation, interpolation, typed joint inputs,
exact edit-mask guarantees, seeds and enforced native pixel dimensions are
unsupported here. An animation sheet is never silently split into frames.
Requested size is prompt-only. Codex exposes a transparency parameter; the
inspected Hermes route expresses transparency in the prompt. Neither is a claim
about observed output alpha until the file is checked. No automatic resizing,
quantization, background removal, alignment or invented craft algorithm runs.

## Local API and agent channels

The same services are available through the browser, persistent JSON Lines and CLI:

```bash
.venv/bin/python -m sprite_workbench --workspace workspaces/my-test/store \
  models catalog catalog-request.json
.venv/bin/python -m sprite_workbench --workspace workspaces/my-test/store \
  models prepare prepare-request.json
```

`catalog-request.json` contains `{}`. A preparation request has this local schema:

```json
{
  "brief": {
    "version": 1,
    "task": "still",
    "prompt": "The exact user-owned image instruction",
    "inputs": [],
    "requirements": {"transparent_background": true, "desired_size": [256, 256]},
    "hard_controls": {}
  },
  "executors": ["codex.imagegen", "hermes.image_generate"]
}
```

Supported `models` subcommands, with corresponding `local.models.*` services:

| Method | Required request fields | Result |
| --- | --- | --- |
| `catalog` | none | Explicit profiles, capabilities, unknowns and held execution |
| `prepare` | `brief`, `executors` | Immutable brief, experiment and prepared task IDs |
| `packet` | `task` | Draft tool call, reference inventory, prerequisites and limits |
| `export_packet` | `task`, `directory` | Complete folder; paths stay inside configured base |
| `ingest` | `task`, `sequence`, `execution` | Raw-image receipt, observed geometry/alpha and unreviewed candidate |
| `results` | `experiment` | Retained results for the frozen experiment |
| `audit_pair` | `left`, `right`, `scope` | Full native-canvas technical evidence; no art approval |

There is no `execute` method. CLI request paths resolve relative to the request
file for bounded export. In JSON Lines use the normal
`{"id":1,"method":"local.models.prepare","params":{...}}` envelope.
Methods exposes the complete closed JSON Schemas; unknown fields are rejected.

## Record actual execution, not inferred identity

Keep the orchestrator provider/model separate from the image vendor/model and
transport. For example, Hermes can use a MiniMax agent to call an OpenAI image
plugin. That is not evidence that MiniMax synthesized the pixels. Requested model
tiers, plugin defaults and chat model names must not be copied into the reported
image-model field unless the actual execution evidence supports that identity.
Use null for undisclosed values.

`execution.kind` is `supplied-diagnostic` or `external-generation`. Optional
execution fields are `orchestrator_provider`, `orchestrator_model`, `image_provider`
(the model vendor), `image_transport` (such as `builtin.imagegen` or the installed
`openai-codex` plugin), `image_model`, `tool`, `actual_prompt`, `submitted_inputs`,
`submitted_controls` and a closed `parameters` object for reported settings.
References use `{slot, role, decoded_rgba_sha256}` in actual submitted order.
`submitted_controls` records actual mapped typed controls; the current Codex
packet has `transparent_background`, while the inspected Hermes packet has none.
Do not put credentials, raw headers or private account responses in receipts.

The host checks these attestations against the frozen task, retains unknowns,
and verifies original output bytes locally. It cannot independently authenticate
a caller's tool log. `comparison_eligible_by_attestation` reflects those bounded
consistency checks only; it neither proves a live execution nor opens the full
art/model experiment gate.

An **orchestrator** audit requires known different actual orchestrators and holds
a known image model fixed. An **image-backend** audit requires known distinct
image identities. Both require matching actual prompt, input hashes/order,
controls, tool/transport binding and canvas. Vendor-name capitalization does not
invent a different backend. Unknown models or missing submission evidence remain
inconclusive. Aliased model IDs and hidden deployed weights are not resolved by
this protocol, and matching seeds never establish cross-provider determinism.

## Add a genuinely different generator

A new adapter needs actual capability evidence, a distinct profile and explicit
packet-field mapping, truthful supported controls, result identity and admission
checks, and rejection tests for unsupported conditioning. It must preserve the
same neutral brief and raw result, and pass fresh-Store portable receipt checks.
The current two routes do not establish arbitrary-provider support or two
different underlying image models. The required Hermes image plugin is a proposed
configuration; the active configuration was deliberately left untouched.

Before new art comparisons, freeze a scoped test protocol and settle the remaining
analysis/runtime prerequisites. Character animation additionally requires coherent
directional artwork, owned parts/hidden surfaces, authored poses and timing, and
adjacent-frame plus normal-speed independent visual review. A still import or
software pass cannot establish a useful walk cycle or 9/10 game art.

## Verification and retained failures

[Current verification](VERIFICATION.json) binds **560 tests at `f82b2f4`**, actual
browser handoff/export/import/audit interactions, desktop/mobile screenshots,
source-bound setup and an independently installed 0.6.0 wheel with 105 matching
runtime files. The checks use supplied diagnostics only; no new art or model calls.
[Installed proof](package/README.md), [adversarial review and corrected failure
history](../source-faithful/MODEL-HANDOFF-REVIEW.md), [initial source-evidenced protocol
proposal](../source-faithful/GENERATION-PROTOCOL-PROPOSAL.md).

The first browser automation attempt used an invalid select command, leaving an
edit target in a still brief; the server correctly returned 400. That attempt is
excluded from positive acceptance. The completed edit flow passed, and a fresh
tab reloaded both retained results with zero console errors/warnings. Raw retained
observations and their hashes are linked from the verification record. The
preceding 0.5 current handoff was preserved under `before-model-handoff-v0.6/`.

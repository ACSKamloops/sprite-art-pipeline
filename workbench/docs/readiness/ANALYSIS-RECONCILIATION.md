# Analysis reconciliation and exact remaining boundary

This pass accounts for the retained investigation; it does not certify full PixelLab replication. The [machine-readable catalog](../../sprite_workbench/contracts/RECONSTRUCTION-CATALOG.json) is the readiness service's source of the requirement, command and flow records. It deliberately leaves comparison readiness false.

The original ledger contains **63 questions in 21 feature families**, not 63 completed techniques. The 23-family view adds the pixel-art workbench and procedural VFX. The catalog keeps those distinct from the 30 source-defined transport/lifecycle flows and the 11 local F01–F11 diagnostic recipes. The joins are explicit editorial mappings; matching a family name does not prove an algorithm was implemented.

| Retained material | What is now individually accounted | What that proves |
| --- | --- | --- |
| Original requirements | All 63 original IDs, question text, family and resolution authorities preserved | No requirement silently drops out of the gate |
| Original authority buckets | 18 questions include shipped-source authority; 24 are runtime-only; 21 require server source/disclosure | These are evidence requirements, not completion counts |
| Feature flows | 21 original families, each with its seven original stages, named branches, QA requirements and retained observations; two additional workbench/VFX families | The original flow descriptions are accessible together; generic stage prose is explicitly partial |
| Source transport flows | All 30 records, including inputs, outputs, clocks, failure/cancel/retry/stale state, persistence and undo/promotion semantics | Source-defined control flow is separate from vendor runtime/hosting guarantees |
| Source anchors | All 64 original file hashes and end-exclusive UTF8 slice hashes rechecked against retained bytes; no missing referenced anchor IDs | The cited source ranges remain reproducible; this is not execution evidence |
| Workbench commands | All 28 returned help texts, syntax lines, flags, disclosed semantics and individual local dispositions | 13 have partial local routes; 15 have no equivalent command yet |
| Structured workbench grammar | 56 conditional records, 42 source-bound grammar claims, complete nine-row scene primitive table, complete returned change-operation and coordinate topics | Useful disclosed grammar is available, but the complete hosted parser/schema is not recovered |
| Local comparisons | All 11 retained diagnostic receipts, routine order and check counts | They verify bounded supplied-marker mechanics; each still records `whole_flow_complete: false` |
| Historical interfaces | All 111 public operations and 101 captured MCP definitions individually retained as unsupported remote handlers | Captured schema coverage is not handler/model coverage |
| Current public drift | A separately pinned 112-operation snapshot and exact addition/change list | Current documentation changed; historical comparison inputs must remain frozen |

## What can be built from the recovered grammar

The incomplete `describe draw_commands` response is not the only available authority. The complete `describe scenes` table separately documents these nine primitives:

| Primitive | Required documented fields, in addition to `op` | Optional documented fields |
| --- | --- | --- |
| `copy` | `part` | `region`, `method` |
| `path` | `points`, `color` | `outline`, `stroke_width` |
| `brush` | `points`, `color` | `size`, `shape`, `pixel_perfect` |
| `polygon` | `points`, `color` | `fill`, `outline`, `stroke_width` |
| `rect` | `box`, `color` | `fill`, `outline`, `stroke_width` |
| `ellipse` | `box`, `color` | `fill`, `outline`, `stroke_width` |
| `circle` | `center`, `radius`, `color` | `fill`, `outline`, `stroke_width` |
| `pixels` | `pixels` | — |
| `grid` | `rows`, `legend` | `at`, `mode` |

Every table row has an exact source file, line number and line hash in the catalog. The same source distinguishes local node coordinates, anchors, pixel rounding, ordered layers/nodes, source masks, outline footprints, transparency and copy sampling. The complete change-operation topic supplies `set_node`, `patch_command`, `duration`, `add_node`, `set_track`, seven raster operation names and the legacy pixel/color operations.

This closes the **documented primitive inventory**. It does not restore the missing structured JSON suffix, unknown-field policy, every nested discriminator or every raster corner case. In particular, `patch_command`'s command index base and `expect` encoding are unprovided; the action-dependent `values|fields|value` payload is prose rather than a fully typed schema. One-based *frame* numbers cannot establish command indexing.

The retained high response cuts 82 further lines; the low response cuts 162. The explicit `describe draw_commands --full` attempt is an error because `describe` accepts no flags. Generic truncation advice mentioning `--node` and `--frames` does not establish that those flags work on `describe`.

The current local plan, raster and construction-service dialects are separately linked. Their stricter validation or corrected behavior must retain local names and versions. They cannot silently become historical PixelLab syntax.

## The build flows are distinct adapters

The 30 transport records preserve the distinctions needed to implement flows:

- Public v2 submission returns an accepted background job; terminal status and family-specific asset retrieval remain separate steps. An unrestricted `last_response` object cannot determine every asset shape.
- Godot dispatch chooses migration-table HTTP or WebSocket paths and has its own concurrency/queue rules. Progress, generation completion and host cel commit are different states.
- Lua generation queues retain their own FIFO/retry/archive and target identity rules. A native transaction does not prove native indexed-color undo parity.
- Browser object directions, consistent-style creation, review promotion and expansion accept/dismiss use different requests and poll branches. Candidate suffix IDs cannot be replaced with positions in a sorted list.
- Chat/session events, hosted agents and project library pagination are separate services. A parser accepting an event name does not prove its server delivery/replay/deduplication semantics.
- UI preset remount, font atlas/TTF persistence and vocal timelines have separate finalization paths. A generic save call cannot substitute for those paths.

The actual source statements, exact inputs/outputs, clocks and failure paths are available in `transport_flows` in the catalog. The local F01–F11 routes are comparison groupings, not implementations of all these vendor adapters.

## Current official source check

Only unauthenticated public documentation/source metadata was fetched. No art generation, editing, account, model comparison or paid feature call was made. The [retrieval receipt](ANALYSIS-public/RETRIEVAL.json) records both successful requests and the initial rejected `main`-branch metadata requests; the official repositories use `master`.

Current public sources:

- [PixelLab llms documentation](https://api.pixellab.ai/v2/llms.txt) and [OpenAPI](https://api.pixellab.ai/v2/openapi.json).
- [Official MCP repository](https://github.com/pixellab-code/pixellab-mcp/tree/b66c475110dc13365e589691353930c955d4e358), still the same README-only commit.
- [Official JavaScript client](https://github.com/pixellab-code/pixellab-js/tree/c95b2dc0d05fa79e64c6bb082412fbee5b29d43f) and [Python client](https://github.com/pixellab-code/pixellab-python/tree/fe5f6a56ab78a43d9a151ef8ab7ed87c0936aad7), both still the previously inspected commits.

The public documentation does not supply the hosted workbench's omitted nested grammar or private handlers. That is a bounded observation about these pinned artifacts, not proof that no other provider source exists.

The [public drift record](ANALYSIS-public/PUBLIC-DRIFT.json) compares current OpenAPI with the prior public-source refresh: **112 operations instead of 111**, with new `POST /normal-map`, five changed operation objects and 273 schemas instead of 271. This is a separate baseline; the original public/MCP contracts remain intact. A reproducible recursive JSON leaf diff covers the full documents, including transitive component changes; semantic interpretations remain separately labeled documentation claims.

The new normal-map contract documents an asynchronous same-size PNG/animation-strip service, OpenGL/DirectX convention and job polling. Its prose says each frame is 8–512 pixels per axis with up to 32 frames, while its `frames` JSON Schema specifies only minimum 1 and no maximum. The catalog preserves that distinction. Neither the declaration of per-part 3D shape nor consistent animation lighting supplies an estimator, geometry algorithm, model or usable local normal-map implementation.

Three existing schemas also changed. `TargetPalette` adds `smart`, a boolean defaulting false; its prose describes beta single-image semantic recoloring by object/material and requires explicit colors. Animation requests explicitly refuse this option. The current image/style descriptions also replace older output-count buckets with finer size ranges: for example 33–35 pixels advertises 49 candidates, 36–41 advertises 36, 42–50 advertises 25, and 65–84 advertises nine. Template animation billing descriptions now mention batches above about 100 pixels. These are current provider declarations, not observed generation counts, palette quality, charges or recovered algorithms. The retained historical client bucketing and pricing helpers cannot silently stand in for this newer server behavior.

## REA and retained evidence

The connected REA session has no active native target. This work used the retained recovered shipped-source and REA producer/summary evidence rather than launching another generic parse of the identical SDK. The retained JavaScript SDK summary identifies source producer `ev_e5fdc36a736c67566b7fd6dbbde38769ec3e0c034c2ce1457234d081b935bf5a` and summary `ev_e887af732809dd9b9a7c38001d7906565bafb1492c5b2a6d3443e2e73e9d6733`. The original summary's semantic coverage remains partial/unknown; a complete application inventory is not complete method recovery. Current official SDK repository heads matching the retained commits supplies no newly released handler to decompile.

REA cannot infer unavailable server weights, training data, hidden prompts, neural kernels or provider durability from client routing strings. Their 21 original questions remain blockers for exact full-vendor replication. Selected static source questions also contain runtime/provider clauses; the old finite source gate must not close the enclosing 63-question ledger.

## What is still required before our own art/model comparisons

Readiness has two independent meanings. The host must check local setup by actually exercising the environment and installed package. This static catalog does not assert setup success. **Full comparison readiness remains false** while the required original questions and missing local branches remain open.

The actionable local work includes the 15 missing workbench command routes, the complete declared draw/scene adapter with independent numeric controls, all supported per-family preparation/finalization branches, frozen baseline selection, actual browser/worker and video-clock checks, missing VFX constructor accounting, performance limits and a versioned backend protocol. A local substitute is useful only after its algorithm, input/output contract and independent oracle are declared; it does not answer a private server implementation question.

Some gaps require another permitted evidence source: a complete provider-issued grammar/schema, legitimately released server/model artifacts, or a separately scoped controlled vendor-runtime observation. They cannot be removed by marking rows complete or by generating a new Captain animation. No such experiment is authorized by this analysis pass.

## Rebuilding and checking the accounting

From this checkout:

```bash
python3 docs/readiness/ANALYSIS-build.py \
  --research /home/astra/projects/pixellab-local-test-20261011
python -m pytest tests/test_readiness_catalog.py -q
```

The builder reads the named retained documents and original source slices; it makes no network or provider calls. Research evidence paths are relative to that separate investigation root. The catalog embeds the working statements and syntax for portability, but the full upstream source corpus remains in the retained investigation. Workbench evidence paths resolve relative to this checkout. Tests reject missing questions/commands/interfaces, silent authority changes, falsely completed grammar/flows, stale local evidence hashes and accidental readiness claims.

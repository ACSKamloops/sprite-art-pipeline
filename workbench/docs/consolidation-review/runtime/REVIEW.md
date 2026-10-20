# Consolidation runtime red-team review

The frozen `530baf35598cdbef24133783dd063bd021d1aa9c` build is a useful batch-oriented deterministic/supplied-art workbench, **not a full PixelLab clone or an accepted character-animation pipeline**. Its README and coverage table already say this. Three claim-driven controls failed at that freeze; one further file-error control failed after the first owner corrections. All originals remain preserved, without xfail conversion or retrospective passes.

## Defects and independent correction checks

| Finding | Frozen outcome | Corrected evidence |
|---|---|---|
| R01 nullable ownership | Valid rendered scene crashes editable export with AttributeError | Nullable scene exports and imports byte-identical sequence ID in a fresh Store |
| R02 unsupported-format acknowledgment | String `"false"` permits unsupported GIF acknowledgment and subsequent publication | Non-boolean flag rejected; boolFalse control also blocks completion/publication |
| R03 standalone paste lineage | Guarded raster paste loses source/edit decision despite broad every-edit claim | Explicit `parent_raster`/`paste_decision` retains raw patch, guard, region, node and stamp; editable fresh Store recovers originals and exact replay yields the same ID/RGBA |
| R04 expected local file failure | Missing font after successful candidate step leaks FileNotFoundError without failed-run receipt | Structured failed step and run ID retain preceding successful step receipt |

Owner fixes `33aab50`, `d32ea6b` and taxonomy follow-up `b212564` were cherry-picked without reviewer producer edits. Final tested local commit: `7e7b6a4` (full identity in CORRECTION-RESOLUTION.json). **6 selected tests passed, 0 failed/skipped**: five reviewer-authored controls and one owner-authored actual durable-job unsupported control independently executed. The latter proves an unavailable learned unzoom remains unsupported, with failed-run artifact, quarantined output and untouched head. It performs no model/provider call.

O01 is a policy observation, not a failed invariant: an earlier explicit publication survives a later failed direct-plan step. Direct plans are sequential, not whole-plan atomic. Registered candidate-only pipeline jobs reject direct publish/promote and use guarded terminal publication. Cancellation is cooperative between steps/at completion, not subprocess termination or rollback of artifacts. These distinctions should stay visible in caller-facing contracts.

The error receipt promise concerns admitted step failures. Invalid pre-admission plans/actions can be rejected before a pipeline-run record exists; CLI error records and durable-job terminal records are separate authorities. This review does not claim every exceptional process/storage failure can create a new receipt.

## What the consolidation actually establishes

The earlier159-test result is independently bound to retained REPORT/SPECIFICATION hashes and original JUnit:159 tests,0 failures/errors/skips at `24957ec`. The packaged smoke receipt reports actual pinned Node execution and fresh Store editable import. We read those receipts; we did **not** rerun that suite, package installation, Node or Godot this pass. That historical result does not cover every later source revision, every branch or every original F01–F11 requirement. The four newly discovered defects illustrate why mechanical pass counts are not completeness.

Typed editable closure now covers the tested supported raster/scene/sequence/preparation/track/edit/effect/font lineage. Arbitrary metadata is not an executable dependency schema, raw raster IDs do not imply original encoded identity, and this review did not enumerate all custom future artifact kinds. The strengthened paste check is actual fresh-store source recovery and replay, not a field-presence test. Sequence edits preserve their animation clock; standalone raster edits require an explicitly supplied sequence/clock association.

`FLOW-COVERAGE.json` records each F01–F11 local subset and wider uncompleted comparison requirement. The most consequential gaps are:

- No implemented vendor model/handler/backend:111 public operations plus101 MCP tools are frozen schemas, with zero vendor handlers and explicit refusal. There is no generation or provider comparison here.
- Batch CLI, editable JSON/layers and read-only review HTML do not form an interactive raster/rig/pose/key editor or native vendor editable-format bridge.
- No automatic source part extraction, missing-view/hidden-surface/anatomy construction, strong pose authorship, foot/contact/grip judgment or fine aesthetic refinement. Supplied asymmetric controls establish mechanics only.
- Pose helpers preserve distinct source conventions and known source discrepancies; they do not prove matching private model conditioning or complete body/gear asset recovery. Local terrain/UI/font/viseme substitutes likewise do not close learned or vendor-host semantics.
- Seventeen pinned effects families are a bounded source port. Real browser Worker/CSP/GPU behavior, all105 constructors/control combinations and current private MCP identity remain outside this consolidation.
- Correct-clock review pages, headless Godot/resource receipts and codec checks do not establish that motion was watched continuously, actual video PTS/cadence, gameplay use or9/10 art. Full native body-only/effects-on viewing and two independent separate aesthetic/motion reviews remain required.

README/COVERAGE currently disclose these boundaries; do not rewrite their159 mechanical checks as eleven whole-flow comparison passes, a completed editor or accepted humanoid art. No further required code correction remains in the selected controls. Useful local mechanics can continue under explicit supplied-art contracts; broad clone/art/normal-speed-video acceptance remains open.

## Evidence scope

BASELINE* retains530 three failures/one passing observation; ADDITIONAL-BASELINE* retains the subsequent missing-font failure/four passes. FINAL* and FINAL-PLUS* retain separate correction executions. SOURCE-ANCHORS.json binds selected source ranges/hashes; PRIOR-VERIFICATION-READBACK.json binds the historical receipt accounting. No provider/model/H3/network, browser, pinned VFX renderer, external video encoder or Godot execution was added in this red-team pass. Local scene/raster rendering, PNG encoding, editable export/import, storage and the durable-job handler actually executed in the selected tests. No aesthetic score was assigned. Coverage is selected, not blanket approval of all code, races, numerical inputs or private vendor behavior.

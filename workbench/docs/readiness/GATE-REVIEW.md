# Independent readiness and catalog-control review

Scope: read-only review of the root implementation represented by commit `32687fa`, followed by negative fixtures against its actual Python readiness service. Producer code was not edited by this reviewer. The fixtures use an explicitly synthetic green setup record to isolate the gate's handling of contradictory or incomplete metadata. They do not claim an attacker can write arbitrary readiness reports through the HTTP API.

Baseline: **10 independent cases, 2 passed and 8 failed**. The original failure evidence is retained in [ANALYSIS-gate-baseline.xml](ANALYSIS-gate-baseline.xml). None of these cases performs art generation or a provider call.

## Accepted baseline findings

| Finding | Reproduced result | Required correction |
| --- | --- | --- |
| G01 — original inventory can disappear | A single invented resolved requirement and an empty blocker summary can set `comparison_ready: true` | Independently pin and validate exact original ID sets, types and uniqueness; do not trust counts in the changing catalog |
| G02 — incomplete grammar can disappear from the blocker summary | With original requirements asserted closed, `grammar.complete: false` is ignored if summary blockers are cleared | Treat complete required grammar and documented local command/flow verification as independent gate inputs |
| G03 — missing local command implementations can disappear | The 15 `local_pending` command rows do not independently hold the gate after clearing the blocker summary | Derive command/flow blockers from individual records rather than trusting summary flags |
| G04 — a repeated recipe is accepted | Twelve recipe rows with the correct eleven-name set still pass setup | Require exactly eleven unique flow records |
| G05 — failed or missing recipe status is accepted | Individual `failed` or missing statuses pass setup when the nine named summary checks are green | Require a completed recipe aggregate and every individual flow status `completed` |
| U01 — new catalog material is absent from UI navigation | The initial page exposes only feature flows, help commands and original requirements | Expose grammar primitives/claims, transport lifecycles, comparison recipes and current public drift; do not leave them accessible only through raw HTTP JSON |

The root accepted G01–G05 and is correcting the gate. U01 was sent to the UI owner. A green setup record is not sufficient to open a comparison gate, and the unchanged real catalog already keeps comparisons held. These findings concern future readiness robustness and honest coverage, not a claim that a provider comparison ran.

## Correction verification

The producer added an independently pinned ID baseline, separate grammar/command/flow gates, and exact eleven-row recipe/status validation. The original ten independent cases then passed; their separate [corrected receipt](ANALYSIS-gate-corrected.xml) preserves the distinction from the original eight failures.

Three follow-up cases check jointly replacing catalog/baseline identities, removing an original requirement through mutable `required_for`, and marking a question `source_answered` while `whole_question_closed` remains false. The first two already held; the third reproduced one additional contradiction and was corrected. The [follow-up failure receipt](ANALYSIS-gate-followup-baseline.xml) remains preserved.

**All 13 independent gate cases now pass.** The [final receipt](ANALYSIS-gate-final.json) pins the actual tested readiness source bytes and test bytes; [JUnit](ANALYSIS-gate-final.xml) records each case. The source hash was checked before and after this verification. These checks do not approve artwork or certify the unresolved vendor behavior.

The revised UI source now exposes separate Grammar, Transport, Comparisons and Interfaces record views. Grammar includes the nine primitives, 42 retained claims and 56 conditional questions; current public drift has a dedicated inspector. This closes the U01 navigation finding at source-review level. Actual browser interaction/layout verification belongs to the UI owner's separate run.

## Existing controls that held

The actual complete catalog remains blocked even with synthetic green setup. It retains all original requirements and the newly documented normal-map interface as unsupported. The server's comparison endpoint and page comparison button were also explicitly unavailable in the inspected source. No remote vendor forwarding handler was present.

## Integration checks

The independent tests are [test_readiness_adversarial.py](../../tests/test_readiness_adversarial.py). Run them in the integration checkout after applying the producer corrections. Preserve this baseline and record a separate corrected result; do not replace the original failures with a later green report. Catalog accounting tests remain separate from these gate behavior tests.

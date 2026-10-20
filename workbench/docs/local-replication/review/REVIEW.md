# Selected local channel and comparison adversarial review

Three concrete defects were reproduced in owner `d004ce3` plus `9de1618`: a bounded huge-integer wait crashed the live JSONL process, a non-object run manifest leaked an exception, and a valid comparison with an unrepresentable preview clock advertised two missing player files. Owner `dfa8a88` resolves all three selected counterexamples. Owner `f5b917a` also resolves the low classification issue for a valid expired wait. **All nine independent final controls pass with zero failures/skips.** No producer modules were edited by this reviewer.

| Finding | Baseline observation | Selected corrected behavior |
|---|---|---|
| C01 medium | `local.jobs.wait` timeout `10**400` leaks `OverflowError`; process exits1 and the following ping receives no reply. | Bounds precede float conversion; structured rejection, subsequent actual ping succeeds. |
| C02 medium | CLI `lab verify-run` with `MANIFEST.json=[]` exits1 with `AttributeError` and noJSON. | Object/version/rows/paths/ID/size admission rejects as structured validation; traversal sentinel unchanged. |
| C03 medium | Two equal sequences with rational hold `1/10**400` compare exactly, but both exported review clocks are unsupported and the HTML links to two nonexistent players. | Per-side export statuses/reasons remain in comparison receipt; unavailable players are explained rather than linked; exact comparison/PNG authorities survive. |
| C04 low | Valid zero-time wait on an intentionally held active job is labeled invalid input. Channel remains responsive. | Explicit `timeout` reply with active-job guidance; not a terminal job success or malformed request. |

`status:completed` on a JSONL reply is transport dispatch, while nested job status is execution state. The negative candidate-only plan test confirms that successful submission does not publish a failed job. Source working directories are trusted local path bases, not sandboxes; no provider or secret forwarding was tested or introduced.

## Independent controls and executed evidence

The reviewer suite exercises actual child processes and actual shipped channel/manager/comparison code. It checks malformed-message recovery, unsupported method namespaces, a4MiB oversized-line drain followed by an intact ping, candidate-only publication rejection, bound suffix-selection/review-rejection services, and relative traversal rejection. The pixel comparison uses independent hardcoded asymmetric values: three changedRGBA pixels, one changedalpha, one both-visibleRGB and one both-hiddenRGB difference, unequal visibleRGBA palettes, changed holds/pivots/directions and a missing ordered baseline frame. No alignment, trimming, matte or art scoring is inferred.

The held-host case replaces **only trusted handler registration** with a local scheduling barrier. It still runs the actual JSONL channel and JobManager in a subprocess. It proves responsive wait/ping/cancel, a late canceled result recorded as quarantined, unchanged accepted head, idempotent retry and eligible retry publication. This controlled handler intentionally ignores cancellation to discriminate terminal ownership; it is not evidence about cancellation during actual pipeline rendering, provider scheduling or forced process termination. Actual JSONL response/job records are retained in `CHANNEL-RECEIPT.json`; the huge-timeout recovery and registration outputs are retained separately.

Executed command for the final snapshot:

```sh
/home/astra/projects/pixellab-local-workbench/.venv/bin/python -m pytest -q tests/test_local_channel_adversarial.py --basetemp=/tmp/pixellab-channel-final-review --junitxml=docs/local-replication/review/FINAL-JUNIT.xml
```

Result: **9 passed, zero failed/skipped/xfails**,1.13s. The interpreter is the root's pinned venv, with cwd/PYTHONPATH bound to this isolated state worktree. Initial owner snapshots map to local `68be2ca`/`7cb29a9`; corrected producer code maps to `6e9bfa5`/`7ffb616`. Receipts bind the exact source and reviewer-test hashes, rather than relying on a commit-name similarity.

A first reviewer run had5pass/4fail because my new record-review caller sent `ident` rather than the channel's `candidate_id`. That malformed caller was corrected locally and its original test/log/XML preserved in HARNESS-INITIAL files. It is **not** a producer defect. The corrected baseline is6pass/3fail; all three actual producer failures are preserved. The owner fixes then yield9pass, followed by the strengthened explicit-timeout check yielding9pass again. Raw pytest/XML outputs intentionally retain original whitespace; they are evidence, not hand-formatted source files.

## Coverage and remaining gates

This selected pass covers channel input/terminal state and supplied comparison mechanics, with the state recipes available in the reviewed producer baseline. It does not review the new geometry/method recipes, execute all eleven channels, prove fresh-wheel replay, rerun the full regression suite, or inspect provider/private/profile data. Those enclosing evidence gates remain with their respective producers and later independent checks. Missing runtime/model/native methods and art approval are not passed merely because local transport or exact pixels work.

No aesthetic/game-motion acceptance, engine/GPU/browser viewing, private model, account, network or provider result follows from these controls. Original whole-flow and63-obligation boundaries remain intact. No remaining required contradiction was found in this selected corrected scope.

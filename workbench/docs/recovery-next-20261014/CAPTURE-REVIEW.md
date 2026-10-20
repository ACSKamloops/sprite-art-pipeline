# Bounded adversarial capture review

The final verifier rejects all nine tested corruptions/counting cases. Two review findings were corrected by root: full REA-record equality and duplicate/repeated-slot counting. No unresolved material defect was found in this bounded pass. Original captures and the canonical checkout were not modified; no provider or credential calls occurred.

Final reviewed `/home/astra/projects/pixellab-local-workbench/scripts/verify_pixellab_probe_phase.py` SHA: **`cd9def6616316b6752b591efd87917ceaa9d4523dc7a618c6b8a9edc47755717`**. Exact script snapshots, copied evidence and test receipts remain under `/home/astra/artifacts/pixellab-palette-capture-review-20261014`. Final receipt `CAPTURE-REVIEW-FINAL.json` SHA: `045b9dad0187d3f859f0ffb6fbcc34b84bdde923e788e72bdb79671492d5addc`.

## Findings and corrected status

* **REA decoded-body binding:** the initial read-only source inspection checked only reported URL/status, allowing the record's other fields to differ conceptually. Root added strict JSON parsing and complete `reported == entry` equality before the sandbox run. The first tested snapshot, SHA `61cef75c13f61a2d079871b6529a28fc4804456bb76b51d8471c387cdd25b299`, already rejected the altered REA body. No pre-fix execution acceptance is claimed. The final snapshot confirms rejection; the equality check is at line76.
* **Duplicate phase counting:** the first tested snapshot accepted `variants:["joint-ab-4","joint-ab-4"]` and reported two cases/six PNGs for one copied capture. Set equality had discarded the duplicate. Root added variant-list uniqueness and a set of resolved run paths across all groups. Final tests reject both the repeated variant and a repeated group referencing the same run, at lines34 and39. This was a verifier counting defect; it did not demonstrate an extra paid submission or corruption of the original unique-case phase.

## Executed tamper matrix

A copied single-case sandbox was legitimately rebound to a new one-case plan/phase SHA, matching state/claim plan hashes and copied-HAR subject path. Its unchanged baseline passed with one case/three PNGs. Rebinding makes the sandbox usable for verifier testing; it is **not a new service capture or independent REA run**. Each tamper was restored before the next test. Credential resolution and transport were patched to raise if invoked.

| Test against final source | Result |
|---|---|
| Baseline rebound sandbox | Accepted:1 case,3 PNGs |
| Append bytes to saved output PNG | Rejected: returned-descriptor mismatch |
| Change HAR response text | Rejected: full raw-response SHA mismatch |
| Change REA subject SHA | Rejected: HAR subject mismatch |
| Change only REA reported response body | Rejected: decoded-record mismatch |
| Add retained Authorization header with a fake test value | Rejected: header whitelist |
| Mark response text redacted | Rejected: exact full-body claim unavailable |
| Change state's reported usage | Rejected: response/state usage mismatch |
| Repeat variant within one phase group | Rejected: duplicate phase variants |
| Repeat resolved run across groups | Rejected: repeated capture slot |

This is a focused review of binding/control behavior, not a rerun of all production cases or the broad test suite. The separate palette analysis binds its four original captures and REA records. Root's broader verification receipts retain their own case counts and timestamps.

## Claims that remain bounded

The runner pins the whole prepared plan and every request/wire before authentication, permits only the two fixed cleanup endpoints, refuses existing evidence, creates an exclusive per-slot claim, fsyncs the file/directory and writes attempted state before transport. Authorization/cookies are omitted before persistence. Known-token JSON key/value scrubbing handles escaped echoes; non-strict/non-JSON/incomplete response text is omitted while its observed byte extent and pre-scrub full/prefix hash remain explicit. A redacted/partial response cannot pass this verifier's exact full-body binding path.

`O_EXCL` plus fsync is an ordinary local duplicate-submission guard. It is **not a crash/power-loss guarantee or provider-side exactly-once protocol**. A transport-ambiguous attempt stays consumed; deleting/copying claims or rewriting all mutually consistent evidence is outside that guard. These hashes establish consistency of retained files against the pinned plans and each other, not network-origin authenticity.

REA independently **parses the retained producer HAR** and is hash-bound to it. It does not supply an independent observation of the original transaction, account balance, server code or model internals. The verifier's attempt bound counts unique listed completed capture slots; it cannot discover unrecorded requests. Generation usage is response-reported and is not an account reconciliation. Those limits are correctly explicit in the final verifier's classification and returned limitations.

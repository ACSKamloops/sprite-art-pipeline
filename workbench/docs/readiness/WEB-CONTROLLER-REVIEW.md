# Independent browser controller review

Baseline: producer commit `32687fa`; independently picked as `869887d` after
history work. Tests commit `6b87bbf`. The reviewer did not edit producer HTTP,
readiness, job or pipeline modules. All cases use fresh temporary Stores,
loopback HTTP, local diagnostic fixtures and fake verification workloads. No
provider, PixelLab credit or art-generation calls occur.

The [baseline record](WEB-CONTROLLER-REVIEW-BASELINE.json) pins source/test hashes;
[baseline JUnit](WEB-CONTROLLER-REVIEW-BASELINE.xml) retains the actual failures.
Nineteen independently written live HTTP tests produced **4 failures, 15 passes,
0 errors and 0 skips**. The four failures reproduce real boundary bypasses:

| ID | Finding | Required correction |
|---|---|---|
| W1 | Generic `local.jobs.submit` can run verification after a source change, bypassing `/api/verify` restart protection. | Enforce the boot-runtime fingerprint inside the trusted verification handler. |
| W2 | Generic retry can run an old verification request after a source change. | The same trusted handler guard must cover retry and direct submission. |
| W3 | Retrying a previously frozen CLI pipeline bypasses HTTP file-path preflight. | Validate frozen requests when they actually execute under the browser-configured handler. |
| W4 | A plan's path can be a reference to an earlier result; preflight sees a reference object, then the worker resolves an outside-base path. | Validate resolved per-step arguments before dispatching file operations. |

W4 used a valid construction animation ID containing an absolute temporary output
path. `construction.get` returned the ID, and a later `construction.write` used
it through `info.animation_ids.0`. The baseline actually created the output
beyond its configured project folder; this is not an inferred warning. W3 only
reads an isolated test-created outside-base PNG.

Passing baseline discriminators cover missing/incorrect session tokens, hostile
Host and Origin headers including null Origin, oversized/malformed/chunked body
framing, symlink input/output paths, inert read-only artifact JSON, failed and
cancelled verification publication, and the separation of green setup checks
from unresolved grammar and comparison requirements. Those passing cases are
bounded evidence, not blanket desktop security or sandbox certification.

Candidate producer commit `d0960de`, independently picked as `4800880`, closes
all four reproduced findings. The trusted verification handler binds its boot
runtime fingerprint, covering both generic submission and retry. Browser pipeline
handlers validate resolved arguments before each operation and verify the runtime
fingerprint before execution, at step boundaries and before final publication.
The passing tests confirm that rejected output paths remain absent.

[Candidate source/test hashes](WEB-CONTROLLER-REVIEW-CANDIDATE.json) and
[candidate JUnit](WEB-CONTROLLER-REVIEW-CANDIDATE.xml) record **22 tests passed,
0 failures, 0 errors and 0 skips**. All original 19 discriminators pass. Three
additional candidate cases change source during verification or after a pipeline
step: they prove failure to publish a green setup proof, prevention of a later
file operation, and prevention of final guarded publication even when the only
step had already completed. Partial immutable candidate artifacts may remain,
as the workbench contract explicitly permits.

No reproduced W1–W4 bypass remains in the reviewed candidate. This is a bounded
clearance of those defects and the tested HTTP envelope/file/job cases; it is
not a blanket security, sandbox, complete analysis or artwork approval. The
source fingerprint and complete readiness inventory receive separate independent
review. This report focuses on runtime HTTP/job/file boundaries and false setup
authorization through those routes.

# Corrected cutout connectivity diagnostic: two frozen requests

**Prepared only; zero calls by this reviewer.** This new fixture corrects the blocked-channel flaw documented in [CUTOUT-FINDINGS.md](CUTOUT-FINDINGS.md). The original requests, input bytes and labels remain untouched. Parent reviews/submits the separately bounded two-POST phase.

Artifact root: `/home/astra/artifacts/pixellab-cutout-connectivity-20261014`.
PLAN SHA256: `d23295b3af242446a5947db8ea626cbc8ad4ff432007bfbf10e2de7c80a692b3`.
PNG SHA256: `f8929723b17cdc39254ced84549817f4c36f9a71a7d66958f13bf27b1f566338`.
[Portable snapshot](cutout-connectivity-frozen/PLAN.json) includes PNG, actual-pixel topology proof, region annotations and both exact request/wire files. Preparation source: [prepare_cutout_connectivity.py](prepare_cutout_connectivity.py); offline connectivity implementation and its hash are bound in PLAN.

Both requests upload the same 96×96 RGBA PNG, all source alpha 255, seed 123, no text hint. Only the task enum changes: `simple` uses `remove_simple_background`; `complex` uses `remove_complex_background`. Opaque alpha deliberately isolates topology/color behavior from the previously demonstrated foreground alpha restoration.

| Slot | Readable request SHA256 | Exact wire SHA256 |
| --- | --- | --- |
| simple | `6a0bcf6d0c86251f456478b4e29671fb82c41e875b521a08a2259f6b98e60e32` | `48409733bf70203f24fbe1e85747e06489daf7228f51e68ef142cd958d79911d` |
| complex | `6b722ee5753be9cd04fb774fb847d04f465815fef38509cea9eb0e0aa88146e9` | `bacc047ecc710acf63943566e8093530624e832fb2621c22f941a51235e3f117` |

## Verified source properties

The generator executes 52 topology assertion statements and two descriptor-byte checks before declaring preparation complete. It calculates connectivity from the actual generated pixel array, rather than relying on drawing intentions. The saved PNG was also visually inspected. All region rectangles are right/bottom exclusive.

| Region | Pixels | Exact-background four-neighbor border connection | Eight-neighbor connection |
| --- | --- | --- | --- |
| True open channel inside body `[20,42,44,46]` | 96 | 96 | 96 |
| Enclosed hole `[52,38,60,46]` | 64 | 0 | 0 |
| Diagonal-only patch `[30,58,35,63]` | 25 | 0 | 25 |
| Dark detail `[62,56,66,60]` | 16 | 0 | 0 |

The open corridor actually extends from x0 through43,y42–45, crossing the left silhouette. The diagonal-only patch reaches border-connected green through a one-pixel diagonal chain `(20+i,48+i)`, i0–10. Cardinal neighbors block four-neighbor access; source checks verify the whole patch is excluded under 4 and included under 8. These are mathematical properties of the input, not predictions of a semantic mask.

Three 64-pixel strips touch the left image border and differ from the top-left background `[30,160,80]` only in red: distances 1,8,32. For max-channel-distance eligibility, each strip is wholly excluded below its distance and wholly included at/above it under either connectivity. Since only one RGB channel changes, these strips do not distinguish Euclidean from maximum-channel distance by themselves.

| Max-channel threshold | Four-neighbor connected total | Eight-neighbor total |
| --- | --- | --- |
| 0 | 5697 | 5731 |
| 1 | 5761 | 5795 |
| 8 | 5825 | 5859 |
| 32 | 5889 | 5923 |

These totals describe authored candidate eligibility/connectivity masks only. None is asserted to be the server's mask. Detailed proof and per-region counts are frozen in `inputs/TOPOLOGY-PROOF.json`. The fixture can falsify parts of the previous exact-fitting family; a matching output would still not establish original server source, semantic architecture, exact thresholds between sampled distances or the PixMiniMax internal cutout route.

## Submission guards and later analysis

New phase max 2 POST attempts, one per allowlisted slot; no automatic retries, redirects, task fallback, lock reset or duplicate slot. Parent must verify reviewed PLAN/input/request/wire pins, atomically create persistent per-slot `.submission.lock` with `O_CREAT|O_EXCL`, and record attempted state before sending. Send exact wire bytes, retain sanitized actual-wire HAR/response/output hashes, use 60s timeout and 4MiB response cap. Reported usage from the preceding phase does not authorize an assumed charge for this one. No network/credential/submission code exists in the preparer.

After parent executes, bind actual HAR request bytes to frozen wire/source pins and response PNG descriptors to saved output bytes before counting changed alpha or retained visible RGB. Compare the two modes and regional masks without a quality score or semantic groundtruth claim. In particular, a channel, diagonal chain or similar-color strip may be interpreted differently by semantic processing; the source proof merely makes that difference measurable.

Execution follow-up: [CUTOUT-CONNECTIVITY-FINDINGS.md](CUTOUT-CONNECTIVITY-FINDINGS.md) binds both completed responses to this frozen plan and reports all regional/candidate outcomes. The plan and source-proof bytes remain unchanged.

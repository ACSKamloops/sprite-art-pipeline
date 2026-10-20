# Native H3 provider boundary, 2026-10-14

This is an authored adapter around a documented native video API. It does not
recover PixelLab inference, its video conversion, or a private checkpoint.
No generation, query, credential-validation or CDN call was made during this
work. Three official documentation pages were fetched publicly; tests use fake
credentials/transports and locally encoded diagnostic video.

## Current official contract

[Create](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)
documents `POST https://api.minimax.io/v2/video_generation`, model
`MiniMax-H3`, nonblank text and first-frame, last-frame, or both image roles.
Reference roles cannot mix with frame roles. H3 accepts integer 4–15 seconds,
768P/2K; image conditioning uses adaptive ratio. Images permit 256–5760px,
aspect .4–2.5, up to30MB. H3-Max is a different model with different limits;
Hailuo controls were not inherited. This adapter deliberately supports only
first-frame with optional last-frame, PNG, <=4MiB each, <=16M pixels and
<=12MiB request. Its7000-character prompt limit is local policy.

[Query](https://platform.minimax.io/docs/api-reference/video-generation-v2-query)
documents `GET /v2/query/video_generation/{task_id}`, a `task` wrapper,
terminal `succeeded` and returned `task.content.url`. The documented query
window is seven days. No native output FPS, alpha or sprite-frame count is
promised by this adapter.

[Context-IR](https://platform.minimax.io/docs/api-reference/video-generation-v2-h3-context-ir)
uses separate `POST /v2/h3_context_ir` and the query endpoint. Its output is
an enhanced prompt in `content.prompt`, not generated video. This adapter does
not call it or silently rewrite the literal supplied prompt. Seed, sprite
frame_count/FPS, alpha removal, palette, rigs and joints are unsupported here.

Public Markdown snapshots and retrieval timestamps are retained under
`/home/astra/artifacts/pixellab-motion-provider-20261014/OFFICIAL-SOURCES.json`:

| Page | SHA256 |
|---|---|
| create | `9f68fada266f3d1c929ff96fe4fa92741eba5d0fd29b8647eb5e4e07daf507f9` |
| query | `bc91317855006307ddfc104d777736fa805c0a5d7df91f95ebfb4f9435e0b270` |
| Context-IR | `6f49a321a7d9d74e4f4dc9c057786ff3da6b7f556b0e1f897ad69b4f79b0e8ae` |

## Auth and execution limits

The credentials skill was read. The bounded local check reported Hermes
`minimax-oauth` access-token **present**, and both approved API-key environment
variables **absent**. No values, auth bodies, refresh, expiry claim or network
validation were printed/performed. Presence does not establish current media
entitlement. Official create documentation specifies a pay-as-you-go Bearer
API key. Historical pilot success with a process-only Hermes token does not
guarantee present validity or authorize another call.

The runtime never reads credentials: an explicitly authorized caller injects
a loader. A Store-wide packet claim and per-run O_EXCL marker are fsynced,
then attempted state is fsynced before the sole POST. This prevents automatic
duplicate attempts within that Store under normal filesystem operation; it
does not prove exactly-once server execution or universal crash/power-loss
durability. Ambiguous outcomes require manual reconciliation. Another Store
is a separate scope. No redirects, proxies, retries or automatic Context-IR.

The actual HTTP producer retains request/response HAR with no auth/cookies.
Valid JSON is recursively scrubbed in string values and keys; unchanged JSON
retains exact response text. Non-JSON/incomplete or duplicate-key response text is omitted to prevent
escaped-token leakage. Raw-before-scrub hashes explicitly distinguish full
bodies from retained prefixes. API responses are capped at4MiB/60s socket
timeout. Exceptions omit detail rather than echo credential-bearing objects.

CDN download accepts exactly `video-product.cdn.minimax.io` (observed retained
case) and `cdn.hailuoai.com` (official example), HTTPS/443 only. It sends no
Authorization or cookies and follows no redirects. It caps512MiB,30s socket
wait and checks120s elapsed transfer between reads; one blocking read can
extend elapsed time beyond120s. Completed downloads are hash-checked and
idempotent; failed attempts retain evidence and require reconciliation.

## Held native admission and remaining limits

Offline admission reused only the retained `h3-walk-001` case under
`/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014`. Its prepared request
matches the retained JSON semantically; raw first-frame PNG and prompt remain
literal. Completion SHA is
`87c39da98e9bab4d29bc5f02546902f55d21acc2f8a27d3969d05304741d14f2`;
MP4 SHA is `97e83ef3522a8892af98672861ee7ec5214c24dd4f441e38cc448c762c5ab046`.
`HELD-ADMISSION.json` in the new artifact directory records actual local
ffprobe results: H.264/yuv420p,768×768,107 frames,24/1 average rate,
4.458333-second container duration, despite requested4seconds. No replacement
clock or alpha is invented.

Admission preserves exact raw bytes and measured probe metadata. Supplied
completion JSON and producer-bound downloads remain evidence with stated
local provenance, not provider signatures. Requested family is H3; underlying
checkpoint and quality remain null. First+last endpoint behavior has current
documentation support but has not been live-tested by this continuation.
Motion Lab orchestration, sampling, masking, review, export, UI and installed
package proof are separate work owned by the parent task.

Validation: `python -m pytest -q tests/test_motion_provider.py` passed26 tests.
This is adapter/protocol coverage, not live endpoint or animation-quality acceptance.

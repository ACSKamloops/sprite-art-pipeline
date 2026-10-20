# PixMiniMax video-family verification — 2026-10-14

**Confirmed: the lab included H3-backed animation, not only image generation.**
PixelLab's retained OpenAPI explicitly attributes PixMiniMax to MiniMax H3. Its
[current official API page](https://www.pixellab.ai/pixellab-api) independently
still names H3. A completed paid lab probe returned an actual ordered animation
array. This finding changes the next backend scope: Image-01 still generation
alone would not cover the known animation flow.

## Retained source and runtime evidence

The [independent source/capture review](../../source-faithful/PIXMINIMAX-ANIMATION-EVIDENCE.md)
and its [machine-readable evidence](../../source-faithful/PIXMINIMAX-ANIMATION-EVIDENCE.json)
bind the original OpenAPI, recovered Godot/Lua sources, successful request,
completed response, nine returned PNG byte checks and diagnostic encoder.
These references distinguish the private client transport from the public probe.

Root also reinspected the original HAR offline with REA; the bounded receipt is
[REA-VIDEO-CAPTURE.json](REA-VIDEO-CAPTURE.json). This made no network replay and
persisted no headers, credentials, job IDs or inline image bodies. It confirms:

| Stage | Observed retained evidence |
| --- | --- |
| Submit | HAR entry 1: `POST /v2/animate-pixminimax`, HTTP 200. First PNG plus description; `frame_count=8`, `seed=123`, `no_background=true`, `enhance_prompt=false`. |
| Complete | HAR entry 24: `GET /v2/background-jobs/{job_id}`, HTTP 200, `status=completed`. |
| Returned artifact | `last_response.images` contains nine PNG entries. No native video field is present in this selected completed response. |
| Original frame | Independent reviewer decoded all nine PNGs and byte-matched the retained files. Return zero exactly equals the submitted PNG, 256×256. |
| Client | Recovered private Godot/Lua route `animate-minimax-h3` has its own caption/raw-raster/count+1/placement contract. It is separate from this public encoded-PNG probe. |
| Review video | Local ffmpeg encoder consumes returned PNGs and creates a derived diagnostic 8-FPS MP4. Source FPS was not supplied. |

The four optional caption fields were not supplied in the actual captured public
request. Their presence in the contract/client does not prove how they were
internally inferred in this run. Likewise, the requested seed does not establish
determinism without a matching repeated run.

REA classifies the retained capture as historical-reference evidence with unknown
live runtime attribution. Its structural inspection is not independent proof of
the remote deployment's authenticity or private inference implementation.

## Current native H3 API is a different contract

MiniMax's own current [create documentation](https://platform.minimax.io/docs/api-reference/video-generation-v2-create),
[task query](https://platform.minimax.io/docs/api-reference/video-generation-v2-query)
and [video guide](https://platform.minimax.io/docs/guides/video-generation)
are retained verbatim under `public/`, with hashes in
[RETRIEVAL.json](public/RETRIEVAL.json).

| Boundary | PixelLab retained contract/observation | Current native MiniMax documentation |
| --- | --- | --- |
| Submission | `/v2/animate-pixminimax`; sprite first frame and motion, optional last frame | `/v2/video_generation`; multimodal `content`, explicit model, resolution and seconds |
| Job/result | Background-job polling; completed `last_response.images` | Task ID; query `/v2/query/video_generation/{task_id}`; succeeded `content.url` returns a video download |
| Canvas | Sprite sides at most 256px | Input image sides 256–5760px; H3 output 768P/2K |
| Motion length | Requested generated frame count, multiples of four, 4–40; captured PixelLab public probe returned count+1 | H3 duration 4–15 integer seconds. No requested output frame-count/FPS control is declared in the inspected create schema |
| Inputs | Separate sprite captions, seed, optional background removal and drift threshold | First/last image roles or a separate reference-media mode; those modes cannot be combined |
| Pixel handling | Transparent PNG results; documented de-flicker behavior; exact source first in this captured PixelLab public probe | No equivalent typed alpha, drift-threshold, sprite-caption slots or output-pixel preservation guarantee is declared in the inspected create schema |
| Seed | Present in PixelLab request | Not declared in the inspected current H3 V2 create schema |
| Enhancement | PixelLab's engine-specific motion enhancement and separate caption steps | H3-Context-IR is a separate service. H3 Max has a distinct prompt-expansion option, defaulting to balanced; neither establishes PixelLab's implementation |

The current schema describes reference-input video FPS limits; these are not
generated video FPS or sprite playback timing. Its prose also differs on whether
a last frame alone is valid: input combinations list it, while the role field
says it must be paired with a first frame. Do not assume that edge case is verified.

H3 Max is a distinct vendor/fal post-trained variant in the current guide. It is
not established as the engine deployed by PixelLab. The H3 attribution identifies
an engine family, not a revision, fine-tune, resolution, sampler or weight hash.

## What is still unknown, and what must be retained next

Not recovered: PixelLab's native H3 invocation; any provider video bytes, latent
output or decoded source timestamps for this run; upscale/padding and frame
selection; alpha/background generation; temporal color correction; or its exact
checkpoint. The PNG response alone cannot reveal these private stages.

Before an honest local comparison can be called ready:

1. Specify a separate H3 video-task interface. The current v0.6 still/edit packet
   contract rejects animation and does not become video-capable by changing a
   model name. Keep M3.1 chat, Image-01 stills and H3 animation distinct.
2. Map only native documented controls. Unsupported PixelLab controls must be
   rejected or exposed as clearly named local policies, with input/output hashes.
   Do not silently turn requested sprite count into clip seconds or invent FPS.
3. Verify media authentication/entitlement separately. The existing Hermes OAuth
   login succeeded for direct chat; no H3 video request has been made. The current
   create page specifies pay-as-you-go while M Plan pages advertise video on
   selected tiers; neither proves this account's actual media permission.
4. On a subsequent generation test after the contract is prepared, retain the exact prompt/input bytes,
   native task records and downloaded original video, then inspect actual codec,
   dimensions, timestamps and decoded frames before conversion. Expiring URLs
   alone are insufficient evidence.
5. Keep original video, decoded frames, locally transformed sprites and playback
   timing as distinct artifacts. Label any frame selection, background removal,
   palette correction or rescaling as independently implemented until recovered
   source or controlled evidence supports equivalence to PixelLab.

This review adds no video implementation, generation run or quality acceptance.
One earlier minimal direct text probe in this review is recorded separately in
[CHAT-PROBE.json](CHAT-PROBE.json); it is not media capability evidence.

An independent reviewer checked the vendor-contract and evidence boundaries.
Their one material finding was ambiguous use of “native” for an unconverted
PixelLab source fixture; that wording was corrected to avoid implying a direct
MiniMax API generation. The selected evidence hashes, all nine PNG byte checks,
source-frame identity and review links are recorded in
[VERIFICATION.json](VERIFICATION.json).

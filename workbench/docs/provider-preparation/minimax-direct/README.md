# Direct MiniMax review — 2026-10-14

**Follow-up:** the later [generic RPG hero pilot](../h3-rpg-pilot/README.md) has
now completed three direct H3 jobs and three matched PixelLab jobs, with REA
capture checks. Statements about untested media access below describe this
earlier connectivity review. Private conversion parity remains unestablished.

PixelLab's **PixMiniMax animation feature is explicitly powered by MiniMax H3**.
That attribution is present in our retained OpenAPI and is still stated on
[PixelLab's official API page](https://www.pixellab.ai/pixellab-api). The retained
paid probe submitted a first sprite plus a motion description, requested eight
generated frames and received nine PNGs, with the original input first. An
Image-01 still-image adapter alone would therefore miss this animation route.

The important boundary is the returned artifact: our captured PixelLab result
contains ordered PNG frames, not a native H3 video file. H3 is a video model, but
we have not recovered PixelLab's private H3 invocation, video decoding/sampling,
alpha generation or color de-flicker implementation. The local diagnostic MP4s
were encoded from the returned PNGs at an analyst-selected playback rate. They
do not prove PixelLab's original video format, FPS, timestamps or frame sampling.

See the [video verification](PIXELLAB-VIDEO-VERIFICATION.md) for the source,
request, completed-response and playback evidence, with explicit unknowns.

## Direct access actually checked

The existing Hermes MiniMax OAuth login works for direct API requests without
launching the Hermes agent. A real model-list GET returned HTTP200, and a minimal
`MiniMax-M3.1-Flash-Preview` request to `/anthropic/v1/messages` returned the exact
requested `MINIMAX_DIRECT_OK` response with HTTP200 and `stop_reason=end_turn`.
[Model-list receipt](MODELS-PROBE.json), [chat receipt](CHAT-PROBE.json).

The text probe used `max_tokens=256` and `output_config.effort=low`. The returned
usage reported84 input tokens,12 output tokens and128 cache-read input tokens;
these are observed fields, not a price calculation. The model-list result did
not list the M3.1 preview, even though the subsequent direct call succeeded, so
listing omission must not be treated as proof of unavailable access.

Only the short connectivity instruction was sent. No project files, reference
images, private chats or user assets were uploaded. No image/video generation
request was made. Credentials remained in process memory and were never copied
to this report or command arguments. No refresh, installation, configuration
change, full Hermes launch or fallback provider was used.

## MiniMax's own documentation

The review now starts from MiniMax's [official documentation index](https://platform.minimax.io/docs/llms.txt).
The exact unauthenticated public Markdown snapshots and hashes are retained in
`public/`; [retrieval manifest](public/RETRIEVAL.json).

| Service | Vendor documentation | Consequence for the pipeline |
| --- | --- | --- |
| M3.1 Flash Preview | [Anthropic-compatible API](https://platform.minimax.io/docs/api-reference/text-anthropic-api) | Chat/reasoning with image/video understanding and tool calls. This is distinct from synthesizing image pixels. Direct text access is now verified. |
| Image-01 | [Text-to-image](https://platform.minimax.io/docs/api-reference/image-generation-t2i), [image-to-image](https://platform.minimax.io/docs/api-reference/image-generation-i2i) | A native MiniMax image backend exists at `POST /v1/image_generation`. It need not pass through a Hermes image plugin. Image access using this account's OAuth remains untested. |
| H3/H3 Max | [Video V2 API](https://platform.minimax.io/docs/api-reference/video-generation-v2-create) | H3 is the relevant named engine family for PixMiniMax animation. The current native API returns a video task, whereas PixelLab's retained public response returns PNG frames. Native API access and conversion parity remain untested. H3 Max is a separate variant and is not established as PixelLab's deployed model. |
| M Plan | [Official overview](https://platform.minimax.io/docs/m-plan/intro) | The vendor lists image/audio across all tiers, and H3 video for Explore/Build. This review did not query the user's tier, balance or media entitlement. |

The user's earlier “H3” shorthand meant their Hermes/MiniMax setup. Keep that
clarification separate from the vendor's actual H3 video model name.

## Video route and remaining replication work

MiniMax's current native contract is `POST /v2/video_generation`, followed by
`GET /v2/query/video_generation/{task_id}` and download of the succeeded task's
`content.url`. First-frame and optional last-frame roles support image-to-video;
reference-to-video is a separate input mode and must not be mixed with those
roles. The retained current schema requires input image dimensions of at least
256px, and H3 produces 768P/2K clips lasting 4–15 seconds. These are not PixelLab's
low-resolution, requested-frame-count sprite API. See the retained [create
schema](public/api-reference__video-generation-v2-create.md) and [query
schema](public/api-reference__video-generation-v2-query.md).

The current create schema does not declare PixelLab's `frame_count`, `seed`,
`no_background`, `drift_threshold`, or four separate sprite-caption fields.
They cannot simply be forwarded as native H3 parameters. It also does not
declare a native output FPS control. The documented 23.976–60 FPS range concerns
**input reference videos**, not generated output or sprite playback.

H3-Context-IR is a separate, proprietary multimodal prompt-expansion service in
the [vendor documentation](public/api-reference__video-generation-v2-h3-context-ir.md).
Its existence does not prove PixelLab uses it. PixelLab's own enhancement and
caption steps remain separate recovered contracts. H3 Max's documented default
prompt expansion must also remain visible if that distinct variant is tested.

The next animation integration needs a **separate H3 video-task contract**, exact
submitted input/prompt records, retained original video bytes, decoded frame
timestamps and an explicitly named conversion policy. Any local upscaling,
frame selection, background removal or palette correction will be an independent
implementation until supported by recovered PixelLab evidence. Keep its result
separate from the current v0.6 still/edit comparison interface, which rejects
animation tasks. A successful Hermes chat request does not establish H3 video
authentication, entitlement or sprite quality.

## Native image controls actually documented

The inspected Image-01 schema has stronger native controls than the session's
built-in image tool: `width` and `height` together from512 to2048 in multiples
of8, or aspect ratio; aspect ratio wins if both are supplied. It documents an
integer seed,1–9 outputs and optional prompt optimization. Vendor prose claims
same-seed reproducibility; no image repeatability experiment was run here.

Set `prompt_optimizer=false` explicitly in a future controlled adapter, retain
the exact submitted prompt, and prefer `response_format=base64` for original-byte
retention because generated URLs expire after24hours. Record actual returned
dimensions/counts and failure metadata instead of assuming the request was met.
The one-reference image-to-image channel is subject identity conditioning.
It must not silently replace style/appearance/pose inputs or an exact edit mask.
No typed transparent-background or pixel-preservation guarantee was present in
the inspected schemas. Do not silently remove backgrounds or downsample outputs
and call those operations original PixelLab techniques.

The provider also publishes [local H3 deployment guidance](https://platform.minimax.io/docs/guides/local-deploy-h3)
for ComfyUI and SGLang. Those are separate weight/runtime configurations. Hardware
figures depend on the precision/offload/topology; no weights were downloaded and
no local generation capability was established by reading those instructions.

## Correction to the earlier boundary

The earlier [Hermes-only inspection](../HERMES-READONLY.md) established that its
active image provider was unselected and its MiniMax image plugin was not
installed. That was insufficient to conclude whether the credentials could be
used directly with MiniMax. Direct chat access is now proved; native image
access is a separate, still unexecuted check. An installed/unselected Hermes
image plugin is not a prerequisite for a direct HTTP adapter.

Keep **M3.1 chat, Image-01 still generation and H3 video generation** as distinct
capabilities. For the animation objective, investigate the H3 task/conversion
boundary before implementing or testing an Image-01-only path. Native H3 would
be a named external backend from the disclosed engine family, not proof of the
same PixelLab checkpoint or private conversion method. The current0.6 software
test/package proof remains a preparation-only snapshot; this later connectivity
review adds one live text call, not a new art/model comparison.

[Machine capability summary](CAPABILITIES.json), [selected evidence hashes](MANIFEST.json).

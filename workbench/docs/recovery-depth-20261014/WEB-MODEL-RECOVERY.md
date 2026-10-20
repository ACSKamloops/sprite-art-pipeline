# Public web/model recovery — 2026-10-14

The current public client yielded **new recoverable client code, but no exact PixelLab checkpoint or private H3 video-to-sprite implementation**. A new linked Pixelorama pack was recovered and compared against the retained version. Current browser PixMiniMax submission, PNG consumption, playback metadata and a pixel-input classifier are source-visible. Native video sampling, temporal color correction and model serving remain outside those recovered paths.

[Machine finding ledger](WEB-MODEL-RECOVERY-LEDGER.json), [public retrieval receipts](PUBLIC-RETRIEVAL.json), [Godot script comparison](GDSCRIPT-DIFF-INVENTORY.json) and [selected H3 identities](H3-CLIENT-SOURCE-IDENTITY.json) bind the conclusions. Full downloads, unchanged function projections, GDRE outputs and REA views are under `/home/astra/artifacts/pixellab-recovery-web-20261014`.

Scope: credential-free public GET/HEAD requests to explicitly linked pages/assets, inert AST inspection and static scripts-only recovery. No credential files, signed-in runtime, provider inference, paid request, project execution, root-checkout or prior-research mutation. No `.map` URL guessing or `/dev` route probing. Mutable public URLs are bound by retrieved UTC time, HTTP status, byte count and SHA-256.

## Changed public client: recovered, not assumed equivalent

The public homepage, API page, `/create-vfx` page and fresh [`llms.txt`](https://api.pixellab.ai/v2/llms.txt) all returned HTTP200. Their script links and six selected build-manifest routes led to current editor, create and animation chunks. Actual Worker constructors and chunk-name tables led to six worker files and three dependency chunks. The completed scope retained 81 GET records, 14,759,031 body bytes and 72 JavaScript files; all requests stayed within published resource references. Four separate editor-resource HEAD records include one404.

The current editor page is **byte-identical** to retained `analysis-client/editor-shipped/editor-bundle.js` (16,612 bytes). Its current `_app` module68202 publishes `v0_0_211` and the iframe URL builder `/pixelorama_<version>/pixelorama_pixellab`; the credential-free base returned HTML. The linked engine JavaScript is also byte-identical to retained `evidence/pixelorama_pixellab.js`, SHA `33c94cb3175f3333b82e2a3be5e8e86f77986f0aa2042b1631f6367a4e5bb6ba`.

The linked PCK is **different**: 9,283,280 bytes, SHA `398455603cf39fc993c59fca3265ed180e246005da631e918018d0c44d497e4f`, versus retained 9,264,816 bytes / `ebf9812ea474bddb84faa22183a1ec0178983cdc285674a4d0177c606e8a4a3f`. Existing GDRE v2.7.4 recovered378 GDScripts successfully without running the project: **368 unchanged, 8 changed, 2 new**. Version changed `0.0.208+pixelorama`→`0.0.211+pixelorama`. Changes concern tileset shape/cost UI, target-palette state, loading controls and GIF shader paths; the two new scripts are `target_palette_option.gd` and `tileset_pro_shape_preview.gd`.

Crucially, `AnimatePixminimax.gd`, `InterpolatePixminimax.gd`, `websocket.gd`, `background_generation.gd` and `draw_image.gd` remain byte-identical. The relevant current H3 cost function is also unchanged, although its containing cost file has tileset changes. Pack freshness therefore does not supply a new H3 sampler.

## Exact H3 browser boundary and clocks

Current `create-vfx-b876fab0cfaf0dae.js` has SHA `08da18c2c8519c6e540544322d8ac39ebef901e3a2e2abe34ff0050f4561cb51`. Its submission function at original **UTF-8 bytes237856–239112** / UTF-16 indices237822–239078 is retained unchanged in the focus projection; selected SHA `3750f03024bfd2d9ae5bae9f78dfb1d673c741a971580c0040d9d2f7cce55a2c`.

It sends a browser/private `rgba_bytes` descriptor to `/animate-minimax-h3/background`, including literal motion text, optional last frame, requested frame count, random seed, transparency choice, caption fields and enhancement flag. It then polls `/background-jobs/{id}`. This is separate from the public `/v2/animate-pixminimax` encoded-PNG contract and from MiniMax's native video API. No authenticated endpoint was queried.

The completed-result consumer at UTF-16 indices236248–237026 obtains returned image dataURLs, loads them through `window.Image`, draws each to a canvas and reads RGBA with `getImageData`. This is **ready-image/PNG decoding and local canvas handling**, not native H3 video decoding. Its inspected result consumer carries no native video URL, codec/PTS or model-revision field.

At UTF-16 indices261943–261994, the browser attaches clip playback metadata from `nv.recipe.fps`, with fallback12. This is the current effect/source recipe's client playback rate. It does not disclose the provider video FPS or a requested-sprite-count→native-duration mapping. Exact assignment and source anchor are retained in `h3-client-playback-anchors.json` under the artifact root.

Current recovered `pro_tool_cost.gd:320–327` computes a cost estimate: side-based scale factor4/2/1, area/65536, `5.9*n + .062*n²`, then `seconds=34+pixels*per_frame` and rounded cost `seconds*6/380`. The variable name “seconds” is not evidence of native clip duration or frame sampling. `AnimatePixminimax.gd:316–337` passes frame count and reserves count+1 destinations; it supplies no native duration/FPS mapping. No such mapping was recovered in the reviewed browser hook, Godot H3 submission/placement or cost helper.

## Real shipped algorithms, with separate ownership

Worker5259 and linked chunk6428 expose module66428, an **original shipped input classifier**. Its source computes run/grid consistency, scale phases, edge softness and other thresholds, returning labels such as `llm`, `upscaled`, `photo` or null. This is actual PixelLab client heuristic code; it is not an invented local replacement. It can be recovered or replayed as its own source-versioned feature, but does not reveal how H3 output was sampled, given alpha or temporally de-flickered. Sources and formatted inspection views are retained; no classifier execution occurred here.

The VFX workers2773/3483/4268/4647/7317 references are actual published resources. In the inspected code, worker2773/7317 handle procedural recipe fitting/rendering, worker3483 exports images/manifests, and worker4647/4268 dispatch through chunk5910's procedural render/export utilities. These are source-visible operations, not proof that the remote animation service uses a browser worker to decode native video. Worker-resource inventory and dependency bindings are retained in the artifact root.

The Godot result handlers consume `image(s)` and `quantized_image(s)` outputs, skip explicitly declared reference slots and place cels (`websocket.gd:168–201`). `draw_image.gd:199–212` recognizes PNG magic, decodes PNG to RGBA8, or interprets supplied raw RGBA bytes. Palette reduction is sent to the remote `quantize-image` route (`quantize_websocket.gd:26–56`); the current loading UI hides reduction controls for animations or an already-used target palette. Neither that routing nor client placement recovers the remote palette algorithm, foreground drift metric or background generation.

## Model disclosures and bounded negative results

The fresh [official OpenAPI](https://api.pixellab.ai/v2/openapi.json), linked by `llms.txt`, returned478,504 bytes, SHA `8cb24ecdd26e9fe48639dc789e44f32b3c78c29e8da8c3121f23ab360ade5dad`. The [official API page](https://www.pixellab.ai/pixellab-api) still explicitly attributes PixMiniMax to **MiniMax H3**. The request retains frame count, seed, background removal, drift threshold and caption/enhancement fields. It declares no native duration, video FPS, checkpoint or provider-video field. Its operation/schema projection is retained in `PUBLIC-MINIMAX-SCHEMA.json`.

This establishes an engine family, not PixelLab's exact H3 revision, fine-tune, sampler, latent resolution or video conversion. Pixen, Pixflux, Bitforge and Pro labels remain product/selector evidence unless supported by a separate explicit architecture declaration. No new exact deployment manifest was found in this bounded public corpus.

No `sourceMappingURL` annotations were found in72 current downloaded JS files,105 retained website JS files or the retained editor bundle. Current script responses had no `SourceMap`/`X-SourceMap` headers. Retained original HTTP headers were not inspected. Therefore **no linked source map was discovered or downloaded**, not “source maps do not exist.” Unlinked or authenticated assets and other builds remain untested.

The current scripts and128 recovered PixelLab GDScripts contained no literal `checkpoint`, `model_revision`, `.safetensors`, `.onnx`, `ffmpeg`, `mp4box`, `video_url` or `native_video` matches in the declared search. Ten `VideoFrame` matches belong to generic Three.js texture/render support, not a traced H3 decoder. The engine JS does contain WebAssembly loading support, which is the Godot runtime, not identified inference code.

The public Godot HTML advertises a39,514,754-byte WASM file; HEAD on that exact linked resource path returned404. No large WASM was downloaded and that one404 does not establish universal unavailability. PCK inventory listed2355 resource paths: the only named model/WASM-extension candidate was `.godot/uid_cache.bin`, a Godot UID cache. This is a filename inventory, not exhaustive interpretation of all opaque package bytes. No model weights were downloaded.

## REA evidence and remaining probes

REA parsed the initial26 eligible downloaded JS files without syntax failures, but semantic extraction reached its100,000-node ceiling and retained67,127 unknowns. Producer `ev_fb6cf11a456553d312af70d5fca6d2d66776b659f0795d7ec1a7a887a109e5dc`; [summary view](REA-WEB-SUMMARY.json). Its complete result exceeded MCP transport size; the producer was not rerun to evade that limit. An immutable initial download snapshot remains in the artifact root.

A smaller31-function,46,108-byte source projection parsed without failures; outer bindings remain unresolved and2,375 semantic unknowns remain (`ev_59f011db9e4db8eb616fdf6fdb7328012802c43016171b09ee49235c47b639ef`). The `frame_count` semantic trace was ambiguous across two slots, not a resolved duration/FPS dependency (`ev_ec929b661c81e400c2494dfb272fd36b5079d77bb82f420bb92961170c8c6ff2`). Literal route/application graph traces returned no matches and cannot establish absence.

The two classifier source files parsed with no failures, but2,283 semantic unknowns remain (`ev_4596d0f7ab01af127c39f193e5e43b65966d7a607171b9ad5a0501340a16c2c4`). Its `verdict` trace found one property node with three relevant unknowns (`ev_be3a84576b2474a55bd1cd294202f112aa96f15ca8d031ddd2f0370166572a96`). These graph results are static syntax/inference evidence, not execution or comprehensive dataflow proof. Exact original source/hash anchors support the manually inspected paths.

Useful next probes are: a separate source-faithful classifier replay against supplied diagnostic markers; an isolated update/review of the changed procedural VFX factories; targeted static tracing of additional public animation components; and an explicit vendor disclosure of checkpoint plus video decode/sample/alpha/drift stages. Any direct H3 implementation remains a disclosed-family backend with independently named conversion policies until those server facts are recovered. This pass does not authorize or require another paid generation.

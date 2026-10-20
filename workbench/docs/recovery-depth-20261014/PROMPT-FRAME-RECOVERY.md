# Prompt, endpoint and frame recovery: bounded original-client pass

This pass adds deterministic replay of selected **original client methods**, plus two precise edge qualifications. It does not recover PixelLab's private motion inference, server prompt writer, frame sampler, resampler or checkpoint. No credentials, network, providers, native editor or artwork generation were used. Research sources and the canonical workbench were read only.

The machine-readable [claim ledger](PROMPT-FRAME-CLAIMS.json) binds 15 selected claims to 26 exact ranges across 18 retained files. Every anchor carries the complete source SHA256, fragment SHA256, original UTF-8 byte interval and line interval. The public declaration snapshot has its own SHA256 and JSON Pointers. This is a selected review, not completion of all animation branches.

Prior work matters: `analysis-poses/depth-round2/animation-client-closure`, `analysis-poses/depth-round4/full-animation-geometry-flows`, and `analysis-models/depth-round2/prompt-enhancement-closure` under `/home/astra/projects/pixellab-local-test-20261011` already establish most caption, caller, endpoint and clock semantics. Their static findings are identified as prior findings in the ledger; replay does not turn them into newly recovered private algorithms.

## New useful qualifications

* **Seed type survives validation.** In original `create-json.lua` lines80–82 and176–178, `tonumber(seed)` is tested but its converted value is not assigned. Numeric strings such as `"123"`, `"-1"`, `"12.5"` and `" 123 "` remain strings in the request table; invalid strings become numeric0. The original table behavior was replayed. The actual native JSON codec and private endpoint acceptance were not tested. This differs from recovered Godot's explicit integer conversion, and must not silently become the public REST integer schema.
* **Selection placement is an OR predicate.** Original `place-image.lua` lines64–66 accepts a selection subregion when either output axis is smaller. A64×16 response against32×32 therefore follows the selection branch despite its width being larger. The original code's comment saying “genuinely a sub-region” is narrower than the predicate. Symbolic replay proves branch selection and fixed destination-canvas calls; actual editor clipping/pixels and any historical failure remain unproved.

These are source-preserving qualifications, not suggested algorithm repairs.

## Prompt preparation and endpoint grammar

Lua stores percent characters doubled for UI handling, then undoubles them for API text. Whitespace-only text is omitted, but nonblank edge whitespace survives. `Auto` is a sentinel for picked view/direction only; free-text subject `Auto` is literal. Advanced enhancement selects existing text slots for improvement, applies description, and preserves user-picked orientation. First-source comparison guards stale caption application and resets caption state on source change. These selected source branches already had static closure; the original executable methods now have replay evidence.

Recovered Godot trims caption text edges. Its caption-application helper directly indexes returned caption keys; it does not have Lua's same defensive field handling. Its first-image change cancels enhancement and clears caption state. First and last image guards are not interchangeable. This pass retraces these recovered source methods but does not execute Godot or establish race handling in its engine.

The original web enhancer at `create-677791a6e206dafa.js` bytes[13133,14631) checks authentication presence and blank prompt, converts optional image URLs, maps camelCase caption options to snake_case, defaults absent engine to `v3`, and sends a private `/enhance-animation-prompt` request. It forwards nonblank prompt spacing. Its own body builder does not enforce integer frame count or enum domains: the replay forwards12.5, `Auto`, and an explicitly empty engine. This says nothing about upstream UI validation or server acceptance. Callback/loading/finally behavior was exercised in a synthetic lexical host with fake fetch; neither authentication nor HTTP was used.

The retained public OpenAPI snapshot SHA256 is `8cb24ecdd26e9fe48639dc789e44f32b3c78c29e8da8c3121f23ab360ade5dad`. It declares server `/v2` and `/enhance-animation-v3-prompt` using `first_frame: Base64Image`, optional `last_frame`, and required `action`, whereas the private web helper uses flat `image_base64`, `image_base64_end`, and `prompt`. Its declared engine domains are `v3`, `pixminimax`, `skeleton-v3`; frame_count is optional integer1–40. The public declaration says direction is accepted but unused for enhancement and belongs on the animation route for MiniMax facing. Those declarations constrain adapters; they are not proof of the implementation behind the endpoint or compatibility with private raw-RGBA/WebSocket routes. The documented returned prompt style is not recovered private prompt-generation code.

## Roles, placement and timing

Lua MiniMax animation captures a nonempty first reference, caps each axis at256, validates frame_count as a multiple of4 in4–40, sends `first_frame` as base64 raw RGBA with explicit dimensions, and posts to `animate-minimax-h3`. It sizes generation to the reference. Whole-canvas resizing uses centered integer offsets after confirmation; selection mode retains the canvas and selection origin. The caller prepares frame_count+1 logical slots and skips only the first marker. Interpolation conditions on first **and** last, prepares count+1 logical slots and skips both endpoints. Its UI's “new frames” count has an offset; count labels are not interchangeable across callers.

Recovered Godot MiniMax retains the first image in its animation tool, sets image_amount=count+1, validates optional last visibility and matching dimensions, and sends raw RGBA. Its interpolation subclass requires the last image, modifies count from slider+1, sets image_amount=count−1, and flags both endpoint skips. These are distinct client response/destination policies. They do not identify the private service's sample positions or establish that any live return satisfies the comments.

Original Lua placement chooses explicit response geometry first. Without both explicit dimensions it tests byte pixel count against the current canvas before the remembered request image_size. Full-canvas output ignores a stale selection origin. Crop metadata and offsets affect placement; they are not a PNG decoder, resize operation or neural repair. The replay preserves these branches rather than substituting local art logic.

For the shared original Lua allocation helper, a17-slot fixture produces17 drawable destinations without skips,16 with first skip,15 with both skips, while retaining false endpoint markers in the17 logical slots. The host NewFrame calls are symbolic. No timestamps, gait phase or true remote sampling positions are inferred from the integer slot count.

Godot frame duration defaults to multiplier1; seconds are duration/fps, and the recovered new-project default is6fps. Existing project clocks remain authoritative. The prior round4 report recovered a predecessor-duration rule in bounded upstream Aseprite commit `14fe117e853bd642672e72018166239506060cd4`; the actual user's installed Aseprite version is still unidentified and was not executed here. Selected website preview effects tick125ms, while selected saved animation records use200ms. Preview time, host insertion time, saved metadata, returned image order and native video PTS are separate evidence. Do not match all107 native video frames to17 PixelLab images, or describe a shared nominal inspection duration as a shared native FPS.

The original MiniMax cost function is a client display estimate with tested64/65 and128/129 size-tier boundaries. Its comments about sampling/upsampling do not recover those server operations, and the display estimate is not billed cost.

## What was executed and retained

[REPLAY-PROOF.json](REPLAY-PROOF.json) records98 passing assertions across9 Lua cases and5 passing web-helper cases, full original-source pins, and harness hashes. Original Lua bytes are loaded into an isolated installed LuaJIT2.1 state; the web helper's exact byte slice executes in Node's isolated lexical context. Image, timeline, app and JSON APIs are explicit symbolic stubs. This proves selected original client control/table behavior under those inputs, not native raster/codec behavior, full UI acceptance, LuaJIT/Aseprite runtime equivalence or art quality. Godot and preview-clock claims remain static source retraces.

Reproduce offline from this checkout:

```sh
python scripts/recovery_depth/build_prompt_frame_ledger.py --check
node --check scripts/recovery_depth/prompt_frame_web_replay.cjs
python scripts/replay_prompt_frame_recovery.py
```

[REA-RECORD.json](REA-RECORD.json) identifies complete private Evidence `ev_26316b3182c471dabe0a50af1fd31b68d81430fbe239f7a41dc32a9588bf7c07`, preserved under `/home/astra/artifacts/pixellab-recovery-depth-20261014/prompt-frame-source-fidelity-01/REA-EVIDENCE.json`, SHA256 `9fcab25d43634a8c270001c2ad17a2d1cc7a0df9882acb31d3424b3a608e52c8`. Focused REA examined two inert carriers containing bound original web-helper bytes, not the complete app:2files,1831text bytes,434AST nodes,0parse failures,71semantic-graph unknowns and unknown semantic coverage. Parsing and a shipped-fragment provenance receipt do not establish whole-app semantic completion. Full Evidence stays private; the ledger contains finite selected-file keyword counts and explicit unsearched bounds.

## Remaining probes

1. In an authorized native Aseprite test, establish its exact version, actual JSON seed encoding, mixed-axis Image clipping and inherited cel durations. Preserve source semantics before any deliberate correction.
2. Exercise recovered Godot enhancement cancellation and first/last changes in the engine, with incomplete caption responses and source mutation during an outstanding request. Static source does not settle actual signal/race timing.
3. Trace the exact mounted web caller and worker/export clock for a chosen workflow/version. Helper absence of validation does not establish a reachable invalid request.
4. Seek shipped or officially disclosed server frame-sampling/prompt-writer code; if unavailable, preserve that boundary. Matched live observations can characterize outputs, but cannot supply an invented private algorithm or isolated model ranking.

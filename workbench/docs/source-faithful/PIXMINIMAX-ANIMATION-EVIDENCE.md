# Retained PixMiniMax animation and video evidence

**The lab did execute PixMiniMax animation. Treating that prior work as image-only
would be incorrect.** Its retained successful public probe returns nine ordered
PNG frames, not a native video file. MiniMax H3 is a documented video-generation
engine family; the exact PixelLab deployment and internal video-to-sprite stages
remain unavailable. This review made no provider/model/agent calls, read no
profiles or authenticated headers, and changed no canonical runtime/research files.

All evidence paths below are relative to
`/home/astra/projects/pixellab-local-test-20261011` unless stated otherwise.
In the retained fixture/report names, “native” means the unconverted source
sprite used by the PixelLab public probe. It does not mean a direct MiniMax API
request or a native provider video, neither of which this probe establishes.

## Actual successful animation, independently rechecked

- `runtime/probes/minimax-walk/request.json:2,10-13`: endpoint
  `/animate-pixminimax`, requested eight frames, seed 123, background removal true,
  enhancement false. The actual body contains first frame plus description and
  those four controls. Its first frame is encoded PNG (`type`, `base64`, `format`),
  not a raw-RGBA private descriptor. Four optional caption fields described in
  some planning documents are **not** in this actual captured request.
- Exact retained transport receipt: `runtime/probes/minimax-walk/network.har`
  contains 25 entries. Zero-based entry **1** is the accepted POST to
  `/v2/animate-pixminimax` (HTTP 200); entry **24** is completed GET polling at
  `/v2/background-jobs/{job_id}` (HTTP 200), returning nine images. Header fields
  were not accessed or printed; no job IDs or image payloads were output.
  HAR SHA-256: `ec82de94d658e455c8cb6c7d86c0262ff39e33f7751825de1151f81084933a25`.
- `analysis-contract/runtime-plan/RUNTIME-CONTRACT-OBSERVATIONS.json:176-195`
  records accepted/completed, 137.75 seconds, nine returned images for eight
  requested, and binds `runtime/probes/minimax-walk/024-response.json`.
- The completed response's top-level status is completed. `last_response` contains
  an `images` array with nine entries; its observed keys contain no video blob or
  video URL. The reviewer base64-decoded all nine entries and matched every PNG
  byte-for-byte against `analysis-poses/runtime-fixtures/minimax-walk-qc/returned-000.png`
  through `returned-008.png`. Submitted first-frame PNG equals return zero exactly,
  with canvas 256×256. This is genuine returned animation-frame evidence, not an
  assumption based on a model selector or a diagnostic playback recording.
- `analysis-poses/depth-round2/source-manifest.json:2-37` independently binds
  native MiniMax frame zero and one to `/last_response/images/0/base64` and
  `/last_response/images/1/base64` in that completed response. Frame zero's PNG
  SHA-256 is `29266199aec2e9e233beff3c5656be047dd7494838df61b058da422750ecd2fb`.
- `PAID-EXPLORATION.md:17,27` preserves the separate converted-source animation:
  nine 126×124 images, first-frame alpha changed at 10,619 positions after
  background removal, with source-exact remaining opaque pixels. It also records
  narrower generated palettes without claiming that fewer colors prove improved
  gait, identity or loop quality. These converted-run observations were read from
  the report here; this review independently decoded only the native run.

## Recovered submission and placement techniques

- Godot `pixelorama-recovered/src/Extensions/PixelLab/ui/tools/AnimatePixminimax.gd:280-323`
  captures supplied first frame, optional equal-size last frame, motion description,
  count, seed, No Background and caption slots. Lines 333-337 reserve count+1
  destinations and select private alias `animate-minimax-h3`.
- `pixelorama-recovered/src/Extensions/PixelLab/Main.gd:577-580` chooses the HTTP
  background implementation for its migrated-endpoint table, otherwise WebSocket.
  `analysis-contract/depth-round2/PIPELINE-SPEC.md:11,29-33` establishes that the
  inspected table includes text-v3 but not this MiniMax alias. Therefore this
  retained private Godot MiniMax path is WebSocket; it is not the same transport
  as the successful public `/v2` probe or current MiniMax direct API.
- Lua `extension-extracted/PixelLab/generate-animate-pixminimax.lua:194-216`
  supplies selected dimensions, raw-RGBA first-frame bytes, actual description
  normalization and caption fields. Lines 229-234 reserve destinations and send
  to `animate-minimax-h3` through the WebSocket helper. The source count/size
  checks are ≤256-pixel sides and multiples of four from 4 through 40.
- `analysis-contract/depth-round2/PIPELINE-SPEC.md:21-25,39-41` separates returned
  reference skipping, reserved destination identities, quantized/original branch
  selection, raw versus encoded decode, masks/selection, and final cel placement.
  Lua's false reference marker is not a universal guarantee that current pixels
  are frozen; Godot append mode can retain the source and append returned frames.
- `analysis-poses/depth-round2/PIPELINE-SPEC.md:51-65` requires final completed
  arrays in original order, no progress-image deduplication, all nine retained,
  separate original/quantized/palette artifacts and explicit reference-role review.
  A shared palette artifact is not a motion frame. No private neural palette
  enforcement, temporal cleanup, background removal or decoder code is recovered.

## Video, ffmpeg, browser and PTS are separate evidence stages

`analysis-poses/runtime-fixtures/minimax-walk-qc/video-provenance.json:2-12` explicitly
says **derived browser-review MP4**, nine source frames, source FPS **not supplied**,
diagnostic 8 FPS, nearest display scaling and lossy H264/YUV420p checker flattening.
`analysis-poses/depth-round2/export_native_video.py:7-21` reads already-returned PNGs,
checks their hashes, composites a checker and **encodes** a six-second repeated
8-FPS MP4 with ffmpeg. It does not extract sprite frames from a provider video.
The reviewer did not rerun that script or its encoder.

Likewise, browser `.webm` recordings are browser-review artifacts. Later
`analysis-poses/depth-round3/engine-roundtrip/REPORT.md:60,68` and
`correct_video_clocks.py:9-16` document captured engine samples, prior 25-Hz concat
decimation and corrected 1-ms timebases, all samples plus a terminal duplicate and
<0.498-ms PTS error. These are engine/display-clock checks, not recovered native
model-video timing or full continuous aesthetic approval.

**No native provider-video response or its extraction procedure was established
by this bounded review.** Do not equate the absence of a video field in this one
PNG-returning probe with proof that PixelLab never uses video internally. Do not
present the local ffmpeg preview encoder as its private video-to-pixel algorithm.

## Engine attribution and current direct MiniMax boundary

The retained original `evidence/openapi.json:1` (minified; use JSON pointer
`/paths/~1animate-pixminimax/post/description`) explicitly states
“Powered by MiniMax H3.” The same operation declares POST submission returning
`background_job_id`, polling `/v2/background-jobs/{job_id}`, and completed
`last_response.images` with count+1. Its request pointer is
`/components/schemas/AnimatePixminimaxRequest`; the 200 response references
`/components/schemas/AnimatePixminimaxResponse`. This is direct retained contract
authority for H3 naming, not merely an interpretation of a client alias.

`analysis-models/MODEL-IDENTITY-RESEARCH.md:7,29,42,61` positively binds PixMiniMax
to the named MiniMax H3 engine family while leaving checkpoint/revision, fine-tune,
serving, pixel conversion, color correction and decoder configuration unknown.
The retained official card
`analysis-models/depth-round2/official-minimax-h3-readme-current.md:57,65,74-75`
describes H3 video output and first/last/reference modes. This is retained release
documentation, not proof of PixelLab's exact model or current direct H3-V2 parity.
Current OAuth chat success does not establish video endpoint authorization,
availability or successful video generation. Those remain untested here.

Preparation should reuse the real historical animation input roles and output
inventory. Keep current image-only handoff support labelled as bounded scope;
it does not replace this known animation work. A future direct-video route needs
its actual video capability/transport mapping, original returned video, codec/PTS
and extraction manifest, and explicit frame-role/clock policy. Such host handling
must be labelled separately from unavailable original PixelLab inference and
postprocessing. No new route or art algorithm was implemented in this review.

## Selected SHA-256 identities

| Evidence | SHA-256 |
| --- | --- |
| `evidence/openapi.json` | `af8ddcf710e1044455a31f091500f4381d2c89da667b2751744f734520ae93ec` |
| `runtime/probes/minimax-walk/request.json` | `1c4ee3aeba17ae3267dead91d61b17db6a1bd78b8325f2e2399e0dffd6e7eedb` |
| `runtime/probes/minimax-walk/024-response.json` | `248803c1614400acc4cca65a9000b14dc22b1e0cecb8a69f78c01ae5277fdac6` |
| `analysis-contract/runtime-plan/RUNTIME-CONTRACT-OBSERVATIONS.json` | `60ae4d6bdeeda3cf8029c40712163dc3751ff94c9f7ec92709b2293a4327e04a` |
| `pixelorama-recovered/src/Extensions/PixelLab/ui/tools/AnimatePixminimax.gd` | `514de90de8ea82fd372e2dde8e0ca5d66885d73010d16623bac83479b91f5f2f` |
| `extension-extracted/PixelLab/generate-animate-pixminimax.lua` | `77de402722626a49d006c50872898fa496c920b3ec71fa0a62b9dcdbc1c660e6` |
| `analysis-contract/depth-round2/PIPELINE-SPEC.md` | `0ab2e64d2700a5b8d522ff4f8cdbb4af313a423fda7b155b77bbdf1b4d80620f` |
| `analysis-poses/depth-round2/PIPELINE-SPEC.md` | `24379bdd4f16940f75237d3e66facbd1c954f199718987450a44e5c55c3e18e8` |
| `analysis-poses/runtime-fixtures/minimax-walk-qc/video-provenance.json` | `239809bb2624420d6f494963e71b027a8a79e1c98f397598af977a59f405105b` |
| `analysis-poses/depth-round2/export_native_video.py` | `4ec3a73acfa0d9a87ab861b05ec77872a1952112f69bf4f97bb6002b1f293428` |
| `analysis-models/MODEL-IDENTITY-RESEARCH.md` | `a880608212d7911d954aa056a1ff823bf2f8e7a451dfb0d99f337349459843bf` |
| `analysis-models/depth-round2/official-minimax-h3-readme-current.md` | `f0116a90332496bdfcc827320c603a26b849c73bf804f2674d03682fbbd2334a` |
| `analysis-poses/depth-round3/engine-roundtrip/receipts/VIDEO-CLOCK-CORRECTION.json` | `4c6efc125be985de9eb9d0eb8b71e72f3affce0db494e9f8c9033f40a2fdebb1` |

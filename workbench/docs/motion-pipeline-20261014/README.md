# Native motion to editable sprites

Version 0.8.1 extends the supplied-art Studio with a complete bounded operational route: first/optional-last PNG and literal prompt → frozen request → explicit native video job → retained video → all decoded PTS frames → explicit pose selection and rational holds → declared local conditioning → editable project/history → preview/export/readback. This is a usable testing route, not an accepted animation library or reproduction of every private PixelLab method.

## Operate locally

Start the installed package or checkout as described in the [main README](../../README.md), then open [Motion Lab](http://127.0.0.1:8874/#motion). Native examples and uploads need no credentials. Paid provider controls require the explicit `--enable-motion-provider` server option. The user's configured MiniMax environment key or existing Hermes MiniMax OAuth is read only when Submit/Poll executes. The local app never displays a credential or silently refreshes it.

Motion decoding requires host `ffmpeg`, `ffprobe` and Linux `prlimit`; recovered selection also requires Godot. The wheel contains the examples and source tools, not those host binaries. Actual live generation/decode proof covers 768P. The provider accepts a 2K request option, but 2K round trips are unverified and can exceed the 512MiB decoded-RGBA budget; supported request syntax does not certify import capacity.

1. Load a retained example, or upload then explicitly decode a video. The video player and native index inspector retain all frames and exact PTS, independent of any sprite clock.
2. Enter ordered native indices, one positive rational `[numerator,denominator]` hold and a role per pose, and an explicit loop flag. Native-derived holds require strictly increasing indices; they represent omitted motion by holding selected poses. Reordered/repeated poses require authored holds. No automatic good-cycle detector is claimed.
3. Create the sample. Playback predecodes its PNGs before drawing a canvas; frame changes do not require a network request. Select fewer poses or condition to 256 if the sample exceeds the 16M-pixel preview budget. Raw frames remain stored.
4. Optionally resize the entire canvas, choose the recovered manual seed selector, and/or map to the supplied 77-color reference palette. Each stage has a receipt. Default Keep choices preserve input pixels. Selector canvases are limited to 512 per side; Keep permits 2048 with the aggregate budget. Inspect all alpha edges and enclosed background pockets.
5. Open the candidate in Studio. Hidden-RGB normalization defaults off and requires explicit opt-in if needed. This preserves visible pixels and alpha while retaining the raw parent. It creates a composite cel project; it does not infer body parts or a rig.
6. Select/edit precise pixels, undo/redo, replay the real clock, and verify/export. Exports retain PNGs, rational timing, editable history and typed dependencies including unsampled native frames. Art review remains unreviewed after mechanical verification.

For native generation, upload a first PNG, optionally supply a last PNG (or explicitly reuse first), enter the literal prompt, prepare, and submit once. Poll manually, download the completed media, then decode explicitly. Preparation is offline. Reopening a packet returns its retained state rather than resetting its submission count. Ambiguous submission never triggers automatic retry. A 32-entry local resume list keeps attempted packets separate from the edited draft.

## Reproduce without a provider

Copy [the native attack diagnostic plan](../../examples/native-motion/plan.json) into a fresh directory, then execute it with an installed package:

```bash
sprite-workbench --workspace /absolute/path/to/fresh-store run /absolute/path/to/plan.json
```

The plan uses the packaged retained margin-slash video, keeps both fast native strike frames 26/27, gives its 16 poses an explicitly authored 48/60-second one-shot clock, and emits editable/PNG/APNG/Godot/review outputs beside the plan. This authored timing is independent of the retained 107/24-second native video. The native sword crop remains a blocker; changing timing cannot repair missing pixels. Choose a fresh output directory for another run.

The [installed-package proof](../../scripts/verify_motion_package.py) exercises actual decode, source clocks, sampling, masks/palette, cold export closure, fine edit/undo/redo, offline request reopening, CLI, JSONL and loopback HTTP. Run it with the installed Python from outside the checkout and an absent output directory. It performs no paid calls and cannot approve art.

All Motion requests share [one schema registry](../../sprite_workbench/motion_services.py): `catalog`, `load_example`, `decode`, `sample`, `condition`, `retime`, `prepare`, `submit`, `poll`, `status`, `download`, exposed as `local.motion.*`. CLI uses `motion METHOD REQUEST.json`; JSONL uses `{id,method,params}`; HTTP uses `/api/invoke`; plans use `{action:"motion",method,request}`. Plans always disable paid execution, even when their HTTP controller permits explicit standalone calls. [CLI/JSONL conventions](../COMMANDS.md) still apply.

## What is reproduced and what is local

| Stage | Evidence and boundary |
|---|---|
| Manual connected seed selection | Runs unchanged recovered Godot host selector code, with its own source manifest and execution receipt. It is a manual selection tool, not PixelLab's private automatic matte. |
| Fixed supplied-palette mapping | Calibrated Oklab distance with quarter-weight lightness. Exact replay matches retained nondithered probes; palette clustering, tie behavior outside the probes and neural deflicker are not recovered. |
| Native MiniMax video | Documented H3 request/poll route, exact request bytes and retained response/download. PixelLab's own underlying model checkpoint is unknown. |
| Decode, pose choice, holds, whole-canvas resize, editor, history, exports | Explicit local engineering decisions with tests and receipts. They are never labelled recovered private algorithms. |
| Codex image generation and other model outputs | Model Lab prepares interchangeable handoffs; actual external results can enter Studio/video admission. This does not make an image tool and a video model equivalent or claim automatic local image execution. |

See [official provider research](PROVIDER-RESEARCH.md), [decode limits and clocks](VIDEO-EXTRACTION.md), [conditioning adversarial tests](CONDITIONING-REVIEW.md), [UI verification](MOTION-UI.md) and [acceptance gates](ANIMATION-ACCEPTANCE.md).

## New retained experiment and actual repair

The artifact root is [/home/astra/artifacts/pixellab-motion-pipeline-20261014](/home/astra/artifacts/pixellab-motion-pipeline-20261014). `EXPERIMENT.json` froze exactly two 4-second native requests sharing one generic hero PNG and literal walk prompt: first-only versus same-PNG first-and-last. Both succeeded and each actually decoded 107 frames at 768×768 with duration 107/24 seconds. `LIVE-SUBMISSION.json`, `LIVE-RESULTS.json` and `LIVE-DECODED.json` bind packet/task/video/extraction identities. Four sanitized retained POST/final-poll captures were inspected offline using REA; `REA-CURRENT-SUMMARY.json` lists their IDs and verified HAR hashes. This verifies our retained observation, not independent private-service attestation.

The [independent walk review](LIVE-WALK-REVIEW.md) prefers first-and-last as an authoring source in this pair, while rejecting seamless-loop approval. Only two stochastic samples were run; they do not establish causal efficacy. First-only changes black to near-white backdrop and turns more frontally. First-and-last has clearer alternating legs but changing blade/shield pose. The provisional 8-phase interval `[18,58)` has a 5/3-second diagnostic clock and remains unapproved. The earlier 16-phase `[16,52)` selection is preserved and explicitly superseded as a proposed full-cycle cut.

`MANUAL-POCKET-EDIT.json` records one actual precision-edit demonstration: exact-black 207-pixel suspected background pocket in native 33/phase 3, seed XY `[110,120]`, tolerance 0. All other seven frames and every pixel outside the mask remain exact; undo/redo restore their exact project IDs. The ambiguous pocket in 38 was left unchanged. Raw references, normalization, recovered mask, guarded edit receipt, full native source and export are retained. This is a candidate repair, not a ground-truth segmentation or finished art approval. [Before/after image](/home/astra/artifacts/pixellab-motion-pipeline-20261014/review/manual-pocket-before-after.png).

Remaining work is specific: trustworthy alpha cleanup across all poses, sword/grip/shield consistency, measured contact phases, a reviewed wrap, additional directions/actions, complete normal-speed visual approval and accepted game-scale quality. Native cropping needs an explicit painted repair or regeneration; background removal cannot recover missing anatomy. Do not expand a library or award 9/10 until these pass.

## Portable binding correction in v0.8.1

The first v0.8 export retained all native raster payloads, PTS and video, but sampling through an extraction ID could omit upstream provider packet/download receipts and packaged input/request bindings. v0.8.1 attaches those bindings to the extraction itself and follows them through cold export. New regression tests exercise the complete decode → sample → condition → Studio → cold import path, including exact request wire bytes, input PNG, native admission/completion and download receipts, and an unsampled native frame. Old exports and their evidence remain preserved; corrected derivatives use new identities while keeping pixel content and clocks exact. The [independent current-export proof](BOUND-WALK-PROOF.md) verifies 146 cold-closure predicates and 74 actual Godot checks, including three normal elapsed cycles of the same eight-pose repaired walk. Mechanical acceptance still leaves art/contact/edge approval open.

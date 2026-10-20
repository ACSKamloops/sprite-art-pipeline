# Accepted hero walk reproduction recipe

> This is the audited historical recipe. Stage names and path suffixes below refer to the preserved research archive. For current portable operations, use the map here and START-HERE.md; historical receipt statuses are not the current approval overlay.

| Current package file | Role |
| --- | --- |
| `references/submitted-appearance384.png` | Exact historical Image1 |
| `reproduction/submitted-motion-guide.mp4` | Exact original dithered Video1 |
| `reproduction/submitted-prompt.txt` | Literal historical prompt |
| `reproduction/returned-h3-native.mp4` | Complete native return |
| `reproduction/submitted-request-parameters.json` | Sanitized actual fields |
| `tools/bake_native_sprites.py` + `reproduction/bake-recipe.json` | Preferred portable offline bake |
| `providers/minimax_h3/runner.py` | Staged provider adapter; offline preparation tested |
| `approved/walk/manifest.json` + `approvals/walk.user.json` | Current portable art and acceptance |


The user accepted the H3 first-cycle despilled walk as the walk baseline. Preserve its 30 original poses, 128 × 128 canvas and exact 1/24-second holds. This records the actual accepted chain so the same hero can enter an attack or jump phase; it does not claim those actions already exist or assign a numeric art score. Historical candidate and approval receipts stay unchanged; the new acceptance belongs in the project hub overlay.

## Actual source chain

| Stage | Retained source | Meaning |
| --- | --- | --- |
| Physical controls | `grounded-pose-controls-EAEAEA/raised-low-swing/CONTINUOUS-160-32HZ-5S.json` | Authored 3D contact and IK model, not inferred private PixelLab internals. |
| Submitted motion | `grounded-motion-guide-ECECEC/low-swing/initial-dithered/guide-384-32fps.mp4` | Original dithered low-swing guide, 160 frames at 32 Hz, 384 square, 5 seconds. |
| Provider job | `h3-grounded-guide-EFEFEF/job-001` | Exact image, video, prompt, sanitized request/response and retained returned video. |
| Complete bake | `h3-grounded-bake-EJEJEJ` | All 124 returned frames retained at native 24 Hz, including the final four frames. |
| Selected walk | `h3-grounded-loop-EOEOEO/despill30` | Original source indices 0..29, exact native timing; user-approved walk baseline. |
| Engine consumer | `engine-grounded-h3-ERERER` | Godot mechanics, texture import and clock verification. |
| Editable exchange | `editable-grounded-hero-ETETET` | One unlocked flat cel layer, 30 complete poses and exact timing sidecar. |

All paths above are relative to `/home/astra/artifacts/pixellab-hybrid-walk-20261015/game-ready-v6`. Absolute paths and SHA-256 values are in [EVIDENCE-INDEX.json](../evidence/method-recipe/EVIDENCE-INDEX.json).

**The current zero-dither EC sparse frames are not the submitted guide.** The accepted request used the preserved `low-swing/initial-dithered` sequence: Blender EEVEE 5.2.0 LTS, dither 1 and 64 TAA samples. The later current folder uses dither 0 and 16 samples. Their frame 0000 hashes differ. Use the exact retained provider input MP4 when reproducing the accepted request.

The physical bank has a 40-sample, 1.25-second period repeated four times. Thirty low-swing poses were newly rendered; ten unchanged stance renders were reused after exact geometry comparison. Each frame i≥40 copies i%40 after root-relative periodicity verification. The provider input is H.264 YUV420 and is lossy; the retained RGB lossless guide verifies the original 160 frame sequence. The bank authors root screen velocity (32, 6.656) px/s, rigid heel/flat/toe contacts, lower-leg IK, camera and swing height. Upper-body template keys are periodically quintic-eased relative to the pelvis. These authored mechanics do not certify that the generated hero preserves physical contacts.

## Exact provider inputs

The submitted appearance came from `imagegen16-finish-DSDSDS/global-y-minus1/frames/00.png` (96 square; SHA `c9be77f29ebe63ca1ef540e84b5940089a126b1a21fc981cfc5a3aa7415e1ce5`), composited at (+16,+16) on a green 128-square canvas and enlarged nearest 3x to 384. This transform was rechecked against the actual retained image.

Ordered request content was literal text, Image1 with role `reference_image`, then Video1 with role `reference_video`. Actual fields were `model="MiniMax-H3"`, `resolution="768P"`, integer `duration=5`, `ratio="1:1"`. There was no seed, first-frame, last-frame or control-strength field. [SANITIZED-REQUEST-PARAMETERS.json](../evidence/method-recipe/SANITIZED-REQUEST-PARAMETERS.json) retains the fields, literal text and media paths/hashes without base64 or credentials. The embedded historical wire media bytes match the retained input files exactly.

| Artifact | Exact retained path suffix | SHA-256 |
| --- | --- | --- |
| Image1 | `h3-grounded-guide-EFEFEF/job-001/inputs/image-1.png` | `345e791427d2b20b97fd661aaae9e947f8197ee27984581a597f0bc78886e0db` |
| Video1 | `h3-grounded-guide-EFEFEF/job-001/inputs/video-1.mp4` | `c241b9315a39e349c2cd4d197de3b8a03e675aed1a66e870671b9911d341f04b` |
| Literal prompt | `h3-grounded-guide-EFEFEF/job-001/PROMPT.txt` | `b90820a74f9f5f469267729bfa06fb4f4c890eef785f048de54d84a02bdeb8c1` |
| Returned video | `h3-grounded-guide-EFEFEF/job-001/native-video.mp4` | `5cf8d962cbb9ea32363b9db8031dee4b46af721e8ad851d575d9fc20f9518430` |

The literal prompt is preserved verbatim in [LITERAL-PROMPT.txt](../evidence/method-recipe/LITERAL-PROMPT.txt). The completed response reports MiniMax-H3, 768P, 1:1 and succeeded status. Actual returned video decodes to 768-square RGB, 124 frames at 24 Hz, duration 31/6 seconds—not the requested 5 seconds. Probe and retain actual timestamps on every new result rather than assuming the requested duration or a prior frame count.

## Local fixed cutout

The executable [reproduce_local_cutout.py](../evidence/method-recipe/reproduce_local_cutout.py) requires only Python, NumPy, Pillow, ffmpeg and ffprobe. It writes only to a new output directory and makes no API call. It reproduces this specific retained source, not a general untested matte for future actions.

1. Decode all 124 native 768-square frames in presentation order with `-fps_mode passthrough`; retain source PTS i/24 and each hold 1/24.
2. Sample the whole canvas once into 128 square: output(x,y) = source(6x+3,6y+3). Do not fit, crop, align or rescale individual poses.
3. At sampled RGB, set alpha 0 exactly when G≥90 and G−R≥45 and G−B≥45; otherwise set alpha 255. Keep every RGB value, including hidden RGB under alpha 0, unchanged.
4. Retain the complete 124-frame bake. The walk branch explicitly copies only original frames 0..29. Their PTS are 0..29/24, their unchanged holds total 5/4 seconds, and looping is a branch decision rather than a claim about the whole source.
5. Keep a byte-exact raw-matte30 comparison. For the accepted despill30 branch only, every opaque pixel with G>max(R,B) gets G=max(R,B). R, B, alpha, all unselected pixels and all hidden RGBA remain exact. No spatial mask, component deletion, repaint or per-pose adjustment is applied.
6. Record every edited pixel as frame, x/y, full before/after RGBA. There are exactly 3525 changed pixel occurrences across the 30 frames. Replay and undo must each reconstruct their originals exactly.

The retained historical APNGs store exact rational holds. The EO movie presents 120 frames at 24 Hz over four loops/5 seconds; lossless RGB and portable YUV previews are distinct evidence. Successful export is not an art score.

## Callable provider path and safe staging

The tested source is `h3-grounded-guide-EFEFEF/runner.py`, relative `transport/minimax_h3_pilot.py`, and `docs/openapi-create.json`. Copy those safe source files together, without credential profiles, environment snapshots, historical job state, gate or submission lock. The runner uses relative paths for its transport and code pins, and prepares only a new strict child run directory. It requires Pillow and ffprobe for offline media validation.

The actual endpoint is POST `https://api.minimax.io/v2/video_generation`; polling uses GET `/v2/query/video_generation/{validated_task_id}`. The runtime loader checks the two named API-key environment variables, then the existing external Hermes OAuth entry. No credential file or environment value was opened in this audit. The platform-specific fallback path and dependency details are recorded in [PROVIDER-PORTABILITY.json](../evidence/method-recipe/PROVIDER-PORTABILITY.json). Expired OAuth is rejected; no silent refresh occurs. The transport redacts credential strings, the runner redacts result URLs, and output downloads forward no Authorization and follow no redirects.

Offline preparation has a real callable interface. `runner.py prepare --run <new-child-run> --image <Image1> --video <Video1> --prompt <prompt> --provenance <guide-provenance> --duration 5 --ratio 1:1` is the parser-derived fresh-run shape, not a claim that this exact shell argv was captured historically. The duration flag matters: its default is 4. `runner.py validate --run <new-child-run>` checks hashes and media correspondence. New submission is a separate network action, guarded by a freshly reviewed, request-hash-bound gate and one-attempt lock; do not reuse the original job gate or infer authorization to submit from these documents.

## Historical commands and rerun limits

[COMMANDS.json](../evidence/method-recipe/COMMANDS.json) distinguishes actual captured argv, documented entry points and parser-derived invocation shapes. ET's two actual LibreSprite save/reopen/export commands are retained verbatim in its exchange receipt. ER documents `python3 launch.py --verify --xvfb`; final Godot logs, tested-code pins and receipts bind that output. Complete original parent shell argv is not separately retained for every build stage, so reconstructed commands are labeled accordingly.

The old scripts are artifact-specific. EJ `prepare.py` writes beside itself; EO `build.py` hardcodes the sibling EJ manifest SHA and overwrites outputs; the EC renderer skips existing frames and must never mix settings in one directory; ER verification rewrites consumer imports, evidence and movies; `build_editable_ET.py` hardcodes ET and rejects an existing output directory. Preserve originals, stage fresh destinations and rebind paths deliberately. ET rebuild also requires `editable-v7-BVBVBV/toolkit/sprite_lab` (eight Python files indexed by hash) and LibreSprite. EJ's local cutout has no hidden source image or shared workbench module dependency beyond the retained video and its listed software tools.

## Verified state and remaining limits

This read-only audit rechecked 820 historical freeze entries, ten provider input/code pins, 13 tested ER code pins and all 16 authored-template upstream pins. It independently decoded the returned video to all 124 EJ frames, recomputed every fixed NN/matte pixel, recomputed all 30 despill outputs and replayed/undid all 3525 journal edits. ET's current source bytes and all 30 exported alpha/visible RGBA poses still match. The current audit did not launch an engine, editor or API. The new local cutout command was actually executed into `reproduction-test`: all 432 native/raw/matte/selected PNG pixel arrays and all 3525 journal changes match the historical outputs. PNG file bytes also match in this current environment; preserve pixel/timing checks across software versions.

ER historical checks cover all 30 imports/GPU-visible poses, nearest 1x/2x/4x and 450 deterministic viewport ticks at 120 Hz (five ticks per pose, three cycles). A separate live AnimatedSprite clock test covers two wraps. Rendering used Xvfb/OpenGL software llvmpipe, with synthetic controls. World velocity (36.5,5.1) px/s is an uncalibrated visual hypothesis, distinct from the guide's authored velocity. ±1 px planting, contact lock, controller feel, hardware GPU behavior, collisions and action transitions remain unverified.

ET preserves one flat layer, not separable anatomy or a limb rig. LibreSprite normalizes hidden RGB; source PNGs preserve the originals. Editor 41/42 ms holds total 1250 ms with at most 1/3 ms boundary error; retain the adjacent sprite-lab sidecar for exact 24 Hz semantics.

Exact provider regeneration is not guaranteed: no seed, immutable backend build/weights or historical environment lock was retained. The original safe media and returned source therefore anchor exact local reproduction. Software package versions beyond the recorded Blender/Godot identities are not locked. Some old sparse metadata contains original absolute paths whose current files differ; use the frozen dithered manifest and input hashes. An attack or jump needs its own authored motion guide, action timing and endpoint/transition review; do not transfer this walk's 30-frame window or `loop=true` automatically.

EO despill30 is accepted. EJ full124 remains the immutable source bake; raw-matte30 remains a comparison; ER and ET are consumers. FA is the later painted alternate with user-observed hesitation. The two GNG timing controls remain optional diagnostics, not baseline replacements. No new score or additional generation was performed.

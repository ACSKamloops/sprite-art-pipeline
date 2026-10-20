# Bounded local video admission and authored sampling

This module admits supplied local video bytes into the existing immutable Store.
It is **authored local video import**, not recovery of PixelLab's private frame
sampler, segmentation, quantizer, deflicker, captioning or generative backend.
No provider calls or new art were made. Visual acceptance remains unreviewed.

## API and immutable evidence

```python
from pathlib import Path
from sprite_workbench.core import Store
from sprite_workbench.motion_frames import extract_video, sample_frames

store = Store('/some/local/store')
result = extract_video(store, Path('/some/local/source.mp4').read_bytes())
# result: media, extraction, sequence, frame_count, canvas, duration, clock_note
sample = sample_frames(store, result['extraction'],
    indices=[0, 26, 27, 27, 106],
    holds=[[1, 24], [1, 24], [1, 12], [1, 24], [1, 6]],
    loop=False,
    roles=['anticipation', 'strike', 'strike', 'authored repeated hold', 'recovery'])
# sample: sequence, decision, extraction, media, frame_count, duration
```

The example's indices/holds/roles are explicit inspection choices; they are not
recommended game timing, automatic attack detection or recovered PixelLab rules.
Inputs are bytes, never decoder paths, URLs, executable names or filter strings.
Callers handling paths should bound their reads before passing bytes.

`motion-extraction` retains the original media blob/hash; raw ffprobe JSON;
local executable binary hashes/version strings; full-canvas raster records;
integer PTS array, rational stream time base and original first PTS; rational
holds and total duration; terminal-duration basis; alpha policy. Raster artifacts
retain exact decoded RGBA blobs via existing Store storage. Decoder conversion
from compressed video to RGBA is recorded; it does not claim original sensor RGB
or cross-version codec equivalence. Binary hashes do not pin dynamically linked
libraries; all decoded raster bytes are independently pinned.

Native sequence holds are adjacent PTS differences, with the final hold from the
last frame's declared duration, or explicitly recorded stream-end fallback.
Nonmonotonic/missing PTS or missing terminal duration reject admission. The native
sequence plays once for inspection; that playback policy is authored and does
not assert that a video container declares one-shot sprite behavior. There is
no FPS rounding or inferred loop. Absolute PTS origin remains in the receipt.

`motion-sample-decision` retains one ordered entry per requested sample, including
sample index, native index, native PTS, unchanged raster ID, role and rational
hold. Repeated/out-of-order indices remain explicit; no deduplication occurs.
The sample sequence references this decision, extraction and original media.
Pivots `[0, 0]` and direction `unspecified` are explicit neutral metadata; no root
registration or directional inference occurs. Opaque video remains opaque.

## Admission limits and failure behavior

- Immutable supplied bytes: 1 byte through 64 MiB.
- First video stream only; MP4/MOV and Matroska/WebM demuxers only. Fixed
  `file,pipe` protocol whitelist; stdin closed, fixed local temporary source.
- 1–512 native frames, sides at most 2048 pixels; total RGBA at most 512 MiB.
  ffprobe reads at most 514 packets; the decoder emits at most 513 frames, so
  over-budget videos reject instead of being silently truncated. Probe/decode
  counts and each probed native dimension must agree.
- Combined 60-second deadline; child CPU limit 60 seconds; address-space limit
  2 GiB; output-file limits (probe 4 MiB, decode 512 MiB), core dumps disabled;
  decoder threads fixed to one. Limits are set by the external Linux `prlimit`
  executable before FFmpeg/ffprobe starts, without Python `preexec_fn`; this is
  safe to launch from the threaded server/job manager. Missing `prlimit` returns
  a validation failure with retained media; limits are never silently disabled.
  These process limits target Linux/WSL.
- No autorotation, resampling, crop, scaling, recentering, cutout or hidden-RGB
  normalization. Compressed video decoding/pixel-format conversion is FFmpeg's.
- Invalid byte admission writes nothing. Once bytes are admitted, decode/probe
  failure retains original media and a bounded `motion-extraction-failure`
  receipt; `VideoExtractionError.receipt` / `.to_dict()['extraction_failure']`
  exposes that ID. Temporary process outputs are cleaned; retained failures do
  not falsely present a successful partial sequence.

The timestamp/size checks are admission rules, not a general multimedia sandbox.
Resource limits cap individual process/output budgets; callers must separately
bound concurrent jobs and their aggregate storage. Missing FFmpeg rejects with
retained evidence and no fallback implementation.

## Verification

Targeted command:

```
/home/astra/projects/pixellab-local-workbench/.venv/bin/python -m pytest -q tests/test_motion_frames.py
```

Completed result: **19 passed in 8.98 seconds**, including the external pilot
check on this machine. FFmpeg version: 8.0.1-3ubuntu2.

The suite covers a tiny lossless alpha fixture; all decoded RGBA including
partial alpha and hidden RGB; nonuniform millisecond PTS; explicit repeated and
reversed samples; malformed sample controls with no new Store writes; invalid
media failure retention; rejected path/URL/mutable input; clock/size guards;
and a real 513-frame 8×8 clip rejected without truncation.

The local retained-pilot check additionally uses:

- `/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014/h3-slash-margin-002/native-video.mp4`
  SHA256 `aed5ac139188860f2e3e39f58484ebda394c77fa7b8ae99f777cced03c572132`.
- Prior media-review manifest SHA256
  `3a5dbd5fc20ad06eefca5629cd6888e3a7caa3523acce3f08b0812abb3ae2186`.
- All 107 native frames, 768×768, integer ticks separated by 512 at time base
  1/12288, holds exactly 1/24 second, total 107/24 seconds. Alpha remains 255.
- Every frame compared pixel-for-pixel against the retained
  `media-review/decoded-native/frame-000000.png` through `frame-000106.png`;
  all match. This is a pixel/clock check, not continuous visual playback.
- Explicit 16-sample test includes native indices
  `0,12,18,23,24,25,26,27,28,35,52,73,78,85,94,106`; chosen raster IDs match
  native extraction IDs exactly. These test holds are authored, not game tuning.

The pilot test skips when that external artifact is absent; ordinary lossless
codec checks still run with installed local FFmpeg. No external PNGs/video are
packaged or regenerated by these tests.

## Integration boundary

Root orchestration owns service exposure, job queues, UI, packaging and
export.py. The current export traversal needs explicit new-kind handling:
`motion-extraction` → media/probe as raw blobs and every frame raster as document;
`motion-sample-decision` → extraction document + media blob;
`motion-extraction-failure` → media blob. Sequences already list the new evidence
in metadata `source_ids`, but that alone does not recursively close new document
kinds. Do not claim fresh-Store portable closure until those integration checks
pass. No root runtime files were edited in this task.

## Complete extraction document shape (threaded-launch follow-up)

`store.get_json(result['extraction'])` is an immutable document with these fields:

```text
kind: "motion-extraction"
version: 1
policy: "authored local video import; not a recovered PixelLab private sampler"
media: SHA256 raw-byte artifact ID
media_sha256: same SHA256
probe: SHA256 raw ffprobe JSON byte artifact ID
tools:
  ffprobe: {path: absolute local executable path, binary_sha256: SHA256, version: first version line}
  ffmpeg:  {path: absolute local executable path, binary_sha256: SHA256, version: first version line}
canvas: [width, height]
frame_count: integer 1..512
frames: [
  {index: zero-based native index, pts: integer source PTS,
   raster: RGBA artifact ID, duration: [positive numerator, denominator],
   pivot: [0, 0], direction: "unspecified"}, ...
]
pts: [integer source PTS, ...] # same order/values as frames[*].pts
time_base: [positive numerator, denominator]
pts_origin: original first integer PTS
duration: [positive numerator, denominator] # sum of native holds
terminal_duration_basis: "last decoded frame duration" | "stream end timestamp minus last frame PTS"
native_clock: "integer presentation timestamps; adjacent PTS differences; terminal duration declared separately"
decode: "first video stream; RGBA conversion; no autorotation/scaling/crop/deduplication"
opaque: boolean # all decoded alpha samples == 255
alpha_policy: "decoded alpha retained; no reconstruction or cutout"
source_ids: [media artifact ID, probe artifact ID]
visual_acceptance: "unreviewed"
```

Use each frame's `duration` for native holds, and `pts * time_base` for absolute
presentation position. The `pts` array remains available for existing callers.
Frames include `pts` directly so UI callers need no parallel-array assumptions.
`prlimit` bounds all decoder/version processes with address space 2147483648,
CPU 60, the per-output file limit, and core size 0. Two simultaneous tiny lossless
decodes are tested through `ThreadPoolExecutor(max_workers=2)` against the same
immutable Store; both preserve exact alpha/RGBA and return the same IDs.

Follow-up verification: **21 passed in 3.86 seconds** for the same targeted suite,
including the simultaneous-thread regression, unavailable-prlimit validation,
and the real 107-frame native pilot. The earlier 19-test result is retained above
as the original baseline, before this launch-safety correction.

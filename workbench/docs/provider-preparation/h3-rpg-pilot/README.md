# Matched PixelLab / direct-H3 RPG hero pilot

**Three matched service comparisons are complete. PixelLab's delivered sprite
arrays are currently more useful than direct H3 plus our simple local extraction.**
This resolves the missing same-subject comparison. It does not recover PixelLab's
private inference/conversion or approve any animation as production art.

Open the local [comparison gallery](http://localhost:8875/). If the task server
has stopped, run:

```bash
python3 -m http.server 8875 --bind 127.0.0.1 --directory /home/astra/artifacts/pixellab-h3-rpg-pilot-20261014
```

Artifacts: `/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014/`.
The [independent visual comparison](MATCHED-VISUAL-COMPARISON.md) identifies actual
frame indices, reviewed contact pages, individual views and remaining defects.
Its coverage is not a claim of continuous visual video review.

## Inputs, controls and actual calls

The user requested an original generic RPG hero instead of the Warhammer
Captain. One built-in image-generation call made the master; its original PNG
and exact brief are retained in `inputs/`. No Captain image was sent to native
H3 in this pilot. The master was resized as one whole canvas to 256px using
nearest-neighbor. A second input scales that canvas to 192px and pastes it at
(32,32) inside a transparent 256px canvas. This 75% actor-scale change is explicit;
it is not a corrected universal game anchor or a same-scale unit pack.

| Pair | Exact input within pair | Exact motion prompt within pair | Native run | PixelLab run |
| --- | --- | --- | --- | --- |
| Walk | `inputs/hero-256.png` | `inputs/walk-prompt.txt` | `h3-walk-001` | `pixellab-walk-v1` |
| Slash | `inputs/hero-256.png` | `inputs/slash-prompt.txt` | `h3-slash-001` | `pixellab-slash-v1` |
| Slash with margin | `inputs/hero-motion-margin-v2.png` | `inputs/slash-prompt.txt` | `h3-slash-margin-002` | `pixellab-slash-margin-v2` |

There were three native H3 submissions and three PixelLab submissions, with no
automatic generation retries. The native H3 requests use MiniMax-H3, first-frame
conditioning, duration4, 768P and adaptive ratio, without a last frame or
H3-Context-IR request. PixelLab uses `/v2/animate-pixminimax`, first-frame input,
16 generated frames, seed123, `no_background=true`, `enhance_prompt=false`.
The four caption fields and drift threshold are omitted. Caption omission can
still allow automatic server captioning. Native H3 has no matching typed sprite
seed, count, alpha, drift or caption controls here. Full conditioning and the
private checkpoint/revision are not established as identical.

The numeric PixelLab balance changed from4750.15 to4744.15 subscription
generations: **six generations for these three jobs**, with USD balance0.
Native service usage reports four seconds per job; actual returned media are
107 frames at24FPS, presentation end107/24 seconds. Usage duration and decoded
duration are deliberately separate. No dollar-price estimate is inferred.

## What REA and the retained outputs prove

Every PixelLab call was recorded by the actual HTTP producer with authorization
and cookies omitted before persistence. Completed captures were frozen as
`network-final.har`; REA inspected submission ordinal0 and completed ordinal2
for each case. `REA-FINAL.json` binds each import to its frozen HAR SHA-256.
These are offline producer captures, not browser instrumentation or evidence of
the private server's code. REA's authority is `historical-reference`.

The offline verifier rechecks exact input PNG bytes and literal UTF-8 prompts,
actual REA/HAR request and result bindings, all51 ordered returned PNGs and all321
decoded native H3 PNG hashes. Reference0 remains separate from16 generated
frames; no duplicates or inconvenient frames are silently removed.

Observed generated PixelLab frames have binary alpha and compact visible RGB
palettes: walk76–88, original slash68–83 and margin slash77–86 colors per frame.
None of the48 generated PNGs touches a canvas border with alpha>0. Both native
H3 attacks show visually confirmed physical sword clipping. Border screens
flag possible defects; they are not automatically weapon-specific diagnoses.

Returned reference0 differs only in RGB hidden under alpha0:49,49 and30 changed
pixels respectively. Its alpha and visible RGB are exact. Zeroing hidden RGB
replays every reference0 exactly, matching the behavior of recovered
`get_image.gd:101-108`. This supports a specific normalization policy, without
proving which private server code ran. It is not a visible redraw.

Recovered client caption serialization, first/last validation, reference/count
roles, codec preparation and editor assembly remain the method authorities in
the [source protocol](../../source-faithful/H3-PILOT-SOURCE-PROTOCOL.md) and
[comparison boundaries](COMPARISON-BOUNDARIES.md). The server's video sampling,
alpha generation, quantization and de-flicker algorithms remain unknown.
The returned `smoothing frames` action is a status label, not an implementation.

## Local conversion and playback verification

Local extraction is explicitly `local-border-connected-black-key-v1`: zero alpha
for RGB<=12 pixels connected to the canvas border, preserve all source RGB, then
resize the whole canvas to256px using nearest-neighbor. It can erase connected
dark outlines or retain codec fringes. It is an independent diagnostic
implementation, not a recovered PixelLab conversion.

The proposed H3 walk uses native interval[16,64), with8/16 samples and an authored
two-second loop clock. The original attacks keep full interval[0,107), native
PTS-derived holds and one-shot completion/replay semantics. Rejected exports are
retained as `sprite-once-rejected`. Uniform margin-attack sampling skipped actual
strike frames26/27; this is a **local sampler defect**, separate from native H3's
clipped blade. A separately retained manual-index export addresses coverage only;
it cannot restore the missing blade pixels or establish PixelLab's sampler.

Browser evidence distinguishes mechanical behavior from aesthetic acceptance:

- Native walk played at1x to its actual end with107 monotonic video-frame
  callbacks and zero reported dropped frames.
- Local walk traversed all16 samples, wrapped, paused, stepped and switched8/16
  variants while preserving phase.
- Original slash completed at its last pose, ignored Play after completion,
  clamped Step and restarted only through Replay.
- All three PixelLab inspection players loaded their16 generated slots, kept
  reference0 separate, paused and sought the last slot without browser errors.
  Their two-second clock is analyst authored. Attack inspection looping is not
  approved one-shot gameplay timing or recovered PixelLab FPS.
- The curated margin slash displayed all16 explicit poses at1x, including26/27,
  and held its terminal pose. The [curated slash review](CURATED-SLASH-REVIEW.md)
  still rejects it for missing blade tips and ambiguous strike/grip presentation.

See `browser-evidence/` for scripts, original CLI logs, parsed results and
screenshots. Failed selector harness attempts are retained separately and do
not count as passes. A working player does not prove a good animation.

## Repeat the evidence checks without spending credits

From `/home/astra/projects/pixellab-local-workbench`:

```bash
python3 scripts/verify_h3_pixellab_comparison.py /home/astra/artifacts/pixellab-h3-rpg-pilot-20261014 --output /tmp/h3-pixellab-recheck.json
python3 -m pytest -q tests/test_minimax_h3_pilot.py tests/test_pixellab_h3_comparison.py tests/test_extract_h3_sprite_cycle.py
```

Generation scripts are separate from this offline verifier. Preparation freezes
source/request identity. Submission writes a persistent claim before one POST;
restarting an ambiguous submission does not automatically resubmit. That guard
is not a power-loss/fsync transaction or a provider-side idempotency guarantee.
Credentials are read only when needed, remain in process and are omitted from
retained HTTP records. Native CDN downloads carry no provider Authorization.
The [controls review](FINAL-CONTROLS-REVIEW.md) found and corrected a response
scrubbing edge case using fake credentials only: JSON Unicode escapes could
hide an echoed token until parsing. Both decoded keys and values are now scrubbed;
sanitized HAR response text is explicitly marked while its original-byte hash
is retained. No real credential leak was established by that review.

The current scripts are CLI research channels. The existing packaged v0.6
workbench runtime and its still/edit UI were not modified. These H3 routes have
not been integrated into that UI, and the old package proof remains a dated
snapshot, not proof of these later model calls.

Validation: **62 focused checks and 622 full-suite tests passed**. The full suite
reported1400 warnings, principally existing Pillow/importlib deprecations. See
[verification](VERIFICATION.json) and the original [suite log](evidence/full-suite.log).
The offline replay found no failures across3 pairs,51 PixelLab PNGs and321 native
decoded frames. These mechanical passes do not change the rejected art status.

## Next useful gate

The next comparison should test phase-aware key-pose selection and exact holds,
sprite alpha on varied backgrounds, equipment continuity, loop seams and foot
contact against these retained PixelLab outputs. Compare raw outputs separately
from equally curated conversions. Shared unit scale/anchors must be corrected
before combining margin input results with the original walk in one character.
No animation here has9/10 acceptance. Further generation is not needed to inspect
these concrete gaps, and private PixelLab algorithms must remain labeled unknown
unless new evidence actually recovers them.

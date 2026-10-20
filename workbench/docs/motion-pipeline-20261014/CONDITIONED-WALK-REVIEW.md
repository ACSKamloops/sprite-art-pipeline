# Conditioned walk and manual-pocket review

The conditioned frames are usable **authoring candidates**, with the same
motion/anatomy limits identified in [the raw review](LIVE-WALK-REVIEW.md).
First-last remains my preferred source in this pair. Neither conditioning nor
the single-pocket repair establishes a finished seamless walk or a numerical
quality target. This report preserves the earlier review unchanged.

## What was compared

Read-only inputs are `CONDITIONED-WALKS.json`,
`DIAGNOSTIC-WALKS-8PHASE.json` and `MANUAL-POCKET-EDIT.json` under
`/home/astra/artifacts/pixellab-motion-pipeline-20261014`.
The original16-sample diagnostic uses native indices
`16,18,20,22,25,27,29,31,34,36,38,40,43,45,47,49`, recorded
1/12 and1/8 holds for3/2seconds over the declared `[16,52)` interval.
It was not approved as a complete gait cycle.

The newer eight-phase diagnostic uses
`18,23,28,33,38,43,48,53`, each held5/24second, totaling5/3seconds over
`[18,58)`. Its looping flag is an authored inspection choice.

I compared all32 original conditioned frames on checkerboards, the exact
resized inputs, recorded alpha masks, pre-palette cutouts and final palettes;
then both new eight-phase checker sheets and enlarged blade/arm details.
Immutable raster hashes and output alpha were checked directly. Inspection
artifacts are separately retained under
`/home/astra/artifacts/pixellab-conditioned-walk-review-20261014`.

## Observed conditioning changes and remaining defects

- **Resize:** whole-canvas768→256 nearest sampling preserves framing but loses
  fine generated face, armor and boot shading. It does not recover a latent
  original pixel grid or turn the model's illustrated/video edges into an
  artist-validated sprite outline.
- **Mask:** the recovered corner-connected selector removes the large black
  or white exterior without relocating the character. It leaves enclosed
  background-looking pockets. First-last native33/38 show a dark region in
  the sword-arm/torso gap; broadening the tolerance is unsafe because nearby
  straps, glove edges and cloth shadows are legitimate dark material. No
  semantic ground-truth segmentation is available.
- **Edges:** first-only shows retained pale edge pixels against magenta/checker,
  including the sword/armor outline. This opaque white-background video has
  already mixed edge colors with the background; a binary flood mask does not
  recover an original soft alpha matte. The enlarged blade is still present;
  I do not substantiate a gross missing-blade claim.
- **Palette:** the77-entry fixed reference visibly makes some silver highlights
  warmer/cream and produces chunkier tonal bands. Shape/alpha changes are not
  a result of palette mapping: measured final alpha exactly matches the
  reconstructed pre-palette cutout in every checked frame. Old16-frame totals
  change102,767 visible RGB pixels for first-last and117,901 for first-only;
  these counts describe quantization, **not a quality score**.
- **Motion:** original torso yaw, shield exposure, grip/boot variation and
  possible contact sliding remain. No gross frame-border gear clipping is
  apparent. Neither masking nor palette reduction repairs a poor pose or
  supplies stable rigid gear/joint behavior.

## Actual local playback, with a limited conclusion

A fresh isolated headless Chromium session played six local canvases:
native `[18,58)` at1/24second per frame, sampled8 and conditioned8 at their
declared5/24 holds, for each case. A retained trace snapshot reports all
expected indices, both `57→18` and `53→18` wraps, no page errors and121
scheduler wraps per player. The confirmed viewport recording and screenshot
are under `output/playwright/` in the QA directory. The first attempted
recording had a malformed wait command; only `timed-loops-confirmed.webm`
is used as the deliberate recording receipt.

This demonstrates actual browser replay of the supplied sources and candidates,
**not human observation of121 loops or timed aesthetic/contact acceptance**.
The visual judgments here use the displayed poses and enlarged boundary
comparisons. The old49→16 sample wrap resets a raised/forward leg into a much
more extended stance, especially in first-last. The new53→18 held transition
and native57→18 transition are different comparisons; neither earns seamless
approval. Sword/shield pitch/exposure still change at the boundary. A more
regular-looking pose sequence alone does not prove planted feet or game-speed
readiness.

## Independent check of the explicit207-pixel edit

The parent made one manual diagnostic edit in first-last phase3/native33,
using seed `[110,120]`, tolerance0, on the conditioned256px cel. I did not
request an edit to the more ambiguous native38 pocket.

From the actual exported editable folder, I cold-imported into a new QA Store
and replay-validated selection receipt
`6a45e653866d02b8706c7fb1e559ef07ee0d0625cd2f6aacddc65bc94ee60efd`.
The resulting sequence is exactly
`9f9e1c53324ea567cb1bbd5be8c310691c0f87f45044279c1f37d81349e66d79`.
Independent checks confirm:

- Only phase3 changes: per-frame changed RGBA counts are
  `[0,0,0,207,0,0,0,0]`; every selected pixel changes
  `[0,0,0,255]→[0,0,0,0]`. Outside those207 pixels, RGBA is identical.
- The other seven frames are exact. Undo/redo restores the exact project IDs.
  Forged changed-action/index receipts reject. Explicit Studio normalization
  records zero hidden-RGB changes in this case.
- The cold closure retains the selection/mask/edit history,107 native raster
  payloads with extraction PTS, and original MP4
  `89d29f48cc97ea3c9e05757959a3ce50835157ec0da2dd9e6841c1dcc63aeb13`.
  It retains the107-frame extraction rather than the separate original
  sequence-wrapper artifact; this is not loss of those source pixels/times.

The before/after view makes the central arm gap cleaner, while residual dark
edge colors and irregular outline specks remain. Exact-black connectivity is
a reproducible **manual selection**, not proof that every selected pixel was
background. A semantic decision about the gap remains explicit, localized and
reversible. This single-frame edit does not repair other poses or the loop seam.

`REVIEW-EVIDENCE.json` in the QA directory pins the independent JSON receipts,
browser recording and screenshot. No provider, credential or paid call was
made; audited source Store/export files were read only.

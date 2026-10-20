# Independent host selector review

The two independent CLI runs reproduce both retained mask PNGs and selected counts exactly, with the input PNG unchanged. **The one material metadata finding is now resolved:** unselected pixels are transparent **white** `[255,255,255,0]`; the initial receipt/docs incorrectly said transparent black. The corrected wrapper changes only its convention string, and fresh receipts describe the same unchanged PNGs accurately. Historical receipts retain the original mistake with an explicit erratum. No algorithmic blocker was found within the demonstrated manual-selector scope.

[HOST-SELECTOR-REVIEW.json](HOST-SELECTOR-REVIEW.json) records executed/current CLI hashes, source pins, decoded mask colors, engine, input/output hashes, receipts and the negative guard. Private independent outputs are under `/home/astra/artifacts/pixellab-host-selector-independent-20261014`. Only the isolated methods worktree and that new private review directory were written. No API, credential or provider calls occurred.

## Actual replay evidence

The canonical root CLI was invoked with root's `.venv/bin/python`, corrected96×96`connectivity-rgba.png`, seed `(0,0)`, and two normalized tolerances. Each invocation wrote to a fresh private review directory.

| Tolerance | Selected pixels | Mask PNG SHA256 |
|---|---:|---|
|8/255|5761|`8d5c66ecbbdcee0c85ba0c0dd994894b43b893781be078bc8e516f340b824579`|
|32/255|5889|`d46178aa2e071504bd68d7bb26fa377dbeeb79868258979706830aca51c11fc3`|

Both PNGs are byte-identical to root's retained examples. Their only decoded colors are `[255,255,255,0]` and `[255,255,255,255]`. The root wrapper fills the mask with original Godot `Color.TRANSPARENT`, then its callback paints selected spans white. In these actual executions that transparent constant retains white hidden RGB. There is no basis to describe the resulting unselected PNG pixels as RGBA0. Changing their hidden RGB to force the earlier prose would change the retained artifact; a truthful convention correction is sufficient.

Each receipt reports the source Image data unchanged during original-method execution. Independently hashing the original input before and after both runs and the negative test confirms that its PNG bytes are unchanged. The fixture decodes as format5/RGBA8. Other formats may be converted to RGBA8 by the declared wrapper; these two tests do not establish lossless decoded-pixel parity for every PNG mode.

The precision behavior at8/255 is retained:5761pixels, not the5825that an integer byte-distance≤8 reinterpretation would produce. Tolerance is the recovered normalized componentwise RGBA comparison with the original approximate-equality shortcut. This review did not replace it with integer or perceptual distance logic.

## Source and scope fidelity

The full recovered `FloodFillObject.gd` SHA matches `63f7320fbb151e1959265a8e1331c341cefaf6511c1975e69df1ccf515c15cb7`; `DrawingAlgos.gd` matches `6acef5d413bdf0e7685b7d034bb65885d40b884d6cee60869065052980ec61a9`. Original UTF-8 bytes round-trip unchanged. The CLI writes the recovered FloodFill text as an unchanged prefix plus appended fixture declarations and extracts the complete unchanged `similar_colors` function. That function hash independently matches both run receipts. The wrapper does not implement a substitute flood algorithm or call a remote service.

The Project/SelectionMap declarations, mask allocation, PNG decoder/conversion, emitted-span callback and receipt are **host wrappers**. `has_selection=false`; active selection constraints, tilemaps, undo and full editor state are not exercised. Source alpha participates in matching; the output is a selection mask rather than a cleared/recolored source image. The source comparison is against the explicit seed color, not automatic background inference.

The stated boundary is accurate: **recovered-source replay, not compiled GDC equivalence**. It does not demonstrate private PixelLab automatic/Complex cutout, segmentation, animation cleanup or full editor integration. The reported one-pixel difference from a public Complex cutout is not tested anew here; no service-substitute claim follows from these masks.

## Guards and remaining limits

The existing five retained guard receipts were inspected. This reviewer independently repeated only the existing-output-directory case: exit2, and every file in the already-created tolerance8directory retained its hash. That verifies preservation at that guard without expanding the test campaign.

Inspected code guards restrict input bytes to4MiB, dimensions to1..512per side, seed to the canvas, tolerance to finite0..1and source files to exact pins. Verified input bytes are copied into a temporary isolated Godot project under the output directory; the original input file is never opened for writing. The subprocess timeout is60seconds, and temporary project/data cleanup is scoped to the new output directory. Timeout, source-pin mutation, every malformed PNG and every host branch were not independently induced. A failed run may retain its failure receipt/output directory; no atomic “all-or-nothing” promise is made.

## Correction closure

The read-only followup verified `MASK-CONVENTION-CORRECTION.json` and both fresh receipts under `/home/astra/artifacts/pixellab-recovery-round3-20261014/manual-selector-current`. New CLI SHA256 is `67cbb80674b9d17cb81aeb423dcadd16aa617a461720894552394a830af37252`. Replacing its one new convention literal with the old literal reproduces original CLI SHA256 `7d1eab72a809c1890fcf1f128398ae6693b43a65a0312b49c13951b3c25750b5` exactly: no other code, mask fill or recovered method changed.

Both fresh receipts pin the new CLI, correct unselected RGBA and unchanged original-method hashes. Their PNG bytes remain exactly equal to the old examples and the independent review outputs, with counts5761/5889. The original input hash is still unchanged. Old receipt SHA256 values match the correction sidecar, so history was preserved. Corrected docs explicitly direct callers to consume mask **alpha**, since RGB alone is white everywhere in these masks.

The metadata finding is closed for current receipts/docs. Initial root example receipts and this review's original private execution receipts remain historical records with inaccurate convention text; use them with the explicit correction, not as independently accurate descriptions of unselected hidden RGB. The proof JSON preserves initial observations and adds the independently checked closure. No additional execution/provider calls were needed for this followup.

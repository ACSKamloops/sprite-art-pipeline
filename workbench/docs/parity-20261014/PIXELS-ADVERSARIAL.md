# Independent source-pixel adversarial protocol

Scope: six recovered Godot methods from original `get_image.gd` SHA256 `8f7224392a2b3511d124e577a4a360c8e3344d9df60f0692f011dcd1e89aa651` and `draw_image.gd` SHA256 `0bce163896b067e794ef168df039ec85cae1e0981efad47d1cc090b097be6ff4`. Tests execute the bounded local wrapper in actual Godot; expected arrays below are independently authored from original bodies. Host image capture and undo sinks are explicitly supplied fixtures, not a full editor runtime or private server implementation. This document and `tests/test_parity_pixels_adversarial.py` are the reviewer's only owned repository files.

The original methods distinguish several superficially similar operations:

- `has_transparent_pixels`: true for **exactly zero** alpha, false for all-partial-alpha images. This is not an opacity predicate.
- `image_to_base64`: row-major RGBA buffer, with RGB cleared only at alpha zero. Source `Image` bytes should remain unchanged.
- `get_limit_color(reference)`: source scan is x outer/y inner, unique RGBA `Color` keys retain distinct partial alpha, zero-alpha colors excluded. Output is 64×64; each distinct color is emitted exactly once in x-major destination order, regardless of count. Remaining pixels stay zero. The first 4096 colors survive a larger source; no nearest-color or frequency ranking is involved.
- `get_mask`: a captured mask image's alpha>0 maps to opaque white; alpha=0 maps to opaque black. `fill_background` adds white where the separately captured ordinary image has exactly zero alpha. `inpaint_empty_image` fills white only if both mask and ordinary image are invisible. An all-black returned mask is still opaque, so using this RGB inpaint mask as a placement mask would copy everywhere.
- `get_image_from_data`: PNG magic triggers decode and actual PNG dimensions; raw bytes use declared dimensions. The decoder converts to RGBA8. Invalid PNG must not turn into an accepted partial image.
- `draw_image`: uses blit, not blend. Source alpha0 overwrites/erases destination pixels if the placement mask permits it. Placement mask alpha, not RGB/luminance, controls writes. Selection dimensions override source rectangle dimensions; selection origin sets destination offset; clipping preserves untouched destination pixels.

## Independent small oracles

Use a nonsquare source so row/x-major swaps fail visibly. A 2×3 image in row-major order containing `A, B / C, D / A, E` yields reference-conditioning order `A,C,B,D,E`; distinct alpha versions of the same RGB remain separate colors. A zero-alpha hidden-RGB marker is excluded rather than normalized into the palette. A 65×65 fixture with color index `x*65+y` produces 4225 distinct colors; expected conditioning stream is indices0..4095 in x-major placement, exactly once each. This distinguishes cap behavior from arbitrary downsampling, frequency ranking and row-major scan.

The serialization fixture uses zero,1,127,254,255 alpha, including RGB under alpha0. Check exact decoded bytes and input immutability. A no-zero-alpha fixture must report no transparent pixels even if every pixel is partial.

For masks, enumerate captured alpha `[0,1,127,255]`. Default expected white selectors are `[false,true,true,true]`, with alpha255 at every output pixel. Test `fill_background` using ordinary alpha `[0,1,255,0]`; test both empty-image controls independently. Supplying an opaque-black placement mask must copy; alpha0 white must block. Never reuse a boolean RGB oracle for placement.

For placement use a destination filled with a nonsymmetric RGBA marker, a source carrying opaque, partial and zero-alpha hidden-RGB pixels, and a mixed-alpha mask. Check full output RGBA including hidden bytes; verify all arguments unchanged. Add negative destination origin, lower/right overflow, selection smaller than source, and PNG dimensions unequal to the declarations. Compare complete arrays, not just hashes or changed-pixel counts.

## Failure boundaries

Wrapper admission should reject invalid raster dtype/shape, dimension/pixel/encoded-byte budgets, malformed encoded input/raw sizes, invalid or truncated PNG, unsupported controls and invalid mask dimensions before publishing an accepted output. Source/manifest corruption must fail rather than silently use a rewritten fallback. Missing Godot, timeout, nonzero exit, malformed output and output-size mismatch must surface explicit failures. These are local wrapper rules, not claimed original editor validation behavior. A rejected operation must preserve source arrays and avoid accepted partial output.

## Completed independent review

Implementation `75ed3a4` was cherry-picked as `e0fb92c` into this isolated worktree. Tests bind `parity_pixels.execute(Store, operation, **request)` and do not modify implementation, vendored methods, shared fixtures or production artifacts.

Completed command:

```bash
/home/astra/projects/pixellab-local-workbench/.venv/bin/python -m pytest -q tests/test_parity_pixels_adversarial.py tests/test_parity_pixels.py
```

Result: **65 passed in 5.98 seconds**, exit 0. This includes 52 independently authored adversarial cases and 13 implementation-owner cases. The first independent 47-case run also passed; it was superseded by the expanded combined run. These counts are mechanical coverage, not parity scores.

Of the 52 independent cases, 23 execute the actual bounded Godot runner with full-array expected outputs/input-preservation observations. They establish the exact distinctions listed above, including distinct partial-alpha conditioning keys, the 4096 cap, source-alpha-zero hidden-RGB copying, partial-alpha mask copying and clipping beyond both source and destination. The remaining 29 cover admission, corruption and injected resource/result failures. Their injected subprocess responses do not establish real OS exhaustion behavior. No critical discrepancy or implementation change was required.

Failure coverage includes raw byte-length mismatch; invalid declared geometry/types; malformed PNG; valid PNG with actual width 513 despite small declared width; APNG; encoded-byte budget; corrupt immutable Store bytes; mismatched capture/placement-mask dimensions; unknown fields/operation; invalid origin/extent/flag types; oversized raster; original source and manifest corruption; absent runtime; injected timeout/nonzero exit/missing or malformed result/wrong raster length/input-mutation claim. Every tested rejection leaves the Store blob set unchanged after inputs were prepared.

Additional limits remain explicit:

- PNG decoding and raster placement are separate API calls. PNG actual-dimension override is tested in decode; the combined original PNG→draw branch is not exposed by this wrapper. The placement wrapper always supplies an explicit selection, so its no-selection/default-rectangle branch is not covered here.
- Capture is flattened supplied RGBA, not actual layer selection/compositing. Original `get_limit_color(image|palette)` branches are deliberately outside this reference-only API. Null-Image transparency and configurable mask colors are not exposed.
- Caller base64 parsing is not an API surface: the runner generates valid base64 internally. Malformed-base64 behavior is not covered.
- Actual OS CPU/address-space/file-limit exhaustion, a genuine 30-second timeout, installed-binary corruption, malformed PNG fallthrough in the original unrestricted editor and multi-layer undo behavior were not induced. Source and manifest corruption tests use temporary copies only.
- Original file/method hashes are verified; host fixture/runner hashes are recorded per receipt. They remain explicit local harness code, not recovered private processing.

No provider/network calls, full-suite rerun, model-equivalence claim, whole-requirement closure or artistic approval accompanies these results.

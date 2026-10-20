# Shipped palette-image extraction

This change exposes one actual PixelLab browser method: importing a single palette image from its already-decoded canvas RGBA. It executes unchanged source, including the histogram, branch threshold, representative reducer, hexadecimal formatting, warnings and rejection. It adds no private palette constructor, arbitrary target count, dithering or pixel recoloring.

The reducer fragment was already replayed in earlier research. The new recovery/integration is the complete import handler and its exact dependencies as a usable bounded operation, with an independent full-original-factory oracle and a real browser decoding check. This closes a shipped client workflow gap; it does not close private `/reduce-colors` or automatic-K gaps.

## Source and operation

Retained asset: `/home/astra/artifacts/pixellab-recovery-web-20261014/assets/2713c302f049-create-9c5cec3372075418.js`, SHA256 `819962c897d4640c126a5efa4b6c5a194819e7eeaf023b242d852a64df74779d`. Webpack factory97981 SHA256 `e9c6cb49052afbda45b9f16559a109f802dba299eab6fd3b166da3154188e0ee`. The minified asset uses byte anchors instead of ambiguous line references. Ranges below are zero-based UTF-8, end-exclusive.

| Definition | Byte range | SHA256 |
| --- | --- | --- |
| sRGB transfer `tR` |125970–126043|`110f58094f1d594e008bb023037ee8c93c282999999257fe23a5876a6c47368e`|
| Oklab distance `tT` |126044–126095|`64c6a95c46eb5756d6ecffc1281cda48499cdd9061af0948fe905a320db84cff`|
| Hex formatting `tO` |131045–131116|`2da12219ee64cee8ed0c9c358af122cf065169b28363cb35aca3a5b391499421`|
| Entire asynchronous image handler `S` |132618–135186|`ba3c98b358af99881d9a64565de8cfddcd9ead4546b3ebf67ff38379ff32dfd1`|

The manifest includes exact original text and both JS-string/UTF-8 ranges. Tests verify every slice against actual retained asset bytes. Production pins the entire manifest and every slice; the independent oracle registers the full asset, pins the complete factory, then finds definitions by unique original literals rather than production offsets or manifest.

Original behavior retained:

- Ignore alpha0; count every alpha>0 pixel once, independent of alpha magnitude. RGB occurrence order is significant.
- Up to256 unique visible RGBs: retain all in first-seen order. There is no user-selected count.
- Above256: aggregate5-bit RGB bins; use weighted existing-color representatives, standard unweighted Oklab distance, fixed dark/light anchors, at most32 centers and20 refinement iterations. Choose existing RGBs and sort by lightness. The nested reducer's second argument is unused.
- Fewer than2 resulting colors: return the original rejection. Even >256 RGBs can reject if all collapse into one bin. The adapter does not repair this case.
- Preserve the exact original warning/error strings. A rejection does not instruct the caller to replace an existing palette.

## Host boundary and integration

`import_palette_image(rgba)` accepts uint8 `[height,width,4]` **canvas-equivalent RGBA**. It returns `accepted`, original `colors/warning/error`, a derived opaque `palette_rgba`, source pins and declared adapter metadata. Input bytes remain unchanged. `palette_rgba` is only hex decoding, not another quantizer. Node is required; there is no fallback algorithm. The local limit is262144 pixels and a bounded subprocess/VM timeout. These budgets are host policy, not recovered PixelLab limits. The interface does not support combined frames, automatic size selection, private mapper behavior, GIF palette construction or rendering.

The Image/canvas adapters supply existing decoded RGBA; React setter adapters record the original palette/warning/error effects. Source image/network decoding and unrelated browser UI state are outside this operation. For portable installation, integration must include `parity_palette_runner.cjs` and `parity_palette_source.json` in package data. This branch intentionally does not edit shared packaging, services, UI or catalog files.

**PNG decoder caveat verified, not hypothetical:** real Chromium canvas decoded diagnostic `[90,2,7,1]` as `[0,0,0,1]`; the original handler consequently included black whereas the raw-RGBA fixture did not. Both executions were exact for their supplied canvas bytes. Do not label Pillow/raw-PNG decoding as complete original-browser import parity. No approximate premultiplication formula was added. Opaque diagnostic images avoid this particular difference; arbitrary browser color-management equivalence is not certified.

## Verification

Focused command: `python -m pytest -q tests/test_parity_palette.py` → **16 passed in3.29s**, no skip in this run. The retained full asset and Node were available. Original-source tests explicitly skip if the retained asset is unavailable; portable CI must not count those as oracle passes.

Eight differential fixtures cover transparent rejection, one RGB with differing partial alpha, first-seen order, exactly256/257 colors, >256 colors in one5-bit bin,4096 colors, and reversed4096 colors. Additional tests pin source bytes, explicit outcomes/threshold, unchanged input, invalid/budget rejection and observed canvas-readback distinction. This is selected-case adapter fidelity, not exhaustive branch coverage or independent palette-quality proof. DOM decode failure/getContext failure are outside the admitted-RGBA boundary and not exercised.

`tests/parity_palette_browser.cjs` executes the original handler with **real Image/canvas** from the full asset, then compares the production runner on that browser's readback. Four local PNG diagnostics (transparent, partial alpha,256 opaque and4096 opaque) all match exact colors/warning/error; Chromium153.0.8010.12; **zero network requests**. Browser inputs/readbacks/full observations are retained externally at `/home/astra/artifacts/pixellab-parity-palette-20261014/`; compact hashes/results are in `RECEIPT.json`. These diagnostics are authored probes, not generated art. Browser evidence scripts require an existing local Playwright/Chromium path or explicit environment overrides; they install nothing.

## Remaining parity gaps

This is distinct from the shipped GIF quantizer and private smart-palette service. Prior `PALETTE-INFERENCE.md` reports only29/32 RGB agreement and768/8192 mapping misses for its closest authored high-K candidate. Prior multi-frame histogram adapters were experiments, not recovered multi-frame browser behavior. No such candidate is substituted here. Private automatic palette construction/high-K ordering, automatic K and dithering remain unresolved; source parity for this import route cannot certify those methods or private model internals.

A useful future **authorized** discriminating probe would freeze predictions for reversed/permuted equal histograms at32 colors, retaining complete input/output palettes and order. It can distinguish source helper order sensitivity from observed service behavior; it cannot uniquely identify private internals. This task made no API, credential or paid/provider call and recommends no unapproved call.

## Independent review correction

The independent reviewer reproduced a caller-mutation race in baseline `b56c733`: JavaScript could process the submitted buffer while later receipt metadata described a caller-mutated array. The adapter now snapshots validated input before serialization and derives both histogram and hash from that same snapshot. A deterministic regression mutates the caller array after Node returns and confirms colors, unique count and hash still bind the submitted pixels. Focused follow-up: **17 passed in3.38s**. The original source slices are unchanged; the correction is host provenance only. The original receipt's16-case/file hashes remain the baseline observation, not revised historical evidence.

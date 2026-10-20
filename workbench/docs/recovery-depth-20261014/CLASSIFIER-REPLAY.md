# Original classifier replay and shipped color metrics

The original current pixel-input classifier **runs locally unchanged**, including through its original worker entry point. The searched client sources did **not identify the quarter-lightness Oklab metric** from the separate server experiment. Two shipped Oklab paths were identified, with different roles/formulas.

This follow-up uses already downloaded public assets from [the recovery ledger](WEB-MODEL-RECOVERY-LEDGER.json). No HTTP, credentials, inference, paid calls, target project execution or modifications to the canonical checkout/research were needed. All fixtures are supplied diagnostics, not generated art.

## Classifier oracle

[Replay receipt](CLASSIFIER-REPLAY.json) pins the original classifier chunk SHA `077cbc8f10724502107814a7a206a1dc24211a1125b7e6e301aadd941b3f4a64` and factory **66428**, SHA `5adbd6fd7b2f0e84918f6ff786d9b9c44764c281519bb2301c536c3f5ee9c686`, UTF-8 bytes `[392,36320)`. The exported `.x` function consumes width, height and RGBA bytes. Its original worker **5259**, factory65259, is separately pinned in the receipt.

[The replay harness](classifier_replay.cjs) parses out the unchanged factory with Acorn, provides only webpack's export-getter helper for direct execution, and rejects unexpected imports. It separately executes the **complete unchanged worker bootstrap** with local `importScripts` resolving exactly its one original linked classifier chunk and `self.postMessage` capturing results. No classifier expression, threshold or decision branch is translated or replaced. Both VM contexts lack HTTP/provider/Node module access.

| Supplied diagnostic | Size | Original public result |
|---|---:|---|
| Opaque black flat blank | 64×64 | `null` |
| Transparent black flat blank | 64×64 | `null` |
| Four-color hard pixel grid | 64×64 | `null` |
| Opaque two-axis smooth gradient | 128×128 | `null` |
| Exact 4× nearest-neighbor expansion of a 32×32 four-color grid | 128×128 | `{"kind":"upscaled","scale":[4,4]}` |

Each input has a pinned raw RGBA SHA. Results agree between two fresh direct-factory contexts and the original worker. The harness asserts the observed output and unchanged input bytes. It ran successfully twice; this receipt is the second run. `null` is the original public return value, not a new quality judgment or proof of clean pixel art. These five fixtures do not establish detection accuracy or coverage of all return branches.

Reproduce using Node and the existing Acorn installation, with a fresh output directory:

```bash
node docs/recovery-depth-20261014/classifier_replay.cjs \
  /home/astra/artifacts/pixellab-recovery-web-20261014/assets \
  /absolute/new/classifier-replay-output
```

The harness rejects source SHA drift. Unchanged extracted factories, raw `.rgba` fixtures and the receipt are preserved under `/home/astra/artifacts/pixellab-recovery-web-20261014/classifier-replay-verified`. This is an original-code execution oracle, not an independent implementation of the classifier.

## Color-method identities and limits

[Color evidence](COLOR-METRIC-REVIEW.json) records exact function byte ranges, source hashes, URLs/retrieval times and the bounded source-set identity. Search covered **72 current downloaded JavaScript files, 378 recovered GDScripts and 40 locally extracted shipped shader/include files**. Literal Oklab names, standard matrix coefficients and cube-root references identify two source files:

* The current `create-9c5cec3372075418.js` palette-image import path converts representative colors to standard Oklab and clusters an image with more than256 distinct colors into at most32 representative colors. Its shared distance helper at UTF-8 `[126044,126095)` is `Math.hypot(dL, da, db)` with **unweighted lightness**. There is no `L*.5` in the identified converter. This is palette extraction from a supplied palette image; it is not evidence of the server's `/reduce-colors` implementation or H3 video conversion.
* Current PCK `src/Palette/Palette.gd:313–349` computes Oklab lightness and a toe remapping to **sort** palette entries. The `0.5` factor at line331 is part of that scalar toe formula, not a nearest-color metric.

The current PCK's GIF-export `addons/gdgifexporter/lookup_similar.gdshader:11–14` instead compares `distance(color.xyz, c.xyz)` directly in RGB, without an Oklab conversion in that shader. Existing GDRE v2.7.4 statically extracted20 `.gdshader` and20 `.gdshaderinc` files from the already downloaded PCK SHA `398455603cf39fc993c59fca3265ed180e246005da631e918018d0c44d497e4f`, with exit0; the shader extraction log and files remain in the artifact root. This did not run the target project or shader.

No identified shipped path supplies `.25*dL²+da²+db²` or an equivalent half-scaled Oklab-L distance. This is a bounded literal/matrix search plus manual review of the identified color paths. Algebraically transformed/obscured methods, unlinked/authenticated assets, other builds and server code remain outside that conclusion. The separate black-box server observation must retain its own evidence and must not be relabeled as recovered client/server source equivalence.

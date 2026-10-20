# Ordered 2×2 dithering: bounded offline characterization

**No exact reconstruction was found.** A bounded grid of 378 parameter combinations compared the retained strength 5/10 outputs across 32,768 RGBA pixels per candidate. The best candidate misses 538 pixels; the best zero-centered Bayer candidate misses 596. Alpha alone matches exactly, and the retained strength 0 outputs are PNG-byte-identical to nondithered outputs. This is behavioral inference from two retained cases, not recovery of server source or a substitute PixelLab implementation.

Only the isolated `/home/astra/projects/pixellab-workbench-state` worktree was written. No HTTP, provider, credential, browser or root/research writes occurred. The script reads request JSON only to bind retained input PNGs and selected public dithering fields. HAR and response files are hashed without reading headers or printing payloads.

## Evidence and coverage

The compared cases are:

- `/home/astra/artifacts/pixellab-reducer-recovery-20261014/fixed-2x2`: strength 5, fixed black/white palette, two 256×32 RGBA outputs.
- `/home/astra/artifacts/pixellab-reducer-recovery-20261014-phase2/bw-2x2-ten`: strength 10, the same palette and same input bytes, two 256×32 RGBA outputs.

Frame 0 contains 4096 RGB-cube colors followed by 4096 gray-ramp pixels. Frame 1 uses the same RGB data with alpha 0/64/128/255. These are two RGB fixtures repeated under different alpha, not four independent RGB scenes. Request-embedded PNG bytes exactly match the retained source PNGs. All source, palette, request, response, HAR and compared-output hashes are in [DITHER-CHARACTERIZATION.json](DITHER-CHARACTERIZATION.json).

| Case | output00 SHA256 | output01 SHA256 |
| --- | --- | --- |
| strength 5 | `1cd07d4160afa011e3eaeee563c30bb9e23a3b5a3fc9391c4e1de9e1e814b191` | `35f69af5d1f9f4b0767a37bfeda4257a6591b2cd0474b538b9d75b547b917501` |
| strength 10 | `15bca735822e5e3c5148949a2880741d317f2a01085d622eaec6aa5ca6f54a54` | `4695bc0ee2f799009bf4b0d9d643bfdb319e8cdb3c5dc7415f424945cb56c384` |

The independently checked controls `fixed-none` and `bw-2x2-zero` match both decoded pixels and PNG bytes. Their output00 SHA256 is `caf7b6518f0304f61c1f6521f8abcee9431514e71ebf510c3461128c5b389b85`; output01 is `8c086426a546d52bcaf3aca76a6f9b0232afc4dda519ae60a40c291b2f5dc512`. This supports a zero-strength bypass on these inputs; it does not establish the unknown implementation of that bypass.

## Candidate grid and results

The explicitly bounded formula was:

```
B = [[0,2],[3,1]], optionally transposed
noise(x,y) = ((B[y%2,x%2] + offset)/4 - 0.5) * strength * factor
RGB' = uint8(rounding(clip(RGB + noise, 0, 255)))
RGB'' = fixed-black-white palette mapper(RGB')
RGBA result = RGB'' + original alpha
```

Offsets tested: 0,0.5,1; factors: 1,2,3,3.2,4,5,8; rounding: truncation, nearest-even rounding, floor. Offset 0.5 gives zero-mean Bayer noise; other offsets deliberately check common biased conventions. After clipping to nonnegative values, truncation/floor duplicate behavior, so 378 is a count of parameter combinations, not 378 distinct functions.

Mappers tested: squared RGB nearest color; Pillow 12.3.0 fixed-palette `quantize(...,dither=NONE)`; and a local model of the shipped GIF module's packed565 first-hit mapping cache. The GIF model was independently cross-checked against **unchanged original module 5958 `applyPalette(...,"rgb565")`** on all 32,768 perturbed pixels for its best candidate: zero differences between the cache model and original factory. This validates that local cache model on these inputs, while its server mismatch remains538. The factory source hash is `cc7e87ddeb584f550ab863bc10792addab01469be1143ede0cded67a096284de`; its GIF/export scope is detailed in [PIXEL-CONVERSION-RECOVERY.md](PIXEL-CONVERSION-RECOVERY.md).

| Best mapper candidate | Parameters | Total RGBA mismatches | Strength5 per frame | Strength10 per frame |
| --- | --- | --- | --- | --- |
| RGB nearest / GIF565 cache | canonical B, offset 1, factor 3, truncation |538/32768 |82:66 cube +16 gray |187:123 cube +64 gray |
| Pillow fixed palette | canonical B, offset 1, factor 4, truncation |624/32768 |100:68 cube +32 gray |212:124 cube +88 gray |
| Best zero-centered candidate | RGB nearest, canonical B, offset 0.5, factor 3, nearest-even |596/32768 | See complete machine ledger | See complete machine ledger |

No-noise RGB/Pillow/GIF565 baselines all miss 1282 pixels across the two positive-strength cases. Adding Bayer noise improves the fit, but none of the tested candidates is an exact two-case replay. Every tested parameter combination and count is retained in JSON; detailed counterexamples are retained for the best 12 combinations and baselines. Choosing the minimum after inspecting retained outputs is fitting these cases, not independent validation.

Concrete counterexamples for the best candidate:

- Strength5 frame 0 `(x=111,y=0)`: predicts opaque black; actual opaque white. Frame 1 has the same RGB disagreement with alpha 64 preserved.
- Strength10 frame 0 `(x=95,y=0)`: predicts opaque black; actual opaque white. Frame 1 preserves alpha 64 at the same disagreement.

The observed first-white gray indices by `(y parity,x parity)` are strength 5 `[[134,127],[122,129]]` and strength 10 `[[140,125],[118,133]]`, using rows 16/17. These are parity-constrained first observed white x positions, not continuous threshold estimates. They demonstrate a repeating 2×2 phase and increased spread at higher strength. They do not identify the color-space transform, exact noise scaling, rounding/cache boundary or palette-distance function of the server.

## Alpha and limits

For both cases, output alpha exactly equals the corresponding source alpha; output RGB is identical between the opaque and varying-alpha inputs. Fully transparent pixels are still mapped to palette RGB: 238 alpha 0 pixels are white at strength 5 and 263 at strength 10. Thus this reduction path does **not** universally zero hidden RGB. This differs from the shipped Godot serialization normalization and should not be conflated with background removal.

The root's separate nondithered weighted-Oklab finding is outside this candidate grid. Positive dithering changes observed behavior toward gray thresholds near 128; neither that observation nor this partial RGB fit proves that the dither branch uses the nondithered matcher. No six-color positive-dither case, different dimensions/origins, random heldout colors, alternative Bayer matrix size, intermediate strength or current-server version change was tested here. No unbounded per-pixel fit or opaque learned surrogate was used.

Reproduce with:

```
/home/astra/projects/pixellab-local-workbench/.venv/bin/python docs/recovery-depth-20261014/characterize_ordered_dither.py
```

The script is an **offline characterization harness**, not a usable exact server replacement. Since exact replication failed, further independent probes would need to discriminate mixed-RGB mapping and phase/rounding behavior before any production implementation claim. No such additional calls were made by this reviewer.

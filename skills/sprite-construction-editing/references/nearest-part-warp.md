# Nearest triangulated sprite-part warp

`scripts/warp_part.py` is a standalone Python CLI requiring Pillow and NumPy. It warps **one explicitly owned source part** into a fresh layer. Canvas size comes from the request;96px is only the retained evidence case. No installed skill, frozen art source or third-party producer is imported or modified.

```bash
python scripts/warp_part.py request.json --out fresh-layer-directory
```

The output directory must not exist; its parent must exist. Inputs are validated and rasterized before output creation. An existing path, including an empty directory or symlink, is refused. Validation failures create no output. A filesystem failure during final file writing can leave a partial fresh directory; preserve/investigate it rather than silently retrying into it.

The strict JSON request has exactly these fields:

```json
{
  "schema": "nearest-part-warp/v1",
  "canvas": [96, 96],
  "donor": {"path": "donor.png", "sha256": "<64 lowercase hex characters>"},
  "owner_mask": {"path": "source-part-owner.png", "sha256": "<64 lowercase hex characters>"},
  "source_vertices": [[20, 20], [40, 20], [40, 50], [20, 50]],
  "target_vertices": [[20, 20], [41, 20], [43, 50], [22, 50]],
  "triangles": [[0, 1, 2], [0, 2, 3]],
  "alpha_mode": "copy-owned"
}
```

Use actual SHA256 values, obtainable with `sha256sum donor.png source-part-owner.png`. Paths resolve relative to the request file, or may be absolute. Donor must be an RGBA PNG and owner must be PNG modeL or1 with only0/255 values. Both dimensions must equal the declared positive integer canvas. The input PNG file hashes are bound to decoded byte snapshots and checked again before publishing output. ICC/profile metadata is not propagated and no color conversion is performed: raw straight RGBA samples are authoritative.

Vertices are finite numeric[x,y] pairs. Source/target counts must match. Triangles use0-based integer indices. Invalid indices, repeated/degenerate geometry, nonfinite coordinates/determinants/inverses, and source-to-target orientation flips are refused. The absolute signed determinant threshold is1e-8 in pixel-coordinate units. This checks each triangle's orientation; it is not a global mesh-injectivity/manifold validator. Nonadjacent target overlaps can be intentional and use the declared deterministic overlap policy. No hidden mirror option, fit, bbox normalization or pose recentering exists.

## Raster contract

- An integer coordinate(x,y) is the pixel center, matching the frozen MM method. There is **no added half-pixel offset**. Target triangle bounding loops are floor(min) through ceil(max), clipped to the canvas.
- Inverse barycentric coordinates evaluate `[x,y,1]`. A point is accepted when all three weights are at least−1e-8.
- Inverse source position is `weights @ source_triangle`. Sample indices are `floor(source_x+0.5)` and `floor(source_y+0.5)`, including negative coordinates. This is not Python's ties-to-even `round`.
- Rounded samples outside the source canvas, or outside the binary source owner, are skipped. The receipt logs each triangle's source-outside sample count. Counts are attempted samples, so overlapping triangles can count the same target position more than once.
- Triangle list order is significant: **last valid owned sample wins**. Skipped/invalid/unowned samples never erase earlier writes. The witness map and triangle map retain the last winning sample.
- The sampled RGBA byte tuple is copied exactly. No channel interpolation, source-over blending, premultiplication, smoothing, dilation or new paint is performed.

`alpha_mode` is mandatory. `copy-owned` reproduces MM's ownership behavior: an owned sample is copied even at alpha0, preserving any hidden RGB and marking spatial ownership. `nonzero-only` skips alpha0 samples and leaves their prior target write, if any, intact; all alpha1..255 samples still copy exactly, including partial alpha. Neither mode thresholds partial alpha or blends it. Output ownership means an accepted source sample, **not automatically visible opaque coverage**; in `copy-owned` it can include transparent pixels. Choose the mode deliberately before compositing.

## Fresh outputs

| File | Meaning |
|---|---|
| `layer.png` | Full-canvas RGBA part layer; unsampled pixels are[0,0,0,0]. |
| `owner-mask.png` | Binary0/255 accepted-sample ownership, including alpha0 when requested. |
| `source-xy.npy` | NumPy int64[height,width,2], channel orderx,y;[-1,-1] means no sample. |
| `triangle-index.npy` | NumPy int64[height,width], winning triangle ordinal or−1. |
| `request.json` | Normalized request copy. |
| `receipt.json` | Bound input/output hashes, rule/alpha mode, signed determinants, ownership and clipping/write counts. |

Read witness arrays with `numpy.load(path, allow_pickle=False)`. For every owned destination(x,y), `layer[y,x]` equals `donor[source_y,source_x]`. The target-clipping statistic is explicitly **bounding-box grid positions clipped**, not exact out-of-canvas triangle area/pixel coverage. Source-outside counts refer to rounded nearest samples attempted within the on-canvas target triangle. Raw donor RGBA and each output file are hashed in the receipt.

This is a layer tool. It does not remove the old part, reconstruct newly exposed body, paint concealed anatomy, protect head/arms/legs, choose part order or infer material ownership. The caller must own those decisions and verify the actual composite. Transparent layer pixels must not silently erase known body paint. Newly needed but absent source paint remains missing. A part warp can create duplicate samples, holes in coverage, thin joints or collisions even when it passes every arithmetic check.

Arbitrary nearest rotations/deformations can jitter, break pixel clusters, change projected part width and lose highlights. Some poses need replacement drawings or deliberately authored source/target shape keys. This is not a native full rig, an anatomy solver, a foot-lock/contact system or an art approval. Do not infer a quality score from a hash or sourceXY match.

## Retained evidence

Original staging evidence: `/home/astra/artifacts/pixellab-hybrid-walk-20261015/game-ready-v6/portable-nn-warp-AOAOAO/validation-final/VALIDATION.json`. The installed CLI is also checked by `scripts/validate_part_warp_examples.py` against the same separately retained art evidence:

- Actual frozen `half-torso-AGAGAG`3.5 torso controls/source/owner reproduce386 known visible composite RGBA samples and298 actual journal sourceXY/RGBA samples.
- Actual frozen6.5 visible far-arm controls/source/owner reproduce65 known visible composite RGBA samples and53 actual journal sourceXY/RGBA samples.
- Every output-owned RGBA in both layers also matches the actual donor at the emitted sourceXY. Comparisons exclude known later occlusion/protected paint; they do not claim full-body compositor equivalence or hidden coverage.
- A tiny independent4×3 fixture verifies full RGBA identity, integer translation with clipping, explicit alpha0/partial-alpha behavior, source-outside logging, and deterministic overlap where later triangles sample different source pixels.
- Stale hashes, invalid indices, degenerate and orientation-flipped triangles, NaN, canvas mismatch, an existing output with preserved sentinel, and a nonbinary owner are rejected. Invalid-input cases leave no fresh output directory.

The harness reads frozen files and their inventory and never imports/executes `build_pilots.py`. It does not rebuild art or import a compositor. `validation/` retains the first passing implementation checkpoint; `validation-final/` is the final exact-code evidence after byte-snapshot/hash-closure hardening and the extra source-clipping fixture. The initial harness needed a correction to read the frozen inventory's `files` wrapper; that failed before writing validation outputs and made no source changes. No other implementation failure was hidden.

Re-run the bounded evidence only into a **new** directory:

```bash
python scripts/validate_part_warp_examples.py --out another-validation \
  --evidence-root /absolute/path/to/game-ready-v6
```

`warp_part.py` has no artifact-specific paths. The validation harness needs the frozen research assets at that root; those assets are provenance evidence, not part of the generic tool's dependencies. Tool versions and tested code hash are in the final validation receipt. `FROZEN-SHA256.json` pins this staging folder. Installed entrypoints are `scripts/warp_part.py` and `scripts/validate_part_warp_examples.py`; the original staging folder remains preserved. AMAMAM's nine-pixel boot study remains unpromoted and is unrelated to this tool.

## Later visible-part construction study

The same20261015 evidence root contains `wholebody-tween-pilot-FZFZFZ`: a manually authored, source-painted full-body midpoint with rigid whole shoes and explicit paint-coordinate witnesses. Its static gate passed; the17-state cycle in `wholebody-tween-cycle-GDGDGD` received no confident preference over the original16-state walk. Correct source sampling and one plausible pose did not establish improved full motion.

`wholebody-midpoints-GK-00-07` and `wholebody-midpoints-GL-08-15` are partial two-interval follow-ups. Newly assigned pelvis/waist and uncertain source ownership are authored construction assumptions; hidden anatomy was not recovered. In GK, knee/cuff seams, a waist patch edge and a tiny source-outline fragment remain despite successful source-donor, journal and outside-region checks. Any extra provisional GK outputs are excluded from its primary manifest. No complete32-state cycle is approved.

The user subsequently selected the unchanged30-pose H3 walk as the usable baseline after actual playback. Preserve that acceptance separately from these construction experiments. Do not force missing limb geometry from ambiguous near/far labels, or promote a cutout rig because it reconstructs the original source exactly.

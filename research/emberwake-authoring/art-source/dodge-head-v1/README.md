# Lyra dodge recovery head layer v1

One final candidate lowers the existing settle head/neck by **south 3, east 3, north 4, west 4 native pixels**. The old head is cleared, then the shifted nonzero-alpha head texels copy exactly. Transparent shifted ownership preserves underlying body outside the old head mask. There is no new paint, scaling, head deformation, full-body/boot move or alpha blending.

The package is **unrated and makes no approval claim**. It provides four native 128x128 PNGs, exact source witnesses, neck inspections and equal-clock A/B dodge proofs. Only this artifact directory was written; source files and earlier artifact packages remain unchanged.

## Frozen sources and exact ownership

`inputs/` contains byte-identical copies of:

- `/home/astra/projects/emberwake-demo/art-source/characters-v2/bake-v5/lyra/atlas.png`
- `/home/astra/projects/emberwake-demo/art-source/characters-v2/bake-v5/lyra/animations.json`
- `/home/astra/projects/emberwake-demo/art-source/attack-settle-v1/lyra/head-protection.json`

`SOURCE-INPUTS.json` binds their absolute source paths and SHA256s. The atlas is 1024x2048, with 128x128 cells and eight columns. `frozen-plan.json` binds source settle cels 116/117/118/119, every output PNG and decoded RGBA hash, exact displacement, and the ownership JSON hash. Ownership comes directly from each view's **`rows_y_x0_x1`**, with half-open x bounds; the descriptive polygon is not rasterized again.

## Final compositor and rejected draft

Let M be the literal source head ownership and N its integer translation. Clear all M to the exact transparent zero texel from source coordinate `[0,0]`. Then, for every source-owned texel with alpha > 0, copy its exact RGBA to `(x,y+dy)`. Shifted alpha0 texels leave the cleared zero inside M and preserve the original body outside M. The affected bound is M union N. Outside that union, every RGBA byte is identical.

The first literal-mask draft copied alpha0 ownership over body paint and erased 3/6/10/25 non-head body pixels (south/east/north/west). It is retained as **rejected diagnostics** under `diagnostics/literal-mask-draft/`, with its original four PNGs and measurements. The final foreground rule preserves all 44 of those pixels. This is one nominated candidate, not multiple head designs or displacement variants.

Nonzero-alpha source samples remain exact copies, including partially transparent source-edge paint. This deliberately does **not** alpha-blend head and body into new colors. Eight/five/eleven/nine partial-alpha head-edge pixels cover formerly visible non-head paint in south/east/north/west. Their copied alpha can lower the local body's prior opacity; one additional enclosed pixel falls below alpha128 in east, north and west. There are **no additional fully transparent alpha0 holes**, and the existing alpha-component counts do not increase. The exact-copy fringe behavior is documented for review rather than hidden as a compositing assumption.

## Measured result and joins

| View | Source settle | dy | Recovery → old settle → neutral head top* | Recovery → final settle → neutral* | Actual changed RGBA pixels | Non-head visible pixels covered | Non-head pixels erased |
|---|---:|---:|---|---|---:|---:|---:|
| South | 116 | 3 | 24 → 17 → 16 | 24 → 20 → 16 | 1,632 | 117 | 0 |
| East | 117 | 3 | 24 → 17 → 17 | 24 → 20 → 17 | 1,551 | 96 | 0 |
| North | 118 | 4 | 24 → 16 → 18 | 24 → 20 → 18 | 1,639 | 154 | 0 |
| West | 119 | 4 | 25 → 17 → 17 | 25 → 21 → 17 | 1,621 | 109 | 0 |

*Head top uses alpha >=128 above y65, consistent with the review's measurements. Alpha>=1 and alpha255 measurements are also retained in `previews/CLOCK-AND-HEAD-TOPS.json`; faint source fringes can begin a pixel earlier.*

All 6,443 changed pixels have explicit same-settle source coordinates and before/after RGBA. Lowering the head covers existing collar/shoulder/back paint as expected; those pixels are separately identified from old-head clearing. The neck looks shorter and the back hair sits lower on the collar. The 4x neck sheets show the join without hiding that overlap. No detached hand near the settle jaw was observed in the four native/2x triptychs; every pixel from **y61 downward**, including both hands' lower regions, costume, legs and boots, is exact. There is no semantic hand mask or invented hidden neck/body underpaint.

Viewed still evidence: all four recovery/settle/neutral triptychs at native and 2x, head detail at 2x, and old/final neck joins at 4x. This worker does not claim uninterrupted human playback acceptance. A/B proof files have exact authored timing and decoded holds; final motion judgment remains independent.

## Files for the main baker

Use only `candidates/{south,east,north,west}.png` as the four new dodge-specific cels. Existing shared settle cells 116..119 continue to serve attack. `BAKER-PROVENANCE-TEMPLATE.json` supplies proposed checkout-relative copy paths `art-source/dodge-head-v1/lyra/{view}.png`, candidate file/decoded hashes, original settle hash, exact source ownership/hash/rows field, displacement and compositor method. Those proposed copy paths have **not** been written by this worker.

`RECEIPT.json` and `replay-verified/witnesses/{view}/` retain old-head-clear ownership, shifted owner extent, shifted nonzero foreground, their union, full-frame integer `source-xy.npy`, operation ownership and exhaustive `changed-pixels.json`. Ownership codes are 0=original body identity, 1=old owned head clear via source `[0,0]`, 2=shifted nonzero head copy. Source coordinates are native cell coordinates in the original same-view settle cel, never atlas coordinates or another direction.

## Replay and verification

Requires Python3, Pillow and NumPy; verification additionally uses SciPy and ffmpeg/ffprobe. No network/model/API is used.

```bash
cd /home/astra/artifacts/emberwake-dodge-head-v1
python3 replay_head.py --out /home/astra/artifacts/emberwake-dodge-head-v1/fresh-replay
python3 verify_package.py --out-name verification-rerun
```

Both output names must be new. `replay_head.py` also accepts `--atlas` and `--masks`; each settle RGBA hash and the exact ownership-file hash must match. Stale targets, changed ownership and existing output paths reject before writing. Verification covers the independently replayed row operation, every source-coordinate witness and changed-pixel journal, rigid nonzero head translation, outside-union equality, y>=61/body/boot preservation, zero hidden RGB, transparent-body preservation, source hashes and rejection behavior.

The dodge remains five nonlooping holds: **9/200, 21/200, 11/200, 11/400, 11/400 seconds**, total **13/50 = 0.26s**. Native source/candidate APNGs and `*-AB-dodge-2x-once.apng` use exactly those fractions and one play. Labeled `*-repeat.apng` files repeat solely for review. MP4 proofs contain 104 frames at 400fps, held 18/42/22/11/11 frames; decoded image equality verifies each hold. APNG is exact RGBA; opaque-background H264 MP4 undergoes RGB-to-YUV444 conversion.

Open `index.html` for the triptychs and A/B proofs. `verification/SUMMARY.json` reports the checks and topology. `ENVIRONMENT.json` records tools. `SHA256SUMS.json` freezes every file except itself. The rejected literal draft and one corrected verification-counter error remain documented in `diagnostics/`.

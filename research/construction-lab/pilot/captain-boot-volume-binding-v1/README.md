# Painted boot volume-binding experiment

This folder preserves the exact 128px lower-body source and the frozen canonical72-pose packet. It contains two different boot bindings, plus the rejected three-anchor affine control. Nothing changes the source illustration or earlier rig/pack.

The personally viewed `artifacts/comparison-8keys-2x.png` compares the actual old affine warp, constrained UV surface, and closed proxy at identical native registration. The old near boot visibly elongates into a slipper. The UV surface keeps more original paint but folds its near side into a jagged face. The closed proxy is the more useful volume comparator: it maintains toe/instep/ankle mass and a black sole through pitch, but its near boot face is simpler than the source. **No finished-art approval or gait score is claimed.** Root must assess it in the full character.

## Rebuild

Python, Pillow, NumPy and SciPy are required. Output directories must be fresh.

```sh
python pilot/captain-boot-volume-binding-v1/build.py --output /path/to/new-surface-output
python pilot/captain-boot-volume-binding-v1/proxy.py --output /path/to/new-proxy-output
python pilot/captain-boot-volume-binding-v1/check.py
python pilot/captain-boot-volume-binding-v1/verify_proxy.py
python pilot/captain-boot-volume-binding-v1/compare.py
```

Checkers and comparison target committed `artifacts/surface-v2` and `artifacts/proxy-v2`. Rendering never writes input sources. Each pack has72 fullcanvas256RGBA frames and144 separate far/near boot layers, original duration16/17ms totaling1200ms, native/2x sheets and a GIF with cumulative10ms quantization totaling1200ms. PNGs retain exact RGBA. No fitting/recentering occurs per pose.

## Source and registration

`source/leg-master-128.png` is a byte-identical copy of root's source lowerbody cell00. It is project-provided artwork, **not claimed CC0**. `source/poses.json` is byte-identical to `captain-3d-pose-guides-v1/artifacts/final-v3/poses.json`. Their hashes appear in each manifest and QA report.

Actual alpha inspection is important: the near boot's opaque source ends at row115, not row120/124. The previous affine anchors put heel/toe beyond the source, contributing to its bad warp. This experiment independently inspected the source and gives `binding.json` explicit sole/cuff/instep material points. All four source-surface sole corners are opaque original pixels. Coordinates do not inherit the previous anchor guesses as truth.

`binding.json` is an editable UV triangle surface: `[source_u,source_v] → [forward,transverse,height]`. Surface vertices are fixed once. They are rotated by the canonical foot's rigid world basis and translated by its rigid origin; the source cannot be independently fit to each frame. The renderer uses orthographic projection, triangle depth ordering and nearest source texture sampling.

`proxy.py` defines a separate **closed authored 3D boot proxy** with fixed cross-sections along forward−8..20, width14..18, heightup to25.235. It has a broad low toe, instep slope, ankle seat, side faces and a closed sole. Every vertex uses the same foot transform. Geometry/pitch comes from the selected atomic heel/toe pivots in the canonical packet. Projected widths remain28..30px and heights27..33px across this cycle.

The proxy uses one fixed per-foot UV camera calibration. Far paint retains a side/three-quarter instep; near paint is originally frontal. Unpainted rear/bottom/extrapolated UV texels are **declared nearest-source-edge extrusion**, using only actual boot-source colors. This preserves the source and palette but is authored texture extension, not recovered rear artwork. The saved `*-edge-extended-UV.png` makes this limitation inspectable. It is neither per-frame paint nor AI redraw. Missing depth motifs still need real source art if visible in a final game view.

## Evidence and limits

The source-surface and proxy checks rasterize actual boot images at a fixed worldcamera. Each foot's flat stance produces one byte-identical RGBA image over the captured episode. This is useful material stability evidence for this direct3D renderer, **not** a held Sprite2D/rootround/fractional-camera or fullactor contact certificate. Pixel silhouettes cannot be certified by vertex equations alone. Source sole material registration is exposed in the surface report; unknown proxy underside texture remains explicit.

Both renders use alpha0/255 and add no new opaque RGBA colors. The proxy's216 frame/layer PNGs were rendered again and match encoded bytes exactly. All mesh vertices remain at/above ground in these72 poses. The original guide's continuous contact/chain validation remains separate; no inherited art approval follows from it.

`artifacts/proxy-v2/manifest.json` exposes all local UV/3D vertices, triangles, world/projected perframe vertices, frame/layer hashes and source bindings. Root can replace only the boot layers in the painted-plane experiment, keeping the canonical bones, shin/upper layers and timing. The render convention subtracts `physical_root_pixels` for in-place PNGs; applying one common actor root restores world movement.

Prior trial-v1/frozen-v1 had nonopaque guessed sole UV corners and are preserved as ignored historical controls. They are not the current material binding. Trial-v2/surface-v2 correct those; the closed proxy is a separately declared shape, not a silent modification of the painted source.

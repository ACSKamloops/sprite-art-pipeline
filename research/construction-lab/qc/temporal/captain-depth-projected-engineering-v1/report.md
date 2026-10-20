# Independent depth-projected Captain engineering audit

Reviewed 2026-10-08. **Bounded engineering checks pass with an explicit UV color ambiguity; no art approval or runtime planting approval.** Inputs are read-only main trial-v3-volume and proxy-v2. All output is reviewer-owned.

Pose packet SHA256: `96604824e533cd8aacb947cd2bc87ff40ce25bb3ef9099bb13cdc465dd498600`. Boot manifest: `04dffac0cf5ab73a8ca7932d81c73889a6e801a97d5a75095a35311e46b37666`. Sprite audition: `a8c029b083239ea426ea7e13193a10b44a8abf5648cc70c57ff1f79e83f686e5`. The original producing renderer is pinned to git `bc8fee9` and blob SHA256 `87fdc9904a6fadb7c1048cb5e9883ed24b1a16b3dbc66b7b61da036fb0cd6efe`; the current renderer file contains later optional branches and its separate live hash is recorded. This audit reconstructs the frozen default equations, not those later branches. Frozen audition origin remains96,80; later moving-preview origin192,80 is outside scope.

## What actually passed

- All72 full sprite RGBA images reconstruct exactly using independently implemented plane projection/affine composition and **actual captured boot layers**. This proves source registration/ordering consistency, not independent exact boot rasterization.
- Both authored boot UV textures reconstruct exactly from source pixels plus declared nearest-edge extrusion. All144 proxy projections agree with recorded vertices.
- Independent area-coordinate triangle rasterization has **85 different RGBA pixels and zero different alpha pixels**, across144 boot layers. Every discrepancy lies within1.421e-14 of an integer UV texel boundary and the actual color is an adjacent texel. Preserve this as numerical ambiguity; there is no byte-exact independent boot-color claim.
- All288 knee/ankle pairs have mask overlap within an8px neighborhood; both masks approach their anchor within2px. This detects anchor-level disconnection, not persuasive joint anatomy or every visible contour.
- Actual opaque pixel-center witnesses approach projected z=0 proxy vertices within1.134px, below the declared1.5px raster-boundary allowance. Flat-phase world proxy vertices stay stable to floating-point precision. These are geometry/raster witnesses, **not complete plantar patches, heel/toe forces or actual held SpriteFrames/world consumption**.

## Falsification and an exposed limit

A real boot raster translated down10px changes820 RGBA pixels and552 alpha pixels; exact comparisons reject it. The same displaced bulk still covers the original support vertices: opaque-proximity alone reports0.540px and **fails to reject this deliberately bad plant**. Moving up10px is rejected by proximity at10.382px. This counterexample is retained in report.json. A mismatched pose hash raises the exercised binding guard. No source artifacts were mutated.

## Viewed scope and remaining gaps

Personally viewed actual fixed256-canvas composites and reconstructed colored joint masks at frames0,9,18,27,36,45,54,63, plus the deliberate shifted-boot difference. No detached ankle hole is apparent in those eight samples. The far knee becomes a narrow angular plate around36/45; hanging gear/shield conceals parts of near knee/shin. Overlap does not resolve these art/depth limitations. This task did not view a complete timed sequence or judge game-art quality.

Hidden cuff rectangles, flat armor planes and edge-extruded unseen boot surfaces are authored construction assumptions. Mathematical contact cannot establish material planting of held source frames between pose updates. That runtime proof remains open, as does visual approval. Future source/canonical stance changes require fresh bindings, not a restamp.

## Reproduce

From this worktree, with Python, Pillow, NumPy and SciPy available:

```sh
python qc/temporal/captain-depth-projected-engineering-v1/audit.py
python qc/temporal/captain-depth-projected-engineering-v1/build_evidence.py
```

The first command independently reconstructs all72 frames and144 boot rasters. The second records frozen source hashes, asserts scoped invariants and runs actual shift negatives. It also generates the two committed visual evidence sheets. Generated individual layer PNGs are ignored, and no producer Python modules are imported.

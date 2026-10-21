# Visible support-boot trajectory diagnostic

This diagnostic measures actual toe/sole contours and a leather-material edge,
not alpha centroids, rig targets or inferred ground contact. It compares the
richer source keys with both the original two-bridge and repaired trials.

```bash
/home/astra/projects/sprite-art-pipeline/.venv/bin/python \
  research/pixelengine-imagen/tools/diagnose-support-trajectory.py \
  --pilot /home/astra/artifacts/pixelengine-imagen-refinement-20261020/source-repair/a15-bridges/rich-pilot01 \
  --repair /home/astra/artifacts/pixelengine-imagen-refinement-20261020/source-repair/a15-bridges/rich-leg-repair02/run02 \
  --rich-source /home/astra/artifacts/pixelengine-imagen-refinement-20261020/imagegen/head-body-palette-union/project.json \
  --recipe research/pixelengine-imagen/tools/support-trajectory-midpoint-recipe.json \
  --output /absolute/fresh-support-trial
```

The plausible support-role trace is the broad right boot at key 1, central/front
boot at key 2, then left boot at key 3. Their visible sole spans on row 70 move
`41–51 → 35–45 → 29–39`. The other foot is partly hidden at key 2, so physical
limb side is not proved. The ankle-height proxy is the right edge of bright
leather `[128,71,42]` on row 65; the anatomical ankle is not visible. Materials
and outlines can redraw between source keys. Linear half-phase displacement
is a testable authoring hypothesis, not proof of constant velocity or contact.

At key 2 / phase 2.5 / key 3 (250 / 312.5 / 375 ms), observed pixels are:

| Feature | Key 2 | Existing 2.5 | Linear midpoint | Key 3 |
| --- | --- | --- | --- | --- |
| Toe outline x, y69 | 45 | 40 | 42 | 39 |
| Sole span x, y70 | 35–45 | 30–40 | 32–42 | 29–39 |
| Bright shaft edge x, y65 | 39 | 35 | 36.5 | 34 |

The existing slot is inside the endpoint range, so it does not spatially
overshoot key 3. It does cover 80–83% of the horizontal displacement at half
phase. Both sole edges are two pixels early; the leather edge is 1.5 pixels
early. Original two-bridge and repair02 have identical support-boot paint.

At key 3 / phase 3.5 / key 4 (375 / 437.5 / 500 ms):

| Feature | Key 3 | Existing 3.5 | Linear midpoint | Key 4 |
| --- | --- | --- | --- | --- |
| Toe outline x, y69 | 39 | 37 | 35.5 | 32 |
| Sole span x, y70 | 29–39 | 27–37 | 27.5–35.5 | 26–32 |
| Bright shaft edge x, y65 | 34 | 32 | 30.5 | 27 |

Here toe/shaft lag 1.5 pixels, but the heel is already within half a pixel of
its midpoint. The source boot turns/narrows; one rigid translation cannot put
all three features at their endpoint midpoints. The diagnostic therefore leaves
phase 3.5 unchanged rather than applying a misleading whole-boot correction.

The single trial moves only phase 2.5's rigid support boot two pixels right and
adjusts only its owned trouser connection. Its actual visible row-70 sole span
becomes `32–42`; its bright shaft edge is `(37,65)`, within half a pixel of the
material midpoint. The component toe-outline point `(42,69)` is occluded by the
unchanged passing boot, while both sole corners `(32,70)` and `(42,70)` remain
visible. Overlap is allowed and is not optimized away. The trial can look more
crowded than repair02; no art improvement or physical-foot claim follows from
the midpoint measurement.

All eight keys/onsets, the other bridge, upper paint, passing-leg cels and exact
one-second clock stay unchanged. Source-coordinate witnesses, visibility flags,
guarded journal, full frozen composite map, equal-clock exports and all pairs
are retained externally at `a15-bridges/support-trajectory-diagnostic01/trial01`
under the refinement artifact root. Root owns full-motion review; no score is
assigned.

[A later coordinated upper-pose hypothesis](COORDINATED-UPPER-PILOT.md) tests
one phase-2.5 head/collar/torso/arm response while preserving this measured lower
pose, every key and all exact timing. Raw seams and explicit repairs are kept.

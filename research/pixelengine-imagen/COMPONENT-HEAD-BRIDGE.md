# One component head midpoint at phase 2.5

This source-bound probe changes only the head component in the richer two-leg-
bridge candidate's `bridge-2-3` cel. The eight original keys, the other lower-
body bridge, every lower-body part/cel, the one-second period and all exact
holds remain unchanged. The original baseline and the rejected no-underpaint
control are retained beside the joined candidate.

```bash
/home/astra/projects/sprite-art-pipeline/.venv/bin/python \
  research/pixelengine-imagen/tools/probe-component-head-bridge.py \
  --candidate /home/astra/artifacts/pixelengine-imagen-refinement-20261020/source-repair/a15-bridges/rich-pilot01/candidate-two-bridges/editable-project.json \
  --head-source /home/astra/artifacts/pixelengine-imagen-refinement-20261020/imagegen/head-body-palette-union/project.json \
  --recipe research/pixelengine-imagen/tools/a15-rich-head-bridge-recipe.json \
  --output /absolute/fresh-head-probe
```

The exact `owner` layer in source key 2 supplies the complete head and its
binary mask. Its anchor is `(40,29)`; the tested midpoint is `(40,28)`, before
source key 3's `(41,27)`. An explicit `(0,-1)` translation preserves every
owned head pixel and source color. The original owner is erased from a fork
of the held-upper cel using exactly that mask; the translated owner has its
own editable layer and frozen sourceXY map. There is no whole-cel shift,
averaging, scaling or change to scarf, gloves, torso or lower-body paint.

The plain translation exposes a nine-pixel gap at y28 between chin and scarf,
so `raw-head-translation` is retained as rejected seam evidence. The joined
`head-neck-cap` candidate adds nine guarded source-colored samples at x37..45,
y28, using source key 2's original head-owner bottom row. This is explicit
authored neck/join paint, not recovered hidden anatomy. Its mask is entirely
inside the original owner, outside the moved owner and outside known body
paint. Neither the moved head nor this cap overlaps known torso/scarf pixels.

The still chronology gives the head a one-pixel rise at phase 2.5, followed by
another one-pixel rise and the original one-pixel rightward move at key 3. That
distributes the visible vertical step across the two intervals. The tradeoff
is a one-row extension of the chin/neck skin-and-outline boundary in the joined
midpoint. The shoulder and scarf remain held until key 3, so the component
change alone does not establish smoother whole-character motion. Root owns
the comparison review; no score or timed-playback preference is claimed.

The external run is
`/home/astra/artifacts/pixelengine-imagen-refinement-20261020/source-repair/a15-bridges/rich-head-bridge01`.
It includes source masks, translated mask/sourceXY, neck-cap source witnesses,
initial project and guarded journal, exact PNG/APNG/ASE exports, native/2×/4×
adjacent chronology and an 8× collar crop. All ten predecessor/current pairs
and the wrap are retained. Replay/undo/redo, unchanged-frame/outside-mask/lower-
cel checks and exact clocks are independent of visual acceptance.

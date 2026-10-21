# Repairing the existing two leg slots

The frozen round-three review found a small local chronology gain in the richer
two-bridge trial, but no overall art gain. Its concrete defect was crowded boot
ownership at phase 2.5, followed by rigid knee/cuff/boot silhouettes and held
pelvis/upper-body poses. This bounded repair changes those two existing slots
only. No frames, key onsets, timing, head, torso, scarf or glove paint change.

```bash
/home/astra/projects/sprite-art-pipeline/.venv/bin/python \
  research/pixelengine-imagen/tools/repair-two-leg-slots.py \
  --pilot /home/astra/artifacts/pixelengine-imagen-refinement-20261020/source-repair/a15-bridges/rich-pilot01 \
  --rich-source /home/astra/artifacts/pixelengine-imagen-refinement-20261020/imagegen/head-body-palette-union/project.json \
  --recipe research/pixelengine-imagen/tools/a15-rich-leg-repair02-recipe.json \
  --output /absolute/fresh-leg-repair
```

The baseline and richer K61-derived source are hash-bound. The first near boot
gets two pixels more lateral clearance, preserving its complete source-owned
distal piece. An actual source-colored pencil/eraser transaction then replaces
the short near-trouser cluster with four seven-pixel diagonal rows, connecting
the held hip to the advanced cuff. All 28 material samples bind to visible
richer source-key-3 trouser pixels. This is authored visible leg paint; no
concealed anatomy is reconstructed. New covered pixels, erased pixels and the
whole explicit mask are retained. The hanging glove remains above the edit.

The second slot rotates the owned near cuff/shin/boot around a declared cuff
proxy. The neighboring source poses' rightmost opaque forefoot edges on row 68
and visible ankle material proxies on row 65 give projected angles 45.00° and
30.96°. Half the change is -7.02°; the trial applies -7°. These are source-bound
screen probes, not recovered bone joints, physical contact or a world path.
Nearest rasterization produces 110 owned output pixels from 108 input pixels:
107 distinct donor texels, three repeated samples and one omitted donor texel.
Every output RGBA is an exact richer-source sample, but rotation does not
preserve every original texel or guarantee a good cluster.

The source map of every leg part and the final composite is frozen. The guarded
journal retains the translation, rotation import and literal cluster eraser/
pencil edit. Original keys, exact clocks and all pixels above y54 are checked
against the frozen baseline. Complete original keys are checked against the
richer source. Exported PNG/APNG/ASE files, native/2×/4× chronology, 8× lower-body
crops and every final adjacency/wrap are retained outside Git.

The external experiment is under
`/home/astra/artifacts/pixelengine-imagen-refinement-20261020/source-repair/a15-bridges/rich-leg-repair02`.
`run01` retains the earlier interior-foot-proxy -10° trial. `run02` uses the
rechecked outer-edge measurement and is the comparison candidate. Each run
preserves the unchanged baseline, the intermediate articulated-controls stage
and the manual-cluster stage separately. No frozen review history is rewritten.

In the inspected still chronology, the first repaired slot separates the boots
more clearly and the short trouser plane connects to the moved cuff. It also
advances the near leg more decisively and simplifies that trouser shading into
an authored diagonal cluster. The second boot changes its angle slightly, with
the nearest-sample texel tradeoff recorded above. The upper pose and pelvis
remain held, so **whole-pose coordination is not fixed under this mask**. The
trial is retained for root review, not promoted as an overall art improvement.
No score, continuous-playback preference or expansion to a full 16-frame bank
is claimed.

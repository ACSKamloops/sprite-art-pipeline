# One coordinated upper-pose hypothesis

This trial replaces only phase 2.5 of the existing ten-slot cycle. It starts
from the measured support-midpoint project, preserving all eight source keys,
their onsets, the other nine cels, the exact one-second clock and every lower-
body cel. The support sole correction and passing-foot overlap are unchanged.
The separate root-authored phase-3.5 roll probe is not imported or modified.

```bash
/home/astra/projects/sprite-art-pipeline/.venv/bin/python \
  research/pixelengine-imagen/tools/coordinated-upper-pilot.py \
  --source /home/astra/artifacts/pixelengine-imagen-refinement-20261020/imagegen/head-body-palette-union/project.json \
  --baseline /home/astra/artifacts/pixelengine-imagen-refinement-20261020/source-repair/a15-bridges/support-trajectory-diagnostic01/trial01/support-midpoint-trial/editable-project.json \
  --plan research/pixelengine-imagen/tools/coordinated-upper-plan.json \
  --output /absolute/fresh-coordinated-pose
```

The plan binds explicit native source-pixel proxies for head/collar attachment,
both sleeve/arm edges, elbow crease, glove/wrist plane, waist buckle and the
pelvis-to-leg seam. They are visible projected material/contour proxies, not
recovered bones: the wrist is covered and source material shapes change between
keys. `MEASURED-CONTROLS.json` records each endpoint coordinate, its actual RGBA
and the chosen target coordinate/actual RGBA. Half-pixel midpoints require
explicit native-grid choices; there is no per-pose fitting.

The upper source painting is explicitly owned:

| Part | Donor and operation |
| --- | --- |
| Head and collar/bib | Complete key-2 owners translate `(0,-1)` together |
| Torso and buckle | Visible key-2 torso translates one pixel up |
| Pelvis garment | Key-2 garment top moves up; hem at y53 remains attached to the unchanged legs |
| Near sleeve/upper arm | Key-3 visible owner translates `(-1,+1)` toward the shoulder/elbow proxies |
| Near forearm | Key-3 visible owner uses a one-pixel projected shear between elbow and glove attachments |
| Near closed hand/glove | All 25 source texels translate rigidly `(-2,+1)` |
| Far upper arm | Key-2 visible owner adjusts proximal x by at most one pixel while moving up |
| Far hand | All 22 source texels translate rigidly `(0,-1)` |

The 351-pixel head and 89-pixel collar retain every source texel and their
original relative join. This avoids the earlier nine-pixel chin/neck cap and
its longer-jaw tradeoff. The pelvis mapping repeats 11 visible garment samples
to connect the raised waist to the fixed hem; it is an authored projected
garment choice, not hidden anatomy or a recovered rigid pelvis.

Raw source-part assembly exposed one enclosed cloth gap at `(35,36)` and one
isolated far-shoulder rim pixel at `(48,36)`. Both raw checkpoints are retained.
The final journal adds one explicitly owned shoulder-cloth pixel from visible
source key 2 `(35,37)` and erases only the isolated rim. No concealed surface is
filled beyond that declared one-pixel garment seam. The existing lower-leg gap
at `(43,57)` remains unchanged. Complete upper assembly is one connected actor;
pixel connectivity alone does not establish anatomy or art acceptance.

All layers retain nearest sourceXY witnesses. The complete resulting cel has a
frozen source-frame/XY map, including the one source-colored seam pixel and the
unchanged lower body. Guarded import/erase/pencil transactions replay literally.
Exact PNG/APNG/ASE exports, all predecessor/current pairs and native/2×/4×
neighbor views are retained. The prior head-only rise plus neck-cap recipe is
rebased as a separate control on the identical legs and clock, so it does not
accidentally compare a different lower-pose repair.

External output is under
`a15-bridges/support-trajectory-diagnostic01/coordinated-upper-pilot03` within
the refinement artifact root. `pilot01` keeps the raw assembly; `pilot02` adds
the two literal seam operations; `pilot03` adds the fair head-only control
without changing the coordinated pixels. This is one pose hypothesis, not a
new bank or accepted animation.

The inspected chronology now advances shoulder, elbow, hand, head/collar and
waist in the existing slot instead of holding the whole upper pose. Head/face
clusters remain sharp source paint and the visible joints are attached. The
trial still combines a key-2 front-torso plane with a key-3 turned sleeve/arm,
and uses a stretched garment connection at the hem. Their directional volume
and motion consistency require root's cold/full-motion review. No score,
continuous-playback preference or overall improvement is claimed.

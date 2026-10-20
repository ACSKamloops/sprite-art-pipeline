# Guided lower-body key-art experiment

Unapproved eight-key walk comparison. An isolated leg-only AI repaint improved
rounded armour and segmented boot craft over the source-surface rig, but redrew
landmarks. This sheet tests whether that craft survives adjacent poses. It is
not a reusable rig, directional library, or accepted animation.

The immutable raw built-in imagegen result, exact prompt and frozen pose guide
are in `source/`. The raw sheet is uniformly resized to512x256, its alpha is
thresholded at128, and eight fixed128x128 cells are placed at68,117 in the
original256x256 frame. These cell bounds and placement were defined before
generation; no individual pose fitting or recentring is applied. The generator
is stochastic; only processing of this frozen raw input is reproducible.

```sh
python pilot/captain-guided-key-art-v1/build.py \
  --upper pilot/captain-full-volume-auditions-v1/artifacts/wider-facets-v1 \
  --output /new/comparison
python pilot/motion-review-harness/export_motion.py \
  --spec /new/comparison/audition-physical.json \
  --output /new/videos --loops 3
```

Python, NumPy, Pillow and the existing frozen upper-source comparison are
required. Export additionally uses FFmpeg. Existing output folders are refused.

Original foreground upper/equipment layers are composited above the generated
legs and their fully opaque RGBA is verified exact. Behind-leg cape pixels may
be newly occluded by the different lower silhouette; they are not promised
unchanged in the final composite. Input layer and output cel hashes are recorded.

Eight150ms holds preserve a1200ms cycle. Pose/root metadata are sampled from the
guide, but generated pixels may change actual foot and joint positions. In
particular, a continuous root translating a held cel can visibly slide the sole
within a hold. Source guide geometry and contact labels do not certify contact
in this new artwork. Motion and foot-pixel reviews remain separate from source
palette/craft and deterministic processing checks.

`artifacts/trial-v1` is an abandoned partial build: the initial check incorrectly
required rear cape pixels to remain visible beneath newly occluding legs. The
foreground-only check is the correct compositing invariant. The complete
comparison is `artifacts/trial-v2`. Neither is approved for game production.

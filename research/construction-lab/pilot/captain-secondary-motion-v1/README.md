# Source-owned cloth follow-through experiment

Unapproved secondary animation experiment, separate from gait/art acceptance.
`cloth.py` inverse-samples the unchanged source cape or tabard with NEAREST.
The attachment follows the current parent; the hem follows the same world
parent at a fixed earlier cycle phase. A smooth fixed source-row profile
interpolates that delay; crossing the cycle boundary includes the canonical
root stride. Cape attaches to the chest and tabard to the pelvis.

This is a 2D material warp, not a recovered cloth simulation. It cannot supply
missing views, credible leg volume, support or anatomical poses. Parent
rotation and source silhouette remain authored hypotheses. Test comparators
preserve the unchanged sequence and independently enable the lag option.

Run `python -m unittest discover -s pilot/captain-secondary-motion-v1`.
Three contracts check exact stationary source RGBA, translated cyclic parent
continuity, and unchanged material palette through all72 dynamic poses.
Those checks do not approve cloth appearance or walking quality.

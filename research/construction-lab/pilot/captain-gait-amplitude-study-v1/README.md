# Larger-step guide comparator, unapproved

Derived from `captain-3d-pose-guides-v2/build.py`; retains the authored
42/48-unit legs, orthographic camera, narrow tracks, shared transverse
pelvic transfer and58% stance. It tests stride70 instead of44, pelvis111,
heel contact-15 degrees, toe-off25 degrees and a global swing endpoint
clearance coefficient2.4. Those are artistic/anatomical hypotheses, not
measurements recovered from the drawing or a biomechanical optimum.

`artifacts/trial-v1` is a rejected intermediate: coefficient1.8 allowed
minimum sole Z=-0.0010414. `trial-v2` uses2.4 and now explicitly refuses
ground penetration below1e-9. Its1441phase preflight finds minimum reach
margin1.7778863, maximum length error floating epsilon and minimum sole
Z=-3.75e-16. That demonstrates reachable authored geometry only.

Preserve the preceding44-unit packet as the control. Use identical source
meshes and fresh projection rasters for comparison, never relabel the old
renders/checks as belonging to this packet. Wholebody art, cadence, weight
transfer and rendered material planting require independent review.

## Longer-stride control

`design-long-stride.json` changes only stride to110. With the same heel/toe,
height and bone settings, all1441phases remain reachable (margin0.6273092)
and nonpenetrating within floating epsilon. `trial-v3-longstride` is a new
packet; trial-v2's70-unit packet is retained. `--design` selects the exact
configuration before camera/pose constants are initialized. Re-render the
identical bound meshes; no frame-by-frame anatomy/texture recalibration.
Larger strides need a wider fixed camera stage or an explicitly following
camera; do not clip a2x preview then rate the clipped gait.

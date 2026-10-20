# Read-only anatomical stance-proxy and presentation diagnosis

**Two factual causes can weaken the visible lateral transfer: widening increases foot/body-proxy separation while preserving the physical root/hips, and DrawRoot removes all captured pelvis/rootX motion from the sprite.** These measurements support examining presentation before adding authored gait compensation. They do not diagnose an invalid dynamic walk or certify whole-body balance.

No gait edits, Blender renders, source writes, body-mass inference or other reviewers' ratings were used. `stance-proxy-diagnosis.png` is a standard standalone numerical plot, not a new character render. Data/recipes/proofs belong only to this new case.

## Sources and anatomical basis

Actual prewide scene: `full-captain-articulated-craft-v7/native384/full-captain-diagnostic.blend`, SHA`b320480050d6c87cb6c0ef1a8114c9dcb4606b29b6a2a9db69df099f57e57f09`. Actual current wide scene: frozen crease `full-captain-diagnostic.blend`, SHA`bfbdbef0b2b0281b854746b05be8018484376d250c0ac2429a6a492c5011bbcd`. Both source-file SHAs remain unchanged.

All521 quarter-interval samples use actual evaluated rigid boot vertices and physical root/hip/ankle bone heads, subtracting only the existing DrawRoot previewXY translation. Its rotation is identity. PositiveX is anatomical left in the authored body frame. Raw boot vertex/topology hashes and authored rest-bone heads match before/after widening. Physical root is exact; before/after hip-midpoint deviation≤0.126micrometers and ipsilateral hip deviation≤0.261micrometers from world-coordinate roundoff. Actual ankle offsets reproduce±125mm within0.481micrometers.

The root-head and midpoint of the two thigh-head hips coincide within0.360micrometers. They are effectively **the same authored pelvis position proxy**, not independent estimates of whole-body center of mass. Body/armor/shield/sword/cape masses and forces are unknown.

## Actual contacts versus projected footprint

Actual contact subset: immutable articulated sole ownership vertices whose evaluated physicalZ is within1mm of the declared floor. Each sample records count, centroid,XY bounds and convex hull. The **whole projected footprint** separately projects all evaluated boot vertices intoXY; it includes elevated geometry and must not be mistaken for active material contact. Heel/toe rolling contacts narrow/change compared with flat stance; that is exposed in the data and plot.

Support labels are the existing inferred episodes: left heel98/stance82 intervals; right heel33/stance78; cycle130. No force plates establish these labels. On520 unique samples, single-left207, single-right191 and double122; the extra closed endpoint is retained only for provenance/projection closure. Boundary-inclusive sample fractions differ slightly from exact interval durations. Exact inferred interval durations: single-left52/130, single-right48/130, double30/130.

| Single-support mean quantity | Prewide | Wide125 |
|---|---:|---:|
| Left active-contact center minus hip midpoint, lateral magnitude |204.44mm|329.44mm|
| Right active-contact center minus hip midpoint, lateral magnitude |175.15mm|300.15mm|
| Left ipsilateral hip minus active-contact centerX |+4.65mm|−120.35mm|
| Right ipsilateral hip minus active-contact centerX |−33.40mm|+91.60mm|
| Alternating stance-contact centerX separation |413.62mm|663.62mm|
| Root meanX difference between left/right single-support phases |34.025mm|34.025mm|

The mean foot-center separation grows250mm, while body-proxy movement is preserved. On520 unique samples rootX span49.756mm; including the closed traveling endpoint gives50.079mm. The phase-mean root displacement/contact-center-separation ratio drops8.23%→5.13%. This is a positional ratio, not a balance metric or required target value.

Using contactX interval bounds rather than center points, the hip-midpoint proxy's mean single-support lateral gap grows58.68→183.68mm on the left and45.16→170.16mm on the right. Whole projected bootX intervals give smaller mean gaps because they include noncontact geometry:34.06→159.06mm left and1.86→124.91mm right. The ipsilateral hip remains within the whole projected bootX interval in single support, while actual rolling-contact gaps/XY containment differ.

The hip-midpointXY proxy lies outside the single-support material-contact hull already **before** widening, and does so after widening. Double-support containment fractions45.08%→30.33% are merely recorded observations. Dynamic walking does not universally require pelvis/root or whole-bodyCOM projection inside a static support polygon; acceleration, momentum, forces and trueCOM are absent. Existing floor/footplant passes do not certify lateral weight transfer either.

## What the actual camera removes

The current DrawRoot cancels both captured horizontal components, not only forward travel. Its physical rootX spans−34.612..+15.468mm,50.079mm peak-to-peak. At source camera ortho2.7m and world camera-right `(0.908490,0.417906,approximately0)`, that removedX contributes **6.4706 pixels at native384** or4.3137 pixels at256. The simple50mm×384/2.7 estimate overstates horizontal screen displacement because camera yaw matters.

The currently rendered root hasX andY span **zero**; projected root screenX span0px. Rendered hip-midpoint screenX span0.0000687px is float noise. The existing59.468mm rootZ bob remains, projecting8.273px vertically. This proves source pelvis/root lateral translation is hidden in the reviewed in-place frames; upper-body tilt/articulation can still move relative to it, so it does not prove the entire character is horizontally rigid.

Undoing all root travel projects104.124px of root screenX range, mostly the1.7855m forward translation through this oblique camera. That is not lateral sway. Read-only projection variants separately measure:

* Restore raw sourceX only:6.4706px root screenX range, but root endpoint advances15.4675mmX,approximately1.9985px. RawX retention alone is **not C0-closed** as a looping cel.
* Remove the meanX stride before retainingX:6.2715px, a diagnostic detrendedX construction.
* Split along actual average travel direction and retain its transverse residual:48.623mm physical transverse span, **6.3072px** source-camera screenX range, positionally closed at the loop endpoint. This preserves the slight diagonal mean travel rather than calling its worldX component pure sway.

The source remainsC0-conditioned; none of these projection calculations certifyC1 velocity continuity or perceptual improvement. `presentation-projection.json` records actual camera matrix, physical/current/restored proxy projections, DrawRoot values, captured stride and forward/transverse axes at all521 times.

## One constrained next test

**Presentation-only split of existing captured root travel, with no added gait motion.** Let `r(t)` be the original physical horizontal root displacement from frame1, `f` the unit vector along its measured cycle stride, `r_parallel=(r·f)f`, and `r_transverse=r−r_parallel`. In an isolated trial replace the cel's full horizontal cancellation by cancellation of only `r_parallel`; retain the exact captured transverse residual inside the cel. It is0 at both endpoints, shows approximately6.31px here, and requires no arm swing, new pelvis curve, extra lean, legIK change or mass assumption.

The world consumer must then apply **only the parallel root trajectory**, not the original fullXY trajectory: `consumer_parallel + cel_transverse` reconstructs the original physical motion. Applying fullXY root motion as well would double-count transverse sway. Validate that reconstructed world foot/material positions and original source bone/action data remain unchanged; keep the current camera/scale/guard/paint and declared whole-frame anchors. Check loop position/velocity and frame margins explicitly. This could expose existing motion hidden by presentation, but cannot by itself repair the physical extra125mm foot/proxy separation introduced by widening. Do not treat it as a balance fix or art gain before viewing.

## Artifacts and reproduction

`measurements.json` contains compact per-phase bone/proxy/contact-hull/whole-footprint data for both frozen scenes; `summary.json` holds source hashes, static geometry/rest proofs, phase definitions and grouped metrics; `phase-detail.json` gives center-separation ratios. `measure.py` and `project_presentation.py` are read-only Blender4.5.9 scripts, CPU6 if invoked with `--threads 6`; neither saves a scene or renders. `plot.py` creates the numerical figure with Matplotlib. Source files, prior ablation/scene cases and original private audit artifacts remain untouched.

# Actual displayed Lyra boot displacement

The existing v9 GPU images show the boot moving relative to the fixed floor grid. During one held04 raster, both an opaque sole-shading feature and a nearby ankle-shading feature move(+6,+6) screen pixels, or8.4853 pixels along SE over53.125ms. Across the sampled04→06 endpoints, both move(+10,+10), or14.1421 pixels over112.5ms. This agrees with the frozen source study's14.0415-pixel residual within nearest-raster tolerance.

This is actual displayed-pixel evidence from previously captured Godot images. It remains a **conditional support hypothesis**: PNGs do not prove plantar contact, and the capture fixture assigns the root directly rather than exercising input or physics. No new engine, browser, art, speed or timing run was made. The completed source study and canonical checkout remain unchanged.

| Captured interval | Cel(s) | Both displayed features | Along SE | Root/source calculation |
|---|---|---:|---:|---:|
| tick72→78 |04 held |(+2,+2)|2.8284px|2.9625px root |
| tick72→89 |04 held |(+6,+6)|8.4853px|8.3938px root |
| tick89→90 |04→05 boundary |(-1,-1)|-1.4142px|-1.3730px root+source |
| tick72→108 |04→06 |(+10,+10)|14.1421px|14.0415px root+source |

The fixed grid witness is actual GPU pixel(399,199), RGB(48,68,56), at the intersection drawn nominally at(400,200). Its surrounding3×3 RGBA block is byte-identical in all nine retained images. Positions above are measured against that fixed grid, not against a moving crop or actor bounds. About20.44% of the sampled root travel is cancelled in the displayed endpoint positions; source geometry predicts21.00%, with the difference attributable to raster sampling. Neither value establishes the true contact schedule.

## Actual features and correspondence

The script first searches the literal right-boot GPU window x400..443/y164..201 for an exact observed pattern. It then checks the unique match against the renderer's source footprint and the retained per-pose source maps. This is a match to displayed color context, followed by source validation; it is not merely a projected coordinate recorded as a detection.

The sole feature is an opaque2×2 pattern from tick72, ending at GPU(413,181). Its lower-right texel is the original source-study heel at source06(49,109), RGBA(66,31,16,255). That RGB alone also occurs at source06(47,97), so the single color is insufficient. The four-color2×2 context is unique in each accepted GPU search window. It survives at ticks72,75,78,89,90,107,108. Its absence at80 and125 is recorded rather than assigned a predicted detection.

The ankle feature is an opaque3×3 pattern from tick72, centered at GPU(413,176). Its center is source06(49,102), close to the original painted ankle witness(51,101). The pattern is unique in accepted GPU windows and survives at72,75,78,89,90,107,108,125. It is a shaded boot feature, not a recovered anatomical joint. The original ankle and forefoot single-pixel colors repeat and are left unaccepted as unique material evidence. They also disappear or change sampled representation at some roots.

For each accepted2×2/3×3 context pixel, the script records its actual GPU RGBA, nearest sampled128-stage coordinate, and original source06 coordinate through the04/05 source maps. All100 accepted context-pixel samples equal their literal alpha255 source RGBA exactly. Thus the checks use opaque paint: no background, shadow or partial-alpha contour is used as a material witness. A final GPU alpha of255 alone would not establish source opacity. Accepted features are inside the boot and show no foreground occlusion in these samples.

## Registration and raster bounds

The retained fixture uses a640×280 SubViewport with no Camera2D. Left actor root=(160,220); only the **right moving actor** is measured. Its assigned root is(395,155)+(1,1)/sqrt2*158*t, with t=(tick+.5)/320. Each cel holds18 ticks,9/160s. The sampled roots agree with this formula within0.00005px, consistent with captured float coordinates.

Actual Hero Sprite2D registration is a128×128 cell, pivot(64,112), centered Sprite2D offset(0,-48), scale(.66,.66), nearest filtering. A native texel center n+.5 projects to root+.66*(n+.5-pivot). The unique observed pattern must contain the asserted center source texel at that root and map. Its GPU pixel center lies within the source texel's.66×.66 footprint, half-width.33px, allowing only0.0001px numeric tolerance. No fitted shift is added. Two accepted endpoints can differ from projected displacement by at most.66px per axis, or.9334px along SE. The measured04→06 discrepancy is only.1007px along SE.

At tick80, the reference sole and ankle contexts are not identifiable after nearest downsampling. This is a sampling limit, not evidence that the boot vanished or changed contact. The scope is nine bounded existing samples, not every raster tick or the full loop. The second loop and fixture transport resets are not examined.

The fixture renders actual production Hero/Sprite2D art but directly assigns root positions and animation times. It does not test collision response, input sampling, the production follow camera, window scaling, boot collision, or a declared support event schedule. No score or game-ready contact approval follows from this result. It closes the distinction between source-coordinate prediction and actual displayed sliding for these samples.

## Review and reproduction

Open `results-final/held04-72-78-89-6x.png` for intra-cel drift and `results-final/contact04-05-06-6x.png` for the conditional contact run. Magenta marks the sole feature; amber encloses the ankle context; cyan marks the fixed grid. Crops retain fixed screen coordinates. `nearest-sampling-72-80-89-6x.png` shows the missing-feature case, and `right-actor-context72-4x.png` provides whole-actor context. All are crops/nearest enlargements of existing GPU PNGs with diagnostic overlays, not newly generated art.

`INPUTS.json` contains the nine actual PNG SHA256 hashes and retained fixture/receipt/source hashes. `FEATURE-OBSERVATIONS.json` records accepted and rejected matches, source opacity, local candidates and raster errors. `MEASURED-PIXELS.csv` and `DISPLACEMENTS.csv` contain the actual measurements. `OPAQUE-CONTEXT-WITNESSES.json` contains all100 literal GPU→source samples. The first `results-v1` conservatively rejected the repeated heel color; it is retained as an earlier diagnostic. `results-final` adds the observed opaque2×2 context that resolves that color ambiguity.

From any directory, with Python3,NumPy and Pillow:

    python3 -B /home/astra/artifacts/emberwake-diagonal-contact-render-v1/scripts/analyze_render.py --output /absolute/fresh/output

This command reads only portable local inputs, validates their hashes, repeats the pixel searches and source checks, and reconstructs the annotated proof and CSV/JSON. It never starts Godot or a browser.

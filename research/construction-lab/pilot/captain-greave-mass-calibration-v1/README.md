# One-time source-profile mass calibration

Unapproved one-view comparator. The earlier fixed-volume packs remain unchanged. This variant changes only the fixed shin ring radius/depth profile; original segmented boot proxies, kneecap size, femur backing, bones, upper body, pose packet and timing stay unchanged. It therefore does not solve the separate boot apparent-mass or upper-body performance criticism.

The observed source shaft masks are copied, with explicit source anchors. `calibrate.py` measures opaque transverse spans in source-bone coordinates, using the observed below-cap region y181..205 far /181..209 near. Three nearest source cross-sections determine each fixed ring radius through the neutral projection map. Depth/radius .55 is an authored volume assumption: one silhouette cannot recover depth. Missing proximal shaft coverage uses the first measured section, not new anatomy inferred from the image.

A first neutral render overfilled the actual source silhouette. `source/neutral-before-fit.json` records that failure; `source/neutral-fit.json` records the one-time measured source/shell median ratio used for radial correction. This is permitted neutral shape calibration, not fitting individual motion frames. The resulting profile is frozen in calibration.json and shared by every pose. There are no per-frame radius or UV adjustments. UV is source-projected once from the canonical neutral bind, with declared nearest-source edge extrusion for unseen surfaces. Widening a volume cannot establish unseen painted motifs.

Run from any directory with Python, NumPy, SciPy and Pillow:

```sh
python pilot/captain-greave-mass-calibration-v1/calibrate.py
python pilot/captain-greave-mass-calibration-v1/build.py --source-mode original --poses pilot/captain-greave-mass-calibration-v1/source/poses-long-110.json --output /new/pack
python pilot/captain-greave-mass-calibration-v1/check.py
```

The final check script targets the committed `artifacts/calibrated-long110` pack. It checks actual alpha connection, original lower-part palette, binary alpha and canvas bounds, and saves actual neutral shell/source-target images. Drop-in layers retain `integration-layers/NNN-{far,near}_{shin,boot,thigh}.png`; combined shin owns its cap, so do not duplicate prior knee imagery. Use the new thigh underlap too.

This uses the root's frozen 110-stride packet, SHA recorded in manifest; .58 stance, fixed42/48 bones, source-origin256 canvas. Bigger stride passed geometric constraints only. No art score, acceptance, body physics or arbitrary-direction support is claimed. Source project art is not claimed CC0. Actual all-eight-key inspection is a visual diagnostic; root/reviewer owns timed whole-loop judgement.

## Observed result

I viewed all eight rendered fullbody keys at2x. Shaft mass is more legible than the narrow baseline, and the far cap/shaft proportion is less extreme. The flame face still sometimes reads as projected paint rather than convincingly rounded armor. This is not a successful final-art claim.

Actual neutral source-target/shell median transverse widths are far24.341/24.492px and near22.376/22.376px. Maximum widths remain lower in the shell than the source (far31.411/28.446, near29.619/26.314), so matching median does not recover the exact source contour. The closed proximal region has greater opaque coverage than the partly occluded source partition (far858→1280px, near701→1102px); it is explicitly authored closure, not exact extracted silhouette. Those limits matter when evaluating the shell appearance.

All72 frames retain alpha connection (nearest thigh/shin gap0), binary alpha, source lower-layer RGBA palette and zero opaque edge clipping. No metric establishes anatomical or aesthetic acceptance.

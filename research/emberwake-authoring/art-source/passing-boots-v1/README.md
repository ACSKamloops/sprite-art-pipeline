# One bounded source-toe/heel passing-boot candidate

This folder is the entire isolated experiment. No checkout, source atlas or game asset was changed. The only proposed cel changes are f112/f113 south and f114/f115 north in each frozen Lyra/Brann v5 bank. No model/provider call, whole-pose fitting, full-boot stretch, palette conversion, body warp or new gait clock was used. There is no worker art score or approval.

## Selected output and review

The eight `candidate/{lyra,brann}/passing-{112,113,114,115}.png` files are complete 128×128 cels on their original stage. `mask-FRAME.png` contains the precise owned boot/seam region; every pixel outside it remains exact. `candidate/JOURNAL.json` names each foot/material owner and records every changed pixel's original RGBA, new RGBA, donor frame and donor coordinates. These are source RGB **and alpha** witnesses, not just palette matches.

Look at each character's `all-four-passing-fullbody-before-after-2x.png`, `all-four-passing-boots-before-after-6x.png`, and both `*-all-joins-native.png` strips. The strips contain all eight source/current pairs and loop ordering, including every 121→112 / 123→113 / 125→114 / 127→115 join. All four normal A/B APNGs encode eight exact **9/160-second** holds, hence the original **9/20 = 0.45-second** cycle. Their `fcTL` fractions are explicitly written as 9/160, avoiding a 56-ms-rounding drift. Slow 3× APNGs use 27/160 per cel and are labelled separately. Before/after retain identical frame order, body registration and clocks.

The images/whole-body strips were viewed here. The timed APNGs are review artifacts; continuous human playback acceptance and actual Godot foot planting are not claimed. Root will combine this candidate with the other head/trim changes and obtain an independent review.

## Concrete changes

The lifted foot keeps its current foreshortened silhouette, cuff and pose. Only opaque distal leather receives matching opaque source detail, clipped to its existing visible contour. A failed first rectangular far-foot paste made a cuff/edge spur; it remains clearly labelled in `brann-first-paired-sample.png` / `first_sample.py` and is **not** the selected operation. The corrected paired sample, `brann-first-paired-sample-refined.png`, matches final Brann f112 exactly. There were no additional design sweeps.

The foreground support shoe reuses a short toe/heel band and immediate ankle seam from the same-view predecessor source. Its final original sole row is preserved. Where explicitly owned, source contour pixels restore limited forefoot width, texture and a darker flatter sole. North uses back-view heel paint rather than a front-facing round toe highlight. No shoe is extended down through the stage to imitate a longer boot. The native whole-actor last nonzero-alpha row remains: Lyra all four110; Brann south111, north109.

All placements are view/role-specific:

| Character | Target | Donor | Lifted distal material offset | Support toe/heel offset |
|---|---:|---:|---|---|
| Lyra |112|121|[3,2]|[1,0]|
| Lyra |113|123|[1,4]|[2,-1]|
| Lyra |114|125|[3,4]|[2,-2]|
| Lyra |115|127|[0,3]|[-1,-2]|
| Brann |112|121|[4,3]|[0,-1]|
| Brann |113|123|[0,2]|[0,0]|
| Brann |114|125|[3,8]|[3,-3]|
| Brann |115|127|[3,2]|[1,-2]|

These offsets locate **copied material samples**, not a translation of the limb or the entire boot. In particular Brann north's +8 lifted donor offset only chooses existing dark raised-heel leather for a few already opaque target pixels. The current cuff, foot trajectory and outer alpha remain the pose authority, except the declared foreground toe/overlap contour changes. All y<96 pixels—including body, cloth and upper cuff—remain byte-identical; no torso/head/trim was repainted here.

`PLAN.json` freezes literal coordinate lists, named material owners, exact target/donor RGBA hashes and source identity. `author_variant.py` records how the one chosen plan was authored from the immutable inputs. It is not a generic ownership/anatomy finder. Transparent source samples may replace a few owned contour pixels (2–4 per cel); no newly enclosed zero-alpha hole results. That topology diagnostic is not evidence of recovered anatomy or a correct leg gap. The changed-pixel counts range116–177 per cel and are listed in `VERIFICATION.json`.

## Portable replay / integration

Requires Python and Pillow. Every source atlas, manifest and upstream receipt is copied into `inputs/`, with exact hashes in `INPUTS.json`.

```bash
python3 /ABSOLUTE/PATH/emberwake-passing-boots-v1/replay.py --output /ABSOLUTE/FRESH/OUTPUT
python3 /ABSOLUTE/PATH/emberwake-passing-boots-v1/verify.py
```

The small callable `replay.apply_variant(atlases, plan)` takes `{character: RGBA atlas}` and returns `{character: {original_frame_id: revised128pxImage}}` plus a journal. It never mutates input images. The CLI requires a new output folder; the caller can append these images to a new bank and update its manifest explicitly. Do not overwrite the frozen v5 bank.

Full target/donor hashes intentionally reject rebasing onto changed cels. For combination with independent head/trim repairs, apply the boot candidate before those repairs or compose the journal's changed pixels only after checking every `before` RGBA against the new base. Preserve unrelated pixels and obtain a combined review. Do not silently replace a newly repaired head with a full older passing PNG or update guards just to force acceptance.

`VERIFICATION.json` records exact outside-mask preservation, y<96 preservation, unchanged raster sole row, literal RGBA donor matches, unchanged input images, a fresh-process byte-identical replay of all eight PNGs, target/donor mutation rejection and encoded APNG clocks. These are mechanical preservation/timing checks, not quality or world-space contact proof. `FILES.sha256` freezes this self-contained package excluding generated Python cache.

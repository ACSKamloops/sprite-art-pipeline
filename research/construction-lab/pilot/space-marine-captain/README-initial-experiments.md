# Space Marine Captain: actual target art

This replaces the generic Ranger as our intended art target. The approved 256px Captain sprite is preserved byte-for-byte in `references/approved-256.png`; 512px is its 2× display. The subject has red armour, bare blond head, cream cape, power sword and ornate black/gold shield.

These are still images. We must author missing views and animation keys, preserve armour/face/heraldry through motion, and retain editable parts/cels for exact corrections. The first art gate is a heavy armoured walk in the approved three-quarter style. A fused generated pose sheet remains a proposal until repaired and reviewed.

`brief.json` freezes identity, original references/hashes, native size, humanoid-only scope and planned actions. No gun is present in this reference; ranged actions require a separate equipped variant. No animation is approved yet.

## Actual technique tests

Open the [local comparison player](http://127.0.0.1:8144/pilot/space-marine-captain/) while the repository server is running. It verifies source/frame hashes and offers pause, restart, previous/next, native/nearest 2×, slower playback, joint targets and source masks. No website publication is involved.

| Test | Actual result | Visual decision |
| --- | --- | --- |
| Generated eight-pose walk | Strong Captain identity; poor leg alternation, scale/row drift, clipping and detail changes | Rejected |
| Visible source parts + two-bone solving | Five exclusive source layers reassemble visible RGBA exactly; twelve reproducible frames | Rejected walk: thighs incomplete, boots rotate with shins, body too fixed |
| Independent boot transforms | Seven source layers; twelve reproducible frames; visible improvement in frames 6–9 | Partial repair only: hips/thighs, seams, body weight and contact still unresolved |
| [Pixel rotation comparison](../captain-rotation-technique/README.md) | Native nearest vs Scale2x ×3 rotation approximation; exact zero-angle identity, repeatability and no new RGBA colours | Better clusters at some diagonals; does not repair anatomy or gait |
| Newly authored complete-leg proposal | Hidden armour surfaces supplied as new concept art; provisional alpha cleanup and individual leg cutouts | Needs perspective/proportion draw-over and contour review; not animation-ready |
| [Actual Godot playback](../captain-godot/README.md) | Frozen first probe, 357 engine checks and 24 exact GPU/background composites | Mechanics only; does not approve the artwork |

Both walk probes have twelve 100-ms holds on the original 256×256 canvas. Their previews are `layer-probe/walk-preview.gif` and `boot-constraint-probe/walk-preview.gif`; PNG frames retain authoritative alpha. No per-pose fit/recentering is used. Thigh masks expose only 163 and 86 substantial pixels; cutting out those fragments cannot recover full limbs. Explicit dark joint backings are new construction pixels.

The independent reviewer viewed all atlas poses and selected enlarged frames. Its [source-bound rejection](adversarial-review.json) remains current. Root separately captured 34 chronological native browser images, covering all twelve frames over approximately 2.4 cycles at quarter speed, and viewed the contact sheet. This is sampled playback inspection, not a claim of continuous video understanding or measured sole contact. Capture receipts: `browser-motion-capture.json`; images: `/home/astra/artifacts/captain-technique-motion/`.

## Repeat

Python3 + Pillow:

```sh
python pilot/space-marine-captain/build_layer_probe.py --output /absolute/fresh-walk-test
python pilot/space-marine-captain/build_layer_probe.py --separate-boots --output /absolute/fresh-boot-test
```

Explicit output paths must be new. [Fresh-folder reproduction](reproduction-checks.json) rendered both variants and compared all 24 frame files byte-for-byte, checked exact source partition reconstruction, and verified existing-output rejection without changing the prior manifest. The portable Godot lab freezes the first probe independently; changing or rebuilding root candidates does not update that lab silently.

The generated masters and exact prompts stay in `generated/`; provenance records dimensions, source hashes, alpha diagnostics and tool identity. The hidden-leg raw preview shows exterior warm RGB glow; proper light/dark composites (`generated/hidden-leg-background-check.png`) show that it is mostly very low alpha, with little visible halo. Root inspection qualifies the reviewer's stronger warning: exterior RGB presentation exaggerates the artifact. The raw has 31,590 pixels at alpha 1–8 and a maximum alpha of 254; the approved native sprite uses only alpha 0/255.

`prepare_leg_matte.py` binds the raw master hash, retains RGB exactly where alpha ≥128, makes those pixels opaque, and zeros lower-alpha pixels and their invisible RGB. It also exports each complete-leg concept as a separate cutout. [The receipt](generated/matte-receipt.json) proves the raw master stayed unchanged and retained RGB was exact. These are provisional contour masks, not reconstructed rig-ready limbs or accepted anatomy. Neither cutout has been silently transplanted into the walk. Repeat with `python pilot/space-marine-captain/prepare_leg_matte.py`; inspect contour changes before choosing a production threshold.

## Next construction gate

Build complete thighs/hips, ankle collars and independent heel/toe surfaces at the Captain's actual perspective and scale. Give each kneecap a single owner and drawn cuff overlap. Split torso, sword arm, shield and cloth into reconstructed parts with deliberate pivots, depth order and restrained weight/lag. Author contact, compression, passing and opposite-contact keys, then use those to direct the rig. Correct difficult silhouettes with replacement cels and exact pixel edits rather than stretching armour or regenerating every frame.

This hybrid is an experiment to test, not an already accepted solution. Godot's primary [cutout documentation](https://docs.godotengine.org/en/stable/tutorials/animation/cutout_animation.html) describes combining articulated parts with replacement cels for feet/hands/complex changes; [2D skeleton documentation](https://docs.godotengine.org/en/stable/tutorials/animation/2d_skeletons.html) covers polygon skinning. These are construction mechanisms. Hard armour will first use rigid parts; softer cloth may warrant separate deformation tests. Aseprite's [rotation documentation](https://www.aseprite.org/docs/rotate/) distinguishes fast and RotSprite transforms. Current docs were inspected 2026-10-07; these are primary technique references, not newly published research or empirical proof of our art quality.

One accepted walk is the gate before further actions/views. Intended humanoid coverage remains idle, walk, run, turn, sword attacks, block, hit, fall/death and recovery. A consistent turnaround and new equipment states still require artwork. No monster work, full animation pack or new skill acceptance is claimed here.

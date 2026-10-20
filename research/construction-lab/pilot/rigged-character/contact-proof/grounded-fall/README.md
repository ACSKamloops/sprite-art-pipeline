# Grounded knockdown/recovery repair

This is an actual GPU pixel-support guard, separate from visual approval. Only knockdown/recover authored tracks change. New optional glove-angle and scarf-tail-angle controls apply only to those clips; all other clips retain their previous render paths. The scarf has an editable pivot, keeping its neck attachment while laying its tail along the floor rather than rotating it through the floor. There is no whole-character translation to hide unsupported mass.

At the settled endpoint, actual named layers have opaque support pixels at row 169: torso 1, head 2, front glove 2, rear arm/glove 2. These are narrow pixel contacts, not a claim that the pose has anatomically correct contact forces. The full sprite has no opaque pixel at/below row 170. The resting body is horizontal with bent knees, and recovery begins with exactly the same rendered RGBA and landmarks before lifting through a palm-supported push and standing.

`ground_support.gd` renders actual whole/torso/head/front-glove/rear-arm-glove isolates at five fractional samples/tick, including explicit one-shot endpoints: 331 knockdown samples and 391 recovery samples. All 722 full-sprite samples have zero below-ground pixels. It checks rest mass and glove support, recovery push glove support, knockdown-rest/recovery-opening byte equality, and recovery-end/neutral-start byte equality. The GPU report binds source hashes and renderer. Reach was also checked separately for all 12 clips at 1001 phases each: all four limb target errors 0. The silhouette/material quality still requires the independent reviewer.

The first rejected repair is preserved in `report-first-failed.json` and its source clip snapshot: torso/head grounded, but the rigid scarf rotated below ground. The second rejected repair in `report-second-failed.json` had no penetration but the glove was one opaque row above the floor. The current report passes those objective guards. Actual GPU support strips and the 2x endpoint image make the pixel evidence inspectable.

Run:

```bash
xvfb-run -a godot --path /tmp/copper-scout-parse \
  --script /home/astra/projects/sprite-construction-lab-rig-pilot/pilot/rigged-character/contact-proof/ground_support.gd \
  --rendering-method gl_compatibility --audio-driver Dummy
```

No physics collision, arbitrary slope, mirrored contact, or production art approval is implied. Historical locomotion contact results bind their earlier global source hashes and must be refreshed after these source changes, even though walk/run tracks remain unchanged.

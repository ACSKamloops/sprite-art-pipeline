# Upright Captain source-owned rig — audition, changes requested

This entirely new construction uses `source/native-256.png` (SHA29266199...), not the old crouched portrait. `design.json` declares newly inspected hip/knee/ankle coordinates and source ownership polygons. Fixed bone lengths derive only from this master. Pure visible-source parts recompose every RGBA byte exactly. Complete concealed thigh tubes, proximal knee/boot cuffs and upper hinge/neck/elbow backing are explicitly authored source-palette construction, not recovered anatomy.

The halo is a separate **chest-owned backpack** layer. Head/gaze angle is zero, but its position follows the chest attachment. The red pauldron stays chest-owned rather than being dragged as shield art. Sword upper arm and forearm are split at an inspected elbow; wrist, hand and blade remain one rigid source-owned grip cluster. Rigid greaves/boots are never stretched, fitted or resized per pose. The renderer uses a named Scale2x8 rotation approximation, not a true RotSprite claim.

## Two frozen trials

`motion.json`: eight explicit contact/down/passing/high poses, shallow source-derived ground projection [-24,+8], opposite .5 support halves, high swing clearance and modest swing boot pitch. `motion-gentle-longer.json`: separate longer [-36,+12] trial with approximately8–10px swing lift and lower swing pitch; pelvis is authored1px lower to keep source chains reachable. No adaptive hip shifts, limb stretching or foot-specific positioning feedback are used.

Each has an actual eight-key held version and a72-pose linearly interpolated version. They are different temporal artifacts. Neither inherits an art approval from source reconstruction, reach tests or another sprite. `geometry-preflight.json` samples361 phases for both; the minimum fixed-chain reach margin is0.248px in the longer variant. This is a rendering bound, not an anatomical score.

**Actual fresh reviews remain changes_requested.** The first upright rig is genuinely taller, and opposed lifted feet/new source materials are readable. But source combat-wide tracks put support away from body mass; the high lift can read as marching, incoming flat boots lack a convincing heel presentation, the far gold kneepad/greave rotates like a flat panel, and a narrow diagonal background notch is visible at the ankle during swing. A connected alpha component does not excuse that cuff slit. Gentle timing/interpolation is not a cure. These controls are preserved; narrower under-body tracks and authored distal ankle underlap are a separate follow-up. If perspective/heel shape remains wrong, alternate source-attached foot/greave drawings are required.

## Repeat and inspect

```bash
python pilot/captain-upright-rig-v1/render.py --keys-only --output "$PWD/pilot/captain-upright-rig-v1/artifacts/frozen-v4-eight-key"
python pilot/captain-upright-rig-v1/render.py --output "$PWD/pilot/captain-upright-rig-v1/artifacts/frozen-v4-dense"
python pilot/captain-upright-rig-v1/render.py --motion pilot/captain-upright-rig-v1/motion-gentle-longer.json --keys-only --output "$PWD/pilot/captain-upright-rig-v1/artifacts/gentle-eight-key"
python pilot/captain-upright-rig-v1/render.py --motion pilot/captain-upright-rig-v1/motion-gentle-longer.json --output "$PWD/pilot/captain-upright-rig-v1/artifacts/gentle-dense"
python pilot/captain-upright-rig-v1/verify.py
```

Old outputs are refused. Constructor writes only to the requested fresh output. `verify.py` independently repeats all rendered layers/full frames, checks eight-key/dense equality at authored phase samples, palette/hardalpha, no clipping and source SHA rejection. Verification caches upscaled images at64 rather than16 entries; cache eviction changes runtime only, and every resulting RGBA surface is still compared.

Run `audition_specs.py PACK` for each pack, then use the root readonly `pilot/motion-review-harness/export_motion.py --spec PACK/audition-in-place.json --output FRESH_DIR --loops 2` and repeat with `audition-moving-root.json`. Its exact current bytes are archived as `export_motion_frozen.py` for portable repeat. Each output has normal/half-speed, native/2x colour and silhouette MP4s plus an HTML player. All use one fixed canvas and actor origin, fixed-world grid, no recentering or limb-specific fitting. Moving-root mode uses declared physical root and one shared actor draw translation with pixel rounding; no contact-lock compensation is silently applied. Codec timestamps are checked; YUV444 decoded RGB can differ≤2LSB. PNG parts/frames remain exact.

`video-receipt.json` binds all64 videos across eight exports. The source cycle is1200ms, played twice normally or twice at half speed; the harness adds a1ms endpoint packet. Neither these timestamps nor analytic sole-target stationarity certify actual wholeboot material/pixel contact. One shallow three-quarter view only; user-provided/imagegen Captain art is not labelled CC0. New animations, alternate source drawings, game engine/collision physics and user acceptance remain outside this audition.

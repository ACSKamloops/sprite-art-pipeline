# Lyra front-right leg repair

V4 is a reviewed **candidate for human timed playback**, not an approved game
replacement. It improves repeated boot shape, visible trouser proportions and
returning-foot separation. The reviewer found no new blocking fault in all eight
poses/pairs/wraps, but stiffness, a possible loop catch and slimmer appearance
remain actual playback questions. No numerical quality score is assigned.

Serve this folder and open `delivery-v4/` for synchronized before/after playback,
normal/quarter speed, frame stepping, native/integer scales and MP4.

## Method

1. Freeze the eight original 128×128 cels, fixed pivot (64,112) and 9/160-second
   exposures: 450 ms total. Retain all originals under `inputs/`.
2. Request new lower-body paint with built-in OpenAI ImageGen, retaining the
   actual prompt/references in REQUEST-v1.json and raw return under `raw/`.
3. Register the **entire** four-by-two returned sheet once. V1's cleaner leather
   did not resolve the passing-leg connection or isolated long toe.
4. Use the selected painted donor boots/trousers in `candidate-v1/00.png` and
   `04.png` as explicitly owned P/Q cloth, calf and foot parts. These are authored
   2D partitions, not recovered anatomical joints or a 3D rig.
5. Inverse nearest sampling retains source-texel maps. Keep foot/calf articulation
   separate. Increase visible trouser area, narrow/taper shafts, and revise the
   returning-foot path through the second support exchange.
6. Preserve original y<78 and all pixels outside the declared edit masks. Do not
   recenter individual frames or alter the 450 ms clock to conceal shape changes.
7. Inspect each full actor, every predecessor/current pair and 7→0. Preserve the
   V1/V3 critiques and V4 review rather than treating better material as gait proof.

## Portable rebuild

With Python, NumPy and Pillow:

```bash
python3 rebuild.py --output /path/to/a-fresh-output-directory
```

`rebuild.py` replays the retained source-texel maps and painted parts, verifying
every layer and all eight final PNG files before writing the replay receipt.
It makes no model call. The portable geometric authoring variant is
`author_pose_geometry.py`; it replaces the historical absolute ownership
dependency with explicit protection masks and writes new parts/layers/maps.
It is **not** the exact replay authority: a fresh test with NumPy2.5.4 changed50
pixels across5 poses compared with the original NumPy2.3.5 calculation. Frozen
maps reproduce the retained output exactly and avoid re-solving those floating
inverse transforms. New authored geometry needs fresh output/review.
`build_parts_v4.py` and `build_delivery.py` are the unmodified historical producers
and retain their old paths. Do not blindly run them in this copied folder.

## Editable/export evidence

`delivery-v4/lyra-walk-SE.aseprite` plus its `.sprite-lab.json` sidecar preserves
the animation for LibreSprite/Aseprite. The editable JSON separates protected
upper paint from editable baked lower paint. Full articulated authoring parts
remain in `candidate-v4/parts/` with the source recipe.

Actual LibreSprite save/reopen and sheet rendering were checked against the
editor-normalized source. Fully transparent hidden RGB was zeroed at 16 declared
pixels for editor rendering; the authoritative PNGs retain original RGBA. The
exact coordinates are in delivery-v4/VERIFICATION.json. All visible/partial-alpha
pixels remain exact. That normalization is not an art correction.

APNG retains exact 9/160-second holds. External editor millisecond holds use
cumulative rounding and keep the original clock in the sidecar. The 3.6-second
160 fps MP4 repeats all eight complete 450 ms loops, without a duplicate wrap pose;
its YUV420 colors are preview-only. PNG/APNG is the pixel authority.

See [V4 review](review-v4/REVIEW.md), earlier
[V1](review-v1/REVIEW.md)/[V3](review-v3/REVIEW.md) findings and
[verification](delivery-v4/VERIFICATION.json).

The original browser automation partially failed on a control selector after
frame stepping; that is not a visual or full-browser acceptance. This copy's
HTML corrects the accessible Speed/Scale labels. Continuous human playback
acceptance has not been recovered from the interrupted session.


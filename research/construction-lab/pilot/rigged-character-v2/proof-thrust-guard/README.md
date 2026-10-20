# Thrust guard recovery repair

Source commit `6fba42e` fixes an independently observed supported-state boundary defect. Side thrust began/ended with hand [126,108] and blade angle 0.1, while equipped idle uses [128,110] and 0.55. Front thrust used a 1.2-radian guard whereas equipped idle uses 0.8. The preparation/recovery endpoints now match those guards. Strike/intermediate keys, duration 48 ticks, and events at ticks 0/17/25 retain their original meanings and timing. Back thrust was already exact and is unchanged.

The previous 96-pack and its evidence remain historical under `../private-final96-repaired/`. Fresh full export lives in `../private-thrust-guard-final96/first/` and `../generated/`.

`compare.py` independently compares every raw full-frame RGBA image with the previous pack, then compares both thrust endpoints with equipped idle tick 0 in all four views. Its receipt reports 6,000 frames, only three changed bindings, 93 exact preserved bindings, and eight exact rendered guard boundaries with identical geometric metadata. It rejects overwrite of an existing audit.

`guard-before-after.png` retains the old terminal pose alongside actual new preparation, strike, recovery and guard frames. It has been visually inspected. The lowering guard fixes the hard-cut recovery issue; front/back thrust reach remains a comparatively restrained orthographic prototype motion, not newly approved depth attack artistry. Left is the acknowledged right-view mirror.

Reproduce from the repository root with fresh output directories:

```
python pilot/rigged-character-v2/build_exports.py --private-output "$PWD/pilot/rigged-character-v2/private-reproduce-thrust"
python pilot/rigged-character-v2/proof-thrust-guard/compare.py pilot/rigged-character-v2/private-final96-repaired/first pilot/rigged-character-v2/generated /tmp/new-thrust-comparison.json
godot --headless --path pilot/rigged-character-v2 --script res://verify_api.gd -- /tmp/new-thrust-api.json
xvfb-run -a godot --path pilot/rigged-character-v2 --audio-driver Dummy --rendering-method gl_compatibility --script res://verify_render.gd
```

The final command rejects an existing GPU audit. GPU equivalence covers the complete actual SpriteFrames atlas rendering plus four live source samples per binding at the same 192×192 canvas, nearest sampling, Godot GL Compatibility/Mesa llvmpipe. It is not a cross-renderer determinism claim or general artistic approval. Source hashes and actual render/export receipts accompany this checkpoint. Moving-world contact and independent timed visual review remain separate evidence.

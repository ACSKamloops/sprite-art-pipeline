# Current provenance-bound repaired walk

The current sequence is
`ec1b861d61c259978dd153944006d8c81500471d1aeff68e043b3ecfb35cdba6`.
Its eight RGBA frames, exact rational holds, canvas and loop/play count are
identical to the earlier reviewed repaired sequence
`9f9e1c53324ea567cb1bbd5be8c310691c0f87f45044279c1f37d81349e66d79`.
Only provenance bindings changed. Prior visual caveats and lack of production
or seamless-loop approval therefore remain unchanged; no new art review or
provider call was performed.

## Fresh actual Godot run

The new export was copied from
`/home/astra/artifacts/pixellab-motion-pipeline-20261014/review/bound-manual-repair/exports/studio-7ffd8c2a452d4fb18f9a26dc3c4df606/godot`
into a fresh project under
`/home/astra/artifacts/pixellab-bound-walk-proof-20261014/godot`.
An actual Godot editor import preceded headless resource/playback checks.

All **74 engine checks passed** on Godot4.7.2-stable official
`ed1daf0bf001b61586d9930840f2f1394092c079`: eight actual imported texture
regions decode to the exact256×256 reference PNG RGBA; resource reload retains
loop/holds; every midpoint and pre/exact clock boundary passes. Normal1×
elapsed playback completed three cycles over5.134296 measured wall seconds.
All eight frame callbacks and three boundary loop callbacks were observed;
pause freezes state and restart resets clock/frame. The exported driver and
original seven Godot/eight PNG inputs remain unchanged.

The same proof script now accepts `--sequence` while retaining the old default:

```bash
python docs/motion-pipeline-20261014/verify_repaired_walk_godot.py \
  --sequence ec1b861d61c259978dd153944006d8c81500471d1aeff68e043b3ecfb35cdba6 \
  --export-godot /home/astra/artifacts/pixellab-motion-pipeline-20261014/review/bound-manual-repair/exports/studio-7ffd8c2a452d4fb18f9a26dc3c4df606/godot \
  --output /home/astra/artifacts/pixellab-bound-walk-proof-20261014/godot
```

Choose another absent output directory to rerun. Exact commands, source hashes,
engine precision observations and results are in
[BOUND-WALK-GODOT-PROOF.json](BOUND-WALK-GODOT-PROOF.json), SHA256
`23a09b3756331cea5f1fe522b312072676bf191c77120c7b953c8d2ed1f683c0`.
The rational manifest remains authoritative for5/24 holds and5/3total;
SpriteFrames hold approximation and headless/event-coverage limitations are
unchanged from [the prior proof](GODOT-WALK-PROOF.md). Original9f9e1c proof
files and external receipts were preserved.

## Independent cold editable closure

The actual new editable folder was imported into a separate new QA Store,
using a read-only snapshot of current runtime modules. **146 explicit closure
predicates passed**; these are evidence checks, not146 additional unit tests.
The current sequence and exact selection receipt replay, all eight prior/new
frame pixels/holds, and frozen experiment prompt/input/request hashes match.

The bound extraction
`5acb3d5637dcc1b4a8dc65e5a86a0216463bf3ddd6a9163399452cffa331d7b6`
reaches both admission and download receipt. The cold Store retains and verifies:

- Packet `c3db9ed21c0906d42301a59e0dd4bb73805d93fbe6cdc0be056d7e0496e8e580`,
  exact request-body bytes, first/last role order, and the exact input PNG
  bytes embedded in both Base64 request items.
- Native admission `78bdd1514622d2aca6a8e81344f80b3a437ebe819473bf6322c047a26df6f5e7`,
  its actual retained probe, succeeded completion and raw MP4 bytes/hash.
- Download receipt `f519e88c60f53a80e7273a1bf5d0331f6807cb5e18e8abd8724513dca1bbd71e`,
  matching task/model/packet/video, completion-body digest and returned-media
  URL digest. Its no-auth/no-cookie/no-redirect declarations survive.
- All107 native768×768 raster payloads with1/24holds and all107 PTS entries.
  Requested family is MiniMax-H3; checkpoint and quality remain null.

[BOUND-WALK-CLOSURE-PROOF.json](BOUND-WALK-CLOSURE-PROOF.json), SHA256
`5e509286a5d01a943d22d8f5628167e8ce82fe82676f4c7d7b981020bd6e1f3d`, pins the exact graph IDs and checks. The external
artifact scope is `/home/astra/artifacts/pixellab-bound-walk-proof-20261014`.

These checks establish immutable local byte/graph consistency. Supplied
completion JSON and producer download receipts are not provider signatures or
independent attestation. No HTTP, credential access, regeneration, source Store
mutation, GPU/game rendering, world foot-contact or art-quality acceptance is
part of this follow-up.

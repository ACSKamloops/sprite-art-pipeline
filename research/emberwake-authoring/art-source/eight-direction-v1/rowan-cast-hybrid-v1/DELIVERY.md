# Rowan hybrid cast — unreviewed delivery

Six candidate frames are in `candidate/{southeast,northeast}/{17,18,20}.png`. Original19 release and22 neutral context are copied beside them without changing their PNG bytes. Root owns integration and the fresh art review; no score is assigned.

Original128-stage body/head/legs and pivot(64,112) remain. Only explicit old-fist and donor hand/forearm union masks change. Every pixel outside that union, including transparency, is exact; every pixel from y84 down through the boots is exact. Source22 supplies clothed torso/background only where an old fist occluded it. It is declared underpaint, not invented hidden anatomy. No model call or new paint was used.

Preparation17→18 moves the complete open donor hand2px right and1px up with a small proximal-map progression. The same real hand paint is reused rigidly, not redrawn; these are different composited poses on the respective original17/18 bodies. NE's palm projects outside the torso. Original release19/socket remain. Recovery20 uses a complete relaxed donor glove. Counter-arms retain their original fists.

`construction-spec.json` declares the literal donor polygons, old-fist polygons, hand/cuff plateaus, proximal controls and offsets. `maps/` retains source/target ownership, source coordinates, frozen triangles and masks. `inputs/` includes original registered bodies, exact raw model returns, native donor PNGs and their maps into those returns. `input-hashes.json` binds all37inputs. `replay_frozen.py` independently checks nested source maps back to raw return pixels and exact outside-mask preservation.

`editable/` contains the initial/final two-layer project, six actual masked-import transactions, receipts and replay journal. The body outside the union is locked; owned arm cells are editable. Undo, redo, journal replay, rendered PNGs and the toolkit ORA roundtrip passed. No external editor was opened. Zero manual source-palette seam edits were needed.

Compare `proofs/{southeast,northeast}-{light,dark}-chronology.png` at native,2x and.66. `media/` holds four exact one-shot control/hybrid APNGs with original60/80/100/80/80/100ms holds (total.50s), rational-delay receipts and decodedRGBA checks. No extra animation frames or timing changes were introduced.

Known limits: donor cuffs/gold elbow detail differ from old armor; SE's relaxed recovery crosses the torso/waist; natural wrist/elbow volume still needs independent review. Final alpha is connected and the source maps replay, which do not establish anatomy or motion quality. No human continuous playback, browser/game test, VFX-origin change or controller acceptance is claimed.

Failed trials are retained. Initial NE recovery controls collapsed a triangle; a first donor mask clipped glove fingers; a later erasure left4old-fist edge pixels; the first SE palm touched outer hair. These were corrected through explicit map/mask/plateau placement changes, with no hidden repaint.

Reproduce into a fresh folder:

```bash
python replay_frozen.py --output /absolute/fresh/replay-folder
```

Read-only verification:

```bash
python replay_frozen.py
sha256sum --check --quiet SHA256SUMS
```

`build_hybrid.py` retains the authoring recipe; frozen maps/triangles are the transport authority. `package_hybrid.py` retains editable/media packaging. Run those only in a disposable copy because their output paths are fixed. Root should provide anonymous paired images/clocks to the next reviewer and withhold this producer history until that report is frozen.

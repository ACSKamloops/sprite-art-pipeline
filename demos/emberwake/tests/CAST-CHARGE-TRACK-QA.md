# Cast preparation charge attachment

`cast_hand_tracks` is optional manifest data: `{view: [[x,y], ...]}` in native cell pixels, with one point for every exposure in that view's cast clip. Partial view declarations are supported; other views and legacy four-view banks keep the fixed `cast_hand` socket. Points must be finite and inside the cell. Unknown views, incorrect counts, malformed points, release points that disagree with `cast_hand`, and inconsistent points for repeated cels reject the bank before atlas loading. A rejected selection preserves the working bank and pending action.

Only `cast_charge` uses `get_cast_charge_hand_global()`. It follows the displayed `current_art_frame`, begins at exposure zero before the cast clip is displayed, and projects through the existing pivot, sprite scale and actor transform. Repeated cels, including the first/final cel 22 in the source strip, share an attachment. Projectiles and release flashes keep `get_cast_hand_global()`; the `.24` release, locked aim, damage and physical collision behavior are unchanged.

## Executed validation

Godot `4.7.2.stable.official.ed1daf0bf`, 2026-10-16, assigned worktree `/home/astra/projects/emberwake-charge-track`:

```bash
LP_NUM_THREADS=4 OMP_NUM_THREADS=4 godot --headless --path . --editor --import
godot --headless --path . --script tests/cast_charge_tracks.gd
godot --headless --path . --script tests/eight_directions.gd -- --test-mode
godot --headless --path . --script tests/spells_v2.gd
```

Baseline results: focused fixture **82 assertions**, direction fixture **161**, spells **80**. The focused fixture drives actual hero requests and actual charge FX across two different preparation points with the same facing. It checks the displayed frame independently of the action clock, actor transforms/movement, fixed release/projectile/flash behavior, duplicate cels, partial and legacy fallback, and atomic rejection before any texture read. It tests `INF`, `-INF` and `NAN` directly and overflowing JSON through the real loader. That intentional overflow case emits Godot's expected `WARNING: Exponent too high`; completed runs have no script or engine errors.

Temporarily copied only atlas/manifest files from `/home/astra/artifacts/emberwake-charge-track-bake-v1/{rowan,lyra,brann}` to the corresponding runtime paths, imported them, then ran:

```bash
godot --headless --path . --script tests/cast_charge_tracks.gd -- --production
godot --headless --path . --script tests/eight_directions.gd -- --test-mode --production
godot --headless --path . --script tests/spells_v2.gd
```

Production results: focused fixture plus every production cast exposure **241 assertions**, existing production resource/behavior checks **1,163**, spells **80**. The focused production mode requires actual eight-view banks and diagonal tracks, and samples all six cast exposures in all 24 character/view combinations. These tests verify declared coordinate projection and behavior; they do not identify anatomical hands or certify art/motion quality. Root's paint measurements and visual review remain separate evidence.

| Bank | Manifest SHA-256 | Atlas SHA-256 |
| --- | --- | --- |
| Rowan | `759cc8e047c95f77f978d5dd0ecdb3a47a737d19e060dab086c1172a2846966c` | `87e6502359cf38c3a8048efbd10cc5e626b5497ca695e42915664ade9910859b` |
| Lyra | `f1405b584e5fa72f2bfc31e707854322afc7f3892c5bdbf864c25e0e0edde81f` | `dc2bd5562c05137d6eb59c37263ea3988ae1b35e84f5c984ee2c9e165b7065b5` |
| Brann | `332981c0aef0c660cbc6ac625d61044ab65c467f66acd1c12530eaae2264b594` | `c3067c050df04dfe52d47c6cab211e10837a5d4133fd079c017d31313db5bfed` |

All six temporary asset files were restored byte-for-byte using saved baseline SHA-256 values, then reimported successfully. No assets, baker changes or generated evidence are included in this change. Local execution logs, production receipts, copied-file hashes and restoration verification remain in `output/charge-track-validation/` (ignored).

## Canonical v6 checkpoint

The previous section records the isolated code-worker run and its temporary v5
assets. Root subsequently installed `registration-v6-all-charge-tracks.json`,
which adds measured cardinal preparation tracks as well. The broad suite now
includes this focused test in production mode: **1,804 assertions and 378 route
samples pass**, including the focused **241**. The focused case iterates every
exposure in all 24 actor/view combinations; only diagonals are explicitly
required to declare tracks, while v6 supplies all eight views per actor.

Separate real native GPU rendering passes **657 assertions**, retaining **24
release and 48 preparation pairs** at `.10` / `.19` seconds under
`docs/evidence/eight-directions-systems/charge-track-v1/`. That receipt binds the
actual v6 manifest and atlas hashes. The ordered source/mapped-point witnesses
are under `art-source/eight-direction-v1/cast-track-measurements-v1/`.
The bake's **3,140** checks include exact old cels/holds, mirror geometry,
ordered charge points, repeated-cel agreement and release agreement. None of
these mechanical receipts certifies finished walk art or continuous motion.

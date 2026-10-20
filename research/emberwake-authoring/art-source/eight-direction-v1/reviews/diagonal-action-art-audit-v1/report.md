# Selected v10 diagonal action art audit

The v10 preview has complete attack/cast bindings for Rowan, Lyra and Brann in all four diagonal views, but only **two separately painted directions per hero**. Southeast and northeast come from retained new diagonal paint; southwest and northwest are exact reflected derivatives. No selected diagonal action cel is made by deforming a frozen cardinal action cel in this baker. This provenance finding is separate from visual acceptance.

The highest-priority visible issues in this bounded action audit are:

1. **Brann NE/NW attack follow-through hand clarity:** cell 11 has a more finger-lobed, partly relaxed silhouette than the compact fist in 10 and 12. Closing it is a useful bounded experiment. Detailed inspection does **not** justify calling it a fully splayed casting palm or a proven anatomical failure. My early message overstated that interpretation; this frozen finding supersedes it.
2. **Rowan NE/NW cast recovery:** cell 20 drops the hand below neutral immediately after the high release pose, with no intermediate-height return drawing. The pose discontinuity is clear in still chronology; a perceived snap during playback remains unverified.
3. **Rowan NE/NW cast preparation material:** cells 17/18 introduce a conspicuous bright ivory/silver cuff with a gold joint and hooked elbow profile, then release 19 returns to a narrower grey metal treatment. At 84 pixels that small bright bend remains prominent. This is a material/volume continuity concern, not a detached-arm allegation.

These are priorities within the selected attack and cast banks, not an exhaustive library ranking. The first finding has medium confidence because knuckles, wrist rotation and partial relaxation can produce similar silhouettes. Findings 2 and 3 are clear drawing differences, with medium confidence about their practical playback severity. I found no comparably clear Lyra-specific problem that should displace these three; I did not invent one to produce one finding per hero. No numeric scores or walk ratings are inherited.

## Actual coverage and behavior

| Item | Verified selected coverage |
|---|---|
| Heroes | Rowan, Lyra, Brann |
| Diagonal table clips | 12 attacks plus 12 casts = 24 bindings |
| Primary painted streams | SE/NE × 3 heroes × 2 actions = 12 streams |
| Reflected streams | SW from SE; NW from NE = 12 additional bindings |
| Attack | cells 08,09,10,11,12,13,14,22; eight distinct exposures; 0.410 s, nonloop |
| Cast | cells 22,17,18,19,20,22; six exposures but five distinct drawings; 0.500 s, nonloop |
| Cross-action reuse | cell 22 is shared neutral for attack return, cast start and cast return, as well as idle |
| Spell reuse | firebolt and nova both select the same directional `cast` body clip; they have separate effects/gameplay code |
| Heal | emits its action event without selecting a separate heal body state in the inspected hero code |

The audit binds all 168 selected attack/cast exposures. They reference 144 actor/view/source-cell combinations, or 72 before the reflected views. Of those 72 primary cells, 65 reconstruct exactly from uniform registration of the six raw diagonal sheets, six are Rowan's hand/forearm hybrid overrides, and one is Brann SE neutral 22's eye override. These counts describe provenance, not art quality.

The actual v10 project catalog maps Rowan to `assets/hero`, Lyra to `assets/characters/lyra`, and Brann to `assets/characters/brann`. Each project's atlas and animation manifest is byte-identical to its v10 bake counterpart. All 168 extracted project cels match the selected baked cel or its exact reflected derivative. The reflection reverses x and adds +1 pixel so the mapping is x→128−x about pivot x=64. It does not independently author handedness, lighting or equipment for the reflected view.

The attack holds are 60,70,55,55,65,35,35,35 ms. Phase starts are 0,60,130,185,240,305,340,375 ms. The inspected hero code schedules the attack hit at 160 ms, within the full-jab cell 10 exposure. Cast holds are 60,80,100,80,80,100 ms, with release phase 3 / cell 19 beginning at 240 ms. Firebolt and nova use that same body release. These are manifest/code findings; no engine was run and no actual hit/VFX alignment was observed.

## Source provenance and reuse

The selected configuration is `art-source/eight-direction-v1/registration-v10-brann-front-weight.json`, SHA-256 `1dc8918ac8bc69bcc57615bf8071137ae911d811a9b22df9c19e689dacec6da3`. It matches the v10 replay receipt. The current diagonal baker also matches the baker hash recorded by that receipt.

| Hero/view | Selected original paint | SHA-256 |
|---|---|---|
| Rowan SE | `art-source/eight-direction-v1/raw/rowan-southeast-initial.png` | `cf76a78ceabde8db48e65e0b8d8006dbcf65a779431f08bb2e8c6af569da48e6` |
| Rowan NE | `art-source/eight-direction-v1/raw/rowan-northeast-initial.png` | `316b7f6f07d7b77b4b8863a62fe45c8d9589842dfdd533a6f9d80064dea181ba` |
| Lyra SE | `art-source/eight-direction-v1/raw/lyra-southeast-initial.png` | `4e4050324cc3b6bd6da9bec1fbd33258386cb50a0ed0eac6404f6fc102670823` |
| Lyra NE | `art-source/eight-direction-v1/raw/lyra-northeast-initial.png` | `a8e77dbdaf0c1de47d71ef9429df558bf9159d325e29889b17e354d21542d738` |
| Brann SE | `art-source/eight-direction-v1/brann-source/raw/brann-se-initial.png` | `c6e2722e9a94e29f695a326526a832d1bc215058c21e5f363bb28c8a76f54d9a` |
| Brann NE | `art-source/eight-direction-v1/brann-source/raw/brann-ne-initial.png` | `e631a1b0e7eb9e346f5d237a87830beed97f44bb3ef5e12857e18def8881cd0d` |

Retained requests identify built-in ImageGen and new diagonal pose banks conditioned on appearance references. Their prompt and appearance hashes verify. Here, “new painted direction” means a separate retained diagonal sheet; it does not mean manually drawn cels, successful anatomy, or independent temporal authorship for every exposure. The selected raw sheets are resized nearest to 2048×1024, separated by connected ownership, alpha-thresholded and uniformly scaled/translated onto 128×128 stages. Those registration operations are not new drawing.

Rowan cells 17,18,20 in both primary views use selected overrides from `rowan-cast-hybrid-v1/candidate`. The construction recipe retains original diagonal bodies, replaces an explicit old-fist region using neutral 22 underpaint, and source-maps complete hand/forearm donors from additional same-view action crops. Preparation 17/18 reuses the same donor hand with small translations and proximal deformation. Recovery 20 uses its recovery donor. Release 19 remains the original diagonal paint. This is a hybrid of new directional body paint and reused/deformed same-view arm paint, not a fresh whole-body cast drawing at every phase and not a cardinal-cel deformation.

Brann SE neutral 22 has a selected eye override and serves attack/cast returns as well as neutral. Lyra has no selected overrides in the inspected attack/cast source cells. Walk overrides are irrelevant to this audit and receive no action-art credit. None of the primary diagonal attack/cast cels is RGBA-identical to a frozen cardinal attack/cast cel or its pivot-correct reflection. That equality check complements the actual bake path; it cannot rule out unrecorded visual influence inside a generator.

## Three bounded repair experiments

**F1 — Brann, NE attack phase 3, source cell 11; NW inherits the reflection.** The hand at approximately native x=99–113, y=29–43 changes from the compact rounded fist in c10 to short finger-like lobes in c11, then returns to a guard fist in c12. The ambiguity weakens a clean same-fist jab read at 84 pixels, especially beside Brann's clearly open spell hand. It is a gesture-clarity concern. A rotated clenched fist can show knuckle lobes, so this is not proof that the hand has become a cast palm.

- Exact v10 baked cel: `bake/brann/northeast/11.png`, PNG SHA-256 `909c8cbb094d0a6108c2740adb394288501c91f4c154f2f5b4e531212ab71d98`; project atlas index 179, phase interval 185–240 ms. Raw source is the Brann NE sheet in the provenance table.
- Smallest experiment: alter only the hand silhouette into an unmistakably closed glove, preserving wrist, forearm, body and holds. Compare c10→11→12 in NE and its NW reflection at 84 pixels. Expected benefit is consistent jab gesture. Keep the original if the closed hand harms volume or follow-through clarity.

**F2 — Rowan, NE cast phase 4, source cell 20; NW inherits the reflection.** The high release hand in c19 gives way to a relaxed hand below the shoulder and below its neutral tracked position in c20. The following c22 brings it back inward/up. This single recovery cel therefore reads as a downward overshoot rather than a visibly halfway return. In the supplied cast-hand metadata, the anchor goes [99,45]→[89,77]→[83,73]; these are visual socket annotations, not physical joints. The high-to-low transition remains visible in the 84 pixel sheets. Whether the action actually snaps at speed requires playback.

- Exact override: `art-source/eight-direction-v1/rowan-cast-hybrid-v1/candidate/northeast/20.png`, also exact v10 baked `bake/rowan/northeast/20.png`; SHA-256 `badde89ee497e2f7c13004a7578c806204e08ba2ee3fba7dc6660180c12ca7a8`. Project atlas index 172, phase interval 320–400 ms. Release c19 SHA-256 `84208f254f26392d88e13ba8c30e6cfa58ebdf62c92e0bc2a5184402b48e9eef`.
- Smallest experiment: make one intermediate-height recovery arm for c20, retaining the body and original c19/c22; preserve the six-exposure 0.500 s timing for the first comparison. Expected benefit is a visibly traceable release-to-rest path. Do not infer missing bones or repaint the whole character from this concern.

**F3 — Rowan, NE cast preparation phases 1/2, source cells 17/18, followed by c19; NW inherits the reflection.** Around native x=82–95, y=55–71, the donor arm creates a bright thick elbow/cuff bend with ivory highlights and gold trim. Release c19 has a narrower grey segmented bracer. The preparation's bright hook remains one of the most salient small forms at 84 pixels. Both states are individually readable, but the same garment changes material/section treatment across the action. The arm is visibly connected; I am not alleging a gap or joint dislocation. SE has a related donor treatment, but NE provides the clearest evidence.

- Exact overrides: `rowan-cast-hybrid-v1/candidate/northeast/17.png`, SHA-256 `14206f73c928aaae3ac1e14bb895de4b8f7ddee37c33dd37a08321c32929788a`; and `.../18.png`, SHA-256 `973ebc6a9c9b00ce051cbd6d690038972c0bb5f115fa547ac4e7e17116b3aa21`. Both are under `art-source/eight-direction-v1/`. Project atlas indices 169/170, intervals 60–140 and 140–240 ms. c19's hash is given in F2.
- Smallest experiment: adjust only the owned cuff/elbow treatment to the same view's original metal palette and section thickness, keeping fingers, hand positions, torso and timing. Compare 17→18→19 on all three grounds. Expected benefit is stable clothing/material identity. A broad arm warp would confound this test with a new pose.

## Evidence, preservation and limits

`exposures.json` provides exact hero/action/view/phase, atlas index, source cell, source PNG hash, raw hash, override, hold, start time and project atlas hash for every selected exposure. `clips.json` preserves the 24 exact timelines; `registration-verification.json` records in-memory reconstruction of all 72 primary source cells; `reuse-checks.json` records the cardinal equality comparisons. Source inputs were read only. All writes are within this fresh audit directory. The canonical checkout, baked preview and previous frozen P07 review were not edited.

I inspected all selected action cels at 256 pixels on light, 128 on light, and 84 on game and dark grounds through `view_image`. The focused findings sheet was inspected at all nine combinations of 128/84/256 and light `#e7e3d6`, dark `#22252b`, game `#27392f`. Complete proof sheets for this bounded attack/cast set exist at all nine combinations; the inspection ledger distinguishes generated sheets from actually inspected sheets. Each uses exact nearest whole-canvas resizing and alpha compositing, with labels outside the stage. The 84 canvas is the requested integer approximation of 0.66×128, not a claim about a running engine's sampling. A supplemental 3× coordinate aid helped inspect the small hand and cuff shapes.

This is a static art/provenance audit. Chronology is reconstructed from cels and declared holds; no continuous normal-speed perception, actual combo, runtime, controller, model, editor, VFX, root-motion, physical contact or damage behavior was tested. The cast body reuse does not prove firebolt and nova are indistinguishable in the complete game, because their effects differ. Reflection coverage does not approve future asymmetric equipment. Three visual concerns do not constitute acceptance or rejection of the whole library.

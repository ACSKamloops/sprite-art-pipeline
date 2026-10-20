# Independent cold review: Brann diagonal walks

The costume, face and overall character remain recognizable. The lower-body drawings do not yet sustain a convincing eight-key walk: the middle keys repeatedly turn a solid leg into a thin, cut-out-looking branch, and the rear-facing feet change volume and connection too abruptly. These are useful internal movement placeholders, but I would repair the lower bodies before treating the walks as finished game art. Most of the upper-body work can be retained.

## Scope and verification

This review used only `input-v1/REVIEW-CARD.md`, `input-v1/INPUTS.json` and the images listed there. All **73 image SHA-256 values match**: 32 nominated diagonal keys, 40 cardinal context images and one reference. Inputs were not edited. The cardinal walks, cardinal idles and reference were used only for identity and static turn context; their animation quality is not rated here.

Every nominated key and every adjacent pair, including **07→00**, was inspected in chronological sheets at native resolution, nearest-neighbor 2×, and the requested 0.66 game scale on all three backgrounds. There are 32 unique keys and 32 unique cyclic pairs, each inspected under nine scale/background conditions. Each chronological row includes 00 again after 07 so that the wrap can be compared directly. The backgrounds are uniform light `(234,230,220)`, dark `(26,29,36)` and ground green `(91,103,70)`. The 0.66 raster preview rounds the 128-pixel stage to 84 pixels. This is a diagnostic compositing choice; engine filtering and fractional screen alignment were not tested.

The specified timing is **eight equal 56.25 ms holds, 450 ms per cycle**. I inspected still chronology and adjacent drawings, not continuous timed playback. I can identify malformed contours and weak correspondence between keys; I cannot confirm the perceived flicker, cadence, foot sliding, movement speed, or camera behavior in an engine. Playback predictions below are explicitly labeled. No desired score or pass threshold was supplied.

Coordinates below are approximate source-image regions on the 128×128 stage, with `(0,0)` at top left. **Left/right always means screen-left/screen-right**, not the character's anatomical side. I have not assumed that any named pose has correct anatomy.

## Separate scores

These are editorial 0–10 ratings for the supplied use, not measured percentages. Identity is deliberately separated from motion quality.

| Loop | Drawing | Identity | Motion readability | Practical game usefulness |
|---|---:|---:|---:|---:|
| Southeast | 6.0 | 8.5 | 4.5 | 5.5 |
| Southwest | 6.0 | 8.5 | 4.5 | 5.5 |
| Northeast | 5.5 | 8.5 | 4.0 | 5.0 |
| Northwest | 5.5 | 8.5 | 4.0 | 5.0 |
| Mean across four loops | 5.8 | 8.5 | 4.3 | 5.3 |

**Drawing:** Hair, face, gold shoulder plates, gloves and tunic have coherent volume. Many outer silhouettes are appealing at native size. The score falls because the visible calf/cuff/boot chains in 02–06 are materially less coherent than the torso, especially 03 and the rear-facing 06 keys.

**Identity:** The dark rounded hair, beard in the front-facing diagonals, navy tunic, paired gold shoulder plates, brown gloves and boots, belt and orange front detail remain consistent with the supplied reference and neighboring cardinal directions. The back views retain the same hair mass, gold shoulders and tunic trim. Static facing changes are readable. This does not establish the quality of a live turn transition.

**Motion:** A general alternating leg action and counter-moving hands can be inferred, but the feet cannot always be followed as two solid branches through the middle of the cycle. The sequence therefore reads more like a set of stride suggestions than a cleanly connected walk. The rear loops are weaker because the lifted foot becomes a conspicuous lateral crescent in 05–06.

**Usefulness:** Facing and character selection remain clear enough for prototyping. At game scale, shoulders and face carry the character, while the lower-body action becomes small, dark and intermittently ambiguous. An internal build could use these temporarily; a finished walk needs the repairs below and a timed in-engine check.

## Findings and smallest useful repairs

### F1 — High: thin hooked or broken-looking leg branch in every 03

- **Southeast 03:** approximately `x54–65, y89–108`, the screen-left branch descends as a narrow brown hook beside the solid central/right boot. A near-transparent slit runs inside that hook. The outer screen-right gray thigh is also much broader than the thin branch beneath the glove. This is not a readable full calf/cuff/boot chain.
- **Southwest 03:** approximately `x63–75, y89–108`, the corresponding screen-right branch has the same narrow hook and background slit beside the solid left/central boot.
- **Northeast 03:** approximately `x42–64, y81–102`, the raised screen-left branch becomes a thin diagonal brown strip leading into a small boot-like mass, with several background-colored openings across its connection to the hip area.
- **Northwest 03:** approximately `x64–86, y81–102`, the corresponding screen-right branch has the same fragmented diagonal connection.

The light background exposes these gaps most strongly. Native and 2× make their shape plain. At 0.66 the fine openings partly disappear, but the front key still has a string-like side branch and the rear key still has an irregular, hard-to-follow knee/boot connection. Dark backgrounds conceal the openings; they do not restore the missing volume. These are background leaks through low-alpha or transparent areas, not painted white decoration.

**Smallest useful repair:** redraw only the affected lower-body branch in each 03, establishing one solid trouser segment, a distinct cuff and one boot, with intentional occlusion against the other leg. Re-check 02→03 and 03→04 after that local redraw. Do not change the head or shoulders to solve this.

### F2 — High: rear-facing lifted foot changes into a thin lateral shoe

In **northeast 05–06**, especially 06 around `x65–90, y83–101`, the screen-right lifted branch becomes a thin dark horizontal connection with a large curved brown shoe extending sideways. The opposite boot remains an upright cylinder. In **northwest 05–06**, especially 06 around `x37–63, y83–101`, the screen-left branch shows the corresponding form. The boot no longer shares the volume and clear cuff-to-shin relationship visible in 00/07. Calling it a sideways shoe is my visual reading, not proof of a particular anatomical side or an intended pose.

The shape is conspicuous on light and ground backgrounds even at 0.66. It is less legible on dark, where the branch can resemble a short dark spur beside the main leg. **06→07** then changes that lateral shape back into a stout downward boot in one key. A visible shape discontinuity is established; an actual timed “pop” is a playback hypothesis.

**Smallest useful repair:** redraw the lifted calf and boot in rear-facing 05 and 06 as a single bent limb with consistent boot bulk; make 06 the outwardmost position of a traceable arc rather than a narrow horizontal attachment. Then reconcile 06→07. Preserve the torso.

### F3 — Medium: cuffs, thighs and occlusion do not carry stable branch mass through 02–06

In the front loops, 02 merges the raised branch closely with the lowered glove; 03 narrows it into the hook; 04 overlaps most of the second branch behind one diagonal boot. In 05–06, a broad gray/black edge projects outward at the hip/cuff region (roughly southeast `x69–84, y82–94`, southwest `x43–58, y82–94`). The relationship between that flap, thigh and boot is unclear. In the rear loops, the trouser/cuff silhouette also changes from broad overlapping masses in 04–05 to the thin lifted branch in 06. The issue is the changing connection and volume, not simply that two legs overlap.

**Smallest useful repair:** after F1/F2, trace each visible branch in a two-color diagnostic across 02–06 and redraw only the pixels needed to retain hip→thigh→cuff→boot continuity. Give the occluded branch a deliberate disappearance and reappearance. Do not add a third boot-shaped piece to explain an ambiguous shape.

### F4 — Low observed concern; unconfirmed playback effect: restrained wrap beside larger middle changes

07 and 00 present very similar split-stride silhouettes in all four directions, whereas the middle keys have much larger contour changes. They are not identical images, and the wrap does not show an obvious large positional reset in still comparison. There may be a perceptual linger around 07/00 followed by a more abrupt excursion into 01–03; this is **not confirmed without continuous playback**. Equal holds alone do not establish a bad cadence.

**Smallest useful repair:** first repair the leg drawings, then play the exact 56.25 ms holds continuously with actual world translation. Only adjust the wrap pose or hold timing if a repeated dwell is visible. Do not change timing to conceal malformed anatomy.

## Every key: visible branch progression

This records what can actually be followed in the drawings. “Lowest” describes screen position, not verified ground contact.

| Key | Southeast | Southwest | Northeast | Northwest |
|---|---|---|---|---|
| 00 | Short tucked left boot; fuller right boot extends down-right. Two branches read. | Fuller left boot extends down-left; right boot tucked. Two branches read. | Left boot extends lower-left; right boot is shorter and higher. | Right boot extends lower-right; left boot is shorter and higher. |
| 01 | Left boot lifts/tucks; right shin and boot are fully exposed. | Right boot lifts/tucks; left shin and boot are exposed. | Left boot moves inward below the body; right branch is mostly dark overlap behind it. | Right boot moves inward; left branch is mostly dark overlap. |
| 02 | Left boot turns inward below the glove; right cuff and boot remain solid. Small crotch gap. | Right boot turns inward below the glove; left cuff and boot remain solid. Small crotch gap. | Raised left boot points toward the viewer/left; right shin stays long. Angular opening between branches. | Raised right boot points toward viewer/right; left shin stays long. Angular opening between branches. |
| 03 | Left branch reduces to hooked brown outline beside solid lower boot; broad right gray thigh. | Right branch reduces to hooked outline beside solid lower boot; broad left gray thigh. | Raised left branch becomes narrow broken-looking diagonal connection; right leg stays solid. | Raised right branch becomes narrow broken-looking diagonal connection; left leg stays solid. |
| 04 | One down-right boot dominates; other branch largely occluded. | One down-left boot dominates; other branch largely occluded. | Overlapping branches mostly read as one diagonal lower boot mass. | Overlapping branches mostly read as one diagonal lower boot mass. |
| 05 | Central lower boot with second brown piece behind; right gray hem protrudes. | Central lower boot with second brown piece behind; left gray hem protrudes. | Low central boot overlaps raised right crescent; its shin connection is unclear. | Low central boot overlaps raised left crescent; its shin connection is unclear. |
| 06 | Lower left/central boot and small raised right boot; angular right cuff/hem. | Lower right/central boot and small raised left boot; angular left cuff/hem. | Left leg upright; right branch extends laterally into curved shoe with thin connection. | Right leg upright; left branch extends laterally into curved shoe with thin connection. |
| 07 | Returns to short tucked left branch and long down-right boot. | Returns to short tucked right branch and long down-left boot. | Returns to stout lower-left and shorter right boots. | Returns to stout lower-right and shorter left boots. |

## Every cyclic pair

These pair judgments were checked at all nine scale/background conditions. Backgrounds and reduction change defect visibility; they do not change the order of branches. A “jump” here means a difference between adjacent drawings, not an observed timed playback event.

| Pair | Southeast | Southwest | Northeast | Northwest |
|---|---|---|---|---|
| 00→01 | Right boot remains long; left tucks upward. Understandable separation. | Left remains long; right tucks upward. Understandable separation. | Split stance closes into overlapping central/lower-left mass. Left branch still inferable. | Split stance closes into central/lower-right overlap. Right branch inferable. |
| 01→02 | Left boot/hand area crowds together; right branch survives clearly. | Right boot/hand area crowds together; left survives clearly. | Left branch lifts outward while right becomes long; branch exchange is large but visible. | Right lifts outward while left becomes long; branch exchange is large but visible. |
| 02→03 | Raised left boot loses bulk and becomes hooked side outline. F1. | Raised right boot loses bulk and becomes hooked outline. F1. | Left calf/boot connection thins and gains background slits. F1. | Right connection thins and gains background slits. F1. |
| 03→04 | Thin left hook disappears into overlap; one diagonal boot dominates. | Thin right hook disappears into overlap; one boot dominates. | Thin left branch vanishes into central overlap. | Thin right branch vanishes into central overlap. |
| 04→05 | Lower boot shifts centrally; second brown piece and gray flap emerge. Mass ambiguous. | Lower boot shifts centrally; second piece and gray flap emerge. Mass ambiguous. | Right curved toe begins to separate from overlapped mass; attachment unclear. | Left curved toe separates from overlap; attachment unclear. |
| 05→06 | Opposite/right short boot separates; hem changes to projecting angular edge. | Opposite/left short boot separates; hem changes to angular edge. | Right shoe extends strongly sideways and its connection becomes thin. F2. | Left shoe extends sideways and connection becomes thin. F2. |
| 06→07 | Raised right boot becomes lower forward-looking boot; left branch tucks. Big contour exchange. | Raised left boot becomes lower forward-looking boot; right tucks. Big exchange. | Lateral right shoe becomes stout downward boot; other leg extends lower-left. F2. | Lateral left shoe becomes stout downward boot; other extends lower-right. F2. |
| 07→00 | Similar split stance; modest contour change. No obvious large wrap reset. | Similar split stance; modest change. No obvious large wrap reset. | Similar two-boot stance; modest change. No obvious large wrap reset. | Similar two-boot stance; modest change. No obvious large wrap reset. |

## Scale, background and turn context

- **Native:** Costume rendering is strong enough to enjoy, but the 03 hooks and rear 06 shoe shapes are visible without magnification. The two front diagonals are easier to parse than the rear pair.
- **Nearest 2×:** Confirms that the problem areas are in the supplied contours and alpha, rather than an effect of game-scale reduction. It also makes the good face, glove and shoulder rendering clear.
- **0.66:** Identity survives well. Fine texture is reduced; legs become roughly small boot masses. The worst connections do not become convincing through reduction: the 03 branch can read as a dangling line, and rear 06 as a sideways spur. The game's precise pixel phase could alter small holes, but it would not repair the broader silhouette.
- **Light:** Strongest diagnostic for low-alpha gaps and skinny connecting strips.
- **Dark:** Hair, dark trousers and boot interiors lose separation. Gold shoulders and front facial highlights remain effective. Some defects are masked by low contrast, while branch tracking becomes harder overall.
- **Ground:** Good overall identity separation, but boots and small gaps still need deliberate silhouettes. This was a flat green field, not a test against detailed ground tiles or effects.

The diagonal heads, shoulder layout and tunic provide plausible static neighbors to their cardinal directions. The front diagonals visibly face toward the lower left/right, and the rear pair expose the back with a small side-face sliver. I did not see an identity change large enough to compete with the leg defects. Transition phase alignment, live turns and translation remain untested.

## Repair order and evidence files

1. Redraw the bad branch in all four 03 keys.
2. Rebuild rear-facing 05–06 calf/boot connections, then reconcile 06→07.
3. Clean the surrounding 02–06 cuff/hem shapes and intentional occlusion. Retain the sound upper body and character identity.
4. Test exact timing in continuous playback on moving ground at intended size. Validate contact and speed there before changing timing.

`diagnostics/*-native-three-backgrounds.png`, `*-2x-three-backgrounds.png` and `*-066-three-backgrounds.png` contain every chronological key and repeated 00 wrap. `*-lower-body-4x.png` provides diagnostic crops, and `priority-defect-coordinate-sheet.png` gives source-coordinate rulers for the largest defects. `cardinal-context-native.png` is identity/turn context only. These are deterministic composites of supplied art, not generated replacement art. `input-verification.json` records all input hashes. `pair-difference-metrics.json` is an auxiliary numerical comparison only; pixel difference magnitude does not measure animation quality. `review.json` records the review in structured form. `SHA256SUMS` freezes all output file contents other than the checksum manifest itself.

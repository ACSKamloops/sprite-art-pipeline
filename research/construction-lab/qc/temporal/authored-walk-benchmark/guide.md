# Authored walk benchmark: drawing before coverage

This guide supports a new original right-facing pilot. It approves no current artwork. The rejected V2 and guided-walk receipts remain unchanged. A complete exporter, coherent rig, or longer frame list does not establish convincing movement.

## Primary artist references

| Artist/source | Verified article date | Useful benchmark | Scope/rights |
|---|---|---|---|
| [Raymond Schlitter, Human Walk Cycle](https://www.slynyrd.com/blog/2024/5/24/pixelblog-50-human-walk-cycle) | May 29, 2024 (visible article date; URL differs) | Video-selected keys, colored anatomy dummy, distinct contact/down/pass/swing poses; controlled clothing folds | Side-view human example. Public tutorial is reference, not permission to incorporate its sprites; downloadable assets/source are offered through Patreon/shop. |
| [Manning Krull, Walking animation for low-res sprites](https://manningkrull.com/__pixel-art/walking.php) | No publication date established | Eight-frame foot path, heel-to-toe rolling, stable near/far shading and opposite arm swing | Small pixel-sprite example; page explicitly reserves all rights. |
| [Raymond Schlitter, Top Down Character Animation](https://www.slynyrd.com/blog/2025/3/24/pixelblog-55-top-down-character-animation) | March 31, 2025 (visible article date; URL differs) | Synchronized directional comparisons, consistent appendage proportions and deliberately variable bounce | Three-quarter RPG projection, not a literal side walk or universal motion formula. |

I viewed Schlitter's displayed dummy sheet (all eight static keys), Krull's eight actual GIF frames at native size and nearest-neighbor 4×, and all six locally extracted Randi right-walk poses. I did not view continuous timed browser playback of these references. Reference files are private/ignored; no artist/game pixels are committed as new artwork.

## Proposed eight-key pilot contract (our adaptation)

This is a starting pose plan, not a timing prescription copied from a tutorial. Fix camera, canvas, scale and ground. Name **near leg A / far leg B** in every drawing. Start with flat distinguishable limb colors before costume rendering.

| Key | Readable body action | Foot/limb test |
|---|---|---|
| 0: A contact | A heel reaches ahead; B finishes behind; torso bridges the stance | A forward, B rear; opposite arm leads. |
| 1: A loading/down | Pelvis settles over A, knee accepts weight | A becomes planted; B heel lifts/toe leaves. |
| 2: B passing | Body rises over supporting A | B bent knee/foot passes under body without becoming a second planted foot. |
| 3: B late swing/up | B extends toward its next landing | A rolls toward toe-off; B remains airborne. |
| 4: B contact | Same character/body mass, reversed limb roles | B forward, A rear; do not duplicate key0's limb identity. |
| 5: B loading/down | Second weight acceptance has the same intended rhythm | B planted; A lifts. |
| 6: A passing | Supporting B carries pelvis | A visibly bent/lifted; compare body volume with key2. |
| 7: A late swing/up | A approaches key0 contact | B toe-off; key7→0 must continue foot/arm trajectories. |

“Up” and “passing” vary with gait and stylization: the artist's Human Walk example places its maximum height at passing. Do not force every gait into a sine wave or a predetermined bob amplitude. Check chosen motion against a real reference, then draw intentional stylization. A fixed in-place stance foot travels backward in image space; in moving-world playback it should remain planted during support. Constant alpha-bounding-box bottoms are not a substitute for identifying that foot.

## Strict review gates

1. **Design at native size:** head, torso, boots and gloves have intentional readable masses. No tiny generic boot attached to a tube limb. A silhouette identifies the same character without material highlights.
2. **Weight:** contact, compression, passing and push differ visibly. The pelvis responds to support; upper body does not merely hover above oscillating knees. Grounded feet share the declared ground plane in both half-cycles.
3. **Alternation:** follow A continuously around the cycle; shading, overlap and knee identity do not swap arbitrarily. The same test applies to arms; held equipment permits a deliberately constrained arm, not broken grip.
4. **Volume and drawing:** joint bends preserve plausible thickness; head/hood/boot sizes do not change to fit a pose. Foreshortening is drawn, not simulated by stretching a flat part. Compare corresponding keys0/4,1/5,2/6,3/7 without independently recentering them.
5. **Material:** cloth follows the body with an authored lag, coherent fold anchors and restrained secondary motion. Scarf silhouette does not disappear in one passing key and balloon in its counterpart without a reason.
6. **Motion at actual clock:** review a native-size continuous loop and a moving-world version with the exact hold schedule. Judge cadence, weight and appeal, then examine every adjacent pair and wrap. Successful pixels/IK/timing checks are engineering evidence only.
7. **Expansion:** approve the single right-view pilot first. New front/back drawings need their own synchronized pose and turnaround review; side-view success cannot approve depth attacks or all equipment states.

## Separate private game control

Existing Randi right walk uses generic indices **251,252,35,254,253,34**, each **five video frames**, at 60.098811862348406 Hz: approximately 0.499178 seconds per cycle. The local movement trace contains a complete right-input cycle at ticks12320–12349 with these six five-tick holds. The extracted GIF's centisecond holds are 80/90/80/80/90/80 ms: rounded preview timing, not the exact engine clock.

Visible reference strengths: a compact head/hair mass remains recognizable, arms separate from the torso, trousers change silhouette through bent passing legs, and alternating poses are drawn instead of only rotating identical rigid pieces. These are qualitative observations, not measured native anatomy/ground/collision claims. It is a stylized three-quarter RPG character, not the anatomy target for Copper Scout. Do not copy ROM pixels into the authored pilot, infer hit windows from poses, or treat its six-frame cycle as the mandatory cadence for every character.

The JSON receipt binds downloaded reference bytes, private local inputs and the selected trace records. It does not certify rights, production artwork, continuous reference playback, or newly authored output.

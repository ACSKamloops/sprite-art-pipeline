# Frozen cold review: Rowan and Lyra diagonal walks

**Scoped overall judgment: 7.0/10.** Both characters are recognizable, cohesive and useful for a prototype. The rear diagonals communicate an alternating bent-leg gesture more clearly. The front diagonals have visible local join defects, and Lyra's second knee-lift cue is not clear enough for confident left/right gait verification. I would repair those drawings before calling the set finished.

This is an art and still-sequence review of exactly the eight nominated diagonal loops. Cardinal walks and idles are context for identity and view changes only; they are not separately accepted or rated. No target score was supplied and no score was awarded for the number of keys, export success or source math.

## Independence and binding

Only the case-free blind review card, `input-v1/INPUTS.json`, its 144 listed PNGs, and `rowan-reference.png` / `lyra-reference.png` were read. No producer reports, INTAKE, previous scores, case history, source mapping or other project artifacts were opened. No accidental exposure occurred. No generation/model API calls or canonical edits were made. All derived views and this report are inside `review-v1`.

Input ledger SHA-256: `9a0441e633a82894e19bad2c836f273e2548a1e73da53413016e51cc7fe52985`. Rowan reference: `ca7a427f9decb2c6fa880ae1772fe37233a53d1c6d8ab13387c6f619a8358512`. Lyra reference: `abd01511ed76cd6d807925fc26215692c78e391b44e93b983005aa527d6e0736`. All 144 ledger image hashes matched. `input-verification.json`, `INPUT-SHA256SUMS`, and `review.json` retain all source fingerprints. `SHA256SUMS` binds the frozen review files and contact sheets.

## Scores

Scores are 0–10 judgments of the visible work. Appearance covers drawing, material, volume, anatomy and edges; identity covers consistency with the supplied references and neighboring views; motion covers the reconstructed pose progression and readability; usefulness covers practical deployment at the supplied scale, including visible turn concerns. Approximate uncertainty is ±0.5 for appearance/identity and ±1 for motion/usefulness. Small differences should not be read as precise measurements.

| Walk | Appearance | Identity | Motion | Usefulness |
|---|---:|---:|---:|---:|
| Rowan southeast | 7.0 | 8.5 | 6.0 | 6.5 |
| Rowan northeast | 7.5 | 8.5 | 6.5 | 7.0 |
| Rowan southwest | 7.0 | 8.5 | 6.0 | 6.5 |
| Rowan northwest | 7.5 | 8.5 | 6.5 | 7.0 |
| Lyra southeast | 7.0 | 9.0 | 5.5 | 6.0 |
| Lyra northeast | 7.5 | 9.0 | 6.5 | 7.0 |
| Lyra southwest | 7.0 | 9.0 | 5.5 | 6.0 |
| Lyra northwest | 7.5 | 9.0 | 6.5 | 7.0 |
| Scoped set | 7.3 | 8.8 | 6.1 | 6.6 |

Hair, faces, shoulder pieces, belts, gloves and boots preserve each actor's identity well. Rowan's copper hair, blue/gold tunic, silver armor and pale trousers remain distinct. Lyra's silver hair, green/gold costume and teal scarf remain distinct. The materials keep useful separation at 0.66, although Lyra's dark trousers and boots merge on the dark background. There is no demonstrated actor-identity collapse or framing cut-off. Torso rotation and compressed passing poses affect gait clarity more than character recognition.

## Coverage and timing

Reviewed 64 diagonal poses; all 64 cyclic predecessor/current pairs, including eight wraps; 128 same-phase diagonal/cardinal neighbor pairs; 64 cardinal walk poses and 16 cardinal idle poses for context; and both supplied reference strips. Every diagonal key was inspected full-stage at native 128×128, nearest-neighbor 2×, and 0.66 game scale (rounded to 84×84 stage), on light `#e5e2d5`, dark `#1b222b` and ground `#5c6743` backgrounds. The ground cue uses a horizontal pivot line at native y112 and subtle horizontal lines; it is not a physical floor measurement.

Every cyclic pair was also explicitly placed side-by-side at native scale, including 07→00. Whole-body turn triples were inspected at native and 0.66 on every background; torso/hip/leg/cuff turn regions were rechecked at 2× on every background. Full-body cardinal idles were checked at 2×. Selected diagnostic joint crops were checked at 4×; those crops do not determine the game-scale art score. The derived sheets preserve the nominated source pixels apart from nearest-neighbor display scaling and compositing.

The packet declares eight equal holds of 9/160 seconds (56.25 ms), 0.45 seconds total. Pose starts are 0, 0.05625, 0.1125, 0.16875, 0.225, 0.28125, 0.3375 and 0.39375 seconds. This is the supplied still chronology, not an independently decoded media timestamp stream.

**Perception limit:** motion judgments reconstruct chronology from stills and known holds. They do not certify human continuous normal-speed playback, controller feel, world-space speed, physical foot contact or toe slip. The same-phase turn comparisons do not prove how the controller selects phases.

## Visible leg progression

Left/right below comes from visible hip/branch attachment and the front/back view; the filename only identifies the nominated view. Screen-left/right is retained so that the evidence is independently locatable. A raised heel is not automatically a high raised knee. Hems and overlap legitimately hide parts of the legs, and a diagonal gait does not require mirrored silhouettes.

**rowan/southeast:** 02: screen-left hip/boot branch folds behind while screen-right leg stays long. 03-05: branches overlap and exchange the long silhouette. 06: screen-right pale knee visibly rises and its boot is tucked; screen-left leg is longer. This supports right-then-left alternation in this front view, with medium confidence through the occluded handoff.

**rowan/southwest:** 02: screen-right branch folds behind while screen-left is long. 03-05: narrow crossing handoff. 06: screen-left pale knee visibly rises with a tucked boot, opposite the longer screen-right branch. This supports left-then-right alternation in this front view, with medium confidence through the handoff.

**rowan/northeast:** 02: screen-left branch has a folded heel and the screen-right shin remains long. 03-05: narrow crossing. 06: screen-right heel folds behind and screen-left shin remains long. From this back view, the visible evidence supports left-then-right bent-leg alternation.

**rowan/northwest:** 02: screen-right heel folds and screen-left shin remains long. 03-05: narrow crossing. 06: screen-left heel folds and screen-right shin remains long. From this back view, the visible evidence supports right-then-left bent-leg alternation.

**lyra/southeast:** 02 has a visibly folded screen-left boot branch. 03-05 compress the inner legs under the tunic. 06 spreads the feet but does not make the opposite knee rise as distinctly as Rowan's; the shorter/higher boot silhouette is still screen-left. I cannot confidently verify a clean right-then-left knee lift from these pixels, although the intended alternating gesture is plausible.

**lyra/southwest:** 02 has a visibly folded screen-right boot branch. 03-05 obscure the handoff under the tunic. 06 spreads the feet but does not make the opposite knee rise distinctly; the shorter/higher boot silhouette is still screen-right. I cannot confidently verify a clean left-then-right knee lift from these pixels.

**lyra/northeast:** 02 folds the screen-left heel under the hem while screen-right stays long; 06 folds screen-right while screen-left stays long. Both branches visibly take a bent/raised-heel role. Back-view left-then-right alternation is readable, though the exact knee joint is hidden by dark trousers and hem.

**lyra/northwest:** 02 folds screen-right while screen-left stays long; 06 folds screen-left while screen-right stays long. Both branches visibly alternate the bent/raised-heel role. Back-view right-then-left alternation is readable; the knee joint itself is partially hidden.

The visible evidence supports an alternating gesture across both branches most strongly in the rear views and Rowan's pale-trouser front views. It does **not** justify a confident claim that Lyra SE/SW show equally clear opposite-knee lifts. It also does not prove a reversed limb assignment or detached rig: that would overstate what the pixels establish.

## Material findings and smallest next experiments

**D1 — visible drawing issue (medium; confidence high).** Narrow straight background-colored cutouts at forearm/cuff and thigh/boot joins, with thin edge extensions. Especially clear in 01 and 07; 03 and 05 compress the crossing legs into lumpy or pinched joins. Approximate source coordinates: SE 01 approximately x42-64,y78-93; reflected screen region in SW. Native 128-stage coordinates, approximate. Smallest next experiment: Redraw only those local cuff and trouser/boot joins in the existing poses; preserve timing and silhouette landmarks for the first comparison. Expected benefit: A continuous sleeve and thigh volume, fewer edge flashes, easier support/swing reading.

**D2 — visible drawing issue (medium; confidence high).** 03 has a thin brown horizontal spur beneath the near glove; 05 has conspicuous irregular notches and slivers around the lower-leg silhouette; 07 has a thin gray downward edge between the legs. These are more legible on light/ground backgrounds than dark. Approximate source coordinates: SE 03 approximately x46-59,y84-93; SE 05 x51-70,y91-110; SE 07 x61-68,y88-101. Approximate. Smallest next experiment: Clean only the spurs/notches and restore the intended black-trouser and brown-boot overlap in those keys. Expected benefit: Boots and thighs read as solid volumes rather than narrow remnants or fabric spikes.

**D3 — visible drawing issue (low to medium; confidence high).** Rear crossing poses are strongly occluded, which is legitimate, but Rowan 03 has a straight pale cut under the hem and Rowan 05 a cuff/hem notch. Lyra 05 has a long narrow brown diagonal crossing-leg shape against a small triangular inner gap. This is less disruptive than the front-diagonal issues; the Lyra shape is ambiguous rather than proven detached anatomy. Smallest next experiment: For Rowan, repair the local hem/cuff cuts. For Lyra, test a two-pixel clearer inner-leg separation in 05 without widening the whole stance. Expected benefit: Cleaner crossing pose and clearer distinction between a bent leg and a thin slash.

**M1 — readability concern; anatomical failure not established (medium; confidence medium).** 02 clearly shows one folded boot branch behind the body. In 06, the opposite trousered knee does not protrude upward as distinctly as Rowan's pale knee; the same screen-side boot remains the shorter/higher silhouette. Across 03-05, overlap and changing torso yaw obscure the branch handoff. This does not establish a wrong-leg rig; it limits the visible evidence for an equally clear second lift. Smallest next experiment: Make one isolated alternate-knee drawing test at 06, with the opposite thigh/knee visibly raised and the supporting shin continuous. Review 04-07 together before changing timing. Expected benefit: A visibly alternating step rather than two ambiguous folded-foot silhouettes.

**M2 — playback hypothesis (medium; confidence medium).** 07,00,01 retain a similar extended-leg configuration around the wrap; 03-04 remain narrow/crossed. Larger configuration changes occur at 01->02 and around 04->05->06. Uniform holds therefore distribute time unevenly across visual displacement. There is no exact-image frozen frame allegation. 07,00,01 occupy 168.75 ms across the wrap; 03,04 occupy 112.5 ms. Each displayed key holds 56.25 ms. Smallest next experiment: After drawing cleanup, play the unchanged loop continuously at 0.66 scale. If the wrap hesitates, compare one exposure-only variant that shortens the near-hold cluster and gives the fastest crossing a little more time. Expected benefit: Potentially steadier perceived cadence without adding frames.

**M3 — heading/readability observation (low to medium; confidence medium).** The torso and face swing between a more frontal and more profile-like three-quarter view within one directional loop. Hair/shoulder volumes stay recognizably the same character. The amount of yaw may make the gait feel swively, but continuous playback is needed to judge whether it exceeds the intended expressive walk. Smallest next experiment: Keep the head yaw and shoulder width within a slightly narrower range in a duplicate comparison, after fixing joins. Expected benefit: A steadier diagonal heading if playback confirms distracting swiveling.

**T1 — visible turn-pair mismatch; controller result unknown (medium; confidence medium-high).** At phase 04, east/west neighbors show a broad fore-aft boot spread while the diagonal is narrow and crossing. At phase 06, the diagonal shows separated bent/long leg branches while north/south neighbors are much more stacked. Identity/materials persist through the turn, but equal phase index does not supply an identical projected contact configuration. Smallest next experiment: Use a phase-locked in-engine turning test at keys 04 and 06, both directions, before deciding whether phase remapping or drawing adjustment is needed. Expected benefit: Evidence about any visible foot pop when changing heading.

**G1 — not verifiable from this packet (scope limit; confidence high).** The drawn soles change angle and apparent height, with compact or overlapping contact shapes in 03-05. No translating world path, floor constraint, collision state or controller timing was supplied. A static pivot line is only a registration aid. Smallest next experiment: Translate the sprites over a ground grid at the intended game speed with a visible contact marker, and assess toe slip at normal playback. Expected benefit: Separates true ground slip from an in-place pose change.

## Loop, stance and practical use

The stance remains recognizably the same compact character; there is no need to rebuild the head, armor, scarf or torso identity. Back views have credible folded-heel alternation despite narrow crossing poses. Front views would benefit most from solid thigh/boot/cuff joins and a legible alternate knee. The supplied cardinal neighbors retain compatible costume volumes, but they have different foot-spread silhouettes at some equal indices; an engine turn check is still needed.

There are no exact duplicate keys asserted here. The near-hold cluster around 07→00→01 is a possible cadence hitch, not a demonstrated continuous-playback freeze. Likewise, apparent in-place sole displacement is a toe-glide cue to test, not a proven world-space skating fault. The visible drawing defects are firmer findings than those motion hypotheses.

Priority: repair local joins with current timing; clarify Lyra's alternate knee in an isolated pose test; then assess unchanged 0.66 normal-speed loops, phase-locked heading changes and translated ground contact. Adjust exposure timing or reduce head yaw only if that playback confirms a distracting hesitation or swivel. More keys alone would not resolve a weak joint or unclear leg role.

This judgment transfers only to these exact fingerprints and declared timing. Other actors, changed art, changed holds, equipment, actions or controllers need their own scoped evidence.

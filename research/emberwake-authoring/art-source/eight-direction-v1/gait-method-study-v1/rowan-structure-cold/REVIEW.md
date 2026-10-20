# Frozen anonymous whole-walk art review

Frozen at 2026-10-17T04:17:29.382866+00:00, before unblinding. No accidental exposure occurred. I opened only the nominated review card, anonymous input packet, and my own derived review images. The permitted input ledger reveals identical A/C hashes in most phases; I did not open any producer mapping, report, history, grade, or art folder.

**Whole-cycle result: A and C are tied at this review's scoring resolution; B is materially weaker.** C has a small local drawing advantage in frame 07, but I cannot honestly turn that into a confident full-loop win. A/C are competent small-scale RPG art that still needs motion/context acceptance. B has a demonstrated ankle attachment fault that should be repaired before final use.

| Anonymous variant | Appearance | Anatomy / attachment | Materials | Temporal identity | Motion / readability | Game usefulness | Scoped overall |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 7.5 | 7.0 | 7.5 | 8.0 | 6.5 | 7.0 | **7.0** |
| B | 6.5 | 4.5 | 6.5 | 7.5 | 5.0 | 5.0 | **5.5** |
| C | 7.5 | 7.0 | 7.5 | 8.0 | 6.5 | 7.0 | **7.0** |

These rounded 0–10 scores apply to each fully inspected SE and SW clip, not to the character's entire animation set. Overall is a holistic judgment, not a mean. On this scale, 5 is promising work with major visible problems, 7 is competent usable game art needing polish, and 9 is excellent finished work. No points were awarded for frame count, export success, mechanical verification, or producer target scores. Drawing and identity uncertainty is approximately ±0.5; motion is ±1.0; practical/overall judgment is ±0.75. Confidence in the B gap finding is high; confidence in A/C rhythm and preference is lower.

## Binding and actual inspection

Input packet: `/home/astra/artifacts/emberwake-rowan-structural-review-v1/input`. `INPUTS.json` SHA-256: `1b81349b346bc8926b4250f8c3b2acb83b5322c134e62bbed9852125fa6df012`. All **79 image hashes** match the permitted ledger: 48 candidate cels plus 31 context images. Exact fingerprints are preserved in `frozen-input-ledger.json`, `verified-inputs.json`, and `REVIEW.json`.

I inspected A/B/C 00–07 in both southeast and southwest, plus every adjacent pair and 07→00 wrap. For each direction, all candidates were composited at an 84×84 game stage (rounded from 0.66×128), 128×128 native stage, and 256×256 nearest enlarged stage on light `#E8E1CF`, dark `#171C29`, and synthetic game-green `#4E5B3C`. The pivot is (64,112) on a 128×128 source stage. I additionally used lower-body crops at 4×/8× to locate faults, not as a substitute for game-scale judgment. All supplied appearance and cardinal images were used only to establish identity and turn context.

The declared timeline holds each pose for 9/160 s = 56.25 ms; starts are 0, 56.25, 112.5, 168.75, 225, 281.25, 337.5 and 393.75 ms, with wrap at 450 ms. This is the ledger timeline, not a verified browser or encoded-video timestamp trace. **Motion judgments reconstruct chronology from ordered stills, pair sheets and these holds. I do not claim continuous human normal-speed playback, controller feel, or physical contact verification.** The optional browser player was not used.

## Whole-art judgment

The copper hair silhouette, blue eyes, blue-and-gold tunic, silver pauldrons and brown leather kit make a coherent, appealing chibi RPG character. The upper-body armor has readable rounded volume and a material response distinct from cloth and leather. The head, hair and torso stay recognizably the same person without a conspicuous loop reset. These are meaningful drawing strengths, not just consistent file dimensions.

At the 84 px game stage the face direction, costume blocks and alternating legs still read. Fine gold trim, folds and texture compress into visual noise, but the character remains legible on all three grounds. Dark brown boots lose some internal modeling on the dark ground while their silhouette remains visible. I saw no obvious source-stage clipping or white matte fringe. The supplied cardinal context is compatible with the diagonal character identity; it does not certify turn transitions.

A and C generally preserve plausible compact hip–knee–boot chains, including heavily occluded rear-leg phases. I found no basis to demand a permanent inter-leg gap, two fully visible boots, or mirrored step silhouettes. Their gait is a brisk, high-kneed stylized action. The comparatively small 00→01 advance and larger subsequent contour changes may produce a dwell-then-hurry rhythm, but that is a playback hypothesis, not a demonstrated support failure. Without ground translation and a human playback check I would not call these final foot-contact or shipping animation acceptance.

B retains much of the attractive upper-body identity, but its lower-body drawing is weaker across several poses and visibly breaks at 06/07. A detailed head and armor do not cancel that structural failure. C's 07 makes the approaching leg's cream thigh-to-boot chain clearer than A's compact paired knee shapes. It also changes toe/shaft angle, so the incoming and outgoing pairs matter. This is a local advantage; A/C remain the same overall tier.

## Material findings and smallest experiments

1. **B: exposed background crosses both trouser-to-boot joins at 06 and 07.** This is visible in both directions and on all three backgrounds, strongest at 128/256 but still capable of reading as floating feet at 84. In `B/southeast/06.png`, the detached boots occupy x41–57/y90–107 and x69–81/y89–102. In `B/southeast/07.png`, they occupy x41–53/y89–101 and x66–86/y93–108. The corresponding SW boot boxes are x47–59/y89–102 and x71–87/y90–107 in 06, and x42–62/y93–108 and x75–87/y89–101 in 07. These are source pixels. At alpha ≥128, each affected image has the main body plus two separate boot components; the visible finding is the background stripe at the internal ankle, with no object in front of it. It is not a complaint about an occluded toe or missing permanent leg gap. The breaks enter at 05→06, persist at 06→07 and reconnect at 07→00. **Smallest repair:** redraw the cuff/ankle bridge and adjacent shin shading in 06/07 while preserving foot placement, upper body and timing; compare 05→06→07→00 again at 84. Expected benefit: continuous leg volume and removal of floating-foot flicker.

2. **B: folded boot volume becomes a narrow hook/stem.** Inspect `B/southeast/02.png` around x49–64/y84–101 and SW02 around x64–79/y84–101, then 01→02→03. The rear boot is much thinner than neighboring poses; 04/05 repeat a narrow drop under the lifted cream knee. This is a drawing/volume weakness, not a proven full disconnection in 02, and perspective may account for part of it. A/C retain a fuller rounded boot/cuff at these phases. **Smallest repair:** after the confirmed gaps are fixed, try one 02 redraw clarifying the cuff-to-shin turn and foreshortened leather volume, then compare the three-pose sequence. Expected benefit: a solid boot instead of a movable brown fragment.

3. **A/C: unequal apparent pose progression needs playback before repainting.** The forward-foot silhouette changes modestly at 00→01, whereas 04→05 changes toe angle, knee bend and leg contour more strongly; all are held equally. This may produce a perceived hitch, but I cannot establish it from still chronology alone. **Smallest experiment:** a human comparison of the present loop against a small timing redistribution around the existing poses, at the same total duration. Adjust a lower-leg drawing only if the hitch survives. Expected benefit: test smoother stride progression without replacing successful art. This is not a claim that any particular foot must remain grounded.

4. **A versus C: local final-pose construction.** Inspect 06→07→00 in both directions, especially SE x58–85/y78–110 and SW x43–70/y78–110. C gives the forward leg a clearer diagonal cream thigh leading into the boot; A keeps both cream knee shapes compact. C also lengthens/turns the boot. The improvement is modest at 84 and does not fix other shared phases. **Smallest experiment:** retain C as the candidate and use human full-loop playback to select between A/C; this review alone does not justify more pixel changes.

## Every pair, including wrap

The following observations apply to the actual SE pairs and were separately checked in the SW pairs; no additional SW-only defect changed the scores.

| Pair | A / C | B |
|---|---|---|
| 00->01 | Front boot stays near the same extended silhouette while the torso/arms change subtly; leg phase is readable but this part advances less than the later poses. | Comparable restrained first transition; no separate boot island observed here. |
| 01->02 | Extended boot narrows and returns toward the body while the rear boot remains tucked; attachment remains plausible. | Rear boot becomes an unusually thin angled sliver; weaker calf/boot volume, though not a demonstrated full disconnect at the alpha threshold used. |
| 02->03 | Tucked leg comes down into a near-passing two-boot pose; no demonstrated leg-role reversal. | Thin rear boot changes into a fuller downward boot; visible volume step is stronger than in A/C. |
| 03->04 | Opposite foot extends and the other knee folds back; clear exchange of leg roles. | Leg roles still read, but the lifted boot is reduced to a narrow stem under the cream knee. |
| 04->05 | Front boot changes to a more diagonal angle and the knees bend; strongest contour/volume change of this half. Treat the impression of a hitch as a playback hypothesis. | Very little lower-body advance relative to the larger 05->06 change, giving unequal apparent progress under equal holds. |
| 05->06 | Knees compress/rise and the body bobs upward; connected forms retain the same costume. Without ground and root movement this does not prove an aerial or support failure. | Both boots become distinct floating islands below their trouser forms; demonstrated joint break. |
| 06->07 | A returns to two compact thigh shapes; C instead gives the forward leg a longer diagonal cream form and a more continuous shaft. C is locally clearer, with a changed toe/shaft angle. | Boot islands persist and relocate; exposed background bands create a disconnected lower-body flicker. |
| 07->00 | A expands a short cream thigh into the forward step; C already prepares that extension, but changes boot angle on the wrap. Neither has a demonstrated identity reset. Whole-cycle C advantage remains modest. | The detached boots reconnect on 00 while the forward boot extends; the structural discontinuity crosses the wrap. |

## Practical scope

A/C are usable for a small-scale RPG prototype and plausible near-final walk candidates, with competent drawing and unresolved playback/context acceptance. They are not exceptional finished animation on the evidence available. B should remain a comparison candidate until its explicit ankle breaks are fixed. The visible result supports A/C over B; it does not support a confident A-versus-C overall winner.

This review certifies no other directions, equipment, actions, transitions, collision, physical foot contact, root-motion speed, live game background, or human playback preference. Changed art or timing requires a new scoped review. All source files were left untouched. `REVIEW.json` carries the exact input ledger, full scope, scores, pair coverage, issues and uncertainty. Review sheets and diagnostic crops are in this review's own folder.

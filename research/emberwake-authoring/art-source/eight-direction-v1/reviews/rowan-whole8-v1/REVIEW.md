# Anonymous diagonal-walk review 11

Frozen 2026-10-17T06:17:10+00:00. **Moderate preference: B.** Both are useful detailed modern RPG sprites; B better preserves the supplied idle's proportions/materials and has a clearer later leg sequence. A remains attractive and readable. Scores are judgments with overlapping uncertainty, not acceptance certificates.

| Candidate | Drawing | Character identity | Motion readability* | Game-size use | Overall |
|---|---:|---:|---:|---:|---:|
| A | 8.0 | 7.5 | 6.8 | 7.7 | 7.4 |
| B | 8.0 | 8.9 | 7.5 | 8.0 | 8.0 |

Approximate uncertainty: ±0.5 drawing/identity/use, ±0.9 motion, ±0.6 overall.

*Tools expose stills. All motion, weight and wrap statements reconstruct ordered still chronology, not continuous human normal-speed perception. No video watching, controller test or physical foot-contact validation occurred. INPUTS declares eight equal 9/160 s (56.25 ms) slots, starts 0, 56.25, 112.5, 168.75, 225, 281.25, 337.5, 393.75 ms; wrap at 450 ms. No animation file is supplied, so there are no independently decoded presentation timestamps.*

## Findings and decisive witnesses

- **Both:** Hair/face, navy/gold tunic, silver armor, ivory trousers and brown leather stay recognizable through both directions. Shoulder/forearm attachment and two-leg structure remain plausible. Arm opposition and alternating extension/tucking support a walking interpretation. All pairs, including 07→00, offer a plausible continuation without a demonstrated texture reset or gross anatomical break. Wrap smoothness and convincing weight at speed remain untested. Modern shading and RGBA softness suit the brief; no palette-purity penalty applies.
- **A: identity/proportion difference, observed.** [Identity witness](witness-identity.png) compares both 00s against matching diagonal idle on the same 128 stage, enlarged nearest to 256. A has longer/larger legs and boots and cleaner/lighter armor treatment. Its alpha bounds reach y122–124 versus idle y112; B is closer to idle scale/treatment. This is not proof of sliding: no world displacement is supplied. Benefit: closer idle/walk continuity. Smallest experiment: human-view idle→A00/A04 at the declared pivot; adjust lower-body proportions only if the difference causes a visible pop.
- **A: passing-leg readability bottleneck, observed.** [02→03→04 witness](witness-A-passing-wrap.png), native region x45–83/y78–112 in both directions: at 03 the ivory thighs become a broad crossed shape and the rear boot narrows to a brown sliver behind the support boot. At 84 this weakens the leg-role handoff relative to B03. The rear boot is source-visible; this is occlusion/readability, not an absent limb or proven broken joint. Benefit: clearer support/swing roles. Smallest experiment: a small crease or rear-boot silhouette clarification in 03, checked at 84 on all grounds.
- **Both, stronger in A: uneven pose progression, observed; cadence effect hypothetical.** [Near-hold witness](witness-near-holds.png): A00/01 and A04/05 retain nearly the same leg silhouette despite small changes; SW behaves similarly. B00/01 also changes little, but subsequent knees/feet differentiate more. Equal holds make this uneven spatial progression worth checking; I cannot claim a perceptible hitch or stutter from stills. Benefit: a deliberate cadence if a problem is confirmed. Smallest experiment: human-view both unchanged 450 ms loops at 84, then test exposure redistribution before commissioning new drawings.

[B passing/wrap witness](witness-B-passing-wrap.png) shows the visible alternating knee/boot progression through 03–07→00. Its higher knee at 06 is traceable to a bent leg, not a missing or detached lower limb. I found no additional material anatomy defect to allege.

At 84, both retain direction, hair silhouette, armor highlights and leg action across game/light/dark grounds. A's larger shapes read strongly but diverge more from context and leave less bottom margin; no clipping is visible. B's detail is denser at this scale, yet its silhouette and costume remain usable. No transition animation is certified.

## Coverage and integrity

Read RUBRIC.md, STYLE.txt and INPUTS.json; all **143** SHA256SUMS entries verified. Inspected all eight ordered frames of A/B × SE/SW and every adjacent pair including 07→00 at **84 and 128 on game, light and dark grounds**, using supplied pair sheets. Selective nearest 256 inspection covered all four ordered sheets plus the decisive identity, passing/wrap and near-hold witnesses. Inspected appearance, all supplied idles and east/south/west walk context. Context establishes identity/camera only. No producer/source mapping, prior reports, parent folders or memory were inspected; no accidental exposure, source edits, model generation, engine work or external communication occurred.

Input binding: SHA256SUMS `4d99f6fb67d0c26dc7e9d944187120ba8b3520e11462a16da5d9b2a1230bd1c0`; INPUTS.json `a1df9c3107c2bafead56deac396829b5c9a799db4eb872f5b9e3fa5f8040d663`. Full metadata is in REVIEW.json. Output fingerprints are in SHA256SUMS. This review covers only these drawings and this declared timing; changed art/timing needs a new review.

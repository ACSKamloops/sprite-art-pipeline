# Assembled-v6 independent art review

**Changes requested — 7.955/10, below the 9/10 gate.** No category minimum or critical-failure requirement has been relaxed. Frozen manifest: `96fed23f2f1e75373363c1db923b9b8031bb5f701c206c28f5e43e15dd0e2207`.

| Art match | Anatomy | Joints | Pixel craft | Cyclic weight | Gear attachment | Game usability |
| --- | --- | --- | --- | --- | --- | --- |
| 9.0 | 7.1 | 7.8 | 7.7 | 7.5 | 8.8 | 7.7 |

I checked all 72 source PNG hashes and viewed all poses on fixed native-size sheets, comparing consecutive poses and the 71→0 wrap. An isolated actual Chromium session captured 40 chronological native player screenshots, twenty with shared contact compensation and twenty without. Each mode spans more than two cycles. I viewed all captured native canvases in chronological sheets, selected complete gameplay views and a paused nearest2× presentation. Before/after state is retained because a screenshot can cross a pose boundary. This is selected chronology review, not a claim of continuously watched video.

This is a substantial improvement over assembled-v1: recognisable Captain identity, readable armour/ornament hierarchy, more continuous leg motion, meaningful variation in the pelvis and upper attachments, and no obvious large loop-reset discontinuity. Sword and shield remain visually coherent with their carriers in the reviewed sequence. Those strengths do not resolve the lower-body design problems.

## Two blocking repairs

1. **Rebuild the near boot's forefoot and ankle volume.** The image-right boot repeatedly reads as a high red cuff with an open dark oval and a tiny curled toe. It lacks the broad armoured toe, instep, heel and grounded mass of the approved boot. Frames12–35 and48–59 expose the problem especially clearly. Gold/red contour noise around that small foot is also weaker than the source's clean plate volumes. Repair its complete perspective and silhouette throughout the cycle, rather than extending a few toe pixels or shrinking it to satisfy the ground.
2. **Strengthen support-to-passing weight poses.** Compare0/36 contacts and18/54 passing poses as full bodies. The legs do narrow, but the mass transfer is not clear enough: the Captain often reads as a combat-ready body rocking over small knee/ankle changes. The planted leg should visibly support the pelvic mass, while the other knee/foot has purposeful clearance and a distinct passing silhouette. Keep gear identity, but let the pelvis/torso respond to support instead of relying on dense interpolation to sell the step.

Shared compensation moves the complete actor and was evaluated as presentation, not mistaken for IK correctness. The raw and compensated player states are captured separately. I did not independently calculate rendered sole drift, so the numerical contact gate remains open; a captured guide dot alone cannot close it. No apparent clipping in the reviewed native gameplay views does not establish every presentation context.

The 72 frames are distinct and the cycle is1.2seconds, but these facts earn no visual-quality credit on their own. The older twelve-frame Godot proof remains historical and has not been applied to this pack. Current screenshot/state evidence is at `/home/astra/artifacts/captain-second-review-v6/chronology/`; its hashes and player/source bindings are recorded in the JSON. I am ready for another frozen sequence after these two repairs, without pressure to approve it.

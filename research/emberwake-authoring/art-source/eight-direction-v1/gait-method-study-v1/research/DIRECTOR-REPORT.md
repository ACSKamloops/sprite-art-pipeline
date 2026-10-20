# Frozen director proposal: current walks and Rowan southeast motion guide

This is an animation design aid. It is not finished sprite art, a final quality review, or a claim that the proposed cycle plays better. No numeric rating is assigned. The current banks remain unchanged.

## What was inspected

All eight actual walk cels in each of these six v11 banks were viewed in bounded contact sheets at native128, nominal game84 and enlarged256 pixels: Rowan SE/NE, Lyra SE/NE, Brann SE/NE. Inputs are exactly `/home/astra/artifacts/emberwake-source-cel-game-preview-v11/bake/{rowan,lyra,brann}/{southeast,northeast}/00..07.png`.

Canonical repository manifests and baked manifests agree on eight equal `9/160s` holds, total `9/20s = 0.45s`. The sheets label every phase time. This tool session exposed static chronology, not visibly observed moving playback; conclusions below concern pose sequence and projected volume. No browser, Godot, controller contact, or live animation acceptance is claimed. 84 is a nominal inspection scale; the manifest draw scale0.66 yields a84.48px canvas before engine rasterization. No historical grades, producer reports, local models, or generation providers informed this pass. No outside reference was necessary to identify the painted sequence issues.

## Structural observations and repair direction

Visible occlusion does not establish anatomical left/right ownership. A narrowed or merged silhouette is described as such; it is not proof of a missing limb.

| Current bank | First structural issue seen in paint | Second structural issue and practical direction |
|---|---|---|
| Rowan SE | The head, tunic and shoulder arrangement remain close to the same upright key while the lower silhouette changes substantially. The leg change at03→04 has a much stronger visual event than the torso's transfer onto that foot. | The second half exposes the opposite white thigh and long boot, so this is not evidence of a wholly absent opposite key. But00/01, the compact03 pose, the long04 boot and the raised06 thigh do not carry equally clear heel-down / loaded / passing / reach roles. Author the complete two-leg path and body phase, then paint complete cels around it. |
| Rowan NE | At03–05 the lower silhouette becomes a narrow, overlapping central boot/cream-cloth column. The wide00/07 arrangement and this central group make the two halves read with different spacing. | The back and head stay almost the same presentation through that large lower change. Make the support-side pelvis/hem shift visible and preserve the inner cuff/boot separation through the overlap; do not infer hidden knees from the cream patches. |
| Lyra SE | The teal coat, face and glove arrangement have a much quieter phase change than the boot pattern. This remains easy to see at84. |00–03 keep the screen-right boot as the strong low silhouette, while the small screen-left boot changes less clearly;04–06 then present the other low leg. A more explicit tucked swing-foot arc and a pelvis/coat response would connect these half-cycles. Preserve the whole charcoal trouser-to-boot volume rather than repairing toe pixels alone. |
| Lyra NE |00/01 and07 have a broad two-boot arrangement, whereas02–06 spend much of the sequence with one long central low boot and the other partly hidden by coat/leg overlap. The second contact is less distinct as a silhouette than the first. | The coat back and scarf presentation are quiet relative to those changes. Give the opposite contact a deliberate support/hem displacement and make the passing foot visible only where the projection permits. Hidden parts need authored paint; a hole or forced V gap in every pose is not required. |
| Brann SE | The low-foot arrangement changes from broad00/01 to compact03–06, with the second contact04 less openly separated than00. This weakens the equal alternating-beat story under his broad torso. | The arm span already varies visibly, more than Rowan/Lyra; it should be coordinated with the support side rather than simply increased. Use the heavy belt/pelvis to establish which foot receives weight, retaining full broad boots during the overlap. |
| Brann NE | The lower silhouette is broad at00/07, compresses around03, and changes through several overlapping boot arrangements in04–06. The two contact halves have noticeably different projected spread. | The broad gold arm/shoulder outline also changes width, especially at03, without an equally explicit pelvis transfer in the painted silhouette. Unify the torso/arm counterphase and leg ownership before fine boot contours. This is not a claim that the view or anatomy is wrong behind the overlap. |

Across all six, the next useful test is a small number of deliberately different whole poses: contact, loading, passing, reach, then the true opposite equivalents. A repeated torso can preserve identity yet leave the legs looking attached to a quiet display pose. Small distal edits cannot create the missing body/weight relation.

## Rowan SE guide contract

`ROWAN-SE-POSE-BLUEPRINT.json` is the renderer-ready source. `ROWAN-SE-COORDINATES.csv` exposes every leg landmark. `guide/00..07.png` are transparent, filled construction-volume rasters. These are deliberately plain and are not candidate game sprites. The head and central tunic paint come from source00; shoulders, arms, gloves, cream thighs and brown boots are construction volumes. `ROWAN-SE-SOURCE-GUIDE-{84,128,256}.png` show current paint, guide, and transparent cyan-source/rose-guide silhouettes in the same native coordinates.

Origin is top-left, x right/y down, cell128×128, render pivot(64,112). A is the screen-right elongated white-thigh/boot chain in source00; B is its screen-left tucked chain. These are durable source-visible labels, not anatomical assertions.

Measured source00 alpha bounds are(35,16)–(91,112). The painted head band y16..54 has bounds x37..90. Approximate visual landmarks are neck(67,56), belt(64,75), and hip origins in the clothing band x52..74/y78..83. Cream thigh widths are about10–15px; the long boot shaft is about11px wide, and its complete projected foot/sole occupies about19px. Only band alpha bounds are measured pixel facts. Hidden joints, precise pivots and guide paths are authored assumptions.

The full8-phase proposal uses the same pattern for both legs, offset4 phases and shifted into their projected lanes. Forward boots are complete cuff/shaft/heel/toe volumes. Cuff and sole rotate together; they are not independent little patches. The two passing/reach overlaps can be legitimate in this view: final paint must preserve an internal cuff/boot seam and consistent overlap order so the matte does not become one brown block. Do not copy frame00 into07.

| Frame / start | Role | Pelvis | A: hip / knee / cuff / heel / toe | B: hip / knee / cuff / heel / toe |
|---|---|---|---|---|
|00 /0ms | A contact; B trailing |64,80 |70,80 /71,87 /71,92 /67,107 /80,110 |55,79 /51,85 /47,89 /43,95 /51,98 |
|01 /56.25ms | A loading; B toe-off |65,81.5 |71,81.5 /70,89 /68.5,95 /65,105 /78,108 |56,80.5 /51,87 /47,90 /44,94 /52,96 |
|02 /112.5ms | A support; B passing |64,79.5 |70,79.5 /68,88 /66,93 /62,102 /75,105 |55,78.5 /58,86 /53,89 /49,91 /57,94 |
|03 /168.75ms | A heel-rise; B reach |63,78.5 |69,78.5 /66,87 /63,91 /59,99 /72,102 |54,77.5 /61,85 /58,91 /54,99 /65,102 |
|04 /225ms | B contact; A trailing |63,80 |69,80 /67,85 /63,89 /59,95 /67,98 |54,79 /57,88 /57,94 /53,108 /66,111 |
|05 /281.25ms | B loading; A toe-off |62.5,81.5 |68.5,81.5 /66,87 /63,90 /60,94 /68,96 |53.5,80.5 /55,90 /54.5,96 /50,106 /63,109 |
|06 /337.5ms | B support; A passing |63,79.5 |69,79.5 /72,86 /68,89 /64,91 /72,94 |54,78.5 /53,88 /52,93 /47,103 /60,106 |
|07 /393.75ms | B heel-rise; A reach |64,78.5 |70,78.5 /76,85 /74,91 /70,100 /81,103 |55,77.5 /51,87 /49,91 /44,100 /57,103 |

Pelvis loads downward at01/05, rises through02/06 into03/07, then receives the opposite contact. Its horizontal2.5px range is toward each supporting side. Neck/head motion follows75% of the vertical displacement and65% of horizontal displacement, keeping the head visually calmer than the pelvis. JSON provides all native anchors. Head yaw stays fixed; the drawing needs no arbitrary new face direction.

The shoulder line counterphases the hips. A's glove center progresses(84,73),(85,75),(84,77),(83,79),(83,81),(82.5,82),(83,78),(84,75); B progresses(43,82),(44,82.5),(43,78),(42,75),(42,73),(41.5,75),(42,78),(43,81). Thus the arm opposite the forward leg has the lower/forward glove. Elbows and shoulder anchors are explicit in JSON. The guide renderer uses simple volumes rather than a textured torso twist; final paint would have to express the proposed shallow countertwist in the tunic/pauldron overlaps.

07→00 lowers A's reaching foot into its full contact while B leaves its trailing toe.03→04 is the opposite event. Both must be judged as part of the0.45s loop. They cannot be solved by replacing the last frame with a duplicate first frame.

## Compatible parts and new paint

Reuse the source head/face/hair, navy-and-gold tunic design, silver pauldron finish, glove design, cream cloth palette, and complete boot material. Preserve the fixed canvas/pivot and the measured short-limbed proportions. Whole source boots are useful appearance references and may be reusable near matching contact angles; a hidden heel or reversed boot side is not present merely because a cropped part can be rotated.

New paint is required for the altered thigh folds and hip/hem overlaps; the bent passing leg; the newly exposed side/back of the swing boot; a continuous cuff/shaft/heel/toe silhouette at changed pitch; and the small arm/pauldron side planes made visible by counterphase. These are complete pose-specific volumes. The source00 painted torso/head in the guide do not prove that all those planes can be supplied by cutout transforms. A/B shaded mattes are construction cues, not a proposed costume recolor.

## What to test next

1. Paint all8 Rowan SE guide phases as a single coordinated experiment, including both opposite contacts, both passing keys and the wrap. Preserve source appearance; test source versus painted experiment at the same0.45s clock and same scale. The important comparison is readability of weight/leg progression, not pixel similarity to the matte.
2. Inspect00→01 loading and04→05 loading for an actual support response;02/06 for a raised full swing boot;03→04 and07→00 for foot lowering and preserved volume. A successful one-frame contact does not establish the cycle.
3. Keep the equal8-pose0.45s control first. If the body/leg story becomes clear but the changes still snap, author actual intermediate cels at16 equal9/320s holds with the same0.45s total. Do not manufacture them by cross-fading toes. If the intended character is a calmer walk, separately test a0.60s total only after the motion design is readable; this changes cadence and must be compared as a separate variable.

The current0.45s cycle contains two contact beats, or4.44 beats per second. The guide's compact stance path is a visual in-place proposal, not a physical foot-lock contract. Read-only `hero.gd` currently sets `MOVE_SPEED=158.0` and manifest draw_scale=0.66. At that speed, a diagonal actor travels about9.52 native pixels per axis during one9/160s hold; this proposed stance heel path retreats about2–3 native pixels per axis per pose. The root's existing world-contact policy must reconcile that mismatch. Do not claim fixed-ground acceptance from these joint targets or from a source/guide silhouette overlay.

## Reproduction and frozen files

Run `python3 build_guide.py` inside this folder to regenerate the guide JSON, transparent guide rasters, comparison sheets and paths from the read-only source00 input. The CSV is an exported view of the JSON. Review inputs and clock observations are retained locally. No source or repository file was edited. `SHA256SUMS` binds this frozen director package; it is an identity receipt, not an art grade.

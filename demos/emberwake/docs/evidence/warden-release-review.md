# Warden rear release: frozen art review

**ACCEPT the candidate as a rear-view weapon-attack release between the nominated windup and neutral.** It is a useful improvement over the windup→neutral fallback because it supplies a distinct extension/release silhouette. This is scoped visual acceptance of these three poses at game scale 0.7, not acceptance of unprovided timing, runtime hit alignment or continuous animation polish.

## Inputs and independence

Inspected only `input-back_windup.png`, `candidate.png`, `input-back_neutral.png` and `sequence.png` in `/home/astra/projects/emberwake-demo/art-source/boss-release-v1/`. No prompt, producer receipt, game review, other boss asset or preservation claim was opened. The candidate was evaluated as new paint, with no assumption that the body pixels or anatomy were source-preserved. No score target was supplied; no numeric rating is assigned.

All three source sprites are 256×256 RGBA. The supplied sequence is 768×276 RGB. Native game-scale inspection used 256→179 nearest resampling (0.7 to rounding), and a doubled 358 px cell view on a contrasting light background. The provided sequence and individual originals were also viewed. A separate proof packet shows the new three-pose sequence and the two-pose fallback at the same scale.

## Reasons for acceptance

- **Weapon-arm ownership is coherent.** The windup bends the screen-left arm above the head; the candidate extends that same side diagonally up-left, while the other large fist stays screen-right. In the candidate, the connected arm/weapon chain runs approximately from the shoulder near local (92,91), through (70,65), to the club cap near (39,27); the opposite fist is around (177,145). Neutral keeps the club on the same screen-left side. There is no visible arm swap, extra limb or detached weapon.
- **One rear-view stone enemy survives the repaint.** The same back-plate stack, branch/antler silhouette, moss, flowers, gold spiral markings, bulky stone hips and rounded stone feet remain identifiable at 0.7 scale. Individual stone partitions, leaf clusters and highlights differ, as expected from new paint, but I do not see a material or body-volume change large enough to suggest another enemy. The rear view remains legible throughout.
- **Footing/origin is serviceable.** The lowest nonzero-alpha rows are y229 in windup,228 in candidate and230 in neutral—about 1.4 game px total variation. Both candidate feet remain present and broadly braced. There is a small lateral stance/torso settle on returning to neutral, rather than a large vertical lift, missing support limb or obvious origin reset. These image bounds are localization evidence, not proof of physical foot planting.
- **The action has a distinct release cue.** Windup presents a bent overhead arm and compact weapon; the candidate presents a long extended diagonal arm/weapon silhouette. At game size it reads as reaching/striking away from the viewer and slightly screen-left. That is a defensible attack release, even without particles. It does not independently communicate a ground impact or a strike centered exactly on the forward axis; no such specific impact brief was provided.

Coordinates above refer to the original 256×256 sprite, x right/y down; they are approximate visible landmarks.

## Adjacent transitions and fair fallback comparison

**Windup→candidate:** coherent bent-arm-to-extension progression. The club moves from overhead toward upper-left while the torso and screen-right fist counterbalance the reach. The silhouette change is large enough to distinguish a release from another held preparation pose. The connected stone segments remain readable as one weapon arm at game scale, although the precise wrist/grip boundary is less clear than the gross arm ownership. I do not see a decisive anatomy failure there.

**Candidate→neutral:** the sharper join. The extended diagonal weapon comes down into the upright held position; the torso and stance return to a less stretched, more square configuration. The stone and foliage redraw is perceptible at 2×, and the pose change could pop if the release is held too long or recovery is too abrupt. Nonetheless, the same-side weapon return and retained body mass make it a plausible coarse recovery. There is no demonstrated visual reason to reject the candidate solely for this missing intermediate recovery pose.

**Old windup→neutral fallback:** simpler and somewhat less visually busy, because it avoids the new-paint body/leaf changes and the extended release-to-rest join. It also jumps directly from preparation to rest, leaving no visible extended strike pose. On the nominated still evidence, that omission is a greater action-readability cost than the candidate's small repaint/settling differences. I therefore prefer the candidate sequence. I am not claiming that adding a frame automatically improves motion; here the added silhouette carries a specific bent-to-extended arm change that the fallback lacks.

## Limits and smallest next check

No exposure times, animation metadata, attack trajectory or moving playback were supplied. I reconstructed the order from stills; I did not perceive normal-speed continuous video and cannot judge the final force, easing, controller feel, impact timing or hit position. A release held for an unsuitable duration could still look like a raised-arm gesture. That does not reverse this pose-level acceptance.

The smallest useful next check is human game-speed playback of **both sequences at identical windup/recovery timing**, with only the candidate release inserted in the new version. Check the candidate→neutral return and confirm that the diagonal weapon reach matches the intended attack direction. Add a recovery intermediate only if that actual playback exposes a distracting snap; there is no clear reason from this narrow review to repaint the entire enemy or force a preservation mask onto the candidate.

## Frozen fingerprints

Start/end SHA-256 fingerprints matched for all four nominated inputs.

| Input | SHA-256 |
|---|---|
| `input-back_windup.png` | `8030f97e86236ffe2c09b757c039e603e00546966412cd536bfbbe239b3afc16` |
| `candidate.png` | `16d27574bd7c726ef91f3473bd947048988f47a9a8a9f4ab21319e5832fa0f24` |
| `input-back_neutral.png` | `4d2dd0bdee957e1b513f1631ddd1f86b389eaa29dcc5d18d4b9328015b5157e4` |
| `sequence.png` | `42c59c846af5c204bcfc5663b619dc9d57d9b85fbe6a71faa5ffc4386b6e7e02` |

Output is confined to `/home/astra/projects/emberwake-review/warden-release-review.md` and the isolated `warden-release-proof.png`. No main asset, producer receipt or game file was modified. Changed art, timing or intended strike direction requires a new scoped judgment.

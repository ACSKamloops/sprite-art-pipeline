# Frozen anonymous full-action review

**Preference: B, modestly, for material continuity.** At the 84-pixel game proxy the practical difference is close to a tie. I find no demonstrated new regression, and no improvement to hand shape, action staging, or timing. This judgment was frozen before any unblinding.

The nominated input is the anonymous Rowan NE/NW cast packet under `/home/astra/artifacts/emberwake-rowan-ne-cast-material-v1/full-action-review/input`. I read only that packet and the case-free blind-review card. No implementation mapping, producer report/history, prior review, frozen-source art, or target was opened. No accidental exposure occurred. All work products are confined to this critic directory. The supplied source art and media were not changed.

## Material, sections and volume

In both views, source exposures **01 and 02** (the sheet's second and third columns, 60–240 ms) provide the useful comparison. A has a small, bright cream/yellow area at the bent inner forearm. B replaces the impression with cooler silver/gray sections, closer to the metal bracers already visible at neutral and in the same hero's appearance/cardinal cast context. On the light, dark and game grounds at 128 and nearest 256, B holds together better as one armored costume. A's bright patch can read as an exposed pale sleeve or a sudden material change rather than a steel section.

That is a relative reading, not proof that A violates an unseen costume specification: the packet does not rule out an intentional pale undersleeve. B is a useful consistency preference, not a wholesale drawing upgrade. At 84, A's brighter patch is a somewhat stronger local accent on dark/game ground; B still preserves the forearm-to-glove separation. I do not find a meaningful loss of hand readability.

The comparison is localized. The measured changed regions are NE 01 `(81,56)–(93,72)`, NE 02 `(83,55)–(95,71)`, NW 01 `(36,56)–(48,72)`, and NW 02 `(34,55)–(46,71)`, in original 128-stage coordinates with exclusive right/bottom bounds. Each contains 73 changed RGBA pixels. All alpha values are identical, and 00/03/04/05 are identical between A and B. These facts bound the claim: section shading changes, but silhouette, limb length, attachment geometry and gesture do not.

The **smallest remaining visible issue** is the compact inner-elbow/lower-bracer shading in B 01/02. At nearest 256, several dark seams and small gray lobes make the bend read somewhat like a stack of hinge blocks rather than one rounded armored forearm. It is a minor section-clarity issue; I do not infer broken anatomy. If another pass is wanted, the smallest useful experiment is one or two shading pixels in one 01 inner-elbow region, keeping B's metal palette and silhouette. Compare 84/128 dark and game proofs before spreading that experiment to 02 or the other view. A full limb redraw or more animation frames is not supported by this finding.

## Identity, hand and full action

Identity is stable and tied. The chestnut/orange spiked hair, large head, blue tunic with gold edging, round silver shoulders, pale shorts and brown boots/gloves remain the same hero throughout. Entry and final neutral agree with the diagonal appearance context. The cardinal cast context supports the same materials and an open gloved casting gesture. The rear-quarter view naturally hides parts of the far arm; occlusion alone is not a missing-limb finding.

The visible brown casting hand opens clearly against all three grounds at 128/256. At 84 it becomes a compact splayed glove but still communicates an open-hand action. Fingers, hand silhouette and wrist position are unchanged between variants. There is no demonstrated hand-anatomy fix or hand regression from B.

I inspected the full sequence and **every neighboring pair for NE A, NE B, NW A and NW B**:

| Boundary | Visible reading and comparison |
| --- | --- |
| 00 → 01, at 60 ms | Neutral arm raises into a bent, open-hand preparation. The localized material change is visible; attachment and gesture tie. |
| 01 → 02, at 140 ms | A small continuing shift of the raised-arm pose. The same A/B material distinction persists without changing the progression. |
| 02 → 03, at 240 ms | The character reaches and leans into the cast. This is the largest pose change. Both variants have the same reach, body/leg shift and open hand. |
| 03 → 04, at 320 ms | Arm lowers and torso returns toward upright. Both variants are identical here; any perceived recovery speed is shared. |
| 04 → 05, at 400 ms | Open hand returns to the hanging neutral glove. Both variants are identical. |
| Final neutral / entry | 05 equals 00 in each direction and variant. This is a one-shot terminal return, not an asserted looping seam. |

The chronology reads as preparation, extension and recovery. The 02→03 and 03→04 steps are relatively large compared with the small 01→02 preparation change; that is a shared staging characteristic, not an A/B regression. Whether those changes feel too abrupt at normal speed requires continuous playback with an observer. No physical foot-contact or controller-feel claim is made.

## Coverage and evidence limits

Directly viewed all 18 paired static sheets: NE and NW × 84, 128 and nearest 256 × light, dark and game ground. Every sheet contains all six A/B exposures. Also directly viewed chronological still strips decoded from all 18 paired one-shot APNGs at those same conditions. The 36 single-variant APNGs were measured and their six decoded exposures proved pixel-identical to the corresponding viewed paired crops. The visual comparison therefore covers their content without pretending a second animation display was observed.

Viewed appearance and cardinal-cast sheets at 84, 128 and 256, plus decoded six-exposure cardinal APNG strips at 84/128 for south, east, north and west. The context establishes identity/material comparison only; this review does not certify new edits or all other actions/directions.

Measured all **62 APNGs**: six frames each, holds **60/80/100/80/80/100 ms**, presentation starts **0/60/140/240/320/400 ms**, total **500 ms**, `plays=1`, no separate default image. No timing-only credit is given to either variant because timing is tied.

This environment supplied static image perception. Motion judgments reconstruct chronology from decoded stills and measured holds. I did not observe continuous video, human normal-speed playback, engine rendering, editor exchange, physical support/contact or live gameplay. The 84 proof is explicit offline nearest resampling, not verified pixel identity with an engine's 0.66 draw scale. Moderate confidence in the B material preference at 128/256; low confidence in any consequential game-scale advantage at 84.

## Frozen integrity

All 114 packet files were fingerprinted before visual inspection. The 113 entries in `SHA256SUMS` matched; all 24 frame PNG/RGBA manifest hashes and all 62 APNG media hashes matched. The packet's own SHA256SUMS file is included in the independent before/after fingerprints. The final verification compares every nominated packet file with that initial baseline and records a separate hash for the rubric. See `input-fingerprints-before.json`, `input-fingerprints-after.json`, `input-integrity-after.json`, `frame-verification.json`, `apng-measured-timing.json`, `single-paired-decoded-equivalence.json`, `coverage.json` and `judgment.json`.

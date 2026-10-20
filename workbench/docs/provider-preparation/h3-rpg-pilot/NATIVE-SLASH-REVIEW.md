# Independent native H3 sword-slash review

**A recognizable one-shot attack draft, with native weapon clipping that blocks
finished sprite acceptance.** It is worth preserving and inspecting, but is not
a 9/10 result. No matched same-subject PixelLab run exists. This reviewer made
no generation/provider/agent calls and edited no root files.

Artifact root:
`/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014/h3-slash-001/`.

| Artifact | SHA-256 |
| --- | --- |
| `source.png` | `571b74ac6bd1a945263c8c5cdf2b1eab9facf277bbc752c767de6f4412bf8084` |
| `native-video.mp4` | `cede01409bbf9a71aee0feaf2678a125fd54f2db52b45439901ba3b1e05b44a6` |
| `media-review/MANIFEST.json` | `f3a3ca8b475281557cf1f724ef6f5dd342f47015a840db9800198f6638f3e32c` |

The video hash and **all 107 decoded native-frame hashes** were independently
checked against the manifest. It records 768×768 H264/YUV420p, 24 FPS, with
presentation end 107/24 seconds (4.4583 seconds), for four requested seconds.

## Actual visual coverage

Viewed chronological pages **00–06, all frames 0–106**, plus the eight-sample
sheet and native-resolution frames **17, 26, 28, 40 and 53**. The same original
source was inspected in the preceding walk review. This is complete chronological
contact-sheet coverage at 256px display with five native detail checks, **not
continuous native-speed viewing**. Root's separate browser playback is not
inherited as this reviewer's visual coverage.

## Provisional subjective ratings

| Area | Rating | Qualification |
| --- | --- | --- |
| Source design | **8/10** | Same readable blue-clad, silver-armored sword/shield hero as the walk input. |
| Attack motion | **6/10** | Clear anticipation, strike, follow-through and recovery; long holds and ambiguous blade/grip during the strike remain. |
| Game-sprite readiness | **3/10** | Native sword clipping, opaque video and incomplete equipment/contact validation prevent production acceptance. |

No loop rating applies: this is a **one-shot**, not a requested locomotion loop.
These scores are not calibrated model rankings or proof of smooth timed playback.

## Frame-specific findings

- **Anticipation:** early frames **0–10** remain near the source stance. Frames
  **12–25** turn the torso, bring the shield forward and raise the sword. The
  preparation reads clearly, but the tip is already clipped at the top in native
  frame **17** and remains outside the displayed canvas in several raised poses.
- **Strike:** **26–30** show a fast sweep/lunge with bright sword streaks. Native
  **26** has overlapping/blurred weapon shapes across the body and behind the
  head. This may be motion smear/effect treatment; it prevents confident inspection
  of one rigid blade and a stable grip through the impact. It is not proof that
  the character literally has two swords.
- **Native clipping:** the bright effect reaches outside the right canvas at
  **27–29**, but the issue is not limited to an effect. Native **40** and **53**
  show the physical blade continuing through the right edge with no visible tip.
  The contact pages show the same issue throughout much of **30–53**. Neither
  adding black padding afterward nor extracting alpha can recover those missing
  native pixels. The source's complete sword must not be silently substituted.
- **Follow-through:** approximately **31–52** hold a wide, extended guard/lunge
  with little pose change. This makes the attack phase easy to identify, but
  extends the held follow pose for roughly 0.9 seconds. Its gameplay timing needs
  actual-speed assessment or an explicitly authored timing derivative.
- **Recovery:** **53–64** bring the weapon down and return toward the source
  stance. **65–106** are predominantly a long settled idle tail. Keeping the
  complete video is important; an edited one-shot should label any removed tail
  and authored frame holds rather than imply native attack duration was shorter.
- **Identity/equipment:** brown hair, face, blue tunic, silver armor and round
  wooden shield remain recognizable. No sustained equipment disappearance was
  observed. Forearm/hand/hilt connection is visible in held poses, but the blurred
  strike and missing tip prevent a full rigid-weapon/grip approval. Shield grip
  remains concealed; coherent appearance is not attachment proof.
- **Camera/feet:** the body moves into a plausible lunge and widens its stance;
  that movement alone is not camera drift. There is no obvious reframing. Exact
  planted-foot behavior, force transfer and ground contact were not measured or
  continuously viewed. Hair/armor edges show video softness and colored fringes;
  model versus codec contribution remains unresolved.

## Decision and derivative boundary

Keep this as an auditable unfinished attack candidate. The main limitation is
native framing of the weapon, not merely transparent export. A local one-shot
derivative may improve presentation/timing but cannot reconstruct missing blade
pixels without additional authored or generated material. No such repair is
approved or performed here. It must remain distinct from native H3 output and
from recovered PixelLab algorithms.

The transparent walk cycle is a different artifact and is not rated in this
slash report. No extra provider call is implied by “worth continuing”; preserve
the current generation budget and inspect existing derivatives separately.

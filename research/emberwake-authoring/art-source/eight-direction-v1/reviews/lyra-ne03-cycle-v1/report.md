# Frozen anonymous complete-cycle review

Frozen before unblinding. Reviewed only the nominated packet at `/home/astra/artifacts/emberwake-lyra-ne03-transition-v1/review-packet/input` and the anonymous review card. No producer material, source mapping, previous review, grade, target, history, skill case or canonical project was opened. The directory/task label indicates NE03 as a focus but discloses no A/B assignment. The input manifest necessarily exposes hashes; those establish integrity and localize the visual comparison, and earn no quality credit. No accidental source-identity exposure occurred.

**Overall judgment: both are visually coherent, usable candidates for the supplied stylized character; I have no confident A/B full-cycle preference.** A has the cleaner, fuller boot rendering in pose 03 at enlargement. B's narrower boot placement might help the passage into 04, but I cannot establish a perceptible whole-loop motion benefit from these stills. At the 84px presentation that local difference is too small to support a strong selection. This is a scoped visual review, not final animation acceptance.

## Separate judgments

| Dimension | Judgment and confidence |
|---|---|
| Appearance, drawing, material and anatomy | Good stylized volume and costume continuity in both; moderate-high confidence from stills. White layered hair, green/teal cloth, gold trim, silver cuffs and brown leather remain distinct. B03 has a small boot contour/shading roughness described below. I find no demonstrated detached joint, extra limb, missing limb, clipped extremity or broad alpha halo. |
| Character identity and temporal identity | Strong match to the supplied appearance strip and east/north/west idle/walk context; high confidence within the shown rear-quarter views. Head mass, short proportions, armor layout, gloves, cape and boot vocabulary remain recognizable. A face hidden by the rear-quarter view is not identity loss. |
| Visible motion chronology | Plausible alternating leg progression, with clear open and compressed silhouettes; moderate confidence in order, low confidence in normal-speed smoothness. The overlap across 03–05 reduces direct support/swing leg identification. Occlusion is a plausible explanation and is not evidence that a leg disappears anatomically. |
| Practical 84px use | Character identity, general facing and broad stepping silhouettes survive. Passing/crossed-leg shapes read less clearly than the open strides, especially on the dark ground. Moderate confidence in still-image usability, low confidence in gameplay feel and movement-speed matching. |
| A/B full-cycle selection | No confident preference in either direction. Small local appearance preference for A03; no proven overall animation win. |

The art is shaded, detailed chibi fantasy imagery. I did not impose a limited palette or a deliberately rough retro style. Neither greater file counts nor hash/coordinate properties influence the aesthetic judgment.

## Actual viewing coverage and presentation

I opened the appearance PNG itself with `view_image`, then actually opened all 30 generated sheets with `view_image(detail=original)`: 18 complete predecessor/current sheets, nine identity-context sheets, and three focused 02/03/04 sheets. These are derived only from nominated PNGs. All 32 candidate cels and all 32 cyclic predecessor/current pairs were present and visually inspected at each of 256, 128 and 84 pixels on each ground. Every pair sheet includes both variants, all eight adjacent pairs and the explicit 07→00 wrap. The 30 cardinal context cels were viewed at the same three stage sizes and grounds for identity/turn context only. Context animations and direction transitions are not certified by this review.

Every presentation retains the complete 128×128 source stage and its registration, including its transparent margins. No trimming, fitting to the actor, recentering, cleanup, translation, recoloring or resampling other than nearest-neighbor full-stage sizing was applied. The supplied pivot is (64,112). 256px is exactly 2×; 128px is native; 84px is the requested integer approximation to the declared 0.66 game scale (128×0.66 = 84.48). The 84px image is therefore a declared review proxy, not proof of the engine's sampler or fractional-pixel placement.

Grounds were solid light `#e6e0d5`, dark `#171b24` and representative game-green `#35452e`. The green ground is a review surrogate, not a supplied level screenshot. Contact sheets have labels outside the stage; these do not affect actor placement. See `coverage.json` for sheet fingerprints and explicit cel/pair records.

## Declared clock and all wraps

The packet supplies static single-frame PNGs and `INPUTS.json`, with no timestamped video or engine capture. Each candidate PNG is one frame and carries no duration metadata. Thus these are the **declared** presentation intervals, not measured media PTS:

| Cel | Start /160 seconds | Start ms | End ms |
|---|---:|---:|---:|
| 00 | 0/160 | 0 | 56.25 |
| 01 | 9/160 | 56.25 | 112.5 |
| 02 | 18/160 | 112.5 | 168.75 |
| 03 | 27/160 | 168.75 | 225 |
| 04 | 36/160 | 225 | 281.25 |
| 05 | 45/160 | 281.25 | 337.5 |
| 06 | 54/160 | 337.5 | 393.75 |
| 07 | 63/160 | 393.75 | 450 |

Every hold is exactly 9/160 s = 56.25 ms; the cycle is 72/160 = 9/20 s = 450 ms. There are eight pose presentations per loop, equivalent to 160/9 ≈ 17.7778 pose presentations per second. The next 00 starts at 450 ms. No interpolated cels or alternate exposure schedule are supplied. I explicitly inspected A-NE 07→00, A-NW 07→00, B-NE 07→00 and B-NW 07→00. Their still-image progression does not reveal a special loop-only identity or registration break; smooth normal-speed wrapping remains unverified.

## Visible pair chronology

These observations apply to each independently inspected A-NE, A-NW, B-NE and B-NW cycle; screen direction reverses between NE and NW. I use screen-visible roles rather than assert anatomical left/right through occlusion.

| Pair, including all four wraps | Visible evidence |
|---|---|
| 00→01 | The broad split stride draws inward; the short/rear-looking boot descends toward a more separated two-boot silhouette. Head, collar, cape and torso stay coherent. |
| 01→02 | One boot becomes the longer nearly vertical leg silhouette while the other rises toward the hem. This is a relatively conspicuous stride change; whether its speed feels abrupt needs actual playback. |
| 02→03 | The raised boot is increasingly hidden under the coat/other leg. The long boot remains visible. A retains a fuller rounded toe and smoother shaft; B has the narrower, more stepped shaft/toe discussed below. Neither demonstrates a severed knee or ankle. |
| 03→04 | The long visible boot turns inward into a crossed/diagonal silhouette. A's wider 03 toe and B's narrower 03 toe are competing local drawings; stills do not establish which produces better perceived weight transfer. |
| 04→05 | The two lower-leg forms are most compressed/crossed. Cloth hem and dark trousers obscure attachment detail, especially at 84px. This is an actual readability limit, not proof of an anatomical failure. |
| 05→06 | The opposite long boot becomes clear and the smaller boot reappears beside it; separation improves without an identity change. |
| 06→07 | The stride opens again; the lower boot moves outward while the other remains higher/shorter in the image. |
| 07→00 | The open-step silhouette continues into the initial broad pose. The upper mass remains registered and identifiable. No distinct wrap-only pop is demonstrated in the sheets. |

The arm/cape action is restrained compared with the lower legs. More reciprocal arm motion could be a performance preference, but it is not established as a drawing defect and does not decide this A/B comparison. I cannot determine planted-foot duration, actual foot sliding, ground contact or physical weight from a stationary transparent-stage walk without its intended movement track.

## Smallest remaining drawing issues and experiments

1. **B pose 03: slightly pinched/stepped leather boot volume.** See B/northeast/03.png, approximately source x65–78, y96–115; corresponding B/northwest/03.png approximately x51–64, y96–115, most clearly in `sheets/local-02-03-04-light.png` and the 256px dark/game versions. The ankle-to-toe region has alternating dark protrusions/notches and a narrower front face than A03 or the neighboring clearly modeled boots. At enlargement it reads a little more corrugated than the broad leather volume elsewhere. This is a small local contour/material issue, not a broken leg. Confidence: moderate at 256px, weak at 84px. Smallest experiment: regroup the boot-cuff/shaft shadow and one or two edge steps into a continuous leather form while keeping B's current limb placement, full-stage registration, hem overlap and timing. Expected benefit: cleaner volume through 02→03→04, without making the far leg artificially visible.

2. **Shared dark-ground passing-pose separation is limited.** A and B, NE/NW 03→04→05, lower-body area approximately x53–80, y86–116 (NE) and x48–75, y86–116 (NW). At 84px the crossed brown/black forms combine into a compact column; the hair and green-gold torso stay readable while the precise foot role is harder to identify. The observed issue is loss of small-scale separation, not a claim that overlap is invalid. Confidence: moderate for this dark proxy ground; actual level performance unknown. Smallest optional experiment: adjust a tiny existing leather highlight/shadow boundary at the overlap or toe in 04/05, keeping the silhouette and pose unchanged, then compare the full cycle at the same 84px size. Expected benefit: preserve the boot's front-facing surface without adding an inappropriate global bright outline. This is a polish experiment, not a prerequisite inferred from a style rule.

I did not find an equally specific A03 drawing defect worth inventing. Its broad toe could be a motion preference in the local transition, but that remains a playback question. No wholesale redraw, extra in-between or timing change is justified by this review alone.

## Integrity, freeze and limits

Before viewing, all 63 nominated PNGs matched the manifest SHA-256 values and there were no extra PNGs. After the review, the manifest and all 63 PNGs were rehashed and remained identical. `INPUTS.json` SHA-256 is `dc3ccc89e633e81d6598c328db1222bd683bae8cf6b0875bc54a28780b28be6f`. Complete input ledgers are `input-hashes-before.json` and `input-hashes-after.json`. Report, structured judgment, coverage, ledgers and sheets are bound by `FROZEN.json`; no unblinding occurred before that freeze.

Perception limits: actual image inspection and chronology reconstructed from stills plus known declared holds; no continuous video perception, human normal-speed playback, player/controller feel, engine execution, actual render filtering, level-background capture, root-motion matching or physical-contact validation. Static inspection cannot certify normal-speed smoothness, weight, planted feet or a universal animation quality threshold. Approval of other actions, other directions, equipment changes, animation transitions or a later art/timing revision is outside this review.

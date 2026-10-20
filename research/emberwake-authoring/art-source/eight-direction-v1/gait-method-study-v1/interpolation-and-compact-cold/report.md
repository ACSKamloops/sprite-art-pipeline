# Anonymous gait-method cold review v1

Frozen before unblinding at 2026-10-17T04:12:32.382679+00:00.

All five variants are good, usable detailed RPG sprites in the **7.5/10 overall** band. Character identity is stronger than leg-motion clarity. No confident overall winner among X-A/B/C. Y-A makes the step clearer than Y-B at84px; that is a weak readability preference, not a verified playback win.

**Perception limit:** Ordered stills and full-cycle chronology with exact declared holds. I did not perceive continuous video, run optional players, measure browser presentation timestamps or test controller feel. Motion judgments reconstruct chronology from PNGs and known holds.

## Ratings

| Actor packet | Variant | Appearance | Temporal identity | Motion/readability | Game use | Overall |
|---|---:|---:|---:|---:|---:|---:|
| X (rowan) | A | 8.0 | 8.0 | 7.0 | 7.5 | 7.5 |
| X (rowan) | B | 8.0 | 8.0 | 7.0 | 7.5 | 7.5 |
| X (rowan) | C | 8.0 | 8.0 | 7.0 | 7.5 | 7.5 |
| Y (lyra) | A | 8.0 | 8.0 | 7.5 | 7.5 | 7.5 |
| Y (lyra) | B | 8.0 | 8.0 | 7.0 | 7.0 | 7.5 |

Drawing/identity uncertainty approximately±0.5; motion, game use and overall approximately±0.75. No automatic points for denser frame counts, export correctness or an assumed method. Overall is a broad scoped judgment, not arithmetic or release certification.7 means good usable work with noticeable limitations;8 strong polished small-sprite candidate;9 exceptional control.

## Full-cycle verdicts

**X-A:** Coherent hair, face, armor, tunic, gloves and boots across8poses. Alternate lifted/reaching leg states are present. Second-half pale overlap limits leg-role clarity.07->00 is a plausible continuing reach, not an exceptional reset fault.

**X-B:** All32poses retain character/costume identity. Smaller chronological changes do not resolve the pale overlap or establish superior normal-speed motion. No exceptional31->00 fault; same overall tier as A.

**X-C:** All32poses retain identity. Small intermediate contour/detail changes do not justify a higher/lower overall art tier at84px. No demonstrated unique structural or31->00 failure. No confident B-versus-C preference.

**Y-A:** Coherent silver hair, teal scarf/cape, costume and limbs across8poses. Wider boot excursion gives a clearer step at84px.04-06 overlap is a compact stylized turn, not evidence of a missing leg. No exceptional07->00 failure.

**Y-B:** All24poses preserve identity. Nearer-resting boot positions yield a restrained step and subtler stride contrast at84px. Could suit a compact performance. No demonstrated structural breakdown or exceptional23->00 failure; normal-speed superiority/inferiority unverified.

Both SE and SW were inspected separately for every variant and occupy the same quality tier. The concerns reflect to the opposite side. No missing limb, detached joint, catastrophic identity change, crop failure or material halo was demonstrated. Cardinal context supports identity consistency, but does not certify transitions or other clips.

## Strongest actionable findings

**X1 — moderate, localized.** The lifted cream knee becomes a large round light mass, then the pale trouser overlap spreads beneath the belt before the boot extends again. The knee/upper-boot and opposite thigh are harder to track than face or armor at84px. Dense variants carry the same silhouette progression.

Evidence: {"A": ["05->06", "06->07", "07->00"], "B": ["20->24", "24->28", "28->31->00"], "C": ["20->24", "24->28", "28->31->00"]}. Approximate source regions (x0,y0,x1,y1): {"southeast": [48, 80, 89, 112], "southwest": [38, 80, 79, 112]}.

Foreshortening and occlusion can explain hidden leg sections. No extra limb, detached knee, reversed phase or impossible anatomy is demonstrated. The high-knee performance itself may be intentional.

Expected benefit: Clearer leg-role and knee-to-boot tracking in the second half of the stride.

Smallest useful next experiment: One lower-body-only drawing alternative for A06 and A07, preserving trajectories and holds. Clarify overlap crease and knee-to-boot silhouette; compare complete original/altered8-pose loops at84px and9/20s with a human before propagation into B/C.

**Y1 — minor to moderate, conditional on game speed.** B keeps both boots nearer the resting stance. Reaching versus lifted-foot contrast and stride direction are less explicit at84px than A; character rendering stays coherent.

Evidence: {"B": ["00->06", "06->12", "12->18", "18->23->00"], "comparison": "A00/02/04/06 versus B00/06/12/18"}. Approximate source regions (x0,y0,x1,y1): {"southeast": [48, 84, 87, 113], "southwest": [40, 84, 79, 113]}.

Compact stepping is valid. The stills do not prove shuffling, sliding, worse fluidity or better fluidity. No travel velocity/contact behavior observed.

Expected benefit: Choose gait amplitude for the actual movement velocity without first increasing frame count.

Smallest useful next experiment: Human compare existing A/B at84px, identical9/20s duration and identical travel velocity on a game ground. If B reads as shuffling, test2-3native pixels of extra toe reach at the two contact extremes and repair their immediate neighbors.

## Evidence and scope

- Read only the supplied blind-review card and nominated X/Y input folders. No parent maps, producer reports, previous grades, skill histories or other assets consulted. No known accidental exposure. Actor names occur in permitted ledgers; methods remain anonymous.
- Verified175 X files and95 Y files against ledger SHA-256 values, including context. All per-file hashes are in fingerprints.json and report.json.
- Reviewed10 diagonal clips,208 variant frames and208 directed adjacent pairs, including10 wraps. All90 clip×scale×background views inspected. Each chronology row repeats its next frame so row transitions and wraps remain adjacent.
- Scales:128px native stage,84px nearest game proxy,256px nearest enlargement. Pivot64,112. Declared0.66scale is84.48px before raster rounding.
- LightRGB222,221,211; dark27,31,41; synthetic textured green ground base66,82,57 with74,88,63 and58,73,51 patches. These are contrast probes, not live game integration.
- Every loop declares9/20s (0.45s): A8×9/160s; X-B/C32×9/640s; Y-B24×3/160s. Exact rational start times and holds are in report.json. Renderer presentation timing was not measured.
- Both appearance strips and all supplied cardinal context frames inspected for identity/turn context only. No provider/model/editor calls, external search, production edits or input mutation performed.
- Other directions, equipment, actions, start/stop/turn transitions, actual movement velocity and physical foot contact remain outside scope. Changed art/timing needs a new review.

Ledger fingerprints:

| Packet | INPUTS.json SHA-256 |
|---|---|
| X | cdbd3a479d73187337ce241cfa3e0203e45c143ad3fac87953673ecac145ac61 |
| Y | 927eb95b4d12e8ec8723216f622a927134efeed5bf80f928ca5ccecd7b46d2db |

Files: report.json contains findings, ratings, full fingerprints and chronology; fingerprints.json binds the inputs; sheet-manifest.json lists all90 reviewed views; FROZEN.sha256 freezes these four records. Generated material is confined to this fresh review folder.

Review complete within the stated still/chronology perception limit.

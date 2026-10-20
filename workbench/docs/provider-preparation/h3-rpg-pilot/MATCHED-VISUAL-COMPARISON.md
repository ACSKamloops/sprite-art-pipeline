# Matched-subject visual comparison: walk, original slash and margin slash

**PixelLab's returned sprite arrays are currently more usable as sprite assets
for these three matched cases.** The walk sword is easier to track, and both
slash cases preserve a visible physical blade tip through the inspected attack poses.
Direct H3 still supplies useful recognizable motion, but its native video and
local sprite derivatives have distinct framing, timing and alpha limitations.
This is a comparison of these **product workflows**, not an isolated base-model
ranking, general superiority claim or 9/10 approval.

Artifact root:
`/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014/`.
No provider/model/agent calls were made by the reviewer; no root files were edited.

## Held inputs and confounds

Walk source SHA-256:
`571b74ac6bd1a945263c8c5cdf2b1eab9facf277bbc752c767de6f4412bf8084`.
Margin-slash source SHA-256:
`e63340b333df3354948b4ee707b2e4bfa23ca901f6b464a941e2ff06281d4a5e`.
The same source within each pair was independently hash-checked. Root separately
verified literal prompt equality through REA. The margin actor is 75% of the
original actor scale; this is a different case, not a same-world-scale comparison
against the original walk or original unpadded slash.

PixelLab requested 16 generated frames plus reference, seed 123, transparent
output, default de-flicker and omitted/auto caption fields. Direct H3 requested
four seconds at 768px, returns opaque video with 107 frames and has no equivalent
typed seed/alpha/frame-count/caption contract here. PixelLab's native frame clock
is unknown. Any displayed two-second inspection clock is analyst authored.
Private PixelLab inference and pixel conversion remain unrecovered.

## Actual review coverage

- All three PixelLab cases: all **16 generated slots** in full-canvas checker contact
  pages, and slot **0** individually. Additional individual detail checks inspected
  both slash cases' slots **2, 6, 7 and 12**. Thus all 17 outputs in each case were
  visually covered, with contact-sheet versus individual coverage distinguished.
- H3 walk: reused the preceding all-107-frame chronological review, eight-sheet
  inspection and individual native frames 19/42/106, whose hashes are unchanged.
- H3 margin slash: newly viewed all seven chronological pages covering **0–106**,
  the eight-sheet, source and individual native frames **24 and 35**.
- H3 original slash: reused the preceding all-107-frame chronological review,
  eight-sheet and native detail frames **17, 26, 28, 40 and 53**, bound to the
  unchanged original slash source/video/media-manifest hashes below.
- Local workflow: the previously inspected H3 walk eight/sixteen atlases are
  separate local keyed/sampled outputs. Newly viewed the H3 margin slash's rejected
  local sixteen-sample atlas and read its explicit native-index mapping.

No continuous visual playback occurred in this comparison. No all-frame contact
review implies timed motion acceptance, ground-contact proof or alpha-edge review
on varied gameplay backgrounds. Original unpadded PixelLab slash completed during
this review and was then inspected as the third case before report finalization.

## Walk: demonstrated differences

PixelLab slots **2–12** show an ordered alternation of stepping/crossing poses;
slots **13–16** settle toward idle. The head, hair, tunic, armor and shield remain
recognizable. The sword stays predominantly down-diagonal throughout and is
visually easier to track than H3 walk's large transition to near-horizontal at
native **40–49** and **84–93**. This is a visible stability/choreography advantage,
not proof that PixelLab preserves a rigid physical weapon or hidden grip perfectly.
Some leg overlaps and torso/profile shifts remain; exact contact is unapproved.

Neither complete raw output is automatically a seamless walk loop: PixelLab's
last four generated slots are near a settled stance, while H3 has near-idle lead
**0–6** and tail **99–106**. Direct H3's selected local **[16,64)** cycle removes
those full-clip pauses and presents a more plausible repeat, but that is locally
authored selection and holds. Comparing it with PixelLab's whole raw sixteen
frames would confound selection with generation. No provider FPS was recovered
from the PixelLab array.

## Original slash: demonstrated differences

PixelLab original slash slots **2–5** visibly draw back and raise the sword;
**6** contains a broad white crescent around the strike, **7** a trailing arc,
**8–11** follow-through, and **12–16** recovery toward the original stance.
Individual slots **2, 6, 7 and 12** show a more complete, readable blade/effect
presentation than the clipped direct-H3 original result. Unlike native H3's top
crop in **17** and physical right crop in **40/53**, the PixelLab contact page
keeps the sword and stylized effect within the canvas in these observed outputs.
Root's separate alpha-edge screen reports no edge contact across its generated
PNGs; that mechanical receipt is not a substitute for the visual checks above.

The PixelLab actor rotates more through the strike; the shield becomes partially
hidden behind the body in **6–11**, instead of remaining prominently in front as
in H3's chosen choreography. That can be plausible torso/far-arm occlusion, not
proof of shield loss. The face, hair and blue/silver outfit remain recognizable.
Neither hidden attachment nor rigid weapon length is fully proved. PixelLab's
finite event sequence is more useful for selecting attack poses than H3 original's
long follow hold **31–52** and settled tail **65–106**, but native PixelLab timing
is unknown, so this cannot establish a faster provider-authored attack.

## Margin slash: demonstrated differences

PixelLab shows anticipation in slots **2–4**, a clear white crescent/sweep in
**6**, held follow-through **7–11**, and recovery **12–16**. Detail views of
**2, 7 and 12** show the physical sword tip fully contained. Slot **6** keeps a
finite crescent effect separate enough to inspect the actor. Hair/face/armor and
the round shield remain recognizable. The blade appears more stable and complete
at sprite scale than in the matched H3 artifact; hidden grip and force transfer
still require review. PixelLab also has repeated-looking follow poses, not sixteen
equally informative unique key poses.

H3 margin winds the sword far behind the actor: native **24** visibly cuts the
physical blade at the **left** canvas boundary. Native **35** cuts the blade at
the **right** boundary. This remains despite the smaller input actor. The full
chronological pages show a very prolonged follow pose approximately **28–73**,
recovery **74–86**, and near-idle **87–106**. Native **26–27** contain the fast
cross-body transition; the sampled/contact representation cannot certify grip
or one rigid blade through its smear. The H3 margin result does not show an
equally obvious finite white crescent at the corresponding event. Both action
choreography and effect treatment differ; exact strike phase alignment is not
established by matching source and prompt.

Physical native clipping cannot be repaired by adding padding or extracting
alpha afterward. No source-completed blade or synthetic repair was substituted.
The edge-flag count reported by root is a separate mechanical screen; the reviewer
directly confirmed the physical blade problem in native 24/35 without assuming
that every flagged border contact is a weapon defect.

## Raw output versus the local sixteen-sprite workflow

| Case | PixelLab returned-array readiness | Direct H3 / local derivative readiness |
| --- | --- | --- |
| Walk | Useful transparent sprite candidate; gait/loop/weapon/contact timing still unapproved. | Native video is a motion source; local [16,64) cycle is a more useful repeat but needs alpha-background, seam and equipment checks. |
| Original slash | Useful contained attack-pose candidate; authored timing and gameplay/contact validation remain. | Native top/right physical weapon clipping blocks complete-sprite acceptance; masking/padding cannot recover missing pixels. |
| Margin slash | Useful contained attack-pose candidate; no independent physical-rig or timed-action approval. | Native left/right physical weapon clipping persists. Rejected uniform sixteen-sample derivative additionally misses fast strike frames. |

None of these is approved production art or a universal quality gate. PixelLab's
returned alpha/native pixel canvas removes work that the current direct-video
workflow must supply locally; it does not settle motion quality by itself.

PixelLab generated outputs already provide 256×256, binary-alpha PNGs. The
reviewer recomputed **76–88 visible RGB colors for walk**, **68–83 for original
slash** and **77–86 for margin slash**, with alpha only 0/255 across all sixteen generated outputs in each case.
This is observed delivered-artifact behavior, not knowledge of the server's
quantizer/de-flicker/background algorithm. Returned reference slot zero is a
different artifact: it retains the original partial alpha and visible RGB exactly.
Only hidden RGB differs at 49 walk / 49 original-slash / 30 margin positions, consistent with the
known hidden-RGB normalization policy but not causal proof of which server code ran.

H3 raw output remains opaque H264/YUV420p. Local sixteen-sprite outputs are
whole-canvas resized and border-black keyed, not native alpha and not recovered
PixelLab conversion. Approximate alpha can lose connected dark outlines or retain
codec fringes; all-frame checker/color-background acceptance is still missing.

The rejected margin sixteen-sample derivative uses native indices
`0,7,14,21,28,35,42,49,56,63,70,77,84,91,98,106`. It **omits native 26/27**, the
actual fast strike transition, and spends many cells on the held follow pose.
Its weaker attack readability is therefore partly a local sampling problem.
Do not blame that derivative's omissions on the generator, or describe uniform
sampling as PixelLab's hidden extraction technique. Explicit authored key-pose
selection/holds could be evaluated separately without claiming native timing.

## Byte verification and evidence identities

The reviewer decoded all **51** completed-response PNG entries across the three PixelLab cases
and matched them to the extracted files, then verified all manifest PNG hashes.
All 107 H3 margin decoded-frame hashes matched its media manifest. The video and
source hashes below were independently recomputed.

| Artifact | SHA-256 |
| --- | --- |
| `pixellab-walk-v1/completed-response.json` | `153ae69313ad6c7ba238eb31d55a6919c912e6a6a817496708aca25f27ed65d0` |
| `pixellab-walk-v1/extracted/manifest.json` | `73b8e2b47f723ce3e5c51d0025f3c0c9d6b9b15fdc87b53386ec96bad1afb173` |
| `h3-walk-001/native-video.mp4` | `97e83ef3522a8892af98672861ee7ec5214c24dd4f441e38cc448c762c5ab046` |
| `h3-walk-001/media-review/MANIFEST.json` | `b5798c0c8f5de2f67e671f9fa0ee93342219c207e1da2a1e7cd4e2430430dd5b` |
| `pixellab-slash-v1/completed-response.json` | `5d99ec4d3ea8c2060e412815862f976bb90108e0f9e0e0d49fe3401548fa8e79` |
| `pixellab-slash-v1/extracted/manifest.json` | `3f471ffbbfd5e150565b46a77d7a29319f0fa2435b91b27d49f681d68fb63346` |
| `h3-slash-001/native-video.mp4` | `cede01409bbf9a71aee0feaf2678a125fd54f2db52b45439901ba3b1e05b44a6` |
| `h3-slash-001/media-review/MANIFEST.json` | `f3a3ca8b475281557cf1f724ef6f5dd342f47015a840db9800198f6638f3e32c` |
| `pixellab-slash-margin-v2/completed-response.json` | `4cf399e8306e467e624cdd0cf87ea053dc72461af4eea862eb7482c2ff9d0f30` |
| `pixellab-slash-margin-v2/extracted/manifest.json` | `ac91ebbf422b1d819210730e08f0e1366ad0c8affc15a6a3b6677819108267bf` |
| `h3-slash-margin-002/native-video.mp4` | `aed5ac139188860f2e3e39f58484ebda394c77fa7b8ae99f777cced03c572132` |
| `h3-slash-margin-002/media-review/MANIFEST.json` | `3a5dbd5fc20ad06eefca5629cd6888e3a7caa3523acce3f08b0812abb3ae2186` |
| `h3-slash-margin-002/sprite-once-rejected/MANIFEST.json` | `97fce59cd0a3bb6db0f886ea503f7e122ad9b487a673fb097dbce1b4f9d62816` |

Keep both successful raw outputs and rejected derivatives. PixelLab's clean,
contained sprite deliverable is a meaningful practical advantage in these cases;
it does not recover private conversion algorithms or prove a better base model.
Timed playback, scene-background alpha inspection and a justified loop/one-shot
keyframe policy remain required before game acceptance. No additional generation
or budget expansion is implied by this report. The original uniform H3 sampler's
omission of the strike was discovered and flagged; root's separately developing
manual-curation correction must retain that original derivative and get a new
review rather than quietly replacing this evidence.

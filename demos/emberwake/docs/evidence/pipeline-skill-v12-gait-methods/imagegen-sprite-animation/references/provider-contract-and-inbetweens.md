# Provider contracts and controlled in-betweens

Use when adapting a documented AI animation workflow to ImageGen or choosing
between new pose paint, a small part rig and image interpolation. These notes
were checked2026-10-16. Recheck changing provider schemas before integration.

## Keep the advertised workflows separate

PixelLab's [skeleton editor tutorial](https://www.pixellab.ai/docs/tools/animate-with-skeleton)
documents an iterative process: preserve one pose and generate two, correct
the drawing/skeleton, then use corrected frames and regional masks as
initialization while increasing initialization strength. It also describes
preserving two neighbors and generating a gap. This is a useful workflow
reference, not evidence about private server weights or architecture.

Its [current API/OpenAPI](https://api.pixellab.ai/v2/docs) has different public
contracts. The inspected `animate-with-skeleton-v3` accepts one appearance
reference, a matching reference skeleton and3–15 ordered18-joint target poses,
up to256px. It does not expose init-image/mask/frozen-frame fields; the older
`animate-with-skeleton` does. `interpolation-v2` exposes start/end images and an
action, with16–128px in the inspected request schema. For `edit-animation-v2`,
the prose limits larger images to four frames although its generic frames
array permits more. Follow the relevant endpoint/schema rather than treating
all editor, marketing and API options as one interchangeable grammar.

These are verified-current **undated** docs, not publications from a claimed
recent date window. The separate PixMiniMax route is advertised as H3; a
no-H3 instruction excludes it. This does not identify other endpoints' models.

## Adapt the discipline, not imaginary controls

The built-in ImageGen tool does not supply that skeleton API, temporal state,
initialization-strength knob or a hard pixel lock. Preserve approved PNGs in
the local compositor. Request a missing coherent pose with its two actual
neighbors, appearance reference and a filled limb-volume guide. Keep every
input's role explicit. Check returned hip→knee→cuff→sole chains and leading/
lifted leg roles before producing bridges; filenames and requested coordinates
do not establish compliance. Newly exposed boot planes need actual paint.

A measured Rowan test returned a clean-looking single pose at1254square, but
again kept the wrong boot forward for the intended gap. One entire nearest
conversion to128 retained the shared stage; the pose was excluded before
whole-cycle or engine packaging. Increasing prompt detail was not a solution
to a misleading/ambiguous volume guide. Keep raw alpha, including unwanted
islands, before any explicitly reviewed cleanup.

## Test interpolation cheaply before expansion

Classical dense optical flow is not a generative model. It estimates apparent
image displacement and does not identify anatomy or an occlusion schedule.
In one bounded Rowan pilot, DIS and Farneback each produced a source-selected
and a premultiplied-blend variant. Four subframes preserved every original key
at the same start time and the0.45s cycle. Source selection plus alpha0 hole
fill produced pinched/speckled boot contours; blending produced double or
translucent soles near03→04. All four were excluded at the drawing gate.
This rejects those exact methods/parameters, not all interpolation research.

Use [OpenCV's dense-flow convention](https://docs.opencv.org/5.0/main_modules/video_track.html)
and [inverse remap semantics](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html)
when implementing such a test. Preserve flow fields, parameters, alpha/color
mixing rules and raw inputs. Nearest donor sampling preserves colors but does
not guarantee volume, attachment or correct occlusion. More frames cannot
repair a missing alternate contact or a rigid upper body.

## Coordinate a small rig with replacement drawings

[Spine4.3's official release](https://en.esotericsoftware.com/blog/Spine-4.3-released)
describes coordinated animation controls, image swaps and draw order. The
reusable lesson is one phase clock for pelvis loading, opposing arms, complete
boot paths and deliberate limb ordering. Keep full shoe volumes; use a
replacement drawing when a required plane is absent instead of stretching
one narrow receding shoe into every role. Compare a full cycle at the intended
game scale before adding a larger rig or more exposures.

The [2026-05-04 Adaptive Interpolation-Synthesis paper](https://arxiv.org/abs/2605.02742)
uses deliberately scheduled keys with interpolation and synthesis in a3D
production workflow. It is a relevant principle, not a tested pixel-sprite
solution or a reason to install a local model. Report the domain gap.

Local evidence: `/home/astra/artifacts/emberwake-gait-design-director-v1/RESEARCH-NOTES.md`,
`emberwake-optical-flow-walk-v1/{METHOD.json,RESULT.md,build.py}` and
`emberwake-rowan-guided-bridges-v1/{REQUEST-03.json,RESULT-03.json}` under the
same artifacts root. These are excluded experiments, not art approvals.

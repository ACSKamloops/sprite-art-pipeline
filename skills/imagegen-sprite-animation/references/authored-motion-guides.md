# Authored motion as an ImageGen pose guide

Use this route when a painted action repeatedly lacks linked pelvis, knees,
feet and hand support, and the user has authorized a licensed 3D reference.
The authored motion supplies geometry, not the character's appearance or a
recovered private provider implementation. Built-in ImageGen still supplies
the new paint; explicit source-part and pixel edits remain separate operations.

## Establish the actual source action

Check the selected source files, action names, time samples, root-motion mode,
license and actual poses. A store page's total animation count does not prove
the downloaded free tier contains the needed clip. Save the archive/member
hashes and included license. Do not depend on a transient signed download URL.

In the tested local case, the official
[Quaternius UAL2 distribution](https://quaternius.itch.io/universal-animation-library-2)
and included license identify CC0. The Standard non-root-motion GLB really has
`LayToIdle`:47 source samples, nominal30Hz, ending at46/30 seconds. The endpoint
is not47/30 seconds. The site's130-plus count covers a larger product; the
downloaded file actually contains43 action names. Source data wins over
marketing counts for a reconstruction claim.

Inspect first/middle/last and support changes before choosing it. This clip is
supine→hands-behind supported seat→feet-loaded squat→stand. The hero's actual
downed pixels show his chest and face upward. Earlier notes loosely called the
same pose prone; that label was corrected rather than forcing a different
choreography. A mismatched prone/chair/kneeling recovery needs a different clip
or an explicit compatible transition.

## Change proportions explicitly and project once

The standalone helper is [render_motion_guide.py](../scripts/render_motion_guide.py).
Copy [the generic config](../assets/motion-guide-config-template.json), supply a
licensed local GLB and license metadata/file, and set the actual imported
mesh/armature/action/bone names. Relative input paths resolve against that config.
It requires Blender with `bpy`, glTF import and CPU Cycles; ordinary Python is
insufficient. No model, network request, repository import or extra Python
package is needed. From this skill folder:

```bash
/path/to/blender --background --threads 4 --python-exit-code 1 \
  --python scripts/render_motion_guide.py -- \
  --config /path/to/my-guide-config.json \
  --output /existing/parent/fresh-guide-directory
```

The output directory must not exist, including as a symlink; its parent must
exist. An interrupted new directory can remain incomplete. Keep it diagnostically
and choose a fresh destination. Only a completed verification/hash receipt
establishes completion. The saved `.blend` embeds source-derived mesh, rig and
actions even though the raw GLB is not copied; retain the source license when
sharing it. The helper records supplied license assertions, not legal approval.

This helper is deliberately bounded to one configured skeletal mesh/armature,
one action slot, stable vertex indexing, a square stage and an optional keyed
leaf Head bone. It clears other scene-object animation. Extra animated objects,
NLA/constraint dependencies and arbitrary retargeting are unsupported assumptions.
It records geometry and actual alpha clipping separately; successful execution
does not automatically certify arbitrary camera near/far visibility or contact.

An adult mannequin is not the final sprite. Decide which source proportions
need changing and record the exact authored operations. Do not describe a
Head-only scale change as a full chibi retarget or physical contact correction.

The tested guide copies the source action and multiplies only the three
`Head` scale curves by2.05. Its other647 scalar curves, non-Head joint positions
and animated head pitch remain unchanged. Writing `pose_bone.scale` after
`frame_set()` was insufficient: later frame evaluation reset it. Editing the
copied action's declared scale keys made the change survive actual rendering.
The unmodified source action's hash is checked before/after.

Use one camera for the entire clip. Scan evaluated mesh bounds across all
frames before rendering, then check actual rendered alpha as well. Geometric
bounds and raster alpha are distinct. Do not independently crop, fit, shift or
recenter individual poses to make them look registered.

This solve calibrates one action with a genuinely standing reference frame.
Do not independently fit a crouched run, attack and idle to the same target
height: that changes character scale between actions. A broader bank needs one
shared character/camera calibration across those actions, with bounds checked
again and failures retained. The bundled helper has not established that
multi-action calibration or arbitrary retarget support.

The local solve targets64px standing geometry on an80×80 stage, with a declared
2D sprite pivot(40,72). Its fixed camera projects the rig world origin near
(40,67.72), while the standing visual sole reference is row71. World rig origin,
2D ground pivot and visual sole are different quantities. Forcing all three to
row72 initially shrank the standing guide to52px. A single shared camera
reanchor solved the fit; per-pose fitting did not. The final Head-weighted
geometric owner projects to about19.46px height, not a guaranteed rendered
hair/face size. All47 geometry bounds and actual alpha masks fit the stage.

The original portable helper was actually tested on all47 frames in Blender
4.5.14 LTS with four CPU threads. Its geometry/joint paths match the prototype;
a tiny shared horizontal camera correction means its raster is **not** identical
(at most18 RGBA channels and two alpha pixels differ per frame). The subsequent
audited revision corrects source-asset provenance and rejects11 malformed-config
cases before import/output/render. A fresh three-frame0/23/46 run verified that
revision's exact sampled geometry and3/647 curve invariant. It was not rerun on
all47 frames. The source asset is not bundled here. Extrapolation beyond the
actual stored action interval defaults off and requires an explicit config flag;
in-range interpolated samples need not be literal source keys.

[The bundled check summary](../assets/motion-guide-checks.json) pins both helper
revisions, the official source hashes, tested frame scopes and fixture replay.
It summarizes actual local receipts; it does not bundle the source GLB or claim
the revised helper was rerun on all47 frames.

Retain the `.blend`, exact camera, joint samples, edited-curve receipt, source
hashes and render configuration. A featureless clay head is only a position and
pitch guide; the canonical hero supplies hairstyle, face, scarf and materials.

## Feed separate appearance, geometry and endpoint references

Save the exact ordered inputs and prompt before generation:

1. Canonical character appearance at the actual native proportions.
2. Connected whole-body geometry at the declared stage/grid, without labels,
   margins or inset framing unless the import explicitly accounts for them.
3. Actual downed/neutral endpoints as context, if they help define the action.

Ask for the complete connected figure and the intended support sequence.
Coordinates and a visual guide are constraints to verify against returned
pixels; neither guarantees model compliance. Do not restore a static canonical
head before checking whether the pose requires a different pitch or occlusion.

The tested call requested six middle poses, source frames4,10,17,25,33,41, in a
1280×1920 sheet with640px cells. Its actual return was1024×1536 with512px cells.
Raw alpha ranged0..254, with no fully opaque pixels and a partial-alpha halo.
The raw request, refs, output and actual measurements are retained. No local
segmentation model was used to replace these diagnostics.

## Recover a cell intrusion without hidden fitting

Cropping nominal cells clipped the last crown and placed its39px native
fragment below the preceding pose. A uniform translation could not fix it
without clipping early boots. Keep that failed literal import.

The bounded successful import used the following explicit operations:

- Compare binary alpha thresholds128 and200 at native resolution. Threshold200
  reduced the actual halo; this case choice is not a universal default.
- Label connected characters in the **full raw image**. This return has exactly
  six connected components at200, all assigned to the six characters. Check
  real disconnected details before applying this method to another sheet.
- Retain original512-cell origins, but sample with overscan from the declared
  full-image character owner, even where it crosses the nominal cell boundary.
  A neighbor's crown belongs to that neighbor, not to the crop containing it.
- Use one common0.90 scale about native pivot(40,72), with zero additional
  per-key shifts. The shared extra margin recovers the crown and reduces all
  six new figures together. It is an authored global rescale, not unchanged
  guide compliance or independent bbox normalization.

For destination pixel coordinate `d`, source cell origin `o`, pivot `p` and
512px raw cells mapped to80px native stages, inverse nearest-center sampling is:

```text
raw_xy = o + floor((((d + 0.5 - p) * 10/9) + p) * 512/80)
```

Retain the sample only when its full-image component equals that key's declared
owner; otherwise write transparent RGBA. Save owner masks, inverse XY maps,
threshold decisions and actual output hashes. All six complete projected owners
fit, no output touches the stage border, and each native character remains one
8-connected component. These are import facts, not proof of anatomy, contact,
camera compliance or good motion. Missing source paint cannot be recovered by
this overscan method.

## Separate clocks and compare complete designs

The source clock is frame/30. The first eight-key paint study uses endpoints
0/46 and the six selected middle frames at frame/40, plus a final0.05s hold:

```text
onsets: 0, .1, .25, .425, .625, .825, 1.025, 1.15
holds: .1, .15, .175, .2, .2, .2, .125, .05
total: 1.2 seconds
```

That is an authored0.75-times source-duration proposal, not source metadata or
accepted animation timing. Exact old downed/neutral pixels bookend six new
painted figures. The comparison retimes the old ten-key action uniformly from
0.8 to1.2 seconds. It compares complete pose/timing designs; it does not isolate
drawing as the only changed variable. Fair added-bridge tests instead preserve
old key onsets and compare a repeated-key control in the identical new slot.

A fresh blind review inspected all18 poses and16 adjacent pairs, native/2x and
light/dark. The new design was preferred7.5 overall versus6 for the retimed old
design. Identity was8 for both. The new04→05 still skips a convincing hand-to-foot
load transfer;02 boots clump;06→07 changes head/torso during settling. These are
scoped ordered-still judgments, not continuous playback or a9/10 pass. Preserve
those faults for the next bounded edit; additional frames alone earn no points.

The next source-part test split the04 hold to insert a.725s upper lift with
complete source boots fixed, plus a separate1.0875s settling key. A blind2×2
comparison kept every old onset and the same1.2s clock. It preferred the support
key modestly; the first settle key improved head timing but pinched a knee/cuff
cluster. That settle remained unselected despite exact source replay and
complete rigid boot rectangles. Protecting only a boot does not protect the
entire calf/knee silhouette. A follow-up therefore locks the whole lower body,
not just the distal plateau. A fresh three-way comparison preferred that
lower-protected settle narrowly7.2 versus the older settle7.1 and repeat control7.
It retained the shared whole-action support/boot/entry limitations. Scores from
these different packets are not added or averaged into a progress score.

The portable `assets/source-settle-fixture/` contains the final small source
warp, source PNG, frozen map, expected RGBA and provenance. Its whole upper moves
rigid(-3,+2), the entire lower body from row53 remains literal, and only the
intervening waist deforms. Both replay and rebake were tested. This is a usable
pixel-transport example, not a claim of9/10 animation or an anatomical rig.

## Local evidence and delivery boundary

Case root: `/home/astra/artifacts/hero-action-set-20261022/quality-round3/`.
`getup-reference-scout/` pins official source/license/clip data;
`professional-getup-guide/` retains the47-frame guide;
`professional-getup-paint/` retains actual inputs/raw/imports;
`professional-getup-comparison/` holds the duration-matched old control;
`review-professional-motion-independent/` freezes the anonymous review.
`professional-support-repair/`, `professional-settle-bridge/` and
`professional-settle-upper-only/` preserve the successful and rejected part
studies. `review-combined-bridges-independent/` and
`review-settle-refinement-independent/` bind their separate visual judgments.
The latest local `package-v4/` selects the new get-up provisionally;135 other
bindings preserve v3 pixels, rational holds, events and loops. Fresh v4 editor,
Godot resource/input, native exported-PCK and actual WebAssembly receipts are
distinct from those art reviews. The whole library still lacks9/10 acceptance.
These local case programs are not a bundled reconstruction of the source GLB.
The provider's private model, weights and hidden processing remain unavailable.
No H3, local generative model or paid-provider request was used.

A portable repository copy now lives in
[the current hero example](https://github.com/ACSKamloops/sprite-art-pipeline/tree/main/examples/current-hero).
Its recovery study includes the actual ordered inputs, prompt/raw, frozen
sampling/ownership maps and guarded support-key journal. The supplied replay
rebuilds all ten selected frames and rational holds without the original
workstation or a new model call. Other historical raw experiments remain local.

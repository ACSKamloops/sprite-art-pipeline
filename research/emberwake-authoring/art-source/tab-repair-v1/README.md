# Brann waist-tab continuity candidate

This isolated repair targets the red-orange hanging waist tab that turned into a short gold split ornament across otherwise compatible neutral/action cels. The original source is `art-source/characters-v2/bake-v1/brann/atlas.png` in the main Emberwake project. It was read only. No runtime atlas, manifest, gameplay code, source paint or generated walk was modified by this task.

**Selected candidate:** `selected-candidate/atlas.png`, SHA-256 `01d5c3b1a3e9b2ab210594b721d50e3b14813ecf61bf0d7fc314fedb9aa51b02`.

This is a candidate for independent art review, not an 8/10 certification. The preservation checks below cannot establish convincing fabric motion or anatomical shading. Review the actual-timing APNGs, the four complete action-bank waist comparisons, and the representative whole-body pairs.

## What was inspected and changed

All 112 waist cels were inspected against the provided four-direction waist contact sheets. Complete silhouettes and enlarged native-pixel grids were inspected for representative donors and targets. The original 32 walk cels are explicitly excluded because the root artist is producing replacement walks separately.

27 original neutral/action/recovery cels received 3,738 changed RGBA pixels. The other 53 action cels retain their original artwork. There are no body resizes, warps, palette transformations, filters, model calls or inferred limb rigs.

| Facing | Frozen donor | Targets |
| --- | --- | --- |
| South | f12, a coherent red tab on an unarmed attack pose | 8, 14–21, 27 |
| East | f37, a coherent red tab on an anticipation pose | 42, 44, 48, 51, 55 |
| North | f71, the existing red-tab neutral pose | 68, 70, 72, 77, 79, 80, 83 |
| West | f93, its existing own painted mirror of east f37 | 98, 100, 104, 107, 111 |

The tab remains red cloth with the donor's existing gold edging. Literal small row masks copy the donor's complete RGBA texels at declared integer offsets. Their boundary includes a few compatible immediate waist/pants texels where the previous gold fork needed underpaint replacement. Pixels outside each mask stay exactly unchanged, including the belt, torso, limbs, gloves and transparent surroundings. No opaque source pixel was erased to zero alpha. Already coherent red tabs and poses with ambiguous hand/waist occlusion were retained rather than painting through a glove.

The original west bank was already a mirrored east bank, shifted one native pixel. The repair copies **west's own original donor pixels**, with matching mirrored masks/offsets. All five modified east/west pairs retain their existing mirror relationship; this does not claim an independently authored west bank.

`repair-plan.json` is the literal editable specification: donor/target cel hashes, per-row `[y,x0,x1_exclusive]` masks and per-target integer offsets. Unused first-draft mask entries are historical context only; the selected operations use f12/f37/f71/f93. `selected-candidate/source-maps.json` records every target pixel and its exact donor/source coordinate. `receipt.json` includes every actually changed coordinate and before/after RGBA value, all 112 cel hashes, and per-frame preservation assertions.

The first draft used the smaller neutral/cast side donors and left too much pointed gold-fork appearance. `candidate-v1/` and `repair-plan-first-draft.json` retain that failed choice. `candidate-v2/` is the selected pixel result before adding timed proofs; its atlas equals `selected-candidate/atlas.png`. The two inspection PNGs retain the working full-character and coordinate-grid evidence.

## Reproduce and integrate

Requires Python and Pillow. Run from the Emberwake project after copying this folder, using a **fresh** output directory:

```sh
python art-source/tab-repair-v1/repair_tabs.py \
  --source art-source/characters-v2/bake-v1/brann/atlas.png \
  --output art-source/tab-repair-v1/replay-fresh

python art-source/tab-repair-v1/verify_repair.py \
  --source art-source/characters-v2/bake-v1/brann/atlas.png \
  --candidate art-source/tab-repair-v1/replay-fresh
```

For the root baker, import `apply_tab_repairs(atlas_image, plan_dict) -> (candidate_image, receipt_dict)`. This leaves the input image intact. Both donor and target **original action-cel RGBA hashes** are preconditions. The whole original PNG hash is recorded for provenance; it is deliberately not the mutation guard, so changing only walk cels can coexist with this action-bank patch. Changing a donor or target action cel rejects; do not disable the guard. Review/rebase the literal masks and source maps if that paint changes.

The CLI optionally reads the source atlas's sibling `animations.json` for timed comparisons. It uses those exact nonwalk frame orders and holds. Each APNG is an 8.42-second state-transition comparison, including neutral holds, attack, cast, hurt, dodge and recovery. It is a comparison fixture, not footage of a playable character controller. No missing motion key or better gait is claimed.

## Verification and remaining review

`verification.json` records 47 successful preservation/replay checks:

- Independent reconstruction from the frozen point maps reproduces the selected candidate RGBA exactly.
- Every changed pixel belongs to the declared target mask and copies its frozen donor RGBA.
- All 32 original walk cels stay unchanged.
- Literal plan replay matches the selected candidate.
- Edited target and donor input cels reject without mutating the supplied image.
- A deliberate walk-only input change remains intact while the action repair stays identical. This checks the integration boundary; it did not test the root's new generated walk assets.
- All five repaired east/west pairs preserve the existing mirrored staging.

The selected tab shape is reused paint, translated to each projected waist. It does not add independent cloth dynamics. Some unmodified action tabs retain their original fold/length differences, and gloves can occlude the tab. The task's independent reviewer must decide whether those differences remain distracting during the full action transitions and when the new walks join them. Normal-speed game rendering and character quality ratings are pending root integration and review.

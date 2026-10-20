# Extend one approved character into a common RPG action library

Separate source actions, logical gameplay states, authored views and final acceptance. A current east three-quarter batch is useful preparation for a top-down RPG, but does not supply north/south/west art. Ground XY movement/Y-sort can already be top-down while the artwork still has one view.

## Scope and dependencies

An example common body-action matrix: idle, combat idle, walk, run, punch, kick, melee swing/thrust, guard, crouch, dodge, hurt, stagger, cast, jump, interact, pickup, item use, talk, victory, sit, stand-up, knockdown and get-up. Choose actions appropriate to the game; climbing, swimming and tools are conditional extensions. A terminal death may reuse a disclosed downed pose rather than claiming another unique drawing sequence.

Split held actions into enter/hold/exit; casting into prepare/channel/release; sitting into sit-down/sitting; knockdown into fall/downed. Jump takeoff/air/landing need actual contact/height calibration before becoming physical states. More state names do not mean more authored art. Keep equipment, hit windows and VFX independent; empty-hand swing art alone does not establish measured per-frame weapon anchors.

Standing-to-seated and seated-to-standing are dependent painting inputs: inspect the returned seated endpoint, retain its exact source index/hash, prepare a fixed-stage appearance reference from it, then submit stand-up with that entry. Likewise downed→get-up. A standing reference can contaminate seated/downed entry. If the preceding paint is unavailable, freeze the guide but leave dependent paint unprepared.

## Author, paint and retain

1. Freeze approved PNG bytes, source timing, shared neutral, camera, body proportions, fixed stage and nominal pivot. An approval quote must bind exact assets and scope; it supplies no invented numeric score.
2. Author strongest keys and inspect them first. Keep physical boot geometry/arm chains fixed, and orient the head basis with a leaning/lying torso. Get-up needs supported hand brace, tucked legs, crouch and rise; reversing a rigid fall failed motion review.
3. Bake the actual guide at its declared clock; decode the encoded transport and verify every pose, dimensions and actual PTS. Dense geometry checks do not establish attractive motion or painted anatomy.
4. A guide plus separate appearance image can condition a video model. Retain exact input bytes, literal prompt, sanitized request fields, request hash, durable submission state, native return and all decoded timestamps. Never assume output frame count/duration equals the requested guide. A five-second example returned124 frames at24Hz, duration31/6s.
5. Inspect every native returned pose and every changed adjacency on light/dark/color backgrounds, including loop wrap. Matte selection is independent: one return ignored green and used black. Edge-connected black removal preserves enclosed dark details but cannot recover unknown true black contours. Preserve original RGB and sensitivity witnesses.
6. Make explicit ordered source-index/hold selections to remove lead-ins or held plateaus. Retiming is authored playback, not original native chronology. Do not omit intervening recovery poses just to shorten a clip: a demonstrated cast85→105 skip snapped both hands to ready in1/24s; restore and inspect the missing recovery.
7. If model body scale drifts, compare head/hair/torso against baseline at comparable poses. Use one documented whole-clip nearest transform, fixed pivot and constant translation, preserve raw originals and source-texel mapping/replay/undo. Do not fit each pose or infer body scale from action-dependent bounding-box height.
8. Export source-byte PNGs and exact-delay APNG; keep editable flat-cel projects, actual LibreSprite save/reopen/import proof, atlas-cell comparisons and exact timing sidecars. Editable tools may canonicalize only hidden RGB beneath alpha0; disclose that independently of unchanged authoritative source PNG bytes.

Every manifest file pointer must resolve against its declared base and match its hash, including video, recipe, sample mapping, matte/raw/upstream PNGs and unregistered originals. A valid visible frame list can still hide broken lineage pointers. Bundle evidence or declare an external dependency; after a metadata-only repair, preserve the original manifest and rebind reviews/exports without suggesting the art changed.

Exact render reuse can accelerate guides: reuse only truly identical geometry with a witness for all render inputs, including camera/head basis and actual floating precision used by transforms/meshes. Do not merge merely close poses. Blender `-t8` did not bound Mesa llvmpipe workers in this case: steady process threads were90 until LP_NUM_THREADS=4, OMP_NUM_THREADS/OMP_THREAD_LIMIT=8 and BLAS caps reduced them to34. Sample steady process thread count rather than trusting a CLI flag; these counts are machine-specific.

## Godot state clock and held input

Use positive rational holds. LCM of hold denominators gives the exact tick rate; SpriteFrames frame weights are integer ticks. Preserve rates when moving between clips.

A concrete bug reset fractional time when an automatic transition called request(), dropping sub-tick carry at mixed rates. Capture `(whole_leftover + fractional_ticks)/old_hz` BEFORE restarting the new action, then multiply by new_hz and split whole/fractional ticks. Carry through chained transitions and ordinary completion returns. Explicit new input may intentionally reset phase.

Releasing guard/crouch/cast during its entry should complete the authored entry before taking the appropriate exit/release. Jumping immediately to exit mid-entry caused a pose discontinuity. Release during hold can start exit; repress during exit can buffer entry. Interruptions clear held input/buffer. Unavailable directions and terminal states reject new actions without arming invisible held input. Key-up must still clear a previously held input after a missing-view request; complete its exit in the already-displayed view without inventing unavailable-view artwork. A concrete audit found that validating the new facing before clearing release caused a stuck held state;19 added assertions cover late/early releases, same-view lifecycle completion and terminal flag cleanup.

The bundled [Godot clock fixture](../assets/rpg-runtime-clock-fixture/) contains actual tested actor/clock and synthetic1px tests:6 fractional-carry assertions plus48 held-input assertions. Copy it to a fresh writable directory, create its evidence folder and run with an installed Godot4.x executable:

```sh
fixture_run=$(mktemp -d /tmp/rpg-clock-test-XXXXXX)
cp -a assets/rpg-runtime-clock-fixture/. "$fixture_run/"
mkdir -p "$fixture_run/evidence"
godot --headless --path "$fixture_run" --script test_fractional.gd
godot --headless --path "$fixture_run" --script test_held.gd
```

Use a unique temporary path for repeated/parallel work. These tests prove input/clock behavior, not rendered-art quality. For production art, also run actual resource save/reload, every frame's decoded PNG hash, imported RGBA, clock boundaries/wrap/one-shot freezes, actual renderer readback, collision/Y-sort and representative transitions. A software llvmpipe rendering pass is not hardware-GPU proof.

For top-down staging use CharacterBody2D floating mode, root XY for collision/Y-sort, and a separate visual-height child/shadow. When a jump is already baked into the pixels, adding procedural sprite height doubles the visual jump. Baked previews do not prove physical takeoff/landing, root motion or damage windows.

## Honest temporal review

A clean drawing is insufficient: an8.5 drawing score coexisted with a6.7 motion score when hurt resembled a guard. Stronger guide head/chest recoil and a brief pained face improved readability, then still needed hold shortening. Independent reviewers should receive exact images/clocks and desired action, not producer scores; disclose any selection rationale they necessarily see. Confirm repair from actual source pixels if a reviewer reports a blank/missing pose; preserve the erroneous review and a separate correction witness.

Frame sheets and PTS checks provide chronological still inspection and playback-mechanics evidence. Human normal-speed viewing remains a separate acceptance gate. Keep scores truthful; passing mechanics or an enthusiastic user response does not manufacture9/10.

Evidence case: `/home/astra/projects/rpg-hero-animation/work/rpg-library-v1/` with action plan in `actions/library-plan-v1.json`, literal prompt/reference/transport jobs under `providers/minimax_h3/jobs/`, and separate frozen source guides, painted packages, independent reviews and runtime evidence. The case does not recover private PixelLab/model inference internals. Provider usage exhaustion is a missing-paint state, not a reason to substitute primitive guides as finished artwork.

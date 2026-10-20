# Same hero: first attack and jump

Status: **PLANNED ONLY. No new art, clips, guide, API request, engine code or approval was produced here.** The user confirmed **both first actions are unarmed**: one same-view straight punch and one small jump. Future interchangeable weapons use separate attachment tracks; they are not baked into the body animation. An equipped action needs compatible body motion and equipment-ready transitions. Other abilities, views and characters remain backlog.

## Accepted source and fixed appearance

The user explicitly approved this H3 walk. Current acceptance is `approvals/walk.user.json`; paths in this document are project-root relative. The portable authority is `approved/walk/manifest.json`, SHA256 `89666748bc27c9f67fb13faf229b56a777907566681b00ee229c31c23fa1d8af`. The original authority remains byte-exact in `evidence/original-walk-manifest.json`, SHA256 `975b6e31a5bab96391ba4045544d62e737a9b4a68a9f78086c243bfe24f212df`. Both describe the same30 original128×128 PNGs at1/24s, period5/4s. Preserve those bytes and holds; acceptance covers only this walk/view, not physical contact, idle, attack, jump or all transitions.

Appearance authority for new actions is the selected walk and `references/action-reference192.png`, which preserves approved H3 frame00 at constant padding(+32,+64); it is not a newly approved idle. `references/submitted-appearance384.png` retains the exact older DS-derived provider input as historical provenance, rather than replacing the approved H3 design.

Keep the young brown-haired, blue-eyed hero, tousled hair, blue coat/gold trim, silver shoulder armor and wrist bracers, cream trousers, brown gloves and complete brown boots. Preserve body/head proportions, coat construction and ornament placement, hand/boot mass, light direction, palette/material separation and crisp native pixel clusters. Use the same orthographic three-quarter right-facing camera, constant scale and fixed registration; do not mirror to invent another view. No weapon, accessories, scene or baked shadow belongs in these first body clips. Hidden surfaces exposed by an action need deliberately authored paint, not claims of recovered walk anatomy.

## Measured margins and fixed new-action canvas

All30 selected EO alpha bboxes were measured in the unchanged128 canvas. Their half-open union is `[41,15,91,111]` (50px wide,96px tall); individual hair tops range15–19 and bottoms108–111. Frame00 bbox is `[41,18,89,110]`. Thus only15px of top margin is guaranteed across the walk; the nominal ground pivot `[64,106]` is an inherited registration anchor, not proof that a rendered sole lies on a horizontal floor.

Use **one fixed192×192 canvas for both new action pilots and their new neutral/transition art**, keeping the original painted scale. Map source128 into it by constant padding `(+32,+64)`, giving nominal pivot `[96,170]`. The measured walk union would then be `[73,79,123,175]`, with79px top,73px left,69px right and17px bottom margin. Keep the approved walk128 files unchanged; the consumer aligns clips through their declared ground pivots, never through independently fitted bboxes. These padded extents are a framing calculation, not newly produced art.

Reserve the same fixed horizontal margins for punch reach, hand follow-through and any later equipment. The first clip is unarmed; a future weapon guide must contain every tip/trail extent with at least4px clear border at all phases before adoption. No tip cropping or whole-body shrink is an acceptable fix. Jump height moves the body relative to the single ground root on this padded stage; no per-pose world-root offset is prescribed to improve framing. Evaluate every authored crouch, extension, airborne and landing bbox before export, since new silhouettes can exceed the walk union.

## Choose the construction route for the actual missing motion

| Route | Useful role | Limit for these actions |
|---|---|---|
| Source-painted parts | Reuse literal costume/detail paint for short coherent arcs and guarded repairs; retain donor coordinates, masks and literal edit journals. | Walk cutouts are not a complete rig. Unknown pelvis/hem seams, missing underpaint and ambiguous limb labels cannot supply a punch torso twist or a crouched/airborne body. Reject stretched armor, cutout elbows and detached boot seams even when source sampling is exact. |
| Newly authored key poses | Draw the neutral, loaded punch, full extension/recoil, crouch, takeoff, apex and landing silhouettes deliberately; preserve reference identity and explicitly author newly visible anatomy. | Attractive individual keys need adjacent-pair and timed review. Filling between them by warping can repeat the failed seam/ownership assumptions. Every new key is PLANNED until produced and reviewed. |
| Complete motion guide plus appearance reference | Preferred starting experiment for genuinely new whole-body actions: author a small camera-matched guide with body mechanics, root/height and contact, then use the accepted hero only as appearance authority. | A guide is motion intent, not proof that painted output follows it. Provider transport, resulting geometry, paint, timing, contact and user acceptance need separate evidence. A mannequin is not a recovered hero model. No call is authorized or made by this planning artifact. |

Begin with a small key/guide gate, not a full ability library. Approve the neutral and strongest anticipation/extension/landing silhouettes at native size before filling complete clips. Keep a single complete action binding in each editable project, with source hashes, ordered holds, named layers and exact export sidecars. New source/guide edits invalidate dependent bakes and reviews; literal cel repairs need replay, undo and outside-mask guards.

## First attack: unarmed straight punch

Provisional direction: the foreground/near gloved fist strikes along the hero's existing right-facing three-quarter line. Rear glove guards; both shoulders, hips and weight transfer contribute. Do not substitute a screen-right arm stretch for an aimed whole-body attack. Keep readable lead support, rear heel release if used, and a clear recoil before the body returns to neutral.

The following is an **authored timing proposal, not existing footage**:10 unique pose slots over18 ticks at24Hz (3/4s), one-shot. Phase tick ranges are half-open.

| Phase | Proposed ticks | Proposed distinct pose slots | Required reading |
|---|---:|---:|---|
| Ready entry |0–2|1|Neutral compatible with planned idle; fist guard and support visible.|
| Anticipation |2–6|2|Load rear leg/hip; elbow retracts; torso prepares without shrinking costume.|
| Strike |6–8|2|Short acceleration into full extension; fist arc and shoulder chain readable.|
| Follow-through |8–10|1|Weight catches; no hitbox left active after withdrawal begins.|
| Recovery |10–16|3|Retract fist, restore balance and guard; avoid instantaneous extended-fist reset.|
| Settle/exit |16–18|1|Return to the same authored neutral endpoint; unlock queued action at documented exit.|

Proposed events: `attack_enter`/lock at0; `hit_start` at6; `hit_end` at8; `recovery_open` at16; `action_complete` at18. Gameplay events are authored proposals, not native triggers. Hit volume follows a separate fist anchor and collision definition; artwork alpha is not the hitbox. No projectile, combo or trail is required. Optional impact/audio runs on its own effect instance and clock after a confirmed collision, not by recoloring fused body pixels.

First pilot is stationary: physical ground root remains fixed; visible hip/torso loading occurs in the pose. A lunge is a separate later root-motion variant consumed through collision, not a sprite-origin slide. Facing is locked for the action. Movement/jump/another attack queues at most the latest legal request and starts after tick18; no repeated restart while the attack button is held. Initial pilot has no voluntary mid-strike cancel. A hurt/death interruption must close the active hitbox immediately, clear owned effects and enter an explicit supported state; those art bindings remain backlog and must not silently display an unrelated pose.

## First jump: small in-place hop with landing

Use a crouch/load, forceful takeoff, rising tuck, readable apex, descending reach, landing compression and recovery. Both legs remain attached and anatomically tracked through overlap. The coat/hair follow-through changes with acceleration; never freeze the entire body while moving a flat walk cel upward.

Provisional nominal preview:12 unique pose slots over24 ticks at24Hz (1s), one-shot: crouch0–4 (2 slots), takeoff4–6 (1), rise6–11 (2), apex11–13 (1), fall13–18 (2), landing compression18–22 (2), settle22–24 (2). These are **guide/storyboard proposals**, not a fixed gameplay landing schedule. Rise/apex/fall select by physical vertical state; touchdown can occur earlier/later due to terrain or collision. Do not force the actor to wait at an apex pose until a nominal timer expires.

Separate coordinates: `ground_root` moves on the gameplay ground plane and owns collision/navigation/depth sorting; `height` is a nonnegative airborne offset above that root; the rendered body projects both through the same camera. For a simple screen-up height projection, final draw origin derives from projected ground root minus height, source pivot and any declared presentation bias, then rounds once. Record a different projection explicitly if used. The ground shadow/contact marker follows `ground_root`, not airborne body, and has an independent layer/state. Neither sprite canvas nor boot centroid is the physical root.

First pilot keeps ground_root stationary. A nominal guide height of16 native pixels is a **provisional framing proposal** only; choose impulse/gravity consistently once the runtime units are known. Use the fixed192 action stage and `[96,170]` pivot specified above; keep full hair/hands/boots clear at every state. The16px nominal height would move the measured rest union top79 to63, before pose deformation. Check actual new-pose extents, including hands above the head. If a later action still exceeds this stage, revise one shared action-canvas contract deliberately and revalidate transitions; preserve walk source bytes/scale. Never shrink, recenter or change the world root independently for individual airborne poses.

Proposed state events: `jump_enter`/lock at crouch start; `takeoff` once at guide tick4, setting height velocity and ending ground support; `apex_crossed` once when vertical velocity changes from up to down; `land_contact` once on actual descending ground collision; `land_recover_open` after4 landing ticks; `action_complete` after6 landing ticks. Nominal touchdown is tick18 only in the storyboard. No double-jump, aerial attack, variable jump, wall jump or coyote-time promise is made. Initial pilot queues movement/attack until landing recovery completes. Reset/interruption clears airborne effect ownership and uses a documented physical landing/reset policy; it must not teleport to idle midair.

## Adjacent clips needed before playable promotion

A walk loop alone supplies no approved idle or attack guard. Plan a same-view neutral idle/ready pose and its action endpoints first. Review neutral→attack-ready→anticipation, full-extension→recovery→neutral, neutral→crouch→takeoff, rise→apex→fall, actual contact→landing compression→neutral, and every replay/completion seam. First/final neutral source equality can prevent a switch pop; intervening action art still needs visual review.

Walk→action needs an explicit stop/settle or a documented conservative support-phase entry policy, plus action→walk startup. Do not snap any arbitrary one of the30 walk poses to neutral and call that complete coverage. Bound the first playable pilot to stationary entries; any walk-input request waits for a supported exit and gets its latency measured. If arbitrary-phase interruption is later required, author and test a finite transition bank for every permitted entry, including fractional times. Preserve ground root/collision and declared draw bias through each switch. Other views, equipped guards, weapon swaps, hurt/fall/recover/death and combo branches remain separate backlog bindings.

## Planned validation and review

All checks below are future requirements, **not results**. Bind the new manifest/source/exports and review receipts to exact hashes; give each clip positive rational holds, explicit loop=false, phase/event definitions, pivots and completed/missing state coverage. Compare every neighbor, full extension/landing and return endpoints on native and2× dark/light/teal, with silhouette-only and isolated hands/feet/coat views. Provide normal-speed playback for the user; decoded sheets/known clocks do not mean continuous human viewing.

One simulation clock owns pose, physical motion and event boundaries. At60/30/15/10 render fps and a250ms hitch, process every crossed event in order even if several rendered poses are skipped. Test immediately before/at/after each boundary, hit_start+hit_end in one update, takeoff/apex/land once per action, completion, pause/resume, rate change, reset and buffered repeated input. No duplicate damage, stale hitbox, duplicate landing or effect leak may survive a cancel. Use collision sweeps or equivalent simulation coverage when rendering skips active strike poses; event delivery alone is not collision coverage. Cap exceptional catch-up explicitly without silently dropping gameplay events.

Verify actual source texture imports and rendered visible RGBA, constant camera/scale, clipping, pivot and final draw origin. Test actual sole material during grounded attack and landing support, including fractions within held cels, with raw moving/displaced-foot controls; an ankle target alone does not establish contact. Test jump body height separately from ground-root motion and shadow position. Re-run relevant contact/transition checks after paint or timing changes. Technical correctness and human art/motion approval remain separate gates.

## Local method references

Installed skills used for this plan: `/home/astra/.codex/skills/sprite-animation-pipeline/SKILL.md` and `/home/astra/.codex/skills/sprite-construction-editing/SKILL.md`. Focused references: animation `manifest.md`, `stateful-effects.md`, `adjacent-frame-review.md`, `locomotion-runtime-and-contact.md`, `human-playback-and-loop-diagnosis.md`; construction `source-paint-and-clip-editing.md`. The bundled `assets/clip_driver.gd` is an example of attack locking and crossed-frame events; it is not an implemented jump controller or an exact timing specification to copy without review. It uses a boundary epsilon, while the stricter clock guidance calls for exact cumulative boundaries and explicit roundoff handling.

## Future modular equipment

The user requests interchangeable weapons as separate attachment tracks. See `docs/equipment-tracks.md`, `actions/attachments.schema.json` and the hash-bound `actions/attachments.example.json`. Both first body actions remain unarmed. A held weapon, its grip/socket, damage volume and independent visual effects have separate authorities and lifetimes. Compatible weapon art may swap within an approved body motion profile; a punch never becomes a sword slash merely by attaching a sword. No attachment anchors, occlusion masks, equipment art or runtime implementation were produced here.

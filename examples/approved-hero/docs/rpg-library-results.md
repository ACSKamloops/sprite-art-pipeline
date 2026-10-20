# RPG hero action library: current delivery and handoff

The available batch contains18 action types in the existing east-three-quarter view. Held phases and casting splits make25 playback clips, plus a ready still. Original walk PNG bytes and timing remain unchanged. The user endorsed repaired punch/jump as the working baseline; new art has individual reviews, not a blanket9/10 approval.

Use [the local art player](http://localhost:8889/game-ready-v6/current-project/work/rpg-library-v1/review/index.html?clip=run) or [the self-contained Godot project](../exports/rpg-library-v1/godot/project.godot). [Delivery index](../exports/rpg-library-v1/DELIVERY-INDEX.json) and [source selection](../work/rpg-library-v1/catalog-selection.json) identify exact chosen inputs. The Godot project rebuilds from its own PNGs/manifests without the authoring workspace, provider credentials or API calls.

## Available art and its limits

- Movement: walk, small-stride run, relaxed idle, combat idle, jump.
- Combat: punch, short front kick, empty-hand swing/thrust, hurt, stagger, evasive lean/dodge, cast.
- Held poses: guard enter/hold/exit, shallow crouch enter/hold/exit, cast prepare/static channel/release.
- Interaction: reach/activate, talk loop, victory.

Every body clip remains unarmed. Equipment, grip/occlusion tracks, magic effects and damage windows are separate future work. Crouch is a shallow11px body lowering, not a deep squat. Dodge is restrained in-place body movement, not a calibrated dash or invulnerability action. Combat idle has a relatively busy native0.5s bob. Guard/crouch entry takes23/24s; that does not approve delayed block activation. Guard/crouch fine paint changes at wrap need human repeated-playback judgment. Jump has baked visual height; physical takeoff, air state, collision/contact and landing triggers are not calibrated. Ground-root movement is not automatically bound to walk/run or calibrated against sole travel.

Pickup, item use, sit, stand-up, knockdown and get-up have completed, verified guides but no painted output. H3 returned terminal error2056, Token Plan usage limit reached, for pickup/item-use/sit. Stand-up/get-up also require the preceding painted seated/downed entry references. Their missing paint is not replaced with primitive guide art. The user chose to finish available clips first; no further provider generation was submitted after that choice.

The plan view IDs `south_front`, `west` and `north_back` remain unavailable. Only `east`/right-three-quarter art is authored here. No silent mirror or missing-view fallback is counted. A requested unavailable view is shown as unavailable while the already-displayed east animation can finish its lifecycle.

## Selected sources and fine editing

- [Locomotion/held-state index](../work/rpg-library-v1/painted-locomotion-delivery/LOCOMOTION-DELIVERY-INDEX-v1.json):9 source state packages, raw alternatives, exact APNGs, atlas/project, actual LibreSprite save/reopen proof, fixed registration evidence.
- [Combat index](../work/rpg-library-v1/painted-combat-delivery/FINAL-SIX.json): kick, stagger, dodge, swing, thrust and repaired castV3. CastV2 is preserved as a rejected timing draft.
- [Repaired social index](../work/rpg-library-v1/painted-combat-delivery/social-repairs-v1/SOCIAL-REPAIRS-INDEX.json): talk77poses, interaction37, victory49, source bundles and editable masters. The earlier root social candidates remain historical drafts.
- [Hurt candidate](../work/rpg-library-v1/painted-hurt-delivery/hurt-v2-compact-candidate-v1/manifest.json), [editable source](../work/rpg-library-v1/painted-hurt-delivery/hurt-v2-compact-candidate-v1-editable-v1/project.json):17/24s light recoil, original full return retained.
- [Walk source](../approved/walk/manifest.json) and [first punch/jump editable handoff](../work/action-editable-delivery-v1/HANDOFF.md).

A flat editable body cel is not a recovered anatomical rig. Use project JSON/LibreSprite master with its exact timing sidecar for fine pixel editing. Authoritative selected PNG bytes remain intact; editable rendering may canonicalize hidden RGB only beneath alpha0, with visibleRGBA and allalpha verified separately. Whole-clip idle/run/victory registration preserves raw originals, fixed sample mapping, replay and undo. There is no per-pose fitting.

Victory's original returned-ready was105px high versus94px baseline. One constant9/10 nearest transform about[96,174], plus constant[0,1] translation, produces95px due raster rounding and aligns sole row177. All poses share that transform. Talk now includes ready→gesture→ready native21..97; interaction restores its omitted entry/recovery. These repairs do not redraw individual frames.

## Generation and evidence chain

The [action plan](../actions/library-plan-v1.json) covers21 new source actions plus the existing walk/punch/jump. Distinguish15 completed unique new painted action sources from16 successful native video returns: hurt was generated twice, withV2 selected. All21 new action guides exist; the stronger hurtV2 is an additional source revision.

Guides use a shared neutral/camera/proportion setup, authored articulated geometry and head orientation,160actual poses at32Hz over5seconds. Actual encoded transport is decoded and checked, including all actual PTS. Exact geometry reuse carries source witnesses rather than merging merely similar poses. Source renderer controls, poses, geometry checks, complete guide videos and separate root visual receipts are retained in the locomotion/combat/social_recovery folders.

H3 receives the retained ImageGen-derived neutral appearance image plus each reviewed moving guide and literal action prompt. The exact appearance image, guide, prompt, sanitized request, request hash, one-POST state, polling receipts and native video are retained under `providers/minimax_h3/jobs/library-*`. No token is included in the art export. Model output is stochastic; reconstructing a saved return is reproducible, repeating the API call is not guaranteed identical.

Each native return here has124poses at24Hz,31/6s, despite the five-second request. Retain the complete native sequence and timestamps before selecting/retiming. The tested bake uses one fixed source sampling map, retained source RGB, disclosed matte/despill edits and original source-index/hold lineage. Idle ignored the requested green background; its separate edge-connected black matte has retained threshold sensitivity evidence. That operation cannot recover unknown true-black contour alpha.

This is an authored guide plus appearance-conditioned video pipeline, informed by retained PixelLab research. It does not establish recovery of PixelLab's private model weights or inference internals.

## Quality review and repairs

Reviews bind exact input hashes and separate drawing, identity, motion, timing and usefulness. Chronological native/2x still inspection, all changed adjacencies and three backgrounds are recorded. Browser playback-state checks are separate from human normal-speed artistic acceptance.

The review folders under [social_recovery](../work/rpg-library-v1/social_recovery/) include original hurt, stronger hurtV2, compact confirmation, combat cohort, castV3, idle, run/combat-idle and held states. [Initial social review](../work/rpg-library-v1/painted-combat-delivery/social-independent-review-v1/REVIEW.md) exposed the talk loop reset, interaction cut and victory scale drift; those inputs remain preserved. A fresh separate reviewer rated repaired talk8.2, interaction8.2 and victory8.0; all163poses, changed pairs, talk wrap, three exactAPNGs and fixed registration were checked.

Useful current judgments include hurt compact8.5 (confirmatory reviewer had proposed the subset), idle8.3, run/combat-idle8.1, kick8.2, swing8.1, thrust8.0, stagger7.8, dodge7.3, repaired cast8.0. Guard phases rate8.1–8.2; shallow crouch7.5–7.8. The precise new social ratings and final input hashes are recorded in the delivery verification JSON. Scores are not raised to satisfy a target; this batch is ready for local human trial, not uniform9/10 production approval.

Concrete repairs demonstrated here:

1. HurtV1 resembled a guard. A stronger head/chest recoil guide and brief pained expression improved the return; explicit source-frame retiming shortened its long pain hold.
2. Cast skipped native85→105 and snapped both hands down. V3 restores every86..104 recovery pose; the52-frame13/6s clip passes the scoped review.
3. Guard hold initially included unfinished raising poses. Final entry18..40, hold41..103, exit104..119 keep the measured painted phases separate. Crouch uses18..40/41..101/102..118.
4. A missing `unregistered_png` lineage file was caught independently. Exact originals/source evidence are now bundled and receipts rebound without changing art pixels or APNG timing.
5. A mixed-rate Godot transition discarded fractional elapsed time. The fixed driver carries whole+fractional seconds across rates before resetting action state.
6. An unavailable-view request blocked key-up and left held inputs stuck. Key-up now clears flags regardless of requested view, then finishes only the current displayed view's lifecycle. New actions still reject unavailable directions.48regressions pass versus17failures before the repair.

## Runtime and reusable methods

Godot uses ground-root XY collision and Y-sort, a separate visual-height child/shadow, nearest texture sampling and exact rational source holds. The original importer disables alpha-border fixing/premultiplication and preserves sourceRGBA. The lab provides ordinary one-shot buffering/restart/freeze, held guard/crouch/cast, interruption, same-view cleanup and missing-art rejection. Terminal/event logic has synthetic fixtures; actual death artwork and actual hit/VFX windows are unavailable.

Final delivery verification passed3,070Godot assertions,828actual softwareOpenGL frame readbacks plus2Y-sort checks, and2,481Chromium frame/background comparisons across25clips. Browser additionally verifies every fetched sourcePNG byte hash and binds the tested catalog hash. See [the final verification receipt](../exports/rpg-library-v1/DELIVERY-VERIFICATION.json).

Run the portable project's `./verify.sh`. It rebuilds only from local source frames and manifests, imports resources, saves/reloads SpriteFrames, checks every importedRGBA/frame duration and clock boundary, exercises fractional and held inputs, and performs actual softwareOpenGL rendered readbacks plus Y-sort overlap checks. `GODOT_BIN` can select another installed executable; this delivery was tested on4.7.2.

The browser suite covers every selected frame over light/dark/teal backgrounds, scrub and1x/2x/4x controls, plus real elapsed-time one-shot/loop state checks in Chromium. Ordered still review and these mechanics checks do not equal human continuous-motion approval. Rendering here uses Mesa llvmpipe; no hardwareGPU-performance claim is made.

Updated skills: [sprite-animation-pipeline](../../../.codex/skills/sprite-animation-pipeline/SKILL.md), its [common RPG library reference](../../../.codex/skills/sprite-animation-pipeline/references/common-rpg-library.md), and [sprite-construction-editing](../../../.codex/skills/sprite-construction-editing/SKILL.md). The animation skill now bundles an isolated runnable54-assertion Godot clock/input fixture. [Skill update receipts](../work/rpg-library-v1/SKILL-UPDATE-EVIDENCE.json) bind the tested files.

## Continue from here

1. Human-review the available loops/actions at1x/2x and normal speed, including repeated guard/crouch wraps and cross-action entry/return. Prioritize weaker dodge/shallow-crouch performances and any paint shimmer. Preserve exact review inputs.
2. Calibrate gameplay ground speed, jump height/contact, block/hit/cancel windows and equipment anchors independently of painted body cels. A successful state-clock test supplies none of these timings automatically.
3. When H3 usage is available again and generation is authorized, resume the six unpainted actions from their retained guides. Known terminal quota failures need fresh hash-bound attempts; ambiguous submissions must not be retried. Generate seated/downed paint first, inspect and bind the matching entry references before stand-up/get-up.
4. Author front/back/west neutral and movement references before directional expansion. Establish anatomy, costume asymmetry and camera consistency in those views, then extend the same action/state matrix. Do not multiply incomplete single-view coverage into a claimed top-down library.

Source guides and authoring work remain under `work/rpg-library-v1`; the canonical tested engine delivery is `exports/rpg-library-v1/godot`. Old working exports/candidates are retained as evidence and are not the recommended entrypoint. Root-owned GET/offline monitors were stopped after all submitted jobs became terminal; the local art server remains available. No public Sites deployment was made.

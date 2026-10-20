# Animation acceptance and pose-cut specification

Review date: 2026-10-14 UTC. Branch baseline `9f8cec0`. This is an independent acceptance plan and local authoring proposal for the retained generic RPG hero, not a recovered private PixelLab mechanism or approved game art. No raster edits, source changes, provider calls, or inferred hit events were made.

## Decision

**Best current contained attack draft: PixelLab `pixellab-slash-margin-v2`, generated slots1–16.** It supplies transparent, contained blade poses and a readable anticipation/strike/recovery sequence. It is not releasable under the retained no-effects brief: slot6 contains a white sweep. Original `pixellab-slash-v1` also contains a sweep at6 and trailing arc at7. Margin is preferred for this editing exercise because its actor/blade have more framing room and its follow poses lack the conspicuous original-slot7 arc; this is a case-specific workflow judgment, not a model ranking. The margin input actor is75% of the original actor scale, so cross-case apparent size is not generation drift.

For walking, PixelLab's raw16 are the simpler transparent editing starting point; slots13–16 settle toward idle and should not be called a seamless locomotion loop. The local H3 `[16,64)` cycle is a plausible separate loop draft, not an accepted loop or native extraction rule. Do not compare a selected H3 cycle against the entire PixelLab output as if generation alone caused the cadence difference.

## Evidence and actual coverage

Fresh visual inspection: all16 generated frames in each PixelLab walk/original-slash/margin-slash checker page; all107 H3 margin frames in chronological pages00–06; H3 original slash and walk eight-sample pages. Previously retained full107-frame walk/original-slash reviews and selected native detail checks are reused with their explicit coverage bounds in `docs/provider-preparation/h3-rpg-pilot/`. Those earlier historical documents predate the completed matched runs; their old statements that no matched run existed are superseded by the completed comparison, not current facts.

Fresh mechanical verification: all321 decoded native PNG hashes and all51 returned PixelLab PNG hashes match their six source manifests. Across all48 generated PixelLab PNGs, no visible alpha touches a canvas border; this is an edge-contact screen, not proof of complete anatomy, correct grip, or good motion. Native H3 manifests each record107 frames at exact1/24-second intervals and presentation end107/24 seconds. PixelLab native FPS remains unknown.

Fresh real-browser execution: all three native videos decoded and reached ended=true at reported duration4.458333 seconds in an isolated Chromium context. Observed video-frame callbacks were106 walk,105 original slash,105 margin slash. Therefore this proves timed decode/completion, **not all107 frames presented** or continuous human visual acceptance. Human examination here remains static ordered sheets, not an uninterrupted aesthetic playback review. Per-pair blink and normal-speed visual sign-off remain release gates below.

External evidence: `/home/astra/artifacts/pixellab-motion-acceptance-20261014/SOURCE-AND-POSE-SPEC.json` (SHA256 `1dd9a7255566dfb4fa62a98e0d3b8a99b57b2a5bcb7f284e15b8fe6204188744`); browser replay/receipt under `output/playwright/native-clock.{cjs,json}` (receipt SHA256 `da9fbc85e8a729d780314a7aa703d6901b557e3131870602bafd8a4f841a6447`). The JSON binds all six source-manifest hashes, frame counts, exact clock, generated alpha/border measurements, and the proposed holds below. Contact pages are observations, not numerical art scores.

## Separate generation, selection, edges, and drift

| Concern | Observed evidence | Appropriate next action |
|---|---|---|
| Generated attack geometry | H3 margin24/25 cut the physical blade on the left;35 cuts its tip on the right. Original H3 has top clipping near17 and right clipping at40/53. | Block complete-weapon release. Padding/keying/resizing cannot restore missing native pixels. Any later authored reconstruction must be an explicit separately reviewed raster edit, not called original output. |
| Strike coverage | H3 margin26/27 show the fast cross-body transition;26 is foreshortened/blurred and27 is a broad smear. Uniform16 sampling omitted both. | Keep both in candidate16; inspect25→26→27→28 at native scale and final scale. Inclusion fixes sampling coverage, not blade rigidity or grip. |
| Excess exposure | Margin28–73 contains a long similar follow pose:46/24 seconds.87–106 is settled tail. Original31–52 follows and65–106 settles. | Retain raw timing. Separately author shorter holds/cuts, then compare timed results; do not claim the source attack originally took0.8seconds. |
| Unrequested effect | PixelLab margin6 and original6/7 contain white sweep/arc shapes despite the no-effects brief. | Record failed brief compliance. Explicitly review/edit the effect pixels and any occluded actor regions, or retain a clearly labelled effects variant; dropping6 alone can also destroy strike readability. No automatic repair is approved. |
| Background/edges | H3 is opaque H264/YUV420p. Border-connected black key tolerance12 and fixed nearest256resize are local derivatives; dark outline loss and video/chroma fringes remain possible. PixelLab generated alpha is binary in these outputs. | Compare original/keyed edges on black,white,checker and saturated scene backgrounds at1×/4×. Never infer private segmentation/de-flicker from these deliverables. |
| Registration versus articulation | Walk boots overlap near H3 18–20/64–68; sword reach changes near40–49/84–93. PixelLab has torso/profile and stance changes. | Annotate planted contacts and equipment landmarks before measuring drift. Global bbox/centroid movement also reflects legitimate limb motion; do not automatically recenter every frame. Ground contact and hidden shield grip remain unmeasured. |

## Source roles and clock policy

The recorded matched protocol pins the same PNG/prompt bytes and `first_frame` role within each pair, with no supplied last frame. PixelLab requests seed123,16 generated frames, transparent output, default de-flicker and omitted automatic-caption fields. Native H3 requests4seconds/768P and has no demonstrated equivalent typed seed/alpha/frame-count contract. Checkpoint, private prompt handling, frame selection and conversion remain unknown. Source equality does not isolate the model backend from those differences.

Keep PixelLab returned slot0 as a separate reference, never a generated playback frame or an invented duplicate prefix. Its visible RGB and alpha equal the submitted source; only hidden RGB differs at49/49/30 positions across walk/original-slash/margin. That is compatible with known normalization behavior, not proof of a private implementation or visible redraw.

Maintain two explicit clocks: **source PTS** for H3 raw and PTS-delta sampling, and **authored rational holds** for any game-oriented cut. A shared nominal inspection duration does not pair107 native frames temporally with16 returned sprites. Ground-contact or impact time must not be inferred from index count.

## Proposed attack pose holds: diagnostic, not approved

Use the unchanged PixelLab margin generated slots1–16 in order. Proposed local clock60ticks/second,48ticks total(4/5second), once-only with final pose held until explicit replay/restart. No authored contact/hit event is included. All16 are retained so that changing exposure cannot conceal the sweep or transition defects. This proposal has not received timed aesthetic acceptance; it is a concrete first editable timing revision.

| Returned slot | Pose annotation | Proposed hold ticks/60 |
|---|---|---|
| 1 | ready | 3 |
| 2 | anticipation | 4 |
| 3 | anticipation | 4 |
| 4 | anticipation | 3 |
| 5 | late anticipation | 2 |
| 6 | strike with unrequested sweep | 1 |
| 7 | follow-through | 3 |
| 8 | follow-through | 3 |
| 9 | follow-through | 3 |
| 10 | follow-through | 3 |
| 11 | follow-through | 3 |
| 12 | recovery | 3 |
| 13 | recovery | 3 |
| 14 | recovery | 3 |
| 15 | recovery | 3 |
| 16 | recovery | 4 |

H3 margin full native annotation covers all107 indices:0–6 ready/lead-in;7–23 preparation;24–25 cropped backswing;26–27 fast strike;28–73 follow-through;74–86 recovery;87–106 settled tail. These are visual phase labels, not skeletal contact/impact ground truth.

Retain the existing curated16 indices, including endpoints0/106 and both26/27. Two independent hold columns below are alternatives, never mixed. Native sampling preserves the entire107/24-second envelope; the proposed authored48/60-second cut shortens/redistributes exposure and remains blocked by the cropped blade and ambiguous strike.

| Native index | Native sampled hold seconds | Proposed authored ticks/60 |
|---|---|---|
| 0 | 1/2 | 3 |
| 12 | 1/4 | 3 |
| 18 | 5/24 | 3 |
| 23 | 1/24 | 3 |
| 24 | 1/24 | 1 |
| 25 | 1/24 | 1 |
| 26 | 1/24 | 1 |
| 27 | 1/24 | 1 |
| 28 | 7/24 | 3 |
| 35 | 17/24 | 3 |
| 52 | 7/8 | 3 |
| 73 | 5/24 | 3 |
| 78 | 7/24 | 5 |
| 85 | 3/8 | 5 |
| 94 | 1/2 | 5 |
| 106 | 1/24 | 5 |

The8-pose existing profile `[0,18,25,27,35,73,85,106]` omits26; keep it a separate coarse diagnostic rather than silently claiming the same fast-phase coverage as16. Do not merge the native-tail hold or reference frame into an invented sprite FPS.

## Required measurable release gates

These are proposed project gates, not automatic art-quality scores. Each must carry explicit reviewer status and exceptions; passing a metric alone cannot approve animation.

1. **Source and transformations:** bind every native/returned index, raster hash, fixed canvas, pivot, role and hold. Preserve raw inputs. Every cut/key/resize/normalization has a named derivative and exact parameters. No per-frame reanchor or hidden reference insertion.
2. **All-frame visual coverage:** inspect100% of chosen output frames at native and intended game scale. For each frame record torso/head, visible hand/hilt/tip, shield, feet, crop, edge and no-effects compliance. Any physically missing required sword tip is a blocker. Critical-part edge contact requires explicit review even if total alpha-border count is zero.
3. **Every adjacent pair:** review all15 adjacent pairs for a16-pose one-shot, including original25→26→27→28 in H3; all106 adjacent pairs for each107-frame native sequence. If looping also inspect last→first and first→second. Use blink/onion-skin as aids; investigate discontinuities rather than smoothing or reanchoring by default. Full raw/native review and selected-output review stay separate.
4. **Ground and equipment measurements:** manually annotate contact intervals and heel/toe/ground-pivot coordinates before calculating planted-foot displacement. Proposed diagnostic tolerance is≤1output pixel during declared stationary contact, with explicit world/camera-motion exceptions. This is unmeasured today. Mark occluded points unknown; do not invent shield grip or rigid blade length from projected distance alone.
5. **Edges and edit locality:** inspect all keyed frames on at least black,white,checker and a saturated background at1×/4×; unresolved outline removal/fringe fails approval. Outside an approved edit mask, exact RGBA changes must equal0; an explicit hidden-RGB normalization derivative is tracked separately. Alpha/bbox/color-count metrics flag work, never auto-pass appearance.
6. **Real timed sequence:** reviewer watches the entire authored cut normally and at slow speed; walk runs≥3complete cycles with seam review, attack runs≥3explicit restarts with≥1second final-pose hold each. Record actual time/frame callbacks, pause freeze and completion. Scheduler drops are disclosed. No callback count substitutes for a human smoothness/contact judgment.
7. **Export/reload:** exact rational holds,pivots,order,roles,declared events and finite/loop behavior survive cold editable/PNG/APNG/Godot replay. Authored impact events remain empty until separately justified. Mechanical export acceptance is necessary and distinct from art acceptance.

Current release state: **unfinished candidates; no art approval**. Highest-value next step is an editable margin-slash timing revision with these phase labels, plus explicit sweep repair/rejection and measured hand/tip/contact review. H3 sampling can be improved locally while its native missing sword pixels remain a visible blocker.

# Extend an approved hero with bounded action experiments

Use an approved clip as identity evidence, not as a recovered rig or automatically suitable neutral pose. Preserve original pixels, timing and acceptance scope. Keep newly drawn ready art, procedural guides, provider returns, normalized candidates and gameplay behavior separately qualified. This case concerns one hero/view, unarmed punch and jump; it establishes no private PixelLab or MiniMax implementation.

Case evidence root: `/home/astra/projects/rpg-hero-animation`. Paths below are relative to that root. These measurements are case configuration, not universal sprite dimensions.

## Lock a shared rest and fixed stage

Before parallel action work, export one exact neutral with joints, complete shoe vertices/markers, camera, proportions and source hashes. Punch/jump must share its entry/exit geometry, not independently adapted rests. Here `work/punch-guide-v2/neutral-frame.json` binds eighteen joints and shared rest; `work/jump-guide-v1/SHARED-READY-COMPARISON.json` checks correspondence. The new 192 stage preserves body scale through constant 128-source padding(+32,+64), nominal pivot[96,170], then whole canvas nearest 2x to384. Never fit/recenter individual poses. A nominal pivot is registration, not sole-contact proof. Keep ground root and airborne height distinct; generated frames may already contain jump height, so runtime must not add it twice.

## Gate silhouettes before full rendering

Mathematical validity did not prevent two visual failures: projected shoes initially fused into one column, and punch v1 resembled pointing/presenting despite a valid arm chain. Correct the shared stance once; then revise action controls without changing neutral/proportions/camera. Punch v2 added readable load, shoulder/trunk twist and projected fist travel beyond the chest, including a camera-visible lateral component. The closed glove remained attached through shoulder/elbow/wrist. See `work/action-guide-review-v1/REVIEW.md` and `work/action-guide-review-v2/REVIEW.md`.

Gate sparse keys at native and 2x on contrasting backgrounds, then inspect actual continuous encoded chronology. A held-key demonstration is not continuous motion. The final punch uses one 0.875-second action inside 160 frames at 32 Hz over 5 seconds, with exact ready pauses. Actual lossless decode, PTS, constant boot geometry and lower-body pixels were verified in `work/punch-guide-v2/VIDEO-PROOF.json` and its geometry/planted-pixel proofs. The independent continuous gate is `work/punch-continuous-review-v2/REVIEW.md`; guide passage did not approve generated art.

## Preserve actual returns and challenge input roles

Retain literal prompts, ordered media bytes, request/code hashes and complete returned video. Both first action returns were 124 frames at 24 Hz, duration 31/6 seconds, despite 160-frame, 32 Hz, 5-second guides. Probe real PTS and positive final holds; do not transfer guide timestamps or the approved walk's first-30 selection. Full returns were sampled768 to 192 at source(4x+2,4y+2), without fitting. See `work/action-production-v1/punch-native-v1/full-return-recipe.json`, `work/action-production-v1/jump-native-v1/full-return-recipe.json` and corresponding `bake/manifest.json`.

Appearance inputs carry pose information. The first punch retained a walking-style rest despite a neutral/action guide and prompt. That observation motivates testing neutral Image1 rather than assuming “appearance reference” means pose-free conditioning. `work/neutral-provider-input-v1/RECEIPT.json` proves the 94-pixel ready candidate was composited onto exact green, visible RGB preserved, then nearest 2x. The paired `providers/minimax_h3/jobs/punch-v2-neutral/state.json` and `providers/minimax_h3/jobs/jump-v2-neutral/state.json` retain completed requests and full native returns. Fresh reviews found improved planted rests, with separate remaining defects described below. This stochastic sensitivity experiment cannot prove causal weights or private architecture, and the new ready candidate is not human-approved authority.

## Separate scale/registration from pose repair

Independent raw-jump review measured 103-pixel ready height versus approved 90–95 pixels and a floor 3 pixels lower than nominated walk00. The jump itself retained a stable floor. Evidence: `work/jump-art-review-v1/REVIEW.md`.

A separate candidate uniformly samples 192 to 176 and places the result at(+8,+12) on192. That includes an explicit constant -2-pixel registration bias relative to the earlier(+8,+14) proposal. It is not recovered root motion, per-pose sole correction or art approval. Preserve all 124 raw and transformed frames; the 55-frame source 14..68 branch is an authored selection. See `work/action-transform-v1/recipe.json`, `fixed_transform.py` and `jump-v1/PROOF.json`.

Record pixelXY witnesses through every sampling stage, including hidden RGBA and zero padding. Do not assume a floating pixel-center formula reproduces a library's nearest ties. Pillow 12.1.1 chose source indices 5, 17, 29 at destinations 5, 16, 27 where another exact-center convention chooses 6, 18, 30. Freeze the literal axis lookup, validate nearest admissibility and compare actual fullRGBA output independently. Distinguish mechanical mapping success from visual scale acceptance.

## Repair timing explicitly

The first punch's extended phase 41..58 lasts eighteen native frames, 0.75 seconds; these are distinct RGBA frames with near-held artwork, not literal duplicates. Independent review also identified sharp 40→41 and 58→59 transitions. Test a shorter authored hold/selection before adding intermediates; preserve the full native return and document changed playback duration/source indices. Never call the retimed result original native flow. Walking-style rest still needs a pose/input repair: timing cannot fix it. Evidence: `work/punch-art-review-v1/REVIEW.md`.

Scoped refinement now passes normalized jump55 scale/floor/edges and punch24 timing: source order[29,31..43,57..66], twenty-four 1/24s holds=1s, extended phase 5/24s≈0.208s. Walking-style rest persists. See `work/action-refinement-review-v1/REVIEW.md`.

Exact 24/55-frame APNGs are verified under `work/action-production-v1/punch-retimed-apng-v1/receipt.json` and `work/action-production-v1/jump-apng-portable-v1/receipt.json`. PNG player/APNG are authoritative here. Both lossy exact_CFR MP4 attempts failed distinct-template classification on nearly identical H3 poses; do not claim those MP4s pass. Jump's initial APNG rejected sibling `../` paths; exact-byte staging repaired layout, not artwork (`work/action-production-v1/stage_manifest.py`).

## Keep still generation and review honest

The one-call punch ImageGen still produced recognizable costume and a closed-fist strike, but direct nearest 192 yielded 87-pixel height, while the unchanged ready transform (nearest 224, crop 16..208) yielded 101 pixels versus ready 94. The striking limb may also differ from the guide. Retain both outcomes without individual fitting or automatic retries: `work/punch-imagegen-key-v1/RECEIPT.json` and `NORMALIZATION.json`. Preserve raw alpha; binary alpha>=128 is an explicit derivative. Document separately whether hidden RGB is preserved or zeroed for a model-reference composite.

Before alleging vanished frames/faces, inspect raw decode, foreground counts, standalone images and contrast composites. Repetitive sheets caused apparent omissions later disproved by raw checks; `work/punch-continuous-review-v2/REVIEW.md` retracts that blocker. Ordered still/timestamp review is not human normal-speed perception.

Finally, `actions/attachments.example.json` leaves grip/hand/occlusion anchors deliberately null. Measure and review anatomical ownership and compatible weapon-motion profiles before attaching equipment. None of these experiments approves final action art, hit windows, landing physics, runtime transitions or interchangeable weapons.


## Subsequent neutral-input results

The paired experiment changed only Image1; literal prompts, guide bytes and remaining request fields matched (`work/action-production-v1/V2-CONTROLLED-INPUT-CHECK.json`). Both new returns retained planted rests. Jump v2 passed local art review at its native scale; its 55-frame source window28..82 needs no rescaling. One pixel of contact variation was documented, without claiming physical ground truth. See `work/jump-art-review-v2/REVIEW.md`.

Punch v2 returned black instead of requested green and added a fist flash at45..46. Never reuse the green matte on such a return: all opaque borders correctly exposed the failed background assumption. The retained derivative uses threshold4 edge-connected black background removal, preserving every RGB value and enclosed dark regions. Its observed edges passed three-background review; the true outline where black paint meets black background remains ambiguous. See `work/black-background-matte-v1/REPORT.md` and `work/punch-refinement-review-v2/REVIEW.md`.

The final punch experiment selects source30..44 and50..66, omitting the embedded flash and some held samples. All32 holds are1/24s, total4/3s: four extended frames together last1/6s. An accidentally exported four-ticks-per-frame variant was caught independently and corrected before delivery; count total exposure, not just poses. Current exact PNG/APNG candidates are under `work/action-production-v1/{jump,punch}-candidate-portable-v2` and `{jump,punch}-apng-v2`. These local review gates are not a9/10 human rating, accepted gameplay, physical jump/controller proof or finished equipment integration.

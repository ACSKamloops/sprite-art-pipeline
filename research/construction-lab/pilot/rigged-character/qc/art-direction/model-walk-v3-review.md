# Model-rendered RPG walk V3 — independent art review

**Decision: changes_requested. The rendering approach is viable; this candidate is not approved final art.** A licensed professional model and a correct export do not satisfy the user's visual-quality requirement automatically.

Reviewed the actual four-view contact sheets at native and 2× scale, all 12 ordered poses per view, and separately decoded GIF boundary frames 10→11→0→1→2 at 3× nearest. The four native GIFs contain 12 frames with 80/90 ms quantized holds totaling one second. This is actual asset/frame inspection, not a claim of uninterrupted human playback or a moving-world contact test. Source: `candidate-walk-rpg128-v3` in the art-expansion worktree; exact file hashes are in the accompanying JSON.

## What is stronger

- Front, back and both sides retain coherent hood, shoulders, chest, pelvis, limbs and costume volumes. Depth views are actual corresponding forms, with changing near/far leg overlap; they no longer resemble side parts rearranged into a front view.
- The side stride has recognizable extended contact, gathering/passing and forward swing. Arm and opposite leg progression is visibly coordinated, with plausible shoulder attachment. Front/back legs alternate in depth rather than just bending sideways beneath a fixed body.
- The planted-versus-swinging leg relationship is easier to read than in the painted rig. Hip/torso movement is restrained and volumes remain stable between phases. The decoded loop-boundary progression shows no obvious identity, scale or pose reset seam.
- This **can work as a modern prerendered RPG sprite at a 128×128 canvas**: silhouette and consistent 3D forms are viable. That is a format/design assessment, not approval of the current character or a promise of pixel-art style. It looks like a shaded low-poly render, not deliberately hand-authored pixel clusters.

## Required polish before another review

1. **Leg and sole readability:** dark trousers, lower legs and boots collapse into one low-value mass against the dark audition background. Side feet are small and lose heel/sole distinction; frontal near/far leg separation is underlit. Lift the lower material values and add controlled lower fill/rim or material separation, without washing out the torso. Review against both the intended light and dark ground palettes, not only transparency.
2. **Face and identity:** the front face is largely a blank light patch. At native size it reads as a faceless stock hooded figure rather than a specific character. Author features and a deliberate hood opening/hair or brow silhouette at the model/texture level, with native-size checks. If facelessness is an intentional design choice, establish a stronger distinctive silhouette/material motif instead; don't leave it as an accidental resolution loss.
3. **Material hierarchy:** gauntlets, belt, chest straps and boots are similar muted browns. They muddy the hand/waist overlap and make the costume generic. Establish a limited value/color hierarchy and a persistent recognizable accent that survives front/back/side rotation. It must remain attached to the model through all poses, not appear as inconsistent per-frame decoration.
4. **Motion presentation:** keep the current camera, scale and pose sampling fixed while polishing so changes can be attributed. Then show at least three cycles at native scale in a simple ground context, including the wrapped boundary and a moving-world audition. Do not speed up the clip to conceal weak contact or approve it from a static contact sheet alone.

I do not find the prior rig's obvious disconnected/rod-like directional anatomy in these frames. The outstanding visual issues are mostly native-size readability and authored character identity. Real foot locking, root velocity, event behavior and controller transitions remain separate, unreviewed gameplay gates for this new source.

## Painted cutout V3 — separate rejection

Viewed `painted-rig-v3/candidate-v3/keys-2x.png` across the eight labeled key poses. **Reject for promotion.** It retains attractive hood/costume fragments, but the arms remain crowded around the waist with weak shoulder-to-hand articulation and unclear opposing swing. The waist/coat/pant joins and deforming trouser contours read as assembled pieces rather than a continuous weighted body; contact/down/passing silhouettes remain insufficiently distinct. More interpolated frames cannot correct the underlying part shapes or joint/occlusion design. No approval transfers from the model route to this cutout.

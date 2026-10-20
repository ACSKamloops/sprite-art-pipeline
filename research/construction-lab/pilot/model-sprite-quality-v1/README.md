# Textured rig → modern sprite walk pilot

Current equipped candidate: `candidate-walk-bow160-final24-v10/`. The prior unequipped `candidate-walk-polished160-final24-v9/` remains intact as a separate comparator. It contains 48 transparent 160×160 PNG keys (12 keys × front/right/back/left), a packed editable `ranger-walk-render.blend`, native-size contact sheets, 1×/2×/3× timed GIFs and source-bound evidence. This is a licensed Quaternius Ranger adaptation and a quality-route benchmark, not the original Copper Scout identity or an approved finished character pack.

## Sources and permissions

The [creator's official RPG Character Pack page](https://quaternius.com/packs/rpgcharacters.html) specifies rigged, animated, textured models under CC0. The [creator's own OpenGameArt upload](https://opengameart.org/content/lowpoly-rpg-characters) provides the downloadable archive used here. `source/provenance.json` records the URLs, archive SHA-256, selected original-file hashes and CC0 license. `source/original/` retains the untouched Ranger `.blend`, original UV textures and the actual included license. The original official Google Drive download returned quota HTML; it was never treated as a model. Its failure and alternative-asset trials are preserved locally in ignored research files.

Kenney's [Animated Characters Protagonists](https://kenney.nl/assets/animated-characters-protagonists) was also checked (CC0), but its supplied actions were idle/jump/run rather than this walk. Quaternius's older knight was accessible but less suitable for the requested textured-clothing test. No credentials, paid downloads or recreated capsule geometry were used.

## Render and authored changes

The actual Ranger mesh, weights, constraints, cloak, armguards, pouch and existing `Walk` animation drive every frame. Cameras rotate around the same model; left is an actual opposite camera view, not an image mirror. Orthographic scale3.6, target Z1.45, camera radius8 and elevation≈12° remain fixed. There is no per-frame fitting, recentering, pose redraw, floor plane or baked floor shadow.

Original texture pixels are unchanged. Original stale image paths are reconnected and shader materials rebuilt. The original bone-parented bow is visible in v10, restoring the source scene carry state; only the prior v9 adaptation hides it. The polished candidate changes fixed area-light fill and applies a monotonic material gamma0.8 shadow lift. Sparse eye/brow marks are explicitly authored Blender UV-shader overlays from `face_detail.json`, attached through the original symmetric face UVs; they are not original Quaternius facial details or per-frame paints. 128-sample Cycles CPU renders retain antialiasing and soft alpha without denoising, which had erased the first overly small facial marks. There is no forced16-bit palette or pixel-art claim.

`matched160-before-after.png` compares actual same-camera/same-scale baseline and polish PNGs at matched160 resolution. The lower-leg/boot values are more legible and the face has small persistent marks. The result still has a sparse face, a visibly low-poly hood, muted natural materials and generic licensed-ranger identity. Those are visual limitations, not removed by successful export tests. Final aesthetic acceptance and timed/moving-world review remain independent.

## Correct source timing

Direct inspection of the untouched source `.blend` shows scene FPS24, base1. `Walk` spans frame0..30; frame30 duplicates frame0. Therefore the native source period is30/24 = **1.25 seconds**. Exported keys are frame0,2.5,…27.5. Each held key lasts2.5/24 seconds (12 keys at9.6fps). Frame30 is excluded from the repeated sequence. Source pose evaluation can interpolate at fractional source frames.

Earlier candidates v4/v7/v8 used an explicit export assumption of30fps and one-second previews; that assumption was wrong for the source scene and is superseded. Those prior snapshots are retained, not stamped as final. `timing-correction-comparison.json` proves all48 v9 RGBA poses are exactly unchanged versus polishedv7; the clock and previews are corrected. GIF durations use cumulative10ms error diffusion and sum to1250ms; they are previews, not an exact rational engine-clock format.

## Source-authoritative landmarks and boundaries

`landmarks.json` contains evaluated bone endpoints at every original source tick0..30 in allfour views: head, pelvis, hips, knees, ankles, wrists and foot controls, with world coordinates and actual projected pixel coordinates. Bone names and deform/control roles are preserved. The rig has no anatomical toe bones; none are invented. Foot.L/R are explicitly exported as controls, not declared sole contact. The fixed ground-plane world-origin projection is about[80,143.037] at160px; this is a camera pivot, not a per-frame fitted lowest sole.

No numerical stance, collision, foot-slip, root-speed or physics acceptance follows from those landmarks. The current renders are an in-place authored walk. A moving-world audition needs measured stance/sole data and an explicit root trajectory. This pilot does not silently substitute a stationary world root as a contact proof.

## Executable reproduction and checks

From this repository root (Linux Blender4.5.9 LTS installed in the shared Mech Warrior Test tools):

```
BLENDER='/home/astra/projects/Mech Warrior Test/tools/blender-linux/blender-4.5.9-linux-x64/blender'
"$BLENDER" --background --python pilot/model-sprite-quality-v1/render_walk_equipped.py -- private-reproduce-equipped
python pilot/model-sprite-quality-v1/make_preview.py pilot/model-sprite-quality-v1/private-reproduce-equipped
```

The render script refuses an existing destination. `fetch_asset.py` can recreate the selected original input snapshot in a fresh source-less copy; it refuses existing original sources. Its included archive bytes are checked by the stored provenance hashes. The packed delivered scene opens without external image dependencies.

`verify_reopen.py` actually reopens and renders first/duplicate-end poses through allfour cameras. `reopen-validation.json` and the independent Pillow byte receipt `reopen-RGBA-exact.json` prove eight exact PNG RGBA comparisons. `coverage.json` checks all48 actual output images for dimensions, alpha and unclipped bounds. `export_landmarks.py` can rerun the geometry sidecar from the packed source without changing the PNGs. The final manifest binds render script, original input files, face-detail descriptor and every PNG SHA.

These checks establish the specific source/render/loop claims above. They do not approve artistic quality, full-action coverage, game integration or moving-world contact. Independent final timed review is required before promotion; no Site publication is part of this local pilot.

## Source equipment posture follow-up

Read-only `equipment-intent-inspection.json` establishes that the original Ranger bow is visible by default, bone-parented to `CharacterArmature/Weapon.R`, and has no independent animation. The source has a single `Walk`, plus distinct `Run`/`Run_Holding` and `Idle`/`Idle_Weapon` actions; no separately named unarmed walk is supplied. Walk contains no visibility channel to stow the bow. This supports a gear-carry interpretation of its guarded hands, but does not establish the author's exclusive intent from a clip name. Hiding the bow for this pilot is an explicit adaptation; it does not magically turn the existing hand posture into a dynamic empty-handed walk. A separate equipped rendering can be evaluated without modifying this frozen pack.

## Equipped v10 checkpoint

The frozen renderer is `render_walk_equipped.py`; its exact pre-invocation archive and freeze receipt are `source/renderers/`. `EQUIPPED_HANDOFF.json` binds the new manifest, packed scene and evidence. Both original character and bow texture hashes are included. Facial UV shader overlays apply only to the character material; the bow uses its original UV texture with the declared fixed tonal shader. No source walk pose, camera, lighting, clock, geometry or original texture pixels changed relative to v9. The images themselves change because the original bow is now rendered, including its physical occlusion and lighting contribution.

`verify_equipped_reopen.py` performs eight actual Blender renders after reopening the new packed scene. `verify_equipped_pack.py` independently checks exact PNG RGBA comparisons, all48 hashes/clock/canvas/bounds, allfourGIF cycle durations, frozen renderer/source hashes and all124 unchanged evaluated body-landmark samples. `byte-validation.json` passes195 checks. `export_equipped_landmarks.py` additionally exports the real Weapon.R socket and bow object world origin, with no assumed contact/collision semantics.

This restores the original default-visible, bone-attached equipment state in the supplied scene. Its constrained right wrist is consistent with carrying that bow, while its left arm retains the authored swing. That is observed rig/animation evidence, not a fabricated statement of exclusive source-artist intent. The new native/timed artwork must receive its own independent review; neither visual acceptance nor world-contact evidence is inherited from v9.

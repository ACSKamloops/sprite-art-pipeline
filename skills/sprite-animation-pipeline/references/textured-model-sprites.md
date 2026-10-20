# Rigged textured model to modern sprites

Use this route when consistent anatomy, equipment and four-direction volume matter more than hand-painted pixel clusters. It requires actual geometry, UV materials, a rig and an authored motion. A flat reference image does not contain those inputs. AI can propose a design; generating unrelated walking images does not create a coherent rig.

The local example uses a licensed Quaternius Ranger as a method benchmark. It does not recreate the original Copper Scout, approve a whole game library or demonstrate automatic image-to-3D reconstruction. The rejected contour rig and painted cutout are preserved: stable pixels and working IK did not rescue weak anatomy and weight. Richer AI pose sheets also failed ground registration, garment consistency and opposing gait phases.

## Prepare a small art pilot

1. Define the intended native size, character proportions, material palette, equipment hand, views and gait. Compare an artist-authored contact/down/passing/up sequence; use real-game extracted timings only when actual decoding/runtime evidence supports them.
2. Obtain a model with permission to use it; retain the exact model, textures, license, source URLs and hashes. Inspect real bones, constraints, action ranges, image paths and source FPS. Do not trust a preview's playback rate or a file name.
3. Choose one complete representative walk in all requested directions. Preserve its equipment context. In the example, the source bow is bone-parented to Weapon.R and the Walk has a constrained right arm. Removing the bow did not produce a convincing dynamic unarmed arm swing. A new freehand walk needs new authored motion.
4. Reconnect the supplied UV textures and pack the editable scene. Establish pose-independent camera scale, root/ground projection and alpha policy. Render true opposite views, not mirrored asymmetric equipment. Do not fit or center individual frames.

## Keep direction and light conventions explicit

For a fixed game camera, render actor turns or orbit the camera together with the lighting rig. The latter must preserve each light's camera-space transform. Orbiting only the camera around fixed lamps preserves object-relative studio lighting, but changes the key direction on screen. The bow pilot caught noticeable left/right brightness changes this way. A corrected candidate rotates Key/Fill/Rim with the view and checks their actual camera-space matrices.

Reopening a directional render must restore both camera and lights. A verifier that restores only camera positions can test a different image than the exporter. Record per-view transforms and materials, not only a sentence saying the lighting is fixed. A game's final environment may require a different lighting/palette treatment; the studio example is a reusable sprite fixture, not a runtime relighting system.

## Export timing and editable sources

Read source FPS before modifying scene render settings. The example's Walk runs from0 to30 at24fps. Its duplicate endpoint is excluded; the cycle is30/24=1.25seconds. Twelve keys at0,2.5,…27.5 each hold2.5/24 seconds. This is9.6 held images per second, or6.25 simulation ticks per pose at60Hz. Do not round holds to integer ticks or call it a one-second loop.

Record source frame, seconds, file hash, fixed canvas, model/material inputs and renderer hash for each export. Save a packed scene retaining the rig and all original actions. Reopen it in a fresh process and render first/duplicate endpoints for every view. Exact endpoint equality proves a loop boundary, not a pleasing gait. GIF timing has10ms quantization; use the rational manifest/engine clock as authority.

## Fine-edit the source, then render again

Use UV textures, source-attached shader features or geometry/rig edits for changes that must follow movement. Preserve a baseline and descriptor preconditions. The example authors sparse eye/brow shader overlays on known face UVs while retaining original texture bytes. Edit that descriptor in an isolated revision, render the same views and phases, and compare the actual results. Confirm the feature stays on the face and does not bleed onto shared hood/limb UVs. Global illumination or antialiasing may affect other pixels; measure the changed regions and magnitude rather than inventing an exact face-only invariant.

For downstream cel fixes use sprite-construction-editing's masked, replayable journals. Rerendered upstream images invalidate those journals and their reviews. Do not silently combine an older pixel patch with changed model exports. New source and image hashes require fresh affected-frame and timed review.

## Verify before expanding

Check dimensions, alpha, unclipped bounds, source/renderer/frame hashes, clocks, reopened resources and duplicate endpoints. Import actual SpriteFrames in Godot, save/reload and compare real GPU output at native and integer scales. Modern soft-alpha exports need compositing tests on a declared opaque background; binary-alpha byte equality from a different prototype does not transfer. State a measured tolerance, including any1LSB rounding.

View every adjacent pose, opposite half-cycle and loop in all directions, including equipment grip/occlusion, anatomical mass, changing materials, knees, narrow feet and face readability. Capture at least three real source-clock loops at intended native size and an integer diagnostic scale. Timestamp screenshots before and after capture; they may span pose boundaries. Paused inspections are separate from chronological playback. AI viewing those captures is not continuous video ingestion.

Use independent adversarial reviewers when requested. Record technical acceptance, limited art acceptance, user direction and missing coverage separately. Passing hundreds of checks does not approve aesthetics. A borrowed professional rig also does not automatically meet a specific character brief.

An in-place loop and a moving actor are separate problems. Do not label foot controls as sole contact or certify foot slip from ankle trajectories. Establish actual sole/contact phases, a root trajectory, camera/raster convention and all held-frame sub-times. Until then the moving audition tests controls and presentation, not production locomotion contact.

## Local evidence and example

In the shared lab, `pilot/model-sprite-quality-v1` contains source/license, frozen renderer revisions, manifests, packed scenes, source landmarks and reopen proofs. `pilot/model-walk-audition` contains a hash-checked four-view player, actual timed captures and corrupt-input controls. `pilot/model-godot` contains the standalone engine fixture when integrated. Consult the current lab handoff for the selected revision and independent review; never substitute an older accepted manifest. The portable example under `assets/model-walk-example` supplies the specific Ranger adapter and original CC0 inputs; copy it to a fresh work folder before rendering. Adapting another character requires explicit object/material/action/bone mappings and a fresh pilot.

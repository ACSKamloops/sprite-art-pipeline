# Inputs and animation routes

Separate identity/geometry, style, material, pose and edit-target references. A clear original brief can supply identity; approve a model sheet before a large batch. For faithful adaptation, inspect sources and missing/occluded details. Multiple views, attachments and the intended game camera improve consistency.

Freeze canvas, projected height, view, pivots, palette/lighting, layers and scale. Independently cropped portraits aren't animation-ready. Choose required directions and preserve equipment asymmetry.

| Route | Inputs | Evaluate |
|---|---|---|
| Native extraction | Artifact and format/code evidence | Aliases, conditional controls, effects, runtime equivalence |
| Pixel editor | Approved sprite/key poses and motion brief | Layers, timing, silhouette and anchors |
| 2D rig/cutout | Separated body parts and stable anchors | Joints, overlaps, rigid motion, cleanup |
| Blender render | Model/rig, orthographic camera, materials | Camera/lights, projection, foot lock, alpha, cleanup |
| AI key poses | Identity/style sheets and intended poses | Anatomy/equipment drift; deterministic in-betweens still need review |

These are selection criteria, not claims every route is implemented. Check actual tools before choosing. A Blender workflow requires a suitable model; Godot alone doesn't provide it.

Blender can also animate flat image planes as a **2D cutout**. This needs separated parts and anchors, rather than a full 3D character. Name that route accurately; a single painted view does not establish hidden geometry. For a pixel cutout, separate boots from rotating calves and forearms from upper arms when contact or bending needs independent control. Rigid whole limbs can produce repeatable but visibly weak motion.

Freeze a common motion brief before comparing: view, ground anchor, projected height, gait/contact phases and attack windup/active/recovery. Compare equal-resolution/palette versions when isolating a conversion; higher resolution is a different variable. Native versus redesigned art has different fidelity goals, so RGB error against a redesign is not an identity score.

Use fixed cell transforms for AI key-pose sheets. Check contact poses actually alternate legs; a convincing still can repeat the same contact in both halves of the gait. A targeted prompt can also change unrelated parts, so inspect the replacement against the identity reference. Keep rejected versions. A repeated contact needs an art correction, not optical-flow morphing that hides the missing pose.

For deterministic rig tests, save part anchors, lengths, overlap order and transforms. Test target reachability and stance landmarks under world travel. A zero IK endpoint error proves a target was reached; it does not prove the painted sole stays flat or touches collision geometry. Render a separate loop-closing sample instead of merely copying frame zero.

For Blender pixel renders, use a fixed orthographic camera, nearest texture interpolation and controlled sampling/color management. The tested cutout used emission planes, Standard display transform, one EEVEE sample and filter_size0.01. Retain the softer prior output if changing sampling. Shader/alpha/color differences can remain even with identical poses, so compare masks and foreground pixels separately. Verify the expected files and a script success marker: Blender can return a successful process exit after a Python script error.

For editor round-trips, reopen the editable project and compare every exported cell. PNG-sequence imports may assign default frame durations. The tested LibreSprite GUI runner sets individual durations through Frame Properties, verifies each saved value and retries missed inputs. Its startup script ran before a usable GUI context and did not establish edits. Keep the portable engine clock authoritative: millisecond editor timing and GIF centiseconds may need rounding with a documented total. An editor preserves/orders art; it does not automatically generate missing poses.

Compare routes on the same movement and attack brief. Author contact/pass/lift key poses, then in-betweens in the chosen editor/rig. Attacks need windup, active motion and recovery; gameplay events are explicit decisions. Decide whether motion is baked into frames, controller-driven or root-motion data; don't apply it twice.

Save actual AI prompts, ordered reference paths, receipts, approved identity and edits. Pilot difficult directions/actions. Repair demonstrated drift against the approved identity; regenerating whole cycles can introduce new differences.

For extraction, enumerate tables and callers. Branches, waits, single return slots, removal and external lifecycles invalidate naive linear walks. Use bounded graph traversal, retain exits and label projections. Static reachability doesn't establish natural gameplay use.

Declare ground anchors before comparing routes. An AI key sheet may use different padding for walk and punch; a centered raw key can float while its exported frame uses another origin. Normalize to a fixed canvas using explicitly reviewed action-sheet anchors, preserve legitimate airborne motion, and display the exact exported atlas cells in the runtime preview. Do not automatically pin every pose's alpha bounds to the floor. Recheck both temporal identity and grounding after the change; prior hash-bound review becomes stale.

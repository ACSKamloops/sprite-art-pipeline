# Compare generated paint, motion guides and pixel processing

Keep the appearance reference, pose scaffold and timing authority separate.
Generate a modest action first, preserve the literal request and raw alpha,
then compare fixed-clock derivatives of the same paint. Compare actual native
painted height, not just equal canvas dimensions. A clean export is not an art
pass, and a captured provider animation still needs motion review.

## Tested distinction

In the local 2026-10-20 generic-hero case, ImageGen text alone repeated apparent
limb roles and drifted toward the viewer. Supplying a retained eight-frame
PixelEngine walk as a 3×3 pose/layout guide, plus the same separate appearance
reference, made the gait clearer. Cold review rated the text-led derivative
5.5/10 and the guided derivative7.5/10 overall. These are one direction/action,
based on still chronology and exact holds; no human playback acceptance or
provider-wide ranking was established. Other directions/actions remain open.

This case supports trying a strong motion scaffold before generating additional
text-only inbetweens. It does not show that repainting automatically fixes a bad
scaffold, reveals hidden anatomy or creates an interchangeable body-part rig.

## Processing order and alpha

The actual retained PixelEngine client WASM can infer a new grid. It inferred
23×23 from an already normalized80×80 walk and15×15 from an80×80 still in this
case. Processing the418×418 source cells first produced93×93 for the text walk
and84×84 for the guided walk. Preserve metadata and output rasters. Choose any
subsequent clip-wide transport explicitly; do not conceal shrinkage through
per-pose fitting or equate a fixed affine with recovered nonuniform grid cuts.

Faint generated background noise can become opaque debris after this processing.
A separate alpha8 preparation removed alpha1–7 and zeroed hidden RGB at alpha0,
preserving all RGBA at alpha>=8. It removed visible specks, but the processed
paint was coarser than the unprocessed guided drawing:7/10 versus7.5/10. Treat
this threshold as a tested candidate, not a general cleanup default or reason
to flatten partial alpha. Inspect light/dark composites at native scale first.

The existing authored24-color palette fitter hit its32-iteration guard. The
replacement experiment explicitly selected the20 opaque reference colors using
the existing fixed mapper. Retain fitting failures and label changed policy;
do not silently extend iterations, reseed, or call an authored approximation
the recovered provider algorithm. Palette changes cannot repair gait phase.

## Transport and evidence

Reuse construction projects, rational holds and exact APNG rather than a new
animation serializer. In this case,8fps with duration_ticks1 preserved eight
125ms holds in PNG/APNG and Godot SpriteFrames. The guided candidate also
survived actual LibreSprite batch save/reopen and sidecar import with all RGBA
and holds exact. This tests editing transport; it does not establish a new
interactive pencil edit or art acceptance.

Keep opaque baseline mattes explicit. Check browser-rendered results separately
from PNG/ASE/APNG equality, since partial-alpha canvas bytes may differ. Freeze
an anonymous packet and exact hash/timing ledger before independent review.
State continuous-motion perception limits; inspect the actual timed player
with the user before claiming game-ready motion.

The canonical optional runner and artifact requirements are under
`research/pixelengine-imagen/` in the sprite-art-pipeline repository. Its adapter
requires separately retained hash-pinned third-party files, blocks fetch and
makes no generation/account calls. It is not installed or triggered as a
default preprocessing stage. Local case evidence is retained at
`/home/astra/artifacts/pixelengine-imagen-comparison-20261020`.

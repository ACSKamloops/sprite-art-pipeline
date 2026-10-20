# Rigging painted sprites: ownership checks

This is a tested construction method, not an 8/10 animation approval.
It applies to the detailed flat sprites used by Emberwake. A source
map proves which painted pixel was sampled; it does not establish anatomy or
the material represented by that pixel.

## Define what stays fixed

Keep stage registration, complete boot source layers and support positions
fixed when testing a new body-weight curve. Move complete head/torso/arm/glove
layers rigidly together. Deform only the connected proximal cloth, fading to
the actual cuff boundary. Preserve the existing walk duration and compare
against an exact control.

Exact visible boot pixels can conflict with natural foreground occlusion.
Lyra00's one-pixel downward glove movement covered eight real upper-boot texels.
The boot geometry and source layer can remain exact underneath that glove;
the final visible output cannot simultaneously show both layers there. Retain
the collision proof, explicit depth order, all newly occluded coordinates and
foreground source witnesses. Do not put the boot over a foreground glove just
to satisfy a visible-pixel assertion.

## Make material ownership explicit

Use literal native-coordinate owners and actual source-layer witnesses.
Inspect the full painted cuff, leather, outline, charcoal cloth, glove and
negative space. A broad boot polygon may omit a few real leather texels. Two
older semantic masks can also overlap at a fused seam; that overlap does not
prove which leg owns the paint.

The failed Lyra weight trial selected cloth using a broad neutral-color test.
It admitted brown leather/outline, including source02 `(52,87)=[31,16,11]`
and source06 `(66,85)=[17,7,2]`. The unchanged lower partition therefore did
not certify a complete fixed boot layer. Keep that failed receipt and its
qualification; replace the owner with reviewed literal boundaries rather than
changing the palette threshold until it passes.

## Anchor the painted seam

The cloth field must reach its fixed plateau at the actual cloth/boot join.
A nominal Y anchor below the last real cloth row can let that edge retreat
when the body rises, leaving a gap above an unchanged boot. Review per-column
cloth endpoints and the curved cuff. Require a monotone source map and retain
all integer source coordinates; mathematical monotonicity alone does not
prove a connected joint.

Separate an incorrect mask/anchor from genuinely missing paint revealed by
moving the coat. The first needs a construction repair. The second needs
explicitly authored underpaint, with its palette/source witnesses, owner,
depth order and visual review; it is not recovered hidden anatomy. Do not
hide either problem with a global alpha threshold or independent pose fitting.

## Review motion after construction

The current corrected body-height hypothesis is `[1,0,-1,0]` repeated twice.
Relative to the old `[0,1,1,0]` body curve, corrections are `[1,-1,-2,0]`.
This changes each adjacent height by one native pixel. The earlier suggested
`[1,1,-1,0]` repeated a low body exposure then jumped two pixels; that timetable
and the aborted construction remain retained. No curve is accepted from this
math alone.

After material and joint checks, inspect every combined cel and cyclic pair at
native and game scale on contrasting ground. Compare actual timing and engine
presentation separately. Reproducible maps, rigid parts and successful guard
tests supply construction evidence; they do not establish an 8/10 animation.

## Retain authored coverage and real editor behavior

Lyra's completed test needed 38 explicitly authored, source-shaded charcoal
undercoat texels: nine newly revealed by the lifted coat, then 29 additional
waist exposures. Every texel has its actual donor/palette witness and depth
order. Existing visible cloth lost through a bad mapping was repaired by
correcting owners and endpoints, not repainted. Normal arm/glove clearances
remain open. Two source-field pins in 04 restore existing paint without new
coverage. The frozen review prefers the resulting weight cue at 7.5 motion;
brisk 02→03 and 06→07 recovery changes still limit it.

See `art-source/eight-direction-v1/lyra-stance-spring-v1/ASSET-MANIFEST.json`
for the exact eight cels, curve, owners, maps and coverage journals. A fresh
relocated replay verifies both source construction and actual editor journals.
The primary exchange is honestly flattened final paint, with six guarded
transactions and undo/redo. Its LibreSprite save/reopen, reimport and rendered
RGBA are exact. Five upstream component layers also survive save/reopen,
but LibreSprite 1.3 normal composition rounds two overlap texels differently
from the toolkit's defined integer compositor. Retain that witness rather
than repainting an approved frame or claiming exact layered tool rendering.

Brann's rear donor-boot construction retains a complete P source layer at its
original placement, including newly revealed paint under the removed old Q.
The new Q naturally covers nine previously visible P texels. The layer can be
exact while its final visibility changes. The 05 and 06 Q poses translate the
same complete 07 source boot with no scaling or reflection; this supplies
paint consistency, not proof of ground contact or a full anatomical rig.

## Check motion against travel

At 158 world pixels per second and a 0.45-second loop, the root travels 71.1
world pixels per cycle. Account for the 0.66 draw scale when comparing that
travel with a source boot's backwards motion. A low sole row alone does not
identify a planted foot: depth, swing and foreshortening can give the same
screen contour. Follow a demonstrated same-source sole/ankle segment, record
contact assumptions and projection, and evaluate both longitudinal residual
and transverse movement. Source exactness and an in-place animation review
cannot certify absence of skating.

## Split a rigid boot when the pose requires articulation

The retained Lyra contact pilot moves one complete visible 278-texel boot by
(8,8). Its attached charcoal field stays positive but visibly compresses. A
three-key extension fails at 06: 41 cloth triangles invert. The failed cloth
is never rasterized, and the boot-only diagnostic is not an animation cel.
This rejects that representation for the tested fold, not animation itself.

The next guide separates 167 visible charcoal thigh/knee texels, 142 leather
shaft/calf texels and 136 distal toe/sole texels. Its row split and hip/knee/
ankle controls are authored hypotheses, not recovered anatomy. Only the distal
paint remains rigid; the calf can foreshorten and overlap behind the thigh.
Sixty-seven yellow guide coordinates denote possible new joint coverage,
not recovered paint or a mask to fill indiscriminately.

One actual ImageGen edit received the base, pose guide, two appearance images
and owner guide. The raw return produced a conventional tall boot and moved
registration. It failed before protected-body restoration; there is no final
sprite or new motion score. A separate one-pose source-part construction tests
whether visible donor materials can supply the bend. Each result must pass
the joint/contour check before any full-cycle expansion.

The frozen experiments live under `art-source/eight-direction-v1/`:
`lyra-contact-rig-pilot-v1`, `lyra-contact-support-strip-v1`,
`lyra-articulated-guide-v1` and `lyra-articulated-imagegen-v1`.
Root's fresh relocated replays match 18, 36, 28 and 16 diagnostic outputs
respectively. Reproducible failed geometry remains failed art.

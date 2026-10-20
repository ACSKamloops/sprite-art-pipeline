# Diagonal paint and visible gait checks

This supplements the directional-bank recipe. Eight directions need actual
diagonal paint; a controller selecting eight names is not an eight-view asset.
Use this when adding NE/SE/NW/SW movement and actions to an existing character.

## Freeze and extend

Preserve old atlas cels, binding IDs and holds before extending them. Repacking
may change file hashes and pixel locations, so compare per-cel decodedRGBA
using each atlas's actual columns. An Emberwake example appends128diagonal
source cels to each frozen bank and repacks at16columns, keeping maximum
texture height small. Its old manifest indices remain valid. Other projects
may use a different format; do not impose these dimensions universally.

For symmetric unarmed designs, NE/SE paint can supply conditional NW/SW
mirrors. A128canvas around pivotX64 needs horizontal mirror plus+1nativeX:
the coordinate mapping is `x_new=128-x_old`, not `127-x_old`. Measure sockets
in the source release paint, then apply the same mapping. This is two new
painted views and four bindings, not four separately authored views.
Asymmetric gear, lighting or costume may need independent paint.

## Extract source ownership before fitting anything

A requested grid can be approximate: actual sheets returned1774×887 for a
requested2048×1024. One whole-sheet nearest conversion establishes the
declared grid; one view scale and shared row anchors establish registration.
Do not independently resize/recenter each silhouette to conceal pose drift.

Nominal cell crops can cut a toe/fist at a boundary and leak that fragment into
the next cell. A source-wide connected-body ownership mask can retain the
overflow with its actual sprite. In the tested unarmed8×4sheets there were
exactly32large disjoint bodies; small islands within3pixels were retained with
their nearest owner and zero components remained unassigned. That is a
measured property of those inputs, not a universal cleanup rule. Preserve all
original pixels and literal mask receipts. Disconnected accessories, particles,
shadows, touching sprites or missing limbs need explicit ownership review;
never delete everything except a largest component by default.

## A colored guide is a hypothesis, not conformance proof

Full eight-pose ImageGen requests repeatedly produced one leading leg twice.
Even a colored full-phase guide did not reliably fix it. Focused two/three-key
requests can supply missing paint, but the first focused trial also failed:
it crossed the hip connections while leaving the same screen-right knee lifted
in both passing keys. The generator followed a visually misleading guide.

Use projected **viewer-left/viewer-right** descriptions and explicit hip,
knee, cuff and sole positions. Colors label authored legA/legB, not verified
anatomical near/far or costume colors. Avoid a very wide crossed opposite
contact whose boot destinations look identical to the first contact. For a
compact128stage, tested guide examples used:

- Left passing: left boot under its own left hip around`[54,95]`, right boot
  planted around`[74,108..110]`. The left boot must visibly be higher.
- Opposite SE contact: left-hip leg reaches down/right around`[68,111]`,
  right-hip leg trails around`[61,103]`; both feet narrowly under the pelvis.
- Opposite NE contact: leading foot around`[68,98]`, trailing foot`[61,112]`.
- Right passing: right boot raised around`[74,95]`, left planted`[54,108]`.

These are authored pose examples for one projection/body, not anatomical
calibration. Measure the actual output: coordinates and lift heights can differ
even when the requested lifted side is now correct. Preserve the actual raw
return and any shared layout transform. Do not report the guide as delivered
geometry. A NE three-cell request returned2172×724; its declared native
normalization was384×128, not the two-cell256×128 transform.

Before building intermediate frames, inspect0/2/4/6 at native and game scale:
which boot is lifted, which remains lower, where each visible trouser chain
joins its hip, whether the stance actually reverses, and which leg is hidden.
Filename labels, distinct RGBA, alpha connectedness and two different hip
labels cannot establish a walking cycle. Reject repeated visible knee roles
even when every source-map check passes.

## Bridge only the remaining small gap

Use complete compatible visible boot/leg donors. Rigid boot plateaus preserve
toe/cuff shape; connect their proximal trouser strips without folds, holes,
paper-thin wedges or old contour remnants. A neutral wide stance with fixed
ankle pitch can look like scissors after translation. Small odd-slot bridges
between real contact/passing paint are a bounded use; a full gait made from
one neutral cutout may need new paint instead.

At crossings, use literal leg-owner polygons or measured row curves rather
than a blind vertical half-plane. Include transparency when erasing old legs,
and protect actual gloves/waist tabs without accidentally clipping new knees.
Mask all old raised-knee/fringe pixels, including those above a nominal hem.
Freeze per-output donor/body roles, sourceXY maps, owners and replay checks.
Unmapped source coverage is an exposed gap, not evidence of reconstruction.

Universal static upper-body restoration can make the result stiff. A compatible
walking upper source or bounded head/torso/arm changes can be compared, with
exact ownership and source hashes. Check hip/hem continuity after replacing
the body: a1–2pixel source-context shift detached a whole thigh in one trial.
Do not call a head/body copied from different poses universally preserved.

## Art, motion and runtime are separate

An overall8.1review can include appearance8.70but motion7.34. It does not meet
a user request for8motion. Preserve separate dimensions, individual defects
and reviewer confidence/perception limits; never choose the overall number
as a substitute for the lower requested dimension. Added frames and exact
durations earn no drawing/motion credit.

The eight-bank controller example validates complete48clip manifests and all
eight release sockets atomically. Movement stays normalized; eight-sector
combat aim stays locked through a committed action; zero input retains the
facing; walking direction changes preserve normalized cycle phase. Paint
projection remains separate from swept ground-plane projectile collision.

Actual engine/browsers must test those behaviors after loading real art.
Synthetic colored fixtures remain explicitly separate. Native frozen release
captures can establish exact24hand alignments; asynchronous browser samples
may miss a projectile and must record an incomplete observation. Compare
locked action snapshots while recovery remains positive, because serialized
key release/browser calls may observe steering after recovery ends.

Art review covers every changed pose/pair, loop wrap, action entry/recovery
and idle turn ring against neighboring cardinal views, on contrasting grounds.
Chronology reconstructed from stills is not human continuous playback. In-place
foot paths also do not prove physical sole contact against world travel speed.

## Current evidence and scope

Project:`/home/astra/projects/emberwake-demo`, branch`codex/eight-direction-heroes`.
Sources:`art-source/eight-direction-v1/`. Rebuilder and invariant checker:
`scripts/bake_eight_directions.py`, `scripts/verify_eight_direction_bake.py`.
Player:`scripts/build_direction_review.py`. Mechanics/release/browser fixtures:
`tests/EIGHT-DIRECTIONS-QA.md`.

At this note's initial update, all three provisional banks load48clips each,
2630artifact invariants,1163production resource assertions,272render assertions
and192ordinary-browser assertions passed against candidate-v2. That candidate
still had rejected walk paint and motion below8. No final8motion or public
eight-direction release is claimed by those results. Later selected assets
must have their own exact hashes, revised art judgments and runtime receipts.

## Later cold reviews and bounded repairs

The first complete four-key bridge package was reproducible but its cold walk
review scored appearance 7.3 and motion 6.1. A subsequent local join-repair set
scored appearance 7.1 and motion 6.0 in another cold review. These are separate
subjective judgments, not an improvement measurement with one calibrated
reviewer. Both found actual cuff/thigh cuts and abrupt front-view arm/waist
presentation changes. These packages remain unselected. Do not inherit an
8/10 approval from successful maps, source ownership or either producer.

Material ownership matters when editing a seam. A one-row empty cut through
an existing brown cuff/boot should be filled with the neighboring leather,
not covered with a large flat gray trouser polygon. The latter removed the
hole but created an obvious squared material block. Prefer sparse local
source-colored fills and literal spur erasures; inspect the material before
choosing the palette. New complete knee/boot paint can still be needed.

A useful targeted paint test combined the existing Lyra upper body with a
complete, already readable Rowan raised-right-knee silhouette below row 78.
ImageGen repainted the white trousers charcoal and the boots warm brown,
while retaining the supplied leg silhouette. That produced a visibly clearer
opposing knee than a verbal eight-frame prompt. The source character was
explicitly positional geometry only; the target references supplied identity
and materials. Whole-stage nearest normalization and exact upper restoration
were retained. This one-key result does not establish a good whole walk.

Source: `art-source/eight-direction-v1/lyra-opposite-knee-v1` retains the actual
request, both actual inputs and raw return. `lyra-walk-repair-v1/replay.py`
checks frozen geometry, reconstructs the editable project, replays sparse
material edits and verifies undo/redo for 16 frames. It is a source-map/editor
proof, not an art pass. A steadier head/torso experiment remains a separate
candidate until judged in the complete sequence.

For a real tiny correction, `brann-eye-v1/replay_editor_edit.py --out FRESH`
replays five donor-colored eye pixels per idle cel through the construction
toolkit, then actually saves/reopens the exported animation with LibreSprite
and checks its pixels/project. Two 29/50-second holds remain authoritative.
Keep the entire intended two-frame pair in the review packet. One reviewer
mistakenly tested each replacement against the other old guard frame, creating
a guard/relax toggle that was absent from the intended pair. That report was
superseded with an explicit correction; other unchanged comparisons were
preserved. Review manifests must bind ordered frame sequences and clocks,
not just a bag of correct image hashes.

The actual game uses nearest texture filtering. A Lanczos 84-pixel proxy of
0.66x is a different rendering and can soften a defect. Label rounded 84/128
proxies, inspect nearest alongside other previews, and retain actual Godot
rendering for final claims. Still chronology does not certify continuous
normal-speed fluidity, physical ground contact or controller feel.

## Charge tracks and later rejected geometry

A fixed release-hand socket is unsuitable for the preparation glow when the
painted hand moves. Retain an ordered native hand point per scheduled cast
exposure, bound to the actual source cel/hash. Repeated physical cels must use
the same point; the release exposure must agree with the existing fixed release
socket. Validate finite coordinates, bounds and sequence length before texture
loading, preserving a working actor on rejection. Follow the displayed cel,
including the initial exposure before the cast clip first presents. Keep the
projectile/flash release socket, action event and collision plane separate.

The Emberwake v6 example retains measured tracks for all eight views of all
three heroes under `art-source/eight-direction-v1/cast-track-measurements-v1/`.
`registration-v6-all-charge-tracks.json` bakes those points without changing
the candidate-v2 walks. Its independent verifier passes 3,140 artifact checks;
the broad engine suite passes 1,804 assertions plus 378 route samples. Separate
actual GPU checks render 24 releases and 48 preparation pairs, with 657
assertions, retained under `docs/evidence/eight-directions-systems/charge-track-v1/`.
These are point-in-time mechanical receipts, not a motion score. Inspect the
marked actual paint and the rendered effect; proximity to opaque pixels alone
does not identify a glove.

The subsequent blinded Rowan contact comparison modestly preferred the deeper
complete-thigh/boot control (appearance 7.7, motion 6.4) over a narrowed manual
edit (7.2, 5.8). The producer initially preferred the narrower edit; preserve
that disagreement and the frozen findings instead of selecting a favored
number. Complete new Brann lower paint likewise scored appearance 7, motion 5:
full boots did not fix upper-body resets, squared rear cloth or missing tabard.
Neither package meets the target. Source-exact complete parts still require
believable shape, proportion, occlusion and the full ordered cycle.

Steady-upper experiments must own complete forearm/glove transparency and
remove old waist fragments. A clipped old source cannot supply a complete
glove merely because the mask is exact. Restore missing hanging accessories
from an explicitly declared donor behind the leg owners, and examine every
affected phase. A completed editor replay proves the edits can be reproduced;
it does not approve their silhouette or anatomy.

### Transparent owners and body underpaint

Complete transparent arm ownership is necessary to remove an old glove; it is
not permission to cut valid body paint behind a newly positioned arm. A later
Brann cycle exposed one-pixel background slits through the inner sleeve/torso
at poses 03–05. The source-bound review preferred its complete gloves and
restored rear accessory, but rated motion 5.9: a steadier torso plus nearly
fixed hands still did not create a convincing full-body walk.

The bounded `brann-underarm-shadow-v1` trial paints 79 explicit transparent
channel pixels with existing same-cel dark torso-edge donor colors. Its
literal coordinate/color witnesses and actual guarded editor journal replay
all eight frames exactly, including undo/redo. Root inspected the real 4x
before/after. Boots and contact coordinates remain exact. This is authored
shadow underpaint, not recovered hidden anatomy or full-gait acceptance.

For reusable-part motion, remove old parts first, supply the missing body
underpaint deliberately, then composite complete arm paint in its proper
occlusion order. Preserve legitimate outside elbow space. Never globally fill
all transparent gaps or paint an entire joint gold merely to close a seam.
An anchored proximal sleeve and a rigid complete cuff/glove can then carry a
modest counter-swing; the complete ordered cycle still needs a fresh review.

### Complete transitional paint, not a whole-sheet reroll

The Rowan front-diagonal 05 repair uses the actual complete neighboring 04/06
paint and a complete source-part placement guide as context for one bounded
ImageGen edit. It paints two connected trouser/boot paths where the previous
pose stacked the feet under a compressed pale band. Register the actual
1254-square return once to128; then restore the original blue/gold hem and
complete gloves. A broad lower-owner mask admitted some old hem pixels, so
the first preview and the later torso-protected composite remain separate.
Do not restore old pale trouser fragments under the guise of protecting a hem.

`rowan-five-bridge-v1/` retains the actual inputs/request/raw, rejected source
proposal, final mask/map and single guarded editor transaction. Fresh raw
construction and journal replay both match all eight RGBA/PNG files, and undo
is exact. The new05 has two pixels of disclosed sole-depth drift; it is not
foot-contact calibration. A fresh SE/SW comparison preferred it and rated
appearance8.1, identity9, motion6.1, usefulness6.7. Thus better transitional
paint cleared a drawing threshold while the complete gait remained unresolved.
The next demonstrated issue was the abrupt06→07 return and unequal projected
role timing. Do not infer8motion from8appearance or repeatedly rerate the same
unchanged cycle. Actual timed human viewing remains a separate check.

### Complete distal parts across independently painted transitions

An opposite-contact04 and a return07 can each look cleaner in isolation while
making the combined walk worse: different generated boot shaft lengths,
trouser volumes and cuff boundaries interrupt persistent leg tracking. The
actual combined Rowan trial did not pass its frozen full-cycle comparison
(appearance6.7, motion5.0). Preserve that rejection and the exact input set;
do not average it with another critic's unrelated grades.

Test a complete distal-part hybrid before asking for more whole-leg paint.
Remove the replaced boot under an explicit owner, translate a complete good
same-view donor without scaling or reflection, preserve generated proximal
trousers, and author only the bounded cuff connection with literal source
colors. Record front/rear occlusion and every donor coordinate. A visible
cutout is not recovered hidden anatomy. Matching soles and exact source
pixels still do not establish gait acceptance.

Check the actual pose landmark after every model return. A further Rowan03
cleanup landed at sole116 where its intermediate guide ended at108, nearly
repeating contact04. Its clean complete paint was rejected; no per-pose fit,
new call or export count was used to disguise the early landing. The direct
source-map guide remains a separately labeled candidate.

The project helper `scripts/build_walk_pair_review.py` freezes eight native
RGBA cels per variant, rational holds, appearance/cardinal context and hashes.
Mirroring is explicit opt-in for the tested symmetric unarmed costume. Its
parent mapping stays outside the anonymous input directory. This is a
case-specific review-packet constructor, not a general anatomical animator.

The actual direct03 plus complete-boot04/07 trial modestly improved readable
exchange in a fresh frozen comparison (appearance7.8, motion6.8). Its remaining
trouser/cuff volume pulse is strongest06→07→00. Repair proximal clothing with
compatible bent source paint instead of retaining generated shorts merely
because their pixels are exact. Complete boots alone do not preserve the leg.

For timed local comparison, the project's `build_walk_pair_player.py` copies
and verifies the packet's images, then builds a direct-PNG pause/step player.
The optional MP4 streams576RGB ticks toFFmpeg at160fps, preserving nine ticks
per exposure without thousands of redundant PNG files. Browser checks on the
tested player verify all32 fetched hashes, rendered phases and actual playback;
they do not supply a motion score. Keep earlier human-review URLs frozen when
adding a new candidate.

### Frozen follow-ups and measured projection repairs

Use the review's demonstrated defect to choose the next experiment. In the
Emberwake front walk, fuller rounded source03 trousers and bent source06 paint
under07 modestly improved a critic's motion judgment from6.8 to7.0. A genuine
04.5 projected midpoint added only0.1. Retiming the same drawings cannot earn
a confident timing preference from static sheets. A separate shoulder and
counter-arm trial tied its control at game size; retain that result and keep
the simpler body rather than increasing motion amplitude without evidence.

The next useful repair was the actual foot path: old05 moved its low boot
inward and then outward again between04 and06. Rowan's source05 complete
foreground leg could retain its paint/volume while an anchored proximal field
reached a rigid-3px distal translation. Lyra's two distinct source06 leg
surfaces could progress from04(+4,+4) through05(+2,+2) into06(0,0), with
separate cuff/proximal controls. These are authored projected surfaces, not
anatomical recovery or measured world contact. Both comparisons improved a
scoped motion judgment from6.5 to7.0; neither reached final motion acceptance.

For a sole-plane snap, choose a compatible real same-view boot projection and
use separately owned cuff/calf/ankle/heel/toe bands. A Brann03 repair reduced
the sole-facing change and improved a scoped motion judgment from6.5 to7.0.
Its tiny partial-alpha joint still needed explicit dark source underpaint.
When layering behind a partial-alpha front, preserve the frontRGBA and record
the exact integer source-over result; blended outputRGB is not a direct donor
texel. Never claim complete hidden limbs from these visible cutouts.

Freeze an exact control and carry its prior score in a same-critic follow-up
after verifying all unchanged hashes. Inspect every cyclic pair again; a
repair of03 cannot erase the unchanged06→07 weakness. Different critics'
absolute grades are separate judgments, not a calibrated improvement series.
Do not transfer these scores to a rear view, another actor or another action.

The review helper now supports a declared primary NE bank and explicit NW
mirroring, as well as the original SE/SW case. Actual rear-only packets found
the same tradeoff: source-guided alternation improved gait legibility but
pinched trouser/cuff joins and boot overlap reduced cel finish. Preserve the
orange rear sash or other identity accessory under its explicit owner.

### Rational playback without oversized scratch exports

The comparison helper accepts variable exposure counts and rational per-variant
holds. All currently tested variants preserve the0.45s cycle. A04.5 midpoint
can split only04's hold and preserve every original key-start time; a separate
retiming trial intentionally changes those times. Use one elapsed clock with
independent phase lookup per variant, including manual stepping and loop wrap.
An8-exposure and9-exposure side cannot share the same frame index.

Stream cached distinct phase-pair RGB buffers into FFmpeg at the rational
clockLCM (160/320Hz in these tests) instead of saving thousands of duplicate
tick PNGs. Keep lossy MP4 as review transport and sourcePNG/RGBA authoritative.
The primary NE player and SE player have actual browser tests for fetched
hashes, all exposures, mirrored direction, grounds, loop wrap and video
decode/advance. Those checks are not observed human motion approval.

Browser Canvas2D may round alpha-composited RGB differently between GPU and
CPU canvases. One actual diagnostic measured maximum1RGB with zero bytes
beyond1; preserve that evidence and use that scoped tolerance for the rendered
comparison while retaining exact PNG hashes. Do not silently generalize the
tolerance or call browserRGBA byte-exact. Retain a failed no-video expectation
and its corrected optional-video scenario instead of deleting the failed run.
Keep full editable projects minified, journals literal and portable inputs
closed; compact replay receipts and explicit external-helper qualifications
avoid duplicating large scratch trees without weakening source evidence.

### Real renderer and failure evidence

An isolated game preview can load preferred unfinished walks before final art
approval. Resolve each asset through the real character catalog; Rowan uses
`assets/hero`, while additional heroes use `assets/characters`. Preserve the
original installed banks and record the six actual replaced atlas/manifests.
The tested8-key preview passes3140 artifact invariants and1804 engine checks
plus378routes. A real OpenGL Hero/Sprite2D fixture additionally captured1728
GPU frames across3heroes ×2primarydiagonalviews and passed8684 assertions.
Distinct held poses and repeatable pixels are renderer evidence, not8motion.

The fixture samples at(tick+0.5)/320s and captures two0.45s cycles; explicit
158px/s translation is a render fixture rather than controller/sole-contact
validation. Six288-frame/.9s MP4s preserve those sample times. A17-assertion
browser check verifies actual encoded hashes, selections, decoded body pixels,
playback, speed and route wrap. Do not call this AI observation of continuous
motion. In the original receipt, the crop consistency digest hashes UTF8hex
text ofRGBA, not rawRGBAbytes; preserve that qualification and use the precise
field name in future runs.

The bake refused distantalpha1 black pixels at the canvas edges of four Brann
cels. Keep that rejection. A separate case-scoped export erased165 exactblack
alpha1/2 pixels farther than3nativepixels from the mainalpha24 body across16
walkcels. All otherRGBA and original sources/reviews stay exact. Retain every
literal erasure, its source witness, exact undo, fresh local replay and the
undetermined speck-origin qualification. Do not globally threshold alpha or
silently erase particles/equipment. The bake gate remains strict.

A new02.5 drawing bridged Brann's boot position but introduced a seven-pixel
enclosed cuff slit, so the frozen whole-loop critic preferred the8-key control.
Keep that failure separate from a later literal charcoal underpaint repair.
Distinguish an enclosed joint hole from legitimate inter-leg clearance; fill
only the demonstrated defect with declared source-colored continuation. More
drawings and exact original timestamps do not establish a better animation.

### Inspect generated patches before restoring protected paint

A cloth edit needs an explicit owner including the small transparent envelope
required for its new contour. A positive-alpha-only owner can merely recolor
a pinched thigh. Author that envelope against actual upper, glove and complete
boot owners; do not use blind dilation. In one Rowan NE edit, four native128
cels formed a256-square grid, enlarged as one1024-square input. The actual
return was1254-square. One whole1254-to256 nearest transform and four fixed
crops preserved that layout; no per-cel fitting occurred.

Inspect normalized raw cuffs, soles, pose roles and material volumes before
restoring original protected paint. All four core sole rows remained fixed,
but one crossing cuff moved about two rows. That pose was excluded: restoring
its boot would conceal raw nonconformance rather than prove a good joint.
Another proposed patch respected the owner but made a pinched shadow below
a protected gold hem stronger. It was self-rejected despite exact outside-mask
pixels. Keep per-pose exclusions, actual raw return, actual ordered inputs and
the exact request. A zero-call preparation manifest stays historical; record
the later actual call separately rather than rewriting preparation evidence.

The seven-pixel Brann midpoint cuff repair removed the flaw, but its follow-up
tied the eight-key control at7.5motion. A separate32pixel source-colored
leather contrast trial improved enlarged creases without a convincing84px
benefit on forest ground; it remained unselected. Neither result supports8.

An automatically selected dark leg surface can include an old glove contour.
In Lyra03, the sourceXY map proved that a horizontal spur came from the key02
glove, while the current glove ended three rows above it. The scoped repair
removed16 remnant/halo texels and restored one underlying hip texel from its
actual retained source. Erasing that composited texel outright would make
a new hole. Verify source-layer ownership before erasing a suspected spur;
darkness and screen position alone do not identify anatomy. This is a drawing
repair, not evidence of better gait timing or weight.


### Preserve layers without forbidding natural depth overlap

For a local knee patch, exact visible protected boots are a useful constraint.
For an intentional body/arm rig, that output constraint can be too strong:
a one-pixel downward glove translation overlapped eight real upper-cuff pixels
in the Lyra00 source. Exact shifted glove pixels and exact visible boot pixels
cannot both occupy the same output coordinates. A broad boot-library polygon
missed those texels; the actual source layer proved they were leather.

Keep the failed strict-constraint diagnostic. A separate declared composition
experiment may preserve the complete boot layer, sourceRGBA, geometry and
support position while letting a foreground glove occlude its top naturally.
Record every newly occluded boot coordinate and the actual glove source witness;
check the combined anatomy and depth order visually. Do not label the composited
visible bootRGBA exact or restore the boot over a foreground hand just to pass
a pixel assertion. This is an explicit ownership/composition decision, not new
hidden paint, an anatomical recovery claim or automatic animation approval.


A subsequent Lyra body-field preview failed both joints and material ownership:
a broad neutralRGB selector admitted leather/outline texels into the charcoal
owner. An unchanged lower partition was therefore not a complete-boot proof.
Examples were source02[52,87]=[31,16,11] and source06[66,85]=[17,7,2]. Keep the
failed maps and qualified receipt. Review literal native cloth/leather/outline
boundaries rather than tuning a color threshold until it passes.

A nominal cuffY below the last actual cloth row can let the cloth edge retract
when the body rises, even with a monotone field and unchanged boot. Bind the
fixed plateau to reviewed per-column painted seam endpoints. Distinguish that
construction defect from genuinely missing paint exposed by a moved coat.
Explicit newly authored source-colored underpaint is a separate visual decision,
not recovered anatomy. Neither a failed partition nor a valid waveform decides
whether the same intended body curve can work after a correct construction.


### Complete real tool exchange and retain observer failures

Lyra's corrected body-weight construction finally needed38 explicitly authored
source-shaded charcoal undercoat pixels, separate from ownership/map repairs.
Nine were genuine coat disocclusions;29 finished other waist exposures. Two
04 source-field pins restored existing coverage without new paint. Literal
source palettes/coordinates and all new coverage/depth witnesses are retained.
Normal arm/glove clearances stay open. The frozen critic prefers the added
weight cue at7.5motion; brisk02→03/06→07 remain, so this does not establish8.

Actual editor exchange can expose a compositor mismatch even when the source
maps and component layers are exact. All40 Lyra component cels survived real
LibreSprite1.3 save/reopen, but its normal compositor rounded two overlap texels
differently from the toolkit integer source-over. Retain that evidence. The
primary exchange therefore uses honestly flattened approved final paint, six
actual guarded transactions, journal/undo/redo and exact native save/reopen,
reimport and renderedRGBA. Keep the upstream five-layer project as editable
construction, not a false exact external-render claim. Portable source and
journal replay reads local retained inputs without a model, network or native
editor requirement; it verifies the retained actual native-tool evidence.

A source-layer can remain exact while newly foreground paint changes visible
RGBA. Brann's complete P boot layer persists under newQ; nine previously visible
P texels are naturally occluded. Restore actual retained source paint newly
revealed after oldQ removal; call it source-based construction, not recovery of
hidden historical anatomy. Whole donor Q boot translations preserve its paint
and volume but do not establish grounding or anatomical rig correctness.

Keep browser observation failures separate from gameplay and art. An original
v8 run passed180 assertions before a short-action wait timed out, with two
incomplete projectile samples. Its old point samples cannot identify the cause;
a nominal seven-tick cadence alone does not prove the window was missed.
The later read-only observer publishes at30Hz with fractional carry and records
a bounded trace before real action-key delivery. Return the matched snapshot
rather than doing a second current-state read. Require the original late
threshold, actual opposite input, empty released pending-hit, committed aim in
every observed locked state, completion and current-cast projectile evidence.
Do not filter bad states away or retry missing samples until pass. The new
ordinary v9 browser run passed193 assertions across24 action traces without
incompletes/errors. Max observed physics-tick gaps were3–4 in those traces;
this is sampled coverage, not proof of every tick or measured zero overhead.

At game speed158 and loop.45, the root travels71.1worldpixels each cycle.
Apply actual .66 drawscale when evaluating backward foot travel. Follow literal
same-source sole/ankle witnesses and explicit contact assumptions; screen-low
sole contours may belong to swing or perspective. Test transverse as well as
longitudinal residual. In-place pixel consistency and a translation renderer
fixture cannot certify absence of skating. Contact acceptance is separate.


### Reuse a rig method without inheriting its material owners

A body-weight curve that worked on one hero did not safely transfer to Rowan.
Old source02/legacy05 masks omitted actual current hem, hip and glove overlaps.
Even a direct current-paint split left cloth-map losses and waist gaps. A
separate31-pixel source-shaded interior completion filled its nominated losses,
but30 uncertain gaps and25 existing-cloth mapping losses remained. Both stages
were frozen as rejected; no editor package or art score was forced. Keep the
better existing walk. Source maps can replay an incorrect partition exactly.

Inspect the whole current painted upper contour and explicit depth order on
every affected cel. A legacy pilot assembly is not authority for paint added
later. Correct real inverse-field/material-boundary losses through the actual
map; use authored undercoat only for genuine new coverage. Do not treat normal
arm/leg clearance or intended silhouette retreat as a hole. If the necessary
anatomical/material split remains ambiguous, qualify or reject the construction
instead of globally filling transparency. Preserved lower rows alone cannot
certify that every boot cuff and overlap was correctly identified.

The portable selected-v9 contact study verifies38 literal source/RGBA witnesses.
Its strongest Lyra04→06 support hypothesis has3.7335worldpixels of backward
sole/ankle travel against17.775root travel, leaving14.0415over112.5ms at158/.66.
The corresponding33.19px/s scalar fit is calculation only, not a recommended
game speed or a certified stance. A Brann recovery run moves transversely;
Rowan uses changing donor drawings; rear swing intervals are excluded. One
speed/clock fit cannot be presented as a general fix. Actual renderer and
contact-aware rig tests have separate receipts and acceptance.


### Verify ground-relative material pixels in the actual renderer

In the existing v9 Hero/Sprite2D GPU captures, first search an actual opaque
2x2 sole or3x3 ankle-shading context inside a bounded boot window, then validate
the unique match against source texels and the exact .66/pivot footprint. One
repeated RGB value is not an identifiable material feature; missing context
matches at a new subpixel phase remain missing evidence. Final framebuffer
alpha255 alone does not prove source opacity. Use alpha255 source samples and
explicitly qualify foreground occlusion and nearest-downsampling loss.

For nine bounded Lyra images,15 unique context detections yielded100 exact
opaque GPU-to-sourceRGBA witnesses. A fixed3x3 floor-grid block was identical
across all nine images. Both sole and ankle features moved(+6,+6) actualpixels
during one held04 cel and(+10,+10) across04-to06:14.1421pixels alongSE versus
14.0415 predicted. This confirms real displayed drift against the floor in
this authored translation fixture. It does not infer actual plantar contact,
exercise live controls/collision/camera, or approve the full loop. Preserve
ambiguous colors and missing matches, all source/PNG hashes, exact projection,
pixel-center/raster tolerances and the fixed-coordinate annotated crops. The
portable local replay reproduced all11 diagnostic outputs byte-for-byte.

# Unarmed hero action set — 2026-10-22

The user requested run, walk, attacks, dash/dodge and the other states needed for
a game character. The follow-on package extends the previous six-action bank to
17 declared states across eight directions, preserving the exact preferred SE
walk and the current source-owned SE jab.

Local delivery: `/home/astra/artifacts/hero-action-set-20261022/`.
Start with `START-HERE.md` for the current checkpoint and `COVERAGE.json` for
the original coverage contract. `package-v1/` and its actual Godot Web export
at `play/` are preserved; the provisional selected refinement is `package-v2/`
with its separately tested Web build at `play-v2/`.
Generation remains built-in OpenAI ImageGen; no H3/local model was run.

New painted families: run, dash, dodge, jump, knockdown, get-up and interaction.
Guard, stun, crouch, landing and death are explicit source-pose/state bindings.
Jump anticipation stays grounded for 0.1 s; the engine applies flight height and
root travel afterward. Death holds its final drawing; knockdown gets up.

Known failures remain in the comparison bank: repeated leading leg in several
runs, S dash turning diagonally, head/hand drift and flat lower silhouettes in
some northern raw outputs. No source pixels were lost for those flat cuts; they
are generated-art defects. A focused SW run retry failed and remains unselected.
A partial NE retry supplies only some opposite-support poses and remains separate.

Selected bounded repairs: the S run mirrors a declared body region for the
opposite half-cycle while retaining head/scarf paint; exactly17 neighbouring
fragment pixels were erased from S dash without claiming to fix its facing;
SE get-up was repainted from the actual fallen pose to avoid reversing the body.
Source maps, masks, prompts, raw outputs and literal journals are retained locally.

The native Godot run checks 136 selected resources/544 exposures, exact decoded
RGBA, 1,001 controller assertions and actual input/state transitions. Web PCK
loading and browser execution have separate receipts. These checks establish
transport and state behavior, not art quality, collision, damage, invulnerability,
modular weapon compatibility or the requested9/10 acceptance.

Reusable lessons are in the ImageGen skill's
[coverage/recovery reference](../../skills/imagegen-sprite-animation/references/action-coverage-and-recovery.md)
and animation skill's
[state contract](../../skills/sprite-animation-pipeline/references/character-state-contract.md).

## Follow-on refinement

Local comparisons now live at `http://localhost:8903/quality-round2/`, with
sources and reports under the same artifact root's `quality-round2/` directory.
The original `package-v1/` and preferred walk remain preserved. This pass adds
S-run bridge/scarf trials, a front-facing low dash with recovery bridges,
SE get-up bridges into the actual idle, targeted northern fall completions and
several SE-run lower-body experiments. Trials and rejected paint are retained.

Frozen cold reviews favour the newer frontal dash recovery and NW fall/get-up
join, but do not establish the requested 9/10. The N-fall repaint lost narrowly
to its control. SE-run reviews disagree; a repaired source mask is not an art
promotion. Exact frame/hash/clock checks and real browser playback transport are
documented separately from these ordered-still judgments. New captures and
selectors belong to their own receipts; the earlier Godot numbers above apply
to the original package, not automatically to follow-on art.

The subsequent canonical-reference audit found that the old SE idle was broader
and offset from the preferred walk. A source-only neutral now preserves the
preferred complete upper and uses a planted source stance. A coupled get-up
approach and its literal hurt/landing neutral dependencies were rebuilt together.
This corrects a shared reference mismatch; it does not certify all action exits.

`package-v2/` selects nine changed bindings, including the dependent states:
S run/dash; SE idle/get-up/hurt/land; NW fall/get-up/death. There are still136
selected states, now553 exposures. Original package-v1, all other selections and
the preferred walk remain intact. The experimental SE-run repaints and N-fall
repaint were not promoted. The latest get-up still has an abrupt07→08 rise.

`http://localhost:8903/play-v2/` is the separately built Godot Web inspector.
Godot4.7.2 resource save/reload verified136 animations/553 exposures, and the
controller check passed1,001 assertions. Actual Web PCK loading and Chromium
keyboard captures passed separately. LibreSprite batch save/reopen preserved31
frames across four changed clips; no editor GUI painting is claimed. The
comparison page loaded115 distinct source PNGs with exact browser RGBA and
working controls. Full receipts are in `quality-round2/browser-proof/`,
`quality-round2/editor-proof/`, and `godot-v2/`.

Cold review6 preferred the canonical neutral at8/10 consistency/usefulness and
the new dash at6.5/10 usefulness. The disclosed-context review7 preferred the
rigid-upper get-up at7/10 usefulness. These are scoped ordered-still judgments;
there is no whole-set9/10 acceptance or continuous-motion human approval.

## Whole-rise identity and support transfer

Round3 comparisons are at `http://localhost:8903/quality-round3/`. These remain
experiments beside package-v2. A corrected canonical appearance reference gave
newly painted rising-leg/body keys; complete preferred head/scarf owners were
then attached at explicit per-pose neck positions. A whole-rise head track
removed the late identity cut without changing the earlier body/leg mechanics.
An explicit foreground-knee layer corrected the scarf depth at one key.

Frozen anonymous review preferred that whole-rise identity treatment: identity8,
progression6.5, overall7. Its predecessor was overall6.5. A separate equal-clock
bridge review preferred the new late upper-body positions modestly but rated
both full clips overall6: they still lack explanatory support transfer. These
are separate packets and comparisons, not an averaged or rising acceptance
score. Neither establishes continuous-motion quality or the target9/10.

Part interpolation exposed missing collar/sleeve cloth. Explicit new underpaint
layers closed those gaps; they are authored paint, not recovered hidden donor
texels. A source-arm release bridge improved its wrist path locally, while a
rigid rear-leg companion disconnected the body and was rejected. A single new
painted release pose supplied connected anatomy but put the hand near the next
key rather than halfway. Its canonical-head repair did not fix that phase error.
A bounded manually articulated arm hybrid was compared separately. A fresh
four-way blind review preferred the shorter original painted arm; the repair
read as stretched over the leg. Its best full-action judgment remained6.5.
Correct wrist coordinates did not imply better anatomy or motion.

The full-action audit identified a larger earlier seated-to-kneel organization
jump, support-foot repositioning and compressed middle timing. An equal-duration
same-art retiming diagnostic preserves those anatomical defects; it does not
claim to redraw them. A four-pose text-conditioned replacement also failed to
follow the requested support/stage progression and remains rejected. A separate
visual-guide-conditioned repaint used connected schematic poses, followed by
declared row/column registration, literal head/boot restoration and bounded
ankle/contour editing. A fresh blind review preferred the older middle narrowly
(6.5 versus6 overall): the new exit was cleaner but its repeated middle staging
and linked leg anatomy were weaker. That repaint was not promoted. Actual
LibreSprite save/reopen verified its ten frames and holds; this transport check
does not override the art judgment. Neither prompted coordinates nor stable
boot pixels prove coherent generated anatomy or support.

The separate brisk-walk timing control retains all16 preferred walk exposures
and13 unique RGBA drawings, accelerated by the actual run/walk speed ratio8/5.
Its5/8s loop supplies no new run or flight pose. A world/native unit error in the
first diagnostic was preserved and corrected: the inspector's160 world units/s
becomes160/3 native pixels/s at its3x actor scale. Actual browser source and
corrected-scale rendering checks are in `quality-round3/browser-proof/`.

A bounded audit of the other seven idle/walk pairs found no clear repeat of
SE's enlarged, offset idle. No other-direction art changed. Fifteen literal
idle-identical selected endpoints identify coupled future contracts, not
historical copying or accepted action progression.

The reusable process and concrete failure decisions are in
[canonical-reference-and-head-track.md](../../skills/imagegen-sprite-animation/references/canonical-reference-and-head-track.md).
Raw generation, maps, literal paint journals, equal-clock controls and frozen
review inputs remain in the local artifact root. Exact source/editor/media
replay and the existing Godot checks do not automatically validate changed
round3 art.

## Package-v3 and authored-motion guide experiment

The separately tested local build is now `http://localhost:8903/play-v3/`.
Library SHA256:
`e7366d1364090c36c24496a06844d1e554163275b721ea0f4051d6afdf280c44`.
It has136 selected bindings and561 exposures at a common9600-tick clock.
Compared with v2, only SE get-up and SE run differ semantically; the other134
bindings keep their exact RGBA, rational holds, events and loop flags.

The get-up selects the whole identity track and the shorter original painted
arm in exit-preparation06. A frozen three-way review preferred that complete
pose, with overall6.5; this is a provisional selection, not a9/10 pass. The
run-button fallback uses all16 preferred walk exposures and13 distinct drawings
at a5/8s loop. It is explicitly a **fast-walk alias**, with no newly painted run
or flight phase. The original preferred walk remains exact and unchanged.

Fresh package-v3 receipts establish:

- Godot4.7.2 resource save/reload:136 animations,561 exposures and exact pixels,
  rational durations, loop flags and speeds.
- Controller/input check:1,001 assertions,96 direction/action completions,
  ten physical action inputs and eight physical direction inputs.
- Actual exported Web PCK loading plus separate Chromium WebAssembly keyboard
  captures of knockdown/get-up, fast movement and dash, with no JS errors.
- Actual external LibreSprite batch save/reopen of26 selected get-up/run
  exposures, with exact RGBA. Run's625ms total is represented by rounded
  integer-ms preview holds; rational5/128 holds remain authoritative.

Receipts are under `godot-v3/`, `quality-round3/editor-proof/` and
`quality-round3/browser-proof/`. File/editor/runtime validation remains distinct
from animation art acceptance. Package-v1/v2 and their playable exports remain.

The read-only eight-view fall-to-rise audit found one demonstrated boundary gap
in S: the roll/recenter and acquisition of the new two-palm support are skipped.
The other seven boundaries did not establish a repair need in that inspection.
Literal endpoint inequality alone was not treated as a defect. Read the actual
SE pixels as supine/face-up; an earlier report's "side-prone" label was loose.

For the remaining whole-body support problem, an official CC0 source supplies
real authored choreography rather than another isolated joint-coordinate guess.
Quaternius Universal Animation Library2 Standard's `LayToIdle` has47 stored
samples across46/30 seconds: supine→hands-behind seat→feet-loaded squat→stand.
The local guide changes only the three Head-scale curves by2.05 and retains
the other647 scalar curves and animated head pitch. One fixed camera gives
64px standing geometry and fits all47 samples. This is pose geometry, not a
complete chibi retarget, measured physical contact or provider reconstruction.

The saved six-pose ImageGen test uses exact separate appearance, motion and
entry/exit references. Its actual1024×1536 return has partial alpha and a crown
crossing a nominal cell boundary. A regular import and128/200-alpha diagnostics
remain unchanged. Full-image connected-character ownership, original512-cell
origins and a single0.90 scale about(40,72) recover that crown and remove the
neighbor's fragment without per-frame fitting. Six new complete figures plus
literal source bookends form an eight-key1.2s study. None of those import facts
proves the model followed the guide or produced better motion. The new sequence
is reviewed separately against the old ten-key sequence uniformly retimed to
the same1.2s; this compares complete designs, not a drawing-only causal test.

The exact source/license, guide, prompt, raw result and ownership maps are local
under `quality-round3/getup-reference-scout/`, `professional-getup-guide/` and
`professional-getup-paint/`. The official source is
[Quaternius UAL2](https://quaternius.itch.io/universal-animation-library-2).
The selected source GLB is not bundled in this methods repository. No H3,
local generative model or paid-provider job was used.

### Later package-v4 selection and reusable skill

`http://localhost:8903/play-v4/` selects the new source-guided get-up with a
source-part support-release key and the revised upper-only settle. Its ten
exposures total1.2s. Library SHA256:
`1eecc125297d9910693f74f226d40062f03a53bfc51c391bf62dedc08f20d04b`.
Only `get_up_SE` changes versus v3;135 bindings preserve exact RGBA, rational
holds, loop flags and events. The preferred walk and all earlier banks remain.

The new eight-key design was preferred7.5 versus the uniformly retimed old
design6. A separate blind2×2 edit study preferred a support-release key modestly,
but found the first settling warp pinched a knee/cuff. The revised settle locks
the entire lower body from row53 and deforms only the waist below its rigid
upper. Another frozen comparison preferred it narrowly7.2 versus7.1/7.0.
These are independent packet-specific judgments, not an averaged trajectory,
continuous playback approval or the target9/10.

Actual v4 checks passed:136 animations/561 exposures at9600 ticks;1,001
controller assertions; exported PCK load; Chromium WebAssembly input captures
showing get-up and return to the actual idle; ten-frame external LibreSprite
save/reopen with exact RGBA and1200ms total. The two native62.5ms settling
exposures become63/62ms in that integer-ms preview; the rational source clock
remains authoritative. Receipts are under `godot-v4/` and round3's editor/browser
proof folders. The latest comparison receipt covers18 cases and286 distinct PNG
paths with exact Canvas RGBA, not new art acceptance.

The skill bundles `scripts/render_motion_guide.py`, a generic supplied-input
config and a frozen80px source-settle replay. The original helper's47-frame
test and audited revision's11 malformed-config checks plus three-frame smoke
remain distinct. The included fixture reproduces the lower-protected settle;
its map is not a hidden anatomical rig. Source GLB/license inputs must be
supplied separately; generated `.blend` files embed source-derived assets.
See [the method](../../skills/imagegen-sprite-animation/references/authored-motion-guides.md).

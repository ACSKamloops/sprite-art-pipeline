# Two source-colored lower-body bridge probes

This bounded experiment adds two actual cels to the new ImageGen 1.5-guided walk,
using only its existing paint. It does not build or approve a full 16-frame walk.
The external source is `imagegen/a15-run01/clips/nearest-binary64-reference`
under the refinement artifact root; the recipe binds its exact project hash.

```bash
/home/astra/projects/sprite-art-pipeline/.venv/bin/python \
  research/pixelengine-imagen/tools/probe-lowerbody-bridges.py \
  --source /home/astra/artifacts/pixelengine-imagen-refinement-20261020/imagegen/a15-run01/clips/nearest-binary64-reference \
  --recipe research/pixelengine-imagen/tools/a15-lowerbody-bridge-recipe.json \
  --output /absolute/fresh-probe
```

All eight source keys remain pixel exact at their original onsets. Only the
125 ms holds after keys 2 and 3 subdivide: source key for 62.5 ms, then an actual
bridge for 62.5 ms. The resulting ten-cel candidate is still exactly one second.
The separate timing-only control has identical ten slots using duplicate source
paint, proving that the actual new drawings are distinct from FPS-only uplift.
APNG rational holds are authoritative. ASE millisecond previews necessarily
quantize 62.5 ms with cumulative 62/63 ms boundaries and retain exact ticks in
their sidecars.

Pixels above y54, including the complete head, torso, arms/gloves and scarf,
remain byte exact from the preceding key in each bridge. Frame 3 supplies the
visible lower-body donor because it contains two readable boot/shin shapes.
The explicit row boundaries partition that donor's lower paint into screen-far
and screen-near pieces, then into short trouser sections and complete distal
shin/cuff/boot pieces. These are authored projected owners, not a recovered
skeleton or evidence of unseen/symmetric limbs.

The two distal pieces use integer translation only. Each preserves every owned
source pixel and its full visible volume before intentional near-over-far
occlusion. Only the short trouser sections use the existing nearest triangular
part warp. Target quads and projected hip/knee/ankle guides are explicit in the
recipe; the guides are approximate screen landmarks, not an anatomy solver.
There is no blending, whole-body flow, fitting or paint synthesis.

Underpaint is explicitly empty. The held upper body ends at y53 and all lower
coverage comes from visible owned source paint. No concealed limb geometry is
invented to close gaps. Output layers, owner masks, per-part frozen sourceXY
maps and a full composite source-frame/XY map record every visible donor texel.
The layered editable project imports those layers through guarded transactions;
its journal replays exactly and the frozen keys remain locked.

The player compares original, timing control and candidate on the same one-second
clock at native/2×/4× scale, with stepping and half-speed controls. Chronology and
all predecessor/current pairs, including the wrap, are retained. Writing this
player is not a claim of browser or human continuous-playback review.

The two-cel still inspection shows complete boots and a plausible extra stride
state. It also retains the tight 2→3 boot overlap and the source's chunky cuff
shapes. Holding upper-body keys while subdividing only legs limits the possible
gain in whole-character motion. A full 16-frame bank is not justified by these
stills alone; first compare the actual two-bridge loop against its equal-clock
control. No numerical rating or quality improvement is claimed.

External outputs are retained at
`/home/astra/artifacts/pixelengine-imagen-refinement-20261020/source-repair/a15-bridges`.
`pilot01` preserves the first successful construction; `pilot02` adds the player
and explicit onset checks with identical pixels. No source or other production
lane is modified.

The same two controls were then tested on root's sharp-head/richer-body
composition using `a15-rich-lowerbody-bridge-recipe.json`, with the source path
`imagegen/head-body-palette-union/delivery`. `rich-pilot01` retains this trial.
The new frame-3 donor differs at 18 lower-body alpha pixels; its row boundaries
were rechecked at pixel scale and rebuilt masks partition its own paint exactly
once. The new donor's visible far/near distal pieces contain 112/108 owned
pixels, each preserved under rigid translation before near-over-far occlusion.
Every new lower-body sample comes from this richer source; no older
reference-palette or C52-colored leg layer is pasted into it.

The richer candidate also passed an actual LibreSprite save/reopen: all ten
rendered RGBA frames and the whole reimported project match. Its tool preview
durations are `125,125,63,62,63,62,125,125,125,125` ms, totaling 1000 ms; APNG
retains the exact 62.5 ms subdivisions. Independent replay of both full
source-frame/XY maps reconstructs both bridge PNGs exactly. The timing control
equals the original at all 32 sampled subframe times. These checks establish
source and clock preservation, not motion approval.

[A single component head midpoint](COMPONENT-HEAD-BRIDGE.md) subsequently tests
anchor `(40,28)` only at phase 2.5, preserving this lower-body trial and all
keys/clocks. Its raw gap and explicit source-colored neck-cap tradeoff remain
separate for root review.

[The two-slot leg repair](TWO-SLOT-LEG-REPAIR.md) subsequently tests an explicit
trouser-cluster edit and measured distal rotation against the crowded original
bridges. It retains the held-pelvis limitation and all original keys/clocks.

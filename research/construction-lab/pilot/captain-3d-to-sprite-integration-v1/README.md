# Fixed-world Captain sprite audition

This adapter consumes **unapproved** actual3D body frames. It is an inspection
tool, not an accepted Captain animation or a physics simulator. The earlier
guided8-key AI walk remains rejected: still craft7.5/10, motion3.5/10, with an
actual opaque sole patch sliding8px sideways during one held cel.

The new independent body review rates still/model craft7/10±1 and body-walk
usability6.5/10±1. It inspected all65 source and decoded frames, silhouettes and
repeated boundaries. Recovery occlusion, knee/cuff craft and ground placement
remain open. A useful change in method is not production acceptance.

## Inputs and ownership

- Generation repo: `/home/astra/projects/captain-3d-generation-lab`; neutral body
  frozen77eb005, separate shield/swordecfe143, halo/backgear/cape8d5d67a.
- Paint repo: `/home/astra/projects/captain-3d-reference-paint-lab`; fixedUV paint
  frozen1882f7b. Same geometry and UVs; no per-frame camera repaint.
- Rig repo: `/home/astra/projects/captain-3d-rig-lab`; initial body339eb8f.
  Thick-boot penetration is an explicit failed gate. Captured bare-foot joint
  positions are not proof of planted thick boot surfaces.
- Independent review: `../../qc/temporal/captain-blind-review-v1/body-semantic-v1/`.

Each producer owns a separate checkout. Root reads these assets and writes only
its integration folder and named external audition output. Standalone producer
commits are provenance identifiers, not commits to cherry-pick into this repo.

## What the replay proves

The65 frames retain exact60Hz timing: one cycle is65/60seconds. The retarget
ledger contains131 native120Hz samples including the closed endpoint. The
renderer explicitly removed only horizontal captured root translation for
in-place sprite baking. This adapter restores the corresponding displacement
through the actual fixed orthographic camera; screenY has the correct downward
sign. The world ground grid atZ=−1m is projected through that same camera. An
independent Blender `world_to_camera_view` witness checks six world points.

Two consumers are kept separate. **Synchronized** advances sprite and root at
60Hz together. **Continuous** advances interpolated root at120Hz while holding
each60Hz cel, exposing any residual within-cel slip. It does not cancel root
travel to make a sole appear stationary. At each wrap, the endpoint stride
accumulates instead of resetting the actor. No per-pose fitting or recentering
occurs. Native and nearest2× colour and silhouette variants use the same fixed
stage/origin.

All actual video packets are decoded and compared numerically against the
source-derived compositing, with≤2RGBLSB allowed for RGB/YUV conversion. Coverage
and hashes are recorded. Chronological sheets are discrete frame witnesses;
this is not a claim of continuously watching the video. A projected grid
provides context, not collision, loading, shadow or foot-force evidence.

## Commands

```sh
python -m unittest discover -s pilot/captain-3d-to-sprite-integration-v1 -p 'test_*.py'
python pilot/captain-3d-to-sprite-integration-v1/world_replay.py \
  --contract /home/astra/projects/captain-3d-rig-lab/render/body-semantic-v1/render-contract.json \
  --joints /home/astra/projects/captain-3d-rig-lab/rig/body-v1/retarget-joints.json \
  --output /home/astra/artifacts/captain-body-world-replay-v1 --loops 3
```

Existing output is refused. The local `index.html` provides video selection,
normal/half playback and an evidence receipt. No site publishing is involved.

## Within-cel actual-pixel witness

`check_held_sole_pixels.py` consumes the actual120Hz continuous video and the
**corrected evaluated-material** foot ledger. The initial contact-v2 ledger's
desired heel/toe anchorZ values were stale after floor correction. The geometry
audit was unaffected, but those values must not guide pixel projections. The
separate anchor-correction ledger records actual evaluated fixed vertices.

At each flat-foot cel, that actual toe projection guides a nearby fully opaque,
distinct3×3 source beauty patch within4px. The script requires a unique match in
both decoded packets of the held cel, with≤2RGBLSB allowance. Ambiguous or
missing matches remain failures of evidence. It measures displacement; it does
not use the target location as an automatic passing result.

Executed contact-v2 witness: all53 eligible flat-foot/cel pairs were uniquely
matched in the first130 actual packets, with at most1px displacement per axis
over8.333ms. An8px shifted actual second packet was correctly rejected. Twelve
fixed-crop paired witnesses were personally inspected. This is a useful bound
on **within-held-cel travel**, not a proof of material identity across poses:
each cel has a separate nearby beauty patch rather than an independently
vertex-tagged marker. It grants no animation quality, force or full plant
approval. The old contact-v2 crouch and cuff tears still block acceptance.

```sh
python pilot/captain-3d-to-sprite-integration-v1/check_held_sole_pixels.py \
  --contract /home/astra/projects/captain-3d-rig-lab/render/contact-v2/render-contract.json \
  --corrected-joints /home/astra/projects/captain-3d-rig-lab/rig/contact-v2-anchor-correction/retarget-joints-corrected.json \
  --export /home/astra/artifacts/captain-contact-world-replay-v2 \
  --output /home/astra/artifacts/captain-contact-held-pixel-check-v2-replay
```

The first output folder of this pixel experiment preserves an unsuccessful
JSON serialization attempt; the fresh replay above completed the receipt.
Source art, rig and video were not changed to repair that exporter error.

## Remaining acceptance gates

Correct owned sole geometry through explicit contact episodes and leg IK;
inspect actual deformed soles, world contact and gait changes. Diagnose armour
ownership during bends, preserve detail and refine unseen side materials.
Integrate anatomically correct shield/sword grip, halo and controlled cape,
then review the entire equipped animation again. Compare camera angles as
separate fixed experiments; ordinary leg occlusion is not automatically an
error. A final useful Captain cycle must earn an independent visual verdict
against the user's game-art expectations. Technical checks add no art points.

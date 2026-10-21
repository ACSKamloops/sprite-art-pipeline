# Methods and reproduction map

## Still art and large collections

Use [reference-art-production](../skills/reference-art-production/SKILL.md) for
source selection, shared style + subject-specific prompts, actual ImageGen
receipts, alpha/export checks and per-subject fidelity review. Its
[batch runbook](../skills/reference-art-production/references/batch-runbook.md)
contains the real `claim_next.py` workflow: initialize, approve references, claim
with an exclusive token, complete/fail, synchronize one manifest, publish a
pending review snapshot, accept by export hash, or create a bounded repair.
Workers do not turn generated assets into accepted assets.

## ImageGen animation route

Start with [imagegen-sprite-animation](../skills/imagegen-sprite-animation/SKILL.md)
and its [production recipe](../skills/imagegen-sprite-animation/references/production-recipe.md).
Freeze character scale and view, generate coherent directional/key-pose banks,
inspect actual gait roles, then author missing opposite-contact/passing/recovery
paint rather than renaming near-identical poses. Register a whole sheet/clip once;
do not fit or recenter each pose independently.

Use painted keys as art, not inferred hidden geometry. Part bridges retain masks,
source-texel witnesses and authored projected controls. Nearest sampling preserves
colors, not automatically good pixel clusters or anatomy. Fix demonstrated seam,
overlap and volume errors using owned paint and explicit downstream edits.
Do not rely on more frames/FPS to repair a missing leg exchange.

The [PixelEngine/ImageGen comparison](../research/pixelengine-imagen/README.md)
connects retained pose guides and genuine client-side pixel processing to this
same constructor/exporter. The guided ImageGen walk scored7.5/10 in a scoped
cold chronology review, versus5.5/10 for text-led paint. Optional grid conversion
introduced shrinkage/debris in some cases; it is explicitly selected and never
a default native-sprite import step. Its exact adapter, source hashes, alpha
controls and failed candidates remain distinct from hosted-model replication.

[Follow-on refinement](../research/pixelengine-imagen/REFINEMENT.md) covers the
stronger scarf guide, owned head/body palette, mixed-rate cloth and bounded
leg/painted-bridge tests. Reviews still prefer the reference; source-key
preservation is not improved weight transfer or9/10 art acceptance.

The [Lyra repair](../examples/lyra-leg-repair/README.md) demonstrates consistent
boot/calf/cloth masters, a revised projected foot path, preserved upper paint,
fixed timing and review of all pairs. Its still-visible repair is useful evidence;
normal-speed human acceptance remains open.

## Precise editing and native editors

The [construction toolkit](../skills/sprite-construction-editing/SKILL.md) provides
layered RGBA/indexed projects, locked regions, guarded paint/erase/paste/palette
transactions, explicit translation/clipping, undo/redo/replay, onion-skin editing,
and layered ASE/ORA exchange. Keep upstream masters/transforms separate from
downstream pixel journals. Changed source hashes invalidate stale edits/reviews.

```bash
TOOLKIT=skills/sprite-construction-editing/assets/toolkit
.venv/bin/python "$TOOLKIT/scripts/sprite_edit.py" validate \
  examples/approved-hero/editable/walk.project.json
.venv/bin/python "$TOOLKIT/scripts/sprite_edit.py" ase-export \
  examples/approved-hero/editable/walk.project.json output/walk.aseprite --animation walk
```

Create `output/` first. Actual LibreSprite save/reopen and actual rendered RGBA
are separate checks from writing a valid ASE file. External-editor integer
milliseconds are a preview; the sidecar retains the authoritative rational clock.

## Native video to sprites

[The approved generic-hero example](../examples/approved-hero/START-HERE.md)
preserves the actual historical H3 return and literal submitted inputs. Rebuild
offline from that saved native video, retaining exact presentation timestamps,
whole-clip framing, explicit selected indices/holds and reversible matte/paint
edits. This does not make a new provider request. See
[offline-native-bake](../skills/sprite-animation-pipeline/references/offline-native-bake.md).

```bash
.venv/bin/python examples/approved-hero/tools/bake_native_sprites.py \
  --video examples/approved-hero/reproduction/returned-h3-native.mp4 \
  --recipe examples/approved-hero/reproduction/bake-recipe.json \
  --output output/fresh-native-bake
```

The source H3 walk and current ImageGen game are distinct artworks. Video-derived
temporal consistency does not establish ground contact, a loop seam or approval
of a new action. Historical H3 quota exhaustion is not permission to run it now.

## Reusable parts, equipment and Blender

For 2D rigs, define owners, underpaint, hip/knee/ankle or shoulder/elbow/wrist
controls, depth order and compatible attachments. Generate/paint missing surfaces
deliberately. A flat cutout rig can test motion but may look stiff or disconnected;
use full painted keys when needed. [Construction methods](../skills/sprite-construction-editing/references/manual-gait-refinement.md)
retain failed approaches as well as useful ones.

A true Blender render route needs geometry, textures, a rig and authored motion.
A reference image alone does not supply that model. Fixed camera/light/scale,
directional renders, stable pivots, source timing and actual exported-frame review
are required. [Mech extraction code/notes](../research/mech-extraction/README.md)
retain the earlier archive-to-Blender process; game data is local-only. The
[textured model reference](../skills/sprite-animation-pipeline/references/textured-model-sprites.md)
separates real rig/UV evidence from image-plane cutouts.

## Timing, review and Godot

[sprite-animation-pipeline](../skills/sprite-animation-pipeline/SKILL.md) documents
the manifest, exact APNG/CFR delivery, source-bound reviews, state/effect clocks,
component timeline unions, actual held-frame world-contact tests and Godot import
and gameplay checks. Run the chosen production renderer; a second unused demo
renderer cannot prove the game's behavior.

```bash
.venv/bin/python skills/sprite-animation-pipeline/scripts/animation_assets.py \
  validate examples/approved-hero/clips.json --report output/approved-walk-validation.json
godot --path demos/emberwake
.venv/bin/python demos/emberwake/tests/run_checks.py
```

Engine tests establish their declared behavior/resource scope, not art scores.
Inspect full actors at native/integer scales, all pair transitions and loop/recovery,
then judge the actual normal-speed loop. Current diagonal quality remains open.

## PixelLab findings and local channels

The [workbench](../workbench/README.md) joins original recovered client subsets
with our explicitly labeled supporting UI/editor/storage/jobs. Read
[consolidated findings](../workbench/docs/consolidation/CONSOLIDATED-FINDINGS.md),
[command grammar](../workbench/docs/COMMANDS.md),
[comparison plans](../workbench/docs/WHOLE-FLOW-COMPARISONS.md) and
[coverage](../workbench/docs/COVERAGE.md).
Model Lab prepares named executor packets; it is not an image generator. Motion
Lab provider execution is separately gated. Observed fitted VFX recipes do not
recover private constructors, and client routing names do not identify private
weights. Report implemented, observed, inferred, missing and rejected separately.


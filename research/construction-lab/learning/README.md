# Learn game behavior and transfer it to authored sprites

This is an executable case system, not a claim that the entire game has been reversed.
The frozen roster has **116 investigation cases**: 85 existing captured routes,
23 animation-family coverage questions, seven unresolved subsystem questions and
one independently reviewed timing intervention. The local queue records **one
verified bounded case and115 pending**. A pending case does not become understood
because its sprites were exported.

## Proven example

`run_hold_experiment.py` and `qc/engine/method-trace/run_hold_experiment_v2.py`
replay the same checkpoint, native equipment setup and input sequence. A private
derived ROM changes just offset116A9A from1C to19. The original ROM stays unchanged.
The instrumented core adds five passive watchpoints in an isolated worktree.
Both runs have zero dropped trace records over268 monitored video ticks each.

`build_learning_map.py` verifies source bytes, raw capture hashes, native register
widths, bounded disassembly, selected pose runs and independently decoded
OAM/VRAM/CGRAM output. The comparison preserves the changing sword palette.

| Observation | Original | Changed |
|---|---:|---:|
| Selected generic171 hold | 5 ticks | 10 ticks |
| Displayed generic171 hold | 5 ticks | 10 ticks |
| Later generic172/173 holds | 5/5 ticks | 5/5 ticks |
| Completion shift | baseline | +5 ticks |
| Observed selection→presentation lag | 1 video tick | 1 video tick |

The script reads frame control atC0F5A3. C0F5CE..F5DB masks low control bits and
stores E012; the newly instrumented trace shows its stored counter changing0→1.
C0F590 handles countdown. C0F632 decodes frame descriptors for sprite assembly;
it is a distinct step from hold control. These findings apply to this observed
branch, not an unconditional timing formula for all actions or status waits.

The independently rebuilt report has313 checks and zero failures. Zero/two-tick
presentation models and a shifted selection transition fail. The independent
review initially rejected an M-width error atC0F90B; the corrected collection
uses observedM8 and decodes CMP#FF as two bytes. Every range now identifies
undecoded intervals and excluded straddling instructions. Complete function
bodies are **not** asserted. Three supplied entry contexts remain assumptions
when no entry watchpoint was observed.

Read `method-graph.json`, `hold-experiment-report.json`, `static-methods.json`,
`independent-audit/report.json` and `independent-audit/revision-report.json`.
The first audit is retained beside its accepted bounded revision. The interactive
viewer is `viewer/index.html`; GIFs deliberately slow each source tick to100ms.

## Repeat the capture and verify

The ROM, checkpoint, harness and compiled instrumented core are private local
dependencies recorded by hash. No ROM or checkpoint is in the portable skill or
public viewer. The SNES adapter is game-specific; other games need their own
memory layout, loader and replay adapter.

```bash
# From /home/astra/projects/sprite-construction-lab:
python3 learning/build_learning_map.py \
  --baseline /home/astra/artifacts/som-method-learning-private/baseline-v2 \
  --variant /home/astra/artifacts/som-method-learning-private/hold-field-1-v2 \
  --rom '/home/astra/artifacts/rea-som-test-2026-10-07/roms/Secret of Mana (USA).sfc'
python3 -m unittest discover -s learning -p test_work_queue.py -v
```

Fresh core/capture commands and original-checkout preservation are documented in
`../qc/engine/method-trace/README.md`. Use new capture output directories for each
run. Keep the original artifacts and dirty worktree unchanged.

REA is connected, but its current generic binary admission rejected both.sfc and
.gpr. `tool-boundary.json` retains the actual errors. The successful specialized
probe uses Ghidra's65816:LE:24:snes language in a private, readOnly project session
and the instrumented SNES core. A loader limitation does not imply analysis is
impossible; do not pretend a host-emulator decompile is the game's65816 code.

## Query all currently captured motion frames

`../qc/engine/motion-index/catalog-v1/motions.sqlite` indexes all28,123ticks
across85routes. Its builder verifies140,615rawsourcefiles and actual expected
RGBA/index/palette images. It retains110,470actorstates,2,708selectionruns,
selected script/counter/action fields and displayed object/palette signatures.
Read `../qc/engine/motion-index/README.md` and `queries.sql` for reproduction and
bounded queries. Six read/verify workers feed one writer; the database is24.27MB.

The methods×routes heatmap covers62 watchedPCs and208,618 sparse events. Only
four local entry contracts establish actorX ownership; other owners remain
unknown. Three routes have no CPU trace and legacy drop counts remain unknown.
A tick without a selected watchpoint is not a lost tick or proof a method never
executed. The map is observed co-occurrence, not a complete causal callgraph.

## Claim the next case

```bash
python3 learning/work_queue.py --db /path/to/method-learning.sqlite register learning/cases.json
python3 learning/work_queue.py --db /path/to/method-learning.sqlite claim --worker worker-name
python3 learning/work_queue.py --db /path/to/method-learning.sqlite status
python3 learning/work_queue.py --db /path/to/method-learning.sqlite finish \
  --id CASE --worker worker-name --token TOKEN --receipt /path/to/receipt.json
python3 learning/work_queue.py --db /path/to/method-learning.sqlite release \
  --id CASE --worker worker-name --token TOKEN --reason 'Checkpointed work before stopping'
```

Preserve the returned token and input fingerprint. Use separate worktrees and
artifact folders. Claims are atomic; 48 competing process requests yielded24
unique claims for24 jobs. Only the owner/token can finish or release a job.
Changed inputs require a new case revision. Changed evidence, stale fingerprints,
duplicate evidence IDs, wrong purposes and boolean stand-ins for causal links
reject. Claimed work is never silently stolen from another worker.

The queue checks ownership and provenance linkage only. It cannot establish that
a report is scientifically true: even correctly labelled irrelevant text can
satisfy its file gate. The game adapter's actual verifier and independent review
must establish conclusions. Source-bound causal receipts link static analysis,
executed trace, controlled intervention and displayed-frame verification.
`normal-right-sword-receipt.json` is the completed example. Artwork uses the
existing leased `animation_queue.py` stages and separate visual approval.

## How one sprite becomes an animation

Start with a design reference plus a consistent visible view, palette/material
regions and world/render anchors. Construct real editable body/equipment layers.
Draw missing surfaces and key poses; a fused picture cannot supply hidden anatomy
or another viewing direction. Use a2D rig where articulated source parts suffice,
pose redraws for deformation/perspective changes, or an actual3D model/rig for
the Blender route. Render onto one fixed canvas, then edit cels precisely.

| Family | Construction and controller | Required quality evidence |
|---|---|---|
| Idle | Neutral pose, subtle articulated motion or replacement face/readiness cels | Grounding, attachment, identity and intended holds |
| Walk/run | Alternating support/swing, knees/arms/torso, root displacement and view-specific poses | Whole hold intervals, wrap, ground contact, raster/camera snapping and seams |
| Melee | Anticipation, contact, follow-through and neutral recovery; independent weapon parts | Weapon attachment, silhouette/weight, interruption and independently proven/authored hit events |
| Charge | Pose progression controlled by charge/state and release | Variable waits, levels, cancellation and transition into the correct strike |
| Projectile | Launch plus a separate travelling/returning entity and cleanup | Spawn/motion/collision/return/despawn; ownership cannot be guessed from nearby pixels |
| Spell | Caster gesture plus separate effect entities and palette state | Target variant, lifetime, palette ticks, state gating and cleanup |
| Damage/recovery | New recoil poses, world knockback and palette/visibility feedback | HP/state triggers, recovery timing and interrupts |
| Death/revival | Authored collapse/dead/recovery poses, driven by actual state | Persistent dead state, target setup and completion; no invented fixed wait |
| Transformation | New identity/sprite configuration plus entry/exit states | Reachable contexts, palette/geometry mapping and original-form restoration |
| Event/NPC/boss motion | Additional view/action key poses and original dispatcher evidence | Currently unresolved contexts remain unlabelled until traced |

The native source informs architecture and timing; it does not supply new approved
character art. Fine edits use masks, palette/part ownership, exact pixel receipts,
undo and replay. AI can propose key poses or repairs; dimensions, preservation,
anatomy, materials and adjacent-frame consistency require separate checks.

## Current quality findings

The original12pose×5tick walk slides4pixels under the tested continuous root.
The60pose×1tick pilot slides1pixel in actual raster readback. A continuously
evaluated unchanged rig measures0pixels in the same sampled test. Both raster
versions fail the unchanged0.5pixel rule; density is an improvement, not approval.
See `../qc/pixel_motion/dense_pilot/README.md` and its captured boot comparisons.
Five fractional samples per tick are measured; analytic hold bounds remain
separate from this finite GPU sampling.

Native floating-point clock conversion could leave8ticks as7.999999999999999.
The corrected controller normalizes only machine-roundoff proximity; all9881
engine checks and9 early-boundary guards pass, with13 real perturbations detected.
Editor Play now resumes paused time; Replay explicitly restarts.13 browser
playback checks,18 editing checks and52 independent Python parity checks pass.

The new cutout character and localized AI knee patch still request changes for
joint/material/anatomy issues. An exact mask allowed three blue-to-pink material
leaks. The production coverage gate still fails639 missing approved-art targets
and two scope gaps. Read `../qc/coverage/README.md`; no full-game or production-art
approval is implied by a working viewer, catalog, queue or check count.

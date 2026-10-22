# Requirements and acceptance

## Product target

Create original, readable humanoid RPG sprites and a repeatable art-to-game
pipeline. The current visual target is compact modern shaded sprite art at a
declared native resolution, with a top-down three-quarter world like the brief
that led to Emberwake. A 16-bit palette is not a requirement. Character size,
camera/view and costume must remain coherent across actions and directions.

Reference imagery is assigned explicit roles: identity, style, pose, material,
direction or edit target. Use comparable professional samples when studying
motion; unrelated body proportions/art styles are qualified controls, not the
new appearance target. Missing images and hidden surfaces remain explicit gaps.

## Required inputs and outputs

| Stage | Required record | Completion evidence |
| --- | --- | --- |
| Brief | Actor/style/scale, action/view/equipment matrix, reference roles | Reviewed source contract and inventory |
| Generation | Exact prompt, ordered references, actual tool/provider, raw result | Saved original pixels and attempt receipt |
| Construction | Fixed canvas/pivots, owned parts, explicit underpaint, poses | Editable project plus source maps/masks where used |
| Fine editing | Locked regions, exact operations and source/project hashes | Guarded journal, actual changed pixels, replay/undo |
| Animation | Ordered frame IDs, rational holds, loops, events | Manifest and decoded/exported clock checks |
| Review | Full actor, every adjacency, wrap/entry/recovery, scale/background | Hash-bound findings and actual normal-speed judgment |
| Engine | Import/readback, animation/state clock, actual inputs and events | Godot checks/captures for the tested package |
| Delivery | Relative paths, source-ID mapping, editable files, notes | Reproduction commands, hashes, coverage and limitations |

A generation success is not review approval. Queue stages retain this difference.
Zero remaining ready jobs is not complete coverage if claims, failures or reviews
remain unresolved.

## Action and direction coverage

Plan coverage by **actor × equipment profile × direction × action × variant**.
The intended top-down direction set is N, NE, E, SE, S, SW, W, NW. Diagonal
fighting/aiming is required; the user's “flight” clarification meant fighting,
not a separate flying action. Movement direction, facing and aim are separate
controller decisions.

The reusable RPG backlog includes idle/breathe, walk, run, unarmed attack phases,
casting, hurt, stun, death/knockdown/get-up, dodge, crouch, jump/takeoff/air/landing,
interaction/pickup and contextual celebration/ready states. These are coverage
requirements, **not a claim that all are delivered in all views**. See each
example's action catalog and the [current status](STATUS.md).

Use measured hand/grip anchors, compatible equipped motion and front/back/hand
occlusion for interchangeable weapons. Weapon/body/effect clocks can differ but
must share an explicit timeline. A physical jump/landing is distinct from body
paint moving up/down in a video. Damage windows and event semantics need their
own gameplay specification; frame position does not prove a hit event.

## Quality gates

1. **Artifact integrity:** source identity, canvas, framing, alpha, palette,
   literal edit localization, clocks and dependency paths.
2. **Drawing:** identity, proportions, material volumes, silhouette, complete
   limbs, leg/arm ownership and plausible joints. Narrowing a cuff or preserving
   pixels cannot by itself prove anatomy.
3. **Temporal:** trace each limb through every predecessor/current pair, loop
   seam and one-shot recovery. Check gait exchange, weight, planted/clearing feet,
   attachment stability and unwanted holds at intended speed and scale.
4. **Gameplay:** actual render/input/state transitions, interruptions, collisions,
   attacks/spells, ground motion and start/stop behavior in the intended engine.
5. **Human acceptance:** keep the preferred original beside every candidate.
   Normal-speed rejection overrides prior still scores or green mechanical tests.

Earlier demo work used an **8/10** threshold. The current full-character
refinement request requires **9/10**, which remains unmet. A score applies only
to its actual source hash, actor, action,
view and review conditions. Do not average a strong still with poor motion and
announce that an entire library meets the target. Preserve reviewer dissent and
state whether a review used stills, decoded frames or actual continuous playback.

## Operational requirements

Keep the approved baseline immutable. Use fresh candidate/output directories,
exclusive claims, bounded retry windows, saved per-attempt receipts and one
manifest publisher. Authorized agents use separate worktrees/ownership.
Provider execution must be explicit; no quota-consuming setup/test jobs.
No H3 or local generative model for current authoring without a new instruction.
The default art route is built-in OpenAI ImageGen with deliberate pixel/part
editing, not a claim that every frame can be independently generated consistently.

PixelLab analysis requirements remain separately cataloged in
[RECONSTRUCTION-CATALOG.json](../workbench/sprite_workbench/contracts/RECONSTRUCTION-CATALOG.json):
63 original questions, plus command/flow/grammar coverage and individual blockers.
Accessible client code and observed API behavior do not reveal private model
weights, training, hidden prompts or complete server algorithms.


# ImageGen art to a playable top-down Godot demo

Use this to integrate authored sprite banks into a small original game and verify the result. The concrete example is Emberwake at `/home/astra/projects/emberwake-demo`, finalized 2026-10-16. The recipe is self-contained guidance; local source pointers below provide the exact tested implementation when available. A missing example checkout is not permission to claim its checks ran.

For generating and repairing views, first read the ImageGen companion's `references/directional-character-banks.md`. A still sprite collection, animation player, layered rig and complete game are different deliverables. Select the scope the user actually requested.

## 1. Contract, ownership and art coverage

Freeze a concise visual/game contract before parallel work: camera/view, painted body size, stage/pivots, intended directions/actions, terrain size, collisions, controls, combat events, save/quest states, playable endpoint and runtime target. Emberwake used an original village/forest/shrine action-adventure; the top-down world brief did not imply reproducing another game's battle engine.

Useful authoring lanes are art/source/bakers, actor combat/FX, world/quest/HUD, then independent visual/gameplay reviews. When delegation is authorized, give each writer a separate branch/worktree and explicit file ownership. Use one integrator for shared contracts/receipts. Reviewers write outside production sources and freeze their exact inputs. Parallel authorship is not independent review.

The case provides four hero facings × idle/walk/unarmed attack/cast/hurt/dodge. Firebolt and frost reuse each direction's cast body while effects have separate clocks. Enemy front/back three-quarter art uses explicit mirrored quadrants. Do not silently expand those into eight-direction art, modular equipment, jumps or a complete death-collapse set. Derive the new game's action/view matrix from its controls.

## 2. World assets, registration and compositing

Keep character and world camera/material/lighting coherent. Generate tile/prop/enemy candidates with actual alpha where appropriate, and retain raw images and literal requests. Paint semantic imagery with ImageGen; use requested source-pixel edits and deterministic composition for measured transforms and repairs.

The example world's principal props have declared foot/contact pivots and y-sorted placement. Tree crowns/roofs are visually above bodies, with solid trunks and independent physical collision. A proximity shader fades the upper artwork for the hero and nearby enemies while keeping the lower trunk opaque. The tested shader blends back to full opacity across texture UV.y 0.66–0.95; that is specific to these tree/roof textures. Inspect actual overlaps before adapting the threshold.

A small map can bake repeated ground draws into one continuous raster if profiling shows draw overhead. `bake_ground.py` combines retained grass/path/water tiles with authored route-distance masks, feathered clearings, ponds and restrained seeded variation. The case ground is 2304×1728; physics contacts and live props remain separate. This is an editable composition, not a newly generated complete map. Rounded/feathered shrine clearing fixed a visible rectangular patch. Do not require one giant texture for an unrelated large world.

The named bronze Bell needed an actual bell image, not an altar that merely had the right quest label. A targeted ImageGen edit supplied it. The village lantern combines a literal cottage-lantern pixel mask with an authored post. Check semantic asset identity in the running scene as well as source quality.

## 3. One authoritative actor state, independent effects

The tested hero is a `CharacterBody2D`; physics owns movement, state duration, costs, cooldowns, invulnerability and one-time pending action releases. A `Sprite2D` displays a custom atlas/JSON bank with explicit variable holds. This implementation does not use `AnimatedSprite2D`; the companion's SpriteFrames driver remains another tested option. Either route must match the same declared action clocks.

The game's `emberwake-animation/v1` manifest is not the companion CLI's canonical manifest schema. Use the case baker and game checks for that bank. A future generic-tool integration needs an explicit adapter that preserves regions, origins, holds, loops and lineage; no such adapter was delivered or verified here. Do not treat the generic validator's schema rejection as an art failure or claim it validated the custom bank.

Core flow:

```text
real input -> eligible/buffered action -> lock action aim and spend resource once
physics time crosses release -> damage/projectile/effect once -> recovery -> idle/walk
render state -> view/action bank -> explicit held cel -> declared stage pivot
```

Separate physical world position from the cel's authored origin. Do not translate the actor's collider to hide a misregistered pose. Four cardinal sprite views may accompany diagonal movement through a dominant-component rule; that does not supply diagonal paint. Lock aim for an attack instead of turning a committed punch to track a moving target silently.

Case timings (adapt, do not prescribe): attack 0.41 s with damage at 0.16 s; cast 0.50 s with release at 0.24 s; dodge 0.26 s. Firebolt costs 10 mana and frost 24; their body cast clip is shared but projectile, nova/radius, warning and impact clocks are independent. Swept projectile segments and line-of-sight checks prevent skipping thin walls or hitting through them. A held contact image is not an instruction to apply damage every frame.

Actor damage returns accepted/rejected status. Successful damage owns one painted impact burst; projectiles must not duplicate it. Missed/invulnerability-rejected melee gets a smaller hollow cue rather than a false damage burst. Restraint matters: added flash/cloud layers can hide exactly the pose being reviewed.

## 4. Group combat and HUD visibility

The first playable build stacked dark enemy silhouettes and overlapping warnings. The repair combined actual spatial/behavior changes with clearer painted intent:

- Local elliptical separation considers sprite bodies above their small foot colliders. The case uses visual delta`(dx,dy*0.72)` and desired spacing`radiusA+radiusB+28`.
- A nearby enemy's windup/strike/phase and first 0.20 s of recovery reserve a commitment against the same target. Waiting foes still approach/reposition. Waiting time, then distance/instance tie-breaks, prevent permanent starvation. Reservations derive from living actor states, so death/interruption/disabled targets release them without a persistent global queue.
- Existing painted anticipation/contact/neutral keys get small declared whole-cel offsets. These improve staging but are not new articulated limb animation. The accepted new Warden rear key supplies genuinely new release paint.
- Warning geometry matches the actual locked hit sector/radius/projectile spread. A missed strike remains a miss; improving feedback cannot secretly increase reach or active time.

These are case-tuned choices, not universal one-enemy combat. Verify actual pressure, all-foe participation, obstruction/narrow paths and moving-player collisions. Stationary invulnerable fixtures test spacing/arbitration, not natural difficulty or excellent feel.

HUD tests must consider actors, not just rectangle intersections. The first relocated boss panel cleared the objective but covered the Warden's torso. The final 960×540 layout reserved bottom-center boss`[306,427,348,38]`, a separate interaction row at y 375 when a boss is present, action belt at y 478, and a left toast ending at x 289. Actual entry and Bell-adjacent browser views confirmed the separation. Small enemy health bars can still cross the hero; preserve that known limit instead of calling all occlusion solved.

## 5. Pause, input, progress and audio

An always-processing root/HUD may host a **pausable actors branch** for hero, foes, projectiles and FX. A modal must freeze pending release, cooldown, effect lifetime and motion clocks without cancelling a spell already in progress. In this implementation `set_input_enabled(false)` was intended for resets and cancelled actions; modals set the input field and pause the tree instead. Adapt that distinction explicitly.

Dispatch actual input events after menus. A focused play-mode Journal button accepted Space as `ui_accept`, opening the journal during dodge. `FOCUS_NONE` for that play button fixed it; direct hero-method smoke tests could never detect the GUI conflict. Test Esc/P resume, Space, clickable dialogue and overwrite confirmation in the real viewport/browser.

Keep quest transitions explicit: ward cleared is distinct from ward kindled; boss defeated is distinct from Bell ending; ending is distinct from completed return conversation. Persist the epilogue flag and clear completed objective/compass. Full ordinary-input play found an Aster return objective that remained after the conversation despite earlier engine checks.

Validate save version, types, checkpoint whitelist and logically consistent flags. Show Continue only for a loadable save, with cached validation refreshed on title entry/save and a guarded load if the file changed. Explicit new-journey overwrite confirmation protects a valid existing checkpoint. Tests use a separate save and restore prior test data; browser saves are isolated profiles. Checkpoint restoration intentionally resets unfinished encounters/resources rather than serializing every projectile.

Original procedural music/cues are another lane, not ImageGen output. The case's NumPy synthesis uses a seeded 16-bar, 84 bpm score plus action WAV cues, then ffmpeg for Ogg. Retain score/source and separate music/SFX controls. Browser autoplay needs a real gesture: CDP observed suspended→running and an advancing audio clock after Begin. That proves audio-engine activity, not audible/nonzero output or sound quality.

## 6. Import and actual Web export

Use `ResourceLoader.exists/load` for imported PNG/WAV before raw-file fallbacks. PCK remapping can remove original raw paths while their engine resources are valid. Editor success does not prove exported loading. Import new images before expecting the release bank loader to find them.

The tested engine was Godot 4.7.2 Compatibility/WebGL2 with matching nonthreaded templates. Use the installed engine's matching templates when adapting; do not assume this is the current latest version. Nonthreaded Web does not need the thread-related cross-origin isolation setup. Serve over HTTP rather than opening HTML with `file://`.

Keep source sheets/raw returns, scripts for authoring, tests, docs, screenshots, proof atlases and existing Web output outside runtime export. An accidental screenshot inclusion enlarged this PCK substantially. Retain them in the editable project and hash them separately. The final example's PCK is 9,470,752 bytes; WASM/runtime files are additional payload, so PCK size alone is not the download size.

Case commands:

```bash
cd /home/astra/projects/emberwake-demo
LP_NUM_THREADS=4 OMP_NUM_THREADS=4 godot --headless --path "$PWD" --editor --import
python3 tests/run_checks.py
# Export to a fresh staging folder, then publish locally only after success.
LP_NUM_THREADS=4 OMP_NUM_THREADS=4 godot --headless --path "$PWD" \
  --export-release Web /ABSOLUTE/FRESH/STAGING/index.html
./play.sh
```

Create the staging directory first. `play.sh` hosts the selected `web/` folder; do not start another server on its occupied port. The case serves localhost 8896 and supports `EMBERWAKE_PORT` for a new server. No model/provider account is required to play or rebake retained pixels. Publish externally or create ZIPs only when requested.

## 7. Separate behavioral, pixel and perceptual verification

The case suite has 280 behavior/resource assertions across systems 114, world 56, pause 26, input/closure regressions 20, save/HUD 34 and combat 30, plus 378 separate route samples. These numbers are receipts, not requirements or visual scores for a future game. Inspect script/runtime errors even when Godot exits 0 and prints a PASS marker: a dependent script failed compilation while another test continued. Preserve failed runs; a later clean rerun does not make an interrupted/error run pass.

Audio shutdown needed a bounded 0.35 s teardown after stopping music and clearing its stream, replacing an observed too-short 0.15 s grace in affected tests. This is not permission to suppress resource errors or add arbitrary sleeps to hide leaks.

For visual checks, divide the work:

| Gate | Actual evidence |
|---|---|
| Pixel/transport | Source/raw hashes, stage transforms, protected RGBA, fresh deterministic rebake, imported/exported resources |
| Character art | All 24 hero clips, native/nearest 2×, preceding/following poses, wraps and state joins; no inherited score |
| Gameplay | Real keyboard/mouse, fights, collisions, costs, misses, interruption, pause, save/reload, ending/epilogue |
| Changed-build review | New PCK hash, replay changed paths, declare which unchanged results retain prior qualified basis |
| Human acceptance | Uninterrupted viewing/play with sound; not replaced by sampled screenshots or perfect hashes |

Use read-only browser diagnostics for state/position/poses and retain raw action logs. Screenshots can land after the triggering state sample; a filename is not proof of its named pose or a boss victory. A mistaken premature victory capture in this work was relabelled, and actual later success was logged separately. For frame-exact claims, capture state/pixels in one controlled render callback; otherwise qualify the temporal sample.

Fixtures that teleport an invulnerable actor into a combat setup must remain labelled as fixtures. Ordinary browser play used `test_mode=false`, no teleport, save injection or damage bypass. Do not equate a correct test objective with a staged screenshot's automatically bypassed quest state.

Freeze reviews before repairs, keep prior poor scores, and request the next change from a concrete observed defect. Do not give reviewers a numeric target to hit or re-rate identical art repeatedly. Whole-demo acceptance is distinct from each sprite/action's score.

## 8. Resource management and handoff

Use safe parallel CPU resources where independent, with per-worker worktrees and bounded tool output. Close only the task's inactive QA browsers: always-processing menus can keep rendering in software GL. Closing old sessions changed measured FPS here; that was concurrent-load cleanup, not proof of a code-performance gain. Headless shared SwiftShader figures are not a user's GPU benchmark.

Deliver one canonical source folder with relative assets, literal prompts/inputs/raws, selected/rejected candidates, baked atlas/manifest, edit/maps, authoring scripts/dependencies, actual review packets and a file hash ledger. A local AI needs those paths, not an upload account. The case's `DELIVERY-INDEX.json`, `DELIVERY-FILES.sha256`, `docs/QUALITY.md` and `docs/evidence/` distinguish current source from historical review scopes. The installed skill's evidence index is the ImageGen companion's `references/game-demo-lessons.md`.

Example code map: `scripts/{hero,enemy,combat_fx,projectile}.gd` for actors; `scripts/{main,hud,browser_diagnostics}.gd` for world/UI/read-only observation; `scripts/bake_assets.py`, `bake_ground.py`, `compose_lantern.py`, `compose_audio.py` for deterministic authoring; `art-source/boss-release-v1/bake.py` for the accepted rear key; `tests/run_checks.py` for actual cases; `export_presets.cfg` and `play.sh` for Web.

Final scope: compact-demo AI review 8.0/10 (moderate confidence), hero art 7.7 and motion 6.9 in a separate atlas review. Sparse enemy keys, front/back gait stiffness and occasional small-bar overlap remain. Human feel/audio quality, broad device/storage behavior and a fully general game-production system were not certified. The user's positive demo feedback did not remove those limits.

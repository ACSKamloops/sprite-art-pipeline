# Emberwake methods: evidence and limits

This is the source index for the 2026-10-16 top-down demo, not a universal art approval. Cold art reviewers should use the companion case-free review card before reading scored history here.

Read the maintained procedures for the work being performed:

- [Directional character banks](directional-character-banks.md): reference roles, actual four-view sheet requests, scale/origins, gait phase selection, side-walk replacement, mirroring, protected passing-leg edits, rejected warps and rear-weapon repair.
- [Top-down Godot demo workflow](../../sprite-animation-pipeline/references/topdown-godot-demo.md): world assets, physics/paint/effect clocks, canopy, group combat/HUD, pause/input/save/quest/audio behavior, actual Web export, reviews and handoff.
- [Source-pixel refinement](source-pixel-refinement.md): the portable source-map helper and bundled compact-jab fixture. That earlier single-view fixture is separate from this game's four-direction library.

## Canonical example

Local project: `/home/astra/projects/emberwake-demo`. Final delivery commit: `faf4362`. Its `DELIVERY-INDEX.json`, `DELIVERY-FILES.sha256`, `README.md` and `docs/QUALITY.md` define the selected snapshot. The game remains editable source; code and raw images are not copied wholesale into this skill.

| Evidence | Source path within the project |
|---|---|
| Literal direction/repair requests | `art-source/hero/*prompt.txt` |
| Raw hero sheets and appearance/pose references | `art-source/hero/` |
| Passing edit inputs, actual requests, direct composites and source maps | `art-source/hero/passing/` |
| Rejected lower-step source-map trial and equal-clock chronology | `art-source/hero/candidates/low-step-v1/` |
| Selected atlas, holds, directions and per-frame lineage | `assets/hero/atlas.png`, `assets/hero/animations.json` |
| Hero compositor with explicit origins and preservation assertions | `scripts/bake_assets.py` |
| World/enemy prompts, raw art, transforms and rejected hand swaps | `art-source/world-production/` |
| Successful rear release, new full paint and exact offline replay | `art-source/boss-release-v1/` |
| World/asset production methods | `docs/ART-PIPELINE.md`, `docs/ARCHITECTURE.md`, `tests/COMBAT-READABILITY.md` |
| Final engine receipts and independent report copies | `docs/evidence/` |
| Complete immutable browser review packets | `/home/astra/projects/emberwake-review/game-v1/`, `game-v2/`, `game-v3/` |

Selected SHA-256 bindings:

```text
web/index.pck
2b93baf201f84fea1c64597ad4cb485cc1617e75740148956732fcccd27c7213
assets/hero/atlas.png
1dc65d4eb637ef35e5be3d3345b1a56d18af6ce041f7ce000c924848d569cb68
assets/hero/animations.json
f295492d3339af898ee49c117b753ac1f475e78e0022cc943feaecf46510965d
assets/enemies/poses/warden/back_strike.png
16d27574bd7c726ef91f3473bd947048988f47a9a8a9f4ab21319e5832fa0f24
```

A fresh hero bake reproduced the atlas, manifest, two proofs and bake receipt exactly. The new rear release also reproduced exactly. This proves saved-input reconstruction in the recorded environment, not deterministic model generation or a byte-identical future PCK/audio encoder output.

## What was accepted

| Review | Result | Actual scope |
|---|---|---|
| Game v1 | 6.0/10 | Ordinary-input full quest; failures in menu/dodge, canopy, presentation and closure retained in frozen report. |
| Game v2 | 7.5/10 | Replayed full ending/epilogue, retries, overwrite choice and reload/Continue; group overlap and boss obstruction remained. |
| Game v3 | 8.0/10, moderate confidence | Replayed all three fights, save/reload/dodge, boss HUD/rear release and live-boss Bell gate. Warden intentionally remained alive; this was not another full-ending pass. |
| Hero v3 | 7.7/10 ±0.7 | All 24 clips and joins through decoded chronology; drawing 8.0, consistency 8.0, motion 6.9. Not human continuous playback. |
| Rear release | Narrow acceptance | Traceable weapon arm, identity/materials and footing, then actual exported back windup/strike/recovery samples. No general rig or excellent-motion certification. |

The user subsequently said the demo looked good and explicitly noted more remains to do. Preserve that positive demo feedback without converting it into approval of every frame, eight-direction art or a finished commercial library.

## Residual limits and repeatable failures

Front/back gait is stiff/march-like; side walk and stance yaw differ. The selected direct passing paint was only weakly preferred to an equal-clock repeated-pose control. Forcing support boots to a common centerline or translating exact boot plateaus with thigh warps did not solve anatomy and was left unselected. Translation fixes stage drift, not drawings or physical sole contact.

Sparse enemy keys limit fluidity; small enemy bars can still obscure the hero. Hero west walk is a disclosed mirror; enemy left quadrants mirror front/back three-quarter paint. Jump/sit/pickup-specific body paint, a separate collapse cycle and interchangeable-weapon rig are not delivered.

The final engine suite passed 280 assertions and 378 route samples. Browser context resume/clock and Windows-localhost transport have separate receipts. Those checks do not assign visual scores, prove audible quality or certify other devices/storage failures. Shared software-GL FPS after closing inactive browsers is not a controlled code-performance comparison.

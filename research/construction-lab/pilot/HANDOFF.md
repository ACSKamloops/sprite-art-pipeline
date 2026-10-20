Current Captain v20 is **visually rejected by the user** after delivered-video review. Prior 9.025/9.17 reviews are superseded, not current approval. See [video findings](space-marine-captain/video-rejection-review.md); frozen sources and historical engine proofs are preserved. The other prototype history below remains separate.

Current quality-correction experiments and reviews: [visual-quality-reset/README.md](visual-quality-reset/README.md). Current WSL skill install: [visual-quality-reset/skill-install.json](visual-quality-reset/skill-install.json); the earlier installation ledger below is historical.

> Current visual status: **rejected by the user**. The earlier prototype approvals below are historical. Directional anatomy and animation quality require a new art pilot; mechanical validation remains separate. See `pilot/visual-quality-reset/rejection.json` from the repository root.

# Local four-view animation handoff — 2026-10-07

The historical, visually rejected original Copper Scout prototype has **12 actions, four directions, 96 bindings and 6000 held 192×192 frames at 60Hz**. It uses reusable 2D continuous contours, rigid parts and two-bone IK, with source-attached materials. No 3D model or per-frame AI redraw is required. Source is `rigged-character-v2/{design.json,clips.json,rig.gd,rig_side.gd}`; baked pack is `rigged-character-v2/generated`. ManifestSHA256: `5543790d9fb8a3153a1c817d189fa16bb1e508b128a568b8e2c50508cca3be1a`.

## View and play

[Final 45.7-second animation reel](http://127.0.0.1:8144/pilot/review-player/final.html) shows all24 action/gear groups side by side in four directions. [Exact PNG playback and previous-frame comparisons](http://127.0.0.1:8144/pilot/review-player/?pack=../rigged-character-v2/generated/) provides pause, step, replay, seek, speed, native/2×/3× scale, difference and onion skins. A completed one-shot stays complete until explicit replay. The reel page verifies source, manifest and video hashes. The server supports byte-range media seeks; an earlier server reset seeks to0 and its failed browser runs remain preserved.

The video file is `/home/astra/artifacts/copper-scout-final96-reel-v2/animation-reel.mp4`. It is a lossy visual preview of exact source ticks; PNGs are the authoritative pixels. Separators distinguish independent clips from gameplay transitions. The local quiet server is running; restart from the repository root if required:

```sh
python3 pilot/tools/serve_local.py --root "$PWD" --port 8144
```

The actual Godot gameplay sandbox uses the matching measured cache:

```sh
godot --display-driver x11 --rendering-method gl_compatibility --path pilot/rigged-character res://world_v2.tscn -- --cache /home/astra/artifacts/world-v2-final96-cache-v5/cache.json
```

Controls: WASD/arrows move, Shift runs, X slash, T thrust, Z shoot, Q charge, C cast, B celebrate, H hurt, K fall, V recover, Space pause and R replay. UI explicitly selects none/sword/blaster, scale, speed and camera. Persistent gear stays through hurt/fall/recovery; mismatched weapon attacks reject. Cast/celebrate require stow. Full fresh-cache/test instructions: [world runbook](rigged-character/qc/world-v2/README.md).

## Reviews and demonstrated repairs

[Historical primary dense review](../qc/temporal/repaired96-review.md) accepted this for prototype use; the user subsequently rejected its drawing and motion quality. That aesthetic acceptance is revoked. Current metrics cover6139 comparisons: 5904 adjacencies, 44 loop wraps, 28 replay resets, 48 diagnostic inspection boundaries and 115 actual supported controller comparisons. 379 were freshly visually inspected after repair; 5760 inherit previous actual inspection only after exact every-frame RGBA, full pose/timing and gear equality for 93 unchanged bindings. All 200 thrust/guard/replay cells were additionally inspected. Fresh actual native browser playback covers all four thrust and four ready clips in 64 chronological captures, alongside the earlier identical-binding96/768 inspection. Coverage gate, 12 current negative controls and 23 adversarial unit tests pass.

[Second independent sampled review](rigged-character/qc/world-v2/sampled-motion-review-v5.json) inspects 144 chronological decoded frames across 96 bindings plus 32 native thrust/ready poses. Its decision is also prototype-only. Root separately viewed seven full-canvas chronological sheets from 28 actual browser captures: walk,run,slash,thrust,shoot,equipped fall and equipped recovery in all four views. Those image-capable reviews do not claim continuous video ingestion.

Repairs included knife-like blaster silhouette, cast elbow branch jumps, gear disappearing during interrupted states, sword floor penetration, and thrust jumping from extended blade to idle guard. Repaired thrust start/end poses and actual RGBA now exactly match equipped ready in all four directions. Earlier sources/exports, failures and rejected reviews remain intact; source-bound receipts were regenerated.

## Mechanical and fine-edit evidence

[Evidence index](final-four-view-evidence.json) binds all current report paths/hashes. Producer checks: 6391 export checks, 6384 exact actual GPU comparisons, 9704 analytical API checks over 9696 poses, and 2160 injury/fall/recovery floor images without floor penetration. [World delivery](rigged-character/qc/world-v2/delivery.json) records 422 checks, 6000 actual held SpriteFrames RGBA comparisons, 2976 equipped boot/contact comparisons and48 walk/run×view×scale×camera contexts with 0px measured stance span under the unchanged 0.5px gate. Physical root stays continuous; one global visual offset compensates held-frame contacts. Actual terminal holds are distinguished from legitimately skipped low-rate presentations.

Complete editable walk/front: `/home/astra/artifacts/copper-scout-v2-full-walk-front-final-editable-v1/project.json` (60frames, 12namedlayers, every full composite exactly equals the GPU/bake). Load it at `/editor/`; actual Chromium masked one-pixel edit, exact visible canvas, stale rejection and undo/redo pass. One binding per document keeps memory bounded. This is editable cel art, not automatic source-paint propagation.

Source-attached paint candidate: `/home/astra/artifacts/copper-scout-source-paint-6fba42e-v1`; 384 actual clean/painted poses and an independent inverse-UV/palette/mask check pass with 1391 visible pixel changes. It remains an unpromoted editing demonstration. Source changes require fresh export/cache/review. No arbitrary weighted texture deformation is claimed.

A separate copied skill toolkit reproduced all 6000 frames/poses exactly, passed 6384 GPU comparisons, 9704 API checks, 220 gameplay action checks/6000 actual held frames and 140 state checks. Current WSL skills are `sprite-construction-editing` and `sprite-animation-pipeline`; [install/rollback ledger](skill-install-four-view.json) binds the exact installed files. [Reusable four-view workflow](../skills/sprite-construction-editing/references/four-view-workflow.md) and [source paint/full-clip guide](../skills/sprite-construction-editing/references/source-paint-and-clip-editing.md) supply the commands and demonstrated failure recipes.

## Remaining limits

Front/back thrust and aiming need depth/foreshortening polish. Left mirrors right; independently authored handedness remains absent. The rig handles rigid paint and deforming contour-owned details; arbitrary textured weighted skinning is unimplemented. The sandbox uses hard pose transitions without blending. Art is approved for a bounded motion prototype, not finished production quality or a complete game.

The original two-view 1536-frame pilot, five-pose bridge and old site are historical evidence. Native Secret-of-Mana extraction/method-learning and at least 639 approved own-art targets plus 2 unknown gaps remain separate unfinished scope. This phase stays local; publishing remains deferred.

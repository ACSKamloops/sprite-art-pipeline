# Brann rear-diagonal gait

This is the selected NE/NW walk for isolated local v12. The independent whole-cycle review rates the retained raw art 8.5 for drawing, 8 for motion and 8 for game use. It used ordered stills and known holds, so continuous human playback and physical foot contact remain separate acceptance questions. The other unfinished walks do not inherit these scores.

## What made this route useful

The first built-in ImageGen call supplied four coherent full poses. Its00, 02 and 06 paint, plus the 04 upper, form the retained key bank. A focused second 04 drawing compressed the body and remained passing-like, so it was excluded. Both requests, actual input roles, raw returns and fixed grid conversion are in`imagegen-provenance/`. No H3 or local generative model was used.

The alternate 04 contact uses actual complete visible 00 leg paint: the receding right chain moves −20 native X, and the extended left chain moves +17 native X. Literal source ownership preserves each boot; genuine overlap is allowed. Odd poses deform compatible trouser strips while their boots move as complete pieces. Actual visible hip roots matter: earlier incorrect roots left gaps. The corrected base and modest opposite arm motion are reproducible from`editor/source-rebuild/` without using final frame paint as a source.

`frames/` retains the exact raw reviewed keys. `cleaned-frames/` removes only 11 literal black alpha-1 NE border pixels to satisfy the strict source-stage guard. `BORDER-CLEANUP.json` binds those edits. The independent`border-delta-review/` confirms every other RGBA sample is exact and finds no meaningful new visible difference; the derived NW delta is seven pixels because four raw NE edge samples were already outside its mirror destination. Six faint alpha-1 NW border samples remain recorded. No opaque anatomy was erased.

## Edit and reproduce

The portable native/editor unit is`editor/`. Open`editor/native/brann-ne-walk.aseprite` with its adjacent timing sidecar. It contains one honest flat layer and eight cels, not a newly inferred articulated rig. The exact clock is 160 Hz × 9 ticks per cel; native 56/57 ms holds total 450 ms, with the sidecar retaining the exact 9/160 s game holds. The raw source, seven real guarded cleanup transactions, undo/redo and source reconstruction stay available separately.

From`editor/`, use fresh output paths:

```sh
python3 source-rebuild/rebuild.py --out /absolute/fresh/source-replay
python3 scripts/replay_editor.py --out /absolute/fresh/editor-replay
```

Root independently ran both after copying this package. All eight decoded cels and native save/reopen/render/reimport match. PNG encoding equality and RGBA equality are recorded separately. The frozen editor manifest's original pending delta flag is historical; `EDITOR-INTAKE.json` points to the completed supplemental audit.

[Play local v12](http://localhost:8898/game-v12/index.html), [view actual NE/NW Godot loops](http://localhost:8898/godot-walks-v12/), or [compare raw source against the old walk](http://localhost:8898/brann-contact-v1/). `docs/evidence/source-cel-preview-v12/QUALIFICATIONS.json` records the actual renderer, Web export and browser evidence and its limits. Installed v6 and the existing public build remain unchanged.

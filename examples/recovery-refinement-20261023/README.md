# Recovery refinement and the missing-leg playback failure

This saved study continues the selected hero's southeast get-up using built-in
OpenAI ImageGen and guarded native pixel editing. It preserves the preferred
walk and every other selected action/view. **The 9/10 target remains open.**

An anonymous still comparison preferred the new entry/support-release variants
at8.2/10 versus7.7 for its control. The user then rejected actual playback because
a leg appeared to vanish. Those scores did not establish acceptance. A follow-up
traced the absent second trouser/cuff/boot cue to pose03, held for200ms between
two poses that each show both legs. The repaired candidate still needs fresh
human timed acceptance. A fresh blind comparison preferred the connected-leg
repair at 7.5/10 versus 7.0 for its immediate control, finding both legs attached
and traceable. This is a different reviewer/packet; its scores are not averaged
with the earlier 8.2. The next question is timed support movement and rhythm,
not another speculative redraw of the now-visible boot.

## Reproduce without generating

From the repository root, after `bash scripts/setup.sh`:

```bash
.venv/bin/python examples/recovery-refinement-20261023/replay.py \
  --output output/recovery-replay --godot
python3 -m http.server 8911 --bind 127.0.0.1 --directory output/recovery-replay
```

Use a fresh output path each time. Omit `--godot` if Godot is unavailable; the
image/editor replay still runs. Open
`http://127.0.0.1:8911/leg-review/` for the previous-versus-repaired comparison,
or `/review/` for the earlier four-way experiment. The viewer uses source frames
and holds, native/2x/4x, light/dark, stepping and a shared playback clock. Its
explicit before/after pauses separate repeated one-shot previews.

The replay exports all four initial variants, the leg repair, editable projects,
ASE, exact APNG and a separate136-binding candidate package. It compares all ten
final RGBA frames and rational holds with the saved candidate. `--godot` builds
and checks that package without replacing `examples/current-hero/package`.
New paint requires an actual ImageGen tool; this script replays saved returns.

## Operations and controls

1. Generation01 supplies a reclined entry with bent knees, replacing01's
   extend-then-refold gesture. This is a performance/readability choice.
2. Generation02 supplies a connected support-release drawing at05. The initial
   whole-row protection test restored part of the old grounded hand as well as
   boots; it was rejected. The corrected mask is x28..61,y56..79, excluding the
   arm. Its exact journal, undo/replay, PNG/ASE/APNG exports are regenerated.
3. The user identified03's loss of the second leg cue. Copying a neighbouring
   leg behind the whole old figure left its connection obscured; that trial
   remains rejected. Generation03 deliberately paints a connected folded leg.
4. Generation03 also moved the full figure in its returned canvas. Its complete
   redraw was not selected. The repair samples the measured1254-square return
   onto80x80, applies an explicit(0,-10) patch translation, then replaces only
   the saved250-pixel polygon. This is a declared patch registration, not an
   automatic per-frame fit. It changes167 RGBA pixels; all pixels outside the
   mask, the other nine drawings and all holds are exact.

Each generation folder contains the actual ordered inputs, literal prompt,
actual return, hashes and measured dimensions. Alpha200 and nearest-center
sampling are explicit choices for these returns, not universal import defaults.
`repair_leg.py` retains the polygon and the guarded editor transaction. Inspect
newly exposed joints in context; exact preservation alone cannot certify them.

The independent contact diagnosis corrected a tempting false fix: the source
guide lifts one hand and moves one ankle in depth. A proposed11px whole-frame
shift was not justified. Source movement, nonrigid painting differences and
registration are distinct. The source guide's raw rig is not included in this
study; measured results and the investigation report retain their evidence scope.

## Evidence and limits

`evidence/` contains frozen comparison packets/reports, the user's rejection,
contact diagnosis, rejected outputs, pixel/LibreSprite/video/Godot receipts and
the expected final manifest. Absolute paths in historical reports are source
provenance; the replay uses this repository's relative assets.

Actual final-candidate checks cover ten-frame LibreSprite export equality,
20 browser canvas comparisons, exact96-frame80Hz video timing, and a
136-animation/561-exposure Godot inspector. These establish their stated
artifact and runtime scope. They do not establish a visual9/10, collision,
damage, equipment behavior or acceptance of other directions. The user rejection
remains recorded in `USER-PLAYBACK-FEEDBACK.md`; a later repair needs its own
normal-speed verdict.

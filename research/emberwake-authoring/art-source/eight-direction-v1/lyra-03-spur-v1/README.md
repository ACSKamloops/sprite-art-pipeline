# Lyra SE03 old-glove remnant cleanup

This package contains the exactly approved17-pixel cleanup:16 erasures of wrongly sampled old glove outline/halo plus1 exact hip-underpaint restoration. Root inspected `proof/compact-source-owner-before-after.png` and approved this scope. It makes no motion-improvement or new art-score claim. No other03 geometry, frame05path, timing, pivot, current glove/upper/hem, or complete boots change.

Inspect `OWNERSHIP-FINDING.md`, the compact proof, `COMPACT-PROOF-RECEIPT.json`, and `projects/EDITOR-RECEIPT.json`. All source witnesses, ownership maps/masks, before values and exact17 coordinates remain in `inputs/` and `journal/03-literal-erasure.json`. The latter is the literal pixel record; `projects/journal.json` is the real sprite toolkit editor journal with one guarded transaction. `projects/initial.json` and `projects/final.json` are complete editable eight-cel projects. The included `/editor/` can load those files when served locally; no external GUI acceptance is claimed.

Rebuild from this folder using Python with Pillow and NumPy:

```bash
python3 repair_spur.py --local-only
python3 scripts/build_editor.py
```

Reproduce in a new folder and verify candidate PNG bytes, exported PNG bytes, RGBA, actual project, transaction and both journals:

```bash
python3 scripts/verify_portable.py /absolute/path/to/a/fresh-replay-folder
```

The main package ran `repair_spur.py` without `--local-only` to hash-check all retained canonical inputs before/after. The separate fresh-folder proof used `--local-only` and never read canonical paths. Toolkit code is copied locally; hashes and source locations are in `docs/TOOLKIT-PROVENANCE.json`. Source maps are existing artwork provenance, not a recovered anatomy or rig claim.

All eight editor-export PNGs decode to exact candidate RGBA. The toolkit uses PNG compression9 while retained candidate PNGs preserve source encodings, so source-versus-editor PNG file hashes may differ. Fresh replay reproduces both banks' respective PNG bytes exactly. Other seven source PNGs are byte-exact. The core rejects stale project, stale cel, outside-mask RGBA, and outside-mask indexed patch attempts atomically, including failure after a staged palette operation. Undo, redo and journal replay return exact project hashes.

The native/2x/84 light/dark sheets retain fixed canvas registration. This is cleanup evidence only; there is no new normal-speed human-playback, engine, world-translation, contact or weight-response test. No additional art experiment is included.

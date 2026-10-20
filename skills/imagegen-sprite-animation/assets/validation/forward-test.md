# Offline forward-use validation

The installed skill's written instructions successfully reproduced the bundled extension and finished recoil in this fresh directory. No model/network API, dependency installation, source project, companion toolkit, or unrelated project history was used. No aesthetic scores were assigned.

## Reproduced outputs

| Output | PNG | Receipt |
| --- | --- | --- |
| Extension | `/tmp/imagegen-skill-forward-ir0kefue/extension/frame.png` | `/tmp/imagegen-skill-forward-ir0kefue/extension/receipt.json` |
| Finished recoil | `/tmp/imagegen-skill-forward-ir0kefue/recoil-finished/frame.png` | `/tmp/imagegen-skill-forward-ir0kefue/recoil-finished/receipt.json` |

Both output directories also contain `source-map.npz` and `triangles.json`.

## Verified

- Both read-only `replay` commands and both fresh `bake` commands passed under Python 3.14.4, NumPy 2.3.5, and Pillow 12.1.1. The bundled explicit triangles meant SciPy was unnecessary for this run.
- An independent decoded-image comparison found zero differing pixels against each retained expected image, across every RGBA channel of both 192x192 outputs.
- Baked `source_xy` and `source_kind` arrays exactly match the retained frozen maps; emitted triangles equal each spec's explicit triangles.
- Helper checks passed for source hashes, protected-body equality, and the exact rigid glove rectangle.
- Finished recoil differs from raw retained recoil at exactly the 18 declared edit destinations; the helper reports 18 requested edits and 18 actual changed RGBA pixels.
- Rerunning each bake at its existing output directory returned exit code 1 with `Refuse to overwrite output directory`. SHA256 inventories before and after prove all output files stayed unchanged. A pre-existing empty output directory was also refused and stayed empty.
- All 40 installed skill files have identical before/after SHA256 inventories. No source project was opened or modified.

## What this establishes for another character

The portable helper can reconstruct this saved mapping and its literal repairs deterministically, preserve the body outside the declared donor ROI, and protect an exact distal glove region. Its documented replay/bake commands were sufficient to perform this local task without source-project dependencies.

A different character still needs accepted actual paint, complete compatible-view limb donors, a measured canvas/ROI, corresponding source/target controls, rigid rectangles, and reviewed connectivity/maps. This test does not establish how easy or reliable that new control authoring is, generate absent anatomy or poses, reproduce a stochastic ImageGen request, transfer art scores, or approve motion. It reran no layered editor exchange, full project journal/undo, APNG/video/timing, browser, Godot, controller, equipment, or other-view test.

## Usability gaps and claim boundaries

No blocker or false completion claim was observed for the documented standalone fixture workflow. The finished-recoil bake is obtained by the straightforward substitution of `recoil-finished.json` into the shown extension bake command; it is not separately shown in the quick commands.

The practical gap for new-character work is manual spec authoring: this package supplies the numerical format and fixed examples, not a control-point picker, anatomical fitting tool, or one-command whole-animation builder. Its standalone output is a PNG/map/triangles/receipt, not a layered editable source, full history journal, timing export, or engine delivery. The text explicitly acknowledges these boundaries and companion dependencies; these replay results must retain that qualification.

Machine-readable evidence and exact executed commands are in `/tmp/imagegen-skill-forward-ir0kefue/validation-summary.json`, `*-replay.json`, `*-bake.json`, and `*-overwrite.json`. The retained harness is `/tmp/imagegen-skill-forward-ir0kefue/validate.py`; it deliberately expects unused output directories and therefore is not intended to rerun in-place.

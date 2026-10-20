Brann northeast walk: editable native package

Open `native/brann-ne-walk.aseprite` in LibreSprite. Keep its adjacent `.sprite-lab.json` sidecar. The primary source is one honest flat layer with8painted cels on a fixed128×128stage and pivot64,112. It does not imply hidden body parts or a rig. Northwest remains the conditional mirror `x_new=128-x_old`; the primary editor project is northeast.

This is the explicit root production derivative of frozen manual-cycle-v6: exactly11black `[0,0,0,1]` background pixels at the stage border were removed across7cels. All otherRGBA, including every alpha≥2pixel, stays exact. `inputs/BORDER-CLEANUP.json` retains the literal root receipt. `raw-project.json` and `cleanup-journal.json` retain the real seven guarded candidate patches. Python and browser journal replay, full undo/redo, and browser Undo/Redo buttons were checked. No pencil strokes or extra cleanup were invented.

The authoritative clock is160Hz with9ticks per cel:9/160second each,72ticks or0.45second per loop. There are no authored events. Native ASE milliseconds are56,57,56,56,56,57,56,56, totaling450ms. Individual quantization errors are−0.25,+0.75,−0.25,−0.25,−0.25,+0.75,−0.25,−0.25ms; cumulative boundary errors are−0.25,+0.5,+0.25,0,−0.25,+0.5,+0.25,0ms. The sidecar preserves exact ticks, loop, pivots and empty event list. Native millisecond holds are an editor preview of that rational clock.

Actual LibreSprite1.3 saved, reopened and rendered all8cels. Both decoded ASE rounds, its1024×128sheet, and sidecar reimport match every sourceRGBAbyte, including alpha. `evidence/VERIFY.json` binds the actual commands, software and checks. The browser's editableRGBAmodel also matches all8cels and traverses the72tick loop without events. Canvas2D display rounds some partially transparentRGBpixels; that display is not claimed byte-identical. The native PNG/ASE/editor model evidence remains exact.

For browser editing, serve this folder with `python -m http.server 16785 --bind 127.0.0.1` and open `http://127.0.0.1:16785/editor/?project=../project.json`. Fresh primary loads with empty edit history. To inspect the actual cleanup history, open `raw-project.json`, then load `cleanup-journal.json` through Open journal. Undo returns the raw source; Redo returns the cleaned primary. Save future changes to new files and retain the sidecar.

Rebuild the flat editor/native package into a fresh folder:

```bash
python scripts/replay_editor.py --out /absolute/path/to/fresh-editor-build
```

Pillow12.1.1 and LibreSprite on PATH are required. `--raw` selects the preserved raw-reviewed source. The default uses only the literal root cleanup, performs the real native save/reopen/render/reimport, and rejects changed pixels outside the declared masks. This uses local package inputs only; original absolute paths in provenance identify historical sources and are not runtime dependencies.

The separate `source-rebuild` folder contains four native ImageGen keys, literal visible-leg ownership/hip placements, the exact base-v5 construction spec, frozen integer source maps, and the real arm-v6journal. Its largerJSONfiles use lossless gzip; `COMPRESSION.json` records decoded-byte hashes. No failed trial directory or final frame paint is used to reconstruct the animation. It first reproduces raw-v6, then applies the separately declared11pixel production delta and emits the conditionalNWmirror. It requires NumPy2.3.5 and Pillow12.1.1:

```bash
python source-rebuild/rebuild.py --out /absolute/path/to/fresh-source-rebuild
```

The source replay checks exact original base/final project hashes, arm-map/journal equality, all8decodedRGBAframes, and exact PNG bytes with the pinned dependencies. It replays retained paint; semantic ImageGen re-execution is not claimed reproducible. Its internal three source layers are reconstruction evidence, while `project.json` is the flat editable primary.

The existing independent variantBreview is retained verbatim under `review/`: drawing8.5, temporal identity8.5, motion/readability8, game use8, overall8, scoped to frozen raw-v6 northeast/northwest. That review used ordered stills/chronology and did not establish human normal-clock fluidity, game velocity or physical contact. The root's cleaned-delta acknowledgment is tracked separately in `MANIFEST.json`; this package does not silently recertify the cleaned art. Native exchange and source replay are separate from art judgment and game integration.

The literal conditionalNWmirror retains six blackalpha1border pixels in06/07 at x127,y50/51/64, because NE x1 maps to NW x127. `evidence/MIRROR-GUARD-NOTE.json` records this. No additional cleanup was performed; the root owns any further guard derivative. The native primary remains the exact11pixel NEderivative.

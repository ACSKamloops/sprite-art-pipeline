# Brann northeast jab: preferred source-hand edit

The primary editable project is `run/preferred-project.json`. The actual LibreSprite-saved and reopened document is `run/native/preferred-reopened.aseprite`; keep `run/native/preferred.aseprite.sprite-lab.json` with it when reimporting. The document honestly contains one flat source-art layer and eight distinct full-canvas cels, in order 08, 09, 10, 11, 12, 13, 14, 22. No separate hand, body, or weapon layers are claimed.

The existing source10 clenched-hand transplant is imported into source11 once through the guarded `candidate_patch` transaction. Its allowed domain is exactly `old_owner | target_owner` from the separately retained upstream hand map. All 234 changes lie within that domain; the other seven source PNGs remain byte-exact frozen inputs, and their constructed and native-rendered RGBA is exact. The source11 PNG is `c68dd7f8f86a2d06b432b0c604e3014279316954649474680c7191105f507350`. The source construction and body preservation are checked independently of editor replay.

The authoritative project runs at 200 Hz with tick holds `[12,14,11,11,13,7,7,7]`, equivalent to `[60,70,55,55,65,35,35,35]` ms. It lasts 410 ms, does not loop, has empty animation events, and keeps both pivots at `[64,112]`. These native millisecond holds survive actual LibreSprite save and reopen without quantization. Hero's 160 ms hit value is parent-supplied source-code context only; no event is invented in this project or ASE exchange. The sidecar retains the nonloop and pivot metadata; LibreSprite's transport is not a game-loop implementation.

This package verifies editing and exchange mechanics. The parent's preferred source-hand choice is retained; no motion, anatomy, game-runtime, or complete-action quality acceptance is inferred. Canonical sources and the full game were not changed. There was no image generation or remote network request.

## Offline reproduction

Required installed dependencies are Python 3, Pillow 12.1.1, NumPy 2.3.5, and LibreSprite 1.3. Toolkit Python/editor code and every input read by the replay are bundled. No external source directories are read. `requirements.txt` records the Python dependency versions; no dependency installer runs as part of replay. `DEPENDENCIES.json` records actual local executable paths and hashes used for this evidence.

From this folder, use a nonexistent destination:

```bash
python3 scripts/verify_package.py
python3 scripts/replay.py --out /tmp/brann-ne-jab-replay-fresh --libresprite libresprite
```

The second command rejects an existing output directory. It reconstructs the source-hand candidate, constructs the flat project, applies one guarded import, proves undo/redo/journal replay, tests real stale-project/stale-cel/outside-mask failures with atomic rollback, exports, invokes actual LibreSprite save/reopen/render, compares all eight RGBA cels and holds, and reimports using the required sidecar. A valid palette operation precedes the stale-cel and outside-mask failures to prove rollback after a staged valid operation. A rejected CLI transaction also preserves two existing output files byte-for-byte. `run/` is the primary evidence; `replay-check/` is the completed independent fresh-output replay. Both have 79 targeted checks and identical project, transaction, journal, and native project bytes.

Raw native PNG encodings differ from the frozen source PNGs for all eight frames. Their decoded RGBA bytes, including partial alpha, match exactly. `run/native/NATIVE-PROOF.json` records both hash types, every actual native path, command, log, and native hold. This distinction prevents PNG compression changes from being mistaken for pixel changes.

## Open the editor

```bash
python3 -m http.server 8937 --bind 127.0.0.1
```

Open `http://127.0.0.1:8937/toolkit/editor/?project=../../run/preferred-project.json`. To inspect the import history, open `run/source-project.json` and then load `run/journal.json` with **Open journal**. The one edit supports exact Undo and Redo. Native reimport is also available directly:

```bash
python3 toolkit/scripts/sprite_edit.py ase-import run/native/preferred-reopened.aseprite /tmp/brann-native-reimport.json --sidecar run/native/preferred.aseprite.sprite-lab.json
```

The actual browser proof is `output/playwright/BROWSER-PROOF.json`, with a source11 editor screenshot and UI-downloaded project/journal. Fourteen targeted browser checks cover the import, actual UI Undo/Redo, file save/reopen, journal file replay, the three real atomic rejection fixtures, exact hold boundaries, and actual one-shot playback. Python independently verifies all eight browser canonical RGBA hashes. Browser Canvas2D readback is not claimed exact for this partial-alpha artwork.

The browser probe used its own `brann-ne-jab-edit-v1` session and local port 8937; both were closed after verification. The optional probe is retained in `scripts/browser-check.js` and uses the locally installed Playwright CLI plus Chromium configured in `.playwright/cli.config.json`. Its external requests are blocked. Early automation failures are retained in `output/playwright/browser-attempt*-failed.log`: the sandbox lacked a Node URL global, then short-clip transport timing and an asynchronous completion poll raced. The final probe captures playback inside the browser and waits on the completed UI state. `browser-run.log` and `BROWSER-PROOF.json` are the current passing results. These were probe failures; native mechanics and the source art did not change.

`upstream/original-construct.py`, `ORIGINAL-INPUTS.json`, and `ACTION-PACKET-INPUTS.json` are frozen historical provenance only. The action packet references other original review/context assets that are not dependencies of this package. Replay uses the local minimal input set, ownership map, and bundled construction code. `PACKAGE.json` is the intake map; `SHA256SUMS` freezes package files. Runtime Python caches are excluded from that ledger.

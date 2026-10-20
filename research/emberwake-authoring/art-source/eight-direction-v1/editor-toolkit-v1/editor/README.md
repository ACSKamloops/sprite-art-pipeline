# Fine pixel editor

A static, local-first workspace for `sprite-edit-project/v1` layered indexed art. Open `editor/` from an HTTP server:

```sh
python -m http.server 8137 --bind 127.0.0.1
# http://127.0.0.1:8137/editor/
```

Append `?project=../examples/study/project.json` to load a relative project URL, or use **Open project**. The default calibration study is a tool fixture, not finished character art. No server writes, external services, package build, or ROM are required. The source project stays separate from the edited project; save both when exchanging a journal.

Choose a frame, layer and palette index. Palettes are paged20colors at a time; the explicit palette-index input and programmatic selector reach every color, including the3461-color authored study. Initial zoom fits the loaded canvas. Pencil and eraser interpolate pixel-coordinate strokes; one stroke is one undo step. Region mask selects an inclusive rectangle, constrains strokes, and limits replace-color. A locked layer refuses edits; a global palette change also refuses to recolor a locked layer using that index. Missing frame cels remain transparent and cannot be painted until the producer supplies a cel; this editor does not invent bindings.

Onion skin shows adjacent project frames; guides show declared render and ground pivots. Changed-pixel overlay compares exact composite RGBA with the original loaded source. Inspect reports coordinate, per-layer cel/index, lock state and canonical RGBA. View overlays are separate from art and never enter saved pixels. Zoom changes display size only. Playback uses animation FPS and frame duration_ticks, emits every crossed authored event, and stops a one-shot at its last frame.

**Save project** downloads lossless project JSON. **Save journal** downloads the common core journal. In the journal panel, **Save source** preserves its starting project; **Open journal** replays against that original source and verifies every receipt before updating any state. Undo/redo preserve the redo branch until a new transaction replaces it. Review notes bind observed defects and repair targets to a current project hash with decision `unreviewed`; passing pixel checks never approves art.

## Programmatic API

`window.SpriteEditor` is available after `SpriteEditor.ready === true`:

```js
const original = SpriteEditor.getProject();
const transaction = {
  schema: 'sprite-edit-transaction/v1',
  expected_project_sha256: await SpriteEditor.projectHash(original),
  reason: 'Repair one scarf seam without changing other pixels',
  operations: [{op:'paint', cel_id:'scarf-right-02', points:[[14,19,6]]}]
};
const receipt = await SpriteEditor.applyTransaction(transaction);
const pixels = SpriteEditor.renderRGBA('walk-right-02'); // Canonical composite RGBA bytes
const displayed = SpriteEditor.canvasRGBA(); // Actual art-canvas read-back, excluding guides/grid/onion/diff
const inspection = SpriteEditor.inspect(14,19);
const journal = await SpriteEditor.exportJournal();
await SpriteEditor.undo();
await SpriteEditor.redo();
await SpriteEditor.replayJournal(original, journal);
```

Other operations: `erase`, `replace_color`, `translate`, `translate_layer`, `palette`, `palette_add`, `candidate_patch`, `frame_timing`, `pivots`. `pixels.js` matches the shared Python operation schema, canonical compact sorted-key SHA256, whole-cel candidate SHA, integer source-over compositor and exact receipt shape. Unknown keys, stale hashes, duplicate masks, clipping without consent, invalid indices and outside-mask candidate changes reject the entire transaction. Timing/pivots remain unchanged unless their explicit operation is used.

`loadProject(project)` validates before replacing state. `getSourceProject()` returns an immutable-copy starting project. `snapshot()` reports the current hash, selections, history cursor, mask and playback state. `selectFrame`, `selectLayer`, `selectPalette`, `play`, `pause` and bounded `advanceTicks(0..10000)` support deterministic automation. Returned project/journal data are copies; callers cannot mutate the editor by changing them.

Canvas2D stores premultiplied colors internally; arbitrary translucent colors can be rounded when reading canvas pixels back. Canonical palette and project RGBA are authoritative editable values. Actual canvas equality is tested for the opaque mouse-edit fixture; canonical integer partial-alpha blending is independently compared with Python. The UI does not infer anatomy, generate missing poses, perform rigging, or replace the full feature set of a dedicated sprite editor.

## Browser and independent Python verification

Playwright CLI is used to run the real browser, not a mocked DOM. Configure a locally installed Chromium executable if the CLI default Chrome channel is unavailable. `editor/.playwright/cli.config.json` records this workstation's path; update it on another machine.

```sh
/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh --session fine-editor open http://127.0.0.1:8137/editor/ --config editor/.playwright/cli.config.json
/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh --session fine-editor snapshot
/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh --session fine-editor run-code --filename editor/browser_check.js
python editor/verify_parity.py --core-root /path/to/sprite-construction-lab-core
```

CLI failures can print an error with a successful process status; require `editor/output/playwright/browser-check.json` with passed=true plus the current success result in the log. Checks include actual mouse paint/erase/mask, UI undo/redo, locked-layer refusal, browser download and file reopen, common journal replay, ten operation-family fixtures, eight atomic rejection cases, actual requestAnimationFrame playback and exact hold/event crossing. Python independently checks every fixture project, receipt, hash and per-frame RGBA plus the mouse journal. Desktop/mobile screenshots and full machine reports are retained under `editor/output/playwright/`.

## Actual project scale check

`large_project_check.js` uploads the real layered-cutout and native walk/Sword projects, makes a real mouse edit on a visible layer pixel, checks actual art-canvas RGBA and indexed data, undoes to the exact initial hash and replays the full receipt journal. Native shared cels remain shared: the edited walk cel has five referencing frames; the Sword cel has two. Root source files stay read-only.

Run with the same CLI session:

```sh
/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh --session fine-editor run-code --filename editor/large_project_check.js
```

The retained report gives measured workstation times, not universal performance promises. The11MB/5.4million-index/24frame/11layer study loaded in855ms, localized mouse edit plus verified hash read-back1483ms, undo737ms, replay2224ms. Native walk timings were256/453/260/586ms and Sword323/613/365/897ms. Exactly20palette swatches were rendered for the3461-color study. Numeric-array hashing, checker patterns and unchanged-hold redraw suppression keep the large project usable without altering its palette or art.

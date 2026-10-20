Frozen Rowan SE odd-pose paint cleanup

`selected/00..07.png` are the exact eight preview frames sent for independent review. They have not been revised during packaging. Poses00/02/04/06 are byte-identical copies of the deeper coherent-upper B control. One built-in OpenAI ImageGen call supplied new complete waist/lower paint for01/03/05/07; the stable B upper and complete source02 forearm/glove RGBA, including transparent ownership, were restored. No new narrowing, timing change or per-pose fit was applied.

The actual1254×1254 returned sheet is retained in `generation/raw.png`, with the literal prompt/request, actual four-cell edit target and eight-pose context, their roles/hashes, original tool output location and before-edit dimension receipt. It was registered once: nearest1254→256 whole sheet, then native translation[0,−2]. Raw tiles are627×627; native tiles128×128. Cells UL/UR/LL/LR supply01/03/05/07. Mainbody alpha ownership only removes foreign faint fragments, using the declared connected-body rule. The whole registration and per-pose bounds are in `REGISTRATION.json`.

The retained `inputs/B/` are the complete frozen coherent-upper starting authority, not partial strips. `inputs/upper/` retains the exact source02 paint and complete arm owners used for restoration. `masks/` and `maps/` preserve permitted lower/waist paint, actual differences, gloves with transparency, generated alpha ownership, and actual raw-pixel witnesses. Actual generated feet are retained: sole bottom drift versus B is−2,+1,0,+2px at01/03/05/07. This is disclosed, not corrected by independent cel fitting. No foot-locking or physical contact claim is made.

`projects/` contains the real toolkit initial/final projects, four guarded candidate-import transactions and journal. Actual undo to initial, redo to final, and journal replay passed. Deterministic replay also reconstructs every cel from the retained raw sheet and upper sources, separately from the journal. In the completed fresh run, both methods matched all eight selected PNGs in decoded RGBA **and PNG bytes**. See `REPLAY-RECEIPT.json`.

Rebuild to a fresh nonexistent output directory; no model call, network or external art path is used:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/rebuild.py --output /FRESH/rowan-cleanup-replay
```

Dependencies: Python3, Pillow12, NumPy2 and SciPy1. The construction toolkit is bundled. The script refuses an existing output directory and writes its eight construction PNGs, eight journal replay PNGs and comparisons there. Initial/final projects retain128×128 stage, pivot[64,112], eight9/160-second holds and450ms loop.

`index.html` links full-eight native,84px nearest proxy and2× before/after chronologies plus synchronized exact-clock MP4. The video contains eight450ms cycles at160fps; each pose holds9frames. These files support visual inspection; this package does not certify continuous human playback or runtime translation/contact.

No producer score or art acceptance is assigned. The separately retained narrow-contact trials were rejected by the prior frozen paired review and are not dependencies. The other three coherent-upper banks are separately packaged as **UNSELECTED** in sibling `unselected-coherent-upper-v1`. `INTAKE.json` lists exact paths and dependencies; `SHA256SUMS` freezes this package.

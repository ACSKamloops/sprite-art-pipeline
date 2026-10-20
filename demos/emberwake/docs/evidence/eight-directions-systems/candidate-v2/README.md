# Provisional candidate-v2 systems, pixels and ordinary browser

These receipts use the six actual candidate-v2 files supplied by the root at `art-source/eight-direction-v1/candidate-v2/{rowan,lyra,brann}/{atlas.png,animations.json}`. `asset-snapshot.json` records each source, destination and exact hash; copied assets are not part of the systems commit. All three atlases declare 16 columns, eight views and all 48 action clips. This is actual provisional paint, separate from the synthetic mechanics fixture and from later final motion/art acceptance.

Verified results:

- Production resources: **1,163 assertions** (`production-resource-checks.json` / `.log`), including every actual action frame/region and all 24 release bindings.
- Rendered releases: **272 assertions**, **24 paired PNGs** under `releases/`; each image shows the plain actual release cel on the left and fire release on the right. `releases/RESULTS.json` binds atlas, manifest and screenshot hashes, socket, frame, columns and changed paint/effect pixels. Actual engine Xvfb rendering used Mesa llvmpipe; one unsupported V-Sync warning is retained. These checks do not recognize glove anatomy or assign an art/motion score.
- Ordinary browser: **192 assertions**, one incomplete asynchronous live-projectile sample for **Brann southeast** (`ordinary-browser-checks.json`). Every selector and all four diagonal walks, punches and casts were exercised through actual menu clicks and keys with `test_mode=false`. All speed samples use simulation ticks and agree with normalized `158` movement speed. Opposite held input cannot swivel the observed committed punch/cast while recovery remains active.

The browser used the exact local export in `web-export-hashes.json`, at `http://127.0.0.1:8908/index.html`, desktop viewport 1280×720, an isolated Chromium context and read-only diagnostics. No teleportation, save editing, damage bypass, actor setter, test-mode mutation or remote publication was used. There were no page errors or app/engine console errors during the successful interaction loop. The retained boot log contains a cosmetic missing `favicon.ico` 404 and four software WebGL ReadPixels stall warnings. This is not a hardware performance or multi-device claim.

`browser-screenshot-manifest.json` records all 25 ordinary-browser PNG hashes and local paths. Four representative screenshots are copied into `browser/`; the complete originals remain in the systems worktree's `output/playwright/`. They are asynchronous samples, so an `attack` filename does not guarantee the exact attack cel. The frozen native fixture supplies exact release evidence.

Preserved failed attempts:

- `browser-setup.json`: default Chrome was absent; the successful launch used an already installed Chromium binary, without installation.
- `ordinary-browser-first-run.log`: a release-facing assumption failed. Serial key-up delivery can leave a cardinal key held between events; the corrected check batches releases and compares actual zero-input idle observations.
- `ordinary-browser-second-run.json` / `.cli.log`: facing had correctly changed to the opposite held direction after recovery ended before the next browser round trip. Its still-locked recovery snapshot retained the original diagonal correctly. No controller change was made.
- `ordinary-browser-checks.json` / `ordinary-browser-third-run.cli.log`: the successful result after correcting those harness assumptions, batching key deliveries, comparing zero-input idle snapshots, reacquiring the requested direction through real keys and checking commitment in the locked recovery snapshot. Failed-attempt screenshots remain locally in `output/eight-direction-browser-candidate-v2-failed/`.

Commands for repeating against the final build are in `tests/EIGHT-DIRECTIONS-QA.md`. The final walk cels and full visual/motion rating still require the root's later checks. The baseline 400 assertions are root-owned for the integrated build and were not rerun in this followup.

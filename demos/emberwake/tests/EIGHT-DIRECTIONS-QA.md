# Eight-direction production QA

Executed against an explicitly frozen copy of the provisional actual `candidate-v2` paint: production resources **1,163 assertions**, rendered release fixture **272 assertions / 24 pairs**, ordinary browser **192 assertions / 1 incomplete asynchronous projectile sample**. Evidence and exact asset/export hashes are under `docs/evidence/eight-directions-systems/candidate-v2/`. These are binding/behavior results for candidate-v2; final motion and art acceptance remain separate. Copied production assets are excluded from the systems commit and restored to the original worktree baseline afterward. The earlier 161-assertion synthetic fixture remains separate evidence.

## Actual production resources and all 24 releases

First import the completed art, then run the existing production resource/behavior test:

```bash
LP_NUM_THREADS=4 OMP_NUM_THREADS=4 godot --headless --path . --editor --import
godot --headless --path . --script tests/eight_directions.gd -- --test-mode --production
```

Run the new fixture with a real renderer and a fresh evidence directory:

```bash
mkdir -p output/eight-directions-production-release-v1
LP_NUM_THREADS=4 OMP_NUM_THREADS=4 xvfb-run -a godot --path . \
  --rendering-method gl_compatibility --rendering-driver opengl3 --audio-driver Dummy \
  --script tests/eight_directions_render.gd -- \
  --eight-render-output=res://output/eight-directions-production-release-v1
```

Use a different directory for a later build/run. Reject any `SCRIPT ERROR`, engine `ERROR` or `EIGHT_RENDER FAIL`, even if the process otherwise prints output.

The renderer preflights Rowan, Lyra and Brann before producing images; every bank must explicitly declare all eight views and pass the actual loader. It then saves 24 PNGs, one per actor/view, each with plain engine pixels on the left and the fire release on the right. Both halves use the actual authored release cel at `.24` seconds. It checks the declared source socket is near opaque paint, that rendered warm pixels change around the projected socket, that the physical projectile stays at the feet and that its direction agrees with the committed view. `RESULTS.json` binds each pair to atlas/manifest/screenshot hashes, actual frame, native socket, cell dimensions and columns. Sixteen-column atlases are supported.

The comparison is a frozen integration fixture. Opaque pixels near a declared socket cannot identify glove anatomy automatically. Review all 24 PNGs for correct painted glove, perspective, occlusion and alignment. Motion/appearance scores require separate full playback and visual review.

## Ordinary browser play through all selectors and diagonals

Export a fresh Web build containing the completed banks and updated read-only `scripts/browser_diagnostics.gd`. Serve that exact build on a task-specific local origin. Use an isolated browser profile; this scenario starts real new journeys and saves normally through the UI.

```bash
mkdir -p output/eight-direction-final-web
godot --headless --path . --export-release Web output/eight-direction-final-web/index.html
python3 -m http.server 8908 --bind 127.0.0.1 --directory output/eight-direction-final-web
```

Leave that task server running in its terminal while using the browser from another terminal.

The existing Playwright CLI workflow accepts the function in `tests/browser_eight_directions.js`, matching the repository's other browser scenarios. For example, from the project directory after starting its local host:

```bash
mkdir -p output/playwright
python3 - <<'PY'
from pathlib import Path
import json
source = Path('docs/evidence/eight-directions-systems/candidate-v2/browser-setup.json')
Path('output/playwright/eight-browser-config.json').write_text(
    json.dumps(json.loads(source.read_text())['config']))
PY
/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh --session emberwake-eight \
  open http://127.0.0.1:8908/index.html --config output/playwright/eight-browser-config.json
/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh --session emberwake-eight \
  resize 1280 720
```

Use the actual task host/port if different. Run the scenario with the small repository runner, which rejects a false scenario result even if the CLI exits zero:

```bash
python3 tests/run_browser_eight_directions.py --session emberwake-eight \
  --out output/playwright/eight-directions-browser.json
```

It invokes the CLI with `--raw run-code --filename=tests/browser_eight_directions.js`, records the full CLI output and writes the parsed scenario JSON. Require `passed:true`, review console/page errors, and preserve the report and screenshots. Close only this task's named session afterward.

This WSL host has no default Chrome at `/opt/google/chrome/chrome`. The executed run used the existing `/home/astra/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome` through an isolated CLI config, with no browser installation. Exact configuration and the initial launch failure are recorded in `candidate-v2/browser-setup.json`. Reuse an installed browser path appropriate to the host when launching the session; `open --config PATH` accepts the standard CLI browser/launchOptions configuration.

The scenario uses real gallery controls to select each of Rowan/Lyra/Brann, confirms a new journey as needed, advances actual dialogue and requires `test_mode=false` plus the exported eight-view declaration. For every hero it drives northeast, southwest, southeast and northwest with real keys, measures displacement against simulation ticks, checks speed `158` and unit diagonal input, then presses punch and firebolt. Opposite held input must not swivel either action through recovery. Read-only diagnostics expose aim, action clock, pending release, velocity, input vector, simulation tick and current projectiles; they provide no control API. Missing asynchronous live projectile samples are explicitly recorded as incomplete observations rather than passing an empty assertion. Physical key-up delivery can briefly leave one cardinal key held, and opposite input may resume steering after recovery before a browser round trip completes; zero retention compares actual idle snapshots and facing commitment uses the still-locked recovery snapshot. Each action reacquires its requested diagonal with real keys. The native release fixture supplies exact launches.

Browser screenshots are asynchronous samples, not frame-exact release evidence or an art rating. No save injection, teleportation, damage bypass, actor setter or test-mode mutation is used. This authoring session did not have the Browser plugin; the scenario follows the repository's regular Playwright path.

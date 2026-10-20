# Installed verification and review — v0.9.0

The final suite passed **982 tests, zero failures/errors/skips** (113.359 JUnit
seconds). Source, wheel and installed runtime match across **186 files**.
Fourteen installed cold workflow checks, 18 real browser checks, 11 browser
postflight checks, nine source-bound setup checks and ten existing Motion Lab
browser regressions passed. No provider requests or new art generation occurred.
The older repaired walk remains unapproved for game art.

Runtime fingerprint: `a00047cb39709fec2fe8c0206de786ec935ad1aea985ba8ada467505e3d3f839`.
Wheel SHA256: `5c27a9b6068e01a7b9d868a8580c548a1aad5d6577c9c0ca6e77f0f4542a4421`.
[Machine evidence inventory](VERIFICATION.json), [source/wheel comparison](evidence/PACKAGE-COMPARISON.json),
[suite](evidence/TESTS.xml), [installed proof](evidence/INSTALLED-PROOF.json).

## Rendered flow

Browser plugin was not available; regular Playwright with installed Chromium
was used. Installed test origin was `http://127.0.0.1:8877/#parity`; the verified
package is now the main controller at **http://127.0.0.1:8874/#parity**.
Viewports: desktop 1440×1000 and mobile width390. The flow tested was hero PNG
upload → original palette/pixel/shape operation → guarded Workspace paint →
undo/redo → Studio export → independent cold reopen.

| Check | Result |
| --- | --- |
| Page identity and nonblank meaningful controls | Passed |
| Framework error overlay | Absent |
| Console/page errors | Zero |
| Desktop and mobile overflow | None observed |
| Real interaction and backend results | 18 checks passed |
| PNG and ZIP bytes, source footprint/history, exact rational still hold | 11 independent postflight checks passed |

The actual source paint changed exactly **52 indices**, all within the 52 unique
source footprint points. Cold restore replays the original source command and
retains undo/redo. All five output PNG hashes matched their receipts. The still
used `[1,12]` seconds; it contains no generated motion. Existing Motion Lab
regression separately exercised full native playback, 16 selected full-canvas
poses and exact authored holds, fine edit/undo, a 390-file ZIP inventory, and
resuming an already completed native run without provider requests.

Screenshots and replay artifacts remain outside Git:

- [Loaded hero input/output, desktop](/home/astra/artifacts/pixellab-parity-20261014/v090-final/browser/run2/UI-PREVIEW.png)
- [Full desktop controls](/home/astra/artifacts/pixellab-parity-20261014/v090-final/browser/run2/desktop.png)
- [Mobile controls](/home/astra/artifacts/pixellab-parity-20261014/v090-final/browser/run2/mobile.png)
- [Real browser receipt](evidence/INSTALLED-UI-QA.json), [cold postflight](evidence/INSTALLED-UI-POSTFLIGHT.json)
- [Reusable browser runner](evidence/qa-parity-real.cjs), [postflight](evidence/postflight.py)

## Defects exposed and fixed

Independent reviews found: mutable-array palette receipt identity drift; forged
pixel receipts accepted for promotion; detached shape evidence lost on export;
altered shape controls accepted with unrelated points; and an inline edit
receipt mistaken for an artifact ID in the UI after successful paint. The fixes
use one immutable snapshot, actual original-method replay, durable history
source edges, actual command/point replay and distinct inline/ID presentation.
[Palette review](PALETTE-ADVERSARIAL.md), [channel review](CHANNELS-ADVERSARIAL.md).
Failed browser runs and intermediate test logs remain in the external artifact
root. The stale pipeline catalog pin was intentionally updated with its old
bytes preserved. A separate scheduling-dependent test was corrected to resume
and explicitly wait for its durable queued job; job-manager behavior was unchanged.

## Reproduce

Run `scripts/verify_parity_installed.py` with the installed interpreter **from
outside the checkout**, supplying `--source`, `--wheel` and a new `--output`.
It verifies imported package location, byte inventories, actual original-method
execution, source receipts, exact still holds, shape paint and cold undo/redo.
`scripts/verify_pixellab_reference_slots.py --inputs RETAINED_PILOT --output NEW`
executes the shipped serializer against three retained actual reference PNGs.
Browser runners accept fresh external output directories; do not overwrite old
observations. No credentials or paid actions are needed for these checks.

Limitations: Linux/Godot/Node/ffmpeg host dependencies remain explicit; private
backend algorithms and universal behavior are not recovered; low-alpha browser
PNG decode differs from arbitrary supplied RGBA; full editor capture/undo
integration is outside the six pixel-method fixture host. No score of9/10 or
whole-product completion is awarded by these mechanical checks.

# Emberwake source loop preview

Run with the installed Python standard library:

```bash
cd /home/astra/artifacts/emberwake-moving-loop-evaluation-player-v1
python3 -m http.server 8796 --bind 127.0.0.1
```

Open http://127.0.0.1:8796/. No packages, models or network service are required. Use HTTP rather than opening the HTML directly so local fetch and integrity checks work.

The player shows A, B or split views; NE/NW; in-place or fixed-world-camera travel; play/pause and source-pose stepping; normal/quarter speed; fixed grid; light/dark/game proxies; exact 0.66 game scale and optional 2× diagnostic zoom. Canvas CSS pixels represent world units at 1× zoom; source stage is 128×128 with pivot (64,112). It never resizes a view to fit the browser. Scroll large views to inspect them; the world grid/camera remain fixed.

All eight holds are 9/160 s = 56.25 ms, totaling 450 ms. A monotonic elapsed-time clock selects the source pose. Travel is normalized NE=(1,-1)/√2 or NW=(-1,-1)/√2, multiplied by 158 units/s and translated simulation time. The constant-speed witness omits canonical acceleration, collision, state and controller behavior. At 1× zoom, 4.5 s of diagonal travel displaces the root by approximately (±502.753,-502.753) world/CSS units. Only the art is scaled by 0.66; world travel is not scaled by 0.66.

Travel pauses after 4.5 simulation seconds at a labelled test boundary; it never teleports the actor back during a running loop. Restart and configuration changes explicitly reset phase/world origin. The optional 9 s sequence holds the root at its starting world position for 4.5 s, then translates for 4.5 s without a root or phase reset at the midpoint. It auto-pauses at the end. Quarter speed stretches the sequence to 36 wall-clock seconds, excluding pauses. Selecting sequence mode and pressing Play also creates a capture ledger. Hiding the tab pauses the clock instead of silently collecting background time.

Export sequence timing JSON includes source hashes, initial/current controls, intended rational timing/onsets, control/boundary events and observed requestAnimationFrame callback times/root positions. Completed, aborted and in-progress exports are labelled. Configuration changes or stepping abort an active sequence; speed changes and pauses are logged. Browser callbacks and encoded JSON are not monitor presentation timestamps. No subjective score is recorded.

Manual boot-point picking is off by default. Enable it to pause and click a source pixel. Use 2× diagnostic zoom for precise pixel picking: at 0.66×, more than one source pixel can fall within one displayed pixel. Points are keyed to bank/direction/source pose; no automatic tracking occurs. They are always labelled **unknown contact** and are only diagnostic overlays.

`manifest.json` binds all 32 copied source PNGs, the exact source INPUTS.json and original full-packet hash ledger. The original context and proof PNGs are unused and omitted; the copied packet ledger therefore describes the original complete packet, not a complete manifest for this subset. The player verifies the 32 PNGs and copied hero.gd before playback. `input/hero.gd` is an exact read-only copy from canonical emberwake-demo, SHA-256 `1189e397a2e2097a9e910bcda7167fafdd6838e5746567b5f5a0a0ba44e92da0`; relevant movement references are lines 11,120,137–140. The canonical project and frozen reviews were not edited. No real game imagery is used.

**SOURCE PREVIEW** means source-image and reference-translation playback, not Godot execution, physical contact certification or human controller/perception acceptance. Normal and quarter-speed playback are available for a human; automated browser checks do not establish a human motion judgment.

Recheck the self-contained inputs and timing geometry with:

```bash
python3 verify-inputs.py
node verify-core.mjs
sha256sum -c SHA256SUMS
```

Browser validation uses a new named, owned Playwright CLI session with an existing cached browser and CLI. `playwright.config.json` is local verification configuration only; its absolute executable path is not a runtime dependency of this static player. See `VERIFICATION.json` for completed checks and limits.

`SHA256SUMS` freezes the deliverable source, copied inputs and saved verification evidence. Mutable `.playwright-cli` bookkeeping, `output/playwright/profile`, and `output/server.*` are excluded. An owned local server may be running; its PID and log are under `output/server.*`.

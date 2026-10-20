# Source loop comparison v2

Open **http://127.0.0.1:8797/**. The owned static server PID is in `output/server.pid`. To serve the completed bundle yourself:

```bash
cd /home/astra/artifacts/emberwake-moving-loop-evaluation-player-v2
python3 -m http.server 8797 --bind 127.0.0.1
```

This is **SOURCE PREVIEW**, with anonymous A/B labels and no score or method disclosure. It is not Godot execution, contact certification or human motion/controller acceptance. No real game imagery, models, installation, generation or engine changes are involved. V1 and its server on 8796 are preserved.

The actual frozen anonymous packet was bound only after root's explicit go. INPUTS.json SHA-256 is `aace754435f398b80d6878e9a5d5f1cba7c0e7f459c9682c4c4aa97470d13dcf`. Its four A/B SE/SW timelines each have sixteen 9/320-second slots: 28.125 ms per slot, 450 ms per complete loop. All 64 source-slot PNGs are exact copied bytes. Repeated drawings remain repeated drawings with their combined exposure; slot count earns no quality claim.

Use A/B/split, direction, in-place/fixed-world travel, play/pause/step, normal/quarter speed, grid, flat background proxies, exact 0.66 nearest rendering and optional 2× diagnostic zoom. The stage is 128×128 and pivot (64,112). Large views scroll without changing the world camera. Manual point picking is optional, untracked, keyed by source slot and always unknown-contact. Use diagnostic zoom for precise picking.

The optional 9-second sequence runs 4.5 seconds stationary then 4.5 seconds translated, with no root or source-phase reset at the midpoint. Translation is the normalized diagonal vector ×158×translated seconds. SE/SW move with positive world y from upper starting origins, and both zooms contain the full witness. Source art scale does not reduce world travel. Travel and sequence ends pause at labelled test boundaries rather than teleporting during the loop. Quarter speed takes 36 wall-clock seconds for the 9 simulation seconds, excluding pauses.

Exported JSON binds the original capture direction/banks, holds, cumulative boundaries, intended slot onsets, source hashes, control/boundary events and observed browser callback slots/root positions. Later UI direction changes do not rewrite a completed capture's timing metadata. Browser callbacks are not monitor presentation timestamps and do not prove subjective smoothness or physical foot contact.

`build.py` is the retained build source. It verifies every full-packet hash, requires INPUTS.json itself to be covered by that ledger, verifies ordered source PNG hashes and copies the required raster subset, exact metadata/ledger and frozen movement-reference script. It refuses to overwrite a binding. It reads 8- or 16-slot schedules and direction names from metadata, supports all four diagonal names, and requires positive rational holds totaling 0.45 seconds with exact integer-microsecond boundaries. Holds may be global, per bank, or on a timeline object with `frames` and `holds`. Split views select each bank's slot independently at the same simulation time; stepping uses the union of visible onset boundaries. A new frozen packet requires a separate new player version.

The copied original packet ledger describes the full original packet; unused context/proof images are omitted from this subset. `manifest.json` is the player binding, and `SHA256SUMS` freezes the complete deliverable. Mutable `.playwright-cli` bookkeeping, `output/playwright/profile` and `output/server.*` are excluded. Deliverable files are read-only after freeze.

Verification:

```bash
python3 verify-bound.py
node verify-bound.mjs
PYTHONDONTWRITEBYTECODE=1 python3 verify-template.py
node verify-template.mjs
sha256sum -c SHA256SUMS
```

`VERIFICATION.json` records the scoped completed checks: actual 16-slot onsets/wrap, SE/SW reference motion, 128 source-pixel composites covering every source slot at both zooms on the game proxy, targeted controls and completed 9-second JSON export. Older v1 8-slot NE/NW browser tests were not rerun. Synthetic template checks additionally cover 8/16 schedules, unequal holds and all four direction vectors. The v2 owned browser session was closed after validation; root/v1 tabs were not touched.

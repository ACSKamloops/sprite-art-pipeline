# All available native capture motion index

The reusable CLI reads an immutable exported capture index, verifies every route hash and every source WRAM/VRAM/CGRAM/OAM/PPU hash, and indexes every original video tick into SQLite. It verifies actual expected OBJ RGBA PNGs, palette RGBA images and indexed OBJ image bytes separately. No screenshots, raw WRAM, ROM, resampled poses or recentered art are copied into this catalog.

Run from the worktree root, with a fresh output folder:

```sh
python qc/engine/motion-index/index_captures.py --workers 6 --output /tmp/native-motion-catalog
python -m unittest discover -s qc/engine/motion-index -v
python qc/engine/motion-index/audit_catalog.py qc/engine/motion-index/catalog-v1
sqlite3 qc/engine/motion-index/catalog-v1/motions.sqlite < qc/engine/motion-index/queries.sql
```

Use `--corpus`, `--evidence-root` and `--artifact-root` to bind other corpus locations. This corpus omits `evidence/expected` from the Site checkout: actual expected PNGs are read from the original `/home/astra/projects/som-native-effect-renderer` export. The CLI resolves and hashes those files; it does not treat a declared pixel hash as verified when the PNG is missing. Six parallel read/verify workers feed one SQLite writer. Output is intentionally created exclusively: failed or prior builds are preserved, and repeated runs require a new folder.

`catalog-v1/summary.json` binds the database, source capture index, builder, CSV heatmaps and route coverage table by SHA256. SQLite `routes` binds each route JSON; `trace_sources` binds every joined raw CPU trace; `assets` records file hashes, actual RGBA hashes and resolved read-only asset paths. Raw source hashes remain per-frame columns. Capture paths can be recovered from the hash-bound source route JSON at `relative_tick`; no original snapshot is embedded here.

`frames` contains one original source-video-tick row, displayed expected OBJ/palette hashes, object/ownership/asset signatures, object counts and owner distribution. `actor_frames` contains all exported active actor slots plus the selected actor slot, decoded directly from that tick's SHA-verified 128KiB WRAM. `motions` joins those raw state fields with the separate display fields. Actor offsets are: E026/2 generic; E018 script start; E016 pointer; E012 countdown; E010 action word/low direction byte; E011 action row; E01C mode; E180 identity; E182 HP; E190 status; E060 effect mode; E020/22 world position; E19B charge; E041/E05D wait context. Direction remains the numeric native byte; unknown rows are not renamed. Selection runs group identical generic/script-start/action-word/mode/status while full per-tick pointer/countdown/state remains queryable.

Every source hash is validated. Route continuity, declared counts, one-tick durations and fixed selected actor scope are checked before indexing. Missing/duplicate ticks, flattened holds, wrong WRAM/display hashes and wrong selected generic are rejected by actual-corpus negative tests.

Sparse CPU traces join only when both capture parent and source tick match. PC/X/P and counts remain queryable. The owner contract is `1=actor-slot-X` only at four proven entry PCs: C0:F582 action selection, C0:F4CB actor update, C2:BF1D projectile construction, C2:C221 projectile update. Evidence paths and hashes are in metadata. Every other PC, invalid X or helper call has `0=unknown-owner`, even if X happens to resemble an actor slot. Stored M/X width flags can be queried; emulation-cached arithmetic flags are not newly synchronized by this passive index.

The long-form heatmap and 85-column matrix are method/route **co-occurrence**, never causal proof. `trace_present=0` means no trace file. `trace_missed_ticks` means ticks without any selected PC record, not lost trace records: scheduling and the selective hook naturally yield empty ticks. Dropped counts remain unknown when the original receipt does not expose them; `trace_sources.dropped_report` says so explicitly. A missing trace never becomes a claim that a method was not executed.

This indexes all available captures, not full-game coverage, every script branch, every target condition or every unobserved method. Expected display is the pure native OBJ reconstruction, not the full gameplay screen with backgrounds/color math/hardware limits. Raw selection state and presented OBJ source can differ by native DMA latency; neither is substituted for the other. Existing staged/natural provenance remains in hash-bound original route/capture ledgers. Full catalog unknowns remain unresolved rather than receiving guessed labels.

The included catalog has 85 routes, 28,123 source ticks, 110,470 actor-state rows, 2,708 selection runs, 187,976 PC/X/P hit groups and 3,764 unique indexed/palette assets. It verifies 140,615 raw source files. Database size is 24,268,800 bytes. Three routes have no CPU trace; 82 have a trace with no recorded dropped-count receipt. There are 4,511 ticks with no selected PC event, which are not classified as dropped. A separate read-only structural audit and eight actual-corpus verifier tests accompany the hash-bound build receipt.

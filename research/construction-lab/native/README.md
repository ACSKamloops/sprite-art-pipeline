# Native construction control

This is original-game control art, not newly authored art and not art approval. Three losslessly layered indexed projects contain **78 consecutive native presented frames**: a full Randi rightwalk cycle (30), normal right Sword action plus onset/recovery (19), and a native close-range Sword action including actual enemy HP20→2 (29). Each has complete copied raw hardware sources, exact source hashes, transparent golden PNGs, editable indexed full-canvas cels, and genuine layered OpenRaster files for every frame.

## Run

Requires Python 3 and Pillow. From repository root:

```sh
python3 native/audit.py
python3 native/export_exchange.py
python3 native/check_native_rules.py '/private/path/Secret of Mana (USA).sfc'
```

The pixel audit is portable and needs no ROM, emulator, source checkout, or capture producer. It independently decodes the preserved OAM high table, signed X, wrapped Y, OBJ sizes, tile addresses, 4bpp bitplanes, flips and CGRAM. It compares every constructed frame and producer golden to those raw pixels. If original capture paths still exist it also checks copied bytes against originals. No internal project hash substitutes for native fidelity.

Rebuild original captures with the already recorded source locations:

```sh
python3 native/build_fixture.py native/sources.json
```

`source_renderer.py` is the producer decoder; `audit.py` is a separate scalar implementation and imports no producer renderer. Their shared inputs are the hardware captures, not intermediate generated pixels. `audit-report.json` preserves real adversarial failures: substituted previous displayed pose, flipped/translated cel, changed positive hold, changed ground pivot, rounded clock, moved observed event, and an actually order-sensitive swapped OAM overlap. A sample with no sensitive overlap is explicitly not applicable rather than a fake pass.

## Coordinates and ownership

The canvas is the original 256×224 screen. No frame is alpha-centered or automatically recentered. Render pivot is the first captured actor screen render center, ground pivot is the first captured native screen/world anchor; both stay fixed. Per-frame native anchors retain movement. Actor world coordinates used by the game logic differ from screen coordinates E020/E022 used by native drawing. Render Y = E022 − (E074 &127) − E045. The cyan line in contact sheets is this captured native ground reference, not an inferred anatomical foot contact.

OAM layer IDs are stable hardware **slots**, not stable anatomical body parts. Layers are ordered back-to-front, descending OAM index; ascending opaque OAM wins. Each full-canvas indexed cel includes exact positions/flips and captured palette color. `bindings.json` retains the original local source pieces, signed positions, tile offsets and per-frame exact WRAM-to-OAM matches. A unique equality across x/y/tile/palette/flip/16px size marks actor body or attached weapon ownership. Unknown or ambiguous matches stay unknown, especially the one-tick parser/presentation phase boundary. Extra scene objects are preserved rather than silently assigned to the hero.

The six rightwalk snapshots visibly change lower-body silhouette and arm/equipment placement; the first wide stance and fourth reversed crouched stance differ. These are directly visible sampled phases, **not proven left/right foot IDs or biomechanical contact labels**. Native ground anchors are annotations supported by RAM, while foot anatomy and stylistic quality need separate review. Exact contact references for newly authored art require human landmarks or explicit rig data rather than mask-bottom inference.

## Native clock and events

Frame duration is one captured video tick at **60.098811862348406fps**; no GIF millisecond rounding defines source timing. `native-rules-report.json` checks the actual normal far Sword script6A96 against the original hashed ROM bytes, selected generic171/172/173 each five video ticks, B-release retaining native action20 until completion/reselection, and observed near enemy HP20→2 at source tick13860. These are observed native conditions/events. The files never invent hit-start/hit-end windows from sword appearance.

The normal frame controls leave E012=0, selecting the next pose on the next active five-video-tick parser invocation. F9 movement and8D palette helpers add no invented pose holds. FF performs completion and dynamic reselection; neither a literal loop nor general attack cancellation policy is inferred. Current WRAM frame selection precedes presented hardware by one video tick in this fixture. The actual hardware timeline stays authoritative, and nominal parser selection is identified separately.

Native rightwalk capture follows held right input at a map collision boundary, so the complete pose cycle is proven but unobstructed world displacement is not. Setup inherits a controlled sword-owned checkpoint; native equipment preparation and input are recorded, not natural game progression. No charge, HP, pose, script or direction RAM edits were added in the fresh right captures.

## Limits

Pure OBJ fidelity covers native object pixels and overlap. Background occlusion, SNES color math, scanline overflow limits and priority rotation are outside this control. The final one-tick sample hold is an export convention; native action end is separately established by captured mode/script transition. Original ROM is private and is never copied into this repository. The capture-derived editable fixture is game source art for verification, not a distributable replacement art library.

## Shared core cross-check and actual fine edit

```sh
python3 native/check_core.py
python3 native/check_exchange.py
```

The shared editing core renders every fixture frame against the independent raw hardware oracle. A real one-pixel masked paint operation on a visible native weapon cel produces exact index/RGBA localization, preserves timing/pivots/events, and demonstrates undo/redo/journal replay and layered ORA re-import. Source projects remain unchanged; the deliberate edit and its transaction/receipt/history are separate under `live-examples/`. Canonical shared API hashes differ intentionally from pretty/file hashes and are recorded in `core-crosscheck-report.json`.

`authoring-review/localized-knee-review.json` is a separate independent review of root's localized AI edit: exact outside-mask/alpha preservation passes, while costume-color drift and loss of the knee bend cue request art refinement. It is hash-bound to the actual reviewed images. Neither this original-game golden fixture nor local pixel preservation approves newly authored finished art.

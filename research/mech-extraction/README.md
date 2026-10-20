# MechWarrior 4 mech extraction workspace

The mech-only asset package is in `handoff/`. Read [the Blender handoff](handoff/BLENDER_HANDOFF.md) for import instructions, catalog counts, validation, and the remaining native animation conversion work.

The downloadable local package is `artifacts/mw4-mech-blender-handoff.zip`.

## Reproduce exports

The downloaded MyAbandonware MekTek ZIP remains in `sources/`, and its unpacked game data remains in `sources/game/`. Downloaded modding tools are in `tools/`; none of their Windows programs or the game executable were run.

The Python environment is `.venv/`. Source scripts preserve archive IDs and original byte hashes. Run these from this workspace in order:

```bash
.venv/bin/python scripts/extract_mechs.py
.venv/bin/python scripts/build_handoff.py
.venv/bin/python scripts/assemble_previews.py
.venv/bin/python scripts/validate_handoff.py
node scripts/validate_glb.cjs
tools/blender-linux/blender-4.5.9-linux-x64/blender --background --python-exit-code 1 --python handoff/tooling/blender_prepare.py -- --handoff handoff
.venv/bin/python scripts/package_handoff.py
```

Python dependencies are pinned in `requirements.txt`; the official glTF validator dependency is isolated in `.validation/`. Rebuilding the handoff overwrites generated OBJ, PNG, GLB, and inventory files; save texture updates and Blender projects separately.

The GPL license in `handoff/tooling/` covers helper code derived from the public ERF editor. It does not assign a license to the extracted game assets.

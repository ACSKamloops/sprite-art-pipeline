# Setup and verification

The tested environment is Ubuntu WSL with Linux-native tooling. Keep Windows and
WSL Codex homes distinct. The repository runs from any suitable Linux path;
historical absolute paths in case notes identify original local evidence.

| Dependency | Purpose |
| --- | --- |
| Python 3.14 + uv | Hashed workbench environment; package itself declares Python >=3.11 |
| NumPy, Pillow, jsonschema, packaging | Supplied-art workbench and raster tooling |
| pytest | Workbench and collection integrity checks |
| SciPy, optional | Source-warp reconstruction helper; frozen-map replay has a narrower dependency set |
| Node.js | Recovered JavaScript client-method execution |
| ffmpeg + ffprobe | Native video decode, exact-timing MP4 export and checks |
| LibreSprite | Actual editable ASE save/reopen tests and manual pixel editing |
| Godot 4.7.2 | Retained demo's recorded engine baseline; matching templates needed for Web exports |

The Godot version here is a recorded project requirement, not a claim about the
latest upstream version. Host binaries and export templates are not vendored.

```bash
bash scripts/setup.sh
.venv/bin/python scripts/verify.py
```

`setup.sh` creates this repository's `.venv`, uses the workbench's hashed lock,
then installs the local package without build isolation. It neither reads model
credentials nor starts a server/provider. `verify.py` writes logs and the current
receipt under `output/verification/`; committed verification receipts identify
the source snapshot tested for the published handoff.

The default verification runs workbench tests, editable-toolkit tests, integrity
checks and portable offline examples. Godot is an additional explicit check:

```bash
LP_NUM_THREADS=4 godot --headless --path demos/emberwake --editor --import
.venv/bin/python demos/emberwake/tests/run_checks.py
```

Actual native-editor checks require `libresprite` on PATH. Web export requires
adjusting machine-specific template paths in `demos/emberwake/export_presets.cfg`.
The imported game can run from its retained runtime assets without rebaking all
historical art. Authoring-script reconstruction may require local-only source
images listed in the provenance index; do not describe those as bundled.

Do not run retained historical generator scripts merely by importing them. Many
are one-shot experiment producers with original absolute paths and write targets.
Use documented entrypoints with fresh output directories and inspect their inputs.


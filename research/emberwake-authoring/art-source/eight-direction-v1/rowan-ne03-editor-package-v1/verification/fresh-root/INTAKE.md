# Intake and portable replay

The candidate03 PNG must have SHA256 `940fa7375b4a0df0e5734e78e789e265879c2e9194527601f878a4a8bc4cd09d`.

The final toolkit project hash must be `b8c0df192ea899a64da94c7ba764cb35aa8f83ac79fdcb9a97c30d6e2c118953`.

The selected input bank is frozen in `inputs/current/`, and the exact desired eight final PNGs are in `inputs/expected-final/`. Only03 differs. `INPUTS.json` retains the actual selected v10 config and49 ordered local input/dependency hashes. Original absolute paths are provenance only; replay reads the retained relative copies and requires no canonical checkout, original artifact folder, model or network.

Requirements: Python3 with NumPy/Pillow and the real `libresprite` binary on PATH. A different binary may be supplied with `--libresprite /absolute/path`. Run from any directory; the output path must be fresh and absolute:

```bash
python3 -B /home/astra/artifacts/emberwake-rowan-ne03-editor-package-v1/scripts/replay.py \
  --output /tmp/emberwake-rowan-ne03-fresh-replay
```

The command copies only inputs, retained source, local scripts/toolkit and contracts into that fresh root. It reconstructs source pixels, performs both guarded transactions and all negative/undo/redo checks, exports the project, then invokes actual LibreSprite save/reopen/render/reimport. `FRESH-ROOT-REPLAY.json` records the actual commands and result. A mismatch stops; no pixels are fitted or repainted to pass.

For inspection:

- Editable toolkit project: `projects/final.json`.
- Actual native output: `exchange/tool-reopened.aseprite`.
- Required sidecar on reimport: `exchange/rowan-ne-final.aseprite.sprite-lab.json`.
- Authoritative timing/pivots: `exchange/RATIONAL-CLOCK.json`.
- Native command logs and raw sheets: `exchange/tool-saved.*`, `exchange/tool-reopened.*`.
- Source parts/maps/owners and four-pixel donor witnesses: `retained-source/`.
- Mechanical receipts: `verification/`.

For a tool-resaved file with another name, use the explicit original sidecar:

```bash
python3 -B scripts/sprite_edit.py ase-import exchange/tool-reopened.aseprite \
  /tmp/rowan-ne03-reimported.json \
  --sidecar exchange/rowan-ne-final.aseprite.sprite-lab.json
```

This intake authorizes review of the package only. It carries no user playback approval,8/10 motion claim, speed/timing change or canonical integration instruction.

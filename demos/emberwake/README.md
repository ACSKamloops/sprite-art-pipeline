# Emberwake: The Hollow Bell

An original small top-down action adventure in Godot 4.7.2. Carry Bellwether's ember through three forest ward encounters, face the Rootbound Warden, wake the bell and return home. The complete quest has an ending, post-game exploration, checkpoint saves and retry. Chrono Trigger informed the world-view brief; this is real-time combat with original art and setting.

**Play publicly:** https://emberwake-hollow-bell.astraithious.chatgpt.site

Public access requires no login. Desktop keyboard and mouse. The public build passed the same 21 ordinary-input checks and 8 cast samples; see [publication evidence](docs/PUBLICATION.md).

**Play locally:** http://localhost:8896/index.html

The original single-character demo received **8.0/10 for the compact demo**, with moderate confidence. The expansion adds selectable **Rowan, Lyra and Brann**, visible frost nova and hand-aligned firebolts. The fresh art review rated Lyra 8.2 and Brann 8.1; the stricter follow-up rated 7.8/7.6. Both judgments and their limits are retained in the [quality record](docs/QUALITY.md). Small enemy HP bars can still cross the hero during close combat.

**Editor/native:** `godot --path /home/astra/projects/emberwake-demo`

The exported game runs locally without model accounts, credentials, network APIs or generation charges. Serve `web/` over HTTP; opening its HTML as a `file://` document will not load WebAssembly correctly.

If the local server has stopped, run `./play.sh` from this folder and leave that terminal open. Set `EMBERWAKE_PORT` to choose a different port.

| Input | Action |
|---|---|
| WASD / arrows | Move; movement sets facing |
| J / left mouse | Unarmed strike |
| K / right mouse / 1 | Firebolt, 10 mana |
| L / Q / 2 | Frost nova, 24 mana; slows nearby foes |
| Space | Dodge through danger |
| E / Enter | Talk, kindle, rest, continue dialogue |
| H | Healing flask; two charges |
| Esc / P | Pause, field journal, map and audio controls |

This build is intended for a desktop keyboard and mouse. The journal, dialogue and menus also have real clickable buttons. Four cardinal hero facings cover idle, movement, strike, casting, hurt and dodge. Fire and frost share the body casting clip and have independent effects/gameplay clocks. Held equipment is not painted into the hero, leaving that route open for modular equipment later.

Use **Choose emberkeeper** on the title screen for a new journey. **Continue** restores the saved character. The paused journal offers **Change emberkeeper** in a quiet clearing; it preserves health, mana, location and progress. All three characters share abilities and stats. Each has 24 body clips across four directions; Brann's symmetric west bank is mirrored from east.

Speak with Aster at the village lantern. The journal shows the three wards and shrine. Defeat each ward's guardians, then press E at its stone. A lit ward refills health, mana and both flasks and becomes a checkpoint. The shrine opens after all three wards. Watch the inked amber telegraphs, dodge the Warden's attacks, then approach the bronze bell. Wards survive death. After the ending, Aster has a return conversation and the completed objective clears.

## Rebuild and checks

```bash
cd /home/astra/projects/emberwake-demo
python3 tests/run_checks.py
LP_NUM_THREADS=4 godot --headless --path "$PWD" --editor --import
LP_NUM_THREADS=4 godot --headless --path "$PWD" --export-release Web "$PWD/web/index.html"
python3 -m http.server 8896 --directory web
```

The installed export preset uses the matching 4.7.2 nonthreaded Web templates. Native export templates are not required to run the source project in the editor. The build uses Compatibility rendering/WebGL2 and requires no cross-origin isolation headers.

`tests/run_checks.py` verifies 400 behavioral/resource assertions and 378 route collision samples. It rejects GDScript errors even when Godot exits zero. The tests use a separate test-save file. The optional renderer probe passes 109 assertions across all three production characters, including frost depth and all 12 hand sockets. An ordinary-input browser pass separately checks 21 assertions and 8 cast samples. These tests do not assign art scores. [Character/spell methods and exact evidence boundaries](docs/CHARACTERS-AND-SPELLS.md) distinguish selector fixtures, production rendering and real browser play.

Optional art rebaking uses Python 3.14.4 and the versions in `requirements-art.txt`; audio composition also uses system ffmpeg 8.0.1. These dependencies are unnecessary for browser play. Rebuild commands consume retained images and make no model requests.

## Sources and editing

- [Art pipeline and exact coverage](docs/ART-PIPELINE.md).
- [Selectable-character production and spell repair](docs/CHARACTERS-AND-SPELLS.md).
- [Game structure and extension points](docs/ARCHITECTURE.md).
- Runtime sprites: `assets/hero/`, `assets/characters/catalog.json`, `assets/characters/{lyra,brann}/`, `assets/enemies/poses/`.
- Generated world/effect art and original synthesized music: `assets/world/`, `assets/effects/`, `assets/audio/`, `assets/sfx/`.
- Complete generation requests, raw returns, references, masks, maps and rejected attempts: `art-source/`.

PNG artwork came from the built-in OpenAI ImageGen tool and recorded compositing/editing. No new H3 calls, local generative model or 3D character model was used. The previously accepted H3 walk supplied eight retained pose-guide images for a new ImageGen side walk; its painted frames are not the new game's walking artwork. Generation is stochastic. Rebaking the retained pixels is deterministic, with all five selected hero artifact hashes reproduced in a fresh output directory (`docs/evidence/rebake-verification.json`).

The new banks rebuild offline with `python3 scripts/bake_characters.py --output <fresh-directory>`. Two independent fresh bakes reproduce all 14 selected files exactly; all 13 manual-refinement PNGs also replay byte for byte. Original 128 cels remain stored alongside appended selected refinements, source-coordinate maps and literal edit journals. See `docs/evidence/character-expansion/rebake-verification.json` and `manual-replay.json`.

The user's previous approved walk/jab project remains separate and unmodified at `/home/astra/projects/rpg-hero-animation`. Do not rerun its frozen authoring jobs while working on this game.

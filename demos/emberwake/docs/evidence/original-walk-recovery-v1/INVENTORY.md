# Original baseline provenance inventory

There are several distinct, recoverable baselines. **The public game has four painted walk views; installed registration v6 has eight walk tables.** The public cardinal clips remain pixel-identical inside the installed atlas, but the installed bank adds diagonals. “Original” must not silently select one of these meanings.

This was read-only source/history/evidence inspection. No art scores, server starts, exports, rebuilds, PCK extraction, historical-blob file extraction, asset edits, credentials or broad log searches occurred. PNG comparison was in memory only. The earlier frozen cold review was not changed.

## Public game: exact existing source copies

The verified local deployed payload is `/home/astra/projects/emberwake-public-site/dist/index.pck`, **12,245,640 bytes**, SHA256 `382a06f7aa84d9532b5a4c1f3c901a004128161afabe30cb71a82ac97b8ed2ce`. `/home/astra/projects/emberwake-demo/output/web-characters-v6/index.pck` is byte-identical. The public checkout's SOURCE.json names canonical commit `2a80f53c30953019f98333922a32ff8ae38f49d9` and runtime commit `1dbfb0554151ffed2780ed180c700dd97f17ca64`. All three historical atlas/manifest pairs match across those commits.

The deployment checkout is commit `797c3f1c35263c68269c69fb101998868cc055ad`. Retained publication evidence records successful public deployment on 2026-10-16; retained browser evidence records HTTP200 and the same PCK hash. The live website was not rechecked in this inventory. Packed imported textures were not decoded, so this is source/payload provenance, not a new GPU texture-equality assertion.

**No PCK unpacking or Git extraction is needed to build a public-source viewer.** All six existing files below match their historical public Git blobs and BASELINE.json hashes exactly:

| Actor | Existing frozen public-source directory | Historical Git paths at 2a80f53 |
|---|---|---|
| Rowan | `/home/astra/projects/emberwake-demo/art-source/eight-direction-v1/baseline/rowan/` | `assets/hero/atlas.png`, `assets/hero/animations.json` |
| Lyra | `/home/astra/projects/emberwake-demo/art-source/eight-direction-v1/baseline/lyra/` | `assets/characters/lyra/atlas.png`, `assets/characters/lyra/animations.json` |
| Brann | `/home/astra/projects/emberwake-demo/art-source/eight-direction-v1/baseline/brann/` | `assets/characters/brann/atlas.png`, `assets/characters/brann/animations.json` |

Each directory contains `atlas.png` and `animations.json`. The baseline ledger was first committed at `118e535229a00be19449ff295266f243034ca6f9`. Lyra and Brann also have exact public atlas/manifest copies in `art-source/characters-v2/bake-v6/{lyra,brann}/`.

All public banks use 128×128 cells, **8 columns**, pivot `[64,112]`, draw scale0.66 and 24 clips: idle, walk, attack, cast, hurt and dodge in **south/east/north/west**. Each public walk is eight exposures ×56.25ms =450ms. Exact frame arrays, every clip duration and source-lineage paths are in INVENTORY.json.

| Actor | Public atlas SHA256 | Public manifest SHA256 |
|---|---|---|
| rowan | `1dc65d4eb637ef35e5be3d3345b1a56d18af6ce041f7ce000c924848d569cb68` | `f295492d3339af898ee49c117b753ac1f475e78e0022cc943feaecf46510965d` |
| lyra | `f177d69482bac4c4a6c1c171e5679e5da1c1c45fa11fbf6b56a0fbf4f5fae901` | `70b8de14097ecb82ba0ff9aec2d92e1c965c67f8010fbeffa82b50236658123f` |
| brann | `69dd1bf4061ee0f7c740bb6f2f9ec44166f13ca8d651293aa5e23b003d6451f4` | `2c9d6d1212eba569c8d705851a129180b633aaeccf2eac643c30acb964f35921` |

## Installed registration v6: distinct eight-view authority

Current canonical resources are `assets/hero/{atlas.png,animations.json}` for Rowan and `assets/characters/{lyra,brann}/{atlas.png,animations.json}` for the others. They match their `66bc89e052adffa2c19f34d2b4e470e21fc8a83b` versions. Their manifests use **16 columns** and 48 clips per actor, including all eight walk directions. Every walk remains eight ×56.25ms =450ms. Preserve each bank's own column count when decoding; using8columns on the installed atlas misidentifies cells.

The declared source is `art-source/eight-direction-v1/registration-v6-all-charge-tracks.json`, SHA256 `dcf870899c2e72a9fbb93628e700cfb5cd7bb664bcdcdafde358cfcaed90fc81`. Its note states walks remain provisional and no8motion acceptance. Its six retained diagonal raw-source files all match their declared hashes. Rowan and Lyra raw inputs are under `art-source/eight-direction-v1/raw/`; Brann's are under `art-source/eight-direction-v1/brann-source/raw/`. Exact paths and hashes are in JSON. The manifest discloses conditional NW/SW reflection around pivotX64 with+1px correction.

I compared all public cardinal clip entries and selected RGBA exposures to installed counterparts using each atlas's own column count: **Rowan116, Lyra128, Brann128 exposures; zero pixel or clip-metadata differences.** This establishes preserved cardinals, not that the public bank has diagonal clips. Installed diagonal art must be shown under its own label.

**Naming collision:** `characters-v2/bake-v6` means the public four-view character bake; `eight-direction-v1/registration-v6` means the later installed eight-view configuration. Documentation that calls the old four-view export “current” is historically scoped and must not override the inspected installed manifests.

## Earlier originals that remain separate

- **First retained painted game hero:** commit `c60f67fbd72811f1baebb79f78dda7ebf8ccb762`, 2026-10-15 23:32:51−07:00, `assets/hero/{atlas.png,animations.json}`. Its south/north walks contain six exposures ×75ms, while east/west contain eight ×56.25ms; every cycle is450ms. This is earlier game art, not a demonstrated approved baseline. Its source hashes and clip metadata are retained in JSON. No files were extracted.
- **Repaired single-hero game:** Rowan's public atlas/manifest already appear at `41c6a1c`. Retained `output/web-v3/index.pck` and `output/web-before-character-expansion/index.pck` both hash to `2b93baf201f84fea1c64597ad4cb485cc1617e75740148956732fcccd27c7213`. These are distinct from the later three-character public PCK.
- **Earlier installed diagonals:** current canonical registration-v6 resources are a recoverable eight-view baseline, separate from isolated later preview/art experiments. Their existence does not establish user approval of diagonal motion.
- **Previous approved H3 walk/jab:** README.md:61 and :65 locate `/home/astra/projects/rpg-hero-animation` and explicitly distinguish its previously accepted walk from the game's new painted art. Eight retained poses served as guides for a new ImageGen side walk; the older painted walk frames are not this game's walk artwork. That separate project was not inspected. Exact approved H3 assets/timing and a direct approval transcript are unverified here.

## Approval and extraction limits

Canonical AGENTS.md records authorization for the public test release on2026-10-16, and PUBLICATION.md/evidence records deployment. That is recorded release authorization, not a newly recovered user approval of each animation. The README records approval of the separate earlier walk/jab project, but this inventory does not establish its exact approved files. No direct user acceptance of eight-view motion was found in this bounded trace. Critic/replay/browser evidence is not substituted for that approval.

For the viewer, use the already verified frozen public directories and separately label current installed8. If the user later identifies “original” as first-game art or the separate H3 project, recover that specific authority in a separate bounded step. Do not infer the selection from the user's broad preference.

PCK extraction is unnecessary for the public-source viewer. If packed/imported-texture identity becomes necessary later, preserve the verified PCK read-only and use a separately validated PCK/imported-texture reader with a fresh artifact output. No extractor route was executed or newly validated here. Exact source paths and read-only Git blob identities are already sufficient for the nominated source comparison.

Inventory is point-in-time at canonical HEAD `68e302beb18973c4c6d5418de1e27060c6e40f11`. Existing unrelated dirty work was left untouched. The JSON contains exact authority paths, hashes, history, walk tables, clip durations and evidence fingerprints.

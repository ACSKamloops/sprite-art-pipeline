# Spell presentation repair

The old frost effect used `z_index = -1`. The world paints its opaque baked ground at zero, so that effect disappeared beneath the map. Frost now remains at zero inside the existing y-sorted actor branch. Painted ice, its expanding ring and a brief hand charge/release are visible; foreground actors still sort over it. Gameplay radius, damage, slow, costs, cooldowns and the 0.24-second release are unchanged.

Firebolt keeps its physical swept trajectory on the feet plane and stores a separate full `visual_offset`. The render origin is `(native_hand - native_pivot) * draw_scale` from the selected painted release cel. The physical projectile starts at the feet, so moving the glove beyond a nearby wall cannot skip that wall. Painted impact placement follows the visual trajectory. Existing actor-owned hit effects remain single and rejected damage is not decorated as a successful hit.

`hero.set_character(id) -> bool` reads `res://assets/characters/catalog.json`, accepting either an array or `{characters: [...]}`. Each entry has `id`, `atlas`, `manifest` and optional UI fields. It validates all 24 action/view clips and atlas frame bounds before changing the working character. Unknown IDs preserve the existing selection; without a catalog Rowan loads its original atlas. Before `_ready`, a valid selection is retained for startup. Switching preserves health, mana, cooldowns, action state and pending hits. `character_id` and `get_debug_state().character` expose the live identity.

The optional manifest `cast_hand` maps south/east/north/west to native `[x,y]` glove coordinates. Optional `cast_release_index` is a zero-based index into each cast clip, either one integer or a facing dictionary. Art timing maps this cel to the unchanged gameplay release at 0.24 seconds; renderer/physics scheduling cannot pick a different launch pose. New characters need measured sockets; the Rowan defaults are not evidence for their anatomy.

Rowan measurements, from actual cast release index 3:

| Facing | Atlas cel | Native hand | Native pivot | Draw scale |
| --- | ---: | --- | --- | ---: |
| South | 15 | [99,72] | [64,112] | 0.66 |
| East | 39 | [102,57] | [64,112] | 0.66 |
| North | 63 | [93,49] | [64,112] | 0.66 |
| West | 87 | [24,60] | [64,112] | 0.66 |

The selected south and north glove is on screen right. East/west use their extended forward glove. Effects are drawn separately from the painted bodies. No model calls, new art, balance changes or game publishing were needed for this repair.

## Verification performed in this worktree

All commands below used Godot 4.7.2 with `LP_NUM_THREADS=4 OMP_NUM_THREADS=4`.

```
godot --headless --path . --script tests/systems_smoke.gd
godot --headless --path . --script tests/pause_smoke.gd -- --test-mode
godot --headless --path . --script tests/combat_readability.gd -- --test-mode
godot --headless --path . --script tests/spells_v2.gd
LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a godot --path . --rendering-method gl_compatibility --rendering-driver opengl3 --audio-driver Dummy --script tests/spells_v2.gd -- --spells-render
```

Existing systems 114, pause 26 and combat-readability 30 assertions passed without script/runtime errors. The new logic test passed 35 assertions with only Rowan present. The final render run passed 48 assertions. Counts expand automatically when more catalog entries are integrated; those new characters were **not present or certified by this worktree run**.

Real Mesa llvmpipe/OpenGL rendering reproduced the old failure: the negative-depth frost image was byte-identical to the opaque-ground baseline. At corrected depth, 40,857 pixels changed, including 39,432 ice-blue pixels; a foreground marker remained above the effect. This checks actual drawn pixels, not just a `z_index` property.

The rendered four-facing launch captures were inspected: bright projectile cores meet the release glove in each view. The pixel regression also requires actual changed warm pixels around each authored glove. These are frozen release frames; they do not certify the complete new character bank, normal-speed animation, every game surface, or browser output. Root integration should rerun both the complete behavioral suite and this rendering probe after installing all character atlases/manifests, then inspect live casts in the actual exported game.

The two-pixel near-wall case deliberately places the extended hand beyond a wall while the physical launch remains behind it. The target stays undamaged and the projectile is consumed. Pending cast, released visual lifetime, and existing mid-flight projectile state all remain paused through simulation boundaries.

`spell-checks.json` is the final rendering-run receipt. PNGs retain the blank baseline, old failure, visible fixed frost, foreground-depth check, plain four-way release poses, and four-way hand-origin fireball presentation. These checks establish behavior and visibility; they do not assign an art or game-quality score.


## Integrated three-character expansion

The later canonical project at `/home/astra/projects/emberwake-demo` integrates Rowan, Lyra and Brann, with the selected new banks frozen at `art-source/characters-v2/bake-v6/`. The full suite passes 400 assertions plus 378 physical route samples: 280 baseline, 40 selector-fixture assertions and 80 production spell/catalog assertions. The selector fixture still uses a stub and does not certify new artwork.

The real-render probe separately passes 109 assertions using all three production banks. All 12 plain/fire release-hand images were inspected, together with the invisible negative-control frost, corrected visible ice and foreground-depth marker. New character cast release index3 is atlas cel19/47/75/103 in south/east/north/west respectively.

| Character | South hand | East hand | North hand | West hand |
|---|---|---|---|---|
| Lyra | [99,72] | [95,58] | [94,57] | [34,58] |
| Brann | [101,72] | [96,52] | [96, 40] | [32,52] |

`spell-logic-checks.json` now retains the headless80-assertion run separately; `spell-checks.json` remains the rendered109-assertion run and is not overwritten by a later headless test. The display driver reports the expected unsupported software V-sync warning; the probe has no script/runtime error. Rendering here uses Mesa llvmpipe, not a device performance benchmark.

The initial35/48 counts above describe the isolated pre-integration worktree only. The current JSON receipts bind the integrated run; art reviews and ordinary-input Web evidence remain separate under `docs/evidence/character-expansion/`.

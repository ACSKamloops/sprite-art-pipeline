# Mana evidence and limits

Local USA SHA256: 4c15013131351e694e05f22e38bb1b3e4031dedac77ec75abecebe8520d82d5f. Evidence currently lives under /home/astra/artifacts/rea-som-animation-2026-10-07; these paths locate the case, not portable prerequisites.

The initial published viewer uses 216 selected clips/792 frames: idle/walk and two normal far-attack rows. Passing browser tests didn't establish complete native coverage. New player inventory records 1,119 words (153 generic,960 weapon-family,six utility-tail), 437 unique roots. Generic allocation bounds use the next config-referenced table, not a stored legal count. Adjacent config tables can include transformed player bodies and need separate scope.

The full BODY-only nominal catalog retains 4,452 bindings/51,924 pose instances/1,662 atlases. Bindings aren't unique animations. Conditional waits, movement, palettes, attachments/effects and dynamic action reselection are omitted; clips play one pass and don't claim native loops.

Demonstrated corrections:

- Equipped weapon image selects shared D1 mappings via D0:FFD0. Actor-specific mapping guesses caused detached weapons despite manifest consistency. D2 body tables are actor-specific.
- Body/weapon share render origin; ground and render pivots differ.
- Opcode89 removal stops parsing; reading adjacent bytes added false poses.
- F1 uses one return slot with overwrites. F9's effective length is three; AB..AF are movement dividers.
- Separate geometry, tiles and palette comparison. A mismatching palette isn't automatically DMA latency.
- Palette cycling has timers independent of pose; baseline weapon colors remain incomplete.
- Godot integer stepping passed while browser JSON float stepping failed.

Near/charged attack selection, running, casting initialization and qualified event poses now have source evidence. Some damage/death labels and projectile/magic lifetimes remain unresolved. Don't label unfamiliar poses solely by appearance.

/home/astra/projects/sprite-animation-pipeline has a Godot fixture, queue/artifact regressions and review evidence. Hit events are authored tests. Source discovery, export consistency, runtime fidelity and visual approval remain separate gates.

## Expanded native and authoring checkpoint

The earlier unresolved items above describe the initial checkpoint. Subsequent evidence covers all eight weapon families at actual charge 1 and 2, native near-target selection, menu-selected casting, actual enemy damage/death, native Cup of Wishes revival, and all nine transformed configurations. Setup changes are logged separately from native input; an injected initial state is not proof of natural progression through the game.

Transformed export v4 contains 2,044 nominal bindings/5,888 timed poses, plus 138 observed windows/674 frames/4,890 actual video ticks. All 817 initial WRAM-versus-presented mismatches are classified: 815 one-video-tick OBJ upload delays and two configuration-copy transitions. Fifteen actual presented transformed routes contain 4,980 frames and pass 101,937 independent raw OAM/VRAM/CGRAM checks. Unknown allocated rows retain IDs; their normal gameplay reachability is not established.

The state-aware interpreter v4 explicitly suspends for external state and resumes native FF continuation; 59 contract checks cover meaningful waits/reselection/completion conditions. This interpreter is not a replacement for the game's complete combat/status/effect helpers. The Godot transformed inspector independently passes 41,556 resource checks plus 280 controls and nine live cases.

The indexed OBJ renderer keeps bodies, attachments, moving objects and independent palettes on actual video ticks. Its first ten routes pass exact comparisons for all 2,827 actual Godot-rendered frames. Expanded route indexes and audit reports live in /home/astra/projects/som-native-effect-renderer. Pure OBJ output excludes backgrounds, color math, scanline evaluation limits and priority rotation; unproven object ownership remains unassigned. Palette helper v2 passes 700 native-state comparisons including rotation modes.

/home/astra/projects/sprite-animation-authoring-comparison contains real AI key-pose generation and repair, 11-part deterministic Godot rigging, the same poses rendered through packed editable Blender image planes, and LibreSprite timing edits/save/reopen. Six clips/72 entries import and play in Godot. Forty-eight sprite-editor frame edits/reopens preserve visible RGBA exactly. Blender/Godot foreground mask overlap is approximately 0.99999 for all 24 matching poses; this is a 2D cutout route, not a reconstructed 3D character. A full 3D route still needs a model and rig.

An independent visual reviewer rejected the AI walk for repeating the same contact leg and accepted the other five clips for prototype use. Joint seams and rotated pixel clusters need cleanup before final art approval. Three real event/preview/restart defects were repaired and independently retested. The queue retains this distinction: one revision requested and five at visual review, with no blanket production-art approval.

Native runtime v2 records 139 attempted routes/136,378 video ticks/43,606 complete rendering-surface captures, retaining failed exploratory cases. All spell IDs 0–41 have native initialization evidence, including a Revivify retry on actual enemy-produced death; spell level/resistance/status/cancellation branches are not exhaustive. Bow/boomerang/javelin constructor/flight/return/terminal hooks at actual charge 0/3/6 prove one/two/three concurrent instances and eventual inactive buffers. The runtime index and raw endpoints distinguish initialization, presented frames and semantic termination. The expanded 43-route shader checkpoint passes all 11,347 actual Godot frames; later successful full-catalog routes and coverage are recorded in the renderer's final index/audit.

The final native player exposes 85 successful routes/28,123 frames, covering all 42 spell IDs plus charges, transformed inputs and revival. Consolidated GPU evidence covers 19,122 fresh frames and 9,001 retained frames only where full route SHA256 equals the previous validated checkpoint. All indexed frames have zero pixel differences; 685 actual browser checks pass. Preserve this union proof and the original reports rather than implying that unchanged frames were rendered twice. This establishes captured OBJ fidelity, not complete BG/color-math rendering or all spell-level/gameplay branches.

Final independent scalar audit also reconstructs 31,672 current and preserved native frames/562,838 visible objects, passing 1,846,874 assertions with no issues. Preserve its scope: larger historical evidence coverage is not the public index's animation count. A separate fresh non-extraction art forward test imports two cutout clips/24 frames and passes 50 playback/driver checks; its current review blocks production-art approval and a subset invalidates the original binding.

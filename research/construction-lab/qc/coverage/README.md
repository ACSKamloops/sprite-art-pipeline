# Animation family coverage and single-sprite authoring contract

This covers the animation kinds actually found in this **player-focused extraction and captured native effect routes**. It is not an inventory of every enemy, boss, NPC gesture, chest, terrain or background animation in the game. Unknown generic action rows remain unknown.

The evidence contains 4,452 normal nominal bindings / 51,924 body frames; 2,044 transformed nominal bindings; and 85 captured native routes / 28,123 presented video ticks. **None of these counts is new authored artwork.** The new layered pilot has only 2 clips (walk and punch), 24 frames and 11 layers; **zero clips have production art approval**. Both request visual refinement.

Current input fingerprint: `15cb4125fe35702d2d251539005f0170a72558796732c2ff238b9404c926fd98`. `matrix.json` holds the exact source-file/route hashes, sampled private capture references, recipes and QC requirements. Its 559 fresh checks audit count/hash/clock consistency; historical all-pixel/Godot reports remain separate proofs, not a claim this audit rendered every pixel again.

## Bound evidence stages

| Stage | What it establishes | What it does not establish |
|---|---|---|
| Decoded binding | Table/script/body/palette mapping and a nominal default-status path | Every allocated row is reachable, every wait has finite duration, or FF is a fixed native loop |
| Runtime observed | Exact native input/context/state and presented capture window | All actors, directions, levels, targets, interruption or cleanup branches |
| Exported/tested | Specific pixels, hashes, clocks, resource imports or actual tool exchange pass | Authored content or artistic quality |
| Newly authored | Explicit new editable character/effect frame assets exist | Native equivalence or finished art |
| Quality approved | Current hash-bound review approves the specified authored clips | Another revision or missing views |
| Engine behavior | Named parser, shader, palette, playback or state-component checks | A complete reconstructed RPG/combat system |

## Source-grounded families and how to build them from one sprite

One fused sprite can supply identity, visible material colors and one view. It cannot prove hidden joints, back/other views or replacement transformed characters. Build declared layers/anchors, draw additional key poses when the source is insufficient, preserve one render/ground frame, and use distinct effect instances/palette state rather than pretending every type is one body GIF.

### Idle / standing

**Identity:** `idle`; source_grounded.

**Source coverage:** decoded {"generic_row": 0, "bindings": 12}; observed {"hero_scenarios": "3heroes idle and natural standing traces", "not_all_event_idle_variants": true}; exported {"body_clips": 12, "normal_body_catalog": true}.

**Authoring:** Extract or draw one consistent grounded neutral key pose per required view. Separate body/equipment palettes and breathing or readiness cels; preserve explicit holds.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check ground/reference position, equipment attachment and breathe/readiness timing.

**Engine scope:** Normal SpriteFrames save/reload and selected playback tested; no full RPG idle dispatcher acceptance.

**Still missing:** No new idle artwork for three hero identities/four directions. Readiness/status-related alternate rows remain contextual.

### Walking

**Identity:** `walk`; source_grounded.

**Source coverage:** decoded {"generic_row": 1, "bindings": 12}; observed {"heroes": ["randi", "primm", "popoi"], "four_direction_inputs": true}; exported {"body_clips": 12, "native_right_control_frames": 30}.

**Authoring:** Starting from one sprite, split only visible body parts with declared anchors or draw contact/opposite-contact keys; construct passing/recoil poses. A single fused sprite does not reveal hidden limbs or back view. Keep stance feet fixed under declared root displacement.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check both support halves, actual raster soles, loop wrap, hip/knee seams, world contact and attachment.

**Engine scope:** Normal SpriteFrames playback tested; authoredpilot GPU layers and fixed stance soles verified.

**Still missing:** Only one right-facing authoredpilot walk with12frames; changes_requested for knee/material/weight. No complete new three-hero/four-direction walk library.

### Running inputs / running pose selection

**Identity:** `run`; source_grounded.

**Source coverage:** decoded {"candidate_generic_rows": [2], "nominal_only": true}; observed {"heroes": ["randi", "primm", "popoi"], "A_right_down_scenarios": true, "R_inputs_not_equated_to_run_success": true, "actual_capture_samples": [{"scenario": "popoi_run_a_right_down", "capture": "013891_a_right", "raw_action_word": "0x201", "script": "0x5cbc", "generic_table_rows": [2], "actual_direction": "down", "evidence": "run_sample/popoi_run_a_right_down/013891_a_right"}, {"scenario": "popoi_run_a_right_down", "capture": "013996_a_down", "raw_action_word": "0x101", "script": "0x5c72", "generic_table_rows": [1], "actual_direction": "down", "evidence": "run_sample/popoi_run_a_right_down/013996_a_down"}, {"scenario": "primm_run_a_right_down", "capture": "013891_a_right", "raw_action_word": "0x201", "script": "0x5cbc", "generic_table_rows": [2], "actual_direction": "down", "evidence": "run_sample/primm_run_a_right_down/013891_a_right"}, {"scenario": "primm_run_a_right_down", "capture": "013996_a_down", "raw_action_word": "0x101", "script": "0x5c72", "generic_table_rows": [1], "actual_direction": "down", "evidence": "run_sample/primm_run_a_right_down/013996_a_down"}, {"scenario": "randi_run_a_right_down", "capture": "013773_a_right", "raw_action_word": "0x102", "script": "0x5c88", "generic_table_rows": [1], "actual_direction": "right", "evidence": "run_sample/randi_run_a_right_down/013773_a_right"}, {"scenario": "randi_run_a_right_down", "capture": "013878_a_down", "raw_action_word": "0x202", "script": "0x5cda", "generic_table_rows": [2], "actual_direction": "right", "evidence": "run_sample/randi_run_a_right_down/013878_a_down"}], "observed_run_row2_directions": ["down", "right"], "input_label_is_not_actual_pose_direction": true}; exported {"nominal_body_rows": true}.

**Authoring:** Create a faster cycle with distinct stride length, lean and support durations from native reference, rather than only speeding up walk.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Compare run input to observed action/script, displacement, contacts, collision stops and transition back to walk.

**Engine scope:** Native scenario traces show poses; world movement/collision and authored running controller not fully tested.

**Still missing:** Up/left running not exhaustively observed. No newly authored running clip; do not alias walk.

### Glove equipment actions / basic and charged attacks

**Identity:** `weapon_glove`; source_grounded.

**Source coverage:** decoded {"family_index": 0, "allocated_rows": 40, "bindings": 480, "mapping": "D0FFD0+weapon image*2; actor-specific D2 body tables"}; observed {"basic_far": "3heroes\u00d74directions native scenarios", "near": "Not independently established for all actors/directions", "observed_charge_levels": [1, 2], "charge_actor": "randi", "site_routes": ["glove-charge-1", "glove-charge-2"]}; exported {"near_far_body_weapon_clips": 24, "ordinary_palette_only": true, "full_body_only_bindings": 480}.

**Authoring:** Construct grip, windup, extension/contact, follow-through and recovery keys specific to glove. Body and weapon share the native render center. Separate weapon cels, handedness and grip offsets; charge levels require distinct native sequence references, not faster copies.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check per-view grip/flips, body/equipment overlap, exact charge gate, script/pose clock, native cancellation and clean recovery. Do not infer hit windows from drawn weapon extension.

**Engine scope:** Native physical selection/movement observed in disclosed scenarios; indexedOBJ replay is not complete combat/charge dispatcher.

**Still missing:** No newly authored glove combat art. Charge levels4/5/7/8 and all charge actors/directions not fully runtime covered. 40allocated rows do not prove40reachable attacks or native loops.

### Sword equipment actions / basic and charged attacks

**Identity:** `weapon_sword`; source_grounded.

**Source coverage:** decoded {"family_index": 1, "allocated_rows": 40, "bindings": 480, "mapping": "D0FFD0+weapon image*2; actor-specific D2 body tables"}; observed {"basic_far": "3heroes\u00d74directions native scenarios", "near": "Sword near row1 with adjacent native-built Rabite only", "observed_charge_levels": [1, 2], "charge_actor": "randi", "site_routes": ["sword-charge-2", "sword-charge-1"]}; exported {"near_far_body_weapon_clips": 24, "ordinary_palette_only": true, "full_body_only_bindings": 480}.

**Authoring:** Construct grip, windup, extension/contact, follow-through and recovery keys specific to sword. Body and weapon share the native render center. Separate weapon cels, handedness and grip offsets; charge levels require distinct native sequence references, not faster copies.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check per-view grip/flips, body/equipment overlap, exact charge gate, script/pose clock, native cancellation and clean recovery. Do not infer hit windows from drawn weapon extension.

**Engine scope:** Native physical selection/movement observed in disclosed scenarios; indexedOBJ replay is not complete combat/charge dispatcher.

**Still missing:** No newly authored sword combat art. Charge levels4/5/7/8 and all charge actors/directions not fully runtime covered. 40allocated rows do not prove40reachable attacks or native loops.

### Axe equipment actions / basic and charged attacks

**Identity:** `weapon_axe`; source_grounded.

**Source coverage:** decoded {"family_index": 2, "allocated_rows": 40, "bindings": 480, "mapping": "D0FFD0+weapon image*2; actor-specific D2 body tables"}; observed {"basic_far": "3heroes\u00d74directions native scenarios", "near": "Not independently established for all actors/directions", "observed_charge_levels": [1, 2], "charge_actor": "randi", "site_routes": ["axe-charge-1", "axe-charge-2"]}; exported {"near_far_body_weapon_clips": 24, "ordinary_palette_only": true, "full_body_only_bindings": 480}.

**Authoring:** Construct grip, windup, extension/contact, follow-through and recovery keys specific to axe. Body and weapon share the native render center. Separate weapon cels, handedness and grip offsets; charge levels require distinct native sequence references, not faster copies.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check per-view grip/flips, body/equipment overlap, exact charge gate, script/pose clock, native cancellation and clean recovery. Do not infer hit windows from drawn weapon extension.

**Engine scope:** Native physical selection/movement observed in disclosed scenarios; indexedOBJ replay is not complete combat/charge dispatcher.

**Still missing:** No newly authored axe combat art. Charge levels4/5/7/8 and all charge actors/directions not fully runtime covered. 40allocated rows do not prove40reachable attacks or native loops.

### Spear equipment actions / basic and charged attacks

**Identity:** `weapon_spear`; source_grounded.

**Source coverage:** decoded {"family_index": 3, "allocated_rows": 40, "bindings": 480, "mapping": "D0FFD0+weapon image*2; actor-specific D2 body tables"}; observed {"basic_far": "3heroes\u00d74directions native scenarios", "near": "Not independently established for all actors/directions", "observed_charge_levels": [1, 2], "charge_actor": "randi", "site_routes": ["spear-charge-1", "spear-charge-2"]}; exported {"near_far_body_weapon_clips": 24, "ordinary_palette_only": true, "full_body_only_bindings": 480}.

**Authoring:** Construct grip, windup, extension/contact, follow-through and recovery keys specific to spear. Body and weapon share the native render center. Separate weapon cels, handedness and grip offsets; charge levels require distinct native sequence references, not faster copies.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check per-view grip/flips, body/equipment overlap, exact charge gate, script/pose clock, native cancellation and clean recovery. Do not infer hit windows from drawn weapon extension.

**Engine scope:** Native physical selection/movement observed in disclosed scenarios; indexedOBJ replay is not complete combat/charge dispatcher.

**Still missing:** No newly authored spear combat art. Charge levels4/5/7/8 and all charge actors/directions not fully runtime covered. 40allocated rows do not prove40reachable attacks or native loops.

### Whip equipment actions / basic and charged attacks

**Identity:** `weapon_whip`; source_grounded.

**Source coverage:** decoded {"family_index": 4, "allocated_rows": 40, "bindings": 480, "mapping": "D0FFD0+weapon image*2; actor-specific D2 body tables"}; observed {"basic_far": "3heroes\u00d74directions native scenarios", "near": "Not independently established for all actors/directions", "observed_charge_levels": [1, 2], "charge_actor": "randi", "site_routes": ["whip-charge-1", "whip-charge-2"]}; exported {"near_far_body_weapon_clips": 24, "ordinary_palette_only": true, "full_body_only_bindings": 480}.

**Authoring:** Construct grip, windup, extension/contact, follow-through and recovery keys specific to whip. Body and weapon share the native render center. Separate weapon cels, handedness and grip offsets; charge levels require distinct native sequence references, not faster copies.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check per-view grip/flips, body/equipment overlap, exact charge gate, script/pose clock, native cancellation and clean recovery. Do not infer hit windows from drawn weapon extension.

**Engine scope:** Native physical selection/movement observed in disclosed scenarios; indexedOBJ replay is not complete combat/charge dispatcher.

**Still missing:** No newly authored whip combat art. Charge levels4/5/7/8 and all charge actors/directions not fully runtime covered. 40allocated rows do not prove40reachable attacks or native loops.

### Bow equipment actions / basic and charged attacks

**Identity:** `weapon_bow`; source_grounded.

**Source coverage:** decoded {"family_index": 5, "allocated_rows": 40, "bindings": 480, "mapping": "D0FFD0+weapon image*2; actor-specific D2 body tables"}; observed {"basic_far": "3heroes\u00d74directions native scenarios", "near": "Not independently established for all actors/directions", "observed_charge_levels": [1, 2, 3, 6], "charge_actor": "randi", "site_routes": ["bow-charge-0", "bow-charge-1", "bow-charge-2", "bow-charge-3", "bow-charge-6"]}; exported {"near_far_body_weapon_clips": 24, "ordinary_palette_only": true, "full_body_only_bindings": 480}.

**Authoring:** Construct grip, windup, extension/contact, follow-through and recovery keys specific to bow. Body and weapon share the native render center. Separate weapon cels, handedness and grip offsets; charge levels require distinct native sequence references, not faster copies.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check per-view grip/flips, body/equipment overlap, exact charge gate, script/pose clock, native cancellation and clean recovery. Do not infer hit windows from drawn weapon extension.

**Engine scope:** Native physical selection/movement observed in disclosed scenarios; indexedOBJ replay is not complete combat/charge dispatcher.

**Still missing:** No newly authored bow combat art. Charge levels4/5/7/8 and all charge actors/directions not fully runtime covered. 40allocated rows do not prove40reachable attacks or native loops.

### Boomerang equipment actions / basic and charged attacks

**Identity:** `weapon_boomerang`; source_grounded.

**Source coverage:** decoded {"family_index": 6, "allocated_rows": 40, "bindings": 480, "mapping": "D0FFD0+weapon image*2; actor-specific D2 body tables"}; observed {"basic_far": "3heroes\u00d74directions native scenarios", "near": "Not independently established for all actors/directions", "observed_charge_levels": [1, 2, 3, 6], "charge_actor": "randi", "site_routes": ["boomerang-charge-0", "boomerang-charge-1", "boomerang-charge-2", "boomerang-charge-3", "boomerang-charge-6"]}; exported {"near_far_body_weapon_clips": 24, "ordinary_palette_only": true, "full_body_only_bindings": 480}.

**Authoring:** Construct grip, windup, extension/contact, follow-through and recovery keys specific to boomerang. Body and weapon share the native render center. Separate weapon cels, handedness and grip offsets; charge levels require distinct native sequence references, not faster copies.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check per-view grip/flips, body/equipment overlap, exact charge gate, script/pose clock, native cancellation and clean recovery. Do not infer hit windows from drawn weapon extension.

**Engine scope:** Native physical selection/movement observed in disclosed scenarios; indexedOBJ replay is not complete combat/charge dispatcher.

**Still missing:** No newly authored boomerang combat art. Charge levels4/5/7/8 and all charge actors/directions not fully runtime covered. 40allocated rows do not prove40reachable attacks or native loops.

### Javelin equipment actions / basic and charged attacks

**Identity:** `weapon_javelin`; source_grounded.

**Source coverage:** decoded {"family_index": 7, "allocated_rows": 40, "bindings": 480, "mapping": "D0FFD0+weapon image*2; actor-specific D2 body tables"}; observed {"basic_far": "3heroes\u00d74directions native scenarios", "near": "Not independently established for all actors/directions", "observed_charge_levels": [1, 2, 3, 6], "charge_actor": "randi", "site_routes": ["javelin-charge-0", "javelin-charge-1", "javelin-charge-2", "javelin-charge-3", "javelin-charge-6"]}; exported {"near_far_body_weapon_clips": 24, "ordinary_palette_only": true, "full_body_only_bindings": 480}.

**Authoring:** Construct grip, windup, extension/contact, follow-through and recovery keys specific to javelin. Body and weapon share the native render center. Separate weapon cels, handedness and grip offsets; charge levels require distinct native sequence references, not faster copies.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check per-view grip/flips, body/equipment overlap, exact charge gate, script/pose clock, native cancellation and clean recovery. Do not infer hit windows from drawn weapon extension.

**Engine scope:** Native physical selection/movement observed in disclosed scenarios; indexedOBJ replay is not complete combat/charge dispatcher.

**Still missing:** No newly authored javelin combat art. Charge levels4/5/7/8 and all charge actors/directions not fully runtime covered. 40allocated rows do not prove40reachable attacks or native loops.

### Bow projectiles

**Identity:** `projectile_bow`; source_grounded.

**Source coverage:** decoded {"native_constructor_update_terminal_hooks": true}; observed {"charge_thresholds": [0, 3, 6], "max_instances": [1, 2, 3], "end_inactive": true}; exported {"site_route_count": 5, "actual_presented_effects": true}.

**Authoring:** Keep actor launch pose separate from projectile/effect instances. Build per-instance motion/rotation/palette and lifetime; boomerang needs outward and returning travel plus reattachment, not a single actor atlas.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check native spawn tick, simultaneous instances, trajectory, wrap, return/catch or terminal condition, cleanup and no orphan effect.

**Engine scope:** Actual native instance spawn/update/terminal or return hooks and indexedOBJ shader playback verified.

**Still missing:** Only controlled Randi/fixed-direction threshold routes. New projectile/return art and authored instance-controller not implemented. PureOBJ excludesBG/color-math/scanline semantics.

### Returning boomerang

**Identity:** `projectile_boomerang`; source_grounded.

**Source coverage:** decoded {"native_constructor_update_terminal_hooks": true}; observed {"charge_thresholds": [0, 3, 6], "max_instances": [1, 2, 3], "end_inactive": true}; exported {"site_route_count": 5, "actual_presented_effects": true}.

**Authoring:** Keep actor launch pose separate from projectile/effect instances. Build per-instance motion/rotation/palette and lifetime; boomerang needs outward and returning travel plus reattachment, not a single actor atlas.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check native spawn tick, simultaneous instances, trajectory, wrap, return/catch or terminal condition, cleanup and no orphan effect.

**Engine scope:** Actual native instance spawn/update/terminal or return hooks and indexedOBJ shader playback verified.

**Still missing:** Only controlled Randi/fixed-direction threshold routes. New projectile/return art and authored instance-controller not implemented. PureOBJ excludesBG/color-math/scanline semantics.

### Javelin projectiles

**Identity:** `projectile_javelin`; source_grounded.

**Source coverage:** decoded {"native_constructor_update_terminal_hooks": true}; observed {"charge_thresholds": [0, 3, 6], "max_instances": [1, 2, 3], "end_inactive": true}; exported {"site_route_count": 5, "actual_presented_effects": true}.

**Authoring:** Keep actor launch pose separate from projectile/effect instances. Build per-instance motion/rotation/palette and lifetime; boomerang needs outward and returning travel plus reattachment, not a single actor atlas.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check native spawn tick, simultaneous instances, trajectory, wrap, return/catch or terminal condition, cleanup and no orphan effect.

**Engine scope:** Actual native instance spawn/update/terminal or return hooks and indexedOBJ shader playback verified.

**Still missing:** Only controlled Randi/fixed-direction threshold routes. New projectile/return art and authored instance-controller not implemented. PureOBJ excludesBG/color-math/scanline semantics.

### Casting and42 normal spell IDs

**Identity:** `spellcasting`; source_grounded.

**Source coverage:** decoded {"generic_table_caster_rows": "not labelled by static row alone", "normal_spell_ids": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]}; observed {"initial_grid": {"attempts": 42, "accepted": 41}, "supplemental_revivify_dead_target": true, "successful_distinct_ids": 42}; exported {"native_site_spell_routes": 42, "frames": 17682}.

**Authoring:** From one caster sprite, build cast anticipation, invocation and recovery per necessary view. Each spell ID needs its own effect asset/motion/palette/target contract; do not substitute one generic flash for42effects.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check menu/target legality, actualMP change, effect layer placement, spell-specific progression, cleanup, caster return and BG/color-math exclusions.

**Engine scope:** Menu-driven native casting/MP/effect initialization observed. Whole spell target/resist/level/pause rules remain partial.

**Still missing:** No42 newly authored spell-effects library. Not every spell level, targetclass/resist, cancel branch or4direction caster pose observed. Initial all-living Revivify rejection must not be mistaken for completed cast.

### Independent palette shimmer / phase and rotation

**Identity:** `palette`; source_grounded.

**Source coverage:** decoded {"CGRAM_buffer_pipeline": true}; observed {"native_model_cases": 700, "phase_cases": 400, "bit20_rotation_cases": 300}; exported {"native85_routes_use_actual_CGRAM": true, "normal_static_attack_export": "baseline palette excludes shimmer"}.

**Authoring:** Keep indexed colors and material masks independent of pose frames. Build explicit palette-state timers or color-effect layers; do not bake one palette phase into everypose.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check samepose at differentvideo ticks, exactpalettephase/rotation, five/fifteen-word bounds and invalidranges.

**Engine scope:** Standalone native palette helper/model and indexedGPU palette lookup tested; supported ranges explicitly bounded.

**Still missing:** No newly authored palette transitions/material-region styling. Static ordinaryweapon clips do not model independent native shimmer.

### Status-conditioned pose and waits

**Identity:** `status`; source_grounded.

**Source coverage:** decoded {"FE_FC_FD_FF_control": true}; observed {"staged_status_bits_per_hero": {"randi": 16, "primm": 16, "popoi": 16}, "prone_status_0010": "observed script5EEC/generic55/56", "barrel_status_0400": "observed script5D22/generic39/40"}; exported {"nominal_rows": "conditional wait assumptions retained", "actual_source_waits": true}.

**Authoring:** Make status clips depend on authoritative state; add prone/barrel-specific art only from provenidentity/reference. A conditional wait needs a resumable state gate, not guessed finiteGIF timing.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check E041override, single-slotcall/return, FE/FC/FDpredicate holds, FFdynamicreselection, interrupts and input gates.

**Engine scope:** RuntimecontextE041/E05D/E060/E190 preserved; parserVM/conditionalcompletion component tested separately from fullRPG.

**Still missing:** Many statussemantic names unknown; staged bits not natural gameplay acquisition. No newstatusposeart or complete authoredstatusdispatcher.

### Observed transformed player configurations

**Identity:** `transformed`; source_grounded.

**Source coverage:** decoded {"config_ids": ["E4", "EC", "EE", "F0", "F1", "F2", "F6", "F7", "F8"], "nominal_bindings": 2044}; observed {"hero_status_input_routes": 15, "bits": [5, 6, 9, 12, 15]}; exported {"native85_transformed_routes": 15, "presented_video_frames": 4980, "nominal_frames": 5888}.

**Authoring:** A transformed character needs replacement silhouette/graphics/config and its gated move/attack poses; cannot repaint normalhero cels and call it equivalent. Use config-specific palettes/bodytables and observedlegal action tables.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check actualconfig transitions, perconfiggfx/bodytable/mapping, preparedspecial2row37C0 arithmetic, gating, one-video presentation lag, restoration.

**Engine scope:** Native configuration/gfx preparation and direction/B/run gates observed;9config resources roundtrip proven separately.

**Still missing:** Allocated nominalrows exceed reached gameplaypaths. No newly authored transformedcharacters/configsprite libraries. 815ordinaryone-tickdelays+2configurationcopybeforebodyassembly transitions must preserveactualOBJpresentation.

### Native damage reaction/recovery

**Identity:** `damage`; source_grounded.

**Source coverage:** decoded {"script_context": "Native source timelines identify reaction/conditionalwait/config restore; static rownamealone insufficient"}; observed {"routes": ["randi-native-damage-recovery"], "natural_rule_context": "ActualRabitehits reduceHP; ghost/death bridge inpartyroute; actualmenuCupofWishes/RevivifyrestorestatusandHP"}; exported {"public_native_routes": 1}.

**Authoring:** Draw distinct reaction, collapse/dead and revival/recovery poses using actuallifecycle references. Reuse character identity/pivots but keep conditions/transitions separate from attack animation.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check HPpositive→zero, conditionalhold, delayedE4/status8000, actualrevival target/MPoritemchange, normalconfig restoration.

**Engine scope:** Actual HP/status lifecycle transitions observed; finite publicclips may cover only reaction subsets.

**Still missing:** No newly authored damage/death/revival animations. Publiclethal120ticks is a lethalreaction excerpt, not the complete bridge or proof of finisheddeathclip. Not allhero/weapon/directioninterrupt branches observed.

### Lethal reaction / dead configuration transition

**Identity:** `lethal`; source_grounded.

**Source coverage:** decoded {"script_context": "Native source timelines identify reaction/conditionalwait/config restore; static rownamealone insufficient"}; observed {"routes": ["randi-native-lethal-reaction", "randi_transform_bit15_inputs"], "natural_rule_context": "ActualRabitehits reduceHP; ghost/death bridge inpartyroute; actualmenuCupofWishes/RevivifyrestorestatusandHP", "bridge_setup": "ControlledpositiveHP1partyfixture, actualenemyhit and later native8000/E4; notthe unchangedHP50route."}; exported {"public_native_routes": 2}.

**Authoring:** Draw distinct reaction, collapse/dead and revival/recovery poses using actuallifecycle references. Reuse character identity/pivots but keep conditions/transitions separate from attack animation.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check HPpositive→zero, conditionalhold, delayedE4/status8000, actualrevival target/MPoritemchange, normalconfig restoration.

**Engine scope:** Actual HP/status lifecycle transitions observed; finite publicclips may cover only reaction subsets.

**Still missing:** No newly authored damage/death/revival animations. Publiclethal120ticks is a lethalreaction excerpt, not the complete bridge or proof of finisheddeathclip. Not allhero/weapon/directioninterrupt branches observed.

### Revival item/spell and restoration

**Identity:** `revival`; source_grounded.

**Source coverage:** decoded {"script_context": "Native source timelines identify reaction/conditionalwait/config restore; static rownamealone insufficient"}; observed {"routes": ["cup-of-wishes-revive", "spell-primm-21-revivify-dead-target"], "natural_rule_context": "ActualRabitehits reduceHP; ghost/death bridge inpartyroute; actualmenuCupofWishes/RevivifyrestorestatusandHP", "item_restoration": "ActualHP0\u219250, followed by newnativeenemy damage to46 before captureend; finalHP alone is notrevivalfailure."}; exported {"public_native_routes": 2}.

**Authoring:** Draw distinct reaction, collapse/dead and revival/recovery poses using actuallifecycle references. Reuse character identity/pivots but keep conditions/transitions separate from attack animation.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check HPpositive→zero, conditionalhold, delayedE4/status8000, actualrevival target/MPoritemchange, normalconfig restoration.

**Engine scope:** Actual HP/status lifecycle transitions observed; finite publicclips may cover only reaction subsets.

**Still missing:** No newly authored damage/death/revival animations. Publiclethal120ticks is a lethalreaction excerpt, not the complete bridge or proof of finisheddeathclip. Not allhero/weapon/directioninterrupt branches observed.

### Unlabelled generic action rows / gesture candidates

**Identity:** `unlabelled_generic`; unknown.

**Source coverage:** decoded {"generic_rows": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50], "bindings": 576, "explicitly_not_all_gestures": true}; observed {"some_scripts_reached_in_damage_status_cast_routes": true, "row_semantic_identity": "unresolved"}; exported {"body_only_nominal_rows": true}.

**Authoring:** Inspect actualevent/action selection before naming a gesture. Then draw the gesture keys from a stable sprite and retain scriptcalls/waits/removedactor semantics. No idle/walkfallback.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Require nativeevent/context and referencepose before semanticlabel. Keep unknownIDs/sourceoffsets; verify fullstart/end and conditionalbranch.

**Engine scope:** Body assets load/play nominally; contextual dispatcher not established for everyrow.

**Still missing:** No verified exhaustivegesture/emote/narrativeaction inventory. Enemy/NPC/boss/chest/terrain/BG-onlyeffect tables are outside thisplayer-focused extraction scope. No newgestureart; unknownrows do not prove unused or nonexistent types.

### Authored right-facing cutout punch pilot

**Identity:** `authored_punch`; authored_pilot_only_not_native_equivalence.

**Source coverage:** decoded {"native_equivalence": false}; observed {"native_gameplay_rule": false}; exported {"pilot_frames": 12, "layers": 11}.

**Authoring:** Construct windup, punch, follow-through and recovery with a stable body/weapon-free rig; add intentionalhip/shoulderweightresponse rather than claimingnative sword equivalence.

**QC:** Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose. Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval. Check foldedarm02..05 seams, shoulderfollow-through, neutralrecovery and declaredauthoredevents.

**Engine scope:** ActualGodotlayer-raster construction and editorexchange mechanics proven; authoredcombatbehavior/hitwindows not established.

**Still missing:** Prototypeonly/changes_requested; not finishedglove or nativeequipmentattack library.

## All42 captured normal spell IDs

These are native spell labels from the current hashed route index, not42 newly painted effects. Original all-living Revivify was rejected; the actual dead-target route supplies successful ID21(hex). Cast/effect/target and palette behavior remain separate components.

| ID hex | Caster | Source spell label | Actual indexed route |
|---|---|---|---|
| 00 | popoi | earth-slide | `spell-popoi-00-earth-slide` |
| 01 | popoi | gem-missile | `spell-popoi-01-gem-missile` |
| 02 | popoi | slowdown | `spell-popoi-02-slowdown` |
| 03 | primm | stone-saber | `spell-primm-03-stone-saber` |
| 04 | primm | speedup | `spell-primm-04-speedup` |
| 05 | primm | defender | `spell-primm-05-defender` |
| 06 | popoi | freeze | `spell-popoi-06-freeze` |
| 07 | popoi | acid-storm | `spell-popoi-07-acid-storm` |
| 08 | popoi | energy-absorb | `spell-popoi-08-energy-absorb` |
| 09 | primm | ice-saber | `spell-primm-09-ice-saber` |
| 0a | primm | remedy | `spell-primm-0a-remedy` |
| 0b | primm | cure-water | `spell-primm-0b-cure-water` |
| 0c | popoi | fireball | `spell-popoi-0c-fireball` |
| 0d | popoi | exploder | `spell-popoi-0d-exploder` |
| 0e | popoi | lava-wave | `spell-popoi-0e-lava-wave` |
| 0f | primm | flame-saber | `spell-primm-0f-flame-saber` |
| 10 | primm | fire-bouquet | `spell-primm-10-fire-bouquet` |
| 11 | primm | blaze-wall | `spell-primm-11-blaze-wall` |
| 12 | popoi | air-blast | `spell-popoi-12-air-blast` |
| 13 | popoi | thunderbolt | `spell-popoi-13-thunderbolt` |
| 14 | popoi | silence | `spell-popoi-14-silence` |
| 15 | primm | thunder-saber | `spell-primm-15-thunder-saber` |
| 16 | primm | balloon | `spell-primm-16-balloon` |
| 17 | primm | analyzer | `spell-primm-17-analyzer` |
| 18 | popoi | change-form | `spell-popoi-18-change-form` |
| 19 | popoi | mp-absorb | `spell-popoi-19-mp-absorb` |
| 1a | popoi | lunar-magic | `spell-popoi-1a-lunar-magic` |
| 1b | primm | moon-saber | `spell-primm-1b-moon-saber` |
| 1c | primm | lunar-boost | `spell-primm-1c-lunar-boost` |
| 1d | primm | moon-energy | `spell-primm-1d-moon-energy` |
| 1e | popoi | sleep-flower | `spell-popoi-1e-sleep-flower` |
| 1f | popoi | burst | `spell-popoi-1f-burst` |
| 20 | popoi | sprite-mana-magic | `spell-popoi-20-sprite-mana-magic` |
| 21 | primm | revivify-dead-target | `spell-primm-21-revivify-dead-target` |
| 22 | primm | wall | `spell-primm-22-wall` |
| 23 | primm | girl-mana-magic | `spell-primm-23-girl-mana-magic` |
| 24 | popoi | evil-gate | `spell-popoi-24-evil-gate` |
| 25 | popoi | dark-force | `spell-popoi-25-dark-force` |
| 26 | popoi | dispel-magic | `spell-popoi-26-dispel-magic` |
| 27 | primm | light-saber | `spell-primm-27-light-saber` |
| 28 | primm | lucent-beam | `spell-primm-28-lucent-beam` |
| 29 | primm | lucid-barrier | `spell-primm-29-lucid-barrier` |

## Native method and causal learning boundary

`matrix.json` links native parser/frame-fetch/body assembly and projectile instance contracts separately from authored assets. Per-type semantic-method and causal-proof fields remain null where unproven. Bounded 65816 width assumptions remain explicit; CPU watchpoint co-occurrence is not a causal callgraph. The parent-owned one-byte normal right Sword experiment now has at least 273 passing checks (313 in the current receipt): control byte 1C→19 changes the first displayed hold from 5 to 10 native ticks, retains subsequent holds of 5/5, and delays later poses/completion by 5 ticks. Independent scalar OAM/VRAM/CGRAM reconstruction supports one-tick presentation lag and rejects zero/two-tick lag. This establishes only that bounded original-game intervention, not a method mapping for other types or newly authored art.

The corrected-player GPU bridge adds **255 actual first/middle/last rendered samples across 85 unchanged routes**, compared with independently raw-rebuilt hardware goldens (11,832 scalar checks). The old full 28,123-frame GPU proof remains bound to its old player; no restamp or full corrected-player render is claimed. The separate current engine clock receipt has 9,881 checks on 14 routes. Historical four-binding stale gate receipts remain in `historical-stale/`; current browser QA is rehashed independently.

## Completeness gates and reproduction

The production target contract proposes four views for ordinary hero/equipment/casting assets and context-gated bindings for transformed/status/lifecycle families. It does not assert that every native source script is reachable in every view. The contract is separately frozen in `requirements.json`; changing it changes the requested scope and requires review.

`new_art_complete` intentionally fails all **639 minimum required binding atoms**, plus unresolved semantic/context scope gaps. These 639 minimum targets are not a complete whole-game specification. A pilot walk/punch is not aliased to Randi, Primm, Popoi, a sword attack,42 spells or transformed configurations. Accounting known families is a separate gate from finished-art completeness.

```sh
python3 qc/coverage/build_matrix.py
python3 qc/coverage/validate.py qc/coverage/matrix.json --requirements qc/coverage/requirements.json --gate discovered_family_accounting --verify-sources --report qc/coverage/accounting-gate.json
python3 qc/coverage/validate.py qc/coverage/matrix.json --requirements qc/coverage/requirements.json --gate decoded_idle_walk_exact_views --report qc/coverage/decoded-gate.json
# Expected failure until exact new assets and current approvals exist:
python3 qc/coverage/validate.py qc/coverage/matrix.json --requirements qc/coverage/requirements.json --gate new_art_complete --report qc/coverage/production-gap-gate.json
python3 qc/coverage/test_validate.py
```

Negative tests remove a complete returning-weapon family, remove the left walk, try a right-view alias, duplicate identities, change equipment/actor, fabricate approval states and alter a source hash. They must fail the **specific missing/stale/unsupported** condition; no fallback silently fills the requirement.

## Current audit findings

All fresh source count/hash/timing crosschecks pass.

Pixel presentation is authoritative:815 transformed current-WRAM poses were exactly one video tick ahead of hardware, and two config-copy transitions preceded body assembly. Normal static ordinary-weapon exports use a baseline palette; independent native palette state is not baked into them. Public OBJ replay excludes backgrounds, color math, scanline overflow and priority rotation. Native hash bindings and browser tests do not constitute deployment verification.

Actionable next work: author and independently review exact requested views/actions/effect assets; add missing run and charge directions/actors, missing charge-level contexts, semantic event/gesture identification, complete conditional dispatcher contracts and relevant spell target/level/cleanup branches. Additional rows or counts cannot close those gaps.

The approval stage additionally requires actual authored project/export evidence and a current approval artifact. A project must declare provenance.asset_role=authored_new_art; the review file must contain decision=approved, exact requested clip_ids, input_fingerprint and asset_sha256 keyed by the matrix evidence IDs. The validator reads the real review file and current asset bindings, so relabelling a changes_requested receipt in a coverage row cannot pass. This verifies approval evidence consistency, not artistic judgment.

#!/usr/bin/env python3
"""Read-only source-bound audit of discovered player/effect animation families.
Counts are explicit evidence strata, never counts of completed new character art.
"""
import collections, hashlib, json, re
from pathlib import Path
BASE = Path(__file__).resolve().parent
ART = Path('/home/astra/artifacts/rea-som-animation-2026-10-07')
SITE = Path('/home/astra/projects/som-sprite-lab-site')
OBJ = Path('/home/astra/projects/som-native-effect-renderer')
LAB = Path('/home/astra/projects/sprite-construction-lab')
ledger = {}
checks = []

def read(id, path):
    data = path.read_bytes()
    ledger[id] = {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    return json.loads(data)

def check(name, condition):
    checks.append({'name': name, 'passed': bool(condition)})
normal = read('normal_catalog', ART / 'integration/full-catalog-v2/clips.json')
static = read('normal_sequence_source', ART / 'animation/full-renderable-animations.json')
inventory = read('normal_inventory', ART / 'animation/full-inventory.json')
trans = read('transformed_catalog', ART / 'animation/full-transformed-export-v4/clips.json')
normal_audit = read('normal_pixel_audit', ART / 'animation/full-export-native-audit.json')
normal_godot = read('normal_godot_audit', ART / 'animation/full-export-godot-audit.json')
trans_audit = read('transformed_pixel_audit', ART / 'animation/full-transformed-export-audit-v4.json')
trans_lag = read('transformed_phase_audit', ART / 'animation/full-transformed-presentation-classification-v4.json')
trans_obs = read('transformed_input_summary', ART / 'runtime/advanced_v2/transformed_inputs_summary.json')
runtime = read('runtime_v2_review', ART / 'runtime/advanced_v2/review_routes_v2.json')
spell = read('spell_coverage', ART / 'runtime/advanced_v2/spell_catalog/native_spell_coverage_v2.json')
projectile = read('projectile_lifecycle', ART / 'runtime/advanced_v2/projectile_lifecycle_summary_v2.json')
expanded = read('runtime_100_scenarios', ART / 'runtime/expanded_summary.json')
palette = read('palette_model', ART / 'runtime/advanced_v2/palette_model_v2_validation.json')
index = read('native_site_index', SITE / 'native-godot/capture-index.json')
gpu = read('native_gpu_audit', OBJ / 'evidence/rendered-route-validation-final85-consolidated.json')
raw = read('native_raw_audit', OBJ / 'evidence/raw-native-obj-validation-final85-and-preserved.json')
browser = read('site_browser_audit', SITE / 'output/native/browser-validation.json')
authored = read('authored_pilot', LAB / 'study/layered-cutout/project.json')
quality = read('authored_review', LAB / 'native/authoring-review/layered-cutout/review.json')
contact = read('authored_contact_proof', LAB / 'study/layered-cutout/construction-proof.json')
attacks = read('body_weapon_normal_clips', ART / 'integration/attack-clips/clips.json')
walk = read('body_idle_walk_clips', ART / 'integration/body-clips/clips.json')
rompath = Path('/home/astra/artifacts/rea-som-test-2026-10-07/roms/Secret of Mana (USA).sfc')
rom = rompath.read_bytes()
ledger['original_private_ROM'] = {'path':str(rompath),'sha256':hashlib.sha256(rom).hexdigest(),'bytes':len(rom),'distribution':'read_only_private_not_copied'}
check('Original ROM SHA256 matches both catalog claims',ledger['original_private_ROM']['sha256']==normal['rom_sha256']==trans['rom_sha256'])
check('Normal export is bound to actual decoded sequence JSON',ledger['normal_sequence_source']['sha256']==normal['source_sha256'])
for image in range(8):
    expected = int.from_bytes(rom[0x10ffd0+image*2:0x10ffd2+image*2],'little')
    matching = [c for c in normal['clips'] if c['source']['table_kind']=='weapon_family' and c['family_index']==image]
    check('All hero family'+str(image)+' mapping uses native image table',len(matching)==480 and all(int(c['source']['mapping_table'],16)==0x110000+expected for c in matching))
check('normal current manifest bound to independent ROM pixel audit', ledger['normal_catalog']['sha256'] == normal_audit['catalog_sha256'] and normal_audit['passed'])
check('transformed current manifest bound to independent ROM pixel audit', ledger['transformed_catalog']['sha256'] == trans_audit['manifest_sha256'] and trans_audit['passed'])
check('decoded/exported normal binding cardinality', len(normal['clips']) == len(static['animations']) == 4452)
check('normal Godot roundtrip records all catalog clips', normal_godot['passed'] and normal_godot['animations'] == len(normal['clips']))
check('transformed finite projection count explicit', len(trans['clips']) == 2044)
check('all42 distinct native spell initializers including supplemental Revivify', set(spell['distinct_spell_ids_with_native_initializer']) == set(range(42)) and spell['initialized'] == 41 and spell['supplemental_dead_target_route']['cast_initializer_observed'])
check('all8 charge1/2 families observed', runtime['charge1_families'] == list(range(8)) and runtime['charge2_families'] == list(range(8)))
check('current authored review requests changes', quality['decision'] == 'changes_requested' and contact['art_quality_approved'] is False)
check('authored current project matches reviewed canonical project', quality['project_canonical_sha256'] == contact['project_sha256'])
check('authored review source file bytehash remains current', quality['source_file_sha256']['project.json'] == ledger['authored_pilot']['sha256'])
routes = []
gpu_ids = {r['id']: r for r in gpu['routes']}
for entry in index['routes']:
    rid = entry['id']
    data = read('route/' + rid, SITE / 'native-godot' / entry['path'])
    frames = data['frames']
    check(rid + ' route hash/count binds index', ledger['route/' + rid]['sha256'] == entry['route_sha256'] and len(frames) == entry['frame_count'])
    check(rid + ' source ticks contiguous', all((b['source_tick'] == a['source_tick'] + 1 for a, b in zip(frames, frames[1:]))))
    check(rid + ' current route binds actual GPU proof', gpu_ids[rid]['route_sha256'] == entry['route_sha256'] and gpu_ids[rid]['frames'] == len(frames) and (gpu_ids[rid]['pixel_differences'] == 0))
    directions = set()
    samples = []
    for f in [frames[0], frames[len(frames) // 2], frames[-1]]:
        sample = {'source_tick': f['source_tick'], 'actor_slot': f['actor_slot'], 'capture': f['capture']}
        ramfile = Path(f['capture']) / 'wram.bin'
        if ramfile.exists():
            ram = ramfile.read_bytes()
            check(rid + ' sampled original WRAM hash', hashlib.sha256(ram).hexdigest() == f['source_hashes']['wram.bin'])
            base = 57344 + f['actor_slot']
            rawdir = ram[base + 16]
            code = rawdir & 3
            direction = 'left' if rawdir & 128 else ['up', 'down', 'right', 'code3_unlabelled'][code]
            directions.add(direction)
            sample.update({'raw_action_word': int.from_bytes(ram[base + 16:base + 18], 'little'), 'sampled_direction': direction, 'identity': ram[base + 384], 'script_start': hex(int.from_bytes(ram[base + 24:base + 26], 'little'))})
        samples.append(sample)
    routes.append({'id': rid, 'actor': entry['actor'], 'actor_slot': entry['actor_slot'], 'frames': len(frames), 'first_source_tick': frames[0]['source_tick'], 'last_source_tick': frames[-1]['source_tick'], 'directions_sampled_not_full_coverage': sorted(directions), 'samples': samples, 'evidence': 'route/' + rid, 'native_condition_scope': 'Controlled checkpoint route; pose selection, palettes and hardware presentation are native; staging is disclosed in source route provenance.'})
check('all85 indexed routes/framecount current', len(routes) == 85 and sum((r['frames'] for r in routes)) == 28123)
check('raw independent audit reports pass with disclosed broader scope', raw['passed'] and raw['frames'] == 31672 and (not raw['issues']))
check('GPU currentindex hash bound', gpu['capture_index_sha256'] == ledger['native_site_index']['sha256'])
bridge_path=BASE/'current-gpu/bridge.json'
bridge_result={'passed':False}
if bridge_path.is_file():
    from current_gpu_bridge import verify_bridge
    read('current_corrected_player_gpu_bridge',bridge_path)
    bridge_result=verify_bridge(bridge_path,SITE/'native-godot',OBJ/'evidence/rendered-route-validation-final85-consolidated.json')
    check('Corrected current player bounded GPU bridge exact hashchain',bridge_result['passed'])
for id, n, key in [('native_player', 'native-godot/scripts/native_obj_player.gd', 'player_sha256'), ('native_shader', 'native-godot/scripts/indexed_object.gdshader', 'shader_sha256')]:
    data = (SITE / n).read_bytes()
    ledger[id] = {'path': str(SITE / n), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    check(id + ' actualcurrentcode bindsGPUproof', gpu[key] == ledger[id]['sha256'] or (id=='native_player' and bridge_result['passed']))
check('browser685current85routes allpass', browser['checks'] == 685 and (len(browser['routes']) if isinstance(browser['routes'], list) else browser['routes']) == 85 and not browser['errors'])
for n, h in browser['tested_artifact_hashes'].items():
    data = (SITE / n).read_bytes()
    ledger['browser_asset/' + n] = {'path': str(SITE / n), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    check('browserartifact ' + n + ' currentSHA', ledger['browser_asset/' + n]['sha256'] == h)
heroes = ['randi', 'primm', 'popoi']
directions = ['up', 'down', 'left', 'right']
weapons = ['glove', 'sword', 'axe', 'spear', 'whip', 'bow', 'boomerang', 'javelin']
families = []

def family(id, label, decoded, observed, exported, engine, recipe, qc, gaps, evidence, authored_clips=None, unknown=False):
    families.append({'id': id, 'label': label, 'label_status': 'unknown' if unknown else 'source_grounded', 'decoded_bindings': decoded, 'runtime_observed': observed, 'exported_tested': exported, 'engine_behavior': engine, 'newly_authored': {'clips': authored_clips or [], 'source': 'authored_pilot' if authored_clips else None}, 'quality_approved': False, 'quality_decision': 'changes_requested' if authored_clips else 'not_reviewed_new_art', 'evidence': evidence, 'single_sprite_authoring_recipe': recipe, 'actual_QC_checks_required': qc, 'remaining_gaps': gaps})
common = ['Review every held pose and adjacent transitions at128x160 or declared game scale; do not recenter cels per pose.', 'Bind review to source/project/export hashes; exact mechanics is separate from finished-art approval.']
family('idle', 'Idle / standing', {'generic_row': 0, 'bindings': 12}, {'hero_scenarios': '3heroes idle and natural standing traces', 'not_all_event_idle_variants': True}, {'body_clips': 12, 'normal_body_catalog': True}, 'Normal SpriteFrames save/reload and selected playback tested; no full RPG idle dispatcher acceptance.', ['Extract or draw one consistent grounded neutral key pose per required view. Separate body/equipment palettes and breathing or readiness cels; preserve explicit holds.'], common + ['Check ground/reference position, equipment attachment and breathe/readiness timing.'], ['No new idle artwork for three hero identities/four directions.', 'Readiness/status-related alternate rows remain contextual.'], ['normal_catalog', 'body_idle_walk_clips', 'runtime_100_scenarios', 'normal_godot_audit'])
family('walk', 'Walking', {'generic_row': 1, 'bindings': 12}, {'heroes': heroes, 'four_direction_inputs': True}, {'body_clips': 12, 'native_right_control_frames': 30}, 'Normal SpriteFrames playback tested; authoredpilot GPU layers and fixed stance soles verified.', ['Starting from one sprite, split only visible body parts with declared anchors or draw contact/opposite-contact keys; construct passing/recoil poses. A single fused sprite does not reveal hidden limbs or back view. Keep stance feet fixed under declared root displacement.'], common + ['Check both support halves, actual raster soles, loop wrap, hip/knee seams, world contact and attachment.'], ['Only one right-facing authoredpilot walk with12frames; changes_requested for knee/material/weight.', 'No complete new three-hero/four-direction walk library.'], ['normal_catalog', 'body_idle_walk_clips', 'runtime_100_scenarios', 'authored_pilot', 'authored_review'], ['walk'])
family('run', 'Running inputs / running pose selection', {'candidate_generic_rows': [2], 'nominal_only': True}, {'heroes': heroes, 'A_right_down_scenarios': True, 'R_inputs_not_equated_to_run_success': True}, {'nominal_body_rows': True}, 'Native scenario traces show poses; world movement/collision and authored running controller not fully tested.', ['Create a faster cycle with distinct stride length, lean and support durations from native reference, rather than only speeding up walk.'], common + ['Compare run input to observed action/script, displacement, contacts, collision stops and transition back to walk.'], ['Up/left running not exhaustively observed.', 'No newly authored running clip; do not alias walk.'], ['normal_catalog', 'runtime_100_scenarios'])
run_samples = []
for folder in sorted((ART / 'runtime/scenarios').glob('*run_a_right_down')):
    for capture in sorted(folder.iterdir()):
        if not capture.is_dir() or not (capture / 'wram.bin').is_file() or not ('a_right' in capture.name or 'a_down' in capture.name):
            continue
        data = (capture / 'wram.bin').read_bytes()
        eid = 'run_sample/' + folder.name + '/' + capture.name
        ledger[eid] = {'path': str(capture / 'wram.bin'), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
        action = int.from_bytes(data[0xe010:0xe012], 'little')
        script = int.from_bytes(data[0xe018:0xe01a], 'little')
        matches = sorted({c['action_row'] for c in normal['clips'] if c['source']['table_kind'] == 'generic' and c['actor'] == 'randi' and int(c['source']['script_start_pc'],16) == 0x110000 + script})
        run_samples.append({'scenario': folder.name, 'capture': capture.name, 'raw_action_word': hex(action), 'script': hex(script), 'generic_table_rows': matches, 'actual_direction': 'left' if action & 128 else ['up','down','right','code3_unlabelled'][action & 3], 'evidence': eid})
        check(eid + ' selected script exists in generic binding table', bool(matches))
run_family = next(f for f in families if f['id'] == 'run')
run_family['runtime_observed']['actual_capture_samples'] = run_samples
run_family['runtime_observed']['observed_run_row2_directions'] = sorted({r['actual_direction'] for r in run_samples if 2 in r['generic_table_rows']})
run_family['runtime_observed']['input_label_is_not_actual_pose_direction'] = True
run_family['evidence'] += [r['evidence'] for r in run_samples]

for n, w in enumerate(weapons):
    nearfar = [c for c in attacks['clips'] if c.get('weapon_family') == w]
    bindings = [c for c in normal['clips'] if c.get('family_index') == n and c['source']['table_kind'] == 'weapon_family']
    rids = [r['id'] for r in routes if r['id'].startswith(w + '-charge-')]
    levels = sorted((int(x.rsplit('-', 1)[-1]) for x in rids))
    family('weapon_' + w, w.title() + ' equipment actions / basic and charged attacks', {'family_index': n, 'allocated_rows': 40, 'bindings': len(bindings), 'mapping': 'D0FFD0+weapon image*2; actor-specific D2 body tables'}, {'basic_far': '3heroes×4directions native scenarios', 'near': 'Sword near row1 with adjacent native-built Rabite only' if w == 'sword' else 'Not independently established for all actors/directions', 'observed_charge_levels': [1, 2] + ([3, 6] if n in [5, 6, 7] else []), 'charge_actor': 'randi', 'site_routes': rids}, {'near_far_body_weapon_clips': len(nearfar), 'ordinary_palette_only': True, 'full_body_only_bindings': len(bindings)}, 'Native physical selection/movement observed in disclosed scenarios; indexedOBJ replay is not complete combat/charge dispatcher.', ['Construct grip, windup, extension/contact, follow-through and recovery keys specific to ' + w + '. Body and weapon share the native render center. Separate weapon cels, handedness and grip offsets; charge levels require distinct native sequence references, not faster copies.'], common + ['Check per-view grip/flips, body/equipment overlap, exact charge gate, script/pose clock, native cancellation and clean recovery.', 'Do not infer hit windows from drawn weapon extension.'], ['No newly authored ' + w + ' combat art.', 'Charge levels4/5/7/8 and all charge actors/directions not fully runtime covered.', '40allocated rows do not prove40reachable attacks or native loops.'], ['normal_catalog', 'body_weapon_normal_clips', 'runtime_100_scenarios', 'runtime_v2_review'] + ['route/' + r for r in rids])
for w in ['bow', 'boomerang', 'javelin']:
    life = [r for r in projectile if 'family' + str(weapons.index(w)) in r['route']]
    family('projectile_' + w, 'Returning boomerang' if w == 'boomerang' else w.title() + ' projectiles', {'native_constructor_update_terminal_hooks': True}, {'charge_thresholds': [0, 3, 6], 'max_instances': [r['max_simultaneous_instances'] for r in life], 'end_inactive': all((r['last_capture']['instances'] == [0, 0, 0] for r in life))}, {'site_route_count': sum((r['id'].startswith(w + '-charge-') for r in routes)), 'actual_presented_effects': True}, 'Actual native instance spawn/update/terminal or return hooks and indexedOBJ shader playback verified.', ['Keep actor launch pose separate from projectile/effect instances. Build per-instance motion/rotation/palette and lifetime; boomerang needs outward and returning travel plus reattachment, not a single actor atlas.'], common + ['Check native spawn tick, simultaneous instances, trajectory, wrap, return/catch or terminal condition, cleanup and no orphan effect.'], ['Only controlled Randi/fixed-direction threshold routes.', 'New projectile/return art and authored instance-controller not implemented.', 'PureOBJ excludesBG/color-math/scanline semantics.'], ['projectile_lifecycle', 'runtime_v2_review'] + ['route/' + r['id'] for r in routes if r['id'].startswith(w + '-charge-')])
spellrows = []
for r in routes:
    if not r['id'].startswith('spell-'):
        continue
    match = re.match('spell-(primm|popoi)-([0-9a-f]{2})-(.*)', r['id'])
    assert match
    spellrows.append({'spell_id': int(match[2], 16), 'hex_id': match[2], 'caster': match[1], 'source_label': match[3], 'route_id': r['id'], 'frames': r['frames'], 'runtime_initializer': True, 'effect_pixels_native_exported': True, 'newly_authored': False, 'quality_approved': False, 'directions': 'Observed route only; not4view coverage', 'evidence': 'route/' + r['id']})
check('public current routes include every normal spellID exactly once', sorted((s['spell_id'] for s in spellrows)) == list(range(42)))
family('spellcasting', 'Casting and42 normal spell IDs', {'generic_table_caster_rows': 'not labelled by static row alone', 'normal_spell_ids': list(range(42))}, {'initial_grid': {'attempts': 42, 'accepted': 41}, 'supplemental_revivify_dead_target': True, 'successful_distinct_ids': 42}, {'native_site_spell_routes': 42, 'frames': sum((s['frames'] for s in spellrows))}, 'Menu-driven native casting/MP/effect initialization observed. Whole spell target/resist/level/pause rules remain partial.', ['From one caster sprite, build cast anticipation, invocation and recovery per necessary view. Each spell ID needs its own effect asset/motion/palette/target contract; do not substitute one generic flash for42effects.'], common + ['Check menu/target legality, actualMP change, effect layer placement, spell-specific progression, cleanup, caster return and BG/color-math exclusions.'], ['No42 newly authored spell-effects library.', 'Not every spell level, targetclass/resist, cancel branch or4direction caster pose observed.', 'Initial all-living Revivify rejection must not be mistaken for completed cast.'], ['spell_coverage', 'runtime_v2_review'] + ['route/' + s['route_id'] for s in spellrows])
family('palette', 'Independent palette shimmer / phase and rotation', {'CGRAM_buffer_pipeline': True}, {'native_model_cases': 700, 'phase_cases': 400, 'bit20_rotation_cases': 300}, {'native85_routes_use_actual_CGRAM': True, 'normal_static_attack_export': 'baseline palette excludes shimmer'}, 'Standalone native palette helper/model and indexedGPU palette lookup tested; supported ranges explicitly bounded.', ['Keep indexed colors and material masks independent of pose frames. Build explicit palette-state timers or color-effect layers; do not bake one palette phase into everypose.'], common + ['Check samepose at differentvideo ticks, exactpalettephase/rotation, five/fifteen-word bounds and invalidranges.'], ['No newly authored palette transitions/material-region styling.', 'Static ordinaryweapon clips do not model independent native shimmer.'], ['palette_model', 'native_gpu_audit', 'native_raw_audit'])
family('status', 'Status-conditioned pose and waits', {'FE_FC_FD_FF_control': True}, {'staged_status_bits_per_hero': expanded['tested_status_bits_per_hero'], 'prone_status_0010': 'observed script5EEC/generic55/56', 'barrel_status_0400': 'observed script5D22/generic39/40'}, {'nominal_rows': 'conditional wait assumptions retained', 'actual_source_waits': True}, 'RuntimecontextE041/E05D/E060/E190 preserved; parserVM/conditionalcompletion component tested separately from fullRPG.', ['Make status clips depend on authoritative state; add prone/barrel-specific art only from provenidentity/reference. A conditional wait needs a resumable state gate, not guessed finiteGIF timing.'], common + ['Check E041override, single-slotcall/return, FE/FC/FDpredicate holds, FFdynamicreselection, interrupts and input gates.'], ['Many statussemantic names unknown; staged bits not natural gameplay acquisition.', 'No newstatusposeart or complete authoredstatusdispatcher.'], ['normal_catalog', 'runtime_100_scenarios', 'transformed_phase_audit'])
family('transformed', 'Observed transformed player configurations', {'config_ids': ['E4', 'EC', 'EE', 'F0', 'F1', 'F2', 'F6', 'F7', 'F8'], 'nominal_bindings': len(trans['clips'])}, {'hero_status_input_routes': 15, 'bits': [5, 6, 9, 12, 15]}, {'native85_transformed_routes': 15, 'presented_video_frames': 4980, 'nominal_frames': sum((len(c['frames']) for c in trans['clips']))}, 'Native configuration/gfx preparation and direction/B/run gates observed;9config resources roundtrip proven separately.', ['A transformed character needs replacement silhouette/graphics/config and its gated move/attack poses; cannot repaint normalhero cels and call it equivalent. Use config-specific palettes/bodytables and observedlegal action tables.'], common + ['Check actualconfig transitions, perconfiggfx/bodytable/mapping, preparedspecial2row37C0 arithmetic, gating, one-video presentation lag, restoration.'], ['Allocated nominalrows exceed reached gameplaypaths.', 'No newly authored transformedcharacters/configsprite libraries.', '815ordinaryone-tickdelays+2configurationcopybeforebodyassembly transitions must preserveactualOBJpresentation.'], ['transformed_catalog', 'transformed_input_summary', 'transformed_pixel_audit', 'transformed_phase_audit'] + ['route/' + r['id'] for r in routes if '_transform_' in r['id']])
for id, label, ids in [('damage', 'Native damage reaction/recovery', ['randi-native-damage-recovery']), ('lethal', 'Lethal reaction / dead configuration transition', ['randi-native-lethal-reaction', 'randi_transform_bit15_inputs']), ('revival', 'Revival item/spell and restoration', ['cup-of-wishes-revive', 'spell-primm-21-revivify-dead-target'])]:
    family(id, label, {'script_context': 'Native source timelines identify reaction/conditionalwait/config restore; static rownamealone insufficient'}, {'routes': ids, 'natural_rule_context': 'ActualRabitehits reduceHP; ghost/death bridge inpartyroute; actualmenuCupofWishes/RevivifyrestorestatusandHP'}, {'public_native_routes': len(ids)}, 'Actual HP/status lifecycle transitions observed; finite publicclips may cover only reaction subsets.', ['Draw distinct reaction, collapse/dead and revival/recovery poses using actuallifecycle references. Reuse character identity/pivots but keep conditions/transitions separate from attack animation.'], common + ['Check HPpositive→zero, conditionalhold, delayedE4/status8000, actualrevival target/MPoritemchange, normalconfig restoration.'], ['No newly authored damage/death/revival animations.', 'Publiclethal120ticks is a lethalreaction excerpt, not the complete bridge or proof of finisheddeathclip.', 'Not allhero/weapon/directioninterrupt branches observed.'], ['runtime_v2_review'] + ['route/' + r for r in ids])
unknown = [c for c in normal['clips'] if c['source']['table_kind'] == 'generic' and c['action_row'] >= 3]
family('unlabelled_generic', 'Unlabelled generic action rows / gesture candidates', {'generic_rows': list(range(3, 51)), 'bindings': len(unknown), 'explicitly_not_all_gestures': True}, {'some_scripts_reached_in_damage_status_cast_routes': True, 'row_semantic_identity': 'unresolved'}, {'body_only_nominal_rows': True}, 'Body assets load/play nominally; contextual dispatcher not established for everyrow.', ['Inspect actualevent/action selection before naming a gesture. Then draw the gesture keys from a stable sprite and retain scriptcalls/waits/removedactor semantics. No idle/walkfallback.'], common + ['Require nativeevent/context and referencepose before semanticlabel. Keep unknownIDs/sourceoffsets; verify fullstart/end and conditionalbranch.'], ['No verified exhaustivegesture/emote/narrativeaction inventory.', 'Enemy/NPC/boss/chest/terrain/BG-onlyeffect tables are outside thisplayer-focused extraction scope.', 'No newgestureart; unknownrows do not prove unused or nonexistent types.'], ['normal_inventory', 'normal_catalog'], unknown=True)
family('authored_punch', 'Authored right-facing cutout punch pilot', {'native_equivalence': False}, {'native_gameplay_rule': False}, {'pilot_frames': 12, 'layers': 11}, 'ActualGodotlayer-raster construction and editorexchange mechanics proven; authoredcombatbehavior/hitwindows not established.', ['Construct windup, punch, follow-through and recovery with a stable body/weapon-free rig; add intentionalhip/shoulderweightresponse rather than claimingnative sword equivalence.'], common + ['Check foldedarm02..05 seams, shoulderfollow-through, neutralrecovery and declaredauthoredevents.'], ['Prototypeonly/changes_requested; not finishedglove or nativeequipmentattack library.'], ['authored_pilot', 'authored_review'], ['attack'])
atoms = []
requirements = []

def atom(family, actor, equipment, direction, variant, decoded=False):
    key = '|'.join([family, actor, equipment, direction, variant])
    atoms.append({'id': key, 'family': family, 'actor': actor, 'equipment': equipment, 'direction': direction, 'variant': variant, 'stages': {'decoded': 'nominal_exported' if decoded else 'not_covered', 'newly_authored': 'not_covered', 'quality_approved': 'not_covered'}, 'evidence': ['normal_catalog'] if decoded else []})
    requirements.append({'id': key, 'family': family, 'actor': actor, 'equipment': equipment, 'direction': direction, 'variant': variant})
for f in ['idle', 'walk', 'run']:
    for h in heroes:
        for d in directions:
            atom(f, h, 'default_sword', d, 'normal', True)
for w in weapons:
    for h in heroes:
        for d in directions:
            for v in ['normal_near', 'normal_far', 'charge_1', 'charge_2']:
                atom('weapon_' + w, h, w, d, v, True)
for w in ['bow', 'boomerang', 'javelin']:
    for d in directions:
        for level in [0, 3, 6]:
            atom('projectile_' + w, 'randi', w, d, 'charge_' + str(level))
for s in spellrows:
    for d in directions:
        atom('spellcasting', s['caster'], 'spell_' + s['hex_id'], d, 'cast_effect')
for config in ['E4', 'EC', 'EE', 'F0', 'F1', 'F2', 'F6', 'F7', 'F8']:
    atom('transformed', 'config_' + config, 'native_prepared', 'context_gated', 'observed_configuration')
for f in ['palette', 'status', 'damage', 'lethal', 'revival', 'unlabelled_generic']:
    atom(f, 'context_dependent', 'not_applicable', 'context_gated', 'reference_and_state_contract')
atoms += [{'id': 'walk|authored_pilot|none|right|cutout', 'family': 'walk', 'actor': 'authored_pilot', 'equipment': 'none', 'direction': 'right', 'variant': 'cutout', 'stages': {'decoded': 'not_applicable', 'newly_authored': 'created_prototype', 'quality_approved': 'changes_requested'}, 'evidence': ['authored_pilot', 'authored_review']}, {'id': 'authored_punch|authored_pilot|none|right|cutout', 'family': 'authored_punch', 'actor': 'authored_pilot', 'equipment': 'none', 'direction': 'right', 'variant': 'cutout', 'stages': {'decoded': 'not_applicable', 'newly_authored': 'created_prototype', 'quality_approved': 'changes_requested'}, 'evidence': ['authored_pilot', 'authored_review']}]
result = {'schema': 'sprite-family-coverage/v1', 'scope': 'Discovered normalhero/weapon and observed transformedplayer/nativeeffect families from this extraction, not everyNPC/boss/terrain/BGanimation in the whole game. Proposed4view authored target is explicit and notnative reachability proof.', 'rom_sha256': normal['rom_sha256'], 'families': families, 'spells': sorted(spellrows, key=lambda s: s['spell_id']), 'native_routes': routes, 'atoms': atoms, 'requirements': requirements, 'summary': {'normal_decoded_bindings': len(normal['clips']), 'normal_exported_body_frames': sum((len(c['frames']) for c in normal['clips'])), 'normal_ordinary_body_weapon_clips': len(attacks['clips']), 'transformed_nominal_bindings': len(trans['clips']), 'native_public_routes': len(routes), 'native_public_frames': sum((r['frames'] for r in routes)), 'authored_pilot_clips': len(authored['animations']), 'authored_pilot_frames': len(authored['frames']), 'authored_pilot_layers': len(authored['layers']), 'quality_approved_new_art_clips': 0, 'family_records': len(families), 'production_requirement_atoms': len(requirements)}, 'gates': {'discovered_family_accounting': {'required_families': [f['id'] for f in families]}, 'decoded_idle_walk_exact_views': {'stage': 'decoded', 'accepted_states': ['nominal_exported'], 'required_ids': [r['id'] for r in requirements if r['family'] in ['idle', 'walk']]}, 'new_art_complete': {'stage': 'quality_approved', 'accepted_states': ['approved_production'], 'required_ids': [r['id'] for r in requirements]}}, 'source_ledger': ledger, 'source_audit': {'passed': all((c['passed'] for c in checks)), 'checks': checks, 'limits': 'Freshreport/hash/count/frameclockcrosschecks and threeWRAMcaptures/route sampled; historicalnativeGPU/rawallpixelproofs remain separatelyidentified. This run did not rerenderallgamepixels.'}, 'approval_boundary': 'Extracted/nominal/runtime/nativepixel/enginepass counts cannot stand for newlyauthored or approvedart. Authoredpilot identity is never aliased toRandi/Primm/Popoi. Everyfamily currentlyneeds additionalnewart/QC.'}
natural_damage = read('native_damage_HP50_states', ART/'runtime/advanced_v2/enemy_damage_released_gate/state_summary.json')
ghost_bridge = read('native_party_lethal_states', ART/'runtime/advanced_v2/party_native_lethal/state_summary.json')
item_revival = read('native_item_revival_states', ART/'runtime/advanced_v2/cup_of_wishes_complete/state_summary.json')
check('Native damage sequence startsHP50 and reaches0',natural_damage[0]['hp']==50 and natural_damage[-1]['hp']==0)
check('Party lethal bridge actually reaches configE4/status8000',ghost_bridge[0]['hp']==1 and ghost_bridge[-1]['hp']==0 and ghost_bridge[-1]['identity']==0xe4 and ghost_bridge[-1]['status']=='0080')
check('CupofWishes native deadtarget restores normalconfig andHP50 before laterdamage',item_revival[0]['hp']==0 and item_revival[0]['identity']==0xe4 and any(r['hp']==50 and r['identity']==0x80 and r['status']=='0000' for r in item_revival))
for f in families:
    if f['id']=='damage':f['evidence'].append('native_damage_HP50_states')
    if f['id']=='lethal':f['evidence'].append('native_party_lethal_states');f['runtime_observed']['bridge_setup']='ControlledpositiveHP1partyfixture, actualenemyhit and later native8000/E4; notthe unchangedHP50route.'
    if f['id']=='revival':f['evidence'].append('native_item_revival_states');f['runtime_observed']['item_restoration']='ActualHP0→50, followed by newnativeenemy damage to46 before captureend; finalHP alone is notrevivalfailure.'

result['current_corrected_player_gpu_bridge']=bridge_result
clock=read('current_engine_clock_report',LAB/'qc/engine/engine-timeline-report.json')
clock_bindings=read('current_engine_clock_source_bindings',LAB/'qc/engine/source-bindings.json')
clock_player=[r for r in clock_bindings if r['local']=='scripts/native_obj_player.gd']
check('Separate corrected player clock9881checks14routes currentbinding',clock['passed'] and clock['check_count']==9881 and len(clock['native_routes'])==14 and len(clock_player)==1 and clock_player[0]['sha256']==ledger['native_player']['sha256'])
result['current_engine_clock_scope']={'checks':9881,'native_routes':14,'evidence':['current_engine_clock_report','current_engine_clock_source_bindings'],'scope':'Separate actual clock/control/negative tests; not an all85 pixelproof or new-art approval.'}
methods = read('root_static_method_bytes', LAB/'learning/static-methods.json') if (LAB/'learning/static-methods.json').is_file() else None
projectile_contract = read('native_projectile_method_contract', ART/'effects/effect-projectile-lifecycle-contract.json')
parser_contract_path = ART/'animation/full-transformed-runtime-contract-v4.json'
parser_contract = read('native_parser_runtime_contract',parser_contract_path)
hold = read('native_right_sword_hold_intervention', LAB/'learning/hold-experiment-report.json')
watchpoints = read('native_right_sword_watchpoint_receipt', LAB/'qc/engine/method-trace/watchpoint-comparison-v2.json')
check('Bounded normal rightSword causal receipt has at least273 checks and zero failures',len(hold['checks'])>=273 and all(c['pass'] for c in hold['checks']) and not hold['failures'])
check('Displayed rightSword hold intervention preserves later5tickholds',[r['duration_ticks'] for r in hold['presented_pose_runs']['baseline']]==[5,5,5] and [r['duration_ticks'] for r in hold['presented_pose_runs']['changed']]==[10,5,5])
result['native_method_bindings'] = {
    'body_script_parser': {'address':'C0:F52D','frame_fetch':'C0:F582','descriptor_assembler':'C0:F632','evidence':['root_static_method_bytes','native_parser_runtime_contract'],'scope':'Byte/parser boundary evidence; selected and presented frames remain separate. Native method execution does not approve authored animations.'},
    'projectile_instances': {'spawn':projectile_contract['spawn'],'update':projectile_contract['update'],'return':projectile_contract['return'],'evidence':['native_projectile_method_contract','projectile_lifecycle'],'scope':'Named buffer/constructor/update/return contracts and observed native hooks; no extra callgraph inferred from co-occurrence.'},
    'causal_frame_hold_experiment': {'evidence':['native_right_sword_hold_intervention','native_right_sword_watchpoint_receipt'],'scope':'One normal right Sword branch only; original-game control fixture, not new authored art or all-family causal method mapping.','patch':hold['patch'],'presented_pose_runs':hold['presented_pose_runs'],'findings':hold['findings'],'limits':hold['limits']},
    'limits':['Unknown method identities/mappings remain null.','Bounded65816method disassembly is not itself runtime execution; width assumptions are explicit in source.','CPU watchpoint co-occurrence is not a causal callgraph.','No original-game causal experiment is newly authored animation or proof all families mapped.']
}
for f in families:
    if f['id'] == 'authored_punch':
        f['label_status'] = 'authored_pilot_only_not_native_equivalence'
    f['native_semantic_method'] = None
    f['causal_method_proof'] = {'binding':'causal_frame_hold_experiment','scope':'Normal right Sword first hold only; no other direction, charge level or equipment inferred.'} if f['id']=='weapon_sword' else None
    f['native_component_contract'] = 'projectile_instances' if f['id'].startswith('projectile_') else 'body_script_parser' if f['id'] in ['idle','walk','run','status','transformed','damage','lethal'] or f['id'].startswith('weapon_') else None

result['source_audit']['catalog_consistency_passed'] = all(c['passed'] for c in checks if not c['name'].startswith('browser'))
result['source_audit']['browser_freshness_passed'] = all(c['passed'] for c in checks if c['name'].startswith('browser'))
result['gates']['new_art_complete']['unresolved_scope_gaps'] = ['Unlabelled generic/event/gesture rows still require semantic identification before all-found-kinds completion.', 'Proposed639atoms are a minimum observed/reference target; further chargelevels/targets/statusbranches and missing gameplay contexts are not erased.']
result['input_fingerprint'] = hashlib.sha256(json.dumps(ledger, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
(BASE / 'matrix.json').write_text(json.dumps(result, indent=2) + '\n')
(BASE / 'requirements.json').write_text(json.dumps({'schema': 'sprite-family-requirements/v1', 'scope': result['scope'], 'gates': result['gates'], 'production_atoms': requirements}, indent=2) + '\n')
print(json.dumps({'source_audit_passed': result['source_audit']['passed'], 'checks': len(checks), 'failed': [c['name'] for c in checks if not c['passed']], 'summary': result['summary'], 'input_fingerprint': result['input_fingerprint']}))

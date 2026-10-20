from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json, hashlib

p = Path(__file__).parent
b = json.loads((p/'input-binding.json').read_text())
c = json.loads((p/'browser-capture.json').read_text())
s = json.loads((p/'output/playwright/served-source-binding-cli.txt').read_text().split('### Result\n')[1].split('\n')[0])
assert s['manifest_sha256'] == b['manifest_sha256'] == '82cc443fc6b5f05e806a60788a01602c4f683376f1a6ff303abb5cdb43a6da86'
m = json.loads(Path(b['manifest']).read_text())
assert hashlib.sha256(Path(b['manifest']).read_bytes()).hexdigest() == b['manifest_sha256']
cs = [
    ('art_target_match',9.25,.20,'Ornate red/gold Captain silhouette, face, halo and carried kit remain recognizable at native size.'),
    ('anatomy_volume',9.00,.15,'Full armored legs, convex greave and seated cap retain mass; the chest now settles separately from the waist without collapsing its volume.'),
    ('joint_continuity',9.00,.15,'Chest/waist articulation and cap face changes remain coherent through the full sequence; no gross hinge slit, neck stretch, grip break or layer pop was observed.'),
    ('pixel_craft',8.75,.10,'Palette and authored shell/collar clusters cohere. Fine transformed gold ornament and cloth contours are still busier at 2x than hand-redrawn pose clusters.'),
    ('cyclic_weight_leg_phasing',9.00,.20,'Alternating travel and passing, restrained chest settle relative to the belt, and slower loaded cadence combine into a convincing heavy armored march rather than only a rocking assembly.'),
    ('gear_attachment_secondary_motion',9.00,.10,'Sword arm and shield follow chest load while maintaining their hold; restrained cape/gear lag does not detach or jump.'),
    ('game_usability',9.00,.10,'Readable native-size one-view walk with stable registration and a clean visible cyclic boundary. Acceptance is scoped to this displayed walk.'),
]
score = float(sum(Decimal(str(v))*Decimal(str(w)) for _,v,w,_ in cs).quantize(Decimal('.001'),rounding=ROUND_HALF_UP))
assert score >= 9 and min(v for _,v,_,_ in cs) >= 8.5
observations = [
    'At loaded support, the chest and shoulder silhouette settle relative to the belt/waist; the release returns to the passing pose without a new global hop. The earlier upper-mass blocker is materially addressed.',
    'The head remains visually stable enough for a heavy carry; sword grip and shield ownership stay coherent during the new chest motion.',
    'Convex shin volume, cap seating and opposing leg exchange remain readable. No old-shin ghost, clipping, abrupt order pop or 71-to-0 reset was confirmed.',
    'The action reads as a restrained armored march with a raised sword and shield. It is not an unencumbered naturalistic walk, and this deliberate carry does not need a free arm swing.',
]
findings = [
    {'id':'ornament-cluster-polish','severity':'nonblocking_polish','frames':'loaded extremes and 2x chronological strips','observation':'Fine transformed gold ornament remains a little busy at enlarged scale. Hand-redrawing selected ornamental edge clusters could improve finish, but no native-size identity or attachment failure was found.'},
    {'id':'cape-sheetiness','severity':'nonblocking_style_limit','frames':'full cycle','observation':'The cape remains a restrained sheet-like secondary motion. More authored fold keys could add appeal later; its current movement is acceptable for the scoped heavy carry.'},
]
r = {
    'schema':'sprite.independent_art_review.v1','reviewer':'som_animation_decoder, independent temporal art reviewer',
    'candidate':'assembled-v20','decision':'approved','approval_scope':'Displayed approved-three-quarter Captain heavy walk only; reviewer art gate, not user acceptance or full production library.',
    'input_fingerprint':b['manifest_sha256'],'clip_ids':['captain_walk_assembled_v20'],'overall_score':score,
    'gate':{'overall_minimum':9,'each_category_minimum':8.5,'critical_defects_observed':[],'passed':True},
    'categories':[{'id':n,'score':v,'weight':w,'reason':why} for n,v,w,why in cs],
    'observations':observations,'findings':findings,
    'visual_coverage':{'fresh_source_poses':72,'ordinary_adjacent_pairs':71,'loop_wrap_pairs':1,'native_pair_pages_personally_viewed':18,'nearest2x_keys_personally_viewed':[0,18,36,54],'actual_browser_screens_personally_viewed':40,'chronological_strip_pages_personally_viewed':28,'runs':{k:{'screens':len(v['records']),'elapsed_clock_ms':v['stopped']['clock_ms'],'scale':v['stopped']['scale']} for k,v in c['runs'].items()},'continuous_video_ingestion':False,'clock_semantics':'Actual screenshot before/after clock ranges can cross a pose boundary.','per_pose_recentering':False,'inherited_visual_review':False},
    'served_binding':s,
    'source_chain':{k:v for k,v in m.items() if ('sha256' in k or k in ['timing_trial','upper_motion_profile','layer_order','source_parts'])},
    'limits':['Mechanical checks award no art points; scores are subjective fresh visual judgments.', 'Exhaustive source-pair viewing plus actual timed chronological screenshots is not continuous video ingestion.', 'No heel/toe-force or whole-boot biomechanical contact proof is asserted by this art review.', 'One view and one action only: no other direction, action, full-game library or user acceptance.', 'New leg masters and hinge underlap are authored art, not recovered hidden original pixels or proven 3D anatomy.', 'All earlier failed receipts remain unchanged; this new input-bound approval does not relabel them.'],
    'evidence_png_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.glob('*.png')},
    'raw_browser_evidence_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (p/'output/playwright').glob('*') if f.is_file()},
}
(p/'review.json').write_text(json.dumps(r,indent=2)+'\n')
lines = ['# Captain assembled-v20 independent full visual review','',f'**Scoped walk approval — {score}/10.** The fixed gate is 9 overall, each category at least 8.5, and no critical visual defect. Lowest category: pixel craft, 8.75. This is my subjective art judgment, not a score derived from passing mechanics.','',f'Manifest `{b["manifest_sha256"]}`. Actual served manifest matches the frozen source. Current player, source and renderer bindings are in review.json.','','Fresh visual coverage: all 72 source poses, 71 ordinary adjacencies and the 71→0 wrap, viewed in 18 fixed native-canvas pair pages; four exact 2x keys; every one of 40 actual browser chronological screenshots viewed in 28 strips. Native playback ran 4.333 seconds, compensation-off 2.100 seconds, and nearest 2x 4.433 seconds, with a 1.2-second cycle. Screenshot clock ranges can cross a pose boundary. This is not continuous video ingestion.','','The new chest/shoulder motion changes the support read: chest mass settles relative to the belt rather than simply leaning with the whole assembly, then releases into passing. The change is restrained enough to preserve the ornate Captain silhouette and carried equipment. No visible waist slit, stretched neck, broken grip, old-shin ghost, hard layer pop, clipping or abrupt cyclic reset was confirmed. Convex leg volume and cap seating remain effective.','','I consider this convincing as a heavy armored march with a raised sword and shield at the displayed native size. The score is not a claim that it is anatomically perfect or that every ornament was redrawn by hand.','', '| Category | Score |','|---|---:|']+[f'| {n.replace("_"," ")} | {v} |' for n,v,_,_ in cs]+['','Nonblocking polish: fine transformed gold ornament is somewhat busy at 2x; the cape still has restrained sheet-like motion. Selective ornamental cluster redraws or authored cloth keys could improve finish later. They are not failures of the scoped native-size walk.','','**Scope:** this reviewer approval covers only the frozen one-view, one-action Captain walk. It does not grant user acceptance, other-direction/action approval, a complete game animation library, or biomechanical heel/toe contact proof. Earlier rejected versions remain rejected on their original evidence.','','Reproduce pair pages with build_pairs.py, timed strips with build_browser_strips.py, and this receipt with write_review.py. Exact raw browser screenshots, capture script, configuration and clock/source logs remain under output/playwright.']
(p/'review.md').write_text('\n'.join(lines)+'\n')
print(score,b['manifest_sha256'])

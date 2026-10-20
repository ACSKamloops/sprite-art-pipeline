from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json, hashlib

p = Path(__file__).parent
b = json.loads((p / 'input-binding.json').read_text())
c = json.loads((p / 'browser-capture.json').read_text())
s = json.loads((p / 'output/playwright/served-source-binding-cli.txt').read_text().split('### Result\n')[1].split('\n')[0])
assert s['manifest_sha256'] == b['manifest_sha256']
m = json.loads(Path(b['manifest']).read_text())
assert hashlib.sha256(Path(b['manifest']).read_bytes()).hexdigest() == b['manifest_sha256']
categories = [
    ('art_target_match', 9.25, .20, 'The Captain silhouette, ornate kit, face and source palette remain recognizable and convincing at native size.'),
    ('anatomy_volume', 8.75, .15, 'The convex near shell has substantial armored mass. Loaded and passing cap faces now fit the changing leg better.'),
    ('joint_continuity', 8.75, .15, 'The flattened cap and authored seat reduce the disc-on-tube impression. No gross joint separation or hard layer pop was observed.'),
    ('pixel_craft', 8.75, .10, 'Gold/red collar, seat shadow and shell planes cohere. Fine transformed ornament still looks busier than individually drawn pose clusters at 2x.'),
    ('cyclic_weight_leg_phasing', 8.50, .20, 'Alternating travel and passing are clear, and variable holds modestly improve loaded rhythm. The upper mass still reads predominantly as a tilted assembly rather than a separately authored settle and release.'),
    ('gear_attachment_secondary_motion', 9.00, .10, 'Sword grip, shield and cape remain attached; restrained lag supports the heavy carry without visible detachment.'),
    ('game_usability', 9.00, .10, 'This is a readable, complete one-view walk candidate with a clean visible loop. It is not approval of other directions, actions or a whole game library.'),
]
score = sum(Decimal(str(v)) * Decimal(str(w)) for _, v, w, _ in categories)
score = float(score.quantize(Decimal('.001'), rounding=ROUND_HALF_UP))
finding = {
    'id': 'loaded-upper-mass-pose', 'priority': 1, 'severity': 'blocking_quality',
    'phases': '4–10 and 40–46 loaded intervals, versus 18–26 and 54–62 passing/release',
    'evidence': ['native-strip-00.png', 'native-strip-10.png', 'twice-strip-01.png', 'twice-strip-05.png', 'twice-strip-09.png', 'twice-strip-11.png'],
    'observation': 'The new timing gives the supporting leg more time, but the chest, shoulders and carried kit still largely lean together while the legs exchange. The change reads as a smoother mechanical march rather than a fully convincing heavy-body settle and push into the next step. This is a motion-appeal judgment; it is not a measured floor slip or heel/toe collision failure.',
    'smallest_trial': 'Author two restrained loaded upper-body keys: a slight chest/shoulder compression and counterrotation relative to the pelvis at each support, releasing toward the existing passing pose. Keep head registration, sword grip, shield ownership, boots, stride and total 1.2-second cycle. Compare against this frozen control at native playback; do not add more global bob or stride and do not reopen the now-improved cap merely to chase a score.',
    'success_criterion': 'The load-to-release distinction must be visible in the chest/shoulder silhouette at native size without stretching the neck, breaking the grip, collapsing the torso or producing an extra bob. This is a testable candidate criterion, not a guaranteed score increase.'
}
r = {
    'schema': 'sprite.independent_art_review.v1',
    'reviewer': 'som_animation_decoder, independent temporal art reviewer',
    'candidate': 'assembled-v18', 'decision': 'changes_requested',
    'input_fingerprint': b['manifest_sha256'], 'clip_ids': ['captain_walk_assembled_v18'],
    'overall_score': score,
    'gate': {'overall_minimum': 9, 'each_category_minimum': 8.5, 'critical_defects_observed': [], 'passed': False, 'failed_conditions': ['overall_score_below_9']},
    'categories': [{'id': n, 'score': v, 'weight': w, 'reason': reason} for n, v, w, reason in categories],
    'observations': [finding['observation'], 'The cap-face/seat repair materially improves the knee and is not retained as the old blocking defect.'],
    'findings': [finding],
    'improvements': ['Convex shell retains heavy volume.', 'Loaded/passing cap faces and seat shadow reduce the round-disc joint defect.', 'Long stride and opposing leg exchange remain readable.', 'Variable holds modestly improve loaded cadence.', 'Weighted gear carry remains attached.'],
    'no_confirmed_gross_defects': ['clipping', 'neck or grip detachment', 'old shin ghost', 'hard layer-order pop', 'abrupt 71-to-0 wrap reset'],
    'visual_coverage': {
        'fresh_source_poses': 72, 'ordinary_adjacent_pairs': 71, 'loop_wrap_pairs': 1,
        'native_pair_pages_personally_viewed': 18, 'nearest2x_keys_personally_viewed': [0, 18, 36, 54],
        'actual_browser_screens_personally_viewed': 40, 'chronological_strip_pages_personally_viewed': 28,
        'runs': {k: {'screens': len(v['records']), 'elapsed_clock_ms': v['stopped']['clock_ms'], 'scale': v['stopped']['scale']} for k, v in c['runs'].items()},
        'continuous_video_ingestion': False, 'clock_semantics': 'Actual browser screenshot before/after clock ranges may cross a pose boundary.',
        'per_pose_recentering': False, 'inherited_visual_review': False
    },
    'served_binding': s,
    'source_chain': {k: m[k] for k in ['source_sha256', 'leg_source_manifest_sha256', 'leg_renderer_sha256', 'upper_source_sha256', 'upper_design_sha256', 'assembler_sha256', 'pixel_affine_sha256', 'timing_trial']},
    'limits': ['Mechanical tests award no art points.', 'No continuous-video-ingestion claim: this is exhaustive source-pair viewing plus fresh actual timed chronological screenshots.', 'Conservative flat stance is permitted; no biomechanical heel/toe-force or whole-boot contact proof is asserted by this art review.', 'New leg masters are authored art, not recovered hidden source pixels or proven 3D anatomy.', 'No other action/direction, full library, user approval or production acceptance.', 'All previous receipts remain unchanged.'],
    'evidence_png_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in p.glob('*.png')},
    'raw_browser_evidence_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in (p / 'output/playwright').glob('*') if f.is_file()}
}
(p / 'review.json').write_text(json.dumps(r, indent=2) + '\n')
lines = [
    '# Captain assembled-v18 independent full art review', '',
    f'**Changes requested — {score}/10.** The fixed gate is 9 overall, every category at least 8.5, with no critical defect. All category minima pass; the overall score does not. This is a subjective art judgment, not a test-derived score.', '',
    f'Manifest: `{b["manifest_sha256"]}`. The actual served manifest matches the frozen file. Source, renderer, assembler, timing and current player hashes are bound in review.json.', '',
    'Fresh coverage: all 72 poses and all 71 ordinary adjacencies plus the 71→0 loop in 18 fixed native-canvas pair pages. I also viewed keys 0/18/36/54 at exact 2x and every one of 40 actual browser chronological screenshots in 28 strips. Native playback ran 4.383 seconds, compensation-off 2.067 seconds, and nearest 2x 4.367 seconds; cycle length is 1.2 seconds. Screenshot labels are before/after clock ranges, not exact readback of the presented pose. This is not continuous video ingestion.', '',
    'The cap repair is visible and useful: its face becomes flatter and changes angle with the loaded/passing leg, while the collar and seat shadow connect it to the convex shell. The old round-disc defect is materially reduced. Captain identity, armored volume, opposing leg travel and weighted gear carry hold up at native size. No gross clipping, neck/grip break, old-plate ghost, hard order pop or wrap reset was confirmed.', '',
    '**Remaining blocker:** ' + finding['observation'], '',
    '**Smallest bounded trial:** ' + finding['smallest_trial'], '',
    finding['success_criterion'], '',
    '| Category | Score |', '|---|---:|',
] + [f'| {n.replace("_", " ")} | {v} |' for n, v, _, _ in categories] + [
    '', 'Flat armored stance is a legitimate conservative choice. This review does not require an unproved heel roll and does not diagnose floor slip from visual appeal. Do not discard the working leg/cap repair or increase global movement to chase the number. A new upper-load trial needs another fresh actual-motion review.', '',
    'Reproduce pair pages with build_pairs.py, browser strips with build_browser_strips.py, and this receipt with write_review.py. Exact raw screenshots, browser configuration, capture script and clock/source logs are preserved under output/playwright. Older reviews are not rewritten or relabelled. No other direction, action, full-game library or user acceptance is granted.'
]
(p / 'review.md').write_text('\n'.join(lines) + '\n')
print(score, b['manifest_sha256'])

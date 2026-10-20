"""Read-only source/evidence reconciliation; output is confined to this folder."""
from pathlib import Path
import hashlib
import json

ROOT = Path('/home/astra/projects/emberwake-demo')
EVIDENCE = ROOT / 'docs/evidence/walk-game-preview-v9'
ACTUAL = Path('/home/astra/artifacts/emberwake-walk-game-preview-v9')
PROJECT = ACTUAL / 'project'
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


qualification = load(EVIDENCE / 'QUALIFICATIONS.json')
isolation = load(EVIDENCE / 'ISOLATION.json')
overlay = load(EVIDENCE / 'TEST-CLEANUP-OVERLAY.json')
copied = qualification['copied_evidence_hashes']
assert all(sha(EVIDENCE / name) == digest for name, digest in copied.items())
assert sha(ROOT / qualification['configuration']) == qualification['config_sha256'] == isolation['config_sha256']
assert sha(ROOT / 'scripts/build_isolated_art_preview.py') == isolation['helper_sha256']

canonical_deltas = {}
preview_deltas = {}
for name, original in isolation['copied_source_hashes'].items():
    current = sha(ROOT / name)
    preview = sha(PROJECT / name)
    if current != original:
        canonical_deltas[name] = current
    if preview != original:
        preview_deltas[name] = preview
assert canonical_deltas == {'tests/final_polish.gd': overlay['patched_sha256']}
expected_preview_deltas = {row['resource']: row['preview_sha256'] for row in isolation['resources']}
expected_preview_deltas['tests/final_polish.gd'] = overlay['patched_sha256']
assert preview_deltas == expected_preview_deltas
for row in isolation['resources']:
    assert sha(ROOT / row['resource']) == row['production_before_sha256']

for name, row in qualification['gameplay_sources_unchanged_from_v8'].items():
    assert sha(ROOT / name) == sha(PROJECT / name) == row['v8_sha256'] == row['v9_sha256']
    assert sha(Path('/home/astra/artifacts/emberwake-walk-game-preview-v8/project') / name) == row['v8_sha256']
for name in ['scripts/browser_diagnostics.gd', 'tests/browser_eight_directions.js', 'tests/final_polish.gd']:
    assert sha(ROOT / name) == sha(PROJECT / name) == sha(EVIDENCE / 'executed-source' / name)
assert sha(ROOT / 'tests/run_browser_eight_directions.py') == isolation['copied_source_hashes']['tests/run_browser_eight_directions.py']
assert sha(EVIDENCE / 'ORIGINAL-FINAL-POLISH.gd') == overlay['original_sha256']
assert sha(PROJECT / 'tests/final_polish_cleanup.gd') == overlay['patched_sha256']

actual_correspondence = {}
for name in ['BROWSER-EIGHT-DIRECTIONS.json', 'behavior-initial/RESULTS.json',
             'behavior-unpatched-followup/RESULTS.json', 'native-walk/RECEIPT.json',
             'media-replay/MEDIA-RECEIPT.json', 'ISOLATION.json',
             'TEST-CLEANUP-OVERLAY.json', 'FINAL-POLISH-CLEANUP.json',
             'BROWSER-TRACE-COVERAGE.json']:
    assert sha(ACTUAL / name) == sha(EVIDENCE / name)
    actual_correspondence[name] = name
assert sha(PROJECT / 'docs/evidence/checks/RESULTS.json') == sha(EVIDENCE / 'behavior-cleanup/RESULTS.json')
actual_correspondence['project/docs/evidence/checks/RESULTS.json'] = 'behavior-cleanup/RESULTS.json'
for run in load(EVIDENCE / 'FINAL-POLISH-CLEANUP.json')['runs']:
    assert sha(ACTUAL / run['log']) == sha(EVIDENCE / run['log']) == run['sha256']

v8_expected = '869e0606aa2d59c2cfe90922fc4a8582c86f84e2b821b4c2b819d1a00fbffd05'
assert sha(ROOT / 'docs/evidence/walk-game-preview-v8/BROWSER-EIGHT-DIRECTIONS.json') == v8_expected
assert sha(Path('/home/astra/artifacts/emberwake-walk-game-preview-v8/BROWSER-EIGHT-DIRECTIONS.json')) == v8_expected

for name, digest in qualification['web_files'].items():
    assert sha(Path('/home/astra/artifacts/emberwake-walk-cadence-study-v1/game-v9') / name) == digest
for kind in ['media', 'media-replay']:
    for clip in load(EVIDENCE / kind / 'MEDIA-RECEIPT.json'):
        assert sha(ACTUAL / kind / (clip['clip'] + '.mp4')) == clip['mp4_sha256']
        if kind == 'media':
            assert sha(EVIDENCE / kind / (clip['clip'] + '.mp4')) == clip['mp4_sha256']

after = {}
for manifest, base in [('INPUTS-BEFORE.json', ROOT), ('ACTUAL-INPUTS-BEFORE.json', Path('/'))]:
    before = load(OUT / manifest)
    values = {}
    for name, row in before.items():
        path = base / name
        values[name] = {'sha256': sha(path), 'bytes': path.stat().st_size}
        assert values[name] == row, f'Input changed during audit: {name}'
    after[manifest] = values
(OUT / 'INPUTS-AFTER.json').write_text(json.dumps(after, indent=2) + '\n')
result = {'passed': True, 'copied_evidence_hashes_verified': len(copied),
          'isolation_source_entries_verified': len(isolation['copied_source_hashes']),
          'canonical_source_deltas': canonical_deltas, 'preview_source_deltas': preview_deltas,
          'actual_copy_correspondence': actual_correspondence,
          'v8_failure_sha256': v8_expected,
          'nominated_before_after_inputs_unchanged': sum(len(v) for v in after.values()),
          'web_files_verified': len(qualification['web_files']),
          'media_MP4_files_verified': 12,
          'limits': 'Full 1728 PNG corpus not rescanned, no engine/browser reruns, no public deployment verification.'}
(OUT / 'HASH-VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))

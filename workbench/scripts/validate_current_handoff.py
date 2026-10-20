#!/usr/bin/env python3
"""Check selected handoff hashes and local links; no semantic/art certification."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = Path('/home/astra/projects/pixellab-local-test-20261011')


def verify(root, research):
    failures = []
    counts = {}

    def read(path):
        return json.loads(path.read_text())

    def matches(path, expected, group):
        counts[group] = counts.get(group, 0) + 1
        try:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                failures.append({'kind': group, 'path': str(path), 'reason': 'hash'})
        except OSError as error:
            failures.append({'kind': group, 'path': str(path), 'reason': type(error).__name__})

    manifest_path = root / 'docs/consolidation/CURRENT-HANDOFF-MANIFEST.json'
    manifest = read(manifest_path)
    paths = [entry['path'] for entry in manifest['files']]
    if len(paths) != len(set(paths)):
        failures.append({'kind': 'duplicate-manifest-path'})
    for entry in manifest['files']:
        matches(Path(entry['path']), entry['sha256'], 'current_manifest_entries_checked')
    mirror = research / 'analysis-root/consolidation-20261012/CURRENT-HANDOFF-MANIFEST.json'
    if mirror.read_bytes() != manifest_path.read_bytes():
        failures.append({'kind': 'manifest-mirror'})

    catalog = read(root / 'sprite_workbench/contracts/RECONSTRUCTION-CATALOG.json')
    for entry in catalog['source_manifest']:
        base = {'research': research, 'workbench': root}[entry['namespace']]
        matches(base / entry['path'], entry['sha256'], 'catalog_source_files_checked')

    notes = read(research / 'REVIEWED-HANDOFF-FILES.json')
    for entry in notes['files']:
        matches(Path(entry['path']), entry['sha256'], 'explicit_authored_notes_checked')
    if len(notes['files']) != 14:
        failures.append({'kind': 'authored-notes-scope-changed'})

    source = root / 'docs/source-faithful'
    verification = read(source / 'VERIFICATION.json')
    for entry in verification['evidence']:
        matches(source / entry['file'], entry['sha256'], 'source_verification_evidence_checked')
    latest = read(root / 'docs/LATEST-VERIFICATION.json')
    current_directory = Path(latest['verification_directory'])
    if current_directory != source:
        for entry in read(current_directory / 'VERIFICATION.json')['evidence']:
            matches(current_directory / entry['file'], entry['sha256'], 'current_verification_evidence_checked')
    package = read(Path(latest['package_comparison']))
    for entry in package['runtime_files']:
        matches(root / 'sprite_workbench' / entry['file'], entry['sha256'], 'final_runtime_files_checked')
    matches(Path(package['wheel']), package['wheel_sha256'], 'final_wheel_checked')
    for path in [research / 'LOCAL-IMPLEMENTATION-STATUS.json',
                 research / 'analysis-root/full-reconstruction/LOCAL-IMPLEMENTATION-STATUS.json']:
        if read(path) != latest:
            failures.append({'kind': 'implementation-status-mirror', 'path': str(path)})
    if read(research / 'ANALYSIS-STATUS.json')['current_local_verification'] != latest:
        failures.append({'kind': 'analysis-status-mirror'})

    preserved = [root / 'docs/readiness/evidence/before-readiness/PRESERVATION.json',
                 source / 'evidence/before-source-v0.5/PRESERVATION.json',
                 research / 'analysis-root/consolidation-20261012/before-source-v0.5/PRESERVATION.json',
                 root / 'docs/provider-preparation/before-model-handoff-v0.6/PRESERVATION.json',
                 research / 'analysis-root/consolidation-20261012/before-model-handoff-v0.6/PRESERVATION.json']
    preserved.extend(Path(path) for path in manifest.get('preservation_manifests', []))
    for path in preserved:
        for entry in read(path)['files']:
            target = Path(entry.get('preserved', entry.get('copy', '')))
            if not target.is_absolute():
                target = root / target
            matches(target, entry['sha256'], 'historical_originals_checked')

    # Frozen documents retain their original link context. Check selected current
    # authored notes and current source guides, not copied historical markdown.
    docs = {Path(p) for p in paths if p.endswith('.md')}
    docs = {p for p in docs if not any(part.startswith('before-') for part in p.parts)}
    links = 0
    for path in sorted(docs):
        text = re.sub(r'^```.*?^```[^\n]*', '', path.read_text(), flags=re.M | re.S)
        for match in re.finditer(r'!?\[[^\]]*\]\((<[^>]+>|[^)\s]+)\)', text):
            target = match.group(1).strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            local = Path(unquote(parsed.path))
            local = local if local.is_absolute() else path.parent / local
            links += 1
            if not local.exists():
                failures.append({'kind': 'local-link', 'document': str(path), 'target': target})
    return {'updated_utc': datetime.now(timezone.utc).isoformat(), **counts,
            'local_links_checked': links, 'markdown_files_checked': len(docs),
            'failures': failures, 'semantic_completion': False,
            'scope': 'Selected current documentation, exact source/runtime/package hashes, status mirrors and preserved originals; no universal source, private-model or art acceptance claim'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--research', type=Path, default=RESEARCH)
    args = parser.parse_args()
    report = verify(args.root, args.research)
    output = args.root / 'docs/consolidation/HANDOFF-VALIDATION.json'
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({**report, 'failures': len(report['failures'])}, indent=2))
    raise SystemExit(2 if report['failures'] else 0)

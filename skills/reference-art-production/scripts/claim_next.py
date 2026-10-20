#!/usr/bin/env python3
"""Durable art-job claims and review queue. Uses SQLite; never calls an image API.

Workers claim/complete/fail jobs. A single publisher syncs the art manifest,
exports images, inspects them, records reviews, and verifies completion.
"""
import argparse
import hashlib
import json
import sqlite3
import sys
import time
import uuid
from collections import Counter
from pathlib import Path

from PIL import Image
from art_assets import need, output_path, resolve, save, sha, spec_for


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def decode(value):
    return json.loads(value) if value else None


def name_for(job_id):
    return hashlib.sha256(job_id.encode()).hexdigest()[:24]


def connect(root):
    directory = root / '.art-pipeline'
    directory.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(directory / 'state.sqlite3', timeout=30, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.executescript('''
        CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY, plan TEXT NOT NULL, fingerprint TEXT NOT NULL,
            status TEXT NOT NULL, source_review TEXT, result TEXT, review TEXT,
            worker TEXT, token TEXT, claimed_at REAL, updated_at REAL NOT NULL,
            attempt INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS events (
            number INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT,
            kind TEXT NOT NULL, created_at REAL NOT NULL, data TEXT NOT NULL);
    ''')
    return db


def event(db, job_id, kind, data):
    db.execute('INSERT INTO events(job_id,kind,created_at,data) VALUES(?,?,?,?)',
               (job_id, kind, time.time(), json.dumps(data, ensure_ascii=False)))


def get_job(db, job_id):
    job = db.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
    need(job is not None, 'Unknown job: ' + job_id)
    return job


def get_meta(db):
    row = db.execute("SELECT value FROM metadata WHERE key='collection'").fetchone()
    need(row is not None, 'Initialize this work area first')
    return decode(row['value'])


def check_references(root, plan):
    for ref in plan.get('references', []):
        need(bool(ref.get('role')), 'Reference needs a role')
        path = resolve(root, ref['path'])
        need(path.is_file() and sha(path) == ref['sha256'], 'Reference hash mismatch: ' + str(path))
        with Image.open(path) as image:
            image.verify()


def validate_plan(plan, spec=None):
    need(isinstance(plan['job_id'], str) and bool(plan['job_id']), 'Missing job_id')
    need(bool(plan.get('prompt')), 'Each job needs its actual prompt')
    need(bool(plan.get('covers', [plan['job_id']])), 'Job covers no requested entries')
    need(plan.get('mode', 'generate') in ('generate', 'edit'), 'Unknown job mode')
    if plan.get('mode') == 'edit':
        need(any(r.get('role') == 'edit-target' for r in plan.get('references', [])), 'Edit needs an edit-target input')
    need(isinstance(plan.get('priority', 0), int), 'Priority must be an integer')
    if spec and (spec['kind'] == 'pixel-sprite' or spec.get('transparent')):
        need(plan.get('transparent_background') is True, 'Job must request the transparency required by its export profile')


def initialize(db, document):
    spec_for({'art_spec': document['art_spec']})
    jobs = document['jobs']
    for plan in jobs:
        validate_plan(plan, document['art_spec'])
    ids = [p['job_id'] for p in jobs]
    targets = document['target_ids']
    covers = [i for p in jobs for i in p.get('covers', [p['job_id']])]
    need(targets and len(set(targets)) == len(targets), 'Freeze a nonempty unique target inventory')
    need(len(set(ids)) == len(ids), 'Duplicate jobs')
    need(set(covers) == set(targets) and all(n == 1 for n in Counter(covers).values()), 'Job coverage differs from targets')
    old = db.execute("SELECT value FROM metadata WHERE key='collection'").fetchone()
    if old:
        need(decode(old['value'])['initial_plan_sha256'] == fingerprint(document),
             'Already initialized with another plan. Use retry for job revisions or a new work area.')
        return {'initialized': False, 'resumed': True, 'jobs': len(jobs)}
    need(not db.execute('SELECT 1 FROM jobs LIMIT 1').fetchone(), 'Unowned jobs already exist')
    meta = {'pipeline_id': str(uuid.uuid4()), 'target_ids': targets, 'art_spec': document['art_spec'],
            'initial_plan_sha256': fingerprint(document)}
    db.execute("INSERT INTO metadata VALUES('collection',?)", (json.dumps(meta),))
    for plan in jobs:
        db.execute('INSERT INTO jobs(id,plan,fingerprint,status,updated_at) VALUES(?,?,?,?,?)',
                   (plan['job_id'], json.dumps(plan, ensure_ascii=False), fingerprint(plan), 'reference-needed', time.time()))
    event(db, None, 'initialized', meta)
    return {'initialized': True, 'pipeline_id': meta['pipeline_id'], 'jobs': len(jobs)}


def source_review(db, root, args):
    job = get_job(db, args.job)
    need(job['status'] in ('reference-needed', 'ready'), 'Cannot change source review during/after a generation attempt')
    plan = decode(job['plan'])
    check_references(root, plan)
    review = json.loads(args.review.read_text())
    need(review.get('reviewer') and review.get('observations'), 'Review needs reviewer and observations')
    review.update(plan_sha256=job['fingerprint'], reviewed_at=time.time())
    db.execute('UPDATE jobs SET source_review=?,status=?,updated_at=? WHERE id=?',
               (json.dumps(review), 'ready', time.time(), args.job))
    event(db, args.job, 'source-reviewed', review)
    return {'job_id': args.job, 'status': 'ready'}


def claim(db, root, worker):
    ready = db.execute("SELECT * FROM jobs WHERE status='ready'").fetchall()
    ready.sort(key=lambda j: (decode(j['plan']).get('priority', 0), decode(j['plan']).get('group', ''), j['id']))
    for job in ready:
        plan = decode(job['plan'])
        need(decode(job['source_review'])['plan_sha256'] == job['fingerprint'], 'Stale source review')
        try:
            check_references(root, plan)
        except (OSError, ValueError, KeyError) as exc:
            db.execute("UPDATE jobs SET status='reference-needed',source_review=NULL,updated_at=? WHERE id=?",
                       (time.time(), job['id']))
            event(db, job['id'], 'source-changed', {'reason': str(exc)})
            continue
        token = str(uuid.uuid4())
        db.execute("UPDATE jobs SET status='claimed',worker=?,token=?,claimed_at=?,updated_at=?,attempt=attempt+1 WHERE id=?",
                   (worker, token, time.time(), time.time(), job['id']))
        event(db, job['id'], 'claimed', {'worker': worker, 'token': token, 'attempt': job['attempt'] + 1})
        return {'job_id': job['id'], 'worker': worker, 'token': token, 'attempt': job['attempt'] + 1,
                'plan_sha256': job['fingerprint'], 'plan': plan}
    return None


def owned(db, args):
    job = get_job(db, args.job)
    need(job['status'] == 'claimed' and job['worker'] == args.worker and job['token'] == args.token,
         'Claim is inactive or belongs to another worker/attempt')
    return job


def finish(db, root, args):
    job = owned(db, args)
    plan = decode(job['plan'])
    receipt = json.loads(args.receipt.read_text())
    need(receipt['executed_prompt'] == plan['prompt'], 'Executed prompt differs from claimed plan')
    expected_refs = [str(resolve(root, r['path'])) for r in plan.get('references', [])]
    actual_refs = [str(resolve(root, p)) for p in receipt['reference_paths']]
    need(actual_refs == expected_refs, 'Ordered inputs differ from claimed plan')
    check_references(root, plan)
    source = resolve(root, receipt['generated_source'])
    with Image.open(source) as image:
        image.load()
        if plan.get('transparent_background', False):
            need(image.mode == 'RGBA' and image.getchannel('A').getextrema()[0] == 0,
                 'Generation does not have requested transparency')
    need(bool(receipt.get('tool')), 'Receipt needs actual tool identity')
    stem = name_for(job['id']) + f"/attempt-{job['attempt']:04d}"
    master = output_path(root, 'masters/' + stem + source.suffix.lower())
    master.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    if master.exists():
        need(master.read_bytes() == data, 'Conflicting master exists for this attempt')
    else:
        pending = master.with_suffix(master.suffix + '.pending')
        pending.write_bytes(data)
        pending.replace(master)
    receipt.update(job_id=job['id'], worker=args.worker, token=args.token, attempt=job['attempt'],
                   plan_sha256=job['fingerprint'], plan=plan, saved_master=str(master.relative_to(root)),
                   saved_master_sha256=sha(master), completed_at=time.time())
    receipt_path = output_path(root, 'receipts/' + stem + '.json')
    if receipt_path.exists():
        previous = json.loads(receipt_path.read_text())
        need(previous['token'] == args.token and previous['saved_master_sha256'] == sha(master), 'Conflicting receipt exists')
    save(receipt_path, receipt)
    result = {'master': {'path': str(master.relative_to(root)), 'sha256': sha(master)},
              'prompt': {'path': str(receipt_path.relative_to(root)), 'sha256': sha(receipt_path)}}
    db.execute("UPDATE jobs SET status='generated',result=?,review=NULL,worker=NULL,token=NULL,updated_at=? WHERE id=?",
               (json.dumps(result), time.time(), job['id']))
    event(db, job['id'], 'generated', result)
    return {'job_id': job['id'], 'status': 'generated', **result}


def fail(db, root, args):
    job = owned(db, args)
    error = json.loads(args.error.read_text())
    need(error.get('error'), 'Failure record needs actual error text')
    error.update(job_id=job['id'], attempt=job['attempt'], plan=decode(job['plan']),
                 worker=args.worker, token=args.token, kind=args.kind, recorded_at=time.time())
    path = output_path(root, f"errors/{name_for(job['id'])}/attempt-{job['attempt']:04d}.json")
    save(path, error)
    db.execute("UPDATE jobs SET status='failed',worker=NULL,token=NULL,updated_at=? WHERE id=?", (time.time(), job['id']))
    event(db, job['id'], 'failed', {'kind': args.kind, 'path': str(path.relative_to(root)), 'sha256': sha(path)})
    return {'job_id': job['id'], 'status': 'failed'}


def retry(db, args):
    job = get_job(db, args.job)
    need(job['status'] in ('failed', 'repair-needed', 'reference-needed'), 'Retry only a failed, rejected or source-incomplete job')
    old = decode(job['plan'])
    plan = json.loads(args.plan.read_text()) if args.plan else old
    validate_plan(plan, get_meta(db)['art_spec'])
    need(plan['job_id'] == job['id'] and plan.get('covers', [job['id']]) == old.get('covers', [job['id']]),
         'A revision must preserve job identity and frozen coverage')
    last = db.execute("SELECT data FROM events WHERE job_id=? AND kind='failed' ORDER BY number DESC LIMIT 1", (job['id'],)).fetchone()
    if job['status'] == 'failed' and last and decode(last['data'])['kind'] == 'blocked':
        need(fingerprint(plan) != job['fingerprint'], 'Blocked request needs a meaningful revised plan, not an identical retry')
    event(db, job['id'], 'retry-requested', {'reason': args.reason, 'old_plan': old, 'new_plan': plan})
    db.execute("UPDATE jobs SET plan=?,fingerprint=?,status='reference-needed',source_review=NULL,result=NULL,review=NULL,worker=NULL,token=NULL,updated_at=? WHERE id=?",
               (json.dumps(plan, ensure_ascii=False), fingerprint(plan), time.time(), job['id']))
    return {'job_id': job['id'], 'status': 'reference-needed', 'requires_source_review': True}


def sync(db, root, manifest_name):
    meta = get_meta(db)
    path = output_path(root, manifest_name)
    old = json.loads(path.read_text()) if path.exists() else {}
    if old:
        need(old.get('pipeline_id') == meta['pipeline_id'], 'Refusing to overwrite an unrelated manifest')
    previous = {s['id']: s for s in old.get('subjects', [])}
    records = []
    mapping = {}
    for job in db.execute('SELECT * FROM jobs ORDER BY id'):
        plan = decode(job['plan'])
        result = decode(job['result'])
        if not result:
            continue
        subject = {'id': job['id'], 'name': plan.get('name', job['id']), 'group': plan.get('group', ''),
                   'covers': plan.get('covers', [job['id']]), 'references': plan.get('references', []),
                   'notes': plan.get('notes', []), 'pipeline_status': job['status'], **result}
        prior = previous.get(job['id'], {})
        if prior.get('master') == result['master']:
            for key in ('exports', 'review_history'):
                if key in prior:
                    subject[key] = prior[key]
        review = decode(job['review'])
        canonical = next((e for e in subject.get('exports', []) if e['scale'] == 1), None)
        if review and canonical and canonical['sha256'] == review['export_sha256'] and \
                sha(output_path(root, canonical['path'])) == canonical['sha256']:
            subject['visual_review'] = review
        else:
            subject['visual_review'] = {'status': 'pending'}
            if review:
                db.execute("UPDATE jobs SET status='generated',review=NULL,updated_at=? WHERE id=?", (time.time(), job['id']))
                subject['pipeline_status'] = 'generated'
                event(db, job['id'], 'review-invalidated', {'previous_review': review, 'reason': 'Canonical export no longer matches'})
        records.append(subject)
        for target in subject['covers']:
            mapping[target] = {'representative_id': job['id'], 'name': subject['name'],
                               'exports': subject.get('exports', []), 'provenance': result['prompt']['path'],
                               'review_status': subject['visual_review']['status']}
    manifest = {'schema_version': 1, 'pipeline_id': meta['pipeline_id'], 'complete': False,
                'target_ids': meta['target_ids'], 'art_spec': old.get('art_spec', meta['art_spec']), 'subjects': records}
    save(path, manifest)
    save(root / 'source-id-map.json', {'pipeline_id': meta['pipeline_id'], 'entries': mapping})
    return {'manifest': str(path), 'available_representatives': len(records), 'covered_entries': len(mapping), 'complete': False}


def review_export(db, root, args):
    job = get_job(db, args.job)
    need(job['status'] in ('generated', 'accepted', 'repair-needed'), 'No current generated candidate to review')
    manifest = json.loads(output_path(root, args.manifest).read_text())
    need(manifest.get('pipeline_id') == get_meta(db)['pipeline_id'], 'Review manifest belongs to another pipeline')
    subject = next(s for s in manifest['subjects'] if s['id'] == args.job)
    need(subject['master'] == decode(job['result'])['master'], 'Manifest has another generation attempt')
    canonical = next(e for e in subject['exports'] if e['scale'] == 1)
    record = json.loads(args.review.read_text())
    need(record.get('reviewer') and record.get('observations'), 'Review needs reviewer and observations')
    need(record['export_sha256'] == canonical['sha256'] == sha(output_path(root, canonical['path'])), 'Reviewed export hash is stale')
    record.update(status=args.decision, reviewed_at=time.time(), attempt=job['attempt'])
    db.execute('UPDATE jobs SET review=?,status=?,updated_at=? WHERE id=?',
               (json.dumps(record), 'accepted' if args.decision == 'accepted' else 'repair-needed', time.time(), job['id']))
    event(db, job['id'], 'export-reviewed', record)
    return {'job_id': job['id'], 'status': args.decision}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init').add_argument('plan', type=Path)
    sub.add_parser('status')
    sub.add_parser('inspect').add_argument('--job', required=True)
    sub.add_parser('next').add_argument('--worker', required=True)
    source = sub.add_parser('source-review'); source.add_argument('--job', required=True); source.add_argument('--review', type=Path, required=True)
    for command in ('complete', 'fail', 'release', 'heartbeat'):
        cmd = sub.add_parser(command)
        for key in ('job', 'worker', 'token'): cmd.add_argument('--' + key, required=True)
        if command == 'complete': cmd.add_argument('--receipt', type=Path, required=True)
        if command == 'fail':
            cmd.add_argument('--error', type=Path, required=True); cmd.add_argument('--kind', choices=['blocked', 'transient', 'other'], default='other')
        if command == 'release': cmd.add_argument('--reason', required=True)
    cmd = sub.add_parser('recover'); cmd.add_argument('--job', required=True); cmd.add_argument('--reason', required=True); cmd.add_argument('--confirmed-stopped', action='store_true', required=True)
    cmd = sub.add_parser('retry'); cmd.add_argument('--job', required=True); cmd.add_argument('--reason', required=True); cmd.add_argument('--plan', type=Path)
    sub.add_parser('sync').add_argument('--manifest', default='art-manifest.json')
    cmd = sub.add_parser('review'); cmd.add_argument('--job', required=True); cmd.add_argument('--manifest', default='art-manifest.json'); cmd.add_argument('--review', type=Path, required=True); cmd.add_argument('--decision', choices=['accepted', 'repair-needed'], required=True)
    args = parser.parse_args()
    root = args.root.resolve(); root.mkdir(parents=True, exist_ok=True)
    db = connect(root)
    try:
        db.execute('BEGIN IMMEDIATE')
        if args.command == 'init':
            result = initialize(db, json.loads(args.plan.read_text()))
        else:
            get_meta(db)
            if args.command == 'source-review': result = source_review(db, root, args)
            elif args.command == 'next': result = claim(db, root, args.worker)
            elif args.command == 'complete': result = finish(db, root, args)
            elif args.command == 'fail': result = fail(db, root, args)
            elif args.command == 'retry': result = retry(db, args)
            elif args.command == 'sync': result = sync(db, root, args.manifest)
            elif args.command == 'review': result = review_export(db, root, args)
            elif args.command == 'inspect':
                result = dict(get_job(db, args.job))
                for key in ('plan', 'source_review', 'result', 'review'): result[key] = decode(result[key])
            elif args.command in ('release', 'recover', 'heartbeat'):
                job = owned(db, args) if args.command != 'recover' else get_job(db, args.job)
                need(job['status'] == 'claimed', 'Job is not actively claimed')
                if args.command == 'heartbeat': db.execute('UPDATE jobs SET updated_at=? WHERE id=?', (time.time(), args.job))
                else:
                    db.execute("UPDATE jobs SET status='ready',worker=NULL,token=NULL,updated_at=? WHERE id=?", (time.time(), args.job))
                    event(db, args.job, args.command, {'reason': args.reason, 'old_worker': job['worker'], 'old_token': job['token']})
                result = {'job_id': args.job, 'status': 'claimed' if args.command == 'heartbeat' else 'ready'}
            elif args.command == 'status':
                jobs = db.execute('SELECT id,status,worker,attempt,updated_at FROM jobs ORDER BY id').fetchall()
                result = {'counts': dict(Counter(j['status'] for j in jobs)), 'total': len(jobs),
                          'jobs': [dict(j) for j in jobs], 'note': 'No eligible next job does not mean complete. Verify the final art manifest.'}
        db.commit()
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, StopIteration, sqlite3.Error) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

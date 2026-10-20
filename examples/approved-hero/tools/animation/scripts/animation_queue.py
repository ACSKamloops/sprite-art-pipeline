#!/usr/bin/env python3
"""SQLite claim-next with exclusive lease tokens and separately recorded stage evidence."""
import argparse
import json
from pathlib import Path
import secrets
import sqlite3
import time
import hashlib
from animation_assets import check_review

STAGES = ['queued', 'authored', 'artifact_validated', 'engine_tested', 'visual_review', 'approved']

def connect(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, payload TEXT NOT NULL, stage TEXT NOT NULL DEFAULT "queued", owner TEXT, token TEXT, lease REAL, revision INTEGER NOT NULL DEFAULT 0)')
    db.execute('CREATE TABLE IF NOT EXISTS history (job TEXT, at REAL, event TEXT, receipt TEXT)')
    return db

def transaction(db, fn):
    db.execute('BEGIN IMMEDIATE')
    try:
        result = fn()
        db.execute('COMMIT')
        return result
    except BaseException:
        db.execute('ROLLBACK')
        raise

def event(db, job, name, receipt):
    db.execute('INSERT INTO history VALUES (?,?,?,?)', (job, time.time(), name, json.dumps(receipt, sort_keys=True)))

def run(db, args):
    if args.command == 'init':
        jobs = json.loads(args.jobs.read_text())
        if not isinstance(jobs, list) or any(not isinstance(j, dict) or not j.get('id') or not j.get('source_fingerprint') for j in jobs):
            raise ValueError('Jobs need stable id and source_fingerprint')
        if len({j['id'] for j in jobs}) != len(jobs):
            raise ValueError('Duplicate job id')
        def add():
            for job in jobs:
                old = db.execute('SELECT payload FROM jobs WHERE id=?', (job['id'],)).fetchone()
                encoded = json.dumps(job, sort_keys=True)
                if old and old['payload'] != encoded:
                    raise ValueError('Existing job changed; create a new versioned id')
                db.execute('INSERT OR IGNORE INTO jobs(id,payload) VALUES (?,?)', (job['id'], encoded))
            return {'jobs': db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]}
        return transaction(db, add)
    if args.command == 'status':
        return {'stages': dict(db.execute('SELECT stage,COUNT(*) FROM jobs GROUP BY stage').fetchall()),
                'active_leases': db.execute('SELECT COUNT(*) FROM jobs WHERE lease>?', (time.time(),)).fetchone()[0]}
    if args.command == 'claim-next':
        if not args.owner.strip() or not 1 <= args.lease_seconds <= 86400:
            raise ValueError('Owner and bounded lease required')
        def claim():
            now = time.time()
            job = db.execute('SELECT * FROM jobs WHERE stage!="approved" AND (lease IS NULL OR lease<=?) ORDER BY id LIMIT 1', (now,)).fetchone()
            if not job:
                return {'job': None}
            token = secrets.token_hex(16)
            db.execute('UPDATE jobs SET owner=?,token=?,lease=?,revision=revision+1 WHERE id=?', (args.owner, token, now + args.lease_seconds, job['id']))
            event(db, job['id'], 'claim', {'owner': args.owner, 'stage': job['stage']})
            return {'job': job['id'], 'payload': json.loads(job['payload']), 'stage': job['stage'], 'token': token, 'lease_expires': now + args.lease_seconds}
        return transaction(db, claim)
    def mutate():
        job = db.execute('SELECT * FROM jobs WHERE id=?', (args.job,)).fetchone()
        if not job or not secrets.compare_digest(job['token'] or '', args.token) or not job['lease'] or job['lease'] <= time.time():
            raise ValueError('Missing job, wrong token or expired lease')
        if args.command == 'release':
            db.execute('UPDATE jobs SET owner=NULL,token=NULL,lease=NULL WHERE id=?', (args.job,))
            event(db, args.job, 'release', {})
        elif args.command == 'heartbeat':
            if not 1 <= args.lease_seconds <= 86400:
                raise ValueError('Lease must be 1..86400 seconds')
            db.execute('UPDATE jobs SET lease=? WHERE id=?', (time.time() + args.lease_seconds, args.job))
        elif args.command == 'revise':
            if not args.reason.strip():
                raise ValueError('Record a demonstrated defect or revision reason')
            event(db, args.job, 'revision_requested', {'previous_stage': job['stage'], 'reason': args.reason})
            db.execute('UPDATE jobs SET stage="queued",owner=NULL,token=NULL,lease=NULL,revision=revision+1 WHERE id=?', (args.job,))
        else:
            receipt = json.loads(args.receipt.read_text())
            if receipt.get('source_fingerprint') != json.loads(job['payload'])['source_fingerprint']:
                raise ValueError('Receipt source fingerprint differs from claimed job')
            old_index, new_index = STAGES.index(job['stage']), STAGES.index(args.stage)
            if new_index != old_index + 1:
                raise ValueError('Advance exactly one stage; preserve failed attempts separately')
            if not receipt.get('output_hashes') or not receipt.get('evidence_paths'):
                raise ValueError('Receipt needs output_hashes and evidence_paths')
            for filename, sha in receipt['output_hashes'].items():
                output = Path(filename)
                output = output if output.is_absolute() else args.receipt.parent / output
                if not output.is_file() or hashlib.sha256(output.read_bytes()).hexdigest() != sha:
                    raise ValueError('Missing or changed output: ' + filename)
            for filename in receipt['evidence_paths']:
                evidence = Path(filename)
                evidence = evidence if evidence.is_absolute() else args.receipt.parent / evidence
                if not evidence.is_file():
                    raise ValueError('Missing evidence: ' + filename)
            if args.stage == 'approved' and (receipt.get('decision') != 'approved' or not receipt.get('reviewer') or not receipt.get('observations')):
                raise ValueError('Approval requires explicit review decision and observations')
            if args.stage == 'approved':
                review_path = Path(receipt['review_receipt'])
                manifest_path = Path(receipt['review_manifest'])
                review_path = review_path if review_path.is_absolute() else args.receipt.parent / review_path
                manifest_path = manifest_path if manifest_path.is_absolute() else args.receipt.parent / manifest_path
                review_result = check_review(manifest_path, review_path)
                actual_review = json.loads(review_path.read_text())
                clip_id = json.loads(job['payload']).get('clip_id', args.job)
                if review_result['decision'] != 'approved' or clip_id not in actual_review['clip_ids']:
                    raise ValueError('This job lacks current hash-bound visual approval')
            db.execute('UPDATE jobs SET stage=?,revision=revision+1 WHERE id=?', (args.stage, args.job))
            event(db, args.job, 'advance:' + args.stage, receipt)
        return {'job': args.job, 'stage': db.execute('SELECT stage FROM jobs WHERE id=?', (args.job,)).fetchone()[0]}
    return transaction(db, mutate)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init'); p.add_argument('jobs', type=Path)
    sub.add_parser('status')
    p = sub.add_parser('claim-next'); p.add_argument('--owner', required=True); p.add_argument('--lease-seconds', type=int, default=1800)
    for name in ['release', 'heartbeat', 'advance', 'revise']:
        p = sub.add_parser(name); p.add_argument('job'); p.add_argument('--token', required=True)
        if name == 'heartbeat':
            p.add_argument('--lease-seconds', type=int, default=1800)
        if name == 'advance':
            p.add_argument('--stage', choices=STAGES[1:], required=True); p.add_argument('--receipt', type=Path, required=True)
        if name == 'revise':
            p.add_argument('--reason', required=True)
    args = parser.parse_args()
    try:
        with connect(args.db) as db:
            print(json.dumps(run(db, args)))
    except (ValueError, OSError, sqlite3.Error, json.JSONDecodeError) as exc:
        parser.exit(1, str(exc) + '\n')

if __name__ == '__main__':
    main()

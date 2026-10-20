#!/usr/bin/env python3
"""Atomic, source-bound claims for reverse-engineering cases; no ROMs in this queue."""
import argparse
import hashlib
import json
import sqlite3
import time
import uuid
from pathlib import Path


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def connect(path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path,timeout=10);db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, payload TEXT NOT NULL, fingerprint TEXT NOT NULL, status TEXT NOT NULL DEFAULT "pending", owner TEXT, token TEXT, claimed REAL, receipt TEXT)')
    return db


def register(db,cases):
    with db:
        for case in cases:
            text=json.dumps(case,sort_keys=True);fp=fingerprint(case)
            existing=db.execute('SELECT fingerprint FROM jobs WHERE id=?',(case['id'],)).fetchone()
            if existing and existing['fingerprint']!=fp:
                raise ValueError('Case inputs changed; register a new case revision: '+case['id'])
            db.execute('INSERT OR IGNORE INTO jobs(id,payload,fingerprint) VALUES(?,?,?)',(case['id'],text,fp))


def claim(db,owner):
    if not owner.strip():raise ValueError('Worker identity required')
    db.execute('BEGIN IMMEDIATE')
    row=db.execute('SELECT * FROM jobs WHERE status=? ORDER BY id LIMIT 1',('pending',)).fetchone()
    if row is None:db.commit();return None
    token=uuid.uuid4().hex
    db.execute('UPDATE jobs SET status=?,owner=?,token=?,claimed=? WHERE id=?',('claimed',owner,token,time.time(),row['id']));db.commit()
    return {'case':json.loads(row['payload']),'input_fingerprint':row['fingerprint'],'owner':owner,'token':token}


def complete(db,job,owner,token,receipt):
    db.execute('BEGIN IMMEDIATE')
    try:
        row=db.execute('SELECT * FROM jobs WHERE id=?',(job,)).fetchone()
        if not row or row['status']!='claimed' or row['owner']!=owner or row['token']!=token:
            raise ValueError('Claim is not owned by this worker/token')
        if receipt.get('input_fingerprint')!=row['fingerprint']:
            raise ValueError('Receipt belongs to different inputs')
        status=receipt.get('scope_status')
        if status not in ('observed_partial','verified_bounded','unresolved'):
            raise ValueError('Explicit bounded result required; no whole-game completion')
        if not receipt.get('limits') or not receipt.get('evidence'):
            raise ValueError('Evidence and limits required')
        evidence_ids={}
        for item in receipt['evidence']:
            path=Path(item['path'])
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
                raise ValueError('Missing or changed evidence: '+str(path))
            if item.get('id'):
                if item['id'] in evidence_ids:raise ValueError('Duplicate evidence identity')
                evidence_ids[item['id']]=item
        if receipt.get('causal_claim'):
            for kind in ('static_analysis','executed_trace','controlled_intervention','displayed_frame_check'):
                reference=receipt.get(kind)
                if not isinstance(reference,str) or reference not in evidence_ids or evidence_ids[reference].get('purpose')!=kind:
                    raise ValueError('Causal receipt needs a named, hash-bound evidence reference for '+kind)
        # This gate verifies ownership and evidence linkage, never scientific truth.
        # The adapter verifier and independent review must establish each conclusion.
        db.execute('UPDATE jobs SET status=?,receipt=? WHERE id=?',(status,json.dumps(receipt,sort_keys=True),job));db.commit()
    except Exception:
        db.rollback();raise


def release(db,job,owner,token,reason):
    if not reason.strip():raise ValueError('Recovery reason required')
    with db:
        changed=db.execute('UPDATE jobs SET status=?,owner=NULL,token=NULL,claimed=NULL,receipt=? WHERE id=? AND status=? AND owner=? AND token=?',
            ('pending',json.dumps({'released_reason':reason}),job,'claimed',owner,token)).rowcount
        if changed!=1:raise ValueError('Only the current claim owner/token can release work')


def main():
    p=argparse.ArgumentParser();p.add_argument('--db',required=True);sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('register');q.add_argument('manifest',type=Path)
    q=sub.add_parser('claim');q.add_argument('--worker',required=True)
    q=sub.add_parser('finish');q.add_argument('--id',required=True);q.add_argument('--worker',required=True);q.add_argument('--token',required=True);q.add_argument('--receipt',type=Path,required=True)
    q=sub.add_parser('release');q.add_argument('--id',required=True);q.add_argument('--worker',required=True);q.add_argument('--token',required=True);q.add_argument('--reason',required=True)
    sub.add_parser('status');args=p.parse_args();db=connect(args.db)
    if args.command=='register':register(db,json.loads(args.manifest.read_text())['cases']);out={'registered':db.execute('SELECT count(*) FROM jobs').fetchone()[0]}
    elif args.command=='claim':out=claim(db,args.worker)
    elif args.command=='finish':complete(db,args.id,args.worker,args.token,json.loads(args.receipt.read_text()));out={'id':args.id,'receipt_accepted':True}
    elif args.command=='release':release(db,args.id,args.worker,args.token,args.reason);out={'id':args.id,'released':True}
    else:out={r[0]:r[1] for r in db.execute('SELECT status,count(*) FROM jobs GROUP BY status')}
    print(json.dumps(out));db.close()


if __name__=='__main__':main()

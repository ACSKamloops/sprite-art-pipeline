#!/usr/bin/env python3
"""Verify the current catalog's hashes and original JSON pointers, not semantics."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def validate(directory):
    catalog=json.loads((directory/'REPORT-CATALOG.json').read_text())
    corpus=json.loads((directory/'RETAINED-FINDING-RECORDS.json').read_text())
    source=Path(catalog['source_root']);loaded={};failures=[]
    for entry in catalog['files']:
        try:raw=(source/entry['path']).read_bytes()
        except OSError:failures.append({'kind':'missing-file','path':entry['path']});continue
        if hashlib.sha256(raw).hexdigest()!=entry['sha256']:
            failures.append({'kind':'hash','path':entry['path']})
    for record in corpus['records']:
        try:
            if record['source_path'] not in loaded:
                loaded[record['source_path']]=json.loads((source/record['source_path']).read_text())
            value=loaded[record['source_path']]
            for key in record['pointer'].split('/')[1:]:
                key=key.replace('~1','/').replace('~0','~')
                value=value[int(key)] if isinstance(value,list) else value[key]
            if value!=record['record']:failures.append({'kind':'pointer-content','id':record['record_id']})
        except (OSError,ValueError,KeyError,IndexError,TypeError):
            failures.append({'kind':'pointer','id':record['record_id']})
    ids=[r['record_id'] for r in corpus['records']]
    if len(ids)!=len(set(ids)):failures.append({'kind':'duplicate-record-id'})
    return {'catalog_files':len(catalog['files']),'overlapping_records':len(corpus['records']),
            'failures':failures,'semantic_completion':False,'shareability_certified':False,
            'scope':'Current generated report catalog only; private and frozen subtrees excluded; author records not automatically true/current'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--directory',type=Path,default=ROOT/'docs/consolidation')
    args=parser.parse_args();report=validate(args.directory)
    (args.directory/'STRUCTURAL-VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'catalog_files':report['catalog_files'],'overlapping_records':report['overlapping_records'],
                      'failures':len(report['failures']),'semantic_completion':False},indent=2))
    return 2 if report['failures'] else 0


if __name__=='__main__':raise SystemExit(main())

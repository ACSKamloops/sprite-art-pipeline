#!/usr/bin/env python3
"""Index retained reports and typed findings without claiming semantic completion.

Only analysis/report material is indexed. Personal profiles, credentials, raw
network captures and frozen historical copies are excluded from traversal.
Outputs are a local evidence catalog, not a recursive sharing allowlist.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

DEFAULT_SOURCE=Path('/home/astra/projects/pixellab-local-test-20261011')
ROOT=Path(__file__).resolve().parents[1]
SOURCE_DIRS=['analysis-root','analysis-contract','analysis-models','analysis-poses','analysis-art','depth-round2','controlled-tests']
PRIVATE_PARTS={'private-evidence','private','browser-profile','extension-download','isolated-chromium-profile',
               'chromium-profile','node_modules','.git','__pycache__'}
HISTORICAL_PARTS={'frozen-initial','frozen-final','frozen-root','frozen-owner','frozen-targets','frozen-review',
                  'owner-corrections','initial-placeholder-audit','review-before-owner-ready','historical-entrypoints','consolidation-20261012'}
TOP_DOCS=['START-HERE.md','HANDOFF.md','CURRENT-ANALYSIS.md','ANALYSIS.md','ANALYSIS-SCOPE.md','ANALYSIS-STATUS.json',
          'RECONSTRUCTION-REQUIREMENTS.md','PAID-EXPLORATION.md','RUNTIME-CONTROLS.md','SUBSCRIPTION-AND-RUNTIME-PLAN.md',
          'runtime/exploration-summary.json','runtime/probe-ledger.json']
ARRAYS={'claims','obligations','additional_disclosure_areas','findings','gaps','questions','methods','flows',
        'commands','corrections'}


def permitted(path):
    parts=set(path.parts)
    return not parts & (PRIVATE_PARTS|HISTORICAL_PARTS) and not any('profile' in p.lower() or p.startswith('frozen-') for p in path.parts)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def generate(source,output):
    source=source.resolve();output.mkdir(parents=True,exist_ok=True)
    paths={source/p for p in TOP_DOCS if (source/p).is_file()}
    for folder in SOURCE_DIRS:
        for path in (source/folder).rglob('*'):
            if path.is_file() and not path.is_symlink() and path.suffix in {'.md','.json'} and permitted(path.relative_to(source)):
                if folder=='controlled-tests' and path.suffix=='.json' and not any(k in path.name.upper() for k in ['RESULTS','ANALYSIS','VERIFICATION','MANIFEST']):
                    continue  # Raw requests/replies/captures are not this report catalog's input.
                paths.add(path)
    catalog=[];records=[]
    for path in sorted(paths):
        rel=path.relative_to(source);raw=path.read_bytes()
        entry={'path':str(rel),'sha256':sha(raw),'bytes':len(raw),'kind':'markdown-report' if path.suffix=='.md' else 'structured-evidence',
               'semantic_review':'not implied by indexing','sharing_status':'not certified by this catalog'}
        role='historical-superseded' if any(k in str(rel).lower() for k in ['superseded','before-owner','initial-invalid','before-wrapper','initial-findings']) else 'retained-unadjudicated'
        entry['provenance_role']=role
        if path.suffix=='.md':
            text=raw.decode('utf-8',errors='replace')
            entry['title']=next((line.lstrip('# ').strip() for line in text.splitlines() if line.startswith('# ')),path.name)
            entry['sections']=[line.strip('# ').strip() for line in text.splitlines() if line.startswith(('## ','### '))]
        else:
            try:document=json.loads(raw)
            except (ValueError,UnicodeDecodeError):document=None;entry['parse_status']='invalid-json'
            if isinstance(document,dict):
                fields=set(document)&ARRAYS
                if path.name=='SOURCE-FLOW-EVIDENCE-INDEX.json':fields.add('records')
                for field in sorted(fields):
                    values=document[field]
                    if isinstance(values,dict):items=values.items()
                    elif isinstance(values,list):items=enumerate(values)
                    else:continue
                    for i,value in items:
                        pointer='/'+field+'/'+str(i).replace('~','~0').replace('/','~1')
                        # Typed author records are retained verbatim, not silently
                        # promoted to current truth or counted as unique findings.
                        records.append({'record_id':str(rel)+'#'+pointer,
                            'source_path':str(rel),'source_sha256':entry['sha256'],
                            'pointer':pointer,'record':value,
                            'provenance_role':role,
                            'status':'retained author record; reconcile source version and review boundary'})
        catalog.append(entry)
    stamp=datetime.now(timezone.utc).isoformat()
    note='Structural indexing only; record counts overlap and are not unique findings, semantic reviews, feature completion or shareability.'
    (output/'REPORT-CATALOG.json').write_text(json.dumps({'version':1,'updated_utc':stamp,'source_root':str(source),
        'scope':SOURCE_DIRS+TOP_DOCS,'private_and_frozen_subtrees_excluded':True,'boundary':note,'files':catalog},indent=2)+'\n')
    (output/'RETAINED-FINDING-RECORDS.json').write_text(json.dumps({'version':1,'updated_utc':stamp,'source_root':str(source),
        'boundary':note,'records':records},indent=2)+'\n')
    lines=['# Retained report catalog','',note,'','Use `RETAINED-FINDING-RECORDS.json` to search typed claims/questions; use original reports for their explanations.','']
    for entry in catalog:
        if entry['kind']=='markdown-report':
            lines.append('- ['+entry['title'].replace(']','\\]')+']('+str(source/entry['path'])+') — `'+entry['path']+'`')
    (output/'REPORT-CATALOG.md').write_text('\n'.join(lines)+'\n')
    return {'reports_and_structured_files':len(catalog),'retained_overlapping_records':len(records),
            'private_and_frozen_subtrees_excluded':True,'semantic_completion_claim':False}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=DEFAULT_SOURCE)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/consolidation')
    args=parser.parse_args();print(json.dumps(generate(args.source,args.output),indent=2))


if __name__=='__main__':main()

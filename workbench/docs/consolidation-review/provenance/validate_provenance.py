#!/usr/bin/env python3
"""Offline, bounded metadata/provenance audit. Never walks or reads private content."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pointer(doc, value):
    for part in value.strip('/').split('/') if value else []:
        part=part.replace('~1','/').replace('~0','~')
        doc=doc[int(part)] if isinstance(doc,list) else doc[part]
    return doc

def denied(path):
    return any(('profile' in p.lower() and not Path(p).suffix) or 'private' in p.lower() or p in ['extension-download','.env']
               or 'credential' in p.lower() or 'token' in p.lower() for p in path.parts)

def walk(doc, loc=''):
    if isinstance(doc,dict):
        yield loc,doc
        for key,value in doc.items():yield from walk(value,loc+'/'+str(key).replace('~','~0').replace('/','~1'))
    elif isinstance(doc,list):
        for i,value in enumerate(doc):yield from walk(value,loc+'/'+str(i))


def audit(root, investigation, implementation):
    result={'scope':'Selected offline provenance/link/package and metadata-only exclusion audit; no runtime/provider/secret inspection',
            'frozen_primary':'530baf35598cdbef24133783dd063bd021d1aa9c','inputs':[]}
    selected=['HANDOFF.md','CURRENT-ANALYSIS.md','ANALYSIS-SCOPE.md','ANALYSIS-STATUS.json','SHAREABLE-PATHS.txt',
              'evidence/report-manifest.json','evidence/handoff-link-verification.json',
              'analysis-root/ANALYSIS-RUN-HANDOFF-20261012.md',
              'analysis-root/full-reconstruction/READINESS.md','analysis-root/full-reconstruction/RECONSTRUCTION-SCOPE.md',
              'analysis-root/full-reconstruction/SOURCE-GATE.json','analysis-root/full-reconstruction/SOURCE-FLOW-EVIDENCE-INDEX.json']
    research=[investigation/p for p in selected]
    local=[root/'README.md']+sorted((root/'docs').rglob('*.md'))
    local=[p for p in local if 'consolidation-review' not in p.parts]
    for p in research+local:
        result['inputs'].append({'path':str(p),'exists':p.exists(),'sha256':sha(p) if p.is_file() else None})
    links=[]
    for p in research+local:
        if p.suffix!='.md' or not p.is_file():continue
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            target=target.strip('<>').split('#')[0]
            if not target or re.match(r'\w+://',target):continue
            target=target.split(' "')[0]
            dest=Path(target) if target.startswith('/') else p.parent/target
            links.append({'document':str(p),'target':target,'exists':dest.exists()})
    result['markdown_links']={'checked':len(links),'missing':[r for r in links if not r['exists']]}
    bindings=[]
    for rel in ['analysis-root/full-reconstruction/SOURCE-GATE.json','analysis-root/full-reconstruction/SOURCE-FLOW-EVIDENCE-INDEX.json','evidence/report-manifest.json',
                'analysis-contract/depth-round4/technique-methods-adversarial-review/OWNER-CORRECTION-RESOLUTION.json',
                'analysis-contract/depth-round4/animation-geometry-adversarial-review/OWNER-CORRECTION-RESOLUTION.json',
                'analysis-poses/depth-round4/transport-flows-adversarial-review/CORRECTION-RESOLUTION.json']:
        doc=json.loads((investigation/rel).read_text())
        for loc,node in walk(doc):
            path=node.get('path') or node.get('owner_path');expected=node.get('sha256')
            if not isinstance(path,str) or not isinstance(expected,str) or not re.fullmatch('[a-f0-9]{64}',expected):continue
            dest=Path(path) if path.startswith('/') else investigation/path
            record={'document':rel,'pointer':loc,'path':path,'expected_sha256':expected}
            if denied(dest):record['status']='private-path-not-read'
            elif not dest.is_file():record['status']='missing'
            else:
                record['actual_sha256']=sha(dest);record['status']='match' if expected==record['actual_sha256'] else 'snapshot-diff'
                if node.get('json_pointer') and dest.suffix=='.json':
                    try:pointer(json.loads(dest.read_text()),node['json_pointer']);record['json_pointer_resolves']=True
                    except (ValueError,KeyError,IndexError,TypeError):record['json_pointer_resolves']=False
            bindings.append(record)
    result['research_bindings']={'checked':len(bindings),'counts':dict(Counter(r['status'] for r in bindings)),'records':bindings}
    index=json.loads((investigation/'analysis-root/full-reconstruction/SOURCE-FLOW-EVIDENCE-INDEX.json').read_text())
    result['source_index']={'declared_records':index.get('record_count'),'actual_records':len(index['records']),
                            'actual_kinds':dict(Counter(r['kind'] for r in index['records'])),'declared_kinds':index.get('counts_by_kind')}
    implementation_receipts=[]
    chosen=[root/'docs/adversarial-root-implementation/LINEAGE-CORRECTION-RESOLUTION.json',
            root/'tests/evidence/geometry-integration-resolution/CORRECTION-RESOLUTION.json',
            root/'tests/evidence/state-geometry-adversarial/CORRECTION-RESOLUTION.json',
            root/'tests/evidence/state-geometry-adversarial/STORE-RESOURCE-RESOLUTION.json']
    for receipt in chosen:
        doc=json.loads(receipt.read_text());rows=doc.get('source_hashes',doc.get('source_files',[]))
        if isinstance(rows,dict):rows=[{'path':k,'sha256':v} for k,v in rows.items()]
        checks=[]
        for row in rows:
            dest=root/row['path'];actual=sha(dest)
            checks.append({'path':row['path'],'bound_sha256':row['sha256'],'current_sha256':actual,
                           'current_matches_bound_snapshot':actual==row['sha256']})
        implementation_receipts.append({'path':str(receipt.relative_to(root)),'sha256':sha(receipt),
                                        'source_identity_checks':checks,'interpretation':'Version-bound receipt; a later-source difference is not a failed past test'})
    result['selected_implementation_review_snapshots']=implementation_receipts
    local_manifests=[]
    for manifest in sorted((root/'tests/evidence').rglob('MANIFEST.json')):
        rows=json.loads(manifest.read_text()).get('files',[]);checks=[]
        for row in rows:
            dest=manifest.parent/row['file']
            checks.append({'file':row['file'],'exists':dest.is_file(),'matches':dest.is_file() and sha(dest)==row['sha256']})
        local_manifests.append({'path':str(manifest.relative_to(root)),'sha256':sha(manifest),'checked':len(checks),
                                'failures':[r for r in checks if not r['matches']]})
    result['local_evidence_manifests']=local_manifests
    methods=json.loads((root/'docs/METHODS-IMPLEMENTATION-RECEIPT.json').read_text());method_checks=[]
    for row in methods['source_binding_checks']:
        dest=investigation/row['path']
        method_checks.append({'path':row['path'],'expected_sha256':row['expected_sha256'],
                              'actual_sha256':sha(dest),'match':sha(dest)==row['expected_sha256']})
    result['implementation_source_bindings']=method_checks
    latest=json.loads((root/'docs/LATEST-VERIFICATION.json').read_text());run=Path(latest['verification_directory'])
    spec=json.loads((run/'SPECIFICATION.json').read_text());report=json.loads((run/'REPORT.json').read_text())
    package=json.loads((run/'PACKAGE-SMOKE.json').read_text())
    suites=list(ET.parse(run/'TESTS.xml').getroot().iter('testsuite'))
    counts={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
    changes=[];missing=[]
    for row in spec['source_files']:
        p=root/row['file']
        if not p.is_file():missing.append(row['file'])
        elif sha(p)!=row['sha256']:changes.append({'file':row['file'],'verified_sha256':row['sha256'],'current_sha256':sha(p)})
    result['verification_snapshot']={'spec_commit':spec['commit'],'report_commit':report['commit'],
        'declared_commit':latest['verified_commit'],'counts_from_xml':counts,'counts_from_latest':latest['mechanical_checks'],
        'report_digest_matches':sha(run/'REPORT.json')==latest['report_sha256'],
        'spec_digest_matches':sha(run/'SPECIFICATION.json')==latest['source_specification_sha256'],
        'declared_source_files':len(spec['source_files']),'changed_since_verified_snapshot':changes,'missing_since_snapshot':missing,
        'example_status':report['example_status'],'package_status':package['status']}
    wheels=sorted((implementation/'dist').glob('*.whl'));packages=[]
    for wheel in wheels:
        mismatch=[];members=[];excluded=[]
        with zipfile.ZipFile(wheel) as z:
            for name in z.namelist():
                members.append(name)
                if denied(Path(name)):excluded.append(name)
                if name.startswith('sprite_workbench/') and not name.endswith('/'):
                    p=root/name;actual=hashlib.sha256(z.read(name)).hexdigest()
                    if not p.is_file() or sha(p)!=actual:mismatch.append({'file':name,'wheel_sha256':actual,'current_sha256':sha(p) if p.is_file() else None})
        packages.append({'path':str(wheel),'bytes':wheel.stat().st_size,'sha256':sha(wheel),
                         'matches_latest_digest':sha(wheel)==latest['package_sha256'],'member_count':len(members),
                         'restricted_name_matches':excluded,'current_package_differences':mismatch})
    result['wheel']=packages
    tracked=subprocess.check_output(['git','ls-files','sprite_workbench'],cwd=root,text=True).splitlines()
    if wheels:
        with zipfile.ZipFile(wheels[0]) as z:names=set(z.namelist())
        result['wheel_missing_tracked_package_files']=[f for f in tracked if f not in names]
    result['contract_copies']=[{'name':p.name,'same':p.read_bytes()==(root/'sprite_workbench/contracts'/p.name).read_bytes()} for p in sorted((root/'contracts').glob('*.json'))]
    # Metadata only: known nested restrictions, not a recursive content inspection.
    restricted=['analysis-poses/depth-round2/isolated-chromium-profile',
        'analysis-poses/depth-round2/persisted-animation-review/isolated-chromium-profile',
        'analysis-poses/depth-round2/map-inpaint-closure/private',
        'analysis-models/depth-round2/prompt-enhancement-closure/private-evidence',
        'analysis-contract/depth-round2/font-ui-source-closure/private-evidence',
        'analysis-contract/depth-round2/workbench-export-followup/private-evidence',
        'analysis-contract/depth-round4/full-flow-contracts/private-evidence']
    result['recursive_share_boundary']=[{'path':p,'directory_exists':(investigation/p).is_dir(),
                                       'broad_parent_listed':p.split('/')[0]+'/' in (investigation/'SHAREABLE-PATHS.txt').read_text().splitlines(),
                                       'contents_read':False} for p in restricted]
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--investigation',type=Path,default=Path('/home/astra/projects/pixellab-local-test-20261011'))
    ap.add_argument('--implementation',type=Path,default=Path('/home/astra/projects/pixellab-local-workbench'))
    ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
    root=Path(__file__).resolve().parents[3]
    data=audit(root,args.investigation,args.implementation)
    args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'links':data['markdown_links'],'bindings':data['research_bindings']['counts'],
        'verification_changed_files':len(data['verification_snapshot']['changed_since_verified_snapshot']),
        'wheel_differences':[len(r['current_package_differences']) for r in data['wheel']],
        'private_contents_read':False},indent=2))

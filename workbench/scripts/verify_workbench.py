#!/usr/bin/env python3
"""Freeze scope, run real checks and keep complete local diagnostic artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]


def run(args,cwd=ROOT):
    return subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180)


def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output).resolve()
    if out.exists():raise SystemExit('Use an absent output directory; prior evidence is preserved')
    out.mkdir(parents=True)
    commit=run(['git','rev-parse','HEAD']).stdout.strip()
    status=run(['git','status','--short']).stdout
    files=[p for folder in ['sprite_workbench','tests','examples','docs'] for p in (ROOT/folder).rglob('*')
           if p.is_file() and '__pycache__' not in p.parts and '.pyc'!=p.suffix]
    files.extend([ROOT/'pyproject.toml',ROOT/'requirements-local.in',ROOT/'requirements-local.lock'])
    files.extend(p for p in (ROOT/'scripts').iterdir() if p.is_file() and p.suffix in {'.py','.sh'})
    from sprite_workbench.replication import doctor
    sources=[{'file':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
    specification={'kind':'local-workbench-verification','version':1,'commit':commit,'git_status_at_freeze':status,
                   'source_files':sources,'environment':doctor(),'provider_calls':0,'artistic_acceptance':'unreviewed',
                   'scope':'frozen mechanical subset; see docs/COVERAGE.md; no full vendor/model parity claim'}
    write(out/'SPECIFICATION.json',specification)
    tests=run([sys.executable,'-m','pytest','-q','--junitxml',str(out/'TESTS.xml')])
    (out/'TESTS.log').write_text(tests.stdout+tests.stderr)
    counts={'tests':0,'failures':0,'errors':0,'skipped':0}
    if (out/'TESTS.xml').exists():
        for suite in ET.parse(out/'TESTS.xml').getroot().iter('testsuite'):
            for key in counts:counts[key]+=int(suite.attrib.get(key,0))
    example=out/'example';shutil.copytree(ROOT/'examples/supplied-motion',example)
    cli=run([sys.executable,'-m','sprite_workbench','--workspace',str(out/'store'),'run',str(example/'plan.json')])
    (out/'EXAMPLE.log').write_text(cli.stdout+cli.stderr)
    try:result=json.loads(cli.stdout)
    except ValueError:result={'status':'technical_failure','reason':'CLI did not return valid JSON'}
    write(out/'EXAMPLE.json',result)
    report={'commit':commit,'checks':counts,'regression_exit':tests.returncode,'example_exit':cli.returncode,
            'example_status':result.get('status'),'source_specification':'SPECIFICATION.json',
            'review_body':'example/output/body/review/review.html',
            'review_composed':'example/output/composed/review/review.html',
            'continuous_motion_viewed':False,'artistic_acceptance':'unreviewed','provider_calls':0,
            'mechanical_status':'passed' if tests.returncode==cli.returncode==0 and not counts['skipped'] else 'incomplete'}
    write(out/'REPORT.json',report)
    print(json.dumps(report,indent=2))
    return 0 if report['mechanical_status']=='passed' else 2


if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
"""Check selected Git content without printing potential credential values."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess

ROOT=Path(__file__).resolve().parents[1]
PATTERNS={
 'provider_key':r'\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}',
 'github_token':r'\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{40,})',
 'jwt':r'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}',
 'aws_key':r'\bAKIA[A-Z0-9]{16}\b',
 'google_key':r'\bAIza[A-Za-z0-9_-]{30,}',
 'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'literal_bearer':r'(?i)bearer[ \t]+[A-Za-z0-9_.-]{28,}',
 'signed_download':r'(?i)(?:X-Amz-Signature|X-Goog-Signature)=[a-f0-9]{32,}',
}
FORBIDDEN_DIRS={'browser-profile','private-evidence','extension-download','node_modules','.venv','.godot','__pycache__'}
FORBIDDEN_SUFFIXES={'.sfc','.smc','.rom','.iso','.sav','.srm','.exe','.dll','.pem','.p12'}

def check():
    paths=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT).decode().split('\0')
    paths=sorted(set(filter(None,paths)));findings=[];text_count=0
    for rel in paths:
        p=ROOT/rel
        if not p.exists():findings.append({'path':rel,'kind':'missing-selected-file'});continue
        if p.is_symlink():findings.append({'path':rel,'kind':'symlink'});continue
        if not p.is_file():continue
        if any(x in FORBIDDEN_DIRS for x in p.relative_to(ROOT).parts) or p.suffix.lower()in FORBIDDEN_SUFFIXES or(p.name.startswith('.env')and p.name!='.env.example'):
            findings.append({'path':rel,'kind':'excluded-material-path'})
        if p.stat().st_size>95*1024*1024:findings.append({'path':rel,'kind':'oversized-git-file'})
        raw=p.read_bytes()
        if b'\0'in raw:continue
        try:s=raw.decode('utf-8')
        except UnicodeDecodeError:continue
        text_count+=1
        for kind,pattern in PATTERNS.items():
            for m in re.finditer(pattern,s):findings.append({'path':rel,'kind':kind,'line':s.count('\n',0,m.start())+1})
    result={'selected_files':len(paths),'text_files_scanned':text_count,'findings':findings,'passed':not findings,'scope':'Pattern/path/size checks of selected content, not a guarantee of all possible secrets or licensing.'}
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--report',type=Path);args=ap.parse_args();result=check()
    if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
if __name__=='__main__':main()


#!/usr/bin/env python3
"""Install the four bundled skills without overwriting differing local work."""
import argparse,hashlib,shutil
from pathlib import Path

def files(root):
    return {p.relative_to(root):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--destination',type=Path,required=True)
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args();source=Path(__file__).resolve().parents[1]/'skills'
    planned=[]
    for skill in sorted(source.iterdir()):
        if not (skill/'SKILL.md').is_file():continue
        dest=args.destination.expanduser().absolute()/skill.name
        if dest.is_symlink():raise SystemExit(f'Refusing symlink destination: {dest}')
        if dest.exists():
            if files(skill)==files(dest):print(f'Already identical: {dest}');continue
            raise SystemExit(f'Preserved differing skill: {dest}. Choose a fresh destination or review/update it separately.')
        planned.append((skill,dest))
    for src,dest in planned:
        print(('Would install: ' if args.dry_run else 'Installing: ')+str(dest))
        if not args.dry_run:shutil.copytree(src,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    print(f'{len(planned)} skill(s) '+('planned' if args.dry_run else 'installed'))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Lossless construction/editing CLI. Writes use atomic replacement."""
import argparse,json,sys,tempfile,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sprite_lab import *
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);payload=(canonical_json(value)+'\n').encode();fd,name=tempfile.mkstemp(dir=path.parent,prefix='.sprite-edit-')
    try:
        with os.fdopen(fd,'wb')as stream:stream.write(payload);stream.flush();os.fsync(stream.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)
def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    for command in ['validate','hash']:
        p=sub.add_parser(command);p.add_argument('project')
    p=sub.add_parser('apply');p.add_argument('project');p.add_argument('transaction');p.add_argument('--output',required=True);p.add_argument('--receipt',required=True)
    p=sub.add_parser('export');p.add_argument('project');p.add_argument('directory');p.add_argument('--columns',type=int,default=8)
    p=sub.add_parser('ora-export');p.add_argument('project');p.add_argument('frame_id');p.add_argument('output')
    p=sub.add_parser('ora-import');p.add_argument('ora');p.add_argument('output')
    p=sub.add_parser('ase-export');p.add_argument('project');p.add_argument('output');p.add_argument('--animation');p.add_argument('--sidecar')
    p=sub.add_parser('ase-import');p.add_argument('ase');p.add_argument('output');p.add_argument('--sidecar')
    p=sub.add_parser('candidate');p.add_argument('project');p.add_argument('cel_id');p.add_argument('png');p.add_argument('mask');p.add_argument('transaction_output')
    p=sub.add_parser('replay');p.add_argument('project');p.add_argument('journal');p.add_argument('output')
    a=parser.parse_args()
    try:
        if a.command=='ora-import':write(a.output,import_ora(a.ora));return
        if a.command=='ase-import':write(a.output,import_aseprite(a.ase,a.sidecar));return
        project=load_json(Path(a.project).read_text());validate_project(project)
        if a.command in ['hash','validate']:print(project_hash(project))
        elif a.command=='apply':
            result=apply_transaction(project,load_json(Path(a.transaction).read_text()));require_paths=[Path(a.output).resolve(),Path(a.receipt).resolve()]
            if require_paths[0]==require_paths[1]:raise EditError('Project and receipt outputs must differ')
            write(a.receipt,result['receipt']);write(a.output,result['project']);print(result['receipt']['after_sha256'])
        elif a.command=='export':print(json.dumps(export_project(project,a.directory,a.columns)))
        elif a.command=='ora-export':print(json.dumps(export_ora(project,a.frame_id,a.output)))
        elif a.command=='ase-export':print(json.dumps(export_aseprite(project,a.output,a.animation,a.sidecar)))
        elif a.command=='candidate':
            from PIL import Image
            write(a.transaction_output,candidate_transaction(project,a.cel_id,Image.open(a.png),load_json(Path(a.mask).read_text())))
        elif a.command=='replay':write(a.output,History.replay(project,load_json(Path(a.journal).read_text())).project)
    except (ValueError,KeyError,TypeError,OSError)as error:
        print('Rejected: '+str(error),file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())

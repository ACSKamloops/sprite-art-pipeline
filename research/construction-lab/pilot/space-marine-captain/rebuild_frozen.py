"""Reproduce frozen assembly with legacy construction writes isolated.

The exact historical assembler and upper builder are used unchanged. Their
generated-part writes go to a private temporary source snapshot, never the
frozen source tree. Keep each requested output directory new.
"""
from pathlib import Path
import argparse, importlib.util, shutil, sys, tempfile

HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--legs',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Use a fresh candidate directory')
    with tempfile.TemporaryDirectory(prefix='captain-frozen-source-')as td:
        snapshot=Path(td)
        shutil.copytree(HERE/'upper-body-rig-v1',snapshot/'upper-body-rig-v1')
        shutil.copytree(HERE/'references',snapshot/'references')
        spec=importlib.util.spec_from_file_location('frozen_assembly',HERE/'assemble.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.ROOT=snapshot
        sys.argv=[str(HERE/'assemble.py'),'--legs',str(a.legs),'--output',str(a.output.resolve()),
                  '--upper-rotation','scale2x8-approximation','--upper-motion','weighted','--inline-foreground']
        module.main()


if __name__=='__main__':main()

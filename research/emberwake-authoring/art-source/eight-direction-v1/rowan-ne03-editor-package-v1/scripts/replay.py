"""Copy only portable inputs/toolkit/scripts to a fresh root and run real replay."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path
from common import ROOT,sha,write,verify_inputs

def main(out,binary):
    verify_inputs();assert out.is_absolute()and not out.exists();out.mkdir(parents=True)
    for folder in ['inputs','retained-source','scripts','docs']:
        shutil.copytree(ROOT/folder,out/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ['INPUTS.json','EXPECTED.json','INTAKE.md','README.md']:
        if(ROOT/name).is_file():shutil.copy2(ROOT/name,out/name)
    commands=[]
    for args in [['scripts/build_editor.py'],['scripts/native_exchange.py']+(['--libresprite',binary]if binary else[])]:
        cmd=[sys.executable,'-B']+args;r=subprocess.run(cmd,cwd=out,text=True,capture_output=True)
        commands.append({'argv':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        if r.returncode:
            write(out/'REPLAY-FAILURE.json',{'commands':commands});raise RuntimeError('Fresh-root replay failed; retained output '+str(out))
    editor=json.loads((out/'verification/EDITOR-RECEIPT.json').read_text());native=json.loads((out/'verification/NATIVE-RECEIPT.json').read_text())
    if(ROOT/'EXPECTED.json').exists():
        expected=json.loads((ROOT/'EXPECTED.json').read_text())
        for field in ['initial_project_sha256','after_import_project_sha256','final_project_sha256']:assert editor[field]==expected[field]
        for f in expected['frames']:assert sha(out/f'editor-render/{f["phase"]:02}.png')==f['sha256']
    write(out/'FRESH-ROOT-REPLAY.json',{'status':'PASS actual portable source/editor/native replay','commands':commands,'final_project_sha256':editor['final_project_sha256'],'two_guarded_transactions':editor['actual_transactions'],'all8_RGBA_PNG_exact':True,'actual_LibreSprite_roundtrip_exact':native['whole_project_reimport_exact'],'model_calls':0,'canonical_writes':0,'normal_speed_acceptance':False})
    print('PASS fresh-root source/editor/native replay:',out)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--libresprite');a=ap.parse_args();main(a.output,a.libresprite)

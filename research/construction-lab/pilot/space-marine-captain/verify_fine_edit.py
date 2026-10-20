"""Run the actual pixel-editor fixture against a declared frozen project."""
from pathlib import Path
import argparse, hashlib, json, subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
CLI='/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--editable',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Keep prior edit receipts frozen')
    a.output.mkdir(parents=True)
    source=a.editable.resolve()/'project.json';before=sha(source)
    script=HERE/'verify_fine_edit.js'
    js=script.read_text().replace('__OUTPUT_DIR__',json.dumps(str(a.output.resolve())+'/')).replace('__EDITABLE_PROJECT__',json.dumps(str(source)))
    result=subprocess.run([CLI,'--session','captain-fine-editor','run-code',js],cwd=ROOT,capture_output=True,text=True)
    (a.output/'tool.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and '### Error'not in result.stdout,result.stdout[:1000]
    receipt_path=a.output/'receipt.json';receipt=json.loads(receipt_path.read_text())
    assert receipt['passed'] and receipt['restored_original'] and sha(source)==before
    assert receipt['initial_hash']==json.loads((a.editable/'receipt.json').read_text())['project_sha256']
    receipt['frozen_source_file_sha256']=before
    receipt['fixture_js_sha256']=sha(script)
    receipt['editor_code_sha256']={p.name:sha(p)for p in [ROOT/'editor/app.js',ROOT/'editor/pixels.js']}
    receipt['actual_editor_screenshot_sha256']=sha(a.output/'actual-editor.png')
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'passed':receipt['passed'],'source_unchanged':True,'load_ms':receipt['load_ms'],'edit_ms':receipt['edit_ms'],'output':str(a.output)}))


if __name__=='__main__':main()

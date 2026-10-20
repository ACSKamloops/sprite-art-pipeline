"""Reopen/save/render the complete layered animation in actual LibreSprite."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, subprocess, sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from sprite_lab import import_aseprite, project_hash


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--editable',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve editor proof outputs')
    a.output.mkdir(parents=True)
    original=a.editable/'captain-walk.aseprite';saved=a.output/'actual-tool-reopened.aseprite'
    sheet=a.output/'actual-tool.png';data=a.output/'actual-tool.json'
    result=subprocess.run(['libresprite','-b','--list-layers',str(original),
                           '--save-as',str(saved),'--sheet',str(sheet),'--sheet-type','horizontal',
                           '--data',str(data),'--format','json-array'],capture_output=True,text=True)
    (a.output/'tool.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stderr[:1000]
    manifest=json.loads((a.candidate/'manifest.json').read_text());tool=json.loads(data.read_text())
    atlas=Image.open(sheet).convert('RGBA');rows=tool['frames'];assert len(rows)==len(manifest['frames'])==72
    holds=[];raster_hashes=[]
    for row,frame in zip(rows,manifest['frames']):
        rect=row['frame'];assert (rect['w'],rect['h'])==(256,256)
        image=atlas.crop((rect['x'],rect['y'],rect['x']+256,rect['y']+256))
        assert image.tobytes()==Image.open(a.candidate/frame['file']).convert('RGBA').tobytes()
        assert abs(row['duration']-frame['duration_ms'])<=.5
        holds.append(row['duration']);raster_hashes.append(hashlib.sha256(image.tobytes()).hexdigest())
    assert sum(holds)==round(manifest['cycle_ms'])
    assert len(tool['meta']['layers'])==len(manifest['layer_order'])==9
    sidecar=Path(str(original)+'.sprite-lab.json')
    project=import_aseprite(saved,sidecar)
    original_receipt=json.loads((a.editable/'receipt.json').read_text())
    assert project_hash(project)==original_receipt['project_sha256']
    receipt={'candidate_manifest_sha256':hashlib.sha256((a.candidate/'manifest.json').read_bytes()).hexdigest(),
             'all72_actual_tool_composites_exact_RGBA':True,'actual_tool_layers':[r['name']for r in tool['meta']['layers']],
             'actual_tool_holds_ms':holds,'actual_tool_cycle_ms':sum(holds),
             'lossless_project_reimport_sha256':project_hash(project),
             'saved_tool_file_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),
             'actual_tool_RGBA_hashes':raster_hashes,
             'scope':'Actual LibreSprite batch reopen/save/render plus lossless sidecar reimport; no art score'}
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k]for k in ['all72_actual_tool_composites_exact_RGBA','actual_tool_cycle_ms','lossless_project_reimport_sha256']}))


if __name__=='__main__':main()

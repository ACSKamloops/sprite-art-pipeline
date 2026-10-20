#!/usr/bin/env python3
"""Replay the real five-pixel eye correction using the installed toolkit API."""
from pathlib import Path
import hashlib,json,sys,importlib.util,argparse,shutil,subprocess
from PIL import Image
import numpy as np
INPUT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True,type=Path);args=parser.parse_args();BASE=args.out
assert not BASE.exists(),'Output must be a fresh directory';BASE.mkdir(parents=True)
for name in ['construction-spec.json','source-a.png','source-b.png','eye-journal.json','22.png']:shutil.copyfile(INPUT/name,BASE/name)
TOOL=INPUT.parent/'editor-toolkit-v1'
sys.path.insert(0,str(TOOL))
from sprite_lab import History,canonical_json,project_hash,render_frame,export_project
from sprite_lab.aseprite import export_aseprite,import_aseprite
loader=importlib.util.spec_from_file_location('construct',TOOL/'scripts/sprite_construct.py');module=importlib.util.module_from_spec(loader);loader.loader.exec_module(module)
source=module.construct(BASE/'construction-spec.json');history=History(source)
journal=json.loads((BASE/'eye-journal.json').read_text());palette=[list(c) for c in source['palette']];operations=[]
for item in journal['changes']:
    color=item['after']
    if color not in palette:
        operations.append({'op':'palette_add','rgba':color});palette.append(color)
for frame,dy in [('idle-a',0),('idle-b',-1)]:
    cel=next(f for f in source['frames'] if f['id']==frame)['cels']['body']
    points=[[p['xy'][0],p['xy'][1]+dy,palette.index(p['after'])] for p in journal['changes']]
    operations.append({'op':'paint','cel_id':cel,'points':points,'mask':[p[:2] for p in points]})
tx={'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(source),'reason':'Restore consistent neutral eye whites from the actual same-view donor; all other pixels and 29/50s holds protected.','operations':operations}
receipt=history.apply(tx);edited=history.project
assert project_hash(history.undo())==project_hash(source)
assert project_hash(history.redo())==project_hash(edited)
replayed=History.replay(source,history.journal()).project
assert project_hash(replayed)==project_hash(edited)
for frame,expected in [('idle-a',BASE/'22.png'),('idle-b',INPUT.parent/'breath-v2/brann/southeast/23.png')]:
    np.testing.assert_array_equal(np.array(render_frame(edited,frame)),np.array(Image.open(expected).convert('RGBA')))
for name,obj in [('source-project.json',source),('edited-project.json',edited),('toolkit-journal.json',history.journal()),('toolkit-receipt.json',receipt)]:
    (BASE/name).write_text(canonical_json(obj)+'\n')
export_project(edited,BASE/'editor-export',columns=2)
export_aseprite(edited,BASE/'brann-idle.aseprite',animation_id='southeast_idle')
proof={'source_project_sha256':project_hash(source),'edited_project_sha256':project_hash(edited),'undo_exact':True,'redo_exact':True,'journal_replay_exact':True,'actual_eye_pixels_per_frame':5,'all_other_rgba_exact':True,'two_frame_rgba_match_runtime_candidates':True,'external_tool_exchange':None}
subprocess.run(['libresprite','-b',str(BASE/'brann-idle.aseprite'),'--save-as',str(BASE/'external.aseprite')],check=True,stdout=subprocess.DEVNULL)
imported=import_aseprite(BASE/'external.aseprite',BASE/'brann-idle.aseprite.sprite-lab.json');assert project_hash(imported)==project_hash(edited)
for fid in ['idle-a','idle-b']:np.testing.assert_array_equal(np.array(render_frame(imported,fid)),np.array(render_frame(edited,fid)))
proof['external_tool_exchange']={'tool':'LibreSprite','actual_batch_save_reopen':True,'imported_project_hash_exact':True,'two_frames_rgba_exact':True,'external_ase_sha256':hashlib.sha256((BASE/'external.aseprite').read_bytes()).hexdigest()}
(BASE/'editor-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))

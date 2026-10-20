"""Verify actual LibreSprite1.3 saved/reopened artifacts against frozen8RGBA.
Native milliseconds are exchange preview; exact clock remains9/160s percel.
"""
from pathlib import Path
import json,sys,hashlib
sys.dont_write_bytecode=True
from PIL import Image
from sprite_lab import load_json,project_hash,import_aseprite,render_frame
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
final=load_json((R/'projects/final.json').read_text());native=R/'native';sidecar=native/'Brann-SE-weight.aseprite.sprite-lab.json';expectedms=[56,57,56,56,56,57,56,56];reports=[]
for stage,ase,sheet,data in [('save','Brann-SE-weight-resaved.aseprite','libresprite-first.png','libresprite-first.json'),('reopen','Brann-SE-weight-reopened.aseprite','libresprite-reopened.png','libresprite-reopened.json')]:
 assert all((native/f).exists()for f in[ase,sheet,data]);atlas=Image.open(native/sheet).convert('RGBA');meta=load_json((native/data).read_text());assert atlas.size==(1024,128);assert len(meta['frames'])==8;assert[f['duration']for f in meta['frames']]==expectedms
 cells=[]
 for i,f in enumerate(meta['frames']):
  rect=f['frame'];assert not f['trimmed']and not f['rotated'];im=atlas.crop((rect['x'],rect['y'],rect['x']+rect['w'],rect['y']+rect['h']));target=R/'frames'/f'{i:02}.png';assert im.tobytes()==Image.open(target).convert('RGBA').tobytes();p=native/f'{stage}-sheet-frames'/f'{i:02}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p);assert p.read_bytes()==target.read_bytes();cells.append({'phase':i,'RGBA_exact':True,'PNG_bytes_exact':True,'RGBA_sha256':hashlib.sha256(im.tobytes()).hexdigest()})
 project=import_aseprite(native/ase,sidecar);assert project_hash(project)==project_hash(final);save(native/f'{stage}-reimported-project.json',project)
 for i in range(8):assert render_frame(project,f'brann-se-{i:02}').tobytes()==Image.open(R/'frames'/f'{i:02}.png').convert('RGBA').tobytes()
 reports.append({'stage':stage,'ase_file':ase,'ase_sha256':sha(native/ase),'tool_sheet':sheet,'tool_sheet_sha256':sha(native/sheet),'full_project_reimport_exact':True,'project_sha256':project_hash(project),'frames':cells})
receipt={'status':'PASS actual LibreSprite1.3 batch save,then actual reopen/render; all16 tool-rendered cels exact RGBA+PNG and both reimported projects exact','representation':'one normal flattened RGBA paint layer per phase; retained upstream construction layers/maps separate','binary_version':'LibreSprite1.3 (actual --version checked)','actual_commands':[['libresprite','-b','--list-layers','native/Brann-SE-weight.aseprite','--save-as','native/Brann-SE-weight-resaved.aseprite','--sheet','native/libresprite-first.png','--sheet-type','horizontal','--data','native/libresprite-first.json','--format','json-array'],['libresprite','-b','--list-layers','native/Brann-SE-weight-resaved.aseprite','--save-as','native/Brann-SE-weight-reopened.aseprite','--sheet','native/libresprite-reopened.png','--sheet-type','horizontal','--data','native/libresprite-reopened.json','--format','json-array']],'quantized_native_preview_ms':expectedms,'native_preview_total_ms':sum(expectedms),'authoritative_clock':{'holds':[[9,160]]*8,'total':[9,20]},'no_art_acceptance_claim':True,'results':reports}
save(native/'LIBRESPRITE-RECEIPT.json',receipt);print(json.dumps({'LibreSprite_saved_reopened_all16_rendered_RGBA_and_PNG_exact':True,'both_project_reimports_exact':True,'receipt':'native/LIBRESPRITE-RECEIPT.json'},indent=2))

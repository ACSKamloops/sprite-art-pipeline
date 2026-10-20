"""Fresh-output native part transfer, integer source-map and guarded editor replay."""
from pathlib import Path
import argparse,json,hashlib,shutil
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel
R=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(R/n).convert('RGBA'))
def m(n):return np.array(Image.open(R/n))>0
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent directory required';out.mkdir(parents=True)
 for n in ['constructed','editor-replay']:(out/n).mkdir()
 base=a('inputs/authority/03.png');owner=m('masks/03-proximal-trouser-owner.png');protected=m('masks/03-upper-arms-complete-boots-protected.png');cfg=json.loads((R/'CONSTRUCTION.json').read_text());donor={i:a(f'inputs/authority/{i:02}.png') for i in [0,2,3,4]}
 constructed=base.copy();constructed[owner]=0
 for lid,c in enumerate(cfg['source_part_transfers'],2):
  source=m(f'inputs/donor-owners/{lid}-source.png');dx,dy=c['native_translation'];paint=donor[c['source_phase']]
  for y,x in np.argwhere(source):
   xx,yy=x+dx,y+dy
   if 0<=xx<128 and 0<=yy<128 and owner[yy,xx]:constructed[yy,xx]=paint[y,x]
 constructed[protected]=base[protected]
 z=np.load(R/'maps/03-source-map.npz');mapped=np.zeros_like(base)
 for y,x in np.argwhere(z['source_phase']>=0):sp=int(z['source_phase'][y,x]);sx,sy=z['source_xy'][y,x];mapped[y,x]=donor[sp][sy,sx]
 expected=a('candidate/03.png');assert np.array_equal(constructed,expected);assert np.array_equal(mapped,expected);assert np.array_equal(expected[protected],base[protected]);assert np.array_equal(expected[~owner],base[~owner]);Image.fromarray(mapped).save(out/'03-source-map.png')
 # Prove both whole fixed03boots against actual02source paint and its exact original native translations.
 boot_rows=[]
 for name,dx,dy in [('screen-left-descending',3,7),('screen-right-retreating',-2,-6)]:
  mask=m(f'inputs/ownership/{name}-complete-boot-source.png')
  for sy,sx in np.argwhere(mask):assert np.array_equal(expected[sy+dy,sx+dx],donor[2][sy,sx])
  boot_rows.append({'name':name,'source_phase':2,'unchanged_native_translation':[dx,dy],'all_source_boot_RGBA_and_alpha_exact':True,'source_pixels':int(mask.sum())})
 initial=json.loads((R/'projects/initial.json').read_text());h=History.replay(initial,json.loads((R/'projects/journal.json').read_text()));assert project_hash(h.project)==project_hash(json.loads((R/'projects/final.json').read_text()));rows=[]
 for i in range(8):
  im=constructed if i==3 else a(f'inputs/authority/{i:02}.png');wanted=a(f'candidate/{i:02}.png');edited=render_cel(h.project,f'rowan-se-{i:02}');assert np.array_equal(im,wanted);assert edited.tobytes()==wanted.tobytes()
  if i==3:Image.fromarray(im).save(out/'constructed'/f'{i:02}.png')
  else:shutil.copy2(R/'inputs/authority'/f'{i:02}.png',out/'constructed'/f'{i:02}.png')
  edited.save(out/'editor-replay'/f'{i:02}.png');rows.append({'phase':i,'construction_RGBA_exact':True,'editor_RGBA_exact':True,'construction_PNG_byte_exact':sha(out/'constructed'/f'{i:02}.png')==sha(R/'candidate'/f'{i:02}.png'),'editor_PNG_byte_exact':sha(out/'editor-replay'/f'{i:02}.png')==sha(R/'candidate'/f'{i:02}.png'),'sha256':sha(R/'candidate'/f'{i:02}.png'),'hold':[9,160]})
 final_hash=project_hash(h.project);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==final_hash
 receipt={'fresh_output':str(out),'external_artifact_dependencies':[],'model_calls':0,'new_authored_pixels':0,'procedural_constructed_frames':8,'independent_editor_journal_frames':8,'compiled_source_map_RGBA_exact':True,'actual_guarded_editor_transactions':1,'actual_undo_redo':True,'both_complete03boots':boot_rows,'other7untouched':True,'rows':rows,'cycle':[9,20]}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

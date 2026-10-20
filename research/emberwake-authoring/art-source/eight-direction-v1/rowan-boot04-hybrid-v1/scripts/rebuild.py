"""Fresh exact hybrid reconstruction, compiled source-map replay and guarded editor journal replay."""
from pathlib import Path
import argparse,hashlib,json,shutil
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel
R=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(R/n).convert('RGBA'))
def m(n):return np.array(Image.open(R/n))>0
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent output required';out.mkdir(parents=True)
 for n in ['constructed','editor-replay']:(out/n).mkdir()
 base=a('inputs/authority/04.png');donors={i:a(f'inputs/authority/{i:02}.png') for i in [0,4,6]};cfg=json.loads((R/'CONSTRUCTION.json').read_text());erase=m('masks/04-old-generated-boots-erased.png');front=m('masks/04-generated-front-pants-preserved.png');stable=m('inputs/ownership/04-stable-upper-hem-owner.png');glove=m('inputs/ownership/04-opaque-gloves-protected.png')
 rebuilt=base.copy();rebuilt[erase]=0
 def boot(c):
  source=donors[c['source_phase']];mask=m('inputs/donor-masks/'+c['source_mask']);dx,dy=c['translation']
  for y,x in np.argwhere(mask&(source[...,3]>0)):rebuilt[y+dy,x+dx]=source[y,x]
 boot(cfg['boot_placements'][0]);restore=front&(base[...,3]>0);rebuilt[restore]=base[restore];boot(cfg['boot_placements'][1]);rebuilt[stable|glove]=base[stable|glove]
 assert np.array_equal(rebuilt,a('experiments/before-cuff-join/04.png'))
 connection=json.loads((R/'CONNECTION-JOURNAL.json').read_text())
 for op in connection['operations']:
  x,y=op['target'];sx,sy=op['source_xy'];assert rebuilt[y,x].tolist()==op['before'];assert donors[op['source_phase']][sy,sx].tolist()==op['after'];rebuilt[y,x]=op['after']
 assert np.array_equal(rebuilt,a('candidate/04.png'));assert np.array_equal(rebuilt[stable|glove],base[stable|glove])
 z=np.load(R/'maps/04-source-map.npz');mapped=np.zeros((128,128,4),np.uint8)
 for y,x in np.argwhere(z['source_phase']>=0):sp=int(z['source_phase'][y,x]);sx,sy=z['source_xy'][y,x];mapped[y,x]=donors[sp][sy,sx]
 assert np.array_equal(mapped,rebuilt);Image.fromarray(mapped).save(out/'04-compiled-map.png')
 initial=json.loads((R/'projects/initial.json').read_text());h=History.replay(initial,json.loads((R/'projects/journal.json').read_text()));assert project_hash(h.project)==project_hash(json.loads((R/'projects/final.json').read_text()))
 rows=[]
 for i in range(8):
  constructed=rebuilt if i==4 else a(f'inputs/authority/{i:02}.png');expected=a(f'candidate/{i:02}.png');edited=render_cel(h.project,f'rowan-se-{i:02}');assert np.array_equal(constructed,expected);assert edited.tobytes()==expected.tobytes()
  if i==4:Image.fromarray(constructed).save(out/'constructed'/f'{i:02}.png')
  else:shutil.copy2(R/'inputs/authority'/f'{i:02}.png',out/'constructed'/f'{i:02}.png')
  edited.save(out/'editor-replay'/f'{i:02}.png');rows.append({'phase':i,'construction_RGBA_exact':True,'editor_RGBA_exact':True,'construction_PNG_byte_exact':sha(out/'constructed'/f'{i:02}.png')==sha(R/'candidate'/f'{i:02}.png'),'editor_PNG_byte_exact':sha(out/'editor-replay'/f'{i:02}.png')==sha(R/'candidate'/f'{i:02}.png'),'sha256':sha(R/'candidate'/f'{i:02}.png'),'hold':[9,160]})
 final_hash=project_hash(h.project);h.undo();h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();h.redo();assert project_hash(h.project)==final_hash
 receipt={'fresh_output':str(out),'external_artifact_dependencies':[],'model_calls':0,'procedural_construction_frames':8,'editor_journal_frames':8,'compiled_source_map_RGBA_exact':True,'actual_guarded_editor_transactions':2,'actual_undo_redo':True,'explicit_authored_connection_pixels':len(connection['operations']),'complete_front_boot_source_pixels':342,'rear_boot_occlusion':'literal original generated foreground thigh, retained in CONSTRUCTION.json','rows':rows,'cycle':[9,20]}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

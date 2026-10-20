"""Independent saved-map/visible-source compositor and guarded editor replay. No generation or outside artwork."""
from pathlib import Path
import argparse,json,hashlib,shutil
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel,load_json
ROOT=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(ROOT/n).convert('RGBA'))
def m(n):return np.array(Image.open(ROOT/n).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent output path required';out.mkdir(parents=True)
 for n in ['source-map','journal-replay','layers']:(out/n).mkdir()
 intake=load_json((ROOT/'INTAKE.json').read_text())
 for item in intake['files']:assert sha(ROOT/item['file'])==item['sha256'],item['file']
 extra=load_json((ROOT/'SOURCE-PART-INPUT-RECEIPT.json').read_text())
 for item in extra['supplemental_actual_inputs_copied_after_initial_cycle_intake']:assert sha(ROOT/item['file'])==item['sha256'],item['file']
 sources={6:a('inputs/source06.png'),7:a('inputs/original07.png')};layers={};counts={}
 bindings=[('left-complete06-boot',6),('right-complete07-boot',7),('left-proximal06',6),('right-bent06-unbending',6)]
 for name,sid in bindings:
  maps=np.load(ROOT/f'maps/{name}.npz',allow_pickle=False);layer=np.zeros((128,128,4),np.uint8)
  for y,x in np.argwhere(maps['owner']):
   sx,sy=map(int,maps['source_xy'][y,x]);assert 0<=sx<128 and 0<=sy<128;layer[y,x]=sources[sid][sy,sx]
  assert np.array_equal(layer,a(f'source-parts/{name}.png'));layers[name]=layer;counts[name]=int(maps['owner'].sum());Image.fromarray(layer).save(out/'layers'/f'{name}.png')
 hip=m('masks/07-actual-hipcap-owner.png');assert int(hip.sum())==117;hiplayer=np.zeros((128,128,4),np.uint8);hiplayer[hip]=sources[7][hip];assert np.array_equal(hiplayer,a('source-parts/actual07-hipcap.png'));layers['actual07-hipcap']=hiplayer
 recipe=load_json((ROOT/'maps/COMPOSITION.json').read_text());lower=np.zeros((128,128,4),np.uint8)
 # Scalar integer source-over is independent of the producer's vector implementation.
 for name in recipe['layer_order']:
  fg=layers[name]
  for y,x in np.argwhere(fg[...,3]>0):
   sr,sg,sb,sa=map(int,fg[y,x]);dr,dg,db,da=map(int,lower[y,x]);N=sa*255+da*(255-sa)
   lower[y,x]=[(s*sa*255+d*da*(255-sa)+N//2)//N for s,d in [(sr,dr),(sg,dg),(sb,db)]]+[(N+127)//255]
 base=a('inputs/cycle/07.png');repair=m('masks/07-lower-repair-owner.png');upper=m('inputs/masks/07-stable-upper-hem-owner.png');gloves=m('inputs/masks/07-opaque-gloves-protected.png');rebuilt=base.copy();rebuilt[repair]=0;rebuilt[repair]=lower[repair];rebuilt[upper|gloves]=base[upper|gloves];rebuilt[rebuilt[...,3]==0]=0
 assert np.array_equal(rebuilt,a('candidate/07.png'));assert np.array_equal(rebuilt[~repair],base[~repair]);assert np.array_equal(rebuilt[upper|gloves],base[upper|gloves]);expected='9b62df0f5faf9bb22a2e8c1e4bdddf9c3f359ad5fbaa01bd6a1348d0b796a618';assert sha(ROOT/'candidate/07.png')==expected
 initial=load_json((ROOT/'projects/initial.json').read_text());journal=load_json((ROOT/'projects/journal.json').read_text());final=load_json((ROOT/'projects/final.json').read_text());h=History.replay(initial,journal);assert project_hash(h.project)==project_hash(final)
 rows=[]
 for i in range(8):
  selected=a(f'candidate/{i:02}.png');constructed=rebuilt if i==7 else a(f'inputs/cycle/{i:02}.png');rendered=np.array(render_cel(h.project,f'rowan-se-{i:02}'));assert np.array_equal(constructed,selected);assert np.array_equal(rendered,selected)
  if i==7:Image.fromarray(constructed).save(out/'source-map'/f'{i:02}.png')
  else:shutil.copy2(ROOT/'inputs/cycle'/f'{i:02}.png',out/'source-map'/f'{i:02}.png')
  Image.fromarray(rendered).save(out/'journal-replay'/f'{i:02}.png');rows.append({'phase':i,'source_map_RGBA_exact':True,'journal_RGBA_exact':True,'source_map_PNG_bytes_exact':sha(out/'source-map'/f'{i:02}.png')==sha(ROOT/'candidate'/f'{i:02}.png'),'journal_PNG_bytes_exact':sha(out/'journal-replay'/f'{i:02}.png')==sha(ROOT/'candidate'/f'{i:02}.png'),'candidate_sha256':sha(ROOT/'candidate'/f'{i:02}.png'),'hold':[9,160]})
 finalhash=project_hash(h.project);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==finalhash
 report={'status':'PASS visible-source map construction and actual guarded editor replay','candidate07_sha256':expected,'new_authored_transition_not_recovered_hidden_anatomy':True,'hip_underpaint_pixels':117,'source_layer_pixel_counts':counts,'source_over_scalar_replay_RGBA_exact':True,'all8_source_map_RGBA_exact':True,'all8_journal_RGBA_exact':True,'actual_guarded_transactions':1,'undo_redo_exact':True,'external_artwork_dependencies':[],'generation_calls':0,'other7_PNG_bytes_exact':all((ROOT/'candidate'/f'{i:02}.png').read_bytes()==(ROOT/'inputs/cycle'/f'{i:02}.png').read_bytes() for i in range(7)),'frames':rows,'stage':[128,128],'pivot':[64,112],'hold':[9,160],'cycle':[9,20],'external_GUI_tested':False,'runtime_tested':False,'art_selection':'unselected pending fresh comparison'}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()

"""Reconstruct the frozen07 boot hybrid from local source maps and independently replay its editor journal."""
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
 for name in ['constructed','journal-replay']:(out/name).mkdir()
 intake=load_json((ROOT/'INTAKE.json').read_text())
 for item in intake['inputs']:assert sha(ROOT/item['file'])==item['sha256'],item['file']
 base=a('inputs/generated07.png');src=a('inputs/A/07.png');repair=m('proposal/07-boot-repair-owner.png');knees=m('proposal/07-generated-knee-protected.png');upper=m('inputs/masks/07-stable-upper-hem-owner.png');gloves=m('inputs/masks/07-opaque-gloves-protected.png');maps=np.load(ROOT/'maps/07-boot-source.npz',allow_pickle=False)
 rebuilt=base.copy();rebuilt[repair]=0;before_cuff=rebuilt.copy();counts={}
 for ident in [1,2,3]:
  owner=maps['source_id']==ident;counts[str(ident)]=int(owner.sum())
  for y,x in np.argwhere(owner):
   sx,sy=map(int,maps['source_xy'][y,x]);assert 0<=sx<128 and 0<=sy<128
   if ident==1:assert [x,y]==[sx+2,sy+2]
   if ident==2:assert [x,y]==[sx,sy-2]
   rebuilt[y,x]=src[sy,sx]
   if ident<3:before_cuff[y,x]=src[sy,sx]
 assert np.array_equal(before_cuff,a('proposal/07-before-cuff.png'));assert np.array_equal(rebuilt,a('proposal/07.png'));assert sha(ROOT/'proposal/07.png')=='0fef5fddaf1a590a5bd655c1f2ebc5527617b1d6bdb21360dbf7769f78d77a30'
 for protected in [knees,upper,gloves,~repair]:assert np.array_equal(rebuilt[protected],base[protected])
 edits=load_json((ROOT/'proposal/cuff-source-edits.json').read_text())['actual_edits'];assert len(edits)==35 and counts['3']==35
 for row in edits:
  x,y=row['at'];sx,sy=row['source_at'];assert maps['source_id'][y,x]==3 and list(maps['source_xy'][y,x])==[sx,sy];assert before_cuff[y,x,3]==0;assert np.array_equal(rebuilt[y,x],src[sy,sx])
 initial=load_json((ROOT/'projects/initial.json').read_text());journal=load_json((ROOT/'projects/journal.json').read_text());final=load_json((ROOT/'projects/final.json').read_text());h=History.replay(initial,journal);assert project_hash(h.project)==project_hash(final);assert len(journal['receipts'])==2
 rows=[]
 for i in range(8):
  expected=a(f'preview/frames/{i:02}.png');constructed=rebuilt if i==7 else a(f'preview/control-frames/{i:02}.png');rendered=np.array(render_cel(h.project,f'rowan-se-{i:02}'));assert np.array_equal(constructed,expected);assert np.array_equal(rendered,expected)
  if i==7:Image.fromarray(constructed).save(out/'constructed'/f'{i:02}.png')
  else:shutil.copy2(ROOT/'preview/control-frames'/f'{i:02}.png',out/'constructed'/f'{i:02}.png')
  Image.fromarray(rendered).save(out/'journal-replay'/f'{i:02}.png')
  rows.append({'phase':i,'source_map_RGBA_exact':True,'journal_RGBA_exact':True,'construction_PNG_bytes_exact':sha(out/'constructed'/f'{i:02}.png')==sha(ROOT/'preview/frames'/f'{i:02}.png'),'journal_PNG_bytes_exact':sha(out/'journal-replay'/f'{i:02}.png')==sha(ROOT/'preview/frames'/f'{i:02}.png'),'sha256':sha(ROOT/'preview/frames'/f'{i:02}.png'),'hold':[9,160]})
 finalhash=project_hash(h.project);h.undo();assert render_cel(h.project,'rowan-se-07').tobytes()==Image.open(ROOT/'proposal/07-before-cuff.png').convert('RGBA').tobytes();h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();h.redo();assert project_hash(h.project)==finalhash
 receipt={'status':'PASS independent source-part-map and guarded editor replay','external_artwork_dependencies':[],'generation_calls':0,'exact_candidate07_sha256':sha(ROOT/'proposal/07.png'),'actual_guarded_transactions':2,'actual_source_colored_cuff_strokes':35,'map_source_pixel_counts':counts,'all8_source_map_RGBA_exact':True,'all8_journal_RGBA_exact':True,'all_generated_cream_knees_upper_hem_gloves_exact':True,'two_step_undo_redo_exact':True,'outside_mask_guard_rejection_previously_verified':'projects/EDITOR-RECEIPT.json','frames':rows,'stage':[128,128],'pivot':[64,112],'hold':[9,160],'cycle':[9,20],'external_GUI_tested':False,'game_runtime_tested':False,'art_acceptance':'unselected pending parent fullcycle review'}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

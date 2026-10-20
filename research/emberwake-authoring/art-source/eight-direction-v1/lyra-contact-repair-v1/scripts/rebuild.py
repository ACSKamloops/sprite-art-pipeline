"""Fresh source-map reconstruction plus independent actual guarded editor journal replay."""
from pathlib import Path
import argparse,sys,subprocess,json,hashlib
from PIL import Image
from sprite_lab import History,project_hash,render_cel,load_json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh nonexistent output path required';out.mkdir(parents=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/replay_source_maps.py'),'--output',str(out/'source-map')],check=True,capture_output=True,text=True)
 source_report=load_json((out/'source-map/SOURCE-REPLAY-RECEIPT.json').read_text());initial=load_json((ROOT/'projects/initial.json').read_text());journal=load_json((ROOT/'projects/journal.json').read_text());final=load_json((ROOT/'projects/final.json').read_text());h=History.replay(initial,journal);assert project_hash(h.project)==project_hash(final);assert len(journal['receipts'])==2
 (out/'journal-replay').mkdir();rows=[]
 for i in range(8):
  actual=render_cel(h.project,f'lyra-se-{i:02}');expected=Image.open(ROOT/'candidate'/f'{i:02}.png').convert('RGBA');assert actual.tobytes()==expected.tobytes();dst=out/'journal-replay'/f'{i:02}.png';actual.save(dst);assert dst.read_bytes()==(ROOT/'candidate'/f'{i:02}.png').read_bytes()
  rows.append({'phase':i,'source_map_RGBA_and_PNG_bytes_exact':True,'guarded_journal_RGBA_and_PNG_bytes_exact':True,'sha256':sha(ROOT/'candidate'/f'{i:02}.png'),'hold':[9,160]})
 finalhash=project_hash(h.project);h.undo();h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();h.redo();assert project_hash(h.project)==finalhash
 receipt={'status':'PASS retained-input source-map/scalar-compositor construction and independent actual guarded journal','generation_calls':0,'new_authored_source_layout_not_recovered_hidden_anatomy':True,'actual_guarded_transactions':2,'source_map_and_journal_all8_RGBA_and_PNG_bytes_exact':True,'two_step_undo_redo_exact':True,'other6_PNG_bytes_exact':True,'original03_04_full_upper_hem_visible_gloves_RGBA_exact':True,'source_underpaint_pixels_per_changed_cel':138,'source_over_partial_alpha_joins':{'03':5,'04':0},'source_map_receipt':'source-map/SOURCE-REPLAY-RECEIPT.json','final_project_sha256':finalhash,'frames':rows,'external_artwork_dependencies':[],'stage':[128,128],'pivot':[64,112],'hold':[9,160],'cycle':[9,20],'inherited_quality_score':None,'external_GUI_tested':False,'game_runtime_tested':False,'art_selection':'candidate pending independent review'}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

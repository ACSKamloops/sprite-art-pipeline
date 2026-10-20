"""Freeze the exact inspected source05 projected foreleg; do not change pixels."""
from pathlib import Path
import copy,json
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,candidate_transaction,render_cel
R=Path(__file__).resolve().parents[1]
def im(bank,i):return Image.open(R/bank/f'{i:02}.png').convert('RGBA')
def dump(p,data):p.write_text(json.dumps(data,separators=(',',':'))+'\n')
def main():
 out=R/'projects';assert not out.exists();out.mkdir()
 palette=[[0,0,0,0]];lookup={(0,0,0,0):0}
 for bank in ['inputs/control','preview-v1/frames']:
  for i in range(8):
   for c in im(bank,i).get_flattened_data():
    if c not in lookup:lookup[c]=len(palette);palette.append(list(c))
 project={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'paint','name':'Complete frozen painted cels; foreleg maps retained separately','locked':False}],'cels':{f'f{i:02}':{'layer_id':'paint','pixels':[lookup[c]for c in im('inputs/control',i).get_flattened_data()]}for i in range(8)},'frames':[{'id':f'f{i:02}','duration_ticks':9,'cels':{'paint':f'f{i:02}'},'landmarks':{'pivot':[64,112]}}for i in range(8)],'animations':[{'id':'walk','frames':[f'f{i:02}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'source':'inputs/control/00..07.png','projection':'preview-v1/maps/05-projection.npz','status':'Unselected bounded authored screen-space foreleg path; no anatomy/contact or art acceptance'}}
 initial=copy.deepcopy(project);h=History(initial)
 before=np.array(im('inputs/control',5));after=im('preview-v1/frames',5);candidate=np.array(after)
 source_owner=np.array(Image.open(R/'preview-v1/maps/source-foreleg-owner.png'))>0
 z=np.load(R/'preview-v1/maps/05-projection.npz');allowed=source_owner|z['placed'];protected=np.array(Image.open(R/'preview-v1/maps/protected-upper.png'))>0;allowed&=~protected
 coords=[[int(x),int(y)]for y,x in np.argwhere(allowed)]
 tx=candidate_transaction(h.project,'f05',after,coords,reason='Source05 complete visible foreground leg: fixed hip; anchored proximal lean into exact-3px rigid distal boot shift. Fix inward/outward path jog, preserve paint volume and other cels.')
 h.apply(tx);final=copy.deepcopy(h.project);final_hash=project_hash(final)
 for i in range(8):assert render_cel(h.project,f'f{i:02}').tobytes()==im('preview-v1/frames',i).tobytes()
 h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==final_hash
 stable=project_hash(h.project);bad=after.copy();bad.putpixel((1,1),(255,0,255,255));rejected=False
 try:candidate_transaction(h.project,'f05',bad,coords)
 except Exception:rejected=True
 assert rejected and project_hash(h.project)==stable
 rejected=False
 try:h.apply(tx)
 except Exception:rejected=True
 assert rejected and project_hash(h.project)==stable
 for name,data in [('initial',initial),('final',final),('journal',h.journal())]:dump(out/f'{name}.json',data)
 (out/'EDITOR-RECEIPT.json').write_text(json.dumps({'actual_guarded_transactions':1,'source_project_hash':project_hash(initial),'final_project_hash':final_hash,'all8_RGBA_exact':True,'undo_redo_exact':True,'stale_and_out_of_mask_rejected_atomically':True,'actual_changed_pixels':int(np.any(before!=candidate,axis=2).sum()),'explicit_allowed_coordinates':len(coords),'fps':160,'hold_ticks_each':9,'cycle_ticks':72,'external_GUI_tested':False,'art_approval':False},indent=2)+'\n')
 print('One guarded transaction; all8 renderedRGBA, undo/redo and two negative guards PASS')
if __name__=='__main__':main()

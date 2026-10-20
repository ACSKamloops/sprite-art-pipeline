from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,candidate_transaction,render_cel
ROOT=Path(__file__).resolve().parents[1]
def main():
    palette=[(0,0,0,0)];lookup={palette[0]:0};cels={};frames=[]
    for i in range(8):
        a=Image.open(ROOT/'inputs/B'/f'{i:02}.png').convert('RGBA');indices=[]
        for rgba in a.get_flattened_data():
            if rgba not in lookup:lookup[rgba]=len(palette);palette.append(rgba)
            indices.append(lookup[rgba])
        cid=f'rowan-se-{i:02}';cels[cid]={'layer_id':'paint','pixels':indices};frames.append({'id':cid,'duration_ticks':9,'cels':{'paint':cid},'landmarks':{'pivot':[64,112]}})
    initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},
        'palette':[list(x)for x in palette],'layers':[{'id':'paint','name':'Frozen coherent-upper B plus one generated lower cleanup','locked':False}],
        'cels':cels,'frames':frames,'animations':[{'id':'walk','frames':[x['id']for x in frames],'fps':160,'loop':True,'events':[]}],
        'provenance':{'input':'inputs/B/00..07.png','one_generation_request':'generation/request.json','registration':'REGISTRATION.json','source_masks':'masks/'}}
    h=History(initial)
    for i in[1,3,5,7]:
        target=Image.open(ROOT/'selected'/f'{i:02}.png').convert('RGBA')
        before=np.array(Image.open(ROOT/'inputs/B'/f'{i:02}.png').convert('RGBA'));after=np.array(target)
        changed=np.any(before!=after,axis=2);allowed=(np.array(Image.open(ROOT/'masks'/f'{i:02}-waist-lower-owner.png'))>0)|(np.array(Image.open(ROOT/'masks'/f'{i:02}-complete-gloves-owner.png'))>0)
        assert not(changed&~allowed).any()
        coordinates=[[int(x),int(y)]for y,x in np.argwhere(changed)]
        tx=candidate_transaction(h.project,f'rowan-se-{i:02}',target,coordinates)
        tx['reason']='Single ImageGen full-painted lower-body cleanup of demonstrated cuff/knee/boot defects; stable upper and complete glove RGBA/transparency restored with literal owners.'
        h.apply(tx)
    final_hash=project_hash(h.project)
    for _ in range(h.cursor):h.undo()
    assert project_hash(h.project)==project_hash(initial)
    for _ in range(len(h.records)):h.redo()
    assert project_hash(h.project)==final_hash
    journal=h.journal();r=History.replay(initial,journal);assert project_hash(r.project)==final_hash
    for i in range(8):assert render_cel(r.project,f'rowan-se-{i:02}').tobytes()==Image.open(ROOT/'selected'/f'{i:02}.png').convert('RGBA').tobytes()
    for name,data in [('initial',initial),('final',h.project),('journal',journal)]: (ROOT/'projects'/f'{name}.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (ROOT/'projects/UNDO-REDO-RECEIPT.json').write_text(json.dumps({'guarded_candidate_transactions':4,'actual_undo_to_initial':True,'actual_redo_to_final':True,'journal_replay_RGBA_frames':8,'initial_sha256':project_hash(initial),'final_sha256':final_hash},indent=2)+'\n')
    print('four guarded transactions; actual undo/redo and eight-frame journal replay passed')
if __name__=='__main__':main()

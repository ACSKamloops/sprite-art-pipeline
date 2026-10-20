from pathlib import Path
import json
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,candidate_transaction,render_cel
ROOT=Path(__file__).resolve().parents[1]
BANKS=[('rowan','northeast'),('lyra','southeast'),('lyra','northeast')]
def main():
    receipts=[]
    for actor,view in BANKS:
        palette=[(0,0,0,0)];lookup={palette[0]:0};cels={};frames=[]
        for i in range(8):
            a=Image.open(ROOT/'inputs'/actor/view/f'{i:02}.png').convert('RGBA');pixels=[]
            for rgba in a.get_flattened_data():
                if rgba not in lookup:lookup[rgba]=len(palette);palette.append(rgba)
                pixels.append(lookup[rgba])
            cid=f'f{i:02}';cels[cid]={'layer_id':'paint','pixels':pixels};frames.append({'id':cid,'duration_ticks':9,'cels':{'paint':cid},'landmarks':{'pivot':[64,112]}})
        initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':[list(x)for x in palette],
            'layers':[{'id':'paint','name':'Unselected coherent upper source-art trial','locked':False}],'cels':cels,'frames':frames,
            'animations':[{'id':'walk','frames':[f['id']for f in frames],'fps':160,'loop':True,'events':[]}],
            'provenance':{'actor':actor,'view':view,'status':'UNSELECTED','source_maps':f'trials/{actor}/{view}/maps/'}}
        h=History(initial)
        for i in range(8):
            a=np.array(Image.open(ROOT/'inputs'/actor/view/f'{i:02}.png').convert('RGBA'));target=Image.open(ROOT/'trials'/actor/view/'frames'/f'{i:02}.png').convert('RGBA');changed=np.any(a!=np.array(target),axis=2)
            tx=candidate_transaction(h.project,f'f{i:02}',target,[[int(x),int(y)]for y,x in np.argwhere(changed)]);tx['reason']='Unselected stable same-view source2 torso, restrained arms/bob, source painted lower poses with explicit integer source maps.';h.apply(tx)
        final=project_hash(h.project)
        for _ in range(h.cursor):h.undo()
        assert project_hash(h.project)==project_hash(initial)
        for _ in range(len(h.records)):h.redo()
        assert project_hash(h.project)==final
        r=History.replay(initial,h.journal());assert project_hash(r.project)==final
        for i in range(8):assert render_cel(r.project,f'f{i:02}').tobytes()==Image.open(ROOT/'trials'/actor/view/'frames'/f'{i:02}.png').convert('RGBA').tobytes()
        d=ROOT/'projects'/actor/view;d.mkdir(parents=True)
        for n,obj in [('initial',initial),('final',h.project),('journal',h.journal())]:(d/f'{n}.json').write_text(json.dumps(obj,separators=(',',':'))+'\n')
        receipts.append({'actor':actor,'view':view,'guarded_transactions':8,'actual_undo_redo_replay':True,'RGBA_frames':8,'status':'UNSELECTED'})
    (ROOT/'projects/UNDO-REDO-RECEIPT.json').write_text(json.dumps(receipts,indent=2)+'\n');print('24 unselected journal frames verified')
if __name__=='__main__':main()

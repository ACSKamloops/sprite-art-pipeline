from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel
ROOT=Path(__file__).resolve().parents[1]
BANKS=[('rowan','northeast'),('lyra','southeast'),('lyra','northeast')]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output).resolve();assert not out.exists(),'Output must be fresh';out.mkdir(parents=True)
    rows=[]
    for actor,view in BANKS:
        sources=[np.array(Image.open(ROOT/'inputs'/actor/view/f'{i:02}.png').convert('RGBA'))for i in range(8)]
        initial=json.loads((ROOT/'projects'/actor/view/'initial.json').read_text());j=json.loads((ROOT/'projects'/actor/view/'journal.json').read_text());h=History.replay(initial,j)
        assert project_hash(h.project)==project_hash(json.loads((ROOT/'projects'/actor/view/'final.json').read_text()))
        d=out/actor/view;d.mkdir(parents=True)
        for i in range(8):
            z=np.load(ROOT/'trials'/actor/view/'maps'/f'{i:02}-source.npz');src=z['source_id'];xy=z['source_xy'];rebuilt=np.zeros((128,128,4),np.uint8)
            for y,x in np.argwhere(src>=0):
                phase=int(src[y,x]);sx,sy=xy[y,x];assert 0<=phase<8 and 0<=sx<128 and 0<=sy<128;rebuilt[y,x]=sources[phase][sy,sx]
            expected=Image.open(ROOT/'trials'/actor/view/'frames'/f'{i:02}.png').convert('RGBA')
            assert rebuilt.tobytes()==expected.tobytes();assert render_cel(h.project,f'f{i:02}').tobytes()==expected.tobytes()
            Image.fromarray(rebuilt).save(d/f'{i:02}.png')
            rows.append({'actor':actor,'view':view,'phase':i,'frozen_map_RGBA_exact':True,'journal_RGBA_exact':True,'PNG_bytes_exact':(d/f'{i:02}.png').read_bytes()==(ROOT/'trials'/actor/view/'frames'/f'{i:02}.png').read_bytes(),'hold':[9,160]})
    (out/'REPLAY-RECEIPT.json').write_text(json.dumps({'status':'UNSELECTED','all24_map_and_journal_RGBA_exact':True,'only_retained_package_inputs_used':True,'rows':rows},indent=2)+'\n');print('24/24 frozen maps and journals replay exactly')
if __name__=='__main__':main()

"""Fresh-output deterministic raw-sheet construction + independent toolkit replay."""
from pathlib import Path
import argparse,hashlib,json,shutil,io
import numpy as np
from PIL import Image
from scipy.ndimage import label,binary_dilation
from sprite_lab import History,project_hash,render_cel
ROOT=Path(__file__).resolve().parents[1]
BOB=[0,1,1,0,0,1,1,0];SW=[0,-1,-2,-1,0,1,2,1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output).resolve()
    assert not out.exists(),'Output must be a fresh nonexistent directory'
    out.mkdir(parents=True);(out/'constructed').mkdir();(out/'journal-replay').mkdir()
    raw=Image.open(ROOT/'generation/raw.png').convert('RGBA');assert raw.size==(1254,1254)
    small=raw.resize((256,256),Image.Resampling.NEAREST);atlas=Image.new('RGBA',(256,256));atlas.paste(small,(0,-2))
    source2=np.array(Image.open(ROOT/'inputs/upper/source02.png').convert('RGBA'))
    arms=[np.array(Image.open(ROOT/'inputs/upper'/f'{n}-arm-owner.png'))>0 for n in['left','right']]
    initial=json.loads((ROOT/'projects/initial.json').read_text());journal=json.loads((ROOT/'projects/journal.json').read_text());h=History.replay(initial,journal)
    assert project_hash(h.project)==project_hash(json.loads((ROOT/'projects/final.json').read_text()))
    rows=[]
    for i in range(8):
        before=np.array(Image.open(ROOT/'inputs/B'/f'{i:02}.png').convert('RGBA'))
        if i%2==0:
            rebuilt=before.copy();shutil.copy2(ROOT/'inputs/B'/f'{i:02}.png',out/'constructed'/f'{i:02}.png')
        else:
            j=[1,3,5,7].index(i);cx,cy=(j%2)*128,(j//2)*128;g=np.array(atlas.crop((cx,cy,cx+128,cy+128)))
            cc,n=label(g[...,3]>16,np.ones((3,3)));counts=np.bincount(cc.ravel());counts[0]=0
            support=binary_dilation(cc==int(counts.argmax()),iterations=1)&(g[...,3]>0);g[~support]=0
            assert np.array_equal(support,np.array(Image.open(ROOT/'masks'/f'{i:02}-generated-mainbody-owner.png'))>0)
            repair=np.array(Image.open(ROOT/'masks'/f'{i:02}-waist-lower-owner.png'))>0;rebuilt=before.copy();rebuilt[repair]=g[repair]
            owner=np.zeros((128,128),bool);gloves=np.zeros_like(before)
            for k,dx in[(0,SW[i]),(1,-SW[i])]:
                for y,x in np.argwhere(arms[k]):
                    tx,ty=int(x)+dx,int(y)+BOB[i]
                    if 0<=tx<128 and 0<=ty<128:owner[ty,tx]=True;gloves[ty,tx]=source2[y,x]
            assert np.array_equal(owner,np.array(Image.open(ROOT/'masks'/f'{i:02}-complete-gloves-owner.png'))>0)
            rebuilt[owner]=gloves[owner]
            assert np.array_equal(rebuilt[~(repair|owner)],before[~(repair|owner)])
            # Frozen actual raw-pixel map witnesses all visible generated paint.
            z=np.load(ROOT/'maps'/f'{i:02}-raw-source.npz');raw_array=np.array(raw)
            for y,x in np.argwhere(z['generated_visible']):
                rx,ry=z['raw_source_xy'][y,x];assert rx>=0 and ry>=0
                assert np.array_equal(rebuilt[y,x],raw_array[ry,rx])
            Image.fromarray(rebuilt).save(out/'constructed'/f'{i:02}.png')
        expected=np.array(Image.open(ROOT/'selected'/f'{i:02}.png').convert('RGBA'));replayed=render_cel(h.project,f'rowan-se-{i:02}')
        assert np.array_equal(rebuilt,expected),f'construction RGBA {i}'
        assert replayed.tobytes()==expected.tobytes(),f'journal RGBA {i}'
        replayed.save(out/'journal-replay'/f'{i:02}.png')
        rows.append({'phase':i,'construction_RGBA_exact':True,'journal_RGBA_exact':True,
          'construction_PNG_bytes_exact':sha(out/'constructed'/f'{i:02}.png')==sha(ROOT/'selected'/f'{i:02}.png'),
          'journal_PNG_bytes_exact':sha(out/'journal-replay'/f'{i:02}.png')==sha(ROOT/'selected'/f'{i:02}.png'),
          'expected_sha256':sha(ROOT/'selected'/f'{i:02}.png'),'hold':[9,160]})
    final_hash=project_hash(h.project)
    for _ in range(h.cursor):h.undo()
    assert project_hash(h.project)==project_hash(initial)
    for _ in range(len(h.records)):h.redo()
    assert project_hash(h.project)==final_hash
    receipt={'only_retained_package_inputs_used':True,'fresh_output':str(out),'raw_construction_frames':8,'journal_replay_frames':8,'actual_undo_redo':True,'rows':rows,'cycle':[9,20]}
    (out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

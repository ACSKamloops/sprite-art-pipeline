from pathlib import Path
import argparse, hashlib, json
from collections import deque
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0

def holes(a):
    m=a[:,:,3]==0;seen=np.zeros((128,128),bool);q=deque()
    for y,x in [(i,0)for i in range(128)]+[(i,127)for i in range(128)]+[(0,i)for i in range(128)]+[(127,i)for i in range(128)]:
        if m[y,x]and not seen[y,x]:seen[y,x]=True;q.append((y,x))
    while q:
        y,x=q.popleft()
        for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:
            yy,xx=y+dy,x+dx
            if 0<=yy<128 and 0<=xx<128 and m[yy,xx]and not seen[yy,xx]:seen[yy,xx]=True;q.append((yy,xx))
    return m&~seen

def main(out):
    assert out.is_absolute()and not out.exists()
    entries=json.loads((P/'INPUTS.json').read_text())['files']
    for f in entries:assert sha(P/f['path'])==f['sha256']
    a=read(P/'inputs/current/03.png');s=json.loads((P/'spec/RECIPE.json').read_text())
    c=mask(P/'final/masks/cloth-source.png');b=mask(P/'final/masks/boot-source.png');u=mask(P/'final/masks/protected-upper.png')
    base=a.copy();base[c|b|u]=0
    upper=np.zeros_like(a);upper[u]=a[u]
    under=np.zeros_like(a)
    for x,y in s['joint_underlap']['identity_coordinates']:under[y,x]=a[y,x]
    layers=[base,under]
    for part in ['cloth','boot']:
        z=np.load(P/f'final/maps/{part}.npz',allow_pickle=False);xy=z['source_xy'];m=xy[:,:,0]>=0;layer=np.zeros_like(a)
        layer[m]=a[xy[:,:,1][m],xy[:,:,0][m]]
        assert np.array_equal(layer,read(P/f'final/layers/{part}.png'))
        layers.append(layer)
    layers.append(upper)
    canvas=Image.new('RGBA',(128,128))
    for layer in layers:canvas=Image.alpha_composite(canvas,Image.fromarray(layer))
    result=np.array(canvas);assert np.array_equal(result,read(P/'final/03.png'))
    new=holes(result)&~holes(a);assert not new.any()
    assert np.array_equal(result[u],a[u])
    assert np.array_equal(result[:82],a[:82])
    overlap=(base[:,:,3]>0)&((layers[2][:,:,3]>0)|(layers[3][:,:,3]>0));assert int(overlap.sum())==9
    outside=(a[:,:,3]>0)&~(c|b|u)&~overlap;assert np.array_equal(result[outside],a[outside])
    raw=read(P/'candidate-proof/03.png');changed=np.any(raw!=result,axis=2)
    expected=np.zeros((128,128),bool)
    for op in s['sole_cleanup']['operations']:x,y=op['target'];expected[y,x]=True
    assert np.array_equal(changed,expected)
    assert np.array_equal(raw[~expected],result[~expected])
    out.mkdir(parents=True)
    Image.fromarray(result).save(out/'03.png');assert sha(out/'03.png')==sha(P/'final/03.png')
    r={'status':'PASS independent retained-map reconstruction, not visual acceptance','input_hashes_exact':len(entries),'candidate_RGBA_PNG_exact':True,'upper_RGBA_exact':True,'all_rows_through81_RGBA_exact':True,'opposite_visible_source_layer_exact':True,'declared_natural_opposite_leg_occlusion_pixels':9,'sole_cleanup_only_four_pixels':True,'new_enclosed_transparent_pixels':0,'new_authored_RGB':0,'model_calls':0,'source_map_replay_imports_producer':False,'canonical_writes':False,'sha256':sha(out/'03.png')}
    (out/'REPLAY-RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();main(a.output)

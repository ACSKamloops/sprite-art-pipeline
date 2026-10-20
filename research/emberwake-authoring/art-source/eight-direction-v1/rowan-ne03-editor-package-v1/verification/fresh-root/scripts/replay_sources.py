"""Retained literal source maps only; no original producer/model/toolkit import."""
import json
import numpy as np
from PIL import Image
from common import ROOT,rgba,mask,sha,write,verify_inputs

def compose(layers):
    im=Image.new('RGBA',(128,128))
    for layer in layers:im=Image.alpha_composite(im,Image.fromarray(layer))
    return im

def replay(out):
    assert not out.exists();out.mkdir(parents=True)
    verify_inputs();s=json.loads((ROOT/'retained-source/RECIPE.json').read_text())
    a=rgba(ROOT/'inputs/current/03.png')
    c=mask(ROOT/'retained-source/masks/cloth-source.png');b=mask(ROOT/'retained-source/masks/boot-source.png');u=mask(ROOT/'retained-source/masks/protected-upper.png')
    base=a.copy();base[c|b|u]=0
    upper=np.zeros_like(a);upper[u]=a[u]
    under=np.zeros_like(a)
    for x,y in s['joint_underlap']['identity_coordinates']:assert (c|b)[y,x];under[y,x]=a[y,x]
    layers={'retained-other':base,'upper':upper,'joint-underlap':under}
    maps={}
    for name,filename,owner in [('cloth','cloth.npz',c),('boot-before-contour-cleanup','boot-before-contour-cleanup.npz',b),('boot','boot.npz',b)]:
        z=np.load(ROOT/'retained-source/maps'/filename,allow_pickle=False);xy=z['source_xy'];valid=xy[:,:,0]>=0
        layer=np.zeros_like(a);sx,sy=xy[:,:,0][valid],xy[:,:,1][valid]
        assert np.all(owner[sy,sx])
        layer[valid]=a[sy,sx];layers[name]=layer;maps[name]=xy
    for name,layer in layers.items():assert np.array_equal(layer,rgba(ROOT/f'retained-source/layers/{name}.png'))
    literal=layers['boot-before-contour-cleanup'].copy()
    for op in s['sole_cleanup']['operations']:
        x,y=op['target'];assert literal[y,x].tolist()==op['expected_before_RGBA']
        if op['op']=='erase':literal[y,x]=0
        else:sx,sy=op['source'];assert a[sy,sx].tolist()==op['source_RGBA'];literal[y,x]=a[sy,sx]
    assert np.array_equal(literal,layers['boot'])
    pre=compose([base,under,layers['cloth'],layers['boot-before-contour-cleanup'],upper]);final=compose([base,under,layers['cloth'],layers['boot'],upper])
    pre.save(out/'03-before-sole.png');assert (out/'03-before-sole.png').read_bytes()==(ROOT/'inputs/03-completed-owner-before-sole.png').read_bytes()
    assert final.tobytes()==rgba(ROOT/'inputs/expected-final/03.png').tobytes()
    rows=[]
    for i in range(8):
        dst=out/f'{i:02}.png'
        if i==3:final.save(dst)
        else:dst.write_bytes((ROOT/f'inputs/current/{i:02}.png').read_bytes())
        assert dst.read_bytes()==(ROOT/f'inputs/expected-final/{i:02}.png').read_bytes()
        rows.append({'phase':i,'RGBA_exact':True,'PNG_exact':True,'sha256':sha(dst)})
    original=np.array(Image.open(ROOT/'inputs/current/03.png'));target=np.array(final)
    assert np.array_equal(original[:82],target[:82]);assert np.array_equal(original[u],target[u])
    overlap=(base[:,:,3]>0)&((layers['cloth'][:,:,3]>0)|(layers['boot'][:,:,3]>0));assert overlap.sum()==9
    r={'status':'PASS local retained-source literal-map replay','all8':rows,'pre_sole03_RGBA_PNG_exact':True,'all_retained_component_layers_exact':True,'eleven_visible_source_seam_underlap_pixels':True,'upper_and_rows_through81_exact':True,'declared_foreground_overlap_pixels':9,'new_authored_RGB':0,'four_literal_sole_operations':s['sole_cleanup']['operations'],'model_calls':0}
    write(out/'SOURCE-REPLAY-RECEIPT.json',r)
    return r

if __name__=='__main__':replay(ROOT/'source-replay')

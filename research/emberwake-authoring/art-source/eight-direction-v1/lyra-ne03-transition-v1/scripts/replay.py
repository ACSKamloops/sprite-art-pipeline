"""Portable fixed-map replay; no canonical files, model, editor or geometry refit."""
from pathlib import Path
from collections import deque
import argparse,hashlib,json,subprocess,sys
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def compose(parts):
    im=Image.new('RGBA',(128,128))
    for a in parts:im=Image.alpha_composite(im,Image.fromarray(a))
    return im
def holes(a):
    m=a[:,:,3]==0;v=np.zeros((128,128),bool);q=deque()
    for y,x in [(i,0)for i in range(128)]+[(i,127)for i in range(128)]+[(0,i)for i in range(128)]+[(127,i)for i in range(128)]:
        if m[y,x]and not v[y,x]:v[y,x]=True;q.append((y,x))
    while q:
        y,x=q.popleft()
        for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:
            yy,xx=y+dy,x+dx
            if 0<=yy<128 and 0<=xx<128 and m[yy,xx]and not v[yy,xx]:v[yy,xx]=True;q.append((yy,xx))
    return m&~v

def replay(out):
    assert out.is_absolute()and not out.exists()
    inputs=json.loads((P/'INPUTS.json').read_text())
    for f in inputs['files']:assert sha(P/f['path'])==f['sha256']
    target=json.loads((P/'FROZEN-TARGETS.json').read_text())
    assert sha(P/'final/03.png')==target['final03_sha256']
    assert sha(P/'final/raw03.png')==target['before_sole03_sha256']
    s=json.loads((P/'spec/RECIPE.json').read_text());a=rgba(P/'inputs/current/03.png')
    c=mask(P/'final/masks/literal-cloth-source.png');b=mask(P/'final/masks/literal-boot-source.png');u=mask(P/'final/masks/protected-upper.png')
    base=a.copy();base[c|b|u]=0;upper=np.zeros_like(a);upper[u]=a[u];under=np.zeros_like(a)
    for x,y in s['declared_cloth_seam_underlap']+s['declared_boot_shared_joint_underlap']:assert(c|b)[y,x];under[y,x]=a[y,x]
    layers={'retained-other':base,'source-seam-underlap':under,'upper':upper}
    for name,filename,owner in [('cloth','cloth.npz',c),('boot','boot.npz',b),('boot-before-cleanup','boot-before-cleanup.npz',b)]:
        xy=np.load(P/'final/maps'/filename,allow_pickle=False)['source_xy'];valid=xy[:,:,0]>=0;ar=np.zeros_like(a);sx,sy=xy[:,:,0][valid],xy[:,:,1][valid];assert np.all(owner[sy,sx]);ar[valid]=a[sy,sx];layers[name]=ar
    for name,ar in layers.items():assert np.array_equal(ar,rgba(P/f'final/layers/{name}.png'))
    raw=compose([base,under,layers['cloth'],layers['boot-before-cleanup'],upper]);final=compose([base,under,layers['cloth'],layers['boot'],upper])
    assert raw.tobytes()==rgba(P/'final/raw03.png').tobytes();assert final.tobytes()==rgba(P/'final/03.png').tobytes()
    A,B=np.array(raw),np.array(final);changed=np.any(A!=B,axis=2);assert int(changed.sum())==1 and changed[115,72]
    assert A[115,72].tolist()==[17,6,0,243]and B[115,72].tolist()==[0,0,0,0]
    assert np.array_equal(B[:82],a[:82])and np.array_equal(B[u],a[u])
    assert not(holes(B)&~holes(a)).any()
    base_positive=base[:,:,3]>0;overlap=base_positive&((layers['cloth'][:,:,3]>0)|(layers['boot'][:,:,3]>0));assert int(overlap.sum())==4
    assert np.array_equal(B[base_positive&~overlap],a[base_positive&~overlap])
    assert np.array_equal(B[base_positive&(np.indices((128,128))[1]<72)],a[base_positive&(np.indices((128,128))[1]<72)])
    geom=json.loads((P/'final/maps/GEOMETRY.json').read_text());assert min(geom['boot']['determinant_ratios'])>0 and min(geom['cloth']['determinant_ratios'])>0
    out.mkdir(parents=True);raw.save(out/'03-before-sole.png');final.save(out/'03.png');assert sha(out/'03.png')==target['final03_sha256'];assert sha(out/'03-before-sole.png')==target['before_sole03_sha256']
    for name in ['control','candidate']:
        folder=out/name;folder.mkdir()
        for i in range(8):
            src=out/'03.png'if name=='candidate'and i==3 else P/f'inputs/current/{i:02}.png'
            (folder/f'{i:02}.png').write_bytes(src.read_bytes())
            assert (folder/f'{i:02}.png').read_bytes()==(P/f'review-banks/{name}/{i:02}.png').read_bytes()
    command=[sys.executable,'-B',str(P/'review-builder-root/scripts/build_walk_pair_review.py'),'--actor','lyra','--primary-view','northeast','--control-primary',str(out/'control'),'--trial-primary',str(out/'candidate'),'--mirror-symmetric','--out',str(out/'review-packet')]
    run=subprocess.run(command,text=True,capture_output=True);assert run.returncode==0,(run.stdout,run.stderr)
    packet=[]
    for original in (P/'review-packet/input').rglob('*'):
        if original.is_file():
            local=out/'review-packet/input'/original.relative_to(P/'review-packet/input');assert original.read_bytes()==local.read_bytes();packet.append(str(original.relative_to(P/'review-packet')))
    r={'status':'PASS retained-map source and exact anonymous packet replay','model_calls':0,'editor_runs':0,'canonical_access_required':False,'all26_retained_inputs_exact':True,'final03_RGBA_PNG_exact':True,'before_sole03_RGBA_PNG_exact':True,'only_one_literal_sole_erasure':True,'upper_and_rows_through81_exact':True,'retained_source_left_of72_RGBA_exact':True,'qualified_retained_fringe_cuff_occlusion_pixels':4,'new_enclosed_transparent_pixels':0,'new_authored_RGB':0,'other_seven_NE_cels_exact':True,'mirroring':'Canonical builder mirror+1 preserving pivot64; symmetric unarmed costume assumption only','exact_packet_files':packet,'packet_command':command,'packet_stdout':run.stdout,'clock':{'holds':[[9,160]]*8,'cycle':[9,20]},'final03_sha256':target['final03_sha256'],'scope':'Mechanical/source proof, no preference, score or playback acceptance'}
    (out/'REPLAY-RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS source maps, one sole erasure, all8 cels and64 packet files:',out)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();replay(a.output)

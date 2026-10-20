"""Bounded source-pixel shoulder/counter-arm experiment; no model call.

This is authored 2-D projected deformation, not recovered anatomy. Output
requires a fresh directory. Raw source/masks are retained beside this script.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PROJECT = Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1')
BOB = [0,1,1,0,0,1,1,0]
OLD = [0,-1,-2,-1,0,1,2,1]
NX = [1,1,0,-1,-1,-1,0,1]
NY = [2,1,0,-1,-2,-1,0,1]
FOREIGN = [(49,82),(50,82),(48,83),(49,83),(50,83),(47,84),
           (48,84),(49,84),(50,84),(47,85),(48,85),(49,85),(50,85)]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p): return np.array(Image.open(p).convert('RGBA'))

def freeze_inputs():
    d = ROOT/'inputs'
    if d.exists(): return
    (d/'control').mkdir(parents=True)
    for i in range(8):
        shutil.copyfile(PROJECT/'rowan-source-legs-v2/frames'/f'{i:02}.png',d/'control'/f'{i:02}.png')
    src = PROJECT/'rowan-painted-odd-v1/inputs/upper'
    for n in ['source02.png','left-arm-owner.png','right-arm-owner.png']:
        shutil.copyfile(src/n,d/n)
    shutil.copyfile(PROJECT/'walk-bundle-rowan-lyra/masks/rowan/southeast/02-lower.png',d/'source02-lower.png')
    (d/'HASHES.json').write_text(json.dumps({p.relative_to(d).as_posix():sha(p) for p in sorted(d.rglob('*.png'))},indent=2)+'\n')

def translate(part,dx,dy):
    out=np.zeros_like(part)
    for y,x in np.argwhere(part[...,3]>0):
        if 0<=x+dx<128 and 0<=y+dy<128: out[y+dy,x+dx]=part[y,x]
    return out

def sample_map(source, owner, kind, phase, sign=1):
    """Inverse-nearest monotone vertical field + proximal horizontal field."""
    yy,xx=np.mgrid[:128,:128]
    sy=np.empty((128,128),np.float64)
    by=BOB[phase]
    c=sign*NY[phase]/2
    for x in range(128):
        y=np.arange(128,dtype=float)
        if kind=='torso':
            weight=np.minimum(np.clip((y-55)/6,0,1),np.clip((84-y)/15,0,1))
            dy=-c*(x-64)/24*weight
        else:
            blend=np.clip((y-66)/8,0,1)
            dy=c+(sign*NY[phase]-c)*blend
        target=y+by+dy
        assert np.all(np.diff(target)>0),'folded vertical map'
        sy[:,x]=np.interp(np.arange(128),target,y,left=-100,right=1000)
    syi=np.floor(sy+.5).astype(int)
    if kind=='arm':
        blend=np.clip((sy-66)/8,0,1)
        sxi=np.floor(xx-sign*NX[phase]*blend+.5).astype(int)
    else: sxi=xx.copy()
    valid=(syi>=0)&(syi<128)&(sxi>=0)&(sxi<128)
    owned=np.zeros_like(valid)
    owned[valid]=owner[syi[valid],sxi[valid]]
    paint=np.zeros_like(source); paint[owned]=source[syi[owned],sxi[owned]]
    xy=np.full((128,128,2),-1,np.int16);xy[owned]=np.stack([sxi[owned],syi[owned]],axis=-1)
    return paint,xy

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists(),'fresh output required'
    freeze_inputs();o=a.output;o.mkdir(parents=True)
    for n in ['frames','maps','masks','layers','proof']:(o/n).mkdir()
    d=ROOT/'inputs';source=arr(d/'source02.png')
    upper=~(np.array(Image.open(d/'source02-lower.png'))>0)
    for x,y in FOREIGN:upper[y,x]=False
    arms=[np.array(Image.open(d/f'{s}-arm-owner.png'))>0 for s in ['left','right']]
    torso=upper&~arms[0]&~arms[1]
    def part(mask):
        q=source.copy();q[~mask]=0;return q
    rows=[];controls=[];trials=[]
    for i in range(8):
        control=arr(d/'control'/f'{i:02}.png');controls.append(Image.fromarray(control))
        old=translate(part(torso),0,BOB[i])
        for mask,dx in [(arms[0],OLD[i]),(arms[1],-OLD[i])]:
            q=translate(part(mask),dx,BOB[i]);use=q[...,3]>0;old[use]=q[use]
        # Reconstruct the original literal shoulder/socket extension as a
        # removal witness; never treat its small fill as hidden anatomy.
        for side,dx in [(0,OLD[i]),(1,-OLD[i])]:
            if dx==0:continue
            for y in [65,66,67]:
                for x in (range(34,55)if side==0 else range(77,89)):
                    tx,ty=x+dx,y+BOB[i]
                    if source[y,x,3] and upper[y,x] and old[ty,tx,3]==0:
                        old[ty,tx]=source[y,x]
        remove=(old[...,3]>0)&np.all(old==control,axis=2)
        # Only source-witnessed upper paint is removed. Current different
        # foreground knee/trouser paint stays in front of the moving body.
        foreground=(control[...,3]>0)&~remove
        foreground[:56]=False
        base=control.copy();base[remove]=0
        new=np.zeros_like(control)
        for kind,mask,sign,name in [('torso',torso,1,'torso'),('arm',arms[1],-1,'far-arm'),('arm',arms[0],1,'near-arm')]:
            q,xy=sample_map(source,mask,kind,i,sign)
            use=q[...,3]>0;new[use]=q[use]
            np.savez_compressed(o/'maps'/f'{i:02}-{name}.npz',source_xy=xy)
            Image.fromarray(q).save(o/'layers'/f'{i:02}-{name}.png')
        # Pilot uses literal source replacement to preserve AA sourceRGBA.
        # Keep that contract here; do not silently change to source-over.
        use=new[...,3]>0;base[use]=new[use];base[foreground]=control[foreground]
        base[:56]=control[:56]
        assert np.array_equal(base[89:],control[89:]),'lower leg/boot mutation'
        Image.fromarray(base).save(o/'frames'/f'{i:02}.png');trials.append(Image.fromarray(base))
        Image.fromarray((remove*255).astype('uint8')).save(o/'masks'/f'{i:02}-removed-source-upper.png')
        Image.fromarray((foreground*255).astype('uint8')).save(o/'masks'/f'{i:02}-protected-other-paint.png')
        rows.append({'phase':i,'changed_pixels':int(np.any(base!=control,axis=2).sum()),'head_rows_0_55_exact':True,'rows_89_127_exact':True,'near_glove_translation':[NX[i],NY[i]+BOB[i]],'far_glove_translation':[-NX[i],-NY[i]+BOB[i]],'sha256':sha(o/'frames'/f'{i:02}.png')})
    for name,size in [('native',128),('2x',256),('game',84)]:
        sheet=Image.new('RGB',(8*size,2*(size+22)),'#e4e1d7');draw=ImageDraw.Draw(sheet)
        for row,seq in enumerate([controls,trials]):
            for i,im in enumerate(seq):
                im=im.resize((size,size),Image.Resampling.NEAREST);sheet.paste(im,(i*size,row*(size+22)+22),im)
                draw.text((i*size+4,row*(size+22)+4),f'{"control"if row==0 else"trial"} {i:02}',fill='black')
        sheet.save(o/'proof'/f'comparison-{name}.png')
    (o/'RECEIPT.json').write_text(json.dumps({'status':'preview only; no art or journal approval','method':'source02 bounded monotone projected shoulder field and source plateau gloves; exact current differing foreground paint; no new colors','clock':{'holds':[[9,160]]*8,'cycle':[9,20]},'rows':rows},indent=2)+'\n')
    print(json.dumps({'out':str(o),'changed_pixels':[r['changed_pixels']for r in rows]}))

if __name__=='__main__':main()

"""Bounded stable-upper experiment: visible source layers only, explicit maps."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'inputs/rowan/southeast'
OUT=ROOT/'pilot-rowan-se'
def polygon(points):
    im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255)
    return np.array(im)>0
def translate(a,dx,dy):
    out=np.zeros_like(a); ys,xs=np.where(a[...,3]>0)
    for y,x in zip(ys,xs):
        xx,yy=x+dx,y+dy
        if 0<=xx<128 and 0<=yy<128:out[yy,xx]=a[y,x]
    return out
def main():
    OUT.mkdir(exist_ok=True);(OUT/'frames').mkdir(exist_ok=True);(OUT/'masks').mkdir(exist_ok=True);(OUT/'maps').mkdir(exist_ok=True)
    a=[np.array(Image.open(IN/f'{i:02}.png').convert('RGBA'))for i in range(8)]
    # The actual frame02 has an open, relaxed same-view upper, with both gloves
    # beside the waist. This experiment never cross-fades different torsos.
    source=2
    lower2=np.array(Image.open(IN/'upstream-masks/02-lower.png'))>0
    upper=~lower2
    # Remove lower-pant fragments admitted by the old rectangular glove guard.
    foreign=[(49,82),(50,82),(48,83),(49,83),(50,83),
             (47,84),(48,84),(49,84),(50,84),(47,85),(48,85),(49,85),(50,85)]
    for x,y in foreign:upper[y,x]=False
    # Literal 2D forearm/hand ownership; whole visible glove plateaus translate
    # rigidly by at most two pixels. Upper pauldrons and shoulders remain fixed.
    left=polygon([(37,66),(51,66),(53,70),(51,75),(49,80),(47,83),(44,85),
                  (36,85),(32,82),(31,78),(32,73),(34,70)]) & upper
    right=polygon([(78,66),(87,66),(91,70),(94,74),(94,79),(90,82),
                   (84,83),(81,80),(80,76),(78,72)]) & upper
    torso=upper & ~left & ~right
    # This is compatible VISIBLE thigh paint, not recovered hidden paint. It is
    # retained only as an underlay for the newly uncovered key0/1/7 hip pocket.
    # Original complete painted lower silhouette/boots composite above it.
    cloth=polygon([(49,81),(60,81),(63,84),(61,88),(58,91),(53,90),(50,87)])
    cloth &= (a[2][...,0]>130)&(a[2][...,1]>90)&(a[2][...,0]>a[2][...,1]+8)&(a[2][...,1]>a[2][...,2]+8)&(a[2][...,3]>200)
    hipseam=polygon([(50,82),(77,82),(79,85),(76,86),(65,86),(60,88),(50,87)]) & lower2
    def layer(mask):
        b=a[source].copy();b[~mask]=0;return b
    for name,m in [('upper',upper),('torso',torso),('left-arm',left),('right-arm',right),('visible-thigh-underlay',cloth),('visible-hip-seam-underlay',hipseam)]:
        Image.fromarray((m*255).astype('uint8')).save(OUT/'masks'/f'{name}.png')
    # Small counter-arm travel, not a running pump. Bob is exactly one pixel.
    bob=[0,1,1,0,0,1,1,0]
    swing=[0,-1,-2,-1,0,1,2,1]
    frames=[];receipts=[]
    for i in range(8):
        if i%2==0:
            own=np.array(Image.open(IN/'upstream-masks'/f'{i:02}-lower.png'))>0
        else:
            z=np.load(IN/f'{i:02}-map.npz');own=z['allowed']|z['old_lower']
        legs=a[i].copy();legs[~own]=0
        # Source index and x/y maps record every visible imported pixel.
        srcid=np.full((128,128),-1,np.int16);xy=np.full((128,128,2),-1,np.int16)
        canvas=np.zeros((128,128,4),np.uint8)
        def over(part,sourceid,dx=0,dy=0,ownmask=None):
            ys,xs=np.where(part[...,3]>0)
            for y,x in zip(ys,xs):
                xx,yy=int(x)+dx,int(y)+dy
                if 0<=xx<128 and 0<=yy<128:
                    # Literal source replace preserves original RGBA, including AA.
                    canvas[yy,xx]=part[y,x];srcid[yy,xx]=sourceid;xy[yy,xx]=[x,y]
        over(layer(torso),source,0,bob[i])
        over(layer(hipseam),2)
        if i in(0,1,7):over(layer(cloth),2)
        over(legs,i)
        over(layer(left),source,swing[i],bob[i])
        over(layer(right),source,-swing[i],bob[i])
        # A 1px arm socket underlay uses source2's actual upper-arm pixel rows.
        # Only fills transparency beside the static shoulder; never repaints feet.
        seam=[]
        for side,dx in [('left',swing[i]),('right',-swing[i])]:
            if dx==0:continue
            m=left if side=='left'else right
            for y in [65,66,67]:
                for x in range(34,55)if side=='left'else range(77,89):
                    xx,yy=x+dx,y+bob[i]
                    if (a[source][y,x,3]>0 and upper[y,x]and
                        0<=xx<128 and 0<=yy<128 and canvas[yy,xx,3]==0):
                        canvas[yy,xx]=a[source][y,x];srcid[yy,xx]=source;xy[yy,xx]=[x,y];seam.append([xx,yy,x,y])
        # Complete visible knee silhouettes take foreground ownership where the
        # common arms would otherwise clip them. This is an explicit occlusion
        # choice, not recolouring or deformation. Record and review this choice.
        knees={
            0:[[(49,86),(63,86),(64,92),(55,94),(49,91)],[(63,79),(78,79),(81,95),(65,95)]],
            2:[[(49,81),(63,81),(63,90),(50,91)],[(63,81),(76,81),(81,96),(65,97)]],
            4:[[(50,81),(63,81),(74,99),(64,101),(53,91)],[(66,81),(77,81),(73,94),(63,94)]],
            6:[[(46,79),(62,79),(62,91),(47,92)],[(74,74),(85,74),(89,82),(85,90),(73,89)]]}
        key=i if i%2==0 else {1:0,3:2,5:6,7:0}[i]
        kneemask=np.zeros((128,128),bool)
        for poly in knees[key]:kneemask|=polygon(poly)
        kneemask &= own
        knee_layer=a[i].copy();knee_layer[~kneemask]=0;over(knee_layer,i)
        # Exact preservation witnesses for the complete published boot masks.
        boots=[]
        if i%2==0:
            for k in (0,1):
                m=np.array(Image.open(IN/'upstream-masks'/f'{i:02}-boot{k}.png'))>0
                boot_layer=a[i].copy();boot_layer[~m]=0;over(boot_layer,i)
                changed=m&np.any(canvas!=a[i],axis=2)
                boots.append({'boot':k,'source_pixels':int(m.sum()),'occluded_or_changed':int(changed.sum()),'changed_coordinates':[[int(x),int(y)]for y,x in np.argwhere(changed)]})
        Image.fromarray(canvas).save(OUT/'frames'/f'{i:02}.png')
        Image.fromarray((own*255).astype('uint8')).save(OUT/'masks'/f'{i:02}-lower-owner.png')
        Image.fromarray((kneemask*255).astype('uint8')).save(OUT/'masks'/f'{i:02}-foreground-knee-owner.png')
        np.savez_compressed(OUT/'maps'/f'{i:02}-source.npz',source_id=srcid,source_xy=xy)
        frames.append(Image.fromarray(canvas))
        receipts.append({'phase':i,'lower_source':f'inputs/rowan/southeast/{i:02}.png','upper_source':'inputs/rowan/southeast/02.png',
                         'bob':bob[i],'left_forearm_dx':swing[i],'right_forearm_dx':-swing[i],
                         'visible_thigh_underlay':i in(0,1,7),'socket_fill':seam,'boot_checks':boots})
    # Native/0.66 actual-size chronology plus enlarged lower and upper comparisons.
    for name,size in [('native',128),('game',84),('2x',256)]:
        out=Image.new('RGB',(8*size,2*(size+22)),'#e5e2d5');d=ImageDraw.Draw(out)
        for row,ims in enumerate([[Image.fromarray(x)for x in a],frames]):
            for i,im in enumerate(ims):
                im=im.resize((size,size),Image.Resampling.NEAREST);out.paste(im,(i*size,row*(size+22)+22),im)
                d.text((i*size+3,row*(size+22)+3),f'{"prior"if row==0 else"steady"} {i:02}',fill='black')
        out.save(OUT/f'before-after-{name}.png')
    (OUT/'receipt.json').write_text(json.dumps({'schema':'coherent-upper-pilot/v1','actor':'rowan','view':'southeast','upper_key':2,'hold':[9,160],
       'total':[9,20],'methods':['same fixed torso/shoulders','max2px rigid forearm/hand shifts','1px bob','actual painted lower poses; no leg warp','explicit compatible visible thigh underlay in uncovered key0/1/7 pocket'],
       'frames':receipts,'score':None,'status':'experiment; inspect before porting'},indent=2)+'\n')
    print(json.dumps({'frames':8,'boot_checks':[r['boot_checks']for r in receipts if r['boot_checks']],
                      'socket_fill_pixels':sum(len(r['socket_fill'])for r in receipts)},indent=2))
if __name__=='__main__':main()

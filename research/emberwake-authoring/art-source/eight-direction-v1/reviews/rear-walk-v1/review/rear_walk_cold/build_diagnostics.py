from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
root=Path('/home/astra/artifacts/emberwake-rear-walk-review-v1')
out=root/'review/rear_walk_cold'
actors=['rowan','lyra','brann']
font=ImageFont.load_default()
def hashfile(p): return hashlib.sha256(p.read_bytes()).hexdigest()
verification={}
for actor in actors:
    folder=root/actor/'input'; m=json.loads((folder/'INPUTS.json').read_text())
    entries=m['context']+[e for v in m['variants'].values() for d in v.values() for e in d]
    rows=[]
    for e in entries:
        p=folder/e['path']; h=hashfile(p)
        with Image.open(p) as im: size=im.size
        rows.append({'path':e['path'],'expected':e['sha256'],'actual':h,'matches':h==e['sha256'],'size':size})
    verification[actor]={'manifest_sha256':hashfile(folder/'INPUTS.json'),'files':rows}
    print(actor,len(rows),'all match',all(r['matches'] for r in rows),'appearance',rows[0]['size'])
(out/'hashes-before.json').write_text(json.dumps(verification,indent=2)+'\n')
def bg(n,s):
    colors={'light':(235,230,215,255),'dark':(27,32,43,255),'ground':(111,125,112,255)}
    im=Image.new('RGBA',(s,s),colors[n]); d=ImageDraw.Draw(im)
    if n=='ground':
        for k in range(0,s,max(1,round(s/8))):
            d.line((k,0,k,s),fill=(122,137,122,255)); d.line((0,k,s,k),fill=(122,137,122,255))
        d.line((0,round(112*s/128),s,round(112*s/128)),fill=(224,204,129,255))
        p=round(64*s/128);q=round(112*s/128)
        d.line((p-4,q,p+4,q),fill=(245,119,121,255));d.line((p,q-4,p,q+4),fill=(245,119,121,255))
    return im
def cell(src,n,s):
    tile=bg(n,s); art=Image.open(src).convert('RGBA').resize((s,s),Image.Resampling.NEAREST)
    tile.alpha_composite(art);return tile
for actor in actors:
    folder=root/actor/'input'
    # All context imagery at native scale; appearance kept separate at original size.
    contexts=sorted((folder/'context').glob('*.png'))
    thumbs=[p for p in contexts if p.name!='appearance.png']
    sh=Image.new('RGB',(8*144,4*156+28),(48,48,52));d=ImageDraw.Draw(sh);d.text((8,5),f'{actor}: cardinal identity and turn context only',font=font,fill='white')
    for i,p in enumerate(thumbs):
        x=(i%8)*144;y=28+(i//8)*156
        sh.paste(cell(p,'light',128).convert('RGB'),(x,y));d.text((x+2,y+131),p.stem,font=font,fill='white')
    sh.save(out/f'{actor}-context.png')
    # Native 128 and 84 proxy, four complete cycles on each background.
    for back in ['light','dark','ground']:
        sh=Image.new('RGB',(8*138,4*152+4*108+36),(47,47,52));d=ImageDraw.Draw(sh)
        d.text((8,5),f'{actor}: {back}; top native 128, bottom nearest 84; columns 00..07',font=font,fill='white')
        y=28
        for s in [128,84]:
            for var,di in [('A','northeast'),('B','northeast'),('A','northwest'),('B','northwest')]:
                d.text((4,y),f'{var} {di} {s}',font=font,fill='white');y+=15
                for i in range(8):sh.paste(cell(folder/var/di/f'{i:02}.png',back,s).convert('RGB'),(i*138,y))
                y+=s+9
        sh.save(out/f'{actor}-{back}-128-84.png')
    # 2x plus every cyclic pair: two strips 00..03 and04..07 on each background.
    for di in ['northeast','northwest']:
        for half in [0,1]:
            sh=Image.new('RGB',(4*266,6*282+34),(47,47,52));d=ImageDraw.Draw(sh)
            d.text((5,5),f'{actor} {di} nearest 2x; columns {half*4:02}..{half*4+3:02}',font=font,fill='white');y=25
            for back in ['light','dark','ground']:
                for var in ['A','B']:
                    d.text((3,y),f'{var} {back}',font=font,fill='white');y+=16
                    for col,i in enumerate(range(half*4,half*4+4)):sh.paste(cell(folder/var/di/f'{i:02}.png',back,256).convert('RGB'),(col*266,y))
                    y+=266
            sh.save(out/f'{actor}-{di}-2x-{half}.png')
    # Explicit cyclic pairs in chronological order, 128 on ground; no position normalization.
    for di in ['northeast','northwest']:
        sh=Image.new('RGB',(4*276,4*158+28),(47,47,52));d=ImageDraw.Draw(sh)
        d.text((5,5),f'{actor} {di}: all adjacent pairs, includes07->00',font=font,fill='white')
        for v,var in enumerate(['A','B']):
            for i in range(8):
                x=(i%4)*276;y=28+(v*2+i//4)*158
                d.text((x+3,y),f'{var} {i:02}->{(i+1)%8:02}',font=font,fill='white')
                for k,j in enumerate([i,(i+1)%8]):sh.paste(cell(folder/var/di/f'{j:02}.png','ground',128).convert('RGB'),(x+k*136,y+16))
        sh.save(out/f'{actor}-{di}-cyclic-pairs.png')

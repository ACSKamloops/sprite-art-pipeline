from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime, math
ROOT=Path('/home/astra/artifacts/emberwake-complete-boots-review-v1/input')
OUT=Path('/home/astra/artifacts/emberwake-complete-boots-review-v1/review')
manifest=json.loads((ROOT/'INPUTS.json').read_text())
entries=[e for variant in manifest['variants'].values() for seq in variant.values() for e in seq]+manifest['context']
check=[]
for e in entries:
    data=(ROOT/e['path']).read_bytes(); got=hashlib.sha256(data).hexdigest()
    im=Image.open(ROOT/e['path'])
    check.append({**e,'actual_sha256':got,'verified':got==e['sha256'],'size':list(im.size),'mode':im.mode})
assert len(check)==63 and all(e['verified'] for e in check)
(OUT/'input-hashes-before.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':check},indent=2)+'\n')
BG={'light':(232,231,219,255),'dark':(24,30,39,255),'ground':(87,101,70,255)}
def tile(im,size,bg):
    im=im.convert('RGBA').resize((size,size),Image.Resampling.NEAREST)
    out=Image.new('RGBA',(size,size),bg);out.alpha_composite(im)
    return out.convert('RGB')
for scale,size in [('native',128),('nearest2x',256),('proxy84',84)]:
    for bgname,bg in BG.items():
        margin=20; left=118; rowh=size+25
        sheet=Image.new('RGB',(left+8*size+margin,32+4*rowh+margin),(47,50,55))
        d=ImageDraw.Draw(sheet);d.text((10,8),f'{scale} | {bgname} | source whole canvas, nearest sampling',(245,245,245))
        row=0
        for variant in ['A','B']:
            for direction in ['southeast','southwest']:
                y=32+row*rowh;d.text((10,y+size//2),f'{variant} {direction}',(245,245,245))
                for i in range(8):
                    im=Image.open(ROOT/f'{variant}/{direction}/{i:02}.png')
                    sheet.paste(tile(im,size,bg),(left+i*size,y));d.text((left+i*size+4,y+size+5),f'{i:02}',(245,245,245))
                row+=1
        sheet.save(OUT/f'sheet-{scale}-{bgname}.png')
# Context is for appearance/turn context only.
contexts=manifest['context'];size=128; cols=8; cellh=155
sheet=Image.new('RGB',(cols*size,math.ceil(len(contexts)/cols)*cellh),(232,231,219));d=ImageDraw.Draw(sheet)
for i,e in enumerate(contexts):
    im=Image.open(ROOT/e['path']);x=i%cols*size;y=i//cols*cellh
    if im.size!=(128,128):
        im=im.copy();im.thumbnail((128,128),Image.Resampling.NEAREST)
        base=Image.new('RGBA',(128,128));base.alpha_composite(im,((128-im.width)//2,(128-im.height)//2));im=base
    sheet.paste(tile(im,128,BG['light']),(x,y));d.text((x+2,y+130),Path(e['path']).stem,(20,20,20))
sheet.save(OUT/'context-identity-turn-only.png')
print('Verified',len(check),'images; generated 9 whole-cel sheets and one context sheet.')

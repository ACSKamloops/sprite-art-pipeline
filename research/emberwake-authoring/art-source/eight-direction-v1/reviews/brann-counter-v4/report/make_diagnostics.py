from pathlib import Path
import json
from PIL import Image, ImageDraw
SRC=Path('/home/astra/artifacts/emberwake-brann-counter-review/input-v1')
OUT=Path('/home/astra/artifacts/emberwake-brann-counter-review/review-v1')
M=json.loads((SRC/'INPUTS.json').read_text())
D=OUT/'diagnostics';D.mkdir()
COLORS={'light':(232,230,220,255),'dark':(25,30,39,255),'ground':(91,98,70,255)}
SCALES={'native':128,'nearest2x':256,'proxy84':84}
def stage(im,bg,n):
    tile=Image.new('RGBA',(128,128),COLORS[bg])
    if bg=='ground':
        dr=ImageDraw.Draw(tile)
        for y in range(4,128,8):
            for x in range((y%16)//2,128,16):
                dr.point((x,y),fill=(104,108,77,255))
        dr.line((0,112,127,112),fill=(132,133,91,255))
    tile.alpha_composite(im)
    return tile.resize((n,n),Image.Resampling.NEAREST).convert('RGB')
for variant,dirs in M['variants'].items():
    for direction,frames in dirs.items():
        ims=[Image.open(SRC/e['path']).convert('RGBA') for e in frames]
        for scale,n in SCALES.items():
            for bg in COLORS:
                pw=n*2+24; ph=n+24
                sheet=Image.new('RGB',(pw*2+24,ph*4+42),(48,49,54))
                dr=ImageDraw.Draw(sheet)
                dr.text((10,7),f'{variant} {direction} | {scale} {n}px | {bg} | cyclic adjacent pairs',(248,248,248))
                for i in range(8):
                    x=12+(i%2)*pw;y=34+(i//2)*ph
                    dr.text((x,y),f'{i:02d} -> {(i+1)%8:02d}',fill=(248,248,248))
                    sheet.paste(stage(ims[i],bg,n),(x,y+16))
                    sheet.paste(stage(ims[(i+1)%8],bg,n),(x+n+8,y+16))
                sheet.save(D/f'{variant}-{direction}-{scale}-{bg}-pairs.png')
        # Upper-body landmarks at 4x for local cuff/shoulder/occlusion review.
        for bg in COLORS:
            sheet=Image.new('RGB',(4*320+20,2*280+50),(48,49,54));dr=ImageDraw.Draw(sheet)
            dr.text((10,8),f'{variant} {direction} upper body crop x4 | {bg}; all eight cels',(248,248,248))
            for i,im in enumerate(ims):
                tile=stage(im,bg,128).crop((24,24,104,88)).resize((320,256),Image.Resampling.NEAREST)
                x=10+(i%4)*320;y=44+(i//4)*280
                dr.text((x,y-14),f'{i:02d}',fill=(248,248,248));sheet.paste(tile,(x,y))
            sheet.save(D/f'{variant}-{direction}-upper4x-{bg}.png')
for direction in ['east','south','west']:
    es=[e for e in M['context'] if e['path'].startswith(f'context/{direction}-')]
    sheet=Image.new('RGB',(8*144+20,2*160+40),(48,49,54));dr=ImageDraw.Draw(sheet)
    dr.text((10,8),f'CONTEXT ONLY: {direction} idle and walk | native',(248,248,248))
    for e in es:
        name=Path(e['path']).stem; idle='-idle-' in name;i=int(name[-2:]); row=0 if idle else 1
        x=10+i*144;y=48+row*160
        dr.text((x,y-16),name,fill=(248,248,248));sheet.paste(stage(Image.open(SRC/e['path']).convert('RGBA'),'light',128),(x,y))
    sheet.save(D/f'context-{direction}.png')
# All-cel lower-stride diagnostic, enlarged with nearest-neighbor sampling.
for direction in ['southeast','southwest']:
    sheet=Image.new('RGB',(4*272+20,4*168+42),(48,49,54));dr=ImageDraw.Draw(sheet)
    dr.text((10,8),f'{direction} lower stride x4; A top two rows, B bottom two; stationary guide y112',(245,245,245))
    for vi,v in enumerate(['A','B']):
        for i,e in enumerate(M['variants'][v][direction]):
            bg=Image.new('RGBA',(128,128),(91,98,70,255));bd=ImageDraw.Draw(bg)
            bd.line((0,112,127,112),fill=(132,133,91,255));bg.alpha_composite(Image.open(SRC/e['path']).convert('RGBA'))
            crop=bg.crop((32,80,96,116)).resize((256,144),Image.Resampling.NEAREST).convert('RGB')
            x=10+(i%4)*272;y=42+(vi*2+i//4)*168
            dr.text((x,y-14),f'{v} {i:02d}',fill=(245,245,245));sheet.paste(crop,(x,y))
    sheet.save(D/f'{direction}-lower4x-ground.png')
print(json.dumps({'diagnostic_pngs':len(list(D.glob('*.png'))),'path':str(D)}))

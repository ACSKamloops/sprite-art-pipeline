from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json
ROOT=Path('/home/astra/artifacts/emberwake-five-bridge-review/input-v1')
OUT=Path('/home/astra/artifacts/emberwake-five-bridge-review/review-v1')
D=json.loads((ROOT/'INPUTS.json').read_text())
FONT=ImageFont.load_default()

def background(size,kind):
    col={'dark':(24,29,38),'light':(228,224,212),'ground':(100,111,79)}[kind]
    im=Image.new('RGB',(size,size),col)
    if kind=='ground':
        dr=ImageDraw.Draw(im)
        step=max(4,round(size/8))
        for y in range(0,size,step):
            for x in range(0,size,step):
                if (x//step+y//step)%2:dr.rectangle((x,y,x+step-1,y+step-1),fill=(104,114,82))
                dr.point((min(size-1,x+step//3),min(size-1,y+step//2)),fill=(92,103,71))
    return im

def cell(path,size,kind):
    sp=Image.open(ROOT/path).convert('RGBA')
    if sp.size!=(size,size):sp=sp.resize((size,size),Image.Resampling.NEAREST)
    out=background(size,kind);out.paste(sp,(0,0),sp)
    return out

for size,scale in [(128,'native128'),(256,'nearest2x'),(84,'proxy84')]:
    for bg in ['dark','light','ground']:
        gap=12;top=45;label=23;left=76
        board=Image.new('RGB',(left+8*(size+gap)+gap,top+4*(size+label+gap)),(49,51,57))
        dr=ImageDraw.Draw(board)
        dr.text((10,10),f'{scale} / {bg} | chronological 00..07 | 9/160 s each; 0.45 s loop | full 128 stage; pivot 64,112',font=FONT,fill='white')
        row=0
        for variant in ['A','B']:
            for direction in ['southeast','southwest']:
                y=top+row*(size+label+gap)
                dr.text((8,y+size//2),variant+' '+direction[:2].upper()+direction[5:6].upper(),font=FONT,fill='white')
                for frame,e in enumerate(D['variants'][variant][direction]):
                    x=left+frame*(size+gap)
                    board.paste(cell(e['path'],size,bg),(x,y+label))
                    dr.text((x,y),f'{variant} {direction} {frame:02}',font=FONT,fill='white')
                row+=1
        board.save(OUT/f'{scale}-{bg}.png')

# Every nominated context sprite is shown here, ordered by facing.
size=128;gap=10;left=64;top=42;label=22
board=Image.new('RGB',(left+10*(size+gap)+gap,top+3*(size+label+gap)),(49,51,57))
dr=ImageDraw.Draw(board);dr.text((10,10),'Identity context / native 128 / dark | idle 00,01 then walk 00..07',font=FONT,fill='white')
for row,direction in enumerate(['south','east','west']):
    names=[f'context/{direction}-idle-{f:02}.png' for f in range(2)]+[f'context/{direction}-walk-{f:02}.png' for f in range(8)]
    y=top+row*(size+label+gap);dr.text((6,y+70),direction,font=FONT,fill='white')
    for col,path in enumerate(names):
        x=left+col*(size+gap);board.paste(cell(path,size,'dark'),(x,y+label));dr.text((x,y),path.rsplit('/',1)[-1],font=FONT,fill='white')
board.save(OUT/'context-native.png')
Image.open(ROOT/'context/appearance.png').convert('RGB').save(OUT/'context-appearance.png')

# Cyclic pair boards preserve duplicate neighbors explicitly, including 07->00.
for variant in ['A','B']:
    for direction in ['southeast','southwest']:
        size=128;pw=2*size+14;ph=size+28;gap=12;top=40
        board=Image.new('RGB',(4*(pw+gap)+gap,top+2*(ph+gap)+gap),(49,51,57))
        dr=ImageDraw.Draw(board);dr.text((12,12),f'{variant} {direction} | all cyclic adjacent pairs | native128 / light',font=FONT,fill='white')
        for i in range(8):
            x=gap+(i%4)*(pw+gap);y=top+(i//4)*(ph+gap);j=(i+1)%8
            dr.text((x,y),f'{i:02} -> {j:02}',font=FONT,fill='white')
            for k,idx in enumerate([i,j]):board.paste(cell(D['variants'][variant][direction][idx]['path'],size,'light'),(x+k*(size+14),y+24))
        board.save(OUT/f'pairs-{variant}-{direction}.png')

# Numerical differences locate evidence only; they do not confer an artistic score.
diffs={}
for direction in ['southeast','southwest']:
    diffs[direction]=[]
    for i in range(8):
        a=Image.open(ROOT/D['variants']['A'][direction][i]['path']).convert('RGBA')
        b=Image.open(ROOT/D['variants']['B'][direction][i]['path']).convert('RGBA')
        changed=[(x,y) for y in range(128) for x in range(128) if a.getpixel((x,y))!=b.getpixel((x,y))]
        bbox=[min(x for x,y in changed),min(y for x,y in changed),max(x for x,y in changed)+1,max(y for x,y in changed)+1] if changed else None
        diffs[direction].append({'frame':i,'changed_pixel_count':len(changed),'bbox':bbox})
(OUT/'difference-locations.json').write_text(json.dumps(diffs,indent=2)+'\n')
print(json.dumps({'diagnostic_pngs':len(list(OUT.glob('*.png'))),'differences':diffs},indent=2))

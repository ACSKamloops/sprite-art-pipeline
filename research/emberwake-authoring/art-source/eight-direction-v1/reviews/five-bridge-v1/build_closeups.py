from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path('/home/astra/artifacts/emberwake-five-bridge-review/input-v1')
OUT=Path('/home/astra/artifacts/emberwake-five-bridge-review/review-v1')
D=json.loads((ROOT/'INPUTS.json').read_text());FONT=ImageFont.load_default()
CROP=(40,68,91,118);W=204;H=200
colors={'dark':(24,29,38),'light':(228,224,212),'ground':(100,111,79)}
for direction in ['southeast','southwest']:
    board=Image.new('RGB',(6*(W+12)+12,3*(H+32)+46),(49,51,57));dr=ImageDraw.Draw(board)
    dr.text((12,12),f'{direction} 04->05->06 | A left triplet; B right triplet | lower-body crop x40:91 y68:118; nearest4x',font=FONT,fill='white')
    for row,bg in enumerate(['dark','light','ground']):
        for col,(variant,frame) in enumerate([(v,f) for v in ['A','B'] for f in [4,5,6]]):
            sp=Image.open(ROOT/D['variants'][variant][direction][frame]['path']).convert('RGBA').crop(CROP).resize((W,H),Image.Resampling.NEAREST)
            cell=Image.new('RGB',(W,H),colors[bg]);cell.paste(sp,(0,0),sp)
            x=12+col*(W+12);y=46+row*(H+32)
            board.paste(cell,(x,y+22));dr.text((x,y),f'{variant} {frame:02} {bg}',font=FONT,fill='white')
    board.save(OUT/f'closeup-040506-{direction}.png')
# All lower bodies in chronology, preserving their stage alignment.
W=153;H=150
board=Image.new('RGB',(8*(W+12)+76,4*(H+30)+40),(49,51,57));dr=ImageDraw.Draw(board)
dr.text((12,12),'Lower bodies / all chronology / nearest3x crop / light',font=FONT,fill='white')
for row,(v,d) in enumerate([(v,d) for v in ['A','B'] for d in ['southeast','southwest']]):
    for f in range(8):
        sp=Image.open(ROOT/D['variants'][v][d][f]['path']).convert('RGBA').crop(CROP).resize((W,H),Image.Resampling.NEAREST)
        cell=Image.new('RGB',(W,H),colors['light']);cell.paste(sp,(0,0),sp)
        x=64+f*(W+12);y=40+row*(H+30);board.paste(cell,(x,y+22));dr.text((x,y),f'{v} {d} {f:02}',font=FONT,fill='white')
board.save(OUT/'lower-bodies-all.png')
print('Created three bounded lower-body sheets.')

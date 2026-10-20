#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
ground=Image.open(ROOT/'inputs/game-ground-crop.png').convert('RGBA')
records=[]
holds=[80,100,80]
def backdrop(name,size):
    if name=='game':return ground.resize((size,size),Image.Resampling.NEAREST)
    return Image.new('RGBA',(size,size),'#dedbd0' if name=='light' else '#24272b')
def frame(variant,n,bg,size):
    im=Image.open(ROOT/('inputs/current' if variant=='before' else 'trial')/f'{n}.png').convert('RGBA')
    if size!=128:im=im.resize((size,size),Image.Resampling.NEAREST)
    tile=backdrop(bg,size);tile.alpha_composite(im);return tile
for bg in ['light','dark','game']:
    for size in [128,84,256]:
        pad=12;label=70;top=28
        sheet=Image.new('RGB',(label+3*(size+pad)+pad,top+2*(size+pad)+22),'#c7c5bc')
        d=ImageDraw.Draw(sheet)
        for j,n in enumerate([17,18,19]):d.text((label+j*(size+pad)+4,6),f'{n}: {holds[j]}ms',fill='black')
        for row,variant in enumerate(['before','trial']):
            d.text((6,top+row*(size+pad)+size//2),variant,fill='black')
            tiles=[]
            for j,n in enumerate([17,18,19]):
                tile=frame(variant,n,bg,size);sheet.paste(tile,(label+j*(size+pad),top+row*(size+pad)));tiles.append(tile)
            # A one-shot excerpt retains native holds, with no artificial loop wrap.
            apng=ROOT/'proofs'/f'{variant}-{bg}-{size}-oneshot.png'
            tiles[0].save(apng,format='PNG',save_all=True,append_images=tiles[1:],duration=holds,loop=1,disposal=0,blend=0)
            dec=Image.open(apng)
            assert dec.n_frames==3
            got=[]
            for i,t in enumerate(tiles):
                dec.seek(i);assert dec.convert('RGBA').tobytes()==t.tobytes();got.append(dec.info['duration'])
            assert got==holds
            records.append({'file':str(apng.relative_to(ROOT)),'sha256':hashlib.sha256(apng.read_bytes()).hexdigest(),'decoded_rgba_exact':True,'holds_ms':got,'plays':1})
        d.text((6,sheet.height-17),f'{size}px stage / nearest; {bg}; offline composite, no engine claim',fill='black')
        sheet.save(ROOT/'proofs'/f'before-trial-{bg}-{size}.png')
# One convenient native 84 triptych, with each background presented at actual size.
files=[Image.open(ROOT/'proofs'/f'before-trial-{bg}-84.png') for bg in ['light','dark','game']]
board=Image.new('RGB',(max(i.width for i in files),sum(i.height for i in files)+72),'#c7c5bc');d=ImageDraw.Draw(board);y=0
for bg,im in zip(['light','dark','game'],files):
    d.text((6,y+4),bg+' / 84px before and trial',fill='black');y+=24;board.paste(im,(0,y));y+=im.height
board.save(ROOT/'proofs/84-all-backgrounds.png')
(ROOT/'proofs/MEDIA-RECEIPT.json').write_text(json.dumps({'schema':'emberwake-bounded-cast-material-proof/v1','sequence':[17,18,19],'holds_ms':holds,'duration_ms':260,'scale_84':'Explicit128-to84 nearest proof; actual engine draw_scale0.66 is not asserted pixel-identical','background_game':'Exact crop of shipped ground texture, offline composite only','records':records},indent=2)+'\n')
html='''<!doctype html><meta charset="utf-8"><title>Rowan NE material pass — unselected</title><style>body{background:#c7c5bc;color:#111;font:15px sans-serif}img{image-rendering:pixelated;max-width:none}p{max-width:900px}.row{display:flex;gap:16px}button{margin:8px}</style><h1>Unselected material pass</h1><p>Before above trial. Only current17/18 metal cuff/elbow shading; original19 retained. Alpha, geometry, hand and timing exact. Offline composites; no engine/editor/full-bank check or score.</p><button onclick="document.querySelectorAll('img[data-replay]').forEach(x=>{let s=x.src.split('?')[0];x.src=s+'?t='+Date.now()})">Replay one-shot excerpts</button>'''
for bg in ['light','dark','game']:
    for size in [84,128,256]:
        html+=f'<h2>{bg} / {size}px</h2><img src="before-trial-{bg}-{size}.png"><div class="row">'
        for v in ['before','trial']:html+=f'<div>{v}<br><img data-replay src="{v}-{bg}-{size}-oneshot.png"></div>'
        html+='</div>'
(ROOT/'proofs/index.html').write_text(html)
print('Nine paired strips and eighteen exact one-shot APNGs.')

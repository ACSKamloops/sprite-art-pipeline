from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, csv, base64
IN=Path('../input-v1')
OUT=Path('.')
manifest=json.loads((IN/'INPUTS.json').read_text())
(OUT/'diagnostics').mkdir(exist_ok=True)
FONT=ImageFont.load_default()
BGS={'light':(233,228,215),'dark':(25,30,36),'ground':(86,105,72)}
chron=[7,0,1,2,3,4,5,6,7,0]

def background(size, name):
 im=Image.new('RGB',size,BGS[name])
 if name=='ground':
  d=ImageDraw.Draw(im)
  for y in range(0,size[1],16):
   for x in range((y//16%2)*8,size[0],24):
    d.line((x,y,x+5,y),fill=(99,116,80))
    d.point((x+9,y+8),fill=(73,91,63))
 return im

def composite(im, bg):
 b=background(im.size,bg); b.paste(im,(0,0),im); return b

ledger=[]
for actor, data in manifest['actors'].items():
 for direction,frames in data['diagonals'].items():
  for idx,f in enumerate(frames):
   p=IN/f['path']; raw=p.read_bytes(); im=Image.open(p).convert('RGBA')
   actual=hashlib.sha256(raw).hexdigest()
   ledger.append({'path':f['path'],'purpose':'diagonal reviewed in every requested scale/background','sha256':actual,'expected_sha256':f['sha256'],'matches':actual==f['sha256'],'size':list(im.size),'alpha_bbox':list(im.getbbox()) if im.getbbox() else None})
  source=[Image.open(IN/f['path']).convert('RGBA') for f in frames]
  for mode in ('native','nearest2x','game066'):
   if mode=='native': scale=1; crop=None; w,h=128,128
   elif mode=='nearest2x': scale=2; crop=(24,8,104,120); w,h=160,224
   else: scale=.66; crop=None; w,h=84,84
   cw,ch=w+8,h+24
   sheet=Image.new('RGB',(cw*10,ch*3+28),(56,58,63)); d=ImageDraw.Draw(sheet)
   d.text((6,6),f'{actor} {direction} | {mode} | 07 -> 00 -> 01 ... 07 -> 00 | full-cycle adjacency',fill='white',font=FONT)
   for row,bg in enumerate(BGS):
    for col,idx in enumerate(chron):
     im=source[idx]
     if crop: im=im.crop(crop)
     if mode=='game066': im=im.resize((84,84),Image.Resampling.NEAREST)
     elif scale!=1: im=im.resize((w,h),Image.Resampling.NEAREST)
     cell=composite(im,bg)
     x=col*cw+4; y=28+row*ch+20
     sheet.paste(cell,(x,y)); d.text((x,y-15),f'{bg} {idx:02d}',fill='white',font=FONT)
   sheet.save(OUT/'diagnostics'/f'{actor}-{direction}-{mode}.png')
 for direction,kind in data['neighbors'].items():
  for typ,frames in kind.items():
   for f in frames:
    p=IN/f['path']; raw=p.read_bytes(); im=Image.open(p).convert('RGBA'); actual=hashlib.sha256(raw).hexdigest()
    ledger.append({'path':f['path'],'purpose':'cardinal identity and turn context only','sha256':actual,'expected_sha256':f['sha256'],'matches':actual==f['sha256'],'size':list(im.size),'alpha_bbox':list(im.getbbox()) if im.getbbox() else None})
 # Native cardinal contact sheet, all supplied keys but no cardinal motion score.
 cw,ch=136,148
 sheet=Image.new('RGB',(cw*10,ch*4+28),(56,58,63)); d=ImageDraw.Draw(sheet)
 d.text((6,6),f'{actor} cardinal identity/turn context; idle00, walk00..07, idle01',fill='white',font=FONT)
 for row,(direction,data2) in enumerate(data['neighbors'].items()):
  fs=[data2['idle'][0]]+data2['walk']+[data2['idle'][1]]
  for col,f in enumerate(fs):
   im=Image.open(IN/f['path']).convert('RGBA'); x=col*cw+4; y=28+row*ch+16
   sheet.paste(composite(im,'light'),(x,y)); d.text((x,y-13),f'{direction} {col:02d}',fill='white',font=FONT)
 sheet.save(OUT/'diagnostics'/f'{actor}-cardinal-context-native.png')
for actor in manifest['actors']:
 name=f'{actor}-reference.png'; p=IN/name; raw=p.read_bytes(); im=Image.open(p)
 ledger.append({'path':name,'purpose':'character identity reference','sha256':hashlib.sha256(raw).hexdigest(),'expected_sha256':None,'matches':None,'size':list(im.size),'alpha_bbox':None})
 im.save(OUT/'diagnostics'/name)
for actor in manifest['actors']:
 sheet=Image.new('RGB',(8*232,2*252),(35,39,43)); d=ImageDraw.Draw(sheet)
 for row,direction in enumerate(('southeast','northeast')):
  for col,idx in enumerate(range(8)):
   im=Image.open(IN/actor/direction/f'{idx:02}.png').convert('RGBA').crop((34,65,92,121)).resize((232,224),Image.Resampling.NEAREST)
   b=Image.new('RGB',im.size,(233,228,215)); b.paste(im,(0,0),im)
   sheet.paste(b,(col*232,row*252+24)); d.text((col*232+5,row*252+5),f'{actor} {direction} {idx:02} lower body x4',fill='white')
 sheet.save(OUT/'diagnostics'/f'{actor}-local-lowerbody-4x.png')
# An offline playback aid for subsequent human checking. It is not evidence of
# continuous playback observation by this reviewer.
loops=[]
for actor,data in manifest['actors'].items():
 for direction,frames in data['diagonals'].items():
  loops.append({'name':f'{actor} {direction}','frames':['data:image/png;base64,'+base64.b64encode((IN/f['path']).read_bytes()).decode() for f in frames]})
html='''<!doctype html><meta charset="utf-8"><title>Cold review playback aid</title>
<style>body{font:15px system-ui;background:#30343a;color:white}button,select{margin:4px;padding:8px}.grid{display:grid;grid-template-columns:repeat(4,max-content);gap:16px}.cell{padding:12px;border:1px solid #70757c}.stage{image-rendering:pixelated;display:block;background:#e9e4d7}.note{max-width:900px}</style>
<p class="note">Offline playback aid. All eight keys, equal 56.25 ms holds, 450 ms cycle. The reviewer did not observe continuous playback. At scale .66 the CSS stage is exactly 84.48 px; nearest sampling and screen refresh depend on the browser. Contact and translation are not tested here.</p>
<button id="play">Pause</button><button id="prev">Previous</button><button id="next">Next</button>
<select id="scale"><option value=".66">.66 game scale</option><option value="1">Native</option><option value="2">Nearest 2×</option></select>
<select id="bg"><option value="#e9e4d7">Light</option><option value="#191e24">Dark</option><option value="#566948">Ground color</option></select><span id="clock"></span><div class="grid" id="grid"></div>
<script>const loops=LOOP_DATA;let running=true,phase=0,last=performance.now();const canvases=[];
for(const loop of loops){const cell=document.createElement('div');cell.className='cell';const label=document.createElement('p');label.textContent=loop.name;cell.append(label);const canvas=document.createElement('canvas');canvas.width=canvas.height=128;canvas.className='stage';cell.append(canvas);grid.append(cell);loop.images=loop.frames.map(src=>{const im=new Image;im.src=src;return im});canvases.push(canvas)}
function style(){const px=128*Number(scale.value);for(const c of canvases){c.style.width=c.style.height=px+'px';c.style.background=bg.value}}style();scale.onchange=bg.onchange=style;
play.onclick=()=>{running=!running;play.textContent=running?'Pause':'Play'};function step(n){running=false;play.textContent='Play';phase=((Math.floor(phase/56.25)+n+8)%8)*56.25}prev.onclick=()=>step(-1);next.onclick=()=>step(1);
function tick(t){if(running)phase=(phase+t-last)%450;last=t;const idx=Math.floor(phase/56.25)%8;clock.textContent='Key '+String(idx).padStart(2,'0');for(let i=0;i<loops.length;i++){const c=canvases[i],ctx=c.getContext('2d');ctx.clearRect(0,0,128,128);ctx.imageSmoothingEnabled=false;const im=loops[i].images[idx];if(im.complete)ctx.drawImage(im,0,0)}requestAnimationFrame(tick)}requestAnimationFrame(tick);</script>'''
(OUT/'playback.html').write_text(html.replace('LOOP_DATA',json.dumps(loops)))
ledger.insert(0,{'path':'INPUTS.json','purpose':'review authority and chronology','sha256':hashlib.sha256((IN/'INPUTS.json').read_bytes()).hexdigest()})
(OUT/'source-hash-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
with (OUT/'source-hash-ledger.tsv').open('w') as f:
 writer=csv.writer(f,delimiter='\t');writer.writerow(['sha256','expected_match','path','purpose'])
 for r in ledger:writer.writerow([r['sha256'],r.get('matches','n/a'),r['path'],r['purpose']])
print(json.dumps({'sources':len(ledger),'mismatches':[r['path'] for r in ledger if r.get('matches') is False],'sheets':len(list((OUT/'diagnostics').glob('*.png')))},indent=2))

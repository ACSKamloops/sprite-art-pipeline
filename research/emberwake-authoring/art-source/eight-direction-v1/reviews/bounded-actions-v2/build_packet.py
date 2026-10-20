from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,html

OUT=Path(__file__).resolve().parent
BASE=Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1')
HYBRID=Path('/home/astra/artifacts/emberwake-diagonal-cast-hybrid-v1/candidate')
REG=BASE/'registered-v1'
BG={'light':(222,226,221),'dark':(28,33,40),'ground':(111,108,77)}
SMALL_FILTER=Image.Resampling.LANCZOS
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',10)
BOLD=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
entries={}
cases=[]
def source(p):
 p=p.resolve(); key=str(p)
 if key not in entries:
  rel=('hybrid/'+p.relative_to(HYBRID).as_posix()) if p.is_relative_to(HYBRID) else ('art/'+p.relative_to(BASE).as_posix())
  dst=OUT/'sources'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
  b=p.read_bytes()
  with Image.open(p) as im: size=list(im.size);mode=im.mode
  entries[key]={'source_path':str(p),'packet_path':dst.relative_to(OUT).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'size':size,'mode':mode}
 return entries[key]['packet_path']
for view in ['southeast','northeast']:
 frames=[22,17,18,19,20,22]
 control=[source(REG/'rowan'/view/f'{f}.png') for f in frames]
 trial=[source(HYBRID/view/f'{f}.png') if f in [17,18,20] else source(REG/'rowan'/view/f'{f}.png') for f in frames]
 cases.append({'id':f'rowan-{view}-cast','actor':'rowan','action':'cast','view':view,'frames':frames,'duration_ms':[60,80,100,80,80,100],'variants':{'control':control,'trial':trial},'context':None})
for actor in ['rowan','lyra','brann']:
 for view in ['southeast','northeast']:
  frames=[24,25,22]
  control=[source(REG/actor/view/f'{f}.png') for f in frames]
  trial=[source(BASE/'hurt-recovery-v1'/actor/view/'25.png') if f==25 else source(REG/actor/view/f'{f}.png') for f in frames]
  cases.append({'id':f'{actor}-{view}-hurt','actor':actor,'action':'hurt','view':view,'frames':frames,'duration_ms':[90,100,100],'variants':{'control':control,'trial':trial},'context':source(REG/actor/view/'22.png')})
cases.append({'id':'brann-southeast-idle','actor':'brann','action':'idle','view':'southeast','frames':[22,23],'duration_ms':[580,580],'variants':{'control':[source(REG/'brann'/'southeast'/f'{f}.png') for f in [22,23]],'trial':[source(BASE/'brann-eye-v1'/'22.png'),source(BASE/'breath-v2'/'brann'/'southeast'/'23.png')]},'context':None})
references={a:source(BASE/'references'/f'{a}-appearance.png') for a in ['rowan','lyra','brann']}
manifest={'review_scope':'Independent bounded visible art comparison; no producer reports or earlier reviews read.','sources':list(entries.values()),'references_identity_only':references,'cases':cases,'rendering':{'native_pixels':[128,128],'small_scale_requested':0.66,'small_pixels':[84,84],'small_scale_actual':84/128,'resampling':'Native unchanged; .66 display in both Pillow LANCZOS proxy and NEAREST runtime-filter matching views; originals untouched','backgrounds_rgb':BG,'ground':'flat muted olive gray; no additional external art','animation_loop':0,'animation_timing':'exact milliseconds supplied for each source sequence; neutral hurt context is separate untimed entry','synchronization':'variants are packed into the same animation frame and share each clock','pair_order':'every adjacent pair, plus last-to-first loop; hurt includes separate neutral22-to-24 context pair'}}
(OUT/'inputs.json').write_text(json.dumps(manifest,indent=2)+'\n')

def load(rel,side):
 im=Image.open(OUT/rel).convert('RGBA')
 return im if im.size==(side,side) else im.resize((side,side),SMALL_FILTER)
def draw_tile(canvas,rel,xy,side,bg):
 x,y=xy;canvas.paste(bg,(x,y,x+side,y+side));im=load(rel,side);canvas.paste(im,(x,y),im)

def storyboard(c,scale,bgname):
 side=128 if scale=='native' else 84
 variants=c['variants']; rows=len(variants); include_ctx=bool(c['context'])
 n=len(c['frames'])+include_ctx; labelw=145; gap=18; top=60; rowh=side+34
 im=Image.new('RGB',(labelw+n*(side+gap)+10,top+rows*rowh+10),(246,246,242));d=ImageDraw.Draw(im)
 d.text((12,9),f"{c['id']} | {scale} | {bgname}",font=BOLD,fill=(15,18,22))
 d.text((12,32),'Hurt context22 is untimed; clocks belong to action frames. All source canvases preserved.',font=SMALL,fill=(40,44,48))
 for r,(name,seq) in enumerate(variants.items()):
  y=top+r*rowh;d.text((10,y+side//2),name,font=FONT,fill=(15,18,22))
  names=[f'{f} / {ms}ms' for f,ms in zip(c['frames'],c['duration_ms'])]
  if include_ctx:seq=[c['context']]+seq; names=['context22 / --']+names
  for i,(rel,label) in enumerate(zip(seq,names)):
   x=labelw+i*(side+gap);draw_tile(im,rel,(x,y),side,BG[bgname]);d.text((x,y+side+5),label,font=SMALL,fill=(15,18,22))
 return im

def pair_sheet(c,scale,bgname):
 side=128 if scale=='native' else 84; labelw=145;gap=16;top=66
 pairs=[]
 if c['context']:pairs.append(('context22 > 24',None,0))
 for i in range(len(c['frames'])-1):pairs.append((f"{c['frames'][i]} > {c['frames'][i+1]}",i,i+1))
 pairs.append((f"{c['frames'][-1]} > {c['frames'][0]} (loop)",len(c['frames'])-1,0))
 colw=side*2+gap+22; maxcols=3;cols=min(len(pairs),maxcols);blocks=(len(pairs)+cols-1)//cols
 blockh=30+len(c['variants'])*(side+10)
 im=Image.new('RGB',(labelw+cols*colw+10,top+blocks*blockh+10),(246,246,242));d=ImageDraw.Draw(im)
 d.text((12,9),f"All adjacent / recovery pairs | {c['id']} | {scale} | {bgname}",font=BOLD,fill=(15,18,22))
 d.text((12,33),'Left frame > right frame. Loop pair explicit; hurt neutral context entry included.',font=SMALL,fill=(40,44,48))
 for p,(label,a,b) in enumerate(pairs):
  row,col=divmod(p,cols);x=labelw+col*colw;y=top+row*blockh;d.text((x,y),label,font=FONT,fill=(15,18,22))
  for v,(name,seq) in enumerate(c['variants'].items()):
   yy=y+25+v*(side+10)
   if col==0:d.text((10,yy+side//2),name,font=SMALL,fill=(15,18,22))
   draw_tile(im,c['context'] if a is None else seq[a],(x,yy),side,BG[bgname]);draw_tile(im,seq[b],(x+side+gap,yy),side,BG[bgname])
 return im

def animation(c,scale,bgname):
 side=128 if scale=='native' else 84; gap=18; top=52;labelh=28;variants=c['variants'];w=len(variants)*(side+gap)+10;h=top+side+labelh
 result=[]
 for i in range(len(c['frames'])):
  im=Image.new('RGB',(w,h),(246,246,242));d=ImageDraw.Draw(im);d.text((10,8),f"{c['actor']} {c['action']} {c['view']}",font=SMALL,fill=(15,18,22))
  d.text((10,25),f"{c['frames'][i]} | {c['duration_ms'][i]} ms | {scale}",font=SMALL,fill=(15,18,22))
  for v,(name,seq) in enumerate(variants.items()):
   x=10+v*(side+gap);draw_tile(im,seq[i],(x,top),side,BG[bgname]);d.text((x,top+side+6),name,font=SMALL,fill=(15,18,22))
  result.append(im)
 return result

for c in cases:
 folder=OUT/'comparisons'/c['id'];folder.mkdir(parents=True,exist_ok=True)
 for bgname in BG:
  for scale in ['native','066']:
   storyboard(c,scale,bgname).save(folder/f'{bgname}-{scale}-sequence.png')
   pair_sheet(c,scale,bgname).save(folder/f'{bgname}-{scale}-pairs.png')
   frames=animation(c,scale,bgname);frames[0].save(folder/f'{bgname}-{scale}-matched.gif',save_all=True,append_images=frames[1:],duration=c['duration_ms'],loop=0,disposal=2,optimize=False)
 # compact overview retains actual 128 and 84 pixel figures, across all backgrounds
 ims=[storyboard(c,scale,bgname) for bgname in BG for scale in ['native','066']]
 overview=Image.new('RGB',(max(x.width for x in ims),sum(x.height for x in ims)+10*(len(ims)-1)),(246,246,242));y=0
 for im in ims:overview.paste(im,(0,y));y+=im.height+10
 overview.save(folder/'overview.png')

# Identity-only references, copies unaltered within labeled sheet.
refsheet=Image.new('RGBA',(800,3*300),(235,237,231,255));d=ImageDraw.Draw(refsheet)
for i,(actor,rel) in enumerate(references.items()):
 d.text((12,i*300+8),actor+' appearance reference - identity only',font=BOLD,fill=(15,18,22,255));im=Image.open(OUT/rel).convert('RGBA');refsheet.alpha_composite(im,(12,i*300+35))
refsheet.convert('RGB').save(OUT/'identity-references.png')
parts=['<!doctype html><html><head><meta charset="utf-8"><title>Bounded art review packet</title><style>body{font:15px system-ui;background:#eee;color:#172024;margin:20px}img{max-width:100%;height:auto}section{margin:30px 0;border-top:2px solid #888}.anim{display:flex;gap:24px;flex-wrap:wrap}figure{margin:10px}a{color:#145780}</style></head><body><h1>Bounded action comparison</h1><p>Exact copied source inputs and clocks are in <a href="inputs.json">inputs.json</a>. Native 128px / requested 0.66 scale rendered at 84px. GIF variants share one frame clock; hurt neutral22 is separate untimed context. Appearance references are for identity only.</p><p><a href="identity-references.png">Identity references</a></p>']
for c in cases:
 root='comparisons/'+c['id'];parts.append('<section><h2>'+html.escape(c['id'])+'</h2>')
 for bgname in BG:
  parts.append('<h3>'+bgname+'</h3><div class="anim">')
  for scale in ['native','066']:parts.append(f'<figure><figcaption>{scale}</figcaption><img src="{root}/{bgname}-{scale}-matched.gif"></figure>')
  parts.append('</div>')
  for scale in ['native','066']:parts.append(f'<p><a href="{root}/{bgname}-{scale}-sequence.png">{scale} full sequence</a> | <a href="{root}/{bgname}-{scale}-pairs.png">{scale} all adjacent/recovery pairs</a></p>')
 parts.append('</section>')
parts.append('</body></html>');(OUT/'index.html').write_text('\n'.join(parts)+'\n')
print(json.dumps({'sources':len(entries),'cases':len(cases),'variants':sum(len(c['variants']) for c in cases),'source_images_copied_exactly':True,'output':str(OUT)},indent=2))

# Additional .66 comparisons matching the declared Godot NEAREST filtering.
SMALL_FILTER=Image.Resampling.NEAREST
for c in cases:
 folder=OUT/'comparisons'/c['id']
 ims=[]
 for bgname in BG:
  seq=storyboard(c,'066-nearest',bgname)
  seq.save(folder/f'{bgname}-066-nearest-sequence.png')
  pair_sheet(c,'066-nearest',bgname).save(folder/f'{bgname}-066-nearest-pairs.png')
  frames=animation(c,'066-nearest',bgname)
  frames[0].save(folder/f'{bgname}-066-nearest-matched.gif',save_all=True,append_images=frames[1:],duration=c['duration_ms'],loop=0,disposal=2,optimize=False)
  ims.append(seq)
 overview=Image.new('RGB',(max(x.width for x in ims),sum(x.height for x in ims)+10*(len(ims)-1)),(246,246,242));y=0
 for im in ims:overview.paste(im,(0,y));y+=im.height+10
 overview.save(folder/'nearest-066-overview.png')
with (OUT/'index.html').open('a') as f:
 f.write('<section><h2>NEAREST .66 runtime-filter comparisons</h2><p>84px nearest-neighbor sprites. Native views above preserve their source pixels.</p>')
 for c in cases:
  root='comparisons/'+c['id']
  f.write('<h3>'+c['id']+'</h3>')
  for bgname in BG:
   f.write(f'<p>{bgname} <a href="{root}/{bgname}-066-nearest-sequence.png">sequence</a> | <a href="{root}/{bgname}-066-nearest-pairs.png">pairs</a></p><img src="{root}/{bgname}-066-nearest-matched.gif">')
 f.write('</section>')

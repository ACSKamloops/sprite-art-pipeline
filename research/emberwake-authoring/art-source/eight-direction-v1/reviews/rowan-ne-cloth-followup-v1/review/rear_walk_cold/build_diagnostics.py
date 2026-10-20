from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import hashlib,json
root=Path('/home/astra/artifacts/emberwake-rowan-ne-cloth-followup-v1');src=root/'input';out=root/'review/rear_walk_cold'
m=json.loads((src/'INPUTS.json').read_text());font=ImageFont.load_default()
anchor={'northeast':['c88e1d925a77784038c4bb6afa78ba11f5838b5d66555e7b0cf7b103ba372bfc','a8777ab1305a5769e23a1848317afdeb0d4175476bbf37216ba30fc683010bae','ba7fbc391d3ec25a40d12f6f4f73b773b1d8e1d220c73c166b8cb33026b2f357','f6684cff2278d8a1724b8c48b0b814877355fcf33e49b250166c5b8fcad6dd60','fd629e8f1b0603a4d3d8780cfec7a7b6a548c7f9d86fa7be83456c49ee3cbe6c','17ee266228ff4d64a3890d3ae4393e8b6d35d6919a27ffb0755737f5621801f7','5e652adc0dafe96ed2747dc6b8bdffd68f800f1b34f04fe7e142e318e407fa0b','407c13cba75d3db81b30bd3d304ffe4c22298dedee20f8ff12154e88dbd94d37'],
'northwest':['70180504ae3ce13998d9b3167a952589957b69d4b2cc3a282378ba122c452fe1','5a0553e00aab6485473f6f1a725f0a0380a3d3d9fb0d5d0cbed3ee9ccc899a8c','af90441c00d55326c27ebc6431c250db9a25a33918ea7de2cde37ce2c1e4b00f','d7fa4608996c222941c3e60c3002a5366100949007b0f4280ed461c745f32d0c','21f7eb97054aba488ceda1151d22a32f05a761594ab6792303333b2faacc6c33','fa4aad7cbf33f43506824a22c1178eb30e279f6de244cbb7a4e5518bebe30861','11387ba57887149610cbce10b565311abe2e56d286996a6afcfa0a95836b531a','8aa6ff0fa20899bf8a5478b684f735c2a44674f23cc5f68c5ae3c0195a7e8bc3']}
entries=m['context']+[e for v in m['variants'].values() for d in v.values() for e in d]
rec={'manifest_sha256':hashlib.sha256((src/'INPUTS.json').read_bytes()).hexdigest(),'files':[],'anchor_matches':{},'scope_difference_bboxes':{}}
for e in entries:
 h=hashlib.sha256((src/e['path']).read_bytes()).hexdigest();rec['files'].append({'path':e['path'],'sha256':h,'manifest_match':h==e['sha256']})
for di in anchor:
 rec['anchor_matches'][di]=[hashlib.sha256((src/'A'/di/f'{i:02}.png').read_bytes()).hexdigest()==anchor[di][i] for i in range(8)];rec['scope_difference_bboxes'][di]={}
 for i in range(8):
  a=Image.open(src/'A'/di/f'{i:02}.png').convert('RGBA');b=Image.open(src/'B'/di/f'{i:02}.png').convert('RGBA');dif=ImageChops.difference(a,b);bbox=dif.convert('RGB').getbbox();ab=dif.getchannel('A').getbbox()
  if ab:bbox=(min(bbox[0],ab[0]),min(bbox[1],ab[1]),max(bbox[2],ab[2]),max(bbox[3],ab[3])) if bbox else ab
  rec['scope_difference_bboxes'][di][f'{i:02}']=bbox
assert all(x['manifest_match'] for x in rec['files']);assert all(all(v) for v in rec['anchor_matches'].values())
(out/'input-before.json').write_text(json.dumps(rec,indent=2)+'\n');print('All63PNG manifest matches;A matches all16 immediately prior B hashes.');print(json.dumps(rec['scope_difference_bboxes']))
def tile(p,s,back):
 colors={'light':(235,230,215,255),'dark':(27,32,43,255),'muted':(111,125,112,255)}
 im=Image.new('RGBA',(s,s),colors[back]);d=ImageDraw.Draw(im)
 if back=='muted':
  for k in range(0,s,max(1,round(s/8))):d.line((k,0,k,s),fill=(122,137,122,255));d.line((0,k,s,k),fill=(122,137,122,255))
  q=round(s*112/128);piv=round(s/2);d.line((0,q,s,q),fill=(224,204,129,255));d.line((piv,q-3,piv,q+3),fill=(245,119,121,255))
 im.alpha_composite(Image.open(p).convert('RGBA').resize((s,s),Image.Resampling.NEAREST));return im.convert('RGB')
def cell(v,di,i,s,back):return tile(src/v/di/f'{i:02}.png',s,back)
for back in ['light','dark','muted']:
 sh=Image.new('RGB',(1104,1076),(47,47,52));d=ImageDraw.Draw(sh);d.text((5,5),f'Rowan cloth followup {back}: native128 top, nearest84 bottom, columns00..07',font=font,fill='white');y=28
 for s in [128,84]:
  for v,di in [('A','northeast'),('B','northeast'),('A','northwest'),('B','northwest')]:
   d.text((3,y),f'{v} {di} {s}',font=font,fill='white');y+=15
   for i in range(8):sh.paste(cell(v,di,i,s,back),(i*138,y))
   y+=s+9
 sh.save(out/f'{back}-128-84.png')
for di in anchor:
 for half in [0,1]:
  sh=Image.new('RGB',(1064,1726),(47,47,52));d=ImageDraw.Draw(sh);d.text((5,5),f'Rowan {di} nearest2x columns{half*4:02}..{half*4+3:02}',font=font,fill='white');y=25
  for back in ['light','dark','muted']:
   for v in ['A','B']:
    d.text((3,y),f'{v} {back}',font=font,fill='white');y+=16
    for c,i in enumerate(range(half*4,half*4+4)):sh.paste(cell(v,di,i,256,back),(c*266,y))
    y+=266
  sh.save(out/f'{di}-2x-{half}.png')
 sh=Image.new('RGB',(1104,660),(47,47,52));d=ImageDraw.Draw(sh);d.text((5,5),f'Rowan {di} all cyclicpairs includes07->00',font=font,fill='white')
 for z,v in enumerate(['A','B']):
  for i in range(8):
   x=(i%4)*276;y=28+(z*2+i//4)*158;d.text((x+3,y),f'{v}{i:02}->{(i+1)%8:02}',font=font,fill='white')
   for k,j in enumerate([i,(i+1)%8]):sh.paste(cell(v,di,j,128,'muted'),(x+k*136,y+16))
 sh.save(out/f'{di}-pairs.png')
sh=Image.new('RGB',(4*194,6*164+28),(47,47,52));d=ImageDraw.Draw(sh);d.text((5,5),'03 and06 material: A then B; nearest4x; rows light/dark/muted',font=font,fill='white')
for br,back in enumerate(['light','dark','muted']):
 for dr,di in enumerate(anchor):
  y=28+(br*2+dr)*164
  for c,(i,v) in enumerate([(3,'A'),(3,'B'),(6,'A'),(6,'B')]):
   x=c*194;d.text((x+3,y),f'{di} {i:02}{v}',font=font,fill='white');p=cell(v,di,i,128,back).crop((42,76,88,112)).resize((184,144),Image.Resampling.NEAREST);sh.paste(p,(x,y+16))
sh.save(out/'changed-material-detail.png')
sh=Image.new('RGB',(1152,652),(47,47,52));d=ImageDraw.Draw(sh);d.text((5,5),'Supplied cardinal context: identity and turn relationship only',font=font,fill='white')
ctx=sorted(p for p in (src/'context').glob('*.png') if p.name!='appearance.png')
for i,p in enumerate(ctx):
 x=(i%8)*144;y=28+(i//8)*156;sh.paste(tile(p,128,'light'),(x,y));d.text((x+2,y+131),p.stem,font=font,fill='white')
sh.save(out/'cardinal-context.png')

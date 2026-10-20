from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import hashlib,json
root=Path('/home/astra/artifacts/emberwake-brann-ne06-followup-v1');src=root/'input';out=root/'review/rear_walk_cold'
m=json.loads((src/'INPUTS.json').read_text());font=ImageFont.load_default()
anchor={'northeast':['592743e219d4055510426dd4c01300a6b39f23066a551c71c2b86238ddc8e863','7b6f4ff48cd0e5533c4ca5a641aea689c4e8b0397f0f2ae344c911b57a58e2d2','7667dde2c775712730d9bed8e51df6162aeb36650a16cca3ea1d07202d1a3c00','5e20136c8416028d30a41f60ece08be3e3d6d0f10e02c3d3b3f77fa74b230e3f','fcb3af4f3cf7905073f9c94284f2db796ba4466fb7b9a2fe59f9b2f994bcbedc','a8dec5d2d8b18e81c611af6d1f076c86cb7b84ba9deb28ee2523105d21c9d148','d02b930d435b8b08375f4f7c7e0dce1bf495e64c1647e9d6e07afc09f42c6f6c','c3969469747a4d57922d5886c08a2ca2b5a72e9ac91d52e2d5184d98ab348012'],
'northwest':['e61da4b30606eae9537f83b7e4c98b3403e355f3f4e481ef412e2175e3697ec2','2c755e0656f4433c5cfc6c68f76621ffda505f11108925d9241109aadaf22704','b2b4011c9486702bb0fdb378249838ba35283c815e46a10626bf2f94e78d90a0','8fda2c947502809fa256e08921636cdc33c732d82e01b8b197b1328d6192f293','3ff6c0f364cba9447b799671158822fa69f02b0d5276977909947e871957d2d2','46b5479fc2228370ac7dc6d879c5167b4bf565797140b2cd6ac5a9371053d915','b76a0fbcda3acff7c7e70cd45175945f8d98c7b79d7b3207aa84153b20045bdd','13135275c0507b5212a1891e8ffeb6c1fad090c74693dc25dce6a048464692a7']}
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
(out/'input-before.json').write_text(json.dumps(rec,indent=2)+'\n');print('All63PNG manifest matches;A matches all16 original review BrannB hashes.');print(json.dumps(rec['scope_difference_bboxes']))
def tile(p,s,back):
 colors={'light':(235,230,215,255),'dark':(27,32,43,255),'muted':(111,125,112,255)}
 im=Image.new('RGBA',(s,s),colors[back]);d=ImageDraw.Draw(im)
 if back=='muted':
  for k in range(0,s,max(1,round(s/8))):d.line((k,0,k,s),fill=(122,137,122,255));d.line((0,k,s,k),fill=(122,137,122,255))
  q=round(s*112/128);piv=round(s/2);d.line((0,q,s,q),fill=(224,204,129,255));d.line((piv,q-3,piv,q+3),fill=(245,119,121,255))
 im.alpha_composite(Image.open(p).convert('RGBA').resize((s,s),Image.Resampling.NEAREST));return im.convert('RGB')
def cell(v,di,i,s,back):return tile(src/v/di/f'{i:02}.png',s,back)
for back in ['light','dark','muted']:
 sh=Image.new('RGB',(1104,1076),(47,47,52));d=ImageDraw.Draw(sh);d.text((5,5),f'Brann06 followup {back}: native128 top, nearest84 bottom, columns00..07',font=font,fill='white');y=28
 for s in [128,84]:
  for v,di in [('A','northeast'),('B','northeast'),('A','northwest'),('B','northwest')]:
   d.text((3,y),f'{v} {di} {s}',font=font,fill='white');y+=15
   for i in range(8):sh.paste(cell(v,di,i,s,back),(i*138,y))
   y+=s+9
 sh.save(out/f'{back}-128-84.png')
for di in anchor:
 for half in [0,1]:
  sh=Image.new('RGB',(1064,1726),(47,47,52));d=ImageDraw.Draw(sh);d.text((5,5),f'Brann {di} nearest2x columns{half*4:02}..{half*4+3:02}',font=font,fill='white');y=25
  for back in ['light','dark','muted']:
   for v in ['A','B']:
    d.text((3,y),f'{v} {back}',font=font,fill='white');y+=16
    for c,i in enumerate(range(half*4,half*4+4)):sh.paste(cell(v,di,i,256,back),(c*266,y))
    y+=266
  sh.save(out/f'{di}-2x-{half}.png')
 sh=Image.new('RGB',(1104,660),(47,47,52));d=ImageDraw.Draw(sh);d.text((5,5),f'Brann {di} all cyclicpairs includes07->00',font=font,fill='white')
 for z,v in enumerate(['A','B']):
  for i in range(8):
   x=(i%4)*276;y=28+(z*2+i//4)*158;d.text((x+3,y),f'{v}{i:02}->{(i+1)%8:02}',font=font,fill='white')
   for k,j in enumerate([i,(i+1)%8]):sh.paste(cell(v,di,j,128,'muted'),(x+k*136,y+16))
 sh.save(out/f'{di}-pairs.png')
sh=Image.new('RGB',(6*194,6*164+28),(47,47,52));d=ImageDraw.Draw(sh);d.text((5,5),'05/06/07 lowerbody: A then B eachcel; nearest4x; crop x42..88 y76..112',font=font,fill='white')
for br,back in enumerate(['light','dark','muted']):
 for dr,di in enumerate(anchor):
  y=28+(br*2+dr)*164
  for c,(i,v) in enumerate([(5,'A'),(5,'B'),(6,'A'),(6,'B'),(7,'A'),(7,'B')]):
   x=c*194;d.text((x+3,y),f'{di} {i:02}{v}',font=font,fill='white');p=cell(v,di,i,128,back).crop((42,76,88,112)).resize((184,144),Image.Resampling.NEAREST);sh.paste(p,(x,y+16))
sh.save(out/'entry-change-exit-detail.png')
sh=Image.new('RGB',(1152,652),(47,47,52));d=ImageDraw.Draw(sh);d.text((5,5),'Supplied cardinal context: identity and turn relationship only',font=font,fill='white')
ctx=sorted(p for p in (src/'context').glob('*.png') if p.name!='appearance.png')
for i,p in enumerate(ctx):
 x=(i%8)*144;y=28+(i//8)*156;sh.paste(tile(p,128,'light'),(x,y));d.text((x+2,y+131),p.stem,font=font,fill='white')
sh.save(out/'cardinal-context.png')

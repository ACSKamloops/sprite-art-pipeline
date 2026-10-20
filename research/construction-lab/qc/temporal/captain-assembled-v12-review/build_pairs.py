from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
base=Path('/home/astra/projects/sprite-construction-lab/pilot/space-marine-captain/assembled-v12')
out=Path(__file__).resolve().parent
m=json.loads((base/'manifest.json').read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert len(m['frames'])==72
ims=[]
for f in m['frames']:
 assert h(base/f['file'])==f['sha256']
 ims.append(Image.open(base/f['file']).convert('RGBA'))
pages=[]
for start in range(0,72,4):
 page=Image.new('RGB',(1024,560),(33,40,46));d=ImageDraw.Draw(page)
 for n in range(4):
  a=start+n;b=(a+1)%72;x=(n%2)*512;y=(n//2)*280
  d.text((x+4,y+3),f'{a:02d} -> {b:02d}'+(' LOOP' if b==0 else ''),fill='white')
  page.paste(ims[a],(x,y+24),ims[a]);page.paste(ims[b],(x+256,y+24),ims[b])
 path=out/f'pairs-{start:02d}.png';page.save(path);pages.append({'file':path.name,'sha256':h(path),'pair_start':start,'pair_end':start+3})
for i in [0,18,36,54]:
 bg=Image.new('RGB',(256,256),(33,40,46));bg.paste(ims[i],(0,0),ims[i]);bg.resize((512,512),Image.Resampling.NEAREST).save(out/f'key-{i:02d}-2x.png')
(out/'input-binding.json').write_text(json.dumps({'manifest':str(base/'manifest.json'),'manifest_sha256':h(base/'manifest.json'),'frames':m['frames'],'pages':pages,'scope':'Algorithm verifies hashes and assembles fixed canvas pairs; art review requires personal viewing.'},indent=2)+'\n')
print('72 frames verified; 71 adjacent+1 wrap;18 pages')

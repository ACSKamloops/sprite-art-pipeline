#!/usr/bin/env python3
"""Independent scalar hardware oracle and adversarial native construction checks.
No producer/native renderer imports. Scalar reads raw OAM/VRAM/CGRAM per pixel.
"""
import copy,hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageChops
BASE=Path(__file__).resolve().parent
SIZE_PAIRS=[((8,8),(16,16)),((8,8),(32,32)),((8,8),(64,64)),((16,16),(32,32)),((16,16),(64,64)),((32,32),(64,64)),((16,32),(32,64)),((16,32),(32,32))]
def sha(b):return hashlib.sha256(b).hexdigest()
def scalar(raw):
 o=(raw/'oam.bin').read_bytes();v=(raw/'vram.bin').read_bytes();c=(raw/'cgram.bin').read_bytes();p=json.loads((raw/'ppu.json').read_text());rgba=bytearray(256*224*4)
 # Ascending OAM wins overlapping opaque samples. Work front-to-back, write only unclaimed.
 for i in range(128):
  x,y,t,a=o[i*4:i*4+4];h=(o[512+i//4]>>(2*(i%4)))&3;x+=256*(h&1);x=x-512 if x>=256 else x;w,ht=SIZE_PAIRS[p['size']][h>>1];t+=256*(a&1)
  for py in range(ht):
   sy=(y+py)&255
   if sy>=224:continue
   yy=ht-1-py if a&128 else py
   for px in range(w):
    sx=x+px
    if not 0<=sx<256:continue
    target=(sy*256+sx)*4
    if rgba[target+3]:continue
    xx=w-1-px if a&64 else px
    n=(t&256)|(((t&240)+(yy//8)*16)&240)|((t+xx//8)&15)
    addr=(p['base']+n*32+(p['select'] if n&256 else 0))&65535;idx=0;bit=7-(xx&7)
    for plane in range(4):idx|=((v[(addr+(yy&7)*2+(plane&1)+(plane//2)*16)&65535]>>bit)&1)<<plane
    if idx==0:continue
    off=(128+((a>>1)&7)*16+idx)*2;word=c[off]|c[off+1]<<8
    rgba[target:target+4]=bytes([(word&31)*255//31,((word>>5)&31)*255//31,((word>>10)&31)*255//31,255])
 return Image.frombytes('RGBA',(256,224),bytes(rgba))
def render(project,frame):
 out=Image.new('RGBA',(project['canvas']['width'],project['canvas']['height']))
 for layer in project['layers']:
  cid=frame['cels'].get(layer['id'])
  if cid is None:continue
  im=Image.new('RGBA',out.size);im.putdata([tuple(project['palette'][v])for v in project['cels'][cid]['pixels']]);out.alpha_composite(im)
 return out
def failures(project,bindings,pixel=True):
 issues=[];first=bindings['frames'][0];raw=BASE/'fixtures'/project['animations'][0]['id']/first['raw'];ram=(raw/'wram.bin').read_bytes();word=lambda off:int.from_bytes(ram[0xe000+off:0xe002+off],'little');anchor=[word(0x20),word(0x22)];center=[anchor[0],anchor[1]-(ram[0xe074]&127)-ram[0xe045]]
 if project['canvas']['ground_pivot']!=anchor or project['canvas']['render_pivot']!=center:issues.append('native pivot calibration changed')
 fids=[f['id']for f in project['frames']]
 if project['animations'][0]['frames']!=fids:issues.append('animation frame order differs from captured ticks')
 if project['animations'][0]['fps']!=60.098811862348406 or project['animations'][0]['loop']:issues.append('native observed clock/finite window changed')
 events=[]
 for i,b in enumerate(bindings['frames']):
  f=project['frames'][i]
  if f['id']!=b['frame_id'] or f['duration_ticks']!=1 or b['source_tick']!=first['source_tick']+i:issues.append(f'{i}: presentation clock mismatch')
  if i:
   a=bindings['frames'][i-1]['native'];n=b['native']
   if a['mode']!=n['mode']:events.append({'at_tick':i,'name':f'observed_action_mode_{a["mode"]:02x}_to_{n["mode"]:02x}'})
   if a['enemy_slot_0800_hp']!=n['enemy_slot_0800_hp']:events.append({'at_tick':i,'name':f'observed_enemy_slot_0800_HP_{a["enemy_slot_0800_hp"]}_to_{n["enemy_slot_0800_hp"]}'})
  if pixel:
   raw=BASE/'fixtures'/project['animations'][0]['id']/b['raw'];expected=scalar(raw);actual=render(project,f)
   if expected.tobytes()!=actual.tobytes():issues.append(f'{i}: raw native presented pixels differ')
 if project['animations'][0]['events']!=events:issues.append('observed event clock differs from raw mode/HP transitions')
 return issues

def audit(directory):
 p=json.loads((directory/'project.json').read_text());b=json.loads((directory/'bindings.json').read_text());checks=0;issues=[];frames=[]
 for entry in b['frames']:
  raw=directory/entry['raw']
  for n,h in entry['hashes'].items():
   checks+=1
   if sha((raw/n).read_bytes())!=h:issues.append(f'{entry["frame_id"]} changed raw {n}')
   source=Path(entry['source_capture'])/n
   if source.exists():
    checks+=1
    if source.read_bytes()!=(raw/n).read_bytes():issues.append(f'{entry["frame_id"]} original capture differs {n}')
  ram=(raw/'wram.bin').read_bytes();word=lambda off:int.from_bytes(ram[0xe000+off:0xe002+off],'little')
  native={'action_word':word(0x10),'script_start':word(0x18),'script_pointer':word(0x16),'generic_index':word(0x26)//2,'mode':ram[0xe01c],'mapping':word(0x2a),'body_table':word(0x72),'global_flip_byte':ram[0xe088],'native_timer':ram[0xe012],'charge_percent':ram[0xe01a],'frame_override_count':ram[0xe041],'single_slot_call_count':ram[0xe05d],'enemy_slot_0800_hp':int.from_bytes(ram[0xe982:0xe984],'little')}
  checks+=len(native)
  if entry['native']!=native:issues.append(f'{entry["frame_id"]} metadata differs independently read native WRAM')
  expected=scalar(raw);golden=Image.open(directory/'golden'/f'{entry["frame_id"]}.png').convert('RGBA');checks+=1
  if golden.tobytes()!=expected.tobytes():issues.append(f'{entry["frame_id"]} producer golden differs scalar')
  frames.append({'frame_id':entry['frame_id'],'source_tick':entry['source_tick'],'independent_rgba_sha256':sha(expected.tobytes())})
 issues+=failures(p,b);checks+=len(b['frames'])*4+4
 # Mutations use actual scene values, not mocked rejection flags.
 adversarial=[]
 def trial(name,mutant,pixel=True):
  result=failures(mutant,b,pixel);adversarial.append({'mutation':name,'rejected':bool(result),'observed_failures':result[:3]})
  if not result:issues.append('Adversarial mutation escaped: '+name)
 q=copy.deepcopy(p);q['frames'][0]['duration_ticks']=2;trial('one extra video hold tick',q,False)
 q=copy.deepcopy(p);q['canvas']['ground_pivot'][1]+=1;trial('ground pivot moved one pixel',q,False)
 q=copy.deepcopy(p);q['animations'][0]['fps']=60;trial('rounded clock 60 instead of SNES video rate',q,False)
 if p['animations'][0]['events']:
  q=copy.deepcopy(p);q['animations'][0]['events'][0]['at_tick']+=1;trial('observed event shifted one tick',q,False)
 # Select first real different-pose/color frame for off-by-one, not an identical hold.
 for i in range(1,len(p['frames'])):
  if render(p,p['frames'][i]).tobytes()!=render(p,p['frames'][i-1]).tobytes():
   q=copy.deepcopy(p);q['frames'][i]['cels']=q['frames'][i-1]['cels'];trial('previous displayed pose substituted at next tick',q);break
 f=p['frames'][0];cid=next(iter(f['cels'].values()));w=p['canvas']['width'];h=p['canvas']['height']
 q=copy.deepcopy(p);data=q['cels'][cid]['pixels'];q['cels'][cid]['pixels']=[v for row in range(h)for v in reversed(data[row*w:(row+1)*w])];trial('full-canvas cel horizontally flipped',q)
 q=copy.deepcopy(p);data=q['cels'][cid]['pixels'];q['cels'][cid]['pixels']=[v for row in range(h)for v in [0]+data[row*w:row*w+w-1]];trial('piece translated one pixel',q)
 # Find genuinely order-sensitive overlapping slots; mere reversal may be inert in a walk.
 baseline=[render(p,f).tobytes()for f in p['frames']];found=False
 for i in range(len(p['layers'])):
  for j in range(i+1,len(p['layers'])):
   q=copy.deepcopy(p);q['layers'][i],q['layers'][j]=q['layers'][j],q['layers'][i]
   if any(render(q,f).tobytes()!=ref for f,ref in zip(q['frames'],baseline)):
    trial('native overlapping OAM layer order swapped',q);found=True;break
  if found:break
 if not found:adversarial.append({'mutation':'native overlapping OAM layer order swapped','not_applicable':'No order-sensitive overlapping opaque pixels in this sample; no false claim of tested rejection.'})
 checks+=len(adversarial)
 return {'fixture':directory.name,'passed':not issues,'checks':checks,'issues':issues,'frames':frames,'adversarial':adversarial,'scope':'Independent pure presented OBJ pixels and capture clock; no background/scanline/color-math claim. Ground anchor is native WRAM origin, not guessed anatomical foot contact.'}
if __name__=='__main__':
 reports=[audit(d)for d in sorted((BASE/'fixtures').iterdir())if(d/'project.json').exists()];report={'schema':'native-construction-audit/v1','passed':all(r['passed']for r in reports),'checks':sum(r['checks']for r in reports),'fixtures':reports,'independent_reviewer':'som_animation_decoder scalar raw hardware oracle'};(BASE/'audit-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':report['checks'],'fixtures':[(r['fixture'],len(r['frames']),r['issues'])for r in reports]}));sys.exit(0 if report['passed']else 1)

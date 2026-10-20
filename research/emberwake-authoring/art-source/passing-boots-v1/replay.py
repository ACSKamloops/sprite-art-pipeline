"""Portable literal passing-boot repair. apply_variant(atlases, plan) returns
{character: {original_frame: new128pxImage}}, journal. Inputs remain immutable.
CLI writes a fresh output folder only, using adjacent frozen inputs by default.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import argparse,hashlib,json,struct,zlib
BASE=Path(__file__).resolve().parent

def sha(data):return hashlib.sha256(data).hexdigest()
def cel(a,f):return a.crop((f%8*128,f//8*128,f%8*128+128,f//8*128+128))
def apply_variant(atlases,plan):
 selected={};journal=[]
 for e in plan['entries']:
  char,frame,source=e['character'],e['target'],e['source']
  if frame not in [112,113,114,115] or source not in [121,123,125,127]:raise ValueError('Unauthorized frame')
  a=atlases[char].convert('RGBA');before=cel(a,frame);donor=cel(a,source)
  if sha(before.tobytes())!=e['target_rgba_sha256'] or sha(donor.tobytes())!=e['source_rgba_sha256']:raise ValueError(f'{char} f{frame} target/donor changed')
  after=before.copy();owners={};events=[]
  for op in e['operations']:
   for tx,ty,sx,sy in op['points_tx_ty_sx_sy']:
    if not all(0<=n<128 for n in [tx,ty,sx,sy]) or ty<96:raise ValueError('Outside boot region')
    rgba=donor.getpixel((sx,sy));after.putpixel((tx,ty),rgba)
    owners[(tx,ty)]={'source_frame':source,'source_xy':[sx,sy],'rgba':list(rgba),'owner':op['owner']}
    events.append([tx,ty,source,sx,sy,op['owner']])
  changed=[]
  for y in range(128):
   for x in range(128):
    old,new=before.getpixel((x,y)),after.getpixel((x,y))
    if old!=new:
     if (x,y) not in owners:raise AssertionError('Outside owner mask')
     changed.append({'xy':[x,y],'before':list(old),'after':list(new),**owners[x,y]})
  selected.setdefault(char,{})[frame]=after
  journal.append({'character':char,'frame':frame,'donor':source,'before_rgba_sha256':sha(before.tobytes()),'after_rgba_sha256':sha(after.tobytes()),'changed_pixels':len(changed),'changed_pixel_witnesses':changed,'literal_operation_events':events,'outside_masks_unchanged':True})
 return selected,{'schema':'emberwake-passing-boot-journal/v1','entries':journal,'quality_status':'Single source-pixel candidate; no score; independent visual review pending'}

def exact_apng(path,frames,numerator=9):
 frames[0].save(path,save_all=True,append_images=frames[1:],duration=56,loop=0,disposal=0,blend=0)
 raw=path.read_bytes();out=bytearray(raw[:8]);p=8
 while p<len(raw):
  size=struct.unpack('>I',raw[p:p+4])[0];kind=raw[p+4:p+8];data=raw[p+8:p+8+size]
  if kind==b'fcTL':data=data[:20]+struct.pack('>HH',numerator,160)+data[24:]
  out+=struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff);p+=size+12
 path.write_bytes(out)

def evidence(originals,selected,plan,out):
 bg=(24,42,47,255)
 for char in ['lyra','brann']:
  dest=out/char;dest.mkdir()
  atlas=originals[char];proof=Image.new('RGBA',(8*256,282),bg);draw=ImageDraw.Draw(proof)
  crop=Image.new('RGBA',(8*256,190),bg);cd=ImageDraw.Draw(crop)
  for i,frame in enumerate([112,113,114,115]):
   after=selected[char][frame];after.save(dest/f'passing-{frame}.png')
   before=cel(atlas,frame);entry=next(e for e in plan['entries'] if e['character']==char and e['target']==frame)
   mask=Image.new('L',(128,128))
   for op in entry['operations']:
    for tx,ty,sx,sy in op['points_tx_ty_sx_sy']:mask.putpixel((tx,ty),255)
   mask.save(dest/f'mask-{frame}.png')
   for j,(image,label) in enumerate([(before,'BEFORE'),(after,'AFTER')]):
    x=(i*2+j)*256;proof.alpha_composite(image.resize((256,256),Image.Resampling.NEAREST),(x,26));draw.text((x+4,5),f'{char} f{frame} {label}',fill='white')
    crop.alpha_composite(image.crop((43,88,85,115)).resize((252,162),Image.Resampling.NEAREST),(x+2,26));cd.text((x+4,5),f'f{frame} {label}',fill='white')
  proof.convert('RGB').save(dest/'all-four-passing-fullbody-before-after-2x.png');crop.convert('RGB').save(dest/'all-four-passing-boots-before-after-6x.png')
  bank=json.loads((BASE/'inputs'/char/'animations.json').read_text())
  for view in ['south','north']:
   clip=bank['animations'][view+'_walk'];frames=[]
   if any(abs(h-9/160)>1e-12 for h in clip['holds']):raise ValueError('Not frozen .45s walk')
   for f in clip['frames']:
    pair=Image.new('RGBA',(512,282),bg);d=ImageDraw.Draw(pair)
    for j,(image,label) in enumerate([(cel(atlas,f),'BEFORE'),(selected[char].get(f,cel(atlas,f)),'AFTER')]):
     pair.alpha_composite(image.resize((256,256),Image.Resampling.NEAREST),(j*256,26));d.text((j*256+4,5),f'{char} {view} f{f} {label}',fill='white')
    frames.append(pair)
   exact_apng(dest/(view+'-AB-450ms.apng'),frames);exact_apng(dest/(view+'-AB-slow3x.apng'),frames,27)
   # Unbroken pose strip proves predecessor/current joins and loop ordering.
   strip=Image.new('RGBA',(8*128,2*152),bg);d=ImageDraw.Draw(strip)
   for i,f in enumerate(clip['frames']):
    for j,image in enumerate([cel(atlas,f),selected[char].get(f,cel(atlas,f))]):
     strip.alpha_composite(image,(i*128,j*152+24));d.text((i*128+3,j*152+4),f'f{f} '+('BEFORE' if j==0 else 'AFTER'),fill='white')
   strip.convert('RGB').save(dest/(view+'-all-joins-native.png'))
   (dest/(view+'-clock.json')).write_text(json.dumps({'frames':clip['frames'],'delay_numerator':9,'delay_denominator':160,'cycle_numerator':9,'cycle_denominator':20,'clock_seconds':.45,'holds_unchanged':True},indent=2)+'\n')

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 if args.output.exists():raise ValueError('Fresh output folder required')
 originals={c:Image.open(BASE/'inputs'/c/'atlas.png').convert('RGBA') for c in ['lyra','brann']};plan=json.loads((BASE/'PLAN.json').read_text())
 selected,journal=apply_variant(originals,plan);args.output.mkdir(parents=True)
 evidence(originals,selected,plan,args.output)
 journal['plan_sha256']=sha((BASE/'PLAN.json').read_bytes());(args.output/'JOURNAL.json').write_text(json.dumps(journal,indent=2)+'\n')
 print('Wrote',sum(map(len,selected.values())),'revised cels; exact9/160s holds, .45s A/B loops')
if __name__=='__main__':main()

from pathlib import Path
from PIL import Image
import hashlib,json
P=Path(__file__).resolve().parents[1]
sizes=[((8,8),(16,16)),((8,8),(32,32)),((8,8),(64,64)),((16,16),(32,32)),((16,16),(64,64)),((32,32),(64,64)),((16,32),(32,64)),((16,32),(32,32))]
checks=0;errors=[];frames=0;objects=0;image_cache={};tile_cache={}
def check(value,message):
 global checks
 checks+=1
 if not value and len(errors)<50:errors.append(message)
def image_bytes(path):
 if path not in image_cache:image_cache[path]=Image.open(P/path).convert('RGBA').tobytes()
 return image_cache[path]
def opaque_tile(raw):
 if raw not in tile_cache:
  pixels=[]
  for y in range(8):
   for x in range(8):
    bit=128>>x;index=0
    for plane in range(4):
     if raw[y*2+(plane%2)+(16 if plane>=2 else 0)]&bit:index|=1<<plane
    if index:pixels.append((x,y,index))
  tile_cache[raw]=pixels
 return tile_cache[raw]
index=json.loads((P/'capture-index.json').read_text())
for entry in index['routes']:
 route=P/entry['path']
 data=json.loads(route.read_text());last=None;route_frames=0
 for frame_index in [0,len(data['frames'])//2,len(data['frames'])-1]:
  frame=data['frames'][frame_index]
  frames+=1;route_frames+=1;check(frame['duration_ticks']==1,'actual clock')
  snap=Path(frame['capture']);o=(snap/'oam.bin').read_bytes();v=(snap/'vram.bin').read_bytes();c=(snap/'cgram.bin').read_bytes();ppu=json.loads((snap/'ppu.json').read_text());layer=Image.new('RGBA',(256,224));pix=layer.load();expected_ids=[];rows={z['index']:z for z in frame['objects']}
  for i in range(128):
   x,y,t,attr=o[i*4:i*4+4];hi=(o[512+i//4]>>((i%4)*2))&3;x|=(hi&1)<<8
   if x>=256:x-=512
   w,h=sizes[ppu['size']][hi>>1];positions=[]
   if -w<x<256 and y<224:positions.append((x,y))
   if -w<x<256 and y+h>256:positions.append((x,y-256))
   if not positions:continue
   raw_indices=bytearray(w*h*4);opaque=[];tile=t|((attr&1)<<8)
   for ty in range(h//8):
    for tx in range(w//8):
     number=(((tile&240)+ty*16)&240)|(tile&256)|((tile+tx)&15);addr=(ppu['base']+number*32+(ppu['select']if number&256 else 0))&65535;raw=bytes(v[(addr+j)&65535]for j in range(32))
     for px,py,index in opaque_tile(raw):
      dx=tx*8+px;dy=ty*8+py
      if attr&64:dx=w-1-dx
      if attr&128:dy=h-1-dy
      off=(dy*w+dx)*4;raw_indices[off:off+4]=bytes([index,0,0,255]);opaque.append((dx,dy,index))
   if not opaque:continue
   expected_ids.append(i);objects+=1;record=rows.get(i);check(record is not None,'missing displayed OBJ')
   if record:
    check(bytes(raw_indices)==image_bytes(record['indexed_texture']),'native index-plane asset');check(record['positions']==[list(p)for p in positions],'OAM coordinates/wrap')
   bank=(attr>>1)&7
   for dx,dy,index in opaque:
    off=(128+bank*16+index)*2;word=c[off]|c[off+1]<<8;rgba=tuple(((word>>b)&31)*255//31 for b in (0,5,10))+(255,)
    for ox,oy in positions:
     px=ox+dx;py=oy+dy
     if 0<=px<256 and 0<=py<224 and not pix[px,py][3]:pix[px,py]=rgba
  check(set(expected_ids)==set(rows),'complete visible OBJ set');actual=image_bytes(frame['expected_texture']);check(layer.tobytes()==actual,'independent native presented RGBA');check(hashlib.sha256(actual).hexdigest()==frame['expected_pixel_sha256'],'expected pixel hash')
 print(json.dumps({'route':data['route_id'],'frames':route_frames,'total_frames':frames,'issues':len(errors)}),flush=True)
report={'passed':not errors,'checks':checks,'frames':frames,'objects':objects,'issues':errors,'unique_native_tiles':len(tile_cache),'scope':'255 first/middle/last presented samples independently rebuilt from raw OAM high-table size/x, byte-keyed independently scalar-decoded VRAM4planes and CGRAM, includingwrap andfirst-index opaquepriority. Tilecache requires exact32byte equality; noWRAM pose substitution. PureOBJ excludesBG/colormath/scanlinelimits.'}
(P/'evidence/raw-sample-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True);raise SystemExit(bool(errors))

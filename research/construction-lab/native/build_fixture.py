#!/usr/bin/env python3
"""Build layered indexed editing inputs from capture-bound native OBJ pieces.
Production decoder uses the previously audited native object renderer; audit.py
uses a separately written scalar decoder and does not trust those PNG hashes.
"""
import argparse, hashlib, importlib.util, json, sys, shutil
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parent
SOURCE=Path('/home/astra/artifacts/rea-som-animation-2026-10-07')
from source_renderer import object_records,object_image

def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,separators=(',',':'))+'\n')
def build(spec):
 out=BASE/'fixtures'/spec['id'];out.mkdir(parents=True,exist_ok=True)
 palette=[(0,0,0,0)];lookup={palette[0]:0};cels={};frames=[];bindings=[];used=set();seen={}
 for tick in range(spec['start_tick'],spec['end_tick']+1):
  candidates=[p for p in Path(spec['source']).glob(f'{tick:06d}_*') if(p/'oam.bin').exists()];assert len(candidates)==1,(tick,candidates)
  source=candidates[0];dest=out/'raw'/f'{tick:06d}';dest.mkdir(parents=True,exist_ok=True)
  for name in ['wram.bin','oam.bin','vram.bin','cgram.bin','ppu.json']:shutil.copyfile(source/name,dest/name)
  ram=(dest/'wram.bin').read_bytes();vram=(dest/'vram.bin').read_bytes();cgram=(dest/'cgram.bin').read_bytes();objects,ppu=object_records(dest)
  active={};proof=[];expected=Image.new('RGBA',(256,224))
  for obj in reversed(objects):
   tile,offsets=object_image(obj,vram,cgram,ppu);full=Image.new('RGBA',(256,224))
   x,y=obj['x'],obj['y']
   if -obj['width']<x<256 and y<224:full.alpha_composite(tile,(x,y))
   if -obj['width']<x<256 and y+obj['height']>256:full.alpha_composite(tile,(x,y-256))
   if full.getchannel('A').getbbox() is None:continue
   layer=f'oam-{obj["index"]:03d}';used.add(layer);expected.alpha_composite(full)
   raw=full.tobytes();identity=(layer,sha(raw));celid=seen.get(identity)
   if celid is None:
    celid=f'{layer}-cel-{len(seen):04d}';seen[identity]=celid;pixels=[]
    for rgba in full.getdata():
     if rgba[3]==0:rgba=(0,0,0,0)
     if rgba not in lookup:lookup[rgba]=len(palette);palette.append(rgba)
     pixels.append(lookup[rgba])
    cels[celid]={'layer_id':layer,'pixels':pixels}
   active[layer]=celid
   # Ownership is exact native WRAM-piece/OAM equality, never appearance.
   ownership=[];signed=lambda n:n-256 if n>127 else n
   for slot in [0,0x200,0x400,0x600,0x800,0xa00]:
    ab=0xe000+slot
    if not ram[ab]:continue
    word=lambda off:int.from_bytes(ram[ab+off:ab+off+2],'little')
    origin=(word(0x20),word(0x22)-(ram[ab+0x74]&127)-ram[ab+0x45])
    for kind,off,count in [('body',0x90,ram[ab+0x83]),('attached_weapon',0xd0,ram[ab+0x84])]:
     if count>16:continue
     for piece in range(count):
      px,py,t,a=ram[ab+off+piece*4:ab+off+piece*4+4];sx=(origin[0]+signed(px))&511;sx=sx-512 if sx>=256 else sx;sy=(origin[1]+signed(py))&255
      if (obj['x'],obj['y'],obj['tile'],obj['palette'],obj['flip_x'],obj['flip_y'],obj['width'],obj['height'])==(sx,sy,t|((a&1)<<8),(a>>1)&7,bool(a&64),bool(a&128),16,16):ownership.append({'actor_slot':slot,'kind':kind,'piece':piece,'ram_offset':ab+off+piece*4})
   proof.append({'layer_id':layer,'oam':obj,'vram_offsets':offsets,'ownership_matches':ownership,'semantic':ownership[0]['kind'] if len(ownership)==1 else 'unknown'})
  fid=f'tick-{tick:06d}';word=lambda off:int.from_bytes(ram[0xe000+off:0xe002+off],'little');x=word(0x20);y=word(0x22);height=ram[0xe074]&127;jump=ram[0xe045]
  frames.append({'id':fid,'duration_ticks':1,'cels':active,'landmarks':{'native_actor_world_anchor':[x,y],'native_actor_render_center':[x,y-height-jump]}})
  bindings.append({'frame_id':fid,'source_tick':tick,'raw':f'raw/{tick:06d}','source_capture':str(source),'hashes':{n:sha((dest/n).read_bytes())for n in ['wram.bin','oam.bin','vram.bin','cgram.bin','ppu.json']},'pieces':proof,'native':{'action_word':word(0x10),'script_start':word(0x18),'script_pointer':word(0x16),'generic_index':word(0x26)//2,'mode':ram[0xe01c],'mapping':word(0x2a),'body_table':word(0x72),'global_flip_byte':ram[0xe088],'native_timer':ram[0xe012],'charge_percent':ram[0xe01a],'frame_override_count':ram[0xe041],'single_slot_call_count':ram[0xe05d],'enemy_slot_0800_hp':int.from_bytes(ram[0xe982:0xe984],'little')}})
  expected.save(out/'golden'/f'{fid}.png') if (out/'golden').exists() else ((out/'golden').mkdir(),expected.save(out/'golden'/f'{fid}.png'))
 events=[]
 for i in range(1,len(bindings)):
  a,b=bindings[i-1]['native'],bindings[i]['native']
  if a['mode']!=b['mode']:events.append({'at_tick':i,'name':f'observed_action_mode_{a["mode"]:02x}_to_{b["mode"]:02x}'})
  if a['enemy_slot_0800_hp']!=b['enemy_slot_0800_hp']:events.append({'at_tick':i,'name':f'observed_enemy_slot_0800_HP_{a["enemy_slot_0800_hp"]}_to_{b["enemy_slot_0800_hp"]}'})
 first=frames[0]['landmarks'];project={'schema':'sprite-edit-project/v1','canvas':{'width':256,'height':224,'render_pivot':first['native_actor_render_center'],'ground_pivot':first['native_actor_world_anchor']},'palette':[list(p)for p in palette],'layers':[{'id':v,'name':f'Native {v}; ownership per-frame binding','locked':False}for v in sorted(used,reverse=True)],'cels':cels,'frames':frames,'animations':[{'id':spec['id'],'frames':[f['id']for f in frames],'fps':60.098811862348406,'loop':False,'events':events}],'provenance':{'source':'Native hardware presented OBJ control, not authored new art','rom_sha256':'4c15013131351e694e05f22e38bb1b3e4031dedac77ec75abecebe8520d82d5f','source_spec':spec,'coordinate_contract':'Unrecentered native 256x224 screen; dense full-canvas OAM cels, ascending index wins overlap. Stable layer IDs denote hardware OAM slots, not stable anatomical identities. Render and world/ground references captured from actor WRAM; feet contacts and limb alternation are NOT inferred from alpha bounds.','clock':'One captured video tick per frame; exact displayed palette may change within same body pose. Event names describe observed RAM transitions, not inferred attack hit windows.','limits':['Pure OBJ: excludes backgrounds, color math, scanline overflow and OAM rotation.','The final sample is a one-tick export convention. Native action completion requires captured mode/script transition.','Whole-scene objects retained; unknown ownership stays unknown.','Layered original game control fixture is copyrighted derived game art; not new authored art.']}}
 dump(out/'project.json',project);dump(out/'bindings.json',{'schema':'native-construction-bindings/v1','frames':bindings});return {'id':spec['id'],'frames':len(frames),'cels':len(cels),'layers':len(used),'palette_colors':len(palette),'project_sha256':sha((out/'project.json').read_bytes())}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('spec',type=Path);a=p.parse_args();print(json.dumps([build(x)for x in json.loads(a.spec.read_text())],indent=2))

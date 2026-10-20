"""Read-only source timing and measured geometry; never exports original art."""
import sys,json,hashlib,sqlite3
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'native'))
from source_renderer import object_records,object_image
DB=ROOT/'qc/engine/motion-index/catalog-v1/motions.sqlite';SITE=Path('/home/astra/projects/som-sprite-lab-site/native-godot');OBJ=Path('/home/astra/projects/som-native-effect-renderer')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
c=sqlite3.connect('file:'+str(DB)+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
ledger={'sqlite':{'path':str(DB),'sha256':sha(DB)},'independent_scalar_renderer':{'path':str(ROOT/'native/source_renderer.py'),'sha256':sha(ROOT/'native/source_renderer.py')}};checks=[];routes=[]
def check(ok,label):checks.append({'passed':bool(ok),'check':label})
def runs(rows):
 out=[]
 for x in rows:
  key=(x['generic'],x['script_start'])
  if out and tuple(out[-1]['key'])==key and out[-1]['last_tick']+1==x['relative_tick']:out[-1]['last_tick']=x['relative_tick'];out[-1]['duration_ticks']+=1
  else:out.append({'key':list(key),'generic':key[0],'script_start':hex(key[1]),'first_tick':x['relative_tick'],'last_tick':x['relative_tick'],'duration_ticks':1})
 return out
for name in ['sword-charge-1','sword-charge-2','randi-native-damage-recovery','randi-native-lethal-reaction']:
 r=dict(c.execute('select * from routes where name=?',(name,)).fetchone());p=SITE/r['route_path'];d=read(p);check(sha(p)==bytes(r['route_sha']).hex(),name+' actual route hash matches DB');ledger[name]={'path':str(p),'sha256':sha(p)}
 rows=[dict(x)for x in c.execute('select f.relative_tick,a.* from frames f join actor_frames a on a.frame_id=f.id where f.route_id=? and a.slot=0 order by f.relative_tick',(r['id'],))];geometry=[]
 for run in runs(rows):
  i=(run['first_tick']+run['last_tick'])//2;f=d['frames'][i];snap=Path(f['capture']);ram=(snap/'wram.bin').read_bytes();v=(snap/'vram.bin').read_bytes();cg=(snap/'cgram.bin').read_bytes();records,ppu=object_records(snap); masks={k:Image.new('RGBA',(256,224))for k in ['actor_body','actor_attached_weapon']};counts={k:0 for k in masks}
  for obj in f['objects']:
   if obj.get('owner_actor_slot')!=0 or obj['semantic_layer'] not in masks:continue
   native=records[obj['index']];check(all(native[k]==obj[k]for k in ['x','y','tile','width','height','palette','flip_x','flip_y']),name+f' sample{i} OBJ{obj["index"]} native fields')
   image,_=object_image(native,v,cg,ppu);idx=Image.open(SITE/obj['indexed_texture']).convert('RGBA');check(image.getchannel('A').tobytes()==idx.getchannel('A').tobytes(),name+f' sample{i} OBJ{obj["index"]} independently decoded alpha')
   for x,y in obj['positions']:masks[obj['semantic_layer']].alpha_composite(image,(x,y))
   counts[obj['semantic_layer']]+=1
  base=0xe000;world=[int.from_bytes(ram[base+o:base+o+2],'little')for o in [0x20,0x22]];render=[world[0],world[1]-ram[base+0x24]-ram[base+0x45]]
  geometry.append({'relative_tick':i,'source_tick':f['source_tick'],'selected_generic':rows[i]['generic'],'world_anchor':world,'render_center':render,'body_alpha_bbox':masks['actor_body'].getbbox(),'weapon_alpha_bbox':masks['actor_attached_weapon'].getbbox(),'matched_piece_counts':counts,'ownership':'Only native-field matched slot0 body/attachedweapon; unmatched pieces not guessed.','capture':str(snap),'raw_sha256':{n:sha(snap/n)for n in ['wram.bin','oam.bin','vram.bin','cgram.bin','ppu.json']}})
 routes.append({'id':name,'fps':r['fps'],'frame_count':r['frame_count'],'selected_pose_runs':runs(rows),'world_x_range':[min(x['world_x']for x in rows),max(x['world_x']for x in rows)],'world_y_range':[min(x['world_y']for x in rows),max(x['world_y']for x in rows)],'sampled_presented_geometry':geometry,'collision_active_windows':None,'limits':'Selected WRAM clock and presented hardware geometry are separate; known one-video-tick body assembly/DMA lag. Runs may be truncated by capture boundaries. HP/status transitions do not establish attack collision intervals.'})
controls=[]
for name in ['randi-right-walk-native','randi-right-sword-native']:
 p=ROOT/'native/fixtures'/name/'bindings.json';d=read(p);ledger[name]={'path':str(p),'sha256':sha(p)};print(name,type(d).__name__)
 control_rows=[]
 for f in d['frames']:
  snap=Path(f['source_capture']);ram=(snap/'wram.bin').read_bytes()
  for n,h in f['hashes'].items():check(sha(snap/n)==h,name+f' {f["source_tick"]} raw {n} binding')
  generic=int.from_bytes(ram[0xe026:0xe028],'little')//2;check(generic==f['native']['generic_index'],name+f' {f["source_tick"]} fresh selected generic')
  records,ppu=object_records(snap);v=(snap/'vram.bin').read_bytes();cg=(snap/'cgram.bin').read_bytes();layer=Image.new('RGBA',(256,224))
  for obj in reversed(records):
   image,_=object_image(obj,v,cg,ppu)
   if -obj['width']<obj['x']<256 and obj['y']<224:layer.alpha_composite(image,(obj['x'],obj['y']))
   if obj['y']+obj['height']>256:layer.alpha_composite(image,(obj['x'],obj['y']-256))
  golden=ROOT/'native/fixtures'/name/'golden'/(f['frame_id']+'.png');check(layer.tobytes()==Image.open(golden).convert('RGBA').tobytes(),name+f' {f["source_tick"]} independent presented golden')
  control_rows.append({'relative_tick':len(control_rows),'generic':generic,'script_start':f['native']['script_start'],'source_tick':f['source_tick'],'presented_pixel_sha256':hashlib.sha256(layer.tobytes()).hexdigest()})
 presented=[]
 for row in control_rows:
  if presented and presented[-1]['pixel_sha256']==row['presented_pixel_sha256']:presented[-1]['duration_ticks']+=1
  else:presented.append({'first_source_tick':row['source_tick'],'duration_ticks':1,'pixel_sha256':row['presented_pixel_sha256']})
 controls.append({'id':name,'selected_pose_runs':runs(control_rows),'actual_presented_pixel_runs':presented,'scope':'Original actual control fixture, not Copper Scout art. Complete30tick walk cycle;19tick attack window contains completion. Selected and displayed holds remain distinct.'})
 rules=read(ROOT/'native/native-rules-report.json');ledger['native_rules']={'path':str(ROOT/'native/native-rules-report.json'),'sha256':sha(ROOT/'native/native-rules-report.json')}
result={'schema':'copper-scout.native-motion-reference.v1','asset_role':'reference_measurements_not_authored_art','source_ledger':ledger,'catalog_routes':routes,'native_control_fixtures':controls,'native_golden_rules':rules,'checks':checks,'passed':all(x['passed']for x in checks),'adaptation_recommendations':['Walk: preserve stance/pass/contact alternation and shared ground reference; author actual Copper Scout hip/knee keys, never infer contact from alpha bounds alone.','Sword: use unequal preparatory/extension/recovery holds; native three5tick poses illustrate economical timing, not a collision spec.','Charge: prolong a readable compressed/ready silhouette before acceleration; higher-level state and independent effects need their own parameters.','Damage: distinguish recoil, prone hold and recovery; source script5E56 demonstrates long recovery dwell, not a required50tick Copper Scout pose.','Use normalized authored joint coordinates, not copied native OAM locations or pixels. Equipment must follow grip anchors and explicit overlap keys.'],'unproven':['Native hit/collision intervals','Anatomical joints or foot contact phase from unlabeled body alpha','All native directions or actors','New character quality or causal improvement from native timing'],'limits':'No ROM art exported or reused; native source fixtures/captures read-only. Bounded DB routes and representative geometry only.'}
(OUT/'reference.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'checks':len(checks),'routes':len(routes)}));raise SystemExit(not result['passed'])

#!/usr/bin/env python3
"""Index immutable native capture exports; raw state and displayed OBJ evidence stay separate."""
import argparse,collections,concurrent.futures,csv,functools,hashlib,json,sqlite3,time
from pathlib import Path
from PIL import Image
RAW_NAMES=('wram.bin','vram.bin','cgram.bin','oam.bin','ppu.json')
ACTOR_COLUMNS=('generic','frame_raw','script_start','script_pointer','countdown','action_word','action_row','direction_raw','action_mode','identity','hp','status','effect_mode','world_x','world_y','charge_level','condition41','condition5d')
# Entry contracts only. Internal helper PCs deliberately remain unknown-owner.
CONTRACTS={0xc0f582:('actor-slot-X','animation/animation-parser-disassembly.json'),0xc0f4cb:('actor-slot-X','animation/full-transformed-native-disassembly-v3.json'),0xc2bf1d:('actor-slot-X','effects/effect-lifecycle-projectile-disassembly.json'),0xc2c221:('actor-slot-X','effects/effect-projectile-terminal-disassembly.json')}
def digest(blob):return hashlib.sha256(blob).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def signature(value):return bytes.fromhex(digest(canonical(value)))
def file_sha(path):return digest(Path(path).read_bytes())
def continuity(frames):
 if not frames:raise ValueError('Empty route')
 for i,f in enumerate(frames):
  if f['duration_ticks']!=1:raise ValueError('Only source-video-tick rows accepted; no flattening or invented holds')
  if i and f['source_tick']!=frames[i-1]['source_tick']+1:raise ValueError('Missing/duplicate/nonconsecutive source tick')
def actor_state(ram,slot):
 if not isinstance(slot,int)or slot<0 or slot>0x1e00 or slot%0x200:raise ValueError('Invalid actor slot')
 b=ram[0xe000+slot:0xe200+slot];u=lambda n:int.from_bytes(b[n:n+2],'little')
 return (u(0x26)//2,u(0x26),u(0x18),u(0x16),b[0x12],u(0x10),b[0x11],b[0x10],b[0x1c],b[0x180],u(0x182),u(0x190),b[0x60],u(0x20),u(0x22),b[0x19b],b[0x41],b[0x5d])
class Verifier:
 def __init__(self,corpus,evidence):self.corpus=Path(corpus);self.evidence=Path(evidence)
 @functools.lru_cache(maxsize=None)
 def asset(self,relative):
  path=self.corpus/relative
  if not path.exists():path=self.evidence/relative
  blob=path.read_bytes()
  with Image.open(path)as im:rgba=im.convert('RGBA');pixels=rgba.tobytes();size=rgba.size
  return file_sha(path),digest(pixels),size,str(path)
 def frame(self,f):
  hashes=[];ram=None;capture=Path(f['capture'])
  for name in RAW_NAMES:
   blob=(capture/name).read_bytes();actual=digest(blob)
   if actual!=f['source_hashes'][name]:raise ValueError(f'Wrong raw source SHA {capture}/{name}')
   hashes.append(bytes.fromhex(actual))
   if name=='wram.bin':ram=blob
  if len(ram)!=131072:raise ValueError('WRAM size is not128KiB')
  slots=set(x['slot']for x in f.get('actor_states',[]));slots.add(f['actor_slot']);states={s:actor_state(ram,s)for s in sorted(slots)}
  main=states[f['actor_slot']]
  if main[0]!=f['actor']['generic_index']:raise ValueError('Raw-selected generic differs from route actor state')
  expected=self.asset(f['expected_texture'])
  if expected[1]!=f['expected_pixel_sha256']:raise ValueError('Expected display RGBA hash mismatch')
  palette=self.asset(f['palette_texture'])
  if palette[1]!=Path(f['palette_texture']).stem.removeprefix('palette-'):raise ValueError('Palette pixel signature mismatch')
  aset=[];ownership=[];owners=collections.Counter()
  for obj in f['objects']:
   actual=self.asset(obj['indexed_texture'])
   if actual[1]!=obj['indexed_pixel_sha256']:raise ValueError('Indexed OBJ pixel signature mismatch')
   aset.append((obj['indexed_texture'],actual[0],actual[1]))
   ownership.append({k:obj[k]for k in ('index','semantic_layer','owner_actor_slot','ownership_matches')if k in obj});owners[str(obj.get('owner_actor_slot','unknown'))]+=1
  return hashes,states,bytes.fromhex(expected[1]),bytes.fromhex(palette[1]),signature(f['objects']),signature(aset),signature(ownership),len(f['objects']),json.dumps(dict(owners),sort_keys=True,separators=(',',':'))
def schema(db):
 db.executescript('''PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;
 CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);
 CREATE TABLE routes(id INTEGER PRIMARY KEY,name TEXT UNIQUE,route_path TEXT,route_sha BLOB,first_tick INTEGER,last_tick INTEGER,frame_count INTEGER,fps REAL,trace_path TEXT,trace_present INTEGER,trace_missed_ticks INTEGER,scope TEXT);
 CREATE TABLE frames(id INTEGER PRIMARY KEY,route_id INTEGER,relative_tick INTEGER,source_tick INTEGER,actor_slot INTEGER,wram_sha BLOB,vram_sha BLOB,cgram_sha BLOB,oam_sha BLOB,ppu_sha BLOB,display_rgba_sha BLOB,palette_rgba_sha BLOB,objects_sha BLOB,assets_sha BLOB,ownership_sha BLOB,object_count INTEGER,ownership_counts TEXT,trace_event_count INTEGER DEFAULT 0,UNIQUE(route_id,relative_tick));
 CREATE TABLE actor_frames(frame_id INTEGER,slot INTEGER,generic INTEGER,frame_raw INTEGER,script_start INTEGER,script_pointer INTEGER,countdown INTEGER,action_word INTEGER,action_row INTEGER,direction_raw INTEGER,action_mode INTEGER,identity INTEGER,hp INTEGER,status INTEGER,effect_mode INTEGER,world_x INTEGER,world_y INTEGER,charge_level INTEGER,condition41 INTEGER,condition5d INTEGER,PRIMARY KEY(frame_id,slot)) WITHOUT ROWID;
 CREATE TABLE selection_runs(route_id INTEGER,actor_slot INTEGER,first_relative_tick INTEGER,last_relative_tick INTEGER,generic INTEGER,script_start INTEGER,action_word INTEGER,action_mode INTEGER,status INTEGER);
 CREATE TABLE method_hits(route_id INTEGER,relative_tick INTEGER,pc INTEGER,x INTEGER,p INTEGER,event_count INTEGER,owner_slot INTEGER,contract_id INTEGER,PRIMARY KEY(route_id,relative_tick,pc,x,p)) WITHOUT ROWID;
 CREATE TABLE trace_sources(path TEXT PRIMARY KEY,sha BLOB,event_count INTEGER,dropped_report TEXT);
 CREATE TABLE assets(relative_path TEXT PRIMARY KEY,resolved_path TEXT,file_sha BLOB,rgba_sha BLOB,width INTEGER,height INTEGER) WITHOUT ROWID;
 CREATE INDEX actor_selection ON actor_frames(generic,script_start,status);
 CREATE INDEX source_ticks ON frames(route_id,source_tick);
 CREATE VIEW motions AS SELECT r.name AS route,f.relative_tick,f.source_tick,f.actor_slot,a.*,hex(f.display_rgba_sha) AS display_pixel_sha256,hex(f.palette_rgba_sha) AS palette_pixel_sha256,f.trace_event_count FROM frames f JOIN routes r ON r.id=f.route_id JOIN actor_frames a ON a.frame_id=f.id;
 ''')
def trace_report(parent):
 # Absence of a drops counter is not zero drops.
 for name in ['scenario.json','experiment.json','metadata.json']:
  path=parent/name
  if path.exists():
   obj=json.loads(path.read_text())
   if 'trace_dropped'in obj:return json.dumps({'source':str(path),'value':obj['trace_dropped']})
 return 'not-recorded; original harness may assert but corpus receipt does not expose count'
def build(args):
 output=Path(args.output);output.mkdir(parents=True,exist_ok=False);dbpath=output/'motions.sqlite';db=sqlite3.connect(dbpath);schema(db)
 corpus=Path(args.corpus);idxpath=corpus/'capture-index.json';index=json.loads(idxpath.read_text());verify=Verifier(corpus,args.evidence_root);artifact=Path(args.artifact_root)
 contracts={pc:desc for pc,desc in CONTRACTS.items()if(artifact/desc[1]).exists()};bindings={hex(pc):{'contract':desc[0],'evidence_path':str(artifact/desc[1]),'evidence_sha256':file_sha(artifact/desc[1])}for pc,desc in contracts.items()}
 route_info=[];frame_ids={};frame_id=0;parents=collections.defaultdict(list);asset_paths=set();started=time.monotonic()
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers)as pool:
  for rid,entry in enumerate(index['routes'],1):
   path=corpus/entry['path'];blob=path.read_bytes();route=json.loads(blob);sha=digest(blob)
   if sha!=entry['route_sha256']:raise ValueError('Route SHA mismatch '+entry['id'])
   continuity(route['frames'])
   if len(route['frames'])!=route['frame_count'] or len(route['frames'])!=route['duration_ticks'] or len(route['frames'])!=entry['frame_count']:raise ValueError('Declared frame count/duration mismatch')
   if len({f['actor_slot']for f in route['frames']})!=1:raise ValueError('Selected actor slot changes within route; run grouping requires explicit split')
   parents_set={str(Path(f['capture']).parent)for f in route['frames']}
   if len(parents_set)!=1:raise ValueError('Route crosses trace provenance parents')
   parent=Path(next(iter(parents_set)));trace=parent/'cpu_trace.jsonl';present=trace.exists();fps=route['video_fps'];previous=None;changes=collections.Counter();run=None;runs=[]
   db.execute('INSERT INTO routes VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(rid,entry['id'],entry['path'],bytes.fromhex(sha),route['frames'][0]['source_tick'],route['frames'][-1]['source_tick'],len(route['frames']),fps,str(trace),int(present),0 if present else None,entry.get('scope',route.get('provenance',''))))
   for rel,(f,result)in enumerate(zip(route['frames'],pool.map(verify.frame,route['frames']))):
    frame_id+=1;hashes,states,display,palette,objects,aset,ownership,objcount,owncounts=result
    db.execute('INSERT INTO frames VALUES('+','.join('?'*18)+')',(frame_id,rid,rel,f['source_tick'],f['actor_slot'],*hashes,display,palette,objects,aset,ownership,objcount,owncounts,0))
    for slot,state in states.items():db.execute('INSERT INTO actor_frames VALUES('+','.join('?'*20)+')',(frame_id,slot,*state))
    state=states[f['actor_slot']];selection=(state[0],state[2],state[5],state[8],state[11])
    if run is None or run['selection']!=selection:
     if run:runs.append(run)
     run={'first':rel,'last':rel,'selection':selection}
    else:run['last']=rel
    cur=(display,palette,objects,aset,ownership)
    if previous:
     for i,key in enumerate(['display','palette','objects','assets','ownership']):changes[key]+=cur[i]!=previous[i]
    previous=cur;frame_ids[(rid,f['source_tick'])]=(frame_id,rel)
    asset_paths.add(f['palette_texture']);asset_paths.update(o['indexed_texture']for o in f['objects'])
   if run:runs.append(run)
   for run in runs:db.execute('INSERT INTO selection_runs VALUES(?,?,?,?,?,?,?,?,?)',(rid,f['actor_slot'],run['first'],run['last'],*run['selection']))
   parents[str(parent)].append((rid,route['frames'][0]['source_tick'],route['frames'][-1]['source_tick']))
   route_info.append({'route':entry['id'],'id':rid,'frames':len(route['frames']),'actor_slot':f['actor_slot'],'selection_runs':len(runs),'changes':dict(changes),'trace_present':present,'trace_missed_ticks':None if not present else 0,'route_sha256':sha})
   print(json.dumps({'indexed_route':entry['id'],'frames':len(route['frames']),'elapsed_seconds':round(time.monotonic()-started,1)}),flush=True)
 for parent,ranges in parents.items():
  path=Path(parent)/'cpu_trace.jsonl'
  if not path.exists():continue
  rawhash=hashlib.sha256();event_count=0;hits=collections.Counter();seen=collections.defaultdict(set)
  with path.open('rb')as stream:
   for line in stream:
    rawhash.update(line);event_count+=1;r=json.loads(line);tick=r['frame']
    for rid,first,last in ranges:
     if first<=tick<=last:
      _,rel=frame_ids[rid,tick];hits[(rid,rel,r['pc'],r['x'],r['p'])]+=1;seen[rid].add(tick)
  db.execute('INSERT INTO trace_sources VALUES(?,?,?,?)',(str(path),rawhash.digest(),event_count,trace_report(Path(parent))))
  totals=collections.Counter()
  for (rid,rel,pc,x,p),count in hits.items():
   contract=contracts.get(pc);slot=x if contract and 0<=x<=0x1e00 and x%0x200==0 else None
   db.execute('INSERT INTO method_hits VALUES(?,?,?,?,?,?,?,?)',(rid,rel,pc,x,p,count,slot,1 if slot is not None else 0));totals[rid,rel]+=count
  for (rid,rel),count in totals.items():db.execute('UPDATE frames SET trace_event_count=? WHERE route_id=? AND relative_tick=?',(count,rid,rel))
  for rid,first,last in ranges:
   missed=last-first+1-len(seen[rid]);db.execute('UPDATE routes SET trace_missed_ticks=? WHERE id=?',(missed,rid));route_info[rid-1]['trace_missed_ticks']=missed
 for path in sorted(asset_paths):
  filehash,pixelhash,(w,h),resolved=verify.asset(path);db.execute('INSERT INTO assets VALUES(?,?,?,?,?,?)',(path,resolved,bytes.fromhex(filehash),bytes.fromhex(pixelhash),w,h))
 for key,value in {'schema':'native-motion-index/v1','capture_index_path':str(idxpath),'capture_index_sha256':file_sha(idxpath),'contracts':json.dumps(bindings,sort_keys=True),'contract_ids':'0=unknown-owner;1=actor-slot-X proven entry only','notes':'Trace join is same capture parent plus source tick; method hits are co-occurrence, never causal. Missing method hit on tick is not evidence of dropped trace. Unknown rows retain numeric IDs.'}.items():db.execute('INSERT INTO metadata VALUES(?,?)',(key,value))
 db.commit()
 with(output/'method-route-heatmap.csv').open('w',newline='')as f:
  writer=csv.writer(f);writer.writerow(['pc','route','events','ticks_with_hits','known_owner_events','unknown_owner_events'])
  for row in db.execute('SELECT printf("%06X",m.pc),r.name,sum(m.event_count),count(DISTINCT m.relative_tick),sum(CASE WHEN owner_slot IS NOT NULL THEN event_count ELSE 0 END),sum(CASE WHEN owner_slot IS NULL THEN event_count ELSE 0 END) FROM method_hits m JOIN routes r ON r.id=m.route_id GROUP BY m.pc,m.route_id ORDER BY m.pc,r.name'):writer.writerow(row)
 with(output/'method-route-heatmap-matrix.csv').open('w',newline='')as f:
  writer=csv.writer(f);writer.writerow(['pc',*[r['route']for r in route_info]])
  matrix=collections.defaultdict(dict)
  for pc,rid,count in db.execute('SELECT pc,route_id,sum(event_count) FROM method_hits GROUP BY pc,route_id'):matrix[pc][rid]=count
  for pc,routes in sorted(matrix.items()):writer.writerow(['%06X'%pc,*[routes.get(r['id'],0)for r in route_info]])
 with(output/'route-coverage.csv').open('w',newline='')as f:
  writer=csv.writer(f);writer.writerow(['route','frames','actor_slot','selection_runs','trace_present','ticks_without_selected_trace_events','display_changes','palette_changes','object_changes','asset_changes','ownership_changes'])
  for r in route_info:writer.writerow([r['route'],r['frames'],r['actor_slot'],r['selection_runs'],r['trace_present'],r['trace_missed_ticks'],*[r['changes'].get(k,0)for k in ['display','palette','objects','assets','ownership']]])
 db.execute('VACUUM');counts={table:db.execute('SELECT count(*) FROM '+table).fetchone()[0]for table in ['routes','frames','actor_frames','selection_runs','method_hits','trace_sources','assets']};db.close()
 summary={'schema':'native-motion-index-summary/v1','counts':counts,'verified_raw_source_files':counts['frames']*5,'source_index_sha256':file_sha(idxpath),'database_sha256':file_sha(dbpath),'database_bytes':dbpath.stat().st_size,'method_heatmap_sha256':file_sha(output/'method-route-heatmap.csv'),'matrix_sha256':file_sha(output/'method-route-heatmap-matrix.csv'),'route_coverage_sha256':file_sha(output/'route-coverage.csv'),'builder_sha256':file_sha(__file__),'routes':route_info,'elapsed_seconds':round(time.monotonic()-started,2),'limits':['All available85capture routes, not full-game coverage.','Raw actor script and selection fields are distinct from presented OBJ/palette hashes; native DMA presentation lag is preserved.','All method hits are source-tick co-occurrence, never causal relationships.','Sparse trace absence/missed ticks are distinguished from dropped events; unavailable drop counters remain unknown.','Expecteddisplay is captured pure OBJ renderer RGBA, not original full gameplay screen.','One video-tick rows only; missing ticks fail rather than resample/recenter/flatten.','Unknown script/action/generic IDs are preserved numeric and remain unlabelled.']}
 (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items()if k!='routes'},indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--corpus',default='/home/astra/projects/som-sprite-lab-site/native-godot');p.add_argument('--evidence-root',default='/home/astra/projects/som-native-effect-renderer');p.add_argument('--artifact-root',default='/home/astra/artifacts/rea-som-animation-2026-10-07');p.add_argument('--workers',type=int,default=6);p.add_argument('--output',required=True);args=p.parse_args()
 if not 1<=args.workers<=8:p.error('workers must be1..8')
 build(args)
if __name__=='__main__':main()

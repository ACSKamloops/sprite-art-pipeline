import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
SITE=Path('/home/astra/projects/som-sprite-lab-site/native-godot')
OBJ=Path('/home/astra/projects/som-native-effect-renderer')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
gpu=read(B/'evidence/rendered-route-validation.json');scalar=read(B/'evidence/raw-sample-validation.json');index=read(SITE/'capture-index.json');old=read(OBJ/'evidence/rendered-route-validation-final85-consolidated.json')
assert gpu['passed'] and gpu['rendered_frames']==255 and scalar['passed'] and scalar['frames']==255
assert sha(B/'capture-index.json')==sha(SITE/'capture-index.json')==old['capture_index_sha256']
assert sha(B/'scripts/native_obj_player.gd')==sha(SITE/'scripts/native_obj_player.gd')
assert sha(B/'scripts/indexed_object.gdshader')==sha(SITE/'scripts/indexed_object.gdshader')==old['shader_sha256']
previous={r['id']:r for r in old['routes']}; rendered={r['id']:r for r in gpu['routes']};rows=[]
for e in index['routes']:
 p=SITE/e['path'];d=read(p);assert sha(p)==e['route_sha256']==previous[e['id']]['route_sha256']
 inds=[0,len(d['frames'])//2,len(d['frames'])-1];assert rendered[e['id']]['sample_indices']==inds and rendered[e['id']]['pixel_differences']==0
 samples=[]
 for i in inds:
  f=d['frames'][i];snap=Path(f['capture']);sources={n:sha(snap/n) for n in ['oam.bin','vram.bin','cgram.bin','ppu.json']}
  actual=B/'evidence/rendered'/f"{e['id']}-{i:04d}.png"
  samples.append({'frame_index':i,'source_tick':f['source_tick'],'capture':str(snap),'raw_sha256':sources,'golden_png_sha256':sha(OBJ/f['expected_texture']),'gpu_png_sha256':sha(actual),'golden_pixel_sha256':f['expected_pixel_sha256']})
 rows.append({'id':e['id'],'route_sha256':sha(p),'frame_count':len(d['frames']),'samples':samples})
r={'schema':'som.current-player-gpu-bridge.v1','passed':True,'sampled_frames':255,'route_count':85,'routes':rows,'capture_index_sha256':sha(SITE/'capture-index.json'),'player_sha256':sha(SITE/'scripts/native_obj_player.gd'),'shader_sha256':sha(SITE/'scripts/indexed_object.gdshader'),'historical_full_gpu_proof':{'path':str(OBJ/'evidence/rendered-route-validation-final85-consolidated.json'),'sha256':sha(OBJ/'evidence/rendered-route-validation-final85-consolidated.json'),'player_sha256':old['player_sha256'],'rendered_indexed_frames':old['rendered_indexed_frames']},'new_gpu_evidence_sha256':sha(B/'evidence/rendered-route-validation.json'),'independent_scalar_evidence_sha256':sha(B/'evidence/raw-sample-validation.json'),'scope':'255 actual OpenGL first/middle/last frames across85unchangedroutes with corrected player. Historical28123frameGPUproof preserved with oldplayerhash. Independent raw OAM/VRAM/CGRAM scalar reconstruction checks sampled goldens. Clock proof is separate. No full corrected-player pixel rerender, BG/color-math/scanline limits or new-art approval.'}
(B/'bridge.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k]for k in ['passed','sampled_frames','route_count','player_sha256']}))

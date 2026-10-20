"""Accept a bounded bridge only with its complete current file/hash chain."""
import hashlib,json
from pathlib import Path
def verify_bridge(path, site, historical):
 def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
 def read(p):return json.loads(Path(p).read_text())
 try:
  path=Path(path);b=read(path);root=path.parent;index=read(site/'capture-index.json');old=read(historical)
  assert b['schema']=='som.current-player-gpu-bridge.v1' and b['passed'] and b['sampled_frames']==255 and b['route_count']==85
  assert sha(historical)==b['historical_full_gpu_proof']['sha256'] and old['passed']
  assert b['historical_full_gpu_proof']['player_sha256']==old['player_sha256']
  assert sha(site/'capture-index.json')==b['capture_index_sha256']==old['capture_index_sha256']
  assert sha(site/'scripts/native_obj_player.gd')==b['player_sha256']==sha(root/'scripts/native_obj_player.gd')
  assert sha(site/'scripts/indexed_object.gdshader')==b['shader_sha256']==old['shader_sha256']==sha(root/'scripts/indexed_object.gdshader')
  assert sha(root/'evidence/rendered-route-validation.json')==b['new_gpu_evidence_sha256']
  assert sha(root/'evidence/raw-sample-validation.json')==b['independent_scalar_evidence_sha256']
  gpu=read(root/'evidence/rendered-route-validation.json');scalar=read(root/'evidence/raw-sample-validation.json')
  assert gpu['passed'] and gpu['rendered_frames']==255 and not gpu['errors'] and scalar['passed'] and scalar['frames']==255 and not scalar['issues']
  rows={r['id']:r for r in b['routes']};prior={r['id']:r for r in old['routes']};actual={r['id']:r for r in gpu['routes']}
  assert len(rows)==len(prior)==len(actual)==len(index['routes'])==85
  for e in index['routes']:
   r=rows[e['id']];d=read(site/e['path']);assert sha(site/e['path'])==r['route_sha256']==e['route_sha256']==prior[e['id']]['route_sha256']
   expected=[0,len(d['frames'])//2,len(d['frames'])-1]
   assert [s['frame_index']for s in r['samples']]==expected==actual[e['id']]['sample_indices'] and actual[e['id']]['pixel_differences']==0 and actual[e['id']]['frames']==3
   for s in r['samples']:
    f=d['frames'][s['frame_index']];assert f['source_tick']==s['source_tick'] and f['capture']==s['capture'] and f['expected_pixel_sha256']==s['golden_pixel_sha256']
    for n,h in s['raw_sha256'].items():assert sha(Path(s['capture'])/n)==h
    golden=Path(historical).parents[1]/f['expected_texture']
    assert sha(golden)==s['golden_png_sha256']
    # GPU screenshots are disposable; signed report/hash chain persists. Recheck if retained.
    png=root/'evidence/rendered'/f"{e['id']}-{s['frame_index']:04d}.png"
    if png.is_file():assert sha(png)==s['gpu_png_sha256']
  return {'passed':True,'scope':b['scope'],'sampled_frames':255}
 except (AssertionError,KeyError,OSError,ValueError) as exc:return {'passed':False,'error':type(exc).__name__+': '+str(exc)}

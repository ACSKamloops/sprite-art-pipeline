"""Mechanical source/render preservation; never an artistic approval."""
from pathlib import Path
import hashlib,json,importlib.util
from PIL import Image
ROOT=Path(__file__).resolve().parent
CONTROL=Path('/home/astra/projects/sprite-construction-lab/pilot/space-marine-captain/assembled-v18')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba(p):return Image.open(p).convert('RGBA')
def main():
 first=ROOT/'artifacts/loaded-v1/weighted';repeat=ROOT/'artifacts/loaded-repeat/weighted'
 a=json.loads((first/'manifest.json').read_text());old=json.loads((CONTROL/'manifest.json').read_text());b=json.loads((repeat/'manifest.json').read_text())
 spec=importlib.util.spec_from_file_location('upper_loaded',ROOT/'build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 # construct has writes: redirect exclusively to an existing private snapshot.
 mod.ROOT=ROOT/'artifacts/loaded-v1/snapshot/pilot/space-marine-captain/upper-body-rig-v1'
 design,parts=mod.construct();chest,waist=mod.torso_partition(design,parts['torso_pack'])
 assert all(not(c[3]and w[3])for c,w in zip(chest.get_flattened_data(),waist.get_flattened_data()))
 palette=set(rgba(ROOT/'source/approved-256.png').get_flattened_data())|{(34,17,22,255),(32,20,24,255),(58,18,24,255),(0,0,0,0)}
 for fp in (CONTROL/'layers').glob('*.png'):palette.update(rgba(fp).get_flattened_data())
 checks=0;changed=[];released=[];rows=[]
 assert a['layer_order']==old['layer_order'] and len(a['layer_order'])==9
 assert a['cycle_ms']==old['cycle_ms']==1200 and len(a['frames'])==72
 for i,(f,o,r) in enumerate(zip(a['frames'],old['frames'],b['frames'])):
  for key in ['landmarks','pelvis','physical_root','duration_ms','source_duration_ms']:assert f[key]==o[key],(i,key)
  assert f==r,(i,'repeat metadata')
  im=rgba(first/f['file']);ref=rgba(CONTROL/o['file']);again=rgba(repeat/r['file']);assert im.tobytes()==again.tobytes()
  assert set(im.getchannel('A').get_flattened_data())<={0,255}
  assert set(im.get_flattened_data())<=palette,(i,'new color')
  box=im.getbbox();assert box and box[0]>0 and box[1]>0 and box[2]<256 and box[3]<256,(i,'canvas clip')
  load=f['upper_attachments']['torso_pack']['load_pulse'];changed_pixels=sum(x!=y for x,y in zip(im.get_flattened_data(),ref.get_flattened_data()))
  if load==0:assert changed_pixels==0;released.append(i)
  else:changed.append(i)
  for layer in a['layer_order']:
   filename=f'{i:02}-{layer}.png';x=rgba(first/'layers'/filename);y=rgba(repeat/'layers'/filename);assert x.tobytes()==y.tobytes()
   assert set(x.getchannel('A').get_flattened_data())<={0,255};assert set(x.get_flattened_data())<=palette
   if layer in ['legs','near_shin_foreground','cape','tabard']:assert x.tobytes()==rgba(CONTROL/'layers'/filename).tobytes(),(i,layer)
   checks+=3
  head=f['upper_attachments']['head'];assert head['angle_clockwise_degrees']==0
  for p,q in zip(head['pivot'],o['upper_attachments']['head']['pivot']):assert abs(p-q)<=1.20000001
  rows.append({'frame':i,'load':load,'changed_fullbody_pixels':changed_pixels,'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest()});checks+=13
 report={'status':'MECHANICAL_PASS_NOT_ART_ACCEPTANCE','frames':72,'layers_per_frame':9,'checks':checks,'source_partition_exact':True,'source_partition_disjoint':True,'released_fullbody_exact_control_frames':released,'loaded_frames':changed,'unchanged_layers':['legs','near_shin_foreground','cape','tabard'],'unchanged_fields':['landmarks','pelvis','physical_root','duration_ms','source_duration_ms'],'hard_alpha_source_palette_only':True,'no_canvas_boundary_contact':True,'repeat_fullbody_and_all_layers_exact':True,'source_bindings':{n:sha(ROOT/n)for n in ['build.py','design.json','pixel_affine.py','source/approved-256.png','build_preview.py']},'root_readonly_bindings':{str(p):sha(p)for p in [CONTROL/'manifest.json',Path('/home/astra/projects/sprite-construction-lab/pilot/space-marine-captain/assemble.py'),Path('/home/astra/projects/sprite-construction-lab/pilot/space-marine-captain/retime.py')]},'candidate_manifest_sha256':sha(first/'manifest.json'),'rows':rows,'limits':['Only original three-quarter direction.','No new artistic score or approval.','No inherited full-actor Godot world-contact certificate.','Source partition proves ownership, not anatomical correctness.']}
 report['max_head_translation_per_axis_px']=[max(abs(f['upper_attachments']['head']['pivot'][j]-o['upper_attachments']['head']['pivot'][j])for f,o in zip(a['frames'],old['frames']))for j in range(2)]
 report['head_angle_locked_degrees']=0
 report['source_palette_scope']='Approved source plus immutable v18 leg/replacement-shin palettes and three explicitly inherited backing colors; no new RGBA colors.'
 frozen=CONTROL.parent/'upper-body-rig-v1'
 report['root_frozen_upper_file_hashes']={str(p):sha(p)for p in frozen.rglob('*')if p.is_file()and '__pycache__'not in str(p)}
 (ROOT/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','frames','checks','released_fullbody_exact_control_frames']}))
if __name__=='__main__':main()

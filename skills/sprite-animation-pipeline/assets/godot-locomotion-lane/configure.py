#!/usr/bin/env python3
"""Copy a selected rational-hold manifest into this isolated Godot consumer."""
import argparse, hashlib, json, pathlib, shutil
from fractions import Fraction
def attach_clock(manifest):
 total=Fraction(0)
 boundaries=[]
 for frame in manifest["frames"]:
  hold=Fraction(*frame["hold"]);assert hold>0
  total+=hold;boundaries.append([total.numerator,total.denominator])
 if "duration" in manifest:assert Fraction(*manifest["duration"])==total, "duration must equal rational holds"
 manifest["runtime_boundaries"]=boundaries;manifest["runtime_duration"]=[total.numerator,total.denominator]
 return manifest
p=argparse.ArgumentParser();p.add_argument('manifest',type=pathlib.Path);p.add_argument('--stride',type=float,default=48);p.add_argument('--idle',type=pathlib.Path);p.add_argument('--idle-pivot',nargs=2,type=float);p.add_argument('--contacts',type=pathlib.Path);p.add_argument('--stance-lock',action='store_true');p.add_argument('--bank',type=pathlib.Path);a=p.parse_args()
base=pathlib.Path(__file__).resolve().parent
m=attach_clock(json.loads(a.manifest.read_text())); assert len(m['canvas'])==2 and len(m['pivot'])==2
out=base/'selected';out.mkdir(exist_ok=True)
pins=[]
for i,f in enumerate(m['frames']):
 src=a.manifest.parent/f['file'];h=hashlib.sha256(src.read_bytes()).hexdigest();assert h==f['sha256'];assert f['hold'][0]>0 and f['hold'][1]>0
 dst=f'{i:04}.png';shutil.copyfile(src,out/dst);pins.append({'source':str(src.resolve()),'sha256':h});f['file']=dst
assert m['frames'] and a.stride>0
(out/'manifest.json').write_text(json.dumps(m,indent=2))
c={'manifest':'res://selected/manifest.json','stride_pixels':a.stride,'scale':2,'idle_frame':0,'idle_status':'PROTOTYPE: held walk pose; authored braced idle pending','start_root':[72,250],'lane_end':550,'idle_file':'','idle_pivot':m['pivot']}
if a.idle:
 shutil.copyfile(a.idle,out/'idle.png');c.update(idle_file='res://selected/idle.png',idle_pivot=a.idle_pivot or m['pivot'],idle_status='Authored braced idle (single pose)');pins.append({'source':str(a.idle.resolve()),'sha256':hashlib.sha256(a.idle.read_bytes()).hexdigest()})
if a.contacts:
 contact=json.loads(a.contacts.read_text());assert len(contact['frames'])==len(m['frames'])
 for i,item in enumerate(contact['frames']):
  if item.get('flat'):
   assert 'episode' in item and len(item['anchor'])==2
   for field in ['foot_mask','visible_foot_mask']:
    if field in item:
     src=a.contacts.parent/item[field];dst=f'{field}-{i:04}.png';shutil.copyfile(src,out/dst);item[field]=dst;pins.append({'source':str(src.resolve()),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
 (out/'contacts.json').write_text(json.dumps(contact,indent=2));c.update(contacts='res://selected/contacts.json',stance_lock=a.stance_lock)
 pins.append({'source':str(a.contacts.resolve()),'sha256':hashlib.sha256(a.contacts.read_bytes()).hexdigest()})
if a.bank:
 bank=json.loads(a.bank.read_text());assert bank['schema']=='authored-locomotion-bank/v1'
 assert bank['idle_variants'], 'at least one idle variant required'
 bank.setdefault('initial_idle',next(iter(bank['idle_variants'])))
 assert bank['initial_idle'] in bank['idle_variants']
 assert set(bank['start_by_idle'])==set(bank['idle_variants']), 'each idle variant needs its own authored start'
 for key in ['walk_manifest_sha256','source_walk_manifest_sha256']:
  if key in bank:assert bank[key]==hashlib.sha256(a.manifest.read_bytes()).hexdigest(), 'bank walk fingerprint mismatch'
 if 'source_walk' in bank:assert bank['source_walk']['sha256']==hashlib.sha256(a.manifest.read_bytes()).hexdigest(), 'bank source_walk hash mismatch'
 bankout=out/'bank';bankout.mkdir(exist_ok=True)
 sourceclips={}
 def copyclip(relative):
  if relative in sourceclips:return sourceclips[relative]
  srcmanifest=a.bank.parent/relative;clip=attach_clock(json.loads(srcmanifest.read_text()));assert clip['canvas']==m['canvas'] and clip['pivot']==m['pivot']
  name=f'clip-{len(sourceclips):03}';folder=bankout/name;folder.mkdir(exist_ok=True)
  pins.append({'source':str(srcmanifest.resolve()),'sha256':hashlib.sha256(srcmanifest.read_bytes()).hexdigest()})
  for i,frame in enumerate(clip['frames']):
   source=srcmanifest.parent/frame['file'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==frame['sha256'];assert frame['hold'][0]>0 and frame['hold'][1]>0
   target=f'{i:04}.png';shutil.copyfile(source,folder/target);frame['file']=target;pins.append({'source':str(source.resolve()),'sha256':digest})
  (folder/'manifest.json').write_text(json.dumps(clip,indent=2));sourceclips[relative]=(f'{name}/manifest.json',clip);return sourceclips[relative]
 idleclips={}
 for key,entry in bank['idle_variants'].items():entry['manifest'],idleclips[key]=copyclip(entry['manifest'])
 seenstops=set()
 def validate_curve(binding,clip):
  from fractions import Fraction
  curve=binding['root_curve'];times=[Fraction(*sample['time']) for sample in curve];duration=sum(Fraction(*f['hold']) for f in clip['frames'])
  assert times[0]==0 and curve[0]['offset']==[0,0] and times[-1]==duration
  assert all(b>a for a,b in zip(times,times[1:]))
  assert not clip['loop']
 for entry in bank['stop_by_walk_frame']:
  entry['manifest'],clip=copyclip(entry['manifest']);i=entry['walk_frame'];assert i not in seenstops;seenstops.add(i)
  assert clip['frames'][0]['sha256']==m['frames'][i]['sha256'], 'stop first must match walk pose'
  assert clip['frames'][-1]['sha256']==idleclips[entry['to_idle']]['frames'][0]['sha256'], 'stop last must match idle'
  validate_curve(entry,clip)
 assert seenstops==set(range(len(m['frames'])))
 for key,entry in bank['start_by_idle'].items():
  entry['manifest'],clip=copyclip(entry['manifest']);assert clip['frames'][0]['sha256']==idleclips[key]['frames'][0]['sha256'];assert clip['frames'][-1]['sha256']==m['frames'][entry['walk_entry_frame']]['sha256'];validate_curve(entry,clip)
 (bankout/'bank.json').write_text(json.dumps(bank,indent=2));c.update(bank='res://selected/bank/bank.json',idle_status='Guarded stance with authored start and stop poses')
 pins.append({'source':str(a.bank.resolve()),'sha256':hashlib.sha256(a.bank.read_bytes()).hexdigest()})
(base/'runtime-config.json').write_text(json.dumps(c,indent=2))
(base/'SOURCE-PINS.json').write_text(json.dumps({'manifest':str(a.manifest.resolve()),'manifest_sha256':hashlib.sha256(a.manifest.read_bytes()).hexdigest(),'frames':pins,'coverage':'one authored view and walk; no mirroring','dependencies':['Godot 4.7.2','Python stdlib for configuration'],'adapter_reference':'sprite-animation-pipeline/scripts/project_delivery.py (optional upstream adapter)'},indent=2))
print(f'Configured {len(m["frames"])} poses; cycle {sum(f["hold"][0]/f["hold"][1] for f in m["frames"]):.6f}s')

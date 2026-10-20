#!/usr/bin/env python3
"""Read-only authority/hash, exact-map, ownership, plateau and media verification."""
from pathlib import Path
import json,hashlib,subprocess
import numpy as np
from PIL import Image
from scipy.ndimage import label
from build_key_bridges import resolve_paths
ROOT=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def image(p):return np.array(Image.open(p).convert('RGBA'))
counts={'frames':0,'exact_key_replays':0,'frozen_bridge_replays':0,'complete_rigid_boot_pixels':0,'distal_strip_plateau_pixels':0,'connected_frames':0,'mp4_clocks':0}
for actor in ('lyra','rowan'):
 c=ROOT/'configs'/f'{actor}.json';cfg=resolve_paths(json.loads(c.read_text()),c)
 for view,v in cfg['views'].items():
  keys={int(k):r for k,r in v['keys'].items()};ims={k:image(r['path']) for k,r in keys.items()}
  for k,r in keys.items():
   assert sha(r['path'])==r['sha256']
   for record in list(r['frozen_owners'].values())+r['frozen_boots']:assert sha(record['path'])==record['sha256']
  d=ROOT/'selected'/actor/view;receipt=json.loads((d/'receipt.json').read_text());assert receipt['holds']==[[9,160]]*8
  for fr in receipt['frames']:
   i=fr['frame'];actual=image(d/f'{i:02d}.png');assert sha(d/f'{i:02d}.png')==fr['output_sha256'];counts['frames']+=1
   if i%2==0:assert np.array_equal(actual,ims[i]);counts['exact_key_replays']+=1
   else:
    m=np.load(d/f'{i:02d}-map.npz');owner=m['owner'];xy=m['source_xy'];body=ims[fr['body_key']];replay=body.copy();replay[owner==3]=0
    yy,xx=np.indices((128,128));outcoords=np.stack((xx,yy),axis=-1)
    for leg,control in enumerate(fr['controls'],1):
     src=ims[control['source_key']];chosen=owner==leg;replay[chosen]=src[xy[:,:,1][chosen],xy[:,:,0][chosen]];delta=np.array(control['rigid_boot_translation'])
     if v['map_method']=='rigid_boot_mesh':
      mark=m['rigid_boot']==leg;assert np.all((outcoords-xy)[mark]==delta);counts['complete_rigid_boot_pixels']+=int(mark.sum())
      boot=np.array(Image.open(keys[control['source_key']]['frozen_boots'][leg-1]['path']))>0;assert not np.any(chosen&boot[xy[:,:,1],xy[:,:,0]]&~mark)
      assert control['mesh_controls']['minimum_area_product']>0
     else:
      distal=chosen&(yy>=control['boot_rigid_below_source_y']+delta[1]);assert np.all((outcoords-xy)[distal]==delta);counts['distal_strip_plateau_pixels']+=int(distal.sum())
    assert np.array_equal(replay,actual);assert np.array_equal(actual[~m['allowed']],body[~m['allowed']]);counts['frozen_bridge_replays']+=1
   lab,n=label(actual[:,:,3]>=24);components=np.bincount(lab.ravel())[1:];assert int((components>=3).sum())==1;(counts.__setitem__('connected_frames',counts['connected_frames']+1))
  for scale in ('native','game'):
   r=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate,nb_frames,duration','-of','json',str(d/f'candidate-{scale}.mp4')],capture_output=True,text=True,check=True);s=json.loads(r.stdout)['streams'][0];assert s['r_frame_rate']=='160/1' and s['nb_frames']=='576' and abs(float(s['duration'])-3.6)<1e-6;counts['mp4_clocks']+=1
print(json.dumps({'passed':counts,'art_acceptance':False,'note':'This verifies mechanical reproduction and clocks; continuous motion, anatomy and game appearance require independent judgment.'}))

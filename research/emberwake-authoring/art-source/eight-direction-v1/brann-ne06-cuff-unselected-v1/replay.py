"""Fresh one-cel source-map replay only. No editor or fullbank construction."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def a(p):return np.array(Image.open(p).convert('RGBA'))
for item in json.loads((R/'INPUTS.json').read_text()):assert sha(R/item['local'])==item['sha256']
recipe=json.loads((R/'CUFF-RECIPE.json').read_text());src=a(R/'inputs/current/06.png');donor=a(R/'inputs/current/07.png');z=np.load(R/'maps/literal-cuff-repair.npz');mask=z['owner'];mp=z['source_xy'];new=src.copy();new[mask]=donor[mp[mask,1],mp[mask,0]]
for op in recipe['operations']:
 x,y=op['destination'];sx,sy=op['new_source_xy'];assert src[y,x].tolist()==op['actual_before_RGBA'];assert donor[sy,sx].tolist()==op['literal_source_RGBA'];assert new[y,x].tolist()==op['new_RGBA']
assert np.array_equal(new,a(R/'final/06.png'));assert np.array_equal(new[~mask],src[~mask])
checks={}
for name,p in [('P_positive_boot','masks/retained-positive-P-boot.png'),('Q_positive_boot','masks/retained-positive-Q-boot.png'),('upper_sash','masks/upper-sash-protected.png')]:
 m=np.array(Image.open(R/p))>0;assert np.array_equal(src[m],new[m]);checks[name+'_RGBA_exact']=True
assert np.array_equal((new[:,:,3]!=src[:,:,3]),z['underpaint_owner'])
out.mkdir(parents=True);p=out/'06.png';Image.fromarray(new).save(p);assert p.read_bytes()==(R/'final/06.png').read_bytes();(out/'06.rgba').write_bytes(new.tobytes())
receipt={'status':'exact one conservative cuff construction replay, no art/wholecycle approval','candidate_sha256':sha(p),'PNG_and_RGBA_exact':True,'source_colors_all18_exact':True,'RGBA_changes':int(mask.sum()),'new_cloth_coverage':int(z['underpaint_owner'].sum()),'checks':checks,'outside18_RGBA_exact':True,'all_other_alpha_exact':True,'neighbor05_07_unchanged':{f'{i:02}':sha(R/f'inputs/current/{i:02}.png')for i in (5,7)},'clock_unchanged':{'hold':[9,160],'total':[9,20]},'model_calls':0,'editor_or_fullbank':False}
(out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

from pathlib import Path
from PIL import Image
import importlib.util,json,hashlib
R=Path('/home/astra/projects/emberwake-demo');P=Path('/home/astra/artifacts/emberwake-walk-game-preview-v10');O=Path(__file__).parent
spec=importlib.util.spec_from_file_location('audit_baker',R/'scripts/bake_eight_directions.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
c=json.loads((R/'art-source/eight-direction-v1/registration-v10-brann-front-weight.json').read_text());re=json.loads((P/'bake/REPLAY.json').read_text());bakerhash=hashlib.sha256((R/'scripts/bake_eight_directions.py').read_bytes()).hexdigest();assert bakerhash==re['baker_sha256']
records=[]
for actor,views in c['actors'].items():
 for view,s in views.items():
  im=Image.open(R/s['raw']).convert('RGBA').resize((2048,1024),Image.Resampling.NEAREST)
  a,masks,owner=mod.source_owners(im)
  for i in (8,9,10,11,12,13,14,17,18,19,20,22):
   override=s.get('cell_overrides',{}).get(str(i))
   if override:
    expected=Image.open(R/override['path']).convert('RGBA');kind='selected_override'
   else:
    px=mod.np.zeros_like(a);px[masks[i]]=a[masks[i]];px[:,:,3][px[:,:,3]>245]=255;px[px[:,:,3]<24]=0
    ax,ay=s['row_anchors'][i//8];sx=i%8*256+ax;sy=i//8*256+ay;sc=s['scale']
    expected=Image.fromarray(px).transform((128,128),Image.Transform.AFFINE,(1/sc,0,sx-64/sc,0,1/sc,sy-112/sc),Image.Resampling.NEAREST);kind='uniform_registered_new_diagonal_paint'
   actual=Image.open(P/f'bake/{actor}/{view}/{i:02}.png').convert('RGBA')
   assert expected.tobytes()==actual.tobytes(),(actor,view,i)
   records.append({'hero':actor,'view':view,'source_cell':i,'provenance':kind,'exact_rgba_reconstructed':True})
(O/'registration-verification.json').write_text(json.dumps({'baker_matches_v10_receipt':True,'records':records,'note':'In-memory source ownership/extraction and transform only. No baker output or canonical write.'},indent=2)+'\n')
print(json.dumps({'selected_source_cells':len(records),'overrides':sum(r['provenance']=='selected_override' for r in records),'all_reconstructed_exact':True}))

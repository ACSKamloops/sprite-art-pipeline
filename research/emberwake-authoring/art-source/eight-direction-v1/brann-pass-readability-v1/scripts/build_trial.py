"""Single literal source-palette contact-shadow hypothesis; no pose/alpha edits."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGBA'))
src={i:arr(R/f'inputs/control/{i:02}.png')for i in range(8)}
donor=arr(R/'inputs/parts/donor00.png')
# Hand-traced locations, not an RGB selection or mask dilation. Q is the
# screen-left foreground part in these retained source constructions; P is
# the screen-right rear part. These names describe paint/depth, not anatomy.
plans={
3:{'contact':[(68,92),(68,93),(68,94),(70,98),(71,99),(72,100),(73,101),(74,102),(74,103),(75,104)],
   'falloff':[(69,92),(69,93),(71,98),(72,99),(73,100),(74,101),(75,102),(75,103),(76,104)]},
4:{'contact':[(66,92),(67,93),(67,94),(68,95),(68,96),(68,97),(68,99),(69,100),(71,101),(72,102),(74,103)],
   'falloff':[(68,93),(69,95),(69,96),(69,97),(69,99),(70,100),(72,101),(73,102)]}}
colors={'contact':(82,100),'falloff':(80,94)}
ops=[];frames=[]
for i in (3,4):
 a=src[i];b=a.copy();p=arr(R/f'inputs/parts/{i:02}-P.png');q=arr(R/f'inputs/parts/{i:02}-Q.png')
 pm=np.load(R/f'inputs/parts/{i:02}-P-map.npz')['source_xy']
 qm=np.load(R/f'inputs/parts/{i:02}-Q-map.npz')['source_xy']
 owner=np.zeros((128,128),np.uint8)
 for role,coords in plans[i].items():
  sx,sy=colors[role];color=donor[sy,sx]
  for x,y in coords:
   assert owner[y,x]==0 and p[y,x,3]>=240 and a[y,x,3]>=240
   assert q[y,x,3]<128, 'Shade rear-visible P, not the core foreground Q.'
   assert np.any(q[y,max(0,x-2):x,3]>=128),'Literal location must touch or closely follow actual Q edge.'
   assert color[0]<=a[y,x,0], 'This one hypothesis only shades the rear plane.'
   owner[y,x]=255;b[y,x,:3]=color[:3]
   ops.append({'frame':i,'destination':[x,y],'old_RGBA':a[y,x].tolist(),'new_RGBA':b[y,x].tolist(),
     'material':'existing visible rear P brown leather; contact shadow from foreground Q',
     'authored_RGB_shading':True,'role':role,'color_source':'inputs/parts/donor00.png',
     'color_source_xy':[sx,sy],'color_source_RGBA':color.tolist(),
     'actual_P_layer_RGBA':p[y,x].tolist(),'P_source_xy':pm[y,x].tolist(),
     'actual_Q_fringe_RGBA':q[y,x].tolist(),'Q_source_xy':qm[y,x].tolist(),
     'depth_reason':'Q is composited after P in the retained boot recipe; this rear-visible band follows its existing curved overlap edge.',
     'alpha_rule':'keep destination alpha byte exactly; source RGB only is newly authored shading'})
 assert np.array_equal(a[...,3],b[...,3]);assert np.array_equal(a[owner==0],b[owner==0])
 assert np.array_equal(np.any(a!=b,axis=2),owner>0)
 Image.fromarray(b).save(R/f'candidate/{i:02}.png');Image.fromarray(owner).save(R/f'masks/{i:02}-literal-RGB-owner.png')
 frames.append({'frame':i,'changed_RGB_pixels':int((owner>0).sum()),'original_sha256':sha(R/f'inputs/control/{i:02}.png'),
  'trial_sha256':sha(R/f'candidate/{i:02}.png'),'all_alpha_exact':True,'all_outside_owner_RGBA_exact':True})
for i in (0,1,2,5,6,7):assert (R/f'inputs/control/{i:02}.png').read_bytes()==(R/f'candidate/{i:02}.png').read_bytes()
record={'status':'UNSELECTED one bounded overlap-depth trial; parent inspection before packaging',
 'model_calls':0,'authored_shading_pixels':len(ops),'new_colors_invented':False,'wholebank_filter_or_RGB_selector':False,
 'outer_silhouette_and_alpha_exact':True,'boot_positions_volumes_and_occlusion_geometry_exact':True,
 'all_upper_cloth_skin_gloves_exact':True,'unchanged_six_PNGs_exact':True,
 'timing':{'exposures':8,'hold':[9,160],'cycle':[9,20]},'roles':'P/Q refer to retained projected paint layers; no hidden anatomy recovered.',
 'frames':frames,'operations':ops}
(R/'RGB-DEPTH-RECIPE.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k]for k in ['authored_shading_pixels','frames','all_upper_cloth_skin_gloves_exact','unchanged_six_PNGs_exact']},indent=2))

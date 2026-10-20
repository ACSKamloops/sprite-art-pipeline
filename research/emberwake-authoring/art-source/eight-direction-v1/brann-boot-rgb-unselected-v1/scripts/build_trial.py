"""One bounded RGB-only cuff/overlap source-palette trial; no geometry/alpha changes."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
def a(i):return np.array(Image.open(R/'inputs/control'/f'{i:02}.png').convert('RGBA'))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
source={i:a(i) for i in range(8)}
# Literalexisting leather RGB witnesses. Destination alpha isalways preservedexactly.
color={'rimsoft':(0,68,95),'rimmid':(5,55,95),'rimlight':(0,72,94),'rimtransition':(5,56,95),'shadowsoft':(0,80,92),'shadowdeep':(0,78,92)}
plans={
3:{'rimsoft':[(55,93)],'rimmid':[(56,93)],'rimtransition':[(57,93)],'shadowdeep':[(71,98),(72,99),(76,104)],'shadowsoft':[(73,100),(74,101),(75,102),(76,103)]},
4:{'rimsoft':[(52,95)],'rimtransition':[(53,95)],'rimlight':[(54,95)],'shadowdeep':[(68,97),(68,98),(69,99),(75,103)],'shadowsoft':[(71,100),(73,101),(74,102)]},
5:{'rimmid':[(54,95)],'rimtransition':[(55,95)],'rimlight':[(56,95)],'shadowsoft':[(68,94),(68,97),(68,98)],'shadowdeep':[(68,95),(68,96),(68,99),(69,100),(69,101),(70,102)]}}
operations=[];receipts=[]
for phase,strokes in plans.items():
 old=source[phase];new=old.copy();owner=np.zeros((128,128),np.uint8);used=set()
 for role,coords in strokes.items():
  sid,sx,sy=color[role];sample=source[sid][sy,sx];rgb=sample[:3]
  for x,y in coords:
   assert (x,y) not in used;used.add((x,y));before=old[y,x].copy();rr,gg,bb,aa=map(int,before);assert y>=93 and aa>=240 and rr>gg*1.35 and gg>bb*1.1,'Literalowner must remainexisting coreleather';new[y,x,:3]=rgb;owner[y,x]=255;operations.append({'phase':phase,'destination':[x,y],'expected_RGBA':before.tolist(),'source_file':f'inputs/control/{sid:02}.png','source_xy':[sx,sy],'source_RGBA_witness':sample.tolist(),'new_RGB':rgb.tolist(),'preserved_destination_alpha':int(before[3]),'authored_shading_role':'foreground upperleftcuff rim continuation' if role.startswith('rim') else 'rear leather underforegroundQocclusion shadow','stroke_role':role})
 assert np.array_equal(new[...,3],old[...,3]);assert np.array_equal(new[owner==0],old[owner==0]);Image.fromarray(new).save(R/'candidate'/f'{phase:02}.png');Image.fromarray(owner).save(R/'masks'/f'{phase:02}-RGB-owner.png');diff=np.any(old[:,:,:3]!=new[:,:,:3],axis=-1);assert np.array_equal(diff,owner>0);receipts.append({'phase':phase,'authored_RGB_pixels':int(diff.sum()),'alpha_silhouette_pose_exact':True,'all_other_RGBA_exact':True,'new_sha256':sha(R/'candidate'/f'{phase:02}.png')})
for phase in [0,1,2,6,7]:assert (R/'candidate'/f'{phase:02}.png').read_bytes()==(R/'inputs/control'/f'{phase:02}.png').read_bytes()
journal={'status':'Unselected bounded localshading trial, parentpreviewbeforeeditorpackage','new_authored_shading':True,'source_palette_reuse':'RGBonlyfromactualretainedleathertexels; destinationalphaunchanged. Shapes/poses/materialregionsfixed.','light_direction':'Upperleftcuffarcs lit; contactshadowonthePsurfacebehindQ. No newlight source.','operations':operations,'global_color_transform':False,'silhouette_alpha_or_position_changes':False,'new_RGB_colors_invented':False,'model_calls':0,'clock':{'holds':[9,160],'cycle':[9,20]},'frames':receipts};(R/'RGB-STROKE-JOURNAL.json').write_text(json.dumps(journal,indent=2)+'\n');print(json.dumps({'authored_RGB_pixels_total':len(operations),'per_frame':receipts,'source_colors':{k:source[s][y,x].tolist() for k,(s,x,y) in color.items()},'all8_alpha_silhouette_positions_exact':True,'other5_original_PNG_bytes_exact':True},indent=2))

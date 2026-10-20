from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,sys,importlib.util
P=Path(__file__).resolve().parent;S=P/'inputs';OUT=P/'candidate-v2';OUT.mkdir(exist_ok=True);PROOF=P/'proofs-v2';PROOF.mkdir(exist_ok=True);MAPS=P/'maps-v2';MAPS.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('source_warp',P/'tools/source_warp.py');warp=importlib.util.module_from_spec(spec);spec.loader.exec_module(warp)
source_polys={
 'southeast-prep':[(85,43),(89,43),(89,37),(92,36),(94,38),(94,43),(98,40),(101,38),(102,40),(101,43),(104,42),(106,43),(106,46),(102,48),(107,48),(108,50),(106,52),(100,53),(98,56),(96,58),(94,62),(91,65),(86,65),(82,62),(83,57),(85,53),(84,49),(82,47),(82,45)],
 'northeast-prep':[(94,45),(96,43),(99,43),(100,40),(103,39),(105,41),(104,44),(108,41),(110,42),(111,44),(108,46),(111,46),(112,48),(110,50),(106,51),(111,51),(112,53),(110,55),(105,55),(101,57),(100,61),(97,66),(93,68),(89,66),(89,61),(91,56),(94,52),(94,49)],
 'southeast-recovery':[(79,74),(85,74),(87,77),(88,81),(88,85),(86,88),(83,91),(81,91),(80,87),(78,87),(77,85),(78,82),(78,78)],
 'northeast-recovery':[(83,70),(88,70),(91,74),(94,78),(97,81),(98,83),(96,85),(95,88),(92,89),(89,87),(88,85),(85,85),(84,83),(83,83),(83,80),(84,78),(81,76),(80,74),(80,72)]}
configs=[]
for v in ['southeast','northeast']:
 for n in [17,18,20]:
  prep=n!=20;donor='00-cast-prep.png' if prep else '02-cast-recovery.png'
  if v=='southeast':
   tx,ty=((-5,6) if n==17 else (-3,5)) if prep else (-7,-7)
   oldpoly=[(63,59),(70,59),(76,62),(78,67),(77,72),(72,75),(65,74),(62,70)] if n!=20 else [(65,60),(73,60),(77,63),(79,67),(77,72),(71,75),(65,72),(63,67)]
   rigid=[82,36,109,62] if prep else [77,74,91,92]
   proximal=[([86,65],[81,70]),([91,65],[85,70])] if prep else []
  else:
   tx,ty=((-6,3) if n==17 else (-4,2)) if prep else (-2,-5)
   oldpoly=[(80,50),(85,50),(88,54),(90,60),(89,64),(85,66),(81,64)] if prep else [(84,61),(91,61),(95,65),(95,70),(91,73),(85,73),(82,70),(82,66)]
   rigid=[94,39,113,62] if prep else [80,70,99,90]
   proximal=[([90,65],[82,69]),([93,68],[85,71])] if prep else []
  configs.append({'view':v,'frame':n,'body':f'inputs/registered/{v}/{n:02}.png','underpaint':f'inputs/registered/{v}/22.png','donor':f'inputs/donors/{v}/{donor}','source_polygon':source_polys[v+('-prep' if prep else '-recovery')],'old_fist_polygon':oldpoly,'rigid_roi':rigid,'translation':[tx,ty],'proximal_controls':proximal,'seam_repairs':[]})
# Config is source-authoritative for reproduction, not inferred pose anatomy.
(P/'construction-spec-v2.json').write_text(json.dumps({'canvas':[128,128],'pivot':[64,112],'body_ownership':'Original17/18/20 except explicit old-fist underpaint and target hand/forearm ownership masks.','configs':configs},indent=2)+'\n')
records=[]
def mask(poly):
 m=Image.new('L',(128,128),0);ImageDraw.Draw(m).polygon(poly,fill=255);return np.array(m)>0
for conf in configs:
 v,n=conf['view'],conf['frame'];base=np.array(Image.open(P/conf['body']).convert('RGBA'));under=np.array(Image.open(P/conf['underpaint']).convert('RGBA'));donor=np.array(Image.open(P/conf['donor']).convert('RGBA'));srcmask=mask(conf['source_polygon']);oldmask=mask(conf['old_fist_polygon']);tx,ty=conf['translation'];r=conf['rigid_roi'];controls={}
 for q in [(0,0),(127,0),(127,127),(0,127)]:controls[q]=list(q)
 # Dense controls keep the complete hand/cuff shape on one rigid translation plateau.
 for y in sorted(set(list(range(r[1],r[3],2))+[r[3]-1])):
  for x in sorted(set(list(range(r[0],r[2],2))+[r[2]-1])):controls[(x,y)]=[x+tx,y+ty]
 for src,dst in conf['proximal_controls']:
  # Progress follows the declared same plateau; proximal changes remain small.
  if n==18:dst=[dst[0]+2,dst[1]-1]
  controls[tuple(src)]=dst
 c={'source_points':[list(x) for x in controls],'target_points':list(controls.values())};xy,tris,ratios=warp.make_map(c,np.ones((128,128),dtype='uint8'));sampled=donor[xy[:,:,1],xy[:,:,0]];owns=srcmask[xy[:,:,1],xy[:,:,0]] & (sampled[:,:,3]>0)
 # The literal old-fist union includes antialiased edges, then donor's complete owned arm.
 result=base.copy();result[oldmask]=under[oldmask];result[owns]=sampled[owns];union=oldmask|owns
 outside=np.array_equal(result[~union],base[~union]);assert outside
 name=f'{v}-{n:02}';folder=OUT/v;folder.mkdir(exist_ok=True);Image.fromarray(result).save(folder/f'{n:02}.png');Image.fromarray((oldmask*255).astype('uint8')).save(MAPS/f'{name}-old-fist-mask.png');Image.fromarray((srcmask*255).astype('uint8')).save(MAPS/f'{name}-donor-source-mask.png');Image.fromarray((owns*255).astype('uint8')).save(MAPS/f'{name}-donor-target-mask.png');Image.fromarray((union*255).astype('uint8')).save(MAPS/f'{name}-union-mask.png')
 yy,xx=np.indices((128,128));owner=np.zeros((128,128),dtype='uint8');owner[oldmask]=1;owner[owns]=2;coords=np.stack([xx,yy],axis=-1).astype('int16');coords[owns]=xy[owns];np.savez_compressed(MAPS/f'{name}-source-map.npz',source_kind=owner,source_xy=coords);(MAPS/f'{name}-warp-controls.json').write_text(json.dumps({**c,'triangles':tris.tolist(),'triangle_area_ratio_range':ratios,'rigid_roi':r,'rigid_translation':[tx,ty]},indent=2)+'\n')
 # Independent replay from the frozen owner/map; body and clothing slots remain distinct.
 replay=base.copy();replay[owner==1]=under[owner==1];replay[owner==2]=donor[coords[:,:,1][owner==2],coords[:,:,0][owner==2]];assert np.array_equal(replay,result)
 changed=np.any(result!=base,axis=2);records.append({'view':v,'frame':n,'output':str((folder/f'{n:02}.png').relative_to(P)),'changed_pixels':int(changed.sum()),'union_owned_pixels':int(union.sum()),'underpaint_owned_pixels':int((owner==1).sum()),'donor_owned_pixels':int((owner==2).sum()),'outside_union_rgba_exact':outside,'map_replay_exact':True,'rgba_sha256':hashlib.sha256(result.tobytes()).hexdigest(),'triangle_area_ratio_range':ratios,'manual_seam_repairs':0})
# Release stays byte-for-byte source; original22 is context, never a new neutral.
for v in ['southeast','northeast']:
 (OUT/v/'19.png').write_bytes((S/'registered'/v/'19.png').read_bytes())
 for bg,color,fg in [('dark',(30,34,43,255),'white'),('light',(220,218,207,255),'black')]:
  rows=[]
  for scale in [2,1,.66]:
   size=round(128*scale)
   for variant in ['original','hybrid']:
    fs=[22,17,18,19,20,22];row=Image.new('RGBA',(6*size,size+40),color);dr=ImageDraw.Draw(row);dr.text((3,3),f'{v} {variant} {scale}x {bg}',fill=fg)
    for j,n in enumerate(fs):
     src=(OUT/v/f'{n:02}.png') if variant=='hybrid' and n!=22 else (S/'registered'/v/f'{n:02}.png');im=Image.open(src).convert('RGBA');dr.text((j*size+3,18),f'{n:02}',fill=fg);row.alpha_composite(im.resize((size,size),Image.Resampling.NEAREST),(j*size,39))
    rows.append(row)
  out=Image.new('RGBA',(max(i.width for i in rows),sum(i.height for i in rows)),(70,70,70,255));y=0
  for row in rows:out.alpha_composite(row,(0,y));y+=row.height
  out.convert('RGB').save(PROOF/f'{v}-{bg}-chronology.png')
(P/'proof-v2.json').write_text(json.dumps({'records':records,'model_calls':0,'release19_png_bytes_preserved':True,'preservation_boundary':'Exact outside declared old-fist+donor union, including alpha. Clothing underpaint is copied from source22 only inside the explicit old-fist mask; no hidden anatomy claim.'},indent=2)+'\n');print(json.dumps(records,indent=2))

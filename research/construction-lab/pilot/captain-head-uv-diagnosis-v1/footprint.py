from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,gzip
out=Path(__file__).parent;a=np.load(out/'source-uv-triangles.npz');h=Image.new('L',(2048,2048));n=h.copy();dh=ImageDraw.Draw(h);dn=ImageDraw.Draw(n)
for uv,head in zip(a['uv'],a['head']):
 points=[(float(u*2048),float((1-v)*2048))for u,v in uv];(dh if head else dn).polygon(points,fill=255)
ha=np.array(h)>0;na=np.array(n)>0;guard=np.array(n.filter(ImageFilter.MaxFilter(5)))>0;safe=ha&~guard;vis=json.load(open(out/'visible-head-pixel-map.json'));named=json.load(open(out/'named-feature-rays.json'))
h.save(out/'head-UV-occupancy.png');n.save(out/'nonhead-shared-image-UV-occupancy.png');Image.fromarray(safe.astype('uint8')*255).save(out/'proposed-head-owned-edit-footprint.png')
r=[]
for p in named:
 x,y=p['texture_xy_top_origin'];p['conservative_head_edit_safe']=bool(0<=x<2048 and 0<=y<2048 and safe[y,x]);r.append(p)
(out/'named-feature-rays.json').write_text(json.dumps(r,indent=2)+'\n')
pix=np.load(out/'packed-texture-linear-float.npy');im=Image.fromarray(np.clip(np.flipud(pix)*255+.5,0,255).astype('uint8'));im.save(out/'packed-source-texture.png');c=im.convert('RGB');ov=np.array(c);ov[ha&na]=[255,0,255];ov[ha&~na]=ov[ha&~na]//2+[0,110,0];Image.fromarray(ov).save(out/'atlas-head-ownership-overlay.png')
patches=[((1490,210,1600,340),'face/forehead UV'),((1860,380,2020,530),'hair/front UV'),((0,1760,140,1950),'eye/temple UV')];canvas=Image.new('RGB',(750,420),(35,40,45));d=ImageDraw.Draw(canvas)
for i,(roi,label)in enumerate(patches):
 crop=im.crop(roi);z=min(240//crop.width,380//crop.height);crop=crop.resize((crop.width*z,crop.height*z),Image.Resampling.NEAREST);canvas.paste(crop,(i*250,0),crop.getchannel('A'));d.text((i*250,390),label,fill='white');d.text((i*250,406),str(roi),fill='white')
canvas.save(out/'atlas-feature-crops.png')
summary={'policy':'Proposed texel footprint only, no edit. Head triangles require all vertices solely head weight1. All triangles sampling same packed image across body and two boot objects are rasterized. Nonhead/boundary occupancy expanded2texels before subtracting. Float UV polygon raster occupancy is an approximate conservative diagnostic, not exact continuous filter proof; recheck candidate pixels analytically before mutation.','head_occupied_texels':int(ha.sum()),'nonhead_occupied_texels':int(na.sum()),'shared_head_nonhead_raster_texels':int((ha&na).sum()),'head_candidate_safe_texels':int(safe.sum()),'visible_ray_pixels':len(vis),'visible_pixel_texels_outside_candidate':sum(not(0<=p['texture_xy_top_origin'][0]<2048 and 0<=p['texture_xy_top_origin'][1]<2048 and safe[p['texture_xy_top_origin'][1],p['texture_xy_top_origin'][0]])for p in vis),'named_features_safe':[{'source':p['source_frame'],'feature':p['feature_label_visual_proposal'],'uv_texel':p['texture_xy_top_origin'],'safe':p['conservative_head_edit_safe']}for p in r]};(out/'UV-footprint-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary)[:1800])
# retain compressed source provenance instead of bulky temporary float cache
with gzip.open(out/'source-triangle-owners.json.gz','wb')as f:f.write((out/'source-triangle-owners.json').read_bytes())
(out/'source-triangle-owners.json').unlink();(out/'packed-texture-linear-float.npy').unlink()
src=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/cape-wide-accommodation-v1/full-captain-wide-cape-camera12-packed.blend');(out/'source-binding.json').write_text(json.dumps({'source':str(src),'SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'render_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in out.glob('source-*.png')},'camera':{'fixed_elev':12,'ortho':2.7,'yaw':24.7024298},'source_unchanged_on_disk':True},indent=2)+'\n')

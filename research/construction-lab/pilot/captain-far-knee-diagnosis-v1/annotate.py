from pathlib import Path
from PIL import Image,ImageDraw
import json,collections,hashlib
out=Path(__file__).parent;v=json.loads((out/'joints-and-rays.json').read_text());sheet=Image.new('RGB',(1024,620),(30,34,38));summary=[]
for i,r in enumerate(v['records']):
 im=Image.open(out/f"source-{r['source']:03}.png").convert('RGBA');bg=Image.new('RGBA',im.size,(30,34,38,255));bg.alpha_composite(im);plain=bg.convert('RGB');label=plain.resize((512,512),Image.Resampling.NEAREST);d=ImageDraw.Draw(label)
 for k,q in r['joints'].items():
  x,y=[a*2 for a in q['pixel']];color=(90,220,255) if k.startswith('l') else (255,110,175);d.ellipse((x-3,y-3,x+3,y+3),fill=color);d.text((x+(8 if k.startswith('l') else -65),y-8),k,fill=color)
 label.save(out/f"annotated-source-{r['source']:03}.png");sheet.paste(label.resize((256,256),Image.Resampling.NEAREST),(i*256,0));sheet.paste(plain,(i*256,310));ds=ImageDraw.Draw(sheet);ds.text((i*256+6,264),f"source{r['source']} / cel{(r['source']-1)//2}",fill='white')
 for side in ['l','r']:
  rs=[q for q in r['rays'] if q['target']==side+'_knee'];counts=collections.Counter((q['object'],max(q['average_source_face_weights'],key=q['average_source_face_weights'].get) if q['average_source_face_weights'] else q['parent_bone'])for q in rs);summary.append({'source':r['source'],'knee':side,'projected_pixel':r['joints'][side+'_knee']['pixel'],'finite9x9_front_surface_counts':[{'object':o,'dominant_source_weight':w,'count':n}for(o,w),n in counts.items()]})
sheet.save(out/'all-four-joints-and-unmodified.png');(out/'ray-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
src=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/shield-support-lift-v1/B/full-captain-diagnostic.blend');ledger=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/full-captain-wide-craft-v8/retarget-joints-actual.json');contract=src.parent/'integration-contract.json';hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [src,ledger,contract]+list(out.glob('source-*.png'))};assert hashes[str(src)]=='f9cdc3671b182452cb4862589b7b1e7e7e5517d9eb21feacc69ecc79700b42ec';(out/'source-binding.json').write_text(json.dumps(hashes,indent=2)+'\n')

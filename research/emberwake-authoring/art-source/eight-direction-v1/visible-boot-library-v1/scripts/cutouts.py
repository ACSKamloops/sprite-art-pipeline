from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for d in ['cutouts','masks','witnesses']:(ROOT/d).mkdir(exist_ok=True)
scope=json.loads((ROOT/'SCOPES.json').read_text());sources=json.loads((ROOT/'INPUTS.json').read_text());records=[]
for item in scope['donors']:
    source=next(s for s in sources if s['actor']==item['actor']and s['view']==item['view']and s['phase']==item['phase'])
    src=np.array(Image.open(ROOT/source['copy']).convert('RGBA'));m=Image.new('L',(128,128));d=ImageDraw.Draw(m)
    for p in item['polygons']:d.polygon([tuple(x)for x in p],fill=255)
    for x,y in item['exclude_pixels']:d.point((x,y),fill=0)
    owner=np.array(m)>0;out=np.zeros_like(src);out[owner]=src[owner]
    png=ROOT/'cutouts'/f'{item["id"]}.png';Image.fromarray(out).save(png);m.save(ROOT/'masks'/f'{item["id"]}.png')
    ys,xs=np.where(owner&(src[:,:,3]>0));rgba=src[ys,xs];xy=np.stack([xs,ys],axis=-1).astype('int16')
    np.savez_compressed(ROOT/'witnesses'/f'{item["id"]}.npz',source_xy=xy,destination_xy=xy,RGBA=rgba)
    assert np.array_equal(out[owner],src[owner]);assert not out[~owner].any()
    records.append({**item,'full_source_cel':source['copy'],'actual_source':source['source'],'source_sha256':source['sha256'],'cutout':str(png.relative_to(ROOT)),'cutout_sha256':sha(png),'mask':f'masks/{item["id"]}.png','mask_sha256':sha(ROOT/'masks'/f'{item["id"]}.png'),'witness':f'witnesses/{item["id"]}.npz','witness_sha256':sha(ROOT/'witnesses'/f'{item["id"]}.npz'),'visible_source_pixels':len(xs),'geometry_transform':'identity; no recenter, fit, scale, rotation or normalization'})
(ROOT/'DONORS.json').write_text(json.dumps(records,indent=2)+'\n')
BG=(230,228,217,255)
for actor,view in dict.fromkeys((s['actor'],s['view'])for s in sources):
    sh=Image.new('RGBA',(216,138),BG)
    for row,phase in enumerate([0,2,6]):
        paths=[ROOT/'sources'/actor/view/f'{phase:02}.png']+[ROOT/'cutouts'/f'{actor}-{view}-{phase:02}-screen-{side}.png'for side in ['left','right']]
        for col,p in enumerate(paths):sh.alpha_composite(Image.open(p).convert('RGBA').crop((28,72,100,118)),(72*col,46*row))
    sh.resize((864,552),Image.Resampling.NEAREST).save(ROOT/'proof'/f'{actor}-{view}-source-and-donors-lower-4x.png')
    for name,size in [('native',128),('066',84)]:
        full=Image.new('RGBA',(3*size,3*(size+20)),BG);d=ImageDraw.Draw(full)
        for row,phase in enumerate([0,2,6]):
            paths=[ROOT/'sources'/actor/view/f'{phase:02}.png']+[ROOT/'cutouts'/f'{actor}-{view}-{phase:02}-screen-{side}.png'for side in ['left','right']]
            for col,p in enumerate(paths):
                im=Image.open(p).convert('RGBA').resize((size,size),Image.Resampling.NEAREST);full.alpha_composite(im,(size*col,(size+20)*row+20));d.text((size*col+2,(size+20)*row+2),f'{phase:02} {["source","screen-left","screen-right"][col]}',fill='black')
        full.save(ROOT/'proof'/f'{actor}-{view}-source-and-donors-{name}.png')
overlaps=[]
for s in sources:
    parts=[np.array(Image.open(ROOT/'cutouts'/f'{s["actor"]}-{s["view"]}-{s["phase"]:02}-screen-{side}.png').convert('RGBA'))[:,:,3]>0 for side in ['left','right']]
    if (parts[0]&parts[1]).any():overlaps.append({'source':s['copy'],'overlap_pixels':[[int(x),int(y)]for y,x in np.argwhere(parts[0]&parts[1])]})
(ROOT/'OVERLAPS.json').write_text(json.dumps(overlaps,indent=2)+'\n')
print('30 literal source cutouts; polygons and source texel witnesses retained. Overlapping visible owner sets:',len(overlaps))

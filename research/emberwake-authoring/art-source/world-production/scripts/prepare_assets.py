#!/usr/bin/env python3
"""Deterministic crops, fitting, and tile periodization of ImageGen artwork.

No model calls or replacement drawing. All source pixels are from preserved PNGs.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/assets'
records = []

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

# Hand-selected complete source silhouettes. Crop boundaries leave transparent
# margins around the alpha>32 connected-component bounds in the source sheet.
SPECS = [
    ('world/tree.png','worldprops-v1.png',(31,11,543,518),(192,256),(96,240),(285,494)),
    ('world/cottage.png','worldprops-v1.png',(585,46,1055,530),(320,320),(160,290),(824,508)),
    ('world/rock.png','worldprops-v1.png',(1139,231,1494,523),(128,96),(64,82),(1316,499)),
    ('world/shrine.png','worldprops-v1.png',(55,536,558,1002),(256,256),(128,230),(306,974)),
    ('world/ward.png','worldprops-v1.png',(698,583,1001,1002),(96,160),(48,144),(851,977)),
    ('world/ward_lit.png','ward-lit-v1.png',(0,0,1067,1475),(96,160),(48,144),(539,1387)),
    ('world/npc.png','worldprops-v1.png',(1169,635,1405,948),(128,128),(64,112),(1283,928)),
    ('enemies/scout.png','enemies-v1.png',(92,312,463,782),(128,128),(64,112),(284,763)),
    ('enemies/brute.png','enemies-v1.png',(593,197,1069,804),(160,160),(80,144),(860,769)),
    ('enemies/warden.png','enemies-v1.png',(1163,6,1863,824),(256,256),(128,224),(1511,790)),
]

for dest, src, box, size, pivot, source_foot in SPECS:
    original = Image.open(ROOT/'raw'/src).convert('RGBA')
    crop = original.crop(box)
    ax, ay = source_foot[0]-box[0], source_foot[1]-box[1]
    margin = 4
    scale = min((pivot[0]-margin)/ax,
                (size[0]-margin-pivot[0])/(crop.width-ax),
                (pivot[1]-margin)/ay,
                (size[1]-margin-pivot[1])/(crop.height-ay))
    fitted = crop.resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.LANCZOS)
    origin = (round(pivot[0]-ax*scale),round(pivot[1]-ay*scale))
    canvas = Image.new('RGBA',size,(0,0,0,0))
    canvas.alpha_composite(fitted,origin)
    path=OUT/dest
    path.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(path)
    records.append({'asset':str(path.relative_to(ROOT)),'sha256':sha(path),
        'source':'raw/'+src,'source_crop_xyxy':list(box),'source_foot_xy':list(source_foot),
        'canvas':list(size),'pivot':list(pivot),'scale':scale,'paste_xy':list(origin),
        'resample':'Pillow LANCZOS RGBA; original generated alpha retained',
        'alpha_extrema':list(canvas.getchannel('A').getextrema()),
        'alpha_bbox':list(canvas.getchannel('A').getbbox())})

# Keep the high resolution ward crop as the actual ImageGen edit reference.
Image.open(ROOT/'raw/worldprops-v1.png').crop((698,583,1001,1002)).save(ROOT/'references/ward-unlit-crop.png')

for name in ['grass','path','water']:
    src=ROOT/'raw'/f'{name}-v1.png'
    original=Image.open(src).convert('RGB')
    # A 384px region retains clear texture detail after reduction to a tile.
    x=(original.width-384)//2
    y=(original.height-384)//2
    crop=original.crop((x,y,x+384,y+384))
    tile=crop.resize((48,48),Image.Resampling.LANCZOS)
    a=np.asarray(tile,dtype=np.float64).copy()
    # Condition the outer six rows/columns symmetrically so both opposing
    # edges match exactly. Interior texture remains entirely source-derived.
    band=6
    for k in range(band):
        strength=(1-k/band)**2
        mean=(a[:,k,:]+a[:,-k-1,:])/2
        a[:,k,:]=(1-strength)*a[:,k,:]+strength*mean
        a[:,-k-1,:]=(1-strength)*a[:,-k-1,:]+strength*mean
    for k in range(band):
        strength=(1-k/band)**2
        mean=(a[k,:,:]+a[-k-1,:,:])/2
        a[k,:,:]=(1-strength)*a[k,:,:]+strength*mean
        a[-k-1,:,:]=(1-strength)*a[-k-1,:,:]+strength*mean
    result=Image.fromarray(np.uint8(np.clip(np.round(a),0,255)),'RGB').convert('RGBA')
    dest=OUT/'world'/f'{name}.png'
    result.save(dest)
    b=np.array(result)
    assert np.array_equal(b[0],b[-1]) and np.array_equal(b[:,0],b[:,-1])
    records.append({'asset':str(dest.relative_to(ROOT)),'sha256':sha(dest),
        'source':str(src.relative_to(ROOT)),'source_crop_xyxy':[x,y,x+384,y+384],
        'canvas':[48,48],'resample':'Pillow LANCZOS RGB; opaque RGBA output',
        'seam_processing':'6px paired opposing-edge blend, strength (1-k/6)^2; exact matching edge pixels',
        'edges_match':True,'alpha_extrema':[255,255]})

font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(font_path,16)
small=ImageFont.truetype(font_path,12)
sheet=Image.new('RGB',(1060,((len(SPECS)+2)//3)*280+60),(15,25,27))
d=ImageDraw.Draw(sheet)
d.text((18,10),'EMBERWAKE  |  WORLD & ENEMY ASSET PROOF',font=font,fill='#e4c28a')
for i,(dest,*_) in enumerate(SPECS):
    row,col=divmod(i,3)
    ox,oy=20+col*345,42+row*280
    for yy in range(0,245,16):
        for xx in range(0,325,16):
            color=(29,44,44) if (xx//16+yy//16)%2 else (38,53,51)
            d.rectangle((ox+xx,oy+yy,ox+xx+15,oy+yy+15),fill=color)
    im=Image.open(OUT/dest).convert('RGBA')
    if im.width>300 or im.height>235:
        im.thumbnail((300,235),Image.Resampling.NEAREST)
    sheet.paste(im,(ox+(325-im.width)//2,oy+245-im.height),im)
    d.text((ox+5,oy+248),dest,font=small,fill='#d4d9c4')
for i,name in enumerate(['grass','path','water']):
    im=Image.open(OUT/'world'/f'{name}.png').convert('RGB')
    proof=Image.new('RGB',(144,144))
    for yy in range(3):
        for xx in range(3): proof.paste(im,(xx*48,yy*48))
    proof=proof.resize((288,288),Image.Resampling.NEAREST)
    proof.save(ROOT/'proof'/f'{name}-3x3-repeat.png')
sheet.save(ROOT/'proof/contact-sheet.png')

title_src=ROOT/'raw/title-panorama-v2.png'
title=Image.open(title_src).convert('RGB')
title_final=ImageOps.fit(title,(960,540),method=Image.Resampling.LANCZOS,centering=(0.5,0.5))
title_dest=OUT/'world/title-panorama.png'
title_final.save(title_dest)
records.append({'asset':str(title_dest.relative_to(ROOT)),'sha256':sha(title_dest),
    'source':str(title_src.relative_to(ROOT)),'source_size':list(title.size),
    'canvas':[960,540],'resample':'Pillow ImageOps.fit center crop 16:9 and LANCZOS scale; opaque RGB',
    'quality_selection':'v2 selected for dark left title/menu area and village on right third; v1 preserved as unselected raw'})

raws=[]
for path in sorted((ROOT/'raw').glob('*.png')):
    im=Image.open(path)
    raws.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),
        'mode':im.mode,'size':list(im.size)})
sources={
  'tool':'Built-in tools.image_gen__imagegen; no local model, API CLI or public upload',
  'game':'Emberwake: The Hollow Bell',
  'style_reference':{'path':'references/approved-walk-frame00.png',
      'sha256':sha(ROOT/'references/approved-walk-frame00.png'),
      'role':'Palette, visual density and sprite medium; original hero not included in world or enemy outputs'},
  'prompts':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'text':p.read_text()}
      for p in sorted((ROOT/'prompts').glob('*.txt'))],
  'raw_outputs':raws,
  'generation_jobs':json.loads((ROOT/'IMAGEGEN-JOBS.json').read_text()),
  'assets':records,
  'processing_script':'scripts/prepare_assets.py',
  'processing_script_sha256':sha(ROOT/'scripts/prepare_assets.py'),
  'scope_disclosure':'Base enemy art is one original neutral sprite per kind. Additional authored step, windup and strike key poses, with matching neutral derivatives, are separately recorded in ENEMY-ANIMATION-SOURCES.json. Gameplay systems implement timing and movement; there are no fully inbetweened sprite cycles.',
  'quality_notes':['All isolated prop and enemy sprites were visually inspected in returned source sheets.',
      'All sources and original generated alpha preserved. Cutouts resampled once with LANCZOS onto exact-size transparent canvases.',
      'Ground tiles are ImageGen raster crops downsampled and edge-conditioned; no procedural replacement texture.'],
}
animation_manifest=ROOT/'ENEMY-ANIMATION-SOURCES.json'
if animation_manifest.exists():
    sources['additional_enemy_animation']={'manifest':str(animation_manifest.relative_to(ROOT)),
        'sha256':sha(animation_manifest),'frames':12,'authored_generated_poses':9,
        'matching_neutral_derivatives':3,
        'scope_disclosure':'Enemy poses include authored step, windup and strike keys; use optional matching neutral for consistent size. Original single sprites preserved.'}
back_manifest=ROOT/'ENEMY-BACK-SOURCES.json'
if back_manifest.exists():
    sources['additional_enemy_back_animation']={'manifest':str(back_manifest.relative_to(ROOT)),
        'sha256':sha(back_manifest),'accepted_frames':11,'rejected_candidates':1,
        'scope_disclosure':'Actual rear neutral/step/windup/strike for scout and brute; Warden rear neutral/step/windup only. Rear Warden strike rejected for hand swap. Whole-bank body compensation multipliers are in this manifest.'}
(ROOT/'ART-SOURCES.json').write_text(json.dumps(sources,indent=2)+'\n')
print(json.dumps({'asset_count':len(records),'manifest':str(ROOT/'ART-SOURCES.json'),
 'contact_sheet':str(ROOT/'proof/contact-sheet.png')},indent=2))

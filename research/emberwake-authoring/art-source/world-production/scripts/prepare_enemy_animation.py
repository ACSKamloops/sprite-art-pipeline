#!/usr/bin/env python3
"""Extract nine generated poses with a shared scale per character, no pose fitting."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'raw/enemy-animation-v1.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(SOURCE).convert('RGBA')
pixels=np.array(im)
labels,n=ndimage.label(pixels[:,:,3]>32)
objects=ndimage.find_objects(labels)
large=[]
for i,s in enumerate(objects):
    if int((labels[s]==i+1).sum())>1000:
        large.append((i+1,s))
assert len(large)==9
# Assign anti-aliased edge pixels to the nearest one of the nine complete
# alpha components. This separates weapons that cross a nominal atlas row.
seeds=np.zeros(labels.shape,dtype=np.int16)
for k,(label,_) in enumerate(large):seeds[labels==label]=k+1
distance,indices=ndimage.distance_transform_edt(seeds==0,return_indices=True)
nearest=seeds[tuple(indices)]

ROWS={
 'scout':{'size':[128,128],'pivot':[64,112],'scale':0.29,
          'step_body_top':62,'step_source_foot_y':384,'original_body_top':6,
          'poses':{'step':([242,384],1),'windup':([624,382],0),'strike':([1016,365],2)}},
 'brute':{'size':[160,160],'pivot':[80,144],'scale':0.325,
          'step_body_top':420,'step_source_foot_y':785,'original_body_top':6,
          'poses':{'step':([236,785],4),'windup':([616,784],3),'strike':([1000,756],5)}},
 'warden':{'size':[256,256],'pivot':[128,224],'scale':0.49,
           'step_body_top':814,'step_source_foot_y':1204,'original_body_top':6,
           'poses':{'step':([224,1204],7),'windup':([607,1204],6),'strike':([1001,1204],8)}},
}
records=[]
for kind,row in ROWS.items():
    folder=ROOT/'output/enemies-animation'/kind
    folder.mkdir(parents=True,exist_ok=True)
    for pose,(foot,component) in row['poses'].items():
        _,s=large[component]
        box=[max(0,s[1].start-4),max(0,s[0].start-4),min(im.width,s[1].stop+4),min(im.height,s[0].stop+4)]
        isolated=pixels.copy()
        isolated[:,:,3]=np.where((nearest==component+1)&(distance<=4),isolated[:,:,3],0)
        crop=Image.fromarray(isolated,'RGBA').crop(box)
        scale=row['scale']
        resized=crop.resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.LANCZOS)
        offset=[round(row['pivot'][0]-(foot[0]-box[0])*scale),round(row['pivot'][1]-(foot[1]-box[1])*scale)]
        # Complete silhouettes must fit without clipping at the destination.
        a=np.array(resized.getchannel('A'))
        ys,xs=np.nonzero(a>32)
        assert xs.min()+offset[0]>=0 and xs.max()+offset[0]<row['size'][0],(kind,pose,'x clip')
        assert ys.min()+offset[1]>=0 and ys.max()+offset[1]<row['size'][1],(kind,pose,'y clip')
        canvas=Image.new('RGBA',row['size'])
        canvas.alpha_composite(resized,offset)
        dest=folder/f'{pose}.png';canvas.save(dest)
        records.append({'asset':str(dest.relative_to(ROOT)),'sha256':sha(dest),'character':kind,'pose':pose,
            'canvas':row['size'],'pivot':row['pivot'],'source':str(SOURCE.relative_to(ROOT)),
            'source_component_index':component,'source_crop_xyxy':box,'source_foot_xy':foot,
            'uniform_row_scale':scale,'paste_xy':offset,'resample':'Pillow LANCZOS RGBA',
            'alpha_isolation':'nearest alpha>32 large component, retaining original alpha within 4px edge fringe',
            'alpha_bbox':list(canvas.getchannel('A').getbbox()),'complete_silhouette_verified':True})
    # Additional compatible neutral, leaving the original asset untouched.
    original=ROOT/'output/assets/enemies'/f'{kind}.png'
    neutral=Image.open(original).convert('RGBA')
    factor=(row['step_source_foot_y']-row['step_body_top'])*row['scale']/(row['pivot'][1]-row['original_body_top'])
    fitted=neutral.resize((round(neutral.width*factor),round(neutral.height*factor)),Image.Resampling.LANCZOS)
    offset=[round(row['pivot'][0]*(1-factor)),round(row['pivot'][1]*(1-factor))]
    canvas=Image.new('RGBA',row['size']);canvas.alpha_composite(fitted,offset)
    dest=folder/'neutral.png';canvas.save(dest)
    row['neutral_relative_scale']=factor
    records.append({'asset':str(dest.relative_to(ROOT)),'sha256':sha(dest),'character':kind,'pose':'neutral',
        'canvas':row['size'],'pivot':row['pivot'],'source':str(original.relative_to(ROOT)),
        'source_sha256':sha(original),'relative_scale':factor,'paste_xy':offset,
        'resample':'Pillow LANCZOS RGBA','purpose':'Optional matching body scale for new poses; original unchanged'})

font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
proof=Image.new('RGB',(1120,900),(14,24,27));draw=ImageDraw.Draw(proof)
draw.text((15,10),'EMBERWAKE ENEMY KEY POSES | same per-row scale; foot registration',font=font,fill='#e7c38b')
for r,kind in enumerate(ROWS):
    for c,pose in enumerate(['neutral','step','windup','strike']):
        ox,oy=15+c*275,45+r*280
        for yy in range(0,245,16):
            for xx in range(0,260,16):
                draw.rectangle((ox+xx,oy+yy,ox+xx+15,oy+yy+15),fill=(30,44,43) if (xx//16+yy//16)%2 else (40,53,50))
        frame=Image.open(ROOT/'output/enemies-animation'/kind/f'{pose}.png')
        px=ox+(260-frame.width)//2;py=oy+245-frame.height
        proof.paste(frame,(px,py),frame)
        pivot=ROWS[kind]['pivot'];fx=px+pivot[0];fy=py+pivot[1]
        draw.line((fx-5,fy,fx+5,fy),fill='#db9d65');draw.line((fx,fy-3,fx,fy+3),fill='#db9d65')
        draw.text((ox+4,oy+249),f'{kind} / {pose}',font=font,fill='#d7dfc8')
proof.save(ROOT/'proof/enemy-animation-keyposes.png')

manifest={'tool':'Built-in tools.image_gen__imagegen, single generation call for nine authored poses',
    'generation_job':json.loads((ROOT/'ENEMY-ANIMATION-JOB.json').read_text()),
    'prompt_path':'prompts/enemy-animation-v1.txt','prompt':(ROOT/'prompts/enemy-animation-v1.txt').read_text(),
    'source_atlas':{'path':str(SOURCE.relative_to(ROOT)),'sha256':sha(SOURCE),'size':list(im.size),'mode':im.mode},
    'reference_authority':[{'path':f'output/assets/enemies/{k}.png','sha256':sha(ROOT/f'output/assets/enemies/{k}.png')} for k in ROWS],
    'registration':ROWS,'assets':records,'script':'scripts/prepare_enemy_animation.py',
    'script_sha256':sha(Path(__file__)),
    'disclosure':'Three newly generated authored key poses per enemy, not a fully inbetweened walk/attack cycle. Each row has one fixed scale and manual source-foot translations. The original near-full-canvas neutral art lacked room for raised weapons, so optional neutral.png variants match new 12-14 percent smaller body heights. Original assets are unchanged.',
    'inspection':'All nine source poses reviewed: scout retains leather/hood/mask/curved dagger; brute retains jade plate/closed helmet/spiked iron mace; Warden retains stone/moss/branch crown/runes/turquoise heart/stone pillar club. No weapon substitutions or flesh/metal material substitutions found.'}
(ROOT/'ENEMY-ANIMATION-SOURCES.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'frames':len(records),'manifest':'ENEMY-ANIMATION-SOURCES.json','proof':'proof/enemy-animation-keyposes.png'},indent=2))

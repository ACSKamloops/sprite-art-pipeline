#!/usr/bin/env python3
"""Extract accepted rear poses; keep handedness failures outside selected output."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
MAIN='raw/enemy-back-animation-v1.png'
REPAIR='raw/enemy-back-handedness-repair-v1.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cache={}
def component(src,label):
    if src not in cache:
        im=Image.open(ROOT/src).convert('RGBA');p=np.array(im)
        labels,n=ndimage.label(p[:,:,3]>32)
        large=np.zeros(labels.shape,dtype=np.int16)
        for i,s in enumerate(ndimage.find_objects(labels)):
            if int((labels[s]==i+1).sum())>1000:large[labels==i+1]=i+1
        distance,ix=ndimage.distance_transform_edt(large==0,return_indices=True)
        nearest=large[tuple(ix)]
        cache[src]=(p,labels,distance,nearest)
    p,labels,distance,nearest=cache[src]
    yy,xx=np.nonzero(labels==label)
    box=[max(0,int(xx.min())-4),max(0,int(yy.min())-4),min(p.shape[1],int(xx.max())+5),min(p.shape[0],int(yy.max())+5)]
    cut=p[box[1]:box[3],box[0]:box[2]].copy()
    good=(nearest[box[1]:box[3],box[0]:box[2]]==label)&(distance[box[1]:box[3],box[0]:box[2]]<=4)
    cut[:,:,3]=np.where(good,cut[:,:,3],0)
    return Image.fromarray(cut,'RGBA'),box

ROWS={
 'scout':{'size':[128,128],'pivot':[64,112],'canonical_row_scale':0.345,
     'back_body_top':51,'canonical_source_foot_y':323,'front_neutral_body_top':18,
     'poses':{'back_neutral':(MAIN,3,[223,323],1.0),'back_step':(MAIN,4,[568,326],1.0),
              'back_windup':(MAIN,1,[890,327],1.0),'back_strike':(MAIN,2,[1252,323],1.0)}},
 'brute':{'size':[160,160],'pivot':[80,144],'canonical_row_scale':0.36,
     'back_body_top':358,'canonical_source_foot_y':656,'front_neutral_body_top':25,
     'poses':{'back_neutral':(MAIN,7,[218,656],1.0),'back_step':(MAIN,8,[577,662],1.0),
              'back_windup':(REPAIR,1,[426,813],298/613),
              'back_strike':(MAIN,6,[1241,661],1.0)}},
 'warden':{'size':[256,256],'pivot':[128,224],'canonical_row_scale':0.514,
     'back_body_top':683,'canonical_source_foot_y':1055,'front_neutral_body_top':33,
     'poses':{'back_neutral':(MAIN,11,[218,1055],1.0),'back_step':(MAIN,12,[570,1053],1.0),
              'back_windup':(MAIN,10,[899,1061],1.0)},
     'rejected_pose':('back_strike',MAIN,9,[1250,1050],1.0)},
}
records=[]
for kind,row in ROWS.items():
    front_height=row['pivot'][1]-row['front_neutral_body_top']
    canonical_body_height=row['canonical_source_foot_y']-row['back_body_top']
    back_height=canonical_body_height*row['canonical_row_scale']
    row['canonical_body_height_px']=canonical_body_height
    row['expected_front_body_height_px']=front_height
    row['expected_back_body_height_px']=back_height
    row['recommended_whole_back_bank_scale_multiplier']=front_height/back_height
    plans=[(pose,*v,True) for pose,v in row['poses'].items()]
    if 'rejected_pose' in row:plans.append((*row['rejected_pose'],False))
    for pose,src,label,foot,native_to_canonical,valid in plans:
        cut,box=component(src,label)
        scale=row['canonical_row_scale']*native_to_canonical
        fitted=cut.resize((round(cut.width*scale),round(cut.height*scale)),Image.Resampling.LANCZOS)
        offset=[round(row['pivot'][0]-(foot[0]-box[0])*scale),round(row['pivot'][1]-(foot[1]-box[1])*scale)]
        a=np.array(fitted.getchannel('A'));ys,xs=np.nonzero(a>32)
        assert xs.min()+offset[0]>=0 and xs.max()+offset[0]<row['size'][0],(kind,pose,'x clipped')
        assert ys.min()+offset[1]>=0 and ys.max()+offset[1]<row['size'][1],(kind,pose,'y clipped')
        canvas=Image.new('RGBA',row['size']);canvas.alpha_composite(fitted,offset)
        folder=ROOT/('output/enemies-animation' if valid else 'output/rejected-enemy-animation')/kind
        folder.mkdir(parents=True,exist_ok=True);dest=folder/f'{pose}.png';canvas.save(dest)
        records.append({'asset':str(dest.relative_to(ROOT)),'sha256':sha(dest),'character':kind,'pose':pose,
            'valid_for_integration':valid,'rejection_reason':None if valid else 'Warden club is incorrectly held by anatomical right arm in this rear strike.',
            'canvas':row['size'],'pivot':row['pivot'],'source':src,'source_component_label':label,
            'source_crop_xyxy':box,'source_foot_xy':foot,'canonical_row_scale':row['canonical_row_scale'],
            'native_to_canonical_body_scale':native_to_canonical,'final_native_scale':scale,'paste_xy':offset,
            'resample':'Pillow LANCZOS RGBA once from native source',
            'alpha_isolation':'nearest alpha>32 connected component, retaining generated alpha within 4px fringe',
            'whole_back_bank_scale_multiplier':row['recommended_whole_back_bank_scale_multiplier'],
            'complete_silhouette_verified':True,
            'anatomical_weapon_hand':'right' if kind!='warden' else ('left' if valid else 'right - rejected')})

font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
sheet=Image.new('RGB',(1120,900),(14,24,27));d=ImageDraw.Draw(sheet)
d.text((15,10),'EMBERWAKE REAR KEY POSES | 11 ACCEPTED; WARDEN STRIKE REJECTED FOR HAND SWAP',font=font,fill='#e7c38b')
for r,kind in enumerate(ROWS):
    for c,pose in enumerate(['back_neutral','back_step','back_windup','back_strike']):
        ox,oy=15+c*275,45+r*280
        for yy in range(0,245,16):
            for xx in range(0,260,16):d.rectangle((ox+xx,oy+yy,ox+xx+15,oy+yy+15),fill=(30,44,43) if (xx//16+yy//16)%2 else (40,53,50))
        rejected=kind=='warden' and pose=='back_strike'
        frame=Image.open(ROOT/('output/rejected-enemy-animation' if rejected else 'output/enemies-animation')/kind/f'{pose}.png')
        px=ox+(260-frame.width)//2;py=oy+245-frame.height;sheet.paste(frame,(px,py),frame)
        fx=px+ROWS[kind]['pivot'][0];fy=py+ROWS[kind]['pivot'][1]
        d.line((fx-5,fy,fx+5,fy),fill='#db9d65');d.line((fx,fy-3,fx,fy+3),fill='#db9d65')
        d.text((ox+4,oy+249),f'{kind} / {pose}'+(' REJECTED' if rejected else ''),font=font,fill='#f2766c' if rejected else '#d7dfc8')
sheet.save(ROOT/'proof/enemy-back-keyposes.png')

jobs=json.loads((ROOT/'ENEMY-BACK-JOBS.json').read_text())
manifest={'tool':'Built-in tools.image_gen__imagegen','generation_jobs':jobs,
    'calls':{'initial_12_pose_atlas':1,'genuine_handedness_repairs':2,'further_generation':'frozen by root instruction'},
    'prompts':[{'path':j['prompt'],'sha256':sha(ROOT/j['prompt']),'text':(ROOT/j['prompt']).read_text()} for j in jobs],
    'raw_outputs':[{'path':j['raw'],'sha256':sha(ROOT/j['raw']),'size':list(Image.open(ROOT/j['raw']).size),'mode':Image.open(ROOT/j['raw']).mode} for j in jobs],
    'authority_references':[{'path':f'output/assets/enemies/{k}.png','sha256':sha(ROOT/f'output/assets/enemies/{k}.png')} for k in ROWS],
    'front_pose_atlas_reference':{'path':'raw/enemy-animation-v1.png','sha256':sha(ROOT/'raw/enemy-animation-v1.png')},
    'derived_repair_reference':{'path':'references/warden-back-left-windup.png','sha256':sha(ROOT/'references/warden-back-left-windup.png'),
        'source':MAIN,'alpha_component_label':10,'isolation':'alpha>32 component dilated 4px','crop_xyxy':[753,668,1045,1075]},
    'registration':ROWS,'assets':records,'script':'scripts/prepare_enemy_back_animation.py',
    'script_sha256':sha(Path(__file__)),
    'direction':'Actual authored rear/upper-right view. Game may mirror whole front/back banks for left quadrants as an explicitly disclosed symmetry. No face, eyes, front chest or turquoise Warden heart visible in accepted rear poses.',
    'selection':'11 accepted back frames; Warden back_strike omitted from selected directory. One rejected candidate exists separately. Both repair candidates that failed Warden handedness remain in raw sources.',
    'body_scale_note':'One canonical body scale per enemy row; no individual pose fitting. Separate-resolution accepted brute repair normalized by explicit head-to-feet body landmarks (298/613), then shared row scale. Exact listed compensation multiplier can be applied to the whole back sprite bank about the foot pivot to match front-animation body height.',
    'fallback_note':'Warden has valid back_neutral/back_step/back_windup. Use phase FX and return to neutral for rear strike rather than claiming rejected image is left-handed.'}
(ROOT/'ENEMY-BACK-SOURCES.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'accepted':11,'rejected':1,'multipliers':{k:r['recommended_whole_back_bank_scale_multiplier'] for k,r in ROWS.items()},'proof':'proof/enemy-back-keyposes.png'},indent=2))

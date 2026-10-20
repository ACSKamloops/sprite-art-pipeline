#!/usr/bin/env python3
"""Bounded vertical-only, two-limb low-step trial. All writes stay in this folder."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
NAMES={112:'south_A',113:'south_B',114:'north_A',115:'north_B'}
VARIANTS={'moderate':{'support':-5,'swing':7},'strong':{'support':-8,'swing':10}}
specmod=importlib.util.spec_from_file_location('source_warp',ROOT/'scripts/source_warp.py')
warp=importlib.util.module_from_spec(specmod);specmod.loader.exec_module(warp)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def writejson(path,data):path.write_text(json.dumps(data,indent=2)+'\n')
def rgba(path):return np.array(Image.open(path).convert('RGBA'))
def save(path,a):Image.fromarray(a).save(path)
def bounds(mask):
    yy,xx=np.where(mask)
    return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None

def run():
    zero=np.zeros((128,128,4),np.uint8);save(ROOT/'inputs/zero.png',zero)
    yy,xx=np.indices((128,128))
    roi=(xx>=45)&(xx<87)&(yy>=81)&(yy<121)
    save(ROOT/'masks/roi.png',(roi*255).astype(np.uint8))
    baselines={}; masks={}; shapes={}; results={}; receipt={
        'scope':'One bounded mathematical trial; no generation; no game or frozen-parent files written.',
        'sole_definition':'Inclusive maximum y among boot-owned source pixels with alpha >127, translated rigidly.',
        'mask_bounds_half_open':[45,81,87,121], 'horizontal_map':'source_x == output_x everywhere; no x64 centering',
        'hip_seam':'y<=81 sampled at identity; rows y<81 restored exactly from current atlas cell',
        'variants':VARIANTS,'frames':{}}
    for fid,name in NAMES.items():
        source=rgba(ROOT/'inputs/frames'/f'{fid:03}.png');baselines[name]=source
        d=ROOT/'masks'/name;d.mkdir(exist_ok=True)
        # Explicit disjoint semantic ownership at the leg gap. Below the old
        # swing boot all remaining source paint belongs to the support leg.
        swing=roi&(yy<95)&((xx<62) if name.endswith('A') else (xx>=66))
        support=roi&~swing
        shapes[name]={};masks[name]={'support':support,'swing':swing}
        record={'frame_id':fid,'source_png':f'inputs/frames/{fid:03}.png','source_sha256':sha(ROOT/'inputs/frames'/f'{fid:03}.png'),'source_legs':{},'variants':{}}
        for leg,ownership in masks[name].items():
            start=90 if leg=='support' else (84 if name.startswith('south') else 82)
            end=116 if leg=='support' else 96
            layer=zero.copy();layer[ownership]=source[ownership]
            save(d/(leg+'-source-layer.png'),layer)
            save(d/(leg+'-leg-mask.png'),(ownership*255).astype(np.uint8))
            boot=ownership&(yy>=start)&(yy<end)
            save(d/(leg+'-boot-mask.png'),(boot*255).astype(np.uint8))
            painted=boot&(source[:,:,3]>127)
            shapes[name][leg]={'start':start,'end':end,'boot':boot,'layer':layer,
                'source_sole':int(yy[painted].max())}
            record['source_legs'][leg]={'ownership_rule':('ROI except swing' if leg=='support' else ('ROI & y<95 & x<62' if name.endswith('A') else 'ROI & y<95 & x>=66')),
                'boot_plateau_y_half_open':[start,end], 'painted_boot_bbox_alpha_gt_127':bounds(painted),
                'source_sole_alpha_gt_127':int(yy[painted].max()),'boot_rgba_pixels_alpha_gt_0':int((boot&(source[:,:,3]>0)).sum())}
        for variant,offsets in VARIANTS.items():
            legresults={};legreports={};targetboots={}
            for leg,dy in offsets.items():
                shape=shapes[name][leg];start,end=shape['start'],shape['end']
                out=ROOT/'maps'/variant/name/leg;out.mkdir(parents=True,exist_ok=True)
                src=[];dst=[]
                for y in [0,80,81,start,end,121,127]:
                    for x in [0,45,87,127]:
                        src.append([x,y]);dst.append([x,y+(dy if start<=y<=end and 45<=x<=87 else 0)])
                body=ROOT/'inputs/zero.png';donor=ROOT/'masks'/name/(leg+'-source-layer.png')
                relbody=os.path.relpath(body,out);reldonor=os.path.relpath(donor,out)
                spec={'schema':'imagegen-source-warp/v1','body':relbody,'donor':reldonor,'canvas':[128,128],
                    'files_sha256':{relbody:sha(body),reldonor:sha(donor)}, 'donor_roi':[45,81,87,121],
                    'source_points':src,'target_points':dst,'rigid_rect':{'source':[45,start,87,end],'target':[45,start+dy,87,end+dy]},
                    'purpose':'Vertical boot plateau with continuous attached upper-leg warp; separate semantic leg layer, no horizontal movement.'}
                owner=roi.astype(np.uint8)
                sourcexy,tris,ratios=warp.make_map(spec,owner)
                assert np.array_equal(sourcexy[:,:,0],xx)
                a,edits,changed=warp.render(spec,zero,shape['layer'],owner,sourcexy,owner)
                assert np.array_equal(a[start+dy:end+dy,45:87],shape['layer'][start:end,45:87])
                save(out/'layer.png',a)
                np.savez_compressed(out/'source-map.npz',source_xy=sourcexy,source_kind=owner)
                spec.update({'triangles':tris.tolist(),'map':'source-map.npz','expected':'layer.png'})
                writejson(out/'spec.json',spec)
                boot_source=shape['boot']&(shape['layer'][:,:,3]>0)
                targetboot=np.zeros((128,128),bool)
                by,bx=np.where(boot_source);targetboot[by+dy,bx]=True
                targetboots[leg]=targetboot
                legresults[leg]=a
                legreports[leg]={'translation':[0,dy],'source_sole':shape['source_sole'],'target_sole':shape['source_sole']+dy,
                    'complete_boot_rectangle_exact_rgba':True,'horizontal_source_map_exact_identity':True,
                    'map':str((out/'source-map.npz').relative_to(ROOT)),'spec':str((out/'spec.json').relative_to(ROOT)),
                    'triangle_area_ratio_range':ratios,'layer_sha256':sha(out/'layer.png')}
            # Separate legs meet without alpha blending. Where translucent fringes
            # overlap, front-view swing is in front; rear-view support is in front.
            result=source.copy();result[roi]=0
            back,front=('support','swing') if name.startswith('south') else ('swing','support')
            for leg in [back,front]:
                visible=legresults[leg][:,:,3]>0
                result[visible&roi]=legresults[leg][visible&roi]
            overlap=(legresults['support'][:,:,3]>0)&(legresults['swing'][:,:,3]>0)
            opaqueoverlap=(legresults['support'][:,:,3]>127)&(legresults['swing'][:,:,3]>127)
            assert np.array_equal(result[~roi],source[~roi])
            assert np.array_equal(result[:81],source[:81])
            assert np.array_equal(result[81],source[81])
            # Report exact boot preservation after the two layers meet, too.
            for leg in ['support','swing']:
                bm=targetboots[leg]
                legreports[leg]['final_visible_boot_pixels_exact_rgba']=bool(np.array_equal(result[bm],legresults[leg][bm]))
                legreports[leg]['final_visible_boot_pixel_mismatches']=int(np.any(result[bm]!=legresults[leg][bm],axis=1).sum())
                measured=bm&(result[:,:,3]>127)
                legreports[leg]['actual_final_sole_alpha_gt_127']=int(yy[measured].max())
            save(ROOT/'candidates'/variant/(name+'.png'),result)
            results[(variant,name)]=result
            record['variants'][variant]={'candidate':f'candidates/{variant}/{name}.png','sha256':sha(ROOT/'candidates'/variant/(name+'.png')),
                'outside_roi_exact_rgba':True,'fixed_body_y_lt_81_exact_rgba':True,'hip_seam_row81_exact_rgba':True,
                'changed_rgba_pixels':int(np.any(result!=source,axis=2).sum()),
                'overlap_alpha_gt_0_pixels':int(overlap.sum()),'overlap_alpha_gt_127_pixels':int(opaqueoverlap.sum()),'legs':legreports}
        receipt['frames'][name]=record
    writejson(ROOT/'receipt.json',receipt)
    # Draw original ownership masks over the input at 4x. Filled color is guide
    # only; original source layers and separate binary masks are retained above.
    guide=Image.new('RGB',(1024,560),(42,46,54));gd=ImageDraw.Draw(guide)
    for i,(fid,name) in enumerate(NAMES.items()):
        a=baselines[name].copy()
        for leg,color in [('support',np.array([65,245,105])),('swing',np.array([245,70,180]))]:
            m=masks[name][leg]&(a[:,:,3]>0)
            a[m,:3]=(a[m,:3].astype(float)*.45+color*.55).astype(np.uint8)
        im=Image.fromarray(a).resize((256,256),Image.Resampling.NEAREST)
        guide.paste(im,(i*256,20),im);gd.text((i*256+8,4),name+' green support / pink swing',fill='white')
        boot=np.zeros((128,128,4),np.uint8)
        for leg,color in [('support',[70,255,100,255]),('swing',[255,70,180,255])]:
            boot[shapes[name][leg]['boot']& (baselines[name][:,:,3]>0)]=color
        bi=Image.fromarray(boot).resize((256,256),Image.Resampling.NEAREST)
        guide.paste(bi,(i*256,298),bi);gd.text((i*256+8,282),name+' complete boot paint masks',fill='white')
    guide.save(ROOT/'proof/source-masks-2x.png')
    manifest=json.loads((ROOT/'inputs/animations.json').read_text())
    chronology={}
    for view in ['south','north']:
        anim=manifest['animations'][view+'_walk'];chronology[view]=anim
        sheet=Image.new('RGB',(2048,840),(42,46,54));d=ImageDraw.Draw(sheet)
        for row,variant in enumerate(['current','moderate','strong']):
            for col,fid in enumerate(anim['frames']):
                a=results[(variant,NAMES[fid])] if variant!='current' and fid in NAMES else rgba(ROOT/'inputs/frames'/f'{fid:03}.png')
                im=Image.fromarray(a).resize((256,256),Image.Resampling.NEAREST)
                x=col*256;y=row*280+20
                sheet.paste(im,(x,y),im)
                d.text((x+5,y-16),f'{variant} {col+1}/8 id{fid} 9/160s',fill='white')
        sheet.save(ROOT/'proof'/(view+'-8-key-chronology-2x.png'))
    writejson(ROOT/'chronology.json',{'views':chronology,'hold_rational_seconds':[9,160],'cycle_rational_seconds':[9,20],
        'replaced_only_frame_ids':NAMES,'timing_changed':False,'pixel_scale_in_proof':2})
    # Compact isolated comparison is secondary to the chronology sheets.
    proof=Image.new('RGB',(1024,840),(42,46,54));d=ImageDraw.Draw(proof)
    for row,variant in enumerate(['current','moderate','strong']):
        for col,(fid,name) in enumerate(NAMES.items()):
            a=baselines[name] if variant=='current' else results[(variant,name)]
            im=Image.fromarray(a).resize((256,256),Image.Resampling.NEAREST)
            proof.paste(im,(col*256,row*280+20),im)
            d.text((col*256+6,row*280+4),name+' '+variant,fill='white')
    proof.save(ROOT/'proof/passing-comparison-2x.png')
    print(json.dumps({name:{v:{'support_sole':r['legs']['support']['target_sole'],'swing_sole':r['legs']['swing']['target_sole'],
        'boot_mismatches':{k:x['final_visible_boot_pixel_mismatches'] for k,x in r['legs'].items()},'overlap':r['overlap_alpha_gt_0_pixels']}
        for v,r in f['variants'].items()} for name,f in receipt['frames'].items()},indent=2))

if __name__=='__main__':run()

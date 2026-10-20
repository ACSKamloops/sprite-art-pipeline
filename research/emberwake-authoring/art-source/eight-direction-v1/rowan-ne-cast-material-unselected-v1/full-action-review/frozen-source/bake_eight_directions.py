#!/usr/bin/env python3
"""Replay diagonal paint registration and append to frozen cardinal banks.

No model calls. Uniform sheet/row transforms; connected source ownership keeps
overflowing toes/fists with their body instead of clipping at nominal cells.
Output must be fresh. Runtime installation is a separate explicit operation.
"""
from pathlib import Path
import argparse, hashlib, json, math
import numpy as np
from PIL import Image, ImageOps, ImageDraw
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'art-source/eight-direction-v1'
DIRECTIONS=['south','southeast','east','northeast','north','northwest','west','southwest']
ACTIONS={
 'idle':([22,23],[.58,.58],True),
 'walk':(list(range(8)),[.05625]*8,True),
 'attack':([8,9,10,11,12,13,14,22],[.06,.07,.055,.055,.065,.035,.035,.035],False),
 'cast':([22,17,18,19,20,22],[.06,.08,.10,.08,.08,.10],False),
 'hurt':([24,25,22],[.09,.10,.10],False),
 'dodge':([27,28,29,30,22],[.045,.105,.055,.0275,.0275],False)}
DEFAULT_HANDS={'rowan':{'south':[99,72],'east':[102,57],'north':[93,49],'west':[24,60]},
 'lyra':{'south':[99,72],'east':[95,58],'north':[94,57],'west':[34,58]},
 'brann':{'south':[101,72],'east':[96,52],'north':[96,40],'west':[32,52]}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba_sha(im):return hashlib.sha256(im.tobytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n')
def source_owners(image):
    """Identify 32 disjoint bodies globally, retaining connected overflow.

    Alpha islands within 3px of exactly one main body belong to that body.
    Other islands are reported, never silently attributed. Original input is
    retained; these masks are literal extraction ownership, not anatomy repair.
    """
    a=np.array(image); labels,n=ndimage.label(a[:,:,3]>=24)
    counts=np.bincount(labels.ravel()); objects=ndimage.find_objects(labels)
    main=[i for i in range(1,n+1) if counts[i]>4000]
    assert len(main)==32, f'Expected32 separate bodies, got{len(main)}'
    assigned={}; masks={}; receipts={}; distances=[]
    for k in main:
        ys,xs=objects[k-1]; cx=(xs.start+xs.stop)/2; cy=(ys.start+ys.stop)/2
        index=int(cy//256)*8+int(cx//256)
        assert index not in assigned, f'Connected/overlapping bodies in cell{index}'
        assigned[index]=k
        mask=labels==k
        masks[index]=mask
        distances.append((index,ndimage.distance_transform_edt(~mask)))
        receipts[index]={'main_label':k,'main_area':int(counts[k]),
           'main_bbox':[xs.start,ys.start,xs.stop,ys.stop],'additional_components':[]}
    assert sorted(assigned)==list(range(32))
    orphans=[]
    for k in range(1,n+1):
        if k in main:continue
        ys,xs=objects[k-1]
        choices=[(float(d[ys,xs][labels[ys,xs]==k].min()),i) for i,d in distances]
        distance,index=min(choices)
        if distance<=3:
            masks[index]|=labels==k
            receipts[index]['additional_components'].append({'label':k,'area':int(counts[k]),'distance':distance})
        else:orphans.append({'label':k,'area':int(counts[k]),'bbox':[xs.start,ys.start,xs.stop,ys.stop],'nearest_distance':distance})
    for i in masks:receipts[i]['ownership_sha256']=hashlib.sha256(masks[i].tobytes()).hexdigest()
    return a,masks,{'cells':receipts,'unassigned_components':orphans,
       'alpha_rule':'Below24 zero; above245 opaque; hiddenRGB zero. Islands within3px nearest body retained.'}
def registered_bank(path,settings,destination):
    im=Image.open(path).convert('RGBA').resize((2048,1024),Image.Resampling.NEAREST)
    a,masks,receipt=source_owners(im); bank=[]
    scale=settings['scale']
    for i in range(32):
        pixels=np.zeros_like(a);pixels[masks[i]]=a[masks[i]]
        pixels[:,:,3][pixels[:,:,3]>245]=255
        pixels[pixels[:,:,3]<24]=0
        ax,ay=settings['row_anchors'][i//8]
        sx=i%8*256+ax;sy=i//8*256+ay
        cel=Image.fromarray(pixels).transform((128,128),Image.Transform.AFFINE,
          (1/scale,0,sx-64/scale,0,1/scale,sy-112/scale),Image.Resampling.NEAREST)
        bbox=cel.getbbox()
        assert bbox and bbox[0]>0 and bbox[1]>0 and bbox[2]<128 and bbox[3]<128,(path.name,i,bbox)
        bank.append(cel);cel.save(destination/f'{i:02d}.png')
        receipt['cells'][i].update({'rgba_sha256':rgba_sha(cel),'native_bbox':bbox})
    return bank,receipt
def mirror(cel):
    out=Image.new('RGBA',cel.size);out.alpha_composite(ImageOps.mirror(cel),(1,0));return out
def proof(bank,path):
    im=Image.new('RGBA',(1024,512))
    for i,cel in enumerate(bank):im.alpha_composite(cel,(i%8*128,i//8*128))
    im.save(path)
def build(out,config,production=False):
    assert not out.exists(), 'Fresh output directory required'
    out.mkdir(parents=True)
    baseline=json.loads((BASE/'BASELINE.json').read_text())
    receipt={'schema':'emberwake-eight-directions-replay/v1','config_sha256':sha(config),'baker_sha256':sha(Path(__file__)),
      'directions':DIRECTIONS,'conditional_mirrors':{'southwest':'southeast','northwest':'northeast'},
      'scope':'Registration candidate; art scores and runtime acceptance separate.','actors':{}}
    plan=json.loads(config.read_text())
    for name,expected in plan.get('files_sha256',{}).items():
        assert sha(ROOT/name)==expected, f'Stale retained source/recipe: {name}'
    for actor,settings_by_view in plan['actors'].items():
        dest=out/actor;dest.mkdir()
        base=baseline['characters'][actor]
        oldatlas=ROOT/base['frozen_atlas'];oldmanifest=ROOT/base['frozen_manifest']
        assert sha(oldatlas)==base['atlas_sha256'] and sha(oldmanifest)==base['manifest_sha256']
        old=Image.open(oldatlas).convert('RGBA');manifest=json.loads(oldmanifest.read_text())
        oldcols=manifest['columns'];physical=old.width//128* (old.height//128)
        frames=[old.crop((i%oldcols*128,i//oldcols*128,i%oldcols*128+128,i//oldcols*128+128)) for i in range(physical)]
        lineage=[{'kind':'frozen-cardinal-cell','old_index':i,'rgba_sha256':rgba_sha(f)} for i,f in enumerate(frames)]
        banks={}; ownership={}
        for view,settings in settings_by_view.items():
            source=ROOT/settings['raw'];assert sha(source)==settings['raw_sha256'],source
            bankdest=dest/view;bankdest.mkdir()
            banks[view],ownership[view]=registered_bank(source,settings,bankdest)
            override=settings.get('walk_override')
            if override:
                assert len(override['frames'])==8
                for i,item in enumerate(override['frames']):
                    p=ROOT/item['path'];assert sha(p)==item['sha256'],p
                    replacement=Image.open(p).convert('RGBA')
                    assert replacement.size==(128,128)
                    box=replacement.getbbox()
                    assert box and min(box[:2])>0 and max(box[2:])<128, ('walk override touches stage border', actor, view, str(p), box)
                    banks[view][i]=replacement;replacement.save(bankdest/f'{i:02d}.png')
                ownership[view]['walk_override']=override
            for index,item in settings.get('cell_overrides',{}).items():
                i=int(index)
                assert 8<=i<32, 'Walks have their own explicit override'
                p=ROOT/item['path'];assert sha(p)==item['sha256'],p
                replacement=Image.open(p).convert('RGBA')
                assert replacement.size==(128,128)
                box=replacement.getbbox()
                assert box and min(box[:2])>0 and max(box[2:])<128
                banks[view][i]=replacement;replacement.save(bankdest/f'{i:02d}.png')
            if settings.get('cell_overrides'):ownership[view]['cell_overrides']=settings['cell_overrides']
            proof(banks[view],dest/f'{view}-native.png')
        for view,donor in [('southwest','southeast'),('northwest','northeast')]:
            banks[view]=[mirror(f) for f in banks[donor]]
        hands=manifest.get('cast_hand',DEFAULT_HANDS[actor]).copy()
        for view in ['southeast','northeast','northwest','southwest']:
            start=len(frames);bank=banks[view]
            for i,f in enumerate(bank):
                sourceview={'southwest':'southeast','northwest':'northeast'}.get(view,view)
                overrides=settings_by_view[sourceview]
                override=overrides.get('cell_overrides',{}).get(str(i))
                if i<8 and overrides.get('walk_override'):override=overrides['walk_override']['frames'][i]
                frames.append(f);lineage.append({'kind':'registered-diagonal','direction':view,'source_cell':i,
                  'painted_source_view':sourceview,'conditional_mirror':view!=sourceview,
                  'selected_override':override,'rgba_sha256':rgba_sha(f)})
            for action,(ids,holds,loop) in ACTIONS.items():
                manifest['animations'][f'{view}_{action}']={'frames':[start+i for i in ids],'holds':holds,'loop':loop}
            if view in settings_by_view and 'cast_hand' in settings_by_view[view]:hands[view]=settings_by_view[view]['cast_hand']
        for view,donor in [('southwest','southeast'),('northwest','northeast')]:
            if donor in hands:hands[view]=[128-hands[donor][0],hands[donor][1]]
        tracks=plan.get('cardinal_cast_tracks',{}).get(actor,{}).copy()
        for view,settings in settings_by_view.items():
            if 'cast_hand_track' not in settings:
                continue
            points=settings['cast_hand_track']
            assert isinstance(points,list) and len(points)==len(ACTIONS['cast'][0]), 'Track every cast exposure'
            for point in points:
                assert isinstance(point,list) and len(point)==2
                assert all(type(value) in (int,float) and math.isfinite(value) and 0<=value<128 for value in point)
            assert points[3]==hands[view], 'Charge track must preserve the measured release hand'
            assert points[0]==points[-1], 'Repeated neutral cel must have one unambiguous hand point'
            tracks[view]=points
        for view,donor in [('southwest','southeast'),('northwest','northeast')]:
            if donor in tracks:tracks[view]=[[128-point[0],point[1]] for point in tracks[donor]]
        for view,points in tracks.items():
            assert view in DIRECTIONS and len(points)==len(manifest['animations'][view+'_cast']['frames'])
            assert points[3]==hands[view], 'Preparation track must preserve the measured release hand'
            for point in points:
                assert isinstance(point,list) and len(point)==2
                assert all(type(value) in (int,float) and math.isfinite(value) and 0<=value<128 for value in point)
        if tracks:manifest['cast_hand_tracks']=tracks
        manifest.update({'directions':DIRECTIONS,'columns':16,'cast_hand':hands,'cast_release_index':3,
          'directional_source':str(config.resolve().relative_to(ROOT)) if config.resolve().is_relative_to(ROOT) else str(config.resolve()),
          'limitations':['Four frozen cardinal banks plus two painted diagonal views; SW/NW conditionally mirrored around pivotX64 with+1px mirror correction.',
            'Symmetric unarmed costume only; asymmetric accessories require new ownership/view paint.',
            'No jump/flying or modular weapon artwork; feet collision and hand projection remain separate.']})
        if production:assert set(hands)==set(DIRECTIONS),'Measure every painted release hand before production bake'
        atlas=Image.new('RGBA',(2048,128*math.ceil(len(frames)/16)))
        for i,f in enumerate(frames):atlas.alpha_composite(f,(i%16*128,i//16*128))
        atlas.save(dest/'atlas.png');dump(dest/'animations.json',manifest)
        dump(dest/'lineage.json',lineage);dump(dest/'source-ownership.json',ownership)
        receipt['actors'][actor]={'old_physical_cells':physical,'new_diagonal_cells':128,'clips':len(manifest['animations']),
          'atlas_sha256':sha(dest/'atlas.png'),'manifest_sha256':sha(dest/'animations.json'),'source_registration':settings_by_view,
          'preserved_old_cells':all(rgba_sha(atlas.crop((i%16*128,i//16*128,i%16*128+128,i//16*128+128)))==lineage[i]['rgba_sha256'] for i in range(physical))}
    dump(out/'REPLAY.json',receipt)
    print(json.dumps({a:{k:v for k,v in r.items() if k in ['clips','preserved_old_cells','atlas_sha256']} for a,r in receipt['actors'].items()}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--config',type=Path,default=BASE/'registration-v1.json');p.add_argument('--production',action='store_true');args=p.parse_args()
    build(args.out,args.config,args.production)

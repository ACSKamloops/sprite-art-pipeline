from pathlib import Path
import argparse, hashlib, json, math
import numpy as np
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rgba(p):
    return np.array(Image.open(p).convert('RGBA'))

def rows_mask(rows):
    m = np.zeros((128,128), bool)
    for y, x0, x1 in rows:
        assert not m[y,x0:x1+1].any()
        m[y,x0:x1+1] = True
    return m

def warp(a, owner, sv, tv, triangles):
    out = np.zeros_like(a)
    xy = np.full((128,128,2), -1, np.int16)
    tr = np.full((128,128), -1, np.int16)
    dets = []
    for n, ids in enumerate(triangles):
        s, t = sv[ids], tv[ids]
        sd = np.linalg.det(np.vstack((s.T, np.ones(3))))
        td = np.linalg.det(np.vstack((t.T, np.ones(3))))
        assert sd*td > 0, (n, sd, td)
        dets.append(float(td/sd))
        inv = np.linalg.inv(np.vstack((t.T, np.ones(3))))
        for y in range(max(0,math.floor(t[:,1].min())),min(127,math.ceil(t[:,1].max()))+1):
            for x in range(max(0,math.floor(t[:,0].min())),min(127,math.ceil(t[:,0].max()))+1):
                w = inv @ [x,y,1]
                if min(w) < -1e-8:
                    continue
                sx, sy = np.floor(w @ s + .5).astype(int)
                if not (0 <= sx < 128 and 0 <= sy < 128 and owner[sy,sx]):
                    continue
                out[y,x] = a[sy,sx]
                xy[y,x] = [sx,sy]
                tr[y,x] = n
    return out, xy, tr, dets

def image_save(a,p):
    Image.fromarray(a).save(p)

def composite(layers):
    im = Image.new('RGBA',(128,128))
    for a in layers:
        im = Image.alpha_composite(im,Image.fromarray(a))
    return np.array(im)

def on_ground(a, size, ground):
    im = Image.fromarray(a).resize((size,size),Image.Resampling.NEAREST)
    bg = Image.new('RGBA',(size,size),ground+(255,))
    return Image.alpha_composite(bg,im).convert('RGB')

def build(out):
    assert out.is_absolute() and not out.exists()
    for f in json.loads((P/'INPUTS.json').read_text())['files']:
        assert sha(P/f['path']) == f['sha256'], f['path']
    spec = json.loads((P/'spec/RECIPE.json').read_text())
    a = rgba(P/'inputs/current/03.png')
    cloth = rows_mask(spec['cloth']['literal_inclusive_rows'])
    boot = rows_mask(spec['boot']['literal_inclusive_rows'])
    z = np.load(P/'inputs/upstream-maps/03.npz',allow_pickle=False)
    upper = np.isin(z['layer_id'],[0,4,5,6]) & (a[:,:,3]>0)
    assert not (cloth & boot).any()
    assert not ((cloth|boot)&upper).any()
    assert np.all(a[cloth|boot,3]>0)
    center = np.array(spec['boot']['pivot'],float)
    ang = math.radians(spec['boot']['angle_clockwise_degrees'])
    R = np.array([[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]])
    bs = np.array([[60,84],[83,84],[83,114],[60,114]],float)
    bt = (bs-center) @ R.T + center
    btri = np.array([[0,1,2],[0,2,3]])
    bl, bxy, btm, bd = warp(a,boot,bs,bt,btri)
    xs,ys = [60,65,70,75,81],[80,81,82,84,86,88,90,92,94]
    cs = np.array([[x,y]for y in ys for x in xs],float)
    cr = (cs-center) @ R.T + center
    weight = np.clip((cs[:,1]-81)/11,0,1)[:,None]
    ct = cs + weight*(cr-cs)
    ctri=[]
    for j in range(len(ys)-1):
        for i in range(len(xs)-1):
            k=j*len(xs)+i
            ctri += [[k,k+1,k+len(xs)+1],[k,k+len(xs)+1,k+len(xs)]]
    ctri=np.array(ctri)
    cl,cxy,ctm,cd=warp(a,cloth,cs,ct,ctri)
    raw_boot=bl.copy()
    raw_bxy=bxy.copy()
    cleanup_witness=[]
    for op in spec.get('sole_cleanup',{}).get('operations',[]):
        x,y=op['target']
        assert 58<=x<=80 and 100<=y<=113
        assert bl[y,x].tolist()==op['expected_before_RGBA']
        if op['op']=='erase':
            bl[y,x]=0;bxy[y,x]=[-1,-1];btm[y,x]=-1
        else:
            sx,sy=op['source'];assert boot[sy,sx]
            assert a[sy,sx].tolist()==op['source_RGBA']
            bl[y,x]=a[sy,sx];bxy[y,x]=[sx,sy];btm[y,x]=-2
        cleanup_witness.append({**op,'after_RGBA':bl[y,x].tolist()})
    base=a.copy();base[cloth|boot|upper]=0
    upl=np.zeros_like(a);upl[upper]=a[upper]
    under=np.zeros_like(a)
    under_witness=[]
    for x,y in spec.get('joint_underlap',{}).get('identity_coordinates',[]):
        assert (cloth|boot)[y,x] and a[y,x,3]>0
        under[y,x]=a[y,x]
        under_witness.append({'target':[x,y],'source_phase':3,'source':[x,y],'RGBA':a[y,x].tolist()})
    result=composite([base,under,cl,bl,upl])
    out.mkdir()
    for d in ['layers','maps','masks','proof']:(out/d).mkdir()
    for name,layer in [('retained-other',base),('joint-underlap',under),('cloth',cl),('boot',bl),('upper',upl)]:image_save(layer,out/f'layers/{name}.png')
    image_save(raw_boot,out/'layers/boot-before-contour-cleanup.png')
    np.savez_compressed(out/'maps/boot-before-contour-cleanup.npz',source_xy=raw_bxy)
    for name,mask in [('cloth-source',cloth),('boot-source',boot),('protected-upper',upper),('other-visible-source',(a[:,:,3]>0)&~(cloth|boot|upper))]:image_save(mask.astype('uint8')*255,out/f'masks/{name}.png')
    image_save(result,out/'03.png')
    np.savez_compressed(out/'maps/cloth.npz',source_xy=cxy,triangle=ctm)
    np.savez_compressed(out/'maps/boot.npz',source_xy=bxy,triangle=btm)
    geometry={'cloth':{'source_vertices':cs.tolist(),'target_vertices':ct.tolist(),'triangles':ctri.tolist(),'determinant_ratios':cd},'boot':{'source_vertices':bs.tolist(),'target_vertices':bt.tolist(),'triangles':btri.tolist(),'determinant_ratios':bd},'raster':'integer centers; inverse barycentric, floor(source+0.5); last valid owned triangle wins; no alpha threshold or paint'}
    (out/'maps/GEOMETRY.json').write_text(json.dumps(geometry,indent=2)+'\n')
    counts={};witness=[]
    other=(base[:,:,3]>0)
    for name,layer,xy in [('cloth',cl,cxy),('boot',bl,bxy)]:
        owned=xy[:,:,0]>=0
        assert np.array_equal(layer[owned],a[xy[:,:,1][owned],xy[:,:,0][owned]])
        unique=set(map(tuple,xy[owned].tolist()))
        counts[name]={'source_pixels':int((cloth if name=='cloth'else boot).sum()),'target_samples':int(owned.sum()),'unique_source_texels':len(unique),'unrepresented_source_texels':int((cloth if name=='cloth'else boot).sum())-len(unique)}
        for y,x in zip(*np.where(owned)):
            sx,sy=map(int,xy[y,x]);witness.append({'part':name,'target':[int(x),int(y)],'source_phase':3,'source':[sx,sy],'RGBA':a[sy,sx].tolist()})
    occlusions=[]
    for y,x in zip(*np.where(other&((cl[:,:,3]>0)|(bl[:,:,3]>0)))):
        occlusions.append({'target':[int(x),int(y)],'retained_RGBA':base[y,x].tolist(),'cloth_RGBA':cl[y,x].tolist(),'boot_RGBA':bl[y,x].tolist(),'composed_RGBA':result[y,x].tolist()})
    upper_overlap=upper&((cl[:,:,3]>0)|(bl[:,:,3]>0))
    assert not upper_overlap.any()
    assert np.array_equal(result[upper],a[upper])
    untouched_other=other&~((cl[:,:,3]>0)|(bl[:,:,3]>0))
    assert np.array_equal(result[untouched_other],a[untouched_other])
    removed=(a[:,:,3]>0)&(result[:,:,3]==0)
    loss=[{'target':[int(x),int(y)],'before_RGBA':a[y,x].tolist(),'original_owner':'cloth'if cloth[y,x]else'boot'if boot[y,x]else'PROTECTED'}for y,x in zip(*np.where(removed))]
    assert all(r['original_owner']!='PROTECTED'for r in loss)
    receipt={'scope':'ONE actual03 source-part transition candidate; no art acceptance','clock':spec['clock'],'model_calls':0,'part_counts':counts,'literal_source_joint_underlap':under_witness,'literal_sole_contour_cleanup':cleanup_witness,'actual_changed_RGBA_pixels':int(np.any(a!=result,axis=2).sum()),'upper_RGBA_exact':True,'other_visible_source_layer_RGBA_exact':True,'natural_foreground_occlusions':occlusions,'upper_overlap':int(upper_overlap.sum()),'new_authored_paint_pixels':0,'old_owned_vacated_pixels':loss,'candidate_sha256':sha(out/'03.png')}
    (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'maps/SOURCE-WITNESSES.json').write_text(json.dumps(witness,indent=2)+'\n')
    current=[rgba(P/f'inputs/current/{i:02}.png')for i in [2,3,4]]
    test=[current[0],result,current[2]]
    grounds={'light':(224,221,211),'dark':(24,28,32),'game':(52,62,48)}
    owner=np.zeros_like(a);owner[cloth]=[245,210,80,255];owner[boot]=[220,90,40,255];owner[upper]=[40,110,240,255];owner[other]=[130,130,130,255]
    for name,g in grounds.items():
        for size in [128,256,84]:
            im=Image.new('RGB',(size*3,size*2+44),g);d=ImageDraw.Draw(im)
            for row,frames in enumerate([current,test]):
                for col,ar in enumerate(frames):im.paste(on_ground(ar,size,g),(col*size,row*(size+22)+22))
                d.text((4,row*(size+22)+4),'CONTROL 02 / 03 / 04'if row==0 else'ONE TEST 02 / new03 / 04',fill=(255,255,255)if name!='light'else(0,0,0))
            im.save(out/f'proof/02-03-04-{size}-{name}.png')
        crop=(56,79,84,114);scale=10;w,h=(crop[2]-crop[0])*scale,(crop[3]-crop[1])*scale
        im=Image.new('RGB',(w*4,h+24),g);d=ImageDraw.Draw(im)
        for col,(label,ar)in enumerate([('02',current[0]),('control03',a),('test03',result),('04',current[2])]):
            c=Image.fromarray(ar).crop(crop).resize((w,h),Image.Resampling.NEAREST);bg=Image.new('RGBA',(w,h),g+(255,));bg=Image.alpha_composite(bg,c);im.paste(bg.convert('RGB'),(col*w,24));d.text((col*w+4,4),label,fill='white'if name!='light'else'black')
        im.save(out/f'proof/joints10x-{name}.png')
    im=Image.new('RGB',(768,282),(224,221,211));d=ImageDraw.Draw(im)
    for col,(label,ar)in enumerate([('current03',a),('literal source owners',owner),('single16deg test',result)]):im.paste(on_ground(ar,256,(224,221,211)),(col*256,26));d.text((col*256+4,5),label,fill='black')
    im.save(out/'proof/owner-control-test-2x.png')
    print(json.dumps({k:v for k,v in receipt.items()if k not in ['natural_foreground_occlusions','old_owned_vacated_pixels']}))
    print('occlusions',len(occlusions),'vacated',len(loss))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();build(args.output)

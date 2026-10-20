"""One source-owned Lyra NE03 hypothesis; no models/editor/game operations."""
from pathlib import Path
from collections import deque
import argparse,hashlib,json,math
import numpy as np
from PIL import Image,ImageDraw

P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def rows_mask(rows):
    m=np.zeros((128,128),bool)
    for y,x0,x1 in rows:assert not m[y,x0:x1+1].any();m[y,x0:x1+1]=True
    return m
def warp(a,owner,sv,tv,triangles):
    out=np.zeros_like(a);xy=np.full((128,128,2),-1,np.int16);ti=np.full((128,128),-1,np.int16);ratios=[]
    for n,ids in enumerate(triangles):
        s,t=sv[ids],tv[ids];sd=np.linalg.det(np.vstack((s.T,np.ones(3))));td=np.linalg.det(np.vstack((t.T,np.ones(3))));assert sd*td>0;ratios.append(float(td/sd));inv=np.linalg.inv(np.vstack((t.T,np.ones(3))))
        for y in range(max(0,math.floor(t[:,1].min())),min(127,math.ceil(t[:,1].max()))+1):
            for x in range(max(0,math.floor(t[:,0].min())),min(127,math.ceil(t[:,0].max()))+1):
                w=inv@[x,y,1]
                if min(w)<-1e-8:continue
                sx,sy=np.floor(w@s+.5).astype(int)
                if not(0<=sx<128 and 0<=sy<128 and owner[sy,sx]):continue
                out[y,x]=a[sy,sx];xy[y,x]=[sx,sy];ti[y,x]=n
    return out,xy,ti,ratios
def compose(parts):
    im=Image.new('RGBA',(128,128))
    for a in parts:im=Image.alpha_composite(im,Image.fromarray(a))
    return np.array(im)
def holes(a):
    m=a[:,:,3]==0;seen=np.zeros((128,128),bool);q=deque()
    for y,x in [(i,0)for i in range(128)]+[(i,127)for i in range(128)]+[(0,i)for i in range(128)]+[(127,i)for i in range(128)]:
        if m[y,x]and not seen[y,x]:seen[y,x]=True;q.append((y,x))
    while q:
        y,x=q.popleft()
        for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:
            yy,xx=y+dy,x+dx
            if 0<=yy<128 and 0<=xx<128 and m[yy,xx]and not seen[yy,xx]:seen[yy,xx]=True;q.append((yy,xx))
    return m&~seen
def ground(a,size,color):
    im=Image.fromarray(a).resize((size,size),Image.Resampling.NEAREST);bg=Image.new('RGBA',(size,size),color+(255,));return Image.alpha_composite(bg,im).convert('RGB')

def build(out):
    assert out.is_absolute()and not out.exists()
    for f in json.loads((P/'INPUTS.json').read_text())['files']:assert sha(P/f['path'])==f['sha256']
    s=json.loads((P/'spec/RECIPE.json').read_text());a=rgba(P/'inputs/current/03.png');cloth=rows_mask(s['cloth']['inclusive_source_rows']);boot=rows_mask(s['boot']['inclusive_source_rows'])
    z=np.load(P/'inputs/maps/03.npz',allow_pickle=False);upper=np.isin(z['layer_id'],[0,4,5,6])&(a[:,:,3]>0)
    assert not(cloth&boot).any()and not((cloth|boot)&upper).any();assert np.all(a[cloth|boot,3]>0)
    cen=np.array(s['boot']['pivot'],float);angle=math.radians(s['boot']['clockwise_angle_degrees']);R=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    bs=np.array([[56,90],[81,90],[81,117],[56,117]],float);bt=(bs-cen)@R.T+cen;btri=np.array([[0,1,2],[0,2,3]])
    bl,bxy,bti,bd=warp(a,boot,bs,bt,btri)
    xs,ys=[60,63,65,68,70,74,78],[81,82,83,84,86,88,90,92,94,96,97]
    cs=np.array([[x,y]for y in ys for x in xs],float);cr=(cs-cen)@R.T+cen;weight=(np.clip((cs[:,1]-83)/12,0,1)*np.clip((cs[:,0]-65)/5,0,1))[:,None];ct=cs+weight*(cr-cs);ctri=[]
    for j in range(len(ys)-1):
        for i in range(len(xs)-1):k=j*len(xs)+i;ctri.extend([[k,k+1,k+len(xs)+1],[k,k+len(xs)+1,k+len(xs)]])
    for point in s['cloth'].get('rigid_terminal_source_pins',[]):
        idx=np.where(np.all(cs==point,axis=1))[0];assert len(idx)==1;ct[idx[0]]=cr[idx[0]]
    ctri=np.array(ctri);cl,cxy,cti,cd=warp(a,cloth,cs,ct,ctri)
    base=a.copy();base[cloth|boot|upper]=0;up=np.zeros_like(a);up[upper]=a[upper];under=np.zeros_like(a)
    for x,y in s['declared_cloth_seam_underlap']:assert cloth[y,x];under[y,x]=a[y,x]
    for x,y in s.get('declared_boot_shared_joint_underlap',[]):assert boot[y,x];under[y,x]=a[y,x]
    raw_boot=bl.copy();raw_bxy=bxy.copy();literal=[]
    for op in s['sole_cleanup']:
        x,y=op['target'];assert bl[y,x].tolist()==op['before_RGBA']
        if op['op']=='erase':bl[y,x]=0;bxy[y,x]=[-1,-1];bti[y,x]=-1
        else:sx,sy=op['source'];assert boot[sy,sx];assert a[sy,sx].tolist()==op['source_RGBA'];bl[y,x]=a[sy,sx];bxy[y,x]=[sx,sy];bti[y,x]=-2
        literal.append({**op,'after_RGBA':bl[y,x].tolist()})
    raw=compose([base,under,cl,raw_boot,up]);result=compose([base,under,cl,bl,up])
    assert np.array_equal(result[upper],a[upper]);assert np.array_equal(result[:82],a[:82])
    other=base[:,:,3]>0;occluded=other&((cl[:,:,3]>0)|(bl[:,:,3]>0));uncovered=other&~occluded;assert np.array_equal(result[uncovered],a[uncovered])
    out.mkdir()
    for d in ['layers','maps','masks','proof']:(out/d).mkdir()
    for name,ar in [('raw03',raw),('03',result)]:Image.fromarray(ar).save(out/f'{name}.png')
    for name,ar in [('retained-other',base),('source-seam-underlap',under),('cloth',cl),('boot-before-cleanup',raw_boot),('boot',bl),('upper',up)]:Image.fromarray(ar).save(out/f'layers/{name}.png')
    for name,m in [('literal-cloth-source',cloth),('literal-boot-source',boot),('protected-upper',upper),('other-visible-source',other)]:Image.fromarray(m.astype('uint8')*255).save(out/f'masks/{name}.png')
    np.savez_compressed(out/'maps/cloth.npz',source_xy=cxy,triangle=cti);np.savez_compressed(out/'maps/boot.npz',source_xy=bxy,triangle=bti);np.savez_compressed(out/'maps/boot-before-cleanup.npz',source_xy=raw_bxy)
    geom={'boot':{'source_vertices':bs.tolist(),'target_vertices':bt.tolist(),'triangles':btri.tolist(),'determinant_ratios':bd},'cloth':{'source_vertices':cs.tolist(),'target_vertices':ct.tolist(),'triangles':ctri.tolist(),'determinant_ratios':cd},'raster':'Integer pixel centers; inverse barycentric; floor(source+0.5); last valid owned sample. No color interpolation or generic masks.'};(out/'maps/GEOMETRY.json').write_text(json.dumps(geom,indent=2)+'\n')
    witness=[];counts={}
    for name,ar,xy,m in [('cloth',cl,cxy,cloth),('boot',bl,bxy,boot)]:
        valid=xy[:,:,0]>=0;assert np.array_equal(ar[valid],a[xy[:,:,1][valid],xy[:,:,0][valid]])
        counts[name]={'source_pixels':int(m.sum()),'target_samples':int(valid.sum()),'distinct_source_texels':len(set(map(tuple,xy[valid].tolist())))}
        for y,x in zip(*np.where(valid)):
            sx,sy=map(int,xy[y,x]);witness.append({'part':name,'target':[int(x),int(y)],'source03_xy':[sx,sy],'RGBA':a[sy,sx].tolist()})
    (out/'maps/SOURCE-WITNESSES.json').write_text(json.dumps(witness,indent=2)+'\n')
    newholes=holes(result)&~holes(a);gapw=[]
    for y,x in zip(*np.where(newholes)):gapw.append({'xy':[int(x),int(y)],'original_RGBA':a[y,x].tolist(),'old_owner':'cloth'if cloth[y,x]else'boot'if boot[y,x]else'other','upstream_layer_id':int(z['layer_id'][y,x])})
    occ=[]
    for y,x in zip(*np.where(occluded)):occ.append({'xy':[int(x),int(y)],'retained_RGBA':base[y,x].tolist(),'cloth_RGBA':cl[y,x].tolist(),'boot_RGBA':bl[y,x].tolist(),'composed_RGBA':result[y,x].tolist()})
    rec={'status':'ONE source-pixel candidate, visual feasibility pending','clock':s['clock'],'angle_clockwise_degrees':s['boot']['clockwise_angle_degrees'],'pivot':s['boot']['pivot'],'part_counts':counts,'new_enclosed_transparent_pixels':gapw,'natural_occlusions_of_retained_source':occ,'upper_and_rows_through81_RGBA_exact':True,'retained_other_source_layer_exact':True,'actual_changed_RGBA_pixels':int(np.any(result!=a,axis=2).sum()),'literal_sole_cleanup':literal,'new_authored_RGB_pixels':0,'PNG_sha256':sha(out/'03.png'),'generation_calls':0,'editor_package':False}
    (out/'RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
    before=[rgba(P/f'inputs/current/{i:02}.png')for i in [2,3,4]];after=[before[0],result,before[2]];grounds={'light':(224,221,211),'dark':(24,28,32),'game':(52,62,48)}
    for g,color in grounds.items():
        ink='black'if g=='light'else'white'
        for size in [128,256,84]:
            sheet=Image.new('RGB',(size*3,2*(size+22)),color);d=ImageDraw.Draw(sheet)
            for row,ims in enumerate([before,after]):
                d.text((4,row*(size+22)+4),'CURRENT 02 / 03 / 04'if row==0 else'ONE TEST 02 / new03 / 04',fill=ink)
                for col,ar in enumerate(ims):sheet.paste(ground(ar,size,color),(col*size,row*(size+22)+22))
            sheet.save(out/f'proof/02-03-04-{size}-{g}.png')
        crop=(55,80,81,117);sc=10;w,h=26*sc,37*sc;sheet=Image.new('RGB',(w*4,h+26),color);d=ImageDraw.Draw(sheet)
        for col,(label,ar)in enumerate([('02',before[0]),('current03',a),('new03',result),('04',before[2])]):
            im=Image.fromarray(ar).crop(crop).resize((w,h),Image.Resampling.NEAREST);bg=Image.new('RGBA',(w,h),color+(255,));bg=Image.alpha_composite(bg,im);sheet.paste(bg.convert('RGB'),(col*w,26));d.text((col*w+4,4),label,fill=ink)
        sheet.save(out/f'proof/joints10x-{g}.png')
    owner=np.zeros_like(a);owner[other]=[130,130,130,255];owner[cloth]=[130,150,225,255];owner[boot]=[225,100,35,255];owner[upper]=[30,100,240,255]
    sheet=Image.new('RGB',(768,282),(224,221,211));d=ImageDraw.Draw(sheet)
    for col,(label,ar)in enumerate([('current03',a),('literal current source owners',owner),('single source test',result)]):sheet.paste(ground(ar,256,(224,221,211)),(col*256,26));d.text((col*256+3,5),label,fill='black')
    sheet.save(out/'proof/source-owner-test2x.png')
    print(json.dumps({k:v for k,v in rec.items()if k not in ['natural_occlusions_of_retained_source','new_enclosed_transparent_pixels']}));print('newholes',len(gapw),'retained-source occlusions',len(occ))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();build(a.output)

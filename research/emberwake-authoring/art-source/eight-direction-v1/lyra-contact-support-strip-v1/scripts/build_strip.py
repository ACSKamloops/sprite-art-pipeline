"""One three-key source-rig feasibility strip. Reject inverted cloth fields."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parents[1]
def a(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def over(back,front):return np.array(Image.alpha_composite(Image.fromarray(back),Image.fromarray(front)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):p.write_text(json.dumps(value,indent=2)+'\n')
def literal_rows(m):
    result={}
    for y in range(128):
        xs=np.flatnonzero(m[y])
        if not len(xs):continue
        runs=[];first=last=int(xs[0])
        for x in xs[1:]:
            if x==last+1:last=int(x)
            else:runs.append([first,last]);first=last=int(x)
        runs.append([first,last]);result[str(y)]=runs
    return result

def field_geometry(cloth,boot,body,hip,weight,boot_delta,hip_dy):
    cache={};faces=[];conflicts=[]
    def corner(x2,y2):
        if (x2,y2) in cache:return cache[x2,y2]
        x,y=x2/2,y2/2
        incident=[(int(math.floor(x))+dx,int(math.floor(y))+dy)for dx,dy in [(0,0),(1,0),(0,1),(1,1)]]
        edge_boot=any(boot[yy,xx]for xx,yy in incident)
        edge_hip=any(body[yy,xx]or hip[yy,xx]for xx,yy in incident)
        values=[weight[yy,xx]for xx,yy in incident if cloth[yy,xx]]
        if edge_boot and edge_hip:conflicts.append([x,y])
        w=1. if edge_boot else(0. if edge_hip else float(np.mean(values)))
        source=np.array([x,y]);target=source+np.array([0.,hip_dy])*(1-w)+boot_delta*w
        cache[x2,y2]=(source,target,w)
        return cache[x2,y2]
    for y,x in np.argwhere(cloth):
        cs=[corner(2*x-1,2*y-1),corner(2*x+1,2*y-1),corner(2*x+1,2*y+1),corner(2*x-1,2*y+1)]
        for tri in [(0,1,2),(0,2,3)]:
            s=np.array([cs[k][0]for k in tri]);t=np.array([cs[k][1]for k in tri])
            det=float(np.linalg.det(np.column_stack((t[1]-t[0],t[2]-t[0]))))
            faces.append({'source_pixel':[int(x),int(y)],'source_triangle':s.tolist(),'target_triangle':t.tolist(),'determinant':det})
    return faces,conflicts

def raster_cloth(source,faces):
    layer=np.zeros_like(source);xy=np.full((128,128,2),-1,np.int16);owner=np.zeros((128,128),bool);overlaps=[]
    for f in faces:
        assert f['determinant']>0,'Refusing to rasterize collapsed/inverted cloth'
        t=np.array(f['target_triangle']);x,y=f['source_pixel'];inv=np.linalg.inv(np.vstack((t.T,np.ones(3))))
        for yy in range(max(0,int(math.ceil(t[:,1].min()))),min(127,int(math.floor(t[:,1].max())))+1):
            for xx in range(max(0,int(math.ceil(t[:,0].min()))),min(127,int(math.floor(t[:,0].max())))+1):
                if (inv@np.array([xx,yy,1.])).min() < -1e-9:continue
                if owner[yy,xx]and xy[yy,xx].tolist()!=[x,y]:overlaps.append([xx,yy])
                layer[yy,xx]=source[y,x];xy[yy,xx]=[x,y];owner[yy,xx]=True
    return layer,xy,owner,overlaps

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    assert not args.output.exists(),'Fresh output required'
    args.output.mkdir(parents=True)
    for e in json.loads((R/'INPUTS.json').read_text()):assert sha(R/e['retained'])==e['sha256']
    master=a(R/'inputs/master04.png');q=mask(R/'inputs/master-Q-owner.png');cloth=mask(R/'inputs/master-cloth-owner.png');boot=mask(R/'inputs/master-boot-owner.png')
    body4=a(R/'inputs/master04-body.png')[...,3]>0;hip=mask(R/'inputs/master-hip-pins.png');weight=np.load(R/'inputs/master-field.npz')['weight']
    xy4=np.load(R/'inputs/master04-donor06.npz')['source_xy']
    outputs=[];records=[];owners={}
    settings={4:([8,8],0,[8,8]),5:([-2,-2],-1,[0,0]),6:([-12,-12],-2,[-8,-8])}
    for phase,(delta,hip_dy,extra) in settings.items():
        current=a(R/f'inputs/{phase:02}-current.png');body_layer=a(R/f'inputs/{phase:02}-body.png');body=body_layer[...,3]>0
        if phase==4:oldq=q.copy()
        elif phase==5:
            oldq=np.load(R/'inputs/05-current-part-map.npz')['owner'].copy()
            oldq|=a(R/'inputs/05-Q-cloth.png')[...,3]>0
            yy,xx=np.indices((128,128));oldq&=(yy>=79)&(xx>=40)&(xx<=67)
        else:
            oldq=np.zeros((128,128),bool)
            for y,x in np.argwhere(q):
                sx,sy=xy4[y,x]
                if sx>=0 and sy>=0:oldq[sy,sx]=True
            oldq|=a(R/'inputs/06-Q-cloth.png')[...,3]>0
        oldq&=(current[...,3]>0)&~body
        owners[str(phase)]={'literal_old_visible_Q_rows':literal_rows(oldq),'body_overlap_after_exclusion':int((oldq&body).sum()),
                            'construction':'04 frozen literal owner;05 actual retained left-front part map plus mapped cloth;06 literal04master donor06 map union mapped cloth. Exact rows serialized, no RGB mask.'}
        faces,conflicts=field_geometry(cloth,boot,body4,hip,weight,np.array(delta,float),hip_dy)
        failed=[f for f in faces if f['determinant']<=0]
        accepted=not failed and not conflicts
        boot_layer=np.zeros_like(master);boot_xy=np.full((128,128,2),-1,np.int16);target_boot=np.zeros((128,128),bool)
        for y,x in np.argwhere(boot):
            tx,ty=x+delta[0],y+delta[1]
            assert 0<=tx<128 and 0<=ty<128,'No boot clamping allowed'
            boot_layer[ty,tx]=master[y,x];boot_xy[ty,tx]=[x,y];target_boot[ty,tx]=True
        assert np.array_equal(boot_layer[target_boot],master[boot])
        if accepted:
            cloth_layer,cloth_xy,target_cloth,overlaps=raster_cloth(master,faces)
            if overlaps:accepted=False
        else:
            cloth_layer=np.zeros_like(master);cloth_xy=np.full((128,128,2),-1,np.int16);target_cloth=np.zeros((128,128),bool);overlaps=[]
        base=current.copy();base[oldq]=0
        candidate=over(over(base,cloth_layer),boot_layer);candidate[body]=current[body]
        # New opaque Q paint changes the background beneath partial-alpha
        # upper edges. Preserve the upper source layer and use actual source-
        # over at those intersections, rather than cutting an alpha hole.
        lower=over(cloth_layer,boot_layer)
        overlap_upper=(target_boot|target_cloth)&body
        assert np.all(lower[overlap_upper,3]==255)
        normal_upper=over(lower,body_layer)
        candidate[overlap_upper]=normal_upper[overlap_upper]
        overlap_witnesses=[]
        for y,x in np.argwhere(overlap_upper):
            overlap_witnesses.append({'target':[int(x),int(y)],'foreground_upper_source_RGBA':body_layer[y,x].tolist(),
                                      'new_opaque_Q_under_RGBA':lower[y,x].tolist(),'previous_displayed_RGBA':current[y,x].tolist(),
                                      'new_source_over_displayed_RGBA':candidate[y,x].tolist()})
        write(args.output/f'{phase:02}-LOWER-UPPER-OVERLAP.json',overlap_witnesses)
        if phase==4:assert np.array_equal(candidate,a(R/'inputs/frozen04-plus8.png'))
        role='support-feasibility'if accepted else'rejected-boot-only-diagnostic'
        Image.fromarray(candidate).save(args.output/f'{phase:02}-{role}.png')
        Image.fromarray(boot_layer).save(args.output/f'{phase:02}-complete-boot-layer.png')
        Image.fromarray(cloth_layer).save(args.output/f'{phase:02}-cloth-layer.png')
        Image.fromarray(oldq.astype('uint8')*255).save(args.output/f'{phase:02}-old-Q-visible-owner.png')
        np.savez_compressed(args.output/f'{phase:02}-source-maps.npz',boot_source04_xy=boot_xy,cloth_source04_xy=cloth_xy,target_boot=target_boot,target_cloth=target_cloth)
        write(args.output/f'{phase:02}-FIELD.json',{'hip_delta':[0,hip_dy],'master_boot_delta':delta,'extra_relative_to_current_sole':extra,
                                                  'triangles':faces,'nonpositive_count':len(failed),'corner_conflicts':conflicts})
        occlusions=[]
        for y,x in np.argwhere(target_boot&body):
            sx,sy=boot_xy[y,x];occlusions.append({'target':[int(x),int(y)],'boot_master04':[int(sx),int(sy)],'retained_boot_RGBA':master[sy,sx].tolist(),
                                               'foreground_current_body_RGBA':current[y,x].tolist(),'composed_RGBA':candidate[y,x].tolist()})
        write(args.output/f'{phase:02}-BOOT-OCCLUSIONS.json',occlusions)
        yb,xb=np.where(target_boot)
        records.append({'phase':phase,'status':role,'field_accepted':accepted,'complete_boot_layer_pixels':int(boot.sum()),
                        'full_boot_layer_RGBA_exact_at_declared_translation':True,'boot_bbox_inclusive':[int(xb.min()),int(yb.min()),int(xb.max()),int(yb.max())],
                        'boot_pixels_occluded_by_current_upper':len(occlusions),'boot_pixels_outside_current_upper':int((target_boot&~body).sum()),
                        'upper_body_source_layer_RGBA_exact':True,
                        'upper_visible_RGBA_exact_except_declared_new_Q_overlap':bool(np.array_equal(candidate[body&~overlap_upper],current[body&~overlap_upper])),
                        'upper_displayed_RGBA_changed_by_new_opaque_background':int(np.any(candidate[body]!=current[body],axis=1).sum()),
                        'minimum_triangle_determinant':min(f['determinant']for f in faces),
                        'nonpositive_triangles':len(failed),'different_donor_overlap_count':len(overlaps),'corner_pin_conflicts':conflicts,
                        'failed_triangle_examples':failed[:8],'new_paint':0,'hidden_fill':0,'cloth_rasterized':accepted})
        outputs.append(candidate)
    write(args.output/'LITERAL-OLD-PART-OWNERS.json',owners)
    write(args.output/'RECEIPT.json',{'status':'Bounded three-key source-rig test; no gait/engine/art acceptance','same_boot_master_for_all_three':True,
                                     'same_04_source_cloth_master':True,'hip_registration_y':{'04':0,'05':-1,'06':-2},
                                     'boot_master_translation':{'04':[8,8],'05':[-2,-2],'06':[-12,-12]},
                                     'extra_vs_existing_distal_sole_path':{'04':[8,8],'05':[0,0],'06':[-8,-8]},'phases':records,
                                     'negative_fields_not_rasterized':True,'new_art_variants_outside_three_keys':0,'editor_or_engine_changes':0})
    for size in [128,84,256]:
        for ground,name,ink in [('#e7e3d6','light','black'),('#22252b','dark','white'),('#27392f','game','white')]:
            board=Image.new('RGB',(size*3,(size+30)*2),ground);d=ImageDraw.Draw(board)
            for j,phase in enumerate([4,5,6]):
                for row,image in enumerate([a(R/f'inputs/{phase:02}-current.png'),outputs[j]]):
                    im=Image.fromarray(image).resize((size,size),Image.Resampling.NEAREST);board.paste(im,(j*size,row*(size+30)+30),im)
                    label=f'current{phase:02}'if row==0 else(f'{phase:02} extra{settings[phase][2]}'if records[j]['field_accepted']else'06 REJECTED cloth')
                    d.text((j*size+3,row*(size+30)+4),label,fill=ink)
                    if row==1 and not records[j]['field_accepted']:d.text((j*size+3,row*(size+30)+16),'boot only / not pose',fill='#ff8080')
            board.save(args.output/f'three-key-{size}-{name}.png')
    # Show the failed source-to-target mesh explicitly instead of painting it.
    board=Image.new('RGB',(640,640),'#e7e3d6');d=ImageDraw.Draw(board)
    current=a(R/'inputs/06-current.png');im=Image.fromarray(current).resize((640,640),Image.Resampling.NEAREST);board.paste(im,(0,0),im)
    faces=json.loads((args.output/'06-FIELD.json').read_text())['triangles']
    for f in faces:
        if f['determinant']>0:continue
        points=[((x+.5)*5,(y+.5)*5)for x,y in f['target_triangle']];d.line(points+[points[0]],fill='#ef3054',width=1)
    d.text((6,6),'06 rejected: inverted target cloth triangles over current06 reference',fill='black')
    board.save(args.output/'06-inverted-field-on-current-reference-5x.png')
    print(json.dumps([{k:r[k]for k in ['phase','field_accepted','minimum_triangle_determinant','nonpositive_triangles','boot_pixels_occluded_by_current_upper','upper_body_source_layer_RGBA_exact','upper_displayed_RGBA_changed_by_new_opaque_background']}for r in records]))

if __name__=='__main__':main()

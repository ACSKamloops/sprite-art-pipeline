#!/usr/bin/env python3
"""Authored orthographic skeletal diagnostic; not recovered anatomy or finished armor."""
import argparse, hashlib, json, math
from pathlib import Path
from PIL import Image, ImageDraw
HERE=Path(__file__).resolve().parent

def add(a,b): return [x+y for x,y in zip(a,b)]
def sub(a,b): return [x-y for x,y in zip(a,b)]
def mul(a,s): return [x*s for x in a]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def length(a): return math.sqrt(dot(a,a))
def unit(a): return mul(a,1/length(a))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def rotate(v,axis,r): return add(add(mul(v,math.cos(r)),mul(cross(axis,v),math.sin(r))),mul(axis,dot(axis,v)*(1-math.cos(r))))
def smooth(t): return t*t*(3-2*t)
CONFIG=json.loads((HERE/'design.json').read_text())
E=math.radians(CONFIG['camera_elevation_degrees']); F=CONFIG['forward_world']; T=CONFIG['transverse_world']; D=CONFIG['stride_world_length']
CAM={'projection':'orthographic','screen_origin':[130,239],'elevation_degrees':18,'world_axes':'X screen right; Y toward camera; Z up','matrix_2x3':[[1,0,0],[0,math.sin(E),-math.cos(E)]],'forward':F,'transverse':T,'pixel_per_world_unit':1}
def project(p): return [CONFIG['screen_origin'][0]+p[0],CONFIG['screen_origin'][1]+math.sin(E)*p[1]-math.cos(E)*p[2]]
FOOT={'heel':mul(F,-CONFIG['heel_distance']),'toe':mul(F,CONFIG['toe_distance']),'ankle':[0,0,CONFIG['ankle_projected_height']/math.cos(E)]}
SOLE=[add(FOOT[n],mul(T,s*CONFIG['foot_width']/2)) for n,s in [('heel',-1),('heel',1),('toe',1),('toe',-1)]]
def foot_transform(origin,theta,role):
    pivot=FOOT['heel'] if role=='heel' else FOOT['toe'] if role=='toe' else [0,0,0]
    def xf(p): return add(add(origin,pivot),rotate(sub(p,pivot),T,theta))
    return {n:xf(p) for n,p in FOOT.items()},[xf(p) for p in SOLE],xf([0,0,0])
def foot(q,offset,rest):
    local=(q+offset)%1; cycle=math.floor(q+offset); root=mul(F,D*q)
    if local<.5:
        origin=add(add(rest,mul(F,D*(.25-local))),root)
        if local<.08: theta=math.radians(-10*(1-smooth(local/.08))); role='heel'
        elif local>.4: theta=math.radians(14*smooth((local-.4)/.1)); role='toe'
        else: theta=0; role='flat'
        points,sole,actual=foot_transform(origin,theta,role)
    else:
        u=(local-.5)/.5; role='air'; theta=math.radians(14-24*smooth(u))
        origin=add(add(rest,mul(F,D*(-.25+.5*smooth(u)))),root)
        _,_,outoffset=foot_transform([0,0,0],math.radians(14),'toe')
        _,_,inoffset=foot_transform([0,0,0],math.radians(-10),'heel')
        origin=add(origin,add(mul(outoffset,1-u),mul(inoffset,u)))
        origin[2]+=CONFIG['swing_clearance']*math.sin(math.pi*u)**2+CONFIG['swing_endpoint_clearance_term']*math.sin(math.pi*u)
        points,sole,actual=foot_transform(origin,theta,'flat')
    return {'phase':local,'episode':cycle,'contact':role!='air','role':role,'pitch_degrees':math.degrees(theta),'points_world':points,'sole_world':sole,'origin_world':actual,'points_pixels':{n:project(p) for n,p in points.items()},'sole_pixels':[project(p) for p in sole],'orientation_world':{'forward':rotate(F,T,theta),'transverse':T,'up':rotate([0,0,1],T,theta)}}
def pose(q):
    root=mul(F,D*q)
    # Explicit common pelvis loading. No per-leg hip correction or chain stretching.
    load=math.sin(4*math.pi*q)
    pelvis=add(root,[-CONFIG['pelvis_transfer_amplitude']*math.sin(2*math.pi*q),-5,CONFIG['pelvis_height']-CONFIG['pelvis_load_amplitude']*load])
    legs={}
    for name,offset,hipoff,rest in [('far',0,[-16,-5,0],[-12,-10,0]),('near',.5,[16,5,0],[12,0,0])]:
        ft=foot(q,offset,rest); hip=add(pelvis,hipoff); ankle=ft['points_world']['ankle']; delta=sub(ankle,hip); distance=length(delta)
        L1,L2=CONFIG['bone_lengths']
        if not abs(L1-L2)<distance<=L1+L2: raise ValueError(f'unreachable {name} phase {q}: {distance}')
        axis=unit(delta); a=(L1*L1-L2*L2+distance*distance)/(2*distance)
        bend=unit(sub(F,mul(axis,dot(F,axis))))
        knee=add(add(hip,mul(axis,a)),mul(bend,math.sqrt(max(0,L1*L1-a*a))))
        pts={'hip':hip,'knee':knee,'ankle':ankle,**{k:v for k,v in ft['points_world'].items() if k!='ankle'}}
        legs[name]={'world':pts,'pixels':{n:project(p) for n,p in pts.items()},'foot':ft,'bone_lengths':[length(sub(knee,hip)),length(sub(ankle,knee))],'projected_lengths':[length(sub(project(knee),project(hip))),length(sub(project(ankle),project(knee)))],'reach_margin':L1+L2-distance,'bend_plane_normal':unit(cross(axis,bend))}
    for leg in legs.values():
        leg['segment_frames']={}
        for label,start,end,width in [('thigh','hip','knee',20),('shin','knee','ankle',18)]:
            axis=unit(sub(leg['world'][end],leg['world'][start])); transverse=unit(sub(T,mul(axis,dot(T,axis)))); normal=unit(cross(transverse,axis))
            leg['segment_frames'][label]={'origin_world':leg['world'][start],'longitudinal':axis,'transverse':transverse,'normal':normal,'guide_width_world':width,'depth_surfaces':'unknown; axes are guide frames, not armor surface recovery'}
    # Torso is an authored anatomical guide; head angle stabilized, position follows chest.
    chest=add(pelvis,[0,0,29-.7*max(0,load)]); counter=math.radians(2*math.sin(2*math.pi*q))
    shoulders={n:add(chest,rotate(v,[0,1,0],counter)) for n,v in [('far_shoulder',[-19,-5,16]),('near_shoulder',[19,5,16])]}
    upper={'pelvis':pelvis,'chest':chest,'head':add(chest,[0,0,37]),**shoulders}
    return {'phase':q,'physical_root_world':root,'physical_root_pixels':sub(project(root),project([0,0,0])),'upper_world':upper,'upper_pixels':{n:project(p) for n,p in upper.items()},'chest_counterrotation_degrees':math.degrees(counter),'head_angle_degrees':0,'legs':legs}
def draw_pose(frame,path,world=False):
    im=Image.new('RGBA',(512 if world else 256,256),(0,0,0,0)); d=ImageDraw.Draw(im)
    root=frame['physical_root_pixels']; shift=[90,0] if world else mul(root,-1)
    def xy(p): return tuple(add(p,shift))
    for name,color in [('far',(224,177,72,255)),('near',(219,66,59,255))]:
        leg=frame['legs'][name]; p=leg['pixels']
        d.line([xy(p[n]) for n in ['hip','knee','ankle']],fill=color,width=7)
        d.polygon([xy(v) for v in leg['foot']['sole_pixels']],outline=(225,225,225,255))
        d.line([xy(p['ankle']),xy(project(leg['foot']['origin_world']))],fill=color,width=3)
        d.line([xy(p['heel']),xy(p['toe'])],fill=color,width=5)
        for n in ['hip','knee','ankle','heel','toe']:
            x,y=xy(p[n]); d.ellipse((x-2,y-2,x+2,y+2),fill=(255,255,255,255))
        d.text((5,10 if name=='far' else 25),name+': '+leg['foot']['role'],fill=color)
    u=frame['upper_pixels']; d.line([xy(u['pelvis']),xy(u['chest']),xy(u['head'])],fill=(77,191,213),width=12)
    d.line([xy(u['far_shoulder']),xy(u['near_shoulder'])],fill=(77,191,213),width=8)
    d.text((5,240),f"phase {frame['phase']:.4f} | authored 3D guide",fill='white')
    im.save(path); return im

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); a=ap.parse_args(); out=Path(a.output)
    if out.exists(): raise ValueError('Refusing existing output')
    out.mkdir(parents=True)
    frames=[]; errors=[]; margins=[]; minsole=1e9; maxbone=0
    for i in range(1441):
        f=pose(i/1440); margins += [v['reach_margin'] for v in f['legs'].values()]
        for v in f['legs'].values():
            maxbone=max(maxbone,abs(v['bone_lengths'][0]-42),abs(v['bone_lengths'][1]-48))
            minsole=min(minsole,min(p[2] for p in v['foot']['sole_world']))
    for i in range(72):
        f=pose(i/72); f['index']=i; f['duration_ms']=round((i+1)*1200/72)-round(i*1200/72); f['source_tick']=i; frames.append(f)
    ims=[]; moving=[]
    for f in frames:
        ims.append(draw_pose(f,out/f"{f['index']:03}.png")); moving.append(draw_pose(f,out/f"moving-{f['index']:03}.png",True))
    ims[0].save(out/'loop-in-place.gif',save_all=True,append_images=ims[1:],duration=[10*(round((i+1)*120/72)-round(i*120/72)) for i in range(72)],loop=0,disposal=2)
    moving[0].save(out/'loop-moving.gif',save_all=True,append_images=moving[1:],duration=[10*(round((i+1)*120/72)-round(i*120/72)) for i in range(72)],loop=0,disposal=2)
    sheet=Image.new('RGBA',(256*4,256*2),(38,43,50,255));
    for j,i in enumerate(range(0,72,9)): sheet.alpha_composite(ims[i],((j%4)*256,(j//4)*256))
    sheet.resize((2048,1024),Image.Resampling.NEAREST).save(out/'eight-keys-2x.png')
    source=HERE/'source/master-256.png'
    packet={'schema':'captain.authored_3d_pose_guides.v1','scope':'Anatomical projection diagnostic, no recovered 3D anatomy, armor surface or artistic approval','camera':CAM,'clock':{'fps':60,'frame_count':72,'duration_ms':1200,'loop_endpoint_excluded':True},'dimensions':{'femur':42,'tibia':48,'foot_forward_length':28,'foot_width':16,'ankle_height':24/math.cos(E),'stride_world':mul(F,D)},'neutral_bind':pose(0),'source_upper_registration':{'source_pivot_pixels':[130,125],'model_bind_pelvis_pixels':pose(0)['upper_pixels']['pelvis'],'rule':'one fixed rest offset; motion follows projected pelvis delta; no per-cell fitting'},'frames':frames,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'builder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'design_sha256':hashlib.sha256((HERE/'design.json').read_bytes()).hexdigest(),'design':CONFIG}
    (out/'poses.json').write_text(json.dumps(packet,indent=2))
    for policy in ['in_place','physical']:
        spec={'schema':'motion-audition/v1','name':'Authored 3D skeletal diagnostic / NOT ART','canvas':[256,256],'stage':[768,656],'origin':[160,80],'camera':'fixed','root_stride':sub(project(mul(F,D)),project([0,0,0])),'root_policy':policy,'cycle_ms':1200,'frames':[]}
        for f in frames:
            file=f"{f['index']:03}.png"
            spec['frames'].append({'index':f['index'],'file':file,'sha256':hashlib.sha256((out/file).read_bytes()).hexdigest(),'duration_ms':f['duration_ms'],'phase_label':f"3D phase {f['phase']:.4f}",'physical_root':f['physical_root_pixels']})
        (out/f'audition-{policy}.json').write_text(json.dumps(spec,indent=2))
    (out/'geometry-check.json').write_text(json.dumps({'sample_count':1441,'min_reach_margin':min(margins),'max_bone_length_error':maxbone,'min_sole_world_height':minsole,'render_scope':'diagnostic skeleton only; palette/armor art not tested'},indent=2))
    print(json.dumps({'output':str(out),'minimum_reach_margin':min(margins),'min_sole_height':minsole}))
if __name__=='__main__': main()

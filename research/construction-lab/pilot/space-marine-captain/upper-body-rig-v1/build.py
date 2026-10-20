"""Source ownership and upper-body animation. No per-frame AI redraw.

Visible art is source-bound. Hidden joint backing is explicitly new construction.
"""
from pathlib import Path
import json, math, hashlib, argparse, importlib.util
from PIL import Image, ImageDraw, ImageChops

ROOT=Path(__file__).resolve().parent
SIZE=(256,256)
spec=importlib.util.spec_from_file_location('pixel_affine',ROOT/'pixel_affine.py')
pixel_affine=importlib.util.module_from_spec(spec);spec.loader.exec_module(pixel_affine)


def polygon(points):
    m=Image.new('L',SIZE);ImageDraw.Draw(m).polygon(points,fill=255);return m


def masked(im,mask):
    out=im.copy();out.putalpha(ImageChops.multiply(im.getchannel('A'),mask))
    out.putdata([p if p[3]else(0,0,0,0)for p in out.get_flattened_data()]);return out


def point(p,origin,target,angle):
    a=math.radians(angle);c,s=math.cos(a),math.sin(a)
    x,y=p[0]-origin[0],p[1]-origin[1]
    return(target[0]+c*x-s*y,target[1]+s*x+c*y)


def rigid(im,origin,target,angle):
    a=math.radians(angle);c,s=math.cos(a),math.sin(a)
    ox,oy=origin;tx,ty=target
    return im.transform(SIZE,Image.Transform.AFFINE,
        (c,s,ox-c*tx-s*ty,-s,c,oy+s*tx-c*ty),
        resample=Image.Resampling.NEAREST,fillcolor=(0,0,0,0))


def construct():
    design=json.loads((ROOT/'design.json').read_text())
    source_path=ROOT/design['source'];source_bytes=source_path.read_bytes()
    assert hashlib.sha256(source_bytes).hexdigest()==design['source_sha256']
    src=Image.open(source_path).convert('RGBA')
    keep=polygon([(0,0),(255,0),(255,design['top_keep_y']-1),(0,design['top_keep_y']-1)])
    for points in design['foreground_polygons'].values():
        keep=ImageChops.lighter(keep,polygon(points))
    upper=masked(src,keep);used=Image.new('L',SIZE);parts={}
    for name in design['source_ownership_priority']:
        m=ImageChops.subtract(polygon(design['part_polygons'][name]),used)
        m=ImageChops.multiply(m,keep);used=ImageChops.lighter(used,m)
        parts[name]=masked(src,m)
    parts['torso_pack']=masked(upper,ImageChops.invert(used))
    recomposed=Image.new('RGBA',SIZE)
    for im in parts.values():recomposed.alpha_composite(im)
    assert recomposed.tobytes()==upper.tobytes(),'Source ownership changed visible pixels'
    out=ROOT/'parts';out.mkdir(exist_ok=True)
    for name,im in parts.items():im.save(out/(name+'.png'))
    upper.save(ROOT/'upper-rest.png')
    (ROOT/'partition-proof.json').write_text(json.dumps({
        'source_sha256':design['source_sha256'],'upper_visible_rgba_exact':True,
        'parts':{name:{'file':'parts/'+name+'.png','bbox':im.getbbox(),
                      'solid_pixels':sum(p[3]==255 for p in im.get_flattened_data())}
                 for name,im in parts.items()},
        'limitation':'Legs intentionally removed; hidden joint underlap not in this exact partition.'},indent=2)+'\n')
    return design,parts


def render_parts(design,parts,phase,pelvis,lean=None):
    if lean is None:lean=0.65*math.sin(phase*2*math.pi)
    pivot=design['pelvis_pivot'];target=pelvis
    result={};landmarks={}
    weighted=design.get('motion_profile','compact')=='weighted'
    # Newly drawn hidden dark-red/black shoulder/neck/cuff overlaps. Foreground
    # source art overlays them; slight carry rotations cannot expose empty holes.
    backing=Image.new('RGBA',SIZE);d=ImageDraw.Draw(backing)
    d.polygon([(99,80),(114,77),(125,95),(117,110),(101,100)],fill=(34,17,22,255))
    d.polygon([(132,79),(153,77),(164,95),(154,105),(136,99)],fill=(32,20,24,255))
    d.polygon([(154,102),(177,94),(186,123),(174,151),(156,143)],fill=(58,18,24,255))
    result['joint_backing']=rigid(backing,pivot,target,lean)
    for name,im in parts.items():
        method=design.get('rotation_method','nearest')
        renderer=pixel_affine.affine if method=='scale2x8-approximation' else rigid
        if name=='torso_pack':result[name]=renderer(im,pivot,target,lean);continue
        origin=design['pivots'][name]
        attached=point(origin,pivot,target,lean)
        angle=lean
        if name=='arm_sword':
            angle+=(-4+3*math.sin(2*math.pi*(phase-0.18))) if weighted else 1.25*math.sin(2*math.pi*(phase-0.06))
        if name=='shield':angle+=(1.8 if weighted else 0.9)*math.sin(2*math.pi*(phase-(0.20 if weighted else 0.12)))
        if name=='head':angle=0 # World-stabilized gaze; preserve face clusters.
        if name=='tabard':angle+=1.8*math.sin(2*math.pi*(phase-0.13))
        if name=='cape':
            shear=(0.14 if weighted else 0.075)*math.sin(2*math.pi*(phase-(0.23 if weighted else 0.20)))
            if method=='nearest':
                im=im.transform(SIZE,Image.Transform.AFFINE,
                                (1,0,0,-shear,1,shear*origin[0]),
                                resample=Image.Resampling.NEAREST)
            angle+=(1.8 if weighted else 0.6)*math.sin(2*math.pi*(phase-(0.25 if weighted else 0.18)))
        if name=='cape' and method=='scale2x8-approximation':
            result[name]=renderer(im,origin,attached,angle,shear=shear)
        else:result[name]=renderer(im,origin,attached,angle)
        landmarks[name]={'pivot':attached,'angle_clockwise_degrees':angle}
    return result,landmarks


def main():
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');args=p.parse_args()
    design,parts=construct()
    if args.preview:
        out=ROOT/'upper-motion';out.mkdir(exist_ok=True)
        atlas=Image.new('RGBA',(1024,768))
        for i in range(12):
            phase=i/12;pelvis=(130+0.7*math.sin(2*math.pi*phase),143+1.7*math.cos(4*math.pi*phase))
            posed,marks=render_parts(design,parts,phase,pelvis)
            frame=Image.new('RGBA',SIZE)
            for name in ['cape','joint_backing','arm_sword','torso_pack','head','tabard','shield']:
                frame.alpha_composite(posed[name])
            frame.save(out/f'{i:02}.png');atlas.paste(frame,((i%4)*256,(i//4)*256))
        atlas.save(ROOT/'upper-motion-atlas.png')
    print(json.dumps({'parts':len(parts),'source_partition_exact':True,'path':str(ROOT)}))


if __name__=='__main__':main()

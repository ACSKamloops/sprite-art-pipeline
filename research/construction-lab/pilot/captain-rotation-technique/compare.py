"""Fixed-origin RGBA rotation comparison; stdlib + Pillow, no fitting/recentering."""
from pathlib import Path
import math,json,hashlib,argparse
from PIL import Image,ImageDraw,__version__ as pillow_version
ROOT=Path(__file__).resolve().parent
PIVOT=(100,169);ANGLES=(-30,-15,0,15,30)
sha=lambda b:hashlib.sha256(b).hexdigest()
def scale2x(im):
    """Exact tuple equality EPX/Scale2x; boundary neighbour is center pixel."""
    w,h=im.size;p=im.load();out=Image.new('RGBA',(w*2,h*2));q=out.load()
    for y in range(h):
        for x in range(w):
            e=p[x,y];b=p[x,y-1]if y else e;d=p[x-1,y]if x else e
            f=p[x+1,y]if x+1<w else e;v=p[x,y+1]if y+1<h else e
            a=c=g=i=e
            if b!=v and d!=f:
                a=d if d==b else e;c=f if b==f else e
                g=d if d==v else e;i=f if v==f else e
            q[x*2,y*2]=a;q[x*2+1,y*2]=c;q[x*2,y*2+1]=g;q[x*2+1,y*2+1]=i
    return out

def rotate(im,angle,pivot):
    # Positive is counterclockwise on screen. Inverse source sampling in
    # boundary-coordinate space: pixel centers are (x+.5,y+.5).
    t=math.radians(angle);c=math.cos(t);s=math.sin(t);px,py=pivot
    return im.transform(im.size,Image.Transform.AFFINE,(c,-s,px-c*px+s*py,s,c,py-s*px-c*py),resample=Image.Resampling.NEAREST,fillcolor=(0,0,0,0))

def pixels(im):return list(im.get_flattened_data())
def render(im,method,angle,expanded=None):
    if method=='nearest':return rotate(im,angle,PIVOT)
    if expanded is None:
        expanded=im
        for _ in range(3):expanded=scale2x(expanded)
    return rotate(expanded,angle,tuple(v*8 for v in PIVOT)).resize(im.size,Image.Resampling.NEAREST)

def run(out):
    if out.exists():raise ValueError('Refuse existing output; use a fresh directory')
    path=ROOT/'source/right_shin.png';provenance=json.loads((ROOT/'source/provenance.json').read_text())
    if sha(path.read_bytes())!=provenance['source_part_sha256']:raise ValueError('Stale source part')
    out.mkdir(parents=True);im=Image.open(path).convert('RGBA');source=pixels(im);palette=set(source)
    enlarged=im
    for _ in range(3):enlarged=scale2x(enlarged)
    checks=[];records=[];imgs={}
    for method in ['nearest','scale2x8-approximation']:
        for angle in ANGLES:
            img=render(im,method,angle,enlarged);again=render(im,method,angle,enlarged);data=pixels(img)
            fname=f'{method}-{angle:+03}.png';img.save(out/fname);imgs[method,angle]=img
            unseen=set(data)-palette;changed=sum(a!=b for a,b in zip(data,source))
            r={'method':method,'degrees':angle,'png':fname,'rgba_sha256':sha(img.tobytes()),'png_sha256':sha((out/fname).read_bytes()),'repeat_RGBA_exact':img.tobytes()==again.tobytes(),'new_RGBA_colours':len(unseen),'opaque_bbox':img.getchannel('A').getbbox(),'nonzero_alpha_pixels':sum(p[3]!=0 for p in data),'changed_pixels_vs_original':changed,'zero_degree_exact_identity':changed==0 if angle==0 else None}
            records.append(r);checks.extend([r['repeat_RGBA_exact'],not unseen]);
            if angle==0:checks.append(r['zero_degree_exact_identity'])
    differences={str(a):sum(p!=q for p,q in zip(pixels(imgs['nearest',a]),pixels(imgs['scale2x8-approximation',a])))for a in ANGLES}
    # Fixed256canvas retained in each cell; nearest-display2x only.
    sheet=Image.new('RGB',(5*512,2*550),(28,30,37));draw=ImageDraw.Draw(sheet)
    for row,method in enumerate(['nearest','scale2x8-approximation']):
        for col,angle in enumerate(ANGLES):
            x=col*512;y=row*550;layer=imgs[method,angle].resize((512,512),Image.Resampling.NEAREST)
            sheet.paste(layer,(x,y+30),layer);draw.text((x+8,y+8),f'{method} {angle:+} deg',fill='white')
            # Pivot is a guide outside exported part imagery.
            px=x+PIVOT[0]*2;py=y+30+PIVOT[1]*2;draw.line((px-6,py,px+6,py),fill=(255,80,150));draw.line((px,py-6,px,py+6),fill=(255,80,150))
    sheet.save(out/'comparison-2x.png')
    # Focused4x crop still fixed same rectangle for every angle/method.
    crop=(40,140,145,245);detail=Image.new('RGB',(5*420,2*446),(28,30,37));d=ImageDraw.Draw(detail)
    for row,method in enumerate(['nearest','scale2x8-approximation']):
        for col,angle in enumerate(ANGLES):
            patch=imgs[method,angle].crop(crop).resize((420,420),Image.Resampling.NEAREST);detail.paste(patch,(col*420,row*446+26),patch);d.text((col*420+4,row*446+5),f'{method} {angle:+}',fill='white')
    detail.save(out/'detail-4x.png')
    report={'schema':'fixed-pivot-rotation-technique/v1','source_png_sha256':sha(path.read_bytes()),'source_RGBA_sha256':sha(im.tobytes()),'approved_reference_sha256':provenance['approved_reference_sha256'],'canvas':[256,256],'pivot_boundary_coordinates':PIVOT,'angle_convention':'positive counterclockwise screen, fixed canvas and source origin, no fit/recenter','algorithm':'Scale2x repeated3 times→nearest affine rotation at8x pivot→nearest downsample; approximation, not full Aseprite RotSprite','implementation_sha256':sha(Path(__file__).read_bytes()),'Pillow':pillow_version,'source_RGBA_colours':len(palette),'checks_passed':all(checks),'records':records,'method_RGBA_difference_pixels':differences,'limitations':['No hidden geometry reconstructed','No palette restriction imposed on actual1745-colour RGBA target','No anatomical gait or temporal acceptance','Fixedcanvas can clip other parts or pivots; this part stays internal at sampledangles']}
    (out/'diagnostics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':all(checks),'method_difference_pixels':differences,'source_colours':len(palette)}))
    if not all(checks):raise SystemExit(2)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'results');args=p.parse_args();run(args.output)

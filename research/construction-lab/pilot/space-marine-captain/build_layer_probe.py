"""Experimental source-pixel articulation. This is NOT an accepted animation.

No image reconstruction or hidden anatomy is claimed. Exclusive masks reassemble
the original RGBA exactly. Small joint backings are explicitly new authored pixels.
Rerun from any directory: python build_layer_probe.py.
"""
from pathlib import Path
import hashlib, json, math
import argparse
from PIL import Image, ImageDraw, ImageChops

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'layer-probe'
SOURCE = ROOT / 'references/approved-256.png'
SIZE = (256, 256)


def poly(points):
    m = Image.new('L', SIZE); ImageDraw.Draw(m).polygon(points, fill=255)
    return m


def part(source, mask):
    out = source.copy()
    out.putalpha(ImageChops.multiply(source.getchannel('A'), mask))
    # Transparent RGB is irrelevant to displayed RGBA but normalized for exports.
    pixels = list(out.get_flattened_data())
    out.putdata([(r, g, b, a) if a else (0, 0, 0, 0) for r, g, b, a in pixels])
    return out


def transform(layer, origin, target, angle):
    # PIL expects inverse mapping. One shared canvas; never fit or recenter a pose.
    a = math.radians(angle); c, s = math.cos(a), math.sin(a)
    ox, oy = origin; tx, ty = target
    return layer.transform(SIZE, Image.Transform.AFFINE,
        (c, s, ox-c*tx-s*ty, -s, c, oy+s*tx-c*ty),
        resample=Image.Resampling.NEAREST)


def vector_angle(a, b):
    return math.degrees(math.atan2(b[1]-a[1], b[0]-a[0]))


def solve_knee(hip, ankle, lengths, side):
    x, y = ankle[0]-hip[0], ankle[1]-hip[1]
    dist = math.hypot(x, y)
    if dist >= sum(lengths) or dist <= abs(lengths[0]-lengths[1]):
        raise ValueError('Unreachable declared ankle: '+str((hip, ankle, lengths)))
    along = (lengths[0]**2-lengths[1]**2+dist**2)/(2*dist)
    offset = math.sqrt(max(0, lengths[0]**2-along**2))
    return (hip[0]+x/dist*along-side*y/dist*offset,
            hip[1]+y/dist*along+side*x/dist*offset)


def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--separate-boots',action='store_true',
                        help='Counter-test: boot pixels have independent ankle transforms')
    parser.add_argument('--output',type=Path,help='Fresh output directory; rejects existing paths')
    args=parser.parse_args()
    if args.separate_boots: OUT=ROOT/'boot-constraint-probe'
    if args.output:
        if args.output.exists(): raise FileExistsError('Output already exists: '+str(args.output))
        OUT=args.output
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'parts').mkdir(exist_ok=True)
    (OUT/'frames').mkdir(exist_ok=True)
    source = Image.open(SOURCE).convert('RGBA')
    # Anatomical right leg is screen-left; anatomical left is screen-right.
    polygons = {
        'right_shin': [(93,155),(108,157),(114,170),(111,190),
            (109,209),(101,220),(91,218),(88,224),(68,225),(65,216),
            (77,192),(86,177),(87,163)],
        'right_thigh': [(104,136),(115,139),(118,150),(114,164),
            (105,172),(94,164),(93,153),(99,142)],
        'left_shin': [(147,169),(162,173),(177,186),(187,201),
            (199,220),(198,234),(192,241),(177,242),(164,231),
            (157,211),(155,196),(152,182)],
        'left_thigh': [(135,153),(146,151),(161,165),(169,181),
            (163,190),(149,181),(143,173)],
    }
    # Foreground tabard + shield/cape remain in the original body layer.
    foreground = poly([(111,133),(132,134),(144,153),(153,178),
                       (159,192),(146,197),(131,194),(125,203),
                       (118,202),(116,189),(111,174),(108,157)])
    foreground = ImageChops.lighter(foreground, poly([
        (174,89),(192,106),(195,125),(206,139),(240,140),
        (249,175),(221,190),(203,199),(181,198),(162,178),
        (150,158),(146,139),(148,126),(145,112)]))
    used = Image.new('L', SIZE)
    layers = {}
    for name, points in polygons.items():
        m = ImageChops.subtract(poly(points), foreground)
        m = ImageChops.subtract(m, used)
        used = ImageChops.lighter(used, m)
        layers[name] = part(source, m)
    layers['body'] = part(source, ImageChops.invert(used))
    if args.separate_boots:
        boot_polygons={
            'right':[(79,198),(94,201),(100,207),(108,206),(109,215),
                     (98,221),(89,224),(69,225),(65,217),(71,206)],
            'left':[(166,209),(180,208),(190,216),(198,225),(199,237),
                    (191,243),(175,242),(162,234),(160,221)],
        }
        for side,points in boot_polygons.items():
            mask=poly(points)
            shin=layers[side+'_shin']
            layers[side+'_boot']=part(shin,mask)
            layers[side+'_shin']=part(shin,ImageChops.invert(mask))
    for name, im in layers.items(): im.save(OUT/'parts'/f'{name}.png')
    # Partition check includes all visible original pixels; exclusive layers.
    reconstructed = Image.new('RGBA', SIZE)
    for layer in layers.values(): reconstructed.alpha_composite(layer)
    orig_visible = part(source, Image.new('L', SIZE, 255))
    if reconstructed.tobytes() != orig_visible.tobytes():
        raise AssertionError('Source partition changed pixels')
    reconstructed.save(OUT/'source-reassembled.png')
    rigs = {
        'right': {'hip': (112,145), 'knee': (100,169),
                  'ankle': (84,207), 'neutral': (105,201), 'bend': -1},
        'left': {'hip': (147,160), 'knee': (158,184),
                 'ankle': (176,222), 'neutral': (167,216), 'bend': -1},
    }
    all_frames = []; records = []
    for i in range(12):
        phase = i/12
        bob = round(1.5*math.cos(phase*4*math.pi))
        frame = Image.new('RGBA', SIZE)
        landmarks = {}
        # Right contact at zero, left contact half a cycle later. Each stance
        # travels back along a fixed ground vector; swing follows the return arc.
        for side in ('left','right'):
            rig = rigs[side]; t=(phase+(0.5 if side=='left' else 0))%1
            if t < 0.6:
                along = 1-2*t/0.6; lift = 0; contact=True
            else:
                swing=(t-0.6)/0.4
                along=-math.cos(swing*math.pi)
                lift=8*math.sin(swing*math.pi); contact=False
            ankle=(rig['neutral'][0]-10*along,
                   rig['neutral'][1]+6*along-lift)
            hip=(rig['hip'][0],rig['hip'][1]+bob)
            lengths=(math.dist(rig['hip'],rig['knee']),
                     math.dist(rig['knee'],rig['ankle']))
            knee=solve_knee(hip, ankle, lengths, rig['bend'])
            thigh_angle=vector_angle(hip,knee)-vector_angle(rig['hip'],rig['knee'])
            shin_angle=vector_angle(knee,ankle)-vector_angle(rig['knee'],rig['ankle'])
            # Small black/red joint backings are construction pixels, not a
            # recovered hidden thigh. Foreground source body overlays these.
            d=ImageDraw.Draw(frame)
            d.line([hip,knee,ankle],fill=(36,17,21,255),width=10)
            d.ellipse((knee[0]-5,knee[1]-5,knee[0]+5,knee[1]+5),fill=(46,20,24,255))
            frame.alpha_composite(transform(layers[side+'_thigh'],rig['hip'],hip,thigh_angle))
            frame.alpha_composite(transform(layers[side+'_shin'],rig['knee'],knee,shin_angle))
            if args.separate_boots:
                # A separate ankle keeps the original sole pitch. This is a
                # counter-test, not a final heel/toe roll/contact solution.
                frame.alpha_composite(transform(layers[side+'_boot'],rig['ankle'],ankle,0))
            landmarks[side]={'hip':hip,'knee':knee,'ankle_target':ankle,
                'declared_stance':contact,'thigh_degrees':thigh_angle,
                'shin_degrees':shin_angle,
                'boot_degrees':0 if args.separate_boots else shin_angle}
        # Identity, heraldry, face, sword and shield use source pixels unchanged.
        frame.alpha_composite(transform(layers['body'],(0,0),(0,bob),0))
        filename=f'frames/{i:02}.png';frame.save(OUT/filename)
        all_frames.append(frame)
        records.append({'frame':i,'file':filename,'duration_ms':100,
                        'body_bob_px':bob,'landmarks':landmarks,
                        'sha256':hashlib.sha256((OUT/filename).read_bytes()).hexdigest()})
    atlas=Image.new('RGBA',(256*4,256*3))
    for i,frame in enumerate(all_frames): atlas.paste(frame,((i%4)*256,(i//4)*256))
    atlas.save(OUT/'walk-atlas.png')
    # GIF is only a convenience; full-alpha PNG frames are authoritative.
    previews=[]
    for frame in all_frames:
        bg=Image.new('RGBA',SIZE,(38,43,49,255));bg.alpha_composite(frame)
        previews.append(bg.convert('RGB').resize((512,512),Image.Resampling.NEAREST))
    previews[0].save(OUT/'walk-preview.gif',save_all=True,append_images=previews[1:],
                     duration=100,loop=0,disposal=2)
    manifest={'schema':'captain-layer-probe-v1','status':'UNAPPROVED_EXPERIMENT',
        'independent_boot_transforms':args.separate_boots,
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'canvas':SIZE,'cycle_ms':1200,'direction':'approved_three_quarter',
        'new_pixels':'Explicit dark knee/hip backing only; missing views/anatomy not recovered.',
        'source_partition_exact_rgba':True,'part_polygons':polygons,
        'rig':rigs,'frames':records,
        'limits':['Rigid source-pixel rotations alter pixel clusters.',
                  'Thigh art is incomplete; source only exposes small fragments.',
                  'Body pose remains source sword-raised silhouette.',
                  'Ground sole/contact not yet measured; targets are not proof.',
                  'No art acceptance, extra views or full action pack.']}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'output':str(OUT),'frames':12,
                     'partition_exact_rgba':True,'status':manifest['status']}))


if __name__=='__main__': main()

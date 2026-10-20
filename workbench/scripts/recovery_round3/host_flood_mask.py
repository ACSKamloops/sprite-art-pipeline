#!/usr/bin/env python3
"""Offline Pixelorama HOST manual selector: unchanged recovered flood methods.
Produces only a mask+receipt. Not PixelLab automatic/background/animation cutout.
"""
import argparse,hashlib,io,json,math,os,re,struct,subprocess,tempfile
from pathlib import Path
from PIL import Image

RESEARCH=Path('/home/astra/projects/pixellab-local-test-20261011')
SOURCE_PINS={
 'pixelorama-recovered/src/Classes/FloodFillObject.gd':'63f7320fbb151e1959265a8e1331c341cefaf6511c1975e69df1ccf515c15cb7',
 'pixelorama-recovered/src/Autoload/DrawingAlgos.gd':'6acef5d413bdf0e7685b7d034bb65885d40b884d6cee60869065052980ec61a9'}
GODOT=Path('/home/astra/.local/bin/godot')
sha=lambda b:hashlib.sha256(b).hexdigest()
# Appended declarations resolve host types/state without changing source bodies.
FIXTURES='''
class SelectionMap:
\tfunc get_selection_rect(_project) -> Rect2i: return Rect2i()
class Project:
\tvar size: Vector2i
\tvar has_selection = false
\tvar selection_map = SelectionMap.new()
\tfunc can_pixel_get_drawn(_p): return false
var DrawingAlgos = load("res://similar.gd").new()
'''
def run(args):
    source_path=args.image.resolve(strict=True)
    if not source_path.is_file()or source_path.stat().st_size>4*1024*1024:raise ValueError('Input must be a PNG file of at most4MiB')
    raw=source_path.read_bytes()
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Only PNG input accepted')
    if len(raw)<33 or raw[12:16]!=b'IHDR':raise ValueError('Invalid PNG header')
    w,h=struct.unpack('>II',raw[16:24])
    if not(1<=w<=512 and 1<=h<=512):raise ValueError('Image dimensions must each be1..512; maximum262144 pixels')
    with Image.open(io.BytesIO(raw))as header:
        assert header.size==(w,h)
        png_mode=header.mode
    if not(0<=args.seed_x<w and 0<=args.seed_y<h):raise ValueError('Seed must lie inside input image')
    if not math.isfinite(args.tolerance)or not 0<=args.tolerance<=1:raise ValueError('Tolerance must be finite normalized RGBA value0..1')
    sources={}
    for relative,pin in SOURCE_PINS.items():
        content=(RESEARCH/relative).read_bytes()
        if sha(content)!=pin:raise ValueError('Recovered source pin changed: '+relative)
        sources[relative]=content.decode()
    flood=sources['pixelorama-recovered/src/Classes/FloodFillObject.gd']
    drawing=sources['pixelorama-recovered/src/Autoload/DrawingAlgos.gd']
    similar=re.search(r'^func similar_colors\(.*?(?=^func |\Z)',drawing,re.M|re.S).group()
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    # Snapshot verified bytes, eliminating source-file changes between validation/decode.
    with tempfile.TemporaryDirectory(prefix='host-selector-',dir=out)as tmp:
        t=Path(tmp);(t/'input.png').write_bytes(raw)
        (t/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Recovered host manual selector"\n')
        (t/'flood.gd').write_text(flood+FIXTURES)
        (t/'similar.gd').write_text('extends RefCounted\n\n'+similar)
        main='''extends SceneTree
var segments_count=0
func collect(target,segments):
    segments_count=segments.size()
    for s in segments:
        target.fill_rect(Rect2i(s.left_position,s.y,s.right_position-s.left_position+1,1),Color.WHITE)
func _init():
    var image=Image.load_from_file("res://input.png")
    assert(not image.is_empty())
    var decoded_format=image.get_format()
    if decoded_format!=Image.FORMAT_RGBA8: image.convert(Image.FORMAT_RGBA8)
    var before=image.get_data()
    var ff=load("res://flood.gd").new()
    var project=ff.Project.new()
    project.size=image.get_size()
    ff.tolerance=__TOLERANCE__
    var mask=Image.create(image.get_width(),image.get_height(),false,Image.FORMAT_RGBA8)
    mask.fill(Color.TRANSPARENT)
    ff.flood_fill(Vector2i(__X__,__Y__),image,mask,project,Callable(self,"collect"))
    assert(image.get_data()==before)
    assert(mask.save_png(__MASK_PATH__)==OK)
    var data=mask.get_data()
    var count=0
    for i in range(3,data.size(),4):
        if data[i]>0: count+=1
    var seed=image.get_pixel(__X__,__Y__)
    print("SELECTOR_OK "+JSON.stringify({"width":image.get_width(),"height":image.get_height(),"selected_pixels":count,"segments":segments_count,"decoded_format_before_rgba8":decoded_format,"source_image_unchanged":true,"seed_normalized_rgba":[seed.r,seed.g,seed.b,seed.a]}))
    quit(0)
'''
        replacements={'__TOLERANCE__':json.dumps(args.tolerance),'__X__':str(args.seed_x),'__Y__':str(args.seed_y),'__MASK_PATH__':json.dumps(str(out/'mask.png'))}
        for key,value in replacements.items():main=main.replace(key,value)
        (t/'selector_main.gd').write_text(main)
        env={k:v for k,v in os.environ.items()if k in ['PATH','HOME','LANG']};env['XDG_DATA_HOME']=str(t/'userdata')
        try:
            result=subprocess.run([str(GODOT),'--headless','--quit-after','1800','--path',tmp,'--script','res://selector_main.gd'],env=env,text=True,capture_output=True,timeout=60)
        except subprocess.TimeoutExpired:
            (out/'FAILURE.json').write_text(json.dumps({'status':'timeout','timeout_seconds':60,'no_api_calls':True})+'\n');raise ValueError('Original-method execution exceeded60 seconds')
        lines=[line[len('SELECTOR_OK '):]for line in result.stdout.splitlines()if line.startswith('SELECTOR_OK ')]
        if result.returncode or len(lines)!=1:
            (out/'FAILURE.json').write_text(json.dumps({'status':'execution-failed','returncode':result.returncode,'stdout':result.stdout[:4000],'stderr':result.stderr[:4000]})+'\n');raise ValueError('Original-method execution failed; see FAILURE.json')
        observed=json.loads(lines[0]);mask_bytes=(out/'mask.png').read_bytes()
        receipt=dict(classification='source-exact-recovered-pixelorama-host-manual-selector',input_path=str(source_path),input_png_sha256=sha(raw),input_png_bytes=len(raw),input_png_mode=png_mode,seed_xy=[args.seed_x,args.seed_y],tolerance_normalized_rgba=args.tolerance,output_mask='mask.png',output_mask_png_sha256=sha(mask_bytes),mask_convention='Selected=[255,255,255,255]; unselected=[255,255,255,0] (transparent white). Consume mask alpha as selection. Source is never cleared/forced opaque.',original_source_pins=SOURCE_PINS,similar_colors_function_sha256=sha(similar.encode()),harness_sha256=sha(Path(__file__).read_bytes()),engine=result.stdout.splitlines()[0],observed=observed,stderr=result.stderr,limits=dict(max_side=512,max_pixels=262144,max_input_bytes=4194304,max_runtime_seconds=60,fresh_output_directory=True),fixture_stubs=['Project.size from decoded PNG','Project.has_selection=false; selection bounds unexercised','SelectionMap.get_selection_rect fixture; unexercised','Project.can_pixel_get_drawn fixture; unexercised','DrawingAlgos instance uses unchanged original similar_colors method','Callback paints emitted original segment spans white'],wrapper_operations=['Input PNG header/size/seed/tolerance/pin guards','Godot decode,convert to RGBA8 if needed','Verified input byte snapshot','Mask allocation and original-segment sink','PNG saving and receipt hashing'],equivalence_boundary='Whole recovered FloodFill source unchanged plus appended fixture declarations; recovered source replay, not compiled GDC equivalence. No editor undo/tilemaps/active selection, automatic background detection, PixelLab service or animation parity.',provider_calls=0)
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        return {'mask':str(out/'mask.png'),'receipt':str(out/'receipt.json'),'selected_pixels':observed['selected_pixels'],'provider_calls':0}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,required=True);parser.add_argument('--seed-x',type=int,required=True);parser.add_argument('--seed-y',type=int,required=True);parser.add_argument('--tolerance',type=float,required=True,help='Normalized source RGBA tolerance0..1; original float semantics, not an integer color-distance rule')
    parser.add_argument('--output-dir',type=Path,required=True,help='Must not already exist')
    args=parser.parse_args()
    try:print(json.dumps(run(args),indent=2))
    except (ValueError,OSError)as exc:parser.exit(2,str(exc)+'\n')
if __name__=='__main__':main()

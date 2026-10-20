"""Execute unchanged recovered host FloodFillObject + original similar_colors.
No provider/network code. Project and segment sink are isolated local fixtures.
"""
import base64,hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
import numpy as np
from PIL import Image
RESEARCH=Path('/home/astra/projects/pixellab-local-test-20261011')
OUT=Path(__file__).resolve().parents[2]/'docs/recovery-round3-20261014'
sha=lambda b:hashlib.sha256(b).hexdigest()
flood_path=RESEARCH/'pixelorama-recovered/src/Classes/FloodFillObject.gd'
drawing_path=RESEARCH/'pixelorama-recovered/src/Autoload/DrawingAlgos.gd'
assert sha(flood_path.read_bytes())=='63f7320fbb151e1959265a8e1331c341cefaf6511c1975e69df1ccf515c15cb7'
assert sha(drawing_path.read_bytes())=='6acef5d413bdf0e7685b7d034bb65885d40b884d6cee60869065052980ec61a9'
flood=flood_path.read_text();drawing=drawing_path.read_text()
sim=re.search(r'^func similar_colors\(.*?(?=^func |\Z)',drawing,re.M|re.S).group()
fixtures='''
# LOCAL HARNESS ONLY: no editor selection, no host mutation/undo integration.
class SelectionMap:
\tfunc get_selection_rect(_project) -> Rect2i: return Rect2i()
class Project:
\tvar size: Vector2i
\tvar has_selection = false
\tvar selection_map = SelectionMap.new()
\tfunc can_pixel_get_drawn(_p): return false
var DrawingAlgos = load("res://similar.gd").new()
'''
inputs=[Path('/home/astra/artifacts/pixellab-cutout-characterization-20261014/inputs/opaque.png'),Path('/home/astra/artifacts/pixellab-cutout-characterization-20261014/inputs/alpha-patches.png'),Path('/home/astra/artifacts/pixellab-cutout-connectivity-20261014/inputs/connectivity-rgba.png')]
for path,pin in zip(inputs,['96816d261e63f65f5a25a6da9e890c79888b03cf316f91db2a2695c3fa53e4ba','93cade3423b49a1dd5cd93dddfb52632d7467576efa29ea55b664732424954f9','f8929723b17cdc39254ced84549817f4c36f9a71a7d66958f13bf27b1f566338']):assert sha(path.read_bytes())==pin
main='''extends SceneTree
func capture(target, segments):
    for segment in segments:
        target.fill_rect(Rect2i(segment.left_position,segment.y,segment.right_position-segment.left_position+1,1),Color.WHITE)
func _init():
    var helper=load("res://similar.gd").new()
    assert(not helper.similar_colors(Color(0,0,0,0),Color(0,0,0,1),0.5))
    assert(helper.similar_colors(Color(0,0,0,1),Color(0.000001,0,0,1),0.0))
    var boundary_image=Image.load_from_file(BOUNDARY_FILE)
    var c1=boundary_image.get_pixel(95,0)
    var c2=boundary_image.get_pixel(0,10)
    print("BOUNDARY "+JSON.stringify({"red_difference":absf(c1.r-c2.r),"requested_tolerance":8.0/255.0,"accepted":helper.similar_colors(c1,c2,8.0/255.0)}))
    var ff=load("res://flood.gd").new()
    for file in INPUTS:
        var image=Image.load_from_file(file)
        var project=ff.Project.new()
        project.size=image.get_size()
        for level in [0,1,8,32]:
            ff.tolerance=float(level)/255.0
            var mask=Image.create(image.get_width(),image.get_height(),false,Image.FORMAT_RGBA8)
            ff.flood_fill(Vector2i.ZERO,image,mask,project,Callable(self,"capture"))
            print("REPLAY "+JSON.stringify({"path":file,"tolerance_input_level":level,"mask_rgba_base64":Marshalls.raw_to_base64(mask.get_data())}))
    print("ASSERTIONS_PASS 2")
    quit(0)
'''.replace('INPUTS',json.dumps([str(p)for p in inputs])).replace('BOUNDARY_FILE',json.dumps(str(inputs[2])))
with tempfile.TemporaryDirectory(prefix='flood-oracle-',dir=OUT)as tmp:
    t=Path(tmp);(t/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Source host flood oracle"\n')
    (t/'flood.gd').write_text(flood+fixtures);(t/'similar.gd').write_text('extends RefCounted\n\n'+sim);(t/'main.gd').write_text(main)
    env={k:v for k,v in os.environ.items()if k in ['PATH','HOME','LANG']};env['XDG_DATA_HOME']=str(t/'userdata')
    p=subprocess.run(['/home/astra/.local/bin/godot','--headless','--quit-after','3','--path',tmp,'--script','res://main.gd'],env=env,capture_output=True,text=True,timeout=30)
    if p.returncode or 'ASSERTIONS_PASS 2'not in p.stdout:
        print(p.stdout[:3000],p.stderr[:3000]);raise SystemExit(1)
    rows=[];boundary=None
    for line in p.stdout.splitlines():
        if line.startswith('BOUNDARY '):boundary=json.loads(line[9:])
        if not line.startswith('REPLAY '):continue
        r=json.loads(line[7:]);raw=base64.b64decode(r.pop('mask_rgba_base64'));mask=np.frombuffer(raw,dtype=np.uint8).reshape(96,96,4)[:,:,3]>0
        src=np.array(Image.open(r['path']).convert('RGBA'));r.update(mask_sha256=sha(raw),source_png_sha256=sha(Path(r['path']).read_bytes()),selected_pixels=int(mask.sum()),selection_matters=False,source_seed_xy=[0,0],segments_to_mask='Local fixture sink fills original segment spans white; no selection tool/undo executed.')
        targets=['simple-opaque','complex-opaque']if r['path']==str(inputs[0])else['simple-alpha']if r['path']==str(inputs[1])else['simple','complex']
        root=Path('/home/astra/artifacts/pixellab-cutout-characterization-20261014')if r['path']!=str(inputs[2])else Path('/home/astra/artifacts/pixellab-cutout-connectivity-20261014')
        scores=[]
        for variant in targets:
            target_path=root/variant/'output-00.png';target=np.array(Image.open(target_path).convert('RGBA'))
            pred=src.copy();pred[:,:,3]=255;pred[mask]=0
            scores.append(dict(variant=variant,target_png_sha256=sha(target_path.read_bytes()),mask_mismatches=int(np.count_nonzero(mask!=(target[:,:,3]==0))),local_clear_and_force_opaque_wrapper_rgba_mismatches=int(np.count_nonzero(np.any(pred!=target,axis=2)))))
        r['server_comparisons']=scores;rows.append(r)
    result=dict(classification='unchanged-recovered-host-selector-replay-not-pixellab-server-cutout',engine=p.stdout.splitlines()[0],original_sources=[dict(path=str(flood_path),sha256=sha(flood_path.read_bytes()),executed='whole original file with local Project/sink/dependency declarations appended'),dict(path=str(drawing_path),sha256=sha(drawing_path.read_bytes()),executed='unchanged similar_colors function',function_sha256=sha(sim.encode()),first_line=drawing[:drawing.index('func similar_colors(')].count('\n')+1)],assertions=2,normalized_rgba_float_boundary=boundary,records=rows,stderr=p.stderr,boundary='No selection bounds/tilemap/undo/full editor integration. Alpha-force/clear is local comparison wrapper, not original auto-cutout. Complete source methods unchanged; no PCK compiled bytecode execution claim.')
    (OUT/'HOST-FLOOD-REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(engine=result['engine'],assertions=2,records=[dict(path=r['path'],level=r['tolerance_input_level'],selected=r['selected_pixels'],comparisons=r['server_comparisons'])for r in rows]),indent=2))

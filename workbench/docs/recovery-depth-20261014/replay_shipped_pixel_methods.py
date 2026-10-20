"""Offline oracle: execute exact function slices from recovered Pixelorama source.
Harness/stubs are local fixtures, never a replacement PixelLab algorithm.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path('/home/astra/projects/pixellab-local-test-20261011')
OUT = Path(__file__).resolve().parent
PINS = {'pixelorama-recovered/src/Extensions/PixelLab/get_image.gd': '8f7224392a2b3511d124e577a4a360c8e3344d9df60f0692f011dcd1e89aa651', 'pixelorama-recovered/src/Extensions/PixelLab/draw_image.gd': '0bce163896b067e794ef168df039ec85cae1e0981efad47d1cc090b097be6ff4', 'pixelorama-recovered/src/Extensions/PixelLab/background_generation.gd': '99ff82d3de3e55cb45a58a981a77a6f3a10ae03f9dba735c382a5c6d780c7fc6'}
receipts = []
def method(relative, name):
    p = ROOT / relative
    raw = p.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PINS[relative], "source pin changed"
    text = raw.decode()
    m = re.search(r'^func ' + re.escape(name) + r'\(.*?(?=^func |\Z)', text, re.M | re.S)
    if not m:
        raise ValueError(name)
    # Whole original method, including its body, without translation.
    body = m.group()
    receipts.append(dict(path=relative, source_sha256=hashlib.sha256(raw).hexdigest(),
                         method=name, first_line=text[:m.start()].count('\n')+1,
                         last_line=text[:m.end()].count('\n'),
                         extracted_sha256=hashlib.sha256(body.encode()).hexdigest()))
    return body
base='pixelorama-recovered/src/Extensions/PixelLab/'
pixel='''extends RefCounted
class ExtensionsApi:
    static var project = {"current_project": null}
class PixelLabUtils:
    static var last_image: Image
    static func get_cel_position(_cel): return [0, 0, null]
    static func set_pixelcel_image_with_undo(image, _label, _frame, _layer, _project): last_image = image
var mask_image: Image
var art_image: Image
func get_image(_frame, _bg, _ignore, only_layer="", _selection={}):
    return (mask_image if only_layer == "Inpainting" else art_image).duplicate()
'''
pixel = re.sub(r'(?m)^( +)', lambda m: '\t' * (len(m[0])//4), pixel)
for name in ['has_transparent_pixels','get_mask','image_to_base64','get_limit_color']:
    pixel += '\n'+method(base+'get_image.gd',name)
for name in ['get_image_from_data','draw_image']:
    pixel += '\n'+method(base+'draw_image.gd',name)

dispatch='''extends RefCounted
var tool_data
var draw_image
var cels = [["fixture-cel"]]
func _base_layer_index(): return 0
func _has_uncropped_data(_data): return false
'''
dispatch = re.sub(r'(?m)^( +)', lambda m: '\t' * (len(m[0])//4), dispatch)
dispatch += method(base+'background_generation.gd','_handle_message_done')
main='''extends SceneTree
class Cel:
    var image: Image
    func _init(im): image=im
    func get_image(): return image
class Draw:
    var calls=[]
    func draw_image(_tool, data, _cel, index): calls.append([data,index])
class Loading:
    var args=[]
    func progress(_v): pass
    func done(_seed,_id,images,quantized,_cel): args=[images,quantized]
func rgba(values): return Image.create_from_data(values.size()/4,1,false,Image.FORMAT_RGBA8,PackedByteArray(values))
func _init():
    var p=load("res://pixel.gd").new()
    var bytes=[90,80,70,0,10,20,30,1,40,50,60,128,70,80,90,255]
    var im=rgba(bytes)
    var encoded=Marshalls.base64_to_raw(p.image_to_base64(im))
    assert(Array(encoded)==[0,0,0,0,10,20,30,1,40,50,60,128,70,80,90,255])
    assert(Array(im.get_data())==bytes)
    assert(p.has_transparent_pixels(im))
    assert(not p.has_transparent_pixels(rgba([1,2,3,128])))
    p.mask_image=im
    p.art_image=rgba([1,2,3,255,1,2,3,0,1,2,3,128,1,2,3,255])
    var mask=p.get_mask(0)
    assert(Array(mask.get_data())==[0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255])
    p.mask_image=rgba([1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0])
    var filled=p.get_mask(0,Color.WHITE,Color.BLACK,[],"Inpainting",{},true)
    assert(Array(filled.get_data())==[0,0,0,255,255,255,255,255,0,0,0,255,0,0,0,255])
    p.art_image=p.mask_image
    var empty=p.get_mask(0,Color.WHITE,Color.BLACK,[],"Inpainting",{},false,true)
    assert(Array(empty.get_data())==[255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255])
    var palette_src=rgba([5,6,7,128,5,6,7,128,5,6,7,255,99,88,77,0])
    var pal=p.get_limit_color(palette_src,null,"reference")
    var pal_bytes=Marshalls.base64_to_raw(pal.base64)
    var visible=0
    for i in range(3,pal_bytes.size(),4):
        if pal_bytes[i]>0: visible+=1
    assert(visible==2)
    assert(pal.width==64 and pal.height==64)
    var png=Marshalls.raw_to_base64(im.save_png_to_buffer())
    var decoded=p.get_image_from_data(png,99,98)
    assert(decoded.get_width()==4 and decoded.get_height()==1)
    assert(decoded.get_data()==im.get_data())
    var raw=Marshalls.raw_to_base64(im.get_data())
    assert(p.get_image_from_data(raw,4,1).get_data()==im.get_data())
    var dest=Image.create(6,2,false,Image.FORMAT_RGBA8)
    dest.fill(Color.RED)
    var td={"image_size":{"width":4,"height":1},"selection":{"width":4,"height":1,"origin":{"x":1,"y":1}}}
    p.draw_image(td,raw,[Cel.new(dest)],0)
    var placed=p.PixelLabUtils.last_image
    assert(placed.get_pixel(1,1).a==0 and placed.get_pixel(0,1)==Color.RED)
    assert(dest.get_pixel(1,1)==Color.RED)
    td.preserve_outside_mask=rgba([0,0,0,0,0,0,0,255,0,0,0,0,0,0,0,0])
    p.draw_image(td,raw,[Cel.new(dest)],0)
    assert(p.PixelLabUtils.last_image.get_pixel(1,1)==Color.RED)
    assert(p.PixelLabUtils.last_image.get_pixel(2,1)==im.get_pixel(1,0))
    var d=load("res://dispatch.gd").new()
    var drawer=Draw.new()
    var loading=Loading.new()
    d.draw_image=drawer
    d.tool_data={"tool":RefCounted.new(),"loading":loading,"skip_first_image":1,"skip_last_image":1}
    var data={"images":[{"base64":"Q0"},{"base64":"Q1"},{"base64":"Q2"}],"original_images":[{"base64":"O0"},{"base64":"O1"},{"base64":"O2"}]}
    d._handle_message_done(data)
    assert(drawer.calls==[["Q1",0]])
    assert(loading.args[0]==[{"base64":"O1"}])
    print("ORACLE_PASS "+JSON.stringify({"assertions":18,"cases":["hidden_rgb_exact_zero_only","input_unchanged","partial_alpha_not_transparent_predicate","mask_any_positive_alpha","fill_exact_zero_art_alpha","empty_art_mask","palette_reference_unique_rgba_unweighted","png_actual_dimensions_and_rgba","raw_rgba_decode","placement_origin_erase_and_copy","masked_placement","background_draw_processed_archive_originals_skip_both"]}))
    quit(0)
'''
with tempfile.TemporaryDirectory(prefix='pixel-oracle-',dir=OUT) as tmp:
    t=Path(tmp)
    (t/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Offline recovered method oracle"\n')
    for name,content in [('pixel.gd',pixel),('dispatch.gd',dispatch),('main.gd',main)]:
        (t/name).write_text(content)
    env={k:v for k,v in os.environ.items() if k in ['PATH','HOME','LANG']}
    env['XDG_DATA_HOME']=str(t/'userdata')
    result=subprocess.run(['/home/astra/.local/bin/godot','--headless','--quit-after','3','--path',tmp,'--script','res://main.gd'],env=env,text=True,capture_output=True,timeout=30)
    evidence=dict(classification='deterministic-shipped-client-method-replay', engine='/home/astra/.local/bin/godot', returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,extractions=receipts,harness_boundary='Extracted methods unchanged; synthetic images, fake capture/cels, undo sink and loading/draw sinks. No editor integration, remote processing or full application parity.')
    (OUT/'PIXEL-METHOD-REPLAY.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(result.stdout,result.stderr)
    if result.returncode or 'ORACLE_PASS' not in result.stdout: raise SystemExit(1)

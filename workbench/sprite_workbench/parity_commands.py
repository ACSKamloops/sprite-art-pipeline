"""Execute unchanged recovered editor footprints; not the private draw grammar.

Only the four pinned DrawingAlgos functions execute in Godot. Python validates
local resource bounds and adapts returned points to guarded indexed edits.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from .core import ValidationError, UnsupportedCapability, canonical_json, digest
from . import construction

SOURCE = Path(__file__).parent/'vendor/host_selection/DrawingAlgos.gd'
SOURCE_SHA = '6acef5d413bdf0e7685b7d034bb65885d40b884d6cee60869065052980ec61a9'
SPAN_SHA = '23d4a11762e56134fed1e63c456b998b805eda42dc390d2cd1b5c2b55e36f930'
METHODS = {'ellipse-outline':'get_ellipse_points', 'ellipse-filled':'get_ellipse_points_filled',
           'rounded-rect-outline':'get_rounded_rect_points', 'rounded-rect-filled':'get_rounded_rect_points_filled'}
BOUNDARY = 'Unchanged recovered editor footprint; hosted MCP argv/nested draw grammar and server equivalence unresolved'


def source_provenance():
    raw = SOURCE.read_bytes()
    if digest(raw) != SOURCE_SHA:
        raise ValidationError('Recovered footprint source changed')
    span = raw[raw.index(b'func get_rounded_rect_points('):raw.index(b'func scale_3x(')]
    if digest(span) != SPAN_SHA:
        raise ValidationError('Recovered footprint function span changed')
    return span, {'source_path':'res://src/Autoload/DrawingAlgos.gd', 'source_sha256':SOURCE_SHA,
        'span_sha256':SPAN_SHA, 'source_lines':[155,326], 'source_utf8_bytes':[5077,9151],
        'retained_pck_sha256':'ebf9812ea474bddb84faa22183a1ec0178983cdc285674a4d0177c606e8a4a3f',
        'current_pck_sha256':'398455603cf39fc993c59fca3265ed180e246005da631e918018d0c44d497e4f',
        'recovery':'Unchanged GDRE-recovered source span; no compiled bytecode equivalence claim', 'boundary':BOUNDARY}


def describe():
    _, provenance = source_provenance()
    return {'kind':'recovered-host-footprint-contract','version':1,'methods':dict(METHODS),
        'bounds':{'commands':16,'size_side':128,'aggregate_grown_area':32768},
        'coordinates':'Integer source points; original ordering and duplicates retained; no implicit clipping',
        'source_provenance':provenance,'hosted_argv_parser_recovered':False,'boundary':BOUNDARY}


def _validate(commands):
    if not isinstance(commands,list) or not 1<=len(commands)<=16:
        raise ValidationError('Provide1..16 explicit local footprint commands')
    area=0
    for cmd in commands:
        if not isinstance(cmd,dict) or not isinstance(cmd.get('method'),str) or cmd.get('method') not in METHODS:
            raise UnsupportedCapability('recovered-host-footprint','Only four source footprint methods are supported')
        method=cmd['method']; required={'method','pos','size'}
        if method.startswith('rounded'):required.add('radius')
        if method in ('ellipse-filled','rounded-rect-outline'):required.add('thickness')
        if set(cmd)!=required:
            raise ValidationError('Declare exactly the source method controls; no hosted argv or inferred defaults')
        for field in ('pos','size'):
            pair=cmd[field]
            if not isinstance(pair,list) or len(pair)!=2 or any(type(v)is not int for v in pair):
                raise ValidationError('Position/size need two exact integers')
        if any(not -4096<=v<=4096 for v in cmd['pos']) or any(not 1<=v<=128 for v in cmd['size']):
            raise ValidationError('Local position/shape bounds exceeded')
        for field,low,high in [('radius',0,128),('thickness',1,16)]:
            if field in cmd and (type(cmd[field])is not int or not low<=cmd[field]<=high):
                raise ValidationError('Local radius/thickness bounds exceeded')
        growth=cmd.get('thickness',1)-1 if method=='ellipse-filled' else 0
        area+=(cmd['size'][0]+growth)*(cmd['size'][1]+growth)
    if area>32768:
        raise ValidationError('Aggregate footprint work budget exceeded')


RUNNER = r'''
func _initialize() -> void:
    var commands = JSON.parse_string(FileAccess.get_file_as_string("res://request.json"))
    var rows: Array = []
    for cmd in commands:
        var pos = Vector2i(cmd.pos[0],cmd.pos[1])
        var size = Vector2i(cmd.size[0],cmd.size[1])
        var points: Array[Vector2i] = []
        match cmd.method:
            "ellipse-outline": points=get_ellipse_points(pos,size)
            "ellipse-filled": points=get_ellipse_points_filled(pos,size,int(cmd.thickness))
            "rounded-rect-outline": points=get_rounded_rect_points(pos,size,int(cmd.radius),int(cmd.thickness))
            "rounded-rect-filled": points=get_rounded_rect_points_filled(pos,size,int(cmd.radius))
        var coordinates: Array = []
        for point in points: coordinates.append([point.x,point.y])
        rows.append(coordinates)
    var output=FileAccess.open("res://result.json",FileAccess.WRITE)
    output.store_string(JSON.stringify({"points":rows,"engine":Engine.get_version_info()}))
    quit(0)
'''.replace('    ', '\t')


def evaluate(commands):
    """Return original ordered point lists, including duplicates and source quirks."""
    _validate(commands); span,provenance=source_provenance()
    godot,prlimit=shutil.which('godot'),shutil.which('prlimit')
    if not godot or not prlimit:
        raise UnsupportedCapability('recovered-host-footprint','Local Godot and Linux prlimit required; no Python geometry fallback')
    with tempfile.TemporaryDirectory(prefix='source-footprints-')as temporary:
        root=Path(temporary)
        (root/'project.godot').write_text('config_version=5\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
        (root/'request.json').write_bytes(canonical_json(commands))
        (root/'runner.gd').write_bytes(b'extends SceneTree\n\n'+span+RUNNER.encode())
        env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'HOME':str(root),'XDG_DATA_HOME':str(root/'data'),
             'XDG_CONFIG_HOME':str(root/'config'),'XDG_CACHE_HOME':str(root/'cache'),'LANG':'C.UTF-8'}
        try:
            with (root/'engine.log').open('w+b')as log:
                ran=subprocess.run([prlimit,'--as=4294967296','--cpu=20','--fsize=8388608','--nofile=128','--',
                    godot,'--headless','--path',str(root),'--script','res://runner.gd'],env=env,
                    stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,timeout=30)
                if ran.returncode!=0:
                    raise UnsupportedCapability('recovered-host-footprint','Original source failed in bounded Godot host')
            path=root/'result.json'
            if path.stat().st_size>4*1024*1024:
                raise ValidationError('Recovered footprint output exceeds byte budget')
            result=json.loads(path.read_bytes())
        except (OSError,subprocess.TimeoutExpired,ValueError)as exc:
            raise UnsupportedCapability('recovered-host-footprint','Bounded original source execution unavailable')from exc
    if not isinstance(result.get('points'),list) or len(result['points'])!=len(commands):
        raise ValidationError('Original source output shape differs')
    rows=[]
    for cmd,points in zip(commands,result['points']):
        if (not isinstance(points,list) or len(points)>150000 or
                any(not isinstance(p,list)or len(p)!=2 or any(type(v)is not int for v in p)for p in points)):
            raise ValidationError('Invalid original footprint coordinates')
        rows.append({'command':cmd,'points':points,'ordered_points_sha256':digest(canonical_json({'points':points})),
            'unique_pixels':len({tuple(p)for p in points}),'returned_points':len(points)})
    return {'kind':'recovered-host-footprints','version':1,'results':rows,'engine':result['engine'],
        'source_provenance':provenance,'boundary':BOUNDARY}


def paint_primitive(store,history,cel_id,command,palette_index):
    """Explicit indexed paint using source geometry and the existing guarded history.

    Refuse any source point outside the canvas; no implicit clipping, outlines,
    palette insertion, opacity forcing or hosted recipe/argv conversion.
    """
    current=construction.load_history(store,history);project=construction.load_project(store,current['project'])
    if not isinstance(cel_id,str) or cel_id not in project['cels']:
        raise ValidationError('Unknown target cel')
    cel=project['cels'][cel_id]
    if next(layer for layer in project['layers']if layer['id']==cel['layer_id']).get('locked',False):
        raise ValidationError('Target layer is locked')
    if type(palette_index)is not int or not 0<=palette_index<len(project['palette']):
        raise ValidationError('Existing exact palette index required')
    footprint=evaluate([command]);points=list(dict.fromkeys(tuple(p)for p in footprint['results'][0]['points']))
    width,height=project['canvas']['width'],project['canvas']['height']
    if not points or any(not 0<=x<width or not 0<=y<height for x,y in points):
        raise ValidationError('Footprint is empty or outside canvas; no implicit clipping')
    candidate=list(cel['pixels'])
    for x,y in points:candidate[y*width+x]=palette_index
    from .construction_core import cel_hash
    tx={'schema':'sprite-edit-transaction/v1','expected_project_sha256':current['project_hash'],
        'reason':'Explicit paint using unchanged recovered editor footprint',
        'operations':[{'op':'candidate_patch','cel_id':cel_id,'expected_cel_sha256':cel_hash(project,cel_id),
            'mask':[list(p)for p in points],'candidate_pixels':candidate}]}
    result=construction.edit_history(store,history,tx)
    footprint_id=store.put_json(footprint)
    bound=construction.bind_source_evidence(store,result['history'],footprint_id)
    return {**result,**bound,'footprint':footprint_id,'painted_pixels':len(points),
        'shared_frames':[f['id']for f in project['frames']if cel_id in f['cels'].values()],
        'boundary':BOUNDARY}

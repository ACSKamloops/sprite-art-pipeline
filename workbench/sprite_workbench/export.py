"""Lossless authoritative PNGs and explicitly bounded portable preview/engine formats."""
from __future__ import annotations

from contextlib import contextmanager
from fractions import Fraction
from io import BytesIO
import json
import math
import os
from pathlib import Path
import shutil
import struct
import tempfile
import zlib

import numpy as np
from PIL import Image, GifImagePlugin

from .core import (MAX_FRAMES, MAX_PIXELS, MAX_SEQUENCE_BYTES, ValidationError, UnsupportedCapability,
                   canonical_json, digest, load_sequence, validate_id)


def png_bytes(array):
    output = BytesIO()
    Image.fromarray(array).save(output, format='PNG', compress_level=9)
    return output.getvalue()


def sequence_timeline(document):
    canvas = document.get('canvas')
    entries = document.get('frames')
    if document.get('kind') != 'sequence' or type(document.get('version')) != int or document['version'] != 1:
        raise ValidationError('Expected local sequence version1')
    if not isinstance(canvas,list) or len(canvas) != 2 or any(type(v) != int or v < 1 for v in canvas) or math.prod(canvas) > MAX_PIXELS:
        raise ValidationError('Invalid sequence canvas')
    if not isinstance(entries,list) or not 1 <= len(entries) <= MAX_FRAMES or math.prod(canvas)*4*len(entries) > MAX_SEQUENCE_BYTES:
        raise ValidationError('Sequence exceeds frame/byte budget')
    if not isinstance(document.get('metadata',{}),dict):
        raise ValidationError('Sequence metadata must be an object')
    elapsed = Fraction(0); frames = []
    for i, frame in enumerate(document['frames']):
        if not isinstance(frame,dict) or type(frame.get('index')) != int or frame['index'] != i:
            raise ValidationError('Sequence indices must match original ordered frame array')
        if not isinstance(frame.get('direction'),str) or not frame['direction']:
            raise ValidationError('Frame direction must be nonempty text')
        d = frame.get('duration')
        if not isinstance(d,list) or len(d) != 2 or any(type(v) != int for v in d):
            raise ValidationError('Expected exact rational duration')
        try:
            hold = Fraction(*d)
        except (ValueError, ZeroDivisionError) as e:
            raise ValidationError('Invalid exported duration') from e
        if not 0 < hold <= 3600:
            raise ValidationError('Duration outside local range')
        pivot = frame.get('pivot')
        if not isinstance(pivot,list) or len(pivot) != 2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in pivot):
            raise ValidationError('Invalid exported pivot')
        frames.append(frame | {'start':[elapsed.numerator,elapsed.denominator],
                               'end':[(elapsed+hold).numerator,(elapsed+hold).denominator]})
        elapsed += hold
    if type(document.get('loop')) != bool:
        raise ValidationError('Sequence loop must be boolean')
    count = document.get('play_count',0 if document['loop'] else 1)
    if type(count) != int or not 0 <= count <= 65536 or document['loop'] != (count == 0):
        raise ValidationError('play_count must be0..65536; loop means infinite only')
    return {'frames':frames,'total':[elapsed.numerator,elapsed.denominator],
            'loop':document['loop'],'play_count':count,
            'play_total':None if count == 0 else [(elapsed*count).numerator,(elapsed*count).denominator],
            'time_unit':'rational seconds','index_unit':'zero-based ordered frame'}


def validated_sequence(store, ident):
    document = store.get_json(ident)
    sequence_timeline(document)  # Admission before loading all frame arrays.
    return load_sequence(store,ident)


def playback_clock(timeline, capability):
    """Admit float-based players separately from the lossless rational artifact."""
    try:
        durations = [float(Fraction(*f['duration'])) for f in timeline['frames']]
        starts = [float(Fraction(*f['start'])) for f in timeline['frames']]
        ends = [float(Fraction(*f['end'])) for f in timeline['frames']]
        total = float(Fraction(*timeline['total']))
        limit = None if timeline['play_count'] == 0 else float(Fraction(*timeline['play_total']))
    except (OverflowError, ValueError) as e:
        raise UnsupportedCapability(capability,'Rational clock exceeds finite float playback range') from e
    if (any(not math.isfinite(v) or v <= 0 for v in durations + ends + [total])
            or any(not math.isfinite(v) or v < 0 for v in starts)
            or any(end <= start for start,end in zip(starts,ends))
            or limit is not None and (not math.isfinite(limit) or limit <= 0)):
        raise UnsupportedCapability(capability,'Positive rational holds collapse or overflow in float playback; exact PNG/manifest remain available')
    return {'durations':durations,'starts':starts,'ends':ends,'total':total,'limit':limit,
            'conversion':'checked finite float seconds; rational manifest authoritative'}


@contextmanager
def output_directory(directory):
    target = Path(directory).absolute()
    if target.is_symlink() or (target.exists() and (not target.is_dir() or any(target.iterdir()))):
        raise ValidationError('Output must be absent or an empty nonsymlink directory; existing artifacts are preserved')
    target.parent.mkdir(parents=True,exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f'.{target.name}-pending-',dir=target.parent))
    try:
        yield stage
        if target.exists():
            target.rmdir()  # Fails if anything arrived meanwhile; never removes user files.
        os.rename(stage,target)
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def _chunk(kind, payload):
    return struct.pack('!I',len(payload)) + kind + payload + struct.pack('!I',zlib.crc32(kind+payload)&0xffffffff)


def apng_bytes(arrays, durations, play_count):
    """Full-frame SOURCE/NONE APNG, no frame coalescing or millisecond conversion."""
    if any(d.numerator > 65535 or d.denominator > 65535 for d in durations):
        raise UnsupportedCapability('apng-exact-clock','Each rational numerator/denominator must fit unsigned16-bit fields')
    h,w = arrays[0].shape[:2]
    output = bytearray(b'\x89PNG\r\n\x1a\n')
    output += _chunk(b'IHDR',struct.pack('!IIBBBBB',w,h,8,6,0,0,0))
    output += _chunk(b'acTL',struct.pack('!II',len(arrays),play_count))
    serial = 0
    for i,(a,d) in enumerate(zip(arrays,durations)):
        output += _chunk(b'fcTL',struct.pack('!IIIIIHHBB',serial,w,h,0,0,d.numerator,d.denominator,0,0))
        serial += 1
        raw = b''.join(b'\0'+row.tobytes() for row in a)
        compressed = zlib.compress(raw,9)
        if i == 0:
            output += _chunk(b'IDAT',compressed)
        else:
            output += _chunk(b'fdAT',struct.pack('!I',serial)+compressed)
            serial += 1
    output += _chunk(b'IEND',b'')
    return bytes(output)


def gif_bytes(arrays, durations, play_count):
    """Shared exact visible palette, binary alpha, explicit nearest-centisecond holds."""
    if max(arrays[0].shape[:2]) > 65535:
        raise UnsupportedCapability('gif-dimensions','GIF dimensions are unsigned16-bit')
    if play_count > 65536:
        raise UnsupportedCapability('gif-plays','Finite play_count requires repeats=play_count-1 in unsigned16-bit field')
    if any(np.any((a[...,3] != 0)&(a[...,3] != 255)) for a in arrays):
        raise UnsupportedCapability('gif-alpha','Partial alpha is not silently flattened or thresholded')
    colors = set()
    for a in arrays:
        colors.update(map(tuple,a[a[...,3] == 255,:3]))
        if len(colors) > 255:
            raise UnsupportedCapability('gif-palette','More than255 visible RGB colors; quantization requires a separate explicit preparation step')
    palette = [(0,0,0)] + sorted(colors)
    color_indices = {c:i+1 for i,c in enumerate(sorted(colors))}
    palette_bytes = bytes(v for c in palette for v in c) + bytes(3*(256-len(palette)))
    ticks = [max(1,(2*d.numerator*100+d.denominator)//(2*d.denominator)) for d in durations]
    if any(t > 65535 for t in ticks):
        raise UnsupportedCapability('gif-clock','Hold exceeds unsigned16-bit centisecond field')
    output = bytearray(); total_error = Fraction(0); errors = []
    for i,a in enumerate(arrays):
        indices = np.zeros(a.shape[:2],dtype=np.uint8)
        for color,index in color_indices.items():
            indices[(a[...,3] == 255)&np.all(a[...,:3] == color,axis=2)] = index
        image = Image.fromarray(indices); image.putpalette(palette_bytes)
        if i == 0:
            info = {'transparency':0,'duration':ticks[0]*10,'background':0,'optimize':False}
            if play_count != 1:
                info['loop'] = 0 if play_count == 0 else play_count-1
            header,_ = GifImagePlugin.getheader(image, info=info)
            output.extend(b''.join(header))
        output.extend(b''.join(GifImagePlugin.getdata(image,duration=ticks[i]*10,transparency=0,
                                                     disposal=2,optimize=False,include_color_table=False)))
        error = Fraction(ticks[i],100)-durations[i]; total_error += error
        errors.append({'frame':i,'encoded_centiseconds':ticks[i],
                       'error_seconds':[error.numerator,error.denominator],
                       'cumulative_error_seconds':[total_error.numerator,total_error.denominator]})
    output.extend(b';')
    return bytes(output), {'status':'written','clock':'nearest centisecond, ties up, minimum1',
                           'alpha':'binary only; hiddenRGB not representable',
                           'palette':'exact shared visible RGB <=255; transparent index0',
                           'duplicates':'all ordered entries encoded, no coalescing',
                           'loop_extension':(0 if play_count == 0 else play_count-1) if play_count != 1 else 'omitted: one-shot',
                           'play_count':play_count,'frames':errors}


def _artifact_closure(store, ident):
    pending = [(ident,True)]; done = {}; interpreted = set()
    while pending:
        key,document = pending.pop()
        if key in done and (not document or key in interpreted):
            continue
        raw = store.get_bytes(key); done[key] = raw
        if sum(map(len,done.values())) > MAX_SEQUENCE_BYTES * 2:
            raise ValidationError('Editable artifact closure exceeds local byte budget')
        if not document:
            continue  # Raw RGBA blobs are never interpreted as JSON, even if their bytes happen to parse.
        interpreted.add(key)
        try:
            doc = json.loads(raw)
        except (ValueError,UnicodeDecodeError):
            continue
        if not isinstance(doc,dict):
            continue
        if doc.get('kind') == 'rgba':
            pending.append((doc['blob'],False))
            metadata=doc.get('metadata',{})
            for field in ('parent_raster','paste_decision'):
                if metadata.get(field):pending.append((metadata[field],True))
        elif doc.get('kind') == 'sequence':
            pending.extend((f['raster'],True) for f in doc['frames'])
            meta = doc.get('metadata',{})
            for field in ['scene_id','parent_sequence','raster_decision','preparation','parent','recipe','track_audit','terrain_recipe','font_atlas','poster_raster','pipeline_plan','construction_project','construction_history','construction_import','pixellab_controls','observed_vfx_default','model_result']:
                if meta.get(field):
                    pending.append((meta[field],True))
            if meta.get('source_bytes'):
                pending.append((meta['source_bytes'],False))
            pending.extend((sid,True) for sid in meta.get('source_ids',[]))
            pending.extend((sid,True) for sid in meta.get('pipeline_source_sequences',[]))
            pending.extend((sid,True) for sid in meta.get('sources',{}).values() if sid)
            pending.extend((p['raster'],True) for p in meta.get('placements',[]) if p.get('raster'))
            pending.extend((sid,True) for sid in meta.get('viseme_rasters',{}).values())
        elif doc.get('kind') == 'model-result':
            pending.extend((doc[field], True) for field in ('task', 'brief', 'raw_sequence'))
        elif doc.get('kind') == 'model-task':
            pending.append((doc['brief'], True))
            for item in doc['inputs']:
                pending.extend([(item['raster'], True), (item['png'], False)])
        elif doc.get('kind') == 'model-brief':
            pending.extend((item['raster'], True) for item in doc['brief']['inputs'])
        elif doc.get('kind') == 'construction-project':
            if doc.get('source_sequence'):
                pending.append((doc['source_sequence'],True))
        elif doc.get('kind') == 'construction-history':
            pending.extend((doc[field],True) for field in ('initial_project','project'))
            pending.extend((checkpoint,True) for checkpoint in doc.get('checkpoints',[]))
            pending.extend((entry['artifact'],True) for entry in doc.get('source_evidence',[]))
        elif doc.get('kind') == 'construction-selection':
            pending.extend((doc[field],True) for field in ('source_project','mask_raster'))
        elif doc.get('kind') == 'construction-selection-edit':
            pending.extend((doc[field],True) for field in ('selection','history_before','history_after','project_before','project_after'))
        elif doc.get('kind') == 'original-pixel-method':
            request = doc['request']
            for field in ('raster','mask','art','source','destination','preserve_mask'):
                if request.get(field):pending.append((request[field],True))
            if request.get('media'):pending.append((request['media'],False))
            if doc.get('output_raster'):pending.append((doc['output_raster'],True))
            if doc.get('raw_rgba'):pending.append((doc['raw_rgba'],False))
        elif doc.get('kind') == 'original-palette-import':
            pending.append((doc['source_raster'],True))
        elif doc.get('kind') == 'studio-normalization':
            pending.append((doc['source_sequence'],True))
        elif doc.get('kind') == 'studio-session':
            pending.extend((doc[field],True) for field in ('source_sequence','editable_sequence','normalization','project','history'))
        elif doc.get('kind') == 'motion-extraction':
            pending.extend((doc[field],False) for field in ('media','probe'))
            pending.extend((f['raster'],True) for f in doc['frames'])
            pending.extend((sid,True) for sid in doc.get('source_bindings',[]))
            if doc.get('parent_extraction'):pending.append((doc['parent_extraction'],True))
        elif doc.get('kind') == 'motion-extraction-failure':
            pending.append((doc['media'],False))
        elif doc.get('kind') == 'motion-sample-decision':
            pending.extend([(doc['extraction'],True),(doc['media'],False)])
        elif doc.get('kind') in ('motion-conditioning','motion-conditioning-failure'):
            pending.append((doc['source_sequence'],True))
            for frame in doc.get('frames',[]):
                pending.extend((frame[field],True) for field in ('source_raster','resized_raster','selection','mask_raster','output_raster') if frame.get(field))
            palette=doc.get('settings',{}).get('palette',{})
            if palette.get('reference_raster'):pending.append((palette['reference_raster'],True))
        elif doc.get('kind') == 'motion-retime':
            pending.append((doc['source_sequence'],True))
        elif doc.get('kind') == 'raster-selection':
            pending.extend((doc[field],True) for field in ('source_raster','mask_raster'))
        elif doc.get('kind') == 'motion-provider-packet':
            pending.append((doc['request'],False))
            pending.extend((item['png'],False) for item in doc['inputs'])
        elif doc.get('kind') == 'motion-native-video':
            pending.extend([(doc['packet'],True),(doc['video'],False),(doc['probe'],True)])
            if doc.get('supplied_completion'):pending.append((doc['supplied_completion'],True))
        elif doc.get('kind') == 'motion-media-download':
            pending.extend([(doc['packet'],True),(doc['video'],False)])
        elif doc.get('kind') == 'construction-ase-binding':
            pending.append((doc['project'],True))
            pending.append((doc['native_bytes'],False))
        elif doc.get('kind') == 'construction-ase-import':
            pending.extend((doc[field],True) for field in ('source_project','binding','imported_project'))
            pending.extend((doc[field],False) for field in ('native_bytes','sidecar_bytes'))
        elif doc.get('kind') == 'layered-scene':
            pending.extend((sid,True) for sid in doc['source_ids'])
            if doc['scene'].get('metadata',{}).get('track_audit'):
                pending.append((doc['scene']['metadata']['track_audit'],True))
            for frame in doc['frame_layers']:
                for layer in frame['layers']:
                    pending.extend((layer[k],True) for k in ['raster','mask','transformed_raster','transformed_mask'])
            guards = doc['scene'].get('guards',{})
            pending.extend((guards[k],True) for k in ['reference_sequence','palette_reference'] if k in guards)
            pending.extend((p['mask'],True) for p in guards.get('protected',[]))
            # Base parts remain editable even when every rendered pose overrides them.
            declared = list(doc['scene'].get('nodes',[]))
            declared.extend(n for f in doc['scene'].get('frames',[]) for n in f.get('nodes',{}).values())
            for node in declared:
                pending.extend((node[k],True) for k in ['raster','mask'] if node.get(k))
                if (node.get('ownership') or {}).get('source'):
                    pending.append((node['ownership']['source'],True))
        elif doc.get('kind') == 'raster-decision':
            pending.append((doc['parent_sequence'],True))
        elif doc.get('kind') == 'raster-paste':
            pending.append((doc['parent_raster'],True))
            pending.append((doc['patch'],True))
        elif doc.get('kind') == 'preparation':
            for field in ['rasters','references','source_rasters','source_references']:
                pending.extend((sid,True) for sid in doc.get(field,[]))
            if doc.get('mask'):
                pending.append((doc['mask'],True))
            if doc.get('source_mask'):
                pending.append((doc['source_mask'],True))
        elif doc.get('kind') == 'effect-recipe':
            if doc.get('subject'):
                pending.append((doc['subject'],True))
            pending.extend((sid,True) for sid in doc.get('images',{}).values())
            if doc.get('renderer_manifest'):
                pending.append((doc['renderer_manifest'],False))
        elif doc.get('kind') == 'terrain-recipe':
            pending.extend((c['raster'],True) for c in doc['cells'])
        elif doc.get('kind') == 'font-atlas':
            pending.append((doc['atlas'],True))
            pending.extend((g['raster'],True) for g in doc['glyphs'].values())
            if doc.get('font_source',{}).get('bytes'):
                pending.append((doc['font_source']['bytes'],False))
        elif doc.get('kind') == 'track-bake':
            for track in doc.get('tracks',[]):
                for keyframe in track.get('keys',[]):
                    value = keyframe['value']
                    if track['property'] in ['raster','mask']:
                        pending.append((value,True))
                    elif track['property'] == 'ownership' and value and value.get('source'):
                        pending.append((value['source'],True))
    return done


def import_editable(store, directory):
    directory = Path(directory)
    if directory.is_symlink() or (directory/'artifacts').is_symlink() or (directory/'index.json').is_symlink():
        raise ValidationError('Editable containers cannot use symlinks')
    try:
        index = json.loads((directory/'index.json').read_text())
    except (ValueError,UnicodeDecodeError,OSError) as e:
        raise ValidationError('Invalid editable index JSON') from e
    if not isinstance(index,dict) or index.get('kind') != 'sprite-workbench-editable' or type(index.get('version')) != int or index['version'] != 1:
        raise ValidationError('Unsupported editable format')
    ids = index.get('artifact_ids')
    if not isinstance(ids,list) or len(ids) > 100000:
        raise ValidationError('Invalid editable artifact inventory')
    pending = []; total_bytes = 0
    for ident in ids:
        validate_id(ident); path = directory/'artifacts'/ident
        if path.is_symlink():
            raise ValidationError('Editable blobs cannot be symlinks')
        total_bytes += path.stat().st_size
        if total_bytes > MAX_SEQUENCE_BYTES*2:
            raise ValidationError('Editable import exceeds byte budget')
        raw = path.read_bytes()
        if digest(raw) != ident:
            raise ValidationError('Editable artifact hash mismatch')
        pending.append(raw)
    for raw in pending:
        store.put_bytes(raw)
    ident = index['sequence_id']; validated_sequence(store,ident)
    if set(_artifact_closure(store,ident)) != set(ids):
        raise ValidationError('Editable closure differs from inventory')
    return ident


def _godot(directory, manifest, columns):
    timeline = sequence_timeline(manifest | {'kind':'sequence'})
    clock = playback_clock(timeline, 'godot-clock')
    source_events = manifest.get('metadata', {}).get('events', [])
    if not isinstance(source_events, list):
        raise ValidationError('Godot events must be a list')
    events = []
    if source_events:
        fps = manifest['metadata'].get('fps')
        if type(fps) not in (int, float) or fps <= 0:
            raise ValidationError('Godot tick events require an explicit positive FPS')
        try:
            fps = Fraction(fps)
        except (ValueError, OverflowError) as error:
            raise ValidationError('Godot event FPS must be finite') from error
        total = Fraction(*timeline['total'])
        for event in source_events:
            if (not isinstance(event, dict) or set(event) != {'at_tick', 'name'}
                    or type(event['at_tick']) is not int or not 0 <= event['at_tick'] <= 9_007_199_254_740_991
                    or not isinstance(event['name'], str) or not event['name']):
                raise ValidationError('Invalid authored Godot tick event')
            at = Fraction(event['at_tick'], 1)/fps
            if not 0 <= at < total:
                raise ValidationError('Godot event lies outside the source clip')
            seconds = float(at)
            if not math.isfinite(seconds) or at > 0 and seconds <= 0 or seconds >= clock['total']:
                raise UnsupportedCapability('godot-clock', 'Event time collapses in float playback')
            events.append({**event, 'at_seconds': seconds})
        events.sort(key=lambda event: event['at_tick'])  # Stable order for simultaneous authored events.
        if any(a['at_tick'] != b['at_tick'] and a['at_seconds'] >= b['at_seconds']
               for a, b in zip(events, events[1:])):
            raise UnsupportedCapability('godot-clock', 'Distinct event times collapse in float playback')
    w, h = manifest['canvas']
    pivots = [frame['pivot'] for frame in manifest['frames']]
    left, top = min(-p[0] for p in pivots), min(-p[1] for p in pivots)
    right, bottom = max(w-p[0] for p in pivots), max(h-p[1] for p in pivots)
    try:
        extent = [float(right-left), float(bottom-top)]
        center = [float(left)+extent[0]/2, float(top)+extent[1]/2]
    except OverflowError as error:
        raise UnsupportedCapability('godot-registration', 'Pivoted canvas envelope overflows') from error
    if any(not math.isfinite(v) or v <= 0 for v in extent) or any(not math.isfinite(v) for v in center):
        raise UnsupportedCapability('godot-registration', 'Pivoted canvas envelope collapses or overflows')
    directory.mkdir()
    shutil.copyfile(directory.parent/'sheet.png',directory/'sheet.png')
    (directory/'timeline.json').write_bytes(canonical_json(manifest))
    # The lossless rational timeline remains authoritative. Godot consumes this
    # explicitly admitted finite-float projection, avoiding JSON integer coercion
    # of arbitrary numerator/denominator sizes inside the engine.
    runtime = {'version': 1, 'sequence_id': manifest['sequence_id'], **clock,
               'frames': [{'pivot': pivot} for pivot in pivots], 'events': events,
               'play_count': timeline['play_count'], 'canvas': [w, h],
               'camera_center': center, 'camera_extent': extent,
               'max_event_crossings_per_advance': 65536}
    (directory/'playback.json').write_bytes(canonical_json(runtime))
    w,h = manifest['canvas']; count = len(manifest['frames'])
    text = [f'[gd_resource type="SpriteFrames" load_steps={count+2} format=3]',
            '[ext_resource type="Texture2D" path="res://sheet.png" id="1"]']
    for i in range(count):
        text.extend([f'[sub_resource type="AtlasTexture" id="frame_{i}"]', 'atlas = ExtResource("1")',
                     f'region = Rect2({i%columns*w}, {i//columns*h}, {w}, {h})'])
    fs = ',\n'.join('{"duration": '+repr(float(Fraction(*f['duration'])))+', "texture": SubResource("frame_'+str(i)+'")}' for i,f in enumerate(manifest['frames']))
    text.extend(['[resource]', 'animations = [{"frames": [\n'+fs+'\n], "loop": '+str(manifest['loop']).lower()+', "name": &"clip", "speed": 1.0}]'])
    (directory/'clip.tres').write_text('\n\n'.join(text)+'\n')
    (directory/'project.godot').write_text('''config_version=5
[application]
config/name="Supplied-art sprite workbench export"
run/main_scene="res://clip.tscn"
[display]
window/size/viewport_width=640
window/size/viewport_height=480
[rendering]
renderer/rendering_method="gl_compatibility"
[importer_defaults]
texture={"compress/mode":0,"process/fix_alpha_border":false,"process/premult_alpha":false,"mipmaps/generate":false}
''')
    (directory/'clip.tscn').write_text('''[gd_scene load_steps=3 format=3]
[ext_resource type="SpriteFrames" path="res://clip.tres" id="1"]
[ext_resource type="Script" path="res://driver.gd" id="2"]
[node name="Clip" type="Node2D"]
script = ExtResource("2")
[node name="AnimatedSprite2D" type="AnimatedSprite2D" parent="."]
texture_filter = 1
sprite_frames = ExtResource("1")
animation = &"clip"
centered = false
[node name="Camera2D" type="Camera2D" parent="."]
enabled = true
''')
    (directory/'driver.gd').write_text('''extends Node2D
signal timeline_event(event: Dictionary)
signal playback_completed
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var camera: Camera2D = $Camera2D
var timeline: Dictionary
var elapsed_seconds: float = 0.0
var completed_plays: int = 0
var playing: bool = true
var completed: bool = false
var rate: float = 1.0
var _loaded: bool = false
var _started: bool = false
var _advancing: bool = false
func _ready() -> void:
    timeline = JSON.parse_string(FileAccess.get_file_as_string("res://playback.json"))
    sprite.stop()
    sprite.speed_scale = 0.0  # Native play/pause flags remain usable; only this elapsed clock advances.
    sprite.frame_changed.connect(_apply_pivot)
    get_viewport().size_changed.connect(_fit_camera)
    _loaded = true
    _fit_camera()
    _show_frame()
    if playing: play()
func _process(delta: float) -> void:
    if playing and not sprite.is_playing(): playing = false
    advance_seconds(delta)
func _apply_pivot() -> void:
    if not _loaded: return
    var p = timeline["frames"][sprite.frame]["pivot"]
    sprite.offset = -Vector2(p[0], p[1])
func _fit_camera() -> void:
    if not _loaded: return
    var center = timeline["camera_center"]
    var extent = timeline["camera_extent"]
    camera.position = Vector2(center[0], center[1])
    var size = get_viewport_rect().size
    if size.x <= 0.0 or size.y <= 0.0: return
    var fit = minf(size.x / float(extent[0]), size.y / float(extent[1])) * 0.9
    if fit >= 1.0: fit = maxf(1.0, floorf(fit))
    camera.zoom = Vector2(fit, fit)
func _play_index(at: float) -> int:
    var total: float = timeline["total"]
    var nearest: float = roundf(at / total)
    if at == nearest * total: return int(nearest)
    return int(floor(at / total))
func _show_frame(event_time: float = -1.0) -> void:
    var total: float = timeline["total"]
    var local_time: float = total if completed else elapsed_seconds - _play_index(elapsed_seconds) * total
    if event_time >= 0.0: local_time = event_time
    var index: int = timeline["ends"].size() - 1
    if not completed:
        for i in range(timeline["ends"].size()):
            if local_time < float(timeline["ends"][i]):
                index = i
                break
    var start: float = timeline["starts"][index]
    var duration: float = timeline["durations"][index]
    var progress = clampf((local_time - start) / duration, 0.0, 1.0)
    sprite.set_frame_and_progress(index, progress)
    _apply_pivot()
func play() -> bool:
    if not _loaded or completed or _advancing: return false
    playing = true
    sprite.play(&"clip")
    if not _started:
        _started = true
        _advancing = true
        for event in timeline["events"]:
            if float(event["at_seconds"]) == 0.0:
                _emit_event(event, 0)
        _advancing = false
    return true
func pause() -> bool:
    if _advancing: return false
    playing = false
    if _loaded: sprite.pause()
    return true
func restart() -> bool:
    if not _loaded or _advancing: return false
    elapsed_seconds = 0.0
    completed_plays = 0
    completed = false
    _started = false
    playing = false
    sprite.stop()
    _show_frame()
    return play()
func set_rate(value: float) -> bool:
    if _advancing or not is_finite(value) or value <= 0.0: return false
    rate = value
    return true
func _emit_event(event: Dictionary, play_index: int) -> void:
    var payload = event.duplicate(true)
    payload["play_index"] = play_index
    payload["absolute_seconds"] = elapsed_seconds
    payload["frame"] = sprite.frame
    timeline_event.emit(payload)
func advance_seconds(delta: float) -> bool:
    if not _loaded or _advancing or not is_finite(delta) or delta < 0.0: return false
    if not playing or completed or delta == 0.0: return true
    var step = delta * rate
    var target = elapsed_seconds + step
    if not is_finite(step) or not is_finite(target) or step > 0.0 and target <= elapsed_seconds: return false
    var count: int = int(timeline["play_count"])
    var total: float = timeline["total"]
    if count > 0: target = minf(target, float(timeline["limit"]))
    if target / total > 9007199254740991.0: return false
    var first_play: int = _play_index(elapsed_seconds)
    var last_play: int = _play_index(target)
    if count > 0: last_play = mini(last_play, count - 1)
    var crossed: Array = []
    if (last_play - first_play + 2) * (timeline["events"].size() + 1) > int(timeline["max_event_crossings_per_advance"]):
        return false  # No state changes on an over-budget advancement.
    for p in range(first_play, last_play + 1):
        for event_index in range(timeline["events"].size()):
            var event = timeline["events"][event_index]
            var at: float = p * total + float(event["at_seconds"])
            if float(event["at_seconds"]) > 0.0 and (at <= p * total or at >= (p + 1) * total): return false
            if at > elapsed_seconds and at <= target:
                crossed.append({"kind": "event", "event": event, "at": at, "play": p, "order": event_index})
    var last_boundary: int = _play_index(target)
    if count > 0: last_boundary = mini(last_boundary, count)
    for p in range(first_play + 1, last_boundary + 1):
        crossed.append({"kind": "boundary", "at": p * total, "play": p, "order": -1})
    crossed.sort_custom(func(a, b):
        if a["at"] == b["at"]: return a["order"] < b["order"]
        return a["at"] < b["at"])
    _advancing = true
    for item in crossed:
        elapsed_seconds = item["at"]
        completed_plays = int(item["play"]) if item["kind"] == "boundary" else _play_index(elapsed_seconds)
        if item["kind"] == "boundary":
            sprite.set_frame_and_progress(timeline["ends"].size() - 1, 1.0)
            _apply_pivot()
            if count == 0: sprite.animation_looped.emit()
            else: sprite.animation_finished.emit()
        else:
            _show_frame(float(item["event"]["at_seconds"]))
            _emit_event(item["event"], item["play"])
    elapsed_seconds = target
    completed = count > 0 and target >= float(timeline["limit"])
    completed_plays = count if completed else _play_index(elapsed_seconds)
    if completed:
        playing = false
        sprite.pause()
    _show_frame()
    _advancing = false
    if completed: playback_completed.emit()
    return true
func get_playback_state() -> Dictionary:
    return {"time": elapsed_seconds, "frame": sprite.frame,
        "frame_progress": sprite.frame_progress, "playing": playing,
        "completed": completed, "completed_plays": completed_plays,
        "rate": rate, "play_count": int(timeline.get("play_count", 1))}
''')


def export_sequence(store, ident, directory, formats=('png','sheet','manifest','apng','gif','editable','godot','review')):
    requested = {formats} if isinstance(formats,str) else set(formats)
    allowed = {'png','sheet','manifest','apng','gif','editable','godot','review'}
    if requested-allowed:
        raise UnsupportedCapability('export-format',str(sorted(requested-allowed)))
    doc,arrays = validated_sequence(store,ident); timeline = sequence_timeline(doc)
    durations = [Fraction(*f['duration']) for f in doc['frames']]
    w,h = doc['canvas']; columns = min(len(arrays),max(1,math.ceil(math.sqrt(len(arrays)))))
    rows = math.ceil(len(arrays)/columns)
    report = {'sequence_id':ident,'visual_acceptance':'unreviewed','requested_formats':sorted(requested),
              'formats':{},'source_ids':doc.get('metadata',{}).get('source_ids',[])}
    with output_directory(directory) as out:
        (out/'frames').mkdir()
        records = []
        for i,(a,f) in enumerate(zip(arrays,timeline['frames'])):
            path = f'frames/frame-{i:04d}.png'; encoded = png_bytes(a); (out/path).write_bytes(encoded)
            records.append(f | {'file':path,'png_sha256':digest(encoded),'rgba_sha256':digest(a.tobytes()),
                                'rectangle':[i%columns*w,i//columns*h,w,h],
                                'source_size':[w,h],'sprite_source_rectangle':[0,0,w,h],'offset':[0,0]})
        report['formats']['png'] = {'status':'written','rgba':'exact including hiddenRGB','ordered_frames':len(arrays)}
        manifest = {'kind':'sprite-workbench-export','version':1,'sequence_id':ident,'canvas':[w,h],
                    'sheet_columns':columns,'sheet_rows':rows,'frames':records,'loop':doc['loop'],
                    'total':timeline['total'],'play_count':timeline['play_count'],'play_total':timeline['play_total'],
                    'units':{'duration':'rational seconds','rectangle':'pixel x/y/w/h',
                    'pivot':'canvas pixel coordinates','indices':'zero-based ordered entries'},
                    'metadata':doc.get('metadata',{}),'visual_acceptance':'unreviewed'}
        if requested & {'sheet','godot'}:
            if w*h*columns*rows > MAX_SEQUENCE_BYTES//4:
                raise ValidationError('Sheet exceeds local byte budget')
            sheet = np.zeros((rows*h,columns*w,4),dtype=np.uint8)
            for i,a in enumerate(arrays):
                sheet[i//columns*h:(i//columns+1)*h,i%columns*w:(i%columns+1)*w] = a
            encoded = png_bytes(sheet); (out/'sheet.png').write_bytes(encoded)
            manifest['sheet'] = {'file':'sheet.png','png_sha256':digest(encoded),'rgba_sha256':digest(sheet.tobytes())}
            report['formats']['sheet'] = {'status':'written','padding_rgba':[0,0,0,0],'trim':'none'}
        for name in ['apng','gif']:
            if name not in requested:
                continue
            try:
                if name == 'apng':
                    encoded = apng_bytes(arrays,durations,timeline['play_count'])
                    info = {'status':'written','clock':'exact rational16-bit APNG fields','blend':'SOURCE','dispose':'NONE',
                            'num_plays':timeline['play_count'],'ordered_frames':len(arrays),'rgba':'exact including hiddenRGB'}
                else:
                    encoded,info = gif_bytes(arrays,durations,timeline['play_count'])
                (out/f'animation.{name}').write_bytes(encoded); info['sha256'] = digest(encoded)
                report['formats'][name] = info
            except UnsupportedCapability as e:
                report['formats'][name] = e.to_dict()
        if 'editable' in requested:
            editable = out/'editable'; (editable/'artifacts').mkdir(parents=True)
            artifacts = _artifact_closure(store,ident)
            for key,raw in artifacts.items():
                (editable/'artifacts'/key).write_bytes(raw)
            scene_id = doc.get('metadata',{}).get('scene_id')
            index = {'kind':'sprite-workbench-editable','version':1,'sequence_id':ident,'scene_id':scene_id,
                     'artifact_ids':sorted(artifacts)}
            (editable/'index.json').write_bytes(canonical_json(index))
            if scene_id:
                (editable/'scene.json').write_bytes(canonical_json(store.get_json(scene_id)))
            report['formats']['editable'] = {'status':'written','artifact_count':len(artifacts),'scene_id':scene_id,
                                             'scope':'local JSON+rawRGBA/masks; no native vendor editable format claimed'}
        if 'godot' in requested:
            try:
                _godot(out/'godot',manifest,columns)
                report['formats']['godot'] = {'status':'written','clock':'single elapsed driver in checked float seconds; rational timeline.json authoritative; SpriteFrames speed1 stores hold weights',
                                          'play_count':timeline['play_count'],'finite_replays':'elapsed clock counts plays and emits animation_finished per completed play',
                                          'pivot':'driver offset=-per-frame pivot, centered=false','runtime_verification':'not executed by export','player':'one checked elapsed clock; pause/play/restart/advance_seconds; authored tick events only','camera':'fixed envelope covering every pivoted canvas'}
            except UnsupportedCapability as e:
                report['formats']['godot'] = e.to_dict()
        if 'review' in requested:
            from .review import _write_review
            try:
                report['formats']['review'] = _write_review(store,ident,out/'review')
            except UnsupportedCapability as e:
                report['formats']['review'] = e.to_dict()
        (out/'manifest.json').write_bytes(canonical_json(manifest))
        report['formats']['manifest'] = {'status':'written','file':'manifest.json','clock':'exact rational seconds',
                                          'play_count':timeline['play_count']}
        report['files'] = [{'file':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())}
                           for p in sorted(out.rglob('*')) if p.is_file()]
        (out/'export-report.json').write_bytes(canonical_json(report))
    return report

#!/usr/bin/env python3
"""Explicit local video-to-sprite derivative; no generation or source repair.

The default interval [16,64) is manually proposed, not automatically detected.
Loop variants use that same interval, with authored two-second clocks. One-shot
variants include both endpoint frames and use selected native PTS differences.
Neither mode identifies a source sprite frame rate or inferred gameplay events.
"""
import argparse
from collections import deque
from fractions import Fraction
import hashlib
from io import BytesIO
import json
from pathlib import Path
import shutil
import tempfile

import numpy as np
from PIL import Image


KEY_NAME = 'local-border-connected-black-key-v1'
KEY_TOLERANCE = 12
TARGET_SIZE = (256, 256)
SAMPLE_COUNTS = (8, 16)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def border_black_key(rgba):
    """Zero alpha only for <=12 RGB pixels 4-connected to any canvas border.

    Scanline flood fill retains enclosed black islands and all RGB, including
    hidden RGB. This local chroma key can remove connected dark outlines and
    leave dark/compressed edge fringes. It is not a PixelLab method or repair.
    """
    if rgba.dtype != np.uint8 or rgba.ndim != 3 or rgba.shape[2] != 4:
        raise ValueError('Expected uint8 RGBA')
    height, width = rgba.shape[:2]
    if not width or not height:
        raise ValueError('Empty key canvas')
    remaining = np.all(rgba[..., :3] <= KEY_TOLERANCE, axis=2)
    removed = np.zeros((height, width), dtype=bool)
    pending = deque((x, y) for y in (0, height-1) for x in range(width) if remaining[y, x])
    pending.extend((x, y) for x in (0, width-1) for y in range(height) if remaining[y, x])
    while pending:
        x, y = pending.pop()
        if not remaining[y, x]:
            continue
        left = right = x
        while left > 0 and remaining[y, left-1]:
            left -= 1
        while right+1 < width and remaining[y, right+1]:
            right += 1
        remaining[y, left:right+1] = False
        removed[y, left:right+1] = True
        for neighbor in (y-1, y+1):
            if not 0 <= neighbor < height:
                continue
            span = remaining[neighbor, left:right+1]
            starts = np.flatnonzero(span & np.concatenate(([True], ~span[:-1])))
            pending.extend((left+int(start), neighbor) for start in starts)
    output = rgba.copy()
    output[removed, 3] = 0
    # Executable preservation assertions, independent of visual acceptance.
    if not np.array_equal(output[..., :3], rgba[..., :3]):
        raise RuntimeError('Key unexpectedly changed source RGB')
    if not np.array_equal(output[~removed], rgba[~removed]):
        raise RuntimeError('Key unexpectedly changed an unselected pixel')
    return output, {'border_connected_pixels': int(removed.sum()),
                    'alpha_values_changed': int(np.count_nonzero(removed & (rgba[..., 3] != 0))),
                    'rgb_byte_preservation': True}


def png_bytes(rgba):
    stream = BytesIO()
    Image.fromarray(rgba).save(stream, format='PNG')
    return stream.getvalue()


def nearest(rgba):
    return np.array(Image.fromarray(rgba).resize(TARGET_SIZE, Image.Resampling.NEAREST))


def _native_source(root, record, dimensions):
    relative = Path(record['file'])
    source = (root / relative).resolve()
    if relative.is_absolute() or not source.is_relative_to(root):
        raise ValueError('Native frame path escapes its manifest folder')
    raw = source.read_bytes()
    if sha(raw) != record['sha256']:
        raise ValueError(f"Native frame hash mismatch at index {record['index']}")
    with Image.open(BytesIO(raw)) as image:
        if image.size != tuple(dimensions) or getattr(image, 'n_frames', 1) != 1:
            raise ValueError('Native source dimensions/frame count differ')
        rgba = np.array(image.convert('RGBA'))
    pts = Fraction(record['pts_seconds_exact'])
    if pts != record['pts_ticks'] * Fraction(record['time_base']):
        raise ValueError('Native PTS seconds differ from ticks/time base')
    return raw, rgba, pts


def sample_indices(start, end, count, mode):
    if mode == 'once':
        return [start + sample*(end-start-1)//(count-1) for sample in range(count)]
    return [start + sample*(end-start)//count for sample in range(count)]


def selection_profiles(start, end, mode, indices_file=None):
    """Choose uniform indices or validate an explicit frozen manual selection.

    No phase/event detection, frame repair, clock edits, or fallback selection.
    """
    if indices_file is None:
        return {count: sample_indices(start, end, count, mode) for count in SAMPLE_COUNTS}, None
    if mode != 'once':
        raise ValueError('--indices-file is only supported in once mode')
    raw = Path(indices_file).read_bytes()
    profiles = json.loads(raw)
    if not isinstance(profiles, dict) or set(profiles) != {'8', '16'}:
        raise ValueError('Indices JSON must contain exactly the 8 and 16 profiles')
    selected = {}
    for count in SAMPLE_COUNTS:
        values = profiles[str(count)]
        if not isinstance(values, list) or len(values) != count:
            raise ValueError(f'Indices profile {count} must contain exactly {count} native indices')
        if any(type(value) is not int or not start <= value < end for value in values):
            raise ValueError(f'Indices profile {count} must use whole native indices inside the candidate interval')
        if any(right <= left for left, right in zip(values, values[1:])):
            raise ValueError(f'Indices profile {count} must be strictly increasing and unique')
        if values[0] != start or values[-1] != end-1:
            raise ValueError(f'Indices profile {count} must include candidate start and final native frame')
        selected[count] = values
    return selected, raw


def extract(manifest_path, output, *, start=16, end=64, duration=None, mode='loop', indices_file=None):
    manifest_path = Path(manifest_path).resolve()
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise ValueError('Output must not exist; existing work is never overwritten')
    if type(start) is not int or type(end) is not int or end-start < max(SAMPLE_COUNTS) or start < 0:
        raise ValueError('Candidate interval needs at least 16 consecutive native frames')
    if mode not in {'loop', 'once'}:
        raise ValueError('Mode must be loop or once')
    if mode == 'once' and duration is not None:
        raise ValueError('One-shot timing uses native PTS; --duration is only for loop mode')
    if mode == 'loop':
        duration = Fraction(2) if duration is None else Fraction(duration)
        if duration <= 0:
            raise ValueError('Authored cycle duration must be positive')
    profiles, indices_raw = selection_profiles(start, end, mode, indices_file)
    manifest_raw = manifest_path.read_bytes()
    source_manifest = json.loads(manifest_raw)
    dimensions = source_manifest['native_dimensions']
    if len(dimensions) != 2 or any(type(side) is not int or side <= 0 for side in dimensions):
        raise ValueError('Invalid native canvas')
    records = source_manifest['native_frames']
    by_index = {record['index']: record for record in records}
    if len(by_index) != len(records):
        raise ValueError('Duplicate native frame indices')
    if any(index not in by_index for index in range(start, end)):
        raise ValueError('Every candidate native frame must exist')
    if end in by_index:
        end_pts = Fraction(by_index[end]['pts_seconds_exact'])
        boundary_authority = 'Native exclusive-end frame PTS'
    elif mode == 'once' and end == max(by_index)+1:
        value = source_manifest.get('presentation_end_seconds_exact',
            source_manifest.get('source_presentation_end_seconds_exact'))
        if value is None:
            raise ValueError('One-shot native presentation-end timestamp is required')
        end_pts = Fraction(value)
        boundary_authority = 'Manifest native presentation-end timestamp; no fabricated end frame'
    else:
        raise ValueError('Candidate exclusive-end PTS frame must exist outside full one-shot mode')
    selected = {index for values in profiles.values() for index in values}
    native, candidate = {}, []
    previous_pts = None
    # Validate every interval frame, not just sparse exported samples; no writes.
    for index in range(start, end+int(end in by_index)):
        record = by_index[index]
        raw, rgba, pts = _native_source(manifest_path.parent, record, dimensions)
        if previous_pts is not None and pts <= previous_pts:
            raise ValueError('Candidate native presentation timestamps must increase')
        previous_pts = pts
        candidate.append(dict(record))
        if index in selected:
            native[index] = (raw, rgba)
    if end_pts <= Fraction(by_index[end-1]['pts_seconds_exact']):
        raise ValueError('Presentation end must follow the final native frame PTS')
    native_span = end_pts - Fraction(by_index[start]['pts_seconds_exact'])
    if mode == 'once':
        duration = native_span
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=output.name+'.building-', dir=output.parent))
    try:
        files = []

        def write(relative, raw):
            path = stage / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            files.append({'file': relative, 'sha256': sha(raw), 'bytes': len(raw)})

        write('SOURCE-MANIFEST.json', manifest_raw)
        if indices_raw is not None:
            write('INDICES.json', indices_raw)
        source_records, resized = {}, {}
        for index in sorted(selected):
            raw, rgba = native[index]
            keyed, stats = border_black_key(rgba)
            source_file = f'native/source-{index:06d}.png'
            keyed_file = f'native/keyed-{index:06d}.png'
            write(source_file, raw)
            write(keyed_file, png_bytes(keyed))
            resized[index] = nearest(rgba), nearest(keyed)
            source_records[index] = {**by_index[index], 'embedded_source': source_file,
                'embedded_keyed_native': keyed_file, 'native_rgba_sha256': sha(rgba.tobytes()),
                'keyed_native_rgba_sha256': sha(keyed.tobytes()), 'key_statistics': stats}
        clips = []
        for count in SAMPLE_COUNTS:
            prefix = 'cycle' if mode == 'loop' else 'once'
            indices = profiles[count]
            frames = []
            columns = 8
            source_atlas = np.zeros((256*((count+columns-1)//columns), 256*columns, 4), np.uint8)
            keyed_atlas = source_atlas.copy()
            for sample in range(count):
                index = indices[sample]
                source, keyed = resized[index]
                x, y = sample % columns * 256, sample // columns * 256
                source_atlas[y:y+256, x:x+256] = source
                keyed_atlas[y:y+256, x:x+256] = keyed
                source_file = f'{prefix}-{count}/source-{sample:02d}.png'
                keyed_file = f'{prefix}-{count}/sprite-{sample:02d}.png'
                write(source_file, png_bytes(source)); write(keyed_file, png_bytes(keyed))
                if mode == 'once':
                    next_pts = Fraction(by_index[indices[sample+1]]['pts_seconds_exact']) if sample+1 < count else end_pts
                    hold = next_pts - Fraction(by_index[index]['pts_seconds_exact'])
                else:
                    hold = duration/count
                frames.append({'sample': sample, 'native_index': index, 'source': source_records[index],
                    'source_png': source_file, 'sprite_png': keyed_file,
                    'source_rgba_sha256': sha(source.tobytes()), 'sprite_rgba_sha256': sha(keyed.tobytes()),
                    'duration_seconds': [hold.numerator, hold.denominator], 'atlas_rect': [x, y, 256, 256]})
            source_sheet, keyed_sheet = f'{prefix}-{count}/source-atlas.png', f'{prefix}-{count}/sprite-atlas.png'
            write(source_sheet, png_bytes(source_atlas)); write(keyed_sheet, png_bytes(keyed_atlas))
            clips.append({'id': f'candidate-{prefix}-{count}', 'sample_count': count, 'loop': mode == 'loop', 'mode': mode,
                'frame_size': [256, 256], 'sheet_columns': columns, 'source_atlas': source_sheet,
                'sprite_atlas': keyed_sheet, 'duration_seconds': [duration.numerator, duration.denominator],
                'timing_origin': ('Selected native PTS differences plus native end minus final selected PTS; no inferred events'
                    if mode == 'once' else 'Explicit uniformly held local derivative; not inferred source sprite fps'), 'frames': frames})
        result = {'version': 1, 'kind': 'local-h3-sprite-cycle-derivative', 'mode': mode,
            'authority': 'Locally authored sampling/key/resize/export; not recovered PixelLab code',
            'source_manifest_sha256': sha(manifest_raw), 'native_video_sha256': source_manifest.get('native_video_sha256'),
            'source_video_embedded': False, 'embedded_native_indices': sorted(selected),
            'source_manifest_original_frame_paths_are_external': True,
            'source_presentation_end_seconds_exact': source_manifest.get('presentation_end_seconds_exact'),
            'native_canvas': dimensions, 'output_canvas': [256, 256],
            'sampling': {'policy': 'explicit-manual-indices-v1' if indices_raw is not None else 'uniform-native-index-v1',
                'manual_curation': indices_raw is not None,
                'profiles': {str(count): values for count, values in profiles.items()},
                'indices_file': 'INDICES.json' if indices_raw is not None else None,
                'indices_file_sha256': sha(indices_raw) if indices_raw is not None else None,
                'boundary': 'Local sampling selection only; inspect the complete native take first. No inferred hit/event or recovered PixelLab algorithm.'},
            'candidate': {'native_interval': [start, end], 'interval_semantics': 'start inclusive, end exclusive',
                'selection': ('Explicit manual one-shot interval; both endpoint frames included; no inferred hit/event'
                    if mode == 'once' else 'Explicit manual candidate interval; repeated gait phase is a visual proposal, not detector output'),
                'source_pts_span_seconds_exact': str(native_span),
                'exclusive_end_boundary': {'index': end, 'pts_seconds_exact': str(end_pts), 'authority': boundary_authority},
                'exclusive_end_record_included': end in by_index,
                ('native_records_including_exclusive_end' if end in by_index else 'native_records'): candidate},
            'key': {'name': KEY_NAME, 'tolerance_per_rgb_channel_inclusive': KEY_TOLERANCE,
                'connectivity': 4, 'seeds': 'All eligible pixels on all four borders', 'changed_channels': 'alpha only',
                'risk': 'Imperfect key: connected dark outlines can disappear and compressed dark edge fringes can remain'},
            'transform': {'resize': 'Whole fixed canvas nearest-neighbor to 256x256', 'crop': None,
                'per_frame_translation': [0, 0], 'anchor': 'Unchanged fixed canvas origin; no per-frame recenter/reanchor',
                'quantization': False, 'recoloring': False, 'ai_repair': False},
            'assertions': {'all_candidate_native_hashes_verified': True, 'all_native_canvas_sizes_equal': True,
                'native_pts_preserved': True, 'key_preserves_all_rgb_bytes': True,
                'both_variants_same_candidate_interval': True, 'uniform_whole_canvas_resize': True,
                'per_frame_transform_variation': False, 'per_frame_reanchor': False},
            'artistic_acceptance': 'unreviewed; no universal quality gate', 'clips': clips}
        write('index.html', player_html(result).encode())
        result['files'] = files
        (stage/'MANIFEST.json').write_text(json.dumps(result, indent=2)+'\n')
        stage.rename(output)
    except BaseException:
        shutil.rmtree(stage)
        raise
    return result


def player_html(manifest):
    data = json.dumps({'clips': manifest['clips'], 'sampling': manifest.get('sampling')}, separators=(',', ':')).replace('<', '\\u003c')
    return PLAYER.replace('__DATA__', data)


PLAYER = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Local candidate sprite clip</title><style>
body{font:16px system-ui;margin:24px auto;padding:0 20px;max-width:940px;background:#202524;color:#eee}button,select{font:inherit;padding:8px;margin:4px}section{display:flex;gap:24px;flex-wrap:wrap}figure{margin:10px 0}canvas{image-rendering:pixelated;max-width:100%;background:#000}.checker{background-color:#ddd;background-image:conic-gradient(#aaa 25%,#ddd 0 50%,#aaa 0 75%,#ddd 0);background-size:20px 20px}p{line-height:1.6}output{display:block;margin:14px 0;font-variant-numeric:tabular-nums}a{color:#a8e4cf}</style>
<h1>Local candidate clip · unreviewed</h1><p>Same manually selected native interval, two sampling variants. Loop mode uses uniformly authored holds; one-shot mode uses selected native PTS differences and the native end timestamp. No sprite frame rate or gameplay event is inferred. Full canvas, fixed origin, nearest-neighbor only.</p>
<p>Local border-connected black key v1 (RGB ≤12, four-connected). Dark connected outlines may disappear; edge fringes may remain. This derivative is not a recovered PixelLab algorithm or art-quality approval.</p>
<p id="sampling">Inspect the complete native take before assessing a sparse derivative.</p>
<label>Samples <select id="variant"><option value="0">8 samples</option><option value="1">16 samples</option></select></label>
<button id="play" disabled>Play</button><button id="replay" disabled>Replay</button><button id="prev" disabled>Step backward</button><button id="next" disabled>Step forward</button>
<label>Speed <select id="speed"><option value="0.25">0.25×</option><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select></label>
<output id="status">Loading exact local PNGs…</output><section><figure><figcaption>Source · same 256px canvas</figcaption><canvas id="source" width="256" height="256"></canvas></figure><figure><figcaption>Alpha-keyed derivative · checkerboard</figcaption><canvas id="keyed" class="checker" width="256" height="256"></canvas></figure></section>
<p><a href="MANIFEST.json">Manifest, source hashes, native indices and PTS</a>. Native source/keyed PNGs and both atlases are included. Original video is not embedded.</p>
<script>'use strict';const data=__DATA__,el=id=>document.getElementById(id);let variant=0,phase=0,playing=false,completed=false,last=null,images,loaded=false,handle=null;
el('sampling').textContent=data.sampling?.manual_curation?'Explicit manually curated native indices; source PTS holds retained. This is local sampling, not detected gameplay events.':'Uniform native-index sampling can omit brief motion. Inspect the complete native take first.';
const clip=()=>data.clips[variant],count=()=>clip().sample_count,mode=()=>clip().loop?'loop':'once',seconds=d=>d[0]/d[1],total=()=>seconds(clip().duration_seconds);
function frameAt(time){let end=0;for(let i=0;i<count()-1;i++){end+=seconds(clip().frames[i].duration_seconds);if(time<end)return i;}return count()-1;}
function frameStart(index){let start=0;for(let i=0;i<index;i++)start+=seconds(clip().frames[i].duration_seconds);return start;}
window.spriteReviewState=()=>({variant:count(),frame:frameAt(phase),native_index:clip().frames[frameAt(phase)].native_index,playing,completed,mode:mode(),rate:Number(el('speed').value),time:phase,loaded,duration_seconds:clip().duration_seconds.slice(),holds:clip().frames.map(f=>f.duration_seconds.slice())});
function draw(){const i=frameAt(phase),f=clip().frames[i];for(const [canvas,key]of[['source','source_png'],['keyed','sprite_png']]){const ctx=el(canvas).getContext('2d');ctx.clearRect(0,0,256,256);ctx.drawImage(images[f[key]],0,0);}el('status').textContent=`${mode()} · ${i+1}/${count()} · native index ${f.native_index} · native PTS ${f.source.pts_seconds_exact}s · hold ${f.duration_seconds.join('/')}s${completed?' · Completed; use Replay to restart':''}`;}
function pause(){playing=false;el('play').textContent='Play';last=null;if(handle!==null)cancelAnimationFrame(handle);handle=null;}
function tick(now){if(!playing)return;if(last!==null){const next=phase+(now-last)/1000*Number(el('speed').value);if(mode()==='once'&&next>=total()){phase=total();completed=true;pause();draw();return;}phase=mode()==='loop'?next%total():next;}last=now;draw();handle=requestAnimationFrame(tick);}
function play(){if(completed)return;playing=true;el('play').textContent='Pause';last=null;handle=requestAnimationFrame(tick);}
el('play').onclick=()=>{if(playing)pause();else play();};
el('replay').onclick=()=>{pause();phase=0;completed=false;draw();play();};
for(const [id,step]of[['prev',-1],['next',1]])el(id).onclick=()=>{pause();const next=frameAt(phase)+step,index=mode()==='loop'?(next+count())%count():Math.max(0,Math.min(count()-1,next));phase=frameStart(index);draw();};
el('variant').onchange=()=>{variant=Number(el('variant').value);if(images)draw();};
(async()=>{images={};const paths=[...new Set(data.clips.flatMap(c=>c.frames.flatMap(f=>[f.source_png,f.sprite_png])))];await Promise.all(paths.map(path=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{images[path]=im;resolve();};im.onerror=()=>reject(Error('Failed local frame '+path));im.src=path;})));loaded=true;for(const id of['play','replay','prev','next'])el(id).disabled=false;draw();})().catch(error=>{el('status').textContent=error.message;});
</script></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New directory; existing paths are refused')
    parser.add_argument('--start', type=int, default=16)
    parser.add_argument('--end', type=int, default=64, help='Exclusive end index; once mode also permits last native index + 1 using manifest end PTS')
    parser.add_argument('--mode', choices=['loop', 'once'], default='loop')
    parser.add_argument('--indices-file', type=Path, default=None, help='Once-only frozen JSON with exact 8 and 16 native-index arrays; endpoints required')
    parser.add_argument('--duration', type=Fraction, default=None, help='Explicit local loop seconds (default 2); not accepted in once mode')
    args = parser.parse_args()
    result = extract(args.manifest, args.output, start=args.start, end=args.end, duration=args.duration, mode=args.mode,
        indices_file=args.indices_file)
    print(json.dumps({'output': str(args.output), 'mode': result['mode'], 'candidate': result['candidate']['native_interval'],
        'variants': [clip['sample_count'] for clip in result['clips']], 'artistic_acceptance': result['artistic_acceptance']}))


if __name__ == '__main__':
    main()

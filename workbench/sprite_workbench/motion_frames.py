"""Bounded offline video decoding and explicitly authored frame sampling.

FFmpeg conversion is local video admission, not PixelLab's private sampler or
cutout. No crop, deduplication, scaling, alpha reconstruction or model runs.
"""
from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

import numpy as np

from .core import ValidationError, digest, validate_id

MAX_MEDIA_BYTES = 64 * 1024 * 1024
MAX_DECODE_BYTES = 512 * 1024 * 1024
MAX_FRAMES = 512
MAX_SIDE = 2048
TIMEOUT_SECONDS = 60
POLICY = 'authored local video import; not a recovered PixelLab private sampler'


class VideoExtractionError(ValidationError):
    def __init__(self, reason, receipt):
        super().__init__(reason)
        self.receipt = receipt

    def to_dict(self):
        return {**super().to_dict(), 'extraction_failure': self.receipt}


def _pair(value):
    return [value.numerator, value.denominator]


def _run(argv, directory, name, deadline, output_limit):
    prlimit = shutil.which('prlimit')
    if not prlimit:
        raise ValidationError('Local Linux prlimit is unavailable; bounded video decoding is required')
    command = [prlimit, '--as=2147483648', '--cpu=60',
               f'--fsize={output_limit}', '--core=0', '--', *argv]
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise ValidationError('Video extraction exceeded the 60 second budget')
    out, err = directory / (name + '.out'), directory / (name + '.err')
    try:
        with out.open('wb') as stdout, err.open('wb') as stderr:
            completed = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=stdout,
                stderr=stderr, timeout=remaining, check=False, cwd=directory,
                env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
    except subprocess.TimeoutExpired as exc:
        raise ValidationError('Video extraction exceeded the 60 second budget') from exc
    if completed.returncode:
        # No caller paths or credentials are forwarded to decoder processes.
        detail = err.read_bytes()[:2000].decode('utf8', errors='replace')
        raise ValidationError(f'{name} failed ({completed.returncode}): {detail}')
    if out.stat().st_size > output_limit:
        raise ValidationError(f'{name} output exceeded its byte budget')
    return out


def _timing(probe):
    streams, frames = probe.get('streams', []), probe.get('frames', [])
    if len(streams) != 1 or not 1 <= len(frames) <= MAX_FRAMES:
        raise ValidationError('Video must decode to 1..512 frames in its first video stream')
    stream = streams[0]
    width, height = stream.get('width'), stream.get('height')
    if type(width) is not int or type(height) is not int or not 1 <= min(width, height) or max(width, height) > MAX_SIDE:
        raise ValidationError('Video canvas must fit 1..2048 pixels on each side')
    if width * height * 4 * len(frames) > MAX_DECODE_BYTES:
        raise ValidationError('Decoded video exceeds the 512 MiB RGBA budget')
    try:
        base = Fraction(stream['time_base'])
        pts = [int(f['pts']) for f in frames]
        if base <= 0 or any(b <= a for a, b in zip(pts, pts[1:])):
            raise ValueError('nonmonotonic PTS')
        tail = frames[-1].get('duration', frames[-1].get('pkt_duration'))
        if tail is not None and int(tail) > 0:
            tail = int(tail)
            tail_origin = 'last decoded frame duration'
        else:
            tail = int(stream['start_pts']) + int(stream['duration_ts']) - pts[-1]
            tail_origin = 'stream end timestamp minus last frame PTS'
        ticks = [b-a for a, b in zip(pts, pts[1:])] + [tail]
        holds = [t * base for t in ticks]
        if any(h <= 0 or h > 3600 for h in holds) or sum(holds) > 3600:
            raise ValueError('duration budget')
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValidationError('Exact monotonic integer PTS and a positive terminal duration are required; no FPS guess is substituted') from exc
    return width, height, pts, holds, base, tail_origin


def extract_video(store, media: bytes):
    """Retain bytes; decode all first-stream frames with their exact source clock.

    Failures after byte admission retain an immutable failure receipt, available
    as VideoExtractionError.receipt. Only MP4/MOV/Matroska/WebM demuxers and local
    file/pipe protocols are admitted. Paths/URLs/filters are never request inputs.
    """
    if not isinstance(media, bytes) or not 1 <= len(media) <= MAX_MEDIA_BYTES:
        raise ValidationError('Video media must be 1 byte..64 MiB of supplied immutable bytes')
    media_id = store.put_bytes(media)
    deadline = time.monotonic() + TIMEOUT_SECONDS
    tools = {}
    try:
        for name in ('ffprobe', 'ffmpeg'):
            executable = shutil.which(name)
            if not executable:
                raise ValidationError(f'Local {name} is unavailable; no fallback decoder is used')
            tools[name] = {'path': str(Path(executable).resolve()), 'binary_sha256': digest(Path(executable).read_bytes())}
        with tempfile.TemporaryDirectory(prefix='sprite-motion-') as temp:
            directory = Path(temp)
            source = directory / 'source.media'
            source.write_bytes(media)
            for name, tool in tools.items():
                version = _run([tool['path'], '-version'], directory, name + '-version', deadline, 65536)
                tool['version'] = version.read_text(errors='replace').splitlines()[0]
            common = ['-v', 'error', '-protocol_whitelist', 'file,pipe', '-format_whitelist', 'mov,matroska,webm']
            probe_path = _run([tools['ffprobe']['path'], *common, '-select_streams', 'v:0',
                '-show_streams', '-show_frames', '-read_intervals', '%+#514', '-show_entries',
                'stream=index,codec_name,width,height,pix_fmt,time_base,start_pts,duration_ts:frame=pts,pkt_duration,duration,width,height',
                '-of', 'json', str(source)], directory, 'ffprobe', deadline, 4 * 1024 * 1024)
            probe = json.loads(probe_path.read_bytes())
            width, height, pts, holds, base, tail_origin = _timing(probe)
            if any(f.get('width') != width or f.get('height') != height for f in probe['frames']):
                raise ValidationError('Changing native frame dimensions are unsupported')
            raw_path = _run([tools['ffmpeg']['path'], *common, '-threads', '1', '-noautorotate',
                '-i', str(source), '-map', '0:v:0', '-an', '-sn', '-dn', '-frames:v', '513',
                '-threads', '1', '-fps_mode', 'passthrough', '-pix_fmt', 'rgba', '-f', 'rawvideo', 'pipe:1'],
                directory, 'ffmpeg', deadline, MAX_DECODE_BYTES)
            frame_bytes = width * height * 4
            if raw_path.stat().st_size != frame_bytes * len(pts):
                raise ValidationError('Probe/decode frame count or canvas disagrees; nothing is silently truncated')
            records = []
            opaque = True
            with raw_path.open('rb') as handle:
                for index, hold in enumerate(holds):
                    a = np.frombuffer(handle.read(frame_bytes), dtype=np.uint8).reshape(height, width, 4)
                    opaque = opaque and bool(np.all(a[..., 3] == 255))
                    records.append({'index': index, 'pts': pts[index], 'raster': store.put_raster(a), 'duration': _pair(hold),
                                    'pivot': [0, 0], 'direction': 'unspecified'})
            probe_id = store.put_bytes(probe_path.read_bytes())
        extraction = store.put_json({'kind': 'motion-extraction', 'version': 1, 'policy': POLICY,
            'media': media_id, 'media_sha256': media_id, 'probe': probe_id, 'tools': tools,
            'canvas': [width, height], 'frame_count': len(records), 'frames': records,
            'pts': pts, 'time_base': _pair(base), 'pts_origin': pts[0],
            'duration': _pair(sum(holds)), 'terminal_duration_basis': tail_origin,
            'native_clock': 'integer presentation timestamps; adjacent PTS differences; terminal duration declared separately',
            'decode': 'first video stream; RGBA conversion; no autorotation/scaling/crop/deduplication',
            'opaque': opaque, 'alpha_policy': 'decoded alpha retained; no reconstruction or cutout',
            'source_ids': [media_id, probe_id], 'visual_acceptance': 'unreviewed'})
        sequence = store.put_json({'kind': 'sequence', 'version': 1, 'canvas': [width, height],
            'frames': records, 'loop': False, 'play_count': 1, 'visual_approval': 'unreviewed',
            'metadata': {'source_ids': [media_id, extraction, probe_id], 'motion_extraction': extraction,
                'clock_note': 'Exact source PTS holds; local inspection plays once (authored policy).',
                'loop_policy': 'authored one-shot inspection; no loop inferred from video', 'policy': POLICY}})
        return {'media': media_id, 'extraction': extraction, 'sequence': sequence,
                'frame_count': len(records), 'canvas': [width, height], 'duration': _pair(sum(holds)),
                'clock_note': 'Exact source PTS holds; authored one-shot inspection'}
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        receipt = store.put_json({'kind': 'motion-extraction-failure', 'version': 1, 'media': media_id,
            'source_ids': [media_id], 'policy': POLICY, 'reason': str(exc)[:4000], 'tools': tools})
        raise VideoExtractionError(str(exc), receipt) from exc


def sample_frames(store, extraction, *, indices, holds, loop, roles):
    """Author a sample without altering pixels; repeated indices stay explicit."""
    validate_id(extraction)
    doc = store.get_json(extraction)
    if doc.get('kind') != 'motion-extraction' or doc.get('version') != 1:
        raise ValidationError('An admitted motion extraction is required')
    if (type(doc.get('frame_count')) is not int or not 1 <= doc['frame_count'] <= MAX_FRAMES
            or not isinstance(doc.get('frames'), list) or len(doc['frames']) != doc['frame_count']
            or not isinstance(doc.get('pts'), list) or len(doc['pts']) != doc['frame_count']
            or not isinstance(doc.get('canvas'), list) or len(doc['canvas']) != 2
            or any(type(v) is not int or not 1 <= v <= MAX_SIDE for v in doc['canvas'])
            or doc.get('media_sha256') != doc.get('media')):
        raise ValidationError('Malformed extraction frame/media metadata')
    validate_id(doc['media'])
    store.get_bytes(doc['media'], max_bytes=MAX_MEDIA_BYTES)
    if not isinstance(indices, list) or not 1 <= len(indices) <= MAX_FRAMES or any(type(i) is not int or not 0 <= i < doc['frame_count'] for i in indices):
        raise ValidationError('Provide 1..512 explicit in-range native frame indices')
    if type(loop) is not bool or not isinstance(roles, list) or len(roles) != len(indices) or any(not isinstance(r, str) or not r.strip() or len(r) > 128 for r in roles):
        raise ValidationError('Explicit loop boolean and one bounded role per sample are required')
    if not isinstance(holds, list) or len(holds) != len(indices):
        raise ValidationError('An explicit rational hold per sample is required')
    times = []
    for hold in holds:
        if not isinstance(hold, list) or len(hold) != 2 or any(type(v) is not int or not 1 <= v <= 9007199254740991 for v in hold):
            raise ValidationError('Authored holds must be positive integer rational pairs')
        f = Fraction(*hold)
        if f > 3600:
            raise ValidationError('Authored sample hold exceeds 3600 seconds')
        times.append(f)
    if sum(times) > 3600:
        raise ValidationError('Authored sample duration exceeds 3600 seconds')
    # Validate all referenced rasters before retaining a decision or sequence.
    for i in set(indices):
        raster = store.get_raster(doc['frames'][i]['raster'])
        if [raster.shape[1], raster.shape[0]] != doc['canvas']:
            raise ValidationError('Extraction raster canvas disagrees')
    mapping = [{'sample_index': n, 'native_index': i, 'native_pts': doc['pts'][i],
                'raster': doc['frames'][i]['raster'], 'duration': _pair(t), 'role': r}
               for n, (i, t, r) in enumerate(zip(indices, times, roles))]
    decision = store.put_json({'kind': 'motion-sample-decision', 'version': 1, 'policy': POLICY,
        'extraction': extraction, 'media': doc['media'], 'media_sha256': doc['media_sha256'],
        'source_ids': [extraction, doc['media']], 'samples': mapping,
        'loop': loop, 'play_count': 0 if loop else 1, 'selection': 'explicit authored indices, roles and holds',
        'pixel_changes': 'none; no crop/recenter/deduplication/cutout', 'visual_acceptance': 'unreviewed'})
    sequence = store.put_json({'kind': 'sequence', 'version': 1, 'canvas': doc['canvas'],
        'frames': [{'index': n, 'raster': sample['raster'], 'duration': sample['duration'],
                    'pivot': [0, 0], 'direction': 'unspecified'} for n, sample in enumerate(mapping)],
        'loop': loop, 'play_count': 0 if loop else 1, 'visual_approval': 'unreviewed',
        'metadata': {'source_ids': [extraction, doc['media'], decision], 'motion_extraction': extraction,
            'sample_decision': decision, 'policy': POLICY, 'clock_note': 'Explicit authored sample holds; native PTS retained in decision'}})
    return {'sequence': sequence, 'decision': decision, 'extraction': extraction, 'media': doc['media'],
            'frame_count': len(mapping), 'duration': _pair(sum(times))}

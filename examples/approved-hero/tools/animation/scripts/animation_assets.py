#!/usr/bin/env python3
"""Validate atlas clips, measure temporal changes and produce hash-bound review sheets.

Accepts the native clips.json contract or the portable equivalent described in
references/manifest.md. Metrics are review hints, never aesthetic approval.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from PIL import Image, ImageDraw

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def asset(root, relative):
    p = (root / relative).resolve()
    if not p.is_relative_to(root.resolve()) or not p.is_file():
        raise ValueError(f'Asset outside root or missing: {relative}')
    return p

def positive(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{label} must be finite and positive')
    return value

def frame_images(root, clip):
    sheet = Image.open(asset(root, clip['sheet'])).convert('RGBA')
    w, h = clip['frame_size']
    columns = clip['sheet_columns']
    if any(isinstance(v, bool) or not isinstance(v, int) or v < 1 for v in [w, h, columns]):
        raise ValueError('Positive integer cell size/columns required')
    if sheet.width % w or sheet.height % h or columns != sheet.width // w:
        raise ValueError('Atlas dimensions disagree with cell size/columns')
    for f in clip['frames']:
        idx = f['atlas_index']
        if isinstance(idx, bool) or not isinstance(idx, int) or idx < 0:
            raise ValueError('Invalid atlas_index')
        x, y = idx % columns * w, idx // columns * h
        if y + h > sheet.height:
            raise ValueError('Atlas region outside sheet')
        yield sheet.crop((x, y, x + w, y + h))

def validate(path):
    path = Path(path).resolve()
    data = json.loads(path.read_text())
    if not isinstance(data.get('clips'), list) or not data['clips']:
        raise ValueError('Nonempty clips list required')
    errors, warnings, inputs, clips = [], [], {}, []
    identities = set()
    for clip in data['clips']:
        key = f"{clip.get('actor', '')}/{clip.get('name', '')}"
        try:
            if not clip.get('actor') or not clip.get('name') or key in identities:
                raise ValueError('Missing or duplicate actor/name')
            if not isinstance(clip['actor'], str) or not re.fullmatch(r'[A-Za-z0-9_-]+', clip['actor']):
                raise ValueError('Actor ID must be safe for a resource filename')
            if any(not isinstance(clip.get(k), str) or not clip[k].strip() for k in ['name', 'action', 'direction']):
                raise ValueError('Nonempty name, action and direction required')
            identities.add(key)
            if not isinstance(clip.get('loop'), bool) or not clip.get('frames'):
                raise ValueError('Explicit loop and nonempty frames required')
            fps = positive(clip.get('video_fps', data.get('video_fps')), 'video_fps')
            pivot = clip['pivot_pixels']
            if len(pivot) != 2 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in pivot):
                raise ValueError('Finite two-coordinate pivot required')
            ground = clip.get('ground_pivot_pixels', pivot)
            if not isinstance(ground, list) or len(ground) != 2 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in ground):
                raise ValueError('Finite two-coordinate ground pivot required')
            images = list(frame_images(path.parent, clip))
            inputs[clip['sheet']] = digest(asset(path.parent, clip['sheet']))
            frame_hashes = []
            seconds = 0.0
            for index, (f, image) in enumerate(zip(clip['frames'], images)):
                ticks = positive(f['duration_video_frames'], 'duration_video_frames')
                duration = ticks / fps
                if 'duration_seconds' in f and not math.isclose(positive(f['duration_seconds'], 'duration_seconds'), duration, rel_tol=1e-8):
                    raise ValueError(f'Frame {index}: ticks and seconds disagree')
                sha = hashlib.sha256(image.tobytes()).hexdigest()
                if f.get('pixel_sha256', sha) != sha:
                    raise ValueError(f'Frame {index}: pixel hash mismatch')
                frame_hashes.append(sha)
                seconds += duration
                bbox = image.getchannel('A').getbbox()
                if bbox is None:
                    warnings.append({'clip': key, 'frame': index, 'kind': 'blank'})
                elif bbox[0] == 0 or bbox[1] == 0 or bbox[2] == image.width or bbox[3] == image.height:
                    warnings.append({'clip': key, 'frame': index, 'kind': 'edge_contact'})
            for event in clip.get('timeline_events', []):
                if not isinstance(event.get('frame'), int) or isinstance(event.get('frame'), bool) or not 0 <= event['frame'] < len(images) or not isinstance(event.get('name'), str) or not event['name']:
                    raise ValueError('Timeline event must have an existing integer frame and nonempty name')
            clips.append({'id': key, 'frames': len(images), 'seconds': seconds, 'frame_hashes': frame_hashes})
        except (ValueError, KeyError, TypeError, OSError) as exc:
            errors.append({'clip': key, 'error': str(exc)})
    try:
        bindings = data.get('gameplay_bindings', {})
        if not isinstance(bindings, dict):
            raise ValueError('gameplay_bindings must be an object')
        for actor, states in bindings.items():
            if not isinstance(states, dict) or not states:
                raise ValueError('Actor bindings need a nonempty state object')
            for state, directions in states.items():
                if not isinstance(state, str) or not isinstance(directions, dict) or not directions:
                    raise ValueError('Each state needs direction bindings')
                for direction, binding in directions.items():
                    values = list(binding.values()) if isinstance(binding, dict) else [binding]
                    if direction not in ['up', 'down', 'left', 'right'] or not values:
                        raise ValueError('Invalid direction or empty equipment bindings')
                    if any(not isinstance(v, str) or actor + '/' + v not in identities for v in values):
                        raise ValueError('Gameplay binding references missing clip')
    except (ValueError, TypeError) as exc:
        errors.append({'clip': 'gameplay_bindings', 'error': str(exc)})
    snapshot = {'manifest_sha256': digest(path), 'sheets': dict(sorted(inputs.items()))}
    fingerprint = hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'manifest': str(path), 'input_fingerprint': fingerprint, 'snapshot': snapshot,
            'clips': clips, 'clip_count': len(clips), 'frame_count': sum(c['frames'] for c in clips),
            'errors': errors, 'warnings': warnings, 'accepted': not errors}

def geometry(image):
    pixels = list(image.get_flattened_data())
    opaque = {i for i, p in enumerate(pixels) if p[3] > 0}
    centroid = [sum(i % image.width for i in opaque) / len(opaque),
                sum(i // image.width for i in opaque) / len(opaque)] if opaque else None
    return pixels, opaque, centroid

def transition(a, b):
    pa, ma, ca = geometry(a)
    pb, mb, cb = geometry(b)
    union = ma | mb
    changed = sum(1 for i in union if pa[i] != pb[i])
    return {'alpha_iou': len(ma & mb) / len(union) if union else 1.0,
            'visible_rgba_changed_fraction': changed / len(union) if union else 0.0,
            'centroid_delta_pixels': math.dist(ca, cb) if ca and cb else None,
            'opaque_area_ratio': len(mb) / len(ma) if ma else None}

def review(path, output, selected=None, max_cells=32):
    result = validate(path)
    if result['errors']:
        raise ValueError(json.dumps(result['errors'][:5]))
    path, output = Path(path).resolve(), Path(output).resolve()
    if output == path.parent or path.parent.is_relative_to(output):
        raise ValueError('Use a separate review output directory')
    output.mkdir(parents=True, exist_ok=True)
    data = json.loads(path.read_text())
    reviewed = []
    for clip in data['clips']:
        key = clip['actor'] + '/' + clip['name']
        if selected and not any(s in key for s in selected):
            continue
        frames = list(frame_images(path.parent, clip))
        transitions = [{'from': i, 'to': i + 1, **transition(frames[i], frames[i + 1])} for i in range(len(frames) - 1)]
        if clip['loop']:
            transitions.append({'from': len(frames) - 1, 'to': 0, 'loop_seam': True, **transition(frames[-1], frames[0])})
        names = []
        for offset in range(0, len(frames), max_cells):
            chunk = frames[offset:offset + max_cells]
            w, h = clip['frame_size']
            # Integer scale capped for contact sheets; preserve the source pixels.
            scale = max(1, min(4, 192 // max(w, h)))
            cell_w, cell_h = max(w * scale + 16, 176), h * scale + 44
            cols = min(8, len(chunk))
            sheet = Image.new('RGB', (cols * cell_w, math.ceil(len(chunk) / cols) * cell_h), '#101820')
            draw = ImageDraw.Draw(sheet)
            for n, image in enumerate(chunk):
                x, y = n % cols * cell_w, n // cols * cell_h
                for gy in range(0, h * scale, 8):
                    for gx in range(0, w * scale, 8):
                        draw.rectangle((x + 8 + gx, y + gy, x + 8 + min(gx + 7, w * scale - 1), y + min(gy + 7, h * scale - 1)), fill='#253541' if (gx + gy) // 8 % 2 else '#1c2a35')
                sheet.paste(image.resize((w * scale, h * scale), Image.Resampling.NEAREST), (x + 8, y), image.resize((w * scale, h * scale), Image.Resampling.NEAREST))
                pivot = clip.get('ground_pivot_pixels', clip['pivot_pixels'])
                px, py = x + 8 + pivot[0] * scale, y + pivot[1] * scale
                draw.line((px - 4, py, px + 4, py), fill='#e9b565')
                draw.line((px, py - 4, px, py + 4), fill='#e9b565')
                f = clip['frames'][offset + n]
                draw.text((x + 4, y + h * scale + 2), f"#{offset+n} {f['duration_video_frames']} ticks", fill='white')
                draw.text((x + 4, y + h * scale + 16), f"body={f.get('frame_index', '-')} src={f.get('native_frame_index', '-')}", fill='#9bafbf')
            slug = hashlib.sha256(key.encode()).hexdigest()[:12]
            name = f'{slug}-{offset:04d}.png'
            sheet.save(output / name)
            names.append({'path': name, 'sha256': digest(output / name)})
        reviewed.append({'id': key, 'contact_sheets': names, 'transitions': transitions,
                         'review_status': 'pending', 'notes': []})
    report = {'input_fingerprint': result['input_fingerprint'], 'snapshot': result['snapshot'],
              'metrics_are_advisory': True, 'clips': reviewed, 'warnings': result['warnings']}
    (output / 'temporal-review.json').write_text(json.dumps(report, indent=2) + '\n')
    return {'clips': len(reviewed), 'contact_sheets': sum(len(c['contact_sheets']) for c in reviewed),
            'input_fingerprint': result['input_fingerprint'], 'output': str(output)}

def check_review(manifest, receipt):
    report = validate(manifest)
    review_data = json.loads(Path(receipt).read_text())
    if report['errors'] or review_data.get('input_fingerprint') != report['input_fingerprint']:
        raise ValueError('Invalid assets or stale review: fingerprint mismatch')
    if review_data.get('decision') not in ['approved', 'changes_requested'] or not review_data.get('reviewer') or not isinstance(review_data.get('observations'), list) or not review_data['observations']:
        raise ValueError('Review requires decision, reviewer and nonempty observations')
    ids = {c['id'] for c in report['clips']}
    covered = review_data.get('clip_ids')
    if not isinstance(covered, list) or not covered or len(set(covered)) != len(covered) or not set(covered).issubset(ids):
        raise ValueError('Review clip_ids must explicitly name existing clips')
    return {'current': True, 'decision': review_data['decision'], 'reviewed_clip_count': len(covered),
            'total_clip_count': len(ids), 'unreviewed_clip_ids': sorted(ids - set(covered)),
            'input_fingerprint': report['input_fingerprint']}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('validate'); p.add_argument('manifest', type=Path); p.add_argument('--report', type=Path)
    p = sub.add_parser('review'); p.add_argument('manifest', type=Path); p.add_argument('output', type=Path); p.add_argument('--select', action='append')
    p = sub.add_parser('check-review'); p.add_argument('manifest', type=Path); p.add_argument('receipt', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'validate':
            result = validate(args.manifest)
            if args.report:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(json.dumps(result, indent=2) + '\n')
            print(json.dumps({k: result[k] for k in ['accepted', 'clip_count', 'frame_count', 'input_fingerprint', 'errors']}))
            raise SystemExit(0 if result['accepted'] else 1)
        elif args.command == 'review':
            print(json.dumps(review(args.manifest, args.output, args.select)))
        else:
            print(json.dumps(check_review(args.manifest, args.receipt)))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + '\n')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Mechanical exports, visual comparison sheets and hash-based art verification.

Requires Pillow. Never generates images or performs semantic image edits.
"""
import argparse
import hashlib
import json
import math
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + '.pending')
    pending.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    pending.replace(path)


def resolve(root, value):
    return (root / value).resolve()


def output_path(root, value):
    path = resolve(root, value)
    if Path(value).is_absolute() or not path.is_relative_to(root):
        raise ValueError('Output path must be relative to the manifest directory: ' + value)
    return path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def spec_for(manifest):
    spec = manifest['art_spec']
    need(spec['kind'] in ('pixel-sprite', 'raster'), 'Unknown art_spec.kind')
    if spec['kind'] == 'pixel-sprite':
        canvas, fit = spec['canvas'], spec['fit']
        need(len(canvas) == len(fit) == 2, 'Canvas and fit need two dimensions')
        need(all(isinstance(n, int) and n > 0 for n in canvas + fit), 'Invalid dimensions')
        need(all(f <= c for f, c in zip(fit, canvas)), 'Fit exceeds canvas')
        need(spec['anchor'] in ('bottom', 'center'), 'Unknown anchor')
        if spec['anchor'] == 'bottom':
            need(fit[1] <= spec['baseline'] <= canvas[1], 'Invalid baseline')
        threshold = spec.get('alpha_threshold')
        need(threshold is None or isinstance(threshold, int) and 1 <= threshold <= 255,
             'alpha_threshold must be null or 1..255')
        scales = spec['scales']
        need(1 in scales and len(set(scales)) == len(scales), 'Scales must uniquely include 1')
        need(all(isinstance(n, int) and n > 0 for n in scales), 'Scales must be positive integers')
    return spec


def sprite_image(path, spec):
    with Image.open(path) as src:
        src.load()
        need(src.mode == 'RGBA', 'Pixel sprite master must be RGBA')
        im = src.copy()
    alpha = im.getchannel('A')
    need(alpha.getextrema()[0] == 0, 'Sprite master has no actual transparent pixels')
    threshold = spec.get('alpha_threshold')
    if threshold is not None:
        alpha = alpha.point(lambda a: 255 if a >= threshold else 0)
    bounds = alpha.getbbox()
    need(bounds is not None, 'Empty sprite')
    touching = bounds[0] == 0 or bounds[1] == 0 or bounds[2] == im.width or bounds[3] == im.height
    if spec.get('reject_source_boundary_touch', True):
        need(not touching, 'Source silhouette touches canvas edge; inspect and repair framing')
    im.putalpha(alpha)
    im = im.crop(bounds)
    ratio = min(spec['fit'][0] / im.width, spec['fit'][1] / im.height)
    size = (max(1, round(im.width * ratio)), max(1, round(im.height * ratio)))
    im = im.resize(size, Image.Resampling.NEAREST)
    # Downsampling can remove the last opaque row. Anchor actual alpha, not the resized box.
    resized_bounds = im.getchannel('A').getbbox()
    need(resized_bounds is not None, 'Subject vanished at canonical resolution')
    im = im.crop(resized_bounds)
    out = Image.new('RGBA', tuple(spec['canvas']))
    x = (out.width - im.width) // 2
    y = spec['baseline'] - im.height if spec['anchor'] == 'bottom' else (out.height - im.height) // 2
    out.paste(im, (x, y))  # No mask: preserve alpha without applying it twice.
    return out


def file_inputs(subject):
    yield subject['master']
    if subject.get('prompt'):
        yield subject['prompt']
    yield from subject.get('references', [])
    for edit in subject.get('edits', []):
        if edit.get('prompt'):
            yield edit['prompt']


def export(manifest, root, spec):
    ids = [s['id'] for s in manifest['subjects']]
    need(len(set(ids)) == len(ids), 'Duplicate representative IDs')
    source_paths = {resolve(root, item['path']) for s in manifest['subjects'] for item in file_inputs(s)}
    for subject in manifest['subjects']:
        master = resolve(root, subject['master']['path'])
        need(sha(master) == subject['master']['sha256'], 'Master hash mismatch: ' + subject['id'])
        slug = re.sub(r'[^a-zA-Z0-9_-]+', '-', subject['id']).strip('-')[:64] or 'asset'
        stem = slug + '--' + hashlib.sha256(subject['id'].encode()).hexdigest()[:12]
        if spec['kind'] == 'pixel-sprite':
            base = sprite_image(master, spec)
            variants = [(n, base.resize((base.width * n, base.height * n), Image.Resampling.NEAREST))
                        for n in spec['scales']]
        else:
            with Image.open(master) as im:
                im.load()
                variants = [(1, im.copy())]
        exports = []
        for scale, im in variants:
            suffix = '.png' if spec['kind'] == 'pixel-sprite' else master.suffix.lower()
            rel = f'exports/{scale}x/{stem}{suffix}'
            dst = output_path(root, rel)
            need(dst not in source_paths, 'Export would overwrite an input')
            dst.parent.mkdir(parents=True, exist_ok=True)
            if spec['kind'] == 'pixel-sprite':
                im.save(dst, optimize=True)
            else:
                shutil.copy2(master, dst)  # Preserve native colours, alpha and encoded bytes.
            exports.append({'path': rel, 'sha256': sha(dst), 'size': list(im.size), 'scale': scale})
        subject['exports'] = exports
        review = subject.get('visual_review')
        if review and review.get('export_sha256') != next(e['sha256'] for e in exports if e['scale'] == 1):
            subject.setdefault('review_history', []).append(review)
            subject['visual_review'] = {'status': 'pending', 'reason': 'Export hash changed'}
    manifest['complete'] = False


def verify(manifest, root, spec):
    errors = []
    targets = manifest.get('target_ids', [])
    ids = [s['id'] for s in manifest['subjects']]
    coverage = [i for s in manifest['subjects'] for i in s.get('covers', [s['id']])]
    if not targets or len(set(targets)) != len(targets):
        errors.append('target_ids must be a nonempty unique frozen inventory')
    if len(set(ids)) != len(ids):
        errors.append('Duplicate representative IDs')
    if set(coverage) != set(targets) or any(n != 1 for n in Counter(coverage).values()):
        errors.append('Requested coverage is missing, extra or duplicated')
    all_outputs = [e['path'] for s in manifest['subjects'] for e in s.get('exports', [])]
    if len(set(all_outputs)) != len(all_outputs):
        errors.append('Two exports share an output path')
    verified_files = 0
    for subject in manifest['subjects']:
        try:
            for item in file_inputs(subject):
                path = resolve(root, item['path'])
                need(path.is_file() and sha(path) == item['sha256'], 'Input/provenance hash mismatch: ' + str(path))
            for reference in subject.get('references', []):
                need(bool(reference.get('role')), 'Reference image needs an explicit role')
                with Image.open(resolve(root, reference['path'])) as image:
                    image.verify()
            need(bool(subject.get('covers', [subject['id']])), 'Representative covers no requested entries')
            need(subject.get('prompt'), 'Actual generation prompt/receipt is missing')
            exports = subject.get('exports', [])
            scales = [e['scale'] for e in exports]
            wanted = spec['scales'] if spec['kind'] == 'pixel-sprite' else [1]
            need(sorted(scales) == sorted(wanted), 'Missing/duplicate export scales')
            canonical = next(e for e in exports if e['scale'] == 1)
            review = subject.get('visual_review', {})
            need(review.get('status') == 'accepted' and review.get('export_sha256') == canonical['sha256'],
                 'Current canonical export lacks accepted visual review')
            need(bool(review.get('reviewer')) and bool(review.get('observations')), 'Review needs reviewer and observations')
            if spec['kind'] == 'pixel-sprite':
                expected = sprite_image(resolve(root, subject['master']['path']), spec)
            else:
                with Image.open(resolve(root, subject['master']['path'])) as src:
                    src.load()
                    expected = src.copy()
            for e in exports:
                path = output_path(root, e['path'])
                need(sha(path) == e['sha256'], 'Export hash mismatch')
                if spec['kind'] == 'raster':
                    need(sha(path) == subject['master']['sha256'], 'Native raster bytes differ from master')
                with Image.open(path) as im:
                    im.load()
                    need(list(im.size) == e['size'], 'Recorded dimensions mismatch')
                    wanted_image = expected.resize((expected.width * e['scale'], expected.height * e['scale']),
                                                   Image.Resampling.NEAREST)
                    need(im.mode == wanted_image.mode and im.size == wanted_image.size and
                         im.tobytes() == wanted_image.tobytes(), 'Export differs from current master/spec')
                    if spec.get('transparent', spec['kind'] == 'pixel-sprite'):
                        need(im.mode == 'RGBA' and im.getchannel('A').getextrema()[0] == 0 and
                             im.getchannel('A').getextrema()[1] > 0, 'Promised transparency missing/empty')
                verified_files += 1
        except (OSError, ValueError, KeyError, StopIteration) as exc:
            errors.append(subject['id'] + ': ' + str(exc))
    return {'passed': not errors, 'requested_entries': len(targets), 'representatives': len(ids),
            'image_files_verified': verified_files, 'errors': errors,
            'scope': 'Coverage, file hashes, current visual-review records, export pixels and input paths. '
                     'Does not itself assess artistic fidelity, animation, tiling or engine behavior.'}


def contact_sheets(manifest, root, destination, page_size, pending_only=False):
    destination = output_path(root, destination)
    destination.mkdir(parents=True, exist_ok=True)
    records = manifest['subjects']
    if pending_only:
        records = [s for s in records if not (
            s.get('visual_review', {}).get('status') == 'accepted' and
            s['visual_review'].get('export_sha256') == next(e['sha256'] for e in s['exports'] if e['scale'] == 1) and
            sha(resolve(root, next(e['path'] for e in s['exports'] if e['scale'] == 1))) == s['visual_review']['export_sha256'])]
    pages = []
    for start in range(0, len(records), page_size):
        subset = records[start:start + page_size]
        columns = min(4, len(subset))
        page = Image.new('RGB', (columns * 320, math.ceil(len(subset) / columns) * 500), '#283544')
        draw = ImageDraw.Draw(page)
        for index, subject in enumerate(subset):
            x, y = index % columns * 320, index // columns * 500
            draw.text((x + 8, y + 8), subject.get('name', subject['id'])[:45], fill='white')
            canonical = next(e for e in subject['exports'] if e['scale'] == 1)
            images = [(resolve(root, canonical['path']), (304, 280), y + 40)]
            reference = next((r for r in subject.get('references', []) if r['role'] in ('identity', 'geometry')),
                             next(iter(subject.get('references', [])), None))
            if reference:
                images.append((resolve(root, reference['path']), (304, 160), y + 332))
            for path, box, top in images:
                with Image.open(path) as src:
                    im = src.convert('RGBA')
                    im.thumbnail(box, Image.Resampling.NEAREST if top == y + 40 and
                                 manifest['art_spec']['kind'] == 'pixel-sprite' else Image.Resampling.LANCZOS)
                    page.paste(im, (x + (320 - im.width) // 2, top), im)
        path = destination / f'comparison-{start // page_size:03d}.png'
        page.save(path)
        pages.append({'path': str(path.relative_to(root)), 'ids': [s['id'] for s in subset]})
    save(destination / 'pages.json', pages)
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['export', 'verify', 'contact-sheet'])
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--complete', action='store_true', help='Verify and set completion only on success')
    parser.add_argument('--out', default='review/comparisons', help='Relative comparison directory')
    parser.add_argument('--page-size', type=int, default=8)
    parser.add_argument('--pending-only', action='store_true', help='Comparison sheets for exports needing review')
    args = parser.parse_args()
    need(not args.complete or args.command == 'verify', '--complete applies only to verify')
    need(1 <= args.page_size <= 16, 'page-size must be 1..16')
    path = args.manifest.resolve()
    root = path.parent
    manifest = json.loads(path.read_text())
    if args.complete:
        manifest['complete'] = False
        save(path, manifest)
    spec = spec_for(manifest)
    if args.command == 'export':
        manifest['complete'] = False
        save(path, manifest)
        export(manifest, root, spec)
        save(path, manifest)
        print(json.dumps({'exported_representatives': len(manifest['subjects']), 'complete': False}))
    elif args.command == 'contact-sheet':
        print(json.dumps(contact_sheets(manifest, root, args.out, args.page_size, args.pending_only), indent=2))
    else:
        if args.complete:
            manifest['complete'] = False
            save(path, manifest)
        report = verify(manifest, root, spec)
        save(root / 'verification.json', report)
        if args.complete and report['passed']:
            manifest['complete'] = True
            save(path, manifest)
        print(json.dumps(report, indent=2))
        return 0 if report['passed'] else 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

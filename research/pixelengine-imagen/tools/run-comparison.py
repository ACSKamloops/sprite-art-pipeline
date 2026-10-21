#!/usr/bin/env python3
"""Replay the retained ImageGen comparison; never calls a provider.

Uses existing palette/construction/timing tools and the explicitly supplied
genuine offline artifact. Generated art and third-party code stay external.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw


REPO = Path(__file__).resolve().parents[3]
TOOLKIT = REPO / 'skills/sprite-construction-editing/assets/toolkit'
sys.path.insert(0, str(REPO / 'workbench/scripts'))
sys.path.insert(0, str(TOOLKIT))
from prepare_palette_predictions import predict, remap_rgba
from sprite_lab import canonical_json
sys.path.insert(0, str(REPO / 'workbench'))
from sprite_workbench.calibrated_palette import reference_palette


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


constructor = module('comparison_constructor', TOOLKIT / 'scripts/sprite_construct.py')
delivery = module('comparison_delivery', REPO / 'skills/sprite-animation-pipeline/scripts/project_delivery.py')
apng = module('comparison_apng', REPO / 'skills/sprite-animation-pipeline/scripts/exact_apng.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def image_stats(image):
    array = np.array(image.convert('RGBA'))
    alpha = array[..., 3]
    return {'canvas': list(image.size), 'rgba_sha256': hashlib.sha256(array.tobytes()).hexdigest(),
            'bounds_alpha_positive': image.getchannel('A').getbbox(),
            'bounds_alpha_at_least_8': image.getchannel('A').point(lambda x: 255 if x >= 8 else 0).getbbox(),
            'partial_alpha_pixels': int(((alpha > 0) & (alpha < 255)).sum()),
            'visible_rgb_colors': len(np.unique(array[alpha > 0, :3], axis=0))}


def stage(image, scale, center_x, floor_y):
    # One specified inverse affine, never fitted separately for each frame.
    return image.transform((80, 80), Image.Transform.AFFINE,
                           (1 / scale, 0, center_x - 40 / scale,
                            0, 1 / scale, floor_y - 72 / scale),
                           resample=Image.Resampling.NEAREST)


def export_clip(out, name, images, provenance):
    source = out / 'projects' / name
    source.mkdir(parents=True)
    records = []
    for i, image in enumerate(images):
        image.save(source / f'{i:02d}.png')
        records.append({'id': f'pose-{i:02d}', 'duration_ticks': 1, 'landmarks': {},
                        'cels': {'body': {'image': f'{i:02d}.png', 'at': [0, 0]}}})
    spec = {'schema': 'sprite-construction-spec/v1',
            'canvas': {'width': 80, 'height': 80, 'render_pivot': [40, 72], 'ground_pivot': [40, 72]},
            'layers': [{'id': 'body', 'name': 'Generated body, not an anatomical rig', 'locked': False}],
            'frames': records,
            'animations': [{'id': 'walk', 'frames': [r['id'] for r in records], 'fps': 8, 'loop': True, 'events': []}],
            'provenance': provenance}
    write(source / 'spec.json', spec)
    project = constructor.construct(source / 'spec.json')
    (source / 'project.json').write_text(canonical_json(project) + '\n')
    receipt = delivery.export(source / 'project.json', out / 'clips' / name,
                              'walk', TOOLKIT, columns=8, actor=name)
    apng.convert(out / 'clips' / name / 'manifest.json', out / 'clips' / name / 'apng')
    return {'id': name, 'manifest': f'clips/{name}/manifest.json',
            'project': f'projects/{name}/project.json',
            'atlas': f'clips/{name}/atlas.png', 'apng': f'clips/{name}/apng/animation.apng.png',
            'stats': [image_stats(i) for i in images], 'export_receipt': receipt}


def run(args):
    root, out = args.artifacts.resolve(), args.output_dir.absolute()
    if out.exists() or out.is_symlink():
        raise ValueError('Fresh output directory required')
    names = ['raw/imagegen-north-original.png', args.walk,
             'references/native-original.png', 'references/north-original.png',
             'references/walk15-original.webp', 'references/walk11-original.webp']
    inputs = {name: sha(root / name) for name in names}
    north = Image.open(root / names[0]).convert('RGBA')
    sheet = Image.open(root / names[1]).convert('RGBA')
    if sheet.width != sheet.height or sheet.width % 3:
        raise ValueError('This experiment requires a square return divisible into3 exact cells')
    edge = sheet.width // 3
    out.mkdir(parents=True)
    for folder in ['inputs', 'registered', 'palette', 'wasm', 'projects', 'clips', 'stills']:
        (out / folder).mkdir()
    raw_cells = [sheet.crop(((i % 3) * edge, (i // 3) * edge, (i % 3 + 1) * edge, (i // 3 + 1) * edge)) for i in range(9)]
    if raw_cells[-1].getchannel('A').point(lambda x: 255 if x >= 8 else 0).getbbox() is not None:
        raise ValueError('Reserved ninth cell has visible content at alpha >=8')
    raw_cells = raw_cells[:8]
    # Threshold8 measures bounds only; it never changes output alpha/RGB.
    boxes = [i.getchannel('A').point(lambda x: 255 if x >= 8 else 0).getbbox() for i in raw_cells]
    scale = 64 / max(b[3] - b[1] for b in boxes)
    floor = max(b[3] for b in boxes)
    registered = [stage(i, scale, edge / 2, floor) for i in raw_cells]
    north_box = north.getchannel('A').point(lambda x: 255 if x >= 8 else 0).getbbox()
    north_scale = 64 / (north_box[3] - north_box[1])
    north_registered = stage(north, north_scale, (north_box[0] + north_box[2]) / 2, north_box[3])
    for i, (raw, native) in enumerate(zip(raw_cells, registered)):
        raw.save(out / 'inputs' / f'{i:02d}.png')
        native.save(out / 'registered' / f'{i:02d}.png')
    north_registered.save(out / 'registered/north.png')
    write(out / 'timing.json', {'holds': [[1, 8]] * 8, 'duration': [1, 1], 'loop': True,
                                'basis': 'Authored ImageGen test clock; baseline WebP holds independently decoded below'})
    if args.palette_mode == 'fit24':
        palette, palette_receipt = predict([np.array(i) for i in registered] + [np.array(north_registered)], 24, 'alpha-weight')
    else:
        source = np.array(Image.open(root / 'references/native-original.png').convert('RGBA'))
        palette = reference_palette(source)
        palette_receipt = {'policy': 'Existing reference_palette: fixed opaque visible RGBA in first-appearance order',
                           'source_sha256': sha(root / 'references/native-original.png'), 'fitted': False}
    Image.fromarray(palette[None]).save(out / 'palette/palette.png')
    write(out / 'palette/receipt.json', palette_receipt | {'rgba': palette.tolist(), 'palette_png_sha256': sha(out / 'palette/palette.png')})
    colors = json.dumps(['#' + ''.join(f'{int(c):02x}' for c in p[:3]) for p in palette])
    offline = REPO / 'research/pixelengine-imagen/tools/offline-pixelengine.cjs'
    def wasm(command, sources, dest):
        if args.wasm_alpha_floor:
            prepared = []
            alpha_records = []
            alpha_dir = out / 'wasm' / (dest.name + '-alpha-inputs')
            alpha_dir.mkdir()
            for i, source in enumerate(sources):
                array = np.array(Image.open(source).convert('RGBA'))
                mask = array[..., 3] < args.wasm_alpha_floor
                alpha_records.append({'source': str(source), 'sha256': sha(source),
                                      'positive_alpha_pixels_removed': int(((array[..., 3] > 0) & mask).sum()),
                                      'preserved_alpha_at_or_above': args.wasm_alpha_floor})
                array[mask] = 0
                target = alpha_dir / f'{i:02d}.png'
                Image.fromarray(array).save(target)
                alpha_records[-1]['output_sha256'] = sha(target)
                prepared.append(target)
            write(alpha_dir / 'receipt.json', {'policy': 'Explicit low-alpha noise experiment before genuine WASM only; no threshold128/opacity flattening',
                                              'frames': alpha_records})
            sources = prepared
        cmd = ['node', str(offline), command, '--wrapper', str(args.wrapper.resolve()), '--wasm', str(args.wasm.resolve())]
        for source in sources:
            cmd += ['--input', str(source)]
        cmd += ['--palette', colors, '--output-dir', str(dest)]
        if command == 'process-frames':
            cmd += ['--timing-sidecar', str(out / 'timing.json')]
        result = subprocess.run(cmd, capture_output=True, text=True)
        write(dest.parent / (dest.name + '-invocation.json'), {'argv': cmd, 'returncode': result.returncode,
                                                             'stdout': result.stdout, 'stderr': result.stderr})
        result.check_returncode()
    wasm('process-frames', [out / 'registered' / f'{i:02d}.png' for i in range(8)], out / 'wasm/registered')
    wasm('process-frames', [out / 'inputs' / f'{i:02d}.png' for i in range(8)], out / 'wasm/raw')
    wasm('process-image', [out / 'registered/north.png'], out / 'wasm/north')
    clips = []
    for label in ['walk15', 'walk11']:
        images, durations = [], []
        with Image.open(root / 'references' / (label + '-original.webp')) as animation:
            for i in range(animation.n_frames):
                animation.seek(i)
                images.append(animation.convert('RGBA'))
                durations.append(animation.info.get('duration'))
        if len(images) != 8 or durations != [125] * 8 or any(i.size != (80, 80) for i in images):
            raise ValueError('Retained baseline changed; inspect timing and stage')
        clips.append(export_clip(out, label, images, {'source_png_conversion_only': True, 'decoded_webp_milliseconds': durations}))
    clips.append(export_clip(out, 'imagegen-nearest', registered, {'processing': 'One whole-clip inverse affine, nearest; original alpha retained'}))
    mapped = [Image.fromarray(remap_rgba(np.array(i), palette)) for i in registered]
    clips.append(export_clip(out, 'imagegen-shared-palette', mapped, {'processing': 'Existing authored shared palette hypothesis + fixed mapper; original alpha retained'}))
    for label in ['registered', 'raw']:
        processed = [Image.open(out / 'wasm' / label / f'frame-{i:06d}.png').convert('RGBA') for i in range(8)]
        sizes = {i.size for i in processed}
        if len(sizes) != 1:
            raise ValueError('Genuine processor returned mixed dimensions')
        w, h = processed[0].size
        # Preserve the actual inferred grid and disclose subsequent transport.
        if label == 'raw':
            if w != h:
                raise ValueError('Raw-cell affine comparison requires square processed grid')
            stages = [stage(image, scale * edge / w, w / 2, floor * w / edge) for image in processed]
            clips.append(export_clip(out, 'imagegen-pe-first', stages,
                                     {'processing': 'Actual pinned shared-frame WASM at full resolution, then one whole-clip affine',
                                      'actual_grid': [w, h], 'uniform_scale': scale * edge / w,
                                      'source_center_x': w / 2, 'source_floor_y': floor * w / edge,
                                      'limitation': 'Affine grid transport, not recovered exact nonuniform source cuts',
                                      'adapter_receipt_sha256': sha(out / 'wasm' / label / 'receipt.json')}))
            continue
        if w > 80 or h > 80:
            write(out / f'{label}-not-staged.json', {'reason': 'Actual grid exceeds80; retained originals for diagnosis', 'size': [w, h]})
            continue
        offset = [(80 - w) // 2, (80 - h) // 2]
        stages = []
        for image in processed:
            canvas = Image.new('RGBA', (80, 80))
            canvas.paste(image, offset)
            stages.append(canvas)
        clips.append(export_clip(out, 'imagegen-pe-' + label, stages,
                                 {'processing': 'Actual pinned shared-frame WASM, then integer pad only',
                                  'actual_grid': [w, h], 'uniform_pad': offset,
                                  'adapter_receipt_sha256': sha(out / 'wasm' / label / 'receipt.json')}))
    stills = {'source': Image.open(root / 'references/native-original.png').convert('RGBA'),
              'north-pixelengine': Image.open(root / 'references/north-original.png').convert('RGBA'),
              'north-imagegen-nearest': north_registered,
              'north-imagegen-palette': Image.fromarray(remap_rgba(np.array(north_registered), palette)),
              'north-imagegen-pe': Image.open(out / 'wasm/north/image.png').convert('RGBA')}
    for name, image in stills.items():
        image.save(out / 'stills' / (name + '.png'))
    # Chronology retains fixed stage; headings are labels, no quality grades.
    contact = Image.new('RGB', (8 * 160, len(clips) * 190), (125, 125, 125))
    draw = ImageDraw.Draw(contact)
    for row, clip in enumerate(clips):
        draw.text((4, row * 190 + 3), clip['id'], fill='white')
        for i in range(8):
            image = Image.open(out / 'clips' / clip['id'] / 'frames' / f'{i:04d}.png').convert('RGBA').resize((160, 160), Image.Resampling.NEAREST)
            contact.paste(image, (i * 160, row * 190 + 22), image)
    contact.save(out / 'contact.png')
    result = {'schema': 'pixelengine-imagegen-comparison/v1', 'input_sha256': inputs,
              'runner_sha256': sha(__file__), 'canvas': [80, 80], 'holds': [[1, 8]] * 8,
              'wasm_alpha_floor': args.wasm_alpha_floor,
              'registration': {'sheet_grid': [3, 3], 'cell': [edge, edge], 'selected_cells': list(range(8)),
                               'bounds_measurement_alpha_threshold_only': 8, 'walk_boxes': boxes,
                               'walk_uniform_scale': scale, 'walk_source_center_x': edge / 2, 'walk_source_floor_y': floor,
                               'north_uniform_scale': north_scale, 'north_source_box': north_box,
                               'alpha_policy': 'No threshold or despill. Affine stage may crop alpha1 background noise; raw retained.',
                               'per_frame_fitting': False},
              'clips': clips, 'stills': {name: image_stats(i) for name, i in stills.items()},
              'inputs_unchanged': all(sha(root / n) == h for n, h in inputs.items()),
              'art_approval': 'unreviewed',
              'scope': 'Retained north art and one selected walk from three recorded ImageGen calls in the combined experiment. This runner makes no provider calls. One hero and walk view; hosted baselines have different controls and no matched seed; no universal provider ranking or hosted/local equality.'}
    write(out / 'RESULTS.json', result)
    return {'output': str(out), 'clips': [c['id'] for c in clips], 'sources_unchanged': result['inputs_unchanged']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--wrapper', type=Path, required=True)
    parser.add_argument('--wasm', type=Path, required=True)
    parser.add_argument('--palette-mode', choices=['fit24', 'reference'], required=True)
    parser.add_argument('--walk', default='raw/imagegen-walk-original.png', help='Relative retained sheet path in artifacts')
    parser.add_argument('--wasm-alpha-floor', type=int, default=0, help='Explicit removal of alpha below this before WASM only, 0..16')
    args = parser.parse_args()
    if not 0 <= args.wasm_alpha_floor <= 16:
        parser.error('--wasm-alpha-floor must be0..16')
    print(json.dumps(run(args)))

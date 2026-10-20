"""Export one editable project animation to exact-video and Godot input schemas.

Preserves declared animation order, repeated frame bindings, canvas, pivots,
positive holds and source pixels. Creates a fresh resource-test project, not
a gameplay controller or a new visual approval.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
from fractions import Fraction
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def export(project_path, output, animation_id=None, toolkit=None, columns=8, actor='actor'):
    from PIL import Image

    here = Path(__file__).resolve()
    toolkit = Path(toolkit).resolve() if toolkit else here.parents[2] / 'sprite-construction-editing/assets/toolkit'
    if not (toolkit / 'sprite_lab/__init__.py').is_file():
        raise ValueError('Companion sprite-construction-editing toolkit missing; supply --toolkit')
    sys.path.insert(0, str(toolkit))
    from sprite_lab import load_project, project_hash
    from sprite_lab.core import render_frames
    from sprite_lab.export import png_bytes

    source = Path(project_path).resolve()
    out = Path(output).resolve()
    if out.exists():
        raise ValueError('Refuse overwrite output directory')
    if type(columns) is not int or columns < 1:
        raise ValueError('columns must be a positive integer')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', actor):
        raise ValueError('actor must be a filename-safe identifier: letters, digits, underscore or hyphen')
    raw = source.read_bytes()
    project = load_project(raw.decode('utf-8'))
    animations = project['animations']
    if animation_id is None:
        if len(animations) != 1:
            raise ValueError('Choose --animation when the project has zero or multiple animations')
        animation = animations[0]
    else:
        animation = next((a for a in animations if a['id'] == animation_id), None)
        if animation is None:
            raise ValueError('Unknown animation: ' + animation_id)
    width, height = project['canvas']['width'], project['canvas']['height']
    rate = Fraction(str(animation['fps']))
    by_id = {f['id']: f for f in project['frames']}
    ordered = animation['frames']
    images = render_frames(project, ordered)
    cols = min(columns, len(ordered))
    atlas = Image.new('RGBA', (cols * width, ((len(ordered) + cols - 1) // cols) * height))
    out.mkdir(parents=True)
    (out / 'frames').mkdir()
    frames, engine_frames = [], []
    total = Fraction()
    for index, (frame_id, image) in enumerate(zip(ordered, images)):
        frame = by_id[frame_id]
        hold = Fraction(frame['duration_ticks']) / rate
        total += hold
        filename = f'frames/{index:04d}.png'
        (out / filename).write_bytes(png_bytes(image))
        frames.append({'index': index, 'source_frame_id': frame_id, 'file': filename,
                       'sha256': digest(out / filename),
                       'rgba_sha256': hashlib.sha256(image.tobytes()).hexdigest(),
                       'hold': [hold.numerator, hold.denominator]})
        atlas.paste(image, ((index % cols) * width, (index // cols) * height))
        engine_frames.append({'atlas_index': index, 'duration_video_frames': frame['duration_ticks']})
    (out / 'atlas.png').write_bytes(png_bytes(atlas))
    (out / 'project.json').write_bytes(raw)
    manifest = {'id': animation['id'], 'canvas': [width, height],
                'pivot': project['canvas']['render_pivot'],
                'ground_pivot': project['canvas']['ground_pivot'],
                'loop': animation['loop'], 'duration': [total.numerator, total.denominator],
                'frames': frames,
                'source': {'project_file_sha256': hashlib.sha256(raw).hexdigest(),
                           'project_canonical_sha256': project_hash(project),
                           'tick_rate_rational': [rate.numerator, rate.denominator],
                           'clock_basis': 'Exact decimal value stored in editable animation.fps; not inferred native timing'},
                'boundary': 'Mechanical single-animation export. No inferred art approval, gameplay or native timing.'}
    write_json(out / 'manifest.json', manifest)
    clips = {'video_fps': animation['fps'], 'clips': [
        {'actor': actor, 'name': animation['id'], 'sheet': 'atlas.png',
         'sheet_columns': cols, 'frame_size': [width, height],
         'loop': animation['loop'], 'frames': engine_frames}]}
    write_json(out / 'clips.json', clips)
    builder = here.parents[1] / 'assets/build_godot.gd'
    shutil.copy2(builder, out / 'build_godot.gd')
    (out / 'project.godot').write_text('config_version=5\n[application]\nconfig/name="Sprite resource verification"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
    receipt = {'schema': 'sprite-project-delivery/v1', 'source_project': str(source),
               'source_file_sha256': hashlib.sha256(raw).hexdigest(),
               'source_project_canonical_sha256': project_hash(project),
               'selected_animation': animation['id'], 'ordered_frame_ids': ordered,
               'frame_count': len(frames), 'canvas': [width, height],
               'duration': manifest['duration'], 'atlas_columns': cols, 'actor': actor,
               'manifest_sha256': digest(out / 'manifest.json'),
               'clips_sha256': digest(out / 'clips.json'),
               'source_unchanged': digest(source) == hashlib.sha256(raw).hexdigest(),
               'boundary': 'PNG and schema conversion only. Godot resources require an import and build run; live playback/render/contact tests remain separate.'}
    if not receipt['source_unchanged']:
        raise ValueError('Source changed during export')
    write_json(out / 'DELIVERY-RECEIPT.json', receipt)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--animation')
    parser.add_argument('--toolkit', type=Path)
    parser.add_argument('--columns', type=int, default=8)
    parser.add_argument('--actor', default='actor')
    args = parser.parse_args()
    result = export(args.project, args.output, args.animation, args.toolkit, args.columns, args.actor)
    print(json.dumps({k: result[k] for k in ['selected_animation', 'frame_count', 'canvas', 'duration', 'source_unchanged']}))

#!/usr/bin/env python3
"""Replay the latest ten-key recovery from retained ImageGen paint and maps."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STUDY = HERE / 'recovery-study'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(output):
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise ValueError('Fresh output required')
    for name, expected in json.loads((STUDY / 'INPUTS.sha256.json').read_text()).items():
        path = (STUDY / name).resolve()
        if not path.is_relative_to(STUDY) or sha(path) != expected:
            raise ValueError('Study input changed: ' + name)
    raw = np.array(Image.open(STUDY / 'raw.png').convert('RGBA'))
    recipe = json.loads((STUDY / 'recipe.json').read_text())
    if list(raw.shape[:2][::-1]) != recipe['raw_dimensions']:
        raise ValueError('Raw dimensions differ')
    paint = []
    for key in range(6):
        xy = np.load(STUDY / f'maps/paint-{key}-raw-xy.npy', allow_pickle=False)
        owner = np.array(Image.open(STUDY / f'maps/paint-{key}-owner-native.png')) > 0
        if xy.shape != (80, 80, 2) or owner.shape != (80, 80):
            raise ValueError('Wrong frozen map shape')
        addressed = xy[owner]
        if (addressed < 0).any() or (addressed[:, 0] >= raw.shape[1]).any() or (addressed[:, 1] >= raw.shape[0]).any():
            raise ValueError('Owner samples outside raw paint')
        image = np.zeros((80, 80, 4), np.uint8)
        image[owner] = raw[addressed[:, 1], addressed[:, 0]]
        if (image[owner, 3] < recipe['alpha_threshold']).any():
            raise ValueError('Frozen owner violates declared alpha threshold')
        image[owner, 3] = 255
        paint.append(image)
    downed = np.array(Image.open(STUDY / 'bookends/downed.png').convert('RGBA'))
    idle = np.array(Image.open(STUDY / 'bookends/idle.png').convert('RGBA'))
    base = [downed] + paint + [idle]
    transfer_map = np.load(STUDY / 'maps/transfer-xy.npy', allow_pickle=False)
    owned = (transfer_map >= 0).all(axis=-1)
    transfer = np.zeros_like(base[4])
    transfer[owned] = base[4][transfer_map[owned, 1], transfer_map[owned, 0]]
    fixture = ROOT / 'skills/imagegen-sprite-animation/assets/source-settle-fixture'
    source = np.array(Image.open(fixture / 'source.png').convert('RGBA'))
    if not np.array_equal(source, base[6]):
        raise ValueError('Settling fixture donor differs from imported pose')
    with np.load(fixture / 'source-map.npz', allow_pickle=False) as maps:
        xy = maps['source_xy']
    settle = base[6][xy[:, :, 1], xy[:, :, 0]]
    if not np.array_equal(settle[53:], base[6][53:]):
        raise ValueError('Protected lower body changed')
    frames = base[:5] + [transfer, base[5], base[6], settle, base[7]]
    library = json.loads((HERE / 'package/library.json').read_text())
    selected = next(c for c in library['clips'] if c['id'] == library['selected']['get_up_SE'])
    if len(selected['frames']) != len(frames):
        raise ValueError('Selected frame count changed')
    for number, (image, expected, hold) in enumerate(zip(frames, selected['frames'], recipe['holds'])):
        if hashlib.sha256(image.tobytes()).hexdigest() != expected['rgba_sha256'] or hold != expected['hold']:
            raise ValueError('Replay differs at exposure ' + str(number))
    spec = importlib.util.spec_from_file_location('recovery_bank', ROOT / 'research/pixelengine-imagen/tools/build-rpg-bank.py')
    bank = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bank)
    bank.export_action(output, 'get_up', 'SE', [Image.fromarray(a) for a in frames],
                       {'loop': False, 'holds': recipe['holds'], 'events': []},
                       {'operation': 'Retained raw ImageGen import, explicit source ownership and two source-part keys',
                        'recipe_sha256': sha(STUDY / 'recipe.json'), 'new_generation': False}, list(range(10)))
    result = {'frames': 10, 'duration': recipe['duration'], 'all_selected_RGBA_and_holds_exact': True,
              'source_settle_lower_body_exact': True,
              'scope': 'Saved raw-to-editable recovery replay, not new generation, visual approval or engine validation.'}
    (output / 'REPLAY-VERIFIED.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(replay(args.output), indent=2))


if __name__ == '__main__':
    main()

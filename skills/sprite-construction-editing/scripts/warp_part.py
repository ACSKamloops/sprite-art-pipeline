#!/usr/bin/env python3
"""Hash-bound, layer-only inverse-barycentric nearest sprite-part warp."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import numpy as np
from PIL import Image

SCHEMA = 'nearest-part-warp/v1'
EPSILON = 1e-8

class ContractError(ValueError):
    pass

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(condition, message):
    if not condition:
        raise ContractError(message)

def bound_image(value, root, label):
    require(isinstance(value, dict) and set(value) == {'path', 'sha256'}, f'{label}: require path and sha256')
    require(isinstance(value['path'], str) and value['path'], f'{label}: invalid path')
    digest = value['sha256']
    require(isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest), f'{label}: invalid SHA256')
    path = (root / value['path']).resolve()
    require(path.is_file(), f'{label}: not a file: {path}')
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == digest, f'{label}: stale SHA256: {path}')
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        if label == 'donor':
            require(image.mode == 'RGBA', 'donor must be straight RGBA PNG; no implicit color/alpha conversion')
            require(image.format == 'PNG', 'donor must be PNG')
            array = np.array(image, dtype=np.uint8)
        else:
            require(image.mode in ('1', 'L') and image.format == 'PNG', 'owner mask must be binary PNG mode1 or L')
            array = np.array(image.convert('L'), dtype=np.uint8)
            require(bool(np.all((array == 0) | (array == 255))), 'owner mask must contain only0 and255')
        size = image.size
    return path, array, size

def vertices(value, label):
    require(isinstance(value, list) and len(value) >= 3, f'{label}: require at least3 vertices')
    require(all(isinstance(p, list) and len(p) == 2 for p in value), f'{label}: each vertex must be[x,y]')
    require(all(isinstance(v, (int, float)) and not isinstance(v, bool) for p in value for v in p), f'{label}: coordinates must be numeric')
    try:
        array = np.array(value, dtype=np.float64)
    except (ValueError, OverflowError) as error:
        raise ContractError(f'{label}: invalid numeric coordinates') from error
    require(bool(np.isfinite(array).all()), f'{label}: NaN/Infinity refused')
    return array

def validate(spec_path: Path):
    try:
        spec = json.loads(spec_path.read_text())
    except (ValueError, OSError) as error:
        raise ContractError(f'cannot read spec: {error}') from error
    keys = {'schema', 'canvas', 'donor', 'owner_mask', 'source_vertices', 'target_vertices', 'triangles', 'alpha_mode'}
    require(isinstance(spec, dict) and set(spec) == keys, 'spec requires exactly: ' + ', '.join(sorted(keys)))
    require(spec['schema'] == SCHEMA, 'unsupported schema')
    canvas = spec['canvas']
    require(isinstance(canvas, list) and len(canvas) == 2 and all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in canvas), 'canvas must be positive integer[width,height]')
    require(spec['alpha_mode'] in ('copy-owned', 'nonzero-only'), 'alpha_mode must explicitly be copy-owned or nonzero-only')
    donor_path, donor, donor_size = bound_image(spec['donor'], spec_path.parent, 'donor')
    owner_path, owner, owner_size = bound_image(spec['owner_mask'], spec_path.parent, 'owner_mask')
    require(tuple(canvas) == donor_size == owner_size, 'canvas/donor/owner dimensions differ')
    source = vertices(spec['source_vertices'], 'source_vertices')
    target = vertices(spec['target_vertices'], 'target_vertices')
    require(source.shape == target.shape, 'source/target vertex counts differ')
    triangles = spec['triangles']
    require(isinstance(triangles, list) and triangles, 'triangles must be a nonempty list')
    inverses = []
    determinants = []
    for number, tri in enumerate(triangles):
        require(isinstance(tri, list) and len(tri) == 3 and all(isinstance(v, int) and not isinstance(v, bool) and 0 <= v < len(source) for v in tri), f'triangle{number}: invalid indices')
        s, t = source[tri], target[tri]
        source_matrix = np.vstack([s.T, np.ones(3)])
        target_matrix = np.vstack([t.T, np.ones(3)])
        with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
            sd, td = float(np.linalg.det(source_matrix)), float(np.linalg.det(target_matrix))
        require(math.isfinite(sd) and math.isfinite(td), f'triangle{number}: nonfinite determinant')
        require(abs(sd) > EPSILON and abs(td) > EPSILON, f'triangle{number}: degenerate source/target triangle')
        require((sd > 0) == (td > 0), f'triangle{number}: orientation flipped/folded source-to-target triangle')
        try:
            inverse = np.linalg.inv(target_matrix)
        except np.linalg.LinAlgError as error:
            raise ContractError(f'triangle{number}: singular target') from error
        require(bool(np.isfinite(inverse).all()), f'triangle{number}: nonfinite inverse')
        inverses.append(inverse)
        determinants.append({'source': sd, 'target': td})
    return spec, donor_path, owner_path, donor, owner > 0, source, target, inverses, determinants

def raster(donor, owner, source, target, triangles, inverses, alpha_mode):
    height, width = owner.shape
    layer = np.zeros_like(donor)
    present = np.zeros((height, width), dtype=bool)
    source_xy = np.full((height, width, 2), -1, dtype=np.int64)
    triangle_map = np.full((height, width), -1, dtype=np.int64)
    stats = []
    for number, (tri, inverse) in enumerate(zip(triangles, inverses)):
        s, t = source[tri], target[tri]
        # Match the original MM loop, including integer-valued center convention.
        x0, x1 = math.floor(t[:, 0].min()), math.ceil(t[:, 0].max()) + 1
        y0, y1 = math.floor(t[:, 1].min()), math.ceil(t[:, 1].max()) + 1
        left, right = max(0, x0), min(width, x1)
        top, bottom = max(0, y0), min(height, y1)
        clipped_bbox_size = max(0, right-left) * max(0, bottom-top)
        row = {'triangle': number, 'target_bbox_xyxy_exclusive': [x0, y0, x1, y1],
               'target_bbox_grid_positions_clipped_outside_canvas': (x1-x0)*(y1-y0)-clipped_bbox_size,
               'inside_triangle_target_samples': 0, 'source_outside_canvas_samples': 0,
               'source_owner_false_samples': 0, 'source_alpha_zero_samples': 0,
               'alpha_zero_skipped_samples': 0, 'writes': 0, 'overwrites': 0}
        for y in range(top, bottom):
            for x in range(left, right):
                bary = inverse @ np.array([x, y, 1.])
                if bary.min() < -EPSILON:
                    continue
                row['inside_triangle_target_samples'] += 1
                position = bary @ s
                require(bool(np.isfinite(position).all()), 'nonfinite mapped source position')
                sx, sy = math.floor(float(position[0])+0.5), math.floor(float(position[1])+0.5)
                if not (0 <= sx < width and 0 <= sy < height):
                    row['source_outside_canvas_samples'] += 1
                    continue
                if not owner[sy, sx]:
                    row['source_owner_false_samples'] += 1
                    continue
                if donor[sy, sx, 3] == 0:
                    row['source_alpha_zero_samples'] += 1
                    if alpha_mode == 'nonzero-only':
                        row['alpha_zero_skipped_samples'] += 1
                        continue
                row['overwrites'] += int(present[y, x])
                layer[y, x] = donor[sy, sx]
                present[y, x] = True
                source_xy[y, x] = [sx, sy]
                triangle_map[y, x] = number
                row['writes'] += 1
        stats.append(row)
    return layer, present, source_xy, triangle_map, stats

def run(spec_path, output):
    spec_path = Path(spec_path).resolve()
    output = Path(output).absolute()
    require(not output.exists() and not output.is_symlink(), f'output already exists: {output}')
    spec_digest = sha256(spec_path)
    spec, dp, op, donor, owner, src, dst, inverses, determinants = validate(spec_path)
    layer, present, source_xy, tri_map, stats = raster(donor, owner, src, dst, spec['triangles'], inverses, spec['alpha_mode'])
    require(sha256(spec_path) == spec_digest, 'spec changed during rasterization')
    require(sha256(dp) == spec['donor']['sha256'], 'donor changed during rasterization')
    require(sha256(op) == spec['owner_mask']['sha256'], 'owner mask changed during rasterization')
    # Reject invalid requests before creating any output. mkdir is exclusive.
    output.mkdir(parents=False, exist_ok=False)
    Image.fromarray(layer).save(output/'layer.png')
    Image.fromarray(present.astype(np.uint8)*255).save(output/'owner-mask.png')
    np.save(output/'source-xy.npy', source_xy, allow_pickle=False)
    np.save(output/'triangle-index.npy', tri_map, allow_pickle=False)
    (output/'request.json').write_text(json.dumps(spec, indent=2, allow_nan=False)+'\n')
    receipt = {
        'schema': 'nearest-part-warp-receipt/v1', 'canvas': spec['canvas'],
        'spec_path': str(spec_path), 'spec_sha256': spec_digest,
        'donor': {'path': str(dp), 'sha256': sha256(dp), 'raw_RGBA_sha256': hashlib.sha256(donor.tobytes()).hexdigest()},
        'owner_mask': {'path': str(op), 'sha256': sha256(op), 'binary': True},
        'alpha_mode': spec['alpha_mode'], 'RGBA_mode': 'straight RGBA; exact byte copy, no interpolation/premultiplication',
        'color_metadata': 'No color management or metadata copying; raw RGBA samples are authoritative',
        'coordinates': 'integer x/y are pixel centers; inverse barycentric; nearest=floor(source+0.5)',
        'inside_epsilon': EPSILON, 'overlap': 'last valid owned sample wins, in triangles list order; invalid/unowned samples never erase earlier writes',
        'triangle_signed_determinants': determinants, 'triangle_statistics': stats,
        'owned_output_pixels': int(present.sum()), 'owned_output_alpha_zero_pixels': int((present & (layer[:, :, 3] == 0)).sum()),
        'owned_output_partial_alpha_pixels': int((present & (layer[:, :, 3] > 0) & (layer[:, :, 3] < 255)).sum()),
        'source_xy_layout': 'int64[height,width,2], channels x,y; -1,-1 means no owned sample',
        'triangle_map_layout': 'int64[height,width], -1 means no owned sample',
        'layer_only': True, 'coverage': 'No body underpaint, removal, protection, occlusion or source-over composition is performed.',
        'outputs': {name: sha256(output/name) for name in ['layer.png', 'owner-mask.png', 'source-xy.npy', 'triangle-index.npy', 'request.json']},
    }
    (output/'receipt.json').write_text(json.dumps(receipt, indent=2, allow_nan=False)+'\n')
    return receipt

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec', type=Path)
    parser.add_argument('--out', required=True, type=Path, help='fresh output directory; its parent must already exist')
    args = parser.parse_args()
    try:
        result = run(args.spec, args.out)
    except (ContractError, OSError, ValueError, OverflowError, np.linalg.LinAlgError) as error:
        print(f'refused: {error}', file=sys.stderr)
        return 2
    print(json.dumps({'output': str(args.out.absolute()), 'owned_pixels': result['owned_output_pixels'], 'layer_sha256': result['outputs']['layer.png']}))
    return 0

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Bake constrained source-pixel bridges or replay their frozen maps.

Pillow/NumPy required. SciPy is only needed when generating new triangles.
No image model, network request or external credential is used.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rect(value, width, height):
    require(isinstance(value, list) and len(value) == 4 and
            all(type(v) is int for v in value), 'Rectangle needs four integers')
    x0, y0, x1, y1 = value
    require(0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height,
            'Rectangle outside canvas')
    return x0, y0, x1, y1


def load(path):
    path = path.resolve()
    spec = json.loads(path.read_text())
    require(spec.get('schema') == 'imagegen-source-warp/v1', 'Unknown spec schema')
    for name, expected in spec.get('files_sha256', {}).items():
        require(sha(path.parent/name) == expected, 'Source hash differs: '+name)
    body = np.array(Image.open(path.parent/spec['body']).convert('RGBA'))
    donor = np.array(Image.open(path.parent/spec['donor']).convert('RGBA'))
    require(body.shape == donor.shape, 'Body/donor canvases differ')
    height, width = body.shape[:2]
    require(spec['canvas'] == [width, height], 'Declared canvas differs')
    x0, y0, x1, y1 = rect(spec['donor_roi'], width, height)
    owner = np.zeros((height, width), dtype=np.uint8)
    owner[y0:y1, x0:x1] = 1
    return path, spec, body, donor, owner


def make_map(spec, owner):
    height, width = owner.shape
    src = np.asarray(spec['source_points'], dtype=float)
    dst = np.asarray(spec['target_points'], dtype=float)
    require(src.ndim == 2 and src.shape[1] == 2 and src.shape == dst.shape,
            'Control arrays need matching Nx2 coordinates')
    require(np.isfinite(src).all() and np.isfinite(dst).all(), 'Nonfinite control')
    require(len(np.unique(src, axis=0)) == len(src), 'Duplicate source control')
    if 'triangles' in spec:
        tris = np.asarray(spec['triangles'])
        require(tris.ndim == 2 and tris.shape[1] == 3 and
                np.issubdtype(tris.dtype, np.integer), 'Invalid triangle indices')
        require((tris >= 0).all() and (tris < len(src)).all(), 'Triangle index outside controls')
    else:
        from scipy.spatial import Delaunay
        tris = Delaunay(src).simplices
    yy, xx = np.indices((height, width))
    xy = np.stack((xx, yy), axis=-1).astype(np.int32)
    covered = np.zeros(owner.shape, dtype=bool)
    ratios = []
    for tri in tris:
        s, d = src[tri], dst[tri]
        sm = np.column_stack((s[1]-s[0], s[2]-s[0]))
        dm = np.column_stack((d[1]-d[0], d[2]-d[0]))
        source_area = float(np.linalg.det(sm))
        require(abs(source_area) > 1e-10, 'Collapsed source triangle')
        ratio = float(np.linalg.det(dm))/source_area
        require(ratio > 1e-8, 'Folded or collapsed target triangle')
        ratios.append(ratio)
        lo = np.maximum(np.floor(d.min(axis=0)).astype(int), 0)
        hi = np.minimum(np.ceil(d.max(axis=0)).astype(int), [width-1, height-1])
        if (hi < lo).any():
            continue
        gx, gy = np.meshgrid(np.arange(lo[0], hi[0]+1), np.arange(lo[1], hi[1]+1))
        q = np.column_stack((gx.ravel(), gy.ravel()))
        uv = (q-d[0]) @ np.linalg.inv(dm).T
        inside = (uv[:, 0] >= -1e-8) & (uv[:, 1] >= -1e-8) & (uv.sum(axis=1) <= 1+1e-8)
        at = q[inside]
        sampled = s[0] + uv[inside] @ np.stack((s[1]-s[0], s[2]-s[0]))
        sampled = np.floor(sampled+0.5).astype(np.int32)
        require((sampled >= 0).all() and (sampled[:, 0] < width).all() and
                (sampled[:, 1] < height).all(), 'Sampling outside source canvas')
        xy[at[:, 1], at[:, 0]] = sampled
        covered[at[:, 1], at[:, 0]] = True
    require(covered.all(), 'Uncovered output pixels; include fixed canvas boundary controls')
    xy[owner == 0] = np.stack((xx, yy), axis=-1)[owner == 0]
    return xy, tris, [min(ratios), max(ratios)]


def render(spec, body, donor, owner, xy, stored_owner):
    height, width = owner.shape
    require(xy.shape == (height, width, 2) and np.issubdtype(xy.dtype, np.integer),
            'Map needs integer HxWx2 source coordinates')
    require(stored_owner.shape == owner.shape and np.array_equal(owner, stored_owner),
            'Map ownership differs from declared ROI')
    require((xy >= 0).all() and (xy[:, :, 0] < width).all() and
            (xy[:, :, 1] < height).all(), 'Map addresses pixels outside source')
    yy, xx = np.indices(owner.shape)
    require(np.array_equal(xy[owner == 0], np.stack((xx, yy), axis=-1)[owner == 0]),
            'Body-owned pixels must preserve identity coordinates')
    result = body.copy()
    sampled = donor[xy[:, :, 1], xy[:, :, 0]]
    result[owner == 1] = sampled[owner == 1]
    unedited = result.copy()
    seen = set()
    edits = []
    for edit in spec.get('pixel_edits', []):
        x, y = edit['at']; sx, sy = edit['source_at']
        require(all(type(v) is int for v in [x, y, sx, sy]), 'Pixel coordinates must be integers')
        require(0 <= x < width and 0 <= y < height and 0 <= sx < width and 0 <= sy < height,
                'Pixel edit/sample outside canvas')
        require(owner[y, x] == 1 and (x, y) not in seen, 'Edit outside ROI or duplicate destination')
        seen.add((x, y))
        before = result[y, x].copy()
        result[y, x] = unedited[sy, sx]
        edits.append({'at':[x,y], 'source_at':[sx,sy], 'before':before.tolist(),
                      'after':result[y,x].tolist()})
    require(np.array_equal(result[owner == 0], body[owner == 0]), 'Protected body pixels changed')
    if 'rigid_rect' in spec:
        a = rect(spec['rigid_rect']['source'], width, height)
        b = rect(spec['rigid_rect']['target'], width, height)
        require((a[2]-a[0], a[3]-a[1]) == (b[2]-b[0], b[3]-b[1]), 'Rigid rectangles differ in size')
        require(np.array_equal(donor[a[1]:a[3], a[0]:a[2]], result[b[1]:b[3], b[0]:b[2]]),
                'Rigid rectangle RGBA differs')
    return result, edits, int(np.any(result != unedited, axis=2).sum())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    replay = sub.add_parser('replay', help='Read-only frozen-map verification')
    replay.add_argument('spec', type=Path)
    bake = sub.add_parser('bake', help='Create a fresh map/PNG/receipt from controls')
    bake.add_argument('spec', type=Path)
    bake.add_argument('output', type=Path)
    args = parser.parse_args()
    path, spec, body, donor, owner = load(args.spec)
    if args.command == 'bake':
        require(not args.output.exists(), 'Refuse to overwrite output directory')
        xy, tris, ratios = make_map(spec, owner)
    else:
        with np.load(path.parent/spec['map'], allow_pickle=False) as maps:
            xy = maps['source_xy']; stored_owner = maps['source_kind']
        require(np.array_equal(owner, stored_owner), 'Frozen ownership differs')
        tris, ratios = None, None
    result, edits, changed = render(spec, body, donor, owner, xy, owner)
    if 'expected' in spec:
        expected = np.array(Image.open(path.parent/spec['expected']).convert('RGBA'))
        require(np.array_equal(result, expected), 'Reconstructed RGBA differs from retained expected image')
    report = {'passed':True, 'command':args.command, 'spec_sha256':sha(path),
        'canvas':spec['canvas'], 'RGBA_sha256':hashlib.sha256(result.tobytes()).hexdigest(),
        'protected_body_exact':True, 'rigid_rectangle_checked':'rigid_rect' in spec,
        'expected_RGBA_checked':'expected' in spec, 'requested_pixel_edits':len(edits),
        'actual_changed_RGBA_pixels':changed,
        'boundary':'Pixel replay only; no visual-quality score, inferred anatomy or runtime acceptance.'}
    if args.command == 'bake':
        args.output.mkdir(parents=True)
        Image.fromarray(result).save(args.output/'frame.png')
        np.savez_compressed(args.output/'source-map.npz', source_xy=xy, source_kind=owner)
        (args.output/'triangles.json').write_text(json.dumps(tris.tolist())+'\n')
        report.update(triangle_area_ratio_range=ratios, pixel_edit_receipts=edits,
                      output_png_sha256=sha(args.output/'frame.png'))
        (args.output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({'passed':False,'error':str(exc)}), file=sys.stderr)
        sys.exit(1)

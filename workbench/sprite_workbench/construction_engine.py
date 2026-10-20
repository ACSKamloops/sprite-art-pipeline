"""Exact accelerated local receipt construction, derived from the pinned toolkit.

The operation and validation rules remain construction_core.core's. Only the
integer compositor and diff traversal differ: identical cel bindings render once,
and NumPy int64 implements the original nonnegative integer formula exactly.
This module does not change the original pinned source or its hash domain.
"""
from __future__ import annotations

import copy
import numpy as np

from .construction_core import core
from .construction_core.canonical import content_hash


def composite(project, bindings):
    """Return flat uint8 RGBA; bound int64 temporaries to 65,536 pixels."""
    area = project['canvas']['width'] * project['canvas']['height']
    out = np.zeros((area, 4), dtype=np.uint8)
    palette = np.asarray(project['palette'], dtype=np.int64)
    for start in range(0, area, 65536):
        end = min(start+65536, area)
        chunk = np.zeros((end-start, 4), dtype=np.int64)
        for cel_id in bindings:
            if cel_id is None:
                continue
            pixels = project['cels'][cel_id]['pixels'][start:end]
            src = palette[np.asarray(pixels, dtype=np.int64)]
            opaque = src[:, 3] == 255
            chunk[opaque] = src[opaque]
            partial = (src[:, 3] != 0) & ~opaque
            if not np.any(partial):
                continue
            s, d = src[partial], chunk[partial]
            sa, da = s[:, 3:4], d[:, 3:4]
            n = sa * 255 + da * (255-sa)
            rgb = (s[:, :3]*sa*255 + d[:, :3]*da*(255-sa) + n//2)//n
            chunk[partial] = np.concatenate((rgb, (n+127)//255), axis=1)
        out[start:end] = chunk
    return out


def diff_projects(before, after):
    width = before['canvas']['width']
    cels, frames, cached = {}, {}, {}
    for key, cel in before['cels'].items():
        a = np.asarray(cel['pixels'], dtype=np.int64)
        b = np.asarray(after['cels'][key]['pixels'], dtype=np.int64)
        changed = np.flatnonzero(a != b)
        if changed.size:
            points = np.column_stack((changed % width, changed // width)).tolist()
            cels[key] = {'changed_pixels': len(points), 'coordinates': points}
    layers = [layer['id'] for layer in before['layers']]
    for frame in before['frames']:
        binding = tuple(frame['cels'].get(layer) for layer in layers)
        if binding not in cached:
            a, b = composite(before, binding), composite(after, binding)
            changed = np.flatnonzero(np.any(a != b, axis=1))
            if changed.size:
                points = np.column_stack((changed % width, changed // width)).tolist()
                cached[binding] = {'changed_pixels': len(points), 'coordinates': points}
                xs, ys = changed % width, changed // width
                cached[binding]['bounds'] = [int(xs.min()), int(ys.min()), int(xs.max())+1, int(ys.max())+1]
            else:
                cached[binding] = None
        if cached[binding] is not None:
            frames[frame['id']] = copy.deepcopy(cached[binding])
    return {'cels': cels, 'frames': frames,
            'unchanged_frames': [frame['id'] for frame in before['frames'] if frame['id'] not in frames]}


def apply_transaction(project, transaction):
    """Same local project and exact receipt as the pinned scalar implementation."""
    core.validate_project(project)
    core.shape(transaction, ['schema', 'expected_project_sha256', 'reason', 'operations'])
    core.require(transaction['schema'] == 'sprite-edit-transaction/v1', 'Unsupported transaction')
    before_hash = content_hash(project)
    core.require(transaction['expected_project_sha256'] == before_hash, 'Stale project')
    core.require(core.identifier(transaction['reason']) and isinstance(transaction['operations'], list)
                 and bool(transaction['operations']), 'Empty edit')
    result = copy.deepcopy(project)
    for operation in transaction['operations']:
        core._operation(result, operation)
    core.validate_project(result)
    receipt = {'schema': 'sprite-edit-receipt/v1', 'before_sha256': before_hash,
        'after_sha256': content_hash(result), 'transaction': copy.deepcopy(transaction),
        'diff': diff_projects(project, result)}
    return {'project': result, 'receipt': receipt}

"""Exact local-v1 raster edits, disclosed ordering rules and explicit local guards.

Frames are one-based; coordinates/regions are zero-based/inclusive. Selectors
are explicit snapshots. This does not claim the unavailable vendor handler.
"""
from collections import Counter, deque
from fractions import Fraction
import hashlib
import re

import numpy as np

from .core import MAX_SEQUENCE_BYTES, ValidationError, canonical_json, load_sequence, save_sequence


def color(value):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?", value):
        raise ValidationError(f"Invalid literal RGBA: {value!r}")
    text = value[1:] + ("ff" if len(value) == 7 else "")
    return np.array([int(text[i:i+2], 16) for i in range(0, 8, 2)], dtype=np.uint8)


def coordinate(p, w, h):
    if not isinstance(p, (list, tuple)) or len(p) != 2 or any(type(x) != int for x in p):
        raise ValidationError("Coordinates must be2integers")
    x, y = p
    if not (0 <= x < w and 0 <= y < h):
        raise ValidationError("Coordinate outside canvas")
    return x, y


def region(box, w, h):
    if not isinstance(box, (list, tuple)) or len(box) != 4:
        raise ValidationError("Region must be inclusive[left,top,right,bottom]")
    l, t = coordinate(box[:2], w, h)
    r, b = coordinate(box[2:], w, h)
    if l > r or t > b:
        raise ValidationError("Reversed region")
    return l, t, r, b


def neighbors(conn):
    if conn not in (4, 8):
        raise ValidationError("Connectivity must be4or8")
    return [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(1, 1), (-1, 1), (1, -1), (-1, -1)] if conn == 8 else [])


def connected(eligible, seed, conn=4, limit=None):
    h, w = eligible.shape
    x, y = coordinate(seed, w, h)
    result = np.zeros_like(eligible, dtype=bool)
    if not eligible[y, x]:
        return result
    todo = deque([(x, y)])
    result[y, x] = True
    count = 1
    steps = neighbors(conn)
    while todo:
        x, y = todo.popleft()
        for dx, dy in steps:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and eligible[ny, nx] and not result[ny, nx]:
                count += 1
                if limit is not None and count > limit:
                    raise ValidationError("Fill exceeds max_pixels")
                result[ny, nx] = True
                todo.append((nx, ny))
    return result


def matches(array, rgba, tolerance=0):
    if type(tolerance) != int or not 0 <= tolerance <= 255:
        raise ValidationError("Tolerance must be integer0..255")
    alpha = array[..., 3] == rgba[3]
    if rgba[3] == 0:
        return alpha
    return alpha & (np.abs(array[..., :3].astype(np.int16) - rgba[:3]).max(axis=-1) <= tolerance)


def selection(array, selector, offset=(0, 0)):
    h, w = array.shape[:2]
    if not isinstance(selector, dict) or "kind" not in selector:
        raise ValidationError("Selection needs a kind")
    kind = selector["kind"]
    allowed = {'rectangle':{'kind','region'}, 'polygon':{'kind','points','region'},
        'color':{'kind','color','colors','region','tolerance'}, 'colors':{'kind','colors','region','tolerance'},
        'alpha':{'kind','min','max','region'}, 'contiguous':{'kind','seed','region','tolerance','connectivity'}}
    if not isinstance(kind,str) or kind not in allowed or set(selector)-allowed[kind]:
        raise ValidationError('Unknown selector kind or fields')
    required = {'rectangle':'region','polygon':'points','contiguous':'seed'}
    if kind in required and required[kind] not in selector:
        raise ValidationError('Missing selector geometry')
    result = np.zeros((h, w), bool)
    if not isinstance(offset, (list, tuple)) or len(offset) != 2:
        raise ValidationError("Offsets must be integer pairs")
    dx, dy = offset
    if any(type(v) != int for v in offset):
        raise ValidationError("Offsets must be integer pairs")
    if kind == "rectangle":
        l, t, r, b = region(selector["region"], w, h)
        # Offset rectangles are clipped, an explicitly local policy.
        l, r, t, b = max(0, l+dx), min(w-1, r+dx), max(0, t+dy), min(h-1, b+dy)
        if l <= r and t <= b:
            result[t:b+1, l:r+1] = True
    elif kind == "polygon":
        points = selector["points"]
        if not isinstance(points,(list,tuple)) or not 3 <= len(points) <= 1000:
            raise ValidationError("Polygon needs3..1000points")
        points = [coordinate(p, w, h) for p in points]
        yy, xx = np.mgrid[:h, :w]
        xx, yy = xx+.5-dx, yy+.5-dy
        # Named local even-odd pixel-center policy, not unknown vendor boundary parity.
        for (x1, y1), (x2, y2) in zip(points, points[1:]+points[:1]):
            if y1 != y2:
                result ^= ((y1 > yy) != (y2 > yy)) & (xx < (x2-x1)*(yy-y1)/(y2-y1)+x1)
    elif kind in ("colors", "color"):
        values = selector.get("colors", [selector.get("color")])
        if not isinstance(values,(list,tuple)) or not 1 <= len(values) <= 256:
            raise ValidationError("Color selector needs1..256colors")
        for value in values:
            result |= matches(array, color(value), selector.get("tolerance", 0))
    elif kind == "alpha":
        lo, hi = selector.get("min", 1), selector.get("max", 255)
        if any(type(v) != int for v in (lo, hi)) or not 0 <= lo <= hi <= 255:
            raise ValidationError("Invalid alpha selector interval")
        result = (array[..., 3] >= lo) & (array[..., 3] <= hi)
    elif kind == "contiguous":
        x, y = coordinate(selector["seed"], w, h)
        eligible = matches(array, array[y, x], selector.get("tolerance", 0))
        if "region" in selector:
            l, t, r, b = region(selector["region"], w, h)
            boundary = np.zeros((h, w), bool); boundary[t:b+1, l:r+1] = True
            eligible &= boundary
        result = connected(eligible, (x, y), selector.get("connectivity", 4))
    else:
        raise ValidationError("Unsupported local selector kind")
    if kind not in ("rectangle", "polygon") and (dx or dy):
        raise ValidationError("Offsets apply only to rectangle/polygon")
    if 'region' in selector and kind != 'rectangle':
        l,t,r,b = region(selector['region'],w,h)
        bound=np.zeros((h,w),bool);bound[t:b+1,l:r+1]=True
        result &= bound
    return result


def line(a, b):
    x, y = a; ex, ey = b
    dx, dy = abs(ex-x), -abs(ey-y)
    sx, sy = 1 if x < ex else -1, 1 if y < ey else -1
    err = dx+dy
    while True:
        yield x, y
        if (x, y) == (ex, ey):
            break
        e2 = 2*err
        if e2 >= dy: err += dy; x += sx
        if e2 <= dx: err += dx; y += sy


def grow(mask):
    out = mask.copy()
    out[1:] |= mask[:-1]; out[:-1] |= mask[1:]
    out[:, 1:] |= mask[:, :-1]; out[:, :-1] |= mask[:, 1:]
    return out


def apply_edits(layers, changes, protected=None):
    if not layers or not isinstance(changes, list) or not changes or len(changes) > 1000:
        raise ValidationError("Need named layers and1..1000ordered changes")
    if not isinstance(layers, dict) or len(layers) > 128:
        raise ValidationError("Layers must be a bounded named object")
    if sum(np.asarray(value).nbytes for value in layers.values()) > MAX_SEQUENCE_BYTES:
        raise ValidationError("Aggregate layer byte budget exceeded")
    initial = {}; result = {}
    shape = None
    for name, value in layers.items():
        a = np.asarray(value)
        if a.dtype != np.uint8 or a.ndim != 4 or a.shape[-1] != 4:
            raise ValidationError("Layer must be uint8[frames,height,width,4]")
        if min(a.shape[:3]) < 1 or np.prod(a.shape[:3]) > 128_000_000:
            raise ValidationError("Layer/mask resource budget exceeded or empty layer")
        if shape is not None and shape != a.shape:
            raise ValidationError("Layer dimensions differ")
        shape = a.shape
        initial[name] = a.copy(); result[name] = a.copy()
    n, h, w, _ = shape
    if not n or w*h*n > 128_000_000:
        raise ValidationError("Layer/mask resource budget exceeded")
    protection = {}
    for name, mask in (protected or {}).items():
        a = np.asarray(mask)
        if name not in layers or a.dtype != bool or a.shape != (n, h, w):
            raise ValidationError("Protection shape/layer mismatch")
        protection[name] = a
    masks = {}; audit = []
    specific = {"patch_pixels": {"pixels"}, "map_colors": {"region", "colors"},
        "copy_region": {"source_layer", "source_frame", "region", "at"},
        "select_mask": {"name", "selector", "combine", "offsets"},
        "flood_fill": {"seed", "expected", "color", "region", "tolerance", "connectivity", "max_pixels"},
        "brush": {"points", "color", "size", "shape", "mode", "region", "pixel_perfect"},
        "outline": {"mode", "color", "colors", "width", "silhouette_layers"}}
    common = {"operation", "layer", "frames", "reason", "view", "mask"}
    required = {"patch_pixels": {"pixels"}, "map_colors": {"region", "colors"},
        "copy_region": {"source_layer", "source_frame", "region", "at"}, "select_mask": {"name", "selector"},
        "flood_fill": {"seed", "expected", "color"}, "brush": {"points"}, "outline": {"mode"}}
    for ordinal, op in enumerate(changes):
        if not isinstance(op, dict) or op.get("operation") not in specific:
            raise ValidationError("Unknown raster operation")
        kind = op["operation"]
        if set(op) - common - specific[kind]:
            raise ValidationError("Unknown operation field")
        if required[kind] - set(op):
            raise ValidationError("Missing required raster operation fields")
        name = op.get("layer", "image")
        if not isinstance(name, str) or name not in result or not isinstance(op.get("reason"), str) or not op["reason"].strip():
            raise ValidationError("Operation needs known layer and observed reason")
        if 'view' in op and (not isinstance(op['view'],str) or not op['view']):
            raise ValidationError("View must be nonempty text")
        if 'colors' in op and (not isinstance(op['colors'],dict) or not 1 <= len(op['colors']) <= 256):
            raise ValidationError("Color mapping must be a nonempty bounded object")
        if kind == 'brush' and op.get('mode','paint') == 'paint' and 'color' not in op:
            raise ValidationError("Paint brush requires a color")
        if kind == 'outline':
            if op['mode'] == 'recolor' and 'colors' not in op:
                raise ValidationError("Recolor outline requires colors")
            if op['mode'] not in ('recolor','erase') and 'color' not in op:
                raise ValidationError("Outline requires a color")
        if 'color' in op:
            color(op['color'])
        if 'pixel_perfect' in op and type(op['pixel_perfect']) != bool:
            raise ValidationError('Pixel-perfect flag must be boolean')
        indices = op.get("frames")
        if not isinstance(indices, list) or not indices or any(type(i) != int or not 1 <= i <= n for i in indices) or len(set(indices)) != len(indices):
            raise ValidationError("Frames must be unique one-based indices")
        if kind == "select_mask":
            label = op.get("name", "")
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", label):
                raise ValidationError("Invalid mask name")
            offsets = op.get("offsets", [[0, 0]]*len(indices))
            if len(offsets) != len(indices):
                raise ValidationError("Mask offset count differs")
            for frame, off in zip(indices, offsets):
                if (label, frame) not in masks and (len(masks)+1)*w*h > 128_000_000:
                    raise ValidationError("Aggregate selection pixel budget exceeded")
                selected = selection(result[name][frame-1], op["selector"], off)
                key = (label, frame)
                previous = masks.get(key, np.zeros((h, w), bool))
                mode = op.get("combine", "replace")
                if mode == "replace": masks[key] = selected
                elif mode == "add": masks[key] = previous | selected
                elif mode == "subtract": masks[key] = previous & ~selected
                elif mode == "intersect": masks[key] = previous & selected
                else: raise ValidationError("Unknown mask combine mode")
            audit.append({"operation": kind, "ordinal": ordinal, "changed": 0})
            continue
        total = 0; touched_total = 0
        for frame in indices:
            target = result[name][frame-1]
            before = target.copy()
            permitted = np.ones((h, w), bool)
            if "mask" in op:
                key = (op["mask"], frame)
                if key not in masks: raise ValidationError("Mask not declared for selected frame")
                permitted &= masks[key]
            touched = np.zeros((h, w), bool)
            if "region" in op and kind != "copy_region":
                l, t, r, b = region(op["region"], w, h)
                bound = np.zeros((h, w), bool); bound[t:b+1, l:r+1] = True
                permitted &= bound
            if kind == "patch_pixels":
                pixels = op["pixels"]
                if not 1 <= len(pixels) <= 10000: raise ValidationError("Invalid patch size")
                seen = set()
                for entry in pixels:
                    if len(entry) != 4: raise ValidationError("Patch entry needs x,y,expected,replacement")
                    x, y = coordinate(entry[:2], w, h)
                    old, new = color(entry[2]), color(entry[3])
                    if (x, y) in seen: raise ValidationError("Duplicate pixel assignment")
                    seen.add((x, y))
                    if permitted[y, x]:
                        if not np.array_equal(target[y, x], old): raise ValidationError("Expected pixel guard failed")
                        target[y, x] = new; touched[y, x] = True
            elif kind == "map_colors":
                mappings = [(color(k), color(v)) for k, v in op["colors"].items()]
                if any(a[3] != b[3] for a, b in mappings): raise ValidationError("Color mapping must preserve alpha")
                normalized = [tuple(a) for a, _ in mappings]
                if len(set(normalized)) != len(normalized): raise ValidationError("Duplicate normalized map colors")
                for old, new in mappings:
                    hit = (before == old).all(axis=-1) & permitted
                    target[hit] = new; touched |= hit
            elif kind == "copy_region":
                src_name = op.get("source_layer", name); src_frame = op["source_frame"]
                if src_name not in initial or type(src_frame) != int or not 1 <= src_frame <= n:
                    raise ValidationError("Invalid copy source")
                l, t, r, b = region(op["region"], w, h); x, y = coordinate(op["at"], w, h)
                coordinate([x+r-l, y+b-t], w, h)
                local = permitted[y:y+b-t+1, x:x+r-l+1]
                dst = target[y:y+b-t+1, x:x+r-l+1]
                dst[local] = initial[src_name][src_frame-1, t:b+1, l:r+1][local]
                touched[y:y+b-t+1, x:x+r-l+1] = local
            elif kind == "flood_fill":
                x, y = coordinate(op["seed"], w, h)
                expected, replacement = color(op["expected"]), color(op["color"])
                if not permitted[y, x]: raise ValidationError("Fill seed excluded by region/mask")
                if not np.array_equal(target[y, x], expected): raise ValidationError("Fill seed guard failed")
                maximum = op.get("max_pixels", w*h)
                if type(maximum) != int or not 1 <= maximum <= w*h: raise ValidationError("Invalid fill limit")
                touched = connected(matches(target, expected, op.get("tolerance", 0)) & permitted, [x, y], op.get("connectivity", 4), maximum)
                target[touched] = replacement
            elif kind == "brush":
                points = op["points"]
                if not 1 <= len(points) <= 10000: raise ValidationError("Invalid brush point count")
                points = [coordinate(p, w, h) for p in points]
                center_count = 1+sum(max(abs(a[0]-b[0]),abs(a[1]-b[1])) for a,b in zip(points,points[1:]))
                if center_count > 200000:
                    raise ValidationError("Brush interpolation budget exceeded")
                size = op.get("size", 1)
                if type(size) != int or not 1 <= size <= 64: raise ValidationError("Brush size must be1..64")
                shape_name = op.get("shape", "circle")
                if shape_name not in ("circle", "square", "diamond"): raise ValidationError("Unknown brush shape")
                mode = op.get("mode", "paint")
                if mode not in ("paint", "erase"): raise ValidationError("Unknown brush mode")
                replacement = np.zeros(4, np.uint8) if mode == "erase" else color(op["color"])
                centers = [points[0]]
                for a, b in zip(points, points[1:]): centers.extend(list(line(a, b))[1:])
                if len(centers) > 200000: raise ValidationError("Brush interpolation budget exceeded")
                if op.get("pixel_perfect", False):
                    if size != 1: raise ValidationError("Pixel-perfect brush requires size1")
                    counts = Counter(centers)
                    centers = [p for i, p in enumerate(centers) if i in (0, len(centers)-1) or counts[p] > 1 or not (abs(centers[i-1][0]-centers[i+1][0]) == 1 and abs(centers[i-1][1]-centers[i+1][1]) == 1)]
                low = -((size-1)//2); high = low+size-1
                dy_grid, dx_grid = np.mgrid[low:high+1,low:high+1]
                cx, cy = dx_grid-(low+high)/2, dy_grid-(low+high)/2
                stamp = np.ones((size,size),bool)
                if shape_name == 'circle': stamp &= cx*cx+cy*cy <= (size/2)**2
                if shape_name == 'diamond': stamp &= abs(cx)+abs(cy) <= size/2
                dxs,dys = dx_grid[stamp],dy_grid[stamp]
                if len(centers)*len(dxs) > 32_000_000:
                    raise ValidationError("Brush stamp work budget exceeded")
                for x, y in centers:
                    nx,ny = x+dxs,y+dys
                    valid = (nx>=0)&(nx<w)&(ny>=0)&(ny<h)
                    touched[ny[valid],nx[valid]] = True
                touched &= permitted; target[touched] = replacement
            elif kind == "outline":
                width = op.get("width", 1)
                if type(width) != int or not 1 <= width <= 32: raise ValidationError("Outline width must be1..32")
                names = op.get("silhouette_layers", [name])
                if not names or any(k not in initial for k in names): raise ValidationError("Unknown silhouette layer")
                silhouette = np.logical_or.reduce([initial[k][frame-1, ..., 3] != 0 for k in names])
                expanded = silhouette.copy(); inner = silhouette.copy()
                for _ in range(width):
                    expanded = grow(expanded)
                    padded = np.pad(inner, 1, constant_values=False)
                    inner = padded[1:-1, 1:-1] & padded[:-2, 1:-1] & padded[2:, 1:-1] & padded[1:-1, :-2] & padded[1:-1, 2:]
                mode = op["mode"]
                if mode in ("outside", "outer"): touched = expanded & ~silhouette
                elif mode in ("inside", "inner", "erase", "recolor"): touched = silhouette & ~inner
                else: raise ValidationError("Unsupported local outline mode")
                touched &= permitted
                if mode == "recolor":
                    mapped = np.zeros((h, w), bool)
                    for old, new in op["colors"].items():
                        hit = (before == color(old)).all(axis=-1) & touched
                        target[hit] = color(new); mapped |= hit
                    touched = mapped
                else: target[touched] = np.zeros(4, np.uint8) if mode == "erase" else color(op["color"])
            if name in protection and (touched & protection[name][frame-1]).any():
                raise ValidationError("Trusted protected pixels touched")
            total += int((before != target).any(axis=-1).sum())
            touched_total += int(touched.sum())
        audit.append({"ordinal": ordinal, "operation": kind, "layer": name, "frames": indices, "matched": touched_total, "changed": total})
    return result, {"dialect": "local-raster-v1", "operations": audit, "status": "candidate_needs_visual_review", "input_mutated": False}


def edit_sequence(store, source, changes, *, protected=None, head=None, expected_head=None):
    doc, frames = load_sequence(store, source)
    edited, audit = apply_edits({"image": np.stack(frames)}, changes, protected)
    decision = store.put_json({'kind':'raster-decision','version':1,'parent_sequence':source,'changes':changes,'audit':audit,
        'destination':'post-scene composite patch; original scene/parts remain immutable'})
    seq = save_sequence(store, edited["image"], durations=[Fraction(*f["duration"]) for f in doc["frames"]],
        pivots=[f["pivot"] for f in doc["frames"]], directions=[f["direction"] for f in doc["frames"]], loop=doc["loop"],
        play_count=doc.get('play_count',0 if doc['loop'] else 1),
        metadata={**doc["metadata"], "parent_sequence": source, "raster_decision":decision, "edit_dialect": "local-raster-v1"})
    revision = store.put_json({"kind": "revision", "version": 1, "parent": source, "sequence": seq, "changes": changes, "audit": audit})
    published = store.set_head(head, revision, expected_head) if head else False
    return {"revision": revision, "sequence": seq, "audit": audit, "published": published,
            "status": "stale_candidate" if head and not published else "candidate_needs_visual_review"}


def crop(store, raster_id, box, *, node="composite"):
    a = store.get_raster(raster_id); h, w = a.shape[:2]
    l, t, r, b = region(box, w, h)
    cropped = a[t:b+1, l:r+1].copy()
    guard = hashlib.sha256(canonical_json({"dialect": "local-crop-v1", "source": raster_id, "node": node,
        "region": list(box), "rgba_sha256": hashlib.sha256(cropped.tobytes()).hexdigest()})).hexdigest()
    return {"dialect": "local-crop-v1", "source": raster_id, "node": node, "region": list(box), "guard": guard,
            "rgba": cropped.tolist(), "raster": store.put_raster(cropped)}


def paste(store, packet, rows, *, expected, stamp=False):
    if type(stamp)!=bool:raise ValidationError('Paste stamp must be a boolean')
    current = crop(store, packet["source"], packet["region"], node=packet["node"])
    if current["guard"] != expected or packet["guard"] != expected:
        raise ValidationError("Local crop/source/node guard failed")
    a = store.get_raster(packet["source"]).copy()
    patch = np.asarray(rows)
    l, t, r, b = packet["region"]
    if patch.shape != (b-t+1, r-l+1, 4) or patch.dtype.kind not in "ui" or (patch < 0).any() or (patch > 255).any():
        raise ValidationError("Paste needs exact bounded RGBA rows")
    patch = patch.astype(np.uint8)
    selected = patch[..., 3] != 0 if stamp else np.ones(patch.shape[:2], bool)
    a[t:b+1, l:r+1][selected] = patch[selected]
    decision=store.put_json({'kind':'raster-paste','version':1,'parent_raster':packet['source'],
        'patch':store.put_raster(patch),'guard':expected,'node':packet['node'],'region':packet['region'],
        'stamp':stamp,'dialect':'local-guarded-crop-paste-v1'})
    document=store.get_json(store.put_raster(a))
    document['metadata']={'parent_raster':packet['source'],'paste_decision':decision}
    return store.put_json(document)

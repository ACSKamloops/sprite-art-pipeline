"""Supplied-cell terrain assembly with explicit local topology conventions.

No terrain pixels, missing tile variants or map objects are invented.
"""
from __future__ import annotations

import numpy as np

from .core import ValidationError, UnsupportedCapability, validate_raster, save_sequence


def topology_indices(occupied, *, boundary="empty"):
    """Local-v1 four-edge mask N=1,E=2,S=4,W=8; empty cells use -1.

    This is a named local contract, not the vendor's Wang/blob atlas ordering.
    """
    a = np.asarray(occupied)
    if a.ndim != 2 or a.dtype != np.bool_ or not a.size:
        raise ValidationError("Topology requires nonempty bool[row,column]")
    if a.size > 16_777_216: raise ValidationError("Topology exceeds cell budget")
    if boundary not in ("empty", "wrap"): raise ValidationError("Boundary must be empty or wrap")
    out = np.full(a.shape, -1, np.int16)
    for y,x in zip(*np.nonzero(a)):
        value = 0
        for dy,dx,bit in ((-1,0,1),(0,1,2),(1,0,4),(0,-1,8)):
            yy,xx = y+dy,x+dx
            connected = a[yy % a.shape[0], xx % a.shape[1]] if boundary == "wrap" else (
                0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and a[yy,xx])
            if connected: value |= bit
        out[y,x] = value
    return out


def _cells(cells):
    if not cells: raise ValidationError("At least one supplied cell is required")
    normalized = {k:validate_raster(a) for k,a in cells.items()}
    shape = next(iter(normalized.values())).shape
    if any(a.shape != shape for a in normalized.values()): raise ValidationError("Cell dimensions differ")
    return normalized, shape


def render_map(cells, layout, *, empty=-1):
    """Overwrite each explicit cell into its map slot, preserving hidden RGB."""
    cells, shape = _cells(cells); layout = np.asarray(layout)
    if layout.ndim != 2 or not layout.size or layout.dtype.kind not in "iu":
        raise ValidationError("Layout requires integer[row,column]")
    h,w = shape[:2]; rows,cols = layout.shape
    if rows*cols*h*w > 16_777_216: raise ValidationError("Map exceeds pixel budget")
    missing = {int(k) for k in np.unique(layout) if k != empty and int(k) not in cells}
    if missing: raise ValidationError(f"Missing supplied cells: {sorted(missing)}")
    out = np.zeros((rows*h,cols*w,4), np.uint8)
    for y in range(rows):
        for x in range(cols):
            key = int(layout[y,x])
            if key != empty: out[y*h:(y+1)*h,x*w:(x+1)*w] = cells[key]
    return out


def connectivity_sheet(cells, order, *, columns=4):
    cells, shape = _cells(cells); order = list(order)
    if not order or len(set(order)) != len(order) or any(k not in cells for k in order):
        raise ValidationError("Sheet order must contain distinct supplied cell keys")
    if type(columns) is not int or columns < 1: raise ValidationError("Columns must be positive integer")
    # Explicit order is authoritative; incomplete last row remains transparent.
    h,w = shape[:2]; rows = (len(order)+columns-1)//columns
    if rows*columns*h*w > 16_777_216: raise ValidationError("Sheet exceeds pixel budget")
    sheet = np.zeros((rows*h,columns*w,4), np.uint8); slots = []
    for i,key in enumerate(order):
        x,y = i%columns*w, i//columns*h
        sheet[y:y+h,x:x+w] = cells[key]
        slots.append({"key": key, "rect": [x,y,w,h]})
    return sheet, {"kind": "tile-sheet", "version": 1, "cell_size": [w,h], "slots": slots,
                   "ordering": "explicit-supplied", "capability": "supplied-art"}


def reblit_regions(canvas, patches):
    """Ordered ROI overwrites, with optional binary masks and exact expected bytes.

    Validate the entire list against evolving candidate arrays. A later failed
    guard raises without mutating the input or publishing any revision.
    """
    out = validate_raster(canvas).copy(); records = []
    for i,patch in enumerate(patches):
        a = validate_raster(patch["array"])
        origin = patch.get("origin")
        if not isinstance(origin, (list,tuple)) or len(origin)!=2 or any(type(v)!=int for v in origin):
            raise ValidationError("Patch origin requires integer x,y")
        x,y = origin; h,w = a.shape[:2]
        if x<0 or y<0 or x+w>out.shape[1] or y+h>out.shape[0]: raise ValidationError("Patch exceeds canvas")
        current = out[y:y+h,x:x+w]
        if patch.get("expected") is not None:
            expected = validate_raster(patch["expected"])
            if expected.shape!=a.shape or not np.array_equal(current, expected):
                raise ValidationError("Region expected-byte guard failed")
        mask = patch.get("mask")
        if mask is None: current[:] = a
        else:
            mask = np.asarray(mask)
            if mask.shape != (h,w) or mask.dtype != np.bool_: raise ValidationError("Patch mask must be bool[H,W]")
            current[mask] = a[mask]
        records.append({"op": "region-reblit", "index": i, "origin": [x,y], "size": [w,h],
                        "masked": mask is not None, "guarded": patch.get("expected") is not None, "mode": "rgba-overwrite"})
    return out, records


def save_terrain(store, cells, layout, *, topology=None, metadata=None):
    raster = render_map(cells, layout)
    recipe=store.put_json({'kind':'terrain-recipe','version':1,'cells':[{"key":int(k),"raster":store.put_raster(a)} for k,a in cells.items()],
        'layout':np.asarray(layout).tolist(),'topology':topology})
    sequence = save_sequence(store, [raster], metadata={"method": "supplied-terrain-v1", **(metadata or {}), 'terrain_recipe':recipe})
    return store.put_json({"kind": "terrain", "version": 1, "sequence": sequence,
                           "cells": [{"key": int(k), "raster":store.put_raster(a)} for k,a in cells.items()],
                           "layout": np.asarray(layout).tolist(), "topology": topology,
                           "capability": "supplied-art"})


def generate_tiles(*args, **kwargs):
    raise UnsupportedCapability("learned-terrain", "Provide every required tile/region; learned topology art and inpainting are unavailable")

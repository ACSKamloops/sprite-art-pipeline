"""Explicit raster preparation; no neural image transformation is performed.

Profiles bind source conventions, not an installed editor's canvas/codec runtime.
Every operation returns new arrays and an ordered, JSON-safe audit record.
"""
from __future__ import annotations

import base64
from io import BytesIO
import math

import numpy as np
from PIL import Image

from .core import ValidationError, UnsupportedCapability, digest, validate_raster, MAX_SEQUENCE_BYTES


PROFILES = {
    "local-rgba-v1": {"encoding": "raw", "hidden_rgb": "preserve", "reference_max": None},
    "godot-raw-v1": {"encoding": "raw", "hidden_rgb": "zero", "reference_max": None},
    "lua-pro-reference-v1": {"encoding": "raw", "hidden_rgb": "preserve", "reference_max": 2048},
    "web-rotation-reference-nearest-v1": {"encoding": "png", "hidden_rgb": "preserve", "reference_max": 1024},
}
LEARNED = {"caption", "enhance_prompt", "unzoom", "correct_pixelart", "remove_background", "generate", "inpaint"}


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValidationError(f"{name} must be an integer >= {minimum}")
    return value


def nearest_resize(array, width, height):
    """Local-v1 left-cell sampling: source=floor(destination*source/destination_size)."""
    a = validate_raster(array)
    width, height = _integer(width, "width", 1), _integer(height, "height", 1)
    if width * height > 16_777_216:
        raise ValidationError("Resize exceeds pixel budget")
    yy = np.arange(height, dtype=np.int64) * a.shape[0] // height
    xx = np.arange(width, dtype=np.int64) * a.shape[1] // width
    return a[yy[:, None], xx].copy()


def crop_pad(array, roi):
    """ROI is [x,y,width,height]; out-of-source samples become transparent zero.

    The requested origin is retained even for negative coordinates. No automatic
    bounding-box recentering occurs.
    """
    a = validate_raster(array)
    if len(roi) != 4 or any(type(x) is not int for x in roi):
        raise ValidationError("ROI requires four integer coordinates")
    x, y, w, h = roi
    _integer(w, "ROI width", 1); _integer(h, "ROI height", 1)
    if w * h > 16_777_216:
        raise ValidationError("ROI exceeds pixel budget")
    out = np.zeros((h, w, 4), np.uint8)
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x+w, a.shape[1]), min(y+h, a.shape[0])
    if x1 > x0 and y1 > y0:
        out[y0-y:y1-y, x0-x:x1-x] = a[y0:y1, x0:x1]
    return out


def binary_mask(mask, shape):
    m = np.asarray(mask)
    if m.shape == (*shape, 4) and m.dtype == np.uint8:
        return (m[..., 3] != 0).astype(np.uint8) * 255
    if m.shape == shape and m.dtype in (np.uint8, np.bool_):
        return (m != 0).astype(np.uint8) * 255
    raise ValidationError("Mask must match canvas as bool/uint8[H,W] or uint8[H,W,4]")


def choose_unzoom(profile, choice, slider_value=None):
    """Lua widget state, including Custom's absent onchange, is preserved."""
    if profile != "lua-widget-v1":
        raise ValidationError("Unknown unzoom widget profile")
    if choice == "Auto": return 0
    if choice == "None": return -1
    if choice != "Custom": raise ValidationError("Unknown unzoom choice")
    if slider_value is None: return None
    if type(slider_value) is not int or not 2 <= slider_value <= 256:
        raise ValidationError("Custom slider must be an integer in 2..256")
    return slider_value


def correction_strength(profile, value=None):
    """Wire scalar conventions; this does not invoke a correction model."""
    if profile == "lua-widget-v1":
        value = 100 if value is None else value
        if type(value) is not int or not 0 <= value <= 200: raise ValidationError("Lua strength is integer0..200")
        return value / 100
    if profile in ("godot-widget-v1", "web-widget-compat-v1", "web-widget-corrected-v1"):
        value = (0.5 if profile == "godot-widget-v1" else 0.1) if value is None else value
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValidationError("Strength must be finite")
        low = 0.05 if profile == "godot-widget-v1" else 0
        if not low <= value <= 1: raise ValidationError("Strength is outside widget range")
        return 0.3 if profile == "web-widget-compat-v1" and value == 0 else float(value)
    raise ValidationError("Unknown correction profile")


def prepare_prompt(profile, text, *, first=None, end=None, interpolate=False, choices=None, allowed_choices=None):
    """Typed prompt/source selection without enhancement or caption inference.

    The returned descriptor is local and inert. Lua MiniMax undoubles stored
    percent pairs and omits exact Auto/empty/null choices. Godot strips text.
    Lua V3 interpolation requires an end frame; Godot permits its absence.
    """
    if profile not in ("lua-minimax-v1", "lua-v3-v1", "godot-v3-v1"):
        raise ValidationError("Unknown prompt preparation profile")
    if text is not None and not isinstance(text,str): raise ValidationError("Prompt must be text or null")
    normalized = text
    if profile == "lua-minimax-v1":
        normalized = None if text is None or not text.strip() else text.replace("%%", "%")
    elif profile == "godot-v3-v1": normalized = (text or "").strip()
    if profile != "lua-minimax-v1" and not normalized:
        raise ValidationError("V3 enhancement input requires nonblank action")
    if first is None: raise ValidationError("A supplied first/reference frame is required")
    if interpolate and profile != "godot-v3-v1" and end is None:
        raise ValidationError("This interpolation adapter requires an end frame")
    first = validate_raster(first)
    end = None if end is None else validate_raster(end)
    picked = {}
    for key,value in (choices or {}).items():
        if value is None or value == "" or value == "Auto": continue
        if key not in (allowed_choices or {}) or value not in allowed_choices[key]:
            raise ValidationError("Unknown picked caption choice")
        picked[key] = value
    return {"profile":profile,"target_field":"description" if profile=="lua-minimax-v1" else "action",
            "text":normalized,"first":_descriptor(first,"raw"),
            "end":None if end is None else _descriptor(end,"raw"),"choices":picked,
            "remote_transformation":"unsupported","local_operations":["text-normalization","typed-source-selection"]}


def palette_conditioner(array, limit=4096):
    """One exemplar per RGBA key with nonzero alpha, first appearance order.

    Distinctness matches source conditioners; order is a declared local policy
    (Lua pairs iteration is not promised). Frequencies are returned separately.
    """
    a = validate_raster(array)
    _integer(limit, "palette limit", 1)
    counts = {}
    for p in a.reshape(-1, 4):
        if p[3]:
            key = tuple(int(v) for v in p)
            counts[key] = counts.get(key, 0) + 1
    if len(counts) > limit: raise ValidationError("Distinct palette exceeds conditioner limit")
    return {"colors": [list(k) for k in counts], "counts": list(counts.values()), "order": "first-appearance-local-v1"}


def _descriptor(array, encoding):
    a = validate_raster(array)
    if encoding == "raw":
        raw = a.tobytes(); fmt = "rgba"
    else:
        buf = BytesIO(); Image.fromarray(a).save(buf, format="PNG"); raw = buf.getvalue(); fmt = "png"
    return {"width": a.shape[1], "height": a.shape[0], "format": fmt,
            "data": base64.b64encode(raw).decode("ascii"), "encoded_sha256": digest(raw),
            "decoded_rgba_sha256": digest(a.tobytes())}


def prepare_request(adapter, images, options=None):
    """Prepare supplied arrays without publication. Store is optional, never serialized.

    Options: roi, mask (source canvas), output_size, pad_size, references,
    reference_limit (slot count), encoding, palette, store, capability.
    ROI applies before resize; mask uses the same operations with binary nearest
    sampling. pad_size places at floor-half difference and rejects cropping.
    """
    options = dict(options or {})
    capability = options.get("capability")
    if capability in LEARNED:
        raise UnsupportedCapability(capability, "Preparation is available; private learned transformation is not")
    if capability is not None: raise ValidationError("Unknown preparation capability")
    if adapter not in PROFILES: raise ValidationError("Unknown preparation adapter")
    profile = PROFILES[adapter]
    sources = list(images)
    if not sources or len(sources)>512: raise ValidationError("Source image count must be1..512")
    sources = [validate_raster(a) for a in sources]
    if sum(a.nbytes for a in sources)>MAX_SEQUENCE_BYTES: raise ValidationError("Preparation exceeds local byte budget")
    images = [a.copy() for a in sources]
    encoding = options.get("encoding", profile["encoding"])
    if encoding not in ("raw", "png"): raise ValidationError("Encoding must be raw or png")
    planned_pixels=0
    for a in images:
        size=options.get("pad_size",options.get("output_size",options.get("roi",[0,0,a.shape[1],a.shape[0]])[-2:]))
        if len(size)!=2 or any(type(v)!=int or v<=0 for v in size): raise ValidationError("Prepared size must be positive width,height")
        planned_pixels+=size[0]*size[1]
    if planned_pixels*4>MAX_SEQUENCE_BYTES: raise ValidationError("Prepared output exceeds local byte budget")
    mask = None
    source_mask = None
    source_mask_format = None
    if options.get("mask") is not None:
        if any(a.shape != images[0].shape for a in images): raise ValidationError("Masked batch canvases differ")
        mask = binary_mask(options["mask"], images[0].shape[:2])
        original_mask=np.asarray(options['mask'])
        source_mask_format={'shape':list(original_mask.shape),'dtype':str(original_mask.dtype),
                            'packing':'rgba' if original_mask.ndim==3 else 'original values in alpha channel'}
        if original_mask.ndim==3:source_mask=original_mask.copy()
        else:
            source_mask=np.zeros((*original_mask.shape,4),np.uint8)
            source_mask[...,3]=original_mask.astype(np.uint8)
    operations, geometry = [], []
    arrays = []
    for i, source in enumerate(images):
        a = source.copy(); origin = [0, 0]; pad_offset = [0, 0]
        if "roi" in options:
            a = crop_pad(a, options["roi"]); origin = list(options["roi"][:2])
            operations.append({"op": "crop-pad", "slot": i, "roi": list(options["roi"]), "outside": "transparent-zero"})
        before_resize = [a.shape[1], a.shape[0]]
        if "output_size" in options:
            size = options["output_size"]
            if len(size) != 2: raise ValidationError("Output size needs width,height")
            a = nearest_resize(a, *size)
            operations.append({"op": "nearest-resize", "slot": i, "from": before_resize, "to": list(size), "sampler": "left-cell-local-v1"})
        if "pad_size" in options:
            w, h = options["pad_size"]
            _integer(w, "pad width", 1); _integer(h, "pad height", 1)
            if w < a.shape[1] or h < a.shape[0]: raise ValidationError("Pad cannot crop input")
            pad_offset = [(w-a.shape[1])//2, (h-a.shape[0])//2]
            a = crop_pad(a, [-pad_offset[0], -pad_offset[1], w, h])
            operations.append({"op": "center-pad", "slot": i, "size": [w, h], "offset": pad_offset})
        if profile["hidden_rgb"] == "zero":
            a[a[..., 3] == 0, :3] = 0
            operations.append({"op": "zero-hidden-rgb", "slot": i, "predicate": "alpha==0"})
        arrays.append(a)
        geometry.append({"source_size": [source.shape[1], source.shape[0]], "origin": origin,
                         "pre_resize_size": before_resize, "output_size": [a.shape[1], a.shape[0]], "pad_offset": pad_offset})
    if mask is not None:
        rgba = np.zeros((*mask.shape, 4), np.uint8); rgba[..., 3] = mask
        if "roi" in options: rgba = crop_pad(rgba, options["roi"])
        if "output_size" in options: rgba = nearest_resize(rgba, *options["output_size"])
        if "pad_size" in options:
            dx, dy = geometry[0]["pad_offset"]; rgba = crop_pad(rgba, [-dx, -dy, *options["pad_size"]])
        mask = rgba[..., 3].copy()
        operations.append({"op": "binary-mask", "predicate": "source-alpha!=0-or-scalar!=0", "transform": "same-roi-size-pad"})
    refs = []
    raw_refs = list(options.get("references", []))
    limit = options.get("reference_limit", 4)
    _integer(limit, "reference slot limit", 1)
    if limit>16: raise ValidationError("Reference limit exceeds local16slot budget")
    if len(raw_refs) > limit: raise ValidationError("Too many reference slots")
    if sum(validate_raster(a).nbytes for a in raw_refs)>MAX_SEQUENCE_BYTES:
        raise ValidationError("Reference input exceeds local byte budget")
    roles=list(options.get("reference_roles",["unspecified"]*len(raw_refs)))
    if len(roles)!=len(raw_refs) or any(role not in ("style","subject","unspecified") for role in roles):
        raise ValidationError("Each reference must have an explicit valid role")
    for i, ref in enumerate(raw_refs):
        a = validate_raster(ref).copy(); before = [a.shape[1], a.shape[0]]
        maximum = profile["reference_max"]
        if maximum and max(before) > maximum:
            factor = maximum/max(before)
            a = nearest_resize(a, max(1, math.floor(before[0]*factor)), max(1, math.floor(before[1]*factor)))
        if profile["hidden_rgb"] == "zero": a[a[...,3]==0,:3]=0
        refs.append(a)
        operations.append({"op": "reference", "slot": i, "from": before, "to": [a.shape[1], a.shape[0]], "max_side": maximum,
                           "sampler": "left-cell-local-v1", "role": roles[i], "hidden_rgb":profile["hidden_rgb"]})
    result = {"adapter": adapter, "capability": "deterministic-source", "arrays": arrays, "references": refs,
              "mask": mask, "geometry": geometry, "operations": operations,
              "descriptors": [_descriptor(a, encoding) for a in arrays],
              "reference_descriptors": [_descriptor(a, encoding) for a in refs], "reference_roles":roles}
    mask_rgba=None
    if mask is not None:
        mask_rgba=np.zeros((*mask.shape,4),np.uint8);mask_rgba[...,3]=mask
        result["mask_descriptor"]=_descriptor(mask_rgba,encoding)
    if options.get("palette"): result["palette"] = palette_conditioner(arrays[0])
    store = options.get("store")
    if store is not None:
        result["raster_ids"] = [store.put_raster(a) for a in arrays]
        result["reference_ids"] = [store.put_raster(a) for a in refs]
        result["mask_id"]=store.put_raster(mask_rgba) if mask_rgba is not None else None
        result["audit_id"] = store.put_json({"kind": "preparation", "version": 1, "adapter": adapter,
                                            "source_rasters":[store.put_raster(a) for a in sources],
                                            "source_references":[store.put_raster(a) for a in raw_refs],
                                            "source_mask":store.put_raster(source_mask) if source_mask is not None else None,
                                            "source_mask_format":source_mask_format,
                                            "rasters": result["raster_ids"], "references": result["reference_ids"],
                                            "mask":result["mask_id"],"reference_roles":roles,
                                            "geometry": geometry, "operations": operations})
    return result

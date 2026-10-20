"""Orthographic source conventions and explicit supplied motion.

Coordinates are normalized about .5, yaw east=0/north=90. These are
deterministic point transforms, never an anatomical or motion generator.
"""
from __future__ import annotations

import math

from .core import ValidationError, UnsupportedCapability, save_sequence


LUA_DIRECTIONS = (90, 67.5, 45, 22.5, 0, 337.5, 315, 292.5, 270, 247.5, 225, 202.5, 180, 157.5, 135, 112.5)
GODOT_DIRECTIONS = (90, 45, 0, 315, 270, 225, 180, 135)
WEIGHTS = {"NECK": 2, "NOSE": 1.8, "LEFT SHOULDER": 1.5, "RIGHT SHOULDER": 1.5,
           "LEFT HIP": 1.5, "RIGHT HIP": 1.5, "LEFT EYE": 1.2, "RIGHT EYE": 1.2,
           "LEFT KNEE": 1, "RIGHT KNEE": 1}
PROFILES = ("lua-raw-v1", "lua-ranked-v1", "godot-raw-v1", "godot-bridge64-v1")


def view_tilt(view, profile="godot-bridge-v1"):
    """Do not unify the generic Godot helper's defaults with active Bridge/Lua."""
    if profile in ("godot-bridge-v1","lua-wrapper-v1"):
        values={"side":5,"low top-down":20,"high top-down":35}
    elif profile=="godot-general-v1": values={"side":10,"low top-down":25,"high top-down":40}
    else: raise ValidationError("Unknown camera view profile")
    if view not in values: raise ValidationError("Unknown camera view")
    return values[view]


def _finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValidationError("Pose values must be finite numbers")
    return float(value)


def _joints(joints, dimensions=3):
    out, labels = [], set()
    for joint in joints:
        if not isinstance(joint, dict): raise ValidationError("Joint must be an object")
        label = joint.get("label")
        if not isinstance(label, str) or not label or label in labels:
            raise ValidationError("Joint labels must be nonempty and unique")
        labels.add(label)
        out.append({**joint, "label": label, **{axis: _finite(joint[axis]) for axis in "xyz"[:dimensions] if axis in joint}})
    if not out: raise ValidationError("Pose must contain labeled joints")
    return out


def project_pose(joints, direction_degrees=0, tilt_degrees=30, profile="godot-raw-v1"):
    if profile not in PROFILES: raise ValidationError("Unknown pose projection profile")
    joints = _joints(joints)
    yaw, tilt = math.radians(_finite(direction_degrees)), math.radians(_finite(tilt_degrees))
    ca, sa, ct, st = math.cos(yaw), math.sin(yaw), math.cos(tilt), math.sin(tilt)
    lua = profile.startswith("lua")
    out = []
    for j in joints:
        default = 0 if lua else .5
        x, y, z = (j.get(axis, default)-.5 for axis in "xyz")
        xr, zr = x*ca-z*sa, x*sa+z*ca
        depth = -zr+y*st if lua else y*st+zr*ct
        quantized = math.floor((depth+.5)*1000) if lua else math.trunc(depth*1000)
        p = {"label": j["label"], "x": xr+.5, "y": y*ct-zr*st+.5,
             "depth": depth, "z_index": quantized, "profile": profile}
        if profile == "godot-bridge64-v1":
            p["x"], p["y"] = math.trunc(p["x"]*64), math.trunc(p["y"]*64)
        out.append(p)
    if profile == "lua-ranked-v1":
        ranks = {v:i+1 for i,v in enumerate(sorted({p["z_index"] for p in out}))}
        for p in out:
            p["raw_z_index"] = p["z_index"]; p["z_index"] = ranks[p["z_index"]]
    return out


def flip_pose(joints, profile="catalog-z-v1"):
    joints = _joints(joints)
    if profile not in ("catalog-z-v1", "godot-general-x-v1"): raise ValidationError("Unknown flip profile")
    out = []
    for j in joints:
        p = dict(j)
        axis = "z" if profile == "catalog-z-v1" else "x"
        if profile == "catalog-z-v1" or axis in p:
            p[axis] = 1-p.get(axis, .5)
        label = p["label"]
        if profile == "catalog-z-v1":
            body = ("SHOULDER", "ELBOW", "ARM", "HIP", "KNEE", "LEG", "FOOT", "EYE", "EAR")
            if label in {"LEFT "+b for b in body}: label = label.replace("LEFT", "RIGHT")
            elif label in {"RIGHT "+b for b in body}: label = label.replace("RIGHT", "LEFT")
        else:
            if label.startswith("LEFT"): label = label.replace("LEFT", "RIGHT")
            elif label.startswith("RIGHT"): label = label.replace("RIGHT", "LEFT")
        p["label"] = label; out.append(p)
    return out


def draw_depth_channels(joints, profile="godot-raster-ordinal-v1"):
    """Source draw/export depth stages without assuming the raw depth is wire depth.

    Godot duplicates increment an ordinal per equal raw-depth group, potentially
    colliding with the next group's ordinal. Supplied list order is explicit.
    Lua ties share rank. These are alpha encodings, not public camera depth.
    """
    out=[dict(j) for j in joints]
    if not out or any(type(p.get("z_index"))!=int for p in out): raise ValidationError("Integer draw z_index required")
    if len(out)>254: raise ValidationError("Local alpha-depth adapter supports at most254 points")
    values=sorted({p["z_index"] for p in out})
    if profile=="godot-raster-ordinal-v1":
        ordinal={v:i for i,v in enumerate(values)};used={}
        for p in out:
            raw=p["z_index"]; extra=used.get(raw,0);used[raw]=extra+1
            p["raw_z_index"]=raw;p["z_index"]=ordinal[raw]+extra
            p["alpha"]=max(0,254-p["z_index"])
            p["recovered_z_index"]=255-p["alpha"] if p["alpha"] not in (0,255) else None
    elif profile=="lua-raster-rank-v1":
        ranks={v:i+1 for i,v in enumerate(values)}
        for p in out:
            raw=p["z_index"];p["raw_z_index"]=raw;p["z_index"]=ranks[raw]
            p["alpha"]=255-p["z_index"];p["recovered_z_index"]=p["z_index"]
    else: raise ValidationError("Unknown draw-depth profile")
    return out


def nearest_pose(template, reference, profile="godot-normalized-v1", canvas=None):
    """Enumerate explicit source search domains; local ties use listed first.

    Lua source pairs iteration is not a portable tie policy. This API records its
    deterministic tie policy instead of claiming that unspecified host order.
    Lua reference coordinates are pixels and must include NECK. Godot uses
    normalized coordinates and all matching labels.
    """
    template = _joints(template)
    reference = {p["label"]: p for p in _joints(reference, 2)}
    if profile not in ("lua-pixel-v1", "godot-normalized-v1"):
        raise ValidationError("Unknown nearest-pose profile")
    lua = profile == "lua-pixel-v1"
    if lua:
        if canvas is None or len(canvas) != 2 or any(type(x) is not int or x <= 0 for x in canvas):
            raise ValidationError("Lua fitting requires positive integer pixel canvas")
        if "NECK" not in reference or "NECK" not in {j["label"] for j in template}:
            raise ValidationError("Lua fitting requires NECK in source and reference")
    if any("x" not in p or "y" not in p for p in reference.values()):
        raise ValidationError("Reference joints need x,y")
    if not set(reference).intersection(j["label"] for j in template):
        raise ValidationError("Reference and template have no matching labels")
    best = None; examined = 0
    for yaw in LUA_DIRECTIONS if lua else GODOT_DIRECTIONS:
        for tilt in range(5, 86, 10):
            projected = project_pose(template, yaw, tilt, "lua-ranked-v1" if lua else "godot-raw-v1")
            pred = {p["label"]: p for p in projected}
            dx = dy = 0
            if lua:
                dx = reference["NECK"]["x"]-pred["NECK"]["x"]*canvas[0]
                dy = reference["NECK"]["y"]-pred["NECK"]["y"]*canvas[1]
            error, total = 0., 0.
            for label, truth in reference.items():
                if label not in pred or (lua and label not in WEIGHTS): continue
                p = pred[label]; weight = WEIGHTS.get(label, 1)
                px, py = (p["x"]*canvas[0], p["y"]*canvas[1]) if lua else (p["x"], p["y"])
                error += weight*((truth["x"]-dx-px)**2+(truth["y"]-dy-py)**2); total += weight
            error /= max(total, 1); examined += 1
            if best is None or error < best["error"]:
                best = {"direction_degrees": yaw, "tilt_degrees": tilt, "error": error, "joints": projected}
    return {**best, "profile": profile, "examined": examined, "tie_policy": "listed-first-local-v1"}


def source_shape_compatibility(branch, *, corrected=False):
    """Explicitly expose recovered auto-helper and Bridge label mismatches.

    No silent name/label conversion or false successful automatic fitting.
    """
    if branch == "lua-auto-direction":
        return {"direction_degrees": 0, "tilt_degrees": None, "matched_terms": 0,
                "reason": "ipairs does not enumerate label-keyed projection"} if not corrected else {"use": "nearest_pose", "profile": "lua-pixel-v1"}
    if branch == "lua-auto-tilt":
        return {"tilt_degrees": -45, "matched_terms": 0,
                "reason": "ipairs does not enumerate label-keyed projection"} if not corrected else {"use": "nearest_pose", "profile": "lua-pixel-v1"}
    if branch == "godot-bridge-name-label":
        return {"valid_labeled_input_required": True, "implicit_name_conversion": False,
                "corrected": bool(corrected), "policy": "explicit-user-name-to-label" if corrected else "source-label-only"}
    raise ValidationError("Unknown source shape compatibility branch")


def project_frames(frames, *, direction_degrees=0, tilt_degrees=30, profile="lua-ranked-v1",
                   auto_direction=False, auto_tilt=False, reference=None, canvas=None, corrected=False):
    """Valid outer frame-list adapter for optional Lua helper shape mismatches.

    Corrected fitting is explicitly named, uses label lookup and requires an
    actual reference. Compatibility returns the source's unmatched helper
    fallbacks. Neither branch creates rendered art.
    """
    frames=list(frames)
    if not frames or len(frames)>512: raise ValidationError("Pose sequence requires1..512 frames")
    if (auto_direction or auto_tilt) and not profile.startswith("lua"):
        raise ValidationError("Optional compatibility auto helpers are Lua-specific")
    if (auto_direction or auto_tilt) and reference is None:
        raise ValidationError("Auto fitting requires an explicit reference")
    results=[]; states=[]
    for joints in frames:
        yaw,tilt=direction_degrees,tilt_degrees
        if auto_direction or auto_tilt:
            if corrected:
                fit=nearest_pose(joints,reference,"lua-pixel-v1",canvas)
                if auto_direction: yaw=fit["direction_degrees"]
                if auto_tilt: tilt=fit["tilt_degrees"]
                state={"method":"corrected-label-lookup-local-v1","error":fit["error"],"examined":fit["examined"]}
            else:
                if auto_direction: yaw=0
                if auto_tilt: tilt=-45
                state={"method":"source-ipairs-compatibility-v1","matched_terms":0}
        else: state={"method":"explicit-projection"}
        results.append(project_pose(joints,yaw,tilt,profile))
        states.append({**state,"direction_degrees":yaw,"tilt_degrees":tilt})
    return {"frames":results,"states":states,"profile":profile,"capability":"deterministic-source"}


def save_supplied_motion(store, frames, durations, *, direction="unspecified", pivots=None, joints=None):
    arrays = list(frames)
    if joints is not None and len(joints) != len(arrays): raise ValidationError("Pose/frame count differs")
    return save_sequence(store, arrays, durations, pivots, directions=[direction]*len(arrays),
                         metadata={"capability": "supplied-art", "method": "supplied-motion-v1", "joints": joints})


def generate_motion(*args, **kwargs):
    raise UnsupportedCapability("learned-motion", "Provide authored frames and/or key poses; anatomy and hidden views are not inferred")

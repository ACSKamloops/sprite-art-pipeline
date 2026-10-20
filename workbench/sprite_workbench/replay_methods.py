"""Callable, frozen local diagnostics for supplied-art method flows.

run_flow takes a fresh output path and a caller-owned Store. It writes a receipt,
exact PNG/editable exports and unviewed review pages. No provider, ambient font,
remote template, private model or authored character is used. These are connected
local subsets of the broader F01/F03/F06/F07/F08 contracts, not vendor replicas.
"""
from __future__ import annotations

import base64
from fractions import Fraction
from io import BytesIO
import math
from pathlib import Path

import numpy as np
from PIL import Image

from .acquisition import import_image
from .assets import (build_glyph_atlas, generate_asset, layout_shapes, render_text,
                     render_ui, save_viseme_timeline, virtual_view)
from .composition import compose_sequences
from .core import (Store, UnsupportedCapability, ValidationError, canonical_json,
                   digest, load_sequence, save_sequence)
from .export import export_sequence, import_editable, output_directory, png_bytes
from .pose import (draw_depth_channels, flip_pose, generate_motion, nearest_pose,
                   project_frames, project_pose, save_supplied_motion, view_tilt)
from .prepare import (choose_unzoom, correction_strength, prepare_prompt,
                      prepare_request)
from .raster import crop, edit_sequence, paste
from .terrain import (connectivity_sheet, generate_tiles, reblit_regions,
                      save_terrain, topology_indices)

FLOW_IDS = ("F01", "F03", "F06", "F07", "F08")


def _fixture():
    """Frozen 7x5 L/marker pattern; no generated or reference character art."""
    a = np.zeros((5, 7, 4), np.uint8)
    a[1:4, 1:3] = [37, 82, 121, 255]
    a[1, 4] = [209, 34, 61, 255]
    a[3, 5] = [18, 192, 73, 255]
    a[0, 6] = [91, 92, 93, 0]
    a[4, 0] = [14, 25, 36, 127]
    return a


def _check(receipt, name, passed, detail=None):
    record = {"name": name, "passed": bool(passed)}
    if detail is not None:
        record["detail"] = detail
    receipt["checks"].append(record)


def _negative(receipt, name, call, expected=ValidationError):
    receipt["routine_order"].append("negative: " + name)
    try:
        call()
    except expected as e:
        # Unsupported is a ValidationError subtype; record its stronger boundary.
        _check(receipt, name, True, e.to_dict() if isinstance(e, UnsupportedCapability)
               else {"error": type(e).__name__, "message": str(e)})
    else:
        _check(receipt, name, False, "Expected rejection did not occur")


def _exchange(store, ident, out, receipt, name="result", *, gif=False):
    receipt["routine_order"].append("export " + name + ": PNG/sheet/rational manifest/APNG/editable/review")
    formats = ["png", "sheet", "manifest", "apng", "editable", "review"]
    if gif:
        formats.append("gif")
    directory = out / "exports" / name
    report = export_sequence(store, ident, directory, formats)
    receipt["exports"][name] = {"directory": "exports/" + name, **report}
    receipt["reviews"][name] = {"file": "exports/" + name + "/review/review.html",
                               "continuous_motion_viewed": False, "visual_acceptance": "unreviewed"}
    before, arrays = load_sequence(store, ident)
    receipt["routine_order"].append("import " + name + " editable closure into a fresh output-local Store")
    reopened = Store(out / "reloaded-stores" / name)
    restored = import_editable(reopened, directory / "editable")
    after, restored_arrays = load_sequence(reopened, restored)
    _check(receipt, name + " editable identity and timeline", restored == ident and before == after)
    _check(receipt, name + " editable exact RGBA", len(arrays) == len(restored_arrays)
           and all(np.array_equal(a, b) for a, b in zip(arrays, restored_arrays)))
    png_exact = True
    for i, a in enumerate(arrays):
        with Image.open(directory / "frames" / f"frame-{i:04d}.png") as im:
            png_exact &= np.array_equal(a, np.array(im.convert("RGBA"), dtype=np.uint8))
    _check(receipt, name + " every PNG exact including hidden RGB", png_exact)
    _check(receipt, name + " review is generated but unviewed",
           report["formats"]["review"]["continuous_motion_viewed"] is False)
    return reopened


def _f01(store, out, r, a):
    r["routine_order"].append("encode frozen supplied array to PNG; import captured local bytes")
    encoded = png_bytes(a)
    source_file = out / "inputs" / "asymmetric.png"
    source_file.parent.mkdir()
    source_file.write_bytes(encoded)
    imported = import_image(store, source_file)
    doc, frames = load_sequence(store, imported["sequence"])
    r["artifacts"].update(source_bytes=imported["source_bytes"], imported_sequence=imported["sequence"])
    r["inputs"].update(encoded_sha256=digest(encoded), acquisition_missing_clock="local 1/12 second")
    _check(r, "captured PNG identity", imported["source_bytes"] == digest(encoded))
    _check(r, "decoded RGBA preserves hidden RGB and partial alpha", np.array_equal(frames[0], a))
    r["routine_order"].append("local RGBA preparation; persist source audit and one-frame sequence")
    prepared = prepare_request("local-rgba-v1", frames, {"store": store})
    parent = save_sequence(store, prepared["arrays"], [Fraction(1, 12)],
                           metadata={**doc["metadata"], "preparation": prepared["audit_id"],
                                     "parent_sequence": imported["sequence"]})
    r["artifacts"].update(preparation=prepared["audit_id"], prepared_sequence=parent)
    protection = np.zeros((1, 5, 7), bool)
    protection[0, 1, 4] = True
    changes = [
        {"operation": "patch_pixels", "frames": [1], "reason": "Change one supplied blue marker",
         "pixels": [[1, 1, "#255279ff", "#e7b513ff"]]},
        {"operation": "copy_region", "frames": [1], "reason": "Copy the original pre-edit blue marker",
         "source_layer": "image", "source_frame": 1, "region": [1, 1, 1, 1], "at": [3, 1]},
        {"operation": "map_colors", "frames": [1], "reason": "Map blue simultaneously in the declared region",
         "region": [0, 0, 6, 4], "colors": {"#255279ff": "#126c90ff"}},
    ]
    r["inputs"]["edit_changes"] = changes
    r["routine_order"].append("ordered guarded patch/copy/map; compare-and-swap revision publication")
    head = "replay/F01"
    if store.get_head(head) is not None:
        raise ValidationError("F01 diagnostic head exists; use a fresh Store")
    initial = store.set_head(head, parent, None)
    edited = edit_sequence(store, parent, changes, protected={"image": protection},
                           head=head, expected_head=parent)
    _, candidate = load_sequence(store, edited["sequence"])
    expected = a.copy()
    expected[1, 1] = [231, 181, 19, 255]
    expected[1, 3] = [37, 82, 121, 255]
    expected[np.all(expected == [37, 82, 121, 255], axis=2)] = [18, 108, 144, 255]
    _check(r, "initial source snapshot copy and ordered map", np.array_equal(candidate[0], expected))
    _check(r, "guarded publication and protected marker", initial and edited["published"]
           and store.get_head(head) == edited["revision"] and np.array_equal(candidate[0][1, 4], a[1, 4]))
    _negative(r, "protected edit rejects without advancing head", lambda: edit_sequence(
        store, parent, [{"operation": "patch_pixels", "frames": [1], "reason": "Deliberately hit protection",
                         "pixels": [[4, 1, "#d1223dff", "#010203ff"]]}],
        protected={"image": protection}, head=head, expected_head=edited["revision"]))
    r["routine_order"].append("attempt stale CAS; preserve the published diagnostic revision")
    stale = edit_sequence(store, parent, changes, head=head, expected_head=parent)
    _check(r, "stale CAS retains published revision", not stale["published"]
           and store.get_head(head) == edited["revision"])
    r["routine_order"].append("crop inclusive pixel rectangle; guarded overwrite including transparent RGB")
    packet = crop(store, store.put_raster(candidate[0]), [1, 1, 2, 1], node="diagnostic-marker")
    patch = [[[9, 8, 7, 255], [61, 62, 63, 0]]]
    _negative(r, "incorrect crop guard rejects", lambda: paste(store, packet, patch, expected="0" * 64))
    pasted = paste(store, packet, patch, expected=packet["guard"])
    final = expected.copy()
    final[1, 1:3] = patch[0]
    _check(r, "guarded paste overwrites hidden RGB", np.array_equal(store.get_raster(pasted), final))
    seq = save_sequence(store, [store.get_raster(pasted)], [Fraction(1, 12)],
                        metadata={"parent_sequence": edited["sequence"], "source_ids": [pasted],
                                  "method": "local-replay-F01-v1"})
    r["artifacts"].update(edited_sequence=edited["sequence"], revision=edited["revision"],
                          pasted_raster=pasted, sequence=seq)
    reopened = _exchange(store, seq, out, r, gif=True)
    _check(r, "source bytes and paste lineage survive closure", reopened.get_bytes(imported["source_bytes"]) == encoded
           and reopened.get_json(pasted)["metadata"]["parent_raster"] == packet["source"])
    _check(r, "partial-alpha GIF is explicitly unsupported", r["exports"]["result"]["formats"]["gif"]["status"] == "unsupported")
    _check(r, "source is immutable", np.array_equal(store.get_raster(imported["rasters"][0]), a))
    r["limitations"].extend(["Local raw-RGBA edit, guard and CAS dialect, not native indexed undo or vendor editor parity.",
                             "Partial alpha makes GIF unsupported; exact PNG/APNG/editable remain authoritative.",
                             "This acquisition fixture is a still PNG, not animated import/poster coverage."])


def _f03(store, out, r, a):
    joints = [{"label": label, "x": x, "y": y, "z": z} for label, x, y, z in
              [("NECK", .4, .3, .7), ("NOSE", .7, .2, .9),
               ("LEFT HIP", .2, .8, .3), ("RIGHT HIP", .8, .7, .6)]]
    r["inputs"].update(joints=joints, yaw_degrees=90, tilt_degrees=0, fitting_canvas=[80, 40])
    r["routine_order"].append("project asymmetric points with separate Lua/Godot depth conventions")
    lua = project_pose(joints, 90, 0, "lua-raw-v1")
    godot = project_pose(joints, 90, 0, "godot-raw-v1")
    expected_xy = [(1-j["z"], j["y"]) for j in joints]
    _check(r, "yaw90 independent x/y and opposite depth equations",
           all(math.isclose(p["x"], x) and math.isclose(p["y"], y)
               and math.isclose(p["depth"], -(j["x"]-.5)) and math.isclose(q["depth"], j["x"]-.5)
               for j, p, q, (x, y) in zip(joints, lua, godot, expected_xy)))
    rank = project_pose(joints, 0, 0, "lua-ranked-v1")
    _check(r, "Lua unique depth bins", [j["z_index"] for j in rank] == [2, 1, 4, 3])
    r["routine_order"].append("encode tied raw z groups with separate draw-depth/readback profiles")
    raw_depth = [{"label": "a", "z_index": -1000}, {"label": "b", "z_index": -1000},
                 {"label": "c", "z_index": 1000}]
    gd = draw_depth_channels(raw_depth)
    ld = draw_depth_channels(raw_depth, "lua-raster-rank-v1")
    _check(r, "Godot ordinal collision differs from shared Lua rank",
           [p["recovered_z_index"] for p in gd] == [1, 2, 2]
           and [p["recovered_z_index"] for p in ld] == [1, 1, 2])
    r["routine_order"].append("fit independent yaw0/tilt25 reference in normalized and neck-aligned pixel domains")
    t = math.radians(25)
    ref = [{"label": j["label"], "x": j["x"],
            "y": (j["y"]-.5)*math.cos(t)-(j["z"]-.5)*math.sin(t)+.5} for j in joints]
    pixels = [{"label": j["label"], "x": j["x"]*80+7, "y": j["y"]*40-3} for j in ref]
    gf = nearest_pose(joints, ref, "godot-normalized-v1")
    lf = nearest_pose(joints, pixels, "lua-pixel-v1", canvas=[80, 40])
    _check(r, "distinct search domains recover known reference", gf["examined"] == 72 and lf["examined"] == 144
           and all(v["direction_degrees"] == 0 and v["tilt_degrees"] == 25 and v["error"] < 1e-20 for v in [gf, lf]))
    r["routine_order"].append("compare source-shape compatibility with explicitly corrected label fit; flip")
    compat = project_frames([joints], auto_direction=True, auto_tilt=True, reference=pixels, canvas=[80, 40])
    corrected = project_frames([joints], auto_direction=True, auto_tilt=True, reference=pixels,
                               canvas=[80, 40], corrected=True)
    _check(r, "compatibility mismatch is not silently corrected", compat["states"][0]["tilt_degrees"] == -45
           and compat["states"][0]["matched_terms"] == 0 and corrected["states"][0]["tilt_degrees"] == 25)
    flipped = flip_pose(joints, "catalog-z-v1")
    _check(r, "catalog z flip swaps known side labels", flipped[2]["label"] == "RIGHT HIP"
           and math.isclose(flipped[2]["z"], .7))
    _check(r, "camera menu profiles stay distinct", view_tilt("side", "godot-bridge-v1") == 5
           and view_tilt("side", "godot-general-v1") == 10)
    record = {"kind": "replay-pose-diagnostic", "version": 1, "joints": joints,
              "lua": lua, "godot": godot, "ranked": rank, "draw_depth": {"lua": ld, "godot": gd},
              "normalized_fit": gf, "pixel_fit": lf, "compatibility": compat, "corrected": corrected}
    audit = store.put_json(record)
    r["inputs"]["normalized_reference"] = ref
    r["inputs"]["pixel_reference"] = pixels
    _negative(r, "Lua fit requires explicit canvas", lambda: nearest_pose(joints, pixels, "lua-pixel-v1"))
    _negative(r, "duplicate label rejected", lambda: project_pose([joints[0], joints[0]]))
    _negative(r, "nonfinite joint rejected", lambda: project_pose([{"label": "a", "x": float("nan")}]))
    _negative(r, "learned motion explicitly unavailable", lambda: generate_motion(joints), UnsupportedCapability)
    r["routine_order"].append("persist supplied geometric arrays and duplicate holds; points do not generate these rasters")
    arrays = [a, a.copy(), a[::-1].copy()]
    durations = [Fraction(1, 30), Fraction(2, 30), Fraction(4, 30)]
    supplied = save_supplied_motion(store, arrays, durations, pivots=[(3, 4)]*3,
                                    direction="north", joints=[lua, lua, godot])
    doc, _ = load_sequence(store, supplied)
    seq = save_sequence(store, arrays, durations, pivots=[(3, 4)]*3, directions=["north"]*3,
                        metadata={**doc["metadata"], "parent_sequence": supplied, "source_ids": [audit],
                                  "raster_relationship": "supplied geometric pattern/hold/vertical flip; no pose-to-art inference"})
    r["artifacts"].update(pose_diagnostic=audit, supplied_sequence=supplied, sequence=seq)
    _check(r, "duplicate holds preserve clocks and pivot", doc["frames"][0]["raster"] == doc["frames"][1]["raster"]
           and [f["duration"] for f in doc["frames"]] == [[1, 30], [1, 15], [2, 15]]
           and all(f["pivot"] == [3, 4] for f in doc["frames"]))
    reopened = _exchange(store, seq, out, r)
    _check(r, "projection audit survives editable closure", reopened.get_json(audit) == record)
    r["limitations"].extend(["Point transforms and depth encodings are not connected-bone rasterization or camera-nearness depth.",
                             "Listed-first nearest ties are local policy; compatibility and corrected fitting are different adapters.",
                             "Supplied hold/flip rasters are independent of projected points; no anatomy, hidden surfaces or neural motion."])


def _f06(store, out, r, a):
    occupied = np.array([[True, True, False], [False, True, True]], bool)
    r["routine_order"].append("derive local NESW topology from the frozen occupancy grid")
    layout = topology_indices(occupied)
    expected_layout = np.array([[2, 12, -1], [-1, 3, 8]], np.int16)
    _check(r, "independent four-edge topology", np.array_equal(layout, expected_layout))
    cells = {}
    for key in [2, 12, 3, 8]:
        cell = a.copy()
        cell[1, 4] = [key, 40+key, 90+key, 255]
        cells[key] = cell
    r["inputs"].update(occupied=occupied.tolist(), topology="N1/E2/S4/W8-local-v1; empty=-1",
                       supplied_cell_ids={str(k): store.put_raster(v) for k, v in cells.items()},
                       sheet_order=[12, 2, 8, 3], sheet_columns=2)
    r["routine_order"].append("pack explicit cell order; persist supplied map recipe and composed sequence")
    sheet, slots = connectivity_sheet(cells, [12, 2, 8, 3], columns=2)
    sheet_seq = save_sequence(store, [sheet], metadata={"method": "explicit-supplied-tile-sheet", "slots": slots,
                                                       "source_ids": list(r["inputs"]["supplied_cell_ids"].values())})
    terrain = save_terrain(store, cells, layout, topology={"convention": "N1/E2/S4/W8-local-v1"})
    terrain_doc = store.get_json(terrain)
    parent = terrain_doc["sequence"]
    parent_doc, arrays = load_sequence(store, parent)
    expected = np.zeros((10, 21, 4), np.uint8)
    expected[:5, :7] = cells[2]
    expected[:5, 7:14] = cells[12]
    expected[5:, 7:14] = cells[3]
    expected[5:, 14:] = cells[8]
    _check(r, "explicit sheet slots", slots["slots"][0]["key"] == 12
           and slots["slots"][2]["rect"] == [0, 5, 7, 5] and np.array_equal(sheet[:5, :7], cells[12]))
    _check(r, "independent map assembly including empty cells and hidden RGB", np.array_equal(arrays[0], expected))
    patch = np.array([[[90, 10, 40, 255], [9, 8, 7, 0]],
                      [[1, 2, 3, 0], [70, 60, 50, 127]]], np.uint8)
    mask = np.array([[True, False], [False, True]], bool)
    guard = expected[1:3, 1:3].copy()
    r["routine_order"].append("guarded masked region reblit with explicit expected bytes")
    revised, operations = reblit_regions(arrays[0], [{"array": patch, "origin": [1, 1], "expected": guard, "mask": mask}])
    oracle = expected.copy()
    oracle[1, 1] = patch[0, 0]
    oracle[2, 2] = patch[1, 1]
    _check(r, "masked patch changes only two selected pixels", np.array_equal(revised, oracle))
    _negative(r, "later reblit guard fails atomically", lambda: reblit_regions(arrays[0], [
        {"array": patch, "origin": [1, 1]}, {"array": patch, "origin": [1, 1], "expected": guard}]))
    _check(r, "failed reblit did not change original", np.array_equal(arrays[0], expected))
    _negative(r, "missing supplied tile fails", lambda: save_terrain(store, {2: cells[2]}, layout))
    _negative(r, "learned terrain explicitly unavailable", lambda: generate_tiles(occupied), UnsupportedCapability)
    mask_rgba = np.zeros((2, 2, 4), np.uint8)
    mask_rgba[..., 3] = mask.astype(np.uint8)*255
    patch_ids = {"raster": store.put_raster(patch), "expected": store.put_raster(guard), "mask": store.put_raster(mask_rgba)}
    decisions = [{**patch_ids, "origin": [1, 1], "mask_format": "bool[2,2] stored in alpha0/255"}]
    seq = save_sequence(store, [revised], metadata={**parent_doc["metadata"], "parent_sequence": parent,
                        "source_ids": list(patch_ids.values()), "region_patches": decisions, "region_operations": operations})
    r["artifacts"].update(terrain=terrain, baseline_sequence=parent, sheet_sequence=sheet_seq, sequence=seq,
                          patch_raster=patch_ids["raster"], patch_mask=patch_ids["mask"])
    reopened = _exchange(store, seq, out, r)
    restored_doc, _ = load_sequence(reopened, seq)
    q = restored_doc["metadata"]["region_patches"][0]
    rebuilt, _ = reblit_regions(load_sequence(reopened, parent)[1][0], [{"array": reopened.get_raster(q["raster"]),
        "expected": reopened.get_raster(q["expected"]), "mask": reopened.get_raster(q["mask"])[..., 3] != 0,
        "origin": q["origin"]}])
    _check(r, "reloaded reblit inputs reproduce exact result", np.array_equal(rebuilt, oracle))
    _exchange(store, sheet_seq, out, r, "sheet")
    r["limitations"].extend(["Local NESW and explicit overwrite layout are not the vendor 4x4 wildcard matcher, Wang ordering or generated seamless art.",
                             "The region patch is supplied pixels, not learned map-object inpainting or private packaging."])


def _f07(store, out, r, a):
    mask = np.zeros_like(a)
    mask[..., :3] = [33, 44, 55]
    mask[0, 6, 3] = 1  # Select the alpha-zero source marker deliberately.
    mask[2, 2, 3] = 255
    refs = [a[::-1].copy(), a.copy()]
    refs[1][1, 4] = [17, 201, 42, 255]
    options = {"roi": [-1, 0, 9, 5], "output_size": [6, 4], "pad_size": [10, 6],
               "mask": mask, "references": refs, "reference_roles": ["style", "subject"], "store": store}
    r["inputs"].update(roi=options["roi"], output_size=options["output_size"], pad_size=options["pad_size"],
                       source_mask=store.put_raster(mask), reference_ids=[store.put_raster(v) for v in refs],
                       reference_roles=["style", "subject"], sampler="floor(dst_index*source_size/destination_size)-local-v1")
    r["routine_order"].append("prepare identical ROI/resize/pad/mask/order with Godot-zero and Lua-preserve hidden RGB")
    gd = prepare_request("godot-raw-v1", [a], options)
    lu = prepare_request("lua-pro-reference-v1", [a], options)
    cropped = np.zeros((5, 9, 4), np.uint8)
    cropped[:, 1:8] = a
    xx, yy = [0, 1, 3, 4, 6, 7], [0, 1, 2, 3]
    small = cropped[np.array(yy)[:, None], np.array(xx)]
    oracle = np.zeros((6, 10, 4), np.uint8)
    oracle[1:5, 2:8] = small
    zeroed = oracle.copy()
    zeroed[zeroed[..., 3] == 0, :3] = 0
    mask_crop = np.zeros((5, 9), np.uint8)
    mask_crop[:, 1:8] = (mask[..., 3] != 0).astype(np.uint8)*255
    mask_oracle = np.zeros((6, 10), np.uint8)
    mask_oracle[1:5, 2:8] = mask_crop[np.array(yy)[:, None], np.array(xx)]
    _check(r, "independent crop/resize/pad oracle", np.array_equal(gd["arrays"][0], zeroed)
           and np.array_equal(lu["arrays"][0], oracle))
    _check(r, "mask uses selection alpha independently of source alpha", np.array_equal(gd["mask"], mask_oracle)
           and gd["mask"][1, 7] == 255 and gd["arrays"][0][1, 7, 3] == 0)
    _check(r, "ROI origin and pad offset retained", gd["geometry"][0]["origin"] == [-1, 0]
           and gd["geometry"][0]["pad_offset"] == [2, 1])
    _check(r, "ordered style/subject references stay distinct", lu["reference_roles"] == ["style", "subject"]
           and all(np.array_equal(got, ref) for got, ref in zip(lu["references"], refs)))
    _check(r, "raw descriptor matches final bytes", base64.b64decode(gd["descriptors"][0]["data"]) == zeroed.tobytes())
    r["routine_order"].append("web nearest-reference cap and PNG encoding, with explicit local sampler")
    wide = np.repeat(a[1:2, 1:2], 1025, axis=1)
    wide[0, -1] = [31, 32, 33, 255]
    web = prepare_request("web-rotation-reference-nearest-v1", [a], {"references": [wide], "store": store})
    with Image.open(BytesIO(base64.b64decode(web["descriptors"][0]["data"]))) as im:
        decoded = np.array(im.convert("RGBA"), dtype=np.uint8)
    _check(r, "PNG hidden RGB preserved and reference capped to1024", np.array_equal(decoded, a)
           and web["references"][0].shape == (1, 1024, 4)
           and web["references"][0][0, -1].tolist() == [37, 82, 121, 255])
    r["routine_order"].append("inert Auto/null/percent/end-frame prompt and correction/unzoom widget routing")
    prompt = prepare_prompt("lua-minimax-v1", "  50%% test ", first=a,
                            choices={"view": "Auto", "direction": "east", "empty": "", "none": None},
                            allowed_choices={"direction": ["east", "west"]})
    optional = prepare_prompt("godot-v3-v1", " test ", first=a, interpolate=True)
    widgets = {"auto": choose_unzoom("lua-widget-v1", "Auto"), "none": choose_unzoom("lua-widget-v1", "None"),
               "custom_unchanged": choose_unzoom("lua-widget-v1", "Custom"),
               "web_compat_zero": correction_strength("web-widget-compat-v1", 0),
               "web_corrected_zero": correction_strength("web-widget-corrected-v1", 0)}
    _check(r, "typed prompt routing preserves caller distinctions", prompt["text"] == "  50% test "
           and prompt["target_field"] == "description" and prompt["choices"] == {"direction": "east"}
           and optional["text"] == "test" and optional["end"] is None)
    _check(r, "unzoom absence and compatibility zero differ", widgets == {"auto": 0, "none": -1,
           "custom_unchanged": None, "web_compat_zero": .3, "web_corrected_zero": 0.0})
    _negative(r, "Lua interpolation requires end", lambda: prepare_prompt("lua-v3-v1", "test", first=a, interpolate=True))
    _negative(r, "Godot strength zero outside widget range", lambda: correction_strength("godot-widget-v1", 0))
    _negative(r, "reference role cardinality rejected", lambda: prepare_request("local-rgba-v1", [a],
               {"references": refs, "reference_roles": ["style"]}))
    _negative(r, "learned caption explicitly unavailable", lambda: prepare_request("local-rgba-v1", [a],
               {"capability": "caption"}), UnsupportedCapability)
    seq = save_sequence(store, [gd["arrays"][0], lu["arrays"][0]], [Fraction(1, 5)]*2,
                        metadata={"preparation": gd["audit_id"], "source_ids": [lu["audit_id"], web["audit_id"]],
                                  "prompt_descriptors": [prompt, optional], "widget_choices": widgets,
                                  "method": "adapter-comparison-local-replay-F07-v1"})
    r["artifacts"].update(godot_preparation=gd["audit_id"], lua_preparation=lu["audit_id"],
                          web_preparation=web["audit_id"], sequence=seq)
    reopened = _exchange(store, seq, out, r)
    audit = reopened.get_json(gd["audit_id"])
    _check(r, "original RGBA mask and format survive closure", np.array_equal(reopened.get_raster(audit["source_mask"]), mask)
           and audit["source_mask_format"]["shape"] == [5, 7, 4] and audit["source_mask_format"]["dtype"] == "uint8")
    _check(r, "original input/reference arrays remain unchanged", np.array_equal(a, _fixture()))
    r["inputs"]["web_source_reference"] = store.put_raster(wide)
    r["limitations"].extend(["Left-cell nearest and reference slots are bounded local policies, not byte parity with a host resize codec or browser smoothing.",
                             "Prompt/widget records are inert: no caption, enhancement, correction, unzoom, segmentation or background-removal model ran.",
                             "These are final-array and source-mask audits, not complete host UI stale/cancel behaviour."])


def _f08(store, out, r, a):
    r["routine_order"].append("compare virtual-view and radius dialects; place explicit pixel-space supplied panel")
    shape = [{"id": "panel", "type": "rounded_rect", "x": 10, "y": 20, "w": 100, "h": 50, "radius": 8}]
    geo = layout_shapes(shape, [512, 512], [512, 128])
    web = layout_shapes(shape, [512, 512], [512, 128], profile="web-example-min-radius-v1")
    _check(r, "virtual view and radius dialects", virtual_view(320, 208) == [512, 333]
           and geo["pieces"][0]["radius"] == 4 and web["pieces"][0]["radius"] == 2)
    panel = store.put_raster(a)
    ui = render_ui(store, [{"raster": panel, "rect": [1, 1, 16, 10]}], [18, 12])
    ui_doc, ui_arrays = load_sequence(store, ui)
    r["routine_order"].append("pack explicitly supplied glyph arrays/bearings/advances; render coverage-checked text")
    glyphs = {}
    for char, pattern, rgb, bearing, advance in [
        ("A", [[0, 1, 0], [1, 0, 1], [1, 1, 1], [1, 0, 1]], [230, 210, 70], [0, -4], 4),
        ("B", [[1, 0], [1, 1], [1, 1]], [90, 220, 170], [1, -3], 4),
        (" ", [[0]], [0, 0, 0], [0, 0], 2),
    ]:
        g = np.zeros((len(pattern), len(pattern[0]), 4), np.uint8)
        selected = np.array(pattern, bool)
        g[selected] = [*rgb, 255]
        glyphs[char] = {"array": g, "bearing": bearing, "advance": advance}
    atlas = build_glyph_atlas(store, glyphs, columns=2, gap=1)
    text = render_text(store, atlas, "AB A", [18, 12], baseline=[2, 7])
    text_doc, text_arrays = load_sequence(store, text)
    expected_text = np.zeros((12, 18, 4), np.uint8)
    expected_text[3:7, 2:5] = glyphs["A"]["array"]
    expected_text[4:7, 7:9] = glyphs["B"]["array"]
    expected_text[3:7, 12:15] = glyphs["A"]["array"]
    _check(r, "independent glyph bearing/advance oracle", np.array_equal(text_arrays[0], expected_text)
           and [p["origin"] for p in text_doc["metadata"]["placements"]] == [[2, 3], [7, 4], [10, 7], [12, 3]])
    _negative(r, "missing glyph coverage rejects", lambda: render_text(store, atlas, "AC", [18, 12], baseline=[2, 7]))
    _negative(r, "UI piece outside pixel canvas rejects", lambda: render_ui(store, [{"raster": panel, "rect": [17, 1, 2, 5]}], [18, 12]))
    r["routine_order"].append("map explicit codepoints to supplied viseme-signals with distinct rational holds")
    on = np.zeros((12, 18, 4), np.uint8)
    on[9:11, 13:16] = [240, 90, 30, 255]
    off = np.zeros_like(on)
    off[10, 13:16] = [45, 50, 60, 255]
    narrow = np.zeros_like(on)
    narrow[9:11, 15] = [90, 140, 230, 255]
    visemes = {"on": on, "off": off, "narrow": narrow}
    letter_map = {"A": "on", " ": "off", "B": "narrow"}
    holds = [Fraction(1, 10), Fraction(1, 5), Fraction(1, 4), Fraction(3, 20)]
    mouth = save_viseme_timeline(store, "AA B", visemes, letter_map, holds, direction="diagnostic")
    mouth_doc, mouth_arrays = load_sequence(store, mouth)
    _check(r, "duplicate supplied signals retain individual clocks", mouth_doc["frames"][0]["raster"] == mouth_doc["frames"][1]["raster"]
           and [f["duration"] for f in mouth_doc["frames"]] == [[1, 10], [1, 5], [1, 4], [3, 20]])
    _negative(r, "unmapped lowercase codepoint rejects", lambda: save_viseme_timeline(store, "a", visemes, letter_map, [Fraction(1, 10)]))
    _negative(r, "learned UI/font/visemes explicitly unavailable", lambda: generate_asset("learned-visemes"), UnsupportedCapability)
    total = sum(holds, Fraction())
    r["routine_order"].append("hold static supplied UI/text for exact timeline; rationally compose signal/UI/text")
    ui_hold = save_sequence(store, ui_arrays, [total], metadata={**ui_doc["metadata"], "parent_sequence": ui})
    text_hold = save_sequence(store, text_arrays, [total], metadata={**text_doc["metadata"], "parent_sequence": text})
    seq = compose_sequences(store, mouth, back=ui_hold, front=text_hold)["sequence"]
    composed_doc, composed = load_sequence(store, seq)
    expected = []
    for signal in mouth_arrays:
        frame = ui_arrays[0].copy()
        selected = signal[..., 3] > 0
        frame[selected] = signal[selected]
        selected = expected_text[..., 3] > 0
        frame[selected] = expected_text[selected]
        expected.append(frame)
    _check(r, "independent opaque overlay oracle across all holds", len(composed) == 4
           and all(np.array_equal(got, want) for got, want in zip(composed, expected))
           and [f["duration"] for f in composed_doc["frames"]] == [[1, 10], [1, 5], [1, 4], [3, 20]])
    r["artifacts"].update(panel_raster=panel, ui_sequence=ui, glyph_atlas=atlas, text_sequence=text,
                          viseme_sequence=mouth, sequence=seq)
    r["inputs"].update(canvas=[18, 12], virtual_layouts={"geometric": geo, "web_min_axis": web},
                       glyphs={c: {"raster": store.put_raster(g["array"]), "bearing": g["bearing"], "advance": g["advance"]}
                               for c, g in glyphs.items()}, text="AB A", baseline=[2, 7],
                       timeline_text="AA B", letter_map=letter_map,
                       durations=[[v.numerator, v.denominator] for v in holds],
                       viseme_ids={k: store.put_raster(v) for k, v in visemes.items()})
    reopened = _exchange(store, seq, out, r)
    restored_atlas = reopened.get_json(atlas)
    _check(r, "glyph and unused-metric/viseme inputs survive closure", restored_atlas == store.get_json(atlas)
           and all(np.array_equal(reopened.get_raster(g["raster"]), glyphs[c]["array"])
                   for c, g in restored_atlas["glyphs"].items())
           and reopened.get_json(mouth)["metadata"]["letter_map"] == letter_map)
    r["limitations"].extend(["Supplied three-codepoint glyph atlas has explicit metrics; no ambient font, shaping, kerning or generated typography.",
                             "Virtual layout math and explicit pixel placement are separate; no private guide-to-raster styling is inferred.",
                             "Rectangular viseme-signals are mechanical supplied fixtures with explicit codepoint clocks, not generated mouths, phonemes, acoustic alignment or the remote vocal plan."])


_FLOWS = {"F01": _f01, "F03": _f03, "F06": _f06, "F07": _f07, "F08": _f08}


def run_flow(flow_id: str, store: Store, output: Path) -> dict:
    """Run a connected local diagnostic and return/write a JSON-safe receipt.

    output must be absent (including no dangling symlink); artifacts are staged
    and renamed only after the recipe finishes. On error, immutable candidate
    blobs may remain in the supplied Store. F01 intentionally publishes its
    diagnostic CAS head; use the orchestrator's fresh per-flow Store. Existing
    outputs are never overwritten. False oracle checks remain explicit failures.
    """
    if not isinstance(flow_id, str) or flow_id not in _FLOWS:
        raise ValidationError("Expected one of: " + ", ".join(FLOW_IDS))
    if not isinstance(store, Store):
        raise ValidationError("A caller-owned Store is required")
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValidationError("Replay output must be an absent fresh path")
    a = _fixture()
    receipt = {"flow_id": flow_id, "artifacts": {"fixture_raster": store.put_raster(a)},
               "checks": [], "inputs": {"fixture": "asymmetric-geometric-markers-v1", "shape": [5, 7, 4],
                  "dtype": "uint8", "rgba_sha256": digest(a.tobytes()), "capability": "supplied-art",
                  "coordinate_units": "integer pixels, x right/y down unless explicitly normalized/virtual",
                  "recipe_version": 1},
               "routine_order": [], "exports": {}, "reviews": {},
               "limitations": ["Local diagnostic subset only; not full vendor flow completion or art/motion acceptance.",
                               "No credentials, provider/model calls, remote templates or new REA sessions.",
                               "Review pages are generated evidence, not proof of human continuous viewing."]}
    with output_directory(output) as stage:
        _FLOWS[flow_id](store, stage, receipt, a)
        receipt["routine_order"].append("write JSON-safe receipt; preserve checks and limitations")
        (stage / "receipt.json").write_bytes(canonical_json(receipt))
    return receipt

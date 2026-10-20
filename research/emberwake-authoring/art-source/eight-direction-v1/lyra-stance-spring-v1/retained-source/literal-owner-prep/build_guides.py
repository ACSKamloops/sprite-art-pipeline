"""Render literal source-owner/anchor guides only. Never render animation art."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent
P = R.parent
SPEC = json.loads((R / "LITERAL-ROWS.json").read_text())


def rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def rows_mask(rows):
    out = np.zeros((128, 128), bool)
    for y, runs in rows.items():
        for lo, hi in runs:
            assert 0 <= lo <= hi < 128
            assert not np.any(out[int(y), lo:hi + 1])
            out[int(y), lo:hi + 1] = True
    return out


def primary_source(phase, x, y):
    if phase in (3, 4):
        z = np.load(P / f"inputs/repair03-04/maps/{phase:02}-composition.npz")
        return {"stage": "03/04 repair composition primary owner", "source_phase": int(z["source_id"][y, x]),
                "source_at": z["source_xy"][y, x].tolist(), "layer_id": int(z["layer_id"][y, x]),
                "partial_alpha_composition_possible": True}
    if phase == 5:
        value = None
        for part in ("right-rear", "left-front"):
            z = np.load(P / f"inputs/repair05/maps/05-{part}.npz")
            if z["owner"][y, x]:
                value = {"stage": "05 repaired leg primary owner", "part": part, "source_phase": int(z["source_phase"]),
                         "source_at": z["source_xy"][y, x].tolist(), "partial_alpha_composition_possible": True}
        if value is not None:
            return value
    z = np.load(P / f"inputs/upstream/maps/{phase:02}-source.npz")
    return {"stage": "coherent upper/lower visible source layer", "source_phase": int(z["source_id"][y, x]),
            "source_at": z["source_xy"][y, x].tolist(), "layer_id": int(z["layer_id"][y, x])}


def main():
    phases = []
    corrections = SPEC["same_correction"]
    for key, parts in SPEC["parts"].items():
        phase = int(key)
        a = rgba(P / f"inputs/current/{phase:02}.png")
        existing_body = np.array(Image.open(P / f"same-curve-occlusion-preview/masks/{phase:02}-body-source-owner.png").convert("L")) > 0
        union = np.zeros((128, 128), bool)
        dark = np.zeros((128, 128), bool)
        plateau = np.zeros((128, 128), bool)
        phaseparts = []
        for name, part in parts.items():
            core = rows_mask(part["rows"])
            boundary = rows_mask(part.get("fixed_boundary_rows", {}))
            assert not np.any(core & union), (phase, name, "overlapping literal part")
            assert not np.any(core & boundary), (phase, name, "core/boundary overlap")
            assert np.all(a[..., 3][core | boundary] > 0), (phase, name, "transparent source claimed as paint")
            assert not np.any(core & existing_body), (phase, name, "literal cloth claimed an existing body-owned source pixel")
            union |= core
            dark |= boundary
            columns = []
            ownplateau = np.zeros((128, 128), bool)
            for x in range(128):
                ys = np.where(core[:, x])[0]
                if len(ys) == 0:
                    continue
                first, last = int(ys.min()), int(ys.max())
                edge = [int(y) for y in np.where(boundary[:, x])[0] if last < y <= last + 1]
                terminal = max([last] + edge)
                # Conservative identity plateau is source-bound, not a Y slice
                # through a boot. Thin exposed columns stay identity for review.
                lasttwo = ys[-2:]
                ownplateau[lasttwo, x] = True
                movable_span = int(lasttwo[0]) - first
                columns.append({
                    "x": x, "first_visible_core_y": first, "last_unambiguous_core_y": last,
                    "fixed_terminal_source_cloth_or_dark_edge_y": terminal,
                    "fixed_terminal_rgba": a[terminal, x].tolist(),
                    "identity_plateau_core_source_y": [int(y) for y in lasttwo],
                    "fixed_dark_edge_source_y": edge,
                    "core_source_y": [int(y) for y in ys],
                    "unpainted_or_body_occluded_source_y_within_span": [y for y in range(first, last + 1) if not core[y, x]],
                    "first_unowned_pixel_below_terminal": {"at": [x, terminal + 1], "rgba": a[terminal + 1, x].tolist()},
                    "hypothesis_body_delta_y": corrections[phase],
                    "source_span_before_plateau": movable_span,
                    "simple_top_to_plateau_map_has_positive_span": movable_span > 0 and movable_span - corrections[phase] > 0,
                    "thin_column_needs_occlusion_or_further_root_decision": movable_span <= 0 or movable_span - corrections[phase] <= 0,
                })
            plateau |= ownplateau
            Image.fromarray(core.astype(np.uint8) * 255).save(R / f"masks/{key}-{name}-literal-core.png")
            Image.fromarray(boundary.astype(np.uint8) * 255).save(R / f"masks/{key}-{name}-fixed-dark-boundary.png")
            Image.fromarray(ownplateau.astype(np.uint8) * 255).save(R / f"masks/{key}-{name}-identity-plateau.png")
            witnesses = [{"at": [int(x), int(y)], "rgba": a[y, x].tolist(),
                          "current_source_file": f"../inputs/current/{key}.png",
                          "original_layer_chain": primary_source(phase, int(x), int(y))}
                         for y, x in np.argwhere(core)]
            phaseparts.append({"name": name, "literal_core_pixels": int(core.sum()),
                               "boundary_note": part["boundary_note"], "column_anchors": columns,
                               "source_RGBA_and_layer_witnesses": witnesses})
        for witness in SPEC["explicit_fixed_material_witnesses"]:
            if int(witness["phase"]) != phase:
                continue
            x, y = witness["at"]
            assert a[y, x].tolist() == witness["rgba"]
            assert not union[y, x], witness
        Image.fromarray(union.astype(np.uint8) * 255).save(R / f"masks/{key}-literal-core-union.png")
        phases.append({"phase": phase, "source_png_sha256": hashlib.sha256((P / f"inputs/current/{key}.png").read_bytes()).hexdigest(),
                       "parts": phaseparts})
        # Two source-only panels at exactly8x. No candidate animation paint.
        canvas = Image.new("RGBA", (1000, 330), (236, 232, 220, 255))
        draw = ImageDraw.Draw(canvas)
        axesfont = ImageFont.load_default(size=8)
        over = a.copy()
        over[union] = [25, 210, 235, 255]
        over[dark] = [250, 170, 20, 255]
        over[plateau] = [235, 30, 80, 255]
        if phase == 6:
            # Newly exposed body-owned coat area, not missing old lower paint.
            for y, xs in ((82, range(66, 71)), (83, range(67, 71))):
                for x in xs:
                    assert existing_body[y, x]
                    over[y, x] = [160, 50, 220, 255]
        for col, pixels in enumerate((a, over)):
            ox, oy = 40 + col * 492, 38
            canvas.alpha_composite(Image.fromarray(pixels).crop((38, 72, 91, 100)).resize((424, 224), Image.Resampling.NEAREST), (ox, oy))
            draw.text((ox, 5), f'{key} {"exact source" if col == 0 else "literal owners / fixed endpoints"} at8x', fill="black")
            for y in range(72, 101):
                yy = oy + (y - 72) * 8
                draw.line((ox, yy, ox + 424, yy), fill=(70, 70, 70, 90))
                if y < 100:
                    draw.text((ox - 25, yy), str(y), fill="black", font=axesfont)
            for x in range(38, 92):
                xx = ox + (x - 38) * 8
                draw.line((xx, oy, xx, oy + 224), fill=(70, 70, 70, 90))
                if x % 5 == 0:
                    draw.text((xx, 23), str(x), fill="black", font=axesfont)
        draw.text((8, 280), "Cyan: literal charcoal core. Red: identity plateau. Gold: fixed dark boundary. Purple:9 body-disocclusion pixels (06 only).", fill="black")
        draw.text((8, 298), "All brown leather/outline stays outside owners. Thin columns and00/01side flap need root review. No new frame rendered.", fill="black")
        canvas.convert("RGB").save(R / f"proof/{key}-literal-owners-anchors-8x.png")
    result = {"status": "Owner-only literal preparation; pending root material/anchor inspection", "new_animation_frames_rendered": 0,
              "new_paint_pixels_authored": 0, "source_RGB_threshold_selection": False,
              "same_absolute_curve": SPEC["same_absolute_curve"], "same_correction": corrections,
              "literal_part_owners_disjoint": True, "all_source_owned_pixels_positive_RGBA": True,
              "all_named_leather_exclusions_outside_core": True,
              "complete_boot_or_complete_garment_ownership_certified": False,
              "identity_plateau_is_proposal_not_applied_map": True, "phases": phases}
    (R / "OWNER-ANCHOR-WITNESSES.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "phases"}, indent=2))


if __name__ == "__main__":
    main()

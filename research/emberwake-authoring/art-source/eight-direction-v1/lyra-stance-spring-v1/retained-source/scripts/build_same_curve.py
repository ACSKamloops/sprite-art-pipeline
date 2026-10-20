"""One body-weight hypothesis, source-owned proximal cloth and fixed lower layers.

No model, fitting, recentering, hidden paint, source-color invention or editor package.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil

import numpy as np
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[1]
Q = P / "same-curve-occlusion-preview"
CORRECTION = [1, -1, -2, 0, 1, -1, -2, 0]


def rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def mask(path):
    return np.array(Image.open(path).convert("L")) > 0


def write(name, value):
    (Q / name).write_text(json.dumps(value, indent=2) + "\n")


def save(name, value):
    Image.fromarray(value).save(Q / name)


def source_over(back, front):
    out = back.copy()
    owned = front[..., 3] > 0
    partial = owned & (front[..., 3] < 255) & (back[..., 3] > 0)
    out[owned & ~partial] = front[owned & ~partial]
    for y, x in np.argwhere(partial):
        sr, sg, sb, sa = map(int, front[y, x])
        dr, dg, db, da = map(int, back[y, x])
        n = sa * 255 + da * (255 - sa)
        out[y, x] = [(s * sa * 255 + d * da * (255 - sa) + n // 2) // n for s, d in ((sr, dr), (sg, dg), (sb, db))] + [(n + 127) // 255]
    return out


def main():
    inputs = json.loads((P / "INPUTS.json").read_text())["records"]
    for row in inputs:
        assert hashlib.sha256((P / row["local"]).read_bytes()).hexdigest() == row["sha256"]
        assert hashlib.sha256(Path(row["source"]).read_bytes()).hexdigest() == row["sha256"]
    spec = json.loads((Q / "SOURCE-FIELD-SPEC.json").read_text())
    perphase = []
    for i, dy in enumerate(CORRECTION):
        a = rgba(P / f"inputs/current/{i:02}.png")
        up = np.load(P / f"inputs/upstream/maps/{i:02}-source.npz")
        body = np.isin(up["layer_id"], [0, 4, 5, 6]) & (a[..., 3] > 0)
        extra = []
        if i == 2:
            # Existing source02 glove's final outline/halo, omitted from the old
            # arm polygon but directly visible in this current hand. Do not pass
            # these brown texels into a charcoal trouser donor or leave a ghost.
            extra = [[x, 85] for x in range(43, 51)] + [[x, 86] for x in range(43, 50)]
            for x, y in extra:
                assert up["layer_id"][y, x] in (3, 7)
                assert a[y, x, 3] > 0
                body[y, x] = True
        # Repaired cels' actual full visible gloves/upper remain protected owners.
        if i in (3, 4):
            g = mask(P / f"inputs/repair03-04/masks/{i:02}-full-visible-gloves-owner.png")
            assert np.all(~(g & (a[..., 3] > 0)) | body)
        if i == 5:
            protected = mask(P / "inputs/repair05/masks/05-upper-hem-full-gloves-protected.png")
            assert np.all(~(body & (a[..., 3] > 0)) | protected)
        cloth_sources = []
        union = np.zeros((128, 128), bool)
        for side, part in spec["parts"].get(str(i), {}).items():
            geometric = Image.new("L", (128, 128))
            ImageDraw.Draw(geometric).polygon([tuple(v) for v in part["polygon"]], fill=255)
            rgb = a[..., :3].astype(int)
            charcoal = (rgb.max(axis=2) - rgb.min(axis=2) <= 20) & (rgb.max(axis=2) <= 130)
            # Explicit per-pose source surfaces; projected parts are disjoint.
            # The first foreground part owns the few ambiguous crotch texels.
            owner = (np.array(geometric) > 0) & charcoal & ~body & ~union & (a[..., 3] > 0)
            save(f"masks/{i:02}-{side}-source-cloth.png", owner.astype(np.uint8) * 255)
            assert not np.any(owner & body)
            assert not np.any(owner & union)
            union |= owner
            cloth_sources.append((side, part, owner))
        fixed = a.copy()
        fixed[body | union] = 0
        original_body = np.zeros_like(a)
        original_body[body] = a[body]
        moved_body = np.zeros_like(a)
        body_xy = np.full((128, 128, 2), -1, np.int16)
        body_dest = np.zeros((128, 128), bool)
        for y, x in np.argwhere(body):
            yy = int(y) + dy
            assert 0 <= yy < 128
            moved_body[yy, x] = a[y, x]
            body_xy[yy, x] = [x, y]
            body_dest[yy, x] = True
        ys, xs = np.where(body)
        assert np.array_equal(moved_body[ys + dy, xs], a[ys, xs])
        sourcebody_count = int(body.sum())
        assert int(body_dest.sum()) == sourcebody_count
        composed = fixed.copy()
        # Every mapped output has a positive visible source-owned charcoal texel.
        # Fields are column-specific: first visible seam follows the body; the
        # declared cuff anchor is fixed. Integer sampling does not alter colors.
        fields = []
        cloth_dest_union = np.zeros((128, 128), bool)
        for side, part, owner in cloth_sources:
            mapped = np.zeros_like(a)
            xy = np.full((128, 128, 2), -1, np.int16)
            dest = np.zeros((128, 128), bool)
            columns = []
            for x in range(128):
                sy_owned = np.where(owner[:, x])[0]
                if len(sy_owned) == 0:
                    continue
                top = int(sy_owned.min())
                anchor = max(int(part["cuff_anchor_y"]), int(sy_owned.max()) + 1)
                source_span = anchor - top
                target_span = anchor - (top + dy)
                assert source_span > 0 and target_span > 0
                derivative = target_span / source_span
                columns.append({"x": x, "source_hip_seam_y": top,
                                "target_hip_seam_y": top + dy, "fixed_cuff_anchor_y": anchor,
                                "source_to_target_derivative": derivative})
                for y in range(max(0, top + dy), min(127, anchor) + 1):
                    sy = int(math.floor(top + (y - top - dy) / derivative + 0.5))
                    if 0 <= sy < 128 and owner[sy, x]:
                        mapped[y, x] = a[sy, x]
                        xy[y, x] = [x, sy]
                        dest[y, x] = True
            assert all(c["source_to_target_derivative"] > 0 for c in columns)
            for y, x in np.argwhere(dest):
                sx, sy = xy[y, x]
                assert np.array_equal(mapped[y, x], a[sy, sx])
            composed = source_over(composed, mapped)
            cloth_dest_union |= dest
            save(f"layers/{i:02}-{side}-cloth.png", mapped)
            save(f"masks/{i:02}-{side}-target-cloth.png", dest.astype(np.uint8) * 255)
            np.savez_compressed(Q / f"maps/{i:02}-{side}-cloth.npz", source_xy=xy, owner=dest)
            fields.append({"side": side, "source_positive_pixels": int(owner.sum()),
                           "mapped_positive_pixels": int(dest.sum()), "columns": columns})
        # The complete current visible body paint is foreground at its new pose.
        # This allows the root-authorized natural new glove occlusion at00.
        composed = source_over(composed, moved_body)
        if dy == 0:
            # Exact original untouched cel; no compositing roundoff or art change.
            composed = a.copy()
        save(f"frames/{i:02}.png", composed)
        save(f"layers/{i:02}-fixed-lower-before.png", fixed)
        save(f"layers/{i:02}-fixed-lower-after.png", fixed)
        save(f"layers/{i:02}-body-source.png", original_body)
        save(f"layers/{i:02}-body-translated.png", moved_body)
        save(f"masks/{i:02}-body-source-owner.png", body.astype(np.uint8) * 255)
        save(f"masks/{i:02}-body-target-owner.png", body_dest.astype(np.uint8) * 255)
        save(f"masks/{i:02}-source-cloth-union.png", union.astype(np.uint8) * 255)
        np.savez_compressed(Q / f"maps/{i:02}-body.npz", source_xy=body_xy, owner=body_dest)
        # Explicit fixed-layer identity witness, including every retained visible
        # leather/cuff/sole texel. No cut, shift or replacement of that layer.
        fixedowner = fixed[..., 3] > 0
        fixedxy = np.full((128, 128, 2), -1, np.int16)
        for y, x in np.argwhere(fixedowner): fixedxy[y, x] = [x, y]
        np.savez_compressed(Q / f"maps/{i:02}-fixed-lower.npz", source_xy=fixedxy, owner=fixedowner)
        overlaps = []
        for y, x in np.argwhere(fixedowner & body_dest):
            if np.array_equal(composed[y, x], a[y, x]):
                continue
            sx, sy = map(int, body_xy[y, x])
            overlaps.append({"at": [int(x), int(y)], "fixed_source_at": [int(x), int(y)],
                             "fixed_rgba": fixed[y, x].tolist(), "foreground_source_at": [sx, sy],
                             "foreground_rgba": moved_body[y, x].tolist(), "composed_rgba": composed[y, x].tolist(),
                             "original_upstream_layer": int(up["layer_id"][y, x])})
        perphase.append({"phase": i, "body_correction_dy": dy,
                         "body_source_pixels": sourcebody_count, "body_translation_exact_before_composition": True,
                         "body_extra_glove_outline_coordinates": extra,
                         "fixed_lower_layer_RGBA_identity_exact": True,
                         "composed_rows_y94_and_below_RGBA_exact": bool(np.array_equal(a[94:], composed[94:])),
                         "complete_boot_material_ownership_certified": False,
                         "fixed_layer_body_occlusion_witnesses": overlaps, "cloth_fields": fields,
                         "changed_composed_RGBA_pixels": int(np.any(a != composed, axis=2).sum())})
    write("BODY-BOOT-CLOTH-RECEIPT.json", {
        "status": "SELF-REJECTED single composition preview: source-material ownership and visible join failures; no score or editor package",
        "absolute_body_curve_original": [0, 1, 1, 0, 0, 1, 1, 0],
        "absolute_body_curve_hypothesis": [1, 0, -1, 0, 1, 0, -1, 0], "correction": CORRECTION,
        "adjacent_absolute_body_change_pixels": [1,1,1,1,1,1,1,1],
        "root_timetable_correction": spec["root_timetable_correction"],
        "intentional_kinematic_deformation": True, "whole_pose_fit_or_recenter": False,
        "composition": ["exact retained fixed lower/boot layer", "source-owned proximal charcoal field", "rigid current visible body foreground"],
        "fixed_lower_partition_RGBA_exact": True,
        "complete_boot_geometry_and_layer_paint_certified": False,
        "boot_claim_limit": "The retained lower partition is byte-exact, but dark leather/outline texels were admitted by the neutral-color proximal owner. That partition is not a certified complete boot layer. See SELF-REJECTION.json.",
        "composed_visibility_may_change": True,
        "complete_hidden_boot_or_trouser_paint_claim": False,
        "only_current_visible_positive_source_texels": True, "model_calls": 0,
        "clock": {"hold": [9, 160], "cycle": [9, 20]}, "stage": [128, 128], "pivot": [64, 112],
        "phases": perphase,
    })
    # Native/84 full8 comparison with fixed registration and contrasting grounds.
    for size, label in ((128, "native"), (84, "84")):
        for ground, bg in (("light", (236, 232, 220, 255)), ("dark", (29, 34, 43, 255))):
            canvas = Image.new("RGBA", (8 * size, 2 * (size + 20)), bg)
            draw = ImageDraw.Draw(canvas)
            fg = "#101010" if ground == "light" else "#eeeeee"
            for row in range(2):
                for i in range(8):
                    file = P / f"inputs/current/{i:02}.png" if row == 0 else Q / f"frames/{i:02}.png"
                    im = Image.open(file).convert("RGBA").resize((size, size), Image.Resampling.NEAREST)
                    canvas.alpha_composite(im, (i * size, row * (size + 20) + 20))
                    draw.text((i * size + 3, row * (size + 20) + 3), f'{"current" if row == 0 else "curve"} {i:02}', fill=fg)
            canvas.convert("RGB").save(Q / f"proof/full8-{label}-{ground}.png")
    canvas = Image.new("RGBA", (4 * 360, 2 * 280), (236, 232, 220, 255))
    draw = ImageDraw.Draw(canvas)
    for col, i in enumerate((0, 2, 4, 6)):
        for row in range(2):
            file = P / f"inputs/current/{i:02}.png" if row == 0 else Q / f"frames/{i:02}.png"
            im = Image.open(file).convert("RGBA").crop((36, 72, 94, 116)).resize((348, 264), Image.Resampling.NEAREST)
            canvas.alpha_composite(im, (col * 360, row * 280 + 16))
            draw.text((col * 360 + 3, row * 280 + 2), f'{"current" if row == 0 else "curve"} {i:02}', fill="black")
    canvas.convert("RGB").save(Q / "proof/00-02-04-06-joint-detail.png")
    for row in inputs:
        assert hashlib.sha256((P / row["local"]).read_bytes()).hexdigest() == row["sha256"]
        assert hashlib.sha256(Path(row["source"]).read_bytes()).hexdigest() == row["sha256"]
    print(json.dumps({"status": "one samecurve preview rendered for visual join inspection", "correction": CORRECTION,
                      "fixed_lower_layers_exact": True, "body_layers_translate_exactly": True,
                      "source_fields_monotone": True, "phase_changed_pixels": [v["changed_composed_RGBA_pixels"] for v in perphase],
                      "phase_body_fixedlayer_new_overlap_counts": [len(v["fixed_layer_body_occlusion_witnesses"]) for v in perphase]}, indent=2))


if __name__ == "__main__":
    main()

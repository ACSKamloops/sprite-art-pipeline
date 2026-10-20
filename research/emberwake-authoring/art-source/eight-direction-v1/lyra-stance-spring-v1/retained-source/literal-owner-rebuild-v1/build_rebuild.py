"""One corrected samecurve rebuild from inspected literal owners.

Reads local source PNGs and literal row data; no RGB segmentation/model/editor.
"""
from pathlib import Path
import hashlib
import json
import math

import numpy as np
from PIL import Image, ImageDraw

Q = Path(__file__).resolve().parent
P = Q.parent
R = P / "literal-owner-prep"
SPEC = json.loads((R / "LITERAL-ROWS.json").read_text())
CORR = SPEC["same_correction"]


def a(path):
    return np.array(Image.open(path).convert("RGBA"))


def m(path):
    return np.array(Image.open(path).convert("L")) > 0


def save(name, image):
    Image.fromarray(image).save(Q / name)


def j(name, data):
    (Q / name).write_text(json.dumps(data, indent=2) + "\n")


def over(back, front):
    out = back.copy()
    pos = front[..., 3] > 0
    partial = pos & (front[..., 3] < 255) & (back[..., 3] > 0)
    out[pos & ~partial] = front[pos & ~partial]
    for y, x in np.argwhere(partial):
        sr, sg, sb, sa = map(int, front[y, x])
        dr, dg, db, da = map(int, back[y, x])
        n = sa * 255 + da * (255 - sa)
        out[y, x] = [(s * sa * 255 + d * da * (255 - sa) + n // 2) // n for s, d in ((sr, dr), (sg, dg), (sb, db))] + [(n + 127) // 255]
    return out


def main():
    hashes = json.loads((P / "INPUTS.json").read_text())["records"]
    for row in hashes:
        assert hashlib.sha256((P / row["local"]).read_bytes()).hexdigest() == row["sha256"]
    perphase = []
    underpaint_journal = []
    all_witnesses = list(SPEC["explicit_fixed_material_witnesses"])
    all_witnesses += [{"phase": "00", "at": [54, 85], "rgba": [18, 12, 9, 255], "material": "ambiguous dark edge; fixed by root"}]
    # Explicitly new nine-pixel shaded undercoat, only at actual body disocclusion.
    # Colors are measured same-view charcoal swatches, not inferred hidden paint.
    patch_recipe = [
        ([66, 82], [64, 84]), ([67, 82], [63, 84]), ([68, 82], [62, 84]),
        ([69, 82], [63, 84]), ([70, 82], [64, 84]),
        ([67, 83], [64, 84]), ([68, 83], [63, 84]),
        ([69, 83], [62, 85]), ([70, 83], [64, 84]),
    ]
    for phase, dy in enumerate(CORR):
        src = a(P / f"inputs/current/{phase:02}.png")
        body = m(P / f"same-curve-occlusion-preview/masks/{phase:02}-body-source-owner.png")
        rigid_body = np.zeros_like(src)
        body_xy = np.full((128, 128, 2), -1, np.int16)
        for y, x in np.argwhere(body):
            rigid_body[y + dy, x] = src[y, x]
            body_xy[y + dy, x] = [x, y]
        sy, sx = np.where(body)
        assert np.array_equal(rigid_body[sy + dy, sx], src[sy, sx])
        perparts = []
        mutable_union = np.zeros((128, 128), bool)
        full_core_union = np.zeros((128, 128), bool)
        cloth_layers = []
        for name, part in SPEC["parts"].get(f"{phase:02}", {}).items():
            core = m(R / f"masks/{phase:02}-{name}-literal-core.png")
            if phase == 0:
                assert src[85, 54].tolist() == [18, 12, 9, 255]
                core[85, 54] = False
            boundary = m(R / f"masks/{phase:02}-{name}-fixed-dark-boundary.png")
            assert not np.any(core & body), (phase, name, "body/cloth ownership overlap")
            assert not np.any(core & full_core_union), (phase, name, "clothpart overlap")
            assert not np.any(core & boundary)
            full_core_union |= core
            mutable = np.zeros((128, 128), bool)
            painted = np.zeros_like(src)
            xy = np.full((128, 128, 2), -1, np.int16)
            owner = np.zeros((128, 128), bool)
            columns = []
            for x in range(128):
                ys = np.where(core[:, x])[0]
                if len(ys) == 0:
                    continue
                first = int(ys.min())
                plateau_ys = ys[-2:]
                plateau_start = int(plateau_ys[0])
                span = plateau_start - first
                active = span > 0 and span - dy > 0
                # Source cloth attached to the coat follows it rigidly first;
                # only the interval down to the real source cuff then deforms.
                proximal_end = min(85, plateau_start - max(dy, 0) - 1)
                if proximal_end < first:
                    active = False
                if active:
                    source_span = plateau_start - proximal_end
                    target_span = plateau_start - proximal_end - dy
                    slope = target_span / source_span
                    assert source_span > 0 and target_span > 0 and slope > 0
                    mutable[:, x] = core[:, x] & (np.arange(128) < plateau_start)
                    for y in range(max(0, first + dy), plateau_start):
                        if y <= proximal_end + dy:
                            source_y = y - dy
                        else:
                            source_y = int(math.floor(proximal_end + (y - proximal_end - dy) / slope + 0.5))
                        if 0 <= source_y < 128 and core[source_y, x]:
                            painted[y, x] = src[source_y, x]
                            xy[y, x] = [x, source_y]
                            owner[y, x] = True
                else:
                    slope = None
                columns.append({"x": x, "first_visible_source_y": first,
                                "terminal_core_y": int(ys.max()),
                                "fixed_identity_plateau_source_y": [int(y) for y in plateau_ys],
                                "proximal_rigid_source_end_y": proximal_end if active else None,
                                "transition_source_to_target_derivative": slope,
                                "thin_column_stays_identity": not active,
                                "rigid_body_delta_y": dy})
            assert not np.any(mutable & boundary)
            assert not np.any(mutable & mutable_union)
            mutable_union |= mutable
            for y, x in np.argwhere(owner):
                xx, yy = xy[y, x]
                assert core[yy, xx] and np.array_equal(painted[y, x], src[yy, xx])
            cloth_layers.append(painted)
            save(f"masks/{phase:02}-{name}-literal-source-core.png", core.astype(np.uint8) * 255)
            save(f"masks/{phase:02}-{name}-mutable-source-owner.png", mutable.astype(np.uint8) * 255)
            save(f"masks/{phase:02}-{name}-target-owner.png", owner.astype(np.uint8) * 255)
            save(f"layers/{phase:02}-{name}-mapped-cloth.png", painted)
            np.savez_compressed(Q / f"maps/{phase:02}-{name}.npz", source_xy=xy, owner=owner)
            perparts.append({"name": name, "source_core_pixels": int(core.sum()),
                             "mutable_source_pixels": int(mutable.sum()), "target_pixels": int(owner.sum()),
                             "columns": columns})
        fixed = src.copy()
        fixed[body | mutable_union] = 0
        authored = np.zeros_like(src)
        if phase == 6:
            for target, donor in patch_recipe:
                x, y = target
                xx, yy = donor
                assert body[y, x] and fixed[y, x, 3] == 0
                assert full_core_union[yy, xx]
                authored[y, x] = src[yy, xx]
                underpaint_journal.append({"at": target, "new_rgba": src[yy, xx].tolist(),
                                          "source_phase": 6, "source_at": donor,
                                          "previous_source_visibility": "coat/body only; no recovered hidden charcoal",
                                          "authoring": "Explicit new shaded charcoal undercoat coverage"})
        composed_no_patch = fixed.copy()
        for layer in cloth_layers:
            composed_no_patch = over(composed_no_patch, layer)
        composed_no_patch = over(composed_no_patch, rigid_body)
        if phase == 6:
            assert all(composed_no_patch[y, x, 3] == 0 for (x, y), donor in patch_recipe)
        composed = over(authored, fixed)
        for layer in cloth_layers:
            composed = over(composed, layer)
        composed = over(composed, rigid_body)
        if dy == 0:
            assert np.array_equal(composed, src)
        assert np.array_equal(composed[94:], src[94:])
        # Verify material exclusions before composition. Foreground occlusion is
        # explicit and never represented as a changed boot-source layer.
        checked = []
        for witness in all_witnesses:
            if int(witness["phase"]) != phase:
                continue
            x, y = witness["at"]
            assert not body[y, x] and not mutable_union[y, x]
            assert np.array_equal(fixed[y, x], src[y, x])
            checked.append({**witness, "fixed_layer_RGBA_exact": True,
                            "composed_RGBA": composed[y, x].tolist()})
        overlaps = []
        for y, x in np.argwhere((fixed[..., 3] > 0) & (rigid_body[..., 3] > 0)):
            if np.array_equal(composed[y, x], src[y, x]):
                continue
            xx, yy = map(int, body_xy[y, x])
            overlaps.append({"at": [int(x), int(y)], "fixed_source_rgba": fixed[y, x].tolist(),
                             "foreground_source_at": [xx, yy], "foreground_rgba": src[yy, xx].tolist(),
                             "composed_rgba": composed[y, x].tolist()})
        newly_clear = [{"at": [int(x), int(y)], "before_rgba": src[y, x].tolist(),
                        "source_owner": "body" if body[y, x] else "mutable_charcoal" if mutable_union[y, x] else "fixed_lower"}
                       for y, x in np.argwhere((src[..., 3] >= 128) & (composed[..., 3] == 0) & (np.indices((128,128))[0] >= 77))]
        # All source and destination ownership fields stay explicit.
        fixed_xy = np.full((128, 128, 2), -1, np.int16)
        for y, x in np.argwhere(fixed[..., 3] > 0): fixed_xy[y, x] = [x, y]
        np.savez_compressed(Q / f"maps/{phase:02}-fixed-lower.npz", source_xy=fixed_xy, owner=fixed[..., 3] > 0)
        np.savez_compressed(Q / f"maps/{phase:02}-body.npz", source_xy=body_xy, owner=rigid_body[..., 3] > 0)
        save(f"masks/{phase:02}-body-source-owner.png", body.astype(np.uint8) * 255)
        save(f"masks/{phase:02}-mutable-charcoal-union.png", mutable_union.astype(np.uint8) * 255)
        save(f"layers/{phase:02}-fixed-lower.png", fixed)
        save(f"layers/{phase:02}-body-rigid.png", rigid_body)
        save(f"layers/{phase:02}-new-authored-undercoat.png", authored)
        save(f"frames/{phase:02}.png", composed)
        save(f"masks/{phase:02}-actual-composed-change.png", np.any(src != composed, axis=2).astype(np.uint8) * 255)
        perphase.append({"phase": phase, "body_delta_y": dy, "body_layer_rigid_RGBA_exact_before_composition": True,
                         "body_cloth_owner_overlap": 0, "cloth_parts_disjoint": True,
                         "retained_fixed_lower_layer_RGBA_identity_exact": True,
                         "composed_rows_y94_and_below_RGBA_exact": True,
                         "named_material_exclusions": checked, "new_body_over_fixed_layer_occlusions": overlaps,
                         "new_alpha0_pixels_after_undercoat_y77_and_below": newly_clear,
                         "parts": perparts})
    j("UNDERCOAT-LITERAL-JOURNAL.json", {"kind": "Explicitly new authored9pixel charcoal undercoat, not recovered hidden source anatomy",
                                        "phase": 6, "source_cel_sha256": hashlib.sha256((P / "inputs/current/06.png").read_bytes()).hexdigest(),
                                        "depth_order": "Behind retained lower/boot layer, mapped charcoal and rigid body",
                                        "new_coverage_pixels": 9, "edits": underpaint_journal})
    assert len(underpaint_journal) == 9
    failure = json.loads((P / "same-curve-occlusion-preview/JOIN-REJECTION-WITNESSES.json").read_text())
    loss_checks = []
    for region in failure["findings"]:
        phase = region["phase"]
        frame = a(Q / f"frames/{phase:02}.png")
        for item in region["new_hole_coordinates"]:
            x, y = item["at"]
            is_undercoat = phase == 6 and [x, y] in [target for target, donor in patch_recipe]
            loss_checks.append({"phase": phase, "at": [x, y], "old_failure_source_owner": item["source_owner_before"],
                                "coverage_positive_now": bool(frame[y, x, 3] > 0),
                                "explicit_new_undercoat": is_undercoat, "current_rgba": frame[y, x].tolist()})
    j("REBUILD-RECEIPT.json", {"status": "One corrected literal-owner rebuild; pending root visual inspection; no art score/editor package",
                               "absolute_body_curve": SPEC["same_absolute_curve"], "correction": CORR,
                               "clock": {"hold": [9,160], "cycle": [9,20]},
                               "source_mask_selection": "Literal row owners inspected by root; no RGB threshold",
                               "specific_fixed_override": {"phase":0,"at":[54,85]},
                               "composition": ["9new authored charcoal undercoat pixels at06 only", "identity retained lower/boot/outline paint", "positive mapped literal charcoal", "rigid current body foreground"],
                               "boot_and_garment_claim": "Known brown/cuff/outline and all paint outside inspected mutable core remain at identity in retained layer; complete hidden boot/garment masters are not claimed. New foreground body occlusion is ledgered separately.",
                               "fixed_unknown_00_01_sideflap": True, "new_undercoat_pixel_count":9,
                               "old_failure_hole_checks": loss_checks, "phases": perphase,
                               "model_calls":0,"canonical_writes":0,"editor_package_created":False,"score":None})
    for size, label in ((128,"native"),(84,"84")):
        for ground, bg in (("light",(236,232,220,255)),("dark",(29,34,43,255))):
            canvas=Image.new("RGBA",(8*size,2*(size+20)),bg);draw=ImageDraw.Draw(canvas)
            for row in range(2):
                for phase in range(8):
                    file=P/f"inputs/current/{phase:02}.png" if row==0 else Q/f"frames/{phase:02}.png"
                    im=Image.open(file).convert("RGBA").resize((size,size),Image.Resampling.NEAREST)
                    canvas.alpha_composite(im,(phase*size,row*(size+20)+20));draw.text((phase*size+3,row*(size+20)+3),f'{"current"if row==0 else"literal"} {phase:02}',fill="black"if ground=="light"else"white")
            canvas.convert("RGB").save(Q/f"proof/full8-{label}-{ground}.png")
    canvas=Image.new("RGBA",(6*300,2*240),(236,232,220,255));draw=ImageDraw.Draw(canvas)
    for col,phase in enumerate((0,1,2,4,5,6)):
        for row in range(2):
            file=P/f"inputs/current/{phase:02}.png"if row==0 else Q/f"frames/{phase:02}.png"
            im=Image.open(file).convert("RGBA").crop((36,72,94,116)).resize((290,220),Image.Resampling.NEAREST)
            canvas.alpha_composite(im,(col*300,row*240+18));draw.text((col*300+3,row*240+3),f'{"current"if row==0 else"literal"} {phase:02}',fill="black")
    canvas.convert("RGB").save(Q/"proof/six-joints-before-after.png")
    print(json.dumps({"status":"one literal-source rebuild rendered", "body_curve":SPEC["same_absolute_curve"],
                      "new_undercoat_pixels":9,"prior_failure_holes_positive_now":sum(v["coverage_positive_now"]for v in loss_checks),
                      "prior_failure_hole_count":len(loss_checks),
                      "residual_new_clear_counts_y77plus":[len(v["new_alpha0_pixels_after_undercoat_y77_and_below"])for v in perphase]},indent=2))


if __name__ == "__main__": main()

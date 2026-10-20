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
EXTRA = json.loads((Q / "ADDITIONAL29-UNDERCOAT-RECIPE.json").read_text())
SCOPE = json.loads((P / "waist-completion-scope-prep/SCOPE-AND-SOURCE-LAYER-WITNESSES.json").read_text())


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
    previous9_recipe = [
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
                top_pin = phase == 4 and x in (54, 79)
                if active:
                    source_span = plateau_start - proximal_end
                    target_span = plateau_start - proximal_end - dy
                    slope = target_span / source_span
                    assert source_span > 0 and target_span > 0 and slope > 0
                    mutable[:, x] = core[:, x] & (np.arange(128) < plateau_start)
                    if top_pin:
                        assert first == 84
                        mutable[first, x] = False
                        # Keep the actual old top source texel. A short column
                        # has only a half-pixel interior correction before its
                        # already-fixed cuff; both source segments stay positive.
                        pin_middle = min(max(proximal_end, first + 1), plateau_start - 1)
                        middle_delta = min(float(dy), (plateau_start - pin_middle) / 2)
                        middle_target = pin_middle + middle_delta
                        pin_slope1 = (middle_target - first) / (pin_middle - first)
                        pin_slope2 = (plateau_start - middle_target) / (plateau_start - pin_middle)
                        assert pin_slope1 > 0 and pin_slope2 > 0
                    for y in range(max(0, first if top_pin else first + dy), plateau_start):
                        if top_pin:
                            if y <= middle_target:
                                source_y = int(math.floor(first + (y - first) / pin_slope1 + 0.5))
                            else:
                                source_y = int(math.floor(pin_middle + (y - middle_target) / pin_slope2 + 0.5))
                        elif y <= proximal_end + dy:
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
                                "literal_source_top_pin": [x, first] if top_pin else None,
                                "top_pin_monotone_segment_slopes": [pin_slope1, pin_slope2] if top_pin and active else None,
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
        patch_recipe = (previous9_recipe if phase == 6 else []) + EXTRA["parts"].get(str(phase), [])
        if patch_recipe:
            source_upstream = np.load(P / f"inputs/upstream/maps/{phase:02}-source.npz")
            for target, donor in patch_recipe:
                x, y = target
                xx, yy = donor
                assert body[y, x] and fixed[y, x, 3] == 0
                assert full_core_union[yy, xx]
                assert int(source_upstream["layer_id"][y, x]) == 0
                authored[y, x] = src[yy, xx]
                underpaint_journal.append({"at": target, "new_rgba": src[yy, xx].tolist(),
                                          "phase": phase, "source_phase": phase, "source_at": donor,
                                          "source_body_original_rgba": src[y, x].tolist(),
                                          "source_body_original_role": "torso/coat/hem layer0",
                                          "original_body_primary_source_at": source_upstream["source_xy"][y, x].tolist(),
                                          "previous_source_visibility": "coat/body only; no recovered hidden charcoal",
                                          "authoring": "Explicit new shaded charcoal undercoat coverage"})
        composed_no_patch = fixed.copy()
        for layer in cloth_layers:
            composed_no_patch = over(composed_no_patch, layer)
        composed_no_patch = over(composed_no_patch, rigid_body)
        if patch_recipe:
            assert all(composed_no_patch[y, x, 3] == 0 for (x, y), donor in patch_recipe)
        composed = over(authored, fixed)
        for layer in cloth_layers:
            composed = over(composed, layer)
        composed = over(composed, rigid_body)
        if dy == 0:
            assert np.array_equal(composed, src)
        assert np.array_equal(composed[94:], src[94:])
        if phase == 4:
            assert all(np.array_equal(composed[84, x], src[84, x]) for x in (54, 79))
        partial = a(P / f"literal-owner-rebuild-v1/frames/{phase:02}.png")
        changed_from_partial = [[int(x), int(y)] for y, x in np.argwhere(np.any(partial != composed, axis=2))]
        expected_new = SCOPE["exact_proposed_new_coverage"].get(str(phase), [])
        if phase == 4:
            assert all(x in (54,79) for x, y in changed_from_partial)
        else:
            assert sorted(changed_from_partial) == sorted(expected_new)
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
                         "changed_from_frozen_partial_coordinates": changed_from_partial,
                         "parts": perparts})
    j("UNDERCOAT-LITERAL-JOURNAL.json", {"kind": "Explicitly new authored38pixel charcoal undercoat across01/02/05/06, not recovered hidden source anatomy",
                                        "depth_order": "Behind retained lower/boot layer, mapped charcoal and rigid body",
                                        "new_coverage_pixels": 38, "edits": underpaint_journal})
    assert len(underpaint_journal) == 38
    failure = json.loads((P / "same-curve-occlusion-preview/JOIN-REJECTION-WITNESSES.json").read_text())
    loss_checks = []
    for region in failure["findings"]:
        phase = region["phase"]
        frame = a(Q / f"frames/{phase:02}.png")
        for item in region["new_hole_coordinates"]:
            x, y = item["at"]
            is_undercoat = any(item["phase"] == phase and item["at"] == [x,y] for item in underpaint_journal)
            loss_checks.append({"phase": phase, "at": [x, y], "old_failure_source_owner": item["source_owner_before"],
                                "coverage_positive_now": bool(frame[y, x, 3] > 0),
                                "explicit_new_undercoat": is_undercoat, "current_rgba": frame[y, x].tolist()})
    j("REBUILD-RECEIPT.json", {"status": "One bounded29pixelcoat-only completion plus2sourcefieldtop pins; pending root visual inspection; no art score/editor package",
                               "absolute_body_curve": SPEC["same_absolute_curve"], "correction": CORR,
                               "clock": {"hold": [9,160], "cycle": [9,20]},
                               "source_mask_selection": "Literal row owners inspected by root; no RGB threshold",
                               "specific_fixed_override": {"phase":0,"at":[54,85]},
                               "composition": ["38new authored charcoal undercoat pixels across01/02/05/06", "identity retained lower/boot/outline paint", "positive mapped literal charcoal", "rigid current body foreground"],
                               "boot_and_garment_claim": "Known brown/cuff/outline and all paint outside inspected mutable core remain at identity in retained layer; complete hidden boot/garment masters are not claimed. New foreground body occlusion is ledgered separately.",
                               "fixed_unknown_00_01_sideflap": True, "new_undercoat_pixel_count":38,
                               "additional_new_coverage_over_frozen_partial":29,
                               "known_lower_mapping_loss_fixed_by_source_top_pins": [[54,84],[79,84]],
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
                      "new_undercoat_pixels":38,"prior_failure_holes_positive_now":sum(v["coverage_positive_now"]for v in loss_checks),
                      "prior_failure_hole_count":len(loss_checks),
                      "residual_new_clear_counts_y77plus":[len(v["new_alpha0_pixels_after_undercoat_y77_and_below"])for v in perphase]},indent=2))


if __name__ == "__main__": main()

from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import json
import hashlib

P = Path(__file__).resolve().parent
OLD = P / "literal-owner-rebuild-v1"
Q = P / "waist-completion-scope-prep"
Q.mkdir(exist_ok=True)
(Q / "proof").mkdir(exist_ok=True)
CHOSEN = {
    1: [[54, 83]] + [[x, 83] for x in range(74, 79)],
    2: [[x, y] for y in (82, 83) for x in (64, 65)],
    5: [[71, 82]] + [[x, 83] for x in range(64, 71)],
    6: [[71, 81], [72, 81], [63, 82], [64, 82], [65, 82], [71, 82], [72, 82],
        [63, 83], [64, 83], [65, 83], [66, 83]],
}


def rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


receipt = json.loads((OLD / "REBUILD-RECEIPT.json").read_text())
checks, clearance = [], []
for phase in receipt["phases"]:
    i = phase["phase"]
    source = rgba(P / f"inputs/current/{i:02}.png")
    now = rgba(OLD / f"frames/{i:02}.png")
    fixed = rgba(OLD / f"layers/{i:02}-fixed-lower.png")
    moved = rgba(OLD / f"layers/{i:02}-body-rigid.png")
    authored = rgba(OLD / f"layers/{i:02}-new-authored-undercoat.png")
    original_body = rgba(P / f"same-curve-occlusion-preview/layers/{i:02}-body-source.png")
    source_map = np.load(P / f"inputs/upstream/maps/{i:02}-source.npz")
    cloth = [rgba(f) for f in (OLD / "layers").glob(f"{i:02}-*-mapped-cloth.png")]
    for item in phase["new_alpha0_pixels_after_undercoat_y77_and_below"]:
        x, y = item["at"]
        layer = int(source_map["layer_id"][y, x])
        row = {
            "phase": i, "at": [x, y], "original_visible_rgba": source[y, x].tolist(),
            "original_body_layer_rgba": original_body[y, x].tolist(),
            "original_source_role": {0: "torso/coat/hem", 4: "leftarm/glove", 5: "rightarm/glove", 6: "arm socket"}.get(layer, "existinglower"),
            "original_layer_id": layer, "original_primary_source_id": int(source_map["source_id"][y, x]),
            "original_primary_source_at": source_map["source_xy"][y, x].tolist(),
            "retained_lower_at_target_rgba": fixed[y, x].tolist(),
            "all_mapped_lower_at_target_rgba": [c[y, x].tolist() for c in cloth],
            "moved_body_at_target_rgba": moved[y, x].tolist(),
            "existing_authored_at_target_rgba": authored[y, x].tolist(),
            "current_composed_rgba": now[y, x].tolist(),
        }
        if [x, y] in CHOSEN.get(i, []):
            assert 52 <= x <= 81 and 81 <= y <= 86 and layer == 0
            assert np.array_equal(original_body[y, x], source[y, x]) and source[y, x, 3] > 0
            assert fixed[y, x, 3] == moved[y, x, 3] == authored[y, x, 3] == now[y, x, 3] == 0
            assert all(c[y, x, 3] == 0 for c in cloth)
            row["scope"] = "Proposed explicitly new charcoal undercoat after coat-only disocclusion; no existinglower loss"
            checks.append(row)
        else:
            row["scope"] = "Excluded from newpaint: glove/arm clearance, outer silhouette, or existinglower mapping loss"
            clearance.append(row)
assert len(checks) == 29
result = {
    "status": "Count and source-layer proof BEFORE any new completion paint",
    "additional_undercoat_pixel_count": 29, "perphase_counts": {str(i): len(v) for i, v in CHOSEN.items()},
    "exact_proposed_new_coverage": CHOSEN, "true_torsohem_disocclusion_preconditions": checks,
    "excluded_residuals": clearance,
    "existinglower_mapping_loss_to_correct_by_field_notpaint": [
        {"phase": 4, "at": [54, 84], "proposal": "Pin existing first sourcecloth texel at identity; positive monotone piecewise field below it; no newpaint"},
        {"phase": 4, "at": [79, 84], "proposal": "Same exact existinglower top-anchor pin; no newpaint"},
    ],
    "existing06_authored_pixel_count": 9, "total_authored_newcoverage_if_approved": 38,
    "no_glove_skin_hair_ghostfill": True, "no_completion_pixels_authored_yet": True,
}
(Q / "SCOPE-AND-SOURCE-LAYER-WITNESSES.json").write_text(json.dumps(result, indent=2) + "\n")
canvas = Image.new("RGBA", (4 * 336, 3 * 180), (236, 232, 220, 255))
draw = ImageDraw.Draw(canvas)
for col, i in enumerate((1, 2, 5, 6)):
    source = rgba(P / f"inputs/current/{i:02}.png")
    now = rgba(OLD / f"frames/{i:02}.png")
    mark = now.copy()
    for x, y in CHOSEN[i]:
        mark[y, x] = [30, 220, 100, 255]
    for row, (label, pixels) in enumerate((("current coat source", source), ("partial rebuild gaps", now), ("green=proposed newcoverage", mark))):
        im = Image.fromarray(pixels).crop((48, 77, 88, 95)).resize((320, 144), Image.Resampling.NEAREST)
        canvas.alpha_composite(im, (col * 336, row * 180 + 20))
        draw.text((col * 336 + 4, row * 180 + 4), f"{i:02} {label}", fill="black")
canvas.convert("RGB").save(Q / "proof/29-coat-only-exposure-scope-8x.png")
files = sorted(f for f in OLD.rglob("*") if f.is_file() and f.name != "FROZEN-SHA256SUMS")
(OLD / "FROZEN-SHA256SUMS").write_text("".join(hashlib.sha256(f.read_bytes()).hexdigest() + "  " + str(f.relative_to(OLD)) + "\n" for f in files))
print(json.dumps({key: value for key, value in result.items() if key not in ("true_torsohem_disocclusion_preconditions", "excluded_residuals")}, indent=2))

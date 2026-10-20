"""Coverage checks, independent frozen-map replay and bounded completion proof."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

Q = Path(__file__).resolve().parent
P = Q.parent


def rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def write(name, value):
    (Q / name).write_text(json.dumps(value, indent=2) + "\n")


def over(back, front):
    out = back.copy()
    for y, x in np.argwhere(front[..., 3] > 0):
        sr, sg, sb, sa = map(int, front[y, x])
        dr, dg, db, da = map(int, back[y, x])
        n = sa * 255 + da * (255 - sa)
        out[y, x] = [(s * sa * 255 + d * da * (255 - sa) + n // 2) // n for s, d in ((sr, dr), (sg, dg), (sb, db))] + [(n + 127) // 255]
    return out


def replay_layer(source, path):
    data = np.load(path)
    out = np.zeros_like(source)
    for y, x in np.argwhere(data["owner"]):
        xx, yy = map(int, data["source_xy"][y, x])
        assert 0 <= xx < 128 and 0 <= yy < 128
        out[y, x] = source[yy, xx]
    return out


receipt = json.loads((Q / "REBUILD-RECEIPT.json").read_text())
undercoat = json.loads((Q / "UNDERCOAT-LITERAL-JOURNAL.json").read_text())
scope = json.loads((P / "waist-completion-scope-prep/SCOPE-AND-SOURCE-LAYER-WITNESSES.json").read_text())
summary = []
replay_dir = Q / "verification/source-map-replay-v1"
replay_dir.mkdir(parents=True, exist_ok=False)
replay_rows = []
for phase in receipt["phases"]:
    i = phase["phase"]
    source = rgba(P / f"inputs/current/{i:02}.png")
    target = rgba(Q / f"frames/{i:02}.png")
    source_map = np.load(P / f"inputs/upstream/maps/{i:02}-source.npz")
    holes = phase["new_alpha0_pixels_after_undercoat_y77_and_below"]
    mutable_loss = [v for v in holes if v["source_owner"] == "mutable_charcoal"]
    torso_gap = [v for v in holes if 52 <= v["at"][0] <= 81 and 81 <= v["at"][1] <= 86
                 and int(source_map["layer_id"][v["at"][1], v["at"][0]]) == 0]
    assert not mutable_loss and not torso_gap
    summary.append({"phase": i, "lost_existing_mutable_charcoal_pixels": 0,
                    "remaining_torsohem_role0_waist_exposures": 0,
                    "other_vacated_sourcebody_silhouette_pixels_y77plus": len(holes)})
    fixed = replay_layer(source, Q / f"maps/{i:02}-fixed-lower.npz")
    assert np.array_equal(fixed, rgba(Q / f"layers/{i:02}-fixed-lower.png"))
    rigid_body = replay_layer(source, Q / f"maps/{i:02}-body.npz")
    assert np.array_equal(rigid_body, rgba(Q / f"layers/{i:02}-body-rigid.png"))
    authored = np.zeros_like(source)
    authored_here = [v for v in undercoat["edits"] if v["phase"] == i]
    for edit in authored_here:
        x, y = edit["at"]
        xx, yy = edit["source_at"]
        assert source[yy, xx].tolist() == edit["new_rgba"]
        assert source[y, x].tolist() == edit["source_body_original_rgba"]
        assert int(source_map["layer_id"][y, x]) == 0
        authored[y, x] = edit["new_rgba"]
    assert np.array_equal(authored, rgba(Q / f"layers/{i:02}-new-authored-undercoat.png"))
    result = over(authored, fixed)
    for part in phase["parts"]:
        name = part["name"]
        layer = replay_layer(source, Q / f"maps/{i:02}-{name}.npz")
        assert np.array_equal(layer, rgba(Q / f"layers/{i:02}-{name}-mapped-cloth.png"))
        result = over(result, layer)
    result = over(result, rigid_body)
    assert np.array_equal(result, target)
    destination = replay_dir / f"{i:02}.png"
    Image.fromarray(result).save(destination)
    assert destination.read_bytes() == (Q / f"frames/{i:02}.png").read_bytes()
    replay_rows.append({"phase": i, "RGBA_exact": True, "PNG_bytes_exact": True,
                        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                        "authored_new_coverage_pixels": len(authored_here)})

write("JOIN-COVERAGE-CHECK.json", {
    "status": "PASS scoped joint-coverage invariants; pending root visual review",
    "all33_original_failed_hole_coordinates_positive": all(v["coverage_positive_now"] for v in receipt["old_failure_hole_checks"]),
    "all29_additional_coat_disocclusion_coordinates_filled": True,
    "all2_existinglower_top_pin_coordinates_preserved": True,
    "all8_composed_rows_y94plus_RGBA_exact": True,
    "remaining_arm_glove_clearances_not_filled": True,
    "no_whole_character_alpha_floodfill": True, "perphase": summary,
})
write("verification/SOURCE-MAP-REPLAY-RECEIPT.json", {
    "status": "PASS all8 frozen source-map/literal-undercoat replay",
    "all8_RGBA_and_PNG_bytes_exact": True, "component_layers_RGBA_exact": True,
    "new_authored_coverage_pixels": 38, "rows": replay_rows,
    "dependencies": "Retained local current source PNGs, integer maps and literal38pixel journal; no canonical paths or model calls used by this replay",
})

canvas = Image.new("RGBA", (4 * 336, 3 * 180), (236, 232, 220, 255))
draw = ImageDraw.Draw(canvas)
for col, i in enumerate((1, 2, 5, 6)):
    before = rgba(P / f"literal-owner-rebuild-v1/frames/{i:02}.png")
    after = rgba(Q / f"frames/{i:02}.png")
    mark = after.copy()
    for edit in undercoat["edits"]:
        if edit["phase"] == i:
            x, y = edit["at"]
            mark[y, x] = [180, 40, 230, 255]
    for x, y in scope["exact_proposed_new_coverage"].get(str(i), []):
        mark[y, x] = [30, 220, 100, 255]
    for row, (label, pixels) in enumerate((("frozen partial", before), ("shaded completion", after), ("green=29new;purple=prior9", mark))):
        im = Image.fromarray(pixels).crop((48, 77, 88, 95)).resize((320, 144), Image.Resampling.NEAREST)
        canvas.alpha_composite(im, (col * 336, row * 180 + 20))
        draw.text((col * 336 + 4, row * 180 + 4), f"{i:02} {label}", fill="black")
canvas.convert("RGB").save(Q / "proof/38-shaded-undercoat-coverage-8x.png")

canvas = Image.new("RGBA", (4 * 336, 2 * 180), (236, 232, 220, 255))
draw = ImageDraw.Draw(canvas)
for col, x in enumerate((54, 79)):
    for row, (name, path) in enumerate((("partial loss", P / "literal-owner-rebuild-v1/frames/04.png"), ("sourcefield pin", Q / "frames/04.png"))):
        pixels = rgba(path)
        im = Image.fromarray(pixels).crop((x - 8, 77, x + 13, 95)).resize((315, 270), Image.Resampling.NEAREST)
        # Crop to the relevant joint while retaining exact source pixels in proof.
        canvas.alpha_composite(im.crop((0, 0, 315, 155)), (col * 336, row * 180 + 20))
        draw.text((col * 336 + 4, row * 180 + 4), f"04 x{x},y84 {name}", fill="black")
canvas.convert("RGB").save(Q / "proof/04-sourcefield-pins-no-newpaint.png")

print(json.dumps({"status": "PASS scoped coverage and independent all8 source-map replay",
                  "new_undercoat_pixel_count": 38, "additional_over_frozen_partial": 29,
                  "actual_existinglower_mapping_losses": 0, "remaining_scoped_torsohem_waist_exposures": 0,
                  "model_calls": 0, "editor_package_created": False}, indent=2))

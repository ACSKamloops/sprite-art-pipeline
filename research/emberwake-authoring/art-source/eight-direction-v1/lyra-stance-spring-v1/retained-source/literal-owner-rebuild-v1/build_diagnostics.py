from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import json

Q = Path(__file__).resolve().parent
P = Q.parent
receipt = json.loads((Q / "REBUILD-RECEIPT.json").read_text())
summary = []
for phase in receipt["phases"]:
    i = phase["phase"]
    holes = phase["new_alpha0_pixels_after_undercoat_y77_and_below"]
    counts = {key: sum(v["source_owner"] == key for v in holes) for key in ("body", "mutable_charcoal", "fixed_lower")}
    waist = [v for v in holes if 52 <= v["at"][0] <= 81 and 80 <= v["at"][1] <= 86]
    summary.append({"phase": i, "all_new_clear_y77plus_count": len(holes), "before_owner_counts": counts,
                    "waist_ROI_x52_81_y80_86_new_clear": waist})
    print(i, counts, "waist", len(waist), waist)
(Q / "RESIDUAL-HOLES.json").write_text(json.dumps({
    "scope": "Exact newclear coordinates include natural vacated body silhouettes. ROI is diagnostic, not proof every hole is anatomically invalid. Waist slits require root visual review. No new paint beyond authorized9.",
    "summary": summary,
}, indent=2) + "\n")

canvas = Image.new("RGBA", (4 * 384, 3 * 190), (236, 232, 220, 255))
draw = ImageDraw.Draw(canvas)
for col, i in enumerate((1, 2, 5, 6)):
    source = np.array(Image.open(P / f"inputs/current/{i:02}.png").convert("RGBA"))
    actual = np.array(Image.open(Q / f"frames/{i:02}.png").convert("RGBA"))
    mark = actual.copy()
    holes = (source[..., 3] >= 128) & (actual[..., 3] == 0)
    change = np.any(source != actual, axis=2)
    mark[change & (actual[..., 3] > 0)] = [210, 20, 190, 255]
    mark[holes] = [250, 150, 0, 255]
    for row, (name, pixels) in enumerate((("source", source), ("literal rebuild", actual), ("magenta diff / gold newclear", mark))):
        im = Image.fromarray(pixels).crop((42, 74, 88, 94)).resize((368, 160), Image.Resampling.NEAREST)
        canvas.alpha_composite(im, (col * 384, row * 190 + 22))
        draw.text((col * 384 + 4, row * 190 + 4), f"{i:02} {name}", fill="black")
canvas.convert("RGB").save(Q / "proof/01-02-05-06-diff-newclear-8x.png")

source = np.array(Image.open(P / "inputs/current/06.png").convert("RGBA"))
actual = np.array(Image.open(Q / "frames/06.png").convert("RGBA"))
journal = json.loads((Q / "UNDERCOAT-LITERAL-JOURNAL.json").read_text())
without = actual.copy()
marked = actual.copy()
for item in journal["edits"]:
    x, y = item["at"]
    without[y, x] = 0
    marked[y, x] = [10, 220, 110, 255]
canvas = Image.new("RGBA", (4 * 280, 240), (236, 232, 220, 255))
draw = ImageDraw.Draw(canvas)
for col, (name, pixels) in enumerate((("current source coat", source), ("same rebuild before9patch", without),
                                     ("actual9 shaded undercoat", actual), ("green=new authoredcoverage", marked))):
    im = Image.fromarray(pixels).crop((57, 75, 83, 97)).resize((260, 220), Image.Resampling.NEAREST)
    canvas.alpha_composite(im, (col * 280, 20))
    draw.text((col * 280 + 3, 3), name, fill="black")
canvas.convert("RGB").save(Q / "proof/06-actual9-undercoat-source-shading.png")

#!/usr/bin/env python3
"""Inspect fixed 4x6 ImageGen candidates; no art repair or per-cel fitting."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def source_components(mask: np.ndarray) -> list[dict]:
    """Run-length 4-connected components without optional imaging dependencies."""
    parent: list[int] = []
    runs: list[tuple[int, int, int, int]] = []
    previous: list[tuple[int, int, int]] = []

    def find(label: int) -> int:
        while parent[label] != label:
            parent[label] = parent[parent[label]]
            label = parent[label]
        return label

    for y, line in enumerate(mask):
        edges = np.flatnonzero(np.diff(np.pad(line.astype(np.int8), (1, 1))))
        current = []
        for x0, x1 in zip(edges[::2].tolist(), edges[1::2].tolist()):
            label = len(parent)
            parent.append(label)
            for p0, p1, plabel in previous:
                if p0 >= x1:
                    break
                if p1 > x0:
                    parent[find(label)] = find(plabel)
            current.append((x0, x1, label))
            runs.append((y, x0, x1, label))
        previous = current
    groups = {}
    for y, x0, x1, label in runs:
        root = find(label)
        if root not in groups:
            groups[root] = {"pixels": 0, "bbox": [x0, y, x1, y + 1]}
        group = groups[root]
        group["pixels"] += x1 - x0
        b = group["bbox"]
        group["bbox"] = [min(b[0], x0), min(b[1], y), max(b[2], x1), max(b[3], y + 1)]
    return list(groups.values())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--rows", type=int, default=6)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    im = Image.open(args.raw).convert("RGBA")
    arr = np.asarray(im)
    alpha = arr[..., 3]
    components = source_components(alpha >= 32)
    bodies = [c for c in components if c["pixels"] >= 1000]
    row_measurements = []
    for row in range(args.rows):
        group = sorted((c for c in bodies if int(((c["bbox"][1] + c["bbox"][3]) / 2) * args.rows / im.height) == row), key=lambda c: c["bbox"][0])
        row_measurements.append({"row": row, "body_count": len(group), "whole_body_bboxes": [c["bbox"] for c in group], "bbox_bottoms": [c["bbox"][3] for c in group], "area32": [c["pixels"] for c in group]})
    records = []
    for index in range(4 * args.rows):
        col, row = index % 4, index // 4
        box = (round(col * im.width / 4), round(row * im.height / args.rows),
               round((col + 1) * im.width / 4), round((row + 1) * im.height / args.rows))
        cel = im.crop(box)
        bounds = Image.fromarray(np.asarray(cel)[..., 3] >= 32).getbbox()
        records.append({"cell": index, "row": row, "column": col,
                        "nominal_source_box": box, "alpha32_bbox_in_cell": bounds,
                        "alpha32_pixels": int((np.asarray(cel)[..., 3] >= 32).sum())})
    # One whole-sheet nearest transform defines every preview cel equally.
    native = im.resize((320, 80 * args.rows), Image.Resampling.NEAREST)
    native.save(args.output / "sheet-native-fixed-grid.png")
    contact = Image.new("RGBA", (1000, 264 * args.rows), (35, 40, 49, 255))
    draw = ImageDraw.Draw(contact)
    for index in range(4 * args.rows):
        col, row = index % 4, index // 4
        x, y = col * 250 + 5, row * 264 + 20
        for cy in range(0, 240, 12):
            for cx in range(0, 240, 12):
                shade = 70 if (cx // 12 + cy // 12) % 2 else 88
                draw.rectangle((x + cx, y + cy, x + cx + 11, y + cy + 11),
                               fill=(shade, shade, shade, 255))
        cel = native.crop((col * 80, row * 80, (col + 1) * 80, (row + 1) * 80))
        contact.alpha_composite(cel.resize((240, 240), Image.Resampling.NEAREST), (x, y))
        draw.text((x + 4, y - 16), str(index), fill="white")
    contact.convert("RGB").save(args.output / "contact-fixed-grid-3x.png")
    report = {"raw_path": str(args.raw.resolve()),
              "raw_sha256": hashlib.sha256(args.raw.read_bytes()).hexdigest(),
              "actual_dimensions": im.size, "mode": im.mode,
              "alpha_min": int(alpha.min()), "alpha_max": int(alpha.max()),
              "zero_alpha_pixels": int((alpha == 0).sum()),
              "partial_alpha_pixels": int(((alpha > 0) & (alpha < 255)).sum()),
              "alpha32_4connected_components": len(components),
              "alpha32_components_area_at_least_1000": len(bodies),
              "whole_body_row_measurements": row_measurements,
              "nominal_equal_grid": {"columns": 4, "rows": args.rows, "cells": 4 * args.rows},
              "preview_transform": {"whole_sheet_nearest_dimensions": [320, 80 * args.rows],
                                    "per_cell_fitting": False,
                                    "alpha_cleanup": None},
              "cells": records,
              "scope": "Mechanical inventory and fixed-grid previews only; visual review separately."}
    (args.output / "inspection.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ["raw_sha256", "actual_dimensions", "alpha_min", "alpha_max", "zero_alpha_pixels", "alpha32_components_area_at_least_1000"]}))


if __name__ == "__main__":
    main()

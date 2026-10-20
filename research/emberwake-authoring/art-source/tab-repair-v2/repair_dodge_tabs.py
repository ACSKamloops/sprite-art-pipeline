#!/usr/bin/env python3
"""Bounded Brann south-dodge waist repair using frozen same-view source pixels.

Requires Pillow. No model, network, scaling or palette changes touch the atlas.
The copied v1 helper and inputs live beside this script for portable replay.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

BASE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("frozen_tab_repair", BASE / "inputs/repair-tabs-v1.py")
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply_dodge_repairs(atlas: Image.Image, plan: dict) -> tuple[Image.Image, dict]:
    if {op["frame"] for op in plan["operations"]} != {24, 26} or len(plan["operations"]) != 2:
        raise ValueError("This revision authorizes exactly south_dodge f24/f26")
    if {spec["donor"] for spec in plan["masks"].values()} != {12}:
        raise ValueError("This revision uses only the frozen same-south-view f12 donor")
    original = atlas.convert("RGBA")
    result, receipt = HELPER.apply_tab_repairs(original, plan)
    if any(j["erased_opaque_to_zero_alpha_pixels"] for j in receipt["journal"]):
        raise ValueError("Waist repair would punch an alpha hole")
    changed_frames = []
    inventory = []
    for frame in range(original.width // 128 * (original.height // 128)):
        before = HELPER.cel(original, frame)
        after = HELPER.cel(result, frame)
        changed = before.tobytes() != after.tobytes()
        if changed:
            changed_frames.append(frame)
        inventory.append({"frame": frame, "changed": changed,
                          "source_rgba_sha256": sha(before.tobytes()),
                          "candidate_rgba_sha256": sha(after.tobytes())})
    if changed_frames != [24, 26]:
        raise AssertionError("Unexpected whole-atlas cel changes")
    receipt["schema"] = "emberwake-south-dodge-tab-repair-receipt/v2"
    receipt.pop("all_112_cel_inventory", None)
    receipt["all_cel_inventory"] = inventory
    receipt["protected_f25_entire_glove_occluded_cel_unchanged"] = True
    receipt["protected_f27_reviewed_red_tab_cel_unchanged"] = True
    receipt["protected_all_other_cels_unchanged"] = True
    receipt["donor_cel_12_unchanged"] = True
    receipt["operations_are_integer_pixel_copies"] = True
    receipt["quality_status"] = "Bounded candidate awaiting independent whole-pose/transition review; no score claimed"
    for j in receipt["journal"]:
        before = HELPER.cel(original, j["frame"])
        after = HELPER.cel(result, j["frame"])
        added = 0
        alpha_increases = 0
        alpha_decreases = 0
        for a, b in zip(before.tobytes()[3::4], after.tobytes()[3::4]):
            added += a == 0 and b > 0
            alpha_increases += b > a
            alpha_decreases += b < a
        j["new_opaque_pixels_inside_cloth_mask"] = added
        j["alpha_increases_inside_mask"] = alpha_increases
        j["alpha_decreases_inside_mask"] = alpha_decreases
    return result, receipt


def masks(before: Image.Image, after: Image.Image, receipt: dict, folder: Path) -> None:
    authorized = Image.new("L", before.size)
    changed = Image.new("L", before.size)
    for entry in receipt["source_maps"]:
        frame = entry["frame"]
        ox, oy = frame % 8 * 128, frame // 8 * 128
        local = Image.new("L", (128, 128))
        for tx, ty, donor, sx, sy in entry["map_tx_ty_donor_sx_sy"]:
            authorized.putpixel((ox + tx, oy + ty), 255)
            local.putpixel((tx, ty), 255)
        local.save(folder / f"f{frame}-authorized-mask.png")
    for channel in ImageChops.difference(before, after).split():
        changed = ImageChops.lighter(changed, channel.point(lambda p: 255 if p else 0))
    authorized.save(folder / "authorized-atlas-mask.png")
    changed.save(folder / "changed-atlas-mask.png")


def proofs(before: Image.Image, after: Image.Image, manifest: dict, folder: Path) -> None:
    background = (24, 42, 47, 255)
    for scale in [1, 2]:
        width, height = 128 * scale, 128 * scale + 24
        sheet = Image.new("RGBA", (8 * width, height), background)
        draw = ImageDraw.Draw(sheet)
        for i, frame in enumerate([24, 25, 26, 27]):
            for variant, atlas in enumerate([before, after]):
                x = (i * 2 + variant) * width
                sheet.alpha_composite(HELPER.cel(atlas, frame).resize((128 * scale, 128 * scale), Image.Resampling.NEAREST), (x, 24))
                draw.text((x + 3, 5), f"f{frame} {'BEFORE' if variant == 0 else 'AFTER'}", fill="white")
        sheet.convert("RGB").save(folder / f"south-dodge-whole-before-after-{scale}x.png")
    sheet = Image.new("RGBA", (8 * 228, 204), background)
    draw = ImageDraw.Draw(sheet)
    for i, frame in enumerate([24, 25, 26, 27]):
        for variant, atlas in enumerate([before, after]):
            x = (i * 2 + variant) * 228
            crop = HELPER.cel(atlas, frame).crop((46, 67, 84, 97)).resize((228, 180), Image.Resampling.NEAREST)
            sheet.alpha_composite(crop, (x, 24))
            draw.text((x + 3, 5), f"f{frame} {'BEFORE' if variant == 0 else 'AFTER'}", fill="white")
    sheet.convert("RGB").save(folder / "south-dodge-waist-before-after-6x.png")
    sequence = []
    for action in ["idle", "dodge", "idle"]:
        clip = manifest["animations"]["south_" + action]
        sequence.extend({"action": action, "frame": frame, "hold_seconds": float(hold)}
                        for frame, hold in zip(clip["frames"], clip["holds"]))
    (folder / "transition-sequence.json").write_text(json.dumps({"origin": "Unchanged v3 manifest; idle -> dodge -> idle", "sequence": sequence}, indent=2) + "\n")
    for speed in [1, 3]:
        frames, durations = [], []
        for step in sequence:
            pair = Image.new("RGBA", (512, 282), background)
            draw = ImageDraw.Draw(pair)
            for variant, atlas in enumerate([before, after]):
                pair.alpha_composite(HELPER.cel(atlas, step["frame"]).resize((256, 256), Image.Resampling.NEAREST), (variant * 256, 26))
                label = f"{'BEFORE' if variant == 0 else 'AFTER'} {step['action']} f{step['frame']} {step['hold_seconds'] * 1000:g}ms"
                draw.text((variant * 256 + 4, 5), label, fill="white")
            frames.append(pair)
            durations.append(round(step["hold_seconds"] * 1000 * speed))
        frames[0].save(folder / ("south-transitions-normal.apng" if speed == 1 else "south-transitions-slow-3x.apng"), save_all=True,
                       append_images=frames[1:], duration=durations, loop=0, disposal=0, blend=0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=BASE / "inputs/brann-v3-atlas.png")
    parser.add_argument("--plan", type=Path, default=BASE / "repair-plan.json")
    parser.add_argument("--manifest", type=Path, default=BASE / "inputs/brann-v3-animations.json")
    parser.add_argument("--output", type=Path, required=True, help="Fresh output directory, never an existing bank")
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output must be a fresh directory")
    source = Image.open(args.source).convert("RGBA")
    plan = json.loads(args.plan.read_text())
    candidate, receipt = apply_dodge_repairs(source, plan)
    # All input/repair validations finish before any output directory is made.
    args.output.mkdir(parents=True)
    candidate.save(args.output / "atlas.png")
    receipt["source_png_sha256"] = sha(args.source.read_bytes())
    receipt["source_matches_frozen_v3_png"] = receipt["source_png_sha256"] == plan["source_png_sha256"]
    receipt["plan_sha256"] = sha(args.plan.read_bytes())
    receipt["candidate_png_sha256"] = sha((args.output / "atlas.png").read_bytes())
    masks(source, candidate, receipt, args.output)
    proofs(source, candidate, json.loads(args.manifest.read_text()), args.output)
    (args.output / "REPAIR-RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Repaired only f24/f26: {receipt['changed_pixels']} pixels; all other cels unchanged")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Replay literal same-view waist-tab copies. No generative model or body warp.

python art-source/tab-repair-v1/repair_tabs.py \
  --source art-source/characters-v2/bake-v1/brann/atlas.png \
  --output art-source/tab-repair-v1/replay

The frozen plan binds the original target/donor cel RGBA, not the entire atlas.
This lets a caller replace only walk cels first, then apply the unchanged action
bank's tab repairs. A changed action/donor cel rejects rather than silently
rebasing the repair. A missing output directory is required for CLI replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cel(atlas: Image.Image, frame: int, columns: int = 8) -> Image.Image:
    x, y = frame % columns * 128, frame // columns * 128
    return atlas.crop((x, y, x + 128, y + 128))


def apply_tab_repairs(atlas: Image.Image, plan: dict) -> tuple[Image.Image, dict]:
    """Apply only the declared original neutral/action bank; inputs stay intact."""
    original = atlas.convert("RGBA")
    result = original.copy()
    if original.width != 1024 or original.height < 1792:
        raise ValueError("Expected 128px cels in the original eight-column layout")
    masks = plan["masks"]
    journal, source_maps = [], []
    authorized_atlas_mask = Image.new("L", original.size)
    for op in plan["operations"]:
        frame = op["frame"]
        if frame % 28 < 8:
            raise ValueError("Walk cels are outside the authorized repair")
        spec = masks[op["mask"]]
        donor = cel(original, spec["donor"])
        target = cel(original, frame)
        if sha(donor.tobytes()) != spec["donor_rgba_sha256"]:
            raise ValueError(f"Donor {spec['donor']} changed; repair requires review/rebase")
        if sha(target.tobytes()) != op["target_rgba_sha256"]:
            raise ValueError(f"Target {frame} changed; repair requires review/rebase")
        out = target.copy()
        mask = Image.new("L", (128, 128))
        dx, dy = op["offset"]
        mapping, changed, alpha_erased = [], [], 0
        for sy, x0, x1 in spec["rows_y_x0_x1"]:
            for sx in range(x0, x1):
                tx, ty = sx + dx, sy + dy
                if not (0 <= tx < 128 and 0 <= ty < 128):
                    raise ValueError("Literal tab mask escaped its cel")
                rgba = donor.getpixel((sx, sy))
                before = target.getpixel((tx, ty))
                out.putpixel((tx, ty), rgba)
                mask.putpixel((tx, ty), 255)
                mapping.append([tx, ty, spec["donor"], sx, sy])
                if rgba != before:
                    changed.append([tx, ty, list(before), list(rgba)])
                if before[3] > 0 and rgba[3] == 0:
                    alpha_erased += 1
        # Compare all four channels; getbbox on an RGBA diff can otherwise
        # ignore RGB-only changes when the alpha-difference channel is zero.
        for channel in ImageChops.difference(out, target).split():
            outside = ImageChops.multiply(channel, ImageChops.invert(mask))
            if outside.getbbox() is not None:
                raise AssertionError("Pixel changed outside literal authorized mask")
        ox, oy = frame % 8 * 128, frame // 8 * 128
        result.paste(out, (ox, oy))
        authorized_atlas_mask.paste(mask, (ox, oy))
        journal.append({"frame": frame, "donor": spec["donor"], "mask": op["mask"],
                        "offset": op["offset"], "mask_bbox": list(mask.getbbox()),
                        "authorized_pixels": len(mapping), "changed_pixels": len(changed),
                        "erased_opaque_to_zero_alpha_pixels": alpha_erased,
                        "outside_mask_unchanged": True,
                        "before_rgba_sha256": sha(target.tobytes()),
                        "after_rgba_sha256": sha(out.tobytes()),
                        "literal_changed_pixels": changed})
        source_maps.append({"frame": frame, "map_tx_ty_donor_sx_sy": mapping})
    for channel in ImageChops.difference(original, result).split():
        outside = ImageChops.multiply(channel, ImageChops.invert(authorized_atlas_mask))
        if outside.getbbox() is not None:
            raise AssertionError("Atlas changed outside authorized action-bank mask")
    walk_frames = [f for f in range(112) if f % 28 < 8]
    assert all(cel(original, f).tobytes() == cel(result, f).tobytes() for f in walk_frames)
    changed_frames = {op["frame"] for op in plan["operations"]}
    inventory = [{"frame": f, "facing": ["south", "east", "north", "west"][f // 28],
                  "local_frame": f % 28,
                  "status": "walk_excluded" if f % 28 < 8 else ("tab_repaired" if f in changed_frames else "retained_original_tab_or_occluded_pose"),
                  "source_rgba_sha256": sha(cel(original, f).tobytes()),
                  "candidate_rgba_sha256": sha(cel(result, f).tobytes())}
                 for f in range(112)]
    return result, {"schema": "emberwake-waist-tab-repair-receipt/v1",
                    "source_rgba_sha256": sha(original.tobytes()),
                    "candidate_rgba_sha256": sha(result.tobytes()),
                    "outside_all_masks_unchanged": True,
                    "walk_cels_unchanged": walk_frames,
                    "repaired_frames": sorted(changed_frames),
                    "changed_pixels": sum(j["changed_pixels"] for j in journal),
                    "journal": journal, "source_maps": source_maps,
                    "all_112_cel_inventory": inventory,
                    "quality_status": "Candidate awaiting independent before/after motion and outfit review"}


def proofs(before: Image.Image, after: Image.Image, folder: Path, manifest: dict | None = None) -> None:
    background = (31, 51, 54, 255)
    for base, view in [(0, "south"), (28, "east"), (56, "north"), (84, "west")]:
        # Paired before/after columns, all original 20 neutral/action cels.
        sheet = Image.new("RGBA", (8 * 216, 5 * 180), background)
        draw = ImageDraw.Draw(sheet)
        for i, local in enumerate(range(8, 28)):
            frame = base + local
            for variant, source in enumerate([before, after]):
                index = i * 2 + variant
                ox, oy = index % 8 * 216, index // 8 * 180
                crop = cel(source, frame).crop((46, 70, 82, 96)).resize((216, 156), Image.Resampling.NEAREST)
                sheet.alpha_composite(crop, (ox, oy + 24))
                draw.text((ox + 3, oy + 5), f"f{frame} {'BEFORE' if variant == 0 else 'AFTER'}", fill="white")
        sheet.convert("RGB").save(folder / f"{view}-waist-before-after-6x.png")
    frames = [14, 15, 16, 21, 27, 42, 43, 44, 48, 70, 71, 72, 77, 79, 83]
    whole = Image.new("RGBA", (10 * 256, 3 * 282), background)
    draw = ImageDraw.Draw(whole)
    for i, frame in enumerate(frames):
        for variant, source in enumerate([before, after]):
            index = i * 2 + variant
            ox, oy = index % 10 * 256, index // 10 * 282
            crop = cel(source, frame).resize((256, 256), Image.Resampling.NEAREST)
            whole.alpha_composite(crop, (ox, oy + 26))
            draw.text((ox + 3, oy + 5), f"f{frame} {'BEFORE' if variant == 0 else 'AFTER'}", fill="white")
    whole.convert("RGB").save(folder / "whole-body-before-after-2x.png")
    if manifest is not None:
        for view in ["south", "east", "north", "west"]:
            frames, durations = [], []
            # Every affected transition, plus holds and wrap at the original
            # action clocks. No new poses or interpolated pixels are made.
            for action in ["idle", "idle", "attack", "idle", "cast", "idle", "hurt", "idle", "dodge", "idle"]:
                clip = manifest["animations"][view + "_" + action]
                for frame, hold in zip(clip["frames"], clip["holds"]):
                    pair = Image.new("RGBA", (512, 282), background)
                    draw = ImageDraw.Draw(pair)
                    for variant, source in enumerate([before, after]):
                        pair.alpha_composite(cel(source, frame).resize((256, 256), Image.Resampling.NEAREST), (variant * 256, 26))
                        draw.text((variant * 256 + 3, 5), f"{view} {action} f{frame} {'BEFORE' if variant == 0 else 'AFTER'}", fill="white")
                    frames.append(pair)
                    durations.append(round(float(hold) * 1000))
            frames[0].save(folder / f"{view}-transitions-before-after.apng", save_all=True,
                           append_images=frames[1:], duration=durations, loop=0,
                           disposal=0, blend=0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output must be a fresh directory")
    plan_path = Path(__file__).with_name("repair-plan.json")
    plan = json.loads(plan_path.read_text())
    before = Image.open(args.source).convert("RGBA")
    result, receipt = apply_tab_repairs(before, plan)
    args.output.mkdir(parents=True)
    result.save(args.output / "atlas.png")
    manifest_path = args.source.with_name("animations.json")
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    proofs(before, result, args.output, manifest)
    if manifest is not None:
        receipt["timed_proof_manifest_sha256"] = sha(manifest_path.read_bytes())
    receipt["source_path"] = str(args.source)
    receipt["source_png_sha256"] = sha(args.source.read_bytes())
    receipt["candidate_png_sha256"] = sha((args.output / "atlas.png").read_bytes())
    receipt["plan_sha256"] = sha(plan_path.read_bytes())
    source_maps = receipt.pop("source_maps")
    (args.output / "source-maps.json").write_text(json.dumps(source_maps, indent=2) + "\n")
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"repaired_frames": receipt["repaired_frames"],
                      "changed_pixels": receipt["changed_pixels"],
                      "candidate_png_sha256": receipt["candidate_png_sha256"],
                      "outside_masks_unchanged": True, "walks_unchanged": 32}))


if __name__ == "__main__":
    main()

"""Bounded literal SE03 donor-contamination erasure. No model or editor call."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

import numpy as np
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def arr(p):
    return np.array(Image.open(p).convert("RGBA"))


def savej(name, data):
    (P / name).write_text(json.dumps(data, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-only", action="store_true", help="Replay solely from retained local inputs without probing original canonical paths")
    args = parser.parse_args()
    intake = json.loads((P / "INPUTS.json").read_text())
    for entry in intake["files"]:
        assert sha(P / entry["local"]) == entry["sha256"], entry
        if not args.local_only and Path(entry["source"]).is_file():
            assert sha(Path(entry["source"])) == entry["sha256"], entry
    before = arr(P / "inputs/current/03.png")
    donor = arr(P / "inputs/original/02.png")
    sourcekey = arr(P / "inputs/source-key02.png")
    mapping = np.load(P / "inputs/maps/03-composition.npz")
    upper = np.array(Image.open(P / "inputs/masks/03-stable-upper-hem-owner.png").convert("L")) > 0
    gloves = np.array(Image.open(P / "inputs/masks/03-full-visible-gloves-owner.png").convert("L")) > 0
    boots = np.array(Image.open(P / "inputs/ownership/03-complete-boot.png").convert("L")) > 0
    donorboots = np.array(Image.open(P / "inputs/ownership/02-complete-boot.png").convert("L")) > 0
    # Measured source glove-bottom line, then only its anti-aliased outer halo.
    # Retain x50+, y87+ where the donor leg's dark lateral contour begins.
    points = [[x, 86] for x in range(44, 51)] + [[x, y] for y in (87, 88) for x in range(45, 50)]
    edits = []
    after = before.copy()
    allowed = np.zeros((128, 128), bool)
    for x, y in points:
        sx, sy = map(int, mapping["source_xy"][y, x])
        assert mapping["source_id"][y, x] == 2
        assert mapping["layer_id"][y, x] == 2
        blended_hip = (x, y) == (50, 86)
        assert np.array_equal(before[y, x], donor[sy, sx]) or blended_hip
        assert np.array_equal(donor[sy, sx], sourcekey[sy, sx])
        assert not (upper[y, x] or gloves[y, x] or boots[y, x])
        assert not donorboots[sy, sx]
        # This last dark line texel was composited over retained hip paint.
        # Restore that measured underpaint rather than creating a new hole.
        replacement = donor[y, x].tolist() if blended_hip else [0, 0, 0, 0]
        edits.append({
            "at": [x, y], "before_rgba": before[y, x].tolist(), "after_rgba": replacement,
            "source": "inputs/original/02.png", "source_at": [sx, sy],
            "owner_before": "03 mapped left-leg layer 2; incorrectly includes original glove contour",
            "operation": "literal source hip restoration" if blended_hip else "literal erase",
            "replacement_source_at": [x, y] if blended_hip else None,
            "raw_donor_rgba": donor[sy, sx].tolist(),
        })
        after[y, x] = replacement
        allowed[y, x] = True
    assert np.array_equal(before[~allowed], after[~allowed])
    assert np.array_equal(before[upper | gloves | boots], after[upper | gloves | boots])
    assert int(np.any(before != after, axis=2).sum()) == 17
    for i in range(8):
        if i != 3:
            shutil.copy2(P / f"inputs/current/{i:02}.png", P / f"candidate/{i:02}.png")
    Image.fromarray(after).save(P / "candidate/03.png")
    Image.fromarray(allowed.astype(np.uint8) * 255).save(P / "proof/03-literal-change-mask.png")
    journal = {
        "schema": "literal-rgba-repair/v1", "kind": "compact pre-editor proof journal",
        "input": "inputs/current/03.png", "input_sha256": sha(P / "inputs/current/03.png"),
        "output": "candidate/03.png", "output_sha256": sha(P / "candidate/03.png"),
        "reason": "Remove original key02 glove bottom/halo incorrectly carried into SE03 by the mapped left-leg owner. Current full glove ends above the detached line. Retain measured hip underpaint at the one blended line texel.",
        "edits": edits,
    }
    savej("journal/03-literal-erasure.json", journal)
    # Replay and undo from the retained literal transaction, independently of inference.
    replay = before.copy()
    for edit in journal["edits"]:
        x, y = edit["at"]
        assert replay[y, x].tolist() == edit["before_rgba"]
        replay[y, x] = edit["after_rgba"]
    assert np.array_equal(replay, after)
    for edit in reversed(journal["edits"]):
        x, y = edit["at"]
        assert replay[y, x].tolist() == edit["after_rgba"]
        replay[y, x] = edit["before_rgba"]
    assert np.array_equal(replay, before)
    # Exact fixed canvas comparisons, with no pose fitting/recentering.
    for scale, size in (("native", 128), ("2x", 256), ("84", 84)):
        for ground, rgba in (("light", (236, 232, 220, 255)), ("dark", (29, 34, 43, 255))):
            text = "#101010" if ground == "light" else "#eeeeee"
            sheet = Image.new("RGBA", (size * 8, (size + 20) * 2), rgba)
            draw = ImageDraw.Draw(sheet)
            for row, bank in enumerate(("inputs/current", "candidate")):
                for i in range(8):
                    im = Image.open(P / bank / f"{i:02}.png").convert("RGBA").resize((size, size), Image.Resampling.NEAREST)
                    sheet.alpha_composite(im, (i * size, row * (size + 20) + 20))
                    draw.text((i * size + 4, row * (size + 20) + 4), f'{"current" if row == 0 else "cleanup"} {i:02}', fill=text)
            sheet.convert("RGB").save(P / f"proof/full8-{scale}-{ground}.png")
    # One compact witness sheet: original source, donor owner, target before/after, actual edits.
    witness = Image.new("RGBA", (1000, 274), (236, 232, 220, 255))
    draw = ImageDraw.Draw(witness)
    own = np.array(Image.open(P / "inputs/source-parts/02-left-source-leg-owner.png").convert("L")) > 0
    owned = donor.copy()
    owned[own] = [240, 15, 170, 255]
    diff = before.copy()
    diff[allowed] = [240, 15, 170, 255]
    samples = (("key02 glove source", sourcekey), ("02 claimed leg owner", owned), ("03 current", before), ("03 literal cleanup", after), ("17 actual edits", diff))
    for col, (label, pixels) in enumerate(samples):
        x = col * 200
        draw.text((x + 4, 5), label, fill="#101010")
        crop = Image.fromarray(pixels).crop((38, 74, 63, 95)).resize((200, 168), Image.Resampling.NEAREST)
        witness.alpha_composite(crop, (x, 24))
        im = Image.fromarray(pixels).resize((84, 84), Image.Resampling.NEAREST)
        witness.alpha_composite(im, (x + 50, 190))
    witness.convert("RGB").save(P / "proof/compact-source-owner-before-after.png")
    # Both actual input sources and frozen local copies remain hash exact.
    for entry in intake["files"]:
        assert sha(P / entry["local"]) == entry["sha256"]
        if not args.local_only and Path(entry["source"]).is_file():
            assert sha(Path(entry["source"])) == entry["sha256"]
    savej("INPUT-HASH-CHECK.json", {
        "all_frozen_inputs_unchanged": True,
        "files": [{**entry, "local_sha256_after": sha(P / entry["local"]),
                   "canonical_sha256_after": sha(Path(entry["source"])) if not args.local_only and Path(entry["source"]).is_file() else None} for entry in intake["files"]],
    })
    savej("COMPACT-PROOF-RECEIPT.json", {
        "scope": "one bounded SE03 erasure trial only; pending root inspection; no score or art approval",
        "generation_calls": 0, "canonical_writes": 0, "stage": [128, 128], "pivot": [64, 112],
        "clock_unchanged": {"holds": [[9, 160]] * 8, "cycle": [9, 20]},
        "changed_cels": [3], "actual_changed_pixels": 17, "erased_pixels": 16, "source_hip_restored_pixels": 1, "full_boot_masks_exact": True,
        "full_target_gloves_exact": True, "full_target_upper_hem_exact": True,
        "outside_literal_mask_RGBA_exact": True, "other7_PNG_bytes_exact": True,
        "input_hashes_before_after_exact": True, "literal_journal_replay_exact": True, "literal_journal_undo_exact": True,
        "input03_sha256": journal["input_sha256"], "candidate03_sha256": journal["output_sha256"],
        "source_owned_witnesses": "journal/03-literal-erasure.json", "editor_package_created": False,
        "notes": "No 02-to-03 recovery geometry altered. No engine contact or normal-speed human-playback claim.",
    })
    print(json.dumps(json.loads((P / "COMPACT-PROOF-RECEIPT.json").read_text()), indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent-coordinate mechanical audit and fresh-process CLI replay.

No rating is produced. Read whole-pose and timed proofs separately.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

import repair_dodge_tabs as repair

BASE = Path(__file__).resolve().parent


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    checks = []

    def check(value: bool, description: str) -> None:
        if not value:
            raise AssertionError(description)
        checks.append(description)

    for item in json.loads((BASE / "INPUTS.json").read_text()):
        check(sha((BASE / "inputs" / item["file"]).read_bytes()) == item["sha256"], "Frozen input matches: " + item["file"])
    original = Image.open(BASE / "inputs/brann-v3-atlas.png").convert("RGBA")
    candidate = Image.open(BASE / "candidate/atlas.png").convert("RGBA")
    plan = json.loads((BASE / "repair-plan.json").read_text())
    receipt = json.loads((BASE / "candidate/REPAIR-RECEIPT.json").read_text())
    check(original.size == candidate.size == (1024, 1920), "Atlas stage/layout unchanged")
    owned = {}
    for entry in receipt["source_maps"]:
        ox, oy = entry["frame"] % 8 * 128, entry["frame"] // 8 * 128
        for tx, ty, donor, sx, sy in entry["map_tx_ty_donor_sx_sy"]:
            owned[(ox + tx, oy + ty)] = (donor % 8 * 128 + sx, donor // 8 * 128 + sy)
    changed, alpha_erased, literal_matches = [], [], 0
    a, b = original.load(), candidate.load()
    for y in range(original.height):
        for x in range(original.width):
            if a[x, y] == b[x, y]:
                continue
            changed.append((x, y))
            check((x, y) in owned, f"Changed coordinate owned: {x},{y}")
            sx, sy = owned[(x, y)]
            check(b[x, y] == a[sx, sy], f"Changed RGBA exactly donor-owned: {x},{y}")
            literal_matches += 1
            if a[x, y][3] > 0 and b[x, y][3] == 0:
                alpha_erased.append((x, y))
    check(len(changed) == literal_matches == 258, "Exactly 258 changed RGBA pixels")
    check(not alpha_erased, "No nonzero-alpha pixel erased to transparency")
    # Independent cel slicing uses no producer helper.
    changed_cels = []
    for frame in range(120):
        x, y = frame % 8 * 128, frame // 8 * 128
        box = (x, y, x + 128, y + 128)
        if original.crop(box).tobytes() != candidate.crop(box).tobytes():
            changed_cels.append(frame)
    check(changed_cels == [24, 26], "All 118 other cels, including whole f25 glove and f27 red tab, unchanged")
    check(sha((BASE / "candidate/atlas.png").read_bytes()) == receipt["candidate_png_sha256"], "Saved candidate matches receipt PNG hash")
    check(sha((BASE / "repair-plan.json").read_bytes()) == receipt["plan_sha256"], "Saved plan matches receipt hash")
    replay, _ = repair.apply_dodge_repairs(original, plan)
    check(replay.tobytes() == candidate.tobytes(), "Fresh in-memory replay matches every RGBA byte")
    failures = []
    with tempfile.TemporaryDirectory(prefix="verify-", dir=BASE) as temporary:
        scratch = Path(temporary)
        command = [sys.executable, str(BASE / "repair_dodge_tabs.py"), "--output", str(scratch / "replay")]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        check(result.returncode == 0, "Fresh-process CLI replay completes")
        check((scratch / "replay/atlas.png").read_bytes() == (BASE / "candidate/atlas.png").read_bytes(), "Fresh-process replay PNG is byte-identical")
        for label, frame in [("target", 24), ("donor", 12)]:
            damaged = original.copy()
            x, y = frame % 8 * 128 + 64, frame // 8 * 128 + 82
            rgba = damaged.getpixel((x, y))
            damaged.putpixel((x, y), (rgba[0] ^ 1, *rgba[1:]))
            source = scratch / (label + ".png")
            damaged.save(source)
            output = scratch / (label + "-rejected")
            command = [sys.executable, str(BASE / "repair_dodge_tabs.py"), "--source", str(source), "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            check(result.returncode != 0 and not output.exists(), f"Changed {label} hash rejected before output creation")
            failures.append({"case": label + " hash mutation", "exit_code": result.returncode, "output_created": output.exists(), "error": result.stderr.strip().splitlines()[-1]})
        command = [sys.executable, str(BASE / "repair_dodge_tabs.py"), "--output", str(BASE / "candidate")]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        check(result.returncode != 0 and sha((BASE / "candidate/atlas.png").read_bytes()) == receipt["candidate_png_sha256"], "Existing output rejected without changing candidate")
    final = {"schema": "emberwake-dodge-cloth-verification/v1", "all_passed": True,
             "assertions": len(checks), "checks": checks,
             "changed_cels": changed_cels, "changed_pixels": len(changed),
             "outside_declared_masks_unchanged": True, "opaque_to_transparent_pixels": 0,
             "literal_same_view_donor_matches": literal_matches, "negative_cases": failures,
             "candidate_png_sha256": receipt["candidate_png_sha256"],
             "quality_status": "Mechanical bounds/replay only; independent visual review pending"}
    (BASE / "VERIFICATION.json").write_text(json.dumps(final, indent=2) + "\n")
    print(f"PASS: {len(checks)} assertions; 258 literal pixels; only f24/f26; no erased alpha; exact CLI replay")


if __name__ == "__main__":
    main()

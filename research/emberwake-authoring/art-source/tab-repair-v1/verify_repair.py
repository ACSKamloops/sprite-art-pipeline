#!/usr/bin/env python3
"""Independent frozen-map replay and preservation/rejection probes."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image

sys.dont_write_bytecode = True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--candidate", required=True, type=Path)
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("waist_repair", here / "repair_tabs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    plan = json.loads((here / "repair-plan.json").read_text())
    before = Image.open(args.source).convert("RGBA")
    selected = Image.open(args.candidate / "atlas.png").convert("RGBA")
    frozen = json.loads((args.candidate / "source-maps.json").read_text())
    replay = before.copy()
    allowed = set()
    checks = []
    def check(condition, name):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    # This reconstruction consumes frozen literal point maps directly; it
    # does not use polygon rasterization or the producer's apply function.
    for item in frozen:
        target = item["frame"]
        for tx, ty, donor, sx, sy in item["map_tx_ty_donor_sx_sy"]:
            a = (target % 8 * 128 + tx, target // 8 * 128 + ty)
            b = (donor % 8 * 128 + sx, donor // 8 * 128 + sy)
            replay.putpixel(a, before.getpixel(b))
            allowed.add(a)
    check(replay.tobytes() == selected.tobytes(), "frozen point-map replay equals selected RGBA")
    raw_before, raw_after = before.load(), selected.load()
    changed = 0
    for y in range(before.height):
        for x in range(before.width):
            if raw_before[x,y] != raw_after[x,y]:
                changed += 1
                if (x,y) not in allowed:
                    raise AssertionError(f"Outside-mask change at {(x,y)}")
    check(changed == 3738, "all 3738 changed pixels are authorized")
    for frame in range(112):
        if frame % 28 < 8:
            check(module.cel(before, frame).tobytes() == module.cel(selected, frame).tobytes(), f"walk cel {frame} unchanged")
    regenerated, _receipt = module.apply_tab_repairs(before, plan)
    check(regenerated.tobytes() == selected.tobytes(), "literal plan replay equals selected RGBA")
    check(before.tobytes() == Image.open(args.source).convert("RGBA").tobytes(), "producer leaves source in memory and on disk unchanged")
    for frame, description in [(14, "changed target"), (12, "changed donor")]:
        corrupt = before.copy()
        point = (frame % 8 * 128 + 2, frame // 8 * 128 + 2)
        corrupt.putpixel(point,(255,0,255,255))
        corrupt_bytes = corrupt.tobytes()
        rejected = False
        try:
            module.apply_tab_repairs(corrupt, plan)
        except ValueError:
            rejected = True
        check(rejected, description + " rejects before output")
        check(corrupt.tobytes() == corrupt_bytes, description + " rejection is nonmutating")
    changed_walk = before.copy()
    changed_walk.putpixel((2,2),(255,0,255,255))
    compatible, _receipt = module.apply_tab_repairs(changed_walk, plan)
    check(compatible.getpixel((2,2)) == (255,0,255,255), "new walk paint can coexist without bypassing action-bank hashes")
    check(module.cel(compatible,14).tobytes() == module.cel(selected,14).tobytes(), "walk replacement leaves target tab repair identical")
    # West was already a +1px staged mirror. The repair must retain that
    # relation using west's original donor texels rather than repainting it.
    for east in [42,44,48,51,55]:
        em = module.cel(selected,east)
        wm = module.cel(selected,east+56)
        exact = all(em.getpixel((x,y)) == wm.getpixel((128-x,y)) for y in range(128) for x in range(1,128))
        check(exact, f"east/west repaired mirror relation retained at {east}/{east+56}")
    report = {"passed":True,"checks":checks,"assertions":len(checks),"changed_pixels":changed,
              "candidate_png_sha256":module.sha((args.candidate / "atlas.png").read_bytes()),
              "note":"Exact replay, source ownership, preservation and rejected-edit checks; not an independent art rating."}
    if args.report:
        if args.report.exists():
            p.error("Report path must be fresh")
        args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"passed":True,"assertions":len(checks),"changed_pixels":changed}))


if __name__ == "__main__":
    main()

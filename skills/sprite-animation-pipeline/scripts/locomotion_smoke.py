#!/usr/bin/env python3
"""Forward-test the bundled Godot locomotion consumer in a fresh folder.

The 12x10 fixture is a clock/state/material diagnostic, not character art.
Requires Godot; --gpu additionally requires xvfb-run, Pillow and NumPy.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--godot", default="godot")
    parser.add_argument("--gpu", action="store_true")
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise FileExistsError(f"Use a fresh output folder: {out}")
    skill = Path(__file__).resolve().parents[1]
    shutil.copytree(skill / "assets/godot-locomotion-lane", out)
    diagnostic = skill / "assets/locomotion-smoke"
    shutil.copytree(diagnostic / "fixture", out / "fixture")
    shutil.copy2(diagnostic / "smoke_runtime.gd", out / "smoke_runtime.gd")
    logs = out / "logs"
    logs.mkdir()
    commands = []

    def run(name, command):
        with (logs / f"{name}.log").open("w") as log:
            completed = subprocess.run(command, cwd=out, stdout=log,
                                       stderr=subprocess.STDOUT, check=False)
        commands.append({"name": name, "command": command,
                         "exit_code": completed.returncode})
        if completed.returncode:
            raise RuntimeError(f"{name} failed; inspect {logs / (name + '.log')}")

    fixture = out / "fixture"
    run("configure", [sys.executable, "configure.py",
        str(fixture / "walk/manifest.json"), "--bank",
        str(fixture / "bank/bank.json"), "--contacts",
        str(fixture / "contacts.json"), "--stance-lock", "--stride", "6"])
    run("engine", [args.godot, "--headless", "--path", str(out),
                   "--script", "smoke_runtime.gd"])
    results = json.loads((out / "SMOKE-RUNTIME-RESULTS.json").read_text())
    check_count = len(results["checks"]) if isinstance(results["checks"], list) else int(results["checks"])
    if results["failed"] != 0 or check_count <= 0:
        raise RuntimeError("Engine assertions failed or produced no checks")
    reports = ["SMOKE-RUNTIME-RESULTS.json"]
    if args.gpu:
        for name, script, extra in [
            ("transition", "capture_transitions.gd", []),
            ("live", "capture_live.gd", ["--fixed-fps", "60"]),
            ("contact", "capture_contact.gd", []),
        ]:
            run(name, ["xvfb-run", "-a", args.godot, "--path", str(out),
                "--rendering-method", "gl_compatibility", *extra,
                "--script", script])
        run("verify-transition", [sys.executable, "verify_transitions.py"])
        run("verify-live", [sys.executable, "verify_transitions.py",
            "--records", "LIVE-CAPTURE-RECORDS.json", "--output",
            "LIVE-CAPTURE-VERIFICATION.json"])
        run("measure-contact", [sys.executable, "measure_contact.py"])
        reports += ["TRANSITION-CAPTURE-VERIFICATION.json",
                    "LIVE-CAPTURE-VERIFICATION.json",
                    "CONTACT-MATERIAL-MEASUREMENTS.json"]
    receipt = {
        "scope": "Portable diagnostic fixture; no animation-art acceptance",
        "checks": check_count, "failed": results["failed"],
        "gpu_requested": args.gpu, "commands": commands,
        "reports": {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
                    for name in reports},
        "consumer_files": {
            str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in out.iterdir() if p.is_file() and p.suffix in {".py", ".gd", ".tscn", ".godot"}
        },
    }
    (out / "SMOKE-RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"output": str(out), "checks": check_count,
                      "failed": results["failed"], "gpu": args.gpu}))


if __name__ == "__main__":
    main()

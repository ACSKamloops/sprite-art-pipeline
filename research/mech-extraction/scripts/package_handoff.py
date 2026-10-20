#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Bundle a verified Blender handoff with portable notes, code, and provenance."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "handoff"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main():
    validation = json.loads((OUT / "inventory/validation.json").read_text())
    gltf = json.loads((OUT / "inventory/gltf-validation.json").read_text())
    blender = json.loads((OUT / "inventory/blender-validation.json").read_text())
    smoke = json.loads((OUT / "inventory/blender-smoke-test.json").read_text())
    if not validation["passed"] or gltf["errors"] or not blender["all_imported_saved_and_reopened"] or not smoke["passed"]:
        raise RuntimeError("Validation must pass before packaging")
    for name in ["erf.py", "mw4.py"]:
        copy(ROOT / "scripts" / name, OUT / "tooling" / name)
    upstream = ROOT / "tools/erf-editor-source"
    copy(upstream / "LICENSE", OUT / "tooling/LICENSE-GPL-3.0.txt")
    copy(upstream / "LICENSE", OUT / "tooling/upstream/LICENSE")
    copy(upstream / "README.md", OUT / "tooling/upstream/README.md")
    for source in (upstream / "Original source").glob("*.pas"):
        copy(source, OUT / "tooling/upstream" / source.name)
    for source in (ROOT / "scripts").glob("*"):
        if source.is_file() and source.suffix in (".py", ".cjs"):
            copy(source, OUT / "provenance/workspace_scripts" / source.name)
    copy(ROOT / "requirements.txt", OUT / "provenance/requirements.txt")
    copy(ROOT / "sources/MechWarrior-4-Mercenaries_Win_EN_MekTek-version.source.json",
         OUT / "provenance/game-source.json")
    copy(ROOT / "reports/mech-extraction.json", OUT / "provenance/native-extraction.json")
    copy(ROOT / "reports/erf-parse-check.json", OUT / "provenance/erf-parse-check.json")
    copy(ROOT / "tools/vendor/blender-4.5.9-linux-x64.tar.xz.source.json",
         OUT / "provenance/blender-source.json")

    summary_path = OUT / "inventory/summary.json"
    summary = json.loads(summary_path.read_text())
    summary["blender_projects"] = blender["files"]
    summary["blender_version_tested"] = blender["blender_version"]
    summary["blender_import_save_reopen_passed"] = True
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    validation["blender_runtime_tested"] = True
    validation["note"] = "Independent geometry/pixel/hash checks plus Blender import/save/reopen; native animation keyframes are not decoded"
    (OUT / "inventory/validation.json").write_text(json.dumps(validation, indent=2) + "\n")

    # Exclude Python caches and Blender save backups created during local checks.
    files = sorted(path for path in OUT.rglob("*") if path.is_file()
                   and "__pycache__" not in path.parts and path.suffix != ".pyc"
                   and not path.name.endswith((".blend1", ".blend2"))
                   and path.name != "SHA256SUMS")
    sums = OUT / "SHA256SUMS"
    sums.write_text("".join(f"{digest(path)}  {path.relative_to(OUT).as_posix()}\n" for path in files))
    files.append(sums)
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    archive = artifacts / "mw4-mech-blender-handoff.zip"
    partial = archive.with_suffix(".zip.part")
    with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=5) as zipped:
        for path in files:
            zipped.write(path, "mw4-mech-blender-handoff/" + path.relative_to(OUT).as_posix())
    with zipfile.ZipFile(partial) as zipped:
        bad = zipped.testzip()
        if bad or len(zipped.infolist()) != len(files):
            raise RuntimeError("Package verification failed: " + str(bad))
    partial.replace(archive)
    sha256 = digest(archive)
    archive.with_suffix(".zip.sha256").write_text(sha256 + "  " + archive.name + "\n")
    report = {"file": archive.relative_to(ROOT).as_posix(), "bytes": archive.stat().st_size,
              "sha256": sha256, "files": len(files), "zip_crc_passed": True,
              "chassis_groups": summary["chassis_groups"], "blender_projects": blender["files"],
              "blender_version": blender["blender_version"], "animations_converted": False}
    archive.with_suffix(".zip.manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()

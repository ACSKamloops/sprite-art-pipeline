#!/usr/bin/env python3
"""Partition the verified handoff into three ordinary ZIPs with disjoint files."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts/mw4-mech-blender-handoff.zip"
OUT = ROOT / "artifacts/separate-zips"
DOWNLOADS = Path("/mnt/c/Users/killu/Downloads")
PREFIX = "mw4-mech-blender-handoff/"
NAMES = {
    "blender": "mw4-blender-projects.zip",
    "meshes": "mw4-meshes-and-textures.zip",
    "native": "mw4-native-assets-and-tools.zip",
}


def sha_file(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def estimated_size(info):
    return info.compress_size + 76 + 2 * len(info.filename.encode("utf-8"))


def group_for(relative):
    parts = relative.split("/")
    if parts[0] in ("blender", "previews") or relative in ("README.md", "BLENDER_HANDOFF.md"):
        return "blender"
    if parts[0] in ("models", "textures"):
        return "meshes"
    if parts[0] == "assembled":
        return None
    if relative in ("inventory/summary.json", "inventory/library.json",
                    "inventory/blender-validation.json", "inventory/blender-smoke-test.json"):
        return "blender"
    if relative.startswith("inventory/mechs/") or relative in (
        "inventory/assemblies.json", "inventory/textures.json", "inventory/gltf-validation.json"
    ):
        return "meshes"
    return "native"


def instructions(group, entries):
    previews = sorted(info.filename.removeprefix(PREFIX) for info in entries
                      if info.filename.startswith(PREFIX + "assembled/"))
    common = ("Each of the three ZIPs is a normal, independent archive with different files.\n"
              "No source file is repeated across these ZIPs. Extract them into the same\n"
              "parent folder to recreate the full library without file conflicts.\n"
              "You can also use the ready-to-open files in each archive separately.\n\n")
    detail = {
        "blender": ("# Blender projects\n\n"
                    "Contains all 113 Blender projects with packed textures and embedded notes,\n"
                    "the full handoff guide, the Atlas render, and Blender validation reports.\n"
                    "Open blender/atlas.blend to start. Named joint objects support rigid posing.\n"
                    "Native animation clips still need conversion to Blender actions.\n\n"),
        "meshes": ("# Mesh and texture exports\n\n"
                   "Contains all 3,905 OBJ/MTL parts, their metadata, all 710 PNG textures,\n"
                   "and the per-chassis manifests. OBJ texture paths work within this archive.\n"
                   "Parts are local meshes in Blender Z-up coordinates (x, -z, y); use the\n"
                   "joint transforms in the chassis manifests to assemble them.\n"
                   "Damaged parts, wrecks, and cockpit cages are also included.\n\n"),
        "native": ("# Original mech assets and tools\n\n"
                   "Contains all 22,423 native files, including original ERFs/TGAs, 3,724 native\n"
                   "animation files, joint/render definitions, reader tools, licenses, source\n"
                   "provenance, and the original complete-library checksum manifest.\n"
                   "Native animation files are not converted Blender actions.\n"
                   "The original SHA256SUMS describes the combined library; use the archive's\n"
                   "SHA256_native.txt to verify only the files in this ZIP.\n\n"),
    }[group]
    result = detail + common
    if previews:
        result += (f"This archive also includes {len(previews)} complete GLB previews with embedded\n"
                   "textures. The remaining GLBs are in the other model archive. Each GLB\n"
                   "can be imported into Blender independently. All 113 chassis also have\n"
                   "complete .blend projects in mw4-blender-projects.zip.\n\n"
                   "GLB previews included here:\n\n" + "\n".join(previews) + "\n")
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source_manifest = json.loads(SOURCE.with_suffix(".zip.manifest.json").read_text())
    if sha_file(SOURCE) != source_manifest["sha256"]:
        raise RuntimeError("Original ZIP checksum mismatch")
    groups = {key: [] for key in NAMES}
    weights = {key: 0 for key in NAMES}
    assigned = set()
    outputs = []
    with zipfile.ZipFile(SOURCE) as source:
        original = source.infolist()
        sums = {}
        for line in source.read(PREFIX + "SHA256SUMS").decode().splitlines():
            checksum, relative = line.split("  ", 1)
            sums[PREFIX + relative] = checksum
        delayed = []
        for info in original:
            if not info.filename.startswith(PREFIX) or info.is_dir():
                raise RuntimeError("Unexpected source ZIP entry: " + info.filename)
            group = group_for(info.filename.removeprefix(PREFIX))
            if group is None:
                delayed.append(info)
            else:
                groups[group].append(info)
                weights[group] += estimated_size(info)
        # Whole GLBs remain self-contained. Balance the two model archives
        # without separating any .blend project or OBJ texture dependency.
        for info in sorted(delayed, key=estimated_size, reverse=True):
            group = min(("blender", "meshes"), key=weights.get)
            groups[group].append(info)
            weights[group] += estimated_size(info)
        for group, infos in groups.items():
            print("BUILDING", NAMES[group], len(infos), "original files", flush=True)
            checksums = []
            output = OUT / NAMES[group]
            partial = output.with_suffix(".zip.part")
            with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=5) as zipped:
                for info in sorted(infos, key=lambda entry: entry.filename):
                    if info.filename in assigned:
                        raise RuntimeError("Duplicate archive assignment: " + info.filename)
                    data = source.read(info)
                    checksum = hashlib.sha256(data).hexdigest()
                    if info.filename in sums and checksum != sums[info.filename]:
                        raise RuntimeError("Source member checksum mismatch: " + info.filename)
                    zipped.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=5)
                    checksums.append((info.filename, checksum))
                    assigned.add(info.filename)
                note_name = PREFIX + f"README_{group.upper()}_ZIP.md"
                note = instructions(group, infos).encode()
                zipped.writestr(note_name, note)
                checksums.append((note_name, hashlib.sha256(note).hexdigest()))
                checksum_text = "".join(f"{checksum}  {name.removeprefix(PREFIX)}\n"
                                        for name, checksum in sorted(checksums))
                zipped.writestr(PREFIX + f"SHA256_{group}.txt", checksum_text)
            with zipfile.ZipFile(partial) as zipped:
                bad = zipped.testzip()
                if bad or len(zipped.infolist()) != len(infos) + 2:
                    raise RuntimeError("New ZIP integrity failure: " + str(bad))
                for name, checksum in checksums:
                    if hashlib.sha256(zipped.read(name)).hexdigest() != checksum:
                        raise RuntimeError("New ZIP member checksum mismatch: " + name)
            partial.replace(output)
            outputs.append({"filename": output.name, "bytes": output.stat().st_size,
                            "sha256": sha_file(output), "original_files": len(infos),
                            "blender_projects": sum(i.filename.endswith(".blend") for i in infos),
                            "glb_previews": sum(i.filename.endswith(".glb") for i in infos),
                            "zip_crc_passed": True, "member_hashes_passed": True})
        if assigned != {info.filename for info in original}:
            raise RuntimeError("Some original files were not assigned")
        members = []
        for output in outputs:
            with zipfile.ZipFile(OUT / output["filename"]) as zipped:
                names = set(zipped.namelist())
                if any(names & other for other in members):
                    raise RuntimeError("Files overlap between the three ZIPs")
                members.append(names)
    (OUT / "separate-zips.manifest.json").write_text(json.dumps({
        "source": source_manifest, "original_files_preserved_exactly_once": len(assigned),
        "archive_members_are_disjoint": True, "archives": outputs,
    }, indent=2) + "\n")

    # Existing user files are never overwritten. A matching previous copy is
    # reused if this script is run again.
    for output in outputs:
        target = DOWNLOADS / output["filename"]
        if target.exists():
            if sha_file(target) != output["sha256"]:
                raise RuntimeError("A different file already exists in Downloads: " + str(target))
        else:
            with (OUT / output["filename"]).open("rb") as src, target.open("xb") as dst:
                shutil.copyfileobj(src, dst, length=8 * 1024 * 1024)
        if target.stat().st_size != output["bytes"] or sha_file(target) != output["sha256"]:
            raise RuntimeError("Downloads copy verification failed: " + str(target))
        print("DOWNLOADS_VERIFIED", target.name, output["bytes"], flush=True)
    # Replace the download copy we created; the complete original ZIP remains
    # preserved in the Linux workspace for recovery.
    old_download = DOWNLOADS / SOURCE.name
    if old_download.exists():
        if sha_file(old_download) == source_manifest["sha256"]:
            old_download.unlink()
            print("Original Downloads copy replaced; workspace original retained", flush=True)
        else:
            print("Original Downloads filename contains changed data; preserved", flush=True)
    print(json.dumps(outputs, indent=2), flush=True)


if __name__ == "__main__":
    main()

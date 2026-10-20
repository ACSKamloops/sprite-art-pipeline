#!/usr/bin/env python3
"""Preserve every handoff file in ordinary ZIPs strictly below 50,000,000 bytes."""
import copy
import hashlib
import json
import re
import shutil
import zipfile
from collections import defaultdict
from pathlib import Path

from split_handoff import DOWNLOADS, PREFIX, ROOT, SOURCE, estimated_size, sha_file

OUT = ROOT / "artifacts/under-50mb"
LIMIT = 50_000_000
PACKS = {
    "blender": ["mw4-blender-library-a.zip", "mw4-blender-library-b.zip"],
    "meshes": ["mw4-mesh-library-a.zip", "mw4-mesh-library-b.zip"],
    "textures": ["mw4-texture-library-a.zip", "mw4-texture-library-b.zip",
                 "mw4-texture-library-c.zip", "mw4-texture-library-d.zip"],
    "native": ["mw4-original-mechs-and-animations.zip"],
}


def classify(relative):
    parts = relative.split("/")
    if parts[0] == "blender":
        return "blender", Path(relative).stem
    if parts[0] == "previews":
        return "blender", Path(relative).stem
    if relative in ("README.md", "BLENDER_HANDOFF.md", "inventory/summary.json",
                    "inventory/library.json", "inventory/blender-validation.json",
                    "inventory/blender-smoke-test.json"):
        return "blender", None
    if parts[0] == "models":
        return "meshes", parts[1]
    if parts[0] == "assembled":
        return "meshes", Path(relative).stem.removesuffix("_rest")
    if relative.startswith("inventory/mechs/"):
        return "meshes", Path(relative).stem
    if relative in ("inventory/assemblies.json", "inventory/gltf-validation.json"):
        return "meshes", None
    if parts[0] == "textures" or relative.startswith("native/textures/textures/"):
        stem = Path(relative).stem.split("_", 1)[1].lower()
        # Keep PNG/TGA copies and the 0..5 mip family in the same texture ZIP.
        return "textures", re.sub(r"[0-5]$", "", stem)
    if relative in ("inventory/textures.json", "SHA256SUMS"):
        return "textures", None
    return "native", None


def readme(category, filename, infos):
    content = {
        "blender": ("Ready-to-open Blender projects with packed images, named rigid joint\n"
                    "hierarchies, a preview studio, and embedded handoff notes. Open any\n"
                    "blender/*.blend file directly. Native actions have not been converted.\n"),
        "meshes": ("Complete GLB previews with embedded images, plus local OBJ/MTL mesh parts\n"
                   "and chassis manifests. Each GLB imports independently. Extract all four\n"
                   "texture ZIPs into the same parent folder for the OBJ material paths.\n"
                   "OBJ axes are already Blender Z-up (x, -z, y). GLBs use standard Y-up.\n"),
        "textures": ("PNG textures and the corresponding original TGAs, kept together with\n"
                     "their mip families. These are different texture files from the other\n"
                     "texture ZIPs. All four texture ZIPs complete the original texture library.\n"
                     "Source SHA256SUMS, when present, describes the full combined library.\n"),
        "native": ("All original mech ERF geometry, core joint/render data, scripts, and\n"
                   "native pose/animation files, plus source provenance and helper code.\n"
                   "Original texture TGAs are paired with PNGs in the four texture ZIPs.\n"
                   "Native clips still need decoding into Blender actions. Some reader and\n"
                   "export workflows also use manifests from the mesh ZIPs.\n"),
    }[category]
    all_names = [name for names in PACKS.values() for name in names]
    text = (f"# {filename}\n\n" + content + "\n"
            "Every ZIP is a standard independent archive below 50,000,000 bytes.\n"
            "Original files appear exactly once across the nine ZIPs; no file is split.\n"
            "Extract all ZIPs into the same parent folder to recreate the full library.\n"
            "All use the mw4-mech-blender-handoff/ root folder and have distinct files.\n"
            "Each archive includes a SHA-256 list of its own contents.\n\n"
            "Archives in the full set:\n\n" + "\n".join(all_names) + "\n\n")
    if category == "blender":
        chassis = sorted(Path(info.filename).stem for info in infos if info.filename.endswith(".blend"))
        text += f"Blender projects in this archive ({len(chassis)}):\n\n" + "\n".join(chassis) + "\n"
    elif category == "meshes":
        chassis = sorted(Path(info.filename).stem.removesuffix("_rest") for info in infos
                         if info.filename.endswith(".glb"))
        text += f"GLB chassis in this archive ({len(chassis)}):\n\n" + "\n".join(chassis) + "\n"
    return text.encode()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source_manifest = json.loads(SOURCE.with_suffix(".zip.manifest.json").read_text())
    if sha_file(SOURCE) != source_manifest["sha256"]:
        raise RuntimeError("Original source ZIP checksum mismatch")
    names = [name for category in PACKS.values() for name in category]
    category_for = {name: category for category, filenames in PACKS.items() for name in filenames}
    groups = {name: [] for name in names}
    sizes = {name: 0 for name in names}
    bundles = defaultdict(list)
    assigned = set()
    outputs = []
    member_sets = []
    with zipfile.ZipFile(SOURCE) as source:
        original = source.infolist()
        source_hashes = dict((PREFIX + relative, checksum) for checksum, relative in
            (line.split("  ", 1) for line in source.read(PREFIX + "SHA256SUMS").decode().splitlines()))
        for info in original:
            if not info.filename.startswith(PREFIX) or info.is_dir():
                raise RuntimeError("Unexpected source member: " + info.filename)
            category, bundle = classify(info.filename.removeprefix(PREFIX))
            if bundle is None:
                target = PACKS[category][0]
                groups[target].append(info)
                sizes[target] += estimated_size(info)
            else:
                bundles[(category, bundle)].append(info)
        for (category, bundle), infos in sorted(bundles.items(),
                key=lambda item: sum(estimated_size(info) for info in item[1]), reverse=True):
            target = min(PACKS[category], key=sizes.get)
            groups[target].extend(infos)
            sizes[target] += sum(estimated_size(info) for info in infos)
        if any(size >= LIMIT for size in sizes.values()):
            raise RuntimeError("Estimated archive exceeds file limit: " + str(sizes))

        for name in names:
            infos = groups[name]
            print("BUILDING", name, len(infos), "original files", flush=True)
            destination = OUT / name
            partial = destination.with_suffix(".zip.part")
            checksums = []
            stem = Path(name).stem.replace("-", "_")
            with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=5) as zipped:
                for info in sorted(infos, key=lambda entry: entry.filename):
                    if info.filename in assigned:
                        raise RuntimeError("Repeated original file: " + info.filename)
                    data = source.read(info)
                    checksum = hashlib.sha256(data).hexdigest()
                    if info.filename in source_hashes and checksum != source_hashes[info.filename]:
                        raise RuntimeError("Source member hash mismatch: " + info.filename)
                    zipped.writestr(copy.copy(info), data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=5)
                    checksums.append((info.filename, checksum))
                    assigned.add(info.filename)
                note = readme(category_for[name], name, infos)
                note_name = PREFIX + f"READ_ME_{stem}.md"
                zipped.writestr(note_name, note)
                checksums.append((note_name, hashlib.sha256(note).hexdigest()))
                sums = "".join(f"{checksum}  {member.removeprefix(PREFIX)}\n"
                               for member, checksum in sorted(checksums))
                zipped.writestr(PREFIX + f"SHA256_{stem}.txt", sums)
            actual_size = partial.stat().st_size
            if actual_size >= LIMIT:
                raise RuntimeError(f"Archive is too large: {name}: {actual_size}")
            with zipfile.ZipFile(partial) as zipped:
                bad = zipped.testzip()
                if bad or len(zipped.infolist()) != len(infos) + 2:
                    raise RuntimeError("ZIP integrity failure: " + str(bad))
                for member, checksum in checksums:
                    if hashlib.sha256(zipped.read(member)).hexdigest() != checksum:
                        raise RuntimeError("New member hash mismatch: " + member)
                members = set(zipped.namelist())
                if any(members & other for other in member_sets):
                    raise RuntimeError("Archive member names overlap")
                member_sets.append(members)
            partial.replace(destination)
            outputs.append({"filename": name, "bytes": actual_size, "sha256": sha_file(destination),
                            "original_files": len(infos),
                            "blender_projects": sum(info.filename.endswith(".blend") for info in infos),
                            "glb_previews": sum(info.filename.endswith(".glb") for info in infos),
                            "zip_crc_passed": True, "member_hashes_passed": True})
            print("ARCHIVE_VERIFIED", name, actual_size, flush=True)
        if assigned != {info.filename for info in original}:
            raise RuntimeError("Original files are missing from the set")
    manifest = {"source": source_manifest, "limit_bytes_exclusive": LIMIT,
                "original_files_preserved_exactly_once": len(assigned),
                "archive_members_are_disjoint": True, "archives": outputs}
    (OUT / "under-50mb.manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    for archive in outputs:
        target = DOWNLOADS / archive["filename"]
        if target.exists():
            if sha_file(target) != archive["sha256"]:
                raise RuntimeError("Different user file exists: " + str(target))
        else:
            with (OUT / archive["filename"]).open("rb") as src, target.open("xb") as dst:
                shutil.copyfileobj(src, dst, length=8 * 1024 * 1024)
        if (target.stat().st_size != archive["bytes"] or target.stat().st_size >= LIMIT
                or sha_file(target) != archive["sha256"]):
            raise RuntimeError("Downloads verification failed: " + str(target))
        print("DOWNLOADS_VERIFIED", target.name, archive["bytes"], flush=True)

    # Remove only the three verified download copies created in the previous
    # turn. Their original ZIPs remain available in the Linux workspace.
    previous = json.loads((ROOT / "artifacts/separate-zips/separate-zips.manifest.json").read_text())
    for archive in previous["archives"]:
        target = DOWNLOADS / archive["filename"]
        if target.exists() and sha_file(target) == archive["sha256"]:
            target.unlink()
            print("REPLACED_PREVIOUS_DOWNLOAD", target.name, flush=True)
    print(json.dumps(outputs, indent=2), flush=True)


if __name__ == "__main__":
    main()

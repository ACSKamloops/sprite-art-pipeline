#!/usr/bin/env python3
"""Extract mech resources only; preserve archive paths, IDs, and duplicates."""
import collections
import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path

from mw4 import Archive

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "sources/game"
OUT = ROOT / "handoff/native"
# These directories contain infantry/battle armor rather than BattleMechs.
NON_MECHS = {
    "claninfantry", "claninfantrye", "claninfantrym", "isinfantryb",
    "isinfantrye", "isinfantrym", "infantry", "elemental", "gnome",
    "golem", "graydeath", "infiltrator", "kanazuchi", "longinus",
}


def mech_entry(entry):
    parts = entry.path.parts
    if len(parts) < 3 or parts[0].lower() != "mechs":
        return False
    chassis = parts[1].lower().removesuffix("_destroyed")
    return chassis not in NON_MECHS


def write_entry(archive, entry, role="mech"):
    source = archive.path.relative_to(GAME).as_posix()
    archive_key = source.removeprefix("RESOURCE/").removesuffix(".mw4")
    path = OUT / archive_key / Path(*entry.path.parts[:-1]) / f"{entry.id:05d}_{entry.path.name}"
    encoding = "raw" if entry.compressed_size == entry.size else "lzw"
    with archive.path.open("rb") as stream:
        stream.seek(archive.base + entry.offset)
        prefix = stream.read(6)
    if prefix == b"mektek":
        # Preserve encrypted gameplay metadata. Geometry/animation is not encrypted.
        with archive.path.open("rb") as stream:
            stream.seek(archive.base + entry.offset)
            data = stream.read(entry.compressed_size)
        path = path.with_name(path.name + ".mektek")
        role = "opaque_gameplay_metadata"
        encoding = "mektek_wrapper_not_decoded"
    else:
        data = archive.read(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise RuntimeError("Refusing to overwrite different existing data: " + str(path))
    else:
        path.write_bytes(data)
    return {
        "archive": source, **asdict(entry),
        "output": path.relative_to(ROOT / "handoff").as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(), "role": role,
        "encoding": encoding, "output_bytes": len(data),
    }


def main():
    started = last = time.monotonic()
    results = []
    scans = []
    skipped = []
    failures = []
    for file in sorted(GAME.rglob("*")):
        if not file.is_file() or file.suffix.lower() != ".mw4":
            continue
        try:
            archive = Archive(file)
        except (ValueError, OSError) as error:
            scans.append({"archive": file.relative_to(GAME).as_posix(), "index_error": str(error)})
            continue
        selected = [entry for entry in archive.entries if mech_entry(entry)]
        excluded = [entry.name for entry in archive.entries
                    if entry.name.lower().startswith("mechs\\") and not mech_entry(entry)]
        if excluded:
            skipped.append({"archive": file.relative_to(GAME).as_posix(), "excluded_infantry_or_battle_armor_entries": len(excluded)})
        scans.append({"archive": file.relative_to(GAME).as_posix(), "entries": len(archive.entries), "selected": len(selected)})
        for entry in selected:
            try:
                results.append(write_entry(archive, entry))
            except (ValueError, OSError) as error:
                failures.append({"archive": file.relative_to(GAME).as_posix(), **asdict(entry), "error": str(error)})
            now = time.monotonic()
            if now - last >= 10:
                print(f"Extracted {len(results)} mech resources; failures {len(failures)}; {now-started:.0f}s", flush=True)
                last = now
    report = {
        "scope": "BattleMech resources and wrecks; infantry and battle armor excluded",
        "excluded_chassis": sorted(NON_MECHS),
        "files": results, "archive_scans": scans,
        "excluded_counts": skipped, "failures": failures,
    }
    (ROOT / "reports/mech-extraction.json").write_text(json.dumps(report, indent=2) + "\n")
    print("FINISHED", len(results), "files;", len(failures), "failures;", len(scans), "archives inspected", flush=True)
    print("TYPES", collections.Counter(Path(f["name"]).suffix.lower() for f in results).most_common(10), flush=True)
    if failures:
        print("FIRST FAILURES", json.dumps(failures[:3], indent=2), flush=True)


if __name__ == "__main__":
    main()

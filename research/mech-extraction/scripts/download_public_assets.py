#!/usr/bin/env python3
"""Download and extract the MW4 asset library without credentials (Python + curl)."""
import argparse
import hashlib
import json
import shutil
import stat
import subprocess
import time
import zipfile
from pathlib import Path


def digest_stream(stream):
    checksum = hashlib.sha256()
    while True:
        block = stream.read(1024*1024)
        if not block:
            return checksum.hexdigest()
        checksum.update(block)


def digest(path):
    with path.open("rb") as stream:
        return digest_stream(stream)


def download(record, path):
    if path.exists():
        if path.stat().st_size == record["bytes"] and digest(path) == record["sha256"]:
            print("Using verified local ZIP:", path.name, flush=True)
            return
        raise RuntimeError("Existing file differs; move it before continuing: " + str(path))
    partial = path.with_suffix(".zip.part")
    for attempt in range(3):
        try:
            if shutil.which("curl") is None:
                raise RuntimeError("The downloader requires curl in addition to Python 3")
            result = subprocess.run(["curl", "-q", "--fail", "--location", "--silent", "--show-error",
                                     "--connect-timeout", "30", "--max-time", "600",
                                     "--output", str(partial), record["url"]],
                                    capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError("Download failed: " + result.stderr.strip())
            if partial.stat().st_size != record["bytes"] or digest(partial) != record["sha256"]:
                raise RuntimeError("Size/SHA-256 mismatch: " + path.name)
            partial.replace(path)
            return
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)


def extract(path, destination):
    with zipfile.ZipFile(path) as zipped:
        if zipped.testzip():
            raise RuntimeError("ZIP integrity check failed: " + path.name)
        for info in zipped.infolist():
            target = (destination / info.filename).resolve()
            try:
                target.relative_to(destination.resolve())
            except ValueError:
                raise RuntimeError("Unsafe archive member: " + info.filename)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise RuntimeError("Unsafe archive member: " + info.filename)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                with zipped.open(info) as source:
                    wanted = digest_stream(source)
                if not target.is_file() or target.stat().st_size != info.file_size or digest(target) != wanted:
                    raise RuntimeError("Existing extracted file differs; preserving it: " + str(target))
                continue
            with zipped.open(info) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output, length=1024*1024)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=Path.cwd()/"mw4-assets")
    parser.add_argument("--only-blender", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).parent / "download-manifest.json").read_text())
    args.destination.mkdir(parents=True, exist_ok=True)
    zip_directory = args.destination / "zip-downloads"
    zip_directory.mkdir(exist_ok=True)
    records = [r for r in manifest["archives"]
               if not args.only_blender or r["filename"].startswith("mw4-blender-library-")]
    for index, record in enumerate(records, 1):
        filename = record["filename"]
        if Path(filename).name != filename or not filename.endswith(".zip"):
            raise RuntimeError("Invalid manifest filename")
        print(f"[{index}/{len(records)}] Downloading {filename} ({record['bytes']/1e6:.2f} MB)", flush=True)
        path = zip_directory / filename
        download(record, path)
        extract(path, args.destination)
        print("Verified and extracted:", filename, flush=True)
    print("Ready:", args.destination / "mw4-mech-blender-handoff", flush=True)
    print("Native animation files still require conversion to Blender actions.", flush=True)


if __name__ == "__main__":
    main()

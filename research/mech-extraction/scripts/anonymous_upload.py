#!/usr/bin/env python3
"""Publish the nine ZIPs to TempFile and verify each anonymous direct download."""
import datetime as dt
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/public-upload"
ARCHIVES = ROOT / "artifacts/under-50mb"
MANIFEST = ARCHIVES / "under-50mb.manifest.json"
API = "https://tempfile.org/api/upload/local"


def utc(milliseconds):
    return dt.datetime.fromtimestamp(milliseconds/1000, dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha_file(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def curl(args):
    result = subprocess.run(["curl", "--fail-with-body", "--silent", "--show-error",
                             "--connect-timeout", "20", "--max-time", "300", *args],
                            capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"curl failed ({result.returncode}): {result.stderr.strip()}")


def upload(path, response_path):
    curl(["--form", f"files=@{path};type=application/zip", "--form", "expiryHours=48",
          API, "--output", str(response_path)])
    response = json.loads(response_path.read_text())
    if not response.get("success") or len(response.get("files", [])) != 1:
        raise RuntimeError("Upload rejected: " + repr(response))
    record = response["files"][0]
    parsed = urlparse(record["url"])
    if parsed.scheme != "https" or parsed.netloc != "tempfile.org" or record["size"] != path.stat().st_size:
        raise RuntimeError("Unexpected upload metadata")
    return record


def verify(record, filename, expected_size, expected_sha):
    url = record["url"].rstrip("/") + "/download"
    local = OUT / "verification" / filename
    local.parent.mkdir(parents=True, exist_ok=True)
    curl(["--location", url, "--output", str(local)])
    if local.stat().st_size != expected_size or sha_file(local) != expected_sha:
        raise RuntimeError("Remote download does not match source: " + filename)
    with zipfile.ZipFile(local) as archive:
        if archive.testzip():
            raise RuntimeError("Remote ZIP CRC check failed: " + filename)
    return url


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    archives = json.loads(MANIFEST.read_text())["archives"]
    progress_path = OUT / "upload-progress.json"
    progress = json.loads(progress_path.read_text()) if progress_path.exists() else {}
    first_response = ROOT / "reports/tempfile-first-upload.json"
    records = []
    for index, archive in enumerate(archives):
        filename = archive["filename"]
        path = ARCHIVES / filename
        if sha_file(path) != archive["sha256"] or path.stat().st_size >= 50_000_000:
            raise RuntimeError("Source ZIP changed or exceeds the limit: " + filename)
        record = progress.get(filename, {}).get("host_response")
        if record is None:
            if index == 0 and first_response.exists():
                record = json.loads(first_response.read_text())["files"][0]
            else:
                print("UPLOADING", index+1, "of", len(archives), filename, flush=True)
                record = upload(path, OUT / (filename + ".response.json"))
            progress[filename] = {"host_response": record, "verified": False}
            progress_path.write_text(json.dumps(progress, indent=2) + "\n")
        if record["expiryTime"] <= dt.datetime.now(dt.timezone.utc).timestamp()*1000:
            raise RuntimeError("Recorded upload has expired: " + filename)
        if "--kit-only" in sys.argv and progress[filename]["verified"]:
            url = record["url"].rstrip("/") + "/download"
        else:
            url = verify(record, filename, archive["bytes"], archive["sha256"])
        progress[filename]["verified"] = True
        progress_path.write_text(json.dumps(progress, indent=2) + "\n")
        records.append({"filename": filename, "url": url, "bytes": archive["bytes"],
                        "sha256": archive["sha256"], "expires_utc": utc(record["expiryTime"]),
                        "anonymous_download_verified": True})
        print("VERIFIED", index+1, "of", len(archives), filename, url, flush=True)

    manifest = {
        "project": "MechWarrior 4 mech-only Blender handoff",
        "requires_credentials": False,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "expires_utc": min(record["expires_utc"] for record in records),
        "chassis_groups": 113, "blender_projects": 113,
        "native_animation_files": 3724, "native_animations_converted_to_blender_actions": False,
        "original_library_files_preserved": 35231,
        "layout": "Independent ZIPs with distinct files; extract all into the same parent folder",
        "guide": "mw4-mech-blender-handoff/BLENDER_HANDOFF.md",
        "archives": records,
    }
    kit = OUT / "kit"
    kit.mkdir(exist_ok=True)
    (kit / "download-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (kit / "download_all.py").write_text((ROOT / "scripts/download_public_assets.py").read_text())
    (kit / "SHA256SUMS").write_text("".join(f"{record['sha256']}  {record['filename']}\n" for record in records))
    (kit / "README.md").write_text(
        "# MW4 mech library download kit\n\n"
        "This small ZIP contains the downloader and direct URLs, not the models themselves.\n"
        "Run `python3 download_all.py` to fetch and extract all nine asset ZIPs.\n"
        "No account, token, cookies, or credentials are needed. Requires Python 3 and curl; no Python packages are needed.\n"
        "The asset ZIPs are each below 50,000,000 bytes and have verified SHA-256 hashes.\n"
        "The complete download is about 376 MB; extracted files need more disk space.\n\n"
        f"Links expire at {manifest['expires_utc']}. Download before then.\n\n"
        "Ready-to-open projects are in mw4-assets/mw4-mech-blender-handoff/blender/.\n"
        "Read BLENDER_HANDOFF.md for source notes, hierarchy/material information, and assembly exceptions.\n"
        "Native poses/animation files are preserved but still need conversion to Blender actions.\n"
        "Use `--only-blender` for just the two ready-to-open Blender collections.\n"
        "Use `--destination /your/path` to choose another output folder.\n"
    )
    kit_zip = OUT / "mw4-download-kit.zip"
    with zipfile.ZipFile(kit_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
        for path in sorted(kit.iterdir()):
            zipped.write(path, "mw4-download-kit/" + path.name)
    kit_sha = sha_file(kit_zip)
    kit_record = upload(kit_zip, OUT / "kit-upload.response.json")
    kit_url = verify(kit_record, kit_zip.name, kit_zip.stat().st_size, kit_sha)
    result = {"download_kit_url": kit_url, "download_kit_bytes": kit_zip.stat().st_size,
              "download_kit_sha256": kit_sha, "earliest_asset_expiry_utc": manifest["expires_utc"],
              "all_nine_anonymous_downloads_verified": True, "archives": records}
    (OUT / "public-links.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PUBLIC_UPLOAD_COMPLETE", json.dumps(result), flush=True)


if __name__ == "__main__":
    main()

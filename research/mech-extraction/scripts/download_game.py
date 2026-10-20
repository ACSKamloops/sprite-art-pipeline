#!/usr/bin/env python3
"""Download the selected package through its normal page/session flow."""
import hashlib
import http.cookiejar
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = "https://www.myabandonware.com/game/mechwarrior-4-mercenaries-3ak"
DOWNLOAD = "https://www.myabandonware.com/download/liro-mechwarrior-4-mercenaries"
DEST = ROOT / "sources/MechWarrior-4-Mercenaries_Win_EN_MekTek-version.zip"
EXPECTED = 1_879_627_447


def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    part = DEST.with_suffix(DEST.suffix + ".part")
    if DEST.exists():
        if DEST.stat().st_size != EXPECTED:
            raise RuntimeError("Existing destination has an unexpected size")
        print("Download already present", flush=True)
    else:
        for attempt in range(1, 9):
            opener = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
            )
            headers = {"User-Agent": "Mozilla/5.0", "Referer": PAGE}
            try:
                with opener.open(urllib.request.Request(PAGE, headers=headers), timeout=30) as response:
                    response.read()
                offset = part.stat().st_size if part.exists() else 0
                if offset == EXPECTED:
                    part.rename(DEST)
                    break
                if offset:
                    headers["Range"] = f"bytes={offset}-"
                url = DOWNLOAD + "?download=" + str(time.time_ns())
                with opener.open(urllib.request.Request(url, headers=headers), timeout=45) as response:
                    if "application/zip" not in response.headers.get("Content-Type", ""):
                        raise RuntimeError("Download returned a page instead of a ZIP")
                    if offset:
                        if response.status != 206 or not response.headers.get("Content-Range", "").startswith(f"bytes {offset}-"):
                            raise RuntimeError("Server did not honor the resume request")
                    else:
                        size = int(response.headers.get("Content-Length", "0"))
                        if size != EXPECTED:
                            raise RuntimeError(f"Package changed: expected {EXPECTED}, received {size}")
                    started = last = time.monotonic()
                    written = offset
                    with part.open("ab" if offset else "xb") as output:
                        while chunk := response.read(1024 * 1024):
                            if not written and chunk[:4] != b"PK\x03\x04":
                                raise RuntimeError("Download does not have a ZIP header")
                            output.write(chunk)
                            written += len(chunk)
                            now = time.monotonic()
                            if now - last >= 10:
                                speed = (written - offset) / (now - started) / 1_000_000
                                print(f"{written / EXPECTED:.1%}: {written / 1_000_000:.0f} / {EXPECTED / 1_000_000:.0f} MB, {speed:.1f} MB/s", flush=True)
                                last = now
                    if written != EXPECTED:
                        raise RuntimeError(f"Incomplete transfer: {written} bytes")
                part.rename(DEST)
                break
            except (OSError, urllib.error.HTTPError, RuntimeError) as exc:
                print(f"Attempt {attempt}: {exc}", flush=True)
                if attempt == 8:
                    raise
                time.sleep(2)
    digest = hashlib.file_digest(DEST.open("rb"), "sha256").hexdigest()
    record = {
        "source_page": PAGE,
        "package": "MekTek",
        "filename": DEST.name,
        "bytes": DEST.stat().st_size,
        "sha256": digest,
        "downloaded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verification": "Local SHA-256 and expected size; not a publisher-authenticated hash.",
    }
    DEST.with_suffix(".source.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2), flush=True)


if __name__ == "__main__":
    main()

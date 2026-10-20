"""Fresh-folder replay using only local input files and vendored editor code."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

from PIL import Image

P = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    out = args.destination.resolve()
    out.mkdir(parents=True, exist_ok=False)
    for directory in ("inputs", "scripts"):
        shutil.copytree(P / directory, out / directory, ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("INPUTS.json", "repair_spur.py"):
        shutil.copy2(P / name, out / name)
    for directory in ("candidate", "proof", "journal", "projects", "exports", "verification"):
        (out / directory).mkdir()
    commands = ([sys.executable, str(out / "repair_spur.py"), "--local-only"],
                [sys.executable, str(out / "scripts/build_editor.py")])
    log = []
    for command in commands:
        process = subprocess.run(command, cwd=out, text=True, capture_output=True)
        log.append({"argv": command, "returncode": process.returncode,
                    "stdout": process.stdout, "stderr": process.stderr})
        assert process.returncode == 0, process.stderr
    compared = []
    for bank in ("candidate", "exports"):
        for src in sorted((P / bank).glob("*.png")):
            dst = out / bank / src.name
            assert sha(src) == sha(dst)
            assert Image.open(src).convert("RGBA").tobytes() == Image.open(dst).convert("RGBA").tobytes()
            compared.append({"relative_path": str(src.relative_to(P)), "sha256": sha(src), "PNG_bytes_and_RGBA_exact": True})
    for name in ("initial", "final", "journal", "03-transaction", "03-transaction-receipt"):
        assert sha(P / f"projects/{name}.json") == sha(out / f"projects/{name}.json")
    assert sha(P / "journal/03-literal-erasure.json") == sha(out / "journal/03-literal-erasure.json")
    result = {"status": "PASS local-only fresh-folder replay", "canonical_paths_read": False,
              "all8_candidate_PNG_bytes_and_RGBA_exact": True,
              "all8_editor_export_PNG_bytes_and_RGBA_exact": True,
              "editor_projects_transaction_receipt_and_journal_bytes_exact": True,
              "literal_journal_bytes_exact": True, "destination": str(out), "commands": log,
              "PNG_comparisons": compared}
    (out / "PORTABLE-REPLAY-RECEIPT.json").write_text(json.dumps(result, indent=2) + "\n")
    (P / "verification/PORTABLE-REPLAY-RECEIPT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in ("commands", "PNG_comparisons")}, indent=2))


if __name__ == "__main__":
    main()

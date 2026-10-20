#!/usr/bin/env python3
"""Evidence-preserving H3 pilot; a native vendor test, not PixelLab inference.

prepare is offline. submit makes exactly one POST, with no automatic retry.
poll queries once; download sends no Authorization to the output host.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time
from urllib import error, parse, request

API = "https://api.minimax.io"
RESEARCH = Path("/home/astra/projects/pixellab-local-test-20261011")
AUTH = Path("/home/astra/.hermes/auth.json")
MAX_JSON = 16 * 1024 * 1024
MAX_VIDEO = 512 * 1024 * 1024


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n")
    tmp.replace(path)


def read_json(path):
    return json.loads(path.read_text())


def load_case(run):
    case = read_json(run / "case.json")
    for name, expected in case["input_hashes"].items():
        if digest((run / name).read_bytes()) != expected:
            raise ValueError(f"Prepared input changed: {name}")
    return case


def prepare(run, source_path, prompt_path, research=RESEARCH):
    run.mkdir(parents=True, exist_ok=False)
    original = research / "runtime/probes/minimax-walk/request.json"
    body = read_json(original)["body"]
    source = source_path.read_bytes()
    motion_prompt = prompt_path.read_text()
    if not motion_prompt.strip() or len(motion_prompt) > 7000:
        raise ValueError("A nonempty native motion prompt of at most 7000 characters is required")
    from PIL import Image
    import io
    with Image.open(io.BytesIO(source)) as image:
        size = image.size
        if size != (256, 256):
            raise ValueError("This declared pilot requires a 256x256 PNG source")
        if image.format != "PNG":
            raise ValueError("This declared pilot requires a PNG source")
    source_uri = "data:image/png;base64," + base64.b64encode(source).decode()
    native = {
        "model": "MiniMax-H3",
        "content": [
            {"type": "text", "text": motion_prompt},
            {"type": "image_url", "image_url": {"url": source_uri}, "role": "first_frame"},
        ],
        "resolution": "768P",
        "duration": 4,
        "ratio": "adaptive",
    }
    (run / "source.png").write_bytes(source)
    write_json(run / "request.json", native)
    case = {
        "version": 1, "created_utc": now(), "method": "native-minimax-h3-image-to-video",
        "method_reference_case": str(original), "method_reference_case_sha256": digest(original.read_bytes()),
        "same_subject_as_pixellab_capture": False,
        "subject": "original generic RPG hero; user excluded the Warhammer Captain from this test",
        "source_path": str(source_path), "prompt_path": str(prompt_path),
        "motion_prompt": motion_prompt, "source_size": list(size),
        "source_png_sha256": digest(source), "native_model": "MiniMax-H3",
        "native_duration_seconds": 4, "native_resolution": "768P",
        "pixellab_controls": {k: v for k, v in body.items() if k != "first_frame"},
        "control_mapping": {
            "first_frame": "same original PNG bytes; documented first_frame role",
            "description": "new generic-hero motion prompt; preserved literally, no enhancement or caption rewriting",
            "frame_count": "unsupported; four native seconds is an independent test duration, not eight sprite frames",
            "seed": "unsupported in inspected native H3 V2 schema; not submitted",
            "no_background": "unsupported; original source alpha retained in submitted PNG, no output-alpha guarantee",
            "enhance_prompt": "no separate Context-IR call; PixelLab private/native prompt processing parity unknown",
        },
        "pixel_conversion": "none; retain native video before any independently named conversion",
        "pixellab_private_inference_replicated": False,
        "input_hashes": {n: digest((run / n).read_bytes()) for n in ["source.png", "request.json"]},
    }
    write_json(run / "case.json", case)
    write_json(run / "state.json", {"status": "prepared", "created_utc": now(), "submission_attempts": 0})
    return {"status": "prepared", "run": str(run), "model": native["model"], "source_sha256": digest(source)}


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def credentials():
    for name in ("MINIMAX_PAYG_KEY", "MINIMAX_API_KEY"):
        if os.environ.get(name):
            return os.environ[name], {"source": name, "kind": "api-key"}
    obj = read_json(AUTH)["providers"]["minimax-oauth"]
    token = obj.get("access_token")
    if not isinstance(token, str) or not token:
        raise ValueError("Existing Hermes MiniMax OAuth credential is missing")
    expiry = obj.get("expires_at")
    if expiry and datetime.fromisoformat(expiry.replace("Z", "+00:00")) <= datetime.now(timezone.utc):
        raise ValueError("Existing Hermes MiniMax OAuth credential expired; not refreshing silently")
    return token, {"source": "existing Hermes minimax-oauth", "kind": "oauth", "refresh_performed": False}


def scrub(value, token):
    if isinstance(value, str):
        return value.replace(token, "[REDACTED]")
    if isinstance(value, list):
        return [scrub(v, token) for v in value]
    if isinstance(value, dict):
        return {scrub(k, token): scrub(v, token) for k, v in value.items()}
    return value


def api_call(method, path, token, payload=None):
    # Callers supply only fixed paths or a validated task ID, never arbitrary URLs.
    if not (path == "/v2/video_generation" or re.fullmatch(r"/v2/query/video_generation/[A-Za-z0-9_-]+", path)):
        raise ValueError("Unexpected API path")
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    req = request.Request(API + path, data=data, method=method,
                          headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    start = time.monotonic()
    try:
        response = request.build_opener(NoRedirect).open(req, timeout=60)
    except error.HTTPError as exc:
        response = exc
    except (error.URLError, TimeoutError):
        return {"http_status": None, "transport": "failed-or-ambiguous", "elapsed_seconds": round(time.monotonic()-start, 3)}, None
    with response:
        raw = response.read(MAX_JSON + 1)
        status = response.code
        if len(raw) > MAX_JSON:
            raise ValueError("API response exceeded bounded retention limit")
    try:
        result = scrub(json.loads(raw), token)
    except (json.JSONDecodeError, UnicodeDecodeError):
        result = {"non_json_body": True, "bytes": len(raw), "body_sha256": digest(raw)}
    return {"http_status": status, "elapsed_seconds": round(time.monotonic()-start, 3)}, result


def submit(run):
    load_case(run)
    state = read_json(run / "state.json")
    if state.get("submission_attempts") != 0 or state.get("status") != "prepared":
        raise ValueError("Submission already attempted; resume polling instead of duplicating a paid job")
    token, origin = credentials()
    # Cross-process exclusive claim as well as the state marker; never remove it.
    fd = os.open(run / ".submission.lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    state.update(status="submission-attempted", submission_attempts=1, submitted_utc=now(), credential=origin)
    write_json(run / "state.json", state)  # Durable marker before paid POST.
    transport, result = api_call("POST", "/v2/video_generation", token, read_json(run / "request.json"))
    write_json(run / "submit-response.json", {"captured_utc": now(), **transport, "body": result})
    task = result.get("task_id") if isinstance(result, dict) else None
    if transport["http_status"] == 200 and isinstance(task, str) and re.fullmatch(r"[A-Za-z0-9_-]+", task):
        state.update(status="accepted", task_id=task)
    else:
        state.update(status="submission-failed" if transport["http_status"] is not None else "submission-ambiguous")
    write_json(run / "state.json", state)
    return {"status": state["status"], **transport, "credential_kind": origin["kind"],
            "error": result.get("error") if isinstance(result, dict) else None}


def task_body(result):
    # The retained vendor query schema returns a `task` wrapper.
    if not isinstance(result, dict):
        return {}
    if isinstance(result.get("task"), dict):
        return result["task"]
    return result


def poll(run):
    load_case(run)
    state = read_json(run / "state.json")
    task = state.get("task_id")
    if not isinstance(task, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", task):
        raise ValueError("No accepted task ID; no request sent")
    token, _ = credentials()
    transport, result = api_call("GET", "/v2/query/video_generation/" + task, token)
    polls = run / "polls"; polls.mkdir(exist_ok=True)
    index = len(list(polls.glob("*.json")))
    write_json(polls / f"{index:04d}.json", {"captured_utc": now(), **transport, "body": result})
    obj = task_body(result)
    status = obj.get("status")
    if transport["http_status"] == 200 and status in ("queued", "running", "succeeded", "failed", "cancelled"):
        state.update(status=status, last_polled_utc=now())
        if status == "succeeded":
            write_json(run / "completed-response.json", result)
    write_json(run / "state.json", state)
    return {"status": state["status"], **transport, "poll_index": index, "error": obj.get("error")}


def download(run):
    load_case(run)
    if (run / "native-video.mp4").exists():
        raise ValueError("Original video already retained")
    obj = task_body(read_json(run / "completed-response.json"))
    if obj.get("status") != "succeeded":
        raise ValueError("No succeeded video task")
    url = obj.get("content", {}).get("url", "")
    parsed = parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Output location must be an HTTPS URL without embedded credentials")
    # Deliberately no vendor Authorization/cookies on CDN requests; no redirects.
    tmp = run / "native-video.mp4.partial"
    try:
        with request.build_opener(NoRedirect).open(request.Request(url), timeout=60) as response, tmp.open("xb") as f:
            count = 0
            while chunk := response.read(1024 * 1024):
                count += len(chunk)
                if count > MAX_VIDEO:
                    raise ValueError("Video exceeded retention size limit")
                f.write(chunk)
        tmp.replace(run / "native-video.mp4")
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    data = (run / "native-video.mp4").read_bytes()
    receipt = {"retained_utc": now(), "bytes": len(data), "sha256": digest(data),
               "request_authorization_sent": False, "source_host": parsed.hostname,
               "redirects_followed": False, "video_semantics": "native provider file; container/codec not yet inspected"}
    write_json(run / "download-receipt.json", receipt)
    return {"status": "downloaded", "bytes": len(data), "sha256": digest(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "submit", "poll", "download"])
    parser.add_argument("run", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--prompt-file", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            if args.source is None or args.prompt_file is None:
                parser.error("prepare requires --source and --prompt-file")
            result = prepare(args.run.resolve(), args.source.resolve(), args.prompt_file.resolve())
        else:
            result = {"submit": submit, "poll": poll, "download": download}[args.command](args.run.resolve())
        print(json.dumps(result))
    except Exception as exc:
        # Do not echo raw urllib exceptions (which may contain signed CDN URLs).
        print(json.dumps({"status": "error", "type": type(exc).__name__, "details": "Inspect local state/receipts; no automatic retry was made"}))
        raise SystemExit(2)


if __name__ == "__main__":
    main()

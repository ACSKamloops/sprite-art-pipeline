"""Immutable byte/raster/document storage and atomic named publication."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from fractions import Fraction

import numpy as np

MAX_PIXELS = 16_777_216
MAX_FRAMES = 512
MAX_SEQUENCE_BYTES = 512 * 1024 * 1024
MAX_DOCUMENT_BYTES = 16 * 1024 * 1024


class ValidationError(ValueError):
    def to_dict(self):
        return {"status": "validation_error", "reason": str(self)}


class UnsupportedCapability(ValidationError):
    def __init__(self, capability, reason):
        self.capability, self.reason = str(capability), str(reason)
        super().__init__(f"{self.capability}: {self.reason}")

    def to_dict(self):
        return {"status": "unsupported", "capability": self.capability, "reason": self.reason}


def canonical_json(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    except (TypeError, ValueError) as e:
        raise ValidationError("Document must contain finite JSON values") from e


def digest(value: bytes):
    return hashlib.sha256(value).hexdigest()


def validate_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValidationError("Artifact ID must be a complete SHA256 digest")
    return value


def validate_raster(array):
    a = np.asarray(array)
    if a.dtype != np.uint8 or a.ndim != 3 or a.shape[2] != 4:
        raise ValidationError("Raster must be uint8[height,width,4]")
    h, w = a.shape[:2]
    if min(w, h) < 1 or w * h > MAX_PIXELS:
        raise ValidationError("Raster exceeds local pixel budget or is empty")
    return a


class Store:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.path.mkdir(parents=True, exist_ok=True)
        (self.path / "blobs").mkdir(exist_ok=True)
        self.db_path = self.path / "state.sqlite"
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE IF NOT EXISTS heads(name TEXT PRIMARY KEY, artifact TEXT NOT NULL)")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db_path, timeout=30)
        try:
            db.execute("PRAGMA busy_timeout=30000")
            with db:
                yield db
        finally:
            db.close()

    def put_bytes(self, value):
        if not isinstance(value, bytes):
            raise ValidationError("Blob must be immutable bytes")
        ident = digest(value)
        target = self.path / "blobs" / ident
        if target.exists():
            self.get_bytes(ident)
            return ident
        fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, target)
            except FileExistsError:
                self.get_bytes(ident)
        finally:
            Path(temporary).unlink(missing_ok=True)
        return ident

    def get_bytes(self, ident, *, max_bytes=None):
        validate_id(ident)
        if max_bytes is not None and (type(max_bytes) is not int or max_bytes < 0):
            raise ValidationError('Blob byte limit must be a nonnegative integer')
        try:
            path = self.path / "blobs" / ident
            if max_bytes is None:
                raw = path.read_bytes()
            else:
                if path.stat().st_size > max_bytes:
                    raise ValidationError('Artifact exceeds requested byte budget')
                with path.open('rb') as stream:
                    raw = stream.read(max_bytes+1)
                if len(raw) > max_bytes:
                    raise ValidationError('Artifact exceeds requested byte budget')
        except FileNotFoundError as e:
            raise ValidationError(f"Missing artifact {ident}") from e
        if digest(raw) != ident:
            raise ValidationError(f"Artifact integrity failed: {ident}")
        return raw

    def put_json(self, value):
        if not isinstance(value, dict):
            raise ValidationError("Document must be a JSON object")
        raw = canonical_json(value)
        if len(raw) > MAX_DOCUMENT_BYTES:
            raise ValidationError("JSON document exceeds local byte budget")
        return self.put_bytes(raw)

    def get_json(self, ident):
        try:
            raw = self.get_bytes(ident, max_bytes=MAX_DOCUMENT_BYTES)
            if len(raw) > MAX_DOCUMENT_BYTES:
                raise ValidationError("JSON document exceeds local byte budget")
            value = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as e:
            raise ValidationError("Artifact is not a JSON document") from e
        if not isinstance(value, dict):
            raise ValidationError("Artifact is not a JSON object")
        canonical_json(value)  # Reject parsed NaN/Infinity and overflowed1e999 recursively.
        return value

    def put_raster(self, array):
        a = validate_raster(array)
        h, w = a.shape[:2]
        raw_id = self.put_bytes(a.tobytes(order="C"))
        return self.put_json({"kind": "rgba", "version": 1, "width": w, "height": h, "raw_sha256": raw_id, "blob": raw_id})

    def get_raster(self, ident, *, expected_size=None):
        meta = self.get_json(ident)
        required = {"width", "height", "blob", "raw_sha256"}
        if meta.get("kind") != "rgba" or type(meta.get("version")) != int or meta["version"] != 1 or required - set(meta):
            raise ValidationError("Expected RGBA artifact")
        w, h = meta["width"], meta["height"]
        if type(w) != int or type(h) != int or min(w, h) < 1 or w * h > MAX_PIXELS:
            raise ValidationError("Invalid raster dimensions")
        if expected_size is not None and [w, h] != expected_size:
            raise ValidationError("Frame/canvas dimensions differ")
        raw = self.get_bytes(meta["blob"], max_bytes=w*h*4)
        if len(raw) != w * h * 4 or digest(raw) != meta["raw_sha256"]:
            raise ValidationError("RGBA dimensions/hash disagree with bytes")
        return np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)

    def get_head(self, name):
        with self.connect() as db:
            row = db.execute("SELECT artifact FROM heads WHERE name=?", (name,)).fetchone()
        return row[0] if row else None

    def set_head(self, name, ident, expected):
        if not isinstance(name, str) or not name or len(name) > 256:
            raise ValidationError("Head name must be a nonempty bounded string")
        self.get_bytes(ident)
        if expected is not None:
            validate_id(expected)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT artifact FROM heads WHERE name=?", (name,)).fetchone()
            previous = row[0] if row else None
            if previous != expected:
                db.rollback()
                return False
            db.execute("INSERT INTO heads VALUES(?,?) ON CONFLICT(name) DO UPDATE SET artifact=excluded.artifact", (name, ident))
            db.commit()
        return True


def save_sequence(store, arrays, durations=None, pivots=None, loop=False, directions=None, metadata=None, play_count=None):
    arrays = list(arrays)
    if not arrays or len(arrays) > MAX_FRAMES:
        raise ValidationError("Sequence must have1..512 ordered frames")
    shape = validate_raster(arrays[0]).shape
    if sum(a.nbytes for a in arrays) > MAX_SEQUENCE_BYTES:
        raise ValidationError("Sequence exceeds local byte budget")
    if any(validate_raster(a).shape != shape for a in arrays):
        raise ValidationError("Sequence frame dimensions differ")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValidationError("Sequence metadata must be an object")
    canonical_json(metadata or {})
    n = len(arrays)
    durations = list(durations) if durations is not None else [Fraction(1, 12)] * n
    pivots = list(pivots) if pivots is not None else [(0, 0)] * n
    directions = list(directions) if directions is not None else ["unspecified"] * n
    if len(durations) != n or len(pivots) != n or len(directions) != n:
        raise ValidationError("Frame metadata count differs")
    if type(loop) != bool:
        raise ValidationError("Loop must be boolean")
    play_count = (0 if loop else 1) if play_count is None else play_count
    if type(play_count) != int or not 0 <= play_count <= 65536 or (play_count == 0) != loop:
        raise ValidationError("Play count must agree with infinite-loop flag")
    records = []
    for i, (array, duration, pivot, direction) in enumerate(zip(arrays, durations, pivots, directions)):
        if isinstance(duration, bool):
            raise ValidationError("Frame duration cannot be boolean")
        try:
            duration = Fraction(*duration) if isinstance(duration, (list, tuple)) else Fraction(duration)
        except (TypeError, ValueError, ZeroDivisionError) as e:
            raise ValidationError("Invalid rational frame duration") from e
        if duration <= 0 or duration > 3600:
            raise ValidationError("Frame duration must be positive and <=3600seconds")
        if not isinstance(pivot, (list, tuple)) or len(pivot) != 2 or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in pivot):
            raise ValidationError("Pivot must have2finite numeric coordinates")
        if not isinstance(direction, str) or not direction:
            raise ValidationError("Direction must be explicit nonempty text")
        records.append({"index": i, "raster": store.put_raster(array), "duration": [duration.numerator, duration.denominator], "pivot": list(pivot), "direction": direction})
    return store.put_json({"kind": "sequence", "version": 1, "canvas": [shape[1], shape[0]], "frames": records,
                           "loop": loop, "play_count": play_count, "metadata": metadata or {}, "visual_approval": "unreviewed"})


def load_sequence(store, ident):
    doc = store.get_json(ident)
    if doc.get("kind") != "sequence" or type(doc.get("version")) != int or doc["version"] != 1 or not isinstance(doc.get("frames"), list) or not doc["frames"]:
        raise ValidationError("Expected nonempty sequence document")
    if len(doc["frames"]) > MAX_FRAMES or not isinstance(doc.get("canvas"), list) or len(doc["canvas"]) != 2:
        raise ValidationError("Invalid sequence shape")
    w, h = doc["canvas"]
    if type(w) != int or type(h) != int or min(w, h) < 1 or w*h > MAX_PIXELS or w*h*4*len(doc["frames"]) > MAX_SEQUENCE_BYTES:
        raise ValidationError("Sequence exceeds resource budget")
    if type(doc.get("loop")) != bool or not isinstance(doc.get("metadata"), dict):
        raise ValidationError("Invalid sequence loop/metadata")
    play_count = doc.get("play_count", 0 if doc["loop"] else 1)
    if type(play_count) != int or not 0 <= play_count <= 65536 or (play_count == 0) != doc["loop"]:
        raise ValidationError("Invalid sequence play count")
    for index, f in enumerate(doc["frames"]):
        if not isinstance(f, dict) or type(f.get("index")) != int or f["index"] != index:
            raise ValidationError("Frame indexes must be consecutive zero-based")
        duration = f.get("duration")
        if not isinstance(duration, list) or len(duration) != 2 or any(type(v) != int or v <= 0 for v in duration) or Fraction(*duration) > 3600:
            raise ValidationError("Invalid positive rational frame duration")
        pivot = f.get("pivot")
        if not isinstance(pivot, list) or len(pivot) != 2 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in pivot):
            raise ValidationError("Invalid frame pivot")
        if not isinstance(f.get("direction"), str) or not f["direction"]:
            raise ValidationError("Invalid frame direction")
        validate_id(f.get("raster"))
    # Enforce the declared aggregate canvas budget before reading each payload.
    # A forged small canvas must not retain larger rasters across all frames.
    arrays = [store.get_raster(f["raster"], expected_size=doc["canvas"]) for f in doc["frames"]]
    if any([a.shape[1], a.shape[0]] != doc["canvas"] for a in arrays):
        raise ValidationError("Frame/canvas dimensions differ")
    return doc, arrays

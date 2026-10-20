#!/usr/bin/env python3
"""Union rational pose boundaries without resampling any component track.

This schedules existing parts; it does not paint, register, mask, or approve them.
Each manifest uses frames[{file, sha256, hold:[numerator, denominator]}].
"""
import argparse
import hashlib
import json
from bisect import bisect_right
from fractions import Fraction
from math import lcm
from pathlib import Path


def rational(value):
    if (not isinstance(value, list) or len(value) != 2
            or any(type(x) is not int for x in value) or value[1] <= 0):
        raise ValueError("hold/duration must be [integer, positive integer]")
    return Fraction(*value)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def schedule(named_paths):
    tracks = {}
    periods = set()
    boundaries = {Fraction(0)}
    for name, path in named_paths:
        if not name or name in tracks:
            raise ValueError("component names must be nonempty and unique")
        path = Path(path).resolve()
        raw = path.read_bytes()
        data = json.loads(raw)
        frames = data.get("frames")
        if data.get("loop") is not True or not isinstance(frames, list) or not frames:
            raise ValueError(f"{name}: a nonempty explicitly looping track is required")
        starts, refs, cursor = [], [], Fraction(0)
        for position, frame in enumerate(frames):
            hold = rational(frame["hold"])
            if hold <= 0:
                raise ValueError(f"{name}: every hold must be positive")
            source = (path.parent / frame["file"]).resolve()
            actual = digest(source)
            if actual != frame["sha256"]:
                raise ValueError(f"{name}: stale source frame {position}")
            starts.append(cursor)
            boundaries.add(cursor)
            refs.append({"position": position, "file": str(source), "sha256": actual})
            cursor += hold
        if "duration" in data and rational(data["duration"]) != cursor:
            raise ValueError(f"{name}: declared duration differs from its holds")
        periods.add(cursor)
        tracks[name] = {"manifest": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                        "starts": starts, "frames": refs}
    if not tracks or len(periods) != 1:
        raise ValueError("all component tracks must have the same positive cycle period")
    period = periods.pop()
    boundaries.add(period)
    edges = sorted(boundaries)
    hz = lcm(*(edge.denominator for edge in edges))
    states = []
    for begin, end in zip(edges, edges[1:]):
        ticks, hold = begin * hz, (end - begin) * hz
        assert ticks.denominator == hold.denominator == 1 and hold > 0
        owners = {name: track["frames"][bisect_right(track["starts"], begin) - 1]["position"]
                  for name, track in tracks.items()}
        states.append({"start_tick": int(ticks), "duration_ticks": int(hold),
                       "hold": [(end-begin).numerator, (end-begin).denominator],
                       "components": owners})
    for track in tracks.values():
        track["starts"] = [[x.numerator, x.denominator] for x in track["starts"]]
    return {"scope": "exact component-clock union only; no art or masking approval",
            "clock_hz": hz, "cycle_ticks": int(period * hz),
            "duration": [period.numerator, period.denominator],
            "tracks": tracks, "states": states}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", action="append", required=True, metavar="NAME=MANIFEST")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        pairs = [entry.split("=", 1) for entry in args.track]
        if any(len(pair) != 2 for pair in pairs):
            raise ValueError("--track requires NAME=MANIFEST")
        result = schedule(pairs)
        payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        with args.output.open("x") as stream:
            stream.write(payload)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"{error}\n")
    print(f"{len(result['states'])} states, {result['cycle_ticks']} ticks at {result['clock_hz']}Hz")


if __name__ == "__main__":
    main()

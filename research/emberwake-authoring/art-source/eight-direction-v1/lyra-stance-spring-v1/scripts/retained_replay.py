"""Local frozen-map reconstruction, independent of the editor renderer."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "retained-source"
ART = SOURCE / "waist-completion-v1"
LAYERS = ("undercoat", "fixed_lower", "cloth_a", "cloth_b", "body")
CHANGED_PHASES = (0, 1, 2, 4, 5, 6)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def normal_over(back, front):
    result = back.copy()
    for y, x in np.argwhere(front[..., 3] > 0):
        sr, sg, sb, sa = map(int, front[y, x])
        dr, dg, db, da = map(int, back[y, x])
        n = sa * 255 + da * (255 - sa)
        result[y, x] = [(s * sa * 255 + d * da * (255 - sa) + n // 2) // n for s, d in ((sr, dr), (sg, dg), (sb, db))] + [(n + 127) // 255]
    return result


def map_layer(source, path):
    data = np.load(path)
    result = np.zeros_like(source)
    for y, x in np.argwhere(data["owner"]):
        xx, yy = map(int, data["source_xy"][y, x])
        assert 0 <= xx < 128 and 0 <= yy < 128
        result[y, x] = source[yy, xx]
    return result


def read_components():
    """Read retained owners/maps, reconstruct every component and baseline."""
    receipt = json.loads((ART / "REBUILD-RECEIPT.json").read_text())
    journal = json.loads((ART / "UNDERCOAT-LITERAL-JOURNAL.json").read_text())
    approved = json.loads((ROOT / "ROOT-FROZEN-INPUT.json").read_text())
    result = []
    for phase in receipt["phases"]:
        i = phase["phase"]
        source = rgba(SOURCE / f"inputs/current/{i:02}.png")
        final = {name: np.zeros_like(source) for name in LAYERS}
        initial = {name: np.zeros_like(source) for name in LAYERS}
        body_owner = np.array(Image.open(ART / f"masks/{i:02}-body-source-owner.png").convert("L")) > 0
        initial["body"][body_owner] = source[body_owner]
        final["body"] = map_layer(source, ART / f"maps/{i:02}-body.npz")
        assert np.array_equal(final["body"], rgba(ART / f"layers/{i:02}-body-rigid.png"))
        dy = receipt["correction"][i]
        bodymap = np.load(ART / f"maps/{i:02}-body.npz")
        for y, x in np.argwhere(bodymap["owner"]):
            assert bodymap["source_xy"][y, x].tolist() == [int(x), int(y) - dy]
        final["fixed_lower"] = map_layer(source, ART / f"maps/{i:02}-fixed-lower.npz")
        assert np.array_equal(final["fixed_lower"], rgba(ART / f"layers/{i:02}-fixed-lower.png"))
        initial["fixed_lower"] = final["fixed_lower"].copy()
        for number, part in enumerate(phase["parts"]):
            assert number < 2
            name = part["name"]
            layer = "cloth_a" if number == 0 else "cloth_b"
            mutable = np.array(Image.open(ART / f"masks/{i:02}-{name}-mutable-source-owner.png").convert("L")) > 0
            assert not np.any(mutable & body_owner)
            initial[layer][mutable] = source[mutable]
            final[layer] = map_layer(source, ART / f"maps/{i:02}-{name}.npz")
            assert np.array_equal(final[layer], rgba(ART / f"layers/{i:02}-{name}-mapped-cloth.png"))
            core = np.array(Image.open(ART / f"masks/{i:02}-{name}-literal-source-core.png").convert("L")) > 0
            mapping = np.load(ART / f"maps/{i:02}-{name}.npz")
            for y, x in np.argwhere(mapping["owner"]):
                xx, yy = mapping["source_xy"][y, x]
                assert core[yy, xx]
        entries = [entry for entry in journal["edits"] if entry["phase"] == i]
        upstream = np.load(SOURCE / f"inputs/upstream/maps/{i:02}-source.npz")
        for entry in entries:
            x, y = entry["at"]
            xx, yy = entry["source_at"]
            assert entry["source_phase"] == i
            assert source[yy, xx].tolist() == entry["new_rgba"]
            assert source[y, x].tolist() == entry["source_body_original_rgba"]
            assert int(upstream["layer_id"][y, x]) == 0
            final["undercoat"][y, x] = entry["new_rgba"]
        assert np.array_equal(final["undercoat"], rgba(ART / f"layers/{i:02}-new-authored-undercoat.png"))
        baseline = np.zeros_like(source)
        target = np.zeros_like(source)
        for layer in LAYERS:
            baseline = normal_over(baseline, initial[layer])
            target = normal_over(target, final[layer])
        assert np.array_equal(baseline, source)
        expected = ART / f"frames/{i:02}.png"
        assert sha(expected) == approved["approved_frames"][i]["sha256"]
        assert np.array_equal(target, rgba(expected))
        assert np.array_equal(target[94:], source[94:])
        result.append({"phase": i, "initial": initial, "final": final, "source": source,
                       "target": target, "undercoat_entries": entries})
    assert sum(len(phase["undercoat_entries"]) for phase in result) == 38
    return result


def write_source_replay(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    components = read_components()
    rows = []
    for phase in components:
        i = phase["phase"]
        destination = directory / f"{i:02}.png"
        Image.fromarray(phase["target"]).save(destination)
        assert destination.read_bytes() == (ART / f"frames/{i:02}.png").read_bytes()
        rows.append({"phase": i, "PNG_bytes_exact": True, "RGBA_exact": True, "sha256": sha(destination)})
    return components, rows

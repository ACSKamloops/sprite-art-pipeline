"""Executable replay recipe checks, not private-service or aesthetic acceptance."""
from fractions import Fraction
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import Store, ValidationError, load_sequence
from sprite_workbench.export import import_editable
from sprite_workbench.raster import edit_sequence, paste, crop
from sprite_workbench.terrain import render_map, reblit_regions
from sprite_workbench.assets import render_text
from sprite_workbench.replay_methods import FLOW_IDS, run_flow


@pytest.fixture
def replay(tmp_path):
    def invoke(flow):
        store = Store(tmp_path / "stores" / flow)
        out = tmp_path / "flows" / flow
        receipt = run_flow(flow, store, out)
        return store, out, receipt
    return invoke


@pytest.mark.parametrize("flow", FLOW_IDS)
def test_receipt_checks_exports_and_fresh_editable_import(replay, tmp_path, flow):
    store, out, receipt = replay(flow)
    assert json.loads((out / "receipt.json").read_text()) == receipt
    assert json.loads(json.dumps(receipt, allow_nan=False)) == receipt
    assert receipt["flow_id"] == flow
    assert all(c["passed"] is True for c in receipt["checks"]), receipt["checks"]
    assert len(receipt["checks"]) >= 10
    assert any("negative:" in step for step in receipt["routine_order"])
    assert receipt["routine_order"][-1].startswith("write JSON-safe receipt")
    assert receipt["limitations"] and receipt["inputs"]["capability"] == "supplied-art"
    for name, ident in receipt["artifacts"].items():
        assert len(ident) == 64 and store.get_bytes(ident), name
    for name, report in receipt["exports"].items():
        directory = out / report["directory"]
        fresh = Store(tmp_path / "independent-import" / flow / name)
        ident = import_editable(fresh, directory / "editable")
        before, a = load_sequence(store, ident)
        after, b = load_sequence(fresh, ident)
        assert before == after
        assert len(a) == len(b) and all(np.array_equal(x, y) for x, y in zip(a, b))
        assert receipt["reviews"][name]["continuous_motion_viewed"] is False
        review = json.loads((directory / "review" / "review.json").read_text())
        assert review["diagnostic_coverage"]["ordered_frames"] == len(a)
        assert review["visual_acceptance"] == "unreviewed"
        assert len(review["pairs"]) == len(a)
        manifest = json.loads((directory / "manifest.json").read_text())
        assert manifest["total"] == review["total"]
        for i, array in enumerate(a):
            with Image.open(directory / "frames" / f"frame-{i:04d}.png") as im:
                np.testing.assert_array_equal(np.asarray(im.convert("RGBA")), array)


@pytest.mark.parametrize("flow", FLOW_IDS)
def test_fresh_replays_bind_same_inputs_and_artifact_ids(tmp_path, flow):
    receipts = [run_flow(flow, Store(tmp_path / f"store-{i}"), tmp_path / f"output-{i}") for i in range(2)]
    assert receipts[0] == receipts[1]  # No timestamps, paths, randomized fixture or font lookup in receipt.


def test_f01_reconstructs_edit_and_paste_decisions_after_closure_import(replay, tmp_path):
    _, out, r = replay("F01")
    fresh = Store(tmp_path / "F01-proof")
    ident = import_editable(fresh, out / "exports" / "result" / "editable")
    doc, final = load_sequence(fresh, ident)
    edited_id = doc["metadata"]["parent_sequence"]
    edited_doc, edited_frames = load_sequence(fresh, edited_id)
    parent = edited_doc["metadata"]["parent_sequence"]
    recreated = edit_sequence(fresh, parent, r["inputs"]["edit_changes"])
    assert recreated["sequence"] == edited_id
    pasted = r["artifacts"]["pasted_raster"]
    decision = fresh.get_json(fresh.get_json(pasted)["metadata"]["paste_decision"])
    packet = crop(fresh, decision["parent_raster"], decision["region"], node=decision["node"])
    reproduced = paste(fresh, packet, fresh.get_raster(decision["patch"]).tolist(),
                       expected=decision["guard"], stamp=decision["stamp"])
    assert reproduced == pasted
    assert final[0][1, 2].tolist() == [61, 62, 63, 0]
    assert final[0][1, 3].tolist() == [18, 108, 144, 255]  # Copy sampled original, then map.
    assert final[0][1, 4].tolist() == [209, 34, 61, 255]  # Protected marker.
    assert r["exports"]["result"]["formats"]["gif"]["capability"] == "gif-alpha"
    np.testing.assert_array_equal(edited_frames[0][0, 6], [91, 92, 93, 0])


def test_f03_distinct_domains_compatibility_and_explicit_motion_clock(replay):
    store, _, r = replay("F03")
    audit = store.get_json(r["artifacts"]["pose_diagnostic"])
    assert audit["lua"][0]["depth"] == pytest.approx(.1)
    assert audit["godot"][0]["depth"] == pytest.approx(-.1)
    assert audit["normalized_fit"]["examined"] == 72
    assert audit["pixel_fit"]["examined"] == 144
    assert audit["compatibility"]["states"][0]["matched_terms"] == 0
    assert audit["corrected"]["states"][0]["tilt_degrees"] == 25
    doc, arrays = load_sequence(store, r["artifacts"]["sequence"])
    assert [f["duration"] for f in doc["frames"]] == [[1, 30], [1, 15], [2, 15]]
    assert all(f["pivot"] == [3, 4] and f["direction"] == "north" for f in doc["frames"])
    np.testing.assert_array_equal(arrays[0], arrays[1])
    np.testing.assert_array_equal(arrays[2], arrays[0][::-1])
    boundary = next(c for c in r["checks"] if c["name"] == "learned motion explicitly unavailable")
    assert boundary["detail"]["status"] == "unsupported"


def test_f06_recipe_and_masked_patch_rebuild_from_fresh_import(replay, tmp_path):
    _, out, r = replay("F06")
    fresh = Store(tmp_path / "F06-proof")
    seq = import_editable(fresh, out / "exports" / "result" / "editable")
    doc, arrays = load_sequence(fresh, seq)
    recipe = fresh.get_json(doc["metadata"]["terrain_recipe"])
    cells = {c["key"]: fresh.get_raster(c["raster"]) for c in recipe["cells"]}
    baseline = render_map(cells, np.array(recipe["layout"], np.int16))
    patch = doc["metadata"]["region_patches"][0]
    rebuilt, _ = reblit_regions(baseline, [{"array": fresh.get_raster(patch["raster"]),
        "expected": fresh.get_raster(patch["expected"]), "origin": patch["origin"],
        "mask": fresh.get_raster(patch["mask"])[..., 3] != 0}])
    np.testing.assert_array_equal(rebuilt, arrays[0])
    assert recipe["layout"] == [[2, 12, -1], [-1, 3, 8]]
    assert not baseline[:5, 14:].any()
    assert arrays[0][1, 1].tolist() == [90, 10, 40, 255]
    assert arrays[0][2, 2].tolist() == [70, 60, 50, 127]
    np.testing.assert_array_equal(arrays[0][1, 2], baseline[1, 2])


def test_f07_preparation_source_and_final_mask_are_distinct(replay, tmp_path):
    _, out, r = replay("F07")
    fresh = Store(tmp_path / "F07-proof")
    seq = import_editable(fresh, out / "exports" / "result" / "editable")
    doc, frames = load_sequence(fresh, seq)
    gd = fresh.get_json(doc["metadata"]["preparation"])
    lu = fresh.get_json(r["artifacts"]["lua_preparation"])
    original_mask = fresh.get_raster(gd["source_mask"])
    final_mask = fresh.get_raster(gd["mask"])
    assert original_mask.shape == (5, 7, 4) and final_mask.shape == (6, 10, 4)
    assert original_mask[0, 6].tolist() == [33, 44, 55, 1]
    assert final_mask[1, 7].tolist() == [0, 0, 0, 255]
    assert frames[0][1, 7].tolist() == [0, 0, 0, 0]
    assert frames[1][1, 7].tolist() == [91, 92, 93, 0]
    assert gd["source_mask_format"] == {"shape": [5, 7, 4], "dtype": "uint8", "packing": "rgba"}
    assert lu["reference_roles"] == ["style", "subject"]
    assert [op["op"] for op in gd["operations"]] == ["crop-pad", "nearest-resize", "center-pad",
        "zero-hidden-rgb", "binary-mask", "reference", "reference"]
    assert doc["metadata"]["widget_choices"]["custom_unchanged"] is None
    assert all(x["remote_transformation"] == "unsupported" for x in doc["metadata"]["prompt_descriptors"])


def test_f08_explicit_glyphs_rebuild_and_codepoint_holds(replay, tmp_path):
    _, out, r = replay("F08")
    fresh = Store(tmp_path / "F08-proof")
    final = import_editable(fresh, out / "exports" / "result" / "editable")
    text = render_text(fresh, r["artifacts"]["glyph_atlas"], "AB A", [18, 12], baseline=[2, 7])
    assert text == r["artifacts"]["text_sequence"]
    atlas = fresh.get_json(r["artifacts"]["glyph_atlas"])
    assert set(atlas["glyphs"]) == {"A", "B", " "}
    assert "font_source" not in atlas  # This fixture uses supplied glyphs, no ambient TTF.
    mouth, frames = load_sequence(fresh, r["artifacts"]["viseme_sequence"])
    assert mouth["metadata"]["symbols"] == ["on", "on", "off", "narrow"]
    assert len(frames) == 4 and mouth["frames"][0]["raster"] == mouth["frames"][1]["raster"]
    doc, composed = load_sequence(fresh, final)
    assert sum((Fraction(*f["duration"]) for f in doc["frames"]), Fraction()) == Fraction(7, 10)
    assert len(composed) == 4 and doc["play_count"] == 1
    assert composed[0][9, 13].tolist() == [240, 90, 30, 255]
    assert composed[0][3, 3].tolist() == [230, 210, 70, 255]  # Supplied A ink.


@pytest.mark.parametrize("invalid", ["F00", "f01", 1, None])
def test_unknown_flow_rejects_without_output(tmp_path, invalid):
    store = Store(tmp_path / "store")
    out = tmp_path / "must-not-exist"
    with pytest.raises(ValidationError):
        run_flow(invalid, store, out)
    assert not out.exists() and not list((store.path / "blobs").iterdir())


def test_existing_and_symlink_outputs_are_preserved(tmp_path):
    store = Store(tmp_path / "store")
    existing = tmp_path / "existing"
    existing.mkdir()
    (existing / "keep").write_text("user content")
    with pytest.raises(ValidationError):
        run_flow("F07", store, existing)
    assert (existing / "keep").read_text() == "user content"
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ValidationError):
        run_flow("F07", store, empty)
    link = tmp_path / "dangling"
    link.symlink_to(tmp_path / "absent-target")
    with pytest.raises(ValidationError):
        run_flow("F07", store, link)
    assert link.is_symlink() and not link.exists()


def test_output_failure_cleans_stage_but_does_not_claim_store_rollback(tmp_path, monkeypatch):
    import sprite_workbench.replay_methods as module
    store = Store(tmp_path / "store")
    out = tmp_path / "failed"
    def fail_export(*args, **kwargs):
        raise ValidationError("deliberate export failure")
    monkeypatch.setattr(module, "export_sequence", fail_export)
    with pytest.raises(ValidationError, match="deliberate export"):
        run_flow("F01", store, out)
    assert not out.exists()
    assert not list(tmp_path.glob(".failed-pending-*"))
    assert store.get_head("replay/F01") is not None  # Explicit earlier diagnostic CAS persists.


@pytest.mark.parametrize("flow,expected", [
    ("F01", {"protected edit rejects without advancing head": "Trusted protected pixels touched",
             "incorrect crop guard rejects": "Local crop/source/node guard failed"}),
    ("F03", {"Lua fit requires explicit canvas": "Lua fitting requires positive integer pixel canvas",
             "duplicate label rejected": "Joint labels must be nonempty and unique",
             "nonfinite joint rejected": "Pose values must be finite numbers"}),
    ("F06", {"later reblit guard fails atomically": "Region expected-byte guard failed",
             "missing supplied tile fails": "Missing supplied cells"}),
    ("F07", {"Lua interpolation requires end": "This interpolation adapter requires an end frame",
             "Godot strength zero outside widget range": "Strength is outside widget range",
             "reference role cardinality rejected": "Each reference must have an explicit valid role"}),
    ("F08", {"missing glyph coverage rejects": "Missing explicit glyph coverage",
             "UI piece outside pixel canvas rejects": "UI piece exceeds canvas",
             "unmapped lowercase codepoint rejects": "Missing supplied viseme"}),
])
def test_negative_controls_hit_declared_failure_reason(replay, flow, expected):
    _, _, receipt = replay(flow)
    checks = {c["name"]: c for c in receipt["checks"]}
    for name, message in expected.items():
        assert checks[name]["passed"] is True
        assert checks[name]["detail"]["error"] == "ValidationError"
        assert message in checks[name]["detail"]["message"]

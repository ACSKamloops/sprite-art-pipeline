"""Package the exactly approved 17-pixel old-glove cleanup in a real editor transaction."""
from pathlib import Path
import copy
import hashlib
import json

from PIL import Image
from sprite_lab import (
    History, EditError, canonical_json, project_hash, cel_hash,
    candidate_transaction, render_cel, render_frame, export_project,
)

P = Path(__file__).resolve().parents[1]


def image(name):
    return Image.open(P / name).convert("RGBA")


def sha(name):
    return hashlib.sha256((P / name).read_bytes()).hexdigest()


def write(name, value):
    (P / name).write_text(canonical_json(value) + "\n")


def main():
    literal = json.loads((P / "journal/03-literal-erasure.json").read_text())
    assert sha("inputs/current/03.png") == literal["input_sha256"]
    assert sha("candidate/03.png") == literal["output_sha256"]
    allowed = [edit["at"] for edit in literal["edits"]]
    assert len(allowed) == len(set(map(tuple, allowed))) == 17
    palette = [[0, 0, 0, 0]]
    lookup = {(0, 0, 0, 0): 0}
    cels, frames = {}, []
    for phase in range(8):
        pixels = []
        for rgba in image(f"inputs/current/{phase:02}.png").getdata():
            if rgba not in lookup:
                lookup[rgba] = len(palette)
                palette.append(list(rgba))
            pixels.append(lookup[rgba])
        cel_id = f"lyra-se-{phase:02}"
        cels[cel_id] = {"layer_id": "paint", "pixels": pixels}
        frames.append({"id": f"{phase:02}", "duration_ticks": 9,
                       "cels": {"paint": cel_id}, "landmarks": {"pivot": [64, 112]}})
    initial = {
        "schema": "sprite-edit-project/v1",
        "canvas": {"width": 128, "height": 128, "render_pivot": [64, 112], "ground_pivot": [64, 112]},
        "palette": palette, "layers": [{"id": "paint", "name": "Lyra SE current05 path plus bounded03 old-glove cleanup", "locked": False}],
        "cels": cels, "frames": frames,
        "animations": [{"id": "lyra-SE-walk", "frames": [f"{i:02}" for i in range(8)], "fps": 160, "loop": True, "events": []}],
        "provenance": {
            "scope": "Exactly17 changed pixels:16 erasures and1 source hip restoration; root approved compact proof; no other shape or motion change",
            "source_bank_png_sha256": [sha(f"inputs/current/{i:02}.png") for i in range(8)],
            "literal_source_witness": "journal/03-literal-erasure.json",
            "source_ownership_finding": "OWNERSHIP-FINDING.md", "generation_calls": 0,
            "editor_layers": "Full raster cels; source owners and maps retained in inputs; no anatomical rig claim",
            "art_score": None, "motion_improvement_claim": False,
        },
    }
    h = History(initial)
    tx = candidate_transaction(initial, "lyra-se-03", image("candidate/03.png"), allowed,
        reason="Exactly approved17-pixel cleanup of source02 old-glove contour/halo wrongly sampled by mapped left-leg owner; restore one retained source hip texel")
    receipt = h.apply(tx)
    assert len(h.records) == 1
    final = copy.deepcopy(h.project)
    journal = h.journal()
    initialhash, finalhash = project_hash(initial), project_hash(final)
    assert set(receipt["diff"]["frames"]) == {"03"}
    assert receipt["diff"]["frames"]["03"]["changed_pixels"] == 17
    assert sorted(receipt["diff"]["frames"]["03"]["coordinates"]) == sorted(allowed)
    for i in range(8):
        assert render_cel(final, f"lyra-se-{i:02}").tobytes() == image(f"candidate/{i:02}.png").tobytes()
        assert render_frame(final, f"{i:02}").tobytes() == image(f"candidate/{i:02}.png").tobytes()
    h.undo()
    assert project_hash(h.project) == initialhash
    h.redo()
    assert project_hash(h.project) == finalhash
    assert project_hash(History.replay(initial, journal).project) == finalhash

    rejection = []

    def reject(name, action, active):
        oldproject = canonical_json(active.project)
        oldjournal = canonical_json(active.journal())
        try:
            action()
        except EditError as error:
            assert canonical_json(active.project) == oldproject
            assert canonical_json(active.journal()) == oldjournal
            rejection.append({"case": name, "rejected": True, "project_and_journal_unchanged": True, "error": str(error)})
        else:
            raise AssertionError(f"Negative case accepted: {name}")

    # Each failure acts on a live History and verifies both project and journal atomicity.
    staleproject = copy.deepcopy(tx)
    staleproject["expected_project_sha256"] = "0" * 64
    scratch = History(initial)
    reject("stale project precondition", lambda: scratch.apply(staleproject), scratch)
    stalecel = copy.deepcopy(tx)
    next(op for op in stalecel["operations"] if op["op"] == "candidate_patch")["expected_cel_sha256"] = "0" * 64
    # A preceding valid palette mutation must also roll back when a later cel check fails.
    stalecel["operations"].insert(0, {"op": "palette_add", "rgba": [1, 2, 3, 4]})
    scratch = History(initial)
    reject("stale cel precondition after staged palette add", lambda: scratch.apply(stalecel), scratch)
    badimage = image("candidate/03.png")
    badimage.putpixel((64, 40), (255, 0, 170, 255))
    scratch = History(initial)
    reject("candidate RGBA outside literal17 owner", lambda: candidate_transaction(scratch.project, "lyra-se-03", badimage, allowed), scratch)
    outside = copy.deepcopy(tx)
    patch = next(op for op in outside["operations"] if op["op"] == "candidate_patch")
    index = 40 * 128 + 64
    patch["candidate_pixels"][index] = (patch["candidate_pixels"][index] + 1) % len(initial["palette"])
    outside["operations"].insert(0, {"op": "palette_add", "rgba": [1, 2, 3, 4]})
    scratch = History(initial)
    reject("indexed patch outside literal17 owner after staged palette add", lambda: scratch.apply(outside), scratch)

    for name, data in (("initial", initial), ("final", final), ("journal", journal), ("03-transaction", tx), ("03-transaction-receipt", receipt)):
        write(f"projects/{name}.json", data)
    write("projects/03-owner-mask.json", allowed)
    exportmanifest = export_project(final, P / "exports")
    comparisons = []
    for i, entry in enumerate(exportmanifest["frames"]):
        exportpath = f'exports/{entry["png"]}'
        sourcepath = f"candidate/{i:02}.png"
        assert image(exportpath).tobytes() == image(sourcepath).tobytes()
        comparisons.append({"phase": i, "candidate_png_sha256": sha(sourcepath),
                            "editor_png_sha256": sha(exportpath),
                            "candidate_rgba_sha256": hashlib.sha256(image(sourcepath).tobytes()).hexdigest(),
                            "editor_rgba_sha256": hashlib.sha256(image(exportpath).tobytes()).hexdigest(),
                            "decoded_png_RGBA_exact": True, "PNG_encoding_bytes_exact": sha(sourcepath) == sha(exportpath)})
    checks = {
        "status": "PASS one real guarded editor transaction; exact approved17-pixel old-glove cleanup only",
        "initial_project_sha256": initialhash, "final_project_sha256": finalhash,
        "source03_cel_sha256": cel_hash(initial, "lyra-se-03"),
        "actual_guarded_transactions": 1, "actual_changed_RGBA_pixels": 17,
        "literal_owner_coordinates": allowed, "all8_source_editor_decoded_PNG_RGBA_exact": True,
        "all8_cel_and_composited_frame_RGBA_exact": True,
        "PNG_encoding_note": "Toolkit export uses compress_level9; source candidates use their retained original PNG encoding. Decoded RGBA is exact; file hashes are recorded separately.",
        "other7_source_PNG_bytes_exact": all(sha(f"candidate/{i:02}.png") == sha(f"inputs/current/{i:02}.png") for i in range(8) if i != 3),
        "undo_exact": True, "redo_exact": True, "journal_replay_exact": True,
        "atomic_rejections": rejection, "PNG_RGBA_comparisons": comparisons,
        "external_GUI_tested": False, "runtime_tested": False, "generation_calls": 0,
        "art_score": None, "motion_improvement_claim": False,
    }
    write("projects/EDITOR-RECEIPT.json", checks)
    print(json.dumps({key: value for key, value in checks.items() if key not in ("literal_owner_coordinates", "PNG_RGBA_comparisons")}, indent=2))


if __name__ == "__main__":
    main()

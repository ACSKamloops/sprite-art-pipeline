"""Actual guarded atomic component-cel transaction, without new artwork."""
from pathlib import Path
import copy
import json

import numpy as np
from PIL import Image
from sprite_lab import (
    History, EditError, canonical_json, project_hash, cel_hash,
    candidate_transaction, render_cel, export_project, export_aseprite,
)
from sprite_lab.core import render_frames
from retained_replay import ROOT, ART, LAYERS, CHANGED_PHASES, sha, rgba, write_source_replay
COMPONENT = ROOT / "component-editor"


def write(name, data):
    (COMPONENT / name).write_text(canonical_json(data) + "\n")


def assert_rejection(history, action, name):
    before = canonical_json(history.project)
    journal = canonical_json(history.journal())
    try:
        action()
    except EditError as error:
        assert canonical_json(history.project) == before
        assert canonical_json(history.journal()) == journal
        return {"case": name, "rejected": True, "project_and_history_unchanged": True, "error": str(error)}
    raise AssertionError(f"Negative case accepted: {name}")


def main():
    components, rawrows = write_source_replay(ROOT / "verification/raw-source-map-v1")
    palette = [[0,0,0,0]]
    lookup = {(0,0,0,0): 0}
    initial_cels = {}
    frames = []
    for phase in components:
        i = phase["phase"]
        bindings = {}
        for layer in LAYERS:
            indices = []
            for color in map(tuple, phase["initial"][layer].reshape(-1,4).tolist()):
                if color not in lookup:
                    lookup[color] = len(palette)
                    palette.append(list(color))
                indices.append(lookup[color])
            cel_id = f"lyra-se-{i:02}-{layer}"
            bindings[layer] = cel_id
            initial_cels[cel_id] = {"layer_id": layer, "pixels": indices}
        frames.append({"id": f"{i:02}", "duration_ticks": 9, "cels": bindings,
                       "landmarks": {"pivot": [64,112]}})
    names = {
        "undercoat": "Explicit new shaded undercoat - 38 literal pixels",
        "fixed_lower": "Retained lower paint, boots, outlines and qualified side flap",
        "cloth_a": "Visible proximal charcoal A - retained integer source field",
        "cloth_b": "Visible proximal charcoal B - retained integer source field",
        "body": "Current visible head torso arms gloves - rigid translated raster",
    }
    initial = {
        "schema": "sprite-edit-project/v1",
        "canvas": {"width":128,"height":128,"render_pivot":[64,112],"ground_pivot":[64,112]},
        "palette": palette, "layers": [{"id":layer,"name":names[layer],"locked":layer=="fixed_lower"} for layer in LAYERS],
        "cels": initial_cels, "frames": frames,
        "animations": [{"id":"lyra-SE-walk","frames":[f"{i:02}" for i in range(8)],"fps":160,"loop":True,"events":[]}],
        "provenance": {
            "scope": "Exactly approved waist-completion eight PNGs, retained visible raster components; one guarded atomic multicel edit; no new art",
            "component_semantics": "Five ordinary RGBA paint layers with exact integer normal source-over; no hidden anatomy, bone rig or full garment master claim",
            "initial_body_curve":[0,1,1,0,0,1,1,0],"final_body_curve":[1,0,-1,0,1,0,-1,0],
            "body_correction":[1,-1,-2,0,1,-1,-2,0],
            "source_and_maps":"retained-source/waist-completion-v1",
            "literal_undercoat":"retained-source/waist-completion-v1/UNDERCOAT-LITERAL-JOURNAL.json",
            "literal_owners":"retained-source/literal-owner-prep/LITERAL-ROWS.json",
            "new_authored_undercoat_pixels":38,"complete_hidden_boot_or_garment_master_claim":False,
            "unknown_00_01_sideflap":"Retained fixed and qualified; no complete garment ownership claim",
            "approved_png_sha256":[sha(ART/f"frames/{i:02}.png") for i in range(8)],
            "model_calls":0,"canonical_writes":0,"new_art_changes_in_package":0,"score":None,
        },
    }
    ids = [f"{i:02}" for i in range(8)]
    initial_render = render_frames(initial, ids)
    for i, image in enumerate(initial_render):
        assert image.tobytes() == components[i]["source"].tobytes()
    operations, masks, changedcels = [], {}, []
    final_expected = {}
    for phase in components:
        i = phase["phase"]
        for layer in LAYERS:
            before, after = phase["initial"][layer], phase["final"][layer]
            cel_id = f"lyra-se-{i:02}-{layer}"
            final_expected[cel_id] = after
            if np.array_equal(before, after):
                continue
            assert i in CHANGED_PHASES and layer != "fixed_lower"
            if layer == "undercoat":
                coords = [entry["at"] for entry in phase["undercoat_entries"]]
            else:
                coords = [[int(x),int(y)] for y,x in np.argwhere((before[...,3]>0)|(after[...,3]>0))]
            allowed = np.zeros((128,128),bool)
            for x,y in coords:
                allowed[y,x] = True
            assert np.array_equal(before[~allowed], after[~allowed])
            candidate = candidate_transaction(initial, cel_id, Image.fromarray(after), coords,
                reason="Import exact approved source component through its literal source/target owner")
            # Every approved component reuses retained source RGBA, including
            # the explicitly new undercoat coverage's existing source swatches.
            assert all(op["op"] == "candidate_patch" for op in candidate["operations"])
            operations.extend(candidate["operations"])
            masks[cel_id] = coords
            changedcels.append({"cel_id":cel_id,"phase":i,"layer":layer,
                                "expected_cel_sha256":cel_hash(initial,cel_id),
                                "actual_changed_component_RGBA_pixels":int(np.any(before!=after,axis=2).sum())})
    transaction = {
        "schema":"sprite-edit-transaction/v1","expected_project_sha256":project_hash(initial),
        "reason":"One atomic multicel import of exact root-approved Lyra stance-spring components across six changed poses;38 declared undercoat pixels; no additional art",
        "operations":operations,
    }
    history = History(initial)
    receipt = history.apply(transaction)
    final = copy.deepcopy(history.project)
    journal = history.journal()
    finalhash = project_hash(final)
    assert set(receipt["diff"]["frames"]) == {f"{i:02}" for i in CHANGED_PHASES}
    assert receipt["diff"]["unchanged_frames"] == ["03","07"]
    final_render = render_frames(final, ids)
    rows = []
    for i,image in enumerate(final_render):
        assert image.tobytes() == components[i]["target"].tobytes()
        destination = COMPONENT / f"editor-render/{i:02}.png"
        image.save(destination)
        assert destination.read_bytes() == (ART/f"frames/{i:02}.png").read_bytes()
        for layer in LAYERS:
            cel_id = f"lyra-se-{i:02}-{layer}"
            assert render_cel(final,cel_id).tobytes() == final_expected[cel_id].tobytes()
        rows.append({"phase":i,"component_layers_RGBA_exact":True,"normal_composited_RGBA_exact":True,
                     "editor_render_PNG_bytes_exact":True,"sha256":sha(destination)})
    history.undo()
    assert project_hash(history.project)==project_hash(initial)
    history.redo()
    assert project_hash(history.project)==finalhash
    assert project_hash(History.replay(initial,journal).project)==finalhash
    negatives=[]
    stale=copy.deepcopy(transaction)
    stale["expected_project_sha256"]="0"*64
    scratch=History(initial)
    negatives.append(assert_rejection(scratch,lambda:scratch.apply(stale),"stale project precondition"))
    stalecel=copy.deepcopy(transaction)
    stalecel["operations"][len(operations)//2]["expected_cel_sha256"]="0"*64
    stalecel["operations"].insert(0,{"op":"palette_add","rgba":[1,2,3,4]})
    scratch=History(initial)
    negatives.append(assert_rejection(scratch,lambda:scratch.apply(stalecel),"stale cel after preceding valid component edits and staged palette add"))
    firstcel=operations[0]["cel_id"]
    bad=Image.fromarray(final_expected[firstcel].copy())
    bad.putpixel((64,10),(255,0,170,255))
    assert [64,10] not in masks[firstcel]
    scratch=History(initial)
    negatives.append(assert_rejection(scratch,lambda:candidate_transaction(scratch.project,firstcel,bad,masks[firstcel]),"candidate RGBA outside component owner"))
    outside=copy.deepcopy(transaction)
    outside["operations"][-1]["candidate_pixels"][10*128+64]=1
    outside["operations"].insert(0,{"op":"palette_add","rgba":[1,2,3,4]})
    scratch=History(initial)
    negatives.append(assert_rejection(scratch,lambda:scratch.apply(outside),"indexed patch outside owner after earlier staged valid edits"))
    for name,value in (("initial",initial),("final",final),("journal",journal),("atomic-transaction",transaction),("atomic-transaction-receipt",receipt),("component-owner-masks",masks)):
        write(f"projects/{name}.json",value)
    exportmanifest=export_project(final,COMPONENT/"exports")
    for entry in exportmanifest["frames"]:
        i=int(entry["id"])
        assert rgba(COMPONENT/"exports"/entry["png"]).tobytes()==components[i]["target"].tobytes()
    exchange=export_aseprite(final,COMPONENT/"exchange/components.aseprite",animation_id="lyra-SE-walk")
    result={
        "status":"PASS actual normal component composition and one guarded atomic multicel transaction",
        "representation":"Five retained visible RGBA component layers; no anatomical rig claim",
        "initial_project_sha256":project_hash(initial),"final_project_sha256":finalhash,
        "actual_guarded_transactions":1,"changed_frame_ids":[f"{i:02}"for i in CHANGED_PHASES],
        "changed_component_cel_count":len(changedcels),"changed_component_cels":changedcels,
        "all8_raw_source_and_editor_PNG_bytes_RGBA_exact":True,
        "all40_final_component_cel_RGBA_exact":True,"fixed_lower_cels_unchanged_locked":True,
        "undo_exact":True,"redo_exact":True,"journal_replay_exact":True,
        "atomic_rejections":negatives,"source_replay_frames":rawrows,"editor_render_frames":rows,
        "framework_export_note":"Toolkit export PNG compression9 may differ from retained approved compression; all8 decodedRGBA exact. editor-render PNGs match approved PNG bytes exactly.",
        "ASE_quantized_ms":[item["milliseconds"]for item in exchange["timing"]],
        "authoritative_clock":{"hold":[9,160],"cycle":[9,20]},
        "external_LibreSprite_test":"not yet performed","new_art_changes":0,"model_calls":0,"canonical_writes":0,"score":None,
    }
    write("projects/EDITOR-RECEIPT.json",result)
    print(json.dumps({key:value for key,value in result.items()if key not in("changed_component_cels","source_replay_frames","editor_render_frames")},indent=2))


if __name__=="__main__":main()

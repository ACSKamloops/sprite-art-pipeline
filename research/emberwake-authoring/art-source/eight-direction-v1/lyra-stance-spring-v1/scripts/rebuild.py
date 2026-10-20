"""Portable local-only source-map and actual editor-journal replay to a fresh path."""
import argparse
import copy
import json
from pathlib import Path

from PIL import Image
from sprite_lab import History, EditError, project_hash, load_json, export_project, import_aseprite
from sprite_lab.core import render_frames
from retained_replay import ROOT, SOURCE, ART, LAYERS, CHANGED_PHASES, sha, rgba, write_source_replay


def rejected_atomically(history, transaction, name):
    before = project_hash(history.project)
    cursor = history.cursor
    receipts = copy.deepcopy(history.journal())
    try:
        history.apply(transaction)
    except EditError as error:
        assert project_hash(history.project) == before
        assert history.cursor == cursor and history.journal() == receipts
        return {"case":name,"rejected_atomically":True,"error":str(error)}
    raise AssertionError(f"Unexpected accepted transaction: {name}")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path,help="Fresh nonexistent output directory")
    args=parser.parse_args()
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    retained_count=0
    for line in (SOURCE/"SHA256SUMS").read_text().splitlines():
        expected,name=line.split("  ",1)
        assert sha(SOURCE/name)==expected,name
        retained_count+=1
    assert retained_count==617
    components,rawrows=write_source_replay(out/"raw-source-map")
    allrows=[]
    project_hashes={}
    for prefix,label,undo_count in((ROOT,"flat-editor",6),(ROOT/"component-editor","component-editor",1)):
        initial=load_json((prefix/"projects/initial.json").read_text())
        journal=load_json((prefix/"projects/journal.json").read_text())
        expected=load_json((prefix/"projects/final.json").read_text())
        history=History.replay(initial,journal)
        assert project_hash(history.project)==project_hash(expected)
        destination=out/label
        destination.mkdir()
        images=render_frames(history.project,[f"{i:02}"for i in range(8)])
        for i,image in enumerate(images):
            assert image.tobytes()==components[i]["target"].tobytes()
            png=destination/f"{i:02}.png"
            image.save(png)
            assert png.read_bytes()==(ART/f"frames/{i:02}.png").read_bytes()
            allrows.append({"representation":label,"phase":i,"PNG_bytes_exact":True,"RGBA_exact":True,"sha256":sha(png)})
        finalhash=project_hash(history.project)
        for _ in range(undo_count):history.undo()
        assert project_hash(history.project)==project_hash(initial)
        for _ in range(undo_count):history.redo()
        assert project_hash(history.project)==finalhash
        project_hashes[label]=finalhash
        if label=="flat-editor":
            export_project(history.project,out/"toolkit-export")
            first=copy.deepcopy(journal["receipts"][0]["transaction"])
            negatives=[]
            stale=copy.deepcopy(first)
            stale["expected_project_sha256"]="0"*64
            negatives.append(rejected_atomically(History(initial),stale,"stale project"))
            stale=copy.deepcopy(first)
            next(op for op in stale["operations"]if op["op"]=="candidate_patch")["expected_cel_sha256"]="0"*64
            stale["operations"].insert(0,{"op":"palette_add","rgba":[1,2,3,4]})
            negatives.append(rejected_atomically(History(initial),stale,"stale cel after staged palette add"))
            outside=copy.deepcopy(first)
            next(op for op in outside["operations"]if op["op"]=="candidate_patch")["candidate_pixels"][10*128+64]=1
            outside["operations"].insert(0,{"op":"palette_add","rgba":[1,2,3,4]})
            negatives.append(rejected_atomically(History(initial),outside,"outside retained owner after staged palette add"))
    # No external executable is required for portable replay. Reimport the
    # retained actual tool-saved flattened file and inspect its actual sheet.
    flat=load_json((ROOT/"projects/final.json").read_text())
    imported=import_aseprite(ROOT/"exchange/approved-flat-tool-saved.aseprite",sidecar=ROOT/"exchange/approved-flat.aseprite.sprite-lab.json")
    assert project_hash(imported)==project_hash(flat)
    tool=Image.open(ROOT/"exchange/approved-flat-tool.png").convert("RGBA")
    assert tool.size==(1024,128)
    for i in range(8):
        assert tool.crop((i*128,0,(i+1)*128,128)).tobytes()==components[i]["target"].tobytes()
    result={"status":"PASS portable retained-source/raw/editor/journal replay",
            "canonical_paths_read":False,"network_or_model_calls":0,
            "retained_617file_ledger_verified":True,
            "all8_raw_source_PNG_bytes_RGBA_exact":True,
            "all8_flat_and_component_editor_PNG_bytes_RGBA_exact":True,
            "six_step_flat_and_one_step_component_undo_redo_exact":True,
            "retained_actual_flat_LibreSprite_saved_project_and_render_exact":True,
            "new_art_changes":0,"project_hashes":project_hashes,"atomic_rejections":negatives,
            "raw_frames":rawrows,"editor_frames":allrows}
    (out/"REPLAY-RECEIPT.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({key:value for key,value in result.items()if key not in("raw_frames","editor_frames")},indent=2))


if __name__=="__main__":main()

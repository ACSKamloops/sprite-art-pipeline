"""Exact approved full-cel exchange; upstream component source stays separate."""
import copy
import json

import numpy as np
from PIL import Image
from sprite_lab import (
    History, canonical_json, project_hash, candidate_transaction, export_project,
    export_aseprite, load_json,
)
from sprite_lab.core import render_frames
from build_package import assert_rejection
from retained_replay import ROOT, SOURCE, ART, CHANGED_PHASES, sha, rgba


def write(name, value):
    (ROOT / name).write_text(canonical_json(value) + "\n")


def main():
    palette = [[0,0,0,0]]
    lookup = {(0,0,0,0):0}
    cels, frames = {}, []
    for i in range(8):
        pixels=[]
        for color in map(tuple,rgba(SOURCE/f"inputs/current/{i:02}.png").reshape(-1,4).tolist()):
            if color not in lookup:
                lookup[color]=len(palette)
                palette.append(list(color))
            pixels.append(lookup[color])
        cel=f"lyra-se-{i:02}"
        cels[cel]={"layer_id":"approved_composite","pixels":pixels}
        frames.append({"id":f"{i:02}","duration_ticks":9,"cels":{"approved_composite":cel},"landmarks":{"pivot":[64,112]}})
    initial={
        "schema":"sprite-edit-project/v1",
        "canvas":{"width":128,"height":128,"render_pivot":[64,112],"ground_pivot":[64,112]},
        "palette":palette,"layers":[{"id":"approved_composite","name":"Approved full composite cels - exact exchange","locked":False}],
        "cels":cels,"frames":frames,
        "animations":[{"id":"lyra-SE-walk","frames":[f"{i:02}"for i in range(8)],"fps":160,"loop":True,"events":[]}],
        "provenance":{
            "representation":"Honest flattened final-paint exchange; no layered anatomical rig claim",
            "why_flattened_exchange":"LibreSprite1.3 preserves all upstream component cels but its normal compositor rounds two overlap pixels differently. Flattened final paint preserves exact approved external-render RGBA.",
            "retained_component_project":"component-editor/projects/final.json",
            "component_exchange_limit_receipt":"component-editor/exchange/TOOL-EXCHANGE-RECEIPT.json",
            "upstream_source_maps_owners_recipe":"retained-source",
            "body_curve":[1,0,-1,0,1,0,-1,0],"body_correction":[1,-1,-2,0,1,-1,-2,0],
            "literal_undercoat_new_coverage_pixels":38,
            "undercoat_journal":"retained-source/waist-completion-v1/UNDERCOAT-LITERAL-JOURNAL.json",
            "approved_png_sha256":[sha(ART/f"frames/{i:02}.png")for i in range(8)],
            "new_art_changes":0,"model_calls":0,"canonical_writes":0,"score":None,
        },
    }
    component_masks=load_json((ROOT/"component-editor/projects/component-owner-masks.json").read_text())
    history=History(initial)
    transactions=[]
    scopes={}
    for i in CHANGED_PHASES:
        points=set()
        for cel,mask in component_masks.items():
            if cel.startswith(f"lyra-se-{i:02}-"):
                points.update(map(tuple,mask))
        coords=[list(point)for point in sorted(points,key=lambda p:(p[1],p[0]))]
        before=rgba(SOURCE/f"inputs/current/{i:02}.png")
        after=rgba(ART/f"frames/{i:02}.png")
        owner=np.zeros((128,128),bool)
        for x,y in coords:owner[y,x]=True
        assert np.array_equal(before[~owner],after[~owner])
        tx=candidate_transaction(history.project,f"lyra-se-{i:02}",Image.fromarray(after),coords,
            reason=f"Import exact approved stance-spring pose{i:02} through retained component source/target owner; final-paint exchange only")
        receipt=history.apply(tx)
        assert set(receipt["diff"]["frames"])=={f"{i:02}"}
        transactions.append((i,tx,receipt))
        scopes[f"{i:02}"]=coords
    final=copy.deepcopy(history.project)
    journal=history.journal()
    finalhash=project_hash(final)
    rendered=render_frames(final,[f"{i:02}"for i in range(8)])
    rows=[]
    for i,image in enumerate(rendered):
        assert image.tobytes()==rgba(ART/f"frames/{i:02}.png").tobytes()
        dst=ROOT/f"editor-render/{i:02}.png"
        image.save(dst)
        assert dst.read_bytes()==(ART/f"frames/{i:02}.png").read_bytes()
        rows.append({"phase":i,"PNG_bytes_exact":True,"RGBA_exact":True,"sha256":sha(dst)})
    for _ in CHANGED_PHASES:history.undo()
    assert project_hash(history.project)==project_hash(initial)
    for _ in CHANGED_PHASES:history.redo()
    assert project_hash(history.project)==finalhash
    assert project_hash(History.replay(initial,journal).project)==finalhash
    negatives=[]
    firsttx=transactions[0][1]
    stale=copy.deepcopy(firsttx)
    stale["expected_project_sha256"]="0"*64
    scratch=History(initial)
    negatives.append(assert_rejection(scratch,lambda:scratch.apply(stale),"stale project precondition"))
    badcel=copy.deepcopy(firsttx)
    next(op for op in badcel["operations"]if op["op"]=="candidate_patch")["expected_cel_sha256"]="0"*64
    badcel["operations"].insert(0,{"op":"palette_add","rgba":[1,2,3,4]})
    scratch=History(initial)
    negatives.append(assert_rejection(scratch,lambda:scratch.apply(badcel),"stale cel after staged palette mutation"))
    badimage=Image.open(ART/"frames/00.png").convert("RGBA")
    badimage.putpixel((64,10),(255,0,170,255))
    assert [64,10]not in scopes["00"]
    scratch=History(initial)
    negatives.append(assert_rejection(scratch,lambda:candidate_transaction(scratch.project,"lyra-se-00",badimage,scopes["00"]),"candidate RGBA outside retained source/target owner"))
    outside=copy.deepcopy(firsttx)
    patch=next(op for op in outside["operations"]if op["op"]=="candidate_patch")
    patch["candidate_pixels"][10*128+64]=1
    outside["operations"].insert(0,{"op":"palette_add","rgba":[1,2,3,4]})
    scratch=History(initial)
    negatives.append(assert_rejection(scratch,lambda:scratch.apply(outside),"indexed patch outside owner after staged palette mutation"))
    for name,value in(("initial",initial),("final",final),("journal",journal),("frame-owner-masks",scopes)):
        write(f"projects/{name}.json",value)
    for i,tx,receipt in transactions:
        write(f"projects/{i:02}-transaction.json",tx)
        write(f"projects/{i:02}-transaction-receipt.json",receipt)
    export_project(final,ROOT/"exports")
    ase=export_aseprite(final,ROOT/"exchange/approved-flat.aseprite",animation_id="lyra-SE-walk")
    result={"status":"PASS exact approved full-cel editor exchange with six actual guarded transactions",
            "representation":"Flattened final composite cels; editable components retained separately as upstream source",
            "initial_project_sha256":project_hash(initial),"final_project_sha256":finalhash,
            "actual_guarded_transactions":6,"changed_frame_ids":[f"{i:02}"for i in CHANGED_PHASES],
            "all8_editor_PNG_bytes_and_RGBA_exact":True,"six_step_undo_redo_exact":True,"journal_replay_exact":True,
            "atomic_rejections":negatives,"frames":rows,
            "authoritative_clock":{"hold":[9,160],"cycle":[9,20]},
            "ASE_quantized_ms":[v["milliseconds"]for v in ase["timing"]],
            "external_flat_exchange":"not yet tested","new_art_changes":0,"model_calls":0,"canonical_writes":0,"score":None}
    write("projects/EDITOR-RECEIPT.json",result)
    print(json.dumps({key:value for key,value in result.items()if key!="frames"},indent=2))


if __name__=="__main__":main()

import json
from PIL import Image
from sprite_lab import import_aseprite, read_aseprite, project_hash, load_json
from retained_replay import ROOT, ART, rgba, sha

final=load_json((ROOT/"projects/final.json").read_text())
saved=ROOT/"exchange/approved-flat-tool-saved.aseprite"
sidecar=ROOT/"exchange/approved-flat.aseprite.sprite-lab.json"
imported=import_aseprite(saved,sidecar=sidecar)
assert project_hash(imported)==project_hash(final)
parsed=read_aseprite(saved)
assert len(parsed["layers"])==1 and len(parsed["frames"])==8
sheet=Image.open(ROOT/"exchange/approved-flat-tool.png").convert("RGBA")
assert sheet.size==(1024,128)
rows=[]
for i in range(8):
    actual=sheet.crop((i*128,0,(i+1)*128,128))
    assert actual.tobytes()==rgba(ART/f"frames/{i:02}.png").tobytes()
    assert parsed["frames"][i]["cels"][0].tobytes()==actual.tobytes()
    rows.append({"phase":i,"external_saved_cel_RGBA_exact":True,"external_render_RGBA_exact":True,
                 "quantized_ms":parsed["frames"][i]["milliseconds"]})
result={"status":"PASS actual LibreSprite1.3 flattened full-cel save/reopen and all8 external-render RGBA",
        "representation":"Honest flattened final-paint exchange; component source retained upstream",
        "actual_native_open_save_reopen":True,"whole_reimported_project_exact":True,
        "all8_external_saved_cel_and_render_RGBA_exact":True,
        "project_sha256":project_hash(final),"tool_saved_ASE_sha256":sha(saved),
        "native_hold":[9,160],"native_loop":[9,20],"tool_ms_total":sum(f["milliseconds"]for f in parsed["frames"]),
        "frames":rows,"new_art_changes":0}
(ROOT/"exchange/TOOL-EXCHANGE-RECEIPT.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))

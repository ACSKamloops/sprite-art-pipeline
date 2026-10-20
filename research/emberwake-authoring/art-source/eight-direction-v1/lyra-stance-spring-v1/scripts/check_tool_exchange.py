from pathlib import Path
import json
import numpy as np
from PIL import Image
from sprite_lab import import_aseprite, read_aseprite, project_hash, load_json, render_cel
from retained_replay import ROOT, ART, LAYERS, rgba, sha

COMPONENT = ROOT / "component-editor"
final = load_json((COMPONENT / "projects/final.json").read_text())
saved = COMPONENT / "exchange/components-tool-saved.aseprite"
sidecar = COMPONENT / "exchange/components.aseprite.sprite-lab.json"
imported = import_aseprite(saved, sidecar=sidecar)
assert project_hash(imported) == project_hash(final)
parsed = read_aseprite(saved)
assert len(parsed["frames"]) == 8
assert len(parsed["layers"]) == 5
sheet = Image.open(COMPONENT / "exchange/components-tool.png").convert("RGBA")
assert sheet.size == (1024,128)
rows = []
for i in range(8):
    target = rgba(ART / f"frames/{i:02}.png")
    tool = np.array(sheet.crop((i*128,0,(i+1)*128,128)))
    points = np.argwhere(np.any(tool != target, axis=2))
    layers_exact = []
    for li, layer in enumerate(LAYERS):
        actual = parsed["frames"][i]["cels"].get(li, Image.new("RGBA",(128,128)))
        expected = render_cel(final,f"lyra-se-{i:02}-{layer}")
        assert actual.tobytes() == expected.tobytes()
        layers_exact.append(layer)
    rows.append({"phase":i,"external_render_RGBA_exact":len(points)==0,
                 "external_render_difference_count":len(points),
                 "external_render_difference_witnesses":[{"at":[int(x),int(y)],"approved":target[y,x].tolist(),"LibreSprite":tool[y,x].tolist()} for y,x in points[:20]],
                 "all5_saved_component_cels_RGBA_exact":True,"quantized_duration_ms":parsed["frames"][i]["milliseconds"]})
result = {
    "status":"PASS layered LibreSprite actual save/reopen and rendering" if all(row["external_render_RGBA_exact"] for row in rows) else "LAYERED COMPONENT CELLS PASS; external normal compositor differs from approved RGBA",
    "tool":"LibreSprite1.3","actual_open_save_reopen":True,
    "all40_saved_component_cels_RGBA_exact":True,"whole_reimported_project_exact":True,
    "final_project_sha256":project_hash(final),"tool_saved_ASE_sha256":sha(saved),
    "all8_external_render_RGBA_exact":all(row["external_render_RGBA_exact"] for row in rows),"frames":rows,
    "total_quantized_ms":sum(frame["milliseconds"] for frame in parsed["frames"]),
    "authoritative_native_hold":[9,160],"authoritative_loop":[9,20],
}
(COMPONENT / "exchange/TOOL-EXCHANGE-RECEIPT.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))

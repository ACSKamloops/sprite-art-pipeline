"""Source/contract anchors for offline cutout provenance, without auth material."""
from pathlib import Path
import hashlib,json,re
R=Path('/home/astra/projects/pixellab-local-test-20261011');O=Path(__file__).resolve().parents[2]/'docs/recovery-round3-20261014'
sha=lambda b:hashlib.sha256(b).hexdigest()
B='pixelorama-recovered/src/Extensions/PixelLab/'
anchors=[('godot-mode-payload',B+'ui/tools/RemoveBackground.gd',69,120),('godot-tool-cost',B+'ui/tools/RemoveBackground.gd',125,155),('godot-tool-dispatch',B+'ui/tools/ToolBase.gd',368,386),('base-and-migration',B+'Main.gd',166,225),('transport-choice',B+'Main.gd',563,583),('background-submit',B+'background_generation.gd',73,103),('animation-mode-input',B+'ui/tools/AnimatePixminimax.gd',267,343),('animation-websocket',B+'websocket.gd',31,59),('response-only-placement',B+'draw_image.gd',199,244),('lua-cutout-submit','extension-extracted/PixelLab/generate-remove-background.lua',69,95),('lua-animation-submit','extension-extracted/PixelLab/generate-animate-pixminimax.lua',193,234),('lua-animation-defaults','extension-extracted/PixelLab/generate-animate-pixminimax.lua',17,34),('host-local-flood','pixelorama-recovered/src/Classes/FloodFillObject.gd',1,190),('host-rgba-tolerance','pixelorama-recovered/src/Autoload/DrawingAlgos.gd',752,763),('host-magic-wand','pixelorama-recovered/src/Tools/SelectionTools/MagicWand.gd',1,90),('host-global-color-select','pixelorama-recovered/src/Tools/SelectionTools/ColorSelect.gd',1,88),('host-bucket-global-replace','pixelorama-recovered/src/Tools/DesignTools/Bucket.gd',250,285),('host-bucket-flood-fill','pixelorama-recovered/src/Tools/DesignTools/Bucket.gd',352,439),('host-alpha-region-slicer','pixelorama-recovered/addons/SmartSlicer/Classes/RegionUnpacker.gd',194,212),('source-color-selection-shader','pixelorama-extracted/src/Shaders/ColorSelect.gdshader',1,40),('source-color-replacement-shader','pixelorama-extracted/src/Shaders/ColorReplace.gdshader',1,43),('shader-execution-bridge','pixelorama-recovered/src/Classes/ShaderImageEffect.gd',11,74)]
rows=[]
for claim,rel,a,b in anchors:
 raw=(R/rel).read_bytes();lines=raw.decode().splitlines(keepends=True);b=min(b,len(lines));rows.append(dict(claim=claim,path=rel,source_sha256=sha(raw),first_line=a,last_line=b,slice_sha256=sha(''.join(lines[a-1:b]).encode())))
for name,token,claim in [('create-677791a6e206dafa.js','id:"remove_background",endpoint:"remove-background"','website-mode-forwarding'),('create-677791a6e206dafa.js','function tQ(e)','website-mode-ui'),('2386-0c23ec27d0c4a587.js','function f(e){return new Promise','website-raw-canvas-serialization')]:
 rel='website-art-bundles/'+name;raw=(R/rel).read_bytes();s=raw.decode();n=s.index(token);rows.append(dict(claim=claim,path=rel,source_sha256=sha(raw),line=s[:n].count('\n')+1,char_offset=n,utf8_byte_offset=len(s[:n].encode()),token=token))
rel='evidence/openapi.json';raw=(R/rel).read_bytes();data=json.loads(raw)
for pointer in ['/components/schemas/RemoveBackgroundRequest','/components/schemas/AnimatePixminimaxRequest/properties/no_background','/paths/~1remove-background/post/description']:
 v=data
 for k in pointer.split('/')[1:]:v=v[k.replace('~1','/').replace('~0','~')]
 rows.append(dict(claim='public-declared-contract',path=rel,source_sha256=sha(raw),line=1,json_pointer=pointer,value=v))
rea=R/'evidence/rea-client-and-pack-analysis.json';rea_data=json.loads(rea.read_text());rea_records=[{k:r.get(k)for k in ['evidence_id','operation','confidence','limitations']}for r in rea_data['records']if r['operation']in ['analyze_javascript_application','trace_application_feature']]
scans=[]
for rel,suffixes in [('pixelorama-recovered/src/Extensions/PixelLab',['.gd']),('extension-extracted/PixelLab',['.lua']),('website-art-bundles',['.js']),('analysis-client/editor-shipped',['.js'])]:
 files=[p for p in (R/rel).rglob('*')if p.suffix in suffixes];hits=[]
 for p in files:
  s=p.read_text()
  for m in re.finditer(r'(?i)flood.?fill|color.?to.?alpha|chroma.?key|FloodFillObject|ColorReplace.gdshader|ColorSelect.gdshader',s):hits.append(dict(path=str(p.relative_to(R)),offset=m.start(),match=m[0]))
 scans.append(dict(scope=rel,files=len(files),pattern='flood.?fill|color.?to.?alpha|chroma.?key|FloodFillObject|ColorReplace.gdshader|ColorSelect.gdshader',hits=hits))
result=dict(classification='bounded-cutout-route-and-host-utility-provenance',research_root=str(R),anchors=rows,scans=scans,existing_rea=dict(path=str(rea),sha256=sha(rea.read_bytes()),records=rea_records,boundary='Existing static/inferred records and limitations only; not live/browser or proof privatecutout exists.'),pck_proof='PCK-MEMBER-PROOF.json',source_replay='HOST-FLOOD-REPLAY.json')
(O/'CUTOUT-PROVENANCE-LEDGER.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(anchors=len(rows),scans=scans),indent=2))

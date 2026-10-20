"""Read-only source-anchor ledger; no provider/network operations."""
from pathlib import Path
import hashlib,json,re
ROOT=Path('/home/astra/projects/pixellab-local-test-20261011')
OUT=Path(__file__).resolve().parent
B='pixelorama-recovered/src/Extensions/PixelLab/'
anchors=[
 ('hidden-rgb',B+'get_image.gd',101,110),('alpha-predicate',B+'get_image.gd',5,13),('mask',B+'get_image.gd',43,73),('palette-reference',B+'get_image.gd',111,184),
 ('decode-and-placement',B+'draw_image.gd',199,246),('rgb-count',B+'lib/PixelLabUtils.gd',96,120),
 ('websocket-array-preference-and-slicing',B+'websocket.gd',169,210),('background-array-normalization',B+'background_generation.gd',222,263),('background-array-delivery',B+'background_generation.gd',266,325),
 ('remote-palette-dither-request',B+'ui/tools/QuantizeColors.gd',289,340),('palette-from-result',B+'ui/tools/QuantizeColors.gd',384,404),('reduce-target-recomputed',B+'ui/tools/QuantizeColors.gd',438,471),
 ('background-removal-request',B+'ui/tools/RemoveBackground.gd',69,120),('animation-client-flags',B+'ui/tools/AnimatePixminimax.gd',316,323),
 ('lua-background-removal','extension-extracted/PixelLab/generate-remove-background.lua',69,95),('lua-color-reference-and-count','extension-extracted/PixelLab/get-image.lua',71,128),
 ('lua-individual-quantize-requests','extension-extracted/PixelLab/quantize-image.lua',329,383),('lua-pixminimax-flags','extension-extracted/PixelLab/generate-animate-pixminimax.lua',17,34),
 ('pro-flash-preserve-mask',B+'ui/tools/InpaintingV3.gd',349,405),
]
records=[]
for claim,rel,first,last in anchors:
 raw=(ROOT/rel).read_bytes(); lines=raw.decode().splitlines(keepends=True)
 records.append(dict(claim=claim,path=rel,source_sha256=hashlib.sha256(raw).hexdigest(),first_line=first,last_line=min(last,len(lines)),slice_sha256=hashlib.sha256(''.join(lines[first-1:last]).encode()).hexdigest()))
js=[('gif-factory','4354-3a62375cb4c03823.js','5958:function'),('gif-quantizer','4354-3a62375cb4c03823.js','function m('),('gif-palette-distance','4354-3a62375cb4c03823.js','function p('),('gif-export-caller','2938-0f2e835ff2fa9208.js','61355:function'),('gif-download-caller','create-677791a6e206dafa.js','let l=n.getImageData(0,0,i,a)'),('animation-processed-preference','generate-animation-17f06517f5e1362c.js','let a=e.quantized_images||e.images')]
for claim,name,token in js:
 rel='website-art-bundles/'+name;raw=(ROOT/rel).read_bytes();s=raw.decode();off=s.index(token)
 records.append(dict(claim=claim,path=rel,source_sha256=hashlib.sha256(raw).hexdigest(),line=s[:off].count('\n')+1,char_offset=off,utf8_byte_offset=len(s[:off].encode()),anchor=token))
p='evidence/openapi.json';raw=(ROOT/p).read_bytes()
for pointer in ['/components/schemas/AnimatePixminimaxRequest/properties/drift_threshold','/components/schemas/AnimatePixminimaxRequest/properties/no_background','/components/schemas/ReduceColorsRequest','/paths/~1reduce-colors/post/description','/paths/~1unzoom/post/description','/paths/~1remove-background/post/description']:
 value=json.loads(raw)
 for k in pointer.split('/')[1:]:value=value[k.replace('~1','/').replace('~0','~')]
 records.append(dict(claim='declared-public-contract',path=p,source_sha256=hashlib.sha256(raw).hexdigest(),line=1,json_pointer=pointer,value_sha256=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()))
scans=[]
for rel,suffix in [('extension-extracted/PixelLab','.lua'),('pixelorama-recovered/src/Extensions/PixelLab','.gd'),('website-art-bundles','.js'),('analysis-client/editor-shipped','.js')]:
 paths=sorted((ROOT/rel).rglob('*'+suffix));hits=[]
 for f in paths:
  s=f.read_text()
  for m in re.finditer('(?i)deflick|de_flick|drift_threshold',s):hits.append(dict(path=str(f.relative_to(ROOT)),offset=m.start()))
 scans.append(dict(scope=rel,suffix=suffix,files=len(paths),pattern='(?i)deflick|de_flick|drift_threshold',hits=hits))
(OUT/'PIXEL-CONVERSION-LEDGER.json').write_text(json.dumps(dict(research_root=str(ROOT),classification='bounded-source-ledger-not-private-backend-recovery',anchors=records,negative_term_scans=scans),indent=2)+'\n')
print(json.dumps(dict(anchors=len(records),scans=scans)))

#!/usr/bin/env python3
"""Build byte-bound evidence for a finite original-client review, read-only corpus."""
from pathlib import Path
import hashlib,json,re,argparse
ROOT=Path('/home/astra/projects/pixellab-local-test-20261011')
OUT=Path(__file__).resolve().parents[2]/'docs/recovery-depth-20261014'
def sha(b): return hashlib.sha256(b).hexdigest()
def anchor(path,lo,hi,bytes_=False):
 b=(ROOT/path).read_bytes()
 if bytes_: start,end=lo,hi
 else:
  ls=b.splitlines(keepends=True); start=sum(map(len,ls[:lo-1]));end=sum(map(len,ls[:hi]))
 f=b[start:end]
 return {'path':path,'source_sha256':sha(b),'source_size_bytes':len(b),'lines_inclusive':[b[:start].count(b'\n')+1,b[:end-1].count(b'\n')+1],'utf8_bytes_half_open':[start,end],'fragment_sha256':sha(f)}
L='extension-extracted/PixelLab/'
G='pixelorama-recovered/src/Extensions/PixelLab/'
claims=[]
def add(id,statement,status,kind,ranges,prior,limit):
 claims.append({'id':id,'statement':statement,'novelty':status,'method_kind':kind,'anchors':[anchor(*x) for x in ranges],'prior_reference':prior,'boundary':limit})
add('PF01','Lua nonblank text preserves edge whitespace, undoubles percent; only view/direction Auto sentinels are omitted. Free-text subject Auto remains literal.','revalidated-with-replay','client-normalization',[(L+'dialog-settings.lua',8,18),(L+'pixminimax.lua',91,143)],'prompt-enhancement-closure L07','Does not recover server prompt rewriting or language model.')
add('PF02','Lua enhancement description replacement, advanced caption merge, picked-slot preservation and stale-first suppression are caller-specific.','revalidated-with-replay','client-state',[(L+'pixminimax.lua',149,216)],'prompt-enhancement-closure L08 and source-change claims','Symbolic Image identity/equality, not native editor concurrency.')
add('PF03','Recovered Godot caption text trims edges; advanced response application indexes requested caption keys directly.','previously-known-static-retrace','client-normalization',[(G+'lib/pixminimax_caption.gd',28,72)],'prompt-enhancement-closure G09','No Godot engine replay; missing-key runtime behavior not established.')
add('PF04','Lua valid numeric seed strings remain strings: tonumber validates but its result is not assigned; invalid seed becomes numeric zero.','new-explicit-qualification-with-replay','request-table',[(L+'create-json.lua',68,83),(L+'create-json.lua',168,179)],'Earlier generic serializer accounting; this type edge now explicit','Original table behavior replayed; symbolic JSON codec does not prove native encoded bytes or private acceptance.')
add('PF05','Lua MiniMax animation requires nonblank motion, count multiple4 in4..40, first image present/nonempty and per-axis <=256. First is RGBA bytes with explicit dimensions.','previously-known-static-retrace','request-wrapper',[(L+'generate-animate-pixminimax.lua',109,242)],'animation-client-closure MiniMax caller','Reference roles are payload roles, not checkpoint internals; request not sent.')
add('PF06','Lua MiniMax animation prepares count+1 logical slots, skips first only. Interpolation uses first/last conditioning and separate both-end skip policy.','previously-known-static-retrace','frame-allocation',[(L+'generate-animate-pixminimax.lua',109,116),(L+'generate-interpolation-pixminimax.lua',109,120),(L+'generate-interpolation-pixminimax.lua',217,231),(L+'prepare-for-generation.lua',276,407)],'animation-client-closure and round4 caller records','Replay proves helper marker destinations only:17 logical ->16 first-skip,15 both-skip. Does not prove actual service count or temporal sampling.')
add('PF07','Godot MiniMax first/optional last must match dimensions and be visible; description remains literal after blank guard; seed converted int. Tool expects count+1 and animate-minimax-h3.','previously-known-static-retrace','request-wrapper',[(G+'ui/tools/AnimatePixminimax.gd',267,348)],'animation-client-closure and prompt-enhancement-closure','Static recovered source only, not native runtime or public REST equivalence.')
add('PF08','Godot first-image change clears caption and cancels enhancement; endpoint state guards differ from first-image guards.','previously-known-static-retrace','client-state',[(G+'ui/tools/AnimatePixminimax.gd',172,266),(G+'enhance_prompt_websocket.gd',94,169)],'prompt-enhancement-closure G07/G08','No engine race exercise.')
add('PF09','Lua response sizing/crop and placement preserve source branch precedence; selection subregion predicate uses OR on smaller axes. A64x16 response on32x32 takes subregion branch despite width exceeding canvas.','new-explicit-qualification-with-replay','placement-wrapper',[(L+'place-image.lua',8,110)],'animation-client-closure placement; qualifies genuinely-smaller shorthand','Symbolic host proves branch/destination calls, not actual Image clipping, retained pixel result, or observed failure.')
add('PF10','Lua frame markers retain logical endpoints as false entries while allocating drawable destinations under skip policy.','revalidated-with-replay','frame-allocation',[(L+'prepare-for-generation.lua',276,407)],'animation-client-closure','No interpolation or recovered remote sample selector; NewFrame host behavior is stubbed.')
add('PF11','Lua cost is a client display formula with size-tier discontinuities, not measured billing or a recovered remote upsampling algorithm.','revalidated-with-replay','display-estimate',[(L+'pixminimax.lua',17,68)],'Existing pixminimax source accounting','Tests bound64/65 and128/129; source comments do not prove remote sampling.')
add('PF12','Web enhancer forwards literal prompt after trim blank guard, maps camelCase fields to snake_case and defaults engine v3; helper itself lacks count/enum validation.','revalidated-with-replay','HTTP-wrapper', [('website-art-bundles/create-677791a6e206dafa.js',13133,14631,True)],'prompt-enhancement-closure W01','Original exact function under synthetic lexical scope/fake fetch; upstream UI validation separate; no HTTP/auth call.')
add('PF13','Recovered Godot frames default duration multiplier1, seconds duration/fps; project default fps6. Existing project clock remains authoritative.','previously-known-static-retrace','host-clock', [('pixelorama-recovered/src/Classes/Frame.gd',7,21),('pixelorama-recovered/src/Classes/Project.gd',80,84),(G+'draw_image.gd',6,126)],'animation-client-closure and round4 clock','No native execution; Lua actual installed Aseprite version remains unidentified.')
add('PF14','Selected web playback effects tick at125ms; selected saved animation records use frameDuration200ms. These are different clocks.','previously-known-static-retrace','preview-storage-clock', [('website-art-bundles/4740-c10d30668d7ecca4.js',9490,9780,True),('website-art-bundles/create-677791a6e206dafa.js',31880,32210,True),('website-art-bundles/4627-44719d0c5e43b757.js',23900,24370,True),('website-art-bundles/7929-0ba5fabea0c5ecc5.js',91500,92050,True)],'animation-client-closure web-frame-clock','Does not establish native model fps or align returned frame index to video PTS.')
add('PF15','Godot interpolation modifies inherited MiniMax tool data: image_amount count-1, skip_first_image1, skip_last_image1. These differ from animation caller retention.','previously-known-static-retrace','frame-wrapper',[(G+'ui/tools/InterpolatePixminimax.gd',1,48)],'animation-client-closure','Source static only; response slicing implementation remains caller-dependent.')
# Negative evidence is finite and disclosed, with positive matches retained as counts.
paths=sorted({a['path'] for c in claims for a in c['anchors']})
patterns=['fps','duration','sample','timestamp','first_frame','last_frame','reference','enhance','caption','animate-minimax-h3']
search=[]
for path in paths:
 b=(ROOT/path).read_bytes();t=b.decode('utf8')
 search.append({'path':path,'sha256':sha(b),'matches_case_insensitive':{p:len(re.findall(re.escape(p),t,re.I)) for p in patterns}})
ledger={'version':1,'scope':'Selected retained original client methods, not entire corpus or private backend','research_root':str(ROOT),'offset_convention':'UTF8 bytes zero-based half-open; lines one-based inclusive; original line endings preserved','claims':claims,'negative_search_bounds':{'files':search,'conclusion':'No executable private generation or server frame sampler recovered in these selected files. Keyword counts alone are not absence proof; no inference about unsearched source.','excluded':['private server implementation','all unselected files','full session history','native editor binaries/runtime','live remote outputs']},'model_or_provider_calls':0,'credentials_loaded':False}
public=Path('/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014/public/pixellab-openapi.json')
pb=public.read_bytes();pd=json.loads(pb)
ledger['captured_public_contract']={'path':str(public),'sha256':sha(pb),'authority':'Retained public OpenAPI declaration, not live or private-server implementation','anchors':['/servers/0/url','/paths/~1enhance-animation-v3-prompt/post','/components/schemas/EnhanceAnimationV3PromptRequest','/paths/~1animate-pixminimax/post'],'selected_declarations':{'server':pd['servers'][0]['url'],'enhancer_request':pd['components']['schemas']['EnhanceAnimationV3PromptRequest']},'boundary':'Public first_frame/action/Base64Image grammar differs from private web image_base64/prompt and rawRGBA clients; schemas do not prove model implementation, endpoint equivalence or private acceptance.'}
OUT.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
serialized=json.dumps(ledger,indent=2)+'\n'
if args.check:
 if (OUT/'PROMPT-FRAME-CLAIMS.json').read_text()!=serialized: raise SystemExit('Source anchors or retained declarations differ from ledger')
else: (OUT/'PROMPT-FRAME-CLAIMS.json').write_text(serialized)
print(json.dumps({'claims':len(claims),'anchors':sum(len(c['anchors']) for c in claims),'files':len(paths)}))

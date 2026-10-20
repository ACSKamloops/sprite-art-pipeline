"""Prepare/verify/analyze <=3 frozen cutout probes. No network or credentials code.
Synthetic shape construction is experimental stimulus, never recovered segmentation.
"""
import argparse,base64,hashlib,io,json
from pathlib import Path
import numpy as np
from PIL import Image

DEFAULT=Path('/home/astra/artifacts/pixellab-cutout-characterization-20261014')
VARIANTS={'simple-opaque':('opaque.png','remove_simple_background'),
          'complex-opaque':('opaque.png','remove_complex_background'),
          'simple-alpha':('alpha-patches.png','remove_simple_background')}
sha=lambda b:hashlib.sha256(b).hexdigest()
def write_json(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def descriptor(p):return {'type':'base64','base64':'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode(),'format':'png'}
def prepare(root):
    root.mkdir(parents=True,exist_ok=False)
    inputs=root/'inputs';inputs.mkdir()
    bg=[30,160,80,255];a=np.empty((96,96,4),dtype=np.uint8);a[:]=bg
    # All rectangles are source design; none is an estimated segmentation output.
    def rect(x0,y0,x1,y1,c):a[y0:y1,x0:x1]=c
    dark=[8,10,14,255];armor=[180,60,65,255];face=[175,185,195,255]
    rect(38,16,58,20,dark);rect(34,20,62,40,dark);rect(37,23,59,37,face)
    rect(40,27,44,31,dark);rect(52,27,56,31,dark)
    rect(28,40,68,68,dark);rect(31,43,65,65,armor)
    rect(18,44,28,68,dark);rect(20,46,26,64,face)
    rect(68,44,78,68,dark);rect(70,46,76,64,face)
    rect(31,68,43,82,dark);rect(53,68,65,82,dark)
    rect(28,80,43,85,dark);rect(53,80,68,85,dark)
    # Same-background color in an enclosed patch and an open channel, respectively.
    rect(44,47,52,55,bg);rect(28,59,42,62,bg)
    rect(57,57,61,61,[38,168,88,255]) # near-background foreground decoration
    rect(33,48,37,52,dark) # protected-probe detail, not an asserted semantic mask
    im=Image.fromarray(a);im.save(inputs/'opaque.png')
    alpha=a.copy()
    patches=[]
    for x,opacity in [(33,0),(39,64),(53,128),(59,255)]:
        # All patches lie on matching armor RGB, away from hole/channel/details.
        alpha[44:46,x:x+3,3]=opacity
        patches.append(dict(name=f'armor_alpha_{opacity}',rect=[x,44,x+3,46],source_alpha=opacity))
    Image.fromarray(alpha).save(inputs/'alpha-patches.png')
    regions=[dict(name='flat_border',rect=[0,0,96,8]),dict(name='enclosed_same_background_rgb',rect=[44,47,52,55]),
             dict(name='open_same_background_channel',rect=[28,59,42,62]),dict(name='dark_chest_detail',rect=[33,48,37,52]),
             dict(name='near_background_foreground_decoration',rect=[57,57,61,61]),dict(name='opaque_armor_reference',rect=[32,54,39,57])]+patches
    write_json(inputs/'REGIONS.json',dict(coordinates='[x0,y0,x1,y1], right/bottom exclusive',regions=regions,warning='Source-designed probe areas; enclosed same-color patch is semantically ambiguous. No estimated/groundtruth semantic removal mask.'))
    slots=[]
    for name,(source,task)in VARIANTS.items():
        run=root/name;run.mkdir()
        payload={'image':descriptor(inputs/source),'image_size':{'width':96,'height':96},'background_removal_task':task,'seed':123}
        write_json(run/'request.json',payload)
        wire=json.dumps(payload,separators=(',',':'),sort_keys=True).encode()
        (run/'request-wire.json').write_bytes(wire)
        slots.append(dict(variant=name,source='inputs/'+source,source_png_sha256=sha((inputs/source).read_bytes()),request_sha256=sha((run/'request.json').read_bytes()),wire_sha256=sha(wire),wire_bytes=len(wire),task=task,text='omitted',seed=123,submission_lock=name+'/.submission.lock'))
    frozen_inputs=[dict(path='inputs/'+p.name,sha256=sha(p.read_bytes()))for p in sorted(inputs.iterdir())]
    plan=dict(version=1,status='prepared-not-submitted',endpoint='https://api.pixellab.ai/v2/remove-background',method='POST',max_posts=3,automatic_retries=0,allow_redirects=False,requests=slots,inputs=frozen_inputs,
              submission_guard=dict(required='Verify all pins BEFORE any call. Only these3 allowlisted slots. Atomically create each .submission.lock with O_CREAT|O_EXCL before sending; retain after every outcome. Write attempted state before POST. Never reclaim on timeout/error/ambiguous response. No automatic retries, no fallback task, no new slot.',wire='Send exact request-wire.json bytes; hash expected in plan.',transport='Reuse approved existing helper credential resolver + decoded JSON response redactor. No token/header/cookie in HAR. No credentials code exists in this preparer.',limits='POST timeout60s; response cap4MiB+1 reject if exceeded; deny redirects. Save actual request/response wire hashes and sanitized one-entry HAR.',budget='At most3 POST attempts; actual charge unknown here. Parent reviews before any submission; stop if response reveals unexpected charge.'),
              technique_boundary='Separate public endpoint; nothing demonstrates PixMiniMax uses this endpoint, task, thresholds, code or request seed internally.',
              source_script_sha256=sha(Path(__file__).read_bytes()),source_schema=dict(path='/home/astra/projects/pixellab-local-test-20261011/evidence/openapi.json',sha256=sha(Path('/home/astra/projects/pixellab-local-test-20261011/evidence/openapi.json').read_bytes()),pointer='/components/schemas/RemoveBackgroundRequest'))
    write_json(root/'PLAN.json',plan)
    return verify(root)
def verify(root):
    p=json.loads((root/'PLAN.json').read_text());assert p['max_posts']==3 and p['automatic_retries']==0
    assert {r['variant']for r in p['requests']}==set(VARIANTS)
    for v in p['inputs']:assert sha((root/v['path']).read_bytes())==v['sha256']
    for v in p['requests']:
        d=root/v['variant'];raw=(d/'request.json').read_bytes();wire=(d/'request-wire.json').read_bytes()
        assert sha(raw)==v['request_sha256'] and sha(wire)==v['wire_sha256']
        j=json.loads(raw);assert j==json.loads(wire)
        assert j['background_removal_task']==VARIANTS[v['variant']][1] and j['seed']==123 and 'text'not in j
        assert j['image_size']=={'width':96,'height':96}
        b=base64.b64decode(j['image']['base64'].split(',',1)[1],validate=True)
        assert b==(root/v['source']).read_bytes()
    return dict(status='verified-frozen-plan',root=str(root),max_posts=3,posts_made_by_this_script=0,existing_slot_locks=[r['variant']for r in p['requests']if(root/r['submission_lock']).exists()],plan_sha256=sha((root/'PLAN.json').read_bytes()))
def compare(source,result,regions):
    if result.shape!=source.shape:return dict(size_mismatch=True,source_shape=list(source.shape),output_shape=list(result.shape))
    def stats(a,b):
        visible=(a[:,:,3]>0)&(b[:,:,3]>0)
        rgb_diff=np.any(a[:,:,:3]!=b[:,:,:3],axis=2)
        return dict(pixels=int(a.shape[0]*a.shape[1]),source_alpha_values=np.unique(a[:,:,3]).tolist(),output_alpha_values=np.unique(b[:,:,3]).tolist(),alpha_changed=int(np.count_nonzero(a[:,:,3]!=b[:,:,3])),became_alpha_zero=int(np.count_nonzero((a[:,:,3]>0)&(b[:,:,3]==0))),became_visible=int(np.count_nonzero((a[:,:,3]==0)&(b[:,:,3]>0))),both_visible_rgb_changed=int(np.count_nonzero(visible&rgb_diff)),all_rgb_changed_including_hidden=int(rgb_diff.sum()),output_alpha_zero_nonzero_rgb=int(np.count_nonzero((b[:,:,3]==0)&np.any(b[:,:,:3]!=0,axis=2))))
    out=stats(source,result);out['regions']={}
    for r in regions:
        x0,y0,x1,y1=r['rect'];out['regions'][r['name']]=stats(source[y0:y1,x0:x1],result[y0:y1,x0:x1])
    return out
def analyze(root):
    verify(root);p=json.loads((root/'PLAN.json').read_text());regions=json.loads((root/'inputs/REGIONS.json').read_text())['regions'];cases=[]
    for r in p['requests']:
        d=root/r['variant'];response=d/'response.json';output=next((f for f in[d/'output.png',d/'output-00.png']if f.exists()),None)
        if output is None and not response.exists():cases.append(dict(variant=r['variant'],status='not-executed-or-no-response'));continue
        try:
            # Prefer captured response descriptor, so analyzed pixels bind to actual returned bytes.
            if response.exists():
                j=json.loads(response.read_text());desc=j.get('image')
                if not desc:cases.append(dict(variant=r['variant'],status='response-without-image',response_sha256=sha(response.read_bytes())));continue
                value=desc['base64'];raw=base64.b64decode(value.split(',',1)[-1],validate=True)
                if output:assert output.read_bytes()==raw,'retained output differs from returned PNG'
            else:raw=output.read_bytes()
            a=np.array(Image.open(root/r['source']).convert('RGBA'));b=np.array(Image.open(io.BytesIO(raw)).convert('RGBA'))
            cases.append(dict(variant=r['variant'],status='decoded',response_sha256=sha(response.read_bytes())if response.exists()else None,returned_png_sha256=sha(raw),metrics=compare(a,b,regions)))
        except (ValueError,KeyError,AssertionError,OSError)as exc:cases.append(dict(variant=r['variant'],status='analysis-error',error=str(exc)))
    result=dict(classification='endpoint-output-measurements-not-segmentation-source-recovery',plan_sha256=sha((root/'PLAN.json').read_bytes()),cases=cases,posts_made_by_this_script=0)
    write_json(root/'ANALYSIS.json',result);return result
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['prepare','verify','analyze']);parser.add_argument('root',type=Path,nargs='?',default=DEFAULT);a=parser.parse_args()
    print(json.dumps(globals()[a.action](a.root),indent=2))

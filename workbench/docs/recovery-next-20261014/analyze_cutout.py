"""Read-only captured cutout analysis + bounded authored counter-candidates.
No endpoint calls. Candidate fit is not original server source recovery.
"""
import base64,hashlib,importlib.util,io,json
from collections import deque
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path('/home/astra/artifacts/pixellab-cutout-characterization-20261014')
OUT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
PIN='7fe6dea39aead1e171caa7239ce1b8e08b766b45568873faa3e7da61e89b8260'
def png_bytes(desc):return base64.b64decode(desc['base64'].split(',',1)[-1],validate=True)
def border_connected(eligible,neighbors=4):
    h,w=eligible.shape;seen=np.zeros_like(eligible);q=deque()
    for y,x in [(0,x)for x in range(w)]+[(h-1,x)for x in range(w)]+[(y,0)for y in range(h)]+[(y,w-1)for y in range(h)]:
        if eligible[y,x]and not seen[y,x]:seen[y,x]=True;q.append((y,x))
    shifts=[(-1,0),(1,0),(0,-1),(0,1)]
    if neighbors==8:shifts+=[(-1,-1),(-1,1),(1,-1),(1,1)]
    while q:
        y,x=q.popleft()
        for dy,dx in shifts:
            yy,xx=y+dy,x+dx
            if 0<=yy<h and 0<=xx<w and eligible[yy,xx]and not seen[yy,xx]:seen[yy,xx]=True;q.append((yy,xx))
    return seen

def main():
    raw=(ROOT/'PLAN.json').read_bytes();assert sha(raw)==PIN;plan=json.loads(raw)
    helper=OUT.parent/'recovery-depth-20261014/prepare_cutout_probe.py';assert sha(helper.read_bytes())==plan['source_script_sha256']
    spec=importlib.util.spec_from_file_location('frozen_helper',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.verify(ROOT)
    regions=json.loads((ROOT/'inputs/REGIONS.json').read_text())['regions'];records=[];arrays=[];pins=[]
    for r in plan['requests']:
        d=ROOT/r['variant'];request=json.loads((d/'request.json').read_text());response=json.loads((d/'response.json').read_text())
        source=png_bytes(request['image']);returned=png_bytes(response['image'])
        assert source==(ROOT/r['source']).read_bytes();assert returned==(d/'output-00.png').read_bytes()
        har=json.loads((d/'network.har').read_text());entries=har['log']['entries'];assert len(entries)==1;e=entries[0]
        assert e['request']['method']=='POST'and e['request']['url']==plan['endpoint'];assert e['response']['status']==200
        sent=e['request']['postData']['text'].encode();assert sha(sent)==r['wire_sha256'];assert json.loads(sent)==request
        wire_response=json.loads(e['response']['content']['text']);assert png_bytes(wire_response['image'])==returned
        state=json.loads((d/'state.json').read_text());assert state['http_status']==200
        a=np.array(Image.open(io.BytesIO(source)).convert('RGBA'));b=np.array(Image.open(io.BytesIO(returned)).convert('RGBA'));arrays.append((r['variant'],a,b))
        records.append(dict(variant=r['variant'],source_png_sha256=sha(source),returned_png_sha256=sha(returned),response_sha256=sha((d/'response.json').read_bytes()),actual_post_wire_sha256=sha(sent),har_returned_png_matches_saved=True,usage=state['usage'],metrics=mod.compare(a,b,regions)))
        for f in ['request.json','request-wire.json','response.json','network.har','state.json','output-00.png']:
            p=d/f;pins.append(dict(path=str(p),sha256=sha(p.read_bytes())))
    a=arrays[0][1];bg=a[0,0,:3];equal=np.all(a[:,:,:3]==bg,axis=2);topology=[]
    for n in [4,8]:
        connected=border_connected(equal,n)
        topology.append(dict(neighbors=n,total_exact_background_color=int(equal.sum()),border_connected_exact_color=int(connected.sum()),regions=[dict(name=r['name'],exact_bg_pixels=int(equal[r['rect'][1]:r['rect'][3],r['rect'][0]:r['rect'][2]].sum()),border_connected_exact_bg_pixels=int(connected[r['rect'][1]:r['rect'][3],r['rect'][0]:r['rect'][2]].sum()))for r in regions]))
    candidates=[]
    # Predeclared small family only: four/eight neighbors, Linf tolerances0/8/16,
    # preserve source alpha vs force retained alpha255. No per-region fitted mask.
    for n in [4,8]:
        for threshold in [0,8,16]:
            for alpha in ['preserve','force-retained-255']:
                scores=[]
                for name,src,target in arrays:
                    eligible=np.max(np.abs(src[:,:,:3].astype(int)-bg.astype(int)),axis=2)<=threshold
                    mask=border_connected(eligible,n);pred=src.copy()
                    if alpha=='force-retained-255':pred[:,:,3]=255
                    pred[mask]=0
                    bad=np.any(pred!=target,axis=2);ys,xs=np.where(bad)
                    scores.append(dict(variant=name,rgba_mismatches=int(bad.sum()),alpha_mask_mismatches=int(np.count_nonzero((pred[:,:,3]>0)!=(target[:,:,3]>0))),counterexamples=[dict(x=int(x),y=int(y),predicted=pred[y,x].tolist(),actual=target[y,x].tolist())for y,x in zip(ys[:3],xs[:3])]))
                candidates.append(dict(params=dict(neighbors=n,color_metric='max absolute RGB difference from top-left source color',threshold=threshold,alpha_policy=alpha,removed_rgba=[0,0,0,0]),scores=scores))
    result=dict(classification='public-endpoint-measurement-and-bounded-fit-not-server-source-recovery',plan_sha256=PIN,pins=pins,cases=records,source_topology=topology,candidates=candidates,candidate_count=len(candidates),all_outputs_png_byte_identical=len({r['returned_png_sha256']for r in records})==1,total_usage_generations=sum(r['usage']['generations']for r in records),posts_made_by_reviewer=0,fixture_correction='Region labeled open_same_background_channel is enclosed by left arm atx27, y59..61. It is not an open-channel test. Original labels/bytes preserved.',limitations='Single RGB fixture; differing inputalpha tests alpha path only. Neighbor connectivity and thresholds0/8/16 observationally indistinguishable here. Same Simple/Complex result does not prove same algorithm; none proves PixMiniMax internalcutout.')
    (OUT/'CUTOUT-FINDINGS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(cases=[dict(variant=r['variant'],png=r['returned_png_sha256'],alpha_changed=r['metrics']['alpha_changed'],visible_rgb_changed=r['metrics']['both_visible_rgb_changed'])for r in records],candidate_count=len(candidates),exact_candidates=[c['params']for c in candidates if all(s['rgba_mismatches']==0 for s in c['scores'])],topology=topology),indent=2))
if __name__=='__main__':main()

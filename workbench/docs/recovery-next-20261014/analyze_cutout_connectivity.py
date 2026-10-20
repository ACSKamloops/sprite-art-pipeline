"""Bound corrected public cutout captures; eight PREDECLARED offline candidates.
No calls. Authored candidate masks never imply recovered server source.
"""
import base64,hashlib,io,json
from pathlib import Path
import numpy as np
from PIL import Image
from analyze_cutout import border_connected
ROOT=Path('/home/astra/artifacts/pixellab-cutout-connectivity-20261014')
OUT=Path(__file__).resolve().parent
PIN='d23295b3af242446a5947db8ea626cbc8ad4ff432007bfbf10e2de7c80a692b3'
sha=lambda b:hashlib.sha256(b).hexdigest()
def decode_png(d):return base64.b64decode(d['base64'].split(',',1)[-1],validate=True)
def main():
    raw=(ROOT/'PLAN.json').read_bytes();assert sha(raw)==PIN;plan=json.loads(raw)
    assert len(plan['requests'])==2 and {r['variant']for r in plan['requests']}=={'simple','complex'}
    for r in plan['inputs']:assert sha((ROOT/r['path']).read_bytes())==r['sha256']
    assert sha(Path(__file__).with_name('analyze_cutout.py').read_bytes())==plan['offline_dependency']['sha256']
    region_data=json.loads((ROOT/'inputs/REGIONS.json').read_text());regions=region_data['regions'];cases=[];pins=[];captured={}
    for r in plan['requests']:
        d=ROOT/r['variant'];reqraw=(d/'request.json').read_bytes();wire=(d/'request-wire.json').read_bytes()
        assert sha(reqraw)==r['request_sha256']and sha(wire)==r['wire_sha256']and json.loads(reqraw)==json.loads(wire)
        req=json.loads(reqraw);source=decode_png(req['image']);assert source==(ROOT/r['source']).read_bytes();assert sha(source)==r['source_png_sha256']
        if not all((d/f).exists()for f in ['response.json','output-00.png','network.har','state.json']):
            cases.append(dict(variant=r['variant'],status='capture-not-complete'));continue
        response_raw=(d/'response.json').read_bytes();response=json.loads(response_raw);png=decode_png(response['image']);assert png==(d/'output-00.png').read_bytes()
        har=json.loads((d/'network.har').read_text());es=har['log']['entries'];assert len(es)==1;e=es[0]
        assert e['request']['method']=='POST'and e['request']['url']==plan['endpoint']and e['response']['status']==200
        sent=e['request']['postData']['text'].encode();assert sent==wire
        assert decode_png(json.loads(e['response']['content']['text'])['image'])==png
        state=json.loads((d/'state.json').read_text());assert state['http_status']==200 and state['status']=='completed'
        a=np.array(Image.open(io.BytesIO(source)).convert('RGBA'));b=np.array(Image.open(io.BytesIO(png)).convert('RGBA'));assert a.shape==b.shape==(96,96,4)
        captured[r['variant']]=b
        bg=a[0,0,:3];distance=np.max(np.abs(a[:,:,:3].astype(int)-bg.astype(int)),axis=2);observed_mask=b[:,:,3]==0
        def metrics(mask):
            return {rg['name']:dict(pixels=(rg['rect'][2]-rg['rect'][0])*(rg['rect'][3]-rg['rect'][1]),removed=int(mask[rg['rect'][1]:rg['rect'][3],rg['rect'][0]:rg['rect'][2]].sum()))for rg in regions}
        candidates=[]
        for n in [4,8]:
            for threshold in [0,1,8,32]:
                mask=border_connected(distance<=threshold,n);pred=a.copy();pred[:,:,3]=255;pred[mask]=0
                bad=np.any(pred!=b,axis=2);ys,xs=np.where(bad)
                candidates.append(dict(neighbors=n,linf_threshold=threshold,retained_alpha=255,removed_rgba=[0,0,0,0],candidate_removed=int(mask.sum()),rgba_mismatches=int(bad.sum()),mask_mismatches=int(np.count_nonzero(mask!=observed_mask)),regional_candidate_removal=metrics(mask),counterexamples=[dict(x=int(x),y=int(y),source=a[y,x].tolist(),candidate=pred[y,x].tolist(),actual=b[y,x].tolist())for y,x in zip(ys[:4],xs[:4])]))
        case=dict(variant=r['variant'],status='bound-and-measured',source_png_sha256=sha(source),returned_png_sha256=sha(png),response_sha256=sha(response_raw),actual_post_wire_sha256=sha(sent),usage=state['usage'],output_alpha=np.unique(b[:,:,3]).tolist(),removed_pixels=int(observed_mask.sum()),retained_visible_rgb_changes=int(np.count_nonzero((b[:,:,3]>0)&np.any(a[:,:,:3]!=b[:,:,:3],axis=2))),zero_alpha_nonzero_rgb=int(np.count_nonzero(observed_mask&np.any(b[:,:,:3]!=0,axis=2))),regions=metrics(observed_mask),candidates=candidates,exact_candidates=[dict(neighbors=c['neighbors'],linf_threshold=c['linf_threshold'])for c in candidates if c['rgba_mismatches']==0])
        cases.append(case)
        for f in ['request.json','request-wire.json','response.json','output-00.png','network.har','state.json']+(['REA-EVIDENCE.json']if(d/'REA-EVIDENCE.json').exists()else[]):
            p=d/f;pins.append(dict(path=str(p),sha256=sha(p.read_bytes())))
    done=[c for c in cases if c['status']=='bound-and-measured']
    pairwise=None
    if len(captured)==2:
        a,b=captured['simple'],captured['complex']
        pairwise=dict(rgba_differing_pixels=int(np.count_nonzero(np.any(a!=b,axis=2))),mask_differing_pixels=int(np.count_nonzero((a[:,:,3]==0)!=(b[:,:,3]==0))),simple_removed_complex_kept=int(np.count_nonzero((a[:,:,3]==0)&(b[:,:,3]>0))),complex_removed_simple_kept=int(np.count_nonzero((b[:,:,3]==0)&(a[:,:,3]>0))),diagonal_chain_actual=[dict(x=x,y=y,simple_rgba=a[y,x].tolist(),complex_rgba=b[y,x].tolist())for x,y in region_data['diagonal_chain_pixels_xy']])
    proof=ROOT/'inputs/TOPOLOGY-PROOF.json';pins.append(dict(path=str(proof),sha256=sha(proof.read_bytes())))
    result=dict(classification='predeclared-public-cutout-candidate-test-not-server-source-recovery',plan_sha256=PIN,pairwise=pairwise,pins=pins,cases=cases,all_complete=len(done)==2,outputs_byte_identical=len(done)==2 and done[0]['returned_png_sha256']==done[1]['returned_png_sha256'],candidate_grid=dict(neighbors=[4,8],linf_threshold=[0,1,8,32],retained_alpha=255,removed_rgba=[0,0,0,0],candidate_count_per_case=8),posts_made_by_reviewer=0,boundary='Same one RGB diagnostic, two task enums. Exact match within grid is not source recovery; cannot infer exact threshold between samples or PixMiniMax internal route.')
    (OUT/'CUTOUT-CONNECTIVITY-FINDINGS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(all_complete=result['all_complete'],outputs_byte_identical=result['outputs_byte_identical'],cases=[{k:c[k]for k in ['variant','status','returned_png_sha256','removed_pixels','retained_visible_rgb_changes','regions','exact_candidates']if k in c}for c in cases]),indent=2))
if __name__=='__main__':main()

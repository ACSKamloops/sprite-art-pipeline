"""Prepare only: two frozen cutout requests with pixel-verified topology.
No HTTP, credentials or submission implementation. Source-designed fixture only.
"""
import base64,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from analyze_cutout import border_connected
ROOT=Path('/home/astra/artifacts/pixellab-cutout-connectivity-20261014')
sha=lambda b:hashlib.sha256(b).hexdigest()
def write_json(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def prepare():
    ROOT.mkdir(parents=True,exist_ok=False);inputs=ROOT/'inputs';inputs.mkdir()
    bg=np.array([30,160,80],dtype=np.uint8);a=np.empty((96,96,4),dtype=np.uint8);a[:,:,:3]=bg;a[:,:,3]=255
    dark=[8,10,14,255];armor=[180,60,65,255]
    def rect(x0,y0,x1,y1,c):a[y0:y1,x0:x1]=c
    rect(20,20,76,76,dark);rect(24,24,72,72,armor)
    rect(36,22,60,36,[175,185,195,255]);rect(40,27,44,31,dark);rect(52,27,56,31,dark)
    rect(30,76,42,88,dark);rect(54,76,66,88,dark)
    rect(0,42,44,46,[*bg.tolist(),255]) # actual edge-open corridor, no arm blocking it
    rect(52,38,60,46,[*bg.tolist(),255]) # enclosed hole, separated from corridor
    for i in range(11):a[48+i,20+i]=[*bg.tolist(),255]
    rect(30,58,35,63,[*bg.tolist(),255]) # reaches border only along diagonal chain
    rect(62,56,66,60,dark)
    strips=[]
    for delta,y in [(1,4),(8,10),(32,16)]:
        c=[int(bg[0])+delta,int(bg[1]),int(bg[2]),255];rect(0,y,16,y+4,c)
        strips.append(dict(name=f'border_close_green_{delta}',rect=[0,y,16,y+4],max_rgb_distance=delta))
    regions=[dict(name='true_open_channel_in_body',rect=[20,42,44,46]),dict(name='truly_enclosed_hole',rect=[52,38,60,46]),dict(name='diagonal_only_patch',rect=[30,58,35,63]),dict(name='dark_detail',rect=[62,56,66,60])]+strips
    def region(mask,r):
        x0,y0,x1,y1=r['rect'];return mask[y0:y1,x0:x1]
    rgb_distance=np.max(np.abs(a[:,:,:3].astype(int)-bg.astype(int)),axis=2)
    # Validate actual source topology, not just intended drawing coordinates.
    exact4=border_connected(rgb_distance==0,4);exact8=border_connected(rgb_distance==0,8)
    assert region(exact4,regions[0]).all()and region(exact8,regions[0]).all()
    assert not region(exact4,regions[1]).any()and not region(exact8,regions[1]).any()
    assert not region(exact4,regions[2]).any()and region(exact8,regions[2]).all()
    assert np.all(a[:,:,3]==255)
    proofs=[]
    for n in [4,8]:
        for threshold in [0,1,8,32]:
            connected=border_connected(rgb_distance<=threshold,n)
            proofs.append(dict(neighbors=n,linf_threshold=threshold,total_connected=int(connected.sum()),regions={r['name']:dict(pixels=int(region(connected,r).size),connected=int(region(connected,r).sum()))for r in regions}))
            for r in strips:
                assert bool(region(connected,r).all())==(threshold>=r['max_rgb_distance'])
                assert bool(region(connected,r).any())==(threshold>=r['max_rgb_distance'])
    png=inputs/'connectivity-rgba.png';Image.fromarray(a).save(png)
    write_json(inputs/'REGIONS.json',dict(coordinates='[x0,y0,x1,y1], exclusive bottom/right',regions=regions,background_rgb=bg.tolist(),diagonal_chain_pixels_xy=[[20+i,48+i]for i in range(11)],all_source_alpha=255,warning='Source annotations/topology, not semantic groundtruth or server removal predictions.'))
    write_json(inputs/'TOPOLOGY-PROOF.json',dict(classification='actual-source-pixel-connectivity-check-not-server-algorithm',fixture_shape=list(a.shape),assertion_statements_executed=52,proofs=proofs,proof_script_sha256=sha(Path(__file__).read_bytes())))
    slots=[]
    for name,task in [('simple','remove_simple_background'),('complex','remove_complex_background')]:
        d=ROOT/name;d.mkdir()
        payload=dict(image={'type':'base64','format':'png','base64':'data:image/png;base64,'+base64.b64encode(png.read_bytes()).decode()},image_size={'width':96,'height':96},background_removal_task=task,seed=123)
        write_json(d/'request.json',payload);wire=json.dumps(payload,sort_keys=True,separators=(',',':')).encode();(d/'request-wire.json').write_bytes(wire)
        slots.append(dict(variant=name,source='inputs/connectivity-rgba.png',source_png_sha256=sha(png.read_bytes()),task=task,seed=123,text='omitted',request_sha256=sha((d/'request.json').read_bytes()),wire_sha256=sha(wire),wire_bytes=len(wire),submission_lock=name+'/.submission.lock'))
    plan=dict(version=1,status='prepared-not-submitted',endpoint='https://api.pixellab.ai/v2/remove-background',method='POST',max_posts=2,automatic_retries=0,allow_redirects=False,requests=slots,inputs=[dict(path='inputs/'+p.name,sha256=sha(p.read_bytes()))for p in sorted(inputs.iterdir())],preparer_sha256=sha(Path(__file__).read_bytes()),
              offline_dependency=dict(path='docs/recovery-next-20261014/analyze_cutout.py',sha256=sha(Path(__file__).with_name('analyze_cutout.py').read_bytes()),method='border_connected'),
              submission_guard=dict(required='Parent review PLAN hash. Verify all pins. Only2 namedslots total,one POSTattempt each. Before sending create persistent .submission.lock O_CREAT|O_EXCL and attemptedstate. Never retry timeout/error/ambiguous. Never resetlock or fallback.',wire='Send exact request-wire.json; pin in request record.',transport='Approved existing helper only; deny redirects;60s timeout;4MiB response cap;actualwire hashes,redactedHAR,responseJSON,returnedPNG. No auth/header/cookies retained.',budget='New separate max2-POSTphase; actual charge unknown before execution. No calls made by preparer.'),
              boundary='Public cutout only; no claim of PixMiniMax internal route/algorithm. Topology is input property, not predicted semantic output.')
    write_json(ROOT/'PLAN.json',plan)
    # Mechanical JSON/descriptor verification without any submission.
    for r in slots:
        req=json.loads((ROOT/r['variant']/'request.json').read_text());assert base64.b64decode(req['image']['base64'].split(',',1)[1])==png.read_bytes()
    return dict(root=str(ROOT),plan_sha256=sha((ROOT/'PLAN.json').read_bytes()),source_png_sha256=sha(png.read_bytes()),posts=0,topology=proofs)
if __name__=='__main__':print(json.dumps(prepare(),indent=2))

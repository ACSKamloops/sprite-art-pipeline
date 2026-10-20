"""Two actual guarded transactions on flattened composite cels; no new art."""
import copy,json
import numpy as np
from PIL import Image
from common import ROOT,rgba,mask,sha,write,verify_inputs
from replay_sources import replay
from sprite_lab import History,EditError,canonical_json,project_hash,cel_hash,candidate_transaction,render_cel,export_project,export_aseprite
from sprite_lab.core import render_frames

def save(path,obj):path.write_text(canonical_json(obj)+'\n')

def rejected(history,action,name):
    p,j=canonical_json(history.project),canonical_json(history.journal())
    try:action()
    except EditError as e:
        assert canonical_json(history.project)==p and canonical_json(history.journal())==j
        return {'case':name,'rejected':True,'project_and_history_unchanged':True,'error':str(e)}
    raise AssertionError('Expected rejection: '+name)

def main():
    verify_inputs()
    for name in ['projects','editor-render','exports','exchange','verification']:
        p=ROOT/name;assert not p.exists();p.mkdir()
    source=replay(ROOT/'source-replay')
    palette=[[0,0,0,0]];lookup={(0,0,0,0):0};cels={};frames=[]
    for i in range(8):
        pixels=[]
        for color in map(tuple,rgba(ROOT/f'inputs/current/{i:02}.png').reshape(-1,4).tolist()):
            if color not in lookup:lookup[color]=len(palette);palette.append(list(color))
            pixels.append(lookup[color])
        cid=f'rowan-ne-{i:02}';cels[cid]={'layer_id':'composite','pixels':pixels}
        frames.append({'id':f'{i:02}','duration_ticks':9,'cels':{'composite':cid},'landmarks':{'pivot':[64,112]}})
    initial={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'composite','name':'Exact composite cels - upstream source parts retained separately','locked':False}],'cels':cels,'frames':frames,'animations':[{'id':'rowan-NE-walk','frames':[f'{i:02}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'representation':'Honest flattened full-cel editable exchange, not a fully layered anatomical rig','scope':'Only frozen03 replacement plus exact four sole operations; other seven cels are current selected canonical controls','upstream_source_parts_maps_recipe':'retained-source','input_receipt':'INPUTS.json','protected_upper_hem_other_leg':'Current03 source paint retained; nine explicit natural foreground occlusions remain as frozen in source receipt','timing':'9 ticks at160Hz each; .45s loop; sidecar authoritative over ASE milliseconds','new_art_changes':0,'model_calls':0,'canonical_writes':0,'normal_speed_playback_acceptance':False}}
    ids=[f'{i:02}'for i in range(8)]
    for i,im in enumerate(render_frames(initial,ids)):assert im.tobytes()==rgba(ROOT/f'inputs/current/{i:02}.png').tobytes()
    cid='rowan-ne-03';h=History(initial)
    owner=mask(ROOT/'retained-source/masks/cloth-source.png')|mask(ROOT/'retained-source/masks/boot-source.png')
    for n in ['cloth','boot-before-contour-cleanup']:
        owner|=np.load(ROOT/f'retained-source/maps/{n}.npz',allow_pickle=False)['source_xy'][:,:,0]>=0
    coords=[[int(x),int(y)]for y,x in zip(*np.where(owner))]
    tx1=candidate_transaction(h.project,cid,Image.open(ROOT/'inputs/03-completed-owner-before-sole.png'),coords,reason='Import frozen completed-owner source03 transition before sole cleanup; literal source/target owner only')
    r1=h.apply(tx1);middle=copy.deepcopy(h.project)
    assert render_cel(middle,cid).tobytes()==rgba(ROOT/'inputs/03-completed-owner-before-sole.png').tobytes()
    s=json.loads((ROOT/'retained-source/RECIPE.json').read_text());ops=s['sole_cleanup']['operations'];sole=[op['target']for op in ops]
    assert sole==[[66,111],[67,111],[73,111],[69,110]]
    donor=ops[-1]['source_RGBA'];index=next(i for i,c in enumerate(h.project['palette'])if c==donor)
    for op in ops:x,y=op['target'];assert list(render_cel(h.project,cid).getpixel((x,y)))==op['expected_before_RGBA']
    guard={'op':'candidate_patch','cel_id':cid,'mask':sole,'candidate_pixels':list(h.project['cels'][cid]['pixels']),'expected_cel_sha256':cel_hash(h.project,cid)}
    tx2={'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(h.project),'reason':'Exact frozen four-pixel sole cleanup: same-cel precondition, three erasures and one literal source-palette paint; no angle or other paint change','operations':[guard,{'op':'erase','cel_id':cid,'points':[op['target']for op in ops if op['op']=='erase'],'mask':sole},{'op':'paint','cel_id':cid,'points':[[69,110,index]],'mask':sole}]}
    r2=h.apply(tx2);final=copy.deepcopy(h.project);journal=h.journal()
    assert set(r1['diff']['frames'])=={'03'} and set(r2['diff']['frames'])=={'03'}
    assert r2['diff']['frames']['03']['changed_pixels']==4
    changed=np.any(rgba(ROOT/'inputs/03-completed-owner-before-sole.png')!=rgba(ROOT/'inputs/expected-final/03.png'),axis=2)
    allowed=np.zeros((128,128),bool)
    for x,y in sole:allowed[y,x]=True
    assert np.array_equal(changed,allowed)
    rows=[]
    for i,im in enumerate(render_frames(final,ids)):
        expect=ROOT/f'inputs/expected-final/{i:02}.png';assert im.tobytes()==rgba(expect).tobytes()
        dst=ROOT/f'editor-render/{i:02}.png';im.save(dst);assert dst.read_bytes()==expect.read_bytes()
        if i!=3:assert final['cels'][f'rowan-ne-{i:02}']==initial['cels'][f'rowan-ne-{i:02}']
        rows.append({'phase':i,'RGBA_exact':True,'PNG_exact':True,'sha256':sha(dst),'protected_other_seven_cel_exact':i!=3})
    mh,fh=project_hash(middle),project_hash(final)
    h.undo();assert project_hash(h.project)==mh
    h.undo();assert project_hash(h.project)==project_hash(initial)
    h.redo();assert project_hash(h.project)==mh
    h.redo();assert project_hash(h.project)==fh
    assert project_hash(History.replay(initial,journal).project)==fh
    neg=[]
    for name,start,tx in [('import',initial,tx1),('sole',middle,tx2)]:
        bad=copy.deepcopy(tx);bad['expected_project_sha256']='0'*64;t=History(start);neg.append(rejected(t,lambda:t.apply(bad),name+' stale project'))
        bad=copy.deepcopy(tx);next(o for o in bad['operations']if o['op']=='candidate_patch')['expected_cel_sha256']='0'*64;bad['operations'].insert(0,{'op':'palette_add','rgba':[1,2,3,4]});t=History(start);neg.append(rejected(t,lambda:t.apply(bad),name+' stale cel after staged palette mutation'))
    badim=Image.open(ROOT/'inputs/03-completed-owner-before-sole.png').convert('RGBA');badim.putpixel((64,10),(255,0,170,255));assert [64,10]not in coords
    t=History(initial);neg.append(rejected(t,lambda:candidate_transaction(t.project,cid,badim,coords),'candidate RGBA outside literal owner'))
    bad=copy.deepcopy(tx1);next(o for o in bad['operations']if o['op']=='candidate_patch')['candidate_pixels'][10*128+64]=1;bad['operations'].insert(0,{'op':'palette_add','rgba':[1,2,3,4]});t=History(initial);neg.append(rejected(t,lambda:t.apply(bad),'indexed candidate outside owner after staged mutation'))
    bad=copy.deepcopy(tx2);bad['operations'].insert(0,{'op':'palette_add','rgba':[1,2,3,4]});next(o for o in bad['operations']if o['op']=='erase')['points'].append([64,10]);t=History(middle);neg.append(rejected(t,lambda:t.apply(bad),'sole erase outside exact four-pixel mask after staged mutation'))
    for name,obj in [('initial',initial),('after-import',middle),('final',final),('journal',journal),('01-import-transaction',tx1),('01-import-receipt',r1),('02-sole-transaction',tx2),('02-sole-receipt',r2),('owners',{'import03':coords,'sole03':sole})]:save(ROOT/f'projects/{name}.json',obj)
    export_project(final,ROOT/'exports');ase=export_aseprite(final,ROOT/'exchange/rowan-ne-final.aseprite',animation_id='rowan-NE-walk')
    clock={'schema':'authoritative-rowan-ne-clock/v1','fps':160,'duration_ticks':[9]*8,'holds':[[9,160]]*8,'cycle':[9,20],'pivot':[64,112],'stage':[128,128],'ASE_quantized_ms':[x['milliseconds']for x in ase['timing']],'timing_quantization':ase['timing'],'limitation':'Native ASE milliseconds are a quantized preview. Original rational ticks remain authoritative. No normal-speed or gameplay acceptance.'};write(ROOT/'exchange/RATIONAL-CLOCK.json',clock)
    r={'status':'PASS source replay and two guarded editor transactions; native tool pending','representation':'Flattened composite cels, retained visible source components/maps separate','actual_transactions':2,'second_transaction_semantics':'A no-op candidate_patch supplies an actual same-cel guard, then erase3 and paint1; one atomic transaction','initial_project_sha256':project_hash(initial),'after_import_project_sha256':mh,'final_project_sha256':fh,'all8_RGBA_PNG_exact':True,'other_seven_cel_indices_exact':True,'undo_import_and_sole_exact':True,'redo_import_and_sole_exact':True,'journal_replay_exact':True,'atomic_rejections':neg,'frames':rows,'import_owner_pixels':len(coords),'sole_owner_pixels':4,'native_quantized_ms':clock['ASE_quantized_ms'],'source_replay':'source-replay/SOURCE-REPLAY-RECEIPT.json','new_art_changes':0,'model_calls':0,'canonical_writes':0,'normal_speed_acceptance':False}
    write(ROOT/'verification/EDITOR-RECEIPT.json',r)
    print(json.dumps({k:v for k,v in r.items()if k not in ['frames','atomic_rejections']}))

if __name__=='__main__':main()

"""Pinned construction policy and immutable/reload/clock oracles, no artwork claims."""
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from sprite_workbench import construction_core as tk
from sprite_workbench.construction import (save_project, load_project, create_history,
    load_history, edit_history, move_history, from_sequence, render_animation)
from sprite_workbench.core import Store, ValidationError, UnsupportedCapability, save_sequence, load_sequence


def fixture():
    return {"schema":"sprite-edit-project/v1", "canvas":{"width":4,"height":3,"render_pivot":[2,1],"ground_pivot":[2,3]},
        "palette":[[0,0,0,0],[255,0,0,255],[0,0,255,255],[0,255,0,128],[255,0,0,255],[11,22,33,0]],
        "layers":[{"id":"back","name":"Back","locked":False},{"id":"front","name":"Front","locked":False}],
        "cels":{"a":{"layer_id":"back","pixels":[0,1,0,0,0,1,4,0,0,0,5,0]},
                "b":{"layer_id":"front","pixels":[0,0,0,0,0,2,0,0,0,0,0,0]},
                "unbound":{"layer_id":"back","pixels":[0,0,0,0,0,0,0,0,0,0,0,1]}},
        "frames":[{"id":"f0","duration_ticks":3,"cels":{"back":"a","front":"b"},"landmarks":{"hand":[1,1]}},
                  {"id":"f1","duration_ticks":5,"cels":{"back":"a"},"landmarks":{}}],
        "animations":[{"id":"clip","frames":["f0","f1","f1"],"fps":60,"loop":True,"events":[{"at_tick":3,"name":"marker"}]}],
        "provenance":{"source":"explicit mechanical fixture", "unicode":{"\U0001f642":.000001,"\uffff":-0.0}}}


def tx(project, *operations):
    return {"schema":"sprite-edit-transaction/v1","expected_project_sha256":tk.project_hash(project),
            "reason":"Observed deterministic marker change","operations":list(operations)}


def test_pin_exact_module_identities_and_import_surface():
    manifest=json.loads(Path('docs/construction/TOOLKIT-ORIGIN.json').read_text())
    assert manifest['module_count']==len(manifest['modules'])==8
    for row in manifest['modules']:
        actual=hashlib.sha256(Path(row['destination']).read_bytes()).hexdigest()
        assert row['byte_exact'] and row['pinned_sha256']==row['original_sha256']
        if Path(row['destination']).name=='aseprite.py' and actual!=row['pinned_sha256']:
            adapted=json.loads(Path('docs/construction/ASE-PARSER-ORIGIN.json').read_text())
            assert adapted['original_sha256']==row['original_sha256'] and adapted['current_sha256']==actual
        else:
            assert actual==row['pinned_sha256']
    assert all(callable(getattr(tk,name)) for name in ('export_aseprite','read_aseprite','import_aseprite','candidate_transaction','render_frame'))


def test_separate_hash_domains_immutable_project_and_aliases(tmp_path):
    store=Store(tmp_path); raw=fixture(); original=copy.deepcopy(raw)
    result=save_project(store,raw)
    assert result['project_hash']==tk.project_hash(original)
    assert result['project']!=result['project_hash']
    raw['palette'][1]=[1,2,3,255]
    restored=load_project(Store(tmp_path),result['project'])
    assert restored==original and restored['cels']['a']['pixels'][6]==4
    assert restored['palette'][1]==restored['palette'][4]
    restored['cels']['a']['pixels'][0]=2
    assert load_project(store,result['project'])==original
    assert store.get_head('construction') is None


def test_shared_cel_edit_affects_all_references_preserves_other_state(tmp_path):
    store=Store(tmp_path); p=fixture(); h=create_history(store,save_project(store,p)['project'])
    changed=edit_history(store,h['history'],tx(p,{'op':'paint','cel_id':'a','points':[[1,0,2]]}))
    q=load_project(store,changed['project'])
    assert q['cels']['a']['pixels'][1]==2 and p['cels']['a']['pixels'][1]==1
    assert set(changed['receipt']['diff']['frames'])=={'f0','f1'}
    assert all(d['coordinates']==[[1,0]] for d in changed['receipt']['diff']['frames'].values())
    assert q['frames']==p['frames'] and q['animations']==p['animations'] and q['canvas']==p['canvas'] and q['provenance']==p['provenance']


def test_palette_global_change_respects_index_alias_and_locked_unbound_cel(tmp_path):
    store=Store(tmp_path);p=fixture();h=create_history(store,save_project(store,p)['project'])
    changed=edit_history(store,h['history'],tx(p,{'op':'palette','index':1,'rgba':[33,77,99,255]}))
    q=load_project(store,changed['project'])
    assert q['palette'][4]==p['palette'][4] and q['cels']==p['cels']
    # Alias index4 remains red while index1 changes; this is indexed local policy.
    assert tk.render_frame(q,'f1').getpixel((2,1))==(255,0,0,255)
    assert tk.render_frame(q,'f1').getpixel((1,0))==(33,77,99,255)
    p['layers'][0]['locked']=True
    locked=create_history(store,save_project(store,p)['project'])
    for op in ({'op':'erase','cel_id':'a','points':[[1,0]]},
               {'op':'palette','index':1,'rgba':[2,3,4,255]},
               {'op':'translate_layer','layer_id':'back','dx':0,'dy':0}):
        with pytest.raises(ValidationError,match='locked'):
            edit_history(store,locked['history'],tx(p,op))


def test_history_reload_cursor_redo_branch_and_exact_undo(tmp_path):
    store=Store(tmp_path);p=fixture();initial=save_project(store,p)
    h=create_history(store,initial['project'])
    one=edit_history(store,h['history'],tx(p,{'op':'erase','cel_id':'b','points':[[1,1]]}))
    q=load_project(store,one['project'])
    two=edit_history(Store(tmp_path),one['history'],tx(q,{'op':'frame_timing','frame_id':'f1','duration_ticks':8}))
    undone=move_history(Store(tmp_path),two['history'],'undo')
    assert undone['project']==one['project']
    state=load_history(Store(tmp_path),undone['history'])
    assert state['journal']['cursor']==1 and len(state['journal']['receipts'])==2
    redone=move_history(Store(tmp_path),undone['history'],'redo')
    assert redone['project']==two['project'] and redone['history']==two['history']
    fullundo=move_history(store,move_history(store,redone['history'],'undo')['history'],'undo')
    assert fullundo['project']==initial['project'] and fullundo['project_hash']==initial['project_hash']
    branch=edit_history(store,undone['history'],tx(q,{'op':'paint','cel_id':'b','points':[[3,2,1]]}))
    branchstate=load_history(store,branch['history'])
    assert branchstate['journal']['cursor']==len(branchstate['journal']['receipts'])==2
    with pytest.raises(ValidationError,match='Nothing to redo'):move_history(store,branch['history'],'redo')


@pytest.mark.parametrize('action',['undo','redo'])
def test_empty_history_movement_fails_without_artifacts(tmp_path,action):
    store=Store(tmp_path);h=create_history(store,save_project(store,fixture())['project'])
    before=set((store.path/'blobs').iterdir())
    with pytest.raises(ValidationError,match='Nothing to'):move_history(store,h['history'],action)
    assert set((store.path/'blobs').iterdir())==before


def test_invalid_transaction_is_atomic_and_stale_guard_exact(tmp_path):
    store=Store(tmp_path);p=fixture();h=create_history(store,save_project(store,p)['project'])
    before=set((store.path/'blobs').iterdir())
    bad=tx(p,{'op':'paint','cel_id':'b','points':[[2,1,1]]},{'op':'paint','cel_id':'b','points':[[9,9,1]]})
    with pytest.raises(ValidationError,match='bounds'):edit_history(store,h['history'],bad)
    stale=tx(p,{'op':'erase','cel_id':'b','points':[[1,1]]});stale['expected_project_sha256']='0'*64
    with pytest.raises(ValidationError,match='Stale project'):edit_history(store,h['history'],stale)
    assert set((store.path/'blobs').iterdir())==before and load_project(store,h['project'])==p


def test_layer_translate_shared_once_including_unbound_and_clip_explicit(tmp_path):
    store=Store(tmp_path);p=fixture();p['cels']['unbound']['pixels'][11]=0
    h=create_history(store,save_project(store,p)['project'])
    changed=edit_history(store,h['history'],tx(p,{'op':'translate_layer','layer_id':'back','dx':1,'dy':0}))
    q=load_project(store,changed['project'])
    assert q['cels']['a']['pixels'][2]==1 and q['cels']['a']['pixels'][3]==0  # Shared cel translated once.
    with pytest.raises(ValidationError,match='clips'):edit_history(store,h['history'],tx(p,{'op':'translate','cel_id':'b','dx':9,'dy':0}))
    clipped=edit_history(store,h['history'],tx(p,{'op':'translate','cel_id':'b','dx':9,'dy':0,'allow_clip':True}))
    assert load_project(store,clipped['project'])['cels']['b']['pixels']==[0]*12


@pytest.mark.parametrize('tamper',['cursor','receipt','bool_diff','current','project_hash','extra'])
def test_forged_journal_or_cursor_project_rejects(tmp_path,tamper):
    store=Store(tmp_path);p=fixture();h=create_history(store,save_project(store,p)['project'])
    changed=edit_history(store,h['history'],tx(p,{'op':'erase','cel_id':'b','points':[[1,1]]}))
    doc=store.get_json(changed['history'])
    if tamper=='cursor':doc['journal']['cursor']=0
    elif tamper=='receipt':doc['journal']['receipts'][0]['after_sha256']='0'*64
    elif tamper=='bool_diff':doc['journal']['receipts'][0]['diff']['cels']['b']['changed_pixels']=True
    elif tamper=='current':doc['project']=h['project']
    elif tamper=='project_hash':doc['project_hash']='0'*64
    else:doc['journal']['unexpected']='field'
    forged=store.put_json(doc)
    with pytest.raises(ValidationError):load_history(store,forged)
    with pytest.raises(ValidationError):move_history(store,forged,'undo')


def test_candidate_mask_preconditions_and_partial_alpha(tmp_path):
    store=Store(tmp_path);p=fixture();h=create_history(store,save_project(store,p)['project'])
    image=tk.render_cel(p,'b');image.putpixel((2,1),(13,157,241,177))
    candidate=tk.candidate_transaction(p,'b',image,[[2,1]])
    changed=edit_history(store,h['history'],candidate)
    q=load_project(store,changed['project'])
    assert tk.render_cel(q,'b').getpixel((2,1))==(13,157,241,177)
    assert changed['receipt']['diff']['cels']['b']['coordinates']==[[2,1]]
    invalid=copy.deepcopy(candidate)
    invalid['operations'][-1]['candidate_pixels'][0]=1
    with pytest.raises(ValidationError,match='outside mask'):edit_history(store,h['history'],invalid)


def test_render_repeated_ids_rational_ticks_pivots_events_and_hidden_policy(tmp_path):
    store=Store(tmp_path);p=fixture();p['cels']['b']['pixels'][5]=3
    saved=save_project(store,p);rendered=render_animation(store,saved['project'],'clip')
    doc,arrays=load_sequence(store,rendered['sequence'])
    assert [f['duration'] for f in doc['frames']]==[[1,20],[1,12],[1,12]]
    assert doc['loop'] and doc['play_count']==0 and doc['frames'][1]['raster']==doc['frames'][2]['raster']
    assert all(f['pivot']==[2,1] for f in doc['frames'])
    assert arrays[0][1,1].tolist()==[127,128,0,255]
    assert arrays[0][2,2].tolist()==[0,0,0,0]  # Source palette hidden RGB retained; composite explicitly normalizes.
    assert load_project(store,saved['project'])['palette'][5]==[11,22,33,0]
    assert doc['metadata']['construction_project']==saved['project'] and doc['metadata']['source_ids']==[saved['project']]
    assert doc['metadata']['frame_ids']==['f0','f1','f1'] and doc['metadata']['events']==p['animations'][0]['events']


def clean_arrays():
    a=np.zeros((2,3,4),np.uint8);a[0,0]=[17,29,53,255];a[1,2]=[13,157,241,177]
    b=a.copy();b[0,2]=[71,83,97,255]
    return [a,a.copy(),b]


def test_from_sequence_exact_auto_clock_shared_cels_lineage_and_roundtrip(tmp_path):
    store=Store(tmp_path);arrays=clean_arrays();durations=[Fraction(1,30),Fraction(2,15),Fraction(7,60)]
    source=save_sequence(store,arrays,durations,pivots=[(1,2)]*3,directions=['north']*3)
    imported=from_sequence(store,source,animation_id='supplied')
    p=load_project(store,imported['project'])
    assert store.get_json(imported['project'])['source_sequence']==source
    assert p['animations'][0]['fps']==60 and [f['duration_ticks'] for f in p['frames']]==[2,8,7]
    assert p['frames'][0]['cels']==p['frames'][1]['cels'] and len(p['cels'])==2
    rendered=render_animation(store,imported['project'],'supplied');doc,result=load_sequence(store,rendered['sequence'])
    assert [f['duration'] for f in doc['frames']]==[[1,30],[2,15],[7,60]]
    assert all(f['pivot']==[1,2] and f['direction']=='north' for f in doc['frames'])
    assert all(np.array_equal(a,b) for a,b in zip(arrays,result))
    history=create_history(store,imported['project'])
    edited=edit_history(store,history['history'],tx(p,{'op':'paint','cel_id':'cel-0','points':[[2,0,1]]}))
    assert store.get_json(edited['project'])['source_sequence']==source


@pytest.mark.parametrize('case',['finite_plays','hidden_rgb','mixed_pivot','mixed_direction','fractional_pivot','clock','huge_fps'])
def test_sequence_admission_refuses_lossy_mapping(tmp_path,case):
    store=Store(tmp_path);arrays=clean_arrays();kwargs={'pivots':[(1,2)]*3,'directions':['north']*3}
    holds=[Fraction(1,30)]*3;fps=None
    if case=='finite_plays':kwargs['play_count']=2
    elif case=='hidden_rgb':arrays[0][0,1]=[11,22,33,0]
    elif case=='mixed_pivot':kwargs['pivots']=[(1,2),(2,2),(1,2)]
    elif case=='mixed_direction':kwargs['directions']=['north','east','north']
    elif case=='fractional_pivot':kwargs['pivots']=[(1.5,2)]*3
    elif case=='clock':holds=[Fraction(1,9_007_199_254_740_993)]*3
    else:fps=2**4096
    seq=save_sequence(store,arrays,holds,**kwargs)
    before=set((store.path/'blobs').iterdir())
    with pytest.raises(UnsupportedCapability):from_sequence(store,seq,fps=fps)
    assert set((store.path/'blobs').iterdir())==before


def test_explicit_binary_float_fps_and_nonobject_provenance(tmp_path):
    store=Store(tmp_path);p=fixture();p['provenance']=None;p['animations'][0]['fps']=7.5
    saved=save_project(store,p);out=render_animation(store,saved['project'],'clip');doc,_=load_sequence(store,out['sequence'])
    assert [f['duration'] for f in doc['frames']]==[[2,5],[2,3],[2,3]]
    assert all(f['direction']=='unspecified' for f in doc['frames'])
    p['animations'][0]['fps']=.1
    out=render_animation(store,save_project(store,p)['project'],'clip');doc,_=load_sequence(store,out['sequence'])
    assert Fraction(*doc['frames'][0]['duration'])==Fraction(3)/Fraction(.1)
    p['animations'][0]['fps']=.0001
    with pytest.raises(UnsupportedCapability,match='3600'):render_animation(store,save_project(store,p)['project'],'clip')


@pytest.mark.parametrize('mutate',[lambda p:p['canvas'].update(width=True),lambda p:p.update(provenance={'bad':float('nan')}),
    lambda p:p['cels']['a']['pixels'].__setitem__(0,True),lambda p:p['animations'][0].update(fps=float('inf'))])
def test_invalid_raw_json_domains_fail_structured_without_store_writes(tmp_path,mutate):
    store=Store(tmp_path);p=fixture();mutate(p)
    with pytest.raises(ValidationError):save_project(store,p)
    assert not list((store.path/'blobs').iterdir())


def test_wrong_typed_envelopes_and_project_hash_refuse(tmp_path):
    store=Store(tmp_path);saved=save_project(store,fixture());doc=store.get_json(saved['project'])
    doc['project_hash']='0'*64
    with pytest.raises(ValidationError,match='hash mismatch'):load_project(store,store.put_json(doc))
    doc['version']=True
    with pytest.raises(ValidationError,match='version1'):load_project(store,store.put_json(doc))
    with pytest.raises(ValidationError):move_history(store,saved['project'],'redo')
    with pytest.raises(ValidationError):move_history(store,saved['project'],'other')


@pytest.mark.parametrize('field',['fps','provenance'])
def test_unsafe_python_integer_rejected_before_vendor_hash(tmp_path,monkeypatch,field):
    from sprite_workbench import construction
    p=fixture()
    if field=='fps':p['animations'][0]['fps']=10**400
    else:p['provenance']={'huge':10**400}
    def never(*args):raise AssertionError('Unsafe integer reached toolkit')
    monkeypatch.setattr(construction.toolkit,'project_hash',never)
    with pytest.raises(ValidationError,match='exact JavaScript range'):
        construction.save_project(Store(tmp_path),p)


def test_portable_decimal_loader_and_nonfinite_or_unsafe_literals():
    from sprite_workbench.construction import parse_project,project_hash
    p=fixture();text=json.dumps(p).replace('"width": 4','"width": 4.0').replace('"height": 3','"height": 3e0')
    parsed=parse_project(text)
    assert type(parsed['canvas']['width']) is int and parsed==p and project_hash(parsed)==tk.project_hash(p)
    for bad in ('NaN','Infinity','1e999',str(10**400)):
        text=json.dumps(p).replace('"width": 4','"width": '+bad)
        with pytest.raises(ValidationError):parse_project(text)
    with pytest.raises(ValidationError):parse_project('{"broken":')


@pytest.mark.parametrize('limit,value,message',[
    ('MAX_CEL_PIXELS',10,'aggregate cel pixel'),('MAX_CELS',1,'aggregate cel count'),
    ('MAX_LAYERS',1,'aggregate layer'),('MAX_FRAMES',1,'aggregate frame'),
    ('MAX_RENDER_WORK',40,'aggregate frame/layer render')])
def test_aggregate_project_admission_precedes_vendor_execution(tmp_path,monkeypatch,limit,value,message):
    from sprite_workbench import construction
    monkeypatch.setattr(construction,limit,value)
    def never(*args):raise AssertionError('Rejected aggregate reached toolkit')
    monkeypatch.setattr(construction.toolkit,'project_hash',never)
    store=Store(tmp_path)
    with pytest.raises(ValidationError,match=message):construction.save_project(store,fixture())
    assert not list((store.path/'blobs').iterdir())


def test_history_receipt_and_cumulative_replay_budgets(tmp_path,monkeypatch):
    from sprite_workbench import construction
    store=Store(tmp_path);p=fixture();h=create_history(store,save_project(store,p)['project'])
    one=edit_history(store,h['history'],tx(p,{'op':'erase','cel_id':'b','points':[[1,1]]}))
    q=load_project(store,one['project'])
    two=edit_history(store,one['history'],tx(q,{'op':'paint','cel_id':'b','points':[[2,1,2]]}))
    monkeypatch.setattr(construction,'MAX_HISTORY_RECEIPTS',1)
    with pytest.raises(ValidationError,match='receipt budget'):load_history(store,two['history'])
    monkeypatch.setattr(construction,'MAX_HISTORY_RECEIPTS',256)
    # V2 replays one checkpoint pair at a time and deduplicates equal frame
    # bindings. It has a separate aggregate work cap from a single operation.
    monkeypatch.setattr(construction,'MAX_HISTORY_REPLAY_WORK',150)
    with pytest.raises(ValidationError,match='journal replay work'):load_history(store,two['history'])
    # One receipt remains under150; another accepted operation would exceed total history budget.
    with pytest.raises(ValidationError,match='history edit work'):edit_history(store,one['history'],tx(q,{'op':'paint','cel_id':'b','points':[[2,1,2]]}))


def test_transaction_budget_and_hidden_alias_clipping(tmp_path,monkeypatch):
    from sprite_workbench import construction
    store=Store(tmp_path);p=fixture();h=create_history(store,save_project(store,p)['project'])
    monkeypatch.setattr(construction,'MAX_TRANSACTION_OPERATIONS',1)
    with pytest.raises(ValidationError,match='operations'):edit_history(store,h['history'],tx(p,
        {'op':'erase','cel_id':'b','points':[[1,1]]},{'op':'erase','cel_id':'b','points':[[2,1]]}))
    monkeypatch.setattr(construction,'MAX_TRANSACTION_OPERATIONS',256)
    # Index5 has alpha0 but is nonzero indexed content; toolkit clipping guard intentionally treats it as owned data.
    hidden=fixture();hidden['cels']['a']['pixels']=[0]*12;hidden['cels']['a']['pixels'][11]=5
    hh=create_history(store,save_project(store,hidden)['project'])
    with pytest.raises(ValidationError,match='clips'):edit_history(store,hh['history'],tx(hidden,{'op':'translate','cel_id':'a','dx':1,'dy':0}))


def test_cyclic_deep_json_and_render_budget_reject_structured(tmp_path,monkeypatch):
    from sprite_workbench import construction
    p=fixture();p['provenance']['cycle']=p
    with pytest.raises(ValidationError,match='cyclic'):save_project(Store(tmp_path),p)
    p=fixture();v={};p['provenance']=v
    for _ in range(66):v['child']={};v=v['child']
    with pytest.raises(ValidationError,match='nesting'):save_project(Store(tmp_path),p)
    store=Store(tmp_path);p=fixture();saved=save_project(store,p)
    monkeypatch.setattr(construction,'MAX_SEQUENCE_BYTES',10)
    with pytest.raises(ValidationError,match='byte budget'):render_animation(store,saved['project'],'clip')


def test_unsafe_integral_float_cannot_emit_unreloadable_canonical_integer(tmp_path):
    from sprite_workbench.construction import parse_project
    for value in (1e18,1e21,-1e18):
        p=fixture();p['provenance']['amount']=value
        with pytest.raises(ValidationError,match='integral float'):save_project(Store(tmp_path),p)
        with pytest.raises(ValidationError):parse_project(json.dumps(p))
    p=fixture();saved=save_project(Store(tmp_path),p)
    assert tk.project_hash(parse_project(tk.canonical_json(p)))==saved['project_hash']


def test_history_snapshot_and_import_aggregate_budgets(tmp_path,monkeypatch):
    from sprite_workbench import construction
    store=Store(tmp_path);p=fixture();h=create_history(store,save_project(store,p)['project'])
    one=edit_history(store,h['history'],tx(p,{'op':'erase','cel_id':'b','points':[[1,1]]}))
    monkeypatch.setattr(construction,'MAX_HISTORY_CEL_VALUES',100)
    with pytest.raises(ValidationError,match='snapshot index'):load_history(store,one['history'])
    with pytest.raises(ValidationError,match='snapshot index'):edit_history(store,h['history'],tx(p,{'op':'erase','cel_id':'b','points':[[1,1]]}))
    monkeypatch.setattr(construction,'MAX_RENDER_WORK',10)
    seq=save_sequence(store,clean_arrays(),[Fraction(1,30)]*3)
    with pytest.raises(ValidationError,match='aggregate cel/render'):from_sequence(store,seq)

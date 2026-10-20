"""Selected independent integration checks; no provider or artwork approval."""
import copy
import json
from pathlib import Path

import pytest

from sprite_workbench.core import Store, ValidationError
from sprite_workbench.construction import save_project, render_animation


def supplied_project():
    return json.loads(Path('examples/local-construction/source.json').read_text())


def test_selected_animation_repetition_budget_before_renderer(tmp_path,monkeypatch):
    from sprite_workbench import construction
    project=supplied_project()
    project['animations'][0]['frames']=[project['frames'][0]['id']]*10
    store=Store(tmp_path/'store')
    saved=save_project(store,project)
    declared_work=project['canvas']['width']*project['canvas']['height']*len(project['layers'])*len(project['frames'])
    monkeypatch.setattr(construction,'MAX_RENDER_WORK',declared_work*2)
    def forbidden_render(*args):
        raise AssertionError('Repeated animation exceeded budget before renderer')
    monkeypatch.setattr(construction.toolkit.core,'render_frames',forbidden_render)
    before=set((store.path/'blobs').iterdir())
    with pytest.raises(ValidationError,match='selected animation.*aggregate render work'):
        render_animation(store,saved['project'],project['animations'][0]['id'])
    assert set((store.path/'blobs').iterdir())==before


def empty_project():
    p=supplied_project();p['canvas'].update(width=3,height=1,render_pivot=[1,1],ground_pivot=[1,1])
    p['layers']=[];p['cels']={}
    for f in p['frames']:f['cels']={}
    return p


def test_empty_layers_still_charge_blank_canvas_admission_work(tmp_path,monkeypatch):
    from sprite_workbench import construction
    p=empty_project();store=Store(tmp_path/'store')
    monkeypatch.setattr(construction,'MAX_RENDER_WORK',5)
    def never(*args):raise AssertionError('Zero-layer project escaped allocation work admission')
    monkeypatch.setattr(construction.toolkit,'project_hash',never)
    with pytest.raises(ValidationError,match='aggregate frame/layer render'):
        save_project(store,p)
    assert not list((store.path/'blobs').iterdir())


def test_empty_layers_repeated_animation_still_charge_canvas_work(tmp_path,monkeypatch):
    from sprite_workbench import construction
    p=empty_project();p['animations'][0]['frames']=[p['frames'][0]['id']]*10
    store=Store(tmp_path/'store');saved=save_project(store,p)
    monkeypatch.setattr(construction,'MAX_RENDER_WORK',10)
    def never(*args):raise AssertionError('Zero-layer repeated render escaped work admission')
    monkeypatch.setattr(construction.toolkit.core,'render_frames',never)
    with pytest.raises(ValidationError,match='selected animation.*aggregate render work'):
        render_animation(store,saved['project'],p['animations'][0]['id'])


def test_empty_layers_transaction_diff_still_charges_blank_frame_work(tmp_path,monkeypatch):
    from sprite_workbench import construction
    p=empty_project();store=Store(tmp_path/'store');saved=save_project(store,p)
    history=construction.create_history(store,saved['project'])
    monkeypatch.setattr(construction,'MAX_RENDER_WORK',12)
    def never(*args):raise AssertionError('Zero-layer diff escaped work admission')
    monkeypatch.setattr(construction.toolkit.History,'apply',never)
    transaction={'schema':'sprite-edit-transaction/v1','expected_project_sha256':saved['project_hash'],
                 'reason':'Change a blank held frame','operations':[{'op':'frame_timing','frame_id':p['frames'][0]['id'],'duration_ticks':9}]}
    with pytest.raises(ValidationError,match='transaction work'):
        construction.edit_history(store,history['history'],transaction)


def clean_source(store):
    import numpy as np
    from sprite_workbench.core import save_sequence
    a=np.zeros((2,3,4),np.uint8);a[0,0]=[31,67,101,255];a[1,2]=[17,41,83,127]
    return save_sequence(store,[a,a.copy()],durations=[[1,10],[1,5]],pivots=[[1,1]]*2,directions=['east']*2)


def test_from_sequence_unchanged_native_roundtrip_keeps_current_project_identity(tmp_path):
    from sprite_workbench.construction_services import invoke_construction
    store=Store(tmp_path/'store')
    project=invoke_construction(store,'from_sequence',{'sequence':clean_source(store)})
    history=invoke_construction(store,'history',{'project':project['project']})
    native=invoke_construction(store,'ase_export',{'project':project['project'],'directory':str(tmp_path/'native')})
    imported=invoke_construction(store,'ase_import',{'path':native['ase_path'],'sidecar':native['sidecar_path']})
    assert imported['project_hash']==project['project_hash']
    assert imported['project']==project['project']  # Unchanged data must not lose its typed source envelope.
    rendered=invoke_construction(store,'render',{'project':imported['project'],'history':history['history'],
        'animation_id':'clip','import_provenance':imported['import_provenance']})
    assert rendered['sequence']


def test_native_binding_boolean_version_is_rejected_at_import(tmp_path):
    from sprite_workbench.construction_services import invoke_construction
    store=Store(tmp_path/'store');project=save_project(store,supplied_project())
    native=invoke_construction(store,'ase_export',{'project':project['project'],'directory':str(tmp_path/'native')})
    binding=store.get_json(native['binding']);binding['version']=True
    forged=store.put_json(binding)
    sidecar=json.loads(Path(native['sidecar_path']).read_text());sidecar['workbench']['binding']=forged
    changed=tmp_path/'changed-sidecar.json';changed.write_text(json.dumps(sidecar))
    with pytest.raises(ValidationError,match='authority|binding'):
        invoke_construction(store,'ase_import',{'path':native['ase_path'],'sidecar':str(changed)})


def test_playback_export_before_native_binding_cannot_bootstrap_new_store_import(tmp_path):
    from sprite_workbench.construction_services import invoke_construction
    from sprite_workbench.export import export_sequence,import_editable
    from sprite_workbench.construction_exchange import ExchangeError
    store=Store(tmp_path/'store');p=save_project(store,supplied_project())
    history=invoke_construction(store,'history',{'project':p['project']})
    rendered=invoke_construction(store,'render',{'project':p['project'],'history':history['history'],'animation_id':'diagnostic'})
    export_sequence(store,rendered['sequence'],tmp_path/'before',['editable'])
    native=invoke_construction(store,'ase_export',{'project':p['project'],'directory':str(tmp_path/'native')})
    fresh=Store(tmp_path/'fresh-before');import_editable(fresh,tmp_path/'before/editable')
    with pytest.raises(ValidationError,match='Missing artifact'):
        fresh.get_bytes(native['binding'])
    with pytest.raises(ExchangeError):
        invoke_construction(fresh,'ase_import',{'path':native['ase_path'],'sidecar':native['sidecar_path']})
    imported=invoke_construction(store,'ase_import',{'path':native['ase_path'],'sidecar':native['sidecar_path']})
    with_native=invoke_construction(store,'render',{'project':imported['project'],'history':history['history'],
        'animation_id':'diagnostic','import_provenance':imported['import_provenance']})
    export_sequence(store,with_native['sequence'],tmp_path/'after',['editable'])
    after=Store(tmp_path/'fresh-after');import_editable(after,tmp_path/'after/editable')
    reimported=invoke_construction(after,'ase_import',{'path':native['ase_path'],'sidecar':native['sidecar_path']})
    assert reimported['project']==p['project']


def test_service_history_replay_precedes_render_and_shared_channel_recovers(tmp_path,monkeypatch):
    import io
    from sprite_workbench.construction_services import invoke_construction
    from sprite_workbench.channel import serve
    from sprite_workbench import construction
    store=Store(tmp_path/'store');p=save_project(store,supplied_project())
    history=invoke_construction(store,'history',{'project':p['project']})
    corrupt=store.get_json(history['history']);corrupt['project_hash']='0'*64
    bad=store.put_json(corrupt)
    def never(*args):raise AssertionError('Forged history reached renderer')
    monkeypatch.setattr(construction,'render_animation',never)
    with pytest.raises(ValidationError):invoke_construction(store,'render',{'project':p['project'],'history':bad,'animation_id':'diagnostic'})
    rows=[{'id':1,'method':'local.construction.render','params':{'project':p['project'],'history':bad,'animation_id':'diagnostic'}},
          {'id':2,'method':'local.construction.get','params':{'project':p['project']}},
          {'id':3,'method':'system.shutdown'}]
    sink=io.StringIO();serve(store,base_dir=tmp_path,result_ref='render.sequence',
        source=io.StringIO(''.join(json.dumps(r)+'\n' for r in rows)),sink=sink)
    replies=[json.loads(x) for x in sink.getvalue().splitlines()]
    assert replies[1]['status']=='validation_error' and replies[2]['status']=='completed'
    assert replies[2]['result']['project']==p['project'] and store.get_head('construction') is None

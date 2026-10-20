"""Replay channels execute real APIs; diagnostics never award artistic acceptance."""
import json
from pathlib import Path
import shutil

import numpy as np
import pytest

from sprite_workbench.core import Store, ValidationError, load_sequence
from sprite_workbench.replay_geometry import FLOW_IDS, run_flow


def test_f02_callable_ownership_tracks_edit_exchange_and_deterministic_identity(tmp_path):
    first=run_flow('F02',Store(tmp_path/'source'),tmp_path/'F02')
    second=run_flow('F02',Store(tmp_path/'independent'),tmp_path/'F02-repeat')
    assert first['status']==second['status']=='completed'
    assert all(c['passed'] for c in first['checks'])
    assert first['inputs']==second['inputs'] and first['artifacts']==second['artifacts']
    assert first['provider_calls']==0 and first['artistic_acceptance']=='unreviewed'
    assert json.loads((tmp_path/'F02/replay-receipt.json').read_text())==first
    store=Store(tmp_path/'F02/fresh-store');doc,frames=load_sequence(store,first['artifacts']['sequence'])
    assert len(frames)==3 and [f['duration'] for f in doc['frames']]==[[1,10]]*3
    assert frames[0][1,1].tolist()==[255,255,0,255]
    assert frames[1][1,1].tolist()==[255,0,0,255]
    assert frames[0][3,3].tolist()==[11,22,33,0]
    np.testing.assert_array_equal(frames[1],frames[2])
    names={c['name'] for c in first['checks']}
    assert {'overlapping source ownership rejected','changed frozen reference frame rejected',
            'stale expected color rejects edit'} <= names


def test_f09_actual_pinned_effect_body_clock_edit_and_fresh_store(tmp_path):
    if shutil.which('node') is None:
        pytest.skip('Node unavailable; pinned VFX not executed or passed')
    result=run_flow('F09',Store(tmp_path/'source'),tmp_path/'F09')
    assert result['status']=='completed' and all(c['passed'] for c in result['checks'])
    fresh=Store(tmp_path/'F09/fresh-store')
    doc,frames=load_sequence(fresh,result['artifacts']['sequence'])
    assert len(frames)==8 and all(f['duration']==[1,12] for f in doc['frames'])
    assert frames[0][1,1].tolist()==[255,0,255,255]
    assert frames[1][1,1].tolist()==[255,0,0,255]
    assert any(np.any(a[20:50,20:50,3]) for a in frames[:-1])
    assert fresh.get_json(result['artifacts']['effect_recipe'])['kind']=='effect-recipe'
    assert result['reviews']['continuous_motion_viewed'] is False


def test_f10_actual_exports_unequal_holds_and_engine_when_available(tmp_path):
    result=run_flow('F10',Store(tmp_path/'source'),tmp_path/'F10')
    engine=result['exports']['engine_verification']
    available=shutil.which('godot') or shutil.which('godot4')
    if available:
        assert result['status']=='completed' and all(c['passed'] for c in result['checks'])
        assert engine['status']=='verified' and set(engine['cases'])=={'0','1','2'}
        for count,case in engine['cases'].items():
            assert case['measurement']['errors']==[] and case['measurement']['play_count']==int(count)
            assert len(case['measurement']['pixels'])==3
            assert Path(case['receipt']).is_file()
    else:
        assert result['status']=='partial' and engine['status']=='unsupported'
        assert result['checks'][-1]['passed'] is False
    assert result['exports']['formats']['apng']['num_plays']==2
    assert json.loads((tmp_path/'F10/export/review/review.json').read_text())['play_total']==[1,2]


def test_missing_engine_is_explicit_partial_not_a_pass(tmp_path,monkeypatch):
    monkeypatch.setattr('sprite_workbench.replay_geometry.shutil.which',lambda name:None)
    result=run_flow('F10',Store(tmp_path/'source'),tmp_path/'F10')
    assert result['status']=='partial'
    assert result['exports']['engine_verification']['status']=='unsupported'
    assert result['checks'][-1]['passed'] is False
    assert all(c['passed'] for c in result['checks'][:-1])
    assert result['exports']['formats']['godot']['status']=='written'  # File creation is not engine execution.


def test_unknown_flow_and_existing_outputs_are_preserved(tmp_path):
    store=Store(tmp_path/'source');out=tmp_path/'existing';out.mkdir();(out/'important').write_text('retain')
    with pytest.raises(ValidationError,match='fresh'):run_flow('F02',store,out)
    with pytest.raises(ValidationError,match='Unknown'):run_flow('F99',store,tmp_path/'unknown')
    assert (out/'important').read_text()=='retain' and not (tmp_path/'unknown').exists()
    assert FLOW_IDS==('F02','F09','F10')


def test_unavailable_engine_cannot_hide_corrupted_export(tmp_path,monkeypatch):
    from PIL import Image
    from sprite_workbench import replay_geometry
    original_export=replay_geometry.export_sequence
    def export_then_corrupt(store,sequence,directory,formats=None):
        report=original_export(store,sequence,directory) if formats is None else original_export(store,sequence,directory,formats)
        if Path(directory).name=='export':
            frame=Path(directory)/'frames/frame-0000.png'
            a=np.array(Image.open(frame).convert('RGBA'));a[0,0]=[99,88,77,255]
            Image.fromarray(a).save(frame)
        return report
    monkeypatch.setattr(replay_geometry,'export_sequence',export_then_corrupt)
    monkeypatch.setattr(replay_geometry.shutil,'which',lambda name:None)
    result=run_flow('F10',Store(tmp_path/'source'),tmp_path/'F10')
    assert result['exports']['engine_verification']['status']=='unsupported'
    assert result['status']=='failed'
    assert any(not c['passed'] and 'PNG and sheet' in c['name'] for c in result['checks'])

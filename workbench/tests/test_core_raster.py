import json
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import Store, ValidationError, load_sequence, save_sequence
from sprite_workbench.raster import apply_edits, crop, edit_sequence, paste

FIX = Path(__file__).parent / "fixtures" / "pixel-baseline"


def test_blob_integrity_hidden_rgb_rational_reload_and_atomic_head(tmp_path):
    store = Store(tmp_path)
    a = np.zeros((3, 4, 4), np.uint8); a[1, 1] = [19, 27, 35, 0]
    seq = save_sequence(store, [a, a.copy()], [Fraction(1, 30), Fraction(1, 15)], pivots=[(2, 3)]*2)
    reopened = Store(tmp_path)
    doc, frames = load_sequence(reopened, seq)
    assert doc['frames'][0]['duration'] == [1, 30]
    assert doc['frames'][1]['duration'] == [1, 15]
    assert doc['frames'][0]['raster'] == doc['frames'][1]['raster']
    assert frames[0][1, 1].tolist() == [19, 27, 35, 0]
    assert not frames[0].flags.writeable
    alternatives = [store.put_json({'kind':'test','number':i}) for i in range(8)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(lambda ident: Store(tmp_path).set_head('winner', ident, None), alternatives))
    assert sum(outcomes) == 1
    raw_id = store.get_json(doc['frames'][0]['raster'])['blob']
    (store.path/'blobs'/raw_id).write_bytes(b'corrupt')
    with pytest.raises(ValidationError, match='integrity'):
        reopened.get_raster(doc['frames'][0]['raster'])


def test_sequence_canvas_mismatch_rejects_before_reading_pixel_payload(tmp_path, monkeypatch):
    store = Store(tmp_path)
    source = save_sequence(store, [np.zeros((2, 2, 4), np.uint8)] * 64,
                           [Fraction(1, 24)] * 64)
    doc = store.get_json(source)
    raster = store.get_json(doc['frames'][0]['raster'])
    doc['canvas'] = [1, 1]  # Forged canvas formerly admitted all larger payloads.
    malformed = store.put_json(doc)
    original_get = store.get_bytes

    def no_pixel_payload(ident, **kwargs):
        if ident == raster['blob']:
            pytest.fail('Mismatched sequence read a pixel payload before rejecting its canvas')
        return original_get(ident, **kwargs)

    monkeypatch.setattr(store, 'get_bytes', no_pixel_payload)
    with pytest.raises(ValidationError, match='Frame/canvas dimensions differ'):
        load_sequence(store, malformed)


@pytest.mark.parametrize('case', json.loads((FIX/'cases.json').read_text())['cases'])
def test_F01_retained_vendor_guard_and_order_oracles(tmp_path, case):
    baseline = np.array(Image.open(FIX/'baseline.png').convert('RGBA'))
    layers = {'Body - diagnostic': np.stack([baseline[:, :16], baseline[:, 16:]])}
    original = layers['Body - diagnostic'].copy()
    store = Store(tmp_path)
    seq = save_sequence(store, list(layers['Body - diagnostic']), [Fraction(1,10),Fraction(1,5)])
    assert store.set_head('source', seq, None)
    if case['expected_local_outcome'] == 'reject':
        with pytest.raises(ValidationError): apply_edits(layers, case['changes'])
        assert store.get_head('source') == seq
    else:
        edited, audit = apply_edits(layers, case['changes'])
        expected = np.array(Image.open(FIX/(case['case']+'.png')).convert('RGBA'))
        assert np.array_equal(np.concatenate(list(edited['Body - diagnostic']), axis=1), expected)
        assert audit['status'] == 'candidate_needs_visual_review'
    assert np.array_equal(layers['Body - diagnostic'], original)


def test_whole_revision_rollback_protection_crop_paste_and_stale_publish(tmp_path):
    store = Store(tmp_path); a = np.zeros((8,8,4),np.uint8); a[3,3] = [255,0,0,255]
    seq = save_sequence(store,[a], [Fraction(1,5)])
    assert store.set_head('current',seq,None)
    change = {'operation':'patch_pixels','layer':'image','frames':[1],'reason':'Observed redpixel','pixels':[[3,3,'#ff0000','#00ff00']]}
    blocked = np.zeros((1,8,8),bool);blocked[0,3,3] = True
    with pytest.raises(ValidationError,match='protected'):
        edit_sequence(store,seq,[change],protected={'image':blocked},head='current',expected_head=seq)
    assert store.get_head('current') == seq
    ok = edit_sequence(store,seq,[change],head='current',expected_head=seq)
    stale = edit_sequence(store,seq,[change],head='current',expected_head=seq)
    assert ok['published'] and stale['status'] == 'stale_candidate'
    assert store.get_head('current') == ok['revision']
    raster = store.put_raster(a); packet = crop(store,raster,[2,2,4,4],node='owned-arm')
    with pytest.raises(ValidationError,match='guard'): paste(store,packet,packet['rgba'],expected='0'*64)
    patch = np.array(packet['rgba'],np.uint8);patch[1,1] = [0,0,0,0]
    pasted = paste(store,packet,patch,expected=packet['guard'])
    assert store.get_raster(pasted)[3,3].tolist() == [0,0,0,0]
    assert store.get_raster(raster)[3,3].tolist() == [255,0,0,255]


def test_fill_brush_and_snapshot_outline_independent_geometry():
    layers = {'image':np.zeros((1,8,8,4),np.uint8)}
    def op(kind,**extra):return {'operation':kind,'layer':'image','frames':[1],'reason':'Frozengeometrycontrol',**extra}
    changes = [op('brush',points=[[3,3]],size=2,shape='square',color='#ff0000'),
               op('select_mask',name='paint',selector={'kind':'rectangle','region':[3,3,4,4]}),
               op('flood_fill',seed=[3,3],expected='#ff0000',color='#00ff00',mask='paint',max_pixels=4)]
    result,audit = apply_edits(layers,changes)
    assert (result['image'][0,3:5,3:5] == [0,255,0,255]).all()
    assert (result['image'][0,...,3] != 0).sum() == 4
    with pytest.raises(ValidationError,match='max_pixels'):
        apply_edits(layers,changes[:-1]+[dict(changes[-1],max_pixels=3)])
    source = {'image':result['image']}
    twice = [op('outline',mode='outside',color='#000000'),op('outline',mode='outside',color='#0000ff')]
    outlined,_=apply_edits(source,twice)
    assert (outlined['image'][0,...,3] != 0).sum() == 12  #4source+8orthogonalneighbors, not a secondring
    assert (source['image'][0,...,3] != 0).sum() == 4

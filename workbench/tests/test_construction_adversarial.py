"""Frozen independent construction cases: indices/history/resource admission, no art score."""
import copy
import json
from pathlib import Path

import numpy as np
import pytest

from sprite_workbench import construction as c
from sprite_workbench.core import Store, ValidationError, UnsupportedCapability, load_sequence, save_sequence

ROOT=Path(__file__).resolve().parents[1]


def fixture():
    return copy.deepcopy(json.loads((ROOT/'docs/construction/SOURCE-AND-ACCEPTANCE.json').read_text())['independent_base_fixture'])


def transaction(project,*operations):
    return {'schema':'sprite-edit-transaction/v1','expected_project_sha256':c.project_hash(project),
            'reason':'independent frozen mechanical case','operations':list(operations)}


def history(tmp_path,project=None):
    store=Store(tmp_path/'store');project=fixture() if project is None else project
    saved=c.save_project(store,project);created=c.create_history(store,saved['project'])
    assert store.set_head('accepted',saved['project'],None)
    return store,project,saved,created


def test_independent_raw_indices_aliases_hidden_rgba_and_composite(tmp_path):
    store,p,saved,_=history(tmp_path)
    raw=c.load_project(Store(store.path),saved['project'])
    assert raw['cels']['shared']['pixels']==[2,3,4] and raw['palette'][1]==raw['palette'][2]
    assert list(c.toolkit.core.render_cel(raw,'shared').getdata())==[(17,31,43,255),(71,83,97,127),(29,37,41,0)]
    rendered=c.render_animation(store,saved['project'],'walk')
    doc,arrays=load_sequence(store,rendered['sequence'])
    assert arrays[0].tolist()==[[[17,31,43,255],[71,83,97,127],[0,0,0,0]]]
    assert [f['duration'] for f in doc['frames']]==[[1,60],[1,30]]
    assert doc['metadata']['events']==[{'at_tick':1,'name':'contact'}]
    assert doc['metadata']['ground_pivot']==[1,1] and doc['frames'][0]['pivot']==[1,0]
    assert store.get_head('accepted')==saved['project']


def test_independent_equal_color_alias_edit_and_exact_history(tmp_path):
    store,p,saved,h=history(tmp_path)
    edit=c.edit_history(store,h['history'],transaction(p,{'op':'paint','cel_id':'shared','points':[[0,0,1]]}))
    q=c.load_project(store,edit['project'])
    assert q['cels']['shared']['pixels']==[1,3,4] and q['frames']==p['frames']
    assert edit['project_hash']!=saved['project_hash']
    assert edit['receipt']['diff']['cels']['shared']['coordinates']==[[0,0]]
    assert edit['receipt']['diff']['frames']=={} # equal colors, different authoritative index
    undo=c.move_history(Store(store.path),edit['history'],'undo')
    assert undo['project']==saved['project'] and c.load_project(store,undo['project'])==p
    redo=c.move_history(store,undo['history'],'redo')
    assert redo['history']==edit['history'] and redo['project']==edit['project']
    edit['receipt']['transaction']['reason']='caller mutation'
    q['palette'][1][0]=99
    assert c.load_project(store,redo['project'])['palette'][1][0]==17
    assert c.load_history(store,redo['history'])['journal']['receipts'][0]['transaction']['reason']=='independent frozen mechanical case'


def test_independent_palette_shared_frames_and_undo_branch(tmp_path):
    store,p,saved,h=history(tmp_path)
    changed=c.edit_history(store,h['history'],transaction(p,{'op':'palette','index':2,'rgba':[101,103,107,255]}))
    q=c.load_project(store,changed['project']);assert q['cels']==p['cels']
    assert q['palette'][1]==[17,31,43,255] and q['palette'][2]==[101,103,107,255]
    assert changed['receipt']['diff']['cels']=={}
    assert set(changed['receipt']['diff']['frames'])=={'f0','f1'}
    assert all(v['coordinates']==[[0,0]] for v in changed['receipt']['diff']['frames'].values())
    undo=c.move_history(store,changed['history'],'undo')
    branch=c.edit_history(store,undo['history'],transaction(p,{'op':'erase','cel_id':'shared','points':[[0,0]]}))
    with pytest.raises(ValidationError):c.move_history(store,branch['history'],'redo')
    assert c.load_history(store,branch['history'])['journal']['cursor']==1
    assert len(c.load_history(store,branch['history'])['journal']['receipts'])==1
    assert c.load_project(store,saved['project'])==p


@pytest.mark.parametrize('kind',['cel','palette','outside_alias','event','bad_point','stale'])
def test_independent_rejection_is_atomic_and_keeps_head(tmp_path,kind):
    p=fixture()
    if kind in ['cel','palette']:p['layers'][0]['locked']=True
    if kind=='event':p['animations'][0]['events']=[{'at_tick':2,'name':'late'}]
    store,p,saved,h=history(tmp_path,p)
    ops={'cel':{'op':'erase','cel_id':'shared','points':[[0,0]]},
         'palette':{'op':'palette','index':2,'rgba':[1,2,3,255]},
         'outside_alias':{'op':'candidate_patch','cel_id':'shared','mask':[[1,0]],'candidate_pixels':[1,3,4],'expected_cel_sha256':c.toolkit.cel_hash(p,'shared')},
         'event':{'op':'frame_timing','frame_id':'f1','duration_ticks':1},
         'bad_point':{'op':'paint','cel_id':'shared','points':[[0,0,1],[99,0,1]]},
         'stale':{'op':'erase','cel_id':'shared','points':[[0,0]]}}
    tx=transaction(p,ops[kind])
    if kind=='stale':tx['expected_project_sha256']='0'*64
    before={v.name for v in (store.path/'blobs').iterdir()}
    with pytest.raises(ValidationError):c.edit_history(store,h['history'],tx)
    assert {v.name for v in (store.path/'blobs').iterdir()}==before
    assert c.load_project(store,saved['project'])==p and store.get_head('accepted')==saved['project']


def test_independent_nonzero_transparent_alias_is_not_silent_clip(tmp_path):
    store,p,saved,h=history(tmp_path)
    tx=transaction(p,{'op':'translate','cel_id':'shared','dx':1,'dy':0})
    with pytest.raises(ValidationError):c.edit_history(store,h['history'],tx)
    tx['operations'][0]['allow_clip']=True
    changed=c.edit_history(store,h['history'],tx)
    q=c.load_project(store,changed['project'])
    assert q['cels']['shared']['pixels']==[0,2,3] and q['frames']==p['frames']
    assert q['animations']==p['animations'] and q['canvas']==p['canvas']


@pytest.mark.parametrize('bad',['huge_int','huge_integral_float','nan','cycle','deep','surrogate'])
def test_independent_portable_finite_numeric_and_depth_guards(tmp_path,bad):
    p=fixture()
    if bad=='huge_int':p['animations'][0]['fps']=10**400
    elif bad=='huge_integral_float':p['provenance']['amount']=1e18
    elif bad=='nan':p['provenance']['amount']=float('nan')
    elif bad=='cycle':p['provenance']['cycle']=p
    elif bad=='deep':
        v=0
        for _ in range(70):v=[v]
        p['provenance']['deep']=v
    elif bad=='surrogate':p['provenance']['text']='\ud800'
    store=Store(tmp_path/'store');before={x.name for x in (store.path/'blobs').iterdir()}
    with pytest.raises(ValidationError):c.save_project(store,p)
    assert {x.name for x in (store.path/'blobs').iterdir()}==before


def test_independent_portable_decimal_and_canonical_key_domains(tmp_path):
    p=fixture();p['provenance']={'\ue000':2,'\U0001f600':1,'zero':-0.0}
    encoded=json.dumps(p).replace('"width": 3','"width": 3.0').replace('"duration_ticks": 1','"duration_ticks": 1e0')
    parsed=c.parse_project(encoded)
    assert type(parsed['canvas']['width']) is int
    assert c.project_hash(parsed)==c.project_hash(p)
    text=c.toolkit.canonical_json(p)
    assert text.index('😀')<text.index('\ue000') and '"zero":0' in text
    p['canvas']['width']=3.0
    with pytest.raises(ValidationError):c.save_project(Store(tmp_path/'store'),p)


def test_independent_partial_alpha_analytic_composite(tmp_path):
    p=fixture();p['canvas']['width']=1;p['palette']=[[0,0,0,0],[21,151,241,96],[201,33,18,64]]
    p['layers']=[{'id':'back','name':'Back','locked':False},{'id':'front','name':'Front','locked':False}]
    p['cels']={'b':{'layer_id':'back','pixels':[1]},'f':{'layer_id':'front','pixels':[2]}}
    for frame in p['frames']:frame['cels']={'back':'b','front':'f'}
    store=Store(tmp_path/'store');saved=c.save_project(store,p)
    rendered=c.render_animation(store,saved['project'],'walk')
    _,images=load_sequence(store,rendered['sequence'])
    assert images[0].tolist()==[[[106,95,136,136]]]


def test_independent_repeated_selected_layer_work_rejects_before_render(tmp_path,monkeypatch):
    p=fixture();p['layers'].append({'id':'over','name':'Over','locked':False})
    p['cels']['over']={'layer_id':'over','pixels':[1,0,0]}
    for f in p['frames']:f['cels']['over']='over'
    p['animations'][0]['frames']=['f0']*12
    store=Store(tmp_path/'store');saved=c.save_project(store,p)
    # Tiny equivalent counterexample: uniqueprojectwork12, selectedwork72>20.
    monkeypatch.setattr(c,'MAX_RENDER_WORK',20)
    def forbidden(*args):raise AssertionError('Renderer reached before selected-work rejection')
    monkeypatch.setattr(c.toolkit.core,'render_frames',forbidden)
    with pytest.raises(ValidationError):c.render_animation(store,saved['project'],'walk')


def test_independent_history_canonical_bool_and_cursor_tamper(tmp_path):
    store,p,_,h=history(tmp_path)
    changed=c.edit_history(store,h['history'],transaction(p,{'op':'erase','cel_id':'shared','points':[[0,0]]}))
    for mode in ['bool','cursor','missing_tx']:
        d=store.get_json(changed['history'])
        if mode=='bool':d['journal']['receipts'][0]['diff']['cels']['shared']['changed_pixels']=True
        elif mode=='cursor':d['journal']['cursor']=0
        else:d['journal']['receipts'][0].pop('transaction')
        tampered=store.put_json(d)
        with pytest.raises(ValidationError):c.load_history(Store(store.path),tampered)
    assert c.load_project(store,changed['project'])['cels']['shared']['pixels']==[0,3,4]


@pytest.mark.parametrize('bad',['hidden','repeats','pivots','direction'])
def test_independent_flat_sequence_import_preserves_loss_boundaries(tmp_path,bad):
    store=Store(tmp_path/'store');a=np.array([[[17,31,43,255],[0,0,0,0]]],dtype=np.uint8)
    if bad=='hidden':a[0,1]=[29,37,41,0]
    kwargs={'durations':[[1,12],[1,6]],'pivots':[[0,0],[0,0]],'directions':['south','south']}
    if bad=='repeats':kwargs['play_count']=2
    if bad=='pivots':kwargs['pivots'][1]=[1,0]
    if bad=='direction':kwargs['directions'][1]='east'
    sequence=save_sequence(store,[a,a],**kwargs)
    before={x.name for x in (store.path/'blobs').iterdir()}
    with pytest.raises(UnsupportedCapability):c.from_sequence(store,sequence)
    assert {x.name for x in (store.path/'blobs').iterdir()}==before

# Independent minimal ASE writer: deliberate format fixtures, not producer export.
import struct
import zlib


def _native_ase(width,height,frames,name='Body'):
    def chunk(kind,payload):return struct.pack('<IH',len(payload)+6,kind)+payload
    data=[]
    for fi,(ms,cels) in enumerate(frames):
        chunks=[]
        if fi==0:
            label=name.encode('utf-8')
            chunks.append(chunk(0x2004,struct.pack('<6HB3x',3,0,0,width,height,0,255)+struct.pack('<H',len(label))+label))
        for info in cels:
            kind=info.get('kind',0);xy=info.get('offset',[0,0])
            body=struct.pack('<HhhBHh5x',info.get('layer',0),*xy,255,kind,0)
            if kind==1:body+=struct.pack('<H',info['link'])
            else:
                body+=struct.pack('<HH',*info.get('size',[width,height]))
                body+=info['data'] if kind==0 else info.get('compressed',zlib.compress(info['data']))
            chunks.append(chunk(0x2005,body))
        payload=b''.join(chunks)
        data.append(struct.pack('<IHHH2xI',16+len(payload),0xf1fa,len(chunks),ms,0)+payload)
    payload=b''.join(data);header=bytearray(128)
    struct.pack_into('<IHHHHHIH',header,0,128+len(payload),0xa5e0,len(frames),width,height,32,1,frames[0][0])
    header[34:36]=b'\x01\x01'
    return bytes(header)+payload


def _exchange(tmp_path,project=None):
    from sprite_workbench.construction_exchange import export_ase
    store,p,saved,h=history(tmp_path,project)
    result=export_ase(store,saved['project'],tmp_path/'export')
    return store,p,saved,result


def test_independent_ase_unchanged_alias_sidecar_and_cumulative_clock(tmp_path):
    from sprite_workbench.construction_exchange import import_ase,validate_import_provenance,export_ase
    p=fixture();p['animations'][0]['frames']=['f0']*3
    store,p,saved,e=_exchange(tmp_path,p)
    assert [v['milliseconds'] for v in e['timing']]==[17,16,17]
    assert sum(v['milliseconds'] for v in e['timing'])==50
    result=import_ase(store,e['ase_path'],e['sidecar_path'])
    assert result['project']==saved['project'] and c.load_project(store,result['project'])==p
    assert validate_import_provenance(store,result['import_provenance'],project_id=result['project'])['native_pixels_changed'] is False
    sentinel=tmp_path/'export/sentinel';sentinel.write_bytes(b'keep')
    before=Path(e['ase_path']).read_bytes()
    with pytest.raises(ValidationError):export_ase(store,saved['project'],tmp_path/'export')
    assert sentinel.read_bytes()==b'keep' and Path(e['ase_path']).read_bytes()==before


def test_independent_cropped_linked_wire_geometry(tmp_path):
    from sprite_workbench.construction_exchange import import_ase
    store,p,saved,e=_exchange(tmp_path)
    color=bytes([17,31,43,255])
    native=_native_ase(3,1,[(17,[{'kind':0,'offset':[1,0],'size':[1,1],'data':color}]),
                           (33,[{'kind':1,'offset':[2,0],'link':0}])])
    path=tmp_path/'cropped-linked.ase';path.write_bytes(native)
    result=import_ase(store,path,e['sidecar_path']);q=c.load_project(store,result['project'])
    assert q['cels'][q['frames'][0]['cels']['body']]['pixels']==[0,1,0]
    assert q['cels'][q['frames'][1]['cels']['body']]['pixels']==[0,0,1]
    record=store.get_json(result['import_provenance'])
    assert record['inventory']['frames'][0]['cels'][0]['offset']==[1,0]
    assert record['inventory']['frames'][1]['cels'][0]['offset']==[2,0]
    assert record['inventory']['frames'][1]['cels'][0]['linked_frame']==0
    assert c.load_project(store,saved['project'])==p
    assert store.get_head('accepted')==saved['project']


def test_independent_shared_frame_external_edit_forks_only_selected_binding(tmp_path):
    from sprite_workbench.construction_exchange import import_ase
    store,p,saved,e=_exchange(tmp_path)
    original=bytes([17,31,43,255,71,83,97,127,29,37,41,0])
    changed=bytes([201,3,7,255])+original[4:]
    path=tmp_path/'edited.ase';path.write_bytes(_native_ase(3,1,[(17,[{'data':changed}]),(33,[{'data':original}])]))
    result=import_ase(store,path,e['sidecar_path']);q=c.load_project(store,result['project'])
    assert q['frames'][0]['cels']['body']!='shared' and q['frames'][1]['cels']['body']=='shared'
    assert q['cels']['shared']==p['cels']['shared'] and q['palette'][:5]==p['palette']
    assert q['cels'][q['frames'][0]['cels']['body']]['pixels'][1:]==[3,4]
    assert q['canvas']==p['canvas'] and q['animations']==p['animations']
    assert c.load_project(store,saved['project'])==p and store.get_head('accepted')==saved['project']


def test_independent_repeat_frame_inconsistent_external_edits_reject(tmp_path):
    from sprite_workbench.construction_exchange import import_ase,ExchangeError
    p=fixture();p['animations'][0]['frames']=['f0','f0']
    store,p,saved,e=_exchange(tmp_path,p)
    a=bytes([17,31,43,255,71,83,97,127,29,37,41,0]);b=bytes([201,3,7,255])+a[4:]
    path=tmp_path/'conflict.ase';path.write_bytes(_native_ase(3,1,[(17,[{'data':b}]),(16,[{'data':a}])]))
    with pytest.raises(ExchangeError) as caught:import_ase(store,path,e['sidecar_path'])
    assert store.get_json(caught.value.receipt)['status']=='failed'
    assert c.load_project(store,saved['project'])==p and store.get_head('accepted')==saved['project']


@pytest.mark.parametrize('kind',['inflate','truncated','trailing'])
def test_independent_bounded_zlib_before_image_allocation(tmp_path,monkeypatch,kind):
    from sprite_workbench.construction_core import aseprite as native
    raw=bytes([17,31,43,255]);encoded=zlib.compress(raw)
    if kind=='inflate':encoded=zlib.compress(b'\0'*65536)
    elif kind=='truncated':encoded=encoded[:-1]
    else:encoded+=b'trailing'
    data=_native_ase(1,1,[(17,[{'kind':2,'size':[1,1],'data':raw,'compressed':encoded}])])
    decoder_factory=native.zlib.decompressobj;limits=[]
    class Decoder:
        def __init__(self):self.decoder=decoder_factory()
        def decompress(self,data,max_length=0):
            limits.append(max_length);return self.decoder.decompress(data,max_length)
        def __getattr__(self,name):return getattr(self.decoder,name)
    monkeypatch.setattr(native.zlib,'decompressobj',Decoder)
    def forbidden(*args,**kwargs):raise AssertionError('PIL image allocated before malformed compressed cel rejection')
    monkeypatch.setattr(native.Image,'frombytes',forbidden)
    with pytest.raises((ValueError,ValidationError)):native.read_aseprite(tmp_path/'unused',data=data)
    assert limits==[5] # advertised1x1RGBA ceiling4+1, not actual64KiB inflation


def test_independent_duplicate_names_and_symlink_exchange_preserve_source(tmp_path):
    from sprite_workbench.construction_exchange import export_ase,import_ase,ExchangeError
    p=fixture();p['layers'].append({'id':'over','name':'Body','locked':False})
    store,p,saved,_=history(tmp_path,p)
    with pytest.raises(ExchangeError):export_ase(store,saved['project'],tmp_path/'ambiguous')
    assert not (tmp_path/'ambiguous').exists()
    store,p,saved,e=_exchange(tmp_path/'normal')
    link=tmp_path/'input-link.ase';link.symlink_to(e['ase_path'])
    before=Path(e['ase_path']).read_bytes()
    with pytest.raises(ExchangeError):import_ase(store,link,e['sidecar_path'])
    assert Path(e['ase_path']).read_bytes()==before


def test_independent_deep_sidecar_rejects_with_immutable_failure_receipt(tmp_path):
    from sprite_workbench.construction_exchange import import_ase,ExchangeError
    store,p,saved,e=_exchange(tmp_path)
    side=Path(e['sidecar_path']);raw=side.read_bytes().strip()
    side.write_bytes(raw[:-1]+b',"extra":'+b'['*500+b'0'+b']'*500+b'}')
    with pytest.raises(ExchangeError) as caught:import_ase(store,e['ase_path'],side)
    assert store.get_json(caught.value.receipt)['status']=='failed'
    assert store.get_head('accepted')==saved['project'] and c.load_project(store,saved['project'])==p


@pytest.mark.parametrize('mode',['bool_version','extra','native_blob','project_hash'])
def test_independent_invalid_binding_never_emits_unusable_success(tmp_path,mode):
    from sprite_workbench.construction_exchange import import_ase,ExchangeError
    store,p,saved,e=_exchange(tmp_path)
    bound=store.get_json(e['binding'])
    if mode=='bool_version':bound['version']=True
    elif mode=='extra':bound['extra']='not part of typedbinding'
    elif mode=='native_blob':bound['native_bytes']=store.put_bytes(b'not original native ASE')
    else:bound['project_hash']='0'*64
    bad_binding=store.put_json(bound)
    side=Path(e['sidecar_path']);envelope=json.loads(side.read_text());envelope['workbench']['binding']=bad_binding;side.write_text(json.dumps(envelope))
    with pytest.raises(ExchangeError):import_ase(store,e['ase_path'],side)
    assert store.get_head('accepted')==saved['project'] and c.load_project(store,saved['project'])==p


def test_independent_readonly_native_keeps_acquisition_envelope_and_history(tmp_path):
    from sprite_workbench.construction_exchange import export_ase,import_ase,validate_import_provenance
    store=Store(tmp_path/'store')
    a=np.array([[[17,31,43,255],[0,0,0,0],[71,83,97,127]]],dtype=np.uint8)
    b=np.array([[[0,0,0,0],[17,31,43,255],[71,83,97,127]]],dtype=np.uint8)
    sequence=save_sequence(store,[a,b],durations=[[1,60],[1,30]],pivots=[[1,0],[1,0]])
    saved=c.from_sequence(store,sequence);h=c.create_history(store,saved['project'])
    e=export_ase(store,saved['project'],tmp_path/'export')
    imported=import_ase(Store(store.path),e['ase_path'],e['sidecar_path'])
    assert imported['project']==saved['project']
    assert store.get_json(imported['project'])['source_sequence']==sequence
    assert c.load_history(store,h['history'])['project']==imported['project']
    assert validate_import_provenance(store,imported['import_provenance'])['source_project']==saved['project']
    rendered=c.render_animation(store,imported['project'],'clip')
    doc,arrays=load_sequence(store,rendered['sequence'])
    assert [f['duration'] for f in doc['frames']]==[[1,60],[1,30]]
    assert np.array_equal(arrays[0],a) and np.array_equal(arrays[1],b)

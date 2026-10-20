"""Actual layered native exchange and hostile admission controls; no art claims."""
import copy
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import zlib

import pytest
from PIL import Image

from sprite_workbench.core import Store
from sprite_workbench.construction_exchange import export_ase,import_ase,ExchangeError
from sprite_workbench.construction_core.aseprite import export_aseprite,read_aseprite,_chunk
from sprite_workbench.construction_core.core import EditError,render_frame,render_cel


def fixture():
    locked=[0]*12;locked[11]=2
    paint_a=[0]*12;paint_a[1]=4;paint_a[6]=3
    paint_b=[0]*12;paint_b[4]=1;paint_b[2]=3
    return {'schema':'sprite-edit-project/v1','canvas':{'width':4,'height':3,'render_pivot':[1,1],'ground_pivot':[2,2]},
      'palette':[[0,0,0,0],[255,0,0,255],[0,0,255,255],[0,255,0,255],[255,0,0,255]],
      'layers':[{'id':'background','name':'Locked background','locked':True},{'id':'paint','name':'Paint','locked':False}],
      'cels':{'locked':{'layer_id':'background','pixels':locked},'a':{'layer_id':'paint','pixels':paint_a},'b':{'layer_id':'paint','pixels':paint_b}},
      'frames':[{'id':name,'duration_ticks':duration,'cels':{'background':'locked','paint':cel},'landmarks':{'grip':[2,1]}}
          for name,duration,cel in [('f0',1,'a'),('f1',2,'b'),('f2',3,'a')]],
      'animations':[{'id':'clip','frames':['f0','f1','f2'],'fps':60,'loop':True,'events':[{'at_tick':2,'name':'contact'}]}]}


def project(store):
    from sprite_workbench.construction import save_project
    return save_project(store,fixture())


def tool(tmp_path,input_path,name,save=None):
    executable=shutil.which('libresprite')
    if executable is None:pytest.skip('LibreSprite missing; no native-tool proof claimed')
    command=[executable,'-b','--list-layers',str(input_path)]
    if save:command+=['--save-as',str(save)]
    command+=['--sheet',str(tmp_path/(name+'.png')),'--sheet-type','horizontal',
        '--data',str(tmp_path/(name+'.json')),'--format','json-array']
    env={**os.environ,'XDG_CONFIG_HOME':str(tmp_path/'tool-config'),'XDG_CACHE_HOME':str(tmp_path/'tool-cache')}
    try:
        result=subprocess.run(command,capture_output=True,text=True,timeout=30,env=env)
        receipt={'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    except (OSError,subprocess.TimeoutExpired) as error:
        receipt={'command':command,'error':type(error).__name__,'reason':str(error)}
    (tmp_path/(name+'-command.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    assert receipt.get('returncode')==0,receipt
    return json.loads((tmp_path/(name+'.json')).read_text()),Image.open(tmp_path/(name+'.png')).convert('RGBA')


def cropped_linked(data):
    """Construct documented cropped/linked cels; independent native tool checks them."""
    offset=128;frames=[]
    for fi in range(struct.unpack_from('<H',data,6)[0]):
        length,magic,count,ms,newcount=struct.unpack_from('<IHHH2xI',data,offset)
        pos=offset+16;chunks=[]
        for _ in range(newcount or count):
            size,kind=struct.unpack_from('<IH',data,pos);payload=data[pos+6:pos+size]
            if kind==0x2005:
                li,x,y,opacity,celtype,order=struct.unpack_from('<HhhBHh',payload)
                w,h=struct.unpack_from('<HH',payload,16)
                image=Image.frombytes('RGBA',(w,h),zlib.decompress(payload[20:]));box=image.getbbox()
                assert box is not None
                image=image.crop(box);x+=box[0];y+=box[1]
                if fi>0 and (li==0 or fi==2):
                    payload=struct.pack('<HhhBHh5xH',li,x,y,opacity,1,order,0)
                else:
                    payload=struct.pack('<HhhBHh5xHH',li,x,y,opacity,2,order,*image.size)+zlib.compress(image.tobytes())
            chunks.append(_chunk(kind,payload));pos+=size
        body=b''.join(chunks);frames.append(struct.pack('<IHHH2xI',16+len(body),magic,len(chunks),ms,len(chunks))+body);offset+=length
    header=bytearray(data[:128]);result=b''.join(frames);struct.pack_into('<I',header,0,128+len(result))
    return bytes(header)+result


def test_actual_libresprite_save_reopen_cropped_links_aliases_and_original_clock(tmp_path):
    from sprite_workbench.construction import load_project
    store=Store(tmp_path/'store');original=project(store)
    exported=export_ase(store,original['project'],tmp_path/'export','clip')
    assert [x['milliseconds'] for x in exported['timing']]==[17,33,50]
    native=tmp_path/'cropped.aseprite';native.write_bytes(cropped_linked(Path(exported['ase_path']).read_bytes()))
    source=read_aseprite(native)
    assert source['frames'][2]['raw_cels'][1].size==(2,2)
    assert import_ase(store,native,exported['sidecar_path'])['project']==original['project']
    saved=tmp_path/'saved.aseprite'
    for input_path,name,save in [(native,'first',saved),(saved,'reopened',None)]:
        meta,sheet=tool(tmp_path,input_path,name,save)
        assert [l['name'] for l in meta['meta']['layers']]==['Locked background','Paint']
        assert [f['duration'] for f in meta['frames']]==[17,33,50]
        for index,record in enumerate(meta['frames']):
            r=record['frame'];decoded=sheet.crop((r['x'],r['y'],r['x']+r['w'],r['y']+r['h']))
            assert decoded.tobytes()==render_frame(fixture(),'f'+str(index)).tobytes()
    imported=import_ase(store,saved,exported['sidecar_path'])
    assert imported['project']==original['project'] and imported['project_hash']==original['project_hash']
    assert load_project(store,imported['project'])==fixture()
    audit=store.get_json(imported['import_provenance'])
    assert audit['inventory']['frames'][0]['cels'][0]['offset']==[3,2]
    assert audit['native_pixels_changed'] is False
    assert load_project(store,imported['project'])['frames'][0]['cels']['paint']==load_project(store,imported['project'])['frames'][2]['cels']['paint']


def test_accepted_fine_pixel_edit_survives_actual_tool_without_changing_other_shared_instance(tmp_path):
    from sprite_workbench.construction import load_project
    store=Store(tmp_path/'store');original=project(store);exported=export_ase(store,original['project'],tmp_path/'export')
    candidate=fixture();candidate['palette'].append([13,157,241,177])
    candidate['cels']['one-instance']=copy.deepcopy(candidate['cels']['a']);candidate['cels']['one-instance']['pixels'][1]=5
    candidate['frames'][0]['cels']['paint']='one-instance'
    path=tmp_path/'edit.aseprite';export_aseprite(candidate,path)
    saved=tmp_path/'edited-saved.aseprite';tool(tmp_path,path,'edited',saved);metadata,sheet=tool(tmp_path,saved,'edited-reopened')
    for index,row in enumerate(metadata['frames']):
        r=row['frame'];decoded=sheet.crop((r['x'],r['y'],r['x']+r['w'],r['y']+r['h']))
        assert decoded.tobytes()==render_frame(candidate,'f'+str(index)).tobytes()
    result=import_ase(store,saved,exported['sidecar_path']);p=load_project(store,result['project'])
    assert render_cel(p,p['frames'][0]['cels']['paint']).getpixel((1,0))==(13,157,241,177)
    assert render_frame(p,'f1').tobytes()==render_frame(fixture(),'f1').tobytes()
    assert render_frame(p,'f2').tobytes()==render_frame(fixture(),'f2').tobytes()
    assert p['frames'][0]['cels']['paint']!=p['frames'][2]['cels']['paint']
    assert p['cels']['a']['pixels'][1]==4  # Identical red RGBA palette alias retained in untouched cel.
    assert p['canvas']==fixture()['canvas'] and p['animations']==fixture()['animations']
    assert [f['duration_ticks'] for f in p['frames']]==[1,2,3]


@pytest.mark.parametrize('case',['dirty-timing','dirty-project','dirty-sequence','layer-order','canvas','tool-timing','locked-pixels'])
def test_dirty_or_unsupported_native_changes_reject_with_receipt_and_no_head_mutation(tmp_path,case):
    store=Store(tmp_path/'store');original=project(store);store.set_head('candidate',original['project'],None)
    exported=export_ase(store,original['project'],tmp_path/'export');native=Path(exported['ase_path']);sidecar=Path(exported['sidecar_path'])
    if case.startswith('dirty'):
        meta=json.loads(sidecar.read_text())
        if case=='dirty-timing':meta['timing'][0]['milliseconds']=18
        elif case=='dirty-project':meta['project']['palette'][1][0]=254
        else:meta['sequence'].reverse()
        sidecar=tmp_path/'dirty.json';sidecar.write_text(json.dumps(meta))
    elif case in ('layer-order','locked-pixels'):
        p=fixture()
        if case=='layer-order':p['layers'].reverse()
        else:p['cels']['locked']['pixels'][11]=1
        native=tmp_path/'changed.aseprite';export_aseprite(p,native)
    else:
        data=bytearray(native.read_bytes())
        struct.pack_into('<H',data,8 if case=='canvas' else 136,5 if case=='canvas' else 18)
        native=tmp_path/'changed.aseprite';native.write_bytes(data)
    with pytest.raises(ExchangeError) as error:import_ase(store,native,sidecar)
    assert store.get_json(error.value.receipt)['status']=='failed'
    assert store.get_head('candidate')==original['project']


def test_existing_outputs_symlinks_missing_binding_and_duplicate_names_refuse(tmp_path):
    from sprite_workbench.construction import save_project
    store=Store(tmp_path/'store');original=project(store);exported=export_ase(store,original['project'],tmp_path/'export')
    before=Path(exported['ase_path']).read_bytes()
    with pytest.raises(ExchangeError):export_ase(store,original['project'],tmp_path/'export')
    assert Path(exported['ase_path']).read_bytes()==before
    alias=tmp_path/'alias';alias.symlink_to(tmp_path/'export',target_is_directory=True)
    with pytest.raises(ExchangeError):export_ase(store,original['project'],alias/'nested')
    link=tmp_path/'linked.aseprite';link.symlink_to(exported['ase_path'])
    with pytest.raises(ExchangeError):import_ase(store,link,exported['sidecar_path'])
    with pytest.raises(ExchangeError):import_ase(Store(tmp_path/'fresh-unbound'),exported['ase_path'],exported['sidecar_path'])
    p=fixture();p['layers'][1]['name']=p['layers'][0]['name'];duplicate=save_project(store,p)
    with pytest.raises(ExchangeError,match='unique'):export_ase(store,duplicate['project'],tmp_path/'duplicate')


def test_native_decoder_inflation_and_aggregate_budgets_precede_image_allocation(tmp_path,monkeypatch):
    from sprite_workbench.construction_core import aseprite
    layers=_chunk(0x2004,struct.pack('<6HB3xH',3,0,0,1,1,0,255,1)+b'L')
    bomb=_chunk(0x2005,struct.pack('<HhhBHh5xHH',0,0,0,255,2,0,1,1)+zlib.compress(b'x'*65536))
    frame=struct.pack('<IHHH2xI',16+len(layers+bomb),0xf1fa,2,17,2)+layers+bomb
    header=bytearray(128);struct.pack_into('<IHHHHHIH',header,0,128+len(frame),0xa5e0,1,1,1,32,1,17)
    allocations=[];real_decompressobj=zlib.decompressobj;limits=[]
    class Limited:
        def __init__(self):self.inner=real_decompressobj()
        def decompress(self,data,max_length):limits.append(max_length);return self.inner.decompress(data,max_length)
        def __getattr__(self,name):return getattr(self.inner,name)
    monkeypatch.setattr(aseprite.zlib,'decompressobj',Limited)
    monkeypatch.setattr(aseprite.Image,'frombytes',lambda *a,**k:allocations.append('frombytes'))
    with pytest.raises(EditError):read_aseprite(None,data=bytes(header)+frame)
    assert limits==[5] and allocations==[]
    big=bytearray(header);struct.pack_into('<IHHHHH',big,0,128,0xa5e0,512,1024,1024,32)
    with pytest.raises(EditError,match='aggregate'):read_aseprite(None,data=bytes(big))
    assert allocations==[]


def test_repeat_frame_instances_cannot_disagree_and_sidecar_clock_cannot_be_forged(tmp_path):
    from sprite_workbench.construction import save_project
    store=Store(tmp_path/'store');p=fixture();p['animations'][0]['frames']=['f0','f0','f1']
    original=save_project(store,p);exported=export_ase(store,original['project'],tmp_path/'export')
    # Same native frame count but different frame1 pixels: external instances of f0 disagree.
    q=fixture();q['frames'][0]['duration_ticks']=1;q['frames'][1]['duration_ticks']=1;q['frames'][2]['duration_ticks']=2
    external=tmp_path/'inconsistent.aseprite';export_aseprite(q,external)
    with pytest.raises(ExchangeError,match='Repeated'):import_ase(store,external,exported['sidecar_path'])
    # Direct bounded adapter independently derives timing, even outside Store-bound wrapper.
    meta=json.loads(Path(exported['sidecar_path']).read_text());meta['timing'][0]['milliseconds']=18
    data=Path(exported['ase_path']).read_bytes();changed=bytearray(data);struct.pack_into('<H',changed,136,18)
    from sprite_workbench.construction_core.aseprite import import_aseprite
    with pytest.raises(EditError,match='clock'):
        import_aseprite(None,'unused',native_data=bytes(changed),sidecar_data=json.dumps(meta).encode())


def test_provenance_validator_rejects_malformed_or_unrelated_dependencies(tmp_path):
    from sprite_workbench.construction import save_project
    from sprite_workbench.construction_exchange import validate_import_provenance
    from sprite_workbench.core import ValidationError
    store=Store(tmp_path/'store');original=project(store);exported=export_ase(store,original['project'],tmp_path/'export')
    result=import_ase(store,exported['ase_path'],exported['sidecar_path'])
    record=validate_import_provenance(store,result['import_provenance'],project_id=original['project'])
    assert record['source_project']==original['project']
    changed=fixture();changed['frames'][0]['duration_ticks']=2;other=save_project(store,changed)
    with pytest.raises(ValidationError,match='different project'):
        validate_import_provenance(store,result['import_provenance'],project_id=other['project'])
    for field,value in [('binding','0'*64),('native_bytes','0'*64),('project_hash','0'*64),('inventory',{}),('source_project',other['project'])]:
        bad={**record,field:value};ident=store.put_json(bad)
        with pytest.raises((ValidationError,EditError)):
            validate_import_provenance(store,ident,project_id=original['project'])


def test_bounded_portable_sidecar_rejects_nonfinite_and_preserves_integral_decimal_spelling(tmp_path):
    from sprite_workbench.construction_core.aseprite import import_aseprite
    store=Store(tmp_path/'store');original=project(store);exported=export_ase(store,original['project'],tmp_path/'export')
    meta=json.loads(Path(exported['sidecar_path']).read_text());meta['project']['canvas']['width']=4.0
    sidecar=tmp_path/'portable.json';sidecar.write_text(json.dumps(meta))
    assert import_ase(store,exported['ase_path'],sidecar)['project']==original['project']
    with pytest.raises((EditError,ValueError)):
        import_aseprite(None,'unused',native_data=Path(exported['ase_path']).read_bytes(),sidecar_data=b'{"x":NaN}')


@pytest.mark.parametrize('kind',[0x1234,0x2006,0x2007,0x2018])
def test_unknown_or_render_affecting_native_chunks_cannot_silently_flatten(tmp_path,kind):
    store=Store(tmp_path/'store');original=project(store);exported=export_ase(store,original['project'],tmp_path/'export')
    data=bytearray(Path(exported['ase_path']).read_bytes());extra=_chunk(kind,b'\x00'*40)
    length,magic,old,ms,new=struct.unpack_from('<IHHH2xI',data,128)
    data[144:144]=extra;struct.pack_into('<I',data,0,len(data))
    struct.pack_into('<IHHH2xI',data,128,length+len(extra),magic,old+1,ms,new+1)
    native=tmp_path/'unknown.aseprite';native.write_bytes(data)
    with pytest.raises(ExchangeError,match='chunk type'):import_ase(store,native,exported['sidecar_path'])


def test_cumulative_quantized_clock_keeps_original_repeated_tick_authority(tmp_path):
    from sprite_workbench.construction import save_project,load_project
    store=Store(tmp_path/'store');p=fixture();p['frames']=p['frames'][:1]
    p['animations'][0]['frames']=['f0']*3
    original=save_project(store,p);exported=export_ase(store,original['project'],tmp_path/'export')
    assert [r['milliseconds'] for r in exported['timing']]==[17,16,17]
    imported=import_ase(store,exported['ase_path'],exported['sidecar_path'])
    assert imported['project_hash']==original['project_hash'] and load_project(store,imported['project'])==p
    meta,_=tool(tmp_path,exported['ase_path'],'cumulative')
    assert [f['duration'] for f in meta['frames']]==[17,16,17]


def test_finite_but_unrepresentable_native_clock_rejects_with_failure_receipt(tmp_path):
    from sprite_workbench.construction import save_project
    store=Store(tmp_path/'store');p=fixture();p['animations'][0]['fps']=1e-300
    original=save_project(store,p)
    with pytest.raises(ExchangeError,match='clock') as error:export_ase(store,original['project'],tmp_path/'overflow')
    assert store.get_json(error.value.receipt)['status']=='failed'


def test_deep_sidecar_and_provenance_refuse_before_recursive_canonicalization(tmp_path):
    from sprite_workbench.construction_exchange import validate_import_provenance
    from sprite_workbench.core import ValidationError
    store=Store(tmp_path/'store');original=project(store);exported=export_ase(store,original['project'],tmp_path/'export')
    imported=import_ase(store,exported['ase_path'],exported['sidecar_path'])
    deep=0
    for _ in range(500):deep=[deep]
    meta=json.loads(Path(exported['sidecar_path']).read_text());meta['extra']=deep
    sidecar=tmp_path/'deep.json';sidecar.write_text(json.dumps(meta))
    with pytest.raises(ExchangeError,match='depth') as error:import_ase(store,exported['ase_path'],sidecar)
    assert store.get_json(error.value.receipt)['status']=='failed'
    record=store.get_json(imported['import_provenance']);bound=store.get_json(record['binding'])
    bound['adapter_sidecar']['extra']=deep;bad_binding=store.put_json(bound)
    malformed=store.put_json({**record,'binding':bad_binding})
    with pytest.raises(ValidationError,match='metadata'):
        validate_import_provenance(store,malformed,project_id=original['project'])
    malformed=store.put_json({**record,'unexpected':deep})
    with pytest.raises(ValidationError,match='metadata'):
        validate_import_provenance(store,malformed,project_id=original['project'])


def test_unchanged_native_from_sequence_preserves_typed_source_and_history_identity(tmp_path):
    import numpy as np
    from sprite_workbench.core import save_sequence
    from sprite_workbench.construction import from_sequence,create_history,load_history,render_animation
    store=Store(tmp_path/'store');sequence=save_sequence(store,[np.array([[[255,0,0,255],[0,0,0,0],[0,255,0,255]]],np.uint8)])
    original=from_sequence(store,sequence);history=create_history(store,original['project'])
    exported=export_ase(store,original['project'],tmp_path/'export');imported=import_ase(store,exported['ase_path'],exported['sidecar_path'])
    assert imported['project']==original['project'] and imported['project_hash']==original['project_hash']
    assert store.get_json(imported['project'])['source_sequence']==sequence
    assert load_history(store,history['history'])['project']==imported['project']
    assert render_animation(store,imported['project'],'clip')['sequence']


def test_binding_boolean_version_rejects_before_returning_unusable_provenance(tmp_path):
    store=Store(tmp_path/'store');original=project(store);exported=export_ase(store,original['project'],tmp_path/'export')
    binding=store.get_json(exported['binding']);binding['version']=True;forged=store.put_json(binding)
    meta=json.loads(Path(exported['sidecar_path']).read_text());meta['workbench']['binding']=forged
    sidecar=tmp_path/'boolean.json';sidecar.write_text(json.dumps(meta))
    with pytest.raises(ExchangeError,match='binding') as error:import_ase(store,exported['ase_path'],sidecar)
    assert store.get_json(error.value.receipt)['status']=='failed'


@pytest.mark.parametrize('field',['native_bytes','project_hash'])
def test_import_binding_source_hash_authority_matches_provenance_validator(tmp_path,field):
    store=Store(tmp_path/'store');original=project(store);exported=export_ase(store,original['project'],tmp_path/'export')
    binding=store.get_json(exported['binding'])
    binding[field]=store.put_bytes(b'wrong original native bytes') if field=='native_bytes' else '0'*64
    forged=store.put_json(binding)
    meta=json.loads(Path(exported['sidecar_path']).read_text());meta['workbench']['binding']=forged
    sidecar=tmp_path/'bad-authority.json';sidecar.write_text(json.dumps(meta))
    with pytest.raises(ExchangeError,match='source/hash') as error:import_ase(store,exported['ase_path'],sidecar)
    assert store.get_json(error.value.receipt)['status']=='failed'

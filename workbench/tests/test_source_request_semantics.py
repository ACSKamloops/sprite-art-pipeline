import copy
import json
import pytest
from sprite_workbench.capabilities import CapabilityRegistry
from sprite_workbench.core import ValidationError,UnsupportedCapability
from sprite_workbench.cli import main

PUBLIC='public:POST:/transfer-outfit-v2'
MCP='mcp:transfer_outfit'

def public(size,count):
    image={'image':{'base64':'fixture'},'size':{'width':size,'height':size}}
    return {'image_size':{'width':size,'height':size},'reference_image':copy.deepcopy(image),
            'frames':[copy.deepcopy(image) for _ in range(count)]}

@pytest.mark.parametrize('size,cap',[(32,15),(64,15),(65,8),(80,8),(81,3),(128,3),(256,3)])
def test_source_cap_boundaries_do_not_rewrite_frozen_schema_or_invoke(size,cap):
    registry=CapabilityRegistry();schema=registry.describe(PUBLIC)['exact_input_schema']
    req=public(size,cap);before=copy.deepcopy(req)
    assert registry.validate_source_request(PUBLIC,req)['source_semantics']['max_frames']==cap
    assert req==before and registry.describe(PUBLIC)['exact_input_schema']==schema
    overflow=public(size,cap+1)
    assert registry.validate_request(PUBLIC,overflow) # raw schema max16 is weaker than size-dependent cap
    with pytest.raises(ValidationError) as exc:registry.validate_source_request(PUBLIC,overflow)
    assert exc.value.to_dict()['validation_layer']=='source-derived'
    with pytest.raises(UnsupportedCapability):registry.invoke(PUBLIC,req)


def test_frozen_schema_layer_and_unknown_semantics_are_identified():
    registry=CapabilityRegistry()
    with pytest.raises(ValidationError) as exc:registry.validate_source_request(PUBLIC,public(257,2))
    assert exc.value.to_dict()['validation_layer']=='frozen-schema'
    result=registry.validate_source_request('public:POST:/generate-image-v2',{'description':'x','image_size':{'width':64,'height':64}})
    assert result['frozen_schema']=='passed' and result['status']=='not-covered'


def test_mcp_unknown_dimensions_stay_incomplete_without_network():
    registry=CapabilityRegistry();req={'frame_urls':['https://invalid.invalid/a.png']*4,'reference_image_url':'https://invalid.invalid/ref.png'}
    r=registry.validate_source_request(MCP,req)
    assert r['status']=='incomplete' and r['source_semantics']['max_frames'] is None
    req.update(width=256,height=256)
    with pytest.raises(ValidationError,match='at most3'):registry.validate_source_request(MCP,req)
    req['frame_urls']=req['frame_urls'][:3]
    assert registry.validate_source_request(MCP,req)['status']=='validated'
    req['frames_base64']=['other']*3
    with pytest.raises(ValidationError,match='exactly one'):registry.validate_source_request(MCP,req)


def test_cli_and_local_registry_report_layers(tmp_path,capsys):
    request=tmp_path/'request.json';request.write_text(json.dumps(public(256,4)))
    assert main(['--workspace',str(tmp_path/'store'),'validate-source-request',PUBLIC,str(request)])==2
    assert json.loads(capsys.readouterr().out)['validation_layer']=='source-derived'
    registry=CapabilityRegistry();registry.bind_source_validation()
    result=registry.invoke('local.requests.validate_source',{'capability':PUBLIC,'request':public(256,3)})
    assert result['status']=='validated' and not result['vendor_handler_implemented']



def test_reduce_colors_equal_dimensions_from_actual_runtime_constraint():
    import base64
    import numpy as np
    from sprite_workbench.export import png_bytes
    registry=CapabilityRegistry()
    def png(w,h):return {'base64':base64.b64encode(png_bytes(np.zeros((h,w,4),np.uint8))).decode()}
    request={'images':[png(94,46),png(94,46),png(95,47)],'num_colors':2}
    before=copy.deepcopy(request)
    assert registry.validate_request('public:POST:/reduce-colors',request)
    with pytest.raises(ValidationError) as exc:registry.validate_source_request('public:POST:/reduce-colors',request)
    assert exc.value.to_dict()['validation_layer']=='source-derived'
    assert exc.value.to_dict()['rule']=='reduce-colors-equal-dimensions'
    assert request==before
    request['images'].pop()
    assert registry.validate_source_request('public:POST:/reduce-colors',request)['source_semantics']['image_size']==[94,46]


def test_png_header_admission_is_bounded_and_validates_ihdr_crc():
    import base64,struct,zlib
    from sprite_workbench.source_semantics import png_header_size
    ihdr=b'IHDR'+struct.pack('>IIBBBBB',100000,100000,8,6,0,0,0)
    header=b'\x89PNG\r\n\x1a\n'+struct.pack('>I',13)+ihdr+struct.pack('>I',zlib.crc32(ihdr)&0xffffffff)
    with pytest.raises(ValidationError) as exc:png_header_size({'base64':base64.b64encode(header).decode()})
    assert exc.value.to_dict()['validation_layer']=='local-resource'
    damaged=header[:-1]+bytes([header[-1]^1])
    with pytest.raises(ValidationError,match='checksum'):png_header_size({'base64':base64.b64encode(damaged).decode()})
    with pytest.raises(ValidationError,match='base64'):png_header_size({'base64':'!'*44})

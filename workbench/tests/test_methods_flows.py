"""Independent supplied-art flow oracles; no network or private models."""
from fractions import Fraction
import base64
from io import BytesIO

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import Store, ValidationError, UnsupportedCapability, load_sequence
from sprite_workbench.prepare import prepare_request, choose_unzoom, correction_strength, palette_conditioner, prepare_prompt
from sprite_workbench.pose import project_pose, nearest_pose, flip_pose, source_shape_compatibility, save_supplied_motion, generate_motion, project_frames, draw_depth_channels, view_tilt
from sprite_workbench.terrain import topology_indices, connectivity_sheet, render_map, reblit_regions, save_terrain, generate_tiles
from sprite_workbench.assets import virtual_view, layout_shapes, render_ui, build_glyph_atlas, render_text, save_viseme_timeline, generate_asset, rasterize_font


def asymmetric():
    # Integer labels in channels include hidden RGB and partial alpha.
    a=np.zeros((3,5,4),np.uint8)
    a[...,0]=np.arange(15).reshape(3,5)+1
    a[...,1]=np.arange(15).reshape(3,5)+30
    a[...,3]=255
    a[1,2]=[91,92,93,0]; a[0,1]=[14,25,36,127]
    return a


def test_f07_prepare_reference_roi_mask_alpha_store_reload(tmp_path):
    store=Store(tmp_path); source=asymmetric(); before=source.copy()
    mask=np.zeros_like(source); mask[0,1,3]=1; mask[1,2,3]=255
    ref=source[::-1].copy()
    result=prepare_request('godot-raw-v1',[source],{'roi':[-1,0,6,3], 'mask':mask,
                          'pad_size':[8,5],'references':[source,ref],'store':store,'palette':True})
    # Requested ROI starts outside; center-pad adds (1,1); source x0->outputx2.
    expected=np.zeros((5,8,4),np.uint8);expected[1:4,2:7]=source
    expected[expected[...,3]==0,:3]=0
    np.testing.assert_array_equal(result['arrays'][0],expected)
    assert result['geometry'][0]['origin']==[-1,0]
    assert result['geometry'][0]['pad_offset']==[1,1]
    assert result['mask'][1,3]==255 and result['mask'][2,4]==255
    assert np.count_nonzero(result['mask'])==2 # alpha-bearing hidden-RGB pixel stays mask-selected
    assert [o['op'] for o in result['operations']]==['crop-pad','center-pad','zero-hidden-rgb','binary-mask','reference','reference']
    np.testing.assert_array_equal(source,before)
    reloaded=Store(tmp_path)
    np.testing.assert_array_equal(reloaded.get_raster(result['raster_ids'][0]),expected)
    normalized_ref=ref.copy();normalized_ref[normalized_ref[...,3]==0,:3]=0
    np.testing.assert_array_equal(reloaded.get_raster(result['reference_ids'][1]),normalized_ref)
    audit=reloaded.get_json(result['audit_id']);assert audit['operations']==result['operations']
    np.testing.assert_array_equal(reloaded.get_raster(audit['mask'])[...,3],result['mask'])
    assert reloaded.get_head('prepared') is None
    raw=base64.b64decode(result['descriptors'][0]['data']);assert raw==expected.tobytes()
    assert store.set_head('prepared',result['audit_id'],None)
    # Failed preparation never mutates published parent/head.
    with pytest.raises(ValidationError): prepare_request('godot-raw-v1',[source],{'pad_size':[1,1],'store':store})
    assert store.get_head('prepared')==result['audit_id']
    with pytest.raises(UnsupportedCapability) as exc: prepare_request('local-rgba-v1',[source],{'capability':'unzoom'})
    assert exc.value.to_dict()['status']=='unsupported'


def test_f07_nearest_png_hiddenrgb_palette_and_widget_dialects():
    source=asymmetric()
    result=prepare_request('local-rgba-v1',[source],{'output_size':[3,2],'encoding':'png'})
    # Independent left-cell index oracle: x=[0,1,3],y=[0,1].
    expected=source[np.array([0,1])[:,None],np.array([0,1,3])]
    np.testing.assert_array_equal(result['arrays'][0],expected)
    png=np.array(Image.open(BytesIO(base64.b64decode(result['descriptors'][0]['data']))).convert('RGBA'))
    np.testing.assert_array_equal(png,expected)
    full_png=prepare_request('local-rgba-v1',[source],{'encoding':'png'})
    decoded=np.array(Image.open(BytesIO(base64.b64decode(full_png['descriptors'][0]['data']))).convert('RGBA'))
    assert decoded[1,2].tolist()==[91,92,93,0] # PNG path independently retains hidden RGB
    raw=prepare_request('local-rgba-v1',[source],{})['arrays'][0]
    assert raw[1,2].tolist()==[91,92,93,0]
    palette=palette_conditioner(source);assert [91,92,93,0] not in palette['colors'] and [14,25,36,127] in palette['colors']
    assert choose_unzoom('lua-widget-v1','Custom') is None
    assert choose_unzoom('lua-widget-v1','Custom',16)==16
    assert choose_unzoom('lua-widget-v1','Auto')==0 and choose_unzoom('lua-widget-v1','None')==-1
    assert correction_strength('lua-widget-v1',200)==2
    assert correction_strength('web-widget-compat-v1',0)==.3
    assert correction_strength('web-widget-corrected-v1',0)==0
    with pytest.raises(ValidationError): correction_strength('godot-widget-v1',0)
    with pytest.raises(ValidationError): prepare_request('unknown',[source])
    large=np.tile(source[0:1,0:1],(2,1025,1))
    resized_ref=prepare_request('web-rotation-reference-nearest-v1',[source],{'references':[large],'reference_roles':['subject']})
    assert resized_ref['references'][0].shape==(1,1024,4)
    assert resized_ref['reference_roles']==['subject']


def test_f03_projection_analytic_depth_rank_flip_and_supplied_sequence(tmp_path):
    joints=[{'label':'NECK','x':.5,'y':.5,'z':.5},
            {'label':'LEFT ELBOW','x':.75,'y':.25,'z':.75},
            {'label':'RIGHT ELBOW','x':.75,'y':.25,'z':.75},
            {'label':'CUSTOM LEFT','x':.25,'y':.75,'z':.25}]
    # At yaw90 tilt0, (x,y,z) .75,.25,.75 -> projected .25,.25.
    lua=project_pose(joints,90,0,'lua-raw-v1'); godot=project_pose(joints,90,0,'godot-raw-v1')
    assert lua[1]['x']==pytest.approx(.25) and lua[1]['y']==pytest.approx(.25)
    assert lua[1]['depth']==pytest.approx(-.25) and godot[1]['depth']==pytest.approx(.25)
    assert lua[1]['z_index']==250 and godot[1]['z_index']==250
    rank=project_pose(joints,0,0,'lua-ranked-v1')
    assert [j['z_index'] for j in rank]==[2,1,1,3] # equal quantized depths share rank
    bridge=project_pose(joints,0,0,'godot-bridge64-v1')
    assert bridge[1]['x']==48 and bridge[1]['y']==16
    # Tilt90 makes Godot depth depend only on Y; Lua retains negative Z too.
    l=project_pose(joints,0,90,'lua-raw-v1')[1];g=project_pose(joints,0,90,'godot-raw-v1')[1]
    assert l['depth']==pytest.approx(-.5) and g['depth']==pytest.approx(-.25)
    catalog=flip_pose(joints,'catalog-z-v1'); general=flip_pose(joints,'godot-general-x-v1')
    assert catalog[1]['label']=='RIGHT ELBOW' and catalog[1]['z']==.25 and catalog[1]['x']==.75
    assert catalog[3]['label']=='CUSTOM LEFT' # exact catalog swap set
    assert general[1]['x']==.25 and general[1]['z']==.75
    assert source_shape_compatibility('lua-auto-direction')['matched_terms']==0
    assert source_shape_compatibility('lua-auto-tilt')['tilt_degrees']==-45
    assert view_tilt('side','godot-general-v1')==10 and view_tilt('side','godot-bridge-v1')==5
    store=Store(tmp_path);a=asymmetric()
    ident=save_supplied_motion(store,[a,a,a[::-1].copy()],[Fraction(1,30),Fraction(2,30),Fraction(4,30)],direction='north',joints=[lua,lua,godot])
    doc,arrays=load_sequence(Store(tmp_path),ident)
    assert [f['duration'] for f in doc['frames']]==[[1,30],[1,15],[2,15]]
    assert doc['frames'][0]['raster']==doc['frames'][1]['raster']
    assert all(f['direction']=='north' for f in doc['frames'])
    np.testing.assert_array_equal(arrays[2],a[::-1])
    with pytest.raises(UnsupportedCapability): generate_motion(joints)


def test_f03_asymmetric_nearest_search_domains_and_negative_shapes():
    # Reference is from an independent elementary yaw0/tilt5 equation.
    import math
    t=math.radians(5)
    joints=[{'label':label,'x':x,'y':y,'z':z} for label,x,y,z in
            [('NECK',.4,.3,.7),('NOSE',.7,.2,.9),('LEFT HIP',.2,.8,.3),('RIGHT HIP',.8,.7,.6)]]
    reference=[{'label':j['label'],'x':j['x'],'y':(j['y']-.5)*math.cos(t)-(j['z']-.5)*math.sin(t)+.5} for j in joints]
    g=nearest_pose(joints,reference,'godot-normalized-v1')
    assert g['examined']==72 and g['direction_degrees']==0 and g['tilt_degrees']==5 and g['error']<1e-20
    pixels=[{'label':j['label'],'x':j['x']*80+7,'y':j['y']*40-3} for j in reference]
    l=nearest_pose(joints,pixels,'lua-pixel-v1',canvas=[80,40])
    assert l['examined']==144 and l['direction_degrees']==0 and l['tilt_degrees']==5 and l['error']<1e-20
    with pytest.raises(ValidationError): nearest_pose(joints,pixels,'lua-pixel-v1')
    with pytest.raises(ValidationError): project_pose([{'label':'a','x':float('nan')}])
    with pytest.raises(ValidationError): project_pose([{'label':'a'},{'label':'a'}])


def test_f06_topology_sheet_map_patch_persist_reload(tmp_path):
    occupied=np.array([[True,True,False],[False,True,True]],bool)
    topology=topology_indices(occupied)
    np.testing.assert_array_equal(topology,[[2,12,-1],[-1,3,8]])
    # Four authored variants with asymmetric pixels; explicit order is not sorted.
    cells={k:asymmetric()+np.uint8(k) for k in (2,12,3,8)}
    sheet,meta=connectivity_sheet(cells,[12,2,8,3],columns=2)
    np.testing.assert_array_equal(sheet[:3,:5],cells[12]);assert meta['slots'][2]['rect']==[0,3,5,3]
    canvas=render_map(cells,topology)
    assert canvas.shape==(6,15,4)
    np.testing.assert_array_equal(canvas[3:6,10:15],cells[8]);assert not canvas[:3,10:15].any()
    patch=np.full((2,2,4),[30,40,50,255],np.uint8); mask=np.array([[True,False],[False,True]])
    expected=canvas[1:3,1:3].copy()
    revised,ops=reblit_regions(canvas,[{'array':patch,'origin':[1,1],'mask':mask,'expected':expected}])
    assert revised[1,1].tolist()==[30,40,50,255]
    np.testing.assert_array_equal(revised[1,2],canvas[1,2]);assert ops[0]['guarded']
    before=canvas.copy()
    with pytest.raises(ValidationError): reblit_regions(canvas,[{'array':patch,'origin':[1,1]}, {'array':patch,'origin':[1,1],'expected':expected}])
    np.testing.assert_array_equal(canvas,before)
    store=Store(tmp_path); terrain=save_terrain(store,cells,topology,topology={'convention':'N1E2S4W8-local-v1'})
    doc=Store(tmp_path).get_json(terrain);sequence,arrays=load_sequence(store,doc['sequence'])
    np.testing.assert_array_equal(arrays[0],canvas)
    assert doc['layout']==topology.tolist()
    with pytest.raises(ValidationError): render_map({2:cells[2]},topology)
    with pytest.raises(UnsupportedCapability): generate_tiles(occupied)


def test_f08_virtual_ui_supplied_glyph_viseme_whole_flow(tmp_path):
    assert virtual_view(320,208)==[512,333]
    pieces=[{'id':'panel','type':'rounded_rect','x':10,'y':20,'w':100,'h':50,'radius':8}]
    shape=layout_shapes(pieces,[512,512],[512,128])
    assert shape['pieces'][0]['x']==10 and shape['pieces'][0]['y']==5 and shape['pieces'][0]['radius']==4
    web=layout_shapes(pieces,[512,512],[512,128],profile='web-example-min-radius-v1')
    assert web['pieces'][0]['radius']==2
    assert pieces[0]['radius']==8
    store=Store(tmp_path);panel=store.put_raster(asymmetric())
    ui=render_ui(store,[{'raster':panel,'rect':[2,1,5,3]}],[12,7])
    _,arrays=load_sequence(store,ui);np.testing.assert_array_equal(arrays[0][1:4,2:7],asymmetric())
    # Explicit supplied glyphs establish coverage and different advances/bearings.
    A=np.zeros((3,2,4),np.uint8);A[...,3]=255;A[...,0]=200
    B=np.zeros((2,2,4),np.uint8);B[...,3]=255;B[...,1]=180
    atlas=build_glyph_atlas(store,{'A':{'array':A,'bearing':[0,-3],'advance':3},'B':{'array':B,'bearing':[1,-2],'advance':4}},columns=2)
    text=render_text(store,atlas,'AB',[10,5],baseline=[1,4]);doc,arrays=load_sequence(Store(tmp_path),text)
    np.testing.assert_array_equal(arrays[0][1:4,1:3],A);np.testing.assert_array_equal(arrays[0][2:4,5:7],B)
    assert doc['metadata']['placements'][1]['origin']==[5,2]
    with pytest.raises(ValidationError): render_text(store,atlas,'AC',[10,5],baseline=[1,4])
    open_mouth=asymmetric();closed=open_mouth.copy();closed[1,1]=[0,0,0,255]
    timeline=save_viseme_timeline(store,'A A',{'open':open_mouth,'closed':closed},{'A':'open',' ':'closed'},[Fraction(1,10),Fraction(1,4),Fraction(1,10)])
    mouth_doc,mouth=load_sequence(Store(tmp_path),timeline)
    assert mouth_doc['metadata']['symbols']==['open','closed','open']
    assert mouth_doc['frames'][0]['raster']==mouth_doc['frames'][2]['raster']
    assert mouth_doc['frames'][1]['duration']==[1,4]
    np.testing.assert_array_equal(mouth[1],closed)
    with pytest.raises(ValidationError): save_viseme_timeline(store,'a',{'open':open_mouth},{'A':'open'},[Fraction(1,10)])
    with pytest.raises(UnsupportedCapability): generate_asset('learned-visemes')


def test_explicit_local_font_file_adapter(tmp_path):
    from pathlib import Path
    path=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    if not path.is_file(): pytest.skip('Optional explicit-font integration requires the named installed fixture')
    glyphs,receipt=rasterize_font(path,'Ag ',size=16)
    assert list(glyphs)==['A','g',' '] and len(receipt['font_sha256'])==64
    assert glyphs[' ']['advance']>0 and not glyphs[' ']['array'].any()
    store=Store(tmp_path);atlas=build_glyph_atlas(store,glyphs,columns=3)
    sequence=render_text(store,atlas,'Ag ',[64,32],baseline=[2,20])
    _,arrays=load_sequence(store,sequence);assert np.count_nonzero(arrays[0][...,3])>0


def test_f03_eighteen_joint_compatibility_corrected_and_raster_depth():
    # Eighteen explicit asymmetric points, valid outer frame-list wrapper input.
    labels=['NECK','NOSE','LEFT HIP','RIGHT HIP']+[f'point{i}' for i in range(14)]
    joints=[{'label':label,'x':.2+(i%5)*.12,'y':.1+(i%7)*.11,'z':.2+(i%4)*.16} for i,label in enumerate(labels)]
    import math
    t=math.radians(25)
    refs=[{'label':j['label'],'x':j['x']*80,'y':((j['y']-.5)*math.cos(t)-(j['z']-.5)*math.sin(t)+.5)*40} for j in joints]
    compat=project_frames([joints,joints],auto_direction=True,auto_tilt=True,reference=refs,canvas=[80,40])
    assert all(s['direction_degrees']==0 and s['tilt_degrees']==-45 and s['matched_terms']==0 for s in compat['states'])
    corrected=project_frames([joints,joints],auto_direction=True,auto_tilt=True,reference=refs,canvas=[80,40],corrected=True)
    assert all(s['direction_degrees']==0 and s['tilt_degrees']==25 for s in corrected['states'])
    assert len(corrected['frames'][0])==18
    depth=[{'label':'a','z_index':-1000},{'label':'b','z_index':-1000},{'label':'c','z_index':1000}]
    g=draw_depth_channels(depth);l=draw_depth_channels(depth,'lua-raster-rank-v1')
    assert [p['z_index'] for p in g]==[0,1,1] # source duplicate ordinal collides with next group
    assert [p['alpha'] for p in g]==[254,253,253]
    assert [p['recovered_z_index'] for p in g]==[1,2,2]
    assert [p['z_index'] for p in l]==[1,1,2]
    assert [p['alpha'] for p in l]==[254,254,253]
    assert depth[0]['z_index']==-1000


def test_f07_caption_null_auto_percent_and_end_frame_boundaries():
    a=asymmetric()
    result=prepare_prompt('lua-minimax-v1','  50%% guard ',first=a,choices={'view':'Auto','direction':'east'},allowed_choices={'direction':['east','west']})
    assert result['text']=='  50% guard ' and result['choices']=={'direction':'east'} and result['target_field']=='description'
    assert prepare_prompt('lua-minimax-v1','  ',first=a)['text'] is None
    g=prepare_prompt('godot-v3-v1',' guard ',first=a,interpolate=True)
    assert g['text']=='guard' and g['end'] is None and g['remote_transformation']=='unsupported'
    with pytest.raises(ValidationError): prepare_prompt('lua-v3-v1','guard',first=a,interpolate=True)
    with pytest.raises(ValidationError): prepare_prompt('lua-minimax-v1','guard',first=a,choices={'view':'auto'})
    assert prepare_prompt('lua-v3-v1',' guard ',first=a,end=a,interpolate=True)['text']==' guard '


def test_local_validation_budget_dimensions_and_explicit_asset_failures(tmp_path):
    a=asymmetric();store=Store(tmp_path)
    with pytest.raises(ValidationError): prepare_request('local-rgba-v1',[a],{'mask':np.zeros((1,1),bool)})
    with pytest.raises(ValidationError): prepare_request('local-rgba-v1',[a],{'references':[a]*5})
    with pytest.raises(ValidationError): prepare_request('local-rgba-v1',[a],{'references':[a],'reference_roles':[]})
    with pytest.raises(ValidationError): layout_shapes([{'id':'x','type':'circle','x':0,'y':0,'r':-1}],[512,512],[128,512])
    with pytest.raises(ValidationError): topology_indices(np.zeros((1,1),np.uint8))
    with pytest.raises(ValidationError): render_ui(store,[{'raster':store.put_raster(a),'rect':[0,0,5,3]}],[3,3])
    with pytest.raises(ValidationError): save_supplied_motion(store,[a],[Fraction(0)])
    assert store.get_head('failed') is None

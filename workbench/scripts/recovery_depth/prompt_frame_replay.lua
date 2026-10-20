-- Host-only harness. Original modules arrive unchanged as source-byte globals.
-- No app runtime, JSON codec, native pixel engine, credentials, or transport.
io=nil; os=nil; package=nil; require=nil; loadfile=nil
local cases,checks={},0
local function eq(a,b) checks=checks+1; assert(a==b,tostring(a)..' ~= '..tostring(b)) end
local function case(name,fn) fn();cases[#cases+1]=name end
assert(loadstring(SOURCE_SAFE_STRING,'@original-dialog-safeString'))()
local pix=assert(loadstring(SOURCE_PIXMINIMAX,'@original-pixminimax.lua'))()

case('text_storage_and_caption_grammar',function()
 eq(pix.api_text(safeString('  30% power \n')),'  30% power \n')
 eq(pix.api_text('%%%%'),'%%');eq(pix.api_text(' \t\n'),nil)
 eq(pix.api_text(0),'0');eq(pix.api_text(false),'false')
 local slots,err=pix.caption_slots({subject_description='Auto',initial_pose='  Ready  ',view='Auto',direction='east'})
 eq(err,nil);eq(slots.subject_description,'Auto');eq(slots.initial_pose,'  Ready  ')
 eq(slots.view,nil);eq(slots.direction,'east')
 local bad,reason=pix.caption_slots({view='auto'});eq(bad,nil);eq(type(reason),'string')
 local request={view='side',direction='west',subject_description='old',other=7}
 pix.put_caption(request,{});eq(request.view,nil);eq(request.direction,nil);eq(request.subject_description,nil);eq(request.other,7)
 eq(pix.improve_fields({}),nil)
 local fields=pix.improve_fields({initial_pose='Ready',subject_description='Hero'})
 eq(fields[1],'subject_description');eq(fields[2],'initial_pose')
end)
case('enhancement_merge_and_stale_first_guard',function()
 local current={description='old',subject_description='oldsubject',initial_pose='oldpose',view='side',direction='east'}
 local reply={enhanced_prompt='  Strike 30%  ',caption={subject_description='new%',initial_pose='newpose',view='high top-down',direction='north'}}
 pix.merge_enhancement(current,reply,false,true)
 eq(pix.api_text(current.description),'  Strike 30%  ');eq(current.subject_description,'oldsubject')
 pix.merge_enhancement(current,reply,true,false);eq(current.subject_description,'oldsubject');eq(current.view,'side')
 pix.merge_enhancement(current,reply,true,true);eq(pix.api_text(current.subject_description),'new%');eq(current.initial_pose,'newpose');eq(current.direction,'east')
 current.view='Auto';current.direction='Auto';pix.merge_enhancement(current,reply,true,true)
 eq(current.view,'high top-down');eq(current.direction,'north')
 local changed=pix.merge_enhancement(current,{enhanced_prompt='next',caption={view='bogus'}},true,true)
 eq(changed.view,nil);eq(current.view,'high top-down')
end)
case('first_source_comparison_and_caption_reset',function()
 local a={width=32,height=32,isEqual=function()return true end}
 local b={width=32,height=32}
 eq(pix.same_first_frame(nil,''),true);eq(pix.same_first_frame(a,b),true)
 b.width=33;eq(pix.same_first_frame(a,b),false)
 local current={subject_description='hero',initial_pose='ready',view='side',direction='east',description='walk'}
 eq(pix.first_frame_changed(current,a,b),true);eq(current.subject_description,'');eq(current.initial_pose,'');eq(current.view,'Auto');eq(current.direction,'Auto');eq(current.description,'walk')
end)
case('cost_estimator_boundaries_and_maximum_axes',function()
 eq(pix.get_cost(64,64,16),2);eq(pix.get_cost(65,65,16),1)
 eq(pix.get_cost(128,128,16),2);eq(pix.get_cost(129,129,16),1);eq(pix.get_cost(256,256,40),6)
 local w,h=pix.generation_size({current_json={a={width=24,height=64},b={width=64,height=24}}},{'a','b'})
 eq(w,64);eq(h,64)
end)

-- Native dependencies are deliberate host stubs, not substitute algorithms.
dofile=function()return {}end
local captured
json={encode=function(value)captured=value;return '{}'end}
ColorMode={RGB='RGB'};BlendMode={SRC='SRC'}
app={activeSprite={width=64,height=64,colorMode='RGB'},alert=function()error('Unexpected alert')end}
_version='offline-version';_secret='OFFLINE-NOT-A-CREDENTIAL';_tier=0
local serializer=assert(loadstring(SOURCE_CREATE_JSON,'@original-create-json.lua'))()
-- This module exports its global table rather than returning it.
serializer=createJSON
case('numeric_seed_strings_not_coerced_by_private_serializer',function()
 local model={current_json={},default_json={}}
 for _,seed in ipairs({'123','-1','12.5',' 123 '})do
  serializer.create(model,{seed=seed},{})
  eq(captured.seed,seed);eq(type(captured.seed),'string')
 end
 serializer.create(model,{seed='invalid'},{});eq(captured.seed,0);eq(type(captured.seed),'number')
 serializer.create(model,{seed=123},{});eq(captured.seed,123);eq(type(captured.seed),'number')
end)

local function image(w,h,mode)
 local im={width=w,height=h,colorMode=mode or 'RGB',ops={}}
 function im:drawImage(source,point,alpha,blend) self.ops[#self.ops+1]={kind='draw',source=source,x=point.x,y=point.y,blend=blend} end
 function im:clear(rect) self.ops[#self.ops+1]={kind='clear',x=rect.x,y=rect.y,w=rect.width,h=rect.height} end
 return im
end
Image=image;Point=function(x,y)return{x=x,y=y}end
Rectangle=function(x,y,w,h)return{x=x,y=y,width=w,height=h}end
app.transaction=function(fn)fn()end
local place=assert(loadstring(SOURCE_PLACE_IMAGE,'@original-place-image.lua'))()
local function destination()
 local old=image(3,3);local layer={};local cel={layer=layer,frameNumber=1,image=old,position=Point(9,10)}
 local sprite={width=32,height=32};layer.sprite=sprite;function layer:cel()return cel end
 function sprite:newCel(_,frame,im,pos)local result={frameNumber=frame,image=im,position=pos,layer=layer};return result end
 return cel
end
case('placement_size_precedence_full_canvas_ignores_stale_selection',function()
 local cel=destination()
 local im,result=place.place_on_cel(string.rep('x',32*32*4),cel,{image_size={width=16,height=16},use_selection=true,selection_origin={5,6}})
 eq(im.width,32);eq(im.height,32);eq(result.image.ops[1].kind,'draw');eq(result.image.ops[1].x,0);eq(result.image.ops[1].y,0)
 eq(result.position.x,0);eq(result.position.y,0)
end)
case('placement_subregion_and_mixed_axis_overflow_predicate',function()
 local cel=destination()
 local im,result=place.place_on_cel(string.rep('x',16*16*4),cel,{image_size={width=16,height=16},use_selection=true,selection_origin={5,6}})
 eq(im.width,16);eq(result.image.ops[2].kind,'clear');eq(result.image.ops[2].w,16);eq(result.image.ops[3].x,5)
 im,result=place.place_on_cel(string.rep('x',64*16*4),cel,{use_selection=true,selection_origin={5,6}},{width=64,height=16})
 eq(im.width,64);eq(im.height,16);eq(result.image.width,32);eq(result.image.height,32)
 eq(result.image.ops[2].kind,'clear');eq(result.image.ops[2].w,64);eq(result.image.ops[3].x,5)
end)
case('response_geometry_and_crop_are_not_png_decode_or_resize',function()
 local im,x,y=place.create_image_from_bytes('PNG-like-bytes',32,32,{width=16,paste_x=-3,paste_y=5})
 eq(im.width,16);eq(im.height,32);eq(im.bytes,'PNG-like-bytes');eq(x,-3);eq(y,5)
 local cel=destination();local crop
 function cel.layer.sprite:crop(a,b,w,h)crop={a,b,w,h}end
 place.fit_sprite_to_result(cel,16,24);eq(crop[1],0);eq(crop[2],0);eq(crop[3],16);eq(crop[4],24)
end)

local background_calls=0
dofile=function()return{get_image=function(...)background_calls=background_calls+1;return 'BACKGROUND-HOST-SENTINEL'end}end
local prepare=assert(loadstring(SOURCE_PREPARE,'@original-prepare-for-generation.lua'))()
case('logical_reference_markers_and_real_destination_count',function()
 for _,flags in ipairs({{false,false,17},{true,false,16},{true,true,15}})do
  local sprite={width=32,height=32,layers={},selection={isEmpty=true}}
  local layer={name='Paint',isGroup=false};sprite.layers={layer};app.activeSprite=sprite;app.activeLayer=layer;app.activeFrame={frameNumber=1}
  local created=0
  function sprite:newEmptyFrame(n)return{frameNumber=n}end
  function sprite:newCel(l,f)created=created+1;return{frameNumber=f.frameNumber,image={drawImage=function()end},position=Point(0,0)}end
  GetSpriteFixPalette=function()return sprite end
  local cels=prepare.prepare_images_animation({current_json={output_method='New frame',use_selection=flags[1] or flags[2]},generation_start_frame=1},true,17,'offline',flags[1],flags[2])
  eq(created,flags[3]);eq(#cels,17)
  eq(cels[1]==false,flags[1]);eq(cels[17]==false,flags[2])
 end
 eq(background_calls,2)
end)

return '{"runtime":"'..jit.version..'","assertions":'..checks..',"cases":["'..table.concat(cases,'","')..'"],"passed":true}'

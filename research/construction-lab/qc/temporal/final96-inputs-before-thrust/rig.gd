extends "rig_side.gd"
## Authored four-view candidate; depth-facing projection is not side-view mirroring.
var master_design: Dictionary={}
var master_clips: Dictionary={}
var current_view="right"
var equipment_selection=""
const ACTION_EQUIPMENT={"slash":"sword","thrust":"sword","charge":"sword","shoot":"blaster","cast":"none","celebrate":"none"}
func set_equipment(selection: String)->bool:
    if selection not in ["none","sword","blaster"]:return false
    equipment_selection=selection
    if not state.is_empty():
        state.equipment=selection
        metadata.equipment=selection
        metadata.effective_equipment=selection
        metadata.equipment_selection=selection
        metadata.equipment_selection_mode="persistent"
    queue_redraw()
    return true
func clear_equipment_selection()->void:
    equipment_selection=""
    if not state.is_empty():pose(metadata.clip,metadata.input_phase,current_view)
func can_play(clip: String)->bool:
    return master_clips.get("clips",{}).has(clip) and (equipment_selection=="" or not ACTION_EQUIPMENT.has(clip) or equipment_selection==ACTION_EQUIPMENT[clip])
const SIDE_ORDER=["rear_leg","rear_boot","rear_arm","front_leg","front_boot","torso","scarf","head","front_arm","shoulder_armor","hands","equipment"]
const FRONT_ORDER=["rear_leg","rear_boot","front_leg","front_boot","rear_arm","torso","scarf","head","front_arm","shoulder_armor","hands","equipment"]
const BACK_ORDER=["rear_leg","rear_boot","front_leg","front_boot","rear_arm","front_arm","hands","equipment","torso","shoulder_armor","scarf","head"]
func configure(new_design: Dictionary,new_clips: Dictionary) -> void:
    equipment_selection=""
    master_design=new_design.duplicate(true)
    master_clips=new_clips.duplicate(true)
    design=master_design.duplicate(true);clips=master_clips.duplicate(true)
    pose("idle",0,"right")
func _ik(a: Vector2,target: Vector2,la: float,lb: float,bend: float)->Dictionary:
    if current_view in ["front","back"]:
        var is_front=false
        if state.has("front_hip") and a.is_equal_approx(state.front_hip):is_front=true
        if state.has("front_shoulder") and a.is_equal_approx(state.front_shoulder):is_front=true
        bend=(-1.0 if current_view=="front"else 1.0)*(1.0 if is_front else -1.0)
    return super._ik(a,target,la,lb,bend)
func pose(clip: String,phase: float,view: String="right")->Dictionary:
    if view not in ["right","left","front","back"]:return {"error":"Unknown authored view"}
    if not master_clips.get("clips",{}).has(clip):return {"error":"Unknown clip"}
    if not can_play(clip):return {"error":"Action requires explicit equipment selection","clip":clip,"required_equipment":ACTION_EQUIPMENT[clip],"equipment_selection":equipment_selection}
    current_view=view
    design=master_design.duplicate(true);clips=master_clips.duplicate(true)
    layer_ids=SIDE_ORDER.duplicate()
    if view in ["front","back"]:
        var author: Dictionary=design.views[view]
        design.anchors.merge(author.anchors,true);design.polygons.merge(author.polygons,true)
        var spec: Dictionary=clips.clips[clip].duplicate(true)
        var overlay: Dictionary=spec.views[view]
        spec.defaults=overlay.defaults.duplicate(true);spec.tracks=overlay.tracks.duplicate(true)
        spec.equipment_poses=overlay.get("equipment_poses",{}).duplicate(true)
        spec.erase("gait")
        if clip in ["walk","run"]:
            var gait: Dictionary=master_clips.clips[clip].gait
            var p=fposmod(phase,1.0)
            var run=clip=="run"
            var y=108.0+(4.2 if run else 0.0)+(3.0 if run else 1.2)*cos(TAU*2*p)
            spec.defaults.pelvis=[96.0+1.0*sin(TAU*p),y]
            spec.defaults.lean=.02*sin(TAU*p)
            for side in ["front","rear"]:
                var t=fposmod(p+(0.5 if side=="rear"else 0.0),1.0)
                var stance=float(gait.stance_fraction)
                var lift=0.0
                var depth_stride=12.0 if run else 8.0
                var depth_sign=1.0 if view=="front"else -1.0
                var foot_y=166.0+depth_sign*depth_stride*stance*.5
                if t<stance:
                    foot_y-=depth_sign*depth_stride*t
                else:
                    var q=(t-stance)/(1.0-stance)
                    foot_y-=depth_sign*depth_stride*stance
                    foot_y+=depth_sign*depth_stride*stance*q*q*(3-2*q)
                    lift=(14.0 if run else 10.0)*sin(PI*q)
                spec.defaults[side+"_foot"]=[float(author.stance_x[side]),foot_y-lift]
            var sign=-1.0 if view=="front"else 1.0
            spec.defaults.front_hand=[96+sign*26+2*sin(TAU*p),y+(17 if run else 18)-(7 if run else 6)*cos(TAU*p)]
            spec.defaults.rear_hand=[96-sign*26-2*sin(TAU*p),y+(17 if run else 18)+(7 if run else 6)*cos(TAU*p)]
        clips.clips[clip]=spec
        layer_ids=FRONT_ORDER.duplicate() if view=="front"else BACK_ORDER.duplicate()
    if equipment_selection!="":
        var selected_pose: Dictionary=clips.clips[clip].get("equipment_poses",{}).get(equipment_selection,{})
        clips.clips[clip].defaults.merge(selected_pose.get("defaults",{}),true)
        clips.clips[clip].tracks.merge(selected_pose.get("tracks",{}),true)
    var result: Dictionary=super.pose(clip,phase,"left"if view=="left"else"right")
    clips=master_clips
    if result.has("error"):return result
    result["declared_clip_equipment"]=state.equipment
    if equipment_selection!="":state.equipment=equipment_selection
    result.equipment=state.equipment
    result["effective_equipment"]=state.equipment
    result["equipment_selection"]=equipment_selection
    result["equipment_selection_mode"]="persistent"if equipment_selection!=""else"declared_clip_inspection_only"
    result["equipment_transition_policy"]="Explicit equip/stow; persist through movement and matching attacks; no attack-trigger equip"
    result.view=view;result["authored_view"]=view!="left"
    result["direction_scope"]="Authored front/back geometry and pose overlays"if view in ["front","back"]else"V1 authored right; left mirrored"
    if view in ["front","back"]:
        result.world_root=[0,0]
        result["contact_basis"]="planar_xy"
        result["ground_projection"]={"type":"facing_depth_plane","phase_zero_ground_boundary":170,"opaque_sole_offset_y":3,"foot_anchor_to_boundary_y":4,"scope":"Each stance boot has its own planar XY reference; no fixed horizontal169-row gate"}
        if clip in ["walk","run"]:
            var stride=12.0 if clip=="run"else 8.0
            var direction=1.0 if view=="front"else -1.0
            result.world_root=[0,direction*stride*phase]
            for side in ["front","rear"]:
                result.contact_flags[side]=fposmod(phase+(0.5 if side=="rear"else 0.0),1.0)<float(master_clips.clips[clip].gait.stance_fraction)
            result["world_motion_status"]="Continuous vertical physics root; local stance target counters root; actual planar raster contact audit pending"
        else:
            result["world_motion_status"]="Stationary planar root; action ground-support review pending"
    result["layer_ids"]=layer_ids.duplicate()
    result["surface_frames"]=_surface_frames()
    result["material_detail_scope"]="Source-attached rigid details and continuous sleeve/trouser seams; no per-frame redraw"
    metadata=result.duplicate(true)
    return result
func _region(layer: String)->Dictionary:
    match layer:
        "torso":
            var exclude=[design.polygons.belt]
            for badge in design.get("details",{}).get("chest_badge",[]):exclude.append(badge.points)
            return {"include":[design.polygons.torso_inner],"exclude":exclude}
        "head":
            var excluded=[design.polygons.helmet_brim]
            if current_view!="back":excluded.append(design.polygons.face)
            return {"include":[design.polygons.hood_inner],"exclude":excluded}
        "shoulder_armor":return {"include":[design.polygons.shoulder_inner],"exclude":[]}
        "equipment":return {"include":[design.polygons.sword_guard if state.equipment=="sword"else design.polygons.blaster_panel],"exclude":[]}
    return {"include":[],"exclude":[]}
func _surface_frames()->Dictionary:
    var frames={}
    for layer in ["torso","head","shoulder_armor","equipment"]:
        var origin: Vector2=state.body
        var angle=float(state.lean)
        if layer=="head":origin=state.head;angle=state.head_angle
        elif layer=="shoulder_armor":origin=state.front_shoulder
        elif layer=="equipment":origin=state.front_hand;angle=state.weapon_angle
        frames[layer]={"origin":_arr(_mapped(origin)),"angle":-angle if mirror else angle,"uv_scale":[-1,1]if mirror else[1,1],"mask":_region(layer),"paint_supported":true}
    return frames
func _packed(points: Array)->PackedVector2Array:
    var p=PackedVector2Array()
    for v in points:p.append(_v(v))
    return p
func _paint(layer: String,origin: Vector2,angle: float)->void:
    var entries: Array=design.get("paint_layers",{}).get(current_view,{}).get(layer,[])
    var region: Dictionary=_region(layer)
    for stroke in entries:
        if not stroke is Dictionary or not stroke.get("at") is Array or stroke.at.size()!=2:continue
        if not design.palette.has(stroke.get("color","")):continue
        var size=stroke.get("size",1)
        if typeof(size) not in [TYPE_INT,TYPE_FLOAT] or not is_finite(float(size)) or float(size)!=floor(float(size)) or size<1 or size>4:continue
        size=int(size)
        if typeof(stroke.at[0]) not in [TYPE_INT,TYPE_FLOAT] or typeof(stroke.at[1]) not in [TYPE_INT,TYPE_FLOAT]:continue
        var at=_v(stroke.at)
        if not is_finite(at.x) or not is_finite(at.y):continue
        for y in range(size):
            for x in range(size):
                var a=at+Vector2(x,y)
                var cell=PackedVector2Array([a,a+Vector2(1,0),a+Vector2(1,1),a+Vector2(0,1)])
                var cut=false
                for polygon in region.exclude:
                    if not Geometry2D.intersect_polygons(cell,_packed(polygon)).is_empty():cut=true;break
                if cut:continue # Conservative around another material's boundary.
                for polygon in region.include:
                    for intersection in Geometry2D.intersect_polygons(cell,_packed(polygon)):
                        var world=PackedVector2Array()
                        for point in intersection:world.append(origin+point.rotated(angle))
                        if world.size()>=3:draw_colored_polygon(world,_color(stroke.color))
func _detail(key: String,origin: Vector2,angle: float)->void:
    for entry in design.get("details",{}).get(key,[]):
        _poly_points(entry.points,origin,angle,entry.color)
func _arm(side: String)->void:
    super._arm(side)
    var a: Vector2=state[side+"_shoulder"];var b: Vector2=state[side+"_elbow"];var c: Vector2=state[side+"_hand"]
    var seam: Dictionary=design.details.sleeve_seam
    _ribbon(a+_v(seam.offset),b+_v(seam.offset),c,seam.widths,seam.color)
func _leg(side: String)->void:
    super._leg(side)
    var a: Vector2=state[side+"_hip"];var b: Vector2=state[side+"_knee"];var c: Vector2=state[side+"_foot"]
    var seam: Dictionary=design.details.trouser_seam
    _ribbon(a+_v(seam.offset),b+_v(seam.offset),c,seam.widths,seam.color)
func _boot(side: String)->void:
    super._boot(side)
    _detail("boot_scuff",state[side+"_foot"],0)
func _equipment()->void:
    if state.equipment!="blaster":
        super._equipment();return
    _shape("blaster_body",state.front_hand,state.weapon_angle,"ink")
    _shape("blaster_panel",state.front_hand,state.weapon_angle,"copper")
    _shape("blaster_barrel",state.front_hand,state.weapon_angle,"copper_light")
    _shape("blaster_muzzle",state.front_hand,state.weapon_angle,"ink")
    _shape("blaster_sight",state.front_hand,state.weapon_angle,"copper_dark")
    _shape("blaster_grip",state.front_hand,state.weapon_angle,"copper_dark")
    _detail("blaster_vents",state.front_hand,state.weapon_angle)
func _head()->void:
    if current_view in ["right","left"]:
        super._head()
        _poly_points([[14,0],[17,3],[14,6],[12,6]],state.head,state.head_angle,"skin_shadow")
        _poly_points([[-16,-3],[-13,-4],[-12,7],[-15,5]],state.head,state.head_angle,"teal_dark")
        _poly_points([[-7,-19],[-5,-19],[-11,-7],[-12,-7]],state.head,state.head_angle,"cream_shadow")
    else:
        _shape("hood_outer",state.head,state.head_angle,"ink")
        _shape("hood_inner",state.head,state.head_angle,"teal")
        _shape("hood_highlight",state.head,state.head_angle,"teal_light")
        if current_view=="front":
            _shape("face",state.head,state.head_angle,"skin")
            _poly_points([[-10,3],[-7,7],[-5,13],[-9,10]],state.head,state.head_angle,"skin_shadow")
            _poly_points([[8,2],[10,3],[9,11],[5,14],[5,11]],state.head,state.head_angle,"skin_shadow")
            for x in [-7,4]:
                _poly_points([[x,-5],[x+4,-5],[x+4,-2],[x,-2]],state.head,state.head_angle,"ink")
                _poly_points([[x+1,-4],[x+3,-4],[x+3,-2],[x+1,-2]],state.head,state.head_angle,"eye")
            _poly_points([[-1,0],[2,0],[3,4],[-1,4]],state.head,state.head_angle,"skin_shadow")
            _poly_points([[-3,9],[3,9],[3,10],[-3,10]],state.head,state.head_angle,"skin_shadow")
        else:
            _poly_points([[-1,-20],[1,-20],[1,14],[-1,14]],state.head,state.head_angle,"teal_dark")
            _poly_points([[4,-18],[6,-17],[9,3],[7,12],[5,10]],state.head,state.head_angle,"teal_light")
            _poly_points([[-5,12],[5,12],[4,15],[-4,15]],state.head,state.head_angle,"copper_dark")
        _shape("helmet_brim",state.head,state.head_angle,"copper")
        _poly_points([[-9,-16],[7,-16],[8,-15],[-9,-15]],state.head,state.head_angle,"copper_light")
    _paint("head",state.head,state.head_angle)
func _draw()->void:
    if state.is_empty():return
    draw_set_transform(Vector2(float(design.canvas[0]),0)if mirror else Vector2.ZERO,0,Vector2(-1,1)if mirror else Vector2.ONE)
    for layer in layer_ids:
        if not _enabled(layer):continue
        match layer:
            "rear_leg":_leg("rear")
            "front_leg":_leg("front")
            "rear_boot":_boot("rear")
            "front_boot":_boot("front")
            "rear_arm":_arm("rear");_hands(["rear"])
            "front_arm":_arm("front")
            "torso":
                _shape("torso_outer",state.body,state.lean,"ink");_shape("torso_inner",state.body,state.lean,"teal")
                _shape("tunic_light",state.body,state.lean,"teal_light");_shape("belt",state.body,state.lean,"copper_dark")
                _poly_points([[1,-1],[6,-1],[6,3],[1,3]],state.body,state.lean,"copper_light")
                _detail("torso_stitch",state.body,state.lean)
                _detail("chest_badge",state.body,state.lean)
                _paint("torso",state.body,state.lean)
            "scarf":
                if state.has("scarf_tail_angle"):
                    var pivot=_v(design.anchors.scarf_tail_pivot);var tail=[]
                    for p in design.polygons.scarf_tail:tail.append(_arr(_v(p)-pivot))
                    _poly_points(tail,state.body+pivot.rotated(state.lean),state.scarf_tail_angle,"cream_shadow")
                else:_shape("scarf_tail",state.body,state.lean,"cream_shadow")
                _shape("scarf_neck",state.body,state.lean,"cream")
            "head":_head()
            "shoulder_armor":
                _shape("shoulder_outer",state.front_shoulder,state.lean,"copper_dark")
                _shape("shoulder_inner",state.front_shoulder,state.lean,"copper_light")
                _detail("armor_ridges",state.front_shoulder,state.lean)
                _paint("shoulder_armor",state.front_shoulder,state.lean)
            "hands":_hands()
            "equipment":
                _equipment()
                if state.equipment!="none":_paint("equipment",state.front_hand,state.weapon_angle)
    draw_set_transform(Vector2.ZERO)

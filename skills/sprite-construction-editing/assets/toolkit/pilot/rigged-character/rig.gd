extends Node2D
## Copper Scout: authored continuous polygon-strip rig. No mesh skinning claim.
var design: Dictionary = {}
var clips: Dictionary = {}
var visible_layers: Array = [] # Empty means all; renderer may isolate named actual layers.
var layer_ids: Array = ["rear_leg","rear_boot","rear_arm","front_leg","front_boot","torso","scarf","head","front_arm","shoulder_armor","hands","equipment"]
var state: Dictionary = {}
var mirror := false
var metadata: Dictionary = {}

func configure(new_design: Dictionary, new_clips: Dictionary) -> void:
    design=new_design.duplicate(true)
    clips=new_clips.duplicate(true)
    pose("idle",0.0)

func _v(value) -> Vector2:
    return Vector2(float(value[0]),float(value[1]))
func _arr(value: Vector2) -> Array:
    return [value.x,value.y]
func _mapped(value: Vector2) -> Vector2:
    return Vector2(float(design.canvas[0])-value.x,value.y) if mirror else value
func _color(name: String) -> Color:
    return Color("#"+str(design.palette[name]))
func _enabled(name: String) -> bool:
    return visible_layers.is_empty() or name in visible_layers
func _sample(track: Array, phase: float, fallback, interpolation: String):
    if track.is_empty():return fallback
    if phase<=float(track[0][0]):return track[0][1]
    for i in range(track.size()-1):
        var a: Array=track[i]
        var b: Array=track[i+1]
        if phase<=float(b[0]):
            var t: float=(phase-float(a[0]))/(float(b[0])-float(a[0]))
            if interpolation=="smoothstep":t=t*t*(3.0-2.0*t)
            if a[1] is Array:return _arr(_v(a[1]).lerp(_v(b[1]),t))
            return lerpf(float(a[1]),float(b[1]),t)
    return track[-1][1]
func _ik(a: Vector2, target: Vector2, length_a: float, length_b: float, bend: float) -> Dictionary:
    var delta: Vector2=target-a
    var distance: float=clampf(delta.length(),absf(length_a-length_b)+0.01,length_a+length_b-0.01)
    var direction: Vector2=delta.normalized() if delta.length()>0.001 else Vector2.DOWN
    var advance: float=(length_a*length_a-length_b*length_b+distance*distance)/(2.0*distance)
    var height: float=sqrt(maxf(0.0,length_a*length_a-advance*advance))
    return {"joint":a+direction*advance+Vector2(direction.y,-direction.x)*height*bend,"endpoint":a+direction*distance,"target_error":absf(delta.length()-distance)}

func pose(clip: String, phase: float, view: String="right") -> Dictionary:
    if design.is_empty() or not clips.has("clips") or not clips.clips.has(clip):return {"error":"Unknown clip/unconfigured rig"}
    if view not in ["right","left"]:return {"error":"Unsupported view; right authored, left mirrored"}
    mirror=view=="left"
    var spec: Dictionary=clips.clips[clip]
    var local_phase: float=fposmod(phase,1.0) if spec.loop else clampf(phase,0.0,1.0)
    state={}
    for key in spec.defaults:
        state[key]=_sample(spec.tracks.get(key,[]),local_phase,spec.defaults[key],spec.get("interpolation","smoothstep"))
    var root_x := 0.0
    if spec.has("gait"):
        var gait: Dictionary=spec.gait
        var stride: float=float(gait.root_motion_px_per_cycle)
        root_x=stride*phase
        state.pelvis=[96.0,float(design.anchors.pelvis[1])+float(gait.get("pelvis_drop_px",0.0))+float(gait.bob_px)*cos(TAU*2.0*local_phase)]
        for side in ["front","rear"]:
            var p: float=fposmod(local_phase+(0.5 if side=="rear"else 0.0),1.0)
            var stance: float=float(gait.stance_fraction)
            var base_x: float=105.0 if side=="front"else 87.0
            var x: float=base_x+stride*stance*0.5
            var y: float=float(design.foot_anchor_y)
            if p<stance:x-=stride*p
            else:
                var q: float=(p-stance)/(1.0-stance)
                x-=stride*stance
                x+=stride*stance*q*q*(3.0-2.0*q)
                y-=float(gait.lift_px)*sin(PI*q)
            state[side+"_foot"]=[x,y]
        state.lean+=float(gait.get("body_sway_radians",0.0))*sin(TAU*local_phase)
        state.front_hand=[107.0-float(gait.arm_swing_px)*cos(TAU*local_phase),state.pelvis[1]+float(gait.hand_drop_px)]
        state.rear_hand=[85.0+float(gait.arm_swing_px)*cos(TAU*local_phase),state.pelvis[1]+float(gait.hand_drop_px)-1.0]
    state.pelvis=_v(state.pelvis)
    var lean: float=float(state.lean)
    state.body=state.pelvis+_v(design.anchors.body_offset).rotated(lean)
    state.head=state.pelvis+_v(design.anchors.head_offset).rotated(lean)
    state.head_angle=lean+float(state.head_tilt)
    var errors: Dictionary={}
    for side in ["front","rear"]:
        state[side+"_hip"]=state.pelvis+_v(design.anchors[side+"_hip"]).rotated(lean)
        state[side+"_shoulder"]=state.pelvis+_v(design.anchors[side+"_shoulder"]).rotated(lean)
        state[side+"_foot"]=_v(state[side+"_foot"])
        var leg: Dictionary=_ik(state[side+"_hip"],state[side+"_foot"],float(design.dimensions.upper_leg),float(design.dimensions.lower_leg),1.0)
        state[side+"_knee"]=leg.joint
        # Foot targets are never silently replaced: error exposes unreachable authored data.
        errors[side+"_leg"]=leg.target_error
        var arm: Dictionary=_ik(state[side+"_shoulder"],_v(state[side+"_hand"]),float(design.dimensions.upper_arm),float(design.dimensions.lower_arm),-1.0 if side=="front"else 1.0)
        state[side+"_elbow"]=arm.joint
        state[side+"_hand"]=arm.endpoint
        errors[side+"_arm"]=arm.target_error
    state.equipment=spec.get("equipment","none")
    state.hand_state=spec.get("hand_state","closed")
    state.phase=local_phase
    var anchors: Dictionary={}
    for key in ["pelvis","head","front_hip","rear_hip","front_knee","rear_knee","front_shoulder","rear_shoulder","front_elbow","rear_elbow","front_hand","rear_hand","front_foot","rear_foot"]:
        anchors[key]=_arr(_mapped(state[key]))
    var contact: Dictionary={}
    for side in ["front","rear"]:
        contact[side]=absf(state[side+"_foot"].y-float(design.foot_anchor_y))<0.001
        if spec.has("gait"):
            contact[side]=fposmod(local_phase+(0.5 if side=="rear"else 0.0),1.0)<float(spec.gait.stance_fraction)
    var grip: Vector2=state.front_hand
    var angle: float=float(state.weapon_angle)
    var blade: Vector2=grip+Vector2(39,0).rotated(angle)
    var muzzle: Vector2=grip+Vector2(21,-3.5).rotated(angle)
    metadata={"clip":clip,"phase":local_phase,"input_phase":phase,"view":view,"mirrored":mirror,"loop":spec.loop,"endpoint":not spec.loop and local_phase==1.0,"landmarks":anchors,"feet":{"front":anchors.front_foot,"rear":anchors.rear_foot},"hands":{"front":anchors.front_hand,"rear":anchors.rear_hand},"hips":{"front":anchors.front_hip,"rear":anchors.rear_hip},"world_root":[-root_x if mirror else root_x,0],"contact_flags":contact,"contact_scope":"Geometric authored target flags; verify actual opaque sole pixels separately.","ik_target_error_px":errors,"layer_ids":layer_ids,"equipment":state.equipment,"grip":anchors.front_hand,"fx_anchors":{"blade_tip":_arr(_mapped(blade)),"muzzle":_arr(_mapped(muzzle)),"cast":_arr(_mapped(grip+Vector2(8,0))),"charge":_arr(_mapped(grip))},"quality_approved":false}
    queue_redraw()
    return metadata.duplicate(true)

func _poly_points(points: Array, origin: Vector2, angle: float, color: String) -> void:
    var vertices := PackedVector2Array()
    for point in points:vertices.append(origin+_v(point).rotated(angle))
    draw_colored_polygon(vertices,_color(color))
func _shape(name: String, origin: Vector2, angle: float, color: String) -> void:
    _poly_points(design.polygons[name],origin,angle,color)
func _ribbon(a: Vector2,b: Vector2,c: Vector2,widths: Array,color: String) -> void:
    # One continuous contour across the bend, with a quadratic rounded corner.
    var radius: float=minf(float(design.dimensions.joint_curve_radius),minf(a.distance_to(b),b.distance_to(c))*0.24)
    var entry: Vector2=b+(a-b).normalized()*radius
    var exit: Vector2=b+(c-b).normalized()*radius
    var path: Array[Vector2]=[a,entry]
    var radii: Array[float]=[float(widths[0]),float(widths[1])]
    for i in range(1,7):
        var t: float=float(i)/6.0
        path.append(entry*(1-t)*(1-t)+2*b*t*(1-t)+exit*t*t)
        radii.append(float(widths[1]))
    path.append(c)
    radii.append(float(widths[2]))
    var left := PackedVector2Array()
    var right := PackedVector2Array()
    for i in range(path.size()):
        var tangent: Vector2=(path[mini(i+1,path.size()-1)]-path[maxi(0,i-1)]).normalized()
        var normal := Vector2(tangent.y,-tangent.x)*radii[i]
        left.append(path[i]+normal)
        right.append(path[i]-normal)
    for i in range(right.size()-1,-1,-1):left.append(right[i])
    draw_colored_polygon(left,_color(color))
func _leg(side: String) -> void:
    var a: Vector2=state[side+"_hip"]
    var b: Vector2=state[side+"_knee"]
    var c: Vector2=state[side+"_foot"]
    var widths: Array=design.dimensions.leg_widths
    _ribbon(a,b,c,widths,"ink")
    _ribbon(a,b,c,[widths[0]-1.4,widths[1]-1.3,widths[2]-1.0],"cloth" if side=="front"else "teal_dark")
    _ribbon(a+Vector2(1,0),b+Vector2(1,0),c,[2.0,1.7,1.0],"cloth_light")
func _arm(side: String) -> void:
    var a: Vector2=state[side+"_shoulder"]
    var b: Vector2=state[side+"_elbow"]
    var c: Vector2=state[side+"_hand"]
    var widths: Array=design.dimensions.arm_widths
    _ribbon(a,b,c,widths,"ink")
    _ribbon(a,b,c,[widths[0]-1.2,widths[1]-1.2,widths[2]-0.8],"teal" if side=="front"else "teal_dark")
    _ribbon(a+Vector2(1,-1),b+Vector2(1,-1),c,[1.5,1.3,0.8],"teal_light")
func _boot(side: String) -> void:
    var foot: Vector2=state[side+"_foot"]
    _shape("boot_outer",foot,0,"ink")
    _shape("boot_inner",foot,0,"copper" if side=="front"else "copper_dark")
    _shape("boot_plate",foot,0,"copper_light")
func _head() -> void:
    var head: Vector2=state.head
    var angle: float=state.head_angle
    _shape("hood_outer",head,angle,"ink")
    _shape("hood_inner",head,angle,"teal")
    _shape("hood_highlight",head,angle,"teal_light")
    _shape("face",head,angle,"skin")
    _shape("helmet_brim",head,angle,"copper")
    _poly_points([[10,-6],[17,-6],[17,-3],[10,-3]],head,angle,"ink")
    _poly_points([[14,-6],[16,-6],[16,-3],[14,-3]],head,angle,"eye")
    _poly_points([[11,9],[15,8],[15,10],[12,11]],head,angle,"skin_shadow")
func _equipment() -> void:
    var hand: Vector2=state.front_hand
    var angle: float=float(state.weapon_angle)
    if state.equipment=="sword":
        _shape("sword_grip",hand,angle,"ink")
        _shape("sword_blade",hand,angle,"cream_shadow")
        _shape("sword_highlight",hand,angle,"cream")
        _shape("sword_guard",hand,angle,"copper")
    elif state.equipment=="blaster":
        _shape("blaster_body",hand,angle,"ink")
        _shape("blaster_panel",hand,angle,"copper")
        _shape("blaster_grip",hand,angle,"copper_dark")
func _hands(sides: Array=["front"]) -> void:
    for side in sides:
        var hand: Vector2=state[side+"_hand"]
        var angle: float=(hand-state[side+"_elbow"]).angle()
        if state.has(side+"_hand_angle"):angle=float(state[side+"_hand_angle"])
        if side=="front"and state.equipment!="none":angle=float(state.weapon_angle)
        _shape("hand_open"if state.hand_state=="open"else "hand_closed",hand,angle,"ink")
        _poly_points([[-2,-2],[3,-3],[5,-1],[4,2],[-2,2]],hand,angle,"cream")
func _draw() -> void:
    if state.is_empty():return
    draw_set_transform(Vector2(float(design.canvas[0]),0)if mirror else Vector2.ZERO,0,Vector2(-1,1)if mirror else Vector2.ONE)
    for layer in layer_ids:
        if not _enabled(layer):continue
        match layer:
            "rear_leg":_leg("rear")
            "rear_boot":_boot("rear")
            "rear_arm":
                _arm("rear")
                _hands(["rear"])
            "front_leg":_leg("front")
            "front_boot":_boot("front")
            "torso":
                _shape("torso_outer",state.body,float(state.lean),"ink")
                _shape("torso_inner",state.body,float(state.lean),"teal")
                _shape("tunic_light",state.body,float(state.lean),"teal_light")
                _shape("belt",state.body,float(state.lean),"copper_dark")
                _poly_points([[1,-1],[6,-1],[6,3],[1,3]],state.body,float(state.lean),"copper_light")
            "scarf":
                if state.has("scarf_tail_angle"):
                    var pivot: Vector2=_v(design.anchors.scarf_tail_pivot)
                    var tail: Array=[]
                    for point in design.polygons.scarf_tail:tail.append(_arr(_v(point)-pivot))
                    _poly_points(tail,state.body+pivot.rotated(float(state.lean)),float(state.scarf_tail_angle),"cream_shadow")
                else:_shape("scarf_tail",state.body,float(state.lean),"cream_shadow")
                _shape("scarf_neck",state.body,float(state.lean),"cream")
            "head":_head()
            "front_arm":_arm("front")
            "shoulder_armor":
                _shape("shoulder_outer",state.front_shoulder,float(state.lean),"copper_dark")
                _shape("shoulder_inner",state.front_shoulder,float(state.lean),"copper_light")
            "hands":_hands()
            "equipment":_equipment()
    draw_set_transform(Vector2.ZERO)

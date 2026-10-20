extends Node2D
## Deterministic authored cutout pilot; source parts and anchors live in rig.json.
var sprites := {}
var specification := {}
var last_foot_targets := {}
var last_ik_errors := {}

func _ready() -> void:
    specification = JSON.parse_string(FileAccess.get_file_as_string("res://assets/rig.json"))
    for name in ["rear_thigh", "rear_shin", "rear_foot", "rear_arm", "torso", "head", "front_thigh", "front_shin", "front_foot", "front_arm", "front_forearm"]:
        var entry: Dictionary = specification.parts[name]
        var sprite := Sprite2D.new()
        sprite.texture = load("res://assets/" + entry.texture)
        sprite.centered = false
        sprite.offset = -Vector2(entry.anchor[0],entry.anchor[1])
        sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        if name.ends_with("_shin"):
            sprite.scale.y=1.25
        add_child(sprite)
        sprites[name] = sprite
    pose("walk", 0.0)

func _part(name: String, anchor: Vector2, angle: float) -> void:
    sprites[name].position = anchor
    sprites[name].rotation = angle

func _leg(side: String, hip: Vector2, foot: Vector2) -> void:
    var length_a := 24.0
    var length_b := 20.0
    var vector := foot-hip
    var distance := clampf(vector.length(),absf(length_a-length_b)+0.001,length_a+length_b-0.001)
    var direction := vector.normalized()
    var advance := (length_a*length_a-length_b*length_b+distance*distance)/(2.0*distance)
    var height := sqrt(maxf(0.0,length_a*length_a-advance*advance))
    var knee := hip+direction*advance+Vector2(direction.y,-direction.x)*height
    var angle_a := (knee-hip).angle()-Vector2(-12,22).angle()
    var angle_b := (foot-knee).angle()-Vector2(0,20).angle()
    _part(side+"_thigh",hip,angle_a)
    _part(side+"_shin",knee,angle_b)
    _part(side+"_foot",foot,0.0)
    last_foot_targets[side] = [foot.x,foot.y]
    var endpoint := knee+Vector2.RIGHT.rotated((foot-knee).angle())*length_b
    last_ik_errors[side] = endpoint.distance_to(foot)

func pose(action: String, phase: float) -> void:
    phase = fposmod(phase,1.0)
    var bob := -0.9*cos(TAU*2.0*phase) if action=="walk" else 0.0
    var hip := Vector2(64,91+bob)
    var torso_angle := 0.0
    var front_arm_angle := 0.8
    var forearm_angle := 0.0
    var rear_arm_angle := -0.25
    if action == "walk":
        for pair in [["rear",0.5],["front",0.0]]:
            var p: float = fposmod(phase+pair[1],1.0)
            var foot := Vector2(64,131)
            if p<0.5:
                foot.x += 12.0-48.0*p
            else:
                var q := (p-0.5)*2.0
                foot.x += -12.0+24.0*(q*q*(3.0-2.0*q))
                foot.y -= 8.0*sin(PI*q)
            _leg(pair[0],hip+Vector2(-2 if pair[0]=="rear" else 2,0),foot)
        front_arm_angle = 0.65+0.22*sin(TAU*phase)
        forearm_angle = 0.1*sin(TAU*phase)
        rear_arm_angle = -0.3-0.2*sin(TAU*phase)
    else:
        _leg("rear",hip+Vector2(-2,0),Vector2(52,131))
        _leg("front",hip+Vector2(2,0),Vector2(78,131))
        # Authored windup, punch, recovery; no native event claim.
        var knots := [[0.0,0.8],[0.25,2.1],[0.42,0.0],[0.58,0.0],[0.9,0.8],[1.0,0.8]]
        for i in range(knots.size()-1):
            if phase>=knots[i][0] and phase<knots[i+1][0]:
                front_arm_angle = lerpf(knots[i][1],knots[i+1][1],(phase-knots[i][0])/(knots[i+1][0]-knots[i][0]))
                break
        var forearm_knots := [[0.0,0.0],[0.25,-2.4],[0.42,0.0],[0.58,0.0],[0.9,0.0],[1.0,0.0]]
        for i in range(forearm_knots.size()-1):
            if phase>=forearm_knots[i][0] and phase<forearm_knots[i+1][0]:
                forearm_angle=lerpf(forearm_knots[i][1],forearm_knots[i+1][1],(phase-forearm_knots[i][0])/(forearm_knots[i+1][0]-forearm_knots[i][0]))
                break
        torso_angle = -0.045*sin(PI*phase)
    _part("torso",hip,torso_angle)
    _part("head",Vector2(67,67+bob),-0.01*sin(TAU*phase))
    _part("rear_arm",Vector2(61,70+bob),rear_arm_angle)
    var shoulder := Vector2(73,71+bob)
    _part("front_arm",shoulder,front_arm_angle)
    _part("front_forearm",shoulder+Vector2(19,0).rotated(front_arm_angle),forearm_angle)

func snapshot() -> Dictionary:
    var transforms := {}
    for name in sprites:
        var part: Sprite2D = sprites[name]
        transforms[name]={"position":[part.position.x,part.position.y],"rotation":part.rotation,"scale":[part.scale.x,part.scale.y],"offset":[part.offset.x,part.offset.y]}
    return {"feet":last_foot_targets,"ik_errors":last_ik_errors,"parts":transforms}

extends Node2D
## Independent original effects, driven by the actor's explicit authored tick clock.
## These are visual effects; they implement no collision or damage rules.
var clock: float = 0.0
var items: Array = []
var received: Dictionary = {}
var history: Array = []

func reset() -> void:
    clock=0.0;items.clear();received.clear();history.clear();queue_redraw()

func receive(token: String, kind: String, born_tick: float, pose: Dictionary) -> bool:
    if token.is_empty() or received.has(token) or not is_finite(born_tick) or born_tick<0:return false
    var anchor_key=""
    match kind:
        "projectile_emit":anchor_key="muzzle"
        "cast_emit":anchor_key="cast"
        "charge_begin","charge_ready":anchor_key="charge"
        _:return false
    var anchor=pose.get("fx_anchors",{}).get(anchor_key)
    if not anchor is Array or anchor.size()!=2:return false
    for value in anchor:
        if not (value is int or value is float) or not is_finite(float(value)):return false
    var point=Vector2(float(anchor[0]),float(anchor[1]))
    var direction=-1.0 if pose.get("mirrored",false) else 1.0
    received[token]=true
    history.append({"token":token,"kind":kind,"born_tick":born_tick,"anchor":[point.x,point.y],"direction":direction})
    match kind:
        "projectile_emit":
            items.append({"type":"flash","point":point,"birth":born_tick,"ttl":6.0,"direction":direction})
            items.append({"type":"bolt","point":point,"birth":born_tick,"ttl":30.0,"direction":direction})
        "cast_emit":items.append({"type":"cast","point":point,"birth":born_tick,"ttl":24.0,"direction":direction})
        "charge_begin":items.append({"type":"charge","point":point,"birth":born_tick,"ttl":60.0,"direction":direction})
        "charge_ready":items.append({"type":"ready","point":point,"birth":born_tick,"ttl":12.0,"direction":direction})
    queue_redraw()
    return true

func set_clock(tick: float) -> bool:
    if not is_finite(tick) or tick<clock:return false
    clock=tick
    var alive: Array=[]
    for item in items:
        if clock-float(item.birth)<float(item.ttl):alive.append(item)
    items=alive;queue_redraw();return true

func snapshot() -> Dictionary:
    return {"clock":clock,"live_count":items.size(),"received_count":received.size(),"history":history.duplicate(true),"items":items.duplicate(true),"scope":"Authored visual VFX only; reset before backward seeking/replay or clip/view changes."}

func _draw() -> void:
    var light=Color("#F0E4C6")
    var teal=Color("#4AB5AE")
    var copper=Color("#EDAA70")
    for item in items:
        var age=clock-float(item.birth)
        if age<0:continue
        var point: Vector2=item.point
        var direction: float=item.direction
        var kind: String=item.type
        if kind=="flash":
            var extent=10.0*(1.0-age/6.0)
            draw_colored_polygon(PackedVector2Array([point+Vector2(-3,-3),point+Vector2(direction*extent,-6),point+Vector2(direction*extent*0.7,0),point+Vector2(direction*extent,6),point+Vector2(-3,3)]),copper)
        elif kind=="bolt":
            var tip=point+Vector2(direction*age*2.0,0)
            draw_line(tip-Vector2(direction*10.0,0),tip,teal,4.0,false)
            draw_rect(Rect2(tip-Vector2(2,2),Vector2(4,4)),light)
        elif kind=="cast":
            var center=point+Vector2(direction*age*0.9,-sin(age/24.0*PI)*6.0)
            var radius=3.0+age*0.42
            var tint=teal;tint.a=1.0-age/24.0
            draw_arc(center,radius,0,TAU,24,tint,2.0,false)
            for i in range(5):
                var star=center+Vector2(cos(i*TAU/5.0+age*0.15),sin(i*TAU/5.0+age*0.15))*radius
                draw_rect(Rect2(star-Vector2.ONE,Vector2(2,2)),light)
        else:
            var radius=5.0+2.0*sin(age*0.25)
            if kind=="ready":radius+=age*0.7
            draw_arc(point,radius,0,TAU,20,copper if kind=="ready"else teal,2.0,false)
            draw_circle(point,2.0,light)

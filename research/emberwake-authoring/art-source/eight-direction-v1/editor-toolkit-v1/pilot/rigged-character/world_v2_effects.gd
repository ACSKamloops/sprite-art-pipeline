extends "effects.gd"
## Four-direction original visual effects. Physics remains in world_v2.gd.
func receive(token: String,kind: String,born_tick: float,pose: Dictionary)->bool:
 var count=items.size();var accepted=super.receive(token,kind,born_tick,pose)
 if accepted:
  var vector=pose.get("direction_vector",[1,0])
  for i in range(count,items.size()):items[i].heading=Vector2(vector[0],vector[1])
 return accepted
func _draw()->void:
 var saved=items;items=items.filter(func(item):return item.type not in ["bolt","flash","cast"])
 super._draw();items=saved
 for item in items:
  var age=clock-float(item.birth)
  if age<0 or item.type not in ["bolt","flash","cast"]:continue
  var direction:Vector2=item.get("heading",Vector2(item.direction,0));var normal=Vector2(-direction.y,direction.x);var point:Vector2=item.point
  if item.type=="bolt":
   var tip=point+direction*age*2.0
   draw_line(tip-direction*10.0,tip,Color("#4AB5AE"),4.0,false);draw_rect(Rect2(tip-Vector2(2,2),Vector2(4,4)),Color("#F0E4C6"))
  elif item.type=="cast":
   var center=point+direction*age*0.9+Vector2(0,-sin(age/24.0*PI)*6.0)
   var radius=3.0+age*0.42;var tint=Color("#4AB5AE");tint.a=1.0-age/24.0
   draw_arc(center,radius,0,TAU,24,tint,2.0,false)
   for i in range(5):
    var star=center+Vector2(cos(i*TAU/5.0+age*0.15),sin(i*TAU/5.0+age*0.15))*radius
    draw_rect(Rect2(star-Vector2.ONE,Vector2(2,2)),Color("#F0E4C6"))
  else:
   var extent=10.0*(1.0-age/6.0)
   draw_colored_polygon(PackedVector2Array([point-direction*3-normal*3,point+direction*extent-normal*6,point+direction*extent*0.7,point+direction*extent+normal*6,point-direction*3+normal*3]),Color("#EDAA70"))

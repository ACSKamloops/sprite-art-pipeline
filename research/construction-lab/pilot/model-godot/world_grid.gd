extends Node2D
# Reference XY world plane only: no reconstructed ground, foot controls or contact markers.
func _draw()->void:
 for i in range(-32,33):
  var x=i*32.0;var y=i*32.0
  draw_line(Vector2(x,-1024),Vector2(x,1024),Color8(104,119,135,65),1,false)
  draw_line(Vector2(-1024,y),Vector2(1024,y),Color8(104,119,135,65),1,false)
 for point in [Vector2(240,170),Vector2(336,170),Vector2(240,74),Vector2(144,170),Vector2(240,266)]:
  draw_line(point-Vector2(5,0),point+Vector2(5,0),Color8(161,177,195,150),1,false)
  draw_line(point-Vector2(0,5),point+Vector2(0,5),Color8(161,177,195,150),1,false)

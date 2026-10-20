extends SceneTree
const Actor = preload("res://actor.gd")
var failures: Array = []
var checks := 0
func check(ok: bool, label: String):
	checks += 1
	if not ok: failures.append(label)
func _initialize(): run.call_deferred()
func run():
	var clips = {
		"ready_still":{"ticks":[100],"hz":24,"loop":true,"events":[],"direction":"east","pivot":[96,170]},
		"a":{"ticks":[1],"hz":24,"loop":false,"events":[],"direction":"east","pivot":[96,170]},
		"b":{"ticks":[100],"hz":60,"loop":true,"events":[],"direction":"east","pivot":[96,170]},
		"c":{"ticks":[100],"hz":24,"loop":true,"events":[],"direction":"east","pivot":[96,170]}}
	var sf=SpriteFrames.new()
	var im=Image.create(1,1,false,Image.FORMAT_RGBA8); im.fill(Color.WHITE)
	var texture=ImageTexture.create_from_image(im)
	for key in clips: sf.add_animation(key); sf.add_frame(key,texture)
	var a=Actor.new();root.add_child(a);a.setup({"clips":clips},sf);a.set_physics_process(false)
	a.request("a",true);a.request("b");a.fractional_ticks=.25;a.advance_ticks(1)
	check(a.clock.id=="b" and a.clock.tick==0,"Buffered unequal-rate transition")
	check(is_equal_approx(a.fractional_ticks,.625),"Keep sub-tick time through24-to60Hz boundary")
	a.request("a",true);a.request("b");a.fractional_ticks=.25;a.advance_ticks(2)
	check(a.clock.tick==3 and is_equal_approx(a.fractional_ticks,.125),"Whole and fractional leftover use same conversion")
	clips.a.next="b";clips.b.loop=false;clips.b.ticks=[1];clips.b.next="c"
	a.request("a",true);a.fractional_ticks=.25;a.advance_ticks(2)
	check(a.clock.id=="c" and a.clock.tick==0 and is_equal_approx(a.fractional_ticks,.85),"Carry across chained mixed-rate transitions")
	clips.a.erase("next");a.freeze_completed=false
	a.request("a",true);a.fractional_ticks=.25;a.advance_ticks(2)
	check(a.clock.id=="ready_still" and a.clock.tick==1 and is_equal_approx(a.fractional_ticks,.25),"Default completion return preserves elapsed time")
	a.fractional_ticks=.9;a.request("a",true)
	check(a.fractional_ticks==0,"Explicit new input resets action clock")
	var suffix="before" if "--before" in OS.get_cmdline_user_args() else "after"
	var f=FileAccess.open("res://evidence/fractional-"+suffix+".json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"checks":checks,"failures":failures,"fixture":"Synthetic1px textures, timing proof only; no art coverage"},"  "));f.close()
	print("FRACTIONAL TESTS ",checks,"; failures ",failures)
	a.queue_free();quit(0 if failures.is_empty() else 1)

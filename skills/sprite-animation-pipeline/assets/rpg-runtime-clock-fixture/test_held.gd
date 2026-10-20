extends SceneTree
const Actor=preload("res://actor.gd")
var checks:=0
var failures:Array=[]
func check(ok:bool,label:String):
	checks+=1
	if not ok: failures.append(label)
func _initialize(): run.call_deferred()
func run():
	var clips={"ready_still":{"ticks":[1],"hz":24,"loop":true,"events":[],"direction":"east","pivot":[96,170]}}
	for profile in Actor.HELD_PROFILES.values():
		for i in 3:
			clips[profile[i]]={"ticks":[3 if i==0 else 2],"hz":24,"loop":i==1,"events":[],"direction":"east","pivot":[96,170]}
		clips[profile[2]].next="ready_still"
	clips.hurt={"ticks":[1],"hz":24,"loop":false,"events":[],"direction":"east","pivot":[96,170]}
	var sf=SpriteFrames.new();var im=Image.create(1,1,false,Image.FORMAT_RGBA8);im.fill(Color.WHITE);var tx=ImageTexture.create_from_image(im)
	for id in clips: sf.add_animation(id);sf.add_frame(id,tx)
	var a=Actor.new();root.add_child(a);a.setup({"clips":clips},sf);a.set_physics_process(false)
	for action in Actor.HELD_PROFILES:
		var p:Array=Actor.HELD_PROFILES[action];a.reset();a.set_held(action,true);a.advance_ticks(1);a.set_held(action,false)
		check(a.clock.id==p[0] and a.clock.tick==1,action+": early release retains entry pose/time")
		a.advance_ticks(2);check(a.clock.id==p[2] and a.clock.tick==0,action+": entry completes before exit")
		a.advance_ticks(2);check(a.clock.id=="ready_still",action+": exit returns to ready")
		a.reset();a.set_held(action,true);a.advance_ticks(3);check(a.clock.id==p[1],action+": held entry reaches hold")
		a.advance_ticks(100);check(a.clock.id==p[1] and not a.clock.completed,action+": held state remains looping")
		a.set_held(action,false);check(a.clock.id==p[2],action+": release starts exit")
		a.set_held(action,true);check(a.buffered==p[0] and a.clock.id==p[2],action+": repress buffers entry until exit finishes")
		a.advance_ticks(2);check(a.clock.id==p[0],action+": repress resolves buffered entry")
		a.interrupt("hurt");check(not a.held_actions[action] and a.buffered.is_empty() and a.clock.id=="hurt",action+": hurt clears held input and buffer")
	for action in Actor.HELD_PROFILES:
		var p:Array=Actor.HELD_PROFILES[action];a.reset();a.set_held(action,true);a.advance_ticks(3);a.facing="north_back"
		check(a.set_held(action,false) and not a.held_actions[action] and a.clock.id==p[2],action+": key-up clears hold after unavailable-view request")
		a.advance_ticks(2);check(a.clock.id=="ready_still" and a.facing=="north_back",action+": finish current-view exit without inventing requested-view art")
		check(not a.request("hurt",true),action+": missing requested view still rejects new action")
		a.reset();a.set_held(action,true);a.advance_ticks(1);a.facing="north_back";a.set_held(action,false)
		check(not a.held_actions[action] and a.clock.id==p[0],action+": early key-up clears input despite missing view")
		a.advance_ticks(2);check(a.clock.id==p[2],action+": authored entry can finish into same-view exit")
		a.advance_ticks(2);check(a.clock.id=="ready_still",action+": pending exit finishes after missing-view request")
	a.reset();a.set_guard(true);a.advance_ticks(3);a.terminal=true;a.set_guard(false)
	check(not a.guard_held and a.terminal and a.clock.id=="guard_hold","Terminal key-up clears stale flag without exiting terminal")
	a.facing="north_back";check(not a.set_guard(true) and not a.guard_held,"Unavailable view cannot arm invisible guard")
	a.reset();a.terminal=true;check(not a.set_cast(true),"Terminal state rejects held input")
	var f=FileAccess.open("res://evidence/held-tests.json",FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"failures":failures,"fixture":"Synthetic1px timing/input states; art reviewed separately"},"  "));f.close()
	print("HELD TESTS ",checks,"; failures ",failures);a.queue_free();quit(0 if failures.is_empty() else 1)

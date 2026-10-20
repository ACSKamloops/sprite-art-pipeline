extends SceneTree
var checks: Array=[]
func check(label: String,value: bool)->void:
    checks.append({"label":label,"passed":value})
func _initialize()->void:
    var rig=load("res://rig.gd").new();root.add_child(rig)
    rig.configure(JSON.parse_string(FileAccess.get_file_as_string("res://design.json")),JSON.parse_string(FileAccess.get_file_as_string("res://clips.json")))
    var initial=rig.metadata.duplicate(true)
    check("Malformed equipment rejected atomically",not rig.set_equipment("spear") and rig.metadata==initial)
    check("Unknown clip cannot play",not rig.can_play("unknown"))
    check("Explicit sword selection accepted",rig.set_equipment("sword"))
    rig.pose("walk",.25,"right")
    var before=rig.metadata.duplicate(true)
    check("Wrong equipment action rejected without pose mutation",rig.pose("shoot",.5,"back").has("error") and rig.metadata==before)
    check("Cast requires explicit stow",not rig.can_play("cast"))
    check("Celebration requires explicit stow",not rig.can_play("celebrate"))
    check("Explicit stow enables cast",rig.set_equipment("none") and rig.can_play("cast"))
    var maximum=0.0;var pose_count=0
    for view in ["right","left","front","back"]:
        rig.clear_equipment_selection()
        for clip in rig.master_clips.clips:
            for sample in range(101):
                var pose=rig.pose(clip,float(sample)/100,view)
                for value in pose.ik_target_error_px.values():maximum=maxf(maximum,value)
                pose_count+=1
        for clip in ["idle","walk","run","hurt","knockdown","recover"]:
            for sample in range(101):
                rig.clear_equipment_selection()
                var baseline=rig.pose(clip,float(sample)/100,view)
                for gear in ["sword","blaster"]:
                    rig.set_equipment(gear)
                    var pose=rig.pose(clip,float(sample)/100,view)
                    check(clip+"/"+view+" equipment-independent feet/world/contact "+str(sample)+gear,pose.feet==baseline.feet and pose.world_root==baseline.world_root and pose.contact_flags==baseline.contact_flags)
                    check(clip+"/"+view+" selected gear/actual grip "+str(sample)+gear,pose.effective_equipment==gear and pose.grip==pose.landmarks.front_hand and pose.equipment_selection_mode=="persistent")
                    for value in pose.ik_target_error_px.values():maximum=maxf(maximum,value)
                    pose_count+=1
    check("All sampled base/equipped limb targets reachable",maximum<.001)
    var report={"schema":"copper-scout-v2-api-validation/v1","checks":checks,"pose_samples":pose_count,"maximum_reach_error":maximum,"scope":"Source API, atomic refusals and analytical equipment-independent foot targets. Does not approve raster contact or visual quality.","source_bindings":{}}
    for file in ["rig.gd","rig_side.gd","design.json","clips.json"]:report.source_bindings[file]=FileAccess.get_sha256("res://"+file)
    var args=OS.get_cmdline_user_args()
    if args.size()!=1:push_error("Pass one report path");quit(2);return
    FileAccess.open(args[0],FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
    var failures=0
    for item in checks:
        if not item.passed:failures+=1
    print("API samples ",pose_count," checks ",checks.size()," failures ",failures," maximum IK error ",maximum)
    quit(0 if failures==0 else 2)

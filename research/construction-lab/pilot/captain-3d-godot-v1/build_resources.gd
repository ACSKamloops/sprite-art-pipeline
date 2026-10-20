extends SceneTree
func _initialize()->void:
    call_deferred("build")
func build()->void:
    var names=DirAccess.get_directories_at("res://packs")
    var args=OS.get_cmdline_user_args()
    if args.has("--pack"):
        var position=args.find("--pack")
        if position+1>=args.size() or not names.has(args[position+1]):
            push_error("Requested pack is missing");quit(2);return
        names=PackedStringArray([args[position+1]])
    for name in names:
        var path="res://packs/"+name
        var pack=JSON.parse_string(FileAccess.get_file_as_string(path+"/pack.json"))
        var frames=SpriteFrames.new()
        frames.clear_all();frames.add_animation("walk");frames.set_animation_speed("walk",60);frames.set_animation_loop("walk",true)
        for item in pack.images:
            if FileAccess.get_sha256(item.resource_path)!=item.sha256:
                push_error("Changed source image: "+item.resource_path);quit(2);return
            var texture=load(item.resource_path)
            if not texture is Texture2D:
                push_error("Import missing: "+item.resource_path);quit(2);return
            frames.add_frame("walk",texture,1)
        if ResourceSaver.save(frames,path+"/walk.res")!=OK:
            quit(2);return
        print("SAVED_SPRITEFRAMES ",name," ",frames.get_frame_count("walk"))
    quit()

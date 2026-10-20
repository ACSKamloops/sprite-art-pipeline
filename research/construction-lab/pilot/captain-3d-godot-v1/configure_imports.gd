extends SceneTree
func _initialize()->void:
    var names=DirAccess.get_directories_at("res://packs")
    var args=OS.get_cmdline_user_args()
    if args.has("--pack"):
        var position=args.find("--pack")
        if position+1>=args.size() or not names.has(args[position+1]):
            push_error("Requested pack is missing");quit(2);return
        names=PackedStringArray([args[position+1]])
    for name in names:
        var path="res://packs/"+name
        for filename in DirAccess.get_files_at(path):
            if not filename.ends_with(".png.import"):continue
            var config=ConfigFile.new()
            if config.load(path+"/"+filename)!=OK:quit(2);return
            config.set_value("params","compress/mode",0)
            config.set_value("params","mipmaps/generate",false)
            config.set_value("params","process/fix_alpha_border",false)
            config.set_value("params","process/premult_alpha",false)
            if config.save(path+"/"+filename)!=OK:quit(2);return
    quit()

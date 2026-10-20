extends SceneTree
## Inspect the actual exported Web PCK in a fresh minimal project.
func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 3:
		quit(2)
		return
	var rows: Array = JSON.parse_string(FileAccess.get_file_as_string(args[1]))
	var output := args[2]
	var passed := ProjectSettings.load_resource_pack(args[0],true)
	var results: Array = []
	for row in rows:
		var actual := ""
		if row.kind == "manifest":
			actual = FileAccess.get_sha256(row.resource)
		else:
			var texture: Texture2D = load(row.resource)
			if texture != null:
				var im := texture.get_image()
				im.convert(Image.FORMAT_RGBA8)
				im.save_png(output.get_base_dir()+"/"+str(row.actor)+"-decoded.png")
				var h := HashingContext.new()
				h.start(HashingContext.HASH_SHA256)
				h.update(im.get_data())
				actual = h.finish().hex_encode()
		var ok: bool = actual == row.expected_sha256
		passed = passed and ok
		results.append({"resource":row.resource,"kind":row.kind,"expected_sha256":row.expected_sha256,"actual_sha256":actual,"ok":ok})
	var f := FileAccess.open(output,FileAccess.WRITE)
	f.store_string(JSON.stringify({"passed":passed,"actual_Web_PCK_sha256":FileAccess.get_sha256(args[0]),"results":results,"scope":"Actual mounted Web export manifests and decoded imported textureRGBA versus selected bake. Not a browser draw, art or motion rating."},"  ")+"\n")
	f.close()
	print("EXPORTED_BANKS "+("PASS" if passed else "FAIL")+": "+str(results.size())+" actual Web PCK resources")
	quit(0 if passed else 1)

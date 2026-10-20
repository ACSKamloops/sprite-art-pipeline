extends SceneTree
var path=""
var out=""
var checks=[]
func _initialize()->void:
 var args=OS.get_cmdline_user_args()
 for i in range(args.size()):
  if args[i]=="--cache":path=args[i+1]
  if args[i]=="--output":out=args[i+1]
 call_deferred("run")
func run()->void:
 if out.is_empty()or DirAccess.dir_exists_absolute(out):push_error("Fresh output required");quit(2);return
 DirAccess.make_dir_recursive_absolute(out)
 var baseline=JSON.parse_string(FileAccess.get_file_as_string(path));var cases=[]
 var altered=baseline.duplicate(true);altered.source_bindings.erase("rig.gd");cases.append(["missing source binding",altered])
 altered=baseline.duplicate(true);altered.fps=59;cases.append(["wrong source clock",altered])
 altered=baseline.duplicate(true);var first=altered.clips.keys()[0];altered.clips[first].duration_ticks+=1;cases.append(["wrong held duration",altered])
 altered=baseline.duplicate(true);var temp=altered.clips[first].frames[0];altered.clips[first].frames[0]=altered.clips[first].frames[1];altered.clips[first].frames[1]=temp;cases.append(["adjacent frame order swap",altered])
 altered=baseline.duplicate(true);altered.clips["walk/right"].frames[0].sole_points.front=[0,0];cases.append(["sole point disagrees actual boot pixels",altered])
 altered=baseline.duplicate(true);altered.clips["walk/right"].root_motion=[999,0];cases.append(["root motion disagrees source",altered])
 altered=baseline.duplicate(true);altered.clips["shoot/right"].events[0].tick+=1;cases.append(["event shifted one tick",altered])
 cases.push_front(["positive copy binding",baseline.duplicate(true)])
 for item in cases:
  # Relative asset paths are rebased to original immutable files; only JSON is adversarial.
  for binding in item[1].clips:
   for row in item[1].clips[binding].frames:
    row.file=("../"+path.get_base_dir().get_file()).path_join(row.file)
    for side in row.boots:row.boots[side]=("../"+path.get_base_dir().get_file()).path_join(row.boots[side])
  var filename=out.path_join(item[0].replace(" ","-")+".json");FileAccess.open(filename,FileAccess.WRITE).store_string(JSON.stringify(item[1]))
  var world=load("res://world_v2.gd").new();var accepted=world.configure(filename)
  checks.append({"description":item[0],"passed":accepted if item[0]=="positive copy binding"else not accepted,"rejection":world.error});world.free()
 var failed=checks.filter(func(v):return not v.passed)
 FileAccess.open(out.path_join("report.json"),FileAccess.WRITE).store_string(JSON.stringify({"checks":checks,"failures":failed,"passed":failed.is_empty(),"cache_sha256":FileAccess.get_sha256(path),"world_sha256":FileAccess.get_sha256("res://world_v2.gd")},"  "));print("WORLD_NEGATIVES ",checks.size()," failures ",failed.size());quit(0 if failed.is_empty()else 2)

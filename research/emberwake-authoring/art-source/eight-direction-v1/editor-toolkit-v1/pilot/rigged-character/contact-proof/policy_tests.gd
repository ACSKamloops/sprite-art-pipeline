extends SceneTree
func _initialize():
    var base=get_script().resource_path.get_base_dir().get_base_dir()
    var policy=load(base.path_join("foot_contact.gd"))
    var meta={"view":"right","feet":{"front":[111,166],"rear":[99,166]},"contact_flags":{"front":true,"rear":false}}
    var cache={"front":102,"rear":90}
    var results=[]
    var initial=JSON.stringify(meta);var cache_initial=JSON.stringify(cache)
    var valid=policy.contact_draw_root(meta,0.0,cache,80.0)
    results.append({"name":"single shared root and unchanged physics","passed":valid.draw_root==0 and valid.physical_root==0 and valid.desired_xmin==182 and valid.active_contact_residual_px.front==0})
    var flight=meta.duplicate(true);flight.contact_flags.front=false
    var flight_result=policy.contact_draw_root(flight,0.8,cache,80.0)
    results.append({"name":"flight explicitly rounds draw only","passed":flight_result.draw_root==1 and flight_result.physical_root==0.8 and flight_result.visual_child_offset>0})
    var negative=[]
    var left=meta.duplicate(true);left.view="left";negative.append(["left unsupported",left,0.0,cache])
    var missing=meta.duplicate(true);missing.erase("feet");negative.append(["missing feet",missing,0.0,cache])
    var flag=meta.duplicate(true);flag.contact_flags.front=1;negative.append(["nonboolean contact",flag,0.0,cache])
    var badfoot=meta.duplicate(true);badfoot.feet.front=[INF,166];negative.append(["infinite foot",badfoot,0.0,cache])
    negative.append(["nonfinite physics root",meta,NAN,cache])
    negative.append(["missing contact sole",meta,0.0,{"front":null,"rear":90}])
    negative.append(["fractional cache pixel",meta,0.0,{"front":102.5,"rear":90}])
    for test in negative:
        var response=policy.contact_draw_root(test[1],test[2],test[3],80.0)
        results.append({"name":test[0],"passed":response.has("error"),"response":response})
    var double=meta.duplicate(true);double.contact_flags.rear=true
    var coherent=policy.contact_draw_root(double,0.0,cache,80.0)
    var conflict=policy.contact_draw_root(double,0.0,{"front":102,"rear":89},80.0)
    results.append({"name":"double contact coherent single translation","passed":coherent.active_contact_residual_px.rear==0})
    results.append({"name":"double contact incompatible residual exposed","passed":conflict.active_contact_residual_px.front==0 and conflict.active_contact_residual_px.rear==-1})
    results.append({"name":"inputs unchanged by accepted or rejected calls","passed":JSON.stringify(meta)==initial and JSON.stringify(cache)==cache_initial})
    var passed=true
    for result in results:
        if not result.passed:passed=false
    var report={"schema":"copper-scout-contact-policy-tests/v1","policy_sha256":FileAccess.get_sha256(base.path_join("foot_contact.gd")),"passed":passed,"cases":results,"scope":"Pure policy contract tests, distinct from GPU moving-world contact proof"}
    var file=FileAccess.open(base.path_join("contact-proof/policy-tests.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"  ")+"\n")
    print("Policy tests ",results.size()," passed ",passed)
    quit(0 if passed else 1)

import importlib.util,json,sys,hashlib,subprocess,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;B=Path('/home/astra/projects/sprite-pipeline-research')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
qc=load('research_qc',B/'AI-image-to-sprite-pipeline/studio/qc.py')
image=Image.new('RGBA',(48,48));d=ImageDraw.Draw(image);d.rectangle((18,6,29,38),fill=(180,30,20,255));d.rectangle((14,38,23,43),fill=(30,30,30,255));d.rectangle((26,38,35,43),fill=(30,30,30,255));static=qc.analyze_frames([image]*8,anchor=image,flow_analysis=False)
print('QC keys',list(static));print('QC summary',static.get('summary'));print('checks',[(x.get('id'),x.get('status'))for x in static.get('checks',[])])
# Literal small counterpart of PoseMetrics.StanceSlide's median speed-deviation rule;
# NOT execution of the C# engine or a physical contact solver.
speeds=[2,2,2];steady=sorted(speeds)[len(speeds)//2];slide=max(abs(x-steady)for x in speeds)
result={'schema':'sprite.source_research_probe.v1','date':'2026-10-08','no_motion_continuity_case':static,'faithful_metric_counterexample':{'rendered_ankle_x':[0,2,4,6],'rendered_ankle_y':[40]*4,'ground_y':40,'near_is_lower_than_far':True,'median_steady_speed':steady,'metric_deviation':slide,'material_world_displacement_without_root_compensation':6,'scope':'Python counterpart of median-deviation calculation; no C# execution.'},'dotnet_available':subprocess.run(['bash','-c','command -v dotnet'],capture_output=True).returncode==0,'repositories':[]}
for owner,name in [('JatCool','AI-Sprite-Animation'),('lifeFedorovAlexey','AI-image-to-sprite-pipeline')]:
 p=B/name;commit=subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip();date=subprocess.check_output(['git','-C',str(p),'show','-s','--format=%cI',commit],text=True).strip();request=urllib.request.Request(f'https://api.github.com/repos/{owner}/{name}',headers={'User-Agent':'independent-sprite-research'});data=json.load(urllib.request.urlopen(request));result['repositories'].append({'url':data['html_url'],'local_commit':commit,'commit_date':date,'github_created_at':data['created_at'],'github_pushed_at':data['pushed_at'],'license':data.get('license',{}).get('spdx_id')})
props=load('research_props',B/'AI-image-to-sprite-pipeline/studio/rigid_props.py')
t=props.one_hand_transform(grip_point=[2,3],handle_axis=[[2,3],[2,7]],palm=[20,10],hand_angle_deg=35)
actual=props.transform_point(t,[2,3]);assert abs(actual[0]-20)<1e-9 and abs(actual[1]-10)<1e-9
reachable=props.solve_two_link_ik([0,0],[6,2],4,4);unreachable=props.solve_two_link_ik([0,0],[20,0],4,4)
result['executed_prop_math']={'grip_transform':t,'mapped_grip':actual,'reachable_ik':reachable,'unreachable_ik':unreachable}
assert static['passed'] is True
assert slide==0
assert reachable['reachable'] is True and reachable['residual']==0
assert unreachable['reachable'] is False and unreachable['residual']==12
result['executed_assertions']=5
fixture=B/'AI-Sprite-Animation/tools/posetests/fixtures/sdpose_chosen_walk.json';poses=json.loads(fixture.read_text());result['pose_fixture']={'path':str(fixture),'sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'frames':len(poses),'canvas_sizes':sorted(set((x['canvas_width'],x['canvas_height'])for x in poses)),'people_counts':[len(x['people'])for x in poses],'scope':'Structure read only; C# retargeting not executed.'}
(O/'probe-results.json').write_text(json.dumps(result,indent=2)+'\n')

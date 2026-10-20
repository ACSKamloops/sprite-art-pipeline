"""Copy only declared current fixtures and runtime code into an isolated Godot QC project."""
from pathlib import Path
import json,shutil,hashlib,argparse
root=Path(__file__).resolve().parents[2];dest=Path(__file__).resolve().parent;files=[]
def copy(src,relative):
 out=dest/relative;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out);files.append({'source':str(src),'local':str(relative),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
for name in ['authored','native_walk','native_sword']:
 for file in ['manifest.json','atlas.png']:copy(root/'godot'/name/file,Path('fixtures')/name/file)
parser=argparse.ArgumentParser();parser.add_argument('--player-source',type=Path);args=parser.parse_args();site=Path('/home/astra/projects/som-sprite-lab-site/native-godot')
for file in ['native_obj_player.gd','indexed_object.gdshader']:copy(args.player_source if file=='native_obj_player.gd' and args.player_source else site/'scripts'/file,Path('scripts')/file)
routes=[];seen_assets=set()
names=[family+'-charge-1' for family in ['glove','sword','axe','spear','whip','bow','boomerang','javelin']]+['bow-charge-3','popoi-freeze-maploaded','randi_transform_bit9_inputs','randi-native-damage-recovery','randi-native-damage-death','cup-of-wishes-revive']
for name in names:
 src=site/'routes'/name/'route.json';copy(src,Path('routes')/name/'route.json');data=json.loads(src.read_text());assets=set()
 for frame in data['frames']:
  assets.add(frame['palette_texture']);assets.update(o['indexed_texture']for o in frame['objects'])
 for asset in sorted(assets):
  if asset not in seen_assets:copy(site/asset,Path(asset));seen_assets.add(asset)
 routes.append({'id':name,'path':f'routes/{name}/route.json'})
(dest/'capture-index.json').write_text(json.dumps({'schema':'som.native_capture_index.v1','routes':routes},indent=2)+'\n');(dest/'source-bindings.json').write_text(json.dumps(files,indent=2)+'\n');(dest/'project.godot').write_text('[application]\nconfig/name="Exact animation engine QC"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
print(json.dumps({'copied_files':len(files),'native_families':len(routes)}))

"""Copy frozen source images unchanged into an isolated imported Godot pack."""
import argparse, json, hashlib, shutil, importlib.util
from pathlib import Path

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('replay',P.parent/'captain-3d-to-sprite-integration-v1/world_replay.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--contract',type=Path,required=True);parser.add_argument('--joints',type=Path,required=True);parser.add_argument('--name',required=True)
    parser.add_argument('--visual-policy',choices=['continuous','coherent'],default='continuous')
    args=parser.parse_args()
    if not args.name.replace('-','').replace('_','').isalnum():raise ValueError('Simple pack name required')
    replay=module.Replay(args.contract,args.joints)
    dest=P/'packs'/args.name
    if dest.exists():raise FileExistsError('Keep earlier pack immutable')
    dest.mkdir(parents=True)
    images=[]
    for i,frame in enumerate(replay.frames):
        source=replay.path.parent/frame['file'];target=dest/f'frame-{i:03}.png';shutil.copy2(source,target)
        assert sha(source)==sha(target)
        images.append({'file':target.name,'sha256':sha(target),'resource_path':f'res://packs/{args.name}/{target.name}'})
    pack={'state':'UNAPPROVED_DIAGNOSTIC_PACK','name':args.name,'source_contract_sha256':sha(args.contract),'source_joints_sha256':sha(args.joints),'canvas':replay.size,'camera':replay.camera.tolist(),'pixels_per_metre':replay.scale,'root_samples':[x.tolist()for x in replay.roots],'cycle_intervals':65,'output_fps':60,'images':images,'limits':['Single threequarter view only','World-root replay is presentation, not force or contact proof','Source clip remains visually unapproved']}
    pack['default_visual_root_policy']='synchronized' if args.visual_policy=='coherent' else 'continuous'
    pack['visual_clock_scope']='Whole actor root and pose snap together60Hz' if args.visual_policy=='coherent' else 'Interpolated visible root while60Hz pose held; diagnostic can slide'
    pack['source_clock_scope']='Captured120Hz ledger retained externally; this viewer does not implement game physics or colliders'
    (dest/'pack.json').write_text(json.dumps(pack,indent=2)+'\n')
    print(json.dumps({'pack':str(dest),'images':len(images),'canvas':replay.size}))
if __name__=='__main__':main()

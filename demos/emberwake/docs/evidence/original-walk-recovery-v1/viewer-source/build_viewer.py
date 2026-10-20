"""Recover exact source versions; never modify the source project or a bound viewer."""
from pathlib import Path
from fractions import Fraction
from PIL import Image
import hashlib,json,subprocess,shutil,argparse

ROOT=Path(__file__).resolve().parent
REPO=Path('/home/astra/projects/emberwake-demo')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
    assert not out.exists(),'Fresh destination required'
    out.mkdir(parents=True)
    versions={}
    rows=[]
    for key,label,source in [
        ('public','Original public release source',REPO/'art-source/eight-direction-v1/baseline'),
        ('installed','Installed diagonal prototype — registration v6',REPO/'assets'),
        ('v12','Latest isolated prototype — v12',Path('/home/astra/artifacts/emberwake-source-cel-game-preview-v12/project/assets')),
    ]:
        version={'label':label,'actors':{}}
        for actor in ['rowan','lyra','brann']:
            rel=Path('hero' if actor=='rowan' else 'characters/'+actor)
            folder=source/actor if key=='public' else source/rel
            dest=out/'references'/key/actor;dest.mkdir(parents=True)
            for name in ['atlas.png','animations.json']:
                p=folder/name
                if key=='public':
                    original=subprocess.run(['git','show','2a80f53:assets/'+(rel/name).as_posix()],cwd=REPO,capture_output=True,check=True).stdout
                    assert p.read_bytes()==original,'Public baseline differs from release Git object'
                shutil.copyfile(p,dest/name)
                rows.append({'version':key,'actor':actor,'source':str(p),'copy':str((dest/name).relative_to(out)),'sha256':sha(p)})
            manifest=json.loads((folder/'animations.json').read_text())
            atlas=Image.open(folder/'atlas.png').convert('RGBA');cw,ch=manifest['cell'];cols=manifest['columns']
            clips={}
            for name,clip in manifest['animations'].items():
                if not name.endswith('_walk'):continue
                direction=name.removesuffix('_walk');frames=[]
                for slot,index in enumerate(clip['frames']):
                    rect=((index%cols)*cw,(index//cols)*ch,(index%cols+1)*cw,(index//cols+1)*ch)
                    target=out/'frames'/key/actor/direction/f'{slot:02}.png';target.parent.mkdir(parents=True,exist_ok=True)
                    atlas.crop(rect).save(target)
                    assert Image.open(target).convert('RGBA').tobytes()==atlas.crop(rect).tobytes()
                    hold=Fraction(str(clip['holds'][slot]))
                    frames.append({'path':str(target.relative_to(out)),'sha256':sha(target),'atlas_index':index,'rectangle':rect,'hold':[hold.numerator,hold.denominator]})
                assert sum(Fraction(*f['hold']) for f in frames)==Fraction(9,20)
                clips[direction]={'frames':frames,'duration_us':450000,'loop':clip['loop'],'source_clip':name}
            version['actors'][actor]=clips
        versions[key]=version
    # These are the two rejected EXPERIMENTAL banks shown on port8797.
    for key,label,source,slots in [
        ('rejected8','Rejected experiment — painted Lyra 8',Path('/home/astra/artifacts/emberwake-lyra-front-painted-gait-v1/candidate-8-v1'),8),
        ('rejected16','Rejected experiment — rounded Lyra 16',Path('/home/astra/artifacts/emberwake-lyra-slot15-rounded-paint-v1/final16-v1'),16),
    ]:
        clips={}
        for direction in ['southeast','southwest']:
            frames=[]
            for slot in range(slots):
                p=source/f'{slot:02}.png';im=Image.open(p).convert('RGBA');assert im.size==(128,128)
                if direction=='southwest':
                    mirrored=Image.new('RGBA',(128,128));mirrored.paste(im.crop((1,0,128,128)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(1,0));im=mirrored
                target=out/'frames'/key/'lyra'/direction/f'{slot:02}.png';target.parent.mkdir(parents=True,exist_ok=True);im.save(target)
                frames.append({'path':str(target.relative_to(out)),'sha256':sha(target),'hold':[9,160*(slots//8)]})
            clips[direction]={'frames':frames,'duration_us':450000,'loop':True}
        versions[key]={'label':label,'actors':{'lyra':clips}}
    data={'schema':'emberwake-original-version-viewer-v1','versions':versions,'stage':[128,128],'pivot':[64,112],'scale':0.66,'public_source_commit':'2a80f53','public_associated_PCK_sha256':'382a06f7aa84d9532b5a4c1f3c901a004128161afabe30cb71a82ac97b8ed2ce','scope':'Exact source-atlas crops and recorded holds, not a Godot renderer or a new art approval. Public source files verified against release Git objects. Different views remain labelled.','source_files':rows}
    (out/'manifest.json').write_text(json.dumps(data,indent=2)+'\n')
    for name in ['index.html','app.js','style.css']:shutil.copyfile(ROOT/name,out/name)
    print(json.dumps({'out':str(out),'source_files_exact':len(rows),'versions':list(versions),'source_clips':sum(len(clips) for v in versions.values() for clips in v['actors'].values())}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);build(p.parse_args().out.resolve())

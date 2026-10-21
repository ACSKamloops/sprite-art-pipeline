#!/usr/bin/env python3
"""Build a portable Godot inspector from the package's selected, pinned PNGs."""
import argparse
from fractions import Fraction
import hashlib
import json
from math import lcm
from pathlib import Path
import shutil
import subprocess

from PIL import Image

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def build(args):
    package, output = args.package.resolve(), args.output.absolute()
    require(not output.exists() and not output.is_symlink(), 'Fresh output required')
    library_file = package/'library.json'
    library = json.loads(library_file.read_text())
    require(library['schema'] == 'rpg-review-library/v1', 'Unsupported package library')
    expected = {f'{action}_{direction}' for direction in library['directions'] for action in library['actions']}
    require(len(library['directions']) == 8 and len(library['actions']) == 6 and len(expected) == 48, 'Expected8directions x6actions')
    require(set(library['directions']) == {'N','NE','E','SE','S','SW','W','NW'} and set(library['actions']) == {'walk','punch','cast','idle','hurt','dodge'}, 'Unexpected bank actions/directions')
    require(set(library['selected']) == expected, 'Complete48selected resource bindings required')
    by_id = {clip['id']: clip for clip in library['clips']}
    clips, source_pins, holds = [], {}, []
    for name, clip_id in library['selected'].items():
        clip = by_id[clip_id]
        require(clip['direction'] in library['directions'] and clip['action'] in library['actions'], 'Unknown action/view')
        require(name == f"{clip['action']}_{clip['direction']}", 'Binding/action mismatch')
        manifest_path = package/clip['manifest']
        require(manifest_path.resolve().is_relative_to(package), 'Escaping manifest')
        require(digest(manifest_path) == clip['manifest_sha256'], 'Stale selected manifest')
        source_pins[clip['manifest']] = clip['manifest_sha256']
        records = []
        for index, frame in enumerate(clip['frames']):
            source = (package/frame['file']).resolve()
            require(source.is_relative_to(package) and digest(source) == frame['sha256'], 'Escaping/stale selected frame')
            with Image.open(source) as image:
                require(image.format == 'PNG' and image.size == (80,80) and getattr(image,'n_frames',1) == 1, 'Expected static80px PNG')
                rgba_hash = hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest()
            require(frame.get('rgba_sha256',rgba_hash) == rgba_hash, 'Stale sourceRGBA hash')
            hold = Fraction(*frame['hold'])
            require(hold > 0, 'Positive rational hold required')
            holds.append(hold)
            records.append({'file':f'assets/{name}/{index:04d}.png', 'source_file':frame['file'], 'sha256':frame['sha256'], 'rgba_sha256':rgba_hash, 'hold':[hold.numerator,hold.denominator]})
            source_pins[frame['file']] = frame['sha256']
        require(bool(records) and sum((Fraction(*f['hold']) for f in records),Fraction()) == Fraction(*clip['duration']), 'Duration mismatch')
        clips.append({'name':name, 'direction':clip['direction'], 'action':clip['action'], 'loop':clip['loop'], 'role':clip['role'], 'review_status':clip['review_status'],
                      'source_clip_id':clip_id, 'source_manifest':clip['manifest'], 'frames':records, 'events':clip.get('events',[]), 'duration':clip['duration']})
    require(library['selected']['walk_SE'] == library['reference'], 'Preferred original SE walk must stay selected')
    require(by_id[library['reference']]['role'] == 'preferred', 'Preferred baseline role missing')
    rate = lcm(*(h.denominator for h in holds))
    output.mkdir(parents=True)
    for clip in clips:
        for frame in clip['frames']:
            destination = output/frame['file']
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(package/frame['source_file'],destination)
            frame['ticks'] = int(Fraction(*frame['hold'])*rate)
            require(digest(destination) == frame['sha256'], 'PNG copy mismatch')
    config = {'completion_return':{'punch':'punch_ready','cast':'cast_ready','hurt':'idle','dodge':'idle'},
              'ready_states':{'punch_ready':{'source_action':'punch','frame':0},'cast_ready':{'source_action':'cast','frame':0}},
              'move_speed':100, 'start_direction':'SE', 'anchors':{'hand':'pending measurement','grip':'pending measurement','release':'pending measurement'}}
    if args.config:
        config = json.loads(args.config.read_text())
    bank = {'schema':'rpg-godot-inspector/v1','canvas':[80,80],'pivot':[40,72],'tick_rate':rate,'directions':library['directions'],'actions':library['actions'],
            'clips':clips,'config':config,'preferred_walk_binding':'walk_SE','preferred_source_clip':library['reference'],
            'source_library_sha256':digest(library_file),'source_file_sha256':source_pins,
            'limits':'Resource/input/clock inspector only. New art remains unreviewed; movement does not prove contact/collision. Authored events have no damage/VFX behavior; hand/grip/release anchors pending.'}
    write(output/'bank.json',bank)
    template_pins = {}
    for source in (HERE/'rpg-preview').iterdir():
        if source.is_file():
            shutil.copy2(source,output/source.name)
            template_pins[source.name] = digest(source)
            require(digest(output/source.name) == template_pins[source.name], 'Template copy changed')
    (output/'project.godot').write_text('''config_version=5
[application]
config/name="Hero RPG bank inspector"
run/main_scene="res://main.tscn"
[display]
window/size/viewport_width=1100
window/size/viewport_height=760
window/stretch/mode="canvas_items"
[rendering]
renderer/rendering_method="gl_compatibility"
textures/default_filters/use_nearest_mipmap_filter=false
environment/defaults/default_clear_color=Color(0.075,0.095,0.125,1)
''')
    commands = [[args.godot,'--headless','--path',str(output),'--script','res://build_resources.gd'],
                [args.godot,'--headless','--path',str(output),'--script','res://validate.gd']]
    if args.check:
        version = subprocess.check_output([args.godot,'--version'],text=True).strip()
        invocations = []
        for command in commands:
            try:
                result = subprocess.run(command,text=True,capture_output=True,timeout=45)
            except subprocess.TimeoutExpired as error:
                invocations.append({'argv':command,'returncode':124,'stdout':str(error.stdout or ''),'stderr':str(error.stderr or ''),'error':'45second check timeout'})
                write(output/'ENGINE-INVOCATIONS.json',{'godot_version':version,'invocations':invocations})
                raise ValueError('Godot check timed out; see ENGINE-INVOCATIONS.json') from error
            invocations.append({'argv':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
            write(output/'ENGINE-INVOCATIONS.json',{'godot_version':version,'invocations':invocations})
            require(result.returncode == 0, 'Godot check failed; see ENGINE-INVOCATIONS.json')
        for filename in ['RESOURCE-VALIDATION.json','RUNTIME-VALIDATION.json']:
            require((output/filename).is_file(), 'Godot did not produce '+filename)
            require(not json.loads((output/filename).read_text()).get('failures'), 'Godot validation reported failures')
    require(all(digest(package/name) == pin for name,pin in source_pins.items()) and digest(library_file) == bank['source_library_sha256'], 'Source package changed during build')
    write(output/'BUILD-RECEIPT.json',{'schema':'rpg-inspector-build/v1','builder_sha256':digest(Path(__file__)),'source_package':str(package),'source_unchanged':True,
                                     'template_sha256':template_pins,'bank_sha256':digest(output/'bank.json'),
                                     'source_library_sha256':bank['source_library_sha256'],'clips':len(clips),'frames':sum(len(c['frames']) for c in clips),
                                     'common_tick_rate':rate,'preferred_walk_SE_original_preserved':True,'checks_run':args.check,
                                     'commands':commands,'scope':bank['limits']})
    (output/'README.txt').write_text('Run: godot --path .\nBuild/check: godot --headless --path . --script res://build_resources.gd\nValidate: godot --headless --path . --script res://validate.gd\nArrows/WASD move and face in8directions. J punch, K cast, L dodge, H hurt. Space toggles in-place walk. Right mouse sets aim only.\nOne-shots return through bank.json explicit completion_return/ready_states config. Punch holds punch frame0; cast holds cast frame0. Hurt/dodge return idle. No weapon/effect/damage behavior.\nThe inspector is portable after build; original source_package is provenance only. All runtime paths are relative.\n')
    return {'output':str(output),'clips':len(clips),'frames':sum(len(c['frames']) for c in clips),'tick_rate':rate,'checks_run':args.check}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--godot',default='godot')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    try:
        print(json.dumps(build(args)))
    except (OSError,ValueError,KeyError,TypeError,subprocess.CalledProcessError) as error:
        parser.exit(2,f'Error: {error}\n')


if __name__ == '__main__':
    main()

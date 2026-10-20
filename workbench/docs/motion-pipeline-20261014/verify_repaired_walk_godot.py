#!/usr/bin/env python3
"""Real-engine proof in a new external copy; never import into the source export."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from PIL import Image

SEQUENCE = '9f9e1c53324ea567cb1bbd5be8c310691c0f87f45044279c1f37d81349e66d79'

SCRIPT = r'''extends SceneTree
var errors: Array = []
var checks: Array = []
var pixels: Array = []
var frame_callbacks: Array = []
var loop_callbacks: Array = []
var finished: int = 0
var completed: int = 0
func check(ok: bool, label: String) -> void:
    checks.append({"id":label,"passed":ok})
    if not ok: errors.append(label)
func rgba_sha(image: Image) -> String:
    var ctx = HashingContext.new()
    ctx.start(HashingContext.HASH_SHA256)
    ctx.update(image.get_data())
    return ctx.finish().hex_encode()
func _initialize() -> void:
    call_deferred("verify")
func verify() -> void:
    var scene = load("res://clip.tscn").instantiate()
    var sprite: AnimatedSprite2D = scene.get_node("AnimatedSprite2D")
    sprite.frame_changed.connect(func(): frame_callbacks.append(sprite.frame))
    sprite.animation_looped.connect(func(): loop_callbacks.append({"time":scene.elapsed_seconds,"frame":sprite.frame,"plays":scene.completed_plays}))
    sprite.animation_finished.connect(func(): finished += 1)
    scene.playback_completed.connect(func(): completed += 1)
    root.add_child(scene)
    scene.set_process(false)
    var total: float = scene.timeline.total
    var resources: SpriteFrames = sprite.sprite_frames
    check(scene.timeline.sequence_id == "9f9e1c53324ea567cb1bbd5be8c310691c0f87f45044279c1f37d81349e66d79","sequence binding")
    check(resources.get_frame_count(&"clip")==8,"eight texture regions")
    check(resources.get_animation_loop(&"clip") and scene.timeline.play_count==0,"declared infinite loop")
    check(abs(total-5.0/3.0)<0.000000001,"total five thirds seconds")
    check(sprite.speed_scale==0.0 and scene.rate==1.0,"driver owns clock at rate one")
    check(ResourceSaver.save(resources,"res://roundtrip.tres")==OK,"save actual imported resource")
    var reload = ResourceLoader.load("res://roundtrip.tres","SpriteFrames",ResourceLoader.CACHE_MODE_IGNORE)
    check(reload.get_animation_loop(&"clip"),"reloaded resource retains loop")
    for i in range(8):
        var texture: AtlasTexture = reload.get_frame_texture(&"clip",i)
        var expected = Image.load_from_file("res://frame-%04d.png" % i)
        var actual = texture.get_image()
        expected.convert(Image.FORMAT_RGBA8)
        actual.convert(Image.FORMAT_RGBA8)
        check(actual.get_width()==256 and actual.get_height()==256,"region dimensions %d" % i)
        check(actual.get_data()==expected.get_data(),"decoded actual texture RGBA %d" % i)
        check(abs(reload.get_frame_duration(&"clip",i)-5.0/24.0)<0.0000001,"resource hold %d" % i)
        pixels.append({"index":i,"rgba_sha256":rgba_sha(actual),"bytes":actual.get_data().size(),"duration":reload.get_frame_duration(&"clip",i),"duration_error_seconds":reload.get_frame_duration(&"clip",i)-5.0/24.0})
        # Public API has no direct seek: restart plus elapsed advancement is used.
        scene.restart()
        scene.advance_seconds(float(scene.timeline.starts[i])+5.0/48.0)
        check(sprite.frame==i and abs(sprite.frame_progress-0.5)<0.000001,"seek midpoint via driver %d" % i)
        scene.restart()
        scene.advance_seconds(float(scene.timeline.ends[i])-0.00000001)
        check(sprite.frame==i,"just before hold boundary %d" % i)
        scene.restart()
        scene.advance_seconds(float(scene.timeline.ends[i]))
        check(sprite.frame==(i+1)%8,"exact hold boundary %d" % i)
    scene.restart()
    scene.advance_seconds(total*3.0)
    check(scene.completed_plays==3 and sprite.frame==0,"deterministic exact third wrap")
    frame_callbacks.clear()
    loop_callbacks.clear()
    finished=0
    completed=0
    scene.restart()
    var wall_start: int = Time.get_ticks_usec()
    scene.set_process(true)
    await create_timer(total*3.0+0.15).timeout
    scene.set_process(false)
    var wall_seconds: float = float(Time.get_ticks_usec()-wall_start)/1000000.0
    var normal_state = scene.get_playback_state().duplicate(true)
    var normal_callbacks = frame_callbacks.duplicate()
    var normal_loops = loop_callbacks.duplicate(true)
    check(wall_seconds>=5.0 and scene.elapsed_seconds>=5.0,"normal wall and owned elapsed exceed three cycles")
    check(scene.completed_plays>=3 and loop_callbacks.size()>=3,"normal process crosses three loop boundaries")
    check(scene.playing and not scene.completed and finished==0 and completed==0,"normal infinite playback never signals finite completion")
    for i in range(8): check(i in frame_callbacks,"normal frame callback coverage %d" % i)
    for callback in loop_callbacks:
        check(callback.frame==7 and abs(callback.time-float(callback.plays)*total)<0.000001,"loop callback at owned boundary")
    check(scene.pause(),"pause accepted")
    var paused = scene.get_playback_state().duplicate(true)
    scene.set_process(true)
    await create_timer(0.08).timeout
    scene.set_process(false)
    check(scene.get_playback_state()==paused,"normal process pause freezes complete state")
    check(scene.restart(),"restart accepted")
    check(scene.elapsed_seconds==0.0 and scene.completed_plays==0 and sprite.frame==0 and scene.playing,"restart resets own clock and first frame")
    var output=FileAccess.open("res://GODOT-RECEIPT.json",FileAccess.WRITE)
    output.store_string(JSON.stringify({"status":"passed" if errors.is_empty() else "failed","errors":errors,"checks":checks,"engine":Engine.get_version_info(),"textures":pixels,"normal_wall_seconds":wall_seconds,"normal_state":normal_state,"normal_frame_callbacks":normal_callbacks,"normal_loop_callbacks":normal_loops,"authored_event_count":scene.timeline.events.size(),"native_finished_signals":finished,"playback_completed_signals":completed,"limitations":"Headless imported resources and elapsed driver only; no GPU screenshot, audio, world foot contact, rig or art approval"},"  "))
    quit(0 if errors.is_empty() else 2)
'''


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def inventory(directory):
    return {str(p.relative_to(directory)): {'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
            for p in sorted(directory.rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export-godot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sequence', default=SEQUENCE)
    args = parser.parse_args()
    source = args.export_godot.resolve(); output = args.output.resolve()
    require(re.fullmatch(r'[0-9a-f]{64}', args.sequence) is not None, 'Full sequence SHA256 required')
    require(not output.is_relative_to(source.parent), 'Proof output must be outside original export')
    require(not source.is_symlink() and source.is_dir(), 'Original Godot export required')
    inputs = inventory(source)
    manifest = json.loads((source/'timeline.json').read_bytes())
    require(manifest['sequence_id']==args.sequence and len(manifest['frames'])==8, 'Wrong repaired sequence')
    require(all(f['duration']==[5,24] for f in manifest['frames']), 'Exact rational holds differ')
    require(manifest['total']==[5,3] and manifest['loop'] is True and manifest['play_count']==0, 'Clock differs')
    frames = source.parent/'frames'
    frame_inputs = inventory(frames)
    output.mkdir(parents=True, exist_ok=False)
    project = output/'project'; shutil.copytree(source,project)
    expected=[]
    for i in range(8):
        name=f'frame-{i:04d}.png'; shutil.copy2(frames/name,project/name)
        with Image.open(frames/name) as image:
            require(image.size==(256,256), 'Source PNG dimensions differ')
            expected.append(sha(image.convert('RGBA').tobytes()))
    (project/'verify.gd').write_text(SCRIPT.replace(SEQUENCE,args.sequence))
    engine=shutil.which('godot') or shutil.which('godot4')
    require(engine is not None,'Actual Godot required')
    env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'HOME':str(output/'home'),
         'XDG_DATA_HOME':str(output/'data'),'XDG_CONFIG_HOME':str(output/'config'),
         'XDG_CACHE_HOME':str(output/'cache'),'LANG':'C.UTF-8'}
    commands=[[engine,'--headless','--path',str(project),'--editor','--import'],
              [engine,'--headless','--path',str(project),'--script','res://verify.gd','--max-fps','240']]
    runs=[]
    for index,cmd in enumerate(commands):
        ran=subprocess.run(cmd,env=env,capture_output=True,timeout=40 if index==0 else 20)
        (output/f'engine-{index}.log').write_bytes(ran.stdout+ran.stderr)
        runs.append({'command':cmd,'returncode':ran.returncode,'log_sha256':sha(ran.stdout+ran.stderr)})
        require(ran.returncode==0,'Godot failed; inspect isolated engine log')
    receipt=json.loads((project/'GODOT-RECEIPT.json').read_bytes())
    require(receipt['status']=='passed' and not receipt['errors'],'Godot checks failed')
    require([r['rgba_sha256'] for r in receipt['textures']]==expected,'Engine RGBA differs from decoded PNG')
    require(inventory(source)==inputs and inventory(frames)==frame_inputs,'Original source export changed')
    report={'kind':'repaired-walk-godot-runtime-proof','version':1,'sequence':args.sequence,
            'source':str(source),'source_inputs':inputs,'frame_inputs':frame_inputs,
            'commands':runs,'driver_copied_unchanged':sha((project/'driver.gd').read_bytes())==inputs['driver.gd']['sha256'],
            'original_godot_and_png_inputs_unchanged':True,'expected_rgba_sha256':expected,'engine_receipt':receipt,
            'provider_calls':0,'visual_acceptance':'unapproved'}
    (output/'PROOF.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':'passed','checks':len(receipt['checks']),'normal_wall_seconds':receipt['normal_wall_seconds'],
                      'normal_completed_plays':receipt['normal_state']['completed_plays'],'proof':str(output/'PROOF.json')}))


if __name__=='__main__':
    main()

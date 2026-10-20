"""Actual exported Godot resources/driver, authored events and runtime boundaries."""
from fractions import Fraction
import json
import os
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

from sprite_workbench.core import Store, ValidationError, save_sequence
from sprite_workbench.export import export_sequence


GODOT_TEST = r'''extends SceneTree
var errors: Array = []
var events: Array = []
var finished: int = 0
var looped: int = 0
var completed_signals: int = 0
func check(value: bool, label: String) -> void:
    if not value: errors.append(label)
func _initialize() -> void:
    call_deferred("run_checks")
func run_checks() -> void:
    var packed: PackedScene = load("res://clip.tscn")
    if packed == null:
        printerr("Cannot load exported scene")
        quit(2)
        return
    var scene = packed.instantiate()
    var sprite: AnimatedSprite2D = scene.get_node("AnimatedSprite2D")
    scene.timeline_event.connect(func(event):
        check(sprite.frame == event.frame, "event callback sees actual current frame")
        check(abs(scene.elapsed_seconds-event.absolute_seconds)<0.0000001,"one event clock")
        if event.name == "marker-start": check(sprite.frame==0,"wrapped start event observes first frame")
        if event.name.begins_with("marker-boundary"): check(sprite.frame==1,"authored boundary event observes next frame")
        if event.name == "marker-last": check(sprite.frame==2,"last authored event observes last frame")
        events.append(event.duplicate(true)))
    scene.playback_completed.connect(func(): completed_signals += 1)
    sprite.animation_finished.connect(func(): finished += 1)
    sprite.animation_looped.connect(func(): looped += 1)
    root.add_child(scene)
    scene.set_process(false)
    var count: int = scene.timeline.play_count
    var total: float = scene.timeline.total
    check(events.size() == 1 and events[0].name == "marker-start", "start event once")
    check(sprite.frame == 0 and sprite.offset == Vector2(-1,0),"initial frame/pivot")
    check(sprite.speed_scale == 0.0 and sprite.is_playing(),"native clock disabled, play flag retained")
    check(scene.get_node("Camera2D").position == Vector2(0,0.5),"fixed camera envelope center")
    var resources: SpriteFrames = sprite.sprite_frames
    check(ResourceSaver.save(resources,"res://reloaded.tres")==OK,"save resource")
    var reload = ResourceLoader.load("res://reloaded.tres","SpriteFrames",ResourceLoader.CACHE_MODE_IGNORE)
    for i in range(3):
        check(abs(reload.get_frame_duration(&"clip",i)-scene.timeline.durations[i])<0.0000001,"hold resource")
        var texture: AtlasTexture = reload.get_frame_texture(&"clip",i)
        var expected = Image.load_from_file("res://frame-%04d.png" % i)
        var actual = texture.get_image()
        expected.convert(Image.FORMAT_RGBA8)
        actual.convert(Image.FORMAT_RGBA8)
        check(actual.get_data()==expected.get_data(),"actual fullRGBA texture %d" % i)
    check(reload.get_animation_loop(&"clip") == (count==0),"resource loop")
    check(scene.pause(),"pause accepted")
    check(scene.advance_seconds(1.0) and scene.elapsed_seconds == 0.0 and events.size()==1,"paused deterministic freeze")
    check(scene.play(),"play accepted")
    check(scene.advance_seconds(scene.timeline.ends[0]),"advance to boundary")
    check(sprite.frame == 1 and sprite.offset == Vector2(-2,-1),"exact hold boundary/pivot")
    check(events.size()==3 and events[1].name=="marker-boundary-a" and events[2].name=="marker-boundary-b","simultaneous event stable order")
    scene.pause()
    var paused_state = scene.get_playback_state().duplicate(true)
    scene.set_process(true)
    await create_timer(0.025).timeout
    check(scene.get_playback_state() == paused_state,"actual process pause freezes")
    scene.set_process(false)
    scene.restart()
    events.clear()
    finished=0
    looped=0
    completed_signals=0
    check(scene.advance_seconds(total*2.25),"large crossing advance")
    var expected_events: int = 10 if count==0 else count*4-1
    check(events.size()==expected_events,"all crossed events including wraps")
    if count==0:
        check(not scene.completed and scene.completed_plays==2 and sprite.frame==1,"loop state after two wraps")
        check(looped==2 and finished==0,"native-compatible loop signals")
        var stable = scene.get_playback_state().duplicate(true)
        check(not scene.advance_seconds(total*100000),"overbudget crossing rejects")
        check(scene.get_playback_state()==stable,"overbudget no state change")
    else:
        check(scene.completed and not scene.playing and sprite.frame==2 and sprite.frame_progress==1.0,"one-shot/finites hold final")
        check(scene.completed_plays==count and finished==count and completed_signals==1,"finite play/event signals")
        check(not scene.play(),"play does not restart completed clip")
        var final_state=scene.get_playback_state().duplicate(true)
        scene.advance_seconds(10.0)
        check(scene.get_playback_state()==final_state,"completed stays frozen")
    if count==0:
        scene.restart()
        events.clear()
        check(scene.advance_seconds(total*3.0),"exact third wrap accepted")
        check(scene.completed_plays==3 and sprite.frame==0,"exact loop boundary selects first frame")
    check(scene.restart(),"explicit restart accepted")
    check(not scene.completed and scene.playing and scene.elapsed_seconds==0.0 and scene.completed_plays==0 and sprite.frame==0,"restart clears completion")
    check(scene.set_rate(2.0),"speed accepted")
    check(scene.advance_seconds(scene.timeline.ends[0]/2.0) and sprite.frame==1,"speed scales wall time only")
    scene.pause()
    check(not scene.advance_seconds(-1.0) and not scene.set_rate(0.0),"invalid clock controls reject")
    scene.set_rate(1.0)
    scene.restart()
    events.clear()
    finished=0
    looped=0
    completed_signals=0
    scene.set_process(true)
    await create_timer(total*2.0+0.06).timeout
    scene.set_process(false)
    if count==0:
        check(scene.completed_plays>=2 and scene.playing and not scene.completed,"actual timed looping")
        check(looped>=2,"actual timed loop boundaries")
    else:
        check(scene.completed and finished==count and completed_signals==1,"actual timed completion")
        check(sprite.frame==2 and not sprite.is_playing(),"actual timed final hold")
    var file=FileAccess.open("res://reliable-godot-receipt.json",FileAccess.WRITE)
    file.store_string(JSON.stringify({"errors":errors,"play_count":count,"state":scene.get_playback_state(),"events":events,"finished":finished,"looped":looped,"engine":Engine.get_version_info(),"scope":"actual headless resources, decoded textures and timed driver; no GPU/art approval"}))
    quit(0 if errors.is_empty() else 2)
'''


def export_fixture(tmp_path, count, metadata=None):
    store = Store(tmp_path / 'store')
    a = np.zeros((2, 3, 4), dtype=np.uint8); a[0, 0] = [17, 29, 41, 255]; a[1, 1] = [19, 23, 31, 0]
    b = a.copy(); b[0, 2] = [71, 89, 107, 127]
    meta = {'fps': 120, 'events': [{'at_tick': 0, 'name': 'marker-start'},
            {'at_tick': 2, 'name': 'marker-boundary-a'}, {'at_tick': 2, 'name': 'marker-boundary-b'},
            {'at_tick': 9, 'name': 'marker-last'}]} if metadata is None else metadata
    sequence = save_sequence(store, [a, b, a], durations=[Fraction(1, 60), Fraction(1, 20), Fraction(1, 60)],
                             pivots=[[1, 0], [2, 1], [1, 0]], loop=count == 0, play_count=count, metadata=meta)
    return export_sequence(store, sequence, tmp_path / 'published', ['godot', 'manifest'])


@pytest.mark.parametrize('count', [0, 1, 2])
def test_reliable_exported_Godot_single_clock_and_actual_playback(tmp_path, count):
    executable = shutil.which('godot') or shutil.which('godot4')
    if executable is None:
        pytest.skip('Godot unavailable; no engine verification claimed')
    result = export_fixture(tmp_path, count)
    assert result['formats']['godot']['status'] == 'written'
    project = tmp_path / 'engine'
    shutil.copytree(tmp_path / 'published/godot', project)
    for source in (tmp_path / 'published/frames').glob('*.png'):
        shutil.copy2(source, project / source.name)
    (project / 'verify.gd').write_text(GODOT_TEST)
    env = {**os.environ, 'XDG_DATA_HOME': str(tmp_path / 'engine-data')}
    imported = subprocess.run([executable, '--headless', '--path', str(project), '--editor', '--import'],
                              capture_output=True, text=True, timeout=40, env=env)
    assert imported.returncode == 0, imported.stdout + imported.stderr
    ran = subprocess.run([executable, '--headless', '--path', str(project), '--script', 'res://verify.gd', '--max-fps', '240'],
                         capture_output=True, text=True, timeout=15, env=env)
    assert ran.returncode == 0, ran.stdout + ran.stderr
    receipt = json.loads((project / 'reliable-godot-receipt.json').read_text())
    assert receipt['errors'] == [], receipt
    assert receipt['play_count'] == count


@pytest.mark.parametrize('metadata', [
    {'events': 'bad'}, {'events': [{'at_tick': 1, 'name': 'missing-clock'}]},
    {'fps': 120, 'events': [{'at_tick': 10, 'name': 'outside'}]},
    {'fps': True, 'events': [{'at_tick': 1, 'name': 'bool-clock'}]},
    {'fps': 120, 'events': [{'at_tick': True, 'name': 'bool-tick'}]},
    {'fps': 120, 'events': [{'at_tick': 1, 'name': 'marker', 'made_up': True}]},
])
def test_invalid_exported_event_metadata_does_not_publish(tmp_path, metadata):
    with pytest.raises(ValidationError):
        export_fixture(tmp_path, 1, metadata)
    assert not (tmp_path / 'published').exists()

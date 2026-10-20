"""Callable supplied-marker replays; mechanics only, never vendor/art acceptance."""
from __future__ import annotations

import copy
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
from PIL import Image

from .core import Store, ValidationError, canonical_json, digest, load_sequence, save_sequence
from .scene import render_scene
from .tracks import bake_tracks
from .raster import edit_sequence
from .composition import compose_sequences
from .effects import render_effect
from .export import export_sequence, import_editable

FLOW_IDS = ('F02', 'F09', 'F10')
LIMITATIONS = [
    'Asymmetric synthetic supplied pixels establish mechanics only; art and motion quality unreviewed.',
    'No private model, generation, provider, hidden anatomy or full vendor/editor parity.',
    'Review HTML creation and headless engine checks are not continuous visual/GPU/video acceptance.',
]

# Retained exact shipped UI/worker arc case /cases/60, not freshly manufactured goldens.
ARC_HASHES = (
    'dfd05c8a8b7f31c9fef19529564004d46303f04d417cd77f6c70d2363d488970',
    '1223697cf6df129fabdf6858c3016f821c37d887ebf0760adb5bf3be06cacff3',
    '7565ec756290639a687ed4cf0e3acaacb0d5930d323d458857f25b9471f32120',
    '97ce85fa159bf1d5ab32f080156e13bb1da3d4d451e81766649cd6f73f46c46c',
    '2b58adbd245a9d280d0a2778e18bd87ab1b473cd36ec5f5bf7ed77b941ed100d',
    'd09d29f38063759a7c51a1feb429427987d1ec637deb6e1ac16fe09c6bef64aa',
    '69eaa1e4c5dbedb829fc022ce038f4758120242c9929dfa1794ec5b87637deb2',
    '4fe7b59af6de3b665b67788cc2f99892ab827efae3a467342b3bb4e3bc8e5bfe',
)
ARC_AUTHORITY = {'path':'analysis-models/depth-round3/renderer-fixtures/OUTCOMES-revised.json',
    'sha256':'bd825b49b605693d4f85636df496e85201b89deb0c104ca5313254e5c14f762c',
    'json_pointer':'/cases/60', 'scope':'retained adapter parity, not independent neural/art algorithm'}


def _check(checks, name, passed, detail=None):
    record = {'name':name, 'passed':bool(passed)}
    if detail is not None:
        record['detail'] = detail
    checks.append(record)


def _rejected(checks, name, call):
    try:
        call()
    except ValidationError as error:
        _check(checks,name,True,str(error))
    else:
        _check(checks,name,False,'Expected local admission/guard rejection did not occur')


def _owned_body(store, checks, *, canvas=16, frames=3, fps=10):
    art = np.zeros((3,4,4),np.uint8)
    art[0,0]=[255,0,0,255]; art[0,1]=[0,255,0,255]
    art[1,0]=[0,0,255,255]; art[2,3]=[255,255,0,255]
    art[2,2]=[11,22,33,0]
    body = np.zeros_like(art); arm = body.copy()
    for y,x in [(0,0),(0,1),(2,2)]: body[y,x,3]=255
    for y,x in [(1,0),(2,3)]: arm[y,x,3]=255
    source,bmask,amask = (store.put_raster(a) for a in (art,body,arm))
    scene = {'canvas':[canvas,canvas], 'require_source_coverage':True, 'clip_policy':'reject',
        'nodes':[{'id':'root','position':[1,1]},
            {'id':'body','parent':'root','raster':source,'mask':bmask,'z':1,
             'ownership':{'source':source,'origin':[0,0]}},
            {'id':'arm','parent':'root','raster':source,'mask':amask,'anchor':[.5,1.5],'z':2,
             'ownership':{'source':source,'origin':[0,0]}}]}
    offsets = [0,2,2] if frames==3 else [0,0,2,2,4,4,4,4]
    keys = [{'time':[0,1],'value':[0,0]},
        {'time':[1 if frames==3 else 2,fps],'value':[2,0]}]
    if frames==8: keys.append({'time':[4,fps],'value':[4,0]})
    tracks = [{'node':'arm','property':'position','interpolation':'hold','keys':keys}]
    baked,audit = bake_tracks(scene,tracks,frame_count=frames,fps=fps,
        direction='diagnostic-south',pivot=[1,3])
    track_id = store.put_json({'kind':'track-bake',**audit})
    baked['metadata']={'track_audit':track_id}
    original = render_scene(store,baked)
    doc,actual = load_sequence(store,original)
    # Independent destination enumeration: no transform/projector called for these goldens.
    goldens=[]
    for dx in offsets:
        a=np.zeros((canvas,canvas,4),np.uint8)
        a[1,1]=art[0,0]; a[1,2]=art[0,1]; a[3,3]=art[2,2]
        a[2,1+dx]=art[1,0]; a[3,4+dx]=art[2,3]; goldens.append(a)
    _check(checks,'owned parent/anchor track destinations including hidden RGB',
           len(actual)==len(goldens) and all(np.array_equal(a,b) for a,b in zip(actual,goldens)))
    _check(checks,'explicit frame order, clock, pivot and direction',
        len(doc['frames'])==frames and all(f['duration']==[1,fps] and f['pivot']==[1,3]
            and f['direction']=='diagnostic-south' for f in doc['frames']))
    overlap=copy.deepcopy(baked);overlap['nodes'][2]['mask']=bmask
    _rejected(checks,'overlapping source ownership rejected',lambda:render_scene(store,overlap))
    frozen=copy.deepcopy(baked);frozen['guards']={'reference_sequence':original,'frozen_frames':[0]}
    frozen['frames'][0]['nodes']['root']={'position':[2,1]}
    _rejected(checks,'changed frozen reference frame rejected',lambda:render_scene(store,frozen))
    changes=[{'operation':'patch_pixels','frames':[1],'layer':'image',
        'reason':'Mechanical red to yellow marker repair','pixels':[[1,1,'#ff0000ff','#ffff00ff']]}]
    edited=edit_sequence(store,original,changes)
    goldens[0]=goldens[0].copy();goldens[0][1,1]=[255,255,0,255]
    _,actual=load_sequence(store,edited['sequence'])
    _check(checks,'one-based expected-color fine edit changes only declared frame/pixel',
           all(np.array_equal(a,b) for a,b in zip(actual,goldens)))
    wrong=copy.deepcopy(changes);wrong[0]['pixels'][0][2]='#000000ff'
    _rejected(checks,'stale expected color rejects edit',lambda:edit_sequence(store,original,wrong))
    definition=store.put_json({'kind':'replay-input','version':1,'scene':baked,'tracks':tracks,
        'changes':changes,'source':source,'body_mask':bmask,'arm_mask':amask})
    return {'sequence':edited['sequence'],'unedited_sequence':original,'revision':edited['revision'],
        'source':source,'body_mask':bmask,'arm_mask':amask,'track_audit':track_id,
        'scene':doc['metadata']['scene_id'],'fixture':definition}, goldens


def _exchange(store, sequence, output, checks, *, formats):
    export = export_sequence(store,sequence,output/'export',formats)
    _check(checks,'requested exchange files written',all(x['status']=='written' for x in export['formats'].values()),
           {k:v['status'] for k,v in export['formats'].items()})
    fresh=Store(output/'fresh-store')
    imported=import_editable(fresh,output/'export/editable')
    doc,arrays=load_sequence(store,sequence);again,decoded=load_sequence(fresh,imported)
    _check(checks,'editable fresh Store full document and RGBA identity',
        imported==sequence and doc==again and all(np.array_equal(a,b) for a,b in zip(arrays,decoded)))
    review=json.loads((output/'export/review/review.json').read_text())
    _check(checks,'all ordered adjacent pairs and return seam retained',
        [(p['from'],p['to']) for p in review['pairs']]==[(i,i+1) for i in range(len(arrays)-1)]+[(len(arrays)-1,0)]
        and review['diagnostic_coverage']['continuous_motion_viewed'] is False)
    return export,fresh


def _f02(store,output,checks):
    artifacts,goldens=_owned_body(store,checks)
    export,fresh=_exchange(store,artifacts['sequence'],output,checks,formats=['png','sheet','manifest','apng','editable','review'])
    layered=fresh.get_json(artifacts['scene'])
    rebuilt=render_scene(fresh,layered['scene'])
    _check(checks,'original editable owned scene rerenders exactly',rebuilt==artifacts['unedited_sequence'])
    _check(checks,'original source/masks/track audit available after portable import',
        all(fresh.get_bytes(artifacts[k])==store.get_bytes(artifacts[k]) for k in ['source','body_mask','arm_mask','track_audit']))
    return artifacts,{'fixture':artifacts['fixture'],'frames':3,'fps':10,'golden_rgba_sha256':[digest(a.tobytes()) for a in goldens]},export


def _f09(store,output,checks):
    artifacts,_=_owned_body(store,checks,canvas=64,frames=8,fps=12)
    recipe={'canvas':{'w':64,'h':64},'frames':8,'fps':12,'seed':123,'origin':[32,40],
        'ramps':{'main':['#160f28','#443264','#8860a8','#d8a0c8','#fff0e8']},
        'outline':{'mode':'none'},'layers':[{'id':'extra','type':'arc','radius':16,'sweep':220,'profile':'slash'}]}
    body_export=export_sequence(store,artifacts['sequence'],output/'body-only',formats=['png','manifest','editable','review'])
    _check(checks,'body-only inspection/export remains separate from effects-on output',
        all(v['status']=='written' for v in body_export['formats'].values()))
    effect=render_effect(store,recipe)
    _,fx=load_sequence(store,effect['sequence'])
    _check(checks,'pinned arc retained full RGBA goldens',[digest(a.tobytes()) for a in fx]==list(ARC_HASHES),ARC_AUTHORITY)
    unknown=copy.deepcopy(recipe)
    unknown['layers'][0]['type']='private-neural-magic'
    try:
        render_effect(store,unknown)
    except ValidationError as error:
        message=str(error)
        _check(checks,'unknown private effect family rejected',
            'private-neural-magic' in message and 'unknown' in message.lower()
            and 'ramps must' not in message.lower(),message)
    else:
        _check(checks,'unknown private effect family rejected',False,'Expected unknown family rejection')
    body=artifacts['sequence']; composed=compose_sequences(store,body,back=effect['streams']['back'],front=effect['streams']['front'])
    _,body_frames=load_sequence(store,body);doc,actual=load_sequence(store,composed['sequence'])
    # Retained arc has empty front and no overlap with marker at the top-left.
    expected=[]
    for b,f in zip(body_frames,fx):
        a=f.copy();a[b[...,3]==255]=b[b[...,3]==255];expected.append(a)
    _check(checks,'shared exact composition clock and independently enumerated marker pixels',
        len(actual)==8 and all(f['duration']==[1,12] for f in doc['frames'])
        and all(np.array_equal(a,b) for a,b in zip(actual,expected)))
    edited=edit_sequence(store,composed['sequence'],[{'operation':'patch_pixels','frames':[1],
        'reason':'Fine edit after body+FX composition','pixels':[[1,1,'#ffff00ff','#ff00ffff']]}])
    expected[0][1,1]=[255,0,255,255]
    _,edited_frames=load_sequence(store,edited['sequence'])
    _check(checks,'post-composition fine edit preserves every other pixel/frame',
        all(np.array_equal(a,b) for a,b in zip(edited_frames,expected)))
    artifacts.update({'body_sequence':body,'sequence':edited['sequence'],'composed_sequence':composed['sequence'],
        'effect_sequence':effect['sequence'],'effect_back':effect['streams']['back'],
        'effect_front':effect['streams']['front'],'effect_recipe':effect['recipe'],'revision':edited['revision']})
    export,fresh=_exchange(store,artifacts['sequence'],output,checks,formats=['png','sheet','manifest','apng','editable','review'])
    reproduced=compose_sequences(fresh,body,back=artifacts['effect_back'],front=artifacts['effect_front'])
    _check(checks,'fresh Store body/effect source composition reproducible',reproduced['sequence']==artifacts['composed_sequence'])
    export['body_only']=body_export
    return artifacts,{'fixture':artifacts['fixture'],'recipe':recipe,'retained_authority':ARC_AUTHORITY},export


_ENGINE_SCRIPT = r'''extends SceneTree
var errors: Array = []
var events: Array = []
var finished: Array = []
var pixels: Array = []
var started: int
var phase: String = "play"
func check(ok: bool, label: String) -> void:
    if not ok: errors.append(label)
func sha(data: PackedByteArray) -> String:
    var hash: HashingContext = HashingContext.new()
    hash.start(HashingContext.HASH_SHA256)
    hash.update(data)
    return hash.finish().hex_encode()
func _initialize() -> void:
    call_deferred("verify")
func verify() -> void:
    var t: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://timeline.json"))
    var original: SpriteFrames = load("res://clip.tres")
    check(ResourceSaver.save(original, "res://reloaded.tres") == OK, "resource save")
    var frames: SpriteFrames = ResourceLoader.load("res://reloaded.tres", "SpriteFrames", ResourceLoader.CACHE_MODE_IGNORE)
    check(frames.get_frame_count(&"clip") == t.frames.size(), "ordered frame count")
    check(frames.get_animation_loop(&"clip") == t.loop, "loop flag")
    check(is_equal_approx(frames.get_animation_speed(&"clip"),1.0), "seconds speed1")
    for i in t.frames.size():
        var texture: AtlasTexture = frames.get_frame_texture(&"clip",i)
        var r: Array = t.frames[i].rectangle
        check(texture.region == Rect2(r[0],r[1],r[2],r[3]), "rectangle " + str(i))
        var image: Image = texture.get_image()
        image.convert(Image.FORMAT_RGBA8)
        var actual: String = sha(image.get_data())
        check(actual == t.frames[i].rgba_sha256, "full RGBA " + str(i))
        var d: Array = t.frames[i].duration
        check(abs(frames.get_frame_duration(&"clip",i)-float(d[0])/d[1]) < 0.0000001, "hold " + str(i))
        pixels.append({"frame":i,"rgba_sha256":actual})
    var packed: PackedScene = load("res://clip.tscn")
    var scene: Node2D = packed.instantiate()
    var sprite: AnimatedSprite2D = scene.get_node("AnimatedSprite2D")
    sprite.frame_changed.connect(func(): events.append({"phase":phase,"frame":sprite.frame,"seconds":float(Time.get_ticks_usec()-started)/1000000.0}))
    sprite.animation_finished.connect(func(): finished.append(float(Time.get_ticks_usec()-started)/1000000.0))
    # Resource loading may consume a large first process delta. Settle the engine
    # before starting this measured scene; do not loosen wall-clock tolerances.
    await create_timer(0.1).timeout
    for tick in 3:
        await process_frame
    started=Time.get_ticks_usec()
    root.add_child(scene)
    var total: float = float(t.total[0])/t.total[1]
    var count: int = int(t.play_count)
    await create_timer(total*(count if count>0 else 1)+0.08).timeout
    check(events.size()>=2 and events[0].frame==1 and events[1].frame==2, "forward order")
    if events.size()>=2:
        var d0: Array = t.frames[0].duration
        var d1: Array = t.frames[1].duration
        check(abs(events[0].seconds-float(d0[0])/d0[1])<0.04, "first hold within40ms")
        check(abs(events[1].seconds-float(d0[0])/d0[1]-float(d1[0])/d1[1])<0.04, "second hold within40ms")
    if count==0:
        check(sprite.is_playing() and finished.is_empty(), "infinite continues without finish")
        var returned: bool = false
        for event in events:
            if event.frame==0: returned=true
        check(returned, "infinite return seam")
    else:
        check(finished.size()==count, "exact completion count")
        check(sprite.frame==t.frames.size()-1 and not sprite.is_playing(), "held final pose")
        for i in finished.size():
            check(abs(finished[i]-total*(i+1))<0.04*(i+1), "bounded completion " + str(i))
        var pivot: Array = t.frames[-1].pivot
        check(sprite.offset == -Vector2(pivot[0],pivot[1]), "held pivot")
        await create_timer(0.05).timeout
        check(sprite.frame==t.frames.size()-1 and not sprite.is_playing(), "additional final hold")
        phase="restart"
        scene.restart()
        check(sprite.frame==0 and sprite.is_playing(), "restart resets")
    var file: FileAccess = FileAccess.open("res://engine-receipt.json",FileAccess.WRITE)
    file.store_string(JSON.stringify({"errors":errors,"engine":Engine.get_version_info(),"events":events,"completion":finished,"pixels":pixels,"play_count":count,"clock_tolerance_ms":40,"startup":"100ms + 3 process frames before scene starts","scope":"headless texture readback and actual AnimatedSprite2D; no GPU/visual acceptance"},"  "))
    quit(0 if errors.is_empty() else 2)
'''


def _engine(project, executable):
    (project/'verify.gd').write_text(_ENGINE_SCRIPT)
    commands = [[executable,'--headless','--path',str(project),'--editor','--import'],
                [executable,'--headless','--path',str(project),'--script','verify.gd','--max-fps','240']]
    outputs=[]
    try:
        for command in commands:
            run=subprocess.run(command,capture_output=True,text=True,timeout=40)
            outputs.append({'command':command,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
            if run.returncode: break
    except (OSError,subprocess.TimeoutExpired) as error:
        outputs.append({'error':type(error).__name__,'reason':str(error)})
    (project/'commands.json').write_bytes(canonical_json(outputs))
    receipt=project/'engine-receipt.json'
    if not receipt.exists():
        return {'status':'failed','commands':str(project/'commands.json'),'reason':'No engine receipt produced'}
    data=json.loads(receipt.read_text())
    return {'status':'verified' if len(outputs)==2 and all(x.get('returncode')==0 for x in outputs) and not data['errors'] else 'failed',
            'receipt':str(receipt),'receipt_sha256':digest(receipt.read_bytes()),'measurement':data,
            'script_sha256':digest(_ENGINE_SCRIPT.encode()),'commands':str(project/'commands.json')}


def _f10(store,output,checks):
    a=np.zeros((16,16,4),np.uint8)
    a[1,1]=[255,0,0,255];a[2,3]=[0,255,0,255];a[3,4]=[11,22,33,0]
    b=a.copy();b[1,1]=[0,0,255,255]
    arrays=[a,b,b.copy()];durations=[Fraction(7,100),Fraction(13,100),Fraction(1,20)]
    sequence=save_sequence(store,arrays,durations=durations,pivots=[[1,3],[2,3],[2,3]],
        directions=['diagnostic-south']*3,play_count=2)
    artifacts={'sequence':sequence,'fixture':store.put_json({'kind':'replay-input','version':1,
        'rasters':[store.put_raster(a) for a in arrays],'durations':[[7,100],[13,100],[1,20]],'play_count':2})}
    export,_=_exchange(store,sequence,output,checks,formats=['png','sheet','manifest','apng','gif','editable','godot','review'])
    manifest=json.loads((output/'export/manifest.json').read_text())
    sheet=np.array(Image.open(output/'export/sheet.png').convert('RGBA'))
    _check(checks,'PNG and sheet rectangles preserve full RGBA including hidden colors',
        all(np.array_equal(np.array(Image.open(output/'export'/f['file']).convert('RGBA')),a)
            and np.array_equal(sheet[f['rectangle'][1]:f['rectangle'][1]+16,f['rectangle'][0]:f['rectangle'][0]+16],a)
            for a,f in zip(arrays,manifest['frames'])))
    _check(checks,'unequal rational holds, duplicate order, explicit finite plays',
        [f['duration'] for f in manifest['frames']]==[[7,100],[13,100],[1,20]]
        and manifest['play_count']==2 and manifest['play_total']==[1,2]
        and manifest['frames'][1]['rgba_sha256']==manifest['frames'][2]['rgba_sha256'])
    with Image.open(output/'export/animation.apng') as apng,Image.open(output/'export/animation.gif') as gif:
        okay=apng.n_frames==gif.n_frames==3 and apng.info['loop']==2 and gif.info['loop']==1
        for i,a in enumerate(arrays):
            apng.seek(i);gif.seek(i);g=np.array(gif.convert('RGBA'))
            okay=okay and np.array_equal(np.array(apng.convert('RGBA')),a) and np.array_equal(g[...,3],a[...,3])
            okay=okay and np.array_equal(g[a[...,3]>0],a[a[...,3]>0]) and round(apng.info['duration'])==gif.info['duration']==[70,130,50][i]
        _check(checks,'APNG exact RGBA and GIF visible/alpha/hold/total-play contract',okay,
            'GIF hidden RGB is not preserved; APNG is full RGBA')
    unsupported=save_sequence(store,[np.array([[[1,2,3,128]]],np.uint8)],durations=[Fraction(1,100000)])
    negative=export_sequence(store,unsupported,output/'unsupported',formats=['gif','apng'])
    _check(checks,'unrepresentable APNG hold and partial-alpha GIF explicitly unsupported',
        negative['formats']['apng']['status']==negative['formats']['gif']['status']=='unsupported')
    before=(output/'export/manifest.json').read_bytes()
    _rejected(checks,'existing export directory preserved',lambda:export_sequence(store,sequence,output/'export'))
    _check(checks,'prior export identity unchanged after rejected overwrite',before==(output/'export/manifest.json').read_bytes())
    executable=shutil.which('godot') or shutil.which('godot4')
    engine={'status':'unsupported','reason':'Godot executable unavailable; no engine pass claimed'}
    if executable:
        cases={}
        for count in (2,1,0):
            if count==2: project=output/'export/godot'
            else:
                variant=save_sequence(store,arrays,durations=durations,pivots=[[1,3],[2,3],[2,3]],
                    directions=['diagnostic-south']*3,loop=count==0,play_count=count)
                artifacts['sequence_plays_'+str(count)]=variant
                export_sequence(store,variant,output/('engine-plays-'+str(count)),formats=['godot','manifest'])
                project=output/('engine-plays-'+str(count))/'godot'
            cases[str(count)]=_engine(project,executable)
        engine={'status':'verified' if all(c['status']=='verified' for c in cases.values()) else 'failed','cases':cases}
    _check(checks,'actual Godot import/reload/RGBA/clocks/once/finite/loop/held-pose',engine['status']=='verified',engine)
    export['engine_verification']=engine
    return artifacts,{'fixture':artifacts['fixture'],'durations':[[7,100],[13,100],[1,20]],'play_count':2,
        'clock_tolerance_ms':40,'engine_cases':[1,2,0],'engine_clock_scope':'measured scene starts after resource checks and100ms+3processframe warmup'},export


def run_flow(flow_id: str, store: Store, output: Path) -> dict:
    """Execute one real local diagnostic. Never overwrite an existing output.

    A completed diagnostic is not the full original F-family comparison or art
    acceptance. Unavailable Godot is explicit partial/unsupported, not a pass.
    """
    if flow_id not in FLOW_IDS:
        raise ValidationError('Unknown replay geometry flow: '+str(flow_id))
    output=Path(output).absolute()
    if output.is_symlink() or output.exists():
        raise ValidationError('Replay output must be fresh; existing output preserved')
    output.mkdir(parents=True)
    output=output.resolve()
    checks=[]
    artifacts,inputs,export={'F02':_f02,'F09':_f09,'F10':_f10}[flow_id](store,output,checks)
    unavailable = flow_id=='F10' and export['engine_verification']['status']=='unsupported'
    engine_check = 'actual Godot import/reload/RGBA/clocks/once/finite/loop/held-pose'
    failed=any(not c['passed'] for c in checks if not (unavailable and c['name']==engine_check))
    status='failed' if failed else 'partial' if unavailable else 'completed'
    receipt={'version':1,'flow_id':flow_id,'status':status,'artifacts':artifacts,'checks':checks,
        'inputs':inputs,'limitations':list(LIMITATIONS),'exports':export,
        'reviews':{'html':str(output/'export/review/review.html'),'json':str(output/'export/review/review.json'),
            'continuous_motion_viewed':False},'output':str(output),'provider_calls':0,'artistic_acceptance':'unreviewed'}
    receipt['routine_order']={
        'F02':['supplied pixels and disjoint ownership masks','parented scene and anchored hold tracks',
               'independent destination oracle','overlap/frozen-source negative controls',
               'guarded one-based fine edit','editable export and fresh Store reconstruction'],
        'F09':['owned body sequence','body-only export','pinned procedural arc render','retained eight-frame hash oracle',
               'rational back/body/front composition','fine edit',
               'editable export and fresh Store reconstruction'],
        'F10':['supplied unequal-clock sequence','PNG/sheet/APNG/GIF/editable/Godot/review export',
               'fresh Store reload','exact decode and rational clock checks','unsupported format controls',
               'overwrite preservation control','Godot availability check; if available, warmed finite/once/infinite engine checks'],
    }[flow_id]
    if flow_id=='F09':
        receipt['reviews']['body_only_html']=str(output/'body-only/review/review.html')
        receipt['reviews']['body_only_json']=str(output/'body-only/review/review.json')
    receipt['receipt_artifact']=store.put_json(receipt)
    (output/'replay-receipt.json').write_bytes(canonical_json(receipt))
    return receipt

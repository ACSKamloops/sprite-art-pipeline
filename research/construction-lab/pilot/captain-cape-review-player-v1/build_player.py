"""Build an offline, synchronized PNG audition without changing source assets."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


TEMPLATE = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Captain cape motion comparison</title>
<style>
body{background:#202328;color:#edf0f4;font:16px system-ui;margin:24px}h1{font-size:23px}
button,select{font:inherit;padding:7px;margin:3px;background:#343b44;color:white;border:1px solid #7c8795;border-radius:4px}
button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #eac368}
.views{display:flex;gap:16px;overflow:auto}.view{flex:none}h2{font-size:18px}
canvas{width:384px;height:384px;image-rendering:pixelated;background:#292c30}
#seek{width:min(680px,85vw)}#status{font-variant-numeric:tabular-nums}a{color:#b5d6ff}
</style>
<h1>Captain cape motion comparison</h1>
<p>Experimental art. Native 384-pixel renders; one three-quarter walk. This comparison does not establish 9/10 quality.</p>
<p id="description"></p>
<div><button id="play">Play</button><button id="pause">Pause</button><button id="previous">Previous frame</button><button id="next">Next frame</button><button id="replay">Restart</button>
<label>Speed <select id="speed"><option value="1">Normal</option><option value="0.5">Half</option></select></label>
<label>Display <select id="zoom"><option value="1">Native 1×</option><option value="2">Nearest 2×</option></select></label></div>
<p><label>Frame <input id="seek" type="range" min="0" max="64" value="0"></label></p>
<p id="status" role="status">Loading original frames…</p><div class="views" id="views"></div>
<p>Space pauses or resumes; arrow keys step. Both variants use the same source frame and clock. The 65-pose loop lasts exactly 65/60 seconds. Restart repeats the first exported pose; it does not claim the source endpoint is pixel-identical.</p>
<p><a href="manifest.json">Source hashes and scope</a> · <a href="README.txt">Review notes</a></p>
<script>
'use strict';
const manifest=__MANIFEST__, $=id=>document.getElementById(id);
const state={ready:false,playing:false,clock:0,speed:1,frame:0,errors:[]};
const variants=manifest.variants.map(v=>{
 const box=document.createElement('section');box.className='view';
 const title=document.createElement('h2');title.textContent=v.label;
 const canvas=document.createElement('canvas');canvas.width=canvas.height=384;canvas.id=v.id;
 box.append(title,canvas);$('views').append(box);return {...v,canvas,images:[]};
});
$('description').textContent=manifest.description;
function draw(){
 if(!state.ready)return;
 state.frame=((Math.floor(state.clock+1e-9)%65)+65)%65;
 for(const v of variants){const c=v.canvas.getContext('2d');c.imageSmoothingEnabled=false;
  for(let y=0;y<384;y+=16)for(let x=0;x<384;x+=16){c.fillStyle=((x+y)/16)%2?'rgb(55,58,62)':'rgb(40,43,47)';c.fillRect(x,y,16,16);}
  c.drawImage(v.images[state.frame],0,0);
 }
 $('seek').value=state.frame;$('status').textContent=`Frame ${state.frame+1}/65 · source ${2*state.frame+1} · ${state.playing?'playing':'paused'} · ${state.speed}×`;
}
function seek(n){state.playing=false;state.clock=((n%65)+65)%65;draw();}
function advance(seconds){if(!Number.isFinite(seconds)||seconds<0)throw Error('Invalid elapsed time');if(state.ready&&state.playing){state.clock+=seconds*60*state.speed;draw();}}
$('play').onclick=()=>{if(state.ready){state.playing=true;draw();}};
$('pause').onclick=()=>{state.playing=false;draw();};
$('previous').onclick=()=>seek(state.frame-1);$('next').onclick=()=>seek(state.frame+1);
$('replay').onclick=()=>{seek(0);state.playing=state.ready;draw();};
$('seek').oninput=()=>seek(Number($('seek').value));
$('speed').onchange=()=>{state.speed=Number($('speed').value);draw();};
$('zoom').onchange=()=>{for(const v of variants){v.canvas.style.width=v.canvas.style.height=`${384*Number($('zoom').value)}px`;}};
document.addEventListener('keydown',e=>{if(e.target.matches('input,select'))return;
 if(e.code==='Space'){e.preventDefault();if(state.ready){state.playing=!state.playing;draw();}}
 if(e.code==='ArrowRight'){e.preventDefault();seek(state.frame+1);}if(e.code==='ArrowLeft'){e.preventDefault();seek(state.frame-1);}
});
let previous=null;function tick(now){const seconds=previous===null?0:Math.max(0,(now-previous)/1000);previous=now;if(!document.hidden)advance(seconds);requestAnimationFrame(tick);}requestAnimationFrame(tick);
document.addEventListener('visibilitychange',()=>{previous=null;});
window.CapeReview={state,manifest,variants,draw,seek,advance};
Promise.all(variants.map(async v=>{v.images=await Promise.all(v.frames.map(f=>new Promise((resolve,reject)=>{
 const img=new Image();img.onload=()=>{if(img.naturalWidth!==384||img.naturalHeight!==384)return reject(Error('Changed canvas: '+f.file));resolve(img);};img.onerror=()=>reject(Error('Missing frame: '+f.file));img.src=f.file;
})));})).then(()=>{state.ready=true;draw();}).catch(e=>{state.errors.push(String(e));state.playing=false;$('status').textContent=String(e);});
</script></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audition', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--candidate', default='followthrough')
    parser.add_argument('--candidate-label', default='Uniform hem lag — experimental')
    parser.add_argument('--description', default='Crease baseline versus uniform hem lag. This experiment shifts a broad panel; reviewers are testing whether it convincingly reads as fabric.')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Preserve existing review copies')
    assert args.candidate and args.candidate.isascii() and all(c.isalnum() or c=='-' for c in args.candidate)
    receipt = args.audition / 'sha256-receipt.json'
    manifest = {
        'state': 'LOCAL_VISUAL_AUDITION_ART_UNAPPROVED',
        'source_receipt_sha256': hashlib.sha256(receipt.read_bytes()).hexdigest(),
        'native': 384, 'poses': 65, 'fps': 60, 'cycle_seconds_fraction': [65, 60],
        'description': args.description,
        'variants': [],
        'limits': ['Both variants rendered with CUDA; not authoritative CPU reopen receipts',
                   'In-place visual review only; not a fresh Godot or world-contact check'],
    }
    # Verify immutable producer receipt before copying any output.
    root = args.audition.parents[1]
    data = json.loads(receipt.read_text())
    if 'assets' in data:
        frozen = {relative: row['sha256'] for relative, row in data['assets'].items()}
    elif 'frozen_files_excluding_this_manifest' in data:
        frozen = data['frozen_files_excluding_this_manifest']
    else:
        raise ValueError('Unknown frozen receipt schema')
    assert frozen, 'Empty producer receipt'
    for relative, digest in frozen.items():
        path = (root / relative).resolve()
        assert path.is_relative_to(root.resolve()), relative
        assert isinstance(digest, str) and len(digest) == 64, relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, relative
    for name in ['baseline', args.candidate]:
        for i in range(65):
            source = args.audition / name / f'frame-{i:03}.png'
            relative = str(source.relative_to(root))
            assert relative in frozen, 'Source frame missing from producer receipt: ' + relative
            with Image.open(source) as image:
                assert image.size == (384, 384)
    args.output.mkdir(parents=True)
    for name, label in [('baseline', 'Crease baseline'), (args.candidate, args.candidate_label)]:
        destination = args.output / name
        destination.mkdir()
        rows = []
        for i in range(65):
            source = args.audition / name / f'frame-{i:03}.png'
            with Image.open(source) as image:
                assert image.size == (384, 384)
            target = destination / source.name
            shutil.copyfile(source, target)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            assert hashlib.sha256(target.read_bytes()).hexdigest() == digest
            rows.append({'index': i, 'source_frame': 2*i+1,
                         'file': f'{name}/{source.name}', 'sha256': digest})
        manifest['variants'].append({'id': name, 'label': label, 'frames': rows})
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    embedded = json.dumps(manifest).replace('<', r'\u003c')
    (args.output / 'start-here.html').write_text(TEMPLATE.replace('__MANIFEST__', embedded))
    (args.output / 'README.txt').write_text(
        'Open start-here.html. Original RGBA PNGs are copied byte-exact; no server or credentials required.\n'
        'Native 1x or nearest 2x, normal/half speed, pause, stepping and synchronized variants.\n'
        'The candidate remains an experiment, not approved finished art.\n'
        'This folder contains one walk view, not a complete action/direction library.\n')
    print(json.dumps({'output': str(args.output), 'copied_source_frames': 130,
                      'source_receipt_sha256': manifest['source_receipt_sha256']}))


if __name__ == '__main__':
    main()

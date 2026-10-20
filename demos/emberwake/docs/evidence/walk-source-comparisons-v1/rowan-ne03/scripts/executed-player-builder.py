#!/usr/bin/env python3
"""Build a local PNG-authority walk player from a frozen pair-review packet."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
from fractions import Fraction
from math import lcm
from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mp4', action='store_true')
    args = parser.parse_args()
    source = args.packet.resolve()
    spec = json.loads((source / 'INPUTS.json').read_text())
    assert not args.out.exists(), 'Fresh output directory required'
    assert spec['stage'] == [128, 128]
    assert spec['duration'] == [9, 20]
    timings = {label: [Fraction(*pair) for pair in
                      spec.get('variant_holds', {}).get(label, spec['holds'])]
               for label in spec['variants']}
    view_names = list(spec['variants']['A'])
    assert view_names, 'Supply at least one declared view'
    assert all(set(views) == set(view_names) for views in spec['variants'].values()), 'All variants must cover the same views'
    primary_view = view_names[0]
    for holds in timings.values():
        assert all(hold > 0 for hold in holds) and sum(holds) == Fraction(9, 20)
    records = []
    for label, views in spec['variants'].items():
        for view, frames in views.items():
            assert len(frames) == len(timings[label])
            for entry in frames:
                path = (source / entry['path']).resolve()
                assert path.is_relative_to(source)
                assert sha(path) == entry['sha256'], path
                with Image.open(path) as image:
                    assert image.size == (128, 128) and image.mode == 'RGBA'
                records.append(entry)
    args.out.mkdir(parents=True)
    for entry in records:
        target = args.out / entry['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / entry['path'], target)
    (args.out / 'INPUTS.json').write_text(json.dumps(spec, indent=2) + '\n')
    receipt = {'packet_sha256': sha(source / 'INPUTS.json'),
               'image_hashes_verified': len(records),
               'primary_view': primary_view,
               'clock': {'loop': [9, 20], 'variant_holds': {
                   label: [[hold.numerator, hold.denominator] for hold in holds]
                   for label, holds in timings.items()}},
               'rendering': 'Direct PNG Canvas2D, nearest sampling. Game size is an84px proxy, not Godot rendering.',
               'art_acceptance': 'Unselected comparison. No continuous human playback approval implied.'}
    if args.mp4:
        # Encode rational holds without thousands of temporary PNGs.
        images = {label: [Image.open(source / e['path']).convert('RGBA')
                          for e in spec['variants'][label][primary_view]]
                  for label in ['A', 'B']}
        clock_hz = lcm(*(hold.denominator for holds in timings.values() for hold in holds))
        assert clock_hz <= 1920, 'Unexpectedly dense preview clock'
        loop_ticks = int(Fraction(9, 20) * clock_hz)
        phase_ticks = {}
        for label in ['A', 'B']:
            phase_ticks[label] = [phase for phase, hold in enumerate(timings[label])
                                  for _ in range(int(hold * clock_hz))]
            assert len(phase_ticks[label]) == loop_ticks
        buffers = {}
        for phases in sorted(set(zip(phase_ticks['A'], phase_ticks['B']))):
            frame = Image.new('RGB', (880, 320), '#1f252d')
            draw = ImageDraw.Draw(frame)
            for n, label in enumerate(['A', 'B']):
                phase = phases[n]
                x = n * 440
                draw.text((x + 12, 12), f'{label} / {primary_view} full walk / .45s', fill='white')
                large = images[label][phase].resize((256, 256), Image.Resampling.NEAREST)
                small = images[label][phase].resize((84, 84), Image.Resampling.NEAREST)
                frame.paste(large, (x + 2, 36), large)
                frame.paste(small, (x + 290, 191), small)
                draw.text((x + 290, 285), f'cel{phase:02} / game proxy', fill='white')
            buffers[phases] = frame.tobytes()
        video = args.out / 'comparison.mp4'
        command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                   '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size',
                   '880x320', '-framerate', str(clock_hz), '-i', '-', '-an',
                   '-c:v', 'libx264', '-threads', '4', '-preset', 'veryfast',
                   '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video)]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        try:
            for tick in range(loop_ticks * 8):
                t = tick % loop_ticks
                process.stdin.write(buffers[phase_ticks['A'][t], phase_ticks['B'][t]])
        finally:
            process.stdin.close()
        assert process.wait() == 0
        probe = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
            '-show_entries', 'stream=nb_read_frames,r_frame_rate,duration',
            '-of', 'json', str(video)], text=True))
        stream = probe['streams'][0]
        assert stream['nb_read_frames'] == str(loop_ticks * 8)
        assert stream['r_frame_rate'] == f'{clock_hz}/1'
        assert stream['duration'] == '3.600000'
        receipt['mp4'] = {'sha256': sha(video), 'probe': probe,
                          'clock_hz': clock_hz, 'loop_ticks': loop_ticks,
                          'note': 'Lossy playback aid; PNGs remain pixel authority.'}
    (args.out / 'PLAYER-RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    html = '''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Emberwake · complete walk comparison</title><link rel="icon" href="data:,">
<style>body{background:#141a22;color:#edf0f4;font:16px system-ui;max-width:1040px;margin:32px auto;padding:0 20px}
h1{font-size:25px}p{color:#b7c2d0;line-height:1.5}button,select{font:inherit;padding:8px;margin:4px;border:1px solid #576579;border-radius:6px;background:#263245;color:white}
.panels{display:flex;gap:20px;flex-wrap:wrap}.panel{background:#202732;border-radius:10px;padding:16px;min-width:280px;flex:1}canvas{image-rendering:pixelated;display:block;margin:auto}.proxy{margin-top:15px}video{width:100%;margin-top:20px}#state{font-variant-numeric:tabular-nums;color:#d8bc80}</style>
<h1>Complete walk comparison</h1><p>Same .45 second cycle. A is the comparison control; the right pane shows the trial. Compare the full loop, especially the leg exchanges and return to the first pose. This comparison does not establish final art approval.</p>
<button id="play">Pause</button><button id="step">Next pose</button><select id="variant" aria-label="Candidate variant"></select>
<select id="view"></select><select id="speed"><option value="1">Normal speed</option><option value=".5">Half speed</option><option value=".25">Quarter speed</option></select>
<select id="bg"><option value="#202732">Dark ground</option><option value="#e1ded1">Light ground</option><option value="#60705a">Green ground</option></select>
<span id="state">Loading…</span><div class="panels"><div class="panel"><b>A · control</b><canvas id="a" width="256" height="256"></canvas><canvas class="proxy" id="as" width="84" height="84"></canvas></div><div class="panel"><b id="candidateLabel">B · candidate</b><canvas id="b" width="256" height="256"></canvas><canvas class="proxy" id="bs" width="84" height="84"></canvas></div></div>
<p>Large: nearest2×. Small:84px game-size proxy. Pause and step to inspect individual poses. This page does not test Godot rendering or physical foot contact.</p>
VIDEO
<script>
const spec=SPEC, banks={}, view=document.querySelector('#view'), variant=document.querySelector('#variant'), state=document.querySelector('#state');
const holds=Object.fromEntries(Object.keys(spec.variants).map(label=>[label,(spec.variant_holds?.[label]||spec.holds).map(([n,d])=>n/d)]));
let playing=true, clock=0, last=null, ready=false;
function phaseAt(label){let end=0;for(let i=0;i<holds[label].length;i++){end+=holds[label][i];if(clock<end-1e-10)return i}return 0}
function seekPhase(n){playing=false;last=null;const h=holds[variant.value],i=((n%h.length)+h.length)%h.length;clock=h.slice(0,i).reduce((a,b)=>a+b,0);document.querySelector('#play').textContent='Play';paint()}
for(const name of Object.keys(spec.variants.A)){const o=document.createElement('option');o.value=name;o.textContent=name;view.append(o)}
for(const name of Object.keys(spec.variants).filter(name=>name!=='A')){const o=document.createElement('option');o.value=name;o.textContent=`Candidate ${name}`;variant.append(o)}
function paint(){if(!ready)return;for(const[label,ids]of [['A',['a','as']],[variant.value,['b','bs']]])for(const id of ids){const c=document.getElementById(id),ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.fillStyle=document.querySelector('#bg').value;ctx.fillRect(0,0,c.width,c.height);ctx.drawImage(banks[label][view.value][phaseAt(label)],0,0,c.width,c.height)}state.textContent=`A:${String(phaseAt('A')).padStart(2,'0')} / ${variant.value}:${String(phaseAt(variant.value)).padStart(2,'0')} / ${playing?'playing':'paused'}`;}
document.querySelector('#play').onclick=()=>{playing=!playing;last=null;document.querySelector('#play').textContent=playing?'Pause':'Play';paint()};
document.querySelector('#step').onclick=()=>seekPhase(phaseAt(variant.value)+1);
view.onchange=paint;document.querySelector('#bg').onchange=paint;variant.onchange=()=>{document.querySelector('#candidateLabel').textContent=variant.value+' · candidate';paint()};
async function init(){const pending=[];for(const[label,views]of Object.entries(spec.variants)){banks[label]={};for(const[name,entries]of Object.entries(views)){banks[label][name]=[];for(const entry of entries){const image=new Image();banks[label][name].push(image);pending.push(new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(Error(entry.path));image.src=entry.path}))}}}await Promise.all(pending);ready=true;paint();}
function tick(now){if(ready&&playing){if(last!==null)clock=(clock+(now-last)/1000*Number(document.querySelector('#speed').value))%.45;paint()}last=now;requestAnimationFrame(tick)}
window.walkReview={get ready(){return ready},get phase(){return phaseAt('A')},get phases(){return Object.fromEntries(Object.keys(holds).map(label=>[label,phaseAt(label)]))},get clock(){return clock},setPhase:seekPhase,seekSeconds(seconds){playing=false;last=null;clock=((seconds%.45)+.45)%.45;paint()},play(){playing=true;last=null;document.querySelector('#play').textContent='Pause'},get phaseSeconds(){return holds.A[0]},get imageCount(){return Object.values(spec.variants).reduce((n,v)=>n+Object.values(v).reduce((s,f)=>s+f.length,0),0)}};
init().catch(error=>{state.textContent='Failed to load: '+error.message;throw error});requestAnimationFrame(tick);
</script>'''
    html = html.replace('SPEC', json.dumps(spec)).replace('VIDEO', '<p>The video below compares A and B.</p><video controls loop muted playsinline src="comparison.mp4"></video>' if args.mp4 else '')
    (args.out / 'index.html').write_text(html)
    print(f'Player: {args.out}; {len(records)} verified images; MP4: {args.mp4}')


if __name__ == '__main__':
    main()

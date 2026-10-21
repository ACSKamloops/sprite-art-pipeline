#!/usr/bin/env python3
"""Package retained comparisons and an anonymous review packet; no generation."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil

from PIL import Image, ImageDraw


PAGE = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sprite method comparison</title><link rel="icon" href="data:,"><style>
body{background:#171c26;color:#eef1f8;font:16px system-ui;margin:24px;max-width:1600px}p{max-width:1000px;line-height:1.5}button,select,input{font:inherit;margin:5px}a{color:#9fdcff}.controls{position:sticky;top:0;background:#171c26ef;padding:8px;z-index:2;border:1px solid #45546d}.grid{display:flex;flex-wrap:wrap;gap:14px;margin:20px 0}.card{background:#242e3e;padding:14px;border-radius:8px;width:max-content;max-width:100%}.stage{background:var(--matte,#7d7d7d);width:max-content}canvas,img{image-rendering:pixelated}canvas{display:block}.small{font-size:13px;max-width:280px}.pair{display:flex;gap:8px}.frames{display:flex;overflow-x:auto;gap:8px}.frames img{width:160px;height:160px;background:var(--matte,#7d7d7d)}h2{font-size:20px}.diag img{background:#7d7d7d}.still{padding:12px;background:var(--matte,#7d7d7d)}code{overflow-wrap:anywhere}
</style><style>.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}.card{width:auto;min-width:0}.small{max-width:none}h2{overflow-wrap:anywhere}@media(max-width:900px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:550px){.grid{grid-template-columns:1fr}}</style><h1>Sprite method comparison</h1>
<p id="brief">Same character, eight ordered poses, exact125ms per pose and a one-second cycle. PixelEngine baselines retain their opaque source mattes. One shared clock drives all clips; no per-frame fitting, interpolation or duplicate removal. Art and motion need separate review.</p>
<div class="controls"><button id="play">Pause</button><button id="restart">Restart</button><button id="prev">Previous</button><button id="next">Next</button>
<label>Scale <select id="scale"><option>1</option><option selected>2</option><option>4</option></select></label><label>Speed <select id="speed"><option value="1">Normal</option><option value="0.5">Half</option></select></label>
<label>Matte <select id="matte"><option value="#7d7d7d">Gray</option><option value="#eeeeee">Light</option><option value="#151922">Dark</option></select></label><input id="seek" type="range" min="0" max="7" step="1" value="0"><output id="status">Loading</output></div>
<div id="players" class="grid"></div><h2>Previous and current pose</h2><p>Pause or step to inspect every adjacent pair, including7→0.</p><div id="pairs" class="grid"></div>
<h2>Complete chronology</h2><div id="chronology"></div><div id="extras">EXTRAS</div>
<script id="data" type="application/json">DATA</script><script>
const data=JSON.parse(document.getElementById('data').textContent),rows=data.clips;
const $=id=>document.getElementById(id);let playing=false,elapsed=0,epoch=0,speed=1,current=0,draws=0,ready=false;
const cards=rows.map(row=>{const card=document.createElement('section');card.className='card';const h=document.createElement('h2');h.textContent=row.title;card.append(h);const stage=document.createElement('div');stage.className='stage';const c=document.createElement('canvas');c.width=80;c.height=80;stage.append(c);card.append(stage);const p=document.createElement('p');p.className='small';p.textContent=row.note;card.append(p);const a=document.createElement('a');a.href=row.apng;a.textContent='Exact APNG';card.append(a);const a2=document.createElement('a');a2.href=row.manifest;a2.textContent=' · Manifest';card.append(a2);$('players').append(card);
const pair=document.createElement('section');pair.className='card';const ph=document.createElement('h2');ph.textContent=row.title;pair.append(ph);const box=document.createElement('div');box.className='pair';const pcs=[0,1].map(()=>{const pc=document.createElement('canvas');pc.width=80;pc.height=80;pc.style.background='var(--matte,#7d7d7d)';box.append(pc);return pc});pair.append(box);$('pairs').append(pair);
const wrap=document.createElement('section');const ch=document.createElement('h2');ch.textContent=row.title;wrap.append(ch);const strip=document.createElement('div');strip.className='frames';for(const f of row.frames){const im=document.createElement('img');im.src=f.file;im.alt='Ordered source pose';strip.append(im)}wrap.append(strip);$('chronology').append(wrap);return {row,c,pcs,images:[]};});
function time(){return playing?elapsed+(performance.now()-epoch)/1000*speed:elapsed}
function draw(t){const phase=((t%1)+1)%1;current=Math.min(7,Math.floor((phase+1e-10)*8)%8);const scale=Number($('scale').value);for(const card of cards){for(const [canvas,index] of [[card.c,current],[card.pcs[0],(current+7)%8],[card.pcs[1],current]]){canvas.style.width=(80*scale)+'px';canvas.style.height=(80*scale)+'px';const ctx=canvas.getContext('2d');ctx.clearRect(0,0,80,80);if(card.images[index])ctx.drawImage(card.images[index],0,0)}}$('seek').value=current;$('status').textContent=`Frame${current} · ${(phase*1000).toFixed(0)}ms /1000ms · ${playing?'playing':'paused'}`;$('play').textContent=playing?'Pause':'Play';window.reviewState={ready,playing,current,time:t,speed,draws:++draws,cycles:Math.floor(t)}}
function tick(){if(ready)draw(time());requestAnimationFrame(tick)}
function pause(){elapsed=time();playing=false;draw(elapsed)}
$('play').onclick=()=>{if(!ready)return;if(playing)pause();else{epoch=performance.now();playing=true;draw(elapsed)}};
$('restart').onclick=()=>{elapsed=0;epoch=performance.now();draw(0)};
function step(delta){pause();current=(current+delta+8)%8;elapsed=current/8;draw(elapsed)}
$('prev').onclick=()=>step(-1);$('next').onclick=()=>step(1);$('seek').oninput=()=>{const f=Number($('seek').value);pause();elapsed=f/8;draw(elapsed)};
$('scale').onchange=()=>draw(time());$('matte').onchange=()=>document.documentElement.style.setProperty('--matte',$('matte').value);
$('speed').onchange=()=>{elapsed=time();epoch=performance.now();speed=Number($('speed').value);draw(elapsed)};
Promise.all(cards.map(async card=>{card.images=await Promise.all(card.row.frames.map(f=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(new Error(f.file));im.src=f.file})));})).then(()=>{ready=true;playing=true;epoch=performance.now();draw(0)}).catch(e=>{$('status').textContent='Image load failed:'+e.message});tick();
</script></html>'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def package(root, out, selection, anonymous):
    if out.exists() or out.is_symlink():
        raise ValueError('Fresh review directory required')
    out.mkdir(parents=True)
    (out / 'clips').mkdir()
    shutil.copy2(root / 'references/native-original.png', out / 'appearance-reference.png')
    clips, pins = [], []
    for letter, (run, clip_id, title, note) in selection.items():
        src = root / 'work' / run / 'clips' / clip_id
        dest = out / 'clips' / letter
        shutil.copytree(src, dest)
        doc = json.loads((dest / 'manifest.json').read_text())
        if doc['canvas'] != [80, 80] or [f['hold'] for f in doc['frames']] != [[1, 8]] * 8:
            raise ValueError('Unexpected comparison canvas or clock')
        # Anonymous packet contains only raster/timing evidence, no source provenance.
        if anonymous:
            for entry in list(dest.iterdir()):
                if entry.name not in {'frames', 'apng'}:
                    if entry.is_dir():
                        shutil.rmtree(entry)
                    else:
                        entry.unlink()
            # Encoder receipts contain producer file paths, outside the blind packet.
            (dest / 'apng/receipt.json').unlink()
            doc = {k: doc[k] for k in ['canvas', 'loop', 'duration', 'frames']}
            for frame in doc['frames']:
                frame.pop('source_frame_id', None)
            write(dest / 'manifest.json', doc)
        frame_records = []
        for f in doc['frames']:
            if sha(dest / f['file']) != f['sha256']:
                raise ValueError('Stale frame source')
            frame_records.append({'file': f'clips/{letter}/' + f['file'], 'hold': f['hold'], 'sha256': f['sha256']})
        clips.append({'id': letter, 'title': letter if anonymous else letter + ': ' + title,
                      'note': 'Eight poses at125ms; inspect all pairs and7→0.' if anonymous else note,
                      'frames': frame_records, 'manifest': f'clips/{letter}/manifest.json',
                      'apng': f'clips/{letter}/apng/animation.apng.png'})
        pins.append({'clip_id': letter, 'manifest_sha256': sha(dest / 'manifest.json'),
                     'apng_sha256': sha(dest / 'apng/animation.apng.png'), 'frames': frame_records})
    extras = ''
    if not anonymous:
        shutil.copytree(root / 'work/text-v2/stills', out / 'stills')
        extras = '<h2>Back-facing pose</h2><p>Source64px, ImageGen stage80px and PixelEngine stage88px are shown at native pixel size×2. The small WASM result is a retained failure.</p><div class="grid diag">'
        for name in ['source', 'north-pixelengine', 'north-imagegen-nearest', 'north-imagegen-palette', 'north-imagegen-pe']:
            image = Image.open(out / 'stills' / (name + '.png'))
            extras += f'<figure class="still"><figcaption>{html.escape(name)} · {image.width}×{image.height}</figcaption><img src="stills/{name}.png" width="{image.width*2}" height="{image.height*2}" alt="{name}"></figure>'
        extras += '</div>'
    payload = json.dumps({'clips': clips}, separators=(',', ':')).replace('<', '\\u003c')
    page = PAGE.replace('DATA', payload, 1).replace('EXTRAS', extras, 1)
    if anonymous:
        page = page.replace('PixelEngine baselines retain their opaque source mattes.', 'Some sources retain opaque gray mattes. The64px appearance reference is appearance-reference.png.')
    (out / 'index.html').write_text(page)
    ledger = {'schema': 'sprite-comparison-review/v1', 'clips': pins,
              'appearance_reference_sha256': sha(out / 'appearance-reference.png'),
              'scope': 'One right-facing eight-pose walk,1second, all eight adjacent/wrap pairs; no other actions/directions approved',
              'reviewer_limits': 'State whether actual continuous motion perception is available; chronology plus timestamps is not human normal-speed acceptance.'}
    fingerprint = hashlib.sha256(json.dumps(ledger, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    ledger['input_fingerprint'] = fingerprint
    write(out / 'INPUTS.json', ledger)
    # Anonymous montage labels only A..F, with every pose and no producer reports.
    montage = Image.new('RGB', (1280, len(clips) * 190), (125, 125, 125))
    draw = ImageDraw.Draw(montage)
    for row, clip in enumerate(clips):
        draw.text((4, row * 190 + 3), clip['id'], fill='white')
        for i, frame in enumerate(clip['frames']):
            image = Image.open(out / frame['file']).convert('RGBA').resize((160, 160), Image.Resampling.NEAREST)
            montage.paste(image, (i * 160, row * 190 + 22), image)
    montage.save(out / 'chronology.png')
    return {'path': str(out), 'input_fingerprint': fingerprint, 'clips': [c['id'] for c in clips]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--anonymous-output', type=Path, required=True)
    args = parser.parse_args()
    selected = {
        'A': ('text-v2', 'walk15', 'PixelEngine1.5 original', 'Original retained WebP frames; PNG conversion only.'),
        'B': ('text-v2', 'walk11', 'PixelEngine1.1 original', 'Original retained WebP frames; PNG conversion only.'),
        'C': ('text-v2', 'imagegen-shared-palette', 'ImageGen text + our pipeline', 'One fixed registration and original identity palette; source alpha retained.'),
        'D': ('guided-v1', 'imagegen-shared-palette', 'ImageGen pose guide + our pipeline', 'PixelEngine1.1 pose guide; ImageGen paint; existing palette and exact exports.'),
        'E': ('guided-v1', 'imagegen-pe-first', 'Guided ImageGen + PixelEngine first', 'Full-resolution genuine WASM shared frames, then fixed global affine; raw alpha.'),
        'F': ('guided-alpha8', 'imagegen-pe-first', 'Guided ImageGen + PixelEngine, alpha noise cleaned', 'Alpha1–7 removed and hidden RGB at alpha0 set to zero before WASM; same single global affine. RGBA at alpha8–255 unchanged.')}
    result = {'labelled': package(args.artifacts, args.output, selected, False),
              'anonymous': package(args.artifacts, args.anonymous_output, selected, True)}
    write(args.output / 'UNBLIND.json', selected)
    print(json.dumps(result))

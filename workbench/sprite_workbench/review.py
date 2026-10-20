"""Hash-bound diagnostics and all-frame review; never an artistic acceptance score."""
from __future__ import annotations

import html
import json
from pathlib import Path

import numpy as np

from .core import canonical_json, digest
from .export import output_directory, png_bytes, sequence_timeline, validated_sequence, playback_clock


def _difference(a,b):
    rgba = np.any(a != b,axis=2)
    visible = ((a[...,3] > 0)|(b[...,3] > 0)) & rgba
    alpha = a[...,3] != b[...,3]
    return {'rgba_changed_pixels':int(rgba.sum()),'visible_rgba_changed_pixels':int(visible.sum()),
            'alpha_changed_pixels':int(alpha.sum()),'hidden_rgb_only_changed_pixels':int((rgba & ~visible).sum()),
            'rgba_exact':not bool(rgba.any())}


def _write_review(store, ident, directory):
    doc,arrays = validated_sequence(store,ident); timeline = sequence_timeline(doc)
    clock = playback_clock(timeline,'review-clock')
    directory = Path(directory); directory.mkdir(exist_ok=True)
    (directory/'frames').mkdir()
    records = []
    for i,(a,meta) in enumerate(zip(arrays,timeline['frames'])):
        path = f'frames/frame-{i:04d}.png'; encoded = png_bytes(a); (directory/path).write_bytes(encoded)
        alpha = a[...,3]; ys,xs = np.nonzero(alpha)
        bounds = [int(xs.min()),int(ys.min()),int(xs.max()-xs.min()+1),int(ys.max()-ys.min()+1)] if len(xs) else None
        records.append(meta | {'file':path,'rgba_sha256':digest(a.tobytes()),'png_sha256':digest(encoded),
                               'visible_bounds':bounds,'visible_pixels':int((alpha>0).sum()),
                               'partial_alpha_pixels':int(((alpha>0)&(alpha<255)).sum()),
                               'hidden_rgb_nonzero_pixels':int(((alpha==0)&np.any(a[...,:3]!=0,axis=2)).sum()),
                               'visible_rgb_colors':len(np.unique(a[alpha>0,:3],axis=0))})
    pairs = [{'from':i,'to':i+1,'kind':'adjacent',**_difference(arrays[i],arrays[i+1])} for i in range(len(arrays)-1)]
    pairs.append({'from':len(arrays)-1,'to':0,'kind':'loop-seam' if doc['loop'] else 'replay-seam',
                  **_difference(arrays[-1],arrays[0])})
    report = {'sequence_id':ident,'canvas':doc['canvas'],'frames':records,'pairs':pairs,
              'total':timeline['total'],'loop':doc['loop'],'play_count':timeline['play_count'],
              'play_total':timeline['play_total'],'metadata':doc.get('metadata',{}),
              'playback_clock':clock,
              'diagnostic_coverage':{'ordered_frames':len(arrays),'adjacent_pairs':len(arrays)-1,
                                     'return_pairs':1,'continuous_motion_viewed':False},
              'visual_acceptance':'unreviewed','normal_speed_review':'Available in review.html; creation is not proof of viewing',
              'discipline':'No automatic art/motion score or anatomy/ground-contact inference'}
    (directory/'review.json').write_bytes(canonical_json(report))
    data = json.dumps(report,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    cards = ''.join(f'<figure><img src="{r["file"]}" alt="Frame {i}" loading="lazy"><figcaption>Frame {i} — {html.escape(r["direction"])} — {r["duration"][0]}/{r["duration"][1]}s</figcaption></figure>' for i,r in enumerate(records))
    comparison = ''.join(f'<section class="pair"><h3>{p["from"]} → {p["to"]}: {p["kind"]}</h3><div class="images"><img src="{records[p["from"]]["file"]}" alt="Previous frame"><img src="{records[p["to"]]["file"]}" alt="Next frame"></div><p>{p["rgba_changed_pixels"]} exact RGBA differences; {p["visible_rgba_changed_pixels"]} visible; {p["hidden_rgb_only_changed_pixels"]} hidden only.</p></section>' for p in pairs)
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ordered supplied-art review</title><style>
body{font:16px system-ui;background:#171a21;color:#edf0f5;margin:24px}button,input,select{font:inherit;margin:6px}img{image-rendering:pixelated;background:repeating-conic-gradient(#bbb 0% 25%,#888 0% 50%) 0/16px 16px}
#stage{padding:20px;overflow:auto;min-height:100px}#player{display:block;max-width:none}.grid{display:flex;flex-wrap:wrap;gap:16px}figure{margin:0;padding:8px;background:#272d39}figure img{width:128px;height:auto}figcaption{max-width:250px}.pair{border-top:1px solid #566;padding:16px 0}.images{display:flex;gap:20px;overflow:auto}.images img{max-width:none}#seek{width:min(600px,80vw)}code{overflow-wrap:anywhere}
</style><h1>Ordered supplied-art review</h1><p>Art and motion are unreviewed. One rational timeline drives this player, frame entries and pair inspection. All canvases retain registration; no per-pose recentering. GIF timing and artistic quality are separate.</p>
<p>Sequence <code>IDENT</code></p><button id="play">Play</button><button id="restart">Restart</button><button id="prev">Previous frame</button><button id="next">Next frame</button><label>Integer display scale <select id="scale"><option>1</option><option selected>2</option><option>4</option></select></label>
<div id="stage"><img id="player" alt="Timed current frame"></div><input id="seek" type="range" min="0" step="any"><output id="status"></output>
<h2>Every ordered frame</h2><div class="grid">CARDS</div><h2>Every adjacent pair and return seam</h2>PAIRS
<script id="review-data" type="application/json">DATA</script><script>
const data=JSON.parse(document.getElementById('review-data').textContent), frames=data.frames;
const clock=data.playback_clock, total=clock.total, count=data.play_count, limit=count===0?Infinity:clock.limit, starts=clock.starts, ends=clock.ends, minHold=Math.min(...clock.durations);
const player=document.getElementById('player'), seek=document.getElementById('seek'), status=document.getElementById('status'), play=document.getElementById('play');
let elapsed=0, epoch=0, playing=false, current=0, ready=false, raf=null;
seek.max=String(count===0?total:limit);
function indexAt(t){const epsilon=Math.min(minHold/4,8*Number.EPSILON*Math.max(total,Math.abs(t)));if(count!==0&&t+epsilon>=limit)return frames.length-1;let phase=Math.max(0,t)%total;if(phase+epsilon>=total)phase=0;for(let i=0;i<ends.length;i++)if(phase<ends[i]-epsilon)return i;return frames.length-1}
function draw(t){current=indexAt(t);player.src=frames[current].file;const s=Number(document.getElementById('scale').value);player.style.width=(data.canvas[0]*s)+'px';player.style.height=(data.canvas[1]*s)+'px';seek.value=String(count===0?t%total:Math.min(t,limit));status.textContent=`Frame ${current}; ${Math.min(t,limit).toFixed(4)}s; cycle ${total.toFixed(4)}s; ${count===0?'infinite loop':count+' total plays, held final pose'}; ${frames[current].direction}`;play.textContent=playing?'Pause':'Play'}
function tick(now){raf=null;if(!playing)return;const t=elapsed+(now-epoch)/1000;draw(t);if(count!==0&&t>=limit){elapsed=limit;playing=false;draw(elapsed);return}raf=requestAnimationFrame(tick)}
function pause(){if(playing)elapsed+=(performance.now()-epoch)/1000;playing=false;if(raf!==null)cancelAnimationFrame(raf);raf=null;draw(elapsed)}
play.onclick=()=>{if(!ready)return;if(playing){pause();return}if(count!==0&&elapsed>=limit)elapsed=0;epoch=performance.now();playing=true;raf=requestAnimationFrame(tick)};
document.getElementById('restart').onclick=()=>{pause();elapsed=0;draw(0)};
seek.oninput=()=>{const selected=Number(seek.value);pause();elapsed=selected;draw(elapsed)};
document.getElementById('scale').onchange=()=>draw(playing?elapsed+(performance.now()-epoch)/1000:elapsed);
function step(delta){pause();current=(current+delta+frames.length)%frames.length;elapsed=starts[current];draw(elapsed)}
document.getElementById('prev').onclick=()=>step(-1);document.getElementById('next').onclick=()=>step(1);
Promise.all(frames.map(f=>new Promise(resolve=>{const im=new Image();im.onload=resolve;im.onerror=()=>{status.textContent='Image loading failed';resolve(false)};im.src=f.file}))).then(results=>{ready=!results.includes(false);draw(0);if(!ready)status.textContent='Image loading failed; playback disabled'});
</script></html>'''
    # Replace bottom-up so labels/data containing a placeholder word are never reprocessed.
    page = page.replace('DATA',data,1).replace('PAIRS',comparison,1).replace('CARDS',cards,1).replace('IDENT',html.escape(ident),1)
    (directory/'review.html').write_text(page)
    return {'status':'written','ordered_frames':len(arrays),'adjacent_pairs':len(arrays)-1,'return_pairs':1,
            'review_file':'review.html','diagnostics_file':'review.json',
            'clock':'single performance timestamp mapped through rational frame holds; no fixed preview fps',
            'visual_acceptance':'unreviewed','continuous_motion_viewed':False}


def review_sequence(store, ident, directory):
    with output_directory(directory) as stage:
        return _write_review(store,ident,stage)

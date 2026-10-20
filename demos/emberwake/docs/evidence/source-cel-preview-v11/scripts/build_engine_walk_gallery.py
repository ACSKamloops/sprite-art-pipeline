#!/usr/bin/env python3
"""Publish an existing six-clip GPU capture set to a fresh local review folder."""
from pathlib import Path
import argparse
import hashlib
import html
import re
import json
import shutil

HTML = '''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>Emberwake · %%REVISION%% walk review</title>
<style>body{margin:0;background:#101b17;color:#e5eee6;font:16px system-ui}main{max-width:1080px;margin:40px auto;padding:0 24px}small{color:#b9cbb7}h1{font-size:30px;margin:10px 0}p{line-height:1.55;color:#b8c9ba}select{font:inherit;border:1px solid #617861;border-radius:7px;background:#23392b;color:#f4f5e9;padding:10px 14px;margin:0 12px 14px 0}label{display:inline-block;margin-right:12px}video{width:100%;height:auto;image-rendering:pixelated;background:#27392f;border:1px solid #617861;border-radius:9px}a{color:#d7c28a}.caption{display:flex;justify-content:space-around;color:#d7c28a;margin-bottom:10px}</style>
<main><small>EMBERWAKE · LOCAL ART REVIEW · %%REVISION-UPPER%%</small><h1>Latest diagonal walks</h1><p>%%SUMMARY%% The 8/10 motion target remains unmet. Choose a hero and view, or <a href="../game-%%REVISION%%/index.html">play the draft</a>.</p>
<label>Hero <select id="actor"><option value="rowan">Rowan</option><option value="lyra">Lyra</option><option value="brann">Brann</option></select></label><label>Facing <select id="view"><option value="southeast">Front diagonal · SE</option><option value="northeast">Back diagonal · NE</option></select></label><label>Speed <select id="speed"><option value="1">Normal</option><option value=".5">Half</option><option value=".25">Quarter</option></select></label>
<div class="caption"><span>In place</span><span>Moving across the grid</span></div><video controls loop autoplay muted playsinline></video><p id="status" aria-live="polite">Loading…</p><p>The game renderer captured two 0.45-second walk cycles. The moving character resets its route after both cycles. Movement here is an arranged rendering test; ground contact and foot sliding need a separate check.</p><p><a id="poses" href="#">Captured poses</a> · <a id="route" href="#">Movement captures</a> · <a href="MEDIA-RECEIPT.json">Capture receipt</a> · <a href="../godot-walks/">Earlier draft</a></p></main>
<script>const actor=document.querySelector('#actor'),view=document.querySelector('#view'),speed=document.querySelector('#speed'),video=document.querySelector('video'),status=document.querySelector('#status');function load(){const key=actor.value+'-'+view.value;video.src=key+'.mp4';video.playbackRate=Number(speed.value);document.querySelector('#poses').href=key+'-pose-strip.png';document.querySelector('#route').href=key+'-translation.png';video.play().catch(()=>{});status.textContent='Loading '+actor.selectedOptions[0].text+'…'}actor.onchange=view.onchange=load;speed.onchange=()=>video.playbackRate=Number(speed.value);video.onloadeddata=()=>status.textContent=actor.selectedOptions[0].text+' · '+view.selectedOptions[0].text+' · captured Godot frames';load();</script>'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--media', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--revision', default='v9', help='Local game route revision, e.g. v9 or v10')
    parser.add_argument('--summary', default='This draft includes Lyra’s body-weight repair and Brann’s rear step repairs.')
    args = parser.parse_args()
    assert re.fullmatch(r'v[1-9][0-9]*[a-z]?', args.revision), 'Invalid local route revision'
    assert not args.out.exists(), 'Use a fresh review directory'
    records = json.loads((args.media / 'MEDIA-RECEIPT.json').read_text())
    expected = {f'{actor}-{view}' for actor in ['rowan', 'lyra', 'brann']
                for view in ['southeast', 'northeast']}
    assert {row['clip'] for row in records} == expected and len(records) == 6
    for row in records:
        assert sha(args.media / (row['clip'] + '.mp4')) == row['mp4_sha256']
    sources = sorted(p for p in args.media.iterdir() if p.is_file())
    args.out.mkdir(parents=True)
    hashes = {}
    for source in sources:
        target = args.out / source.name
        shutil.copyfile(source, target)
        hashes[source.name] = sha(source)
        assert sha(target) == hashes[source.name]
    page = HTML.replace('%%REVISION%%', args.revision).replace(
        '%%REVISION-UPPER%%', args.revision.upper()).replace('%%SUMMARY%%', html.escape(args.summary))
    (args.out / 'index.html').write_text(page + '\n')
    receipt = {'scope': 'Transport and local player only; no motion acceptance',
               'source_media': str(args.media.resolve()), 'source_hashes': hashes,
               'index_sha256': sha(args.out / 'index.html'),
               'builder_sha256': sha(Path(__file__)), 'all_copied_bytes_exact': True,
               'revision': args.revision, 'summary': args.summary}
    (args.out / 'GALLERY-RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'Local six-clip review ready: {args.out}')


if __name__ == '__main__':
    main()

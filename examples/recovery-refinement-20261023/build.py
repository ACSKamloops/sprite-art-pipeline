#!/usr/bin/env python3
"""Rebuild the frozen recovery comparison; no model requests."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
RAW_HASHES = {
    'generation-01': '890bbe6e0cb1069da2bcbc13f0492911010479db5b3d41185693064374ecac51',
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def native(path):
    raw = Image.open(path).convert('RGBA')
    a = np.array(raw.resize((80, 80), Image.Resampling.NEAREST))
    a[:, :, 3] = np.where(a[:, :, 3] >= 200, 255, 0)
    a[a[:, :, 3] == 0] = 0
    return Image.fromarray(a)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    repo, out = args.repo.resolve(), args.output.absolute()
    if out.exists() or out.is_symlink():
        raise ValueError('Fresh output directory required')
    source = json.loads((HERE/'inputs/source.json').read_text())
    package = repo/'examples/current-hero/package'
    if sha(package/'library.json') != source['source_library_sha256']:
        raise ValueError('Frozen source library changed')
    clip = source['clip']
    images = []
    for f in clip['frames']:
        path = package/f['file']
        if sha(path) != f['sha256']:
            raise ValueError('Source frame changed')
        images.append(Image.open(path).convert('RGBA'))
    for dirname in ['generation-01', 'generation-02']:
        request = json.loads((HERE/dirname/'request.json').read_text())
        ret = json.loads((HERE/dirname/'return.json').read_text())
        if sha(HERE/dirname/'raw.png') != ret['raw_sha256']:
            raise ValueError('Generation return changed')
        if dirname in RAW_HASHES and ret['raw_sha256'] != RAW_HASHES[dirname]:
            raise ValueError('Wrong frozen raw')
        if sha(HERE/dirname/'prompt.txt') != request['prompt_sha256']:
            raise ValueError('Saved prompt changed')
        for f in request['ordered_inputs']:
            if sha(HERE/dirname/f['file']) != f['sha256']:
                raise ValueError('Saved generation input changed')
    entry = native(HERE/'generation-01/raw.png')
    support = native(HERE/'generation-02/raw.png')
    protected = np.array(support)
    protected[56:,28:62] = np.array(images[5])[56:,28:62]
    protected = Image.fromarray(protected)
    variants = {
        'control': images,
        'entry': [entry if i == 1 else im for i, im in enumerate(images)],
        'entry-support': [entry if i == 1 else support if i == 5 else im for i, im in enumerate(images)],
        'entry-protected-support': [entry if i == 1 else protected if i == 5 else im for i, im in enumerate(images)],
    }
    bank = load_module('recovery_bank', repo/'research/pixelengine-imagen/tools/build-rpg-bank.py')
    out.mkdir(parents=True)
    rows = {}
    for name, frames in variants.items():
        result = bank.export_action(out/name, 'get_up', 'SE', frames,
             {'loop': False, 'holds': [f['hold'] for f in clip['frames']], 'events': []},
             {'operation': name, 'source_library_sha256': source['source_library_sha256'],
              'generation': 'saved built-in OpenAI ImageGen returns; no new request',
              'registration': 'entire measured raw canvas to80x80 nearest-center, alpha200; no fit/recenter',
              'protected_region': 'x28..61,y56..79 from old05 only for entry-protected-support; grounded arm excluded'}, list(range(10)))
        rows[name] = result
        for i, im in enumerate(frames):
            if i not in (1,5) and im.tobytes() != images[i].tobytes():
                raise ValueError('Untargeted pose changed')
    # Record the lower-body restoration as a guarded, replayable native pixel edit.
    from sprite_lab import History, candidate_transaction, project_hash, canonical_json, render_frame
    project = json.loads((out/'entry-support/construction/get_up/project.json').read_text())
    original = json.loads(json.dumps(project))
    frame = project['frames'][5]
    cel = frame['cels']['body']
    mask = [[x,y] for y in range(56,80) for x in range(28,62)]
    tx = candidate_transaction(project, cel, protected, mask)
    tx['reason'] = 'Restore frozen boots/shins in x28..61,y56..79; exclude old grounded arm; review knee joins independently'
    hist = History(project)
    hist.apply(tx)
    edited = hist.project
    if render_frame(edited, frame['id']).tobytes() != protected.tobytes():
        raise ValueError('Editor output differs')
    journal = hist.journal()
    replay = History.replay(original, journal)
    if project_hash(replay.project) != project_hash(edited):
        raise ValueError('Journal replay differs')
    hist.undo()
    if project_hash(hist.project) != project_hash(original):
        raise ValueError('Undo differs')
    edit = out/'pixel-edit'
    edit.mkdir()
    (edit/'initial.json').write_text(canonical_json(original)+'\n')
    (edit/'final.json').write_text(canonical_json(edited)+'\n')
    write(edit/'journal.json', journal)
    write(edit/'VERIFIED.json', {'undo_exact':True,'replay_exact':True,'frame05_RGBA_exact':True,
                               'mask':'x28..61,y56..79','art_acceptance':False})
    # Only the independent packet contains anonymized names.
    packet = out/'packet'
    packet.mkdir()
    mapping = {'A':'entry-protected-support', 'B':'control', 'C':'entry', 'D':'entry-support'}
    for label, name in mapping.items():
        dest = packet/label
        dest.mkdir()
        frames = variants[name]
        record = {'canvas':[80,80], 'pivot':[40,72], 'loop':False,'duration':[6,5], 'frames':[]}
        for i, im in enumerate(frames):
            p = dest/f'{i:02d}.png'
            im.save(p)
            record['frames'].append({'file':p.name,'hold':clip['frames'][i]['hold'],'sha256':sha(p),
                                    'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest()})
        write(dest/'clip.json',record)
        for scale in (1,2):
            for bg, color in [('light','#ddd9cc'),('dark','#26323c')]:
                sheet = Image.new('RGB',(400*scale,190*scale),color)
                draw = ImageDraw.Draw(sheet)
                for i,im in enumerate(frames):
                    x,y=(i%5)*80*scale,(i//5)*95*scale
                    up=im.resize((80*scale,80*scale),Image.Resampling.NEAREST)
                    sheet.paste(up,(x,y),up)
                    draw.text((x+2,y+80*scale),f'{i:02d}',fill='black' if bg=='light' else 'white')
                sheet.save(dest/f'poses-{bg}-{scale}x.png')
        for bg,color in [('light','#ddd9cc'),('dark','#26323c')]:
            sheet=Image.new('RGB',(960,570),color)
            draw=ImageDraw.Draw(sheet)
            for i in range(9):
                x,y=(i%3)*320,(i//3)*190
                for j in (0,1):
                    im=frames[i+j].resize((160,160),Image.Resampling.NEAREST)
                    sheet.paste(im,(x+j*160,y),im)
                draw.text((x+4,y+164),f'{i:02d} -> {i+1:02d}',fill='black' if bg=='light' else 'white')
            sheet.save(dest/f'pairs-{bg}.png')
    images[9].save(packet/'appearance.png')
    (packet/'BRIEF.md').write_text('Four anonymous complete SE get-up variants. Each has10 exposures with identical rational holds, total1.2 seconds. The first and last poses are identical across variants. The action is a one-shot; stand-to-floor replay reset is not a loop seam. Inspect every pose and adjacent pair at native and nearest2x, light/dark. Judge drawing, character identity, readable limb ownership, support progression, entry and exit. Give independent scoped ratings and precise visible defects, with no target score. A timed export is not proof of continuous human playback. Do not read mappings, implementation or earlier reports until your assessment is frozen.\n')
    write(packet/'FREEZE.json',{str(p.relative_to(packet)):sha(p) for p in sorted(packet.rglob('*')) if p.is_file()})
    write(out/'UNBLIND.json',mapping)
    write(out/'RESULTS.json',{'build_script_sha256':sha(Path(__file__)), 'variants':rows,'changed_slots':[1,5],'clocks_unchanged':True,
                            'literal_endpoints_unchanged':True,'untargeted_frames_exact':True,
                            'scope':'Artifact/editor/replay checks; art acceptance pending'})
    print(json.dumps({'output':str(out),'variants':list(variants),'checks':'exact frames, holds, APNG, ASE and guarded pixel undo/replay'},indent=2))

if __name__ == '__main__':
    main()

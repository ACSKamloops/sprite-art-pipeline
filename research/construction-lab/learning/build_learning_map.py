#!/usr/bin/env python3
"""Join private ROM bytes, bounded disassembly, CPU observations and displayed pixels.

This verifies a declared experiment; it does not infer animation labels from atlases.
Full ROMs/checkpoints stay outside the portable output.
"""
import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
POSES = (171, 172, 173)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def runs(values):
    result = []
    for tick, value in enumerate(values):
        if not result or result[-1]['value'] != value:
            result.append({'value': value, 'start_tick': tick, 'duration_ticks': 1})
        else:
            result[-1]['duration_ticks'] += 1
    return result


def check_pair(baseline, changed, displayed, templates, lag=1):
    failures = []
    for name, source in [('baseline', baseline), ('changed', changed)]:
        for i, row in enumerate(source['rows']):
            if i < lag:
                continue
            expected = source['rows'][i-lag]['selected_generic']
            if expected in POSES and displayed[name][i] not in templates[expected]:
                failures.append(f'{name} displayed tick{i} contradicts selected pose{expected} at lag{lag}')
    return failures


def build(base, variant, rom, static, output):
    output.mkdir(parents=True, exist_ok=True)
    a, b = load(base/'experiment.json'), load(variant/'experiment.json')
    checks = []

    def require(condition, label):
        checks.append({'check': label, 'pass': bool(condition)})
        if not condition:
            raise ValueError(label)

    for field in ('original_rom_sha256', 'core_sha256', 'checkpoint_sha256', 'fps', 'setup'):
        require(a[field] == b[field], 'same controlled input: '+field)
    require(a['original_rom_sha256'] == digest(rom), 'original ROM current hash matches capture')
    require(a['original_unchanged'] and b['original_unchanged'], 'original retained unchanged during both captures')
    require(a['executed_rom_sha256'] == a['original_rom_sha256'], 'baseline executes original bytes')
    patch = b['patch']
    derived = bytearray(rom.read_bytes())
    require(derived[patch['offset']] == patch['before'], 'intervention source byte exists')
    derived[patch['offset']] = patch['after']
    require(hashlib.sha256(derived).hexdigest() == b['executed_rom_sha256'], 'variant differs by exactly declared one byte')
    require([(r['relative_tick'], r['keys']) for r in a['rows']] ==
            [(r['relative_tick'], r['keys']) for r in b['rows']], 'same tick-by-tick input sequence')
    require(all(r['source_tick'] == a['rows'][0]['source_tick']+i for i,r in enumerate(a['rows'])), 'baseline consecutive video frames')
    require(all(r['source_tick'] == b['rows'][0]['source_tick']+i for i,r in enumerate(b['rows'])), 'variant consecutive video frames')

    analysis = load(static)
    methods = []
    for method in analysis['methods']:
        off = method['source_file_offset']
        raw = bytes.fromhex(method['bytes_hex'])
        require(rom.read_bytes()[off:off+len(raw)] == raw, 'static bytes match original: '+method['start'])
        methods.append({**method, 'role_status': 'bounded instruction analysis; role requires separate evidence', 'runtime_cases': {}})

    spec = importlib.util.spec_from_file_location('independent_native_scalar', ROOT/'native/audit.py')
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    ram = (base/a['rows'][0]['raw']/'wram.bin').read_bytes()
    x = int.from_bytes(ram[0xe020:0xe022], 'little')
    y = int.from_bytes(ram[0xe022:0xe024], 'little')
    roi = (x-25, y-40, x+28, y+6)
    images, displayed, all_inputs, traces = {}, {}, {}, {}
    for name, folder, source in [('baseline', base, a), ('changed', variant, b)]:
        images[name], displayed[name] = [], []
        for row in source['rows']:
            raw = folder/row['raw']
            require(digest(raw/'wram.bin') == row['wram_sha256'], f'{name} tick{row["relative_tick"]} WRAM hash')
            require(digest(raw/'oam.bin') == row['oam_sha256'], f'{name} tick{row["relative_tick"]} OAM hash')
            for filename in ('wram.bin','oam.bin','vram.bin','cgram.bin','ppu.json'):
                path = raw/filename
                all_inputs[str(path)] = digest(path)
            im = oracle.scalar(raw).crop(roi)
            images[name].append(im)
            displayed[name].append(hashlib.sha256(im.tobytes()).hexdigest())
        trace_path = folder/'cpu_trace.jsonl'
        all_inputs[str(trace_path)] = digest(trace_path)
        lo, hi = source['rows'][0]['source_tick'], source['rows'][-1]['source_tick']
        relevant = []
        for line in trace_path.open():
            record = json.loads(line)
            if record['x'] == 0 and lo <= record['frame'] <= hi:
                relevant.append(record)
        traces[name] = relevant
        counts = Counter(record['pc'] for record in relevant)
        for method in methods:
            start, end = int(method['start'],16), int(method['end'],16)
            hits = [r for r in relevant if start <= r['pc'] <= end]
            method['runtime_cases'][name] = {'watchpoint_hits': len(hits),
                'points': {hex(pc): count for pc,count in counts.items() if start <= pc <= end},
                'processor_status_values': sorted({r['p'] for r in hits})}
            entry_hits=[r for r in relevant if r['pc']==start]
            entry_modes=sorted({(int(bool(r['p']&32)),int(bool(r['p']&16))) for r in entry_hits})
            method['runtime_cases'][name]['observed_entry_MF_XF']=entry_modes
            if entry_modes:
                require((method['entry_mode']['MF'],method['entry_mode']['XF']) in entry_modes,
                        f'{name} entry width matches executed processor status: '+method['start'])
            require(all(int(inst['address'],16)+inst['length']-1<=end for inst in method['instructions']),
                    f'{name} static instructions stay inside byte evidence: '+method['start'])

    # Learn displayed signatures from baseline's already observed one-video-tick lag.
    # Several signatures per pose retain native palette/equipment flicker.
    templates = {pose: set() for pose in POSES}
    for i in range(1,len(a['rows'])):
        pose = a['rows'][i-1]['selected_generic']
        if pose in templates:
            templates[pose].add(displayed['baseline'][i])
    require(all(templates.values()), 'all three native pose signature classes observed')
    require(not any(templates[p] & templates[q] for p in POSES for q in POSES if p != q), 'displayed pose classes disjoint')
    require(not check_pair(a,b,displayed,templates), 'variant hardware pixels corroborate one-video-tick presentation lag')
    require(bool(check_pair(a,b,displayed,templates,lag=0)), 'adversary: zero presentation lag rejected')
    require(bool(check_pair(a,b,displayed,templates,lag=2)), 'adversary: two presentation ticks rejected')
    lookup = {signature:pose for pose, signatures in templates.items() for signature in signatures}
    classified = {name:[lookup.get(h,'outside studied three poses') for h in hashes] for name,hashes in displayed.items()}
    observed = {name:[r for r in runs(values) if r['value'] in POSES] for name,values in classified.items()}
    require([(r['value'],r['duration_ticks']) for r in observed['baseline']] == [(171,5),(172,5),(173,5)], 'baseline displayed holds are5/5/5')
    require([(r['value'],r['duration_ticks']) for r in observed['changed']] == [(171,10),(172,5),(173,5)], 'intervention displayed holds are10/5/5')
    mutated = json.loads(json.dumps(b));mutated['rows'][10]['selected_generic'] = 172
    require(bool(check_pair(a,mutated,displayed,templates)), 'adversary: selected-frame transition shifted one tick rejected')

    strip = Image.new('RGB', (24*53*3, 2*(46*3+24)), '#20282e');draw=ImageDraw.Draw(strip)
    for j,name in enumerate(('baseline','changed')):
        for i,im in enumerate(images[name][:24]):
            bg=Image.new('RGBA',im.size,'#20282e');bg.alpha_composite(im)
            strip.paste(bg.convert('RGB').resize((53*3,46*3),Image.Resampling.NEAREST),(i*53*3,j*(46*3+24)))
            draw.text((i*53*3,j*(46*3+24)+46*3),f'{i}: {classified[name][i]}',fill='white')
        frames=[]
        for im in images[name]:
            bg=Image.new('RGBA',im.size,'#20282e');bg.alpha_composite(im)
            frames.append(bg.convert('RGB').resize((53*6,46*6),Image.Resampling.NEAREST))
        frames[0].save(output/(name+'-slow.gif'),save_all=True,append_images=frames[1:],duration=100,loop=0)
    strip.save(output/'hold-comparison.png')
    viewer=output/'viewer';viewer.mkdir(exist_ok=True)
    for name in images:
        (viewer/name).mkdir(exist_ok=True)
        for i,im in enumerate(images[name]):im.save(viewer/name/f'{i:02}.png')
    (viewer/'frames.json').write_text(json.dumps({'fps':a['fps'],'total_ticks':len(a['rows']),
        'cases':{name:[{'tick':i,'source_tick':row['source_tick'],'selected_pose':row['selected_generic'],
                        'displayed_pose':classified[name][i],'image':f'{name}/{i:02}.png'} for i,row in enumerate(source['rows'])]
                 for name,source in [('baseline',a),('changed',b)]},
        'scope':'Fixed hardware-OBJ crop from consecutive captures; one script byte changed. Outside studied poses remain unlabelled.'},indent=2)+'\n')
    report={'schema':'game-method-learning/v1','status':'verified bounded intervention; broader game coverage partial',
        'experiment':'normal right Sword first frame-control1C→19','clock_fps':a['fps'], 'fixed_hardware_roi':roi,
        'checks':checks,'failures':0,'source_files':{str(base/'experiment.json'):digest(base/'experiment.json'),str(variant/'experiment.json'):digest(variant/'experiment.json'),str(static):digest(static),'native/audit.py':digest(ROOT/'native/audit.py')},
        'raw_inputs':all_inputs,'selected_runs':{name:runs([row['selected_generic'] for row in source['rows']]) for name,source in [('baseline',a),('changed',b)]},
        'presented_pose_runs':observed, 'patch':patch,'methods':methods,
        'findings':[{'claim':'First frame hold doubles5→10ticks; same pose order; subsequent pose and completion delayed5ticks','evidence_type':'controlled one-byte intervention plus independent raw hardware rendering'},
         {'claim':'Selected actor pose appears one video tick later in the observed hardware buffers','evidence_type':'baseline signature classification corroborated on changed runtime; zero/two lag rejected'},
         {'claim':'C0F5A3 reads script data; C0F5CE..C0F5DB masks low control bits and stores actor hold counter','evidence_type':'bounded 65816 instruction analysis; execution watchpoints separately recorded'},
         {'claim':'C0F632 begins hardware-object assembly; it is not the frame-hold decoder','evidence_type':'bounded instruction analysis and captured watchpoint hits'}],
        'pipeline_transfer':{'timing':'Author positive holds at an explicit simulation clock; implement control/wait branches as state, not flattened atlas order',
            'construction':'Separate body/equipment cels, palette state, root movement, effects, and emitted gameplay events',
            'verification':'Replay same start state/input; compare frame selection, displayed pixels and completion; reject shifted timings',
            'art_acceptance':'Native timing evidence does not approve a new character silhouette, anatomy or joint seams'},
        'limits':['Only one normal right Sword branch is causally intervened on; no complete game claim',
            'Pose signatures use fixed-ROI baseline classes and retain flicker; they are not an independent semantic pose decoder',
            'Scalar renderer covers OBJ buffers, not complete background/color-math/scanline behavior',
            'Selective CPU watchpoints are not a complete instruction trace or call graph',
            'GIFs are explicitly slowed100ms/tick; report and contact sheet retain source-clock ticks']}
    (output/'hold-experiment-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks':len(checks),'failures':0,'presented_holds':observed,'methods':len(methods),'output':str(output)}))
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path,required=True);parser.add_argument('--variant',type=Path,required=True)
    parser.add_argument('--rom',type=Path,required=True);parser.add_argument('--static',type=Path,default=ROOT/'learning/static-methods.json');parser.add_argument('--output',type=Path,default=ROOT/'learning')
    args=parser.parse_args();build(args.baseline,args.variant,args.rom,args.static,args.output)

"""Run the local 65-cel Captain consumer checks on one fresh frozen export.

This is a case-specific verified consumer recipe, not a general animation
generator or an art approval tool. World and engine branches run independently.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
WORLD = HERE.parent / 'captain-3d-to-sprite-integration-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_passing_evidence(output):
    """Diagnostics can exit successfully while reporting a failed condition."""
    runtime = json.loads((output / 'godot/report.json').read_text())
    gpu = json.loads((output / 'godot/independent-gpu-proof.json').read_text())
    world = json.loads((output / 'world/receipt.json').read_text())
    held = json.loads((output / 'held-sole/report.json').read_text())
    if not runtime['passed'] or runtime['failures']:
        raise AssertionError('Engine runtime reported failed checks')
    if gpu['actual_native_readbacks'] != 130 or gpu['max_channel_error'] > 1:
        raise AssertionError('GPU readback coverage or tolerance failed')
    if not gpu['negative_actual_image_shift_one_px']['channels_over_one_lsb']:
        raise AssertionError('GPU negative control failed to reject a shift')
    if len(world['variants']) != 9 or sum(v['decoded_frame_count'] for v in world['variants']) != 2730:
        raise AssertionError('World replay coverage incomplete')
    if any(v['clipped_count'] or v['actual_all_frames_max_rgb_error'] > 2 for v in world['variants']):
        raise AssertionError('World replay pixels or framing failed')
    if held['actual_decoded_packets'] != 130 or not held['negative_control']['correctly_rejected']:
        raise AssertionError('Held-sole evidence or negative control incomplete')
    failures = [row for row in held['rows'] if row['status'] != 'WITHIN_ONE_PIXEL_PER_AXIS']
    if not held['rows'] or failures:
        raise AssertionError(f'Held-sole one-pixel gate failed: {len(failures)} failed or unmeasured pairs')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--joints', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--visual-policy', choices=('continuous','coherent'), default='continuous')
    args = parser.parse_args()
    args.contract = args.contract.resolve()
    args.joints = args.joints.resolve()
    args.output = args.output.resolve()
    if not args.name.replace('-', '').replace('_', '').isalnum():
        raise ValueError('A simple fresh pack name is required')
    if args.output.exists() or (HERE / 'packs' / args.name).exists():
        raise FileExistsError('Keep prior auditions and packs immutable')
    godot = shutil.which('godot')
    xvfb = shutil.which('xvfb-run')
    if not godot or not xvfb:
        raise RuntimeError('Godot and xvfb-run are required')
    spec = importlib.util.spec_from_file_location('replay', WORLD / 'world_replay.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    replay = module.Replay(args.contract, args.joints)
    source_files = [args.contract, args.joints] + [args.contract.parent / f['file'] for f in replay.frames]
    before = {str(p): sha(p) for p in source_files}
    old_pack_files = {str(p): sha(p) for p in (HERE / 'packs').rglob('*')
                      if p.is_file() and p.suffix in ('.png', '.json', '.res')}
    code_files = [Path(__file__), WORLD / 'world_replay.py', WORLD / 'check_held_sole_pixels.py']
    code_files += [HERE / x for x in ('prepare_pack.py', 'configure_imports.gd',
                                    'build_resources.gd', 'test_runtime.gd', 'viewer.gd', 'check_gpu.py')]
    code_hashes = {str(p): sha(p) for p in code_files}
    args.output.mkdir(parents=True)
    logs = args.output / 'logs'
    logs.mkdir()
    stages = []

    def run(stage, command):
        started = time.monotonic()
        print('START', stage, flush=True)
        with (logs / (stage + '.log')).open('w') as log:
            result = subprocess.run([str(x) for x in command], cwd=HERE, stdout=log, stderr=subprocess.STDOUT)
        stages.append({'name': stage, 'argv': [str(x) for x in command], 'exit_code': result.returncode,
                       'elapsed_seconds': time.monotonic() - started, 'log_SHA256': sha(logs / (stage + '.log'))})
        if result.returncode:
            raise RuntimeError(f'{stage} failed; inspect {logs / (stage + ".log")}')
        print('PASS', stage, flush=True)

    def world_branch():
        run('world', [sys.executable, WORLD / 'world_replay.py', '--contract', args.contract,
                      '--joints', args.joints, '--output', args.output / 'world', '--loops', '3'])
        run('held-sole', [sys.executable, WORLD / 'check_held_sole_pixels.py', '--contract', args.contract,
                         '--corrected-joints', args.joints, '--export', args.output / 'world',
                         '--output', args.output / 'held-sole', '--mode', args.visual_policy])

    def engine_branch():
        run('prepare', [sys.executable, HERE / 'prepare_pack.py', '--contract', args.contract,
                        '--joints', args.joints, '--name', args.name, '--visual-policy', args.visual_policy])
        base = [godot, '--headless', '--audio-driver', 'Dummy', '--path', HERE]
        run('import-1', base + ['--editor', '--import'])
        run('configure', base + ['--script', 'configure_imports.gd', '--', '--pack', args.name])
        run('import-2', base + ['--editor', '--import'])
        run('resources', base + ['--script', 'build_resources.gd', '--', '--pack', args.name])
        run('runtime', [xvfb, '-a', godot, '--audio-driver', 'Dummy', '--path', HERE, '--script',
                        'test_runtime.gd', '--', '--pack', args.name, '--output', args.output / 'godot'])
        run('gpu', [sys.executable, HERE / 'check_gpu.py', '--output', args.output / 'godot',
                    '--pack', HERE / 'packs' / args.name])

    receipt = {'state': 'RUNNING_LOCAL_CONSUMER_CHECKS', 'art_accepted': False,
               'selected_visual_policy': args.visual_policy,
               'source_SHA256': before, 'code_SHA256': code_hashes, 'stages': stages,
               'scope': '65-cel threequarter export; no directions, attack actions or artistic acceptance inferred'}
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(world_branch), pool.submit(engine_branch)]
            for future in futures:
                future.result()
        require_passing_evidence(args.output)
        if before != {str(p): sha(p) for p in source_files}:
            raise AssertionError('Frozen export changed during consumer checks')
        if any(sha(p) != h for p, h in old_pack_files.items()):
            raise AssertionError('Prior Godot pack changed')
        if any(sha(p) != h for p, h in code_hashes.items()):
            raise AssertionError('Consumer code changed during audition')
        for relative in ('world/receipt.json', 'held-sole/report.json', 'godot/report.json',
                         'godot/independent-gpu-proof.json'):
            receipt.setdefault('evidence_SHA256', {})[relative] = sha(args.output / relative)
        receipt.update(state='PASS_LOCAL_CONSUMER_CHECKS_ART_UNAPPROVED',
                       frozen_source_unchanged=True, old_pack_files_preserved=len(old_pack_files))
        print('AUDITION_PASS', args.output, flush=True)
    except Exception as error:
        receipt.update(state='FAILED_LOCAL_CONSUMER_CHECKS', error=str(error))
        raise
    finally:
        (args.output / 'audition.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()

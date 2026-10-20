#!/usr/bin/env python3
"""Encode the six explicit Godot walk captures; source PNGs stay authoritative."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--expected', type=Path)
    args = parser.parse_args()
    native = args.native.resolve()
    captures = json.loads((native / 'RECEIPT.json').read_text())
    assert captures['passed'] and captures['clock_hz'] == 320
    assert not args.out.exists(), 'A fresh output directory is required'
    ledger = []
    for line in (native / 'SHA256SUMS').read_text().splitlines():
        digest, relative = line.split(None, 1)
        path = (native / relative.strip()).resolve()
        assert path.is_relative_to(native) and sha(path) == digest
        ledger.append(relative.strip())
    expected = None
    if args.expected:
        expected = {row['clip']: row['mp4_sha256']
                    for row in json.loads(args.expected.read_text())}
    args.out.mkdir(parents=True)

    def encode(clip):
        key = clip['actor'] + '-' + clip['view']
        assert Path(key).name == key and clip['ticks'] == 288
        assert all(row['file'] in ledger for row in clip['samples'])
        target = args.out / (key + '.mp4')
        command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-framerate',
                   '320', '-i', str(native / key / '%04d.png'), '-an', '-c:v',
                   'libx264', '-threads', '2', '-preset', 'veryfast', '-crf', '16',
                   '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(target)]
        subprocess.run(command, check=True, capture_output=True)
        probe = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,avg_frame_rate,nb_read_frames,duration',
            '-of', 'json', str(target)], text=True))['streams'][0]
        assert probe['avg_frame_rate'] == '320/1'
        assert int(probe['nb_read_frames']) == 288 and float(probe['duration']) == .9
        assert (probe['width'], probe['height']) == (640, 280)
        if expected is not None:
            assert sha(target) == expected[key], 'Encoded bytes or toolchain changed'
        poses = Image.new('RGB', (96 * 8, 104))
        route = Image.new('RGB', (320 * 8, 280))
        for phase in range(8):
            tick = phase * 18 + 9
            with Image.open(native / key / f'{tick:04}.png') as frame:
                poses.paste(frame.crop((112, 132, 208, 236)), (phase * 96, 0))
                route.paste(frame.crop((320, 0, 640, 280)), (phase * 320, 0))
        poses.save(args.out / (key + '-pose-strip.png'))
        route.save(args.out / (key + '-translation.png'))
        return {'clip': key, 'mp4_sha256': sha(target), 'command': command,
                'probe': probe, 'expected_encoded_bytes_exact': expected is not None,
                'source_capture_ledger_entries_verified': len(ledger),
                'scope': 'Lossy review transport; no art, contact or continuous perception score.'}

    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(encode, captures['clips']))
    (args.out / 'MEDIA-RECEIPT.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(f'Encoded {len(rows)} .9s clips; {len(ledger)} source hashes verified')


if __name__ == '__main__':
    main()

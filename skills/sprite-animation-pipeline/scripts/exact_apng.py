#!/usr/bin/env python3
"""Encode ordered manifest PNGs as lossless APNG with exact rational holds."""
import argparse
import binascii
import hashlib
import io
import json
from pathlib import Path
import struct
from fractions import Fraction
from PIL import Image


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def chunks(data):
    require(data[:8] == b'\x89PNG\r\n\x1a\n', 'Invalid PNG signature')
    at = 8
    while at < len(data):
        require(at + 12 <= len(data), 'Truncated PNG chunk')
        n = struct.unpack('>I', data[at:at+4])[0]
        require(at + n + 12 <= len(data), 'Truncated PNG payload')
        kind, body = data[at+4:at+8], data[at+8:at+8+n]
        crc = struct.unpack('>I', data[at+8+n:at+12+n])[0]
        require(crc == binascii.crc32(kind + body) & 0xffffffff, 'PNG CRC mismatch')
        yield kind, body
        at += n + 12
    require(at == len(data), 'Trailing PNG bytes')


def chunk(kind, body):
    return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', binascii.crc32(kind + body) & 0xffffffff)


def rational(value):
    require(isinstance(value, list) and len(value) == 2 and all(type(n) is int and n > 0 for n in value), 'Expected positive integer rational [numerator, denominator]')
    return Fraction(*value)


def encode(images, holds, plays):
    output = bytearray(b'\x89PNG\r\n\x1a\n')
    sequence = 0
    header = None
    for i, (image, hold) in enumerate(zip(images, holds)):
        stream = io.BytesIO()
        image.save(stream, format='PNG', optimize=False)
        parts = list(chunks(stream.getvalue()))
        ihdr = parts[0][1]
        if i == 0:
            header = ihdr
            output += chunk(b'IHDR', ihdr) + chunk(b'acTL', struct.pack('>II', len(images), plays))
        require(ihdr == header, 'Inconsistent frame PNG headers')
        output += chunk(b'fcTL', struct.pack('>IIIIIHHBB', sequence, image.width, image.height, 0, 0, hold.numerator, hold.denominator, 0, 0))
        sequence += 1
        for kind, body in parts:
            if kind != b'IDAT':
                continue
            if i == 0:
                output += chunk(b'IDAT', body)
            else:
                output += chunk(b'fdAT', struct.pack('>I', sequence) + body)
                sequence += 1
    return bytes(output + chunk(b'IEND', b''))


def verify(data, images, holds, plays):
    parts = list(chunks(data))
    require(parts[0][0] == b'IHDR' and parts[1] == (b'acTL', struct.pack('>II', len(images), plays)) and parts[-1] == (b'IEND', b''), 'Invalid APNG chunk ordering/control')
    require(sum(k == b'acTL' for k, _ in parts) == 1, 'Duplicate animation control')
    sequence, frame, have_data = 0, -1, False
    controls = []
    for kind, body in parts[2:-1]:
        require(kind in (b'fcTL', b'IDAT', b'fdAT'), 'Unexpected APNG chunk')
        if kind in (b'fcTL', b'fdAT'):
            require(struct.unpack('>I', body[:4])[0] == sequence, 'APNG sequence mismatch')
            sequence += 1
        if kind == b'fcTL':
            require(frame == -1 or have_data, 'Frame missing image data')
            frame += 1
            require(frame < len(images) and len(body) == 26, 'Unexpected frame control')
            _, width, height, x, y, num, den, dispose, blend = struct.unpack('>IIIIIHHBB', body)
            require((width, height) == images[frame].size and (x, y, dispose, blend) == (0, 0, 0, 0), 'Frame rectangle/disposal/blend mismatch')
            require((num, den) == (holds[frame].numerator, holds[frame].denominator), 'APNG rational hold mismatch')
            controls.append([num, den])
            have_data = False
        else:
            require(frame >= 0 and kind == (b'IDAT' if frame == 0 else b'fdAT'), 'APNG frame data order mismatch')
            have_data = True
    require(frame + 1 == len(images) and have_data, 'APNG frame count mismatch')
    with Image.open(io.BytesIO(data)) as reopened:
        require(reopened.n_frames == len(images) and reopened.info['loop'] == plays and not reopened.info.get('default_image', False), 'Pillow frame count/loop/default-image mismatch')
        for i, image in enumerate(images):
            reopened.seek(i)
            require(reopened.convert('RGBA').tobytes() == image.tobytes(), f'Pillow RGBA mismatch frame {i}')
            require(abs(reopened.info['duration'] / 1000 - float(holds[i])) < 1e-12, f'Pillow hold mismatch frame {i}')
    return {'crc_all_chunks_valid': True, 'sequence_fields_checked': sequence, 'frame_data_order_exact': True, 'actual_fctl_holds': controls, 'pillow_all_rgba_exact': True, 'actual_actl': [len(images), plays]}


def convert(manifest, output_directory):
    manifest, output_directory = Path(manifest).resolve(), Path(output_directory).absolute()
    require(not output_directory.exists() and not output_directory.is_symlink(), 'Output directory must be fresh; refusing overwrite')
    require(output_directory.parent.is_dir(), 'Output parent must already exist')
    raw = manifest.read_bytes()
    source = json.loads(raw)
    canvas = source.get('canvas')
    require(isinstance(canvas, list) and len(canvas) == 2 and all(type(n) is int and 0 < n <= 65535 for n in canvas), 'Invalid canvas')
    require(type(source.get('loop')) is bool, 'loop must be true or false')
    frames = source.get('frames')
    require(isinstance(frames, list) and 2 <= len(frames) <= 512, 'Expected 2-512 ordered frames')
    images, holds, pins = [], [], []
    for i, frame in enumerate(frames):
        rel = Path(frame['file'])
        require(not rel.is_absolute() and '..' not in rel.parts, 'Frame file must be a relative path inside manifest directory')
        path = (manifest.parent / rel).resolve()
        require(path.is_relative_to(manifest.parent), 'Frame symlink escapes manifest directory')
        data = path.read_bytes()
        require(sha(data) == frame['sha256'], f'Stale source hash frame {i}')
        hold = rational(frame['hold'])
        require(hold.numerator <= 65535 and hold.denominator <= 65535, f'Hold frame {i} exceeds exact APNG 16-bit delay fields')
        with Image.open(io.BytesIO(data)) as original:
            require(original.format == 'PNG' and getattr(original, 'n_frames', 1) == 1, 'Expected static source PNG')
            image = original.convert('RGBA')
        require(list(image.size) == canvas, f'Canvas mismatch frame {i}')
        rgba = image.tobytes()
        images.append(image)
        holds.append(hold)
        pins.append({'index': i, 'file': frame['file'], 'resolved_source': str(path), 'sha256': sha(data), 'rgba_sha256': sha(rgba), 'partial_alpha_pixels': sum(0 < a < 255 for a in rgba[3::4]), 'transparent_nonzero_rgb_pixels': sum(rgba[p+3] == 0 and any(rgba[p:p+3]) for p in range(0, len(rgba), 4))})
    duration = sum(holds, Fraction())
    if 'duration' in source:
        require(rational(source['duration']) == duration, 'Declared duration mismatch')
    plays = 0 if source['loop'] else 1
    encoded = encode(images, holds, plays)
    verification = verify(encoded, images, holds, plays)
    receipt = {'schema': 'exact-apng-receipt/v1', 'manifest': str(manifest), 'manifest_sha256': sha(raw), 'canvas': canvas, 'loop': source['loop'], 'duration': [duration.numerator, duration.denominator], 'frames': pins, 'output': 'animation.apng.png', 'output_sha256': sha(encoded), 'verification': verification, 'scope': 'Exact file encoding and decoded source RGBA; no art, contact or browser playback approval'}
    # All source validation, encoding and independent decoding finish before mkdir.
    output_directory.mkdir()
    with (output_directory / 'animation.apng.png').open('xb') as stream:
        stream.write(encoded)
    with (output_directory / 'receipt.json').open('x') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output_directory', type=Path)
    args = parser.parse_args()
    try:
        receipt = convert(args.manifest, args.output_directory)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f'Error: {error}\n')
    print(json.dumps({'output': str(args.output_directory), 'sha256': receipt['output_sha256'], 'frames': len(receipt['frames']), 'verified': True}))


if __name__ == '__main__':
    main()

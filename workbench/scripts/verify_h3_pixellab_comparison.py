#!/usr/bin/env python3
"""Replay the retained three-case comparison checks offline; no model calls.

Verifies artifact bindings and measures delivered pixels. Does not recover private
inference, infer native PixelLab timing, or certify animation aesthetics.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image


CASES = [('walk-v1', 'h3-walk-001', 'pixellab-walk-v1'),
         ('slash-v1', 'h3-slash-001', 'pixellab-slash-v1'),
         ('slash-margin-v2', 'h3-slash-margin-002', 'pixellab-slash-margin-v2')]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(value):
    return base64.b64decode(value.split(',', 1)[-1], validate=True)


def rgba(raw):
    with Image.open(BytesIO(raw)) as image:
        if image.format != 'PNG' or image.size != (256, 256):
            raise ValueError('Expected 256x256 PNG')
        return np.array(image.convert('RGBA'))


def captured_pair(har, records):
    """Count the complete producer capture, not just the selected REA projection."""
    ordinals = {r['ordinal'] for r in records}
    if len(ordinals) != len(records):
        raise ValueError('Repeated REA ordinal')
    if not all(r['reported'] == har[r['ordinal']] for r in records):
        raise ValueError('REA record/HAR mismatch')
    posts = [i for i, entry in enumerate(har) if entry['request']['method'] == 'POST']
    finals = [i for i, entry in enumerate(har) if entry['request']['method'] == 'GET'
              and json.loads(entry['response']['content']['text']).get('status') == 'completed']
    if len(posts) != 1 or len(finals) != 1:
        raise ValueError('Full HAR must contain exactly one POST and one completed GET')
    if not set(posts + finals).issubset(ordinals):
        raise ValueError('REA selection omits captured submission or completed result')
    return har[posts[0]], har[finals[0]]


def verify(root):
    failures, cases = [], []

    def check(condition, label):
        if not condition:
            raise ValueError(label)

    for name, native_name, pixel_name in CASES:
        try:
            native, pixel = root / native_name, root / pixel_name
            load = lambda path: json.loads(path.read_bytes())
            nr, pr = load(native / 'request.json'), load(pixel / 'request.json')
            case, pair = load(native / 'case.json'), load(pixel / 'pair.json')
            for filename, expected in case['input_hashes'].items():
                check(digest((native / filename).read_bytes()) == expected, 'Native prepared-input hash mismatch')
            check(digest((native / 'case.json').read_bytes()) == pair['native_case_sha256'], 'Pair/native case hash mismatch')
            check(digest((native / 'request.json').read_bytes()) == pair['native_request_sha256'], 'Pair/native request hash mismatch')
            source = (pixel / 'source.png').read_bytes()
            check(digest(source) == pair['source_png_sha256'] == case['source_png_sha256'], 'Pinned source hash mismatch')
            check(source == (native / 'source.png').read_bytes(), 'Source PNG pair mismatch')
            check(source == decode(pr['first_frame']['base64']), 'PixelLab request PNG mismatch')
            first = [c for c in nr['content'] if c.get('role') == 'first_frame']
            check(len(first) == 1, 'Native first-frame role mismatch')
            check(source == decode(first[0]['image_url']['url']), 'Native request PNG mismatch')
            prompt = [c['text'] for c in nr['content'] if c['type'] == 'text']
            check(prompt == [pr['description']], 'Literal prompt mismatch')
            check(digest(pr['description'].encode()) == pair['literal_prompt_sha256'], 'Pinned literal prompt hash mismatch')
            check(set(nr) == {'model', 'content', 'resolution', 'duration', 'ratio'} and len(nr['content']) == 2,
                  'Unexpected native control/conditioning field')
            check(set(pr) == {'first_frame', 'description', 'frame_count', 'seed', 'no_background', 'enhance_prompt'},
                  'Unexpected PixelLab control/conditioning field')
            check(pr['frame_count'] == 16 and pr['no_background'] is True, 'PixelLab controls mismatch')
            check(pr['seed'] == 123 and pr['enhance_prompt'] is False, 'PixelLab prompt/seed mismatch')
            check(nr['model'] == 'MiniMax-H3' and nr['duration'] == 4, 'Native controls mismatch')
            check(nr['resolution'] == '768P' and nr['ratio'] == 'adaptive', 'Native resolution/ratio mismatch')
            har_path = pixel / 'network-final.har'
            har_bytes = har_path.read_bytes()
            har = json.loads(har_bytes)['log']['entries']
            rea = load(pixel / 'REA-FINAL.json')
            check(rea['subject']['digest']['sha256'] == digest(har_bytes), 'REA subject hash mismatch')
            check(rea['normalized_result']['artifact']['sha256'] == digest(har_bytes), 'REA artifact hash mismatch')
            records = rea['normalized_result']['records']
            post, final = captured_pair(har, records)
            check(post['request']['url'] == 'https://api.pixellab.ai/v2/animate-pixminimax', 'Wrong captured route')
            check(json.loads(post['request']['postData']['text']) == pr, 'REA submission/request mismatch')
            completed = load(pixel / 'completed-response.json')
            check(json.loads(final['response']['content']['text']) == completed,
                  'REA completed-response mismatch')
            check(completed['status'] == 'completed', 'Job incomplete')
            images = completed['last_response']['images']
            manifest = load(pixel / 'extracted/manifest.json')
            check(len(images) == len(manifest['frames']) == 17, 'Reference+generated count mismatch')
            stats, arrays = [], []
            for slot, (value, record) in enumerate(zip(images, manifest['frames'])):
                raw = (pixel / 'extracted' / record['file']).read_bytes()
                check(record['index'] == slot, 'Returned slot order mismatch')
                check(raw == decode(value['base64']), 'Returned/extracted PNG bytes mismatch')
                check(digest(raw) == record['png_sha256'], 'PNG manifest hash mismatch')
                array = rgba(raw)
                check(digest(array.tobytes()) == record['decoded_rgba_sha256'], 'Decoded RGBA hash mismatch')
                alpha = array[..., 3]
                arrays.append(array)
                stats.append({'slot': slot, 'visible_rgb_colors': int(len(np.unique(array[..., :3][alpha > 0], axis=0))),
                              'alpha_values': np.unique(alpha).tolist(),
                              'alpha_border_pixels': int(np.count_nonzero(alpha[0]) + np.count_nonzero(alpha[-1])
                                  + np.count_nonzero(alpha[:, 0]) + np.count_nonzero(alpha[:, -1]))})
            original, returned = rgba(source), arrays[0]
            zeroed = original.copy()
            zeroed[zeroed[..., 3] == 0, :3] = 0
            reference = {'alpha_exact': bool(np.array_equal(original[..., 3], returned[..., 3])),
                         'visible_rgb_exact': bool(np.array_equal(original[..., :3][original[..., 3] > 0],
                                                                  returned[..., :3][original[..., 3] > 0])),
                         'zero_hidden_rgb_replay_exact': bool(np.array_equal(zeroed, returned)),
                         'hidden_rgb_changed_pixels': int(np.count_nonzero(np.any(original != returned, axis=2)))}
            check(all(reference[k] for k in ['alpha_exact', 'visible_rgb_exact', 'zero_hidden_rgb_replay_exact']),
                  'Reference normalization did not replay exactly')
            media = load(native / 'media-review/MANIFEST.json')
            video_hash = digest((native / 'native-video.mp4').read_bytes())
            check(video_hash == media['native_video_sha256'], 'Native video hash mismatch')
            for frame in media['native_frames']:
                path = native / 'media-review' / frame['file']
                check(digest(path.read_bytes()) == frame['sha256'], 'Native frame hash mismatch')
            cases.append({'case': name, 'native_run': native_name, 'pixellab_run': pixel_name,
                          'source_png_sha256': digest(source), 'prompt_utf8_sha256': digest(pr['description'].encode()),
                          'rea_evidence_id': rea['evidence_id'], 'rea_har_sha256': digest(har_bytes),
                          'rea_authority': rea['authority'], 'returned_pngs_verified': len(images),
                          'native_frames_verified': len(media['native_frames']), 'native_video_sha256': video_hash,
                          'reference0': reference, 'generated_frame_stats': stats[1:],
                          'source_fps_known': False, 'same_private_checkpoint_known': False})
        except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
            failures.append({'case': name, 'error': str(error)})
    return {'version': 1, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'cases': cases,
            'failures': failures, 'offline_only': True, 'art_acceptance': False,
            'private_conversion_recovered': False,
            'scope': 'Matched inputs, actual producer HAR/REA bindings, ordered PNG bytes, native media hashes and observed pixel statistics'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.root.resolve())
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'cases_verified': len(result['cases']), 'failures': result['failures'],
                      'returned_pngs_verified': sum(c['returned_pngs_verified'] for c in result['cases']),
                      'native_frames_verified': sum(c['native_frames_verified'] for c in result['cases'])}))
    raise SystemExit(bool(result['failures']))

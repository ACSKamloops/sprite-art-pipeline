"""Source-bound procedural effect sequences, with no prepared-part inference."""
import base64
from fractions import Fraction
import json
from pathlib import Path
import subprocess

import numpy as np

from .core import ValidationError, canonical_json, digest, save_sequence

PINNED_MANIFEST_SHA256 = '188743c8078e006117a6cbc51fdf96a73cafecc387a1a998276d93aa8d19645f'


def render_effect(store, recipe, *, subject=None, images=None, timeout=60):
    # Local resource profile narrows source limits, recorded as our policy.
    if not isinstance(recipe, dict):
        raise ValidationError('Effect recipe must be an object')
    if isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or not 0 < timeout <= 120:
        raise ValidationError('Effect time budget must be positive and <=120seconds')
    payload = json.loads(canonical_json(recipe))
    canvas = payload.get('canvas', {})
    if not isinstance(canvas,dict) or not isinstance(payload.get('layers',[]),list):
        raise ValidationError('Effect canvas/layers must be object/list')
    w, h = canvas.get('w'), canvas.get('h')
    if type(w) != int or type(h) != int or not 16 <= w <= 512 or not 16 <= h <= 512:
        raise ValidationError('Local VFX profile requires16..512whole-pixel sides')
    frames = payload.get('frames', 8)
    if type(frames) != int or not 1 <= frames <= 32:
        raise ValidationError('Local VFX profile requires1..32frames')
    if len(payload.get('layers', [])) > 128 or len(canonical_json(payload)) > 2*1024*1024:
        raise ValidationError('VFX recipe exceeds local layer/JSON budget')
    total_pixels = 0
    def image_input(ident):
        nonlocal total_pixels
        if ident is None:
            return None
        a = store.get_raster(ident)
        ih, iw = a.shape[:2]; total_pixels += iw*ih
        if total_pixels > 8*1024*1024:
            raise ValidationError('Effect source rasters exceed local budget')
        return {'width':iw,'height':ih,'rgba_base64':base64.b64encode(a.tobytes()).decode()}
    supplied_images = {} if images is None else images
    if not isinstance(supplied_images,dict) or any(not isinstance(k,str) or not k for k in supplied_images):
        raise ValidationError('Effect images must be a named object')
    if len(supplied_images) > 64:
        raise ValidationError('Too many effect source images')
    request = {'recipe':payload,'subject':image_input(subject),'images':{k:image_input(v) for k,v in supplied_images.items()}}
    runner = Path(__file__).with_name('vfx_runner.cjs')
    manifest_raw = (runner.parent/'vendor/vfx/manifest.json').read_bytes()
    if digest(manifest_raw) != PINNED_MANIFEST_SHA256:
        raise ValidationError('Renderer manifest identity changed; choose an explicit new source version')
    try:
        completed = subprocess.run(['node', '--max-old-space-size=2048', str(runner)], input=canonical_json(request),
            capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as e:
        raise ValidationError('Effect exceeded its explicit local time budget') from e
    except FileNotFoundError as e:
        raise ValidationError('Node is required for the pinned source renderer') from e
    try:
        result = json.loads(completed.stdout)
    except (ValueError, UnicodeDecodeError) as e:
        raise ValidationError('Effect adapter failed before producing a structured result') from e
    if completed.returncode or result.get('status') != 'candidate':
        raise ValidationError(result.get('reason','Source renderer rejected recipe'))
    recipe_id = store.put_json({'kind':'effect-recipe','version':1,'input':payload,'normalized':result['recipe'],
        'subject':subject,'images':supplied_images,'renderer_manifest':store.put_bytes(manifest_raw)})
    nw, nh = result['recipe']['canvas']['w'], result['recipe']['canvas']['h']
    fps = Fraction(str(result['recipe']['fps']))
    streams = {}
    for name, encoded in result['streams'].items():
        if len(encoded) != frames:
            raise ValidationError('Renderer output frame count differs')
        arrays = []
        for item in encoded:
            raw = base64.b64decode(item, validate=True)
            if len(raw) != nw*nh*4:
                raise ValidationError('Renderer output dimensions differ')
            arrays.append(np.frombuffer(raw,np.uint8).reshape(nh,nw,4))
        streams[name] = save_sequence(store, arrays, [1/fps]*frames, loop=result['recipe']['loop'],
            pivots=[result['recipe']['origin']]*frames,
            metadata={'kind':'procedural-effect','recipe':recipe_id,'stream':name,'subject_box':result.get('subjectBox'),
                'renderer':'pinned-website-factories-v1','renderer_manifest':result['manifest_sha256'],
                'source_alpha_policy':'binary visibility/composition from retained client','visual_quality':'unreviewed'})
    return {'sequence':streams['frames'],'streams':streams,'recipe':recipe_id,
            'status':'candidate_needs_visual_review','renderer_manifest':result['manifest_sha256'],'executed_modules':result['executed']}

"""Video generation/admission, authored sampling and explicit sprite derivatives.

The fixed-palette rule is calibrated, the manual selector is recovered source,
and orchestration/resize/timing decisions are ours. None is private inference.
"""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from io import BytesIO
import json
import os
from pathlib import Path
import time

import numpy as np
from PIL import Image

from .core import ValidationError, canonical_json, digest, load_sequence, validate_id
from .export import sequence_timeline
from . import motion_frames, motion_provider

EXAMPLES = Path(__file__).with_name('motion_examples')
BOUNDARY = 'Local motion workflow with declared stages; no private PixelLab sampler, neural cutout or deflicker recovery claim'
MAX_CONDITION_FRAMES = 64
MAX_CONDITION_PIXELS = 16 * 1024 * 1024


def _run(base_dir, packet):
    validate_id(packet)
    base = Path(base_dir).resolve()
    folder = base / 'motion-runs'
    if folder.is_symlink() or not folder.resolve().is_relative_to(base):
        raise ValidationError('Motion run folder must stay within the project')
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / packet
    if target.is_symlink():
        raise ValidationError('Motion run cannot be a symlink')
    return target


def credentials():
    """Read the user's already-authorized Hermes route only at actual execution."""
    for name in ('MINIMAX_PAYG_KEY','MINIMAX_API_KEY'):
        if os.environ.get(name):
            return os.environ[name]
    path = Path.home() / '.hermes' / 'auth.json'
    try:
        provider = json.loads(path.read_text())['providers']['minimax-oauth']
        value = provider['access_token']
        expiry = provider.get('expires_at')
        if not isinstance(value, str) or not value:
            raise ValueError()
        if expiry and datetime.fromisoformat(expiry.replace('Z','+00:00')) <= datetime.now(timezone.utc):
            raise ValueError()
        return value
    except (OSError,ValueError,KeyError,TypeError):
        raise ValidationError('Configured Hermes MiniMax credential is unavailable or expired; no automatic refresh or submission') from None


def catalog(store, *, live_provider_enabled=False):
    manifest = json.loads((EXAMPLES/'manifest.json').read_text())
    palette_path = Path(__file__).with_name('studio_examples')/'hero-walk'/'frame-001.png'
    with Image.open(palette_path) as image:
        palette_reference = store.put_raster(np.array(image.convert('RGBA')))
    return {'version':1, 'examples':[{'id':r['id'],'title':r['title']} for r in manifest['examples']],
        'provider':motion_provider.catalog(), 'live_provider_enabled':live_provider_enabled,
        'palette_reference':palette_reference, 'boundary':BOUNDARY,
        'methods':{'resize':'Declared whole-canvas nearest resize; no per-pose fitting',
            'background':'Recovered manual seed selector; connected outlines can be lost. Inspect all masks.',
            'palette':'Calibrated supplied opaque palette rule; not automatic clustering or neural deflicker'},
        'decode_limits':{'encoded_bytes':motion_frames.MAX_MEDIA_BYTES,
            'rgba_bytes':motion_frames.MAX_DECODE_BYTES,'frames':motion_frames.MAX_FRAMES},
        'visual_acceptance':'unreviewed'}


def _bind_extraction_sources(store, result, sources):
    """Keep upstream bindings reachable when sampling only an extraction ID."""
    original = result['extraction']
    extraction = store.get_json(original)
    extraction['parent_extraction'] = original
    extraction['source_bindings'] = list(dict.fromkeys(extraction.get('source_bindings', []) + sources))
    bound = store.put_json(extraction)
    sequence = store.get_json(result['sequence'])
    sequence['metadata']['motion_extraction'] = bound
    sequence['metadata']['source_ids'] += [bound] + sources
    return result | {'extraction':bound,'sequence':store.put_json(sequence),
                     'media_url':'/api/motion/media/'+bound+'.mp4'}


def decode(store, media, *, native_video=None, download_receipt=None):
    raw = store.get_bytes(validate_id(media), max_bytes=motion_frames.MAX_MEDIA_BYTES)
    references = []
    for key, expected in ((native_video,'motion-native-video'),(download_receipt,'motion-media-download')):
        if key:
            doc = store.get_json(validate_id(key))
            if doc.get('kind') != expected or doc.get('video') != media:
                raise ValidationError('Video admission/download does not match supplied bytes')
            references.append(key)
    result = motion_frames.extract_video(store, raw)
    if references:
        result = _bind_extraction_sources(store,result,references)
    return result | {'media_url':'/api/motion/media/'+result['extraction']+'.mp4'}


def load_example(store, ident):
    manifest = json.loads((EXAMPLES/'manifest.json').read_text())
    example = next((r for r in manifest['examples'] if r['id']==ident),None)
    if example is None:
        raise ValidationError('Unknown packaged native motion example')
    directory = EXAMPLES/ident
    inputs = {}
    for field in ('media','request','reference'):
        raw = (directory/example[field]).read_bytes()
        if digest(raw) != example[field+'_sha256']:
            raise ValidationError('Packaged motion fixture integrity failed')
        inputs[field] = store.put_bytes(raw)
    result = decode(store, inputs['media'])
    result = _bind_extraction_sources(store,result,[inputs['request'],inputs['reference'],store.put_json(example)])
    sequence = store.get_json(result['sequence'])
    sequence['metadata']['source_ids'] += [inputs['request'],inputs['reference'],store.put_json(example)]
    sequence['metadata']['fixture_provenance'] = example['provenance']
    result['sequence'] = store.put_json(sequence)
    return result | {'source_note':example['provenance']}


def prepare(store, *, first_png, prompt, base_dir, last_png=None, duration=4, resolution='768P'):
    first = store.get_bytes(validate_id(first_png), max_bytes=motion_provider.MAX_IMAGE)
    last = store.get_bytes(validate_id(last_png), max_bytes=motion_provider.MAX_IMAGE) if last_png else None
    result = motion_provider.prepare_packet(store, first, prompt, last_png=last,
                                            duration=duration,resolution=resolution)
    run = _run(base_dir,result['packet'])
    if run.exists():
        motion_provider._prepared(store,result['packet'],run)
    else:
        motion_provider.write_prepared(store,result['packet'],run)
    state = motion_provider.packet_status(store,result['packet'],run)
    return state | {'request_sha256':result['request_sha256'],
            'provider':'MiniMax','model':motion_provider.MODEL,'checkpoint':None,
            'duration':duration,'resolution':resolution,'submission_performed':False}


def provider_action(store, method, packet, *, base_dir, enabled=False):
    run = _run(base_dir,packet)
    if method=='status':
        return motion_provider.packet_status(store,packet,run)
    if not enabled:
        raise ValidationError('Native video execution is disabled in this controller; restart with --enable-motion-provider')
    if method=='submit':
        return motion_provider.submit_prepared(store,packet,run,credential_loader=credentials,authorized=True)
    if method=='poll':
        return motion_provider.poll_prepared(store,packet,run,credential_loader=credentials,authorized=True)
    if method=='download':
        result = motion_provider.download_prepared(store,packet,run,authorized=True)
        return result | {'media':result['video']}
    raise ValidationError('Unknown native video action')


def condition(store, sequence, *, output_size, background, palette):
    """Declare optional lossy stages separately, keep raw native evidence intact."""
    from .selection import select_raster, _controls
    from .prepare import nearest_resize
    from .calibrated_palette import remap_rgba,reference_palette,POLICY
    doc = store.get_json(validate_id(sequence))
    sequence_timeline(doc)
    if (not isinstance(output_size,list) or len(output_size)!=2 or
            any(type(x)is not int or not 1<=x<=2048 for x in output_size)):
        raise ValidationError('Conditioning canvas must have two integer sides1..2048')
    if (len(doc['frames']) > MAX_CONDITION_FRAMES or
            output_size[0]*output_size[1]*len(doc['frames']) > MAX_CONDITION_PIXELS):
        raise ValidationError('Condition a deliberately selected clip of at most64 frames/16M pixels')
    if (not isinstance(background,dict) or background.get('method') not in ('keep','recovered-host-selection') or
            set(background)-{'method','seed','tolerance'}):
        raise ValidationError('Declare keep or recovered-host-selection background processing')
    if background['method']=='keep' and set(background)!={'method'}:
        raise ValidationError('Background keep accepts no selector controls')
    if background['method']=='recovered-host-selection':
        if set(background)!={'method','seed','tolerance'}:
            raise ValidationError('Recovered selection needs explicit seed and tolerance')
        _controls(*output_size,background['seed'],background['tolerance'])
    if (not isinstance(palette,dict) or palette.get('method') not in ('keep','calibrated-fixed') or
            set(palette)-{'method','reference_raster'}):
        raise ValidationError('Declare keep or calibrated-fixed palette processing')
    if palette['method']=='keep' and set(palette)!={'method'}:
        raise ValidationError('Palette keep accepts no reference')
    colors = None
    if palette['method']=='calibrated-fixed':
        if set(palette)!={'method','reference_raster'}:
            raise ValidationError('Calibrated fixed palette needs a declared reference raster')
        meta=store.get_json(validate_id(palette['reference_raster']))
        if (meta.get('kind')!='rgba' or type(meta.get('width'))is not int or type(meta.get('height'))is not int
                or not 1<=meta['width']*meta['height']<=512*512):
            raise ValidationError('Fixed-palette reference exceeds the local raster budget')
        colors = reference_palette(store.get_raster(palette['reference_raster']))
    doc, arrays = load_sequence(store,sequence)
    deadline=time.monotonic()+90
    records=[]
    for i,a in enumerate(arrays):
        if time.monotonic()>deadline:
            raise ValidationError('Conditioning exceeded90seconds; completed immutable intermediate artifacts retained')
        resized=nearest_resize(a,*output_size)
        before=store.put_raster(resized)
        selected=None;count=0
        if background['method']=='recovered-host-selection':
            selected=select_raster(store,before,background['seed'],background['tolerance'])
            mask=store.get_raster(selected['mask_raster'])[...,3]>0
            output=resized.copy();output[mask]=0
            if not np.array_equal(resized[~mask],output[~mask]):
                raise ValidationError('Background edit changed unselected RGBA')
            count=int(np.count_nonzero(resized[...,3]!=output[...,3]))
        else:
            output=resized.copy()
        if colors is not None:
            output=remap_rgba(output,colors)
        records.append({'index':i,'source_raster':doc['frames'][i]['raster'],
            'resized_raster':before,'selection':selected['selection'] if selected else None,
            'mask_raster':selected['mask_raster'] if selected else None,
            'output_raster':store.put_raster(output),'alpha_changed_pixels':count,
            'outside_mask_rgba_preserved_before_palette':True,'palette_preserves_all_alpha':True})
    receipt={'kind':'motion-conditioning','version':1,'source_sequence':sequence,
        'settings':{'output_size':output_size,'background':background,'palette':palette},
        'frames':records,'boundary':BOUNDARY,'palette_policy':POLICY if colors is not None else 'unchanged',
        'palette_entries':len(colors) if colors is not None else None,
        'warnings':['This connected seed mask can erase attached dark outlines; inspect every result.',
                    'A fixed palette does not establish neural deflicker or high quality motion.'],
        'visual_acceptance':'unreviewed'}
    ident=store.put_json(receipt)
    result=deepcopy(doc)
    for frame,record in zip(result['frames'],records):
        frame['raster']=record['output_raster']
        frame['pivot']=[frame['pivot'][j]*output_size[j]/doc['canvas'][j] for j in range(2)]
    result['canvas']=output_size
    result['metadata']|={'source_ids':[sequence,ident], 'parent_sequence':sequence,
                        'motion_conditioning':ident,'conditioning_boundary':BOUNDARY}
    meta=result['metadata']
    # Pixel coordinates are transformed uniformly; source geometry is never fitted.
    if 'ground_pivot'in meta:
        meta['ground_pivot']=[meta['ground_pivot'][j]*output_size[j]/doc['canvas'][j]for j in range(2)]
    if 'landmarks'in meta:
        meta['landmarks']=[{k:[p[j]*output_size[j]/doc['canvas'][j]for j in range(2)]for k,p in frame.items()}for frame in meta['landmarks']]
    return {'sequence':store.put_json(result),'conditioning':ident,
            'background_changed_pixels':sum(r['alpha_changed_pixels']for r in records),
            'visual_acceptance':'unreviewed','boundary':BOUNDARY}


def retime(store,sequence,*,holds,roles,loop):
    """Explicit inspection/edit timing; never replace the retained native clock."""
    doc,_=load_sequence(store,sequence);sequence_timeline(doc)
    if doc['metadata'].get('events'):
        raise ValidationError('Retiming existing events needs an explicit event remapping; no silent event loss')
    if (type(loop)is not bool or not isinstance(holds,list)or not isinstance(roles,list)
            or len(holds)!=len(doc['frames']) or len(roles)!=len(holds)):
        raise ValidationError('One exact hold and role per frame plus explicit loop are required')
    durations=[]
    for d,r in zip(holds,roles):
        if (not isinstance(d,list)or len(d)!=2 or any(type(v)is not int or not 1<=v<=9007199254740991 for v in d)
                or not isinstance(r,str)or not r.strip()or len(r)>128):
            raise ValidationError('Invalid authored hold/role')
        t=Fraction(*d)
        if t>3600:raise ValidationError('Authored hold exceeds3600seconds')
        durations.append([t.numerator,t.denominator])
    if sum((Fraction(*d)for d in durations),Fraction())>3600:
        raise ValidationError('Authored timeline exceeds3600seconds')
    decision=store.put_json({'kind':'motion-retime','version':1,'source_sequence':sequence,
        'holds':durations,'roles':roles,'loop':loop,'policy':'Explicit authored inspection timing; original clock retained separately',
        'visual_acceptance':'unreviewed'})
    result=deepcopy(doc)
    for f,d in zip(result['frames'],durations):f['duration']=d
    result['loop']=loop;result['play_count']=0 if loop else 1
    # Source ticks describe the parent, not this authored derivative.
    for key in ('fps','duration_ticks'):result['metadata'].pop(key,None)
    result['metadata']|={'source_ids':[sequence,decision],'parent_sequence':sequence,
        'motion_retime':decision,'roles':roles,'clock_note':'Explicit authored holds; source timeline retained unchanged'}
    return {'sequence':store.put_json(result),'decision':decision,'visual_acceptance':'unreviewed'}

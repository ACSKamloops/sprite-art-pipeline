"""Explicit shared rational-clock composition; distinct from source binary VFX."""
from fractions import Fraction
import numpy as np

from .core import MAX_FRAMES, ValidationError, load_sequence, save_sequence


def source_over(back, front):
    if back.shape != front.shape:
        raise ValidationError('Composite raster dimensions differ')
    d, s = back.astype(np.uint64), front.astype(np.uint64)
    sa, da = s[...,3], d[...,3]
    denominator = sa*255 + da*(255-sa)
    numer = s[...,:3]*sa[...,None]*255+d[...,:3]*da[...,None]*(255-sa[...,None])
    out = back.copy()
    out[...,:3] = ((numer+denominator[...,None]//2)//np.maximum(denominator[...,None],1)).astype(np.uint8)
    out[...,3] = ((denominator+127)//255).astype(np.uint8)
    out[denominator==0] = back[denominator==0]  # Preserve back hiddenRGB explicitly.
    return out


def compose_sequences(store, body, *, back=None, front=None, duration=None, loop=False):
    loaded = {name:load_sequence(store,ident) for name,ident in [('body',body),('back',back),('front',front)] if ident}
    body_doc = loaded['body'][0]
    periods = {}
    for name,(doc,arrays) in loaded.items():
        if doc['canvas'] != body_doc['canvas']:
            raise ValidationError('Composite canvases differ; prepare placement explicitly')
        periods[name] = sum((Fraction(*f['duration']) for f in doc['frames']), Fraction())
    body_plays = body_doc.get('play_count',0 if body_doc['loop'] else 1)
    total = periods['body']*max(body_plays,1) if duration is None else Fraction(*duration) if isinstance(duration,(tuple,list)) else Fraction(duration)
    if total <= 0 or total > 3600:
        raise ValidationError('Invalid composition duration')
    if loop and any(not loaded[n][0]['loop'] or total % p for n,p in periods.items()):
        raise ValidationError('Loop composition requires an explicit common period and looping sources')
    points = {Fraction(),total}
    for name,(doc,arrays) in loaded.items():
        plays = doc.get('play_count',0 if doc['loop'] else 1)
        repeats = int(total/periods[name])+1 if plays==0 else min(plays,int(total/periods[name])+1)
        if repeats*len(arrays)>MAX_FRAMES:
            raise ValidationError('Composite clock exceeds local frame budget')
        for r in range(repeats):
            t = periods[name]*r
            for f in doc['frames']:
                t += Fraction(*f['duration'])
                if 0 < t < total: points.add(t)
    ordered = sorted(points)
    if len(ordered)-1>MAX_FRAMES:
        raise ValidationError('Merged timeline exceeds local frame budget')
    h,w = loaded['body'][1][0].shape[:2]
    empty = np.zeros((h,w,4),np.uint8)
    def at(name,time):
        if name not in loaded: return empty,None
        doc,arrays = loaded[name]; t = time
        plays = doc.get('play_count',0 if doc['loop'] else 1)
        if plays>0 and t >= periods[name]*plays:
            return (arrays[-1],len(arrays)-1) if name=='body' else (empty,None)
        t %= periods[name]
        accumulated = Fraction()
        for i,f in enumerate(doc['frames']):
            accumulated += Fraction(*f['duration'])
            if t < accumulated: return arrays[i],i
        raise ValidationError('Invalid source timeline')
    arrays=[];mapping=[];pivots=[];directions=[]
    for t in ordered[:-1]:
        b,bi = at('body',t);bg,bgi = at('back',t);fg,fgi = at('front',t)
        base = source_over(bg,b) if back is not None else b.copy()
        arrays.append(source_over(base,fg) if front is not None else base)
        mapping.append({'time':[t.numerator,t.denominator],'body_frame':bi,'back_frame':bgi,'front_frame':fgi})
        f = body_doc['frames'][bi]
        pivots.append(f['pivot']);directions.append(f['direction'])
    result = save_sequence(store,arrays,[b-a for a,b in zip(ordered,ordered[1:])],pivots,loop,directions,
        metadata={'method':'straight-alpha-rational-composition-local-v1','sources':{'body':body,'back':back,'front':front},
            'mapping':mapping,'ended_body':'hold-last','ended_nonloop_effect':'transparent',
            'rounding':'integer-half-up','zero_alpha_rgb':'retain-back-hiddenRGB; absent back starts from exactbody',
            'finite_plays':'flatten explicitly into mergedtimeline'})
    return {'sequence':result,'frames':len(arrays),'duration':[total.numerator,total.denominator],
            'status':'candidate_needs_visual_review'}

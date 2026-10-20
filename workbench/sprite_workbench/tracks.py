"""Bake explicit local pose tracks into discrete scene frames; no learned motion."""
from fractions import Fraction
import json
import math
from .core import MAX_FRAMES,ValidationError,canonical_json


def bake_tracks(scene, tracks, *, frame_count, fps, direction='unspecified', pivot=(0,0)):
    tracks = json.loads(canonical_json({'tracks':tracks}))['tracks']
    if type(frame_count) != int or not 1 <= frame_count <= MAX_FRAMES:
        raise ValidationError('Track bake needs1..512frames')
    try: rate = Fraction(str(fps))
    except (ValueError,ZeroDivisionError) as e: raise ValidationError('Invalid explicitfps') from e
    if not 0 < rate <= 240:
        raise ValidationError('Track bake fps must be positive and <=240')
    blueprint = json.loads(canonical_json(scene))
    names = {n['id'] for n in blueprint.get('nodes',[])}
    if not isinstance(tracks,list) or len(tracks)>128:
        raise ValidationError('Tracks must be a bounded list')
    supported = {'position','anchor','rotation_degrees','scale','z','visible','raster','mask','ownership'}
    seen=set();normalized=[]
    for track in tracks:
        if not isinstance(track,dict) or set(track)-{'node','property','keys','interpolation'}:
            raise ValidationError('Invalid track fields')
        node,prop=track.get('node'),track.get('property')
        if node not in names or prop not in supported or (node,prop) in seen:
            raise ValidationError('Track target is missing/unsupported/duplicated')
        seen.add((node,prop));mode=track.get('interpolation','linear')
        if mode not in ('hold','linear','smoothstep'):
            raise ValidationError('Unknown local interpolation method')
        if prop in ('z','visible','raster','mask','ownership') and mode!='hold':
            raise ValidationError('Discrete track properties require hold interpolation')
        keys=track.get('keys')
        if not isinstance(keys,list) or not 1<=len(keys)<=512:
            raise ValidationError('Track requires1..512explicit keys')
        parsed=[]
        for key in keys:
            if not isinstance(key,dict) or set(key)!={'time','value'}:
                raise ValidationError('Key requires exact time/value')
            time=key['time']
            try:t=Fraction(*time) if isinstance(time,list) else Fraction(str(time))
            except (TypeError,ValueError,ZeroDivisionError) as e: raise ValidationError('Invalid key clock') from e
            if t<0 or parsed and t<=parsed[-1][0]:raise ValidationError('Keys must have strictly increasing nonnegative clocks')
            value=json.loads(canonical_json({'value':key['value']}))['value']
            if prop in ('position','anchor','scale'):
                if not isinstance(value,list) or len(value)!=2 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in value):
                    raise ValidationError('Vector track values require2finite numbers')
            elif prop=='rotation_degrees' and (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value)):
                raise ValidationError('Rotation track value must be finite')
            parsed.append((t,value))
        normalized.append((node,prop,mode,parsed))
    def sample(mode,keys,t):
        if t<=keys[0][0]:return keys[0][1]
        if t>=keys[-1][0]:return keys[-1][1]
        for (a,va),(b,vb) in zip(keys,keys[1:]):
            if a<=t<b:
                if mode=='hold':return va
                u=float((t-a)/(b-a))
                if mode=='smoothstep':u=u*u*(3-2*u)
                return [x+(y-x)*u for x,y in zip(va,vb)] if isinstance(va,list) else va+(vb-va)*u
        raise ValidationError('Unresolvable track clock')
    frames=[]
    for index in range(frame_count):
        overrides={}
        for node,prop,mode,keys in normalized:
            overrides.setdefault(node,{})[prop]=json.loads(canonical_json({'value':sample(mode,keys,Fraction(index)/rate)}))['value']
        hold=1/rate
        frames.append({'duration':[hold.numerator,hold.denominator],'direction':direction,'pivot':list(pivot),'nodes':overrides})
    blueprint['frames']=frames
    return blueprint, {'method':'explicit-track-bake-local-v1','tracks':tracks,'fps':[rate.numerator,rate.denominator],
        'frame_count':frame_count,'sampling':'zero-basedframe-start','rotation':'unwrappeddegrees','endpoint_policy':'clamp; add an explicit final hold frame when needed'}

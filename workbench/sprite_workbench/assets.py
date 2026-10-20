"""Supplied UI pieces, local font glyphs and explicitly mapped viseme timelines.

No font/style/mouth model is inferred. Rasterization defaults to the installed Pillow
font stack, with explicit optional unhinted FreeType; neither mode claims vendor
font construction or typography.
"""
from __future__ import annotations

from fractions import Fraction
from io import BytesIO
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .core import ValidationError, UnsupportedCapability, validate_raster, save_sequence, digest
from .prepare import nearest_resize


def virtual_view(width, height):
    if any(type(v)!=int or v<=0 for v in (width,height)):
        raise ValidationError("View dimensions must be positive integers")
    # Positive half-up rounding is explicit (Python round uses ties-to-even).
    if width >= height: return [512, math.floor(512*height/width+.5)]
    return [math.floor(512*width/height+.5), 512]


def layout_shapes(pieces, source_view, destination_view, *, profile="geometric-radius-local-v1"):
    """Transform numeric UI primitives in virtual coordinates, not output pixels.

    Geometric radius follows Godot add/example and aspect-change branches; web
    example load uses min-axis radius. Snapping/ID assignment is separate and
    is not implied. All pieces retain their explicit IDs and list ordering.
    """
    if profile not in ("geometric-radius-local-v1", "web-example-min-radius-v1"):
        raise ValidationError("Unknown layout profile")
    for size in (source_view, destination_view):
        if len(size)!=2 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in size):
            raise ValidationError("View requires two positive finite dimensions")
    sx,sy = destination_view[0]/source_view[0],destination_view[1]/source_view[1]
    sr = math.sqrt(sx*sy) if profile=="geometric-radius-local-v1" else min(sx,sy)
    out,ids = [],set()
    for piece in pieces:
        p = dict(piece)
        if not isinstance(p.get("id"),str) or not p["id"] or p["id"] in ids:
            raise ValidationError("UI piece IDs must be distinct nonempty strings")
        ids.add(p["id"])
        if p.get("type") not in ("rect", "rounded_rect", "circle", "polygon"):
            raise ValidationError("Unsupported supplied UI primitive")
        fields = ("x","y","w","h") if p["type"] in ("rect","rounded_rect") else ("x","y","r")
        if any(k not in p for k in fields): raise ValidationError("UI primitive is missing coordinates")
        for key in (*fields, *(('radius',) if p["type"]=="rounded_rect" else ())):
            v=p.get(key)
            if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v):
                raise ValidationError("UI coordinates must be finite")
            if key in ("w","h","r","radius") and v<0: raise ValidationError("UI extents cannot be negative")
            p[key]=v*(sx if key in ("x","w") else sy if key in ("y","h") else sr)
        if p["type"]=="polygon":
            if type(p.get("sides"))!=int or not 3<=p["sides"]<=256: raise ValidationError("Polygon sides must be3..256")
            phase=p.get("phase",0)
            if isinstance(phase,bool) or not isinstance(phase,(int,float)) or not math.isfinite(phase): raise ValidationError("Polygon phase must be finite radians")
            p["phase"]=phase
        out.append(p)
    return {"pieces":out,"source_view":list(source_view),"view":list(destination_view),
            "profile":profile,"axis_scale":[sx,sy],"radius_scale":sr,"units":"virtual-view"}


def render_ui(store, pieces, canvas_size, *, metadata=None):
    """Place supplied raster pieces at explicit integer rects; ordered overwrite.

    This local pixel-space policy is separate from the private virtual-to-raster
    UI generation transform. Nearest stretch is declared, never neural styling.
    """
    w,h=canvas_size
    if any(type(v)!=int or v<1 for v in (w,h)) or w*h>16_777_216: raise ValidationError("Invalid UI canvas")
    canvas=np.zeros((h,w,4),np.uint8); records=[]
    for p in pieces:
        rect=p.get("rect",[])
        if len(rect)!=4 or any(type(v)!=int for v in rect): raise ValidationError("UI pixel rect must have four integers")
        x,y,pw,ph=rect
        if min(x,y)<0 or min(pw,ph)<1 or x+pw>w or y+ph>h: raise ValidationError("UI piece exceeds canvas")
        a=store.get_raster(p["raster"])
        canvas[y:y+ph,x:x+pw]=nearest_resize(a,pw,ph)
        records.append({"raster":p["raster"],"rect":rect,"mode":"nearest-rgba-overwrite-local-v1"})
    return save_sequence(store,[canvas],metadata={"method":"supplied-ui-v1","placements":records,**(metadata or {})})


def build_glyph_atlas(store, glyphs, *, columns=16, gap=1):
    """Pack explicit glyph raster/bearing/advance records into fixed-size cells.

    Cell size is max supplied width/height; baseline and advance remain explicit
    metrics, not inferred from alpha bounds. Missing glyph coverage is an error
    in render_text unless an explicit fallback glyph is supplied.
    """
    if not glyphs or type(columns)!=int or columns<1 or type(gap)!=int or gap<0:
        raise ValidationError("Invalid glyph packing parameters")
    entries=[]
    for character,g in glyphs.items():
        if not isinstance(character,str) or len(character)!=1: raise ValidationError("Glyph key must be one Unicode code point")
        a=validate_raster(g["array"])
        bearing=g.get("bearing",[0,0]); advance=g.get("advance")
        if len(bearing)!=2 or any(type(v)!=int for v in bearing): raise ValidationError("Glyph bearing must be integer x,y")
        if isinstance(advance,bool) or not isinstance(advance,(float,int)) or not math.isfinite(advance) or advance<0:
            raise ValidationError("Glyph advance must be nonnegative finite number")
        entries.append((character,g,a))
    cw=max(a.shape[1] for _,_,a in entries)+gap; ch=max(a.shape[0] for _,_,a in entries)+gap
    rows=(len(entries)+columns-1)//columns
    if columns*cw*rows*ch>16_777_216: raise ValidationError("Font atlas exceeds pixel budget")
    atlas=np.zeros((rows*ch,columns*cw,4),np.uint8); records={}
    for i,(char,g,a) in enumerate(entries):
        x,y=i%columns*cw,i//columns*ch; h,w=a.shape[:2]
        atlas[y:y+h,x:x+w]=a
        records[char]={"rect":[x,y,w,h],"bearing":list(g.get("bearing",[0,0])),"advance":g["advance"],"raster":store.put_raster(a)}
    return store.put_json({"kind":"font-atlas","version":1,"atlas":store.put_raster(atlas),"glyphs":records,
                           "cell_size":[cw,ch],"columns":columns,"gap":gap,"capability":"supplied-art"})


def rasterize_font(path, characters, *, size=16, color=(255,255,255,255), mode="pillow", timeout=10):
    """Explicit local font-file adapter; no downloads or name-based discovery."""
    if isinstance(path,bytes):raw_font=path
    else:
        try: path=Path(path)
        except (TypeError,ValueError) as exc: raise ValidationError("Explicit font input must be bytes or a file path") from exc
        if not path.is_file(): raise ValidationError("Explicit font file is missing")
        if path.stat().st_size>32*1024*1024:raise ValidationError('Local font input exceeds32MiB')
        raw_font=path.read_bytes()
    if len(raw_font)>32*1024*1024:raise ValidationError('Local font input exceeds32MiB')
    if not isinstance(characters,(str,list,tuple)) or not 1<=len(characters)<=4096:
        raise ValidationError('Explicit glyph coverage must contain1..4096code points')
    if type(size)!=int or not 1<=size<=512: raise ValidationError("Font size must be1..512")
    if not isinstance(color,(list,tuple)) or len(color)!=4 or any(type(v)!=int or not 0<=v<=255 for v in color): raise ValidationError("Color must be RGBA bytes")
    if any(not isinstance(char,str) or len(char)!=1 or 0xD800<=ord(char)<=0xDFFF for char in characters):
        raise ValidationError("Coverage must contain Unicode scalar code points")
    characters=list(dict.fromkeys(characters))
    if mode not in ('pillow','freetype-no-hinting'):
        raise ValidationError('Font mode must be pillow or freetype-no-hinting')
    if mode=='freetype-no-hinting':
        from .font_native import rasterize_unhinted
        return rasterize_unhinted(raw_font,characters,size,color,timeout=timeout)
    try: font=ImageFont.truetype(BytesIO(raw_font),size)
    except (OSError,ValueError) as e: raise ValidationError("Unsupported local font file") from e
    glyphs={};pixels=0
    for char in dict.fromkeys(characters):
        if not isinstance(char,str) or len(char)!=1: raise ValidationError("Coverage must contain Unicode code points")
        x0,y0,x1,y1=font.getbbox(char,anchor="ls")
        pixels+=max(x1-x0,1)*max(y1-y0,1)
        if pixels>16_777_216:raise ValidationError('Glyph rasters exceed local pixel budget')
        image=Image.new("RGBA",(max(x1-x0,1),max(y1-y0,1)))
        ImageDraw.Draw(image).text((-x0,-y0),char,font=font,fill=color,anchor="ls")
        glyphs[char]={"array":np.array(image,dtype=np.uint8),"bearing":[x0,y0],"advance":font.getlength(char)}
    return glyphs,{"method":"pillow-explicit-font-v1","font_sha256":digest(raw_font),"size":size,"coverage":list(glyphs)}


def render_text(store, atlas_id, text, canvas_size, *, baseline=(0,0), fallback=None):
    atlas=store.get_json(atlas_id)
    if atlas.get("kind")!="font-atlas": raise ValidationError("Expected font atlas")
    if not isinstance(text,str): raise ValidationError("Text must be a string")
    w,h=canvas_size
    if any(type(v)!=int or v<=0 for v in (w,h)) or w*h>16_777_216: raise ValidationError("Invalid text canvas")
    if len(baseline)!=2 or any(type(v)!=int for v in baseline): raise ValidationError("Baseline must be integer x,y")
    out=np.zeros((h,w,4),np.uint8); x,y=baseline; placements=[]
    for char in text:
        key=char if char in atlas["glyphs"] else fallback
        if key not in atlas["glyphs"]: raise ValidationError(f"Missing explicit glyph coverage: {char!r}")
        g=atlas["glyphs"][key]; a=store.get_raster(g["raster"]); gh,gw=a.shape[:2]
        px,py=math.floor(x)+g["bearing"][0],y+g["bearing"][1]
        if px<0 or py<0 or px+gw>w or py+gh>h: raise ValidationError("Text glyph exceeds canvas")
        # Local straight-alpha source-over; transparent glyph cells don't erase
        # previously placed ink. Glyph metadata/pixels themselves remain exact.
        dest=out[py:py+gh,px:px+gw].astype(np.float64)/255; src=a.astype(np.float64)/255
        alpha=src[...,3:4]+dest[...,3:4]*(1-src[...,3:4])
        premul=src[...,:3]*src[...,3:4]+dest[...,:3]*dest[...,3:4]*(1-src[...,3:4])
        rgb=np.divide(premul,alpha,out=np.zeros_like(premul),where=alpha!=0)
        out[py:py+gh,px:px+gw]=np.floor(np.concatenate((rgb,alpha),axis=2)*255+.5).astype(np.uint8)
        placements.append({"character":char,"glyph":key,"origin":[px,py],"advance":g["advance"]});x+=g["advance"]
    return save_sequence(store,[out],metadata={"method":"supplied-glyph-text-v1","font_atlas":atlas_id,"text":text,"placements":placements})


def save_viseme_timeline(store, text, visemes, letter_map, durations, *, fallback=None, direction="unspecified"):
    """One supplied frame per explicit code point; duplicate holds are retained.

    Letter mapping/durations are caller data, not speech recognition, phoneme
    synthesis or the vendor's remote plan. Case and whitespace are significant.
    """
    if not isinstance(text,str) or not text: raise ValidationError("Timeline text must be nonempty")
    durations=list(durations)
    if len(durations)!=len(text): raise ValidationError("Letter duration count differs")
    arrays=[]; symbols=[]
    for char in text:
        symbol=letter_map.get(char,fallback)
        if symbol not in visemes: raise ValidationError(f"Missing supplied viseme for {char!r}")
        value=visemes[symbol]
        arrays.append(store.get_raster(value) if isinstance(value,str) else validate_raster(value))
        symbols.append(symbol)
    return save_sequence(store,arrays,durations,directions=[direction]*len(text),
                         metadata={"method":"supplied-letter-visemes-v1","text":text,"symbols":symbols,"letter_map":dict(letter_map),
                            "fallback":fallback,"viseme_rasters":{k:value if isinstance(value,str) else store.put_raster(value) for k,value in visemes.items()},"capability":"supplied-art"})


def generate_asset(capability, *args, **kwargs):
    raise UnsupportedCapability(capability, "Only supplied UI/glyph/viseme art and explicit local font-file rasterization are implemented")

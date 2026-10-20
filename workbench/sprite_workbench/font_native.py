"""Optional subprocess FreeType adapter with uniform no-hinting flags.

Requires a local C compiler, pkg-config, FreeType development files. Nothing is
installed, downloaded or executed in process; the native rasterizer has memory,
CPU, glyph and output limits and the parent enforces a wall-clock deadline.
"""
import math
from pathlib import Path
import shlex
import shutil
import struct
import subprocess
import tempfile
import time

import numpy as np
from .core import ValidationError, UnsupportedCapability, digest

CAPABILITY='local.font.freetype-no-hinting'
MAX_PIXELS=16_777_216


def _tools():
    cc=shutil.which('cc');pkg=shutil.which('pkg-config')
    if not cc or not pkg:
        raise UnsupportedCapability(CAPABILITY,'Optional mode requires local cc, pkg-config and FreeType development files; default Pillow remains available')
    return cc,pkg


def rasterize_unhinted(raw_font,characters,size,color,*,timeout=10):
    if isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or not math.isfinite(timeout) or not .05<=timeout<=15:
        raise ValidationError('Native font timeout must be finite0.05..15seconds')
    cc,pkg=_tools();started=time.monotonic();deadline=started+timeout
    def run(argv):
        remaining=deadline-time.monotonic()
        if remaining<=0:raise ValidationError('Native font wall-clock budget exceeded')
        try:return subprocess.run(argv,check=False,capture_output=True,timeout=remaining)
        except subprocess.TimeoutExpired as e:raise ValidationError('Native font wall-clock budget exceeded') from e
        except OSError as e:raise UnsupportedCapability(CAPABILITY,'Optional native font tool could not start') from e
    flags=run([pkg,'--cflags','--libs','freetype2'])
    if flags.returncode:
        raise UnsupportedCapability(CAPABILITY,'Optional mode requires locally installed FreeType headers/library discoverable by pkg-config')
    source=Path(__file__).resolve().parent/'native/font_unhinted.c'
    with tempfile.TemporaryDirectory(prefix='sprite-font-') as folder:
        dest=Path(folder);font=dest/'source.ttf';codes=dest/'codepoints.txt';exe=dest/'rasterize'
        font.write_bytes(raw_font);codes.write_text('\n'.join(str(ord(c)) for c in characters)+'\n')
        compile_result=run([cc,'-O2','-Wall','-Wextra','-Werror',str(source),*shlex.split(flags.stdout.decode()),'-o',str(exe)])
        if compile_result.returncode:
            raise UnsupportedCapability(CAPABILITY,'Optional native font helper could not compile against installed FreeType; no fallback was substituted')
        result=run([str(exe),str(font),str(size),str(codes),str(len(characters))])
    if result.returncode:
        if result.returncode==3:raise ValidationError('Unsupported local font file')
        if result.returncode==6:raise ValidationError('Native glyph rasters exceed local pixel/dimension budget')
        raise ValidationError('Native font rasterization failed or exceeded process resource budget')
    raw=result.stdout
    if not raw.startswith(b'SWFT1\n') or len(raw)>MAX_PIXELS+4096*24+26:
        raise ValidationError('Invalid native font output protocol')
    try:
        major,minor,patch,load_flags,count=struct.unpack_from('<5I',raw,6);offset=26
        if count!=len(characters) or load_flags!=32774:raise ValueError
        glyphs={};pixels=0
        for char in characters:
            cp,w,h,left,top,advance=struct.unpack_from('<IIIiii',raw,offset);offset+=24
            if cp!=ord(char) or not 1<=w<=4096 or not 1<=h<=4096 or advance<0:raise ValueError
            pixels+=w*h
            if pixels>MAX_PIXELS or offset+w*h>len(raw):raise ValueError
            alpha=np.frombuffer(raw,np.uint8,count=w*h,offset=offset).reshape(h,w);offset+=w*h
            image=np.empty((h,w,4),np.uint8);image[:,:,:3]=color[:3]
            image[:,:,3]=((alpha.astype(np.uint16)*color[3]+127)//255).astype(np.uint8)
            # Match supplied-art convention: transparent pixels carry zero RGB.
            image[image[:,:,3]==0]=0
            glyphs[char]={'array':image,'bearing':[left,top],'advance':advance/64}
        if offset!=len(raw):raise ValueError
    except (ValueError,struct.error,OverflowError) as e:
        raise ValidationError('Invalid native font output protocol') from e
    return glyphs,{'method':'freetype-no-hinting-v1','font_sha256':digest(raw_font),'size':size,'coverage':list(characters),
        'freetype_version':f'{major}.{minor}.{patch}','load_flags':load_flags,
        'load_flag_names':['FT_LOAD_RENDER','FT_LOAD_NO_HINTING','FT_LOAD_NO_AUTOHINT'],
        'helper_sha256':digest(source.read_bytes()),'elapsed_seconds':time.monotonic()-started,
        'pixel_count':pixels,'glyph_count':count,'wall_clock_budget_seconds':timeout,
        'glyph_metrics':{char:{'size':[g['array'].shape[1],g['array'].shape[0]],
            'bearing':g['bearing'],'advance':g['advance'],
            'rgba_sha256':digest(g['array'].tobytes()),
            'visible_pixels':int(np.count_nonzero(g['array'][:,:,3])),
            'alpha_values':np.unique(g['array'][:,:,3]).tolist()} for char,g in glyphs.items()},
        'process_limits':{'address_space_bytes':512*1024*1024,'cpu_seconds':10},
        'boundary':'Explicit local rasterization; no target private font construction or typography equivalence'}

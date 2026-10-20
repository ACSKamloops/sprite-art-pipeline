"""Bounded RGBA ASE adapter; official aseprite/docs/ase-file-specs.md.

Pinned original hashes live in TOOLKIT-ORIGIN.json. Local safety changes cap
native bytes, output inflation and aggregate raw/full-canvas cel work. Tick,
source/index/alias metadata lives in a sidecar, not millisecond inference.
"""
import copy
import hashlib
import math
import os
from pathlib import Path
import stat
import struct
import zlib
from PIL import Image
from .core import validate_project,render_cel,project_hash,require
from .canonical import canonical_json,content_hash
from .loading import load_json

MAX_ASE_BYTES=64*1024*1024
MAX_SIDECAR_BYTES=16*1024*1024
MAX_PIXEL_WORK=64_000_000
MAX_FRAMES=512
MAX_LAYERS=128


def bounded_read(path,limit):
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
    with os.fdopen(fd,'rb') as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode),'ASE input must be a regular file')
        data=stream.read(limit+1)
    require(len(data)<=limit,'ASE/sidecar byte limit')
    return data



def bounded_metadata(value):
    """Iterative depth/node check before recursive canonicalization; no fanout stack."""
    stack=[(iter((value,)),0)];nodes=0
    while stack:
        iterator,depth=stack[-1]
        try:item=next(iterator)
        except StopIteration:
            stack.pop();continue
        nodes+=1
        require(nodes<=MAX_SIDECAR_BYTES and depth<=64,'ASE metadata JSON depth/node limit')
        if isinstance(item,dict):
            require(all(isinstance(k,str) for k in item),'ASE metadata string keys required')
            stack.append((iter(item.values()),depth+1))
        elif isinstance(item,list):stack.append((iter(item),depth+1))
    return value


def load_sidecar(data):
    try:value=load_json(data.decode('utf-8'))
    except RecursionError as error:raise ValueError('ASE metadata JSON recursion limit') from error
    return bounded_metadata(value)


def _snapshot(path,data,limit):
    if data is None:return bounded_read(path,limit)
    require(isinstance(data,bytes) and len(data)<=limit,'Invalid/big native input snapshot')
    return data


def _chunk(kind,payload):return struct.pack('<IH',len(payload)+6,kind)+payload

def _string(value):
    encoded=value.encode('utf-8');require(len(encoded)<=65535,'ASE string too long')
    return struct.pack('<H',len(encoded))+encoded


def export_aseprite(project,path,animation_id=None,sidecar=None):
    validate_project(project);path=Path(path)
    sidecar=Path(sidecar) if sidecar else Path(str(path)+'.sprite-lab.json')
    anim=next((a for a in project['animations'] if a['id']==animation_id),None) if animation_id else (project['animations'][0] if project['animations'] else None)
    require(anim is not None,'Animation selection required')
    byid={f['id']:f for f in project['frames']};frames=[byid[i] for i in anim['frames']]
    w=project['canvas']['width'];h=project['canvas']['height']
    require(w<=65535 and h<=65535 and 1<=len(frames)<=MAX_FRAMES and 1<=len(project['layers'])<=MAX_LAYERS,'ASE local dimension/frame/layer bound')
    require(len({l['name'] for l in project['layers']})==len(project['layers']),'ASE duplicate layer names are ambiguous')
    require(w*h*len(frames)*len(project['layers'])*2<=MAX_PIXEL_WORK,'ASE aggregate pixel work limit')
    output=[];timing=[];elapsed_ticks=0;previous_boundary=0;total_bytes=128
    for fi,frame in enumerate(frames):
        elapsed_ticks+=frame['duration_ticks']
        value=elapsed_ticks*1000/anim['fps']
        require(math.isfinite(value) and value<=65535*len(frames)+.5,'ASE clock outside representable milliseconds')
        boundary=math.floor(value+.5)
        ms=boundary-previous_boundary;previous_boundary=boundary
        require(1<=ms<=65535,'ASE millisecond duration is not representable')
        timing.append({'frame_id':frame['id'],'duration_ticks':frame['duration_ticks'],'milliseconds':ms,
            'quantization_error_ms':ms-frame['duration_ticks']*1000/anim['fps'],
            'cumulative_boundary_error_ms':boundary-elapsed_ticks*1000/anim['fps']})
        chunks=[]
        if fi==0:
            for layer in project['layers']:
                flags=1|(4 if layer['locked'] else 2)
                chunks.append(_chunk(0x2004,struct.pack('<6HB3x',flags,0,0,w,h,0,255)+_string(layer['name'])))
        for li,layer in enumerate(project['layers']):
            if layer['id'] not in frame['cels']:continue
            im=render_cel(project,frame['cels'][layer['id']])
            chunks.append(_chunk(0x2005,struct.pack('<HhhBHh5xHH',li,0,0,255,2,0,w,h)+zlib.compress(im.tobytes(),9)))
        payload=b''.join(chunks);total_bytes+=len(payload)+16
        require(total_bytes<=MAX_ASE_BYTES,'ASE output byte limit')
        output.append(struct.pack('<IHHH2xI',len(payload)+16,0xf1fa,len(chunks),ms,len(chunks))+payload)
    data=b''.join(output);header=bytearray(128)
    struct.pack_into('<IHHHHHIH',header,0,len(data)+128,0xa5e0,len(frames),w,h,32,1,timing[0]['milliseconds'])
    header[34:36]=b'\x01\x01';native=bytes(header)+data
    metadata={'schema':'sprite-edit-ase-sidecar/v1','format_source':'https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md',
        'project':project,'project_sha256':project_hash(project),'animation_id':anim['id'],'sequence':anim['frames'],'timing':timing,
        'millisecond_clock':'Cumulative boundary rounding; original ticks remain authoritative',
        'ase_sha256':hashlib.sha256(native).hexdigest(),
        'bounds':'RGBA normal layers/cropped or linked cels; no groups/blend modes/opacity transforms. Original ticks/events/pivots remain authoritative. Changed tool durations require explicit timing edits.'}
    meta_bytes=(canonical_json(metadata)+'\n').encode('utf-8')
    require(len(meta_bytes)<=MAX_SIDECAR_BYTES,'ASE sidecar byte limit')
    path.write_bytes(native);sidecar.write_bytes(meta_bytes)
    return metadata



def _validate_palette(kind,b):
    # Only the two harmless optional RGBA palette chunks observed in LibreSprite1.3.
    # Official ASE spec: palettes optional above8bpp; pixel data remains explicit RGBA.
    if kind==0x0004:
        require(len(b)>=2,'Truncated optional old palette')
        packets=struct.unpack_from('<H',b)[0];pos=2;entry=0
        require(packets<=256,'Old palette packet bound')
        for _ in range(packets):
            require(pos+2<=len(b),'Truncated optional palette packet')
            skip,count=b[pos:pos+2];count=count or 256;pos+=2;entry+=skip+count
            require(entry<=256 and pos+count*3<=len(b),'Invalid optional old palette entries')
            pos+=count*3
    else:
        require(len(b)>=20,'Truncated optional palette')
        total,first,last=struct.unpack_from('<III',b);pos=20
        require(0<=first<=last<total<=65536,'Optional palette entry bound')
        for _ in range(last-first+1):
            require(pos+6<=len(b),'Truncated optional palette entry')
            flags=struct.unpack_from('<H',b,pos)[0];pos+=6
            require(flags in (0,1),'Unknown optional palette flags')
            if flags:
                require(pos+2<=len(b),'Truncated palette name')
                size=struct.unpack_from('<H',b,pos)[0];pos+=2
                require(pos+size<=len(b),'Truncated palette name bytes')
                b[pos:pos+size].decode('utf-8');pos+=size
    require(pos==len(b),'Unexpected optional palette bytes')


def read_aseprite(path,*,data=None):
    data=_snapshot(path,data,MAX_ASE_BYTES)
    require(len(data)>=128,'Truncated ASE header')
    size,magic,count,w,h,depth=struct.unpack_from('<IHHHHH',data)
    require(size==len(data) and magic==0xa5e0 and depth==32,'Unsupported ASE header/depth')
    require(struct.unpack_from('<I',data,14)[0] in (0,1) and all(v in (0,1) for v in data[34:36]),'Unsupported ASE header group/UUID flags or pixel ratio')
    require(1<=count<=MAX_FRAMES and w>0 and h>0 and w*h<=16777216,'ASE canvas/frame bound')
    require(w*h*count*2<=MAX_PIXEL_WORK,'ASE aggregate canvas work limit')
    layers=[];frames=[];offset=128;work=0;ignored=[]
    for fi in range(count):
        require(offset+16<=len(data),'Truncated frame')
        length,magic,oldcount,ms,newcount=struct.unpack_from('<IHHH2xI',data,offset)
        require(magic==0xf1fa and length>=16 and offset+length<=len(data) and ms>0,'Invalid ASE frame')
        pos=offset+16;end=offset+length;cels={};raw_cels={};chunks=newcount or oldcount
        require(chunks<=(end-pos)//6,'Invalid ASE chunk count')
        for _ in range(chunks):
            require(pos+6<=end,'Truncated chunk')
            chunklen,kind=struct.unpack_from('<IH',data,pos)
            require(chunklen>=6 and pos+chunklen<=end,'Invalid chunk')
            b=data[pos+6:pos+chunklen]
            if kind==0x2004:
                require(fi==0 and len(b)>=18,'Late/truncated layer')
                flags,layer_type,child,_,_,blend,opacity=struct.unpack_from('<6HB',b)
                n=struct.unpack_from('<H',b,16)[0]
                require(layer_type==0 and child==0 and blend==0 and opacity==255 and flags&1 and not flags&~0x17 and len(b)==18+n,'Unsupported layer structure/blend/flags')
                name=b[18:18+n].decode('utf-8')
                require(len(layers)<MAX_LAYERS and name not in [l['name'] for l in layers],'ASE duplicate/excess layers')
                require(w*h*count*(len(layers)+1)*2<=MAX_PIXEL_WORK,'ASE aggregate layer/canvas work limit')
                layers.append({'name':name,'flags':flags})
            elif kind==0x2005:
                require(len(b)>=16,'Truncated cel')
                li,x,y,opacity,celtype,zindex=struct.unpack_from('<HhhBHh',b)
                require(li<len(layers) and opacity==255 and zindex==0 and li not in cels and not any(b[11:16]),'Unsupported cel layer/opacity/order/reserved semantics')
                if celtype==1:
                    require(len(b)>=18,'Truncated linked cel')
                    linked=struct.unpack_from('<H',b,16)[0]
                    require(linked<fi and li in frames[linked]['cels'],'Invalid linked cel')
                    source=frames[linked]['raw_cels'][li];cw,ch=source.size
                elif celtype in (0,2):
                    require(len(b)>=20,'Truncated image cel')
                    cw,ch=struct.unpack_from('<HH',b,16)
                else:raise ValueError('Unsupported cel type')
                require(cw>0 and ch>0 and cw*ch<=16777216 and x>=0 and y>=0 and x+cw<=w and y+ch<=h,'Cel outside canvas/size limit')
                work+=w*h+cw*ch
                require(work<=MAX_PIXEL_WORK,'ASE aggregate decoded/link/fullcanvas work limit')
                if celtype==1:image=source.copy()
                else:
                    expected=cw*ch*4
                    if celtype==2:
                        decoder=zlib.decompressobj();raw=decoder.decompress(b[20:],expected+1)
                        require(len(raw)==expected and decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data,'Invalid/big/trailing compressed RGBA payload')
                    else:raw=b[20:]
                    require(len(raw)==expected,'Invalid RGBA payload')
                    image=Image.frombytes('RGBA',(cw,ch),raw)
                raw_cels[li]=image;full=Image.new('RGBA',(w,h));full.paste(image,(x,y));cels[li]=full
            elif kind in (0x0004,0x2019):
                _validate_palette(kind,b)
                ignored.append({'frame':fi,'kind':kind,'bytes':chunklen,'reason':'Optional palette metadata is not used for RGBA32 pixel lookup'})
            else:
                raise ValueError('Unsupported ASE chunk type '+hex(kind))
            pos+=chunklen
        require(pos==end,'Unexpected frame bytes')
        frames.append({'milliseconds':ms,'cels':cels,'raw_cels':raw_cels});offset=end
    require(offset==len(data) and bool(layers),'Invalid layer/end')
    return {'width':w,'height':h,'layers':layers,'frames':frames,'ignored_chunks':ignored}


def import_aseprite(path,sidecar=None,*,native_data=None,sidecar_data=None):
    sidecar=Path(sidecar) if sidecar else Path(str(path)+'.sprite-lab.json')
    raw_sidecar=_snapshot(sidecar,sidecar_data,MAX_SIDECAR_BYTES)
    meta=load_sidecar(raw_sidecar)
    require(isinstance(meta,dict) and meta.get('schema')=='sprite-edit-ase-sidecar/v1','Invalid ASE sidecar')
    project=copy.deepcopy(meta['project']);require(project_hash(project)==meta['project_sha256'],'Stale sidecar project')
    anim=next((a for a in project['animations'] if a['id']==meta.get('animation_id')),None)
    require(anim is not None and meta['sequence']==anim['frames'],'ASE sidecar animation/sequence mismatch')
    require(len(anim['frames'])<=MAX_FRAMES and len(project['layers'])<=MAX_LAYERS,'ASE sidecar frame/layer work bound')
    require(project['canvas']['width']*project['canvas']['height']*len(anim['frames'])*max(len(project['layers']),1)*2<=MAX_PIXEL_WORK,'ASE sidecar aggregate work bound')
    byid={f['id']:f for f in project['frames']};expected_timing=[];elapsed=0;previous=0
    for fid in anim['frames']:
        elapsed+=byid[fid]['duration_ticks'];value=elapsed*1000/anim['fps']
        require(math.isfinite(value) and value<=65535*len(anim['frames'])+.5,'ASE source clock outside representable milliseconds')
        boundary=math.floor(value+.5)
        expected_timing.append((fid,byid[fid]['duration_ticks'],boundary-previous));previous=boundary
    require(isinstance(meta.get('timing'),list) and len(meta['timing'])==len(expected_timing),'ASE sidecar timing structure')
    require(all(isinstance(row,dict) and type(row.get('duration_ticks')) is int and type(row.get('milliseconds')) is int and (row.get('frame_id'),row.get('duration_ticks'),row.get('milliseconds'))==expected for row,expected in zip(meta['timing'],expected_timing)),'ASE sidecar timing differs from original clock')
    ase=read_aseprite(path,data=native_data)
    require((ase['width'],ase['height'])==(project['canvas']['width'],project['canvas']['height']),'ASE resized canvas')
    require([x['name'] for x in ase['layers']]==[x['name'] for x in project['layers']],'ASE renamed/reordered layers')
    require(len(ase['frames'])==len(meta['sequence']),'ASE changed frame structure')
    mapping={tuple(c):i for i,c in reversed(list(enumerate(project['palette'])))};changes={}
    for fi,external in enumerate(ase['frames']):
        require(external['milliseconds']==meta['timing'][fi]['milliseconds'],'ASE changed quantized timing')
        frame=byid[meta['sequence'][fi]]
        for li,layer in enumerate(project['layers']):
            image=external['cels'].get(li)
            if image is None:image=Image.new('RGBA',(ase['width'],ase['height']))
            oldid=frame['cels'].get(layer['id']);old=project['cels'][oldid]['pixels'] if oldid else [0]*(ase['width']*ase['height']);pixels=[]
            for i,color in enumerate(image.getdata()):
                if tuple(project['palette'][old[i]])==color:index=old[i]
                else:
                    if color not in mapping:mapping[color]=len(project['palette']);project['palette'].append(list(color))
                    index=mapping[color]
                pixels.append(index)
            key=(frame['id'],layer['id']);require(key not in changes or changes[key]==pixels,'Repeated animation frame edited inconsistently');changes[key]=pixels
            if pixels!=old:
                require(not layer['locked'],'ASE changes locked layer')
                newid='ase:'+frame['id']+':'+layer['id']+':'+content_hash(pixels)[:12]
                project['cels'][newid]={'layer_id':layer['id'],'pixels':pixels};frame['cels'][layer['id']]=newid
    validate_project(project)
    return project

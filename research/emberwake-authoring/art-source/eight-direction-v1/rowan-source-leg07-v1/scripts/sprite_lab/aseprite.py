"""Bounded RGBA ASE adapter, official aseprite/docs/ase-file-specs.md.
Exact tick timing/pivots/source live in a sidecar, not millisecond inference.
"""
import copy,json,struct,zlib,math,hashlib
from pathlib import Path
from PIL import Image
from .core import validate_project,render_cel,project_hash,require
from .canonical import canonical_json,content_hash

def _chunk(kind,payload):return struct.pack('<IH',len(payload)+6,kind)+payload
def _string(value):
    encoded=value.encode('utf-8');require(len(encoded)<=65535,'ASE string too long');return struct.pack('<H',len(encoded))+encoded

def export_aseprite(project,path,animation_id=None,sidecar=None):
    validate_project(project);path=Path(path);sidecar=Path(sidecar)if sidecar else Path(str(path)+'.sprite-lab.json');anim=next((a for a in project['animations']if a['id']==animation_id),None)if animation_id else(project['animations'][0]if project['animations']else None);require(anim is not None,'Animation selection required')
    byid={f['id']:f for f in project['frames']};frames=[byid[i]for i in anim['frames']];w=project['canvas']['width'];h=project['canvas']['height'];require(w<=65535 and h<=65535 and len(frames)<=65535 and len(project['layers'])<=65535,'ASE format dimensions/frame/layer bound');output=[];timing=[]
    elapsed_ticks=0;previous_boundary=0
    for fi,frame in enumerate(frames):
        elapsed_ticks+=frame['duration_ticks']
        boundary=math.floor(elapsed_ticks*1000/anim['fps']+.5)
        ms=boundary-previous_boundary;previous_boundary=boundary
        require(1<=ms<=65535,'ASE millisecond duration is not representable');timing.append({'frame_id':frame['id'],'duration_ticks':frame['duration_ticks'],'milliseconds':ms,'quantization_error_ms':ms-frame['duration_ticks']*1000/anim['fps'],'cumulative_boundary_error_ms':boundary-elapsed_ticks*1000/anim['fps']})
        chunks=[]
        if fi==0:
            for layer in project['layers']:
                flags=1|(4 if layer['locked']else 2);chunks.append(_chunk(0x2004,struct.pack('<6HB3x',flags,0,0,w,h,0,255)+_string(layer['name'])))
        for li,layer in enumerate(project['layers']):
            if layer['id']not in frame['cels']:continue
            im=render_cel(project,frame['cels'][layer['id']]);cel=struct.pack('<HhhBHh5xHH',li,0,0,255,2,0,w,h)+zlib.compress(im.tobytes(),9);chunks.append(_chunk(0x2005,cel))
        payload=b''.join(chunks);output.append(struct.pack('<IHHH2xI',len(payload)+16,0xf1fa,len(chunks)if len(chunks)<65535 else 65535,ms,len(chunks))+payload)
    data=b''.join(output);header=bytearray(128);struct.pack_into('<IHHHHHIH',header,0,len(data)+128,0xa5e0,len(frames),w,h,32,1,timing[0]['milliseconds']);header[34:36]=b'\x01\x01';path.write_bytes(bytes(header)+data)
    metadata={'schema':'sprite-edit-ase-sidecar/v1','format_source':'https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md','project':project,'project_sha256':project_hash(project),'animation_id':anim['id'],'sequence':anim['frames'],'timing':timing,'millisecond_clock':'Cumulative boundary rounding; original ticks remain authoritative','ase_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds':'RGBA normal layers/cropped or linked cels; no groups/blend modes/opacity transforms. Original ticks/events/pivots remain authoritative. Changed tool durations require explicit timing edits.'};sidecar.write_text(canonical_json(metadata)+'\n',encoding='utf-8');return metadata

def read_aseprite(path):
    data=Path(path).read_bytes();require(len(data)>=128,'Truncated ASE header');size,magic,count,w,h,depth=struct.unpack_from('<IHHHHH',data);require(size==len(data)and magic==0xa5e0 and depth==32,'Unsupported ASE header/depth');layers=[];frames=[];offset=128
    for fi in range(count):
        require(offset+16<=len(data),'Truncated frame');length,magic,oldcount,ms,newcount=struct.unpack_from('<IHHH2xI',data,offset);require(magic==0xf1fa and length>=16 and offset+length<=len(data),'Invalid ASE frame');pos=offset+16;end=offset+length;cels={};raw_cels={}
        for _ in range(newcount or oldcount):
            require(pos+6<=end,'Truncated chunk');chunklen,kind=struct.unpack_from('<IH',data,pos);require(chunklen>=6 and pos+chunklen<=end,'Invalid chunk');b=data[pos+6:pos+chunklen]
            if kind==0x2004:
                require(len(b)>=18,'Truncated layer');flags,layer_type,child,_,_,blend,opacity=struct.unpack_from('<6HB',b);n=struct.unpack_from('<H',b,16)[0];require(layer_type==0 and child==0 and blend==0 and opacity==255 and flags&1 and len(b)>=18+n,'Unsupported layer structure/blend');layers.append({'name':b[18:18+n].decode('utf-8'),'flags':flags})
            elif kind==0x2005:
                require(len(b)>=16,'Truncated cel');li,x,y,opacity,celtype,zindex=struct.unpack_from('<HhhBHh',b);require(opacity==255 and zindex==0 and li not in cels,'Unsupported cel opacity/order')
                if celtype==1:
                    require(len(b)>=18,'Truncated linked cel');linked=struct.unpack_from('<H',b,16)[0];require(linked<fi and li in frames[linked]['cels'],'Invalid linked cel');image=frames[linked]['raw_cels'][li].copy()
                elif celtype in [0,2]:
                    require(len(b)>=20,'Truncated image cel');cw,ch=struct.unpack_from('<HH',b,16);require(cw>0 and ch>0 and cw*ch<=16777216,'Cel size limit');raw=zlib.decompress(b[20:])if celtype==2 else b[20:];require(len(raw)==cw*ch*4,'Invalid RGBA payload');image=Image.frombytes('RGBA',(cw,ch),raw)
                else:raise ValueError('Unsupported cel type')
                require(x>=0 and y>=0 and x+image.width<=w and y+image.height<=h,'Cel outside canvas');raw_cels[li]=image;full=Image.new('RGBA',(w,h));full.paste(image,(x,y));cels[li]=full
            pos+=chunklen
        require(pos==end,'Unexpected frame bytes');frames.append({'milliseconds':ms,'cels':cels,'raw_cels':raw_cels});offset=end
    require(offset==len(data)and all(li<len(layers)for f in frames for li in f['cels']),'Invalid layer index/end');return {'width':w,'height':h,'layers':layers,'frames':frames}

def import_aseprite(path,sidecar=None):
    sidecar=Path(sidecar)if sidecar else Path(str(path)+'.sprite-lab.json');meta=json.loads(sidecar.read_text());require(meta.get('schema')=='sprite-edit-ase-sidecar/v1','Invalid ASE sidecar');project=copy.deepcopy(meta['project']);require(project_hash(project)==meta['project_sha256'],'Stale sidecar project');ase=read_aseprite(path);require((ase['width'],ase['height'])==(project['canvas']['width'],project['canvas']['height']),'ASE resized canvas');require([x['name']for x in ase['layers']]==[x['name']for x in project['layers']],'ASE renamed/reordered layers');require(len(ase['frames'])==len(meta['sequence']),'ASE changed frame structure');mapping={tuple(c):i for i,c in reversed(list(enumerate(project['palette'])))};byid={f['id']:f for f in project['frames']};changes={}
    for fi,external in enumerate(ase['frames']):
        require(external['milliseconds']==meta['timing'][fi]['milliseconds'],'ASE changed quantized timing');frame=byid[meta['sequence'][fi]]
        for li,layer in enumerate(project['layers']):
            image=external['cels'].get(li,Image.new('RGBA',(ase['width'],ase['height'])));oldid=frame['cels'].get(layer['id']);old=project['cels'][oldid]['pixels']if oldid else[0]*(ase['width']*ase['height']);pixels=[]
            for i,color in enumerate(image.getdata()):
                if tuple(project['palette'][old[i]])==color:index=old[i]
                else:
                    if color not in mapping:mapping[color]=len(project['palette']);project['palette'].append(list(color))
                    index=mapping[color]
                pixels.append(index)
            key=(frame['id'],layer['id']);require(key not in changes or changes[key]==pixels,'Repeated animation frame edited inconsistently');changes[key]=pixels
            if pixels!=old:
                require(not layer['locked'],'ASE changes locked layer');newid='ase:'+frame['id']+':'+layer['id']+':'+content_hash(pixels)[:12];project['cels'][newid]={'layer_id':layer['id'],'pixels':pixels};frame['cels'][layer['id']]=newid
    validate_project(project);return project

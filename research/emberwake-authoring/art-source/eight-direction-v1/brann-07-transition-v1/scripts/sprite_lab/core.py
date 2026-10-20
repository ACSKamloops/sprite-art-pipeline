import copy,math
from PIL import Image
from .canonical import canonical_json,content_hash

class EditError(ValueError):pass

def require(value,message):
    if not value:raise EditError(message)
def integer(value):return type(value)is int and abs(value)<=9007199254740991
def identifier(value):return isinstance(value,str)and bool(value)
def pair(value):return isinstance(value,list)and len(value)==2 and all(integer(x)for x in value)
def rgba(value):return isinstance(value,list)and len(value)==4 and all(integer(x)and 0<=x<=255 for x in value)
def shape(value,required,optional=()):
    require(isinstance(value,dict),'Expected object')
    require(set(required)<=set(value)<=set(required)|set(optional),'Missing or unknown fields')
def validate_project(p):
    shape(p,['schema','canvas','palette','layers','cels','frames','animations'],['provenance'])
    require(p['schema']=='sprite-edit-project/v1','Unsupported project schema')
    c=p['canvas'];shape(c,['width','height','render_pivot','ground_pivot'])
    require(all(integer(c[k])and c[k]>0 for k in ['width','height'])and c['width']*c['height']<=16777216,'Invalid canvas dimensions')
    require(pair(c['render_pivot'])and pair(c['ground_pivot']),'Invalid pivots')
    palette=p['palette'];require(isinstance(palette,list)and bool(palette)and palette[0]==[0,0,0,0]and all(rgba(x)for x in palette),'Invalid RGBA palette')
    require(isinstance(p['layers'],list),'Invalid layers');layers={}
    for layer in p['layers']:
        shape(layer,['id','name','locked']);require(identifier(layer['id'])and identifier(layer['name'])and type(layer['locked'])is bool and layer['id']not in layers,'Invalid/duplicate layer');layers[layer['id']]=layer
    require(isinstance(p['cels'],dict),'Invalid cels');n=c['width']*c['height']
    for cel_id,cel in p['cels'].items():
        shape(cel,['layer_id','pixels']);require(identifier(cel_id)and identifier(cel['layer_id'])and cel['layer_id']in layers,'Invalid cel owner')
        require(isinstance(cel['pixels'],list)and len(cel['pixels'])==n and all(integer(i)and 0<=i<len(palette)for i in cel['pixels']),'Invalid indexed pixels')
    require(isinstance(p['frames'],list)and bool(p['frames']),'No frames');frames={}
    for frame in p['frames']:
        shape(frame,['id','duration_ticks','cels','landmarks']);require(identifier(frame['id'])and frame['id']not in frames and integer(frame['duration_ticks'])and frame['duration_ticks']>0,'Invalid frame')
        require(isinstance(frame['cels'],dict)and isinstance(frame['landmarks'],dict)and all(identifier(k)and pair(v)for k,v in frame['landmarks'].items()),'Invalid frame metadata')
        for layer_id,cel_id in frame['cels'].items():require(layer_id in layers and identifier(cel_id)and cel_id in p['cels']and p['cels'][cel_id]['layer_id']==layer_id,'Invalid cel binding')
        frames[frame['id']]=frame
    require(isinstance(p['animations'],list),'Invalid animations');ids=set()
    for anim in p['animations']:
        shape(anim,['id','frames','fps','loop','events']);require(identifier(anim['id'])and anim['id']not in ids,'Invalid animation id');ids.add(anim['id'])
        require(isinstance(anim['frames'],list)and bool(anim['frames'])and all(identifier(i)and i in frames for i in anim['frames']),'Invalid animation frames')
        require(type(anim['fps'])in(int,float)and math.isfinite(anim['fps'])and anim['fps']>0 and type(anim['loop'])is bool,'Invalid animation clock')
        total=sum(frames[i]['duration_ticks']for i in anim['frames']);require(isinstance(anim['events'],list),'Invalid events')
        for event in anim['events']:
            shape(event,['at_tick','name']);require(integer(event['at_tick'])and 0<=event['at_tick']<total and identifier(event['name']),'Invalid event')
    # Pixel arrays are already checked above; canonical validation is needed only
    # for metadata/string encoding, not millions of known-safe integer indices.
    canonical_json({**p,'cels':{k:{'layer_id':v['layer_id']}for k,v in p['cels'].items()}})
    return p

def project_hash(p):validate_project(p);return content_hash(p)
def cel_hash(p,cel_id):return content_hash(p['cels'][cel_id])
def render_cel(p,cel_id):
    c=p['canvas'];im=Image.new('RGBA',(c['width'],c['height']));im.putdata([tuple(p['palette'][i])for i in p['cels'][cel_id]['pixels']]);return im
def render_frame(p,frame_id):
    validate_project(p);return _render_frame(p,frame_id)
def render_frames(p,frame_ids):
    """Render one bounded batch with one complete project validation."""
    validate_project(p)
    return [_render_frame(p,frame_id) for frame_id in frame_ids]
def _render_frame(p,frame_id):
    frame=next((x for x in p['frames']if x['id']==frame_id),None);require(frame is not None,'Unknown frame')
    pixels=[[0,0,0,0]for _ in range(p['canvas']['width']*p['canvas']['height'])]
    for layer in p['layers']:
        if layer['id']not in frame['cels']:continue
        source=p['cels'][frame['cels'][layer['id']]]['pixels']
        for i,index in enumerate(source):
            src=p['palette'][index];sa=src[3]
            if sa==0:continue
            if sa==255:pixels[i]=src;continue
            dst=pixels[i];da=dst[3];n=sa*255+da*(255-sa)
            if n==0:pixels[i]=[0,0,0,0]
            else:pixels[i]=[(src[k]*sa*255+dst[k]*da*(255-sa)+n//2)//n for k in range(3)]+[(n+127)//255]
    im=Image.new('RGBA',(p['canvas']['width'],p['canvas']['height']));im.putdata([tuple(x)for x in pixels]);return im

def _mask(p,value):
    require(isinstance(value,list),'Mask must be coordinate list');w=p['canvas']['width'];h=p['canvas']['height'];indices=set()
    for point in value:
        require(pair(point)and 0<=point[0]<w and 0<=point[1]<h,'Invalid mask point');i=point[1]*w+point[0];require(i not in indices,'Duplicate mask point');indices.add(i)
    return indices

def _cel(p,cel_id):
    require(identifier(cel_id)and cel_id in p['cels'],'Unknown cel');cel=p['cels'][cel_id];layer=next(x for x in p['layers']if x['id']==cel['layer_id']);require(not layer['locked'],'Layer is locked');return cel

def _translate(p,cel,dx,dy,allow_clip):
    require(integer(dx)and integer(dy)and type(allow_clip)is bool,'Invalid translation');w=p['canvas']['width'];h=p['canvas']['height'];out=[0]*(w*h)
    for i,index in enumerate(cel['pixels']):
        if index==0:continue
        x=i%w+dx;y=i//w+dy
        if not(0<=x<w and 0<=y<h):require(allow_clip,'Translation clips nontransparent indices');continue
        out[y*w+x]=index
    cel['pixels']=out

def _operation(p,op):
    require(isinstance(op,dict)and isinstance(op.get('op'),str),'Invalid operation');kind=op['op'];w=p['canvas']['width'];h=p['canvas']['height']
    if kind in ['paint','erase']:
        shape(op,['op','cel_id','points'],['mask']);cel=_cel(p,op['cel_id']);require(isinstance(op['points'],list),'Invalid points');mask=_mask(p,op['mask'])if 'mask'in op else None
        for point in op['points']:
            require(isinstance(point,list)and len(point)==(3 if kind=='paint'else 2)and all(integer(v)for v in point),'Invalid stroke point');x,y=point[:2];require(0<=x<w and 0<=y<h,'Stroke out of bounds');i=y*w+x;require(mask is None or i in mask,'Stroke outside mask');index=point[2]if kind=='paint'else 0;require(0<=index<len(p['palette']),'Palette index out of bounds');cel['pixels'][i]=index
    elif kind=='replace_color':
        shape(op,['op','cel_id','from_index','to_index','mask']);cel=_cel(p,op['cel_id']);require(all(integer(op[k])and 0<=op[k]<len(p['palette'])for k in ['from_index','to_index']),'Invalid color index')
        for i in _mask(p,op['mask']):
            if cel['pixels'][i]==op['from_index']:cel['pixels'][i]=op['to_index']
    elif kind in ['translate','translate_layer']:
        key='cel_id'if kind=='translate'else'layer_id';shape(op,['op',key,'dx','dy'],['allow_clip'])
        if kind=='translate':cels=[_cel(p,op[key])]
        else:
            layer=next((x for x in p['layers']if x['id']==op[key]),None);require(layer is not None and not layer['locked'],'Unknown/locked layer');cels=[c for c in p['cels'].values()if c['layer_id']==op[key]]
        for cel in cels:_translate(p,cel,op['dx'],op['dy'],op.get('allow_clip',False))
    elif kind=='palette':
        shape(op,['op','index','rgba']);require(integer(op['index'])and 0<op['index']<len(p['palette'])and rgba(op['rgba']),'Invalid palette edit');require(not any(layer['locked']and any(c['layer_id']==layer['id']and op['index']in c['pixels']for c in p['cels'].values())for layer in p['layers']),'Palette edit changes locked layer');p['palette'][op['index']]=copy.deepcopy(op['rgba'])
    elif kind=='palette_add':
        shape(op,['op','rgba']);require(rgba(op['rgba']),'Invalid RGBA');p['palette'].append(copy.deepcopy(op['rgba']))
    elif kind=='candidate_patch':
        shape(op,['op','cel_id','mask','candidate_pixels','expected_cel_sha256']);cel=_cel(p,op['cel_id']);require(cel_hash(p,op['cel_id'])==op['expected_cel_sha256'],'Stale candidate cel');mask=_mask(p,op['mask']);candidate=op['candidate_pixels'];require(isinstance(candidate,list)and len(candidate)==w*h and all(integer(x)and 0<=x<len(p['palette'])for x in candidate),'Invalid candidate pixels')
        require(all(candidate[i]==cel['pixels'][i]for i in range(w*h)if i not in mask),'Candidate changes outside mask');cel['pixels']=copy.deepcopy(candidate)
    elif kind=='frame_timing':
        shape(op,['op','frame_id','duration_ticks']);frame=next((f for f in p['frames']if f['id']==op['frame_id']),None);require(frame is not None and integer(op['duration_ticks'])and op['duration_ticks']>0,'Invalid frame timing');frame['duration_ticks']=op['duration_ticks']
    elif kind=='pivots':
        shape(op,['op','render_pivot','ground_pivot']);require(pair(op['render_pivot'])and pair(op['ground_pivot']),'Invalid pivots');p['canvas']['render_pivot']=copy.deepcopy(op['render_pivot']);p['canvas']['ground_pivot']=copy.deepcopy(op['ground_pivot'])
    else:raise EditError('Unknown operation '+kind)

def diff_projects(before,after):
    validate_project(before);validate_project(after);return _diff_projects(before,after)
def _diff_projects(before,after):
    w=before['canvas']['width'];cels={};frames={}
    for key,cel in before['cels'].items():
        points=[[i%w,i//w]for i,(a,b)in enumerate(zip(cel['pixels'],after['cels'][key]['pixels']))if a!=b]
        if points:cels[key]={'changed_pixels':len(points),'coordinates':points}
    for frame in before['frames']:
        a=list(_render_frame(before,frame['id']).getdata());b=list(_render_frame(after,frame['id']).getdata());points=[[i%w,i//w]for i,(x,y)in enumerate(zip(a,b))if x!=y]
        if points:frames[frame['id']]={'changed_pixels':len(points),'coordinates':points,'bounds':[min(x[0]for x in points),min(x[1]for x in points),max(x[0]for x in points)+1,max(x[1]for x in points)+1]}
    return {'cels':cels,'frames':frames,'unchanged_frames':[f['id']for f in before['frames']if f['id']not in frames]}

def apply_transaction(project,transaction):
    validate_project(project);shape(transaction,['schema','expected_project_sha256','reason','operations']);require(transaction['schema']=='sprite-edit-transaction/v1','Unsupported transaction');before_hash=content_hash(project);require(transaction['expected_project_sha256']==before_hash,'Stale project');require(identifier(transaction['reason'])and isinstance(transaction['operations'],list)and bool(transaction['operations']),'Empty edit')
    result=copy.deepcopy(project)
    for op in transaction['operations']:_operation(result,op)
    validate_project(result);receipt={'schema':'sprite-edit-receipt/v1','before_sha256':before_hash,'after_sha256':content_hash(result),'transaction':copy.deepcopy(transaction),'diff':_diff_projects(project,result)}
    return {'project':result,'receipt':receipt}

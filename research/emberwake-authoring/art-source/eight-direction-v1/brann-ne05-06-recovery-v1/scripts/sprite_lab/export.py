import copy,io,json,zipfile,hashlib
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
from .core import validate_project,render_frame,render_cel,project_hash,require,_render_frame
from .canonical import canonical_json,content_hash

def png_bytes(image):
    stream=io.BytesIO();image.save(stream,format='PNG',compress_level=9,optimize=False);return stream.getvalue()
def export_project(project,directory,columns=8):
    validate_project(project);require(type(columns)is int and columns>0,'Invalid columns');directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);w=project['canvas']['width'];h=project['canvas']['height'];frames=project['frames'];cols=min(columns,len(frames));atlas=Image.new('RGBA',(cols*w,((len(frames)+cols-1)//cols)*h));rows=[]
    for i,frame in enumerate(frames):
        image=_render_frame(project,frame['id']);name=f'frame-{i:04d}.png';payload=png_bytes(image);(directory/name).write_bytes(payload);x=(i%cols)*w;y=(i//cols)*h;atlas.paste(image,(x,y));rows.append({'id':frame['id'],'png':name,'png_sha256':hashlib.sha256(payload).hexdigest(),'rgba_sha256':hashlib.sha256(image.tobytes()).hexdigest(),'region':[x,y,w,h],'duration_ticks':frame['duration_ticks'],'landmarks':frame['landmarks']})
    (directory/'atlas.png').write_bytes(png_bytes(atlas));manifest={'schema':'sprite-edit-export/v1','project_sha256':content_hash(project),'canvas':project['canvas'],'frames':rows,'animations':project['animations'],'provenance':project.get('provenance',{})};(directory/'manifest.json').write_text(canonical_json(manifest)+'\n',encoding='utf-8');(directory/'project.json').write_text(canonical_json(project)+'\n',encoding='utf-8');return manifest

def export_ora(project,frame_id,path):
    validate_project(project);frame=next(f for f in project['frames']if f['id']==frame_id);c=project['canvas'];root=ET.Element('image',{'version':'0.0.3','w':str(c['width']),'h':str(c['height']),'name':frame_id});stack=ET.SubElement(root,'stack');files={};bindings=[]
    for i,layer in reversed(list(enumerate(project['layers']))):
        name=f'data/layer-{i:04d}.png';image=render_cel(project,frame['cels'][layer['id']])if layer['id']in frame['cels']else Image.new('RGBA',(c['width'],c['height']));files[name]=png_bytes(image);ET.SubElement(stack,'layer',{'name':layer['name'],'src':name,'x':'0','y':'0','opacity':'1.0','visibility':'visible','composite-op':'svg:src-over'});bindings.append({'src':name,'layer_id':layer['id']})
    files['stack.xml']=ET.tostring(root,encoding='utf-8',xml_declaration=True);files['mergedimage.png']=png_bytes(_render_frame(project,frame_id));files['sprite-lab/project.json']=canonical_json(project).encode();files['sprite-lab/bindings.json']=canonical_json({'frame_id':frame_id,'layers':bindings}).encode()
    with zipfile.ZipFile(path,'w')as archive:
        for name,payload in [('mimetype',b'image/openraster')]+sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_STORED if name=='mimetype'else zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;archive.writestr(info,payload,compresslevel=9)
    return {'frame_id':frame_id,'project_sha256':content_hash(project),'ora_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}

def import_ora(path):
    with zipfile.ZipFile(path)as archive:
        require(archive.read('mimetype')==b'image/openraster','Not OpenRaster');project=json.loads(archive.read('sprite-lab/project.json'));binding=json.loads(archive.read('sprite-lab/bindings.json'));validate_project(project);frame=next(f for f in project['frames']if f['id']==binding['frame_id']);stack=ET.fromstring(archive.read('stack.xml'));require(int(stack.attrib['w'])==project['canvas']['width']and int(stack.attrib['h'])==project['canvas']['height'],'ORA resized canvas')
        layers=list(stack.find('stack'));require([x.attrib['src']for x in layers]==[x['src']for x in binding['layers']],'ORA changed layer order/structure')
        require(all(x.attrib.get('x','0')=='0'and x.attrib.get('y','0')=='0'and float(x.attrib.get('opacity','1'))==1 and x.attrib.get('visibility','visible')=='visible'and x.attrib.get('composite-op','svg:src-over')=='svg:src-over'for x in layers),'Unsupported ORA layer transform/blend')
        mapping={tuple(color):i for i,color in reversed(list(enumerate(project['palette'])))}
        for entry in binding['layers']:
            image=Image.open(io.BytesIO(archive.read(entry['src']))).convert('RGBA');require(image.size==(project['canvas']['width'],project['canvas']['height']),'ORA resized layer');layer_id=entry['layer_id'];old_id=frame['cels'].get(layer_id);old=project['cels'][old_id]['pixels']if old_id else [0]*(image.width*image.height);pixels=[]
            for i,color in enumerate(image.getdata()):
                if tuple(project['palette'][old[i]])==color:index=old[i]
                else:
                    if color not in mapping:mapping[color]=len(project['palette']);project['palette'].append(list(color))
                    index=mapping[color]
                pixels.append(index)
            if pixels!=old:
                layer=next(x for x in project['layers']if x['id']==layer_id);require(not layer['locked'],'ORA changes locked layer');shared=old_id and sum(f['cels'].get(layer_id)==old_id for f in project['frames'])>1;cel_id=('ora:'+binding['frame_id']+':'+layer_id+':'+content_hash(pixels)[:12])if shared or not old_id else old_id;project['cels'][cel_id]={'layer_id':layer_id,'pixels':pixels};frame['cels'][layer_id]=cel_id
    validate_project(project);return project

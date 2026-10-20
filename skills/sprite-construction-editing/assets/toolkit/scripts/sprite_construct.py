#!/usr/bin/env python3
"""Lossless, explicit layered construction from a portable source-image spec."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image
from sprite_lab import load_json,validate_project,canonical_json,project_hash
from sprite_lab.core import shape,require,pair

def construct(path):
    path=Path(path);spec=load_json(path.read_text())
    shape(spec,['schema','canvas','layers','frames','animations'],['provenance']);require(spec['schema']=='sprite-construction-spec/v1','Unknown construction schema')
    canvas=spec['canvas'];w,h=canvas['width'],canvas['height'];layers=spec['layers'];known={r['id'] for r in layers}
    validate_project({'schema':'sprite-edit-project/v1','canvas':canvas,'layers':layers,'palette':[[0,0,0,0]],'cels':{},
        'frames':[{'id':'validation','duration_ticks':1,'cels':{},'landmarks':{}}],'animations':[]})
    palette=[[0,0,0,0]];lookup={tuple(palette[0]):0};cels={};bindings={};frames=[];hashes={}
    for frame in spec['frames']:
        shape(frame,['id','duration_ticks'],['cels','landmarks'])
        frame_bindings={}
        for layer,entry in frame.get('cels',{}).items():
            shape(entry,['image'],['at']);require(isinstance(entry['image'],str) and bool(entry['image']),'Invalid source path');require(pair(entry.get('at',[0,0])),'Integer source placement required')
            if layer not in known:raise ValueError('Unknown construction layer')
            image_path=(path.parent/entry['image']).resolve()
            if not image_path.is_relative_to(path.parent.resolve()):raise ValueError('Construction inputs must be portable paths inside the spec folder')
            x,y=entry.get('at',[0,0])
            if type(x)is not int or type(y)is not int:raise ValueError('Integer source placement required')
            key=(layer,entry['image'],x,y)
            if key not in bindings:
                image=Image.open(image_path).convert('RGBA');pixels=[0]*(w*h)
                for sy in range(image.height):
                    for sx in range(image.width):
                        color=image.getpixel((sx,sy))
                        if not color[3]:continue
                        px,py=x+sx,y+sy
                        if not(0<=px<w and 0<=py<h):raise ValueError('Visible source pixels would be clipped')
                        if color not in lookup:lookup[color]=len(palette);palette.append(list(color))
                        pixels[py*w+px]=lookup[color]
                cid=f'cel-{len(cels):04d}';cels[cid]={'layer_id':layer,'pixels':pixels};bindings[key]=cid
                hashes[entry['image']]=hashlib.sha256(image_path.read_bytes()).hexdigest()
            frame_bindings[layer]=bindings[key]
        frames.append({'id':frame['id'],'duration_ticks':frame['duration_ticks'],'cels':frame_bindings,'landmarks':frame.get('landmarks',{})})
    provenance=dict(spec.get('provenance',{}));provenance.update({'construction_spec_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_image_sha256':hashes,'transparent_rgb':'Canonical zero only for alpha0; all visible RGBA preserved'})
    project={'schema':'sprite-edit-project/v1','canvas':canvas,'palette':palette,'layers':layers,'cels':cels,'frames':frames,'animations':spec['animations'],'provenance':provenance}
    validate_project(project);return project
def main():
    parser=argparse.ArgumentParser();parser.add_argument('spec');parser.add_argument('output');args=parser.parse_args()
    project=construct(args.spec);out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(canonical_json(project)+'\n');print(project_hash(project))
if __name__=='__main__':main()

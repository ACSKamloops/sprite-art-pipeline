#!/usr/bin/env python3
"""Reuse a real ImageGen cottage lantern as a separate editable village prop."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
root=Path(__file__).resolve().parents[1]
source=root/'assets/world/cottage.png'
im=Image.open(source).convert('RGBA')
mask=Image.new('L',im.size)
polygon=[(234,202),(241,198),(244,192),(249,194),(250,200),(257,204),(260,207),(257,210),(255,223),(244,230),(234,224),(232,210),(230,207)]
ImageDraw.Draw(mask).polygon(polygon,fill=255)
lamp=Image.new('RGBA',im.size);lamp.paste(im,(0,0),mask)
lamp=lamp.crop((228,190,262,232))
out=Image.new('RGBA',(64,96));d=ImageDraw.Draw(out)
# Authored pixel post, using the cottage's warm wooden material palette.
d.ellipse((21,84,43,91),fill=(25,32,25,95))
d.polygon([(27,87),(28,40),(34,40),(36,87)],fill=(62,48,33,255))
d.line([(29,85),(30,43)],fill=(133,98,56,255),width=2)
d.line([(34,85),(33,43)],fill=(34,35,25,255),width=1)
d.rectangle((25,83,38,88),fill=(76,62,39,255))
d.line([(26,84),(36,84)],fill=(155,122,68,255),width=1)
out.alpha_composite(lamp,(16,4));out.save(root/'assets/world/lantern.png')
(root/'art-source/LANTERN-RECEIPT.json').write_text(json.dumps({'origin':'ImageGen cottage component plus authored pixel wooden post','source':'assets/world/cottage.png','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'literal_component_polygon':polygon,'crop':[228,190,262,232],'placement':[16,4],'canvas':[64,96],'pivot':[32,88],'output_sha256':hashlib.sha256((root/'assets/world/lantern.png').read_bytes()).hexdigest()},indent=2)+'\n')

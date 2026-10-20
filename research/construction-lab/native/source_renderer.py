#!/usr/bin/env python3
"""Inspect captured SNES OBJ tiles, independently of the ROM frame parser.

Pure OBJ reconstruction excludes background priority, scanline limits and color
math. Captures retain those in the original emulator screenshot.
"""
import argparse
import json
from pathlib import Path
from PIL import Image
class tiles:
    @staticmethod
    def decode_tile(raw):
        return [sum(((raw[y*2+(plane&1)+(plane//2)*16]>>(7-x))&1)<<plane for plane in range(4)) for y in range(8) for x in range(8)]

SIZES = [((8,8),(16,16)), ((8,8),(32,32)), ((8,8),(64,64)),
         ((16,16),(32,32)), ((16,16),(64,64)), ((32,32),(64,64)),
         ((16,32),(32,64)), ((16,32),(32,32))]

def rgb(word):
    return tuple(((word >> bit) & 31) * 255 // 31 for bit in (0,5,10))

def object_records(snapshot):
    oam = (snapshot / 'oam.bin').read_bytes()
    ppu = json.loads((snapshot / 'ppu.json').read_text())
    records = []
    for index in range(128):
        x, y, tile, attr = oam[index*4:index*4+4]
        hi = (oam[512+index//4] >> ((index%4)*2)) & 3
        x |= (hi & 1) << 8
        if x >= 256:
            x -= 512
        width, height = SIZES[ppu['size']][(hi >> 1) & 1]
        records.append({'index':index, 'x':x, 'y':y, 'tile':tile | ((attr&1)<<8),
                        'width':width, 'height':height, 'palette':(attr>>1)&7,
                        'priority':(attr>>4)&3, 'flip_x':bool(attr&64), 'flip_y':bool(attr&128)})
    return records, ppu

def object_image(record, vram, cgram, ppu):
    width, height = record['width'], record['height']
    palette_start = (128 + record['palette'] * 16) * 2
    colors = [(*rgb(int.from_bytes(cgram[palette_start+i*2:palette_start+i*2+2], 'little')),
               0 if i==0 else 255) for i in range(16)]
    image = Image.new('RGBA', (width,height))
    sources = []
    for ty in range(height//8):
        for tx in range(width//8):
            number = ((record['tile'] & 0xF0) + ty*16) & 0xF0
            number |= (record['tile'] & 0x100) | ((record['tile']+tx) & 15)
            source = (ppu['base'] + number*32 + (ppu['select'] if number&0x100 else 0)) & 0xFFFF
            raw = bytes(vram[(source+i)&0xFFFF] for i in range(32))
            tile = Image.new('RGBA', (8,8))
            tile.putdata([colors[index] for index in tiles.decode_tile(raw)])
            image.paste(tile, (tx*8,ty*8))
            sources.append(source)
    if record['flip_x']:
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if record['flip_y']:
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    return image, sources

def export(snapshot, output):
    output.mkdir(parents=True,exist_ok=True)
    vram=(snapshot/'vram.bin').read_bytes(); cgram=(snapshot/'cgram.bin').read_bytes()
    records, ppu = object_records(snapshot)
    layer = Image.new('RGBA', (256,224))
    for record in reversed(records):
        image, sources = object_image(record,vram,cgram,ppu)
        record['vram_tile_offsets'] = sources
        if -record['width'] < record['x'] < 256 and record['y'] < 224:
            layer.alpha_composite(image,(record['x'],record['y']))
        if record['y']+record['height'] > 256:
            layer.alpha_composite(image,(record['x'],record['y']-256))
    layer.save(output/'objects.png')
    (output/'objects.json').write_text(json.dumps({'snapshot':str(snapshot.resolve()),'ppu':ppu,
        'limits':['Pure OBJ view; no background occlusion, color math, priority rotation or scanline sprite limits.'],
        'objects':records},indent=2)+'\n')
    print(json.dumps({'snapshot':snapshot.name,'output':str(output),'objects':len(records)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();export(args.snapshot,args.output)

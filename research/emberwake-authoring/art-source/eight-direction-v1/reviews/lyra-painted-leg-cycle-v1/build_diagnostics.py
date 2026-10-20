from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/home/astra/artifacts/emberwake-lyra-painted-leg-whole-walk-v1/packet/input')
SHEETS = ROOT / 'sheets'
SHEETS.mkdir(exist_ok=True)
manifest = json.loads((SOURCE / 'INPUTS.json').read_text())
font = ImageFont.load_default(size=14)
grounds = {'light': '#e7e3d6', 'dark': '#22252b', 'game': '#27392f'}
directions = {'southeast': 'SE', 'southwest': 'SW'}
index = []

def sprite(rel, scale, bg):
    source = Image.open(SOURCE / rel).convert('RGBA')
    assert source.size == (128, 128), (rel, source.size)
    enlarged = source.resize((scale, scale), Image.Resampling.NEAREST)
    result = Image.new('RGBA', (scale, scale), bg)
    result.alpha_composite(enlarged)
    return result.convert('RGB')

def save(sheet, name, kind, scale, ground, coverage):
    sheet.save(SHEETS / name)
    index.append(dict(file='sheets/' + name, kind=kind, scale=scale,
                      ground=ground, background=grounds[ground], coverage=coverage))

for scale in [128, 256, 84]:
    font = ImageFont.load_default(size=9 if scale == 84 else 12 if scale == 128 else 14)
    for ground, bg in grounds.items():
        margin, label, gap = 12, 24, 8
        cellw, cellh = scale + gap, scale + label + gap
        sheet = Image.new('RGB', (margin * 2 + 8 * cellw, margin * 2 + 4 * cellh), '#444444')
        draw = ImageDraw.Draw(sheet)
        for row, (variant, direction) in enumerate((v, d) for v in ['A', 'B'] for d in directions):
            for frame in range(8):
                x, y = margin + frame * cellw, margin + row * cellh
                draw.text((x, y), f'{variant} {directions[direction]} {frame:02}', fill='white', font=font)
                sheet.paste(sprite(f'{variant}/{direction}/{frame:02}.png', scale, bg), (x, y + label))
        save(sheet, f'poses-{scale}-{ground}.png', 'poses', scale, ground,
             'A and B; southeast and southwest; 00 through 07')
        for direction in directions:
            for start in [0, 4]:
                sheet = Image.new('RGB', (margin * 2 + 4 * cellw + 24, margin * 2 + 4 * cellh), '#444444')
                draw = ImageDraw.Draw(sheet)
                for row, frame in enumerate(range(start, start + 4)):
                    next_frame = (frame + 1) % 8
                    for col, (variant, shown) in enumerate([('A', frame), ('A', next_frame), ('B', frame), ('B', next_frame)]):
                        x = margin + col * cellw + (24 if col >= 2 else 0)
                        y = margin + row * cellh
                        draw.text((x, y), f'{variant} {directions[direction]} {frame:02}>{next_frame:02}: {shown:02}', fill='white', font=font)
                        sheet.paste(sprite(f'{variant}/{direction}/{shown:02}.png', scale, bg), (x, y + label))
                save(sheet, f'pairs-{direction}-{start:02}-{start+3:02}-{scale}-{ground}.png',
                     'pairs', scale, ground, f'A and B {direction}: ' + ', '.join(f'{i:02}>{(i+1)%8:02}' for i in range(start, start + 4)))
        rels = [x['path'] for x in manifest['context'] if x['path'] != 'context/appearance.png']
        sheet = Image.new('RGB', (margin * 2 + 10 * cellw, margin * 2 + 3 * cellh), '#444444')
        draw = ImageDraw.Draw(sheet)
        for k, rel in enumerate(rels):
            x, y = margin + k % 10 * cellw, margin + k // 10 * cellh
            title = Path(rel).stem.replace('-walk-', '-w-').replace('-idle-', '-i-')
            draw.text((x, y), title, fill='white', font=font)
            sheet.paste(sprite(rel, scale, bg), (x, y + label))
        save(sheet, f'context-{scale}-{ground}.png', 'identity_turn_context', scale, ground,
             'east/south/west idle 00..01 and walk 00..07; identity and turn only')
(ROOT / 'sheet-index.json').write_text(json.dumps(index, indent=2) + '\n')

# A mechanical verification of the diagnostic image cells, independent of labels.
for entry in index:
    scale, ground = entry['scale'], entry['ground']
    sheet = Image.open(ROOT / entry['file'])
    cellw, cellh = scale + 8, scale + 32
    checks = []
    if entry['kind'] == 'poses':
        checks = [(f'{v}/{d}/{i:02}.png', 12+i*cellw, 36+row*cellh)
                  for row,(v,d) in enumerate((v,d) for v in ['A','B'] for d in directions) for i in range(8)]
    elif entry['kind'] == 'pairs':
        filename = Path(entry['file']).stem.split('-')
        direction, start = filename[1], int(filename[2])
        checks = [(f'{v}/{direction}/{shown:02}.png', 12+col*cellw+(24 if col>=2 else 0), 36+row*cellh)
                  for row,i in enumerate(range(start,start+4))
                  for col,(v,shown) in enumerate([('A',i),('A',(i+1)%8),('B',i),('B',(i+1)%8)])]
    else:
        checks = [(rel,12+k%10*cellw,36+k//10*cellh) for k,rel in enumerate(rels)]
    for rel,x,y in checks:
        assert sheet.crop((x,y,x+scale,y+scale)).tobytes() == sprite(rel,scale,grounds[ground]).tobytes(), (entry['file'],rel)
print(json.dumps({'sheets':len(index),'cell_checks':sum(32 if e['kind']=='poses' else 16 if e['kind']=='pairs' else 30 for e in index),'resampling':'nearest','whole_canvas':True}))

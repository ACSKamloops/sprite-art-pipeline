from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json

ROOT = Path(__file__).resolve().parent
UPSTREAM = Path('/home/astra/artifacts/emberwake-lyra-stance-spring-v1/same-curve-occlusion-preview')

# Literal visual observations at the lower cloth boundary. These are sparse
# diagnostic witnesses, NOT a complete ownership mask or automatic classifier.
CORE = {
    '02': {54:87, 55:88, 56:89, 57:89, 58:89, 59:89, 60:89, 61:89, 62:88, 63:87},
    '06': {72:84, 73:85, 74:85, 75:86, 76:86, 77:86, 78:86, 79:86, 80:85, 81:85, 82:84},
}
LIP = {
    '02': [(57,90),(58,90),(59,90),(60,90),(62,89),(63,88),(64,86),(64,87)],
    '06': [(71,83),(71,84),(72,85),(73,86),(74,86),(76,87),(77,87),(78,87),(79,87),(80,86),(81,86),(82,85),(83,84)],
}
WARM = {
    '02': [(52,87),(53,87),(54,88),(55,89),(56,90),(54,91),(58,91)],
    '06': [(66,85),(65,86),(64,89),(75,87),(73,88),(77,88)],
}
EXPOSED = [(x,82) for x in range(66,71)] + [(x,83) for x in range(67,71)]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def witness(im, xy):
    return {'xy': list(xy), 'rgba': list(im.getpixel(tuple(xy)))}

observations = {'coordinate_convention':'zero-based native128 x,y; inclusive row/column statements',
                'status':'read-only sparse visual material advisory, not an executable owner', 'phases':{}}
for phase in ('02','06'):
    im=Image.open(ROOT/'source'/f'{phase}.png').convert('RGBA')
    observations['phases'][phase]={
        'last_unequivocal_charcoal_per_column':[witness(im,(x,y)) for x,y in CORE[phase].items()],
        'fixed_dark_boundary_or_shared_outline':[witness(im,p) for p in LIP[phase]],
        'warm_leather_or_cuff_boundary_exclusions':[witness(im,p) for p in WARM[phase]],
    }
    box=(46,80,86,97); scale=20;cw=(box[2]-box[0])*scale;ch=(box[3]-box[1])*scale
    sheet=Image.new('RGB',(cw*2+70,ch+100),(235,233,221));d=ImageDraw.Draw(sheet)
    bg=Image.new('RGBA',(cw,ch),(235,233,221,255));bg.alpha_composite(im.crop(box).resize((cw,ch),Image.Resampling.NEAREST))
    sheet.paste(bg.convert('RGB'),(30,74));sheet.paste(bg.convert('RGB'),(cw+60,74))
    d.text((30,6),f'{phase} actual source / no pixel edits',fill=(0,0,0))
    d.text((cw+60,6),'Sparse diagnostic endpoint witnesses',fill=(0,0,0))
    d.text((30,24),'Green=core endpoint; magenta=keep dark transition fixed; orange=warm exclusion',fill=(0,0,0))
    if phase=='06':d.text((30,38),'Red=9 coat-owned pixels exposed after body-up2; no visible hidden-cloth donor',fill=(0,0,0))
    for xoff in (30,cw+60):
        for x in range(box[0],box[2]):
            px=xoff+(x-box[0])*scale
            d.text((px+1,62),str(x),fill=(0,0,0))
        for y in range(box[1],box[3]):
            py=74+(y-box[1])*scale
            d.text((xoff-18,py+3),str(y),fill=(0,0,0))
    def mark(p,color):
        x,y=p
        px=cw+60+(x-box[0])*scale;py=74+(y-box[1])*scale
        d.rectangle((px+1,py+1,px+scale-2,py+scale-2),outline=color,width=2)
    for p in CORE[phase].items():mark(p,(0,230,110))
    for p in LIP[phase]:mark(p,(220,0,220))
    for p in WARM[phase]:mark(p,(255,130,0))
    if phase=='06':
        for p in EXPOSED:mark(p,(255,30,40))
    sheet.save(ROOT/'proof'/f'{phase}-source-endpoint-witnesses20x.png')

# Account for actual source coverage at the producer's frozen rejected holes.
rejection=json.loads((UPSTREAM/'JOIN-REJECTION-WITNESSES.json').read_text())
accounting=[]
for finding in rejection['findings']:
    phase=finding['phase']
    layers={n:Image.open(UPSTREAM/'layers'/f'{phase:02}-{n}.png').convert('RGBA')
            for n in ('body-source','body-translated','left-cloth','right-cloth','fixed-lower-before','fixed-lower-after')}
    rows=[]
    for w in finding['new_hole_coordinates']:
        p=tuple(w['at'])
        rows.append({'xy':list(p),'source_rgba':w['before_rgba'],
                     'source_body_rgba':list(layers['body-source'].getpixel(p)),
                     'actual_target_layer_rgba':{n:list(im.getpixel(p)) for n,im in layers.items() if n!='body-source'},
                     'cause_class': 'coat-disocclusion-no-visible-underpaint' if layers['body-source'].getpixel(p)[3] else 'previously-visible-lower-carved-or-unmapped'})
    accounting.append({'phase':phase,'hole_count':len(rows),'coat_disocclusion_count':sum(x['cause_class']=='coat-disocclusion-no-visible-underpaint' for x in rows),'holes':rows})

observations['rejected_trial_hole_accounting']=accounting
observations['read_only_consulted_upstream']={str(p):sha(p) for p in [UPSTREAM/'JOIN-REJECTION-WITNESSES.json',UPSTREAM/'BODY-BOOT-CLOTH-RECEIPT.json',UPSTREAM/'proof'/'00-02-04-06-joint-detail.png']}
(ROOT/'BOUNDARY-WITNESSES.json').write_text(json.dumps(observations,indent=2)+'\n')

# Own copy of source-v-rejected is evidence only, not a proposed cel.
for phase in ('02','06'):
    src=Image.open(ROOT/'source'/f'{phase}.png').convert('RGBA')
    rejected=Image.open(UPSTREAM/'frames'/f'{phase}.png').convert('RGBA')
    box=(45,77,87,98);scale=16;sz=((box[2]-box[0])*scale,(box[3]-box[1])*scale)
    pair=Image.new('RGBA',(sz[0]*2+40,sz[1]+28),(235,233,221,255));d=ImageDraw.Draw(pair)
    d.text((0,5),f'{phase} source',fill=(0,0,0));d.text((sz[0]+40,5),f'{phase} rejected trial',fill=(0,0,0))
    pair.alpha_composite(src.crop(box).resize(sz,Image.Resampling.NEAREST),(0,28))
    pair.alpha_composite(rejected.crop(box).resize(sz,Image.Resampling.NEAREST),(sz[0]+40,28))
    pair.convert('RGB').save(ROOT/'proof'/f'{phase}-source-v-rejected16x.png')

# Confirm untouched originals still match our exact copied witnesses.
sources=json.loads((ROOT/'SOURCE-WITNESSES.json').read_text())
assert all(sha(Path(v['source']))==v['sha256']==sha(ROOT/'source'/f'{p}.png') for p,v in sources.items())
print('Read-only source equality: 8/8; sparse endpoint evidence and hole accounting written.')

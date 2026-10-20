#!/usr/bin/env python3
"""Deterministic atlas registration; raw ImageGen outputs are never overwritten."""
import hashlib
import json
import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageDraw
from scipy.ndimage import label

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "art-source/hero"
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=ROOT/'assets/hero')
parser.add_argument('--passing-mode',choices=['painted','hold','none'],default='painted')
args=parser.parse_args()
OUT = args.output.resolve()
OUT.mkdir(parents=True, exist_ok=True)
CELL = 128
frames = []
lineage = []
animations = {}

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def cut(p, cols, rows, index):
    im = Image.open(p).convert("RGBA")
    if p.name == "east-walk-repair-raw.png":
        # Actual return1774x887, fractional443.5px nominal grid. One full-sheet
        # NN resize to1792x896 makes the uniform cell boundaries explicit.
        im = im.resize((1792,896),Image.Resampling.NEAREST)
    assert im.width % cols == 0 and im.height % rows == 0, (p, im.size)
    w, h = im.width // cols, im.height // rows
    x, y = index % cols * w, index // cols * h
    return im.crop((x, y, x+w, y+h))

def register(im, source_anchor, scale):
    # One declared affine per source sheet. No per-pose bbox fitting.
    sx, sy = source_anchor
    result = im.transform((CELL, CELL), Image.Transform.AFFINE,
        (1/scale, 0, sx-64/scale, 0, 1/scale, sy-112/scale),
        Image.Resampling.NEAREST)
    pixels = np.array(result)
    a = pixels[:, :, 3]
    a[a < 24] = 0
    a[a > 245] = 255
    pixels[a == 0] = 0
    # Remove only disconnected backdrop/grid components; keep the complete body
    # and its soft contour. Do not raise the contour's global alpha threshold.
    labels, count = label(pixels[:,:,3] > 0, np.ones((3,3)))
    if count:
        sizes = np.bincount(labels.ravel());sizes[0] = 0
        pixels[labels != sizes.argmax()] = 0
    return Image.fromarray(pixels)

def translated(im,dx=0,dy=0):
    out=Image.new('RGBA',(128,128));out.alpha_composite(im,(dx,dy));return out

def append(im, source, source_index, transform):
    index = len(frames)
    frames.append(im)
    lineage.append({"frame": index, "source": str(source.relative_to(ROOT)),
                    "source_sha256": digest(source), "source_cell": source_index,
                    "transform": transform,
                    "rgba_sha256": hashlib.sha256(im.tobytes()).hexdigest()})
    return index

for direction in ["south", "east", "north", "west"]:
    path = SOURCE / f"{direction}-raw.png"
    raw = Image.open(path)
    # All four initial atlases use 256x256 source cells. Source baseline244;
    # .42 preserves ~94-99px native actor heights before worldscale.66.
    assert raw.size == (1536, 1024), (direction, raw.size)
    transform = {"scale": .42, "source_anchor": [128,244],
                 "destination_anchor": [64,112], "resampling": "nearest",
                 "alpha": "below24->0,above245->255,hiddenRGB->0"}
    bank = []
    for i in range(24):
        src = path
        source_index = i
        if direction == "north" and i in [6,7,8,9,10,11]:
            src = SOURCE / "north-attack-fix-raw.png"
            # The returned second contact had the other arm raised. Reject it.
            source_index = 8 if i == 9 else i
        cel = register(cut(src,6,4,source_index), (128,244), .42)
        adjustment = dict(transform)
        if i < 6 and direction in ['north','south']:
            # Measured spine/belt-root drift, corroborated by head and both legs.
            # Explicit authored root offsets, never per-frame bbox normalization.
            dx = {'north':[-10,-9,-6,-5,-2,2], 'south':[-3,-2,-1,0,2,3]}[direction][i]
            cel=translated(cel,dx,0)
            adjustment['root_translation']=[dx,0]
            adjustment['registration_basis']='shared pelvis/spine stage root; retain residual cyclical sway'
        # Generated sheet columns also drift within in-place actions. These are
        # explicit pelvis-root offsets measured on the upper cream trouser/hip
        # row, corroborated against the torso; never fitted silhouette bounds.
        # Each full cel translates without changing any anatomical pixel.
        if 6 <= i < 20:
            offsets={
                'south':[-3,1,0,0,0,3,-1,-1,0,1,1,2,-1,-1],
                'east':[-2,1,4,2,-1,2,-4,-1,4,6,1,1,-3,1],
                'north':[-7,-8,-8,-8,-4,-2,-9,-8,-6,-3,0,2,-7,-8],
                'west':[-5,-7,-8,-9,-6,1,-6,-2,-1,-1,-4,2,-7,-2],
            }
            dx=offsets[direction][i-6]
            cel=translated(cel,dx,0)
            adjustment['inplace_root_translation']=[dx,0]
            adjustment['registration_basis']='authored uppertrouser pelvis origin; preserve fullpose and physicalstage'
        bank.append(append(cel,src,source_index,adjustment))
    clips = {
       "idle": ([18,19], [.58,.58], True),
       "walk": (list(range(6)), [.075]*6, True),
       "attack": (list(range(6,12)), [.06,.07,.055,.055,.065,.105], False),
       "cast": (list(range(12,18)), [.06,.08,.10,.08,.08,.10], False),
       "hurt": ([20,21,18], [.09,.10,.10], False),
       "dodge": ([22,23,22,18], [.045,.105,.055,.055], False),
    }
    for state,(indices,holds,loop) in clips.items():
        animations[f"{direction}_{state}"] = {"frames":[bank[i] for i in indices], "holds": holds,"loop":loop}
    if direction=='north':
        # Return-order51 reverses foot role between50and52. This trial groups
        # corresponding A and B halves; dedicated passing paint is separate.
        animations['north_walk']['frames']=[48,49,51,50,52,53]

# Selected pose-guided correction: unlike rejected original east/west walk rows,
# these eight keys include actual passing poses. West walk is a disclosed mirror
# of that corrected east walk only; west's other five actions are separately painted.
path = SOURCE / "east-walk-repair-raw.png"
im = Image.open(path)
w,h = im.width//4,im.height//2
assert im.size == (1774,887), im.size
for direction in ["east","west"]:
    bank=[]
    for i in range(8):
        cel=register(cut(path,4,2,i), (224,425), .248)
        dy=3 if i>=4 else -2
        cel=translated(cel,0,dy)
        if direction=="west":
            cel=ImageOps.mirror(cel)
            # mirror axis x63.5; stage pivot remains64, explicit onepixel shift
            shifted=Image.new("RGBA",(128,128)); shifted.alpha_composite(cel,(1,0));cel=shifted
        bank.append(append(cel,path,i,{"scale":.248,"raw_size":[1774,887],"whole_sheet_NN_size":[1792,896],"source_anchor":[224,425],"destination_anchor":[64,112],"resampling":"nearest","mirror_x":direction=="west","mirror_offset_x":1 if direction=="west" else 0,"row_y_translation":dy,"alpha":"below24->0,above245->255,hiddenRGB->0;disconnectedgridcomponentsremoved"}))
    animations[f"{direction}_walk"]={"frames":bank,"holds":[.05625]*8,"loop":True}

if args.passing_mode!='none':
    added={}
    for name,source_id in [('south_A',1),('south_B',4),('north_A',49),('north_B',52)]:
        src=SOURCE/'passing/output/passing'/f'{name}.png'
        cel=Image.open(src).convert('RGBA') if args.passing_mode=='painted' else frames[source_id].copy()
        assert cel.size==(128,128)
        if args.passing_mode=='painted':
            base=np.array(frames[source_id]);edited=np.array(cel)
            mask=np.zeros((128,128),bool);mask[81:121,45:87]=True
            assert np.array_equal(base[~mask],edited[~mask]),name+' protected body'
        added[name]=append(cel,src,0,{'operation':'protectedbody passingleg composite' if args.passing_mode=='painted' else 'same-clock heldpose control','protected_body_frame':source_id,'allowed_roi':[45,81,87,121]})
    animations['south_walk']['frames']=[5,0,1,added['south_A'],2,3,4,added['south_B']]
    animations['north_walk']['frames']=[48,49,51,added['north_A'],50,52,53,added['north_B']]
    for direction in ['north','south']:
        animations[f'{direction}_walk']['holds']=[.05625]*8

atlas=Image.new("RGBA",(CELL*8,CELL*((len(frames)+7)//8)))
for i,im in enumerate(frames):
    atlas.alpha_composite(im,(i%8*CELL,i//8*CELL))
atlas.save(OUT/'atlas.png')
manifest={"schema":"emberwake-animation/v1","cell":[128,128],"columns":8,"pivot":[64,112],"draw_scale":.66,"passing_mode":args.passing_mode,
"animations":animations,"lineage":lineage,"provider":"OpenAI built-in ImageGen","note":"Body is unarmed. Independent spell effects and physical ground root. West WALK is symmetric mirror of pose-guided east keys; other west actions independently generated. Source8north contact reused in slot9 to avoid wrong-arm returned key."}
(OUT/'animations.json').write_text(json.dumps(manifest,indent=2)+'\n')

# Readable actual selected-frame proof at native and game height, no producer score.
proof=Image.new("RGB",(8*132,4*6*150),'#172d30')
d=ImageDraw.Draw(proof)
for row,(name,clip) in enumerate(animations.items()):
    for col,i in enumerate(clip['frames']):
        proof.paste(frames[i],(col*132,row*150+18),frames[i])
    d.text((4,row*150+2),name,fill='#e8ca90')
proof.save(OUT/'selected-contact-sheet.png')
game_proof=Image.new('RGB',(760,24*90),'#193735');gd=ImageDraw.Draw(game_proof)
for row,(name,clip) in enumerate(animations.items()):
    gd.text((2,row*90),name,fill='#f1d19c')
    for j,i in enumerate(clip['frames']):
        cel=frames[i].resize((84,84),Image.Resampling.NEAREST)
        game_proof.paste(cel,(j*92,row*90+10),cel)
game_proof.save(OUT/'game-scale-proof.png')
(OUT/'BAKE-RECEIPT.json').write_text(json.dumps({"atlas_sha256":digest(OUT/'atlas.png'),"manifest_sha256":digest(OUT/'animations.json'),"frames":len(frames),"selected_clips":len(animations),"unselected_original_sidewalk_frames":12,"rules":"constant source registration plus explicit measured root/row translation, component cleanup, duplicate/reject/mirror and exact upperbody passingleg preservation; no inferred hidden anatomy"},indent=2)+'\n')
print(f"Baked{len(frames)}frames, {len(animations)}clips. Atlas{atlas.size}.")

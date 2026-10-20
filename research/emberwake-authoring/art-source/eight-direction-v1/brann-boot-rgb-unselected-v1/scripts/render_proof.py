from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[1]
ground=Image.open(R/'inputs/forest-ground.png').convert('RGBA');forest=ground.crop((800,0,928,128));forest.save(R/'inputs/forest-ground-stage-crop.png');bgs={'forest':forest,'dark':Image.new('RGBA',(128,128),(18,30,25,255)),'light':Image.new('RGBA',(128,128),(233,233,222,255))}
for name,bg in bgs.items():
 for size,label in [(128,'native'),(256,'2x'),(84,'game')]:
  for group,seq in [('03-04-05',[3,4,5]),('full8',list(range(8)))]:
   c=Image.new('RGBA',(len(seq)*size,2*(size+20)),(29,34,43,255));d=ImageDraw.Draw(c)
   for row,folder in enumerate(['inputs/control','candidate']):
    for j,i in enumerate(seq):
     z=bg.copy();z.alpha_composite(Image.open(R/folder/f'{i:02}.png').convert('RGBA'));z=z.resize((size,size),Image.Resampling.NEAREST);c.alpha_composite(z,(j*size,row*(size+20)+20));d.text((j*size+3,row*(size+20)+2),f'{"original" if row==0 else "RGBtrial"} {i:02}',fill='white')
   c.save(R/'proof'/f'{group}-{name}-{label}.png')
# Fixedlowercrop on actualforest, before/after; nearest4x isdiagnosticonly.
c=Image.new('RGBA',(3*224,2*170),(29,34,43,255));d=ImageDraw.Draw(c)
for row,folder in enumerate(['inputs/control','candidate']):
 for j,i in enumerate([3,4,5]):
  z=forest.copy();z.alpha_composite(Image.open(R/folder/f'{i:02}.png').convert('RGBA'));z=z.crop((42,82,98,119)).resize((224,148),Image.Resampling.NEAREST);c.alpha_composite(z,(j*224,row*170+20));d.text((j*224+3,row*170+2),f'{"original"if row==0 else"RGBtrial"} {i:02}',fill='white')
c.save(R/'proof/lower-before-after-forest-4x.png')
# LiteralRGBdiff positions, not alphadifferences.
c=Image.new('RGBA',(3*128,148),(29,34,43,255));d=ImageDraw.Draw(c)
for j,i in enumerate([3,4,5]):
 z=Image.open(R/'inputs/control'/f'{i:02}.png').convert('RGBA');o=Image.open(R/'masks'/f'{i:02}-RGB-owner.png');z.paste((255,80,220,255),(0,0,128,128),o);c.alpha_composite(z,(j*128,20));d.text((j*128+3,2),f'RGBdiff {i:02}',fill='white')
c.save(R/'proof/RGB-diff-native.png');c.resize((c.width*2,c.height*2),Image.Resampling.NEAREST).save(R/'proof/RGB-diff-2x.png')
(R/'proof/index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{background:#1d222b;color:white;font:16px sans-serif}img{image-rendering:pixelated;max-width:100%}</style><h1>Brann03–05 local leather separation trial</h1><p>Unselected, newly authored source-palette RGB strokes only. Originalalpha/silhouette/pose/upper exact. Same8drawings and.45s clock. Existing upperleft leather light and rear overlap shadow; no globalcoloroperation.</p>'+''.join(f'<p>{n}</p><img src="{n}.png">' for n in ['03-04-05-forest-native','03-04-05-forest-2x','03-04-05-forest-game','lower-before-after-forest-4x','RGB-diff-2x','full8-forest-game','full8-dark-game','03-04-05-light-native']))
(R/'BACKGROUND-RECEIPT.json').write_text(json.dumps({'forest_source':'inputs/forest-ground.png','readonly_original':'/home/astra/projects/emberwake-demo/assets/world/ground.png','exactcrop_native':[800,0,928,128],'forest_crop':'inputs/forest-ground-stage-crop.png','allpanels_sameper-cellbackground':True,'nearestproxy':[84,128],'stagesize':[128,128]},indent=2)+'\n')
print('CompactRGBproofready')

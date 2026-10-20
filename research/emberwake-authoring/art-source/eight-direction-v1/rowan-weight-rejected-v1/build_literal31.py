"""One root-authorized31pixel authored undercoat completion; no curve change."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
Q=Path(__file__).resolve().parent;R=Q/'sourcefield-probe-v1';O=Q/'literal31-completion-v1';O.mkdir(exist_ok=False)
for n in ['frames','layers','proof','maps','masks']:(O/n).mkdir()
def a(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Exact source-coordinate decisions, reviewed against native source/probe joins.
PAINT={2:[([65,76],[65,78]),([67,76],[67,78]),([53,80],[53,82]),([54,80],[54,82])]+[([x,81],[x,83])for x in range(55,61)],6:[([65,76],[65,78]),([66,76],[66,78]),([67,76],[67,78]),([64,77],[64,79]),([64,78],[64,80]),([68,78],[68,80]),([63,79],[63,81]),([68,79],[68,81]),([63,80],[63,82]),([69,80],[69,82])]+[([x,81],[x,83])for x in range(54,63)]+[([69,81],[69,83]),([70,82],[70,84])]}
journal=[];records=[]
for i in range(8):
 source=a(Q/f'inputs/current/{i:02}.png');before=a(R/f'frames/{i:02}.png');layer=np.zeros_like(before);xy=np.full((128,128,2),-1,np.int16);mask=np.zeros((128,128),bool)
 for target,donor in PAINT.get(i,[]):
  x,y=target;sx,sy=donor
  assert before[y,x].tolist()==[0,0,0,0]
  assert all(a(R/f'layers/{i:02}-{name}.png')[y,x,3]==0 for name in ['fixed-lower','left-mapped-cloth','right-mapped-cloth','body-rigid'])
  assert source[sy,sx,3]>0
  layer[y,x]=source[sy,sx];xy[y,x]=[sx,sy];mask[y,x]=1
  journal.append({'phase':i,'at':target,'before_rgba':[0,0,0,0],'new_rgba':source[sy,sx].tolist(),'donor':{'file':f'../inputs/current/{i:02}.png','sha256':sha(Q/f'inputs/current/{i:02}.png'),'at':donor},'chosen_material':'New authored cream trouser/undercoat continuation, source-shaded ochre shadow','depth':'Behind unchanged fixed lower, mapped cloth, then rigid upper','why_internal_continuity':'Conservative green interior waist-gap witness in generation-guide-v1; connects retained cream mass directly below the raised hem; not an outer silhouette fill','hidden_anatomy_recovered':False})
 after=before.copy();after[mask]=layer[mask]
 assert np.array_equal(after[~mask],before[~mask]);assert np.array_equal(after[before[...,3]>0],before[before[...,3]>0]);assert int(np.any(after!=before,axis=2).sum())==len(PAINT.get(i,[]))
 p=O/f'frames/{i:02}.png'
 if i not in PAINT:shutil.copyfile(R/f'frames/{i:02}.png',p)
 else:Image.fromarray(after).save(p)
 Image.fromarray(layer).save(O/f'layers/{i:02}-new-authored-undercoat.png');Image.fromarray(mask.astype('uint8')*255).save(O/f'masks/{i:02}-literal31-new-coverage.png');np.savez_compressed(O/f'maps/{i:02}-new-undercoat-donors.npz',source_xy=xy,owner=mask)
 records.append({'phase':i,'file':str(p),'sha256':sha(p),'changed_from_rejected_probe':int(mask.sum()),'all_existing_positive_probe_pixels_RGBA_exact':True,'other6_PNG_bytes_exact':i in PAINT or sha(p)==sha(R/f'frames/{i:02}.png')})
(O/'LITERAL-UNDERCOAT-JOURNAL.json').write_text(json.dumps({'status':'One root-authorized31pixel seam completion, still pending visual result','authorization':'Root message: separate ONE minimal literal seam-completion test for31green visually interior losses; only02/06; other6 exact','method':'31 literal same-cel source-shaded authored coverage pixels. No hidden anatomy recovery, RGB segmentation, curve change or generation.','edits':journal},indent=2)+'\n')
(O/'OUTPUTS.json').write_text(json.dumps(records,indent=2)+'\n')
for size,tag in [(128,'native'),(256,'2x'),(84,'84')]:
 for bg,label in [('#e9e4d7','light'),('#1d222b','dark'),('#344c32','forest')]:
  board=Image.new('RGBA',(8*size,3*(size+20)),bg);dr=ImageDraw.Draw(board)
  for row,bank in enumerate([Q/'inputs/current',R/'frames',O/'frames']):
   for i in range(8):
    board.alpha_composite(Image.open(bank/f'{i:02}.png').resize((size,size),Image.Resampling.NEAREST),(size*i,row*(size+20)+20));dr.text((size*i+2,row*(size+20)+2),f'{["selected","REJECTED raw","31pixel test"][row]} {i:02}',fill='white'if label!='light'else'black')
  board.convert('RGB').save(O/f'proof/full8-{tag}-{label}.png')
  pairs=Image.new('RGBA',(8*size,4*(size+20)),bg);dr=ImageDraw.Draw(pairs)
  for bankrow,bank in enumerate([Q/'inputs/current',O/'frames']):
   for i in range(8):
    col=i%4;row=i//4+2*bankrow;j=(i+1)%8;x=col*2*size;y=row*(size+20)
    dr.text((x+2,y+2),f'{"selected"if bankrow==0 else"31pixel"} {i:02}>{j:02}',fill='black'if label=='light'else'white')
    for off,k in enumerate([i,j]):pairs.alpha_composite(Image.open(bank/f'{k:02}.png').resize((size,size),Image.Resampling.NEAREST),(x+off*size,y+20))
  pairs.convert('RGB').save(O/f'proof/cyclic-pairs-{tag}-{label}.png')
# Actual near-waist before/after coverage, 16x nearest.
board=Image.new('RGBA',(3*720,2*440),'#e9e4d7');dr=ImageDraw.Draw(board)
for row,i in enumerate([2,6]):
 after=a(O/f'frames/{i:02}.png');marked=after.copy()
 for target,_ in PAINT[i]:x,y=target;marked[y,x]=[20,220,90,255]
 for col,(label,image)in enumerate([('REJECTED raw',a(R/f'frames/{i:02}.png')),('31pixel authored continuation',after),('green=exact new coverage',marked)]):
  im=Image.fromarray(image).crop((44,72,89,98)).resize((720,416),Image.Resampling.NEAREST);board.alpha_composite(im,(col*720,row*440+24));dr.text((col*720+2,row*440+3),f'{i:02} {label}',fill='black')
board.convert('RGB').save(O/'proof/02-06-literal31-waist-16x.png')
manifest={'canvas':[128,128],'loop':True,'duration':[9,20],'frames':[{'file':f'{i:02}.png','sha256':sha(O/f'frames/{i:02}.png'),'hold':[9,160]}for i in range(8)]};(O/'frames/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'authored_pixels':len(journal),'changed_frames':[2,6],'other6_exact':True,'out':str(O)},indent=2))

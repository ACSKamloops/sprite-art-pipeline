"""Pose-specific source art comparison. No source-exact or gait acceptance claim."""
from pathlib import Path
from PIL import Image,ImageDraw
import sys,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1]/'captain-upright-rig-v1';sys.path.insert(0,str(R));import render,construct
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Redundant generated keys are excluded. Reading order is not trusted as a motion clock.
order=[0,1,2,3,4,6]
holds=[200,200,200,200,200,200]
labels=['far contact proposal','near release/passing proposal','near incoming proposal','near support/far release proposal','far passing proposal','far incoming proposal']
OUT=P/'artifacts/six-key-trial-v1';assert not OUT.exists(),'Preserve previous experiments';OUT.mkdir(parents=True);(OUT/'frames').mkdir();cfg,parts,construction=construct.construct(OUT/'master-parts');motion=json.loads((R/'motion.json').read_text());frames=[]
upperorder=[n for n in render.ORDER if not n.startswith(('far_','near_'))];bg=(35,38,44,255);sheet=Image.new('RGBA',(768,560),bg);dr=ImageDraw.Draw(sheet)
for i,cell in enumerate(order):
 q=i/len(order);layers,meta=render.pose(cfg,parts,motion,q);im=Image.new('RGBA',(256,256));im.alpha_composite(layers['cape']);im.alpha_composite(layers['backpack_halo']);leg=Image.open(P/'cells'/f'{cell:02}.png').convert('RGBA');dx=round(meta['pelvis'][0]-130);dy=round(meta['pelvis'][1]-129);im.alpha_composite(leg,(66+dx,120+dy))
 for n in upperorder:
  if n not in ['cape','backpack_halo']:im.alpha_composite(layers[n])
 file=f'frames/{i:02}.png';im.save(OUT/file);frames.append({'index':i,'file':file,'sha256':sha(OUT/file),'phase_label':labels[i],'duration_ms':holds[i],'source_cell':cell});xy=(i%3*256,i//3*280);sheet.alpha_composite(im,xy);dr.text((xy[0]+5,xy[1]+260),f'{i}: cell {cell}',fill='white')
sheet.convert('RGB').save(OUT/'six-keys-native.png');sheet.resize((1536,1120),Image.Resampling.NEAREST).convert('RGB').save(OUT/'six-keys-2x.png')
spec={'schema':'motion-audition/v1','label':'UNAPPROVED phase-specific lowerbody source study','canvas':[256,256],'cycle_ms':1200,'stage':[768,640],'origin':[96,80],'root_stride':[0,0],'root_policy':'in_place','camera':'fixed','frames':frames};(OUT/'audition.json').write_text(json.dumps(spec,indent=2)+'\n');(OUT/'construction.json').write_text(json.dumps({'state':'UNAPPROVED_HYBRID_SOURCE_EXPERIMENT','generated_sheet_sha256':sha(P/'native-sheet.png'),'cell_order':order,'registration':'One common placement66,120 for all cells, plus shared pelvis translation from exact master rig; no cell fitting','upper_source_sha256':sha(R/cfg['source']),'upper_renderer_sha256':sha(R/'render.py'),'limits':['Selected six generated keys; phase labels are proposals','Generated lower limbs redraw motifs and geometry','No quantitative hip registration or floor support proof','Upper load trajectory borrowed for comparison; not tuned to six source keys','Cannot approve gait from this construction report']},indent=2)+'\n');print(OUT)

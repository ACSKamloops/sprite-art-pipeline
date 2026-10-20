from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import csv,hashlib,json,importlib.util
R=Path('/home/astra/projects/emberwake-demo')
P=Path('/home/astra/artifacts/emberwake-walk-game-preview-v10')
O=Path(__file__).parent
D=O/'proofs';D.mkdir(exist_ok=True)
C=O/'cels';C.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba(im):return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
config=R/'art-source/eight-direction-v1/registration-v10-brann-front-weight.json'
plan=json.loads(config.read_text());base=json.loads((R/'art-source/eight-direction-v1/BASELINE.json').read_text())
bake=json.loads((P/'bake/REPLAY.json').read_text())
assert sha(config)==bake['config_sha256']
inputs=set([config,R/'scripts/bake_eight_directions.py',R/'art-source/eight-direction-v1/BASELINE.json',R/'art-source/eight-direction-v1/PROMPT-CONTRACT.txt',P/'bake/REPLAY.json',P/'project/scripts/hero.gd'])
exposures=[];clips=[];comparison=[];allcel={}
views=['southeast','southwest','northeast','northwest']
for actor in ('rowan','lyra','brann'):
 b=P/'bake'/actor;m=json.loads((b/'animations.json').read_text());lineage=json.loads((b/'lineage.json').read_text())
 ap=P/'project'/base['characters'][actor]['atlas'];mp=P/'project'/base['characters'][actor]['manifest']
 assert sha(ap)==sha(b/'atlas.png') and sha(mp)==sha(b/'animations.json')
 inputs.update([ap,mp,b/'atlas.png',b/'animations.json',b/'lineage.json',b/'source-ownership.json'])
 for key in ('frozen_atlas','frozen_manifest','appearance'):inputs.add(R/base['characters'][actor][key])
 atlas=Image.open(ap).convert('RGBA');cols=m['columns'];old=json.loads((R/base['characters'][actor]['frozen_manifest']).read_text())
 oldatlas=Image.open(R/base['characters'][actor]['frozen_atlas']).convert('RGBA')
 oldcells=[]
 for v in ('south','east','north','west'):
  for action in ('attack','cast'):
   for i in old['animations'][v+'_'+action]['frames']:
    oldcells.append(oldatlas.crop((i%old['columns']*128,i//old['columns']*128,i%old['columns']*128+128,i//old['columns']*128+128)))
 cardinal_rgba={rgba(x) for x in oldcells};cardinal_mirror_rgba=set()
 for im in oldcells:
  reflected=Image.new('RGBA',(128,128));reflected.alpha_composite(ImageOps.mirror(im),(1,0));cardinal_mirror_rgba.add(rgba(reflected))
 for view,s in plan['actors'][actor].items():
  raw=R/s['raw'];assert sha(raw)==s['raw_sha256'];inputs.add(raw)
  for cell,item in s.get('cell_overrides',{}).items():
   if int(cell) in (8,9,10,11,12,13,14,17,18,19,20,22):
    file=R/item['path'];assert sha(file)==item['sha256'];inputs.add(file)
  if actor=='brann':
   ab='se' if view=='southeast' else 'ne';prefix=R/'art-source/eight-direction-v1/brann-source'
   inputs.update([prefix/f'receipts/brann-{ab}-request.json',prefix/f'receipts/brann-{ab}-raw.json',prefix/f'prompts/brann-{ab}-initial.txt'])
  else:
   req=R/f'art-source/eight-direction-v1/requests/{actor}-{view}-request.json';record=json.loads(req.read_text());inputs.add(req);inputs.add(R/record['prompt'])
 for view in views:
  donor={'southwest':'southeast','northwest':'northeast'}.get(view,view);s=plan['actors'][actor][donor]
  for action in ('attack','cast'):
   clip=m['animations'][view+'_'+action];row={'hero':actor,'view':view,'action':action,**clip,'duration':sum(clip['holds'])};clips.append(row)
   for phase,(idx,hold) in enumerate(zip(clip['frames'],clip['holds'])):
    entry=lineage[idx];cell=entry['source_cell'];cel=atlas.crop((idx%cols*128,idx//cols*128,idx%cols*128+128,idx//cols*128+128))
    selected=P/f'bake/{actor}/{donor}/{cell:02}.png';inputs.add(selected)
    source=Image.open(selected).convert('RGBA')
    if view!=donor:
     mirrored=Image.new('RGBA',(128,128));mirrored.alpha_composite(ImageOps.mirror(source),(1,0));source=mirrored
    assert rgba(cel)==rgba(source),(actor,view,action,phase,'preview != selected')
    dest=C/actor/view;dest.mkdir(parents=True,exist_ok=True);cel.save(dest/f'{cell:02}.png')
    allcel[(actor,view,cell)]=cel
    override=entry.get('selected_override')
    record={'hero':actor,'view':view,'action':action,'phase':phase,'atlas_index':idx,'source_cell':cell,'hold_seconds':hold,'start_seconds':sum(clip['holds'][:phase]),'baked_selected_file':str(selected),'baked_selected_png_sha256':sha(selected),'rgba_sha256':rgba(cel),'raw_source':s['raw'],'raw_sha256':s['raw_sha256'],'painted_source_view':donor,'conditional_mirror':view!=donor,'selected_override':override,'preview_atlas':str(ap),'preview_atlas_sha256':sha(ap),'exact_cardinal_action_rgba_reuse':rgba(cel) in cardinal_rgba,'exact_mirrored_cardinal_action_rgba_reuse':rgba(cel) in cardinal_mirror_rgba}
    exposures.append(record)
 # Determine exact frame reuse within corresponding action timelines.
 for view in ('southeast','northeast'):
  for action in ('attack','cast'):
   rows=[e for e in exposures if (e['hero'],e['view'],e['action'])==(actor,view,action)]
   comparison.append({'hero':actor,'view':view,'action':action,'exposures':len(rows),'unique_rgba':len(set(e['rgba_sha256'] for e in rows)),'exact_cardinal_matches':sum(e['exact_cardinal_action_rgba_reuse'] for e in rows),'exact_cardinal_mirror_matches':sum(e['exact_mirrored_cardinal_action_rgba_reuse'] for e in rows)})
# Record hybrid recipe and donor inputs without reading previous art reviews.
h=R/'art-source/eight-direction-v1/rowan-cast-hybrid-v1'
inputs.update([h/'construction-spec.json',h/'build_hybrid.py',h/'input-hashes.json',h/'production.json'])
for view in ('southeast','northeast'):
 for name in ('00-cast-prep.png','02-cast-recovery.png'):inputs.add(h/'inputs/donors'/view/name)
 for n in (17,18,20,22):inputs.add(h/'inputs/registered'/view/f'{n:02}.png')
# All input source bytes are bound before visual inspection; no source is written.
ledger=[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(inputs)]
(O/'input-before.json').write_text(json.dumps(ledger,indent=2)+'\n')
(O/'clips.json').write_text(json.dumps(clips,indent=2)+'\n')
(O/'exposures.json').write_text(json.dumps(exposures,indent=2)+'\n')
(O/'reuse-checks.json').write_text(json.dumps(comparison,indent=2)+'\n')
font=ImageFont.load_default();grounds={'light':'#e7e3d6','dark':'#22252b','game':'#27392f'}
for actor in ('rowan','lyra','brann'):
 for action in ('attack','cast'):
  for n in (128,84,256):
   for ground,bg in grounds.items():
    width=8 if action=='attack' else 6;cw=n+8;rh=n+26
    sheet=Image.new('RGB',(width*cw+8,4*rh+30),bg);draw=ImageDraw.Draw(sheet);fg='#171717' if ground=='light' else '#eee9df'
    draw.text((8,6),f'{actor} {action} | actual v10 preview | {n}px whole canvas NEAREST | {ground}',fill=fg,font=font)
    for row,view in enumerate(views):
     seq=[e for e in exposures if (e['hero'],e['view'],e['action'])==(actor,view,action)]
     for col,e in enumerate(seq):
      x=8+col*cw;y=30+row*rh
      code = dict(southeast="SE", southwest="SW", northeast="NE", northwest="NW")[view]
      draw.text((x,y),f'{code} p{e["phase"]} c{e["source_cell"]}',fill=fg,font=font)
      cel=allcel[(actor,view,e['source_cell'])].resize((n,n),Image.Resampling.NEAREST)
      sheet.paste(Image.alpha_composite(Image.new('RGBA',(n,n),bg),cel).convert('RGB'),(x,y+18))
    sheet.save(D/f'{actor}-{action}-{n}-{ground}.png')
print(json.dumps({'clips':len(clips),'exposures':len(exposures),'distinct_actor_view_cells':len(allcel),'inputs_bound':len(ledger),'source_project_atlas_and_manifest_equal':True,'source_mirror_matches_all_exposures':True,'reuse_checks':comparison},indent=2))

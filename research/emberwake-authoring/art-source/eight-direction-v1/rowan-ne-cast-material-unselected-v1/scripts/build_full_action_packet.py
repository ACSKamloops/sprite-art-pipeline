#!/usr/bin/env python3
"""Freeze the existing trial and create an anonymous full-action review packet."""
from pathlib import Path
import hashlib,json,shutil,sys
from PIL import Image,ImageOps,ImageDraw
import numpy as np

ART=Path(__file__).resolve().parents[1]
FROZEN_INPUT=Path(__file__).resolve().parent/'frozen-source'
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else ART/'full-action-review'
assert DEST.is_absolute() and not DEST.exists(), 'Use a fresh absolute packet directory'
DEST.mkdir(); INPUT=DEST/'input'; INPUT.mkdir(); SOURCE=DEST/'frozen-source';SOURCE.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(im):return hashlib.sha256(im.tobytes()).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,indent=2)+'\n')

original=Path('/home/astra/artifacts/emberwake-walk-game-preview-v10/bake/rowan')
project=Path('/home/astra/projects/emberwake-demo')
dependencies={} if FROZEN_INPUT.is_dir() else json.loads((ART/'dependency-hashes.json').read_text())
if not FROZEN_INPUT.is_dir():
    for p,h in dependencies.items():assert sha(p)==h, f'Stale dependency: {p}'

# Parent-only frozen sources retain all provenance. None is copied into input.
freeze=[('current/atlas.png',original/'atlas.png'),('current/animations.json',original/'animations.json'),
 ('registration-v10-brann-front-weight.json',project/'art-source/eight-direction-v1/registration-v10-brann-front-weight.json'),
 ('bake_eight_directions.py',project/'scripts/bake_eight_directions.py'),
 ('trial/17.png',ART/'trial/17.png'),('trial/18.png',ART/'trial/18.png'),
 ('game-ground-crop.png',ART/'inputs/game-ground-crop.png'),
 ('game-ground-source.json',ART/'inputs/game-ground-source.json')]
for n in [22,17,18,19,20]:freeze.append((f'current/northeast/{n}.png',original/'northeast'/f'{n:02}.png'))
for name in ['dependency-hashes.json','source-color-plan.json','source-color-witnesses.json','SOURCE-WITNESS-VALIDATION.json','MECHANICAL-CHECKS.json','editable/initial.json','editable/project.json','editable/journal.json','editable/receipt.json']:
    freeze.append((f'material-source/{name}',ART/name))
for n in [17,18]:
    freeze.extend((f'material-source/maps/northeast-{n}-{suffix}',ART/'inputs/maps'/f'northeast-{n}-{suffix}') for suffix in ['source-map.npz','donor-target-mask.png','warp-controls.json'])
if FROZEN_INPUT.is_dir():
    # Portable replay depends only on this packet's frozen files, not the live
    # project/artifact locations recorded for provenance by the producer.
    previous=json.loads((FROZEN_INPUT.parent/'SOURCE-HASHES.json').read_text())
    freeze=[]
    for record in previous:
        p=FROZEN_INPUT.parent/record['frozen']
        assert sha(p)==record['sha256'], f'Frozen source changed: {p}'
        freeze.append((str(Path(record['frozen']).relative_to('frozen-source')),p))
source_receipt=[]
for name,p in freeze:
    q=SOURCE/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    source_receipt.append({'frozen':str(q.relative_to(DEST)),'original':str(p),'sha256':sha(q)})
dump(DEST/'SOURCE-HASHES.json',source_receipt)
for n,h in [(17,'34994179d19ad50a23fd2d92f6afa0432d86c1cad924f7101a2f832307fdeea8'),
            (18,'6a0d8b56defe754683468abf23cfd28d0935922114d99e90001b83380376064c')]:
    assert sha(SOURCE/'trial'/f'{n}.png')==h, 'The73+73trial must stay frozen'

atlas=Image.open(SOURCE/'current/atlas.png').convert('RGBA')
manifest=json.loads((SOURCE/'current/animations.json').read_text())
cols=manifest['columns'];assert manifest['cell']==[128,128]
def cel(i):return atlas.crop(((i%cols)*128,(i//cols)*128,(i%cols+1)*128,(i//cols+1)*128))
def mirror(im):
    out=Image.new('RGBA',im.size);out.alpha_composite(ImageOps.mirror(im),(1,0));return out
def same(a,b):return a.tobytes()==b.tobytes()
holds=[60,80,100,80,80,100];physical=[22,17,18,19,20,22]
variants={};proof=[]
for view in ['northeast','northwest']:
    clip=manifest['animations'][view+'_cast']
    assert clip['loop'] is False and [round(x*1000) for x in clip['holds']]==holds
    variants[view]={'A':[cel(i) for i in clip['frames']]}
    if view=='northeast':
        for n,im in zip(physical,variants[view]['A']):assert same(im,Image.open(SOURCE/'current/northeast'/f'{n}.png').convert('RGBA'))
        trial=[im.copy() for im in variants[view]['A']]
        trial[1]=Image.open(SOURCE/'trial/17.png').convert('RGBA');trial[2]=Image.open(SOURCE/'trial/18.png').convert('RGBA')
    else:
        assert all(same(a,mirror(b)) for a,b in zip(variants[view]['A'],variants['northeast']['A']))
        trial=[mirror(im) for im in variants['northeast']['B']]
    variants[view]['B']=trial
    changes=[]
    for i,(a,b) in enumerate(zip(variants[view]['A'],trial)):
        aa=np.array(a);bb=np.array(b);count=int(np.any(aa!=bb,axis=2).sum())
        assert np.array_equal(aa[:,:,3],bb[:,:,3]);assert count==(73 if i in [1,2] else 0)
        changes.append(count)
    proof.append({'direction':view,'actual_current_atlas_indices':clip['frames'],
       'physical_cells':physical,'holds_ms':holds,'loop':False,
       'changed_rgba_pixels_by_exposure':changes,'alpha_exact_all_exposures':True})

frame_records=[]
for view,vs in variants.items():
    for name,frames in vs.items():
        d=INPUT/'frames'/view/name;d.mkdir(parents=True)
        for i,im in enumerate(frames):
            p=d/f'{i:02}.png';im.save(p)
            frame_records.append({'file':str(p.relative_to(INPUT)),'rgba_sha256':rgba(im),'png_sha256':sha(p),'hold_ms':holds[i]})

ground=Image.open(SOURCE/'game-ground-crop.png').convert('RGBA')
def tile(im,bg,size):
    if size!=128:im=im.resize((size,size),Image.Resampling.NEAREST)
    b=ground.resize((size,size),Image.Resampling.NEAREST) if bg=='game' else Image.new('RGBA',(size,size),'#dedbd0' if bg=='light' else '#24272b')
    b.alpha_composite(im);return b
def save_apng(p,frames,durations):
    frames[0].save(p,format='PNG',save_all=True,append_images=frames[1:],duration=durations,loop=1,disposal=0,blend=0)
    im=Image.open(p);assert im.n_frames==len(frames)
    actual=[]
    for i,f in enumerate(frames):
        im.seek(i);assert same(im.convert('RGBA'),f);actual.append(im.info['duration'])
    assert actual==durations
    return {'file':str(p.relative_to(INPUT)),'sha256':sha(p),'decoded_rgba_exact':True,'holds_ms':actual,'plays':1}

media=[]
(INPUT/'proofs').mkdir()
for view,vs in variants.items():
    for bg in ['light','dark','game']:
        for size in [128,84,256]:
            tiles={name:[tile(im,bg,size) for im in frames] for name,frames in vs.items()}
            pad=10;left=38;top=26
            strip=Image.new('RGBA',(left+6*(size+pad)+pad,top+2*(size+pad)+20),'#c7c5bc');d=ImageDraw.Draw(strip)
            for i,h in enumerate(holds):d.text((left+i*(size+pad),5),f'{i+1}: {h}ms',fill='black')
            for row,name in enumerate(['A','B']):
                d.text((10,top+row*(size+pad)+size//2),name,fill='black')
                for i,t in enumerate(tiles[name]):strip.alpha_composite(t,(left+i*(size+pad),top+row*(size+pad)))
                media.append(save_apng(INPUT/'proofs'/f'{view}-{name}-{bg}-{size}-oneshot.png',tiles[name],holds))
            d.text((6,strip.height-17),f'{view} / {size}px / {bg} / same500ms, nonloop / offline',fill='black')
            strip.convert('RGB').save(INPUT/'proofs'/f'{view}-paired-{bg}-{size}.png')
            # Pair canvas includes both complete stages; no clipping at its right edge.
            together=[]
            for i in range(6):
                pair=Image.new('RGBA',(2*size+30,size+24),'#c7c5bc');dd=ImageDraw.Draw(pair);dd.text((4,5),'A',fill='black');dd.text((size+34,5),'B',fill='black');pair.alpha_composite(tiles['A'][i],(0,24));pair.alpha_composite(tiles['B'][i],(size+30,24));together.append(pair)
            media.append(save_apng(INPUT/'proofs'/f'{view}-paired-{bg}-{size}-oneshot.png',together,holds))

# Current selected same-hero appearance and all four cardinal cast contexts.
(INPUT/'context').mkdir();context_records=[]
for size in [84,128,256]:
    pad=10;top=24
    appearance=Image.new('RGBA',(4*(size+pad),2*(size+pad+top)),'#c7c5bc');d=ImageDraw.Draw(appearance)
    for i,view in enumerate(manifest['directions']):
        idx=manifest['animations'][view+'_idle']['frames'][0];x=i%4*(size+pad);y=i//4*(size+pad+top)
        d.text((x+3,y+4),view,fill='black');appearance.alpha_composite(tile(cel(idx),'dark',size),(x,y+top))
    appearance.convert('RGB').save(INPUT/'context'/f'appearance-{size}.png')
    card=Image.new('RGBA',(6*(size+pad)+80,4*(size+pad+top)),'#c7c5bc');d=ImageDraw.Draw(card)
    for row,view in enumerate(['south','east','north','west']):
        clip=manifest['animations'][view+'_cast'];frames=[cel(i) for i in clip['frames']];y=row*(size+pad+top)
        d.text((5,y+top+size//2),view,fill='black')
        for i,im in enumerate(frames):
            d.text((80+i*(size+pad),y+4),f'{i+1}: {round(clip["holds"][i]*1000)}ms',fill='black');card.alpha_composite(tile(im,'dark',size),(80+i*(size+pad),y+top))
        if size in [84,128]:context_records.append(save_apng(INPUT/'context'/f'{view}-cast-{size}-oneshot.png',[tile(f,'dark',size) for f in frames],[round(h*1000) for h in clip['holds']]))
    card.convert('RGB').save(INPUT/'context'/f'cardinal-cast-{size}.png')

dump(INPUT/'manifest.json',{'schema':'anonymous-whole-cast-visual-packet/v1','character':'Rowan',
 'directions':['northeast','northwest'],'variants':['A','B'],'exposure_count':6,
 'holds_ms':holds,'duration_ms':500,'loop':False,'stage':[128,128],'render_pivot':[64,112],
 'size_84':'Explicit128to84nearest offline proof; native engine0.66draw scale not asserted pixel-identical',
 'game_backdrop':'Same current game ground-texture crop for both variants; offline composite',
 'context':'Actual current selected same-hero appearance and cardinal cast art, unchanged in both variants',
 'frames':frame_records,'media':media,'context_media':context_records})
INPUT.joinpath('README.md').write_text('''# Anonymous Rowan cast comparison\n\nCompare A and B through the whole six-exposure action: preparation, release, recovery and return. Each is500ms, nonloop, with identical60/80/100/80/80/100ms holds. Judge material consistency, section/volume continuity, hand readability and overall action against the same hero's appearance/cardinalcast context. State a preference, no useful difference, or a regression, and name remaining defects. No score or approval is requested.\n\nStart with `proofs/{northeast,northwest}-paired-{light,dark,game}-84.png` at native display size. Inspect128and nearest256and the synchronized paired one-shot APNGs, then context/appearance and context/cardinal-cast at84/128. `index.html` presents these and replays the one-shot files. APNGs make exactly one pass and stop on the final neutral; the replay control is outside the action timing.\n\nThe packet is offline visual evidence. It does not assert game rendering, external editor exchange, anatomical correctness or acceptance. The84stage is explicit nearest scaling. All frames/media are hashed in manifest.json and SHA256SUMS. Keep any implementation mapping or producer history outside this input directory.\n''')
html='''<!doctype html><meta charset="utf-8"><title>Anonymous whole-cast comparison</title><style>body{background:#c7c5bc;color:#111;font:15px sans-serif}img{image-rendering:pixelated;max-width:none}p{max-width:900px}button{margin:8px}h2{margin-top:32px}</style><h1>Rowan A / B whole-cast comparison</h1><p>Six exposures;500ms; nonloop. Compare complete preparation → release → recovery against the same hero's appearance and cardinalcast context. No score or approval is requested.</p><button onclick="document.querySelectorAll('img[data-replay]').forEach(x=>{let s=x.src.split('?')[0];x.src=s+'?t='+Date.now()})">Replay one-shot animations</button>'''
for size in [84,128,256]:
    html+=f'<h2>Same hero appearance / {size}</h2><img src="context/appearance-{size}.png"><h2>Cardinal cast context / {size}</h2><img src="context/cardinal-cast-{size}.png">'
for view in ['northeast','northwest']:
    for size in [84,128,256]:
        for bg in ['light','dark','game']:
            html+=f'<h2>{view} / {size}px / {bg}</h2><img data-replay src="proofs/{view}-paired-{bg}-{size}-oneshot.png"><br><img src="proofs/{view}-paired-{bg}-{size}.png">'
INPUT.joinpath('index.html').write_text(html)

dump(DEST/'PARENT-MAPPING.json',{'do_not_supply_to_critic':True,
 'A':'Exact currentv10 selected atlas/manifest, all six exposures',
 'B':'A except frozen73pixel changes in each northeast17/18; northwest uses the exact existing mirror+1pixel correction',
 'source_trial_png_sha256':{str(n):sha(SOURCE/'trial'/f'{n}.png') for n in [17,18]},
 'scope':'Full-action comparison authorization only; no selection, score, new paint, native full bank, editor or canonical writes',
 'proof':proof})
shutil.copy2(__file__,DEST/'replay_packet.py')
# Hashes include source, replay and anonymous packet, but keep the mapping outside input.
for folder in [INPUT,DEST]:
    files=sorted(p for p in folder.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
    folder.joinpath('SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(folder))+'\n' for p in files))
print(json.dumps({'packet':str(DEST),'critic_input':str(INPUT),'variants':proof,
                  'frozen_trial_sha256':{str(n):sha(SOURCE/'trial'/f'{n}.png') for n in [17,18]},
                  'manifest_sha256':sha(INPUT/'manifest.json')},indent=2))

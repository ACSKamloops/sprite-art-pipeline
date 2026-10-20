#!/usr/bin/env python3
"""Bounded offline v11 artifact audit; writes only this audit directory."""
from pathlib import Path
import hashlib, json, struct, subprocess, time
import numpy as np
from PIL import Image, ImageOps

OUT=Path(__file__).resolve().parent
ROOT=Path('/home/astra/projects/emberwake-demo')
OLD=Path('/home/astra/artifacts/emberwake-walk-game-preview-v10')
NEW=Path('/home/astra/artifacts/emberwake-source-cel-game-preview-v11')
SERVED=Path('/home/astra/artifacts/emberwake-walk-cadence-study-v1')
CONFIG=ROOT/'art-source/eight-direction-v1/registration-v11-rowan-turn-and-brann-fist.json'
checks=[]
details={}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(ok,note,detail=None):
    checks.append({'ok':bool(ok),'note':note,**({'detail':detail} if detail is not None else {})})
def pixels(p):return Image.open(p).convert('RGBA')
def cell(im,i):return im.crop((i%16*128,i//16*128,(i%16+1)*128,(i//16+1)*128))
def diff(a,b,p=''):
    if type(a)!=type(b):return [p]
    if isinstance(a,dict):
        return sum((diff(a[k],b[k],p+'/'+str(k)) if k in a and k in b else [p+'/'+str(k)] for k in sorted(a.keys()|b.keys())),[])
    if isinstance(a,list):
        if len(a)!=len(b):return [p+'/length']
        return sum((diff(x,y,p+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    return [] if a==b else [p]

plan=read(CONFIG)
replay=read(NEW/'bake/REPLAY.json')
selection=read(NEW/'SELECTION.json')
isolation=read(NEW/'ISOLATION.json')
check(sha(CONFIG)==selection['sha256']==replay['config_sha256']==isolation['config_sha256'],'current config equals all three frozen v11 source bindings')
check(sha(ROOT/'scripts/bake_eight_directions.py')==replay['baker_sha256'],'current baker equals frozen bake receipt')
check(sha(ROOT/'scripts/build_isolated_art_preview.py')==isolation['helper_sha256'],'current isolator equals frozen isolation receipt')
hash_refs={}
for k,v in plan['files_sha256'].items():hash_refs[k]=v
for actor,views in plan['actors'].items():
    check(replay['actors'][actor]['source_registration']==views,actor+' replay registration equals complete config actor data')
    for view,s in views.items():
        hash_refs[s['raw']]=s['raw_sha256']
        for f in s.get('walk_override',{}).get('frames',[]):hash_refs[f['path']]=f['sha256']
        for f in s.get('cell_overrides',{}).values():hash_refs[f['path']]=f['sha256']
bad_refs=[k for k,v in hash_refs.items() if not (ROOT/k).is_file() or sha(ROOT/k)!=v]
check(not bad_refs,'every config source and recipe hash resolves exactly',{'unique_refs':len(hash_refs),'files_sha256_entries':len(plan['files_sha256']),'bad':bad_refs})
oldconfig=ROOT/read(OLD/'bake/rowan/animations.json')['directional_source']
check(sha(oldconfig)==read(OLD/'bake/REPLAY.json')['config_sha256'],'prior v10 config still matches frozen v10 receipt')
details['config_actor_delta']=diff(read(oldconfig)['actors'],plan['actors'])
expected={'rowan':[155,187],'lyra':[],'brann':[179,211]}
details['pixel_delta']={}
for actor in expected:
    a=pixels(OLD/'bake'/actor/'atlas.png');b=pixels(NEW/'bake'/actor/'atlas.png')
    check(a.size==b.size,actor+' atlas dimensions unchanged',list(b.size))
    aa=np.array(a);bb=np.array(b);mask=np.any(aa!=bb,axis=2)
    yy,xx=np.where(mask);changed=sorted(set((yy//128*16+xx//128).tolist()))
    entry={'changed_cells':changed,'changed_RGBA_pixels':int(mask.sum()),'atlas_sha256':sha(NEW/'bake'/actor/'atlas.png'),'cell_changes':{str(i):int(np.any(np.array(cell(a,i))!=np.array(cell(b,i)),axis=2).sum()) for i in changed},'total_physical_cells':b.width//128*(b.height//128)}
    details['pixel_delta'][actor]=entry
    check(changed==expected[actor],actor+' exact expected changed cells',entry)
    receipt=read(NEW/'SOURCE-DELTA.json')['actors'][actor]
    check(entry['changed_RGBA_pixels']==receipt['changed_RGBA_pixels'] and changed==receipt['changed_cells'] and entry['atlas_sha256']==receipt['new_atlas_sha256'],actor+' recomputed delta equals frozen SOURCE-DELTA')
    om=read(OLD/'bake'/actor/'animations.json');nm=read(NEW/'bake'/actor/'animations.json')
    changedkeys=[k for k in om.keys()|nm.keys() if om.get(k)!=nm.get(k)]
    check(changedkeys==['directional_source'],actor+' manifest changes only directional_source',changedkeys)
    check(om['animations']==nm['animations'] and om['cast_hand']==nm['cast_hand'] and om['cast_hand_tracks']==nm['cast_hand_tracks'],actor+' all 48 action bindings, holds, loops and hand tracks exact')
    for view,source_index,target_index in [('northeast',3 if actor=='rowan' else 11,155 if actor=='rowan' else 179)]:
        if actor=='lyra':continue
        s=plan['actors'][actor][view]
        source=s['walk_override']['frames'][source_index] if actor=='rowan' else s['cell_overrides'][str(source_index)]
        sourceim=pixels(ROOT/source['path'])
        check(sourceim.tobytes()==cell(b,target_index).tobytes(),actor+' selected literal source cel equals actual atlas RGBA')
        mirror=Image.new('RGBA',(128,128));mirror.alpha_composite(ImageOps.mirror(sourceim),(1,0))
        check(mirror.tobytes()==cell(b,target_index+32).tobytes(),actor+' NW is exact +1px pivot-correct source reflection')

catalog=read(NEW/'project/assets/characters/catalog.json')
for actor in catalog['characters']:
    for kind,filename in [('atlas','atlas.png'),('manifest','animations.json')]:
        rel=actor[kind].removeprefix('res://')
        check(sha(NEW/'project'/rel)==sha(NEW/'bake'/actor['id']/filename),actor['id']+' catalog-bound '+kind+' exact bake bytes')
        row=next(x for x in isolation['resources'] if x['resource']==rel)
        check(sha(ROOT/rel)==row['production_before_sha256'] and sha(NEW/'project'/rel)==row['preview_sha256'],actor['id']+' canonical production '+kind+' remains preserved and distinct from preview')
runtime=[]
for sub in ['scripts','scenes']:
    for p in (OLD/'project'/sub).rglob('*'):
        if p.is_file() and p.suffix in ['.gd','.tscn']:
            rel=p.relative_to(OLD/'project');runtime.append(str(rel));check(sha(p)==sha(NEW/'project'/rel),'v10/v11 runtime source exact '+str(rel))
check(sha(OLD/'project/project.godot')==sha(NEW/'project/project.godot'),'v10/v11 project.godot exact')
for rel,h in read(NEW/'RUNTIME-SOURCE-EQUALITY.json')['exact_runtime_files'].items():
    check(sha(OLD/'project'/rel)==sha(NEW/'project'/rel)==h,'runtime equality receipt current '+rel)
check(sha(OLD/'project/assets/characters/catalog.json')==sha(NEW/'project/assets/characters/catalog.json'),'v10/v11 catalog resource paths unchanged')
bad_copy=[k for k,h in isolation['copied_source_hashes'].items() if not (ROOT/k).is_file() or sha(ROOT/k)!=h]
check(not bad_copy,'all copied canonical source hashes still match isolation receipt',{'files':len(isolation['copied_source_hashes']),'bad':bad_copy})

def parse_pck(path):
    data=path.read_bytes();magic,version,major,minor,patch,flags=struct.unpack_from('<6I',data)
    assert data[:4]==b'GDPC' and version==4 and flags==2
    base,directory=struct.unpack_from('<2Q',data,24)
    count=struct.unpack_from('<I',data,directory)[0];pos=directory+4;entries={}
    for _ in range(count):
        n=struct.unpack_from('<I',data,pos)[0];pos+=4
        name=data[pos:pos+n].rstrip(b'\0').decode();pos+=n
        offset,size=struct.unpack_from('<2Q',data,pos);pos+=16
        md5=data[pos:pos+16];pos+=16
        entryflags=struct.unpack_from('<I',data,pos)[0];pos+=4
        payload=data[base+offset:base+offset+size]
        assert entryflags==0 and len(payload)==size and hashlib.md5(payload).digest()==md5,(name,offset,size,entryflags)
        entries[name]=payload
    assert pos==len(data),(pos,len(data))
    return entries

packs={}
for rev in [10,11]:
    p=SERVED/f'game-v{rev}/index.pck';packs[rev]=parse_pck(p)
    check(True,f'served v{rev} PCK index parsed and every payload MD5 verified',{'sha256':sha(p),'entries':len(packs[rev])})
entries=packs[11];packbind=[]
for actor in catalog['characters']:
    manifest=actor['manifest'].removeprefix('res://')
    check(entries[manifest]==(NEW/'project'/manifest).read_bytes(),actor['id']+' actual served PCK manifest equals baked/project bytes')
    source=actor['atlas'].removeprefix('res://')
    imp=NEW/'project'/(source+'.import')
    # Export deliberately strips authoring-only deps/params and terminates remap text with NUL.
    exported_remap=entries[source+'.import'].decode().rstrip('\0').strip()
    preview_remap=imp.read_text().split('[deps]',1)[0].strip()
    check(exported_remap==preview_remap,actor['id']+' served atlas importer remap equals preview remap after explicit export stripping')
    import re
    ctex=re.search(r'path="res://([^"]+)"',imp.read_text()).group(1)
    check(entries[ctex]==(NEW/'project'/ctex).read_bytes(),actor['id']+' served imported atlas equals preview importer artifact')
    md5file=NEW/'project'/(ctex.rsplit('.',1)[0]+'.md5')
    source_md5=re.search(r'source_md5="([0-9a-f]+)"',md5file.read_text()).group(1)
    check(hashlib.md5((NEW/'project'/source).read_bytes()).hexdigest()==source_md5,actor['id']+' preview imported texture cache bound to actual source atlas MD5')
    packbind.append({'actor':actor['id'],'manifest':manifest,'imported_texture':ctex,'source_atlas_sha256':sha(NEW/'project'/source),'imported_texture_sha256':hashlib.sha256(entries[ctex]).hexdigest()})
check(entries['assets/characters/catalog.json']==(NEW/'project/assets/characters/catalog.json').read_bytes(),'actual served PCK catalog equals preview catalog')
details['served_pck_binding']=packbind
details['pck_delta']={'added':sorted(entries.keys()-packs[10].keys()),'removed':sorted(packs[10].keys()-entries.keys()),'changed':[k for k in sorted(entries.keys()&packs[10].keys()) if entries[k]!=packs[10][k]]}
for k in sorted(packs[10].keys()&entries.keys()):
    if k.endswith('.gdc'):check(entries[k]==packs[10][k],'served compiled runtime v10/v11 exact '+k)
details['served_web_files']={str(p.relative_to(SERVED/'game-v11')):sha(p) for p in sorted((SERVED/'game-v11').iterdir()) if p.is_file()}
check(details['served_web_files']['index.html']==read(NEW/'WEB-SHELL-ADJUSTMENT.json')['after_sha256'],'served game HTML matches recorded shell-adjustment hash')

fixture=read(NEW/'CAPTURE-FIXTURE-INPUTS.json')
check(sha(NEW/'capture_changed_cels.gd')==fixture['driver_sha256'],'paired still driver bound to frozen fixture input')
for rel,h in fixture['copied_v10_resources'].items():
    actor=Path(rel).name.split('-')[0];kind='atlas.png' if rel.endswith('-atlas.png') else 'animations.json'
    check(sha(NEW/'project'/rel)==sha(OLD/'bake'/actor/kind)==h,'paired still actual v10 substitution bytes '+rel)
paired=read(NEW/'paired-cels/RECEIPT.json')
check(paired['passed'] is True and not paired['failures'] and paired['assertions']==38 and len(paired['cases'])==4,'paired fixture records 38 successful checks and four cases')
details['paired_pixel_counts']=[]
for case in paired['cases']:
    path=NEW/'paired-cels'/case['screenshot'];im=np.array(pixels(path));a=im[132:236,112:208];b=im[132:236,432:528];n=int(np.any(a!=b,axis=2).sum())
    check(sha(path)==case['screenshot_sha256'] and n==case['changed_actual_crop_pixels'],'paired still actual hash and crop delta '+case['screenshot'],n)
    details['paired_pixel_counts'].append({'file':case['screenshot'],'changed_game_scale_pixels':n})

native=read(NEW/'native-walk/RECEIPT.json')
check(native['passed'] is True and not native['failures'] and native['assertions']==8684 and len(native['clips'])==6 and native['clock_hz']==320 and native['loops']==2,'native receipt existing six clips, 8684 assertions, 320Hz, two cycles')
ledger=(NEW/'native-walk/SHA256SUMS').read_text().splitlines();bad=[]
for line in ledger:
    h,rel=line.split('  ',1)
    if not (NEW/'native-walk'/rel).is_file() or sha(NEW/'native-walk'/rel)!=h:bad.append(rel)
check(not bad and len(ledger)==1729,'all 1729 native capture ledger entries verify including receipt',bad)
samplecount=0
for clip in native['clips']:
    samples=clip['samples'];folder=f"{clip['actor']}-{clip['view']}"
    check(len(samples)==288 and len(list((NEW/'native-walk'/folder).glob('*.png')))==288,'actual 288 PNGs and samples '+folder)
    check(all(s['file']==f'{folder}/{i:04d}.png' and s['tick']==i and abs(s['time']-(i+.5)/320)<1e-10 for i,s in enumerate(samples)),'native sample index/time/file binding '+folder)
    samplecount+=len(samples)
details['native_sample_count']=samplecount
media=read(NEW/'media/MEDIA-RECEIPT.json');gallery=read(SERVED/'godot-walks-v11/GALLERY-RECEIPT.json')
details['media_probes']=[]
for row in media:
    mp4=NEW/'media'/(row['clip']+'.mp4')
    cmd=['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,avg_frame_rate,duration,nb_read_frames','-of','json',str(mp4)]
    probe=json.loads(subprocess.check_output(cmd))['streams'][0]
    check(sha(mp4)==row['mp4_sha256'],'actual MP4 hash bound '+row['clip'])
    check(probe==row['probe'],'actual ffprobe matches frozen encode receipt '+row['clip'],probe)
    details['media_probes'].append({'clip':row['clip'],'sha256':sha(mp4),'probe':probe})
copybad=[]
for name,h in gallery['source_hashes'].items():
    if sha(NEW/'media'/name)!=h or sha(SERVED/'godot-walks-v11'/name)!=h:copybad.append(name)
check(not copybad and len(gallery['source_hashes'])==19,'all 19 actual served gallery media/receipt files equal source bytes',copybad)
check(sha(SERVED/'godot-walks-v11/index.html')==gallery['index_sha256'],'actual served gallery HTML equals gallery receipt')
gb=read(NEW/'GALLERY-BROWSER.json')
check(gb['passed'] is True and len(gb['receipts'])==17 and all(x['ok'] is True for x in gb['receipts']),'existing gallery browser receipt has 17 successful transport/playback checks')
browser=read(NEW/'BROWSER-EIGHT-DIRECTIONS.json');coverage=read(NEW/'BROWSER-TRACE-COVERAGE.json')
check(browser['passed'] is True and len(browser['receipts'])==193 and all(x['ok'] is True for x in browser['receipts']) and not browser['consoleMessages'] and not browser['pageErrors'],'existing ordinary-input browser JSON contains 193 true receipts, no incomplete/error receipts, console or page errors')
check(sha(NEW/'BROWSER-EIGHT-DIRECTIONS.json')==coverage['source_report_sha256'] and coverage['successful_assertions']==193 and coverage['complete_action_traces']==24,'frozen trace coverage summary bound to actual browser receipt')
details['browser_trace_counts']={'traces':len(browser['actionTraces']),'samples':sum(len(t['samples']) for t in browser['actionTraces']),'sample_range':[min(len(t['samples']) for t in browser['actionTraces']),max(len(t['samples']) for t in browser['actionTraces'])],'max_tick_gap':max(x['physics_tick_gap_max'] for x in coverage['rows']),'fps_range':[min(x['reported_fps_range'][0] for x in coverage['rows']),max(x['reported_fps_range'][1] for x in coverage['rows'])]}
for t in browser['actionTraces']:
    c=t['context'];ss=t['samples'];locked=[x['snapshot'] for x in ss if x['snapshot']['hero']['state']==c['pose'] and x['snapshot']['hero']['state_left']>0]
    if c['id']=='brann' and c['pose']=='attack' and c['view'] in ['northeast','northwest']:
        changedframe=179 if c['view']=='northeast' else 211
        observed=[s['hero']['art_frame'] for s in locked]
        details.setdefault('changed_brann_exposure_browser_samples',[]).append({'view':c['view'],'changed_frame':changedframe,'observed':observed,'changed_frame_observed':changedframe in observed})

result={'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'scope':'Offline read-only artifact/hash/pixel/probe inspection only; no engine, browser, model, network or art-grade invocation. Own audit output only.','passed':all(x['ok'] for x in checks),'checks':checks,'details':details}
(OUT/'CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':result['passed'],'checks':len(checks),'failures':[x for x in checks if not x['ok']],'details':details},indent=2))

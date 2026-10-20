#!/usr/bin/env python3
"""Build deduplicated editable project and independently measure actual draw surfaces."""
import sys,json,hashlib,math,collections
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT))
from qc.pixel_motion.check import composite,check,sha,data,diagnostic
ORDER=['rear_thigh','rear_shin','rear_foot','rear_arm','torso','head','front_thigh','front_shin','front_foot','front_arm','front_forearm']
def image(ref):
    im=Image.open(HERE/ref['path']).convert('RGBA');assert hashlib.sha256(im.tobytes()).hexdigest()==ref['rgba_sha256'];return im

def fast_sole(im):
    alpha=im.getchannel('A').point(lambda a:255 if a>=128 else 0);box=alpha.getbbox()
    if box is None:return None
    y=box[3]-1;xs=[x for x in range(box[0],box[2])if alpha.getpixel((x,y))];return {'row':y,'center':(min(xs)+max(xs))/2,'xmin':min(xs),'xmax':max(xs)}
def main():
    raw=json.loads((HERE/'gpu-observations.json').read_text());old=json.loads((ROOT/'study/layered-cutout/project.json').read_text());palette=list(old['palette']);lookup={tuple(c):i for i,c in enumerate(palette)};cels={};frames=[];refs={};unique={};colors=set();mismatches=[]
    for record in raw['dense']:
        bindings={}
        for lid in ORDER:
            ref=record['layers'][lid];im=image(ref);pixels=[]
            for color in data(im):
                if color[3]==0:color=(0,0,0,0)
                colors.add(color)
                if color not in lookup:lookup[color]=len(palette);palette.append(list(color))
                pixels.append(lookup[color])
            key=(lid,ref['rgba_sha256']);cid=unique.get(key)
            if cid is None:cid=lid+':'+ref['rgba_sha256'];unique[key]=cid;cels[cid]={'layer_id':lid,'pixels':pixels}
            bindings[lid]=cid
        fid=record['id'];frame={'id':fid,'duration_ticks':1,'cels':bindings,'landmarks':{name:[round(x)for x in part['position']]for name,part in record['snapshot']['parts'].items()}};frames.append(frame);refs[fid]={'duration_ticks':1,'landmarks':frame['landmarks'],'layers':{lid:{'path':str((HERE/record['layers'][lid]['path']).relative_to(ROOT)),'sha256':sha(HERE/record['layers'][lid]['path'])}for lid in ORDER},'composite':{'path':str((HERE/record['composite']['path']).relative_to(ROOT)),'sha256':sha(HERE/record['composite']['path'])}}
    project={'schema':'sprite-edit-project/v1','canvas':old['canvas'],'palette':palette,'layers':old['layers'],'cels':cels,'frames':frames,'animations':[{'id':'walk_dense','frames':[f['id']for f in frames],'fps':60,'loop':True,'events':[]}],'provenance':{'source':'Actual Godot render of unchanged cutout rig at60phases; framesheld1tick.','source_inputs_sha256':sha(HERE/'inputs.json'),'capture_sha256':sha(HERE/'gpu-observations.json'),'root_speed_px_s':48,'native_game_art':False,'quality_approved':False,'status':'changes_requested','no_new_anatomy':True,'source_rig_sha256':sha(HERE/'cutout_rig.gd')}}
    payload=json.dumps(project,sort_keys=True,separators=(',',':'),ensure_ascii=False);assert len(payload.encode())<=25_000_000; (HERE/'project.json').write_text(payload+'\n')
    for r,f in zip(raw['dense'],frames):
        actual,_=composite(project,f);gpu=image(r['composite']);assert actual.tobytes()==gpu.tobytes(),f['id']
        if r['index']%5==0:
            ref=Image.open(HERE/'baseline'/f"walk_{r['index']//5:02d}-composite.png").convert('RGBA')
            if gpu.tobytes()!=ref.tobytes():mismatches.append(f['id'])
    source_colors={(0,0,0,0)}
    for path in(HERE/'assets').glob('*.png'):
        source_colors.update(tuple(c)if c[3]else(0,0,0,0)for c in data(Image.open(path).convert('RGBA')))
    assert colors<=source_colors,'Generated color outside actual source part palette'
    annotations={'schema':'sprite-pixel-motion-annotations/v1','canvas':project['canvas'],'layer_order':ORDER,'alpha_threshold':128,'edge_margin':1,'frames':refs,'source_hashes':{},'actions':[{'id':'walk_dense','sequence':[f['id']for f in frames],'fps':60,'loop':True,'root_speed_px_s':48,'world_motion':'continuous','contacts':[{'layer':side+'_foot','stance_frames':[f['id']for i,f in enumerate(frames)if(i/60+(.5 if side=='rear'else 0))%1<.5],'ground_row':139,'max_ground_error_px':0,'max_boundary_slip_px':.01,'max_hold_slip_px':.5}for side in ['front','rear']]}],'unresolved':['Dense sampling does not change knee anatomy/material seams.','Hold-slip0.5px and boundary0.01px limits unchanged; no pass relabeling.','World GPU proof below measures cached raster snapping separately from local-pixel+continuous-root analytic QC.']}
    (HERE/'annotations.json').write_text(json.dumps(annotations,indent=2)+'\n');qc,renders=check(project,annotations,ROOT);qc['inputs']={'project_file_sha256':sha(HERE/'project.json'),'gpu_capture_sha256':sha(HERE/'gpu-observations.json')};diagnostic(renders,qc,HERE/'diagnostics')
    world=[];summary=[]
    for record in raw['world']:
        footmetrics={}
        for side in ['front','rear']:
            m=fast_sole(image(record['layers'][side+'_foot']));assert m is not None;phase=(record['phase']+(.5 if side=='rear'else 0))%1;footmetrics[side]={**m,'world_center':m['center']-record['viewport_origin_x'],'stance':phase<.5}
        world.append({'mode':record['mode'],'tick':record['tick'],'phase':record['phase'],'root_x':record['root_x'],'feet':footmetrics,'composite':record['composite']})
    for mode in ['old_12_hold5','dense_60_hold1','continuous_rig']:
        records=[r for r in world if r['mode']==mode];sides=[];hold=5 if mode=='old_12_hold5'else 1
        for side in ['front','rear']:
            stance=[r for r in records if r['feet'][side]['stance']and r['tick']<60];groups=collections.defaultdict(list)
            for r in stance:groups[int(r['tick']//hold)].append(r['feet'][side]['world_center'])
            ranges=[max(v)-min(v)for v in groups.values()];centers=[r['feet'][side]['world_center']for r in stance];ground=sorted(set(r['feet'][side]['row']for r in stance));actual_range=max(centers)-min(centers)
            sides.append({'side':side,'ground_rows':ground,'ground_contact_satisfied':ground==[139],'actual_gpu_stance_world_range_px':actual_range,'actual_gpu_max_within_hold_world_range_px':max(ranges),'unchanged_slip_limit_px':.5,'actual_gpu_within_hold_rule_satisfied':max(ranges)<=.5,'measured_sample_count':len(stance),'interval_scope':'Five fractions per tick, all60ticks and exactwrap; maximum over captured raster surfaces, not an assertion of every possible real-valued timestamp.'})
        summary.append({'mode':mode,'held_ticks':None if mode=='continuous_rig'else hold,'analytic_continuous_root_within_hold_supremum_px':None if mode=='continuous_rig'else 48*hold/60,'actual_gpu':sides})
    report={'schema':'sprite-dense-pilot-comparison/v1','status':'changes_requested','art_quality_approved':False,'godot':raw['godot'],'renderer':raw['renderer'],'video_adapter':raw['video_adapter'],'inputs':{'original_project_sha256':sha(ROOT/'study/layered-cutout/project.json'),'dense_project_sha256':sha(HERE/'project.json'),'rig_sha256':sha(HERE/'cutout_rig.gd'),'gpu_observations_sha256':sha(HERE/'gpu-observations.json'),'capture_script_sha256':sha(HERE/'render_dense.gd'),'analysis_script_sha256':sha(__file__)},'construction':{'dense_frames':60,'unique_cels':len(cels),'project_bytes':len(payload.encode()),'actual_gpu_composite_equality':True,'source_colors_preserved':True,'baseline_phase_composite_mismatches':mismatches},'models':summary,'dense_analytic_issue_codes':sorted(set(i['code']for i in qc['issues'])),'world_samples':world,'scope':'Actual Godot OpenGL framebuffer readback on Mesa llvmpipe, including translated cachedold/dense raster frames vs continuously evaluated unchangedrig. No new anatomy/material fixes; no artistic approval; analytic full-hold bound and measured GPU raster quantization distinguished.'}
    (HERE/'comparison-report.json').write_text(json.dumps(report,indent=2)+'\n')
    selected=[0,.75,4,4.75,5,29.75,30,59.75,60];strip=Image.new('RGB',(256*3,(160+22)*len(selected)),(35,35,35));draw=ImageDraw.Draw(strip)
    for column,mode in enumerate(['old_12_hold5','dense_60_hold1','continuous_rig']):
        for row,tick in enumerate(selected):
            entry=next(r for r in world if r['mode']==mode and r['tick']==tick);im=image(entry['composite']);x=column*256;y=row*182;strip.paste(im,(x,y),im);draw.line((x,y+140,x+255,y+140),fill='green');draw.text((x+2,y+161),f"{mode} tick{tick} frontworld {entry['feet']['front']['world_center']}",fill='white')
    strip.save(HERE/'gpu-contact-comparison.png')
    detail=Image.new('RGB',(42*6*3,(22*6+20)*2),(35,35,35));draw=ImageDraw.Draw(detail)
    for row,tick in enumerate([.75,4.75]):
        for col,mode in enumerate(['old_12_hold5','dense_60_hold1','continuous_rig']):
            record=next(r for r in raw['world']if r['mode']==mode and r['tick']==tick);foot=image(record['layers']['front_foot']);crop=foot.crop((88,123,130,145));bg=Image.new('RGB',crop.size,(35,35,35));bg.paste(crop,(0,0),crop);ImageDraw.Draw(bg).line((0,17,41,17),fill='green');detail.paste(bg.resize((252,132),Image.Resampling.NEAREST),(col*252,row*152));measured=fast_sole(foot)['center']-24;draw.text((col*252+2,row*152+134),f'{mode} t{tick} world{measured}',fill='white')
    detail.save(HERE/'gpu-foot-contact-6x.png')
    for mode in ['old_12_hold5','dense_60_hold1','continuous_rig']:
        frames=[]
        for r in world:
            if r['mode']!=mode or r['tick']!=int(r['tick']):continue
            im=image(r['composite']);bg=Image.new('RGB',(256,182),(35,35,35));bg.paste(im,(0,0),im);draw=ImageDraw.Draw(bg);draw.line((0,140,255,140),fill='green');draw.text((2,162),f"{mode} tick{r['tick']} sole {r['feet']['front']['world_center']}",fill='white');frames.append(bg)
        frames[0].save(HERE/(mode+'.gif'),save_all=True,append_images=frames[1:],duration=100,loop=0)
    print(json.dumps({'project_bytes':len(payload.encode()),'unique_cels':len(cels),'phase_mismatches':mismatches,'model_summary':summary,'status':'changes_requested'}))
if __name__=='__main__':main()

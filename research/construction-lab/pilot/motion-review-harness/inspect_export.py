#!/usr/bin/env python3
"""Decode actual frozen VFR packets, compare declared scene, expose transitions.
No art verdict, no claim that anybody continuously watched the video.
"""
import argparse, hashlib, json, math, subprocess
from decimal import Decimal
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from export_motion import Motion, sha


def read_exact(stream, size):
    chunks=[];remaining=size
    while remaining:
        chunk=stream.read(remaining)
        if not chunk:break
        chunks.append(chunk);remaining-=len(chunk)
    return b''.join(chunks)


def probe(video):
    raw=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-show_frames','-show_entries','stream=width,height,time_base:frame=best_effort_timestamp_time','-of','json',str(video)])
    p=json.loads(raw);times=[]
    for f in p['frames']:
        time=Decimal(f['best_effort_timestamp_time'])*1000
        if time!=int(time):raise ValueError('Video timestamp is not an integer millisecond')
        times.append(int(time))
    if not times or times!=sorted(set(times)):raise ValueError('Unordered/duplicate decoded timestamps')
    return p['streams'][0],times,hashlib.sha256(raw).hexdigest()



def fixed_crop(stage, canvas, zoom, observations, requested=None):
    """One stage-coordinate rectangle; never use a pose's alpha/opaque bbox."""
    rectangles=[(r['draw_origin'][0],r['draw_origin'][1],r['draw_origin'][0]+canvas[0]*zoom,r['draw_origin'][1]+canvas[1]*zoom)for r in observations]
    if not rectangles:raise ValueError('No observed actor placements')
    union=[math.floor(min(r[0]for r in rectangles)),math.floor(min(r[1]for r in rectangles)),math.ceil(max(r[2]for r in rectangles)),math.ceil(max(r[3]for r in rectangles))]
    automatic=requested=='union'
    if automatic:crop=[max(0,min(stage[0],union[0])),max(0,min(stage[1],union[1])),max(0,min(stage[0],union[2])),max(0,min(stage[1],union[3]))]
    else:
        crop=list(requested)
        if len(crop)!=4 or any(isinstance(x,bool)or not isinstance(x,int)for x in crop):raise ValueError('Explicit crop requires4 integer bounds')
        if crop[0]<0 or crop[1]<0 or crop[2]>stage[0]or crop[3]>stage[1]:raise ValueError('Explicit crop outside stage')
    if crop[0]>=crop[2]or crop[1]>=crop[3]:raise ValueError('Empty fixed crop')
    uncovered=0
    for r in rectangles:
        visible=(max(0,r[0]),max(0,r[1]),min(stage[0],r[2]),min(stage[1],r[3]))
        if visible[0]<visible[2]and visible[1]<visible[3]and not(crop[0]<=visible[0]and crop[1]<=visible[1]and crop[2]>=visible[2]and crop[3]>=visible[3]):uncovered+=1
    if automatic and uncovered:raise AssertionError('Union crop excludes visible actor canvas')
    return {'stage_rectangle_xyxy':crop,'method':'all-observed-full-canvas-union-clamped-stage'if automatic else 'explicit-fixed-stage-rectangle','unclamped_full_canvas_union_xyxy':union,'observed_full_canvas_samples':len(rectangles),'visible_canvas_placements_not_fully_covered':uncovered,'same_rectangle_all_transitions':True,'uses_alpha_bbox':False}


def decode_variant(motion, folder, variant, out, tile_width, tolerance, detail_crop=None, detail_scale=1):
    video=folder/variant['file']
    if sha(video)!=variant['sha256']:raise ValueError('Frozen video hash mismatch: '+variant['file'])
    stream,times,probe_hash=probe(video)
    observations=variant['observations']
    if times!=[x['output_ms']for x in observations]:raise ValueError('Encoded/report timestamp mismatch')
    if [stream['width'],stream['height']]!=motion.stage:raise ValueError('Actual video canvas differs')
    if times[-1]!=variant['exact_duration_ms']:raise ValueError('Missing exact loop endpoint')
    name=video.stem;output=out/name;output.mkdir()
    crop_geometry=fixed_crop(motion.stage,motion.canvas,variant['zoom'],observations,detail_crop)if detail_crop is not None else None
    detail_paths=[];detail_page=[]
    crop_width=(crop_geometry['stage_rectangle_xyxy'][2]-crop_geometry['stage_rectangle_xyxy'][0])*detail_scale if crop_geometry else 0
    crop_height=(crop_geometry['stage_rectangle_xyxy'][3]-crop_geometry['stage_rectangle_xyxy'][1])*detail_scale if crop_geometry else 0
    command=['ffmpeg','-v','error','-threads','2','-i',str(video),'-map','0:v:0','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-']
    child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    packet_size=stream['width']*stream['height']*3
    max_error=0;bad_frames=0;excess_channels=0;state_mismatches=0;previous=None;transition_count=0;wrap_count=0;selected=[];sheet_paths=[];page=[]
    height=round(motion.stage[1]*tile_width/motion.stage[0]);cell_height=height+30
    def flush():
        if not page:return
        sheet=Image.new('RGB',(tile_width*4,cell_height*math.ceil(len(page)/4)),(28,34,40));draw=ImageDraw.Draw(sheet)
        for n,(thumb,label) in enumerate(page):
            x=(n%4)*tile_width;y=(n//4)*cell_height;sheet.paste(thumb,(x,y));draw.text((x+4,y+height+3),label,fill='white')
        path=output/f'transitions-{len(sheet_paths):03d}.png';sheet.save(path);sheet_paths.append({'file':str(path.relative_to(out)),'sha256':sha(path),'tiles':len(page)});page.clear()
    def flush_detail():
        if not detail_page:return
        # Keep native detail readable; integer enlargement only, no shrink-to-fit.
        columns=3 if crop_width<=768 else 2
        sheet=Image.new('RGB',(crop_width*columns,(crop_height+30)*math.ceil(len(detail_page)/columns)),(28,34,40));draw=ImageDraw.Draw(sheet)
        for n,(image,label)in enumerate(detail_page):
            x=(n%columns)*crop_width;y=(n//columns)*(crop_height+30);sheet.paste(image,(x,y));draw.text((x+4,y+crop_height+3),label,fill='white')
        path=output/f'fixed-crop-{len(detail_paths):03d}.png';sheet.save(path);detail_paths.append({'file':str(path.relative_to(out)),'sha256':sha(path),'tiles':len(detail_page)});detail_page.clear()
    trace_path=output/'decoded-observations.jsonl'
    try:
        with trace_path.open('w') as trace:
            for n,(time,declared) in enumerate(zip(times,observations)):
                raw=read_exact(child.stdout,packet_size)
                if len(raw)!=packet_size:raise ValueError('Truncated passthrough decode')
                source_time=time/variant['slowdown']
                expected,state=motion.render(source_time,variant['zoom'],variant['silhouette'])
                actual=np.frombuffer(raw,dtype=np.uint8).reshape(motion.stage[1],motion.stage[0],3)
                delta=np.abs(actual.astype(np.int16)-np.asarray(expected,dtype=np.int16))
                error=int(delta.max());max_error=max(max_error,error);bad=error>tolerance
                bad_frames+=int(bad);excess_channels+=int(np.count_nonzero(delta>tolerance))
                def vector_equal(key):return all(abs(a-b)<1e-8 for a,b in zip(state[key],declared[key]))
                agrees=state['frame']==declared['frame'] and state['cycle']==declared['cycle'] and state['draw_origin']==declared['draw_origin'] and all(vector_equal(k)for k in ['physical_root','draw_root','camera'])
                state_mismatches+=int(not agrees)
                change=previous is None or (previous['frame'],previous['cycle'])!=(state['frame'],state['cycle'])
                wrap=previous is not None and state['cycle']!=previous['cycle']
                if change:
                    transition_count+=1;wrap_count+=int(wrap)
                    image=Image.frombytes('RGB',tuple(motion.stage),raw)
                    thumb=image.resize((tile_width,height),Image.Resampling.NEAREST)
                    label=f"{time}ms c{int(state['cycle'])} f{state['frame']:02d}"+(' WRAP'if wrap else '')
                    page.append((thumb,label))
                    if crop_geometry:
                        detail=image.crop(tuple(crop_geometry['stage_rectangle_xyxy']))
                        if detail_scale!=1:detail=detail.resize((crop_width,crop_height),Image.Resampling.NEAREST)
                        detail_page.append((detail,label))
                        if len(detail_page)==12:flush_detail()
                    selected.append({'decoded_index':n,'output_ms':time,'source_frame':state['frame'],'cycle':state['cycle'],'wrap':wrap})
                    if len(page)==24:flush()
                trace.write(json.dumps({'decoded_index':n,'output_ms':time,'source_frame':state['frame'],'cycle':state['cycle'],'draw_origin':state['draw_origin'],'max_RGB_error':error,'render_state_agrees':agrees,'decoded_RGB_sha256':hashlib.sha256(raw).hexdigest()})+'\n')
                previous=state
        extra=child.stdout.read(1);stderr=child.stderr.read().decode();status=child.wait()
        if extra or status:raise ValueError(f'Decode extra/failed packets: {status} {stderr}')
        flush();flush_detail()
    finally:
        if child.poll() is None:child.kill();child.wait()
        child.stdout.close();child.stderr.close()
    if sha(video)!=variant['sha256']:raise ValueError('Video changed during decode')
    return {'video':variant['file'],'video_sha256':variant['sha256'],'ffprobe_timestamp_dump_sha256':probe_hash,'actual_decoded_frame_count':len(times),'all_actual_timestamps_match_report':True,'exact_source_duration_ms':variant['exact_duration_ms'],'endpoint_packet_ms':variant['last_endpoint_packet_ms'],'decoded_RGB_max_error':max_error,'RGB_tolerance':tolerance,'failed_decoded_frames':bad_frames,'channels_exceeding_tolerance':excess_channels,'declared_scene_state_mismatches':state_mismatches,'passed':bad_frames==0 and state_mismatches==0,'actual_source_transitions_including_initial':transition_count,'actual_wrap_count':wrap_count,'sheets':sheet_paths,'fixed_crop_geometry':crop_geometry,'fixed_crop_integer_scale':detail_scale if crop_geometry else None,'fixed_crop_sheets':detail_paths,'selected_transition_tiles':selected,'decoded_observations_path':str(trace_path.relative_to(out)),'decoded_observations_sha256':sha(trace_path),'clipped_source_samples':variant['clipped_sample_count']}


def inspect(spec, folder, out, variants=None, tile_width=256, tolerance=2, detail_crop=None, detail_scale=1):
    spec=Path(spec).resolve();folder=Path(folder).resolve();out=Path(out).resolve()
    if out.exists():raise FileExistsError('Preserve prior inspection')
    if not 128<=tile_width<=512 or tolerance!=2:raise ValueError('Bounded tile128..512; fixed codec tolerance2')
    if detail_scale not in[1,2]:raise ValueError('Detail scale1/native or2/integer nearest')
    source_hash=sha(spec);report_path=folder/'report.json';report_hash=sha(report_path);report=json.loads(report_path.read_text());motion=Motion(spec)
    if source_hash!=report['spec_sha256']:raise ValueError('Spec/report SHA mismatch')
    if sha(Path(__file__).with_name('export_motion.py'))!=report['code_sha256']:raise ValueError('Scene renderer/code SHA mismatch: use exact frozen exporter')
    if report['source_sha256']!=[f['sha256']for f in motion.frames]:raise ValueError('Source frame SHA ledger mismatch')
    for i,f in enumerate(motion.frames):
        if sha(folder/'source-frames'/f'{i:02d}.png')!=f['sha256']:raise ValueError('Copied source PNG hash mismatch')
    chosen=[v for v in report['variants']if variants is None or v['file']in variants]
    if not chosen or (variants and len(chosen)!=len(variants)):raise ValueError('Unknown/duplicate variant selection')
    if len(chosen)>8 or sum(len(v['observations'])for v in chosen)>6000 or motion.stage[0]*motion.stage[1]>1024*1024:
        raise ValueError('Inspection budget: max8variants/6000packets/1024²stagepixels')
    out.mkdir(parents=True);rows=[]
    for v in chosen:rows.append(decode_variant(motion,folder,v,out,tile_width,tolerance,detail_crop,detail_scale))
    if sha(spec)!=source_hash or sha(report_path)!=report_hash:raise ValueError('Frozen inputs changed during inspection')
    for f in motion.frames:
        if sha(spec.parent/f['file'])!=f['sha256']:raise ValueError('Source image changed during inspection')
    summary={'schema':'decoded-motion-export-inspection/v1','spec_sha256':source_hash,'report_sha256':report_hash,'input_export':str(folder),'inspector_sha256':sha(__file__),'scene_renderer_sha256':report['code_sha256'],'passed':all(x['passed']for x in rows),'variants':rows,'art_verdict':'NOT_REVIEWED','continuous_video_watching_claim':False,'limits':['Every actual decoded packet compared; chronological sheets select every source transition and wrap, not everypresentation packet','Fullstage sheets remain unchanged; optional detail sheets use ONEcommon stage-coordinate crop, never per-pose fitting; explicitcrop omissions are recorded','RGB codec conversion tolerance2LSB; no RGBA alpha stored in MP4','Declared root/camera/support metadata validated against scene rendering, not anatomical/physics truth','Successful decode/export comparison provides no aesthetic approval or score']}
    (out/'receipt.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


def main():
    p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--export',dest='folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--variants',help='Comma-separated exact filenames; default all');p.add_argument('--tile-width',type=int,default=256);p.add_argument('--detail-crop',help='union or fixed stage bounds x0,y0,x1,y1; optional alongside fullstage');p.add_argument('--detail-scale',type=int,choices=[1,2],default=1);a=p.parse_args()
    crop='union'if a.detail_crop=='union'else tuple(map(int,a.detail_crop.split(',')))if a.detail_crop else None
    r=inspect(a.spec,a.folder,a.output,set(a.variants.split(','))if a.variants else None,a.tile_width,detail_crop=crop,detail_scale=a.detail_scale)
    print(json.dumps({'output':str(a.output),'passed':r['passed'],'variants':len(r['variants']),'decoded_packets':sum(x['actual_decoded_frame_count']for x in r['variants']),'failed_frames':sum(x['failed_decoded_frames']for x in r['variants'])}))
    raise SystemExit(0 if r['passed']else 1)
if __name__=='__main__':main()

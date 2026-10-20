#!/usr/bin/env python3
"""Independent pixel/motion checks. No sprite_lab renderer or validation import."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def layer_image(p,frame,layer):
    w=p['canvas']['width'];h=p['canvas']['height'];cid=frame['cels'].get(layer);pixels=p['cels'][cid]['pixels']if cid else[0]*(w*h)
    im=Image.new('RGBA',(w,h));im.putdata([tuple(p['palette'][i])for i in pixels]);return im

def composite(p,frame):
    w=p['canvas']['width'];h=p['canvas']['height'];out=[(0,0,0,0)]*(w*h);owners=[None]*(w*h)
    for layer in p['layers']:
        cid=frame['cels'].get(layer['id'])
        if cid is None:continue
        for i,index in enumerate(p['cels'][cid]['pixels']):
            s=p['palette'][index];a=s[3]
            if a==0:continue
            if a==255:out[i]=tuple(s);owners[i]=layer['id'];continue
            d=out[i];n=a*255+d[3]*(255-a);out[i]=tuple((s[k]*a*255+d[k]*d[3]*(255-a)+n//2)//n for k in range(3))+((n+127)//255,);owners[i]=layer['id']
    im=Image.new('RGBA',(w,h));im.putdata(out);return im,owners

def data(im):return im.get_flattened_data()if hasattr(im,'get_flattened_data')else im.getdata()
def points(im,threshold=128):return [(i%im.width,i//im.width)for i,c in enumerate(data(im))if c[3]>=threshold]
def sole(im,threshold=128,roi=None):
    pts=points(im,threshold)
    if roi is not None:pts=[(x,y)for x,y in pts if roi[0]<=x<roi[2]and roi[1]<=y<roi[3]]
    if not pts:return None
    y=max(p[1]for p in pts);xs=[x for x,py in pts if py==y];return {'row':y,'x_min':min(xs),'x_max':max(xs),'center_x':(min(xs)+max(xs))/2,'pixels':[[x,y]for x in xs]}
def changed(a,b):return [(i%a.width,i//a.width)for i,(x,y)in enumerate(zip(data(a),data(b)))if x!=y]
def roi_distance(a,b,roi,threshold):
    def inside(im):return [(x,y)for x,y in points(im,threshold)if roi[0]<=x<roi[2]and roi[1]<=y<roi[3]]
    x=inside(a);y=inside(b)
    return {'a_pixels':len(x),'b_pixels':len(y),'minimum_pixel_center_distance':min((math.hypot(px-qx,py-qy)for px,py in x for qx,qy in y),default=None),'overlap_pixels':len(set(x)&set(y))}

def validate_inputs(p,ann):
    if ann.get('schema')!='sprite-pixel-motion-annotations/v1':raise ValueError('Unsupported annotation schema')
    w=p['canvas']['width'];h=p['canvas']['height']
    if type(w)is not int or type(h)is not int or w<=0 or h<=0 or w*h>16777216:raise ValueError('Invalid canvas')
    if type(ann['alpha_threshold'])is not int or not 1<=ann['alpha_threshold']<=255:raise ValueError('Invalid alpha threshold')
    for color in p['palette']:
        if len(color)!=4 or any(type(c)is not int or not 0<=c<=255 for c in color):raise ValueError('Invalid RGBA palette')
    for cel in p['cels'].values():
        if len(cel['pixels'])!=w*h or any(type(i)is not int or not 0<=i<len(p['palette'])for i in cel['pixels']):raise ValueError('Invalid indexed cel')
    ids={f['id']for f in p['frames']}
    for frame in p['frames']:
        if type(frame['duration_ticks'])is not int or frame['duration_ticks']<=0:raise ValueError('Invalid hold')
    for anim in p['animations']:
        if type(anim['fps'])not in(int,float)or not math.isfinite(anim['fps'])or anim['fps']<=0 or not anim['frames']or any(f not in ids for f in anim['frames']):raise ValueError('Invalid action clock or sequence')
    for action in ann['actions']:
        if action['world_motion']not in ['continuous','stepped']or type(action['root_speed_px_s'])not in(int,float)or not math.isfinite(action['root_speed_px_s']):raise ValueError('Invalid world-motion rule')
        for contact in action.get('contacts',[]):
            if any(fid not in ids for fid in contact['stance_frames']):raise ValueError('Unknown stance frame')
            for key in ['max_ground_error_px','max_boundary_slip_px','max_hold_slip_px']:
                if type(contact[key])not in(int,float)or not math.isfinite(contact[key])or contact[key]<0:raise ValueError('Invalid contact tolerance')

def check(p,ann,root,reference=True):
    validate_inputs(p,ann);root=Path(root);issues=[];rows=[];renders={};byid={f['id']:f for f in p['frames']};threshold=ann['alpha_threshold'];w=p['canvas']['width'];h=p['canvas']['height']
    def issue(code,**values):issues.append({'code':code,**values})
    for path,digest in ann.get('source_hashes',{}).items():
        if reference and(not(root/path).is_file()or sha(root/path)!=digest):issue('REFERENCE_SOURCE_STALE',path=path)
    palette_digest=hashlib.sha256(json.dumps(p['palette'],separators=(',',':')).encode()).hexdigest()
    if palette_digest!=ann.get('palette_sha256',palette_digest):issue('PALETTE_REFERENCE_CHANGED',actual_sha256=palette_digest)
    if p['canvas']!=ann['canvas']:issue('ANCHOR_OR_CANVAS_CHANGED',actual=p['canvas'],expected=ann['canvas'])
    if [l['id']for l in p['layers']]!=ann['layer_order']:issue('LAYER_ORDER_CHANGED')
    for fid,expect in ann['frames'].items():
        if fid not in byid:issue('FRAME_MISSING',frame=fid);continue
        frame=byid[fid];im,owners=composite(p,frame);renders[fid]=im;pts=points(im,threshold);edge=[list(q)for q in pts if min(q[0],q[1],w-1-q[0],h-1-q[1])<ann['edge_margin']]
        if edge:issue('ALPHA_CANVAS_EDGE',frame=fid,pixels=edge)
        if frame['landmarks']!=expect['landmarks']:issue('FRAME_ANCHOR_CHANGED',frame=fid)
        if frame['duration_ticks']!=expect['duration_ticks']:issue('FRAME_TIMING_CHANGED',frame=fid)
        layer_metrics={}
        for lid in ann['layer_order']:
            li=layer_image(p,frame,lid);lp=points(li,threshold);layer_metrics[lid]={'bbox':li.getchannel('A').getbbox(),'opaque_pixels':len(lp)}
            if reference:
                ref=Image.open(root/expect['layers'][lid]['path']).convert('RGBA');changes=changed(li,ref);refpts=set(points(ref,threshold));actualpts=set(lp);layer_metrics[lid].update({'reference_opaque_pixels':len(refpts),'lost_alpha_pixels':len(refpts-actualpts),'gained_alpha_pixels':len(actualpts-refpts),'reference_bbox':ref.getchannel('A').getbbox()})
                if changes:issue('REFERENCE_LAYER_PIXELS',frame=fid,layer=lid,changed_pixels=len(changes),first_coordinates=[list(x)for x in changes[:12]])
        if reference:
            ref=Image.open(root/expect['composite']['path']).convert('RGBA');changes=changed(im,ref)
            if changes:issue('REFERENCE_POSE_COMPOSITE',frame=fid,changed_pixels=len(changes),first_coordinates=[list(x)for x in changes[:12]])
        joints=[]
        for joint in expect.get('joints',[]):
            metric=roi_distance(layer_image(p,frame,joint['a']),layer_image(p,frame,joint['b']),joint['roi'],threshold);seams=[]
            for y in range(max(0,joint['roi'][1]),min(h,joint['roi'][3])):
                for x in range(max(0,joint['roi'][0]),min(w,joint['roi'][2])):
                    if owners[y*w+x]!=joint['a']:continue
                    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        xx=x+dx;yy=y+dy
                        if 0<=xx<w and 0<=yy<h and owners[yy*w+xx]==joint['b']:
                            ca=im.getpixel((x,y));cb=im.getpixel((xx,yy));seams.append({'a_xy':[x,y],'b_xy':[xx,yy],'a_rgba':list(ca),'b_rgba':list(cb),'rgb_distance':math.sqrt(sum((ca[k]-cb[k])**2 for k in range(3)))})
            metric['visible_part_boundary_pairs']=len(seams);metric['largest_visible_color_transitions']=sorted(seams,key=lambda s:s['rgb_distance'],reverse=True)[:3];metric['material_interpretation']='Unclassified RGB discontinuity evidence only; no anatomy, cloth identity or quality approval inferred.';joints.append({**joint,**metric})
            if 'max_gap_px'in joint and(metric['minimum_pixel_center_distance']is None or metric['minimum_pixel_center_distance']>joint['max_gap_px']):issue('ANNOTATED_ATTACHMENT_GAP',frame=fid,joint=joint['name'],measurement=metric)
        rows.append({'frame':fid,'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'alpha_bbox':im.getchannel('A').getbbox(),'edge_pixels':len(edge),'layers':layer_metrics,'joints':joints})
    actions=[]
    for rule in ann['actions']:
        anim=next((a for a in p['animations']if a['id']==rule['id']),None)
        if anim is None:issue('ACTION_MISSING',action=rule['id']);continue
        if 'sequence'in rule and anim['frames']!=rule['sequence']:issue('ACTION_SEQUENCE_CHANGED',action=rule['id'])
        if 'fps'in rule and anim['fps']!=rule['fps']:issue('ACTION_FPS_CHANGED',action=rule['id'],actual=anim['fps'],expected=rule['fps'])
        if 'loop'in rule and anim['loop']!=rule['loop']:issue('ACTION_LOOP_POLICY_CHANGED',action=rule['id'])
        sequence=anim['frames'];starts=[];tick=0
        for fid in sequence:starts.append(tick);tick+=byid[fid]['duration_ticks']
        total=tick;fps=anim['fps'];speed=rule['root_speed_px_s'];cycle_dx=speed*total/fps;contacts=[];transitions=[];samples=[]
        for contact in rule.get('contacts',[]):
            foot=contact['layer'];metrics=[];stance=set(contact['stance_frames'])
            for i,fid in enumerate(sequence):
                m=sole(layer_image(p,byid[fid],foot),threshold,contact.get('sole_rois',{}).get(fid,contact.get('sole_roi')))
                if m is None:issue('FOOT_ALPHA_MISSING',frame=fid,layer=foot);continue
                world=m['center_x']+speed*starts[i]/fps;isstance=fid in stance
                if isstance and abs(m['row']-contact['ground_row'])>contact['max_ground_error_px']:issue('STANCE_GROUND_CONTACT',frame=fid,layer=foot,sole_row=m['row'],expected_row=contact['ground_row'])
                if isstance:
                    hold_dx=abs(speed*byid[fid]['duration_ticks']/fps)
                    if rule['world_motion']=='continuous'and hold_dx>contact['max_hold_slip_px']:issue('HELD_FRAME_WORLD_SLIDING',frame=fid,layer=foot,supremum_slip_px=hold_dx,interval='[start_tick,end_tick); end displacement is supremum, not an included sample')
                _,owner=composite(p,byid[fid]);visible=[xy for xy in m['pixels']if owner[xy[1]*w+xy[0]]==foot]
                metrics.append({'frame':fid,'start_tick':starts[i],'duration_ticks':byid[fid]['duration_ticks'],'stance':isstance,'visible_sole_pixels':len(visible),'world_center_at_frame_start':world,**m})
            for i,m in enumerate(metrics):
                j=(i+1)%len(metrics)
                if j==0 and not anim['loop']:continue
                nxt=metrics[j];dx=nxt['world_center_at_frame_start']+(cycle_dx if j==0 else 0)-m['world_center_at_frame_start'];both=m['stance']and nxt['stance'];entry={'layer':foot,'from':m['frame'],'to':nxt['frame'],'loop_wrap':j==0,'same_stance_segment':both,'world_center_delta_px':dx,'sole_row_delta_px':nxt['row']-m['row']};transitions.append(entry)
                if both and abs(dx)>contact['max_boundary_slip_px']:issue('STANCE_BOUNDARY_WORLD_SLIDING',**entry)
            # Fractional ticks, every discrete boundary and both sides of wrap. No interpolation invented.
            for t in sorted(set([0,total/2,total-1e-6,total,total+1e-6]+[s+f for i,s in enumerate(starts)for f in [0,0.5,1e-6,byid[sequence[i]]['duration_ticks']-1e-6]])):
                if t>=total and not anim['loop']:continue
                cycle=math.floor(t/total);local=t%total;i=max(k for k,s in enumerate(starts)if s<=local);fid=sequence[i];m=sole(layer_image(p,byid[fid],foot),threshold,contact.get('sole_rois',{}).get(fid,contact.get('sole_roi')))
                if m is None:
                    samples.append({'tick':t,'frame':fid,'layer':foot,'measurement':'foot alpha missing; world contact unknown'});continue
                rootx=speed*t/fps if rule['world_motion']=='continuous'else speed*starts[i]/fps+cycle*cycle_dx
                samples.append({'tick':t,'seconds':t/fps,'frame':fid,'layer':foot,'stance':fid in stance,'root_world_x':rootx,'sole_world_x':m['center_x']+rootx,'sole_row':m['row']})
            contacts.append({'layer':foot,'ground_row':contact['ground_row'],'frames':metrics})
        continuity=[]
        for i,fid in enumerate(sequence):
            j=(i+1)%len(sequence)
            if j==0 and not anim['loop']:continue
            other=sequence[j];a=renders[fid];b=renders[other];a_pts=set(points(a,threshold));b_pts=set(points(b,threshold));union=a_pts|b_pts
            continuity.append({'from':fid,'to':other,'loop_wrap':j==0,'changed_rgba_pixels':len(changed(a,b)),'silhouette_iou':len(a_pts&b_pts)/len(union)if union else 1,'interpretation':'measurement only; no anatomical or choreography threshold asserted'})
        actions.append({'action':rule['id'],'fps':fps,'total_ticks':total,'duration_seconds':total/fps,'loop':anim['loop'],'world_motion_assumption':rule['world_motion'],'root_speed_px_s':speed,'cycle_world_displacement_px':cycle_dx,'contacts':contacts,'transitions':transitions,'fractional_tick_samples':samples,'pose_continuity':continuity})
    report={'schema':'sprite-pixel-motion-qc/v1','decision':'violations_found'if issues else'annotated_rules_satisfied','art_quality_approved':False,'canvas':p['canvas'],'issues':issues,'frames':rows,'actions':actions,'palette':{'sha256':palette_digest,'colors':len(p['palette']),'alpha_values':sorted(set(c[3]for c in p['palette']))},'unresolved':ann.get('unresolved',[]),'scope':'Independent scalar indexed compositor; declared contacts/world clock/anchors/source integrity. Joint ROIs measure connectivity only. Artistic anatomy, readability and choreography remain human review.'}
    return report,renders

def material_check(source,candidate,annotation):
    a=Image.open(source).convert('RGBA');b=Image.open(candidate).convert('RGBA');results=[]
    for sample in annotation['samples']:
        xy=tuple(sample['xy']);before=a.getpixel(xy);after=b.getpixel(xy);relation=sample['criterion'];passed=after[2]>after[0]if relation=='blue_exceeds_red'else list(after)==sample['expected_rgba'];results.append({**sample,'source_rgba':list(before),'candidate_rgba':list(after),'satisfied':passed})
    return {'schema':'sprite-annotated-material-qc/v1','source_sha256':sha(source),'candidate_sha256':sha(candidate),'art_quality_approved':False,'samples':results,'violations':[{'code':'ANNOTATED_MATERIAL_LEAK',**s}for s in results if not s['satisfied']],'scope':'Only three independently reviewer-annotated blue-trouser locations; no universal rejection of pink or inferred segmentation.'}

def diagnostic(renders,report,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);ids=list(renders);w,h=next(iter(renders.values())).size;cols=4;sheet=Image.new('RGB',(cols*w,math.ceil(len(ids)/cols)*(h+18)),(35,35,35));d=ImageDraw.Draw(sheet)
    ground=report['canvas']['ground_pivot'][1]-1;problems={x.get('frame')for x in report['issues']}
    for i,fid in enumerate(ids):
        x=i%cols*w;y=i//cols*(h+18);sheet.paste(renders[fid],(x,y),renders[fid]);d.text((x+3,y+h+2),fid,fill='orange'if fid in problems else'white');d.line((x,y+ground,x+w,y+ground),fill=(70,180,70))
    sheet.save(out/'all-poses-contact.png');frames=[]
    for action in report['actions']:
        if not action['contacts']:continue
        contact=action['contacts'][0]
        for row in contact['frames']:
            fid=row['frame'];im=Image.new('RGB',(w*2,h+32),(35,35,35));im.paste(renders[fid],(0,0),renders[fid]);dr=ImageDraw.Draw(im);dr.line((0,ground,w*2,ground),fill='green');dr.text((4,h+2),f"{fid} sole {row['row']} world {row['world_center_at_frame_start']:.2f}",fill='white');frames.append(im)
    if frames:frames[0].save(out/'walk-contact.gif',save_all=True,append_images=frames[1:],duration=250,loop=0)
    for action in report['actions']:
        if not action['contacts']or action['action']!='walk':continue
        rows=action['contacts'][0]['frames'];timeline=[];total=action['total_ticks'];speed=action['root_speed_px_s'];fps=action['fps'];width=w+math.ceil(abs(action['cycle_world_displacement_px']))+48
        for tick in range(total+1):
            local=tick%total;row=next((r for r in reversed(rows)if r['start_tick']<=local),None)
            if row is None:continue
            rootx=speed*tick/fps if action['world_motion_assumption']=='continuous'else speed*row['start_tick']/fps+math.floor(tick/total)*action['cycle_world_displacement_px']
            im=Image.new('RGB',(width,h+30),(35,35,35));dr=ImageDraw.Draw(im)
            for x in range(0,width,8):dr.line((x,0,x,h),fill=(45,45,45))
            x=24+round(rootx);im.paste(renders[row['frame']],(x,0),renders[row['frame']]);dr.line((0,action['contacts'][0]['ground_row'],width,action['contacts'][0]['ground_row']),fill='green');sx=x+row['center_x'];dr.ellipse((sx-2,row['row']-2,sx+2,row['row']+2),outline='yellow');dr.text((3,h+2),f"tick {tick} {row['frame']} root {rootx:.2f} soleworld {row['center_x']+rootx:.2f}",fill='white');timeline.append(im)
        if timeline:
            timeline[0].save(out/'continuous-world-contact.gif',save_all=True,append_images=timeline[1:],duration=100,loop=0)
            chosen=sorted(set(t for t in [0,4,5,total//2-1,total//2,total-1,total]if 0<=t<len(timeline)));strip=Image.new('RGB',(width*2,(h+30)*math.ceil(len(chosen)/2)),(35,35,35))
            for i,t in enumerate(chosen):strip.paste(timeline[t],((i%2)*width,(i//2)*(h+30)))
            strip.save(out/'world-tick-strip.png')
    report['visual_diagnostics']={'walk_contact_ms_per_pose':250,'world_contact_ms_per_source_tick':100,'timing_scope':'GIFs deliberately slowed for inspection; analytic ticks/seconds/FPS in report remain authoritative. At60fps, world GIF is6xslow.'}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('annotations');ap.add_argument('--root',default='.');ap.add_argument('--output',required=True);args=ap.parse_args();p=json.loads(Path(args.project).read_text());ann=json.loads(Path(args.annotations).read_text());report,renders=check(p,ann,args.root);report['inputs']={'project_file_sha256':sha(args.project),'annotations_sha256':sha(args.annotations),'checker_sha256':sha(__file__),'references':ann['source_hashes']};diagnostic(renders,report,args.output);print(json.dumps({'decision':report['decision'],'issue_codes':sorted(set(i['code']for i in report['issues'])),'report':str(Path(args.output)/'report.json')}));return 1 if report['issues']else 0
if __name__=='__main__':raise SystemExit(main())

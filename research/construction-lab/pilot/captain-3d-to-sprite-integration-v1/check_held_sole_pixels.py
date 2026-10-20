"""Actual-video nearby-sole opaque patch checks within60Hz held cels.

Material identity is qualified: evaluated toe vertex guides a nearby visible
beauty patch; this does NOT claim a vertex-ID render or plant across poses.
"""
import argparse, importlib.util, json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

spec=importlib.util.spec_from_file_location('world_replay',Path(__file__).with_name('world_replay.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def pick(image,projection):
    rgba=np.array(image);x,y=[m.rounded(v)for v in projection];choices=[]
    for dy in range(-4,5):
        for dx in range(-4,5):
            xx,yy=x+dx,y+dy
            if not (1<=xx<rgba.shape[1]-1 and 1<=yy<rgba.shape[0]-1):continue
            patch=rgba[yy-1:yy+2,xx-1:xx+2]
            if np.all(patch[:,:,3]==255):
                variance=float(patch[:,:,:3].var())
                if variance>=8:choices.append((dx*dx+dy*dy,-variance,xx,yy,patch[:,:,:3]))
    if not choices:return None
    return min(choices,key=lambda p:p[:2])


def locate(actual,patch,expected):
    x,y=expected;matches=[]
    for dy in range(-12,13):
        for dx in range(-12,13):
            xx,yy=x+dx,y+dy
            got=actual[yy-1:yy+2,xx-1:xx+2]
            if got.shape!=patch.shape:continue
            err=np.abs(got.astype(np.int16)-patch.astype(np.int16))
            if int(err.max())<=2:matches.append((int(xx),int(yy)))
    return matches


def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--corrected-joints',type=Path,required=True);p.add_argument('--export',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--mode',choices=['continuous','coherent'],default='continuous');a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve prior evidence')
    a.output.mkdir(parents=True);replay=m.Replay(a.contract,a.corrected_joints)
    joints=json.loads(a.corrected_joints.read_text());receipt=json.loads((a.export/'receipt.json').read_text())
    if receipt['contract_sha256']!=m.sha(a.contract):raise ValueError('Wrong video/source contract')
    variant=next(v for v in receipt['variants']if v['file']==a.mode+'-1x-colour.mp4');video=a.export/variant['file']
    if m.sha(video)!=variant['sha256']:raise ValueError('Actual video hash mismatch')
    process=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-i',str(video),'-frames:v','130','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
    stage=tuple(receipt.get('stage_canvas',[1024,1024]))
    origin=np.array(receipt.get('fixed_origin_px',[416.,80.]),dtype=float)
    rows=[];examples=[];negative=None;length=stage[0]*stage[1]*3
    for cel in range(65):
        frames=[]
        for _ in range(2):
            raw=bytearray()
            while len(raw)<length:
                chunk=process.stdout.read(length-len(raw))
                if not chunk:raise ValueError('Truncated actual video')
                raw.extend(chunk)
            frames.append(np.frombuffer(raw,dtype=np.uint8).reshape(stage[1],stage[0],3).copy())
        for side,foot in joints[cel*2]['feet'].items():
            if foot['mode']!='flat':continue
            xyz=np.array(foot['actual_evaluated_toe_material_world_m'])-replay.roots[cel]
            projection=replay.ground(xyz);choice=pick(replay.images[cel],projection)
            row={'cel':cel,'side':side,'mode':'flat','evaluated_toe_source_projection_px':projection.tolist(),'status':'NO_DISTINCT_OPAQUE_PATCH'}
            if choice is None:rows.append(row);continue
            _,variance,x,y,patch=choice;locations=[]
            for phase in range(2):
                state=replay.state(cel*2+phase,a.mode);draw=origin+state[2];expected=np.array([m.rounded(v)for v in draw])+[x,y]
                locations.append(locate(frames[phase],patch,expected))
            row.update(source_patch_centre_px=[x,y],source_patch_size=[3,3],source_patch_variance=-variance,actual_matches=locations)
            if any(len(v)!=1 for v in locations):row['status']='AMBIGUOUS_OR_MISSING_ACTUAL_MATCH';rows.append(row);continue
            delta=np.array(locations[1][0])-locations[0][0];row.update(actual_within_hold_delta_px=delta.tolist(),status='WITHIN_ONE_PIXEL_PER_AXIS' if max(abs(delta))<=1 else 'EXCESSIVE_HELD_SLIDE')
            if len(examples)<12:
                # Same fixed world crop for both within-hold packets, centred ONCE.
                cx,cy=locations[0][0];bounds=(cx-18,cy-22,cx+18,cy+14);panel=Image.new('RGB',(576,328),(28,35,40));draw=ImageDraw.Draw(panel)
                for phase,frame in enumerate(frames):
                    im=Image.fromarray(frame).crop(bounds).resize((288,288),Image.Resampling.NEAREST);panel.paste(im,(phase*288,0));xx,yy=locations[phase][0];draw.rectangle((phase*288+(xx-bounds[0])*8-5,(yy-bounds[1])*8-5,phase*288+(xx-bounds[0])*8+5,(yy-bounds[1])*8+5),outline='cyan',width=1)
                draw.text((8,296),f'cel{cel:02d} {side} +0ms / +8.333ms | actual delta{delta.tolist()}px',fill='white');name=f'witness-{cel:02d}-{side}.png';panel.save(a.output/name);examples.append(name)
            if negative is None:
                shifted=np.roll(frames[1],8,axis=1);state=replay.state(cel*2+1,a.mode);expected=np.array([m.rounded(v)for v in origin+state[2]])+[x,y];bad=locate(shifted,patch,expected)
                if len(bad)==1:
                    bad_delta=np.array(bad[0])-locations[0][0];negative={'cel':cel,'side':side,'actual_second_packet_horizontal_shift_px':8,'observed_delta_px':bad_delta.tolist(),'correctly_rejected':bool(max(abs(bad_delta))>1)}
            rows.append(row)
    if process.wait()!=0:raise ValueError('Decode failed')
    if negative is None or not negative['correctly_rejected']:raise AssertionError('Actual packet negative control did not fail')
    report={'state':'WITHIN_HELD_CEL_PIXEL_DIAGNOSTIC_NOT_PLANT_APPROVAL','contract_sha256':m.sha(a.contract),'corrected_joints_sha256':m.sha(a.corrected_joints),'video_sha256':m.sha(video),'script_sha256':m.sha(__file__),'actual_decoded_packets':130,'pixel_tolerance_per_axis':1,'rows':rows,'status_counts':{s:sum(r['status']==s for r in rows)for s in sorted({r['status']for r in rows})},'negative_control':negative,'viewable_witnesses':examples,'limits':['Evaluated fixed toe guides nearby opaque beauty patch within4px; source pixel is NOT independently vertex-ID tagged','Each sourcepose has its own patch; only same-cel pairs are matched, not material identity across poses','A unique3x3 actualRGB match uses<=2LSB YUV tolerance; ambiguous/missing patches are not silently accepted','First130 actual packets cover one65cel cycle at120Hz; later repeat interiors not separately checked here','This measures within-hold consumption, not forces/loading/full gait aesthetics or across-pose world plant']}
    report['visual_root_policy']=a.mode
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['state','actual_decoded_packets','status_counts','negative_control']}))


if __name__=='__main__':main()

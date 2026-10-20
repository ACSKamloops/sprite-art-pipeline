"""One native source-part and articulated06 proposal. Guide only, no new art."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[1]
COLORS={'distal':(213,65,178),'shaft':(220,128,42),'thigh':(39,169,201),'joint':(249,237,115)}
CONTROLS={'hip':[58,83],'knee':[52,92],'ankle':[43,93],
          'heel_paint_witness':[41,101],'forefoot_paint_witness':[49,102]}
THIGH=[[54,81],[62,82],[62,86],[58,91],[54,95],[49,94],[47,90],[51,86]]
CALF=[[50,89],[55,91],[55,94],[46,96],[40,95],[39,92],[44,90]]
KNEE_NEW=[[49,89],[54,89],[56,92],[53,95],[49,94],[47,92]]
ANKLE_NEW=[[40,90],[46,90],[48,92],[46,95],[41,95],[39,93]]

def a(p):return np.array(Image.open(p).convert('RGBA'))
def m(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def pm(points):
    im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def part(source,owner):
    p=np.zeros_like(source);p[owner]=source[owner];return p
def literal_rows(owner):
    rows={}
    for y in range(128):
        xs=np.flatnonzero(owner[y])
        if not len(xs):continue
        spans=[];first=last=int(xs[0])
        for x in xs[1:]:
            if x==last+1:last=int(x)
            else:spans.append([first,last]);first=last=int(x)
        spans.append([first,last]);rows[str(y)]=spans
    return rows

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    assert not args.output.exists(),'Fresh output required'
    args.output.mkdir(parents=True)
    for e in json.loads((R/'INPUTS.json').read_text()):assert sha(R/e['retained'])==e['sha256']
    source=a(R/'inputs/source04.png');current=a(R/'inputs/current06.png');body=a(R/'inputs/current06-body.png')[...,3]>0
    q=m(R/'inputs/source04-Q-owner.png');cloth=m(R/'inputs/source04-cloth-owner.png');boot=m(R/'inputs/source04-boot-owner.png')
    yy,xx=np.indices((128,128))
    distal=boot&(yy>=105)
    shaft=boot&~distal
    assert np.array_equal(q,cloth|shaft|distal)
    assert not np.any(cloth&shaft|cloth&distal|shaft&distal)
    names={'thigh-knee-charcoal':cloth,'shaft-calf-leather':shaft,'distal-toe-sole-protected':distal}
    samples={}
    for name,owner in names.items():
        Image.fromarray(part(source,owner)).save(args.output/f'04-{name}.png')
        Image.fromarray(owner.astype('uint8')*255).save(args.output/f'04-{name}-owner.png')
        samples[name]=[{'source04':[int(x),int(y)],'RGBA':source[y,x].tolist()}for y,x in np.argwhere(owner)]
    save(args.output/'SOURCE-PART-SAMPLES.json',samples)
    target_distal=np.zeros_like(source);target_owner=np.zeros((128,128),bool);witnesses=[]
    for y,x in np.argwhere(distal):
        tx,ty=x-12,y-12
        assert 0<=tx<128 and 0<=ty<128
        target_distal[ty,tx]=source[y,x];target_owner[ty,tx]=True
        witnesses.append({'source04':[int(x),int(y)],'target06':[int(tx),int(ty)],'RGBA':source[y,x].tolist()})
    assert not np.any(target_owner&body)
    assert np.array_equal(target_distal[target_owner],source[distal])
    oldq=m(R/'inputs/current06-old-Q-owner.png')
    other=(current[...,3]>0)&~oldq&~body
    new_knee=pm(KNEE_NEW)&~target_owner&~body&~other
    new_ankle=pm(ANKLE_NEW)&~target_owner&~body&~other
    for name,owner in [('proposed-new-knee',new_knee),('proposed-new-ankle',new_ankle),('protected-current06-upper',body),('protected-distal-target',target_owner)]:
        Image.fromarray(owner.astype('uint8')*255).save(args.output/f'{name}-owner.png')
    Image.fromarray(target_distal).save(args.output/'06-protected-distal-source-paint.png')
    save(args.output/'DISTAL-TARGET-WITNESSES.json',witnesses)
    # Diagram overlays are annotations; no calf or thigh texture is synthesized.
    base=current.copy();base[oldq]=0
    base[target_owner]=target_distal[target_owner]
    guide=Image.fromarray(base)
    overlay=Image.new('RGBA',(128,128));draw=ImageDraw.Draw(overlay)
    draw.polygon(CALF,fill=COLORS['shaft']+(100,),outline=COLORS['shaft']+(255,))
    draw.polygon(THIGH,fill=COLORS['thigh']+(100,),outline=COLORS['thigh']+(255,))
    tinted=np.array(overlay);tinted[body|target_owner]=0
    overlay=Image.fromarray(tinted)
    guide=Image.alpha_composite(guide,overlay)
    mark=Image.new('RGBA',(128,128));d=ImageDraw.Draw(mark)
    for owner in [new_knee,new_ankle]:
        for y,x in np.argwhere(owner):
            if (x+y)%3==0:d.point((int(x),int(y)),fill=COLORS['joint']+(255,))
    h,k,n=[tuple(CONTROLS[name])for name in ['hip','knee','ankle']]
    d.line([h,k,n],fill=(250,250,245,255),width=1)
    for label,pos in [('H',h),('K',k),('A',n)]:
        d.ellipse((pos[0]-1,pos[1]-1,pos[0]+1,pos[1]+1),outline=(250,250,245,255))
    marks=np.array(mark);marks[body|target_owner]=0
    guide=Image.alpha_composite(guide,Image.fromarray(marks))
    guide_a=np.array(guide);guide_a[body]=current[body]
    assert np.array_equal(guide_a[body],current[body])
    assert np.array_equal(guide_a[target_owner],target_distal[target_owner])
    Image.fromarray(guide_a).save(args.output/'06-articulated-pose-guide-only.png')
    Image.fromarray(base).save(args.output/'06-upper-otherleg-and-distal-only.png')
    split=source.copy()
    for name,owner in [('thigh',cloth),('shaft',shaft),('distal',distal)]:split[owner,:3]=COLORS[name]
    Image.fromarray(split).save(args.output/'04-native-source-part-diagram.png')
    # Source swatches are actual same-view colors, proposed donors, never new paint.
    swatches=[]
    for role,coords in [('charcoal',[(57,88),(55,92),(56,96),(57,97)]),('leather',[(50,95),(54,96),(57,107),(61,110)])]:
        for point in coords:
            x,y=point
            assert (cloth if role=='charcoal' else boot)[y,x]
            swatches.append({'role':role,'source04_xy':point,'RGBA':source[y,x].tolist()})
    save(args.output/'PROPOSED-JOINT-COVERAGE.json',{
        'status':'Guide masks only; zero authored sprite pixels yet. New joint coverage requires explicit later art work.',
        'knee':{'polygon':KNEE_NEW,'literal_candidate_rows':literal_rows(new_knee),'pixels':int(new_knee.sum())},
        'ankle':{'polygon':ANKLE_NEW,'literal_candidate_rows':literal_rows(new_ankle),'pixels':int(new_ankle.sum())},
        'unique_candidate_joint_coverage_pixels':int((new_knee|new_ankle).sum()),
        'candidate_masks_overlap_pixels':int((new_knee&new_ankle).sum()),
        'owners_excluded':['protected distal target','actual current06 upper owner','retained other visible leg'],
        'palette_witnesses':swatches,
        'limits':'Source palette witnesses guide new shading; they do not recover hidden joint anatomy. No mask is automatically filled.'})
    save(args.output/'PART-LAYOUT-AND-CONTROLS.json',{
        'status':'One articulated source-layout and06pose-guide proposal, not finished art or animation.',
        'registration':{'stage':[128,128],'pivot':[64,112],'draw_scale':.66},
        'source_partition':{'charcoal_thigh_knee':literal_rows(cloth),'leather_shaft_calf':literal_rows(shaft),'protected_distal_toe_sole':literal_rows(distal)},
        'articulation_cut':'Authored source row104/105 paint-owner boundary. It is not a recovered anatomical ankle or actual boot seam.',
        'controls_authored_not_measured':CONTROLS,
        'source_control_proxies':{'hip':[58,85],'knee':[57,96],'ankle':[55,105]},
        'target_segment_lengths_native':{'hip_knee':math.dist(h,k),'knee_ankle':math.dist(k,n)},
        'distal_rigid_translation_from_master04':[-12,-12],
        'distal_extra_vs_current06_sole':[-8,-8],
        'depth_order_back_to_front':['retained current06 other visible leg','separate calf/shaft proposal','protected distal toe/sole','charcoal thigh/knee proposal over proximal calf','unchanged current06 torso/arms/gloves'],
        'source_rgba_constraints':{'upper_exact':True,'distal_target_RGBA_exact':True,'complete_boot_geometry_invariant':False},
        'requires_review':['Actual split near ankle is an authored paint decision.','Leather calf source is irregular and has no clean complete joint master.','Hip is hidden; H is a control below current hem, not a detected bone.','K and A are authored for this single guide.','New joint coverage may be required; no body, glove or other-leg ghost fill is allowed.'],
        'model_calls':0,'canonical_writes':0,'new_sprite_paint_pixels':0,'full_loop_frames':0})
    for size in [128,84,256]:
        for ground,name,ink in [('#e7e3d6','light','black'),('#22252b','dark','white'),('#27392f','game','white')]:
            board=Image.new('RGB',(size*4,size+34),ground);d=ImageDraw.Draw(board)
            for j,(label,image)in enumerate([('source04',source),('source split',split),('current06',current),('06 GUIDE ONLY',guide_a)]):
                im=Image.fromarray(image).resize((size,size),Image.Resampling.NEAREST);board.paste(im,(j*size,34),im);d.text((j*size+3,4),label,fill=ink)
            d.text((3,19),'cyan thigh / orange shaft / magenta protected distal / yellow NEW COVERAGE guide',fill=ink)
            board.save(args.output/f'source-and06-guide-{size}-{name}.png')
    # Joint detail includes literal axes and controls without marking the protected art.
    box=(32,76,68,108);scale=10
    detail=Image.new('RGB',(36*scale+210,32*scale+30),'#e7e3d6')
    crop=Image.fromarray(guide_a).crop(box).resize((36*scale,32*scale),Image.Resampling.NEAREST);detail.paste(crop,(0,30),crop);d=ImageDraw.Draw(detail)
    for label,key in [('H','hip'),('K','knee'),('A','ankle')]:
        x,y=CONTROLS[key];cx=(x-box[0]+.5)*scale;cy=30+(y-box[1]+.5)*scale;d.text((cx+5,cy-8),label,fill='white')
    d.text((365,34),'AUTHORED controls',fill='black')
    for j,(key,value)in enumerate(CONTROLS.items()):d.text((365,55+j*30),key.replace('_paint_witness','')+'\n'+str(value),fill='black')
    d.text((3,5),'06 modular guide; source distal remains exact',fill='black')
    detail.save(args.output/'06-joint-foot-detail10x.png')
    print(json.dumps({'source_part_pixels':{k:int(v.sum())for k,v in names.items()},'knee_candidate_new_coverage':int(new_knee.sum()),'ankle_candidate_new_coverage':int(new_ankle.sum()),'upper_and_distal_exact':True,'new_sprite_paint':0}))

if __name__=='__main__':main()

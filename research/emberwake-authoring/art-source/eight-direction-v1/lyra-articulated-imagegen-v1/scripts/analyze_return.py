"""Replay the single raw return and its failure proof. Never calls a model."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[1]
POINTS={'hip_control':[58,83],'knee_control':[52,92],'ankle_control':[43,93],
        'protected_heel':[41,101],'protected_forefoot':[49,102]}
def a(p):return np.array(Image.open(p).convert('RGBA'))
def m(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    assert not args.output.exists(),'Fresh output required'
    args.output.mkdir(parents=True)
    intake=json.loads((R/'INPUTS.json').read_text())
    for e in intake['retained_sources']:assert sha(R/e['retained'])==e['sha256']
    for e in intake['ordered_actual_image_inputs']:assert sha(R/e['file'])==e['sha256']
    raw_receipt=json.loads((R/'raw/RETURN-RECEIPT.json').read_text())
    assert sha(R/'raw/raw-return.png')==raw_receipt['raw_sha256']
    raw=Image.open(R/'raw/raw-return.png').convert('RGBA')
    assert raw.width==raw.height,'Refuse nonuniform stage normalization'
    normalized=raw.resize((128,128),Image.Resampling.NEAREST)
    assert normalized.tobytes()==Image.open(R/'raw/whole-canvas-nearest128.png').convert('RGBA').tobytes()
    normalized.save(args.output/'raw-wholecanvas128.png')
    gen=np.array(normalized);base=a(R/'inputs/01-authoritative-base.png');guide=a(R/'inputs/02-articulated-pose-guide.png')
    allowed=m(R/'masks/allowed-proximal-and-joints.png')
    owners={'upper':m(R/'masks/protected-upper.png'),'other_visible_lower':m(R/'masks/protected-other-visible-lower.png'),
            'distal':m(R/'masks/protected-distal.png')}
    changed=np.any(gen!=base,axis=2)
    owner_counts={}
    for name,owner in owners.items():
        owner_counts[name]={'pixels':int(owner.sum()),'raw_RGBA_equal_at_target':int((owner&~changed).sum()),
                            'raw_alpha_at_least128_at_target':int((owner&(gen[...,3]>=128)).sum()),
                            'raw_alpha_zero_at_target':int((owner&(gen[...,3]==0)).sum())}
    controls=[]
    for label,(x,y)in POINTS.items():
        controls.append({'name':label,'native_xy':[x,y],'base_RGBA':base[y,x].tolist(),'raw_RGBA':gen[y,x].tolist(),
                         'protected_distal':bool(owners['distal'][y,x]),'inside_allowed_owner':bool(allowed[y,x])})
    bboxes={}
    for label,image in [('base',base),('raw',gen)]:
        bboxes[label]={}
        for threshold in [0,1,16,128]:
            yy,xx=np.where(image[...,3]>threshold)
            bboxes[label][str(threshold)]={'pixels':len(xx),'bbox_inclusive':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]}
    write(args.output/'RAW-GEOMETRY-REJECTION.json',{
        'status':'Rejected at raw geometry gate before protected restoration; no candidate assembled.',
        'actual_generation_calls':1,'tool':'built-in OpenAI image_gen.imagegen','raw_SHA256':raw_receipt['raw_sha256'],
        'raw_size':[raw.width,raw.height],'normalized_size':[128,128],
        'normalization':'Exactly one uniform whole-canvas nearest resize. No crop, translation, fit, stretch, alpha cleanup or repaint.',
        'allowed_owner_pixels':int(allowed.sum()),'allowed_owner_with_raw_alpha_at_least128':int((allowed&(gen[...,3]>=128)).sum()),
        'protected_owner_samples':owner_counts,'literal_control_samples':controls,
        'raw_changed_RGBA_outside_allowed_owner':int((changed&~allowed).sum()),
        'alpha_bboxes_diagnostic_only':bboxes,
        'visual_failure':['Tall conventional foreground boot replaces the requested bent calf and anchored short distal foot.',
                          'Raw ankle target43,93 and protected heel41,101 are transparent.',
                          'Only42 of136 protected distal coordinates receive alpha>=128; that does not establish matching foot identity.',
                          'Raw opaque sprite envelope differs from fixed registration; no fitting/recentering is attempted.'],
        'candidate_constructed':False,'protected_restoration_performed':False,'alpha_cleanup_performed':False,
        'reroll_or_second_model_call':False,'editor_or_engine_change':False,
        'critic_should_see_as_completed_pose':False,
        'critic_scope':'Useful pose/registration adherence failure proof only. Do not submit as a finished articulated pose or assign art scores.'})
    write(args.output/'CONTROL-SAMPLES.json',controls)
    # Literal raw RGBA witnesses make the failed targets inspectable.
    distal_witnesses=[]
    for y,x in np.argwhere(owners['distal']):
        distal_witnesses.append({'native_xy':[int(x),int(y)],'protected_base_RGBA':base[y,x].tolist(),'raw_RGBA':gen[y,x].tolist()})
    write(args.output/'RAW-AT-PROTECTED-DISTAL.json',distal_witnesses)
    for size in [128,256,84]:
        for ground,name,ink in [('#e7e3d6','light','black'),('#22252b','dark','white'),('#27392f','game','white')]:
            board=Image.new('RGB',(4*size,size+32),ground);d=ImageDraw.Draw(board)
            for j,(label,image)in enumerate([('fixed base',base),('pose guide',guide),('RAW REJECTED',gen),('allowed owner',a(R/'inputs/05-allowed-owner-guide.png'))]):
                im=Image.fromarray(image).resize((size,size),Image.Resampling.NEAREST);board.paste(im,(j*size,32),im);d.text((j*size+3,4),label,fill=ink)
            d.text((3,18),'One call; raw geometry failed. No restored final pose.',fill=ink)
            board.save(args.output/f'base-guide-raw-owner-{size}-{name}.png')
    box=(30,76,70,112);scale=8;width=40*scale;height=36*scale
    for ground,name,ink in [('#e7e3d6','light','black'),('#22252b','dark','white'),('#27392f','game','white')]:
        board=Image.new('RGB',(3*width,height+48),ground);d=ImageDraw.Draw(board)
        annotated=gen.copy();overlay=Image.new('RGBA',(128,128));draw=ImageDraw.Draw(overlay)
        for y,x in np.argwhere(owners['distal']):
            if any(not owners['distal'][y+dy,x+dx]for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]):draw.point((int(x),int(y)),fill=(215,65,180,255))
        for label,point in POINTS.items():
            if 'control'not in label:continue
            x,y=point;draw.ellipse((x-1,y-1,x+1,y+1),outline=(100,245,255,255))
        annotated=np.array(Image.alpha_composite(Image.fromarray(annotated),overlay))
        for j,(label,image)in enumerate([('expected guide',guide),('raw normalized',gen),('raw + expected targets',annotated)]):
            im=Image.fromarray(image).crop(box).resize((width,height),Image.Resampling.NEAREST);board.paste(im,(j*width,48),im);d.text((j*width+3,4),label,fill=ink)
        d.text((3,20),'Magenta=protected sole outline; cyan=H58,83 K52,92 A43,93',fill=ink)
        board.save(args.output/f'raw-guide-joints8x-{name}.png')
    print(json.dumps({'raw_rejected':True,'calls':1,'distal':owner_counts['distal'],'outside_owner_RGBA_changes':int((changed&~allowed).sum()),'restoration':False}))

if __name__=='__main__':main()

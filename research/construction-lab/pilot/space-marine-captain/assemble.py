"""Assemble independently owned Captain rig parts on one fixed game canvas."""
from pathlib import Path
import argparse, importlib.util, json, hashlib
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--legs',type=Path,required=True)
    p.add_argument('--upper-rotation',choices=['nearest','scale2x8-approximation'],default='nearest')
    p.add_argument('--upper-motion',choices=['compact','weighted'],default='compact')
    p.add_argument('--foreground-shin',type=Path)
    p.add_argument('--inline-foreground',action='store_true')
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('Use fresh candidate output')
    args.output.mkdir(parents=True);(args.output/'frames').mkdir();(args.output/'layers').mkdir()
    module_path=ROOT/'upper-body-rig-v1/build.py'
    spec=importlib.util.spec_from_file_location('upper',module_path);upper=importlib.util.module_from_spec(spec);spec.loader.exec_module(upper)
    design,parts=upper.construct()
    design['rotation_method']=args.upper_rotation
    design['motion_profile']=args.upper_motion
    leg_path=args.legs/'manifest.json';leg_manifest=json.loads(leg_path.read_text())
    foreground_manifest=json.loads((args.foreground_shin/'manifest.json').read_text()) if args.foreground_shin else None
    if foreground_manifest:
        assert foreground_manifest['source_manifest_sha256']==hashlib.sha256(leg_path.read_bytes()).hexdigest(), 'Foreground pose source mismatch'
        assert len(foreground_manifest['frames'])==len(leg_manifest['frames'])
    frames=[];images=[];source_ids=[]
    for i,record in enumerate(leg_manifest['frames']):
        leg_file=args.legs/record['png'];blob=leg_file.read_bytes()
        assert hashlib.sha256(blob).hexdigest()==record['png_sha256']
        legs=Image.open(leg_file).convert('RGBA')
        assert legs.size==(256,256)
        phase=record['phase'];pelvis=record['pelvis']['origin']
        layers,marks=upper.render_parts(design,parts,phase,pelvis,record['pelvis']['lean_degrees'])
        frame=Image.new('RGBA',(256,256));all_layers={'legs':legs,**layers}
        order=['cape','legs','joint_backing','arm_sword','torso_pack','head','tabard','shield']
        fg_record=foreground_manifest['frames'][i] if foreground_manifest else record.get('foreground') if args.inline_foreground else None
        if fg_record:
            assert abs(fg_record.get('phase',phase)-phase)<1e-12
            fg_root=args.foreground_shin if foreground_manifest else args.legs
            fg_file=fg_root/fg_record['png'];fg_bytes=fg_file.read_bytes()
            assert hashlib.sha256(fg_bytes).hexdigest()==fg_record['png_sha256']
            all_layers['near_shin_foreground']=Image.open(fg_file).convert('RGBA')
            order.insert(order.index('shield'),'near_shin_foreground')
        for name in order:
            frame.alpha_composite(all_layers[name])
            out=args.output/'layers'/f'{i:02}-{name}.png';all_layers[name].save(out)
        filename=f'frames/{i:02}.png';frame.save(args.output/filename);images.append(frame)
        landmarks={side:{'hip':leg['hip'],'knee':leg['knee'],
            'ankle_target':leg['ankle'],'declared_stance':leg['contact'],
            'actual_sole':leg['actual_sole'],
            **{k:leg[k] for k in ['material_sole_source_pixel','material_sole_native_RGBA',
                'boot_material_RGBA_sha256','toe_pitch_degrees','joint_angles_degrees',
                'swing_lift','hip_compression_adjustment'] if k in leg}}
            for side,leg in record['legs'].items()}
        frames.append({'frame':i,'file':filename,'duration_ms':record['duration_ticks']/leg_manifest['fps']*1000,
            'sha256':hashlib.sha256((args.output/filename).read_bytes()).hexdigest(),
            'landmarks':landmarks,'upper_attachments':marks,'pelvis':record['pelvis'],
            'physical_root':record['physical_root'],'bbox':frame.getbbox()})
        source_ids.append({'file':str(leg_file),'sha256':hashlib.sha256(blob).hexdigest()})
    count=len(frames);atlas=Image.new('RGBA',(1024,256*((count+3)//4)))
    for i,frame in enumerate(images):atlas.paste(frame,((i%4)*256,(i//4)*256))
    atlas.save(args.output/'walk-atlas.png')
    previews=[]
    for frame in images:
        bg=Image.new('RGBA',frame.size,(38,43,49,255));bg.alpha_composite(frame)
        previews.append(bg.convert('RGB').resize((512,512),Image.Resampling.NEAREST))
    # GIF has a ten-millisecond clock. Quantize cumulative boundaries rather
    # than each hold: truncating 60-Hz holds changes a 1200ms cycle to720ms.
    gif_delays=[];elapsed=0.;previous_boundary=0
    for f in frames:
        elapsed+=f['duration_ms'];boundary=round(elapsed/10)*10
        gif_delays.append(boundary-previous_boundary);previous_boundary=boundary
    assert min(gif_delays)>=10, 'GIF preview cannot represent this frame rate'
    previews[0].save(args.output/'walk-preview.gif',save_all=True,append_images=previews[1:],
                     duration=gif_delays,loop=0,disposal=2)
    with Image.open(args.output/'walk-preview.gif') as gif:
        actual_gif_ms=0
        for i in range(gif.n_frames):
            gif.seek(i);actual_gif_ms+=gif.info.get('duration',0)
    assert actual_gif_ms==previous_boundary
    manifest={'schema':'captain-layer-probe-v1','status':'UNAPPROVED_EXPERIMENT',
        'source_sha256':design['source_sha256'],'canvas':[256,256],
        'cycle_ms':sum(f['duration_ms']for f in frames),'frames':frames,
        'preview_gif':{'clock_quantum_ms':10,'duration_ms':actual_gif_ms,
            'holds_ms':gif_delays,'method':'cumulative boundary quantization'},
        'direction':'approved_three_quarter','source_parts':'Originalupperbody+newlyauthoredcompletelegs',
        'layer_order':order,'leg_source_manifest_sha256':hashlib.sha256(leg_path.read_bytes()).hexdigest(),
        'leg_renderer_sha256':leg_manifest['renderer_sha256'],
        'leg_input_frames':source_ids,'upper_source_sha256':hashlib.sha256(module_path.read_bytes()).hexdigest(),
        'upper_design_sha256':hashlib.sha256((module_path.parent/'design.json').read_bytes()).hexdigest(),
        'upper_rotation_method':args.upper_rotation,
        'upper_motion_profile':args.upper_motion,
        'near_shin_depth_trial':None if not (foreground_manifest or args.inline_foreground) else {
            'manifest_sha256':hashlib.sha256(((args.foreground_shin if foreground_manifest else args.legs)/'manifest.json').read_bytes()).hexdigest(),
            'rule':'Visible near shin only above hanging holster, below shield; no hidden cuff/thigh promoted'},
        'root_stride':leg_manifest['root_stride'],
        'ground_policy':leg_manifest['ground_policy'],
        'pixel_affine_sha256':hashlib.sha256((module_path.parent/'pixel_affine.py').read_bytes()).hexdigest(),
        'assembler_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'limits':['Unapprovedart;sourcejointreconstructionandmotionmustbereviewed',
                  'Oneview,oneaction;newlegartnotrecoverednativeanatomy',
                  'Wholeheldworld-contactstillneedsverification']}
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'output':str(args.output),'frames':count,'cycle_ms':manifest['cycle_ms']}))


if __name__=='__main__':main()

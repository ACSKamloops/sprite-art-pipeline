#!/usr/bin/env python3
"""Replay retained ImageGen native keys, literal owners and frozen integer maps.

No model execution, paid generation, hidden fill or old trial directory is used.
Requires NumPy/Pillow plus the sibling bundled toolkit. Fresh --out only.
"""
import argparse, gzip, hashlib, importlib.util, json, shutil, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'toolkit'))
from sprite_lab import canonical_json, project_hash, render_frame, render_cel, export_project
from sprite_lab.history import History

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def image(p): return Image.open(p).convert('RGBA')
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();out=args.out.resolve()
    if out.exists(): raise ValueError('Fresh output folder required')
    expected=json.loads((ROOT/'EXPECTED.json').read_text())
    for name,h in expected['source_key_sha256'].items(): assert sha(ROOT/'source-keys'/name)==h
    spec=json.loads((ROOT/'base-build-spec.json').read_text())
    own=json.loads((ROOT/'contact-ownership.json').read_text())
    (out/'base/parts').mkdir(parents=True);(out/'contact-parts').mkdir();(out/'raw-frames').mkdir()
    base=out/'base'; parts=base/'parts'
    for part in own['parts']:
        a=np.array(image(ROOT/'source-keys'/part['source']))
        mask=Image.new('1',(128,128));draw=ImageDraw.Draw(mask);draw.polygon(part['polygon'],fill=1)
        draw.point([tuple(q) for q in part.get('extra_owner_pixels',[])],fill=1)
        a[~np.array(mask,dtype=bool)]=0;a[a[:,:,3]==0]=0
        Image.fromarray(a).save(out/'contact-parts'/f"{part['id']}.png")
    polygons=spec['provenance']['source_part_polygons']; plans=spec['provenance']['odd_slot_plans']
    for n,leg_polygons in polygons.items():
        source=np.array(image(ROOT/'source-keys'/f'{int(n):02}.png'))
        for name,poly in leg_polygons.items():
            mask=Image.new('1',(128,128));ImageDraw.Draw(mask).polygon(poly,fill=1)
            a=source.copy();a[~np.array(mask,dtype=bool)]=0;a[a[:,:,3]==0]=0
            Image.fromarray(a).save(parts/f'part{int(n):02}-{name}.png')
    for n in range(8):
        if n in [0,2,6]: shutil.copy2(ROOT/'source-keys'/f'{n:02}.png',parts/f'{n:02}-whole.png')
        elif n==4:
            for name,source in [('far','forward-left'),('near','trailing-right'),('upper','upper')]:
                shutil.copy2(out/'contact-parts'/f'{source}.png',parts/f'04-{name}.png')
        else:
            plan=plans[str(n)];key=plan['key'];upper=image(ROOT/'source-keys'/f'{key:02}.png')
            upper.paste((0,0,0,0),(0,83,128,128))
            if n==3:
                mask=Image.new('1',(128,128));ImageDraw.Draw(mask).polygon(polygons['2']['far'],fill=1)
                a=np.array(upper);a[np.array(mask,dtype=bool)]=0;upper=Image.fromarray(a)
            upper.save(parts/f'{n:02}-upper.png')
            for name in ['far','near']:
                plan_part=plan[name]
                source=(parts/plan_part['source']) if plan_part['source'].startswith('part') else out/'contact-parts'/Path(plan_part['source']).name
                meta=json.loads((ROOT/'maps/base-v5'/f'{n:02}-{name}.json').read_text())
                assert sha(source)==meta['source_sha256'],(n,name,'source bytes differ')
                with np.load(ROOT/'maps/base-v5'/f'{n:02}-{name}.npz',allow_pickle=False) as data: xy=data['source_xy']
                a=np.array(image(source));assert xy.shape==(128,128,2)
                assert (xy>=0).all() and (xy<128).all()
                Image.fromarray(a[xy[:,:,1],xy[:,:,0]]).save(parts/f'{n:02}-{name}.png')
    # Preserve the exact construction spec and PNG identity so the real journal's
    # project/cel preconditions remain meaningful. No final frame pixels are inputs.
    shutil.copy2(ROOT/'base-build-spec.json',base/'construction-spec.json')
    loader=importlib.util.spec_from_file_location('construct',ROOT.parent/'toolkit/scripts/sprite_construct.py')
    mod=importlib.util.module_from_spec(loader);loader.loader.exec_module(mod)
    project=mod.construct(base/'construction-spec.json')
    assert project_hash(project)==expected['base_project_sha256'],'Base project precondition differs'
    (base/'project.json').write_text(canonical_json(project)+'\n')
    journal=json.loads(gzip.decompress((ROOT/'arm-v6-journal.json.gz').read_bytes()).decode());history=History.replay(project,journal)
    final=history.project;assert project_hash(final)==expected['final_project_sha256']
    # Independently replay each upper map and compare to the journal's cel result.
    arm_checks=[]
    for n in range(1,8):
        cel=project['frames'][n]['cels']['upper'];a=np.array(render_cel(project,cel))
        with np.load(ROOT/'maps/arm-v6'/f'{n:02}-upper.npz',allow_pickle=False) as data: xy=data['source_xy']
        candidate=a.copy();sampled=a[xy[:,:,1],xy[:,:,0]];candidate[:83]=sampled[:83];candidate[candidate[:,:,3]==0]=0
        assert candidate.tobytes()==render_cel(final,cel).tobytes()
        arm_checks.append({'slot':n,'frozen_map_equals_real_journal_cel':True})
    checks=[]
    for row in expected['expected_raw_ne']:
        n=row['frame'];im=render_frame(final,f'frame{n:02}')
        assert hashlib.sha256(im.tobytes()).hexdigest()==row['rgba_sha256']
        path=out/'raw-frames'/f'{n:02}.png';im.save(path)
        checks.append({'slot':n,'decoded_RGBA_exact':True,'png_bytes_exact':sha(path)==row['png_sha256']})
    (out/'source-restored-project.json').write_text(canonical_json(final)+'\n')
    receipt={'passed':True,'base_project_sha256':project_hash(project),'final_project_sha256':project_hash(final),
      'raw_NE':checks,'arm_map_checks':arm_checks,'journal_replay_exact':True,
      'no_final_frame_paint_used_as_rebuild_input':True,'no_model_execution':True,
      'semantic_generation_boundary':expected['semantic_generation_boundary']}
    cleanup_path=ROOT/'PRODUCTION-CLEANUP.json'
    if cleanup_path.exists():
        cleanup=json.loads(cleanup_path.read_text());(out/'production-frames').mkdir();cleanchecks=[]
        for n in range(8):
            a=np.array(image(out/'raw-frames'/f'{n:02}.png'));before=a.copy()
            pixels=cleanup['frames'][n]['pixels']
            for entry in pixels:
                x,y=entry['at'];assert a[y,x].tolist()==entry['before'];a[y,x]=entry['after']
            changed=np.any(a!=before,axis=2);assert int(changed.sum())==len(pixels)
            assert hashlib.sha256(a.tobytes()).hexdigest()==cleanup['frames'][n]['rgba_sha256']
            final_path=out/'production-frames'/f'{n:02}.png';Image.fromarray(a).save(final_path)
            cleanchecks.append({'slot':n,'literal_changed_pixels':len(pixels),'outside_mask_exact':True,'decoded_RGBA_exact':True,
                'png_bytes_exact':sha(final_path)==cleanup['frames'][n]['png_sha256']})
        receipt['production_cleanup']=cleanchecks
        mirror=out/'production-northwest-conditional';mirror.mkdir()
        for n in range(8):
            source=image(out/'production-frames'/f'{n:02}.png')
            reflected=source.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            target=Image.new('RGBA',(128,128));target.paste(reflected,(1,0));target.save(mirror/f'{n:02}.png')
        receipt['conditional_northwest']={'frames':8,'mapping':'x_new=128-x_old; y unchanged',
            'status':'conditional source mirror only; no independent repaint or new art rating'}
    (out/'VERIFY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'passed':True,'out':str(out),'raw_RGBA_frames':8,'production_cleanup':'production_cleanup'in receipt}))
if __name__=='__main__':main()

"""Export a frozen Captain candidate to the existing pixel editor/LibreSprite.

The art decision stays external. Never grants approval or changes source art.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from sprite_lab import export_aseprite,project_hash,canonical_json
from sprite_lab.core import render_frames


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('Keep prior editable projects frozen')
    args.output.mkdir(parents=True);(args.output/'sources').mkdir()
    manifest_path=args.candidate/'manifest.json';manifest=json.loads(manifest_path.read_text())
    assert manifest['canvas']==[256,256]
    spec={'schema':'sprite-construction-spec/v1',
        'canvas':{'width':256,'height':256,'render_pivot':[130,143],'ground_pivot':[130,242]},
        'layers':[{'id':name,'name':name.replace('_',' ').title(),'locked':False}
                  for name in manifest['layer_order']],
        'frames':[],'animations':[],
        'provenance':{'candidate_manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            'art_status':'External source-bound reviews remain authoritative; export gives zero art points',
            'guide_policy':'Rounded editor landmarks only; authoritative floating rig anchors remain in candidate manifest',
            'sharing':'Identical same-layer RGBA cels share one source; edits affect all their frame bindings'}}
    uniform_sixty=all(abs(f['duration_ms']-1000/60)<1e-8 for f in manifest['frames'])
    fps=60 if uniform_sixty else 1000
    if not uniform_sixty:
        assert all(abs(f['duration_ms']-round(f['duration_ms']))<1e-8 for f in manifest['frames']), 'Exact millisecond timing required'
    source_bindings={};events=[];elapsed=0
    for frame in manifest['frames']:
        ticks=1 if uniform_sixty else round(frame['duration_ms'])
        i=frame['frame'];row={'id':f'walk-{i:02}','duration_ticks':ticks,'cels':{},'landmarks':{}}
        for name in manifest['layer_order']:
            path=args.candidate/'layers'/f'{i:02}-{name}.png'
            image=Image.open(path).convert('RGBA')
            digest=hashlib.sha256(image.tobytes()).hexdigest();key=(name,digest)
            if key not in source_bindings:
                relative=f'sources/{name}-{digest}.png'
                (args.output/relative).write_bytes(path.read_bytes());source_bindings[key]=relative
            row['cels'][name]={'image':source_bindings[key],'at':[0,0]}
        for side,leg in frame['landmarks'].items():
            for name in ['hip','knee','ankle_target','actual_sole']:
                row['landmarks'][side+'_'+name]=[round(v)for v in leg[name]]
            stance=leg['declared_stance']
            # The cycle begins during near-foot stance; don't invent a new
            # near-contact event at0. Emit actual sampled stance transitions.
            previous=manifest['frames'][i-1]['landmarks'][side]['declared_stance']
            if stance!=previous:
                events.append({'at_tick':elapsed,'name':f'{side}_foot_'+('contact' if stance else 'lift')})
        spec['frames'].append(row);elapsed+=ticks
    spec['animations']=[{'id':'combat_ready_walk','frames':[r['id']for r in spec['frames']],
                         'fps':fps,'loop':True,'events':events}]
    spec_path=args.output/'construction.json';spec_path.write_text(json.dumps(spec,indent=2)+'\n')
    module_spec=importlib.util.spec_from_file_location('construct',ROOT/'scripts/sprite_construct.py')
    module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
    project=module.construct(spec_path)
    (args.output/'project.json').write_text(canonical_json(project)+'\n')
    images=render_frames(project,[r['id']for r in project['frames']])
    for image,record in zip(images,manifest['frames']):
        expected_path=args.candidate/record['file']
        assert hashlib.sha256(expected_path.read_bytes()).hexdigest()==record['sha256']
        assert image.tobytes()==Image.open(expected_path).convert('RGBA').tobytes()
    exchange=export_aseprite(project,args.output/'captain-walk.aseprite')
    assert sum(r['milliseconds']for r in exchange['timing'])==round(manifest['cycle_ms'])
    receipt={'candidate_manifest_sha256':spec['provenance']['candidate_manifest_sha256'],
             'project_sha256':project_hash(project),'frames':len(images),'layers':len(project['layers']),
             'cels':len(project['cels']),'RGBA_palette_entries':len(project['palette']),
             'all_layer_composites_exact_source':True,'cycle_ticks':elapsed,'fps':fps,
             'ase_actual_ms':sum(r['milliseconds']for r in exchange['timing']),
             'ase_sha256':exchange['ase_sha256'],'scope':'Construction/exchange only; independent tool reopen remains required'}
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':main()

"""Fixed-cell AI lower art + exact upper source comparator, no art approval."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parent
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--upper', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists(), 'Preserve previous comparator'
    source = P/'source/raw-eight-legs.png'
    raw = Image.open(source).convert('RGBA')
    assert abs(raw.width/raw.height-2) < .01, 'Only uniform 2:1 sheet supported'
    atlas = np.array(raw.resize((512,256), Image.Resampling.NEAREST))
    atlas[atlas[:,:,3] < 128] = 0
    atlas[atlas[:,:,3] >= 128,3] = 255
    atlas = Image.fromarray(atlas)
    construction = json.loads((a.upper/'construction.json').read_text())
    base_spec = json.loads((a.upper/'audition-physical.json').read_text())
    lower = {'far_thigh','far_shin','far_cap','far_boot',
             'near_thigh','near_shin','near_cap','near_boot'}
    a.output.mkdir(parents=True)
    (a.output/'frames').mkdir()
    atlas.save(a.output/'native-lower-atlas.png')
    frames, records, images = [], [], []
    for j, index in enumerate(range(0,72,9)):
        cell = atlas.crop((j%4*128,j//4*128,j%4*128+128,j//4*128+128))
        candidate = Image.new('RGBA',(256,256))
        candidate.alpha_composite(cell,(68,117))
        composed = Image.new('RGBA',(256,256))
        foreground_upper = Image.new('RGBA',(256,256))
        inserted = False
        inputs = {}
        for name in construction['layer_order']:
            if name in lower:
                if not inserted:
                    composed.alpha_composite(candidate)
                    inserted = True
            else:
                path = a.upper/'layers'/f'{index:03}-{name}.png'
                image = Image.open(path).convert('RGBA')
                inputs[name] = {'file':str(path.resolve()), 'sha256':sha(path)}
                composed.alpha_composite(image)
                if inserted:
                    foreground_upper.alpha_composite(image)
        # Exact source upper/equipment wherever fully opaque above lower art.
        full = np.array(composed)
        upper_pixels = np.array(foreground_upper)
        opaque = upper_pixels[:,:,3] == 255
        assert np.array_equal(full[opaque],upper_pixels[opaque])
        path = a.output/'frames'/f'{j:03}.png'
        composed.save(path)
        images.append(composed)
        original = base_spec['frames'][index]
        frames.append({'index':j, 'file':str(path.relative_to(a.output)),
                       'sha256':sha(path), 'duration_ms':150,
                       'phase_label':f'AI key {j}, source pose {index}; contacts unverified',
                       'physical_root':original['physical_root']})
        records.append({'key':j,'source_index':index,'upper_source_layers':inputs,
                        'fixed_crop':[68,117,196,245],
                        'foreground_upper_opaque_rgba_exact':True})
    for policy in ['in_place','physical']:
        spec = dict(base_spec)
        spec.update(name='UNAPPROVED guided AI 8-key lower artwork',frames=frames,root_policy=policy)
        (a.output/f'audition-{policy}.json').write_text(json.dumps(spec,indent=2)+'\n')
    sheet = Image.new('RGBA',(1024,560),(35,38,44,255))
    d = ImageDraw.Draw(sheet)
    for j, im in enumerate(images):
        xy=(j%4*256,j//4*280)
        sheet.alpha_composite(im,xy)
        d.text((xy[0]+4,xy[1]+258),f'key{j}/pose{j*9} UNAPPROVED',fill='white')
    sheet.save(a.output/'eight-keys-native.png')
    sheet.resize((2048,1120),Image.Resampling.NEAREST).save(a.output/'eight-keys-2x.png')
    receipt={'state':'UNAPPROVED_GUIDED_AI_KEY_ART','raw_sha256':sha(source),
             'guide_sha256':sha(P/'source/pose-guide.png'),'builder_sha256':sha(__file__),
             'upper_construction_sha256':sha(a.upper/'construction.json'),
             'processing':'Uniform whole 2:1 atlas nearest resize512x256, alpha threshold128; fixed128cells and placement68,117 selected before generation; no recentering or per-pose fit',
             'records':records,'limits':['AI artwork may alter landmarks, ornament and mass; no contact proof inherited from guide',
                                       'Eight150ms holds; continuous root with held artwork may cause visible stance slide',
                                       'Merged lower cels are artwork, not a reusable limb rig or full action/direction library',
                                       'Opaque upper source preserved does not establish lower identity or art acceptance']}
    (a.output/'construction.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(a.output)

if __name__ == '__main__':
    main()

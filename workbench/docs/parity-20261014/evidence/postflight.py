"""Offline verification of real browser-produced artifacts. No network API calls."""
import argparse, hashlib, json, sys, zipfile
from pathlib import Path, PurePosixPath

parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--package-root')
parser.add_argument('--expected-fingerprint')
args=parser.parse_args()
if args.package_root:
    sys.path.insert(0,args.package_root)
import numpy as np
from PIL import Image
from sprite_workbench.core import Store, load_sequence, canonical_json
from sprite_workbench import construction
from sprite_workbench.export import import_editable
import sprite_workbench
from sprite_workbench.readiness import source_fingerprint
actual_fingerprint=source_fingerprint()
assert not args.expected_fingerprint or actual_fingerprint==args.expected_fingerprint

root=Path(args.output).resolve()
assert not(root/'POSTFLIGHT.json').exists(), 'Preserve prior evidence'
records=json.loads((root/'records.json').read_text())
sha=lambda raw: hashlib.sha256(raw).hexdigest()
checks=[]
def check(name,**evidence):
    checks.append({'name':name,'status':'passed',**evidence})

source_path=Path('/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014/inputs/hero-256.png')
source=np.asarray(Image.open(source_path).convert('RGBA'))
assert sha(source_path.read_bytes())==records['upload']['source_bytes']
assert sha(source.tobytes())==records['upload']['source_rgba_sha256']
for operation in ['serialize','reference_palette','mask','decode','place']:
    result=records[operation]['result']
    pixels=np.asarray(Image.open(root/records[operation]['png']).convert('RGBA'))
    assert sha(pixels.tobytes())==result['output_rgba_sha256']
    assert pixels.shape[:2]==(result['height'],result['width'])
    check('PNG readback equals output raw RGBA SHA: '+operation,rgba_sha256=sha(pixels.tobytes()))
normalized=source.copy();normalized[normalized[...,3]==0,:3]=0
serialized=np.asarray(Image.open(root/'serialize.png').convert('RGBA'))
assert np.array_equal(serialized,normalized)
assert np.array_equal(np.asarray(Image.open(root/'decode.png').convert('RGBA')),source)
assert records['transparency']['result']['has_exact_zero_alpha']==bool(np.any(source[...,3]==0))
check('serialization only zeros hidden RGB; decoded PNG exact; zero-alpha predicate exact')
masked=np.asarray(Image.open(root/'mask.png').convert('RGBA'))
mask_colors=np.unique(masked.reshape(-1,4),axis=0).tolist()
assert all(color in [[0,0,0,255],[255,255,255,255]] for color in mask_colors)
check('request-mask encoding uses opaque black/white RGB',colors=mask_colors)
archive=root/'painted-package.zip'
assert sha(archive.read_bytes())==records['export']['zip']
with zipfile.ZipFile(archive) as z:
    names=set(z.namelist())
    for name in names:
        p=PurePosixPath(name)
        assert not p.is_absolute() and '..' not in p.parts
    package=json.loads(z.read('PACKAGE.json'))
    inventory={f['file']:f for f in package['files']}
    assert set(inventory)==names-{'PACKAGE.json'}
    for name,item in inventory.items():
        raw=z.read(name)
        assert len(raw)==item['bytes'] and sha(raw)==item['sha256']
    index=json.loads(z.read('editable/index.json'))
    assert records['painted']['footprint'] in index['artifact_ids']
    for ident in index['artifact_ids']:
        assert sha(z.read('editable/artifacts/'+ident))==ident
    unpacked=root/'unpacked'
    assert not unpacked.exists()
    z.extractall(unpacked)
check('actual ZIP exact inventory and all CAS bytes verified',files=len(names),editable_artifacts=len(index['artifact_ids']))
store=Store(root/'cold-store')
sequence=import_editable(store,unpacked/'editable')
assert sequence==records['export']['sequence']
history_id=records['afterUndoRedo']['history']
history=construction.load_history(store,history_id)
assert history['project']==records['painted']['project']
history_doc=store.get_json(history_id)
assert any(row['artifact']==records['painted']['footprint'] for row in history_doc['source_evidence'])
footprint=store.get_json(records['painted']['footprint'])
assert footprint['results'][0]['command']['method']=='ellipse-filled'
# load_history above performs current original-source footprint replay and verifies
# the indexed transaction binding in a fresh Store, not the warm server cache.
check('cold editable import and source-footprint-bound history replay',footprint=records['painted']['footprint'])
before=construction.load_project(store,history_doc['initial_project'])
after=construction.load_project(store,history_doc['project'])
cel_id=records['painted']['receipt']['transaction']['operations'][0]['cel_id']
command=records['painted']['receipt']['transaction']['operations'][0]
width=before['canvas']['width'];old=before['cels'][cel_id]['pixels'];new=after['cels'][cel_id]['pixels']
allowed={y*width+x for x,y in footprint['results'][0]['points']}
assert len(old)==len(new)
changed={i for i,(a,b) in enumerate(zip(old,new)) if a!=b}
assert changed and changed<=allowed
assert all(new[i]==command['candidate_pixels'][i] for i in allowed)
check('actual paint changed only original footprint pixels',changed_pixels=len(changed),unique_source_points=len(allowed))
manifest,arrays=load_sequence(store,sequence)
source_manifest,_=load_sequence(store,records['upload']['sequence'])
assert len(arrays)==1 and manifest['frames'][0]['duration']==source_manifest['frames'][0]['duration']
assert np.array_equal(np.asarray(Image.open(unpacked/'frames/frame-0000.png').convert('RGBA')),arrays[0])
# This imported still is deliberately not motion proof or an inferred sprite FPS.
check('single imported still preserves supplied rational hold and exported frame bytes',duration=manifest['frames'][0]['duration'],loop=manifest['loop'])
report={'version':1,'scope':'Actual browser export bytes, source footprint and cold history; no motion/art approval',
        'source_fingerprint':actual_fingerprint,'recipe_sha256':sha(Path(__file__).read_bytes()),'package_path':str(Path(sprite_workbench.__file__).resolve()),'checks':checks,'passed':len(checks),
        'records_sha256':sha((root/'records.json').read_bytes()),'zip_sha256':sha(archive.read_bytes())}
(root/'POSTFLIGHT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'output':str(root/'POSTFLIGHT.json')}))

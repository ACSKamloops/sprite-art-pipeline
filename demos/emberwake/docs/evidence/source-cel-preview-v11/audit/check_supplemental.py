#!/usr/bin/env python3
"""Inspect additive root receipts and their recorded outputs; no native tool call."""
from pathlib import Path
import hashlib,json,struct
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
NEW=Path('/home/astra/artifacts/emberwake-source-cel-game-preview-v11')
BASE=Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1')
checks=[];details={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def image(p):return np.array(Image.open(p).convert('RGBA'))
def check(ok,note,detail=None):checks.append({'ok':bool(ok),'note':note,**({'detail':detail} if detail is not None else {})})
receipt=read(NEW/'processed-export-verification/RECEIPT.json')
check(receipt['passed'] is True and len(receipt['results'])==6 and all(x['ok'] for x in receipt['results']),'additive processed export receipt contains all six successful resources')
check(receipt['actual_Web_PCK_sha256']==sha(Path('/home/astra/artifacts/emberwake-walk-cadence-study-v1/game-v11/index.pck')),'processed export receipt bound to actual served PCK')
for a in ['rowan','lyra','brann']:
    source=image(NEW/'bake'/a/'atlas.png');decoded=image(NEW/'decoded-export'/f'{a}-decoded.png');processed=image(NEW/'processed-export-verification'/f'{a}-expected-processed.png')
    row=next(x for x in receipt['results'] if x['kind']=='atlas' and x['resource']==('res://assets/hero/atlas.png' if a=='rowan' else f'res://assets/characters/{a}/atlas.png'))
    delta=np.any(source!=decoded,axis=2);alpha=source[:,:,3]
    entry={'source_RGBA_sha256':hashlib.sha256(source.tobytes()).hexdigest(),'decoded_RGBA_sha256':hashlib.sha256(decoded.tobytes()).hexdigest(),'processed_RGBA_sha256':hashlib.sha256(processed.tobytes()).hexdigest(),'raw_differing_pixels':int(delta.sum()),'changed_original_alpha_range':[int(alpha[delta].min()),int(alpha[delta].max())],'changed_alpha_positive_pixels':int((delta & (alpha>0)).sum()),'alpha_everywhere_exact':bool(np.array_equal(alpha,decoded[:,:,3])),'source_alpha20_or_higher_exact':bool(np.array_equal(source[alpha>=20],decoded[alpha>=20]))}
    details[a+'_export']=entry
    check(entry['source_RGBA_sha256']==row['raw_source_RGBA_sha256'] and entry['decoded_RGBA_sha256']==row['actual_sha256'] and entry['processed_RGBA_sha256']==row['expected_fix_alpha_edges_RGBA_sha256'],a+' independently decoded PNG hashes equal processed export receipt')
    check(np.array_equal(decoded,processed) and entry['alpha_everywhere_exact'] and entry['source_alpha20_or_higher_exact'] and entry['changed_original_alpha_range'][1]==19,a+' actual exported PNG equals processed expected PNG; alpha exact and RGB difference limited to original alpha0..19')

brann=BASE/'brann-ne-jab-editor-v1';r=read(brann/'ROOT-REPLAY.json');fresh=Path(r['fresh_output'])
check(r['actual_targeted_checks']==79 and r['common_generated_files']==63 and r['byte_exact']==56 and len(r['path_only_metadata_or_logs'])==7 and not r['other_differences'],'Brann root native replay accurately declares 79 checks and 56/63 byte exact with seven path-only differences')
for row in r['files']:
    p=fresh/row['file'];q=brann/'run'/row['file']
    check(sha(p)==row['fresh_sha256'] and sha(q)==row['primary_sha256'],'actual root replay hash pair '+row['file'])
    if not row['byte_exact']:
        a=p.read_text();b=q.read_text()
        priorpackage='/home/astra/artifacts/emberwake-brann-ne-jab-editor-v1'
        normalized=a.replace(str(fresh),'/ACTUAL_OUTPUT_ROOT/').replace(str(brann),'/ACTUAL_PACKAGE_ROOT/')
        prior=b.replace(priorpackage+'/run','/ACTUAL_OUTPUT_ROOT/').replace(priorpackage,'/ACTUAL_PACKAGE_ROOT/')
        check(normalized==prior,'actual declared output/package path-only metadata/log difference '+row['file'])
verified=read(fresh/'VERIFIED.json')
check(verified['passed'] is True and len(verified['checks'])==79 and all(x['passed'] for x in verified['checks']),'actual preserved root VERIFIED has all 79 targeted checks true')
native=fresh/'native/preferred-reopened.aseprite'
check(sha(native)==r['native_reopened_ASE_sha256']==read(brann/'PACKAGE.json')['native_primary_sha256'],'actual root reopened native ASE equals retained primary hash')
data=native.read_bytes();size,magic,count,width,height=struct.unpack_from('<I4H',data);pos=128;holds=[]
for _ in range(count):
    n,framemagic,chunks,duration=struct.unpack_from('<I3H',data,pos);assert framemagic==0xF1FA;holds.append(duration);pos+=n
check(size==len(data) and magic==0xA5E0 and count==8 and width==height==128 and pos==len(data) and holds==[60,70,55,55,65,35,35,35],'actual reopened ASE header/frame clock: eight128x128cels, exact410ms holds',holds)
for i,sourceframe in enumerate(['08','09','10','11','12','13','14','22']):
    png=fresh/'native/render'/f'frame{i+1}.png'
    expected=BASE/'brann-ne-jab-fist-v1'/('raw-v1/11.png' if sourceframe=='11' else f'inputs/{sourceframe}.png')
    check(np.array_equal(image(png),image(expected)),'actual retained root native render RGBA equals selected source '+sourceframe)
details['native']={'root_replay_receipt_sha256':sha(brann/'ROOT-REPLAY.json'),'native_ASE_sha256':sha(native),'holds_ms':holds,'flat_layer_limitation':read(brann/'PACKAGE.json')['qualification'],'scope':r['scope']}
result={'scope':'Read-only offline inspection of existing additive root/native/export receipts and output pixels. No engine/editor/browser invocation by auditor.','passed':all(x['ok'] for x in checks),'checks':checks,'details':details}
(OUT/'SUPPLEMENTAL-CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':result['passed'],'checks':len(checks),'failures':[x for x in checks if not x['ok']],'details':details},indent=2))

"""Execute exact root frozen builders with side effects confined to a private ROOT."""
from pathlib import Path
from PIL import Image
import argparse,json,hashlib,shutil,runpy,sys,os
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(folder):return{str(p.relative_to(folder)):sha(p)for p in folder.rglob('*')if p.is_file()and p.suffix not in ['.pyc']and'__pycache__'not in p.parts}
def main(root,artifacts):
 if artifacts.exists():raise ValueError('Refuse previous rebuilt artifacts')
 captain=root/'pilot/space-marine-captain';upper=captain/'upper-body-rig-v1';protected_before=hashes(upper);artifacts.mkdir(parents=True);snapshot=artifacts/'snapshot';private=snapshot/'pilot/space-marine-captain';(private/'upper-body-rig-v1').mkdir(parents=True);(private/'references').mkdir();(snapshot/'pilot/captain-leg-rig-v1').symlink_to(root/'pilot/captain-leg-rig-v1',target_is_directory=True)
 inputs={}
 for n in ['build.py','design.json','pixel_affine.py']:
  src=upper/n;shutil.copy2(src,private/'upper-body-rig-v1'/n);inputs[str(src.relative_to(root))]=sha(src)
 src=captain/'references/approved-256.png';shutil.copy2(src,private/'references/approved-256.png');inputs[str(src.relative_to(root))]=sha(src)
 for n in ['assemble.py','retime.py']:
  shutil.copy2(captain/n,private/n);inputs[str((captain/n).relative_to(root))]=sha(captain/n)
 legs=Path('pilot/captain-leg-rig-v1/convex-near-greave-v1/long-stride-keyshape-v3');inputs[str(legs/'manifest.json')]=sha(root/legs/'manifest.json');fixed=artifacts/'fresh-v17';weighted=artifacts/'fresh-v18';cwd=Path.cwd();argv=sys.argv[:]
 try:
  os.chdir(snapshot);sys.argv=[str(captain/'assemble.py'),'--legs',str(legs),'--upper-rotation','scale2x8-approximation','--upper-motion','weighted','--inline-foreground','--output',str(fixed)];ns=runpy.run_path(str(captain/'assemble.py'),run_name='isolated_exact_builder');ns['main'].__globals__['ROOT']=private;ns['main']()
  sys.argv=[str(captain/'retime.py'),'--candidate',str(fixed),'--output',str(weighted)];runpy.run_path(str(captain/'retime.py'),run_name='__main__')
 finally:os.chdir(cwd);sys.argv=argv
 checks={};comparisons={}
 for label,new,old in [('v17',fixed,captain/'assembled-v17'),('v18',weighted,captain/'assembled-v18')]:
  a=json.loads((new/'manifest.json').read_text());b=json.loads((old/'manifest.json').read_text());rgba=[];layerrows=[]
  for i in range(72):
   na=Image.open(new/a['frames'][i]['file']).convert('RGBA').tobytes();nb=Image.open(old/b['frames'][i]['file']).convert('RGBA').tobytes();rgba.append({'frame':i,'actualRGBA_equal':na==nb,'RGBA_sha256':hashlib.sha256(na).hexdigest()})
   for name in a['layer_order']:
    fn=f'{i:02}-{name}.png';pa=Image.open(new/'layers'/fn).convert('RGBA').tobytes();pb=Image.open(old/'layers'/fn).convert('RGBA').tobytes();layerrows.append({'layer':fn,'actualRGBA_equal':pa==pb,'RGBA_sha256':hashlib.sha256(pa).hexdigest()})
  checks[label+'_72_actualRGBA']=all(r['actualRGBA_equal']for r in rgba);checks[label+'_648_actualLayerRGBA']=len(a['layer_order'])==9 and all(r['actualRGBA_equal']for r in layerrows);checks[label+'_all_holds']=all(x['duration_ms']==y['duration_ms']for x,y in zip(a['frames'],b['frames']));checks[label+'_root_pelvis_landmarks_attachments']=all(all(x[k]==y[k]for k in ['physical_root','pelvis','landmarks','upper_attachments'])for x,y in zip(a['frames'],b['frames']));checks[label+'_cycle1200']=a['cycle_ms']==b['cycle_ms']==1200;checks[label+'_manifest_bytes']=sha(new/'manifest.json')==sha(old/'manifest.json');comparisons[label]={'root_manifest_sha256':sha(old/'manifest.json'),'rebuilt_manifest_sha256':sha(new/'manifest.json'),'frame_RGBA':rgba,'layer_RGBA':layerrows,'holds_ms':[f['duration_ms']for f in a['frames']]}
 checks['root_upper_inputs_and_derived_parts_unchanged']=protected_before==hashes(upper);checks['root_builder_input_bytes_unchanged']=all(sha(root/n)==d for n,d in inputs.items());receipt={'schema':'captain-frozen-rebuild-receipt/v1','passed':all(checks.values()),'checks':checks,'root_repository':str(root),'receipt_builder_sha256':sha(Path(__file__)),'inputs_sha256':inputs,'private_side_effect_policy':'Exactroot assemble.py runvia runpy; onlyitsruntimeROOT redirectedto privateexactupper/design/pixel_affine/approvedPNGsnapshot. construct() writesparts/rest/partitionproof ONLYthere. Readonlylegsymlink preservesoriginalrelativeinputpathstrings. ROOTretime.py writesonlyfreshownoutput. No root filesedited.','comparisons':comparisons,'scope':'Exactsource/72finalRGBA/648layerRGBA/holds/root/pelvis/landmarks/attachments/cycle/manifests repeatability. NOTartapproval/≥9rating/GPU/worldcontactproof.'};(HERE/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('rebuildpassed',receipt['passed'],checks)
 if not receipt['passed']:raise RuntimeError('Fresh rebuild discrepancy')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('/home/astra/projects/sprite-construction-lab'));p.add_argument('--artifacts',type=Path,default=HERE/'artifacts');a=p.parse_args();main(a.root.resolve(),a.artifacts.resolve())

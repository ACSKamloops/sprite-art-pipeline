#!/usr/bin/env python3
"""Assemble a separate review package with only the SE get-up rebound."""
import argparse, hashlib, importlib.util, json, shutil
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--clip',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 repo=a.repo.resolve();out=a.output.absolute();source=repo/'examples/current-hero/package'
 assert not out.exists() and not out.is_symlink()
 old=json.loads((source/'library.json').read_text());shutil.copytree(source,out)
 dest=out/'clips/SE/get_up/leg-continuity-trial';shutil.copytree(a.clip,dest)
 spec=importlib.util.spec_from_file_location('candidate_bank',repo/'research/pixelengine-imagen/tools/build-rpg-bank.py');bank=importlib.util.module_from_spec(spec);spec.loader.exec_module(bank)
 clip=bank.review_clip(out,dest/'manifest.json','candidate','human-reported-leg-loss-repair-pending-review','get_up','SE','leg-continuity-trial')
 library=json.loads(json.dumps(old));library['clips'].append(clip);library['selected']['get_up_SE']=clip['id']
 before={c['id']:c for c in old['clips']};after={c['id']:c for c in library['clips']}
 unchanged=[]
 for name,ident in old['selected'].items():
  if name!='get_up_SE':
   assert ident==library['selected'][name] and before[ident]==after[ident];unchanged.append(name)
 assert len(unchanged)==135
 for i in (0,9):assert clip['frames'][i]['rgba_sha256']==before[old['selected']['get_up_SE']]['frames'][i]['rgba_sha256']
 assert [f['hold'] for f in clip['frames']]==[f['hold'] for f in before[old['selected']['get_up_SE']]['frames']]
 (out/'library.json').write_text(json.dumps(library,indent=2)+'\n')
 receipt={'changed_binding':'get_up_SE','unchanged_bindings':135,'preferred_walk_exact':True,'getup_endpoints_and_holds_exact':True,'candidate_library_sha256':hashlib.sha256((out/'library.json').read_bytes()).hexdigest(),'art_acceptance':False}
 (out/'CANDIDATE-ASSEMBLY.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

"""Bind neutral motion-review-harness inputs without altering renderer images."""
from pathlib import Path
import json,hashlib,argparse,math
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def make(pack):
 m=json.loads((pack/'manifest.json').read_text());n=len(m['frames']);keys=json.loads((Path(__file__).parent/'motion.json').read_text())['keys'];holds=[round((i+1)*m['cycle_ms']/n)-round(i*m['cycle_ms']/n)for i in range(n)]
 for policy,name in [('in_place','in-place'),('physical','moving-root')]:
  spec={'schema':'motion-audition/v1','name':f'Upright candidate / {n} poses / {name} / UNRATED','canvas':[256,256],'stage':[640,656],'origin':[96,80],'camera':'fixed','root_stride':m['frames'][-1]['physical_root'],'root_policy':policy,'cycle_ms':m['cycle_ms'],'frames':[]}
  # End root comes from excluded loop endpoint, not final rendered sample.
  spec['root_stride']=[v/m['frames'][-1]['phase']for v in m['frames'][-1]['physical_root']]
  for i,f in enumerate(m['frames']):
   assert sha(pack/f['file'])==f['sha256'];spec['frames'].append({'index':i,'file':f['file'],'sha256':f['sha256'],'duration_ms':holds[i],'phase_label':keys[min(7,int(f['phase']*8))]['name'],'physical_root':f['physical_root']})
  (pack/f'audition-{name}.json').write_text(json.dumps(spec,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('pack',type=Path);make(p.parse_args().pack.resolve())

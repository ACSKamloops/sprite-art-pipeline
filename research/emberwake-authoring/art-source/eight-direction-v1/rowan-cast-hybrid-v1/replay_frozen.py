from pathlib import Path
from PIL import Image
import argparse,json,hashlib,numpy as np
P=Path(__file__).resolve().parent
arg=argparse.ArgumentParser();arg.add_argument('--output',type=Path);args=arg.parse_args()
if args.output:
 assert not args.output.exists(),'Use a fresh replay output directory';args.output.mkdir(parents=True)
for item in json.loads((P/'input-hashes.json').read_text()):assert hashlib.sha256((P/item['file']).read_bytes()).hexdigest()==item['sha256'],item['file']
records=[]
for c in json.loads((P/'construction-spec.json').read_text())['configs']:
 v,n=c['view'],c['frame'];m=np.load(P/'maps'/f'{v}-{n:02}-source-map.npz');owner=m['source_kind'];xy=m['source_xy'];body=np.array(Image.open(P/c['body']).convert('RGBA'));under=np.array(Image.open(P/c['underpaint']).convert('RGBA'));donor=np.array(Image.open(P/c['donor']).convert('RGBA'));out=body.copy();out[owner==1]=under[owner==1];out[owner==2]=donor[xy[:,:,1][owner==2],xy[:,:,0][owner==2]];expected=np.array(Image.open(P/'candidate'/v/f'{n:02}.png').convert('RGBA'));assert np.array_equal(out,expected);assert np.array_equal(out[owner==0],body[owner==0])
 # Trace each visible donor pixel through its retained integer map into the original model-return bytes.
 role='00-cast-prep' if n!=20 else '02-cast-recovery';dm=np.load(P/'inputs/donors'/v/f'{role}-source-map.npy');raw=np.array(Image.open(P/'inputs/raw'/f'{v}-return.png').convert('RGBA'));dxy=xy[owner==2];rxy=dm[dxy[:,1],dxy[:,0]];assert (rxy>=0).all();rr=raw[rxy[:,1],rxy[:,0]].copy();rr[:,3][rr[:,3]<24]=0;rr[:,3][rr[:,3]>245]=255;rr[rr[:,3]==0,:3]=0;assert np.array_equal(rr,out[owner==2])
 if args.output:
  dest=args.output/v;dest.mkdir(exist_ok=True);Image.fromarray(out).save(dest/f'{n:02}.png')
 records.append({'view':v,'frame':n,'rgba_exact':True,'protected_body_exact':True,'all_donor_pixels_trace_to_raw_return':True})
for v in ['southeast','northeast']:
 for n in [19,22]:assert (P/'candidate'/v/f'{n:02}.png').read_bytes()==(P/'inputs/registered'/v/f'{n:02}.png').read_bytes()
report={'all_inputs_match':True,'records':records,'release19_and_neutral22_png_bytes_exact':True}
if args.output:(args.output/'replay-proof.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))

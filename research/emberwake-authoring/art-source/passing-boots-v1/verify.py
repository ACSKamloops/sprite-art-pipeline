from pathlib import Path
from PIL import Image
from collections import deque
import hashlib,json,struct,subprocess,sys,tempfile
import replay
B=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
plan=json.loads((B/'PLAN.json').read_text());inputs={c:Image.open(B/'inputs'/c/'atlas.png').convert('RGBA') for c in ['lyra','brann']}
frozen={c:im.tobytes() for c,im in inputs.items()}
for item in json.loads((B/'INPUTS.json').read_text()):assert sha((B/item['path']).read_bytes())==item['sha256']
selected,journal=replay.apply_variant(inputs,plan);records=[]
for e,j in zip(plan['entries'],journal['entries']):
 c,f=e['character'],e['target'];a=replay.cel(inputs[c],f);b=selected[c][f];actual=Image.open(B/'candidate'/c/f'passing-{f}.png').convert('RGBA');assert b.tobytes()==actual.tobytes()
 owners={(p[0],p[1]) for op in e['operations'] for p in op['points_tx_ty_sx_sy']}
 for y in range(128):
  for x in range(128):
   if a.getpixel((x,y))!=b.getpixel((x,y)):assert (x,y) in owners
 # Consumer scans final literal witnesses independently of producer's event log.
 donor=replay.cel(inputs[c],e['source'])
 for p in j['changed_pixel_witnesses']:
  assert list(b.getpixel(tuple(p['xy'])))==p['after']==list(donor.getpixel(tuple(p['source_xy'])))
 assert a.crop((0,0,128,96)).tobytes()==b.crop((0,0,128,96)).tobytes()
 base=lambda im:max(y for y in range(128) for x in range(128) if im.getpixel((x,y))[3]>0)
 assert base(a)==base(b)
 erased=[(x,y) for y in range(128) for x in range(128) if a.getpixel((x,y))[3]>0 and b.getpixel((x,y))[3]==0]
 # A topology diagnostic only, never a claim about recovered anatomy.
 outside=set();q=deque((x,y) for x in range(128) for y in [0,127] if b.getpixel((x,y))[3]==0)
 q.extend((x,y) for y in range(128) for x in [0,127] if b.getpixel((x,y))[3]==0)
 while q:
  x,y=q.popleft()
  if (x,y) in outside:continue
  outside.add((x,y))
  for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
   if 0<=xx<128 and 0<=yy<128 and (xx,yy) not in outside and b.getpixel((xx,yy))[3]==0:q.append((xx,yy))
 internal=[p for p in erased if p not in outside];assert not internal
 records.append({'character':c,'frame':f,'changed_pixels':j['changed_pixels'],'png_sha256':sha((B/'candidate'/c/f'passing-{f}.png').read_bytes()),'outside_masks_unchanged':True,'all_y_less_than_96_unchanged':True,'original_actor_sole_y':base(a),'candidate_actor_sole_y':base(b),'transparent_contour_replacements':len(erased),'new_enclosed_zero_alpha_holes':len(internal),'literal_RGBA_witnesses_verified':True})
assert all(inputs[c].tobytes()==frozen[c] for c in inputs)
assert selected['brann'][112].tobytes()==Image.open(B/'brann-south-first-sample-f112-refined.png').convert('RGBA').tobytes()
clocks=[]
for c in inputs:
 for view in ['south','north']:
  raw=(B/'candidate'/c/(view+'-AB-450ms.apng')).read_bytes();p=8;delays=[]
  while p<len(raw):
   n=struct.unpack('>I',raw[p:p+4])[0];kind=raw[p+4:p+8];data=raw[p+8:p+8+n]
   if kind==b'fcTL':delays.append(struct.unpack('>HH',data[20:24]))
   p+=n+12
  assert delays==[(9,160)]*8
  clocks.append({'character':c,'view':view,'encoded_delay_fractions':delays,'cycle_seconds':.45})
negative=[]
for source_frame,label in [(112,'target'),(121,'donor')]:
 changed={c:im.copy() for c,im in inputs.items()};im=changed['lyra'];x,y=source_frame%8*128+65,source_frame//8*128+104;old=im.getpixel((x,y));im.putpixel((x,y),(old[0]^1,*old[1:]))
 try:replay.apply_variant(changed,plan)
 except ValueError:negative.append(label+' mutation rejected')
 else:raise AssertionError('Changed source accepted')
with tempfile.TemporaryDirectory(prefix='fresh-replay-',dir=B) as tmp:
 out=Path(tmp)/'out';r=subprocess.run([sys.executable,str(B/'replay.py'),'--output',str(out)],capture_output=True,text=True,timeout=30);assert r.returncode==0,(r.stdout,r.stderr)
 for c in inputs:
  for f in [112,113,114,115]:assert (out/c/f'passing-{f}.png').read_bytes()==(B/'candidate'/c/f'passing-{f}.png').read_bytes()
report={'schema':'emberwake-passing-boot-verification/v1','all_passed':True,'source_inputs_immutable':True,'fresh_process_all8_PNGs_byte_identical':True,'outside_owned_masks_exact':True,'records':records,'clocks':clocks,'negative_cases':negative,'source_role_limit':'Manual visible boot ownership; no hidden anatomy recovered or inferred from alpha topology. Sole tests are whole-actor raster lower bounds, not world-space foot-planting or support-role proof.','quality_status':'Candidate, no worker score; visual review pending.'}
(B/'VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: eight literal-pixel repairs, unchanged soleY/cuffs/body/outside masks, exact fresh replay, four encoded450ms loops')

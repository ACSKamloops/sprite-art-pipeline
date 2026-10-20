from pathlib import Path
import json,shutil,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path('/home/astra/artifacts/emberwake-rowan-ne-knee-paint-v1');A=P/'assessment-v1';D=P/'composite-diagnostic-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def load(p):return json.loads(p.read_text())
def save(n,d):(D/n).write_text(json.dumps(d,indent=2)+'\n')
old=load(D/'DIAGNOSTIC-RECEIPT.json');save('PROPOSED-ALL3-RECEIPT.json',old)
# Keep rejected04 proposed bytes/maps and old all3 proof, but never apply it to current frames.
shutil.copy2(P/'inputs/source-frames/04.png',D/'frames/04.png')
shutil.move(str(D/'maps/04-raw-source-map.npz'),str(D/'rejected/04-raw-source-map.npz'))
for n in ['04-actual-change.png','04-frozen-cloth-owner.png']:shutil.move(str(D/'masks'/n),str(D/'rejected'/n))
for p in list((D/'proof').glob('*.png')):
 if p.name.startswith('02-03-04-05-06-')or p.name.startswith('full8-')or p.name=='joint-boundary-8x.png':shutil.move(str(p),str(p.with_name('proposed-all3-'+p.name)))
save('rejected/04-STATUS.json',{'status':'Producer self-rejected as stronger; original04 retained in current eight-frame diagnostic','proposed_png':'../proposed/04.png','proposed_sha256':sha(D/'proposed/04.png'),'source04_sha256':sha(P/'inputs/source-frames/04.png'),'reason':'Exact protected gold V over the new adjacent shadow makes the central cream neck read more pinched. No demonstrated84px gain; mechanical invariants alone do not approve this patch.','new_alpha0_hole':False,'boundary_proof':'../proof/04-hem-cuff-threeway-12x.png','raw_source_map':'04-raw-source-map.npz','model_calls':0})
# Current diagnostic proof has03/06 imports only; rejected04 remains visible separately.
for size,name in [(128,'native'),(256,'2x'),(84,'game')]:
 for ids,prefix in [([2,3,4,5,6],'02-03-04-05-06'),(list(range(8)),'full8')]:
  can=Image.new('RGB',(len(ids)*size,6*(size+18)));d=ImageDraw.Draw(can)
  for bgr,(bgname,bg)in enumerate([('light',(235,230,215)),('dark',(29,34,43)),('green',(64,111,80))]):
   for row,bank in enumerate([P/'inputs/source-frames',D/'frames']):
    y=(bgr*2+row)*(size+18);d.rectangle((0,y,can.width,y+size+18),fill=bg)
    for col,i in enumerate(ids):
     im=Image.open(bank/f'{i:02}.png').convert('RGBA').resize((size,size),Image.Resampling.NEAREST);can.paste(im,(col*size,y+18),im);d.text((col*size+2,y+2),f'{"source"if row==0 else"03/06diag"} {i:02} {bgname}',fill='black'if bgr==0 else'white')
  can.save(D/f'proof/{prefix}-{name}.png')
can=Image.new('RGBA',(4*344,2*274),(235,230,215,255));d=ImageDraw.Draw(can)
for row,bank in enumerate([P/'inputs/source-frames',D/'frames']):
 for col,i in enumerate([3,4,5,6]):
  im=Image.open(bank/f'{i:02}.png').convert('RGBA').crop((41,76,84,108)).resize((344,256),Image.Resampling.NEAREST);can.alpha_composite(im,(col*344,row*274+18));d.text((col*344+3,row*274+2),f'{"source"if row==0 else"03/06 DIAG"} {i:02}',fill='black')
can.save(D/'proof/joint-boundary-8x.png')
# Alpha connection tests distinguish a new interior cut from contour antialiasing.
connections=[]
for i in [3,4,6]:
 base=arr(P/f'inputs/source-frames/{i:02}.png');prop=arr(D/f'proposed/{i:02}.png');allowed=mask(P/f'owners/{i:02}-allowed-trouser-knee-cuff.png');boot=mask(P/f'owners/{i:02}-complete-boot-protected-region.png');upper=mask(P/f'owners/{i:02}-upper-hem-gloves.png');loss=(base[...,3]>=128)&(prop[...,3]<128)&allowed;losses=[]
 for y,x in np.argwhere(loss):
  edge=any(not(0<=x+dx<128 and 0<=y+dy<128)or base[y+dy,x+dx,3]<128 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)])
  losses.append({'xy':[int(x),int(y)],'source_alpha':int(base[y,x,3]),'proposed_alpha':int(prop[y,x,3]),'on_existing_silhouette_boundary':edge})
 assert all(p['on_existing_silhouette_boundary']for p in losses)
 assert not np.any((base[...,3]>0)&(prop[...,3]==0)&allowed)
 def comps(a):
  active=allowed&(a[...,3]>=128);seen=np.zeros((128,128),bool);out=[]
  for sy,sx in np.argwhere(active):
   if seen[sy,sx]:continue
   stack=[(int(sy),int(sx))];seen[sy,sx]=True;points=[]
   while stack:
    y,x=stack.pop();points.append((y,x))
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
     xx=x+dx;yy=y+dy
     if 0<=xx<128 and 0<=yy<128 and active[yy,xx]and not seen[yy,xx]:seen[yy,xx]=True;stack.append((yy,xx))
   contacts=[]
   for y,x in points:
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
     xx=x+dx;yy=y+dy
     if 0<=xx<128 and 0<=yy<128 and boot[yy,xx]and base[yy,xx,3]>=128:contacts.append([xx,yy])
   out.append({'pixels':len(points),'bounds':[min(x for y,x in points),min(y for y,x in points),max(x for y,x in points),max(y for y,x in points)],'touches_original_protected_boot_alpha128':bool(contacts),'boot_contact_coordinates':sorted(set(map(tuple,contacts)))})
  return out
 connections.append({'phase':i,'new_alpha0_inside_old_positive':[],'core_alpha_losses':losses,'new_interior_core_holes':False,'source_owner_components':comps(base),'proposed_owner_components':comps(prop),'interpretation':'Alpha connectivity only; visual seam/material quality judged separately.'})
 # Exact current protected boot/upper and unchanged source outside owners.
 current=arr(D/f'frames/{i:02}.png');assert np.array_equal(current[~allowed],base[~allowed]);assert np.array_equal(current[boot],base[boot]);assert np.array_equal(current[upper],base[upper])
save('ALPHA-GAP-CHECKS.json',connections)
# Exact raw-source-map reproduction; no second registration or resampling.
raw=arr(P/'generation/raw.png');replay=[]
for i in [3,6]:
 base=arr(P/f'inputs/source-frames/{i:02}.png');data=np.load(D/f'maps/{i:02}-raw-source-map.npz');xy=data['raw_source_xy'];owner=data['allowed'];out=base.copy();ys,xs=np.where(owner);out[ys,xs]=raw[xy[ys,xs,1],xy[ys,xs,0]];assert np.array_equal(out,arr(D/f'frames/{i:02}.png'));replay.append({'phase':i,'RGBA_exact_from_actual1254raw_source_xy':True,'PNG_sha256':sha(D/f'frames/{i:02}.png')})
for i in [0,1,2,4,5,7]:assert (D/f'frames/{i:02}.png').read_bytes()==(P/f'inputs/source-frames/{i:02}.png').read_bytes()
# All frozen preparation, raw assessment and original references remain unchanged.
for ledgerroot in [P,A]:
 for line in (ledgerroot/'SHA256SUMS').read_text().splitlines():expected,n=line.split('  ',1);assert sha(ledgerroot/n)==expected,n
receipt={'status':'03/06 bounded composite diagnostic pending root inspection;04 self-rejected;05 raw unimported','current_changed_phases':[3,6],'current_original_byte_exact':[0,1,2,4,5,7],'proposed_records':[{**rec,'current_candidate_applied':rec['phase']in[3,6],'disposition':'retain diagnostic for root inspection'if rec['phase']in[3,6]else'self-rejected04; current frame original'}for rec in old['records']],'alpha_connection_checks':'ALPHA-GAP-CHECKS.json','new_alpha0_positive_paint_loss':False,'all_core_alpha_losses_on_existing_silhouette_boundaries':True,'protected_upper_hem_gloves_and_complete_boot_regions_RGBA_exact':True,'source_rawmap_replay':replay,'raw1254_sha256':sha(P/'generation/raw.png'),'no_fit_or_additional_resampling':True,'raw_alpha_preserved_inside_allowed':True,'independent_art_acceptance':False,'editor_packaged':False,'new_model_calls':0}
save('DIAGNOSTIC-RECEIPT.json',receipt)
(D/'REPORT.md').write_text('''Rowan NE composite diagnostic, before editor packaging\n\nCurrent eight-cel diagnostic imports03 and06 only.00/01/02/04/05/07 are byte-exact source cels. No fit, extra resampling, alpha normalization or model call was used. All pixels outside the frozen cloth owners, including upper/hem/gloves, full boot regions and negative space, remain RGBA-exact.\n\n03 changes127RGBA pixels and06 changes158. Literal changed coordinates and raw-source maps are retained. Direct replay from the actual1254raw image matches both proposed cels. There is no positive-source→alpha0 cut. The2core-alpha losses in03 and3in06 are all on existing silhouette boundaries, not interior holes. The06raised cream cap still has a positive-alpha route into the original protected raised boot; its small exposed area remains constrained and needs visual review rather than a claim of new anatomy.\n\n04 is self-rejected as stronger: the exact restored gold V over the new adjacent shadow makes its central cream neck look more pinched, without a demonstrated84px gain. Proposed04 still passes preservation and has no new alpha0hole; those mechanics do not approve the seam. Its proposed PNG, map, all3proposal proofs and12x source/raw/composite boundary image are retained. Current04 is original.\n\n05 is unimported because of the earlier raw two-row local cuff/material shift; its raw PNG/receipt are retained and current05 is original.\n\nInspect proof/02-03-04-05-06-{native,2x,game}.png, proof/full8-{native,2x,game}.png and proof/joint-boundary-8x.png for current03/06-only art.04/06threeway12x proofs show the raw versus actual protected-boundary results. No editor package or quality/motion score is inferred.\n''')
(D/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(D)}\n'for p in sorted(D.rglob('*'))if p.is_file()and p.name!='SHA256SUMS'))
print(json.dumps({'current_changed':[3,6],'03sha':sha(D/'frames/03.png'),'06sha':sha(D/'frames/06.png'),'04':'self-rejected/current original','05':'raw unimported/current original','report':str(D/'REPORT.md'),'ledger_sha256':sha(D/'SHA256SUMS')}))

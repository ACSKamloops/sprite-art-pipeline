"""Compact complete combined replay: frozen07control/map +03literalunderpaint +editor guards."""
from pathlib import Path
import argparse,json,hashlib,shutil
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel,candidate_transaction
R=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(R/n).convert('RGBA'))
def sha(n):return hashlib.sha256(n.read_bytes()).hexdigest()
def over(dst,src):
 d=dst.astype('int64');s=src.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);out=d.copy();use=sa>0
 for k in range(3):out[:,:,k][use]=(s[:,:,k][use]*sa[use]*255+d[:,:,k][use]*da[use]*(255-sa[use])+n[use]//2)//n[use]
 out[:,:,3][use]=(n[use]+127)//255
 return out.astype(np.uint8)
def part_from_controls(source,own,c):
 src=np.array(c['source_vertices'],float);dst=np.array(c['target_vertices'],float);part=np.zeros((128,128,4),np.uint8);mp=np.full((128,128,2),-1,np.int16);owner=np.zeros((128,128),bool)
 for t in c['triangles']:
  s,d=src[t],dst[t];ds=np.linalg.det(np.stack([s[1]-s[0],s[2]-s[0]],axis=1));dd=np.linalg.det(np.stack([d[1]-d[0],d[2]-d[0]],axis=1));assert ds*dd>0;inv=np.linalg.inv(np.vstack([d.T,np.ones(3)]))
  for y in range(max(0,int(np.floor(d[:,1].min()))),min(127,int(np.ceil(d[:,1].max())))+1):
   for x in range(max(0,int(np.floor(d[:,0].min()))),min(127,int(np.ceil(d[:,0].max())))+1):
    bary=inv@np.array([x,y,1.])
    if bary.min()<-1e-8:continue
    sx,sy=np.floor(bary@s+.5).astype(int)
    if 0<=sx<128 and 0<=sy<128 and own[sy,sx]:part[y,x]=source[sy,sx];mp[y,x]=[sx,sy];owner[y,x]=True
 return part,mp,owner
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh output only';out.mkdir(parents=True)
 source=a('inputs/control/00.png');base=a('inputs/control/07.png');z=np.load(R/'maps/07-newP-source00.npz');part=np.zeros_like(base)
 for y,x in np.argwhere(z['owner']):sx,sy=z['source_xy'][y,x];part[y,x]=source[sy,sx]
 controls=json.loads((R/'RECIPE.json').read_text());own=np.array(Image.open(R/'masks/00-P-complete-visible-leg.png'))>0;rebuilt,xy,owner=part_from_controls(source,own,controls);assert np.array_equal(part,rebuilt);assert np.array_equal(xy,z['source_xy']);assert np.array_equal(owner,z['owner']);assert np.array_equal(part,a('layers/07-newP-projected-leg.png'))
 upper=np.array(Image.open(R/'masks/07-upper-protected.png'))>0;qowner=np.array(Image.open(R/'masks/07-Q-visible-preserved.png'))>0;q=np.zeros_like(base);q[qowner]=base[qowner];assert np.array_equal(q,a('layers/07-Q-preserved.png'));body=base.copy();body[~upper]=0;built07=over(over(body,q),part);built07[upper]=base[upper];assert np.array_equal(built07,a('frames/07.png'));assert np.array_equal(built07[upper],base[upper])
 front=a('inputs/control/03.png');built03=front.copy();j=json.loads((R/'03-UNDERPAINT-JOURNAL.json').read_text());assert len(j['operations'])==2;coords=[]
 for op in j['operations']:
  x,y=op['destination'];sx,sy=op['underpaint_source_xy'];under=source[sy,sx].astype(np.int64);f=front[y,x].astype(np.int64);assert f.tolist()==op['expected_front_RGBA'];assert under.tolist()==op['underpaint_RGBA'];assert under[3]==255;af=int(f[3]);result=[int((int(f[k])*af+int(under[k])*(255-af)+127)//255) for k in range(3)]+[255];assert result==op['result_RGBA'];built03[y,x]=result;coords.append([x,y])
 assert sorted(coords)==[[67,96],[68,97]];assert np.any(front!=built03,axis=-1).sum()==2;assert np.array_equal(built03[98,68],front[98,68]);assert np.array_equal(built03,a('frames/03.png'))
 initial=json.loads((R/'projects/initial.json').read_text());journal=json.loads((R/'projects/journal.json').read_text());h=History.replay(initial,journal);final=json.loads((R/'projects/final.json').read_text());assert len(journal['receipts'])==2;finalhash=project_hash(h.project);assert finalhash==project_hash(final);h.undo();h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();h.redo();assert project_hash(h.project)==finalhash
 bad=Image.fromarray(built03).copy();bad.putpixel((0,0),(1,1,1,255));guard_rejected=False
 try:candidate_transaction(h.project,'brann-se-03',bad,[[67,96],[68,97]],reason='guardprobeonly')
 except Exception:guard_rejected=True
 assert guard_rejected and project_hash(h.project)==finalhash
 (out/'editor').mkdir();rows=[]
 for i in range(8):
  if i in [3,7]:Image.fromarray(built03 if i==3 else built07).save(out/f'{i:02}.png')
  else:assert (R/'inputs/control'/f'{i:02}.png').read_bytes()==(R/'frames'/f'{i:02}.png').read_bytes();shutil.copy2(R/'inputs/control'/f'{i:02}.png',out/f'{i:02}.png')
  assert sha(out/f'{i:02}.png')==sha(R/'frames'/f'{i:02}.png');edited=render_cel(h.project,f'brann-se-{i:02}');assert edited.tobytes()==a(f'frames/{i:02}.png').tobytes();edited.save(out/'editor'/f'{i:02}.png');assert sha(out/'editor'/f'{i:02}.png')==sha(R/'frames'/f'{i:02}.png');rows.append({'phase':i,'control_map_RGBA_PNG_exact':True,'editor_RGBA_PNG_exact':True,'sha256':sha(out/f'{i:02}.png')})
 receipt={'status':'Frozen exact07plus2pixel03underpaint; changed-art review pending, no wholeloop acceptance','all8_controls_inverse_source_map_and_editor_RGBA_PNG_exact':True,'07_frozen_inspected_sha256':sha(R/'frames/07.png'),'03_only2_RGBA_coords':coords,'03_third68_98_exact':True,'unchanged6_PNG_bytes_exact':[0,1,2,4,5,6],'actual07upper_RGBA_exact':True,'newP_source00RGBA_exact':True,'Q_same07source_part_exact':True,'integer_source_over_derived_composite_alpha':True,'03explicit_darkcuff_underpaint_witnesses':True,'actual_guarded_transactions':2,'actual_undo2_redo2':True,'actual_outside_mask_guard_rejected_atomically':True,'stale_project_guard_proof':'projects/EDITOR-RECEIPT.json','model_calls':0,'hold':[9,160],'cycle':[9,20],'rows':rows};(out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

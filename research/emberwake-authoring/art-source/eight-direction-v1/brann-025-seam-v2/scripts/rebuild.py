"""Self-contained freshsource/alpha/editor replay of exactlyseven cuffslit pixels."""
from pathlib import Path
from fractions import Fraction
import argparse,json,hashlib,shutil
import numpy as np
from PIL import Image
from sprite_lab import History,project_hash,render_cel,candidate_transaction
R=Path(__file__).resolve().parents[1]
def a(n):return np.array(Image.open(R/n).convert('RGBA'))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def halfup(f):return (f.numerator*2+f.denominator)//(2*f.denominator)
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve();assert not out.exists(),'Fresh output required';out.mkdir(parents=True)
 for d in ['source-alpha','editor']:(out/d).mkdir()
 original=a('inputs/original-bank/02.5.png');source=a('inputs/original-bank/03.png');built=original.copy();j=json.loads((R/'UNDERPAINT-JOURNAL.json').read_text());z=np.load(R/'maps/seven-pixel-underpaint.npz');wantedcoords={(53,90),(54,90),(55,90),(53,91),(54,91),(55,91),(56,91)}
 assert len(j['operations'])==7;rows_alpha=[]
 for i,op in enumerate(j['operations']):
  x,y=op['destination'];sx,sy=op['underpaint_source_xy'];f=original[y,x].astype(np.int64);u=source[sy,sx].astype(np.int64);assert [x,y]==z['destination'][i].tolist();assert [sx,sy]==z['source_xy'][i].tolist();assert int(z['source_phase'][i])==3;assert f.tolist()==op['expected_front_RGBA']==z['front_RGBA'][i].tolist();assert u.tolist()==op['underpaint_source_RGBA']==z['under_RGBA'][i].tolist()
  fa,ua=int(f[3]),int(u[3]);den=fa*255+ua*(255-fa);integer=[int((int(f[k])*fa*255+int(u[k])*ua*(255-fa)+den//2)//den) for k in range(3)]+[(den+127)//255];af,au=Fraction(fa,255),Fraction(ua,255);oa=af+au*(1-af);rational=[halfup((int(f[k])*af+int(u[k])*au*(1-af))/oa) for k in range(3)]+[halfup(oa*255)];pil=list(Image.alpha_composite(Image.new('RGBA',(1,1),tuple(map(int,u))),Image.new('RGBA',(1,1),tuple(map(int,f)))).getpixel((0,0)));assert integer==rational==pil==u.tolist()==op['source_over_result_RGBA']==z['result_RGBA'][i].tolist();assert fa==0 and ua==255;built[y,x]=integer;rows_alpha.append({'destination':[x,y],'source03xy':[sx,sy],'sourceRGBA':u.tolist(),'integer_rational_Pillow_alpha_over_exact':True})
 changed=np.any(built!=original,axis=-1);assert {(int(x),int(y)) for y,x in np.argwhere(changed)}==wantedcoords;assert np.array_equal(built[~changed],original[~changed]);assert np.array_equal(built[90:98,61:68],original[90:98,61:68]);assert np.array_equal(built[90,59],original[90,59]);assert np.array_equal(built,a('candidate/02.5.png'))
 initial=json.loads((R/'projects/initial.json').read_text());journal=json.loads((R/'projects/journal.json').read_text());h=History.replay(initial,journal);assert len(journal['receipts'])==1;final=json.loads((R/'projects/final.json').read_text());finalhash=project_hash(h.project);assert finalhash==project_hash(final);h.undo();assert project_hash(h.project)==project_hash(initial);h.redo();assert project_hash(h.project)==finalhash
 coords=[op['destination'] for op in j['operations']];stale=candidate_transaction(initial,'brann-se-02.5',Image.fromarray(built),coords,reason='staleguardprobe');staleok=False
 try:h.apply(stale)
 except Exception:staleok=True
 assert staleok and project_hash(h.project)==finalhash
 bad=Image.fromarray(built);bad.putpixel((59,90),(14,14,14,255));outsideok=False
 try:candidate_transaction(h.project,'brann-se-02.5',bad,coords,reason='largerclearanceguardprobe')
 except Exception:outsideok=True
 assert outsideok and project_hash(h.project)==finalhash
 t=json.loads((R/'TIMING.json').read_text());original_t=json.loads((R/'inputs/ORIGINAL-TIMING.json').read_text());assert t==original_t;spec=json.loads((R/'ROOT-REVIEW-SPEC.json').read_text());clock=0;starts={};rows=[]
 for n,hold,f in zip(t['order'],t['hold_ticks'],spec['frames']):
  assert f=={'file':f'candidate/{n}.png','hold':[hold,320]};starts[n]=clock;clock+=hold
  if n=='02.5':Image.fromarray(built).save(out/'source-alpha'/f'{n}.png')
  else:assert (R/'candidate'/f'{n}.png').read_bytes()==(R/'inputs/original-bank'/f'{n}.png').read_bytes();shutil.copy2(R/'inputs/original-bank'/f'{n}.png',out/'source-alpha'/f'{n}.png')
  edited=render_cel(h.project,f'brann-se-{n}');assert edited.tobytes()==a(f'candidate/{n}.png').tobytes();edited.save(out/'editor'/f'{n}.png')
  for folder in ['source-alpha','editor']:assert sha(out/folder/f'{n}.png')==sha(R/'candidate'/f'{n}.png')
  rows.append({'drawing':n,'hold_ticks320':hold,'source_alpha_RGBA_PNG_exact':True,'editor_RGBA_PNG_exact':True,'sha256':sha(R/'candidate'/f'{n}.png')})
 assert clock==144 and starts['02.5']==45 and all(starts[f'{i:02}']==i*18 for i in range(8));assert sum(Fraction(*f['hold']) for f in spec['frames'])==Fraction(9,20)
 receipt={'status':'Frozen exact7pixelappearance/joinrepair; nosmoothnessgainorwhole-loopacceptanceclaimed','old_midpoint_sha256':sha(R/'inputs/original-bank/02.5.png'),'fixed_midpoint_sha256':sha(R/'candidate/02.5.png'),'changed_count':7,'changed_coordinates':coords,'all_other_midRGBA_exact':True,'larger_leg_clearance_RGBA_exact':True,'original8_PNG_bytes_exact':True,'all9_source_alpha_and_editor_RGBA_PNG_exact':True,'actual_guarded_transactions':1,'actual_undo_redo':True,'stale_project_guard_atomic':True,'outside_seven_pixel_owner_guard_atomic':True,'original9exposure_clock_exact':True,'cycle_ticks320':144,'model_calls':0,'external_artifact_dependencies':[],'alpha_source_witnesses':rows_alpha,'rows':rows};(out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

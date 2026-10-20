"""Compact saved-map replay; no canonical paths or new geometry decisions."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
def a(p):return np.array(Image.open(p).convert('RGBA'))
def mask(n):return np.array(Image.open(R/'masks'/n).convert('L'))>0
def over(s,d):
 s=s.astype('int64');d=d.astype('int64');sa=s[:,:,3];da=d[:,:,3];n=sa*255+da*(255-sa);o=np.zeros_like(s);v=n>0;o[:,:,3]=(n+127)//255
 for c in range(3):o[:,:,c][v]=(s[:,:,c][v]*sa[v]*255+d[:,:,c][v]*da[v]*(255-sa[v])+n[v]//2)//n[v]
 return o.astype('uint8')
p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args();O=Path(args.out)
if O.exists():raise SystemExit('Fresh output required')
O.mkdir(parents=True)
src=a(R/'inputs/control/05.png');d=a(R/'inputs/control/07.png');reg=a(R/'inputs/provenance/registered00.png');under=a(R/'inputs/provenance/original05-underpaint.png');mp=np.load(R/'maps/05.npz');P=np.zeros_like(src)
for y,x in np.argwhere(mask('P-complete-layer-owner.png')):sx,sy=mp['complete_P_source_xy'][y,x];P[y,x]=reg[sy,sx]
assert np.array_equal(P,a(R/'parts/complete-P-source-layer-UNCHANGED.png'));Pcomp=over(P,under);out=src.copy();remove=mask('old-Q-complete-removal-owner.png');out[remove]=0;reveal=mask('P-source-revealed-after-oldQ-removal.png');out[reveal]=Pcomp[reveal]
# The original P undercloth was retained only where the old Q removal reveals
# that exact existing layer, prior to shaded newQ cloth projection.
yy,xx=np.mgrid[:128,:128]
from PIL import ImageDraw
pm=Image.new('L',(128,128));ImageDraw.Draw(pm).polygon([(50,76),(65,76),(62,90),(50,92)],fill=255);allow=np.array(Image.open(R/'inputs/provenance/05-allowed.png').convert('L'))>0;under_reveal=remove&(np.array(pm)>0)&allow&(out[:,:,3]==0);out[under_reveal]=under[under_reveal]
assert np.array_equal(out,a(R/'parts/05-after-complete-oldQ-removal-P-reveal.png'))
for y,x in np.argwhere(mask('shaded-proximal-cloth-owner.png')):sx,sy=mp['cloth_source_xy'][y,x];out[y,x]=d[sy,sx]
assert np.array_equal(out,a(R/'parts/05-before-Q-source-over.png'))
boot=np.zeros_like(src)
for y,x in np.argwhere(mask('Q-new-complete-target-owner.png')):sx,sy=mp['new_Q_source_xy'][y,x];boot[y,x]=d[sy,sx]
assert np.array_equal(boot,a(R/'parts/source07-boot-translated-minus7-0.png'));active=boot[:,:,3]>0;out[active]=over(boot,out)[active];protected=mask('upper-sash-protected.png');out[protected]=src[protected];out[out[:,:,3]==0]=0
assert np.array_equal(out,a(R/'frames/05.png'))
checks=[]
for i in range(8):
 frame=out if i==5 else a(R/'inputs/control'/f'{i:02}.png');path=O/f'{i:02}.png';Image.fromarray(frame).save(path);target=R/'frames'/f'{i:02}.png';assert path.read_bytes()==target.read_bytes();checks.append({'phase':i,'PNG_exact':True,'RGBA_exact':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
receipt={'saved_map_replay':checks,'P_complete_layer_RGBA_exact':True,'P_current_visible_RGBA_exact_except_9_Q_occlusions':bool(np.array_equal(out[mask('P-current-visible-owner.png')&~mask('Q-over-current-visible-P-nine.png')],src[mask('P-current-visible-owner.png')&~mask('Q-over-current-visible-P-nine.png')])),'upper_sash_RGBA_exact':bool(np.array_equal(out[protected],src[protected])),'frozen06_byte_exact':(O/'06.png').read_bytes()==(R/'inputs/control/06.png').read_bytes(),'source_over':'independent exact rational integer operation','model_calls':0,'editor_package':False}
(O/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'all8_PNG_exact':True,'new05':checks[5]['sha256'],'frozen06':checks[6]['sha256']},indent=2))

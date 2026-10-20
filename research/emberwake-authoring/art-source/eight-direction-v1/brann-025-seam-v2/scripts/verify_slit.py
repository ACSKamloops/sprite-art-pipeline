"""Saved-file independent verification of onlythe7reported cuffslit pixels."""
from pathlib import Path
from fractions import Fraction
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def halfup(f):return (f.numerator*2+f.denominator)//(f.denominator*2)
a=np.array(Image.open(R/'inputs/original-bank/02.5.png').convert('RGBA'));b=np.array(Image.open(R/'candidate/02.5.png').convert('RGBA'));s=np.array(Image.open(R/'inputs/original-bank/03.png').convert('RGBA'));j=json.loads((R/'UNDERPAINT-JOURNAL.json').read_text());z=np.load(R/'maps/seven-pixel-underpaint.npz');changed=np.any(a!=b,axis=-1);expected={(53,90),(54,90),(55,90),(53,91),(54,91),(55,91),(56,91)};actual={(int(x),int(y)) for y,x in np.argwhere(changed)};assert actual==expected
rows=[]
for i,op in enumerate(j['operations']):
 x,y=op['destination'];sx,sy=op['underpaint_source_xy'];f=list(map(int,a[y,x]));u=list(map(int,s[sy,sx]));assert f==op['expected_front_RGBA']==z['front_RGBA'][i].tolist();assert u==op['underpaint_source_RGBA']==z['under_RGBA'][i].tolist();af,au=Fraction(f[3],255),Fraction(u[3],255);oa=af+au*(1-af);rgba=[halfup((f[k]*af+u[k]*au*(1-af))/oa) for k in range(3)]+[halfup(oa*255)];assert rgba==b[y,x].tolist()==op['source_over_result_RGBA']==z['result_RGBA'][i].tolist();assert rgba==u and f[3]==0;rows.append({'destination':[x,y],'source03xy':[sx,sy],'actual_sourceRGBA':u,'exact_fractional_alpha_over_result':rgba})
assert np.array_equal(a[~changed],b[~changed]);assert np.array_equal(a[90,59],b[90,59]);assert np.array_equal(a[90:98,61:68],b[90:98,61:68]);other8=[]
for n in ['00','01','02','03','04','05','06','07']:assert (R/'candidate'/f'{n}.png').read_bytes()==(R/'inputs/original-bank'/f'{n}.png').read_bytes();other8.append(n)
t=json.loads((R/'inputs/ORIGINAL-TIMING.json').read_text());assert sum(t['hold_ticks'])==144 and t['fps']==320;assert all(t['start_ticks'][f'{i:02}']==18*i for i in range(8))
original=R.parent;w=json.loads((R/'inputs/FROZEN-ORIGINAL-WITNESS.json').read_text());assert sha(original/'SHA256SUMS')==w['original_ledger_file_sha256'];entries=(original/'SHA256SUMS').read_text().splitlines();assert all(sha(original/line.split('  ',1)[1])==line.split('  ',1)[0] for line in entries)
r={'status':'Exact7pixelactualslit repair, visualinspectionpending; noartscore','new_midpoint_sha256':sha(R/'candidate/02.5.png'),'changed_count':7,'changed_coordinates':sorted([list(x) for x in actual]),'all_other_midRGBA_exact':True,'larger_leg_clearance_RGBA_exact':True,'other8_PNG_bytes_exact':other8,'original9exposure_clock_unchanged':True,'cycle_ticks320':144,'frozen_original_ledger_unchanged':True,'all_original_frozen_file_hashes_verify':True,'original_frozen_entries_verified':len(entries),'sourceRGBA_and_exact_fractional_alpha_over':rows,'editor_package_created':False,'model_calls':0};(R/'VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

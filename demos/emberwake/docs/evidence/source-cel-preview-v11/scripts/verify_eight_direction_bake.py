#!/usr/bin/env python3
"""Independent artifact invariants: exact preserved cels, clocks, mirrors, sockets.

This has no visual scoring. Run against a real bake; optionally compare an
independently rebuilt directory for deterministic byte-for-byte replay.
"""
from pathlib import Path
import argparse,json,hashlib,math
from fractions import Fraction
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
VIEWS=['south','southeast','east','northeast','north','northwest','west','southwest']
ACTION_LENGTHS={'idle':Fraction(29,25),'walk':Fraction(9,20),'attack':Fraction(41,100),'cast':Fraction(1,2),'hurt':Fraction(29,100),'dodge':Fraction(13,50)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frame(im,cols,i):return im.crop((i%cols*128,i//cols*128,i%cols*128+128,i//cols*128+128))
def main():
 p=argparse.ArgumentParser();p.add_argument('--bake',required=True,type=Path);p.add_argument('--replay',type=Path);p.add_argument('--receipt',type=Path);args=p.parse_args()
 report={'scope':'Exact artifacts/resources only; no artwork, physical contact or animation quality score.','actors':{},'checks':0}
 def check(v,n):
  report['checks']+=1
  if not v:raise AssertionError(n)
 for a in ['rowan','lyra','brann']:
  b=args.bake/a;atlas=Image.open(b/'atlas.png').convert('RGBA');m=json.loads((b/'animations.json').read_text());oldbase=ROOT/'art-source/eight-direction-v1/baseline'/a
  old=Image.open(oldbase/'atlas.png').convert('RGBA');om=json.loads((oldbase/'animations.json').read_text());count=old.width//128*(old.height//128)
  check(m['directions']==VIEWS,a+' complete direction declaration')
  check(len(m['animations'])==48 and m['columns']==atlas.width//128,a+' actual columns/48clips')
  for i in range(count):check(frame(atlas,m['columns'],i).tobytes()==frame(old,om['columns'],i).tobytes(),f'{a} oldcel{i} unchanged')
  for k,v in om['animations'].items():check(m['animations'][k]==v,a+' original clock/frame binding '+k)
  for v in VIEWS:
   for action,duration in ACTION_LENGTHS.items():
    clip=m['animations'][v+'_'+action];ids=clip['frames'];holds=clip['holds']
    check(len(ids)==len(holds) and all(h>0 for h in holds),f'{a} {v} {action} holds')
    check(sum(map(lambda h:Fraction(str(h)),holds))==duration,f'{a} {v} {action} duration')
    check(clip['loop']==(action in ['idle','walk']),f'{a} {v} {action} loop')
    for i in ids:
     check(0<=i<atlas.width//128*(atlas.height//128),f'{a} {v} {action} bound')
     check(frame(atlas,m['columns'],i).getbbox() is not None,f'{a} {v} {action} nonempty')
   release=m['animations'][v+'_cast']['frames'][3];hand=m['cast_hand'][v];cel=frame(atlas,m['columns'],release)
   check(cel.getpixel(tuple(hand))[3]>128,a+' measured painted palm '+v)
  for view,points in m.get('cast_hand_tracks',{}).items():
   check(view in VIEWS,a+' charge track view '+view)
   clip=m['animations'][view+'_cast']
   check(len(points)==len(clip['frames']),a+' ordered charge exposure count '+view)
   check(points[3]==m['cast_hand'][view],a+' charge/release socket agreement '+view)
   previous={}
   for index,point in enumerate(points):
    check(len(point)==2 and all(type(n) in (int,float) and math.isfinite(n) and 0<=n<128 for n in point),a+' charge point bounds '+view)
    cel_id=clip['frames'][index]
    check(cel_id not in previous or point==previous[cel_id],a+' duplicate cel charge point '+view)
    previous[cel_id]=point
    cel=frame(atlas,m['columns'],cel_id)
    check(cel.getpixel(tuple(round(n) for n in point))[3]>24,a+' painted charge point '+view+' '+str(index))
  for west,east in [('southwest','southeast'),('northwest','northeast')]:
   if east in m.get('cast_hand_tracks',{}):
    check(m['cast_hand_tracks'][west]==[[128-p[0],p[1]] for p in m['cast_hand_tracks'][east]],a+' reflected charge track '+west)
  for west,east in [('southwest','southeast'),('northwest','northeast')]:
   for action in ACTION_LENGTHS:
    wc=m['animations'][west+'_'+action];ec=m['animations'][east+'_'+action]
    for wi,ei in zip(wc['frames'],ec['frames']):
     mirror=Image.new('RGBA',(128,128));mirror.alpha_composite(ImageOps.mirror(frame(atlas,m['columns'],ei)),(1,0))
     check(mirror.tobytes()==frame(atlas,m['columns'],wi).tobytes(),a+' conditional mirror '+west+' '+action)
  report['actors'][a]={'atlas_sha256':sha(b/'atlas.png'),'manifest_sha256':sha(b/'animations.json'),'preserved_old_physical_cells':count,'body_clips':48,'new_diagonal_clips':24}
  if args.replay:
   for f in ['atlas.png','animations.json','lineage.json','source-ownership.json']:check(sha(b/f)==sha(args.replay/a/f),a+' deterministic replay '+f)
 if args.receipt:
  args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(report,indent=2)+'\n')
 print(f"ARTIFACT_INVARIANTS PASS: {report['checks']} checks;144clips; no art score")
if __name__=='__main__':main()

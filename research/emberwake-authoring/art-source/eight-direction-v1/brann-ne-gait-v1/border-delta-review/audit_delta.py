from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
import hashlib,json
root=Path('/home/astra/artifacts/emberwake-brann-border-delta-review-v1')
src=Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1/brann-ne-gait-v1')
ledger=json.loads((src/'BORDER-CLEANUP.json').read_text());declared={r['file']:r for r in ledger['rows']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def points(mask,a):
 return [{'xy':[int(x),int(y)],'rgba':[int(c) for c in a[y,x]]} for y,x in np.argwhere(mask)]
def mirror(a):
 b=np.zeros_like(a)
 for x in range(128):
  nx=128-x
  if 0<=nx<128:b[:,nx]=a[:,x]
 return b
rows=[];frame_arrays={k:[] for k in ['raw-ne','clean-ne','raw-nw','clean-nw']}
for i in range(8):
 fn=f'{i:02}.png';rawpath=src/'frames'/fn;cleanpath=src/'cleaned-frames'/fn
 ri=Image.open(rawpath);ci=Image.open(cleanpath)
 assert ri.mode==ci.mode=='RGBA' and ri.size==ci.size==(128,128)
 a=np.array(ri);b=np.array(ci);diff=np.any(a!=b,axis=2)
 yy,xx=np.indices((128,128));border=(yy==0)|(yy==127)|(xx==0)|(xx==127)
 literal=np.all(a==[0,0,0,1],axis=2)&border
 ds=[]
 for y,x in np.argwhere(diff):ds.append({'xy':[int(x),int(y)],'before':[int(c) for c in a[y,x]],'after':[int(c) for c in b[y,x]],'border':bool(border[y,x])})
 ma=mirror(a);mb=mirror(b);mdiff=np.any(ma!=mb,axis=2)
 for key,z in [('raw-ne',a),('clean-ne',b),('raw-nw',ma),('clean-nw',mb)]:frame_arrays[key].append(z)
 rawmirror=root/'evidence/mirrored-raw'/fn;cleanmirror=root/'evidence/mirrored-clean'/fn
 Image.fromarray(ma).save(rawmirror);Image.fromarray(mb).save(cleanmirror)
 row={'file':fn,'raw_sha256':sha(rawpath),'cleaned_sha256':sha(cleanpath),
 'raw_matches_declared_hash':sha(rawpath)==declared[fn]['source_sha256'],
 'cleaned_matches_declared_hash':sha(cleanpath)==declared[fn]['output_sha256'],
 'changed_texels':int(diff.sum()),'changes':ds,
 'raw_literal_black_alpha1_border_texels':points(literal,a),
 'changes_exactly_all_literal_black_alpha1_border':bool(np.array_equal(diff,literal)),
 'all_changed_before_black_alpha1':all(z['before']==[0,0,0,1] for z in ds),
 'all_changed_after_zero_rgba':all(z['after']==[0,0,0,0] for z in ds),
 'all_other_rgba_exact':bool(np.array_equal(a[~diff],b[~diff])),
 'nonborder_rgba_exact':bool(np.array_equal(a[~border],b[~border])),
 'raw_alpha2plus_texels':int((a[:,:,3]>=2).sum()),
 'alpha2plus_rgba_exact':bool(np.array_equal(a[a[:,:,3]>=2],b[a[:,:,3]>=2])),
 'declared_coordinate_set_matches':sorted(z['xy'] for z in ds)==sorted(e['xy'] for e in declared[fn]['edits']),
 'raw_positive_alpha_border':points(border&(a[:,:,3]>0),a),
 'cleaned_positive_alpha_border':points(border&(b[:,:,3]>0),b),
 'mirror':{'rule':'x_new=128-x_old; y_new=y_old; skip destinations outside 0..127; zero-initialize all RGBA',
 'raw_png_sha256':sha(rawmirror),'cleaned_png_sha256':sha(cleanmirror),
 'raw_decoded_rgba_sha256':hashlib.sha256(ma.tobytes()).hexdigest(),'cleaned_decoded_rgba_sha256':hashlib.sha256(mb.tobytes()).hexdigest(),
 'changed_texels':int(mdiff.sum()),'changes':[{'xy':[int(x),int(y)],'before':[int(c) for c in ma[y,x]],'after':[int(c) for c in mb[y,x]]} for y,x in np.argwhere(mdiff)],
 'raw_positive_alpha_border':points(border&(ma[:,:,3]>0),ma),
 'cleaned_positive_alpha_border':points(border&(mb[:,:,3]>0),mb),
 'removed_by_transform_from_delta':sum(z['xy'][0]==0 for z in ds),
 'cleaned_source_x1_positive_alpha':points((xx==1)&(b[:,:,3]>0),b),
 'alpha2plus_rgba_exact':bool(np.array_equal(ma[ma[:,:,3]>=2],mb[ma[:,:,3]>=2]))}}
 rows.append(row)
summary={'scope':'Raw vs cleaned NE source pixels, and independently derived NW with explicit x_new=128-x_old. No art rerating or game/runtime test.',
 'cleanup_ledger_sha256':sha(src/'BORDER-CLEANUP.json'),'source_root':str(src),
 'total_ne_changed_texels':sum(r['changed_texels'] for r in rows),
 'total_nw_changed_texels':sum(r['mirror']['changed_texels'] for r in rows),
 'total_ne_alpha2plus_texels_retained':sum(r['raw_alpha2plus_texels'] for r in rows),
 'total_ne_cleaned_positive_alpha_border_texels':sum(len(r['cleaned_positive_alpha_border']) for r in rows),
 'total_nw_cleaned_positive_alpha_border_texels':sum(len(r['mirror']['cleaned_positive_alpha_border']) for r in rows),
 'rows':rows}
(root/'DATA-AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
# Ordinary composites preserve actual alpha; no visibility amplification.
bgs={'light':(224,224,216),'dark':(28,32,40),'game':(71,82,61)}
for direct in ('ne','nw'):
 for bgn,bgc in bgs.items():
  specs=[('raw',128),('clean',128),('raw',84),('clean',84)]
  sheet=Image.new('RGB',(8*132+20,600),(246,246,246));d=ImageDraw.Draw(sheet)
  d.text((8,6),f'Brann {direct.upper()} raw/clean delta | actual alpha | light/dark/game flat review contrast | no new art rating',fill='black');y=24
  for mode,scale in specs:
   d.text((8,y),f'{mode} {direct} {scale}px, nearest',fill='black');y+=18
   for i,a in enumerate(frame_arrays[f'{mode}-{direct}']):
    im=Image.fromarray(a).resize((scale,scale),Image.Resampling.NEAREST)
    tile=Image.new('RGB',(scale,scale),bgc);tile.paste(im,(0,0),im);x=10+i*132
    sheet.paste(tile,(x,y));d.text((x+1,y+scale+2),f'{i:02}',fill='black')
   y+=scale+17
  sheet.save(root/f'evidence/{direct}-{bgn}-raw-clean.png')
# Deterministic composite delta measures for each tested background and size.
composites={}
for key in ('ne','nw'):
 composites[key]={}
 for scale in (84,128):
  composites[key][str(scale)]={}
  for bgn,bgc in bgs.items():
   rr=[]
   for i in range(8):
    vals=[]
    for mode in ('raw','clean'):
     im=Image.fromarray(frame_arrays[f'{mode}-{key}'][i]).resize((scale,scale),Image.Resampling.NEAREST)
     tile=Image.new('RGB',(scale,scale),bgc);tile.paste(im,(0,0),im);vals.append(np.array(tile).astype(int))
    delta=np.abs(vals[0]-vals[1]);rr.append({'file':f'{i:02}.png','changed_display_pixels':int(np.any(delta,axis=2).sum()),'max_abs_rgb_code_difference':int(delta.max())})
   composites[key][str(scale)][bgn]=rr
(root/'COMPOSITE-DELTA.json').write_text(json.dumps({'resampling':'nearest neighbor','backgrounds_rgb':bgs,'per_frame':composites},indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2))
for row in rows:print(row['file'],'NE delta',row['changed_texels'],'NW delta',row['mirror']['changed_texels'],'clean NW border',row['mirror']['cleaned_positive_alpha_border'])
assert summary['total_ne_changed_texels']==11
assert all(r['changes_exactly_all_literal_black_alpha1_border'] and r['all_changed_before_black_alpha1'] and r['all_changed_after_zero_rgba'] and r['all_other_rgba_exact'] and r['nonborder_rgba_exact'] and r['alpha2plus_rgba_exact'] and r['raw_matches_declared_hash'] and r['cleaned_matches_declared_hash'] and r['declared_coordinate_set_matches'] for r in rows)

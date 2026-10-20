from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import json,hashlib
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent;FINAL=PARENT/'candidate-walk-bow160-game-light-v11';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
sheet=Image.new('RGBA',(160*9,182*4),(27,33,39,255));draw=ImageDraw.Draw(sheet)
for row,view in enumerate(['front','right','back','left']):
 for i,frame in enumerate([0,10,20]):
  baseline=Image.open(ROOT/'baseline'/view/f'{i:02d}.png').convert('RGBA');edited=Image.open(ROOT/'edited'/view/f'{i:02d}.png').convert('RGBA');expected=Image.open(FINAL/view/f'{frame//2.5:02.0f}.png').convert('RGBA')
  mask=Image.open(ROOT/'feature-masks'/f'{view}-{i}.png').convert('RGB').getchannel('R').point(lambda x:255 if x>=16 else 0);expanded=mask.filter(ImageFilter.MaxFilter(5));a=list(baseline.getdata());b=list(edited.getdata());domain=list(expanded.getdata());delta=[];alpha_count=0
  for old,new in zip(a,b):
   alpha_count+=old[3]!=new[3];delta.append(max(abs(x-y)for x,y in zip(old,new))if old[3]or new[3]else 0)
  groups={}
  for threshold in [1,4,12,32]:
   locations=[(j%160,j//160)for j,d in enumerate(delta)if d>=threshold];outside=[(j%160,j//160)for j,d in enumerate(delta)if d>=threshold and not domain[j]]
   bounds=lambda q:[min(x for x,y in q),min(y for x,y in q),max(x for x,y in q)+1,max(y for x,y in q)+1]if q else None
   groups[str(threshold)]={'changed_pixels':len(locations),'bounds':bounds(locations),'outside_feature_domain_plus2px':len(outside),'outside_bounds':bounds(outside)}
  diff=Image.new('RGBA',(160,160),(0,0,0,255));diff.putdata([(min(d*8,255),0,min(d*4,255),255)for d in delta])
  for offset,im,label in [(0,baseline,'before'),(1,edited,'edited'),(2,diff,'delta×8')]:sheet.alpha_composite(im,((i*3+offset)*160,row*182));draw.text(((i*3+offset)*160+3,row*182+163),f'{view} f{frame} {label}',fill='white')
  rows.append({'view':view,'source_frame':frame,'baseline_RGBA_exact_final_v11':baseline.tobytes()==expected.tobytes(),'alpha_changed_pixels':alpha_count,'UV_feature_mask_bounds':mask.getbbox(),'maximum_visible_component_delta':max(delta),'thresholded_regions':groups})
protected=json.loads((ROOT/'protected-before.json').read_text());unchanged={f:sha(PARENT/f)==s for f,s in protected.items()};report={'schema':'nativeUV-face-fineedit-actual-render-comparison/v1','final_v11_manifest_sha256':sha(FINAL/'manifest.json'),'rows':rows,'all12_baseline_RGBA_exact_final_v11':all(r['baseline_RGBA_exact_final_v11']for r in rows),'protected_files_unchanged':all(unchanged.values()),'protected_file_checks':unchanged,'scope':'ActualRGBA color/radiusedit at12samples. UVdomainpass traces rendered mark surfaces with indirectbounces disabled; two-pixel rastermargin explicit. RemoteGI/samplechanges reported at1/4/12/32byte thresholds, never assumedzero. No fullcycle artisticapproval.'};(ROOT/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');sheet.save(ROOT/'before-after-difference.png');sheet.resize((sheet.width*2,sheet.height*2),Image.Resampling.NEAREST).save(ROOT/'before-after-difference-2x.png')
print('baseline12 exact',report['all12_baseline_RGBA_exact_final_v11'],'protected',report['protected_files_unchanged']);print([(r['view'],r['source_frame'],r['thresholded_regions']['4'])for r in rows])

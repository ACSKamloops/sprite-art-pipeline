#!/usr/bin/env python3
"""Read-only independent scalar comparison and binding audit; no root imports/network."""
import base64,hashlib,json,math
from datetime import datetime
from io import BytesIO
from pathlib import Path
from PIL import Image
BASE=Path('/home/astra/artifacts/pixellab-reducer-recovery-20261014')
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def decode(value):
 raw=base64.b64decode(value['base64'].split(',')[-1],validate=True)
 with Image.open(BytesIO(raw)) as im:
  pixels=im.convert('RGBA').tobytes()
  return raw,im.size,[tuple(pixels[i:i+4]) for i in range(0,len(pixels),4)]
def lab(color):
 linear=[]
 for byte in color[:3]:
  v=byte/255.0
  linear.append(v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4)
 r,g,b=linear
 l=math.cbrt(.4122214708*r+.5363325363*g+.0514459929*b)
 m=math.cbrt(.2119034982*r+.6806995451*g+.1073969566*b)
 s=math.cbrt(.0883024619*r+.2817188376*g+.6299787005*b)
 return (.2104542553*l+.7936177850*m-.0040720468*s,
         1.9779984951*l-2.4285922050*m+.4505937099*s,
         .0259040371*l+.7827717662*m-.8086757660*s)
def main():
 names=[(BASE,'fixed-none'),(BASE,'fixed-repeat'),(BASE,'fixed-2x2'),
        (Path(str(BASE)+'-phase2'),'six-color-none'),(Path(str(BASE)+'-phase2'),'bw-2x2-zero'),
        (Path(str(BASE)+'-phase2'),'bw-2x2-ten'),(Path(str(BASE)+'-holdout'),'weighted-holdout')]
 records=[];weight_lower=0.0;weight_upper=math.inf;calibration_colors=set()
 for root,name in names:
  run=root/name;pb=(root/'PLAN.json').read_bytes();plan=json.loads(pb)
  qb=(run/'request.json').read_bytes();q=json.loads(qb);hb=(run/'network.har').read_bytes();entries=json.loads(hb)['log']['entries']
  if len(entries)!=1:raise ValueError('Unexpected request count')
  h=entries[0];rea=load(run/'REA.json');response=load(run/'response.json');body=h['request']['postData']['text'].encode()
  if sha(qb)!=next(x['request_sha256'] for x in plan['requests'] if x['variant']==name):raise ValueError('PLAN byte pin differs')
  if json.loads(body)!=q or sha(body)!=h['_request_body_sha256']:raise ValueError('Actual request byte/semantic binding differs')
  if json.dumps(q,separators=(',',':'),ensure_ascii=False).encode()!=body:raise ValueError('Compact transport bytes differ')
  if json.loads(h['response']['content']['text'])!=response or h['response']['status']!=200:raise ValueError('Returned response differs')
  if not h['response']['content'].get('text_redacted') and sha(h['response']['content']['text'].encode())!=h['_response_body_sha256_before_scrub']:raise ValueError('Raw response byte pin differs')
  if rea['subject']['digest']['sha256']!=sha(hb) or rea['normalized_result']['records'][0]['reported']!=h:raise ValueError('REA subject/record differs')
  if rea['normalized_result']['total_records']!=1:raise ValueError('REA count differs')
  if plan['endpoint']!='https://api.pixellab.ai/v2/reduce-colors' or h['request']['method']!='POST' or h['request']['url']!=plan['endpoint']:raise ValueError('Endpoint differs')
  prepared=datetime.fromisoformat(plan['prepared_utc']);started=datetime.fromisoformat(h['startedDateTime'])
  palettebytes,_,palette=decode(q['palette_image']);plabs=[lab(c) for c in palette];cache={};gaps=[];ties=0;frames=[];sourcecolors=set()
  for i,(sourcevalue,actualvalue) in enumerate(zip(q['images'],response['images'],strict=True)):
   srcbytes,size,src=decode(sourcevalue);outbytes,outsize,actual=decode(actualvalue)
   if size!=outsize or outbytes!=(run/f'output-{i:02}.png').read_bytes():raise ValueError('Output canvas/byte binding differs')
   mismatches=alpha=hidden=unweighted=srgb=0
   for pixel,returned in zip(src,actual,strict=True):
    rgb=pixel[:3];sourcecolors.add(rgb)
    if rgb not in cache:
     x=lab(rgb);dist=[.25*(x[0]-p[0])**2+(x[1]-p[1])**2+(x[2]-p[2])**2 for p in plabs]
     order=sorted(range(len(palette)),key=lambda n:dist[n]);ties+=dist[order[0]]==dist[order[1]];gaps.append(dist[order[1]]-dist[order[0]])
     win=order[0]
     if q['dithering']=='none' or q['dithering_strength']==0:
      aw=(x[0]-plabs[win][0])**2;bw=sum((x[j]-plabs[win][j])**2 for j in (1,2))
      for n,p in enumerate(plabs):
       if n==win:continue
       coefficient=aw-(x[0]-p[0])**2
       rhs=sum((x[j]-p[j])**2 for j in (1,2))-bw
       if coefficient>0:weight_upper=min(weight_upper,rhs/coefficient)
       elif coefficient<0:weight_lower=max(weight_lower,rhs/coefficient)
     uw=min(range(len(palette)),key=lambda n:sum((x[j]-plabs[n][j])**2 for j in range(3)))
     sw=min(range(len(palette)),key=lambda n:sum((rgb[j]-palette[n][j])**2 for j in range(3)))
     cache[rgb]=(palette[win][:3],palette[uw][:3],palette[sw][:3])
    predicted,uw,sw=cache[rgb];bad=predicted+(pixel[3],)!=returned
    mismatches+=bad;alpha+=pixel[3]!=returned[3];hidden+=bool(bad and pixel[3]==0)
    unweighted+=uw!=returned[:3];srgb+=sw!=returned[:3]
   frames.append({'index':i,'size':size,'rgba_entries':len(src),'source_png_sha256':sha(srcbytes),'output_png_sha256':sha(outbytes),'weighted_rgba_mismatches':mismatches,'alpha_mismatches':alpha,'hidden_alpha0_rgba_mismatches':hidden,'unweighted_oklab_rgb_mismatches':unweighted,'srgb_rgb_mismatches':srgb,'distinct_rgb_colors':len({p[:3] for p in src}),'alpha_values':sorted({p[3] for p in src})})
  if name=='weighted-holdout':
   if q['images'][0]['base64']!= 'data:image/png;base64,'+base64.b64encode((root/'inputs/rgb-holdout.png').read_bytes()).decode():raise ValueError('Heldout saved input differs')
   if q['images'][1]['base64']!= 'data:image/png;base64,'+base64.b64encode((root/'inputs/rgba-holdout.png').read_bytes()).decode():raise ValueError('Heldout saved alpha input differs')
   if palettebytes!=(root/'inputs/holdout-palette.png').read_bytes():raise ValueError('Heldout saved palette differs')
   overlap=len(sourcecolors&calibration_colors)
  else:
   calibration_colors.update(sourcecolors);overlap=None
  records.append({'case':name,'returned_usage':response.get('usage'),'response_text_redacted':h['response']['content'].get('text_redacted'),'heldout_distinct_rgb_overlap_with_calibration':overlap,'plan_sha256':sha(pb),'request_file_sha256':sha(qb),'transport_body_sha256':sha(body),'request_file_equals_transport_bytes':qb==body,'transport_bytes_equal_compact_serialization':True,'har_sha256':sha(hb),'rea_sha256':sha((run/'REA.json').read_bytes()),'rea_id':rea['evidence_id'],'rea_authority':rea['authority'],'plan_prepared_utc':plan['prepared_utc'],'har_started_utc':h['startedDateTime'],'plan_lead_seconds':(started-prepared).total_seconds(),'predeclared_prediction':plan.get('predeclared_prediction'),'palette_png_sha256':sha(palettebytes),'palette_colors':len(palette),'palette_alpha_values':sorted({p[3] for p in palette}),'dithering':q['dithering'],'strength':q['dithering_strength'],'nondithered_or_zero_strength':q['dithering']=='none' or q['dithering_strength']==0,'distinct_rgb_colors_across_frames':len(sourcecolors),'exact_distance_ties':ties,'min_top_two_distance_gap':min(gaps),'frames':frames})
 nond=[r for r in records if r['nondithered_or_zero_strength']]
 result={'version':1,'implementation':'Independent Python scalar sRGB transfer, explicit Oklab dot products, weighted nearest palette; no root implementation imported','script_sha256':sha(Path(__file__).read_bytes()),'cases':records,'matching_nondithered_rgba_entries_including_repeats':sum(f['rgba_entries'] for r in nond for f in r['frames']),'matching_nondithered_rgba_mismatches':sum(f['weighted_rgba_mismatches'] for r in nond for f in r['frames']),'timestamp_authority':'Self-recorded local PLAN and Python HAR timestamps, not independent external chronology attestation','scalar_L_weight_interval_compatible_with_all_nondithered_winners':[weight_lower,weight_upper],'parameter_interval_boundary_ties_unresolved':True,'private_source_recovered':False,'whole_pipeline_certified':False,'retained_post_records':len(records),'reported_generation_usage_total':sum(r['returned_usage']['generations'] for r in records),'calls':0,'credentials_loaded':False,'reviewed_root_scripts':[{'path':str(q),'sha256':sha(q.read_bytes())} for q in [Path('/home/astra/projects/pixellab-local-workbench/scripts/replay_pixellab_fixed_palette.py'),Path('/home/astra/projects/pixellab-local-workbench/scripts/analyze_reducer_recovery.py'),Path('/home/astra/projects/pixellab-local-workbench/scripts/probe_pixellab_color_reducer.py')]]}
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()

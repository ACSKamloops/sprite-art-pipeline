"""Independent raw-observation episode peak-to-peak reduction; no renderer inference."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
here=Path(__file__).parent
report=json.loads((here/'report.json').read_text())
summary={'schema':'copper-scout-contact-summary/v1','source_sha256':report['source_sha256'],'renderer':report['renderer'],'threshold_px':.5,'criterion':'Per physical stance episode, actual opaque sole xmin peak-to-peak <=0.5px; no missing sole or below-ground opaque pixels. Also records xmax and sole-center ranges.','runner_sha256':hashlib.sha256((here/'runner-at-capture.gd').read_bytes()).hexdigest(),'raw_report_sha256':hashlib.sha256((here/'report.json').read_bytes()).hexdigest(),'routes':[],'artistic_approval':False}
for route in report['routes']:
    metrics={}
    for mode in report['modes']:
        episodes={}
        for row in route['samples']:
            if not row['contact']:continue
            obs=row['measured'][mode]
            episodes.setdefault(row['stance_segment'],[]).append(obs)
        spans=[]
        for segment, observations in episodes.items():
            valid=[o for o in observations if o['xmin']is not None]
            lo=[o['xmin'] for o in valid];hi=[o['xmax']for o in valid]
            mid=[(o['xmin']+o['xmax'])/2 for o in valid]
            spans.append({'stance_segment':segment,'samples':len(observations),'missing_sole_samples':len(observations)-len(valid),'below_ground_pixels':sum(o['below_ground_pixels']for o in observations),'xmin_range':[min(lo),max(lo)]if lo else None,'xmax_range':[min(hi),max(hi)]if hi else None,'center_range':[min(mid),max(mid)]if mid else None,'peak_to_peak_px':max(lo)-min(lo)if lo else None})
        maximum=max(s['peak_to_peak_px'] or 0 for s in spans)
        metrics[mode]={'episodes':spans,'max_peak_to_peak_px':maximum,'passes_0_5px_gate':maximum<=.5 and all(not s['missing_sole_samples']and not s['below_ground_pixels']for s in spans)}
    targets={}
    for row in route['samples']:
        if row['contact']:targets.setdefault(row['stance_segment'],[]).append(row['analytic_target_world_x'])
    summary['routes'].append({'clip':route['clip'],'side':route['side'],'samples':route['sample_count'],'metrics':metrics,'max_analytic_target_stance_range_px':max(max(v)-min(v)for v in targets.values()),'max_ik_target_error_px':max(r['ik_target_error_px']for r in route['samples'])})
(here/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
# Contact diagnostics from saved actual GPU surfaces, no pixel repairs.
for clip in ['walk','run']:
    pngs=sorted(here.glob(clip+'_front_sample*.png'))
    strip=Image.new('RGBA',(1280,212*len(pngs)),(28,34,42,255));draw=ImageDraw.Draw(strip)
    for y,path in enumerate(pngs):
        raw=Image.open(path)
        for lane,mode in enumerate(report['modes']):
            strip.alpha_composite(raw.crop((lane*512+48,0,lane*512+304,192)),(lane*256,y*212+20))
            draw.text((lane*256+3,y*212+3),mode+' '+path.stem.split('sample')[-1],fill='white')
    strip.save(here/(clip+'-loop-contact-strip.png'))
print(json.dumps({r['clip']+'_'+r['side']:{m:v['max_peak_to_peak_px']for m,v in r['metrics'].items()}for r in summary['routes']},indent=2))

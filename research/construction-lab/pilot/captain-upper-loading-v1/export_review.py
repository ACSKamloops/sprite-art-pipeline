from pathlib import Path
import json,sys,importlib.util,argparse
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('frozen_motion',P/'source/export_motion_frozen.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();a.output.mkdir(parents=True);m=h.Motion(a.spec)
vs=[h.export_variant(m,a.output,z,1,mask,3,17)for z in [1,2]for mask in [False,True]]
r={'schema':'motion-audition-export/v1','spec_sha256':h.sha(a.spec),'source_sha256':[f['sha256']for f in m.frames],'code_sha256':h.sha(__file__),'frozen_harness_sha256':h.sha(P/'source/export_motion_frozen.py'),'cycle_ms':m.cycle,'source_holds_ms':[f['duration_ms']for f in m.frames],'variants':vs,'art_verdict':'NOT_REVIEWED','limits':['Three actual exported loops,1ms endpoint packet; no biomechanical/art approval.']};(a.output/'report.json').write_text(json.dumps(r,indent=2)+'\n');print({'variants':len(vs),'clipping':[v['clipped_sample_count']for v in vs]})

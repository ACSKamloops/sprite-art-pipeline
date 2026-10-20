"""Independent bounded JSONL/admission/registration controls; synthetic mechanics only."""
from pathlib import Path
import hashlib
import json
import os
import select
import subprocess
import sys
import time

import numpy as np

from sprite_workbench.core import Store, save_sequence
from sprite_workbench.replication import compare_sequences

REPO = Path(__file__).resolve().parents[1]


def cli(args, **kwargs):
    env = dict(os.environ, PYTHONPATH=str(REPO))
    return subprocess.run([sys.executable, '-m', 'sprite_workbench', *args], cwd=REPO,
                          env=env, capture_output=True, text=True, timeout=15, **kwargs)


def channel_batch(tmp_path, lines):
    return cli(['--workspace', str(tmp_path/'store'), 'channel', '--base-dir', str(tmp_path),
                '--result-ref', 'source.sequence'], input=''.join(json.dumps(x)+'\n' if not isinstance(x,str) else x+'\n' for x in lines))


def replies(process):
    return [json.loads(line) for line in process.stdout.splitlines()]


def test_channel_huge_timeout_rejects_without_losing_followup_ping(tmp_path):
    result=channel_batch(tmp_path,[{'id':1,'method':'local.jobs.wait','params':{'job_id':'absent','timeout':10**400}},
                                  {'id':2,'method':'system.ping'}])
    assert result.returncode==0,result.stderr[-1200:]
    received=replies(result)
    assert received[1]['id']==1 and received[1]['status']=='validation_error'
    assert received[2]=={'id':2,'status':'completed','result':{'alive':True}}
    (tmp_path/'RECOVERY-RECEIPT.json').write_text(json.dumps({'exit':result.returncode,'responses':received,'scope':'Huge timeout rejected, next actual JSONL ping preserved'},indent=2)+'\n')


def test_channel_bad_shapes_unknown_methods_and_negative_pipeline_remain_live(tmp_path):
    plan={'version':1,'steps':[{'id':'bad','action':'publish','head':'accepted','artifact':'0'*64}]}
    requests=['not JSON',{'id':False,'method':'system.ping'}, {'id':1,'method':'system.ping','params':[]},
              {'id':2,'method':'public:POST:/generate-image-v2'}, {'id':3,'method':'local.unknown'},
              {'id':4,'method':'local.jobs.submit','params':{'handler':'local.pipeline','request':{'plan':plan},'head':'accepted'}},
              {'id':5,'method':'system.ping'}, {'id':6,'method':'system.shutdown'}]
    result=channel_batch(tmp_path,requests);assert result.returncode==0,result.stderr
    received=replies(result)
    assert [x['status'] for x in received[1:6]]==['validation_error']*4+['unsupported']
    assert received[6]['status']=='completed' # admission envelope, not completed job
    assert received[7]['result']=={'alive':True}
    job=received[6]['result']
    from sprite_workbench.jobs import JobManager
    from sprite_workbench.pipeline import register_pipeline_job
    with JobManager(Store(tmp_path/'store')) as manager:
        # A shutdown can preserve an unclaimed queued job. Re-register its real
        # handler and wait explicitly; admission is not a completion barrier.
        register_pipeline_job(manager,base_dir=tmp_path,result_ref='source.sequence')
        terminal=manager.wait(job,timeout=5)
    assert terminal['status']=='validation_error'
    assert Store(tmp_path/'store').get_head('accepted') is None


def test_channel_oversized_line_is_drained_without_consuming_next_request(tmp_path):
    oversized={'id':1,'method':'system.ping','params':{'padding':'x'*(4*1024*1024)}}
    result=channel_batch(tmp_path,[oversized,{'id':2,'method':'system.ping'}])
    assert result.returncode==0,result.stderr
    got=replies(result)
    assert len(got)==3 and got[1]['id'] is None and got[1]['status']=='validation_error'
    assert got[2]['id']==2 and got[2]['result']=={'alive':True}


def test_channel_library_actual_suffix_and_review_rejection(tmp_path):
    store=Store(tmp_path/'store');raster=store.put_raster(np.array([[[17,31,43,255]]],dtype=np.uint8))
    # Record/reload actual candidate through the channel, then reject promotion.
    from sprite_workbench.library import Library
    candidate=Library(store).create_candidate(raster,source_id='frame_10')
    result=channel_batch(tmp_path,[{'id':1,'method':'local.library.select','params':{'candidate_ids':[candidate],'source_ids':['frame_10']}},
                                  {'id':2,'method':'local.library.record_review','params':{'candidate_id':candidate,'visual_status':'rejected'}},
                                  {'id':3,'method':'system.capabilities'}])
    assert result.returncode==0,result.stderr
    got=replies(result);assert got[1]['result']==[candidate]
    assert got[2]['status']=='completed',got[2]
    rejected=got[2]['result']
    second=channel_batch(tmp_path,[{'id':4,'method':'local.library.promote','params':{'candidate_ids':[rejected],'name':'must-not-publish'}}])
    assert replies(second)[1]['status']=='validation_error'
    assert Library(Store(tmp_path/'store')).list()==[]
    assert {'local.library.select','local.library.record_review','local.library.remove_direction'} <= {v['id'] for v in got[3]['result']}


HELD_HOST=r'''
import sys,time
from pathlib import Path
from sprite_workbench.core import Store,ValidationError
from sprite_workbench import channel
base=Path(sys.argv[1])
def register(manager,**kwargs):
 def held(request,context):
  (base/'started').write_text('started')
  deadline=time.monotonic()+8
  while not (base/'release').exists():
   if time.monotonic()>deadline:raise ValidationError('Controlled barrier timed out')
   time.sleep(.005)
  return context.store.put_json(request) # intentionally ignores cancel, tests late quarantine
 manager.register('local.pipeline',held)
channel.register_pipeline_job=register
channel.serve(Store(base/'store'),base_dir=base,result_ref='fixture.artifact')
'''


def test_actual_jsonl_controlled_host_wait_cancel_late_quarantine_and_retry(tmp_path):
    # The channel+manager are shipped code; only trusted handler registration is
    # a deliberately held local fixture. This does not test pipeline rendering.
    process=subprocess.Popen([sys.executable,'-c',HELD_HOST,str(tmp_path)],cwd=REPO,
                             env=dict(os.environ,PYTHONPATH=str(REPO)),stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    def receive():
        raw=b'';deadline=time.monotonic()+10
        while not raw.endswith(b'\n'):
            assert time.monotonic()<deadline,'JSONL response deadline'
            assert select.select([process.stdout],[],[],max(0,deadline-time.monotonic()))[0]
            part=os.read(process.stdout.fileno(),1);assert part,'Unexpected child EOF'
            raw+=part
        return json.loads(raw)
    def send(i,method,params=None):
        process.stdin.write((json.dumps({'id':i,'method':method,'params':params or {}})+'\n').encode());process.stdin.flush()
        result=receive();assert result['id']==i
        return result
    try:
        assert receive()['event']=='ready'
        job=send(1,'local.jobs.submit',{'handler':'local.pipeline','request':{'value':7},'head':'accepted'})['result']
        deadline=time.monotonic()+5
        while not (tmp_path/'started').exists():
            assert time.monotonic()<deadline;time.sleep(.005)
        timed=send(2,'local.jobs.wait',{'job_id':job,'timeout':0})
        assert timed['status']=='timeout' # valid elapsed wait is not malformed input or terminal success
        assert send(3,'system.ping')['result']=={'alive':True}
        assert send(4,'local.jobs.cancel',{'job_id':job})['result'] is True
        (tmp_path/'release').write_text('release')
        terminal=send(5,'local.jobs.wait',{'job_id':job,'timeout':3})['result']
        assert terminal['status']=='cancelled' and terminal['outputs'][0]['disposition']=='quarantined'
        assert Store(tmp_path/'store').get_head('accepted') is None
        retry=send(6,'local.jobs.retry',{'job_id':job})['result']
        assert send(7,'local.jobs.retry',{'job_id':job})['result']==retry
        done=send(8,'local.jobs.wait',{'job_id':retry,'timeout':3})['result']
        assert done['status']=='completed' and done['outputs'][0]['disposition']=='published'
        assert Store(tmp_path/'store').get_json(done['artifact'])=={'value':7}
        (tmp_path/'CHANNEL-RECEIPT.json').write_text(json.dumps({'timed_wait':timed,'cancelled':terminal,'retry_completed':done,'scope':'Actual JSONL/JobManager with a controlled trusted handler, not pipeline rendering/art'},indent=2)+'\n')
        assert send(9,'system.shutdown')['result']['closing'] is True
        process.communicate(timeout=10);assert process.returncode==0
    finally:
        (tmp_path/'release').touch()
        if process.poll() is None:process.kill();process.communicate(timeout=5)


def test_verify_nonobject_manifest_returns_json_validation_error(tmp_path):
    directory=tmp_path/'bad';directory.mkdir();(directory/'MANIFEST.json').write_text('[]')
    result=cli(['lab','verify-run',str(directory)])
    assert result.returncode==2,result.stderr
    assert json.loads(result.stdout)['status']=='validation_error'
    assert (directory/'MANIFEST.json').read_text()=='[]'


def test_verify_traversal_never_reads_or_changes_external_file(tmp_path):
    directory=tmp_path/'bad';directory.mkdir();outside=tmp_path/'sentinel';outside.write_bytes(b'unchanged')
    (directory/'MANIFEST.json').write_text(json.dumps({'kind':'local-run-file-manifest','version':1,
      'files':[{'file':'../sentinel','bytes':9,'sha256':hashlib.sha256(b'unchanged').hexdigest()}]}))
    result=cli(['lab','verify-run',str(directory)])
    assert result.returncode==2 and json.loads(result.stdout)['status']=='validation_error'
    assert outside.read_bytes()==b'unchanged'


def test_comparison_unsupported_clock_has_no_dead_review_links(tmp_path):
    store=Store(tmp_path/'store');a=np.array([[[17,31,43,255]]],dtype=np.uint8)
    sequence=save_sequence(store,[a],durations=[[1,10**400]])
    out=tmp_path/'comparison';report=compare_sequences(store.path,sequence,store.path,sequence,out)
    assert report['status']=='completed' and report['exact_sequence_match']
    import re
    links=re.findall(r'href="([^"]+)"',(out/'index.html').read_text())
    assert all((out/link).is_file() for link in links),'Unsupported previews must not be advertised as available'
    assert (out/'baseline/frames/frame-0000.png').is_file()
    assert 'unsupported' in json.dumps(report),'Comparison receipt must retain format-specific limitations'


def test_comparison_independent_registration_hidden_visible_palette_clock_goldens(tmp_path):
    store=Store(tmp_path/'store');a=np.array([[[11,23,37,0],[41,59,73,255],[83,97,101,127]]],dtype=np.uint8)
    b=a.copy();b[0,0,0]=12;b[0,1,1]=60;b[0,2,3]=255
    left=save_sequence(store,[a],durations=[[1,8]],pivots=[[1,2]],directions=['south'])
    right=save_sequence(store,[b,b],durations=[[3,20],[1,10]],pivots=[[2,1],[2,1]],directions=['east','east'],play_count=2)
    result=compare_sequences(store.path,left,store.path,right,tmp_path/'comparison')
    assert result['exact_sequence_match'] is False
    row=result['frames'][0]
    assert (row['rgba_changed_pixels'],row['alpha_changed_pixels'],row['both_visible_rgb_changed_pixels'],row['both_hidden_rgb_changed_pixels'])==(3,1,1,1)
    assert row['visible_rgba_palette']=={'baseline_count':2,'candidate_count':2,'equal':False}
    assert row['duration_equal'] is row['pivot_equal'] is row['direction_equal'] is False
    assert result['frames'][1]['baseline_present'] is False
    assert result['registration_policy']=='Original ordered full canvases; no alignment, resampling or coalescing'
    assert result['artistic_acceptance']=='unreviewed'
    (tmp_path/'REGISTRATION-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')

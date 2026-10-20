"""F04/F05/F11 local supplied-art/state flows; no provider/model/art calls."""
from fractions import Fraction
import json
from pathlib import Path
import select
import subprocess
import sys
import threading

import numpy as np
import pytest

from sprite_workbench.core import Store, ValidationError, UnsupportedCapability, save_sequence, load_sequence
from sprite_workbench.jobs import JobManager, JobResult
from sprite_workbench.library import Library, StaleRevision
from sprite_workbench.capabilities import CapabilityRegistry


def raster(value):
    a=np.zeros((3,5,4),dtype=np.uint8)
    a[0,0]=[value,7,9,255];a[1,2]=[13,value,29,127];a[2,4]=[81,23,value,0]
    return a


def test_f04_supplied_direction_state_animation_reload_delete_restore(tmp_path):
    store=Store(tmp_path);library=Library(store)
    refs={direction:library.create_candidate(store.put_raster(raster(v)),source_id='reference_'+direction)
          for direction,v in [('south',31),('east',71)]}
    entity=library.promote(list(refs.values()),name='supplied-character',entity_kind='character',directions=refs)
    initial=library.get(entity)
    for direction,reference in initial['document']['directions'].items():
        np.testing.assert_array_equal(store.get_raster(reference['artifact_id']),raster(31 if direction=='south' else 71))
    revision=library.set_state(entity,'outfit',directions={'south':refs['south']},expected=initial['revision_id'])
    with JobManager(store,workers=2) as jobs:
        # This handler only wraps supplied arrays; it does not infer missing art.
        def supplied(req,ctx):
            frames=[ctx.store.get_raster(id) for id in req['frames']]
            ctx.progress(.5,{'phase':'loaded_supplied_frames'})
            return save_sequence(ctx.store,frames,durations=req['durations'],directions=[req['direction']]*len(frames),metadata={'lineage':'supplied'})
        jobs.register('supplied.sequence',supplied)
        sequence_ids={}
        for direction,values,durations in [('south',[31,41],[[1,10],[1,5]]),('east',[71,71,81],[[1,12],[1,6],[1,4]])]:
            request={'frames':[store.put_raster(raster(v)) for v in values],'durations':durations,'direction':direction}
            job=jobs.wait(jobs.submit('supplied.sequence',request))
            assert job['status']=='completed' and job['result_status']=='candidate'
            candidate=library.create_candidate(job['artifact'],source_id='walk_'+direction,technical_status='verified')
            revision=library.set_animation(entity,'outfit','walk',{direction:candidate},expected=revision)
            sequence_ids[direction]=job['artifact']
    reloaded=Library(Store(tmp_path)).get(entity)
    group=reloaded['document']['states']['outfit']['animations']['walk']['directions']
    assert set(group)=={'south','east'}
    for direction,id in sequence_ids.items():
        assert group[direction]['artifact_id']==id
        doc,arrays=load_sequence(store,id)
        assert [f['index'] for f in doc['frames']]==list(range(len(arrays)))
        assert [f['direction'] for f in doc['frames']]==[direction]*len(arrays)
        assert doc['visual_approval']=='unreviewed'
    east_doc,east=load_sequence(store,sequence_ids['east'])
    assert east_doc['frames'][0]['raster']==east_doc['frames'][1]['raster']
    assert [Fraction(*f['duration']) for f in east_doc['frames']]==[Fraction(1,12),Fraction(1,6),Fraction(1,4)]
    revision=library.remove_animation(entity,'outfit','walk',direction='south',expected=revision)
    assert set(library.get(entity)['document']['states']['outfit']['animations']['walk']['directions'])=={'east'}
    revision=library.remove_state(entity,'outfit',expected=revision)
    assert library.get(entity)['document']['states']=={}
    assert set(library.get(entity)['document']['directions'])=={'south','east'}
    retained=revision;tombstone=library.delete(entity,expected=revision)
    assert Library(Store(tmp_path)).list()==[]
    with pytest.raises(ValidationError):library.get(entity)
    assert store.get_json(sequence_ids['east'])==east_doc
    library.restore(entity,retained,expected=tombstone)
    assert library.get(entity)['revision_id']==retained


def test_f05_explicit_suffix_selection_promotion_missing_direction_and_stale_guard(tmp_path):
    store=Store(tmp_path);lib=Library(store)
    candidates=[lib.create_candidate(store.put_raster(raster(v)),source_id=source)
                for source,v in [('frame_10',10),('frame_2',2),('frame_1',1)]]
    selected=lib.select(candidates,['frame_2','frame_10'])
    assert selected==[candidates[1],candidates[0]]
    entity=lib.promote(selected,name='selected',directions={'south':selected[0]},metadata={'selection':'explicit source suffixes'})
    current=lib.get(entity)
    assert [r['source_id'] for r in current['document']['candidates']]==['frame_2','frame_10']
    assert set(current['document']['directions'])=={'south'}
    old=current['revision_id']
    revision=lib.set_direction(entity,'east',selected[1],expected=old)
    with pytest.raises(StaleRevision):lib.set_direction(entity,'north',candidates[2],expected=old)
    assert lib.get(entity)['revision_id']==revision
    assert 'north' not in lib.get(entity)['document']['directions']
    revision=lib.set_state(entity,'damaged',directions={'east':selected[1]},expected=revision)
    assert set(lib.get(entity)['document']['states']['damaged']['directions'])=={'east'}
    archived=lib.archive(entity,expected=revision)
    assert lib.list()==[] and lib.list(include_archived=True)[0]['revision_id']==archived
    failed=lib.create_candidate(store.put_raster(raster(91)),source_id='frame_91',status='technical_failure')
    rejected=lib.record_review(candidates[2],visual_status='rejected')
    for bad in [failed,rejected,2]:
        with pytest.raises(ValidationError):lib.promote([bad],name='must not promote')
    assert len(lib.list(include_archived=True))==1


def test_f11_immutable_request_concurrency_bound_queued_cancel_and_admission(tmp_path):
    store=Store(tmp_path);release=threading.Event();started=threading.Event();lock=threading.Lock()
    active=0;peak=0;entered=0;observed=[]
    def handler(req,ctx):
        nonlocal active,peak,entered
        with lock:
            active+=1;entered+=1;peak=max(peak,active)
            if entered==2:started.set()
        assert release.wait(5)
        observed.append(req['nested']['value'])
        req['nested']['value']=-1
        with lock:active-=1
        return ctx.store.put_json({'kind':'diagnostic','value':req['id']})
    with JobManager(store,workers=2,max_pending=3) as jobs:
        jobs.register('bounded',handler)
        request={'id':1,'nested':{'value':7}}
        first=jobs.submit('bounded',request);request['nested']['value']=99
        second=jobs.submit('bounded',{'id':2,'nested':{'value':8}})
        assert started.wait(5)
        queued=jobs.submit('bounded',{'id':3,'nested':{'value':9}})
        with pytest.raises(ValidationError):jobs.submit('bounded',{'id':4})
        assert jobs.cancel(queued) and jobs.wait(queued)['status']=='cancelled'
        release.set()
        assert jobs.wait(first)['status']==jobs.wait(second)['status']=='completed'
        assert peak==2 and entered==2 and sorted(observed)==[7,8]
        assert jobs.request(first)['nested']['value']==7
        assert len(jobs.list())==3
        with pytest.raises(ValidationError):jobs.submit('bounded',{'api_key':'never accepted'})


def test_f11_new_result_publishes_old_completion_stale_and_cancel_quarantines(tmp_path):
    store=Store(tmp_path);old_release=threading.Event();old_started=threading.Event()
    cancel_release=threading.Event();cancel_started=threading.Event()
    def handler(req,ctx):
        if req['id']=='old':old_started.set();assert old_release.wait(5)
        if req['id']=='cancel':cancel_started.set();assert cancel_release.wait(5)
        return JobResult(ctx.store.put_json(req))
    with JobManager(store,workers=2) as jobs:
        jobs.register('delayed',handler)
        old=jobs.submit('delayed',{'id':'old'},head='accepted')
        assert old_started.wait(5)
        new=jobs.wait(jobs.submit('delayed',{'id':'new'},head='accepted'))
        old_release.set();late=jobs.wait(old)
        assert late['status']=='stale' and late['outputs'][0]['disposition']=='quarantined'
        assert store.get_head('accepted')==new['artifact']
        cancel=jobs.submit('delayed',{'id':'cancel'},head='other')
        assert cancel_started.wait(5);assert jobs.cancel(cancel)
        cancel_release.set();cancelled=jobs.wait(cancel)
        assert cancelled['status']=='cancelled' and cancelled['outputs'][0]['disposition']=='quarantined'
        assert store.get_head('other') is None
        assert store.get_json(cancelled['artifact'])=={'id':'cancel'}
        assert not jobs.cancel(new['id'])


@pytest.mark.parametrize('classification',['technical_failure','validation_error','visually_rejected'])
def test_f11_downloadable_failed_or_visually_rejected_output_never_promoted(tmp_path,classification):
    store=Store(tmp_path)
    with JobManager(store,workers=1) as jobs:
        jobs.register('reject',lambda req,ctx:JobResult(ctx.store.put_json({'diagnostic':True}),classification))
        job=jobs.wait(jobs.submit('reject',{},head='blocked'))
        assert job['result_status']==classification
        assert job['status']==('completed' if classification=='visually_rejected' else classification)
        assert job['outputs'][0]['disposition']=='quarantined'
        assert store.get_head('blocked') is None


def test_f11_retry_callback_error_and_manager_exclusivity(tmp_path):
    store=Store(tmp_path);attempts=[];progress=[]
    def handler(req,ctx):
        attempts.append(req)
        if len(attempts)==1:raise RuntimeError('controlled failure')
        ctx.progress(.5,{'phase':'working'})
        return ctx.store.put_json({'ok':True})
    def callback(event):progress.append(event);raise RuntimeError('advisory callback')
    with JobManager(store,workers=1) as jobs:
        with pytest.raises(ValidationError):JobManager(store)
        jobs.register('retry',handler)
        first=jobs.wait(jobs.submit('retry',{'source':3},head='result'))
        assert first['status']=='technical_failure'
        second=jobs.wait(jobs.retry(first['id'],on_progress=callback))
        assert second['status']=='completed' and second['attempt']==2 and second['retry_of']==first['id']
        assert second['request_id']==first['request_id']
        assert jobs.retry(first['id'])==second['id']  # Same parent retry is idempotent, even after completion.
        assert len(jobs.list())==2
        assert progress[0]['fraction']==.5
        assert any(e['event']=='callback_error' for e in jobs.events(second['id']))
        with pytest.raises(ValidationError):jobs.retry(second['id'])


def test_f11_actual_process_restart_accounting_and_queued_resume(tmp_path):
    script='''
import json,sys,threading
from sprite_workbench.core import Store
from sprite_workbench.jobs import JobManager
store=Store(sys.argv[1]);jobs=JobManager(store,workers=1)
started=threading.Event();block=threading.Event()
def h(request,ctx):started.set();block.wait();return ctx.store.put_json(request)
jobs.register('resume',h)
running=jobs.submit('resume',{'phase':'abandoned'})
assert started.wait(5)
queued=jobs.submit('resume',{'phase':'queued'})
print(json.dumps({'running':running,'queued':queued}),flush=True)
block.wait()
'''
    process=subprocess.Popen([sys.executable,'-c',script,str(tmp_path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        assert select.select([process.stdout],[],[],5)[0], 'child did not persist jobs'
        line=process.stdout.readline()
        assert line,process.stderr.read()
        ids=json.loads(line)
    finally:
        process.terminate();process.communicate(timeout=5)
    store=Store(tmp_path)
    with JobManager(store,workers=1) as jobs:
        assert jobs.get(ids['running'])['status']=='interrupted'
        assert jobs.get(ids['running'])['attempt']==1
        assert jobs.get(ids['queued'])['status']=='queued'
        jobs.register('resume',lambda req,ctx:ctx.store.put_json(req))
        queued=jobs.wait(ids['queued'])
        assert store.get_json(queued['artifact'])=={'phase':'queued'}
        retried=jobs.wait(jobs.retry(ids['running']))
        assert retried['attempt']==2 and retried['retry_of']==ids['running']
        assert store.get_json(retried['artifact'])=={'phase':'abandoned'}
        assert len(jobs.list())==3


def test_f11_close_timeout_does_not_let_old_worker_publish_after_restart(tmp_path):
    store=Store(tmp_path);entered=threading.Event();release=threading.Event()
    def old(req,ctx):
        entered.set();assert release.wait(5)
        return ctx.store.put_json({'late':True})
    manager=JobManager(store,workers=1);manager.register('old',old)
    ident=manager.submit('old',{},head='must-not-publish');assert entered.wait(5)
    manager.close(wait=False)
    with JobManager(store,workers=1) as restarted:
        assert restarted.get(ident)['status']=='interrupted'
        release.set()
        manager._threads[0].join(5)
        assert not manager._threads[0].is_alive()
        job=restarted.get(ident)
        assert job['status']=='interrupted' and job['outputs'][0]['disposition']=='quarantined'
        assert store.get_head('must-not-publish') is None


def test_f11_exact_registry_offline_validation_and_local_services(tmp_path):
    registry=CapabilityRegistry();public=json.loads(Path('contracts/PUBLIC-OPERATION-CONTRACTS.json').read_text())
    mcp=json.loads(Path('contracts/MCP-TOOL-CONTRACTS.json').read_text())
    assert len(registry.list('public'))==111 and len(registry.list('mcp'))==101
    for operation in public['operations']:
        record=registry.describe(operation['id'])
        assert record['requestBody']==operation['requestBody'] and record['responses']==operation['responses']
        assert record['parameters']==operation['parameters'] and not record['handler_implemented']
    for tool in mcp['tools']:
        assert registry.describe(tool['id'])['exact_input_schema']==tool['inputSchema']
    valid={'description':'diagnostic','image_size':{'width':64,'height':64}}
    assert registry.validate_request('public:POST:/generate-image-v2',valid)
    assert 'seed' not in valid  # Validation does not invent/apply schema defaults.
    with pytest.raises(ValidationError):registry.validate_request('mcp:create_image_pro_flash',{'description':'x','width':63})
    with pytest.raises(UnsupportedCapability):registry.invoke('public:POST:/generate-image-v2',valid)
    with pytest.raises(UnsupportedCapability):registry.invoke('mcp:create_image_pro_flash',{'description':'x'})
    store=Store(tmp_path);lib=Library(store)
    registry.bind_library(lib)
    with JobManager(store,workers=1) as jobs:
        jobs.register('local',lambda req,ctx:ctx.store.put_json(req));registry.bind_jobs(jobs)
        id=registry.invoke('local.jobs.submit',{'handler':'local','request':{'x':1}})
        assert registry.invoke('local.jobs.wait',{'job_id':id})['status']=='completed'
        candidate=registry.invoke('local.library.create_candidate',{'artifact_id':store.put_raster(raster(3)),'source_id':'supplied'})
        entity=registry.invoke('local.library.promote',{'candidate_ids':[candidate],'name':'local-only'})
        assert registry.invoke('local.library.get',{'entity_id':entity})['document']['candidates'][0]['source_id']=='supplied'
        assert registry.describe('local.library.promote')['vendor_equivalence'] is False


def test_f11_external_schema_ref_cannot_trigger_network():
    registry=CapabilityRegistry()
    registry.register_local('local.external-schema',lambda req:req,request_schema={'$ref':'https://example.invalid/schema'})
    with pytest.raises(UnsupportedCapability):registry.invoke('local.external-schema',{})


def test_f04_bad_clock_and_wrong_optional_types_do_not_mutate_library(tmp_path):
    store=Store(tmp_path);lib=Library(store)
    seq=save_sequence(store,[raster(1)])
    broken=store.get_json(seq);broken['frames'][0]['duration']=[1,0]
    with pytest.raises(ValidationError):lib.create_candidate(store.put_json(broken))
    candidate=lib.create_candidate(store.put_raster(raster(1)))
    entity=lib.promote([candidate],name='guarded');old=lib.get(entity)['revision_id']
    with pytest.raises(ValidationError):lib.set_state(entity,'bad',directions=[],expected=old)
    assert lib.get(entity)['revision_id']==old
    registry=CapabilityRegistry();registry.bind_library(lib)
    with pytest.raises(ValidationError):registry.invoke('local.library.list',[])

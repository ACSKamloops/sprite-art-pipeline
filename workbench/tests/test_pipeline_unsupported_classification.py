"""Unavailable learned operations stay unavailable through real durable jobs."""
import numpy as np
from sprite_workbench.core import Store,save_sequence
from sprite_workbench.jobs import JobManager
from sprite_workbench.pipeline import register_pipeline_job


def test_nested_unsupported_plan_retains_failed_run_and_never_publishes(tmp_path):
    store=Store(tmp_path);sequence=save_sequence(store,[np.zeros((1,1,4),np.uint8)])
    plan={'version':1,'steps':[{'id':'learned','action':'prepare','sequence':sequence,
                              'options':{'capability':'unzoom'}}]}
    with JobManager(store,workers=1) as jobs:
        register_pipeline_job(jobs,base_dir=tmp_path)
        result=jobs.wait(jobs.submit('local.pipeline',{'plan':plan},head='accepted'))
    assert result['status']=='unsupported' and result['result_status']=='unsupported'
    assert store.get_head('accepted') is None
    assert result['outputs'][0]['disposition']=='quarantined'
    run=store.get_json(result['artifact'])
    assert run['status']=='failed' and run['failed_step']=='learned'
    assert run['error']['status']=='unsupported' and run['error']['capability']=='unzoom'

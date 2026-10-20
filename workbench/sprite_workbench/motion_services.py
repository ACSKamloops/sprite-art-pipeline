"""One schema for Motion Lab's local, CLI, JSONL and plan operations."""
from pathlib import Path
import threading

from .construction_services import ID,TEXT,schema
from .core import ValidationError

SIZE={'type':'array','items':{'type':'integer','minimum':1,'maximum':2048},'minItems':2,'maxItems':2}
HOLDS={'type':'array','minItems':1,'maxItems':512,'items':{'type':'array','items':{'type':'integer','minimum':1,'maximum':9007199254740991},'minItems':2,'maxItems':2}}
ROLES={'type':'array','minItems':1,'maxItems':512,'items':{'type':'string','minLength':1,'maxLength':128}}
BACKGROUND={'oneOf':[
    schema({'method':{'const':'keep'}},['method']),
    schema({'method':{'const':'recovered-host-selection'},
            'seed':{'type':'array','items':{'type':'integer','minimum':0,'maximum':511},'minItems':2,'maxItems':2},
            'tolerance':{'type':'number','minimum':0,'maximum':1}},['method','seed','tolerance'])]}
PALETTE={'oneOf':[schema({'method':{'const':'keep'}},['method']),
    schema({'method':{'const':'calibrated-fixed'},'reference_raster':ID},['method','reference_raster'])]}
SCHEMAS={
    'catalog':schema({},[]),
    'load_example':schema({'id':{'enum':['native-walk','native-slash','native-slash-margin']}},['id']),
    'decode':schema({'media':ID,'native_video':ID,'download_receipt':ID},['media']),
    'sample':schema({'extraction':ID,'indices':{'type':'array','minItems':1,'maxItems':512,'items':{'type':'integer','minimum':0,'maximum':511}},
        'holds':HOLDS,'roles':ROLES,'loop':{'type':'boolean'}},['extraction','indices','holds','roles','loop']),
    'condition':schema({'sequence':ID,'output_size':SIZE,'background':BACKGROUND,'palette':PALETTE},['sequence','output_size','background','palette']),
    'retime':schema({'sequence':ID,'holds':HOLDS,'roles':ROLES,'loop':{'type':'boolean'}},['sequence','holds','roles','loop']),
    'prepare':schema({'first_png':ID,'last_png':ID,'prompt':{'type':'string','minLength':1,'maxLength':7000},
        'duration':{'type':'integer','minimum':4,'maximum':15},'resolution':{'enum':['768P','2K']}},['first_png','prompt']),
    'submit':schema({'packet':ID},['packet']),
    'poll':schema({'packet':ID},['packet']),
    'status':schema({'packet':ID},['packet']),
    'download':schema({'packet':ID},['packet']),
}


def bind_motion(registry,store,*,base_dir=None,live_provider_enabled=False):
    from . import motion_workflow as core
    from .motion_frames import sample_frames
    slots=threading.BoundedSemaphore(2)
    def bounded(fn,request):
        if not slots.acquire(blocking=False):
            raise ValidationError('Two local motion operations are already active; wait for completion before retrying')
        try:return fn(**request)
        finally:slots.release()
    handlers={
        'catalog':lambda r:core.catalog(store,live_provider_enabled=live_provider_enabled),
        'load_example':lambda r:bounded(lambda **q:core.load_example(store,q['id']),r),
        'decode':lambda r:bounded(lambda **q:core.decode(store,**q),r),
        'sample':lambda r:sample_frames(store,**r),
        'condition':lambda r:bounded(lambda **q:core.condition(store,**q),r),
        'retime':lambda r:core.retime(store,**r),
        'prepare':lambda r:core.prepare(store,base_dir=base_dir or '.',**r),
    }
    for method in ('submit','poll','status','download'):
        handlers[method]=lambda r,m=method:core.provider_action(store,m,r['packet'],base_dir=base_dir or '.',enabled=live_provider_enabled)
    for method,handler in handlers.items():
        registry.register_local('local.motion.'+method,handler,classification='supplied-art',
            request_schema=SCHEMAS[method],evidence={'implementation':'sprite_workbench.motion_workflow',
                'ownership':core.BOUNDARY,'provider_calls_enabled':live_provider_enabled})


def invoke_motion(store,method,request,*,base_dir=None,live_provider_enabled=False):
    from .capabilities import CapabilityRegistry
    if method not in SCHEMAS:raise ValidationError('Unknown local motion method')
    registry=CapabilityRegistry()
    bind_motion(registry,store,base_dir=base_dir,live_provider_enabled=live_provider_enabled)
    return registry.invoke('local.motion.'+method,request)

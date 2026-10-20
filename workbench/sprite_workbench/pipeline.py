"""One declarative local workspace pipeline joining actual shared services."""
from pathlib import Path
import json
import re
from fractions import Fraction

import numpy as np

from .core import ValidationError,UnsupportedCapability,canonical_json,load_sequence,save_sequence

SUPPORTED = {'import','prepare','edit','scene','tracks','effects','compose','export','review','pose','terrain','ui','font','text','visemes','candidate','promote','publish','construction','pixellab_vfx','studio','selection','motion','parity'}
PRIMARY_EXPORTS = ['png','sheet','manifest','apng','editable','godot','review']


def execute_plan(store,plan,*,base_dir=None,checkpoint=None,path_validator=None):
    plan=json.loads(canonical_json({'plan':plan}))['plan']
    if not isinstance(plan,dict) or type(plan.get('version'))!=int or plan['version']!=1 or set(plan)-{'version','name','steps'}:
        raise ValidationError('Plan must use local-v1name/steps schema')
    steps=plan.get('steps')
    if not isinstance(steps,list) or not 1<=len(steps)<=128:
        raise ValidationError('Plan needs1..128steps')
    names=set()
    for step in steps:
        if not isinstance(step,dict) or not isinstance(step.get('id'),str) or not re.fullmatch('[A-Za-z][A-Za-z0-9_-]{0,63}',step['id']) or step['id'] in names:
            raise ValidationError('Step IDs must be unique bounded names')
        if step.get('action') not in SUPPORTED:
            raise UnsupportedCapability(str(step.get('action')),'Only declared local services are executable; learned/vendor actions have no implicit fallback')
        names.add(step['id'])
    frozen=store.put_json({'kind':'pipeline-plan','version':1,'plan':plan})
    results={};receipts=[];base=Path(base_dir or '.').resolve();sequence_owners={}
    def input_sequences(value):
        if isinstance(value,str):return sequence_owners.get(value,set())
        if isinstance(value,dict):return set().union(*(input_sequences(v) for v in value.values()))
        if isinstance(value,(list,tuple)):
            return set().union(*(input_sequences(v) for v in value))
        return set()
    def resolve(value):
        if isinstance(value,dict) and set(value)=={'ref'}:
            if not isinstance(value['ref'],str) or not value['ref']:
                raise ValidationError('Step reference must be nonempty text')
            parts=value['ref'].split('.')
            try:
                found=results[parts[0]]
                for key in parts[1:]:found=found[int(key)] if isinstance(found,list) else found[key]
            except (KeyError,IndexError,ValueError,TypeError) as e:raise ValidationError('Unknown prior step reference') from e
            return json.loads(canonical_json({'value':found}))['value']
        if isinstance(value,dict):return {k:resolve(v) for k,v in value.items()}
        if isinstance(value,list):return [resolve(v) for v in value]
        return value
    def path(value):
        p=Path(value);return p if p.is_absolute() else base/p
    for step_index,step in enumerate(steps):
        if checkpoint:checkpoint(step_index/len(steps),{'step':step['id'],'action':step['action']})
        action=step['action']
        try:
            args=resolve({k:v for k,v in step.items() if k not in ('id','action')})
            if path_validator:
                path_validator(args)
            allowed={
                'import':{'path'},'prepare':{'sequence','rasters','adapter','options'},'edit':{'sequence','changes'},
                'scene':{'scene'},'tracks':{'scene','tracks','frame_count','fps','direction','pivot'},
                'effects':{'recipe','subject','images'},'compose':{'body','back','front','duration','loop'},
                'export':{'sequence','directory','formats','allow_unsupported_formats'},'review':{'sequence','directory'},
                'pose':{'joints','direction_degrees','tilt_degrees','profile'},'terrain':{'cells','layout'},
                'ui':{'pieces','canvas'},'font':{'path','characters','size','columns','mode','timeout'},'text':{'atlas','text','canvas','baseline','fallback'},
                'visemes':{'text','visemes','letter_map','durations','fallback','direction'},
                'candidate':{'artifact','source_id'},'promote':{'candidates','name','entity_kind','directions'},
                'publish':{'head','artifact','expected'},'construction':{'method','request'},
                'studio':{'method','request'},'selection':{'method','request'},
                'motion':{'method','request'},
                'parity':{'method','request'},
                'pixellab_vfx':{'recipe','values','subject','images','timeout'}}
            if set(args)-allowed[action]:raise ValidationError('Unsupported local step arguments; protection must not be silently ignored')
            if action=='import':
                from .acquisition import import_image
                out=import_image(store,path(args['path']))
            elif action=='parity':
                from .parity_services import invoke_parity
                out=invoke_parity(store,args['method'],args['request'],base_dir=base)
            elif action=='motion':
                from .motion_services import invoke_motion
                out=invoke_motion(store,args['method'],args['request'],base_dir=base,live_provider_enabled=False)
            elif action in ('studio','selection'):
                from .studio_services import invoke_studio
                from .selection_services import invoke_selection
                invoke=invoke_studio if action=='studio' else invoke_selection
                out=invoke(store,args['method'],args['request'],base_dir=base)
            elif action=='construction':
                from .construction_services import invoke_construction
                out=invoke_construction(store,args['method'],args['request'],base_dir=base)
            elif action=='pixellab_vfx':
                from .source_workflow import invoke_source_vfx
                out=invoke_source_vfx(store,'render',args)
            elif action=='prepare':
                from .prepare import prepare_request
                options=dict(args.get('options',{}));options['store']=store
                original=None
                if args.get('sequence'):
                    original,arrays=load_sequence(store,args['sequence'])
                else:arrays=[store.get_raster(i) for i in args['rasters']]
                for field in ('references','mask'):
                    if field in options:
                        options[field]=[store.get_raster(i) for i in options[field]] if field=='references' else store.get_raster(options[field])
                prepared=prepare_request(args.get('adapter','local-rgba-v1'),arrays,options)
                out={k:prepared[k] for k in ('adapter','raster_ids','reference_ids','mask_id','audit_id','geometry','operations')}
                if all(a.shape==prepared['arrays'][0].shape for a in prepared['arrays']):
                    pivots=[]
                    for i,g in enumerate(prepared['geometry']):
                        p=original['frames'][i]['pivot'] if original else [0,0]
                        scale=options.get('output_size',g['pre_resize_size'])
                        pivots.append([(p[j]-g['origin'][j])*scale[j]/g['pre_resize_size'][j]+g['pad_offset'][j] for j in range(2)])
                    out['sequence']=save_sequence(store,prepared['arrays'],durations=[Fraction(*f['duration']) for f in original['frames']] if original else None,
                        pivots=pivots,loop=original['loop'] if original else False,
                        play_count=original.get('play_count') if original else None,
                        directions=[f['direction'] for f in original['frames']] if original else None,
                        metadata={'preparation':prepared['audit_id'],'parent':args.get('sequence'),'pivot_transform':'local-pixel-corner-affine'})
                else:out['sequence']=None
            elif action=='edit':
                from .raster import edit_sequence
                out=edit_sequence(store,args['sequence'],args['changes'])
            elif action=='scene':
                from .scene import render_scene
                out={'sequence':render_scene(store,args['scene'])}
            elif action=='tracks':
                from .tracks import bake_tracks
                from .scene import render_scene
                scene,audit=bake_tracks(args['scene'],args['tracks'],frame_count=args['frame_count'],fps=args['fps'],
                    direction=args.get('direction','unspecified'),pivot=args.get('pivot',[0,0]))
                audit_id=store.put_json({'kind':'track-bake',**audit})
                scene['metadata']={**scene.get('metadata',{}),'track_audit':audit_id}
                rendered=render_scene(store,scene);doc=store.get_json(rendered)
                doc['metadata']={**doc['metadata'],'track_audit':audit_id}
                out={'sequence':store.put_json(doc),'track_audit':audit_id}
            elif action=='effects':
                from .effects import render_effect
                out=render_effect(store,args['recipe'],subject=args.get('subject'),images=args.get('images'))
            elif action=='compose':
                from .composition import compose_sequences
                out=compose_sequences(store,args['body'],back=args.get('back'),front=args.get('front'),duration=args.get('duration'),loop=args.get('loop',False))
            elif action in ('export','review'):
                if action=='export':
                    from .export import export_sequence
                    if type(args.get('allow_unsupported_formats',False))!=bool:
                        raise ValidationError('allow_unsupported_formats must be an explicit JSON boolean')
                    out=export_sequence(store,args['sequence'],path(args['directory']),args.get('formats',PRIMARY_EXPORTS))
                    missing={k:v for k,v in out['formats'].items() if v.get('status')=='unsupported'}
                    if missing and not args.get('allow_unsupported_formats',False):
                        receipts.append({'step':step['id'],'action':action,'partial_result':out})
                        raise ValidationError('Requested export format unsupported; exact candidate files retained in export report')
                else:
                    from .review import review_sequence
                    out=review_sequence(store,args['sequence'],path(args['directory']))
            elif action=='pose':
                from .pose import project_pose
                projected=project_pose(args['joints'],args.get('direction_degrees',0),args.get('tilt_degrees',30),args.get('profile','godot-raw-v1'))
                out={'pose':projected,'artifact':store.put_json({'kind':'pose','profile':args.get('profile','godot-raw-v1'),'joints':projected})}
            elif action=='terrain':
                from .terrain import save_terrain
                terrain=save_terrain(store,{int(k):store.get_raster(v) for k,v in args['cells'].items()},args['layout'])
                out={'terrain':terrain,'sequence':store.get_json(terrain)['sequence']}
            elif action in ('ui','font','text','visemes'):
                from . import assets
                if action=='ui':out={'sequence':assets.render_ui(store,args['pieces'],args['canvas'])}
                elif action=='font':
                    font_path=path(args['path'])
                    if font_path.stat().st_size>32*1024*1024:raise ValidationError('Local font input exceeds32MiB')
                    raw_font=font_path.read_bytes()
                    glyphs,font_info=assets.rasterize_font(raw_font,args['characters'],size=args.get('size',16),
                                                          mode=args.get('mode','pillow'),timeout=args.get('timeout',10))
                    atlas=assets.build_glyph_atlas(store,glyphs,columns=args.get('columns',16))
                    atlas_document=store.get_json(atlas)
                    atlas_document['font_source']={'bytes':store.put_bytes(raw_font),'rasterization':font_info}
                    out={'atlas':store.put_json(atlas_document), 'font_info':font_info}
                elif action=='text':out={'sequence':assets.render_text(store,args['atlas'],args['text'],args['canvas'],baseline=args.get('baseline',[0,0]),fallback=args.get('fallback'))}
                else:out={'sequence':assets.save_viseme_timeline(store,args['text'],{k:store.get_raster(v) for k,v in args['visemes'].items()},args['letter_map'],[Fraction(*v) for v in args['durations']],fallback=args.get('fallback'),direction=args.get('direction','unspecified'))}
            elif action in ('candidate','promote'):
                from .library import Library
                library=Library(store)
                if action=='candidate':out={'candidate':library.create_candidate(args['artifact'],source_id=args.get('source_id'))}
                else:out={'entity':library.promote(args['candidates'],name=args['name'],entity_kind=args.get('entity_kind','object'),directions=args.get('directions'))}
            elif action=='publish':
                out={'published':store.set_head(args['head'],args['artifact'],args.get('expected')),'artifact':args['artifact']}
                if not out['published']:
                    raise ValidationError('Stale publication guard; candidate retained without changing head')
            # Retain the owning acquisition/preparation sequences when a later
            # step consumes their raw raster IDs (e.g. a supplied-part scene).
            dependencies=sorted(input_sequences(args))
            # Studio signs the exact sequence in verification/export receipts.
            # The pipeline-run retains plan provenance without rewriting that identity.
            produced=[out['sequence']] if action not in ('studio','motion') and isinstance(out.get('sequence'),str) else []
            produced.extend(out.get('streams',{}).values())
            replacement={}
            for sequence in dict.fromkeys(produced):
                document=store.get_json(sequence)
                document['metadata']={**document['metadata'],'pipeline_plan':frozen,
                                      'pipeline_source_sequences':dependencies}
                replacement[sequence]=store.put_json(document)
                owner=replacement[sequence]
                sequence_owners[owner]={owner}
                for frame in document['frames']:
                    sequence_owners.setdefault(frame['raster'],set()).add(owner)
            if produced:
                out['sequence']=replacement[out['sequence']]
                if 'streams' in out:out['streams']={k:replacement[v] for k,v in out['streams'].items()}
                for field in ('revision','terrain'):
                    if out.get(field):
                        container=store.get_json(out[field])
                        if container.get('sequence') in replacement:
                            container['sequence']=replacement[container['sequence']]
                            out[field]=store.put_json(container)
            results[step['id']]=out
            receipts.append({'step':step['id'],'action':action,'result':out})
        except (ValidationError,KeyError,TypeError,ValueError,OSError) as e:
            failure=e.to_dict() if isinstance(e,ValidationError) else {'status':'validation_error','reason':'Invalid/missing local step argument','exception_type':type(e).__name__}
            run=store.put_json({'kind':'pipeline-run','version':1,'plan':frozen,'status':'failed','steps':receipts,'failed_step':step['id'],'error':failure})
            return {'run':run,'status':'failed','error':failure,'failed_step':step['id'],'results':results}
    run=store.put_json({'kind':'pipeline-run','version':1,'plan':frozen,'status':'completed','steps':receipts,'visual_approval':'unreviewed'})
    return {'run':run,'status':'completed','results':results,'visual_approval':'unreviewed'}


def register_pipeline_job(manager, *, name='local.pipeline', base_dir=None, result_ref=None,
                          path_validator=None, before_run=None):
    """Register a trusted candidate-only plan runner with guarded job publication.

    Directory and result selection are host configuration, not request fields.
    Library promotion and direct head publication must run after the job; neither
    is allowed to bypass the manager's cancellation/stale completion guard.
    """
    from .jobs import JobResult
    def handler(request,context):
        if before_run:
            before_run()
        if set(request)!={'plan'} or not isinstance(request['plan'],dict):
            raise ValidationError('Pipeline job accepts one declared plan object')
        steps=request['plan'].get('steps',[])
        if not isinstance(steps,list) or any(isinstance(s,dict) and s.get('action') in ('publish','promote') for s in steps):
            raise ValidationError('Pipeline jobs produce candidates; publish/promote only after guarded completion')
        def checkpoint(fraction,detail):
            if before_run:
                before_run()
            context.check_cancel();context.progress(fraction,detail)
        run=execute_plan(context.store,request['plan'],base_dir=base_dir,checkpoint=checkpoint,path_validator=path_validator)
        if run['status']!='completed':
            classification='unsupported' if run['error']['status']=='unsupported' else 'validation_error'
            return JobResult(run['run'],classification,{'run':run['run'],'error':run['error']})
        context.check_cancel()
        if before_run:
            before_run()
        if result_ref:
            try:
                parts=result_ref.split('.');artifact=run['results'][parts[0]]
                for field in parts[1:]:artifact=artifact[field]
            except (KeyError,TypeError) as e:
                raise ValidationError('Trusted job result reference is unavailable') from e
        else:
            artifact=next((r['sequence'] for r in reversed(list(run['results'].values())) if r.get('sequence')),run['run'])
        return JobResult(artifact,'candidate',{'run':run['run'],'visual_approval':'unreviewed'})
    manager.register(name,handler)

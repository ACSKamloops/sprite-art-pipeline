"""Local CLI: immutable import/edit/plan/inspection; no implicit provider calls."""
import argparse
import json
from pathlib import Path
import re
from .core import Store,ValidationError,canonical_json,load_sequence


def read_json(path):
    p=Path(path)
    if p.stat().st_size>4*1024*1024:raise ValidationError('InputJSON exceeds4MiB')
    try:value=json.loads(p.read_text())
    except (ValueError,UnicodeDecodeError) as e:raise ValidationError('Input is not validJSON') from e
    canonical_json(value)
    return value


def sequence_id(store,value):
    ident=value if re.fullmatch('[0-9a-f]{64}',value) else store.get_head(value)
    if ident is None:raise ValidationError('Unknown head/artifact')
    doc=store.get_json(ident)
    if doc.get('kind')=='revision':ident=doc['sequence']
    return ident


def main(argv=None):
    parser=argparse.ArgumentParser(description='Evidence-bound local sprite workbench')
    parser.add_argument('--workspace',default='workspaces/default')
    sub=parser.add_subparsers(dest='command',required=True)
    imp=sub.add_parser('import');imp.add_argument('path')
    ins=sub.add_parser('inspect');ins.add_argument('artifact')
    edit=sub.add_parser('edit');edit.add_argument('sequence');edit.add_argument('changes')
    plan=sub.add_parser('run');plan.add_argument('plan')
    exp=sub.add_parser('export');exp.add_argument('sequence');exp.add_argument('directory');exp.add_argument('--formats',default='png,sheet,manifest,apng,editable,godot,review')
    rev=sub.add_parser('review');rev.add_argument('sequence');rev.add_argument('directory')
    contracts=sub.add_parser('capabilities');contracts.add_argument('--id');contracts.add_argument('--domain')
    admission=sub.add_parser('validate-source-request',help='Offline frozen-schema and source-semantic admission; no provider call')
    admission.add_argument('id');admission.add_argument('request',help='JSON request file')
    from .construction_services import SCHEMAS
    construct=sub.add_parser('construct',help='Immutable layered/indexed editing and native editor exchange')
    construct.add_argument('method',choices=sorted(SCHEMAS));construct.add_argument('request',help='JSON request file; paths resolve beside this file')
    source=sub.add_parser('pixellab-vfx',help='Execute unchanged recovered PixelLab browser functions')
    source.add_argument('method',choices=['describe','validate','controls','render','observed_catalog','observed_default','render_observed'])
    source.add_argument('request',help='JSON request file; renderer inputs are Store artifact IDs')
    from .model_handoff import SCHEMAS as MODEL_SCHEMAS
    models=sub.add_parser('models',help='Prepare non-executing model handoffs and audit imported raw results')
    models.add_argument('method',choices=sorted(MODEL_SCHEMAS))
    models.add_argument('request',help='JSON request file; no provider or agent is launched')
    from .selection_services import SCHEMAS as SELECTION_SCHEMAS
    from .studio_services import SCHEMAS as STUDIO_SCHEMAS
    from .motion_services import SCHEMAS as MOTION_SCHEMAS
    from .parity_services import SCHEMAS as PARITY_SCHEMAS
    for name, methods in [('selection', SELECTION_SCHEMAS), ('studio', STUDIO_SCHEMAS), ('motion', MOTION_SCHEMAS), ('parity', PARITY_SCHEMAS)]:
        p=sub.add_parser(name,help='Local sprite selection and verified supplied-art workflows')
        p.add_argument('method',choices=sorted(methods))
        p.add_argument('request',help='JSON request file; paths resolve beside this file')
        if name=='motion':p.add_argument('--enable-motion-provider',action='store_true',help='Allow explicit native MiniMax calls using the configured credential')
    c=sub.add_parser('crop');c.add_argument('raster');c.add_argument('region',type=lambda s:[int(v) for v in s.split(',')]);c.add_argument('--node',default='composite')
    paste=sub.add_parser('paste');paste.add_argument('packet');paste.add_argument('rows');paste.add_argument('--expect',required=True);paste.add_argument('--stamp',action='store_true')
    channel=sub.add_parser('channel',help='Persistent local JSON Lines jobs/library channel')
    channel.add_argument('--base-dir',required=True);channel.add_argument('--result-ref',required=True)
    channel.add_argument('--workers',type=int,default=2)
    channel.add_argument('--enable-motion-provider',action='store_true')
    web=sub.add_parser('web',help='Local browser controls and source-bound readiness gates')
    web.add_argument('--base-dir',required=True);web.add_argument('--port',type=int,default=8874)
    web.add_argument('--workers',type=int,default=2)
    web.add_argument('--enable-motion-provider',action='store_true')
    lab=sub.add_parser('lab',help='Local replication and evidence tools')
    labsub=lab.add_subparsers(dest='lab_command',required=True)
    labsub.add_parser('doctor');labsub.add_parser('catalog')
    replay=labsub.add_parser('replay');replay.add_argument('--flow',action='append');replay.add_argument('--output',required=True)
    verify=labsub.add_parser('verify-run');verify.add_argument('directory')
    compare=labsub.add_parser('compare');compare.add_argument('--baseline-store',required=True)
    compare.add_argument('--baseline',required=True);compare.add_argument('--candidate-store',required=True)
    compare.add_argument('--candidate',required=True);compare.add_argument('--output',required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='lab':
            from .replication import doctor,catalog,replay,verify_run,compare_sequences
            if args.lab_command=='doctor':result=doctor()
            elif args.lab_command=='catalog':result=catalog()
            elif args.lab_command=='replay':result=replay(args.output,args.flow)
            elif args.lab_command=='verify-run':result=verify_run(args.directory)
            else:result=compare_sequences(args.baseline_store,args.baseline,args.candidate_store,args.candidate,args.output)
            print(json.dumps(result,indent=2,allow_nan=False))
            return 2 if result.get('status') in ('failed','incomplete','validation_error','unsupported') else 0
        store=Store(args.workspace)
        if args.command=='channel':
            from .channel import serve
            return serve(store,base_dir=args.base_dir,result_ref=args.result_ref,workers=args.workers,enable_motion_provider=args.enable_motion_provider)
        elif args.command=='web':
            from .web_server import serve_web
            return serve_web(store,base_dir=args.base_dir,port=args.port,workers=args.workers,enable_motion_provider=args.enable_motion_provider)
        elif args.command=='import':
            from .acquisition import import_image
            result=import_image(store,args.path)
        elif args.command=='construct':
            from .construction_services import invoke_construction
            result=invoke_construction(store,args.method,read_json(args.request),base_dir=Path(args.request).resolve().parent)
        elif args.command=='pixellab-vfx':
            from .source_workflow import invoke_source_vfx
            result=invoke_source_vfx(store,args.method,read_json(args.request))
        elif args.command=='models':
            from .model_handoff import invoke_models
            result=invoke_models(store,args.method,read_json(args.request),base_dir=Path(args.request).resolve().parent)
        elif args.command=='motion':
            from .motion_services import invoke_motion
            result=invoke_motion(store,args.method,read_json(args.request),base_dir=Path(args.request).resolve().parent,
                                 live_provider_enabled=args.enable_motion_provider)
        elif args.command=='parity':
            from .parity_services import invoke_parity
            result=invoke_parity(store,args.method,read_json(args.request),base_dir=Path(args.request).resolve().parent)
        elif args.command in ('studio','selection'):
            from .studio_services import invoke_studio
            from .selection_services import invoke_selection
            invoke=invoke_studio if args.command=='studio' else invoke_selection
            result=invoke(store,args.method,read_json(args.request),base_dir=Path(args.request).resolve().parent)
        elif args.command=='inspect':result=store.get_json(sequence_id(store,args.artifact))
        elif args.command=='edit':
            from .raster import edit_sequence
            result=edit_sequence(store,sequence_id(store,args.sequence),read_json(args.changes))
        elif args.command=='run':
            from .pipeline import execute_plan
            result=execute_plan(store,read_json(args.plan),base_dir=Path(args.plan).resolve().parent)
        elif args.command in ('export','review'):
            ident=sequence_id(store,args.sequence)
            if args.command=='export':
                from .export import export_sequence
                result=export_sequence(store,ident,args.directory,args.formats.split(','))
            else:
                from .review import review_sequence
                result=review_sequence(store,ident,args.directory)
        elif args.command=='validate-source-request':
            from .capabilities import CapabilityRegistry
            result=CapabilityRegistry().validate_source_request(args.id,read_json(args.request))
        elif args.command=='capabilities':
            from .capabilities import CapabilityRegistry
            registry=CapabilityRegistry()
            result=registry.describe(args.id) if args.id else registry.list(args.domain)
        elif args.command=='crop':
            from .raster import crop
            result=crop(store,args.raster,args.region,node=args.node)
            if (args.region[2]-args.region[0]+1)*(args.region[3]-args.region[1]+1)>4096:
                result.pop('rgba');result['rows_omitted']='CLI4096pixel response budget; exact crop remains in Store'
        elif args.command=='paste':
            from .raster import paste
            result={'raster':paste(store,read_json(args.packet),read_json(args.rows),expected=args.expect,stamp=args.stamp)}
        print(json.dumps(result,indent=2,allow_nan=False))
        return 2 if isinstance(result,dict) and result.get('status') in ('failed','validation_error','unsupported') else 0
    except (ValidationError,OSError,KeyError,TypeError,ValueError,OverflowError,RecursionError) as e:
        result=e.to_dict() if isinstance(e,ValidationError) else {'status':'validation_error','reason':'Invalid local input','exception_type':type(e).__name__}
        print(json.dumps(result,indent=2));return 2


if __name__=='__main__':raise SystemExit(main())

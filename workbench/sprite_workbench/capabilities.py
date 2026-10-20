"""Exact frozen vendor schemas and separately invoked actual local services.

Vendor interfaces are always unsupported here. A similarly named local service
is an explicit analogue, never automatic provider forwarding or model inference.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from .core import Store, ValidationError, UnsupportedCapability, canonical_json, digest
from .jobs import _snapshot


class CapabilityRegistry:
    def __init__(self, contract_dir=None):
        self.contract_dir=Path(contract_dir) if contract_dir is not None else Path(__file__).resolve().parent/'contracts'
        def load(name):
            try: raw=(self.contract_dir/name).read_bytes()
            except OSError as e: raise ValidationError("Frozen contract directory is unavailable") from e
            return json.loads(raw),digest(raw)
        self.openapi,self.openapi_file_sha256=load('openapi.json')
        public,self.public_projection_sha256=load('PUBLIC-OPERATION-CONTRACTS.json')
        mcp,self.mcp_projection_sha256=load('MCP-TOOL-CONTRACTS.json')
        if public['sha256']!=self.openapi_file_sha256:
            raise ValidationError("Public schema snapshot hash disagrees with original OpenAPI")
        self._entries={};self._local={}
        for operation in public['operations']:
            exact=self.openapi['paths'][operation['path']][operation['method'].lower()]
            if operation['requestBody']!=exact.get('requestBody') or operation['responses']!=exact.get('responses',{}) or operation['parameters']!=exact.get('parameters',[]):
                raise ValidationError("Public operation projection differs from OpenAPI")
            record=copy.deepcopy(operation)
            schema=operation.get('requestBody',{} ) or {}
            schema=schema.get('content',{}).get('application/json',{}).get('schema')
            self._add(record,'public',schema,operation['source_sha256'],operation['pointer'])
        for tool in mcp['tools']:
            self._add(copy.deepcopy(tool),'mcp',tool['inputSchema'],mcp['sha256'],tool['json_pointer'])
        if len(public['operations'])!=111 or len(mcp['tools'])!=101 or len(self._entries)!=212:
            raise ValidationError("Frozen registry must account exactly111public/101MCP definitions")
        self.snapshot={'public_operations':111,'captured_mcp_tools':101,'implemented_vendor_handlers':0,
            'openapi_sha256':self.openapi_file_sha256,'public_projection_sha256':self.public_projection_sha256,
            'mcp_capture_source_sha256':mcp['sha256'],'mcp_projection_sha256':self.mcp_projection_sha256,
            'boundary':'Frozen snapshots are contracts, not current provider availability or212unique algorithms'}

    def _add(self, record, domain, schema, source_sha, pointer):
        ident=record['id']
        if ident in self._entries: raise ValidationError("Duplicate capability ID")
        record.update({'domain':domain,'vendor_status':'unsupported','local_classification':'unsupported',
            'handler_implemented':False,'provider_forwarding':False,'exact_input_schema':copy.deepcopy(schema),
            'schema_sha256':digest(canonical_json(schema)) if schema is not None else None,
            'schema_source_sha256':source_sha,'schema_pointer':pointer,
            'unsupported_reason':'Vendor model/handler/account/persistence implementation is not supplied; no remote calls or hidden algorithm substitution',
            'local_analogues':self._analogues(record)})
        self._entries[ident]=record

    @staticmethod
    def _analogues(record):
        path=record.get('path','');name=record.get('name','')
        if 'job' in path or name in {'get_background_job','cancel_background_job','wait_for_jobs'}:
            return ['local.jobs.get','local.jobs.list','local.jobs.cancel','local.jobs.wait']
        if path.startswith(('/characters','/objects')) or name in {'get_character','list_characters','get_object','list_objects'}:
            return ['local.library.get','local.library.list','local.library.promote','local.library.set_state','local.library.set_animation']
        return []

    def describe(self, ident):
        if ident in self._entries: return copy.deepcopy(self._entries[ident])
        if ident in self._local:
            local=self._local[ident]
            return {k:copy.deepcopy(v) for k,v in local.items() if k!='handler'}
        raise UnsupportedCapability(ident,'Unknown frozen or registered local capability')

    def list(self, domain=None):
        result=[self.describe(ident) for ident in self._entries]
        if domain in (None,'local'): result.extend(self.describe(ident) for ident in self._local)
        return [r for r in result if domain is None or r['domain']==domain]

    def register_local(self, name, handler, *, classification='local-substitute', request_schema=None, evidence=None):
        if not isinstance(name,str) or not name.startswith('local.') or not callable(handler):
            raise ValidationError("Register a named local.* callable")
        if name in self._local or name in self._entries: raise ValidationError("Capability name already registered")
        if classification not in {'supplied-art','deterministic-source','local-substitute'}:
            raise ValidationError("Invalid local implementation classification")
        if request_schema is not None: canonical_json(request_schema)
        self._local[name]={'id':name,'domain':'local','local_classification':classification,'handler_implemented':True,
            'vendor_equivalence':False,'provider_forwarding':False,'request_schema':copy.deepcopy(request_schema),
            'evidence':_snapshot(evidence or {}),'handler':handler}

    def bind_jobs(self, manager):
        services={
            'submit':lambda r:manager.submit(r['handler'],r['request'],head=r.get('head'),expected=r.get('expected')),
            'get':lambda r:manager.get(r['job_id']),
            'list':lambda r:manager.list(r.get('status'),limit=r.get('limit',100),offset=r.get('offset',0)),
            'cancel':lambda r:manager.cancel(r['job_id']),
            'retry':lambda r:manager.retry(r['job_id']),
            'wait':lambda r:manager.wait(r['job_id'],timeout=r.get('timeout',30)),
        }
        for name,handler in services.items(): self.register_local('local.jobs.'+name,handler,evidence={'implementation':'sprite_workbench.jobs.JobManager','policy':'local immutable durable jobs, not vendor scheduler'})

    def bind_library(self, library):
        services={
            'create_candidate':lambda r:library.create_candidate(**r),
            'record_review':lambda r:library.record_review(r['candidate_id'],visual_status=r.get('visual_status'),technical_status=r.get('technical_status'),metadata=r.get('metadata')),
            'select':lambda r:library.select(r['candidate_ids'],r['source_ids']),
            'get':lambda r:library.get(r['entity_id'],include_deleted=r.get('include_deleted',False)),
            'list':lambda r:library.list(**r),
            'promote':lambda r:library.promote(**r),
            'set_direction':lambda r:library.set_direction(r['entity_id'],r['direction'],r['candidate_id'],expected=r['expected']),
            'remove_direction':lambda r:library.remove_direction(r['entity_id'],r['direction'],expected=r['expected']),
            'set_state':lambda r:library.set_state(r['entity_id'],r['state'],directions=r.get('directions'),metadata=r.get('metadata'),expected=r['expected']),
            'set_animation':lambda r:library.set_animation(r['entity_id'],r['state'],r['animation'],r['directions'],expected=r['expected'],replace=r.get('replace',False),metadata=r.get('metadata')),
            'remove_state':lambda r:library.remove_state(r['entity_id'],r['state'],expected=r['expected']),
            'remove_animation':lambda r:library.remove_animation(r['entity_id'],r['state'],r['animation'],expected=r['expected'],direction=r.get('direction')),
            'archive':lambda r:library.archive(r['entity_id'],expected=r['expected'],archived=r.get('archived',True)),
            'delete':lambda r:library.delete(r['entity_id'],expected=r['expected']),
            'restore':lambda r:library.restore(r['entity_id'],r['revision_id'],expected=r['expected']),
        }
        for name,handler in services.items(): self.register_local('local.library.'+name,handler,classification='supplied-art',evidence={'implementation':'sprite_workbench.library.Library','policy':'explicit supplied candidates and direction labels, not learned generation'})

    def validate_request(self, ident, request):
        """Validate body/tool JSON offline. URL/path/query parameters are separate."""
        descriptor=self.describe(ident)
        schema=descriptor.get('exact_input_schema',descriptor.get('request_schema'))
        if schema is None:
            if descriptor['domain']=='local':
                _snapshot({} if request is None else request)
                return True
            if request not in (None,{}): raise ValidationError("This entry has no captured JSON body schema")
            return True
        try:
            from jsonschema import Draft202012Validator
            from referencing import Registry, Resource
            from referencing.jsonschema import DRAFT202012
        except ImportError:
            raise UnsupportedCapability('local.schema-validation','Install the declared jsonschema dependency') from None
        base='urn:local:pixellab:openapi'
        def rewrite(value):
            if isinstance(value,dict):
                result={k:rewrite(v) for k,v in value.items()}
                if '$ref' in result:
                    ref=result['$ref']
                    if not isinstance(ref,str) or not ref.startswith('#'):
                        raise UnsupportedCapability(ident,'External schema references are disabled')
                    if descriptor['domain']=='public': result['$ref']=base+ref
                return result
            if isinstance(value,list): return [rewrite(v) for v in value]
            return value
        schema=rewrite(schema)
        # The registry has no retrieval callback. Even unexpected references cannot fetch.
        resource=Resource.from_contents(self.openapi,default_specification=DRAFT202012)
        registry=Registry().with_resource(base,resource)
        errors=list(Draft202012Validator(schema,registry=registry).iter_errors(request))
        if errors:
            error=errors[0];pointer='/'+('/'.join(str(v).replace('~','~0').replace('/','~1') for v in error.absolute_path))
            raise ValidationError(f"Request fails schema at {pointer} ({error.validator})")
        return True

    def validate_source_request(self, ident, request):
        """Frozen-schema plus explicit source rules, without invoking a provider."""
        from .source_semantics import RequestAdmissionError, validate_source_semantics
        try:
            self.validate_request(ident, request)
        except UnsupportedCapability:
            raise
        except ValidationError as exc:
            raise RequestAdmissionError(str(exc),layer='frozen-schema') from exc
        semantic=validate_source_semantics(ident,request)
        return {'status':'validated' if semantic['status']=='passed' else semantic['status'],
                'capability':ident,'frozen_schema':'passed','source_semantics':semantic,
                'vendor_handler_implemented':False,'provider_forwarding':False}

    def bind_source_validation(self):
        self.register_local('local.requests.validate_source',
            lambda r:self.validate_source_request(r['capability'],r['request']),
            classification='deterministic-source',request_schema={
                'type':'object','additionalProperties':False,'required':['capability','request'],
                'properties':{'capability':{'type':'string'},'request':{}}},
            evidence={'implementation':'sprite_workbench.source_semantics',
                      'boundary':'Offline admission only; frozen schemas unchanged; vendor handlers unsupported'})

    def invoke(self, ident, request=None):
        if ident not in self._local:
            record=self.describe(ident)
            raise UnsupportedCapability(ident,record['unsupported_reason'])
        request=_snapshot({} if request is None else request)
        self.validate_request(ident,request)
        try: return self._local[ident]['handler'](request)
        except (KeyError,TypeError) as e:
            raise ValidationError("Local service request fields are missing or invalid") from e

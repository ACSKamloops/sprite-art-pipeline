"""Bounded native RGBA ASE exchange with Store-bound authoritative sidecars.

Actual native-tool execution belongs to the caller; writing ASE is not a tool
roundtrip or visual acceptance. The original Store binding is required on import.
"""
from pathlib import Path
import struct
import math
import zlib

from .core import Store, ValidationError, canonical_json, digest, MAX_DOCUMENT_BYTES

MAX_ASE_BYTES = 64*1024*1024
SCHEMA = 'sprite-workbench-ase-binding/v1'


class ExchangeError(ValidationError):
    """A rejected exchange whose immutable failure receipt remains recoverable."""
    def __init__(self, reason, receipt):
        super().__init__(reason)
        self.receipt = receipt
    def to_dict(self):
        return {**super().to_dict(),'exchange_receipt':self.receipt}


def _safe_path(value, *, absolute=False, file=False, limit=None):
    path=Path(value)
    if absolute and not path.is_absolute():
        raise ValidationError('Native exchange output must be an absolute path')
    path=path.absolute()
    if any(p.is_symlink() for p in [path,*path.parents]):
        raise ValidationError('Native exchange rejects symlinks, including parent paths')
    if file and (not path.is_file() or limit is not None and path.stat().st_size>limit):
        raise ValidationError('Native exchange input must be a bounded regular file')
    return path



def _binding_shape(bound):
    fields={'kind','version','project','project_hash','native_bytes','adapter_sidecar'}
    if not isinstance(bound,dict) or set(bound)!=fields or bound['kind']!='construction-ase-binding' or type(bound['version']) is not int or bound['version']!=1:
        raise ValidationError('Invalid original native exchange binding authority')
    return bound



def _binding_authority(store,bound):
    """Shared semantic source checks: importing must not emit unusable lineage."""
    from .construction import load_project
    from .construction_core.core import project_hash
    from .construction_core.canonical import canonical_json as portable_canonical
    from .core import validate_id
    _binding_shape(bound)
    for field in ('project','project_hash','native_bytes'):validate_id(bound[field])
    original=load_project(store,bound['project'])
    meta=bound['adapter_sidecar']
    original_native=store.get_bytes(bound['native_bytes'])
    if len(original_native)>MAX_ASE_BYTES or not isinstance(meta,dict) or meta.get('project_sha256')!=bound['project_hash'] or project_hash(original)!=bound['project_hash'] or digest(original_native)!=meta.get('ase_sha256') or portable_canonical(original)!=portable_canonical(meta.get('project')):
        raise ValidationError('Invalid original native exchange binding source/hash authority')
    return original


def _failure(store,operation,error,inputs):
    receipt=store.put_json({'kind':'construction-ase-receipt','version':1,'operation':operation,
        'status':'failed','reason':str(error),'exception_type':type(error).__name__,'inputs':inputs,
        'visual_acceptance':'unreviewed'})
    return ExchangeError(str(error),receipt)


def _inventory(data, decoded):
    """Offsets/link types from already validated native chunks, without rendering."""
    offset=128;frames=[]
    for frame in decoded['frames']:
        length,_,oldcount,_,newcount=struct.unpack_from('<IHHH2xI',data,offset)
        pos=offset+16;cels=[]
        for _ in range(newcount or oldcount):
            size,kind=struct.unpack_from('<IH',data,pos)
            if kind==0x2005:
                li,x,y,opacity,celtype,_=struct.unpack_from('<HhhBHh',data,pos+6)
                image=frame['raw_cels'][li]
                record={'layer':li,'offset':[x,y],'size':list(image.size),'type':celtype,
                    'rgba_sha256':digest(frame['cels'][li].tobytes()),'opacity':opacity}
                if celtype==1:record['linked_frame']=struct.unpack_from('<H',data,pos+6+16)[0]
                cels.append(record)
            pos+=size
        frames.append({'milliseconds':frame['milliseconds'],'cels':cels});offset+=length
    return {'canvas':[decoded['width'],decoded['height']],
        'layers':[{'name':x['name'],'flags':x['flags']} for x in decoded['layers']], 'frames':frames,'ignored_chunks':decoded['ignored_chunks'],
        'format':'RGBA32 normal layers; cropped/linked cels accepted; not native indexed ASE'}


def export_ase(store: Store, project_id: str, output_absent_dir: Path, animation=None) -> dict:
    """Write asset.aseprite plus required immutable-bound sidecar, preserving outputs."""
    inputs={'project':project_id,'animation':animation}
    output=None
    try:
        from .construction import load_project
        from .construction_core.aseprite import export_aseprite, read_aseprite, bounded_read
        project=load_project(store,project_id)
        if len({l['name'] for l in project['layers']})!=len(project['layers']):
            raise ValidationError('Native exchange requires unique layer names to identify order')
        output=_safe_path(output_absent_dir,absolute=True)
        if output.exists():raise ValidationError('Existing native exchange output preserved')
        output.mkdir(parents=True)
        native=output/'asset.aseprite';sidecar=output/'asset.aseprite.sprite-lab.json'
        meta=export_aseprite(project,native,animation_id=animation,sidecar=sidecar)
        if native.stat().st_size>MAX_ASE_BYTES:
            raise ValidationError('Native ASE exceeds local64MiB exchange limit')
        native_data=bounded_read(native,MAX_ASE_BYTES)
        if digest(native_data)!=meta['ase_sha256']:raise ValidationError('Native export changed before binding')
        native_id=store.put_bytes(native_data)
        binding=store.put_json({'kind':'construction-ase-binding','version':1,'project':project_id,
            'project_hash':meta['project_sha256'],'native_bytes':native_id,'adapter_sidecar':meta})
        envelope={**meta,'workbench':{'schema':SCHEMA,'binding':binding,'project':project_id}}
        envelope_data=canonical_json(envelope)+b'\n'
        if len(envelope_data)>MAX_DOCUMENT_BYTES:
            raise ValidationError('Native sidecar exceeds local document limit')
        sidecar.write_bytes(envelope_data)
        result={'status':'written','project':project_id,'project_hash':meta['project_sha256'],
            'binding':binding,'native_bytes':native_id,'sidecar_bytes':store.put_bytes(envelope_data),
            'ase_path':str(native),'sidecar_path':str(sidecar),'animation':meta['animation_id'],
            'timing':meta['timing'],'inventory':_inventory(native_data,read_aseprite(native,data=native_data)),
            'limitations':['Native RGBA32; original palette indices/aliases, ticks, pivots, events and sharing live in sidecar',
                'Bounded normal layers only; no hidden anatomy/private model/native indexed ASE claim',
                'Files written; native tool and visual verification not performed by this API']}
        receipt=store.put_json({'kind':'construction-ase-export','version':1,**result})
        result['exchange_receipt']=receipt
        (output/'exchange-receipt.json').write_bytes(canonical_json(result))
        return result
    except (OSError,ValueError,TypeError,KeyError,OverflowError,RecursionError,struct.error,zlib.error) as error:
        raise _failure(store,'export',error,inputs) from error


def import_ase(store: Store, asepath: Path, sidecarpath: Path) -> dict:
    """Accept native pixels only under the original Store-bound sidecar authority.

    Native bytes may change after an external edit; metadata/clock authority may
    not. No head publication. Unchanged projects retain exact raw/index aliases.
    """
    inputs={'ase_path':str(asepath),'sidecar_path':str(sidecarpath)}
    try:
        from .construction import load_project,save_project
        from .construction_core.aseprite import read_aseprite,import_aseprite,bounded_read,load_sidecar,bounded_metadata
        from .construction_core.loading import load_json
        from .construction_core.canonical import canonical_json as portable_canonical
        native=_safe_path(asepath,file=True,limit=MAX_ASE_BYTES)
        sidecar=_safe_path(sidecarpath,file=True,limit=MAX_DOCUMENT_BYTES)
        native_data=bounded_read(native,MAX_ASE_BYTES)
        sidecar_data=bounded_read(sidecar,MAX_DOCUMENT_BYTES)
        envelope=load_sidecar(sidecar_data)
        if not isinstance(envelope,dict) or not isinstance(envelope.get('workbench'),dict):
            raise ValidationError('Missing immutable workbench native sidecar binding')
        wb=envelope['workbench']
        if set(wb)!={'schema','binding','project'} or wb['schema']!=SCHEMA:
            raise ValidationError('Invalid native sidecar binding fields')
        bound=bounded_metadata(store.get_json(wb['binding']))
        _binding_shape(bound)
        if bound['project']!=wb['project']:
            raise ValidationError('Invalid original native exchange authority')
        meta={k:v for k,v in envelope.items() if k!='workbench'}
        if portable_canonical(meta)!=portable_canonical(bound['adapter_sidecar']):
            raise ValidationError('Dirty/stale sidecar metadata differs from immutable original binding')
        original=_binding_authority(store,bound)
        if portable_canonical(original)!=portable_canonical(meta['project']):
            raise ValidationError('Original project differs from native exchange binding')
        project=import_aseprite(native,sidecar,native_data=native_data,sidecar_data=sidecar_data)
        from .construction_core.core import project_hash as raw_project_hash
        current_hash=raw_project_hash(project)
        if current_hash==bound['project_hash'] and portable_canonical(project)==portable_canonical(original):
            saved={'project':bound['project'],'project_hash':current_hash}
        else:
            saved=save_project(store,project)
        inventory=_inventory(native_data,read_aseprite(native,data=native_data))
        audit={'kind':'construction-ase-import','version':1,'source_project':bound['project'],
            'binding':wb['binding'],'native_bytes':store.put_bytes(native_data),
            'sidecar_bytes':store.put_bytes(sidecar_data),'imported_project':saved['project'],
            'project_hash':saved['project_hash'],'inventory':inventory,'authoritative_clock':'Original sidecar ticks/fps/events; tool milliseconds checked, not inferred',
            'native_pixels_changed':saved['project_hash']!=bound['project_hash'],
            'shared_cel_policy':'Untouched aliases preserved; changed external frame instances fork their original cel binding',
            'visual_acceptance':'unreviewed'}
        receipt=store.put_json(audit)
        return {**saved,'status':'imported','import_provenance':receipt,'source_project':bound['project'],
                'binding':wb['binding'],'native_bytes':audit['native_bytes'],'sidecar_bytes':audit['sidecar_bytes']}
    except (OSError,ValueError,TypeError,KeyError,OverflowError,RecursionError,struct.error,zlib.error) as error:
        raise _failure(store,'import',error,inputs) from error


def validate_import_provenance(store: Store, provenance_id: str, *, project_id=None) -> dict:
    """Validate typed dependencies before attaching import lineage to a render.

    This is integrity/schema validation, not authentication of a writable Store
    or a rerun of the native pixel importer. It writes no artifacts or heads.
    """
    from .construction import load_project
    from .construction_core.core import project_hash
    from .construction_core.aseprite import load_sidecar,bounded_metadata
    from .construction_core.canonical import canonical_json as portable_canonical
    from .core import validate_id
    try:record=bounded_metadata(store.get_json(provenance_id))
    except (ValueError,RecursionError) as error:raise ValidationError('Malformed import provenance metadata: '+str(error)) from error
    required={'kind','version','source_project','binding','native_bytes','sidecar_bytes','imported_project',
        'project_hash','inventory','authoritative_clock','native_pixels_changed','shared_cel_policy','visual_acceptance'}
    if not isinstance(record,dict) or set(record)!=required or record['kind']!='construction-ase-import' or type(record['version']) is not int or record['version']!=1:
        raise ValidationError('Invalid construction import provenance shape/version')
    for field in ('source_project','binding','native_bytes','sidecar_bytes','imported_project','project_hash'):
        validate_id(record[field])
    if type(record['native_pixels_changed']) is not bool or record['visual_acceptance']!='unreviewed' or any(not isinstance(record[f],str) or len(record[f])>4096 for f in ['authoritative_clock','shared_cel_policy']):
        raise ValidationError('Invalid construction import provenance classifications')
    if project_id is not None and record['imported_project']!=project_id:
        raise ValidationError('Import provenance belongs to a different project')
    original=load_project(store,record['source_project']);imported=load_project(store,record['imported_project'])
    if project_hash(imported)!=record['project_hash']:
        raise ValidationError('Import provenance project hash mismatch')
    try:bound=bounded_metadata(store.get_json(record['binding']))
    except (ValueError,RecursionError) as error:raise ValidationError('Malformed import binding metadata: '+str(error)) from error
    _binding_shape(bound)
    if bound['project']!=record['source_project']:
        raise ValidationError('Import provenance original binding mismatch')
    validate_id(bound['native_bytes']);validate_id(bound['project_hash'])
    _binding_authority(store,bound)
    native=store.get_bytes(record['native_bytes']);sidecar=store.get_bytes(record['sidecar_bytes'])
    if len(native)>MAX_ASE_BYTES or len(sidecar)>MAX_DOCUMENT_BYTES:
        raise ValidationError('Import provenance blob bound exceeded')
    meta=bound['adapter_sidecar']
    try:envelope=load_sidecar(sidecar)
    except (ValueError,RecursionError) as error:raise ValidationError('Malformed import sidecar metadata: '+str(error)) from error
    if not isinstance(envelope,dict) or envelope.get('workbench')!={'schema':SCHEMA,'binding':record['binding'],'project':record['source_project']} or portable_canonical({k:v for k,v in envelope.items() if k!='workbench'})!=portable_canonical(meta):
        raise ValidationError('Import provenance sidecar differs from original binding')
    if record['native_pixels_changed']!=(record['project_hash']!=bound['project_hash']):
        raise ValidationError('Import provenance changed-pixels classification mismatch')
    selected=next((a for a in original['animations'] if a['id']==meta.get('animation_id')),None)
    if selected is None or meta.get('schema')!='sprite-edit-ase-sidecar/v1' or meta.get('sequence')!=selected['frames'] or not isinstance(meta.get('timing'),list) or len(meta['timing'])!=len(selected['frames']):
        raise ValidationError('Import provenance binding animation/clock structure')
    byid={f['id']:f for f in original['frames']};elapsed=0;previous=0
    for frame_id,timing in zip(selected['frames'],meta['timing']):
        elapsed+=byid[frame_id]['duration_ticks'];value=elapsed*1000/selected['fps']
        if not math.isfinite(value) or value>65535*len(selected['frames'])+.5:
            raise ValidationError('Import provenance source clock not representable')
        boundary=math.floor(value+.5)
        if not isinstance(timing,dict) or timing.get('frame_id')!=frame_id or type(timing.get('duration_ticks')) is not int or timing['duration_ticks']!=byid[frame_id]['duration_ticks'] or type(timing.get('milliseconds')) is not int or timing['milliseconds']!=boundary-previous:
            raise ValidationError('Import provenance binding timing differs from source ticks')
        previous=boundary
    inventory=record['inventory']
    if not isinstance(inventory,dict) or set(inventory)!={'canvas','layers','frames','format','ignored_chunks'} or inventory['canvas']!=[imported['canvas']['width'],imported['canvas']['height']] or not isinstance(inventory['layers'],list) or [l.get('name') if isinstance(l,dict) else None for l in inventory['layers']]!=[l['name'] for l in imported['layers']]:
        raise ValidationError('Import provenance inventory canvas/layers mismatch')
    if not isinstance(inventory['frames'],list) or len(inventory['frames'])!=len(meta['sequence']) or len(inventory['frames'])>512:
        raise ValidationError('Import provenance inventory frame structure')
    if not isinstance(inventory['ignored_chunks'],list) or any(not isinstance(c,dict) or set(c)!={'frame','kind','bytes','reason'} or type(c['frame']) is not int or not 0<=c['frame']<len(inventory['frames']) or type(c['kind']) is not int or c['kind'] not in (4,0x2019) or type(c['bytes']) is not int or c['bytes']<6 or not isinstance(c['reason'],str) for c in inventory['ignored_chunks']):
        raise ValidationError('Import provenance ignored metadata shape')
    if not isinstance(inventory['format'],str) or any(not isinstance(l,dict) or set(l)!={'name','flags'} or type(l['flags']) is not int or not 0<=l['flags']<=65535 for l in inventory['layers']):
        raise ValidationError('Import provenance inventory layer flags/format')
    for fi,(frame,timing) in enumerate(zip(inventory['frames'],meta['timing'])):
        if not isinstance(frame,dict) or set(frame)!={'milliseconds','cels'} or type(frame['milliseconds']) is not int or frame['milliseconds']!=timing['milliseconds'] or not isinstance(frame['cels'],list) or len(frame['cels'])>128:
            raise ValidationError('Import provenance inventory clock/cels mismatch')
        for cel in frame['cels']:
            if not isinstance(cel,dict) or not {'layer','offset','size','type','rgba_sha256','opacity'}<=set(cel)<={'layer','offset','size','type','rgba_sha256','opacity','linked_frame'} or type(cel['layer']) is not int or not 0<=cel['layer']<len(inventory['layers']) or type(cel['type']) is not int or cel['type'] not in (0,1,2) or type(cel['opacity']) is not int or cel['opacity']!=255:
                raise ValidationError('Import provenance inventory cel structure')
            if (cel['type']==1 and (type(cel.get('linked_frame')) is not int or not 0<=cel['linked_frame']<fi)) or (cel['type']!=1 and 'linked_frame' in cel):
                raise ValidationError('Import provenance inventory cel link')
            validate_id(cel['rgba_sha256'])
            if any(not isinstance(cel[k],list) or len(cel[k])!=2 or any(type(v) is not int for v in cel[k]) for k in ['offset','size']) or any(v<0 for v in cel['offset']) or any(v<=0 for v in cel['size']) or any(cel['offset'][i]+cel['size'][i]>inventory['canvas'][i] for i in (0,1)):
                raise ValidationError('Import provenance inventory cel geometry')
    return record

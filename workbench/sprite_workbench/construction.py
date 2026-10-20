"""Immutable integration of the pinned local sprite-edit-project/v1 toolkit.

Project artifact IDs hash the workbench's typed envelope. project_hash is the
separate toolkit canonical document hash (UTF16 key ordering/number policy).
The initial toolkit pin is byte-exact; separately recorded ASE parser hardening
may change that module. Guarded edits, index aliases and compositing
are its declared local policies, not native indexed undo or vendor parity.
"""
from __future__ import annotations

import copy
from collections import OrderedDict
from fractions import Fraction
import math
import threading

import numpy as np

from . import construction_core as toolkit
from . import construction_engine
from .core import (MAX_DOCUMENT_BYTES, MAX_FRAMES, MAX_SEQUENCE_BYTES, Store,
                   UnsupportedCapability, ValidationError, canonical_json,
                   digest, load_sequence, save_sequence, validate_id)

_SAFE_INTEGER = 9_007_199_254_740_991
MAX_LAYERS = 128
MAX_CELS = 4096
MAX_CEL_PIXELS = MAX_DOCUMENT_BYTES // 2
MAX_RENDER_WORK = 64 * 1024 * 1024
MAX_HISTORY_RECEIPTS = 256
MAX_HISTORY_CEL_VALUES = MAX_SEQUENCE_BYTES // 16
MAX_HISTORY_CHECKPOINT_BYTES = MAX_SEQUENCE_BYTES // 2
MAX_HISTORY_REPLAY_WORK = 512 * 1024 * 1024
MAX_HISTORY_PROOFS = 128
# Proofs contain only artifact IDs, never project arrays or trusted file stats.
# Every reuse re-reads and SHA-verifies all dependency bytes via Store.get_bytes.
_HISTORY_PROOFS = OrderedDict()
_HISTORY_PROOF_LOCK = threading.Lock()
MAX_PALETTE_ENTRIES = 1_048_576
MAX_TRANSACTION_OPERATIONS = 256
_TOOL_ERRORS = (ValueError, TypeError, KeyError, IndexError, OverflowError, UnicodeError)


def _tool_call(label, call, *args):
    try:
        return call(*args)
    except _TOOL_ERRORS as e:
        raise ValidationError("Construction " + label + ": " + str(e)) from e


def _bounded_json(value):
    # Reject unsafe integers before any toolkit math.isfinite/int conversion.
    # Estimate a lower bound before allocating the canonical JSON byte string.
    lower = 0
    active = set()
    def visit(v, depth=0):
        nonlocal lower
        if depth > 64:
            raise ValidationError("Construction JSON nesting exceeds64")
        if v is None or isinstance(v, bool):
            lower += 5
        elif type(v) is int:
            if abs(v) > _SAFE_INTEGER:
                raise ValidationError("Construction JSON integer exceeds exact JavaScript range")
            lower += len(str(v))+1
        elif type(v) is float:
            if not math.isfinite(v):
                raise ValidationError("Construction JSON must contain finite numbers")
            if v.is_integer() and abs(v) > _SAFE_INTEGER:
                raise ValidationError("Construction integral float exceeds portable safe integer range")
            lower += len(repr(v))+1
        elif isinstance(v, str):
            lower += len(v)+2
        elif isinstance(v, (list, dict)):
            key = id(v)
            if key in active:
                raise ValidationError("Construction JSON is cyclic")
            lower += len(v)+2
            if lower > MAX_DOCUMENT_BYTES:
                raise ValidationError("Construction JSON exceeds Store budget")
            active.add(key)
            if isinstance(v, dict):
                for k, child in v.items():
                    if not isinstance(k, str):
                        raise ValidationError("Construction JSON keys must be strings")
                    visit(k, depth+1)
                    visit(child, depth+1)
            else:
                for child in v:
                    visit(child, depth+1)
            active.remove(key)
        else:
            raise ValidationError("Construction input must be portable JSON values")
        if lower > MAX_DOCUMENT_BYTES:
            raise ValidationError("Construction JSON exceeds Store budget")
    visit(value)
    raw = _tool_call("JSON", canonical_json, value)
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise ValidationError("Construction document exceeds the immutable Store JSON budget")


def _project_limits(project):
    if not isinstance(project, dict):
        raise ValidationError("Construction project must be an object")
    layers = project.get("layers", [])
    cels = project.get("cels", {})
    frames = project.get("frames", [])
    if isinstance(layers, list) and len(layers) > MAX_LAYERS:
        raise ValidationError("Construction aggregate layer budget exceeded")
    if isinstance(cels, dict) and len(cels) > MAX_CELS:
        raise ValidationError("Construction aggregate cel count exceeded")
    if isinstance(frames, list) and len(frames) > MAX_FRAMES:
        raise ValidationError("Construction aggregate frame budget exceeded")
    palette = project.get("palette", [])
    if isinstance(palette, list) and len(palette) > MAX_PALETTE_ENTRIES:
        raise ValidationError("Construction aggregate palette budget exceeded")
    pixels = sum(len(c.get("pixels", [])) for c in cels.values()
                 if isinstance(c, dict) and isinstance(c.get("pixels"), list)) if isinstance(cels, dict) else 0
    if pixels > MAX_CEL_PIXELS:
        raise ValidationError("Construction aggregate cel pixel budget exceeded")
    canvas = project.get("canvas", {})
    w, h = (canvas.get("width"), canvas.get("height")) if isinstance(canvas, dict) else (None, None)
    if type(w) is int and type(h) is int:
        if abs(w) > _SAFE_INTEGER or abs(h) > _SAFE_INTEGER:
            raise ValidationError("Construction dimensions exceed safe integer domain")
        work = w*h*(max(1, len(layers)) if isinstance(layers, list) else 1)*(len(frames) if isinstance(frames, list) else 1)
        if work > MAX_RENDER_WORK:
            raise ValidationError("Construction aggregate frame/layer render budget exceeded")
    return pixels


def _transaction_work(project, transaction):
    operations = transaction.get("operations") if isinstance(transaction, dict) else None
    if not isinstance(operations, list) or not 1 <= len(operations) <= MAX_TRANSACTION_OPERATIONS:
        raise ValidationError("Construction transaction needs1..256 operations")
    canvas = project["canvas"]
    work = 2*canvas["width"]*canvas["height"]*max(1, len(project["layers"]))*len(project["frames"])
    cels = project["cels"]
    for op in operations:
        if not isinstance(op, dict):
            raise ValidationError("Construction operation must be an object")
        kind = op.get("op")
        if kind in ("paint", "erase", "replace_color", "candidate_patch"):
            for key in ("points", "mask", "candidate_pixels"):
                if isinstance(op.get(key), list):
                    work += len(op[key])
        elif kind == "translate":
            cel = cels.get(op.get("cel_id")) if isinstance(op.get("cel_id"), str) else None
            work += len(cel["pixels"]) if cel else 0
        elif kind in ("translate_layer", "palette"):
            work += sum(len(c["pixels"]) for c in cels.values())
        else:
            work += 1
        if work > MAX_RENDER_WORK:
            raise ValidationError("Construction aggregate transaction work budget exceeded")
    return work


def _journal_limits(project, journal):
    receipts = journal.get("receipts")
    if not isinstance(receipts, list) or len(receipts) > MAX_HISTORY_RECEIPTS:
        raise ValidationError("Construction history receipt budget exceeded")
    values = sum(len(c["pixels"]) for c in project["cels"].values())
    if values*(2+2*len(receipts)) > MAX_HISTORY_CEL_VALUES:
        raise ValidationError("Construction aggregate history snapshot index budget exceeded")
    work = 0
    for receipt in receipts:
        if not isinstance(receipt, dict):
            raise ValidationError("Construction receipt must be an object")
        work += _transaction_work(project, receipt.get("transaction"))
        if work > MAX_RENDER_WORK:
            raise ValidationError("Construction aggregate journal replay work budget exceeded")
    _bounded_json(journal)


def project_hash(rawproject: dict) -> str:
    """Toolkit canonical hash after strict finite/numeric/resource admission."""
    _project_limits(rawproject)
    _bounded_json(rawproject)
    return _tool_call("project", toolkit.project_hash, rawproject)


def parse_project(text: str | bytes) -> dict:
    """Portable finite JSON boundary; normalize safe integral decimals only."""
    if not isinstance(text, (str, bytes)) or len(text) > MAX_DOCUMENT_BYTES:
        raise ValidationError("Construction input JSON must be bounded text/bytes")
    # Parse without project validation first: admission must precede toolkit math.
    project = _tool_call("portable JSON", toolkit.load_json, text)
    project_hash(project)
    return project


def _project_document(store, ident):
    doc = store.get_json(ident)
    required = {"kind", "version", "document", "project_hash"}
    if (set(doc) - required - {"source_sequence"} or required - set(doc)
            or doc.get("kind") != "construction-project"
            or type(doc.get("version")) is not int or doc["version"] != 1):
        raise ValidationError("Expected construction-project version1")
    actual = project_hash(doc["document"])
    if doc["project_hash"] != actual:
        raise ValidationError("Construction project hash mismatch")
    if "source_sequence" in doc:
        validate_id(doc["source_sequence"])
        load_sequence(store, doc["source_sequence"])
    return doc


def _save_project(store, rawproject, source_sequence=None):
    ident = project_hash(rawproject)
    project = _tool_call("snapshot", copy.deepcopy, rawproject)
    doc = {"kind": "construction-project", "version": 1, "document": project, "project_hash": ident}
    if source_sequence is not None:
        validate_id(source_sequence)
        load_sequence(store, source_sequence)
        doc["source_sequence"] = source_sequence
    return {"project": store.put_json(doc), "project_hash": ident}


def save_project(store: Store, rawproject: dict) -> dict:
    """Validate/store a snapshot; no head publication or inferred source links."""
    return _save_project(store, rawproject)


def load_project(store: Store, ident: str) -> dict:
    """Return a validated detached raw toolkit document, not its envelope."""
    return _project_document(store, ident)["document"]


def _proof_key(store, ident):
    return (str(store.path.resolve()), ident)


def clear_history_proofs():
    """Drop process-local acceleration; the next v2 load verifies cold replay."""
    with _HISTORY_PROOF_LOCK:
        _HISTORY_PROOFS.clear()


def _remember_proof(store, ident, dependencies):
    with _HISTORY_PROOF_LOCK:
        _HISTORY_PROOFS[_proof_key(store, ident)] = tuple(sorted(set(dependencies)))
        _HISTORY_PROOFS.move_to_end(_proof_key(store, ident))
        while len(_HISTORY_PROOFS) > MAX_HISTORY_PROOFS:
            _HISTORY_PROOFS.popitem(last=False)


def _cached_proof(store, ident):
    with _HISTORY_PROOF_LOCK:
        dependencies = _HISTORY_PROOFS.get(_proof_key(store, ident))
    if dependencies is None:
        return None
    total = 0
    for dependency in dependencies:
        total += len(store.get_bytes(dependency))
        if total > MAX_HISTORY_CHECKPOINT_BYTES:
            raise ValidationError("Construction history checkpoint byte budget exceeded")
    return set(dependencies)


def _project_dependencies(store, project_id, document):
    dependencies = {project_id}
    source = document.get('source_sequence')
    if source is not None:
        sequence = store.get_json(source)
        dependencies.add(source)
        for frame in sequence['frames']:
            dependencies.add(frame['raster'])
            dependencies.add(store.get_json(frame['raster'])['blob'])
    return dependencies


def _v2_limits(initial, journal, checkpoints):
    required = {'schema', 'initial_project_sha256', 'cursor', 'receipts'}
    if not isinstance(journal, dict) or set(journal) != required:
        raise ValidationError("Invalid construction journal fields")
    receipts, cursor = journal['receipts'], journal['cursor']
    if not isinstance(receipts, list) or len(receipts) > MAX_HISTORY_RECEIPTS:
        raise ValidationError("Construction history receipt budget exceeded")
    if (journal['schema'] != 'sprite-edit-journal/v1' or type(cursor) is not int
            or not 0 <= cursor <= len(receipts)):
        raise ValidationError("Invalid construction journal cursor/schema")
    if not isinstance(checkpoints, list) or len(checkpoints) != len(receipts)+1:
        raise ValidationError("Construction history checkpoints differ from receipts")
    for checkpoint in checkpoints:
        validate_id(checkpoint)
    values = sum(len(c['pixels']) for c in initial['cels'].values())
    if values*4 > MAX_HISTORY_CEL_VALUES:
        raise ValidationError("Construction history peak working snapshot index budget exceeded")
    # Operations cannot change layer, frame or cel topology. Render each unique
    # binding once instead of once per frame, and release each replay pair.
    bindings = {tuple(f['cels'].get(l['id']) for l in initial['layers']) for f in initial['frames']}
    area = initial['canvas']['width']*initial['canvas']['height']
    render_work = 2*area*sum(sum(c is not None for c in binding) for binding in bindings)
    work = 0
    for receipt in receipts:
        if not isinstance(receipt, dict) or not isinstance(receipt.get('transaction'), dict):
            raise ValidationError("Construction receipt must contain transaction")
        original = _transaction_work(initial, receipt['transaction'])
        redundant = 2*area*max(1, len(initial['layers']))*len(initial['frames'])
        work += original-redundant+render_work+values
        if work > MAX_HISTORY_REPLAY_WORK:
            raise ValidationError("Construction aggregate journal replay work budget exceeded")
    _bounded_json(journal)


def _rehydrate_v1(store, ident, doc, materialize=False):
    required = {'kind', 'version', 'initial_project', 'project', 'project_hash', 'journal'}
    if set(doc) != required:
        raise ValidationError("Invalid construction-history version1 fields")
    initial_document = _project_document(store, doc['initial_project'])
    initial = initial_document['document']
    journal = doc['journal']
    if not isinstance(journal, dict) or set(journal) != {'schema', 'initial_project_sha256', 'cursor', 'receipts'}:
        raise ValidationError("Invalid construction journal fields")
    _journal_limits(initial, journal)
    history = _tool_call('journal replay', toolkit.History.replay, initial, journal)
    if toolkit.canonical_json(history.journal()) != toolkit.canonical_json(journal):
        raise ValidationError("Construction journal differs from exact replay receipt")
    current = _project_document(store, doc['project'])
    if (doc['project_hash'] != current['project_hash']
            or toolkit.project_hash(history.project) != current['project_hash']
            or history.project != current['document']):
        raise ValidationError("Construction history cursor/project mismatch")
    if not materialize:
        return doc, current, set()
    if initial_document.get('source_sequence') != current.get('source_sequence'):
        raise ValidationError("Construction v1 migration source sequence mismatch")
    # Mutations migrate only after complete old-format verification. Read-only
    # load_history never writes checkpoint artifacts into an older store.
    checkpoints = [doc['initial_project']]
    dependencies = _project_dependencies(store, doc['initial_project'], initial_document)
    for record in history.records:
        saved = _save_project(store, record['after'], current.get('source_sequence'))
        checkpoints.append(saved['project'])
        dependencies.update(_project_dependencies(store, saved['project'], _project_document(store, saved['project'])))
    return {**doc, 'version': 2, 'checkpoints': checkpoints}, current, dependencies


def _source_evidence_dependencies(store, doc, *, verify_artifacts=()):
    """Bind source geometry to its exact guarded journal transaction.

    This optional local history metadata carries the original footprint through
    edits, branching, undo/redo and portable closure. It is not a vendor journal.
    """
    entries = doc.get('source_evidence', [])
    if not isinstance(entries, list) or len(entries) > MAX_HISTORY_RECEIPTS:
        raise ValidationError('Construction source evidence budget/type differs')
    dependencies, seen = set(), set()
    for entry in entries:
        if (not isinstance(entry, dict) or set(entry) != {'artifact', 'receipt_index'}
                or type(entry['receipt_index']) is not int or entry['receipt_index'] < 0
                or entry['receipt_index'] in seen):
            raise ValidationError('Construction source evidence entry differs')
        seen.add(entry['receipt_index'])
        validate_id(entry['artifact'])
        footprint = store.get_json(entry['artifact'])
        from . import parity_commands
        if (footprint.get('kind') != 'recovered-host-footprints' or type(footprint.get('version')) is not int
                or footprint['version'] != 1 or footprint.get('source_provenance') != parity_commands.describe()['source_provenance']
                or not isinstance(footprint.get('results'), list) or len(footprint['results']) != 1):
            raise ValidationError('Construction source footprint provenance differs')
        try:
            row = footprint['results'][0]
            parity_commands._validate([row['command']])
            points = row['points']
            if (not isinstance(points, list) or len(points) > 150000 or
                    any(not isinstance(p, list) or len(p) != 2 or any(type(v) is not int for v in p) for p in points)):
                raise ValidationError('Construction source footprint points differ')
            exact_points = {tuple(p) for p in points}
            operations = doc['journal']['receipts'][entry['receipt_index']]['transaction']['operations']
            if (row['ordered_points_sha256'] != digest(canonical_json({'points': points}))
                    or row['returned_points'] != len(points) or row['unique_pixels'] != len(exact_points)
                    or len(operations) != 1 or operations[0]['op'] != 'candidate_patch'
                    or {tuple(p) for p in operations[0]['mask']} != exact_points):
                raise ValidationError('Construction source evidence differs from guarded transaction')
            if entry['artifact'] in verify_artifacts:
                replayed = parity_commands.evaluate([row['command']])
                if canonical_json({'rows': replayed['results']}) != canonical_json({'rows': footprint['results']}):
                    raise ValidationError('Construction source command differs from actual Godot footprint replay')
        except (KeyError, IndexError, TypeError) as exc:
            raise ValidationError('Construction source evidence journal binding differs') from exc
        dependencies.add(entry['artifact'])
    return dependencies


def bind_source_evidence(store, history_id, artifact):
    """Attach source footprint to the latest exact transaction without pixel edits."""
    old, _, dependencies = _rehydrate_history(store, history_id)
    if old['version'] != 2 or old['journal']['cursor'] < 1:
        raise ValidationError('Source evidence requires an existing latest v2 transaction')
    entries = list(old.get('source_evidence', []))
    entries.append({'artifact': artifact, 'receipt_index': old['journal']['cursor'] - 1})
    doc = {**old, 'source_evidence': entries}
    return _persist_history(store, doc, dependencies)


def _rehydrate_history(store, ident, *, migrate_v1=False):
    doc = store.get_json(ident)
    if doc.get('kind') != 'construction-history' or type(doc.get('version')) is not int:
        raise ValidationError("Expected construction-history version1 or version2")
    if doc['version'] == 1:
        return _rehydrate_v1(store, ident, doc, materialize=migrate_v1)
    required = {'kind', 'version', 'initial_project', 'project', 'project_hash', 'journal', 'checkpoints'}
    if doc['version'] != 2 or not required <= set(doc) <= required | {'source_evidence'}:
        raise ValidationError("Expected construction-history version2 exact fields")
    evidence_dependencies = _source_evidence_dependencies(store, doc)
    initial = _project_document(store, doc['initial_project'])
    journal, checkpoints = doc['journal'], doc['checkpoints']
    _v2_limits(initial['document'], journal, checkpoints)
    if (checkpoints[0] != doc['initial_project'] or journal['initial_project_sha256'] != initial['project_hash']
            or checkpoints[journal['cursor']] != doc['project']):
        raise ValidationError("Construction history cursor/checkpoint mismatch")
    dependencies = _cached_proof(store, ident)
    if dependencies is None:
        _source_evidence_dependencies(store, doc, verify_artifacts=evidence_dependencies)
        dependencies = _project_dependencies(store, doc['initial_project'], initial) | evidence_dependencies
        before = initial
        total_bytes = len(store.get_bytes(doc['initial_project']))
        counted_checkpoints = {doc['initial_project']}
        for receipt, checkpoint in zip(journal['receipts'], checkpoints[1:]):
            after = _project_document(store, checkpoint)
            if checkpoint not in counted_checkpoints:
                total_bytes += len(store.get_bytes(checkpoint))
                counted_checkpoints.add(checkpoint)
            if total_bytes > MAX_HISTORY_CHECKPOINT_BYTES:
                raise ValidationError("Construction history checkpoint byte budget exceeded")
            if before.get('source_sequence') != after.get('source_sequence'):
                raise ValidationError("Construction history source sequence changed")
            result = _tool_call('checkpoint replay', construction_engine.apply_transaction,
                                before['document'], receipt['transaction'])
            if (toolkit.canonical_json(result['receipt']) != toolkit.canonical_json(receipt)
                    or result['receipt']['after_sha256'] != after['project_hash']
                    or result['project'] != after['document']):
                raise ValidationError("Construction checkpoint differs from exact replay receipt")
            dependencies.update(_project_dependencies(store, checkpoint, after))
            before = after
        # Include source-raster closure in the same aggregate integrity budget.
        if sum(len(store.get_bytes(key)) for key in dependencies) > MAX_HISTORY_CHECKPOINT_BYTES:
            raise ValidationError("Construction history checkpoint byte budget exceeded")
        _remember_proof(store, ident, dependencies)
    current = _project_document(store, doc['project'])
    if current['project_hash'] != doc['project_hash']:
        raise ValidationError("Construction history cursor/project hash mismatch")
    return doc, current, dependencies


def _persist_history(store, doc, dependencies):
    _bounded_json(doc)
    evidence = _source_evidence_dependencies(store, doc)
    _source_evidence_dependencies(store, doc, verify_artifacts=evidence - set(dependencies))
    dependencies = set(dependencies) | evidence
    if sum(len(store.get_bytes(key)) for key in dependencies) > MAX_HISTORY_CHECKPOINT_BYTES:
        raise ValidationError("Construction history checkpoint byte budget exceeded")
    ident = store.put_json(doc)
    _remember_proof(store, ident, dependencies)
    return {'history': ident, 'project': doc['project'], 'project_hash': doc['project_hash']}


def create_history(store: Store, project_id: str) -> dict:
    """Create a v2 cursor-zero history from one immutable validated project."""
    project = _project_document(store, project_id)
    journal = {'schema': 'sprite-edit-journal/v1', 'initial_project_sha256': project['project_hash'],
               'cursor': 0, 'receipts': []}
    _v2_limits(project['document'], journal, [project_id])
    doc = {'kind': 'construction-history', 'version': 2, 'initial_project': project_id,
        'project': project_id, 'project_hash': project['project_hash'], 'journal': journal,
        'checkpoints': [project_id]}
    return _persist_history(store, doc, _project_dependencies(store, project_id, project))


def load_history(store: Store, history_id: str) -> dict:
    """Validate exact cold replay, or re-hash every dependency of a proven state."""
    doc, _, _ = _rehydrate_history(store, history_id)
    return {'history': history_id, 'initial_project': doc['initial_project'],
            'project': doc['project'], 'project_hash': doc['project_hash'], 'journal': doc['journal'],
            **({'source_evidence': doc['source_evidence']} if 'source_evidence' in doc else {})}


def edit_history(store: Store, history_id: str, transaction: dict) -> dict:
    """Guarded incremental edit; checkpoints are immutable and cold-verifiable."""
    _bounded_json(transaction)
    old, current, dependencies = _rehydrate_history(store, history_id, migrate_v1=True)
    _transaction_work(current['document'], transaction)
    journal = copy.deepcopy(old['journal'])
    cursor = journal['cursor']
    if cursor >= MAX_HISTORY_RECEIPTS:
        raise ValidationError("Construction history receipt budget exceeded")
    # Run all guards and compute the exact pinned receipt before publishing blobs.
    result = _tool_call('edit', construction_engine.apply_transaction, current['document'], transaction)
    journal['receipts'] = journal['receipts'][:cursor]+[result['receipt']]
    journal['cursor'] = cursor+1
    checkpoints = old['checkpoints'][:cursor+1]+['0'*64]
    try:
        _v2_limits(current['document'], journal, checkpoints)
    except ValidationError as error:
        if 'journal replay work' in str(error):
            raise ValidationError('Construction aggregate history edit work budget exceeded') from error
        raise
    saved = _save_project(store, result['project'], current.get('source_sequence'))
    checkpoints[-1] = saved['project']
    doc = {**old, **saved, 'version': 2, 'journal': journal, 'checkpoints': checkpoints}
    if 'source_evidence' in doc:
        doc['source_evidence'] = [entry for entry in doc['source_evidence'] if entry['receipt_index'] < cursor]
    # A branch retains only the prefix checkpoints and its shared source closure.
    dependencies = set(checkpoints)
    dependencies.update(_project_dependencies(store, saved['project'], _project_document(store, saved['project'])))
    return {**_persist_history(store, doc, dependencies), 'receipt': result['receipt']}


def move_history(store: Store, history_id: str, action: str) -> dict:
    """Move the cursor to a verified immutable checkpoint without replay copying."""
    if action not in ('undo', 'redo') or not isinstance(action, str):
        raise ValidationError("Construction history action must be undo or redo")
    old, _, dependencies = _rehydrate_history(store, history_id, migrate_v1=True)
    journal = copy.deepcopy(old['journal'])
    cursor = journal['cursor'] + (-1 if action == 'undo' else 1)
    if not 0 <= cursor <= len(journal['receipts']):
        raise ValidationError('Nothing to '+action)
    journal['cursor'] = cursor
    project_id = old['checkpoints'][cursor]
    project = _project_document(store, project_id)
    doc = {**old, 'project': project_id, 'project_hash': project['project_hash'], 'journal': journal}
    return _persist_history(store, doc, dependencies)


def _pivot(values):
    if any(type(v) not in (int, float) or abs(v) > _SAFE_INTEGER or not math.isfinite(v) or int(v) != v for v in values):
        raise UnsupportedCapability("construction-pivot", "Toolkit canvas pivots require safe integer coordinates")
    return [int(v) for v in values]


def from_sequence(store: Store, sequence_id: str, *, animation_id="clip", fps=None) -> dict:
    """Import registered supplied frames as one indexed paint layer.

    No hidden layer/part geometry is inferred. The palette deduplicates exact RGBA
    by first appearance; equal full-canvas rasters deliberately share cels. Only
    one-shot/infinite play counts and common integer pivots/directions map to the
    toolkit. Explicit construction clock, frame IDs, landmarks, events and ground
    pivot survive; contradictory declarations reject rather than lose metadata.
    Nonzero alpha-zero RGB rejects because its compositor renders those
    pixels black. An explicit FPS must give integral safe ticks for every hold;
    auto FPS is the exact denominator LCM, never clock quantization.
    """
    doc, arrays = load_sequence(store, sequence_id)
    count = doc.get("play_count", 0 if doc["loop"] else 1)
    if count not in (0, 1):
        raise UnsupportedCapability("construction-play-count", "Toolkit animations represent one-shot or infinite loop, not finite repeats")
    pivots = [f["pivot"] for f in doc["frames"]]
    directions = [f["direction"] for f in doc["frames"]]
    if any(p != pivots[0] for p in pivots) or any(d != directions[0] for d in directions):
        raise UnsupportedCapability("construction-registration", "One toolkit animation needs common pivot and direction; split the supplied sequence explicitly")
    pivot = _pivot(pivots[0])
    if not isinstance(animation_id, str) or not animation_id:
        raise ValidationError("Construction animation ID must be nonempty text")
    if any(np.any((a[..., 3] == 0) & np.any(a[..., :3] != 0, axis=2)) for a in arrays):
        raise UnsupportedCapability("construction-hidden-rgb", "Indexed cels can store hidden colors but toolkit frame composition normalizes them; no silent raw-RGBA import loss")
    durations = [Fraction(*f["duration"]) for f in doc["frames"]]
    metadata = doc.get("metadata", {})
    source_fps = metadata.get("fps")
    if "fps" in metadata:
        if type(source_fps) is int and source_fps > _SAFE_INTEGER:
            raise UnsupportedCapability("construction-clock", "Source FPS exceeds the toolkit safe integer domain")
        if type(source_fps) not in (int, float) or source_fps <= 0 or not math.isfinite(source_fps):
            raise ValidationError("Construction source FPS must be positive and finite")
        if fps is not None and (type(fps) not in (int, float)
                                or type(fps) is int and abs(fps) > _SAFE_INTEGER or not math.isfinite(fps)
                                or Fraction(fps) != Fraction(source_fps)):
            raise UnsupportedCapability("construction-clock", "Explicit FPS conflicts with the declared source clock; retime metadata explicitly")
        fps = source_fps
    source_ticks = metadata.get("duration_ticks")
    if "duration_ticks" in metadata:
        if (source_fps is None or not isinstance(source_ticks, list) or len(source_ticks) != len(arrays)
                or any(type(t) is not int or not 0 < t <= _SAFE_INTEGER for t in source_ticks)):
            raise ValidationError("Construction source ticks require an explicit FPS and one positive safe integer per frame")
        if any(Fraction(t, 1)/Fraction(source_fps) != d for t, d in zip(source_ticks, durations)):
            raise ValidationError("Construction source ticks/FPS contradict sequence holds")
    events = copy.deepcopy(metadata.get("events", []))
    if not isinstance(events, list) or events and source_fps is None:
        raise ValidationError("Construction events require a list and an explicit source FPS")
    frame_ids = copy.deepcopy(metadata.get("frame_ids", ["frame-" + str(i) for i in range(len(arrays))]))
    if (not isinstance(frame_ids, list) or len(frame_ids) != len(arrays)
            or any(not isinstance(f, str) or not f for f in frame_ids)):
        raise ValidationError("Construction source frame IDs must match the ordered frames")
    landmarks = copy.deepcopy(metadata.get("landmarks", [{} for _ in arrays]))
    if not isinstance(landmarks, list) or len(landmarks) != len(arrays) or any(not isinstance(v, dict) for v in landmarks):
        raise ValidationError("Construction source landmarks must match the ordered frames")
    ground_pivot = copy.deepcopy(metadata.get("ground_pivot", pivot))
    if not isinstance(ground_pivot, list) or len(ground_pivot) != 2:
        raise ValidationError("Construction ground pivot must have two coordinates")
    ground_pivot = _pivot(ground_pivot)
    if fps is None:
        fps = 1
        for duration in durations:
            fps = math.lcm(fps, duration.denominator)
            if fps > _SAFE_INTEGER:
                raise UnsupportedCapability("construction-clock", "Exact denominator LCM exceeds the toolkit safe integer FPS domain")
    if type(fps) is int and fps > _SAFE_INTEGER:
        raise UnsupportedCapability("construction-clock", "Integer FPS exceeds the toolkit safe integer domain")
    if type(fps) not in (int, float) or fps <= 0 or not math.isfinite(fps):
        raise ValidationError("Construction FPS must be a positive finite number")
    clock = Fraction(fps)  # Binary float value is explicit; no decimal/rounding approximation.
    ticks = [d*clock for d in durations]
    if any(t.denominator != 1 or not 0 < t.numerator <= _SAFE_INTEGER for t in ticks):
        raise UnsupportedCapability("construction-clock", "Exact holds must map to positive safe integer ticks at this FPS")
    area = doc["canvas"][0]*doc["canvas"][1]
    if area*len(arrays) > MAX_RENDER_WORK or area*len({digest(a.tobytes()) for a in arrays}) > MAX_CEL_PIXELS:
        raise ValidationError("Construction supplied sequence exceeds aggregate cel/render budget")
    palette = [[0, 0, 0, 0]]
    colors = {(0, 0, 0, 0): 0}
    cels, by_raster, frames, by_frame = {}, {}, [], {}
    for i, (a, hold) in enumerate(zip(arrays, ticks)):
        key = digest(a.tobytes())
        if key not in by_raster:
            cel_id = "cel-" + str(i)
            pixels = []
            for rgba in a.reshape(-1, 4):
                color = tuple(int(v) for v in rgba)
                if color not in colors:
                    if len(palette) >= MAX_PALETTE_ENTRIES:
                        raise ValidationError("Construction supplied sequence exceeds palette budget")
                    colors[color] = len(palette)
                    palette.append(list(color))
                pixels.append(colors[color])
            cels[cel_id] = {"layer_id": "paint", "pixels": pixels}
            by_raster[key] = cel_id
        frame = {"id": frame_ids[i], "duration_ticks": hold.numerator,
                 "cels": {"paint": by_raster[key]}, "landmarks": landmarks[i]}
        if frame["id"] in by_frame:
            if by_frame[frame["id"]] != frame:
                raise ValidationError("Repeated source frame ID has conflicting pixels, holds or landmarks")
        else:
            by_frame[frame["id"]] = frame
            frames.append(frame)
    project = {"schema": "sprite-edit-project/v1", "canvas": {"width": doc["canvas"][0],
        "height": doc["canvas"][1], "render_pivot": pivot, "ground_pivot": ground_pivot},
        "palette": palette, "layers": [{"id": "paint", "name": "Supplied composite", "locked": False}],
        "cels": cels, "frames": frames, "animations": [{"id": animation_id,
        "frames": frame_ids, "fps": fps, "loop": doc["loop"], "events": events}],
        "provenance": {"workbench_source_sequence": sequence_id, "workbench_direction": directions[0],
            "import_policy": "one supplied composite paint layer; exact RGBA palette, equal rasters share cels",
            "clock_policy": "exact ticks/FPS; float FPS means its exact binary value",
            "ground_pivot_policy": "preserved explicit source ground pivot" if "ground_pivot" in metadata else "copied render pivot; sequence has no independent ground pivot",
            "metadata_policy": "preserve explicit construction clock/frame IDs/landmarks/events; inconsistent declarations reject",
            "missing_geometry": "no inferred layers, rig, anatomy, hidden surfaces or direction synthesis"}}
    return _save_project(store, project, source_sequence=sequence_id)


def render_animation(store: Store, project_id: str, animation_id: str) -> dict:
    """Render ordered toolkit composited frames to a rational-clock sequence.

    Hidden RGB/palette aliases remain editable in the source document; rendered
    alpha-zero composite pixels are black. Float FPS is treated as its exact
    binary value; unsupported exporter clocks remain separate explicit limits.
    Events, landmarks, ground pivot and frame IDs survive in sequence metadata.
    """
    project = load_project(store, project_id)
    if not isinstance(animation_id, str):
        raise ValidationError("Construction animation ID must be text")
    animation = next((a for a in project["animations"] if a["id"] == animation_id), None)
    if animation is None:
        raise ValidationError("Unknown construction animation")
    ids = animation["frames"]
    width, height = project["canvas"]["width"], project["canvas"]["height"]
    if len(ids) > MAX_FRAMES or width*height*4*len(ids) > MAX_SEQUENCE_BYTES:
        raise ValidationError("Construction animation exceeds sequence frame/byte budget")
    if width*height*len(ids)*max(1, len(project["layers"])) > MAX_RENDER_WORK:
        raise ValidationError("Construction selected animation exceeds aggregate render work budget")
    frames = {f["id"]: f for f in project["frames"]}
    fps = Fraction(animation["fps"])
    durations = [Fraction(frames[f]["duration_ticks"], 1)/fps for f in ids]
    if any(not 0 < d <= 3600 for d in durations):
        raise UnsupportedCapability("construction-clock", "Rendered holds must be positive and <=3600 seconds")
    rendered = _tool_call("render", toolkit.core.render_frames, project, ids)
    arrays = [np.array(im, dtype=np.uint8) for im in rendered]
    provenance = project.get("provenance", {})
    direction = provenance.get("workbench_direction", "unspecified") if isinstance(provenance, dict) else "unspecified"
    if not isinstance(direction, str) or not direction:
        direction = "unspecified"  # Arbitrary provenance cannot declare an invalid sequence label.
    metadata = {"construction_project": project_id, "source_ids": [project_id],
        "project_hash": _tool_call("hash", toolkit.project_hash, project), "animation": animation_id,
        "frame_ids": ids, "duration_ticks": [frames[f]["duration_ticks"] for f in ids],
        "fps": animation["fps"], "fps_policy": "exact integer or exact binary float value",
        "ground_pivot": project["canvas"]["ground_pivot"], "landmarks": [frames[f]["landmarks"] for f in ids],
        "events": animation["events"], "hidden_rgb_policy": "toolkit composite alpha-zero becomes black; indexed source retained",
        "method": "pinned-construction-toolkit-v1", "capability": "supplied-art", "artistic_acceptance": "unreviewed"}
    seq = save_sequence(store, arrays, durations, pivots=[project["canvas"]["render_pivot"]]*len(arrays),
                        loop=animation["loop"], directions=[direction]*len(arrays), metadata=metadata)
    return {"sequence": seq, "project": project_id, "project_hash": metadata["project_hash"]}

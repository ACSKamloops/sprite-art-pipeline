"""Executable local state recipes. Fixtures are diagnostics, not generated art."""
from pathlib import Path
import json
import threading

import numpy as np

from .core import Store, ValidationError, UnsupportedCapability, save_sequence, load_sequence
from .library import Library, StaleRevision
from .jobs import JobManager
from .capabilities import CapabilityRegistry
from .export import export_sequence

FLOW_IDS = ('F04', 'F05', 'F11')


def marker(value):
    a = np.zeros((5, 7, 4), np.uint8)
    a[1:4, 2:5] = [value, 31, 67, 255]
    a[1, 5] = [17, value, 73, 127]
    a[4, 0] = [29, 37, value, 0]
    return a


def run_flow(flow_id: str, store: Store, output: Path):
    if flow_id not in FLOW_IDS:
        raise ValidationError('Unknown state replay flow')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    checks = []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    def rejected(name, fn, error=ValidationError):
        try:
            fn()
        except error:
            check(name, True)
        else:
            check(name, False)
    arrays = [marker(v) for v in (31, 71, 111)]
    rasters = [store.put_raster(a) for a in arrays]
    inputs = {'fixture': 'asymmetric-local-state-v1', 'rasters': rasters,
              'durations': [[1, 10], [1, 5]], 'artistic_acceptance': 'unreviewed'}
    (output / 'INPUTS.json').write_text(json.dumps(inputs, indent=2) + '\n')
    sequence = save_sequence(store, arrays[:2], durations=inputs['durations'],
                             directions=['south', 'south'], metadata={'fixture': inputs['fixture']})
    artifacts = {'sequence': sequence}
    library = Library(store)
    order = []
    if flow_id == 'F04':
        order = ['supplied directions', 'promote local entity', 'state', 'unequal animation clocks',
                 'fresh Store reload', 'remove animation direction', 'tombstone', 'restore', 'export']
        refs = {d: library.create_candidate(rasters[i], source_id=d)
                for i, d in enumerate(('south', 'east'))}
        entity = library.promote(list(refs.values()), name='diagnostic-character',
                                 entity_kind='character', directions=refs)
        rev = library.get(entity)['revision_id']
        rev = library.set_state(entity, 'base', expected=rev)
        east = save_sequence(store, [arrays[1], arrays[1], arrays[2]],
                             durations=[[1, 12], [1, 6], [1, 4]], directions=['east'] * 3)
        artifacts['east_sequence'] = east
        for direction, seq in [('south', sequence), ('east', east)]:
            candidate = library.create_candidate(seq, source_id='walk_' + direction)
            rev = library.set_animation(entity, 'base', 'walk', {direction: candidate}, expected=rev)
        fresh = Library(Store(store.path)).get(entity)
        group = fresh['document']['states']['base']['animations']['walk']['directions']
        check('fresh_store_retains_explicit_directions', set(group) == {'south', 'east'})
        east_doc, _ = load_sequence(store, group['east']['artifact_id'])
        check('unequal_clocks_retained', [f['duration'] for f in east_doc['frames']] == [[1, 12], [1, 6], [1, 4]])
        check('duplicate_frames_not_coalesced', east_doc['frames'][0]['raster'] == east_doc['frames'][1]['raster'])
        old = rev
        rev = library.remove_animation(entity, 'base', 'walk', direction='south', expected=rev)
        rejected('stale_removal_rejected', lambda: library.remove_state(entity, 'base', expected=old), StaleRevision)
        retained = rev
        deleted = library.delete(entity, expected=rev)
        check('tombstone_hides_entity', library.list() == [])
        library.restore(entity, retained, expected=deleted)
        check('restore_exact_revision', library.get(entity)['revision_id'] == retained)
        artifacts.update(entity=entity, revision=retained)
    elif flow_id == 'F05':
        order = ['supplied candidates', 'select by actual source suffix', 'promote', 'review rejection',
                 'add supplied direction', 'stale update rejection', 'reload', 'export']
        candidates = [library.create_candidate(r, source_id=s)
                      for r, s in zip(rasters, ['frame_10', 'frame_2', 'frame_1'])]
        selected = library.select(candidates, ['frame_2', 'frame_10'])
        check('selection_is_by_source_id_not_position', selected == [candidates[1], candidates[0]])
        entity = library.promote(selected, name='diagnostic-object', directions={'south': selected[0]})
        old = library.get(entity)['revision_id']
        rev = library.set_direction(entity, 'east', selected[1], expected=old)
        rejected('stale_direction_rejected', lambda: library.set_direction(entity, 'north', candidates[2], expected=old), StaleRevision)
        bad = library.record_review(candidates[2], visual_status='rejected')
        rejected('rejected_art_cannot_promote', lambda: library.promote([bad], name='rejected'))
        rejected('index_is_not_candidate_id', lambda: library.promote([2], name='wrong'))
        fresh = Library(Store(store.path)).get(entity)
        check('missing_views_not_invented', set(fresh['document']['directions']) == {'south', 'east'})
        check('failed_updates_preserve_revision', fresh['revision_id'] == rev)
        artifacts.update(entity=entity, revision=rev, rejected_candidate=bad)
    else:
        order = ['freeze supplied request', 'bounded local workers', 'guarded publication',
                 'late completion quarantine', 'cancel quarantine', 'fresh manager reload',
                 'offline schema validation', 'unsupported vendor handler', 'export']
        release = threading.Event()
        started = threading.Event()
        cancel_release = threading.Event()
        cancel_started = threading.Event()
        def handler(request, context):
            if request['mode'] == 'old':
                started.set()
                if not release.wait(10):
                    raise ValidationError('Replay scheduling barrier timed out')
            if request['mode'] == 'cancel':
                cancel_started.set()
                if not cancel_release.wait(10):
                    raise ValidationError('Replay cancellation barrier timed out')
            return context.store.put_json(request)
        jobs_receipt = []
        with JobManager(store, workers=2) as jobs:
            jobs.register('local.replay.supplied', handler)
            request = {'mode': 'old', 'source': sequence, 'value': 7}
            old_id = jobs.submit('local.replay.supplied', request, head='accepted')
            try:
                if not started.wait(10):
                    raise ValidationError('Replay worker did not start')
                request['value'] = 99
                new = jobs.wait(jobs.submit('local.replay.supplied', {'mode': 'new', 'source': sequence}, head='accepted'))
                release.set()
                old = jobs.wait(old_id)
                check('request_is_frozen', jobs.request(old_id)['value'] == 7)
                check('old_completion_quarantined', old['status'] == 'stale' and old['outputs'][0]['disposition'] == 'quarantined')
                check('newer_result_remains_published', store.get_head('accepted') == new['artifact'])
                cancelled_id = jobs.submit('local.replay.supplied', {'mode': 'cancel', 'source': sequence}, head='cancelled')
                if not cancel_started.wait(10):
                    raise ValidationError('Replay cancel worker did not start')
                jobs.cancel(cancelled_id)
                cancel_release.set()
                cancelled = jobs.wait(cancelled_id)
                check('cancelled_candidate_quarantined', cancelled['status'] == 'cancelled' and cancelled['outputs'][0]['disposition'] == 'quarantined')
                check('cancel_does_not_publish', store.get_head('cancelled') is None)
                jobs_receipt = [old, new, cancelled]
            finally:
                release.set()
                cancel_release.set()
        with JobManager(Store(store.path), workers=1) as fresh:
            check('job_records_survive_reload', len(fresh.list()) == 3 and fresh.get(old_id)['status'] == 'stale')
        (output / 'JOBS.json').write_text(json.dumps(jobs_receipt, indent=2) + '\n')
        registry = CapabilityRegistry()
        request = {'description': 'diagnostic', 'image_size': {'width': 64, 'height': 64}}
        check('captured_request_validates_offline', registry.validate_request('public:POST:/generate-image-v2', request))
        rejected('vendor_handler_explicitly_unsupported', lambda: registry.invoke('public:POST:/generate-image-v2', request), UnsupportedCapability)
        check('all_vendor_definitions_remain_unimplemented', len(registry.list()) == 212 and not any(r['handler_implemented'] for r in registry.list()))
        artifacts['published_document'] = store.get_head('accepted')
    exported = export_sequence(store, sequence, output / 'export', ['png', 'manifest', 'editable', 'review'])
    return {'artifacts': artifacts, 'checks': checks, 'inputs': inputs, 'routine_order': order,
            'exports': exported, 'limitations': ['Supplied diagnostic art only; no generation or visual approval.',
             'This local recipe exercises a bounded subset; full vendor flow and server semantics remain incomplete.',
             'UUIDs and job timestamps vary across fresh runs; input and sequence artifact hashes are comparable.']}

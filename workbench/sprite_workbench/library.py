"""Explicit supplied-art candidates and CAS revisioned local entity libraries.

Deletion is a tombstone, not blob destruction. Direction labels are supplied by
callers: response position never implies a cardinal direction or candidate ID.
"""
from __future__ import annotations

import copy
from fractions import Fraction
import math
import time
import uuid

from .core import Store, ValidationError, load_sequence, validate_id
from .jobs import _snapshot


def _label(value):
    if not isinstance(value,str) or not value or len(value)>128 or any(ord(c)<32 for c in value):
        raise ValidationError("Library label must be nonempty bounded text")
    return value


class StaleRevision(ValidationError):
    def to_dict(self): return {'status':'stale_revision','reason':str(self)}


class Library:
    def __init__(self, store: Store):
        self.store=store
        with store.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS local_library(
                id TEXT PRIMARY KEY, entity_kind TEXT NOT NULL, created REAL NOT NULL,
                archived INTEGER NOT NULL DEFAULT0, deleted INTEGER NOT NULL DEFAULT0)
                """.replace('DEFAULT0','DEFAULT 0'))

    def _art(self, ident, sequence=False):
        doc=self.store.get_json(validate_id(ident))
        if doc.get('kind')=='rgba' and not sequence:
            self.store.get_raster(ident)
        elif doc.get('kind')=='sequence':
            try:
                load_sequence(self.store,ident)
                frames=doc['frames']
                if not isinstance(frames,list) or not 1<=len(frames)<=512: raise ValueError()
                for index,frame in enumerate(frames):
                    duration=frame['duration'];pivot=frame['pivot']
                    if frame['index']!=index or type(frame['index']) is not int: raise ValueError()
                    if not isinstance(duration,list) or len(duration)!=2 or any(type(x) is not int for x in duration): raise ValueError()
                    if not 0<Fraction(*duration)<=3600: raise ValueError()
                    if not isinstance(pivot,list) or len(pivot)!=2 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in pivot): raise ValueError()
                    _label(frame['direction'])
                if type(doc['loop']) is not bool: raise ValueError()
            except (KeyError,TypeError,ValueError,ZeroDivisionError):
                raise ValidationError("Candidate sequence has invalid frame indexes/clock/pivot metadata") from None
        else:
            raise ValidationError("Candidate must reference RGBA or sequence art")
        return doc

    def create_candidate(self, artifact_id=None, *, source_id=None, status='candidate',
                         validation_status='passed', technical_status='unverified', visual_status='unreviewed', metadata=None):
        if status not in {'candidate','validation_error','technical_failure'}:
            raise ValidationError("Invalid candidate status")
        if validation_status not in {'passed','failed','unverified'} or technical_status not in {'verified','failed','unverified'} or visual_status not in {'approved','rejected','unreviewed'}:
            raise ValidationError("Invalid independent candidate review status")
        if status=='validation_error': validation_status='failed'
        if status=='technical_failure': technical_status='failed'
        if artifact_id is None and status=='candidate': raise ValidationError("Candidate art needs an explicit artifact")
        if artifact_id is not None:
            self._art(artifact_id)
        if source_id is not None: _label(source_id)
        return self.store.put_json({'kind':'library_candidate','version':1,'artifact':artifact_id,'source_id':source_id,
            'status':status,'validation_status':validation_status,'technical_status':technical_status,
            'visual_status':visual_status,'metadata':_snapshot({} if metadata is None else metadata)})

    def candidate(self, ident):
        doc=self.store.get_json(validate_id(ident))
        if doc.get('kind')!='library_candidate': raise ValidationError("Expected explicit candidate ID")
        return doc

    def record_review(self, ident, *, visual_status=None, technical_status=None, metadata=None):
        doc=self.candidate(ident)
        kwargs={k:doc[k] for k in ('source_id','status','validation_status','technical_status','visual_status')}
        if visual_status is not None: kwargs['visual_status']=visual_status
        if technical_status is not None: kwargs['technical_status']=technical_status
        result=self.create_candidate(doc['artifact'],**kwargs,metadata={**doc['metadata'],**_snapshot({} if metadata is None else metadata),'review_parent':ident})
        return result

    def select(self, candidate_ids, source_ids):
        candidates={}
        for ident in candidate_ids:
            doc=self.candidate(ident);source=doc['source_id']
            if source is None: raise ValidationError("Source-ID selection requires explicit source IDs")
            if source in candidates: raise ValidationError("Ambiguous duplicate source candidate ID")
            candidates[source]=ident
        if not source_ids or len(set(source_ids))!=len(source_ids): raise ValidationError("Select nonempty unique source IDs")
        try: return [candidates[source] for source in source_ids]
        except KeyError: raise ValidationError("Selected source candidate ID is absent") from None

    def _eligible(self, ident, sequence=False):
        doc=self.candidate(ident)
        if doc['status']!='candidate' or doc['validation_status']!='passed' or doc['technical_status']=='failed' or doc['visual_status']=='rejected':
            raise ValidationError("Failed/rejected candidate cannot be promoted")
        artifact=doc['artifact']
        self._art(artifact,sequence=sequence)
        return {'candidate_id':ident,'artifact_id':artifact,'source_id':doc['source_id'],
                'validation_status':doc['validation_status'],'technical_status':doc['technical_status'],'visual_status':doc['visual_status']}

    def _directions(self, mapping, sequence=False):
        if not isinstance(mapping,dict) or len(mapping)>256: raise ValidationError("Directions must be an explicit bounded mapping")
        return {_label(direction):self._eligible(ident,sequence) for direction,ident in mapping.items()}

    def promote(self, candidate_ids, *, name, entity_kind='object', directions=None, metadata=None):
        _label(name);_label(entity_kind)
        candidate_ids=list(candidate_ids)
        if not 1<=len(candidate_ids)<=512 or len(set(candidate_ids))!=len(candidate_ids):
            raise ValidationError("Promotion requires1..512 unique explicit candidate IDs")
        candidates=[self._eligible(ident) for ident in candidate_ids]
        directional=self._directions({} if directions is None else directions)
        if any(record['candidate_id'] not in candidate_ids for record in directional.values()):
            raise ValidationError("Promoted directions must use the explicitly selected candidates")
        doc={'kind':'library_entity','version':1,'origin':uuid.uuid4().hex,'name':name,'entity_kind':entity_kind,
             'candidates':candidates,'directions':directional,'states':{},'archived':False,'metadata':_snapshot({} if metadata is None else metadata)}
        ident=self.store.put_json(doc)
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT INTO local_library(id,entity_kind,created) VALUES(?,?,?)",(ident,entity_kind,time.time()))
            db.execute("INSERT INTO heads(name,artifact) VALUES(?,?)",(self._head(ident),ident));db.commit()
        return ident

    @staticmethod
    def _head(ident): return 'library:entity:'+validate_id(ident)

    def get(self, ident, *, include_deleted=False):
        head=self._head(ident)
        with self.store.connect() as db:
            db.execute('BEGIN')
            row=db.execute("SELECT deleted FROM local_library WHERE id=?",(ident,)).fetchone()
            revision=db.execute("SELECT artifact FROM heads WHERE name=?",(head,)).fetchone()
        if row is None or revision is None: raise ValidationError("Unknown local library entity")
        if row[0] and not include_deleted: raise ValidationError("Entity is deleted")
        return {'entity_id':ident,'revision_id':revision[0],'document':self.store.get_json(revision[0]),'deleted':bool(row[0])}

    def list(self, *, entity_kind=None, include_archived=False, include_deleted=False, limit=100, offset=0):
        if type(limit) is not int or not 1<=limit<=1000 or type(offset) is not int or offset<0:
            raise ValidationError("Invalid local library pagination")
        where=[];args=[]
        if entity_kind is not None: where.append('entity_kind=?');args.append(_label(entity_kind))
        if not include_archived: where.append('archived=0')
        if not include_deleted: where.append('deleted=0')
        with self.store.connect() as db:
            query="SELECT l.id,h.artifact,l.deleted FROM local_library l JOIN heads h ON h.name=('library:entity:'||l.id)"+(' WHERE '+' AND '.join(where) if where else '')+' ORDER BY created,id LIMIT ? OFFSET ?'
            rows=db.execute(query,(*args,limit,offset)).fetchall()
        return [{'entity_id':r[0],'revision_id':r[1],'document':self.store.get_json(r[1]),'deleted':bool(r[2])} for r in rows]

    def _update(self, ident, expected, mutate):
        validate_id(expected)
        current=self.get(ident)
        if current['revision_id']!=expected: raise StaleRevision("Library revision changed")
        doc=copy.deepcopy(current['document']);mutate(doc)
        revision=self.store.put_json(doc)
        self._publish(ident,revision,expected,doc)
        return revision

    def _publish(self, ident, revision, expected, doc):
        self.store.get_bytes(validate_id(revision));validate_id(expected)
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT artifact FROM heads WHERE name=?",(self._head(ident),)).fetchone()
            if row is None or row[0]!=expected: raise StaleRevision("Library revision changed")
            db.execute("UPDATE heads SET artifact=? WHERE name=?",(revision,self._head(ident)))
            db.execute("UPDATE local_library SET archived=?,deleted=? WHERE id=?",
                       (bool(doc.get('archived')),doc.get('kind')=='library_entity_deleted',ident));db.commit()

    def set_direction(self, ident, direction, candidate_id, *, expected):
        direction=_label(direction);record=self._eligible(candidate_id)
        return self._update(ident,expected,lambda doc:doc['directions'].__setitem__(direction,record))

    def set_state(self, ident, state, *, directions=None, metadata=None, expected):
        state=_label(state);records=self._directions({} if directions is None else directions);metadata=_snapshot({} if metadata is None else metadata)
        def mutate(doc):
            old=doc['states'].get(state,{'directions':{},'animations':{},'metadata':{}})
            doc['states'][state]={'directions':{**old['directions'],**records},'animations':old['animations'],'metadata':{**old['metadata'],**metadata}}
        return self._update(ident,expected,mutate)

    def set_animation(self, ident, state, animation, directions, *, expected, replace=False, metadata=None):
        state=_label(state);animation=_label(animation);records=self._directions(directions,sequence=True)
        if not records: raise ValidationError("Animation needs at least one labeled direction")
        if type(replace) is not bool: raise ValidationError("Animation replacement flag must be bool")
        metadata=_snapshot({} if metadata is None else metadata)
        def mutate(doc):
            if state not in doc['states']: raise ValidationError("Create state before adding animation")
            groups=doc['states'][state]['animations'];old=groups.get(animation,{'directions':{},'metadata':{}})
            groups[animation]={'directions':records if replace else {**old['directions'],**records},'metadata':{**old['metadata'],**metadata}}
        return self._update(ident,expected,mutate)

    def remove_direction(self, ident, direction, *, expected):
        def mutate(doc):
            if direction not in doc['directions']: raise ValidationError("Direction absent")
            del doc['directions'][direction]
        return self._update(ident,expected,mutate)

    def remove_animation(self, ident, state, animation, *, expected, direction=None):
        def mutate(doc):
            try:
                group=doc['states'][state]['animations'][animation]
                if direction is None: del doc['states'][state]['animations'][animation]
                else:
                    del group['directions'][direction]
                    if not group['directions']: del doc['states'][state]['animations'][animation]
            except KeyError: raise ValidationError("State/animation direction absent") from None
        return self._update(ident,expected,mutate)

    def remove_state(self, ident, state, *, expected):
        def mutate(doc):
            if state not in doc['states']: raise ValidationError("State absent")
            del doc['states'][state]
        return self._update(ident,expected,mutate)

    def archive(self, ident, *, expected, archived=True):
        if type(archived) is not bool: raise ValidationError("Archive flag must be bool")
        return self._update(ident,expected,lambda doc:doc.__setitem__('archived',archived))

    def delete(self, ident, *, expected):
        def mutate(doc):
            doc.clear();doc.update({'kind':'library_entity_deleted','version':1,'origin':self.store.get_json(ident)['origin'],
                                   'previous_revision':expected,'archived':False})
        return self._update(ident,expected,mutate)

    def restore(self, ident, revision, *, expected):
        current=self.get(ident,include_deleted=True)
        if current['revision_id']!=expected: raise StaleRevision("Library revision changed")
        doc=self.store.get_json(validate_id(revision))
        origin=self.store.get_json(ident).get('origin')
        if doc.get('kind')!='library_entity' or doc.get('origin')!=origin:
            raise ValidationError("Restore revision must belong to this entity")
        self._publish(ident,revision,expected,doc)
        return revision

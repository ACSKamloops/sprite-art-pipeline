"""Durable local jobs with immutable inputs and atomic guarded publication.

This is a local policy, not an emulation of PixelLab's cloud scheduler. Registered
handlers are trusted Python code. Cancellation is cooperative; late results are
retained as quarantined artifacts rather than published.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import fcntl
import json
import math
import sqlite3
import threading
import time
import uuid

from .core import Store, ValidationError, UnsupportedCapability, canonical_json, validate_id

TERMINAL = frozenset({"completed", "stale", "cancelled", "interrupted", "validation_error", "unsupported", "technical_failure"})
RESULT_STATUSES = frozenset({"candidate", "technically_verified", "visual_unreviewed", "visually_approved", "visually_rejected", "technical_failure", "validation_error", "unsupported"})
_CREDENTIAL_KEYS = {"secret", "password", "api_key", "apikey", "access_token", "refresh_token", "authorization", "bearer_token"}


def _snapshot(value):
    if not isinstance(value, dict):
        raise ValidationError("Local job request must be a JSON object")
    def check(node):
        if isinstance(node, dict):
            for key, child in node.items():
                if not isinstance(key, str):
                    raise ValidationError("Request keys must be strings")
                if key.lower() in _CREDENTIAL_KEYS:
                    raise ValidationError("Credentials are not accepted by local job requests")
                check(child)
        elif isinstance(node, (list, tuple)):
            for child in node: check(child)
    check(value)
    raw = canonical_json(value)
    if len(raw) > 4 * 1024 * 1024:
        raise ValidationError("Local job request exceeds4MiB; use artifact IDs")
    return json.loads(raw)


def _name(value):
    if not isinstance(value, str) or not value or len(value) > 128:
        raise ValidationError("Handler name must be nonempty text up to128characters")
    return value


def _timeout(value):
    if (isinstance(value,bool) or not isinstance(value,(int,float)) or value < 0
            or value > threading.TIMEOUT_MAX or not math.isfinite(value)):
        raise ValidationError("Timeout must be finite and within the platform's nonnegative wait range")
    return value


@dataclass(frozen=True)
class JobResult:
    artifact_id: str
    result_status: str = "candidate"
    metadata: dict = field(default_factory=dict)


class JobCancelled(Exception):
    pass


class JobContext:
    def __init__(self, manager, job_id):
        self._manager, self.job_id, self.store = manager, job_id, manager.store

    @property
    def cancelled(self):
        job = self._manager.get(self.job_id)
        return job["cancel_requested"] or job["status"] in {"cancelled", "interrupted"} or self._manager._closed

    def check_cancel(self):
        if self.cancelled: raise JobCancelled()

    def progress(self, fraction, detail=None):
        self.check_cancel()
        if isinstance(fraction, bool) or not isinstance(fraction, (int, float)) or not math.isfinite(fraction) or not 0 <= fraction <= 1:
            raise ValidationError("Progress must be a finite fraction0..1")
        detail = _snapshot({} if detail is None else detail)
        self._manager._progress(self.job_id, float(fraction), detail)


class JobManager:
    def __init__(self, store: Store, workers=4, max_pending=256):
        if type(workers) is not int or not 1 <= workers <= 32 or type(max_pending) is not int or max_pending < workers:
            raise ValidationError("Use1..32workers and max_pending>=workers")
        self.store, self.workers, self.max_pending = store, workers, max_pending
        self.owner = uuid.uuid4().hex
        self._handlers, self._callbacks = {}, {}
        self._condition = threading.Condition()
        self._closed = self._stopping = False
        self._lease = open(store.path / ".local-job-manager.lock", "a+b")
        try:
            fcntl.flock(self._lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._lease.close()
            raise ValidationError("A job manager already owns this workspace") from None
        try:
            with store.connect() as db:
                db.executescript("""
                    CREATE TABLE IF NOT EXISTS local_jobs(
                        id TEXT PRIMARY KEY, handler TEXT NOT NULL, request_id TEXT NOT NULL,
                        status TEXT NOT NULL, created REAL NOT NULL, updated REAL NOT NULL,
                        owner TEXT, progress REAL NOT NULL DEFAULT0, cancel_requested INTEGER NOT NULL DEFAULT0,
                        head TEXT, expected TEXT, retry_of TEXT, attempt INTEGER NOT NULL,
                        artifact TEXT, result_status TEXT, error TEXT, metadata TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS local_job_events(
                        seq INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL,
                        time REAL NOT NULL, event TEXT NOT NULL, detail TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS local_job_outputs(
                        seq INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL,
                        artifact TEXT NOT NULL, result_status TEXT NOT NULL,
                        disposition TEXT NOT NULL, time REAL NOT NULL, metadata TEXT NOT NULL);
                    CREATE UNIQUE INDEX IF NOT EXISTS local_job_retry_once
                        ON local_jobs(retry_of) WHERE retry_of IS NOT NULL;
                """.replace("DEFAULT0", "DEFAULT 0"))
                db.execute("BEGIN IMMEDIATE")
                now = time.time()
                abandoned = db.execute("SELECT id FROM local_jobs WHERE status IN ('running','cancel_requested')").fetchall()
                for (ident,) in abandoned:
                    db.execute("UPDATE local_jobs SET status='interrupted',cancel_requested=1,updated=?,error=? WHERE id=?",
                               (now, json.dumps({"status":"interrupted","reason":"Previous manager stopped before terminal commit"}), ident))
                    self._event(db, ident, "recovered_interrupted", {})
                db.commit()
        except Exception:
            self._lease.close()
            raise
        self._threads = [threading.Thread(target=self._worker, name=f"local-job-{i}", daemon=True) for i in range(workers)]
        for thread in self._threads: thread.start()

    @staticmethod
    def _event(db, ident, event, detail):
        db.execute("INSERT INTO local_job_events(job_id,time,event,detail) VALUES(?,?,?,?)", (ident,time.time(),event,canonical_json(detail).decode()))

    def register(self, name, handler):
        _name(name)
        if not callable(handler): raise ValidationError("Local handler must be callable")
        with self._condition:
            if self._stopping: raise ValidationError("Manager is closed")
            if name in self._handlers: raise ValidationError("Handler already registered")
            self._handlers[name] = handler
            self._condition.notify_all()

    def submit(self, name, request, *, head=None, expected=None, on_progress=None, metadata=None):
        return self._submit(name, request, head, expected, on_progress, {} if metadata is None else metadata, None, 1)

    def _submit(self, name, request, head, expected, callback, metadata, retry_of, attempt):
        _name(name)
        if head is not None and (not isinstance(head,str) or not head or len(head)>256):
            raise ValidationError("Publication head must be nonempty bounded text")
        if head is not None and head.startswith('library:entity:'):
            raise ValidationError("Library revisions require explicit Library mutation, not raw job publication")
        if head is None and expected is not None: raise ValidationError("Expected revision requires a head")
        if expected is not None: self.store.get_bytes(validate_id(expected))
        if callback is not None and not callable(callback): raise ValidationError("Progress callback must be callable")
        request = _snapshot(request); metadata = _snapshot(metadata)
        with self._condition:
            if self._stopping: raise ValidationError("Manager is closed")
            if name not in self._handlers: raise UnsupportedCapability(name,"No registered local handler")
            request_id = self.store.put_json({"kind":"job_request","version":1,"handler":name,"request":request})
            ident = uuid.uuid4().hex
            with self.store.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                if retry_of is not None:
                    previous=db.execute("SELECT id FROM local_jobs WHERE retry_of=?",(retry_of,)).fetchone()
                    if previous is not None: return previous[0]
                active = db.execute("SELECT count(*) FROM local_jobs WHERE status IN ('queued','running','cancel_requested')").fetchone()[0]
                if active >= self.max_pending: raise ValidationError("Local queue admission limit reached")
                now=time.time()
                db.execute("INSERT INTO local_jobs(id,handler,request_id,status,created,updated,head,expected,retry_of,attempt,metadata) VALUES(?,?,?,'queued',?,?,?,?,?,?,?)",
                           (ident,name,request_id,now,now,head,expected,retry_of,attempt,canonical_json(metadata).decode()))
                self._event(db,ident,"queued",{"request_id":request_id,"retry_of":retry_of,"attempt":attempt})
                db.commit()
            if callback is not None: self._callbacks[ident]=callback
            self._condition.notify_all()
        return ident

    def get(self, ident):
        with self.store.connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM local_jobs WHERE id=?",(ident,)).fetchone()
            if row is None: raise ValidationError("Unknown local job")
            result=dict(row)
            for key in ('metadata','error'):
                result[key]=json.loads(result[key]) if result[key] is not None else None
            result['cancel_requested']=bool(result['cancel_requested'])
            result['outputs']=[{'artifact_id':r[0],'result_status':r[1],'disposition':r[2],'time':r[3],'metadata':json.loads(r[4])}
                for r in db.execute("SELECT artifact,result_status,disposition,time,metadata FROM local_job_outputs WHERE job_id=? ORDER BY seq",(ident,))]
            return result

    def request(self, ident):
        return self.store.get_json(self.get(ident)['request_id'])['request']

    def list(self, status=None, *, limit=100, offset=0):
        if type(limit) is not int or not 1<=limit<=1000 or type(offset) is not int or offset<0:
            raise ValidationError("Invalid local pagination")
        with self.store.connect() as db:
            if status is None: rows=db.execute("SELECT id FROM local_jobs ORDER BY created,id LIMIT ? OFFSET ?",(limit,offset)).fetchall()
            else: rows=db.execute("SELECT id FROM local_jobs WHERE status=? ORDER BY created,id LIMIT ? OFFSET ?",(status,limit,offset)).fetchall()
        return [self.get(row[0]) for row in rows]

    def events(self, ident):
        self.get(ident)
        with self.store.connect() as db:
            return [{'seq':r[0],'time':r[1],'event':r[2],'detail':json.loads(r[3])} for r in
                db.execute("SELECT seq,time,event,detail FROM local_job_events WHERE job_id=? ORDER BY seq",(ident,))]

    def cancel(self, ident):
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT status FROM local_jobs WHERE id=?",(ident,)).fetchone()
            if row is None: raise ValidationError("Unknown local job")
            if row[0] in TERMINAL: return False
            status='cancelled' if row[0]=='queued' else 'cancel_requested'
            db.execute("UPDATE local_jobs SET status=?,cancel_requested=1,updated=? WHERE id=?",(status,time.time(),ident))
            self._event(db,ident,"cancel_requested",{"status":status});db.commit()
        with self._condition: self._condition.notify_all()
        return True

    def retry(self, ident, *, on_progress=None):
        job=self.get(ident)
        if job['status'] not in {'technical_failure','interrupted','cancelled','stale'}:
            raise ValidationError("Only failed/interrupted/cancelled/stale jobs may be retried")
        return self._submit(job['handler'],self.request(ident),job['head'],job['expected'],on_progress,job['metadata'],ident,job['attempt']+1)

    def wait(self, ident, timeout=30):
        deadline=time.monotonic()+_timeout(timeout)
        with self._condition:
            while True:
                job=self.get(ident)
                if job['status'] in TERMINAL: return job
                remaining=deadline-time.monotonic()
                if remaining<=0: raise TimeoutError("Local job still active")
                self._condition.wait(min(remaining,.1))

    def _claim(self):
        with self._condition:
            if self._stopping or not self._handlers: return None
            names=tuple(self._handlers)
            with self.store.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                placeholders=','.join('?' for _ in names)
                row=db.execute(f"SELECT id,handler,request_id FROM local_jobs WHERE status='queued' AND handler IN ({placeholders}) ORDER BY created,id LIMIT1".replace('LIMIT1','LIMIT 1'),names).fetchone()
                if row is None: return None
                db.execute("UPDATE local_jobs SET status='running',owner=?,updated=? WHERE id=?",(self.owner,time.time(),row[0]))
                self._event(db,row[0],"started",{"owner":self.owner});db.commit()
                return row,self._handlers[row[1]]

    def _progress(self, ident, fraction, detail):
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT status,cancel_requested,owner,progress FROM local_jobs WHERE id=?",(ident,)).fetchone()
            if row is None or row[0]!='running' or row[1] or row[2]!=self.owner: raise JobCancelled()
            if fraction<row[3]: raise ValidationError("Progress cannot move backward")
            db.execute("UPDATE local_jobs SET progress=?,updated=? WHERE id=?",(fraction,time.time(),ident))
            self._event(db,ident,"progress",{"fraction":fraction,"detail":detail});db.commit()
        callback=self._callbacks.get(ident)
        if callback:
            try: callback({'job_id':ident,'fraction':fraction,'detail':detail})
            except Exception as e:
                with self.store.connect() as db: self._event(db,ident,"callback_error",{"type":type(e).__name__})

    def _finish(self, ident, result=None, error=None):
        if result is not None:
            if isinstance(result,str): result=JobResult(result)
            if not isinstance(result,JobResult): raise ValidationError("Handler must return JobResult or artifact ID")
            self.store.get_bytes(validate_id(result.artifact_id))
            if result.result_status not in RESULT_STATUSES: raise ValidationError("Invalid result classification")
            metadata=_snapshot(result.metadata)
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT status,cancel_requested,owner,head,expected,progress FROM local_jobs WHERE id=?",(ident,)).fetchone()
            if row is None: raise ValidationError("Missing job during terminal commit")
            owned=row[2]==self.owner and row[0] in {'running','cancel_requested'}
            cancelled=bool(row[1]) or self._closed or not owned
            status=row[0] if not owned else 'cancelled' if cancelled else 'completed'
            disposition='quarantined' if cancelled else 'candidate'
            rejected=result is not None and result.result_status in {'technical_failure','validation_error','visually_rejected','unsupported'}
            if rejected and not cancelled:
                disposition='quarantined'
                if result.result_status in {'technical_failure','validation_error','unsupported'}: status=result.result_status
            if result is not None and not cancelled and not rejected and row[3] is not None:
                old=db.execute("SELECT artifact FROM heads WHERE name=?",(row[3],)).fetchone()
                if (old[0] if old else None)!=row[4]: status,disposition='stale','quarantined'
                else:
                    db.execute("INSERT INTO heads(name,artifact) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET artifact=excluded.artifact",(row[3],result.artifact_id))
                    disposition='published'
            if result is not None:
                db.execute("INSERT INTO local_job_outputs(job_id,artifact,result_status,disposition,time,metadata) VALUES(?,?,?,?,?,?)",
                           (ident,result.artifact_id,result.result_status,disposition,time.time(),canonical_json(metadata).decode()))
            if error is not None and owned and not cancelled:
                status=error.get('status','technical_failure')
            if owned:
                db.execute("UPDATE local_jobs SET status=?,updated=?,artifact=?,result_status=?,error=?,progress=? WHERE id=?",
                    (status,time.time(),result.artifact_id if result else None,result.result_status if result else None,
                     canonical_json(error).decode() if error else None,1.0 if result and status=='completed' else row[5],ident))
            self._event(db,ident,"terminal" if owned else "late_quarantine",{'status':status,'disposition':disposition,'artifact_id':result.artifact_id if result else None})
            db.commit()
        with self._condition: self._condition.notify_all()
        self._callbacks.pop(ident,None)

    def _worker(self):
        while True:
            claimed=self._claim()
            if claimed is None:
                with self._condition:
                    if self._stopping: return
                    self._condition.wait(.1)
                continue
            (ident,_,request_id),handler=claimed
            try:
                request=self.store.get_json(request_id)['request']
                result=handler(request,JobContext(self,ident))
                self._finish(ident,result=result)
            except JobCancelled:
                self._finish(ident,error={'status':'cancelled','reason':'Cooperative cancellation'})
            except UnsupportedCapability as e:
                self._finish(ident,error=e.to_dict())
            except ValidationError as e:
                self._finish(ident,error=e.to_dict())
            except Exception as e:
                self._finish(ident,error={'status':'technical_failure','reason':str(e),'type':type(e).__name__})

    def close(self, wait=True, timeout=5):
        if type(wait) is not bool: raise ValidationError("Shutdown wait flag must be bool")
        timeout=_timeout(timeout)
        with self._condition:
            if self._closed: return
            self._stopping=True;self._condition.notify_all()
        if wait:
            deadline=time.monotonic()+timeout
            for thread in self._threads: thread.join(max(0,deadline-time.monotonic()))
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            rows=db.execute("SELECT id FROM local_jobs WHERE owner=? AND status IN ('running','cancel_requested')",(self.owner,)).fetchall()
            for (ident,) in rows:
                db.execute("UPDATE local_jobs SET status='interrupted',cancel_requested=1,updated=?,error=? WHERE id=?",
                    (time.time(),json.dumps({'status':'interrupted','reason':'Manager closed before result commit'}),ident))
                self._event(db,ident,"manager_interrupted",{})
            db.commit()
        self._closed=True
        self._lease.close()
        with self._condition: self._condition.notify_all()

    def __enter__(self): return self
    def __exit__(self,*args): self.close()

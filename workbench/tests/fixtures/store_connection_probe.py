"""Bounded process-local SQLite FD measurement; no GC or descriptor exhaustion."""
import gc
import json
import os
from pathlib import Path
import sys
import tempfile

from sprite_workbench.core import Store


def handles(store):
    out=[]
    for p in Path('/proc/self/fd').iterdir():
        try:target=os.readlink(p)
        except FileNotFoundError:continue
        if target.startswith(str(store.db_path)):out.append(target)
    return out


with tempfile.TemporaryDirectory(prefix='pixellab-store-fd-review-') as temp:
    store=Store(temp);ident=store.put_json({'fixture':'descriptor-control'})
    assert store.set_head('accepted',ident,None)
    gc.collect();gc.disable()
    before=len(handles(store));counts=[]
    try:
        for _ in range(32):
            assert store.get_head('accepted')==ident
            counts.append(len(handles(store)))
        rollback=False
        try:
            with store.connect() as db:
                db.execute("UPDATE heads SET artifact=? WHERE name='accepted'",('0'*64,))
                raise RuntimeError('controlled rollback')
        except RuntimeError:rollback=store.get_head('accepted')==ident
        result={'operations':32,'gc_disabled':True,'before_store_fds':before,
                'after_each_get_head':counts,'after_rollback_check':len(handles(store)),
                'rollback_preserved_head':rollback,'scope':'bounded descriptor/transaction control; no exhaustion attempt'}
        Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result))
    finally:gc.enable();gc.collect()

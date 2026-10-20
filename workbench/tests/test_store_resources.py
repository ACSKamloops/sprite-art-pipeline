"""Durable repeated operations must not rely on garbage collection to release FDs."""
import gc
from pathlib import Path
import pytest
from sprite_workbench.core import Store


def test_store_repeated_connections_release_descriptors_even_without_gc(tmp_path):
    store=Store(tmp_path);ident=store.put_json({'value':1})
    assert store.set_head('accepted',ident,None)
    def handles():
        count=0
        for entry in Path('/proc/self/fd').iterdir():
            try:target=entry.resolve(strict=True)
            except FileNotFoundError:continue
            if str(target).startswith(str(store.db_path)):count+=1
        return count
    before=handles();was_enabled=gc.isenabled();gc.disable()
    try:
        for _ in range(128):assert store.get_head('accepted')==ident
        assert handles()<=before+1
        with pytest.raises(RuntimeError):
            with store.connect() as db:
                db.execute("UPDATE heads SET artifact=? WHERE name='accepted'",('0'*64,))
                raise RuntimeError('Controlled transaction failure')
        assert store.get_head('accepted')==ident
        assert handles()<=before+1
    finally:
        if was_enabled:gc.enable()

"""Behavior checks: process races, ownership, stale inputs, dishonest completion."""
import concurrent.futures
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import work_queue as queue


def worker(pair):
    dbpath,identity=pair;db=queue.connect(dbpath)
    try:return queue.claim(db,identity)
    finally:db.close()


class QueueChecks(unittest.TestCase):
    def test_process_race_and_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            dbpath=str(Path(folder)/'queue.sqlite');db=queue.connect(dbpath)
            cases=[{'id':f'case-{i:02}','scope':'one input and direction'} for i in range(24)]
            queue.register(db,cases)
            with concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool:
                claims=list(pool.map(worker,[(dbpath,f'worker-{i}') for i in range(48)]))
            claimed=[r for r in claims if r]
            self.assertEqual(len(claimed),24);self.assertEqual(len({r['case']['id'] for r in claimed}),24)
            c=claimed[0];case=c['case']['id'];evidence=Path(folder)/'evidence.txt';evidence.write_text('actual bounded result')
            receipt={'input_fingerprint':c['input_fingerprint'],'scope_status':'observed_partial','limits':['One case only'],'evidence':[{'path':str(evidence),'sha256':hashlib.sha256(evidence.read_bytes()).hexdigest()}]}
            for changes in ({'input_fingerprint':'old'},{'scope_status':'all_game_complete'},{'evidence':[]},{'causal_claim':True},
                            {'causal_claim':True,'static_analysis':True,'executed_trace':True,'controlled_intervention':True,'displayed_frame_check':True}):
                with self.assertRaises(ValueError):queue.complete(db,case,c['owner'],c['token'],{**receipt,**changes})
            with self.assertRaises(ValueError):queue.complete(db,case,'other-worker',c['token'],receipt)
            evidence.write_text('edited after receipt')
            with self.assertRaises(ValueError):queue.complete(db,case,c['owner'],c['token'],receipt)
            evidence.write_text('actual bounded result');queue.complete(db,case,c['owner'],c['token'],receipt)
            with self.assertRaises(ValueError):queue.register(db,[{**c['case'],'scope':'different input'}])
            second=claimed[1]
            with self.assertRaises(ValueError):queue.release(db,second['case']['id'],'other',second['token'],'worker recovery')
            queue.release(db,second['case']['id'],second['owner'],second['token'],'checkpointed work; worker stopping')
            recovered=queue.claim(db,'replacement')
            self.assertEqual(recovered['case']['id'],second['case']['id'])
            self.assertNotEqual(recovered['token'],second['token'])
            with self.assertRaises(ValueError):queue.complete(db,second['case']['id'],second['owner'],second['token'],receipt)
            db.close()


if __name__=='__main__':unittest.main()

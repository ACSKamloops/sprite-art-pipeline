#!/usr/bin/env python3
"""Read-only structural/hash audit of a completed catalog."""
import argparse,hashlib,json,sqlite3
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('catalog',type=Path);a=p.parse_args();root=a.catalog;summary=json.loads((root/'summary.json').read_text());checks=[]
def check(label,ok):checks.append({'label':label,'passed':bool(ok)})
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for file,key in [('motions.sqlite','database_sha256'),('method-route-heatmap.csv','method_heatmap_sha256'),('method-route-heatmap-matrix.csv','matrix_sha256'),('route-coverage.csv','route_coverage_sha256')]:check(file+' hash binding',sha(root/file)==summary[key])
db=sqlite3.connect('file:'+str((root/'motions.sqlite').resolve())+'?mode=ro',uri=True)
check('SQLite integrity',db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
for table,count in summary['counts'].items():check(table+' row count',db.execute('SELECT count(*) FROM '+table).fetchone()[0]==count)
check('One selected actor row per source tick',db.execute('SELECT count(*) FROM frames f JOIN actor_frames a ON a.frame_id=f.id AND a.slot=f.actor_slot').fetchone()[0]==summary['counts']['frames'])
check('No missing relative tick',db.execute('SELECT count(*) FROM (SELECT route_id,count(*) n,max(relative_tick)+1 m,min(relative_tick) z FROM frames GROUP BY route_id HAVING n!=m OR z!=0)').fetchone()[0]==0)
check('Source ticks never flattened',db.execute('SELECT count(*) FROM frames f JOIN routes r ON r.id=f.route_id WHERE f.source_tick!=r.first_tick+f.relative_tick').fetchone()[0]==0)
known=[int(pc,16)for pc in json.loads(db.execute("SELECT value FROM metadata WHERE key='contracts'").fetchone()[0])]
check('Known owner PCs have hash-bound evidence',db.execute('SELECT count(*) FROM method_hits WHERE contract_id=1 AND pc NOT IN ('+','.join('?'for _ in known)+')',known).fetchone()[0]==0)
check('Unknown owners never get a slot',db.execute('SELECT count(*) FROM method_hits WHERE contract_id=0 AND owner_slot IS NOT NULL').fetchone()[0]==0)
check('Known entry owners match X and slot alignment',db.execute('SELECT count(*) FROM method_hits WHERE contract_id=1 AND (owner_slot!=x OR x%512!=0 OR x<0 OR x>7680)').fetchone()[0]==0)
check('Missing trace routes preserve unknown missed count',db.execute('SELECT count(*) FROM routes WHERE trace_present=0 AND trace_missed_ticks IS NOT NULL').fetchone()[0]==0)
check('Selection runs cover every selected frame exactly once',db.execute('SELECT sum(last_relative_tick-first_relative_tick+1) FROM selection_runs').fetchone()[0]==summary['counts']['frames'])
check('All event count aggregates match frame count readback',db.execute('SELECT count(*) FROM frames f WHERE f.trace_event_count!=coalesce((SELECT sum(event_count) FROM method_hits h WHERE h.route_id=f.route_id AND h.relative_tick=f.relative_tick),0)').fetchone()[0]==0)
report={'schema':'native-motion-index-audit/v1','passed':all(c['passed']for c in checks),'database_sha256':summary['database_sha256'],'checks':checks,'coverage':summary['counts'],'trace_present_routes':db.execute('SELECT count(*) FROM routes WHERE trace_present=1').fetchone()[0],'trace_absent_routes':db.execute('SELECT count(*) FROM routes WHERE trace_present=0').fetchone()[0],'ticks_without_selected_PC_events':db.execute('SELECT count(*) FROM frames WHERE trace_event_count=0').fetchone()[0],'recorded_PC_events':db.execute('SELECT sum(event_count) FROM method_hits').fetchone()[0],'known_owner_entry_events':db.execute('SELECT sum(event_count) FROM method_hits WHERE contract_id=1').fetchone()[0],'unknown_owner_events':db.execute('SELECT sum(event_count) FROM method_hits WHERE contract_id=0').fetchone()[0]};print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed']else 2)

#!/usr/bin/env python3
"""Core API cross-check on actual indexed game source, not implementation mirrors."""
import json,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sprite_lab import validate_project,render_frame,project_hash,apply_transaction,History,export_ora,import_ora
from audit import scalar
BASE=Path(__file__).resolve().parent;issues=[];checks=0;bindings=[]
def check(name,ok):
 global checks
 checks+=1
 if not ok:issues.append(name)
for d in sorted((BASE/'fixtures').iterdir()):
 p=json.loads((d/'project.json').read_text());validate_project(p);b=json.loads((d/'bindings.json').read_text());bindings.append({'fixture':d.name,'canonical_project_sha256':project_hash(p),'file_sha256':__import__('hashlib').sha256((d/'project.json').read_bytes()).hexdigest()})
 for f in b['frames']:check(d.name+'/'+f['frame_id']+' coreRGBA vs scalar raw hardware',render_frame(p,f['frame_id']).tobytes()==scalar(d/f['raw']).tobytes())
# A genuinely visible foreground native weapon pixel. Preserve source and edit only explicit mask.
d=BASE/'fixtures/randi-right-sword-native';p=json.loads((d/'project.json').read_text());frame=p['frames'][5];cid=frame['cels'][p['layers'][-1]['id']];cel=p['cels'][cid];k=next(i for i,v in enumerate(cel['pixels'])if v);xy=[k%256,k//256];old=cel['pixels'][k];new=next(i for i,c in enumerate(p['palette'])if i and i!=old and c!=p['palette'][old]);tx={'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(p),'reason':'Demonstrate precise one-pixel edit on original-game control; no art acceptance','operations':[{'op':'paint','cel_id':cid,'points':[[*xy,new]],'mask':[xy]}]};result=apply_transaction(p,tx);live=result['project']
check('transaction input source unchanged',project_hash(p)==tx['expected_project_sha256']);check('all timing pivots events landmarks unchanged',live['canvas']==p['canvas']and live['animations']==p['animations']and[(f['id'],f['duration_ticks'],f['landmarks'])for f in live['frames']]==[(f['id'],f['duration_ticks'],f['landmarks'])for f in p['frames']]);check('exact one indexed pixel changed',[(c,i)for c in p['cels']for i,(a,b)in enumerate(zip(p['cels'][c]['pixels'],live['cels'][c]['pixels']))if a!=b]==[(cid,k)])
changed=[]
for f in p['frames']:
 before=render_frame(p,f['id']).tobytes();after=render_frame(live,f['id']).tobytes();coords=[(i%256,i//256)for i in range(256*224)if before[i*4:i*4+4]!=after[i*4:i*4+4]]
 check(f['id']+' localized visible RGBA delta',all(list(pos)==xy for pos in coords))
 if coords:changed.append(f['id'])
check('paint changes a visible native pixel',bool(changed));history=History(p);history.apply(tx);check('undo restores raw native exact source',project_hash(history.undo())==project_hash(p));check('redo restores exact edited result',project_hash(history.redo())==project_hash(live));check('journal replay exact result',project_hash(History.replay(p,history.journal()).project)==project_hash(live))
out=BASE/'live-examples';out.mkdir(exist_ok=True)
for name,data in [('transaction.json',tx),('receipt.json',result['receipt']),('live.json',live),('journal.json',history.journal())]:(out/name).write_text(json.dumps(data,separators=(',',':'))+'\n')
ora=out/'native-edited.ora';export_ora(live,frame['id'],ora);reopened=import_ora(ora);check('core ORA reopens exact edited project',project_hash(reopened)==project_hash(live));check('core ORA reopens visible edit exactRGBA',render_frame(reopened,frame['id']).tobytes()==render_frame(live,frame['id']).tobytes())
report={'passed':not issues,'checks':checks,'issues':issues,'native_fixture_bindings':bindings,'actual_edit':{'cel_id':cid,'coordinate':xy,'before_palette_index':old,'after_palette_index':new,'affected_frame_ids':changed,'scope':'Precise pixel mechanics demonstrated on original game control, not a new-art quality approval.'},'core_source_sha256':{n:__import__('hashlib').sha256((BASE.parent/n).read_bytes()).hexdigest()for n in ['sprite_lab/core.py','sprite_lab/canonical.py','sprite_lab/export.py']}};(BASE/'core-crosscheck-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':checks,'issues':issues,'edit':report['actual_edit']}));sys.exit(0 if report['passed']else 1)

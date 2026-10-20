#!/usr/bin/env python3
"""Capture-backed native timing/event rules, with ROM byte provenance.
No hit window inferred from sword art. Real damage event is separately observed.
"""
import hashlib,json,sys
from pathlib import Path
from audit import scalar
BASE=Path(__file__).resolve().parent
rom=Path(sys.argv[1] if len(sys.argv)>1 else '/home/astra/artifacts/rea-som-test-2026-10-07/roms/Secret of Mana (USA).sfc').read_bytes();assert hashlib.sha256(rom).hexdigest()=='4c15013131351e694e05f22e38bb1b3e4031dedac77ec75abecebe8520d82d5f'
checks=[]
def check(name,condition,evidence):checks.append({'name':name,'passed':bool(condition),'evidence':evidence})
def bindings(name):return json.loads((BASE/'fixtures'/name/'bindings.json').read_text())['frames']
def runs(entries,key):
 result=[]
 for e in entries:
  value=e['native'][key]
  if result and result[-1]['value']==value:result[-1]['duration_ticks']+=1
  else:result.append({'source_tick':e['source_tick'],'value':value,'duration_ticks':1})
 return result
attack=bindings('randi-right-sword-native');walk=bindings('randi-right-walk-native');near=bindings('randi-sword-near-down-native')
check('ROM normal far right Sword script frame words',rom[0x116a96:0x116aa2]==bytes.fromhex('8df903001cab18ac18ad83ff'),{'offset':'0x116A96','bytes':rom[0x116a96:0x116aa2].hex(),'note':'8D/F9/83 are helper commands, not extra pose holds or collision hit-window declarations.'})
active=[e for e in attack if e['native']['script_start']==0x6a96]
check('Native selected normal Sword poses171/172/173 hold five video ticks each',[(r['value'],r['duration_ticks'])for r in runs(active,'generic_index')]==[(171,5),(172,5),(173,5)],runs(active,'generic_index'))
cal=BASE/'source-receipts/right-sword-v1-calibration.json';c=json.loads(cal.read_text());bytick={r['tick']:r for r in c['rows']}
released=[e for e in active if not bytick[e['source_tick']]['keys']]
check('Releasing B does not cut this native20 action before parser completion',len(released)==14 and all(e['native']['mode']==0x20 for e in released),{'B_press_ticks':[r['tick']for r in c['rows']if r['keys']==['b']],'released_action_ticks':[e['source_tick']for e in released],'completion_tick':next(e['source_tick']for e in attack if e['source_tick']>active[-1]['source_tick']and e['native']['mode']==0),'limits':'Observed branch only; no general cancellation/AI/gameplay dispatcher inferred.'})
check('Completed native far Sword switches mode20 to0 and reselects idle',attack[-3]['native']['mode']==0 and attack[-3]['native']['script_start']==0x5c1c,{'tick':attack[-3]['source_tick'],'native':attack[-3]['native']})
# Selection is current WRAM, hardware is one video phase later; retain this distinction.
check('One complete walk cycle selected in six five-video-tick runs',[(r['value'],r['duration_ticks'])for r in runs(walk[:-1],'generic_index')][:5]==[(251,4),(252,5),(35,5),(254,5),(253,5)] and walk[-1]['native']['generic_index']==251,{'WRAM_runs':runs(walk,'generic_index'),'note':'Window is presented cycle13922..13951. Current WRAM selection leads the presented body by one video tick; never relabel hardware from current WRAM.'})
shown=[]
for e in walk:
 h=hashlib.sha256(scalar(BASE/'fixtures/randi-right-walk-native'/e['raw']).tobytes()).hexdigest()
 if shown and shown[-1]['pixel_sha256']==h:shown[-1]['duration_ticks']+=1
 else:shown.append({'source_tick':e['source_tick'],'duration_ticks':1,'pixel_sha256':h})
check('Actually presented walk has six exact five-tick hardware pixel holds',len(shown)==6 and all(r['duration_ticks']==5 for r in shown),shown)
check('Near native damage observation is20 to2 at13860',next((e['source_tick']for e in near if e['native']['enemy_slot_0800_hp']==2),None)==13860 and near[0]['native']['enemy_slot_0800_hp']==20,{'event':'observed_enemy_slot_0800_HP_20_to_2','source_tick':13860,'relative_tick':14,'note':'Native damage transition, not an inferred attack active interval.'})
report={'schema':'native-construction-rules/v1','passed':all(c['passed']for c in checks),'checks':checks,'rom_sha256':hashlib.sha256(rom).hexdigest(),'native_update_semantics':'C0F52D parser uses E012 hold counter; all three1C/18 Sword frame controls leave timer0, advancing next active player parser invocation. Recorded native video selection cadence is five ticks. F9 movement and8D palette helper add no invented pose tick. LiteralFF ends the special action and dynamically reselects; fixed native loop is not asserted.'};(BASE/'native-rules-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'rules':[(c['name'],c['passed'])for c in checks]}));sys.exit(0 if report['passed']else 1)

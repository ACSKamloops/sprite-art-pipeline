#!/usr/bin/env python3
"""Run real engine cases and reject runtime errors even if Godot exits zero.
Godot can continue a test script after a dependent GDScript compilation error;
therefore a PASS string or exit code alone is insufficient.
"""
from pathlib import Path
import os,re,json,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/evidence/checks'
OUT.mkdir(parents=True,exist_ok=True)
env={**os.environ,'LP_NUM_THREADS':'4','OMP_NUM_THREADS':'4'}
cases=[('systems_smoke.gd',r'SYSTEMS_SMOKE PASS: 114 behavioral checks'),('world_smoke.gd',r'WORLD PASS: 56 assertions'),('pause_smoke.gd',r'PAUSE PASS: 26 assertions'),('routes_smoke.gd',r'ROUTE SAMPLES: 378; blocked: \[\]'),('regressions.gd',r'REGRESSIONS PASS: 20 assertions'),('final_polish.gd',r'FINAL_POLISH PASS: 34 assertions'),('combat_readability.gd',r'COMBAT_READABILITY PASS: 30 assertions')]
cases.extend([('character_selection.gd',r'CHARACTER_SELECTION PASS: 40 assertions'),('spells_v2.gd',r'SPELLS_V2 PASS: (\d+) assertions')])
cases.append(('eight_directions.gd',r'EIGHT_DIRECTIONS PASS: (\d+) assertions; production_required=true'))
cases.append(('cast_charge_tracks.gd',r'CAST_CHARGE_TRACKS PASS: (\d+) assertions'))
receipts=[]
spell_assertions=0
eight_assertions=0
charge_assertions=0
for name,expected in cases:
    start=time.monotonic()
    cmd=['godot','--headless','--path',str(ROOT),'--script',f'tests/{name}','--','--test-mode']
    if name in ['eight_directions.gd','cast_charge_tracks.gd']:
        cmd.append('--production')
    r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
    (OUT/(name+'.log')).write_text(r.stdout)
    errors=re.findall(r'^.*(?:SCRIPT ERROR:|^ERROR:|FAIL:|FAILED:).*$',r.stdout,re.M)
    passed=r.returncode==0 and bool(re.search(expected,r.stdout)) and not errors
    if name=='spells_v2.gd' and re.search(expected,r.stdout):
        spell_assertions=int(re.search(expected,r.stdout).group(1))
    if name=='eight_directions.gd' and re.search(expected,r.stdout):
        eight_assertions=int(re.search(expected,r.stdout).group(1))
    if name=='cast_charge_tracks.gd' and re.search(expected,r.stdout):
        charge_assertions=int(re.search(expected,r.stdout).group(1))
    receipts.append({'case':name,'exit_code':r.returncode,'seconds':round(time.monotonic()-start,3),'passed':passed,'errors':errors,'expected_receipt':expected,'log':name+'.log'})
    print(name, 'PASS' if passed else 'FAIL',r.returncode,flush=True)
report={'engine':subprocess.check_output(['godot','--version'],text=True).strip(),'cases':receipts,'all_passed':all(r['passed'] for r in receipts),'assertions':320+spell_assertions+eight_assertions+charge_assertions,'baseline_assertions':280,'selection_fixture_assertions':40,'production_spell_assertions':spell_assertions,'eight_direction_assertions':eight_assertions,'cast_charge_assertions':charge_assertions,'route_samples':378,'note':'Behavioral/resource tests, not art scores. Selection is a fixture; spell/eight-direction/charge cases also load production character banks. Direction and charge counts include explicitly synthetic mechanics fixtures plus actual resource/projection assertions. Rendered attachment tests are separate. Model/API calls are not used.'}
(OUT/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
raise SystemExit(0 if report['all_passed'] else 1)

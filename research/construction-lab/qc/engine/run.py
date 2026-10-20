"""Strict engine runner: Godot script errors can coexist with exit0; reject both."""
import argparse,json,pathlib,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--player-source',type=pathlib.Path);p.add_argument('--prepare',action='store_true');a=p.parse_args();root=pathlib.Path(__file__).resolve().parent
if a.prepare:
 cmd=[sys.executable,str(root/'prepare.py')]
 if a.player_source:cmd+=['--player-source',str(a.player_source)]
 subprocess.run(cmd,check=True)
commands=[]
for name,args in [('import',['--editor','--import']),('run',['--script','timeline_check.gd'])]:
 cmd=['godot','--headless','--path',str(root),*args];r=subprocess.run(cmd,text=True,capture_output=True);log=r.stdout+r.stderr;(root/(name+'.log')).write_text(log);commands.append(dict(command=cmd,exit_code=r.returncode));
 if 'SCRIPT ERROR:'in log or 'Parse Error:'in log:raise SystemExit('Engine script error: '+name+'.log')
 if name=='import'and r.returncode:raise SystemExit(r.returncode)
report=json.loads((root/'engine-timeline-report.json').read_text());summary=dict(passed=report['passed'],checks=report['check_count'],failures=report['failures'],commands=commands,source_bindings='source-bindings.json');(root/'runner-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':report['check_count'],'failures':len(report['failures'])}));sys.exit(0 if report['passed']else 2)

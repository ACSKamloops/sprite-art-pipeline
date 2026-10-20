#!/usr/bin/env python3
"""Capture actual chronological browser playback; do not label screenshots as exact poses."""
import json,subprocess,hashlib,argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
args=argparse.ArgumentParser();args.add_argument('--output',default='/home/astra/artifacts/model-walk-bow-final24-timed');args.add_argument('--variant',choices=['bow','guarded'],default='bow');options=args.parse_args()
OUT=Path(options.output)
CLI='/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh'
OUT.mkdir(parents=True,exist_ok=True)
code='''async (page) => {
 await page.setViewportSize({width:1440,height:960});
 await page.goto('http://127.0.0.1:8144/pilot/model-walk-audition/VARIANT');
 await page.waitForFunction(()=>window.WalkAudition?.ready===true);
 const result={url:page.url(),manifest_sha256:await page.evaluate(()=>WalkAudition.manifest_sha256),modes:[]};
 for(const scale of [1,2]){
  await page.selectOption('#scale',String(scale));
  await page.evaluate(()=>{WalkAudition.pause();WalkAudition.seek(0);WalkAudition.play();});
  const entries=[];let i=0;
  while((await page.evaluate(()=>WalkAudition.state().seconds))<3.75){
   const before=await page.evaluate(()=>WalkAudition.state());
   const path=OUT+'/timed-'+scale+'x-'+String(i++).padStart(2,'0')+'.png';
   await page.locator('#views').screenshot({path});
   const after=await page.evaluate(()=>WalkAudition.state());
   entries.push({path,before,after});await page.waitForTimeout(90);
  }
  const stopped=await page.evaluate(()=>WalkAudition.pause());await page.waitForTimeout(180);
  const afterPause=await page.evaluate(()=>WalkAudition.state());
  const log=await page.evaluate(()=>WalkAudition.log);
  result.modes.push({scale,entries,stopped,after_pause:afterPause,playback_log:log});
 }
 const paused=[];for(let i=0;i<12;i++){
  await page.evaluate(i=>{WalkAudition.pause();WalkAudition.seek(i*1.25/12+1e-8)},i);
  const s=await page.evaluate(()=>WalkAudition.state());
  const path=OUT+'/paused-pose-'+String(i).padStart(2,'0')+'.png';
  await page.locator('#views').screenshot({path});paused.push({path,state:s});
 }
 result.paused=paused;return result;
}'''.replace('OUT',json.dumps(str(OUT))).replace('VARIANT','?variant=guarded' if options.variant=='guarded' else '')
proc=subprocess.run([CLI,'--session=copper-reel-final','run-code',code],cwd=ROOT,text=True,capture_output=True)
(OUT/'browser.log').write_text(proc.stdout+'\n'+proc.stderr)
if proc.returncode or '### Error' in proc.stdout:raise SystemExit((proc.stdout+proc.stderr)[:2000])
payload=proc.stdout.split('### Result\n',1)[1].split('\n### ',1)[0]
result=json.loads(payload)
for mode in result['modes']:
 assert mode['stopped']['seconds']==mode['after_pause']['seconds'],'Pause drift'
 assert mode['stopped']['seconds']>=3.75,'Three cycles not played'
 for e in mode['entries']:e['screenshot_sha256']=hashlib.sha256(Path(e['path']).read_bytes()).hexdigest()
for e in result['paused']:e['screenshot_sha256']=hashlib.sha256(Path(e['path']).read_bytes()).hexdigest()
result['player_sha256']=hashlib.sha256((ROOT/'pilot/model-walk-audition/index.html').read_bytes()).hexdigest()
result['capture_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
result['capture_contract']='Actual requestAnimationFrame playback. Screenshot timestamps bound by before/after states; capture may span pose boundaries. Paused inspection is separate. Three source-clock cycles per display scale. AI can inspect chronological stills, not continuously ingest video.'
(OUT/'capture.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'manifest':result['manifest_sha256'],'three_cycles_per_scale':True,'screenshots':[len(x['entries']) for x in result['modes']],'paused':len(result['paused']),'output':str(OUT)}))

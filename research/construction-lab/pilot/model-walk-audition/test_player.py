#!/usr/bin/env python3
"""Actual browser controls, source clock, wrap and corrupt-input checks."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CLI='/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh'
code=r'''async page=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const url='http://127.0.0.1:8144/pilot/model-walk-audition/';
 await page.goto(url);await page.waitForFunction(()=>window.WalkAudition?.ready===true);
 const manifest=await page.evaluate(()=>WalkAudition.manifest_sha256),checks=[];
 async function pixels(){return page.evaluate(async()=>{const out={};for(const v of ['front','right','back','left']){
  const bytes=document.getElementById('walk-'+v).getContext('2d').getImageData(0,0,160,160).data;
  out[v]=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');}return out;});}
 await page.evaluate(()=>{WalkAudition.pause();WalkAudition.seek(0)});const first=await pixels();
 for(let i=0;i<12;i++){await page.evaluate(i=>WalkAudition.seek(i*1.25/12+1e-8),i);if((await page.evaluate(()=>WalkAudition.state().pose))!==i)throw Error('Wrong heldpose');}
 checks.push('All12 held poses at rational source boundaries');
 await page.evaluate(()=>WalkAudition.seek(1.25));if(JSON.stringify(first)!==JSON.stringify(await pixels()))throw Error('Loop pixel reset differs');
 checks.push('All4views loop returns exactcanvas pixels');
 await page.click('#restart');if((await page.evaluate(()=>WalkAudition.state().seconds))!==0)throw Error('Restart failed');
 await page.click('#step');if((await page.evaluate(()=>WalkAudition.state().pose))!==1)throw Error('Step failed');
 await page.click('#back');if((await page.evaluate(()=>WalkAudition.state().pose))!==0)throw Error('Back failed');
 checks.push('Restart, forward and backward buttons');
 await page.click('#play');await page.waitForTimeout(220);await page.click('#pause');const paused=await page.evaluate(()=>WalkAudition.state());
 await page.waitForTimeout(180);if((await page.evaluate(()=>WalkAudition.state().seconds))!==paused.seconds)throw Error('Pause drift');
 checks.push('Actualplay advances; actualpause freezes');
 await page.selectOption('#speed','0.5');await page.evaluate(()=>{WalkAudition.seek(0);WalkAudition.play()});
 const start=await page.evaluate(()=>WalkAudition.state());await page.waitForTimeout(350);const end=await page.evaluate(()=>WalkAudition.pause());
 const actual=end.seconds-start.seconds,expected=(end.performance_ms-start.performance_ms)/1000*.5;
 if(Math.abs(actual-expected)>.025)throw Error('Wronghalfspeed');checks.push('Actual halfspeed wallclock within25ms');
 await page.selectOption('#scale','1');const native=await page.locator('#walk-front').boundingBox();if(native.width!==160||native.height!==160)throw Error('Native scale');
 await page.selectOption('#scale','2');const large=await page.locator('#walk-front').boundingBox();if(large.width!==320||large.height!==320)throw Error('2xscale');
 checks.push('Exact1x/2x canvasdisplay sizes');
 if(errors.length)throw Error('Unexpectedbrowsererrors');
 const negatives=[];
 await page.route('**/model-walk-audition/config.json',async route=>{const res=await route.fetch(),m=await res.json();m.manifest_sha256='0'.repeat(64);await route.fulfill({json:m})});
 await page.goto(url);await page.waitForFunction(()=>window.WalkAudition?.error);let reason=await page.evaluate(()=>WalkAudition.error);
 if(!reason.includes('Manifest differs'))throw Error('Manifestnegative failed');negatives.push(reason);await page.unroute('**/model-walk-audition/config.json');
 await page.route('**/front/00.png',async route=>{const res=await route.fetch(),b=await res.body();b[b.length-1]^=1;await route.fulfill({response:res,body:b})});
 await page.goto(url);await page.waitForFunction(()=>window.WalkAudition?.error);reason=await page.evaluate(()=>WalkAudition.error);
 if(!reason.includes('Changed frame front/0'))throw Error('Framenegative failed');negatives.push(reason);await page.unroute('**/front/00.png');
 await page.goto(url);await page.waitForFunction(()=>window.WalkAudition?.ready===true);
 return {manifest_sha256:manifest,checks,negatives,limits:'Controls/input tests do not approve anatomy, style, gait or world contact.'};
}'''
p=subprocess.run([CLI,'--session=copper-reel-final','run-code',code],cwd=ROOT,text=True,capture_output=True)
out=ROOT/'pilot/model-walk-audition/control-checks.log';out.write_text(p.stdout+'\n'+p.stderr)
if p.returncode or '### Error' in p.stdout:raise SystemExit((p.stdout+p.stderr)[:2500])
result=json.loads(p.stdout.split('### Result\n',1)[1].split('\n### ',1)[0])
(out.parent/'control-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

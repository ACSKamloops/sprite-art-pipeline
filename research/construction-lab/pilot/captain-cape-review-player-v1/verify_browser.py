"""Actual Chromium source compositing, clocks, controls and wall-time playback."""
import argparse
import base64
import hashlib
import io
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image


CLI = '/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    code = r'''async page => {
      const pageErrors=[];page.on('pageerror',error=>pageErrors.push(String(error)));
      await page.reload();
      await page.waitForFunction(()=>window.CapeReview?.state.ready);
      const checks=await page.evaluate(()=>{
        const a=window.CapeReview,checks=[],rasters=[];
        for(let n=0;n<65;n++){
          a.seek(n);checks.push({kind:'seek',n,pass:a.state.frame===n&&!a.state.playing});
          for(const v of a.variants)rasters.push({id:v.id,n,png:v.canvas.toDataURL('image/png')});
        }
        a.seek(64);document.getElementById('next').click();checks.push({kind:'next-wrap',pass:a.state.frame===0});
        document.getElementById('previous').click();checks.push({kind:'previous-wrap',pass:a.state.frame===64});
        a.seek(0);document.getElementById('play').click();a.advance(65/60);
        checks.push({kind:'cycle-rational',pass:a.state.frame===0&&Math.abs(a.state.clock-65)<1e-8});
        a.seek(0);const speed=document.getElementById('speed');speed.value='0.5';speed.dispatchEvent(new Event('change'));
        document.getElementById('play').click();a.advance(1/30);
        checks.push({kind:'half-clock',pass:a.state.frame===1&&a.state.speed===.5});
        document.getElementById('pause').click();const before=a.state.clock;a.advance(1);
        checks.push({kind:'pause',pass:a.state.clock===before});
        let invalidRejected=false;try{a.advance(-1);}catch(error){invalidRejected=true;}
        checks.push({kind:'invalid-elapsed-rejected',pass:invalidRejected&&a.state.clock===before});
        const zoom=document.getElementById('zoom');zoom.value='2';zoom.dispatchEvent(new Event('change'));
        checks.push({kind:'nearest-zoom',pass:a.variants.every(v=>v.canvas.width===384&&v.canvas.getBoundingClientRect().width===768&&getComputedStyle(v.canvas).imageRendering==='pixelated')});
        zoom.value='1';zoom.dispatchEvent(new Event('change'));speed.value='1';speed.dispatchEvent(new Event('change'));a.seek(0);
        return {checks,rasters};
      });
      await page.getByRole('button',{name:'Play',exact:true}).click();
      const timed=[];
      for(let i=0;i<8;i++){await page.waitForTimeout(150);timed.push(await page.evaluate(()=>({frame:window.CapeReview.state.frame,clock:window.CapeReview.state.clock,wall:performance.now()})));}
      await page.getByRole('button',{name:'Pause',exact:true}).click();
      const pauseBefore=await page.evaluate(()=>window.CapeReview.state.clock);
      await page.waitForTimeout(200);
      const pauseAfter=await page.evaluate(()=>window.CapeReview.state.clock);
      await page.locator('#speed').selectOption('0.5');
      await page.getByRole('button',{name:'Play',exact:true}).click();
      const halfTimed=[];
      for(let i=0;i<8;i++){await page.waitForTimeout(150);halfTimed.push(await page.evaluate(()=>({frame:window.CapeReview.state.frame,clock:window.CapeReview.state.clock,wall:performance.now()})));}
      await page.getByRole('button',{name:'Pause',exact:true}).click();
      await page.locator('#speed').selectOption('1');
      await page.keyboard.press('ArrowRight');const keyboardNext=await page.evaluate(()=>window.CapeReview.state.frame);
      await page.keyboard.press('ArrowLeft');const keyboardPrevious=await page.evaluate(()=>window.CapeReview.state.frame);
      const snapshot=await page.screenshot({fullPage:true});
      return {...checks,timed,halfTimed,pauseBefore,pauseAfter,keyboardNext,keyboardPrevious,pageErrors,screenshot:snapshot.toString('base64')};
    }'''
    result = subprocess.run([CLI, '-s=captain-cape-local', 'run-code', code],
                            capture_output=True, text=True)
    (args.output / 'browser-cli.txt').write_text(result.stdout + result.stderr)
    assert result.returncode == 0 and '### Error' not in result.stdout
    captured = json.loads(result.stdout.split('### Result\n', 1)[1].split('\n###', 1)[0])
    assert all(row['pass'] for row in captured['checks'])
    assert not captured['pageErrors'], captured['pageErrors']
    assert captured['keyboardNext'] == (captured['keyboardPrevious'] + 1) % 65
    assert captured['timed'][-1]['clock'] > captured['timed'][0]['clock'] + 40
    assert captured['halfTimed'][-1]['clock'] > captured['halfTimed'][0]['clock'] + 20
    assert captured['pauseBefore'] == captured['pauseAfter']
    timing = []
    for name, speed in [('timed', 1), ('halfTimed', .5)]:
        start, end = captured[name][0], captured[name][-1]
        expected = (end['wall'] - start['wall']) / 1000 * 60 * speed
        observed = end['clock'] - start['clock']
        error = abs(observed - expected)
        # Sampling can occur on either side of a requestAnimationFrame update.
        assert error <= 2.1, (name, observed, expected, error)
        timing.append({'speed':speed, 'expected_frames':expected,
                       'observed_frames':observed, 'error_frames':error,
                       'limit_frames':2.1})
    manifest = json.loads((args.pack / 'manifest.json').read_text())
    variants = {v['id']: v for v in manifest['variants']}
    yy, xx = np.indices((384, 384))
    checker = np.where(((xx//16+yy//16)%2)[...,None],
                       np.array([55,58,62]), np.array([40,43,47]))
    comparisons = []
    for row in captured['rasters']:
        f = variants[row['id']]['frames'][row['n']]
        p = args.pack / f['file']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == f['sha256']
        rgba = np.asarray(Image.open(p).convert('RGBA')).astype(float)
        alpha = rgba[...,3:4] / 255
        expected = np.rint(rgba[...,:3]*alpha + checker*(1-alpha)).astype(np.int16)
        png = base64.b64decode(row['png'].split(',',1)[1])
        actual = np.asarray(Image.open(io.BytesIO(png)).convert('RGB')).astype(np.int16)
        error = int(np.abs(actual-expected).max())
        assert error <= 1, (row['id'], row['n'], error)
        comparisons.append({'variant':row['id'],'index':row['n'],'max_RGB_error':error})
    (args.output / 'browser.png').write_bytes(base64.b64decode(captured['screenshot']))
    report = {'state':'PASS_LOCAL_BROWSER_CHECKS_ART_UNAPPROVED',
              'checks':captured['checks'],'source_composite_readbacks':comparisons,
              'timed':captured['timed'],'keyboard_step_passed':True,
              'half_timed':captured['halfTimed'],'timing_comparisons':timing,
              'wall_time_pause_exact':captured['pauseBefore']==captured['pauseAfter'],
              'manifest_sha256':hashlib.sha256((args.pack/'manifest.json').read_bytes()).hexdigest(),
              'player_sha256':hashlib.sha256((args.pack/'start-here.html').read_bytes()).hexdigest(),
              'scope':'130 actual native Chromium canvas readbacks, ±1RGB rounding; clock/wrap/zoom/keyboard and normal/half wall-time playback/pause checks; no art score or Godot/world-contact proof'}
    (args.output / 'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'state':report['state'],'readbacks':len(comparisons),
                      'max_RGB_error':max(r['max_RGB_error']for r in comparisons),
                      'timed_samples':len(captured['timed'])+len(captured['halfTimed'])}))


if __name__ == '__main__':
    main()

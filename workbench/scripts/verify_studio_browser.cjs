// Real Chromium controls, persistence and download. No page-state shortcuts or provider calls.
// node verify_studio_browser.cjs URL OUTPUT_DIR PLAYWRIGHT_MODULE CHROMIUM_EXECUTABLE
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.argv[4] || 'playwright');
const url = process.argv[2];
const out = path.resolve(process.argv[3]);
fs.mkdirSync(out, {recursive: false});
const report = {browser_plugin: 'not available; direct Playwright Chromium', checks: [], errors: [], provider_calls: 0, visual_acceptance: 'unreviewed'};
const check = (id, passed, detail) => { report.checks.push({id, passed: Boolean(passed), ...(detail ? {detail} : {})}); if (!passed) throw Error(id); };
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms)); // Deliberate playback observation intervals.
(async () => {
  const browser = await chromium.launch({headless:true, executablePath:process.argv[5], args:['--no-sandbox']});
  const context = await browser.newContext({viewport:{width:1440,height:1000}, acceptDownloads:true,
    recordVideo:{dir:path.join(out,'video'),size:{width:1440,height:1000}}});
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push(error.message));
  const content = id => page.locator('#studio-'+id).textContent();
  const settled = () => page.waitForFunction(() => !document.getElementById('studio-play').disabled);
  const first = async () => { await page.locator('#studio-frame').focus(); await page.keyboard.press('Home'); };
  const screenshot = name => page.screenshot({path:path.join(out,name+'.png'),fullPage:true});
  const pixelHash = () => page.locator('#studio-canvas').evaluate(async el => {
    const bytes=el.getContext('2d').getImageData(0,0,el.width,el.height).data;
    return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(v=>v.toString(16).padStart(2,'0')).join('');
  });
  try {
    await page.goto(url+'/#studio');
    await page.waitForFunction(()=>!document.getElementById('studio-demo').disabled);
    await page.selectOption('#studio-demo','hero-walk'); await page.click('#studio-load'); await settled();
    const initialProject=await content('project-id'), initialHash=await pixelHash();
    check('real_walk_loaded', /^[0-9a-f]{64}$/.test(initialProject) && (await content('frame-label')).includes('1 / 16'));
    check('authored_clock_label_visible', (await content('clock-note')).includes('provider timing unavailable'));
    await screenshot('walk-initial');
    await page.click('#studio-play'); await sleep(450);
    check('timed_walk_advances', (await content('frame-label')) !== '1 / 16');
    await page.click('#studio-play'); const paused=await content('frame-label'); await sleep(300);
    check('pause_holds_frame', (await content('frame-label')) === paused);
    await first();
    await page.click('#studio-play'); const samples=[];
    for(let i=0;i<19;i++) { await sleep(125); samples.push({frame:Number((await content('frame-label')).split('/')[0])-1, canvas_sha256:await pixelHash()}); }
    await page.click('#studio-play');
    check('actual_loop_wrap_observed', samples.some((s,i)=>i>0 && s.frame<samples[i-1].frame));
    report.loop_playback_samples=samples; await first();
    await page.fill('#studio-seed-x','128'); await page.fill('#studio-seed-y','128'); await page.fill('#studio-tolerance','0');
    await page.click('#studio-select'); await page.waitForFunction(()=>!document.getElementById('studio-erase').disabled);
    check('real_local_mask_created', (await content('selection-info')).includes('selected'));
    await screenshot('selection-overlay');
    await page.click('#studio-next'); check('frame_change_invalidates_mask', await page.locator('#studio-erase').isDisabled());
    await first(); await page.click('#studio-select'); await page.waitForFunction(()=>!document.getElementById('studio-erase').disabled);
    await page.click('#studio-erase');
    await page.waitForFunction(old => document.getElementById('studio-project-id').textContent !== old,initialProject); await settled();
    const editedProject=await content('project-id');
    check('mask_edit_changes_visible_pixels', (await pixelHash()) !== initialHash);
    await page.click('#studio-undo'); await page.waitForFunction(old=>document.getElementById('studio-project-id').textContent===old,initialProject); await settled();
    check('undo_exact_canvas_pixels', (await pixelHash()) === initialHash);
    await page.click('#studio-redo'); await page.waitForFunction(old=>document.getElementById('studio-project-id').textContent===old,editedProject); await settled();
    await page.reload(); await settled();
    check('browser_reopen_preserves_revision', (await content('project-id')) === editedProject);
    check('browser_reopen_discards_mask', await page.locator('#studio-erase').isDisabled());
    await page.locator('#studio-frame').focus(); await page.keyboard.press('End');
    check('shared_cel_scope_visible', (await content('linked')).includes('3'));
    await screenshot('shared-cel-scope'); await first();
    await page.click('#studio-verify');
    await page.waitForFunction(()=>document.getElementById('studio-mechanical').textContent.includes('passed'));
    check('visual_not_autoapproved', (await content('visual')).includes('unreviewed'));
    await page.click('#studio-export'); await page.waitForSelector('#studio-download:not([hidden])',{timeout:60000});
    const downloadPromise=page.waitForEvent('download'); await page.click('#studio-download'); const download=await downloadPromise;
    await download.saveAs(path.join(out,'downloaded-package.zip'));
    check('verified_export_downloaded', fs.statSync(path.join(out,'downloaded-package.zip')).size>1000);
    await screenshot('verified-export');
    await page.selectOption('#studio-demo','hero-slash'); await page.click('#studio-load'); await settled();
    await page.click('#studio-play'); await page.waitForFunction(()=>document.getElementById('studio-play').textContent==='Replay',{timeout:10000});
    check('slash_stops_on_final_frame', (await content('frame-label'))==='16 / 16');
    const endpoint=await pixelHash(); await sleep(300); check('one_shot_endpoint_holds', (await pixelHash())===endpoint);
    await page.click('#studio-play'); await sleep(180); await page.click('#studio-play');
    check('one_shot_restarts', (await content('frame-label')) !== '16 / 16');
    await screenshot('slash-restarted');
    await page.setViewportSize({width:390,height:844}); await screenshot('mobile');
    const dimensions=await page.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
    check('mobile_no_horizontal_overflow', dimensions.scroll<=dimensions.width, dimensions);
    check('no_browser_exceptions',report.errors.length===0);
    report.status='passed';
  } catch(error) { report.status='failed'; report.failure=error.message; await screenshot('failure'); }
  finally { await context.close(); await browser.close(); fs.writeFileSync(path.join(out,'REPORT.json'),JSON.stringify(report,null,2)+'\n'); }
  console.log(JSON.stringify({status:report.status,checks:report.checks.length,report:path.join(out,'REPORT.json'),failure:report.failure}));
  if(report.status!=='passed')process.exitCode=1;
})().catch(error=>{console.error(error.message);process.exitCode=1;});

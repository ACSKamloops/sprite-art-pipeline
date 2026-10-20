async (page) => {
  // Ordinary input only. No save edits, teleports, actor setters or test mode.
  // Run on a freshly exported eight-way build in an isolated browser profile.
  // Browser plugin not available in this authoring session; repo Playwright path.
  const views = ['south','southeast','east','northeast','north','northwest','west','southwest'];
  const diagonals = [
    {view:'northeast',keys:['w','d'],opposite:['s','a'],aim:[Math.SQRT1_2,-Math.SQRT1_2]},
    {view:'southwest',keys:['s','a'],opposite:['w','d'],aim:[-Math.SQRT1_2,Math.SQRT1_2]},
    {view:'southeast',keys:['s','d'],opposite:['w','a'],aim:[Math.SQRT1_2,Math.SQRT1_2]},
    {view:'northwest',keys:['w','a'],opposite:['s','d'],aim:[-Math.SQRT1_2,-Math.SQRT1_2]},
  ];
  const receipts = [], consoleMessages = [], pageErrors = [], actionTraces = [];
  let phase = {stage:"setup"};
  const installActionTrace = function installActionTrace(context) {
  if (window.__emberwakeEightTrace) throw Error('Action observer already installed');
  const trace = {context, status:'recording', samples:[], saw_action:false};
  const startedAt = performance.now();
  let previous, raf, timer;
  const finish = status => {
    if (trace.status !== 'recording') return;
    trace.status = status;
    trace.elapsed_ms = performance.now() - startedAt;
    cancelAnimationFrame(raf);
    clearTimeout(timer);
  };
  const sample = () => {
    const s = window.emberwakeState;
    if (!s || s === previous) return;
    previous = s;
    if (trace.samples.length >= 96) { finish('buffer_limit'); return; }
    const snapshot = JSON.parse(JSON.stringify({
      mode:s.mode, test_mode:s.test_mode, position:s.position,
      physics_tick:s.physics_tick, physics_hz:s.physics_hz,
      rendered_frames:s.rendered_frames, fps:s.fps,
      hero:s.hero, projectiles:s.projectiles,
    }));
    trace.samples.push({observed_ms:performance.now()-startedAt, snapshot});
    const active = s.mode === 'play' && s.hero?.state === context.pose && s.hero.state_left > 0;
    if (active) trace.saw_action = true;
    else if (trace.saw_action) finish('action_ended');
  };
  const frame = () => {
    sample();
    if (trace.status === 'recording') raf = requestAnimationFrame(frame);
  };
  // A fixed, single observation period. Never trigger another action to get a pass.
  timer = setTimeout(() => finish('timeout'), 2500);
  window.__emberwakeEightTrace = {trace, cancel:() => finish('cancelled')};
  sample();
  if (trace.status === 'recording') raf = requestAnimationFrame(frame);
  return {baseline_tick:trace.samples[0]?.snapshot.physics_tick};
};
  const analyzeActionTrace = function analyzeActionTrace(trace) {
  const c = trace.context;
  const same = (a,b) => Array.isArray(a) && Array.isArray(b) && Math.hypot(a[0]-b[0],a[1]-b[1]) < .002;
  const reject = (name,message) => {
    const error = Error(message + ': ' + JSON.stringify(c));
    error.name = name;
    throw error;
  };
  const incomplete = message => reject('IncompleteObservation',message);
  const failed = message => reject('ObservedBehaviorFailure',message);
  const states = trace.samples.map(item => item.snapshot);
  if (trace.status !== 'action_ended') incomplete('Trace did not observe action completion ('+trace.status+')');
  const locked = states.filter(s => s.mode === 'play' && s.hero?.state === c.pose && s.hero.state_left > 0);
  if (!locked.length) incomplete('No locked action snapshot');
  const started = locked.find(s => s.hero.state_time >= .035);
  if (!started) incomplete('No action snapshot at/after initial .035s observation');
  if (locked.some(s => s.test_mode !== false || s.hero.character !== c.id)) failed('Unexpected actor or test mode');
  if (locked.some(s => s.hero.facing !== c.view || !same(s.hero.action_aim,c.aim))) failed('Observed facing/action_aim changed during lock');
  const released = locked.filter(s => s.hero.state_time >= c.release);
  // Do not filter out pending_hit before checking; doing so hides release bugs.
  if (released.some(s => s.hero.pending_hit !== '')) failed('Observed pending hit after gameplay release clock');
  const opposed = released.filter(s => same(s.hero.movement_input,c.oppositeAim));
  if (!opposed.length) incomplete('No released locked snapshot with actual opposite movement_input');
  // Retain the old late-recovery threshold. RAF cannot manufacture an absent emission.
  const late = opposed.filter(s => s.hero.state_time >= c.duration-.11);
  if (!late.length) incomplete('No late locked snapshot with actual opposite movement_input');
  const end = states[states.length-1];
  if (end.mode !== 'play' || !['walk','idle'].includes(end.hero?.state)) failed('Action ended outside ordinary walk/idle');
  const actionStartTick = started.physics_tick - started.hero.state_time*started.physics_hz;
  const projectiles = [];
  for (const s of states) {
    if (s.physics_tick <= actionStartTick) continue;
    for (const bolt of s.projectiles || []) {
      // Existing diagnostics have no projectile ID. Inferred birth after this
      // action excludes older friendly bolts; this remains a sampled direction check.
      const born = s.physics_tick - bolt.elapsed*s.physics_hz;
      if (!bolt.hostile && bolt.elapsed >= 0 && bolt.elapsed < .31 && born > actionStartTick+1)
        projectiles.push({physics_tick:s.physics_tick,...bolt});
    }
  }
  if (c.pose === 'cast') {
    if (!projectiles.length) incomplete('No current-cast projectile in the complete observation trace');
    if (projectiles.some(bolt => !same(bolt.direction,c.aim))) failed('Observed current-cast projectile changed committed direction');
  }
  return {started, recovery:late[late.length-1], locked_count:locked.length,
    released_count:released.length, opposed_count:opposed.length, late_count:late.length,
    projectile_observations:projectiles.length};
};
  const onConsole = message => {
    if (['error','warning'].includes(message.type())) consoleMessages.push({type:message.type(),text:message.text()});
  };
  const onPageError = error => pageErrors.push(String(error));
  page.on('console',onConsole);
  page.on('pageerror',onPageError);
  const state = () => page.evaluate(() => window.emberwakeState);
  const length = value => Math.hypot(...value);
  const sameVector = (a,b) => Array.isArray(a) && Math.hypot(a[0]-b[0],a[1]-b[1]) < .002;
  const compact = s => ({mode:s.mode,test_mode:s.test_mode,position:s.position,physics_tick:s.physics_tick,physics_hz:s.physics_hz,hero:s.hero,projectiles:s.projectiles});
  const check = (ok,note,data) => {
    receipts.push({ok,note,data});
    if (!ok) throw Error(note);
  };
  const waitMode = mode => page.waitForFunction(m => window.emberwakeState?.mode === m,mode,{timeout:10000});
  const releaseKeys = async () => {
    await Promise.all(['w','a','s','d'].map(key=>page.keyboard.up(key)));
  };
  const hold = async keys => {
    await releaseKeys();
    await Promise.all(keys.map(key=>page.keyboard.down(key)));
  };
  const click = async action => {
    await page.waitForFunction(a => window.emberwakeState?.ui_controls?.some(b => b.action === a && !b.disabled),action,{timeout:10000});
    const s = await state();
    const button = s.ui_controls.find(b => b.action === action && !b.disabled);
    const box = await page.locator('canvas').boundingBox();
    if (!box || !button) throw Error('No real UI control '+action);
    await page.mouse.click(box.x+(button.rect[0]+button.rect[2]/2)*box.width/s.viewport[0],box.y+(button.rect[1]+button.rect[3]/2)*box.height/s.viewport[1]);
    await page.waitForTimeout(140);
  };
  const waitHero = async (desiredState,minTime=0) => {
    const matched=await page.waitForFunction(({desiredState,minTime}) => {
      const s=window.emberwakeState;
      return s?.mode==='play' && s.hero?.state===desiredState && s.hero.state_time>=minTime ? s : false;
    },{desiredState,minTime},{timeout:5000});
    try { return await matched.jsonValue(); } finally { await matched.dispose(); }
  };
  const chooseAndStart = async id => {
    await waitMode('title');
    await click('characters'); await waitMode('characters');
    await click('character_select:'+id);
    check((await state()).character_choice===id,'actual gallery selects '+id);
    await click('character_apply'); await waitMode('title');
    check((await state()).selected_character===id,'title retains selected '+id);
    await click('new');
    if ((await state()).mode==='confirm') await click('new_confirmed');
    for (let n=0;n<10 && (await state()).mode==='dialogue';n++) await click('dialogue_next');
    await waitMode('play');
    const s=await state();
    check(s.test_mode===false,'ordinary play never enables test mode '+id);
    check(s.hero.character===id && s.hero.art_ready,'new journey binds actual selected production art '+id,compact(s));
    check(JSON.stringify(s.hero.directions)===JSON.stringify(views),'actual exported production bank declares eight views '+id,s.hero.directions);
    check(Number.isFinite(s.physics_tick) && s.physics_hz>0 && Array.isArray(s.hero.action_aim),'readonly movement and action diagnostics are exported '+id);
  };
  const walk = async (id,direction) => {
    await hold(direction.keys);
    await page.waitForFunction(({view,aim}) => {
      const s=window.emberwakeState;
      return s?.mode==='play' && s.hero?.state==='walk' && s.hero.facing===view && Math.hypot(...s.hero.velocity)>157 && Math.hypot(s.hero.movement_input[0]-aim[0],s.hero.movement_input[1]-aim[1])<.002;
    },direction,{timeout:5000});
    const before=await state();
    await page.waitForFunction(tick => window.emberwakeState?.physics_tick>=tick+12,before.physics_tick,{timeout:5000});
    const after=await state();
    await page.screenshot({path:`output/playwright/eight-${id}-${direction.view}-walk.png`});
    await releaseKeys();
    const seconds=(after.physics_tick-before.physics_tick)/after.physics_hz;
    const displacement=[after.position[0]-before.position[0],after.position[1]-before.position[1]];
    const measuredSpeed=length(displacement)/seconds;
    check(after.hero.character===id && after.hero.facing===direction.view && after.hero.art_clip===direction.view+'_walk','real keys select diagonal travel art '+id+' '+direction.view,compact(after));
    check(Math.abs(length(after.hero.movement_input)-1)<.002 && sameVector(after.hero.movement_input,direction.aim),'diagonal keyboard input is a unit vector '+id+' '+direction.view);
    check(Math.abs(measuredSpeed-158)<5 && length(after.hero.velocity)<=158.01,'simulation-tick distance confirms normalized speed '+id+' '+direction.view,{before:compact(before),after:compact(after),seconds,displacement,measuredSpeed});
    check(sameVector(displacement.map(value=>value/length(displacement)),direction.aim),'actual path follows the requested diagonal '+id+' '+direction.view,displacement);
    const idle=await waitHero('idle');
    await page.waitForFunction(tick=>window.emberwakeState?.physics_tick>=tick+4,idle.physics_tick,{timeout:5000});
    const stillIdle=await state();
    check(stillIdle.hero.state==='idle' && length(stillIdle.hero.movement_input)===0 && stillIdle.hero.facing===idle.hero.facing && sameVector(stillIdle.hero.aim,idle.hero.aim),'zero input retains the last actually observed aim '+id+' '+direction.view,{idle:compact(idle),stillIdle:compact(stillIdle),qualification:'Physical key-up delivery can briefly leave one cardinal key held; the last actual nonzero aim may therefore differ from the earlier diagonal sample.'});
    return measuredSpeed;
  };
  const committedAction = async (id,direction,key,pose,duration,release) => {
    const context={id,view:direction.view,key,pose,duration,release,aim:direction.aim,oppositeAim:direction.aim.map(v=>-v)};
    phase={...context,stage:'prepare_direction'};
    await hold(direction.keys);
    await page.waitForFunction(view=>window.emberwakeState?.hero?.state==='walk' && window.emberwakeState.hero.facing===view,direction.view,{timeout:5000});
    phase={...context,stage:'install_observer'};
    await page.evaluate(installActionTrace,context);
    let trace, screenshotTask=Promise.resolve(null);
    try {
      phase={...context,stage:'press_real_action_key'};
      await page.keyboard.press(key);
      // Reverse promptly; the observer already retains the initial commitment.
      phase={...context,stage:'hold_opposite_real_keys'};
      await hold(direction.opposite);
      if (pose==='attack') screenshotTask=page.screenshot({path:`output/playwright/eight-${id}-${direction.view}-attack.png`}).then(()=>null,error=>error);
      phase={...context,stage:'collect_action_trace'};
      const matched=await page.waitForFunction(() => {
        const t=window.__emberwakeEightTrace?.trace;
        return t && t.status!=='recording' ? t : false;
      },null,{timeout:3500});
      try { trace=await matched.jsonValue(); } finally { await matched.dispose(); }
    } finally {
      await releaseKeys();
      const partial=await page.evaluate(() => {
        const observer=window.__emberwakeEightTrace;
        if (!observer) return null;
        observer.cancel();
        const trace=observer.trace;
        delete window.__emberwakeEightTrace;
        return trace;
      });
      if (partial) actionTraces.push(partial);
      const screenshotError=await screenshotTask;
      if (screenshotError) throw screenshotError;
    }
    phase={...context,stage:'analyze_locked_recovery'};
    let observed;
    try { observed=analyzeActionTrace(trace); }
    catch (error) {
      if (error.name==='IncompleteObservation') receipts.push({ok:null,note:String(error),data:{phase,trace_index:actionTraces.length-1}});
      throw error;
    }
    const {started,recovery}=observed;
    check(started.hero.facing===direction.view && sameVector(started.hero.action_aim,direction.aim),'ordinary '+pose+' commits requested diagonal '+id+' '+direction.view,compact(started));
    check(recovery.hero.facing===direction.view && sameVector(recovery.hero.action_aim,direction.aim) && recovery.hero.state_left>0 && sameVector(recovery.hero.movement_input,context.oppositeAim),'opposite held input cannot swivel '+pose+' through recovery '+id+' '+direction.view,{...compact(recovery),observed_locked:observed.locked_count,observed_released:observed.released_count,observed_opposed:observed.opposed_count,observed_late:observed.late_count});
    check(recovery.hero.pending_hit==='' && recovery.hero.state_time>=release,'pending '+pose+' releases at its unchanged gameplay clock '+id+' '+direction.view,compact(recovery));
    if (pose==='cast') check(observed.projectile_observations>0,'observed live firebolts retain committed diagonal '+id+' '+direction.view,{observed_projectile_samples:observed.projectile_observations});
    phase={...context,stage:'await_idle_after_action'};
    const idle=await waitHero('idle');
    check(sameVector(idle.hero.action_aim,direction.aim),'completed '+pose+' retains its committed action vector '+id+' '+direction.view,{idle:compact(idle),qualification:'Opposite input may resume steering once recovery ends; all observed locked snapshots above were checked.'});
  };
  try {
    await waitMode('title');
    check(/Emberwake/i.test(await page.title()),'page identity is Emberwake',{url:page.url(),title:await page.title()});
    const canvas=await page.locator('canvas').boundingBox();
    check(canvas && canvas.width>0 && canvas.height>0 && (await state()).character_count===3,'meaningful engine screen and all three selectors are present');
    await page.screenshot({path:'output/playwright/eight-title.png'});
    for (const id of ['rowan','lyra','brann']) {
      await chooseAndStart(id);
      const speeds=[];
      for (const direction of diagonals) {
        speeds.push(await walk(id,direction));
        await committedAction(id,direction,'j','attack',.41,.16);
        await committedAction(id,direction,'k','cast',.50,.24);
        // Await the real firebolt cooldown using observations, not a mutation.
        await page.waitForFunction(() => window.emberwakeState?.hero?.cooldowns?.firebolt===0,null,{timeout:5000});
      }
      check(Math.max(...speeds)-Math.min(...speeds)<5,'all four diagonal travel speeds agree '+id,speeds);
      await page.keyboard.press('Escape'); await waitMode('pause');
      await click('save_title'); await waitMode('title');
    }
    check(pageErrors.length===0,'no JavaScript page errors',pageErrors);
    const appErrors=consoleMessages.filter(message=>message.type==='error' || /SCRIPT ERROR|\bERROR:|FAIL:|FAILED:/i.test(message.text));
    check(appErrors.length===0,'no engine or app console errors during the interaction loop',appErrors);
    const report = {passed:true,scope:'Actual exported production banks, ordinary menu clicks and keyboard only, test_mode=false, isolated profile. Browser plugin not available; repository Playwright workflow.',qualification:'Native frozen fixture supplies exact release screenshots. Browser screenshots and readonly state are asynchronous samples; neither passes a visual art/motion score.',receipts,consoleMessages,pageErrors,actionTraces,final:compact(await state())};
    return report;
  } catch (error) {
    return {passed:false,error:String(error),phase,receipts,consoleMessages,pageErrors,actionTraces,final:compact(await state())};
  } finally {
    await releaseKeys();
    page.off('console',onConsole);
    page.off('pageerror',onPageError);
  }
}

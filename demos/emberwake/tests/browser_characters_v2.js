async (page) => {
  const receipts = [];
  const state = () => page.evaluate(() => window.emberwakeState);
  const waitMode = mode => page.waitForFunction(m => window.emberwakeState?.mode === m, mode);
  const click = async action => {
    await page.waitForFunction(a => window.emberwakeState?.ui_controls?.some(b => b.action === a && !b.disabled), action);
    const s = await state();
    const b = s.ui_controls.find(b => b.action === action);
    const box = await page.locator('canvas').boundingBox();
    if (!box || !b) throw Error('No actual control '+action);
    await page.mouse.click(box.x+(b.rect[0]+b.rect[2]/2)*box.width/s.viewport[0], box.y+(b.rect[1]+b.rect[3]/2)*box.height/s.viewport[1]);
    await page.waitForTimeout(180);
  };
  const check = (ok, note, data) => {
    receipts.push({ok, note, data});
    if (!ok) throw Error(note);
  };
  await waitMode('title');
  check((await state()).character_count === 3, 'export contains all three real characters');
  for (const id of ['lyra','brann']) {
    await click('characters'); await waitMode('characters');
    await page.screenshot({path:`output/playwright/characters-v2-${id}-gallery.png`});
    await click('character_select:'+id);
    check((await state()).character_choice === id, 'actual gallery draft '+id);
    await click('character_apply'); await waitMode('title');
    await click('new');
    if ((await state()).mode === 'confirm') await click('new_confirmed');
    for (let n=0;n<4 && (await state()).mode==='dialogue';n++) await click('dialogue_next');
    await waitMode('play');
    check((await state()).hero.character === id && (await state()).hero.art_ready, 'real exported hero bank '+id);
    await page.keyboard.press('l');
    await page.waitForTimeout(300);
    await page.screenshot({path:`output/playwright/characters-v2-${id}-frost.png`});
    const frost=await state();
    check(frost.hero.mana <= 37, 'frost pays resource '+id, frost);
    await page.waitForTimeout(450);
    await page.keyboard.press('h');
    await page.waitForTimeout(180);
    for (const [key,view] of [['w','north'],['a','west'],['s','south'],['d','east']]) {
      await page.keyboard.down(key); await page.waitForTimeout(140);
      const walking = await state(); await page.keyboard.up(key);
      check(walking.hero.facing === view && walking.hero.character === id, 'normal input facing '+id+' '+view, walking);
      await page.waitForTimeout(140);
      await page.keyboard.press('j'); await page.waitForTimeout(470);
      await page.keyboard.press('k'); await page.waitForTimeout(245);
      await page.screenshot({path:`output/playwright/characters-v2-${id}-fire-${view}.png`});
      receipts.push({note:'normal-input cast sample '+id+' '+view, data:await state(), qualification:'state and asynchronous screenshot may sample different frames'});
      await page.waitForTimeout(540);
    }
    await page.keyboard.press('Space'); await page.waitForTimeout(100);
    const dodge=await state();
    check(dodge.mode==='play', 'Space dodges without GUI reopening journal '+id, dodge);
    await page.waitForTimeout(300);
    await page.keyboard.press('Escape'); await waitMode('pause');
    const before=await state();
    await click('characters'); await waitMode('characters');
    const other=id==='lyra'?'brann':'lyra';
    await click('character_select:'+other); await click('character_apply'); await waitMode('pause');
    const swapped=await state();
    check(swapped.hero.character===other && swapped.hero.hp===before.hero.hp && swapped.hero.mana===before.hero.mana && JSON.stringify(swapped.position)===JSON.stringify(before.position), 'safe real bank swap preserves health mana and location '+id+' -> '+other, {before,swapped});
    await click('characters'); await click('character_select:'+id); await click('character_apply'); await waitMode('pause');
    await click('save_title'); await waitMode('title');
    await page.reload(); await waitMode('title');
    await click('continue'); await waitMode('play');
    check((await state()).hero.character===id, 'Continue restores actual saved character '+id, await state());
    await page.keyboard.press('Escape'); await waitMode('pause');
    await click('save_title'); await waitMode('title');
  }
  await page.screenshot({path:'output/playwright/characters-v2-title.png'});
  return {scope:'Ordinary-input local browser, test_mode=false, isolated browser profile, no gameplay mutation',receipts,final:await state()};
}

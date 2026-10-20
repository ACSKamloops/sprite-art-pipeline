async (page) => {
  const receipts=[];
  const state=()=>page.evaluate(()=>window.emberwakeState);
  for(const [key,name] of [['w','north'],['a','west'],['s','south'],['d','east']]) {
    const before=await state();
    await page.keyboard.down(key);
    await page.waitForTimeout(180);
    const during=await state();
    await page.screenshot({path:`output/playwright/walk-${name}.png`});
    await page.keyboard.up(key);
    await page.waitForTimeout(150);
    await page.keyboard.press('j');
    await page.waitForTimeout(160);
    const attack=await state();
    await page.screenshot({path:`output/playwright/attack-${name}.png`});
    await page.waitForTimeout(300);
    await page.keyboard.press('k');
    await page.waitForTimeout(240);
    const cast=await state();
    await page.screenshot({path:`output/playwright/cast-${name}.png`});
    await page.waitForTimeout(550);
    receipts.push({name,before,during,attack,cast,after:await state()});
  }
  await page.keyboard.press('l');
  await page.waitForTimeout(340);
  await page.screenshot({path:'output/playwright/nova.png'});
  const nova=await state();
  await page.keyboard.press('Space');
  await page.waitForTimeout(120);
  const dodge=await state();
  await page.screenshot({path:'output/playwright/dodge.png'});
  await page.keyboard.press('Escape');
  const paused=await state();
  await page.waitForTimeout(550);
  const stillpaused=await state();
  await page.screenshot({path:'output/playwright/journal.png'});
  await page.keyboard.press('Escape');
  console.log(JSON.stringify({receipts,nova,dodge,paused,stillpaused,final:await state()},null,2));
}

const { chromium } = require('playwright');
(async () => {
  const [,, ts, outdir] = process.argv;
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + require('path').resolve('short.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  for (const t of ts.split(',')) { await p.evaluate(x => window.render(+x), t); await p.screenshot({ path: `${outdir}/t_${t}.png` }); }
  await b.close();
})();

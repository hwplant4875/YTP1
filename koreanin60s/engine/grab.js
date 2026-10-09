// usage: node grab.js <dir> t1,t2,...  -> <dir>/t_<t>.png
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2]);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + dir + '/short.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300); await p.evaluate(() => window.layout && window.layout());
  for (const t of process.argv[3].split(',')) { await p.evaluate(x => window.render(+x), t); await p.screenshot({ path: `${dir}/t_${t}.png` }); }
  await b.close();
})();

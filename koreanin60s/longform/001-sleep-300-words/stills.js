const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2]); const jobs = JSON.parse(fs.readFileSync(dir + '/jobs.json'));
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + dir + '/frame.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  for (const [out, kind, args] of jobs) { if (fs.existsSync(out)) continue; await p.evaluate(([k, a]) => window[k](...a), [kind, args]); await p.screenshot({ path: out }); }
  await b.close();
})();

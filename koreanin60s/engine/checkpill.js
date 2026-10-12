// usage: node checkpill.js <dir>  -> lists elements overlapping the top label pill while it is on screen (exit 1 if any)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2]);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + dir + '/short.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300); await p.evaluate(() => { window.fit && window.fit(); window.layout && window.layout(); });
  const end = await p.evaluate(() => D.pillOut + 0.3); const hits = new Set();
  for (let t = 0.3; t <= end; t += 0.1) {
    await p.evaluate(x => window.render(+x), t);
    const r = await p.evaluate(() => {
      const pill = document.getElementById('pill').getBoundingClientRect(); if (pill.width < 50) return [];
      const vis = e => { for (; e && e.id !== 'scenes'; e = e.parentElement) { const s = getComputedStyle(e); if (+s.opacity < 0.05 || s.display === 'none' || s.visibility === 'hidden') return false; } return true; };
      return [...document.querySelectorAll('#scenes > * > *')].filter(vis).map(e => [e.getBoundingClientRect(), e.textContent.slice(0, 30) || e.querySelector('img')?.src.slice(-0) && 'img'])
        .filter(([q]) => q.width > 0 && q.left < pill.right && q.right > pill.left && q.top < pill.bottom + 12 && q.bottom > pill.top).map(([q, n]) => `${n} top=${Math.round(q.top)} pillBottom=${Math.round(pill.bottom)}`);
    });
    r.forEach(x => hits.add(`t=${t.toFixed(1)} ${x}`));
  }
  console.log(hits.size ? [...hits].slice(0, 6).join('\n') : 'pill clear'); await b.close(); process.exit(hits.size ? 1 : 0);
})();

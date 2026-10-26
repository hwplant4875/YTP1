// node render.js in.svg out.png size  -> renders an SVG square with headless Chromium
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [inp, out, size] = process.argv.slice(2); const n = parseInt(size || '2000');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: n, height: n } });
  const svg = fs.readFileSync(inp, 'utf8');
  await p.setContent(`<html><body style="margin:0;background:transparent">${svg.replace('<svg ', `<svg width="${n}" height="${n}" `)}</body></html>`);
  await p.waitForTimeout(300);
  await p.screenshot({ path: out, omitBackground: true, clip: { x: 0, y: 0, width: n, height: n } }); await b.close();
})();

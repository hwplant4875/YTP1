import { chromium } from 'playwright';
const [mod, ts, pre] = process.argv.slice(2);
const m = await import('./' + mod);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: m.W, height: m.H } });
await p.setContent(`<style>${m.FONTS}body{margin:0;background:#000}</style><div id="c"></div>`);
for (const t of ts.split(',').map(Number)) { await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, m.frame(t)); await p.waitForTimeout(50); await p.screenshot({ path: `${pre}_${t}.png` }); }
await b.close();

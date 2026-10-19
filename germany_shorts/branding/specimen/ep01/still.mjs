import { chromium } from 'playwright';
import { FONTS } from './eng.mjs';
// usage: node still.mjs module id t1,t2 prefix
const [mod, id, ts, pre] = process.argv.slice(2);
const m = await import('./' + mod); const { SC } = await import('./tl.mjs');
const sc = SC.find(s => s.id === id);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.setContent(`<style>${FONTS}body{margin:0;background:#000}</style><div id="c"></div>`);
for (const t of ts.split(',').map(Number)) { await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, m[id](t, sc.len)); await p.waitForTimeout(40); await p.screenshot({ path: `${pre}_${id}_${t}.png` }); }
await b.close();

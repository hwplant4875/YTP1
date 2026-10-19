import { chromium } from 'playwright';
import { FONTS } from './eng.mjs';
// usage: node chkall.mjs module id1,id2 fracs out.jpg-prefix
const [mod, ids, fr, pre] = process.argv.slice(2);
const m = await import('./' + mod); const { SC } = await import('./tl.mjs');
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.setContent(`<style>${FONTS}body{margin:0;background:#000}</style><div id="c"></div>`);
const out = [];
for (const id of ids.split(',')) { const sc = SC.find(s => s.id === id);
  for (const f of fr.split(',').map(Number)) { const t = +(f * sc.len).toFixed(2); await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, m[id](t, sc.len)); await p.waitForTimeout(30);
    const fn = `${pre}_${id}_${t}.png`; await p.screenshot({ path: fn }); out.push(fn); } }
await b.close(); console.log(out.join(' '));

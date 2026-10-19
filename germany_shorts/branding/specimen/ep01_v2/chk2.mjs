import { chromium } from 'playwright';
// usage: node chk2.mjs id1,id2 fracs prefix
const [ids, fr, pre] = process.argv.slice(2);
const m = await import('./main2.mjs'); const { SC } = await import('./tl2.mjs');
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.setContent(`<style>${m.FONTS}body{margin:0;background:#000}</style><div id="c"></div>`);
const out = [];
for (const id of ids.split(',')) { const sc = SC.find(s => s.id === id);
  for (const f of fr.split(',').map(Number)) { const t = +(f * sc.len).toFixed(2); await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, m.scene(id, t)); await p.waitForTimeout(30);
    const fn = `${pre}_${id}_${t}.png`; await p.screenshot({ path: fn }); out.push(fn); } }
await b.close(); console.log(out.join(' '));

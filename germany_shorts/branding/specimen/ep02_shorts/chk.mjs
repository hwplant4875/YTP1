import { chromium } from 'playwright';
// usage: SHORT=b01 node chk.mjs times|auto out_prefix
const m = await import('./vert.mjs'); const [ts, pre] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.setContent(`<style>${m.FONTS}body{margin:0}</style>${m.EXTRA}<div id="c"></div>`);
const P = (await import('./plan.mjs')).PLANS[process.env.SHORT];
const T0 = ts === 'auto' ? [0, ...P.parts.flatMap(x => [x.T0 + 0.5, x.T0 + x.len * 0.35, x.T0 + x.len * 0.7, x.T0 + x.len - 0.1])] : ts.split(',').map(Number);
const out = []; for (const T of T0) {
  await p.evaluate(h => { document.getElementById('c').innerHTML = h; }, m.frame(T)); await p.waitForTimeout(20); const f = `${pre}_${T.toFixed(2)}.png`; await p.screenshot({ path: f }); out.push(f); }
await b.close(); console.log(out.length);

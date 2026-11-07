// usage: node still.mjs <page.html rel to repo> t1,t2,... outprefix [WxH]
import { openPage } from './browser.mjs';
const [rel, ts, pre, size] = process.argv.slice(2);
const [W, H] = (size || '1080x1920').split('x').map(Number);
const [relPath, qs] = rel.split('?');
const P = await openPage(relPath, W, H, qs || '');
for (const t of ts.split(',').map(Number)) {
  const t0 = Date.now();
  await P.page.evaluate(async t => { await window.render(t); }, t);
  await P.page.screenshot({ path: `${pre}_${t.toFixed(2)}.png`, timeout: 600000 });
  console.log('still', t, (Date.now() - t0) + 'ms');
}
if (P.errs.length) { console.error(P.errs.join('\n')); process.exitCode = 1; }
await P.close();

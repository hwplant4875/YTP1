// Stills for thumbnails (the thumbnail sets its own words): like engine/still.mjs, but with the hook line and all
// big key text switched off; NOREADOUT=1 also hides the stack's running height readout.
// usage (from germany_shorts/peek/shorts/engine): node ../../longform/ep_money/tools/thumb_still.mjs germany_shorts/peek/longform/ep_money/episode.html 3.0,20.5 <outprefix> 1920x1080
import { openPage } from '../../../shorts/engine/browser.mjs';
const [rel, ts, pre, size] = process.argv.slice(2);
const [W, H] = size.split('x').map(Number);
const P = await openPage(rel, W, H, '');
const NORO = !!process.env.NOREADOUT;
await P.page.evaluate((NORO) => {
  window.ep.hookOut = -10;
  if (NORO) window.ep.opening.c.readout = false;   // no running height readout on the stack
  // no big key text at all (the payoff line): the thumbnail sets its own words
  for (const fn of ['fillText', 'strokeText']) {
    const orig = CanvasRenderingContext2D.prototype[fn];
    CanvasRenderingContext2D.prototype[fn] = function (...a) { if (/YTSans/.test(this.font)) return; return orig.apply(this, a); };
  }
}, NORO);
for (const t of ts.split(',').map(Number)) {
  await P.page.evaluate(async t => { await window.render(t); }, t);
  await P.page.screenshot({ path: `${pre}_${t.toFixed(2)}.png`, timeout: 600000 });
}
if (P.errs.length) { console.error(P.errs.join('\n')); process.exitCode = 1; }
await P.close();

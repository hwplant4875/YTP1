// usage: node dump_events.mjs <page.html rel> out.json  -- dumps scene timing tables (cue objects) from a loaded episode page
import { openPage } from './browser.mjs';
import { writeFileSync } from 'fs';
const [rel, out] = process.argv.slice(2);
const P = await openPage(rel, 1920, 1080, '');
const data = await P.page.evaluate(() => {
  const ep = window.ep;
  const nums = (o, depth = 0) => {
    const r = {};
    if (!o || depth > 2) return r;
    for (const k of Object.keys(o)) {
      const v = o[k];
      if (typeof v === 'number' && isFinite(v)) r[k] = +v.toFixed(3);
      else if (Array.isArray(v) && v.length && v.length <= 400 && v.every(x => typeof x === 'number' || x === undefined || x === null)) r[k] = v.map(x => (typeof x === 'number' ? +x.toFixed(3) : null));
      else if (v && typeof v === 'object' && !Array.isArray(v) && !(v instanceof HTMLElement) && !(v instanceof CanvasRenderingContext2D) && k.length <= 12 && depth < 2) {
        const sub = nums(v, depth + 1); if (Object.keys(sub).length) r[k] = sub;
      }
    }
    return r;
  };
  const scenes = ep.list.map(([t0, t1, s]) => ({ name: s.constructor ? s.constructor.name : 'fn', t0: +t0.toFixed(3), t1: +t1.toFixed(3), fields: nums(s) }));
  const op = ep.opening; const c = op.c;
  const inv = (T) => { let lo = -1, hi = 400; for (let n = 0; n < 60; n++) { const m = (lo + hi) / 2; if (c.warp(m) < T) lo = m; else hi = m; } return +(((lo + hi) / 2).toFixed(3)); };
  const opening = { VLAND: (op.VLAND || []).map(x => (x === undefined ? null : +x.toFixed(3))), ring: inv(c.ring), plane: inv(c.plane), issIn: inv(c.issIn), seven: inv(c.seven),
    pins: Object.fromEntries(Object.entries(c.pins).map(([k, v]) => [k, v == null ? null : (Array.isArray(v) ? v.map(inv) : inv(v))])), TA: inv(2.8), T11_3: inv(11.3), T13: inv(13), T14_5: inv(14.5), T17: inv(17) };
  return { scenes, opening, fields: nums(op) };
});
writeFileSync(out, JSON.stringify(data, null, 1));
await P.close(); console.log('ok', out);

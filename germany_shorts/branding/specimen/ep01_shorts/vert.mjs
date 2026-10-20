// 9:16 frame for a shark short: vertical sea background, the long-form scene cropped into a big window, a headline on top
import * as S1 from '/tmp/claude-0/sp2/s1.mjs'; import * as S2 from '/tmp/claude-0/sp2/s2.mjs'; import * as S3 from '/tmp/claude-0/sp2/s3.mjs';
import { K, f1, eo, pop, seed, rnd, esc } from '/tmp/claude-0/sp2/eng2.mjs';
import { PLANS } from './plan.mjs';
import { WIN } from './win.mjs';
import { VS } from './vs.mjs';
export { FONTS } from '/tmp/claude-0/sp2/eng2.mjs';
export const W = 1080, H = 1920;
const F = { ...S1, ...S2, ...S3 };
const BGK = { n16: 'deep', n17: 'deep', n18: 'night', n20: 'night', n21: 'deep', n22: 'deep', n23: 'night', n26: 'deep', n27: 'sand' };
const P = PLANS[process.env.SHORT];
export const TOTAL = P.total;
const bgV = (t, v) => {
  const g = v === 'deep' ? ['#1a5f9c', '#0b3866'] : v === 'night' ? ['#123a66', '#08203f'] : v === 'sand' ? ['#f6eedb', '#efe2c2'] : [K.sea1, K.sea2];
  let s = `<defs><linearGradient id="bgV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${g[0]}"/><stop offset="1" stop-color="${g[1]}"/></linearGradient></defs><rect width="${W}" height="${H}" fill="url(#bgV)"/>`;
  if (v === 'sand') return s;
  for (let i = 0; i < 3; i++) { const x = 100 + i * 380 + 50 * Math.sin(t * 0.3 + i); s += `<path d="M${f1(x)} -20 L${f1(x + 150)} -20 L${f1(x + 380)} ${H} L${f1(x + 100)} ${H}Z" fill="#ffffff" opacity="0.045"/>`; }
  seed(78); for (let i = 0; i < 30; i++) { const x0 = rnd() * W, sp = 30 + rnd() * 50, r = 3 + rnd() * 7, ph = rnd() * 3000;
    const y = H + 40 - ((t * sp + ph) % (H + 120)), x = x0 + 14 * Math.sin(t * 1.3 + i);
    s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(r)}" fill="none" stroke="#ffffff" stroke-width="2" opacity="0.28"/>`; }
  return s;
};
// headline: two lines max, big, white with navy outline; the hook headline is fully visible on frame 0
const head = (txt, t, hook, dark) => {
  const k = hook ? 1 + 0.06 * Math.max(0, 1 - t / 0.5) : pop(0, t, 0.3), words = txt.split(' ');
  let lines = [txt]; if (txt.length > 13) { let a = '', b = ''; for (const w of words) { if ((a + ' ' + w).trim().length <= Math.ceil(txt.length / 2) + 2 && !b) a = (a + ' ' + w).trim(); else b = (b + ' ' + w).trim(); } lines = [a, b]; }
  const size = Math.min(150, Math.floor(900 / (Math.max(...lines.map(l => l.length)) * 0.68))), y0 = 330 - (lines.length - 1) * size * 0.5;
  return `<g transform="translate(540 ${f1(y0)}) scale(${f1(k * 1000) / 1000})">${lines.map((l, i) => `<text x="0" y="${f1(i * size * 1.02 + size * 0.36)}" font-family="Black" font-size="${size}" fill="${i === lines.length - 1 && hook ? K.yellow : '#fff'}" stroke="${K.navy}" stroke-width="${f1(size * 0.13)}" paint-order="stroke" stroke-linejoin="round" text-anchor="middle">${esc(l)}</text>`).join('')}</g>`;
};
const brand = (dark) => `<text x="540" y="128" font-family="Black" font-size="44" fill="${dark ? K.navy : '#ffffff'}" opacity=".85" text-anchor="middle" letter-spacing="4">X-RAY ZOO</text>`;
export const frame = T => {
  let i = P.parts.length - 1; for (let k = 0; k < P.parts.length; k++) if (T < P.parts[k].T0 + P.parts[k].len) { i = k; break; }
  const p = P.parts[i], lt = T - p.T0, t = p.t0 + lt;
  const [wx, wy, ww, wh] = (WIN[process.env.SHORT] || {})[i] || (p.kind === 'hook' ? [260, 210, 1400, 860] : [160, 40, 1600, 1040]);
  const sc = W / ww, y = 900 - wh * sc / 2, z = p.kind === 'hook' ? 1.0 + 0.05 * (1 - eo(0, 2.5, lt)) : 1.03 - 0.03 * eo(0, 0.35, lt);
  const V = (VS[process.env.SHORT] || [])[i];
  if (V) return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${bgV(T, BGK[p.id])}${V(p.kind === 'hook' ? lt : t)}${brand(BGK[p.id] === 'sand')}${head(P.parts[0].head, T, true, BGK[p.id] === 'sand')}</svg>`;
  const body = F[p.id](t);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${bgV(T, BGK[p.id])}
    <svg x="0" y="${y}" width="${W}" height="${f1(wh * sc)}" viewBox="${wx} ${wy} ${ww} ${wh}" overflow="hidden"><g transform="translate(${wx + ww / 2} ${wy + wh / 2}) scale(${f1(z * 1000) / 1000}) translate(${-(wx + ww / 2)} ${-(wy + wh / 2)})">${body}</g></svg>
    ${brand(BGK[p.id] === 'sand')}${head(P.parts[0].head, T, true, BGK[p.id] === 'sand')}</svg>`;
};

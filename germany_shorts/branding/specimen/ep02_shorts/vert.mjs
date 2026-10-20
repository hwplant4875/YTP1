// 9:16 frame for a hummingbird short: vertical sky (or night) background, a dedicated vertical scene, brand + headline on top
import { K, f1, pop, seed, rnd, esc } from '/tmp/claude-0/sp2/eng2.mjs';
import { PLANS } from './plan.mjs';
import { VS } from './vs.mjs';
import { OUT } from './out.mjs';
import { PHOTO_DEFS } from '/tmp/claude-0/hb2/photos.mjs';
export { FONTS } from '/tmp/claude-0/sp2/eng2.mjs';
export const W = 1080, H = 1920;
export const EXTRA = PHOTO_DEFS();
const NIGHT = { h20: 1, h21: 1 };
const P = PLANS[process.env.SHORT];
export const TOTAL = P.total;
const bgV = (t, night) => {
  const g = night ? ['#1d2a5c', '#0b1433'] : ['#e3f4ff', '#b9e1f7'];
  let s = `<defs><linearGradient id="bgV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${g[0]}"/><stop offset="1" stop-color="${g[1]}"/></linearGradient></defs><rect width="${W}" height="${H}" fill="url(#bgV)"/>`;
  if (night) { seed(9); for (let i = 0; i < 45; i++) { const x = rnd() * W, y = rnd() * H * 0.85, r = 2 + rnd() * 3; s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(r)}" fill="#fff" opacity="${f1(0.3 + 0.5 * Math.abs(Math.sin(t + i)))}"/>`; } return s; }
  seed(31); for (let i = 0; i < 7; i++) { const w = 220 + rnd() * 200, y = 120 + rnd() * 1500, x = ((rnd() * (W + 600) + t * (12 + rnd() * 10)) % (W + 600)) - 300;
    s += `<g opacity=".75" fill="#fff"><ellipse cx="${f1(x)}" cy="${f1(y)}" rx="${f1(w / 2)}" ry="${f1(w / 7)}"/><ellipse cx="${f1(x - w / 6)}" cy="${f1(y - w / 9)}" rx="${f1(w / 5)}" ry="${f1(w / 6)}"/><ellipse cx="${f1(x + w / 8)}" cy="${f1(y - w / 8)}" rx="${f1(w / 4.5)}" ry="${f1(w / 5)}"/></g>`; }
  return s;
};
// headline: two lines max, big, white with navy outline, last line yellow; fully visible on frame 0
const head = (txt, t) => {
  const k = 1 + 0.06 * Math.max(0, 1 - t / 0.5), words = txt.split(' ');
  let lines = [txt]; if (txt.length > 13) { let a = '', b = ''; for (const w of words) { if ((a + ' ' + w).trim().length <= Math.ceil(txt.length / 2) + 2 && !b) a = (a + ' ' + w).trim(); else b = (b + ' ' + w).trim(); } lines = [a, b]; }
  const size = Math.min(150, Math.floor(900 / (Math.max(...lines.map(l => l.length)) * 0.68))), y0 = 330 - (lines.length - 1) * size * 0.5;
  return `<g transform="translate(540 ${f1(y0)}) scale(${f1(k * 1000) / 1000})">${lines.map((l, i) => `<text x="0" y="${f1(i * size * 1.02 + size * 0.36)}" font-family="Black" font-size="${size}" fill="${i === lines.length - 1 ? K.yellow : '#fff'}" stroke="${K.navy}" stroke-width="${f1(size * 0.13)}" paint-order="stroke" stroke-linejoin="round" text-anchor="middle">${esc(l)}</text>`).join('')}</g>`;
};
const brand = (night) => `<text x="540" y="128" font-family="Black" font-size="44" fill="${night ? '#ffffff' : K.navy}" opacity=".85" text-anchor="middle" letter-spacing="4">X-RAY ZOO</text>`;
export const frame = T => {
  let i = P.parts.length - 1; for (let k = 0; k < P.parts.length; k++) if (T < P.parts[k].T0 + P.parts[k].len) { i = k; break; }
  const p = P.parts[i], lt = T - p.T0, t = p.t0 + lt, night = NIGHT[p.id];
  const V = p.kind === 'outro' ? OUT(process.env.SHORT) : VS[process.env.SHORT][i];
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${bgV(T, night)}${V(p.kind === 'clip' ? t : lt, lt)}${brand(night)}${head(P.parts[0].head, T)}</svg>`;
};

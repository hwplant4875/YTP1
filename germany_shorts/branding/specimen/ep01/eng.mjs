// SPECIMEN motion-graphics engine (16:9, SVG frames rendered by Playwright)
import fs from 'fs';
export { SHARK, anatomy } from '/tmp/claude-0/hc/specimen.mjs';
const FD = '/tmp/claude-0/vz/flat/fonts/';
const ff = (n, f, fmt = 'woff2') => `@font-face{font-family:${n};src:url(data:font/${fmt};base64,${fs.readFileSync(f).toString('base64')})}`;
export const FONTS = ff('Mono', FD + 'mono.woff2') + ff('SerifI', FD + 'serif_i.woff2') + ff('Inter', FD + 'inter.woff2') + ff('InterB', FD + 'interb.woff2')
  + ff('Black', '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf', 'otf');
export const W = 1920, H = 1080;
export const C = { navy: '#0d0f1c', navy2: '#141729', ink: '#e9e6f2', dim: '#8a8aa6', faint: '#3a3d58', acc: '#3fd0ff', warm: '#ff8a7a', paper: '#eeeae1', pink: '#f2a7a0',
  pInk: '#16151c', pDim: '#7b7a88', red: '#e0482f', liver: '#d9a640', gold: '#ffcf6b' };
export const f1 = v => (Math.round(v * 10) / 10).toString();
export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
export const eo = (a, b, t) => { const x = clamp((t - a) / (b - a)); return 1 - Math.pow(1 - x, 3); };
export const lerp = (a, b, k) => a + (b - a) * k;
export const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
let _S = 1; export const seed = s => { _S = s; }; export const rnd = () => (_S = (_S * 16807) % 2147483647) / 2147483647;

export const open = (bg = C.navy) => `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>
<filter id="b3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="b8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="b20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="20"/></filter>
</defs><rect width="${W}" height="${H}" fill="${bg}"/>`;
export const close = (dark = true) => (dark ? `<rect width="${W}" height="${H}" fill="url(#vig)"/>` : '') + '</svg>';
export const grid = (col = '#ffffff', op = 0.035, step = 60) => { let s = ''; for (let x = 0; x <= W; x += step) s += `<path d="M${x} 0 L${x} ${H}" stroke="${col}" opacity="${op}"/>`;
  for (let y = 0; y <= H; y += step) s += `<path d="M0 ${y} L${W} ${y}" stroke="${col}" opacity="${op}"/>`; return s; };
export const mono = (x, y, t, { size = 18, fill = C.dim, anchor = 'start', op = 1, ls = 0, w = '' } = {}) =>
  op <= 0.005 ? '' : `<text x="${f1(x)}" y="${f1(y)}" font-family="Mono" font-size="${size}" fill="${fill}" text-anchor="${anchor}" opacity="${f1(op * 1000) / 1000}" letter-spacing="${ls}"${w}>${esc(t)}</text>`;
export const txt = (x, y, t, { font = 'Inter', size = 30, fill = C.ink, anchor = 'start', op = 1, ls = 0 } = {}) =>
  op <= 0.005 ? '' : `<text x="${f1(x)}" y="${f1(y)}" font-family="${font}" font-size="${size}" fill="${fill}" text-anchor="${anchor}" opacity="${f1(op * 1000) / 1000}" letter-spacing="${ls}">${esc(t)}</text>`;
// typed text with block cursor; chars revealed from t0 at cps
export const typed = (x, y, s, t, t0, { cps = 28, size = 22, fill = C.ink, cursor = true, font = 'Mono', anchor = 'start' } = {}) => {
  if (t < t0) return ''; const n = Math.min(s.length, Math.floor((t - t0) * cps)); const shown = s.slice(0, n);
  const blink = cursor && (n < s.length || Math.floor(t * 2) % 2 === 0);
  const cw = size * 0.6;
  return `<text x="${x}" y="${y}" font-family="${font}" font-size="${size}" fill="${fill}" text-anchor="${anchor}">${esc(shown)}</text>` +
    (blink && anchor === 'start' ? `<rect x="${f1(x + n * cw + 3)}" y="${f1(y - size * 0.8)}" width="${f1(size * 0.55)}" height="${f1(size * 0.95)}" fill="${fill}"/>` : '');
};
// lyric-style serif line: words appear one by one at given times (array), with rise + blur-in
export const words = (x, y, list, t, { size = 64, fill = C.ink, hi = {}, font = 'SerifI', anchor = 'start', dim = null } = {}) => {
  let s = `<text x="${x}" y="${y}" font-family="${font}" font-size="${size}" text-anchor="${anchor}">`;
  list.forEach(([w, tw], i) => { const k = eo(tw, tw + 0.35, t); if (k <= 0) { s += `<tspan fill="none"> ${esc(w)}</tspan>`; return; }
    s += `<tspan dy="0" fill="${hi[i] || fill}" opacity="${f1(k * 1000) / 1000}">${i ? ' ' : ''}${esc(w)}</tspan>`; });
  return s + '</text>';
};
// reveal a path by drawing (pathLength=1) with a leading glow dot handled by caller if needed
export const draw = (d, k, { stroke = C.ink, w = 2, op = 1, fill = 'none', extra = '' } = {}) => k <= 0 ? '' :
  `<path d="${d}" pathLength="1" stroke="${stroke}" stroke-width="${w}" fill="${fill}" opacity="${op}" stroke-dasharray="${f1(k * 1000) / 1000} 2" ${extra}/>`;
export const dot = (x, y, { r = 6, col = '#fff1d6', glow = C.acc } = {}) => `<circle cx="${f1(x)}" cy="${f1(y)}" r="${r * 3}" fill="${glow}" opacity=".25"/><circle cx="${f1(x)}" cy="${f1(y)}" r="${r}" fill="${col}"/>`;
// odometer-style number that cycles before landing
export const cycle = (target, t, t0, dur = 0.8) => { if (t < t0) return ''; if (t >= t0 + dur) return target;
  seed(Math.floor(t * 30) + 7); return target.replace(/[0-9]/g, () => String(Math.floor(rnd() * 10))); };
// standard document header
export const header = (t, section, idx, { dark = true } = {}) => {
  const c = dark ? C.dim : C.pDim;
  return mono(80, 78, 'SPECIMEN 001', { size: 18, fill: C.acc }) + mono(80, 104, `Carcharodon carcharias · ${section}`, { size: 16, fill: c })
    + mono(1840, 78, `${String(idx).padStart(2, '0')} / 25`, { size: 16, fill: c, anchor: 'end' }) + mono(1840, 104, 'great white shark', { size: 14, fill: c, anchor: 'end', op: 0.7 });
};
// label with leader line
export const label = (x, y, tx, ty, a, b, op = 1, { dark = true, anchor = 'start' } = {}) => {
  if (op <= 0.01) return ''; const ink = dark ? C.ink : C.pInk, off = anchor === 'end' ? -8 : 8;
  return `<g opacity="${f1(op * 1000) / 1000}"><path d="M${f1(x)} ${f1(y)} L${f1(tx)} ${f1(ty)}" stroke="${ink}" stroke-width="1.4" fill="none" opacity=".55"/>${dot(x, y, { r: 4.5 })}
   ${mono(tx + off, ty - 8, a, { size: 20, fill: ink, anchor })}${b ? mono(tx + off, ty + 20, b, { size: 15, fill: C.acc, anchor }) : ''}</g>`;
};
// shark figure helpers (box 1000x400) — place with transform
export const sharkG = (x, y, sc, inner, { rot = 0 } = {}) => `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${rot}) scale(${sc})">${inner}</g>`;

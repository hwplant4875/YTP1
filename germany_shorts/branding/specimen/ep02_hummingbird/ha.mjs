// X-RAY ZOO EP02 hummingbird: shared helpers and props
import { K, f1, clamp, sm, eo, pop, lerp, seed, rnd, esc } from '/tmp/claude-0/sp2/eng2.mjs';
import { birdSolid, birdInside, wings, placeB, toB, PT, C, BIRD, BEAK, SHOULDER } from '/tmp/claude-0/hb/bird.mjs';
export { birdSolid, birdInside, wings, placeB, toB, PT, C, BIRD, BEAK, SHOULDER };
const N = K.navy;
export const bobB = (t, a = 10, f = 2.2) => a * Math.sin(t * f);
let _i = 0; const uid = p => p + (_i++ % 100000);

// flying bird: body + beating wing (slowed so the eye can follow, with motion ghosts)
export const fly = (cx, cy, sc, t, { rate = 7, amp = 55, blur = 3, rot = 0, flip = false, inside = null, body = null, still = null } = {}) =>
  placeB(cx, cy, sc, (body || (inside ? birdInside(inside) : birdSolid())) + wings(t, { rate, amp, blur, still, bones: inside ? 1 : 0 }), { rot, flip });
// perched bird with folded wing
export const perched = (cx, cy, sc, { puff = 0, closed = 0, rot = 0, throat = 1 } = {}) => {
  const pf = `translate(600 330) scale(${f1((1 + 0.12 * puff) * 100) / 100} ${f1((1 + 0.22 * puff) * 100) / 100}) translate(-600 -330)`;
  let s = `<g transform="${pf}">${birdSolid({ throat })}${wings(0, { still: -76, blur: 0, fill: C.back })}`;
  if (closed) s += `<circle cx="714" cy="168" r="17" fill="${C.back}"/><path d="M699 166 Q714 ${f1(166 + 12 * closed)} 729 166" stroke="${N}" stroke-width="5" fill="none" stroke-linecap="round"/>`;
  s += '</g>';
  return placeB(cx, cy, sc, s, { rot });
};
// branch the perched bird holds (feet at box y≈446)
export const branch = (x0, x1, y, th = 22) => { const d = `M${x0} ${y} C${(x0 + x1) / 2} ${y - 18} ${(x0 + x1) / 2} ${y + 14} ${x1} ${y - 6}`;
  return `<path d="${d}" stroke="${N}" stroke-width="${th + 12}" fill="none" stroke-linecap="round"/><path d="${d}" stroke="#8a5a2b" stroke-width="${th}" fill="none" stroke-linecap="round"/>`; };

// red tubular flower (what hummingbirds love), mouth at (0,0) pointing up-left by default
export const flowerT = (x, y, s, { rot = -30, col = '#ff3d5e', col2 = '#c41f45', stem = 1, glowUV = 0 } = {}) => {
  let g = '';
  if (stem) g += `<path d="M0 196 C10 300 -10 420 20 600" stroke="#2f9a4f" stroke-width="16" fill="none" stroke-linecap="round"/><path d="M6 330 C70 280 140 300 160 344 C110 364 50 362 6 330Z" fill="#3fbf6a" stroke="${N}" stroke-width="6"/><path d="M8 450 C-50 410 -110 420 -130 460 C-80 480 -30 478 8 450Z" fill="#3fbf6a" stroke="${N}" stroke-width="6"/>`;
  g += `<path d="M-16 200 C-20 140 -28 70 -44 20 L44 20 C28 70 20 140 16 200 C8 210 -8 210 -16 200Z" fill="${col}" stroke="${N}" stroke-width="7" stroke-linejoin="round"/>`;
  g += `<path d="M-30 150 C-30 110 -34 70 -40 30" stroke="${col2}" stroke-width="6" fill="none" opacity=".6" stroke-linecap="round"/>`;
  g += `<path d="M-44 20 C-80 18 -110 0 -120 -20 C-90 -26 -60 -16 -40 -4 C-46 -30 -40 -56 -24 -70 C-10 -48 -6 -24 -2 -6 C4 -26 18 -50 36 -60 C44 -36 40 -14 34 -2 C56 -18 86 -26 116 -20 C104 2 76 18 44 20Z" fill="${col}" stroke="${N}" stroke-width="7" stroke-linejoin="round"/>`;
  g += `<ellipse cx="0" cy="10" rx="34" ry="10" fill="${col2}"/><path d="M0 10 L-10 -70 M6 10 L20 -66" stroke="#ffe27a" stroke-width="4" stroke-linecap="round"/><circle cx="-10" cy="-72" r="7" fill="#ffd23a" stroke="${N}" stroke-width="3"/><circle cx="20" cy="-68" r="7" fill="#ffd23a" stroke="${N}" stroke-width="3"/>`;
  if (glowUV) g += `<g opacity="${f1(glowUV)}"><path d="M-44 20 C-80 18 -110 0 -120 -20 C-90 -26 -60 -16 -40 -4 C-46 -30 -40 -56 -24 -70 C-10 -48 -6 -24 -2 -6 C4 -26 18 -50 36 -60 C44 -36 40 -14 34 -2 C56 -18 86 -26 116 -20 C104 2 76 18 44 20Z" fill="#a24bff" opacity=".8"/><circle cx="0" cy="8" r="40" fill="#ffffff" opacity=".85"/><path d="M-90 -10 L-20 8 M-30 -50 L-8 4 M28 -46 L10 4 M90 -16 L24 8" stroke="#f0e0ff" stroke-width="8" stroke-linecap="round"/><path d="M-16 200 C-20 140 -28 70 -44 20 L44 20 C28 70 20 140 16 200Z" fill="#6a2cff" opacity=".45"/></g>`;
  return `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(rot)}) scale(${f1(s * 1000) / 1000})">${g}</g>`;
};
// simple daisy-like flower for counting grids
export const blossom = (x, y, r, col = '#ff5f87', k = 1) => { if (k <= 0) return ''; let s = `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(k * 100) / 100})">`;
  for (let i = 0; i < 5; i++) { const a = i * 72 * Math.PI / 180; s += `<circle cx="${f1(Math.cos(a) * r * 0.62)}" cy="${f1(Math.sin(a) * r * 0.62)}" r="${f1(r * 0.48)}" fill="${col}" stroke="${N}" stroke-width="${f1(r * 0.09)}"/>`; }
  return s + `<circle r="${f1(r * 0.38)}" fill="${K.yellow}" stroke="${N}" stroke-width="${f1(r * 0.09)}"/></g>`; };

// coin
export const coin = (x, y, r) => `<g transform="translate(${f1(x)} ${f1(y)})"><ellipse cx="0" cy="${f1(r * 0.18)}" rx="${r}" ry="${f1(r * 0.34)}" fill="#a87412" stroke="${N}" stroke-width="7"/><ellipse cx="0" cy="0" rx="${r}" ry="${f1(r * 0.34)}" fill="#f2c13a" stroke="${N}" stroke-width="7"/><ellipse cx="0" cy="0" rx="${f1(r * 0.72)}" ry="${f1(r * 0.24)}" fill="none" stroke="#c99512" stroke-width="5"/></g>`;
// kitchen scale with a digital readout, pan top at (x, y)
export const scale = (x, y, txt) => `<g transform="translate(${f1(x)} ${f1(y)})"><rect x="-240" y="30" width="480" height="150" rx="28" fill="#ffffff" stroke="${N}" stroke-width="8"/><rect x="-120" y="70" width="240" height="78" rx="12" fill="${N}"/><text x="0" y="128" font-family="Black" font-size="56" fill="#7dffb0" text-anchor="middle">${esc(txt)}</text><path d="M-260 20 L260 20" stroke="${N}" stroke-width="22" stroke-linecap="round"/><path d="M-40 20 L-40 34 M40 20 L40 34" stroke="${N}" stroke-width="10"/></g>`;
// honey bee, centred, ~200 px long
export const bee = (x, y, s, t = 0) => { const w = 18 * Math.sin(t * 60);
  return `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><ellipse cx="-10" cy="-50" rx="46" ry="26" transform="rotate(${f1(-30 + w)} -10 -30)" fill="#ffffff" opacity=".75" stroke="${N}" stroke-width="5"/><ellipse cx="20" cy="-48" rx="40" ry="22" transform="rotate(${f1(-50 + w)} 20 -30)" fill="#ffffff" opacity=".75" stroke="${N}" stroke-width="5"/>
  <ellipse cx="0" cy="0" rx="78" ry="46" fill="${K.yellow}" stroke="${N}" stroke-width="7"/><path d="M-30 -42 C-38 -10 -38 10 -30 42 M2 -46 C-6 -14 -6 14 2 46 M34 -40 C28 -12 28 12 34 40" stroke="${N}" stroke-width="16" fill="none"/>
  <circle cx="82" cy="-6" r="30" fill="${N}"/><circle cx="92" cy="-14" r="7" fill="#fff"/><path d="M100 -30 Q120 -60 140 -62 M92 -34 Q104 -66 118 -74" stroke="${N}" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M-78 0 L-104 0" stroke="${N}" stroke-width="8" stroke-linecap="round"/></g>`; };
// human heart outline (simple) for comparisons
export const heartIcon = (x, y, s, col = K.red) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 1000) / 1000})"><path d="M0 70 C-90 10 -110 -50 -70 -80 C-40 -100 -10 -86 0 -60 C10 -86 40 -100 70 -80 C110 -50 90 10 0 70Z" fill="${col}" stroke="${N}" stroke-width="9" stroke-linejoin="round"/><path d="M-56 -50 C-66 -34 -64 -16 -54 -4" stroke="#fff" stroke-width="10" fill="none" opacity=".5" stroke-linecap="round"/></g>`;
// anatomical bird heart big (same drawing as inside the bird)
export const birdHeart = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 1000) / 1000}) rotate(-20)"><path d="M-10 -34 C-12 -54 8 -64 24 -54 L20 -44 C10 -50 2 -46 2 -34Z" fill="#d63a46" stroke="${N}" stroke-width="2.4"/><path d="M8 -36 C14 -50 30 -50 34 -40 L28 -34Z" fill="#7a8fd6" stroke="${N}" stroke-width="2.4"/>
  <path d="M-2 -36 C24 -40 38 -18 32 6 C26 28 10 44 -2 52 C-16 42 -32 22 -34 0 C-36 -20 -24 -34 -2 -36Z" fill="${C.heart}" stroke="${N}" stroke-width="2.6"/><path d="M2 -30 C8 -6 6 22 -2 48" stroke="#b8283a" stroke-width="3" fill="none"/><path d="M-22 -18 C-28 -6 -28 8 -22 20" stroke="#fff" stroke-width="5" fill="none" opacity=".45" stroke-linecap="round"/></g>`;
// person silhouette (simple, friendly) ~ 300 px tall, feet at (x,y)
export const kid = (x, y, s, c = '#ffffff') => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><circle cx="0" cy="-250" r="52" fill="#ffd9b8" stroke="${N}" stroke-width="8"/><path d="M-70 -180 Q0 -200 70 -180 L80 -60 L50 -60 L50 0 L10 0 L10 -60 L-10 -60 L-10 0 L-50 0 L-50 -60 L-80 -60Z" fill="${c}" stroke="${N}" stroke-width="8" stroke-linejoin="round"/><circle cx="18" cy="-258" r="6" fill="${N}"/><circle cx="-14" cy="-258" r="6" fill="${N}"/><path d="M-14 -228 Q2 -216 18 -228" stroke="${N}" stroke-width="5" fill="none" stroke-linecap="round"/></g>`;
// round gauge: value 0..1 (needle), label under
export const gauge = (x, y, r, v, { lab = '', red = 0.8, lo = '', hi = '', rev = 0 } = {}) => { const a0 = Math.PI * 0.85, a1 = Math.PI * 2.15, A = a => [x + Math.cos(a) * r, y + Math.sin(a) * r];
  const arc = (u0, u1, c, w) => { const p0 = A(lerp(a0, a1, u0)), p1 = A(lerp(a0, a1, u1)); return `<path d="M${f1(p0[0])} ${f1(p0[1])} A${r} ${r} 0 ${(u1 - u0) * 1.3 > 1 ? 1 : 0} 1 ${f1(p1[0])} ${f1(p1[1])}" stroke="${c}" stroke-width="${w}" fill="none"/>`; };
  const na = lerp(a0, a1, clamp(v)), np = [x + Math.cos(na) * r * 0.82, y + Math.sin(na) * r * 0.82];
  let s = `<circle cx="${x}" cy="${y}" r="${f1(r * 1.18)}" fill="#ffffff" stroke="${N}" stroke-width="10"/>` + (rev ? arc(0, red, K.red, r * 0.16) + arc(red, 1, '#2fd47a', r * 0.16) : arc(0, red, '#2fd47a', r * 0.16) + arc(red, 1, K.red, r * 0.16));
  for (let i = 0; i <= 10; i++) { const a = lerp(a0, a1, i / 10), p = [x + Math.cos(a) * r * 0.66, y + Math.sin(a) * r * 0.66], q = [x + Math.cos(a) * r * 0.76, y + Math.sin(a) * r * 0.76]; s += `<path d="M${f1(p[0])} ${f1(p[1])} L${f1(q[0])} ${f1(q[1])}" stroke="${N}" stroke-width="5"/>`; }
  s += `<path d="M${x} ${y} L${f1(np[0])} ${f1(np[1])}" stroke="${N}" stroke-width="14" stroke-linecap="round"/><circle cx="${x}" cy="${y}" r="${f1(r * 0.12)}" fill="${N}"/>`;
  if (lo) { const p = [x + Math.cos(a0) * r * 0.5, y + Math.sin(a0) * r * 0.5], q = [x + Math.cos(a1) * r * 0.5, y + Math.sin(a1) * r * 0.5];
    s += `<text x="${f1(p[0])}" y="${f1(p[1] + r * 0.1)}" font-family="Black" font-size="${f1(r * 0.26)}" fill="${N}" text-anchor="middle">${lo}</text><text x="${f1(q[0])}" y="${f1(q[1] + r * 0.1)}" font-family="Black" font-size="${f1(r * 0.26)}" fill="${N}" text-anchor="middle">${hi}</text>`; }
  if (lab) s += `<text x="${x}" y="${f1(y + r * 0.62)}" font-family="Black" font-size="${f1(r * 0.24)}" fill="${N}" text-anchor="middle">${lab}</text>`;
  return s; };
// big number readout box
export const readout = (x, y, num, unit, { size = 150, col = '#fff', ucol = N, w = 0 } = {}) =>
  `<text x="${f1(x)}" y="${f1(y)}" font-family="Black" font-size="${size}" fill="${col}" text-anchor="middle" stroke="${N}" stroke-width="${f1(size * 0.11)}" paint-order="stroke">${esc(num)}</text>` +
  (unit ? `<text x="${f1(x)}" y="${f1(y + size * 0.62)}" font-family="Black" font-size="${f1(size * 0.36)}" fill="${ucol}" text-anchor="middle">${esc(unit)}</text>` : '');
// rounded panel
export const card = (x, y, w, h, fill = '#ffffff', o = 1) => `<rect x="${f1(x)}" y="${f1(y)}" width="${f1(w)}" height="${f1(h)}" rx="40" fill="${fill}" opacity="${o}" stroke="${N}" stroke-width="9"/>`;
// ECG trace that scrolls (beats per second bps), drawn from x0..x1 at baseline y
export const ecg = (x0, x1, y, t, bps, { amp = 120, col = K.red, w = 10 } = {}) => {
  const per = Math.max(30, 220 / Math.max(bps, 0.2) * 0.9); let d = `M${x0} ${y}`;
  const off = (t * bps * per) % per;
  for (let x = x0 - per + (per - off); x < x1 + per; x += per) {
    const pts = [[0, 0], [per * 0.32, 0], [per * 0.38, -amp * 0.15], [per * 0.42, 0], [per * 0.48, 0], [per * 0.52, -amp], [per * 0.57, amp * 0.6], [per * 0.62, 0], [per * 0.75, -amp * 0.18], [per * 0.82, 0]];
    for (const [dx, dy] of pts) { const X = x + dx; if (X < x0 || X > x1) continue; d += ` L${f1(X)} ${f1(y + dy)}`; } }
  return `<path d="${d} L${x1} ${y}" stroke="${col}" stroke-width="${w}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>`; };
// clock/timer pie
export const timer = (x, y, r, k, col = K.yellow) => { const a = -Math.PI / 2 + k * Math.PI * 2, big = k > 0.5 ? 1 : 0;
  return `<circle cx="${f1(x)}" cy="${f1(y)}" r="${r}" fill="#fff" stroke="${N}" stroke-width="6"/>` + (k > 0.001 ? (k >= 0.999 ? `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(r - 8)}" fill="${col}"/>` : `<path d="M${f1(x)} ${f1(y)} L${f1(x)} ${f1(y - r + 8)} A${r - 8} ${r - 8} 0 ${big} 1 ${f1(x + Math.cos(a) * (r - 8))} ${f1(y + Math.sin(a) * (r - 8))}Z" fill="${col}"/>`) : '') + `<path d="M${f1(x)} ${f1(y)} L${f1(x)} ${f1(y - r * 0.6)}" stroke="${N}" stroke-width="5" stroke-linecap="round"/>`; };
// motion lines behind something moving left->right (towards +x)
export const speed = (x, y, n = 4, len = 160, o = 0.8) => { let s = ''; for (let i = 0; i < n; i++) s += `<path d="M${f1(x - len - i * 30)} ${f1(y - 60 + i * 40)} L${f1(x - 40 - i * 20)} ${f1(y - 60 + i * 40)}" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity="${o}"/>`; return s; };
// arrow from a to b
export const arrow = (x1, y1, x2, y2, { col = '#fff', w = 16, head = 44, dash = '' } = {}) => { const a = Math.atan2(y2 - y1, x2 - x1), hx = x2 - Math.cos(a) * head * 0.8, hy = y2 - Math.sin(a) * head * 0.8;
  return `<path d="M${f1(x1)} ${f1(y1)} L${f1(hx)} ${f1(hy)}" stroke="${col}" stroke-width="${w}" stroke-linecap="round" ${dash ? `stroke-dasharray="${dash}"` : ''}/><path d="M${f1(x2)} ${f1(y2)} L${f1(x2 - Math.cos(a - 0.5) * head)} ${f1(y2 - Math.sin(a - 0.5) * head)} L${f1(x2 - Math.cos(a + 0.5) * head)} ${f1(y2 - Math.sin(a + 0.5) * head)}Z" fill="${col}" stroke="${N}" stroke-width="5" stroke-linejoin="round"/>`; };
export { uid };

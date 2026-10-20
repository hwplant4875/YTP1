// X-RAY ZOO EP02 hummingbird: shared helpers and props
import { K, f1, clamp, sm, eo, pop, lerp, seed, rnd, esc } from '/tmp/claude-0/sp2/eng2.mjs';
import { birdSolid, birdInside, wings, placeB, toB, PT, C, BIRD, BEAK, SHOULDER, prettyHeart, prettyBrain, brainWindow, standB, FOOT_Y, birdDefs, WING, PAL } from '/tmp/claude-0/hb/bird.mjs';
export { PAL } from '/tmp/claude-0/hb/bird.mjs';
export { birdSolid, birdInside, wings, placeB, toB, PT, C, BIRD, BEAK, SHOULDER, prettyHeart, prettyBrain, brainWindow, standB, FOOT_Y, birdDefs, WING };
const N = K.navy;
export const bobB = (t, a = 10, f = 2.2) => a * Math.sin(t * f);
let _i = 0; const uid = p => p + (_i++ % 100000);

// flying bird: body + beating wing (slowed so the eye can follow, with motion ghosts)
export const fly = (cx, cy, sc, t, { rate = 7, amp = 55, blur = 3, rot = 0, flip = false, inside = null, body = null, still = null } = {}) =>
  placeB(cx, cy, sc, (body || (inside ? birdInside(inside) : birdSolid())) + wings(t, { rate, amp, blur, still, bones: inside ? 1 : 0 }), { rot, flip });
// perched bird with folded wing
export const perchedInner = ({ puff = 0, closed = 0, throat = 1, tailRot = 0, pal = 'ruby', beakD = null } = {}) => {
  const pf = `translate(600 452) scale(${f1((1 + 0.12 * puff) * 100) / 100} ${f1((1 + 0.22 * puff) * 100) / 100}) translate(-600 -452)`, bk = PAL[pal].b;
  let s = `<g transform="${pf}">${birdSolid({ throat, tailRot, pal, beakD })}${wings(0, { still: -76, blur: 0, fill: bk })}`;
  if (closed) s += `<circle cx="711" cy="170" r="21" fill="${bk}"/><path d="M699 166 Q714 ${f1(166 + 12 * closed)} 729 166" stroke="${N}" stroke-width="5" fill="none" stroke-linecap="round"/>`;
  return s + '</g>'; };
// bird standing on a flat surface: toes on groundY, tail lifted clear of the ground
export const standing = (cx, groundY, sc, o = {}) => standB(cx, groundY, sc, `<g transform="rotate(${o.lean ?? -14} 584 450)">${perchedInner({ tailRot: 30, ...o })}</g>`, { flip: o.flip });
// bird perched on a branch drawn with branch(..., by, th): toes sit on the top of the bark
export const onBranch = (cx, by, sc, o = {}) => standB(cx, by - (o.th ?? 22) * 0.5 - 4, sc, `<g transform="rotate(${o.lean ?? 0} 584 450)">${perchedInner(o)}</g>`, { flip: o.flip, rot: o.rot });
export const perched = (cx, cy, sc, { puff = 0, closed = 0, rot = 0, throat = 1 } = {}) => {
  const pf = `translate(600 452) scale(${f1((1 + 0.12 * puff) * 100) / 100} ${f1((1 + 0.22 * puff) * 100) / 100}) translate(-600 -452)`;
  let s = `<g transform="${pf}">${birdSolid({ throat })}${wings(0, { still: -76, blur: 0, fill: C.back })}`;
  if (closed) s += `<circle cx="711" cy="170" r="21" fill="${C.back}"/><path d="M699 166 Q714 ${f1(166 + 12 * closed)} 729 166" stroke="${N}" stroke-width="5" fill="none" stroke-linecap="round"/>`;
  s += '</g>';
  return placeB(cx, cy, sc, s, { rot });
};
// branch the perched bird holds (feet at box y≈446)
export const branch = (x0, x1, y, th = 22, { leaves = 1 } = {}) => { const d = `M${x0} ${y} C${(x0 + x1) / 2} ${y - 18} ${(x0 + x1) / 2} ${y + 14} ${x1} ${y - 6}`;
  const L = x1 - x0, yb = x => { const u = (x - x0) / L; return y * (1 - u) ** 3 + 3 * (1 - u) ** 2 * u * (y - 18) + 3 * (1 - u) * u * u * (y + 14) + u ** 3 * (y - 6); };
  let s = '';
  // side twig with leaves (behind the branch)
  if (leaves) for (const [u, dir] of [[0.18, -1], [0.78, 1]]) { const bx = x0 + L * u, by = yb(bx), tx = bx + dir * 90, ty = by - 120;
    s += `<path d="M${f1(bx)} ${f1(by)} Q${f1(bx + dir * 20)} ${f1(by - 70)} ${f1(tx)} ${f1(ty)}" stroke="${N}" stroke-width="${f1(th * 0.55 + 10)}" fill="none" stroke-linecap="round"/><path d="M${f1(bx)} ${f1(by)} Q${f1(bx + dir * 20)} ${f1(by - 70)} ${f1(tx)} ${f1(ty)}" stroke="#8a5a2b" stroke-width="${f1(th * 0.55)}" fill="none" stroke-linecap="round"/>`;
    for (const [lx, ly, a] of [[tx, ty, dir * 30 - 90], [bx + dir * 30, by - 60, dir * 70 - 90], [tx - dir * 10, ty + 30, dir * 110 - 90]]) s += leaf(lx, ly, a, th / 22); }
  s += `<path d="${d}" stroke="${N}" stroke-width="${th + 12}" fill="none" stroke-linecap="round"/><path d="${d}" stroke="#8a5a2b" stroke-width="${th}" fill="none" stroke-linecap="round"/>`;
  s += `<path d="${d}" stroke="#b9854b" stroke-width="${f1(th * 0.28)}" fill="none" stroke-linecap="round" transform="translate(0 ${f1(-th * 0.22)})" opacity=".9"/>`;
  seed(Math.round(x0 + y)); for (let i = 0; i < L / 60; i++) { const x = x0 + 30 + rnd() * (L - 60), yy = yb(x) + (rnd() - 0.3) * th * 0.4;
    s += `<path d="M${f1(x)} ${f1(yy)} l${f1(18 + rnd() * 24)} ${f1((rnd() - 0.5) * 4)}" stroke="#5e3c1b" stroke-width="${f1(Math.max(2, th * 0.12))}" stroke-linecap="round" opacity=".7"/>`; }
  return s; };
export const leaf = (x, y, a, k = 1) => `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(a)}) scale(${f1(k * 100) / 100})"><path d="M0 0 C18 -14 52 -18 84 0 C52 18 18 14 0 0Z" fill="#4fbf5a" stroke="${N}" stroke-width="5" stroke-linejoin="round"/><path d="M4 0 L76 0" stroke="#2f8a3c" stroke-width="3"/></g>`;
// flat ground with soil and a grassy edge; top at y
export const ground = (y, t = 0) => { let s = `<path d="M-40 ${y} L1960 ${y} L1960 1120 L-40 1120Z" fill="#c99a62" stroke="${N}" stroke-width="8"/><path d="M-40 ${y + 26} L1960 ${y + 26}" stroke="#b5864f" stroke-width="10" opacity=".6"/>`;
  seed(7); for (let i = 0; i < 26; i++) { const x = rnd() * 1920, yy = y + 50 + rnd() * 150; s += `<ellipse cx="${f1(x)}" cy="${f1(yy)}" rx="${f1(10 + rnd() * 16)}" ry="${f1(6 + rnd() * 6)}" fill="#a97a45" opacity=".7"/>`; }
  for (let x = -20; x < 1960; x += 26) { const h = 22 + 14 * Math.sin(x * 0.37), sw = 4 * Math.sin(t * 2 + x * 0.05); s += `<path d="M${x} ${y + 4} Q${f1(x + 4 + sw)} ${f1(y - h * 0.5)} ${f1(x + 8 + sw)} ${f1(y - h)}" stroke="#3f9a45" stroke-width="7" fill="none" stroke-linecap="round"/>`; }
  return s; };

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
export const heartIcon = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 1.45 * 1000) / 1000})">${birdDefs()}${prettyHeart(1, { sw: 4 })}</g>`;
// anatomical bird heart big (same drawing as inside the bird)
export const birdHeart = (x, y, s, k = 1) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 0.72 * 1000) / 1000}) rotate(-12)">${birdDefs()}${prettyHeart(k, { sw: 3.2 })}</g>`;
// real photo in a white frame that pops in (symbol P_<name> comes from photos.mjs, injected once per page)
export const photo = (name, x, y, w, h, k, { rot = -2, cap = '' } = {}) => { if (k <= 0) return '';
  const id = 'ph' + name.replace(/\W/g, '') + Math.round(x);
  return `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(rot * k)}) scale(${f1(k * 1000) / 1000})"><rect x="${f1(-w / 2 - 22 + 14)}" y="${f1(-h / 2 - 22 + 18)}" width="${f1(w + 44)}" height="${f1(h + 44 + (cap ? 90 : 0))}" rx="22" fill="#000" opacity=".22"/>
    <rect x="${f1(-w / 2 - 22)}" y="${f1(-h / 2 - 22)}" width="${f1(w + 44)}" height="${f1(h + 44 + (cap ? 90 : 0))}" rx="22" fill="#ffffff" stroke="${N}" stroke-width="7"/>
    <clipPath id="${id}"><rect x="${f1(-w / 2)}" y="${f1(-h / 2)}" width="${f1(w)}" height="${f1(h)}" rx="10"/></clipPath>
    <g clip-path="url(#${id})"><rect x="${f1(-w / 2)}" y="${f1(-h / 2)}" width="${f1(w)}" height="${f1(h)}" fill="#dfe6f0"/><use href="#P_${name}" x="${f1(-w / 2)}" y="${f1(-h / 2)}" width="${f1(w)}" height="${f1(h)}"/></g>
    ${cap ? `<text x="0" y="${f1(h / 2 + 74)}" font-family="Black" font-size="58" fill="${N}" text-anchor="middle">${esc(cap)}</text>` : ''}</g>`; };
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
// box point -> screen for placeB(cx, cy, sc, .., { rot })
export const bptB = (cx, cy, sc, rot, x, y) => { const r = rot * Math.PI / 180, dx = (x - 600) * sc, dy = (y - 300) * sc; return [cx + dx * Math.cos(r) - dy * Math.sin(r), cy + dx * Math.sin(r) + dy * Math.cos(r)]; };
// local flower point -> screen for flowerT(x, y, s, { rot })
export const fpt = (x, y, s, rot, lx, ly) => { const r = rot * Math.PI / 180; return [x + (lx * Math.cos(r) - ly * Math.sin(r)) * s, y + (lx * Math.sin(r) + ly * Math.cos(r)) * s]; };
// meadow: rolling grass hill + round bushes along the bottom (drawn in two layers so stems can tuck in between)
export const meadowBack = (t = 0) => { let s = `<path d="M-60 900 C300 840 620 880 960 860 C1300 840 1620 870 1980 850 L1980 1140 L-60 1140Z" fill="#7fcf6a" stroke="${N}" stroke-width="7"/>`;
  seed(41); for (let i = 0; i < 9; i++) { const x = -40 + i * 250 + rnd() * 60, y = 880 + rnd() * 30, r = 90 + rnd() * 50;
    s += `<g fill="#3fae5a" stroke="${N}" stroke-width="7"><circle cx="${f1(x - r * 0.6)}" cy="${f1(y + 10)}" r="${f1(r * 0.7)}"/><circle cx="${f1(x + r * 0.6)}" cy="${f1(y + 14)}" r="${f1(r * 0.75)}"/><circle cx="${f1(x)}" cy="${f1(y - r * 0.25)}" r="${f1(r)}"/></g>
      <path d="M${f1(x - r * 0.5)} ${f1(y - r * 0.5)} q${f1(r * 0.3)} -${f1(r * 0.2)} ${f1(r * 0.6)} 0" stroke="#7fe08f" stroke-width="7" fill="none" stroke-linecap="round" opacity=".7"/>`; }
  return s; };
export const meadowFront = (t = 0) => { let s = `<path d="M-60 1000 C400 960 800 1000 1200 980 C1500 966 1750 990 1980 975 L1980 1140 L-60 1140Z" fill="#5cbf5f" stroke="${N}" stroke-width="7"/>`;
  seed(77); for (let i = 0; i < 46; i++) { const x = rnd() * 1960, y = 990 + rnd() * 70, h = 26 + rnd() * 30, sw = 5 * Math.sin(t * 1.5 + i);
    s += `<path d="M${f1(x)} ${f1(y)} q${f1(4 + sw)} -${f1(h * 0.6)} ${f1(sw * 1.5 + 8)} -${f1(h)}" stroke="#2f8f4a" stroke-width="5" fill="none" stroke-linecap="round"/>`; }
  return s; };
// stem from a flower's tube end down into the bushes, with two leaves
export const stemTo = (x0, y0, x1, y1, sw = 14) => { const mx = x0 + (x1 - x0) * 0.3, my = y0 + (y1 - y0) * 0.22;
  return `<path d="M${f1(x0)} ${f1(y0)} C${f1(x0 + 30)} ${f1(my)} ${f1(x1 - 30)} ${f1(my)} ${f1(x1)} ${f1(y1)}" stroke="${N}" stroke-width="${sw + 10}" fill="none" stroke-linecap="round"/><path d="M${f1(x0)} ${f1(y0)} C${f1(x0 + 30)} ${f1(my)} ${f1(x1 - 30)} ${f1(my)} ${f1(x1)} ${f1(y1)}" stroke="#2f9a4f" stroke-width="${sw}" fill="none" stroke-linecap="round"/>
  <path d="M${f1(mx)} ${f1(my + 20)} C${f1(mx + 60)} ${f1(my - 30)} ${f1(mx + 130)} ${f1(my - 10)} ${f1(mx + 150)} ${f1(my + 30)} C${f1(mx + 100)} ${f1(my + 50)} ${f1(mx + 40)} ${f1(my + 48)} ${f1(mx)} ${f1(my + 20)}Z" fill="#3fbf6a" stroke="${N}" stroke-width="6"/>
  <path d="M${f1(mx - 4)} ${f1(my + 70)} C${f1(mx - 60)} ${f1(my + 30)} ${f1(mx - 120)} ${f1(my + 50)} ${f1(mx - 136)} ${f1(my + 86)} C${f1(mx - 90)} ${f1(my + 104)} ${f1(mx - 36)} ${f1(my + 98)} ${f1(mx - 4)} ${f1(my + 70)}Z" fill="#3fbf6a" stroke="${N}" stroke-width="6"/>`; };

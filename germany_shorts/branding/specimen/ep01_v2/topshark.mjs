// Top-view shark that bends along its swim path (spine warp), plus a fleeing fish.
import { K, f1, clamp } from './eng2.mjs';

// Catmull-Rom through waypoints, then resample by arc length
export function track(pts, n = 1400) {
  const P = [pts[0], ...pts, pts[pts.length - 1]], raw = [];
  for (let i = 1; i < P.length - 2; i++) for (let j = 0; j < 40; j++) {
    const u = j / 40, [p0, p1, p2, p3] = [P[i - 1], P[i], P[i + 1], P[i + 2]];
    const c = k => 0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u * u + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u * u * u);
    raw.push([c(0), c(1)]);
  }
  raw.push(pts[pts.length - 1]);
  const L = [0]; for (let i = 1; i < raw.length; i++) L.push(L[i - 1] + Math.hypot(raw[i][0] - raw[i - 1][0], raw[i][1] - raw[i - 1][1]));
  const len = L[L.length - 1];
  const at = s => { s = clamp(s, 0, len); let lo = 0, hi = L.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (L[m] <= s) lo = m; else hi = m; }
    const k = (s - L[lo]) / Math.max(1e-6, L[hi] - L[lo]); return [raw[lo][0] + (raw[hi][0] - raw[lo][0]) * k, raw[lo][1] + (raw[hi][1] - raw[lo][1]) * k]; };
  const dir = s => { const a = at(s - 3), b = at(s + 3), d = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1; return [(b[0] - a[0]) / d, (b[1] - a[1]) / d]; };
  return { at, dir, len };
}

// body frame: x along the body 0 (tail tip) .. 1000 (snout), n sideways (+ = right side)
// returns map(x, n) -> screen point, given head arc position sh, scale sc, swim phase ph and wave amplitude A
export function bodyMap(tr, sh, sc, ph, A = 34) {
  const cache = new Map();
  const spine = x => { const key = Math.round(x); if (cache.has(key)) return cache.get(key);
    const s = sh - (1000 - x) * sc, p = tr.at(s), d = tr.dir(s), nrm = [-d[1], d[0]];
    const r = (1000 - x) / 1000, w = A * sc * Math.pow(r, 1.7) * Math.sin(ph - r * 5.2);
    const v = [p[0] + nrm[0] * w, p[1] + nrm[1] * w, nrm]; cache.set(key, v); return v; };
  return (x, n) => { const [px, py, nr] = spine(x); return [px + nr[0] * n * sc, py + nr[1] * n * sc]; };
}

// half width of the top-view body at x
const HW = x => {
  if (x > 840) return 112 * Math.pow((1000 - x) / 160, 0.62);
  if (x > 640) return 112 + 6 * Math.sin((840 - x) / 200 * Math.PI / 2);
  if (x > 170) { const u = (640 - x) / 470; return 22 + (118 - 22) * (0.5 + 0.5 * Math.cos(u * Math.PI)); }
  return 22 - 12 * (170 - x) / 170;
};
const P = (m, x, n) => { const p = m(x, n); return `${f1(p[0])} ${f1(p[1])}`; };
// fins stay stiff: map them in the local frame at their root instead of along the bent spine
const rigid = (m, x0) => { const a = m(x0 - 12, 0), b = m(x0 + 12, 0), r = m(x0, 0), sc = Math.hypot(b[0] - a[0], b[1] - a[1]) / 24, tx = (b[0] - a[0]) / 24 / sc, ty = (b[1] - a[1]) / 24 / sc;
  return (x, n) => [r[0] + (x - x0) * sc * tx - n * sc * ty, r[1] + (x - x0) * sc * ty + n * sc * tx]; };
const poly = (m, pts) => 'M' + pts.map(([x, n]) => P(m, x, n)).join(' L') + 'Z';

export function topShark(m, { fill = '#ffffff', back = '#d7e1ee', stroke = K.navy, sw = 6, bite = 0 } = {}) {
  let s = '';
  // tail fin seen from above: thin vertical blade, plus caudal keel
  s += `<path d="${poly(m, [[150, -14], [-30, -8], [-60, 0], [-30, 8], [150, 14]])}" fill="${back}" stroke="${stroke}" stroke-width="${sw}" stroke-linejoin="round"/>`;
  // pelvic fins
  for (const sd of [-1, 1]) s += `<path d="${poly(rigid(m, 320), [[350, sd * 30], [300, sd * 78], [262, sd * 82], [290, sd * 28]])}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" stroke-linejoin="round"/>`;
  // pectoral fins: long swept-back wings
  for (const sd of [-1, 1]) s += `<path d="${poly(rigid(m, 640), [[700, sd * 80], [610, sd * 250], [540, sd * 300], [520, sd * 270], [560, sd * 90]])}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" stroke-linejoin="round"/>`;
  // body outline sampled along the spine
  const L = [], R = []; for (let x = 0; x <= 1000; x += 10) { L.push(P(m, x, -HW(x))); R.unshift(P(m, x, HW(x))); }
  s += `<path d="M${L.join(' L')} L${R.join(' L')}Z" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" stroke-linejoin="round"/>`;
  // darker grey back band (sharks are grey on top)
  const L2 = [], R2 = []; for (let x = 120; x <= 950; x += 10) { const w = HW(x) * 0.58; L2.push(P(m, x, -w)); R2.unshift(P(m, x, w)); }
  s += `<path d="M${L2.join(' L')} L${R2.join(' L')}Z" fill="${back}"/>`;
  // dorsal fin from above: a slim ridge
  s += `<path d="${poly(m, [[600, 0], [560, -10], [450, -6], [420, 0], [450, 6], [560, 10]])}" fill="#b8c6d8" stroke="${stroke}" stroke-width="${f1(sw * 0.7)}" stroke-linejoin="round"/>`;
  // gill slits on both sides
  for (const sd of [-1, 1]) for (let i = 0; i < 5; i++) { const x = 790 - i * 22, w = HW(x); s += `<path d="M${P(m, x, sd * (w - 4))} L${P(m, x - 10, sd * (w - 22))}" stroke="${stroke}" stroke-width="${f1(sw * 0.55)}" stroke-linecap="round" opacity=".6"/>`; }
  // eyes on the sides of the head + nostrils
  for (const sd of [-1, 1]) { const e = m(890, sd * HW(890) * 0.78); s += `<circle cx="${f1(e[0])}" cy="${f1(e[1])}" r="${f1(sw * 1.6)}" fill="${stroke}"/>`;
    const n = m(968, sd * HW(968) * 0.6); s += `<circle cx="${f1(n[0])}" cy="${f1(n[1])}" r="${f1(sw * 0.6)}" fill="${stroke}" opacity=".6"/>`; }
  // mouth flash when biting
  if (bite > 0) { const a = m(985, -40 * bite), b = m(1010, 0), c = m(985, 40 * bite);
    s += `<path d="M${f1(a[0])} ${f1(a[1])} Q${f1(b[0])} ${f1(b[1])} ${f1(c[0])} ${f1(c[1])}" stroke="#fff" stroke-width="${sw}" fill="none" stroke-linecap="round" opacity="${f1(bite)}"/>`; }
  return s;
}

// small fish seen from above, nose at (x,y) heading along d
export function topFish(x, y, d, t, sc = 1, col = '#ffd23f') {
  const ang = Math.atan2(d[1], d[0]) * 180 / Math.PI, wag = 22 * Math.sin(t * 22);
  return `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(ang)}) scale(${f1(sc * 100) / 100})">
    <g transform="translate(-62 0) rotate(${f1(wag)})"><path d="M0 0 L-38 -24 L-30 0 L-38 24Z" fill="${col}" stroke="${K.navy}" stroke-width="5" stroke-linejoin="round"/></g>
    <path d="M0 0 C-10 -20 -40 -22 -66 -8 L-66 8 C-40 22 -10 20 0 0Z" fill="${col}" stroke="${K.navy}" stroke-width="5" stroke-linejoin="round"/>
    <circle cx="-14" cy="-9" r="4" fill="${K.navy}"/><circle cx="-14" cy="9" r="4" fill="${K.navy}"/></g>`;
}

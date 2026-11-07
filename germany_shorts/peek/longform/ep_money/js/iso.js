// True isometric (orthographic) projection, right-handed world, z up.
// The camera looks along -(1,1,1): +x runs screen left-down, +y right-down, z up.
//   sx = ox + (y - x) * cos30 * k      sy = oy + ((x + y) / 2 - z) * k
// k = pixels per metre along a world axis; screen-parallel lengths scale by S = 1.2247 k.
export const W = 1920, H = 1080;
export const C30 = Math.cos(Math.PI / 6);
export const SQ15 = Math.sqrt(1.5);

export class Cam {
  constructor() { this.k = 1; this.ox = W / 2; this.oy = H / 2; }
  set(ox, oy, k) { this.k = k; this.ox = ox; this.oy = oy; }
  px(x, y) { return this.ox + (y - x) * C30 * this.k; }
  py(x, y, z) { return this.oy + ((x + y) * 0.5 - z) * this.k; }
  p(x, y, z) { return [this.ox + (y - x) * C30 * this.k, this.oy + ((x + y) * 0.5 - z) * this.k]; }
}

// ---------- colour ----------
export function rgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
export function mix(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }
export function css(c, a = 1) {
  return a >= 1 ? `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})` : `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a.toFixed(4)})`;
}
const WARM = rgb('#FFF8EC'), COOL = rgb('#231A2C');
// three tones per solid: top light, left (+x face) mid, right (+y face) dark
export function tones(hex) {
  const b = typeof hex === 'string' ? rgb(hex) : hex;
  return { top: css(mix(b, WARM, 0.2)), left: css(b), right: css(mix(b, COOL, 0.22)), base: b };
}

// ---------- easing ----------
export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a, b, t) => a + (b - a) * t;
export const sstep = (a, b, v) => { const t = clamp((v - a) / (b - a)); return t * t * (3 - 2 * t); };
export const smoother = (t) => { t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); };
export const easeOut = (t) => 1 - Math.pow(1 - clamp(t), 3);
export const easeIn = (t) => Math.pow(clamp(t), 3);
export function backOut(t, s = 1.70158) { t = clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1; }

// monotone cubic (Fritsch-Carlson) through [[t, v], ...]
export function monotone(pts) {
  const n = pts.length, xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const d = [], m = new Array(n);
  for (let i = 0; i < n - 1; i++) d.push((ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]));
  m[0] = d[0]; m[n - 1] = d[n - 2];
  for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
  for (let i = 0; i < n - 1; i++) {
    if (d[i] === 0) { m[i] = m[i + 1] = 0; continue; }
    const a = m[i] / d[i], b = m[i + 1] / d[i], s = a * a + b * b;
    if (s > 9) { const t = 3 / Math.sqrt(s); m[i] = t * a * d[i]; m[i + 1] = t * b * d[i]; }
  }
  return (x) => {
    if (x <= xs[0]) return ys[0];
    if (x >= xs[n - 1]) return ys[n - 1];
    let i = 0; while (x > xs[i + 1]) i++;
    const h = xs[i + 1] - xs[i], t = (x - xs[i]) / h, t2 = t * t, t3 = t2 * t;
    return (2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h * m[i] + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h * m[i + 1];
  };
}

export function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------- drawing ----------
// filled polygon from world points; a thin same-colour stroke hides AA seams between faces
export function poly(ctx, cam, pts, fill, seam = 0.9) {
  ctx.beginPath();
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i];
    const x = cam.px(p[0], p[1]), y = cam.py(p[0], p[1], p[2]);
    if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y);
  }
  ctx.closePath();
  ctx.fillStyle = fill; ctx.fill();
  if (seam) { ctx.strokeStyle = fill; ctx.lineWidth = seam; ctx.lineJoin = 'round'; ctx.stroke(); }
}

export function box(ctx, cam, x0, y0, z0, sx, sy, sz, T, seam = 0.9) {
  const x1 = x0 + sx, y1 = y0 + sy, z1 = z0 + sz;
  poly(ctx, cam, [[x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]], T.left, seam);
  poly(ctx, cam, [[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], T.right, seam);
  poly(ctx, cam, [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], T.top, seam);
}

// square frustum centred at (cx, cy): half size a at z0, b at z1
export function frustum(ctx, cam, cx, cy, z0, z1, a, b, T) {
  poly(ctx, cam, [[cx + a, cy - a, z0], [cx + a, cy + a, z0], [cx + b, cy + b, z1], [cx + b, cy - b, z1]], T.left);
  poly(ctx, cam, [[cx - a, cy + a, z0], [cx + a, cy + a, z0], [cx + b, cy + b, z1], [cx - b, cy + b, z1]], T.right);
  poly(ctx, cam, [[cx - b, cy - b, z1], [cx + b, cy - b, z1], [cx + b, cy + b, z1], [cx - b, cy + b, z1]], T.top);
}

// draw an image onto the parallelogram O + u*E1 + v*E2 (image coords 0..w, 0..h)
export function texQuad(ctx, img, O, E1, E2) {
  ctx.save();
  ctx.setTransform(E1[0] / img.width, E1[1] / img.width, E2[0] / img.height, E2[1] / img.height, O[0], O[1]);
  ctx.drawImage(img, 0, 0);
  ctx.restore();
}

// ---------- type ----------
export const FONT = 'Jost';
export function label(ctx, s, x, y, o) {
  const size = o.size || 28, weight = o.weight || 400;
  ctx.font = `${weight} ${size}px ${FONT}`;
  ctx.letterSpacing = (o.track || 0) + 'px';
  ctx.textAlign = o.align || 'left';
  ctx.textBaseline = o.base || 'alphabetic';
  ctx.globalAlpha = o.a === undefined ? 1 : o.a;
  // mode 'halo' / 'fill' draws one pass only, so lines can sit between a halo and its glyphs
  if (o.halo && o.mode !== 'fill') {
    ctx.lineJoin = 'round'; ctx.miterLimit = 2;
    ctx.strokeStyle = o.halo; ctx.lineWidth = o.haloW || 14; ctx.strokeText(s, x, y);
  }
  if (o.mode !== 'halo') { ctx.fillStyle = o.color; ctx.fillText(s, x, y); }
  const w = ctx.measureText(s).width;
  ctx.globalAlpha = 1; ctx.letterSpacing = '0px';
  return w;
}

// Label pin: dot (ink ring, pale fill) -> vertical leader -> horizontal rule -> text.
// p = build progress 0..1, a = overall alpha, dir = +1 (rule to the right) / -1 (left)
export function pin(ctx, ax, ay, o) {
  const p = o.p === undefined ? 1 : o.p, a = o.a === undefined ? 1 : o.a;
  if (p <= 0 || a <= 0) return;
  const ink = o.ink, paper = o.paper, dir = o.dir || 1, lead = o.lead || 60, rule = o.rule || 260;
  const sDot = backOut((p - 0.0) / 0.22), pl = easeOut((p - 0.12) / 0.3), pr = easeOut((p - 0.32) / 0.3);
  const pt = easeOut((p - 0.5) / 0.5);
  // text is laid out first and drawn in two passes (halos, then glyphs) around the leader, rule
  // and dot, so a halo never cuts the rule under a comma or the leader beside the title
  const txt = [];
  if (pt > 0) {
    const ry = ay - lead, x0 = dir > 0 ? ax + 6 : ax - 6, al = dir > 0 ? 'left' : 'right', rise = (1 - pt) * 12;
    const halo = o.halo || paper;
    if (o.num) {
      const ns = o.numSize || 66, us = Math.round(ns * 0.5);
      // number + unit on one baseline, sitting on the rule
      ctx.font = `400 ${ns}px ${FONT}`; ctx.letterSpacing = '0px';
      const nw = ctx.measureText(o.num).width;
      ctx.font = `500 ${us}px ${FONT}`; ctx.letterSpacing = `${(us * 0.08).toFixed(1)}px`;
      const uw = o.unit ? ctx.measureText(' ' + o.unit).width : 0;
      ctx.letterSpacing = '0px';
      const total = nw + uw, sx = dir > 0 ? x0 : x0 - total, by = ry - 14 + rise;
      txt.push([o.num, sx, by, { size: ns, weight: 400, color: ink, halo, haloW: 14, a: a * pt }]);
      if (o.unit) txt.push([' ' + o.unit, sx + nw, by, { size: us, weight: 500, color: ink, halo, haloW: 12, a: a * pt, track: us * 0.08 }]);
    }
    if (o.title) {
      const ts = o.titleSize || 24;
      txt.push([o.title.toUpperCase(), x0, ry + ts + 12 + rise * 0.5, { size: ts, weight: 600, color: ink, halo, haloW: 12, a: a * pt, align: al, track: ts * 0.12 }]);
    }
  }
  for (const [s, x, y, q] of txt) label(ctx, s, x, y, { ...q, mode: 'halo' });
  ctx.save();
  ctx.globalAlpha = a;
  ctx.strokeStyle = ink; ctx.lineWidth = o.lw || 2.4; ctx.lineCap = 'round';
  const top = ay - lead * pl;
  if (pl > 0) { ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(ax, top); ctx.stroke(); }
  if (pr > 0) { ctx.beginPath(); ctx.moveTo(ax, ay - lead); ctx.lineTo(ax + dir * rule * pr, ay - lead); ctx.stroke(); }
  if (sDot > 0) {
    const r = (o.dot || 8) * sDot;
    ctx.beginPath(); ctx.arc(ax, ay, r, 0, Math.PI * 2);
    ctx.fillStyle = paper; ctx.fill(); ctx.lineWidth = 2.6; ctx.stroke();
  }
  ctx.restore();
  for (const [s, x, y, q] of txt) label(ctx, s, x, y, { ...q, mode: 'fill' });
}

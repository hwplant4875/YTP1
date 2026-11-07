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
  // tp / ttp: optional separate progress for the number line and the title line
  const ptn = o.tp !== undefined ? easeOut(o.tp) : pt, ptt = o.ttp !== undefined ? easeOut(o.ttp) : pt;
  // text is laid out first and drawn in two passes (halos, then glyphs) around the leader, rule
  // and dot, so a halo never cuts the rule under a comma or the leader beside the title
  const txt = [];
  if (ptn > 0 || ptt > 0) {
    const ry = ay - lead, x0 = dir > 0 ? ax + 6 : ax - 6, al = dir > 0 ? 'left' : 'right', rise = (1 - ptn) * 12, riseT = (1 - ptt) * 12;
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
      if (ptn > 0) txt.push([o.num, sx, by, { size: ns, weight: 400, color: o.numColor || ink, halo, haloW: 14, a: a * ptn }]);
      if (o.unit && ptn > 0) txt.push([' ' + o.unit, sx + nw, by, { size: us, weight: 500, color: o.numColor || ink, halo, haloW: 12, a: a * ptn, track: us * 0.08 }]);
    }
    if (o.title) {
      const ts = o.titleSize || 24;
      if (ptt > 0) txt.push([o.title.toUpperCase(), x0, ry + ts + 12 + riseT * 0.5, { size: ts, weight: 600, color: ink, halo, haloW: 12, a: a * ptt, align: al, track: ts * 0.12 }]);
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

// ---------- camera helpers ----------
// put world point (x, y, z) at screen (sx, sy) with a frame `fh` world units tall
export function camLook(cam, x, y, z, fh, sx = W / 2, sy = H / 2) {
  const k = H / fh;
  cam.set(sx - (y - x) * C30 * k, sy - ((x + y) * 0.5 - z) * k, k);
}
// keys: [[t, x, y, z, fh, sx?, sy?], ...]; smootherstep between keys, frame height eased in log space;
// a key with .lin = true moves linearly to the next key (a slow drift through a long hold)
export function camPath(keys) {
  return (t) => {
    if (t <= keys[0][0]) return keys[0];
    for (let i = 0; i < keys.length - 1; i++) {
      const a = keys[i], b = keys[i + 1];
      if (t > b[0]) continue;
      const v = (t - a[0]) / (b[0] - a[0]), u = a.lin ? Math.min(1, Math.max(0, v)) : smoother(v);
      const r = [t];
      for (let j = 1; j < Math.max(a.length, b.length); j++) {
        const va = a[j] ?? (j === 5 ? W / 2 : H / 2), vb = b[j] ?? (j === 5 ? W / 2 : H / 2);
        r.push(j === 4 ? Math.exp(Math.log(va) + (Math.log(vb) - Math.log(va)) * u) : va + (vb - va) * u);
      }
      return r;
    }
    return keys[keys.length - 1];
  };
}
export function applyCam(cam, k) { camLook(cam, k[1], k[2], k[3], k[4], k[5] ?? W / 2, k[6] ?? H / 2); }

// ---------- faces ----------
// texQuad arguments that map an image upright onto a box face: 'x' (+x, left face), 'y' (+y, right face), 'top'
export function faceFrame(cam, face, x0, y0, z0, sx, sy, sz) {
  const x1 = x0 + sx, y1 = y0 + sy, z1 = z0 + sz, d = (a, b) => [b[0] - a[0], b[1] - a[1]];
  if (face === 'x') { const O = cam.p(x1, y0, z1); return [O, d(O, cam.p(x1, y1, z1)), d(O, cam.p(x1, y0, z0))]; }
  if (face === 'y') { const O = cam.p(x1, y1, z1); return [O, d(O, cam.p(x0, y1, z1)), d(O, cam.p(x1, y1, z0))]; }
  const O = cam.p(x0, y0, z1); return [O, d(O, cam.p(x0, y1, z1)), d(O, cam.p(x1, y0, z1))];
}

// ghost of a box: its visible edges as dashed ink lines (value that exists only on paper)
export function dashedBox(ctx, cam, x0, y0, z0, sx, sy, sz, o = {}) {
  const x1 = x0 + sx, y1 = y0 + sy, z1 = z0 + sz, P = (x, y, z) => cam.p(x, y, z);
  const a = o.a === undefined ? 1 : o.a;
  if (a <= 0.005) return;
  ctx.save();
  ctx.globalAlpha = a;
  if (o.fill) {
    ctx.fillStyle = o.fill; ctx.beginPath();
    for (const q of [P(x0, y0, z1), P(x0, y1, z1), P(x0, y1, z0), P(x1, y1, z0), P(x1, y0, z0), P(x1, y0, z1)]) ctx.lineTo(q[0], q[1]);
    ctx.closePath(); ctx.fill();
  }
  ctx.strokeStyle = o.color || '#2B2533'; ctx.lineWidth = o.lw || 2; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.setLineDash(o.dash || [7, 6]); ctx.lineDashOffset = o.offset || 0;
  const seg = (p, q) => { ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]); };
  ctx.beginPath();
  // top face rim
  seg(P(x0, y0, z1), P(x1, y0, z1)); seg(P(x1, y0, z1), P(x1, y1, z1)); seg(P(x1, y1, z1), P(x0, y1, z1)); seg(P(x0, y1, z1), P(x0, y0, z1));
  if (sz > 1e-6) {
    // three visible vertical edges and the two visible bottom edges
    seg(P(x1, y0, z0), P(x1, y0, z1)); seg(P(x1, y1, z0), P(x1, y1, z1)); seg(P(x0, y1, z0), P(x0, y1, z1));
    if (!o.noBottom) { seg(P(x1, y0, z0), P(x1, y1, z0)); seg(P(x1, y1, z0), P(x0, y1, z0)); }
  }
  ctx.stroke();
  ctx.restore();
}

// filled ellipse lying on a z plane (circle of radius r in the world)
export function discZ(ctx, cam, cx, cy, z, r, fill) {
  const [x, y] = cam.p(cx, cy, z);
  ctx.fillStyle = fill; ctx.beginPath(); ctx.ellipse(x, y, r * SQ15 * cam.k, r * Math.SQRT1_2 * cam.k, 0, 0, Math.PI * 2); ctx.fill();
}

// ---------- big key text (YouTube Sans Black: white, black stroke, slight shadow, one highlight colour) ----------
export const HL = '#FFD23F';
// parts: string or [[text, colour], ...]; p = pop progress 0..1
export function bigText(ctx, parts, x, y, o = {}) {
  const p = o.p === undefined ? 1 : o.p, a = o.a === undefined ? 1 : o.a;
  if (p <= 0 || a <= 0) return 0;
  if (typeof parts === 'string') parts = [[parts, '#FFFFFF']];
  const size = o.size || 96;
  ctx.save();
  ctx.font = `${size}px YTSans`; ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left'; ctx.letterSpacing = '0px';
  const ws = parts.map(([s]) => ctx.measureText(s).width), tw = ws.reduce((q, v) => q + v, 0);
  const s = 0.82 + 0.18 * backOut(p), al = clamp(p * 2.2) * a;
  const x0 = o.align === 'left' ? x : o.align === 'right' ? x - tw : x - tw / 2;
  ctx.translate(x, y - size * 0.35); ctx.scale(s, s); ctx.translate(-x, -(y - size * 0.35));
  ctx.globalAlpha = al;
  // soft drop shadow, then the black stroke, then the fill
  let cx = x0;
  ctx.lineJoin = 'round'; ctx.miterLimit = 2;
  ctx.fillStyle = 'rgba(20,14,26,0.35)';
  for (let i = 0; i < parts.length; i++) { ctx.fillText(parts[i][0], cx + size * 0.03, y + size * 0.06); cx += ws[i]; }
  cx = x0; ctx.strokeStyle = '#141018'; ctx.lineWidth = size * 0.16;
  for (let i = 0; i < parts.length; i++) { ctx.strokeText(parts[i][0], cx, y); cx += ws[i]; }
  cx = x0;
  for (let i = 0; i < parts.length; i++) { ctx.fillStyle = parts[i][1] || '#FFFFFF'; ctx.fillText(parts[i][0], cx, y); cx += ws[i]; }
  ctx.restore();
  return tw;
}
export function measureBig(ctx, s, size) { ctx.save(); ctx.font = `${size}px YTSans`; ctx.textAlign = 'left'; ctx.letterSpacing = '0px'; const w = ctx.measureText(s).width; ctx.restore(); return w; }

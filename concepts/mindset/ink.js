// Hand-drawn "tablet" ink engine for Canvas 2D.
// Everything is drawn from code: wobbly tapered brush strokes that "boil"
// (re-jitter) a few times per second, like frame-by-frame tablet animation.

function h1(i, s) { const x = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return x - Math.floor(x); }
function noise1(x, s) {
  const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
  return h1(i, s) * (1 - u) + h1(i + 1, s) * u;
}
const lerp = (a, b, t) => a + (b - a) * t;

// Resample a polyline every `step` px, returning [{x,y,s,nx,ny}] with normals.
function resample(pts, step = 4) {
  const out = [];
  let total = 0;
  const seg = [];
  for (let i = 1; i < pts.length; i++) {
    const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    seg.push(d); total += d;
  }
  if (total < 0.5) return [];
  const n = Math.max(2, Math.ceil(total / step));
  let si = 0, acc = 0;
  for (let k = 0; k <= n; k++) {
    const s = (k / n) * total;
    while (si < seg.length - 1 && acc + seg[si] < s) { acc += seg[si]; si++; }
    const t = seg[si] ? (s - acc) / seg[si] : 0;
    const a = pts[si], b = pts[si + 1];
    out.push({ x: lerp(a[0], b[0], t), y: lerp(a[1], b[1], t), s });
  }
  for (let k = 0; k < out.length; k++) {
    const p = out[Math.max(0, k - 1)], q = out[Math.min(out.length - 1, k + 1)];
    let dx = q.x - p.x, dy = q.y - p.y; const l = Math.hypot(dx, dy) || 1;
    out[k].nx = -dy / l; out[k].ny = dx / l;
  }
  out.total = total;
  return out;
}

// Smooth a few control points into a curve (Catmull-Rom).
function curve(ctrl, per = 10) {
  if (ctrl.length < 3) return ctrl;
  const out = [];
  for (let i = 0; i < ctrl.length - 1; i++) {
    const p0 = ctrl[Math.max(0, i - 1)], p1 = ctrl[i], p2 = ctrl[i + 1], p3 = ctrl[Math.min(ctrl.length - 1, i + 2)];
    for (let k = 0; k < per; k++) {
      const t = k / per, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(j => 0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)));
    }
  }
  out.push(ctrl[ctrl.length - 1]);
  return out;
}

// Tapered, wobbly brush stroke. opt: w, color, wob (px), seed, taper (px), alpha, pressure
function brush(ctx, pts, opt = {}) {
  const w = opt.w ?? 6, wob = opt.wob ?? 1.6, seed = (opt.seed ?? 1) + (opt.boil ?? 0) * 17.13;
  const r = resample(pts, opt.step ?? 3);
  if (!r.length) return;
  const L = r.total, tp = opt.taper ?? Math.min(40, L * 0.3);
  const left = [], right = [];
  for (const p of r) {
    const off = (noise1(p.s / 55, seed) - 0.5) * 2 * wob + (noise1(p.s / 13, seed + 3) - 0.5) * wob * 0.5;
    const end = Math.min(1, (p.s + 1) / tp, (L - p.s + 1) / tp);
    const taper = opt.noTaper ? 1 : Math.pow(Math.max(0.05, end), 0.55);
    const pr = (opt.pressure ?? 0.35);
    const ww = w * taper * (1 - pr / 2 + pr * noise1(p.s / 70, seed + 9)) / 2;
    const cx = p.x + p.nx * off, cy = p.y + p.ny * off;
    left.push([cx + p.nx * ww, cy + p.ny * ww]);
    right.push([cx - p.nx * ww, cy - p.ny * ww]);
  }
  ctx.save();
  ctx.globalAlpha = opt.alpha ?? 1;
  ctx.fillStyle = opt.color ?? '#111';
  ctx.beginPath();
  ctx.moveTo(left[0][0], left[0][1]);
  for (const q of left) ctx.lineTo(q[0], q[1]);
  for (let i = right.length - 1; i >= 0; i--) ctx.lineTo(right[i][0], right[i][1]);
  ctx.closePath(); ctx.fill();
  if (opt.roundCaps) {
    const a = r[0], b = r[r.length - 1];
    ctx.beginPath(); ctx.arc(a.x, a.y, w / 2, 0, 7); ctx.arc(b.x, b.y, w / 2, 0, 7); ctx.fill();
  }
  ctx.restore();
}

// Pencil: several faint thin passes with grain.
function pencil(ctx, pts, opt = {}) {
  const passes = opt.passes ?? 3;
  for (let k = 0; k < passes; k++) {
    brush(ctx, pts, { ...opt, w: (opt.w ?? 3) * (0.7 + 0.3 * k / passes), wob: (opt.wob ?? 1.5) * (1 + k * 0.4), alpha: (opt.alpha ?? 0.9) / passes * 1.6, seed: (opt.seed ?? 1) + k * 31, color: opt.grain || opt.color });
  }
}

// Hand-drawn circle outline (slight overshoot where the pen closes).
function circlePts(cx, cy, r, seed = 1, over = 0.35, squash = 1) {
  const a0 = h1(seed, 2) * 6.28, pts = [];
  const n = 64;
  for (let i = 0; i <= n; i++) {
    const a = a0 + (i / n) * (6.283 + over);
    const rr = r * (1 + (noise1(i / 9, seed) - 0.5) * 0.05) * (1 + i / n * 0.015);
    pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr * squash]);
  }
  return pts;
}

// Filled wobbly blob (circle-ish).
function blobFill(ctx, cx, cy, r, color, seed = 1, boil = 0, squash = 1) {
  ctx.save(); ctx.fillStyle = color; ctx.beginPath();
  const n = 72, s = seed + boil * 7.7;
  for (let i = 0; i <= n; i++) {
    const a = (i / n) * 6.283;
    const rr = r * (1 + (noise1(i / 8, s) - 0.5) * 0.045);
    const x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr * squash;
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  }
  ctx.fill(); ctx.restore();
}

// Fill an arbitrary polygon with a slight wobble.
function polyFill(ctx, pts, color, seed = 1, boil = 0, wob = 2) {
  const r = resample([...pts, pts[0]], 6);
  ctx.save(); ctx.fillStyle = color; ctx.beginPath();
  r.forEach((p, i) => {
    const o = (noise1(p.s / 40, seed + boil * 5.3) - 0.5) * 2 * wob;
    const x = p.x + p.nx * o, y = p.y + p.ny * o;
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  });
  ctx.fill(); ctx.restore();
}

// Paper grain texture canvas (generated once).
function grainCanvas(W, H, seed, dark) {
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d'); const id = g.createImageData(W, H); const d = id.data;
  let s = seed * 9301 + 49297;
  for (let i = 0; i < d.length; i += 4) {
    s = (s * 9301 + 49297) % 233280; const r = s / 233280;
    const v = dark ? 255 : 0;
    d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = r * (dark ? 14 : 22);
  }
  g.putImageData(id, 0, 0);
  // soft fibres
  g.globalAlpha = dark ? 0.03 : 0.05; g.strokeStyle = dark ? '#fff' : '#000';
  for (let i = 0; i < 900; i++) {
    const x = h1(i, seed) * W, y = h1(i, seed + 1) * H, a = h1(i, seed + 2) * 6.28, l = 6 + h1(i, seed + 3) * 22;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
  }
  return c;
}

function vignette(ctx, W, H, strength = 0.45, color = '0,0,0') {
  const g = ctx.createRadialGradient(W / 2, H * 0.45, Math.min(W, H) * 0.3, W / 2, H / 2, Math.max(W, H) * 0.75);
  g.addColorStop(0, `rgba(${color},0)`); g.addColorStop(1, `rgba(${color},${strength})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

// Text that boils slightly (hand-lettered feel).
function handText(ctx, str, x, y, opt = {}) {
  const boil = opt.boil ?? 0;
  ctx.save();
  ctx.font = opt.font; ctx.fillStyle = opt.color ?? '#111'; ctx.textAlign = opt.align ?? 'center'; ctx.textBaseline = 'alphabetic';
  if (opt.perChar) {
    // Draw each glyph with its own tiny jitter.
    const total = ctx.measureText(str).width;
    let cx = opt.align === 'left' ? x : x - total / 2;
    ctx.textAlign = 'left';
    for (let i = 0; i < str.length; i++) {
      const ch = str[i], cw = ctx.measureText(ch).width;
      const jx = (h1(i, boil + 3) - 0.5) * 2.2, jy = (h1(i, boil + 7) - 0.5) * 2.6, rot = (h1(i, boil + 11) - 0.5) * 0.04;
      ctx.save(); ctx.translate(cx + jx, y + jy); ctx.rotate(rot); ctx.fillText(ch, 0, 0); ctx.restore();
      cx += cw;
    }
  } else {
    ctx.translate(x + (h1(1, boil) - 0.5) * 2, y + (h1(2, boil) - 0.5) * 2);
    ctx.rotate((h1(3, boil) - 0.5) * 0.01);
    ctx.fillText(str, 0, 0);
  }
  ctx.restore();
}

// ---------- tiny figure rig ----------
// Angles: 0 = pointing straight down, positive = rotated toward facing direction.
function limb(origin, a1, l1, a2, l2, dir) {
  const k = [origin[0] + Math.sin(a1) * l1 * dir, origin[1] + Math.cos(a1) * l1];
  const e = [k[0] + Math.sin(a2) * l2 * dir, k[1] + Math.cos(a2) * l2];
  return [origin, k, e];
}
// Two-bone IK: returns [a, mid, b]
function ik(a, b, l1, l2, bendSign) {
  let dx = b[0] - a[0], dy = b[1] - a[1]; let d = Math.hypot(dx, dy);
  d = Math.min(d, l1 + l2 - 0.01);
  const ang = Math.atan2(dy, dx);
  const c = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d);
  const t = ang + bendSign * Math.acos(Math.max(-1, Math.min(1, c)));
  const m = [a[0] + Math.cos(t) * l1, a[1] + Math.sin(t) * l1];
  return [a, m, [a[0] + Math.cos(ang) * d, a[1] + Math.sin(ang) * d]];
}

window.Ink = { h1, noise1, lerp, resample, curve, brush, pencil, circlePts, blobFill, polyFill, grainCanvas, vignette, handText, limb, ik };

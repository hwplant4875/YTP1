// Protocol 404, EP03 "If Your Reflection Ever Tells You To RUN". Canvas renderer: window.draw(t).
// Black background, flat white pictograms, red only for what is wrong. Needs window.TL (timeline.json).
(() => {
const W = 1920, H = 1080;
const NAME = 'PROTOCOL';   // the channel's name, as it appears on screen ("NAME 404")
const C = { bg: '#000', fig: '#f2f2f2', sec: '#bdbdbd', mid: '#7c7c7c', dim: '#3c3c3c', dark: '#1a1a1a', red: '#ff2b2b', txt: '#f4f4f4' };
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = x => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const backOut = x => { x = clamp(x); const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
const D2R = Math.PI / 180;

// ---------- primitives ----------
const glow = (c = 'rgba(255,255,255,0.35)', b = 22) => { ctx.shadowColor = c; ctx.shadowBlur = b; };
const redGlow = (b = 22) => glow('rgba(255,43,43,0.85)', b);
const noGlow = () => { ctx.shadowBlur = 0; ctx.shadowColor = 'transparent'; };
const rr = (x, y, w, h, r, f) => { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fillStyle = f; ctx.fill(); };
const rrS = (x, y, w, h, r, s, lw) => { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.strokeStyle = s; ctx.lineWidth = lw; ctx.stroke(); };
const circ = (x, y, r, f) => { ctx.beginPath(); ctx.arc(x, y, Math.max(0, r), 0, Math.PI * 2); ctx.fillStyle = f; ctx.fill(); };
const circS = (x, y, r, s, lw) => { ctx.beginPath(); ctx.arc(x, y, Math.max(0, r), 0, Math.PI * 2); ctx.strokeStyle = s; ctx.lineWidth = lw; ctx.stroke(); };
const ell = (x, y, rx, ry, rot, f) => { ctx.beginPath(); ctx.ellipse(x, y, Math.max(0, rx), Math.max(0, ry), rot, 0, Math.PI * 2); ctx.fillStyle = f; ctx.fill(); };
const ln = (x1, y1, x2, y2, w, s, cap = 'round') => { ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.lineWidth = w; ctx.strokeStyle = s; ctx.lineCap = cap; ctx.stroke(); };
const poly = (pts, w, s) => { ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (const p of pts.slice(1)) ctx.lineTo(p[0], p[1]); ctx.lineWidth = w; ctx.strokeStyle = s; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke(); };
const pth = (d, f) => { ctx.fillStyle = f; ctx.fill(new Path2D(d)); };
const pthS = (d, s, w) => { ctx.strokeStyle = s; ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke(new Path2D(d)); };
const text = (s, x, y, font, f, align = 'center', base = 'alphabetic') => { ctx.font = font; ctx.fillStyle = f; ctx.textAlign = align; ctx.textBaseline = base; ctx.fillText(s, x, y); };
const spaced = (s, x, y, font, f, sp, align = 'center') => { ctx.font = font; ctx.letterSpacing = sp + 'px'; text(s, x, y, font, f, align); ctx.letterSpacing = '0px'; };
// draw a line progressively (p 0..1)
const lnP = (x1, y1, x2, y2, w, s, p) => { if (p > 0) ln(x1, y1, lerp(x1, x2, clamp(p)), lerp(y1, y2, clamp(p)), w, s); };
// pop-in: scale around (x,y) with overshoot, fade in
function pop(t, t0, x, y, fn, d = 0.38) {
  const k = (t - t0) / d; if (k <= 0) return;
  ctx.save(); ctx.globalAlpha *= clamp(k * 2.5); const s = lerp(0.55, 1, backOut(k));
  ctx.translate(x, y); ctx.scale(s, s); ctx.translate(-x, -y); fn(); ctx.restore();
}
function fadeIn(t, t0, fn, d = 0.3) { const k = clamp((t - t0) / d); if (k <= 0) return; ctx.save(); ctx.globalAlpha *= k; fn(); ctx.restore(); }
function slideIn(t, t0, dx, dy, fn, d = 0.45) { const k = (t - t0) / d; if (k <= 0) return; const e = easeOut(k);
  ctx.save(); ctx.globalAlpha *= clamp(k * 2); ctx.translate(dx * (1 - e), dy * (1 - e)); fn(); ctx.restore(); }
// slow camera push for a shot
function cam(t, t0, d, z0, z1, cx = W / 2, cy = H / 2, fn) {
  const z = lerp(z0, z1, ease((t - t0) / d));
  ctx.save(); ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy); fn(); ctx.restore();
}
function shake(amp, t) { ctx.translate(Math.sin(t * 91) * amp, Math.cos(t * 77) * amp); }

// ---------- timeline helpers ----------
const norm = w => w.toLowerCase().replace(/[^a-z0-9']/g, '');
function wt(seg, word, nth = 1) {
  let n = 0; for (const w of seg.words) if (norm(w.w) === word && ++n === nth) return w.s;
  return seg.end;
}
const prog = (t, t0, d = 0.3) => clamp((t - t0) / d);
const evs = type => window.TL.events.filter(e => e.type === type);
// knock times inside a knock3 event (the triple knock file has hits at 0, 0.56, 1.12 s)
const knockTimes = () => evs('knock3').flatMap(e => [e.t, e.t + 0.56, e.t + 1.12]);
function knockPulse(t) { let p = 0; for (const k of knockTimes()) { const d = t - k; if (d >= 0 && d < 0.4) p = Math.max(p, 1 - d / 0.4); } return p; }
function lastKnock(t) { let l = -9; for (const k of knockTimes()) if (k <= t) l = k; return l; }
function ripple(x, y, t0, t, col = C.red, r0 = 20, r1 = 170, lw = 6) {
  const dt = t - t0; if (dt < 0 || dt > 1.2) return;
  for (let i = 0; i < 3; i++) {
    const k = dt * 1.1 - i * 0.18; if (k <= 0 || k > 1) continue;
    ctx.save(); ctx.globalAlpha *= 1 - k; circS(x, y, r0 + easeOut(k) * (r1 - r0), col, lw); ctx.restore();
  }
}
function knockLines(x, y, a, col = C.red, dir = 1, s = 1) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; if (col === C.red) redGlow(16);
  ln(x, y - 36 * s, x - 36 * dir * s, y - 58 * s, 9 * s, col); ln(x - 4 * dir * s, y, x - 46 * dir * s, y, 9 * s, col); ln(x, y + 36 * s, x - 36 * dir * s, y + 58 * s, 9 * s, col);
  noGlow(); ctx.restore();
}
function redX(cx, cy, r, p, lw = 0.24) {
  if (p <= 0) return;
  redGlow(18); const a = clamp(p * 2), b = clamp(p * 2 - 1);
  lnP(cx - r, cy - r, cx + r, cy + r, r * lw, C.red, a);
  lnP(cx + r, cy - r, cx - r, cy + r, r * lw, C.red, b); noGlow();
}
function check(cx, cy, r, p, col = C.fig) {
  if (p <= 0) return;
  const a = clamp(p * 2), b = clamp(p * 2 - 1);
  lnP(cx - r, cy, cx - r * 0.3, cy + r * 0.7, r * 0.26, col, a);
  if (b > 0) lnP(cx - r * 0.3, cy + r * 0.7, cx + r, cy - r * 0.8, r * 0.26, col, b);
}


// Instruction 404, EP01 "If Your Cat Ever Knocks On Your Bedroom Door". Canvas renderer: window.draw(t).
// Needs window.TL (timeline.json) before the first draw.
(() => {
const W = 1920, H = 1080;
const C = { bg: '#0c2e14', fig: '#d8ffdc', sec: '#8fd99a', bedG: '#a9e6b2', leg: '#6fb27a', wall: '#164a22', floor: '#1d5a2a',
  panel: '#17401f', red: '#ff2a2a', txt: '#eaffea', dim: '#5d9b68' };
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = x => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const lerp = (a, b, k) => a + (b - a) * k;

// ---------- primitives ----------
const glow = (c = 'rgba(216,255,220,0.55)', b = 26) => { ctx.shadowColor = c; ctx.shadowBlur = b; };
const noGlow = () => { ctx.shadowBlur = 0; ctx.shadowColor = 'transparent'; };
const rr = (x, y, w, h, r, f) => { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fillStyle = f; ctx.fill(); };
const rrS = (x, y, w, h, r, s, lw) => { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.strokeStyle = s; ctx.lineWidth = lw; ctx.stroke(); };
const circ = (x, y, r, f) => { ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = f; ctx.fill(); };
const ell = (x, y, rx, ry, rot, f) => { ctx.beginPath(); ctx.ellipse(x, y, rx, ry, rot, 0, Math.PI * 2); ctx.fillStyle = f; ctx.fill(); };
const ln = (x1, y1, x2, y2, w, s) => { ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.lineWidth = w; ctx.strokeStyle = s; ctx.lineCap = 'round'; ctx.stroke(); };
const pth = (d, f) => { ctx.fillStyle = f; ctx.fill(new Path2D(d)); };
const pthS = (d, s, w) => { ctx.strokeStyle = s; ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke(new Path2D(d)); };
const text = (s, x, y, font, f, align = 'center', base = 'alphabetic') => { ctx.font = font; ctx.fillStyle = f; ctx.textAlign = align; ctx.textBaseline = base; ctx.fillText(s, x, y); };

// ---------- props (thumbnail coordinates, 1280x720 space, floor y=690) ----------
function bed(mode = 'woke') {
  glow();
  rr(70, 420, 36, 270, 14, C.fig); rr(70, 566, 480, 58, 16, C.bedG);
  rr(96, 620, 24, 66, 6, C.leg); rr(510, 620, 24, 66, 6, C.leg); ell(150, 556, 50, 15, 0, C.bedG);
  if (mode === 'woke') {
    circ(204, 456, 40, C.fig);
    pth('M150,568 C150,522 176,498 214,498 C262,498 300,506 340,510 C420,516 480,528 552,548 L552,590 L150,590 Z', C.fig);
    noGlow(); circ(230, 450, 9, '#000');
  } else {
    circ(168, 522, 40, C.fig);
    pth('M186,560 C196,522 268,504 340,510 C420,516 480,528 552,548 L552,590 L186,590 Z', C.fig);
    noGlow(); pthS('M178,516 q9,8 18,0', '#000', 5);
  }
  noGlow();
}
function doorEdge() {
  rr(690, 186, 48, 504, 0, C.wall);
  glow(); rr(696, 232, 36, 452, 4, C.fig);
  rr(676, 452, 22, 16, 6, C.fig); circ(676, 460, 11, C.fig); rr(730, 452, 22, 16, 6, C.fig); circ(752, 460, 11, C.fig); noGlow();
}
// standing cat; k = 0 paw on the door, 1 = pulled back for the next knock; alpha for reveal
function standCat(k = 0, eyeA = 1) {
  glow();
  pthS('M948,560 C1012,556 1030,488 1004,436', C.sec, 18);
  ln(928, 556, 946, 676, 24, C.sec); ell(958, 682, 26, 9, 0, C.sec);
  ln(896, 420, 884, 520, 22, C.sec);
  ctx.save(); ctx.translate(904, 470); ctx.rotate(-6 * Math.PI / 180); ell(0, 0, 54, 112, 0, C.fig); ctx.restore();
  ln(900, 556, 892, 676, 26, C.fig); ell(878, 682, 28, 10, 0, C.fig);
  pth('M854,300 L860,236 L896,290 Z', C.fig); pth('M890,292 L928,246 L930,310 Z', C.fig);
  circ(884, 334, 50, C.fig); ell(846, 348, 14, 12, 0, C.fig);
  const px = lerp(762, 800, k), py = lerp(326, 306, k);
  ln(872, 404, px, py, 26, C.fig); circ(px, py, 17, C.fig);
  noGlow();
  pth('M832,342 l8,0 l-4,6 z', '#000');
  ctx.globalAlpha *= eyeA; glow('rgba(255,42,42,0.9)', 22); ell(860, 322, 10, 9, 0, C.red); noGlow(); ctx.globalAlpha /= eyeA || 1;
  rr(858, 314, 4, 16, 2, '#000');
}
function knockLines(x, y, a, col = C.red, flip = 1) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; glow(col === C.red ? 'rgba(255,42,42,0.9)' : 'rgba(216,255,220,0.7)', 18);
  const s = flip;
  ln(x, y - 34, x - 34 * s, y - 54, 9, col); ln(x - 4 * s, y, x - 44 * s, y, 9, col); ln(x, y + 34, x - 34 * s, y + 54, 9, col);
  noGlow(); ctx.restore();
}
// normal small cat sitting, side view facing right, feet at (0,0)
function sitCat(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  glow();
  pthS('M-40,-8 C-80,-4 -92,-40 -70,-62', C.sec, 9);
  ell(0, -40, 46, 38, 0, C.fig);
  const hx = o.push ? 52 : 40, hy = o.push ? -78 : -86;
  circ(hx, hy, 28, C.fig);
  pth(`M${hx - 22},${hy - 12} L${hx - 18},${hy - 46} L${hx - 2},${hy - 22} Z`, C.fig);
  pth(`M${hx + 2},${hy - 24} L${hx + 20},${hy - 46} L${hx + 24},${hy - 10} Z`, C.fig);
  if (o.paw) ln(30, -30, 66, -64 - 10 * Math.sin(o.paw * 20), 12, C.fig); else ln(28, -6, 40, 0, 12, C.fig);
  noGlow();
  circ(hx + 12, hy - 4, 4.5, '#000');
  ctx.restore();
}
// front view door; light: hallway light under the door (0..1); feet: shadow feet count
function doorFront(x, y, w, h, o = {}) {
  rrS(x - 18, y - 18, w + 36, h + 18, 2, C.dim, 8);
  rr(x, y, w, h, 4, C.panel);
  rrS(x + w * 0.12, y + h * 0.06, w * 0.76, h * 0.38, 6, C.sec, 5);
  rrS(x + w * 0.12, y + h * 0.52, w * 0.76, h * 0.4, 6, C.sec, 5);
  glow(); circ(x + w * 0.1, y + h * 0.52, w * 0.035, C.fig); noGlow();
  if (o.light) { ctx.save(); ctx.globalAlpha *= o.light; glow('rgba(234,255,234,0.9)', 30); rr(x, y + h - 2, w, 10, 0, '#f4fff4'); noGlow(); ctx.restore();
    for (let i = 0; i < (o.feet || 0); i++) rr(x + w * (0.34 + i * 0.2), y + h - 2, w * 0.1, 10, 0, '#000'); }
  ln(0, y + h + 8, W, y + h + 8, 4, C.floor);
}
function redX(cx, cy, r, p) {
  if (p <= 0) return;
  glow('rgba(255,42,42,0.9)', 24);
  const a = clamp(p * 2), b = clamp(p * 2 - 1);
  ln(cx - r, cy - r, lerp(cx - r, cx + r, a), lerp(cy - r, cy + r, a), r * 0.28, C.red);
  if (b > 0) ln(cx + r, cy - r, lerp(cx + r, cx - r, b), lerp(cy - r, cy + r, b), r * 0.28, C.red);
  noGlow();
}
function check(cx, cy, r, p) {
  if (p <= 0) return;
  glow(); const a = clamp(p * 2), b = clamp(p * 2 - 1);
  ln(cx - r, cy, lerp(cx - r, cx - r * 0.3, a), lerp(cy, cy + r * 0.7, a), r * 0.26, C.fig);
  if (b > 0) ln(cx - r * 0.3, cy + r * 0.7, lerp(cx - r * 0.3, cx + r, b), lerp(cy + r * 0.7, cy - r * 0.8, b), r * 0.26, C.fig);
  noGlow();
}
function ripple(x, y, t0, t, col = C.red) {
  const dt = t - t0; if (dt < 0 || dt > 1.2) return;
  for (let i = 0; i < 3; i++) {
    const k = dt * 1.1 - i * 0.18; if (k <= 0 || k > 1) continue;
    ctx.beginPath(); ctx.arc(x, y, 20 + k * 150, 0, Math.PI * 2);
    ctx.strokeStyle = col; ctx.globalAlpha = 1 - k; ctx.lineWidth = 6; ctx.stroke(); ctx.globalAlpha = 1;
  }
}

// ---------- timeline helpers ----------
const norm = w => w.toLowerCase().replace(/[^a-z0-9']/g, '');
function wt(seg, word, nth = 1) {
  let n = 0; for (const w of seg.words) if (norm(w.w) === word && ++n === nth) return w.s;
  return seg.end;
}
const prog = (t, t0, d = 0.3) => clamp((t - t0) / d);
const knocks = () => window.TL.events.filter(e => e.type === 'knock');
// pulse 1 at each knock, fading
function knockPulse(t) { let p = 0; for (const e of knocks()) { const d = t - e.t; if (d >= 0 && d < 0.45) p = Math.max(p, 1 - d / 0.45); } return p; }

const RULE = { s05: 1, s06: 1, s07: 1, s08: 1, s09: 1, s10: 2, s11: 2, s12: 2, s13: 2, s14: 2, s15: 3, s16: 3, s17: 3, s18: 3, s19: 3,
  s20: 4, s21: 4, s22: 4, s23: 4, s24: 4, s25: 5, s26: 5, s27: 5, s28: 5, s29: 5, s30: 6, s31: 6, s32: 6, s33: 6, s34: 6, s35: 6, s36: 6, s37: 7, s38: 7 };

// ---------- scenes (t = absolute seconds, seg = segment) ----------
function thumbSpace(fn, zoom = 1, cx = 640, cy = 440) {
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(1.5 * zoom, 1.5 * zoom); ctx.translate(-cx, -cy); fn(); ctx.restore();
}
function floorLine() { ln(0, 690, 1280, 690, 4, C.floor); }

const S = {};
S.s01 = (t, seg) => {
  const z = 1 + 0.05 * clamp((t - seg.start) / 6);
  thumbSpace(() => { floorLine(); bed('woke'); doorEdge(); const k = 0.5 + 0.5 * Math.sin(t * 2.2); standCat(k * 0.25, 0.75 + 0.25 * Math.sin(t * 3)); }, z, 640, 450);
};
S.s02 = (t, seg) => {
  const k0 = knocks()[0];
  if (k0 && t > k0.t - 0.35) { // the knocks: close-up of the door from the bed
    doorFront(760, 140, 400, 760, { light: 0.25 });
    const p = knockPulse(t);
    ctx.save(); ctx.translate(960, 560); ctx.scale(1 + 0.012 * p, 1 + 0.012 * p); ctx.translate(-960, -560); ctx.restore();
    for (const e of knocks().slice(0, 3)) { ripple(960, 560, e.t, t); }
    knockLines(700, 560, p, C.red, 1); knockLines(1220, 560, p, C.red, -1);
    const n = knocks().slice(0, 3).filter(e => t >= e.t).length;
    if (n) text('KNOCK'.padEnd(5) + ' ×' + n, 960, 1040 - 10, '900 50px M', C.red);
    return;
  }
  const items = [['up', 560, iconGetUp], ['light', 960, iconBulb], ['name', 1360, iconTalk]];
  items.forEach(([w, x, ic], i) => {
    const a = prog(t, seg.start + i * 0.12, 0.25);
    ctx.globalAlpha = a; rrS(x - 150, 330, 300, 300, 28, C.dim, 6); ic(x, 480); ctx.globalAlpha = 1;
    redX(x, 480, 105, prog(t, wt(seg, w) - 0.05, 0.3));
  });
};
function iconGetUp(x, y) {
  glow(); rr(x - 100, y + 30, 200, 26, 10, C.bedG); rr(x - 100, y - 30, 16, 86, 6, C.fig);
  circ(x - 40, y - 30, 26, C.fig); rr(x - 64, y - 4, 70, 40, 16, C.fig);
  ln(x + 50, y + 10, x + 50, y - 80, 12, C.fig); pth(`M${x + 26},${y - 66} L${x + 50},${y - 100} L${x + 74},${y - 66} Z`, C.fig); noGlow();
}
function iconBulb(x, y) {
  glow(); ctx.beginPath(); ctx.arc(x, y - 30, 62, Math.PI * 0.8, Math.PI * 2.2); ctx.lineTo(x + 26, y + 46); ctx.lineTo(x - 26, y + 46); ctx.closePath();
  ctx.fillStyle = C.fig; ctx.fill(); rr(x - 26, y + 52, 52, 14, 4, C.sec); rr(x - 22, y + 70, 44, 12, 4, C.sec); noGlow();
}
function iconTalk(x, y) {
  glow(); rr(x - 100, y - 80, 200, 130, 30, C.fig); pth(`M${x - 50},${y + 44} L${x - 74},${y + 92} L${x - 6},${y + 44} Z`, C.fig); noGlow();
  text('?', x, y - 15, '900 96px M', C.bg, 'center', 'middle');
}
S.s03 = (t, seg) => {
  const a = prog(t, seg.start, 0.2);
  ctx.globalAlpha = a; glow('rgba(216,255,220,0.6)', 40);
  text('3:12', 920, 560, '900 300px M', C.fig); text('AM', 1270, 560, '900 90px M', C.sec, 'left'); noGlow(); ctx.globalAlpha = 1;
  const tk = wt(seg, 'knock'), ta = wt(seg, 'always');
  for (let i = 0; i < 3; i++) {
    const p = prog(t, tk + 0.25 + i * 0.28, 0.2); if (p <= 0) continue;
    const red = t >= ta; ctx.globalAlpha = p;
    const x = 760 + i * 200, y = 760;
    glow(red ? 'rgba(255,42,42,0.9)' : 'rgba(216,255,220,0.6)', 24); circ(x, y, 40, red ? C.red : C.fig); noGlow();
    text(String(i + 1), x, y + 2, '900 44px M', C.bg, 'center', 'middle'); ctx.globalAlpha = 1;
  }
};
S.s04 = (t, seg) => {
  const tt = wt(seg, 'two'), tw = wt(seg, 'why');
  for (let i = 0; i < 7; i++) {
    const x = 960 + (i - 3) * 210, y = 470, a = prog(t, seg.start + i * 0.08, 0.2);
    ctx.globalAlpha = a; rrS(x - 75, y - 75, 150, 150, 18, i < 2 && t > tt ? C.fig : C.dim, 6);
    text('RULE ' + (i + 1), x, y + 130, '30px Plex', C.sec); ctx.globalAlpha = 1;
    if (i < 2) check(x, y, 48, prog(t, tt + 0.15 + i * 0.25, 0.3));
    else if (t > tw) { ctx.globalAlpha = prog(t, tw + (i - 2) * 0.07, 0.2); text('?', x, y + 4, '900 96px M', C.red, 'center', 'middle'); ctx.globalAlpha = 1; }
  }
};
function ruleCard(t, seg, n, line) {
  const p = prog(t, seg.start, 0.25);
  ctx.globalAlpha = p; glow('rgba(216,255,220,0.6)', 40); text('RULE ' + n, 960, 520, '900 210px M', C.fig); noGlow(); ctx.globalAlpha = 1;
  const words = line.split(' '); let shown = 0;
  const tws = seg.words.slice(2); // words after "Rule one."
  for (let i = 0; i < words.length; i++) if (t >= (tws[i] ? tws[i].s : seg.end)) shown = i + 1;
  glow('rgba(255,42,42,0.8)', 18); text(words.slice(0, shown).join(' '), 960, 660, '600 64px Plex', C.red); noGlow();
}
S.s05 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT OPEN THE DOOR');
S.s06 = (t, seg) => {
  doorFront(760, 140, 400, 760, {});
  const tb = wt(seg, 'bottom'), tm = wt(seg, 'middle');
  if (t < tb) ripple(960, 560, seg.start + 0.3, t, C.sec);
  if (t >= tb) { ripple(960, 850, tb + Math.floor((t - tb) / 1.3) * 1.3, t, C.sec); glow(); text('NOT HERE', 1260, 865, '600 44px Plex', C.sec, 'left'); noGlow();
    redX(1215, 850, 22, prog(t, tb + 0.1, 0.3)); }
  if (t >= tm) { for (let k = 0; k < 4; k++) ripple(960, 540, tm + k * 0.6, t); glow('rgba(255,42,42,0.9)', 22); text('HERE', 1260, 555, '900 64px M', C.red, 'left'); noGlow();
    ln(1250, 540, 1200, 540, 8, C.red); }
};
function catAtDoor(t, seg, o = {}) {
  doorFront(920, 140, 400, 760, { light: 0 });
  sitCat(780, 906, 1.5, o);
}
S.s07 = (t, seg) => {
  const ts = wt(seg, 'scratch'), tp = wt(seg, 'push'), tc = wt(seg, 'cry');
  const o = {};
  if (t >= ts && t < tp) o.paw = t;
  if (t >= tp && t < tc) o.push = true;
  catAtDoor(t, seg, o);
  if (t >= ts) { const a = t < tp ? 1 : 0.5; ctx.globalAlpha = a; for (let i = 0; i < 3; i++) ln(935 + i * 22, 860 - i * 6, 965 + i * 22, 800 - i * 6, 6, C.fig); ctx.globalAlpha = 1; }
  if (t >= tc) { const p = prog(t, tc, 0.2); ctx.globalAlpha = p; glow(); rr(740, 620, 230, 100, 30, C.fig); pth('M790,716 L780,760 L830,716 Z', C.fig); noGlow();
    text('MEOW', 855, 690, '900 54px M', C.bg); ctx.globalAlpha = 1; }
};
S.s08 = (t, seg) => {
  catAtDoor(t, seg);
  const tn = wt(seg, 'not'), tk = wt(seg, 'knock', 2);
  if (t >= tn) { const p = prog(t, tn, 0.2); ctx.globalAlpha = p; rrS(1390, 380, 340, 280, 28, C.dim, 6);
    glow(); text('KNOCK', 1560, 545, '900 70px M', C.fig); noGlow(); ctx.globalAlpha = 1; redX(1560, 520, 110, prog(t, tk, 0.3)); }
};
S.s09 = (t, seg) => {
  const th = wt(seg, 'height'), tH = wt(seg, 'hand');
  const reveal = prog(t, tH - 0.1, 0.6);
  thumbSpace(() => {
    floorLine(); bed('woke'); doorEdge();
    // height ruler on the bedroom side of the door
    const cm = v => 690 - v * 2.26;
    ln(590, cm(0), 590, cm(180), 3, C.dim);
    for (let v = 0; v <= 180; v += 20) { ln(582, cm(v), 598, cm(v), 3, C.dim); if (v % 40 === 0) text(v + '', 574, cm(v) + 6, '16px Plex', C.dim, 'right'); }
    if (t >= th) { const p = prog(t, th, 0.3); ctx.globalAlpha = p; ln(590, cm(160), 690, cm(160), 5, C.red); glow('rgba(255,42,42,0.9)', 14);
      text('160 CM', 600, cm(160) - 12, '700 20px Plex', C.red, 'left'); noGlow(); ctx.globalAlpha = 1;
      knockLines(670, 326 + 40, 0.6 + 0.4 * Math.sin(t * 8), C.red, 1); }
    ctx.save(); ctx.globalAlpha = reveal; standCat(0.15 + 0.15 * Math.sin(t * 6), 1); ctx.restore();
  }, 1.0 + 0.04 * clamp((t - seg.start) / 4), 640, 450);
};

// ---------- HUD, captions, texture ----------
let grainC = null, scanP = null, vig = null;
function initTex() {
  grainC = [0, 1, 2, 3].map(() => { const g = document.createElement('canvas'); g.width = 480; g.height = 270; const gx = g.getContext('2d');
    const im = gx.createImageData(480, 270); for (let i = 0; i < im.data.length; i += 4) { const v = Math.random() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    gx.putImageData(im, 0, 0); return g; });
  const sc = document.createElement('canvas'); sc.width = 4; sc.height = 4; const sx = sc.getContext('2d'); sx.fillStyle = 'rgba(0,0,0,0.18)'; sx.fillRect(0, 0, 4, 2);
  scanP = ctx.createPattern(sc, 'repeat');
}
function hud(t, seg) {
  const on = (t % 1.2) < 0.8;
  if (on) { glow('rgba(255,42,42,0.9)', 14); circ(78, 64, 12, C.red); noGlow(); }
  text('REC', 100, 75, '30px Plex', C.txt, 'left');
  const sec = Math.floor(12 * 60 + 4 + t), mm = Math.floor(sec / 60) % 60, ss = sec % 60;
  text(`03:${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')} AM`, 1842, 75, '30px Plex', C.txt, 'right');
  text('INSTRUCTION 001 // DO NOT OPEN', 960, 62, '24px Plex', C.sec);
  const r = RULE[seg.id] || (seg.id > 's38' ? 8 : 0);
  for (let i = 0; i < 7; i++) {
    const x = 960 + (i - 3) * 34 - 11, y = 80;
    if (i + 1 < r) rr(x, y, 22, 22, 3, C.sec);
    else if (i + 1 === r) { glow('rgba(255,42,42,0.9)', 12); rr(x, y, 22, 22, 3, C.red); noGlow(); }
    else rrS(x, y, 22, 22, 3, C.dim, 2.5);
  }
  // viewfinder corners
  ctx.globalAlpha = 0.7; pthS('M40,130 v-40 h40 M1880,130 v-40 h-40 M40,950 v40 h40 M1880,950 v40 h-40', C.txt, 5); ctx.globalAlpha = 1;
}
function chunks(seg) {
  if (seg._ch) return seg._ch;
  const out = []; let cur = [];
  seg.words.forEach((w, i) => { cur.push(w); const end = /[.,?!…]$/.test(w.w) || w.w.endsWith('...'); if (end || cur.length >= 5) { out.push(cur); cur = []; } });
  if (cur.length) out.push(cur);
  return (seg._ch = out);
}
function caption(t, seg) {
  if (t > seg.end + 0.35) return;
  const ch = chunks(seg); let c = null;
  for (const k of ch) if (t >= k[0].s - 0.05) c = k;
  if (!c && seg === window.TL.segments[0]) c = ch[0];
  if (!c) return;
  const s = c.map(w => w.w).join(' ').toUpperCase();
  ctx.font = '900 54px M'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  ctx.lineJoin = 'round'; ctx.lineWidth = 12; ctx.strokeStyle = 'rgba(0,0,0,0.85)'; ctx.strokeText(s, 960, 1010);
  ctx.fillStyle = '#ffffff'; ctx.fillText(s, 960, 1010);
}
function glitch(t, f) {
  // brief tape glitch at every scene cut
  const segs = window.TL.segments; let cut = -9;
  for (const s of segs) if (s.start <= t) cut = s.start;
  const dt = t - cut; if (dt < 0 || dt > 0.2) return;
  const tmp = glitch.c || (glitch.c = document.createElement('canvas')); tmp.width = W; tmp.height = H; tmp.getContext('2d').drawImage(cv, 0, 0);
  let seed = f * 9301 + 49297; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  for (let i = 0; i < 9; i++) { const y = rnd() * H, h = 10 + rnd() * 60, dx = (rnd() - 0.5) * 120; ctx.drawImage(tmp, 0, y, W, h, dx, y, W, h); }
  ctx.globalAlpha = 0.35 * (1 - dt / 0.2); ctx.fillStyle = '#eaffea'; for (let i = 0; i < 6; i++) ctx.fillRect(0, rnd() * H, W, 2 + rnd() * 3); ctx.globalAlpha = 1;
}

window.draw = (t) => {
  if (!grainC) initTex();
  const f = Math.round(t * 30);
  const segs = window.TL.segments; let seg = segs[0];
  for (const s of segs) if (s.start <= t + 1e-6) seg = s;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; noGlow();
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  (S[seg.id] || S.s01)(t, seg);
  glitch(t, f);
  hud(t, seg);
  caption(t, seg);
  ctx.fillStyle = scanP; ctx.fillRect(0, 0, W, H);
  ctx.globalAlpha = 0.07; ctx.drawImage(grainC[f % 4], 0, 0, W, H); ctx.globalAlpha = 1;
  if (!vig) { vig = ctx.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.05); vig.addColorStop(0, 'rgba(0,0,0,0)'); vig.addColorStop(1, 'rgba(0,0,0,0.6)'); }
  ctx.fillStyle = vig; ctx.fillRect(0, 0, W, H);
};
})();

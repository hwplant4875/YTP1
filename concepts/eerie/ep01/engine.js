// Instruction 404, EP01 "If Your Cat Ever Knocks On Your Bedroom Door". Canvas renderer: window.draw(t).
// Black background, flat white pictograms, red only for what is wrong. Needs window.TL (timeline.json).
(() => {
const W = 1920, H = 1080;
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

// ---------- props ----------
// side-view bed; person: 'woke' (propped up, eye toward the door), 'sleep', 'none'. Origin = bed's left foot on the floor.
function bed(x, y, s = 1, mode = 'woke', o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  glow('rgba(255,255,255,0.25)', 18);
  rr(0, -330, 30, 330, 10, C.fig);                 // headboard
  rr(560, -170, 22, 170, 8, C.fig);                // footboard
  rr(0, -150, 582, 46, 12, C.fig);                 // frame
  rr(26, -104, 16, 104, 4, C.sec); rr(540, -104, 16, 104, 4, C.sec);
  rr(30, -196, 530, 48, 18, C.sec);                // mattress
  ell(98, -204, 56, 16, 0, C.fig);                 // pillow
  if (mode === 'woke') {
    circ(150, -298, 46, C.fig);
    pth('M88,-196 C90,-250 120,-268 160,-268 C220,-268 260,-250 300,-246 C390,-240 470,-232 560,-220 L560,-180 L88,-180 Z', C.fig);
    noGlow(); circ(178 + (o.look || 0) * 6, -304, 9, '#000');
  } else if (mode === 'sleep') {
    circ(112, -238, 44, C.fig);
    pth('M140,-200 C160,-240 240,-252 320,-248 C400,-244 480,-236 560,-222 L560,-180 L140,-180 Z', C.fig);
    noGlow(); pthS('M116,-240 q11,9 22,0', '#000', 5);
  }
  noGlow(); ctx.restore();
}
// wall with the door seen edge-on; x = wall centre, y = floor
function doorEdge(x, y, h = 470, open = 0) {
  rr(x - 30, y - h - 140, 60, h + 140, 0, C.dark);
  glow('rgba(255,255,255,0.25)', 16);
  ctx.save(); ctx.translate(x - 18, y - 6); ctx.rotate(-open * 70 * D2R);
  rr(0, -h, 36, h, 3, C.fig); circ(-10, -h * 0.47, 11, C.fig); circ(46, -h * 0.47, 11, C.fig);
  ctx.restore(); noGlow();
}
// front view door. o.light: hallway light under the door 0..1; o.feet: shadow count; o.open: 0..1 swing
function doorFront(x, y, w, h, o = {}) {
  ln(x - 40, y + h, x + w + 40, y + h, 4, C.dim);
  rrS(x - 16, y - 16, w + 32, h + 16, 2, C.mid, 7);
  if (o.light) { ctx.save(); ctx.globalAlpha *= o.light; glow('rgba(255,250,235,0.95)', 34); rr(x, y + h - 4, w, 10, 0, '#fffaf0'); noGlow();
    const g = ctx.createLinearGradient(0, y + h, 0, y + h + 140); g.addColorStop(0, 'rgba(255,250,235,0.22)'); g.addColorStop(1, 'rgba(255,250,235,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(x, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w + 160, y + h + 140); ctx.lineTo(x - 160, y + h + 140); ctx.fill(); ctx.restore();
    for (const f of (o.feet || [])) { ctx.save(); ctx.globalAlpha *= f.a ?? 1; rr(x + w * f.x - w * 0.06, y + h - 5, w * 0.12, 12, 2, '#000'); ctx.restore(); } }
  const op = o.open || 0;
  if (op > 0) { rr(x, y, w, h - 4, 2, '#0b0b0b'); if (o.inside) o.inside(); }
  ctx.save(); ctx.translate(x, y); ctx.transform(1 - op * 0.75, op * 0.12, 0, 1, 0, 0);
  rr(0, 0, w, h - 4, 3, '#151515');
  rrS(w * 0.12, h * 0.06, w * 0.76, h * 0.38, 6, C.mid, 5); rrS(w * 0.12, h * 0.52, w * 0.76, h * 0.4, 6, C.mid, 5);
  glow(); circ(w * 0.9, h * 0.53, w * 0.035, C.fig); noGlow();
  ctx.restore();
}
// ordinary small cat sitting, side view facing right; feet at (x,y)
function sitCat(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(o.flip ? -s : s, s);
  glow('rgba(255,255,255,0.3)', 16);
  const puff = o.puff || 0;
  pthS('M-40,-8 C-84,-4 -96,-44 -72,-70', C.sec, 9 + puff * 16);
  ell(0, -42, 46, 40, 0, C.fig);
  const hx = o.push ? 54 : 40, hy = (o.push ? -80 : -88) + (o.down || 0) * 50;
  const ear = (o.ear || 0) * 14;
  circ(hx, hy, 29, C.fig);
  pth(`M${hx - 24},${hy - 12} L${hx - 20 + ear},${hy - 48} L${hx - 2},${hy - 23} Z`, C.fig);
  pth(`M${hx + 2},${hy - 25} L${hx + 20 + ear},${hy - 48} L${hx + 25},${hy - 10} Z`, C.fig);
  if (o.paw) ln(30, -30, 68, -66 - 10 * Math.sin(o.paw * 22), 12, C.fig); else ln(28, -6, 42, 0, 12, C.fig);
  noGlow();
  if (o.closed) ln(hx + 6, hy - 4, hx + 20, hy - 4, 4, '#000'); else { circ(hx + 13, hy - 5, 5, '#000'); }
  ctx.restore();
}
// cat lying down (loaf), facing right
function lyingCat(x, y, s, eyes = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  pthS('M-62,-10 C-90,-6 -96,8 -60,4', C.sec, 9);
  ell(0, -26, 66, 28, 0, C.fig); circ(58, -38, 26, C.fig);
  pth('M40,-50 L44,-82 L60,-58 Z', C.fig); pth('M62,-60 L80,-80 L82,-46 Z', C.fig); noGlow();
  if (eyes > 0.15) ell(70, -42, 4.5, 4.5 * eyes, 0, '#000'); else ln(64, -42, 76, -42, 3.5, '#000');
  ctx.restore();
}
// the thing in the hallway: a cat body stretched to human height. Feet at (x,y), faces left toward the door.
// k: knocking arm 0 (on the door) .. 1 (pulled back); tilt: head tilt degrees; eye: red eye brightness
function standCat(x, y, s = 1, o = {}) {
  const k = o.k || 0, tilt = o.tilt || 0, eye = o.eye ?? 1, sway = o.sway || 0;
  const col = o.col || '#e9e9e9', col2 = o.col2 || '#a9a9a9';
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(sway * D2R);
  glow('rgba(255,255,255,0.28)', 20);
  // tail, thin and too long, hanging to the floor
  pthS('M24,-300 C70,-250 74,-150 58,-60 C52,-20 80,-6 104,-14', col2, 12);
  // back leg (far)
  poly([[18, -300], [50, -186], [16, -84], [36, -6]], 22, col2); ell(48, -4, 30, 9, 0, col2);
  // near leg: long thigh, knee bent the wrong way, long hock
  poly([[0, -306], [-30, -186], [10, -78], [-6, -6]], 30, col); ell(-24, -4, 34, 10, 0, col);
  // far arm hanging past the hips, long fingers
  poly([[14, -470], [34, -360], [26, -236]], 18, col2);
  for (let i = 0; i < 4; i++) ln(26, -236, 18 + i * 7, -196 + i * 3, 6, col2);
  // torso: narrow, hunched forward
  pth('M-28,-470 C-46,-430 -40,-360 -22,-318 C-12,-296 22,-292 30,-312 C44,-360 46,-430 26,-478 C10,-500 -16,-494 -28,-470 Z', col);
  noGlow();
  ctx.globalAlpha *= 0.55; for (let i = 0; i < 4; i++) pthS(`M${-30 + i * 2},${-440 + i * 26} q22,8 44,0`, '#000', 4); ctx.globalAlpha /= 0.55;
  glow('rgba(255,255,255,0.28)', 20);
  // neck, too long
  poly([[-6, -478], [-22, -540]], 30, col);
  // knocking arm: shoulder -> elbow -> human hand on the door
  const hx = lerp(-150, -112, k), hy = lerp(-430, -446, k);
  poly([[-18, -462], [-84, -392], [hx, hy]], 20, col);
  circ(hx, hy, 15, col);
  for (let i = 0; i < 4; i++) ln(hx - 2, hy - 10 + i * 7, hx - 22, hy - 14 + i * 9, 6, col);
  // head, tilted
  ctx.save(); ctx.translate(-28, -566); ctx.rotate(tilt * D2R);
  pth('M-34,-24 L-30,-80 L-4,-40 Z', col); pth('M6,-42 L34,-84 L36,-18 Z', col);
  circ(0, 0, 46, col); ell(-40, 12, 15, 13, 0, col);
  noGlow();
  // too-wide mouth
  pthS('M-50,20 C-30,34 4,34 20,22', '#000', 4);
  pth('M-55,4 l9,0 l-4.5,6 z', '#000');
  ctx.save(); ctx.globalAlpha *= eye; redGlow(26); ell(-16, -8, 13, 11, 0, C.red); noGlow(); ctx.restore();
  rr(-18, -18, 4, 20, 2, '#000');
  ctx.restore();
  noGlow(); ctx.restore();
}
// big cat face (front) for close-ups; ears: -1..1 turn toward the door (left); eyes 0..1 open
function catFace(x, y, s, o = {}) {
  const ear = o.ear || 0, eyes = o.eyes ?? 1;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 24);
  ctx.save(); ctx.translate(-92, -120); ctx.rotate(-ear * 28 * D2R); pth('M-40,40 L-10,-70 L50,20 Z', C.fig); ctx.restore();
  ctx.save(); ctx.translate(92, -120); ctx.rotate(-ear * 28 * D2R); pth('M40,40 L10,-70 L-50,20 Z', C.fig); ctx.restore();
  ell(0, 0, 170, 140, 0, C.fig); noGlow();
  for (const d of [-1, 1]) {
    ell(d * 66, -10, 30, 30 * eyes + 0.5, 0, '#000');
    if (eyes > 0.2) rr(d * 66 - 4, -10 - 22 * eyes, 8, 44 * eyes, 4, '#fff');
  }
  pth('M-14,40 L14,40 L0,56 Z', '#000');
  for (const d of [-1, 1]) for (let i = 0; i < 3; i++) ln(d * 110, 40 + i * 16, d * 240, 22 + i * 26, 4, C.sec);
  ctx.restore();
}
// person pictogram standing; feet at (x,y)
function person(x, y, s = 1, col = C.fig, arm = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.25)', 14);
  circ(0, -330, 30, col); rr(-26, -290, 52, 140, 20, col);
  ln(-12, -160, -14, -8, 22, col); ln(12, -160, 14, -8, 22, col);
  ln(-24, -270, -34, -170, 18, col);
  ln(24, -270, lerp(34, 70, arm), lerp(-170, -300, arm), 18, col);
  noGlow(); ctx.restore();
}
function icon(name, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  if (name === 'getup') { rr(-110, 40, 220, 24, 10, C.sec); rr(-110, -40, 16, 104, 6, C.fig); circ(-30, -60, 28, C.fig); rr(-56, -32, 60, 72, 18, C.fig);
    ln(70, 20, 70, -70, 12, C.fig); pth('M46,-56 L70,-92 L94,-56 Z', C.fig); }
  if (name === 'bulb') { ctx.beginPath(); ctx.arc(0, -30, 62, Math.PI * 0.8, Math.PI * 2.2); ctx.lineTo(26, 46); ctx.lineTo(-26, 46); ctx.closePath(); ctx.fillStyle = C.fig; ctx.fill();
    rr(-26, 52, 52, 14, 4, C.sec); rr(-22, 70, 44, 12, 4, C.sec); }
  if (name === 'mouth') { circ(-30, -10, 70, C.fig); noGlow(); pth('M10,-6 C30,-16 30,8 10,4 Z', '#000'); glow();
    for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(40, -6, 50 + i * 26, -0.6, 0.6); ctx.strokeStyle = C.fig; ctx.lineWidth = 8; ctx.stroke(); } }
  if (name === 'eye') { pth('M-90,0 C-50,-56 50,-56 90,0 C50,56 -50,56 -90,0 Z', C.fig); noGlow(); circ(0, 0, 26, '#000'); }
  if (name === 'ear') { pthS('M-30,50 C-60,20 -60,-60 0,-70 C60,-74 70,0 30,20 C10,30 14,60 -6,70', C.fig, 16); pthS('M-14,10 C-20,-20 0,-40 20,-24', C.fig, 10); }
  if (name === 'paw') { ell(0, 20, 46, 38, 0, C.fig); for (let i = 0; i < 4; i++) ell(-48 + i * 32, -40 - (i % 3 ? 14 : 0), 16, 20, 0, C.fig); }
  if (name === 'fist') { rr(-50, -50, 100, 96, 26, C.fig); noGlow(); for (let i = 1; i < 4; i++) ln(-50 + i * 25, -50, -50 + i * 25, -14, 4, '#000'); }
  if (name === 'moon') { circ(0, 0, 40, C.fig); noGlow(); circ(18, -12, 36, '#000'); }
  if (name === 'sun') { circ(0, 0, 40, C.fig); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; ln(Math.cos(a) * 58, Math.sin(a) * 58, Math.cos(a) * 80, Math.sin(a) * 80, 8, C.fig); } }
  if (name === 'foot') { ell(0, 0, 18, 34, 0, C.fig); for (let i = 0; i < 4; i++) circ(-15 + i * 10, -44 + Math.abs(i - 1.5) * 4, 6, C.fig); }
  noGlow(); ctx.restore();
}
function bubble(x, y, w, h, s, t, t0, col = C.fig, txtCol = '#000', tail = 1) {
  pop(t, t0, x, y, () => { glow(); rr(x - w / 2, y - h / 2, w, h, 26, col); pth(`M${x - tail * 30},${y + h / 2 - 2} L${x - tail * 60},${y + h / 2 + 40} L${x + tail * 6},${y + h / 2 - 2} Z`, col); noGlow();
    text(s, x, y + 2, `900 ${Math.round(h * 0.42)}px M`, txtCol, 'center', 'middle'); });
}
// label box like a manual callout
function tag(s, x, y, col = C.fig, size = 30, align = 'left') {
  ctx.font = `900 ${size}px M`; const w = ctx.measureText(s).width + 28;
  const x0 = align === 'left' ? x : align === 'right' ? x - w : x - w / 2;
  rrS(x0, y - size * 0.95, w, size * 1.5, 6, col, 4); text(s, x0 + w / 2, y + 2, `900 ${size}px M`, col);
}
function ruler(x, yFloor, pxPerCm, maxCm, col = C.dim, labelEvery = 40) {
  ln(x, yFloor, x, yFloor - maxCm * pxPerCm, 3, col);
  for (let v = 0; v <= maxCm; v += 20) { ln(x - 9, yFloor - v * pxPerCm, x + 9, yFloor - v * pxPerCm, 3, col);
    if (v % labelEvery === 0) text(v + '', x - 16, yFloor - v * pxPerCm + 8, '22px Plex', col, 'right'); }
}
function gauge(x, y, r, label, v, col, t, t0) {
  pop(t, t0, x, y, () => {
    ctx.beginPath(); ctx.arc(x, y, r, Math.PI, 2 * Math.PI); ctx.strokeStyle = C.dim; ctx.lineWidth = 14; ctx.stroke();
    const k = easeOut((t - t0 - 0.15) / 0.7) * v;
    ctx.beginPath(); ctx.arc(x, y, r, Math.PI, Math.PI + Math.PI * k); ctx.strokeStyle = col; ctx.lineWidth = 14; if (col === C.red) redGlow(14); ctx.stroke(); noGlow();
    const a = Math.PI + Math.PI * k; ln(x, y, x + Math.cos(a) * r * 0.82, y + Math.sin(a) * r * 0.82, 7, C.fig); circ(x, y, 12, C.fig);
    spaced(label, x, y + 66, '900 34px M', col, 3);
  });
}

// ---------- step header + manual card ----------
function stepCard(t, seg, n, line) {
  const t0 = seg.start;
  cam(t, t0, seg.end - t0 + 0.6, 1, 1.05, W / 2, H / 2, () => {
    slideIn(t, t0, -60, 0, () => {
      glow('rgba(255,255,255,0.3)', 30); rr(560, 300, 230, 230, 14, C.fig); noGlow();
      text(String(n).padStart(2, '0'), 675, 418, '900 150px M', '#000', 'center', 'middle');
    });
    slideIn(t, t0 + 0.08, 60, 0, () => { spaced('STEP', 830, 360, '900 40px M', C.mid, 14, 'left'); });
    // instruction text types in word by word
    const ws = line.split(' '), tw = seg.words.slice(2); let shown = 0;
    for (let i = 0; i < ws.length; i++) if (t >= (tw[i] ? tw[i].s - 0.05 : seg.end)) shown = i + 1;
    const lines = []; let cur = '';
    for (const w of ws.slice(0, shown)) { if ((cur + ' ' + w).trim().length > 16) { lines.push(cur); cur = w; } else cur = (cur + ' ' + w).trim(); }
    if (cur) lines.push(cur);
    lines.forEach((l, i) => text(l, 830, 446 + i * 74, '900 68px M', C.fig, 'left'));
    const lp = prog(t, t0 + 0.3, 0.6); redGlow(12); lnP(560, 580, 1360, 580, 6, C.red, easeOut(lp)); noGlow();
    // four step pips, the fourth never filled
    for (let i = 0; i < 4; i++) { const x = 560 + i * 54, y = 618, a = prog(t, t0 + 0.4 + i * 0.06, 0.2);
      ctx.save(); ctx.globalAlpha *= a;
      if (i + 1 < n) rr(x, y, 38, 38, 5, C.sec); else if (i + 1 === n) { redGlow(12); rr(x, y, 38, 38, 5, C.red); noGlow(); } else rrS(x, y, 38, 38, 5, C.mid, 3);
      if (i === 3) text('?', x + 19, y + 31, '900 28px M', i + 1 === n ? '#000' : C.mid);
      ctx.restore(); }
  });
}

// ---------- scenes ----------
// room cutaway used by several shots: bed, wall with door, hallway
function room(t, o = {}) {
  ln(0, 860, W, 860, 4, C.dim);
  bed(150, 860, 1.05, o.person || 'woke', { look: 1 });
  if (o.cat) o.cat();
  doorEdge(1080, 860, 500, o.open || 0);
  if (o.hall) o.hall();
}
const S = {};
S.s01 = (t, seg) => {
  // opening: the thumbnail scene, the thing knocks in the hallway
  const p = knockPulse(t), lk = lastKnock(t), k = p > 0 ? 1 - p : 0.7;
  cam(t, 0, 7, 1.0, 1.06, 1100, 560, () => {
    ctx.save(); if (p > 0.6) shake(3 * p, t);
    room(t, { hall: () => standCat(1250, 860, 1.0, { k: clamp(k), tilt: -8 + 4 * Math.sin(t * 0.8), eye: 0.8 + 0.2 * Math.sin(t * 3) }) });
    ctx.restore();
    knockLines(1050, 430, p, C.red, 1);
    if (lk > 0) ripple(1080, 430, lk, t, C.red, 10, 110);
  });
  if (t > wt(seg, 'not') - 0.05 && t < seg.end + 1) pop(t, wt(seg, 'not') - 0.05, 960, 190, () => { tag('DO NOT OPEN', 960, 200, C.red, 46, 'center'); }, 0.3);
};
S.s02 = (t, seg) => {
  const items = [['getup', 520, 'get'], ['bulb', 960, 'turn'], ['mouth', 1400, 'call']];
  cam(t, seg.start, seg.end - seg.start, 1, 1.04, W / 2, 470, () => {
    items.forEach(([ic, x, w], i) => {
      const t0 = wt(seg, w) - 0.25;
      pop(t, t0, x, 470, () => { rrS(x - 170, 300, 340, 340, 26, C.dim, 5); icon(ic, x, 470, 1.05); });
      redX(x, 470, 120, prog(t, wt(seg, w) + 0.35, 0.35));
    });
  });
};
S.s03 = (t, seg) => {
  cam(t, seg.start, 3, 0.96, 1.04, W / 2, 480, () => {
    pop(t, seg.start, W / 2, 480, () => {
      glow('rgba(255,255,255,0.35)', 40);
      const sec = Math.floor(t - seg.start) % 60;
      text('03', 760, 560, '900 260px M', C.fig); text('12', 1160, 560, '900 260px M', C.fig);
      if ((t % 1) < 0.6) text(':', 960, 540, '900 240px M', C.fig);
      noGlow(); redGlow(16); text('AM', 1390, 560, '900 80px M', C.red, 'left'); noGlow();
      text(':' + String(14 + sec).padStart(2, '0'), 1390, 470, '600 50px Plex', C.mid, 'left');
    });
    // a tiny bed and a moon to place us in the night
    fadeIn(t, seg.start + 0.5, () => { icon('moon', 960, 750, 0.8); });
  });
};
S.s04 = (t, seg) => {
  const tf = wt(seg, 'there'), th = wt(seg, 'three', 1);
  if (t < tf - 0.1) {
    // the manual: a sheet slides up, stamped
    cam(t, seg.start, tf - seg.start, 1, 1.05, W / 2, 520, () => {
      slideIn(t, seg.start, 0, 260, () => {
        glow('rgba(255,255,255,0.25)', 30); rr(660, 170, 600, 700, 10, '#ececec'); noGlow();
        rr(660, 170, 600, 90, 10, '#111'); spaced('INSTRUCTION', 960, 232, '900 44px M', C.fig, 8);
        text('001', 960, 360, '900 140px M', '#000');
        text('IF YOUR CAT KNOCKS', 960, 430, '900 34px M', '#000');
        for (let i = 0; i < 5; i++) rr(720, 480 + i * 46, 480 - (i % 2) * 120, 14, 4, '#bdbdbd');
      }, 0.55);
      const tfo = wt(seg, 'follow');
      pop(t, tfo + 0.2, 1170, 760, () => { ctx.save(); ctx.translate(1170, 760); ctx.rotate(-12 * D2R);
        redGlow(10); rrS(-150, -46, 300, 92, 10, C.red, 7); text('IN ORDER', 0, 16, '900 48px M', C.red); noGlow(); ctx.restore(); }, 0.3);
    });
    return;
  }
  cam(t, tf, seg.end - tf + 0.7, 1, 1.06, W / 2, 470, () => {
    for (let i = 0; i < 4; i++) {
      const x = 960 + (i - 1.5) * 260, y = 470, t0 = tf + 0.6 + i * 0.16;
      const missing = i === 3 && t > th;
      pop(t, t0, x, y, () => {
        if (missing) { ctx.save(); if ((t * 12 | 0) % 7 === 0) ctx.translate(8, 0); redGlow(20); rrS(x - 95, y - 95, 190, 190, 16, C.red, 7); noGlow();
          text('?', x, y + 6, '900 120px M', C.red, 'center', 'middle'); ctx.restore(); }
        else { glow(); rrS(x - 95, y - 95, 190, 190, 16, C.fig, 7); noGlow(); text(String(i + 1), x, y + 6, '900 110px M', C.fig, 'center', 'middle'); }
        spaced('STEP', x, y + 160, '900 30px M', missing ? C.red : C.mid, 6);
      });
    }
  });
};
S.s05 = (t, seg) => stepCard(t, seg, 1, 'DO NOT OPEN THE DOOR');
S.s06 = (t, seg) => {
  const tb = wt(seg, 'bottom'), tm = wt(seg, 'middle');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, 900, 520, () => {
    doorFront(700, 130, 420, 760, {});
    pop(t, seg.start + 0.1, 400, 500, () => icon('ear', 400, 500, 1.2));
    if (t < tb) { ripple(910, 520, seg.start + 0.3, t, C.mid); ripple(910, 520, seg.start + 1.2, t, C.mid); }
    if (t >= tb) { ripple(910, 860, tb + Math.floor((t - tb) / 1.2) * 1.2, t, C.mid, 10, 90, 5);
      pop(t, tb, 1250, 870, () => { text('NOT HERE', 1250, 880, '900 46px M', C.mid, 'left'); ln(1240, 868, 1500, 868, 6, C.mid); }); }
    if (t >= tm) { for (let k = 0; k < 5; k++) ripple(910, 500, tm + k * 0.5, t, C.red, 20, 200);
      pop(t, tm, 1250, 510, () => { redGlow(18); text('HERE', 1250, 530, '900 84px M', C.red, 'left'); ln(1230, 500, 1150, 500, 9, C.red); noGlow(); }); }
  });
};
function catChecklist(t, rows) {
  rows.forEach(([label, t0, mark], i) => {
    const y = 330 + i * 120;
    slideIn(t, t0, 50, 0, () => {
      rrS(1250, y - 46, 70, 70, 10, mark === 'x' ? C.red : C.mid, 5);
      text(label, 1350, y + 8, '900 60px M', mark === 'x' ? C.red : C.fig, 'left');
      if (mark === 'x') redX(1285, y - 11, 26, prog(t, t0 + 0.25, 0.3)); else check(1285, y - 11, 26, prog(t, t0 + 0.2, 0.3));
    });
  });
}
S.s07 = (t, seg) => {
  const ts = wt(seg, 'scratch'), tp = wt(seg, 'push'), tc = wt(seg, 'cry');
  const o = {}; if (t >= ts && t < tp) o.paw = t; if (t >= tp && t < tc) o.push = true;
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.04, 700, 600, () => {
    ctx.save(); if (t >= tp && t < tc) { const w = Math.sin((t - tp) * 18) * 3 * (1 - prog(t, tp, 1)); ctx.translate(w, 0); }
    doorFront(560, 170, 360, 690, {}); ctx.restore();
    sitCat(420, 860, 1.7, o);
    if (t >= ts) { ctx.save(); ctx.globalAlpha *= 0.8; for (let i = 0; i < 3; i++) lnP(580 + i * 22, 840 - i * 6, 610 + i * 22, 780 - i * 6, 6, C.fig, prog(t, ts + i * 0.1, 0.15)); ctx.restore(); }
    if (t >= tc) bubble(330, 560, 250, 110, 'MEOW', t, tc);
    catChecklist(t, [['SCRATCH', ts, 'v'], ['PUSH', tp, 'v'], ['CRY', tc, 'v']]);
  });
};
S.s08 = (t, seg) => {
  const tn = wt(seg, 'not'), tc = wt(seg, 'cats');
  if (t < tc - 0.05) {
    cam(t, seg.start, tc - seg.start, 1.04, 1.06, 700, 600, () => {
      doorFront(560, 170, 360, 690, {}); sitCat(420, 860, 1.7, {});
      catChecklist(t, [['SCRATCH', -9, 'v'], ['PUSH', -9, 'v'], ['CRY', -9, 'v'], ['KNOCK', tn, 'x']]);
    });
    return;
  }
  cam(t, tc, seg.end - tc + 0.6, 1, 1.06, W / 2, 480, () => {
    pop(t, tc, 640, 480, () => icon('paw', 640, 480, 2.0));
    pop(t, tc + 0.25, 1280, 480, () => icon('fist', 1280, 480, 2.0));
    pop(t, tc + 0.45, 960, 480, () => { redGlow(14); ln(910, 450, 1010, 450, 12, C.red); ln(910, 510, 1010, 510, 12, C.red); lnP(990, 410, 930, 550, 12, C.red, 1); noGlow(); });
    fadeIn(t, tc + 0.1, () => { spaced('CAT', 640, 700, '900 40px M', C.mid, 8); spaced('KNOCK', 1280, 700, '900 40px M', C.mid, 8); });
  });
};
S.s09 = (t, seg) => {
  // knock height: a person on the bedroom side for scale, the knock at hand height
  const th = wt(seg, 'height'), boom = evs('boom')[0];
  if (boom && t >= boom.t - 0.02) {
    // reveal: the thing, full height, flash in
    const k = t - boom.t;
    cam(t, boom.t, 1.6, 1.12, 1.0, 1400, 560, () => {
      room(t, { hall: () => standCat(1250, 860, 1.0, { k: 0.2 + 0.2 * Math.sin(t * 5), tilt: -10, eye: 1 }) });
    });
    if (k < 0.12) { ctx.fillStyle = `rgba(255,255,255,${0.5 * (1 - k / 0.12)})`; ctx.fillRect(0, 0, W, H); }
    return;
  }
  cam(t, seg.start, seg.end - seg.start + 0.5, 1, 1.05, 1000, 560, () => {
    ln(0, 860, W, 860, 4, C.dim);
    doorEdge(1080, 860, 500);
    person(860, 860, 1.0, C.mid, prog(t, th, 0.4));
    ruler(640, 860, 2.9, 180);
    const y160 = 860 - 160 * 2.9;
    if (t >= th) { const p = prog(t, th, 0.4); redGlow(14); lnP(650, y160, 1060, y160, 5, C.red, p); noGlow();
      fadeIn(t, th + 0.2, () => text('160 CM', 660, y160 - 18, '700 34px Plex', C.red, 'left')); }
    const kt = seg.start + 0.3; for (let i = 0; i < 3; i++) ripple(1080, y160, kt + i * 0.6, t, C.red, 10, 120);
    // the hallway is dark; only a red eye, high up
    fadeIn(t, th, () => { redGlow(26); ell(1206, 286, 12, 10, 0, C.red); noGlow(); rr(1204, 278, 4, 18, 2, '#000'); }, 0.6);
  });
};
S.s10 = (t, seg) => {
  const tl = wt(seg, 'legs'), tm = wt(seg, 'mind');
  const t0 = seg.start;
  if (t < tl - 0.1) {
    cam(t, t0, tl - t0, 1.0, 1.08, 1300, 520, () => {
      ln(0, 860, W, 860, 4, C.dim); doorEdge(1080, 860, 500);
      standCat(1430, 860, 1.0, { k: 0.05, tilt: -10 + Math.sin(t * 0.7) * 3, sway: Math.sin(t * 1.3) * 0.8 });
      fadeIn(t, t0 + 0.6, () => { spaced('STANDING', 1640, 300, '900 34px M', C.mid, 6, 'left'); text(String(Math.floor(41 + (t - t0) * 7)).padStart(3, '0') + ' MIN', 1640, 360, '600 46px Plex', C.fig, 'left'); });
    });
    return;
  }
  if (t < tm - 0.6) {
    // legs close-up with callouts
    cam(t, tl, tm - tl, 1.6, 1.7, 1440, 700, () => {
      ln(0, 860, W, 860, 4, C.dim);
      const tr = Math.sin(t * 40) * 1.2;
      standCat(1430 + tr, 860, 1.0, { k: 0.05, tilt: -10 });
      pop(t, tl + 0.2, 1380, 680, () => { redGlow(12); circS(1400, 676, 30, C.red, 4); ln(1370, 676, 1250, 640, 4, C.red); noGlow(); text('KNEE', 1240, 640, '900 26px M', C.red, 'right'); });
      pop(t, tl + 0.6, 1440, 790, () => { redGlow(12); circS(1440, 790, 26, C.red, 4); ln(1414, 796, 1300, 790, 4, C.red); noGlow(); text('WRONG WAY', 1290, 798, '900 26px M', C.red, 'right'); });
    });
    return;
  }
  // head slowly turns toward us
  const z = lerp(1.6, 1.85, ease((t - tm + 0.6) / 3));
  ctx.save(); ctx.translate(960, 520); ctx.scale(z, z); ctx.translate(-1400, -330);
  (() => {
    ln(0, 860, W, 860, 4, C.dim);
    standCat(1430, 860, 1.0, { k: 0.05, tilt: lerp(-10, 24, ease((t - tm + 0.4) / 2.2)), eye: 1 });
  })(); ctx.restore();
};
S.s11 = (t, seg) => stepCard(t, seg, 2, 'DO NOT LOOK UNDER THE DOOR');
S.s12 = (t, seg) => {
  const tl = wt(seg, 'light'), tn = wt(seg, 'not');
  const fl = t < tl ? 0 : ((t - tl) < 0.35 ? ((t * 30 | 0) % 2) : 1);
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, 960, 700, () => {
    doorFront(760, 120, 400, 740, { light: fl });
    pop(t, tn, 480, 480, () => { rrS(400, 360, 160, 240, 16, C.mid, 5); rr(450, 410, 60, 140, 10, C.dark); rr(458, 480, 44, 62, 8, C.fig);
      text('OFF', 480, 650, '900 36px M', C.mid); });
    pop(t, tn + 0.2, 1450, 480, () => { tag('HALLWAY: ON', 1360, 490, C.red, 40); });
  });
};
S.s13 = (t, seg) => {
  const tg = wt(seg, 'gap'), tt = wt(seg, 'two'), tf = wt(seg, 'four');
  if (t < tf - 0.1) {
    // zoom into the gap under the door
    // zoom into the gap: it moves from the bottom of the frame to the centre
    const k = ease((t - seg.start) / Math.max(0.5, tt - seg.start)), z = lerp(1, 2.4, k);
    ctx.save(); ctx.translate(960, lerp(860, 520, k)); ctx.scale(z, z); ctx.translate(-960, -860);
    (() => {
      doorFront(760, 120, 400, 740, { light: 1, feet: t >= tt ? [{ x: 0.36, a: prog(t, tt, 0.4) }, { x: 0.62, a: prog(t, tt + 0.25, 0.4) }] : [] });
    })(); ctx.restore();
    if (t >= tt) pop(t, tt + 0.3, 1640, 300, () => { spaced('SHADOWS', 1640, 240, '900 34px M', C.mid, 6); text('2', 1640, 400, '900 150px M', C.fig); });
    return;
  }
  cam(t, tf, seg.end - tf + 0.6, 1, 1.05, W / 2, 480, () => {
    pop(t, tf - 0.05, 620, 470, () => { sitCat(560, 600, 2.2, {}); });
    pop(t, tf + 0.15, 1240, 470, () => { for (let i = 0; i < 4; i++) icon('foot', 1080 + i * 100, 470, 1.0); });
    fadeIn(t, tf + 0.3, () => { spaced('YOUR CAT', 620, 760, '900 36px M', C.mid, 6); text('4', 1240, 700, '900 110px M', C.fig); });
  });
};
S.s14 = (t, seg) => {
  const tn = wt(seg, 'number');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1, 1.12, 960, 820, () => {
    // the two shadows, steady; the counter will not change
    doorFront(560, -260, 800, 1100, { light: 1, feet: [{ x: 0.36 }, { x: 0.62 }] });
    const flick = (t * 20 | 0) % 9 === 0;
    pop(t, seg.start, 960, 420, () => { if (t >= tn) redGlow(30); else glow(); text('2', 960 + (flick ? 6 : 0), 520, '900 300px M', t >= tn ? C.red : C.fig); noGlow(); });
    redX(960, 420, 150, prog(t, wt(seg, 'count') + 0.1, 0.35) * (t < tn ? 1 : 0));
  });
};
S.s15 = (t, seg) => {
  // the meow: a waveform that is wrong
  const m = evs('meow1')[0];
  cam(t, seg.start, 5, 1, 1.08, W / 2, 500, () => {
    doorFront(760, 120, 400, 740, { light: 0.6 });
    const on = m && t >= m.t && t < m.t + 3.2;
    if (on) {
      const k = (t - m.t) / 3.2;
      ctx.save(); redGlow(20); ctx.beginPath();
      for (let x = 300; x <= 1620; x += 6) { const env = Math.sin(Math.PI * clamp((x - 300) / 1320)) * Math.sin(Math.PI * k);
        const y = 500 + Math.sin(x * 0.045 + t * 9) * 110 * env * (0.6 + 0.4 * Math.sin(x * 0.011 - t * 3));
        x === 300 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
      ctx.strokeStyle = C.red; ctx.lineWidth = 7; ctx.stroke(); noGlow(); ctx.restore();
      const s = 'M E O W'.slice(0, Math.max(1, Math.floor(k * 9)));
      ctx.save(); ctx.translate(960, 300); ctx.scale(1 + k * 0.6, 1 - k * 0.15); redGlow(14); text(s, 0, 0, '900 110px M', C.red, 'center', 'middle'); noGlow(); ctx.restore();
    }
  });
};
S.s16 = (t, seg) => {
  const tm = wt(seg, 'meow', 2);
  if (t < tm - 0.2) {
    cam(t, seg.start, tm - seg.start, 1, 1.05, W / 2, 600, () => {
      ln(300, 780, 1620, 780, 4, C.dim);
      pop(t, seg.start, 650, 780, () => sitCat(650, 780, 1.6, {}));
      pop(t, seg.start + 0.15, 1270, 780, () => sitCat(1270, 780, 1.6, { flip: true }));
      bubble(780, 470, 220, 100, 'MEOW', t, seg.start + 0.6);
      redX(780, 470, 70, prog(t, wt(seg, 'never') + 0.1, 0.35));
      fadeIn(t, wt(seg, 'almost'), () => { spaced('CAT TO CAT', 960, 880, '900 34px M', C.mid, 6); });
    });
    return;
  }
  cam(t, tm, seg.end - tm + 0.6, 1, 1.05, W / 2, 600, () => {
    ln(300, 820, 1620, 820, 4, C.dim);
    pop(t, tm - 0.15, 600, 820, () => sitCat(600, 820, 1.6, {}));
    pop(t, tm, 1300, 820, () => person(1300, 820, 1.3, C.fig));
    bubble(800, 520, 220, 100, 'MEOW', t, tm + 0.2);
    check(980, 520, 36, prog(t, wt(seg, 'people'), 0.35));
    fadeIn(t, wt(seg, 'only'), () => { spaced('CAT TO HUMAN', 960, 920, '900 34px M', C.mid, 6); });
  });
};
S.s17 = (t, seg) => {
  const tl = wt(seg, 'long');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, 900, 520, () => {
    ln(0, 860, W, 860, 4, C.dim); doorEdge(760, 860, 500);
    standCat(1080, 860, 1.0, { k: 1, tilt: 22 + Math.sin(t * 2) * 2, eye: 0.9, col: '#5c5c5c', col2: '#3c3c3c' });
    // recordings of the sound, collected over time
    const n = Math.floor(clamp((t - seg.start - 0.5) / (seg.end - seg.start)) * 14);
    for (let i = 0; i < n; i++) { const x = 1320 + (i % 7) * 72, y = 300 + Math.floor(i / 7) * 120;
      ctx.save(); ctx.globalAlpha *= 0.9; ctx.beginPath(); for (let j = 0; j < 48; j++) { const yy = y + Math.sin(j * 0.6 + i) * 22 * Math.sin(Math.PI * j / 48); j ? ctx.lineTo(x + j, yy) : ctx.moveTo(x, yy); }
      ctx.strokeStyle = i % 4 === 3 ? C.red : C.sec; ctx.lineWidth = 4; ctx.stroke(); ctx.restore(); }
    fadeIn(t, seg.start + 0.6, () => { spaced('SAMPLES', 1320, 250, '900 30px M', C.mid, 6, 'left'); text(String(n * 83 + 17).padStart(4, '0'), 1880, 250, '600 36px Plex', C.fig, 'right'); });
    if (t >= tl) fadeIn(t, tl, () => { text('SINCE 2009', 1320, 600, '600 34px Plex', C.red, 'left'); });
  });
};
S.s18 = (t, seg) => {
  const ts = wt(seg, 'slow'), tlo = wt(seg, 'low'), th = wt(seg, 'high'), m = evs('meow2')[0];
  if (m && t >= m.t - 0.15) {
    // it meows again, from 160 cm
    cam(t, m.t, 3, 1.0, 1.1, 1300, 380, () => {
      room(t, { person: 'woke', hall: () => { ctx.save(); ctx.globalAlpha *= 0.0; ctx.restore(); } });
      for (let k = 0; k < 4; k++) ripple(1206, 286, m.t + k * 0.5, t, C.red, 20, 260);
      redGlow(26); ell(1206, 286, 12, 10, 0, C.red); noGlow(); rr(1204, 278, 4, 18, 2, '#000');
    });
    return;
  }
  cam(t, seg.start, seg.end - seg.start + 0.4, 1, 1.04, W / 2, 500, () => {
    pop(t, seg.start, 960, 260, () => { spaced('IT IS CLOSE', 960, 230, '900 46px M', C.fig, 8); });
    gauge(520, 600, 170, 'TOO SLOW', 0.12, C.red, t, ts - 0.2);
    gauge(960, 600, 170, 'TOO LOW', 0.08, C.red, t, tlo - 0.2);
    // height: a cat should be here
    pop(t, th - 0.3, 1400, 600, () => {
      ruler(1330, 760, 2.4, 180, C.dim);
      redGlow(16); ell(1400, 760 - 160 * 2.4, 12, 10, 0, C.red); noGlow();
      rr(1370, 760 - 30 * 2.4, 60, 30 * 2.4, 10, C.mid); spaced('TOO HIGH', 1430, 830, '900 34px M', C.red, 3);
    });
  });
};
S.s19 = (t, seg) => stepCard(t, seg, 3, 'LOOK AT THE FOOT OF YOUR BED');
S.s20 = (t, seg) => {
  const tn = wt(seg, 'night');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.25, 1.45, 820, 640, () => {
    room(t, { person: 'woke', cat: () => pop(t, seg.start + 0.2, 700, 684, () => sitCat(690, 684, 0.9, { flip: false })) });
    pop(t, seg.start + 0.5, 700, 520, () => { glow(); pthS('M700,560 l0,-40 M684,534 l16,-16 l16,16', C.fig, 7); noGlow(); spaced('YOUR CAT', 700, 500, '900 30px M', C.fig, 4); });
    fadeIn(t, tn, () => text('ALL NIGHT', 900, 560, '600 30px Plex', C.mid, 'left'));
  });
};
S.s21 = (t, seg) => {
  const tk = wt(seg, 'knocking'), p = knockPulse(t), lk = lastKnock(t);
  cam(t, seg.start, 4.5, 1.0, 1.12, 1080, 520, () => {
    ctx.save(); if (p > 0.6) shake(4 * p, t);
    room(t, { person: 'woke', cat: () => sitCat(690, 684, 0.9, { ear: p > 0 ? 1 : 0.4 }) });
    ctx.restore();
    if (t >= tk) pop(t, tk, 1450, 420, () => { redGlow(30); text('?', 1450, 520, '900 300px M', C.red); noGlow(); });
    knockLines(1050, 430, p, C.red, 1); if (lk > seg.start) ripple(1080, 430, lk, t, C.red, 10, 120);
  });
};
S.s22 = (t, seg) => {
  const tw = wt(seg, 'watch', 2);
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 480, () => {
    pop(t, seg.start, 960, 470, () => icon('eye', 960, 470, 1.4));
    // sight line: first to the door (crossed), then to the cat
    pop(t, seg.start + 0.1, 1500, 470, () => { rrS(1420, 300, 160, 300, 8, C.mid, 6); circ(1555, 460, 8, C.mid); });
    ctx.setLineDash([16, 14]); ln(1110, 470, 1400, 470, 6, t < tw ? C.fig : C.dim); ctx.setLineDash([]);
    redX(1255, 470, 40, prog(t, wt(seg, 'door') + 0.1, 0.3));
    if (t >= tw) { pop(t, tw, 420, 560, () => sitCat(400, 600, 1.4, {}));
      ctx.setLineDash([16, 14]); lnP(810, 470, 520, 520, 6, C.fig, prog(t, tw, 0.4)); ctx.setLineDash([]); }
  });
};
S.s23 = (t, seg) => {
  const tf = wt(seg, 'footsteps'), tb = wt(seg, 'breathing');
  if (t < tf - 0.1) {
    cam(t, seg.start, tf - seg.start, 1, 1.04, W / 2, 520, () => {
      const base = 760;
      ln(420, base, 1500, base, 4, C.dim);
      const p = easeOut((t - seg.start - 0.3) / 1.4);
      pop(t, seg.start, 700, base, () => { rr(620, base - 200 * clamp(p * 3), 160, 200 * clamp(p * 3), 8, C.mid); spaced('YOU', 700, base + 56, '900 32px M', C.mid, 5); text('20 kHz', 700, base - 220 * clamp(p * 3) - 16, '600 34px Plex', C.mid); });
      pop(t, seg.start + 0.2, 1200, base, () => { glow(); rr(1120, base - 600 * p, 160, 600 * p, 8, C.fig); noGlow(); spaced('YOUR CAT', 1200, base + 56, '900 32px M', C.fig, 5); text('64 kHz', 1200, base - 600 * p - 16, '600 34px Plex', C.fig); });
    });
    return;
  }
  cam(t, tf, seg.end - tf + 0.6, 1, 1.06, W / 2, 500, () => {
    const n = Math.floor((t - tf) / 0.28);
    for (let i = 0; i < Math.min(n, 8); i++) { ctx.save(); ctx.globalAlpha *= (t < tb ? 0.9 : 0.35); icon('foot', 360 + i * 150, 560 + (i % 2) * 70, 1.0); ctx.restore(); }
    if (t >= tb) { ctx.save(); redGlow(16); ctx.beginPath();
      for (let x = 360; x <= 1560; x += 6) { const y = 420 + Math.sin((x - 360) / 1200 * Math.PI * 4 - t * 2.4) * 70 * prog(t, tb, 0.6); x === 360 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
      ctx.strokeStyle = C.red; ctx.lineWidth = 7; ctx.stroke(); noGlow(); ctx.restore(); }
    fadeIn(t, tf + 0.2, () => spaced('YOU WILL NEVER HEAR', 960, 860, '900 34px M', C.mid, 6));
  });
};
S.s24 = (t, seg) => {
  const tl = wt(seg, 'listening');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.1, W / 2, 470, () => {
    const ear = t >= tl ? Math.sin((t - tl) * 3) * 0.6 : 0;
    pop(t, seg.start, 960, 520, () => catFace(960, 520, 1.25, { ear, eyes: 1 }));
    if (t >= tl) for (let i = 0; i < 3; i++) { ctx.save(); ctx.globalAlpha *= 0.4 + 0.6 * ((Math.sin(t * 4 - i) + 1) / 2);
      ctx.beginPath(); ctx.arc(960, 470, 300 + i * 50, Math.PI * 1.08, Math.PI * 1.3); ctx.strokeStyle = C.fig; ctx.lineWidth = 7; ctx.stroke();
      ctx.beginPath(); ctx.arc(960, 470, 300 + i * 50, Math.PI * 1.7, Math.PI * 1.92); ctx.stroke(); ctx.restore(); }
  });
};
S.s25 = (t, seg) => {
  const tt = wt(seg, 'tail');
  if (t < tt - 0.3) {
    const te = wt(seg, 'ears');
    cam(t, seg.start, tt - seg.start, 1, 1.06, 900, 470, () => {
      catFace(1100, 520, 1.15, { ear: ease((t - te) / 0.6) * 1, eyes: 1 });
      pop(t, te + 0.1, 380, 470, () => { rrS(300, 270, 160, 330, 8, C.mid, 6); circ(435, 440, 8, C.mid); });
      ctx.setLineDash([14, 12]); lnP(860, 400, 480, 420, 5, C.mid, prog(t, te + 0.2, 0.4)); ctx.setLineDash([]);
      pop(t, wt(seg, 'move') - 0.3, 1100, 860, () => tag('DO NOT MOVE', 1100, 870, C.red, 46, 'center'));
    });
    return;
  }
  cam(t, tt, seg.end - tt + 0.6, 1, 1.05, W / 2, 560, () => {
    sitCat(900, 760, 2.6, { puff: ease((t - tt) / 0.5), ear: 1 });
    const tb = wt(seg, 'breath');
    pop(t, tb - 0.3, 1450, 400, () => { tag('HOLD YOUR BREATH', 1450, 410, C.red, 40, 'center');
      text(String(Math.max(0, 9 - Math.floor(t - tb))).padStart(2, '0'), 1450, 560, '600 90px Plex', C.fig); });
  });
};
S.s26 = (t, seg) => {
  const tl = wt(seg, 'lies'), tc = wt(seg, 'closes'), tg = wt(seg, 'gone'), tsl = wt(seg, 'sleep');
  if (t < tsl - 0.9) {
    cam(t, seg.start, tsl - seg.start, 1, 1.08, W / 2, 620, () => {
      ln(400, 800, 1520, 800, 4, C.dim);
      const eyes = 1 - ease((t - tc) / 0.8);
      if (t < tl) sitCat(960, 800, 2.4, {}); else lyingCat(960, 800, 2.6, eyes);
      if (t >= tg) fadeIn(t, tg, () => spaced('IT IS GONE', 960, 360, '900 50px M', C.fig, 10));
    });
    return;
  }
  // the light under the door goes out; you lie back down
  cam(t, tsl - 0.9, 3, 1.0, 1.04, 820, 600, () => {
    room(t, { person: prog(t, tsl, 0.5) > 0.5 ? 'sleep' : 'woke', cat: () => lyingCat(700, 690, 0.8, 0) });
  });
};
S.s27 = (t, seg) => {
  const tm = wt(seg, 'many'), ty = wt(seg, 'thought');
  if (t < ty - 0.1) {
    cam(t, seg.start, ty - seg.start, 1, 1.05, W / 2, 470, () => {
      const n = t < tm ? 1 : Math.floor(1 + Math.pow((t - tm) / 1.6, 2) * 120);
      for (let i = 0; i < Math.min(n, 120); i++) { const x = 260 + (i % 20) * 72, y = 230 + Math.floor(i / 20) * 86; icon('moon', x, y, 0.42); }
      pop(t, tm, 960, 860, () => { spaced('NIGHTS', 860, 880, '900 34px M', C.mid, 6, 'right'); text(String(Math.min(n * 9, 1460)).padStart(4, '0'), 900, 890, '600 60px Plex', C.fig, 'left'); });
    });
    return;
  }
  cam(t, ty, seg.end - ty + 0.6, 1.2, 1.35, 700, 600, () => {
    room(t, { person: 'sleep', cat: () => { sitCat(690, 684, 0.9, { ear: 1 }); } });
    // what you thought: zzz; what it was: eyes on the door
    const z = wt(seg, 'feet');
    ctx.save(); ctx.globalAlpha *= 1 - prog(t, z, 0.3); for (let i = 0; i < 3; i++) text('z', 760 + i * 26, 560 - i * 30 - ((t * 20) % 10), `900 ${30 + i * 8}px M`, C.mid); ctx.restore();
    if (t >= z) { ctx.setLineDash([12, 12]); lnP(740, 600, 1050, 470, 5, C.red, prog(t, z, 0.5)); ctx.setLineDash([]); }
  });
};
S.s28 = (t, seg) => {
  const to = wt(seg, 'open'), ts = wt(seg, 'safe');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, 860, 560, () => {
    pop(t, seg.start, 1500, 230, () => icon('sun', 1500, 230, 1.1));
    const op = ease((t - to) / 0.8);
    doorFront(760, 120, 400, 740, { open: op, inside: () => { const g = ctx.createLinearGradient(760, 0, 1160, 0); g.addColorStop(0, '#2a2a2a'); g.addColorStop(1, '#0b0b0b'); ctx.fillStyle = g; ctx.fillRect(760, 120, 400, 736); } });
    sitCat(620, 860, 1.6, { push: t > seg.start + 1 && t < to });
    if (t >= ts) pop(t, ts - 0.1, 1350, 600, () => { glow(); rrS(1260, 520, 180, 180, 16, C.fig, 7); noGlow(); check(1350, 600, 50, prog(t, ts, 0.35)); spaced('SAFE', 1350, 760, '900 36px M', C.fig, 6); });
  });
};
S.s29 = (t, seg) => {
  const tm = wt(seg, 'middle'), th = wt(seg, 'hand');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, 960, 520, () => {
    doorFront(760, 120, 400, 740, {});
    ruler(640, 856, 4.2, 180, C.dim);
    const lx = lerp(1300, 960, ease((t - tm) / 0.7)), ly = lerp(700, 856 - 160 * 4.2, ease((t - tm) / 0.7));
    if (t >= th) { redGlow(14); lnP(650, 856 - 160 * 4.2, 1160, 856 - 160 * 4.2, 5, C.red, prog(t, th, 0.4)); noGlow(); }
    pop(t, seg.start + 0.3, lx, ly, () => { glow(); circS(lx, ly, 90, C.fig, 10); ln(lx + 64, ly + 64, lx + 150, ly + 150, 18, C.fig); noGlow(); });
  });
};
S.s30 = (t, seg) => {
  const tp = wt(seg, 'paw'), tf = wt(seg, 'far');
  cam(t, seg.start, seg.end - seg.start + 1.0, 1, 1.08, 960, 500, () => {
    rr(460, 140, 1000, 760, 6, '#141414');
    // three long marks, like fingers dragged down the door
    for (let i = 0; i < 3; i++) { const x = 760 + i * 200, p = prog(t, seg.start + 0.15 + i * 0.22, 0.4);
      ctx.save(); ctx.globalAlpha *= 0.9; redGlow(10); lnP(x, 300, x + 14, 620, 18, '#b81f1f', easeOut(p)); noGlow(); ctx.restore(); }
    if (t >= tp) pop(t, tp, 960, 460, () => { ctx.save(); ctx.globalAlpha *= 0.85; icon('paw', 960, 460, 0.9); ctx.restore(); });
    if (t >= tf) { const p = prog(t, tf, 0.4); ln(767, 690, lerp(767, 1167, p), 690, 5, C.fig);
      ln(767, 670, 767, 710, 5, C.fig); if (p >= 1) ln(1167, 670, 1167, 710, 5, C.fig);
      fadeIn(t, tf + 0.3, () => { text('TOO FAR APART', 967, 770, '900 46px M', C.red); }); }
  });
};
S.s31 = (t, seg) => {
  const ti = wt(seg, 'inside'), e = evs('error')[0];
  if (e && t >= e.t) {
    // ERROR 404
    const k = t - e.t;
    ctx.save(); if (k < 0.5) shake(8 * (1 - k / 0.5), t);
    redGlow(40); text('404', 960, 520, '900 330px M', C.red, 'center', 'middle'); noGlow();
    spaced('INSTRUCTION NOT FOUND', 960, 760, '900 54px M', C.fig, 10);
    ctx.restore();
    return;
  }
  stepCard(t, seg, 4, 'IF IT KNOCKS FROM INSIDE');
  if (t >= ti) { const p = knockPulse(t); fadeIn(t, ti, () => { ctx.fillStyle = 'rgba(255,0,0,0.06)'; ctx.fillRect(0, 0, W, H); }); }
};
S.s32 = (t, seg) => {
  const tn = wt(seg, 'nobody');
  if (t < tn - 0.1) {
    cam(t, seg.start, tn - seg.start, 1, 1.05, W / 2, 520, () => {
      glow('rgba(255,255,255,0.25)', 30); rr(660, 170, 600, 700, 10, '#ececec'); noGlow();
      rr(660, 170, 600, 90, 10, '#111'); spaced('STEP 4', 960, 232, '900 44px M', C.fig, 8);
      for (let i = 0; i < 7; i++) { ctx.setLineDash([10, 10]); ln(720, 340 + i * 70, 1200, 340 + i * 70, 3, '#bdbdbd'); ctx.setLineDash([]); }
      if ((t % 1) < 0.55) rr(722, 300, 6, 46, 2, '#000');
    });
    return;
  }
  cam(t, tn, seg.end - tn + 0.6, 1, 1.05, W / 2, 470, () => {
    const p = easeOut((t - tn) / 1.5);
    spaced('SENT', 640, 330, '900 40px M', C.mid, 8); text(String(Math.floor(p * 213)).padStart(3, '0'), 640, 480, '900 150px M', C.fig);
    spaced('RETURNED', 1280, 330, '900 40px M', C.red, 8); redGlow(20); text('000', 1280, 480, '900 150px M', C.red); noGlow();
  });
};
S.s33 = (t, seg) => {
  const td = wt(seg, 'door'), tw = wt(seg, 'this'), kk = evs('knock3').slice(-1)[0];
  if (kk && t >= kk.t - 0.4) {
    // the last knocks: black, the door seen from the bed, knocking on our side
    const p = knockPulse(t), lk = lastKnock(t);
    ctx.save(); if (p > 0.5) shake(6 * p, t);
    doorFront(760, 120, 400, 740, {});
    if (lk >= kk.t) ripple(960, 500, lk, t, C.red, 30, 300, 8);
    knockLines(720, 500, p, C.red, 1); knockLines(1200, 500, p, C.red, -1);
    ctx.restore();
    if (t > kk.t + 1.6) { ctx.fillStyle = `rgba(0,0,0,${prog(t, kk.t + 1.6, 0.25)})`; ctx.fillRect(0, 0, W, H); }
    return;
  }
  if (t < tw - 0.1) {
    cam(t, seg.start, tw - seg.start, 1.0, 1.06, 820, 600, () => {
      room(t, { person: 'sleep', cat: () => lyingCat(700, 690, 0.8, 0) });
      pop(t, seg.start + 0.3, 690, 520, () => { glow(); circS(690, 620, 70, C.fig, 5); noGlow(); });
      pop(t, td - 0.1, 1080, 260, () => { tag('CLOSED', 1080, 270, C.fig, 36, 'center'); });
    });
    return;
  }
  cam(t, tw, 4, 1, 1.05, W / 2, 500, () => {
    pop(t, tw, 960, 470, () => {
      rrS(560, 300, 800, 330, 12, C.mid, 5);
      spaced('INSTRUCTION 001', 960, 410, '900 64px M', C.fig, 8);
      text('STEP 1  ✓    STEP 2  ✓    STEP 3  ✓', 960, 500, '600 34px Plex', C.sec);
      redGlow(12); text('STEP 4  —  404 NOT FOUND', 960, 570, '600 34px Plex', C.red); noGlow();
    });
  });
};

// ---------- HUD, captions, texture ----------
const STEP = {}; ['s05', 's06', 's07', 's08', 's09', 's10'].forEach(s => STEP[s] = 1);
['s11', 's12', 's13', 's14', 's15', 's16', 's17', 's18'].forEach(s => STEP[s] = 2);
['s19', 's20', 's21', 's22', 's23', 's24', 's25', 's26', 's27', 's28', 's29', 's30'].forEach(s => STEP[s] = 3);
['s31', 's32'].forEach(s => STEP[s] = 4);
let grainC = null, vig = null;
function initTex() {
  grainC = [0, 1, 2, 3].map(() => { const g = document.createElement('canvas'); g.width = 480; g.height = 270; const gx = g.getContext('2d');
    const im = gx.createImageData(480, 270); for (let i = 0; i < im.data.length; i += 4) { const v = Math.random() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    gx.putImageData(im, 0, 0); return g; });
}
function hud(t, seg) {
  ctx.save(); ctx.globalAlpha = 0.75;
  text('INSTRUCTION 001', 60, 62, '900 22px M', C.mid, 'left');
  text('// IF YOUR CAT KNOCKS', 290, 62, '600 20px Plex', C.dim, 'left');
  const sec = Math.floor(12 * 60 + 4 + t), mm = Math.floor(sec / 60) % 60, ss = sec % 60;
  text(`03:${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')} AM`, 1860, 62, '600 22px Plex', C.mid, 'right');
  const r = STEP[seg.id] || 0;
  for (let i = 0; i < 4; i++) {
    const x = 960 + (i - 1.5) * 30 - 9, y = 46;
    if (i + 1 < r) rr(x, y, 18, 18, 3, C.mid);
    else if (i + 1 === r) { redGlow(10); rr(x, y, 18, 18, 3, C.red); noGlow(); }
    else rrS(x, y, 18, 18, 3, C.dim, 2);
  }
  ctx.restore();
}
function chunks(seg) {
  if (seg._ch) return seg._ch;
  const out = []; let cur = [];
  seg.words.forEach(w => { cur.push(w); if (/[.?!]$/.test(w.w) || (cur.length >= 7 && /,$/.test(w.w)) || cur.length >= 10) { out.push(cur); cur = []; } });
  if (cur.length) out.push(cur);
  return (seg._ch = out);
}
function caption(t, seg) {
  if (t > seg.end + 0.3) return;
  const ch = chunks(seg); let c = null;
  for (const k of ch) if (t >= k[0].s - 0.08) c = k;
  if (!c) return;
  const s = c.map(w => w.w).join(' ').toUpperCase();
  ctx.font = '800 34px M'; ctx.letterSpacing = '1.5px'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  ctx.lineJoin = 'round'; ctx.lineWidth = 8; ctx.strokeStyle = 'rgba(0,0,0,0.9)'; ctx.strokeText(s, 960, 1000);
  ctx.fillStyle = '#ffffff'; ctx.fillText(s, 960, 1000); ctx.letterSpacing = '0px';
}
// shot boundaries for glitch transitions: every segment start plus the extra cuts inside segments
// shot boundaries for glitch transitions come from timeline.py
const cutTimes = () => window.TL.cuts || window.TL.segments.map(s => s.start);
function glitch(t, f) {
  let cut = -9; for (const c of cutTimes()) if (c <= t) cut = c;
  const dt = t - cut, dur = 0.17; if (dt < 0 || dt > dur || cut < 1) return;
  const k = 1 - dt / dur;
  const tmp = glitch.c || (glitch.c = document.createElement('canvas')); tmp.width = W; tmp.height = H; tmp.getContext('2d').drawImage(cv, 0, 0);
  // RGB split
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.5 * k;
  ctx.drawImage(tmp, 14 * k, 0); ctx.globalAlpha = 0.35 * k; ctx.drawImage(tmp, -10 * k, 2); ctx.restore();
  let seed = f * 9301 + 49297; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  for (let i = 0; i < 10; i++) { const y = rnd() * H, h = 6 + rnd() * 50, dx = (rnd() - 0.5) * 160 * k; ctx.drawImage(tmp, 0, y, W, h, dx, y, W, h); }
  ctx.globalAlpha = 0.4 * k; ctx.fillStyle = '#fff'; for (let i = 0; i < 5; i++) ctx.fillRect(0, rnd() * H, W, 1 + rnd() * 3); ctx.globalAlpha = 1;
}

// analog interference ("지지직"): short random tears, stronger around knocks, meows, the reveal and the error
const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
function disturbance(t) {
  let I = 0;
  const b = Math.floor(t * 3); if (hash(b) < 0.08 && (t * 3 - b) < 0.3) I = 0.45;      // a stray tear every few seconds
  I = Math.max(I, knockPulse(t) * 0.6);
  for (const e of window.TL.events) {
    const d = t - e.t;
    if (e.type === 'meow1' || e.type === 'meow2') { if (d > 0 && d < 3.2) I = Math.max(I, 0.35 + 0.35 * Math.abs(Math.sin(d * 7))); }
    if (e.type === 'boom' && d > 0 && d < 0.4) I = Math.max(I, 0.8 * (1 - d / 0.4));
    if (e.type === 'error' && d > -0.1 && d < 1.6) I = Math.max(I, d < 0.25 ? 0.9 : 0.3);
    if (e.type === 'tapestop' && d > 0 && d < 0.8) I = Math.max(I, 0.7);
  }
  return I;
}
function interfere(t, f, I) {
  if (I <= 0.02) return;
  const tmp = interfere.c || (interfere.c = document.createElement('canvas')); tmp.width = W; tmp.height = H; tmp.getContext('2d').drawImage(cv, 0, 0);
  let seed = f * 7919 + 13; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  ctx.globalAlpha = 0.28 * I;
  ctx.drawImage(tmp, 12 * I + rnd() * 6 * I, 0); ctx.globalAlpha = 0.18 * I; ctx.drawImage(tmp, -9 * I, 1);
  ctx.restore();
  for (let i = 0; i < Math.round(4 + 12 * I); i++) { const y = rnd() * H, h = 3 + rnd() * 40 * I, dx = (rnd() - 0.5) * 140 * I; ctx.drawImage(tmp, 0, y, W, h, dx, y, W, h); }
  ctx.globalAlpha = 0.5 * I; ctx.fillStyle = '#fff'; for (let i = 0; i < 6; i++) ctx.fillRect(0, rnd() * H, W, 1 + rnd() * 2);
  ctx.globalAlpha = 0.1 * I; ctx.drawImage(grainC[f % 4], 0, 0, W, H); ctx.globalAlpha = 1;
}

window.draw = (t) => {
  if (!grainC) initTex();
  const f = Math.round(t * 30);  // texture/glitch seed changes 30x a second even at 60 fps
  const segs = window.TL.segments; let seg = segs[0];
  for (const s of segs) if (s.start <= t + 1e-6) seg = s;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; noGlow(); ctx.setLineDash([]);
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  // slow handheld drift so no frame is ever perfectly still
  ctx.translate(W / 2 + Math.sin(t * 0.53) * 5 + Math.sin(t * 1.7) * 1.2, H / 2 + Math.cos(t * 0.41) * 4);
  ctx.rotate(Math.sin(t * 0.29) * 0.0025); ctx.translate(-W / 2, -H / 2);
  (S[seg.id] || S.s01)(t, seg);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; noGlow();
  glitch(t, f);
  interfere(t, f, disturbance(t));
  hud(t, seg);
  caption(t, seg);
  ctx.globalAlpha = 0.07; ctx.drawImage(grainC[f % 4], 0, 0, W, H); ctx.globalAlpha = 1;
  const by = ((t * 90) % (H + 300)) - 150, bg = ctx.createLinearGradient(0, by - 80, 0, by + 80);
  bg.addColorStop(0, 'rgba(255,255,255,0)'); bg.addColorStop(0.5, 'rgba(255,255,255,0.025)'); bg.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = bg; ctx.fillRect(0, by - 80, W, 160);
  if (!vig) { vig = ctx.createRadialGradient(W / 2, H / 2, H * 0.5, W / 2, H / 2, H * 1.1); vig.addColorStop(0, 'rgba(0,0,0,0)'); vig.addColorStop(1, 'rgba(0,0,0,0.55)'); }
  ctx.fillStyle = vig; ctx.fillRect(0, 0, W, H);
};
})();

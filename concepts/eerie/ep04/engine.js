// Instruction 444, EP04 "If Your Security Camera Ever Records Tomorrow". Canvas renderer: window.draw(t).
// Black background, flat white pictograms, red only for what is wrong. Needs window.TL (timeline.json).
(() => {
const W = 1920, H = 1080;
const NAME = 'INSTRUCTION';   // the channel's name, as it appears on screen ("NAME NUM")
const NUM = '444';
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
// World scale for the room cutaway: floor at y=860, 2.6 px per cm (door 200 cm = 520 px).
const FY = 860, PX = 2.6, DOOR_H = 520, DOOR_X = 1080, KNOCK_Y = FY - DOOR_H * 0.70;   // knocks land on the upper half of the door, at the height a person knocks
// glowing eye: white normally, red when red>0 (the scary moments)
function eyeGlow(x, y, rx, ry, red = 0, slit = 1) {
  ctx.save();
  ell(x, y, rx * 1.28, ry * 1.25, 0, '#000');                       // dark eye socket so a white eye still reads on white fur
  const r = Math.round(lerp(245, 255, red)), g = Math.round(lerp(245, 43, red)), b = Math.round(lerp(240, 43, red));
  ctx.shadowColor = red > 0.05 ? `rgba(255,43,43,${0.5 + 0.5 * red})` : 'rgba(255,255,255,0.7)'; ctx.shadowBlur = 14 + 26 * red;
  ell(x, y, rx, ry, 0, `rgb(${r},${g},${b})`); noGlow();
  if (slit > 0) rr(x - rx * 0.16, y - ry * 0.85 * slit, rx * 0.32, ry * 1.7 * slit, rx * 0.16, '#000');
  ctx.restore();
}
// side-view bed; person: 'woke' (propped up, eye toward the door), 'sleep', 'none'. Origin = bed's left foot on the floor.
// o.cat: 'sleep' | 'sit' | 'empty' draws the cat's place at the foot of the bed
function bed(x, y, s = 1, mode = 'woke', o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  glow('rgba(255,255,255,0.22)', 16);
  rr(0, -330, 30, 330, 10, C.fig); rr(-6, -342, 42, 18, 8, C.fig);              // headboard + cap
  rr(560, -170, 22, 170, 8, C.fig); rr(554, -182, 34, 16, 7, C.fig);            // footboard + cap
  rr(0, -150, 582, 46, 12, C.fig);                                              // frame
  rr(26, -104, 16, 104, 4, C.sec); rr(540, -104, 16, 104, 4, C.sec);
  rr(30, -196, 530, 48, 18, C.sec);                                             // mattress
  noGlow(); for (let i = 1; i < 8; i++) ln(30 + i * 66, -190, 30 + i * 66, -156, 2, 'rgba(0,0,0,0.18)');
  glow('rgba(255,255,255,0.22)', 16); ell(98, -204, 56, 16, 0, C.fig);          // pillow
  if (mode === 'woke') {
    circ(150, -298, 46, C.fig);
    pth('M88,-196 C90,-250 120,-268 160,-268 C220,-268 260,-250 300,-246 C390,-240 470,-232 560,-220 L560,-180 L88,-180 Z', C.fig);
    noGlow(); circ(178 + (o.look || 0) * 6, -304, 9, '#000');
  } else if (mode === 'sleep') {
    circ(112, -238, 44, C.fig);
    pth('M140,-200 C160,-240 240,-252 320,-248 C400,-244 480,-236 560,-222 L560,-180 L140,-180 Z', C.fig);
    noGlow(); pthS('M118,-252 q10,7 20,0', '#000', 4.5);   // closed eye only, no mouth
  } else if (mode === 'flat') {
    // nobody under it: the blanket lies thrown back over the mattress and hangs over the side
    pth('M64,-200 C110,-226 200,-224 280,-216 C380,-226 480,-218 568,-208 L574,-136 C470,-146 300,-142 60,-148 Z', C.fig);
    noGlow(); ctx.save(); ctx.globalAlpha *= 0.3; pthS('M120,-206 q60,-8 110,4 M300,-210 q70,-10 140,2 M200,-170 q80,-8 160,4', '#000', 3); ctx.restore();
  } else {
    pth('M88,-196 C100,-214 300,-214 560,-206 L560,-180 L88,-180 Z', C.fig);
  }
  noGlow();
  // blanket fold lines
  ctx.globalAlpha *= 0.25; pthS('M260,-232 q40,14 80,8 M380,-224 q50,10 110,6', '#000', 3); ctx.globalAlpha /= 0.25;
  if (o.cat === 'sleep') { ctx.save(); ctx.translate(470, -226); curledCat(0, 0, 0.62); ctx.restore(); }
  if (o.cat === 'sit') sitCat(470, -222, 0.62, { collar: true });
  if (o.cat === 'empty' || o.cat === 'warm') {
    if (o.cat === 'warm') { const tt = o.t || 0; ctx.save(); redGlow(10); ctx.globalAlpha *= 0.85;
      for (let i = 0; i < 3; i++) pthS(`M${446 + i * 24},${-240} q-10,-14 0,-28 q10,-14 0,-28 q-10,-14 0,-28`.replace(/-240/, String(-240 - ((tt * 30 + i * 9) % 12))), C.red, 5);
      ctx.restore(); }
  }
  ctx.restore();
}
// curled sleeping cat (top of blanket), origin at its base
function curledCat(x, y, s) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 14);
  ell(0, -34, 70, 36, 0, C.fig); circ(-52, -44, 28, C.fig);
  pth('M-70,-58 L-66,-86 L-50,-64 Z', C.fig); pth('M-46,-66 L-34,-90 L-28,-60 Z', C.fig);
  pthS('M60,-20 C70,6 10,10 -30,-4', C.sec, 12); noGlow();
  pthS('M-64,-44 q7,6 14,0', '#000', 3.5);
  ctx.restore();
}
// bedroom furniture and wall details left of the door (drawn behind the bed)
function bedroomDecor(t, o = {}) {
  if (!o.noWindow) {
  // window with moon (or sun)
  rrS(330, 230, 220, 230, 6, C.mid, 6); ln(440, 236, 440, 454, 4, C.mid); ln(336, 345, 544, 345, 4, C.mid);
  if (o.sun) { ctx.save(); glow('rgba(255,255,255,0.6)', 30); circ(400, 290, 26, C.fig); ctx.restore(); }
  else { ctx.save(); glow('rgba(255,255,255,0.5)', 24); circ(500, 285, 22, C.fig); noGlow(); circ(510, 278, 20, '#000'); ctx.restore(); }
  pth('M316,222 C340,300 330,400 300,470 L316,470 Z', C.dim); pth('M564,222 C540,300 550,400 580,470 L564,470 Z', C.dim);
  rr(300, 216, 280, 10, 3, C.mid);
  }
  // nightstand with a clock
  rr(800, FY - 150, 120, 150, 6, '#262626'); rrS(800, FY - 150, 120, 150, 6, C.mid, 3); ln(810, FY - 95, 910, FY - 95, 3, C.mid); circ(860, FY - 120, 5, C.mid);
  rr(816, FY - 196, 88, 44, 6, '#111'); rrS(816, FY - 196, 88, 44, 6, C.mid, 3);
  ctx.save(); redGlow(10); if (o.sun) text('7:00', 860, FY - 163, '700 26px Plex', C.mid); else text('3:00', 860, FY - 163, '700 26px Plex', C.red); ctx.restore();
  // picture frame
  rrS(640, 300, 90, 110, 4, C.dim, 5); pthS('M652,396 L680,350 L700,376 L716,356 L722,396', C.dim, 3);
  // baseboard
  ln(0, FY - 10, DOOR_X - 30, FY - 10, 3, C.dim);
}
function hallDecor(t, o = {}) {
  const on = o.light ?? 0;
  ln(DOOR_X + 30, FY - 10, W, FY - 10, 3, C.dim);
  // ceiling lamp
  ln(1560, 0, 1560, 120, 3, C.mid); pth('M1520,150 L1600,150 L1584,120 L1536,120 Z', C.mid);
  if (on > 0) { ctx.save(); ctx.globalAlpha *= on; const g = ctx.createRadialGradient(1560, 160, 10, 1560, 400, 520);
    g.addColorStop(0, 'rgba(255,250,235,0.20)'); g.addColorStop(1, 'rgba(255,250,235,0)'); ctx.fillStyle = g; ctx.fillRect(DOOR_X + 30, 0, W, FY);
    glow('rgba(255,250,235,0.9)', 26); ell(1560, 154, 24, 8, 0, '#fffaf0'); ctx.restore(); }
  // picture frame in the hallway
  rrS(1700, 290, 110, 140, 4, C.dim, 5); circ(1755, 345, 18, C.dim); rr(1730, 368, 50, 40, 10, C.dim);
}
// wall with the door seen edge-on; the wall runs to the top of the frame
function doorEdge(x = DOOR_X, y = FY, open = 0) {
  const h = DOOR_H;
  rr(x - 30, 0, 60, y - h - 6, 0, '#222');                          // wall above the door, up to the top of the frame
  ln(x - 30, 0, x - 30, y - h - 6, 2, C.dim); ln(x + 30, 0, x + 30, y - h - 6, 2, C.dim);
  rr(x - 34, y - h - 14, 68, 10, 2, C.mid);                         // head trim
  glow('rgba(255,255,255,0.22)', 14);
  if (open < 0.05) rr(x - 18, y - h, 36, h - 4, 3, C.fig);
  else {   // the door swings into the bedroom, toward the viewer: seen as a widening panel hinged on the bedroom side
    const wd = Math.sin(open * 80 * D2R) * 230, hx = x - 18;
    ctx.beginPath(); ctx.moveTo(hx, y - h); ctx.lineTo(hx - wd, y - h - 10 * open); ctx.lineTo(hx - wd, y + 6 * open); ctx.lineTo(hx, y - 4); ctx.closePath();
    ctx.fillStyle = '#4c4c4c'; ctx.fill(); noGlow(); ctx.strokeStyle = '#9a9a9a'; ctx.lineWidth = 3; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(hx - wd * 0.12, y - h * 0.94); ctx.lineTo(hx - wd * 0.88, y - h * 0.95 - 8 * open); ctx.lineTo(hx - wd * 0.88, y - h * 0.55); ctx.lineTo(hx - wd * 0.12, y - h * 0.55); ctx.closePath(); ctx.strokeStyle = '#9a9a9a'; ctx.lineWidth = 3; ctx.stroke();
    circ(hx - wd * 0.85, y - h * 0.42, 8, '#8a8a8a');
    rr(x - 18, y - h, 36, h - 4, 0, 'rgba(255,250,235,0.18)');   // the open doorway
  }
  noGlow();
  if (open < 0.05) { rr(x - 34, y - h * 0.42 - 6, 18, 12, 4, C.sec); circ(x - 36, y - h * 0.42, 9, C.sec); rr(x + 16, y - h * 0.42 - 6, 18, 12, 4, C.sec); circ(x + 36, y - h * 0.42, 9, C.sec); }
}
// front view door with frame, panels, hinges and a lever handle. o.light: hallway light under the door; o.feet: shadows;
// o.open: 0..1 swing; o.handle: lever rotation 0..1; o.marks: claw marks where it knocked 0..1
function doorFront(x, y, w, h, o = {}) {
  rr(x - 40, y - 40, w + 80, h + 40, 2, '#151515');                 // wall around the door
  ln(x - 300, y + h, x + w + 300, y + h, 4, C.dim);
  rrS(x - 18, y - 18, w + 36, h + 18, 2, C.mid, 8); rrS(x - 8, y - 8, w + 16, h + 8, 2, C.dim, 2);
  if (o.light) { ctx.save(); ctx.globalAlpha *= o.light; glow('rgba(255,250,235,0.95)', 34); rr(x, y + h - 4, w, 10, 0, '#fffaf0'); noGlow();
    const g = ctx.createLinearGradient(0, y + h, 0, y + h + 140); g.addColorStop(0, 'rgba(255,250,235,0.22)'); g.addColorStop(1, 'rgba(255,250,235,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(x, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w + 160, y + h + 140); ctx.lineTo(x - 160, y + h + 140); ctx.fill(); ctx.restore();
    for (const f of (o.feet || [])) { ctx.save(); ctx.globalAlpha *= f.a ?? 1; rr(x + w * f.x - w * 0.06, y + h - 5, w * 0.12, 12, 2, '#000'); ctx.restore(); } }
  const op = o.open || 0;
  if (op > 0) { rr(x, y, w, h - 4, 2, '#0b0b0b'); if (o.inside) o.inside(); }
  ctx.save(); ctx.translate(x, y); ctx.transform(1 - op * 0.75, op * 0.12, 0, 1, 0, 0);
  rr(0, 0, w, h - 4, 3, '#171717');
  for (const [py, ph] of [[0.06, 0.38], [0.52, 0.4]]) {               // raised panels with an inner bevel
    rrS(w * 0.12, h * py, w * 0.76, h * ph, 6, C.mid, 5); rrS(w * 0.12 + 12, h * py + 12, w * 0.76 - 24, h * ph - 24, 4, C.dim, 2);
  }
  rr(-4, h * 0.1, 8, 34, 2, C.mid); rr(-4, h * 0.82, 8, 34, 2, C.mid);   // hinges
  // lever handle
  const hx = w * 0.88, hy = h * 0.58;
  glow(); circ(hx, hy, w * 0.04, C.sec); noGlow();
  ctx.save(); ctx.translate(hx, hy); ctx.rotate(-(o.handle || 0) * 38 * D2R); rr(-w * 0.17, -7, w * 0.17, 14, 7, C.fig); ctx.restore();   // pressed down
  // keyhole (o.keyLight: the lit hallway shows through it)
  { const kc = o.keyLight ? '#ffe7b0' : '#000'; if (o.keyLight) glow('rgba(255,231,176,0.9)', 8 * o.keyLight);
    circ(hx, hy + 27, 4.5, kc); pth(`M${hx - 2.6},${hy + 28} L${hx + 2.6},${hy + 28} L${hx + 4},${hy + 41} L${hx - 4},${hy + 41} Z`, kc); noGlow(); }
  if (o.marks) { ctx.save(); redGlow(8); for (let i = 0; i < 3; i++) lnP(w * 0.36 + i * w * 0.14, h * 0.2, w * 0.38 + i * w * 0.14, h * 0.36, 9, '#b81f1f', clamp(o.marks * 3 - i)); ctx.restore(); }
  ctx.restore();
}
// your cat, sitting, side view facing right; feet at (x,y)
function sitCat(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(o.flip ? -s : s, s);
  glow('rgba(255,255,255,0.3)', 16);
  const puff = o.puff || 0;
  pthS('M-30,-20 C-78,-16 -96,-46 -76,-74', C.sec, 9 + puff * 16);      // tail starts inside the haunch
  ell(-6, -40, 46, 40, 0, C.fig); ell(18, -62, 26, 32, 0.3, C.fig);       // haunch, chest
  ell(-14, -5, 22, 7, 0, C.fig);                                          // hind paw on the floor
  const hx = o.push ? 54 : 40, hy = (o.push ? -80 : -88) + (o.down || 0) * 50;
  const ear = (o.ear || 0) * 14;
  circ(hx, hy, 29, C.fig); ell(hx + 18, hy + 8, 13, 11, 0, C.fig);
  pth(`M${hx - 24},${hy - 12} L${hx - 20 + ear},${hy - 48} L${hx - 2},${hy - 23} Z`, C.fig);
  pth(`M${hx + 2},${hy - 25} L${hx + 20 + ear},${hy - 48} L${hx + 25},${hy - 10} Z`, C.fig);
  // forelegs: straight down from the chest to round paws; when scratching, the near one reaches up the door
  ln(20, -50, 22, -8, 13, C.sec); ell(28, -5, 12, 6, 0, C.sec);
  if (o.paw) { const py = -70 - 12 * Math.sin(o.paw * 22); ln(30, -52, 62, py, 13, C.fig); circ(64, py - 2, 9, C.fig); }
  else { ln(30, -50, 34, -8, 13, C.fig); ell(40, -5, 12, 6, 0, C.fig); }
  noGlow();
  pth(`M${hx - 18},${hy - 16} L${hx - 15 + ear},${hy - 38} L${hx - 7},${hy - 22} Z`, '#cfcfcf');
  if (o.closed) ln(hx + 6, hy - 4, hx + 20, hy - 4, 4, '#000'); else eyeGlow(hx + 13, hy - 5, 5.5, 5.5, o.red || 0, 0.8);
  pth(`M${hx + 29},${hy + 4} l5,0 l-2.5,4 z`, '#555');
  ctx.globalAlpha *= 0.6; for (let i = 0; i < 2; i++) ln(hx + 26, hy + 9 + i * 5, hx + 50, hy + 6 + i * 8, 1.5, C.mid); ctx.globalAlpha /= 0.6;
  ctx.restore();
}
// cat walking on four legs, facing left; feet at (x,y); ph = walk phase
function walkCat(x, y, s, ph = 0, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  const sw = Math.sin(ph) * 12;
  pthS('M58,-62 C100,-70 112,-110 96,-130', C.sec, 9);
  ln(-36, -40, -36 + sw, 0, 11, C.sec); ln(40, -40, 40 - sw, 0, 11, C.sec);
  ell(4, -58, 62, 28, 0, C.fig);
  ln(-30, -44, -30 - sw, 0, 12, C.fig); ln(46, -44, 46 + sw, 0, 12, C.fig);
  circ(-62, -78, 26, C.fig); pth('M-82,-92 L-80,-122 L-64,-98 Z', C.fig); pth('M-60,-100 L-46,-124 L-40,-92 Z', C.fig);
  noGlow(); eyeGlow(-74, -82, 5, 5, o.red || 0, 0.8);
  ctx.restore();
}
// YOUR cat, standing upright at human height, drawn in the first version's flat geometric shapes. Feet at (x,y), faces left toward the door.
// o.k: knocking arm 0 (paw on the door) .. 1 (pulled back); o.red: red eye 0..1; o.tilt: head tilt; o.ears: flatten 0..1; o.sway: lean
const GEO = 'A';
const CAT_S = GEO === 'A' ? 1.12 : 1, CAT_X = 1112 + 128 * CAT_S;
// where the standing cat's eye sits in the hallway (for shots that show only the eye in the dark)
const CAT_EYE = GEO === 'A' ? { x: CAT_X - 40 * CAT_S, y: FY - 360 * CAT_S } : { x: CAT_X - 30 * CAT_S, y: FY - 420 * CAT_S };
function geoEye(x, y, red) {
  if (red > 0) redGlow(24 * red);
  ell(x, y, 10, 9, 0, red > 0.5 ? C.red : '#ffffff'); noGlow();
  if (red <= 0.5) { ctx.beginPath(); ctx.ellipse(x, y, 11, 10, 0, 0, Math.PI * 2); ctx.strokeStyle = '#777'; ctx.lineWidth = 2; ctx.stroke(); }
  rr(x - 2, y - 8, 4, 16, 2, '#000');
}
function geoHead(cx, cy, r, col, o) {
  const ea = (o.ears || 0);
  ctx.save(); ctx.translate(cx, cy); ctx.rotate((o.tilt || 0) * D2R); ctx.translate(-cx, -cy);
  ctx.save(); ctx.translate(cx - 6 + 10 * ea, cy - 40 + 4 * ea); ctx.rotate(ea * 1.05); ctx.scale(1, 1 - 0.45 * ea); pth('M-21,6 L-15,-58 L21,-4 Z', col); ctx.restore();
  ctx.save(); ctx.translate(cx + 26, cy - 36 + 10 * ea); ctx.rotate(ea * 0.95); ctx.scale(1, 1 - 0.45 * ea); pth('M-20,-6 L18,-52 L20,12 Z', col); ctx.restore();
  circ(cx, cy, r, col); ell(cx - 38, cy + 14, 14, 12, 0, col);
  noGlow(); pth(`M${cx - 52},${cy + 8} l8,0 l-4,6 z`, '#000');
  geoEye(cx - 24, cy - 12, o.red || 0);
  ctx.restore();
}
// a dark halo (o.halo) keeps the white cat readable against the white bed
const catGlow = o => o.halo ? glow('rgba(0,0,0,0.95)', 18) : glow('rgba(255,255,255,0.3)', 24);
function standCat(x, y, s = 1, o = {}) {
  const k = o.k ?? 1, col = o.col || '#eeeeee', col2 = o.col2 || '#a9a9a9', fl = Math.sin((o.t || 0) * 1.7) * 8;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate((o.sway || 0) * D2R); catGlow(o);
  let px = lerp(-128, -96, k), py = lerp(KNOCK_Y - FY, KNOCK_Y - FY - 18, k) / s;
  if (o.arm === 'down') { px = GEO === 'A' ? -34 : -50; py = GEO === 'A' ? -166 : -176; }
  if (GEO === 'A') {
    // the first design: a tilted egg body on thin straight legs
    pthS(`M48,-122 C112,-126 ${130 + fl},-194 ${104 + fl},-246`, col2, 18);
    ln(28, -126, 46, -6, 24, col2); ell(58, 0, 26, 9, 0, col2);
    ln(-4, -262, -16, -162, 22, col2);
    ln(0, -126, -8, -6, 26, col); ell(-22, 0, 28, 10, 0, col);
    // o.lean bends the upper body forward from the hips (leaning over the bed)
    ctx.save(); ctx.translate(0, -126); ctx.rotate((o.lean || 0) * D2R); ctx.translate(0, 126);
    ctx.save(); ctx.translate(4, -212); ctx.rotate(-6 * D2R); ell(0, 0, 54, 112, 0, col); ctx.restore();
    catGlow(o); if (o.arm !== 'none') { if (o.arm === 'down') poly([[-28, -278], [-40, -220], [px, py]], 24, col); else ln(-28, -278, px, py, 26, col); circ(px, py, 17, col); }
    geoHead(-16, -348, 50, col, o);
    ctx.restore();
  } else {
    // the same flat shapes built like a person: square shoulders, a neck, long straight legs, elbows
    pthS(`M30,-196 C96,-200 ${110 + fl},-260 ${92 + fl},-306`, col2, 14);
    ln(16, -200, 22, -6, 22, col2); ell(34, 0, 24, 8, 0, col2);
    poly([[30, -342], [44, -250], [38, -160]], 18, col2); circ(38, -152, 13, col2);
    pth('M-46,-346 L42,-350 L30,-236 L34,-196 L-30,-196 L-26,-236 Z', col);
    ln(-12, -200, -16, -6, 24, col); ell(-30, 0, 26, 9, 0, col);
    rr(-16, -372, 26, 30, 4, col);
    catGlow(o); poly([[-40, -336], [-86, -300], [px, py]], 22, col); circ(px, py, 16, col);
    geoHead(-6, -408, 46, col, o);
  }
  noGlow(); ctx.restore();
}
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
// thr 0..1 brings the left hand up to the throat
// o.eye: draw the eye (faces right); o.hand: {x,y} in world coords for the right hand (knocking, holding the handle)
function person(x, y, s = 1, col = C.fig, arm = 0, thr = 0, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.25)', 14);
  circ(0, -330, 30, col); rr(-26, -290, 52, 140, 20, col);
  ln(-12, -160, -14, -8, 22, col); ln(12, -160, 14, -8, 22, col);
  if (thr > 0) { poly([[-24, -270], [lerp(-34, -44, thr), lerp(-170, -250, thr)], [lerp(-34, -8, thr), lerp(-170, -292, thr)]], 18, col); }
  else ln(-24, -270, -34, -170, 18, col);
  if (o.hand) { const hx = (o.hand.x - x) / s, hy = (o.hand.y - y) / s, ex = lerp(24, hx, 0.45) + 6, ey = lerp(-270, hy, 0.45) + 22;
    poly([[22, -270], [ex, ey], [hx, hy]], 18, col); circ(hx, hy, 11, col); }
  else ln(24, -270, lerp(34, 70, arm), lerp(-170, -300, arm), 18, col);
  noGlow(); if (o.eye) circ(14, -336, 5.5, '#000');
  ctx.restore();
}
// speech bubble whose tail points at (tx, ty)
function bubbleTo(x, y, w, h, s, t, t0, tx, ty, col = C.fig, txtCol = '#000') {
  pop(t, t0, x, y, () => { glow(); rr(x - w / 2, y - h / 2, w, h, 26, col);
    const bx = clamp(tx, x - w / 2 + 50, x + w / 2 - 50), by = ty > y ? y + h / 2 - 4 : y - h / 2 + 4;
    pth(`M${bx - 22},${by} L${tx},${ty} L${bx + 22},${by} Z`, col); noGlow();
    text(s, x, y + 2, `900 ${Math.round(h * 0.42)}px M`, txtCol, 'center', 'middle'); });
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
  ctx.save(); ctx.globalAlpha *= 0.82; rr(x0, y - size * 0.95, w, size * 1.5, 6, '#0b0b0b'); ctx.restore();   // dark fill so a frame edge behind the label never runs through it
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

// ---------- rule card, emergency card ----------
function ruleCard(t, seg, n, line) {
  const t0 = seg.start;
  cam(t, t0, seg.end - t0 + 0.6, 1, 1.05, W / 2, H / 2, () => {
    slideIn(t, t0, -60, 0, () => {
      glow('rgba(255,255,255,0.3)', 30); rr(560, 300, 230, 230, 14, C.fig); noGlow();
      text(String(n), 675, 418, '900 170px M', '#000', 'center', 'middle');
    });
    slideIn(t, t0 + 0.08, 60, 0, () => { spaced('RULE', 830, 360, '900 40px M', C.mid, 14, 'left'); });
    const ws = line.split(' '), tw = seg.words.slice(2); let shown = 0;
    for (let i = 0; i < ws.length; i++) if (t >= (tw[i] ? tw[i].s - 0.05 : seg.end)) shown = i + 1;
    const wrap = list => { const out = []; let cur = '';
      for (const w of list) { if ((cur + ' ' + w).trim().length > 16) { out.push(cur); cur = w; } else cur = (cur + ' ' + w).trim(); }
      if (cur) out.push(cur); return out; };
    const lines = wrap(ws.slice(0, shown)), dy = Math.max(0, wrap(ws).length - 2) * 74;   // a third line pushes the underline and the pips down
    lines.forEach((l, i) => text(l, 830, 446 + i * 74, '900 68px M', C.fig, 'left'));
    lnP(560, 580 + dy, 1360, 580 + dy, 5, C.fig, easeOut(prog(t, t0 + 0.3, 0.6)));
    for (let i = 0; i < 4; i++) { const x = 560 + i * 54, y = 618 + dy; ctx.save(); ctx.globalAlpha *= prog(t, t0 + 0.4 + i * 0.06, 0.2);
      if (i + 1 <= n) rr(x, y, 38, 38, 5, i + 1 === n ? C.fig : C.mid); else rrS(x, y, 38, 38, 5, i === 3 ? C.red : C.mid, 3); ctx.restore(); }
  });
}
function hazard(x, y, w, h, off = 0) {
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  rr(x, y, w, h, 0, C.fig); off = ((off % 56) + 56) % 56; for (let i = -h - 56; i < w + h; i += 56) { ctx.beginPath(); ctx.moveTo(x + i + off, y); ctx.lineTo(x + i + 28 + off, y); ctx.lineTo(x + i + 28 - h + off, y + h); ctx.lineTo(x + i - h + off, y + h); ctx.fillStyle = '#000'; ctx.fill(); }
  ctx.restore();
}
function emergencyCard(t, seg) {
  const t0 = seg.start, te = wt(seg, 'emergency'), th = wt(seg, 'how');
  cam(t, t0, seg.end - t0 + 0.8, 1, 1.05, W / 2, H / 2, () => {
    const p = easeOut(prog(t, t0, 0.5));
    hazard(0, 170, W * p, 34, t * 40); hazard(W * (1 - p), 800, W * p, 34, -t * 40);
    slideIn(t, t0, -60, 0, () => { redGlow(30 + 14 * Math.sin(t * 7)); rr(380, 330, 230, 230, 14, C.red); noGlow(); text('4', 495, 448, '900 170px M', '#000', 'center', 'middle'); });
    slideIn(t, t0 + 0.08, 60, 0, () => { spaced('RULE', 650, 390, '900 40px M', C.mid, 14, 'left'); });
    if (t >= te - 0.05) pop(t, te - 0.05, 1060, 470, () => { redGlow(22); spaced('EMERGENCY PROTOCOL', 650, 490, '900 80px M', C.red, 6, 'left'); noGlow(); });
    if (t >= th - 0.05) pop(t, th - 0.05, 1000, 610, () => { spaced('HOW TO FIGHT BACK', 650, 630, '900 64px M', C.fig, 8, 'left'); });
    for (let i = 0; i < 4; i++) { const x = 380 + i * 54, y = 700; ctx.save(); ctx.globalAlpha *= prog(t, t0 + 0.4 + i * 0.06, 0.2);
      rr(x, y, 38, 38, 5, i === 3 ? C.red : C.mid); ctx.restore(); }
  });
  if (t >= te) { ctx.save(); ctx.globalAlpha = 0.1 * (0.5 + 0.5 * Math.sin((t - te) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
}
// ---------- scenes ----------
const S = {};
const P = { x: 510, y: 110, w: 900, h: 800 };
// left-aligned text shrunk to fit a width
function fitText(str, x, y, maxW, size, col) { ctx.font = `900 ${size}px M`; const w = ctx.measureText(str).width; if (w > maxW) size = Math.floor(size * maxW / w); text(str, x, y, `900 ${size}px M`, col, 'left'); }
const ROWY = i => P.y + 150 + i * 158;
// rubber stamp: double red border, worn ink, slams down from above
function stampMark(t, t0, x, y, lines, rot = -0.12, paper = '#e6e6e6', wear = 70) {
  if (t < t0) return;
  const k = clamp((t - t0) / 0.13), s = lerp(1.8, 1, easeOut(k));
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); ctx.globalAlpha *= clamp(k * 4);
  let w = 0, h = 0; for (const [str, sz] of lines) { ctx.font = `900 ${sz}px M`; ctx.letterSpacing = sz * 0.08 + 'px'; w = Math.max(w, ctx.measureText(str).width); h += sz * 1.05; }
  w += 70; h += 46;
  rrS(-w / 2, -h / 2, w, h, 10, C.red, 9); rrS(-w / 2 + 14, -h / 2 + 14, w - 28, h - 28, 6, C.red, 3);
  let yy = -h / 2 + 22; for (const [str, sz] of lines) { yy += sz * 1.0; ctx.font = `900 ${sz}px M`; ctx.letterSpacing = sz * 0.08 + 'px'; text(str, 0, yy - sz * 0.08, `900 ${sz}px M`, C.red); }
  ctx.letterSpacing = '0px';
  // worn ink: paper-coloured specks knocked out of the stamp
  for (let i = 0; i < wear; i++) { const px = (hash(i * 3.1) - 0.5) * w, py = (hash(i * 7.7) - 0.5) * h; circ(px, py, 1.5 + hash(i) * 3, paper); }
  ctx.restore();
}
function paperclip(x, y, s = 1, col = C.mid) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  pthS('M0,0 L0,-90 C0,-112 30,-112 30,-90 L30,10 C30,30 10,30 10,10 L10,-70', col, 7); ctx.restore();
}
function fileCover(t, o = {}) {
  const pc = '#e6e6e6';
  glow('rgba(255,255,255,0.18)', 30);
  rr(P.x + 40, P.y - 46, 240, 70, 12, '#cfcfcf'); rr(P.x, P.y, P.w, P.h, 12, pc); noGlow();
  text('FILE ' + NUM, P.x + 160, P.y - 6, '900 28px M', '#333');
  rr(P.x, P.y + 40, P.w, 130, 0, '#111');
  spaced(NAME, P.x + P.w / 2, P.y + 128, '900 62px M', C.fig, 14);
  const rows = [['SUBJECT', null], ['LOCATION', 'YOUR LIVING ROOM'], ['TIME', '03:00 AM']];
  rows.forEach(([l, v], i) => { const y = P.y + 270 + i * 82;
    text(l, P.x + 60, y, '600 28px Plex', '#666', 'left'); ln(P.x + 250, y + 12, P.x + P.w - 60, y + 12, 2, '#bbb');
    if (v === null) rr(P.x + 260, y - 30, 330, 40, 3, '#111');
    else { ctx.save(); ctx.filter = 'blur(9px)'; text(v, P.x + 262, y, '900 36px M', i === 2 ? '#d61f1f' : '#111', 'left'); ctx.restore(); } });   // classified: blurred
  // barcode and a hazard edge
  for (let i = 0; i < 40; i++) { const bw = hash(i * 1.7) < 0.35 ? 6 : 3; rr(P.x + P.w - 300 + i * 6.4, P.y + P.h - 170, bw, 70, 0, '#111'); }
  text('NO. 0' + NUM, P.x + P.w - 172, P.y + P.h - 74, '600 24px Plex', '#444');
  text('DO NOT REMOVE FROM THE LIVING ROOM', P.x + 60, P.y + P.h - 130, '600 22px Plex', '#666', 'left');
  ctx.save(); ctx.beginPath(); ctx.roundRect(P.x, P.y, P.w, P.h, 12); ctx.clip(); hazard(P.x, P.y + P.h - 42, P.w, 42, t * 30); ctx.restore();
  paperclip(P.x + P.w - 90, P.y + 30, 1.1, '#8a8a8a');
}
// small dark pictograms drawn on the white page
function pageIcon(name, x, y, col = '#111') {
  ctx.save(); ctx.translate(x, y);
  if (name === 'door') { rrS(-30, -50, 60, 100, 4, col, 6); circ(18, 4, 5, col); rrS(-20, -40, 40, 34, 3, col, 3); }
  if (name === 'gap') { rrS(-30, -50, 60, 92, 4, col, 6); ln(-46, 50, 46, 50, 4, col);
    ctx.save(); glow('rgba(255,200,120,0.9)', 14); rr(-28, 42, 56, 7, 2, '#ffd27a'); ctx.restore(); rr(-14, 42, 8, 7, 1, col); rr(6, 42, 8, 7, 1, col); }
  if (name === 'eye') { ctx.beginPath(); ctx.moveTo(-46, 0); ctx.quadraticCurveTo(0, -46, 46, 0); ctx.quadraticCurveTo(0, 46, -46, 0); ctx.lineWidth = 6; ctx.strokeStyle = col; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-46, 0); ctx.quadraticCurveTo(0, 30, 46, 0); ctx.lineWidth = 6; ctx.stroke(); for (let i = -1; i <= 1; i++) ln(i * 16, 15, i * 20, 28, 4, col); }
  if (name === 'chat') { rrS(-44, -40, 88, 64, 14, col, 6); pth('M-24,22 L-34,46 L-4,24 Z', col); for (let i = -1; i <= 1; i++) circ(i * 20, -8, 6, col); }
  if (name === 'corner') { ln(-40, -44, 44, -44, 7, col); ln(-40, -44, -40, 44, 7, col); circ(-12, -16, 13, col); circ(-12, -16, 5, '#ececec'); ctx.setLineDash([6, 7]); ln(0, -4, 34, 34, 4, col); ctx.setLineDash([]); }
  if (name === 'photo') { rrS(-46, -40, 92, 80, 8, col, 6); circ(-10, 2, 14, col); rr(4, -6, 32, 22, 8, col); circ(26, -24, 6, col); }
  if (name === 'warn') { const tri = () => { ctx.beginPath(); ctx.moveTo(0, -50); ctx.lineTo(50, 40); ctx.lineTo(-50, 40); ctx.closePath(); };
    ctx.lineJoin = 'round'; tri(); ctx.fillStyle = C.red; ctx.fill(); if (col === '#fff') { ctx.lineWidth = 6; ctx.strokeStyle = '#fff'; ctx.stroke(); }
    rr(-6, -22, 12, 38, 5, '#fff'); circ(0, 28, 7, '#fff'); }
  if (name === 'fist') { rr(-34, -34, 68, 64, 18, col); for (let i = 1; i < 4; i++) ln(-34 + i * 17, -34, -34 + i * 17, -10, 3, '#ff2b2b'); }
  ctx.restore();
}
const RULES = [['play', 'DO NOT WATCH IT TO THE END', '', ['DO NOT WATCH IT', 'TO THE END']], ['hoodie', 'DO NOT WEAR WHAT YOU WEAR IN IT', '', ['DO NOT WEAR WHAT', 'YOU WEAR IN IT']], ['clock', 'DO NOT BE HOME AT 3 AM', '', ['DO NOT BE HOME', 'AT 3 AM']], ['warn', 'EMERGENCY PROTOCOL', 'HOW TO FIGHT BACK']];
// the index page. o.rowT[i]: when row i slides in; o.fillT[i]: when its content is written; o.hot: rule 4 armed 0..1; o.struck[i]; o.dim
function rulePage(t, o) {
  const pc = '#ececec';
  glow('rgba(255,255,255,0.2)', 30); rr(P.x, P.y, P.w, P.h, 8, pc); noGlow();
  for (let i = 0; i < 3; i++) circ(P.x + 26, P.y + 220 + i * 230, 10, '#0b0b0b');
  text(NAME + ' ' + NUM, P.x + 60, P.y + 72, '900 42px M', '#111', 'left');
  ln(P.x + 60, P.y + 102, P.x + P.w - 50, P.y + 102, 5, '#111');
  for (let i = 0; i < 4; i++) {
    const t0 = o.rowT[i]; if (t < t0) continue;
    const y = ROWY(i), four = i === 3, k = easeOut((t - t0) / 0.35);
    ctx.save(); ctx.globalAlpha *= clamp(k * 2) * (o.dim && !four ? lerp(1, 0.32, o.dim) : 1); ctx.translate(40 * (1 - k), 0);
    const hot = four ? (o.hot || 0) : 0;
    if (hot > 0) { ctx.save(); ctx.globalAlpha *= hot; redGlow(30 + 20 * Math.sin(t * 8)); rr(P.x + 40, y - 8, P.w - 80, 146, 10, '#e02424'); noGlow();
      ctx.beginPath(); ctx.rect(P.x + 40, y - 8, P.w - 80, 146); ctx.clip(); hazard(P.x + 40, y - 8, P.w - 80, 14, t * 50); hazard(P.x + 40, y + 124, P.w - 80, 14, -t * 50); ctx.restore(); }
    rr(P.x + 60, y + 18, 96, 96, 10, four ? (hot > 0.5 ? '#111' : C.red) : '#111');
    text(String(i + 1), P.x + 108, y + 92, '900 70px M', four && hot > 0.5 ? C.red : (four ? '#111' : '#fff'));
    const fill = o.fillT[i] ?? 1e9, fk = clamp((t - fill) / 0.3), ink = hot > 0.5 ? '#fff' : (four ? '#d61f1f' : '#111');
    if (t < fill) { for (let j = 0; j < 2; j++) rr(P.x + 200, y + 40 + j * 40, j ? 260 : 400, 20, 4, four ? '#111' : '#cfcfcf'); }   // redacted / blank until it is read out
    else { ctx.save(); ctx.globalAlpha *= fk; pageIcon(RULES[i][0], P.x + 240, y + 66, ink);
      if (four) fitText(RULES[i][1], P.x + 310, y + 62, P.w - 370, 50, ink);
      else {   // the three "do not" rules: one size, the long ones on two lines
        const ls = RULES[i][3] || [RULES[i][1]];
        ls.forEach((l, j) => text(l, P.x + 310, y + 82 + (j - (ls.length - 1) / 2) * 46, '900 42px M', ink, 'left')); }
      if (RULES[i][2]) text(RULES[i][2], P.x + 310, y + 110, '900 32px M', hot > 0.5 ? '#111' : '#444', 'left'); ctx.restore(); }
    if (o.struck && o.struck[i] != null && t >= o.struck[i]) { ctx.save(); redGlow(12); lnP(P.x + 50, y + 74, P.x + P.w - 50, y + 58, 10, C.red, easeOut((t - o.struck[i]) / 0.18)); ctx.restore(); }
    ctx.restore();
  }
}
S.o1 = (t, seg) => {
  // the file slides up, and the stamp slams onto it
  const ts = wt(seg, 'four'), k = easeOut((t - seg.start + 0.15) / 0.6);
  const hit = t - ts;
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); ctx.rotate((1 - k) * 0.05); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t);
    stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1);
    ctx.restore();
  });
};
S.o2 = (t, seg) => {
  const tf = wt(seg, 'four'), te = wt(seg, 'exactly'), to = wt(seg, 'otherwise'), ta = wt(seg, 'emergency');
  // the cover swings open on its left edge and the rule page underneath is revealed
  const op = ease((t - seg.start) / 0.6);
  const rows = [tf, tf + 0.16, tf + 0.32, tf + 0.48];
  // "otherwise": push in on rule 4 and arm it
  const zk = ease((t - to) / 0.9), z = lerp(1.0, 1.32, zk), fy = lerp(520, ROWY(3) + 66, zk), hot = prog(t, ta - 0.05, 0.3);
  ctx.save(); ctx.translate(W / 2, 520); ctx.scale(z, z); ctx.translate(-960, -fy);
  cam(t, seg.start, to - seg.start, 1.0, 1.03, W / 2, 520, () => {
    rulePage(t, { rowT: rows, fillT: rows.map(r => r + 0.12), hot });
    if (t >= te) stampMark(t, te, P.x + P.w - 200, P.y + 56, [['FOLLOW THE RULES', 24]], -0.06, '#ececec');
    if (op < 1) { ctx.save(); ctx.translate(P.x, 0); ctx.scale(Math.cos(op * Math.PI / 2), 1); ctx.translate(-P.x, 0); fileCover(t);
      stampMark(t, -9, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore(); }
  });
  ctx.restore();
  if (hot > 0) { ctx.save(); ctx.globalAlpha = 0.14 * hot * (0.5 + 0.5 * Math.sin((t - ta) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
};
// the camera rides down the page to whichever rule is being read
function pageCam(t, seg, rows, fn, z = 1.24) {
  let row = rows[0][1], prev = rows[0][1], tc = seg.start;
  for (const [t0, r] of rows) if (t >= t0) { prev = row; row = r; tc = t0; }
  const k = ease((t - tc) / 0.5), y = lerp(ROWY(prev) + 66, ROWY(row) + 66, k);
  ctx.save(); ctx.translate(W / 2, 520); ctx.scale(z, z); ctx.translate(-960, -y); fn(); ctx.restore();
}// ---------- EP04: the living room in 3D, the security camera in its corner, and the thing under the sofa ----------
// World in metres. x: right as you face the back wall, y: up, z: out of the back wall into the room. Back wall z = 0 (sofa, front door), left wall x = x0 (window).
const ROOM = { x0: -2.4, x1: 2.4, y1: 2.5, z1: 4.2 };
const SOFA = { x0: -1.55, x1: 0.75, z0: 0.06, z1: 0.98, gap: 0.13, seat: 0.46, back: 0.92, arm: 0.64 };
const FDOOR = { x0: 1.25, x1: 2.1, h: 2.1 };                    // the front door, in the back wall
const WIN = { z0: 1.1, z1: 2.7, y0: 0.95, y1: 2.05 };            // the window, in the left wall
const LAMP = { x: 0.98, z: 0.3 };
const CHAIR = { x: -1.95, z: 3.35 };
const SPOT = { x: -0.65, z: 2.0 };                               // where you stand in the clip, on the rug in front of the sofa
const UI = 'I';
// the security camera: high in the front right corner, looking down across the room at the sofa
const CCTV = { x: 2.22, y: 2.36, z: 4.02 };
const CAMS = {
  cctv: { x: CCTV.x, y: CCTV.y, z: CCTV.z, yaw: 0.72, pitch: -0.47, f: 930 },
  sofa: { x: CCTV.x, y: CCTV.y, z: CCTV.z, yaw: 0.52, pitch: -0.5, f: 980 },          // turned to point straight at the sofa (rule 4)
  side: { x: 2.0, y: 1.25, z: 3.4, yaw: 0.62, pitch: -0.12, f: 900 },                 // a person's height, across the room
  chair: { x: 0.4, y: 1.3, z: 2.5, yaw: 1.95, pitch: -0.24, f: 1050 },                // across the room at the chair by the window
  low: { x: 1.1, y: 0.32, z: 3.0, yaw: 0.35, pitch: -0.02, f: 1100 },                 // down on the floor, looking under the sofa
};
let CAM = null;
function setCam(c) { CAM = { ...c, cyw: Math.cos(c.yaw || 0), syw: Math.sin(c.yaw || 0), cp: Math.cos(c.pitch || 0), sp: Math.sin(c.pitch || 0) }; }
const lerpCam = (a, b, k) => { const o = {}; for (const key of ['x', 'y', 'z', 'yaw', 'pitch', 'f']) o[key] = lerp(a[key], b[key], k); return o; };
setCam(CAMS.cctv);
const V3 = { add: (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], sub: (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], mul: (a, k) => [a[0] * k, a[1] * k, a[2] * k],
  dot: (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2], len: a => Math.hypot(a[0], a[1], a[2]), lerp: (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)] };
V3.norm = a => V3.mul(a, 1 / (V3.len(a) || 1));
// camera space: right, up, depth (forward is -z at yaw 0; positive yaw turns left, positive pitch looks up)
function toCam(p) {
  const dx = p[0] - CAM.x, dy = p[1] - CAM.y, dz = p[2] - CAM.z;
  const xc = dx * CAM.cyw - dz * CAM.syw, f0 = -dx * CAM.syw - dz * CAM.cyw;
  return [xc, dy * CAM.cp - f0 * CAM.sp, f0 * CAM.cp + dy * CAM.sp];
}
const camToScr = c => { const s = CAM.f / c[2]; return [W / 2 + c[0] * s, H / 2 - c[1] * s, c[2], s]; };
function prj(p) { const c = toCam(p); return c[2] < 0.03 ? null : camToScr(c); }
const camPos = () => [CAM.x, CAM.y, CAM.z];
function polyW(pts, fill, stroke, lw = 2) {
  let cs = pts.map(toCam); const N = 0.05, out = [];
  for (let i = 0; i < cs.length; i++) { const a = cs[i], b = cs[(i + 1) % cs.length];
    if (a[2] >= N) out.push(a);
    if ((a[2] >= N) !== (b[2] >= N)) { const k = (N - a[2]) / (b[2] - a[2]); out.push([lerp(a[0], b[0], k), lerp(a[1], b[1], k), N]); } }
  if (out.length < 3) return null;
  const sp = out.map(camToScr); ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.stroke(); }
  return sp;
}
function lnW(a, b, w, col) { const ca = toCam(a), cb = toCam(b); const N = 0.05; if (ca[2] < N && cb[2] < N) return;
  let A = ca, B = cb; if (A[2] < N) { const k = (N - A[2]) / (B[2] - A[2]); A = [lerp(A[0], B[0], k), lerp(A[1], B[1], k), N]; }
  if (B[2] < N) { const k = (N - B[2]) / (A[2] - B[2]); B = [lerp(B[0], A[0], k), lerp(B[1], A[1], k), N]; }
  const p = camToScr(A), q = camToScr(B); ln(p[0], p[1], q[0], q[1], w, col); }
function ringPts(c, u, v, n = 28) { const out = []; for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; out.push(V3.add(c, V3.add(V3.mul(u, Math.cos(a)), V3.mul(v, Math.sin(a))))); } return out; }
// a box: only the faces turned toward the camera, far ones first. cols: { top, side, front, edge }
function box3(x0, x1, y0, y1, z0, z1, cols) {
  const c = camPos(), F = [];
  F.push({ n: [0, 1, 0], ctr: [(x0 + x1) / 2, y1, (z0 + z1) / 2], p: [[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], col: cols.top });
  F.push({ n: [0, 0, 1], ctr: [(x0 + x1) / 2, (y0 + y1) / 2, z1], p: [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], col: cols.front });
  F.push({ n: [0, 0, -1], ctr: [(x0 + x1) / 2, (y0 + y1) / 2, z0], p: [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]], col: cols.front });
  F.push({ n: [1, 0, 0], ctr: [x1, (y0 + y1) / 2, (z0 + z1) / 2], p: [[x1, y0, z0], [x1, y0, z1], [x1, y1, z1], [x1, y1, z0]], col: cols.side });
  F.push({ n: [-1, 0, 0], ctr: [x0, (y0 + y1) / 2, (z0 + z1) / 2], p: [[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]], col: cols.side });
  F.push({ n: [0, -1, 0], ctr: [(x0 + x1) / 2, y0, (z0 + z1) / 2], p: [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], col: cols.side });
  const vis = F.filter(f => V3.dot(f.n, V3.sub(c, f.ctr)) > 0).sort((a, b) => V3.len(V3.sub(c, b.ctr)) - V3.len(V3.sub(c, a.ctr)));
  for (const f of vis) polyW(f.p, f.col, cols.edge || '#4a4a4e', 2);
}

// ---------- the room ----------
const WALL_C = '#141416', SIDE_C = '#101012', FLOOR_C = '#19191a', EDGE_C = '#2e2e31';
// o.night 0..1 (the window), o.sun 0..1 (sunrise through the window), o.lamp 0..1 (the floor lamp is on), o.doorOpen 0..1
function room4(t, o = {}) {
  const { x0, x1, y1, z1 } = ROOM, sun = o.sun || 0;
  polyW([[x0, 0, 0], [x1, 0, 0], [x1, 0, z1], [x0, 0, z1]], FLOOR_C, EDGE_C, 2);
  for (let z = 0.5; z < z1; z += 0.5) lnW([x0, 0, z], [x1, 0, z], 1.5, '#222224');
  polyW([[x0, 0, 0], [x1, 0, 0], [x1, y1, 0], [x0, y1, 0]], WALL_C, EDGE_C, 2);
  polyW([[x0, 0, 0], [x0, 0, z1], [x0, y1, z1], [x0, y1, 0]], SIDE_C, EDGE_C, 2);
  polyW([[x1, 0, 0], [x1, 0, z1], [x1, y1, z1], [x1, y1, 0]], SIDE_C, EDGE_C, 2);
  polyW([[x0, y1, 0], [x1, y1, 0], [x1, y1, z1], [x0, y1, z1]], '#0a0a0b', EDGE_C, 2);
  for (const z of [0, z1]) lnW([x0, 0.1, z], [x1, 0.1, z], 2, '#2a2a2d');   // skirting
  // the window in the left wall: night blue, or the sunrise
  const wp = [[x0 + 0.005, WIN.y0, WIN.z0], [x0 + 0.005, WIN.y0, WIN.z1], [x0 + 0.005, WIN.y1, WIN.z1], [x0 + 0.005, WIN.y1, WIN.z0]];
  polyW(wp, sun > 0 ? `rgb(${Math.round(lerp(22, 255, sun))},${Math.round(lerp(26, 196, sun))},${Math.round(lerp(40, 140, sun))})` : '#16202c', '#5a5a60', 4);
  lnW([x0 + 0.01, WIN.y0, (WIN.z0 + WIN.z1) / 2], [x0 + 0.01, WIN.y1, (WIN.z0 + WIN.z1) / 2], 4, '#5a5a60');
  lnW([x0 + 0.01, (WIN.y0 + WIN.y1) / 2, WIN.z0], [x0 + 0.01, (WIN.y0 + WIN.y1) / 2, WIN.z1], 4, '#5a5a60');
  if (sun > 0) { ctx.save(); ctx.globalAlpha *= 0.5 * sun; ctx.globalCompositeOperation = 'screen';   // the light falling across the floor
    polyW([[x0, 0.002, WIN.z0], [x0, 0.002, WIN.z1], [x0 + 2.6, 0.002, WIN.z1 + 0.9], [x0 + 2.6, 0.002, WIN.z0 + 0.6]], '#ffc98a', null); ctx.restore(); }
  else if ((o.moon ?? 1) > 0) { const m = prj([x0 + 0.01, 1.78, WIN.z0 + 0.35]); if (m) { ctx.save(); glow('rgba(200,215,255,0.6)', 18); circ(m[0], m[1], 0.07 * m[3], '#c8d4e6'); ctx.restore(); } }
  // the front door in the back wall
  const op = o.doorOpen || 0, dz = 0.005;
  if (op > 0.01) polyW([[FDOOR.x0, 0, dz], [FDOOR.x1, 0, dz], [FDOOR.x1, FDOOR.h, dz], [FDOOR.x0, FDOOR.h, dz]], '#000', null);
  if (o.inDoor) o.inDoor();
  const a = op * 1.4, w = FDOOR.x1 - FDOOR.x0, ex = FDOOR.x1 - w * Math.cos(a), ez = dz + w * Math.sin(a);
  polyW([[FDOOR.x1, 0.01, dz], [ex, 0.01, ez], [ex, FDOOR.h - 0.01, ez], [FDOOR.x1, FDOOR.h - 0.01, dz]], '#202023', '#4c4c50', 3);
  const kp = prj([lerp(FDOOR.x1, ex, 0.88), 1.0, lerp(dz, ez, 0.88) + 0.02]); if (kp) circ(kp[0], kp[1], 0.03 * kp[3], '#77777c');
  polyW([[FDOOR.x0 - 0.06, 0, dz], [FDOOR.x0, 0, dz], [FDOOR.x0, FDOOR.h, dz], [FDOOR.x1, FDOOR.h, dz], [FDOOR.x1, 0, dz], [FDOOR.x1 + 0.06, 0, dz], [FDOOR.x1 + 0.06, FDOOR.h + 0.06, dz], [FDOOR.x0 - 0.06, FDOOR.h + 0.06, dz]], '#2a2a2d', '#55555a', 2);
  // the rug
  polyW([[SPOT.x - 1.0, 0.004, SPOT.z - 0.55], [SPOT.x + 0.95, 0.004, SPOT.z - 0.55], [SPOT.x + 0.95, 0.004, SPOT.z + 0.75], [SPOT.x - 1.0, 0.004, SPOT.z + 0.75]], '#202022', '#38383c', 2);
  lamp4(o.lamp ?? 0);
}
function lamp4(on) {
  const { x, z } = LAMP;
  polyW(ringPts([x, 0.01, z], [0.16, 0, 0], [0, 0, 0.16]), '#2a2a2d', '#4a4a4e', 2);
  lnW([x, 0.02, z], [x, 1.45, z], 5, '#5a5a5e');
  const top = [x, 1.62, z], bot = [x, 1.38, z];
  if (on > 0) { const p = prj([x, 1.45, z]); if (p) { ctx.save(); ctx.globalAlpha *= on; const g = ctx.createRadialGradient(p[0], p[1], 4, p[0], p[1], 0.9 * p[3]); g.addColorStop(0, 'rgba(255,226,170,0.5)'); g.addColorStop(1, 'rgba(255,226,170,0)'); ctx.fillStyle = g; ctx.fillRect(p[0] - 0.9 * p[3], p[1] - 0.9 * p[3], 1.8 * p[3], 1.8 * p[3]); ctx.restore(); } }
  polyW([...ringPts(bot, [0.23, 0, 0], [0, 0, 0.23], 16).slice(0, 9), ...ringPts(top, [0.15, 0, 0], [0, 0, 0.15], 16).slice(0, 9).reverse()], on > 0 ? '#e8dcc4' : '#3a3a3e', '#5a5a5e', 2);
}
// the sofa: legs, the dark gap under it, seat, back, arms
const SOFA_C = { top: '#3a3a3f', side: '#2a2a2e', front: '#303035', edge: '#58585e' };
function sofa4(o = {}) {
  const { x0, x1, z0, z1, gap, seat, back, arm } = SOFA, sh = o.shift || 0;   // shift: it moves, only a little
  ctx.save(); if (sh) ctx.translate(Math.sin(sh * 40) * 3 * sh, 0);
  for (const [lx, lz] of [[x0 + 0.08, z1 - 0.08], [x1 - 0.08, z1 - 0.08], [x0 + 0.08, z0 + 0.08], [x1 - 0.08, z0 + 0.08]]) box3(lx - 0.03, lx + 0.03, 0, gap, lz - 0.03, lz + 0.03, { top: '#444', side: '#333', front: '#3a3a3a', edge: '#555' });
  box3(x0, x1, gap, seat, z0, z1, SOFA_C);
  box3(x0, x1, seat, back, z0, z0 + 0.24, SOFA_C);
  box3(x0, x0 + 0.2, seat, arm, z0, z1, SOFA_C); box3(x1 - 0.2, x1, seat, arm, z0, z1, SOFA_C);
  // two cushions
  for (const cx of [x0 + 0.2, (x0 + x1) / 2]) box3(cx + 0.02, cx + (x1 - x0 - 0.4) / 2 - 0.02, seat, seat + 0.07, z0 + 0.26, z1 - 0.02, { top: '#45454a', side: '#333337', front: '#3b3b40', edge: '#5e5e64' });
  ctx.restore();
}
// the chair by the window, with the grey hoodie on it (o.hoodie: 'hang' | 'folded' | null)
function chair4(o = {}) {
  const { x, z } = CHAIR, cc = { top: '#333336', side: '#28282b', front: '#2e2e31', edge: '#55555a' };
  for (const [dx, dz] of [[-0.2, -0.2], [0.2, -0.2], [-0.2, 0.2], [0.2, 0.2]]) box3(x + dx - 0.02, x + dx + 0.02, 0, 0.45, z + dz - 0.02, z + dz + 0.02, cc);
  box3(x - 0.24, x + 0.24, 0.45, 0.5, z - 0.24, z + 0.24, cc);
  box3(x - 0.24, x - 0.2, 0.5, 1.0, z - 0.24, z + 0.24, cc);
  if (o.hoodie === 'hang') { const p = prj([x - 0.16, 0.74, z]); if (p) { const k = p[3] / 260;   // the grey hoodie over the chair back: hood, sleeves hanging
    ctx.save(); ctx.translate(p[0], p[1]); ctx.scale(k, k); glow('rgba(255,255,255,0.25)', 14);
    pth('M-70,-40 C-60,-80 60,-80 70,-40 L84,70 L56,74 L52,-6 L52,90 L-52,90 L-52,-6 L-56,74 L-84,70 Z', HOOD_C); noGlow();
    ell(0, -44, 26, 20, 0, '#55555a'); ln(-12, -20, -15, 18, 4, '#6a6a70'); ln(12, -20, 15, 18, 4, '#6a6a70'); rr(-30, 40, 60, 26, 8, '#87878d'); ctx.restore(); } }
  if (o.hoodie === 'folded') { box3(x - 0.17, x + 0.17, 0.5, 0.58, z - 0.15, z + 0.15, { top: '#b4b4ba', side: '#88888e', front: '#949499', edge: '#c4c4ca' });
    const p = prj([x, 0.585, z]); if (p) { const k = p[3]; ctx.save(); glow('rgba(255,255,255,0.2)', 8); ell(p[0], p[1], 0.07 * k, 0.03 * k, 0, '#9a9aa0'); ctx.restore(); } }
}
// the camera itself (a small dome on a bracket), for shots that see it. yaw: where it points; led: '#fff' | red
function cctv4(o = {}) {
  const { x, y, z } = CCTV, p = prj([x, y, z]); if (!p) return;
  const s = p[3]; ctx.save(); glow('rgba(255,255,255,0.15)', 10);
  rr(p[0] - 0.04 * s, p[1] - 0.12 * s, 0.08 * s, 0.1 * s, 0.01 * s, '#d8d8dc');
  ell(p[0], p[1], 0.1 * s, 0.075 * s, 0, '#e8e8ec'); noGlow();
  const a = o.dir ?? 2.6; circ(p[0] + Math.cos(a) * 0.04 * s, p[1] + Math.sin(a) * 0.03 * s + 0.01 * s, 0.035 * s, '#111');
  circ(p[0] + Math.cos(a) * 0.04 * s, p[1] + Math.sin(a) * 0.03 * s + 0.01 * s, 0.014 * s, '#3a4a5a');
  ctx.save(); if (o.led === 'red') redGlow(12); else glow('rgba(160,255,190,0.9)', 8); circ(p[0] + 0.06 * s, p[1] - 0.03 * s, 0.012 * s, o.led === 'red' ? C.red : '#9effc0'); ctx.restore();
  ctx.restore();
}

// ---------- people (from EP03: a 3D pictogram) ----------
const HOOD_C = '#9b9ba1';
const STAND = { L: [-0.22, 0.8, 0.02], R: [0.22, 0.8, 0.02] };
function poseOf(p) { return { x: SPOT.x, z: SPOT.z, yaw: 0, lean: 0, look: 0, roll: 0, ...STAND, ...p }; }
function skeleton(ps) {
  const yaw = ps.yaw || 0, F = [-Math.sin(yaw), 0, -Math.cos(yaw)], R = [Math.cos(yaw), 0, -Math.sin(yaw)];
  const Wd = (lx, ly, lz) => [ps.x + R[0] * lx + F[0] * lz, ly, ps.z + R[2] * lx + F[2] * lz];
  const hipY = 0.95, la = ps.lean || 0;
  const up = (lx, ly, lz = 0) => { const dy = ly - hipY; return Wd(lx, hipY + dy * Math.cos(la) - lz * Math.sin(la), lz * Math.cos(la) + dy * Math.sin(la)); };
  const look = ps.look || 0, roll = ps.roll || 0;
  const head = up(0.05 * roll, 1.63 - 0.035 * look - 0.012 * Math.abs(roll), 0.045 * look);
  const j = { look, F, R, head, neck: up(0, 1.47), chest: up(0, 1.36), pelvis: up(0, 1.02), sh: { L: up(-0.19, 1.42), R: up(0.19, 1.42) } };
  j.hand = { L: Wd(...ps.L), R: Wd(...ps.R) };
  j.elb = {};
  for (const [s, sg] of [['L', -1], ['R', 1]]) { const S = j.sh[s], Hh = j.hand[s], d = V3.sub(Hh, S), L = V3.len(d), B = 0.31;
    const mid = V3.lerp(S, Hh, 0.5); let bend = V3.add(V3.mul(R, sg * 0.7), V3.add([0, -0.55, 0], V3.mul(F, -0.45)));
    const dn = V3.norm(d); bend = V3.norm(V3.sub(bend, V3.mul(dn, V3.dot(bend, dn))));
    j.elb[s] = L >= 2 * B ? mid : V3.add(mid, V3.mul(bend, Math.sqrt(B * B - L * L / 4))); }
  const ph = ps.step || 0, sw = ps.walk ? 0.22 : 0;
  j.hip = { L: Wd(-0.09, 0.95, 0), R: Wd(0.09, 0.95, 0) };
  j.foot = { L: Wd(-0.1, 0.04 + Math.max(0, Math.sin(ph)) * 0.06 * (sw > 0), Math.cos(ph) * sw + 0.03), R: Wd(0.1, 0.04 + Math.max(0, -Math.sin(ph)) * 0.06 * (sw > 0), -Math.cos(ph) * sw + 0.03) };
  if (ps.footL) j.foot.L = ps.footL;
  j.knee = { L: V3.add(V3.lerp(j.hip.L, j.foot.L, 0.5), V3.mul(F, 0.03)), R: V3.add(V3.lerp(j.hip.R, j.foot.R, 0.5), V3.mul(F, 0.03)) };
  return j;
}
// o.col: skin, o.top: the hoodie (torso and sleeves), o.legs: trousers, o.hood: a hoodie with its hood, strings, pocket and cuffs, o.mark: a red box round the hoodie
const LEG_C = '#6a6a70', SHOE_C = '#2a2a2e', HOOD_EDGE = '#5e5e64';
function body3(ps, o = {}) {
  const j = skeleton(ps), col = o.col || C.fig, top = o.top || col, flat = !!o.flat, legs = flat ? col : (o.legs || LEG_C);
  const fd = V3.dot(j.F, V3.norm(V3.sub(camPos(), j.chest)));   // > 0: facing the camera
  const parts = [], P = q => prj(q);
  const cap = (a, b, w, c = col, d) => parts.push({ d: d ?? (toCam(a)[2] + toCam(b)[2]) / 2, f: () => { const p = P(a), q = P(b); if (p && q) ln(p[0], p[1], q[0], q[1], w * (p[3] + q[3]) / 2, c); } });
  const quad = (pts, fill, edge, d) => parts.push({ d, f: () => { const sp = pts.map(P); if (sp.some(x => !x)) return; ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); if (edge) { ctx.lineJoin = 'round'; ctx.strokeStyle = edge; ctx.lineWidth = 2; ctx.stroke(); } } });
  // legs (trousers) and shoes
  for (const s of ['L', 'R']) { cap(j.hip[s], j.knee[s], 0.14, legs); cap(j.knee[s], j.foot[s], 0.12, legs);
    if (!flat) parts.push({ d: toCam(j.foot[s])[2] - 0.01, f: () => { const f0 = P(j.foot[s]), f1 = P(V3.add(j.foot[s], V3.mul(j.F, 0.13))); if (!f0 || !f1) return;
      ln(f0[0], f0[1], f1[0], f1[1], 0.1 * f0[3], SHOE_C); ln(f0[0], f0[1] + 0.03 * f0[3], f1[0], f1[1] + 0.03 * f0[3], 0.025 * f0[3], '#77777c'); } }); }
  // the hoodie body: a real torso shape, wider at the shoulders, a ribbed band at the hem
  const sw = 0.22, hw = 0.17, dc = toCam(j.chest)[2] + 0.02;
  const shL = V3.add(j.sh.L, V3.mul(j.R, -0.03)), shR = V3.add(j.sh.R, V3.mul(j.R, 0.03)), hipL = V3.add(j.pelvis, V3.mul(j.R, -hw)), hipR = V3.add(j.pelvis, V3.mul(j.R, hw));
  quad([V3.add(shL, [0, 0.03, 0]), V3.add(shR, [0, 0.03, 0]), V3.add(hipR, [0, -0.04, 0]), V3.add(hipL, [0, -0.04, 0])], top, flat ? null : HOOD_EDGE, dc);
  if (!flat && o.hood) {
    const band = (y0, y1) => quad([V3.add(hipL, [0, y0, 0]), V3.add(hipR, [0, y0, 0]), V3.add(hipR, [0, y1, 0]), V3.add(hipL, [0, y1, 0])], '#a4a4aa', null, dc - 0.001);
    band(-0.04, 0.0);
    if (fd > 0.15) {   // the front: the kangaroo pocket and the two strings
      const pc = V3.add(V3.lerp(j.chest, j.pelvis, 0.72), V3.mul(j.F, 0.1));
      quad([V3.add(pc, V3.add(V3.mul(j.R, -0.11), [0, 0.07, 0])), V3.add(pc, V3.add(V3.mul(j.R, 0.11), [0, 0.07, 0])), V3.add(pc, V3.add(V3.mul(j.R, 0.14), [0, -0.07, 0])), V3.add(pc, V3.add(V3.mul(j.R, -0.14), [0, -0.07, 0]))], '#8e8e94', HOOD_EDGE, dc - 0.002);
      for (const sg of [-1, 1]) { const a = V3.add(j.neck, V3.add(V3.mul(j.R, sg * 0.04), V3.mul(j.F, 0.09))), b = V3.add(a, [sg * 0.005, -0.17, 0]);
        parts.push({ d: dc - 0.003, f: () => { const p = P(a), q = P(b); if (p && q) { ln(p[0], p[1], q[0], q[1], 0.012 * p[3], '#e8e8ec'); circ(q[0], q[1], 0.012 * q[3], '#e8e8ec'); } } }); }
    }
    // the hood: lying on the back, seen from behind; a rim round the neck from the front
    const hb = V3.add(j.neck, V3.add(V3.mul(j.F, -0.06), [0, -0.06, 0]));
    parts.push({ d: fd > 0.15 ? toCam(j.head)[2] + 0.05 : toCam(j.chest)[2] - 0.05, f: () => { const p = P(hb); if (!p) return; const r = p[3];
      ctx.save(); ctx.beginPath(); ctx.ellipse(p[0], p[1], 0.13 * r, 0.09 * r, 0, 0, Math.PI * 2); ctx.fillStyle = '#929298'; ctx.fill(); ctx.strokeStyle = HOOD_EDGE; ctx.lineWidth = 2; ctx.stroke();
      ln(p[0] - 0.09 * r, p[1] - 0.02 * r, p[0] + 0.09 * r, p[1] - 0.02 * r, 2, HOOD_EDGE); ctx.restore(); } });
  }
  cap(j.neck, j.chest, 0.08);
  for (const s of ['L', 'R']) { cap(j.sh[s], j.elb[s], 0.1, top); cap(j.elb[s], j.hand[s], 0.09, top);
    if (!flat && o.hood) { const c0 = V3.lerp(j.elb[s], j.hand[s], 0.86); cap(c0, V3.lerp(j.elb[s], j.hand[s], 0.97), 0.095, '#8a8a90', toCam(c0)[2] - 0.003); }
    parts.push({ d: toCam(j.hand[s])[2] - 0.004, f: () => { const p = P(j.hand[s]); if (p) circ(p[0], p[1], 0.05 * p[3], col); } }); }
  parts.push({ d: toCam(j.head)[2], f: () => head3(j, col, o) });
  if (o.mark) parts.push({ d: -1, f: () => { const c = P(V3.lerp(j.chest, j.pelvis, 0.4)); if (c) { noGlow(); redGlow(16); rrS(c[0] - 0.26 * c[3], c[1] - 0.4 * c[3], 0.52 * c[3], 0.8 * c[3], 8, C.red, 4); noGlow(); } } });
  parts.sort((a, b) => b.d - a.d);
  ctx.save(); glow(o.glow || 'rgba(255,255,255,0.22)', 14); for (const p of parts) { ctx.save(); p.f(); ctx.restore(); } ctx.restore();
  return j;
}
function head3(j, col, o) {
  const p = prj(j.head); if (!p) return; const r = 0.11 * p[3];
  circ(p[0], p[1], r, col); noGlow();
  const fd = V3.dot(j.F, V3.norm(V3.sub(camPos(), j.head)));
  ctx.save(); ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.clip();
  const side = prj(V3.add(j.head, V3.mul(j.F, 0.05))), sx = side ? (side[0] - p[0]) : 0;
  const up = lerp(0.0, 0.78, (fd + 1) / 2) * r;
  circ(p[0] - sx * 0.9 * (1 - fd * fd), p[1] - up, r * 1.02, o.hair || '#4a4a50');
  if (fd < 0.2) for (let i = -2; i <= 2; i++) ln(p[0] + i * r * 0.28, p[1] - r, p[0] + i * r * 0.34, p[1] + r * 0.2, 1.5, '#38383d');   // strands of hair from behind
  ctx.restore();
  if (fd > 0.15) { const a = clamp((fd - 0.15) / 0.3);   // a face toward the camera always shows both eyes
    for (const sg of [-1, 1]) { const e = prj(V3.add(j.head, V3.add(V3.mul(j.F, 0.1), V3.add(V3.mul(j.R, sg * 0.042), [0, 0.005 - 0.05 * (j.look || 0), 0])))); if (!e) continue;
      ctx.save(); ctx.globalAlpha *= a; ell(e[0], e[1], 0.014 * e[3], (o.blink ? 0.003 : 0.018) * e[3], 0, o.eye || '#000'); ctx.restore(); } }
}
// someone lying on the floor, feet toward (fx, fz), head toward the direction a (radians in the floor plane).
// o.clipZ: only what is in front of that z is drawn (the rest has gone under the sofa); o.reach 0..1 arms stretched past the head, clawing
function lying3(fx, fz, a, o = {}) {
  const col = o.col || C.fig, top = o.top || col, legs = o.flat ? col : (o.legs || LEG_C), u = [Math.sin(a), 0, Math.cos(a)], r = [Math.cos(a), 0, -Math.sin(a)];
  const P = (along, side, y = 0.08) => [fx + u[0] * along + r[0] * side, y, fz + u[2] * along + r[2] * side];
  const cz = o.clipZ ?? -99;
  const cut = (A, B) => { if (A[2] < cz && B[2] < cz) return null; if (A[2] >= cz && B[2] >= cz) return [A, B]; const k = (cz - A[2]) / (B[2] - A[2]), M = V3.lerp(A, B, k); return A[2] < cz ? [M, B] : [A, M]; };
  const cap = (A, B, w, c) => { const ab = cut(A, B); if (!ab) return; const p = prj(ab[0]), q = prj(ab[1]); if (p && q) ln(p[0], p[1], q[0], q[1], w * (p[3] + q[3]) / 2, c); };
  const wig = o.wig || 0, rc = o.reach ?? 0;
  ctx.save(); glow('rgba(255,255,255,0.2)', 12);
  cap(P(0, -0.1), P(0.5, -0.09), 0.13, legs); cap(P(0.02, 0.1), P(0.5, 0.09), 0.13, legs);
  if (!o.flat) for (const sd of [-0.1, 0.1]) cap(P(-0.04, sd, 0.06), P(0.06, sd, 0.06), 0.1, SHOE_C);
  cap(P(0.5, 0, 0.11), P(1.05, 0, 0.12), 0.3, top);
  if (!o.flat && o.hood !== false) cap(P(0.5, 0, 0.12), P(0.56, 0, 0.12), 0.31, '#8a8a90');
  // arms flung up past the head, fingers clawing at the floor
  for (const sg of [-1, 1]) { const s0 = P(1.0, sg * 0.19, 0.1), e = P(1.0 + 0.3 + 0.18 * rc, sg * (0.3 + 0.06 * Math.sin(wig + sg)), 0.06), h = P(1.0 + 0.48 + 0.25 * rc, sg * (0.28 + 0.08 * Math.sin(wig * 1.3 + sg)), 0.03);
    cap(s0, e, 0.09, top); cap(e, h, 0.085, top); const ab = cut(h, h); if (ab) { const hp = prj(h); if (hp) circ(hp[0], hp[1], 0.05 * hp[3], col); } }
  const hc = P(1.27, 0, 0.11); if (hc[2] >= cz) { const h = prj(hc); if (h) { circ(h[0], h[1], 0.11 * h[3], col); circ(h[0], h[1] - 0.03 * h[3], 0.1 * h[3], '#4a4a50'); } }
  ctx.restore();
}

// ---------- the thing under the sofa ----------
// Grey, thin, wrong. A long cracked skull with one red eye and one stitched-shut socket, wet black hair, a spine, and arms with far too many joints.
// It only moves when the camera is not looking at it.
const THING_C = '#b4b4ba', THING_EDGE = '#2a2a2e', THING_X = 0.4;
function underThing(t, o = {}) {
  const ex = o.ex ?? THING_X;
  if ((o.eye || 0) > 0 && !(o.head > 0)) { const p = prj([ex, 0.07, SOFA.z1 + 0.01]); if (p) { ctx.save(); ctx.globalAlpha *= o.eye; redGlow(26 + 10 * Math.sin(t * 5)); ell(p[0], p[1], 0.05 * p[3], 0.03 * p[3], 0, C.red); noGlow(); ell(p[0], p[1], 0.008 * p[3], 0.026 * p[3], 0, '#1a0000'); ctx.restore(); } }
  if (o.head > 0) thingHead(t, ex, o.head, o);
}
// the arm: from under the front edge of the sofa out across the floor to `to`, k of the way; every other joint knuckles high off the floor, like an insect's
function armPath(from, to, n = 7) {
  const pts = []; for (let i = 0; i <= n; i++) { const u = i / n, wob = Math.sin(u * Math.PI * 3) * 0.08 * (1 - u);
    const dx = to[0] - from[0], dz = to[1] - from[1], L = Math.hypot(dx, dz) || 1;
    pts.push([lerp(from[0], to[0], u) - dz / L * wob, i === n ? 0.05 : i % 2 ? 0.17 : 0.03, lerp(from[1], to[1], u) + dx / L * wob]); }
  return pts;
}
// one bone: thick at the joints, thin in the middle, a tendon down its length
function bone3(a, b, col, edge, w = 0.045) {
  const p = prj(a), q = prj(b); if (!p || !q) return;
  const dx = q[0] - p[0], dy = q[1] - p[1], L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L, w0 = w * p[3], w1 = w * q[3], wm = 0.55 * (w0 + w1) / 2;
  const mx = (p[0] + q[0]) / 2, my = (p[1] + q[1]) / 2;
  ctx.beginPath(); ctx.moveTo(p[0] + nx * w0 / 2, p[1] + ny * w0 / 2); ctx.quadraticCurveTo(mx + nx * wm / 2, my + ny * wm / 2, q[0] + nx * w1 / 2, q[1] + ny * w1 / 2);
  ctx.lineTo(q[0] - nx * w1 / 2, q[1] - ny * w1 / 2); ctx.quadraticCurveTo(mx - nx * wm / 2, my - ny * wm / 2, p[0] - nx * w0 / 2, p[1] - ny * w0 / 2); ctx.closePath();
  ctx.fillStyle = col; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = edge; ctx.stroke();
  ctx.save(); ctx.globalAlpha *= 0.5; ln(p[0] + nx * w0 * 0.15, p[1] + ny * w0 * 0.15, q[0] + nx * w1 * 0.15, q[1] + ny * w1 * 0.15, 1.5, edge); ctx.restore();
}
function knuckle3(c, col, edge, r = 0.035) { const p = prj(c); if (!p) return; ell(p[0], p[1], r * p[3], r * 0.8 * p[3], 0, col); ctx.lineWidth = 2; ctx.strokeStyle = edge; ctx.stroke();
  ctx.beginPath(); ctx.arc(p[0], p[1] + r * 0.2 * p[3], r * 0.5 * p[3], 3.6, 5.8); ctx.stroke(); }
// a hand: a narrow palm and five long fingers of three bones each, dark pointed nails. grip: curled shut (round an ankle)
function claw2(x, y, a0, s, o = {}) {
  const col = o.col || THING_C, edge = o.edge || THING_EDGE, grip = o.grip ? 1 : 0, t = o.t || 0;
  ctx.save(); ctx.translate(x, y); ctx.rotate(a0);
  ctx.beginPath(); ctx.ellipse(0.02 * s, 0, 0.05 * s, 0.035 * s, 0, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = edge; ctx.stroke();
  for (let i = 0; i < 5; i++) { const thumb = i === 4, sp = thumb ? 1.25 : (i - 1.5) * 0.24, len = (thumb ? 0.65 : i === 1 || i === 2 ? 1.15 : 1) * 0.085 * s;
    let px = 0.05 * s * Math.cos(sp), py = 0.04 * s * Math.sin(sp), ang = sp * (1 - 0.5 * grip);
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for (let k = 0; k < 3; k++) { const bend = grip ? 0.85 : 0.22 + 0.08 * Math.sin(t * 5 + i + k); ang += bend * (thumb ? -1 : 1) * (k ? 1 : 0.4);
      const nx = px + Math.cos(ang) * len * (1 - k * 0.18), ny = py + Math.sin(ang) * len * (1 - k * 0.18);
      ln(px, py, nx, ny, 0.026 * s * (1 - k * 0.22) + 3, edge); ln(px, py, nx, ny, 0.026 * s * (1 - k * 0.22), col);
      if (k < 2) circ(nx, ny, 0.016 * s, col);
      else { const na = ang; pth(`M${nx + Math.cos(na + 1.6) * 0.012 * s},${ny + Math.sin(na + 1.6) * 0.012 * s} L${nx + Math.cos(na) * 0.04 * s},${ny + Math.sin(na) * 0.04 * s} L${nx + Math.cos(na - 1.6) * 0.012 * s},${ny + Math.sin(na - 1.6) * 0.012 * s} Z`, '#121214'); }
      px = nx; py = ny; } }
  ctx.restore();
}
function thingArm(t, o) {
  const ex = o.ex ?? THING_X, to = o.to || [SPOT.x, SPOT.z], from = [ex + 0.24 * (to[0] < ex ? -1 : 1), SOFA.z1 - 0.1], k = clamp(o.k ?? 1);
  const pts = armPath(from, to, o.n || 7), n = pts.length - 1, reach = k * n, col = o.col || THING_C, edge = o.edge || THING_EDGE;
  const segs = []; let last = pts[0];
  for (let i = 0; i < n && i < reach; i++) { const a = pts[i], b = i + 1 <= reach ? pts[i + 1] : V3.lerp(pts[i], pts[i + 1], reach - i); segs.push([a, b]); last = b; }
  ctx.save(); glow('rgba(255,255,255,0.14)', 10);
  segs.forEach(([a, b], i) => bone3(a, b, col, edge, 0.05 - i * 0.002));
  segs.forEach(([a], i) => { if (i > 0) knuckle3(a, col, edge, 0.034); });
  noGlow();
  const hp = prj(last), pv = prj(segs.length ? segs[segs.length - 1][0] : pts[0]);
  if (hp && pv && k > 0.05) claw2(hp[0], hp[1], Math.atan2(hp[1] - pv[1], hp[0] - pv[0]), hp[3] * 1.5, { grip: o.grip, col, edge, t });
  ctx.restore();
  return last;
}
// its head sliding out from under the sofa, lying on its side, then lifting its one red eye to the camera. o.size scales it; o.hands: two hands on the floor beside it
function thingHead(t, ex, k, o = {}) {
  const out = ease(clamp(k * 1.6)), lift = ease(clamp(k * 1.6 - 0.6));
  const c = [ex, 0.08 + 0.1 * lift, SOFA.z1 - 0.15 + 0.32 * out], p = prj(c); if (!p) return;
  const s = p[3] * (o.size || 1.4), col = o.col || THING_C, edge = o.edge || THING_EDGE;
  // the neck: a ridge of vertebrae running back into the dark under the sofa
  const nb = prj([ex + 0.05, 0.05, SOFA.z1 - 0.25]); if (nb) { ctx.save(); ln(nb[0], nb[1], p[0], p[1], 0.07 * s, col); ctx.globalAlpha *= 0.9;
    for (let i = 1; i < 6; i++) { const u = i / 6; circ(lerp(nb[0], p[0], u), lerp(nb[1], p[1], u) - 0.02 * s, 0.022 * s, '#8a8a90'); } ctx.restore(); }
  // the hands, flat on the floor either side, fingers splayed toward you
  if (o.hands !== false) for (const sg of [-1, 1]) { const h = prj([ex + sg * 0.3, 0.02, SOFA.z1 + 0.05 + 0.1 * out]), b = prj([ex + sg * 0.3, 0.02, SOFA.z1 - 0.1]); if (h && b) {
    ctx.save(); ln(b[0], b[1], h[0], h[1], 0.04 * h[3], col); claw2(h[0], h[1], Math.atan2(h[1] - b[1], h[0] - b[0]) + sg * 0.25, h[3] * 1.3, { col, edge, t: t + sg }); ctx.restore(); } }
  ctx.save(); glow('rgba(255,255,255,0.16)', 14);
  ctx.translate(p[0], p[1]); ctx.rotate(lerp(1.35, 0.12, lift) + Math.sin(t * 0.8) * 0.03);
  // long wet black hair hanging from the crown down both sides of the skull
  const hair = (i, n, front) => { const u = i / (n - 1), ang = lerp(-2.7, -0.45, u), sx = Math.cos(ang) * 0.15 * s, sy = -0.04 * s + Math.sin(ang) * 0.18 * s, side = Math.sign(Math.cos(ang)) || 1, sway = Math.sin(t * 0.8 + i * 1.7) * 0.012 * s;
    const len = (0.42 + 0.12 * ((i * 7) % 5) / 4) * s; ctx.beginPath(); ctx.moveTo(sx, sy);
    ctx.bezierCurveTo(sx + side * 0.07 * s, sy + 0.05 * s, sx + side * (0.05 * s) + sway, sy + len * 0.5, sx + side * (0.02 * s + 0.03 * s * Math.sin(i)) + sway * 2, sy + len);
    ctx.strokeStyle = front ? 'rgba(18,18,20,0.92)' : (i % 2 ? '#141416' : '#26262b'); ctx.lineWidth = (front ? 0.008 : 0.013) * s; ctx.lineCap = 'round'; ctx.stroke(); };
  for (let i = 0; i < 26; i++) hair(i, 26, false);
  // the skull: tall dome, long narrow jaw, slightly crooked; no mouth
  const sk = () => { ctx.beginPath(); ctx.moveTo(-0.01 * s, -0.21 * s); ctx.bezierCurveTo(0.14 * s, -0.21 * s, 0.15 * s, 0.0, 0.08 * s, 0.14 * s); ctx.bezierCurveTo(0.05 * s, 0.22 * s, 0.01 * s, 0.27 * s, -0.025 * s, 0.26 * s);
    ctx.bezierCurveTo(-0.07 * s, 0.24 * s, -0.11 * s, 0.12 * s, -0.12 * s, 0.02 * s); ctx.bezierCurveTo(-0.14 * s, -0.12 * s, -0.11 * s, -0.21 * s, -0.01 * s, -0.21 * s); };
  sk(); ctx.fillStyle = col; ctx.fill(); noGlow(); ctx.lineWidth = 3; ctx.strokeStyle = edge; ctx.stroke();
  ctx.save(); sk(); ctx.clip();
  // hollow cheeks and a dark underside
  ctx.globalAlpha = 0.45; ell(-0.085 * s, 0.09 * s, 0.035 * s, 0.09 * s, 0.15, '#4a4a50'); ell(0.085 * s, 0.07 * s, 0.03 * s, 0.08 * s, -0.2, '#4a4a50');
  const g = ctx.createLinearGradient(0, -0.2 * s, 0, 0.27 * s); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.6, 'rgba(0,0,0,0.1)'); g.addColorStop(1, 'rgba(0,0,0,0.6)'); ctx.globalAlpha = 1; ctx.fillStyle = g; ctx.fillRect(-0.2 * s, -0.25 * s, 0.4 * s, 0.55 * s);
  // cracks over the dome
  ctx.strokeStyle = edge; ctx.lineWidth = 1.6; ctx.globalAlpha = 0.8;
  ctx.beginPath(); ctx.moveTo(0.03 * s, -0.21 * s); ctx.lineTo(0.05 * s, -0.16 * s); ctx.lineTo(0.035 * s, -0.12 * s); ctx.lineTo(0.06 * s, -0.09 * s); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-0.1 * s, -0.12 * s); ctx.lineTo(-0.07 * s, -0.1 * s); ctx.lineTo(-0.075 * s, -0.06 * s); ctx.stroke();
  // two slits where a nose should be
  ctx.globalAlpha = 0.9; ell(-0.012 * s, 0.07 * s, 0.006 * s, 0.018 * s, 0.1, '#1a1a1c'); ell(0.012 * s, 0.07 * s, 0.006 * s, 0.018 * s, -0.1, '#1a1a1c');
  ctx.restore();
  // the left socket: stitched shut
  ell(-0.06 * s, -0.04 * s, 0.035 * s, 0.022 * s, -0.15, '#3a3a3f'); ctx.lineWidth = 1.8; ctx.strokeStyle = '#121214';
  ln(-0.088 * s, -0.035 * s, -0.032 * s, -0.045 * s, 2, '#121214'); for (let i = 0; i < 4; i++) { const x = (-0.082 + i * 0.016) * s; ln(x, -0.055 * s, x + 0.003 * s, -0.025 * s, 1.6, '#121214'); }
  // the right one: wide open, the only red thing about it
  ell(0.045 * s, -0.05 * s, 0.062 * s, 0.05 * s, 0.1, '#0c0c0d');
  redGlow(28 + 12 * Math.sin(t * 5)); ell(0.045 * s, -0.05 * s, 0.046 * s, 0.037 * s, 0.1, C.red); noGlow();
  ctx.strokeStyle = 'rgba(90,0,0,0.9)'; ctx.lineWidth = 1.2; for (let i = 0; i < 7; i++) { const a = i * 0.9; ctx.beginPath(); ctx.moveTo(0.045 * s + Math.cos(a) * 0.044 * s, -0.05 * s + Math.sin(a) * 0.035 * s); ctx.lineTo(0.045 * s + Math.cos(a + 0.2) * 0.026 * s, -0.05 * s + Math.sin(a + 0.2) * 0.02 * s); ctx.stroke(); }
  ell(0.047 * s, -0.05 * s, 0.008 * s, 0.032 * s, 0.1, '#150000'); circ(0.06 * s, -0.064 * s, 0.006 * s, 'rgba(255,220,220,0.8)');
  for (const i of [4, 6, 7, 9, 11]) hair(i, 26, true);
  ctx.restore();
}

// ---------- the phone ----------
const SW = 368, SH = 808;
function phone(x, y, s, fn, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(o.rot || 0);
  const bright = o.bright ?? 1;
  if (bright > 0) { ctx.save(); ctx.globalAlpha *= 0.55 * bright; glow('rgba(215,228,255,0.9)', 90); rr(-190, -414, 380, 828, 50, '#0d0d0d'); ctx.restore(); }
  rr(-200, -424, 400, 848, 58, '#111'); rrS(-200, -424, 400, 848, 58, '#5e5e5e', 5); rrS(-193, -417, 386, 834, 52, '#262626', 3);
  rr(-204, -280, 6, 70, 3, '#3a3a3a'); rr(198, -300, 6, 110, 3, '#3a3a3a');
  ctx.save(); ctx.beginPath(); ctx.roundRect(-SW / 2, -SH / 2, SW, SH, 44); ctx.clip();
  ctx.translate(-SW / 2, -SH / 2); rr(0, 0, SW, SH, 0, '#000'); fn();
  if (bright < 1) { ctx.globalAlpha = 1 - bright; rr(0, 0, SW, SH, 0, '#000'); ctx.globalAlpha = 1; }
  ctx.restore();
  rr(-58, -SH / 2 + 14, 116, 34, 17, '#000'); circ(30, -SH / 2 + 31, 7, '#151515');
  ctx.restore();
}
function statusBar(time = '3:02', dark = true) {
  const c = dark ? '#f2f2f2' : '#111';
  text(time, 46, 40, `600 19px ${UI}`, c, 'left');
  for (let i = 0; i < 4; i++) rr(276 + i * 8, 34 - i * 3, 5, 6 + i * 3, 1, c);
  rrS(312, 26, 32, 15, 4, c, 2); rr(315, 29, 22, 9, 2, c); rr(345, 30, 2, 7, 1, c);
}
// a camera-app notification card (generic, no real brand)
function camNotif(x, y, w, sub = 'Living room · 3:02 AM', o = {}) {
  ctx.save(); ctx.globalAlpha *= 0.96; rr(x, y, w, 96, 22, o.light ? '#e9e9ec' : '#1e1e21'); ctx.restore();
  const tc = o.light ? '#111' : '#f2f2f2', sc = o.light ? '#555' : '#9a9a9e';
  rr(x + 16, y + 20, 56, 56, 14, '#2b2b2f'); circS(x + 44, y + 48, 15, '#e8e8ec', 4); circ(x + 44, y + 48, 6, C.red);
  text('Motion detected', x + 88, y + 44, `700 22px ${UI}`, tc, 'left'); text(sub, x + 88, y + 74, `500 18px ${UI}`, sc, 'left');
  text('now', x + w - 20, y + 40, `500 15px ${UI}`, sc, 'right');
}
// ---------- EP04 scenes: "If Your Security Camera Ever Records Tomorrow" ----------
const ev = type => window.TL.events.filter(e => e.type === type);
const evAfter = (type, t0) => { const l = ev(type).filter(e => e.t >= t0 - 0.01); return l.length ? l.reduce((a, b) => (b.t < a.t ? b : a)) : null; };
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
const sideTag = (t, t0, s, x, y, col = C.fig, size = 50) => { if (t >= t0) pop(t, t0, x, y, () => tag(s, x, y + 10, col, size, 'center')); };
const redFlash = (t, t0, a = 0.1) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a * (0.5 + 0.5 * Math.sin((t - t0) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const whiteFlash = (t, t0, a = 0.55, d = 0.07) => { if (t >= t0 && t < t0 + d) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const blackAfter = (t, t0) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
function xTag(s, x, y, size, p) { tag(s, x, y, C.fig, size, 'center'); ctx.font = `900 ${size}px M`; const w = ctx.measureText(s).width + 28; redX(x - w / 2 - size * 0.95, y - size * 0.2, size * 0.5, p); }
const zk = (t, t0, d, z0, z1) => lerp(z0, z1, ease((t - t0) / d));
const clockStr = s => { s = Math.max(0, Math.floor(s)); const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, x = s % 60; return [h, m, x].map(v => String(v).padStart(2, '0')).join(':'); };
const T302 = 3 * 3600 + 2 * 60;

// ---------- the living room, seen by some camera ----------
// o: room4 options + thing {eye, ex, head}, arm {k, to, grip}, shift (the sofa moves), people [{pose, o}], lying [{x,z,a,o}], hoodie, cctvDev {led, dir}
function living(t, o = {}) {
  room4(t, o);
  for (const L of (o.lying || [])) if (L.under) lying3(L.x, L.z, L.a, L.o || {});
  sofa4({ shift: o.shift || 0 });
  // the dark gap under the front of the sofa
  { const sh = o.shift ? Math.sin(o.shift * 40) * 3 * o.shift : 0; ctx.save(); ctx.translate(sh, 0); ctx.globalAlpha *= 0.85; polyW([[SOFA.x0 + 0.04, 0.003, SOFA.z1 - 0.02], [SOFA.x1 - 0.04, 0.003, SOFA.z1 - 0.02], [SOFA.x1 - 0.04, 0.003, SOFA.z1 + 0.1], [SOFA.x0 + 0.04, 0.003, SOFA.z1 + 0.1]], '#050505', null); ctx.restore(); }
  if (o.thing) underThing(t, { ...o.thing, head: 0 });
  if (o.arm && !o.arm.over) thingArm(t, o.arm);
  if (o.thing && o.thing.head > 0) thingHead(t, o.thing.ex ?? THING_X, o.thing.head, o.thing);
  chair4({ hoodie: o.hoodie });
  for (const L of (o.lying || [])) if (!L.under) lying3(L.x, L.z, L.a, L.o || {});
  const ps = (o.people || []).slice().sort((a, b) => V3.len(V3.sub(camPos(), [b.pose.x, 1, b.pose.z])) - V3.len(V3.sub(camPos(), [a.pose.x, 1, a.pose.z])));
  for (const p of ps) body3(p.pose, p.o || {});
  if (o.arm && o.arm.over) thingArm(t, o.arm);   // the hand closes over the ankle, in front of the leg
  if (o.cctvDev) cctv4(o.cctvDev);
  if (o.front) o.front();
}
// a shot of the room (not through the security camera): push in toward a world point
function view(t, t0, d, z0, z1, focus, o) {
  setCam(o.camObj || o.cam || CAMS.side); const f = prj(focus) || [W / 2, H / 2];
  cam(t, t0, d, z0, z1, f[0], f[1], () => living(t, o));
}
// ---------- the security camera's picture ----------
// o.rect {x,y,w} where it sits (default: big, above the captions); o.z zoom, o.focus world point to zoom on; o.date 'TOMORROW'|'TODAY'|'LIVE'|'TONIGHT';
// o.clock seconds; o.bar 0..1 (playback position); o.label; o.noise 0..1; o.off 0..1 (no signal)
const FR = { x: 160, y: 40, w: 1600 };
let LASTFEED = null;
function feed(t, o = {}) {
  const r = o.rect || FR, s = r.w / W;
  ctx.save(); ctx.translate(r.x, r.y); ctx.scale(s, s);
  ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.clip();
  rr(0, 0, W, H, 0, '#000');
  setCam(o.camObj || CAMS.cctv);
  const z = o.z || 1, fp = o.focus ? (prj(o.focus) || [W / 2, H / 2]) : [W / 2, H / 2];
  LASTFEED = { r, s, z, fx: fp[0], fy: fp[1], camObj: o.camObj || CAMS.cctv };
  ctx.save(); ctx.translate(fp[0], fp[1]); ctx.scale(z, z); ctx.translate(-fp[0], -fp[1]);
  if (!(o.off >= 1)) living(t, o);
  ctx.restore();
  // the camera's own look: cold grey, scan lines, noise, a dark rim
  ctx.save(); ctx.globalCompositeOperation = 'color'; ctx.globalAlpha = 0.5; ctx.fillStyle = '#7a8a86'; ctx.fillRect(0, 0, W, H); ctx.restore();
  ctx.save(); ctx.globalAlpha = 0.09; for (let y = 0; y < H; y += 6) rr(0, y, W, 2, 0, '#000'); ctx.restore();
  if (grainC) { ctx.save(); ctx.globalAlpha = 0.1 + 0.4 * (o.noise || 0); ctx.drawImage(grainC[Math.floor(t * 24) % 4], 0, 0, W, H); ctx.restore(); }
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.0); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.75)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  if (o.off > 0) { ctx.save(); ctx.globalAlpha = clamp(o.off); rr(0, 0, W, H, 0, '#050505'); ctx.globalAlpha *= 0.3; ctx.drawImage(grainC[Math.floor(t * 30) % 4], 0, 0, W, H); ctx.restore();
    if (o.off >= 1) spaced('NO SIGNAL', W / 2, H / 2 + 24, '600 64px Plex', '#bdbdbd', 8); }
  // the overlay: a blinking dot, the room, the date and time
  if (Math.floor(t * 1.6) % 2 === 0) { ctx.save(); redGlow(14); circ(70, 70, 16, C.red); ctx.restore(); }
  text('CAM 1', 100, 84, '600 40px Plex', '#e8e8e8', 'left');
  text(o.label || 'LIVING ROOM', 60, H - 44, '600 44px Plex', '#e8e8e8', 'left');
  const date = o.date || 'TOMORROW', hot = date === 'TOMORROW' || date === 'TONIGHT';
  const tm = clockStr(o.clock ?? T302);
  ctx.font = '600 44px Plex'; const tw = ctx.measureText(tm).width;
  text(tm, W - 60, H - 44, '600 44px Plex', '#e8e8e8', 'right');
  ctx.save(); if (hot) redGlow(14); text(date, W - 90 - tw, H - 44, '700 44px Plex', hot ? C.red : '#e8e8e8', 'right'); ctx.restore();
  if (o.bar != null) { rr(60, H - 22, W - 120, 8, 4, 'rgba(255,255,255,0.25)'); ctx.save(); redGlow(10); rr(60, H - 22, (W - 120) * clamp(o.bar), 8, 4, C.red); ctx.restore(); circ(60 + (W - 120) * clamp(o.bar), H - 18, 13, '#f2f2f2'); }
  ctx.restore();
  rrS(r.x, r.y, r.w, r.w * H / W, 6, '#3a3a3e', 3);
}
// where a world point lands on screen in the last feed drawn this frame
function feedPt(p) { const L = LASTFEED; if (!L) return null; setCam(L.camObj); const q = prj(p); if (!q) return null;
  const x = L.fx + (q[0] - L.fx) * L.z, y = L.fy + (q[1] - L.fy) * L.z; return [L.r.x + x * L.s, L.r.y + y * L.s, q[3] * L.z * L.s]; }
// a label tied to something in the feed: a thin line from the thing to the tag
function feedTag(t, t0, s, p, tx, ty, col = C.fig, size = 44) {
  if (t < t0) return; const q = feedPt(p); if (!q) return;
  if (tx === 'rel') { tx = q[0] + ty[0]; ty = q[1] + ty[1]; }
  const k = easeOut(prog(t, t0, 0.3)); ctx.save(); ctx.globalAlpha *= k; ctx.setLineDash([8, 8]); ln(q[0], q[1], lerp(q[0], tx, k), lerp(q[1], ty + 20, k), 3, col); ctx.setLineDash([]);
  circ(q[0], q[1], 9, col); ctx.restore(); pop(t, t0 + 0.1, tx, ty, () => tag(s, tx, ty + 10, col, size, 'center'));
}
// the camera app on the phone: the clip on top, the playback bar, the list of clips
function appScreen(t, o = {}) {
  rr(0, 0, SW, SH, 0, '#0b0b0c'); statusBar(o.time || '3:02');
  pthS('M30,82 l-12,12 l12,12', '#bdbdbd', 3.5); text(o.title || 'Living room', SW / 2, 102, `700 22px ${UI}`, '#f2f2f2');
  feed(t, { ...o, rect: { x: 0, y: 136, w: SW } });
  const by = 136 + SW * H / W + 34, p = clamp(o.bar ?? 0), dur = o.dur ?? 240;
  rr(24, by, SW - 48, 6, 3, '#333'); rr(24, by, (SW - 48) * p, 6, 3, C.red); circ(24 + (SW - 48) * p, by + 3, 9, '#f2f2f2');
  if (o.limit != null) { const lx = 24 + (SW - 48) * o.limit; ln(lx, by - 12, lx, by + 18, 3, '#ffd34d'); }
  const m = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  text(m(p * dur), 24, by + 34, `500 16px ${UI}`, '#9a9a9e', 'left'); text(m(dur), SW - 24, by + 34, `500 16px ${UI}`, '#9a9a9e', 'right');
  // play / pause
  const cy = by + 82; circ(SW / 2, cy, 30, '#1e1e21'); if (o.playing) { rr(SW / 2 - 10, cy - 12, 7, 24, 2, '#f2f2f2'); rr(SW / 2 + 3, cy - 12, 7, 24, 2, '#f2f2f2'); } else pth(`M${SW / 2 - 8},${cy - 13} L${SW / 2 + 13},${cy} L${SW / 2 - 8},${cy + 13} Z`, '#f2f2f2');
  // the clip list
  const clips = o.clips || [['Living room', 'Tomorrow · 3:02 AM', true]];
  text('CLIPS', 24, cy + 74, `700 15px ${UI}`, '#7a7a7e', 'left');
  clips.forEach(([a, b, red, at], i) => { const y = cy + 92 + i * 84; if (at != null && t < at) return; const k = at != null ? easeOut(prog(t, at, 0.3)) : 1;
    ctx.save(); ctx.globalAlpha *= k; rr(18, y, SW - 36, 72, 14, '#18181b'); rr(30, y + 10, 92, 52, 6, '#26262a'); pth(`M${68},${y + 26} L${86},${y + 36} L${68},${y + 46} Z`, '#bdbdbd');
    text(a, 136, y + 32, `600 18px ${UI}`, '#f2f2f2', 'left'); text(b, 136, y + 56, `500 15px ${UI}`, red ? '#ff5a5a' : '#9a9a9e', 'left'); ctx.restore(); });
}
function lockScreen(t, o = {}) {
  const g = ctx.createLinearGradient(0, 0, 0, SH); g.addColorStop(0, o.morning ? '#3a3328' : '#15161b'); g.addColorStop(1, '#050506'); ctx.fillStyle = g; ctx.fillRect(0, 0, SW, SH);
  statusBar(o.time || '3:02');
  text(o.time || '3:02', SW / 2, 230, `200 104px ${UI}`, '#f2f2f2'); text(o.day || 'Tuesday', SW / 2, 136, `500 22px ${UI}`, '#d8d8d8');
  if (o.notif != null && t >= o.notif) slideIn(t, o.notif, 0, -40, () => camNotif(14, 300, SW - 28, o.sub || 'Living room · 3:02 AM'), 0.35);
}

// ---------- flat icons (white), for the teaser boxes ----------
function icon4(name, x, y, s = 1, col = C.fig) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  if (name === 'play') { rrS(-96, -66, 192, 120, 14, col, 9); pth('M-22,-30 L30,-4 L-22,22 Z', col); rr(-96, 74, 192, 10, 5, '#555'); rr(-96, 74, 150, 10, 5, col); }
  if (name === 'hoodie') { pth('M-70,-40 C-60,-80 60,-80 70,-40 L100,70 L60,74 L52,-6 L52,90 L-52,90 L-52,-6 L-60,74 L-100,70 Z', col); noGlow(); ell(0, -42, 30, 24, 0, '#000'); ln(-12, -20, -16, 20, 4, '#000'); ln(12, -20, 16, 20, 4, '#000'); }
  if (name === 'home') { pth('M0,-86 L92,-10 L70,-10 L70,80 L-70,80 L-70,-10 L-92,-10 Z', col); noGlow(); rr(-22, 18, 44, 62, 4, '#000'); circ(12, 50, 4, col); }
  if (name === 'clock') { circS(0, 0, 76, col, 10); ln(0, 0, 0, -48, 9, col); ln(0, 0, 36, 18, 9, col); circ(0, 0, 9, col); }
  noGlow(); ctx.restore();
}
// rule-page pictograms (dark on the page)
const _pageIcon = pageIcon;
pageIcon = function (name, x, y, col = '#111') {
  ctx.save(); ctx.translate(x, y);
  if (name === 'play') { rrS(-46, -34, 92, 62, 8, col, 6); pth('M-10,-16 L16,-2 L-10,12 Z', col); rr(-46, 38, 92, 6, 3, '#999'); rr(-46, 38, 70, 6, 3, col); ctx.restore(); return; }
  if (name === 'hoodie') { pth('M-34,-20 C-30,-42 30,-42 34,-20 L48,34 L28,36 L24,-2 L24,44 L-24,44 L-24,-2 L-28,36 L-48,34 Z', col); ell(0, -22, 14, 11, 0, '#ececec'); ctx.restore(); return; }
  if (name === 'clock') { circS(0, 0, 40, col, 6); ln(0, 0, 0, -24, 5, col); ln(0, 0, 18, 10, 5, col); ctx.restore(); return; }
  ctx.restore(); return _pageIcon(name, x, y, col);
};

// ---------- hook ----------
const ANKLE = [SPOT.x - 0.1, SPOT.z + 0.03];
const hoodieMe = (p = {}) => ({ pose: poseOf(p), o: { top: HOOD_C, hood: true } });
S.h1 = (t, seg) => {
  // frame 0: tomorrow's clip, already playing: you on the rug, and the grey arm out from under the sofa, around your ankle
  const tn = wt(seg, 'not');
  feed(t, { z: zk(t, 0, seg.end + 0.6, 1.45, 1.6), focus: [SPOT.x - 0.2, 0.55, SPOT.z - 0.35], clock: T302 + 14 + t, people: [hoodieMe({ look: 0.6 })],
    thing: { eye: 1 }, arm: { k: 1, to: ANKLE, grip: true, over: true }, bar: 0.92 + 0.02 * t / 6 });
  if (t >= tn) pop(t, tn, 1420, 230, () => tag('DO NOT BE HOME AT 3 AM', 1420, 240, C.red, 50, 'center'), 0.3);
};
// the three "do not"s as a teaser: each one is done anyway, you see what happens, then black
function h2Windows(seg) { return [[seg.start, wt(seg, 'do', 2), 'play', 'watch', 250], [wt(seg, 'do', 2), wt(seg, 'do', 3), 'hoodie', 'wear', 250], [wt(seg, 'do', 3), nextStart(seg), 'home', 'go', 250]]; }
const H2_HIT = 0.6, H2_BLACK = 0.4;
function teaserBox(t, seg, w0, ic, word, y) {
  const x = 1580, tx = wt(seg, word);
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(x - 140, y - 130, 280, 260, 22, '#000'); ctx.restore(); rrS(x - 140, y - 130, 280, 260, 22, C.fig, 5); icon4(ic, x, y, 0.95); }, 0.3);
  redX(x, y, 105, prog(t, tx + 0.25, 0.3));
}
S.h2 = (t, seg) => {
  const ws = h2Windows(seg); let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, ic, word, by] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit;
  if (t < blk) {
    const reach = ease(prog(t, hit - 0.35, 0.35));
    if (i === 0) {
      // you watch to the end: the bar races to the end, and the arm comes for you
      feed(t, { z: zk(t, w0, blk - w0, 1.05, 1.3), focus: [SPOT.x, 0.6, SPOT.z - 0.3], clock: T302 + 6 + (t - w0) * 20, people: [hoodieMe({})], thing: { eye: 1 }, arm: { k: reach, to: ANKLE, grip: reach > 0.95, over: true }, bar: ease(prog(t, w0, hit - w0)) });
    } else if (i === 1) {
      // you in the grey hoodie: it knows you by that
      feed(t, { z: zk(t, w0, blk - w0, 1.1, 1.45), focus: [SPOT.x, 1.0, SPOT.z], clock: T302 + 20 + (t - w0), people: [{ pose: poseOf({}), o: { top: HOOD_C, hood: true, mark: t > w0 + 0.3 } }], thing: { eye: 1 }, arm: { k: reach, to: ANKLE, grip: reach > 0.95, over: true } });
    } else {
      // you go back to check: the front door opens on the dark room, and under the sofa an eye turns to you
      const op = ease(prog(t, w0, 0.6)), hd = prog(t, w0 + 0.5, hit - w0 - 0.5);
      feed(t, { z: zk(t, w0, blk - w0, 1.1, 1.6), focus: [THING_X, 0.2, SOFA.z1], date: 'TODAY', clock: T302 + 300 + (t - w0), doorOpen: op, people: [{ pose: poseOf({ x: (FDOOR.x0 + FDOOR.x1) / 2, z: 0.35 + 0.4 * op, yaw: Math.PI, walk: true, step: t * 6 }) }], thing: { eye: 1, head: hd } });
      if (d > 0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.45 * clamp(d / 0.2); ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    }
    if (i < 2) redFlash(t, hit, 0.12);
  }
  blackAfter(t, blk);
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); teaserBox(t, seg, w0, ic, word, by); ctx.restore();
};

// ---------- rule 1: do not watch it to the end ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT WATCH IT TO THE END');
S.a1 = (t, seg) => {
  // 3:02 AM: the phone on the nightstand lights up
  const tn = wt(seg, 'notification'), tm = wt(seg, 'motion');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08, W / 2, 470, () => {
    phone(960, 520, 0.95, () => lockScreen(t, { notif: tm - 0.2 }), { bright: prog(t, tn - 0.5, 0.3) * 0.9 + 0.1 });
  });
  if (t >= tm) pop(t, tm, 1480, 300, () => tag('3:02 AM', 1480, 310, C.red, 54, 'center'));
};
function bed2(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.2)', 16);
  rr(-260, -40, 520, 60, 10, '#3a3a3e'); rr(-280, -150, 26, 190, 8, '#555'); rr(254, -90, 26, 130, 8, '#555');
  rr(-240, -64, 120, 34, 14, C.sec); ell(-160, -88, 44, 40, 0, C.fig); rr(-150, -76, 400, 44, 18, '#d6d6da');
  noGlow(); if (o.awake) { ell(-140, -96, 6, 8, 0, '#000'); ell(-166, -98, 6, 8, 0, '#000'); }
  ctx.restore();
}
S.a2 = (t, seg) => {
  const tb = wt(seg, 'bed'), te = wt(seg, 'empty');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, W / 2, 470, () => {
    slideIn(t, seg.start, -40, 0, () => { bed2(470, 560, 1.15, { awake: true }); text('YOU', 470, 720, '900 48px M', C.fig); });
    slideIn(t, te - 0.6, 40, 0, () => { feed(t, { rect: { x: 980, y: 300, w: 800 }, date: 'TODAY', clock: T302 + (t - seg.start) }); text('LIVING ROOM', 1380, 790, '900 48px M', C.fig); });
  });
  if (t >= te) pop(t, te, 1380, 250, () => tag('EMPTY', 1380, 260, C.fig, 50, 'center'));
};
S.a3 = (t, seg) => {
  const ts = wt(seg, 'sofa'), tl = wt(seg, 'lamp'), td = wt(seg, 'door');
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06), clock: T302 + (t - seg.start), date: '' + 'TOMORROW' });
  feedTag(t, ts, 'SOFA', [-0.4, SOFA.back, 0.3], 'rel', [0, -170]);
  feedTag(t, tl, 'LAMP', [LAMP.x, 1.5, LAMP.z], 'rel', [-170, -40]);
  feedTag(t, td, 'FRONT DOOR', [(FDOOR.x0 + FDOOR.x1) / 2, 1.3, 0], 'rel', [-60, -230]);
};
S.a4 = (t, seg) => {
  // the date in the corner: zoom on it, and it is tomorrow
  const tc = wt(seg, 'corner'), tt = wt(seg, "tomorrow's"), z = ease(prog(t, tc - 0.3, 0.9));
  cam(t, seg.start, 0.01, 1, 1, W / 2, H / 2, () => {
    ctx.save(); ctx.translate(1600, 890); ctx.scale(lerp(1, 2.6, z), lerp(1, 2.6, z)); ctx.translate(-1600, -890);
    feed(t, { clock: T302 + (t - seg.start), date: 'TOMORROW' }); ctx.restore();
  });
  if (t >= tt) { pop(t, tt, 760, 300, () => tag("TOMORROW'S DATE", 760, 310, C.red, 54, 'center')); redFlash(t, tt, 0.06); }
};
// you walk into the room in the clip, from the hall at the front left, to the rug
const walkIn = (t, t0, d = 2.6) => { const k = ease(prog(t, t0, d)); return poseOf({ x: lerp(-2.0, SPOT.x, k), z: lerp(4.1, SPOT.z, k), yaw: lerp(-0.5, 0, k), walk: k > 0 && k < 1, step: t * 7, L: [-0.22, 0.8, 0.1 * Math.sin(t * 7) * (k < 1)], R: [0.22, 0.8, -0.1 * Math.sin(t * 7) * (k < 1)] }); };
S.a5 = (t, seg) => {
  const tw = wt(seg, 'walks'), ty = wt(seg, 'you');
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.15), focus: [SPOT.x, 1, SPOT.z], clock: T302 + 8 + (t - tw), people: t > tw - 0.4 ? [{ pose: walkIn(t, tw - 0.4), o: { top: HOOD_C, hood: true } }] : [], bar: 0.03 + 0.01 * (t - seg.start) });
  if (t >= ty) { const j = skeleton(walkIn(t, tw - 0.4)); feedTag(t, ty, 'YOU', j.head, 1300, 260, C.red, 56); }
};
S.a6 = (t, seg) => {
  const tw = wt(seg, 'why'), tk = wt(seg, 'keep');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08, 760, 520, () => {
    phone(760, 540, 1.0, () => appScreen(t, { clock: T302 + 20 + (t - seg.start), people: [hoodieMe({})], bar: 0.08 + 0.01 * (t - seg.start), playing: true }));
    if (t >= tw) bubble(1150, 330, 170, 130, '?', t, tw);
  });
  if (t >= tk) slideIn(t, tk, 40, 0, () => xTag('KEEP WATCHING', 1420, 640, 48, prog(t, tk + 0.3, 0.3)));
};
S.a7 = (t, seg) => {
  // the bar fills; at the end the clip turns from a recording into a schedule
  const t0 = seg.start, te = wt(seg, 'end'), ts = wt(seg, 'schedule'), p = ease(prog(t, t0 + 0.2, te - t0));
  cam(t, t0, seg.end - t0 + 0.8, 1, 1.04, W / 2, 470, () => {
    const x0 = 360, x1 = 1560, y = 520;
    rr(x0, y - 9, x1 - x0, 18, 9, '#2a2a2e'); ctx.save(); redGlow(16); rr(x0, y - 9, (x1 - x0) * p, 18, 9, C.red); ctx.restore(); circ(x0 + (x1 - x0) * p, y, 26, C.fig);
    text('0:00', x0, y + 80, '600 40px Plex', C.sec, 'left'); text('4:00', x1, y + 80, '600 40px Plex', C.sec, 'right');
    const rec = 1 - prog(t, ts - 0.2, 0.3);
    if (rec > 0) { ctx.save(); ctx.globalAlpha *= rec; redGlow(10); circ(x0 + 14, 360, 16, C.red); noGlow(); text('RECORDING', x0 + 44, 375, '900 46px M', C.fig, 'left'); ctx.restore(); }
    if (t >= ts - 0.2) pop(t, ts - 0.2, 960, 340, () => { ctx.save(); redGlow(20); rrS(x0, 290, 300, 110, 12, C.red, 6); ctx.restore(); rr(x0, 290, 300, 30, 0, C.red); text('03:02', x0 + 150, 380, '900 52px M', C.red); text('SCHEDULED', x0 + 340, 375, '900 58px M', C.red, 'left'); });
  });
};
S.a8 = (t, seg) => {
  const tc = wt(seg, 'close'), td = wt(seg, 'delete'), ta = wt(seg, 'as'), close = ease(prog(t, wt(seg, 'minute') + 0.1, 0.4));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, 760, 520, () => {
    ctx.save(); ctx.translate(760, 540); ctx.scale(lerp(1, 0.2, close), lerp(1, 0.2, close)); ctx.globalAlpha *= 1 - close * 0.9; ctx.translate(-760, -540);
    phone(760, 540, 1.0, () => appScreen(t, { clock: T302 + 60, people: [hoodieMe({})], bar: lerp(0.15, 0.25, prog(t, seg.start, tc - seg.start + 1)), limit: 0.25, playing: false }));
    ctx.restore();
    if (close > 0.5) phone(760, 540, 1.0, () => lockScreen(t, { time: '3:15' }), { bright: 0.5 });
  });
  if (t >= tc) slideIn(t, tc, 40, 0, () => { text('STOP AT', 1420, 300, '900 46px M', C.fig); text('1:00', 1420, 380, '900 80px M', '#ffd34d'); });
  if (t >= td) slideIn(t, td, 40, 0, () => xTag('DELETE', 1420, 520, 50, prog(t, td + 0.3, 0.3)));
  if (t >= ta) pop(t, ta, 1420, 700, () => tag('NO ENDING', 1420, 710, C.fig, 50, 'center'));
};
// if you watch to the end: the arm, the ankle, the fall, and you are pulled under the sofa
S.a9 = (t, seg) => {
  // the arm comes out, closes on your ankle and yanks it; you go down on your back and are pulled feet first into the dark under the sofa
  const gr = evAfter('grab', seg.end), dr = evAfter('drag', seg.end);
  const tg = gr ? gr.t : seg.end + 0.8, td = dr ? dr.t : seg.end + 1.5;
  const reach = ease(prog(t, tg - 0.45, 0.45)), yank = easeOut(prog(t, tg, td - tg)), fallen = t >= td;
  const p = prog(t, td + 0.12, 1.35), pull = p * p * (1.6 - 0.6 * p);   // slow at first, then it takes you all at once
  const fx = SPOT.x - 0.1, fz = lerp(SPOT.z + 0.15, SOFA.z1 - 1.75, pull);
  const standing = { pose: poseOf({ look: lerp(0.2, -0.6, yank), lean: -0.35 * yank, footL: [lerp(ANKLE[0], ANKLE[0] + 0.05, yank), 0.05 + 0.1 * yank, lerp(ANKLE[1], ANKLE[1] - 0.35, yank)],
    L: [-0.3 - 0.1 * yank, 0.8 + 0.7 * yank, 0.1], R: [0.3 + 0.1 * yank, 0.8 + 0.75 * yank, 0.1] }), o: { top: HOOD_C, hood: true } };
  const feetZ = fz, armOut = !fallen || feetZ > SOFA.z1 + 0.02;
  feed(t, { z: zk(t, seg.start, td - seg.start + 1.4, 1.1, 1.45), focus: [SPOT.x, 0.35, (SPOT.z + SOFA.z1) / 2 + 0.2], clock: T302 + 236 + (t - seg.start), bar: lerp(0.97, 1, prog(t, seg.start, td - seg.start)),
    shift: fallen ? 0.6 * (1 - p) : 0, people: fallen ? [] : [standing], thing: { eye: 1 },
    arm: !armOut ? null : fallen ? { k: 1, to: [fx, feetZ], grip: true, over: false } : { k: reach, to: [standing.pose.footL ? standing.pose.footL[0] : ANKLE[0], standing.pose.footL ? standing.pose.footL[2] : ANKLE[1]], grip: reach > 0.95, over: true },
    lying: fallen && pull < 1 ? [{ x: fx, z: fz, a: 0, under: false, o: { top: HOOD_C, clipZ: SOFA.z1 - 0.02, reach: 1, wig: t * 16 } }] : [],
    front: () => { if (fallen) { ctx.save(); ctx.globalAlpha = 0.6; for (let i = 0; i < 4; i++) { const x = SPOT.x - 0.32 + i * 0.07 + (i > 1 ? 0.12 : 0); lnW([x, 0.006, Math.max(SOFA.z1, fz + 1.5)], [x, 0.006, SPOT.z + 1.5], 3, '#8a8a90'); } ctx.restore(); } } });
  redFlash(t, tg, 0.1);
};

// ---------- rule 2: do not wear what you wear in it ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT WEAR WHAT YOU WEAR IN IT');
S.b1 = (t, seg) => {
  const to = wt(seg, 'only');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06, 760, 520, () => {
    phone(760, 540, 1.0, () => appScreen(t, { clock: T302 + 9 + (t - seg.start), people: [{ pose: walkIn(t, seg.start - 1.5), o: { top: HOOD_C, hood: true } }], bar: prog(t, seg.start, 3) * 0.24, limit: 0.25, playing: true }));
  });
  if (t >= to) pop(t, to, 1420, 380, () => tag('FIRST MINUTE ONLY', 1420, 390, '#ffd34d', 46, 'center'));
};
S.b2 = (t, seg) => {
  // in the clip: the grey hoodie. Then the real room: the same hoodie on your chair
  const tg = wt(seg, 'grey'), to = wt(seg, 'one'), real = t >= to - 0.1;
  if (!real) { feed(t, { z: zk(t, seg.start, to - seg.start, 1.2, 1.6), focus: [SPOT.x, 1.2, SPOT.z], clock: T302 + 30, people: [hoodieMe({})] });
    if (t >= tg) { const j = skeleton(poseOf({})); feedTag(t, tg, 'GREY HOODIE', j.chest, 1360, 260, C.fig, 48); } }
  else { view(t, to - 0.1, seg.end - to + 0.9, 1.35, 1.6, [CHAIR.x, 0.7, CHAIR.z], { cam: CAMS.chair, hoodie: 'hang', lamp: 1, moon: 1 });
    pop(t, to + 0.2, 1420, 280, () => tag('RIGHT NOW', 1420, 290, C.red, 54, 'center')); }
};
S.b3 = (t, seg) => {
  const tf = wt(seg, 'faces'), th = wt(seg, 'hoodie');
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.6, 1.9), focus: [SPOT.x, 1.25, SPOT.z], clock: T302 + 31, people: [{ pose: poseOf({}), o: { top: HOOD_C, hood: true, mark: t >= th } }] });
  const hp = feedPt(skeleton(poseOf({})).head);
  if (hp && t >= tf) pop(t, tf, hp[0], hp[1], () => { ctx.save(); ctx.globalAlpha *= 0.95; rr(hp[0] - 70, hp[1] - 70, 140, 140, 10, '#2a2a2e'); ctx.globalAlpha = 0.6; ctx.drawImage(grainC[Math.floor(t * 20) % 4], hp[0] - 70, hp[1] - 70, 140, 140); ctx.restore(); text('?', hp[0], hp[1] + 30, '900 90px M', C.fig); });
  if (t >= tf) slideIn(t, tf, 40, 0, () => xTag('FACE', 1500, 330, 50, prog(t, tf + 0.3, 0.3)));
  if (t >= th) pop(t, th, 1500, 470, () => tag('HOODIE', 1500, 480, C.red, 54, 'center'));
};
// a street at night: lamp post, the bin, you throwing the hoodie in
function street(t, o = {}) {
  rr(0, 760, W, 320, 0, '#101012'); ln(0, 760, W, 760, 4, '#2c2c30');
  for (let x = 0; x < W; x += 240) ln(x, 900, x + 120, 900, 6, '#26262a');
  ctx.save(); glow('rgba(255,226,170,0.8)', 40); ln(1460, 760, 1460, 250, 12, '#5a5a5e'); ln(1460, 250, 1380, 250, 10, '#5a5a5e'); rr(1340, 248, 80, 22, 8, '#ffe2aa'); ctx.restore();
  const g = ctx.createRadialGradient(1380, 300, 10, 1380, 600, 520); g.addColorStop(0, 'rgba(255,226,170,0.14)'); g.addColorStop(1, 'rgba(255,226,170,0)'); ctx.fillStyle = g; ctx.fillRect(900, 250, 1000, 600);
  ctx.save(); glow('rgba(255,255,255,0.2)', 14); rr(1120, 560, 190, 200, 12, '#4a4a50'); rr(1104, 540, 222, 36, 10, '#5c5c62'); ctx.restore();
}
S.b4 = (t, seg) => {
  const tt = wt(seg, 'throw'), tb = wt(seg, 'bin'), k = ease(prog(t, tb - 0.2, 0.7));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06, 1100, 560, () => {
    street(t);
    person(820, 760, 0.85, C.fig, prog(t, tb - 0.3, 0.3) * (1 - prog(t, tb + 0.4, 0.3)), 0, { eye: true });
    const x = lerp(860, 1215, k), y = lerp(520, 545, k) - Math.sin(k * Math.PI) * 180;
    if (k < 1) { ctx.save(); ctx.translate(x, y); ctx.rotate(k * 4); glow('rgba(255,255,255,0.2)', 10); rr(-50, -30, 100, 60, 18, HOOD_C); ctx.restore(); }
  });
  if (t >= tt) slideIn(t, tt, 40, 0, () => tag('TONIGHT', 1560, 220, C.fig, 50, 'center'));
};
S.b5 = (t, seg) => {
  const tf = wt(seg, 'folded');
  view(t, seg.start, seg.end - seg.start + 0.8, 1.4, 1.7, [CHAIR.x, 0.6, CHAIR.z], { cam: CAMS.chair, hoodie: 'folded', sun: 0.7 });
  slideIn(t, seg.start + 0.3, 40, 0, () => text('7:00 AM', 1560, 200, '700 54px Plex', C.fig));
  if (t >= tf) pop(t, tf, 1420, 330, () => tag('FOLDED', 1420, 340, C.red, 60, 'center'));
};
S.b6 = (t, seg) => {
  const tp = wt(seg, 'put'), tb = wt(seg, 'bright'), tn = wt(seg, 'never');
  setCam(CAMS.side);
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, W / 2, 500, () => {
    const pl = { x: 0.2, z: 1.9, yaw: -2.27 };
    ctx.save(); ctx.translate(-380, -40); setCam({ ...CAMS.side, f: 760 }); slideIn(t, seg.start, -40, 0, () => body3(poseOf(pl), { top: HOOD_C, hood: true })); ctx.restore();
    if (t >= tb) { ctx.save(); ctx.translate(380, -40); setCam({ ...CAMS.side, f: 760 }); pop(t, tb, 960, 500, () => body3(poseOf(pl), { top: '#ffffff', glow: 'rgba(255,255,255,0.7)' })); ctx.restore(); }
  });
  if (t >= tp + 0.2) { redX(580, 260, 60, prog(t, tp + 0.2, 0.3)); }
  if (t >= tb) check(1340, 260, 60, prog(t, tb + 0.3, 0.3));
  if (t >= tn) pop(t, tn, 1340, 860, () => tag('NEVER SEEN', 1340, 870, C.fig, 46, 'center'));
};
S.b7 = (t, seg) => {
  const tn = wt(seg, 'not');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.04, W / 2, 470, () => {
    feed(t, { rect: { x: 120, y: 180, w: 1000 }, z: 1.3, focus: [SPOT.x, 1.0, SPOT.z], clock: T302 + 40, people: [hoodieMe({})] });
    text('THE CLIP', 620, 830, '900 48px M', C.fig);
    setCam({ ...CAMS.side, f: 760 }); ctx.save(); ctx.translate(560, -60); slideIn(t, seg.start + 0.4, 40, 0, () => body3(poseOf({ x: 0.2, z: 1.9, yaw: -2.27 }), { top: '#ffffff', glow: 'rgba(255,255,255,0.6)' })); ctx.restore();
    text('YOU', 1560, 830, '900 48px M', C.fig);
  });
  if (t >= tn) check(1560, 260, 60, prog(t, tn, 0.3));
};

// ---------- rule 3: do not be home at 3 AM ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'DO NOT BE HOME AT 3 AM');
// the outside of your front door: you lock it, the key turns
S.c1 = (t, seg) => {
  const tl = wt(seg, 'lock'), k = ease(prog(t, tl, 0.5));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08, 900, 520, () => {
    rr(0, 0, W, H, 0, '#0c0c0d'); rr(0, 860, W, 220, 0, '#141416');
    ctx.save(); glow('rgba(255,255,255,0.12)', 30); rr(640, 120, 520, 740, 6, '#26262a'); ctx.restore(); rrS(640, 120, 520, 740, 6, '#55555a', 4);
    rrS(680, 160, 440, 300, 4, '#3a3a3e', 3); rrS(680, 500, 440, 320, 4, '#3a3a3e', 3);
    circ(1100, 500, 20, '#77777c'); ctx.save(); ctx.translate(1100, 560); ctx.rotate(k * Math.PI / 2); rr(-4, -16, 8, 32, 3, '#111'); ctx.restore(); circS(1100, 560, 22, '#77777c', 5);
    // your hand on the key
    person(1340, 860, 0.9, C.fig, 0, 0, { eye: true, hand: { x: 1112, y: 566 } });
    text(NUM, 900, 230, '900 64px M', '#55555a');
  });
  slideIn(t, seg.start + 0.2, 40, 0, () => text('2:30 AM', 1560, 200, '700 54px Plex', C.fig));
  if (t >= tl + 0.4) pop(t, tl + 0.4, 1560, 340, () => tag('LOCKED', 1560, 350, C.fig, 50, 'center'));
};
// somewhere bright, with people: an all-night store window
function store(t) {
  rr(0, 0, W, H, 0, '#08080a'); rr(0, 820, W, 260, 0, '#121214');
  ctx.save(); glow('rgba(255,250,230,0.5)', 60); rr(300, 160, 1320, 560, 8, '#e9e6dc'); ctx.restore();
  for (let i = 0; i < 4; i++) rr(340 + i * 330, 200, 260, 380, 6, '#d2cfc4');
  for (let i = 0; i < 5; i++) ln(320, 260 + i * 80, 1600, 260 + i * 80, 3, '#c0bdb2');
  for (const [x, s] of [[520, 0.55], [880, 0.6], [1280, 0.52]]) person(x, 700, s, '#55555a');
  text('OPEN 24H', 960, 140, '900 54px M', '#ffd34d');
}
S.c2 = (t, seg) => {
  const to = wt(seg, 'open'), ph = ease(prog(t, to - 0.2, 0.5));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06, W / 2, 520, () => {
    store(t); person(960, 980, 0.95, C.fig, 0, 0, { eye: true });
    if (ph > 0) { ctx.save(); ctx.globalAlpha *= ph; ctx.translate(0, 80 * (1 - ph)); phone(1480, 560, 0.85, () => appScreen(t, { date: 'LIVE', clock: T302 - 1800 + (t - seg.start), bar: 1, title: 'Live' })); ctx.restore(); }
  });
};
S.c3 = (t, seg) => {
  const te = wt(seg, 'empty'), tx = wt(seg, 'except');
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08), date: 'LIVE', clock: T302 + (t - seg.start) });
  if (t >= te) pop(t, te, 960, 240, () => tag('EMPTY', 960, 250, C.fig, 54, 'center'));
  if (t >= tx) { slideIn(t, tx, 40, 0, () => { feed(t, { rect: { x: 1240, y: 520, w: 480 }, z: 1.3, focus: [SPOT.x, 1, SPOT.z], clock: T302 + 14, people: [hoodieMe({})] }); text('THE CLIP', 1480, 830, '900 34px M', C.sec); }); }
};
S.c4 = (t, seg) => {
  const tm = wt(seg, 'moves'), sh = t >= tm ? Math.max(0, 1 - (t - tm) / 0.9) : 0;
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.4), focus: [-0.4, 0.3, SOFA.z1], date: 'LIVE', clock: T302 + 9 + (t - seg.start), shift: sh });
  if (t >= tm) pop(t, tm, 1420, 260, () => tag('IT MOVED', 1420, 270, C.red, 54, 'center'));
};
S.c5 = (t, seg) => {
  const ta = wt(seg, 'arm'), tj = wt(seg, 'joint'), tj2 = wt(seg, 'joint', 2);
  const k = t < ta ? 0.15 * prog(t, seg.start + 0.6, ta - seg.start - 0.6) : t < tj ? lerp(0.15, 0.35, ease(prog(t, ta, 0.4))) : t < tj2 ? lerp(0.35, 0.6, ease(prog(t, tj, 0.4))) : lerp(0.6, 0.8, ease(prog(t, tj2, 0.4)));
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.4, 1.6), focus: [-0.3, 0.1, SOFA.z1 + 0.4], date: 'LIVE', clock: T302 + 13 + (t - seg.start), thing: { eye: 0.7 }, arm: { k, to: [SPOT.x, SPOT.z + 0.1] } });
  if (t >= tj) feedTag(t, tj, 'JOINT', armPath([THING_X, SOFA.z1 - 0.1], [SPOT.x, SPOT.z + 0.1])[3], 1420, 270, C.fig, 46);
  if (t >= tj2) feedTag(t, tj2, 'ANOTHER JOINT', armPath([THING_X, SOFA.z1 - 0.1], [SPOT.x, SPOT.z + 0.1])[5], 1420, 420, C.red, 46);
};
S.c6 = (t, seg) => {
  const ts = wt(seg, 'standing'), sweep = Math.sin((t - seg.start) * 1.6);
  const to = [SPOT.x + 0.35 * sweep, SPOT.z + 0.15 + 0.2 * Math.cos((t - seg.start) * 1.1)];
  feed(t, { z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.35, 1.5), focus: [SPOT.x, 0.3, SPOT.z - 0.3], date: 'LIVE', clock: T302 + 18 + (t - seg.start), thing: { eye: 0.7 }, arm: { k: 1, to },
    front: () => { if (t >= ts - 0.3) { ctx.save(); ctx.globalAlpha *= 0.6 * prog(t, ts - 0.3, 0.4); ctx.setLineDash([10, 10]); const j = skeleton(poseOf({}));
      const a = prj(j.head), b = prj(j.foot.L), c = prj(j.foot.R); if (a && b && c) { circS(a[0], a[1], 0.11 * a[3], C.fig, 4); ln(a[0], a[1] + 0.12 * a[3], (b[0] + c[0]) / 2, b[1], 4, C.fig); ln(b[0], b[1], c[0], c[1], 4, C.fig); } ctx.restore(); } } });
  if (t >= ts) pop(t, ts, 1420, 270, () => tag('WHERE YOU SHOULD BE', 1420, 280, C.fig, 44, 'center'));
};
S.c7 = (t, seg) => {
  const tn = wt(seg, 'nothing'), te = wt(seg, 'eye'), tc = wt(seg, 'camera'), hd = prog(t, te - 0.4, tc - te + 0.6);
  feed(t, { z: zk(t, te - 0.4, seg.end - te + 1.2, 1.4, 2.3), focus: [THING_X, 0.1, SOFA.z1 + 0.1], date: 'LIVE', clock: T302 + 26 + (t - seg.start), thing: { eye: 1, head: hd }, arm: { k: 1, to: [SPOT.x, SPOT.z + 0.15] } });
  if (t >= tn) pop(t, tn, 1420, 260, () => tag('NOTHING', 1420, 270, C.fig, 50, 'center'));
  redFlash(t, tc, 0.08);
};
S.c8 = (t, seg) => {
  const tb = wt(seg, 'black'), off = prog(t, tb - 0.15, 0.25);
  feed(t, { z: 2.3, focus: [THING_X, 0.1, SOFA.z1 + 0.1], date: 'LIVE', clock: T302 + 31 + (t - seg.start), thing: { eye: 1, head: 1 }, arm: { k: 1, to: [SPOT.x, SPOT.z + 0.15] }, noise: prog(t, seg.start, 0.6), off });
};
S.c9 = (t, seg) => {
  const tg = wt(seg, 'go'), ts = wt(seg, 'sun'), sk = ease(prog(t, ts - 0.1, 1.0));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, W / 2, 520, () => {
    store(t); person(960, 980, 0.95, C.fig, 0, 0, { eye: true });
    if (sk > 0) { ctx.save(); ctx.globalAlpha *= sk; icon('sun', 1640, lerp(420, 260, sk), 1.1); ctx.restore(); }
  });
  if (t >= tg) slideIn(t, tg, 40, 0, () => xTag('GO BACK', 330, 800, 52, prog(t, tg + 0.3, 0.3)));
  if (t >= ts) pop(t, ts, 1560, 790, () => tag('STAY UNTIL SUNRISE', 1560, 800, C.fig, 40, 'center'));
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
S.d1 = (t, seg) => {
  const tn = wt(seg, 'tonight'), flip = t >= tn - 0.05;
  cam(t, seg.start, 0.01, 1, 1, W / 2, H / 2, () => {
    ctx.save(); ctx.translate(1600, 890); ctx.scale(2.2, 2.2); ctx.translate(-1600, -890);
    feed(t, { clock: T302 + 236 + (t - seg.start), date: flip ? 'TONIGHT' : 'TOMORROW', noise: flip ? 0.4 * (1 - prog(t, tn, 0.5)) : 0, people: [hoodieMe({})], bar: 1 }); ctx.restore();
  });
  if (flip) redFlash(t, tn, 0.1);
};
S.d2 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 500, () => {
    pop(t, seg.start, 960, 450, () => { hazard(560, 260, 800, 30, t * 40); rrS(560, 300, 800, 330, 10, C.fig, 5);
      spaced('WHAT DOES NOT WORK', 960, 482, '900 50px M', C.fig, 5); hazard(560, 640, 800, 30, -t * 40); });
  });
};
// the camera, close: the plug comes out, the light turns red, it keeps recording
S.d3 = (t, seg) => {
  const tu = wt(seg, 'unplug'), tr = wt(seg, 'red'), tk = wt(seg, 'keeps'), out = ease(prog(t, tu + 0.1, 0.4));
  const cc = { x: CCTV.x - 1.0, y: CCTV.y - 0.4, z: CCTV.z - 1.1, yaw: -2.4, pitch: 0.24, f: 1700 };
  setCam(cc); const f = prj([CCTV.x, CCTV.y - 0.1, CCTV.z]) || [W / 2, H / 2];
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.15, f[0], f[1], () => {
    living(t, { cctvDev: { led: t >= tr ? 'red' : 'green' } });
    const a = prj([CCTV.x - 0.02, CCTV.y - 0.12, CCTV.z]), b = prj([CCTV.x - 0.02 - 0.3 * out, CCTV.y - 0.9 - 0.3 * out, CCTV.z - 0.1]);
    if (a && b) { ln(a[0], a[1], lerp(a[0], b[0], 0.3), b[1] - 200, 5, '#bdbdbd'); ln(lerp(a[0], b[0], 0.3), b[1] - 200, b[0], b[1], 5, '#bdbdbd'); rr(b[0] - 18, b[1] - 6, 36, 40, 6, '#e8e8e8'); }
  });
  if (t >= tu) slideIn(t, tu, 40, 0, () => xTag('UNPLUG IT', 400, 300, 50, prog(t, tu + 0.3, 0.3)));
  if (t >= tk) pop(t, tk, 400, 450, () => { ctx.save(); redGlow(12); circ(310, 452, 14, C.red); ctx.restore(); text('STILL RECORDING', 340, 466, '900 40px M', C.red, 'left'); });
};
S.d4 = (t, seg) => {
  const th = wt(seg, 'hide'), ts = wt(seg, 'second'), tb = wt(seg, 'bedroom', 2);
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06, 760, 520, () => {
    phone(760, 540, 1.0, () => appScreen(t, { clock: T302 + 60, people: [hoodieMe({})], bar: 1, clips: [['Living room', 'Tomorrow · 3:02 AM', true], ['Bedroom', 'Tomorrow · 3:04 AM', true, ts]] }));
  });
  if (t >= th) slideIn(t, th, 40, 0, () => xTag('HIDE IN THE BEDROOM', 1420, 300, 42, prog(t, th + 0.3, 0.3)));
  if (t >= tb) pop(t, tb, 1420, 470, () => tag('BEDROOM 03:04', 1420, 480, C.red, 50, 'center'));
};
S.d5 = (t, seg) => {
  const tc = wt(seg, 'call'), tf = wt(seg, 'clip'), clip = t >= tf - 0.1;
  if (!clip) cam(t, seg.start, tf - seg.start, 1.0, 1.06, 760, 520, () => {
    phone(760, 540, 1.0, () => { rr(0, 0, SW, SH, 0, '#0b0b0c'); statusBar('2:51'); circ(SW / 2, 240, 70, '#2a2a2e'); circ(SW / 2, 222, 26, '#8a8a90'); rr(SW / 2 - 40, 254, 80, 40, 20, '#8a8a90');
      text('Calling…', SW / 2, 380, `600 30px ${UI}`, '#f2f2f2'); circ(SW / 2, 680, 40, C.red); }); });
  else feed(t, { z: zk(t, tf, seg.end - tf + 0.8, 1.2, 1.4), focus: [SPOT.x, 0.2, SPOT.z - 0.3], clock: T302 + 200, thing: { eye: 1 },
    lying: [{ x: SPOT.x - 0.1, z: SPOT.z - 0.4, a: 0.3, o: { col: '#d8d8dc' } }], arm: { k: 1, to: [SPOT.x - 0.1, SPOT.z - 0.4], grip: true, over: true } });
  if (t >= tc && !clip) slideIn(t, tc, 40, 0, () => xTag('CALL SOMEONE', 1420, 300, 46, prog(t, tc + 0.3, 0.3)));
  if (clip) pop(t, tf + 0.3, 1420, 260, () => tag('THEM, NOT YOU', 1420, 270, C.red, 50, 'center'));
};
S.d6 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, W / 2, 470, () => {
    pop(t, seg.start, 960, 470, () => { glow(); rrS(860, 370, 200, 200, 18, C.fig, 8); noGlow(); });
    check(960, 470, 64, prog(t, seg.end - 0.5, 0.4));
    fadeIn(t, seg.start + 0.3, () => spaced('ONLY ONE', 960, 680, '900 44px M', C.fig, 10));
  });
};
// the floor plan from above: the camera's cone of view, and the thing waiting at its edge
S.d7 = (t, seg) => {
  const te = wt(seg, 'edge'), tl = wt(seg, 'looking');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, W / 2, 500, () => {
    const X = x => 1000 + x * 190, Z = z => 120 + z * 175;
    rrS(X(ROOM.x0), Z(0), (ROOM.x1 - ROOM.x0) * 190, ROOM.z1 * 175, 6, C.mid, 4);
    ctx.save(); ctx.beginPath(); ctx.rect(X(ROOM.x0), Z(0), (ROOM.x1 - ROOM.x0) * 190, ROOM.z1 * 175); ctx.clip();
    rr(X(SOFA.x0), Z(SOFA.z0), (SOFA.x1 - SOFA.x0) * 190, (SOFA.z1 - SOFA.z0) * 175, 10, '#3a3a3e'); text('SOFA', X((SOFA.x0 + SOFA.x1) / 2), Z(0.62), '900 34px M', C.sec);
    // the cone: it sweeps a little; the thing (a red dot) moves only where the cone is not
    const cx = X(CCTV.x), cz = Z(CCTV.z), dir = -2.3 + 0.35 * Math.sin((t - seg.start) * 1.2), half = 0.42;
    ctx.save(); ctx.globalAlpha = 0.16; ctx.beginPath(); ctx.moveTo(cx, cz); ctx.arc(cx, cz, 1500, dir - half, dir + half); ctx.closePath(); ctx.fillStyle = C.fig; ctx.fill(); ctx.restore();
    ln(cx, cz, cx + Math.cos(dir - half) * 1500, cz + Math.sin(dir - half) * 1500, 3, C.sec); ln(cx, cz, cx + Math.cos(dir + half) * 1500, cz + Math.sin(dir + half) * 1500, 3, C.sec);
    ctx.restore(); ctx.save(); glow(); circ(cx, cz, 16, C.fig); ctx.restore();
    const ang = (x, z) => Math.atan2(Z(z) - cz, X(x) - cx), inCone = (x, z) => Math.abs(((ang(x, z) - dir + Math.PI * 3) % (Math.PI * 2)) - Math.PI) < half;
    const tx = -1.3 + 0.9 * ((t * 0.35) % 1), tz = SOFA.z1 + 0.25, seen = inCone(tx, tz);
    ctx.save(); redGlow(seen ? 6 : 20); circ(X(tx), Z(tz), 18, seen ? '#7a2a2a' : C.red); ctx.restore();
    if (seen) text('FROZEN', X(tx), Z(tz) - 34, '900 28px M', C.sec);
  });
  if (t >= tl) pop(t, tl, 300, 300, () => tag('NOT WATCHED = MOVES', 300, 310, C.red, 30, 'center'));
  if (t >= te) pop(t, te, 300, 430, () => tag('THE EDGE', 300, 440, C.fig, 40, 'center'));
};
// you turn the camera; its picture swings to the sofa
S.d8 = (t, seg) => {
  const tt = wt(seg, 'turn'), tp = wt(seg, 'point'), k = ease(prog(t, tt, tp - tt + 0.6));
  feed(t, { camObj: lerpCam(CAMS.cctv, CAMS.sofa, k), date: 'TONIGHT', clock: T302 - 1500 + (t - seg.start), lamp: 1, noise: Math.sin(k * Math.PI) * 0.3 });
  if (t >= tp) pop(t, tp, 1420, 260, () => tag('AT THE SOFA', 1420, 270, C.fig, 54, 'center'));
};
S.d9 = (t, seg) => {
  const ts = wt(seg, 'sit'), tl = wt(seg, 'look');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.06, 960, 520, () => {
    phone(960, 520, 1.05, () => appScreen(t, { camObj: CAMS.sofa, date: 'LIVE', clock: T302 - 900 + (t - seg.start), bar: 1, title: 'Live', lamp: 1, thing: { eye: 0 } }));
  });
  if (t >= tl) pop(t, tl, 1500, 300, () => tag('DO NOT LOOK AWAY', 1500, 310, C.red, 48, 'center'));
};
S.d10 = (t, seg) => {
  const tm = wt(seg, 'move'), ts = wt(seg, 'stop'), sh = t >= tm && t < ts ? 0.6 + 0.4 * Math.sin((t - tm) * 9) : 0;
  feed(t, { camObj: CAMS.sofa, z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.15), focus: [-0.4, 0.3, SOFA.z1], date: 'LIVE', clock: T302 + (t - seg.start), lamp: 1, shift: sh, thing: { eye: t >= tm ? 0.6 : 0 } });
  if (t >= ts) pop(t, ts, 1420, 260, () => tag('IT STOPS', 1420, 270, C.fig, 54, 'center'));
};
// the blink: your eyes and the camera's light, two tracks; they must never close together
S.d11 = (t, seg) => {
  const tw = wt(seg, 'blink'), ts = wt(seg, 'same');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1, 1.04, W / 2, 470, () => {
    const x0 = 520, x1 = 1600, ys = [380, 600];
    icon('eye', 360, ys[0], 0.7); ctx.save(); glow('rgba(160,255,190,0.9)', 10); circ(360, ys[1], 26, '#9effc0'); ctx.restore(); text('CAMERA', 360, ys[1] + 70, '900 30px M', C.sec);
    for (const y of ys) lnP(x0, y, x1, y, 5, C.dim, easeOut(prog(t, seg.start, 0.6)));
    const run = (t - seg.start) * 240;
    for (let i = 0; i < 6; i++) { const ex = x0 + ((i * 260 + run) % (x1 - x0)), cx2 = x0 + ((i * 260 + 130 + run) % (x1 - x0));
      rr(ex - 10, ys[0] - 30, 20, 60, 6, C.fig); rr(cx2 - 10, ys[1] - 30, 20, 60, 6, '#9effc0'); }
    if (t >= ts) { const x = 1060; ctx.save(); redGlow(16); rr(x - 12, ys[0] - 34, 24, 68, 6, C.red); rr(x - 12, ys[1] - 34, 24, 68, 6, C.red); ctx.restore();
      ctx.save(); ctx.setLineDash([10, 9]); ln(x, ys[0] + 40, x, ys[1] - 40, 4, C.red); ctx.restore(); redX(x + 120, (ys[0] + ys[1]) / 2, 50, prog(t, ts + 0.2, 0.3)); }
  });
  if (t >= tw) pop(t, tw, 960, 200, () => tag('NEVER AT THE SAME TIME', 960, 210, C.fig, 44, 'center'));
};
S.d12 = (t, seg) => {
  const ts = wt(seg, 'sunrise'), to = wt(seg, 'out'), sun = ease(prog(t, ts, to - ts + 0.6)), eye = 1 - prog(t, to - 0.2, 0.6);
  feed(t, { camObj: CAMS.sofa, z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.2), focus: [THING_X, 0.1, SOFA.z1], date: 'TODAY', clock: 6 * 3600 + 41 * 60 + (t - seg.start) * 20, sun, moon: 1 - sun, thing: { eye } });
};

// ---------- morning ----------
S.e1 = (t, seg) => {
  const tn = wt(seg, 'notification');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08, W / 2, 470, () => phone(960, 520, 0.95, () => lockScreen(t, { time: '7:00', morning: true, notif: tn - 0.2, sub: 'Living room · now' })));
};
S.e2 = (t, seg) => {
  const tt = wt(seg, 'tomorrow'), z = ease(prog(t, seg.start + 0.3, 0.9));
  cam(t, seg.start, 0.01, 1, 1, W / 2, H / 2, () => {
    ctx.save(); ctx.translate(1600, 890); ctx.scale(lerp(1, 2.4, z), lerp(1, 2.4, z)); ctx.translate(-1600, -890);
    feed(t, { camObj: CAMS.sofa, clock: T302 + (t - seg.start), date: 'TOMORROW', sun: 0.5, moon: 0 }); ctx.restore();
  });
  if (t >= tt) { pop(t, tt, 760, 300, () => tag('AGAIN', 760, 310, C.red, 60, 'center')); redFlash(t, tt, 0.06); }
};
S.e3 = (t, seg) => {
  const ts = wt(seg, 'sofa');
  feed(t, { camObj: CAMS.sofa, z: zk(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.1), focus: [-0.4, 0.3, SOFA.z1], clock: T302 + 4 + (t - seg.start), date: 'TOMORROW', sun: 0.5, moon: 0 });
  if (t >= ts) pop(t, ts, 1420, 260, () => tag('EMPTY', 1420, 270, C.fig, 54, 'center'));
};
S.e4 = (t, seg) => {
  // very slowly its head comes out from under the sofa and turns up to the lens: to you, watching
  const tt = wt(seg, 'turns'), tl = wt(seg, 'lens'), hd = prog(t, tt - 0.3, tl - tt + 0.6);
  feed(t, { camObj: CAMS.sofa, z: zk(t, seg.start, seg.end - seg.start + 1.6, 1.1, 3.2), focus: [THING_X, 0.12, SOFA.z1 + 0.2], clock: T302 + 9 + (t - seg.start), date: 'TOMORROW', sun: 0.5, moon: 0, thing: { eye: 1, head: hd } });
  redFlash(t, tl, 0.06);
};
// the file closes
S.e5 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore();
  });
};
// sign-off: the rules once more, the stamp, and the picture sinks into the dark around it
S.e6 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts, dk = ease(prog(t, ts + 0.5, 1.0));
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9] });
    if (dk > 0) { ctx.save(); ctx.globalAlpha = 0.95 * dk; ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
    if (t >= ts) { ctx.save(); redGlow(lerp(0, 40, dk)); stampMark(t, ts, 960, 540, [['FOLLOW', 96], ['THE RULES', 96]], -0.12, dk > 0.02 ? 'rgba(0,0,0,0)' : '#ececec', 12); ctx.restore(); }
    ctx.restore();
  });
};
// ---------- HUD, captions, texture ----------
let grainC = null, vig = null;
function initTex() {
  grainC = [0, 1, 2, 3].map(() => { const g = document.createElement('canvas'); g.width = 480; g.height = 270; const gx = g.getContext('2d');
    const im = gx.createImageData(480, 270); for (let i = 0; i < im.data.length; i += 4) { const v = Math.random() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    gx.putImageData(im, 0, 0); return g; });
}
function chunks(seg) {
  if (seg._ch) return seg._ch;
  const out = []; let cur = [];
  const ws = seg.words;
  ws.forEach((w, i) => { cur.push(w); const endsNext = ws[i + 1] && /[.?!]$/.test(ws[i + 1].w);   // never leave one word alone: a sentence that ends on the next word keeps it
    if (/[.?!]$/.test(w.w) || (cur.length >= 4 && /,$/.test(w.w)) || (cur.length >= 10 && !endsNext)) { out.push(cur); cur = []; } });
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
  // dark band only where the scene behind the caption is bright (white bed, body)
  const tw = ctx.measureText(s).width + 60, px = ctx.getImageData(960 - tw / 2, 958, tw, 56).data;
  let lum = 0; for (let i = 0; i < px.length; i += 16) lum += px[i]; lum /= px.length / 16;
  if (lum > 50) { ctx.fillStyle = `rgba(0,0,0,${Math.min(0.72, 0.35 + (lum - 50) / 200)})`; ctx.beginPath(); ctx.roundRect(960 - tw / 2, 958, tw, 56, 10); ctx.fill(); }
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
    if (e.type === 'meow1' || e.type === 'meow2') { if (d > 0 && d < 2.8) I = Math.max(I, 0.2 + 0.2 * Math.abs(Math.sin(d * 7))); }
    if (e.type === 'boom' && d > 0 && d < 0.4) I = Math.max(I, 0.8 * (1 - d / 0.4));
    if (e.type === 'error' && d > -0.1 && d < 1.6) I = Math.max(I, d < 0.25 ? 0.9 : 0.3);
    if (e.type === 'tapestop' && d > 0 && d < 0.8) I = Math.max(I, 0.7);
    if (e.type === 'morph' && d > 0 && d < 0.75) I = Math.max(I, d < 0.5 ? 0.85 : 0.85 * (1 - (d - 0.5) / 0.25));
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
  (S[seg.id] || S.h1)(t, seg);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; noGlow();
  glitch(t, f);
  interfere(t, f, disturbance(t));
  caption(t, seg);
  ctx.globalAlpha = 0.07; ctx.drawImage(grainC[f % 4], 0, 0, W, H); ctx.globalAlpha = 1;
  const by = ((t * 90) % (H + 300)) - 150, bg = ctx.createLinearGradient(0, by - 80, 0, by + 80);
  bg.addColorStop(0, 'rgba(255,255,255,0)'); bg.addColorStop(0.5, 'rgba(255,255,255,0.025)'); bg.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = bg; ctx.fillRect(0, by - 80, W, 160);
  if (!vig) { vig = ctx.createRadialGradient(W / 2, H / 2, H * 0.38, W / 2, H / 2, H * 1.05); vig.addColorStop(0, 'rgba(0,0,0,0)'); vig.addColorStop(0.6, 'rgba(0,0,0,0.32)'); vig.addColorStop(1, 'rgba(0,0,0,0.82)'); }
  ctx.fillStyle = vig; ctx.fillRect(0, 0, W, H);
  // blackouts: the screen dies until the next line starts
  for (const e of window.TL.events) if (e.type === 'blackout' && t >= e.t) {
    const nx = segs.find(sg => sg.start > e.t); if (!nx || t < nx.start - 0.001) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); }
  }
};
})();

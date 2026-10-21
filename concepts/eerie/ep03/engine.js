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
  text('FILE 404', P.x + 160, P.y - 6, '900 28px M', '#333');
  rr(P.x, P.y + 40, P.w, 130, 0, '#111');
  spaced(NAME, P.x + P.w / 2, P.y + 128, '900 62px M', C.fig, 14);
  const rows = [['SUBJECT', null], ['LOCATION', 'YOUR BATHROOM'], ['TIME', '03:00 AM']];
  rows.forEach(([l, v], i) => { const y = P.y + 270 + i * 82;
    text(l, P.x + 60, y, '600 28px Plex', '#666', 'left'); ln(P.x + 250, y + 12, P.x + P.w - 60, y + 12, 2, '#bbb');
    if (v === null) rr(P.x + 260, y - 30, 330, 40, 3, '#111');
    else { ctx.save(); ctx.filter = 'blur(9px)'; text(v, P.x + 262, y, '900 36px M', i === 2 ? '#d61f1f' : '#111', 'left'); ctx.restore(); } });   // classified: blurred
  // barcode and a hazard edge
  for (let i = 0; i < 40; i++) { const bw = hash(i * 1.7) < 0.35 ? 6 : 3; rr(P.x + P.w - 300 + i * 6.4, P.y + P.h - 170, bw, 70, 0, '#111'); }
  text('NO. 0404', P.x + P.w - 172, P.y + P.h - 74, '600 24px Plex', '#444');
  text('DO NOT REMOVE FROM THE BATHROOM', P.x + 60, P.y + P.h - 130, '600 22px Plex', '#666', 'left');
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
const RULES = [['mirror', 'DO NOT TEST IT', '', ['DO NOT TEST', 'YOUR REFLECTION']], ['door', 'DO NOT LOOK BEHIND IT', '', ['DO NOT LOOK', 'BEHIND IT']], ['run', 'WHEN IT WRITES, RUN', '', ['WHEN IT WRITES,', 'RUN']], ['warn', 'EMERGENCY PROTOCOL', 'HOW TO FIGHT BACK']];
// the index page. o.rowT[i]: when row i slides in; o.fillT[i]: when its content is written; o.hot: rule 4 armed 0..1; o.struck[i]; o.dim
function rulePage(t, o) {
  const pc = '#ececec';
  glow('rgba(255,255,255,0.2)', 30); rr(P.x, P.y, P.w, P.h, 8, pc); noGlow();
  for (let i = 0; i < 3; i++) circ(P.x + 26, P.y + 220 + i * 230, 10, '#0b0b0b');
  text(NAME + ' 404', P.x + 60, P.y + 72, '900 42px M', '#111', 'left');
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
    stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], ['404', 150]], -0.1);
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
      stampMark(t, -9, P.x + 300, P.y + 610, [[NAME, 38], ['404', 150]], -0.1); ctx.restore(); }
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
}// ---------- EP03: the bathroom, built in 3D so the mirror obeys the law of reflection ----------
// World in metres. x: to the right as you face the mirror, y: up, z: out of the mirror into the room. The glass is the plane z = 0.
// The mirror shows the room reflected through that plane (z -> -z). Seen from in front, left and right stay where they are and only depth flips:
// the watch on your left wrist is on the same side of the picture in the reflection, which makes it your reflection's right wrist.
const MIR = { x0: -0.6, x1: 0.6, y0: 1.05, y1: 2.0 };          // the glass
const ROOM = { x0: -1.25, x1: 1.25, y1: 2.45, z1: 3.3 };       // floor y = 0, mirror wall z = 0, door wall z = z1
const DOOR = { x0: -0.15, x1: 0.65, h: 2.05 };                // the door, in the wall behind you
const CTR = { x0: -0.85, x1: 0.85, y: 0.88, z: 0.55 };          // the counter under the mirror
const SINK = { x: 0, z: 0.3, rx: 0.25, rz: 0.16 };
const ME = { x: -0.05, z: 0.72 };                              // where you stand at the sink
const CAMS = {
  ots: { x: 0.5, y: 1.75, z: 2.0, yaw: 0.2, pitch: -0.05, f: 1250 },     // over your right shoulder, at the mirror
  door: { x: 0.45, y: 1.62, z: 3.15, yaw: 0.06, pitch: -0.06, f: 1000 }, // from the doorway: you face the camera, the mirror behind you
  otsL: { x: -0.8, y: 1.85, z: 2.35, yaw: -0.3, pitch: -0.1, f: 1250 },   // over your left shoulder
  rev: { x: 0.3, y: 2.3, z: 0.05, yaw: Math.PI - 0.06, pitch: -0.45, f: 720 }   // from above the mirror, looking back into the room
};
let CAM = null;
function setCam(c) { CAM = { ...c, cyw: Math.cos(c.yaw || 0), syw: Math.sin(c.yaw || 0), cp: Math.cos(c.pitch || 0), sp: Math.sin(c.pitch || 0) }; }
const lerpCam = (a, b, k) => { const o = {}; for (const key of ['x', 'y', 'z', 'yaw', 'pitch', 'f']) o[key] = lerp(a[key], b[key], k); return o; };
setCam(CAMS.ots);
const V3 = { add: (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], sub: (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], mul: (a, k) => [a[0] * k, a[1] * k, a[2] * k],
  dot: (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2], len: a => Math.hypot(a[0], a[1], a[2]), lerp: (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)] };
V3.norm = a => V3.mul(a, 1 / (V3.len(a) || 1));
const MIRROR = p => [p[0], p[1], -p[2]];
// camera space: right, up, depth (forward is -z at yaw 0; positive yaw turns left, positive pitch looks up)
function toCam(p) {
  const dx = p[0] - CAM.x, dy = p[1] - CAM.y, dz = p[2] - CAM.z;
  const xc = dx * CAM.cyw - dz * CAM.syw, f0 = -dx * CAM.syw - dz * CAM.cyw;
  return [xc, dy * CAM.cp - f0 * CAM.sp, f0 * CAM.cp + dy * CAM.sp];
}
const camToScr = c => { const s = CAM.f / c[2]; return [W / 2 + c[0] * s, H / 2 - c[1] * s, c[2], s]; };
function prj(p) { const c = toCam(p); return c[2] < 0.03 ? null : camToScr(c); }
const camPos = () => [CAM.x, CAM.y, CAM.z];
// a flat polygon in the world, clipped at the near plane
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
// a circle lying in a plane: centre, two axis vectors
function ringPts(c, u, v, n = 28) { const out = []; for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; out.push(V3.add(c, V3.add(V3.mul(u, Math.cos(a)), V3.mul(v, Math.sin(a))))); } return out; }

// ---------- the room ----------
const WALL_C = '#111113', SIDE_C = '#0c0c0d', FLOOR_C = '#161616', CEIL_C = '#070707', EDGE_C = '#2c2c2e', TILE_C = '#1d1d20';
// m: 1 to draw the reflected room (inside the mirror). o.door: 0 closed .. 1 wide open
function room3(m, o = {}) {
  const T = m ? MIRROR : (p => p), z1 = ROOM.z1, { x0, x1, y1 } = ROOM;
  const P = a => polyW(a.map(T), null, null);
  // door wall (behind you; in the mirror it is the far wall)
  polyW([[x0, 0, z1], [x1, 0, z1], [x1, y1, z1], [x0, y1, z1]].map(T), WALL_C, EDGE_C, 2);
  for (let y = 0.3; y < 1.25; y += 0.3) lnW(T([x0, y, z1]), T([x1, y, z1]), 1.5, TILE_C);
  // floor, ceiling, side walls
  polyW([[x0, 0, 0], [x1, 0, 0], [x1, 0, z1], [x0, 0, z1]].map(T), FLOOR_C, EDGE_C, 2);
  for (let x = x0 + 0.42; x < x1; x += 0.42) lnW(T([x, 0, 0]), T([x, 0, z1]), 1.5, '#222');
  for (let z = 0.42; z < z1; z += 0.42) lnW(T([x0, 0, z]), T([x1, 0, z]), 1.5, '#222');
  polyW([[x0, y1, 0], [x1, y1, 0], [x1, y1, z1], [x0, y1, z1]].map(T), CEIL_C, EDGE_C, 2);
  for (const x of [x0, x1]) { polyW([[x, 0, 0], [x, 0, z1], [x, y1, z1], [x, y1, 0]].map(T), SIDE_C, EDGE_C, 2);
    for (let y = 0.3; y < 1.25; y += 0.3) lnW(T([x, y, 0]), T([x, y, z1]), 1.5, TILE_C); }
  // the door: frame, and the door itself swinging into the room on its hinge (x0 side)
  const op = o.door ?? 0, dz = z1 - 0.005;
  if (op > 0.01) polyW([[DOOR.x0, 0, dz], [DOOR.x1, 0, dz], [DOOR.x1, DOOR.h, dz], [DOOR.x0, DOOR.h, dz]].map(T), '#000', null);   // the dark hall beyond
  if (o.inDoor) o.inDoor();   // whatever stands in the doorway
  const a = op * 1.45, w = DOOR.x1 - DOOR.x0, ex = DOOR.x0 + w * Math.cos(a), ez = dz - w * Math.sin(a);
  polyW([[DOOR.x0, 0.01, dz], [ex, 0.01, ez], [ex, DOOR.h - 0.01, ez], [DOOR.x0, DOOR.h - 0.01, dz]].map(T), '#1f1f22', '#4a4a4e', 3);
  const kn = [lerp(DOOR.x0, ex, 0.88), 1.0, lerp(dz, ez, 0.88) - 0.02]; const kp = prj(T(kn)); if (kp) circ(kp[0], kp[1], 0.03 * kp[3], '#6a6a6e');
  polyW([[DOOR.x0 - 0.06, 0, dz], [DOOR.x0, 0, dz], [DOOR.x0, DOOR.h, dz], [DOOR.x1, DOOR.h, dz], [DOOR.x1, 0, dz], [DOOR.x1 + 0.06, 0, dz], [DOOR.x1 + 0.06, DOOR.h + 0.06, dz], [DOOR.x0 - 0.06, DOOR.h + 0.06, dz]].map(T), '#2a2a2d', '#55555a', 2);
}
// the mirror wall around the glass (real room only)
function mirrorWall() {
  const { x0, x1, y1 } = ROOM;
  polyW([[x0, 0, 0], [x1, 0, 0], [x1, y1, 0], [x0, y1, 0]], WALL_C, EDGE_C, 2);
  for (let y = 0.3; y < 1.0; y += 0.3) lnW([x0, y, 0], [x1, y, 0], 1.5, TILE_C);
  for (let x = x0 + 0.3; x < x1; x += 0.3) lnW([x, 0, 0], [x, 0.9, 0], 1.5, TILE_C);
}
const glassPts = () => [[MIR.x0, MIR.y0, 0], [MIR.x1, MIR.y0, 0], [MIR.x1, MIR.y1, 0], [MIR.x0, MIR.y1, 0]];
function clipGlass() { const sp = glassPts().map(prj); if (sp.some(q => !q)) return false; ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath(); ctx.clip(); return true; }
function mirrorFrame(o = {}) {
  polyW([[MIR.x0 - 0.03, MIR.y0 - 0.03, 0.005], [MIR.x1 + 0.03, MIR.y0 - 0.03, 0.005], [MIR.x1 + 0.03, MIR.y1 + 0.03, 0.005], [MIR.x0 - 0.03, MIR.y1 + 0.03, 0.005]], null, '#8a8a8e', 5);
  // the light bar over the mirror
  const lit = o.light ?? 1;
  ctx.save(); glow(`rgba(255,250,235,${0.8 * lit})`, 40); polyW([[-0.45, 2.06, 0.02], [0.45, 2.06, 0.02], [0.45, 2.12, 0.07], [-0.45, 2.12, 0.07]], `rgba(${Math.round(lerp(60, 250, lit))},${Math.round(lerp(60, 248, lit))},${Math.round(lerp(60, 238, lit))},1)`, null); ctx.restore();
}
// the glass itself: a faint cold tint and two highlight streaks, over whatever the mirror shows
function glassSheen(o = {}) {
  const sp = glassPts().map(prj); if (sp.some(q => !q)) return;
  ctx.save(); ctx.globalAlpha = 0.06; ctx.fillStyle = '#b8c8d0'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const a = sp[3], b = sp[1];
  ctx.save(); ctx.globalAlpha = 0.045; for (const [k, w] of [[0.28, 70], [0.36, 26]]) { const x = lerp(a[0], b[0], k); ln(x - 260, a[1] - 40, x + 260, b[1] + 40, w, '#fff', 'butt'); } ctx.restore();
}
function counter3(m) {
  const T = m ? MIRROR : (p => p), { x0, x1, y, z } = CTR;
  polyW([[x0, 0, z], [x1, 0, z], [x1, y, z], [x0, y, z]].map(T), '#1b1b1d', '#3c3c40', 2);           // cabinet front
  for (const x of [-0.42, 0, 0.42]) lnW(T([x, 0.08, z + 0.002]), T([x, y - 0.08, z + 0.002]), 2, '#333');
  polyW([[x0, y, 0], [x1, y, 0], [x1, y, z], [x0, y, z]].map(T), '#2e2e31', '#5a5a5e', 2);           // top
  // basin: an ellipse cut into the top, and its dark inside
  polyW(ringPts([SINK.x, y + 0.002, SINK.z], [SINK.rx, 0, 0], [0, 0, SINK.rz]).map(T), '#c9c9cc', null);
  polyW(ringPts([SINK.x, y + 0.003, SINK.z + 0.01], [SINK.rx * 0.82, 0, 0], [0, 0, SINK.rz * 0.78]).map(T), '#8d8d92', null);
  const dr = prj(T([SINK.x, y + 0.004, SINK.z + 0.02])); if (dr) circ(dr[0], dr[1], 0.018 * dr[3], '#3a3a3e');
  // tap: up from the back of the basin, then out over it
  const t0 = T([0, y, 0.07]), t1 = T([0, y + 0.16, 0.07]), t2 = T([0, y + 0.16, 0.17]);
  const q0 = prj(t0), q1 = prj(t1), q2 = prj(t2);
  if (q0 && q1 && q2) { ln(q0[0], q0[1], q1[0], q1[1], 0.03 * q1[3], '#d8d8dc'); ln(q1[0], q1[1], q2[0], q2[1], 0.026 * q2[3], '#d8d8dc');
    const h0 = prj(T([-0.06, y + 0.12, 0.05])), h1 = prj(T([0.06, y + 0.12, 0.05])); if (h0 && h1) ln(h0[0], h0[1], h1[0], h1[1], 0.022 * h0[3], '#bdbdc2'); }   // the handle
}
function waterStream(m, k = 1) {
  if (k <= 0) return; const T = m ? MIRROR : (p => p);
  const a = prj(T([0, CTR.y + 0.15, 0.17])), b = prj(T([0, CTR.y + 0.01, 0.2])); if (!a || !b) return;
  ctx.save(); ctx.globalAlpha *= 0.7 * k; glow('rgba(220,235,255,0.6)', 10); ln(a[0], a[1], b[0], b[1], 0.012 * a[3], '#e6f0ff', 'butt'); ctx.restore();
}

// ---------- people ----------
// a pose: { x, z, yaw (0 = facing the mirror), lean (rad), look (0..1 head down), roll (-1..1 head tilt), L/R: hand in body coords [right, up, forward],
//          step (walk phase), dir (walk), fing: 'point'|'flat' on R }
const STAND = { L: [-0.22, 0.8, 0.02], R: [0.22, 0.8, 0.02] };
const WASH = { L: [-0.07, 0.98, 0.42], R: [0.07, 0.98, 0.42], lean: 0.2, look: 1 };
function poseOf(p) { return { x: ME.x, z: ME.z, yaw: 0, lean: 0, look: 0, roll: 0, ...STAND, ...p }; }
function skeleton(ps) {
  const yaw = ps.yaw || 0, F = [-Math.sin(yaw), 0, -Math.cos(yaw)], R = [Math.cos(yaw), 0, -Math.sin(yaw)];
  const Wd = (lx, ly, lz) => [ps.x + R[0] * lx + F[0] * lz, ly, ps.z + R[2] * lx + F[2] * lz];
  const hipY = 0.95, la = ps.lean || 0;
  const up = (lx, ly, lz = 0) => { const dy = ly - hipY; return Wd(lx, hipY + dy * Math.cos(la) - lz * Math.sin(la), lz * Math.cos(la) + dy * Math.sin(la)); };
  const look = ps.look || 0, roll = ps.roll || 0;
  const head = up(0.05 * roll, 1.63 - 0.035 * look - 0.012 * Math.abs(roll), 0.045 * look);
  const j = { look, F, R, head, neck: up(0, 1.47), chest: up(0, 1.36), pelvis: up(0, 1.02), sh: { L: up(-0.19, 1.42), R: up(0.19, 1.42) } };
  j.hand = { L: Wd(...ps.L), R: Wd(...ps.R) };
  // elbows: two equal bones, bent outwards, down and back
  j.elb = {};
  for (const [s, sg] of [['L', -1], ['R', 1]]) { const S = j.sh[s], Hh = j.hand[s], d = V3.sub(Hh, S), L = V3.len(d), B = 0.31;
    const mid = V3.lerp(S, Hh, 0.5); let bend = V3.add(V3.mul(R, sg * 0.7), V3.add([0, -0.55, 0], V3.mul(F, -0.45)));
    const dn = V3.norm(d); bend = V3.norm(V3.sub(bend, V3.mul(dn, V3.dot(bend, dn))));
    j.elb[s] = L >= 2 * B ? mid : V3.add(mid, V3.mul(bend, Math.sqrt(B * B - L * L / 4))); }
  // legs, with a walk cycle
  const ph = ps.step || 0, sw = ps.walk ? 0.22 : 0;
  j.hip = { L: Wd(-0.09, 0.95, 0), R: Wd(0.09, 0.95, 0) };
  j.foot = { L: Wd(-0.1, 0.04 + Math.max(0, Math.sin(ph)) * 0.06 * (sw > 0), Math.cos(ph) * sw + 0.03), R: Wd(0.1, 0.04 + Math.max(0, -Math.sin(ph)) * 0.06 * (sw > 0), -Math.cos(ph) * sw + 0.03) };
  j.knee = { L: V3.add(V3.lerp(j.hip.L, j.foot.L, 0.5), V3.mul(F, 0.03)), R: V3.add(V3.lerp(j.hip.R, j.foot.R, 0.5), V3.mul(F, 0.03)) };
  return j;
}
// draw a body. o.mirror: draw its reflection; o.col; o.scars: red marks across the back (0..1); o.watch (default on)
function body3(ps, o = {}) {
  let j = skeleton(ps);
  if (o.mirror) { const M = MIRROR, mm = q => ({ L: M(q.L), R: M(q.R) });
    j = { ...j, look: j.look, F: [j.F[0], 0, -j.F[2]], R: [j.R[0], 0, -j.R[2]], head: M(j.head), neck: M(j.neck), chest: M(j.chest), pelvis: M(j.pelvis), sh: mm(j.sh), hand: mm(j.hand), elb: mm(j.elb), hip: mm(j.hip), foot: mm(j.foot), knee: mm(j.knee) }; }
  const col = o.col || C.fig, cp = camPos();
  const parts = [];
  const cap = (a, b, w, c = col) => parts.push({ d: (toCam(a)[2] + toCam(b)[2]) / 2, f: () => { const p = prj(a), q = prj(b); if (p && q) ln(p[0], p[1], q[0], q[1], w * (p[3] + q[3]) / 2, c); } });
  for (const s of ['L', 'R']) { cap(j.hip[s], j.knee[s], 0.13); cap(j.knee[s], j.foot[s], 0.12); }
  // torso: a rounded block from chest to pelvis
  parts.push({ d: toCam(j.chest)[2] + 0.02, f: () => { const p = prj(j.chest), q = prj(j.pelvis); if (!p || !q) return; ln(p[0], p[1], q[0], q[1], 0.29 * (p[3] + q[3]) / 2, col);
    const sl = prj(j.sh.L), sr = prj(j.sh.R); if (sl && sr) ln(sl[0], sl[1], sr[0], sr[1], 0.1 * (sl[3] + sr[3]) / 2, col);
    // scars across the back, seen only when the back faces the camera
    const back = V3.dot(j.F, V3.norm(V3.sub(cp, j.chest)));
    if (o.scars && back < -0.25) scars3(j, o.scars * clamp((-back - 0.25) / 0.3)); } });
  cap(j.neck, j.chest, 0.08);
  for (const s of ['L', 'R']) { cap(j.sh[s], j.elb[s], 0.095); cap(j.elb[s], j.hand[s], 0.085);
    parts.push({ d: toCam(j.hand[s])[2] - 0.001, f: () => { const p = prj(j.hand[s]); if (p) circ(p[0], p[1], 0.05 * p[3], col);
      if (s === 'L' && o.watch !== false) watch3(j); } }); }
  parts.push({ d: toCam(j.head)[2], f: () => head3(j, col, o) });
  parts.sort((a, b) => b.d - a.d);
  ctx.save(); glow(o.glow || 'rgba(255,255,255,0.22)', 14); for (const p of parts) p.f(); ctx.restore();
  return j;
}
function head3(j, col, o) {
  const p = prj(j.head); if (!p) return; const r = 0.11 * p[3];
  circ(p[0], p[1], r, col); noGlow();
  // which way the face points, against the line to the camera: 1 facing us, -1 facing away
  const fd = V3.dot(j.F, V3.norm(V3.sub(camPos(), j.head)));
  ctx.save(); ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.clip();
  // hair: a darker cap; from behind it covers most of the head, from the front only the top
  const side = prj(V3.add(j.head, V3.mul(j.F, 0.05))), sx = side ? (side[0] - p[0]) : 0;
  const up = lerp(0.0, 0.78, (fd + 1) / 2) * r;
  circ(p[0] - sx * 0.9 * (1 - fd * fd), p[1] - up, r * 1.02, o.hair || '#8e8e92'); ctx.restore();
  if (fd > 0.15) { const a = clamp((fd - 0.15) / 0.3);
    for (const sg of [-1, 1]) { const e = prj(V3.add(j.head, V3.add(V3.mul(j.F, 0.1), V3.add(V3.mul(j.R, sg * 0.042), [0, 0.005 - 0.05 * (j.look || 0), 0])))); if (!e) continue;
      ctx.save(); ctx.globalAlpha *= a; ell(e[0], e[1], 0.014 * e[3], (o.blink ? 0.003 : 0.018) * e[3], 0, o.eye || '#000'); ctx.restore(); } }
}
function watch3(j) {
  const a = prj(V3.lerp(j.hand.L, j.elb.L, 0.2)), b = prj(V3.lerp(j.hand.L, j.elb.L, 0.3)); if (!a || !b) return;
  const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l, w = 0.06 * a[3];
  ctx.save(); noGlow(); ln(a[0] + nx * w, a[1] + ny * w, a[0] - nx * w, a[1] - ny * w, 0.032 * a[3], '#141414', 'butt');
  circ(a[0], a[1], 0.022 * a[3], '#141414'); circ(a[0], a[1], 0.014 * a[3], '#9a9a9a'); ctx.restore();
}
// claw marks over the back: many, in rows of three, some fresh (red), some healed (dark)
function scars3(j, k) {
  const R = j.R, U = [0, 1, 0], B = V3.mul(j.F, -0.165);
  const at = (u, v) => prj(V3.add(V3.lerp(j.chest, j.pelvis, v), V3.add(V3.mul(R, u), B)));
  ctx.save(); ctx.globalAlpha *= k; ctx.lineCap = 'round';
  // a grid of claw marks (three parallel cuts each) over the whole back, slanting both ways
  let n = 0;
  for (let row = 0; row < 6; row++) for (let col = 0; col < 3; col++) { n++;
    const u0 = -0.11 + col * 0.09 + (hash(n * 3.7) - 0.5) * 0.05, v0 = 0.04 + row * 0.15 + (hash(n * 1.9) - 0.5) * 0.06, sl = (row + col) % 2 ? 1 : -1;
    const du = sl * (0.05 + hash(n * 5.1) * 0.04), dv = 0.07 + hash(n * 2.3) * 0.05, fresh = hash(n * 9.1) < 0.55;
    for (let m = 0; m < 3; m++) { const a = at(u0 + m * 0.02, v0 + m * 0.012), b = at(u0 + du + m * 0.02, Math.min(1, v0 + dv + m * 0.012)); if (!a || !b) continue;
      if (fresh) { redGlow(6); ln(a[0], a[1], b[0], b[1], 0.009 * a[3], C.red); noGlow(); } else ln(a[0], a[1], b[0], b[1], 0.008 * a[3], '#8a3434'); } }
  ctx.restore();
}

// ---------- the thing in the doorway (it exists only in the mirror) ----------
// feet at (x, z) on the mirror side; it faces the glass. o.reach: [x,y,z] where its right hand goes (through the glass), o.k how far along
const THING_C = '#9a9a9f';
function thing3(x, z, o = {}) {
  const t = o.t || 0, sway = Math.sin(t * 1.3) * 0.01, col = o.col || THING_C;
  const sc = o.sc ?? 1, P = (dx, y, dz = 0) => [x + dx + sway * (y / 2), y * sc, z + dz];
  const head = P(0.02, 1.95), neck0 = P(0.01, 1.78), sh = { L: P(-0.15, 1.72), R: P(0.15, 1.73) }, hip = { L: P(-0.06, 1.0), R: P(0.06, 1.0) };
  const segs = [];
  const cap = (a, b, w) => { const p = prj(a), q = prj(b); if (p && q) ln(p[0], p[1], q[0], q[1], w * (p[3] + q[3]) / 2, col); };
  ctx.save(); glow('rgba(255,255,255,0.18)', 16);
  for (const s of ['L', 'R']) { const kx = s === 'L' ? -0.08 : 0.08; cap(hip[s], P(kx, 0.52, 0.02), 0.055); cap(P(kx, 0.52, 0.02), P(kx * 1.1, 0.02, 0.04), 0.05); }
  cap(P(0, 1.7), P(0, 1.05), 0.15); cap(sh.L, sh.R, 0.07); cap(neck0, head, 0.05);
  const arm = (s, hand) => { const S = sh[s], E = V3.lerp(S, hand, 0.5); E[0] += (s === 'L' ? -0.05 : 0.05); cap(S, E, 0.045); cap(E, hand, 0.04); fingers3(hand, V3.norm(V3.sub(hand, E)), col); };
  arm('L', P(-0.22, 0.6, 0.02));
  if (!o.reach) arm('R', P(0.22, 0.58, 0.02));
  // head: a long skull, tilted, with two dark hollows and no mouth
  const hp = prj(head); if (hp) { ctx.save(); ctx.translate(hp[0], hp[1]); ctx.rotate(0.22 + Math.sin(t * 0.7) * 0.03); ell(0, 0, 0.075 * hp[3], 0.11 * hp[3], 0, col); noGlow();
    for (const sg of [-1, 1]) ell(sg * 0.03 * hp[3], -0.005 * hp[3], 0.017 * hp[3], 0.026 * hp[3], 0, o.eyes || '#050505'); ctx.restore(); }
  ctx.restore();
  return { sh, P };
}
function fingers3(hand, dir, col, len = 0.17) {
  const p = prj(hand); if (!p) return; const q = prj(V3.add(hand, V3.mul(dir, 0.1))); const a0 = q ? Math.atan2(q[1] - p[1], q[0] - p[0]) : Math.PI / 2;
  for (let i = 0; i < 4; i++) { const a = a0 + (i - 1.5) * 0.22, L = len * p[3] * (i === 1 || i === 2 ? 1.1 : 0.9);
    ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.quadraticCurveTo(p[0] + Math.cos(a) * L * 0.6, p[1] + Math.sin(a) * L * 0.6 + 4, p[0] + Math.cos(a) * L, p[1] + Math.sin(a) * L);
    ctx.lineWidth = Math.max(2, 0.016 * p[3]); ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.stroke(); }
}
// its arm through the glass: from its shoulder (mirror side) to the point on the glass, then on into the room to your wrist
function greyArm(shoulder, G, wrist, k = 1, inside = true) {
  const pts = inside ? [shoulder, V3.lerp(shoulder, G, 0.5), G] : [G, V3.lerp(G, wrist, k)];
  ctx.save(); glow('rgba(255,255,255,0.2)', 12);
  for (let i = 0; i < pts.length - 1; i++) { const p = prj(pts[i]), q = prj(pts[i + 1]); if (p && q) ln(p[0], p[1], q[0], q[1], 0.045 * (p[3] + q[3]) / 2, THING_C); }
  ctx.restore();
}
// fingers closed around your wrist
function gripWrist(wrist, k = 1) {
  const p = prj(wrist); if (!p) return; const r = 0.05 * p[3];
  ctx.save(); glow('rgba(255,255,255,0.2)', 10); ctx.lineCap = 'round';
  for (let i = 0; i < 4; i++) { const y = p[1] - r * 0.9 + i * r * 0.6; ctx.beginPath(); ctx.moveTo(p[0] - r * 1.4, y); ctx.quadraticCurveTo(p[0], y + r * 0.5 * k, p[0] + r * 1.4 * k, y - r * 0.2);
    ctx.lineWidth = Math.max(2.5, 0.016 * p[3]); ctx.strokeStyle = THING_C; ctx.stroke(); }
  ctx.restore();
}
// rings spreading over the glass where something passes through it
function glassRipple(G, t0, t) {
  const d = t - t0; if (d < 0 || d > 1.6) return;
  for (let i = 0; i < 3; i++) { const k = d * 0.9 - i * 0.2; if (k <= 0 || k > 1) continue;
    const pts = ringPts(G, [0.04 + 0.22 * easeOut(k), 0, 0], [0, 0.04 + 0.22 * easeOut(k), 0], 36);
    ctx.save(); ctx.globalAlpha *= 0.55 * (1 - k); polyW(pts, null, '#dfe8ef', 3); ctx.restore(); }
}

// ---------- fog on the glass, and what is written in it ----------
// letters on the glass in glass coordinates (x right, y up, metres), drawn as you read them from the room
const RUN_BOX = { x: -0.13, y: 1.5, h: 0.25, w: 0.17, gap: 0.065 };
const LETTERS = {
  R: [[[0, 0], [0, 1]], [[0, 1], [0.55, 1], [0.8, 0.94], [0.92, 0.8], [0.9, 0.64], [0.75, 0.53], [0.5, 0.5], [0, 0.5]], [[0.42, 0.5], [0.95, 0]]],
  U: [[[0, 1], [0, 0.32], [0.08, 0.1], [0.25, 0.01], [0.5, -0.01], [0.75, 0.01], [0.92, 0.1], [1, 0.32], [1, 1]]],
  N: [[[0, 0], [0, 1], [1, 0], [1, 1]]]
};
// all strokes of the word in order, in glass coordinates, with their lengths
function runStrokes() {
  if (runStrokes.c) return runStrokes.c; const out = [];
  'RUN'.split('').forEach((ch, i) => { const x0 = RUN_BOX.x + i * (RUN_BOX.w + RUN_BOX.gap);
    for (const s of LETTERS[ch]) { const pts = s.map(([u, v]) => [x0 + u * RUN_BOX.w, RUN_BOX.y + v * RUN_BOX.h]); let L = 0; for (let k = 1; k < pts.length; k++) L += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]); out.push({ ch: i, pts, L }); } });
  return (runStrokes.c = out);
}
// how much of each letter is written: p[i] 0..1 per letter. Returns the fingertip (glass point) of the stroke being drawn, if any
function runTip(p) {
  let tip = null;
  for (let i = 0; i < 3; i++) { const ss = runStrokes().filter(s => s.ch === i), tot = ss.reduce((a, s) => a + s.L, 0); let left = clamp(p[i]) * tot;
    if (p[i] <= 0 || p[i] >= 1) continue;
    for (const s of ss) { if (left <= s.L) { let l = left; for (let k = 1; k < s.pts.length; k++) { const d = Math.hypot(s.pts[k][0] - s.pts[k - 1][0], s.pts[k][1] - s.pts[k - 1][1]);
          if (l <= d) { const u = l / d; tip = [lerp(s.pts[k - 1][0], s.pts[k][0], u), lerp(s.pts[k - 1][1], s.pts[k][1], u)]; break; } l -= d; } break; }
      left -= s.L; } }
  return tip;
}
let fogC = null;
// fog: amount 0..1 over the glass; p: letters written; drip: 0..1 how far the drops have run
function fog3(t, amt, p = [0, 0, 0], drip = 0, wipe = null) {
  if (amt <= 0) return;
  const cw = ctx.canvas.width, ch = ctx.canvas.height;   // the canvas may be a 9:16 wrapper with its own camera
  if (!fogC || fogC.width !== cw || fogC.height !== ch) { fogC = document.createElement('canvas'); fogC.width = cw; fogC.height = ch; }
  const fx = fogC.getContext('2d'); fx.setTransform(1, 0, 0, 1, 0, 0); fx.globalCompositeOperation = 'source-over'; fx.clearRect(0, 0, cw, ch);
  // the fog layer in screen space, built from the glass outline (the current canvas transform is the camera push; apply it too)
  fx.setTransform(ctx.getTransform());
  const sp = glassPts().map(prj); if (sp.some(q => !q)) return;
  fx.beginPath(); fx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) fx.lineTo(q[0], q[1]); fx.closePath();
  const cx = (sp[0][0] + sp[2][0]) / 2, cy = (sp[0][1] + sp[2][1]) / 2;
  const g = fx.createRadialGradient(cx, cy + 120, 40, cx, cy, 900); g.addColorStop(0, `rgba(205,214,220,${0.62 * amt})`); g.addColorStop(1, `rgba(190,200,206,${0.42 * amt})`);
  fx.fillStyle = g; fx.fill();
  if (grainC) { fx.save(); fx.clip(); fx.globalAlpha = 0.18 * amt; fx.globalCompositeOperation = 'destination-out'; fx.drawImage(grainC[2], 0, 0, cw, ch); fx.restore(); }
  // wipe the strokes out of the fog, as far as they are written
  fx.globalCompositeOperation = 'destination-out'; fx.lineCap = 'round'; fx.lineJoin = 'round'; fx.shadowColor = 'rgba(0,0,0,1)'; fx.shadowBlur = 6;
  for (let i = 0; i < 3; i++) { const ss = runStrokes().filter(s => s.ch === i), tot = ss.reduce((a, s) => a + s.L, 0); let left = clamp(p[i]) * tot;
    for (const s of ss) { if (left <= 0) break; let l = left; fx.beginPath();
      for (let k = 0; k < s.pts.length; k++) { const q = prj([s.pts[k][0], s.pts[k][1], 0]);
        if (k === 0) { fx.moveTo(q[0], q[1]); continue; }
        const d = Math.hypot(s.pts[k][0] - s.pts[k - 1][0], s.pts[k][1] - s.pts[k - 1][1]);
        if (l < d) { const u = l / d, e = prj([lerp(s.pts[k - 1][0], s.pts[k][0], u), lerp(s.pts[k - 1][1], s.pts[k][1], u), 0]); fx.lineTo(e[0], e[1]); break; }
        fx.lineTo(q[0], q[1]); l -= d; }
      fx.lineWidth = 0.038 * prj([RUN_BOX.x, RUN_BOX.y, 0])[3]; fx.stroke(); left -= s.L; } }
  fx.fillStyle = '#000'; if (wipe) for (const [x, y, r] of wipe) { const q = prj([x, y, 0]); if (q) { fx.beginPath(); fx.arc(q[0], q[1], (r || 0.08) * q[3], 0, Math.PI * 2); fx.fill(); } }
  // drops running down from the bottom of the letters
  if (drip > 0) for (let i = 0; i < 9; i++) { const x = RUN_BOX.x + 0.01 + hash(i * 4.3) * (3 * RUN_BOX.w + 2 * RUN_BOX.gap), y0 = RUN_BOX.y + 0.01, y1 = y0 - (0.04 + hash(i * 7.9) * 0.14) * clamp(drip * (0.6 + hash(i)));
    const a = prj([x, y0, 0]), b = prj([x, y1, 0]); fx.lineWidth = 0.009 * a[3]; fx.beginPath(); fx.moveTo(a[0], a[1]); fx.lineTo(b[0], b[1]); fx.stroke(); }
  ctx.save(); (window.rawSetTransform || ctx.setTransform.bind(ctx))(1, 0, 0, 1, 0, 0); ctx.drawImage(fogC, 0, 0); ctx.restore();
}
// the towel over the mirror; bump 0..1 pushes it out from behind, at bx,by on the glass
function towel3(t, k = 1, bump = 0, bx = 0, by = 1.5) {
  if (k <= 0) return;
  const top = MIR.y1 + 0.06, bot = lerp(top, MIR.y0 - 0.12, k), x0 = MIR.x0 - 0.06, x1 = MIR.x1 + 0.06;
  const sp = polyW([[x0, bot, 0.03], [x1, bot, 0.03], [x1, top, 0.03], [x0, top, 0.03]], '#b9b9bd', null);
  ctx.save(); ctx.globalAlpha *= 0.35; for (let i = 1; i < 9; i++) { const x = lerp(x0, x1, i / 9) + Math.sin(i * 2.1) * 0.02; lnW([x, top, 0.032], [x + 0.01, bot, 0.032], 3, '#7c7c80'); } ctx.restore();
  lnW([x0, bot, 0.033], [x1, bot, 0.033], 4, '#d6d6da'); lnW([x0 - 0.04, top, 0.035], [x1 + 0.04, top, 0.035], 6, '#9a9a9e');
  if (bump > 0 && k > 0.95) { const c = prj([bx, by, 0.03]); if (c) { const r = (0.12 + 0.05 * bump) * c[3];
    const g = ctx.createRadialGradient(c[0] - r * 0.3, c[1] - r * 0.3, r * 0.1, c[0], c[1], r); g.addColorStop(0, `rgba(240,240,244,${0.9 * bump})`); g.addColorStop(0.7, `rgba(120,120,126,${0.5 * bump})`); g.addColorStop(1, 'rgba(120,120,126,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(c[0], c[1], r, 0, Math.PI * 2); ctx.fill(); } }
}

// ---------- the whole bathroom shot ----------
// o.me: your pose; o.refl: the pose your reflection copies (default: yours); o.reflOff: draw no reflection; o.door; o.thing {x,z,reach,...}
// o.fog/o.run/o.drip; o.water; o.inMirror(): extra things drawn inside the glass; o.front(): extra things in the room, in front of the counter
// o.scars: on the reflection; o.meScars; o.towel/o.bump
function bathroom(t, o = {}) {
  setCam(o.cam || CAMS.ots);
  const camZ = CAM.z;
  // the real room: the walls you can see from here
  if (CAM.cyw < 0) {   // looking back into the room (away from the mirror)
    room3(0, { door: o.realDoor ?? 0, inDoor: o.inRealDoor });
    if (o.me) body3(o.me, { scars: o.meScars });
    counter3(0);
    if (o.front) o.front();
    return;
  }
  // side walls, floor and ceiling of the real room, then the mirror wall
  { const { x0, x1, y1 } = ROOM, z1 = ROOM.z1;
    polyW([[x0, 0, 0], [x1, 0, 0], [x1, 0, z1], [x0, 0, z1]], FLOOR_C, EDGE_C, 2);
    for (let x = x0 + 0.42; x < x1; x += 0.42) lnW([x, 0, 0], [x, 0, z1], 1.5, '#222');
    for (let z = 0.42; z < z1; z += 0.42) lnW([x0, 0, z], [x1, 0, z], 1.5, '#222');
    polyW([[x0, y1, 0], [x1, y1, 0], [x1, y1, z1], [x0, y1, z1]], CEIL_C, EDGE_C, 2);
    for (const x of [x0, x1]) { polyW([[x, 0, 0], [x, 0, z1], [x, y1, z1], [x, y1, 0]], SIDE_C, EDGE_C, 2); for (let y = 0.3; y < 1.25; y += 0.3) lnW([x, y, 0], [x, y, z1], 1.5, TILE_C); } }
  mirrorWall();
  // inside the glass
  ctx.save();
  if (clipGlass()) {
    ctx.fillStyle = '#000'; ctx.fillRect(-W, -H, 3 * W, 3 * H);
    const th = o.thing;
    room3(1, { door: o.door ?? 0, inDoor: th && th.inDoor ? () => thing3(th.x, th.z, th) : null });
    if (th && !th.inDoor) thing3(th.x, th.z, th);
    if (o.behind) o.behind();
    if (!o.reflOff && (o.refl || o.me)) body3(o.refl || o.me, { mirror: true, col: o.reflCol || '#dcdcde', scars: o.scars, blink: o.reflBlink });
    if (o.inMirror) o.inMirror();
    counter3(1); waterStream(1, o.water || 0);
    ctx.save(); ctx.globalAlpha = 0.14; ctx.fillStyle = '#000'; ctx.fillRect(-W, -H, 3 * W, 3 * H); ctx.restore();   // a mirror gives back a little less light
    glassSheen();
    if (o.glassFx) o.glassFx();
    fog3(t, o.fog || 0, o.run || [0, 0, 0], o.drip || 0, o.wipe);
  }
  ctx.restore();
  mirrorFrame({ light: o.light ?? 1 });
  if (o.towel) towel3(t, o.towel, o.bump || 0, o.bx, o.by);
  counter3(0); waterStream(0, o.water || 0);
  if (o.behindMe) o.behindMe();
  if (o.me && !o.meOff && o.me.z < camZ - 0.2) body3(o.me, { scars: o.meScars });
  if (o.front) o.front();
}

// ---------- EP03 scenes: "If Your Reflection Ever Tells You To RUN" ----------
const ev = type => window.TL.events.filter(e => e.type === type);
const evAfter = (type, t0) => { const l = ev(type).filter(e => e.t >= t0 - 0.01); return l.length ? l.reduce((a, b) => (b.t < a.t ? b : a)) : null; };
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
// a bathroom shot with a slow 2D push toward a point in the world (the push is a narrower lens: it changes nothing in the geometry)
function shot(t, t0, d, z0, z1, focus, o) {
  setCam(o.cam || CAMS.ots); const f = prj(focus) || [W / 2, H / 2];
  cam(t, t0, d, z0, z1, f[0], f[1], () => bathroom(t, o));
}
const GLASS_C = [0, 1.52, 0];
const sideTag = (t, t0, s, x, y, col = C.fig, size = 50) => { if (t >= t0) pop(t, t0, x, y, () => tag(s, x, y + 10, col, size, 'center')); };
const redFlash = (t, t0, a = 0.1) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a * (0.5 + 0.5 * Math.sin((t - t0) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
// poses
const wave = (t, k = 1) => ({ R: [lerp(0.24, 0.32 + 0.07 * Math.sin(t * 9), k), lerp(0.9, 1.74, k), lerp(0.04, 0.14, k)] });
const washing = (t, k = 1) => ({ ...WASH, L: [-0.07 + 0.025 * Math.sin(t * 8) * k, 0.98, 0.42], R: [0.07 - 0.025 * Math.sin(t * 8) * k, 0.98, 0.42] });
// your reflection, writing on the glass from its side: it stands closer, leans in, one finger on the glass at tip (glass coords)
function writerPose(tip, k = 1) { const x = ME.x + 0.17 * k, z = 0.55; return poseOf({ x, z, lean: 0.22 * k, R: tip ? [lerp(0.24, tip[0] - x, k), lerp(0.9, tip[1] - 0.04, k), lerp(0.04, z - 0.08, k)] : STAND.R }); }
function reflFinger(p, tip, k = 1) { if (!tip || k < 0.9) return; const h = MIRROR(skeleton(p).hand.R), a = prj(h), b = prj([tip[0], tip[1], 0]);
  if (a && b) { ctx.save(); glow('rgba(255,255,255,0.25)', 10); ln(a[0], a[1], b[0], b[1], 0.024 * a[3], '#dcdcde'); ctx.restore(); } }
// an open hand flat on the glass, at glass point g; back: seen from the back (yours) or the palm (its)
function palmOn(g, col, z = 0.01, mirror = false) {
  const c = prj([g[0], g[1], z]); if (!c) return; const s = c[3];
  ctx.save(); glow('rgba(255,255,255,0.25)', 12); ell(c[0], c[1], 0.045 * s, 0.055 * s, 0, col);
  const fs = mirror ? -1 : 1;
  for (let i = 0; i < 4; i++) { const a = -Math.PI / 2 + (i - 1.5) * 0.24 * fs; ln(c[0] + Math.cos(a) * 0.04 * s, c[1] + Math.sin(a) * 0.04 * s, c[0] + Math.cos(a) * (0.1 + (i === 1 || i === 2 ? 0.015 : 0)) * s, c[1] + Math.sin(a) * (0.1 + (i === 1 || i === 2 ? 0.015 : 0)) * s, 0.02 * s, col); }
  ln(c[0] - fs * 0.04 * s, c[1] + 0.01 * s, c[0] - fs * 0.085 * s, c[1] - 0.03 * s, 0.022 * s, col);   // thumb
  ctx.restore();
}

// ---------- white icons ----------
function icon3(name, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  if (name === 'wipe') { rrS(-80, -90, 160, 180, 8, C.fig, 9); ctx.globalAlpha *= 0.5; for (let i = 0; i < 3; i++) pthS(`M${-50},${-40 + i * 34} q50,-24 100,0`, C.fig, 8); ctx.globalAlpha = 1; ell(30, 40, 26, 32, -0.3, C.fig); }
  if (name === 'ask') { rrS(-96, -70, 192, 120, 26, C.fig, 10); pth('M-50,48 L-70,94 L-14,50 Z', C.fig); text('?', 0, 20, '900 100px M', C.fig); }
  if (name === 'turn') { ctx.beginPath(); ctx.arc(0, 0, 70, -Math.PI * 0.2, Math.PI * 1.25); ctx.lineWidth = 14; ctx.strokeStyle = C.fig; ctx.stroke(); pth('M44,-78 L92,-40 L34,-24 Z', C.fig); circ(0, 0, 18, C.fig); }
  noGlow(); ctx.restore();
}
// small dark pictograms on the rule page
const _pageIcon = pageIcon;
pageIcon = function (name, x, y, col = '#111') {
  if (name === 'mirror') { ctx.save(); ctx.translate(x, y); rrS(-34, -50, 68, 92, 6, col, 6); circ(0, -14, 12, col); rr(-14, 0, 28, 30, 8, col); ln(-12, 54, 12, 54, 6, col); ctx.restore(); return; }
  if (name === 'run') { ctx.save(); ctx.translate(x, y); circ(10, -40, 11, col); poly([[4, -26], [-6, 8]], 12, col); poly([[-6, 8], [14, 26], [8, 48]], 10, col); poly([[-6, 8], [-22, 28], [-40, 30]], 10, col); poly([[0, -18], [22, -6], [34, -18]], 9, col); poly([[0, -18], [-18, -6], [-30, 4]], 9, col); ctx.restore(); return; }
  return _pageIcon(name, x, y, col);
};

// ---------- hook ----------
const RUN_END = (() => { const s = runStrokes(); const l = s[s.length - 1].pts; return l[l.length - 1]; })();
S.h1 = (t, seg) => {
  const tn = wt(seg, 'not'), tr = wt(seg, 'run');
  // frame 0: the word is already there, written from the other side; your reflection's finger is still on the last stroke, and behind it the doorway is not empty
  const rp = writerPose(RUN_END);
  shot(t, 0, seg.end + 0.6, 1.0, 1.1, GLASS_C, { me: poseOf({}), refl: rp, door: 1, thing: { x: 0.3, z: -3.12, t, inDoor: true }, fog: 0.85, run: [1, 1, 1], drip: 0.4 + 0.6 * prog(t, 0, 5),
    inMirror: () => reflFinger(rp, RUN_END) });
  if (t >= tn) pop(t, tn, 1500, 250, () => tag('DO NOT LOOK BACK', 1500, 260, C.red, 54, 'center'), 0.3);
};
// the three "do not"s as a teaser: each one is done anyway, you see what happens, then black
function h2Windows(seg) { return [[seg.start, wt(seg, 'do', 2), 'wipe', 'wipe', 200], [wt(seg, 'do', 2), wt(seg, 'do', 3), 'ask', 'ask', 770], [wt(seg, 'do', 3), nextStart(seg), 'turn', 'turn', 200]]; }
const H2_HIT = 0.6, H2_BLACK = 0.4;
function teaserBox(t, seg, w0, ic, word, y) {
  const x = 960, tx = wt(seg, word);
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.82; rr(x - 140, y - 130, 280, 260, 22, '#000'); ctx.restore(); rrS(x - 140, y - 130, 280, 260, 22, C.fig, 5); icon3(ic, x, y, 0.95); }, 0.3);
  redX(x, y, 105, prog(t, tx + 0.25, 0.3));
}
S.h2 = (t, seg) => {
  const ws = h2Windows(seg); let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, ic, word, by] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit;
  if (t < blk) {
    if (i === 0) {
      // you wipe the fog away. Behind the glass, where your face should be, it is waiting; its hand hits the glass
      const k = prog(t, w0 + 0.2, hit - w0 - 0.3), wipe = [];
      for (let n = 0; n < 14; n++) { const u = n / 13; if (u > k) break; wipe.push([lerp(-0.25, 0.25, (Math.sin(u * 9) + 1) / 2) + 0.02, 1.45 + u * 0.22, 0.11]); }
      const tip = wipe.length ? wipe[wipe.length - 1] : [0, 1.45];
      const me = poseOf({ lean: 0.18, R: [tip[0] - ME.x, tip[1] - 0.02, ME.z - 0.06] });
      shot(t, w0, blk - w0, 1.15, 1.45, [0.0, 1.55, 0], { me, reflOff: true, door: 1, fog: 0.9, wipe,
        behind: () => thing3(0.0, -0.32, { t, sc: 0.84, col: '#a2a2a8' }),
        glassFx: () => { if (d > -0.05) { palmOn([0.12, 1.5], '#a2a2a8', -0.005, true); glassRipple([0.12, 1.5, 0], hit, t); } } });
      if (d > 0 && d < 0.07) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.6; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    } else if (i === 1) {
      // you ask it why. It answers by turning red
      const r = ease(prog(t, w0 + 0.9, hit - w0 - 0.9));
      shot(t, w0, blk - w0, 1.1, 1.5, [ME.x, 1.6, -ME.z], { me: poseOf({}), door: 1, reflCol: `rgb(${Math.round(lerp(220, 235, r))},${Math.round(lerp(220, 30, r))},${Math.round(lerp(222, 30, r))})`,
        glassFx: () => { if (r > 0) { ctx.save(); ctx.globalAlpha = 0.35 * r; ctx.fillStyle = '#ff1a1a'; ctx.fillRect(-W, -H, 3 * W, 3 * H); ctx.restore(); } } });
      const hp = prj(skeleton(poseOf({})).head);
      if (hp) bubbleTo(hp[0] + 150, hp[1] - 190, 150, 110, '?', t, w0 + 0.25, hp[0] + 60, hp[1] - 60);
      if (d > 0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.5 * clamp(d / 0.2); ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    } else {
      // you turn around. Behind you, in the glass, it steps up to your reflection and takes it
      const k = ease(prog(t, w0 + 0.2, 0.7)), c = ease(prog(t, w0 + 0.5, hit - w0 - 0.5));
      const me = poseOf({ yaw: Math.PI * k });
      shot(t, w0, blk - w0, 1.05, 1.5, [ME.x, 1.6, -ME.z], { me, refl: poseOf({}), door: 1,
        thing: { x: lerp(0.3, ME.x + 0.12, c), z: lerp(-3.12, -ME.z - 0.45, c), t, inDoor: c < 0.05 },
        inMirror: () => { if (c > 0.8) { const j = skeleton(poseOf({})); for (const s of ['L', 'R']) fingers3(MIRROR(V3.add(j.sh[s], [0, 0.03, 0])), [0, -1, 0], '#9a9a9f', 0.15); } } });
      if (d > 0 && d < 0.08) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.55; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    }
  }
  if (t >= blk) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); teaserBox(t, seg, w0, ic, word, by); ctx.restore();
};

// ---------- rule 1: do not test your reflection ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT TEST YOUR REFLECTION');
S.a1 = (t, seg) => {
  const tw = wt(seg, 'washing');
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.1, GLASS_C, { me: poseOf(washing(t, prog(t, tw - 0.4, 0.4))), water: prog(t, tw - 0.6, 0.3), door: 0, light: 0.85 + 0.15 * (hash(Math.floor(t * 12)) > 0.08 ? 1 : 0) });
  if (t >= seg.start + 0.6) slideIn(t, seg.start + 0.6, 40, 0, () => { ctx.save(); redGlow(10); text('3:00 AM', 1560, 200, '700 54px Plex', C.red); ctx.restore(); });
};
// you look up; your reflection a moment later
const lookUp = (t, t0) => ({ ...WASH, look: 1 - ease(prog(t, t0, 0.4)), lean: 0.2 * (1 - ease(prog(t, t0, 0.4))) });
S.a2 = (t, seg) => {
  const tu = wt(seg, 'up'), tm = wt(seg, 'moment'), lag = 0.9;
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.6, [ME.x, 1.6, -ME.z], { me: poseOf(lookUp(t, tu)), refl: poseOf(lookUp(t - lag, tu)), water: 1 - prog(t, tu, 0.3) });
  if (t >= tm) pop(t, tm, 1480, 300, () => tag('A MOMENT LATER', 1480, 310, C.red, 50, 'center'));
};
S.a3 = (t, seg) => {
  // two tracks: when you move, and when it moves
  const t0 = seg.start, tt = wt(seg, 'tired');
  cam(t, t0, seg.end - t0 + 0.8, 1, 1.04, W / 2, 500, () => {
    const x0 = 420, x1 = 1500, y = [400, 600];
    [['YOU', C.fig], ['REFLECTION', C.sec]].forEach(([l, c], i) => { slideIn(t, t0 + i * 0.1, -40, 0, () => { text(l, x0 - 30, y[i] + 12, '900 40px M', c, 'right'); lnP(x0, y[i], x1, y[i], 5, C.dim, easeOut(prog(t, t0, 0.6))); }); });
    const mx = 880, lagX = 1080, k = prog(t, t0 + 0.4, 0.5), k2 = prog(t, t0 + 1.0, 0.5);
    if (k > 0) pop(t, t0 + 0.4, mx, y[0], () => { glow(); circ(mx, y[0], 26, C.fig); noGlow(); });
    if (k2 > 0) pop(t, t0 + 1.0, lagX, y[1], () => { glow(); circ(lagX, y[1], 26, C.sec); noGlow(); });
    if (t >= t0 + 1.3) { ctx.save(); ctx.setLineDash([10, 9]); ln(mx, y[0] + 30, mx, y[1] + 40, 3, C.mid); ctx.restore(); redGlow(10);
      lnP(mx, y[1] + 70, lagX, y[1] + 70, 6, C.red, easeOut(prog(t, t0 + 1.3, 0.4))); noGlow();
      fadeIn(t, t0 + 1.5, () => text('0.9 s', (mx + lagX) / 2, y[1] + 130, '900 52px M', C.red)); }
    if (t >= tt) pop(t, tt, 960, 230, () => tag('JUST TIRED?', 960, 240, C.fig, 50, 'center'));
  });
};
// a crossed-out action: the label in its box with a red X beside it (never over the words)
function xTag(s, x, y, size, p) { tag(s, x, y, C.fig, size, 'center'); ctx.font = `900 ${size}px M`; const w = ctx.measureText(s).width + 28; redX(x - w / 2 - size * 0.95, y - size * 0.2, size * 0.5, p); }
S.a4 = (t, seg) => {
  const tw = wt(seg, 'wave'), tt = wt(seg, 'tilt'), lag = 0.9;
  const pose = u => poseOf({ ...wave(u, prog(u, tw - 0.2, 0.3) * (1 - prog(u, tt - 0.5, 0.3))), roll: Math.sin(clamp((u - tt) / 1.2) * Math.PI) * 1.0 });
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.1, 1.3, [ME.x, 1.55, -ME.z], { me: pose(t), refl: pose(t - lag) });
  if (t >= tw + 0.2) slideIn(t, tw + 0.2, 40, 0, () => { xTag('DO NOT WAVE', 1460, 300, 48, prog(t, tw + 0.5, 0.3)); });
  if (t >= tt + 0.2) slideIn(t, tt + 0.2, 40, 0, () => { xTag('DO NOT TILT', 1460, 430, 48, prog(t, tt + 0.5, 0.3)); });
};
// every test: it falls further behind
const lagA5 = (t, seg) => { const t1 = wt(seg, 'one'), t2 = wt(seg, 'two'), t3 = wt(seg, 'three');
  if (t < t1) return lerp(0.9, 1, prog(t, seg.start, t1 - seg.start)); if (t < t2) return lerp(1, 2, (t - t1) / (t2 - t1)); if (t < t3) return lerp(2, 3, (t - t2) / (t3 - t2)); return 3; };
S.a5 = (t, seg) => {
  const t1 = wt(seg, 'one');
  const pose = u => poseOf({ ...wave(u, prog(u, seg.start + 0.1, 0.3)) });
  const lag = lagA5(t, seg);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.3, [ME.x, 1.55, -ME.z], { me: pose(t), refl: poseOf({ ...wave(t - lag, prog(t - lag, seg.start + 0.1, 0.3)) }) });
  if (t >= t1 - 0.1) fadeIn(t, t1 - 0.1, () => { spaced('BEHIND BY', 1500, 330, '900 34px M', C.mid, 6); ctx.save(); redGlow(14); text(lag.toFixed(1) + ' s', 1500, 450, '900 110px M', C.red); ctx.restore(); });
};
// it is not slow: long grey fingers over its shoulders, from behind
function heldBack(j, k = 1) { if (k <= 0) return; ctx.save(); ctx.globalAlpha *= k; for (const s of ['L', 'R']) { const sp = MIRROR(V3.add(j.sh[s], [0, 0.03, 0])); fingers3(sp, [0, -1, 0.3], '#9a9a9f', 0.16); } ctx.restore(); }
S.a6 = (t, seg) => {
  const ts = wt(seg, 'something'), th = wt(seg, 'holding'), rp = poseOf({ ...wave(t - 3, 1) });
  const frozen = poseOf({ ...wave(seg.start - 3, 1) });   // it has stopped
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.3, 1.9, [ME.x, 1.5, -ME.z], { me: poseOf({}), refl: frozen,
    inMirror: () => heldBack(skeleton(frozen), prog(t, ts, 0.8)) });
  if (t >= th) pop(t, th, 1500, 800, () => tag('HOLDING IT BACK', 1500, 810, C.red, 50, 'center'));   // low on the dark door, clear of the frame and the raised arm
};
// what would happen: it stops, it is covered and pulled back into the dark, and the thing takes its place at the glass
S.a7 = (t, seg) => {
  const gr = evAfter('grab', seg.end), wh = evAfter('whoosh', seg.end), sl = evAfter('slam', seg.end);
  const tg = gr ? gr.t : seg.end + 0.75, tw = wh ? wh.t : seg.end + 1.15, ts = sl ? sl.t : seg.end + 1.85;
  const stop = seg.start + 1.2, pose = u => poseOf({ ...wave(u, prog(u, seg.start, 0.3)) });
  const rp = pose(Math.min(t - 1.5, stop)), pull = ease(prog(t, tw, 0.45));
  const rz = lerp(ME.z, 3.0, pull);   // its distance behind the glass as it is dragged away
  shot(t, seg.start, ts - seg.start + 0.3, 1.1, 1.35, [ME.x, 1.55, -ME.z], { me: pose(t), door: 1,
    refl: { ...rp, z: rz, x: lerp(rp.x, 0.0, pull) }, reflOff: pull > 0.98,
    thing: t >= ts - 0.12 ? { x: ME.x + 0.05, z: lerp(-1.2, -0.25, prog(t, ts - 0.12, 0.12)), t, sc: 0.86, col: '#a8a8ae' } : null,
    inMirror: () => { if (t >= tg && pull < 0.98) { const j = skeleton({ ...rp, z: rz, x: lerp(rp.x, 0.0, pull) }); const hp = prj(MIRROR(j.head));
      if (hp) { ctx.save(); glow('rgba(255,255,255,0.2)', 12); ell(hp[0] - 0.02 * hp[3], hp[1], 0.1 * hp[3], 0.07 * hp[3], 0.2, '#9a9a9f'); fingers3(MIRROR(V3.add(j.head, [0.06, 0, -0.08])), [-1, -0.2, 0], '#9a9a9f', 0.14); ctx.restore(); } } },
    glassFx: () => { if (t >= ts) { palmOn([ME.x + 0.2, 1.42], '#a8a8ae', -0.005, true); glassRipple([ME.x + 0.2, 1.42, 0], ts, t); } } });
  if (t >= ts && t < ts + 0.07) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.6; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
};

// ---------- rule 2: do not look behind your reflection ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT LOOK BEHIND YOUR REFLECTION');
S.b1 = (t, seg) => {
  // turned around for a moment: the door behind you, closed
  const tc = wt(seg, 'closed');
  setCam(CAMS.rev); const f = prj([0, 1.2, ROOM.z1]);
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.12, f[0], f[1], () => bathroom(t, { cam: CAMS.rev, me: poseOf({}), realDoor: 0 }));
  if (t >= tc) pop(t, tc, 1480, 280, () => tag('CLOSED', 1480, 290, C.fig, 56, 'center'));
};
const DOOR_C = [0.25, 1.15, -ROOM.z1];
S.b2 = (t, seg) => {
  const to = wt(seg, 'open'), op = ease(prog(t, seg.start + 0.3, 1.4));
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.45, DOOR_C, { me: poseOf({}), door: op });
  if (t >= to) pop(t, to, 1480, 280, () => tag('OPEN', 1480, 290, C.red, 60, 'center'));
};
S.b3 = (t, seg) => {
  const tl = wt(seg, 'tall'), tn = wt(seg, 'thin'), tt = wt(seg, 'touches');
  const vis = ease(prog(t, seg.start, 1.6));
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.6, 2.2, [0.25, 1.3, -ROOM.z1], { me: poseOf({}), door: 1, thing: { x: 0.3, z: -3.12, t, inDoor: true, col: `rgba(154,154,159,${vis})` } });
  if (t >= tl) pop(t, tl, 1500, 260, () => tag('TALL', 1500, 270, C.fig, 56, 'center'));
  if (t >= tn) pop(t, tn, 1500, 390, () => tag('TOO THIN', 1500, 400, C.fig, 56, 'center'));
  if (t >= tt) { setCam(CAMS.ots); const p = prj([0.25, DOOR.h, -ROOM.z1]); if (p) { ctx.save(); const z = lerp(1.6, 2.2, ease((t - seg.start) / (seg.end - seg.start + 0.8))), fc = prj([0.25, 1.3, -ROOM.z1]);
      const x = fc[0] + (p[0] - fc[0]) * z, y = fc[1] + (p[1] - fc[1]) * z; redGlow(14); ctx.setLineDash([12, 9]); ctx.beginPath(); ctx.arc(x, y, 70 * prog(t, tt, 0.3) + 1, 0, Math.PI * 2); ctx.strokeStyle = C.red; ctx.lineWidth = 6; ctx.stroke(); ctx.restore(); } }
};
// the floor plan, from above. The glass is the vertical line in the middle: your room on the right, the room in the mirror on the left
const PL = { cx: 960, cy: 500, s: 190 };
const pl = (x, z) => [PL.cx + z * PL.s, PL.cy - x * PL.s];
function planRoom(m, o = {}) {
  const sg = m ? -1 : 1, a = pl(ROOM.x1, 0), b = pl(ROOM.x0, sg * ROOM.z1);
  ctx.save(); if (m) { ctx.setLineDash([12, 10]); ctx.globalAlpha *= 0.85; }
  const x0 = Math.min(a[0], b[0]), x1 = Math.max(a[0], b[0]), y0 = Math.min(a[1], b[1]), y1 = Math.max(a[1], b[1]);
  rr(x0, y0, x1 - x0, y1 - y0, 0, m ? '#0b0b0d' : '#121214'); rrS(x0, y0, x1 - x0, y1 - y0, 0, C.mid, 4);
  // counter and basin along the mirror wall
  const c0 = pl(CTR.x1, 0), c1 = pl(CTR.x0, sg * CTR.z); rr(Math.min(c0[0], c1[0]), c0[1], Math.abs(c1[0] - c0[0]), c1[1] - c0[1], 0, '#222');
  const sc = pl(0, sg * SINK.z); ell(sc[0], sc[1], SINK.rz * PL.s, SINK.rx * PL.s, 0, '#555');
  ctx.restore();
  // the door in the far wall: a gap, and the door leaf (open or shut)
  const dx = m ? x0 : x1, d0 = pl(DOOR.x1, sg * ROOM.z1), d1 = pl(DOOR.x0, sg * ROOM.z1);
  ln(dx, d0[1], dx, d1[1], 8, '#000', 'butt');
  const op = o.door ?? 0, hinge = d1, L = (DOOR.x1 - DOOR.x0) * PL.s, ang = -Math.PI / 2 + sg * 0;
  const a1 = op * 1.45; ln(hinge[0], hinge[1], hinge[0] - sg * Math.sin(a1) * L, hinge[1] - Math.cos(a1) * L, 6, m ? C.sec : C.fig);
  if (o.label) text(o.label, (x0 + x1) / 2, y0 - 26, '900 38px M', m ? C.mid : C.sec);
}
function planPerson(x, z, face, col, label, r = 0.2) {
  const [px, py] = pl(x, z); ctx.save(); glow('rgba(255,255,255,0.25)', 12); circ(px, py, r * PL.s, col);
  pth(`M${px + face * r * PL.s * 1.35},${py} L${px + face * r * PL.s * 0.6},${py - 14} L${px + face * r * PL.s * 0.6},${py + 14} Z`, col); ctx.restore();
  if (label) text(label, px, py + r * PL.s + 48, '900 34px M', col);
}
function planThing(x, z, col = '#9a9a9f', label = 'IT') { const [px, py] = pl(x, z); ctx.save(); glow('rgba(255,255,255,0.2)', 12); ell(px, py, 0.1 * PL.s, 0.2 * PL.s, 0, col); circ(px, py, 0.08 * PL.s, '#bdbdc2'); ctx.restore(); if (label) text(label, px, py - 0.3 * PL.s - 14, '900 36px M', C.red); }
function plan(t, o = {}) {
  planRoom(1, { door: 1, label: 'IN THE MIRROR' }); planRoom(0, { door: 0, label: 'YOUR BATHROOM' });
  // the glass
  const g0 = pl(MIR.x1, 0), g1 = pl(MIR.x0, 0); ctx.save(); glow('rgba(200,225,255,0.8)', 16); ln(g0[0], g0[1], g1[0], g1[1], 10, '#cfe0ef'); ctx.restore();
  text('MIRROR', g0[0], g0[1] - 26, '900 34px M', '#cfe0ef');
  planPerson(ME.x, ME.z, -1, C.fig, 'YOU');
  planPerson(ME.x, -ME.z, 1, '#bdbdc2', 'REFLECTION');
  if (o.thing !== false) planThing(o.thingX ?? 0.3, o.thingZ ?? -3.1);
}
S.b4 = (t, seg) => {
  const tt = wt(seg, 'turn'), tn = wt(seg, 'nothing');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.22, W / 2, H / 2, () => {
    fadeIn(t, seg.start, () => plan(t));
    if (t >= tt) { const [px, py] = pl(ME.x, ME.z), k = prog(t, tt, 0.5); ctx.save(); ctx.beginPath(); ctx.arc(px, py, 52, -Math.PI * 0.8, -Math.PI * 0.8 + Math.PI * 1.4 * k); ctx.strokeStyle = C.fig; ctx.lineWidth = 6; ctx.stroke(); ctx.restore(); }
    if (t >= tn) { const [dx, dy] = pl(0, ROOM.z1 - 0.45); pop(t, tn, dx, dy, () => tag('NOTHING', dx - 30, dy + 10, C.fig, 36, 'center')); }
  });
};
S.b5 = (t, seg) => {
  const tt = wt(seg, 'turn'), te = wt(seg, 'eyes'), tl = wt(seg, 'leave'), ta = wt(seg, 'alone');
  const go = ease(prog(t, ta - 0.2, 1.4));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.22, 1.3, 860, H / 2, () => {
    plan(t, { thingX: lerp(0.3, ME.x + 0.05, go), thingZ: lerp(-3.1, -ME.z - 0.5, go) });
    const [px, py] = pl(ME.x, ME.z), [gx, gy] = pl(ME.x, 0);
    if (t >= tt && t < te) { pop(t, tt, px, py - 110, () => { redX(px, py - 110, 40, prog(t, tt + 0.2, 0.3)); }); }
    if (t >= te) { const away = prog(t, tl, 0.3); ctx.save(); ctx.setLineDash([12, 10]);
      if (away < 1) lnP(px - 30, py, gx, gy, 5, C.fig, prog(t, te, 0.4) * (1 - away));
      if (away > 0) { redGlow(10); lnP(px + 30, py, px + 30 + 260 * away, py, 5, C.red, 1); } ctx.restore(); }
    if (t >= ta) { const [rx, ry] = pl(ME.x, -ME.z); pop(t, ta, rx, ry + 120, () => tag('ALONE WITH IT', rx, ry + 130, C.red, 36, 'center')); }   // under the labels, clear of the IT marker
  });
};
S.b6 = (t, seg) => {
  const tb = wt(seg, 'between'), tl = wt(seg, 'late');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.3, 1.22, 860, H / 2, () => {
    plan(t);
    if (t >= tb) { const a = pl(ME.x, ME.z), b = pl(0.3, -3.1); ctx.save(); redGlow(10); ctx.setLineDash([14, 10]); lnP(a[0], a[1], b[0], b[1], 5, C.red, prog(t, tb, 0.8)); ctx.restore();
      const [rx, ry] = pl(ME.x, -ME.z); ctx.save(); glow('rgba(255,255,255,0.8)', 30); circS(rx, ry, 0.2 * PL.s + 12, C.fig, 4); ctx.restore(); }
    if (t >= tl) { const [rx, ry] = pl(ME.x, -ME.z), k = 0.5 + 0.5 * Math.sin((t - tl) * 5); ctx.save(); ctx.translate(rx, ry); ctx.rotate(Math.PI * k); pth(`M${-0.2 * PL.s * 1.4},0 L${-0.2 * PL.s * 0.7},-14 L${-0.2 * PL.s * 0.7},14 Z`, C.red); ctx.restore();
      pop(t, tl, rx, ry + 120, () => tag('IT KEEPS LOOKING BACK', rx, ry + 130, C.red, 34, 'center')); }
  });
};

// ---------- rule 3: when it writes, run ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'WHEN IT WRITES, RUN');
const WRITE = { x: ME.x };
// the writing: the first stroke of R in c2, the rest on "R. U. N."
function runProgress(t) {
  const c2 = window.TL.segments.find(s => s.id === 'c2'), c4 = window.TL.segments.find(s => s.id === 'c4'); if (!c2 || !c4) return [1, 1, 1];
  const tl = wt(c2, 'line'), r = wt(c4, 'r'), u = wt(c4, 'u'), n = wt(c4, 'n');
  const first = runStrokes()[0].L / runStrokes().filter(s => s.ch === 0).reduce((a, s) => a + s.L, 0);
  return [t < r - 0.1 ? first * prog(t, tl, 1.1) : lerp(first, 1, prog(t, r - 0.1, 0.55)), prog(t, u - 0.05, 0.42), prog(t, n - 0.05, 0.5)];
}
// your reflection's hand: raised to the glass while it writes, down again after
function writing(t) {
  const p = runProgress(t), tip = runTip(p);
  const c2 = window.TL.segments.find(s => s.id === 'c2'), k = c2 ? ease(prog(t, wt(c2, 'line') - 0.6, 0.5)) : 1;
  const last = tip || (p[2] >= 1 ? RUN_END : (p[0] > 0 ? (runTip([Math.min(p[0], 0.999), 0, 0]) || [RUN_BOX.x, RUN_BOX.y + RUN_BOX.h]) : [RUN_BOX.x, RUN_BOX.y]));
  return { p, tip: last, pose: writerPose(last, k), k };
}
S.c1 = (t, seg) => {
  const tf = wt(seg, 'fog'), tc = wt(seg, 'cold');
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.05, 1.25, GLASS_C, { me: poseOf({ ...WASH, look: 0, lean: 0.12 }), water: 1, fog: 0.85 * ease(prog(t, tf - 0.2, 1.6)) });
  if (t >= tc) pop(t, tc, 1480, 280, () => { tag('COLD', 1480, 290, '#9fd0ff', 60, 'center'); });
};
S.c2 = (t, seg) => {
  const to = wt(seg, 'other'), w = writing(t);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.2, 1.45, [0.0, 1.55, 0], { me: poseOf({}), refl: w.pose, fog: 0.85, run: w.p, inMirror: () => reflFinger(w.pose, w.tip, w.k) });
  // side view of the glass: the finger is on the far side
  if (t >= to - 0.1) slideIn(t, to - 0.1, 40, 0, () => {
    const x = 1560, y = 330; ctx.save(); ctx.globalAlpha *= 0.92; rr(x - 190, y - 190, 380, 380, 16, '#000'); ctx.restore(); rrS(x - 190, y - 190, 380, 380, 16, C.dim, 3);
    ctx.save(); glow('rgba(200,225,255,0.8)', 12); rr(x - 8, y - 140, 16, 280, 3, '#cfe0ef'); ctx.restore();
    rr(x + 8, y - 140, 26, 280, 3, 'rgba(210,220,226,0.55)');                 // fog on your side
    text('GLASS', x, y + 175, '900 24px M', '#cfe0ef'); text('IT', x - 110, y - 150, '900 28px M', C.sec); text('YOU', x + 110, y - 150, '900 28px M', C.fig);
    poly([[x - 170, y + 40], [x - 70, y + 10], [x - 12, y - 10]], 18, '#dcdcde'); circ(x - 12, y - 10, 9, '#dcdcde');   // its finger, pressed on the glass from behind
    ctx.save(); redGlow(10); ln(x + 21, y - 70, x + 21, y + 40, 8, '#000'); ctx.restore();   // the line it draws shows on your side
  });
};
S.c3 = (t, seg) => {
  const tb = wt(seg, 'backwards'), tr = wt(seg, 'read'), w = writing(t);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.45, 1.55, [0.0, 1.55, 0], { me: poseOf({}), refl: w.pose, fog: 0.85, run: w.p, inMirror: () => reflFinger(w.pose, w.tip, w.k) });
  // its side and your side of the same word
  const box = (x, y, lbl, flip, t0) => slideIn(t, t0, 0, 30, () => { ctx.save(); ctx.globalAlpha *= 0.92; rr(x - 170, y - 100, 340, 210, 14, '#000'); ctx.restore(); rrS(x - 170, y - 100, 340, 210, 14, C.dim, 3);
    text(lbl, x, y - 58, '900 24px M', C.mid); ctx.save(); ctx.translate(x, y + 50); if (flip) ctx.scale(-1, 1); text('RUN', 0, 0, '900 90px M', flip ? C.sec : C.fig); ctx.restore(); });
  box(330, 300, 'ITS SIDE', true, tb - 0.2); box(1590, 300, 'YOUR SIDE', false, tr - 0.3);
};
S.c4 = (t, seg) => {
  const w = writing(t);
  shot(t, seg.start, seg.end - seg.start + 1.0, 1.55, 1.7, [0.0, 1.58, 0], { me: poseOf({}), refl: w.pose, fog: 0.85, run: w.p, drip: prog(t, seg.end - 0.2, 1.5), inMirror: () => reflFinger(w.pose, w.tip, w.k) });
};
S.c5 = (t, seg) => {
  const te = wt(seg, 'empty'), w = writing(t), down = ease(prog(t, seg.start + 0.2, 0.6)), rp = writerPose(RUN_END, 1 - down);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.5, 2.0, [0.25, 1.3, -ROOM.z1], { me: poseOf({}), refl: rp, door: 1, fog: 0.4, run: [1, 1, 1], drip: 1 });
  if (t >= te) pop(t, te, 1480, 280, () => tag('EMPTY', 1480, 290, C.red, 60, 'center'));
  redFlash(t, te, 0.06);
};
S.c6 = (t, seg) => {
  // from the doorway: you turn and run. Your reflection does not follow. It watches you go
  const tl = wt(seg, 'look'), k = ease(prog(t, seg.start, 0.45)), run = prog(t, seg.start + 0.4, 1.6);
  const me = poseOf({ yaw: Math.PI * k, x: lerp(ME.x, -1.0, ease(run)), z: lerp(ME.z, 2.3, run), walk: run > 0, step: t * 13, L: [-0.24, 0.85, 0.3 * Math.sin(t * 13)], R: [0.24, 0.85, -0.3 * Math.sin(t * 13)] });   // out past the left of the doorway, arms swinging, never close enough to clip the lens
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.35, 1.5, GLASS_C, { cam: CAMS.door, me, refl: poseOf({}), door: 0, fog: 0.75, run: [1, 1, 1], drip: 1 });
  if (t >= tl) pop(t, tl, 1500, 250, () => tag('DO NOT LOOK BACK', 1500, 260, C.red, 54, 'center'));
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
// the grab: its arm comes out of the glass at G and closes around your left wrist (the one with the watch)
const G = [-0.26, 1.1, 0];
const GRAB = { ...WASH, look: 0.3, lean: 0.15, L: [-0.2, 0.98, 0.4], R: [0.1, 0.98, 0.36] };
const wristOf = ps => { const j = skeleton(ps); return V3.lerp(j.hand.L, j.elb.L, 0.15); };
function grabScene(t, me, k, o = {}) {
  // k: how far the arm is out (0..1); the thing stands right behind your reflection, its arm through the glass
  const wr = wristOf(me), th = { x: ME.x + 0.38, z: -ME.z - 0.55, t, reach: true, sc: 0.95 };
  return { cam: CAMS.otsL, me, door: 1, thing: th, ...o,
    inMirror: () => { const sh = [th.x - 0.15, 1.73 * th.sc, th.z]; greyArm(sh, G, wr, 1, true);
      // the part of the arm that is out in your room is a real thing in front of the glass, so the mirror shows it too: on your reflection's wrist
      if (k > 0) { greyArm(null, G, MIRROR(wr), k, false); if (k >= 1) gripWrist(MIRROR(wr), 1); } if (o.inMirror) o.inMirror(); },
    glassFx: () => { glassRipple(G, o.rip ?? -9, t); if (o.glassFx) o.glassFx(); },
    front: () => { if (k > 0) { greyArm(null, G, wr, k, false); if (k >= 1) gripWrist(wr, 1); } if (o.front) o.front(); } };
}
S.d1 = (t, seg) => {
  const th = wt(seg, 'hand'), tg = wt(seg, 'grey'), tw = wt(seg, 'wrist'), k = ease(prog(t, th, tw - th));
  const me = poseOf(GRAB);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.1, 1.5, wristOf(me), grabScene(t, me, k, { rip: th }));
  if (t >= tg) pop(t, tg, 1480, 280, () => tag('LONG GREY FINGERS', 1480, 290, C.fig, 46, 'center'));
  redFlash(t, tw, 0.08);
};
S.d2 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 500, () => {
    pop(t, seg.start, 960, 450, () => { hazard(560, 260, 800, 30, t * 40); rrS(560, 300, 800, 330, 10, C.fig, 5);
      spaced('WHAT DOES NOT WORK', 960, 482, '900 50px M', C.fig, 5); hazard(560, 640, 800, 30, -t * 40); });
  });
};
S.d3 = (t, seg) => {
  const tp = wt(seg, 'pull'), ts = wt(seg, 'stronger'), pull = ease(prog(t, tp - 0.1, 0.4)), back = ease(prog(t, ts, 0.5));
  const me = poseOf({ ...GRAB, lean: lerp(0.15, -0.12, pull) + 0.2 * back, L: [-0.2, 0.98, lerp(0.4, 0.3, pull) + 0.1 * back], x: ME.x, z: ME.z + 0.04 * pull - 0.06 * back });
  ctx.save(); if (pull > 0 && pull < 1) shake(4, t);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.2, 1.3, wristOf(me), grabScene(t, me, 1));
  ctx.restore();
  if (t >= tp) slideIn(t, tp, 40, 0, () => { xTag('PULL', 1560, 300, 56, prog(t, tp + 0.3, 0.3)); });
  if (t >= ts) pop(t, ts, 1480, 450, () => tag('STRONGER THAN YOU', 1480, 460, C.red, 44, 'center'));
};
// the glass cracks from where your fist hits it, and every piece has something looking out of it
const CRACK = [0.12, 1.5];
function cracks(t, k, eyes) {
  if (k <= 0) return; const rays = 11;
  ctx.save(); ctx.lineJoin = 'round';
  const shards = [];
  for (let i = 0; i < rays; i++) { const a = i / rays * Math.PI * 2 + hash(i) * 0.4, L = 0.9 * k; const pts = [[CRACK[0], CRACK[1]]];
    for (let s = 1; s <= 6; s++) { const r = L * s / 6, j = (hash(i * 13 + s) - 0.5) * 0.09; pts.push([CRACK[0] + Math.cos(a + j) * r, CRACK[1] + Math.sin(a + j) * r]); }
    const sp = pts.map(p => prj([p[0], p[1], 0.001])); ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]);
    ctx.strokeStyle = 'rgba(235,240,245,0.85)'; ctx.lineWidth = 2.5; ctx.stroke();
    const a2 = a + Math.PI / rays; shards.push([CRACK[0] + Math.cos(a2) * 0.28, CRACK[1] + Math.sin(a2) * 0.2]); }
  for (let r = 0.09; r < 0.5 * k; r += 0.11) { const ring = []; for (let i = 0; i <= rays; i++) { const a = i / rays * Math.PI * 2; ring.push(prj([CRACK[0] + Math.cos(a) * r * (0.8 + hash(i + r * 10) * 0.4), CRACK[1] + Math.sin(a) * r * (0.8 + hash(i * 3 + r) * 0.4), 0.001])); }
    ctx.beginPath(); ctx.moveTo(ring[0][0], ring[0][1]); for (const q of ring.slice(1)) ctx.lineTo(q[0], q[1]); ctx.strokeStyle = 'rgba(235,240,245,0.5)'; ctx.lineWidth = 1.8; ctx.stroke(); }
  // a face in every piece
  if (eyes > 0) shards.forEach((s, i) => { if (s[0] < MIR.x0 + 0.06 || s[0] > MIR.x1 - 0.06 || s[1] < MIR.y0 + 0.06 || s[1] > MIR.y1 - 0.06) return;
    const p = prj([s[0], s[1], -0.3]); if (!p) return; const e = clamp(eyes * 3 - i * 0.15); if (e <= 0) return;
    ctx.save(); ctx.globalAlpha *= e; glow('rgba(255,255,255,0.2)', 10); ell(p[0], p[1], 0.05 * p[3], 0.07 * p[3], 0.2, '#9a9a9f'); noGlow();
    for (const sg of [-1, 1]) ell(p[0] + sg * 0.018 * p[3], p[1], 0.01 * p[3], 0.016 * p[3], 0, '#050505'); ctx.restore(); });
  ctx.restore();
}
S.d4 = (t, seg) => {
  const tb = wt(seg, 'break'), tp = wt(seg, 'piece'), ck = ease(prog(t, tb + 0.05, 0.25));
  const me = poseOf({ ...GRAB, R: t < tb + 0.05 ? [lerp(0.1, CRACK[0] - ME.x, prog(t, tb - 0.4, 0.4)), lerp(0.98, CRACK[1], prog(t, tb - 0.4, 0.4)), lerp(0.36, ME.z - 0.08, prog(t, tb - 0.4, 0.4))] : [0.12, 1.2, 0.4] });
  ctx.save(); const hb = t - tb; if (hb > 0 && hb < 0.25) shake(8 * (1 - hb / 0.25), t);
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.35, [0.05, 1.5, 0], grabScene(t, me, 1, { glassFx: () => cracks(t, ck, prog(t, tp, 1.2)) }));
  ctx.restore();
  if (t >= tb) slideIn(t, tb, 40, 0, () => { xTag('BREAK IT', 1560, 300, 56, prog(t, tb + 0.3, 0.3)); });
  if (t >= tp + 0.6) pop(t, tp + 0.6, 1500, 450, () => tag('A NEW WINDOW', 1500, 460, C.red, 44, 'center'));
};
S.d5 = (t, seg) => {
  // someone comes to the door behind you: in the glass, their reflection, and the fingers on its shoulder too
  const tc = wt(seg, 'call'), tw = wt(seg, 'whoever'), tm = wt(seg, 'mirror'), come = ease(prog(t, tw - 0.3, 1.0));
  const me = poseOf(GRAB), helper = poseOf({ x: -0.15, z: lerp(3.9, 3.05, come), yaw: 0 });
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.4, [-0.1, 1.4, -2.0], grabScene(t, me, 1, {
    inMirror: () => { if (come > 0) { body3(helper, { mirror: true, col: '#cfcfd2' }); const j = skeleton(helper); if (t >= tm) { ctx.save(); ctx.globalAlpha *= prog(t, tm, 0.5); for (const s of ['L', 'R']) fingers3(MIRROR(V3.add(j.sh[s], [0, 0.03, 0])), [0, -1, 0.3], '#9a9a9f', 0.13); ctx.restore(); } } } }));
  if (t >= tc) slideIn(t, tc, 40, 0, () => { xTag('CALL FOR HELP', 1540, 300, 50, prog(t, tc + 0.3, 0.3)); });
};
S.d6 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, W / 2, 470, () => {
    pop(t, seg.start, 960, 470, () => { glow(); rrS(860, 370, 200, 200, 18, C.fig, 8); noGlow(); });
    check(960, 470, 64, prog(t, seg.end - 0.5, 0.4));
    fadeIn(t, seg.start + 0.3, () => spaced('ONLY ONE', 960, 680, '900 44px M', C.fig, 10));
  });
};
// your free hand, flat on the glass; then its hand, late, against yours
const PALM = [0.22, 1.42];
const handUp = k => ({ ...GRAB, look: 0, lean: lerp(0.15, 0.32, k), R: [lerp(0.1, PALM[0] - ME.x, k), lerp(0.98, PALM[1] - 0.02, k), lerp(0.36, ME.z - 0.06, k)] });
S.d7 = (t, seg) => {
  const tf = wt(seg, 'flat'), k = ease(prog(t, seg.start + 0.3, tf - seg.start - 0.2));
  const me = poseOf(handUp(k));
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.35, [0.08, 1.3, 0], grabScene(t, me, 1, { refl: poseOf(GRAB), front: () => { if (k > 0.97) palmOn(PALM, C.fig, 0.012); } }));
  if (t >= tf) pop(t, tf, 1500, 280, () => tag('FLAT ON THE GLASS', 1500, 290, C.fig, 46, 'center'));
};
S.d8 = (t, seg) => {
  const tp = wt(seg, 'press'), tpp = wt(seg, 'palm'), k2 = ease(prog(t, tp - 0.6, 1.1));
  const me = poseOf(handUp(1)), rp = poseOf(handUp(k2));
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.4, 1.9, [PALM[0], PALM[1], 0], grabScene(t, me, 1, { refl: rp,
    inMirror: () => { if (k2 > 0.97) palmOn(PALM, '#dcdcde', -0.012, true); },
    glassFx: () => { if (k2 > 0.97) { const c = prj([PALM[0], PALM[1], 0]); ctx.save(); const g = ctx.createRadialGradient(c[0], c[1], 5, c[0], c[1], 0.22 * c[3]); g.addColorStop(0, 'rgba(255,255,255,0.35)'); g.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = g; ctx.fillRect(c[0] - 300, c[1] - 300, 600, 600); ctx.restore(); } },
    front: () => palmOn(PALM, C.fig, 0.012) }));
  if (t >= tpp) pop(t, tpp, 1500, 280, () => tag('PALM TO PALM', 1500, 290, C.fig, 50, 'center'));
};
S.d9 = (t, seg) => {
  // it turns its back to you, takes hold of the grey arm and pulls; the hand lets go of your wrist and slides back into the glass
  const tt = wt(seg, 'turn'), tp = wt(seg, 'pull'), to = wt(seg, 'off');
  const turn = ease(prog(t, tt - 0.1, 0.6)), rel = ease(prog(t, to - 0.1, 0.5));
  const me = poseOf(handUp(1 - ease(prog(t, to, 0.6)))), wr = wristOf(me);
  const th = { x: ME.x + 0.38, z: -ME.z - 0.55, t, reach: true, sc: 0.95 };
  const rp = poseOf({ yaw: Math.PI * turn, z: ME.z + 0.1 * turn, L: [-0.15, 1.15, 0.3 * turn], R: [0.15, 1.15, 0.3 * turn] });
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.2, 1.45, [0.0, 1.35, -0.4], { cam: CAMS.otsL, me, refl: rp, door: 1, thing: th,
    inMirror: () => { const sh = [th.x - 0.15, 1.73 * th.sc, th.z]; const g2 = V3.lerp(G, [G[0], G[1], -0.3], rel); greyArm(sh, g2, wr, 1, true);
      if (rel < 1) { greyArm(null, G, MIRROR(wr), 1 - rel, false); if (rel < 0.15) gripWrist(MIRROR(wr), 1); } },
    glassFx: () => glassRipple(G, to, t),
    front: () => { if (rel < 1) { greyArm(null, G, wr, 1 - rel, false); if (rel < 0.15) gripWrist(wr, 1); } } });
  if (t >= tp) pop(t, tp, 1500, 280, () => tag('IT PULLS IT OFF YOU', 1500, 290, C.fig, 46, 'center'));
};
S.d10 = (t, seg) => {
  // you back away. In the glass they fight; do not watch
  const tw = wt(seg, 'watch'), b = ease(prog(t, seg.start, 1.4));
  const me = poseOf({ z: lerp(ME.z, 1.35, b), lean: -0.05 });
  const shake2 = Math.sin(t * 23) * 0.04;
  shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.3, GLASS_C, { me, refl: poseOf({ yaw: Math.PI, x: ME.x + shake2, z: ME.z + 0.2, L: [-0.15, 1.2, 0.35], R: [0.15, 1.2, 0.35] }), door: 1,
    thing: { x: ME.x + 0.1 - shake2, z: -ME.z - 0.75, t: t * 4, sc: 0.95 } });
  if (t >= tw) pop(t, tw, 1500, 280, () => tag('DO NOT STAY', 1500, 290, C.red, 54, 'center'));
};
S.d11 = (t, seg) => {
  const tc = wt(seg, 'towel'), th = wt(seg, 'hear'), tl = wt(seg, 'lift');
  const tk = ease(prog(t, tc - 0.4, 0.5)), bump = t >= th ? Math.max(0, Math.sin((t - th) * 5.5)) ** 3 : 0;
  shot(t, seg.start, seg.end - seg.start + 1.2, 1.05, 1.2, GLASS_C, { me: poseOf({ z: 1.35 }), refl: poseOf({ yaw: Math.PI, z: ME.z + 0.2 }), door: 1, thing: { x: ME.x + 0.1, z: -ME.z - 0.75, t: t * 4, sc: 0.95 },
    towel: tk, bump, bx: -0.1 + 0.25 * Math.sin(Math.floor((t - th) * 5.5 / Math.PI) * 2.3), by: 1.45 + 0.15 * Math.cos(Math.floor((t - th) * 1.75) * 1.7) });
  if (t >= tl) pop(t, tl, 1500, 280, () => tag('DO NOT LIFT IT', 1500, 290, C.red, 54, 'center'));
};

// ---------- morning ----------
function morning(fn) { fn(); ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.1; ctx.fillStyle = '#ffe6c8'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
S.e1 = (t, seg) => {
  const td = wt(seg, 'down'), tx = wt(seg, 'exactly'), tk = 1 - ease(prog(t, td - 0.3, 0.5));
  morning(() => shot(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.15, GLASS_C, { me: poseOf({}), towel: tk, light: 1 }));
  slideIn(t, seg.start + 0.3, 40, 0, () => text('7:00 AM', 1560, 200, '700 54px Plex', C.fig));
  if (t >= tx) pop(t, tx, 1500, 330, () => { tag('ON TIME', 1500, 340, C.fig, 54, 'center'); });
};
S.e2 = (t, seg) => {
  const tu = wt(seg, 'up'), tw = wt(seg, 'wash'), wk = prog(t, tw - 0.3, 0.4);
  const pose = { ...poseOf(lookUp(t, tu + 0.1)), ...(wk > 0 ? washing(t, wk) : {}), look: wk > 0 ? 0.6 : poseOf(lookUp(t, tu + 0.1)).look };
  morning(() => shot(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.35, [ME.x, 1.5, -ME.z], { me: poseOf(pose), water: wk }));
  [[tu, 'LOOK UP', 300], [tw, 'WASH', 430]].forEach(([t0, l, y]) => { if (t >= t0) slideIn(t, t0, 40, 0, () => { text(l, 1420, y + 16, '900 48px M', C.fig, 'left'); check(1370, y, 26, prog(t, t0 + 0.2, 0.3)); }); });
};
// from the doorway: you turn your back on the mirror and walk out. So does it. Its back is covered in marks; yours is not
const E_CAM = { x: 0.9, y: 1.62, z: 3.05, yaw: 0.2, pitch: -0.07, f: 1000 };
function leaving(t, seg3) {
  const tt = wt(seg3, 'turn'), k = ease(prog(t, tt - 0.2, 0.9)), w = prog(t, tt + 0.6, 2.4);
  return poseOf({ yaw: Math.PI * k, x: lerp(ME.x, -0.55, ease(w)), z: lerp(ME.z, 1.45, w), walk: w > 0 && w < 1, step: t * 8, L: [-0.22, 0.8, 0.12 * Math.sin(t * 8) * (w > 0 && w < 1)], R: [0.22, 0.8, -0.12 * Math.sin(t * 8) * (w > 0 && w < 1)] });
}
S.e3 = (t, seg) => {
  const me = leaving(t, seg);
  morning(() => shot(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.1, GLASS_C, { cam: E_CAM, me, scars: 1 }));
};
S.e4 = (t, seg) => {
  const s3 = window.TL.segments.find(s => s.id === 'e3'), me = leaving(t, s3);
  const rb = MIRROR(skeleton(me).chest);
  morning(() => shot(t, seg.start, seg.end - seg.start + 1.4, 1.4, 3.2, rb, { cam: E_CAM, me, scars: 1 }));
  redFlash(t, seg.start + 0.9, 0.04);
};
// the file closes
S.e5 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], ['404', 150]], -0.1); ctx.restore();
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

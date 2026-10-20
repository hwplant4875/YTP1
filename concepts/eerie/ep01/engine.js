// Instruction 404, EP01 "If Your Cat Ever Knocks On Your Bedroom Door". Canvas renderer: window.draw(t).
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
    const lines = []; let cur = '';
    for (const w of ws.slice(0, shown)) { if ((cur + ' ' + w).trim().length > 16) { lines.push(cur); cur = w; } else cur = (cur + ' ' + w).trim(); }
    if (cur) lines.push(cur);
    lines.forEach((l, i) => text(l, 830, 446 + i * 74, '900 68px M', C.fig, 'left'));
    lnP(560, 580, 1360, 580, 5, C.fig, easeOut(prog(t, t0 + 0.3, 0.6)));
    for (let i = 0; i < 4; i++) { const x = 560 + i * 54, y = 618; ctx.save(); ctx.globalAlpha *= prog(t, t0 + 0.4 + i * 0.06, 0.2);
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
function room(t, o = {}) {
  bedroomDecor(t, o); hallDecor(t, o);
  ln(0, FY, W, FY, 4, C.dim);
  bed(150, FY, 1.05, o.person || 'woke', { look: 1, cat: o.bedCat, t });
  doorEdge(DOOR_X, FY, o.open || 0);
  if (o.hall) o.hall();
}
// knock-synced standing cat in the hallway; eyes go red while knocks land (scary)
function knocker(t, extra = {}) {
  const p = knockPulse(t);
  standCat(CAT_X, FY, CAT_S, { k: p > 0 ? 1 - p : 0.75, red: extra.red ?? Math.max(p, extra.redBase || 0), tilt: extra.tilt ?? (-6 + 3 * Math.sin(t * 0.8)), t, ...extra });
}
function knockFx(t, t0 = -1) {
  const p = knockPulse(t), lk = lastKnock(t);
  knockLines(DOOR_X - 34, KNOCK_Y, p, C.red, 1);
  if (lk > t0) ripple(DOOR_X, KNOCK_Y, lk, t, C.red, 10, 110);
}
const S = {};
S.s01 = (t, seg) => {
  const p = knockPulse(t);
  cam(t, 0, 8, 1.0, 1.07, 1080, 560, () => {
    ctx.save(); if (p > 0.6) shake(3 * p, t);
    room(t, { light: 0.5, hall: () => knocker(t, { red: 0 }) });
    ctx.restore(); knockFx(t);
  });
  if (t > wt(seg, 'not') - 0.05 && t < seg.end + 1) pop(t, wt(seg, 'not') - 0.05, 960, 190, () => { tag('DO NOT OPEN', 960, 200, C.red, 46, 'center'); }, 0.3);
};
S.s02 = (t, seg) => {
  const items = [['getup', 520, 'get'], ['bulb', 960, 'turn'], ['mouth', 1400, 'call']];
  cam(t, seg.start, seg.end - seg.start, 1, 1.04, W / 2, 470, () => {
    items.forEach(([ic, x, w]) => {
      const t0 = wt(seg, w) - 0.25;
      pop(t, t0, x, 470, () => { rrS(x - 170, 300, 340, 340, 26, C.dim, 5); icon(ic, x, 470, 1.05); });
      redX(x, 470, 120, prog(t, wt(seg, w) + 0.35, 0.35));
    });
  });
};
// ---------- opening: the protocol file and its four rules ----------
const P = { x: 510, y: 110, w: 900, h: 800 };
// left-aligned text shrunk to fit a width
function fitText(str, x, y, maxW, size, col) { ctx.font = `900 ${size}px M`; const w = ctx.measureText(str).width; if (w > maxW) size = Math.floor(size * maxW / w); text(str, x, y, `900 ${size}px M`, col, 'left'); }
const ROWY = i => P.y + 150 + i * 158;
// rubber stamp: double red border, worn ink, slams down from above
function stampMark(t, t0, x, y, lines, rot = -0.12, paper = '#e6e6e6') {
  if (t < t0) return;
  const k = clamp((t - t0) / 0.13), s = lerp(1.8, 1, easeOut(k));
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); ctx.globalAlpha *= clamp(k * 4);
  let w = 0, h = 0; for (const [str, sz] of lines) { ctx.font = `900 ${sz}px M`; ctx.letterSpacing = sz * 0.08 + 'px'; w = Math.max(w, ctx.measureText(str).width); h += sz * 1.05; }
  w += 70; h += 46;
  rrS(-w / 2, -h / 2, w, h, 10, C.red, 9); rrS(-w / 2 + 14, -h / 2 + 14, w - 28, h - 28, 6, C.red, 3);
  let yy = -h / 2 + 22; for (const [str, sz] of lines) { yy += sz * 1.0; ctx.font = `900 ${sz}px M`; ctx.letterSpacing = sz * 0.08 + 'px'; text(str, 0, yy - sz * 0.08, `900 ${sz}px M`, C.red); }
  ctx.letterSpacing = '0px';
  // worn ink: paper-coloured specks knocked out of the stamp
  for (let i = 0; i < 70; i++) { const px = (hash(i * 3.1) - 0.5) * w, py = (hash(i * 7.7) - 0.5) * h; circ(px, py, 1.5 + hash(i) * 3, paper); }
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
  const rows = [['SUBJECT', null], ['LOCATION', 'YOUR BEDROOM'], ['TIME', '03:00 AM']];
  rows.forEach(([l, v], i) => { const y = P.y + 270 + i * 82;
    text(l, P.x + 60, y, '600 28px Plex', '#666', 'left'); ln(P.x + 250, y + 12, P.x + P.w - 60, y + 12, 2, '#bbb');
    if (v === null) rr(P.x + 260, y - 30, 330, 40, 3, '#111');
    else { ctx.save(); ctx.filter = 'blur(9px)'; text(v, P.x + 262, y, '900 36px M', i === 2 ? '#d61f1f' : '#111', 'left'); ctx.restore(); } });   // classified: blurred
  // barcode and a hazard edge
  for (let i = 0; i < 40; i++) { const bw = hash(i * 1.7) < 0.35 ? 6 : 3; rr(P.x + P.w - 300 + i * 6.4, P.y + P.h - 170, bw, 70, 0, '#111'); }
  text('NO. 0404', P.x + P.w - 172, P.y + P.h - 74, '600 24px Plex', '#444');
  text('DO NOT REMOVE FROM THE BEDROOM', P.x + 60, P.y + P.h - 130, '600 22px Plex', '#666', 'left');
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
  if (name === 'warn') { const tri = () => { ctx.beginPath(); ctx.moveTo(0, -50); ctx.lineTo(50, 40); ctx.lineTo(-50, 40); ctx.closePath(); };
    ctx.lineJoin = 'round'; tri(); ctx.fillStyle = C.red; ctx.fill(); if (col === '#fff') { ctx.lineWidth = 6; ctx.strokeStyle = '#fff'; ctx.stroke(); }
    rr(-6, -22, 12, 38, 5, '#fff'); circ(0, 28, 7, '#fff'); }
  if (name === 'fist') { rr(-34, -34, 68, 64, 18, col); for (let i = 1; i < 4; i++) ln(-34 + i * 17, -34, -34 + i * 17, -10, 3, '#ff2b2b'); }
  ctx.restore();
}
const RULES = [['door', 'THE DOOR', ''], ['gap', 'THE GAP UNDER IT', ''], ['eye', 'YOUR EYES', ''], ['warn', 'EMERGENCY PROTOCOL', 'HOW TO FIGHT BACK']];
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
      fitText(RULES[i][1], P.x + 310, y + (RULES[i][2] ? 62 : 82), P.w - 370, 50, ink);
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
}
S.s06 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT OPEN THE DOOR');
const DF = { x: 760, y: 120, w: 400, h: 740 };   // standard front-view door; DMID is where the knocks land
const DMID = { x: DF.x + DF.w / 2, y: DF.y + DF.h * 0.28 };
S.s07 = (t, seg) => {
  const tb = wt(seg, 'bottom'), tm = wt(seg, 'middle');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, 960, 500, () => {
    doorFront(DF.x, DF.y, DF.w, DF.h, {});
    pop(t, seg.start + 0.1, 420, 500, () => icon('ear', 420, 500, 1.2));
    if (t < tb) { ripple(DMID.x, DMID.y, seg.start + 0.3, t, C.mid); ripple(DMID.x, DMID.y, seg.start + 1.2, t, C.mid); }
    if (t >= tb) { ripple(DMID.x, DF.y + DF.h - 30, tb + Math.floor((t - tb) / 1.2) * 1.2, t, C.mid, 10, 90, 5);
      pop(t, tb, 1260, DF.y + DF.h - 20, () => { text('NOT HERE', 1260, DF.y + DF.h - 10, '900 46px M', C.mid, 'left'); ln(1250, DF.y + DF.h - 22, 1510, DF.y + DF.h - 22, 6, C.mid); }); }
    if (t >= tm) { for (let k = 0; k < 5; k++) ripple(DMID.x, DMID.y, tm + k * 0.5, t, C.red, 20, 210);
      pop(t, tm, 1260, DMID.y, () => { redGlow(18); text('HERE', 1260, DMID.y + 26, '900 84px M', C.red, 'left'); ln(1240, DMID.y, 1150, DMID.y, 9, C.red); noGlow(); }); }
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
S.s08 = (t, seg) => {
  const ts = wt(seg, 'scratch'), tp = wt(seg, 'push'), tc = wt(seg, 'cry');
  const o = { collar: true }; if (t >= ts && t < tp) o.paw = t; if (t >= tp && t < tc) o.push = true;
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.04, 700, 600, () => {
    ctx.save(); if (t >= tp && t < tc) ctx.translate(Math.sin((t - tp) * 18) * 3 * (1 - prog(t, tp, 1)), 0);
    doorFront(560, 170, 360, 690, {}); ctx.restore();
    sitCat(420, 860, 1.7, o);
    if (t >= ts) { ctx.save(); ctx.globalAlpha *= 0.8; for (let i = 0; i < 3; i++) lnP(580 + i * 22, 840 - i * 6, 610 + i * 22, 780 - i * 6, 6, C.fig, prog(t, ts + i * 0.1, 0.15)); ctx.restore(); }
    if (t >= tc) bubbleTo(300, 540, 250, 110, 'MEOW', t, tc, 500, 668);   // the tail points at the cat
    catChecklist(t, [['SCRATCH', ts, 'v'], ['PUSH', tp, 'v'], ['CRY', tc, 'v']]);
  });
};
S.s09 = (t, seg) => {
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
    pop(t, tc + 0.45, 960, 480, () => { redGlow(14); ln(910, 450, 1010, 450, 12, C.red); ln(910, 510, 1010, 510, 12, C.red); ln(990, 410, 930, 550, 12, C.red); noGlow(); });
    fadeIn(t, tc + 0.1, () => { spaced('CAT', 640, 700, '900 40px M', C.mid, 8); spaced('KNOCK', 1280, 700, '900 40px M', C.mid, 8); });
  });
};
// you, standing at the door: the mirror image of the cat across it, so your eye is level with its eye
const YOU = { s: 1.2 }; YOU.x = 2 * DOOR_X - CAT_EYE.x - 14 * YOU.s;
S.s10 = (t, seg) => {
  // the knock lands in the middle of the door; a person knocking puts the hand there, and the eye behind the door sits level with yours
  const tw = wt(seg, 'where'), kn = evs('knock3').find(e => e.t > seg.start);
  if (kn && t >= kn.t - 0.05) {
    const k = t - kn.t;
    cam(t, kn.t, 1.8, 1.14, 1.0, 1200, 560, () => { room(t, { light: 0.5, hall: () => knocker(t, { redBase: k < 1.2 ? 1 - k / 1.2 : 0 }) }); knockFx(t, kn.t - 0.1); });
    return;
  }
  const ex = YOU.x + 14 * YOU.s, ey = FY - 336 * YOU.s;
  cam(t, seg.start, seg.end - seg.start + 1.2, 1.12, 1.2, 1080, 560, () => {
    ln(0, FY, W, FY, 4, C.dim); doorEdge(DOOR_X, FY);
    for (let i = 0; i < 3; i++) ripple(DOOR_X, KNOCK_Y, seg.start + 0.3 + i * 0.6, t, C.red, 10, 120);
    // at "where a hand would knock" you step up and knock on the same spot, twice
    if (t >= tw - 0.15) {
      const kts = [tw + 0.35, tw + 0.85]; let back = 1;
      for (const kt of kts) back = Math.min(back, clamp(Math.abs(t - kt) / 0.22));
      if (t > kts[1]) back = 0.15;
      const reach = ease((t - tw + 0.15) / 0.35);
      const hand = { x: lerp(YOU.x + 40, DOOR_X - 24 - 34 * back, reach), y: lerp(FY - 200 * YOU.s, KNOCK_Y, reach) };
      fadeIn(t, tw - 0.15, () => person(YOU.x, FY, YOU.s, C.mid, 0, 0, { eye: 1, hand }), 0.25);
      for (const kt of kts) ripple(DOOR_X, KNOCK_Y, kt, t, C.fig, 10, 90, 4);
      // the eye behind the door, level with yours
      fadeIn(t, tw + 0.2, () => { redGlow(26); geoEye(CAT_EYE.x, CAT_EYE.y, 1); noGlow(); }, 0.5);
      if (t >= tw + 0.6) { ctx.setLineDash([10, 10]); lnP(ex + 12, ey, CAT_EYE.x - 14, CAT_EYE.y, 3, 'rgba(255,255,255,0.7)', prog(t, tw + 0.6, 0.5)); ctx.setLineDash([]); }
    }
  });
};
S.s11 = (t, seg) => {
  // you, shaking, take the handle; behind the door only its red eye. Then the door opens, it is there, one swipe, and black.
  const to = wt(seg, 'open'), dop = evs('dooropen').find(e => e.t > seg.start), sw = evs('swipe').find(e => e.t > seg.start);
  const CX = 1196, PXs = 984, PS = YOU.s;
  const eye = { x: CX - 40 * CAT_S, y: FY - 360 * CAT_S }, neck = { x: PXs + 4 * PS, y: FY - 296 * PS };
  const handle = { x: DOOR_X - 38, y: FY - DOOR_H * 0.42 };
  const op = dop ? 0.62 * ease((t - dop.t) / 0.4) : 0, rev = dop ? ease((t - dop.t - 0.12) / 0.45) : 0;
  const T0 = sw ? sw.t + 0.02 : 1e9, u = (t - T0) / 0.1, reach = u > 0 && u < 1 ? Math.sin(Math.PI * u) : 0;
  const z = lerp(1.25, 1.42, ease((t - seg.start) / (seg.end - seg.start + 1.4)));
  ctx.save(); ctx.translate(960, 540); ctx.scale(z, z); ctx.translate(-1080, -580);
  bedroomDecor(t, {}); hallDecor(t, { light: 0 }); ln(0, FY, W, FY, 4, C.dim);
  // the cat: only the eye until the door opens, then it comes out of the dark
  if (rev > 0) { ctx.save(); ctx.globalAlpha *= rev; standCat(CX, FY, CAT_S, { k: 1, arm: u > 0 && u < 1.6 ? 'none' : 'down', red: 1, tilt: -6, sway: -7 * reach, t }); ctx.restore(); }
  else { const fl = 0.75 + 0.25 * Math.sin(t * 5); ctx.save(); ctx.globalAlpha *= fl; redGlow(30); geoEye(eye.x, eye.y, 1); noGlow(); ctx.restore(); }
  doorEdge(DOOR_X, FY, op);
  // you, trembling, hand on the handle
  const tr = t < (dop ? dop.t : 1e9) ? 1 : 0.4, hk = ease((t - to + 0.1) / 0.5);
  ctx.save(); ctx.translate(Math.sin(t * 47) * 2.4 * tr, Math.cos(t * 39) * 1.3 * tr);
  const hand = { x: lerp(PXs + 40, handle.x, hk) - (op > 0 ? 150 * op : 0), y: lerp(FY - 190 * PS, handle.y, hk) + Math.sin(t * 31) * 2 * tr };
  person(PXs, FY, PS, C.fig, 0, 0, { eye: 1, hand: t >= to - 0.1 ? hand : null });
  ctx.restore();
  // the swipe: from its resting pose straight to your throat and back in 0.1 s, smeared by motion blur
  if (u > -0.05 && u < 1.6) {
    const sh = { x: CX - 28 * CAT_S - 26 * reach, y: FY - 278 * CAT_S }, rest = { x: CX - 34 * CAT_S, y: FY - 166 * CAT_S };
    const pawAt = v => { const r = v > 0 && v < 1 ? Math.sin(Math.PI * v) : 0; return { x: lerp(rest.x, neck.x - 18, r), y: lerp(rest.y, neck.y, r) - Math.sin(Math.PI * r) * 30 }; };
    ctx.save();
    for (let j = 7; j >= 1; j--) { const q = pawAt(u - j * 0.07), a = (1 - j / 8) * 0.35; ctx.globalAlpha = a * rev; ln(sh.x, sh.y, q.x, q.y, 24, '#ffffff'); circ(q.x, q.y, 18, '#ffffff'); }
    ctx.restore();
    const p = pawAt(u); glow('rgba(255,255,255,0.4)', 18); ln(sh.x, sh.y, p.x, p.y, 24, '#eeeeee'); circ(p.x, p.y, 17, '#eeeeee'); noGlow();
  }
  if (u >= 0.5) { ctx.save(); redGlow(14); lnP(neck.x + 26, neck.y - 4, neck.x - 26, neck.y + 4, 4, C.red, clamp((u - 0.5) * 4)); ctx.restore(); }
  ctx.restore();
};
S.s12 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT LOOK UNDER THE DOOR');
S.s13 = (t, seg) => {
  const tl = wt(seg, 'light'), tn = wt(seg, 'not');
  const fl = t < tl ? 0 : ((t - tl) < 0.35 ? ((t * 30 | 0) % 2) : 1);
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, 960, 700, () => {
    doorFront(DF.x, DF.y, DF.w, DF.h, { light: fl });
    pop(t, tn, 480, 480, () => { rrS(400, 360, 160, 240, 16, C.mid, 5); rr(450, 410, 60, 140, 10, C.dark); rr(458, 480, 44, 62, 8, C.fig); text('OFF', 480, 650, '900 36px M', C.mid); });
    pop(t, tn + 0.2, 1450, 480, () => { tag('HALLWAY: ON', 1360, 490, C.red, 40); });
  });
};
S.s14 = (t, seg) => {
  const tt = wt(seg, 'two'), tf = wt(seg, 'cat');
  if (t < tf - 0.1) {
    const k = ease((t - seg.start) / Math.max(0.5, tt - seg.start)), z = lerp(1, 2.4, k);
    ctx.save(); ctx.translate(960, lerp(860, 520, k)); ctx.scale(z, z); ctx.translate(-960, -860);
    doorFront(DF.x, DF.y, DF.w, DF.h, { light: 1, feet: t >= tt ? [{ x: 0.36, a: prog(t, tt, 0.4) }, { x: 0.62, a: prog(t, tt + 0.25, 0.4) }] : [] });
    ctx.restore();
    if (t >= tt) pop(t, tt + 0.3, 1640, 300, () => { spaced('SHADOWS', 1640, 240, '900 34px M', C.mid, 6); text('2', 1640, 400, '900 150px M', C.fig); });
    return;
  }
  cam(t, tf, seg.end - tf + 0.6, 1, 1.05, W / 2, 480, () => {
    pop(t, tf - 0.05, 620, 470, () => { sitCat(560, 600, 2.2, {}); });
    pop(t, tf + 0.15, 1240, 470, () => { for (let i = 0; i < 4; i++) icon('foot', 1080 + i * 100, 470, 1.0); });
    fadeIn(t, tf + 0.3, () => { spaced('A CAT', 620, 760, '900 36px M', C.mid, 6); text('4', 1240, 700, '900 110px M', C.fig); });
  });
};
S.s15 = (t, seg) => {
  const tn = wt(seg, 'number');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1, 1.12, 960, 820, () => {
    doorFront(560, -260, 800, 1100, { light: 1, feet: [{ x: 0.36 }, { x: 0.62 }] });
    const flick = (t * 20 | 0) % 9 === 0;
    pop(t, seg.start, 960, 420, () => { if (t >= tn) redGlow(30); else glow(); text('2', 960 + (flick ? 6 : 0), 520, '900 300px M', t >= tn ? C.red : C.fig); noGlow(); });
    redX(960, 420, 150, prog(t, wt(seg, 'count') + 0.1, 0.35) * (t < tn ? 1 : 0));
  });
};
function meowWave(t, t0, dur, y = 500) {
  const k = (t - t0) / dur; if (k < 0 || k > 1) return;
  ctx.save(); redGlow(20); ctx.beginPath();
  for (let x = 300; x <= 1620; x += 6) { const env = Math.sin(Math.PI * clamp((x - 300) / 1320)) * Math.sin(Math.PI * k);
    const yy = y + Math.sin(x * 0.045 + t * 9) * 110 * env * (0.6 + 0.4 * Math.sin(x * 0.011 - t * 3)); x === 300 ? ctx.moveTo(x, yy) : ctx.lineTo(x, yy); }
  ctx.strokeStyle = C.red; ctx.lineWidth = 7; ctx.stroke(); noGlow(); ctx.restore();
}
S.s16 = (t, seg) => {
  const m = evs('meow1')[0];
  cam(t, seg.start, 5, 1, 1.08, W / 2, 500, () => {
    doorFront(DF.x, DF.y, DF.w, DF.h, { light: 0.6 });
    if (m && t >= m.t) { meowWave(t, m.t, 3.2);
      const k = (t - m.t) / 3.2; if (k < 1) { const s = 'M E O W'.slice(0, Math.max(1, Math.floor(k * 9)));
        ctx.save(); ctx.translate(960, 300); ctx.scale(1 + k * 0.6, 1 - k * 0.15); redGlow(14); text(s, 0, 0, '900 110px M', C.red, 'center', 'middle'); noGlow(); ctx.restore(); } }
  });
};
// Rule 2's end: the meow draws you to the door, you look through the keyhole, and it is already looking back
const KEY = { x: DF.x + DF.w * 0.88, y: DF.y + DF.h * 0.58 + 33 };
S.k1 = (t, seg) => {
  const tk = wt(seg, 'keyhole'), k = ease((t - seg.start) / (seg.end - seg.start + 0.35)), z = Math.pow(40, k);
  const bob = Math.sin((t - seg.start) * 5.2) * 6 * (1 - k);
  ctx.save(); ctx.translate(960, 540 + bob); ctx.scale(z, z); ctx.translate(-lerp(960, KEY.x, ease(k * 1.4)), -lerp(500, KEY.y, ease(k * 1.4)));
  doorFront(DF.x, DF.y, DF.w, DF.h, { light: 0.6, keyLight: 0.6 + 0.4 * prog(t, tk - 0.3, 0.6) });
  ctx.restore();
};
function keyholeMask() { ctx.beginPath(); ctx.arc(960, 420, 200, 0.62 * Math.PI, 2.38 * Math.PI); ctx.lineTo(1100, 860); ctx.lineTo(820, 860); ctx.closePath(); }
S.k2 = (t, seg) => {
  const ta = wt(seg, 'already') - 0.05, z = lerp(1, 1.08, ease((t - ta) / 3));
  ctx.save(); ctx.translate(960, 540); ctx.scale(z, z); ctx.translate(-960, -540);
  keyholeMask(); ctx.save(); ctx.clip();
  if (t < ta) {   // the hallway, lit and empty
    const g = ctx.createLinearGradient(0, 200, 0, 880); g.addColorStop(0, '#6a6458'); g.addColorStop(1, '#2a2722'); ctx.fillStyle = g; ctx.fillRect(700, 180, 520, 700);
    rr(700, 720, 520, 160, 0, '#1c1a17'); ln(700, 720, 1220, 720, 4, '#3c3833');
  } else {        // its face fills the hole: white fur, one red eye, slit pupil
    const p = 0.5 + 0.5 * Math.sin((t - ta) * 2.2), dil = 1 + 0.25 * ease((t - ta - 1.2) / 1.5);
    rr(700, 180, 520, 700, 0, '#e4e4e4'); ctx.save(); ctx.globalAlpha = 0.25; for (let i = 0; i < 26; i++) ln(700 + hash(i) * 520, 200 + hash(i * 3.3) * 660, 700 + hash(i) * 520 + 30, 200 + hash(i * 3.3) * 660 + 12, 4, '#9a9a9a'); ctx.restore();
    ell(960, 440, 205, 180, 0, '#000');
    ctx.save(); redGlow(40 + 20 * p); ell(960, 440, 175, 155, 0, C.red); ctx.restore();
    ell(960, 440, 24 * dil, 140, 0, '#000'); circ(1020, 380, 18, 'rgba(255,255,255,0.85)');
  }
  ctx.restore();
  // a soft vignette inside the keyhole edge
  ctx.save(); keyholeMask(); ctx.strokeStyle = 'rgba(0,0,0,0.9)'; ctx.lineWidth = 30; ctx.filter = 'blur(12px)'; ctx.stroke(); ctx.restore();
  ctx.restore();
};
const HEAD = { x: 150 + 112 * 1.05, y: FY - 238 * 1.05 };      // your head on the pillow, asleep
// the bedroom with the cat standing behind the bed (the bed hides its legs)
function bedside(t, o) {
  bedroomDecor(t, {}); hallDecor(t, { light: 0.4 }); ln(0, FY, W, FY, 4, C.dim);
  if (o.cat) o.cat();
  rr(150 + 26 * 1.05, FY - 110 * 1.05, 530 * 1.05, 110 * 1.05, 0, '#070707');   // the dark under the bed hides the cat's legs behind it
  bed(150, FY, 1.05, 'sleep', { cat: o.bedCat || 'empty', t });
  if (o.front) o.front();
  doorEdge(DOOR_X, FY, o.open ?? 0.9);
}
// the cat leaning over the bed: same design, the whole body tips from the feet toward your face
const OVER = { x: 470, sway: -17 };
const overCat = (t, o = {}) => standCat(OVER.x, FY, CAT_S, { k: 1, arm: 'down', red: 0, sway: OVER.sway, tilt: -14, t, ...o });
S.r1 = (t, seg) => ruleCard(t, seg, 3, 'PRETEND TO BE ASLEEP');
S.r2 = (t, seg) => {
  const ts = wt(seg, 'stops'), tsi = wt(seg, 'cat') - 0.1, ta = wt(seg, 'always'), te = wt(seg, 'enter');
  if (t < tsi - 0.15) {
    // the knocking, then nothing
    cam(t, seg.start, tsi - seg.start, 1, 1.05, 1000, 560, () => room(t, { person: 'sleep', light: 0.5,
      hall: () => knocker(t, { red: 0, k: t < ts ? 0.25 + 0.6 * Math.abs(Math.sin(t * 6)) : 1 }) }));
    if (t < ts) { const k = (t * 1.6) % 1; knockLines(DOOR_X - 34, KNOCK_Y, k < 0.3 ? 1 - k / 0.3 : 0, C.fig, 1); }
    if (t >= ts) pop(t, ts, 1500, 240, () => tag('SILENCE', 1500, 250, C.fig, 40, 'center'));
    return;
  }
  // it did not leave: it is standing right there, and the door begins to move
  const open = 0.18 * ease((t - te) / 0.8);
  cam(t, tsi - 0.15, seg.end - tsi + 1, 1.25, 1.4, 1180, 520, () => room(t, { person: 'sleep', light: 0.5, open, hall: () => knocker(t, { red: 0, k: 1, tilt: -10 }) }));
  if (t >= ta) pop(t, ta, 1560, 330, () => tag('IT ALWAYS COMES IN', 1560, 340, C.fig, 34, 'center'));
};
S.r3 = (t, seg) => {
  // the lever handle, turning slowly
  const ts = wt(seg, 'slowly'), tp = wt(seg, 'practicing');
  const k = ease((t - seg.start - 0.4) / 2.6);
  cam(t, seg.start, seg.end - seg.start + 1, 2.0, 2.4, DF.x + DF.w * 0.8, DF.y + DF.h * 0.58, () => {
    ctx.save(); shake(0.8, t); doorFront(DF.x, DF.y, DF.w, DF.h, { handle: k, light: 0.5 }); ctx.restore();
    if (t >= ts) { ctx.save(); ctx.globalAlpha *= 0.7; ctx.setLineDash([6, 8]); ctx.beginPath(); ctx.arc(DF.x + DF.w * 0.88, DF.y + DF.h * 0.58, 90, Math.PI * 0.98, Math.PI * 0.98 - 0.66 * prog(t, ts, 1.2), true); ctx.strokeStyle = C.fig; ctx.lineWidth = 4; ctx.stroke(); ctx.setLineDash([]); ctx.restore(); }
  });
  if (t >= ts) pop(t, ts, 1500, 240, () => tag('SLOWLY', 1500, 250, C.fig, 40, 'center'));
  if (t >= tp) pop(t, tp, 1500, 350, () => tag('PRACTICED', 1500, 360, C.red, 44, 'center'));
};
function bigEye(x, y, s, lid, red, squeeze = 0, quiver = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(-150, 0); ctx.quadraticCurveTo(0, -110 * (1 - lid), 150, 0); ctx.quadraticCurveTo(0, 110 * (1 - lid), -150, 0); ctx.closePath();
  glow(); ctx.fillStyle = C.fig; ctx.fill(); noGlow();
  if (lid < 0.85) { ctx.save(); ctx.clip(); circ(0, 0, 56, red ? C.red : '#222'); circ(0, 0, 24, '#000'); circ(18, -18, 10, '#fff'); ctx.restore(); }
  ctx.beginPath(); ctx.moveTo(-150, 0); ctx.quadraticCurveTo(0, -110 * (1 - lid), 150, 0); ctx.strokeStyle = C.fig; ctx.lineWidth = 8; ctx.stroke();
  if (lid >= 0.95 && !squeeze) for (let i = -2; i <= 2; i++) { const q = quiver * Math.sin(T_ * 37 + i * 1.7) * 4; ln(i * 40, 4, i * 48 + q, 34 + Math.abs(q) * 0.5, 6, C.fig); }
  if (squeeze) { // a tight, crumpled lid: wrinkles fanning out from the corners
    for (const d of [-1, 1]) for (let i = 0; i < 3; i++) ln(d * (150 + 10), -30 + i * 30, d * (220 + i * 10), -50 + i * 50, 7, C.fig);
    for (let i = 0; i < 3; i++) ln(-70 + i * 70, -40, -60 + i * 70, -70, 6, C.fig); }
  ctx.restore();
}
let T_ = 0;
S.r4 = (t, seg) => {
  T_ = t;
  const tc = wt(seg, 'close'), ta = wt(seg, 'after'), ts = wt(seg, 'see');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 470, () => {
    const shut = ease((t - tc) / 0.5), fear = t >= ts ? 1 : 0.55;
    ctx.save(); if (shut >= 1) ctx.translate(Math.sin(t * 41) * 2.2 * fear, Math.cos(t * 33) * 1.6 * fear);
    bigEye(560, 470, 1.3, shut >= 1 ? 1 : shut, false, 0, shut >= 1 ? fear : 0); ctx.restore();
    const rows = [['1', 'CLOSE EYES'], ['2', 'DOOR OPENS']];
    rows.forEach(([n, l], i) => pop(t, tc + 0.3 + i * 0.25, 1300, 380 + i * 110, () => { rrS(1100, 340 + i * 110, 60, 60, 8, C.fig, 4); text(n, 1130, 384 + i * 110, '900 36px M', C.fig);
      text(l, 1190, 386 + i * 110, '900 46px M', C.fig, 'left'); }));
    if (t >= ta) pop(t, ta, 1300, 640, () => { tag('NOT THE OTHER WAY', 1100, 650, C.red, 36); });
  });
};
S.r5 = (t, seg) => {
  const tsd = wt(seg, 'side'), tb = wt(seg, 'breathe');
  {
    cam(t, seg.start, seg.end - seg.start + 0.7, 1.9, 2.15, HEAD.x + 120, HEAD.y + 20, () => {
      bedroomDecor(t, {}); ln(0, FY, W, FY, 4, C.dim); bed(150, FY, 1.05, 'sleep', { cat: 'empty', t });
      // slow breathing: the blanket rises and falls
      if (t >= tb) { const k = (Math.sin((t - tb) * 1.4) + 1) / 2; ctx.save(); ctx.globalAlpha *= 0.5; ctx.beginPath(); ctx.ellipse(HEAD.x + 150, HEAD.y + 26 - k * 6, 90, 10, 0, Math.PI, 2 * Math.PI); ctx.strokeStyle = C.fig; ctx.lineWidth = 3; ctx.stroke(); ctx.restore(); }
    });
    [['ON YOUR SIDE', tsd], ['SLOW BREATHS', tb]].forEach(([l, t0], i) => { if (t >= t0) slideIn(t, t0, 40, 0, () => {
      rrS(1260, 300 + i * 100, 50, 50, 8, C.fig, 4); check(1285, 325 + i * 100, 18, prog(t, t0 + 0.2, 0.3)); text(l, 1340, 342 + i * 100, '900 44px M', C.fig, 'left'); }); });
  }
};
S.r6 = (t, seg) => {
  const tw = wt(seg, 'walk'), tst = wt(seg, 'stand'), tl = wt(seg, 'lean');
  const k = ease((t - tw) / Math.max(0.6, tst - tw));
  const x = lerp(CAT_X, OVER.x, k), bob = Math.abs(Math.sin((t - tw) * 7)) * 8 * (k > 0 && k < 1 ? 1 : 0);
  const sway = OVER.sway * ease((t - tl) / 0.9);
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.05, 1.25, lerp(1000, 520, k), 560, () => {
    bedside(t, { cat: () => standCat(x, FY - bob, CAT_S, { k: 1, arm: 'down', red: 0, sway, tilt: lerp(-4, -14, ease((t - tl) / 0.9)), t }) });
  });
};
S.r7 = (t, seg) => {
  const tb = wt(seg, 'breath'), ts = wt(seg, 'smells');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.9, 2.15, HEAD.x + 80, HEAD.y - 70, () => {
    bedside(t, { cat: () => overCat(t), front: () => {
      if (t >= tb) for (let i = 0; i < 3; i++) { const p = ((t - tb) * 0.8 + i / 3) % 1; ctx.save(); ctx.globalAlpha *= 0.6 * (1 - p);
        pthS(`M${HEAD.x + 70 - p * 50},${HEAD.y - 70 + p * 40} q8,6 0,12 q-8,6 0,12`, C.fig, 3); ctx.restore(); } } });
  });
  if (t >= ts) pop(t, ts, 1450, 250, () => tag('SMELLS LIKE YOUR CAT', 1450, 260, C.fig, 36, 'center'));
};
S.r8 = (t, seg) => {
  const tc = wt(seg, 'checking'), tm = wt(seg, 'move'), tsw = wt(seg, 'swallow');
  cam(t, seg.start, seg.end - seg.start + 0.6, 2.2, 2.5, HEAD.x + 70, HEAD.y - 80, () => {
    bedside(t, { cat: () => overCat(t, { red: prog(t, tc, 0.4), tilt: -14 + Math.sin(t * 1.3) * 4 }) });
  });
  // heartbeat trace along the bottom
  ctx.save(); ctx.beginPath(); for (let x = 200; x <= 1720; x += 6) { const ph = ((x - 200) / 260 - t * 1.6) % 1, u = ph < 0 ? ph + 1 : ph;
    const y = 880 - (u > 0.45 && u < 0.5 ? -60 : u > 0.5 && u < 0.55 ? 80 : 0); x === 200 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
  ctx.strokeStyle = C.red; ctx.lineWidth = 4; redGlow(10); ctx.stroke(); noGlow(); ctx.restore();
  if (t >= tm) pop(t, tm, 1450, 230, () => tag('DO NOT MOVE', 1450, 240, C.red, 40, 'center'));
  if (t >= tsw) pop(t, tsw, 1450, 330, () => tag('DO NOT SWALLOW', 1450, 340, C.red, 40, 'center'));
};
S.r9 = (t, seg) => {
  // it straightens up, tips forward onto four legs while its shapes shrink, lands on the blanket as your small cat, and curls up
  const td = wt(seg, 'drop'), tc = wt(seg, 'curl'), ta = wt(seg, 'always');
  const up = ease((t - seg.start) / 0.9);                           // straighten up from the lean
  const e = clamp((t - td + 0.05) / 0.55), es = ease(e);
  const BED = { x: 150 + 452 * 1.05, y: FY - 226 * 1.05 };           // the foot of the bed, on the blanket
  const ax = lerp(OVER.x, BED.x, es), ay = lerp(FY, BED.y, es) - Math.sin(Math.PI * es) * 70;
  const big = () => { if (e >= 1) return; ctx.save(); ctx.globalAlpha *= 1 - clamp((e - 0.55) / 0.35);
    standCat(ax, ay, lerp(CAT_S, 0.42, es), { k: 1, arm: 'down', red: 0, sway: e > 0 ? lerp(0, -78, es) : lerp(OVER.sway, 0, up), tilt: lerp(-14, 0, Math.max(up, es)), t }); ctx.restore(); };
  const small = () => { if (e < 0.45 || t >= tc + 0.35) return; ctx.save(); ctx.globalAlpha *= clamp((e - 0.45) / 0.35) * (t >= tc ? 1 - clamp((t - tc) / 0.35) : 1);
    walkCat(ax, ay, 0.66, 0); ctx.restore(); };
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.3, 1.2, 600, 600, () => {
    bedside(t, { bedCat: 'empty', cat: () => { if (e < 0.5) big(); }, front: () => {
      if (e >= 0.5) big(); small();
      if (t >= tc) { ctx.save(); ctx.globalAlpha *= clamp((t - tc) / 0.35); ctx.translate(150, FY); ctx.scale(1.05, 1.05); ctx.translate(470, -226); curledCat(0, 0, 0.62); ctx.restore(); } } });
    // the shapes shedding off as it shrinks
    if (e > 0 && e < 1) { ctx.save(); for (let i = 0; i < 8; i++) { const a = hash(i * 5.3) * Math.PI * 2, r = 30 + es * 160 * hash(i * 2.1);
      ctx.globalAlpha = 0.6 * (1 - e); rr(ax + Math.cos(a) * r - 6, ay - 120 * (1 - es) + Math.sin(a) * r - 6, 12, 12, 2, '#ffffff'); } ctx.restore(); }
  });
  if (t >= ta) pop(t, ta, 1450, 260, () => tag('LIKE ALWAYS', 1450, 270, C.fig, 40, 'center'));
};
S.s28 = (t, seg) => {
  const tf = wt(seg, 'four'), tp = wt(seg, 'purring');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.2, 1.35, 700, 620, () => {
    room(t, { person: 'sleep', sun: true, bedCat: 'sleep' });
    if (t >= tp) for (let i = 0; i < 3; i++) { const k = ((t - tp) * 1.5 + i / 3) % 1; ctx.save(); ctx.globalAlpha *= 1 - k; pthS(`M${640 + i * 30},${600 - k * 50} q6,-8 0,-16 q-6,-8 0,-16`, C.fig, 4); ctx.restore(); }
  });
  if (t >= tf) pop(t, tf, 1450, 300, () => { tag('4 LEGS', 1450, 310, C.fig, 40, 'center'); });
  if (t >= tp) pop(t, tp, 1450, 420, () => { tag('PURRING', 1450, 430, C.fig, 40, 'center'); });
};
S.s29 = (t, seg) => {
  const tm = wt(seg, 'middle');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, 960, 520, () => {
    pop(t, seg.start, 1500, 230, () => icon('sun', 1500, 230, 1.0));
    doorFront(DF.x, DF.y, DF.w, DF.h, { marks: prog(t, tm + 0.4, 0.8) });
    const k = ease((t - tm) / 0.7), lx = lerp(1300, DMID.x, k), ly = lerp(760, DMID.y, k);
    pop(t, seg.start + 0.3, lx, ly, () => { glow(); circS(lx, ly, 95, C.fig, 10); ln(lx + 68, ly + 68, lx + 155, ly + 155, 18, C.fig); noGlow(); });
  });
};
S.s30 = (t, seg) => {
  const tl = wt(seg, 'like'), tf = wt(seg, 'far');
  cam(t, seg.start, seg.end - seg.start + 1.0, 1, 1.08, 960, 500, () => {
    rr(460, 140, 1000, 760, 6, '#141414');
    const xs = [700, 960, 1220];
    xs.forEach((x, i) => { const p = prog(t, seg.start + 0.15 + i * 0.22, 0.4); ctx.save(); redGlow(10);
      for (let j = 0; j < 3; j++) lnP(x - 18 + j * 18, 300, x - 12 + j * 18, 640, 7, '#b81f1f', easeOut(p)); ctx.restore(); });
    if (t >= tl) pop(t, tl, 960, 470, () => { ctx.save(); ctx.globalAlpha *= 0.85; icon('paw', 960, 470, 0.9); ctx.restore(); });
    if (t >= tf) { const p = prog(t, tf, 0.4); ln(700, 700, lerp(700, 1220, p), 700, 5, C.fig); ln(700, 680, 700, 720, 5, C.fig); if (p >= 1) ln(1220, 680, 1220, 720, 5, C.fig);
      fadeIn(t, tf + 0.3, () => text('TOO FAR APART', 960, 780, '900 46px M', C.red)); }
  });
};
S.s31 = (t, seg) => emergencyCard(t, seg);
S.s32 = (t, seg) => {
  // too late: your eyes are open, and it is looking right at you
  const ts = wt(seg, 'saw'), to = wt(seg, 'over');
  const CXs = 700;
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.5, 1.9, 520, 520, () => {
    ctx.save(); if (t >= ts && t < ts + 0.6) shake(4, t);
    bedroomDecor(t, {}); ln(0, FY, W, FY, 4, C.dim);
    standCat(CXs, FY, CAT_S, { k: 1, arm: 'down', red: t >= ts ? 1 : 0.2, tilt: 6, t });
    bed(150, FY, 1.05, 'woke', { look: 1, cat: 'empty', t });
    const ex = 150 + 184 * 1.05, ey = FY - 304 * 1.05, cx = CXs - 40 * CAT_S, cy = FY - 360 * CAT_S;
    ctx.setLineDash([12, 10]); lnP(ex + 14, ey, cx - 14, cy, 4, t >= ts ? C.red : C.fig, prog(t, seg.start + 0.6, 0.8)); ctx.setLineDash([]);
    ctx.restore();
  });
  if (t >= ts) pop(t, ts, 1480, 220, () => tag('EYE CONTACT', 1480, 230, C.red, 50, 'center'));
  if (t >= to) pop(t, to, 1480, 360, () => { redGlow(14); spaced('RULES 1-3: OVER', 1480, 370, '900 52px M', C.red, 6); noGlow(); });
};
// list of things that don't work: a header and a running tally
const NOPE = [['THROW THINGS', 's34'], ['RUN', 's35'], ['GIVE AN ARM', 's36'], ['CATNIP', 's37']];
function nopeList(t, upto, x0 = 1280) {
  spaced('DOES NOT WORK', x0, 200, '900 34px M', C.red, 6, 'left');
  NOPE.forEach(([lbl, id], i) => { if (i > upto) return; const y = 300 + i * 80; const done = i < upto;
    ctx.save(); ctx.globalAlpha *= done ? 0.55 : 1; text(lbl, x0 + 60, y + 12, '900 38px M', done ? C.mid : C.fig, 'left'); rrS(x0, y - 22, 40, 40, 6, C.red, 4); redX(x0 + 20, y - 2, 13, done ? 1 : 0.0); ctx.restore(); });
}
S.s33 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 500, () => {
    pop(t, seg.start, 960, 450, () => { hazard(560, 260, 800, 30, t * 40); rrS(560, 300, 800, 330, 10, C.fig, 5);
      spaced('WHAT DOES NOT WORK', 960, 482, '900 50px M', C.fig, 5); hazard(560, 640, 800, 30, -t * 40); });
  });
};
S.s34 = (t, seg) => {
  const td = wt(seg, 'dodge');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.04, 700, 540, () => {
    ln(0, FY, 1200, FY, 4, C.dim);
    // objects fly from the left; the cat leans out of the way each time
    const items = ['pillow', 'book', 'lamp'];
    let lean = 0;
    items.forEach((it, i) => { const t0 = seg.start + 0.2 + i * (seg.end - seg.start - 0.6) / 3, k = (t - t0) / 0.8; if (k < 0) return;
      const x = lerp(80, 1300, clamp(k)), y = FY - 360 + Math.sin(clamp(k) * Math.PI) * -60 + i * 30;
      if (k < 1.2) { ctx.save(); ctx.translate(x, y); ctx.rotate(k * 6); glow(); if (it === 'pillow') ell(0, 0, 50, 26, 0, C.sec); if (it === 'book') rr(-30, -40, 60, 80, 4, C.sec); if (it === 'lamp') { pth('M-30,-10 L30,-10 L18,-50 L-18,-50 Z', C.sec); rr(-4, -10, 8, 40, 2, C.sec); } noGlow(); ctx.restore(); }
      const d = Math.abs(k - 0.62); if (d < 0.25) lean = Math.max(lean, 1 - d / 0.25) * (i % 2 ? -1 : 1); });
    standCat(820, FY, CAT_S, { k: 1, arm: 'down', sway: lean * 14, red: t >= td ? 0.6 : 0, t });
    if (t >= td) pop(t, td, 300, 260, () => { spaced('HITS', 300, 220, '900 32px M', C.mid, 6); text('0', 300, 340, '900 120px M', C.red); });
    nopeList(t, 0);
  });
};
S.s35 = (t, seg) => {
  const tn = wt(seg, 'nearly'), tl = wt(seg, 'longer');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.04, 700, 540, () => {
    // speedometer
    pop(t, seg.start + 0.2, 560, 560, () => {
      ctx.beginPath(); ctx.arc(560, 600, 220, Math.PI, 2 * Math.PI); ctx.strokeStyle = C.dim; ctx.lineWidth = 16; ctx.stroke();
      const v = t < tn ? 0.2 : t < tl ? lerp(0.2, 0.62, easeOut((t - tn) / 0.8)) : lerp(0.62, 1.08, easeOut((t - tl) / 0.8));
      ctx.beginPath(); ctx.arc(560, 600, 220, Math.PI, Math.PI + Math.PI * Math.min(v, 1)); ctx.strokeStyle = v > 0.9 ? C.red : C.fig; ctx.lineWidth = 16; ctx.stroke();
      const a = Math.PI + Math.PI * Math.min(v, 1.04) + (v > 1 ? Math.sin(t * 40) * 0.03 : 0);
      ln(560, 600, 560 + Math.cos(a) * 190, 600 + Math.sin(a) * 190, 8, C.fig); circ(560, 600, 14, C.fig);
      text(t < tl ? (t < tn ? '—' : '50 KM/H') : '??? KM/H', 560, 700, '600 56px Plex', t < tl ? C.fig : C.red);
    });
    if (t >= tl) pop(t, tl, 960, 760, () => { tag('LONGER LEGS', 960, 770, C.red, 36, 'center'); });
    nopeList(t, 1);
  });
};
S.s36 = (t, seg) => {
  const tt = wt(seg, 'take'), tb = wt(seg, 'blood');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.04, 700, 540, () => {
    // an arm offered forward; claw slashes; a blood meter drains
    pop(t, seg.start + 0.2, 560, 520, () => { glow(); rr(260, 480, 520, 70, 35, C.fig); circ(800, 515, 46, C.fig); noGlow(); });
    if (t >= tt) { ctx.save(); redGlow(12); for (let i = 0; i < 3; i++) lnP(440 + i * 70, 450, 480 + i * 70, 580, 9, C.red, prog(t, tt + i * 0.1, 0.15)); ctx.restore(); }
    const lvl = t < tb ? 1 : 1 - easeOut((t - tb) / 1.6) * 0.92;
    pop(t, seg.start + 0.3, 980, 520, () => { rrS(940, 340, 80, 360, 12, C.fig, 5); rr(948, 348 + 344 * (1 - lvl), 64, 344 * lvl, 8, C.red); spaced('BLOOD', 980, 750, '900 30px M', C.mid, 5); });
    nopeList(t, 2);
  });
};
S.s37 = (t, seg) => {
  const td = wt(seg, 'distract'), tb = wt(seg, 'taste');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.04, 700, 540, () => {
    pop(t, seg.start, 520, FY, () => person(520, FY, 1.3, C.fig));
    // catnip leaves all over
    const n = Math.floor(clamp((t - seg.start - 0.3) / 1.2) * 12);
    for (let i = 0; i < n; i++) { const x = 470 + ((i * 37) % 100), y = FY - 420 + ((i * 53) % 330); ctx.save(); ctx.translate(x, y); ctx.rotate(i); ell(0, 0, 14, 7, 0, '#9a9a9a'); ln(-14, 0, 14, 0, 2, '#555'); ctx.restore(); }
    if (t >= td) { ctx.save(); ctx.translate(960, FY); ctx.scale(0.75, 0.75); standCat(0, 0, 1, { k: 1, arm: 'down', red: 0.3, t }); ctx.restore(); }
    if (t >= tb) pop(t, tb, 760, 260, () => { tag('TASTE +100%', 760, 270, C.red, 40, 'center'); });
    nopeList(t, 3);
  });
};
S.s39 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, W / 2, 470, () => {
    pop(t, seg.start, 960, 470, () => { glow(); rrS(860, 370, 200, 200, 18, C.fig, 8); noGlow(); });
    check(960, 470, 64, prog(t, seg.end - 0.5, 0.4));
    fadeIn(t, seg.start + 0.3, () => spaced('ONLY ONE', 960, 680, '900 44px M', C.fig, 10));
  });
};
// you, sitting up on the bed like a sitting dog: haunches on the mattress, arms straight down in front, head up. (x,y) = rear on the mattress
// you, sitting up on the bed like a sitting dog: rear down, knees up, arms straight down in front like front legs, head up. (x,y) = rear on the blanket
// you, sitting up on the bed like a sitting dog: haunches down, chest up, arms straight down in front like front legs, head up. (x,y) = rear on the blanket
function dogSit(x, y, s, bark = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.25)', 14);
  const hb = -bark * 10;
  ln(60, -182, 86, -10, 20, C.sec); ell(92, -6, 16, 7, 0, C.sec);    // far arm, a front leg
  ell(0, -36, 48, 38, 0, C.fig); ell(40, -9, 46, 11, 0, C.fig);     // haunch, and the folded leg along the blanket
  ln(10, -54, 44, -196, 58, C.fig);                                 // chest, upright
  ln(44, -184, 66, -10, 21, C.fig); ell(72, -6, 16, 7, 0, C.fig);   // near arm straight down, hand flat like a paw
  circ(60, -256 + hb, 32, C.fig);                                   // head up, toward the cat
  noGlow(); circ(76, -262 + hb, 5.5, '#000');
  ctx.restore();
}
S.s40 = (t, seg) => {
  const tsit = wt(seg, 'sit'), td = wt(seg, 'dog'), te = wt(seg, 'eyes'), tb = wt(seg, 'bark'), tl = wt(seg, 'loud');
  const k = ease((t - tsit) / 0.6);
  const MT = FY - 214 * 1.05;                                 // top of the blanket
  const barkK = t >= tb ? Math.max(0, Math.sin((t - tb) * 14)) : 0;
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.1, 1.2, 700, 560, () => {
    bedroomDecor(t, { noWindow: true }); ln(0, FY, W, FY, 4, C.dim);
    // the window sits where your head comes up, so it moves to the left for this shot
    ctx.save(); ctx.translate(-300, 0); rrS(330, 230, 220, 230, 6, C.mid, 6); ln(440, 236, 440, 454, 4, C.mid); ln(336, 345, 544, 345, 4, C.mid); glow('rgba(255,255,255,0.5)', 24); circ(500, 285, 22, C.fig); noGlow(); circ(510, 278, 20, '#000'); ctx.restore();
    ctx.save(); ctx.globalAlpha *= 1 - k; bed(150, FY, 1.05, 'woke', { look: 1, cat: 'empty', t }); ctx.restore();
    ctx.save(); ctx.globalAlpha *= k; bed(150, FY, 1.05, 'flat', { cat: 'empty', t }); dogSit(330, MT + 6, 1.15, barkK); ctx.restore();
    standCat(1000, FY, CAT_S, { k: 1, arm: 'down', red: t < tb ? 1 : 0.4, t, sway: t >= tl ? 4 * ease((t - tl) / 0.4) : 0 });
    if (t >= te) { ctx.setLineDash([12, 12]); lnP(330 + 80 * 1.15, MT + 6 - 262 * 1.15, 1000 - 40 * CAT_S - 14, FY - 360 * CAT_S, 4, C.fig, prog(t, te, 0.4)); ctx.setLineDash([]); }
    if (t >= td && t < te) pop(t, td, 1400, 260, () => tag('LIKE A DOG', 1400, 270, C.fig, 40, 'center'));
    if (t >= tb) { const big = t >= tl ? 1.25 : 1; ctx.save(); ctx.translate(700, 230); ctx.scale(big, big); ctx.translate(-700, -230); bubble(700, 230, 320, 130, 'WOOF!', t, tb, C.fig, '#000', 1); ctx.restore(); }
  });
};
S.s41 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 1, 1, 1.1, W / 2, 500, () => {
    for (let i = 0; i < 9; i++) { const t0 = seg.start + i * 0.18; if (t < t0) continue;
      pop(t, t0, 300 + (i % 3) * 660, 260 + Math.floor(i / 3) * 230, () => text('WOOF', 300 + (i % 3) * 660, 290 + Math.floor(i / 3) * 230, `900 ${70 + (i % 2) * 30}px M`, C.fig), 0.25); }
  });
};
S.s42 = (t, seg) => {
  const tf = wt(seg, 'flatten'), ts = wt(seg, 'step'), td = wt(seg, 'drop'), tw = wt(seg, 'walk');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.1, 1.0, 1100, 560, () => {
    ln(0, FY, W, FY, 4, C.dim); doorEdge(700, FY, 1);
    const back = ease((t - ts) / 0.8) * 120;
    if (t < td + 0.2) standCat(1100 + back, FY, CAT_S, { k: 1, arm: 'down', ears: ease((t - tf) / 0.4), red: lerp(0.8, 0, prog(t, tf, 1)), t });
    if (t >= td) { const k = (t - td); const x = 1220 + Math.max(0, k - 0.4) * 120; ctx.save(); ctx.globalAlpha *= prog(t, td, 0.25); walkCat(x, FY, 1.4, k * 8); ctx.restore(); }
    if (t >= tw) pop(t, tw, 760, 300, () => tag('AS IF NOTHING HAPPENED', 760, 310, C.fig, 34, 'center'));
  });
};
S.s43 = (t, seg) => {
  const tn = wt(seg, 'neighbors'), tl = wt(seg, 'let');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 560, () => {
    // sunrise behind an apartment block; windows light up with complaints
    const sun = ease((t - seg.start) / (seg.end - seg.start));
    ctx.save(); glow('rgba(255,255,255,0.6)', 40); circ(1500, lerp(860, 300, sun), 70, C.fig); ctx.restore();
    rr(560, 260, 700, 600, 6, '#141414'); rrS(560, 260, 700, 600, 6, C.mid, 4);
    for (let r = 0; r < 5; r++) for (let c = 0; c < 6; c++) { const i = r * 6 + c, x = 610 + c * 105, y = 300 + r * 105;
      const on = t >= tn && hash(i) < clamp((t - tn) / 1.6); rr(x, y, 70, 70, 4, on ? C.fig : '#262626');
      if (on && hash(i + 9) < 0.3) text('!', x + 35, y + 56, '900 50px M', '#000'); }
    rr(560, 860, 700, 4, 0, C.dim);
    if (t >= tl) pop(t, tl, 960, 180, () => tag('LET THEM', 960, 190, C.fig, 46, 'center'));
  });
};
S.s44 = (t, seg) => {
  const tf = wt(seg, 'feed'), tp = wt(seg, 'pet');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.2, 1.35, 700, 620, () => {
    room(t, { person: 'woke', sun: true, bedCat: 'sit' });
    if (t >= tf) pop(t, tf, 880, FY - 20, () => { rr(840, FY - 30, 90, 30, 10, C.sec); ell(885, FY - 30, 45, 8, 0, '#777'); });
    if (t >= tf) pop(t, tf, 1400, 330, () => tag('FEED IT', 1400, 340, C.fig, 40, 'center'));
    if (t >= tp) pop(t, tp, 1400, 440, () => tag('PET IT', 1400, 450, C.fig, 40, 'center'));
    if (t >= tp) for (let i = 0; i < 3; i++) { const k = ((t - tp) * 1.5 + i / 3) % 1; ctx.save(); ctx.globalAlpha *= 1 - k; pthS(`M${700 + i * 26},${590 - k * 50} q6,-8 0,-16 q-6,-8 0,-16`, C.fig, 4); ctx.restore(); }
  });
};
S.s45 = (t, seg) => {
  const tk = wt(seg, 'knocking');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 500, () => {
    pop(t, seg.start, 600, 470, () => { person(600, 760, 1.0, C.fig); bubble(600, 300, 260, 110, 'WOOF', t, seg.start, C.fig, '#000', 1); });
    redX(600, 300, 70, prog(t, seg.start + 0.6, 0.35));
    if (t >= tk - 0.4) pop(t, tk - 0.4, 1320, 470, () => { sitCat(1260, 760, 2.0, {}); bubble(1320, 300, 300, 110, 'KNOCK', t, tk - 0.4, C.fig, '#000', -1); });
    redX(1320, 300, 70, prog(t, tk + 0.2, 0.35));
    // the cat gives you one look
    if (t >= tk + 0.6 && t < tk + 1.1) eyeGlow(1260 + 53 * 2, 760 - 93 * 2, 11, 11, 1, 0.8);
  });
};
S.s46 = (t, seg) => {
  const kk = evs('knock3').slice(-1)[0];
  if (kk && t >= kk.t - 0.4) {
    const p = knockPulse(t), lk = lastKnock(t);
    ctx.save(); if (p > 0.5) shake(6 * p, t);
    doorFront(DF.x, DF.y, DF.w, DF.h, {});
    if (lk >= kk.t) ripple(DMID.x, DMID.y, lk, t, C.red, 30, 300, 8);
    knockLines(DF.x - 40, DMID.y, p, C.red, 1); knockLines(DF.x + DF.w + 40, DMID.y, p, C.red, -1);
    ctx.restore();
    return;
  }
  cam(t, seg.start, 4, 1, 1.05, W / 2, 500, () => {
    pop(t, seg.start, 960, 470, () => {
      rrS(560, 300, 800, 330, 12, C.mid, 5);
      spaced(NAME + ' 404', 960, 420, '900 64px M', C.fig, 8);
      text('RULE 1 ✓   RULE 2 ✓   RULE 3 ✓', 960, 510, '600 32px Plex', C.sec);
      redGlow(8); text('RULE 4  EMERGENCY PROTOCOL  ✓', 960, 570, '600 32px Plex', C.red); noGlow();
    });
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
  seg.words.forEach(w => { cur.push(w); if (/[.?!]$/.test(w.w) || (cur.length >= 4 && /,$/.test(w.w)) || cur.length >= 10) { out.push(cur); cur = []; } });
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
  (S[seg.id] || S.s01)(t, seg);
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

// Protocol 404, EP05 "If Your AI Job Interview Ever Asks Who Else Is In The Room". Canvas renderer: window.draw(t).
// Black background, flat white pictograms, red only for what is wrong. Needs window.TL (timeline.json).
(() => {
const W = 1920, H = 1080;
const NAME = 'PROTOCOL';   // the channel's name, as it appears on screen ("NAME NUM")
const NUM = '404';
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
  const rows = [['SUBJECT', null], ['LOCATION', 'ROOM 4B, FLOOR 9'], ['TIME', 'MONDAY, 9:00 AM']];
  rows.forEach(([l, v], i) => { const y = P.y + 270 + i * 82;
    text(l, P.x + 60, y, '600 28px Plex', '#666', 'left'); ln(P.x + 250, y + 12, P.x + P.w - 60, y + 12, 2, '#bbb');
    if (v === null) rr(P.x + 260, y - 30, 330, 40, 3, '#111');
    else { ctx.save(); ctx.filter = 'blur(9px)'; text(v, P.x + 262, y, '900 36px M', i === 2 ? '#d61f1f' : '#111', 'left'); ctx.restore(); } });   // classified: blurred
  // barcode and a hazard edge
  for (let i = 0; i < 40; i++) { const bw = hash(i * 1.7) < 0.35 ? 6 : 3; rr(P.x + P.w - 300 + i * 6.4, P.y + P.h - 170, bw, 70, 0, '#111'); }
  text('NO. 0' + NUM, P.x + P.w - 172, P.y + P.h - 74, '600 24px Plex', '#444');
  text('DO NOT TELL THE TRUTH', P.x + 60, P.y + P.h - 130, '600 22px Plex', '#666', 'left');
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
  if (name === 'self') { circ(-14, -18, 17, col); rr(-36, 4, 44, 44, 12, col); rrS(14, -50, 44, 32, 8, col, 5); pth('M22,-20 L18,-6 L32,-19 Z', col); }
  if (name === 'truth') { rrS(-44, -40, 88, 64, 14, col, 6); pth('M-24,22 L-34,46 L-4,24 Z', col); ln(-16, -22, 16, 6, 7, col === '#fff' ? '#fff' : '#d61f1f'); ln(16, -22, -16, 6, 7, col === '#fff' ? '#fff' : '#d61f1f'); }
  if (name === 'ask') { rrS(-44, -44, 88, 68, 14, col, 6); pth('M-24,22 L-34,46 L-4,24 Z', col); text('?', 0, 6, '900 52px M', col); }
  if (name === 'warn') { const tri = () => { ctx.beginPath(); ctx.moveTo(0, -50); ctx.lineTo(50, 40); ctx.lineTo(-50, 40); ctx.closePath(); };
    ctx.lineJoin = 'round'; tri(); ctx.fillStyle = C.red; ctx.fill(); if (col === '#fff') { ctx.lineWidth = 6; ctx.strokeStyle = '#fff'; ctx.stroke(); }
    rr(-6, -22, 12, 38, 5, '#fff'); circ(0, 28, 7, '#fff'); }
  if (name === 'hand') { ctx.lineJoin = 'round'; pth('M-50,-6 L-10,-24 L22,-24 L50,-6 L50,18 L16,28 L-20,28 L-50,18 Z', col); ln(-62, 6, -50, 6, 14, col); ln(50, 6, 62, 6, 14, col);
    ln(-6, -24, 10, -6, 4, col === '#fff' ? '#000' : '#ececec'); ln(8, -24, 24, -6, 4, col === '#fff' ? '#000' : '#ececec'); }
  if (name === 'fist') { rr(-34, -34, 68, 64, 18, col); for (let i = 1; i < 4; i++) ln(-34 + i * 17, -34, -34 + i * 17, -10, 3, '#ff2b2b'); }
  ctx.restore();
}
const RULES = [['hand', 'DO NOT SHAKE TOO HARD', '', ['DO NOT SHAKE', 'TOO HARD']], ['truth', 'DO NOT TELL THE TRUTH', '', ['DO NOT TELL', 'THE TRUTH']], ['ask', 'NEVER SAY YOU HAVE NO QUESTIONS', '', ['NEVER SAY YOU', 'HAVE NO QUESTIONS']], ['warn', 'EMERGENCY PROTOCOL', 'HOW TO FIGHT BACK']];
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
}// ---------- EP07 props: the interview room ----------
// Flat 2D pictograms on black. The interviewers are bright white mannequins in suits with crisp black detail lines; faceless,
// the middle one has red eyes. Red only for danger.
const SUIT = { jacket: '#dcdce0', shirt: '#ffffff', trousers: '#b9b9bf', shoe: '#1c1c1f', line: '#0b0b0d', head: '#f4f4f6', headSh: '#c9c9cf', board: '#9a9aa0', paper: '#fbfbfb' };
const ellS = (x, y, rx, ry, rot, s, w = 6) => { ctx.beginPath(); ctx.ellipse(x, y, rx, ry, rot, 0, Math.PI * 2); ctx.strokeStyle = s; ctx.lineWidth = w; ctx.stroke(); };

// a clipboard, centred at (x,y), 130 x 176 at s=1. o.lines: text lines on the paper [str, red?]; o.under: index of the line underlined in red, o.up 0..1
function clipboard(x, y, s = 1, rot = 0, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  rr(-80, -88, 160, 180, 8, SUIT.board); rrS(-80, -88, 160, 180, 8, SUIT.line, 3);
  rr(-70, -70, 140, 154, 2, SUIT.paper);
  rr(-26, -96, 52, 22, 6, '#2a2a2e'); rrS(-26, -96, 52, 22, 6, '#6a6a70', 2); circ(0, -86, 4, '#9a9aa0');
  if (o.lines) {
    o.lines.forEach(([str, red], i) => text(str, -60, -30 + i * 28, '900 15px M', red ? '#d61f1f' : '#222', 'left'));
    if (o.under != null && o.up > 0) { ctx.font = '900 15px M'; const w = ctx.measureText(o.lines[o.under][0]).width; lnP(-62, -24 + o.under * 28, -58 + w, -25 + o.under * 28, 3.5, '#d61f1f', o.up); }
  } else for (let i = 0; i < 6; i++) ln(-56, -44 + i * 20, i % 3 === 2 ? 10 : 54, -44 + i * 20, 4, '#c4c4c8');
  ctx.restore();
}
// a pen: tip at (x,y)
function pen(x, y, s = 1, rot = -0.6) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  pth('M0,0 L8,-10 L8,-120 L-8,-120 L-8,-10 Z', '#1d1d20'); rr(-8, -126, 16, 10, 3, '#bdbdc2'); rr(6, -112, 5, 40, 2, '#bdbdc2'); ln(0, 0, 0, -6, 3, '#d61f1f');
  ctx.restore();
}
// the interviewer: a faceless white mannequin in a suit. Front view, feet at (x,y), ~620 tall at s=1.
// o.eyes 0..1 red eyes; o.arms: 'desk' (hands on the desk at waist), 'board' (clipboard at the chest), 'write' (board + pen, o.wt animates),
// 'down'; o.lean 0..1 (leans in, head drops forward); o.fold 0..1 (flattens into a sheet of paper); o.shake (px); o.dim 0..1
function suit(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (o.shake) ctx.translate(Math.sin((o.t || 0) * 83) * o.shake, Math.cos((o.t || 0) * 71) * o.shake * 0.5);
  const fold = o.fold || 0;
  if (fold > 0) { ctx.translate(0, -300); ctx.scale(1, 1 - 0.96 * ease(fold)); ctx.translate(0, 300); }
  if (o.dim) ctx.globalAlpha *= 1 - 0.6 * o.dim;
  const L = SUIT.line, lean = o.lean || 0;
  glow('rgba(255,255,255,0.28)', 18);
  // legs + shoes
  for (const d of [-1, 1]) {
    pth(`M${d * 6},-292 L${d * 66},-292 L${d * 56},-24 L${d * 14},-24 Z`, SUIT.trousers);
    rr(d > 0 ? 10 : -62, -26, 52, 26, 10, SUIT.shoe);
  }
  noGlow();
  for (const d of [-1, 1]) { pthS(`M${d * 6},-292 L${d * 66},-292 L${d * 56},-24 L${d * 14},-24 Z`, L, 3); ln(d * 36, -280, d * 35, -40, 2, 'rgba(0,0,0,0.25)'); }
  ctx.save(); ctx.translate(0, -300); ctx.rotate(0); ctx.translate(0, lean * 14);
  // jacket body: shoulders at -200 (relative to the hips at 0), hem at +34
  glow('rgba(255,255,255,0.28)', 18);
  pth('M-96,-188 C-104,-190 -110,-176 -108,-150 L-92,34 L92,34 L108,-150 C110,-176 104,-190 96,-188 C60,-206 -60,-206 -96,-188 Z', SUIT.jacket);
  noGlow();
  pthS('M-96,-188 C-104,-190 -110,-176 -108,-150 L-92,34 L92,34 L108,-150 C110,-176 104,-190 96,-188 C60,-206 -60,-206 -96,-188 Z', L, 3.5);
  // shirt V + collar + tie
  pth('M-30,-198 L30,-198 L0,-96 Z', SUIT.shirt); pthS('M-30,-198 L30,-198 L0,-96 Z', L, 2.5);
  pth('M-30,-198 L-6,-198 L-12,-176 Z', '#e9e9ec'); pth('M30,-198 L6,-198 L12,-176 Z', '#e9e9ec'); pthS('M-30,-198 L-12,-176 L-4,-196 M30,-198 L12,-176 L4,-196', L, 2.5);
  pth('M-8,-192 L8,-192 L6,-176 L-6,-176 Z', o.tieRed ? C.red : '#111'); pth('M-6,-176 L6,-176 L13,-112 L0,-98 L-13,-112 Z', o.tieRed ? C.red : '#111');
  // lapels (notched), buttons, breast pocket
  pthS('M-30,-198 L-56,-150 L-44,-140 L-60,-128 L-2,-58 M30,-198 L56,-150 L44,-140 L60,-128 L2,-58', L, 4);
  ln(0, -58, 0, 34, 3, L); circ(-6, -36, 4.5, L); circ(-6, -6, 4.5, L);
  ln(52, -100, 86, -104, 3.5, L); pth('M60,-102 L66,-116 L72,-102 Z', SUIT.shirt);
  ln(-86, -20, -40, -18, 3, L); ln(40, -18, 86, -20, 3, L);
  // arms
  const arm = (d, pts) => { ctx.save(); glow('rgba(255,255,255,0.2)', 10); poly(pts, 36, SUIT.jacket); noGlow(); ctx.restore(); poly(pts, 2, 'rgba(0,0,0,0)'); };
  const A = o.arms || 'desk';
  const hand = (hx, hy) => { ctx.save(); glow('rgba(255,255,255,0.2)', 8); ell(hx, hy, 18, 15, 0, SUIT.head); noGlow(); ellS(hx, hy, 18, 15, 0, L, 2.5); ctx.restore(); };
  const sleeve = (pts) => { ctx.save(); ctx.lineJoin = 'round'; ctx.lineCap = 'round'; poly(pts, 40, L); poly(pts, 33, SUIT.jacket); ctx.restore(); };
  if (A === 'down') { for (const d of [-1, 1]) { sleeve([[d * 98, -170], [d * 112, -60], [d * 108, 20]]); hand(d * 108, 40); } }
  else if (A === 'desk') { for (const d of [-1, 1]) { sleeve([[d * 98, -170], [d * 118, -60], [d * 70, 4]]); hand(d * 56, 10); } }
  else {   // board / write: the clipboard held in front of the chest
    sleeve([[-98, -170], [-118, -80], [-62, -70]]); hand(-56, -70);
    const wt = o.wt || 0, px = 24 + Math.sin(wt * 9) * 22 + ((wt * 40) % 40), py = -110 + Math.floor((wt * 1.2) % 3) * 22;
    clipboard(-6, -104, 1.0, -0.06, { lines: o.lines, under: o.under, up: o.up });
    if (A === 'write') { sleeve([[98, -170], [124, -80], [px + 20, py + 26]]); pen(px, py, 0.8, -0.5); hand(px + 18, py + 22); }
    else { sleeve([[98, -170], [118, -80], [62, -70]]); hand(56, -70); }
  }
  // neck + head (faceless mannequin, lit from the upper left)
  ctx.save(); ctx.translate(0, lean * 26); ctx.translate(0, -232); ctx.rotate(-lean * 0.08 + (o.tilt || 0)); ctx.translate(0, 232);
  rr(-17, -232, 34, 40, 8, SUIT.headSh); ln(-17, -200, 17, -200, 2, L);
  glow('rgba(255,255,255,0.35)', 22); ell(0, -276, 42, 54, 0, SUIT.head); noGlow();
  ctx.save(); ctx.beginPath(); ctx.ellipse(0, -276, 42, 54, 0, 0, Math.PI * 2); ctx.clip();
  ctx.filter = 'blur(10px)'; ell(30, -262, 24, 60, 0, SUIT.headSh); ell(-6, -232, 40, 14, 0, 'rgba(180,180,188,0.6)'); ctx.filter = 'none'; ctx.restore();
  ellS(0, -276, 42, 54, 0, L, 3);
  ell(-43, -272, 7, 13, 0, SUIT.headSh); ell(43, -272, 7, 13, 0, SUIT.headSh);
  const re = o.eyes || 0;
  if (re > 0) { ctx.save(); ctx.globalAlpha *= re; redGlow(26); ell(-15, -282, 9, 5, 0.12, C.red); ell(15, -282, 9, 5, -0.12, C.red); noGlow(); ctx.restore(); }
  ctx.restore();
  ctx.restore();
  ctx.restore();
}
// the long interview desk seen from the candidate's chair: top at y, from x0 to x1. o.items: draw glasses, nameplates
function desk(x0, x1, y, o = {}) {
  glow('rgba(255,255,255,0.25)', 18); rr(x0, y, x1 - x0, 20, 4, '#f0f0f2'); noGlow();
  rr(x0 + 24, y + 20, x1 - x0 - 48, 300, 0, '#111113'); rrS(x0 + 24, y + 20, x1 - x0 - 48, 300, 0, '#4a4a50', 3);
  ln(x0 + 24, y + 70, x1 - 24, y + 70, 2, '#2a2a2e');
  if (o.items !== false) {
    const n = o.n || 3;
    for (let i = 0; i < n; i++) {
      const cx = lerp(x0, x1, (i + 0.5) / n);
      // a blank nameplate and a glass of water
      pth(`M${cx - 70},${y} L${cx - 62},${y - 34} L${cx + 62},${y - 34} L${cx + 70},${y} Z`, '#2a2a2e'); ln(cx - 40, y - 17, cx + 40, y - 17, 3, '#55555c');
      ctx.save(); ctx.globalAlpha *= 0.9; rrS(cx + 110, y - 60, 30, 60, 4, '#cfcfd4', 3); rr(cx + 113, y - 34, 24, 31, 2, 'rgba(200,220,255,0.18)'); ctx.restore();
    }
  }
}
// the room behind them: a clean black wall with a clock, an air vent and a window strip. o.clock: [h, m, s] hands; o.ac 0..1 vanes open
function roomWall(o = {}) {
  ctx.fillStyle = '#060607'; ctx.fillRect(-200, -200, W + 400, H + 400);
  ln(-200, o.floor ?? 700, W + 200, o.floor ?? 700, 3, '#1f1f22');
  // clock
  const [cx, cy] = o.clockAt || [1640, 260];
  ctx.save(); glow('rgba(255,255,255,0.3)', 16); circ(cx, cy, 62, '#f2f2f2'); noGlow(); circS(cx, cy, 62, '#000', 3);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; ln(cx + Math.sin(a) * 50, cy - Math.cos(a) * 50, cx + Math.sin(a) * 56, cy - Math.cos(a) * 56, i % 3 ? 2 : 4, '#000'); }
  const [h, m, s] = o.clock || [9, 0, 0], ah = (h % 12 + m / 60) / 12 * Math.PI * 2, am = m / 60 * Math.PI * 2, as = s / 60 * Math.PI * 2;
  ln(cx, cy, cx + Math.sin(ah) * 30, cy - Math.cos(ah) * 30, 6, '#000'); ln(cx, cy, cx + Math.sin(am) * 44, cy - Math.cos(am) * 44, 4, '#000');
  ln(cx, cy, cx + Math.sin(as) * 50, cy - Math.cos(as) * 50, 2, o.secRed ? C.red : '#000'); circ(cx, cy, 5, '#000'); ctx.restore();
  // air conditioner high on the left wall
  const [ax, ay] = o.acAt || [70, 240];
  rr(ax, ay, 300, 90, 12, '#e6e6ea'); rrS(ax, ay, 300, 90, 12, '#000', 3); rr(ax + 18, ay + 56, 264, 22, 6, '#2a2a2e');
  const op = o.ac ?? 1; for (let i = 0; i < 3; i++) ln(ax + 26 + i * 86, ay + 66, ax + 26 + i * 86 + 70, ay + 66 + 8 * op, 4, '#9a9aa0');
  circ(ax + 270, ay + 22, 5, op > 0.5 ? '#7ad67a' : '#3a3a3e');
}
// the candidate's chair from behind with you in it (back of your head and shoulders above the backrest). Floor at y.
function meBack(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  glow('rgba(255,255,255,0.3)', 18); circ(0, -470, 56, C.fig); rr(-92, -420, 184, 200, 50, C.fig); noGlow();
  ell(-58, -476, 9, 16, 0, '#d6d6da'); ell(58, -476, 9, 16, 0, '#d6d6da');
  // the backrest + the seat edge + the gas lift + base
  rr(-120, -380, 240, 250, 34, '#2c2c31'); rrS(-120, -380, 240, 250, 34, '#8a8a92', 3); for (let i = 0; i < 4; i++) ln(-90, -330 + i * 50, 90, -330 + i * 50, 2, '#3c3c42');
  rr(-14, -130, 28, 70, 4, '#8a8a92'); ln(-140, -40, 140, -40, 14, '#55555c'); for (const d of [-1, 0, 1]) circ(d * 140, -22, 14, '#2c2c31');
  ctx.restore();
}
// you (or another candidate) seated in profile on a plain chair, facing o.dir (1 right). Floor at y, ~420 tall.
// o.hair: long hair; o.eye; o.hands: 'lap' | 'fold'; o.lockLegs: the trousers run down into the chair (c5)
function sitSide(x, y, s = 1, o = {}) {
  const dir = o.dir || 1, col = o.col || C.fig;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * dir, s);
  // chair: seat, back, legs
  rr(-60, -200, 130, 16, 5, '#55555c'); rr(-66, -380, 16, 196, 6, '#55555c'); ln(-50, -184, -56, 0, 8, '#55555c'); ln(60, -184, 66, 0, 8, '#55555c');
  glow('rgba(255,255,255,0.25)', 14);
  rr(-40, -376, 64, 170, 26, col);                       // torso
  ln(-10, -210, 96, -206, 34, col); ln(96, -206, 104, -18, 30, col); rr(90, -20, 52, 20, 8, col);   // thigh, shin, shoe
  circ(-4, -420, 40, col); noGlow();
  if (o.hair) { pth('M-46,-430 C-48,-478 40,-480 40,-436 C24,-452 -8,-456 -30,-438 C-34,-410 -40,-380 -52,-360 C-62,-390 -56,-416 -46,-430 Z', '#bdbdc2'); }
  ctx.save(); glow('rgba(255,255,255,0.2)', 8); poly([[0, -350], [30, -270], [80, -224]], 22, col); noGlow(); ctx.restore();
  if (o.eye !== false) circ(20, -424, 5.5, '#000');
  ctx.restore();
}
// a lone office chair, front view (the interviewer's): floor at y. o.legs: trouser legs fused into the column (0..1)
function officeChair(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  glow('rgba(255,255,255,0.18)', 14);
  rr(-110, -560, 220, 280, 40, '#2c2c31'); rrS(-110, -560, 220, 280, 40, '#9a9aa2', 3);
  rr(-130, -270, 260, 50, 18, '#2c2c31'); rrS(-130, -270, 260, 50, 18, '#9a9aa2', 3);
  noGlow(); rr(-14, -220, 28, 150, 4, '#9a9aa2');
  ln(-160, -70, 160, -70, 14, '#6a6a72'); ln(-90, -70, -120, -30, 12, '#6a6a72'); ln(90, -70, 120, -30, 12, '#6a6a72');
  for (const d of [-160, -120, 120, 160]) circ(d, -20, 16, '#1c1c1f');
  ctx.restore();
}
// the interviewer in profile in his office chair, facing o.dir. Floor at y. o.fused 0..1: his shins narrow and become the chair's column
function suitSide(x, y, s = 1, o = {}) {
  const dir = o.dir || 1, f = o.fused || 0, L = SUIT.line;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * dir, s);
  // chair back + seat
  rr(-120, -560, 36, 260, 14, '#2c2c31'); rrS(-120, -560, 36, 260, 14, '#9a9aa2', 3); ln(-96, -300, -60, -260, 12, '#6a6a72');
  rr(-110, -272, 220, 40, 14, '#2c2c31'); rrS(-110, -272, 220, 40, 14, '#9a9aa2', 3);
  // the base: five spokes and wheels
  ln(-160, -40, 160, -40, 14, '#6a6a72'); for (const d of [-150, -50, 60, 150]) circ(d, -16, 16, '#1c1c1f');
  // column: chrome when free; when fused it is the two trouser legs, twisted together into one
  if (f < 1) { ctx.save(); ctx.globalAlpha *= 1 - f; rr(-14, -232, 28, 196, 4, '#9a9aa2'); ctx.restore(); }
  glow('rgba(255,255,255,0.25)', 16);
  // thigh along the seat
  pth('M-70,-312 L120,-312 C140,-312 146,-280 128,-270 L-70,-268 Z', SUIT.trousers);
  if (f < 0.01) {   // normal shins and shoes
    pth('M84,-300 L128,-292 L126,-34 L86,-34 Z', SUIT.trousers); rr(80, -36, 80, 30, 10, SUIT.shoe);
  } else {
    // the shins bend back under the seat and run down the column; no shoes, the fabric spreads into the base
    const k = ease(f), bx = lerp(106, 0, k);
    ctx.beginPath(); ctx.moveTo(84, -290); ctx.bezierCurveTo(lerp(84, 40, k), -230, lerp(90, 18, k), -150, bx - 22, -60); ctx.lineTo(bx - 40, -40); ctx.lineTo(bx + 40, -40); ctx.lineTo(bx + 22, -60);
    ctx.bezierCurveTo(lerp(126, 26, k), -150, lerp(130, 40, k), -230, 128, -282); ctx.closePath(); ctx.fillStyle = SUIT.trousers; ctx.fill(); noGlow(); ctx.strokeStyle = L; ctx.lineWidth = 3; ctx.stroke();
    ctx.save(); ctx.globalAlpha *= k; for (let i = 0; i < 5; i++) pthS(`M${lerp(96, 6, k) - 14 + i * 7},${-230 + i * 34} q14,10 26,0`, 'rgba(0,0,0,0.45)', 2.5); ctx.restore();
    if (k > 0.5) { ctx.save(); ctx.globalAlpha *= (k - 0.5) * 2; redGlow(26); ln(bx - 42, -40, bx + 42, -40, 6, C.red); noGlow(); ctx.restore(); }
  }
  noGlow(); pthS('M-70,-312 L120,-312 C140,-312 146,-280 128,-270 L-70,-268 Z', L, 3);
  // torso, arm, head
  glow('rgba(255,255,255,0.25)', 16);
  pth('M-74,-540 C-50,-560 30,-560 46,-530 L60,-300 L-78,-300 Z', SUIT.jacket); noGlow();
  pthS('M-74,-540 C-50,-560 30,-560 46,-530 L60,-300 L-78,-300 Z', L, 3); pthS('M30,-536 L44,-470 L20,-380', L, 3);
  ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round'; poly([[-10, -520], [10, -390], [110, -360]], 40, L); poly([[-10, -520], [10, -390], [110, -360]], 33, SUIT.jacket); ctx.restore();
  ell(126, -360, 18, 14, 0, SUIT.head);
  rr(-24, -590, 34, 44, 8, SUIT.headSh);
  glow('rgba(255,255,255,0.35)', 20); ell(-6, -636, 44, 54, 0, SUIT.head); noGlow(); ellS(-6, -636, 44, 54, 0, L, 3); ell(-12, -632, 7, 13, 0, SUIT.headSh);
  if (o.eyes) { ctx.save(); redGlow(22); ell(30, -642, 8, 4.5, 0, C.red); noGlow(); ctx.restore(); }
  ctx.restore();
}
// a flat white person; feet at (x,y), 360 tall at s=1. o.face: 'front' | 'back' | 'left' | 'right'; o.arms: [l, r] raise 0..1; o.walk phase
function me(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); const col = o.col || C.fig;
  glow('rgba(255,255,255,0.25)', 14);
  const sw = o.walk != null ? Math.sin(o.walk) : 0;
  ln(-14, -170, -16 - sw * 16, -6, 26, col); ln(14, -170, 16 + sw * 16, -6, 26, col);
  rr(-34, -300, 68, 150, 24, col);
  const [al, ar] = o.arms || [0, 0];
  ln(-30, -280, lerp(-44 + sw * 14, -70, al), lerp(-170, -330, al), 20, col);
  ln(30, -280, lerp(44 - sw * 14, 70, ar), lerp(-170, -330, ar), 20, col);
  circ(0, -340, 36, col); noGlow();
  if (o.hair) pth('M-38,-344 C-42,-392 40,-394 38,-346 C30,-366 -10,-372 -30,-352 C-30,-330 -34,-300 -46,-286 C-52,-310 -48,-330 -38,-344 Z', '#bdbdc2');
  const f = o.face || 'front';
  if (f === 'front') { circ(-12, -344, 5.5, '#000'); circ(12, -344, 5.5, '#000'); }
  if (f === 'left') circ(-18, -344, 5.5, '#000');
  if (f === 'right') circ(18, -344, 5.5, '#000');
  ctx.restore();
}
// speech bubble from a speaker at (tx,ty); white with black text, or o.red for a dangerous line
function say(t, t0, x, y, str, tx, ty, size = 54, o = {}) {
  if (t < t0) return;
  ctx.font = `900 ${size}px M`; const lines = str.split('\n'), w = Math.max(...lines.map(l => ctx.measureText(l).width)) + 80, h = lines.length * size * 1.18 + 52;
  pop(t, t0, x, y, () => {
    const col = o.red ? C.red : C.fig; o.red ? redGlow(24) : glow('rgba(255,255,255,0.35)', 24);
    rr(x - w / 2, y - h / 2, w, h, 26, col);
    const bx = clamp(tx, x - w / 2 + 50, x + w / 2 - 50), by = ty > y ? y + h / 2 - 4 : y - h / 2 + 4;
    pth(`M${bx - 24},${by} L${tx},${ty} L${bx + 24},${by} Z`, col); noGlow();
    lines.forEach((l, i) => text(l, x, y + (i - (lines.length - 1) / 2) * size * 1.18 + size * 0.36, `900 ${size}px M`, o.red ? '#fff' : '#000'));
  }, 0.3);
}
// the night bedroom from the side: bed on the left, the door on the right
function bedroomNight(o = {}) {
  ctx.fillStyle = '#040405'; ctx.fillRect(-200, -200, W + 400, H + 400);
  ln(-200, 900, W + 200, 900, 3, '#1c1c20');
  // window with blinds, faint moonlight
  rr(330, 230, 260, 300, 4, '#0d0f14'); for (let i = 0; i < 9; i++) ln(334, 250 + i * 32, 586, 250 + i * 32, 6, '#1d2028'); rrS(330, 230, 260, 300, 4, '#2a2a30', 4);
  // the door
  if (o.door !== false) { rr(1640, 380, 200, 520, 4, '#0e0e10'); rrS(1640, 380, 200, 520, 4, '#3a3a40', 4); circ(1660, 650, 8, '#55555c'); ln(1620, 900, 1860, 900, 4, '#2a2a30');
    if (o.gapGlow) { ctx.save(); ctx.globalAlpha *= o.gapGlow; glow('rgba(255,255,255,0.8)', 14); rr(1640, 892, 200, 6, 2, '#f2f2f2'); ctx.restore(); } }
  // bedside clock: 3:00 in red
  rr(160, 760, 150, 140, 6, '#141416'); rrS(160, 760, 150, 140, 6, '#2c2c30', 3);
  rr(176, 700, 118, 54, 8, '#0a0a0b'); rrS(176, 700, 118, 54, 8, '#3a3a40', 3); ctx.save(); redGlow(14); text(o.time || '3:00', 235, 742, '900 38px M', C.red); ctx.restore();
}
// email screen on a laptop or phone: o.from, o.subj, o.body (typed by t)
function mailCard(x, y, w, h, o = {}) {
  glow('rgba(255,255,255,0.3)', 26); rr(x, y, w, h, 22, '#f4f4f6'); noGlow();
  rr(x, y, w, 70, 22, '#1d1d20'); rr(x, y + 40, w, 30, 0, '#1d1d20'); text('INBOX', x + 40, y + 47, '900 28px M', '#f4f4f6', 'left');
  circ(x + w - 50, y + 35, 10, o.dot ? C.red : '#55555c');
  text('FROM', x + 40, y + 130, '600 22px Plex', '#777', 'left'); text(o.from || '', x + 140, y + 130, '900 30px M', o.fromRed ? '#d61f1f' : '#111', 'left');
  ln(x + 40, y + 160, x + w - 40, y + 160, 2, '#d0d0d4');
  if (o.subj) text(o.subj, x + 40, y + 214, '900 36px M', '#111', 'left');
  (o.body || []).forEach((l, i) => text(l, x + 40, y + 280 + i * 50, '600 32px I', '#222', 'left'));
}
// list icons drawn white on black
function icon7(name, x, y, s = 1, col = C.fig) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 14);
  if (name === 'self') { circ(-40, -30, 34, col); rr(-80, 10, 80, 80, 24, col); rr(10, -90, 90, 64, 16, col); pth('M24,-30 L14,0 L44,-28 Z', col); }
  if (name === 'money') { rr(-90, -50, 180, 100, 12, col); noGlow(); circS(0, 0, 30, '#000', 7); text('$', 0, 16, '900 44px M', '#000'); }
  if (name === 'game') { rr(-90, -40, 180, 90, 44, col); noGlow(); rr(-62, -6, 40, 12, 4, '#000'); rr(-48, -20, 12, 40, 4, '#000'); circ(44, -10, 9, '#000'); circ(64, 10, 9, '#000'); }
  if (name === 'family') { circ(-50, -46, 22, col); rr(-74, -20, 48, 80, 16, col); circ(50, -46, 22, col); rr(26, -20, 48, 80, 16, col); circ(0, -6, 16, col); rr(-18, 12, 36, 52, 12, col); }
  if (name === 'pin') { pth('M0,80 C-30,30 -64,0 -64,-30 C-64,-66 -34,-90 0,-90 C34,-90 64,-66 64,-30 C64,0 30,30 0,80 Z', col); noGlow(); pth('M-28,-22 L0,-48 L28,-22 L28,6 L-28,6 Z', '#000'); }
  if (name === 'clock') { circS(0, 0, 70, col, 12); ln(0, 0, 0, -44, 10, col); ln(0, 0, 32, 14, 10, col); }
  if (name === 'stage') { rr(-90, 50, 180, 24, 6, col); ln(0, 50, 0, -20, 10, col); ell(0, -40, 22, 30, 0, col); for (let i = 0; i < 2; i++) { ctx.beginPath(); ctx.arc(0, -40, 50 + i * 22, -0.6, 0.6); ctx.strokeStyle = col; ctx.lineWidth = 7; ctx.stroke(); } }
  if (name === 'sweat') { circ(-10, 0, 60, col); noGlow(); circ(-28, -8, 7, '#000'); circ(8, -8, 7, '#000'); pth('M66,-56 C80,-30 90,-14 76,-2 C64,8 50,-6 56,-22 C60,-34 64,-44 66,-56 Z', col); }
  if (name === 'sleep') { rr(-90, 30, 180, 30, 10, col); circ(-60, 10, 22, col); rr(-34, 0, 120, 30, 12, col); text('Z', 30, -30, '900 50px M', col); text('z', 70, -64, '900 34px M', col); }
  if (name === 'offer') { rr(-70, -40, 140, 100, 12, col); noGlow(); rrS(-26, -62, 52, 26, 8, col, 9); ln(-70, 0, 70, 0, 5, '#000'); }
  if (name === 'mail') { rr(-90, -56, 180, 112, 10, col); noGlow(); poly([[-86, -50], [0, 10], [86, -50]], 8, '#000'); }
  if (name === 'ask') { rr(-80, -60, 160, 100, 22, col); pth('M-40,36 L-56,76 L-6,38 Z', col); noGlow(); text('?', 0, 20, '900 80px M', '#000'); }
  noGlow(); ctx.restore();
}
// a dark card behind a list of items over a busy scene
function listCard(x, y, w, h) { ctx.save(); ctx.globalAlpha *= 0.94; rr(x, y, w, h, 18, '#050505'); ctx.restore(); rrS(x, y, w, h, 18, '#2a2a2d', 3); }
// a row with an icon box, text, and a red X that draws on at tx
function noRow(t, t0, tx, x, y, ic, label, size = 46) {
  slideIn(t, t0, 50, 0, () => {
    rr(x, y - 60, 120, 120, 16, '#121214'); rrS(x, y - 60, 120, 120, 16, '#3a3a3e', 3); icon7(ic, x + 60, y, 0.5);
    text(label, x + 160, y + size * 0.36, `900 ${size}px M`, C.fig, 'left');
    if (tx != null) redX(x + 60, y, 50, prog(t, tx, 0.3));
  }, 0.35);
}
// a row with a white check (allowed answers)
function okRow(t, t0, x, y, label, size = 58) {
  slideIn(t, t0, 50, 0, () => {
    glow('rgba(255,255,255,0.3)', 20); rr(x, y - 60, 120, 120, 16, C.fig); noGlow(); check(x + 60, y, 34, prog(t, t0 + 0.15, 0.3), '#000');
    text(label, x + 160, y + size * 0.36, `900 ${size}px M`, C.fig, 'left');
  }, 0.35);
}
// a big résumé page, centred at (x,y), 520 x 700 at s=1
function resume(x, y, s = 1, rot = 0, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  glow('rgba(255,255,255,0.3)', 24); rr(-260, -350, 520, 700, 6, SUIT.paper); noGlow();
  circ(-170, -250, 54, '#d0d0d4'); circ(-170, -266, 20, '#9a9aa0'); pth('M-206,-214 C-200,-240 -140,-240 -134,-214 Z', '#9a9aa0');
  rr(-90, -290, 300, 30, 4, '#111'); rr(-90, -246, 200, 16, 4, '#9a9aa0');
  for (let k = 0; k < 3; k++) { rr(-210, -150 + k * 150, 160, 18, 4, '#111'); for (let i = 0; i < 3; i++) rr(-210, -118 + k * 150 + i * 28, i === 2 ? 260 : 400, 12, 3, '#c4c4c8'); }
  // their marks: circles and underlines in red pen
  const m = o.marks || 0;
  if (m > 0) { ctx.save(); ctx.globalAlpha *= clamp(m); ctx.strokeStyle = '#d61f1f'; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.ellipse(-150, -110, 80, 26, -0.05, 0, Math.PI * 2 * clamp(m)); ctx.stroke();
    lnP(-214, 50, 190, 48, 4, '#d61f1f', clamp(m * 1.5 - 0.3)); lnP(-214, 196, 60, 194, 4, '#d61f1f', clamp(m * 1.5 - 0.6));
    ctx.restore(); }
  ctx.restore();
}
// ---------- EP07 v5: the three interviewers as Matrix-style agents ----------
// Channel identity: analog horror. PURE BLACK background, PURE WHITE flat characters with thin black detail lines. Red only for danger.
// Three near-identical bald agents: black sunglasses, an earpiece with a coiled wire, a narrow black tie. No nose, no mouth.
// The heads are flat white (no outline) so the ears melt into the silhouette. Tiny differences only:
//   'young' (left, the handshake one): narrow rectangular lenses
//   'hr'    (middle, asks the question; lenses glow red): wider lenses
//   'boss'  (right, behind the laptop): rounder lenses, slightly broader head
const PP = { fig: '#f4f4f4', line: '#000', eye: '#000' };
const PK = { young: { R: 60, neck: 22, nw: 40 }, hr: { R: 60, neck: 22, nw: 40 }, boss: { R: 62, neck: 18, nw: 46 } };
const ppHeadY = k => -222 - PK[k].neck - 50;
const AGENT_HEAD = 'M-50,-34 C-52,-78 -26,-94 0,-94 C26,-94 52,-78 50,-34 L49,14 C47,40 30,60 0,62 C-30,60 -47,40 -49,14 Z';

// a head, face centre at (0,0), the neck hanging below. o.eyes 0..1: the lenses glow red; o.look -1..1 turns the glint
function ppHead(kind, o = {}) {
  const K = PK[kind], F = PP.fig, L = PP.line, w = kind === 'boss' ? 1.06 : 1;
  ctx.save(); ctx.scale(w, 1);
  rr(-K.nw / 2 / w, 40, K.nw / w, K.neck + 30, 6, F);
  glow('rgba(255,255,255,0.35)', 24); ell(-50, -6, 10, 18, 0, F); ell(50, -6, 10, 18, 0, F); pth(AGENT_HEAD, F); noGlow();
  // the earpiece and its coiled wire running down into the collar
  circ(-52, -2, 5, L); pthS('M-52,4 C-56,16 -48,24 -54,34 C-60,44 -50,52 -54,62 C-58,74 -48,84 -52,96', L, 2.5);
  // sunglasses
  const re = o.eyes || 0, lens = kind === 'young' ? [34, 18, 4] : kind === 'hr' ? [38, 22, 5] : [36, 22, 11];
  const [lw, lh, lr] = [lens[0] + 4, lens[1] + 3, lens[2]], ly = -14;
  ln(-50, ly - 2, 50, ly - 2, 4, L);
  for (const d of [-1, 1]) {
    const cx = d * 24;
    ctx.save(); if (re > 0) redGlow(30 * re); rr(cx - lw / 2, ly - lh / 2, lw, lh, lr, re > 0 ? `rgb(${Math.round(255 * re)},${Math.round(43 * re)},${Math.round(43 * re)})` : L); noGlow(); ctx.restore();
    if (re < 0.3) { ctx.save(); ctx.globalAlpha *= 0.6; ln(cx - lw * 0.3 + (o.look || 0) * 6, ly - lh * 0.25, cx - lw * 0.1 + (o.look || 0) * 6, ly - lh * 0.25, 2.5, '#fff'); ctx.restore(); }
  }
  ctx.restore();
}

// an interviewer, waist at (x,y) (the desk top). Flat white suit, black lines.
// o.arms: 'desk' (long fingers flat on the desk), 'board' (clipboard), 'write' (+ pen, o.wt), 'laptop' (o.lid 1 open -> 0 shut), 'hand' (reaching to shake, o.reach), 'down'
// o.eyes, o.look, o.lean 0..1, o.tilt, o.sink, o.shake, o.fold 0..1, o.dim 0..1, o.stand (draw legs; (x,y) = feet), o.tieRed
function agent(kind, x, y, s = 1, o = {}) {
  const F = PP.fig, L = PP.line, lean = o.lean || 0;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (o.stand) {
    glow('rgba(255,255,255,0.28)', 18);
    pth('M-104,-300 L104,-300 L88,-22 L12,-22 L3,-190 L-3,-190 L-12,-22 L-88,-22 Z', F);
    noGlow(); pthS('M3,-190 L12,-22 M-3,-190 L-12,-22', L, 2.5);
    for (const d of [-1, 1]) { const sp = `M${d * 10},-24 L${d * 92},-24 C${d * 106},-24 ${d * 108},0 ${d * 94},0 L${d * 10},0 Z`; pth(sp, '#0b0b0c'); pthS(sp, F, 2.5); }
    ctx.translate(0, -300);
  }
  if (o.shake) ctx.translate(Math.sin((o.t || 0) * 83) * o.shake, Math.cos((o.t || 0) * 71) * o.shake * 0.5);
  const fold = o.fold || 0;
  if (fold > 0) { ctx.translate(0, -240); ctx.scale(1, 1 - 0.96 * ease(fold)); ctx.translate(0, 240); }
  if (o.dim) ctx.globalAlpha *= 1 - 0.6 * o.dim;
  if (o.sink) ctx.translate(0, o.sink);
  ctx.translate(0, lean * 18);
  // jacket: natural shoulders, a slight taper at the waist
  const J = 'M-114,-208 C-130,-202 -136,-182 -134,-150 C-130,-100 -120,-50 -116,10 L116,10 C120,-50 130,-100 134,-150 C136,-182 130,-202 114,-208 C78,-224 -78,-224 -114,-208 Z';
  glow('rgba(255,255,255,0.28)', 20); pth(J, F); noGlow();
  // shirt collar around the neck, the open V, a narrow black tie
  pthS('M-26,-230 L-30,-220 L-12,-196 L0,-214 L12,-196 L30,-220 L26,-230', L, 2.5);
  pthS('M-30,-220 L0,-112 L30,-220', L, 2.5);
  pth('M-7,-212 L7,-212 L5,-196 L-5,-196 Z', L);
  pth('M-5,-196 L5,-196 L10,-128 L0,-116 L-10,-128 Z', o.tieRed ? C.red : L);
  // notched lapels, the closure, two buttons, a breast pocket
  pthS('M-30,-220 L-54,-170 L-42,-162 L-56,-148 L-4,-66 M30,-220 L54,-170 L42,-162 L56,-148 L4,-66', L, 3);
  ln(0, -66, 0, 10, 2.5, L); circ(-6, -42, 4, L); circ(-6, -12, 4, L);
  ln(-96, -118, -62, -120, 2.5, L); ln(68, -40, 100, -42, 2.5, L); ln(-100, -40, -68, -42, 2.5, L);
  // arms: tapered sleeves with a shirt cuff, simple mitten hands (no fingers)
  const limb = (pts, w0, w1) => {   // a sleeve: black outline strokes first, then white, so the joints stay seamless
    ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for (const [col, add] of [[L, 5], [F, 0]]) for (let i = 0; i < pts.length - 1; i++) {
      ctx.beginPath(); ctx.moveTo(...pts[i]); ctx.lineTo(...pts[i + 1]); ctx.lineWidth = lerp(w0, w1, i / Math.max(1, pts.length - 2)) + add; ctx.strokeStyle = col; ctx.stroke(); }
    ctx.restore();
    const [p, q] = pts.slice(-2), ang = Math.atan2(q[1] - p[1], q[0] - p[0]);
    ctx.save(); ctx.translate(q[0], q[1]); ctx.rotate(ang); ln(-10, -w1 / 2 + 3, -10, w1 / 2 - 3, 2.5, L); ctx.restore();
  };
  const hand = (hx, hy, rot = 0, sx = 1) => {
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(rot); ctx.scale(sx, 1);
    const h = 'M-6,-13 C8,-16 26,-12 32,-2 C35,6 30,14 18,15 C6,16 -4,12 -6,4 Z';
    pth(h, F); pthS(h, L, 2.5); pthS('M4,-13 C10,-20 18,-20 20,-14', L, 2.5);
    ctx.restore(); };
  const A = o.arms || 'desk', sh = 114, sy = -196;
  if (A === 'desk') { limb([[-sh + 6, sy + 10], [-134, -76], [-58, -20]], 44, 36); limb([[sh - 6, sy + 10], [134, -76], [58, -20]], 44, 36); hand(-44, -20, 0, 1); hand(40, -16, 0.1, -1); }
  else if (A === 'down') { limb([[-sh + 6, sy + 10], [-128, -90], [-124, -6]], 42, 36); limb([[sh - 6, sy + 10], [128, -90], [124, -6]], 42, 36); hand(-122, 12, 1.62, 1); hand(122, 12, 1.52, 1); }
  else if (A === 'hand') { if (o.stand) { limb([[-sh + 6, sy + 10], [-128, -90], [-124, -6]], 42, 36); hand(-122, 12, 1.62, 1); } else { limb([[-sh + 6, sy + 10], [-134, -76], [-58, -20]], 44, 36); hand(-44, -20, 0, 1); }
    const r = o.reach ?? 1; limb([[sh - 6, sy + 10], [140, -96], [110 + 40 * r, -40 - 10 * r]], 42, 36); hand(124 + 40 * r, -38 - 10 * r, 0.35, 1); }
  else if (A === 'laptop') { limb([[-sh + 6, sy + 10], [-134, -76], [-76, -20]], 44, 36); limb([[sh - 6, sy + 10], [134, -76], [76, -20]], 44, 36); }
  else {
    limb([[-sh, sy], [-138, -100], [-84, -84]], 44, 34);
    const wt = o.wt || 0, px = 24 + Math.sin(wt * 9) * 22 + ((wt * 40) % 40), py = -130 + Math.floor((wt * 1.2) % 3) * 22;
    clipboard(-6, -120, 1.05, -0.06, { lines: o.lines, under: o.under, up: o.up });
    hand(-70, -84, 0, 1);
    if (A === 'write') { limb([[sh, sy], [140, -100], [px + 34, py + 34]], 44, 34); pen(px, py, 0.8, -0.5); hand(px + 22, py + 26, 0.3, -1); }
    else { limb([[sh, sy], [138, -100], [84, -84]], 44, 34); hand(70, -84, 0, -1); }
  }
  // head
  ctx.save(); ctx.translate(0, ppHeadY(kind) + lean * 34); ctx.rotate(-lean * 0.06 + (o.tilt || 0)); ctx.scale(1.25, 1.25); ppHead(kind, o); ctx.restore();
  // the laptop: a white lid seen from behind, in front of everything
  if (A === 'laptop') {
    const lid = o.lid ?? 1, hh = 320 * lid;
    rr(-150, -12, 300, 14, 4, F); ln(-150, 2, 150, 2, 2, L);
    if (hh > 4) { glow('rgba(255,255,255,0.25)', 16); rr(-140, -12 - hh, 280, hh, 10, F); noGlow(); rrS(-140, -12 - hh, 280, hh, 10, L, 3); circ(0, -12 - hh / 2, 12 * lid, '#000'); }
    if (lid < 0.98) { hand(-64, -16, 0, 1); hand(64, -16, 0, -1); }
  }
  ctx.restore();
}

// the room: nothing but black. A white wall clock and a thin floor line.
function meetRoom(o = {}) {
  ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400);
  if (o.floor !== false) ln(-200, o.floor ?? 760, W + 200, o.floor ?? 760, 2, '#262626');
  if (o.clockAt === false) return;
  const [cx, cy] = o.clockAt || [300, 280];
  ctx.save(); glow('rgba(255,255,255,0.3)', 16); circ(cx, cy, 58, PP.fig); noGlow();
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; ln(cx + Math.sin(a) * 46, cy - Math.cos(a) * 46, cx + Math.sin(a) * 52, cy - Math.cos(a) * 52, i % 3 ? 2 : 4, '#000'); }
  const [h, m, s] = o.clock || [9, 0, 0], ah = (h % 12 + m / 60) / 12 * Math.PI * 2, am = m / 60 * Math.PI * 2, as = s / 60 * Math.PI * 2;
  ln(cx, cy, cx + Math.sin(ah) * 28, cy - Math.cos(ah) * 28, 6, '#000'); ln(cx, cy, cx + Math.sin(am) * 40, cy - Math.cos(am) * 40, 4, '#000');
  ln(cx, cy, cx + Math.sin(as) * 46, cy - Math.cos(as) * 46, 2, o.secRed ? C.red : '#000'); circ(cx, cy, 5, '#000'); ctx.restore();
}
// the long table: a white slab on thin legs; o.items: glasses of water and sheets of paper
function meetDesk(x0, x1, y, o = {}) {
  glow('rgba(255,255,255,0.3)', 18); rr(x0, y, x1 - x0, 22, 4, PP.fig); noGlow();
  for (const lx of [x0 + 40, x1 - 54]) rr(lx, y + 22, 14, 300, 2, '#d8d8d8');
  if (o.items !== false) {
    const n = o.n || 3;
    for (let i = 0; i < n; i++) {
      const cx = lerp(x0, x1, (i + 0.5) / n);
      rrS(cx + 130, y - 58, 30, 58, 4, PP.fig, 3); rr(cx - 160, y - 5, 84, 5, 1, PP.fig);
    }
  }
}
// ---------- EP07 v4 scenes: "If Your Interviewer Ever Asks 'What Is Your Greatest Weakness?'" (Protocol 404) ----------
// Pure black, pure white vector figures, red only for danger. The interviewers are three near-identical bald agents in sunglasses.
const ev = type => window.TL.events.filter(e => e.type === type);
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
const blackAfter = (t, t0) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const zk = (t, t0, d, z0, z1) => lerp(z0, z1, ease((t - t0) / d));
const black = () => { ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); };
const typed = (s, t, t0, cps = 28) => s.slice(0, Math.max(0, Math.floor((t - t0) * cps)));
const segEnd = seg => seg.end + 0.7;
const seg$ = id => window.TL.segments.find(s => s.id === id);
// a close-up: (cx, cy) is brought to the centre of the screen at zoom z
function focus(t, t0, d, z0, z1, cx, cy, fn) { const z = zk(t, t0, d, z0, z1); ctx.save(); ctx.translate(W / 2, H / 2 - 40); ctx.scale(z, z); ctx.translate(-cx, -cy); fn(); ctx.restore(); }
const flatT = fn => { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); fn(); ctx.restore(); };
function brackets(x, y, w, h, a, col = C.fig) {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha *= a; const L = 34;
  for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const cx = x + sx * w / 2, cy = y + sy * h / 2; poly([[cx, cy - sy * L], [cx, cy], [cx - sx * L, cy]], 6, col); }
  ctx.restore();
}
const KINDS = ['young', 'hr', 'boss'];

// ---------- the interview room ----------
const IX = [560, 960, 1360], DESK_Y = 700, CLOCK = [300, 280];
const HEADY = DESK_Y - 294;   // the agents' face centre when seated
// o.arms: one mode or three; o.eyes (middle 0..1); o.lean/o.tilt (middle); o.stand 0..1 (they rise); o.me: your back in the foreground; o.who [bools]; o.reach (left one's hand)
function room(t, o = {}) {
  meetRoom({ clock: o.clock, secRed: o.secRed, clockAt: o.clockAt ?? CLOCK });
  if (o.door) roomDoor(t, o.door);
  for (let i = 0; i < 3; i++) {
    if (o.who && !o.who[i]) continue;
    const st = ease(o.standI ? o.standI[i] : (o.stand || 0));
    const arms = Array.isArray(o.arms) ? o.arms[i] : (o.arms || 'desk');
    agent(KINDS[i], IX[i], st > 0.01 ? DESK_Y + 300 - st * 120 : DESK_Y, 1, { stand: st > 0.01 ? 1 : 0, arms, eyes: i === 1 ? (o.eyes ?? 0) : 0, lean: i === 1 ? o.lean : 0, tilt: i === 1 ? o.tilt : 0,
      shake: o.shake ? o.shake[i] : 0, t, reach: o.reach, lid: o.lid, look: o.look });
  }
  meetDesk(260, 1660, DESK_Y, { n: 3 });
  if (o.me) meBack(o.meX ?? 960, 1400, 1.3);
}
// a door in the right of the room: white outline; o = { lock: 0..1 red padlock, open: 0..1 }
function roomDoor(t, d) {
  rrS(1720, 330, 170, 430, 4, C.fig, 5); circ(1742, 560, 8, C.fig);
  spaced('EXIT', 1805, 310, '900 30px M', '#8a8a8a', 8);
  if (d.lock > 0) { ctx.save(); ctx.globalAlpha *= d.lock; const red = d.open ? 1 - d.open : 1;
    ctx.translate(1805, 560); ctx.beginPath(); ctx.arc(0, -30 - 30 * (d.open || 0), 26, Math.PI, 0); ctx.lineWidth = 10; ctx.strokeStyle = red > 0.5 ? C.red : C.fig; ctx.stroke();
    red > 0.5 ? redGlow(20) : glow(); rr(-40, -30, 80, 66, 10, red > 0.5 ? C.red : C.fig); noGlow(); circ(0, 0, 8, '#000'); ctx.restore(); }
}
// a "does not work" header at the top left with a red X on the icon at tx
function noHead(t, seg, ic, label, tx) {
  flatT(() => slideIn(t, seg.start, -40, 0, () => { const w = 190 + label.length * 31; ctx.save(); ctx.globalAlpha *= 0.88; rr(60, 60, w, 130, 18, '#050505'); ctx.restore(); rrS(60, 60, w, 130, 18, '#2a2a2d', 3);
    icon7(ic, 125, 125, 0.5); text(label, 200, 142, '900 46px M', C.fig, 'left'); redX(125, 125, 48, prog(t, tx, 0.3)); }, 0.35));
}
// a small white note card (what they write down)
function noteCard(t, t0, x, y, str, rot = -0.05, col = '#111') {
  if (t < t0) return;
  pop(t, t0, x, y, () => { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.font = '900 44px M'; const w = ctx.measureText(str).width + 80;
    glow(); rr(-w / 2, -50, w, 100, 10, '#fbfbfb'); noGlow(); text(str, 0, 16, '900 44px M', col); ctx.restore(); }, 0.3);
}

// ---------- the night bedroom (rule 4) ----------
const TRIO = [1130, 1350, 1570];
// you sitting up in bed, facing right
function sitUpInBed(s = 1.3) {
  ctx.save(); ctx.translate(360, 900); ctx.scale(s, s);
  glow('rgba(255,255,255,0.25)', 16); rr(110, -360, 90, 190, 36, C.fig); circ(156, -410, 46, C.fig); noGlow(); circ(186, -416, 9, '#000');
  ctx.save(); glow('rgba(255,255,255,0.2)', 8); poly([[130, -320], [176, -250], [236, -236]], 26, C.fig); noGlow(); ctx.restore();
  ctx.restore();
}
function nightRoom(o = {}) {
  black(); ln(-200, 900, W + 200, 900, 3, '#262626');
  if (o.door !== false) { const op = o.doorOpen || 0;
    if (op > 0) { ctx.save(); ctx.globalAlpha *= 0.5 * op; rr(1700, 380, 180, 520, 2, '#1a1a1a'); ctx.restore(); }
    rrS(1700, 380, 180 * (1 - op * 0.7), 520, 4, C.fig, 5); circ(1720 + 0 * op, 650, 8, C.fig); }
  // the bedside clock: 3:00 in red
  rrS(150, 760, 160, 140, 6, '#5a5a5a', 3); rrS(166, 690, 128, 60, 8, C.fig, 4); ctx.save(); redGlow(14); text(o.time || '3:00', 230, 736, '900 40px M', C.red); ctx.restore();
}
// the three standing at the foot of the bed. o.arms (one or three), o.eyes, o.xs, o.s, o.y, o.shake [3], o.who, o.boxes 0..1, o.badges 0..1, o.drop 0..1
function trio(t, o = {}) {
  const xs = o.xs || TRIO, s = o.s || 0.78, y = o.y ?? 900;
  for (let i = 0; i < 3; i++) { if (o.who && !o.who[i]) continue;
    const arms = Array.isArray(o.arms) ? o.arms[i] : (o.arms || 'board');
    const x = xs[i] + (o.walk ? o.walk[i] : 0);
    agent(KINDS[i], x, y, s, { stand: 1, arms, eyes: i === 1 ? (o.eyes ?? 1) : 0, shake: o.shake ? o.shake[i] : 0, t });
    if (o.badges) { ctx.save(); ctx.globalAlpha *= o.badges; ctx.translate(x, y - 300 * s); ctx.scale(s, s); rr(30, -150, 72, 44, 5, C.fig); rrS(30, -150, 72, 44, 5, '#000', 3); text('STAFF', 66, -121, '900 17px M', '#000'); ctx.restore(); }
    if (o.boxes) cardboardBox(x, y - 300 * s + 20 * s, s * 1.05, o.boxes);
  }
  if (o.drop) for (let i = 0; i < 3; i++) {   // their clipboards on the floor
    const k = ease(o.drop), x = xs[i] - 20, yy = lerp(y - 420 * s, y - 10, k);
    ctx.save(); ctx.translate(x, yy); ctx.rotate(lerp(-0.06, 1.45 + i * 0.1, k)); clipboard(0, 0, 0.8 * s / 0.78); ctx.restore(); }
}
// a cardboard box held at the waist: a stapler and a sad little plant inside
function cardboardBox(x, y, s, a = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.globalAlpha *= a;
  // plant: drooping leaves
  ln(20, -70, 20, -150, 5, '#000'); ln(20, -70, 20, -150, 3, C.fig);
  for (const [dx, dy, r] of [[-26, -128, -0.9], [60, -120, 0.9], [-14, -160, -0.4], [50, -160, 0.6]]) { ctx.save(); ctx.translate(20 + dx * 0.5, dy + 10); ctx.rotate(r); ell(dx * 0.5, 0, 26, 11, 0, C.fig); ctx.beginPath(); ctx.ellipse(dx * 0.5, 0, 26, 11, 0, 0, Math.PI * 2); ctx.strokeStyle = '#000'; ctx.lineWidth = 2.5; ctx.stroke(); ctx.restore(); }
  rr(-4, -96, 48, 34, 4, C.fig); rrS(-4, -96, 48, 34, 4, '#000', 3);   // the pot
  // stapler
  rr(-110, -92, 100, 22, 8, '#111'); rrS(-110, -92, 100, 22, 8, C.fig, 2.5); rr(-110, -72, 100, 10, 3, '#111'); rrS(-110, -72, 100, 10, 3, C.fig, 2.5);
  // the box
  glow('rgba(255,255,255,0.25)', 18); rr(-150, -70, 300, 170, 6, C.fig); noGlow(); rrS(-150, -70, 300, 170, 6, '#000', 3);
  pth('M-150,-70 L-176,-104 L-130,-104 L-110,-70 Z', C.fig); pthS('M-150,-70 L-176,-104 L-130,-104 L-110,-70', '#000', 3);
  pth('M150,-70 L176,-104 L130,-104 L110,-70 Z', C.fig); pthS('M150,-70 L176,-104 L130,-104 L110,-70', '#000', 3);
  rr(-40, -40, 80, 26, 13, '#000');   // the hand hole
  ctx.restore();
}
function night(t, o = {}) {
  nightRoom(o);
  if (o.sitUp) { bed(360, 900, 1.3, 'empty'); sitUpInBed(); } else bed(360, 900, 1.3, o.bed || 'woke', { look: 1 });
  if (o.trio !== false) trio(t, o);
}

// ---------- the handshake close-up ----------
// your arm from the left (plain white), his from the right (sleeve, cuff, outline). o.sq 0..1 his grip; o.shake px; o.crack 0..1; o.apart 0..1; o.long 0..1 (his hand stretches)
function handshake(t, o = {}) {
  const ap = ease(o.apart || 0), sh = o.shake ? Math.sin(t * 60) * o.shake : 0;
  ctx.save(); ctx.translate(-260 * ap, 0);
  glow('rgba(255,255,255,0.3)', 20); poly([[-200, 760], [700, 580]], 120, C.fig); noGlow();
  ctx.save(); ctx.translate(780, 566); ctx.rotate(-0.2); const yh = 'M-70,-52 C30,-74 120,-46 134,-4 C126,40 40,62 -70,52 Z';
  glow('rgba(255,255,255,0.25)', 14); pth(yh, C.fig); noGlow(); pthS(yh, '#000', 4); pthS('M-10,-58 C30,-40 50,-20 56,4', '#000', 4); ctx.restore();
  ctx.restore();
  ctx.save(); ctx.translate(260 * ap + sh, sh * 0.4);
  ctx.save(); ctx.lineCap = 'round'; poly([[2200, 380], [1150, 540]], 132, '#000'); poly([[2200, 380], [1150, 540]], 122, C.fig); ctx.restore();
  ctx.save(); ctx.translate(1150, 540); ctx.rotate(-0.15); ln(40, -58, 40, 58, 4, '#000'); ctx.restore();   // the shirt cuff
  const L = 1 + 0.5 * (o.long || 0), sq = o.sq || 0;
  // his hand wraps over yours: a long mitten
  ctx.save(); ctx.translate(1080, 550); ctx.scale(1 - 0.06 * sq, 1 - 0.1 * sq);
  const hp = `M60,-70 C${-120 * L},-96 ${-260 * L},-60 ${-270 * L},10 C${-268 * L},64 ${-150 * L},80 0,74 C40,72 70,40 70,0 Z`;
  glow('rgba(255,255,255,0.25)', 16); pth(hp, C.fig); noGlow(); pthS(hp, '#000', 5);
  pthS(`M${-60 * L},-62 C${-110 * L},-30 ${-150 * L},10 ${-160 * L},50`, '#000', 4);   // the thumb's edge
  ctx.restore(); ctx.restore();
  if (o.crack > 0) { ctx.save(); ctx.globalAlpha *= o.crack; redGlow(20);
    for (const [a, l] of [[-2.4, 90], [-1.2, 110], [0.4, 80], [2.2, 100], [-0.3, 130]]) { const x0 = 860 + Math.cos(a) * 110, y0 = 560 + Math.sin(a) * 80;
      poly([[x0, y0], [x0 + Math.cos(a) * l * 0.5 + 14, y0 + Math.sin(a) * l * 0.5 - 10], [x0 + Math.cos(a) * l, y0 + Math.sin(a) * l]], 6, C.red); }
    noGlow(); ctx.restore(); }
}
// the grip meter: two bars, YOU and HIM. o.you, o.him 0..1.6 (over 1 = red, past the top)
function gripMeter(t, o) {
  flatT(() => {
    const bars = [['YOU', o.you, 200], ['HIM', o.him, 380]];
    for (const [lab, v, x] of bars) {
      rrS(x - 45, 120, 90, 360, 10, '#5a5a5a', 4);
      const h = 340 * Math.min(v, 1.3), red = v > 1.0;
      ctx.save(); if (red) redGlow(24); rr(x - 35, 470 - h, 70, h, 6, red ? C.red : C.fig); noGlow(); ctx.restore();
      text(lab, x, 540, '900 44px M', red ? C.red : C.fig);
    }
    ln(140, 130, 440, 130, 3, '#8a8a8a'); text('MAX', 290, 105, '600 24px Plex', '#8a8a8a');
  });
}

// ---------- hook ----------
S.h1 = (t, seg) => {
  // frame 0: the three agents, the question already asked; the middle one's lenses are red
  const td = wt(seg, 'do');
  cam(t, 0, seg.end + 0.6, 1.0, 1.12, 960, 470, () => room(t, { me: true, eyes: 1 }));
  if (t < td - 0.1) say(t, -1, 960, 120, 'WHAT IS YOUR GREATEST WEAKNESS?', 960, 250, 50);
  else pop(t, td - 0.1, 960, 140, () => tag('DO NOT TELL THE TRUTH', 960, 150, C.red, 56, 'center'), 0.3);
};
function teaserBox(t, seg, w0, draw, tx, y, x = 1600) {
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(x - 140, y - 130, 280, 260, 22, '#000'); ctx.restore(); rrS(x - 140, y - 130, 280, 260, 22, C.fig, 5); draw(x, y); }, 0.3);
  redX(x, y, 105, prog(t, tx + 0.25, 0.3));
}
const H2_HIT = 0.6, H2_BLACK = 0.4;
S.h2 = (t, seg) => {
  // three quick "do not"s: the handshake, where you live, no questions
  const ws = [[seg.start, wt(seg, 'do', 2), 'hard'], [wt(seg, 'do', 2), wt(seg, 'and'), 'live'], [wt(seg, 'and'), nextStart(seg), 'questions']];
  let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, word] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit;
  if (t < blk) {
    black();
    if (i === 0) cam(t, w0, blk - w0, 1.0, 1.12, 960, 560, () => handshake(t, { sq: prog(t, w0 + 0.3, blk - w0 - 0.5), shake: 4 * prog(t, w0 + 0.6, 0.6), crack: prog(t, hit, 0.15) }));
    else if (i === 1) cam(t, w0, blk - w0, 1.0, 1.2, 800, 520, () => clipboard(800, 540, 3.6, -0.05, { lines: [['NO. 117', 0], ['AGE  29', 0], ['LIVES ALONE', 0]], under: 2, up: prog(t, w0 + 0.6, 1.0) }));
    else { const k = ease(prog(t, w0 + 0.3, hit - w0 - 0.3)); focus(t, w0, blk - w0, 2.6, 3.0, ...CLOCK, () => meetRoom({ clock: [9, lerp(47, 0, k), 30 * (1 - k)], secRed: true, floor: false })); }
    if (d > 0) flatT(() => { ctx.globalAlpha = 0.35 * clamp(d / 0.2); ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); });
  }
  blackAfter(t, blk);
  const draws = [(x, y) => pageIcon('hand', x, y, '#fff'), (x, y) => icon7('pin', x, y, 0.9), (x, y) => icon7('ask', x, y, 1.0)];
  flatT(() => teaserBox(t, seg, w0, draws[i], wt(seg, word), 250, i === 2 ? 1600 : (i === 0 ? 1600 : 1600)));
};

// ---------- rule 1: do not shake too hard ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT SHAKE TOO HARD');
S.a1 = (t, seg) => {
  // the one on the left stands and holds out his hand; his fingers are longer than they should be
  const th = wt(seg, 'hand'), tf = wt(seg, 'fingers');
  if (t < tf - 0.2) {
    cam(t, seg.start, tf - seg.start, 1.0, 1.25, 700, 470, () => room(t, { arms: [t >= th - 0.6 ? 'hand' : 'desk', 'desk', 'laptop'], standI: [prog(t, seg.start + 0.3, 0.7), 0, 0], reach: ease(prog(t, th - 0.6, 0.8)), lid: 0, me: true, meX: 760 }));
    return;
  }
  black();
  cam(t, tf - 0.2, segEnd(seg) - tf, 1.0, 1.1, 1150, 560, () => handshake(t, { apart: 1 - 0, long: ease(prog(t, tf, 1.2)) }));
  if (t >= tf + 0.5) flatT(() => { ctx.save(); ctx.setLineDash([10, 10]); ln(620, 800, 1380, 800, 3, '#8a8a8a'); ctx.restore(); text('TOO LONG', 1000, 860, '900 48px M', C.red); });
};
S.a2 = (t, seg) => {
  // everyone's advice: a firm handshake, show them you are strong
  const tf = wt(seg, 'firm'), ts = wt(seg, 'show');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.05, 960, 520, () => {
    slideIn(t, seg.start, 0, -30, () => spaced('EVERYONE SAYS', 960, 260, '900 44px M', '#8a8a8a', 14), 0.4);
    okRow(t, tf - 0.3, 480, 450, 'A FIRM HANDSHAKE.', 64);
    okRow(t, ts - 0.3, 480, 650, 'SHOW THEM YOU ARE STRONG.', 56);
  });
};
S.a3 = (t, seg) => {
  // "Do not." The advice is crossed out. A firm grip is a challenge, and they always answer one.
  const tc = wt(seg, 'challenge'), ta = wt(seg, 'answer');
  if (t < tc - 0.2) {
    black();
    cam(t, seg.start, tc - seg.start, 1.0, 1.04, 960, 520, () => {
      spaced('EVERYONE SAYS', 960, 260, '900 44px M', '#5a5a5a', 14);
      okRow(t, -9, 480, 450, 'A FIRM HANDSHAKE.', 64); okRow(t, -9, 480, 650, 'SHOW THEM YOU ARE STRONG.', 56);
      ctx.save(); redGlow(12); lnP(460, 470, 1500, 430, 12, C.red, prog(t, seg.start + 0.1, 0.25)); lnP(460, 670, 1560, 630, 12, C.red, prog(t, seg.start + 0.3, 0.25)); ctx.restore();
    });
    return;
  }
  // close on the left agent: a glint in his lenses
  focus(t, tc - 0.2, segEnd(seg) - tc, 2.2, 2.5, IX[0] - 200, HEADY + 20, () => room(t, { arms: 'desk', lid: 0, look: Math.sin(t * 2) }));
  if (t >= ta) flatT(() => pop(t, ta, 520, 560, () => { tag('CHALLENGE', 520, 540, C.red, 64, 'center'); tag('ACCEPTED', 520, 650, C.red, 64, 'center'); }, 0.3));
};
S.a4 = (t, seg) => {
  // squeeze, and he squeezes back; harder; he does not stop when you stop
  const tq = wt(seg, 'squeezes'), th = wt(seg, 'harder', 1), th2 = wt(seg, 'harder', 2), ts = wt(seg, 'stop', 2);
  const you = t < ts ? lerp(0.3, 0.85, ease(prog(t, seg.start, 1.0))) : lerp(0.85, 0.15, ease(prog(t, ts - 0.4, 0.5)));
  const him = Math.max(0, lerp(0, 0.7, ease(prog(t, tq - 0.2, 0.6))) + 0.25 * ease(prog(t, th, 0.5)) + 0.35 * ease(prog(t, th2, 0.5)) + 0.4 * prog(t, ts, 1.5));
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 860, 560, () => handshake(t, { sq: clamp(him), shake: him > 1 ? 4 : him * 2 }));
  gripMeter(t, { you, him });
};
S.a5 = (t, seg) => {
  // the waiting room: a row of candidates; a crack through the door; every head turns
  const th = wt(seg, 'heard'), tw = wt(seg, 'waiting');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 1.2, 1.0, 1.08, 900, 560, () => {
    ln(-200, 900, W + 200, 900, 3, '#262626');
    rrS(1480, 360, 220, 540, 4, C.fig, 5); circ(1504, 640, 8, C.fig); spaced('INTERVIEW', 1590, 330, '900 30px M', '#8a8a8a', 6);
    for (let i = 0; i < 4; i++) sitSide(260 + i * 290, 900, 0.95, { dir: 1, hair: i === 1 });
    if (t >= th - 0.15) { const k = prog(t, th - 0.15, 0.2); ctx.save(); ctx.globalAlpha *= k; redGlow(24);
      for (const [a, l] of [[-2.6, 120], [-3.0, 160], [2.7, 120], [-2.2, 90]]) { const x0 = 1470, y0 = 560; poly([[x0, y0], [x0 + Math.cos(a) * l * 0.5 + 10, y0 + Math.sin(a) * l * 0.5 + 12], [x0 + Math.cos(a) * l, y0 + Math.sin(a) * l]], 7, C.red); }
      noGlow(); ctx.restore();
      for (let i = 0; i < 4; i++) pop(t, th + 0.1 + i * 0.08, 260 + i * 290, 420, () => text('!', 260 + i * 290 + 10, 470 - 0 * 0.95, '900 60px M', C.fig), 0.2); }
    if (t >= th + 0.1) pop(t, th + 0.1, 1590, 220, () => tag('CRACK.', 1590, 230, C.red, 60, 'center'), 0.25);
  });
};
S.a6 = (t, seg) => {
  // he signs everything with his left hand now: a right arm in a cast and sling, the left hand writing
  const tl = wt(seg, 'left');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 960, 560, () => {
    // the contract
    glow(); rr(560, 380, 620, 560, 8, '#fbfbfb'); noGlow(); text('CONTRACT', 870, 460, '900 44px M', '#111');
    for (let i = 0; i < 6; i++) rr(620, 510 + i * 44, i % 3 === 2 ? 300 : 500, 12, 3, '#c4c4c8');
    ln(620, 860, 1000, 860, 3, '#111');
    const k = prog(t, seg.start + 0.4, 2.2);
    ctx.save(); ctx.beginPath(); for (let i = 0; i <= 40 * k; i++) { const x = 640 + i * 8.5, y = 836 + Math.sin(i * 0.9) * 18 * (1 - i / 50) + (i % 7 === 0 ? -14 : 0); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.strokeStyle = '#111'; ctx.lineWidth = 4; ctx.stroke(); ctx.restore();
    // the left hand with the pen, shaky
    const px = 640 + 340 * k, py = 836 + Math.sin(t * 30) * 4;
    pen(px, py, 1.2, -0.5); ctx.save(); glow(); ell(px + 40, py - 60, 50, 36, -0.5, C.fig); noGlow(); ctx.beginPath(); ctx.ellipse(px + 40, py - 60, 50, 36, -0.5, 0, Math.PI * 2); ctx.strokeStyle = '#000'; ctx.lineWidth = 3; ctx.stroke(); ctx.restore();
    // the right arm in a cast and a sling
    ctx.save(); glow(); rr(1300, 300, 130, 420, 60, C.fig); noGlow(); rrS(1300, 300, 130, 420, 60, '#000', 3); for (let i = 0; i < 5; i++) ln(1310, 380 + i * 60, 1420, 400 + i * 60, 2, '#9a9a9a');
    ln(1290, 260, 1440, 760, 10, '#5a5a5a'); ctx.restore();
  });
  if (t >= tl) flatT(() => pop(t, tl, 960, 160, () => tag('LEFT HAND ONLY', 960, 170, C.red, 56, 'center'), 0.3));
};
S.a7 = (t, seg) => {
  // keep your hand soft; let him hold it; count to three
  const tc = wt(seg, 'count'), th = wt(seg, 'three');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 860, 560, () => handshake(t, { sq: 0.15 }));
  gripMeter(t, { you: 0.12, him: 0.18 });
  if (t >= tc) flatT(() => { for (let k = 0; k < 3; k++) { const t0 = tc + 0.25 + k * ((th - tc) / 2.2); if (t >= t0) pop(t, t0, 360 + k * 220, 220, () => text(String(k + 1), 360 + k * 220, 260, '900 140px M', C.fig), 0.25); } });
};
S.a8 = (t, seg) => {
  // he loses interest and lets go; he writes "NOT A THREAT"
  const tl = wt(seg, 'lets'), tw = wt(seg, 'writes'), tg = wt(seg, 'good');
  black();
  if (t < tw - 0.2) { cam(t, seg.start, tw - seg.start, 1.0, 1.04, 960, 560, () => handshake(t, { apart: prog(t, tl - 0.2, 0.8) })); return; }
  cam(t, tw - 0.2, segEnd(seg) - tw, 1.0, 1.06, 960, 520, () => {
    clipboard(960, 540, 3.2, -0.04, { lines: [['CANDIDATE', 0], ['GRIP: SOFT', 0], ['NOT A THREAT', 0]], under: 2, up: prog(t, tw + 0.6, 0.8) });
  });
  if (t >= tg) flatT(() => { ctx.save(); ctx.translate(1480, 300); check(0, 0, 70, prog(t, tg, 0.3)); ctx.restore(); });
};

// ---------- rule 2: do not tell the truth ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT TELL THE TRUTH');
function folder(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.25)', 22);
  rr(-260, -200, 200, 50, 10, '#d8d8d8'); rr(-260, -170, 520, 360, 12, '#ececec'); noGlow(); rrS(-260, -170, 520, 360, 12, '#000', 3);
  text('CANDIDATE: YOU', -220, -100, '900 36px M', '#111', 'left'); ln(-220, -80, 220, -80, 3, '#9a9a9a');
  (o.lines || []).forEach((l, i) => text(l, -220, -30 + i * 46, '900 30px M', l.startsWith('!') ? '#d61f1f' : '#333', 'left'));
  if (!o.lines) for (let i = 0; i < 3; i++) rr(-220, -40 + i * 40, i === 2 ? 220 : 360, 14, 4, '#b9b9b9');
  ctx.restore();
}
// a small house pictogram
function house(x, y, s = 1, col = C.fig) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16); pth('M-70,0 L-70,-80 L0,-140 L70,-80 L70,0 Z', col); noGlow(); rr(-18, -60, 36, 60, 3, '#000'); ctx.restore(); }
S.b1 = (t, seg) => {
  // everything goes into a file; the file is a map to you
  const tm = wt(seg, 'map', 1), tm2 = wt(seg, 'map', 2);
  black();
  if (t < tm - 0.2) { cam(t, seg.start, tm - seg.start, 1.0, 1.1, 960, 540, () => folder(960, 560, 1.4, { lines: ['NAME', 'LAST JOB', 'ADDRESS'] })); return; }
  cam(t, tm - 0.2, segEnd(seg) - tm, 1.0, 1.08, 960, 540, () => {
    // a street map: a grid, the office on the left, your house on the right, a red route drawn between them
    for (let i = 0; i < 9; i++) { ln(160 + i * 200, 120, 160 + i * 200, 980, 3, '#262626'); ln(100, 140 + i * 110, 1820, 140 + i * 110, 3, '#262626'); }
    glow(); rr(220, 420, 160, 200, 6, C.fig); noGlow(); for (let i = 0; i < 3; i++) for (let j = 0; j < 4; j++) rr(240 + i * 46, 440 + j * 44, 30, 26, 3, '#000'); text('ROOM 4B', 300, 670, '900 30px M', '#8a8a8a');
    house(1580, 760, 1.2);
    const route = [[380, 520], [760, 520], [760, 250], [1160, 250], [1160, 690], [1500, 690]], p = prog(t, tm + 0.1, 1.6);
    ctx.save(); ctx.setLineDash([22, 16]); redGlow(14); let acc = 0; const segs = route.slice(1).map((q, i) => Math.hypot(q[0] - route[i][0], q[1] - route[i][1])), tot = segs.reduce((a, b) => a + b, 0);
    ctx.beginPath(); ctx.moveTo(...route[0]); for (let i = 0; i < segs.length; i++) { const r = clamp((p * tot - acc) / segs[i]); if (r <= 0) break; ctx.lineTo(lerp(route[i][0], route[i + 1][0], r), lerp(route[i][1], route[i + 1][1], r)); acc += segs[i]; }
    ctx.strokeStyle = C.red; ctx.lineWidth = 9; ctx.stroke(); ctx.restore();
    if (t >= tm2) pop(t, tm2, 1580, 560, () => { ctx.save(); redGlow(20); icon7('pin', 1580, 540, 0.8, C.red); ctx.restore(); text('YOU', 1580, 900, '900 50px M', C.red); }, 0.3);
  });
};
S.b2 = (t, seg) => {
  // "Tell me about yourself." Your name, one sentence, then stop.
  const ts = wt(seg, 'say', 1), to = wt(seg, 'one'), tt = wt(seg, 'stop');
  if (t < ts - 0.2) { cam(t, seg.start, ts - seg.start, 1.0, 1.08, 960, 470, () => room(t, { me: true, lid: 0 })); say(t, seg.start + 0.05, 960, 120, 'TELL ME ABOUT YOURSELF.', 960, 250, 50); return; }
  black();
  cam(t, ts - 0.2, segEnd(seg) - ts, 1.0, 1.05, 960, 520, () => {
    sitSide(480, 900, 1.35, { dir: 1 });
    [['SAY YOUR NAME.', ts], ['ONE SENTENCE.', to], ['THEN STOP.', tt]].forEach(([l, t0], i) => okRow(t, t0 - 0.15, 860, 300 + i * 190, l, 58));
  });
};
S.b3 = (t, seg) => {
  // never say you live alone: she said it; the one in the middle wrote it down and underlined it twice
  const tc = wt(seg, 'candidate'), tw = wt(seg, 'wrote'), tu = wt(seg, 'underlined'), t2 = wt(seg, 'twice');
  if (t < tw - 0.3) {
    black();
    cam(t, seg.start, tw - seg.start, 1.0, 1.06, 760, 560, () => {
      ln(-200, 900, W + 200, 900, 3, '#262626'); sitSide(560, 900, 1.3, { dir: 1, hair: true });
      if (t < tc) { listCard(240, 90, 860, 190); noRow(t, seg.start, seg.start + 0.9, 290, 185, 'pin', 'I LIVE ALONE', 60); }
      else say(t, tc, 700, 240, 'I LIVE ALONE.', 640, 360, 56);
      agent('hr', 1500, 760, 0.9, { arms: 'desk' }); meetDesk(1150, 1850, 760, { items: false });
    });
    return;
  }
  black();
  const up1 = prog(t, tu - 0.05, 0.6), up2 = prog(t, t2 - 0.05, 0.5);
  cam(t, tw - 0.3, segEnd(seg) - tw + 1.2, 1.0, 1.2, 900, 520, () => {
    clipboard(900, 560, 4.4, -0.04, { lines: [['NO. 117', 0], ['AGE  29', 0], ['LIVES ALONE', up1 > 0.9 ? 1 : 0]], under: 2, up: up1 });
    ctx.save(); ctx.translate(900, 560); ctx.rotate(-0.04); ctx.scale(4.4, 4.4); ctx.font = '900 15px M'; const w = ctx.measureText('LIVES ALONE').width;
    if (up2 > 0) lnP(-62, 40, -58 + w, 39, 3.5, '#d61f1f', up2);
    pen(-62 + (w + 4) * (up2 > 0 ? up2 : up1), (up2 > 0 ? 8 : 0) - 24 + 2 * 28, 0.6, 2.0); ctx.restore();
  });
};
S.b4 = (t, seg) => {
  // living alone: no one notices when you stop coming home. Your window goes dark; the mail piles up; the days count.
  const tn = wt(seg, 'notice'), ts = wt(seg, 'stop');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 1.2, 1.0, 1.1, 960, 560, () => {
    ln(-200, 940, W + 200, 940, 3, '#262626');
    rrS(560, 140, 800, 800, 4, C.fig, 5);
    for (let r = 0; r < 5; r++) for (let c = 0; c < 5; c++) { const mine = r === 2 && c === 3, dark = mine && t >= ts - 0.2;
      if (dark) rrS(620 + c * 150, 190 + r * 140, 90, 80, 3, '#5a5a5a', 3); else { glow('rgba(255,255,255,0.4)', 14); rr(620 + c * 150, 190 + r * 140, 90, 80, 3, C.fig); noGlow(); } }
    // your door: the mail piles up
    rrS(1460, 700, 150, 240, 4, C.fig, 4);
    const n = Math.floor(lerp(0, 9, ease(prog(t, tn, 2.5))));
    for (let i = 0; i < n; i++) { ctx.save(); ctx.translate(1535 + (hash(i) - 0.5) * 80, 930 - i * 14); ctx.rotate((hash(i * 3) - 0.5) * 0.5); rr(-50, -12, 100, 28, 3, '#fbfbfb'); rrS(-50, -12, 100, 28, 3, '#000', 2); ctx.restore(); }
    if (t >= tn) { const d = Math.floor(lerp(1, 31, ease(prog(t, tn, 3.0)))); pop(t, tn, 360, 300, () => { listCard(170, 220, 380, 160); text('DAYS GONE', 360, 270, '600 26px Plex', '#8a8a8a'); text(String(d), 360, 350, '900 64px M', C.red); }, 0.3); }
  });
};
S.b5 = (t, seg) => {
  const tl = wt(seg, 'leans'), tg = wt(seg, 'glasses'), tw = wt(seg, 'what'), lean = ease(prog(t, tl, 1.2));
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.6, 960, 420, () => room(t, { lean, eyes: prog(t, tg - 0.1, 0.4), lid: 0 }));
  say(t, tw - 0.1, 960, 120, 'WHAT IS YOUR GREATEST WEAKNESS?', 960, 230, 46);
};
S.b6 = (t, seg) => {
  // your real weakness is how they will come for you
  const tr = wt(seg, 'real'), th = wt(seg, 'how');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.05, 960, 520, () => {
    pop(t, seg.start, 960, 260, () => { glow(); spaced('DO NOT TELL THE TRUTH', 960, 290, '900 70px M', C.fig, 6); noGlow(); }, 0.3);
    if (t >= tr - 0.1) slideIn(t, tr - 0.1, -40, 0, () => { glow(); rr(300, 480, 560, 150, 16, C.fig); noGlow(); text('YOUR REAL', 580, 545, '900 48px M', '#000'); text('WEAKNESS', 580, 600, '900 48px M', '#000'); }, 0.35);
    if (t >= th - 0.3) { lnP(880, 555, 1040, 555, 10, C.red, prog(t, th - 0.3, 0.3)); pth('M1040,525 L1090,555 L1040,585 Z', t >= th ? C.red : 'rgba(0,0,0,0)'); }
    if (t >= th) slideIn(t, th, 40, 0, () => { redGlow(26); rr(1100, 480, 560, 150, 16, C.red); noGlow(); text('HOW THEY', 1380, 545, '900 48px M', '#fff'); text('COME FOR YOU', 1380, 600, '900 48px M', '#fff'); }, 0.35);
  });
};
S.b7 = (t, seg) => {
  // "I'm afraid of the dark." That night, the power goes out in his building. Only his building.
  const tn = wt(seg, 'night'), tp = wt(seg, 'power'), to = wt(seg, 'only');
  black();
  if (t < tn - 0.2) {
    cam(t, seg.start, tn - seg.start, 1.0, 1.06, 760, 560, () => { ln(-200, 900, W + 200, 900, 3, '#262626'); sitSide(560, 900, 1.3, { dir: 1 }); say(t, seg.start + 0.3, 760, 240, '"I\'M AFRAID OF THE DARK."', 640, 360, 50); agent('hr', 1500, 760, 0.9, { arms: 'desk', eyes: 1 }); meetDesk(1150, 1850, 760, { items: false }); });
    return;
  }
  const off = t >= tp + 0.1;
  cam(t, tn - 0.2, segEnd(seg) - tn + 1.4, 1.0, 1.14, 960, 560, () => {
    ln(-200, 940, W + 200, 940, 3, '#262626');
    const B = [[140, 520, 260], [440, 300, 300], [790, 420, 300], [1140, 260, 280], [1460, 480, 320]];
    B.forEach(([x, top, w], bi) => { const his = bi === 2, dark = his && off;
      rrS(x, top, w, 940 - top, 3, dark ? '#3a3a3a' : '#8a8a8a', 3);
      for (let r = 0; r < Math.floor((900 - top) / 70); r++) for (let c = 0; c < Math.floor((w - 30) / 60); c++) {
        const lit = hash(bi * 97 + r * 13 + c) > 0.35; if (!lit || dark) continue; rr(x + 24 + c * 60, top + 30 + r * 70, 34, 36, 2, C.fig); } });
    // in the dark building, a window with three pairs of red lenses
    if (off && t >= to) { ctx.save(); ctx.globalAlpha *= prog(t, to + 0.3, 0.5); redGlow(18); for (let k = 0; k < 3; k++) { rr(830 + k * 70, 650, 22, 10, 3, C.red); rr(856 + k * 70, 650, 22, 10, 3, C.red); } ctx.restore(); }
  });
  if (t >= to) flatT(() => pop(t, to, 960, 150, () => tag('ONLY HIS BUILDING', 960, 160, C.red, 56, 'center'), 0.3));
};
S.b8 = (t, seg) => {
  // the answer everyone gives
  const tw = wt(seg, 'work'), tp = wt(seg, "perfectionist");
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.05, 960, 520, () => {
    slideIn(t, seg.start, 0, -30, () => spaced('THE ANSWER EVERYONE GIVES', 960, 280, '900 44px M', '#8a8a8a', 12), 0.4);
    okRow(t, tw - 0.4, 480, 470, '"I WORK TOO HARD."', 64);
    okRow(t, tp - 0.5, 480, 670, '"I\'M A PERFECTIONIST."', 64);
  });
};
S.b9 = (t, seg) => {
  // already in every file: a wall of identical files; then the red fades from his glasses
  const tl = wt(seg, 'learn'), tr = wt(seg, 'red');
  if (t < tr - 0.4) {
    black();
    cam(t, seg.start, tr - seg.start, 1.15, 1.0, 960, 540, () => {
      for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) { const x = 230 + c * 292, y = 220 + r * 210, k = prog(t, seg.start + (r * 6 + c) * 0.04, 0.25);
        ctx.save(); ctx.globalAlpha *= k; rr(x - 120, y - 80, 240, 160, 8, '#ececec'); rr(x - 120, y - 100, 90, 26, 6, '#d8d8d8'); text('"I WORK', x, y - 10, '900 26px M', '#333'); text('TOO HARD."', x, y + 26, '900 26px M', '#333'); ctx.restore(); }
      if (t >= tl) pop(t, tl, 960, 540, () => { ctx.save(); glow(); rr(560, 470, 800, 140, 16, '#000'); rrS(560, 470, 800, 140, 16, C.fig, 4); noGlow(); text('NOTHING NEW', 960, 565, '900 70px M', C.fig); ctx.restore(); }, 0.3);
    });
    return;
  }
  focus(t, tr - 0.4, segEnd(seg) - tr, 2.6, 2.8, IX[1], HEADY + 10, () => room(t, { eyes: 1 - prog(t, tr + 0.1, 1.0), lid: 0 }));
};

// ---------- rule 3: never say you have no questions ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'NEVER SAY YOU HAVE NO QUESTIONS');
S.c1 = (t, seg) => {
  const tp = wt(seg, 'pens'), td = wt(seg, 'do');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.1, 960, 470, () => room(t, { arms: t < tp ? 'board' : 'desk', me: true, lid: 0 }));
  say(t, td - 0.1, 960, 120, 'DO YOU HAVE ANY QUESTIONS FOR US?', 960, 240, 46);
};
S.c2 = (t, seg) => {
  // the interview only ends when you ask: the exit is locked until a question unlocks it
  const te = wt(seg, 'ends'), ta = wt(seg, 'ask');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 1300, 520, () => room(t, { door: { lock: prog(t, seg.start + 0.4, 0.3) }, me: true, meX: 900, lid: 0 }));
  if (t >= ta) pop(t, ta, 1805, 700, () => { glow(); circ(1805, 690, 50, C.fig); noGlow(); text('?', 1805, 718, '900 76px M', '#000'); }, 0.3);
};
S.c3 = (t, seg) => {
  // "No, I think you covered everything." The clock goes back to nine.
  const tc = wt(seg, 'clock'), tn = wt(seg, 'nine');
  if (t < tc - 0.3) {
    cam(t, seg.start, 3, 1.0, 1.05, 960, 470, () => room(t, { me: true, lid: 0 }));
    say(t, seg.start + 0.2, 1400, 830, '"NO, I THINK YOU\nCOVERED EVERYTHING."', 1040, 760, 46);
    return;
  }
  const k = ease(prog(t, tc + 0.1, tn - tc + 0.1)), m = lerp(58, 0, k);
  focus(t, tc - 0.3, 4, 3.0, 3.3, ...CLOCK, () => meetRoom({ clock: [9, m, (t * 60) % 60 * (1 - k)], secRed: true, floor: false }));
  if (k >= 1) flatT(() => pop(t, tn, 960, 900, () => tag('9:00 AM', 960, 920, C.red, 60, 'center'), 0.3));
};
S.c4 = (t, seg) => {
  // the one on the left stands and holds out his hand again: it starts over
  const tg = wt(seg, 'again'), tt = wt(seg, 'thanks'), ts = wt(seg, 'starts');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.2, 760, 470, () => room(t, { arms: ['hand', 'desk', 'laptop'], standI: [prog(t, seg.start + 0.1, 0.6), 0, 0], reach: ease(prog(t, seg.start + 0.3, 0.8)), lid: 0, clock: [9, 0, 0], me: true, meX: 760 }));
  say(t, tt - 0.1, 760, 120, 'THANKS FOR COMING IN.', 620, 250, 46);
  if (t >= ts) flatT(() => pop(t, ts, 1500, 900, () => tag('AGAIN.', 1500, 920, C.red, 60, 'center'), 0.3));
};
S.c5 = (t, seg) => {
  // the loop: handshake, question, clock, around and around until you ask
  const th = wt(seg, 'handshake'), tq = wt(seg, 'question'), tu = wt(seg, 'until');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 540, () => {
    const R = 300, cx = 960, cy = 540, rot = t * 0.9;
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot);
    for (let k = 0; k < 3; k++) { ctx.beginPath(); ctx.arc(0, 0, R, k * 2.09 + 0.25, k * 2.09 + 1.85); ctx.strokeStyle = '#5a5a5a'; ctx.lineWidth = 10; ctx.stroke();
      const a = k * 2.09 + 1.85; ctx.save(); ctx.rotate(a); ctx.translate(R, 0); pth('M-22,-10 L0,30 L22,-10 Z', '#5a5a5a'); ctx.restore(); }
    ctx.restore();
    const icons = [(x, y) => pageIcon('hand', x, y, '#fff'), (x, y) => icon7('ask', x, y, 0.6), (x, y) => icon7('clock', x, y, 0.6)], times = [th, tq, seg.start];
    for (let k = 0; k < 3; k++) { const a = rot + k * 2.09 - 1.57, x = cx + Math.cos(a) * R, y = cy + Math.sin(a) * R;
      ctx.save(); glow(); circ(x, y, 74, '#000'); noGlow(); circS(x, y, 74, k === 0 && t >= th && t < tq ? C.red : C.fig, 5); icons[k](x, y); ctx.restore(); }
    const loops = 1 + Math.floor((t - seg.start) * 1.6);
    text('LOOP', cx, cy - 20, '600 30px Plex', '#8a8a8a'); text(String(loops), cx, cy + 60, '900 90px M', C.fig);
    if (t >= tu) pop(t, tu, cx, cy + 420, () => tag('UNTIL YOU ASK', cx, cy + 440, C.red, 56, 'center'), 0.3);
  });
};
S.c6 = (t, seg) => {
  // one candidate said no forty times; for him it is still Monday, nine A.M.
  const tf = wt(seg, 'forty'), tm = wt(seg, 'monday');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 1.0, 1.0, 1.12, 760, 560, () => {
    ln(-200, 900, W + 200, 900, 3, '#262626'); sitSide(620, 900, 1.3, { dir: 1 });
    const n = Math.floor(lerp(1, 40, ease(prog(t, seg.start + 0.3, Math.max(0.5, tf - seg.start)))));
    pop(t, seg.start + 0.3, 330, 330, () => { listCard(170, 240, 330, 170); text('"NO."', 335, 300, '900 40px M', '#8a8a8a'); text('×' + n, 335, 380, '900 70px M', t >= tf ? C.red : C.fig); }, 0.3);
    if (t >= tm) pop(t, tm, 1320, 600, () => { glow(); rr(1180, 500, 280, 220, 12, '#ececec'); noGlow(); rr(1180, 500, 280, 64, 12, '#d61f1f'); text('MONDAY', 1320, 546, '900 34px M', '#fff'); text('9:00', 1320, 676, '900 86px M', '#111'); }, 0.3);
  });
};
S.c7 = (t, seg) => {
  const ts = wt(seg, 'salary'), tl = wt(seg, 'last');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.1, 1.18, 960, 470, () => room(t, { eyes: 1, lid: 0 }));
  listCard(380, 280, 1160, 440);
  noRow(t, ts - 0.4, ts + 0.3, 440, 400, 'money', 'THE SALARY', 52);
  noRow(t, tl - 0.4, tl + 0.4, 440, 590, 'ask', 'THE LAST PERSON IN THIS JOB', 46);
};
S.c8 = (t, seg) => {
  // the one question: when will I hear back? The lock opens.
  const tw = wt(seg, 'when');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 1300, 520, () => room(t, { door: { lock: 1, open: prog(t, seg.end - 0.6, 0.4) }, me: true, meX: 900, lid: 0 }));
  say(t, tw - 0.1, 1340, 860, '"WHEN WILL I\nHEAR BACK?"', 1000, 780, 50);
  if (t >= seg.end - 0.6) flatT(() => { ctx.translate(1805, 420); check(0, 0, 40, prog(t, seg.end - 0.6, 0.3)); });
};
S.c9 = (t, seg) => {
  const ts = wt(seg, 'stand'), tw = wt(seg, "we'll");
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 470, () => room(t, { stand: prog(t, ts - 0.1, 0.8), arms: 'down', lid: 0 }));
  say(t, tw - 0.1, 960, 110, "WE'LL BE IN TOUCH.", 960, 210, 54);
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
S.d1 = (t, seg) => {
  // break even one rule, and they will be in touch, exactly as promised
  const tb = wt(seg, 'broke'), tt = wt(seg, 'touch'), te = wt(seg, 'exactly');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, W / 2, 520, () => {
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9], struck: [null, tb + 0.3, null, null], dim: prog(t, tt, 0.4) });
  });
  if (t >= tt) flatT(() => pop(t, tt, 960, 900, () => { ctx.save(); redGlow(24); rr(520, 830, 880, 130, 16, C.red); noGlow(); text("THEY'LL BE IN TOUCH", 960, 915, '900 60px M', '#fff'); ctx.restore(); }, 0.3));
};
S.d2 = (t, seg) => {
  // 3 AM. You wake up. Three of them at the foot of your bed, holding your file.
  const tw = wt(seg, 'wake'), ti = wt(seg, 'interviewers'), tf = wt(seg, 'foot');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.1, 1100, 560, () => {
    const on = t >= ti - 0.1;
    night(t, { bed: t >= tw ? 'woke' : 'sleep', trio: on, eyes: prog(t, ti + 0.3, 0.3) });
    if (on && t < ti + 0.25) { ctx.save(); ctx.globalAlpha = 0.25 * (1 - prog(t, ti - 0.1, 0.35)); ctx.fillStyle = '#fff'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
  });
  if (t >= tf) flatT(() => pop(t, tf, 1420, 150, () => tag('3:00 AM', 1420, 160, C.red, 52, 'center'), 0.3));
};
S.d3 = (t, seg) => {
  cam(t, seg.start, segEnd(seg) - seg.start + 0.3, 1.3, 1.4, 1440, 500, () => night(t, {}));
  say(t, seg.start + 0.1, 1100, 190, 'WE HAVE A FEW\nMORE QUESTIONS.', 1420, 330, 40);
};
S.d4 = (t, seg) => {
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 520, () => {
    pop(t, seg.start, 960, 470, () => { ctx.save(); redGlow(24); spaced('DOES NOT WORK', 960, 500, '900 110px M', C.red, 8); ctx.restore(); }, 0.35);
    lnP(420, 560, 1500, 560, 6, C.red, prog(t, seg.start + 0.3, 0.5));
  });
};
S.d5 = (t, seg) => {
  // pretending to sleep: LACKS ENTHUSIASM
  const tl = wt(seg, 'lacks');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 1000, 560, () => night(t, { bed: 'sleep' }));
  noHead(t, seg, 'sleep', 'PRETEND TO SLEEP', seg.start + 1.5);
  noteCard(t, tl - 0.1, 1300, 280, 'LACKS ENTHUSIASM', -0.05, '#d61f1f');
};
S.d6 = (t, seg) => {
  // screaming: STRONG COMMUNICATION SKILLS
  const tsc = wt(seg, 'screaming'), ts = wt(seg, 'strong');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 1000, 560, () => {
    night(t, { sitUp: true });
    // sound lines from your head (no mouth)
    if (t >= tsc) { ctx.save(); ctx.globalAlpha *= 0.9; for (let k = 0; k < 3; k++) { const r = 60 + k * 40 + ((t * 120) % 40); ctx.beginPath(); ctx.arc(360 + 156 * 1.3, 900 - 410 * 1.3, r, -0.7, 0.7); ctx.strokeStyle = C.fig; ctx.lineWidth = 6; ctx.stroke(); } ctx.restore(); }
  });
  noHead(t, seg, 'sweat', 'SCREAM', seg.start + 1.0);
  noteCard(t, ts - 0.1, 1300, 280, 'STRONG COMMUNICATION SKILLS', -0.05, '#111');
};
S.d7 = (t, seg) => {
  // another job: they ask for the company's name, and they visit that company too
  const ta = wt(seg, 'ask'), tv = wt(seg, 'visit');
  if (t < tv - 0.3) {
    cam(t, seg.start, tv - seg.start, 1.0, 1.08, 1000, 560, () => night(t, { sitUp: true }));
    noHead(t, seg, 'offer', 'ANOTHER JOB', ta + 0.3);
    say(t, ta - 0.1, 1150, 200, "WHAT'S THE\nCOMPANY'S NAME?", 1420, 330, 40);
    return;
  }
  cam(t, tv - 0.3, segEnd(seg) - tv + 0.5, 1.0, 1.1, 960, 560, () => {
    black();
    rrS(620, 80, 680, 900, 4, '#8a8a8a', 4);
    for (let r = 0; r < 12; r++) for (let c = 0; c < 6; c++) { const lit = hash(r * 7 + c) > 0.45; if (lit) rr(660 + c * 104, 120 + r * 66, 76, 40, 3, '#cfcfcf'); }
    rr(840, 860, 240, 120, 4, '#000'); rrS(840, 860, 240, 120, 4, C.fig, 3); ln(-200, 980, W + 200, 980, 3, '#262626');
    trio(t, { xs: [900, 960, 1020], s: 0.18, y: 980, arms: 'down' });
  });
  noHead(t, seg, 'offer', 'ANOTHER JOB', ta + 0.3);
};
S.d8 = (t, seg) => {
  // only one thing works: remember what they are. Not monsters. Employees.
  const tr = wt(seg, 'remember'), tm = wt(seg, 'monsters'), te = wt(seg, 'employees');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 520, () => {
    if (t < tr - 0.1) { pop(t, seg.start, 960, 520, () => { glow(); spaced('ONLY ONE THING WORKS', 960, 540, '900 70px M', C.fig, 6); noGlow(); }, 0.35); return; }
    agent('hr', 960, 1000, 0.95, { stand: 1, arms: 'down', eyes: 0 });
    if (t >= tm - 0.1) { pop(t, tm - 0.1, 420, 420, () => { text('MONSTER', 420, 440, '900 64px M', C.fig); }, 0.3); redX(420, 420, 110, prog(t, tm + 0.3, 0.3)); }
    if (t >= te - 0.1) { pop(t, te - 0.1, 1500, 420, () => { glow(); rr(1240, 360, 520, 120, 14, C.fig); noGlow(); text('EMPLOYEE', 1500, 440, '900 64px M', '#000'); }, 0.3);
      ctx.save(); ctx.globalAlpha *= prog(t, te, 0.3); ctx.translate(960, 1000 - 300 * 0.95); ctx.scale(0.95, 0.95); rr(30, -150, 72, 44, 5, C.fig); rrS(30, -150, 72, 44, 5, '#000', 3); text('STAFF', 66, -121, '900 17px M', '#000'); ctx.restore(); }
  });
};
S.d9 = (t, seg) => {
  // every employee is afraid of the same thing: one empty cardboard box under a light
  const ts = wt(seg, 'same');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 0.4, 1.0, 1.15, 960, 600, () => {
    const g = ctx.createRadialGradient(960, 300, 20, 960, 700, 520); g.addColorStop(0, 'rgba(255,255,255,0.16)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ln(400, 860, 1520, 860, 3, '#262626');
    fadeIn(t, seg.start + 0.3, () => cardboardBox(960, 760, 1.6), 0.6);
    if (t >= ts) { ctx.save(); ctx.globalAlpha *= prog(t, ts, 0.4); redGlow(16); spaced('THE BOX', 960, 960, '900 54px M', C.red, 10); ctx.restore(); }
  });
};
S.d10 = (t, seg) => {
  // sit up, fold your hands, look the middle one in the eye: "Congratulations. You're hired."
  const te = wt(seg, 'eye'), tc = wt(seg, 'congratulations');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, t >= te ? 1.2 : 1.06, t >= te ? 1200 : 1000, 540, () => night(t, { sitUp: true }));
  if (t >= te && t < tc) flatT(() => brackets(1420, 900 - 0.78 * 640 + 60, 160, 160, prog(t, te, 0.3)));
  say(t, tc - 0.1, 760, 200, '"CONGRATULATIONS.\nYOU\'RE HIRED."', 620, 380, 50);
};
S.d11 = (t, seg) => {
  // they freeze. Whoever makes the offer is the boss. You just made the offer.
  const tf = wt(seg, 'freeze'), tb = wt(seg, 'boss'), tm = wt(seg, 'made');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.05, 1.12, 1000, 540, () => {
    night(t, { sitUp: true, eyes: 1 - prog(t, tf, 0.3) });
    if (t >= tf) { ctx.save(); ctx.globalAlpha *= prog(t, tf, 0.25); for (let i = 0; i < 3; i++) { rr(TRIO[i] - 26, 220, 18, 60, 4, C.fig); rr(TRIO[i] + 8, 220, 18, 60, 4, C.fig); } ctx.restore(); }
  });
  flatT(() => {
    if (t >= tb - 0.1) slideIn(t, tb - 0.1, -40, 0, () => { listCard(70, 70, 700, 160); text('MAKES THE OFFER', 110, 136, '600 30px Plex', '#8a8a8a', 'left'); text('= THE BOSS', 110, 200, '900 54px M', C.fig, 'left'); }, 0.35);
    if (t >= tm) pop(t, tm, 590, 330, () => { glow(); rr(470, 290, 240, 70, 12, C.fig); noGlow(); text('YOU', 590, 342, '900 48px M', '#000'); }, 0.3);
  });
};
S.d12 = (t, seg) => {
  // their clipboards drop; they stand up straight; they are your employees now
  const td = wt(seg, 'drop'), ts = wt(seg, 'straight'), te = wt(seg, 'employees');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.05, 1.1, 1100, 540, () => night(t, { sitUp: true, eyes: 0, arms: t >= td - 0.1 ? 'down' : 'board', drop: t >= td - 0.1 ? prog(t, td - 0.1, 0.6) : 0, badges: prog(t, te, 0.4) }));
  if (t >= te) flatT(() => pop(t, te, 1420, 150, () => tag('YOUR EMPLOYEES', 1420, 160, C.fig, 52, 'center'), 0.3));
};
S.d13 = (t, seg) => {
  // "Unfortunately... we're letting you go. Effective immediately."
  const tu = wt(seg, 'unfortunately'), te = wt(seg, 'effective');
  cam(t, seg.start, segEnd(seg) - seg.start, 1.05, 1.12, 1000, 540, () => night(t, { sitUp: true, eyes: 0, arms: 'down', badges: 1, shake: t >= te ? [4, 4, 4] : [0, 0, 0] }));
  say(t, tu - 0.1, 760, 200, t < te - 0.1 ? '"UNFORTUNATELY...\nWE\'RE LETTING YOU GO."' : '"UNFORTUNATELY...\nWE\'RE LETTING YOU GO.\nEFFECTIVE IMMEDIATELY."', 620, 380, 44, { red: t >= te });
};
S.d14 = (t, seg) => {
  // three cardboard boxes appear in their hands: a stapler and a sad little plant in each
  const ta = wt(seg, 'appear'), ts = wt(seg, 'stapler');
  if (t < ts - 0.3) { cam(t, seg.start, ts - seg.start, 1.05, 1.15, 1300, 560, () => night(t, { sitUp: true, eyes: 0, arms: 'down', badges: 1, boxes: prog(t, ta - 0.1, 0.4) })); return; }
  black();
  cam(t, ts - 0.3, segEnd(seg) - ts, 1.0, 1.1, 960, 560, () => {
    cardboardBox(960, 700, 2.2);
    if (t >= ts) { ctx.save(); ctx.globalAlpha *= prog(t, ts, 0.3); text('STAPLER', 600, 380, '900 40px M', C.fig); ln(620, 400, 760, 470, 3, '#8a8a8a'); ctx.restore(); }
    if (t >= wt(seg, 'sad')) { ctx.save(); ctx.globalAlpha *= prog(t, wt(seg, 'sad'), 0.3); text('SAD LITTLE PLANT', 1360, 300, '900 40px M', C.fig); ln(1300, 320, 1080, 400, 3, '#8a8a8a'); ctx.restore(); }
  });
};
S.d15 = (t, seg) => {
  // they walk out one by one; you never give them a reference
  const tw = wt(seg, 'walk'), tr = wt(seg, 'reference');
  cam(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.05, 1.0, 1100, 560, () => {
    const walk = [0, 1, 2].map(i => 420 * ease(prog(t, tw + i * 0.5, 1.6))), who = walk.map(w => w < 400);
    night(t, { sitUp: true, eyes: 0, arms: 'down', badges: 1, boxes: 1, walk, who, doorOpen: prog(t, tw - 0.3, 0.4) });
  });
  if (t >= tr) flatT(() => stampMark(t, tr, 1300, 260, [['NO REFERENCE', 70]], -0.1, '#000', 20));
};

// ---------- the next morning ----------
S.f1 = (t, seg) => {
  const te = wt(seg, 'email'), tw = wt(seg, 'we');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.05, 960, 520, () => {
    if (t < tw - 0.1) {
      pop(t, seg.start, 960, 250, () => { glow(); spaced('THE NEXT MORNING', 960, 270, '900 64px M', C.fig, 10); noGlow(); }, 0.35);
      if (t >= te - 0.1) pop(t, te - 0.1, 960, 560, () => { glow(); rr(560, 470, 800, 180, 24, '#f4f4f6'); noGlow(); icon7('mail', 680, 560, 0.6, '#111'); text('1 NEW EMAIL', 780, 580, '900 54px M', '#111', 'left'); ctx.save(); redGlow(14); circ(1320, 500, 18, C.red); ctx.restore(); }, 0.35);
      return;
    }
    ctx.translate(960, 480); ctx.scale(1.3, 1.3); ctx.translate(-960, -480);
    mailCard(460, 200, 1000, 560, { from: 'HR', subj: 'Changes in our team', body: [typed('We are sorry to hear about', t, tw, 30), typed('the recent changes in our team.', t, tw + 0.9, 30)] });
  });
};
S.f2 = (t, seg) => {
  const tw = wt(seg, 'we');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.05, 1.1, 960, 520, () => {
    ctx.translate(960, 480); ctx.scale(1.3, 1.3); ctx.translate(-960, -480);
    mailCard(460, 200, 1000, 560, { from: 'HR', subj: 'Changes in our team', body: ['We are sorry to hear about', 'the recent changes in our team.', '', typed('We have restructured our', t, tw, 30), typed('hiring process.', t, tw + 0.9, 30)] });
  });
};
// the peephole: a round fisheye view of the hallway with three new agents, one holding out his hand
function peephole(t, z, o = {}) {
  black();
  ctx.save(); ctx.beginPath(); ctx.arc(960, 520, 400, 0, Math.PI * 2); ctx.clip();
  ctx.fillStyle = '#0a0a0a'; ctx.fillRect(0, 0, W, H);
  ctx.translate(960, 520); ctx.scale(z, z); ctx.translate(-960, -520);
  ln(300, 860, 1620, 860, 3, '#3a3a3a'); ln(560, 120, 560, 860, 3, '#262626'); ln(1360, 120, 1360, 860, 3, '#262626');
  for (let i = 0; i < 3; i++) agent(KINDS[i], 760 + i * 200, 880, 0.62 + (i === 1 ? 0.06 : 0), { stand: 1, arms: i === 1 ? 'hand' : 'down', reach: 0.4, eyes: o.eyes && i === 1 ? o.eyes : 0, t });
  ctx.restore();
  const g = ctx.createRadialGradient(960, 520, 250, 960, 520, 400); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.85)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(960, 520, 401, 0, Math.PI * 2); ctx.fill();
  circS(960, 520, 404, C.fig, 8);
}
S.f3 = (t, seg) => {
  // the doorbell; through the peephole, three new interviewers; one is already holding out his hand
  const tp = wt(seg, 'peephole'), tb = wt(seg, 'doorbell');
  if (t < tp - 0.2) { black(); cam(t, seg.start, tp - seg.start, 1.0, 1.06, 960, 520, () => { rrS(760, 160, 400, 760, 6, C.fig, 6); circ(1110, 560, 12, C.fig); circS(960, 360, 22, C.fig, 5);
    if (t >= tb) for (let k = 0; k < 3; k++) { ctx.save(); ctx.globalAlpha *= 1 - prog(t, tb + k * 0.15, 0.8); circS(960, 360, 40 + 60 * prog(t, tb + k * 0.15, 0.8), C.fig, 4); ctx.restore(); }
    text('DING DONG', 960, 1000, '900 40px M', '#8a8a8a'); }); return; }
  peephole(t, lerp(1.0, 1.15, ease(prog(t, tp, 3))));
};
S.f4 = (t, seg) => {
  peephole(t, lerp(1.15, 1.5, ease(prog(t, seg.start, 2.0))), { eyes: prog(t, seg.start + 0.4, 0.5) });
  say(t, seg.start + 0.1, 1560, 230, 'WELCOME TO THE\nSECOND ROUND.', 1180, 380, 46, { red: true });
};
S.f5 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore();
  });
};
S.f6 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts, dk = ease(prog(t, ts + 0.5, 1.0));
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9] });
    if (dk > 0) { ctx.save(); ctx.globalAlpha = 0.5 * dk; ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
    if (t >= ts) { ctx.save(); redGlow(lerp(0, 40, dk)); stampMark(t, ts, 960, 540, [['FOLLOW', 96], ['THE RULES', 96]], -0.12, dk > 0.02 ? 'rgba(0,0,0,0)' : '#ececec', 12); ctx.restore(); }
    ctx.restore();
  });
};
// EP07 thumbnails, benchmark style: pure black, flat white figures, one red danger element, huge DON'T TELL THE TRUTH.
function thTitle(a, b, y, size, x = W / 2, align = 'center') {
  ctx.save(); ctx.font = `900 ${size}px M`; const wa = ctx.measureText(a).width, wb = ctx.measureText(b).width;
  const x0 = align === 'center' ? x - (wa + wb) / 2 : x;
  text(a, x0, y, `900 ${size}px M`, '#fff', 'left'); redGlow(26); text(b, x0 + wa, y, `900 ${size}px M`, C.red, 'left'); ctx.restore();
}
const thBg = () => { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); };
// 1: the three agents at the desk, big; the middle one's lenses red; the title over them
window.drawThumbA = () => {
  thBg();
  const g = ctx.createRadialGradient(960, 700, 60, 960, 760, 900); g.addColorStop(0, 'rgba(255,255,255,0.08)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(960, 1080); ctx.scale(1.45, 1.45); ctx.translate(-960, -880);
  agent('young', 560, 760, 1, { arms: 'desk' }); agent('hr', 960, 760, 1, { arms: 'desk', eyes: 1 }); agent('boss', 1360, 760, 1, { arms: 'desk' });
  meetDesk(200, 1720, 760, { items: false });
  ctx.restore();
  thTitle("DON'T TELL THE ", 'TRUTH', 170, 140);
};
// 2: just the middle one, huge, red lenses; the title on the left
window.drawThumbB = () => {
  thBg();
  ctx.save(); ctx.translate(1400, 1080); ctx.scale(2.5, 2.5); ctx.translate(-960, -760);
  agent('hr', 960, 760, 1, { arms: 'desk', eyes: 1, lean: 0.3 });
  ctx.restore();
  ctx.save(); text("DON'T", 90, 360, '900 170px M', '#fff', 'left'); text('TELL THE', 90, 550, '900 170px M', '#fff', 'left'); redGlow(28); text('TRUTH', 90, 740, '900 170px M', C.red, 'left'); ctx.restore();
};
// 3: the clipboard, LIVES ALONE underlined twice in red; the agent behind it
window.drawThumbC = () => {
  thBg();
  ctx.save(); ctx.translate(1420, 1080); ctx.scale(2.0, 2.0); ctx.translate(-960, -760); ctx.globalAlpha = 0.95;
  agent('hr', 960, 760, 1, { arms: 'desk', eyes: 1 }); ctx.restore();
  ctx.save(); ctx.translate(560, 660); ctx.rotate(-0.06); clipboard(0, 0, 3.4, 0, { lines: [['NO. 117', 0], ['AGE  29', 0], ['LIVES ALONE', 1]], under: 2, up: 1 });
  ctx.scale(3.4, 3.4); ctx.font = '900 15px M'; const w = ctx.measureText('LIVES ALONE').width; ln(-62, 40, -58 + w, 39, 3.5, '#d61f1f'); ctx.restore();
  thTitle("DON'T TELL THE ", 'TRUTH', 170, 130);
};
// v2 design sketches
window.drawDesign1 = () => {
  thBg(); meetRoom({ clock: [9, 0, 0] });
  agent('young', 560, 700, 1, { arms: 'desk' });
  agent('hr', 960, 700, 1, { arms: 'desk' });
  agent('boss', 1360, 700, 1, { arms: 'laptop', lid: 0 });
  meetDesk(260, 1660, 700);
};
window.drawDesign2 = () => {
  thBg(); meetRoom({ clock: [9, 0, 0] });
  for (const [k, x, o] of [['young', 330, {}], ['hr', 960, { eyes: 1 }], ['boss', 1590, {}]]) { ctx.save(); ctx.translate(x, 480); ctx.scale(2.4, 2.4); ppHead(k, o); ctx.restore(); }
};
window.drawDesign3 = () => {
  thBg(); meetRoom({ clockAt: false });
  agent('young', 560, 1000, 0.8, { stand: 1, arms: 'down' });
  agent('hr', 960, 1000, 0.8, { stand: 1, arms: 'hand', reach: 0.6, eyes: 1 });
  agent('boss', 1360, 1000, 0.8, { stand: 1, arms: 'down' });
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

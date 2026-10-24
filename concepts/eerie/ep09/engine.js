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
  const rows = [['SUBJECT', null], ['LOCATION', 'FRONT HALLWAY'], ['TIME', '6:40 PM']];
  rows.forEach(([l, v], i) => { const y = P.y + 270 + i * 82;
    text(l, P.x + 60, y, '600 28px Plex', '#666', 'left'); ln(P.x + 250, y + 12, P.x + P.w - 60, y + 12, 2, '#bbb');
    if (v === null) rr(P.x + 260, y - 30, 330, 40, 3, '#111');
    else { ctx.save(); ctx.filter = 'blur(9px)'; text(v, P.x + 262, y, '900 36px M', i === 2 ? '#d61f1f' : '#111', 'left'); ctx.restore(); } });   // classified: blurred
  // barcode and a hazard edge
  for (let i = 0; i < 40; i++) { const bw = hash(i * 1.7) < 0.35 ? 6 : 3; rr(P.x + P.w - 300 + i * 6.4, P.y + P.h - 170, bw, 70, 0, '#111'); }
  text('NO. 0' + NUM, P.x + P.w - 172, P.y + P.h - 74, '600 24px Plex', '#444');
  text('DO NOT SMILE BACK', P.x + 60, P.y + P.h - 130, '600 22px Plex', '#666', 'left');
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
  if (name === 'smile') { circS(0, -6, 46, col, 6); ctx.beginPath(); ctx.arc(0, -8, 28, 0.3, Math.PI - 0.3); ctx.lineWidth = 7; ctx.strokeStyle = col; ctx.stroke(); circ(-16, -20, 5, col); circ(16, -20, 5, col); }
  if (name === 'plate') { circS(-6, 0, 40, col, 6); circS(-6, 0, 22, col, 4); ln(50, -36, 50, 40, 6, col); for (let i = -1; i <= 1; i++) ln(50 + i * 9, -42, 50 + i * 9, -20, 4, col); }
  if (name === 'mirror') { rrS(-32, -50, 64, 100, 12, col, 7); ln(-14, -18, 6, -36, 4, col); ln(-14, 2, 16, -28, 4, col); }
  if (name === 'fist') { rr(-34, -34, 68, 64, 18, col); for (let i = 1; i < 4; i++) ln(-34 + i * 17, -34, -34 + i * 17, -10, 3, '#ff2b2b'); }
  ctx.restore();
}
const RULES = [['smile', 'DO NOT SMILE BACK', '', ['DO NOT SMILE BACK']], ['plate', 'DO NOT LET IT EAT FROM YOUR PLATE', '', ['DO NOT LET IT EAT', 'FROM YOUR PLATE']], ['mirror', 'NEVER LET IT LOOK IN THE MIRROR', '', ['NEVER LET IT LOOK', 'IN THE MIRROR']], ['warn', 'EMERGENCY PROTOCOL', 'HOW TO FIGHT BACK']];
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
// ---------- EP09: the dog, you, and the house ----------
// Channel identity: analog horror. PURE BLACK background, PURE WHITE flat figures with thin black detail lines. Red only for danger.
// The dog is a plain white retriever. You are faceless (a plain round head, no mouth). Only the dog has a mouth: its smile is the horror.
const DOG = { fig: '#f4f4f4', far: '#c4c4c4', ear: '#dcdcdc', line: '#000', tooth: '#fbfbf6' };
const FL = 860;   // the floor line in most rooms
const rotP = (px, py, cx, cy, a) => { const c = Math.cos(a), s = Math.sin(a); return [cx + (px - cx) * c - (py - cy) * s, cy + (px - cx) * s + (py - cy) * c]; };
const inv = (wx, wy, x, y, s, dir) => [(wx - x) / (s * dir), (wy - y) / s];
// a two-part limb (thigh/shin, upper arm/forearm) with a soft joint bent to side b
function limb2(a, c, w, col, b = 1, bend = 0.12) {
  const mx = (a[0] + c[0]) / 2, my = (a[1] + c[1]) / 2, dx = c[0] - a[0], dy = c[1] - a[1];
  poly([a, [mx - dy * bend * b, my + dx * bend * b], c], w, col);
}


// the dog in profile, facing right (o.dir -1: left). Paws on the floor at (x,y). About 400 long and 330 tall at s=1.
// o.rear 0..1: the front of the body rises around the hips (1 = up on its back legs, taller than you)
// o.sit 0..1: sitting; o.walk: gait phase; o.wag: tail phase; o.crouch 0..1: front low (growling)
// o.reach: [x,y] world point for the near front paw (o.reachK 0..1 blends it in); o.scratch 0..1: hind leg scratches behind the ear
function dog(x, y, s = 1, o = {}) {
  const dir = o.dir || 1, F = DOG.fig, FA = DOG.far, L = DOG.line;
  const rear = ease(o.rear || 0), sit = ease(o.sit || 0), cr = o.crouch || 0;
  const sw = o.walk != null ? Math.sin(o.walk) : 0, sw2 = o.walk != null ? Math.sin(o.walk + Math.PI) : 0;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * dir, s);
  const hip = [-100, -178 + 70 * sit + 10 * cr];
  const a = -rear * 1.36 - sit * 0.5 * (1 - rear) + cr * 0.16;   // body angle around the hip
  const R = (p) => rotP(p[0], p[1] + (hip[1] + 178), hip[0], hip[1], a);   // a body point (drawn at stand height) into place
  const shoulder = R([92, -170]), neck = R([128, -205]);
  let headC = R([180, -262 + 30 * cr]);
  if (rear > 0) headC = [headC[0] + 30 * rear, headC[1] + 10 * rear];
  // front paws: on the floor, or hanging in front of the chest when it stands up
  const floorP = (off) => [lerp(102 + off, 120, sit), -12];
  const hang = [shoulder[0] + 60, shoulder[1] + 110];
  let pn = [lerp(floorP(sw * 28)[0], hang[0], rear), lerp(-12, hang[1], rear)];
  let pf = [lerp(floorP(-14 + sw2 * 28)[0], hang[0] - 26, rear), lerp(-12, hang[1] + 8, rear)];
  if (o.reach) { const r = inv(o.reach[0], o.reach[1], x, y, s, dir), k = o.reachK ?? 1; pn = [lerp(pn[0], r[0], k), lerp(pn[1], r[1], k)]; }
  // hind legs: standing, folded under (sitting), or straight under the hips (up)
  const hindN = sit > 0.5 ? null : [lerp(-112 + sw2 * 26, -96, rear), -12], hindF = [lerp(-86 + sw * 26, -76, rear), -12];
  glow('rgba(255,255,255,0.22)', 16);
  // far legs
  limb2(hip, hindF, 28, FA, -1, 0.18); ell(hindF[0] + 10, -10, 20, 11, 0, FA);
  limb2(R([70, -165]), pf, 26, FA, 1, 0.06 + 0.1 * rear); ell(pf[0] + 10, pf[1] + 2, 19, 11, 0, FA);
  // tail
  const wag = o.wag != null ? Math.sin(o.wag) * 0.5 : 0, tb = R([-128, -192]);
  ctx.save(); ctx.translate(tb[0], tb[1]); ctx.rotate(-0.5 + wag - rear * 0.9 * (1 - sit) + sit * 1.4);
  pth('M0,-12 C-40,-22 -80,-34 -112,-40 C-118,-30 -110,-20 -100,-18 C-70,-10 -36,6 0,12 Z', F); ctx.restore();
  // body
  ctx.save(); ctx.translate(hip[0], hip[1]); ctx.rotate(a); ctx.translate(-hip[0], -hip[1]);
  ell(0, hip[1] - (-178) - 180, 142, 64, 0, F);
  ctx.restore();
  // near hind leg: a haunch when sitting
  if (sit > 0.5) { ell(hip[0] + 20, -64, 74, 62, -0.2, F); ell(-10, -12, 34, 13, 0, F); pthS(`M${hip[0] - 30},-40 C${hip[0]},-10 ${hip[0] + 60},-10 ${hip[0] + 80},-50`, 'rgba(0,0,0,0.35)', 3); }
  else if (o.scratch) { const sc = Math.sin((o.t || 0) * 30) * 0.5 + 0.5, ear = [headC[0] - 30, headC[1] + 10];
    limb2(hip, [lerp(hip[0] + 60, ear[0] - 20, 0.7), lerp(-80, ear[1] + 40 + sc * 26, 0.8)], 30, F, 1, 0.3); }
  else { limb2(hip, hindN, 30, F, -1, 0.18); ell(hindN[0] + 10, -10, 22, 12, 0, F); }
  // neck and chest
  poly([shoulder, neck, [headC[0] - 30, headC[1] + 20]], 70, F);
  // near front leg
  limb2(R([96, -160]), pn, 28, F, 1, 0.06 + 0.12 * rear); ell(pn[0] + 10, pn[1] + 2, 21, 12, 0, F);
  noGlow();
  // collar
  ctx.save(); ctx.translate(...[(neck[0] + headC[0]) / 2 - 18, (neck[1] + headC[1]) / 2 + 22]); ctx.rotate(0.9 - rear * 0.4); rr(-30, -6, 60, 12, 5, '#1a1a1a'); circ(0, 12, 7, o.tagRed ? C.red : '#9a9a9a'); ctx.restore();
  // head
  ctx.save(); ctx.translate(...headC); ctx.rotate((o.head || 0) - a * 0.1 + cr * 0.15); dogHead(o); ctx.restore();
  ctx.restore();
}


// you, faceless, in profile facing right (o.dir -1: left). Feet (or knees, hands) on the floor at (x,y). 360 tall standing at s=1.
// o.pose: 'stand' | 'sit' (chair seat at y-170) | 'fours' | 'curl' (asleep on your side) | 'back' (pinned on your back) | 'kneel'
// o.hand: [x,y] world target for the near hand; o.walk: gait phase; o.red: a red halo (danger); o.head: tilt
function you(x, y, s = 1, o = {}) {
  const dir = o.dir || 1, col = o.col || C.fig, far = '#b8b8b8', P = o.pose || 'stand';
  ctx.save(); ctx.translate(x, y); ctx.scale(s * dir, s);
  const H = o.hand ? inv(o.hand[0], o.hand[1], x, y, s, dir) : null;
  const arm = (sh, hd, c, w = 20) => { limb2(sh, hd, w, c, 1, 0.1); circ(hd[0], hd[1], w * 0.6, c); };
  const head = (hx, hy, r = 36) => { if (o.red) { ctx.save(); redGlow(30 * o.red); circ(hx, hy, r, col); ctx.restore(); circS(hx, hy, r + 3, C.red, 4 * o.red); } else circ(hx, hy, r, col); };
  glow('rgba(255,255,255,0.25)', 14);
  if (P === 'stand') {
    const sw = o.walk != null ? Math.sin(o.walk) : 0;
    arm([0, -282], [10 - sw * 26, -160], far); ln(-2, -172, -6 + sw * 22, -10, 26, far); rr(-8 + sw * 22 - 6, -18, 34, 16, 6, far);
    ln(2, -172, 6 - sw * 22, -10, 26, col); rr(6 - sw * 22 - 6, -18, 36, 16, 6, col);
    rr(-30, -302, 60, 150, 24, col); head(4, -344);
    arm([0, -282], H || [14 + sw * 26, -160], col);
  } else if (P === 'sit') {
    arm([4, -282], [80, -210], far); poly([[-6, -184], [92, -180], [98, -14]], 28, far);
    poly([[6, -180], [100, -176], [106, -14]], 30, col); rr(96, -20, 40, 16, 6, col);
    rr(-34, -306, 64, 136, 24, col); head(2, -348);
    arm([4, -282], H || [90, -214], col);
  } else if (P === 'fours') {
    const sh = [72, -196], hp = [-112, -184];
    arm(sh, [58, -8], far, 22); limb2(hp, [-90, -18], 30, far, -1, 0.05); ln(-90, -16, -196, -12, 24, far);
    poly([hp, sh], 66, col); limb2([hp[0] + 10, hp[1]], [-104, -18], 32, col, -1, 0.05); ln(-104, -16, -214, -12, 26, col);
    head(140 + (o.lunge || 0) * 20, -214 + (o.head || 0));
    arm([sh[0] + 6, sh[1]], H || [96, -8], col, 22);
  } else if (P === 'curl') {
    poly([[-96, -44], [20, -18], [-60, -12]], 28, far);
    ell(-6, -54, 112, 44, 0.04, col); head(126, -70, 34); poly([[-90, -48], [30, -26], [-40, -14]], 30, col);
    arm([70, -78], [140, -24], col, 20);
  } else if (P === 'back') {
    ln(40, -44, 210, -24, 28, far); ln(40, -40, 200, -14, 30, col);
    poly([[-150, -46], [40, -44]], 66, col); head(-204, -50);
    arm([-110, -60], H || [-60, -150], col, 20);
  } else if (P === 'kneel') {
    ln(-40, -14, -150, -12, 26, far); ln(-30, -14, -140, -12, 28, col);
    poly([[-36, -18], [-24, -156]], 32, col);
    rr(-48, -300, 64, 150, 24, col); head(-12, -342);
    arm([-14, -280], H || [70, -190], col);
  }
  noGlow(); ctx.restore();
}
// a red outline of a person, curled up inside the dog's body (what moved in)
function insideMe(x, y, s, a = 1, dir = 1) {
  if (a <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * dir, s); ctx.globalAlpha *= a; redGlow(16); ctx.strokeStyle = C.red; ctx.lineWidth = 6; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(70, -30, 26, 0, Math.PI * 2); ctx.stroke();
  ctx.stroke(new Path2D('M44,-24 C10,-40 -50,-40 -80,-10 C-96,8 -80,30 -50,26 L-10,22 C10,20 20,30 30,40 M-30,22 C-10,36 30,30 50,8'));
  noGlow(); ctx.restore();
}

// ---------- rooms and props (white outlines on black) ----------
function floorLine(y = FL, col = '#262626') { ln(-200, y, W + 200, y, 3, col); }
function hallDoor(x, open = 0, o = {}) {   // the front door: outline, opens to a light doorway
  const w = 220, h = 470, y = FL - h;
  if (open > 0) { ctx.save(); glow('rgba(255,255,255,0.6)', 30); rr(x, y, w * open, h, 2, '#e9e9e9'); ctx.restore(); }
  rrS(x, y, w, h, 4, C.fig, 5);
  ctx.save(); ctx.translate(x, 0); ctx.scale(1 - open * 0.85, 1); rr(4, y + 4, w - 8, h - 8, 2, '#000'); rrS(4, y + 4, w - 8, h - 8, 2, '#9a9a9a', 3); circ(w - 30, y + 250, 8, C.fig); ctx.restore();
}
function mirrorFrame(x, y, w, h, o = {}) {   // a tall wall mirror: white frame, black glass; o.inner(fn) draws the reflection clipped inside
  glow('rgba(255,255,255,0.3)', 20); rrS(x, y, w, h, 14, C.fig, 14); noGlow();
  rr(x + 7, y + 7, w - 14, h - 14, 8, '#050505');
  if (o.inner) { ctx.save(); ctx.beginPath(); ctx.roundRect(x + 7, y + 7, w - 14, h - 14, 8); ctx.clip(); o.inner(); ctx.restore(); }
  ctx.save(); ctx.globalAlpha *= 0.12; ln(x + 40, y + 60, x + 110, y + 10, 8, '#fff'); ln(x + 40, y + 120, x + 170, y + 10, 4, '#fff'); ctx.restore();
}
function table(x0, x1, y = 600, o = {}) {   // dining table, side view: top slab on two legs
  glow('rgba(255,255,255,0.3)', 18); rr(x0, y, x1 - x0, 20, 4, C.fig); noGlow();
  for (const lx of [x0 + 40, x1 - 54]) rr(lx, y + 20, 14, FL - y - 20, 2, '#d0d0d0');
}
function chair(x, s = 1, dir = 1, o = {}) {   // side view chair, seat at FL-170; the back on the far side from dir
  ctx.save(); ctx.translate(x, FL); ctx.scale(s * dir, s);
  const c = o.col || '#8c8c8c';
  rr(-70, -176, 140, 14, 4, c); rr(-74, -420, 14, 258, 5, c); ln(-62, -162, -66, 0, 9, c); ln(60, -162, 64, 0, 9, c);
  ctx.restore();
}
function plate(x, y, s = 1, o = {}) {   // a plate seen from the side, food optional; o.fork
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ell(0, -6, 80, 12, 0, C.fig); ell(0, -10, 56, 6, 0, '#cfcfcf');
  if (o.food) { pth('M-34,-12 C-30,-36 30,-36 34,-12 Z', '#bdbdbd'); }
  if (o.fork) { ln(100, -4, 170, -4, 6, C.fig); for (let i = 0; i < 3; i++) ln(170, -8 + i * 4, 196, -8 + i * 4, 3, C.fig); }
  ctx.restore();
}
function bowl(x, s = 1, o = {}) {   // the dog's bowl on the floor; o.full
  ctx.save(); ctx.translate(x, FL); ctx.scale(s, s);
  if (o.full) pth('M-64,-48 C-56,-82 56,-82 64,-48 Z', '#cfcfcf');
  glow('rgba(255,255,255,0.3)', 14); pth('M-84,-50 L84,-50 L66,-2 L-66,-2 Z', C.fig); noGlow(); ln(-84, -50, 84, -50, 4, '#000');
  if (o.label) text(o.label, 0, -16, '900 26px M', '#000');
  ctx.restore();
}
function dogBed(x, s = 1) { ctx.save(); ctx.translate(x, FL); ctx.scale(s, s); glow('rgba(255,255,255,0.25)', 14); ell(0, -30, 230, 40, 0, C.fig); noGlow(); ell(0, -40, 196, 24, 0, '#0c0c0c'); ctx.restore(); }
// a fork held in a hand (close-up), at (x,y) pointing right
function forkHand(x, y, s = 1, rot = 0, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  glow('rgba(255,255,255,0.3)', 14); poly([[-420, 60], [-120, 10]], 90, C.fig); noGlow();
  rr(-130, -40, 90, 90, 36, C.fig); ln(-40, 0, 160, 0, 12, C.fig); for (let i = 0; i < 4; i++) ln(160, -21 + i * 14, 230, -21 + i * 14, 7, C.fig);
  if (o.food) ell(210, 0, 34, 24, 0, '#bdbdbd');
  ctx.restore();
}
// dental chart: a row of flat human teeth seen front on, centred at (x,y); o.fangAt: index of the one long sharp tooth; o.label
function teethRow(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const n = 10, w = 76;
  glow('rgba(255,43,43,0.4)', 14); rr(-n * w / 2 - 30, -70, n * w + 60, 54, 26, C.red); noGlow();
  for (let i = 0; i < n; i++) {
    const tx = -n * w / 2 + i * w + 4, c = 1 - Math.abs(i - 4.5) / 6, h = 70 + 50 * c;
    if (o.fangAt === i) { ctx.save(); const k = o.fang ?? 1; redGlow(24 * k); ctx.beginPath(); ctx.moveTo(tx, -30); ctx.lineTo(tx + w - 8, -30); ctx.lineTo(tx + (w - 8) / 2 + 6, -30 + lerp(h, 220, k)); ctx.closePath(); ctx.fillStyle = DOG.tooth; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = '#000'; ctx.stroke(); ctx.restore(); }
    else { rr(tx, -30, w - 8, h, [3, 3, 18, 18], DOG.tooth); rrS(tx, -30, w - 8, h, [3, 3, 18, 18], '#000', 3); }
  }
  ctx.restore();
}
function nightstand(x, s = 1) { ctx.save(); ctx.translate(x, FL); ctx.scale(s, s); rr(-110, -200, 220, 200, 6, '#141414'); rrS(-110, -200, 220, 200, 6, '#4a4a4a', 3); ln(-100, -110, 100, -110, 3, '#4a4a4a'); circ(0, -150, 7, '#6a6a6a'); ctx.restore(); }
// the collar lying flat with its tag; o.red 0..1 (the name on the tag)
function collar(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.beginPath(); ctx.ellipse(0, 0, 220, 70, 0, 0, Math.PI * 2); ctx.lineWidth = 34; ctx.strokeStyle = '#222'; ctx.stroke(); ctx.lineWidth = 3; ctx.strokeStyle = '#7a7a7a'; ctx.stroke();
  rr(-30, 52, 60, 36, 6, '#9a9a9a'); rr(-14, 60, 28, 20, 3, '#222');
  ln(0, 86, 0, 120, 6, '#9a9a9a');
  const red = o.red || 0; ctx.save(); if (red > 0) redGlow(30 * red); circ(0, 200, 88, red > 0.5 ? C.red : C.fig); ctx.restore();
  circS(0, 200, 74, red > 0.5 ? '#fff' : '#000', 3); circ(0, 126, 10, '#000');
  text(o.name || 'YOU', 0, 222, '900 64px M', red > 0.5 ? '#fff' : '#000');
  ctx.restore();
}
// swap arrows: two curved arrows trading places between a and b
function swapArrows(ax, bx, y, p = 1, col = C.red, r = 120) {
  if (p <= 0) return;
  const mx = (ax + bx) / 2, rx = Math.abs(bx - ax) / 2;
  ctx.save(); redGlow(14);
  for (const d of [-1, 1]) {
    const a0 = d < 0 ? Math.PI : 0, a1 = a0 + d * Math.PI * clamp(p);
    ctx.beginPath(); ctx.ellipse(mx, y, rx, r, 0, d < 0 ? Math.PI * 1.08 : 0.08, d < 0 ? Math.PI * 1.08 + Math.PI * 0.84 * clamp(p) : 0.08 + Math.PI * 0.84 * clamp(p));
    ctx.lineWidth = 12; ctx.strokeStyle = col; ctx.stroke();
    if (p > 0.95) { const a = d < 0 ? Math.PI * 1.92 : Math.PI * 0.92, ex = mx + Math.cos(a) * rx, ey = y + Math.sin(a) * r, ang = a + Math.PI / 2;
      ctx.save(); ctx.translate(ex, ey); ctx.rotate(ang); pth('M0,-26 L34,0 L0,26 Z', col); ctx.restore(); }
  }
  ctx.restore();
}
// sound arcs coming off a head at (x,y) toward dir; col; n rings, a breathing pulse
function growlArcs(x, y, t, dir = 1, col = C.fig, size = 1, a = 1) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; if (col === C.red) redGlow(16);
  for (let k = 0; k < 3; k++) { const r = (50 + k * 36 + ((t * 90) % 36)) * size; ctx.beginPath(); ctx.arc(x, y, r, dir > 0 ? -0.6 : Math.PI - 0.6, dir > 0 ? 0.6 : Math.PI + 0.6); ctx.strokeStyle = col; ctx.lineWidth = 7 * size; ctx.stroke(); }
  noGlow(); ctx.restore();
}
// a progress bar with a label; v 0..1
function meter(x, y, w, label, v, col = C.red) {
  text(label, x, y - 18, '900 36px M', C.fig, 'left');
  rrS(x, y, w, 44, 8, '#5a5a5a', 4); ctx.save(); if (col === C.red) redGlow(18); rr(x + 6, y + 6, (w - 12) * clamp(v), 32, 5, col); ctx.restore();
  text(Math.round(v * 100) + '%', x + w + 24, y + 36, '900 40px M', col, 'left');
}
// an old phone handset (the vet call)
function phoneIcon(x, y, s = 1, col = C.fig) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  pth('M-110,-30 C-110,-70 -60,-80 -40,-60 L-20,-30 C-14,-20 -20,-8 -34,-4 L-50,0 C-40,40 -10,70 30,84 L40,66 C46,54 60,50 70,58 L100,80 C120,96 110,140 70,140 C-20,140 -110,60 -110,-30 Z', col); noGlow(); ctx.restore(); }
function bellButton(x, y, s = 1, ring = 0) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); rr(-40, -60, 80, 120, 14, '#1a1a1a'); rrS(-40, -60, 80, 120, 14, C.fig, 4); ctx.save(); if (ring > 0) redGlow(30 * ring); circ(0, 0, 22, ring > 0 ? C.red : C.fig); ctx.restore(); ctx.restore(); }
// ---------- EP09 v2: the human teeth, in detail ----------
// The dog's face front on and in profile, with a full set of real-looking human teeth: shaped incisors, canines, premolars and molars
// foreshortened around the arch, scalloped red gums, black dog lips pulled back into a grin that reaches the cheeks, eyes that do NOT smile (wide, staring),
// stretched cheek folds and a string of saliva. Flat vector tones only (no gradients): enamel, a shade tone on the far side, a cervical tone, a highlight.
const TC = { enamel: '#efe9d9', shade: '#cbc2ad', neck: '#d6c59a', edge: '#dfe1e2', hi: '#ffffff', line: '#231c1a', gum: '#b5101f', gumHi: '#ff4d5e', gumDk: '#5c0610', mouth: '#060101', tongue: '#3e060b' };
const thash = n => { const x = Math.sin(n * 91.7 + 13.1) * 43758.5453; return x - Math.floor(x); };
const TOOTH_ORDER = [0, 9, 1, 8, 2, 7, 3, 6, 4, 5];   // the order the front teeth fall out (d14)
// one tooth. (x, y0) = centre of the gum end; h > 0 grows down (upper row), h < 0 grows up (lower row). kind: inc | can | pm | mol. side: -1/1 which way the arch turns away (shade side)
function toothShape(x, y0, w, h, kind) {
  const d = Math.sign(h), a = Math.abs(h), p = new Path2D(), nw = w * 0.84;
  const Y = v => y0 + d * v;
  p.moveTo(x - nw / 2, Y(0));
  if (kind === 'can') {   // a long cusp to a rounded point
    p.bezierCurveTo(x - w / 2, Y(a * 0.45), x - w / 2, Y(a * 0.7), x - w * 0.18, Y(a * 0.94)); p.quadraticCurveTo(x, Y(a * 1.04), x + w * 0.18, Y(a * 0.94));
    p.bezierCurveTo(x + w / 2, Y(a * 0.7), x + w / 2, Y(a * 0.45), x + nw / 2, Y(0));
  } else if (kind === 'pm' || kind === 'mol') {   // rounded cusps
    p.bezierCurveTo(x - w / 2, Y(a * 0.5), x - w / 2, Y(a * 0.86), x - w * 0.24, Y(a * 0.98)); p.quadraticCurveTo(x, Y(a * 0.9), x + w * 0.24, Y(a * 0.98));
    p.bezierCurveTo(x + w / 2, Y(a * 0.86), x + w / 2, Y(a * 0.5), x + nw / 2, Y(0));
  } else {   // incisor: widens a little toward a straight biting edge with soft corners
    p.bezierCurveTo(x - w * 0.5, Y(a * 0.4), x - w * 0.52, Y(a * 0.8), x - w * 0.48, Y(a * 0.93)); p.quadraticCurveTo(x - w * 0.46, Y(a), x - w * 0.34, Y(a));
    p.lineTo(x + w * 0.34, Y(a)); p.quadraticCurveTo(x + w * 0.46, Y(a), x + w * 0.48, Y(a * 0.93)); p.bezierCurveTo(x + w * 0.52, Y(a * 0.8), x + w * 0.5, Y(a * 0.4), x + nw / 2, Y(0));
  }
  p.closePath(); return p;
}
function drawTooth(x, y0, w, h, kind, side, o = {}) {
  if (w < 1.2) return;
  const p = toothShape(x, y0, w, h, kind), d = Math.sign(h), a = Math.abs(h);
  ctx.fillStyle = TC.enamel; ctx.fill(p);
  ctx.save(); ctx.clip(p);
  ctx.fillStyle = TC.neck; ctx.fillRect(x - w, d > 0 ? y0 - 1 : y0 - a * 0.2, w * 2, a * 0.2 + 1);   // a yellowed band next to the gum
  ctx.fillStyle = TC.shade; ctx.fillRect(side > 0 ? x + w * 0.18 : x - w, Math.min(y0, y0 + h) - 2, w * 0.82, a + 4);   // the far side turns away into shadow
  if (kind === 'inc') { ctx.fillStyle = TC.edge; ctx.fillRect(x - w, y0 + d * a * 0.88 - (d < 0 ? a * 0.12 : 0), w * 2, a * 0.12); }   // a translucent biting edge
  if (w > 9) { ctx.fillStyle = TC.hi; ctx.beginPath(); ctx.roundRect(x - side * w * 0.22 - w * 0.07, Math.min(y0 + d * a * 0.22, y0 + d * a * 0.66), w * 0.14, a * 0.44, w * 0.07); ctx.fill(); }
  ctx.restore();
  ctx.lineWidth = o.lw || 1.8; ctx.strokeStyle = TC.line; ctx.lineJoin = 'round'; ctx.stroke(p);
}
// a dog's tooth (after the human ones are gone): sharp, curved; long for the canines
function dogTooth(x, y0, w, len, side) {
  const d = Math.sign(len), a = Math.abs(len); if (a < 1) return;
  const p = new Path2D(); p.moveTo(x - w / 2, y0); p.quadraticCurveTo(x - w * 0.4, y0 + d * a * 0.6, x + side * w * 0.15, y0 + d * a); p.quadraticCurveTo(x + w * 0.45, y0 + d * a * 0.5, x + w / 2, y0); p.closePath();
  ctx.fillStyle = TC.enamel; ctx.fill(p); ctx.save(); ctx.clip(p); ctx.fillStyle = TC.shade; ctx.fillRect(side > 0 ? x : x - w, y0 - a, w / 2, a * 2); ctx.restore();
  ctx.lineWidth = 1.8; ctx.strokeStyle = TC.line; ctx.stroke(p);
}

// ---- the front view arch ----
const UPPER = [[30, 56, 'inc'], [25, 48, 'inc'], [27, 60, 'can'], [23, 43, 'pm'], [22, 40, 'pm'], [28, 36, 'mol'], [24, 31, 'mol']];
const LOWER = [[21, 34, 'inc'], [21, 33, 'inc'], [25, 42, 'can'], [23, 31, 'pm'], [23, 29, 'pm'], [28, 26, 'mol']];
// where every tooth sits around an arch of radius R: [{x, w, p (perspective 1 front .. 0.6 back), j, side}]
function archSlots(list, R) {
  const out = []; let cum = 0;
  list.forEach(([aw, ah, kind], j) => { const t0 = cum / R, t1 = (cum + aw) / R; cum += aw;
    for (const side of [-1, 1]) { const x0 = R * Math.sin(Math.min(t0, 1.56)), x1 = R * Math.sin(Math.min(t1, 1.56));
      out.push({ x: side * (x0 + x1) / 2, w: x1 - x0, p: 1 - 0.36 * clamp(((t0 + t1) / 2) / 1.5), h: ah, kind, j, side }); } });
  return out;
}
// the mouth geometry for smile k (front view): upper lip line yU(x), lower lip line yL(x), corners at ±cw
function mouthGeo(k) {
  const cw = 112 + 26 * k, cy = 80 - 22 * k, top = 102, bot = 104 + 112 * k;
  return { cw, cy, top, bot, yU: x => lerp(top, cy, Math.min(1, (x / cw) ** 2)), yL: x => lerp(bot, cy, Math.min(1, Math.abs(x / cw) ** 1.7)) };
}
// the teeth that fall out first: the outside ones (index into the full list of slots, upper then lower)
function lostSet(n, total) { const order = []; for (let j = 6; j >= 0; j--) order.push(['u', j]); for (let j = 5; j >= 0; j--) order.push(['l', j]);
  const m = Math.round(n / 10 * total), s = new Set(); let c = 0; for (const [r, j] of order) { if (c >= m) break; s.add(r + j + 'L'); c++; if (c < m) { s.add(r + j + 'R'); c++; } } return s; }
function mouthFront(k, o = {}) {
  const G = mouthGeo(k), { cw, cy, yU, yL } = G, Ru = 118, Rl = 102;
  const lost = lostSet(o.lost || 0, 26), fang = o.fang || 0;
  const key = (r, s) => r + s.j + (s.side < 0 ? 'L' : 'R');
  const mouthPath = () => { const p = new Path2D(); p.moveTo(-cw, cy); for (let x = -cw; x <= cw; x += 4) p.lineTo(x, yU(x)); for (let x = cw; x >= -cw; x -= 4) p.lineTo(x, yL(x)); p.closePath(); return p; };
  const mp = mouthPath();
  ctx.fillStyle = TC.mouth; ctx.fill(mp);
  ctx.save(); ctx.clip(mp);
  // tongue deep in the mouth
  ell(0, yL(0) - 22, 84, 40 * k + 6, 0, TC.tongue); pthS(`M-30,${yL(0) - 40} q30,10 60,0`, '#1c0204', 3);
  // lower teeth, back to front, then the lower gum (scalloped up between the teeth)
  const lo = archSlots(LOWER, Rl).sort((a, b) => a.p - b.p);
  for (const s of lo) { const yb = yL(s.x) - 12 * s.p, hh = -s.h * s.p * clamp(k * 1.4) * (0.92 + 0.16 * thash(s.j * 13 - s.side));
    if (lost.has(key('l', s))) { if (fang > 0) dogTooth(s.x, yb, s.w * 0.9, -(s.kind === 'can' ? 54 : 22) * fang * s.p, s.side); else circ(s.x, yb - 3, s.w * 0.25, TC.gumDk); continue; }
    ctx.save(); ctx.translate(s.x, yb); ctx.rotate((thash(s.j * 7 + s.side) - 0.5) * 0.07); drawTooth(0, 0, s.w, hh, s.kind, s.side); ctx.restore(); }
  { const g = new Path2D(); g.moveTo(-cw, cy + 2); const sl = archSlots(LOWER, Rl).sort((a, b) => a.x - b.x);
    for (const s of sl) { const l = s.x - s.w / 2, r = s.x + s.w / 2; g.lineTo(l, yL(l) - 16 * s.p); g.quadraticCurveTo(s.x, yL(s.x) - 4, r, yL(r) - 16 * s.p); }
    g.lineTo(cw, cy + 2); for (let x = cw; x >= -cw; x -= 6) g.lineTo(x, yL(x) + 4); g.closePath(); ctx.fillStyle = TC.gum; ctx.fill(g); }
  // upper teeth, back to front, then the upper gum scalloped down between them
  const up = archSlots(UPPER, Ru).sort((a, b) => a.p - b.p);
  for (const s of up) { const yt = yU(s.x) + 10 * s.p, hh = s.h * s.p * (0.55 + 0.45 * k) * (0.93 + 0.14 * thash(s.j * 11 + s.side));
    if (lost.has(key('u', s))) { if (fang > 0) dogTooth(s.x, yt, s.w * 0.9, (s.kind === 'can' ? 74 : 28) * fang * s.p, s.side); else circ(s.x, yt + 3, s.w * 0.25, TC.gumDk); continue; }
    ctx.save(); ctx.translate(s.x, yt + (thash(s.j * 3 + s.side) - 0.5) * 3); ctx.rotate((thash(s.j * 5 + s.side * 2) - 0.5) * 0.06); drawTooth(0, 0, s.w, hh, s.kind, s.side); ctx.restore(); }
  { const g = new Path2D(); for (let x = -cw; x <= cw; x += 6) g.lineTo(x, yU(x) - 4); const sl = archSlots(UPPER, Ru).sort((a, b) => b.x - a.x);
    for (const s of sl) { const r = s.x + s.w / 2, l = s.x - s.w / 2; g.lineTo(r, yU(r) + 20 * s.p); g.quadraticCurveTo(s.x, yU(s.x) + 6, l, yU(l) + 20 * s.p); }
    g.closePath(); ctx.fillStyle = TC.gum; ctx.fill(g);
    ctx.save(); ctx.globalAlpha *= 0.85; ctx.beginPath(); for (const s of sl) { const r = s.x + s.w / 2, l = s.x - s.w / 2; ctx.moveTo(r, yU(r) + 18 * s.p); ctx.quadraticCurveTo(s.x, yU(s.x) + 4, l, yU(l) + 18 * s.p); }
    ctx.lineWidth = 2; ctx.strokeStyle = TC.gumHi; ctx.stroke(); ctx.restore();
    ctx.beginPath(); for (let x = -cw; x <= cw; x += 6) ctx.lineTo(x, yU(x) + 1); ctx.lineWidth = 6; ctx.strokeStyle = TC.gumDk; ctx.stroke(); }
  // saliva: a thin string from an upper canine down to the lower lip
  if (k > 0.6) { const sx = 72, a = (k - 0.6) / 0.4, y1 = yU(sx) + 60, y2 = yL(sx - 8) - 10; ctx.save(); ctx.globalAlpha *= 0.75 * a;
    ctx.beginPath(); ctx.moveTo(sx, y1); ctx.quadraticCurveTo(sx - 6, (y1 + y2) / 2 + 26, sx - 8, y2); ctx.lineWidth = 2.2; ctx.strokeStyle = '#e8e8e8'; ctx.stroke();
    ell(sx - 5, (y1 + y2) / 2 + 13, 3, 4.5, 0, '#f2f2f2'); ctx.restore(); }
  ctx.restore();
  // black dog lips around it: thick at the middle, tapering to tight curled corners
  for (const [f, w] of [[yU, 9], [yL, 8]]) { ctx.beginPath(); for (let x = -cw; x <= cw; x += 4) ctx.lineTo(x, f(x)); ctx.lineWidth = w; ctx.strokeStyle = '#000'; ctx.lineCap = 'round'; ctx.stroke(); }
  for (const d of [-1, 1]) { pth(`M${d * (cw - 4)},${cy - 6} q${d * 16},4 ${d * 12},20 q${d * -8},-4 ${d * -18},-8 Z`, '#000'); }
  // the cheeks bunch up into folds above the corners
  if (k > 0.25) { ctx.save(); ctx.globalAlpha *= clamp((k - 0.25) / 0.4);
    for (const d of [-1, 1]) { pthS(`M${d * (cw - 2)},${cy - 14} q${d * 26},-16 ${d * 22},-50`, '#000', 3.5); pthS(`M${d * (cw - 30)},${cy - 30} q${d * 18},-10 ${d * 14},-34`, '#000', 3); }
    ctx.restore(); }
}
// where tooth i (0..9 across the front) sits at full smile, for teeth that fall: local face coords
function toothPos(i, row = 0) { const G = mouthGeo(1), x = lerp(-100, 100, (i + 0.5) / 10); return [x, row ? G.yL(x) - 32 : G.yU(x) + 38]; }
function looseTooth(x, y, s = 1, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); glow('rgba(255,255,255,0.35)', 8); ctx.fillStyle = TC.enamel; const p = toothShape(0, -22, 26, 40, 'inc'); ctx.fill(p); noGlow();
  ctx.save(); ctx.clip(p); ctx.fillStyle = TC.gumDk; ctx.fillRect(-20, -26, 40, 6); ctx.fillStyle = TC.shade; ctx.fillRect(4, -30, 20, 60); ctx.restore(); ctx.lineWidth = 2; ctx.strokeStyle = TC.line; ctx.stroke(p); ctx.restore(); }

// the dog's face, front on: centre (x,y), about 460 wide at s=1.
// o.smile 0..1: the lips pull back over a full set of human teeth; o.eye red 0..1; o.lost 0..10; o.fang 0..1; o.snarl 0..1
function dogFace(x, y, s = 1, o = {}) {
  const F = DOG.fig, L = DOG.line, k = o.smile ?? 0;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(o.tilt || 0);
  for (const d of [-1, 1]) { const p = `M${d * 118},-160 C${d * 236},-160 ${d * 268},-24 ${d * 248},90 C${d * 236},152 ${d * 176},164 ${d * 154},114 C${d * 132},40 ${d * 118},-60 ${d * 118},-160 Z`;
    glow('rgba(255,255,255,0.2)', 18); pth(p, DOG.ear); noGlow(); pthS(p, L, 4);
    ctx.save(); ctx.globalAlpha *= 0.35; pthS(`M${d * 150},-120 C${d * 210},-100 ${d * 226},10 ${d * 200},100`, L, 2.5); ctx.restore(); }
  // the head; with the grin the cheeks widen a little
  const cwk = 1 + 0.05 * k;
  const head = `M-172,-64 C-172,-196 -92,-236 0,-236 C92,-236 172,-196 172,-64 C172,18 ${146 * cwk},66 ${126 * cwk},98 C${106 * cwk},196 54,242 0,242 C-54,242 ${-106 * cwk},196 ${-126 * cwk},98 C${-146 * cwk},66 -172,18 -172,-64 Z`;
  glow('rgba(255,255,255,0.32)', 34); pth(head, F); noGlow(); pthS(head, L, 4);
  if (k < 0.03) pthS('M-112,62 C-100,22 -50,12 0,16 C50,12 100,22 112,62', 'rgba(0,0,0,0.45)', 3);
  // fur tufts at the cheeks
  ctx.save(); ctx.globalAlpha *= 0.4; for (const d of [-1, 1]) for (let i = 0; i < 3; i++) pthS(`M${d * (150 - i * 8)},${-10 + i * 26} l${d * 14},6`, L, 2.5); ctx.restore();
  const er = o.eye || 0;
  for (const d of [-1, 1]) {
    const ex = d * 80, ey = -52;
    if (er > 0) { ctx.save(); redGlow(30 * er); ell(ex, ey, 23, 25, 0, C.red); ctx.restore(); circ(ex, ey, 6, '#2a0000'); }
    else { ell(ex, ey, 23 + 4 * k, 25 + 4 * k, 0, L); circ(ex + 7, ey - 9, 6.5 - 3.5 * k, '#fff'); if (k < 0.3) circ(ex - 6, ey + 8, 2.5, '#fff'); }
    // the eyes do not smile: wide, glassy, fixed on you; the brows pull down and in
    if (k > 0.05 && !er) { const q = clamp(k * 1.3); ctx.save(); ctx.globalAlpha *= q; pthS(`M${ex - 30},${ey + 34} q${30},${10} 60,0`, 'rgba(0,0,0,0.5)', 2.5); ctx.restore(); }
    pthS(`M${d * (44 + 6 * k)},${-96 + 12 * k} q${d * 30},${-16 + 4 * k} ${d * 60},${-6 * k}`, L, 4);
  }
  const sn = Math.max(o.snarl || 0, k * 0.8);
  if (sn > 0) { ctx.save(); ctx.globalAlpha *= sn; for (let i = 0; i < 3; i++) pthS(`M-26,${-4 - i * 12} q26,-8 52,0`, L, 3); ctx.restore(); }
  pth('M-48,30 C-48,4 48,4 48,30 C48,58 14,72 0,72 C-14,72 -48,58 -48,30 Z', L); ell(-14, 22, 11, 6, 0, '#5a5a5a'); ell(-18, 52, 9, 5, 0.4, '#1d1d1d'); ell(18, 52, 9, 5, -0.4, '#1d1d1d');
  if (k < 0.03) { ln(0, 72, 0, 98, 4, L); pthS('M-74,112 C-42,130 -14,120 0,98 C14,120 42,130 74,112', L, 4); }
  else { ln(0, 72, 0, mouthGeo(k).top - 2, 4, L); mouthFront(k, o); }
  ctx.restore();
}

// ---- the profile ----
// a dog's head in profile, centre (0,0), facing right. o.smile 0..1, o.eye red 0..1, o.close
const SIDE_UP = [[7, 14, 'inc'], [7, 13, 'inc'], [10, 18, 'can'], [10, 12, 'pm'], [10, 11, 'pm'], [12, 11, 'mol'], [11, 9, 'mol']];
const SIDE_LO = [[6, 11, 'inc'], [6, 11, 'inc'], [8, 14, 'can'], [9, 10, 'pm'], [9, 9, 'pm'], [11, 8, 'mol']];
function dogHead(o = {}) {
  const F = DOG.fig, L = DOG.line, k = o.smile || 0;
  const jaw = 10 * k;
  const head = `M-46,22 C-58,-20 -34,-56 6,-56 C34,-56 52,-44 60,-28 C70,-22 90,-16 106,-8 C116,-3 118,12 110,20 L106,28 C104,${44 + jaw} 92,${58 + jaw} 66,${62 + jaw} C40,${66 + jaw} 14,62 -6,70 C-30,66 -42,46 -46,22 Z`;
  glow('rgba(255,255,255,0.32)', 22); pth(head, F); noGlow(); pthS(head, 'rgba(0,0,0,0.5)', 2);
  ell(108, 8, 13, 10.5, 0.1, L); ell(114, 10, 3.5, 2.5, 0, '#4a4a4a');
  if (k < 0.04) pthS('M106,30 C90,42 64,46 44,44', L, 3.5);
  else {
    const cx = lerp(44, 6, k), cy = lerp(44, 24, k);
    const top = u => [lerp(104, cx, u), lerp(29, cy, u) + Math.sin(u * Math.PI) * (5 - 9 * k)];
    const bot = u => [lerp(101, cx, u), lerp(34 + jaw, cy, u) + Math.sin(u * Math.PI) * (6 + 16 * k)];
    const mp = new Path2D(); for (let i = 0; i <= 16; i++) mp.lineTo(...top(i / 16)); for (let i = 16; i >= 0; i--) mp.lineTo(...bot(i / 16)); mp.closePath();
    ctx.fillStyle = TC.mouth; ctx.fill(mp); ctx.save(); ctx.clip(mp);
    // lower teeth (pointing up), then upper teeth (pointing down), back to front; tooth slots run from the front (u small) to the corner
    const run = (list, f, dir) => { let u = 0.04; const slots = list.map(([w, h, kind]) => { const s = { u: u + w / 2 / 84, w: w * 1.4, h: h * 1.3, kind }; u += w / 84; return s; });
      for (const s of slots.slice().reverse()) { const [tx, ty] = f(s.u); const sc = 1 - s.u * 0.25; drawTooth(tx, ty + dir * 5, s.w * sc, dir * s.h * sc * (0.6 + 0.4 * k), s.kind, -1, { lw: 1.1 }); }
      return slots; };
    run(SIDE_LO, bot, -1);
    const us = run(SIDE_UP, top, 1);
    // upper gum: a red band with scallops between the teeth
    const g = new Path2D(); for (let i = 0; i <= 16; i++) g.lineTo(top(i / 16)[0], top(i / 16)[1] - 3);
    for (const s of us.slice().reverse()) { const hw = s.w / 1.4 / 168; const [a0, b0] = top(s.u + hw), [a1, b1] = top(s.u), [a2, b2] = top(s.u - hw); g.lineTo(a0, b0 + 7); g.quadraticCurveTo(a1, b1 + 2, a2, b2 + 7); }
    g.closePath(); ctx.fillStyle = TC.gum; ctx.fill(g);
    ctx.restore();
    // black lips and a cheek fold at the corner
    for (const f of [top, bot]) { ctx.beginPath(); for (let i = 0; i <= 16; i++) ctx.lineTo(...f(i / 16)); ctx.lineWidth = 3.5; ctx.strokeStyle = '#000'; ctx.stroke(); }
    ctx.save(); ctx.globalAlpha *= clamp(k * 1.5); pthS(`M${cx - 2},${cy - 4} q-10,-6 -8,-20`, L, 2.5); pthS(`M${cx + 10},${cy - 10} q-6,-6 -4,-16`, L, 2); ctx.restore();
  }
  if (o.close) pthS('M8,-16 q10,7 20,0', L, 4.5);
  else if ((o.eye || 0) > 0) { ctx.save(); redGlow(22 * o.eye); ell(18, -16, 8, 8.5, 0, C.red); ctx.restore(); }
  else { ell(18, -16, 7.5 + 1.5 * k, 8 + 1.5 * k, 0, L); circ(20.5, -18.5, 2.2 - 1 * k, '#fff'); }
  pthS(`M2,${-32 + 4 * k} q14,${-8 + 6 * k} 28,${-2 + 6 * k}`, L, 3);   // the brow pulls down; the eye stays wide and does not smile
  if (k > 0.3) { ctx.save(); ctx.globalAlpha *= k; pthS('M62,-24 q6,-6 12,-2 M66,-16 q6,-6 12,-2', L, 2); ctx.restore(); }   // the snout wrinkles
  const ep = 'M14,-50 C-24,-58 -46,-30 -50,6 C-54,44 -46,74 -26,80 C-8,84 0,64 -2,40 C-4,10 4,-20 22,-40 C26,-46 22,-50 14,-50 Z';
  glow('rgba(0,0,0,0.5)', 6); pth(ep, '#d2d2d2'); noGlow(); pthS('M14,-50 C-4,-30 -6,10 -2,40 C0,64 -8,84 -26,80', 'rgba(0,0,0,0.55)', 2.5);
}
// a close-up of the profile for the big moments: centre (x,y), scale s; facing right (dir -1 left)
function dogProfileBig(x, y, s, o = {}) { ctx.save(); ctx.translate(x, y); ctx.scale(s * (o.dir || 1), s);
  // neck and chest behind the head
  glow('rgba(255,255,255,0.25)', 20); pth('M-60,30 C-90,90 -110,190 -120,320 L80,320 C60,200 40,110 30,60 Z', DOG.fig); noGlow();
  ctx.save(); ctx.translate(-30, 60); ctx.rotate(0.5); rr(-50, -8, 100, 16, 6, '#1a1a1a'); ctx.restore();
  dogHead(o); ctx.restore(); }
// ---------- EP09 scenes: "If Your Dog Ever Smiles With Human Teeth… DO NOT SMILE BACK" (Protocol 404) ----------
// Pure black, pure white vector figures, red only for danger. You are faceless; only the dog has a mouth.
const ev = type => window.TL.events.filter(e => e.type === type);
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
const blackAfter = (t, t0) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const zk = (t, t0, d, z0, z1) => lerp(z0, z1, ease((t - t0) / d));
const black = () => { ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); };
const segEnd = seg => seg.end + 0.7;
const seg$ = id => window.TL.segments.find(s => s.id === id);
// a close-up: (cx, cy) is brought to the centre of the screen at zoom z
function focus(t, t0, d, z0, z1, cx, cy, fn) { const z = zk(t, t0, d, z0, z1); ctx.save(); ctx.translate(W / 2, H / 2 - 40); ctx.scale(z, z); ctx.translate(-cx, -cy); fn(); ctx.restore(); }
const flatT = fn => { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); fn(); ctx.restore(); };
const redWash = (a) => { if (a > 0) flatT(() => { ctx.globalAlpha = a; ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); }); };
// shot switcher: [[t0, fn], ...] -> the last shot whose start has passed
function shots(t, list) { let f = list[0][1], t0 = list[0][0]; for (const [a, g] of list) if (t >= a) { f = g; t0 = a; } f(t0); }
// a "does not work" header at the top left: a small drawn icon, the label, a red X on the icon at tx
function noHead(t, seg, draw, label, tx) {
  flatT(() => slideIn(t, seg.start, -40, 0, () => { ctx.font = '900 46px M'; const w = 200 + ctx.measureText(label).width; ctx.save(); ctx.globalAlpha *= 0.9; rr(60, 60, w, 130, 18, '#050505'); ctx.restore(); rrS(60, 60, w, 130, 18, '#2a2a2d', 3);
    draw(125, 125); text(label, 200, 142, '900 46px M', C.fig, 'left'); redX(125, 125, 48, prog(t, tx, 0.3)); }, 0.35));
}
// a big label that pops and stays
const bigTag = (t, t0, s, x, y, col = C.fig, size = 56) => { if (t >= t0) pop(t, t0, x, y, () => tag(s, x, y, col, size, 'center'), 0.3); };
// the dog's head of each figure for growl arcs / bubbles
const DOGX = 1260, YOUX = 620;

// ---------- hook ----------
S.h1 = (t, seg) => {
  // frame 0: the dog's face, already smiling with a full set of human teeth
  const td = wt(seg, 'do'), tt = wt(seg, 'teeth');
  black();
  cam(t, 0, seg.end + 0.6, 1.0, 1.14, 960, 560, () => dogFace(960, 560, 1.32, { smile: 1, eye: prog(t, tt, 0.4) * 0.0 }));
  if (t >= td - 0.1) flatT(() => pop(t, td - 0.1, 960, 110, () => tag('DO NOT SMILE BACK', 960, 120, C.red, 56, 'center'), 0.3));
};
function teaserBox(t, w0, draw, tx, y = 250, x = 1640) {
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(x - 130, y - 120, 260, 240, 22, '#000'); ctx.restore(); rrS(x - 130, y - 120, 260, 240, 22, C.fig, 5); draw(x, y); }, 0.3);
  redX(x, y, 95, prog(t, tx + 0.25, 0.3));
}
const H2_HIT = 0.6, H2_BLACK = 0.4;
S.h2 = (t, seg) => {
  // three quick "do not"s, each done anyway: it pats your head / it sits at your table / the mirror
  const ws = [[seg.start, wt(seg, 'do', 2), 'smile'], [wt(seg, 'do', 2), wt(seg, 'and'), 'eat'], [wt(seg, 'and'), nextStart(seg), 'look']];
  let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, word] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit, L = blk - w0;
  if (t < blk) {
    black();
    if (i === 0) cam(t, w0, L, 1.0, 1.15, 900, 560, () => { floorLine();
      const up = prog(t, w0 + 0.5, 1.0), pat = prog(t, hit - 0.5, 0.3);
      you(760, FL, 1.05, { dir: 1 });
      dog(1120, FL, 1.12, { dir: -1, rear: up, eye: prog(t, hit - 0.2, 0.2), smile: 1, reach: [790, 452 + Math.abs(Math.sin((t - hit) * 18)) * 18 * (t > hit - 0.5 ? 1 : 0)], reachK: pat }); });
    else if (i === 1) cam(t, w0, L, 1.0, 1.12, 1100, 560, () => { floorLine(); chair(1380, 1, -1); dog(1384, FL - 176, 1.0, { dir: -1, rear: 1, sit: 1, eye: prog(t, hit - 0.3, 0.2), smile: prog(t, w0 + 0.4, 0.6), reach: [1270, 596], reachK: 1 });
      table(640, 1290); plate(820, 600, 1, { food: true }); plate(1150, 600, 1, { fork: false }); chair(560, 1, 1); you(560, FL - 0, 1, { pose: 'sit', hand: [700, 594] }); });
    else cam(t, w0, L, 1.0, 1.2, 960, 520, () => { floorLine();
      mirrorFrame(760, 170, 400, 690, { inner: () => { floorLine(FL, '#1a1a1a'); you(950, FL, 0.78, { pose: 'fours', dir: -1, red: prog(t, hit - 0.3, 0.2) }); } });
      dog(560, FL, 0.95, { dir: 1, sit: 1 }); });
    redWash(d > 0 ? 0.35 * clamp(d / 0.2) : 0);
  }
  blackAfter(t, blk);
  const draws = [(x, y) => pageIcon('smile', x, y, '#fff'), (x, y) => pageIcon('plate', x, y, '#fff'), (x, y) => pageIcon('mirror', x, y, '#fff')];
  flatT(() => teaserBox(t, w0, (x, y) => { ctx.save(); ctx.translate(x, y); ctx.scale(1.5, 1.5); ctx.translate(-x, -y); draws[i](x, y); ctx.restore(); }, wt(seg, word)));
};

// ---------- rule 1: do not smile back ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT SMILE BACK');
S.a1 = (t, seg) => {
  // you come home; the dog runs to the door, tail going
  const tr = wt(seg, 'runs'), ttl = wt(seg, 'tail');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 1100, 560, () => {
    floorLine();
    const op = ease(prog(t, seg.start + 0.1, 0.6));
    hallDoor(1500, op);
    you(lerp(1610, 1440, ease(prog(t, seg.start + 0.4, 1.4))), FL, 1, { dir: -1, walk: t < seg.start + 1.8 ? t * 8 : null });
    const run = ease(prog(t, tr - 0.3, 1.8)), dx = lerp(-200, 1130, run);
    dog(dx, FL, 0.95, { dir: 1, walk: run < 1 ? t * 14 : null, wag: t >= ttl - 0.3 ? t * 16 : t * 4 });
  });
};
S.a2 = (t, seg) => {
  // the smile: it opens slowly; then a close-up of the teeth
  const ts = wt(seg, 'smiles'), tw = wt(seg, 'wide'), tb = wt(seg, 'behind'), th = wt(seg, 'human');
  black();
  if (t < tb - 0.05) {
    const k = lerp(0, 0.25, prog(t, ts, 0.8)) + lerp(0, 0.35, prog(t, tw, 0.6));
    cam(t, seg.start, tb - seg.start, 1.0, 1.12, 960, 560, () => dogFace(960, 560, 1.15, { smile: k }));
  } else {
    focus(t, tb - 0.05, 3.0, 1.9, 2.15, 960, 700, () => dogFace(960, 560, 1.15, { smile: lerp(0.6, 1, ease(prog(t, tb, 1.4))) }));
    if (t >= th) flatT(() => { ctx.save(); redGlow(16); lnP(1560, 470, 1240, 700, 6, C.red, prog(t, th, 0.3)); ctx.restore(); bigTag(t, th + 0.2, 'HUMAN TEETH', 1600, 430, C.red, 52); });
  }
};
S.a3 = (t, seg) => {
  // something moved in; it copies the face it sees most (yours); the smile is a question
  const tl = wt(seg, 'learns'), ty = wt(seg, 'yours'), ta = wt(seg, 'and'), tq = wt(seg, 'question');
  black();
  shots(t, [
    [seg.start, t0 => cam(t, t0, tl - t0, 1.0, 1.1, 960, 600, () => { floorLine(); dog(980, FL, 1.4, { dir: 1, sit: 1 }); insideMe(880, FL - 230, 1.05, prog(t, t0 + 0.6, 0.6)); })],
    [tl - 0.05, t0 => cam(t, t0, ta - t0, 1.0, 1.06, 960, 560, () => { floorLine();
      you(560, FL, 1.15, { dir: 1, red: t >= ty ? 0.8 : 0 }); dog(1260, FL, 1.15, { dir: -1, sit: 1 });
      ctx.save(); ctx.setLineDash([16, 14]); ctx.lineDashOffset = -t * 60; ln(1170, 520, 640, 460, 5, t >= ty ? C.red : C.fig); ctx.restore();
      bigTag(t, t0 + 0.6, 'COPYING', 900, 330, C.fig, 50); })],
    [ta - 0.05, t0 => { cam(t, t0, segEnd(seg) - t0, 1.0, 1.08, 960, 560, () => dogFace(860, 580, 1.0, { smile: 1 }));
      if (t >= tq - 0.3) say(t, tq - 0.3, 1450, 260, '?', 1140, 400, 120); }],
  ]);
};
S.a4 = (t, seg) => {
  // trade places: you and the dog, two red arrows swapping
  const tt = wt(seg, 'trade');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 560, () => {
    floorLine(); you(620, FL, 1.1, { dir: 1 }); dog(1300, FL, 1.1, { dir: -1, sit: 1, smile: 1 });
    swapArrows(640, 1290, 360, prog(t, tt - 0.1, 0.6), C.red, 150);
  });
};
S.a5 = (t, seg) => {
  // every day of its life: a wall of smiles; a smile is a yes
  const tdo = wt(seg, 'do'), ty = wt(seg, 'yes');
  black();
  if (t < tdo - 0.05) {
    const n = Math.floor(clamp((t - seg.start - 0.3) / (tdo - seg.start - 0.8)) * 160);
    cam(t, seg.start, tdo - seg.start, 1.0, 1.06, 960, 520, () => {
      for (let i = 0; i < 160; i++) { if (i >= n) break; const cx = 300 + (i % 20) * 69, cy = 200 + Math.floor(i / 20) * 72; ctx.save(); ctx.translate(cx, cy); ctx.scale(0.62, 0.62); ctx.translate(-cx, -cy); pageIcon('smile', cx, cy, C.fig); ctx.restore(); }
      text((Math.round(n * 22.8)).toLocaleString('en-US') + ' DAYS', 960, 860, '900 64px M', C.fig);
    });
  } else {
    cam(t, tdo - 0.05, segEnd(seg) - tdo, 1.0, 1.08, 960, 520, () => {
      ctx.save(); ctx.translate(960, 480); ctx.scale(4, 4); ctx.translate(-960, -480); pageIcon('smile', 960, 480, t >= ty ? C.red : C.fig); ctx.restore();
      if (t >= ty - 0.1) stampMark(t, ty - 0.1, 1230, 660, [['YES', 120]], -0.12, '#000', 30);
    });
  }
};
S.a6 = (t, seg) => {
  // what to do instead
  const tk = seg.start + 0.05, tp = wt(seg, 'pet'), tn = wt(seg, 'say'), tw = wt(seg, 'then');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.04, 960, 520, () => {
    okRow(t, tk, 520, 300, 'KEEP YOUR FACE STILL');
    okRow(t, tp - 0.1, 520, 460, 'PET IT');
    okRow(t, tn - 0.1, 520, 620, 'SAY ITS NAME');
    okRow(t, tw - 0.1, 520, 780, 'WALK AWAY');
  });
};
S.a7 = (t, seg) => {
  // one owner smiled back: it stood up and patted his head. "Good boy." In his voice.
  const tsb = wt(seg, 'smiled'), tst = wt(seg, 'stood'), tr = wt(seg, 'reached'), tp = wt(seg, 'patted'), tg = wt(seg, 'good'), tv = wt(seg, 'voice');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.0, 1.22, 960, 470, () => {
    floorLine();
    const reach = prog(t, tr - 0.2, 0.6), pt = t - tp, bob = pt > 0 && pt < 1.2 ? Math.abs(Math.sin(pt * 9)) * 22 : 0;
    you(800, FL, 1.05, { dir: 1, red: t >= tv ? 0.8 : 0 });
    dog(1180, FL, 1.18, { dir: -1, rear: prog(t, tst - 0.1, 1.1), eye: t >= tg ? 1 : 0, smile: t >= tsb ? 1 : 0.2, reach: [834, 456 - bob], reachK: reach });
    if (t >= tg) say(t, tg - 0.05, 1350, 170, 'GOOD BOY.', 1180, 300, 56, { red: true });
  });
};

// ---------- rule 2: do not let it eat from your plate ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT LET IT EAT FROM YOUR PLATE');
// the dining room: you at the left end of the table; o.dogAt: 'floor' (next to your chair) | 'chair' (the chair opposite) | null; o.chairOut 0..1
function dining(t, o = {}) {
  floorLine();
  const cx = lerp(1420, 1520, ease(o.chairOut ?? 0));
  if (o.dogAt === 'chair') { chair(cx, 1, -1); dog(cx + 4, FL - 176, 1.0, { dir: -1, rear: 1, sit: 1, eye: o.eye || 0, reach: [1255, 596], reachK: 1, smile: o.smile || 0 }); }
  else chair(cx, 1, -1);
  table(620, 1300);
  plate(800, 600, 1, { food: true }); if (o.dogAt === 'chair' || o.two) plate(1140, 600, 1, { food: false, fork: o.dogAt === 'chair' });
  if (o.salt) { rr(940, 556, 30, 44, 6, C.fig); circ(955, 556, 10, C.fig); }
  chair(520, 1, 1); you(522, FL, 1, { pose: 'sit', hand: o.hand || [700, 594] });
  if (o.forkUp != null) { const k = o.forkUp; ln(700, 594 - 60 * k, 770, 560 - 60 * k, 6, C.fig); }
  if (o.dogAt === 'floor') dog(380, FL, 0.8, { dir: 1, sit: 1, head: -0.3 });
  if (o.bowl !== false) bowl(1700, 0.9, { full: o.full });
}
S.b1 = (t, seg) => {
  // dinner: it walks past its bowl and sits next to your chair, watching your fork
  const tg = wt(seg, 'go'), tsit = wt(seg, 'sits'), tw = wt(seg, 'watches');
  black();
  if (t < tw - 0.1) {
    cam(t, seg.start, tw - seg.start, 1.0, 1.05, 960, 560, () => {
      dining(t, { dogAt: null, full: true });
      const k = ease(prog(t, tg - 0.6, tsit - tg + 0.8)), dx = lerp(1780, 380, k);
      dog(dx, FL, 0.8, { dir: -1, walk: k < 1 ? t * 12 : null, sit: k >= 1 ? prog(t, tsit + 0.2, 0.3) : 0 });
      if (t >= tg) bigTag(t, tg, 'BOWL', 1700, 700, '#8a8a8a', 30);
    });
  } else {
    focus(t, tw - 0.1, segEnd(seg) - tw, 1.9, 2.1, 640, 520, () => {
      dining(t, { dogAt: 'floor', forkUp: 0.5 + 0.5 * Math.sin(t * 2.4) });
      ctx.save(); ctx.setLineDash([10, 10]); ctx.lineDashOffset = -t * 40; ln(470, 630, 720, 530 - 30 * (0.5 + 0.5 * Math.sin(t * 2.4)), 4, C.red); ctx.restore();
    });
  }
};
S.b2 = (t, seg) => {
  // a real dog begs; this one is studying: the grip, the chewing, the pauses
  const tsd = wt(seg, 'studying'), th = wt(seg, 'hold'), tc = wt(seg, 'chew'), tw = wt(seg, 'wait');
  black();
  if (t < tsd - 0.1) {
    cam(t, seg.start, tsd - seg.start, 1.0, 1.06, 960, 560, () => { floorLine(); you(760, FL, 1, { pose: 'sit', hand: [870, 594] }); table(840, 1300); dog(1180, FL, 0.95, { dir: -1, rear: 0.35, wag: t * 10, reach: [1040, 600], reachK: 0.6 });
      bigTag(t, seg.start + 0.3, 'REAL DOG: BEGS', 1100, 300, '#9a9a9a', 40); });
  } else {
    cam(t, tsd - 0.1, segEnd(seg) - tsd, 1.0, 1.08, 760, 560, () => {
      dining(t, { dogAt: 'floor', forkUp: 0.5 + 0.5 * Math.sin(t * 3), bowl: false });
      const scan = (y0, y1, t0) => { if (t < t0) return; ctx.save(); ctx.setLineDash([10, 10]); ctx.globalAlpha *= 0.9; ln(470, 620, y0, y1, 3, C.red); ctx.restore(); };
      scan(720, 590, th); scan(540, 512, tc); scan(800, 600, tw);
      if (t >= th) pop(t, th, 1100, 380, () => tag('FORK GRIP: RIGHT HAND', 980, 390, C.fig, 36, 'left'), 0.3);
      if (t >= tc) pop(t, tc, 1100, 470, () => tag('CHEWS: 14 TIMES', 980, 480, C.fig, 36, 'left'), 0.3);
      if (t >= tw) pop(t, tw, 1100, 560, () => tag('PAUSE: 6.2 S', 980, 570, C.red, 36, 'left'), 0.3);
    });
  }
};
S.b3 = (t, seg) => {
  // not even one piece: every bite teaches it what you are made of
  const te = wt(seg, 'every'), tt = wt(seg, 'teaches');
  black();
  if (t < te - 0.05) {
    cam(t, seg.start, te - seg.start, 1.0, 1.06, 960, 540, () => {
      forkHand(640, 560, 1.1, 0.05, { food: true });
      dog(1520, FL + 60, 1.25, { dir: -1, sit: 1, head: -0.15 });
      redX(870, 540, 90, prog(t, seg.start + 0.6, 0.3));
    });
  } else {
    cam(t, te - 0.05, segEnd(seg) - te, 1.0, 1.06, 960, 540, () => {
      floorLine(); dog(1000, FL, 1.35, { dir: 1, sit: 1 });
      insideMe(900, FL - 220, 1.0, 0.4 + 0.6 * prog(t, tt, 0.5));
      flatT(() => meter(560, 140, 700, 'YOU, COPIED', lerp(0.12, 0.31, ease(prog(t, tt, 1.2)))));
    });
  }
};
S.b4 = (t, seg) => {
  // the next night: the bowl still full; the chair across from you pulled out
  const tc = wt(seg, 'chair'), tp = wt(seg, 'pulled');
  black();
  if (t < tc - 0.1) {
    focus(t, seg.start, tc - seg.start, 2.2, 2.4, 1700, 790, () => { floorLine(); bowl(1700, 0.9, { full: true }); });
    flatT(() => bigTag(t, seg.start + 0.3, 'NEXT NIGHT', 960, 160, C.fig, 50));
  } else {
    cam(t, tc - 0.1, segEnd(seg) - tc + 0.4, 1.0, 1.06, 1000, 560, () => dining(t, { dogAt: null, chairOut: prog(t, tp - 0.1, 0.5), full: true, two: true }));
  }
};
S.b5 = (t, seg) => {
  // it is sitting in it: back straight, paws on the table, waiting for the salt
  const tb = wt(seg, 'back'), tpw = wt(seg, 'paws'), ts = wt(seg, 'salt');
  black();
  focus(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.25, 1.5, 1200, 480, () => {
    dining(t, { dogAt: 'chair', salt: true, eye: t >= ts ? 1 : 0, smile: t >= ts ? 0.6 : 0 });
    if (t >= tb && t < tpw) { ctx.save(); ctx.setLineDash([12, 10]); ln(1450, 330, 1450, 690, 4, C.fig); ctx.restore(); }
    if (t >= tpw) { ctx.save(); redGlow(14); circS(1262, 590, 46, C.red, 5); ctx.restore(); }
  });
};
S.b6 = (t, seg) => {
  // feed it in another room, close the door, eat fast
  const tc = wt(seg, 'close'), te = wt(seg, 'eat');
  black();
  shots(t, [
    [seg.start, t0 => cam(t, t0, tc - t0, 1.0, 1.05, 960, 560, () => { floorLine(); bowl(1100, 1, { full: true }); dog(820, FL, 0.9, { dir: 1, walk: t * 10 }); })],
    [tc - 0.05, t0 => cam(t, t0, te - t0, 1.0, 1.04, 960, 560, () => { floorLine(); const k = ease(prog(t, t0 + 0.1, 0.35)); rrS(860, FL - 470, 220, 470, 4, C.fig, 5);
      ctx.save(); ctx.translate(860, 0); ctx.scale(1 - 0.85 * (1 - k), 1); rr(4, FL - 466, 212, 462, 2, '#000'); rrS(4, FL - 466, 212, 462, 2, '#9a9a9a', 3); circ(186, FL - 220, 8, C.fig); ctx.restore(); })],
    [te - 0.05, t0 => cam(t, t0, segEnd(seg) - t0, 1.0, 1.06, 700, 560, () => dining(t, { dogAt: null, forkUp: 0.5 + 0.5 * Math.sin(t * 14), bowl: false }))],
  ]);
};

// ---------- rule 3: never let it look in the mirror ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'NEVER LET IT LOOK IN THE MIRROR');
// the hallway mirror with the dog sitting in front of it. o.refl(fn) overrides what the glass shows
const MIR = [820, 160, 420, 700];
function mirrorHall(t, o = {}) {
  floorLine();
  const [mx, my, mw, mh] = MIR, dk = o.dogX ?? 640;
  mirrorFrame(mx, my, mw, mh, { inner: o.refl || (() => { floorLine(FL, '#1c1c1c'); dog(1090, FL, 0.8, { dir: -1, sit: o.sit ?? 1, smile: o.smile || 0 }); }) });
  dog(dk, FL, 0.95, { dir: 1, sit: o.sit ?? 1, walk: o.walk, smile: o.smile || 0, eye: o.eye || 0, head: o.head || 0 });
}
S.c1 = (t, seg) => {
  // dogs don't care about mirrors; yours stops in front of the hallway mirror and stays
  const tst = wt(seg, 'stops'), ts = wt(seg, 'stays');
  black();
  if (t < tst - 0.1) cam(t, seg.start, tst - seg.start, 1.0, 1.04, 960, 560, () => { floorLine(); dog(lerp(-100, 1900, prog(t, seg.start, 3.2)), FL, 0.85, { dir: 1, walk: t * 12, wag: t * 6 });
    flatT(() => bigTag(t, seg.start + 0.2, 'MIRRORS: IGNORED', 960, 150, '#9a9a9a', 40)); });
  else cam(t, tst - 0.1, segEnd(seg) - tst, 1.0, 1.1, 900, 520, () => {
    const k = ease(prog(t, tst - 0.1, 1.0));
    mirrorHall(t, { dogX: lerp(200, 640, k), sit: prog(t, tst + 0.8, 0.3), walk: k < 1 ? t * 12 : null });
    if (t >= ts) pop(t, ts, 1500, 220, () => tag('2 HOURS', 1500, 230, C.red, 46, 'center'), 0.3);
  });
};
S.c2 = (t, seg) => {
  // checking its work: its teeth against yours
  const tc = wt(seg, 'comparing');
  black();
  if (t < tc - 0.05) cam(t, seg.start, tc - seg.start, 1.0, 1.08, 1000, 480, () => mirrorHall(t, { smile: prog(t, seg.start + 0.3, 0.5) }));
  else cam(t, tc - 0.05, segEnd(seg) - tc, 1.0, 1.04, 960, 520, () => {
    teethRow(960, 330, 0.95); text('YOURS', 960, 230, '900 40px M', C.fig);
    teethRow(960, 690, 0.95); text('ITS', 960, 590, '900 40px M', C.red);
    const sy = lerp(260, 820, (t - tc) % 1.2 / 1.2); ctx.save(); redGlow(12); ln(520, sy, 1400, sy, 3, C.red); ctx.restore();
    text(Math.min(98, Math.round(prog(t, tc, 1.6) * 98)) + '% MATCH', 1560, 540, '900 52px M', C.red);
  });
};
S.c3 = (t, seg) => {
  // cover it, move it, turn it to the wall
  const tc = wt(seg, 'cover'), tm = wt(seg, 'move'), tw = wt(seg, 'turn');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.05, 960, 520, () => {
    floorLine(); const [mx, my, mw, mh] = MIR;
    const mv = ease(prog(t, tm, 0.5)) * 140, tr = ease(prog(t, tw, 0.5));
    ctx.save(); ctx.translate(mx + mw / 2 + mv, 0); ctx.scale(Math.max(0.04, Math.abs(Math.cos(tr * Math.PI))), 1); ctx.translate(-(mx + mw / 2), 0);
    if (tr < 0.5) mirrorFrame(mx, my, mw, mh, { inner: () => { floorLine(FL, '#1c1c1c'); dog(1090, FL, 0.8, { dir: -1, sit: 1 }); } });
    else { rr(mx, my, mw, mh, 14, '#1a1a1a'); rrS(mx, my, mw, mh, 14, C.fig, 8); ln(mx + 40, my + 40, mx + mw - 40, my + mh - 40, 3, '#3a3a3a'); ln(mx + mw - 40, my + 40, mx + 40, my + mh - 40, 3, '#3a3a3a'); }
    const cv = ease(prog(t, tc, 0.5));   // a sheet drops over it
    if (cv > 0 && tr < 0.5) { glow('rgba(255,255,255,0.25)', 16); pth(`M${mx - 30},${my - 20} L${mx + mw + 30},${my - 20} L${mx + mw + 40},${my - 20 + (mh * 0.75) * cv} C${mx + mw * 0.7},${my + mh * 0.7 * cv} ${mx + mw * 0.3},${my + mh * 0.82 * cv} ${mx - 40},${my - 20 + mh * 0.78 * cv} Z`, '#e4e4e4'); noGlow(); }
    ctx.restore();
    dog(640, FL, 0.95, { dir: 1, sit: 1, head: -0.1 });
  });
  flatT(() => { okRow(t, tc - 0.1, 1480, 300, 'COVER', 44); okRow(t, tm - 0.1, 1480, 450, 'MOVE', 44); okRow(t, tw - 0.1, 1480, 600, 'TURN', 44); });
};
S.c4 = (t, seg) => {
  // the day it sees a face that matches yours, it stops being a dog
  const tm = wt(seg, 'matches'), ts = wt(seg, 'stops');
  black();
  focus(t, seg.start, segEnd(seg) - seg.start, 1.5, 1.8, 1030, 420, () => mirrorHall(t, { smile: 1, refl: () => { ctx.fillStyle = '#050505'; ctx.fillRect(0, 0, W, H); dogFace(1030, 430, 0.62, { smile: 1, eye: prog(t, ts, 0.3) }); } }));
  flatT(() => meter(560, 110, 700, 'MATCH', lerp(0.98, 1, prog(t, tm, 0.6)), t >= tm ? C.red : C.fig));
};
S.c5 = (t, seg) => {
  // in the mirror, where your dog is sitting, there is a person on all fours; the dog smiles
  const tp = wt(seg, 'person'), tf = wt(seg, 'fours'), tsm = wt(seg, 'smiling');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.0, 1.2, 960, 560, () => {
    const show = t >= tp - 0.1;
    mirrorHall(t, { smile: t >= tsm - 0.1 ? 1 : 0, refl: () => { floorLine(FL, '#1c1c1c'); if (show) you(1010, FL, 0.8, { pose: 'fours', dir: -1 }); else dog(1090, FL, 0.8, { dir: -1, sit: 1 }); } });
    if (show && t < tp + 0.25) { ctx.save(); ctx.globalAlpha = 0.3 * (1 - prog(t, tp - 0.1, 0.35)); ctx.fillStyle = '#fff'; ctx.fillRect(MIR[0], MIR[1], MIR[2], MIR[3]); ctx.restore(); }
  });
};
S.c6 = (t, seg) => {
  // it turns around, slowly: which one of you is the copy
  const tt = wt(seg, 'turns'), tw = wt(seg, 'which');
  black();
  focus(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.5, 2.0, 1060, 640, () => {
    const turn = ease(prog(t, tt, 2.2));
    mirrorHall(t, { smile: 1, refl: () => { floorLine(FL, '#1c1c1c'); you(1010, FL, 0.8, { pose: 'fours', dir: -1, head: -30 * turn, red: t >= tw ? 1 : turn * 0.5 }); } });
  });
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
S.d1 = (t, seg) => {
  // broke a rule: the trade begins; leave it alone and it finishes
  const ts = wt(seg, 'smiled'), tf = wt(seg, 'fed'), tm = wt(seg, 'mirror'), tt = wt(seg, 'trade'), tfi = wt(seg, 'finishes');
  black();
  if (t < tt - 0.1) cam(t, seg.start, tt - seg.start, 1.0, 1.06, W / 2, 520, () => rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9], struck: [ts + 0.2, tf + 0.2, tm + 0.2, null] }));
  else cam(t, tt - 0.1, segEnd(seg) - tt, 1.0, 1.06, 960, 520, () => {
    floorLine(); you(620, FL, 1.05, { dir: 1, red: t >= tfi ? 1 : 0 }); dog(1300, FL, 1.05, { dir: -1, sit: 1, smile: 1, eye: t >= tfi ? 1 : 0 });
    swapArrows(640, 1290, 380, prog(t, tt, 0.5), C.red, 150);
    flatT(() => meter(560, 130, 700, 'TRADE', lerp(0.1, 1, ease(prog(t, tt + 0.4, tfi - tt + 0.2)))));
  });
};
function bedroom9(t, o = {}) {
  bedroomNight({ door: false });
  // your bed: something dog-shaped under the blanket, its head on your pillow, a tail hanging over the side
  ctx.save(); ctx.translate(380, 900); ctx.scale(1.25, 1.25);
  glow('rgba(255,255,255,0.22)', 16);
  rr(0, -330, 30, 330, 10, C.fig); rr(560, -170, 22, 170, 8, C.fig); rr(0, -150, 582, 46, 12, C.fig); rr(26, -104, 16, 104, 4, C.sec); rr(540, -104, 16, 104, 4, C.sec); rr(30, -196, 530, 48, 18, C.sec);
  ell(98, -204, 56, 16, 0, C.fig); noGlow();
  ctx.save(); ctx.translate(96, -262); ctx.scale(-0.8, 0.8); dogHead({ close: !o.awake, eye: o.awake ? 1 : 0 }); ctx.restore();
  glow('rgba(255,255,255,0.22)', 16); pth('M140,-196 C170,-252 260,-262 340,-256 C420,-250 500,-238 568,-222 L572,-176 L140,-176 Z', C.fig); noGlow();
  ctx.save(); ctx.translate(560, -186); ctx.rotate(1.3 + Math.sin(t * 2) * 0.05); pth('M0,-12 C-40,-22 -80,-34 -112,-40 C-118,-30 -110,-20 -100,-18 C-70,-10 -36,6 0,12 Z', C.fig); ctx.restore();
  ctx.restore();
  dogBed(1440, 1.05); you(1440, FL - 14, 0.95, { pose: 'curl', dir: -1, red: o.meRed || 0 });
}
S.d2 = (t, seg) => {
  // 3 AM: you wake up on the floor in the dog bed; something is asleep on your pillow
  const tw = wt(seg, 'wake'), tu = wt(seg, 'up');
  black();
  if (t < tu - 0.1) focus(t, seg.start, tu - seg.start, 1.6, 1.8, 1430, 760, () => bedroom9(t, { meRed: t >= tw ? 0.6 : 0 }));
  else cam(t, tu - 0.1, segEnd(seg) - tu + 0.4, 1.0, 1.12, 760, 600, () => bedroom9(t, {}));
  flatT(() => bigTag(t, seg.start + 0.2, '3:00 AM', 1640, 140, C.red, 52));
};
S.d3 = (t, seg) => {
  // on the nightstand: a collar, a tag, your name
  const tc = wt(seg, 'collar'), tn = wt(seg, 'name', 2);
  black();
  focus(t, seg.start, segEnd(seg) - seg.start + 0.4, 1.3, 1.45, 960, 470, () => { nightstand(960, 2.2); collar(960, FL - 440 - 70, 1.0, { red: prog(t, tn, 0.3) }); });
};
S.d4 = (t, seg) => {
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 520, () => {
    pop(t, seg.start, 960, 470, () => { ctx.save(); redGlow(24); spaced('DOES NOT WORK', 960, 500, '900 110px M', C.red, 8); ctx.restore(); }, 0.35);
    lnP(420, 560, 1500, 560, 6, C.red, prog(t, seg.start + 0.3, 0.5));
  });
};
S.d5 = (t, seg) => {
  // the vet: his teeth are perfectly healthy; healthier than yours
  const th = wt(seg, 'his'), thr = wt(seg, 'healthier');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 560, () => {
    phoneIcon(560, 560, 2.2, t < th ? C.fig : '#9a9a9a');
    if (t >= th) say(t, th - 0.05, 1240, 430, 'PERFECTLY\nHEALTHY.', 760, 520, 64);
    if (t >= thr) say(t, thr - 0.05, 1300, 700, 'HEALTHIER\nTHAN YOURS.', 820, 640, 54, { red: true });
  });
  noHead(t, seg, (x, y) => { ctx.save(); ctx.translate(x, y); ctx.scale(0.36, 0.36); phoneIcon(0, -20, 1); ctx.restore(); }, 'CALL THE VET', seg.start + 1.0);
};
S.d6 = (t, seg) => {
  // locked outside: thirty seconds later, the doorbell rings
  const tth = wt(seg, 'thirty'), td = wt(seg, 'doorbell');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 1000, 560, () => {
    floorLine(); hallDoor(860, 0);
    const lk = prog(t, seg.start + 0.6, 0.3); ctx.save(); ctx.translate(1000, 560); if (lk > 0) { ctx.globalAlpha *= lk; rr(-40, -10, 80, 66, 10, C.red); ctx.beginPath(); ctx.arc(0, -10, 26, Math.PI, 0); ctx.lineWidth = 10; ctx.strokeStyle = C.red; ctx.stroke(); circ(0, 22, 8, '#000'); } ctx.restore();
    bellButton(1180, 520, 1, t >= td ? 0.5 + 0.5 * Math.sin((t - td) * 20) : 0);
    if (t >= td) ripple(1180, 520, td, t, C.red, 30, 200, 6);
    if (t >= tth) text('0:' + String(Math.min(30, Math.floor((t - tth) * 14))).padStart(2, '0'), 1500, 360, '900 90px M', C.fig);
  });
  noHead(t, seg, (x, y) => { ctx.save(); ctx.translate(x, y); rrS(-24, -40, 48, 80, 4, C.fig, 5); circ(14, 4, 5, C.fig); ctx.restore(); }, 'LOCK IT OUTSIDE', seg.start + 1.2);
};
S.d7 = (t, seg) => {
  // hiding: it is still a dog; it can smell you anywhere
  const tsm = wt(seg, 'smell');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 560, () => {
    // the house in section: three rooms, you in the closet on the right
    rrS(260, 260, 1400, 600, 6, '#5a5a5a', 4); ln(720, 260, 720, 860, 4, '#5a5a5a'); ln(1200, 260, 1200, 860, 4, '#5a5a5a'); ln(260, 560, 1660, 560, 4, '#5a5a5a');
    rrS(1460, 600, 160, 250, 4, C.fig, 4); you(1540, 846, 0.62, { dir: -1 });
    const k = prog(t, seg.start + 0.5, 3.4), dx = lerp(380, 1340, k);
    dog(dx, 860, 0.62, { dir: 1, walk: k < 1 ? t * 12 : null, head: 0.25 });
    if (t >= tsm - 0.6) { ctx.save(); redGlow(12); ctx.globalAlpha *= prog(t, tsm - 0.6, 0.4);
      for (let i = 0; i < 4; i++) { const yy = 700 + i * 30; ctx.beginPath(); for (let x = dx + 60; x < 1520; x += 10) ctx.lineTo(x, yy + Math.sin(x * 0.03 + t * 5 + i) * 10); ctx.strokeStyle = C.red; ctx.lineWidth = 4; ctx.stroke(); }
      ctx.restore(); }
  });
  noHead(t, seg, (x, y) => { ctx.save(); ctx.translate(x, y); rrS(-26, -42, 52, 84, 4, C.fig, 5); you(0, 34, 0.18, {}); ctx.restore(); }, 'HIDE', seg.start + 1.0);
};
S.d8 = (t, seg) => {
  // fighting it: a forty-kilo dog with a grown man's mind; it is on your chest before your hand comes down
  const tb = wt(seg, 'body'), tbe = wt(seg, 'before'), tc = wt(seg, 'chest'), ti = wt(seg, 'its'), tsm = wt(seg, 'smiles');
  black();
  shots(t, [
    [seg.start, t0 => { cam(t, t0, tb - t0, 1.0, 1.06, 960, 560, () => { floorLine(); you(760, FL, 1.05, { dir: 1, hand: [820, 420] }); dog(1250, FL, 1.05, { dir: -1, crouch: 0.6, smile: 0.5 }); });
      noHead(t, seg, (x, y) => { ctx.save(); ctx.translate(x, y); rr(-28, -28, 56, 52, 14, C.fig); ctx.restore(); }, 'FIGHT IT', seg.start + 1.0); }],
    [tb - 0.1, t0 => cam(t, t0, tbe - t0, 1.0, 1.05, 960, 540, () => {
      floorLine(); dog(560, FL, 1.0, { dir: 1, sit: 0 }); you(1380, FL, 1.05, { dir: -1 });
      bigTag(t, t0 + 0.3, 'BODY: 40 KG DOG', 560, 300, C.fig, 46); bigTag(t, wt(seg, 'mind') - 0.1, 'MIND: GROWN MAN', 1380, 300, C.red, 46); })],
    [tbe - 0.1, t0 => { const hit = tc - 0.35, k = ease(prog(t, hit, 0.2)), sh = t > hit && t < hit + 0.4 ? 10 * (1 - (t - hit) / 0.4) : 0;
      cam(t, t0, ti - t0, 1.0, 1.1, 960, 640, () => { ctx.translate(Math.sin(t * 90) * sh, 0); floorLine();
        if (k < 0.5) { you(760, FL, 1.05, { dir: 1, hand: [800 - 40 * prog(t, t0, 0.6), 380 - 60 * prog(t, t0, 0.6)] }); dog(lerp(1250, 900, k * 2), FL, 1.05, { dir: -1, crouch: 1 - k * 2, rear: k, smile: 1 }); }
        else { you(860, FL, 1.05, { pose: 'back', dir: 1 }); dog(820, FL - 40, 1.1, { dir: 1, crouch: 0.4, smile: 1, eye: 1 }); } }); }],
    [ti - 0.1, t0 => { focus(t, t0, segEnd(seg) - t0 + 0.4, 1.0, 1.12, 960, 520, () => {
      dogFace(960, 420, 1.15, { smile: lerp(0.85, 1, prog(t, tsm, 0.5)), eye: 1 });
      glow('rgba(255,255,255,0.25)', 16); pth('M300,1100 C420,860 620,800 960,800 C1300,800 1500,860 1620,1100 Z', C.fig); noGlow(); });
      flatT(() => { ctx.save(); redGlow(12); ln(1560, 520, 1560, 740, 5, C.red); ln(1530, 520, 1590, 520, 5, C.red); ln(1530, 740, 1590, 740, 5, C.red); ctx.restore(); bigTag(t, t0 + 0.3, '1 INCH', 1560, 460, C.red, 44); }); }],
  ]);
};
S.d9 = (t, seg) => {
  // the one thing that works: it copies you
  const tr = wt(seg, 'remember'), tc = wt(seg, 'copies');
  black();
  if (t < tr - 0.1) cam(t, seg.start, tr - seg.start, 1.0, 1.04, 960, 520, () => okRow(t, seg.start + 0.1, 600, 520, 'ONE THING WORKS', 72));
  else cam(t, tr - 0.1, segEnd(seg) - tr, 1.0, 1.06, 960, 560, () => { floorLine();
    you(620, FL, 1.1, { dir: 1 }); dog(1300, FL, 1.1, { dir: -1, sit: 1 });
    ctx.save(); ctx.setLineDash([16, 14]); ctx.lineDashOffset = t * 60; ln(680, 470, 1180, 520, 5, C.fig); ctx.restore();
    bigTag(t, tc - 0.1, 'IT COPIES YOU', 960, 320, C.fig, 52); });
};
S.d10 = (t, seg) => {
  // give it something else to copy: be the dog
  const tb = wt(seg, 'be');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 960, 560, () => { floorLine();
    const k = ease(prog(t, tb - 0.2, 0.5));
    if (k < 0.5) you(860, FL, 1.15, { dir: 1 }); else you(860, FL, 1.15, { pose: 'fours', dir: 1 });
    if (t >= tb) pop(t, tb, 960, 250, () => { ctx.save(); glow('rgba(255,255,255,0.4)', 20); text('BE THE DOG.', 960, 280, '900 120px M', C.fig); ctx.restore(); }, 0.35);
  });
};
S.d11 = (t, seg) => {
  // all fours, lips back, teeth, growl. Louder.
  const tl = wt(seg, 'pull'), tt = wt(seg, 'show'), tg = wt(seg, 'growl'), tlo = wt(seg, 'loud');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.1, 820, 600, () => { floorLine();
    you(720, FL, 1.3, { pose: 'fours', dir: 1, lunge: t >= tg ? 0.5 + 0.5 * Math.sin(t * 9) : 0 });
    growlArcs(720 + 140 * 1.3 + 60, FL - 214 * 1.3, t, 1, t >= tlo ? C.red : C.fig, t >= tlo ? 1.5 : 1, prog(t, tg - 0.1, 0.2));
  });
  flatT(() => { const x = 1240; okRow(t, seg.start + 0.1, x, 230, 'ALL FOURS', 40); okRow(t, tl - 0.1, x, 370, 'LIPS BACK', 40); okRow(t, tt - 0.1, x, 510, 'TEETH', 40); okRow(t, tg - 0.1, x, 650, 'GROWL', 40); });
};
S.d12 = (t, seg) => {
  // it hesitates; then it copies you, down onto four legs
  const th = wt(seg, 'hesitates'), tth = wt(seg, 'then'), tc = wt(seg, 'copies');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 580, () => { floorLine();
    you(560, FL, 1.05, { pose: 'fours', dir: 1, lunge: 0.4 + 0.4 * Math.sin(t * 9) });
    const down = ease(prog(t, tc - 0.3, 0.9));
    dog(1360, FL, 1.12, { dir: -1, rear: 1 - down, crouch: down, head: t < tth ? Math.sin(t * 3) * 0.12 + 0.15 : 0, smile: 1 - down * 0.7 });
    growlArcs(560 + 147 + 60, FL - 225, t, 1, C.fig, 0.9, 1);
  });
};
S.d13 = (t, seg) => {
  // face to face, both growling; the more it copies a dog, the less room for you
  const tl = wt(seg, 'lips'), tg = wt(seg, 'growls'), tm = wt(seg, 'more'), tr = wt(seg, 'room');
  black();
  if (t < tm - 0.1) cam(t, seg.start, tm - seg.start, 1.0, 1.08, 960, 600, () => { floorLine();
    you(520, FL, 1.05, { pose: 'fours', dir: 1, lunge: 0.4 + 0.4 * Math.sin(t * 9) });
    dog(1400, FL, 1.05, { dir: -1, crouch: 1, smile: t >= tl ? 1 : 0.4 });
    growlArcs(520 + 147 + 60, FL - 225, t, 1, C.fig, 0.9, 1);
    growlArcs(1400 - 220 - 40, FL - 240, t + 0.3, -1, C.fig, 0.9, prog(t, tg, 0.2));
  });
  else cam(t, tm - 0.1, segEnd(seg) - tm, 1.0, 1.06, 960, 560, () => { floorLine();
    dog(980, FL, 1.4, { dir: 1, crouch: 1 });
    const left = lerp(1, 0.2, ease(prog(t, tr - 0.4, 1.4)));
    insideMe(880, FL - 220, 1.05 * (0.4 + 0.6 * left), left);
    flatT(() => meter(560, 140, 700, 'YOU, INSIDE IT', left));
  });
};
S.d14 = (t, seg) => {
  // one by one the human teeth fall out; click, click, click; sharp dog teeth slide back in
  const clicks = [wt(seg, 'click', 1), wt(seg, 'click', 2), wt(seg, 'click', 3)], tf = wt(seg, 'onto'), tsh = wt(seg, 'sharp');
  black();
  const lostAt = tt => { let n = 0; const st = seg.start + 0.6; if (tt > st) n = Math.min(4, (tt - st) / 0.5); for (const c of clicks) if (tt > c) n += 2; return Math.min(10, n); };
  if (t < tf - 0.1 || t >= tsh - 0.1) {
    const fang = prog(t, tsh, 0.8);
    cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.08, 960, 560, () => {
      dogFace(960, 460, 1.2, { smile: 1, lost: t >= tsh - 0.1 ? 10 : lostAt(t), fang, snarl: 1 });
      // falling teeth
      for (let j = 0; j < 10; j++) { const i = TOOTH_ORDER[j];
        let tj = j < 4 ? seg.start + 0.6 + j * 0.5 : clicks[Math.floor((j - 4) / 2)] + (j % 2) * 0.08;
        const dt = t - tj; if (dt < 0 || dt > 1.4) continue;
        const [lx, ly] = toothPos(i, j % 2), x = 960 + lx * 1.2 + (j - 5) * 12 * dt, y = 460 + ly * 1.2 + 900 * dt * dt;
        looseTooth(x, y, 1.1, dt * (j % 2 ? 4 : -4)); }
    });
  } else {
    focus(t, tf - 0.1, tsh - tf, 1.0, 1.08, 960, 800, () => { floorLine(900, '#3a3a3a');
      for (let j = 0; j < 10; j++) looseTooth(560 + hash(j * 3.3) * 800, 880 - hash(j * 1.7) * 30, 1.0, hash(j) * 6); });
  }
};
S.d15 = (t, seg) => {
  // bark, it barks; scratch behind your ear, it scratches; don't stop until the last tooth hits the floor
  const tb = wt(seg, 'bark'), tbs = wt(seg, 'barks'), tsc = wt(seg, 'scratch'), tss = wt(seg, 'scratches'), td = wt(seg, 'do'), tl = wt(seg, 'hits');
  black();
  if (t < td - 0.1) cam(t, seg.start, td - seg.start, 1.0, 1.06, 960, 600, () => { floorLine();
    const sc = t >= tsc && t < tss + 1.4;
    you(520, FL, 1.05, { pose: 'fours', dir: 1, hand: sc ? [520 + 120, FL - 300 + Math.sin(t * 28) * 14] : null, lunge: 0.3 });
    dog(1400, FL, 1.05, { dir: -1, crouch: 0.3, scratch: t >= tss ? 1 : 0, t });
    if (t >= tb && t < tb + 0.9) growlArcs(520 + 147 + 60, FL - 225, t, 1, C.fig, 1.1, 1 - prog(t, tb + 0.5, 0.4));
    if (t >= tbs && t < tbs + 0.9) growlArcs(1400 - 220 - 40, FL - 240, t, -1, C.fig, 1.1, 1 - prog(t, tbs + 0.5, 0.4));
  });
  else focus(t, td - 0.1, segEnd(seg) - td + 0.4, 1.0, 1.15, 960, 800, () => { floorLine(900, '#3a3a3a');
    for (let j = 0; j < 9; j++) looseTooth(560 + hash(j * 3.3) * 800, 880 - hash(j * 1.7) * 30, 1.0, hash(j) * 6);
    const k = clamp((t - (tl - 0.5)) / 0.5), y = lerp(100, 878, k * k);
    looseTooth(1020, y, 1.2, k * 3);
    if (t >= tl) ripple(1020, 890, tl, t, C.red, 20, 160, 5);
  });
};
S.d16 = (t, seg) => {
  // the question only a real dog cannot answer
  const tw = wt(seg, "who's");
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 960, 560, () => { floorLine();
    you(640, FL, 1.05, { pose: 'kneel', dir: 1, hand: [820, 600] }); dog(1260, FL, 1.05, { dir: -1, sit: 1 });
    if (t >= tw - 0.1) say(t, tw - 0.1, 760, 230, "WHO'S A GOOD BOY?", 660, 400, 56);
  });
};
S.d17 = (t, seg) => {
  // it does not say "I am"; it just wags its tail
  const tj = wt(seg, 'just');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.06, 1100, 560, () => { floorLine();
    dog(1100, FL, 1.25, { dir: -1, sit: t >= tj ? 0 : 1, wag: t >= tj ? t * 18 : 0 });
    if (t < tj + 0.4) { say(t, seg.start + 0.2, 1500, 300, 'I AM.', 1260, 460, 60, { red: true }); redX(1500, 300, 90, prog(t, seg.start + 0.9, 0.3)); }
  });
};

// ---------- the morning ----------
S.e1 = (t, seg) => {
  // morning: asleep in its own bed, normal teeth, normal dog
  const tn = wt(seg, 'normal'), tn2 = wt(seg, 'normal', 2);
  black();
  focus(t, seg.start, segEnd(seg) - seg.start, 1.5, 1.65, 1000, 700, () => { floorLine();
    rrS(1340, 220, 300, 300, 6, '#5a5a5a', 4); icon('sun', 1490, 370, 1.1);
    dogBed(900, 1.2); ctx.save(); ctx.translate(900, FL - 30); ctx.scale(1.15, 1.15); glow('rgba(255,255,255,0.25)', 14); ell(0, -40, 150, 52, 0, C.fig); ctx.restore(); noGlow();
    ctx.save(); ctx.translate(1060, FL - 100); ctx.scale(0.85, 0.85); dogHead({ close: true }); ctx.restore();
  });
  flatT(() => { okRow(t, tn - 0.1, 160, 220, 'NORMAL TEETH', 40); okRow(t, tn2 - 0.1, 160, 370, 'NORMAL DOG', 40); });
};
S.e2 = (t, seg) => {
  // brushing your teeth; you smile at the mirror
  const ts = wt(seg, 'smile');
  black();
  cam(t, seg.start, segEnd(seg) - seg.start, 1.0, 1.1, 960, 480, () => {
    mirrorFrame(560, 120, 800, 620, { inner: () => { glow('rgba(255,255,255,0.25)', 14); circ(960, 420, 120, C.fig); rr(820, 560, 280, 260, 60, C.fig); noGlow();
      ctx.save(); ctx.translate(1100, 470); ctx.rotate(-0.6); rr(-10, -10, 160, 20, 8, '#9a9a9a'); rr(-40, -16, 40, 32, 6, '#cfcfcf'); ctx.restore(); } });
    rr(480, 760, 960, 40, 8, C.fig); ln(960, 800, 960, 860, 30, '#8a8a8a');
  });
};
S.e3 = (t, seg) => {
  // top row, left side: one tooth is long, sharp, and not yours
  const tl = wt(seg, 'left'), to = wt(seg, 'one'), tsh = wt(seg, 'sharp');
  black();
  focus(t, seg.start, segEnd(seg) - seg.start + 0.6, 1.0, 1.25, lerp(960, 760, ease(prog(t, tl, 0.6))), 460, () => {
    teethRow(960, 400, 1.15, { fangAt: 2, fang: ease(prog(t, to, 1.4)) });
    if (t >= tsh) { ctx.save(); redGlow(16); circS(960 - 5 * 76 * 1.15 + 2.5 * 76 * 1.15, 520, 120, C.red, 6); ctx.restore(); }
  });
};
S.e4 = (t, seg) => {
  // it copied you; for a few minutes last night, you copied it
  const ty = wt(seg, 'you', 2);
  black();
  cam(t, seg.start, segEnd(seg) - seg.start + 0.4, 1.0, 1.06, 960, 560, () => { floorLine();
    you(620, FL, 1.1, { dir: 1, red: t >= ty ? 0.8 : 0 }); dog(1300, FL, 1.1, { dir: -1, sit: 1 });
    const arr = (x0, x1, y, col, p) => { if (p <= 0) return; ctx.save(); if (col === C.red) redGlow(14); lnP(x0, y, x1, y, 10, col, p); if (p >= 1) { ctx.translate(x1, y); ctx.scale(Math.sign(x1 - x0), 1); pth('M0,-24 L32,0 L0,24 Z', col); } ctx.restore(); };
    arr(1180, 760, 380, C.fig, prog(t, seg.start + 0.3, 0.5));
    arr(760, 1180, 470, C.red, prog(t, ty, 0.5));
  });
};
S.e5 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore();
  });
};
S.e6 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts, dk = ease(prog(t, ts + 0.5, 1.0));
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9] });
    if (dk > 0) { ctx.save(); ctx.globalAlpha = 0.5 * dk; ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
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

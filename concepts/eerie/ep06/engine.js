// Protocol 404, EP05 "If Your AI Job Interview Ever Asks Who Else Is In The Room". Canvas renderer: window.draw(t).
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
    for (let i = 0; i < 5; i++) { const x = 560 + i * 54, y = 618 + dy; ctx.save(); ctx.globalAlpha *= prog(t, t0 + 0.4 + i * 0.06, 0.2);
      if (i + 1 <= n) rr(x, y, 38, 38, 5, i + 1 === n ? C.fig : C.mid); else rrS(x, y, 38, 38, 5, i === 4 ? C.red : C.mid, 3); ctx.restore(); }
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
    slideIn(t, t0, -60, 0, () => { redGlow(30 + 14 * Math.sin(t * 7)); rr(380, 330, 230, 230, 14, C.red); noGlow(); pageIcon('warn', 495, 452, '#000'); });
    slideIn(t, t0 + 0.08, 60, 0, () => { spaced('LAST RESORT', 650, 390, '900 40px M', C.mid, 14, 'left'); });
    if (t >= te - 0.05) pop(t, te - 0.05, 1060, 470, () => { redGlow(22); spaced('EMERGENCY PROTOCOL', 650, 490, '900 80px M', C.red, 6, 'left'); noGlow(); });
    if (t >= th - 0.05) pop(t, th - 0.05, 1000, 610, () => { spaced('HOW TO FIGHT BACK', 650, 630, '900 64px M', C.fig, 8, 'left'); });
    for (let i = 0; i < 5; i++) { const x = 380 + i * 54, y = 700; ctx.save(); ctx.globalAlpha *= prog(t, t0 + 0.4 + i * 0.06, 0.2);
      rr(x, y, 38, 38, 5, i === 4 ? C.red : C.mid); ctx.restore(); }
  });
  if (t >= te) { ctx.save(); ctx.globalAlpha = 0.1 * (0.5 + 0.5 * Math.sin((t - te) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
}
// ---------- scenes ----------
const S = {};
const P = { x: 510, y: 110, w: 900, h: 800 };
// left-aligned text shrunk to fit a width
function fitText(str, x, y, maxW, size, col) { ctx.font = `900 ${size}px M`; const w = ctx.measureText(str).width; if (w > maxW) size = Math.floor(size * maxW / w); text(str, x, y, `900 ${size}px M`, col, 'left'); }
const ROWY = i => P.y + 140 + i * 128;
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
  const rows = [['SUBJECT', null], ['LOCATION', 'YOUR STREET'], ['TIME', 'OCT 31, 11 PM']];
  rows.forEach(([l, v], i) => { const y = P.y + 270 + i * 82;
    text(l, P.x + 60, y, '600 28px Plex', '#666', 'left'); ln(P.x + 250, y + 12, P.x + P.w - 60, y + 12, 2, '#bbb');
    if (v === null) rr(P.x + 260, y - 30, 330, 40, 3, '#111');
    else { ctx.save(); ctx.filter = 'blur(9px)'; text(v, P.x + 262, y, '900 36px M', i === 2 ? '#d61f1f' : '#111', 'left'); ctx.restore(); } });   // classified: blurred
  // barcode and a hazard edge
  for (let i = 0; i < 40; i++) { const bw = hash(i * 1.7) < 0.35 ? 6 : 3; rr(P.x + P.w - 300 + i * 6.4, P.y + P.h - 170, bw, 70, 0, '#111'); }
  text('NO. 0' + NUM, P.x + P.w - 172, P.y + P.h - 74, '600 24px Plex', '#444');
  text('DO NOT LOOK AWAY', P.x + 60, P.y + P.h - 130, '600 22px Plex', '#666', 'left');
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
  if (name === 'turn') { circ(0, -24, 16, col); rr(-18, -4, 36, 46, 10, col); ctx.beginPath(); ctx.arc(0, -10, 40, 3.6, 5.9); ctx.lineWidth = 6; ctx.strokeStyle = col; ctx.stroke(); pth('M36,-36 L48,-14 L24,-16 Z', col); }
  if (name === 'knives') { ctx.save(); ctx.rotate(-0.45); for (let i = 0; i < 4; i++) { if (i === 2) rrS(-30 + i * 18, -50, 12, 36, 4, col === '#fff' ? '#fff' : C.red, 3); else rr(-30 + i * 18, -50, 12, 36, 4, col); } ctx.restore(); pth('M-46,46 L40,46 L36,6 L-6,-34 L-48,-18 Z', col); }
  if (name === 'closet') { rrS(-36, -48, 72, 96, 4, col, 5); ln(0, -48, 0, 48, 4, col); for (let i = 0; i < 5; i++) { ln(-28, -36 + i * 16, -6, -32 + i * 16, 4, col); ln(6, -36 + i * 16, 28, -32 + i * 16, 4, col); } }
  if (name === 'rise') { rr(-50, 34, 100, 6, 3, col); circ(-32, 18, 13, col); rr(-16, 8, 62, 20, 8, col); ln(-32, 0, -32, -30, 6, col); pth('M-44,-26 L-32,-46 L-20,-26 Z', col); }
  if (name === 'fist') { rr(-34, -34, 68, 64, 18, col); for (let i = 1; i < 4; i++) ln(-34 + i * 17, -34, -34 + i * 17, -10, 3, '#ff2b2b'); }
  ctx.restore();
}
const RULES = [['eye', 'DO NOT LOOK AWAY', ''], ['knives', 'COUNT THE KNIVES', ''], ['closet', 'DO NOT HIDE IN THE CLOSET', '', ['DO NOT HIDE', 'IN THE CLOSET']], ['rise', "NEVER CHECK IF HE'S DEAD", '', ['NEVER CHECK', "IF HE'S DEAD"]], ['warn', 'EMERGENCY PROTOCOL', 'HOW TO FIGHT BACK']];
// the index page. o.rowT[i]: when row i slides in; o.fillT[i]: when its content is written; o.hot: rule 4 armed 0..1; o.struck[i]; o.dim
function rulePage(t, o) {
  const pc = '#ececec';
  glow('rgba(255,255,255,0.2)', 30); rr(P.x, P.y, P.w, P.h, 8, pc); noGlow();
  for (let i = 0; i < 3; i++) circ(P.x + 26, P.y + 220 + i * 230, 10, '#0b0b0b');
  text(NAME + ' ' + NUM, P.x + 60, P.y + 72, '900 42px M', '#111', 'left');
  ln(P.x + 60, P.y + 102, P.x + P.w - 50, P.y + 102, 5, '#111');
  for (let i = 0; i < 5; i++) {
    const t0 = o.rowT[i]; if (t < t0) continue;
    const y = ROWY(i), four = i === 4, k = easeOut((t - t0) / 0.35);
    ctx.save(); ctx.globalAlpha *= clamp(k * 2) * (o.dim && !four ? lerp(1, 0.32, o.dim) : 1); ctx.translate(40 * (1 - k), 0);
    const hot = four ? (o.hot || 0) : 0;
    if (hot > 0) { ctx.save(); ctx.globalAlpha *= hot; redGlow(30 + 20 * Math.sin(t * 8)); rr(P.x + 40, y - 6, P.w - 80, 122, 10, '#e02424'); noGlow();
      ctx.beginPath(); ctx.rect(P.x + 40, y - 6, P.w - 80, 122); ctx.clip(); hazard(P.x + 40, y - 6, P.w - 80, 12, t * 50); hazard(P.x + 40, y + 104, P.w - 80, 12, -t * 50); ctx.restore(); }
    rr(P.x + 60, y + 13, 84, 84, 10, four ? (hot > 0.5 ? '#111' : C.red) : '#111');
    text(four ? '!' : String(i + 1), P.x + 102, y + 79, '900 62px M', four && hot > 0.5 ? C.red : (four ? '#111' : '#fff'));
    const fill = o.fillT[i] ?? 1e9, fk = clamp((t - fill) / 0.3), ink = hot > 0.5 ? '#fff' : (four ? '#d61f1f' : '#111');
    if (t < fill) { for (let j = 0; j < 2; j++) rr(P.x + 200, y + 32 + j * 36, j ? 260 : 400, 20, 4, four ? '#111' : '#cfcfcf'); }   // redacted / blank until it is read out
    else { ctx.save(); ctx.globalAlpha *= fk; pageIcon(RULES[i][0], P.x + 236, y + 55, ink);
      if (four) fitText(RULES[i][1], P.x + 310, y + 52, P.w - 370, 46, ink);
      else {   // the three "do not" rules: one size, the long ones on two lines
        const ls = RULES[i][3] || [RULES[i][1]];
        ls.forEach((l, j) => text(l, P.x + 310, y + 70 + (j - (ls.length - 1) / 2) * 40, '900 38px M', ink, 'left')); }
      if (RULES[i][2]) text(RULES[i][2], P.x + 310, y + 94, '900 28px M', hot > 0.5 ? '#111' : '#444', 'left'); ctx.restore(); }
    if (o.struck && o.struck[i] != null && t >= o.struck[i]) { ctx.save(); redGlow(12); lnP(P.x + 50, y + 62, P.x + P.w - 50, y + 48, 10, C.red, easeOut((t - o.struck[i]) / 0.18)); ctx.restore(); }
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
  const rows = [tf, tf + 0.14, tf + 0.28, tf + 0.42, tf + 0.56];
  // "otherwise": push in on rule 4 and arm it
  const zk = ease((t - to) / 0.9), z = lerp(1.0, 1.32, zk), fy = lerp(520, ROWY(4) + 56, zk), hot = prog(t, ta - 0.05, 0.3);
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
  const k = ease((t - tc) / 0.5), y = lerp(ROWY(prev) + 56, ROWY(row) + 56, k);
  ctx.save(); ctx.translate(W / 2, 520); ctx.scale(z, z); ctx.translate(-960, -y); fn(); ctx.restore();
}// ---------- EP06 props: Halloween night, the man in the white mask ----------
// Flat 2D pictograms. Everything dark and white; warm amber only for lamps and pumpkin light; red only for danger.
const NIGHT = { sky0: '#06080c', sky1: '#000', house: '#111214', houseHi: '#26272b', roof: '#0b0b0d', street: '#0c0c0e', walk: '#151517', grass: '#090b09',
  amber: '#ffc36b', jump: '#2a323f', jumpHi: '#4a5568', jumpLo: '#1b212b', mask: '#eef0ed', maskSh: '#b7bbbb', hair: '#2b2119', hairHi: '#4b3b2c' };
const amberGlow = (b = 24) => glow('rgba(255,180,90,0.85)', b);

// ---------- the man ----------
// front view, feet at (x,y), 600 units tall at s=1. o.tilt (rad, head), o.knife: 0 none, 1 low at his side, 2 raised; o.wave 0..1 (left hand up);
// o.walk: step phase (rad) or null; o.back: seen from behind; o.red 0..1 (eyes); o.dark 0..1 (body sinks into the dark, only the mask stays);
// o.lower 0..1 (raised knife comes down); o.handsEmpty: show both open hands
function myers(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const dk = o.dark || 0, body = o.bodyCol || NIGHT.jump, edge = `rgba(150,158,170,${0.55 * (1 - dk)})`;
  const sw = o.walk != null ? Math.sin(o.walk) : 0;
  ctx.save(); ctx.globalAlpha *= 1 - 0.75 * dk;
  // legs
  for (const d of [-1, 1]) {
    const lift = o.walk != null ? Math.max(0, d * sw) * 18 : 0, fx = d * 34 + (o.walk != null ? d * sw * 10 : 0);
    ctx.beginPath(); ctx.moveTo(d * 8, -300); ctx.lineTo(d * 62, -300); ctx.lineTo(fx + d * 24, -22 - lift); ctx.lineTo(fx - d * 22, -22 - lift); ctx.closePath();
    ctx.fillStyle = body; ctx.fill(); ctx.strokeStyle = edge; ctx.lineWidth = 3; ctx.stroke();
    ln(d * 36 - 14, -150, d * 36 + 12, -144, 2, NIGHT.jumpLo); ln(d * 36 - 10, -136, d * 36 + 8, -132, 2, NIGHT.jumpLo);   // creases at the knee
    rr(fx - 30, -30 - lift, 60, 30, 10, '#121315');                                       // boots
  }
  // torso: work coveralls, wide shoulders
  const torso = new Path2D('M-78,-500 C-90,-470 -84,-380 -66,-290 L66,-290 C84,-380 90,-470 78,-500 C40,-512 -40,-512 -78,-500 Z');
  ctx.fillStyle = body; ctx.fill(torso); ctx.strokeStyle = edge; ctx.lineWidth = 3; ctx.stroke(torso);
  if (!o.back) {
    ln(0, -470, 0, -300, 3, '#59627a'); rr(-4, -462, 8, 16, 2, '#7a8296');                                   // zip and its pull
    for (const d of [-1, 1]) {
      pth(`M${d * 4},-506 L${d * 46},-508 L${d * 40},-476 L${d * 2},-462 Z`, NIGHT.jumpHi);              // pointed collar
      pthS(`M${d * 4},-506 L${d * 46},-508 L${d * 40},-476 L${d * 2},-462`, NIGHT.jumpLo, 2);
      rr(d > 0 ? 18 : -60, -446, 42, 44, 4, NIGHT.jumpLo); rr(d > 0 ? 16 : -62, -450, 46, 14, 3, '#151a22');   // chest pockets with flaps
      ln(d * 60, -340, d * 30, -330, 2, NIGHT.jumpLo);                                                  // a fold at the hip
    }
  }
  else ln(0, -505, 0, -300, 2, NIGHT.jumpLo);
  rr(-68, -304, 136, 10, 3, NIGHT.jumpLo); for (let i = -5; i <= 5; i++) ln(i * 12, -306, i * 12, -296, 1.5, '#151a22');   // elastic waist
  // arms: shoulder -> elbow -> hand; returns the knife hand position
  const arm = (d, hand, elbow) => { ctx.beginPath(); ctx.moveTo(d * 70, -492); ctx.lineTo(elbow[0], elbow[1]); ctx.lineTo(hand[0], hand[1]);
    ctx.lineWidth = 38; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = body; ctx.stroke();
    ctx.lineWidth = 3; ctx.strokeStyle = edge; ctx.stroke(); circ(hand[0], hand[1], 19, '#cfcdc4'); };
  // his right hand (screen left)
  let kh = null, kAng = Math.PI / 2;
  const raise = o.knife === 2 ? 1 - (o.lower || 0) : 0;
  if (o.knife) {
    const hx = lerp(-96, -60, raise), hy = lerp(-270, -640, raise), ex = lerp(-100, -132, raise), ey = lerp(-385, -520, raise);
    kh = [hx, hy]; kAng = lerp(Math.PI / 2, -Math.PI / 2 - 0.1, raise);
    arm(-1, kh, [ex, ey]);
  } else arm(-1, [-96 + (o.walk != null ? -sw * 14 : 0), -268], [-102, -385]);
  // left hand (screen right): down, or waving
  const wv = o.wave || 0;
  if (wv > 0) { const wob = Math.sin((o.waveT || 0) * 7) * 0.5 * clamp(wv * 2 - 1);
    const hx = lerp(96, 120 + wob * 40, wv), hy = lerp(-268, -600, wv); arm(1, [hx, hy], [lerp(102, 150, wv), lerp(-385, -470, wv)]);
    if (wv > 0.6) for (let i = 0; i < 4; i++) { const a = -2.2 + i * 0.32 + wob * 0.3; ln(hx + Math.cos(a) * 12, hy + Math.sin(a) * 12, hx + Math.cos(a) * 42, hy + Math.sin(a) * 42, 9, '#cfcdc4'); } }
  else arm(1, [96 + (o.walk != null ? sw * 14 : 0), -268], [102, -385]);
  ctx.restore();
  // the knife: dark handle, long pale blade with a glint
  if (kh) knife(kh[0], kh[1], kAng, 1, { red: o.knifeRed });
  // head
  ctx.save(); ctx.translate(0, -505); ctx.rotate(o.tilt || 0);
  rr(-20, -24, 40, 30, 8, body);                                                            // neck / collar
  maskHead(0, -58, 1, o);
  ctx.restore();
  ctx.restore();
}
// the mask, centred at (x,y): the pale latex face from the film (long face, high cheekbones, thin straight nose,
// hollow almond eyes under heavy lids, thin closed lips), the mask's neck tucked into the collar, messy brown hair swept back
function maskHead(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const SH = a => `rgba(55,64,74,${a})`, HAIR = NIGHT.hair, HI = NIGHT.hairHi;
  // hair behind: full, wavy
  pth('M-62,-4 C-76,-40 -70,-94 -32,-112 C-6,-124 32,-122 54,-102 C74,-82 74,-36 64,-4 C62,8 56,16 50,20 L-50,20 C-58,14 -62,6 -62,-4 Z', HAIR);
  if (o.back) { pth('M-58,-50 C-60,0 -48,40 0,60 C48,40 60,0 58,-50 C46,-96 -46,-96 -58,-50 Z', HAIR);
    ctx.save(); ctx.globalAlpha *= 0.6; for (let i = 0; i < 7; i++) { const a = -44 + i * 15; pthS(`M${a},-80 C${a + 6},-40 ${a - 4},0 ${a + 2},40`, HI, 3); } ctx.restore(); ctx.restore(); return; }
  // the mask's neck, going into the collar
  rr(-25, 46, 50, 56, 12, '#c4c8c7');
  // the face
  glow(`rgba(255,255,255,${o.glowA ?? 0.32})`, o.glowB ?? 28);
  const face = new Path2D('M0,-90 C26,-90 44,-76 45,-52 C47,-30 48,-12 46,4 C44,22 38,40 30,54 C24,66 16,78 0,82 C-16,78 -24,66 -30,54 C-38,40 -44,22 -46,4 C-48,-12 -47,-30 -45,-52 C-44,-76 -26,-90 0,-90 Z');
  const g = ctx.createLinearGradient(-48, 0, 48, 0); g.addColorStop(0, '#c3c7c6'); g.addColorStop(0.22, '#e8eae7'); g.addColorStop(0.5, NIGHT.mask); g.addColorStop(0.78, '#e8eae7'); g.addColorStop(1, '#c3c7c6');
  ctx.fillStyle = g; ctx.fill(face); noGlow();
  // sculpted shading, soft, kept inside the face
  ctx.save(); ctx.clip(face); ctx.filter = `blur(${Math.max(1, 5 * s)}px)`;
  for (const d of [-1, 1]) {
    ell(d * 32, 32, 12, 24, d * 0.35, SH(0.22));                 // cheek hollows under the cheekbones
    ell(d * 44, -40, 9, 24, 0, SH(0.2));                         // temples
    ell(d * 19, -22, 18, 12, d * 0.08, SH(0.32));                // eye sockets
    ell(d * 9, 2, 5, 18, d * 0.1, SH(0.16));                     // sides of the nose
    ell(d * 17, 40, 5, 12, d * -0.3, SH(0.14));                  // beside the mouth
    ell(d * 30, -2, 12, 7, d * -0.4, 'rgba(255,255,255,0.5)');   // cheekbones catch the light
  }
  ell(0, 86, 42, 16, 0, SH(0.26)); ell(0, 56, 9, 4, 0, SH(0.2)); ell(0, -62, 22, 10, 0, 'rgba(255,255,255,0.45)');
  ctx.filter = 'none'; ctx.restore();
  for (const d of [-1, 1]) {
    pthS(`M${d * 34},-36 C${d * 26},-41 ${d * 13},-41 ${d * 6},-35`, SH(0.3), 3);            // brow ridge
    pthS(`M${d * 7},-26 C${d * 14},-32 ${d * 26},-32 ${d * 33},-21`, SH(0.28), 2);           // heavy upper lid
    pth(`M${d * 7},-20 C${d * 12},-28 ${d * 26},-28 ${d * 32},-16 C${d * 25},-12 ${d * 12},-12 ${d * 7},-20 Z`, '#040404');   // the eye hole, drooping at the outside
    ell(d * 6, 22, 3.4, 1.8, 0, 'rgba(35,38,42,0.6)');                                      // nostrils
    const r = o.red || 0;
    if (r > 0) { ctx.save(); ctx.globalAlpha *= r; redGlow(16); circ(d * 19, -19, 3.2, C.red); noGlow(); ctx.restore(); }
  }
  ctx.save(); ctx.globalAlpha *= 0.6; ln(0, -34, 0, 12, 5, '#ffffff'); ctx.restore();         // the bridge catches the light
  pthS('M-11,19 C-6,24 6,24 11,19', SH(0.3), 2);                                               // tip of the nose
  pth('M-15,45 C-8,41 -3,42 0,43 C3,42 8,41 15,45 C8,46 -8,46 -15,45 Z', SH(0.28));            // thin upper lip
  pthS('M-15,45 C-6,47 6,47 15,45', '#4a4e53', 1.8);                                           // closed
  // hair over the top: high hairline, thick and messy, swept back, loose at the temples
  pth('M-52,-40 C-60,-84 -36,-114 2,-114 C40,-114 64,-88 53,-40 C49,-56 42,-68 32,-73 C27,-81 16,-84 6,-81 C-4,-86 -18,-84 -25,-77 C-35,-75 -46,-62 -52,-40 Z', HAIR);
  for (const d of [-1, 1]) pth(`M${d * 44},-60 C${d * 54},-46 ${d * 52},-26 ${d * 48},-14 C${d * 46},-28 ${d * 45},-42 ${d * 40},-54 Z`, HAIR);
  ctx.save(); ctx.globalAlpha *= 0.8;
  for (const [a, b] of [[-44, -92], [-30, -104], [-12, -110], [8, -110], [26, -104], [42, -92]]) pthS(`M${a},${b} C${a + 6},${b + 6} ${a + 4},${b + 14} ${a + 10},${b + 18}`, HI, 2.5);
  ctx.restore();
  ctx.restore();
  ctx.restore();
}
// a kitchen knife: handle at (x,y), blade pointing along ang
function knife(x, y, ang, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s);
  rr(-34, -9, 40, 18, 5, '#1b1b1d'); circ(-22, 0, 2.5, '#777'); circ(-8, 0, 2.5, '#777');
  glow(o.red ? 'rgba(255,43,43,0.8)' : 'rgba(255,255,255,0.35)', o.red ? 18 : 12);
  pth('M8,-11 L120,-6 C134,-4 140,2 146,8 L8,11 Z', o.red ? '#ffdede' : '#e9e9e9'); noGlow();
  ln(20, -6, 118, -3, 2, 'rgba(255,255,255,0.9)');
  ctx.restore();
}

// ---------- you, the neighbours, the kids ----------
// a flat white person; feet at (x,y), 360 tall at s=1. o.face: 'front' (two eyes, no mouth) | 'back' | 'left' | 'right'; o.arms: [l, r] raise 0..1; o.walk phase
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
  const f = o.face || 'front';
  if (f === 'front') { circ(-12, -344, 5.5, '#000'); circ(12, -344, 5.5, '#000'); }
  if (f === 'left') circ(-18, -344, 5.5, '#000');
  if (f === 'right') circ(18, -344, 5.5, '#000');
  ctx.restore();
}
// trick-or-treaters: kind 'ghost' | 'witch' | 'kid'; feet at (x,y), ~200 tall at s=1, bag swinging
function trickKid(x, y, s, kind, ph = 0) {
  ctx.save(); ctx.translate(x, y + Math.abs(Math.sin(ph)) * -6 * s); ctx.scale(s, s);
  glow('rgba(255,255,255,0.22)', 10);
  if (kind === 'ghost') {
    pth('M-44,0 C-48,-70 -46,-170 0,-176 C46,-170 48,-70 44,0 L30,-12 L15,0 L0,-12 L-15,0 L-30,-12 Z', C.fig); noGlow();
    ell(-14, -128, 7, 10, 0, '#000'); ell(14, -128, 7, 10, 0, '#000');
  } else {
    ln(-10, -70, -12 - Math.sin(ph) * 10, 0, 16, C.fig); ln(10, -70, 12 + Math.sin(ph) * 10, 0, 16, C.fig);
    rr(-24, -150, 48, 86, 16, C.fig); circ(0, -172, 26, C.fig); noGlow();
    circ(-9, -174, 4, '#000'); circ(9, -174, 4, '#000');
    if (kind === 'witch') { pth('M-40,-188 L40,-188 L6,-268 Z', '#9a9a9a'); rr(-46, -194, 92, 10, 4, '#9a9a9a'); }
  }
  // the candy pillowcase
  const bx = 34 + Math.sin(ph) * 4; ln(26, -110, bx, -70, 6, C.sec); pth(`M${bx - 20},-74 L${bx + 22},-74 L${bx + 26},-20 C${bx + 10},-6 ${bx - 10},-6 ${bx - 24},-20 Z`, C.sec);
  ctx.restore();
}

// ---------- the street ----------
function jackO(x, y, r, lit = 1, smashed = false) {
  if (smashed) { for (let i = 0; i < 6; i++) { const a = hash(x + i) * 6.28, d = r * (0.4 + hash(i + y) * 1.2); ell(x + Math.cos(a) * d, y + 6 + Math.sin(a) * d * 0.3, r * 0.34, r * 0.16, a, '#3a3a3a'); } return; }
  ell(x, y, r * 1.25, r, 0, '#2a2a2a'); ell(x, y, r * 0.6, r, 0, '#232323'); rr(x - r * 0.1, y - r * 1.25, r * 0.2, r * 0.35, 3, '#3a3a3a');
  if (lit > 0) { ctx.save(); ctx.globalAlpha *= lit; amberGlow(r * 0.8);
    pth(`M${x - r * 0.62},${y - r * 0.22} L${x - r * 0.3},${y - r * 0.22} L${x - r * 0.46},${y - r * 0.52} Z M${x + r * 0.62},${y - r * 0.22} L${x + r * 0.3},${y - r * 0.22} L${x + r * 0.46},${y - r * 0.52} Z M${x - r * 0.7},${y + r * 0.2} L${x + r * 0.7},${y + r * 0.2} L${x + r * 0.4},${y + r * 0.5} L${x + r * 0.15},${y + r * 0.34} L${x - r * 0.15},${y + r * 0.5} L${x - r * 0.4},${y + r * 0.34} Z`, NIGHT.amber);
    noGlow(); ctx.restore(); }
}
// a house: base centre (x, y), width w; o.win: lit amount per window [4]; o.porch: porch light; o.pumpkins; o.old (empty house: boards, no light); o.door 0..1 open
function house(x, y, w, o = {}) {
  const h = w * 0.62, l = x - w / 2;
  ctx.save();
  // roof
  ctx.beginPath(); ctx.moveTo(l - w * 0.06, y - h); ctx.lineTo(x, y - h - w * 0.38); ctx.lineTo(l + w * 1.06, y - h); ctx.closePath(); ctx.fillStyle = NIGHT.roof; ctx.fill(); ctx.strokeStyle = NIGHT.houseHi; ctx.lineWidth = 3; ctx.stroke();
  if (o.chimney !== false) rr(x + w * 0.22, y - h - w * 0.36, w * 0.08, w * 0.2, 2, NIGHT.roof);
  rr(l, y - h, w, h, 0, o.old ? '#0d0d0e' : NIGHT.house); rrS(l, y - h, w, h, 0, NIGHT.houseHi, 3);
  // windows: two up, two down beside the door
  const ws = [[l + w * 0.16, y - h * 0.86], [l + w * 0.62, y - h * 0.86], [l + w * 0.1, y - h * 0.42], [l + w * 0.68, y - h * 0.42]], ww = w * 0.22, wh = h * 0.26;
  ws.forEach(([wx, wy], i) => {
    const lit = (o.win || [])[i] || 0;
    rr(wx, wy, ww, wh, 2, '#050505');
    if (lit > 0) { ctx.save(); ctx.globalAlpha *= lit; amberGlow(30); rr(wx, wy, ww, wh, 2, '#8a6a3e'); noGlow(); ctx.restore(); }
    if (o.who && o.who.win === i) { ctx.save(); ctx.beginPath(); ctx.rect(wx, wy, ww, wh); ctx.clip(); o.who.fn(wx, wy, ww, wh); ctx.restore(); }
    rrS(wx, wy, ww, wh, 2, NIGHT.houseHi, 3); ln(wx + ww / 2, wy, wx + ww / 2, wy + wh, 3, NIGHT.houseHi); ln(wx, wy + wh / 2, wx + ww, wy + wh / 2, 3, NIGHT.houseHi);
    if (o.old && i !== (o.who ? o.who.win : -1) && i % 2 === 0) { ln(wx - 6, wy + wh * 0.3, wx + ww + 6, wy + wh * 0.5, 7, '#2b2622'); ln(wx - 6, wy + wh * 0.7, wx + ww + 6, wy + wh * 0.55, 7, '#2b2622'); }
  });
  // door + steps
  const dx = x - w * 0.09, dw = w * 0.18, dh = h * 0.5;
  rr(dx, y - dh, dw, dh, 2, '#070707');
  const op = o.door || 0;
  if (op < 1) { ctx.save(); ctx.translate(dx, 0); ctx.scale(1 - op * 0.85, 1); rr(0, y - dh, dw, dh, 2, o.old ? '#16130f' : '#1d1d20'); rrS(0, y - dh, dw, dh, 2, NIGHT.houseHi, 3); circ(dw * 0.8, y - dh * 0.45, 4, '#777'); ctx.restore(); }
  rr(dx - dw * 0.3, y - 10, dw * 1.6, 10, 2, '#1a1a1c');
  if (o.porch) { ctx.save(); amberGlow(26); circ(dx + dw + 14, y - dh * 0.8, 6, NIGHT.amber); noGlow(); const g = ctx.createRadialGradient(dx + dw + 14, y - dh * 0.8, 4, dx + dw + 14, y - dh * 0.8, w * 0.35);
    g.addColorStop(0, 'rgba(255,190,110,0.18)'); g.addColorStop(1, 'rgba(255,190,110,0)'); ctx.fillStyle = g; ctx.fillRect(l - w * 0.2, y - h, w * 1.4, h + 20); ctx.restore(); }
  if (o.pumpkins) { jackO(dx - dw * 0.5, y - 12, w * 0.04, o.pumpkins, o.smashed); jackO(dx + dw * 1.5, y - 12, w * 0.032, o.pumpkins, o.smashed); }
  if (o.old) { // dead tree beside the empty house
    pthS(`M${l - w * 0.18},${y} L${l - w * 0.17},${y - h * 1.1} M${l - w * 0.17},${y - h * 0.7} L${l - w * 0.3},${y - h * 0.95} M${l - w * 0.17},${y - h * 0.9} L${l - w * 0.05},${y - h * 1.25}`, '#232323', 8); }
  ctx.restore();
}
function streetlight(x, y, s = 1, on = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (on > 0) { const g = ctx.createRadialGradient(0, -560, 10, 0, -200, 420); g.addColorStop(0, `rgba(255,250,235,${0.2 * on})`); g.addColorStop(1, 'rgba(255,250,235,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-30, -580); ctx.lineTo(30, -580); ctx.lineTo(240, 10); ctx.lineTo(-240, 10); ctx.closePath(); ctx.fill();
    ctx.save(); ctx.globalAlpha *= 0.25 * on; ell(0, 4, 230, 30, 0, '#fff7e6'); ctx.restore(); }
  rr(-7, -600, 14, 600, 4, '#2c2c30'); pthS('M0,-596 C0,-640 30,-650 60,-640', '#2c2c30', 12);
  rr(30, -650, 70, 22, 8, '#3a3a3e'); if (on > 0) { glow('rgba(255,250,235,0.9)', 30); rr(38, -632, 54, 8, 4, '#fffaf0'); noGlow(); }
  ctx.restore();
}
function mailbox(x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rr(-6, -110, 12, 110, 3, '#2a2a2c'); rr(-40, -150, 80, 46, 18, '#3a3a3e'); rrS(-40, -150, 80, 46, 18, '#55555a', 3); rr(34, -170, 6, 34, 2, '#55555a');
  ctx.restore();
}
// the view across the street. Coordinates are screen pixels at z=1. o.him: null | {x, y, s, ...myers options}; o.kids: phase; o.cam: [z, fx, fy]
function streetScene(t, o = {}) {
  const [z, fx, fy] = o.cam || [1, 960, 540], [scx, scy] = o.scr || [960, 540];
  ctx.save(); ctx.translate(scx, scy); ctx.scale(z, z); ctx.translate(-fx, -fy);
  const g = ctx.createLinearGradient(0, -200, 0, 640); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-600, -400, 3200, 1100);
  // moon and a few stars
  if (!o.morning) { ctx.save(); glow('rgba(255,255,255,0.5)', 40); circ(1560, 150, 46, '#d9d9d4'); noGlow(); ctx.restore(); }
  if (!o.morning) for (let i = 0; i < 40; i++) { const sx = hash(i * 3.3) * 2400 - 200, sy = hash(i * 5.1) * 380; ctx.save(); ctx.globalAlpha = 0.25 + 0.3 * Math.sin(t * 1.3 + i); circ(sx, sy, 1.6, '#fff'); ctx.restore(); }
  // the houses across the street
  const row = o.houses || [[-120, 0.5, [0, 0.8, 0.6, 0]], [340, 0.48, [0.7, 0, 0, 0.9]], [800, 0.5, [0, 0, 0.8, 0.6]], [1300, 0.52, [0.8, 0.5, 0, 0]], [1820, 0.5, [0, 0.7, 0.7, 0]], [2300, 0.48, [0.6, 0, 0, 0.8]]];
  row.forEach(([hx, k, win], i) => house(hx, 600, 380 * k * 2, { win: o.dimHouses ? win.map(v => v * 0.4) : win, porch: !o.morning && i % 2 === 0, pumpkins: o.morning ? 0 : 1, smashed: o.morning }));
  if (o.emptyHouse) o.emptyHouse();
  // sidewalk, street, near sidewalk, your lawn
  rr(-600, 600, 3200, 40, 0, NIGHT.walk); rr(-600, 640, 3200, 160, 0, NIGHT.street);
  for (let i = -6; i < 30; i++) rr(i * 140 + 20, 716, 70, 7, 2, '#2a2a2c');
  rr(-600, 800, 3200, 36, 0, NIGHT.walk); rr(-600, 836, 3200, 400, 0, NIGHT.grass);
  for (let i = 0; i < 90; i++) { const gx = hash(i * 1.9) * 2400 - 200, gy = 850 + hash(i * 2.7) * 220; ln(gx, gy, gx + 3, gy - 10, 2, '#151a15'); }
  if (o.extra) o.extra();
  streetlight(1100, 640, 0.95, o.light ?? 1);
  if (o.mailbox !== false) mailbox(820, 880, 1.2);
  if (o.kids != null) { const ph = o.kids; const ks = [['witch', 0], ['ghost', 210], ['kid', 330], ['ghost', 700], ['kid', 820]];
    ks.forEach(([k, off], i) => { const kx = ((off + ph * 60) % 2600) - 300; trickKid(kx, 632 - (i % 2) * 4, 0.55, k, ph * 5 + i); }); }
  if (o.him) myers(o.him.x, o.him.y, o.him.s, o.him);
  if (o.near) o.near();
  ctx.restore();
}
// your window, from inside: the dark wall around a window with curtains. o.close 0..1 (curtains drawn), o.fn draws the outside
function windowPOV(t, o = {}) {
  const X0 = o.x0 ?? 300, X1 = o.x1 ?? 1620, Y0 = o.y0 ?? 80, Y1 = o.y1 ?? 930;
  ctx.save(); ctx.beginPath(); ctx.rect(X0, Y0, X1 - X0, Y1 - Y0); ctx.clip(); o.fn && o.fn(); ctx.restore();
  // the room wall (even-odd hole)
  ctx.save(); ctx.beginPath(); ctx.rect(-200, -200, W + 400, H + 400); ctx.rect(X0, Y0, X1 - X0, Y1 - Y0); ctx.fillStyle = '#060606'; ctx.fill('evenodd'); ctx.restore();
  // frame and the cross
  rrS(X0, Y0, X1 - X0, Y1 - Y0, 2, '#2a2a2d', 22); if (o.cross !== false) { ln((X0 + X1) / 2, Y0, (X0 + X1) / 2, Y1, 14, '#1e1e21'); ln(X0, (Y0 + Y1) / 2 - 60, X1, (Y0 + Y1) / 2 - 60, 12, '#1e1e21'); }
  rr(X0 - 50, Y1 + 10, X1 - X0 + 100, 26, 4, '#1c1c1f');                                                 // sill
  // curtains: soft folds; they meet in the middle when closed
  const cl = clamp(o.close || 0), cw = lerp(150, (X1 - X0) / 2 + 30, cl);
  for (const side of [0, 1]) {
    ctx.save(); const cx = side ? X1 + 60 - cw : X0 - 60;
    ctx.fillStyle = '#17161a'; ctx.fillRect(cx, Y0 - 50, cw, Y1 - Y0 + 120);
    for (let i = 0; i < 6; i++) { const fx = cx + (i + 0.5) * cw / 6; ln(fx, Y0 - 40, fx + Math.sin(t + i) * 3, Y1 + 60, 5, 'rgba(255,255,255,0.05)'); }
    ctx.restore();
  }
  rr(X0 - 90, Y0 - 66, X1 - X0 + 180, 16, 6, '#2a2a2d');                                                // the rail
}

// ---------- inside the house ----------
// a knife block on the counter: origin = bottom centre. Five handles, biggest first. o.missing: slot index; o.red: the empty slot glows red
const BLK = { A: [-190, -330], B: [170, -140], f: [0.13, 0.3, 0.47, 0.64, 0.81], k: [1.18, 1.06, 0.96, 0.88, 0.8] };
const BLK_N = [0.47, -0.88], BLK_ANG = Math.atan2(-0.88, 0.47), BLK_FACE = Math.atan2(BLK.B[1] - BLK.A[1], BLK.B[0] - BLK.A[0]);
const blkP = i => [lerp(BLK.A[0], BLK.B[0], BLK.f[i]), lerp(BLK.A[1], BLK.B[1], BLK.f[i])];
const blkTip = (i, extra = 50) => { const p = blkP(i), L = 150 * BLK.k[i] + extra; return [p[0] + BLK_N[0] * L, p[1] + BLK_N[1] * L]; };
function blkHandle(i, out = 0) {   // out: how far it is pulled out (0 = seated)
  const p = blkP(i), k = BLK.k[i], L = 150 * k, w = 30 * k;
  ctx.save(); ctx.translate(p[0] + BLK_N[0] * out, p[1] + BLK_N[1] * out); ctx.rotate(BLK_ANG);
  if (out > 0) { glow('rgba(255,255,255,0.4)', 14); pth(`M0,${-w * 0.42} L${-out},${-w * 0.1} L${-out},${w * 0.3} L0,${w * 0.42} Z`, '#dcdcdc'); noGlow(); }
  rr(-4, -w * 0.55, 14, w * 1.1, 3, '#8a8a90');
  rr(10, -w / 2, L, w, w * 0.45, '#161618'); rrS(10, -w / 2, L, w, w * 0.45, '#46464d', 2.5);
  for (const f of [0.3, 0.55, 0.8]) circ(10 + L * f, 0, 3.4 * k, '#9a9aa0');
  ctx.restore();
}
function knifeBlock(x, y, s = 1, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const miss = o.missing ?? -1;
  // the block: front face, top face
  pth(`M-200,0 L180,0 L180,${BLK.B[1] + 10} L${BLK.A[0] - 10},${BLK.A[1] + 6} Z`, '#3d3128');
  for (let i = 0; i < 5; i++) ln(-190 + i * 10, -40 - i * 50, 170, -30 - i * 22, 2, 'rgba(0,0,0,0.18)');
  pth(`M${BLK.A[0] - 10},${BLK.A[1] + 6} L${BLK.A[0] + 6},${BLK.A[1] - 14} L${BLK.B[0] + 12},${BLK.B[1] - 12} L${BLK.B[0] + 10},${BLK.B[1] + 10} Z`, '#2a2119');
  pthS(`M-200,0 L180,0 L180,${BLK.B[1] + 10} L${BLK.A[0] - 10},${BLK.A[1] + 6} Z`, '#5a4a3c', 3);
  for (let i = 0; i < 5; i++) {
    const p = blkP(i);
    ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(BLK_FACE);
    if (i === miss && o.red) { redGlow(18 + 8 * Math.sin((o.t || 0) * 6)); rrS(-20 * BLK.k[i], -7, 40 * BLK.k[i], 14, 4, C.red, 5); noGlow(); }
    rr(-18 * BLK.k[i], -5, 36 * BLK.k[i], 10, 3, '#0a0806');
    ctx.restore();
  }
  for (let i = 4; i >= 0; i--) if (i !== miss && !(o.out && o.out[0] === i)) blkHandle(i);
  if (o.out) blkHandle(o.out[0], o.out[1]);
  ctx.restore();
}
// the dark kitchen: counter across the bottom, cabinets, the window over the sink (black glass). o.reflect(t): draws inside the glass
function kitchen(t, o = {}) {
  ctx.fillStyle = '#060606'; ctx.fillRect(-200, -200, W + 400, H + 400);
  // moonlight from the side
  const g = ctx.createLinearGradient(0, 0, W, 0); g.addColorStop(0, 'rgba(140,160,200,0.07)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 5; i++) { rr(80 + i * 360, 60, 330, 250, 6, '#0e0e10'); rrS(80 + i * 360, 60, 330, 250, 6, '#1f1f22', 3); circ(80 + i * 360 + (i % 2 ? 30 : 300), 280, 6, '#333'); }
  // the window over the sink
  const wx = o.winX ?? 760, wy = 330, ww = 520, wh = 330;
  rr(wx, wy, ww, wh, 4, '#030304');
  if (o.reflect) { ctx.save(); ctx.beginPath(); ctx.rect(wx, wy, ww, wh); ctx.clip(); o.reflect(wx, wy, ww, wh); ctx.restore(); }
  ctx.save(); ctx.globalAlpha = 0.08; pth(`M${wx + 40},${wy} L${wx + 140},${wy} L${wx + 20},${wy + wh} L${wx - 80},${wy + wh} Z`, '#fff'); ctx.restore();   // glass sheen
  rrS(wx, wy, ww, wh, 4, '#2a2a2d', 14); ln(wx + ww / 2, wy, wx + ww / 2, wy + wh, 10, '#1e1e21');
  // counter
  rr(-100, 700, W + 200, 40, 0, '#232327'); rr(-100, 740, W + 200, 400, 0, '#0e0e10');
  for (let i = 0; i < 6; i++) rrS(40 + i * 320, 770, 300, 300, 6, '#1d1d20', 3);
  if (o.block !== false) knifeBlock(o.blockX ?? 380, 700, o.blockS ?? 0.9, o.blockO || {});
}
// slatted closet door seen from inside: the scene behind, then the louvres over it. k = how open the gaps are
function slats(fnBehind, o = {}) {
  ctx.save(); ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); fnBehind(); ctx.restore();
  const gap = o.gap ?? 36, pitch = 74;
  ctx.fillStyle = '#0b0a09';
  for (let y = -40; y < H + 80; y += pitch) {
    ctx.beginPath(); ctx.moveTo(-50, y); ctx.lineTo(W + 50, y); ctx.lineTo(W + 50, y + pitch - gap); ctx.lineTo(-50, y + pitch - gap); ctx.closePath(); ctx.fill();
    ln(-50, y + pitch - gap, W + 50, y + pitch - gap, 3, '#24211e');
  }
  // the door frame edges, very dark
  const v = ctx.createLinearGradient(0, 0, W, 0); v.addColorStop(0, 'rgba(0,0,0,0.95)'); v.addColorStop(0.12, 'rgba(0,0,0,0)'); v.addColorStop(0.88, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.95)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}
// one-point hallway: vanishing point (960, 470). o.open[i] for the side doors (0..1), o.labels, o.fig(dep) to draw someone at a depth
const HALL = { vx: 960, vy: 470 };
function hallway(t, o = {}) {
  ctx.fillStyle = '#040404'; ctx.fillRect(-200, -200, W + 400, H + 400);
  const P = d => { const k = 1 / (1 + d); return [(x, y) => [HALL.vx + (x - HALL.vx) * k, HALL.vy + (y - HALL.vy) * k]]; };
  const at = (x, y, d) => { const k = 1 / (1 + d); return [HALL.vx + (x - HALL.vx) * k, HALL.vy + (y - HALL.vy) * k]; };
  // walls, floor, ceiling as quads from d=0 to d=6
  const q = (a, b, c, e, col) => { ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.lineTo(...c); ctx.lineTo(...e); ctx.closePath(); ctx.fillStyle = col; ctx.fill(); };
  const L = 260, R = 1660, T = -60, B = 1130, D = 7;
  q(at(L, T, 0), at(L, T, D), at(L, B, D), at(L, B, 0), '#1a1a1e');
  q(at(R, T, 0), at(R, T, D), at(R, B, D), at(R, B, 0), '#16161a');
  q(at(L, B, 0), at(L, B, D), at(R, B, D), at(R, B, 0), '#1d1c20');
  q(at(L, T, 0), at(L, T, D), at(R, T, D), at(R, T, 0), '#0e0e10');
  const end = [at(L, T, D), at(R, B, D)]; rr(end[0][0], end[0][1], end[1][0] - end[0][0], end[1][1] - end[0][1], 0, '#202128');
  { const a = at(760, 200, D), b = at(1160, 700, D); ctx.save(); glow('rgba(170,190,230,0.6)', 30); rr(a[0], a[1], b[0] - a[0], b[1] - a[1], 2, '#3a4152'); noGlow(); ln((a[0] + b[0]) / 2, a[1], (a[0] + b[0]) / 2, b[1], 3, '#202128'); ctx.restore(); }
  for (let d = 0.5; d < D; d += 0.6) { const a = at(L, B, d), b = at(R, B, d); ln(a[0], a[1], b[0], b[1], 2, '#1a191c'); }   // floorboards
  // side doors: [side, depth]
  const doors = o.doors || [[-1, 0.5], [1, 1.25], [-1, 2.1], [1, 3.1]];
  doors.forEach(([sd, d], i) => {
    const x = sd < 0 ? L : R, d1 = d + 0.55, op = (o.open || [])[i] || 0;
    const a = at(x, 260, d), b = at(x, 260, d1), c = at(x, B, d1), e = at(x, B, d);
    q(a, b, c, e, '#000');
    // the door leaf swings into the room
    const sw = lerp(d1, d1 - 0.5 * op, 1), lx = x - sd * 520 * op;
    q(at(x, 260, d), at(lx, 260, d + 0.55 * (1 - op)), at(lx, B, d + 0.55 * (1 - op)), at(x, B, d), '#2c2b31'); { const m = at(lx + sd * 60 * (1 - op), 700, d + 0.45 * (1 - op)); circ(m[0], m[1], 7 / (1 + d), '#77777e'); }
    ctx.save(); ctx.globalAlpha = 0.6; ln(...at(x, 260, d), ...at(x, B, d), 3, '#333'); ctx.restore();
    if (o.labels && o.labels[i] && o.labels[i][1] <= t) { const m = at(x, 560, d + 0.27), ly = m[1] - 200 / (1 + d) + (o.labels[i][2] || 0); pop(t, o.labels[i][1], m[0], ly, () => tag(o.labels[i][0], m[0], ly, C.fig, 34, 'center'), 0.3); }
  });
  if (o.fig) o.fig(at);
  // light from the far end
  const lg = ctx.createRadialGradient(HALL.vx, HALL.vy, 10, HALL.vx, HALL.vy, 700); lg.addColorStop(0, 'rgba(200,210,230,0.10)'); lg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = lg; ctx.fillRect(0, 0, W, H);
  return at;
}
// top-down floor plan; rooms: [name, x, y, w, h]; returns the room map
const PLAN = [['BEDROOM', 360, 180, 420, 330], ['BATHROOM', 780, 180, 260, 330], ['GUEST ROOM', 1040, 180, 420, 330], ['LAUNDRY', 360, 590, 300, 300], ['HALL', 660, 510, 800, 80], ['CLOSET', 1300, 590, 160, 300], ['KITCHEN', 660, 590, 640, 300]];
function floorPlan(t, o = {}) {
  ctx.save(); glow('rgba(255,255,255,0.2)', 20);
  rr(340, 160, 1140, 750, 6, '#0b0b0c'); noGlow();
  for (const [n, x, y, w, h] of PLAN) {
    if (n === 'HALL') { rr(x, y, w, h, 0, '#121214'); continue; }
    const hot = o.hot === n, chk = (o.checked || []).includes(n);
    rr(x + 6, y + 6, w - 12, h - 12, 4, hot ? 'rgba(255,43,43,0.12)' : '#0f0f11');
    rrS(x, y, w, h, 2, hot ? C.red : C.fig, 6);
    text(n, x + w / 2, y + h / 2 + 12, '900 30px M', hot ? C.red : (chk ? C.mid : C.sec));
    if (chk) { check(x + w / 2, y + h / 2 + 62, 22, 1, C.mid); }
  }
  // door gaps on the hall
  for (const gx of [540, 880, 1220]) rr(gx, 504, 70, 12, 0, '#0b0b0c');
  for (const gx of [480, 960, 1350]) rr(gx, 584, 70, 12, 0, '#0b0b0c');
  ctx.restore();
}
// rooms centres for paths
const roomC = n => { const r = PLAN.find(p => p[0] === n); return [r[1] + r[3] / 2, r[2] + r[4] / 2]; };

// a cutaway of the house: two floors, side view. rooms: [name, x, y, w, h]
const CUT = [['BEDROOM', 520, 250, 440, 300], ['CLOSET', 960, 250, 160, 300], ['BATHROOM', 1120, 250, 280, 300], ['KITCHEN', 520, 550, 520, 300], ['LIVING ROOM', 1040, 550, 360, 300]];
function cutaway(t, o = {}) {
  ctx.save();
  ctx.beginPath(); ctx.moveTo(480, 250); ctx.lineTo(960, 40); ctx.lineTo(1440, 250); ctx.closePath(); ctx.fillStyle = '#0d0d0f'; ctx.fill(); ctx.strokeStyle = '#3a3a3e'; ctx.lineWidth = 5; ctx.stroke();
  for (const [n, x, y, w, h] of CUT) {
    const hot = (o.hot || []).includes(n);
    rr(x, y, w, h, 0, hot ? 'rgba(255,43,43,0.08)' : '#0b0b0c'); rrS(x, y, w, h, 0, '#3a3a3e', 5);
    if (o.labels !== false) text(n, x + w / 2, y + 44, '900 24px M', hot ? C.red : C.mid);
  }
  rr(440, 850, 1040, 14, 0, '#3a3a3e');
  if (o.fn) o.fn();
  ctx.restore();
}
// car interior at night: the road through the windshield, the rear-view mirror at the top. o.face: 0..1 white face in the mirror
function carView(t, o = {}) {
  ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400);
  // the road in the headlights
  ctx.save(); const g = ctx.createRadialGradient(960, 760, 40, 960, 760, 760); g.addColorStop(0, 'rgba(255,248,230,0.16)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 300, W, 800);
  ctx.beginPath(); ctx.moveTo(900, 470); ctx.lineTo(1020, 470); ctx.lineTo(1700, 1080); ctx.lineTo(220, 1080); ctx.closePath(); ctx.fillStyle = '#0d0d0f'; ctx.fill();
  for (let i = 0; i < 8; i++) { const k = ((i / 8 + t * 0.9) % 1), y = lerp(480, 1080, k * k), w = lerp(3, 30, k * k), h = lerp(6, 90, k * k); rr(960 - w / 2, y, w, h, 2, '#3a3a3a'); }
  ctx.restore();
  // dashboard and the frame of the windshield
  pth('M-100,1080 L-100,820 C300,760 1620,760 2020,820 L2020,1080 Z', '#060607'); pthS('M-100,820 C300,760 1620,760 2020,820', '#222226', 4);
  pth('M-100,-100 L2020,-100 L2020,180 C1600,140 320,140 -100,180 Z', '#050506');
  pth('M-100,-100 L300,-100 L80,1080 L-100,1080 Z', '#050506'); pth('M2020,-100 L1620,-100 L1840,1080 L2020,1080 Z', '#050506');
  // steering wheel
  ctx.save(); ctx.lineWidth = 34; ctx.strokeStyle = '#141416'; ctx.beginPath(); ctx.arc(620, 1080, 300, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); ctx.restore();
  // the mirror
  const mx = 960, my = 180, mw = 520, mh = 150;
  ln(mx, 130, mx, my - mh / 2, 14, '#1a1a1c');
  rr(mx - mw / 2 - 12, my - mh / 2 - 12, mw + 24, mh + 24, 30, '#1a1a1c');
  ctx.save(); ctx.beginPath(); ctx.roundRect(mx - mw / 2, my - mh / 2, mw, mh, 22); ctx.clip();
  ctx.fillStyle = '#0a0b0d'; ctx.fillRect(mx - mw / 2, my - mh / 2, mw, mh);
  // the back seat and the rear window in the mirror
  rr(mx - 220, my + 10, 440, 80, 20, '#151518'); rr(mx - 180, my - 70, 360, 60, 10, '#101114');
  if ((o.face || 0) > 0) { ctx.save(); ctx.globalAlpha *= o.face; rr(mx - 70 + 20, my - 10, 120, 120, 40, NIGHT.jump); maskHead(mx + 10, my + 6, 0.62, { red: o.red || 0, glowA: 0.25, glowB: 16 }); ctx.restore(); }
  ctx.globalAlpha = 0.08; pth(`M${mx - mw / 2},${my - mh / 2} L${mx - mw / 2 + 120},${my - mh / 2} L${mx - mw / 2 + 40},${my + mh / 2} L${mx - mw / 2 - 80},${my + mh / 2} Z`, '#fff');
  ctx.restore();
  rrS(mx - mw / 2, my - mh / 2, mw, mh, 22, '#2e2e33', 4);
}
// icons for the teaser boxes and lists (white on dark)
function icon6(name, x, y, s = 1, col = C.fig) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 14);
  if (name === 'eye') { pth('M-90,0 C-50,-56 50,-56 90,0 C50,56 -50,56 -90,0 Z', col); noGlow(); circ(0, 0, 26, '#000'); }
  if (name === 'closet') { rrS(-70, -90, 140, 180, 6, col, 8); ln(0, -90, 0, 90, 6, col); for (let i = 0; i < 6; i++) { ln(-58, -68 + i * 26, -10, -60 + i * 26, 6, col); ln(10, -68 + i * 26, 58, -60 + i * 26, 6, col); } circ(-14, 10, 5, col); circ(14, 10, 5, col); }
  if (name === 'rise') { rr(-110, 70, 220, 12, 5, C.sec); circ(-80, 36, 28, col); rr(-46, 16, 150, 44, 18, col); ln(-80, -10, -80, -80, 12, col); pth('M-108,-66 L-80,-104 L-52,-66 Z', col); }
  if (name === 'knives') { ctx.rotate(-0.4); for (let i = 0; i < 4; i++) { rr(-60 + i * 36, -90, 20, 70, 6, col); } ctx.rotate(0.4); rr(-90, -10, 180, 90, 10, col); noGlow(); rrS(-60 + 3 * 36 - 12, -80, 40, 30, 5, C.red, 0); }
  if (name === 'phone') { rrS(-38, -72, 76, 144, 14, col, 8); circ(0, 52, 7, col); }
  if (name === 'curtain') { ln(-90, -84, 90, -84, 8, col); pth('M-80,-80 C-60,-20 -70,40 -40,84 L-4,84 C-24,40 -14,-20 -10,-80 Z', col); pth('M80,-80 C60,-20 70,40 40,84 L4,84 C24,40 14,-20 10,-80 Z', col); }
  if (name === 'blink') { pthS('M-90,0 C-50,40 50,40 90,0', col, 10); for (let i = -2; i <= 2; i++) ln(i * 34, 26 - Math.abs(i) * 4, i * 44, 56 - Math.abs(i) * 4, 7, col); }
  if (name === 'search') { circS(-14, -14, 52, col, 12); ln(24, 24, 74, 74, 16, col); }
  if (name === 'voice') { circ(-40, 0, 40, col); for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(-10, 0, 46 + i * 24, -0.7, 0.7); ctx.strokeStyle = col; ctx.lineWidth = 8; ctx.stroke(); } }
  if (name === 'door') { rrS(-56, -90, 112, 180, 6, col, 8); circ(32, 4, 8, col); }
  if (name === 'step') { ell(-30, 20, 22, 42, -0.2, col); ell(36, -30, 22, 42, 0.2, col); }
  if (name === 'breath') { for (let i = 0; i < 3; i++) pthS(`M-80,${-40 + i * 40} C-30,${-60 + i * 40} 10,${-20 + i * 40} 80,${-40 + i * 40}`, col, 9); }
  if (name === 'hand') { rr(-40, -10, 80, 90, 24, col); for (let i = 0; i < 4; i++) rr(-40 + i * 21, -80, 16, 80, 8, col); ctx.save(); ctx.translate(-44, 30); ctx.rotate(-0.7); rr(-8, -50, 16, 56, 8, col); ctx.restore(); }
  if (name === 'back') { circ(0, -60, 32, col); rr(-34, -22, 68, 100, 20, col); pthS('M60,-40 C110,-20 110,40 60,60', col, 8); pth('M54,46 L82,70 L50,80 Z', col); }
  if (name === 'hanger') { pthS('M0,-50 C0,-80 30,-80 30,-60 C30,-46 0,-44 0,-30 L-90,40 L90,40 L0,-30', col, 9); }
  if (name === 'needle') { ln(-90, 70, 90, -70, 9, col); ellS(-70, 54, 12, 6, -0.66, col); }
  if (name === 'knife') { knife(-70, 30, -0.45, 0.95); }
  if (name === 'gun') { rr(-90, -30, 150, 40, 8, col); ctx.save(); ctx.translate(30, 0); ctx.rotate(0.25); rr(-10, 0, 40, 80, 8, col); ctx.restore(); circS(10, 30, 16, col, 6); }
  if (name === 'lock') { ctx.beginPath(); ctx.arc(0, -20, 40, Math.PI, 0); ctx.lineWidth = 14; ctx.strokeStyle = col; ctx.stroke(); rr(-60, -20, 120, 100, 14, col); noGlow(); circ(0, 22, 12, '#000'); rr(-5, 22, 10, 30, 3, '#000'); }
  if (name === 'car') { pth('M-100,30 L-90,-10 L-56,-60 L56,-60 L90,-10 L100,30 L100,50 L-100,50 Z', col); noGlow(); circ(-56, 54, 22, '#000'); circ(56, 54, 22, '#000'); circ(-56, 54, 12, col); circ(56, 54, 12, col); rr(-46, -48, 40, 34, 4, '#000'); rr(6, -48, 40, 34, 4, '#000'); }
  if (name === 'scream') { circ(0, -10, 56, col); for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(0, -10, 80 + i * 24, -0.5, 0.5); ctx.strokeStyle = col; ctx.lineWidth = 8; ctx.stroke(); ctx.beginPath(); ctx.arc(0, -10, 80 + i * 24, Math.PI - 0.5, Math.PI + 0.5); ctx.stroke(); } }
  if (name === 'call') { pth('M-60,-70 C-80,-40 -60,20 -10,60 C30,90 70,80 80,60 L50,30 L20,44 C0,30 -30,0 -36,-24 L-20,-50 Z', col); }
  noGlow(); ctx.restore();
}
const ellS = (x, y, rx, ry, rot, s, w = 6) => { ctx.beginPath(); ctx.ellipse(x, y, rx, ry, rot, 0, Math.PI * 2); ctx.strokeStyle = s; ctx.lineWidth = w; ctx.stroke(); };
// a dark card behind a list of items over a busy scene
function listCard(x, y, w, h) { ctx.save(); ctx.globalAlpha *= 0.86; rr(x, y, w, h, 18, '#050505'); ctx.restore(); rrS(x, y, w, h, 18, '#2a2a2d', 3); }
// a row with an icon box, text, and a red X that draws on at tx
function noRow(t, t0, tx, x, y, ic, label, size = 46) {
  slideIn(t, t0, 50, 0, () => {
    rr(x, y - 60, 120, 120, 16, '#121214'); rrS(x, y - 60, 120, 120, 16, '#3a3a3e', 3); icon6(ic, x + 60, y, 0.5);
    text(label, x + 160, y + size * 0.36, `900 ${size}px M`, C.fig, 'left');
    redX(x + 60, y, 50, prog(t, tx, 0.3));
  }, 0.35);
}
// the man in profile (facing o.dir = 1 right / -1 left). Feet at (x,y), 600 tall at s=1.
// o.walk phase, o.knife 0/1/2, o.lean (rad, whole body tips back around the feet: falling), o.floor 0..1: lying on his back -> o.sit 0..1 sits up from the waist
function myersSide(x, y, s = 1, o = {}) {
  const dir = o.dir || 1;
  ctx.save(); ctx.translate(x, y); ctx.scale(s * dir, s);
  const body = NIGHT.jump, edge = 'rgba(150,158,170,0.5)';
  const limb = (pts, w, col = body) => { ctx.beginPath(); ctx.moveTo(...pts[0]); for (const p of pts.slice(1)) ctx.lineTo(...p); ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = col; ctx.stroke(); };
  const upper = (o2) => {   // torso, arm, head around the hip at (0,0), pointing up
    const tor = new Path2D('M-50,-210 C-58,-150 -52,-60 -44,0 L44,0 C52,-60 56,-150 46,-210 C20,-222 -26,-222 -50,-210 Z');
    ctx.fillStyle = body; ctx.fill(tor); ctx.strokeStyle = edge; ctx.lineWidth = 3; ctx.stroke(tor);
    const raise = o2.knife === 2 ? 1 : 0;
    const hand = o2.knife === 2 ? [46, -350] : o2.floorHand ? [40, -20] : [26 + (o2.walk != null ? Math.sin(o2.walk) * 18 : 0), 30];
    limb([[0, -196], [lerp(18, 30, raise), lerp(-90, -270, raise)], hand], 36);
    circ(hand[0], hand[1], 18, '#cfcdc4');
    if (o2.knife) knife(hand[0], hand[1], o2.knife === 2 ? -Math.PI / 2 + 0.25 : Math.PI / 2 - 0.1, 1);
    // head in profile
    ctx.save(); ctx.translate(6, -262);
    pth('M-52,-30 C-58,-76 -24,-104 12,-100 C34,-98 46,-78 42,-44 L-20,44 C-50,34 -58,0 -52,-30 Z', NIGHT.hair);
    glow('rgba(255,255,255,0.3)', 24);
    pth('M-8,-74 C24,-82 44,-60 44,-34 C46,-24 56,-12 52,-4 C48,2 44,4 44,10 C46,36 34,58 12,62 C-6,60 -18,40 -20,10 C-24,-30 -24,-60 -8,-74 Z', NIGHT.mask); noGlow();
    pth('M-12,-72 C14,-84 40,-70 44,-44 C30,-58 10,-62 -14,-56 Z', NIGHT.hair);
    ctx.save(); ctx.filter = 'blur(3px)'; ell(22, -26, 16, 11, 0.1, 'rgba(55,64,74,0.35)'); ell(4, 18, 16, 22, 0, 'rgba(55,64,74,0.1)'); ell(30, 50, 14, 8, 0, 'rgba(55,64,74,0.2)'); ctx.filter = 'none'; ctx.restore();
    pthS('M8,-40 C18,-46 32,-46 40,-38', 'rgba(55,64,74,0.4)', 3);                 // brow
    pth('M16,-26 C20,-32 30,-32 34,-24 C30,-20 20,-20 16,-26 Z', '#030303');           // the eye hole
    ell(46, 2, 3, 2, 0, 'rgba(35,38,42,0.6)');                                         // nostril
    pthS('M38,22 L46,22', '#4a4e53', 2);                                               // closed lips
    if (o2.red) { ctx.save(); ctx.globalAlpha *= o2.red; redGlow(16); circ(25, -26, 3, C.red); noGlow(); ctx.restore(); }
    ctx.restore();
  };
  if (o.floor) {
    // lying on his back: legs along the floor toward +x, torso tips up from -x as he sits up
    const sit = clamp(o.sit || 0);
    limb([[0, -40], [150, -36], [300, -30]], 44); limb([[0, -40], [160, -50], [300, -40]], 44, NIGHT.jumpLo); rr(286, -64, 34, 60, 10, '#121315');
    ctx.save(); ctx.translate(0, -40); ctx.rotate(lerp(-Math.PI / 2, 0, ease(sit))); upper({ ...o, knife: 0, floorHand: true }); ctx.restore();
    if (o.knife) knife(80, -14, 0.05, 1);
  } else {
    ctx.rotate(-(o.lean || 0));
    const sw = o.walk != null ? Math.sin(o.walk) : 0;
    limb([[0, -300], [sw * 40, -150], [sw * 70, -16]], 44, NIGHT.jumpLo); rr(sw * 70 - 18, -30, 64, 30, 10, '#121315');
    limb([[0, -300], [-sw * 40, -150], [-sw * 70, -16]], 44); rr(-sw * 70 - 18, -30, 64, 30, 10, '#121315');
    ctx.save(); ctx.translate(0, -300); upper(o); ctx.restore();
  }
  ctx.restore();
}
// ---------- EP06 scenes: "If Michael Myers Is Standing Outside Your House" ----------
const ev = type => window.TL.events.filter(e => e.type === type);
const evAfter = (type, t0) => { const l = ev(type).filter(e => e.t >= t0 - 0.01); return l.length ? l.reduce((a, b) => (b.t < a.t ? b : a)) : null; };
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
const redFlash = (t, t0, a = 0.1) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a * (0.5 + 0.5 * Math.sin((t - t0) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const blackAfter = (t, t0) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
function xTag(s, x, y, size, p) { tag(s, x, y, C.fig, size, 'center'); ctx.font = `900 ${size}px M`; const w = ctx.measureText(s).width + 28; redX(x - w / 2 - size * 0.95, y - size * 0.2, size * 0.5, p); }
const zk = (t, t0, d, z0, z1) => lerp(z0, z1, ease((t - t0) / d));
const clockStr = s => { s = Math.max(0, Math.floor(s)); const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, x = s % 60; return [h, m, x].map(v => String(v).padStart(2, '0')).join(':'); };
const T300 = 3 * 3600;
// typed text: the first n characters by time
const typed = (s, t, t0, cps = 28) => s.slice(0, Math.max(0, Math.floor((t - t0) * cps)));

// ---------- shared shots ----------
const LIGHT = { x: 1080, y: 642, s: 0.42 };            // where he stands: under the streetlight across the street
const MAILBOX = { x: 900, y: 884, s: 0.74 };
const LAWN = { x: 1010, y: 1080, s: 1.32 };
const black = () => { ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); };
// a white bracket frame around a point (focus marks)
function brackets(x, y, w, h, a, col = C.fig) {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha *= a; const L = 34;
  for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const cx = x + sx * w / 2, cy = y + sy * h / 2; poly([[cx, cy - sy * L], [cx, cy], [cx - sx * L, cy]], 6, col); }
  ctx.restore();
}
// the street through your window. o.z, o.f: zoom + focus, o.him, o.close
function lookOut(t, o = {}) {
  const x0 = o.x0 ?? 300, x1 = o.x1 ?? 1620, y0 = o.y0 ?? 80, y1 = o.y1 ?? 930;
  windowPOV(t, { cross: o.cross ?? false, close: o.close, x0, x1, y0, y1,
    fn: () => streetScene(t, { scr: [(x0 + x1) / 2, (y0 + y1) / 2], cam: [o.z || 1.3, ...(o.f || [1060, 520])], him: o.him === undefined ? LIGHT : o.him, light: o.light, kids: o.kids, near: o.near, emptyHouse: o.emptyHouse, houses: o.houses }) });
}
// a "does not work" header row at the top left, X drawn at tx
function noHead(t, seg, ic, label, tx) {
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  slideIn(t, seg.start, -40, 0, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(60, 60, 150 + label.length * 30, 130, 18, '#050505'); ctx.restore(); rrS(60, 60, 150 + label.length * 30, 130, 18, '#2a2a2d', 3);
    icon6(ic, 125, 125, 0.48); text(label, 200, 142, '900 46px M', C.fig, 'left'); redX(125, 125, 48, prog(t, tx, 0.3)); }, 0.35);
  ctx.restore();
}

// ---------- hook ----------
S.h1 = (t, seg) => {
  // frame 0: through your window, he is already there under the streetlight, looking in
  const ta = wt(seg, 'away');
  lookOut(t, { cross: false, x0: 120, x1: 1800, y0: 30, y1: 1000, z: zk(t, 0, seg.end + 0.8, 2.15, 2.6), f: [1082, 470] });
  if (t >= ta - 0.3) pop(t, ta - 0.3, 960, 150, () => tag('DO NOT LOOK AWAY', 960, 160, C.red, 52, 'center'), 0.3);
};
function h2Windows(seg) { return [[seg.start, wt(seg, 'do'), 'knives', 'knives', 250], [wt(seg, 'do'), wt(seg, 'and'), 'closet', 'closet', 250], [wt(seg, 'and'), nextStart(seg), 'rise', 'dead', 250]]; }
const H2_HIT = 0.6, H2_BLACK = 0.4;
function teaserBox(t, seg, w0, ic, word, y) {
  const x = 1600, tx = wt(seg, word);
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(x - 140, y - 130, 280, 260, 22, '#000'); ctx.restore(); rrS(x - 140, y - 130, 280, 260, 22, C.fig, 5); icon6(ic, x, y, 0.95); }, 0.3);
  redX(x, y, 105, prog(t, tx + 0.25, 0.3));
}
S.h2 = (t, seg) => {
  const ws = h2Windows(seg); let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, ic, word, by] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit;
  if (t < blk) {
    if (i === 0) {
      // the knife block in the dark kitchen: one slot is empty, and it turns red
      black(); rr(-200, 960, W + 400, 200, 0, '#121214');
      cam(t, w0, blk - w0, 1.0, 1.25, 860, 760, () => blockClose(t, { x: 860, y: 1000, s: 1.7, missing: 0, red: t >= w0 + 0.5 }));
    } else if (i === 1) {
      // you hide in the closet: the mask comes right up to the slats
      const k = ease(prog(t, w0 + 0.2, hit - w0 - 0.2));
      slats(() => { hallway(t, {}); ctx.save(); ctx.translate(960, 560); const z = lerp(0.5, 2.6, k); ctx.scale(z, z); ctx.globalAlpha = 0.85; myers(0, 520, 1, { knife: 1, red: prog(t, hit - 0.3, 0.3) }); ctx.restore(); });
    } else {
      // you go to check: he sits up
      black(); ctx.fillStyle = '#0d0c0b'; ctx.fillRect(0, 760, W, 400); for (let j = 0; j < 9; j++) ln(0, 780 + j * 34, W, 780 + j * 34, 2, '#191715');
      cam(t, w0, blk - w0, 1.1, 1.45, 820, 640, () => myersSide(760, 830, 1.15, { floor: 1, sit: prog(t, hit - 0.75, 0.6), knife: 1, red: prog(t, hit - 0.1, 0.2) }));
    }
    if (d > 0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.35 * clamp(d / 0.2); ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  }
  blackAfter(t, blk);
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); teaserBox(t, seg, w0, ic, word, by); ctx.restore();
};

// ---------- rule 1: do not look away ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT LOOK AWAY');
const kidX = (off, ph) => ((off + ph * 60) % 2600) - 300;
S.a1 = (t, seg) => {
  // Halloween: the street full of masks
  const tw = wt(seg, 'witches'), tg = wt(seg, 'ghosts'), tk = wt(seg, 'kids');
  streetScene(t, { cam: [zk(t, seg.start, seg.end - seg.start + 0.7, 1.35, 1.5), lerp(560, 760, ease((t - seg.start) / (seg.end - seg.start))), 470], him: null, kids: t - seg.start + 9,
    near: () => {
      const lab = [[tw, 'WITCH', 0], [tg, 'GHOST', 210], [tk, 'CANDY', 330]];
      for (const [t0, s, off] of lab) if (t >= t0) { const x = kidX(off, t - seg.start + 9) + 30; pop(t, t0, x, 480, () => tag(s, x, 480, C.fig, 26, 'center'), 0.3); }
    } });
};
S.a2 = (t, seg) => {
  // one of them is not moving: the camera stops on him while the kids walk past
  const tm = wt(seg, 'moving');
  streetScene(t, { cam: [zk(t, seg.start, 2.4, 1.6, 2.2), 1080, 480], him: LIGHT, kids: t + 30,
    near: () => { ctx.save(); trickKid(kidX(560, t + 30) + 0, 660, 0.62, 'ghost', t * 5); ctx.restore();
      brackets(LIGHT.x, LIGHT.y - 130, 150, 310, prog(t, tm - 0.1, 0.25), C.fig); } });
};
S.a3 = (t, seg) => {
  // the man: dark coveralls, pale mask, perfectly still
  const tj = wt(seg, 'jumpsuit'), tm = wt(seg, 'mask'), ts = wt(seg, 'still');
  streetScene(t, { cam: [zk(t, seg.start, seg.end - seg.start + 0.7, 2.6, 2.9), 1082, 520], him: LIGHT, kids: null,
    near: () => {
      const s = 1 / 2.7;
      if (t >= tj) pop(t, tj, 1180, 560, () => { ln(1105, 560, 1170, 560, 3 * s * 2, C.fig); ctx.save(); ctx.translate(1180, 560); ctx.scale(s, s); tag('DARK JUMPSUIT', 0, 10, C.fig, 30, 'left'); ctx.restore(); }, 0.3);
      if (t >= tm) pop(t, tm, 980, 405, () => { ln(1068, 405, 1000, 405, 3 * s * 2, C.fig); ctx.save(); ctx.translate(990, 405); ctx.scale(s, s); tag('WHITE MASK', 0, 10, C.fig, 30, 'right'); ctx.restore(); }, 0.3);
      if (t >= ts) pop(t, ts, 1180, 640, () => { ctx.save(); ctx.translate(1180, 650); ctx.scale(s, s); tag('PERFECTLY STILL', 0, 10, C.fig, 30, 'left'); ctx.restore(); }, 0.3);
    } });
};
S.a4 = (t, seg) => {
  // over his shoulder: not the houses. Your window.
  const th = wt(seg, 'houses'), tw = wt(seg, 'window');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.08, 1100, 500, () => {
    const g = ctx.createLinearGradient(0, 0, 0, 700); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    house(560, 700, 520, { win: [0.6, 0, 0, 0.5], porch: 1, pumpkins: 1 });
    house(1260, 720, 700, { win: [0, 0.95, 0.3, 0], porch: 1, pumpkins: 1, who: { win: 1, fn: (x, y, w, h) => me(x + w / 2, y + h + h * 0.55, h / 300, { face: 'front' }) } });
    house(1880, 700, 480, { win: [0.5, 0.5, 0, 0], pumpkins: 1 });
    rr(-200, 700, W + 400, 400, 0, NIGHT.grass);
    // the looks: the other houses get crossed, then the line ends on your window
    const hx = 330, hy = 380;
    if (t >= th && t < tw + 0.2) for (const [x, y] of [[505, 520], [1840, 520]]) { ctx.save(); ctx.setLineDash([14, 12]); ctx.globalAlpha = 0.6; ln(hx, hy, x, y, 4, C.fig); ctx.restore(); redX(x, y, 28, prog(t, th + 0.4, 0.25)); }
    if (t >= tw - 0.1) { const k = ease(prog(t, tw - 0.1, 0.5)), wx = 1260 + 700 * 0.62 / 2 * 0 + 112, wy = 720 - 434 * 0.86 + 56;
      ctx.save(); redGlow(14); ctx.setLineDash([16, 12]); ln(hx, hy, lerp(hx, 1287, k), lerp(hy, 403, k), 6, C.red); ctx.restore(); if (k >= 1) brackets(1287, 403, 180, 130, 1, C.red); }
    myers(330, 1260, 1.45, { back: true });
  });
};
S.a5 = (t, seg) => {
  // the head tilts, slowly
  const tt = wt(seg, 'tilts');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.12, 960, 480, () => {
    black(); const g = ctx.createRadialGradient(960, 300, 50, 960, 400, 900); g.addColorStop(0, 'rgba(255,250,235,0.08)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    myers(960, 2500, 3.6, { tilt: -0.32 * ease(prog(t, tt, 2.4)) });
  });
};
S.a6 = (t, seg) => {
  // you at the window. Not to call. Not the curtains. Not even a long blink.
  const tc = wt(seg, 'call'), tu = wt(seg, 'curtains'), tb = wt(seg, 'blink');
  lookOut(t, { x0: 860, x1: 1800, y0: 90, y1: 900, z: 1.9, f: [1000, 470] });
  me(1120, 1420, 2.3, { face: 'back' });
  listCard(80, 250, 700, 560);
  noRow(t, tc - 0.2, tc + 0.25, 130, 360, 'phone', 'CALL SOMEONE', 42);
  noRow(t, tu - 0.2, tu + 0.25, 130, 530, 'curtain', 'CLOSE CURTAINS', 42);
  noRow(t, tb - 0.2, tb + 0.25, 130, 700, 'blink', 'BLINK TOO LONG', 42);
};
S.a7 = (t, seg) => {
  // he never runs: he walks
  const tr = wt(seg, 'runs'), tn = wt(seg, 'need');
  black(); rr(-200, 900, W + 400, 300, 0, '#0c0c0e'); ln(-200, 900, W + 400, 900, 3, '#26262a');
  pop(t, seg.start, 520, 600, () => { me(520, 900, 1.3, { face: 'right', walk: t * 14, arms: [0.35 + 0.3 * Math.sin(t * 14), 0.35 - 0.3 * Math.sin(t * 14)] }); }, 0.3);
  if (t >= tr) { redX(520, 620, 170, prog(t, tr, 0.3)); }
  if (t >= tr + 0.3) slideIn(t, tr + 0.3, 80, 0, () => { myersSide(1300 + (t - tr) * 30, 910, 1.0, { walk: (t - tr) * 3.2, knife: 1 }); });
  if (t >= tn) pop(t, tn, 1340, 230, () => tag('HE WALKS', 1340, 240, C.fig, 44, 'center'), 0.3);
};
S.a8 = (t, seg) => {
  // every time you look away (black), he is closer: the streetlight, the mailbox, your lawn
  const ts = wt(seg, 'streetlight'), tm = wt(seg, 'mailbox'), tl = wt(seg, 'lawn');
  const him = t < tm - 0.05 ? LIGHT : t < tl - 0.05 ? MAILBOX : LAWN;
  const lab = t < tm - 0.05 ? (t >= ts ? ['STREETLIGHT', 1080, 330] : null) : t < tl - 0.05 ? ['MAILBOX', 900, 360] : ['YOUR LAWN', 1010, 140];
  lookOut(t, { z: 1.25, f: [1000, 560], him });
  if (lab) pop(t, him === LIGHT ? ts : him === MAILBOX ? tm : tl, lab[1], lab[2], () => tag(lab[0], lab[1], lab[2], him === LAWN ? C.red : C.fig, 40, 'center'), 0.25);
  for (const b of [wt(seg, 'away'), ts, tm, tl]) if (t > b - 0.16 && t < b - 0.02) blackAfter(t, b - 0.16);   // the blink
};
S.a9 = (t, seg) => {
  // you look back: the streetlight is empty
  const te = wt(seg, 'empty');
  lookOut(t, { z: zk(t, seg.start, seg.end - seg.start + 0.6, 1.4, 2.0), f: [1080, 520], him: null });
  if (t >= te) pop(t, te, 960, 150, () => tag('EMPTY', 960, 160, C.red, 52, 'center'), 0.3);
};
S.a10 = (t, seg) => {
  // he is already inside: the white mask in the hallway door behind you
  const ti = wt(seg, 'inside'), k = ease(prog(t, ti - 0.3, 1.0));
  black();
  cam(t, seg.start, 3.5, 1.0, 1.12, 700, 520, () => {
    rr(1100, 120, 680, 700, 4, '#05070a'); ctx.save(); ctx.beginPath(); ctx.rect(1100, 120, 680, 700); ctx.clip(); streetScene(t, { cam: [1.5, 1080, 500], him: null }); ctx.restore();
    rrS(1100, 120, 680, 700, 4, '#2a2a2d', 18); ln(1440, 120, 1440, 820, 12, '#1e1e21');
    rr(260, 230, 340, 820, 2, '#020202'); rrS(260, 230, 340, 820, 2, '#1d1d20', 10);   // the dark hall door behind you
    ctx.save(); ctx.globalAlpha *= k; myers(430, 1050, 1.28, { dark: 0.55, knife: 1, red: prog(t, seg.end + 0.6, 0.3) }); ctx.restore();
    me(1440, 1240, 2.2, { face: 'back' });
  });
};

// ---------- rule 2: count the knives ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'COUNT THE KNIVES');
// knife block in close-up: slot tips for the numbers
function blockClose(t, o = {}) {
  ctx.save(); ctx.translate(o.x ?? 960, o.y ?? 940); ctx.scale(o.s ?? 2.4, o.s ?? 2.4);
  knifeBlock(0, 0, 1, { missing: o.missing ?? -1, red: o.red, t, out: o.out });
  for (let i = 0; i < 5; i++) { const nt = (o.numT || [])[i]; if (nt != null && t >= nt) { const [x, y] = blkTip(i, 44); pop(t, nt, x, y, () => { circ(x, y, 22, C.fig); text(String(i + 1), x, y + 10, '900 28px M', '#000'); }, 0.25); } }
  ctx.restore();
}
S.b1 = (t, seg) => {
  // the dark kitchen, the light stays off, count
  const tl = wt(seg, 'light'), tc = wt(seg, 'count');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.2, 760, 560, () => {
    kitchen(t, { blockX: 400, blockS: 1.0 });
    rr(1380, 470, 70, 110, 10, '#2a2a2e'); rr(1402, 495, 26, 50, 6, '#111');
    if (t >= tl) { tag('LIGHT', 1415, 650, C.fig, 30, 'center'); redX(1415, 525, 60, prog(t, tl + 0.2, 0.3)); }
    ctx.save(); ctx.translate(400, 700); ctx.scale(1.0, 1.0); for (let i = 0; i < 5; i++) { const nt = tc + 0.3 + i * 0.28; if (t >= nt) { const [x, y] = blkTip(i, 44); pop(t, nt, x, y, () => { circ(x, y, 22, C.fig); text(String(i + 1), x, y + 10, '900 28px M', '#000'); }, 0.25); } } ctx.restore();
  });
};
S.b2 = (t, seg) => {
  // he never brings a knife. He takes yours.
  const to = wt(seg, 'own'), tu = wt(seg, 'uses'), k = ease(prog(t, tu, 0.9));
  black(); rr(-200, 940, W + 400, 300, 0, '#0c0c0e');
  rr(1140, 820, 760, 30, 0, '#232327'); rr(1140, 850, 760, 300, 0, '#0e0e10');
  knifeBlock(1500, 820, 1.4, { missing: k > 0 ? 0 : -1 });
  myers(560, 1010, 1.25, { knife: k >= 1 ? 1 : 0 });
  if (t >= to) { pop(t, to, 560, 200, () => tag('NO KNIFE OF HIS OWN', 560, 210, C.fig, 36, 'center'), 0.3); }
  if (k > 0 && k < 1) { const tp = blkTip(0, -40), sx = 1500 + tp[0] * 1.4, sy = 820 + tp[1] * 1.4; knife(lerp(sx, 440, k), lerp(sy, 680, k), lerp(-2.1, Math.PI / 2, k) + k * 6.28, 1.25); }
  if (t >= tu + 0.9) pop(t, tu + 0.9, 1500, 260, () => tag('YOURS', 1500, 270, C.red, 44, 'center'), 0.3);
};
S.b3 = (t, seg) => {
  // five slots, five handles: good, he is still outside
  const t1 = wt(seg, 'five', 1), t2 = wt(seg, 'five', 2), tg = wt(seg, 'good'), to = wt(seg, 'outside');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 800, 600, () => {
    black(); rr(-200, 940, W + 400, 300, 0, '#121214');
    blockClose(t, { x: 700, y: 1010, s: 1.45, numT: [0, 1, 2, 3, 4].map(i => t1 + 0.2 + i * 0.12) });
    if (t >= t2) pop(t, t2, 520, 180, () => tag('5 HANDLES', 520, 190, C.fig, 40, 'center'), 0.3);
    if (t >= tg) { pop(t, tg, 860, 180, () => { check(860, 175, 40, prog(t, tg, 0.3)); }, 0.3); }
  });
  if (t >= to - 0.3) slideIn(t, to - 0.3, 60, 0, () => {
    rr(1300, 300, 520, 420, 16, '#000'); ctx.save(); ctx.beginPath(); ctx.roundRect(1310, 310, 500, 400, 12); ctx.clip(); streetScene(t, { scr: [1560, 510], cam: [1.7, 1080, 500], him: LIGHT }); ctx.restore();
    rrS(1310, 310, 500, 400, 12, C.fig, 4); tag('STILL OUTSIDE', 1560, 790, C.fig, 34, 'center'); });
};
S.b4 = (t, seg) => {
  // one slot is empty
  const te = wt(seg, 'empty');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.3, 760, 560, () => { black(); rr(-200, 940, W + 400, 300, 0, '#121214'); blockClose(t, { x: 900, y: 1020, s: 1.55, missing: 0, red: t >= te }); });
  redFlash(t, te, 0.05);
};
S.b5 = (t, seg) => {
  // do not look for it, do not call out, do not check the other rooms
  const tl = wt(seg, 'look'), tc = wt(seg, 'call'), tr = wt(seg, 'check');
  ctx.save(); ctx.globalAlpha = 0.45; black(); rr(-200, 940, W + 400, 300, 0, '#121214'); blockClose(t, { x: 1500, y: 1000, s: 1.7, missing: 0, red: true }); ctx.restore();
  listCard(160, 230, 900, 580);
  noRow(t, tl - 0.25, tl + 0.3, 220, 350, 'search', 'LOOK FOR IT', 46);
  noRow(t, tc - 0.25, tc + 0.3, 220, 520, 'voice', 'CALL OUT', 46);
  noRow(t, tr - 0.25, tr + 0.3, 220, 690, 'door', 'CHECK THE ROOMS', 46);
};
S.b6 = (t, seg) => {
  // the cutaway: you in the kitchen, him in the living room, your biggest knife
  const ti = wt(seg, 'inside'), tb = wt(seg, 'biggest');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.1, 960, 560, () => {
    black(); cutaway(t, { hot: t >= ti ? ['LIVING ROOM'] : [] });
    me(700, 850, 0.62, { face: 'front' });
    if (t >= ti - 0.1) fadeIn(t, ti - 0.1, () => myers(1230, 850, 0.42, { knife: 1, knifeRed: t >= tb, red: t >= tb ? 1 : 0 }), 0.4);
    if (t >= tb) pop(t, tb, 1220, 470, () => tag('YOUR BIGGEST KNIFE', 1220, 480, C.red, 30, 'center'), 0.3);
  });
};
S.b7 = (t, seg) => {
  // you go looking: a dark hallway, the torch beam sweeping
  const tf = wt(seg, 'find');
  hallway(t, { open: [0.6, 0.2, 0, 0.3] });
  ctx.save(); ctx.globalAlpha = 0.5; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const bx = 960 + Math.sin(t * 1.1) * 300, by = 560 + Math.cos(t * 0.8) * 50;
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; const g = ctx.createRadialGradient(bx, by, 10, bx, by, 300); g.addColorStop(0, 'rgba(255,245,220,0.22)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.beginPath(); ctx.moveTo(640, 820); ctx.lineTo(bx - 150, by - 90); ctx.lineTo(bx + 150, by + 90); ctx.closePath(); ctx.fillStyle = 'rgba(255,245,220,0.05)'; ctx.fill(); ctx.restore();
  me(560, 1420, 2.0, { face: 'back', arms: [0, 0.35] });
  if (t >= tf) pop(t, tf, 960, 160, () => tag('YOU WILL FIND IT', 960, 170, C.fig, 44, 'center'), 0.3);
};
S.b8 = (t, seg) => {
  // in the black kitchen window: you, and right behind you, the mask and the knife
  const tr = wt(seg, 'reflection'), tb = wt(seg, 'behind'), k = ease(prog(t, tb - 0.2, 0.8));
  cam(t, seg.start, seg.end - seg.start + 1.6, 1.25, 1.75, 1020, 470, () => {
    kitchen(t, { block: false, reflect: (x, y, w, h) => {
      ctx.save(); ctx.globalAlpha = 0.42; me(x + w * 0.36, y + h + 240, 1.3, { face: 'front' }); ctx.restore();
      if (k > 0) { ctx.save(); ctx.globalAlpha = 0.65 * k; myers(x + w * 0.68, y + h + 470, 1.1, { knife: 2, red: prog(t, seg.end + 0.5, 0.3) }); ctx.restore(); }
    } });
  });
  me(700, 1560, 2.6, { face: 'back' });
};

// ---------- rule 3: do not hide in the closet ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'DO NOT HIDE IN THE CLOSET');
S.c1 = (t, seg) => {
  // everyone hides in the closet. He knows that.
  const tw = wt(seg, 'want'), tk = wt(seg, 'knows'), k = ease(prog(t, tw, 1.4));
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.08, 960, 520, () => {
    black(); cutaway(t, { hot: t >= tk ? ['CLOSET'] : [] });
    me(lerp(700, 1040, k), 550, 0.62, { face: k > 0.98 ? 'front' : 'right', walk: k < 1 ? t * 12 : null });
    myers(1230, 850, 0.42, { knife: 1, tilt: t >= tk ? -0.3 * ease(prog(t, tk, 0.6)) : 0 });
    if (t >= tk) { ctx.save(); redGlow(12); ctx.setLineDash([12, 10]); const kk = ease(prog(t, tk, 0.5)); ln(1230, 630, lerp(1230, 1040, kk), lerp(630, 420, kk), 5, C.red); ctx.restore(); }
  });
};
S.c2 = (t, seg) => {
  // through the slats: a shape walks past, slowly, your knife in his hand
  const tw = wt(seg, 'walks'), k = prog(t, tw - 1.0, seg.end - tw + 1.6);
  slats(() => {
    cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.08, 960, 520, () => {
      ctx.fillStyle = '#2a2a31'; ctx.fillRect(-200, -200, W + 400, H + 400); rr(-200, 860, W + 400, 400, 0, '#24232a');
      for (let i = 0; i < 4; i++) { rr(150 + i * 480, 220, 230, 640, 2, '#121216'); rrS(150 + i * 480, 220, 230, 640, 2, '#3a3a42', 6); }
      const g = ctx.createRadialGradient(1500, 260, 20, 1500, 260, 900); g.addColorStop(0, 'rgba(170,190,230,0.2)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
      if (k > 0) myersSide(lerp(-250, 2150, k), 1010, 1.25, { walk: (t - tw) * 3.0, knife: 1 });
    });
  }, { gap: 30 });
};
S.c3 = (t, seg) => {
  // every door, one by one
  const tb = wt(seg, 'bathroom'), tl = wt(seg, 'laundry'), tg = wt(seg, 'guest');
  const op = [prog(t, tb - 0.2, 0.6), prog(t, tl - 0.2, 0.6), 0, prog(t, tg - 0.2, 0.6)].map(ease);
  hallway(t, { open: op, labels: [['BATHROOM', tb], ['LAUNDRY', tl], null, ['GUEST ROOM', tg, -110]],
    fig: at => { const d = lerp(0.4, 3.0, ease(prog(t, seg.start, seg.end - seg.start + 0.6))), p = at(960, 1130, d); myers(p[0], p[1], 1.55 / (1 + d), { back: true, walk: t * 3 }); } });
};
S.c4 = (t, seg) => {
  // the route through the house: the closet is always last
  const tl = wt(seg, 'last'), route = ['HALL', 'BATHROOM', 'GUEST ROOM', 'BEDROOM', 'LAUNDRY', 'KITCHEN', 'CLOSET'];
  const k = prog(t, seg.start, tl - seg.start), n = Math.floor(k * (route.length - 1)), f = k * (route.length - 1) - n;
  floorPlan(t, { checked: route.slice(1, Math.min(n + 1, route.length - 1)), hot: t >= tl ? 'CLOSET' : null });
  const a = roomC(route[Math.min(n, route.length - 1)]), b = roomC(route[Math.min(n + 1, route.length - 1)]);
  const x = lerp(a[0], b[0], ease(f)), y = lerp(a[1], b[1], ease(f));
  ctx.save(); redGlow(16); circ(x, y - 40, 16, C.red); noGlow(); ctx.restore();
  if (t >= tl) pop(t, tl, 1380, 560, () => tag('LAST', 1380, 570, C.red, 40, 'center'), 0.3);
};
S.c5 = (t, seg) => {
  // when he leaves a room, slip into it behind him
  const ts = wt(seg, 'slip'), tw = wt(seg, 'walks');
  const himK = ease(prog(t, tw - 0.2, 1.4)), meK = ease(prog(t, ts - 0.2, 1.0));
  floorPlan(t, { checked: ['BATHROOM', 'GUEST ROOM'] });
  const g = roomC('GUEST ROOM'), b = roomC('BEDROOM'), c = roomC('CLOSET');
  ctx.save(); redGlow(16); circ(lerp(g[0], b[0], himK), g[1] - 40, 16, C.red); noGlow(); ctx.restore();
  const yx = lerp(c[0], g[0] + 60, meK), yy = lerp(c[1], g[1] + 40, meK); glow(); circ(yx, yy, 16, C.fig); noGlow();
  if (t >= ts + 0.8) pop(t, ts + 0.8, g[0] + 60, g[1] + 110, () => tag('YOU', g[0] + 60, g[1] + 120, C.fig, 30, 'center'), 0.3);
};
S.c6 = (t, seg) => {
  // he never checks a room twice
  const tt = wt(seg, 'twice');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.25, 1250, 350, () => {
    floorPlan(t, { checked: ['BATHROOM', 'GUEST ROOM', 'BEDROOM'] });
    const g = roomC('GUEST ROOM'); glow(); circ(g[0] + 60, g[1] + 40, 16, C.fig); noGlow();
    stampMark(t, tt - 0.1, g[0], g[1] - 60, [['CHECKED', 44]], -0.12, '#0f0f11', 20);
  });
};
S.c7 = (t, seg) => {
  // stay in the closet: the last thing you see through the slats is white
  const tw = wt(seg, 'white'), k = ease(prog(t, tw - 1.6, 2.2));
  slats(() => {
    ctx.fillStyle = '#2a2a31'; ctx.fillRect(-200, -200, W + 400, H + 400); rr(-200, 860, W + 400, 400, 0, '#24232a');
    if (k < 0.2) { const g = ctx.createRadialGradient(1500, 260, 20, 1500, 260, 900); g.addColorStop(0, 'rgba(170,190,230,0.12)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400); }
    const s = lerp(1.2, 6.5, k * k); ctx.save(); ctx.globalAlpha = 0.9; myers(960, 1040 + 520 * s * k * 0.9, s, { knife: 1, red: prog(t, seg.end + 0.5, 0.3), glowA: 0.15 }); ctx.restore();
  }, { gap: 30 });
};

// ---------- rule 4: never check if he is dead ----------
S.d0 = (t, seg) => ruleCard(t, seg, 4, "NEVER CHECK IF HE'S DEAD");
function floorTop() { ctx.fillStyle = '#0e0c0a'; ctx.fillRect(-200, -200, W + 400, H + 400); for (let i = -2; i < 16; i++) { ln(-200, i * 90, W + 200, i * 90, 3, '#1a1714'); for (let j = 0; j < 6; j++) ln(((i * 137 + j * 410) % 2300) - 200, i * 90, ((i * 137 + j * 410) % 2300) - 200, i * 90 + 90, 2, '#171411'); } }
S.d1 = (t, seg) => {
  // a hanger, a needle, your own knife. He falls.
  const th = wt(seg, 'hanger'), tn = wt(seg, 'needle'), tk = wt(seg, 'knife'), tf = wt(seg, 'falls');
  if (t < tf - 0.15) {
    black();
    [[th, 'hanger', 'COAT HANGER', 420], [tn, 'needle', 'KNITTING NEEDLE', 960], [tk, 'knife', 'KITCHEN KNIFE', 1500]].forEach(([t0, ic, s, x]) => { if (t >= t0 - 0.1) pop(t, t0 - 0.1, x, 470, () => {
      rr(x - 200, 300, 400, 340, 22, '#0f0f11'); rrS(x - 200, 300, 400, 340, 22, '#3a3a3e', 4); icon6(ic, x, 450, 1.3); text(s, x, 610, '900 30px M', C.fig); }, 0.3); });
  } else {
    black(); rr(-200, 900, W + 400, 300, 0, '#0e0c0a'); ln(-200, 900, W + 400, 900, 3, '#262320');
    const k = ease(prog(t, tf - 0.15, 0.55));
    myersSide(1000, 900, 1.15, { lean: k * Math.PI / 2 * 0.98, knife: 1 });
  }
};
S.d2 = (t, seg) => {
  // from above: he lies there, he does not move, the mask still on
  const tm = wt(seg, 'mask');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.35, 760, 540, () => {
    floorTop();
    ctx.save(); ctx.translate(1100, 540); ctx.rotate(Math.PI / 2); myers(0, 360, 1.2, { knife: 1 }); ctx.restore();
    if (t >= tm) pop(t, tm, 560, 330, () => tag('THE MASK IS STILL ON', 560, 340, C.fig, 30, 'center'), 0.3);
  });
};
S.d3 = (t, seg) => {
  // do not go closer, do not check his breathing, do not take the knife
  const tc = wt(seg, 'closer'), tb = wt(seg, 'breathing'), tk = wt(seg, 'take');
  ctx.save(); ctx.globalAlpha = 0.5; floorTop(); ctx.translate(1350, 560); ctx.rotate(Math.PI / 2); myers(0, 360, 1.2, { knife: 1 }); ctx.restore();
  listCard(120, 230, 960, 580);
  noRow(t, tc - 0.25, tc + 0.3, 180, 350, 'step', 'GO CLOSER', 46);
  noRow(t, tb - 0.25, tb + 0.3, 180, 520, 'breath', 'CHECK HIS BREATHING', 46);
  noRow(t, tk - 0.25, tk + 0.3, 180, 690, 'hand', 'TAKE THE KNIFE', 46);
};
function roomSide(t) {
  black(); rr(-200, 900, W + 400, 300, 0, '#0e0c0a'); ln(-200, 900, W + 400, 900, 3, '#262320');
  rr(-200, 0, W + 400, 900, 0, '#0b0b0d');
  rr(1640, 300, 230, 600, 2, '#020202'); rrS(1640, 300, 230, 600, 2, '#26262a', 8);    // the door out
}
S.d4 = (t, seg) => {
  // walk out backwards, eyes on him
  const tb = wt(seg, 'backwards'), te = wt(seg, 'eyes'), k = ease(prog(t, tb - 0.3, seg.end - tb + 0.6));
  roomSide(t); myersSide(500, 900, 1.15, { floor: 1, sit: 0, knife: 1 });
  const x = lerp(1180, 1560, k); me(x, 900, 1.25, { face: 'left', walk: k > 0 && k < 1 ? -t * 8 : null });
  if (t >= te) { ctx.save(); ctx.setLineDash([14, 12]); const kk = ease(prog(t, te, 0.4)); ln(x - 20, 470, lerp(x - 20, 420, kk), lerp(470, 820, kk), 5, C.fig); ctx.restore(); pop(t, te, x, 280, () => tag('EYES ON HIM', x, 290, C.fig, 36, 'center'), 0.3); }
  if (t >= tb) { for (let i = 0; i < 3; i++) { const a = prog(t, tb + i * 0.15, 0.3); ctx.save(); ctx.globalAlpha *= a * 0.7; pth(`M${x + 100 + i * 40},842 l26,18 l-26,18 z`, C.fig); ctx.restore(); } }
};
S.d5 = (t, seg) => {
  // the moment you turn around
  const ta = wt(seg, 'around');
  cam(t, seg.start, seg.end - seg.start + 1.0, 1.0, 1.08, 1100, 600, () => {
    roomSide(t); myersSide(500, 900, 1.15, { floor: 1, sit: 0, knife: 1 });
    me(1560, 900, 1.25, { face: t >= ta ? 'back' : 'left' });
  });
};
S.d6 = (t, seg) => {
  // behind you, very slowly, he sits up
  const ts = wt(seg, 'sits');
  cam(t, seg.start, seg.end - seg.start + 1.0, 1.08, 1.25, 900, 640, () => {
    roomSide(t); myersSide(500, 900, 1.15, { floor: 1, sit: ease(prog(t, ts - 0.6, 2.4)), knife: 1, red: prog(t, ts + 1.6, 0.4) });
    me(1560, 900, 1.25, { face: 'back' });
  });
};
S.d7 = (t, seg) => {
  // he always gets back up: the mask rises into the frame
  const k = ease(prog(t, seg.start - 0.1, 1.6));
  black(); const g = ctx.createRadialGradient(960, 400, 50, 960, 500, 800); g.addColorStop(0, 'rgba(255,250,235,0.06)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  myers(960, lerp(3400, 2560, k), 3.6, { red: prog(t, seg.end + 0.2, 0.3) });
};

// ---------- emergency protocol ----------
S.e0 = (t, seg) => emergencyCard(t, seg);
S.e1 = (t, seg) => {
  // cornered: he stands in front of you, knife up
  const tw = wt(seg, 'work');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.1, 1100, 560, () => {
    black(); rr(-200, 920, W + 400, 300, 0, '#0e0c0a'); pth('M1300,0 L1920,0 L1920,1080 L1300,920 Z', '#0d0d10'); ln(1300, 0, 1300, 920, 4, '#26262a');
    me(1560, 960, 1.4, { face: 'left', arms: [0.4, 0.4] });
    myers(820, 1020, 1.18, { knife: 2 });
  });
  if (t >= tw) pop(t, tw, 420, 160, () => tag('DOES NOT WORK', 420, 170, C.red, 50, 'center'), 0.3);
};
S.e2 = (t, seg) => {
  // six shots, he goes over the balcony; you look down: the lawn is empty
  const ts = wt(seg, 'six'), tb = wt(seg, 'balcony'), tl = wt(seg, 'look'), te = wt(seg, 'empty');
  if (t < tl - 0.1) {
    black();
    cam(t, seg.start, tl - seg.start, 1.0, 1.08, 1060, 520, () => {
      rr(440, 20, 1180, 480, 0, '#111214'); rrS(440, 20, 1180, 480, 0, '#26272b', 4);   // the back of the house, upstairs
      rr(600, 160, 220, 320, 2, '#050505');                                               // your bedroom door, open
      rr(860, 480, 640, 24, 0, '#2a2a2e'); for (let i = 0; i < 13; i++) rr(880 + i * 48, 380, 8, 100, 2, '#2a2a2e'); rr(860, 370, 640, 14, 3, '#2a2a2e');   // balcony, open at the right end
      rr(-200, 800, W + 400, 400, 0, '#121812'); for (let i = 0; i < 40; i++) ln(-100 + i * 55, 800, -90 + i * 55, 788, 3, '#1b231b');
      let hits = 0; for (let i = 0; i < 6; i++) if (t >= ts + i * 0.32) hits = i + 1;
      const fall = ease(prog(t, tb - 0.4, 0.7)), drop = prog(t, tb + 0.2, 0.5);
      if (drop < 1) { const x = 1180 + hits * 30 + fall * 200, y = lerp(480, 880, drop * drop);
        myersSide(x, y, 0.62, { dir: -1, lean: -(hits * 0.04 + fall * 0.5 + drop * 1.0), knife: 1 }); }
      else myersSide(1540, 880, 0.62, { dir: -1, floor: 1, sit: 0, knife: 1 });
      for (let i = 0; i < 6; i++) { const ft = ts + i * 0.32; if (t >= ft && t < ft + 0.1) { ctx.save(); glow('rgba(255,240,200,0.9)', 30); for (let r = 0; r < 8; r++) { const a = r * Math.PI / 4; ln(810, 330, 810 + Math.cos(a) * 40, 330 + Math.sin(a) * 40, 6, '#fff3d6'); } noGlow(); ctx.restore(); } }
      me(700, 500, 0.95, { face: 'right', arms: [0, 0.72] });
    });
  } else {
    // from above: the grass, the shape he left, and no one
    cam(t, tl - 0.1, seg.end - tl + 1, 1.0, 1.2, 960, 540, () => {
      ctx.fillStyle = '#0a0d0a'; ctx.fillRect(-200, -200, W + 400, H + 400);
      for (let i = 0; i < 260; i++) { const gx = hash(i * 1.3) * 2100 - 90, gy = hash(i * 2.9) * 1200 - 60; ln(gx, gy, gx + 4, gy - 14, 3, '#162016'); }
      ctx.save(); ctx.translate(960, 560); ctx.rotate(Math.PI / 2 - 0.2); ctx.setLineDash([12, 12]); ctx.globalAlpha = 0.6;
      pthS('M-60,-560 C-80,-520 -70,-470 -56,-450 L-120,-440 L-150,-300 L-90,-270 L-60,-20 L60,-20 L90,-270 L150,-300 L120,-440 L56,-450 C70,-470 80,-520 60,-560 C30,-600 -30,-600 -60,-560 Z', '#8a9a8a', 5); ctx.restore();
      if (t >= te) pop(t, te, 960, 160, () => tag('EMPTY', 960, 170, C.red, 52, 'center'), 0.3);
    });
  }
  noHead(t, seg, 'gun', 'SHOOT HIM', te + 0.3);
};
S.e3 = (t, seg) => {
  // you lock the door; the camera pulls back: he was already inside
  const tl = wt(seg, 'lock'), ti = wt(seg, 'inside'), k = ease(prog(t, ti - 0.6, 1.0));
  cam(t, 0, 1, lerp(1.7, 1.0, k), lerp(1.7, 1.0, k), 1420, 560, () => {
    black(); rr(-200, 920, W + 400, 300, 0, '#0e0c0a'); rr(1220, 220, 360, 700, 2, '#1d1d20'); rrS(1220, 220, 360, 700, 2, '#2e2e33', 6);
    rr(1260, 560, 40, 60, 8, '#55555a'); ctx.save(); ctx.translate(1280, 590); ctx.rotate(t >= tl ? Math.PI / 2 : 0); rr(-5, -20, 10, 40, 3, '#222'); ctx.restore();
    me(1440, 1000, 1.5, { face: 'back', arms: [0, 0.45] });
    myers(680, 1000, 1.25, { knife: 1, dark: 0.25 });
  });
  noHead(t, seg, 'lock', 'LOCK THE DOOR', ti + 0.2);
};
S.e4 = (t, seg) => {
  // drive: there is a white face in the back seat
  const tf = wt(seg, 'face');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, lerp(1.0, 1.9, 1), 960, 200, () => {});
  ctx.save(); const z = lerp(1.0, 2.2, ease(prog(t, tf - 1.0, 1.4))); ctx.translate(960, 200); ctx.scale(z, z); ctx.translate(-960, -200);
  carView(t, { face: ease(prog(t, tf - 0.4, 0.5)), red: prog(t, tf + 0.8, 0.3) }); ctx.restore();
  noHead(t, seg, 'car', 'DRIVE AWAY', tf + 0.4);
};
S.e5 = (t, seg) => {
  // scream: the neighbours step out, think it's a prank, and clap
  const ts = wt(seg, 'scream'), tn = wt(seg, 'neighbors'), tc = wt(seg, 'clap');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.06, 960, 560, () => {
    const g = ctx.createLinearGradient(0, 0, 0, 700); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    [[280, 0], [960, 1], [1640, 2]].forEach(([x, i]) => { house(x, 640, 520, { win: [0.6, 0.4, 0.7, 0.5], porch: 1, pumpkins: 1, door: t >= tn + i * 0.2 ? 1 : 0 });
      if (t >= tn + i * 0.2 + 0.2) { const cl = t >= tc ? Math.abs(Math.sin((t - tc) * 9)) : 0; fadeIn(t, tn + i * 0.2 + 0.2, () => me(x - 30 + (i - 1) * 60, 646, 0.42, { face: 'front', arms: [0.45 + cl * 0.15, 0.45 + cl * 0.15] }), 0.3);
        if (t >= tc) { ctx.save(); ctx.globalAlpha = 0.7 * (0.5 + 0.5 * Math.sin((t - tc) * 18)); text('CLAP', x - 30 + (i - 1) * 60, 470, '900 26px M', C.fig); ctx.restore(); } } });
    rr(-200, 640, W + 400, 500, 0, NIGHT.street); rr(-200, 900, W + 400, 300, 0, NIGHT.grass);
    me(700, 1000, 1.0, { face: 'front', arms: [0.8, 0.8] });
    if (t >= ts) for (let i = 0; i < 3; i++) { ctx.save(); ctx.globalAlpha = 0.6 * (1 - ((t - ts) * 1.2 + i / 3) % 1); ctx.beginPath(); ctx.arc(700, 640, 80 + (((t - ts) * 1.2 + i / 3) % 1) * 200, -2.4, -0.7); ctx.strokeStyle = C.fig; ctx.lineWidth = 6; ctx.stroke(); ctx.restore(); }
    myers(1200, 1000, 0.95, { knife: 2 });
  });
  noHead(t, seg, 'scream', 'SCREAM', tc + 0.3);
};
S.e6 = (t, seg) => {
  // only one thing works
  black(); const g = ctx.createRadialGradient(960, 520, 20, 960, 520, 500); g.addColorStop(0, 'rgba(255,255,255,0.08)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  pop(t, seg.start, 960, 500, () => { rr(780, 330, 360, 360, 26, '#0f0f11'); rrS(780, 330, 360, 360, 26, C.fig, 6); check(960, 510, 90, prog(t, wt(seg, 'works'), 0.4)); }, 0.35);
  if (t >= wt(seg, 'one')) pop(t, wt(seg, 'one'), 960, 800, () => spaced('ONLY ONE THING WORKS', 960, 810, '900 50px M', C.fig, 6), 0.3);
};
S.e7 = (t, seg) => {
  // say his name
  black(); ctx.save(); ctx.globalAlpha = 0.2; maskHead(960, 520, 5.2, { glowA: 0.1 }); ctx.restore();
  pop(t, seg.start, 960, 540, () => spaced('SAY HIS NAME.', 960, 570, '900 120px M', C.fig, 10), 0.35);
};
S.e8 = (t, seg) => {
  // "Michael." The knife is up.
  cam(t, seg.start, 2.2, 1.0, 1.06, 960, 500, () => { black(); myers(1380, 1900, 2.3, { knife: 2, dark: 0.2 }); });
  ctx.save(); ctx.globalAlpha = 0.8; ctx.fillStyle = '#000'; ctx.fillRect(0, 380, 1100, 300); ctx.restore();
  fadeIn(t, wt(seg, 'michael') - 0.05, () => spaced('MICHAEL.', 560, 580, '900 150px M', C.fig, 14), 0.4);
};
S.e9 = (t, seg) => {
  // six years old; and the knife stops in the air
  const t6 = wt(seg, 'six'), tk = wt(seg, 'knife');
  if (t < tk - 0.1) {
    cam(t, seg.start, tk - seg.start, 1.0, 1.1, 960, 600, () => {
      black(); const g = ctx.createRadialGradient(960, 700, 20, 960, 700, 600); g.addColorStop(0, 'rgba(255,255,255,0.06)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      rr(-200, 900, W + 400, 300, 0, '#0c0c0e');
      me(960, 900, 0.95, { face: 'front' }); pth('M920,602 L1000,602 L960,505 Z', C.sec); circ(960, 500, 8, C.sec);   // a small boy in a costume hat
      if (t >= t6) pop(t, t6, 960, 320, () => tag('AGE 6', 960, 330, C.fig, 52, 'center'), 0.3);
    });
  } else {
    cam(t, tk - 0.1, seg.end - tk + 1, 1.3, 1.36, 760, 380, () => { black(); myers(1180, 1900, 2.3, { knife: 2 }); });
    const fx = 760, fy = 250; for (let i = 0; i < 4; i++) { const a = -0.6 + i * 0.4; ln(fx + Math.cos(a) * 170, fy + Math.sin(a) * 170, fx + Math.cos(a) * 230, fy + Math.sin(a) * 230, 6, C.fig); }
    pop(t, wt(seg, 'stops'), 420, 420, () => tag('STOPPED', 420, 430, C.fig, 50, 'center'), 0.3);
  }
};
S.e10 = (t, seg) => {
  // say it again, like his mother: calm, tired
  const tc = wt(seg, 'calm'), tt = wt(seg, 'tired');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.08, 960, 560, () => {
    black(); rr(-200, 940, W + 400, 300, 0, '#0c0c0e');
    myers(620, 1000, 1.35, { knife: 2 });
    me(1340, 1000, 1.45, { face: 'left' });
  });
  if (t >= tc) pop(t, tc, 1350, 200, () => tag('CALM.', 1250, 210, C.fig, 50, 'center'), 0.3);
  if (t >= tt) pop(t, tt, 1560, 200, () => tag('TIRED.', 1560, 210, C.fig, 50, 'center'), 0.3);
};
S.e11 = (t, seg) => {
  // "Michael. Go home."
  const tg = wt(seg, 'go');
  cam(t, seg.start, seg.end - seg.start + 1.4, 1.0, 1.05, 960, 540, () => { black(); ctx.save(); ctx.globalAlpha = 0.35; myers(1500, 1900, 2.3, { knife: 2, tilt: -0.2 * ease(prog(t, seg.end, 0.8)) }); ctx.restore(); });
  spaced('MICHAEL.', 760, 470, '900 110px M', C.fig, 12);
  if (t >= tg - 0.05) pop(t, tg - 0.05, 760, 640, () => spaced('GO HOME.', 760, 660, '900 130px M', C.fig, 12), 0.35);
};
S.e12 = (t, seg) => {
  // he tilts his head, and lowers the knife
  const tt = wt(seg, 'tilts'), tl = wt(seg, 'lowers');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.1, 960, 520, () => {
    black(); rr(-200, 940, W + 400, 300, 0, '#0c0c0e');
    myers(960, 1260, 1.9, { knife: 2, tilt: -0.3 * ease(prog(t, tt, 1.0)), lower: ease(prog(t, tl, 1.0)) });
  });
};
S.e13 = (t, seg) => {
  // out of your house, across the street, into the empty house on the corner
  const tn = wt(seg, 'nobody'), te = wt(seg, 'empty'), k = prog(t, seg.start + 0.2, te - seg.start + 0.4);
  const path = [[640, 1040, 0.9], [900, 900, 0.72], [1180, 720, 0.52], [1560, 650, 0.44], [1835, 600, 0.4]];
  const n = Math.min(path.length - 2, Math.floor(k * (path.length - 1))), f = k * (path.length - 1) - n;
  const p = path[n].map((v, i) => lerp(v, path[n + 1][i], f));
  const inside = k >= 1;
  streetScene(t, { cam: [1.15, 1200, 560], him: null, mailbox: false,
    houses: [[-120, 0.5, [0, 0.8, 0.6, 0]], [340, 0.48, [0.7, 0, 0, 0.9]], [800, 0.5, [0, 0, 0.8, 0.6]], [1300, 0.52, [0.8, 0.5, 0, 0]]],
    emptyHouse: () => house(1860, 600, 420, { old: true, chimney: false, door: k > 0.9 && t < te + 1.0 ? 1 : 0 }),
    near: () => { if (!inside) myersSide(p[0], p[1], p[2], { walk: t * 3.2, knife: 1, dir: 1 });
      if (t >= tn) pop(t, tn, 1860, 300, () => tag('EMPTY FOR YEARS', 1860, 310, C.fig, 28, 'center'), 0.3); } });
};
S.e14 = (t, seg) => {
  // do not follow, do not watch which window
  const tf = wt(seg, 'follow'), tw = wt(seg, 'watch');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.06, 960, 520, () => {
    const g = ctx.createLinearGradient(0, 0, 0, 900); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    house(1180, 920, 1000, { old: true, chimney: false }); rr(-200, 920, W + 400, 300, 0, NIGHT.grass);
  });
  listCard(60, 300, 560, 400);
  noRow(t, tf - 0.25, tf + 0.3, 100, 410, 'step', 'FOLLOW HIM', 40);
  noRow(t, tw - 0.25, tw + 0.3, 100, 590, 'eye', 'WATCH WINDOWS', 40);
};

// ---------- the morning, and every Halloween after ----------
S.f1 = (t, seg) => {
  // grey morning: smashed pumpkins, wrappers, police tape
  ctx.save(); streetScene(t, { cam: [1.25, 900, 600], him: null, morning: true, light: 0, dimHouses: true, houses: [[-120, 0.5, [0, 0, 0, 0]], [340, 0.48, [0, 0, 0, 0]], [800, 0.5, [0, 0, 0, 0]], [1300, 0.52, [0, 0, 0, 0]], [1820, 0.5, [0, 0, 0, 0]]],
    near: () => { for (let i = 0; i < 22; i++) { const x = hash(i * 4.1) * 1800, y = 650 + hash(i * 6.3) * 140; ctx.save(); ctx.translate(x, y); ctx.rotate(hash(i) * 3); rr(-10, -5, 20, 10, 2, i % 3 ? '#5a5a5a' : '#8a8a8a'); ctx.restore(); }
      jackO(560, 830, 30, 0, true); jackO(1320, 836, 26, 0, true); } });
  ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = 'rgba(70,75,85,0.35)'; ctx.fillRect(0, 0, W, H); ctx.restore();   // grey dawn
  if (t >= wt(seg, 'police')) { const k = ease(prog(t, wt(seg, 'police') - 0.1, 0.4)); ctx.save(); ctx.translate(960, 760); ctx.rotate(-0.08); ctx.globalAlpha = k; rr(-1100, -30, 2200, 60, 0, '#d8d8d8');
    ctx.beginPath(); ctx.rect(-1100, -30, 2200, 60); ctx.clip(); for (let i = -10; i < 10; i++) text('POLICE LINE  DO NOT CROSS', i * 520 + ((t * 30) % 520), 14, '900 32px M', '#111', 'left'); ctx.restore(); }
};
S.f2 = (t, seg) => {
  // your knife is back in the block, clean
  const tb = wt(seg, 'back'), k = ease(prog(t, tb - 0.4, 0.7)), tc = wt(seg, 'clean');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.1, 880, 640, () => {
    black(); ctx.save(); ctx.globalCompositeOperation = 'lighter'; const g = ctx.createLinearGradient(0, 0, W, 0); g.addColorStop(0, 'rgba(120,130,150,0.12)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
    rr(-200, 960, W + 400, 300, 0, '#1a1a1d');
    blockClose(t, { x: 900, y: 1010, s: 1.5, out: k < 1 ? [0, 260 * (1 - k)] : null, fade: k });
    // (the handle slides back in: blockClose draws it pulled out)
    if (t >= tc) { const gx = 640, gy = 330, a = 1 - prog(t, tc + 0.4, 0.6); ctx.save(); ctx.globalAlpha = a; glow('rgba(255,255,255,1)', 30); for (let i = 0; i < 4; i++) { const an = i * Math.PI / 2; ln(gx, gy, gx + Math.cos(an) * 40, gy + Math.sin(an) * 40, 5, '#fff'); } noGlow(); ctx.restore();
      pop(t, tc, 1300, 300, () => tag('CLEAN', 1300, 310, C.fig, 50, 'center'), 0.3); }
  });
};
const inWindow = (o = {}) => (x, y, w, h) => { ctx.fillStyle = '#020202'; ctx.fillRect(x, y, w, h); const s = h * 0.5 / 150; myers(x + w / 2, y + h * 0.42 + 563 * s, s, o); };
S.f3 = (t, seg) => {
  // every Halloween since: he stands in the dark window of the empty house
  const th = wt(seg, 'halloween'), tl = wt(seg, 'looks');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.12, 1100, 420, () => {
    const g = ctx.createLinearGradient(0, 0, 0, 900); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    house(1100, 960, 1000, { old: true, chimney: false, who: { win: 1, fn: inWindow({}) } }); rr(-200, 960, W + 400, 300, 0, NIGHT.grass);
    if (t >= tl) { ctx.save(); ctx.setLineDash([14, 12]); const k = ease(prog(t, tl, 0.6)); ln(1355, 520, lerp(1355, 300, k), lerp(520, 980, k), 5, C.fig); ctx.restore(); }
  });
  if (t >= th) { const n = Math.min(3, 1 + Math.floor((t - th) / 0.5)); pop(t, th, 300, 260, () => { rr(180, 140, 240, 250, 16, '#e6e6e6'); rr(180, 140, 240, 70, 16, '#d61f1f'); text('OCT', 300, 196, '900 40px M', '#fff'); text('31', 300, 330, '900 110px M', '#111');
    text(n === 1 ? '1 YEAR' : n + ' YEARS', 300, 450, '900 34px M', C.fig); }, 0.3); }
};
S.f4 = (t, seg) => {
  // he never comes over; he listens to his mother
  const to = wt(seg, 'over'), tm = wt(seg, 'mother');
  cam(t, seg.start, seg.end - seg.start + 0.6, 1.0, 1.05, 960, 520, () => {
    const g = ctx.createLinearGradient(0, 0, 0, 800); g.addColorStop(0, NIGHT.sky0); g.addColorStop(1, '#000'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    house(420, 700, 620, { old: true, chimney: false, who: { win: 1, fn: inWindow({}) } });
    house(1500, 700, 620, { win: [0.9, 0.6, 0.4, 0], porch: 1, pumpkins: 1 });
    rr(-200, 700, W + 400, 140, 0, NIGHT.street); rr(-200, 840, W + 400, 300, 0, NIGHT.grass);
    if (t >= to) { ctx.save(); ctx.setLineDash([16, 12]); const k = ease(prog(t, to, 0.5)); ln(560, 760, lerp(560, 1360, k), 760, 6, C.fig); ctx.restore(); redX(960, 760, 50, prog(t, to + 0.5, 0.3)); }
  });
  if (t >= tm) pop(t, tm, 960, 160, () => tag('HE LISTENS TO HIS MOTHER', 960, 170, C.fig, 40, 'center'), 0.3);
};
S.f5 = (t, seg) => {
  // this year, for the first time, he raises his hand
  const th = wt(seg, 'raises'), k = ease(prog(t, th - 0.2, 1.4));
  cam(t, seg.start, seg.end - seg.start + 1.4, 1.0, 1.15, 960, 500, () => {
    black(); rr(560, 140, 800, 760, 4, '#030303');
    ctx.save(); ctx.beginPath(); ctx.rect(560, 140, 800, 760); ctx.clip(); myers(960, 1640, 2.0, { wave: k * 0.75 }); ctx.restore();
    rrS(560, 140, 800, 760, 4, '#2a2a2d', 26); ln(500, 230, 860, 120, 26, '#2b2622'); ln(1080, 900, 1420, 780, 26, '#2b2622');   // a board across each corner
  });
};
S.f6 = (t, seg) => {
  // he is waving
  cam(t, seg.start - 0.1, seg.end - seg.start + 1.6, 1.15, 1.22, 960, 500, () => {
    black(); rr(560, 140, 800, 760, 4, '#030303');
    ctx.save(); ctx.beginPath(); ctx.rect(560, 140, 800, 760); ctx.clip(); myers(960, 1640, 2.0, { wave: 1, waveT: t - seg.start }); ctx.restore();
    rrS(560, 140, 800, 760, 4, '#2a2a2d', 26); ln(500, 230, 860, 120, 26, '#2b2622'); ln(1080, 900, 1420, 780, 26, '#2b2622');
  });
};
S.f7 = (t, seg) => {
  // do not wave back: your hand comes up, and stops
  const tw = wt(seg, 'wave'), k = ease(prog(t, seg.start, 1.0));
  lookOut(t, { z: 1.9, f: [1700, 470], him: null, houses: [[340, 0.48, [0.7, 0, 0, 0.9]], [800, 0.5, [0, 0, 0.8, 0.6]], [1300, 0.52, [0.8, 0.5, 0, 0]]],
    emptyHouse: () => house(1860, 600, 420, { old: true, chimney: false, who: { win: 1, fn: inWindow({ wave: 1, waveT: t }) } }) });
  ctx.save(); ctx.translate(800, lerp(1400, 860, k)); glow('rgba(255,255,255,0.25)', 16); rr(-80, 0, 160, 220, 50, C.fig); for (let i = 0; i < 4; i++) rr(-80 + i * 42, -150 + Math.abs(i - 1.5) * 18, 34, 170, 17, C.fig); rr(-150, 20, 40, 130, 20, C.fig); ctx.restore(); noGlow();
  if (t >= tw) redX(800, 820, 190, prog(t, tw, 0.35));
};
// the file closes
S.f8 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore();
  });
};
// sign-off: the rules once more, the stamp, and the picture sinks into the dark around it
S.f9 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts, dk = ease(prog(t, ts + 0.5, 1.0));
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9, -9], fillT: [-9, -9, -9, -9, -9] });
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

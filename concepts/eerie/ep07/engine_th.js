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
  if (name === 'fist') { rr(-34, -34, 68, 64, 18, col); for (let i = 1; i < 4; i++) ln(-34 + i * 17, -34, -34 + i * 17, -10, 3, '#ff2b2b'); }
  ctx.restore();
}
const RULES = [['self', 'DO NOT TELL THEM ABOUT YOURSELF', '', ['DO NOT TELL THEM', 'ABOUT YOURSELF']], ['truth', 'DO NOT TELL THE TRUTH', '', ['DO NOT TELL', 'THE TRUTH']], ['ask', 'DO NOT SAY YOU HAVE NO QUESTIONS', '', ['DO NOT SAY YOU', 'HAVE NO QUESTIONS']], ['warn', 'EMERGENCY PROTOCOL', 'HOW TO FIGHT BACK']];
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
// ---------- EP07 scenes: "If Your Interviewer Ever Asks 'What Is Your Greatest Weakness?'" ----------
const ev = type => window.TL.events.filter(e => e.type === type);
const nextStart = seg => { const n = window.TL.segments.find(s => s.start > seg.start + 0.01); return n ? n.start : seg.end + 0.7; };
const blackAfter = (t, t0) => { if (t >= t0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); } };
const zk = (t, t0, d, z0, z1) => lerp(z0, z1, ease((t - t0) / d));
const black = () => { ctx.fillStyle = '#000'; ctx.fillRect(-200, -200, W + 400, H + 400); };
const typed = (s, t, t0, cps = 28) => s.slice(0, Math.max(0, Math.floor((t - t0) * cps)));
// a close-up: (cx, cy) is brought to the centre of the screen at zoom z
function focus(t, t0, d, z0, z1, cx, cy, fn) { const z = zk(t, t0, d, z0, z1); ctx.save(); ctx.translate(W / 2, H / 2 - 40); ctx.scale(z, z); ctx.translate(-cx, -cy); fn(); ctx.restore(); }
const CLOCK = [1640, 260], AC = [220, 285];
const segDur = seg => nextStart(seg) - seg.start;
function brackets(x, y, w, h, a, col = C.fig) {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha *= a; const L = 34;
  for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const cx = x + sx * w / 2, cy = y + sy * h / 2; poly([[cx, cy - sy * L], [cx, cy], [cx - sx * L, cy]], 6, col); }
  ctx.restore();
}
// ---------- the interview room ----------
// interviewers sit at x = 560 / 960 / 1360 behind the desk; their feet at FEET (hidden), desk top at DESK_Y
const IX = [560, 960, 1360], FEET = 905, DESK_Y = 620;
const HEAD = i => [IX[i], FEET - 300 - 276];
// o.arms: one mode or an array of three; o.eyes (middle, 0..1); o.lean, o.tilt (middle); o.me: your back in the foreground; o.stand 0..1; o.who [bools]
function room(t, o = {}) {
  roomWall({ floor: 900, clock: o.clock, ac: o.ac, secRed: o.secRed, door: o.door });
  // a soft overhead light on the desk
  const g = ctx.createRadialGradient(960, 260, 40, 960, 520, 900); g.addColorStop(0, 'rgba(255,255,255,0.10)'); g.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
  if (o.door) roomDoor(t, o.door);
  const st = ease(o.stand || 0);
  for (let i = 0; i < 3; i++) {
    if (o.who && !o.who[i]) { if (o.chairs) officeChair(IX[i], 905, 0.82); continue; }
    const arms = Array.isArray(o.arms) ? o.arms[i] : (o.arms || 'board');
    suit(IX[i], FEET - st * 110, 1, { arms, wt: t + i * 1.7, eyes: i === 1 ? (o.eyes ?? 1) : 0, lean: i === 1 ? o.lean : 0, tilt: i === 1 ? o.tilt : 0,
      shake: o.shake ? o.shake[i] : 0, t, lines: o.lines, under: o.under, up: o.up });
  }
  desk(260, 1660, DESK_Y, { n: 3 });
  if (o.me) meBack(o.meX ?? 960, 1330, 1.3);
}
// a door in the right wall: o = { lock: 0..1 red padlock, open: 0..1 }
function roomDoor(t, d) {
  rr(1700, 360, 170, 540, 4, '#0d0d0f'); rrS(1700, 360, 170, 540, 4, '#55555c', 4); circ(1720, 640, 8, '#9a9aa0');
  spaced('EXIT', 1785, 330, '900 30px M', '#6a6a72', 8);
  if (d.lock > 0) { ctx.save(); ctx.globalAlpha *= d.lock; const red = d.open ? 1 - d.open : 1;
    ctx.translate(1785, 620); ctx.beginPath(); ctx.arc(0, -30 - 30 * (d.open || 0), 26, Math.PI, 0); ctx.lineWidth = 10; ctx.strokeStyle = red > 0.5 ? C.red : C.fig; ctx.stroke();
    red > 0.5 ? redGlow(20) : glow(); rr(-40, -30, 80, 66, 10, red > 0.5 ? C.red : C.fig); noGlow(); circ(0, 0, 8, '#000'); ctx.restore(); }
}
// a "does not work" header at the top left with a red X on the icon at tx
function noHead(t, seg, ic, label, tx) {
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  slideIn(t, seg.start, -40, 0, () => { const w = 190 + label.length * 31; ctx.save(); ctx.globalAlpha *= 0.88; rr(60, 60, w, 130, 18, '#050505'); ctx.restore(); rrS(60, 60, w, 130, 18, '#2a2a2d', 3);
    icon7(ic, 125, 125, 0.5); text(label, 200, 142, '900 46px M', C.fig, 'left'); redX(125, 125, 48, prog(t, tx, 0.3)); }, 0.35);
  ctx.restore();
}
const TRIO = [1310, 1530, 1750];
function trio(t, o = {}) {   // the three standing in the dark (rule 4)
  const xs = o.xs || TRIO, ss = o.ss || [0.8, 0.8, 0.8];
  for (let i = 0; i < 3; i++) { if (o.who && !o.who[i]) continue;
    if (o.fold && o.fold[i] > 0.97) continue;
    suit(xs[i], o.y ?? 900, ss[i], { arms: o.arms || 'board', eyes: i === 1 ? (o.eyes ?? 1) : 0, wt: t + i, shake: o.shake ? o.shake[i] : 0, t, fold: o.fold ? o.fold[i] : 0, lines: o.lines, under: o.under, up: o.up }); }
}
// the night bedroom with you in bed and them at the foot of it
function night(t, o = {}) {
  bedroomNight({ gapGlow: o.gapGlow, time: o.time });
  bed(360, 900, 1.3, o.bed || 'woke', { look: 1 });
  if (o.trio !== false) trio(t, o);
}

// ---------- hook ----------
S.h1 = (t, seg) => {
  // frame 0: the panel, the question already asked; the middle one's eyes are red
  const td = wt(seg, 'do');
  cam(t, 0, seg.end + 0.6, 1.0, 1.1, 960, 420, () => room(t, { me: true, arms: ['board', 'desk', 'board'] }));
  if (t < td - 0.1) say(t, -1, 960, 130, 'WHAT IS YOUR GREATEST WEAKNESS?', 960, 250, 50);
  else pop(t, td - 0.1, 960, 140, () => tag('DO NOT TELL THE TRUTH', 960, 150, C.red, 56, 'center'), 0.3);
};
function teaserBox(t, seg, w0, ic, word, y, x = 1600) {
  const tx = wt(seg, word);
  pop(t, w0, x, y, () => { ctx.save(); ctx.globalAlpha *= 0.85; rr(x - 140, y - 130, 280, 260, 22, '#000'); ctx.restore(); rrS(x - 140, y - 130, 280, 260, 22, C.fig, 5); icon7(ic, x, y, 1.0); }, 0.3);
  redX(x, y, 105, prog(t, tx + 0.25, 0.3));
}
const H2_HIT = 0.6, H2_BLACK = 0.4;
S.h2 = (t, seg) => {
  const ws = [[seg.start, wt(seg, 'never', 1), 'self', 'tell'], [wt(seg, 'never', 1), wt(seg, 'and'), 'ask', 'questions'], [wt(seg, 'and'), nextStart(seg), 'clock', 'back']];
  let i = 0; for (let k = 0; k < 3; k++) if (t >= ws[k][0]) i = k;
  const [w0, w1, ic, word] = ws[i], hit = w1 - H2_HIT, blk = w1 - H2_BLACK, d = t - hit;
  if (t < blk) {
    if (i === 0) {   // the clipboard: LIVES ALONE, underlined
      black(); cam(t, w0, blk - w0, 1.0, 1.2, 800, 520, () => clipboard(800, 540, 3.6, -0.05, { lines: [['NO. 117', 0], ['AGE  29', 0], ['LIVES ALONE', 0]], under: 2, up: prog(t, w0 + 0.6, 1.0) }));
    } else if (i === 1) {   // the clock runs back to nine
      black(); const k = ease(prog(t, w0 + 0.3, hit - w0 - 0.3)), m = lerp(47, -60 * 0, k);
      focus(t, w0, blk - w0, 2.6, 3.0, ...CLOCK, () => roomWall({ clock: [9, lerp(47, 0, k), 30 * (1 - k)], secRed: true, floor: 2000 }));
    } else {   // 3 AM: three of them at the foot of your bed
      cam(t, w0, blk - w0, 1.0, 1.15, 1100, 600, () => night(t, { eyes: prog(t, hit - 0.3, 0.3) }));
    }
    if (d > 0) { ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.35 * clamp(d / 0.2); ctx.fillStyle = '#ff1a1a'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  }
  blackAfter(t, blk);
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); teaserBox(t, seg, w0, ic, word, 250, i === 2 ? 300 : 1600); ctx.restore();
};

// ---------- rule 1: do not tell them about yourself ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT TELL THEM ABOUT YOURSELF');
S.a1 = (t, seg) => {
  // "Tell me about yourself." They have already read your résumé. Three times. Every page.
  const ta = wt(seg, 'already'), t3 = wt(seg, 'three'), te = wt(seg, 'every');
  if (t < ta - 0.1) {
    cam(t, seg.start, ta - seg.start, 1.25, 1.35, 700, 400, () => room(t, { arms: ['board', 'desk', 'desk'], eyes: 0.6 }));
    say(t, seg.start, 1080, 250, 'TELL ME ABOUT\nYOURSELF.', 660, 330, 54);
    return;
  }
  black();
  cam(t, ta, seg.end - ta + 0.7, 1.0, 1.08, 960, 480, () => {
    const n = t >= te ? 4 : 1, fk = ease(prog(t, te, 0.5));
    for (let i = n - 1; i >= 0; i--) resume(960 + (i - 1.5) * 150 * fk + (n === 1 ? 0 : 0), 520 + i * 6 * fk, 0.95, (i - 1.5) * 0.06 * fk, { marks: prog(t, ta + 0.2 + i * 0.1, 0.9) });
    for (let k = 0; k < 3; k++) if (t >= t3 + k * 0.22) pop(t, t3 + k * 0.22, 1500 + k * 46, 180, () => { ctx.save(); redGlow(16); ln(1500 + k * 46, 130, 1500 + k * 46, 230, 12, C.red); ctx.restore(); }, 0.2);
    if (t >= t3) pop(t, t3, 1300, 180, () => tag('READ', 1300, 196, C.fig, 40, 'right'), 0.25);
  });
};
S.a2 = (t, seg) => {
  // three versions of you on the chart; only one may leave the room
  const tc = wt(seg, 'checking'), ts = wt(seg, 'safe'), tr = wt(seg, 'room');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 520, () => {
    black();
    for (let i = 0; i <= 8; i++) { const y = 860 - i * 70; ln(260, y, 1660, y, 2, '#2a2a2e'); if (i % 2 === 0) text(`${150 + i * 10}`, 240, y + 8, '600 22px Plex', '#55555c', 'right'); }
    const V = [['A', { face: 'front', arms: [0.15, 0.15] }], ['B', { face: 'front', arms: [0, 0] }], ['C', { face: 'left', arms: [0, 0.9] }]];
    V.forEach(([lab, oo], i) => { const x = 560 + i * 400;
      slideIn(t, seg.start + 0.2 + i * 0.25, 0, 40, () => { me(x, 860, 1.45, oo); rr(x - 50, 880, 100, 56, 8, '#1a1a1d'); text(lab, x, 924, '900 40px M', C.fig); }, 0.4); });
    if (t >= tc) { const k = prog(t, tc, 0.4); brackets(960, 600, 300, 620, k); }
    if (t >= ts) { redX(560, 520, 90, prog(t, ts, 0.3)); redX(1360, 520, 90, prog(t, ts + 0.15, 0.3)); }
    if (t >= tr) pop(t, tr, 960, 150, () => { glow(); rr(810, 100, 300, 90, 14, C.fig); noGlow(); spaced('SAFE', 960, 165, '900 54px M', '#000', 10); }, 0.3);
  });
};
S.a3 = (t, seg) => {
  // the script: smile, your name, one sentence, stop
  const W4 = [wt(seg, 'smile'), wt(seg, 'name'), wt(seg, 'sentence'), wt(seg, 'stop')];
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.05, 960, 520, () => {
    black(); sitSide(520, 900, 1.35, { dir: 1 });
    ['SMILE.', 'SAY YOUR NAME.', 'ONE SENTENCE.', 'THEN STOP.'].forEach((l, i) => okRow(t, W4[i] - 0.15, 900, 230 + i * 170, l, 56));
  });
};
S.a4 = (t, seg) => {
  const th = wt(seg, 'hobbies'), tf = wt(seg, 'family'), tl = wt(seg, 'live');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.1, 1.18, 960, 420, () => room(t, { arms: 'write', eyes: 0.8 }));
  listCard(420, 210, 1080, 600);
  noRow(t, th - 0.25, th + 0.25, 480, 330, 'game', 'YOUR HOBBIES', 52);
  noRow(t, tf - 0.25, tf + 0.25, 480, 510, 'family', 'YOUR FAMILY', 52);
  noRow(t, tl - 0.25, tl + 0.25, 480, 690, 'pin', 'WHERE YOU LIVE', 52);
};
S.a5 = (t, seg) => {
  // the last candidate: "I live alone." He writes it down.
  const tw = wt(seg, 'wrote');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 520, () => {
    roomWall({ floor: 900, clockAt: [960, 150], acAt: [-600, 0] });
    sitSide(470, 900, 1.25, { dir: 1, hair: true });
    say(t, seg.start + 0.3, 520, 210, 'I LIVE ALONE.', 500, 330, 50);
    suit(1380, 905, 1.0, { arms: t >= tw - 0.2 ? 'write' : 'board', wt: t, eyes: 0 });
    desk(1080, 1680, DESK_Y, { n: 1 });
  });
};
S.a6 = (t, seg) => {
  // then he underlined it
  const tu = wt(seg, 'underlined'), up = prog(t, tu - 0.05, 0.7);
  black();
  cam(t, seg.start, seg.end - seg.start + 1.6, 1.0, 1.25, 900, 520, () => {
    clipboard(900, 560, 4.4, -0.04, { lines: [['NO. 117', 0], ['AGE  29', 0], ['LIVES ALONE', up > 0.9 ? 1 : 0]], under: 2, up });
    ctx.save(); ctx.translate(900, 560); ctx.rotate(-0.04); ctx.scale(4.4, 4.4); ctx.font = '900 15px M'; const w = ctx.measureText('LIVES ALONE').width;
    pen(-62 + (w + 4) * up, -24 + 2 * 28, 0.6, 2.0); ctx.restore();
  });
};

// ---------- rule 2: do not tell the truth ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT TELL THE TRUTH');
S.b1 = (t, seg) => {
  const tl = wt(seg, 'leans'), tw = wt(seg, 'what'), lean = ease(prog(t, tl, 1.2));
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.55, 960, 380, () => room(t, { arms: ['board', 'desk', 'board'], lean, eyes: lerp(0.5, 1, lean) }));
  say(t, tw - 0.1, 960, 120, 'WHAT IS YOUR GREATEST WEAKNESS?', 960, 230, 46);
};
S.b2 = (t, seg) => {
  // quiet: the air conditioner stops, the clock stops
  const tc = wt(seg, 'conditioner'), tk = wt(seg, 'clock');
  if (t < tc - 0.4) { cam(t, seg.start, 3, 1.0, 1.04, 960, 520, () => room(t, { arms: 'desk', me: true })); return; }
  if (t < tk - 0.2) { focus(t, tc - 0.4, 3, 2.6, 2.8, ...AC, () => roomWall({ ac: 1 - prog(t, tc + 0.2, 0.8), floor: 2000 })); return; }
  const sec = 40 + (t < tk + 0.4 ? (t - tk) * 0 : 0) + (Math.sin(t * 40) * 0.25 * (t > tk + 0.2 ? 1 : 0));
  focus(t, tk - 0.2, 3, 3.0, 3.3, ...CLOCK, () => roomWall({ clock: [9, 13, sec], secRed: t > tk + 0.2, floor: 2000 }));
};
S.b3 = (t, seg) => {
  const tw = wt(seg, 'work'), tc = wt(seg, 'care');
  black();
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.05, 960, 520, () => {
    slideIn(t, seg.start, 0, -30, () => spaced('ALLOWED ANSWERS', 960, 280, '900 44px M', C.mid, 14), 0.4);
    lnP(560, 320, 1360, 320, 4, C.mid, prog(t, seg.start + 0.2, 0.5));
    okRow(t, tw - 0.3, 480, 470, '"I WORK TOO HARD."', 64);
    okRow(t, tc - 0.3, 480, 670, '"I CARE TOO MUCH."', 64);
  });
};
S.b4 = (t, seg) => {
  const tp = wt(seg, 'procrastination'), ts = wt(seg, 'public'), tn = wt(seg, 'nervous');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.1, 1.18, 960, 420, () => room(t, { arms: ['board', 'desk', 'board'], eyes: 1 }));
  listCard(420, 210, 1080, 600);
  noRow(t, tp - 0.25, tp + 0.35, 480, 330, 'clock', 'PROCRASTINATION', 52);
  noRow(t, ts - 0.25, ts + 0.35, 480, 510, 'stage', 'PUBLIC SPEAKING', 52);
  noRow(t, tn - 0.25, tn + 0.35, 480, 690, 'sweat', 'I GET NERVOUS', 52);
};
function folder(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.25)', 22);
  rr(-260, -200, 200, 50, 10, '#cfcfd4'); rr(-260, -170, 520, 360, 12, '#e4e4e8'); noGlow(); rrS(-260, -170, 520, 360, 12, '#000', 3);
  text('CANDIDATE: YOU', -220, -100, '900 36px M', '#111', 'left'); ln(-220, -80, 220, -80, 3, '#9a9aa0');
  for (let i = 0; i < 3; i++) rr(-220, -40 + i * 40, i === 2 ? 220 : 360, 14, 4, '#b9b9bf');
  ctx.restore();
}
S.b5 = (t, seg) => {
  // whatever you say becomes your weakness. Forever. It goes in your file, and the file follows you.
  const tf = wt(seg, 'forever'), tfi = wt(seg, 'file'), tfo = wt(seg, 'follows');
  black();
  if (t < tfo - 0.15) {
    cam(t, seg.start, tfo - seg.start, 1.0, 1.12, 960, 540, () => {
      folder(960, 560, 1.4);
      if (t >= tfi) stampMark(t, tfi, 1040, 680, [['WEAKNESS', 70], ['PERMANENT', 34]], -0.12, '#e4e4e8', 40);
    });
    if (t >= tf && t < tfi) pop(t, tf, 960, 150, () => tag('FOREVER', 960, 160, C.red, 60, 'center'), 0.3);
    return;
  }
  // you walk away down the street; the file floats after you
  const k = (t - tfo) / 3.2, x = lerp(700, 1300, k);
  cam(t, tfo, 3.5, 1.0, 1.05, 960, 540, () => {
    ln(-200, 860, W + 200, 860, 3, '#2a2a2e');
    for (let i = 0; i < 6; i++) { const lx = ((i * 380 - (t - tfo) * 120) % 2300 + 2300) % 2300 - 200; rr(lx, 300, 12, 560, 4, '#1c1c20'); circ(lx + 6, 300, 14, '#2a2a2e'); }
    me(x, 860, 1.25, { face: 'right', walk: t * 7 });
    folder(x - 380, 470 + Math.sin(t * 3) * 14, 0.42);
    ctx.save(); ctx.setLineDash([12, 12]); ln(x - 260, 480, x - 40, 470, 3, '#55555c'); ctx.restore();
  });
};
S.b6 = (t, seg) => {
  const ts = wt(seg, 'said');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.08, 760, 560, () => {
    roomWall({ floor: 900, clockAt: [1500, 200], acAt: [-600, 0] });
    sitSide(620, 900, 1.3, { dir: 1 });
    say(t, ts + 0.1, 760, 240, '"I CAN\'T SAY NO."', 680, 340, 56);
    suit(1420, 905, 1.0, { arms: 'write', wt: t, eyes: 1 }); desk(1120, 1720, DESK_Y, { n: 1 });
  });
};
S.b7 = (t, seg) => {
  // the office at night through the glass: he is still there. Nine years. He never went home.
  const tn = wt(seg, 'nine'), th = wt(seg, 'home');
  cam(t, seg.start, seg.end - seg.start + 1.4, 1.0, 1.2, 1000, 520, () => {
    ctx.fillStyle = '#040406'; ctx.fillRect(-200, -200, W + 400, H + 400);
    // the glass wall: frames and reflections
    for (let i = 0; i < 4; i++) { rrS(200 + i * 400, 120, 400, 760, 0, '#2a2a30', 6); ctx.save(); ctx.globalAlpha = 0.06; pth(`M${260 + i * 400},120 L${330 + i * 400},120 L${230 + i * 400},880 L${200 + i * 400},880 Z`, '#fff'); ctx.restore(); }
    // his desk + monitor glow
    const g = ctx.createRadialGradient(1080, 520, 20, 1080, 560, 520); g.addColorStop(0, 'rgba(220,235,255,0.22)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    rr(840, 640, 520, 16, 4, '#d6d6da'); rr(860, 656, 16, 220, 3, '#55555c'); rr(1320, 656, 16, 220, 3, '#55555c');
    glow('rgba(220,235,255,0.9)', 30); rr(1150, 450, 200, 130, 8, '#e8f0ff'); noGlow(); rr(1240, 580, 20, 60, 3, '#55555c');
    for (let i = 0; i < 4; i++) rr(1170, 474 + i * 24, typed('████████████', t, seg.start + i * 0.6, 8).length * 12, 10, 2, '#7a8aa0');
    sitSide(960, 880, 1.05, { dir: 1, eye: t >= th - 0.2 ? false : true });
    if (t >= th - 0.2) { ctx.save(); const hx = 960 - 4 * 1.05, hy = 880 - 420 * 1.05; redGlow(18); circ(hx - 10, hy - 4, 6, C.red); circ(hx + 12, hy - 4, 6, C.red); ctx.restore(); }   // he turns to you
    // the wall calendar
    if (t >= tn) pop(t, tn, 560, 330, () => { rr(440, 220, 240, 250, 12, '#e6e6e6'); rr(440, 220, 240, 64, 12, '#d61f1f'); text('YEAR', 560, 266, '900 36px M', '#fff'); text('9', 560, 430, '900 140px M', '#111'); }, 0.3);
  });
};

// ---------- rule 3: do not say you have no questions ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'DO NOT SAY YOU HAVE NO QUESTIONS');
S.c1 = (t, seg) => {
  const tp = wt(seg, 'pens'), td = wt(seg, 'do');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.1, 960, 420, () => room(t, { arms: t < tp ? 'write' : 'desk', me: true }));
  say(t, td - 0.1, 960, 130, 'DO YOU HAVE ANY QUESTIONS FOR US?', 960, 250, 46);
};
S.c2 = (t, seg) => {
  // never say no: the door stays locked until you ask something
  const tn = wt(seg, 'never'), ta = wt(seg, 'ask');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.08, 1300, 520, () => room(t, { arms: 'desk', door: { lock: prog(t, seg.start + 0.6, 0.3) }, me: true, meX: 900 }));
  if (t >= tn) { say(t, tn - 0.05, 1230, 800, '"NO."', 990, 730, 70); redX(1230, 800, 70, prog(t, tn + 0.3, 0.3)); }
  if (t >= ta) pop(t, ta, 1785, 720, () => { glow(); circ(1785, 760, 50, C.fig); noGlow(); text('?', 1785, 788, '900 76px M', '#000'); }, 0.3);
};
S.c3 = (t, seg) => {
  // "No, I think you covered everything." The clock on the wall goes back to nine.
  const tc = wt(seg, 'clock'), tn = wt(seg, 'nine');
  if (t < tc - 0.2) {
    cam(t, seg.start, 3, 1.0, 1.05, 960, 520, () => room(t, { arms: 'desk', me: true }));
    say(t, seg.start + 0.2, 1420, 790, '"NO, I THINK YOU\nCOVERED EVERYTHING."', 1040, 730, 46);
    return;
  }
  const k = ease(prog(t, tc + 0.1, tn - tc + 0.1)), m = lerp(58, 0, k) - (k < 1 ? 0 : 0), h = 9 + m / 60 * (k < 1 ? 1 : 0);
  focus(t, tc - 0.2, 4, 3.0, 3.3, ...CLOCK, () => roomWall({ clock: [9, m, (t * 60) % 60 * (1 - k)], secRed: true, floor: 2000 }));
  if (k >= 1) pop(t, tn, 960, 860, () => tag('9:00 AM', 960, 880, C.red, 60, 'center'), 0.3);
};
S.c4 = (t, seg) => {
  // the middle one tilts his head: then let's start again
  const tt = wt(seg, 'tilts'), tl = wt(seg, 'then'), tilt = -0.28 * ease(prog(t, tt, 1.2));
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.4, 1.75, 960, 380, () => room(t, { arms: ['board', 'desk', 'board'], tilt, eyes: 1, clock: [9, 0, 0] }));
  say(t, tl - 0.1, 960, 110, "THEN LET'S START AGAIN.", 1000, 200, 44);
  if (t >= wt(seg, 'tell')) say(t, wt(seg, 'tell') - 0.1, 960, 880, 'TELL ME ABOUT YOURSELF.', 960, 760, 44, { red: true });
};
S.c5 = (t, seg) => {
  // he said no three times. He is still in there. Monday, 9:00. His beard reaches the floor.
  const ts = wt(seg, 'still'), tm = wt(seg, 'monday'), g = ease(prog(t, ts - 0.2, 3.5));
  cam(t, seg.start, seg.end - seg.start + 1.6, 1.0, 1.18, 760, 560, () => {
    roomWall({ floor: 900, clock: [9, 0, 0], clockAt: [1500, 200], acAt: [-600, 0], secRed: true });
    sitSide(620, 900, 1.3, { dir: 1 });
    // cobwebs between him and the chair; the day counter keeps going, the clock does not
    if (g > 0) { ctx.save(); ctx.globalAlpha *= g * 0.8; const cx0 = 620 - 50 * 1.3, cy0 = 900 - 380 * 1.3;
      for (let k = 0; k < 6; k++) { const a = k / 5 * Math.PI / 2; ln(cx0, cy0, cx0 + Math.cos(a) * 150, cy0 + Math.sin(a) * 150, 2, '#d6d6da'); }
      for (let r = 1; r <= 4; r++) { ctx.beginPath(); for (let k = 0; k < 6; k++) { const a = k / 5 * Math.PI / 2, rr2 = r * 34 + (k % 2) * 4; k ? ctx.lineTo(cx0 + Math.cos(a) * rr2, cy0 + Math.sin(a) * rr2) : ctx.moveTo(cx0 + Math.cos(a) * rr2, cy0 + Math.sin(a) * rr2); } ctx.strokeStyle = '#d6d6da'; ctx.lineWidth = 2; ctx.stroke(); }
      const fx = 620 + 140 * 1.3, fy = 900; for (let k = 0; k < 5; k++) { const a = Math.PI + k / 4 * Math.PI / 2; ln(fx, fy, fx + Math.cos(a) * 90, fy + Math.sin(a) * 90, 2, '#d6d6da'); }
      ctx.restore();
      const days = Math.floor(lerp(1, 4019, ease(g))); pop(t, ts - 0.2, 1320, 330, () => { listCard(1110, 250, 420, 150); text('DAYS IN THIS ROOM', 1320, 300, '600 24px Plex', '#8a8a92'); text(days.toLocaleString('en-US'), 1320, 370, '900 60px M', C.fig); }, 0.3); }
    // three NOs
    for (let k = 0; k < 3; k++) pop(t, seg.start + 0.4 + k * 0.3, 380 + k * 0, 300 + k * 110, () => { tag('NO.', 300, 320 + k * 110, C.fig, 54, 'center'); }, 0.25);
    // the desk calendar: MONDAY
    if (t >= tm) pop(t, tm, 1320, 640, () => { rr(1180, 560, 280, 200, 12, '#e6e6e6'); rr(1180, 560, 280, 60, 12, '#d61f1f'); text('MONDAY', 1320, 604, '900 34px M', '#fff'); text('9:00', 1320, 720, '900 80px M', '#111'); }, 0.3);
    if (t >= tm) rr(1120, 760, 400, 16, 4, '#d6d6da');
  });
};
S.c6 = (t, seg) => {
  const ts = wt(seg, 'salary'), tl = wt(seg, 'last');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.1, 1.18, 960, 420, () => room(t, { arms: 'desk', eyes: 1 }));
  listCard(380, 280, 1160, 440);
  noRow(t, ts - 0.4, ts + 0.3, 440, 400, 'money', 'THE SALARY', 52);
  noRow(t, tl - 0.4, tl + 0.4, 440, 590, 'ask', 'THE LAST PERSON IN THIS ROLE', 46);
};
S.c7 = (t, seg) => {
  // the one question: when will I hear back? The lock opens.
  const tw = wt(seg, 'when');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 1300, 520, () => room(t, { arms: 'desk', door: { lock: 1, open: prog(t, seg.end - 0.6, 0.4) }, me: true, meX: 900 }));
  say(t, tw - 0.1, 1330, 800, '"WHEN WILL I\nHEAR BACK?"', 990, 730, 50);
  if (t >= seg.end - 0.6) { ctx.save(); ctx.translate(1330, 640); check(0, 0, 40, prog(t, seg.end - 0.6, 0.3)); ctx.restore(); }
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
S.d1 = (t, seg) => {
  const ts = wt(seg, 'stand'), tw = wt(seg, "we'll");
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 420, () => room(t, { arms: 'board', stand: prog(t, ts - 0.1, 0.8) }));
  say(t, tw - 0.1, 960, 110, "WE'LL GET BACK TO YOU.", 960, 200, 50);
};
S.d2 = (t, seg) => {
  // 3 AM. You wake up. Three of them at the foot of your bed.
  const tw = wt(seg, 'wake'), ti = wt(seg, 'interviewers'), tf = wt(seg, 'foot');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.1, 1100, 560, () => {
    const on = t >= ti - 0.1;
    night(t, { bed: t >= tw ? 'woke' : 'sleep', trio: on, eyes: prog(t, ti + 0.3, 0.3), arms: 'board' });
    if (on && t < ti + 0.25) { ctx.save(); ctx.globalAlpha = 0.25 * (1 - prog(t, ti - 0.1, 0.35)); ctx.fillStyle = '#fff'; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore(); }
  });
  if (t >= tf) pop(t, tf, 1530, 160, () => tag('3:00 AM', 1530, 170, C.red, 52, 'center'), 0.3);
};
S.d3 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 1.0, 1.3, 1.4, 1820, 470, () => night(t, { arms: ['write', 'board', 'write'] }));
  say(t, seg.start + 0.1, 1150, 170, 'WE HAVE A FEW\nMORE QUESTIONS.', 1480, 300, 34);
};
S.d4 = (t, seg) => {
  black();
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 520, () => {
    pop(t, seg.start, 960, 470, () => { ctx.save(); redGlow(24); spaced('DOES NOT WORK', 960, 500, '900 110px M', C.red, 8); ctx.restore(); }, 0.35);
    lnP(420, 560, 1500, 560, 6, C.red, prog(t, seg.start + 0.3, 0.5));
  });
};
S.d5 = (t, seg) => {
  // pretending to sleep: LACKS ENTHUSIASM
  const tw = wt(seg, 'write'), tl = wt(seg, 'lacks');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.08, 1000, 560, () => night(t, { bed: 'sleep', arms: t >= tw - 0.3 ? ['board', 'write', 'board'] : 'board' }));
  noHead(t, seg, 'sleep', 'PRETEND TO SLEEP', seg.start + 1.6);
  if (t >= tl - 0.1) pop(t, tl - 0.1, 1300, 300, () => { ctx.save(); ctx.translate(1300, 300); ctx.rotate(-0.05); glow(); rr(-260, -50, 520, 100, 10, '#fbfbfb'); noGlow(); text('LACKS ENTHUSIASM', 0, 16, '900 44px M', '#d61f1f'); ctx.restore(); }, 0.3);
};
S.d6 = (t, seg) => {
  // another offer: they ask for the name, and they go there too
  const ta = wt(seg, 'ask'), tv = wt(seg, 'visit');
  if (t < tv - 0.3) {
    cam(t, seg.start, tv - seg.start, 1.0, 1.08, 1000, 560, () => night(t, {}));
    noHead(t, seg, 'offer', 'ANOTHER OFFER', ta + 0.3);
    say(t, ta - 0.1, 1230, 190, "WHAT'S THE\nCOMPANY'S NAME?", 1500, 320, 40);
    return;
  }
  cam(t, tv - 0.3, 3.5, 1.0, 1.1, 960, 560, () => {
    black();
    // the other company's tower at night; one floor goes dark window by window
    rr(620, 80, 680, 900, 4, '#0d0d10'); rrS(620, 80, 680, 900, 4, '#3a3a40', 4);
    for (let r = 0; r < 12; r++) for (let c = 0; c < 6; c++) { const lit = hash(r * 7 + c) > 0.45; rr(660 + c * 104, 120 + r * 66, 76, 40, 3, lit ? '#8a8a92' : '#1a1a1e'); }
    rr(840, 860, 240, 120, 4, '#2a2a30'); ln(-200, 980, W + 200, 980, 3, '#2a2a2e');
    trio(t, { xs: [880, 960, 1040], ss: [0.3, 0.3, 0.3], y: 980, arms: 'board' });
  });
  noHead(t, seg, 'offer', 'ANOTHER OFFER', ta + 0.3);
};
S.d7 = (t, seg) => {
  // blocking their email: the next one comes from inside your house
  const tn = wt(seg, 'next'), ti = wt(seg, 'inside');
  black();
  cam(t, seg.start, seg.end - seg.start + 1.4, 1.0, 1.1, 960, 560, () => {
    if (t < tn - 0.1) {
      mailCard(560, 260, 800, 520, { from: 'INTERVIEWS', subj: 'A few more questions', body: ['We noticed you have not replied.', 'We will try again.'] });
      if (t >= seg.start + 1.0) stampMark(t, seg.start + 1.0, 1140, 640, [['BLOCKED', 64]], -0.1, '#f4f4f6', 20);
    } else {
      mailCard(560, 260, 800, 520, { dot: true, from: 'YOUR LIVING ROOM', fromRed: true, subj: 'We are in the hallway.', body: ['Please come out.', 'We have a few more questions.'] });
    }
  });
  noHead(t, seg, 'mail', 'BLOCK THEIR EMAIL', seg.start + 1.2);
};
S.d8 = (t, seg) => {
  // the only thing that works: interview them. The clipboard is yours now.
  const ti = wt(seg, 'interview');
  black();
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 520, () => {
    if (t >= ti - 0.1) {
      pop(t, ti - 0.1, 960, 270, () => { glow(); spaced('INTERVIEW THEM.', 960, 300, '900 104px M', C.fig, 4); noGlow(); }, 0.35);
      slideIn(t, ti + 0.2, 0, 60, () => { me(960, 960, 1.35, { face: 'front' }); clipboard(960, 640, 1.1, 0.05); }, 0.4);
    } else pop(t, seg.start, 960, 520, () => { ctx.save(); glow(); spaced('ONLY ONE THING WORKS', 960, 540, '900 70px M', C.fig, 6); ctx.restore(); }, 0.35);
  });
};
S.d9 = (t, seg) => {
  // sit up, fold your hands, look the middle one in the eye
  const ts = wt(seg, 'so'), te = wt(seg, 'eye');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, t >= te ? 1.3 : 1.1, t >= te ? 1450 : 1000, 520, () => night(t, { bed: 'woke', arms: 'board' }));
  if (t >= te) brackets(1530, 900 - 0.8 * 576, 150, 170, prog(t, te, 0.3), C.fig);
  say(t, ts - 0.1, 760, 200, '"SO. WHAT IS YOUR\nGREATEST WEAKNESS?"', 600, 470, 44);
};
S.d10 = (t, seg) => {
  // the rules of that room apply to them too: they cannot lie
  const tl = wt(seg, 'lie');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.15, 1.25, 1530, 520, () => night(t, { arms: 'down' }));
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  slideIn(t, seg.start + 0.2, 0, -40, () => { rr(470, 70, 600, 150, 12, '#ececec'); rr(490, 103, 84, 84, 10, '#111'); text('2', 532, 169, '900 62px M', '#fff'); pageIcon('truth', 630, 145, '#111');
    text('DO NOT TELL', 700, 136, '900 40px M', '#111', 'left'); text('THE TRUTH', 700, 178, '900 40px M', '#111', 'left'); }, 0.4);
  if (t >= tl - 0.1) pop(t, tl - 0.1, 770, 300, () => { ctx.save(); redGlow(20); text('THEY CANNOT LIE', 770, 320, '900 58px M', C.red); ctx.restore(); }, 0.3);
  ctx.restore();
};
const SHRINK = (t, t0) => lerp(0.8, 0.5, ease(prog(t, t0, 0.9)));
S.d11 = (t, seg) => {
  const tb = wt(seg, 'being'), ts = wt(seg, 'smaller');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.15, 1.22, 1460, 540, () => night(t, { arms: ['down', 'board', 'board'], ss: [SHRINK(t, ts - 0.2), 0.8, 0.8], shake: [t > tb ? 3 : 0, 0, 0] }));
  say(t, tb - 0.15, 1080, 200, '"BEING ASKED\nQUESTIONS."', 1300, 330, 44);
};
S.d12 = (t, seg) => {
  const tt = wt(seg, 'tell'), tsh = wt(seg, 'shake'), ts = wt(seg, 'smaller');
  const d11 = window.TL.segments.find(s => s.id === 'd11'), s0 = SHRINK(t, wt(d11, 'smaller') - 0.2);
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.15, 1.22, 1460, 540, () => night(t, { arms: ['down', 'down', 'board'], ss: [s0, SHRINK(t, ts - 0.2), 0.8], shake: [0, t > tsh ? 6 : 0, 0] }));
  say(t, tt - 0.1, 700, 200, '"TELL ME ABOUT\nYOURSELF."', 560, 450, 46);
};
S.d13 = (t, seg) => {
  const th = wt(seg, 'why');
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.12, 1.22, 1700, 560, () => night(t, { arms: ['down', 'down', 'down'], ss: [0.5, 0.5, 0.8], shake: [5, 5, t > th + 0.6 ? 8 : 0], eyes: 0.6 + 0.4 * Math.abs(Math.sin(t * 9)) }));
  say(t, th - 0.1, 700, 200, '"WHY SHOULD\nI HIRE YOU?"', 560, 450, 56);
};
S.d14 = (t, seg) => {
  // they fold up like paper and slide out under your door
  const tf = wt(seg, 'fold'), tsl = wt(seg, 'slide');
  const f = prog(t, tf - 0.1, 1.1), sl = ease(prog(t, tsl - 0.2, 1.4));
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.15, 1.08, 1500, 600, () => {
    night(t, { trio: false, gapGlow: sl > 0 ? 0.6 : 0 });
    const xs = TRIO, ss = [0.5, 0.5, 0.8];
    if (f < 0.97) {
      const k = clamp((f - 0.2) / 0.6);
      ctx.save(); ctx.globalAlpha *= 1 - k; trio(t, { xs, ss, arms: 'down', fold: [f * 0.6, f * 0.6, f * 0.6], shake: [2, 2, 2] }); ctx.restore();
      // each one becomes a sheet of paper, folding in half and in half again down to the floor
      for (let i = 0; i < 3; i++) { const h = lerp(560 * ss[i], 10, ease(f)), w = lerp(200 * ss[i], 170 * ss[i], f), x = xs[i];
        ctx.save(); ctx.globalAlpha *= k; glow(); rr(x - w / 2, 900 - h, w, h, 3, '#fbfbfb'); noGlow();
        if (h > 30) { ln(x - w / 2, 900 - h / 2, x + w / 2, 900 - h / 2, 2, '#9a9aa0'); ln(x - w / 2, 900 - h * 0.75, x + w / 2, 900 - h * 0.75, 1.5, '#c4c4c8'); for (let j = 0; j < 5; j++) ln(x - w / 2 + 16, 900 - h + 20 + j * h / 7, x + w / 2 - 16 - (j % 2) * 30, 900 - h + 20 + j * h / 7, 3, '#d6d6da'); }
        ctx.restore(); }
    }
    else for (let i = 0; i < 3; i++) {   // three sheets on the floor, sliding to the gap under the door
      const x = lerp(xs[i], 1700 + i * 40, sl), w = 170 * ss[i];
      ctx.save(); ctx.globalAlpha *= 1 - clamp((sl - 0.6) / 0.4); glow(); rr(x - w / 2, 890, w, 10, 2, C.fig); noGlow(); ctx.restore();
    }
    // the door is drawn again over the sheets so they disappear under it
    if (f >= 0.97) rr(1640, 380, 200, 510, 4, '#0e0e10');
    if (f >= 0.97) rrS(1640, 380, 200, 510, 4, '#3a3a40', 4); circ(1660, 650, 8, '#55555c');
  });
};

// ---------- one week later ----------
S.f1 = (t, seg) => {
  const te = wt(seg, 'email');
  black();
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.05, 960, 520, () => {
    pop(t, seg.start, 960, 250, () => { ctx.save(); glow(); spaced('ONE WEEK LATER', 960, 270, '900 64px M', C.fig, 10); ctx.restore(); }, 0.35);
    if (t >= te - 0.1) pop(t, te - 0.1, 960, 560, () => { glow(); rr(560, 470, 800, 180, 24, '#f4f4f6'); noGlow(); icon7('mail', 680, 560, 0.6, '#111'); text('1 NEW EMAIL', 780, 580, '900 54px M', '#111', 'left'); ctx.save(); redGlow(14); circ(1320, 500, 18, C.red); ctx.restore(); }, 0.35);
  });
};
S.f2 = (t, seg) => {
  const tw = wt(seg, 'we'), tp = wt(seg, 'would');
  black();
  cam(t, seg.start, seg.end - seg.start + 0.7, 1.0, 1.06, 960, 520, () => {
    const b1 = typed('We regret to inform you that our', t, tw, 30), b2 = typed('interviewers have resigned.', t, tw + 1.1, 30), b3 = typed('Would you like the position?', t, tp - 0.1, 30);
    mailCard(460, 200, 1000, 560, { from: 'HR', subj: 'Your application', body: [b1, b2, '', b3] });
  });
};
S.f3 = (t, seg) => {
  // job title: interviewer. Location: the chair.
  const tj = wt(seg, 'job'), tl = wt(seg, 'location'), tc = wt(seg, 'chair');
  cam(t, seg.start, seg.end - seg.start + 1.2, 1.0, 1.25, 960, 480, () => {
    room(t, { who: [false, false, false], chairs: true });
    if (t >= tc) { ctx.save(); redGlow(40); ctx.globalAlpha = prog(t, tc, 0.4); rrS(960 - 110 * 0.82, 905 - 560 * 0.82, 220 * 0.82, 280 * 0.82, 30, C.red, 6); ctx.restore(); }
  });
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  if (t >= tj - 0.1) slideIn(t, tj - 0.1, -50, 0, () => { listCard(70, 70, 760, 230); text('JOB TITLE', 110, 140, '600 26px Plex', '#8a8a92', 'left'); text('INTERVIEWER', 110, 210, '900 62px M', C.fig, 'left');
    if (t >= tl - 0.1) { text('LOCATION', 110, 256, '600 26px Plex', '#8a8a92', 'left'); text('THE CHAIR', 280, 262, '900 40px M', C.red, 'left'); } }, 0.35);
  ctx.restore();
};
S.f4 = (t, seg) => {
  const ts = wt(seg, 'four'), hit = t - ts, k = easeOut((t - seg.start + 0.15) / 0.6);
  cam(t, seg.start, seg.end - seg.start + 1.2, 0.98, 1.06, W / 2, 520, () => {
    ctx.save(); ctx.translate(0, 300 * (1 - k)); if (hit > 0 && hit < 0.3) shake(7 * (1 - hit / 0.3), t);
    ctx.globalAlpha *= clamp(k * 1.6); fileCover(t); stampMark(t, ts, P.x + 300, P.y + 610, [[NAME, 38], [NUM, 150]], -0.1); ctx.restore();
  });
};
S.f5 = (t, seg) => {
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
// 1: the panel of three, big, the middle one's eyes red; the title over them
window.drawThumbA = () => {
  thBg();
  const g = ctx.createRadialGradient(960, 600, 60, 960, 700, 900); g.addColorStop(0, 'rgba(255,255,255,0.10)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(960, 0); ctx.scale(1.55, 1.55); ctx.translate(-960, -30);
  for (let i = 0; i < 3; i++) suit(560 + i * 400, 905, 1, { arms: i === 1 ? 'desk' : 'board', eyes: i === 1 ? 1 : 0 });
  desk(160, 1760, 620, { n: 3 });
  ctx.restore();
  thTitle("DON'T TELL THE ", 'TRUTH', 190, 140);
};
// 2: just the middle one, huge, leaning in; red eyes; title on the left
window.drawThumbB = () => {
  thBg();
  ctx.save(); ctx.translate(1340, 0); ctx.scale(2.6, 2.6); ctx.translate(-960, -205);
  suit(960, 905, 1, { arms: 'desk', eyes: 1, lean: 0.8 });
  ctx.restore();
  ctx.save(); ctx.font = '900 170px M'; text("DON'T", 90, 380, '900 170px M', '#fff', 'left'); text('TELL THE', 90, 560, '900 170px M', '#fff', 'left'); redGlow(28); text('TRUTH', 90, 740, '900 170px M', C.red, 'left'); ctx.restore();
};
// 3: the clipboard: GREATEST WEAKNESS with the answer underlined in red, a faceless interviewer behind
window.drawThumbC = () => {
  thBg();
  ctx.save(); ctx.translate(1380, 0); ctx.scale(1.9, 1.9); ctx.translate(-960, -108); ctx.globalAlpha = 0.9;
  suit(960, 905, 1, { arms: 'desk', eyes: 1 }); ctx.restore();
  ctx.save(); ctx.translate(620, 640); ctx.rotate(-0.06); ctx.scale(3.2, 3.2);
  rr(-80, -88, 160, 180, 8, SUIT.board); rrS(-80, -88, 160, 180, 8, SUIT.line, 3); rr(-70, -70, 140, 154, 2, SUIT.paper);
  rr(-26, -96, 52, 22, 6, '#2a2a2e'); text('GREATEST', -60, -38, '900 17px M', '#222', 'left'); text('WEAKNESS:', -60, -16, '900 17px M', '#222', 'left');
  text('"I GET', -60, 22, '900 20px M', '#d61f1f', 'left'); text('NERVOUS"', -60, 46, '900 20px M', '#d61f1f', 'left');
  ln(-62, 54, 44, 52, 3.5, '#d61f1f'); ctx.restore();
  thTitle("DON'T TELL THE ", 'TRUTH', 170, 130);
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

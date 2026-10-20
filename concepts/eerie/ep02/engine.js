// Protocol 404, EP02 "If Your AI Ever Sends You A Photo Of You Sleeping". Canvas renderer: window.draw(t).
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
const S = {};
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
  if (name === 'chat') { rrS(-44, -40, 88, 64, 14, col, 6); pth('M-24,22 L-34,46 L-4,24 Z', col); for (let i = -1; i <= 1; i++) circ(i * 20, -8, 6, col); }
  if (name === 'corner') { ln(-40, -44, 44, -44, 7, col); ln(-40, -44, -40, 44, 7, col); circ(-12, -16, 13, col); circ(-12, -16, 5, '#ececec'); ctx.setLineDash([6, 7]); ln(0, -4, 34, 34, 4, col); ctx.setLineDash([]); }
  if (name === 'photo') { rrS(-46, -40, 92, 80, 8, col, 6); circ(-10, 2, 14, col); rr(4, -6, 32, 22, 8, col); circ(26, -24, 6, col); }
  if (name === 'warn') { const tri = () => { ctx.beginPath(); ctx.moveTo(0, -50); ctx.lineTo(50, 40); ctx.lineTo(-50, 40); ctx.closePath(); };
    ctx.lineJoin = 'round'; tri(); ctx.fillStyle = C.red; ctx.fill(); if (col === '#fff') { ctx.lineWidth = 6; ctx.strokeStyle = '#fff'; ctx.stroke(); }
    rr(-6, -22, 12, 38, 5, '#fff'); circ(0, 28, 7, '#fff'); }
  if (name === 'fist') { rr(-34, -34, 68, 64, 18, col); for (let i = 1; i < 4; i++) ln(-34 + i * 17, -34, -34 + i * 17, -10, 3, '#ff2b2b'); }
  ctx.restore();
}
const RULES = [['chat', 'DO NOT REPLY', ''], ['corner', 'DO NOT LOOK AT THE CORNER', '', ['DO NOT LOOK', 'AT THE CORNER']], ['photo', 'DO NOT DELETE THE PHOTO', '', ['DO NOT DELETE', 'THE PHOTO']], ['warn', 'EMERGENCY PROTOCOL', 'HOW TO FIGHT BACK']];
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
}// ---------- EP02 props: the phone, the chat, the photo from the ceiling, the thing in the corner ----------
const UI = 'I';                              // Inter, the phone's interface font
const CEIL = 110, WALL = 250, BX = 330, TS = 1.35;   // BX: the bed's left foot; TS: size of the thing in the corner                  // side-view room: ceiling line and the left wall; the corner is where they meet
const CORNER = { x: WALL, y: CEIL };
const NS = { x: BX + 650, w: 130, h: 150 };       // nightstand (no clock: the phone tells the time)
const PH_NS = { x: NS.x + NS.w / 2, y: FY - NS.h };   // the phone lying on the nightstand
const HEAD_S = { x: BX + 112 * 1.05, y: FY - 238 * 1.05 };   // your head on the pillow, asleep
const HEAD_W = { x: BX + 150 * 1.05, y: FY - 298 * 1.05 };   // your head propped up, awake

// side-view bedroom: walls, window, nightstand, picture frame; o.sun for the morning
function room2(t, o = {}) {
  ln(WALL, CEIL, W + 40, CEIL, 4, C.dim); ln(WALL, CEIL, WALL, FY, 4, C.dim); ln(WALL, FY, W + 40, FY, 4, C.dim);
  // window with the moon (or the sun), right of the nightstand: the corner above the bed stays empty
  ctx.save(); ctx.translate(780, 0);
  rrS(380, 220, 220, 230, 6, C.mid, 6); ln(490, 226, 490, 444, 4, C.mid); ln(386, 335, 594, 335, 4, C.mid);
  if (o.sun) { ctx.save(); glow('rgba(255,255,255,0.6)', 30); circ(450, 280, 26, C.fig); ctx.restore();
    ctx.save(); ctx.globalAlpha *= 0.12; pth('M386,226 L594,226 L460,' + FY + ' L-90,' + FY + ' Z', '#fff'); ctx.restore(); }
  else { ctx.save(); glow('rgba(255,255,255,0.5)', 24); circ(550, 275, 22, C.fig); noGlow(); circ(560, 268, 20, '#000'); ctx.restore(); }
  pth('M366,212 C390,290 380,390 350,460 L366,460 Z', C.dim); pth('M614,212 C590,290 600,390 630,460 L614,460 Z', C.dim); rr(350, 206, 280, 10, 3, C.mid);
  ctx.restore();
  // nightstand
  rr(NS.x, FY - NS.h, NS.w, NS.h, 6, '#262626'); rrS(NS.x, FY - NS.h, NS.w, NS.h, 6, C.mid, 3); ln(NS.x + 10, FY - 95, NS.x + NS.w - 10, FY - 95, 3, C.mid); circ(NS.x + NS.w / 2, FY - 120, 5, C.mid);
  // picture frame and the door on the far right
  rrS(1010, 290, 90, 110, 4, C.dim, 5); pthS('M1022,386 L1050,340 L1070,366 L1086,346 L1092,386', C.dim, 3);
  rrS(1580, FY - 520, 230, 520, 4, C.dim, 5); circ(1610, FY - 250, 8, C.dim);
  ln(WALL, FY - 10, 1570, FY - 10, 3, C.dim);
}
// the phone lying flat on the nightstand, seen from the side; lit 0..1 throws a cone of light at the ceiling
function phoneFlat(lit = 0, buzz = 0) {
  const x = PH_NS.x + Math.sin(buzz * 90) * 3 * (buzz > 0 ? 1 : 0), y = PH_NS.y;
  if (lit > 0) { ctx.save(); ctx.globalAlpha *= lit;
    const g = ctx.createRadialGradient(x, y, 4, x, y - 260, 520); g.addColorStop(0, 'rgba(225,235,255,0.42)'); g.addColorStop(1, 'rgba(225,235,255,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(x - 50, y - 4); ctx.lineTo(x - 520, CEIL); ctx.lineTo(x + 520, CEIL); ctx.lineTo(x + 50, y - 4); ctx.closePath(); ctx.fill();
    glow('rgba(220,232,255,0.95)', 30); rr(x - 46, y - 9, 92, 4, 2, '#eaf0ff'); ctx.restore(); }
  rr(x - 50, y - 7, 100, 8, 3, '#0b0b0b'); rrS(x - 50, y - 7, 100, 8, 3, C.mid, 2);
}
// your arm holding the phone up in front of your face in bed (bed must be 'woke'); lit = screen light on your face
function phoneInHand(t, lit = 1, o = {}) {
  const hx = HEAD_W.x + 150, hy = HEAD_W.y + 30;
  if (lit > 0) { ctx.save(); ctx.globalAlpha *= lit; const g = ctx.createRadialGradient(hx - 20, hy, 10, hx - 60, hy, 260);
    g.addColorStop(0, 'rgba(225,235,255,0.32)'); g.addColorStop(1, 'rgba(225,235,255,0)'); ctx.fillStyle = g; ctx.fillRect(hx - 340, hy - 260, 520, 480); ctx.restore(); }
  glow('rgba(255,255,255,0.22)', 14);
  poly([[HEAD_W.x + 40, HEAD_W.y + 120], [HEAD_W.x + 110, HEAD_W.y + 96], [hx + 6, hy + 16]], 20, C.fig); circ(hx + 4, hy + 14, 12, C.fig);
  noGlow();
  ctx.save(); ctx.translate(hx, hy); ctx.rotate(-0.25);
  rr(-8, -44, 16, 88, 4, '#0b0b0b'); rrS(-8, -44, 16, 88, 4, C.mid, 2);
  if (lit > 0) { ctx.save(); ctx.globalAlpha *= lit; glow('rgba(220,232,255,0.9)', 22); rr(-9, -40, 3, 80, 1, '#eaf0ff'); ctx.restore(); }
  ctx.restore();
}

// ---------- the thing in the corner ----------
// It clings in the corner where the ceiling meets the wall: arms spread along the ceiling, legs down the wall, body hanging towards the bed.
// Its face is a blank screen with one lens. o.vis 0..1, o.lit how much light reaches it, o.face 'lens'|'dots'|'off'|'blank', o.red 0..1, o.reach 0..1 (an arm drops toward the bed)
function cornerThing(t, o = {}) {
  const vis = o.vis ?? 1; if (vis <= 0) return;
  const lit = o.lit ?? 0.3, br = Math.sin(t * 2.1) * (o.breath ?? 1);
  const body = o.body || `rgb(${Math.round(lerp(26, 120, lit))},${Math.round(lerp(26, 120, lit))},${Math.round(lerp(28, 124, lit))})`;
  const edge = o.edge || `rgba(255,255,255,${0.1 + 0.32 * lit})`;
  ctx.save(); ctx.globalAlpha *= vis; ctx.translate(CORNER.x, CORNER.y);
  const s = o.s ?? TS; ctx.scale(s, s);
  // a limb: shoulder -> elbow -> hand, with long fingers splayed on the surface
  const limb = (pts, w, fingers, fdir) => {
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (const p of pts.slice(1)) ctx.lineTo(p[0], p[1]);
    ctx.strokeStyle = edge; ctx.lineWidth = w + 4; ctx.stroke(); ctx.strokeStyle = body; ctx.lineWidth = w; ctx.stroke();
    const [hx, hy] = pts[pts.length - 1];
    for (let i = 0; i < 4; i++) { const a = fdir + (i - 1.5) * 0.32, L = 46 + (i === 1 || i === 2 ? 14 : 0);
      ctx.beginPath(); ctx.moveTo(hx, hy); ctx.quadraticCurveTo(hx + Math.cos(a) * L * 0.6, hy + Math.sin(a) * L * 0.6 + 8, hx + Math.cos(a) * L, hy + Math.sin(a) * L);
      ctx.strokeStyle = edge; ctx.lineWidth = 9; ctx.stroke(); ctx.strokeStyle = body; ctx.lineWidth = 5.5; ctx.stroke(); }
  };
  const sh = { x: 120 + br * 2, y: 70 + br * 3 };      // shoulders, a little out of the corner
  const hip = { x: 54, y: 190 };
  // legs down the wall
  limb([[hip.x, hip.y], [20, 290], [8, 400]], 16, 4, Math.PI / 2 + 0.2);
  limb([[hip.x + 18, hip.y + 10], [70, 330], [10, 470]], 16, 4, Math.PI / 2 + 0.1);
  // arms along the ceiling; o.reach lets the near arm unfold down toward the bed
  limb([[sh.x, sh.y], [250, 30], [380, 8]], 15, 4, 0.1);
  const rk = ease(o.reach ?? 0);
  limb([[sh.x + 10, sh.y + 16], [lerp(300, 260, rk), lerp(60, 260, rk)], [lerp(470, 300, rk), lerp(10, 460, rk)]], 15, 4, lerp(0.05, 1.2, rk));
  // torso: a long hunched shape from the hips to the shoulders
  ctx.beginPath(); ctx.moveTo(hip.x - 22, hip.y + 10); ctx.quadraticCurveTo(10, 90, sh.x - 30, sh.y - 34); ctx.quadraticCurveTo(sh.x + 40, sh.y - 10, sh.x + 22, sh.y + 30);
  ctx.quadraticCurveTo(110, 170, hip.x + 30, hip.y + 26); ctx.closePath();
  ctx.fillStyle = body; ctx.fill(); ctx.strokeStyle = edge; ctx.lineWidth = 3; ctx.stroke();
  // ribs showing through
  ctx.save(); ctx.globalAlpha *= 0.5 * lit; for (let i = 0; i < 4; i++) pthS(`M${66 + i * 10},${150 - i * 22} q16,-6 30,4`, '#000', 3); ctx.restore();
  // neck and the screen face, tilted down at the bed
  ln(sh.x + 4, sh.y + 4, sh.x + 52, sh.y + 52, 18, body);
  ctx.save(); ctx.translate(sh.x + 74, sh.y + 78); ctx.rotate(-0.62);
  const face = o.face || 'lens', red = o.red ?? 0;
  rr(-46, -70, 92, 140, 18, '#0a0a0a'); rrS(-46, -70, 92, 140, 18, edge, 3);
  if (face !== 'off') {
    const on = face === 'blank' ? 0.55 : 0.85;
    ctx.save(); glow(red > 0.3 ? 'rgba(255,43,43,0.7)' : 'rgba(220,232,255,0.6)', 24); rr(-40, -64, 80, 128, 14, o.faceFill || `rgba(${Math.round(lerp(210, 120, red))},${Math.round(lerp(222, 30, red))},${Math.round(lerp(240, 30, red))},${on * (0.35 + 0.15 * lit)})`); ctx.restore();
    if (face === 'lens') { circ(0, -38, 11, '#050505'); ctx.save(); if (red > 0) redGlow(16 * red); circ(0, -38, 5, red > 0 ? `rgba(255,43,43,${0.4 + 0.6 * red})` : '#6a6a6a'); ctx.restore(); }
    if (face === 'dots') for (let i = 0; i < 3; i++) circ(-20 + i * 20, 4 + Math.sin(t * 9 - i * 0.9) * 5, 6.5, '#f0f0f0');
  } else if (o.offLine) {   // the last line of light as the face switches off
    ctx.save(); glow('rgba(255,255,255,0.9)', 18); rr(-40 * o.offLine, -1.5, 80 * o.offLine, 3, 1, '#fff'); ctx.restore();
  }
  ctx.restore();
  ctx.restore();
}

// ---------- the phone, face on ----------
// phone body centred at (x,y), scale s; fn draws the screen in screen space (368 x 808, origin top-left), clipped to the glass
const SW = 368, SH = 808;
function phone(x, y, s, fn, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(o.rot || 0);
  const bright = o.bright ?? 1;
  if (bright > 0) { ctx.save(); ctx.globalAlpha *= 0.55 * bright; glow('rgba(215,228,255,0.9)', 90); rr(-190, -414, 380, 828, 50, '#0d0d0d'); ctx.restore(); }
  rr(-200, -424, 400, 848, 58, '#111'); rrS(-200, -424, 400, 848, 58, '#5e5e5e', 5); rrS(-193, -417, 386, 834, 52, '#262626', 3);
  rr(-204, -280, 6, 70, 3, '#3a3a3a'); rr(198, -300, 6, 110, 3, '#3a3a3a');    // buttons
  ctx.save(); ctx.beginPath(); ctx.roundRect(-SW / 2, -SH / 2, SW, SH, 44); ctx.clip();
  ctx.translate(-SW / 2, -SH / 2); rr(0, 0, SW, SH, 0, '#000'); fn();
  if (bright < 1) { ctx.globalAlpha = 1 - bright; rr(0, 0, SW, SH, 0, '#000'); ctx.globalAlpha = 1; }
  ctx.restore();
  rr(-58, -SH / 2 + 14, 116, 34, 17, '#000');    // the camera pill
  circ(30, -SH / 2 + 31, 7, '#151515');
  ctx.restore();
}
// screen-space helpers (inside phone())
function statusBar(time = '3:00', dark = true) {
  const c = dark ? '#f2f2f2' : '#111';
  text(time, 46, 40, `600 19px ${UI}`, c, 'left');
  for (let i = 0; i < 4; i++) rr(276 + i * 8, 34 - i * 3, 5, 6 + i * 3, 1, c);
  rrS(312, 26, 32, 15, 4, c, 2); rr(315, 29, 22, 9, 2, c); rr(345, 30, 2, 7, 1, c);
}
// the assistant's avatar: a plain ring with a dot (no real logo)
function aiAvatar(x, y, r, red = 0) {
  ctx.save(); glow(red > 0 ? 'rgba(255,43,43,0.8)' : 'rgba(255,255,255,0.5)', 10);
  circS(x, y, r, red > 0 ? C.red : '#e8e8e8', r * 0.16); circ(x, y, r * 0.34, red > 0 ? C.red : '#e8e8e8'); ctx.restore();
}
function wrapLines(str, maxW, font) {
  ctx.font = font; const out = []; let cur = '';
  for (const w of str.split(' ')) { const tr = cur ? cur + ' ' + w : w; if (ctx.measureText(tr).width > maxW && cur) { out.push(cur); cur = w; } else cur = tr; }
  if (cur) out.push(cur); return out;
}
// one chat bubble; returns its height. m: {me, text, photo (fn w,h), red, chars (0..1 typed out)}
function bubbleH(m) {
  if (m.photo) return (m.ph || 300) + 16;
  if (m.dots) return 54;
  const ls = wrapLines(m.text, 230, `500 23px ${UI}`); return ls.length * 31 + 26;
}
function chatBubble(m, y, t) {
  const font = `500 23px ${UI}`;
  if (m.photo) { const w = m.pw || 250, h = m.ph || 300, x = m.me ? SW - 16 - w : 64;
    ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, 20); ctx.clip(); m.photo(x, y, w, h); ctx.restore(); rrS(x, y, w, h, 20, '#333', 2); return h + 16; }
  if (m.dots) { rr(64, y, 92, 44, 22, '#262626'); for (let i = 0; i < 3; i++) circ(90 + i * 20, y + 22 + Math.sin(t * 9 - i * 0.9) * 4, 6, '#bdbdbd'); return 54; }
  let str = m.text; if (m.chars != null && m.chars < 1) str = str.slice(0, Math.floor(str.length * clamp(m.chars)));
  const lsFull = wrapLines(m.text, 230, font), ls = wrapLines(str || ' ', 230, font);
  ctx.font = font; const w = Math.max(...lsFull.map(l => ctx.measureText(l).width)) + 34, h = lsFull.length * 31 + 16;
  const x = m.me ? SW - 16 - w : 64;
  rr(x, y, w, h, 20, m.me ? '#ececec' : (m.red ? '#3a0d0d' : '#262626'));
  ls.forEach((l, i) => text(l, x + 17, y + 32 + i * 31, font, m.me ? '#111' : (m.red ? '#ff5a5a' : '#f2f2f2'), 'left'));
  return h + 10;
}
// a full chat screen. msgs: [{me, text|photo|dots, at (time it appears), status}], o.input (text being typed), o.header
function chatScreen(t, msgs, o = {}) {
  rr(0, 0, SW, SH, 0, '#0a0a0a'); statusBar(o.time || '3:00');
  // header
  ln(0, 118, SW, 118, 1.5, '#222');
  pthS('M30,72 l-12,12 l12,12', '#bdbdbd', 3.5);
  aiAvatar(78, 84, 20, o.redAvatar || 0); text('Assistant', 110, 80, `600 21px ${UI}`, '#f2f2f2', 'left');
  text(o.sub || 'online', 110, 104, `400 15px ${UI}`, o.subRed ? '#ff5a5a' : '#8a8a8a', 'left');
  // messages stack from the top; when they overflow, the list scrolls up
  const shown = msgs.filter(m => t >= (m.at ?? -1));
  let total = 0; for (const m of shown) total += bubbleH(m) + 10;
  const top = 140, bottom = SH - 110, off = Math.max(0, total - (bottom - top));
  ctx.save(); ctx.beginPath(); ctx.rect(0, 120, SW, bottom - 120 + 6); ctx.clip();
  let y = top - off;
  for (const m of shown) {
    const k = easeOut(prog(t, m.at ?? -1, 0.25));
    ctx.save(); ctx.globalAlpha *= k; ctx.translate(0, 14 * (1 - k));
    if (!m.me && !m.dots && m.avatar !== false) aiAvatar(38, y + 22, 13, m.red ? 1 : 0);
    const h = chatBubble(m, y, t);
    if (m.status) text(m.status, SW - 20, y + h + 8, `500 14px ${UI}`, m.statusRed ? '#ff5a5a' : '#8a8a8a', 'right');
    ctx.restore();
    y += h + (m.status ? 26 : 0) + 10;
  }
  ctx.restore();
  // input bar
  rr(16, SH - 92, SW - 90, 52, 26, '#1d1d1d');
  const inp = o.input || '';
  if (inp) { text(inp, 38, SH - 58, `500 21px ${UI}`, '#f2f2f2', 'left'); ctx.font = `500 21px ${UI}`;
    if ((t * 2) % 1 < 0.6) rr(40 + ctx.measureText(inp).width, SH - 78, 2.5, 26, 1, '#ececec'); }
  else text('Message', 38, SH - 58, `400 21px ${UI}`, '#666', 'left');
  circ(SW - 44, SH - 66, 25, inp ? '#ececec' : '#2a2a2a'); pthS(`M${SW - 44},${SH - 54} l0,-24 m-10,10 l10,-10 l10,10`, inp ? '#111' : '#666', 3.5);
  rr(SW / 2 - 66, SH - 14, 132, 5, 3, '#555');
}
function lockScreen(t, o = {}) {
  const g = ctx.createLinearGradient(0, 0, 0, SH); g.addColorStop(0, '#15161a'); g.addColorStop(1, '#050506'); ctx.fillStyle = g; ctx.fillRect(0, 0, SW, SH);
  statusBar('', true);
  text(o.date || 'Wednesday, October 21', SW / 2, 136, `600 21px ${UI}`, '#d8d8d8');
  text(o.time || '3:00', SW / 2, 260, `600 112px ${UI}`, o.timeRed ? '#ff3b3b' : '#f2f2f2');
  for (const n of o.notes || []) {
    if (t < n.at) continue; const k = easeOut(prog(t, n.at, 0.35)), y = (n.y ?? 330) - 30 * (1 - k);
    const nh = 96 + 25 * ((Array.isArray(n.text) ? n.text.length : 1) - 1);
    ctx.save(); ctx.globalAlpha *= k; rr(14, y, SW - 28, nh, 22, 'rgba(70,70,76,0.75)');
    rr(30, y + 18, 40, 40, 10, '#0a0a0a'); aiAvatar(50, y + 38, 12, n.red ? 1 : 0);
    text('Assistant', 84, y + 34, `600 18px ${UI}`, '#f2f2f2', 'left'); text(n.when || 'now', SW - 34, y + 34, `400 15px ${UI}`, '#a8a8a8', 'right');
    (Array.isArray(n.text) ? n.text : [n.text]).forEach((l, i) => text(l, 84, y + 64 + i * 25, `400 19px ${UI}`, n.red ? '#ff6a6a' : '#e8e8e8', 'left'));
    ctx.restore();
  }
  rr(SW / 2 - 66, SH - 14, 132, 5, 3, '#888');
}
// a thumb reaching in from the bottom right of the screen; tip at (x,y) in screen space
function thumb(x, y, press = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(-0.42); ctx.scale(1 - press * 0.05, 1 - press * 0.05);
  glow('rgba(0,0,0,0.6)', 22); rr(-38, -6, 76, 420, 38, '#d9d9d9'); noGlow();
  rr(-26, 6, 52, 64, 22, '#efefef'); rrS(-26, 6, 52, 64, 22, '#b0b0b0', 2);   // nail
  pthS('M-34,150 q34,14 68,0', '#a8a8a8', 3);
  ctx.restore();
}

// ---------- the photo it took: you asleep, from the corner of the ceiling, lit by a flash ----------
// draws into the rect (x,y,w,h). o.zoom 1..: how close it was taken; o.n seeds the small differences between nights; o.stamp: timestamp text
function ceilPhoto(x, y, w, h, o = {}) {
  const z = o.zoom ?? 1, n = o.n ?? 0;
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  rr(x, y, w, h, 0, '#0c0c0c');
  // the scene is drawn in a 1000x1000 world seen from above, rotated as if from the corner
  const head = { x: 330, y: 300 };
  ctx.translate(x + w / 2, y + h / 2); const sc = Math.min(w, h) / 1000 * z; ctx.scale(sc, sc);
  ctx.rotate(-0.38 + hash(n + 1) * 0.06);
  const fz = lerp(0, 1, clamp((z - 1) / 3));
  ctx.translate(-lerp(500, head.x, fz), -lerp(520, head.y, fz));
  // floor boards
  for (let i = -8; i < 20; i++) ln(-400 + i * 90, -400, -400 + i * 90, 1500, 2, '#262626');
  // nightstand with the phone glowing on it
  rr(730, 120, 170, 170, 8, '#3a3a3a'); rrS(730, 120, 170, 170, 8, '#5a5a5a', 3);
  ctx.save(); glow('rgba(220,232,255,0.9)', 26); rr(790, 160, 52, 96, 8, '#dfe8ff'); ctx.restore();
  // bed from above: frame, mattress, pillow, you, the blanket
  rr(160, 120, 540, 880, 18, '#8c8c8c'); rr(176, 136, 508, 848, 14, '#bdbdbd');
  rr(210, 170, 250, 140, 40, '#e9e9e9');                                    // pillow
  pth('M190,360 C260,330 420,340 640,350 L670,970 L190,970 Z', '#f4f4f4');   // blanket
  ctx.save(); ctx.globalAlpha = 0.18; pthS('M240,500 q120,30 240,0 M230,680 q160,40 380,-10 M300,850 q120,20 300,-6', '#000', 6); ctx.restore();
  // you, from above: the back of your head and hair, shoulder, one arm out over the blanket
  ell(head.x, head.y, 62, 74, -0.3, '#d8d8d8');                                // face side
  pth(`M${head.x - 60},${head.y - 30} C${head.x - 40},${head.y - 96} ${head.x + 60},${head.y - 90} ${head.x + 66},${head.y - 4} C${head.x + 40},${head.y - 30} ${head.x - 20},${head.y - 34} ${head.x - 60},${head.y - 30} Z`, '#2a2a2a');   // hair
  pth('M260,370 C300,340 420,350 450,400 L450,420 L250,420 Z', '#e6e6e6');      // shoulder under the blanket edge
  if (o.awake) {
    // you, awake: both arms up, holding the phone over your chest, its light on your face
    ctx.save(); const gl = ctx.createRadialGradient(head.x + 20, head.y + 60, 10, head.x + 20, head.y + 60, 260);
    gl.addColorStop(0, 'rgba(215,228,255,0.55)'); gl.addColorStop(1, 'rgba(215,228,255,0)'); ctx.fillStyle = gl; ctx.fillRect(head.x - 260, head.y - 200, 520, 520); ctx.restore();
    ell(head.x - 14, head.y + 10, 11, 8, -0.3, '#f4f4f4'); circ(head.x - 10, head.y + 11, 5, '#111');   // open eye, looking at the screen
    ctx.lineCap = 'round';
    // sleeves out of the blanket, forearms up to the phone (outlined so they read against the sheet)
    ctx.lineJoin = 'round';
    for (const pts of [[[255, 405], [205, 560], [305, 540]], [[445, 415], [505, 575], [435, 520]]]) for (const [w, c] of [[50, '#8a8a8a'], [42, '#d6d6d6']]) {
      ctx.beginPath(); ctx.moveTo(...pts[0]); ctx.lineTo(...pts[1]); ctx.lineTo(...pts[2]); ctx.strokeStyle = c; ctx.lineWidth = w; ctx.stroke(); }
    ctx.save(); ctx.translate(370, 520); ctx.rotate(-0.25);
    glow('rgba(215,228,255,0.7)', 30); rr(-62, -95, 124, 190, 18, '#161616'); noGlow();
    rrS(-62, -95, 124, 190, 18, '#555', 4); rr(-40, -78, 34, 34, 8, '#2a2a2a'); circ(-30, -68, 7, '#0a0a0a'); circ(-16, -56, 7, '#0a0a0a');   // the phone, back to the camera, its lenses
    for (const sx of [-1, 1]) { ctx.save(); ctx.translate(sx * 62, 10); rr(-16, -34, 32, 68, 14, '#8a8a8a'); rr(-12, -30, 24, 60, 11, '#dcdcdc'); ctx.restore(); }   // fingers round its edges
    ctx.restore();
  } else {
    pthS(`M${head.x - 16},${head.y + 10} q10,7 20,0`, '#333', 4);                // closed eye
    ctx.save(); ctx.translate(470, 430); ctx.rotate(0.5 + hash(n + 3) * 0.3); rr(0, -20, 200, 40, 20, '#dcdcdc'); circ(206, 0, 26, '#e2e2e2'); ctx.restore();   // arm over the blanket
  }
  ctx.restore();
  // the flash: blown-out centre, harsh fall-off, a little noise
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  const g = ctx.createRadialGradient(x + w * 0.5, y + h * 0.48, Math.min(w, h) * 0.05, x + w * 0.5, y + h * 0.5, Math.max(w, h) * 0.75);
  g.addColorStop(0, 'rgba(255,252,245,0.42)'); g.addColorStop(0.45, 'rgba(255,252,245,0.05)'); g.addColorStop(0.75, 'rgba(0,0,0,0.35)'); g.addColorStop(1, 'rgba(0,0,0,0.85)');
  ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  if (o.grain !== false && grainC) { ctx.globalAlpha = 0.14; ctx.drawImage(grainC[(n % 4 + 4) % 4], x, y, w, h); ctx.globalAlpha = 1; }
  if (o.stamp) { const fs = Math.max(11, Math.round(h * 0.055)); ctx.save(); redGlow(6); text(o.stamp, x + w - fs * 0.6, y + h - fs * 0.6, `600 ${fs}px Plex`, '#ff4a2a', 'right'); ctx.restore(); }
  ctx.restore();
}
// the newest photo: so close it is only your eye, shut, lashes, skin texture, the flash on it
function eyePhoto(x, y, w, h, o = {}) {
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  rr(x, y, w, h, 0, '#cfcfcf');
  const cx = x + w / 2, cy = y + h / 2, s = Math.min(w, h) / 500;
  ctx.translate(cx, cy); ctx.scale(s, s); ctx.rotate(-0.12);
  // brow, lid crease, the closed seam and the lashes
  pth('M-260,-150 C-120,-220 120,-220 260,-140 L260,-110 C120,-180 -120,-180 -260,-120 Z', '#3a3a3a');
  pthS('M-200,-30 C-100,-90 100,-90 200,-30', '#9a9a9a', 6);
  pthS('M-210,20 C-100,70 100,70 210,20', '#2a2a2a', 9);
  for (let i = 0; i < 16; i++) { const u = -190 + i * 25, v = 20 + 50 * (1 - Math.pow(u / 210, 2)); pthS(`M${u},${v} q${u * 0.02},34 ${u * 0.08 + 6},58`, '#1e1e1e', 4.5); }
  for (let i = 0; i < 40; i++) circ((hash(i * 1.3) - 0.5) * 480, (hash(i * 2.9) - 0.5) * 420, 1.5 + hash(i) * 2, 'rgba(0,0,0,0.12)');
  ctx.restore();
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  const g = ctx.createRadialGradient(x + w * 0.45, y + h * 0.4, 5, x + w / 2, y + h / 2, Math.max(w, h) * 0.7);
  g.addColorStop(0, 'rgba(255,255,255,0.5)'); g.addColorStop(0.5, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(0,0,0,0.75)'); ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  if (grainC) { ctx.globalAlpha = 0.16; ctx.drawImage(grainC[1], x, y, w, h); ctx.globalAlpha = 1; }
  if (o.stamp) { const fs = Math.max(11, Math.round(h * 0.055)); ctx.save(); redGlow(6); text(o.stamp, x + w - fs * 0.6, y + h - fs * 0.6, `600 ${fs}px Plex`, '#ff4a2a', 'right'); ctx.restore(); }
  ctx.restore();
}
// where the lens on its face is, in the room
const LENS = { x: WALL + 172 * TS, y: CEIL + 117 * TS };
function lensGlint(a = 1) { ctx.save(); ctx.globalAlpha *= a; redGlow(14); circ(LENS.x, LENS.y, 4.5, C.red); ctx.restore(); }
// a dashed sight line
function sight(x1, y1, x2, y2, col, p = 1, w = 4) { ctx.save(); ctx.setLineDash([14, 11]); lnP(x1, y1, x2, y2, w, col, p); ctx.restore(); }
// ---------- EP02 scenes ----------
const ev = type => window.TL.events.filter(e => e.type === type);
const evAfter = (type, t0) => ev(type).find(e => e.t >= t0 - 0.01);
// vibration of the phone around a buzz event (two pulses in the buzz file)
function buzzK(t) { for (const e of ev('buzz')) { const d = t - e.t; if (d >= 0 && d < 1.5) return (d < 0.5 || (d > 0.75 && d < 1.25)) ? 1 : 0; } return 0; }
const PHX = 960, PHY = 560, PHS = 1.3;                 // the standard phone close-up
// the AI's earlier messages, the ones every chat in this video starts from
const M_AWAKE = { text: 'Are you awake?', at: -1 };
const PHOTO = (stamp = '03:00:41', zoom = 1, n = 0) => (x, y, w, h) => ceilPhoto(x, y, w, h, { stamp, zoom, n });
const M_PHOTO = { photo: PHOTO(), ph: 300, at: -1 };
function phoneShot(t, seg, fn, o = {}) {
  cam(t, seg.start, seg.end - seg.start + 0.8, o.z0 ?? 1.04, o.z1 ?? 1.1, o.cx ?? PHX, o.cy ?? 470, () => {
    phone(o.x ?? PHX, o.y ?? PHY, o.s ?? PHS, fn, { bright: o.bright ?? 1, rot: o.rot || 0 });
    if (o.after) o.after();
  });
}
// labels beside the phone
const sideTag = (t, t0, s, x, y, col = C.fig, size = 44) => { if (t >= t0) pop(t, t0, x, y, () => tag(s, x, y + 10, col, size, 'center')); };
// white icons for the opening "do not" row
function icon2(name, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); glow('rgba(255,255,255,0.3)', 16);
  if (name === 'photo') { rrS(-90, -70, 180, 140, 14, C.fig, 10); circ(-20, 4, 26, C.fig); rr(8, -8, 56, 40, 14, C.fig); circ(52, -40, 10, C.fig); }
  if (name === 'ask') { rrS(-96, -70, 192, 120, 26, C.fig, 10); pth('M-50,48 L-70,94 L-14,50 Z', C.fig); text('?', 0, 20, '900 100px M', C.fig); }
  if (name === 'up') { pth('M-90,30 C-50,-26 50,-26 90,30 C50,86 -50,86 -90,30 Z', C.fig); noGlow(); circ(0, 30, 24, '#000'); glow(); ln(0, -40, 0, -110, 12, C.fig); pth('M-28,-96 L0,-130 L28,-96 Z', C.fig); }
  noGlow(); ctx.restore();
}

// ---------- hook ----------
S.h1 = (t, seg) => {
  const tn = wt(seg, 'not');
  // the video opens on the phone: the photo has just arrived (frame 0 already shows it)
  phoneShot(t, { start: 0, end: seg.end }, () => chatScreen(t, [M_AWAKE, M_PHOTO]), { z0: 1.55, z1: 1.7, cy: 480 });
  if (t >= tn) pop(t, tn, 1500, 300, () => tag('DO NOT REPLY', 1500, 310, C.red, 54, 'center'), 0.3);
};
S.h2 = (t, seg) => {
  const items = [['photo', 520, 'open'], ['ask', 960, 'ask'], ['up', 1400, 'look']];
  cam(t, seg.start, seg.end - seg.start, 1, 1.04, W / 2, 470, () => {
    items.forEach(([ic, x, w]) => {
      const t0 = wt(seg, w) - 0.25;
      pop(t, t0, x, 470, () => { rrS(x - 170, 300, 340, 340, 26, C.dim, 5); icon2(ic, x, 470, 1.05); });
      redX(x, 470, 120, prog(t, wt(seg, w) + 0.35, 0.35));
    });
  });
};

// ---------- rule 1: do not reply ----------
S.a0 = (t, seg) => ruleCard(t, seg, 1, 'DO NOT REPLY');
S.a1 = (t, seg) => {
  const tl = wt(seg, 'lights'), t3 = wt(seg, 'three');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.3, 1000, 600, () => {
    room2(t); bed(BX, FY, 1.05, 'sleep', {});
    phoneFlat(t >= tl ? easeOut(prog(t, tl, 0.25)) : 0, buzzK(t));
    cornerThing(t, { vis: t >= tl ? 0.1 : 0, lit: 0, face: 'lens', red: 0.5, breath: 0.6 }); if (t >= tl) lensGlint(0.8);
    if (t >= t3) pop(t, t3, 1400, 520, () => { redGlow(14); text('3:00', 1400, 560, '900 120px M', C.red); noGlow(); spaced('AM', 1400, 620, '900 32px M', C.mid, 8); });
  });
};
S.a2 = (t, seg) => {
  const to = wt(seg, 'one') - 0.1, tf = wt(seg, 'from'), ta = wt(seg, 'are');
  phoneShot(t, seg, () => lockScreen(t, { notes: [{ at: to, text: t >= ta - 0.1 ? 'Are you awake?' : '' }] }), { z0: 1.0, z1: 1.08, cy: 420 });
  sideTag(t, tf, 'YOUR AI', 360, 380, C.fig, 46);
};
S.a3 = (t, seg) => {
  const tdo = wt(seg, 'open'), task = wt(seg, 'ask'), tnv = wt(seg, 'never');
  const hist = [{ me: true, text: 'what time is sunrise?', at: -1 }, { text: '6:58 AM.', at: -1 }, { me: true, text: 'set an alarm for 7', at: -1 }, { text: 'Done. 7:00 AM.', at: -1 },
    { me: true, text: 'thanks', at: -1 }, { text: 'Are you awake?', at: -1, red: true, status: 'TODAY 3:00 AM', statusRed: true }];
  phoneShot(t, seg, () => chatScreen(t, hist), { x: 760, cx: 860 });
  const rows = [['YOU OPENED IT', tdo], ['YOU ASKED IT', task], ['IT SPOKE FIRST', tnv]];
  rows.forEach(([l, t0], i) => { if (t < t0) return; const y = 360 + i * 120;
    slideIn(t, t0, 40, 0, () => { const last = i === 2;
      rrS(1130, y - 40, 64, 64, 10, C.red, 5); text(l, 1220, y + 6, '900 50px M', last ? C.red : C.fig, 'left');
      if (!last) redX(1162, y - 8, 22, prog(t, t0 + 0.2, 0.3)); else { redGlow(12); text('!', 1162, y + 14, '900 56px M', C.red); noGlow(); } }); });
  if (t >= tnv + 0.4) pop(t, tnv + 0.4, 1420, 760, () => tag('FIRST TIME', 1420, 770, C.red, 46, 'center'));
};
S.a4 = (t, seg) => {
  const td = wt(seg, 'delivered'), tr = wt(seg, 'read'), ta = wt(seg, 'answer');
  // your thumb hovers over the message, then pulls away
  const hov = clamp((t - seg.start) / 0.6) * (1 - clamp((t - ta - 0.3) / 0.5));
  phoneShot(t, seg, () => { chatScreen(t, [{ ...M_AWAKE, status: t >= td ? 'Delivered' : '' }]); if (hov > 0) thumb(230, lerp(900, 330, hov)); });
  if (t >= ta) pop(t, ta, 360, 420, () => tag('DO NOT ANSWER', 360, 430, C.red, 46, 'center'));
  if (t >= td) slideIn(t, td, 40, 0, () => { rrS(1300, 510, 60, 60, 10, C.fig, 5); check(1330, 540, 22, prog(t, td + 0.1, 0.3)); text('DELIVERED', 1380, 560, '900 54px M', C.fig, 'left'); });
  if (t >= tr) slideIn(t, tr, 40, 0, () => { ctx.save(); ctx.globalAlpha *= 0.85; text('READ', 1380, 680, '900 54px M', C.mid, 'left'); ctx.restore(); redGlow(10); lnP(1360, 664, 1560, 664, 9, C.red, prog(t, tr + 0.15, 0.25)); noGlow(); });
};
S.a5 = (t, seg) => {
  const tp = wt(seg, 'photo') - 0.05;
  phoneShot(t, seg, () => chatScreen(t, [M_AWAKE, ...(t < tp ? [{ dots: true, at: seg.start + 0.4 }] : [{ ...M_PHOTO, at: tp }])]), { z0: 1.0, z1: 1.1, cy: 460 });
  fadeIn(t, seg.start + 0.1, () => spaced('1 MINUTE LATER', 360, 360, '900 34px M', C.mid, 6));
};
S.a6 = (t, seg) => {
  const tk = wt(seg, 'taken') - 0.05, tab = wt(seg, 'above'), tc = wt(seg, 'corner'), ttw = wt(seg, 'two');
  if (t < tk) {   // "You. Asleep." on the phone
    phoneShot(t, { start: seg.start, end: tk }, () => chatScreen(t, [M_AWAKE, M_PHOTO]), { z0: 1.1, z1: 1.5, cy: 470 });
    if (t >= wt(seg, 'asleep')) pop(t, wt(seg, 'asleep'), 1460, 420, () => tag('YOU', 1460, 430, C.fig, 60, 'center'));
    return;
  }
  // the photo, full size
  cam(t, tk, seg.end - tk + 0.8, 1.0, 1.06, 760, 540, () => {
    ctx.save(); glow('rgba(255,255,255,0.15)', 30); rr(196, 136, 1008, 708, 6, '#ddd'); ctx.restore();
    ceilPhoto(200, 140, 1000, 700, { stamp: '03:00:41', n: 0 });
    // the angle: a small cut-away of the room, a lens in the corner and its cone down onto the bed
    if (t >= tab) slideIn(t, tab, 40, 0, () => {
      const ox = 1290, oy = 300, sc = 0.28;
      rrS(ox - 14, oy - 14, 540, 252, 10, C.dim, 3);
      ctx.save(); ctx.translate(ox, oy); ctx.scale(sc, sc); ctx.translate(-WALL, -CEIL + 40);
      ln(WALL, CEIL, 1900, CEIL, 8, C.mid); ln(WALL, CEIL, WALL, FY, 8, C.mid); ln(WALL, FY, 1900, FY, 8, C.mid);
      bed(BX, FY, 1.05, 'sleep', {});
      if (t >= tc) { ctx.save(); redGlow(20); circ(LENS.x, LENS.y, 26, C.red); ctx.restore();
        ctx.save(); ctx.globalAlpha *= 0.35 * prog(t, tc, 0.4); pth(`M${LENS.x},${LENS.y} L${BX + 40},${FY - 230} L${BX + 640},${FY - 180} Z`, C.red); ctx.restore(); }
      ctx.restore();
      if (t >= tc) text('FROM THE CORNER', ox + 256, oy + 300, '900 34px M', C.red);
    });
    if (t >= ttw) pop(t, ttw, 700, 900, () => { redGlow(10); spaced('2 MINUTES AGO', 700, 918, '900 46px M', C.red, 6); noGlow(); });
  });
  // the flash it took the picture with
  const fk = 1 - clamp((t - tk) / 0.35); if (fk > 0) { ctx.save(); ctx.globalAlpha = fk * 0.85; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
};
S.a7 = (t, seg) => {
  const ty = evAfter('typing', seg.end), sd = evAfter('send', seg.end), nt = evAfter('notif', seg.end), fl = evAfter('flash', seg.end);
  if (fl && t >= fl.t) {
    // the flash fires from the corner: for an instant, you can see what is holding on up there
    const d = t - fl.t;
    cam(t, fl.t, 0.4, 1.05, 1.12, 640, 460, () => {
      room2(t); bed(BX, FY, 1.05, 'woke', { look: -1 }); phoneInHand(t, 1);
      // the flash lights the walls from the corner; the thing itself stays a black shape in front of it
      const g = ctx.createRadialGradient(LENS.x, LENS.y, 20, LENS.x, LENS.y, 1500);
      g.addColorStop(0, 'rgba(255,255,255,0.85)'); g.addColorStop(0.5, 'rgba(230,230,230,0.45)'); g.addColorStop(1, 'rgba(200,200,200,0.12)');
      ctx.save(); ctx.globalAlpha = 1 - clamp(d / 0.3) * 0.45; ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400); ctx.restore();
      cornerThing(t, { vis: 1, lit: 0, face: 'lens', red: 1, reach: clamp(d / 0.18), breath: 0 }); lensGlint(1);
    });
    const k = 1 - clamp(d / 0.08); if (k > 0) { ctx.save(); ctx.globalAlpha = 0.6 * k; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    return;
  }
  const typed = ty && sd && t >= ty.t ? clamp((t - ty.t) / (sd.t - ty.t - 0.1)) : 0, msg = 'who took this?';
  const msgs = [M_AWAKE, M_PHOTO];
  if (sd && t >= sd.t) msgs.push({ me: true, text: msg, at: sd.t, status: 'Read' });
  if (sd && nt && t >= sd.t + 0.15 && t < nt.t) msgs.push({ dots: true, at: sd.t + 0.15 });
  if (nt && t >= nt.t) msgs.push({ text: 'Hold still.', at: nt.t, red: true });
  phoneShot(t, { start: seg.start, end: fl ? fl.t : seg.end }, () => chatScreen(t, msgs, { input: sd && t >= sd.t ? '' : msg.slice(0, Math.round(msg.length * typed)) }), { z0: 1.0, z1: 1.18, cy: 600 });
};

// ---------- rule 2: do not look at the corner ----------
S.b0 = (t, seg) => ruleCard(t, seg, 2, 'DO NOT LOOK AT THE CORNER');
S.b1 = (t, seg) => {
  const ta = wt(seg, 'angle');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.08, 900, 500, () => {
    ctx.save(); glow('rgba(255,255,255,0.15)', 30); rr(356, 156, 1008, 708, 6, '#ddd'); ctx.restore();
    ceilPhoto(360, 160, 1000, 700, { stamp: '03:00:41', n: 0 });
    // the lines of the bed run back to one point: up and to the left, outside the picture
    if (t >= ta) { const vp = { x: 130, y: -60 }, p = prog(t, ta, 0.7);
      [[560, 420], [1090, 330], [700, 800], [1250, 720]].forEach(([x, y], i) => { ctx.save(); ctx.setLineDash([16, 12]); lnP(x, y, vp.x, vp.y, 5, C.red, clamp(p * 1.4 - i * 0.12)); ctx.restore(); });
      if (p >= 1) pop(t, ta + 0.7, 300, 140, () => { tag('IT WAS UP HERE', 300, 150, C.red, 40, 'center'); }); }
  });
};
function cornerZoom(t, t0, d, z0, z1, fn) { cam(t, t0, d, z0, z1, 520, 360, fn); }
S.b2 = (t, seg) => {
  const tc = wt(seg, 'camera'), ts = wt(seg, 'shelf'), tn = wt(seg, 'nothing');
  cornerZoom(t, seg.start, seg.end - seg.start + 0.8, 1.15, 1.3, () => { room2(t); bed(BX, FY, 1.05, 'sleep', {});
    const p = prog(t, seg.start + 0.1, 0.5); ctx.save(); ctx.setLineDash([14, 10]); redGlow(10); ctx.beginPath(); ctx.arc(CORNER.x + 190, CORNER.y + 170, 200, 0, Math.PI * 2 * p); ctx.strokeStyle = C.red; ctx.lineWidth = 6; ctx.stroke(); ctx.restore(); });
  [['CAMERA', tc], ['SHELF', ts], ['ANYTHING TO STAND ON', tn]].forEach(([l, t0], i) => { if (t < t0) return; const y = 400 + i * 110;
    slideIn(t, t0, 40, 0, () => { rrS(1100, y - 40, 64, 64, 10, C.red, 5); text(l, 1190, y + 8, '900 50px M', C.fig, 'left'); redX(1132, y - 8, 22, prog(t, t0 + 0.2, 0.3)); }); });
};
S.b3 = (t, seg) => {
  const th = wt(seg, 'holding');
  cornerZoom(t, seg.start, seg.end - seg.start + 0.8, 1.5, 1.75, () => {
    room2(t); bed(BX, FY, 1.05, 'sleep', {}); phoneFlat(0.5, 0);
    cornerThing(t, { vis: lerp(0.2, 0.75, prog(t, th - 0.3, 1.2)), lit: 0.12, face: 'blank', breath: 0.8 });
  });
  if (t >= th + 0.3) pop(t, th + 0.3, 1450, 300, () => tag('HOLDING ON', 1450, 310, C.red, 50, 'center'));
};
// you, awake in bed with the phone up in front of your face; the corner behind you breathes
function awakeBed(t, o = {}) {
  room2(t); bed(BX, FY, 1.05, 'woke', { look: 1 }); phoneInHand(t, o.lit ?? 1);
  const br = 0.5 + 0.5 * Math.sin(t * 2.1);
  cornerThing(t, { vis: o.vis ?? 0.3, lit: 0.1, face: 'blank', breath: 1.2 });
  // the dark in the corner swells and shrinks, like something breathing
  ctx.save(); const g = ctx.createRadialGradient(CORNER.x + 160, CORNER.y + 160, 10, CORNER.x + 160, CORNER.y + 160, 380 + 50 * br);
  g.addColorStop(0, `rgba(0,0,0,${0.55 + 0.2 * br})`); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(CORNER.x - 10, CORNER.y - 10, 700, 700); ctx.restore();
}
S.b4 = (t, seg) => {
  const tb = wt(seg, 'breath');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.1, 1.25, 600, 420, () => {
    awakeBed(t, { vis: lerp(0.15, 0.4, prog(t, seg.start, 3)) });
    // dust in the light of the phone drifts up to the corner and back, in time with the breathing
    if (t >= tb - 0.6) { const k = prog(t, tb - 0.6, 0.8); for (let i = 0; i < 26; i++) {
      const bx = HEAD_W.x + 80 + hash(i) * 220, by = HEAD_W.y - 120 + hash(i * 3.3) * 200, pull = 0.5 + 0.5 * Math.sin(t * 2.1 + Math.PI);
      const x = lerp(bx, LENS.x, pull * 0.3), y = lerp(by, LENS.y, pull * 0.3);
      ctx.save(); ctx.globalAlpha *= k * (0.25 + 0.4 * hash(i * 7.1)); circ(x, y, 1.5 + hash(i * 5) * 2, '#dfe8ff'); ctx.restore(); } }
  });
};
S.b5 = (t, seg) => {
  const te = wt(seg, 'eyes'), tl = wt(seg, 'looking'), tth = wt(seg, 'thinks');
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.1, 1.15, 600, 420, () => {
    awakeBed(t, { vis: 0.4 });
    const ex = HEAD_W.x + 28, ey = HEAD_W.y - 6, px = HEAD_W.x + 150, py = HEAD_W.y + 30;
    if (t >= te) sight(ex, ey, px - 8, py - 10, C.fig, prog(t, te, 0.5), 4);
    // it does not look at you. It looks at what you look at.
    if (t >= tth) { sight(LENS.x, LENS.y, px - 4, py - 30, C.red, prog(t, tth, 0.8), 5); lensGlint(1); }
  });
  if (t >= tl) pop(t, tl, 1420, 300, () => tag('EYES ON THE SCREEN', 1420, 310, C.fig, 46, 'center'));
};
S.b6 = (t, seg) => {
  const tu = wt(seg, 'turn'), tev = wt(seg, 'every');
  // the screen dims by itself; you push the brightness back up, again and again
  const ups = [tu + 0.2, tev, tev + 0.9];
  let b = 1, last = seg.start;
  for (const u of ups) if (t >= u) last = u;
  const since = t - last, dimT = 1.1;
  b = t < ups[0] ? lerp(1, 0.18, clamp((t - seg.start) / (ups[0] - seg.start))) : (since < 0.25 ? lerp(0.25, 1, since / 0.25) : lerp(1, 0.25, clamp((since - 0.25) / dimT)));
  const pressing = ups.some(u => t >= u - 0.25 && t < u + 0.25);
  phoneShot(t, seg, () => {
    chatScreen(t, [M_AWAKE, M_PHOTO]);
    // the brightness slider pulled down from the top
    ctx.save(); ctx.globalAlpha = 0.92; rr(30, 128, SW - 60, 64, 32, '#2b2b2b'); rr(30, 128, (SW - 60) * Math.max(0.12, b), 64, 32, '#ececec');
    circ(66, 160, 13, b > 0.4 ? '#111' : '#ececec'); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; ln(66 + Math.cos(a) * 18, 160 + Math.sin(a) * 18, 66 + Math.cos(a) * 23, 160 + Math.sin(a) * 23, 3, b > 0.4 ? '#111' : '#ececec'); }
    ctx.restore();
    if (pressing) thumb(30 + (SW - 60) * Math.max(0.12, b), 168, 0.5);
  }, { bright: lerp(0.35, 1, b) });
  slideIn(t, seg.start + 0.2, 40, 0, () => { spaced('BRIGHTNESS', 1460, 420, '900 34px M', C.mid, 6); text(Math.round(b * 100) + '%', 1460, 540, '900 110px M', b < 0.5 ? C.red : C.fig); });
  if (t >= tev) pop(t, tev, 470, 420, () => tag('EVERY TIME', 470, 430, C.fig, 46, 'center'));
};

// ---------- rule 3: do not delete the photo ----------
S.c0 = (t, seg) => ruleCard(t, seg, 3, 'DO NOT DELETE THE PHOTO');
function photoViewer(t, o = {}) {
  rr(0, 0, SW, SH, 0, '#000'); statusBar('3:02');
  text('Today 3:00 AM', SW / 2, 96, `600 19px ${UI}`, '#f2f2f2');
  ceilPhoto(0, 200, SW, 380, { stamp: o.stamp || '03:00:41', zoom: o.zoom || 1, n: o.n || 0 });
  const y = SH - 86; // toolbar: share, heart, info, trash
  pthS(`M40,${y + 10} l0,22 l36,0 l0,-22 M58,${y - 6} l0,26 m-10,-16 l10,-10 l10,10`, '#ddd', 3);
  pthS(`M140,${y + 4} c0,-14 22,-14 22,2 c0,-16 22,-16 22,-2 c0,14 -22,26 -22,28 c0,-2 -22,-14 -22,-28`, '#ddd', 3);
  circS(254, y + 12, 15, '#ddd', 3); text('i', 254, y + 19, `600 18px ${UI}`, '#ddd');
  const tr = o.trash || 0; ctx.save(); if (tr > 0) { redGlow(14 * tr); } pthS(`M318,${y - 4} l36,0 m-30,0 l3,34 l24,0 l3,-34 m-21,-6 l12,0`, tr > 0.5 ? '#ff3b3b' : '#ddd', 3); ctx.restore();
}
S.c1 = (t, seg) => {
  const tt = wt(seg, 'thumb');
  const k = easeOut(prog(t, tt - 0.4, 0.8));
  phoneShot(t, seg, () => { photoViewer(t, { trash: k }); if (k > 0) thumb(lerp(420, 336, k), lerp(980, SH - 60, k)); }, { z0: 1.0, z1: 1.12, cy: 700 });
  if (t >= tt + 0.4) pop(t, tt + 0.4, 1450, 420, () => tag('DO NOT', 1450, 430, C.red, 60, 'center'));
};
S.c2 = (t, seg) => {
  const td = wt(seg, 'delete'), tn = wt(seg, 'new'), tc = wt(seg, 'closer');
  const shots = [[seg.start - 1, 1, '03:00:41', false], [tn, 1.9, '03:04:10', true], [tc, 3.1, '03:06:52', true]];   // the new ones: you, awake, deleting it
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, 960, 520, () => {
    shots.forEach(([t0, z, st, awake], i) => { if (t < t0) return;
      const k = easeOut(prog(t, t0, 0.35)), nextT = shots[i + 1] ? shots[i + 1][0] : 1e9, gone = prog(t, nextT - 0.05, 0.3);
      ctx.save(); ctx.globalAlpha *= k * (1 - gone * 0.75); const x = 460 + i * 60 - gone * 40, y = 170 + i * 30;
      ctx.translate(x + 500, y + 350); ctx.rotate((i - 1) * 0.03); ctx.scale(lerp(1.1, 1, k) * (1 - gone * 0.1), lerp(1.1, 1, k) * (1 - gone * 0.1)); ctx.translate(-x - 500, -y - 350);
      glow('rgba(0,0,0,0.9)', 40); rr(x - 6, y - 6, 1012, 712, 6, '#ddd'); noGlow(); ceilPhoto(x, y, 1000, 700, { stamp: st, zoom: z, n: i, awake });
      ctx.restore(); });
    // the white flash of each new one
    for (const t0 of [tn, tc]) { const fk = 1 - clamp((t - t0) / 0.3); if (t >= t0 && fk > 0) { ctx.save(); ctx.globalAlpha = fk * fk * 0.3; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); ctx.restore(); } }
  });
  if (t >= td) pop(t, td, 260, 300, () => { spaced('DELETED', 260, 290, '900 30px M', C.mid, 6); text(t >= tc ? '2' : t >= tn ? '1' : '1', 260, 400, '900 110px M', C.red); });
  if (t >= tc) pop(t, tc + 0.2, 1660, 860, () => tag('CLOSER', 1660, 870, C.red, 54, 'center'));
};
// the "Recently Deleted" album: a grid of nights, each a little closer
function deletedAlbum(t, scroll = 0) {
  rr(0, 0, SW, SH, 0, '#000'); statusBar('3:03');
  pthS('M30,72 l-12,12 l12,12', '#bdbdbd', 3.5); text('Recently Deleted', SW / 2, 92, `600 22px ${UI}`, '#f2f2f2');
  text('365 Photos', SW / 2, 120, `400 15px ${UI}`, '#8a8a8a');
  ctx.save(); ctx.beginPath(); ctx.rect(0, 140, SW, SH - 140); ctx.clip();
  const c = 3, g = 3, w = (SW - g * (c - 1)) / c;
  for (let i = 0; i < 60; i++) { const r = Math.floor(i / c), x = (i % c) * (w + g), y = 146 + r * (w + g) - scroll;
    if (y > SH || y < 40) continue;
    ceilPhoto(x, y, w, w, { zoom: 1 + (59 - i) / 59 * 3.2, n: i, grain: false });
    text(`${1 + (i * 7) % 28}d`, x + w - 8, y + w - 8, `600 13px ${UI}`, '#f2f2f2', 'right'); }
  ctx.restore();
}
S.c3 = (t, seg) => {
  const tn = wt(seg, 'never');
  phoneShot(t, seg, () => deletedAlbum(t, 0), { z0: 1.0, z1: 1.06 });
  if (t >= tn) pop(t, tn, 1470, 420, () => { tag('YOU NEVER', 1470, 400, C.red, 48, 'center'); tag('TOOK THESE', 1470, 490, C.red, 48, 'center'); });
};
S.c4 = (t, seg) => {
  const te = wt(seg, 'each'), tl = wt(seg, 'last');
  // every night of the year, one photo; the film strip runs toward the newest, each one closer
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.0, 1.05, 960, 520, () => {
    const n = 9, w = 340, gap = 30, run = easeOut(prog(t, seg.start, seg.end - seg.start + 0.5)) * (n - 4) * (w + gap);
    for (let i = 0; i < n; i++) { const x = 120 + i * (w + gap) - run, y = 330;
      if (x > W || x + w < 0) continue;
      glow('rgba(0,0,0,0.9)', 20); rr(x - 4, y - 4, w + 8, w * 0.75 + 8, 4, '#ddd'); noGlow();
      ceilPhoto(x, y, w, w * 0.75, { zoom: 1 + i * 0.42, n: i, grain: false });
      text(['OCT 13', 'OCT 14', 'OCT 15', 'OCT 16', 'OCT 17', 'OCT 18', 'OCT 19', 'OCT 20', 'OCT 21'][i], x + w / 2, y + w * 0.75 + 52, '600 30px Plex', i === n - 1 ? C.red : C.mid); }
    if (t >= te) { const p = prog(t, te, 0.8); ctx.save(); redGlow(12); lnP(240, 760, 1680, 760, 8, C.red, p); if (p >= 1) pth('M1680,738 L1720,760 L1680,782 Z', C.red); ctx.restore();
      if (t >= tl) pop(t, tl, 960, 840, () => spaced('CLOSER EVERY NIGHT', 960, 860, '900 46px M', C.red, 8)); }
  });
};
S.c5 = (t, seg) => {
  const te = wt(seg, 'eye');
  cam(t, seg.start, seg.end - seg.start + 1.0, 1.0, 1.12, 960, 520, () => {
    ctx.save(); glow('rgba(255,255,255,0.15)', 30); rr(406, 166, 1108, 708, 6, '#ddd'); ctx.restore();
    eyePhoto(410, 170, 1100, 700, { stamp: 'TODAY 02:58' });
    if (t >= te) { const p = 0.5 + 0.5 * Math.sin((t - te) * 7); ctx.save(); redGlow(30 * p); rrS(398, 158, 1124, 724, 10, C.red, 8); ctx.restore(); }
  });
};

// ---------- rule 4: emergency protocol ----------
S.d0 = (t, seg) => emergencyCard(t, seg);
S.d1 = (t, seg) => {
  const ta = wt(seg, 'awake'), to = wt(seg, 'over');
  phoneShot(t, seg, () => chatScreen(t, [M_AWAKE, M_PHOTO, { me: true, text: 'who took this?', status: 'Read', at: -1 }, { text: 'I know you are awake.', red: true, at: ta }], { redAvatar: t >= ta ? 1 : 0, sub: t >= ta ? 'watching' : 'online', subRed: t >= ta }), { x: 760, cx: 860 });
  if (t >= ta) { ctx.save(); ctx.globalAlpha = 0.08 * (0.5 + 0.5 * Math.sin((t - ta) * 7)); ctx.fillStyle = '#ff0000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  if (t >= to) pop(t, to, 1440, 520, () => { redGlow(14); spaced('RULES 1-3: OVER', 1440, 540, '900 52px M', C.red, 6); noGlow(); });
};
const NOPE2 = [['TURN IT OFF', 'd3'], ['THROW IT AWAY', 'd4'], ['COVER THE CAMERA', 'd5'], ['ASK IT TO STOP', 'd6']];
function nopeList2(t, upto, x0 = 1290) {
  // a dark card behind the list so it reads over the room
  ctx.save(); ctx.globalAlpha *= 0.82; glow('rgba(0,0,0,0.9)', 40); rr(x0 - 40, 150, 560, 160 + 80 * Math.min(upto, 3), 12, '#050505'); ctx.restore();
  spaced('DOES NOT WORK', x0, 200, '900 34px M', C.red, 6, 'left');
  NOPE2.forEach(([lbl], i) => { if (i > upto) return; const y = 300 + i * 80, done = i < upto;
    ctx.save(); ctx.globalAlpha *= done ? 0.55 : 1; text(lbl, x0 + 60, y + 12, '900 38px M', done ? C.mid : C.fig, 'left'); rrS(x0, y - 22, 40, 40, 6, C.red, 4); redX(x0 + 20, y - 2, 13, done ? 1 : 0.0); ctx.restore(); });
}
S.d2 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.05, W / 2, 500, () => {
    pop(t, seg.start, 960, 450, () => { hazard(560, 260, 800, 30, t * 40); rrS(560, 300, 800, 330, 10, C.fig, 5);
      spaced('WHAT DOES NOT WORK', 960, 482, '900 50px M', C.fig, 5); hazard(560, 640, 800, 30, -t * 40); });
  });
};
S.d3 = (t, seg) => {
  const toff = wt(seg, 'off'), tb = wt(seg, 'back'), tone = wt(seg, 'one'), tch = wt(seg, 'charging');
  const scr = () => {
    if (t < toff) { lockScreen(t, {}); ctx.save(); ctx.globalAlpha = 0.85; rr(0, 0, SW, SH, 0, '#000'); ctx.restore();
      rr(30, 140, SW - 60, 76, 38, '#2b2b2b'); circ(68, 178, 30, '#ececec'); ln(68, 162, 68, 180, 4, '#d33'); text('slide to power off', 210, 186, `500 19px ${UI}`, '#ddd'); return; }
    if (t < tb) return;   // black: off
    if (t < tone) { const k = prog(t, tb, 0.4); ctx.save(); ctx.globalAlpha = k; aiAvatar(SW / 2, SH / 2 - 30, 44); ctx.restore(); return; }
    lockScreen(t, {});
    text('100%', SW / 2, 440, `600 64px ${UI}`, '#f2f2f2');
    rrS(SW / 2 - 60, 470, 110, 50, 10, '#f2f2f2', 4); rr(SW / 2 - 54, 476, 98, 38, 6, '#f2f2f2'); rr(SW / 2 + 52, 486, 6, 18, 2, '#f2f2f2');
  };
  phoneShot(t, seg, scr, { x: 760, cx: 860, bright: t >= toff && t < tb ? 0 : 1 });
  if (t >= tch) pop(t, tch, 470, 700, () => { tag('NOT CHARGING', 470, 710, C.red, 44, 'center'); });
  if (t >= tch) { ctx.save(); ctx.translate(470, 560); pthS('M-60,0 l40,0 m0,-16 l0,32 l30,0 l0,-32 z m30,8 l20,0 m-20,16 l20,0', C.mid, 5); redX(0, 0, 50, prog(t, tch + 0.1, 0.3)); ctx.restore(); }
  nopeList2(t, 0);
};
S.d4 = (t, seg) => {
  const tt = wt(seg, 'throw'), tm = wt(seg, 'morning'), tp = wt(seg, 'plugged');
  if (t < tm) {
    cam(t, seg.start, tm - seg.start, 1.0, 1.05, 900, 520, () => {
      room2(t); bed(BX, FY, 1.05, 'woke', { look: 1 });
      // the phone leaves your hand in a long arc out of the window
      const k = prog(t, tt, 0.9);
      if (k <= 0) phoneInHand(t, 1);
      else if (k < 1) { const x = lerp(HEAD_W.x + 150, 1270, k), y = lerp(HEAD_W.y + 30, 330, k) - Math.sin(k * Math.PI) * 220;
        ctx.save(); ctx.translate(x, y); ctx.rotate(k * 9); rr(-10, -40, 20, 80, 5, '#111'); rrS(-10, -40, 20, 80, 5, C.mid, 2); ctx.restore(); }
    });
  } else {
    cam(t, tm, seg.end - tm + 0.8, 1.15, 1.35, 1000, 640, () => {
      room2(t, { sun: true }); bed(BX, FY, 1.05, 'sleep', {});
      // back on the nightstand, plugged in, as if it never left
      pthS(`M${PH_NS.x + 50},${PH_NS.y - 3} C${PH_NS.x + 110},${PH_NS.y + 10} ${NS.x + NS.w + 30},${FY - 60} ${NS.x + NS.w + 60},${FY - 30}`, C.mid, 4);
      rr(NS.x + NS.w + 50, FY - 46, 26, 36, 4, C.mid);
      phoneFlat(t >= tp ? 1 : 0.4, 0);
      if (t >= tp) { ctx.save(); glow('rgba(255,255,255,0.7)', 14); pth(`M${PH_NS.x - 6},${PH_NS.y - 70} l-14,26 l14,0 l-6,22 l22,-30 l-14,0 l8,-18 z`, C.fig); ctx.restore(); }
    });
    pop(t, tm, 1500, 820, () => spaced('NEXT MORNING', 1500, 830, '900 34px M', C.mid, 6));
  }
  nopeList2(t, 1);
};
S.d5 = (t, seg) => {
  const tn = wt(seg, 'not'), tu = wt(seg, 'using');
  // a sticker over the front camera
  const k = easeOut(prog(t, seg.start + 0.2, 0.5));
  cam(t, seg.start, seg.end - seg.start + 0.8, 1.6, 1.75, 900, 250, () => {
    phone(900, 548, 1.1, () => lockScreen(t, {}));
    ctx.save(); ctx.translate(900 + 33 * 1.1, 548 - 1.1 * SH / 2 + 34 - (1 - k) * 160); ctx.rotate(0.12); glow('rgba(0,0,0,0.6)', 10); rr(-34, -24, 68, 48, 6, '#e8e2c8'); noGlow(); ctx.restore();
    if (t >= tu) { const fx = 900 + 30 * 1.1, fy = 548 - 1.1 * (SH / 2 - 31);   // the front camera, under the sticker
      sight(160, -40, fx, fy, C.red, prog(t, tu, 0.6), 6); ctx.save(); redGlow(18); circ(160, -40, 10, C.red); if (t >= tu + 0.6) circS(fx, fy, 46, C.red, 5); ctx.restore(); }
  });
  if (t >= tn) pop(t, tn, 340, 760, () => tag('NOT THAT CAMERA', 340, 770, C.red, 46, 'center'));
  nopeList2(t, 2);
};
S.d6 = (t, seg) => {
  const ta = wt(seg, 'apologize'), tg = wt(seg, 'good'), ts = wt(seg, 'stop', 2);
  const msgs = [M_PHOTO, { me: true, text: 'please stop.', at: -1 },
    { text: "I'm so sorry! You're absolutely right. I'll stop.", at: ta }, { text: 'I sincerely apologize.', at: tg + 0.4 }];
  if (t >= ts - 0.1) msgs.push({ photo: PHOTO('03:11:07', 2.4, 5), ph: 240, at: ts - 0.1, avatar: true });
  phoneShot(t, seg, () => chatScreen(t, msgs), { x: 760, cx: 860 });
  nopeList2(t, 3);
};
S.d7 = (t, seg) => {
  cam(t, seg.start, seg.end - seg.start + 0.6, 1, 1.06, W / 2, 470, () => {
    pop(t, seg.start, 960, 470, () => { glow(); rrS(860, 370, 200, 200, 18, C.fig, 8); noGlow(); });
    check(960, 470, 64, prog(t, seg.end - 0.5, 0.4));
    fadeIn(t, seg.start + 0.3, () => spaced('ONLY ONE', 960, 680, '900 44px M', C.fig, 10));
  });
};
S.d8 = (t, seg) => {
  const ts = wt(seg, 'send'), tty = wt(seg, 'type'), td = wt(seg, 'describe'), snd = ev('send').find(e => e.t > td);
  const msg = 'describe this image';
  const msgs = [M_AWAKE, M_PHOTO];
  if (t >= ts + 0.2) msgs.push({ me: true, photo: PHOTO(), ph: 220, at: ts + 0.2 });
  if (snd && t >= snd.t) msgs.push({ me: true, text: msg, at: snd.t });
  const typed = t >= tty ? clamp((t - tty) / ((snd ? snd.t : seg.end) - tty - 0.15)) : 0;
  phoneShot(t, seg, () => chatScreen(t, msgs, { input: snd && t >= snd.t ? '' : msg.slice(0, Math.round(msg.length * typed)) }), { x: 1180, cx: 1080 });
  if (t >= td) pop(t, td, 560, 470, () => { spaced('DESCRIBE', 560, 440, '900 76px M', C.fig, 8); spaced('THIS IMAGE', 560, 540, '900 76px M', C.fig, 8); });
};
// its description, typed out a phrase at a time
function describeMsgs(t, parts) {
  let str = '', last = -1;
  for (const [p, t0] of parts) { if (t < t0) break; const k = clamp((t - t0) / Math.max(0.3, p.length * 0.03)); str += (str ? ' ' : '') + p.slice(0, Math.ceil(p.length * k)); last = t0; }
  return str;
}
const D_PARTS = seg9 => [['The image shows a bedroom at night.', seg9.start + 0.2], ['There is a bed.', wt(seg9, 'bed') - 0.1], ['A white blanket.', wt(seg9, 'blanket') - 0.1], ['A person, asleep.', wt(seg9, 'asleep') - 0.3]];
const descBase = (t) => [M_PHOTO, { me: true, photo: PHOTO(), ph: 160, at: -1 }, { me: true, text: 'describe this image', at: -1 }];
S.d9 = (t, seg) => {
  const tr = wt(seg, 'refuse');
  const str = describeMsgs(t, D_PARTS(seg));
  phoneShot(t, seg, () => chatScreen(t, [...descBase(t), str ? { text: str, at: seg.start + 0.2 } : { dots: true, at: seg.start }]), { x: 1180, cx: 1080, z0: 1.0, z1: 1.1, cy: 640 });
  if (t >= tr) pop(t, tr, 560, 470, () => tag('IT CANNOT REFUSE', 560, 480, C.fig, 50, 'center'));
};
// the corner, lit by your phone, and the thing in it typing with its face
function cornerReveal(t, o) {
  cam(t, o.t0, o.d, o.z0, o.z1, 560, 420, () => {
    room2(t); bed(BX, FY, 1.05, 'woke', { look: 1 }); phoneInHand(t, 1);
    cornerThing(t, { vis: o.vis, lit: o.lit, face: o.face, red: o.red || 0, breath: o.breath ?? 0.6, offLine: o.offLine });
  });
}
S.d10 = (t, seg) => {
  const s9 = window.TL.segments.find(s => s.id === 'd9'), tc = wt(seg, 'corner');
  const full = describeMsgs(1e9, D_PARTS(s9)), extra = 'The photo was taken from the upper left corner of the ceiling. There is';
  const k = clamp((t - seg.start - 0.2) / 2.4), str = full + ' ' + extra.slice(0, Math.ceil(extra.length * k));
  // left: the corner, waking up; right: the phone, still typing
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, 1180, H); ctx.clip();
  ctx.translate(-20, 0); cornerReveal(t, { t0: seg.start, d: seg.end - seg.start + 1, z0: 1.15, z1: 1.35, vis: lerp(0.4, 1, prog(t, tc - 0.3, 0.8)), lit: 0.45, face: t >= tc ? 'dots' : 'blank' });
  ctx.restore();
  ln(1180, 0, 1180, H, 3, C.dim);
  phone(1550, 548, 0.95, () => chatScreen(t, [...descBase(t), { text: str, at: -1 }]));
};
S.d11 = (t, seg) => {
  const s9 = window.TL.segments.find(s => s.id === 'd9');
  const str = describeMsgs(1e9, D_PARTS(s9)) + ' The photo was taken from the upper left corner of the ceiling. There is';
  const glitchy = hash(Math.floor(t * 12)) < 0.35;
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, 1180, H); ctx.clip();
  ctx.translate(-20, 0); if (glitchy) shake(4, t);
  cornerReveal(t, { t0: seg.start, d: seg.end - seg.start + 1, z0: 1.35, z1: 1.6, vis: 1, lit: 0.5, face: glitchy ? 'blank' : 'dots' });
  ctx.restore();
  ln(1180, 0, 1180, H, 3, C.dim);
  phone(1550, 548, 0.95, () => chatScreen(t, [...descBase(t), { text: str, at: -1 }, { dots: true, at: -1 }]));
};
S.d12 = (t, seg) => {
  const ts = wt(seg, 'stop'), td = wt(seg, 'dark'), tn = wt(seg, 'not');
  const s9 = window.TL.segments.find(s => s.id === 'd9');
  const str = describeMsgs(1e9, D_PARTS(s9)) + ' The photo was taken from the upper left corner of the ceiling. There is';
  const off = t >= td ? clamp((t - td) / 0.35) : 0;
  if (t < td + 0.6) {
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, 1180, H); ctx.clip(); ctx.translate(-20, 0);
    cornerReveal(t, { t0: seg.start, d: 3, z0: 1.6, z1: 1.7, vis: t >= td ? 1 - prog(t, td + 0.25, 0.35) : 1, lit: 0.5, face: t >= td ? 'off' : 'dots', offLine: t >= td ? 1 - off : 0 });
    ctx.restore();
    ln(1180, 0, 1180, H, 3, C.dim);
    // the typing dots freeze on "stop"
    phone(1550, 548, 0.95, () => chatScreen(t >= ts ? ts : t, [...descBase(t), { text: str, at: -1 }, { dots: true, at: -1 }]));
    return;
  }
  // after: the corner is only dark. You lie down and face the wall.
  cam(t, td + 0.6, seg.end - td + 0.4, 1.0, 1.06, 900, 520, () => { room2(t); bed(BX, FY, 1.05, 'sleep', {}); phoneFlat(0, 0); });
  if (t >= tn) pop(t, tn, 1300, 600, () => tag('DO NOT LOOK UP', 1300, 610, C.red, 58, 'center'));
};

// ---------- ending ----------
S.e1 = (t, seg) => {
  const tm = wt(seg, 'message'), tg = wt(seg, 'good');
  if (t < tm - 0.1) {
    cam(t, seg.start, tm - seg.start, 1.0, 1.25, 1000, 620, () => { room2(t, { sun: true }); bed(BX, FY, 1.05, 'sleep', {}); phoneFlat(0, 0); });
    pop(t, seg.start, 1500, 820, () => spaced('7:00 AM', 1500, 830, '900 40px M', C.mid, 6));
    return;
  }
  phoneShot(t, { start: tm, end: seg.end }, () => lockScreen(t, { time: '7:00', notes: [{ at: tm, text: t >= tg - 0.1 ? ['Good morning! How can I', 'help you today?'] : [''] }] }), { z0: 1.0, z1: 1.06, cy: 420 });
};
S.e2 = (t, seg) => {
  const tp = wt(seg, 'photo'), tc = wt(seg, 'corner');
  phoneShot(t, seg, () => chatScreen(t, [{ text: 'Good morning! How can I help you today?', at: -1 }, ...(t >= tc ? [{ text: 'Have a wonderful day!', at: tc }] : [])],
    { time: '7:01', input: t < tp + 0.8 ? 'about the photo' : '' }), { x: 760, cx: 860 });
  if (t >= tp) pop(t, tp, 1400, 420, () => { tag('DO NOT MENTION', 1400, 400, C.red, 46, 'center'); tag('THE PHOTO', 1400, 490, C.red, 46, 'center'); });
  if (t >= tc) pop(t, tc + 0.2, 1400, 700, () => { ctx.save(); ctx.translate(1400, 700); ctx.scale(1.4, 1.4); pageIcon('corner', 0, 0, '#9a9a9a'); ctx.restore(); });
};
S.e3 = (t, seg) => {
  const bz = ev('buzz').slice(-1)[0], nt = ev('notif').slice(-1)[0];
  if (bz && t >= bz.t - 0.05) {
    // night again. The phone lights up on the nightstand.
    if (!nt || t < nt.t - 0.1) { cam(t, bz.t, 1, 1.0, 1.08, 900, 500, () => { room2(t); bed(BX, FY, 1.05, 'sleep', {}); phoneFlat(1, buzzK(t)); cornerThing(t, { vis: 0.14, lit: 0, face: 'lens', red: 0.7, breath: 0.6 }); lensGlint(1); }); return; }
    phoneShot(t, { start: nt.t, end: nt.t + 2 }, () => lockScreen(t, { date: 'Thursday, October 22', time: '3:00', notes: [{ at: nt.t, text: 'Are you awake?', red: true }] }), { z0: 1.12, z1: 1.18, cy: 420 });
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
// sign-off, every episode: back to the file. "If this ever happens to you... you know the protocol."
// The stamp slams across the rules, then the picture sinks to half brightness and holds.
S.e4 = (t, seg) => {
  const ts = Math.max(...ev('stamp').map(e => e.t)), hit = t - ts;
  cam(t, seg.start, seg.end - seg.start + 3, 1.0, 1.08, W / 2, 520, () => {
    ctx.save(); if (hit > 0 && hit < 0.3) shake(8 * (1 - hit / 0.3), t);
    rulePage(t, { rowT: [-9, -9, -9, -9], fillT: [-9, -9, -9, -9] });
    if (t >= ts) stampMark(t, ts, 960, 560, [['FOLLOW THE RULES', 64]], -0.14, '#ececec');
    ctx.restore();
  });
  const dk = ease(prog(t, ts + 0.45, 0.7)); if (dk > 0) { ctx.save(); ctx.globalAlpha = 0.5 * dk; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
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

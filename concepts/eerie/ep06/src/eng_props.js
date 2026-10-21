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

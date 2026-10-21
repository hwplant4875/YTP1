// ---------- EP07 props: the interview room ----------
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

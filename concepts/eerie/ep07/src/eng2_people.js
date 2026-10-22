// ---------- EP07 v4: the three interviewers, minimal vector ----------
// Channel identity: analog horror. PURE BLACK background, PURE WHITE flat characters with thin black detail lines. Red only for danger.
// Heads are perfect white circles with only eyes. The uncanny is in proportion, never texture:
//   'young' long thin neck, small head, eyes too close together (the handshake one, clipboard)
//   'hr'    big head, huge black eyes that turn red (the one in the middle who asks the question)
//   'boss'  no neck, head sunk into the shoulders, both eyes half shut under flat lids (the silent one behind the laptop)
const PP = { fig: '#f4f4f4', line: '#000', eye: '#000' };
const PK = { young: { R: 56, neck: 74, nw: 26 }, hr: { R: 78, neck: 26, nw: 40 }, boss: { R: 66, neck: 0, nw: 0 } };
const ppHeadY = k => -222 - PK[k].neck - PK[k].R * 0.9;

// a head centred at (0,0), its neck hanging below. o.eyes 0..1 red; o.look -1..1 sideways
function ppHead(kind, o = {}) {
  const K = PK[kind], R = K.R, F = PP.fig, L = PP.line;
  if (K.neck) rr(-K.nw / 2, R * 0.6, K.nw, K.neck + R * 0.32, 4, F);
  glow('rgba(255,255,255,0.35)', 24); circ(0, 0, R, F); noGlow();
  const re = o.eyes || 0, lk = (o.look || 0) * R * 0.06;
  const eyeCol = re > 0 ? C.red : PP.eye;
  const E = kind === 'young' ? { dx: 0.2, y: 0.02, rx: 0.12, ry: 0.19 } : kind === 'hr' ? { dx: 0.36, y: 0.0, rx: 0.2, ry: 0.27 } : { dx: 0.36, y: 0.04, rx: 0.15, ry: 0.15 };
  for (const d of [-1, 1]) {
    const ex = d * R * E.dx + lk, ey = R * E.y, rx = R * E.rx, ry = R * E.ry;
    ctx.save(); if (re > 0) { ctx.globalAlpha *= 0.5 + 0.5 * re; redGlow(26); }
    if (kind === 'boss') {   // heavy lids: black half-discs under flat lids, a dead stare
      ctx.beginPath(); ctx.ellipse(ex, ey, rx, ry, 0, 0, Math.PI); ctx.closePath(); ctx.fillStyle = eyeCol; ctx.fill(); noGlow(); ln(ex - rx - 6, ey, ex + rx + 6, ey, 4, L);
    } else ell(ex, ey, rx, ry, 0, eyeCol);
    ctx.restore();
    if (kind === 'hr' && re < 0.5) circ(ex - rx * 0.3, ey - ry * 0.35, R * 0.035, '#fff');   // a pinpoint of light in the black
  }
}

// an interviewer, waist at (x,y) (the desk top). Flat white suit, black lines.
// o.arms: 'desk' (long fingers flat on the desk), 'board' (clipboard), 'write' (+ pen, o.wt), 'laptop' (o.lid 1 open -> 0 shut), 'hand' (reaching to shake, o.reach), 'down'
// o.eyes, o.look, o.lean 0..1, o.tilt, o.sink, o.shake, o.fold 0..1, o.dim 0..1, o.stand (draw legs; (x,y) = feet), o.tieRed
function person(kind, x, y, s = 1, o = {}) {
  const F = PP.fig, L = PP.line, lean = o.lean || 0;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (o.stand) {
    glow('rgba(255,255,255,0.28)', 18);
    for (const d of [-1, 1]) pth(`M${d * 8},-300 L${d * 70},-300 L${d * 58},-24 L${d * 14},-24 Z`, F);
    noGlow(); ln(0, -300, 0, -40, 3, L);
    rr(10, -26, 54, 26, 10, '#1c1c1f'); rr(-64, -26, 54, 26, 10, '#1c1c1f');
    ctx.translate(0, -300);
  }
  if (o.shake) ctx.translate(Math.sin((o.t || 0) * 83) * o.shake, Math.cos((o.t || 0) * 71) * o.shake * 0.5);
  const fold = o.fold || 0;
  if (fold > 0) { ctx.translate(0, -240); ctx.scale(1, 1 - 0.96 * ease(fold)); ctx.translate(0, 240); }
  if (o.dim) ctx.globalAlpha *= 1 - 0.6 * o.dim;
  if (o.sink) ctx.translate(0, o.sink);
  ctx.translate(0, lean * 18);
  // jacket
  const J = kind === 'boss' ? 'M-132,-196 C-142,-190 -146,-170 -144,-140 L-130,10 L130,10 L144,-140 C146,-170 142,-190 132,-196 C90,-214 -90,-214 -132,-196 Z'
                            : 'M-116,-206 C-126,-200 -132,-178 -130,-150 L-120,10 L120,10 L130,-150 C132,-178 126,-200 116,-206 C80,-226 -80,-226 -116,-206 Z';
  glow('rgba(255,255,255,0.28)', 20); pth(J, F); noGlow();
  // shirt, collar, tie (black); the hr one has a plain black blouse and a lanyard
  if (kind === 'hr') { pth('M-40,-220 C-28,-176 28,-176 40,-220 Z', '#000'); pthS('M-24,-208 C-18,-150 -10,-110 -2,-92 M24,-208 C22,-150 26,-110 32,-92', L, 3); rr(-6, -96, 52, 66, 5, F); rrS(-6, -96, 52, 66, 5, L, 3); rr(4, -84, 32, 26, 3, L); ln(4, -46, 36, -46, 3, L); }
  else {
    const top = kind === 'boss' ? -212 : -222;
    pthS(`M-32,${top} L0,-108 L32,${top}`, L, 3);
    pthS(`M-32,${top} L-12,${top + 24} L-4,${top + 4} M32,${top} L12,${top + 24} L4,${top + 4}`, L, 3);
    pth(`M-8,${top + 6} L8,${top + 6} L6,${top + 24} L-6,${top + 24} Z`, L);
    const tl = kind === 'young' ? 128 : 96;
    pth(`M-6,${top + 24} L6,${top + 24} L11,${top + 24 + tl} L0,${top + 36 + tl} L-11,${top + 24 + tl} Z`, o.tieRed ? C.red : L);
  }
  // lapels, button line, buttons
  pthS('M-32,-220 L-58,-168 L-44,-158 L-62,-144 L-4,-60 M32,-220 L58,-168 L44,-158 L62,-144 L4,-60', L, 3.5);
  ln(0, -60, 0, 10, 3, L); circ(-7, -36, 4.5, L); circ(-7, -8, 4.5, L);
  // arms and hands: plain white sleeves, hands with four long thin fingers
  const sleeve = (pts) => { ctx.save(); poly(pts, 44, L); poly(pts, 38, F); ctx.restore(); };
  const hand = (hx, hy, rot = 0, sx = 1, curl = 0.5) => {
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(rot); ctx.scale(sx, 1);
    ell(0, 0, 16, 13, 0, F); ctx.beginPath(); ctx.ellipse(0, 0, 16, 13, 0, 0, Math.PI * 2); ctx.strokeStyle = L; ctx.lineWidth = 2.5; ctx.stroke();
    for (let i = 0; i < 4; i++) { const y0 = -8 + i * 5.5, pts = [[12, y0], [40, y0 + 2], [64, y0 + 10 * curl + i * 1.5]]; poly(pts, 7, L); poly(pts, 3.6, F); }
    ctx.restore(); };
  const A = o.arms || 'desk', sh = kind === 'boss' ? 132 : 118, sy = kind === 'boss' ? -186 : -198;
  if (A === 'desk') { sleeve([[-sh, sy], [-sh - 24, -70], [-70, -12]]); sleeve([[sh, sy], [sh + 24, -70], [70, -12]]); hand(-52, -8, 0.1, 1); hand(52, -8, -0.1, -1); }
  else if (A === 'down') { sleeve([[-sh, sy], [-sh - 18, -60], [-sh - 12, 14]]); sleeve([[sh, sy], [sh + 18, -60], [sh + 12, 14]]); hand(-sh - 12, 34, 1.55, 1, 0.2); hand(sh + 12, 34, 1.55, -1, 0.2); }
  else if (A === 'hand') { sleeve([[-sh, sy], [-sh - 24, -70], [-70, -12]]); hand(-52, -8, 0.1, 1); const r = o.reach ?? 1; sleeve([[sh, sy], [sh + 26, -90], [sh + 26 + 110 * r, -60 - 30 * r]]); hand(sh + 50 + 110 * r, -60 - 30 * r, -0.2, 1, 0.15); }
  else if (A === 'laptop') { sleeve([[-sh, sy], [-sh - 26, -70], [-70, -20]]); sleeve([[sh, sy], [sh + 26, -70], [70, -20]]); }
  else {
    sleeve([[-sh, sy], [-sh - 22, -90], [-84, -84]]);
    const wt = o.wt || 0, px = 24 + Math.sin(wt * 9) * 22 + ((wt * 40) % 40), py = -130 + Math.floor((wt * 1.2) % 3) * 22;
    clipboard(-6, -120, 1.05, -0.06, { lines: o.lines, under: o.under, up: o.up });
    hand(-70, -84, 0, 1, 0.6);
    if (A === 'write') { sleeve([[sh, sy], [sh + 26, -90], [px + 34, py + 34]]); pen(px, py, 0.8, -0.5); hand(px + 22, py + 26, 0.3, -1, 0.6); }
    else { sleeve([[sh, sy], [sh + 22, -90], [84, -84]]); hand(70, -84, 0, -1, 0.6); }
  }
  // head
  ctx.save(); ctx.translate(0, ppHeadY(kind) + lean * 34); ctx.rotate(-lean * 0.06 + (o.tilt || 0)); ppHead(kind, o); ctx.restore();
  // the laptop: a white lid seen from behind, in front of everything
  if (A === 'laptop') {
    const lid = o.lid ?? 1, hh = 320 * lid;
    rr(-150, -12, 300, 14, 4, F); ln(-150, 2, 150, 2, 2, L);
    if (hh > 4) { glow('rgba(255,255,255,0.25)', 16); rr(-140, -12 - hh, 280, hh, 10, F); noGlow(); rrS(-140, -12 - hh, 280, hh, 10, L, 3); circ(0, -12 - hh / 2, 12 * lid, '#000'); }
    if (lid < 0.98) { hand(-84, -16, 0, 1, 0.2); hand(84, -16, 0, -1, 0.2); }
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

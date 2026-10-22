// ---------- EP07 v3: the three interviewers ----------
// Round bald heads with only eyes (sunken sockets, pinprick pupils, no nose, no mouth, no hair). Sickly mottled skin, lit from
// the upper left. Suits that are worn, stained, wrinkled and torn: they have been wearing them for years. Red only for danger.
// kinds: 'young' (tall, long thin neck, stitched head, beige-grey suit, clipboard: the handshake one)
//        'hr'    (big head, cracked, eyes too wide, black blazer, lanyard: the one in the middle who asks the question)
//        'boss'  (dented head, one eye half shut, charcoal three-piece: the silent one behind the laptop)
const PP = {
  skin: '#d6d2cb', skinHi: '#ece9e3', skinSh: '#8c8780', skinDeep: '#57524d', line: '#0d0d0f',
  young: { R: 62, neck: 78, nw: 28, jacket: '#a6a59e', jacketSh: '#6c6b65', edge: '#0d0d0f', shirt: '#c6c2b7', tie: '#19191b' },
  hr: { R: 76, neck: 38, nw: 40, jacket: '#26262b', jacketSh: '#121215', edge: '#5e5e65', shirt: '#bcb8af', tie: null },
  boss: { R: 68, neck: 30, nw: 46, jacket: '#47464c', jacketSh: '#29292e', edge: '#7d7c83', shirt: '#c2bfb6', tie: '#5e5e64', vest: '#36353b' },
};
const ppHeadY = k => -222 - PP[k].neck - PP[k].R * 0.82;

// a head centred at (0,0); the neck hangs below it. o.eyes 0..1 red pupils; o.look -1..1
function ppHead(kind, o = {}) {
  const P = PP[kind], R = P.R, L = PP.line;
  // neck: thin, with tendons
  const nTop = R * 0.6, nBot = R * 0.82 + P.neck + 2, w = P.nw / 2;
  pth(`M${-w},${nTop} L${w},${nTop} L${w + 4},${nBot} L${-w - 4},${nBot} Z`, PP.skinSh);
  ctx.save(); ctx.globalAlpha *= 0.5; ln(-w * 0.4, nTop + 10, -w * 0.7, nBot - 6, 3, PP.skinDeep); ln(w * 0.4, nTop + 10, w * 0.7, nBot - 6, 3, PP.skinDeep); ctx.restore();
  ctx.save(); ctx.globalAlpha *= 0.6; ell(0, R * 0.86, w + 6, 10, 0, PP.skinDeep); ctx.restore();
  // the skull: a ball, mottled, lit from the upper left
  const g = ctx.createRadialGradient(-R * 0.35, -R * 0.4, R * 0.1, 0, 0, R * 1.05); g.addColorStop(0, PP.skinHi); g.addColorStop(0.55, PP.skin); g.addColorStop(1, PP.skinSh);
  glow('rgba(0,0,0,0.7)', 26); circ(0, 0, R, g); noGlow();
  ctx.save(); ctx.beginPath(); ctx.arc(0, 0, R, 0, Math.PI * 2); ctx.clip(); ctx.filter = 'blur(6px)';
  for (const [x, y, r, a] of [[-0.5, 0.35, 0.18, 0.25], [0.45, -0.5, 0.14, 0.2], [0.2, 0.55, 0.22, 0.22], [-0.2, -0.7, 0.12, 0.18], [0.65, 0.2, 0.16, 0.25]])
    ell(x * R, y * R, r * R, r * R * 0.8, 0, `rgba(110,100,92,${a})`);
  ell(R * 0.15, R * 1.1, R * 0.95, R * 0.32, 0, 'rgba(60,55,50,0.3)');
  ctx.filter = 'none';
  if (kind === 'young') {   // a stitched seam over the top of the skull
    pthS(`M${-R * 0.95},${-R * 0.1} C${-R * 0.6},${-R * 0.95} ${R * 0.4},${-R * 1.0} ${R * 0.9},${-R * 0.45}`, PP.skinDeep, 3);
    for (let i = 1; i < 12; i++) { const t = i / 12, x = (1 - t) ** 3 * -0.95 + 3 * (1 - t) ** 2 * t * -0.6 + 3 * (1 - t) * t * t * 0.4 + t ** 3 * 0.9, y = (1 - t) ** 3 * -0.1 + 3 * (1 - t) ** 2 * t * -0.95 + 3 * (1 - t) * t * t * -1.0 + t ** 3 * -0.45;
      ln(x * R - 5, y * R - 6, x * R + 5, y * R + 6, 2.5, L); }
  } else if (kind === 'hr') {   // hairline cracks running down from the crown
    pthS(`M${R * 0.15},${-R} L${R * 0.1},${-R * 0.78} L${R * 0.22},${-R * 0.62} L${R * 0.12},${-R * 0.44} M${R * 0.22},${-R * 0.62} L${R * 0.4},${-R * 0.55} M${-R * 0.5},${-R * 0.9} L${-R * 0.42},${-R * 0.72} L${-R * 0.5},${-R * 0.6}`, PP.skinDeep, 2.5);
  } else {   // a dent in the side of the skull, with veins
    ctx.filter = 'blur(5px)'; ell(R * 0.62, -R * 0.42, R * 0.26, R * 0.2, -0.5, 'rgba(70,64,58,0.6)'); ctx.filter = 'none';
    pthS(`M${R * 0.45},${-R * 0.3} q${-R * 0.15},${R * 0.1} ${-R * 0.12},${R * 0.3} M${R * 0.5},${-R * 0.62} q${-R * 0.2},${-R * 0.06} ${-R * 0.3},${-R * 0.2}`, 'rgba(80,74,68,0.7)', 2);
  }
  ctx.restore();
  ctx.beginPath(); ctx.arc(0, 0, R, 0, Math.PI * 2); ctx.strokeStyle = L; ctx.lineWidth = 3.5; ctx.stroke();
  // eyes: deep sockets, wet whites, pinprick pupils. Each head is off in its own way.
  const re = o.eyes || 0, lk = (o.look || 0) * R * 0.05;
  const eyes = kind === 'young' ? [[-1, 0, 1], [1, 0.07, 1.16]] : kind === 'hr' ? [[-1, 0, 1.12], [1, 0, 1.12]] : [[-1, 0, 1], [1, 0, 1]];
  for (const [d, dy, k] of eyes) {
    const ex = d * R * 0.36, ey = R * (-0.04 + dy), rx = R * 0.2 * k, ry = R * (kind === 'hr' ? 0.19 : 0.14) * k;
    ctx.save(); ctx.filter = 'blur(7px)'; ell(ex, ey + 2, rx * 1.55, ry * 1.9, 0, 'rgba(38,34,31,0.85)'); ctx.filter = 'none'; ctx.restore();
    const sc = `M${ex - rx},${ey} Q${ex},${ey - ry * 1.5} ${ex + rx},${ey} Q${ex},${ey + ry * 1.35} ${ex - rx},${ey} Z`;
    pth(sc, re > 0 ? '#e9d9d6' : '#efece4');
    ctx.save(); ctx.clip(new Path2D(sc));
    ctx.globalAlpha *= 0.5; ctx.filter = 'blur(3px)'; ell(ex, ey - ry * 0.8, rx, ry * 0.5, 0, 'rgba(60,55,50,0.8)'); ctx.filter = 'none'; ctx.globalAlpha /= 0.5;
    if (re > 0) { ctx.globalAlpha *= re; for (let i = 0; i < 4; i++) { const a = i / 4 * Math.PI * 2 + 0.4; ln(ex + Math.cos(a) * rx, ey + Math.sin(a) * ry, ex + Math.cos(a) * rx * 0.4, ey + Math.sin(a) * ry * 0.4, 1.5, '#b33'); } ctx.globalAlpha /= re; }
    // boss: the left lid hangs half shut
    if (kind === 'boss' && d < 0) pth(`M${ex - rx - 2},${ey + 1} Q${ex},${ey - ry * 0.2} ${ex + rx + 2},${ey + 1} L${ex + rx + 2},${ey - ry * 2} L${ex - rx - 2},${ey - ry * 2} Z`, '#9d978f');
    ctx.restore();
    if (kind === 'boss' && d < 0) pthS(`M${ex - rx},${ey + 1} Q${ex},${ey - ry * 0.2} ${ex + rx},${ey + 1}`, L, 3.5);
    const pr = R * 0.042 * (1 + re * 0.5), half = kind === 'boss' && d < 0, py = ey + (half ? ry * 0.45 : 0);
    if (re > 0) { ctx.save(); redGlow(20); circ(ex + lk, py, pr, C.red); noGlow(); ctx.restore(); } else circ(ex + lk, py, pr, '#050505');
    if (!half) pthS(`M${ex - rx},${ey} Q${ex},${ey - ry * 1.5} ${ex + rx},${ey}`, L, 3.5);
    pthS(`M${ex - rx * 0.8},${ey + ry * 0.9} Q${ex},${ey + ry * 1.5} ${ex + rx * 0.8},${ey + ry * 0.9}`, 'rgba(50,45,40,0.6)', 2);
  }
}

// an interviewer, waist at (x,y) (the desk top), ~500 tall above it at s=1.
// o.arms: 'desk' (long fingers spread on the desk), 'board' (clipboard at the chest), 'write' (+ pen, o.wt), 'laptop' (an open laptop in front, o.lid 1 open -> 0 shut),
//         'hand' (right hand reaching out to shake, o.reach), 'down'
// o.eyes, o.look, o.lean 0..1, o.tilt (rad), o.sink (px, slides down behind the laptop), o.shake, o.fold 0..1, o.dim 0..1, o.stand (draw legs; (x,y) = feet)
function person(kind, x, y, s = 1, o = {}) {
  const P = PP[kind], L = PP.line, lean = o.lean || 0;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (o.stand) {
    for (const d of [-1, 1]) { const g = `M${d * 8},-300 L${d * 70},-300 L${d * 60},-20 L${d * 14},-20 Z`; pth(g, P.jacketSh); pthS(g, P.edge, 2.5);
      ctx.save(); ctx.globalAlpha *= 0.4; pthS(`M${d * 22},-200 q${d * 14},10 ${d * 30},0 M${d * 24},-110 q${d * 14},8 ${d * 28},-2`, '#000', 2.5); ctx.restore(); }
    rr(10, -24, 58, 24, 8, '#0c0c0e'); rr(-68, -24, 58, 24, 8, '#0c0c0e'); rrS(10, -24, 58, 24, 8, '#55555b', 2); rrS(-68, -24, 58, 24, 8, '#55555b', 2);
    ctx.translate(0, -300);
  }
  if (o.shake) ctx.translate(Math.sin((o.t || 0) * 83) * o.shake, Math.cos((o.t || 0) * 71) * o.shake * 0.5);
  const fold = o.fold || 0;
  if (fold > 0) { ctx.translate(0, -240); ctx.scale(1, 1 - 0.96 * ease(fold)); ctx.translate(0, 240); }
  if (o.dim) ctx.globalAlpha *= 1 - 0.6 * o.dim;
  if (o.sink) ctx.translate(0, o.sink);
  ctx.translate(0, lean * 18);
  // jacket: slumped, one shoulder lower, worn
  const J = 'M-124,-214 C-136,-206 -140,-180 -138,-150 L-126,10 L126,10 L134,-146 C136,-170 130,-192 120,-198 C84,-224 -84,-232 -124,-214 Z';
  glow('rgba(0,0,0,0.6)', 30); pth(J, P.jacket); noGlow();
  ctx.save(); ctx.clip(new Path2D(J)); ctx.filter = 'blur(14px)'; ell(110, -80, 50, 170, 0, P.jacketSh);
  ctx.filter = 'blur(5px)'; for (const [sx, sy, r] of [[-70, -40, 26], [80, -130, 18], [30, 0, 22], [-96, -150, 14]]) ell(sx, sy, r, r * 0.8, 0.4, 'rgba(0,0,0,0.32)');
  ctx.filter = 'none'; ctx.globalAlpha *= 0.55;
  pthS('M-110,-120 q30,22 56,8 M-120,-60 q36,14 60,-8 M70,-70 q22,-14 50,6 M60,-20 q30,6 56,-10 M-100,-10 q20,-12 44,2', P.jacketSh === '#121215' ? '#3a3a40' : '#000', 3);
  ctx.restore();
  pthS(J, P.edge, 3);
  // stitches along the right shoulder seam, a torn hole under the left lapel
  for (let i = 0; i < 6; i++) { const sx = 72 + i * 9, sy = -212 + i * 3; ln(sx - 4, sy - 5, sx + 4, sy + 5, 2.2, kind === 'hr' ? '#8a8a90' : L); ln(sx + 4, sy - 5, sx - 4, sy + 5, 2.2, kind === 'hr' ? '#8a8a90' : L); }
  pth('M-92,-92 L-80,-104 L-72,-94 L-60,-102 L-56,-84 L-66,-72 L-80,-76 L-90,-70 Z', '#070708'); pthS('M-92,-92 L-80,-104 L-72,-94 L-60,-102 L-56,-84 L-66,-72 L-80,-76 L-90,-70 Z', P.edge, 2);
  ln(-74, -72, -70, -58, 1.5, P.edge); ln(-62, -76, -56, -64, 1.5, P.edge);
  // shirt / blouse (yellowed, a stain at the collar), the tie (too long, crooked, frayed)
  if (kind === 'hr') {
    pth('M-44,-222 C-30,-172 30,-172 44,-222 Z', P.shirt); pthS('M-44,-222 C-30,-172 30,-172 44,-222', L, 2.5);
    ctx.save(); ctx.filter = 'blur(3px)'; ell(14, -200, 12, 8, 0, 'rgba(70,60,50,0.5)'); ctx.filter = 'none'; ctx.restore();
  } else {
    pth('M-34,-224 L34,-224 L0,-108 Z', P.shirt); pthS('M-34,-224 L34,-224 L0,-108 Z', L, 2.5);
    ctx.save(); ctx.filter = 'blur(3px)'; ell(-14, -206, 12, 7, 0, 'rgba(70,60,50,0.5)'); ctx.filter = 'none'; ctx.restore();
    if (kind === 'boss') { pth('M-30,-200 L30,-200 L46,-40 L0,-20 L-46,-40 Z', P.vest); pthS('M-30,-200 L-46,-40 L0,-20 L46,-40 L30,-200', P.edge, 2); circ(0, -150, 3.5, '#77777e'); circ(0, -120, 5, '#8a8a90'); ln(0, -90, 4, -74, 1.5, '#8a8a90'); circ(5, -72, 3, '#77777e'); circ(0, -60, 3.5, '#77777e'); }
    pth('M-34,-224 L-8,-224 L-16,-198 Z', '#d6d2c8'); pth('M34,-224 L8,-224 L22,-236 Z', '#d6d2c8'); pthS('M-34,-224 L-16,-198 L-5,-221 M34,-224 L22,-236 L5,-221', L, 2.5);
    ctx.save(); ctx.translate(0, -212); ctx.rotate(0.12);
    pth('M-9,-6 L9,-6 L7,12 L-7,12 Z', P.tie);
    const tieLen = kind === 'young' ? 220 : 150;
    const tie = `M-6,12 L6,12 L12,${tieLen - 10} L8,${tieLen} L4,${tieLen - 8} L0,${tieLen + 2} L-4,${tieLen - 8} L-8,${tieLen} L-12,${tieLen - 10} Z`;
    pth(tie, P.tie);
    if (kind === 'boss') { ctx.save(); ctx.clip(new Path2D(tie)); for (let i = 0; i < 14; i++) ln(-14, i * 12, 14, 12 + i * 12, 3, '#48484e'); ctx.restore(); }
    ctx.save(); ctx.globalAlpha *= 0.6; ctx.filter = 'blur(2px)'; ell(2, tieLen * 0.6, 7, 10, 0, 'rgba(0,0,0,0.6)'); ctx.filter = 'none'; ctx.restore();
    ctx.restore();
  }
  // lapels, mismatched buttons (one missing, a thread hanging)
  pthS('M-34,-224 L-62,-170 L-48,-160 L-66,-146 L-4,-60 M34,-224 L62,-168 L48,-158 L66,-144 L4,-60', P.edge, 4);
  ln(0, -60, 0, 10, 3, P.edge); circ(-7, -36, 6.5, P.edge); circ(-7, -36, 3, P.jacketSh); ln(-7, -12, -4, 6, 1.5, P.edge); circ(-3, 8, 2.5, P.edge);
  if (kind === 'hr') {   // lanyard and a badge with the name scratched out
    pthS('M-26,-202 C-20,-140 -10,-110 -2,-92 M26,-202 C24,-150 28,-110 34,-92', '#8a8a92', 3); rr(-6, -96, 56, 72, 6, '#d9d6cf'); rr(4, -84, 36, 30, 3, '#7a7a82');
    pthS('M2,-42 l8,-6 l6,8 l8,-8 l6,8 l8,-6', '#222', 3); pthS('M2,-34 l10,-4 l8,6 l10,-6 l10,4', '#222', 2.5);
  }
  // arms: sleeves too short, bony wrists, long thin fingers
  const sleeve = (pts) => { ctx.save(); poly(pts, 46, P.edge); poly(pts, 40, P.jacket); ctx.restore(); };
  const hand = (hx, hy, rot = 0, sx = 1, curl = 1) => {
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(rot); ctx.scale(sx, 1);
    poly([[-30, 0], [-6, 0]], 15, L); poly([[-30, 0], [-6, 0]], 10, PP.skinSh);   // wrist
    const h = 'M-12,-12 C0,-16 14,-14 18,-6 C20,2 18,10 10,14 C0,16 -10,12 -12,4 Z'; pth(h, PP.skin); pthS(h, L, 2.5);
    for (let i = 0; i < 4; i++) { const y0 = -8 + i * 6.5, pts = [[14, y0], [34, y0 + 1], [52, y0 + 6 * curl + i], [62, y0 + 16 * curl + i]];
      poly(pts, 8, L); poly(pts, 4.5, PP.skin); circ(34, y0 + 1, 3, PP.skinSh); circ(52, y0 + 6 * curl + i, 2.6, PP.skinSh); }
    poly([[4, -12], [18, -24], [30, -24]], 8, L); poly([[4, -12], [18, -24], [30, -24]], 4.5, PP.skin);
    ctx.restore(); };
  const A = o.arms || 'desk';
  if (A === 'desk') { sleeve([[-124, -200], [-150, -70], [-76, -12]]); sleeve([[124, -194], [150, -70], [76, -12]]); hand(-52, -6, 0.15, 1, 0.6); hand(52, -6, -0.15, -1, 0.6); }
  else if (A === 'down') { sleeve([[-124, -200], [-142, -60], [-136, 10]]); sleeve([[124, -194], [142, -60], [136, 10]]); hand(-136, 34, 1.5, 1); hand(136, 34, 1.6, -1); }
  else if (A === 'hand') { sleeve([[-124, -200], [-150, -70], [-76, -12]]); hand(-52, -6, 0.15, 1, 0.6); const r = o.reach ?? 1; sleeve([[124, -194], [150, -90], [146 + 110 * r, -60 - 30 * r]]); hand(176 + 110 * r, -60 - 30 * r, -0.2, 1, 0.3); }
  else if (A === 'laptop') { sleeve([[-124, -200], [-150, -70], [-70, -20]]); sleeve([[124, -194], [150, -70], [70, -20]]); }
  else {
    sleeve([[-124, -200], [-146, -90], [-84, -84]]);
    const wt = o.wt || 0, px = 24 + Math.sin(wt * 9) * 22 + ((wt * 40) % 40), py = -130 + Math.floor((wt * 1.2) % 3) * 22;
    clipboard(-6, -120, 1.05, -0.06, { lines: o.lines, under: o.under, up: o.up });
    hand(-66, -84, 0, 1, 0.8);
    if (A === 'write') { sleeve([[124, -194], [150, -90], [px + 34, py + 34]]); pen(px, py, 0.8, -0.5); hand(px + 22, py + 26, 0.3, -1, 0.8); }
    else { sleeve([[124, -194], [146, -90], [84, -84]]); hand(66, -84, 0, -1, 0.8); }
  }
  // head on the neck
  ctx.save(); ctx.translate(0, ppHeadY(kind) + lean * 34); ctx.rotate(-lean * 0.06 + (o.tilt || 0)); ppHead(kind, o); ctx.restore();
  // the laptop goes in front of everything, its lid hiding the face when open
  if (A === 'laptop') {
    const lid = o.lid ?? 1, hh = 320 * lid;
    rr(-150, -14, 300, 18, 4, '#3a3a40'); rrS(-150, -14, 300, 18, 4, '#6a6a70', 2);
    if (hh > 4) { glow('rgba(0,0,0,0.6)', 20); rr(-140, -14 - hh, 280, hh, 10, '#2a2a30'); noGlow(); rrS(-140, -14 - hh, 280, hh, 10, '#6e6e76', 3); circ(0, -14 - hh / 2, 14 * lid, '#4a4a52'); }
    if (lid < 0.98) { hand(-80, -14, 0, 1, 0.4); hand(80, -14, 0, -1, 0.4); }
  }
  ctx.restore();
}


// the new room: a dim grey meeting room under one pendant lamp, window blinds on the right, the clock on the left
function meetRoom(o = {}) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#0c0c0e'); g.addColorStop(0.55, '#1a1a1e'); g.addColorStop(1, '#0a0a0b');
  ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
  const lx = o.lampX ?? 960;
  // the pool of light from the lamp on the back wall
  const r = ctx.createRadialGradient(lx, 330, 20, lx, 420, 760); r.addColorStop(0, 'rgba(235,235,240,0.30)'); r.addColorStop(0.5, 'rgba(200,200,210,0.10)'); r.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = r; ctx.fillRect(-200, -200, W + 400, H + 400);
  // window with blinds
  const wx = o.winX ?? 1500; rr(wx, 170, 330, 420, 6, '#0d0d10'); ctx.save(); ctx.globalAlpha *= 0.85;
  for (let i = 0; i < 16; i++) rr(wx + 12, 184 + i * 25, 306, 15, 2, i % 5 === 3 ? '#4a4a52' : '#5c5c64'); ctx.restore();
  rrS(wx, 170, 330, 420, 6, '#2e2e34', 6); ln(wx + 300, 184, wx + 300, 560, 2, '#2a2a30');
  // a skirting line and the floor
  ln(-200, o.floor ?? 760, W + 200, o.floor ?? 760, 3, '#26262b');
  // clock on the left wall
  const [cx, cy] = o.clockAt || [300, 280];
  ctx.save(); glow('rgba(255,255,255,0.18)', 14); circ(cx, cy, 58, '#e8e8ea'); noGlow(); circS(cx, cy, 58, '#000', 4);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; ln(cx + Math.sin(a) * 46, cy - Math.cos(a) * 46, cx + Math.sin(a) * 52, cy - Math.cos(a) * 52, i % 3 ? 2 : 4, '#000'); }
  const [h, m, s] = o.clock || [9, 0, 0], ah = (h % 12 + m / 60) / 12 * Math.PI * 2, am = m / 60 * Math.PI * 2, as = s / 60 * Math.PI * 2;
  ln(cx, cy, cx + Math.sin(ah) * 28, cy - Math.cos(ah) * 28, 6, '#000'); ln(cx, cy, cx + Math.sin(am) * 40, cy - Math.cos(am) * 40, 4, '#000');
  ln(cx, cy, cx + Math.sin(as) * 46, cy - Math.cos(as) * 46, 2, o.secRed ? C.red : '#000'); circ(cx, cy, 5, '#000'); ctx.restore();
  // the pendant lamp
  ln(lx, -10, lx, 120, 3, '#3a3a40'); pth(`M${lx - 90},190 L${lx - 40},120 L${lx + 40},120 L${lx + 90},190 Z`, '#2a2a30'); pthS(`M${lx - 90},190 L${lx - 40},120 L${lx + 40},120 L${lx + 90},190 Z`, '#55555c', 3);
  ctx.save(); glow('rgba(255,255,240,0.9)', 40); ell(lx, 192, 84, 8, 0, '#f4f4ea'); noGlow(); ctx.restore();
}
// the long table: dark wood with a lit front edge
function meetDesk(x0, x1, y, o = {}) {
  glow('rgba(0,0,0,0.7)', 30); rr(x0, y, x1 - x0, 26, 6, '#3a3a40'); noGlow();
  const g = ctx.createLinearGradient(0, y, 0, y + 26); g.addColorStop(0, '#77777f'); g.addColorStop(1, '#3a3a40'); ctx.fillStyle = g; ctx.beginPath(); ctx.roundRect(x0, y, x1 - x0, 26, 6); ctx.fill();
  rr(x0 + 30, y + 26, x1 - x0 - 60, 400, 0, '#141417'); ln(x0 + 30, y + 26, x1 - 30, y + 26, 3, '#0a0a0b');
  if (o.items !== false) {
    const n = o.n || 3;
    for (let i = 0; i < n; i++) {
      const cx = lerp(x0, x1, (i + 0.5) / n);
      ctx.save(); ctx.globalAlpha *= 0.9; rrS(cx + 120, y - 62, 32, 62, 4, '#c9c9ce', 3); rr(cx + 123, y - 34, 26, 31, 2, 'rgba(200,220,255,0.16)'); ctx.restore();
      rr(cx - 150, y - 6, 80, 6, 2, '#d8d8dc');   // a sheet of paper on the table
    }
  }
}

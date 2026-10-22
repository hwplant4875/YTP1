// ---------- EP07 v2: the three interviewers, drawn as real people ----------
// Greyscale, lit from the upper left, crisp dark outlines. Faces have eyes, brows and a nose but never a mouth.
// kinds: 'young' (slicked-back undercut, light grey slim suit, clipboard: the handshake one)
//        'hr'    (sharp black bob with blunt bangs, dark blazer, lanyard: the one in the middle who asks the question)
//        'boss'  (grey side part, glasses, charcoal three-piece: the silent one behind the laptop)
const PP = {
  skin: '#e6e2de', skinSh: '#b9b4af', skinDeep: '#8f8a85', line: '#121214', white: '#fbfbfc',
  young: { hair: '#232327', hairHi: '#4c4c54', side: '#3c3c43', jacket: '#bdbdc4', jacketSh: '#93939b', edge: '#121214', shirt: '#f6f6f8', tie: '#141416' },
  hr: { hair: '#0f0f12', hairHi: '#3c3c46', jacket: '#2c2c33', jacketSh: '#1b1b20', edge: '#6a6a72', shirt: '#f2f2f4', tie: null },
  boss: { hair: '#a4a4aa', hairHi: '#d2d2d8', side: '#8a8a90', jacket: '#4a4a52', jacketSh: '#33333a', edge: '#8a8a92', shirt: '#eeeef0', tie: '#7a7a82', vest: '#3a3a41' },
};
const FACE = 'M-56,-20 C-58,-70 -30,-88 0,-88 C30,-88 58,-70 56,-20 C55,6 50,28 36,46 C24,58 12,63 0,63 C-12,63 -24,58 -36,46 C-50,28 -55,6 -56,-20 Z';

// a head, face centre at (0,0) in the current transform, ~165 tall. o.eyes 0..1 red irises; o.look -1..1 irises sideways
function ppHead(kind, o = {}) {
  const P = PP[kind], L = PP.line;
  // hair behind the head (the bob)
  if (kind === 'hr') pth('M-72,-36 C-80,-100 -40,-118 0,-118 C40,-118 80,-100 72,-36 L76,58 C66,72 46,70 34,60 L-34,60 C-46,70 -66,72 -76,58 Z', P.hair);
  // neck, with the jaw's shadow on it
  pth('M-22,30 L22,30 L26,120 L-26,120 Z', PP.skinSh); ctx.save(); ctx.globalAlpha *= 0.55; ell(0, 58, 26, 14, 0, PP.skinDeep); ctx.restore();
  // ears (the bob covers them)
  if (kind !== 'hr') for (const d of [-1, 1]) {
    const e = `M${d * 52},-16 C${d * 68},-24 ${d * 74},-2 ${d * 68},14 C${d * 64},28 ${d * 58},32 ${d * 50},26 Z`;
    pth(e, PP.skin); pthS(e, L, 2.5); pthS(`M${d * 56},-8 C${d * 64},-10 ${d * 66},4 ${d * 60},14`, PP.skinDeep, 2.5);
  }
  // undercut: the shaved sides
  if (kind === 'young') for (const d of [-1, 1]) { ctx.save(); ctx.globalAlpha *= 0.85; pth(`M${d * 56},-22 C${d * 58},-52 ${d * 50},-66 ${d * 40},-72 L${d * 34},-40 C${d * 44},-36 ${d * 52},-30 ${d * 56},-22 Z`, P.side); ctx.restore(); }
  // the face, shaded from the upper left
  const fg = ctx.createLinearGradient(-56, 0, 56, 0); fg.addColorStop(0, '#efebe7'); fg.addColorStop(0.5, PP.skin); fg.addColorStop(1, PP.skinSh);
  pth(FACE, fg);
  ctx.save(); ctx.clip(new Path2D(FACE)); ctx.filter = 'blur(12px)';
  ell(0, 68, 56, 16, 0, 'rgba(150,145,140,0.55)'); ell(-24, 22, 14, 8, 0, 'rgba(255,255,255,0.3)'); ell(10, 30, 12, 8, 0, 'rgba(140,135,130,0.35)');
  ell(-22, 8, 13, 5, 0, 'rgba(150,145,140,0.18)'); ell(22, 8, 13, 5, 0, 'rgba(150,145,140,0.22)');
  ctx.filter = 'none'; ctx.restore();
  pthS(FACE, L, 3);
  // eyes: almond whites, dark irises, a heavy upper lid. Red when o.eyes.
  const re = o.eyes || 0, lk = (o.look || 0) * 4;
  for (const d of [-1, 1]) {
    const ex = d * 22, ey = -4;
    const a = `M${ex - 15},${ey} Q${ex - 2},${ey - 12} ${ex + 15},${ey - 1} Q${ex + 2},${ey + 7} ${ex - 15},${ey} Z`;
    pth(a, PP.white);
    ctx.save(); ctx.clip(new Path2D(a)); circ(ex + lk, ey - 2, 6.5, PP.line);
    if (re > 0) { ctx.globalAlpha *= re; redGlow(18); circ(ex + lk, ey - 2, 6.5, C.red); noGlow(); }
    ctx.restore();
    if (re > 0) { ctx.save(); ctx.globalAlpha *= re; redGlow(24); circ(ex + lk, ey - 2, 3, '#ffb0b0'); noGlow(); ctx.restore(); }
    else circ(ex + lk - 2, ey - 4, 1.8, '#fff');
    pthS(`M${ex - 16},${ey + 1} Q${ex - 2},${ey - 13} ${ex + 16},${ey - 1}`, L, 3.5);
    if (kind === 'hr') pthS(`M${ex + d * 14},${ey - 2} l${d * 6},-5`, L, 2.5);   // lashes
  }
  // brows: stern, angled down to the nose
  const bw = kind === 'boss' ? 6 : kind === 'young' ? 5.5 : 4.5, bc = kind === 'boss' ? '#6e6e74' : P.hair;
  for (const d of [-1, 1]) pthS(`M${d * 38},-26 Q${d * 24},-30 ${d * 9},-21`, bc, bw);
  // nose: a bridge line, the tip and nostrils (no mouth below it, ever)
  pthS('M5,-14 C3,2 12,14 11,22', PP.skinDeep, 2.5); ell(-5, 26, 4, 2.4, 0.2, PP.skinDeep); ell(8, 26, 4, 2.4, -0.2, PP.skinDeep);
  // hair on top
  if (kind === 'young') {
    const h = 'M-56,-26 C-68,-84 -44,-132 4,-136 C52,-138 76,-100 60,-28 C56,-50 46,-64 30,-70 C10,-76 -22,-76 -40,-66 C-50,-58 -54,-44 -56,-26 Z';
    pth(h, P.hair); pthS(h, L, 2.5);
    for (let i = 0; i < 5; i++) pthS(`M${-38 + i * 18},${-70 - i} C${-44 + i * 16},${-104} ${-24 + i * 14},${-126} ${10 + i * 10},${-130 + i * 3}`, P.hairHi, 2.5);
  } else if (kind === 'hr') {
    const bang = 'M-64,-30 C-68,-96 -32,-114 0,-114 C34,-114 68,-96 64,-30 L60,-38 C40,-44 20,-42 0,-40 C-20,-42 -40,-44 -60,-38 Z';
    pth(bang, P.hair);
    for (const d of [-1, 1]) pth(`M${d * 64},-32 L${d * 72},56 C${d * 64},66 ${d * 50},66 ${d * 44},58 L${d * 54},2 C${d * 56},-14 ${d * 58},-26 ${d * 60},-38 Z`, P.hair);
    pthS('M-40,-108 C-20,-100 -6,-80 -4,-42', P.hairHi, 3); pthS('M30,-106 C42,-90 50,-60 50,-40', P.hairHi, 2.5); pthS('M-52,-60 C-58,-20 -60,20 -62,50', P.hairHi, 2.5);
    pthS('M-60,-38 C-40,-44 -20,-42 0,-40 C20,-42 40,-44 60,-38', L, 2);
  } else {
    const h = 'M-57,-22 C-64,-82 -30,-110 4,-110 C44,-110 66,-82 57,-22 C54,-46 46,-60 34,-66 C10,-74 -14,-70 -30,-60 C-44,-52 -52,-40 -57,-22 Z';
    pth(h, P.hair); pthS(h, L, 2.5); for (const d of [-1, 1]) ell(d * 55, -24, 5, 14, 0, P.side);
    pthS('M-28,-62 C-30,-80 -28,-96 -20,-106', '#6a6a70', 3);
    for (let i = 0; i < 4; i++) pthS(`M${-22 + i * 4},${-100 + i * 9} C${0 + i * 4},${-104 + i * 8} ${26 + i * 2},${-96 + i * 8} ${46 - i * 2},${-70 + i * 6}`, P.hairHi, 2.5);
    ctx.save(); ctx.globalAlpha *= 0.35; pthS('M-24,-48 Q0,-52 24,-48 M-18,-40 Q0,-43 18,-40', PP.skinDeep, 2); ctx.restore();
    // glasses
    for (const d of [-1, 1]) { ctx.save(); ctx.globalAlpha *= 0.12; rr(d * 22 - 21, -17, 42, 26, 6, '#cfe0ff'); ctx.restore(); ctx.beginPath(); ctx.roundRect(d * 22 - 21, -17, 42, 26, 6); ctx.strokeStyle = L; ctx.lineWidth = 4; ctx.stroke(); }
    ln(-1, -6, 1, -6, 4, L); ln(-43, -10, -54, -14, 3.5, L); ln(43, -10, 54, -14, 3.5, L);
    ctx.save(); ctx.globalAlpha *= 0.5; ln(-34, -13, -26, -3, 3, '#fff'); ln(10, -13, 18, -3, 3, '#fff'); ctx.restore();
  }
}

// an interviewer, waist at (x,y) (the desk top), ~470 tall above it at s=1.
// o.arms: 'desk' (hands clasped on the desk), 'board' (clipboard at the chest), 'write' (+ pen, o.wt), 'laptop' (an open laptop in front, o.lid 1 open -> 0 shut),
//         'hand' (right hand reaching out to shake), 'down'
// o.eyes, o.look, o.lean 0..1, o.tilt (rad), o.sink (px, slides down behind the laptop), o.shake, o.fold 0..1, o.dim 0..1, o.stand (draw legs; (x,y) = feet)
function person(kind, x, y, s = 1, o = {}) {
  const P = PP[kind], L = PP.line, lean = o.lean || 0;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (o.stand) {
    for (const d of [-1, 1]) { const g = `M${d * 8},-300 L${d * 70},-300 L${d * 58},-24 L${d * 16},-24 Z`; pth(g, kind === 'hr' ? '#24242a' : P.jacketSh); pthS(g, kind === 'hr' ? P.edge : L, 2.5); }
    rr(10, -26, 54, 26, 10, '#0c0c0e'); rr(-64, -26, 54, 26, 10, '#0c0c0e'); rrS(10, -26, 54, 26, 10, '#5a5a60', 2); rrS(-64, -26, 54, 26, 10, '#5a5a60', 2);
    ctx.translate(0, -300);
  }
  if (o.shake) ctx.translate(Math.sin((o.t || 0) * 83) * o.shake, Math.cos((o.t || 0) * 71) * o.shake * 0.5);
  const fold = o.fold || 0;
  if (fold > 0) { ctx.translate(0, -240); ctx.scale(1, 1 - 0.96 * ease(fold)); ctx.translate(0, 240); }
  if (o.dim) ctx.globalAlpha *= 1 - 0.6 * o.dim;
  if (o.sink) ctx.translate(0, o.sink);
  ctx.translate(0, lean * 18);
  // jacket body
  const J = 'M-122,-206 C-132,-200 -138,-178 -136,-150 L-124,10 L124,10 L136,-150 C138,-178 132,-200 122,-206 C84,-228 -84,-228 -122,-206 Z';
  glow('rgba(0,0,0,0.6)', 30); pth(J, P.jacket); noGlow();
  ctx.save(); ctx.clip(new Path2D(J)); ctx.filter = 'blur(14px)'; ell(110, -80, 50, 170, 0, P.jacketSh); ctx.filter = 'none'; ctx.restore();
  pthS(J, P.edge, 3);
  // shirt / blouse, tie, vest
  if (kind === 'hr') {
    pth('M-44,-220 C-30,-170 30,-170 44,-220 Z', P.shirt); pthS('M-44,-220 C-30,-170 30,-170 44,-220', L, 2.5);
    pthS('M-30,-210 C-20,-150 20,-150 30,-210', '#8e8e96', 2); circ(0, -172, 5, '#d8d8de');   // a thin necklace
  } else {
    pth('M-34,-222 L34,-222 L0,-108 Z', P.shirt); pthS('M-34,-222 L34,-222 L0,-108 Z', L, 2.5);
    if (kind === 'boss') { pth('M-30,-200 L30,-200 L46,-40 L0,-20 L-46,-40 Z', P.vest); pthS('M-30,-200 L-46,-40 L0,-20 L46,-40 L30,-200', P.edge, 2); for (let i = 0; i < 4; i++) circ(0, -150 + i * 30, 3.5, '#77777e'); }
    pth('M-34,-222 L-8,-222 L-14,-198 Z', '#e4e4e8'); pth('M34,-222 L8,-222 L14,-198 Z', '#e4e4e8'); pthS('M-34,-222 L-14,-198 L-5,-219 M34,-222 L14,-198 L5,-219', L, 2.5);
    pth('M-9,-216 L9,-216 L7,-198 L-7,-198 Z', P.tie);
    const tie = kind === 'boss' ? 'M-7,-198 L7,-198 L12,-150 L0,-140 L-12,-150 Z' : 'M-6,-198 L6,-198 L10,-118 L0,-106 L-10,-118 Z';
    pth(tie, P.tie);
    if (kind === 'boss') { ctx.save(); ctx.clip(new Path2D(tie)); for (let i = 0; i < 6; i++) ln(-14, -200 + i * 12, 14, -188 + i * 12, 3, '#55555c'); ctx.restore(); }
  }
  // lapels, buttons, pocket square
  pthS('M-34,-222 L-62,-168 L-48,-158 L-66,-144 L-4,-60 M34,-222 L62,-168 L48,-158 L66,-144 L4,-60', P.edge, 4);
  ln(0, -60, 0, 10, 3, P.edge); circ(-7, -36, 4.5, P.edge); circ(-7, -8, 4.5, P.edge);
  if (kind !== 'young') { ln(56, -112, 92, -116, 3, P.edge); pth('M64,-114 L70,-128 L78,-114 Z', '#e8e8ec'); }
  if (kind === 'hr') { pthS('M-26,-200 C-20,-140 -10,-110 -2,-92 M26,-200 C24,-150 28,-110 34,-92', '#9a9aa2', 3); rr(-6, -96, 56, 72, 6, '#e6e6ea'); rr(4, -84, 36, 30, 3, '#9a9aa2'); ln(4, -42, 40, -42, 3, '#9a9aa2'); }
  // arms
  const sleeve = (pts, cuff) => { ctx.save(); poly(pts, 46, P.edge); poly(pts, 40, P.jacket); ctx.restore(); if (cuff) { const [a, b] = pts.slice(-2); const ang = Math.atan2(b[1] - a[1], b[0] - a[0]); ctx.save(); ctx.translate(b[0], b[1]); ctx.rotate(ang); rr(-4, -16, 10, 32, 3, P.shirt); ctx.restore(); } };
  const hand = (hx, hy, rot = 0, sx = 1) => { ctx.save(); ctx.translate(hx, hy); ctx.rotate(rot); ctx.scale(sx, 1);
    const h = 'M-16,-14 C-4,-20 16,-18 24,-10 C30,-4 30,6 24,12 C14,18 -6,18 -16,12 Z'; pth(h, PP.skin); pthS(h, L, 2.5); pthS('M2,-14 C10,-12 16,-6 18,2', PP.skinDeep, 2); ctx.restore(); };
  const A = o.arms || 'desk';
  if (A === 'desk') { sleeve([[-124, -196], [-148, -70], [-40, -4]], 1); sleeve([[124, -196], [148, -70], [40, -4]], 1); hand(-22, -2, 0); hand(18, -8, 0, -1); }
  else if (A === 'down') { sleeve([[-124, -196], [-142, -60], [-136, 30]], 1); sleeve([[124, -196], [142, -60], [136, 30]], 1); hand(-136, 46, 1.5); hand(136, 46, 1.6, -1); }
  else if (A === 'hand') { sleeve([[-124, -196], [-148, -70], [-40, -4]], 1); const r = o.reach ?? 1; sleeve([[124, -196], [150, -90], [150 + 120 * r, -60 - 30 * r]], 1); hand(-22, -2, 0); hand(170 + 120 * r, -60 - 30 * r, -0.2); }
  else if (A === 'laptop') { sleeve([[-124, -196], [-150, -70], [-70, -20]], 1); sleeve([[124, -196], [150, -70], [70, -20]], 1); }
  else {
    sleeve([[-124, -196], [-146, -90], [-70, -84]], 1); hand(-60, -84, 0);
    const wt = o.wt || 0, px = 24 + Math.sin(wt * 9) * 22 + ((wt * 40) % 40), py = -130 + Math.floor((wt * 1.2) % 3) * 22;
    clipboard(-6, -120, 1.05, -0.06, { lines: o.lines, under: o.under, up: o.up });
    if (A === 'write') { sleeve([[124, -196], [150, -90], [px + 24, py + 30]], 1); pen(px, py, 0.8, -0.5); hand(px + 22, py + 26, 0, -1); }
    else { sleeve([[124, -196], [146, -90], [70, -84]], 1); hand(62, -84, 0, -1); }
  }
  // head on the neck
  ctx.save(); ctx.translate(0, -318 + lean * 34); ctx.rotate(-lean * 0.06 + (o.tilt || 0)); ppHead(kind, o); ctx.restore();
  // the laptop goes in front of everything, its lid hiding the face when open
  if (A === 'laptop') {
    const lid = o.lid ?? 1, hh = 300 * lid;
    rr(-150, -14, 300, 18, 4, '#3a3a40'); rrS(-150, -14, 300, 18, 4, '#6a6a70', 2);
    if (hh > 4) { glow('rgba(0,0,0,0.6)', 20); rr(-140, -14 - hh, 280, hh, 10, '#2a2a30'); noGlow(); rrS(-140, -14 - hh, 280, hh, 10, '#6e6e76', 3); circ(0, -14 - hh / 2, 14 * lid, '#4a4a52'); }
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

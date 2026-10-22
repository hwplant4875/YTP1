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
  // a plain round head: no face, no ears, no glasses. Danger: a red glow around it.
  const K = PK[kind], F = PP.fig, re = o.eyes || 0, R = kind === 'boss' ? 66 : 62;
  ctx.save();
  rr(-K.nw / 2, 40, K.nw, K.neck + 30, 6, F);
  if (re > 0) redGlow(40 * re); else glow('rgba(255,255,255,0.35)', 24);
  circ(0, -16, R, F); noGlow();
  if (re > 0) { ctx.save(); ctx.globalAlpha *= re; redGlow(24); circS(0, -16, R + 3, C.red, 5); ctx.restore(); }
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

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

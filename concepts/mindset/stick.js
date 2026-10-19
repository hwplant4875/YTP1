(() => {
// Stick-figure (졸라맨) drafts, 16:9, on the whiteboard frame.
const { h1, curve, brush, circlePts, blobFill, polyFill, ik } = window.Ink;
const { boardBase, boardTray, magnet, sticky, mtext, M, arrow } = window.Board;
const lerp = (a, b, k) => a + (b - a) * k;
const ease = k => k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
const MK = { k: '#17171d', r: '#e0353b', b: '#2457d6', g: '#1f9d55', o: '#ff8a1f' };
const LW = 15;

// ---------- the stick man ----------
function lerpPose(A, B, k) {
  const L = (a, b) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k)];
  return { hip: L(A.hip, B.hip), sh: L(A.sh, B.sh), head: L(A.head, B.head),
    hands: [L(A.hands[0], B.hands[0]), L(A.hands[1], B.hands[1])], feet: [L(A.feet[0], B.feet[0]), L(A.feet[1], B.feet[1])],
    knee: k < 0.5 ? A.knee : B.knee, elbow: k < 0.5 ? A.elbow : B.elbow, expr: k < 0.5 ? A.expr : B.expr, dir: k < 0.5 ? A.dir : B.dir };
}
function stickFace(ctx, cx, cy, R, dir, expr, boil, col = MK.k) {
  const fx = cx + dir * R * 0.22;
  const ex = [fx - R * 0.3, fx + R * 0.3], ey = cy - R * 0.05;
  ex.forEach((x, i) => {
    if (expr === 'sleepy') M(ctx, [[x - R * 0.13, ey], [x + R * 0.13, ey + 1]], col, 700 + i, boil, R * 0.1);
    else if (expr === 'strain') { const k = i ? -1 : 1; M(ctx, [[x - R * 0.12 * k, ey - R * 0.12], [x + R * 0.1 * k, ey], [x - R * 0.12 * k, ey + R * 0.12]], col, 700 + i, boil, R * 0.09); }
    else blobFill(ctx, x, ey, R * (expr === 'shock' ? 0.13 : 0.1), col, 702 + i, boil);
    const inner = i ? -1 : 1, by = ey - R * 0.3;
    const tilt = { det: 0.25, strain: 0.25, shout: 0.22, shock: -0.25, sleepy: -0.05, happy: -0.15 }[expr] ?? 0;
    M(ctx, [[x - inner * R * 0.17, by - R * tilt * 0.4 - (expr === 'shock' ? R * 0.1 : 0)], [x + inner * R * 0.13, by + R * tilt * 0.5 - (expr === 'shock' ? R * 0.1 : 0)]], col, 704 + i, boil, R * 0.1);
  });
  const my = cy + R * 0.42;
  if (expr === 'shock') { M(ctx, circlePts(fx, my, R * 0.13, 710 + boil, 0.2), col, 710, boil, R * 0.08); }
  else if (expr === 'shout') polyFill(ctx, [[fx - R * 0.24, my - R * 0.08], [fx + R * 0.24, my - R * 0.1], [fx + R * 0.12, my + R * 0.24], [fx - R * 0.12, my + R * 0.24]], col, 711, boil, 2);
  else if (expr === 'strain') { M(ctx, [[fx - R * 0.22, my], [fx + R * 0.22, my]], col, 712, boil, R * 0.16); M(ctx, [[fx - R * 0.16, my], [fx + R * 0.16, my]], '#fff', 713, boil, R * 0.05); }
  else if (expr === 'happy') M(ctx, curve([[fx - R * 0.22, my - R * 0.06], [fx, my + R * 0.14], [fx + R * 0.22, my - R * 0.06]], 6), col, 714, boil, R * 0.09);
  else if (expr === 'sleepy') M(ctx, [[fx - R * 0.1, my], [fx + R * 0.1, my + 1]], col, 715, boil, R * 0.08);
  else M(ctx, [[fx - R * 0.2, my + 2], [fx + R * 0.2, my - 2]], col, 716, boil, R * 0.09);
}
// P: hip, sh, head, hands[2], feet[2], knee[2], elbow[2], dir, expr. seg = bone length.
function stick(ctx, P, boil, opt = {}) {
  const seg = opt.seg ?? 120, R = opt.R ?? 54, col = opt.col ?? MK.k, w = opt.w ?? LW;
  const o = { w, color: col, noTaper: true, roundCaps: true, boil, wob: 1.1, pressure: 0.15, alpha: opt.alpha ?? 1 };
  ctx.save(); if (opt.alpha) ctx.globalAlpha = opt.alpha;
  for (let i = 0; i < 2; i++) {
    brush(ctx, ik(P.hip, P.feet[i], seg, seg, P.knee[i]), { ...o, seed: 600 + i });
    brush(ctx, ik(P.sh, P.hands[i], seg * 0.82, seg * 0.78, P.elbow[i]), { ...o, seed: 610 + i });
  }
  brush(ctx, [P.hip, P.sh], { ...o, seed: 620 });
  // neck towards head
  const dx = P.head[0] - P.sh[0], dy = P.head[1] - P.sh[1], d = Math.hypot(dx, dy) || 1;
  brush(ctx, [P.sh, [P.head[0] - dx / d * R, P.head[1] - dy / d * R]], { ...o, seed: 621 });
  blobFill(ctx, P.head[0], P.head[1], R, opt.headFill ?? '#ffffff', 622, boil);
  brush(ctx, circlePts(P.head[0], P.head[1], R, 623 + boil, 0.3), { w: w * 0.85, color: col, seed: 624, boil, wob: 0.8, taper: 20, pressure: 0.3, alpha: opt.alpha ?? 1 });
  if (!opt.noFace) stickFace(ctx, P.head[0], P.head[1], R, P.dir, P.expr, boil, col);
  if (opt.band) { // the one recurring prop: an orange sweatband on the wrist
    const h = P.hands[1]; M(ctx, [[h[0] - 10, h[1] - 22], [h[0] + 10, h[1] - 30]], MK.o, 630, boil, 16);
  }
  ctx.restore();
}
function scribbleGhost(ctx, x, y, r, boil, t) {
  // the excuse: a grey scribble cloud with lazy eyes
  ctx.save(); ctx.globalAlpha = 0.9;
  const pts = []; for (let i = 0; i < 70; i++) { const a = i * 0.6; const rr = r * (0.55 + 0.45 * h1(i, boil % 3)); pts.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr * 0.8]); }
  brush(ctx, curve(pts, 3), { w: 5, color: '#8a8f99', seed: 640, boil, wob: 2, taper: 30 });
  ctx.restore();
  M(ctx, [[x - 26, y - 6], [x - 6, y - 4]], MK.k, 641, boil, 7); M(ctx, [[x + 8, y - 4], [x + 28, y - 6]], MK.k, 642, boil, 7);
  M(ctx, curve([[x - 16, y + 22], [x + 2, y + 30], [x + 22, y + 16]], 5), MK.k, 643, boil, 6);
}
function lines(ctx, cx, cy, n, r0, r1, col, boil, s) {
  for (let i = 0; i < n; i++) { const a = i / n * 6.283 + 0.3; M(ctx, [[cx + Math.cos(a) * r0, cy + Math.sin(a) * r0], [cx + Math.cos(a) * r1, cy + Math.sin(a) * r1]], col, s + i, boil, 6); }
}

// ---------- 10: 5:00 AM, out of bed ----------
const K = {
  A: { hip: [520, 735], sh: [650, 728], head: [728, 722], hands: [[600, 745], [640, 742]], feet: [[330, 742], [350, 736]], knee: [-1, -1], elbow: [1, 1], expr: 'sleepy', dir: 1 },
  A2: { hip: [520, 735], sh: [650, 728], head: [728, 722], hands: [[600, 745], [640, 742]], feet: [[330, 742], [350, 736]], knee: [-1, -1], elbow: [1, 1], expr: 'shock', dir: 1 },
  B: { hip: [880, 560], sh: [1015, 520], head: [1100, 495], hands: [[1170, 460], [1150, 545]], feet: [[750, 545], [735, 610]], knee: [1, 1], elbow: [-1, -1], expr: 'shout', dir: 1 },
  C: { hip: [1160, 785], sh: [1230, 690], head: [1275, 612], hands: [[1310, 770], [1110, 770]], feet: [[1100, 893], [1235, 893]], knee: [-1, -1], elbow: [1, -1], expr: 'det', dir: 1 },
  D: { hip: [1185, 690], sh: [1190, 550], head: [1196, 460], hands: [[1120, 690], [1270, 410]], feet: [[1140, 893], [1230, 893]], knee: [-1, -1], elbow: [1, 1], expr: 'det', dir: 1 },
};
function pose10(t) {
  const seq = [[0, 'A'], [0.5, 'A2'], [0.75, 'A2'], [1.25, 'B'], [1.6, 'C'], [2.0, 'D'], [9, 'D']];
  for (let i = 0; i < seq.length - 1; i++) if (t < seq[i + 1][0]) return lerpPose(K[seq[i][1]], K[seq[i + 1][1]], ease((t - seq[i][0]) / (seq[i + 1][0] - seq[i][0])));
  return K.D;
}
function scene10(ctx, W, H, t) {
  const boil = Math.floor(t * 8), tq = Math.floor(t * 12) / 12;
  boardBase(ctx, W, H, boil);
  mtext(ctx, '5:00 AM.', 110, 160, 78, MK.r, boil, -0.02, 'PMarker', 'left');
  mtext(ctx, 'Feet on the floor', 110, 250, 64, MK.k, boil, -0.02, 'PMarker', 'left');
  mtext(ctx, 'before the excuses wake up.', 110, 325, 52, MK.k, boil + 1, -0.02, 'PMarker', 'left');
  const fy = 900;
  M(ctx, [[150, fy], [1780, fy + 4]], MK.k, 1, boil, 8);
  // bed
  M(ctx, [[230, 760], [770, 760], [770, 820], [230, 820], [230, 756]], MK.k, 2, boil, 9);
  M(ctx, [[230, 680], [230, fy]], MK.k, 3, boil, 10); M(ctx, [[770, 820], [770, fy]], MK.k, 4, boil, 10);
  // the excuse ghost holds the blanket
  const P = pose10(tq);
  const flying = Math.min(1, Math.max(0, (tq - 0.75) / 0.8));
  scribbleGhost(ctx, 330 + flying * -20, 640 - flying * 30, 70, boil, t);
  const bl = flying < 0.05
    ? curve([[300, 712], [420, 700], [560, 706], [690, 716], [760, 750]], 6)
    : curve([[360, 690], [470, 600 - flying * 60], [600, 650 - flying * 120], [700, 610 - flying * 80]], 6);
  polyFill(ctx, [...bl, [bl[bl.length - 1][0], bl[bl.length - 1][1] + 40], [bl[0][0], bl[0][1] + 40]], 'rgba(36,87,214,0.55)', 5, boil, 3);
  M(ctx, bl, MK.b, 6, boil, 8);
  stick(ctx, P, boil, { band: true });
  // alarm clock
  const shake = tq < 1.4 ? Math.sin(tq * 70) * 5 : 0;
  const ax = 880 + shake, ay = 820;
  M(ctx, circlePts(ax, ay, 55, 30 + boil), MK.r, 30, boil, 10);
  mtext(ctx, '5:00', ax, ay + 16, 40, MK.r, boil);
  M(ctx, [[ax - 30, ay + 52], [ax - 44, fy]], MK.k, 31, boil, 8); M(ctx, [[ax + 30, ay + 52], [ax + 44, fy]], MK.k, 32, boil, 8);
  if (tq < 1.4) { lines(ctx, ax, ay, 7, 75, 105, MK.r, boil, 40); mtext(ctx, 'RRRING', ax + 60, ay - 100, 48, MK.r, boil, 0.1); }
  if (tq > 1.5 && tq < 2.0) lines(ctx, 1170, 893, 6, 60, 110, MK.k, boil, 50);
  // motion arc while jumping
  if (tq > 0.7 && tq < 1.7) M(ctx, curve([[640, 700], [820, 520], [1050, 520], [1180, 760]], 8), 'rgba(23,23,29,0.25)', 60, boil, 5);
  magnet(ctx, 1700, 150, MK.r);
  sticky(ctx, 1700, 230, 210, 0.05, '#ffe66b', [['DAY 1', 54]], boil);
  boardTray(ctx, W, H, boil);
}

// ---------- 11: running in the rain ----------
function runPose(x, gy, ph) {
  const seg = 120, bob = Math.abs(Math.cos(ph)) * 10, lean = 0.28;
  const hip = [x, gy - 225 - bob], sh = [hip[0] + Math.sin(lean) * 140, hip[1] - Math.cos(lean) * 140];
  const feet = [0, 1].map(i => {
    const p = ph + i * Math.PI, th = 0.2 + 0.85 * Math.sin(p), s2 = th - (0.25 + 1.35 * Math.max(0, Math.cos(p)));
    const kx = hip[0] + Math.sin(th) * seg, ky = hip[1] + Math.cos(th) * seg;
    return [kx + Math.sin(s2) * seg, Math.min(gy - 6, ky + Math.cos(s2) * seg)];
  });
  const hands = [0, 1].map(i => { const sw = -Math.sin(ph + i * Math.PI); return [sh[0] + 20 + 80 * sw, sh[1] + 95 - 45 * Math.max(0, sw)]; });
  return { hip, sh, head: [sh[0] + 40, sh[1] - 82], hands, feet, knee: [-1, -1], elbow: [1, 1], expr: 'det', dir: 1 };
}
function scene11(ctx, W, H, t) {
  const boil = Math.floor(t * 8), tq = Math.floor(t * 12) / 12;
  boardBase(ctx, W, H, boil);
  const gy = 880;
  // rain
  for (let i = 0; i < 70; i++) {
    const x = 60 + h1(i, 1) * (W - 120), y = 60 + ((h1(i, 2) * 820 + tq * 900) % 820);
    M(ctx, [[x, y], [x - 12, y + 40]], 'rgba(36,87,214,0.55)', 800 + i, boil, 4);
  }
  // cloud
  M(ctx, curve([[1250, 200], [1300, 130], [1400, 140], [1450, 100], [1560, 130], [1620, 200], [1250, 200]], 6), MK.k, 810, boil, 8);
  mtext(ctx, "It's raining.", 110, 170, 72, MK.k, boil, -0.02, 'PMarker', 'left');
  mtext(ctx, 'Good.', 110, 270, 96, MK.r, boil + 1, -0.03, 'PMarker', 'left');
  M(ctx, [[150, gy], [1780, gy + 4]], MK.k, 811, boil, 8);
  // scrolling ground marks + puddle splash
  for (let i = 0; i < 8; i++) { const x = ((i * 240 - t * 700) % 1900 + 1900) % 1900; M(ctx, [[x, gy + 40], [x + 60, gy + 42]], MK.k, 820 + i, boil, 6); }
  const P = runPose(900, gy, tq * 10.5);
  for (let g = 3; g >= 1; g--) stick(ctx, runPose(900 - g * 110, gy, (tq - g * 0.06) * 10.5), boil, { alpha: 0.1 + 0.05 * (3 - g), noFace: true, headFill: 'rgba(255,255,255,0)' });
  stick(ctx, P, boil, { band: true });
  const lowFoot = P.feet[0][1] > P.feet[1][1] ? P.feet[0] : P.feet[1];
  if (lowFoot[1] > gy - 10) lines(ctx, lowFoot[0], gy, 5, 20, 55, MK.b, boil, 830);
  // distance counter on a sticky
  const km = (4.2 + t * 0.05).toFixed(2);
  magnet(ctx, 1690, 330, MK.b);
  sticky(ctx, 1690, 420, 230, -0.04, '#a8e6ff', [['KM', 44], [km, 60, MK.r]], boil);
  arrow(ctx, [[1500, 560], [1300, 600], [1110, 640]], MK.k, 840, boil);
  mtext(ctx, 'still going', 1520, 580, 44, MK.k, boil, 0, 'PMarker', 'left');
  boardTray(ctx, W, H, boil);
}

// ---------- 12: push-ups vs the voice ----------
function scene12(ctx, W, H, t) {
  const boil = Math.floor(t * 8), tq = Math.floor(t * 12) / 12;
  boardBase(ctx, W, H, boil);
  const fy = 880;
  M(ctx, [[150, fy], [1780, fy + 4]], MK.k, 900, boil, 8);
  const cyc = tq * 0.9, n = Math.floor(cyc), k = cyc - n;
  const ph = Math.sin(k * Math.PI); // 0 up -> 1 down -> 0 up
  const shake = Math.sin(tq * 60) * 3 * (0.5 + ph);
  const sh = [1020 + shake, lerp(fy - 245, fy - 135, ph) + shake];
  const L = 560, feet = [sh[0] - Math.sqrt(L * L - (fy - 8 - sh[1]) ** 2), fy - 8];
  const hip = [lerp(sh[0], feet[0], 0.36), lerp(sh[1], feet[1], 0.36)];
  const P = { hip, sh, head: [sh[0] + 95, sh[1] - 30], hands: [[1030, fy - 4], [1050, fy - 4]], feet: [feet, [feet[0] + 14, fy - 8]],
    knee: [1, 1], elbow: [1, 1], expr: 'strain', dir: 1 };
  stick(ctx, P, boil, { band: true, seg: 150, R: 60, w: 15 });
  // sweat drops
  for (let i = 0; i < 3; i++) { const s = (t * 1.5 + i / 3) % 1; blobFill(ctx, sh[0] + 130 + s * 60, sh[1] - 60 + s * 150, 9, 'rgba(36,87,214,0.7)', 910 + i, boil, 1.3); }
  // shake marks
  M(ctx, [[960, fy - 90], [945, fy - 60]], MK.k, 920, boil, 6); M(ctx, [[1075, fy - 90], [1090, fy - 60]], MK.k, 921, boil, 6);
  // the voice: a grey scribble sitting on his back
  const vx = hip[0] + 20, vy = hip[1] - 70;
  scribbleGhost(ctx, vx, vy, 48, boil, t);
  M(ctx, [[vx - 300, vy - 250], [vx - 20, vy - 250], [vx - 20, vy - 150], [vx - 70, vy - 150], [vx - 30, vy - 80], [vx - 120, vy - 150], [vx - 300, vy - 150], [vx - 300, vy - 254]], '#8a8f99', 930, boil, 6);
  mtext(ctx, 'stay down...', vx - 160, vy - 185, 44, '#6b7079', boil);
  // the count
  const count = 37 + n;
  mtext(ctx, String(count), 1460, 480, 260, MK.r, boil, -0.04);
  M(ctx, [[1330, 520], [1610, 505]], MK.r, 940, boil, 10);
  mtext(ctx, 'Count the ones', 110, 170, 68, MK.k, boil, -0.02, 'PMarker', 'left');
  mtext(ctx, 'that hurt.', 110, 255, 68, MK.r, boil + 1, -0.02, 'PMarker', 'left');
  magnet(ctx, 1730, 150, MK.g);
  boardTray(ctx, W, H, boil);
}

Object.assign(window.SCENES, { '10': scene10, '11': scene11, '12': scene12 });
})();

(() => {
// Style drafts 4-6: fun, expressive, still drawn 100% in code.
const { h1, noise1, curve, brush, circlePts, blobFill, polyFill, grainCanvas, handText, ik } = window.Ink;
const G = {};
const grain = (W, H, k, dark) => G[k] || (G[k] = grainCanvas(W, H, k.length * 31 + 3, dark));

// Thick limb with outline under a colour fill (marker-cartoon trick).
function limbStroke(ctx, pts, w, col, F, seed) {
  const o = { noTaper: true, roundCaps: true, boil: F.boil, wob: F.wob ?? 1.2, pressure: 0.1 };
  brush(ctx, pts, { ...o, w: w + F.ol * 2, color: F.line, seed });
  ctx.save(); ctx.translate(F.mis[0], F.mis[1]);
  if (F.fillOp) ctx.globalCompositeOperation = F.fillOp;
  brush(ctx, pts, { ...o, w: w, color: col, seed: seed + 1 });
  ctx.restore();
}
function blobOl(ctx, x, y, r, col, F, seed, sq = 1) {
  blobFill(ctx, x, y, r + F.ol, F.line, seed, F.boil, sq);
  ctx.save(); ctx.translate(F.mis[0], F.mis[1]);
  if (F.fillOp) ctx.globalCompositeOperation = F.fillOp;
  blobFill(ctx, x, y, r, col, seed + 1, F.boil, sq); ctx.restore();
}

// Expressive face. expr: shout | strain | smug | grin | sleepy | proud
function toonFace(ctx, cx, cy, R, dir, expr, F, look = [1, 0]) {
  const L = F.line, b = F.boil, fx = cx + dir * R * 0.2;
  const eyes = [[fx - R * 0.33, cy - R * 0.08], [fx + R * 0.3, cy - R * 0.08]];
  eyes.forEach(([x, y], i) => {
    const s = 300 + i * 10;
    if (expr === 'strain') {
      const k = i === 0 ? 1 : -1;
      brush(ctx, [[x - R * 0.14 * k, y - R * 0.12], [x + R * 0.1 * k, y], [x - R * 0.14 * k, y + R * 0.12]], { w: R * 0.08, color: L, seed: s, boil: b, wob: 0.6, taper: 6 });
    } else if (expr === 'sleepy' || expr === 'smug') {
      brush(ctx, [[x - R * 0.16, y], [x + R * 0.16, y + 1]], { w: R * 0.07, color: L, seed: s, boil: b, wob: 0.6 });
      if (expr === 'smug') blobFill(ctx, x + R * 0.05, y + R * 0.06, R * 0.07, L, s + 2, b);
    } else {
      const er = expr === 'shout' ? R * 0.17 : R * 0.2;
      blobFill(ctx, x, y, er + F.ol * 0.8, L, s, b, 1.15);
      blobFill(ctx, x, y, er, '#ffffff', s + 1, b, 1.15);
      blobFill(ctx, x + look[0] * er * 0.38, y + look[1] * er * 0.4, er * 0.48, L, s + 2, b);
      blobFill(ctx, x + look[0] * er * 0.38 - er * 0.15, y + look[1] * er * 0.4 - er * 0.18, er * 0.13, '#fff', s + 3, b);
    }
    // brows
    const inner = i === 0 ? 1 : -1, by = y - R * 0.3;
    const tilt = { shout: 0.2, strain: 0.22, smug: -0.06, grin: -0.08, sleepy: -0.1, proud: -0.12 }[expr] ?? 0;
    brush(ctx, [[x - inner * R * 0.2, by - R * tilt * 0.5], [x + inner * R * 0.16, by + R * tilt * 0.6]], { w: R * 0.11, color: L, seed: s + 5, boil: b, wob: 0.6, taper: 8 });
  });
  const mx = fx, my = cy + R * 0.42;
  if (expr === 'shout') {
    const pts = [[mx - R * 0.26, my - R * 0.08], [mx + R * 0.26, my - R * 0.1], [mx + R * 0.16, my + R * 0.28], [mx - R * 0.14, my + R * 0.3]];
    polyFill(ctx, pts, L, 320, b, 2);
    polyFill(ctx, [[mx - R * 0.17, my], [mx + R * 0.17, my - 2], [mx + R * 0.1, my + R * 0.2], [mx - R * 0.09, my + R * 0.22]], '#b8323a', 321, b, 1.5);
    blobFill(ctx, mx, my + R * 0.15, R * 0.08, '#ff7b84', 322, b);
  } else if (expr === 'strain') {
    polyFill(ctx, [[mx - R * 0.26, my - R * 0.06], [mx + R * 0.26, my - R * 0.06], [mx + R * 0.24, my + R * 0.14], [mx - R * 0.24, my + R * 0.14]], L, 330, b, 1.5);
    polyFill(ctx, [[mx - R * 0.2, my - R * 0.02], [mx + R * 0.2, my - R * 0.02], [mx + R * 0.19, my + R * 0.1], [mx - R * 0.19, my + R * 0.1]], '#fff', 331, b, 1);
    brush(ctx, [[mx - R * 0.2, my + R * 0.04], [mx + R * 0.2, my + R * 0.04]], { w: 3, color: L, seed: 332, boil: b, noTaper: true });
  } else {
    const up = expr === 'smug' ? 0.12 : expr === 'sleepy' ? -0.02 : 0.14;
    const ptsM = expr === 'smug'
      ? [[mx - R * 0.2, my], [mx + R * 0.05, my + R * 0.04], [mx + R * 0.24, my - R * 0.1]]
      : [[mx - R * 0.22, my - R * up * 0.3], [mx, my + R * up], [mx + R * 0.22, my - R * up * 0.3]];
    brush(ctx, curve(ptsM, 8), { w: R * 0.08, color: L, seed: 340, boil: b, wob: 0.6, taper: 8 });
  }
}

// Full toon figure. F: hip, sh, head, R, hands[2], feet[2] (index 0 = far side), seg, lw, cols, dir...
function toonFig(ctx, F) {
  const leg = i => ik(F.hip, F.feet[i], F.seg, F.seg, F.kneeSign[i]);
  const arm = i => ik(F.sh, F.hands[i], F.seg * 0.85, F.seg * 0.8, F.elbowSign[i]);
  const shoe = (i, legPts) => {
    const [x, y] = legPts[2];
    blobOl(ctx, x + F.dir * F.lw * 0.35, y + F.lw * 0.15, F.lw * 0.75, F.cols.shoe, F, 400 + i, 0.62);
  };
  const hand = (i, a) => blobOl(ctx, a[2][0], a[2][1], F.lw * 0.5, F.cols.skin, F, 420 + i);
  const back = F.cols.shade ?? 0.82;
  const A0 = arm(0), L0 = leg(0), L1 = leg(1), A1 = arm(1);
  ctx.save();
  limbStroke(ctx, A0, F.lw * 0.9, F.cols.top, F, 201); hand(0, A0);
  limbStroke(ctx, L0, F.lw, F.cols.pants, F, 203); shoe(0, L0);
  ctx.restore();
  // torso (hoodie) as a fat stroke
  limbStroke(ctx, [F.hip, [(F.hip[0] + F.sh[0]) / 2, (F.hip[1] + F.sh[1]) / 2 - 4], F.sh], F.lw * 2.0, F.cols.top, F, 205);
  limbStroke(ctx, L1, F.lw, F.cols.pants, F, 207); shoe(1, L1);
  // head + hair
  const [hx, hy] = F.head, R = F.R;
  blobOl(ctx, hx, hy, R, F.cols.skin, F, 209);
  if (F.cols.hair) {
    const pts = [];
    for (let k = 0; k <= 9; k++) {
      const a = Math.PI * (1.08 + k * 0.094) - F.dir * 0.12;
      const rr = R * (k % 2 ? 1.28 : 1.04);
      pts.push([hx + Math.cos(a) * rr, hy + Math.sin(a) * rr]);
    }
    pts.push([hx + R * 0.7 * F.dir, hy - R * 0.55], [hx - R * 0.6 * F.dir, hy - R * 0.5]);
    polyFill(ctx, pts.map(p => [p[0], p[1] - F.ol]), F.line, 211, F.boil, 2);
    polyFill(ctx, pts.map(p => [p[0] + F.mis[0] * 0.5, p[1] + 2]), F.cols.hair, 212, F.boil, 2);
  }
  toonFace(ctx, hx, hy, R, F.dir, F.expr, F, F.look);
  limbStroke(ctx, A1, F.lw * 0.9, F.cols.top, F, 213); hand(1, A1);
}

function speedLines(ctx, x0, x1, ys, col, boil, t, w = 6) {
  ys.forEach((y, i) => {
    const off = ((t * 900 + i * 137) % 160);
    brush(ctx, [[x0 - off, y], [x1 - off, y + 2]], { w, color: col, seed: 500 + i, boil, wob: 1, taper: 30 });
  });
}
function sweat(ctx, x, y, s, F, seed) {
  const pts = [[x, y - s * 1.3], [x + s * 0.7, y + s * 0.2], [x, y + s * 0.8], [x - s * 0.7, y + s * 0.2]];
  polyFill(ctx, pts.map(p => [p[0] - F.ol * 0.6, p[1]]), F.line, seed, F.boil, 1);
  polyFill(ctx, curve([...pts, pts[0]], 4).map(p => [p[0] + 1, p[1] + 1]), '#8fd4ff', seed + 1, F.boil, 1);
}
function boldText(ctx, str, x, y, size, fill, line, boil, opt = {}) {
  ctx.save(); ctx.font = `${size}px ${opt.font ?? 'PMarker'}`; ctx.textAlign = 'center'; ctx.lineJoin = 'round';
  ctx.translate(x + (h1(1, boil) - 0.5) * 3, y + (h1(2, boil) - 0.5) * 3); ctx.rotate((opt.rot ?? 0) + (h1(3, boil) - 0.5) * 0.015);
  if (opt.shadow) { ctx.fillStyle = opt.shadow; ctx.fillText(str, 8, 8); }
  if (line) { ctx.strokeStyle = line; ctx.lineWidth = opt.lw ?? 14; ctx.strokeText(str, 0, 0); }
  ctx.fillStyle = fill; ctx.fillText(str, 0, 0); ctx.restore();
}

// ---------- 4: MARKER CARTOON — the bed fights back ----------
function scene4(ctx, W, H, t) {
  const boil = Math.floor(t * 8), tq = Math.floor(t * 12) / 12;
  const F0 = { line: '#1b1720', ol: 6, mis: [5, 4], boil, wob: 1.4 };
  // room
  ctx.fillStyle = '#bfe0f4'; ctx.fillRect(0, 0, W, H);
  const fy = 1300;
  polyFill(ctx, [[-20, fy], [W + 20, fy], [W + 20, H + 20], [-20, H + 20]], '#f2c98d', 1, boil, 2);
  brush(ctx, [[-20, fy], [W + 20, fy + 4]], { w: 8, color: F0.line, seed: 2, boil, noTaper: true });
  // window with sunrise
  const wx = 690, wy = 640, ww = 300, wh = 300;
  polyFill(ctx, [[wx, wy], [wx + ww, wy], [wx + ww, wy + wh], [wx, wy + wh]], '#ffb36b', 3, boil, 2);
  blobFill(ctx, wx + ww * 0.5, wy + wh * 0.82, 70, '#ffe36e', 4, boil);
  brush(ctx, [[wx, wy], [wx + ww, wy], [wx + ww, wy + wh], [wx, wy + wh], [wx, wy - 4]], { w: 10, color: F0.line, seed: 5, boil, noTaper: true, roundCaps: true });
  brush(ctx, [[wx + ww / 2, wy], [wx + ww / 2, wy + wh]], { w: 8, color: F0.line, seed: 6, boil, noTaper: true });
  // bed
  const bx0 = 40, bx1 = 600, by = 1120;
  polyFill(ctx, [[bx0 - 6, by - 6], [bx1 + 6, by - 6], [bx1 + 6, by + 106], [bx0 - 6, by + 106]], F0.line, 7, boil, 2);
  polyFill(ctx, [[bx0, by], [bx1, by], [bx1, by + 100], [bx0, by + 100]], '#ffffff', 8, boil, 2);
  limbStroke(ctx, [[bx0 + 30, by + 100], [bx0 + 30, fy]], 22, '#a86b3c', F0, 9);
  limbStroke(ctx, [[bx1 - 30, by + 100], [bx1 - 30, fy]], 22, '#a86b3c', F0, 11);
  limbStroke(ctx, [[bx0 + 10, by - 160], [bx0 + 10, fy]], 34, '#a86b3c', F0, 13);
  // excuse monster under the blanket (purple), grabbing the ankle
  const shake = Math.sin(tq * 40) * 5;
  const mx = 300, my = by - 40;
  const footBack = [560 + shake, by - 30];
  limbStroke(ctx, curve([[mx + 60, my - 10], [mx + 170, my - 70 + shake], footBack.map((v, i) => v + (i ? 18 : -14))], 8), 34, '#8b5cf6', F0, 15);
  blobOl(ctx, mx, my - 30, 115, '#8b5cf6', F0, 17, 0.85);
  toonFace(ctx, mx - 10, my - 50, 95, 1, 'smug', F0);
  // blanket over the monster's lower half
  polyFill(ctx, [[bx0 - 6, by - 6], [bx0 + 80, by - 80], [mx + 120, by - 50], [bx1 - 80, by - 26], [bx1 - 30, by + 50], [bx0 - 6, by + 50]], F0.line, 19, boil, 3);
  polyFill(ctx, [[bx0 + 2, by], [bx0 + 84, by - 70], [mx + 118, by - 42], [bx1 - 86, by - 18], [bx1 - 38, by + 44], [bx0 + 2, by + 44]], '#2fb5a4', 20, boil, 3);
  // hero lunging out of bed toward the window
  const lunge = Math.sin(tq * 6) * 12;
  const hip = [640 + lunge * 0.3, 1010], sh = [790 + lunge, 930], R = 92;
  const F = { ...F0, hip, sh, head: [sh[0] + 75, sh[1] - 95], R, seg: 120, lw: 38, dir: 1,
    hands: [[960 + lunge, 850 + shake], [1000 + lunge, 920 - shake]], feet: [footBack, [780, 1150 + shake]],
    kneeSign: [1, -1], elbowSign: [-1, -1], expr: 'shout', look: [1, -0.2],
    cols: { skin: '#ffd9b8', top: '#ff6a2b', pants: '#2a3e8f', shoe: '#ffffff', hair: '#3a2416' } };
  toonFig(ctx, F);
  sweat(ctx, 760, 790, 22, F0, 600); sweat(ctx, 1000, 760, 16, F0, 610);
  // alarm clock jumping
  const ax = 330, ay = 1420 - Math.abs(Math.sin(tq * 30)) * 18;
  blobOl(ctx, ax, ay, 70, '#ff3b3b', F0, 30);
  blobFill(ctx, ax, ay, 48, '#fffbe8', 32, boil);
  ctx.save(); ctx.font = '44px PMarker'; ctx.fillStyle = '#ff3b3b'; ctx.textAlign = 'center'; ctx.fillText('5:00', ax, ay + 16); ctx.restore();
  [[-1, -1], [1, -1]].forEach(([sx], i) => {
    for (let k = 0; k < 3; k++) brush(ctx, [[ax + sx * (90 + k * 4), ay - 40 + k * 32], [ax + sx * (125 + k * 6), ay - 52 + k * 36]], { w: 7, color: F0.line, seed: 34 + i * 3 + k, boil, taper: 8 });
  });
  // text
  boldText(ctx, 'RRRING!', 620, 1440, 76, '#ff3b3b', F0.line, boil, { rot: -0.08, lw: 12 });
  boldText(ctx, 'The bed always wins.', W / 2, 330, 72, '#1b1720', null, boil, { font: 'Gaegu' });
  boldText(ctx, 'NOT TODAY.', W / 2, 480, 130, '#ffffff', F0.line, boil, { rot: -0.04, lw: 18, shadow: '#ff6a2b' });
  brush(ctx, [[W / 2 - 70, 312], [W / 2 + 85, 300]], { w: 9, color: '#ff3b3b', seed: 40, boil, taper: 10 });
  ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(grain(W, H, 'g4', false), 0, 0); ctx.globalCompositeOperation = 'source-over';
}

// ---------- 5: NOTEBOOK DOODLE — 9PM me vs 5AM me ----------
function scene5(ctx, W, H, t) {
  const boil = Math.floor(t * 8), tq = Math.floor(t * 12) / 12;
  const pen = '#1d3bb3', hlY = 'rgba(255,236,60,0.75)', hlP = 'rgba(255,105,180,0.55)', hlG = 'rgba(90,230,140,0.55)';
  ctx.fillStyle = '#fdfcf6'; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(80,140,220,0.22)'; ctx.lineWidth = 2;
  for (let y = 40; y < H; y += 44) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.strokeStyle = 'rgba(230,70,70,0.45)'; ctx.beginPath(); ctx.moveTo(96, 0); ctx.lineTo(96, H); ctx.stroke();
  const P = (pts, s, w = 5) => brush(ctx, pts, { w, color: pen, seed: s, boil, wob: 1.6, taper: 12, pressure: 0.5 });
  const hl = (pts, col, s) => { ctx.save(); ctx.globalCompositeOperation = 'multiply'; polyFill(ctx, pts, col, s, boil, 4); ctx.restore(); };
  const write = (s, x, y, size, col = pen, rot = 0, font = 'Gaegu') => { ctx.save(); ctx.translate(x, y); ctx.rotate(rot + (h1(5, boil) - 0.5) * 0.01); ctx.font = `${size}px ${font}`; ctx.fillStyle = col; ctx.textAlign = 'center'; ctx.fillText(s, 0, 0); ctx.restore(); };
  // header
  hl([[160, 330], [930, 318], [935, 380], [165, 392]], hlY, 1);
  write('my brain at 9PM vs 5AM', W / 2, 370, 84);
  // panel 1 box
  const box = (x, y, w, h, s) => P([[x, y], [x + w, y + 3], [x + w - 2, y + h], [x + 2, y + h - 2], [x, y - 6]], s, 6);
  box(130, 470, 820, 520, 2); box(130, 1040, 820, 470, 3);
  write('9:00 PM', 250, 530, 56, pen, -0.05);
  // proud planner with cape + checklist
  const bob = Math.sin(tq * 5) * 8;
  const cx = 360, cy = 760 + bob;
  hl([[cx - 70, cy - 40], [cx + 70, cy - 46], [cx + 60, cy + 120], [cx - 60, cy + 125]], hlG, 4); // shirt
  hl([[cx - 60, cy - 30], [cx - 190, cy + 170 + bob], [cx - 40, cy + 120]], 'rgba(255,90,90,0.55)', 5); // cape
  P(circlePts(cx, cy - 120, 70, 6 + boil), 6, 6);
  P(curve([[cx - 50, cy - 168], [cx - 10, cy - 205], [cx + 30, cy - 175], [cx + 60, cy - 200]], 6), 7, 6);
  // face: sparkly eyes + big grin
  [[-24, 0], [24, 0]].forEach(([dx], i) => { P([[cx + dx - 12, cy - 130], [cx + dx + 12, cy - 130]], 8 + i, 6); P([[cx + dx, cy - 142], [cx + dx, cy - 118]], 10 + i, 6); });
  P(curve([[cx - 34, cy - 92], [cx, cy - 66], [cx + 34, cy - 92]], 6), 12, 6);
  P([[cx, cy - 50], [cx, cy + 120]], 13, 6);
  P([[cx, cy + 120], [cx - 50, cy + 210]], 14); P([[cx, cy + 120], [cx + 50, cy + 210]], 15);
  P([[cx, cy - 10], [cx - 60, cy - 70], [cx - 70, cy - 120]], 16); // fist up
  P(circlePts(cx - 70, cy - 132, 16, 17), 17, 5);
  P([[cx, cy - 10], [cx + 90, cy + 20]], 18);
  // checklist
  const lx = 560, ly = 610;
  P([[lx, ly], [lx + 330, ly + 6], [lx + 322, ly + 330], [lx - 4, ly + 326], [lx, ly - 4]], 19, 5);
  ['5AM wake up', 'run 5K', 'read 30 pages', 'cold shower'].forEach((s, i) => {
    const y = ly + 70 + i * 70;
    P([[lx + 24, y - 30], [lx + 54, y - 30], [lx + 54, y], [lx + 24, y], [lx + 24, y - 34]], 20 + i, 4);
    write(s, lx + 190, y, 44, pen, (i - 1.5) * 0.01);
  });
  write('easy.', 790, 990 - 22, 56, '#e0306a', -0.08, 'Caveat');
  // sparkles
  for (let i = 0; i < 3; i++) {
    const sx = [230, 480, 520][i], sy = [610, 590, 860][i], k = 14 + 6 * Math.sin(tq * 8 + i * 2);
    P([[sx - k, sy], [sx + k, sy]], 30 + i, 4); P([[sx, sy - k], [sx, sy + k]], 33 + i, 4);
  }
  // panel 2: 5AM puddle
  write('5:00 AM', 250, 1100, 56, pen, -0.04);
  const wob = Math.sin(tq * 3) * 6;
  // bed
  P([[200, 1380], [880, 1384]], 40, 6); P([[200, 1380], [200, 1460]], 41); P([[880, 1384], [880, 1460]], 42);
  P([[200, 1300], [200, 1460]], 43, 6);
  // blanket blob with melted guy
  const bl = curve([[240, 1380], [300, 1300 + wob], [480, 1280 - wob], [700, 1300 + wob], [840, 1340], [860, 1384]], 8);
  hl([...bl, [240, 1384]], hlP, 44);
  P(bl, 45, 6);
  P(circlePts(300, 1290, 52, 46 + boil, 0.3, 0.75), 46, 5); // squished head
  P([[275, 1290], [295, 1292]], 47, 5); P([[312, 1292], [332, 1290]], 48, 5); // closed eyes
  P(curve([[280, 1318], [300, 1312], [320, 1318]], 5), 49, 4);
  // drool + zzz
  P([[322, 1318], [324, 1336 + wob]], 50, 3);
  ['z', 'z', 'Z'].forEach((z, i) => {
    const zt = (t * 0.6 + i * 0.33) % 1;
    write(z, 380 + i * 40 + zt * 30, 1240 - i * 50 - zt * 60, 50 + i * 12, pen);
  });
  // annotation arrow
  P(curve([[700, 1180], [640, 1215], [560, 1260]], 6), 51, 5);
  P([[560, 1260], [585, 1235]], 52, 5); P([[560, 1260], [592, 1262]], 53, 5);
  write('same guy.', 800, 1180, 62, '#e0306a', -0.05, 'Caveat');
  ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(grain(W, H, 'g5', false), 0, 0); ctx.globalCompositeOperation = 'source-over';
}

// ---------- 6: RISO PRINT — one more rep ----------
function halftone(ctx, cx, cy, r0, r1, col, step = 22) {
  ctx.save(); ctx.fillStyle = col;
  for (let y = cy - r1; y < cy + r1; y += step) for (let x = cx - r1 + ((y / step) % 2 ? step / 2 : 0); x < cx + r1; x += step) {
    const d = Math.hypot(x - cx, y - cy); if (d > r1) continue;
    const k = 1 - Math.max(0, (d - r0) / (r1 - r0));
    ctx.beginPath(); ctx.arc(x, y, step * 0.48 * k, 0, 7); ctx.fill();
  }
  ctx.restore();
}
function scene6(ctx, W, H, t) {
  const boil = Math.floor(t * 8), tq = Math.floor(t * 12) / 12;
  const pink = '#ff4f8b', blue = '#2747d8', paper = '#f6f0e4';
  ctx.fillStyle = paper; ctx.fillRect(0, 0, W, H);
  ctx.globalCompositeOperation = 'multiply';
  // big halftone sun burst behind
  halftone(ctx, W / 2 + 6, 1010 + 4, 160, 440, pink, 24);
  // rays
  for (let i = 0; i < 14; i++) {
    const a = i / 14 * Math.PI * 2 + t * 0.15;
    brush(ctx, [[W / 2 + Math.cos(a) * 330, 1010 + Math.sin(a) * 330], [W / 2 + Math.cos(a) * 560, 1010 + Math.sin(a) * 560]], { w: 14, color: pink, seed: 60 + i, boil, taper: 40 });
  }
  // counter
  ctx.save(); ctx.font = '300px PMarker'; ctx.fillStyle = 'rgba(39,71,216,0.18)'; ctx.textAlign = 'center'; ctx.fillText('47', W / 2, 1300); ctx.restore();
  // push-up: slow down/up with shaking arms
  const ph = (Math.sin(tq * 2.2) + 1) / 2; // 0 up, 1 down
  const shake = Math.sin(tq * 55) * 4 * (0.4 + ph);
  const fy = 1330, hand = [740, fy];
  const shY = lerp(fy - 215, fy - 120, ph) + shake;
  const sh = [720 + shake * 0.5, shY];
  const feet = [sh[0] - Math.sqrt(500 * 500 - (fy - 8 - shY) ** 2), fy - 8];
  const hip = [lerp(sh[0], feet[0], 0.44), lerp(sh[1], feet[1], 0.44)], hipY = hip[1];
  const F = { line: blue, ol: 7, mis: [6, 4], boil, wob: 1.3, hip, sh, head: [sh[0] + 92, sh[1] - 38], R: 84, seg: 138, lw: 36, dir: 1,
    hands: [[hand[0] - 30, fy], [hand[0] + 6, fy]], feet: [[feet[0] + 14, fy - 8], feet],
    kneeSign: [-1, -1], elbowSign: [1, 1], expr: 'strain', look: [0, 0],
    cols: { skin: '#ffd6e2', top: '#ff6f9c', pants: '#ff9dbb', shoe: paper, hair: blue, shade: 0.92 } };
  // ground line
  brush(ctx, [[120, fy + 26], [960, fy + 30]], { w: 10, color: blue, seed: 70, boil, noTaper: true });
  ctx.globalCompositeOperation = 'source-over';
  toonFig(ctx, F);
  // sweat + shake marks
  for (let i = 0; i < 3; i++) {
    const st = (t * 1.6 + i / 3) % 1;
    sweat(ctx, sh[0] + 140 + st * 90 + i * 20, sh[1] - 120 + st * 160, 18, F, 80 + i * 3);
  }
  [[-1], [1]].forEach(([s], i) => { brush(ctx, [[hand[0] + s * 70, fy - 110], [hand[0] + s * 84, fy - 70]], { w: 7, color: blue, seed: 90 + i, boil, taper: 6 }); brush(ctx, [[hand[0] + s * 90, fy - 120], [hand[0] + s * 106, fy - 80]], { w: 7, color: blue, seed: 92 + i, boil, taper: 6 }); });
  // tiny voice on his back
  const vx = hip[0] - 20, vy = hipY - 75;
  blobOl(ctx, vx, vy, 34, '#9fb0ff', { ...F, ol: 5 }, 95);
  toonFace(ctx, vx, vy, 30, -1, 'smug', F);
  polyFill(ctx, [[vx - 250, vy - 230], [vx - 10, vy - 236], [vx - 14, vy - 140], [vx - 40, vy - 138], [vx - 20, vy - 60], [vx - 90, vy - 136], [vx - 248, vy - 132]], blue, 96, boil, 3);
  ctx.save(); ctx.font = '50px PMarker'; ctx.fillStyle = paper; ctx.textAlign = 'center'; ctx.fillText('stop...', vx - 130, vy - 165); ctx.restore();
  // big lettering, riso misregistered
  ctx.globalCompositeOperation = 'multiply';
  const pulse = 1 + 0.04 * Math.sin(tq * 6);
  ctx.save(); ctx.translate(W / 2, 430); ctx.scale(pulse, pulse);
  boldText(ctx, 'ONE', -120 + 8, 6, 190, pink, null, boil, { rot: -0.07 });
  boldText(ctx, 'ONE', -120, 0, 190, blue, null, boil, { rot: -0.07 });
  boldText(ctx, 'MORE.', 90 + 8, 196, 190, pink, null, boil + 1, { rot: -0.07 });
  boldText(ctx, 'MORE.', 90, 190, 190, blue, null, boil + 1, { rot: -0.07 });
  ctx.restore();
  ctx.globalCompositeOperation = 'source-over';
  ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(grain(W, H, 'g6', false), 0, 0); ctx.globalCompositeOperation = 'source-over';
}
const lerp = (a, b, k) => a + (b - a) * k;

Object.assign(window.SCENES, { '4': scene4, '5': scene5, '6': scene6 });
})();

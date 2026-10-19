(() => {
// Style drafts 7-9 (16:9): the whole frame is a whiteboard; the inside changes per style.
const { h1, curve, brush, circlePts, blobFill, polyFill, grainCanvas, ik } = window.Ink;
const { limbStroke, blobOl, toonFace, toonFig, sweat, boldText } = window.Toon;
const lerp = (a, b, k) => a + (b - a) * k;
const MK = { k: '#1d1d24', r: '#e0353b', b: '#2457d6', g: '#1f9d55' };

// ---------- shared whiteboard frame ----------
function boardBase(ctx, W, H, boil) {
  // aluminium frame
  const fg = ctx.createLinearGradient(0, 0, 0, H);
  fg.addColorStop(0, '#d9dce1'); fg.addColorStop(0.5, '#b8bdc5'); fg.addColorStop(1, '#a3a9b2');
  ctx.fillStyle = fg; ctx.fillRect(0, 0, W, H);
  const m = 34;
  ctx.fillStyle = '#8d939c'; ctx.fillRect(m - 4, m - 4, W - 2 * m + 8, H - 2 * m + 8);
  const bg = ctx.createLinearGradient(0, 0, W, H);
  bg.addColorStop(0, '#ffffff'); bg.addColorStop(1, '#f1f3f6');
  ctx.fillStyle = bg; ctx.fillRect(m, m, W - 2 * m, H - 2 * m);
  // ghost smudges from erased marker
  for (let i = 0; i < 9; i++) {
    const x = m + h1(i, 3) * (W - 2 * m), y = m + h1(i, 4) * (H - 2 * m), r = 120 + h1(i, 5) * 220;
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, 'rgba(120,130,150,0.06)'); g.addColorStop(1, 'rgba(120,130,150,0)');
    ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r);
  }
  for (let i = 0; i < 5; i++) {
    const x = m + 80 + h1(i, 7) * (W - 400), y = m + 60 + h1(i, 8) * (H - 300);
    brush(ctx, curve([[x, y], [x + 90, y - 20], [x + 200, y + 10]], 6), { w: 26, color: 'rgba(110,120,140,0.05)', seed: 900 + i, wob: 3 });
  }
  return m;
}
function boardTray(ctx, W, H, boil) {
  // marker tray along the bottom edge, with markers and an eraser
  const ty = H - 30;
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.25)'; ctx.shadowBlur = 10; ctx.shadowOffsetY = -2;
  const tg = ctx.createLinearGradient(0, ty - 12, 0, H);
  tg.addColorStop(0, '#e3e6ea'); tg.addColorStop(1, '#9ea4ad');
  ctx.fillStyle = tg; ctx.fillRect(W * 0.12, ty - 12, W * 0.76, 42); ctx.restore();
  const marker = (x, col, cap) => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.3)'; ctx.shadowBlur = 6; ctx.shadowOffsetY = 3;
    ctx.fillStyle = '#f4f4f6'; roundRect(ctx, x, ty - 30, 150, 26, 12); ctx.fill(); ctx.restore();
    ctx.fillStyle = col; roundRect(ctx, x + 112, ty - 31, 46, 28, 10); ctx.fill();
    ctx.fillStyle = col; ctx.fillRect(x + 20, ty - 24, 70, 14);
  };
  marker(W * 0.18, MK.k); marker(W * 0.27, MK.r); marker(W * 0.36, MK.b);
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.3)'; ctx.shadowBlur = 8; ctx.shadowOffsetY = 3;
  ctx.fillStyle = '#2b2f38'; roundRect(ctx, W * 0.7, ty - 46, 170, 44, 8); ctx.fill(); ctx.restore();
  ctx.fillStyle = '#d7d9de'; roundRect(ctx, W * 0.7, ty - 18, 170, 16, 5); ctx.fill();
}
function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}
function magnet(ctx, x, y, col) {
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = 10; ctx.shadowOffsetY = 5;
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, 22, 0, 7); ctx.fill(); ctx.restore();
  ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.beginPath(); ctx.arc(x - 7, y - 7, 7, 0, 7); ctx.fill();
}
function sticky(ctx, x, y, w, rot, col, lines, boil) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.shadowColor = 'rgba(0,0,0,0.22)'; ctx.shadowBlur = 14; ctx.shadowOffsetY = 6;
  ctx.fillStyle = col; ctx.fillRect(-w / 2, -w / 2, w, w); ctx.shadowColor = 'transparent';
  ctx.fillStyle = 'rgba(0,0,0,0.06)'; ctx.fillRect(-w / 2, -w / 2, w, 18);
  lines.forEach(([s, size, c], i) => { ctx.font = `${size}px PMarker`; ctx.fillStyle = c ?? MK.k; ctx.textAlign = 'center'; ctx.fillText(s, (h1(i, boil) - 0.5) * 2, -w / 2 + 70 + i * (size + 10)); });
  ctx.restore();
}
const M = (ctx, pts, col, s, boil, w = 7) => brush(ctx, pts, { w, color: col, seed: s, boil, wob: 1.4, taper: 10, pressure: 0.3 });
function mtext(ctx, s, x, y, size, col, boil, rot = 0, font = 'PMarker', align = 'center') {
  ctx.save(); ctx.translate(x + (h1(1, boil) - 0.5) * 2, y + (h1(2, boil) - 0.5) * 2); ctx.rotate(rot + (h1(3, boil) - 0.5) * 0.012);
  ctx.font = `${size}px ${font}`; ctx.fillStyle = col; ctx.textAlign = align; ctx.fillText(s, 0, 0); ctx.restore();
}
function arrow(ctx, pts, col, s, boil) {
  const c = curve(pts, 8); M(ctx, c, col, s, boil, 6);
  const a = c[c.length - 1], b = c[c.length - 4], ang = Math.atan2(a[1] - b[1], a[0] - b[0]);
  [0.5, -0.5].forEach((d, i) => M(ctx, [a, [a[0] - Math.cos(ang + d) * 26, a[1] - Math.sin(ang + d) * 26]], col, s + 1 + i, boil, 6));
}

// Running figure targets for toonFig.
function runner(x, gy, S, ph, dir) {
  const seg = S * 0.25, bob = Math.abs(Math.cos(ph)) * S * 0.03;
  const hip = [x, gy - S * 0.44 - bob];
  const lean = 0.28;
  const sh = [hip[0] + Math.sin(lean) * S * 0.3 * dir, hip[1] - Math.cos(lean) * S * 0.3];
  const feet = [0, 1].map(i => {
    const p = ph + i * Math.PI, th = 0.2 + 0.8 * Math.sin(p), sh2 = th - (0.25 + 1.3 * Math.max(0, Math.cos(p)));
    const k = [hip[0] + Math.sin(th) * seg * dir, hip[1] + Math.cos(th) * seg];
    return [k[0] + Math.sin(sh2) * seg * dir, Math.min(gy - 8, k[1] + Math.cos(sh2) * seg)];
  });
  const hands = [0, 1].map(i => {
    const p = ph + i * Math.PI, sw = -Math.sin(p);
    return [sh[0] + dir * S * (0.03 + 0.17 * sw), sh[1] + S * (0.2 - 0.1 * Math.max(0, sw))];
  });
  return { hip, sh, feet, hands, head: [sh[0] + dir * S * 0.09, sh[1] - S * 0.19], seg };
}

// ---------- 7: marker drawn straight on the whiteboard, annotated like a lesson ----------
function scene7(ctx, W, H, t) {
  const boil = Math.floor(t * 8), tq = Math.floor(t * 12) / 12;
  boardBase(ctx, W, H, boil);
  // title
  mtext(ctx, 'Your brain says DONE.', 140, 150, 66, MK.k, boil, -0.01, 'PMarker', 'left');
  mtext(ctx, "You're only 40% in.", 140, 240, 66, MK.r, boil + 1, -0.01, 'PMarker', 'left');
  M(ctx, [[140, 262], [700, 256]], MK.r, 5, boil, 8);
  // floor
  const fy = 900;
  M(ctx, [[260, fy], [1300, fy + 4]], MK.k, 6, boil, 7);
  // deadlift: bar rises slowly with shaking
  const lift = (Math.sin(tq * 1.6 - 1.2) + 1) / 2, shake = Math.sin(tq * 60) * 3;
  const cx = 780, barY = lerp(fy - 110, fy - 330, lift) + shake;
  const hip = [cx - lerp(110, 20, lift), lerp(fy - 230, fy - 360, lift)];
  const sh = [cx + lerp(70, 0, lift), barY - 205];
  const dl = Math.hypot(sh[0] - hip[0], sh[1] - hip[1]), ux = (sh[0] - hip[0]) / dl, uy = (sh[1] - hip[1]) / dl;
  const F = { line: MK.k, ol: 5, mis: [0, 0], boil, wob: 1.3, hip, sh, head: [sh[0] + ux * 95 + 10, sh[1] + uy * 95], R: 74, seg: 132, lw: 30, dir: 1,
    hands: [[cx + 8, barY], [cx + 20, barY]], feet: [[cx - 30, fy - 10], [cx, fy - 10]],
    kneeSign: [-1, -1], elbowSign: [1, 1], expr: 'strain', look: [0, 0],
    cols: { skin: '#ffffff', top: '#c4d6fb', pants: '#e3e4ea', shoe: '#ffffff', hair: MK.k, shade: 1 } };
  toonFig(ctx, F);
  M(ctx, [[cx - 330, barY], [cx + 370, barY + 2]], MK.k, 7, boil, 14);
  [[-300, 1], [-255, 2], [300, 3], [345, 4]].forEach(([dx, s]) => {
    polyFill(ctx, [[cx + dx - 18, barY - 120], [cx + dx + 18, barY - 120], [cx + dx + 18, barY + 120], [cx + dx - 18, barY + 120]], s % 2 ? MK.r : MK.b, 20 + s, boil, 2);
    M(ctx, [[cx + dx - 18, barY - 120], [cx + dx + 18, barY - 120], [cx + dx + 18, barY + 120], [cx + dx - 18, barY + 120], [cx + dx - 18, barY - 124]], MK.k, 30 + s, boil, 5);
  });
  F.hands.forEach((p, i) => blobOl(ctx, p[0], p[1], 15, '#ffffff', F, 35 + i));
  sweat(ctx, sh[0] + 150, sh[1] - 120, 16, F, 60); sweat(ctx, sh[0] - 60, sh[1] - 130, 13, F, 63);
  // shake marks on legs
  M(ctx, [[cx - 120, fy - 120], [cx - 140, fy - 90]], MK.k, 40, boil, 5); M(ctx, [[cx - 140, fy - 150], [cx - 160, fy - 120]], MK.k, 41, boil, 5);
  // annotations
  arrow(ctx, [[1080, 175], [1000, 220], [F.head[0] + 90, F.head[1] - 40]], MK.r, 42, boil);
  mtext(ctx, 'brain: "quit. now."', 1090, 170, 46, MK.r, boil, -0.02, 'PMarker', 'left');
  arrow(ctx, [[360, 640], [480, 680], [cx - 150, fy - 130]], MK.b, 45, boil);
  mtext(ctx, 'legs: jelly', 170, 620, 46, MK.b, boil, 0.02, 'PMarker', 'left');
  arrow(ctx, [[1200, 840], [1170, 800], [cx + 380, barY + 60]], MK.g, 48, boil);
  mtext(ctx, '100 kg (feels like 300)', 1200, 870, 40, MK.g, boil, -0.02, 'PMarker', 'left');
  // fuel gauge
  const gx = 1480, gy = 380;
  M(ctx, [[gx, gy], [gx + 260, gy], [gx + 260, gy + 120], [gx, gy + 120], [gx, gy - 4]], MK.k, 50, boil, 7);
  M(ctx, [[gx + 260, gy + 35], [gx + 285, gy + 35], [gx + 285, gy + 85], [gx + 260, gy + 85]], MK.k, 51, boil, 7);
  const fill = 0.6 + 0.03 * Math.sin(tq * 4);
  polyFill(ctx, [[gx + 14, gy + 14], [gx + 14 + 232 * fill, gy + 14], [gx + 14 + 232 * fill, gy + 106], [gx + 14, gy + 106]], 'rgba(31,157,85,0.75)', 52, boil, 2);
  mtext(ctx, 'actually left', gx + 130, gy + 180, 40, MK.k, boil);
  mtext(ctx, '60%', gx + 130, gy + 82, 56, MK.k, boil);
  // tally counter + sticky
  mtext(ctx, 'REPS', 1500, 640, 44, MK.k, boil, 0, 'PMarker', 'left');
  for (let i = 0; i < 7; i++) {
    const x = 1500 + i * 32 + (i >= 5 ? 30 : 0);
    if (i === 4) M(ctx, [[1490, 735], [1640, 675]], MK.k, 70 + i, boil, 6);
    else M(ctx, [[x, 670], [x + 4, 740]], MK.k, 70 + i, boil, 6);
  }
  magnet(ctx, 1690, 160, '#e0353b');
  sticky(ctx, 1690, 230, 200, 0.05, '#ffe66b', [['DAY 47', 48]], boil);
  boardTray(ctx, W, H, boil);
}

// ---------- 8: colour cartoon print taped onto the whiteboard, marker notes around it ----------
function tape(ctx, x, y, rot) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.fillStyle = 'rgba(240,226,180,0.85)'; ctx.fillRect(-70, -20, 140, 40);
  ctx.fillStyle = 'rgba(255,255,255,0.25)'; ctx.fillRect(-70, -20, 140, 8); ctx.restore();
}
function scene8(ctx, W, H, t) {
  const boil = Math.floor(t * 8), tq = Math.floor(t * 12) / 12;
  boardBase(ctx, W, H, boil);
  // marker notes on the board edges
  mtext(ctx, 'MORNING PLAN', 90, 150, 40, MK.k, boil, -0.02, 'PMarker', 'left');
  [['wake 5:00', true], ['run 3K', true], ['no snooze', false]].forEach(([s, done], i) => {
    const y = 230 + i * 70;
    M(ctx, [[120, y - 30], [150, y - 30], [150, y], [120, y], [120, y - 34]], MK.k, 100 + i, boil, 5);
    if (done) M(ctx, [[116, y - 16], [132, y], [160, y - 44]], MK.g, 110 + i, boil, 7);
    mtext(ctx, s, 175, y, 38, MK.k, boil, 0, 'PMarker', 'left');
  });
  arrow(ctx, [[1760, 190], [1700, 150], [1620, 180]], MK.r, 120, boil);
  mtext(ctx, 'you', 1790, 215, 50, MK.r, boil);
  sticky(ctx, 1765, 860, 190, -0.06, '#ff9ec4', [['DAY', 40], ['12', 64, MK.r]], boil);
  magnet(ctx, 1765, 780, MK.b);
  // the print
  const px = 470, py = 130, pw = 1140, ph = 760;
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.25)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 10;
  ctx.fillStyle = '#ffffff'; ctx.fillRect(px - 14, py - 14, pw + 28, ph + 28); ctx.restore();
  ctx.save(); ctx.beginPath(); ctx.rect(px, py, pw, ph); ctx.clip();
  const sky = ctx.createLinearGradient(0, py, 0, py + ph);
  sky.addColorStop(0, '#7fc3f7'); sky.addColorStop(0.55, '#ffc58a'); sky.addColorStop(1, '#ff9a76');
  ctx.fillStyle = sky; ctx.fillRect(px, py, pw, ph);
  const F0 = { line: '#1b1720', ol: 6, mis: [5, 4], boil, wob: 1.3 };
  blobFill(ctx, px + pw * 0.72, py + ph * 0.62, 120, '#ffe36e', 1, boil);
  const scroll = t * 260;
  const hill = (base, amp, col, s, sp) => {
    const pts = []; for (let x = -40; x <= pw + 40; x += 60) pts.push([px + x, py + base + Math.sin((x + scroll * sp) / 220 + s) * amp]);
    const c = curve(pts, 6);
    polyFill(ctx, [...c, [px + pw + 40, py + ph + 40], [px - 40, py + ph + 40]], F0.line, s, boil, 1);
    polyFill(ctx, [...c.map(p => [p[0], p[1] + 6]), [px + pw + 40, py + ph + 40], [px - 40, py + ph + 40]], col, s + 1, boil, 1);
  };
  hill(560, 40, '#7bcf8a', 3, 0.4);
  hill(640, 26, '#3fae6a', 5, 1);
  // speed lines
  for (let i = 0; i < 5; i++) {
    const y = py + 300 + i * 60, off = (t * 900 + i * 230) % 500;
    brush(ctx, [[px + pw - off, y], [px + pw - off - 160, y]], { w: 6, color: 'rgba(255,255,255,0.9)', seed: 130 + i, boil, taper: 40 });
  }
  // excuse monster chasing
  const gy = py + 650, mph = tq * 9;
  const mx = px + 260 + Math.sin(t * 2) * 20, my = gy - 120 - Math.abs(Math.sin(mph)) * 30;
  blobOl(ctx, mx, my, 105, '#8b5cf6', F0, 142, 0.9);
  toonFace(ctx, mx + 10, my - 10, 82, 1, 'smug', F0);
  ctx.save(); ctx.font = '40px PMarker'; ctx.fillStyle = '#ffffff'; ctx.strokeStyle = F0.line; ctx.lineWidth = 8; ctx.lineJoin = 'round';
  ctx.strokeText('"just 5 more min..."', mx - 120, my - 130); ctx.fillText('"just 5 more min..."', mx - 120, my - 130); ctx.restore();
  // hero running away from it
  const R = runner(px + 760, gy + 10, 430, tq * 10.5, 1);
  toonFig(ctx, { ...F0, ...R, R: 78, lw: 34, dir: 1, kneeSign: [-1, -1], elbowSign: [1, 1], expr: 'shout', look: [1, 0],
    cols: { skin: '#ffd9b8', top: '#ff6a2b', pants: '#2a3e8f', shoe: '#ffffff', hair: '#3a2416' } });
  sweat(ctx, R.head[0] - 100, R.head[1] - 40, 16, F0, 150);
  boldText(ctx, 'OUTRUN IT.', px + pw * 0.5, py + 150, 120, '#ffffff', F0.line, boil, { rot: -0.03, lw: 16, shadow: '#ff6a2b' });
  ctx.restore();
  tape(ctx, px + 10, py + 6, -0.5); tape(ctx, px + pw - 10, py + 6, 0.5); tape(ctx, px + 10, py + ph - 6, 0.5); tape(ctx, px + pw - 10, py + ph - 6, -0.5);
  boardTray(ctx, W, H, boil);
}

// ---------- 9: paper cut-out collage held on the whiteboard by magnets ----------
function paper(ctx, pts, col, seed, boil, sh = 1) {
  ctx.save(); ctx.shadowColor = `rgba(0,0,0,${0.28 * sh})`; ctx.shadowBlur = 12 * sh; ctx.shadowOffsetX = 4 * sh; ctx.shadowOffsetY = 7 * sh;
  polyFill(ctx, pts, col, seed, boil, 2.5); ctx.restore();
}
const rectP = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
function circP(cx, cy, r, n = 40) { const p = []; for (let i = 0; i < n; i++) { const a = i / n * 6.283; p.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } return p; }
function scene9(ctx, W, H, t) {
  const boil = Math.floor(t * 6), tq = Math.floor(t * 12) / 12;
  boardBase(ctx, W, H, boil);
  // marker scribbles on the board around the collage
  mtext(ctx, '9 hours', 90, 300, 54, MK.k, boil, -0.03, 'PMarker', 'left');
  mtext(ctx, 'for work.', 90, 370, 54, MK.k, boil + 1, -0.03, 'PMarker', 'left');
  mtext(ctx, '1 hour', 1570, 300, 54, MK.r, boil, 0.03, 'PMarker', 'left');
  mtext(ctx, 'for you.', 1570, 370, 54, MK.r, boil + 1, 0.03, 'PMarker', 'left');
  M(ctx, [[1570, 392], [1820, 400]], MK.r, 205, boil, 7);
  // collage sheet (dark blue card)
  const px = 420, py = 120, pw = 1100, ph = 700;
  paper(ctx, rectP(px, py, pw, ph), '#1e2b5c', 201, boil, 1.4);
  ctx.save(); ctx.beginPath(); ctx.rect(px, py, pw, ph); ctx.clip();
  // moon + stars
  paper(ctx, circP(px + 1040, py + 140, 70), '#ffe9a8', 202, boil);
  paper(ctx, circP(px + 1070, py + 125, 62), '#1e2b5c', 203, boil, 0.3);
  for (let i = 0; i < 9; i++) { const sx = px + 80 + h1(i, 1) * 900, sy = py + 40 + h1(i, 2) * 180, tw = 0.6 + 0.4 * Math.sin(t * 4 + i); paper(ctx, circP(sx, sy, 6 * tw, 8), '#fff6d0', 204 + i, boil, 0.3); }
  // city skyline cut-outs with lit windows
  for (let i = 0; i < 8; i++) {
    const bw = 120 + h1(i, 3) * 80, bh = 180 + h1(i, 4) * 220, bx = px - 30 + i * 165, by = py + ph - 120 - bh;
    paper(ctx, rectP(bx, by, bw, bh + 140), i % 2 ? '#2f3f7c' : '#283670', 220 + i, boil, 0.8);
    for (let wy = by + 30; wy < by + bh; wy += 50) for (let wx = bx + 20; wx < bx + bw - 30; wx += 40) {
      const on = h1(wx * 3 + wy, i) > 0.55;
      if (on) polyFill(ctx, rectP(wx, wy, 20, 26), '#ffd66b', 300 + wx + wy, boil, 1);
    }
  }
  // desk, lamp, laptop
  const dy = py + ph - 150;
  paper(ctx, rectP(px + 300, dy, 640, 34), '#c98b52', 240, boil);
  paper(ctx, rectP(px + 330, dy + 34, 26, 140), '#a86f3e', 241, boil);
  paper(ctx, rectP(px + 880, dy + 34, 26, 140), '#a86f3e', 242, boil);
  const flick = Math.floor(t * 12) % 23 === 0 ? 0.4 : 1;
  ctx.save(); ctx.globalAlpha = 0.35 * flick; ctx.fillStyle = '#ffe28a'; ctx.beginPath(); ctx.moveTo(px + 840, dy - 190); ctx.lineTo(px + 700, dy); ctx.lineTo(px + 930, dy); ctx.fill(); ctx.restore();
  paper(ctx, [[px + 800, dy - 200], [px + 880, dy - 200], [px + 900, dy - 160], [px + 780, dy - 160]], '#ff6a4d', 243, boil);
  paper(ctx, rectP(px + 836, dy - 160, 10, 160), '#e2e2e2', 244, boil, 0.5);
  paper(ctx, [[px + 470, dy - 150], [px + 640, dy - 150], [px + 660, dy], [px + 490, dy]], '#c9ced8', 245, boil);
  ctx.save(); ctx.globalAlpha = 0.3; ctx.fillStyle = '#9fd0ff'; ctx.fillRect(px + 380, dy - 170, 280, 170); ctx.restore();
  // hero sitting, typing, tired
  const F = { line: '#20223a', ol: 3, mis: [0, 0], boil, wob: 1, dir: -1 };
  const tap = Math.sin(tq * 22) * 6;
  const hip = [px + 760, dy - 40], sh = [px + 720, dy - 220];
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.3)'; ctx.shadowBlur = 10; ctx.shadowOffsetX = 4; ctx.shadowOffsetY = 6;
  toonFig(ctx, { ...F, hip, sh, head: [sh[0] - 30, sh[1] - 95], R: 70, seg: 118, lw: 30,
    hands: [[px + 600, dy - 18 + tap], [px + 630, dy - 18 - tap]], feet: [[px + 690, dy + 160], [px + 660, dy + 170]],
    kneeSign: [1, 1], elbowSign: [-1, -1], expr: 'sleepy', look: [-1, 0.3],
    cols: { skin: '#ffd2b0', top: '#f2f2f2', pants: '#3b4a8f', shoe: '#ffffff', hair: '#2b1e18', shade: 1 } });
  ctx.restore();
  // chair
  paper(ctx, rectP(px + 740, dy - 30, 140, 22), '#6b4a8a', 250, boil, 0.6);
  paper(ctx, rectP(px + 860, dy - 200, 22, 190), '#6b4a8a', 251, boil, 0.6);
  // clock spinning
  const cx = px + 160, cy = py + 150;
  paper(ctx, circP(cx, cy, 70), '#ffffff', 260, boil);
  const a1 = t * 3, a2 = t * 0.25;
  M(ctx, [[cx, cy], [cx + Math.sin(a1) * 55, cy - Math.cos(a1) * 55]], '#20223a', 261, boil, 6);
  M(ctx, [[cx, cy], [cx + Math.sin(a2) * 36, cy - Math.cos(a2) * 36]], '#20223a', 262, boil, 8);
  ctx.restore();
  // paper label strip
  ctx.save(); ctx.translate(px + pw / 2, py + ph + 105); ctx.rotate(-0.02);
  paper(ctx, rectP(-330, -50, 660, 100), '#fffaf0', 270, boil);
  ctx.font = '62px PMarker'; ctx.fillStyle = '#20223a'; ctx.textAlign = 'center'; ctx.fillText('STILL GOING TO THE GYM.', 0, 22); ctx.restore();
  magnet(ctx, px + 20, py + 20, MK.r); magnet(ctx, px + pw - 20, py + 20, MK.b); magnet(ctx, px + 20, py + ph - 20, MK.g); magnet(ctx, px + pw - 20, py + ph - 20, '#ffb000');
  boardTray(ctx, W, H, boil);
}

Object.assign(window.SCENES, { '7': scene7, '8': scene8, '9': scene9 });
window.Board = { boardBase, boardTray, magnet, sticky, mtext, M, arrow };
})();

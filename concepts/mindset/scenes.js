(() => {
// Style draft scenes for the mindset short-film channel (3 looks, 9:16).
const { h1, noise1, lerp, curve, brush, pencil, circlePts, blobFill, polyFill, grainCanvas, vignette, handText, limb, ik } = window.Ink;

// ---------- poses ----------
// Returns {lean, legs:[[thigh,shin],[..]], arms:[[upper,fore],[..]], tilt} ; index 0 = far side.
function poseRun(ph) {
  const legs = [], arms = [];
  for (let i = 0; i < 2; i++) {
    const p = ph + i * Math.PI;
    const th = 0.2 + 0.85 * Math.sin(p);
    legs.push([th, th - (0.25 + 1.35 * Math.max(0, Math.cos(p)))]);
    const up = -0.85 * Math.sin(p);
    arms.push([up, up + 1.55]);
  }
  return { lean: 0.32, legs, arms, tilt: -0.1, bob: Math.abs(Math.cos(ph)) };
}
function poseWalk(ph) {
  const legs = [], arms = [];
  for (let i = 0; i < 2; i++) {
    const p = ph + i * Math.PI;
    const th = 0.42 * Math.sin(p);
    legs.push([th, th - (0.08 + 0.55 * Math.max(0, Math.cos(p)))]);
    const up = -0.32 * Math.sin(p);
    arms.push([up, up + 0.3]);
  }
  return { lean: 0.07, legs, arms, tilt: 0.18, bob: Math.abs(Math.cos(ph)) * 0.4 };
}

// Build joint positions. feetY: ground y the lowest foot should touch.
function rig(x, feetY, S, pose, dir) {
  const T = 0.32 * S, TH = 0.235 * S, SH = 0.235 * S, UA = 0.165 * S, FA = 0.155 * S, R = 0.135 * S;
  let hip = [0, 0];
  const legs = pose.legs.map(([a, b]) => limb(hip, a, TH, b, SH, dir));
  const sh = [hip[0] + Math.sin(pose.lean) * T * dir, hip[1] - Math.cos(pose.lean) * T];
  const arms = pose.arms.map(([a, b]) => limb(sh, a + pose.lean * 0.3, UA, b + pose.lean * 0.3, FA, dir));
  const ha = pose.lean + pose.tilt;
  const head = [sh[0] + Math.sin(ha) * (R + 0.03 * S) * dir, sh[1] - Math.cos(ha) * (R + 0.03 * S)];
  const low = Math.max(...legs.map(l => l[2][1]));
  const dy = feetY - low - 0.012 * S;
  const mv = p => [p[0] + x, p[1] + dy];
  return {
    hip: mv(hip), sh: mv(sh), head: mv(head), R, S, dir,
    legs: legs.map(l => l.map(mv)), arms: arms.map(a => a.map(mv)),
  };
}

// ---------- figure painters ----------
function face(ctx, J, look, col, boil, opt = {}) {
  const { head: [cx, cy], R, dir } = J;
  const ex = opt.ex ?? 0.32, ey = opt.ey ?? -0.02;
  const eyes = [[cx + dir * R * (ex - 0.42), cy + R * ey], [cx + dir * R * (ex + 0.06), cy + R * ey]];
  const er = R * (opt.eyeR ?? 0.085);
  eyes.forEach(([x, y], i) => {
    if (look === 'tired') {
      brush(ctx, [[x - er * 1.5, y], [x + er * 1.5, y + 1]], { w: er * 0.9, color: col, seed: 50 + i, boil, wob: 0.6 });
    } else blobFill(ctx, x, y, er, col, 60 + i, boil);
    // brows
    const by = y - R * 0.27;
    let tiltIn = look === 'det' ? 0.22 : look === 'tired' ? -0.12 : 0.04;
    const inner = (i === 0 ? 1 : -1) * dir; // inner side direction
    const bx0 = x - inner * R * 0.16, bx1 = x + inner * R * 0.13;
    brush(ctx, [[bx0, by - R * tiltIn * 0.3], [bx1, by + R * tiltIn * 0.5]], { w: R * 0.075, color: col, seed: 70 + i, boil, wob: 0.8 });
  });
  if (opt.mouth) {
    const mx = cx + dir * R * 0.12, my = cy + R * 0.38;
    brush(ctx, [[mx - R * 0.12, my], [mx + R * 0.12, my + (look === 'det' ? 2 : 0)]], { w: R * 0.06, color: col, seed: 80, boil, wob: 0.6 });
  }
}

function figInk(ctx, J, boil, paper) {
  const w = 0.03 * J.S, c = '#151413';
  const st = (p, s, ww = w) => brush(ctx, p, { w: ww, color: c, seed: s, boil, wob: 1.2, taper: 14, pressure: 0.45 });
  st(J.arms[0], 11); st(J.legs[0], 12);
  st([J.hip, J.sh], 13, w * 1.15);
  st(J.legs[1], 14); st(J.arms[1], 15);
  blobFill(ctx, J.head[0], J.head[1], J.R * 0.98, paper, 3, boil);
  brush(ctx, circlePts(J.head[0], J.head[1], J.R, 21 + boil * 3), { w: w * 0.85, color: c, seed: 22, boil, wob: 0.9, taper: 30, pressure: 0.5 });
  face(ctx, J, 'det', c, boil);
}

function figCream(ctx, J, boil, pose) {
  const fr = '#efe6cf', bk = '#bdb39b', ww = 0.078 * J.S;
  const st = (p, s, col, w = ww) => brush(ctx, p, { w, color: col, seed: s, boil, wob: 0.9, noTaper: true, roundCaps: true, pressure: 0.12 });
  st(J.arms[0], 11, bk); st(J.legs[0], 12, bk);
  st([J.hip, J.sh], 13, fr, 0.13 * J.S);
  st(J.legs[1], 14, fr);
  blobFill(ctx, J.head[0], J.head[1], J.R, fr, 3, boil);
  st(J.arms[1], 15, fr, ww * 0.95);
  face(ctx, J, pose.look ?? 'det', '#2b2620', boil, { mouth: true });
}

function figPencil(ctx, J, boil, paper) {
  const c = '#33363d', w = 0.022 * J.S;
  const st = (p, s, ww = w) => pencil(ctx, p, { w: ww, color: c, seed: s, boil, wob: 1.0, taper: 8, alpha: 0.95, passes: 3 });
  st(J.arms[0], 11); st(J.legs[0], 12);
  st([J.hip, J.sh], 13, w * 1.1);
  st(J.legs[1], 14); st(J.arms[1], 15);
  blobFill(ctx, J.head[0], J.head[1], J.R * 0.97, paper, 3, boil);
  pencil(ctx, circlePts(J.head[0], J.head[1], J.R, 21 + boil * 3), { w: w * 0.8, color: c, seed: 22, boil, wob: 0.8, taper: 20, passes: 3 });
  face(ctx, J, 'calm', c, boil, { eyeR: 0.07 });
}

// ---------- scenes ----------
const G = {};
function grain(W, H, key, dark) { return G[key] || (G[key] = grainCanvas(W, H, key.length * 13 + 7, dark)); }

// A: black ink on warm paper, one red sun.
function sceneA(ctx, W, H, t) {
  const boil = Math.floor(t * 8), paper = '#f3eee4';
  ctx.fillStyle = paper; ctx.fillRect(0, 0, W, H);
  const gy = H * 0.63;
  // sun (rising very slowly)
  blobFill(ctx, W * 0.70, gy - 30 - t * 5, 200, '#e64a2e', 9, boil);
  // hill/ground
  const ground = curve([[-30, gy + 40], [W * 0.25, gy + 8], [W * 0.5, gy], [W * 0.8, gy + 14], [W + 30, gy + 50]], 12);
  polyFill(ctx, [...ground, [W + 30, H + 20], [-30, H + 20]], paper, 4, boil, 1);
  brush(ctx, ground, { w: 7, color: '#151413', seed: 5, boil, wob: 1.5, taper: 120 });
  // ground ticks scrolling (speed feel)
  for (let i = 0; i < 7; i++) {
    const x = ((i * 190 - t * 520) % (W + 300) + W + 300) % (W + 300) - 150;
    const y = gy + 70 + h1(i, 4) * 120;
    brush(ctx, [[x, y], [x + 40 + h1(i, 5) * 50, y + 1]], { w: 4, color: '#151413', seed: 30 + i, boil, wob: 0.8, alpha: 0.55 });
  }
  // runner, animated on twos (12 fps)
  const tq = Math.floor(t * 12) / 12;
  const J = rig(W * 0.34, gy + 6, 470, poseRun(tq * 10.5), 1);
  figInk(ctx, J, boil, paper);
  // text
  handText(ctx, '4:58 AM', W / 2, 300, { font: '52px PatrickHand', color: '#8c8579', boil, perChar: true });
  handText(ctx, "You don't need", W / 2, 430, { font: '700 104px Caveat', color: '#151413', boil, perChar: true });
  handText(ctx, 'to feel like it.', W / 2, 540, { font: '700 104px Caveat', color: '#151413', boil: boil + 1, perChar: true });
  ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(grain(W, H, 'paperA', false), 0, 0); ctx.globalCompositeOperation = 'source-over';
  vignette(ctx, W, H, 0.12, '60,40,20');
}

// B: dark room, cream figure, one amber light.
function sceneB(ctx, W, H, t) {
  const boil = Math.floor(t * 8), bg = '#0f0f11';
  ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
  const fy = H * 0.64, line = '#6b6b70';
  // window + faint light
  const wx = W * 0.12, wy = H * 0.33, ww = 210, wh = 250;
  ctx.save(); const lg = ctx.createLinearGradient(wx, wy, wx + 260, fy);
  lg.addColorStop(0, 'rgba(160,170,200,0.10)'); lg.addColorStop(1, 'rgba(160,170,200,0)');
  ctx.fillStyle = lg; ctx.beginPath(); ctx.moveTo(wx, wy + wh); ctx.lineTo(wx + ww, wy + wh); ctx.lineTo(wx + ww + 360, fy); ctx.lineTo(wx + 120, fy); ctx.fill(); ctx.restore();
  const box = (x, y, w, h, s) => brush(ctx, [[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y - 3]], { w: 5, color: line, seed: s, boil, wob: 1.2, taper: 10, noTaper: true });
  box(wx, wy, ww, wh, 1);
  brush(ctx, [[wx + ww / 2, wy], [wx + ww / 2, wy + wh]], { w: 4, color: line, seed: 2, boil });
  brush(ctx, [[wx, wy + wh / 2], [wx + ww, wy + wh / 2]], { w: 4, color: line, seed: 3, boil });
  blobFill(ctx, wx + ww * 0.75, wy + wh * 0.25, 16, '#cfd3dc', 4, boil);
  // floor
  brush(ctx, [[-20, fy], [W + 20, fy + 3]], { w: 4, color: line, seed: 5, boil, wob: 1.2, noTaper: true });
  // bed
  const bx0 = W * 0.02, bx1 = W * 0.50, by = fy - 150;
  polyFill(ctx, [[bx0, by], [bx1, by], [bx1, by + 60], [bx0, by + 60]], '#1c1d22', 6, boil);
  polyFill(ctx, [[bx0, by - 10], [bx1 - 70, by - 22], [bx1 - 40, by + 4], [bx0, by + 10]], '#2c3242', 7, boil, 3);
  box(bx0, by, bx1 - bx0, 60, 8);
  brush(ctx, [[bx0 + 20, by + 60], [bx0 + 20, fy]], { w: 5, color: line, seed: 9, boil });
  brush(ctx, [[bx1 - 20, by + 60], [bx1 - 20, fy]], { w: 5, color: line, seed: 10, boil });
  // alarm clock, amber
  const cx = W * 0.80, cyy = fy - 95, cw = 150, ch = 95;
  ctx.save(); const rg = ctx.createRadialGradient(cx + cw / 2, cyy + ch / 2, 10, cx + cw / 2, cyy + ch / 2, 330);
  rg.addColorStop(0, 'rgba(255,170,60,0.16)'); rg.addColorStop(1, 'rgba(255,170,60,0)'); ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H); ctx.restore();
  polyFill(ctx, [[cx, cyy], [cx + cw, cyy], [cx + cw, cyy + ch], [cx, cyy + ch]], '#18181b', 11, boil);
  box(cx, cyy, cw, ch, 12);
  const blink = (Math.floor(t * 2) % 2 === 0) || t < 0.5;
  ctx.save(); ctx.shadowColor = 'rgba(255,170,60,0.9)'; ctx.shadowBlur = 18;
  handText(ctx, blink ? '4:59' : '4:59', cx + cw / 2, cyy + 66, { font: '700 60px PatrickHand', color: blink ? '#ffb23e' : '#b9792a', boil });
  ctx.restore();
  // figure sitting on bed edge, tying shoe (built with IK)
  const S = 430, dir = 1, tq = Math.floor(t * 12) / 12;
  const hip = [bx1 - 55, by - 4];
  const lean = 0.85 + Math.sin(tq * 2.4) * 0.03;
  const sh = [hip[0] + Math.sin(lean) * 0.32 * S, hip[1] - Math.cos(lean) * 0.32 * S];
  const footF = [hip[0] + 0.30 * S, fy - 10], footB = [hip[0] + 0.12 * S, fy - 10];
  const legF = ik(hip, footF, 0.235 * S, 0.235 * S, -1), legB = ik(hip, footB, 0.235 * S, 0.235 * S, -1);
  const loop = tq * 9;
  const handF = [footF[0] - 0.01 * S + Math.cos(loop) * 0.025 * S, footF[1] - 0.075 * S + Math.sin(loop) * 0.02 * S];
  const handB = [footF[0] - 0.07 * S + Math.cos(loop + 2) * 0.02 * S, footF[1] - 0.06 * S + Math.sin(loop + 2) * 0.018 * S];
  const armF = ik(sh, handF, 0.165 * S, 0.155 * S, 1), armB = ik(sh, handB, 0.165 * S, 0.155 * S, 1);
  const ha = lean + 0.25, R = 0.135 * S;
  const head = [sh[0] + Math.sin(ha) * (R + 0.03 * S), sh[1] - Math.cos(ha) * (R + 0.03 * S)];
  const J = { hip, sh, head, R, S, dir, legs: [legB, legF], arms: [armB, armF] };
  figCream(ctx, J, boil, { look: 'det' });
  // shoe hints
  brush(ctx, [[footF[0] - 22, footF[1] + 8], [footF[0] + 34, footF[1] + 8]], { w: 16, color: '#efe6cf', seed: 40, boil, noTaper: true, roundCaps: true });
  // text
  handText(ctx, "Nobody's watching.", W / 2, 420, { font: '86px PatrickHand', color: '#efe6cf', boil, perChar: true });
  handText(ctx, 'Do it anyway.', W / 2, 530, { font: '86px PatrickHand', color: '#ffb23e', boil: boil + 1, perChar: true });
  ctx.drawImage(grain(W, H, 'darkB', true), 0, 0);
  vignette(ctx, W, H, 0.55);
}

// C: graphite pencil on cool paper, tiny figure in the rain, one blue.
function sceneC(ctx, W, H, t) {
  const boil = Math.floor(t * 8), paper = '#e8eaed', c = '#33363d', blue = '#2f6fe4';
  ctx.fillStyle = paper; ctx.fillRect(0, 0, W, H);
  const gy = H * 0.66;
  // rain (re-drawn on each boil step, falling)
  for (let i = 0; i < 120; i++) {
    const x = h1(i, 1) * (W + 200) - 100;
    const y = ((h1(i, 2) * H + Math.floor(t * 12) / 12 * 1500) % (H + 200)) - 100;
    const l = 30 + h1(i, 3) * 40;
    brush(ctx, [[x, y], [x - l * 0.25, y + l]], { w: 2.2, color: c, seed: i, boil, wob: 0.4, alpha: 0.35 });
  }
  // horizon
  pencil(ctx, curve([[-30, gy + 6], [W * 0.3, gy - 4], [W * 0.7, gy + 2], [W + 30, gy - 6]], 12), { w: 4, color: c, seed: 5, boil, wob: 1.6, taper: 80, passes: 3 });
  // puddle ahead, blue rings
  const px = W * 0.66, py = gy + 26;
  for (let k = 0; k < 2; k++) {
    const rr = 60 + ((t * 40 + k * 40) % 80);
    brush(ctx, circlePts(px, py, rr, 30 + k + boil, 0.2, 0.22), { w: 3, color: blue, seed: 31 + k, boil, wob: 0.6, alpha: 1 - ((t * 40 + k * 40) % 80) / 80, taper: 20 });
  }
  brush(ctx, circlePts(px, py, 52, 33, 0.25, 0.2), { w: 3.5, color: blue, seed: 34, boil, wob: 0.6, taper: 20 });
  // tiny walker
  const tq = Math.floor(t * 12) / 12;
  const J = rig(W * 0.40, gy + 2, 250, poseWalk(tq * 5.5), 1);
  figPencil(ctx, J, boil, paper);
  // text
  handText(ctx, 'DAY 37', W / 2, 320, { font: '56px PatrickHand', color: '#7b8089', boil, perChar: true });
  handText(ctx, 'Still raining.', W / 2, 450, { font: '700 100px Caveat', color: c, boil, perChar: true });
  handText(ctx, 'Still going.', W / 2, 560, { font: '700 100px Caveat', color: blue, boil: boil + 1, perChar: true });
  ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(grain(W, H, 'paperC', false), 0, 0); ctx.globalCompositeOperation = 'source-over';
  vignette(ctx, W, H, 0.10, '20,30,50');
}

window.SCENES = { A: sceneA, B: sceneB, C: sceneC };
window.draw = (name, t) => {
  const cv = document.getElementById('c'), ctx = cv.getContext('2d');
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  window.SCENES[name](ctx, cv.width, cv.height, t);
};
})();

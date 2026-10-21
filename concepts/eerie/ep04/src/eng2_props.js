// ---------- EP04: the living room in 3D, the security camera in its corner, and the thing under the sofa ----------
// World in metres. x: right as you face the back wall, y: up, z: out of the back wall into the room. Back wall z = 0 (sofa, front door), left wall x = x0 (window).
const ROOM = { x0: -2.4, x1: 2.4, y1: 2.5, z1: 4.2 };
const SOFA = { x0: -1.55, x1: 0.75, z0: 0.06, z1: 0.98, gap: 0.13, seat: 0.46, back: 0.92, arm: 0.64 };
const FDOOR = { x0: 1.25, x1: 2.1, h: 2.1 };                    // the front door, in the back wall
const WIN = { z0: 1.1, z1: 2.7, y0: 0.95, y1: 2.05 };            // the window, in the left wall
const LAMP = { x: 0.98, z: 0.3 };
const CHAIR = { x: -1.95, z: 3.35 };
const SPOT = { x: -0.65, z: 2.0 };                               // where you stand in the clip, on the rug in front of the sofa
const RUG = { x0: SPOT.x - 1.0, x1: SPOT.x + 0.95, z0: SPOT.z - 0.55, z1: SPOT.z + 0.75 };
const UI = 'I';
// the security camera: high in the front right corner, looking down across the room at the sofa
const CCTV = { x: 2.22, y: 2.36, z: 4.02 };
const CAMS = {
  cctv: { x: CCTV.x, y: CCTV.y, z: CCTV.z, yaw: 0.72, pitch: -0.47, f: 930 },
  sofa: { x: CCTV.x, y: CCTV.y, z: CCTV.z, yaw: 0.52, pitch: -0.5, f: 980 },          // turned to point straight at the sofa (rule 4)
  side: { x: 2.0, y: 1.25, z: 3.4, yaw: 0.62, pitch: -0.12, f: 900 },                 // a person's height, across the room
  chair: { x: 0.4, y: 1.3, z: 2.5, yaw: 1.95, pitch: -0.24, f: 1050 },                // across the room at the chair by the window
  low: { x: 1.1, y: 0.32, z: 3.0, yaw: 0.35, pitch: -0.02, f: 1100 },                 // down on the floor, looking under the sofa
};
let CAM = null;
function setCam(c) { CAM = { ...c, cyw: Math.cos(c.yaw || 0), syw: Math.sin(c.yaw || 0), cp: Math.cos(c.pitch || 0), sp: Math.sin(c.pitch || 0) }; }
const lerpCam = (a, b, k) => { const o = {}; for (const key of ['x', 'y', 'z', 'yaw', 'pitch', 'f']) o[key] = lerp(a[key], b[key], k); return o; };
setCam(CAMS.cctv);
const V3 = { add: (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], sub: (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], mul: (a, k) => [a[0] * k, a[1] * k, a[2] * k],
  dot: (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2], len: a => Math.hypot(a[0], a[1], a[2]), lerp: (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)] };
V3.norm = a => V3.mul(a, 1 / (V3.len(a) || 1));
// camera space: right, up, depth (forward is -z at yaw 0; positive yaw turns left, positive pitch looks up)
function toCam(p) {
  const dx = p[0] - CAM.x, dy = p[1] - CAM.y, dz = p[2] - CAM.z;
  const xc = dx * CAM.cyw - dz * CAM.syw, f0 = -dx * CAM.syw - dz * CAM.cyw;
  return [xc, dy * CAM.cp - f0 * CAM.sp, f0 * CAM.cp + dy * CAM.sp];
}
const camToScr = c => { const s = CAM.f / c[2]; return [W / 2 + c[0] * s, H / 2 - c[1] * s, c[2], s]; };
function prj(p) { const c = toCam(p); return c[2] < 0.03 ? null : camToScr(c); }
const camPos = () => [CAM.x, CAM.y, CAM.z];
function polyW(pts, fill, stroke, lw = 2) {
  let cs = pts.map(toCam); const N = 0.05, out = [];
  for (let i = 0; i < cs.length; i++) { const a = cs[i], b = cs[(i + 1) % cs.length];
    if (a[2] >= N) out.push(a);
    if ((a[2] >= N) !== (b[2] >= N)) { const k = (N - a[2]) / (b[2] - a[2]); out.push([lerp(a[0], b[0], k), lerp(a[1], b[1], k), N]); } }
  if (out.length < 3) return null;
  const sp = out.map(camToScr); ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.stroke(); }
  return sp;
}
function lnW(a, b, w, col) { const ca = toCam(a), cb = toCam(b); const N = 0.05; if (ca[2] < N && cb[2] < N) return;
  let A = ca, B = cb; if (A[2] < N) { const k = (N - A[2]) / (B[2] - A[2]); A = [lerp(A[0], B[0], k), lerp(A[1], B[1], k), N]; }
  if (B[2] < N) { const k = (N - B[2]) / (A[2] - B[2]); B = [lerp(B[0], A[0], k), lerp(B[1], A[1], k), N]; }
  const p = camToScr(A), q = camToScr(B); ln(p[0], p[1], q[0], q[1], w, col); }
function ringPts(c, u, v, n = 28) { const out = []; for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; out.push(V3.add(c, V3.add(V3.mul(u, Math.cos(a)), V3.mul(v, Math.sin(a))))); } return out; }
// a box: only the faces turned toward the camera, far ones first. cols: { top, side, front, edge }
function box3(x0, x1, y0, y1, z0, z1, cols) {
  const c = camPos(), F = [];
  F.push({ n: [0, 1, 0], ctr: [(x0 + x1) / 2, y1, (z0 + z1) / 2], p: [[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]], col: cols.top });
  F.push({ n: [0, 0, 1], ctr: [(x0 + x1) / 2, (y0 + y1) / 2, z1], p: [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], col: cols.front });
  F.push({ n: [0, 0, -1], ctr: [(x0 + x1) / 2, (y0 + y1) / 2, z0], p: [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]], col: cols.front });
  F.push({ n: [1, 0, 0], ctr: [x1, (y0 + y1) / 2, (z0 + z1) / 2], p: [[x1, y0, z0], [x1, y0, z1], [x1, y1, z1], [x1, y1, z0]], col: cols.side });
  F.push({ n: [-1, 0, 0], ctr: [x0, (y0 + y1) / 2, (z0 + z1) / 2], p: [[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]], col: cols.side });
  F.push({ n: [0, -1, 0], ctr: [(x0 + x1) / 2, y0, (z0 + z1) / 2], p: [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], col: cols.side });
  const vis = F.filter(f => V3.dot(f.n, V3.sub(c, f.ctr)) > 0).sort((a, b) => V3.len(V3.sub(c, b.ctr)) - V3.len(V3.sub(c, a.ctr)));
  for (const f of vis) polyW(f.p, f.col, cols.edge || '#4a4a4e', 2);
}

// ---------- the room ----------
const WALL_C = '#141416', SIDE_C = '#101012', FLOOR_C = '#19191a', EDGE_C = '#2e2e31';
// o.night 0..1 (the window), o.sun 0..1 (sunrise through the window), o.lamp 0..1 (the floor lamp is on), o.doorOpen 0..1
function room4(t, o = {}) {
  const { x0, x1, y1, z1 } = ROOM, sun = o.sun || 0;
  polyW([[x0, 0, 0], [x1, 0, 0], [x1, 0, z1], [x0, 0, z1]], FLOOR_C, EDGE_C, 2);
  for (let z = 0.5; z < z1; z += 0.5) lnW([x0, 0, z], [x1, 0, z], 1.5, '#222224');
  polyW([[x0, 0, 0], [x1, 0, 0], [x1, y1, 0], [x0, y1, 0]], WALL_C, EDGE_C, 2);
  polyW([[x0, 0, 0], [x0, 0, z1], [x0, y1, z1], [x0, y1, 0]], SIDE_C, EDGE_C, 2);
  polyW([[x1, 0, 0], [x1, 0, z1], [x1, y1, z1], [x1, y1, 0]], SIDE_C, EDGE_C, 2);
  polyW([[x0, y1, 0], [x1, y1, 0], [x1, y1, z1], [x0, y1, z1]], '#0a0a0b', EDGE_C, 2);
  for (const z of [0, z1]) lnW([x0, 0.1, z], [x1, 0.1, z], 2, '#2a2a2d');   // skirting
  // the window in the left wall: night blue, or the sunrise
  const wp = [[x0 + 0.005, WIN.y0, WIN.z0], [x0 + 0.005, WIN.y0, WIN.z1], [x0 + 0.005, WIN.y1, WIN.z1], [x0 + 0.005, WIN.y1, WIN.z0]];
  polyW(wp, sun > 0 ? `rgb(${Math.round(lerp(22, 255, sun))},${Math.round(lerp(26, 196, sun))},${Math.round(lerp(40, 140, sun))})` : '#16202c', '#5a5a60', 4);
  lnW([x0 + 0.01, WIN.y0, (WIN.z0 + WIN.z1) / 2], [x0 + 0.01, WIN.y1, (WIN.z0 + WIN.z1) / 2], 4, '#5a5a60');
  lnW([x0 + 0.01, (WIN.y0 + WIN.y1) / 2, WIN.z0], [x0 + 0.01, (WIN.y0 + WIN.y1) / 2, WIN.z1], 4, '#5a5a60');
  if (sun > 0) { ctx.save(); ctx.globalAlpha *= 0.5 * sun; ctx.globalCompositeOperation = 'screen';   // the light falling across the floor
    polyW([[x0, 0.002, WIN.z0], [x0, 0.002, WIN.z1], [x0 + 2.6, 0.002, WIN.z1 + 0.9], [x0 + 2.6, 0.002, WIN.z0 + 0.6]], '#ffc98a', null); ctx.restore(); }
  else if ((o.moon ?? 1) > 0) { const m = prj([x0 + 0.01, 1.78, WIN.z0 + 0.35]); if (m) { ctx.save(); glow('rgba(200,215,255,0.6)', 18); circ(m[0], m[1], 0.07 * m[3], '#c8d4e6'); ctx.restore(); } }
  // the front door in the back wall
  const op = o.doorOpen || 0, dz = 0.005;
  if (op > 0.01) polyW([[FDOOR.x0, 0, dz], [FDOOR.x1, 0, dz], [FDOOR.x1, FDOOR.h, dz], [FDOOR.x0, FDOOR.h, dz]], '#000', null);
  if (o.inDoor) o.inDoor();
  const a = op * 1.4, w = FDOOR.x1 - FDOOR.x0, ex = FDOOR.x1 - w * Math.cos(a), ez = dz + w * Math.sin(a);
  polyW([[FDOOR.x1, 0.01, dz], [ex, 0.01, ez], [ex, FDOOR.h - 0.01, ez], [FDOOR.x1, FDOOR.h - 0.01, dz]], '#202023', '#4c4c50', 3);
  const kp = prj([lerp(FDOOR.x1, ex, 0.88), 1.0, lerp(dz, ez, 0.88) + 0.02]); if (kp) circ(kp[0], kp[1], 0.03 * kp[3], '#77777c');
  polyW([[FDOOR.x0 - 0.06, 0, dz], [FDOOR.x0, 0, dz], [FDOOR.x0, FDOOR.h, dz], [FDOOR.x1, FDOOR.h, dz], [FDOOR.x1, 0, dz], [FDOOR.x1 + 0.06, 0, dz], [FDOOR.x1 + 0.06, FDOOR.h + 0.06, dz], [FDOOR.x0 - 0.06, FDOOR.h + 0.06, dz]], '#2a2a2d', '#55555a', 2);
  // the rug
  const rg = o.rug ?? 1, rx0 = lerp(RUG.x1, RUG.x0, rg);   // o.rug: how much of it still lies flat (it rolls up from the left)
  if (rg > 0.01) polyW([[rx0, 0.004, RUG.z0], [RUG.x1, 0.004, RUG.z0], [RUG.x1, 0.004, RUG.z1], [rx0, 0.004, RUG.z1]], '#202022', '#38383c', 2);
  lamp4(o.lamp ?? 0);
}
function lamp4(on) {
  const { x, z } = LAMP;
  polyW(ringPts([x, 0.01, z], [0.16, 0, 0], [0, 0, 0.16]), '#2a2a2d', '#4a4a4e', 2);
  lnW([x, 0.02, z], [x, 1.45, z], 5, '#5a5a5e');
  const top = [x, 1.62, z], bot = [x, 1.38, z];
  if (on > 0) { const p = prj([x, 1.45, z]); if (p) { ctx.save(); ctx.globalAlpha *= on; const g = ctx.createRadialGradient(p[0], p[1], 4, p[0], p[1], 0.9 * p[3]); g.addColorStop(0, 'rgba(255,226,170,0.5)'); g.addColorStop(1, 'rgba(255,226,170,0)'); ctx.fillStyle = g; ctx.fillRect(p[0] - 0.9 * p[3], p[1] - 0.9 * p[3], 1.8 * p[3], 1.8 * p[3]); ctx.restore(); } }
  polyW([...ringPts(bot, [0.23, 0, 0], [0, 0, 0.23], 16).slice(0, 9), ...ringPts(top, [0.15, 0, 0], [0, 0, 0.15], 16).slice(0, 9).reverse()], on > 0 ? '#e8dcc4' : '#3a3a3e', '#5a5a5e', 2);
}
// the sofa: legs, the dark gap under it, seat, back, arms
const SOFA_C = { top: '#3a3a3f', side: '#2a2a2e', front: '#303035', edge: '#58585e' };
function sofa4(o = {}) {
  const { x0, x1, z0, z1, gap, seat, back, arm } = SOFA, sh = o.shift || 0;   // shift: it moves, only a little
  ctx.save(); if (sh) ctx.translate(Math.sin(sh * 40) * 3 * sh, 0);
  for (const [lx, lz] of [[x0 + 0.08, z1 - 0.08], [x1 - 0.08, z1 - 0.08], [x0 + 0.08, z0 + 0.08], [x1 - 0.08, z0 + 0.08]]) box3(lx - 0.03, lx + 0.03, 0, gap, lz - 0.03, lz + 0.03, { top: '#444', side: '#333', front: '#3a3a3a', edge: '#555' });
  box3(x0, x1, gap, seat, z0, z1, SOFA_C);
  box3(x0, x1, seat, back, z0, z0 + 0.24, SOFA_C);
  box3(x0, x0 + 0.2, seat, arm, z0, z1, SOFA_C); box3(x1 - 0.2, x1, seat, arm, z0, z1, SOFA_C);
  // two cushions
  for (const cx of [x0 + 0.2, (x0 + x1) / 2]) box3(cx + 0.02, cx + (x1 - x0 - 0.4) / 2 - 0.02, seat, seat + 0.07, z0 + 0.26, z1 - 0.02, { top: '#45454a', side: '#333337', front: '#3b3b40', edge: '#5e5e64' });
  ctx.restore();
}
// the chair by the window, with the grey hoodie on it (o.hoodie: 'hang' | 'folded' | null)
function chair4(o = {}) {
  const { x, z } = CHAIR, cc = { top: '#333336', side: '#28282b', front: '#2e2e31', edge: '#55555a' };
  for (const [dx, dz] of [[-0.2, -0.2], [0.2, -0.2], [-0.2, 0.2], [0.2, 0.2]]) box3(x + dx - 0.02, x + dx + 0.02, 0, 0.45, z + dz - 0.02, z + dz + 0.02, cc);
  box3(x - 0.24, x + 0.24, 0.45, 0.5, z - 0.24, z + 0.24, cc);
  box3(x - 0.24, x - 0.2, 0.5, 1.0, z - 0.24, z + 0.24, cc);
  if (o.hoodie === 'hang') { const p = prj([x - 0.16, 0.74, z]); if (p) { const k = p[3] / 260;   // the grey hoodie over the chair back: hood, sleeves hanging
    ctx.save(); ctx.translate(p[0], p[1]); ctx.scale(k, k); glow('rgba(255,255,255,0.25)', 14);
    pth('M-70,-40 C-60,-80 60,-80 70,-40 L84,70 L56,74 L52,-6 L52,90 L-52,90 L-52,-6 L-56,74 L-84,70 Z', HOOD_C); noGlow();
    ell(0, -44, 26, 20, 0, '#55555a'); ln(-12, -20, -15, 18, 4, '#6a6a70'); ln(12, -20, 15, 18, 4, '#6a6a70'); rr(-30, 40, 60, 26, 8, '#87878d'); ctx.restore(); } }
  if (o.hoodie === 'folded') { box3(x - 0.17, x + 0.17, 0.5, 0.58, z - 0.15, z + 0.15, { top: '#b4b4ba', side: '#88888e', front: '#949499', edge: '#c4c4ca' });
    const p = prj([x, 0.585, z]); if (p) { const k = p[3]; ctx.save(); glow('rgba(255,255,255,0.2)', 8); ell(p[0], p[1], 0.07 * k, 0.03 * k, 0, '#9a9aa0'); ctx.restore(); } }
}
// the camera itself (a small dome on a bracket), for shots that see it. yaw: where it points; led: '#fff' | red
function cctv4(o = {}) {
  const { x, y, z } = CCTV, p = prj([x, y, z]); if (!p) return;
  const s = p[3]; ctx.save(); glow('rgba(255,255,255,0.15)', 10);
  rr(p[0] - 0.04 * s, p[1] - 0.12 * s, 0.08 * s, 0.1 * s, 0.01 * s, '#d8d8dc');
  ell(p[0], p[1], 0.1 * s, 0.075 * s, 0, '#e8e8ec'); noGlow();
  const a = o.dir ?? 2.6; circ(p[0] + Math.cos(a) * 0.04 * s, p[1] + Math.sin(a) * 0.03 * s + 0.01 * s, 0.035 * s, '#111');
  circ(p[0] + Math.cos(a) * 0.04 * s, p[1] + Math.sin(a) * 0.03 * s + 0.01 * s, 0.014 * s, '#3a4a5a');
  ctx.save(); if (o.led === 'red') redGlow(12); else glow('rgba(160,255,190,0.9)', 8); circ(p[0] + 0.06 * s, p[1] - 0.03 * s, 0.012 * s, o.led === 'red' ? C.red : '#9effc0'); ctx.restore();
  ctx.restore();
}

// ---------- people (from EP03: a 3D pictogram) ----------
const HOOD_C = '#9b9ba1';
const STAND = { L: [-0.22, 0.8, 0.02], R: [0.22, 0.8, 0.02] };
// a hand at a world point, as the local [side, height, forward] that poseOf's L/R take
function handAt(ps, w) { const yaw = ps.yaw || 0, F = [-Math.sin(yaw), 0, -Math.cos(yaw)], R = [Math.cos(yaw), 0, -Math.sin(yaw)], dx = w[0] - ps.x, dz = w[2] - ps.z; return [R[0] * dx + R[2] * dz, w[1], F[0] * dx + F[2] * dz]; }
function poseOf(p) { return { x: SPOT.x, z: SPOT.z, yaw: 0, lean: 0, look: 0, roll: 0, ...STAND, ...p }; }
function skeleton(ps) {
  const yaw = ps.yaw || 0, F = [-Math.sin(yaw), 0, -Math.cos(yaw)], R = [Math.cos(yaw), 0, -Math.sin(yaw)];
  const Wd = (lx, ly, lz) => [ps.x + R[0] * lx + F[0] * lz, ly, ps.z + R[2] * lx + F[2] * lz];
  const hipY = 0.95, la = ps.lean || 0, cr = ps.crouch || 0, drop = 0.42 * cr;
  const up = (lx, ly, lz = 0) => { const dy = ly - hipY; return Wd(lx, hipY - drop + dy * Math.cos(la) - lz * Math.sin(la), lz * Math.cos(la) + dy * Math.sin(la)); };
  const look = ps.look || 0, roll = ps.roll || 0;
  const head = up(0.05 * roll, 1.63 - 0.035 * look - 0.012 * Math.abs(roll), 0.045 * look);
  const j = { look, F, R, head, neck: up(0, 1.47), chest: up(0, 1.36), pelvis: up(0, 1.02), sh: { L: up(-0.19, 1.42), R: up(0.19, 1.42) } };
  j.hand = { L: Wd(...ps.L), R: Wd(...ps.R) };
  j.elb = {};
  for (const [s, sg] of [['L', -1], ['R', 1]]) { const S = j.sh[s], Hh = j.hand[s], d = V3.sub(Hh, S), L = V3.len(d), B = 0.31;
    const mid = V3.lerp(S, Hh, 0.5); let bend = V3.add(V3.mul(R, sg * 0.7), V3.add([0, -0.55, 0], V3.mul(F, -0.45)));
    const dn = V3.norm(d); bend = V3.norm(V3.sub(bend, V3.mul(dn, V3.dot(bend, dn))));
    j.elb[s] = L >= 2 * B ? mid : V3.add(mid, V3.mul(bend, Math.sqrt(B * B - L * L / 4))); }
  const ph = ps.step || 0, sw = ps.walk ? 0.22 : 0;
  j.hip = { L: Wd(-0.09, 0.95 - drop, 0), R: Wd(0.09, 0.95 - drop, 0) };
  j.foot = { L: Wd(-0.1, 0.04 + Math.max(0, Math.sin(ph)) * 0.06 * (sw > 0), Math.cos(ph) * sw + 0.03), R: Wd(0.1, 0.04 + Math.max(0, -Math.sin(ph)) * 0.06 * (sw > 0), -Math.cos(ph) * sw + 0.03) };
  if (ps.footL) j.foot.L = ps.footL;
  const kf = V3.add(V3.mul(F, 0.03 + 0.3 * cr), [0, 0.12 * cr, 0]);   // crouched: the knees come forward and up
  j.knee = { L: V3.add(V3.lerp(j.hip.L, j.foot.L, 0.5), kf), R: V3.add(V3.lerp(j.hip.R, j.foot.R, 0.5), kf) };
  return j;
}
// o.col: skin, o.top: the hoodie (torso and sleeves), o.legs: trousers, o.hood: a hoodie with its hood, strings, pocket and cuffs, o.mark: a red box round the hoodie
const LEG_C = '#6a6a70', SHOE_C = '#2a2a2e', HOOD_EDGE = '#5e5e64';
function body3(ps, o = {}) {
  const j = skeleton(ps), col = o.col || C.fig, top = o.top || col, flat = !!o.flat, legs = flat ? col : (o.legs || LEG_C);
  const fd = V3.dot(j.F, V3.norm(V3.sub(camPos(), j.chest)));   // > 0: facing the camera
  const parts = [], P = q => prj(q);
  const cap = (a, b, w, c = col, d) => parts.push({ d: d ?? (toCam(a)[2] + toCam(b)[2]) / 2, f: () => { const p = P(a), q = P(b); if (p && q) ln(p[0], p[1], q[0], q[1], w * (p[3] + q[3]) / 2, c); } });
  const quad = (pts, fill, edge, d) => parts.push({ d, f: () => { const sp = pts.map(P); if (sp.some(x => !x)) return; ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); if (edge) { ctx.lineJoin = 'round'; ctx.strokeStyle = edge; ctx.lineWidth = 2; ctx.stroke(); } } });
  // legs (trousers) and shoes
  for (const s of ['L', 'R']) { cap(j.hip[s], j.knee[s], 0.14, legs); cap(j.knee[s], j.foot[s], 0.12, legs);
    if (!flat) parts.push({ d: toCam(j.foot[s])[2] - 0.01, f: () => { const f0 = P(j.foot[s]), f1 = P(V3.add(j.foot[s], V3.mul(j.F, 0.13))); if (!f0 || !f1) return;
      ln(f0[0], f0[1], f1[0], f1[1], 0.1 * f0[3], SHOE_C); ln(f0[0], f0[1] + 0.03 * f0[3], f1[0], f1[1] + 0.03 * f0[3], 0.025 * f0[3], '#77777c'); } }); }
  // the hoodie body: a real torso shape, wider at the shoulders, a ribbed band at the hem
  const sw = 0.22, hw = 0.17, dc = toCam(j.chest)[2] + 0.02;
  const shL = V3.add(j.sh.L, V3.mul(j.R, -0.03)), shR = V3.add(j.sh.R, V3.mul(j.R, 0.03)), hipL = V3.add(j.pelvis, V3.mul(j.R, -hw)), hipR = V3.add(j.pelvis, V3.mul(j.R, hw));
  quad([V3.add(shL, [0, 0.03, 0]), V3.add(shR, [0, 0.03, 0]), V3.add(hipR, [0, -0.04, 0]), V3.add(hipL, [0, -0.04, 0])], top, flat ? null : HOOD_EDGE, dc);
  if (!flat && o.hood) {
    const band = (y0, y1) => quad([V3.add(hipL, [0, y0, 0]), V3.add(hipR, [0, y0, 0]), V3.add(hipR, [0, y1, 0]), V3.add(hipL, [0, y1, 0])], '#a4a4aa', null, dc - 0.001);
    band(-0.04, 0.0);
    if (fd > 0.15) {   // the front: the kangaroo pocket and the two strings
      const pc = V3.add(V3.lerp(j.chest, j.pelvis, 0.72), V3.mul(j.F, 0.1));
      quad([V3.add(pc, V3.add(V3.mul(j.R, -0.11), [0, 0.07, 0])), V3.add(pc, V3.add(V3.mul(j.R, 0.11), [0, 0.07, 0])), V3.add(pc, V3.add(V3.mul(j.R, 0.14), [0, -0.07, 0])), V3.add(pc, V3.add(V3.mul(j.R, -0.14), [0, -0.07, 0]))], '#8e8e94', HOOD_EDGE, dc - 0.002);
      for (const sg of [-1, 1]) { const a = V3.add(j.neck, V3.add(V3.mul(j.R, sg * 0.04), V3.mul(j.F, 0.09))), b = V3.add(a, [sg * 0.005, -0.17, 0]);
        parts.push({ d: dc - 0.003, f: () => { const p = P(a), q = P(b); if (p && q) { ln(p[0], p[1], q[0], q[1], 0.012 * p[3], '#e8e8ec'); circ(q[0], q[1], 0.012 * q[3], '#e8e8ec'); } } }); }
    }
    // the hood: lying on the back, seen from behind; a rim round the neck from the front
    const hb = V3.add(j.neck, V3.add(V3.mul(j.F, -0.06), [0, -0.06, 0]));
    parts.push({ d: fd > 0.15 ? toCam(j.head)[2] + 0.05 : toCam(j.chest)[2] - 0.05, f: () => { const p = P(hb); if (!p) return; const r = p[3];
      ctx.save(); ctx.beginPath(); ctx.ellipse(p[0], p[1], 0.13 * r, 0.09 * r, 0, 0, Math.PI * 2); ctx.fillStyle = '#929298'; ctx.fill(); ctx.strokeStyle = HOOD_EDGE; ctx.lineWidth = 2; ctx.stroke();
      ln(p[0] - 0.09 * r, p[1] - 0.02 * r, p[0] + 0.09 * r, p[1] - 0.02 * r, 2, HOOD_EDGE); ctx.restore(); } });
  }
  cap(j.neck, j.chest, 0.08);
  for (const s of ['L', 'R']) { cap(j.sh[s], j.elb[s], 0.1, top); cap(j.elb[s], j.hand[s], 0.09, top);
    if (!flat && o.hood) { const c0 = V3.lerp(j.elb[s], j.hand[s], 0.86); cap(c0, V3.lerp(j.elb[s], j.hand[s], 0.97), 0.095, '#8a8a90', toCam(c0)[2] - 0.003); }
    parts.push({ d: toCam(j.hand[s])[2] - 0.004, f: () => { const p = P(j.hand[s]); if (p) circ(p[0], p[1], 0.05 * p[3], col); } }); }
  parts.push({ d: toCam(j.head)[2], f: () => head3(j, col, o) });
  if (o.knife) { const dir = V3.norm(o.knifeDir || V3.sub(j.hand.R, j.elb.R)), h = j.hand.R;   // a kitchen knife in the right hand
    parts.push({ d: toCam(h)[2] - 0.006, f: () => knife3(h, dir, o.knife) }); }
  if (o.mark) parts.push({ d: -1, f: () => { const c = P(V3.lerp(j.chest, j.pelvis, 0.4)); if (c) { noGlow(); redGlow(16); rrS(c[0] - 0.26 * c[3], c[1] - 0.4 * c[3], 0.52 * c[3], 0.8 * c[3], 8, C.red, 4); noGlow(); } } });
  parts.sort((a, b) => b.d - a.d);
  ctx.save(); glow(o.glow || 'rgba(255,255,255,0.22)', 14); for (const p of parts) { ctx.save(); p.f(); ctx.restore(); } ctx.restore();
  return j;
}
function head3(j, col, o) {
  const p = prj(j.head); if (!p) return; const r = 0.11 * p[3];
  circ(p[0], p[1], r, col); noGlow();
  const fd = V3.dot(j.F, V3.norm(V3.sub(camPos(), j.head)));
  ctx.save(); ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.clip();
  const side = prj(V3.add(j.head, V3.mul(j.F, 0.05))), sx = side ? (side[0] - p[0]) : 0;
  const up = lerp(0.0, 0.78, (fd + 1) / 2) * r;
  circ(p[0] - sx * 0.9 * (1 - fd * fd), p[1] - up, r * 1.02, o.hair || '#4a4a50');
  if (fd < 0.2) for (let i = -2; i <= 2; i++) ln(p[0] + i * r * 0.28, p[1] - r, p[0] + i * r * 0.34, p[1] + r * 0.2, 1.5, '#38383d');   // strands of hair from behind
  ctx.restore();
  if (fd > 0.15) { const a = clamp((fd - 0.15) / 0.3);   // a face toward the camera always shows both eyes
    for (const sg of [-1, 1]) { const e = prj(V3.add(j.head, V3.add(V3.mul(j.F, 0.1), V3.add(V3.mul(j.R, sg * 0.042), [0, 0.005 - 0.05 * (j.look || 0), 0])))); if (!e) continue;
      ctx.save(); ctx.globalAlpha *= a; ell(e[0], e[1], 0.014 * e[3], (o.blink ? 0.003 : 0.018) * e[3], 0, o.eye || '#000'); ctx.restore(); } }
}
// someone lying on the floor, feet toward (fx, fz), head toward the direction a (radians in the floor plane).
// o.clipZ: only what is in front of that z is drawn (the rest has gone under the sofa); o.reach 0..1 arms stretched past the head, clawing
function lying3(fx, fz, a, o = {}) {
  const col = o.col || C.fig, top = o.top || col, legs = o.flat ? col : (o.legs || LEG_C), u = [Math.sin(a), 0, Math.cos(a)], r = [Math.cos(a), 0, -Math.sin(a)];
  const P = (along, side, y = 0.08) => [fx + u[0] * along + r[0] * side, y, fz + u[2] * along + r[2] * side];
  const cz = o.clipZ ?? -99;
  const cut = (A, B) => { if (A[2] < cz && B[2] < cz) return null; if (A[2] >= cz && B[2] >= cz) return [A, B]; const k = (cz - A[2]) / (B[2] - A[2]), M = V3.lerp(A, B, k); return A[2] < cz ? [M, B] : [A, M]; };
  const cap = (A, B, w, c) => { const ab = cut(A, B); if (!ab) return; const p = prj(ab[0]), q = prj(ab[1]); if (p && q) ln(p[0], p[1], q[0], q[1], w * (p[3] + q[3]) / 2, c); };
  const wig = o.wig || 0, rc = o.reach ?? 0;
  ctx.save(); glow('rgba(255,255,255,0.2)', 12);
  cap(P(0, -0.1), P(0.5, -0.09), 0.13, legs); cap(P(0.02, 0.1), P(0.5, 0.09), 0.13, legs);
  if (!o.flat) for (const sd of [-0.1, 0.1]) cap(P(-0.04, sd, 0.06), P(0.06, sd, 0.06), 0.1, SHOE_C);
  cap(P(0.5, 0, 0.11), P(1.05, 0, 0.12), 0.3, top);
  if (!o.flat && o.hood !== false) cap(P(0.5, 0, 0.12), P(0.56, 0, 0.12), 0.31, '#8a8a90');
  // arms flung up past the head, fingers clawing at the floor
  for (const sg of [-1, 1]) { const s0 = P(1.0, sg * 0.19, 0.1), e = P(1.0 + 0.3 + 0.18 * rc, sg * (0.3 + 0.06 * Math.sin(wig + sg)), 0.06), h = P(1.0 + 0.48 + 0.25 * rc, sg * (0.28 + 0.08 * Math.sin(wig * 1.3 + sg)), 0.03);
    cap(s0, e, 0.09, top); cap(e, h, 0.085, top); const ab = cut(h, h); if (ab) { const hp = prj(h); if (hp) circ(hp[0], hp[1], 0.05 * hp[3], col); } }
  const hc = P(1.27, 0, 0.11); if (hc[2] >= cz) { const h = prj(hc); if (h) { circ(h[0], h[1], 0.11 * h[3], col); circ(h[0], h[1] - 0.03 * h[3], 0.1 * h[3], '#4a4a50'); } }
  ctx.restore();
}

// a kitchen knife held at h, the blade along dir; k: 0..1 it appears (a glint runs along the blade)
function knife3(h, dir, k = 1) {
  const a = V3.sub(h, V3.mul(dir, 0.07)), b = V3.add(h, V3.mul(dir, 0.04)), tip = V3.add(h, V3.mul(dir, 0.4));
  const pa = prj(a), pb = prj(b), pt = prj(tip); if (!pa || !pb || !pt) return;
  ctx.save(); ctx.globalAlpha *= clamp(k); noGlow();
  ln(pa[0], pa[1], pb[0], pb[1], 0.032 * pb[3], '#1c1c1e');
  const dx = pt[0] - pb[0], dy = pt[1] - pb[1], L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L, w = 0.036 * pb[3];
  glow('rgba(255,255,255,0.5)', 12);
  pth(`M${pb[0] + nx * w},${pb[1] + ny * w} L${pt[0]},${pt[1]} L${pb[0] - nx * w * 0.3},${pb[1] - ny * w * 0.3} Z`, '#e4e4e8'); noGlow();
  ln(pb[0] + nx * w * 0.3, pb[1] + ny * w * 0.3, lerp(pb[0], pt[0], 0.9), lerp(pb[1], pt[1], 0.9), 1.5, '#9a9aa0');
  if (k < 1.6) { const g = clamp(k - 0.2); const gx = lerp(pb[0], pt[0], g), gy = lerp(pb[1], pt[1], g); ctx.globalAlpha *= 1 - clamp(k - 0.6); glow('rgba(255,255,255,0.9)', 18); circ(gx, gy, 5, '#fff'); }
  ctx.restore();
}
// a solid cylinder between world points a and b (the rolled-up rug): its outline, and the round end that faces the camera, rolled up in a spiral
function cyl3(a, b, r, col, edge, endCol) {
  const d = V3.norm(V3.sub(b, a)); let u = [d[2], 0, -d[0]]; if (V3.len(u) < 0.1) u = [1, 0, 0]; u = V3.norm(u);
  const v = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]];
  const ra = ringPts(a, V3.mul(u, r), V3.mul(v, r), 20), rb = ringPts(b, V3.mul(u, r), V3.mul(v, r), 20);
  const sp = [...ra, ...rb].map(prj); if (sp.some(q => !q)) return;
  const pts = sp.map(q => [q[0], q[1]]).sort((p, q) => p[0] - q[0] || p[1] - q[1]), cr = (o, p, q) => (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0]);
  const lo = [], hi = []; for (const p of pts) { while (lo.length > 1 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); }
  for (const p of pts.slice().reverse()) { while (hi.length > 1 && cr(hi[hi.length - 2], hi[hi.length - 1], p) <= 0) hi.pop(); hi.push(p); }
  const hull = lo.slice(0, -1).concat(hi.slice(0, -1));
  ctx.beginPath(); hull.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); ctx.fillStyle = col; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = edge; ctx.stroke();
  const c = V3.sub(camPos(), b), end = V3.dot(d, c) > 0 ? b : a, ring = end === b ? rb : ra;
  polyW(ring, endCol || col, edge, 2);
  for (const k of [0.68, 0.4, 0.15]) polyW(ringPts(end, V3.mul(u, r * k), V3.mul(v, r * k), 16), null, edge, 1.5);
}
// the bait: the rug rolled up (o.roll), stood up where you stood (o.stand) with the grey hoodie on it (o.hood); o.pos [x,z] its foot,
// o.tilt: leans its top toward the sofa (+) or falls back on the floor (-1.5)
const BAIT_H = RUG.z1 - RUG.z0, BAIT_R = 0.12;
function baitTop(o) { const b = baitBase(o), d = baitDir(o); return V3.add(b, V3.mul(d, BAIT_H)); }
function baitDir(o) { const st = ease(clamp(o.stand ?? 1)), tl = o.tilt || 0; return V3.norm(V3.lerp([0, 0, 1], [0, Math.cos(tl), -Math.sin(tl)], st)); }
function baitBase(o) { const st = ease(clamp(o.stand ?? 1)), r = BAIT_R * Math.sqrt(clamp(o.roll ?? 1)) + 0.02, pos = o.pos || [SPOT.x, SPOT.z];
  const lying = [lerp(RUG.x0, RUG.x1, clamp(o.roll ?? 1)), r, RUG.z0], up = [pos[0], Math.max(0, r * Math.abs(Math.sin(Math.min(0, o.tilt || 0)))), pos[1]];
  return V3.lerp(lying, up, st); }
function rugBait(o = {}) {
  const roll = clamp(o.roll ?? 1); if (roll <= 0.001) return;
  const r = BAIT_R * Math.sqrt(roll) + 0.02, a = baitBase(o), d = baitDir(o), b = V3.add(a, V3.mul(d, BAIT_H));
  ctx.save(); glow('rgba(255,255,255,0.12)', 10); cyl3(a, b, r, '#36363b', '#5a5a60', '#2a2a2e'); noGlow(); ctx.restore();
  const hk = clamp(o.hood || 0); if (hk <= 0) return;
  // the hoodie, dropped over its top: a torso, two empty sleeves, the hood up with nothing inside it
  const lift = V3.mul(d, 0.45 * (1 - easeOut(hk))), T = V3.add(b, lift), cp = camPos(), fw = V3.norm([cp[0] - T[0], 0, cp[2] - T[2]]), rg = [fw[2], 0, -fw[0]];
  const at = (along, side) => V3.add(V3.add(T, V3.mul(d, -along)), V3.mul(rg, side));
  ctx.save(); ctx.globalAlpha *= clamp(hk * 2); glow('rgba(255,255,255,0.2)', 12);
  for (const sg of [-1, 1]) { const s0 = prj(at(0.08, sg * 0.21)), s1 = prj(at(0.6, sg * 0.27)); if (s0 && s1) { ln(s0[0], s0[1], s1[0], s1[1], 0.09 * s0[3], HOOD_C); circ(s1[0], s1[1], 0.045 * s1[3], '#8a8a90'); } }
  const q = [at(0.05, -0.22), at(0.05, 0.22), at(0.62, 0.18), at(0.62, -0.18)].map(prj);
  if (q.every(Boolean)) { ctx.beginPath(); q.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); ctx.fillStyle = HOOD_C; ctx.fill(); noGlow(); ctx.lineWidth = 2; ctx.strokeStyle = HOOD_EDGE; ctx.stroke(); }
  const band = [at(0.57, -0.18), at(0.57, 0.18), at(0.62, 0.18), at(0.62, -0.18)].map(prj); if (band.every(Boolean)) { ctx.beginPath(); band.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); ctx.fillStyle = '#a4a4aa'; ctx.fill(); }
  const pk = [at(0.38, -0.11), at(0.38, 0.11), at(0.52, 0.14), at(0.52, -0.14)].map(prj); if (pk.every(Boolean)) { ctx.beginPath(); pk.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); ctx.fillStyle = '#8e8e94'; ctx.fill(); ctx.strokeStyle = HOOD_EDGE; ctx.lineWidth = 2; ctx.stroke(); }
  for (const sg of [-1, 1]) { const s0 = prj(at(0.04, sg * 0.04)), s1 = prj(at(0.2, sg * 0.045)); if (s0 && s1) { ln(s0[0], s0[1], s1[0], s1[1], 0.012 * s0[3], '#e8e8ec'); circ(s1[0], s1[1], 0.012 * s1[3], '#e8e8ec'); } }
  const h = prj(V3.add(T, V3.mul(d, 0.1))), pT = prj(V3.sub(T, V3.mul(d, 0.2))); if (h && pT) { const k = h[3];
    ctx.save(); ctx.translate(h[0], h[1]); ctx.rotate(Math.atan2(h[0] - pT[0], pT[1] - h[1]));
    ctx.beginPath(); ctx.ellipse(0, 0, 0.13 * k, 0.16 * k, 0, 0, Math.PI * 2); ctx.fillStyle = '#929298'; ctx.fill(); ctx.strokeStyle = HOOD_EDGE; ctx.lineWidth = 2; ctx.stroke();
    ctx.beginPath(); ctx.ellipse(0, 0.02 * k, 0.075 * k, 0.1 * k, 0, 0, Math.PI * 2); ctx.fillStyle = '#121214'; ctx.fill(); ctx.restore(); }
  ctx.restore();
}
// what the knife took off: one long grey joint, a knuckle and a dark nail, black ooze at the cut. c: floor point, a: its direction on the floor, tw: twitch
function severed3(t, c, a, o = {}) {
  const u = [Math.cos(a), 0, Math.sin(a)], tw = (o.tw || 0) * Math.sin(t * 23) * 0.04;
  const p0 = [c[0], 0.03, c[2]], p1 = V3.add(p0, V3.add(V3.mul(u, 0.28), [0, 0.05 + tw, 0])), p2 = V3.add(p1, V3.add(V3.mul([Math.cos(a + 0.35), 0, Math.sin(a + 0.35)], 0.24), [0, -0.045, 0]));
  const q0 = prj(p0); if (q0) { ctx.save(); ell(q0[0], q0[1] + 0.01 * q0[3], 0.06 * q0[3], 0.025 * q0[3], 0, '#030303'); ctx.strokeStyle = '#4a4a50'; ctx.lineWidth = 1.5; ctx.stroke(); ctx.restore(); }
  ctx.save(); glow('rgba(255,255,255,0.14)', 10); bone3(p0, p1, THING_C, THING_EDGE, 0.06); bone3(p1, p2, THING_C, THING_EDGE, 0.048); noGlow(); knuckle3(p1, THING_C, THING_EDGE, 0.04);
  const a2 = prj(p2), tp = prj(V3.add(p2, V3.mul([Math.cos(a + 0.5), 0, Math.sin(a + 0.5)], 0.08))); if (a2 && tp) { const dx = tp[0] - a2[0], dy = tp[1] - a2[1], L = Math.hypot(dx, dy) || 1, w = 0.02 * a2[3];
    pth(`M${a2[0] - dy / L * w},${a2[1] + dx / L * w} L${tp[0]},${tp[1]} L${a2[0] + dy / L * w},${a2[1] - dx / L * w} Z`, '#121214'); }
  if (q0) { ctx.globalAlpha *= 0.9; circ(q0[0], q0[1], 0.022 * q0[3], '#050505'); }
  ctx.restore();
}
// black liquid where the blade went in: a spurt of drops (k: seconds since the cut) and a pool that spreads
function ooze3(c, k) {
  if (k < 0) return; const pool = easeOut(clamp(k / 2.2));
  const pts = []; for (let i = 0; i < 18; i++) { const an = i / 18 * Math.PI * 2, rr2 = (0.17 + 0.07 * Math.sin(i * 2.7) + 0.04 * Math.cos(i * 5.1)) * pool; pts.push([c[0] + Math.cos(an) * rr2 * 1.3, 0.005, c[2] + Math.sin(an) * rr2]); }
  if (pool > 0.02) polyW(pts, '#040404', '#45454b', 1.5);
  if (k < 0.7) for (let i = 0; i < 12; i++) { const an = i * 2.39, sp = 0.6 + (i % 4) * 0.25, vy = 1.2 + (i % 3) * 0.5, x = c[0] + Math.cos(an) * sp * k, z = c[2] + Math.sin(an) * sp * k * 0.7, y = Math.max(0.01, 0.17 + vy * k - 4.9 * k * k);
    const q = prj([x, y, z]); if (q) { ctx.save(); ctx.globalAlpha *= 1 - k / 0.7; circ(q[0], q[1], (0.016 + 0.006 * (i % 3)) * q[3], '#050505'); ctx.lineWidth = 1; ctx.strokeStyle = '#6a6a70'; ctx.stroke(); ctx.restore(); } }
}

// ---------- the thing under the sofa ----------
// Grey, thin, wrong. A long cracked skull with one red eye and one stitched-shut socket, wet black hair, a spine, and arms with far too many joints.
// It only moves when the camera is not looking at it.
const THING_C = '#b4b4ba', THING_EDGE = '#2a2a2e', THING_X = 0.4;
function underThing(t, o = {}) {
  const ex = o.ex ?? THING_X;
  if ((o.eye || 0) > 0 && !(o.head > 0)) { const p = prj([ex, 0.07, SOFA.z1 + 0.01]); if (p) { ctx.save(); ctx.globalAlpha *= o.eye; redGlow(26 + 10 * Math.sin(t * 5)); ell(p[0], p[1], 0.05 * p[3], 0.03 * p[3], 0, C.red); noGlow(); ell(p[0], p[1], 0.008 * p[3], 0.026 * p[3], 0, '#1a0000'); ctx.restore(); } }
  if (o.head > 0) thingHead(t, ex, o.head, o);
}
// the arm: from under the front edge of the sofa out across the floor to `to`, k of the way; every other joint knuckles high off the floor, like an insect's
function armPath(from, to, n = 7) {
  const pts = []; for (let i = 0; i <= n; i++) { const u = i / n, wob = Math.sin(u * Math.PI * 3) * 0.08 * (1 - u);
    const dx = to[0] - from[0], dz = to[1] - from[1], L = Math.hypot(dx, dz) || 1;
    pts.push([lerp(from[0], to[0], u) - dz / L * wob, i === n ? 0.05 : i % 2 ? 0.17 : 0.03, lerp(from[1], to[1], u) + dx / L * wob]); }
  return pts;
}
// one bone: thick at the joints, thin in the middle, a tendon down its length
function bone3(a, b, col, edge, w = 0.045) {
  const p = prj(a), q = prj(b); if (!p || !q) return;
  const dx = q[0] - p[0], dy = q[1] - p[1], L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L, w0 = w * p[3], w1 = w * q[3], wm = 0.55 * (w0 + w1) / 2;
  const mx = (p[0] + q[0]) / 2, my = (p[1] + q[1]) / 2;
  ctx.beginPath(); ctx.moveTo(p[0] + nx * w0 / 2, p[1] + ny * w0 / 2); ctx.quadraticCurveTo(mx + nx * wm / 2, my + ny * wm / 2, q[0] + nx * w1 / 2, q[1] + ny * w1 / 2);
  ctx.lineTo(q[0] - nx * w1 / 2, q[1] - ny * w1 / 2); ctx.quadraticCurveTo(mx - nx * wm / 2, my - ny * wm / 2, p[0] - nx * w0 / 2, p[1] - ny * w0 / 2); ctx.closePath();
  ctx.fillStyle = col; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = edge; ctx.stroke();
  ctx.save(); ctx.globalAlpha *= 0.5; ln(p[0] + nx * w0 * 0.15, p[1] + ny * w0 * 0.15, q[0] + nx * w1 * 0.15, q[1] + ny * w1 * 0.15, 1.5, edge); ctx.restore();
}
function knuckle3(c, col, edge, r = 0.035) { const p = prj(c); if (!p) return; ell(p[0], p[1], r * p[3], r * 0.8 * p[3], 0, col); ctx.lineWidth = 2; ctx.strokeStyle = edge; ctx.stroke();
  ctx.beginPath(); ctx.arc(p[0], p[1] + r * 0.2 * p[3], r * 0.5 * p[3], 3.6, 5.8); ctx.stroke(); }
// a hand: a narrow palm and five long fingers of three bones each, dark pointed nails. grip: curled shut (round an ankle)
function claw2(x, y, a0, s, o = {}) {
  const col = o.col || THING_C, edge = o.edge || THING_EDGE, grip = o.grip ? 1 : 0, t = o.t || 0;
  ctx.save(); ctx.translate(x, y); ctx.rotate(a0);
  ctx.beginPath(); ctx.ellipse(0.02 * s, 0, 0.05 * s, 0.035 * s, 0, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = edge; ctx.stroke();
  for (let i = 0; i < 5; i++) { const thumb = i === 4, sp = thumb ? 1.25 : (i - 1.5) * 0.24, len = (thumb ? 0.65 : i === 1 || i === 2 ? 1.15 : 1) * 0.085 * s;
    let px = 0.05 * s * Math.cos(sp), py = 0.04 * s * Math.sin(sp), ang = sp * (1 - 0.5 * grip);
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for (let k = 0; k < 3; k++) { const bend = grip ? 0.85 : 0.22 + 0.08 * Math.sin(t * 5 + i + k); ang += bend * (thumb ? -1 : 1) * (k ? 1 : 0.4);
      const nx = px + Math.cos(ang) * len * (1 - k * 0.18), ny = py + Math.sin(ang) * len * (1 - k * 0.18);
      ln(px, py, nx, ny, 0.026 * s * (1 - k * 0.22) + 3, edge); ln(px, py, nx, ny, 0.026 * s * (1 - k * 0.22), col);
      if (k < 2) circ(nx, ny, 0.016 * s, col);
      else { const na = ang; pth(`M${nx + Math.cos(na + 1.6) * 0.012 * s},${ny + Math.sin(na + 1.6) * 0.012 * s} L${nx + Math.cos(na) * 0.04 * s},${ny + Math.sin(na) * 0.04 * s} L${nx + Math.cos(na - 1.6) * 0.012 * s},${ny + Math.sin(na - 1.6) * 0.012 * s} Z`, '#121214'); }
      px = nx; py = ny; } }
  ctx.restore();
}
function thingArm(t, o) {
  const ex = o.ex ?? THING_X, to = o.to || [SPOT.x, SPOT.z], from = [ex + 0.24 * (to[0] < ex ? -1 : 1), SOFA.z1 - 0.1], k = clamp(o.k ?? 1);
  const pts = armPath(from, to, o.n || 7), n = pts.length - 1, reach = k * n, col = o.col || THING_C, edge = o.edge || THING_EDGE;
  const segs = []; let last = pts[0];
  for (let i = 0; i < n && i < reach; i++) { const a = pts[i], b = i + 1 <= reach ? pts[i + 1] : V3.lerp(pts[i], pts[i + 1], reach - i); segs.push([a, b]); last = b; }
  ctx.save(); glow('rgba(255,255,255,0.14)', 10);
  segs.forEach(([a, b], i) => bone3(a, b, col, edge, 0.05 - i * 0.002));
  segs.forEach(([a], i) => { if (i > 0) knuckle3(a, col, edge, 0.034); });
  noGlow();
  const hp = prj(last), pv = prj(segs.length ? segs[segs.length - 1][0] : pts[0]);
  if (hp && pv && k > 0.05) claw2(hp[0], hp[1], Math.atan2(hp[1] - pv[1], hp[0] - pv[0]), hp[3] * 1.5, { grip: o.grip, col, edge, t });
  ctx.restore();
  return last;
}
// its head sliding out from under the sofa, lying on its side, then lifting its one red eye to the camera. o.size scales it; o.hands: two hands on the floor beside it
function thingHead(t, ex, k, o = {}) {
  const out = ease(clamp(k * 1.6)), lift = ease(clamp(k * 1.6 - 0.6));
  const c = [ex, 0.08 + 0.1 * lift, SOFA.z1 - 0.15 + 0.32 * out], p = prj(c); if (!p) return;
  const s = p[3] * (o.size || 1.4), col = o.col || THING_C, edge = o.edge || THING_EDGE;
  // the neck: a ridge of vertebrae running back into the dark under the sofa
  const nb = prj([ex + 0.05, 0.05, SOFA.z1 - 0.25]); if (nb) { ctx.save(); ln(nb[0], nb[1], p[0], p[1], 0.07 * s, col); ctx.globalAlpha *= 0.9;
    for (let i = 1; i < 6; i++) { const u = i / 6; circ(lerp(nb[0], p[0], u), lerp(nb[1], p[1], u) - 0.02 * s, 0.022 * s, '#8a8a90'); } ctx.restore(); }
  // the hands, flat on the floor either side, fingers splayed toward you
  if (o.hands !== false) for (const sg of [-1, 1]) { const h = prj([ex + sg * 0.3, 0.02, SOFA.z1 + 0.05 + 0.1 * out]), b = prj([ex + sg * 0.3, 0.02, SOFA.z1 - 0.1]); if (h && b) {
    ctx.save(); ln(b[0], b[1], h[0], h[1], 0.04 * h[3], col); claw2(h[0], h[1], Math.atan2(h[1] - b[1], h[0] - b[0]) + sg * 0.25, h[3] * 1.3, { col, edge, t: t + sg }); ctx.restore(); } }
  ctx.save(); glow('rgba(255,255,255,0.16)', 14);
  ctx.translate(p[0], p[1]); ctx.rotate(lerp(1.35, 0.12, lift) + Math.sin(t * 0.8) * 0.03);
  // long wet black hair hanging from the crown down both sides of the skull
  const hair = (i, n, front) => { const u = i / (n - 1), ang = lerp(-2.7, -0.45, u), sx = Math.cos(ang) * 0.15 * s, sy = -0.04 * s + Math.sin(ang) * 0.18 * s, side = Math.sign(Math.cos(ang)) || 1, sway = Math.sin(t * 0.8 + i * 1.7) * 0.012 * s;
    const len = (0.42 + 0.12 * ((i * 7) % 5) / 4) * s; ctx.beginPath(); ctx.moveTo(sx, sy);
    ctx.bezierCurveTo(sx + side * 0.07 * s, sy + 0.05 * s, sx + side * (0.05 * s) + sway, sy + len * 0.5, sx + side * (0.02 * s + 0.03 * s * Math.sin(i)) + sway * 2, sy + len);
    ctx.strokeStyle = front ? 'rgba(18,18,20,0.92)' : (i % 2 ? '#141416' : '#26262b'); ctx.lineWidth = (front ? 0.008 : 0.013) * s; ctx.lineCap = 'round'; ctx.stroke(); };
  for (let i = 0; i < 26; i++) hair(i, 26, false);
  // the skull: tall dome, long narrow jaw, slightly crooked; no mouth
  const sk = () => { ctx.beginPath(); ctx.moveTo(-0.01 * s, -0.21 * s); ctx.bezierCurveTo(0.14 * s, -0.21 * s, 0.15 * s, 0.0, 0.08 * s, 0.14 * s); ctx.bezierCurveTo(0.05 * s, 0.22 * s, 0.01 * s, 0.27 * s, -0.025 * s, 0.26 * s);
    ctx.bezierCurveTo(-0.07 * s, 0.24 * s, -0.11 * s, 0.12 * s, -0.12 * s, 0.02 * s); ctx.bezierCurveTo(-0.14 * s, -0.12 * s, -0.11 * s, -0.21 * s, -0.01 * s, -0.21 * s); };
  sk(); ctx.fillStyle = col; ctx.fill(); noGlow(); ctx.lineWidth = 3; ctx.strokeStyle = edge; ctx.stroke();
  ctx.save(); sk(); ctx.clip();
  // hollow cheeks and a dark underside
  ctx.globalAlpha = 0.45; ell(-0.085 * s, 0.09 * s, 0.035 * s, 0.09 * s, 0.15, '#4a4a50'); ell(0.085 * s, 0.07 * s, 0.03 * s, 0.08 * s, -0.2, '#4a4a50');
  const g = ctx.createLinearGradient(0, -0.2 * s, 0, 0.27 * s); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.6, 'rgba(0,0,0,0.1)'); g.addColorStop(1, 'rgba(0,0,0,0.6)'); ctx.globalAlpha = 1; ctx.fillStyle = g; ctx.fillRect(-0.2 * s, -0.25 * s, 0.4 * s, 0.55 * s);
  // cracks over the dome
  ctx.strokeStyle = edge; ctx.lineWidth = 1.6; ctx.globalAlpha = 0.8;
  ctx.beginPath(); ctx.moveTo(0.03 * s, -0.21 * s); ctx.lineTo(0.05 * s, -0.16 * s); ctx.lineTo(0.035 * s, -0.12 * s); ctx.lineTo(0.06 * s, -0.09 * s); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-0.1 * s, -0.12 * s); ctx.lineTo(-0.07 * s, -0.1 * s); ctx.lineTo(-0.075 * s, -0.06 * s); ctx.stroke();
  // two slits where a nose should be
  ctx.globalAlpha = 0.9; ell(-0.012 * s, 0.07 * s, 0.006 * s, 0.018 * s, 0.1, '#1a1a1c'); ell(0.012 * s, 0.07 * s, 0.006 * s, 0.018 * s, -0.1, '#1a1a1c');
  ctx.restore();
  // the left socket: stitched shut
  ell(-0.06 * s, -0.04 * s, 0.035 * s, 0.022 * s, -0.15, '#3a3a3f'); ctx.lineWidth = 1.8; ctx.strokeStyle = '#121214';
  ln(-0.088 * s, -0.035 * s, -0.032 * s, -0.045 * s, 2, '#121214'); for (let i = 0; i < 4; i++) { const x = (-0.082 + i * 0.016) * s; ln(x, -0.055 * s, x + 0.003 * s, -0.025 * s, 1.6, '#121214'); }
  // the right one: wide open, the only red thing about it
  ell(0.045 * s, -0.05 * s, 0.062 * s, 0.05 * s, 0.1, '#0c0c0d');
  redGlow(28 + 12 * Math.sin(t * 5)); ell(0.045 * s, -0.05 * s, 0.046 * s, 0.037 * s, 0.1, C.red); noGlow();
  ctx.strokeStyle = 'rgba(90,0,0,0.9)'; ctx.lineWidth = 1.2; for (let i = 0; i < 7; i++) { const a = i * 0.9; ctx.beginPath(); ctx.moveTo(0.045 * s + Math.cos(a) * 0.044 * s, -0.05 * s + Math.sin(a) * 0.035 * s); ctx.lineTo(0.045 * s + Math.cos(a + 0.2) * 0.026 * s, -0.05 * s + Math.sin(a + 0.2) * 0.02 * s); ctx.stroke(); }
  ell(0.047 * s, -0.05 * s, 0.008 * s, 0.032 * s, 0.1, '#150000'); circ(0.06 * s, -0.064 * s, 0.006 * s, 'rgba(255,220,220,0.8)');
  for (const i of [4, 6, 7, 9, 11]) hair(i, 26, true);
  ctx.restore();
}

// ---------- the phone ----------
const SW = 368, SH = 808;
function phone(x, y, s, fn, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(o.rot || 0);
  const bright = o.bright ?? 1;
  if (bright > 0) { ctx.save(); ctx.globalAlpha *= 0.55 * bright; glow('rgba(215,228,255,0.9)', 90); rr(-190, -414, 380, 828, 50, '#0d0d0d'); ctx.restore(); }
  rr(-200, -424, 400, 848, 58, '#111'); rrS(-200, -424, 400, 848, 58, '#5e5e5e', 5); rrS(-193, -417, 386, 834, 52, '#262626', 3);
  rr(-204, -280, 6, 70, 3, '#3a3a3a'); rr(198, -300, 6, 110, 3, '#3a3a3a');
  ctx.save(); ctx.beginPath(); ctx.roundRect(-SW / 2, -SH / 2, SW, SH, 44); ctx.clip();
  ctx.translate(-SW / 2, -SH / 2); rr(0, 0, SW, SH, 0, '#000'); fn();
  if (bright < 1) { ctx.globalAlpha = 1 - bright; rr(0, 0, SW, SH, 0, '#000'); ctx.globalAlpha = 1; }
  ctx.restore();
  rr(-58, -SH / 2 + 14, 116, 34, 17, '#000'); circ(30, -SH / 2 + 31, 7, '#151515');
  ctx.restore();
}
function statusBar(time = '3:02', dark = true) {
  const c = dark ? '#f2f2f2' : '#111';
  text(time, 46, 40, `600 19px ${UI}`, c, 'left');
  for (let i = 0; i < 4; i++) rr(276 + i * 8, 34 - i * 3, 5, 6 + i * 3, 1, c);
  rrS(312, 26, 32, 15, 4, c, 2); rr(315, 29, 22, 9, 2, c); rr(345, 30, 2, 7, 1, c);
}
// a camera-app notification card (generic, no real brand)
function camNotif(x, y, w, sub = 'Living room · 3:02 AM', o = {}) {
  ctx.save(); ctx.globalAlpha *= 0.96; rr(x, y, w, 96, 22, o.light ? '#e9e9ec' : '#1e1e21'); ctx.restore();
  const tc = o.light ? '#111' : '#f2f2f2', sc = o.light ? '#555' : '#9a9a9e';
  rr(x + 16, y + 20, 56, 56, 14, '#2b2b2f'); circS(x + 44, y + 48, 15, '#e8e8ec', 4); circ(x + 44, y + 48, 6, C.red);
  text('Motion detected', x + 88, y + 44, `700 22px ${UI}`, tc, 'left'); text(sub, x + 88, y + 74, `500 18px ${UI}`, sc, 'left');
  text('now', x + w - 20, y + 40, `500 15px ${UI}`, sc, 'right');
}

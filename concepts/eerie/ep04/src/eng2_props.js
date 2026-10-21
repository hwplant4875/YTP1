// ---------- EP04: the living room in 3D, the security camera in its corner, and the thing under the sofa ----------
// World in metres. x: right as you face the back wall, y: up, z: out of the back wall into the room. Back wall z = 0 (sofa, front door), left wall x = x0 (window).
const ROOM = { x0: -2.4, x1: 2.4, y1: 2.5, z1: 4.2 };
const SOFA = { x0: -1.55, x1: 0.75, z0: 0.06, z1: 0.98, gap: 0.13, seat: 0.46, back: 0.92, arm: 0.64 };
const FDOOR = { x0: 1.25, x1: 2.1, h: 2.1 };                    // the front door, in the back wall
const WIN = { z0: 1.1, z1: 2.7, y0: 0.95, y1: 2.05 };            // the window, in the left wall
const LAMP = { x: 0.98, z: 0.3 };
const CHAIR = { x: -1.95, z: 3.35 };
const SPOT = { x: -0.65, z: 2.0 };                               // where you stand in the clip, on the rug in front of the sofa
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
  polyW([[SPOT.x - 1.0, 0.004, SPOT.z - 0.55], [SPOT.x + 0.95, 0.004, SPOT.z - 0.55], [SPOT.x + 0.95, 0.004, SPOT.z + 0.75], [SPOT.x - 1.0, 0.004, SPOT.z + 0.75]], '#202022', '#38383c', 2);
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
function poseOf(p) { return { x: SPOT.x, z: SPOT.z, yaw: 0, lean: 0, look: 0, roll: 0, ...STAND, ...p }; }
function skeleton(ps) {
  const yaw = ps.yaw || 0, F = [-Math.sin(yaw), 0, -Math.cos(yaw)], R = [Math.cos(yaw), 0, -Math.sin(yaw)];
  const Wd = (lx, ly, lz) => [ps.x + R[0] * lx + F[0] * lz, ly, ps.z + R[2] * lx + F[2] * lz];
  const hipY = 0.95, la = ps.lean || 0;
  const up = (lx, ly, lz = 0) => { const dy = ly - hipY; return Wd(lx, hipY + dy * Math.cos(la) - lz * Math.sin(la), lz * Math.cos(la) + dy * Math.sin(la)); };
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
  j.hip = { L: Wd(-0.09, 0.95, 0), R: Wd(0.09, 0.95, 0) };
  j.foot = { L: Wd(-0.1, 0.04 + Math.max(0, Math.sin(ph)) * 0.06 * (sw > 0), Math.cos(ph) * sw + 0.03), R: Wd(0.1, 0.04 + Math.max(0, -Math.sin(ph)) * 0.06 * (sw > 0), -Math.cos(ph) * sw + 0.03) };
  if (ps.footL) j.foot.L = ps.footL;
  j.knee = { L: V3.add(V3.lerp(j.hip.L, j.foot.L, 0.5), V3.mul(F, 0.03)), R: V3.add(V3.lerp(j.hip.R, j.foot.R, 0.5), V3.mul(F, 0.03)) };
  return j;
}
// o.col: skin/limbs, o.top: the torso and arms (the grey hoodie), o.hood: draw the hood behind the head
function body3(ps, o = {}) {
  const j = skeleton(ps), col = o.col || C.fig, top = o.top || col;
  const parts = [];
  const cap = (a, b, w, c = col) => parts.push({ d: (toCam(a)[2] + toCam(b)[2]) / 2, f: () => { const p = prj(a), q = prj(b); if (p && q) ln(p[0], p[1], q[0], q[1], w * (p[3] + q[3]) / 2, c); } });
  for (const s of ['L', 'R']) { cap(j.hip[s], j.knee[s], 0.13); cap(j.knee[s], j.foot[s], 0.12); }
  parts.push({ d: toCam(j.chest)[2] + 0.02, f: () => { const p = prj(j.chest), q = prj(j.pelvis); if (!p || !q) return; ln(p[0], p[1], q[0], q[1], 0.29 * (p[3] + q[3]) / 2, top);
    const sl = prj(j.sh.L), sr = prj(j.sh.R); if (sl && sr) ln(sl[0], sl[1], sr[0], sr[1], 0.1 * (sl[3] + sr[3]) / 2, top);
    if (o.hood) { const n = prj(V3.add(j.neck, V3.mul(j.F, -0.07))); if (n) circ(n[0], n[1], 0.1 * n[3], top); }
    if (o.mark) { const c = prj(V3.lerp(j.chest, j.pelvis, 0.4)); if (c) { ctx.save(); noGlow(); redGlow(16); rrS(c[0] - 0.24 * c[3], c[1] - 0.36 * c[3], 0.48 * c[3], 0.72 * c[3], 8, C.red, 4); ctx.restore(); } } } });
  cap(j.neck, j.chest, 0.08);
  for (const s of ['L', 'R']) { cap(j.sh[s], j.elb[s], 0.095, top); cap(j.elb[s], j.hand[s], 0.085, top);
    parts.push({ d: toCam(j.hand[s])[2] - 0.001, f: () => { const p = prj(j.hand[s]); if (p) circ(p[0], p[1], 0.05 * p[3], col); } }); }
  parts.push({ d: toCam(j.head)[2], f: () => head3(j, col, o) });
  parts.sort((a, b) => b.d - a.d);
  ctx.save(); glow(o.glow || 'rgba(255,255,255,0.22)', 14); for (const p of parts) p.f(); ctx.restore();
  return j;
}
function head3(j, col, o) {
  const p = prj(j.head); if (!p) return; const r = 0.11 * p[3];
  circ(p[0], p[1], r, col); noGlow();
  const fd = V3.dot(j.F, V3.norm(V3.sub(camPos(), j.head)));
  ctx.save(); ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.clip();
  const side = prj(V3.add(j.head, V3.mul(j.F, 0.05))), sx = side ? (side[0] - p[0]) : 0;
  const up = lerp(0.0, 0.78, (fd + 1) / 2) * r;
  circ(p[0] - sx * 0.9 * (1 - fd * fd), p[1] - up, r * 1.02, o.hair || '#8e8e92'); ctx.restore();
  if (fd > 0.15) { const a = clamp((fd - 0.15) / 0.3);   // a face toward the camera always shows both eyes
    for (const sg of [-1, 1]) { const e = prj(V3.add(j.head, V3.add(V3.mul(j.F, 0.1), V3.add(V3.mul(j.R, sg * 0.042), [0, 0.005 - 0.05 * (j.look || 0), 0])))); if (!e) continue;
      ctx.save(); ctx.globalAlpha *= a; ell(e[0], e[1], 0.014 * e[3], (o.blink ? 0.003 : 0.018) * e[3], 0, o.eye || '#000'); ctx.restore(); } }
}
// someone lying on the floor, feet toward (fx, fz), head toward the direction a (radians in the floor plane)
function lying3(fx, fz, a, o = {}) {
  const col = o.col || C.fig, top = o.top || col, u = [Math.sin(a), 0, Math.cos(a)], r = [Math.cos(a), 0, -Math.sin(a)];
  const P = (along, side, y = 0.08) => [fx + u[0] * along + r[0] * side, y, fz + u[2] * along + r[2] * side];
  const cap = (a, b, w, c) => { const p = prj(a), q = prj(b); if (p && q) ln(p[0], p[1], q[0], q[1], w * (p[3] + q[3]) / 2, c); };
  ctx.save(); glow('rgba(255,255,255,0.2)', 12);
  cap(P(0, -0.1), P(0.5, -0.09), 0.12, col); cap(P(0.02, 0.1), P(0.5, 0.09), 0.12, col);
  cap(P(0.5, 0, 0.11), P(1.05, 0, 0.12), 0.29, top);
  cap(P(1.0, -0.19, 0.1), P(1.4, -0.3, 0.06), 0.09, top); cap(P(1.0, 0.19, 0.1), P(1.42, 0.28, 0.06), 0.09, top);   // arms flung up past the head
  const h = prj(P(1.27, 0, 0.11)); if (h) circ(h[0], h[1], 0.11 * h[3], col);
  ctx.restore();
}

// ---------- the thing under the sofa ----------
// Flat and grey. One red eye. An arm with far too many joints. It only moves when the camera is not looking at it.
const THING_C = '#c4c4ca', THING_X = 0.4;
// o.eye 0..1 (the red eye glowing in the gap), o.ex: where along the sofa; o.arm {k 0..1, to [x,z], grip}, o.head 0..1 (it slides its head out and looks up at the camera)
function underThing(t, o = {}) {
  const ex = o.ex ?? THING_X, ez = SOFA.z1 - 0.05;
  if ((o.eye || 0) > 0 && !(o.head > 0)) { const p = prj([ex, 0.07, SOFA.z1 + 0.01]); if (p) { ctx.save(); ctx.globalAlpha *= o.eye; redGlow(26 + 10 * Math.sin(t * 5)); ell(p[0], p[1], 0.05 * p[3], 0.03 * p[3], 0, C.red); ctx.restore(); } }
  if (o.head > 0) thingHead(t, ex, o.head, o);
}
// the arm: from under the front edge of the sofa out across the floor to `to`, k of the way; each joint knuckles up off the floor
function armPath(from, to, n = 7) {
  const pts = []; for (let i = 0; i <= n; i++) { const u = i / n, wob = Math.sin(u * Math.PI * 3) * 0.08 * (1 - u);
    const dx = to[0] - from[0], dz = to[1] - from[1], L = Math.hypot(dx, dz) || 1;
    pts.push([lerp(from[0], to[0], u) - dz / L * wob, i % 2 ? 0.11 : 0.04, lerp(from[1], to[1], u) + dx / L * wob]); }
  return pts;
}
function thingArm(t, o) {
  const from = [(o.ex ?? THING_X) + 0.24, SOFA.z1 - 0.1], to = o.to || [SPOT.x, SPOT.z], k = clamp(o.k ?? 1);
  const pts = armPath(from, to, o.n || 7), n = pts.length - 1, reach = k * n;
  ctx.save(); glow('rgba(255,255,255,0.18)', 12);
  let last = pts[0];
  for (let i = 0; i < n; i++) { if (i >= reach) break; const a = pts[i], b = i + 1 <= reach ? pts[i + 1] : V3.lerp(pts[i], pts[i + 1], reach - i);
    const p = prj(a), q = prj(b); if (p && q) { ln(p[0], p[1], q[0], q[1], 0.05 * (p[3] + q[3]) / 2, o.col || THING_C); if (i > 0) { circ(p[0], p[1], 0.038 * p[3], o.col || THING_C); circ(p[0], p[1], 0.016 * p[3], '#3a3a3e'); } }
    last = b; }
  // the hand: long fingers spread on the floor, or closed around an ankle
  const hp = prj(last), pv = prj(pts[Math.max(0, Math.floor(reach) - 1)] || pts[0]);
  if (hp && pv && k > 0.05) { const a0 = Math.atan2(hp[1] - pv[1], hp[0] - pv[0]), s = hp[3];
    for (let i = 0; i < 5; i++) { const a = a0 + (i - 2) * 0.32 * (o.grip ? 0.5 : 1), L = 0.3 * s * (i === 2 ? 1.15 : 1), bend = o.grip ? 0.9 : 0.25 + 0.1 * Math.sin(t * 6 + i);
      ctx.beginPath(); ctx.moveTo(hp[0], hp[1]); ctx.quadraticCurveTo(hp[0] + Math.cos(a) * L * 0.6, hp[1] + Math.sin(a) * L * 0.6, hp[0] + Math.cos(a + bend) * L, hp[1] + Math.sin(a + bend) * L);
      ctx.lineWidth = Math.max(3, 0.018 * s); ctx.strokeStyle = o.col || THING_C; ctx.lineCap = 'round'; ctx.stroke(); } }
  ctx.restore();
  return last;
}
// its head sliding out from under the sofa: a long pale skull lying sideways, then lifting its one red eye to the camera
function thingHead(t, ex, k, o = {}) {
  const out = ease(clamp(k * 1.6)), lift = ease(clamp(k * 1.6 - 0.6));
  const c = [ex, 0.08 + 0.1 * lift, SOFA.z1 - 0.15 + 0.32 * out], p = prj(c); if (!p) return;
  const s = p[3] * (o.size || 1.4), col = o.col || THING_C;
  ctx.save(); glow('rgba(255,255,255,0.2)', 16);
  // fingers hooked on the floor either side: long, thin, three knuckles each
  for (const sg of [-1, 1]) { const f0 = prj([ex + sg * 0.2, 0.02, SOFA.z1 + 0.02]); if (!f0) continue;
    for (let i = 0; i < 3; i++) { const a = -Math.PI / 2 + sg * (0.5 + i * 0.35) + Math.sin(t * 2 + i) * 0.03; let x = f0[0] + sg * i * 0.03 * s, y = f0[1];
      ctx.beginPath(); ctx.moveTo(x, y); for (let j = 1; j <= 3; j++) { x += Math.cos(a + j * sg * 0.5) * 0.07 * s; y += Math.sin(a + j * sg * 0.5) * 0.07 * s * 0.6 + 0.02 * s; ctx.lineTo(x, y); }
      ctx.lineWidth = 0.022 * s; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = col; ctx.stroke(); } }
  ctx.translate(p[0], p[1]); ctx.rotate(lerp(1.35, 0.15, lift) + Math.sin(t * 0.8) * 0.03);
  // the head: a long smooth skull, wider at the top, no mouth
  ctx.beginPath(); ctx.moveTo(0, -0.2 * s); ctx.bezierCurveTo(0.15 * s, -0.2 * s, 0.13 * s, 0.12 * s, 0.05 * s, 0.2 * s); ctx.bezierCurveTo(0, 0.24 * s, -0.05 * s, 0.24 * s, -0.08 * s, 0.18 * s);
  ctx.bezierCurveTo(-0.15 * s, 0.05 * s, -0.15 * s, -0.2 * s, 0, -0.2 * s); ctx.fillStyle = col; ctx.fill(); noGlow();
  ell(0, -0.05 * s, 0.07 * s, 0.05 * s, 0, '#111');
  redGlow(26 + 12 * Math.sin(t * 5)); ell(0, -0.05 * s, 0.054 * s, 0.038 * s, 0, C.red); noGlow(); ell(0.004 * s, -0.05 * s, 0.009 * s, 0.032 * s, 0, '#1a0000');
  // the skull narrows into the dark under the sofa
  const g = ctx.createLinearGradient(0, -0.2 * s, 0, 0.24 * s); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.55, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.beginPath(); ctx.moveTo(0, -0.2 * s); ctx.bezierCurveTo(0.15 * s, -0.2 * s, 0.13 * s, 0.12 * s, 0.05 * s, 0.2 * s); ctx.bezierCurveTo(0, 0.24 * s, -0.05 * s, 0.24 * s, -0.08 * s, 0.18 * s); ctx.bezierCurveTo(-0.15 * s, 0.05 * s, -0.15 * s, -0.2 * s, 0, -0.2 * s); ctx.fillStyle = g; ctx.fill();
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

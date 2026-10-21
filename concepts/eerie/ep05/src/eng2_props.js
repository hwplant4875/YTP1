// ---------- EP05: your room at 3 A.M., seen by the laptop's camera; the AI interviewer; the thing that is only on the screen ----------
// World in metres. x: right as you face the back wall, y: up, z: out of the back wall toward the desk. Back wall z = 0 (the closet).
const ROOM = { x0: -1.9, x1: 1.9, y1: 2.4, z1: 3.4 };
const CLOSET = { x0: 0.25, x1: 1.15, h: 2.05 };                  // the closet door in the back wall, hinged on its right edge
const SEAT = { x: 0, z: 2.05 };                                  // your chair, facing the desk (+z)
const DESK = { x0: -0.75, x1: 0.75, z0: 2.42, z1: 3.05, y: 0.74 };
const BED = { x0: -1.9, x1: -0.95, z0: 0.0, z1: 2.0 };
const SPOT = SEAT;
const UI = 'I';
// the laptop's camera: at the top of the screen, looking back at you and the room behind you
const WEBCAM = { x: 0, y: 1.13, z: 2.86 };
const CAMS = {
  web: { x: WEBCAM.x, y: WEBCAM.y, z: WEBCAM.z, yaw: 0, pitch: 0.3, f: 900 },
  closet: { x: 0.75, y: 1.15, z: 0.2, yaw: Math.PI + 0.32, pitch: -0.05, f: 900 },     // from inside the closet, at your back (rule 4)
  side: { x: 1.75, y: 1.35, z: 3.25, yaw: 0.95, pitch: -0.16, f: 1000 },              // the real room, from the corner by the desk
  back: { x: -0.2, y: 1.5, z: 0.45, yaw: Math.PI - 0.05, pitch: -0.2, f: 1050 },      // behind you, over your shoulder at the laptop
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
// o.closet: 0 shut .. 1 wide open; o.lamp: the desk lamp; o.glow: the laptop's light on you and the wall
function room5(t, o = {}) {
  const { x0, x1, y1, z1 } = ROOM;
  polyW([[x0, 0, 0], [x1, 0, 0], [x1, 0, z1], [x0, 0, z1]], FLOOR_C, EDGE_C, 2);
  for (let x = x0 + 0.3; x < x1; x += 0.3) lnW([x, 0, 0], [x, 0, z1], 1.2, '#202022');   // floorboards
  polyW([[x0, 0, 0], [x1, 0, 0], [x1, y1, 0], [x0, y1, 0]], WALL_C, EDGE_C, 2);
  polyW([[x0, 0, 0], [x0, 0, z1], [x0, y1, z1], [x0, y1, 0]], SIDE_C, EDGE_C, 2);
  polyW([[x1, 0, 0], [x1, 0, z1], [x1, y1, z1], [x1, y1, 0]], SIDE_C, EDGE_C, 2);
  polyW([[x0, y1, 0], [x1, y1, 0], [x1, y1, z1], [x0, y1, z1]], '#0c0c0d', EDGE_C, 2);
  lnW([x0, 0.08, 0.005], [x1, 0.08, 0.005], 2, '#2a2a2d');
  // a poster and a shelf on the back wall, left of the closet
  polyW([[-0.85, 1.25, 0.004], [-0.3, 1.25, 0.004], [-0.3, 1.95, 0.004], [-0.85, 1.95, 0.004]], '#1d1d20', '#3a3a3e', 2);
  polyW([[-0.78, 1.33, 0.006], [-0.37, 1.33, 0.006], [-0.37, 1.6, 0.006], [-0.78, 1.6, 0.006]], '#26262a', null);
  box3(-0.9, -0.2, 0.95, 0.98, 0.0, 0.22, { top: '#38383c', side: '#2a2a2d', front: '#323236', edge: '#4c4c50' });
  for (let i = 0; i < 6; i++) box3(-0.85 + i * 0.06, -0.81 + i * 0.06, 0.98, 1.14 + 0.03 * (i % 3), 0.04, 0.18, { top: '#3a3a3e', side: '#2c2c30', front: i % 2 ? '#34343a' : '#2e2e33', edge: '#45454a' });
  // the window in the left wall
  polyW([[x0 + 0.005, 1.0, 0.7], [x0 + 0.005, 1.0, 1.9], [x0 + 0.005, 2.0, 1.9], [x0 + 0.005, 2.0, 0.7]], '#141c27', '#4a4a50', 3);
  lnW([x0 + 0.01, 1.5, 0.7], [x0 + 0.01, 1.5, 1.9], 3, '#4a4a50');
  // the bed along the left wall
  box3(BED.x0, BED.x1, 0, 0.45, BED.z0, BED.z1, { top: '#2e2e33', side: '#242428', front: '#29292d', edge: '#46464b' });
  box3(BED.x0 + 0.05, BED.x1 - 0.05, 0.45, 0.55, BED.z0 + 0.05, BED.z0 + 0.45, { top: '#3c3c41', side: '#2f2f33', front: '#35353a', edge: '#4e4e53' });
  closet5(o.closet || 0, o);
  // the ceiling light, off
  const cl = prj([0, y1 - 0.01, 1.4]); if (cl) ell(cl[0], cl[1], 0.18 * cl[3], 0.05 * cl[3], 0, '#1e1e21');
}
// the closet: black inside; its door swings into the room on the hinge at x1
function closet5(op, o = {}) {
  const { x0, x1, h } = CLOSET, dz = 0.004, w = x1 - x0;
  polyW([[x0 - 0.05, 0, dz], [x1 + 0.05, 0, dz], [x1 + 0.05, h + 0.05, dz], [x0 - 0.05, h + 0.05, dz]], '#2a2a2d', '#4c4c50', 2);
  polyW([[x0, 0, dz + 0.001], [x1, 0, dz + 0.001], [x1, h, dz + 0.001], [x0, h, dz + 0.001]], '#000', null);
  if (o.inCloset) o.inCloset();
  const a = op * 1.5, ex = x1 - w * Math.cos(a), ez = dz + w * Math.sin(a);
  polyW([[x1, 0.01, dz + 0.002], [ex, 0.01, ez], [ex, h - 0.01, ez], [x1, h - 0.01, dz + 0.002]], '#232326', '#525257', 3);
  if (op < 0.6) for (const [y0, y1] of [[0.15, 0.95], [1.1, 1.9]]) { const k = 0.12, P = u => [lerp(x1, ex, u), 0, lerp(dz + 0.002, ez, u)];
    const a0 = P(k), a1 = P(1 - k); polyW([[a0[0], y0, a0[2] + 0.002], [a1[0], y0, a1[2] + 0.002], [a1[0], y1, a1[2] + 0.002], [a0[0], y1, a0[2] + 0.002]], null, '#3a3a3e', 2); }
  const kp = prj([lerp(x1, ex, 0.9), 1.0, lerp(dz, ez, 0.9) + 0.02]); if (kp) circ(kp[0], kp[1], 0.025 * kp[3], '#77777c');
}
// your desk chair: seat, a tall back behind you
function chair5(o = {}) {
  const { x, z } = o.at || SEAT, cc = { top: '#2e2e31', side: '#242427', front: '#2a2a2d', edge: '#4c4c50' };
  box3(x - 0.03, x + 0.03, 0.05, 0.45, z - 0.03, z + 0.03, cc);
  for (const a of [0, 1.26, 2.51, 3.77, 5.03]) lnW([x, 0.05, z], [x + Math.cos(a) * 0.3, 0.03, z + Math.sin(a) * 0.3], 6, '#2a2a2d');
  box3(x - 0.25, x + 0.25, 0.45, 0.52, z - 0.25, z + 0.22, cc);
  box3(x - 0.24, x + 0.24, 0.55, 1.18, z - 0.3, z - 0.24, cc);
}
// the desk and the laptop on it (for the shots that see them)
function desk5(o = {}) {
  const { x0, x1, z0, z1, y } = DESK, dc = { top: '#2c2c30', side: '#222225', front: '#27272a', edge: '#48484d' };
  for (const [lx, lz] of [[x0 + 0.04, z0 + 0.04], [x1 - 0.04, z0 + 0.04], [x0 + 0.04, z1 - 0.04], [x1 - 0.04, z1 - 0.04]]) box3(lx - 0.025, lx + 0.025, 0, y - 0.03, lz - 0.025, lz + 0.025, dc);
  box3(x0, x1, y - 0.03, y, z0, z1, dc);
  // the laptop: base, and the screen standing up facing you (-z), lit
  box3(-0.17, 0.17, y, y + 0.02, 2.55, 2.8, { top: '#3a3a3e', side: '#2c2c30', front: '#333337', edge: '#55555a' });
  const sc = [[-0.17, y + 0.02, 2.82], [0.17, y + 0.02, 2.82], [0.17, y + 0.24, 2.86], [-0.17, y + 0.24, 2.86]];
  polyW(sc, '#2a2a2e', '#55555a', 2);
  const inner = sc.map((p, i) => [p[0] * 0.92, p[1] + (i < 2 ? 0.012 : -0.012), p[2] - 0.004]);
  if (o.lit !== 0 && camPos()[2] < 2.84) { ctx.save(); glow('rgba(200,215,255,0.8)', 30); polyW(inner, o.screenCol || '#c8d2e6', null); ctx.restore(); }
  else polyW(inner, '#0c0c0e', null);
  const wc = prj([0, y + 0.235, 2.855]); if (wc) { circ(wc[0], wc[1], 0.006 * wc[3], '#111'); if (o.tape) rr(wc[0] - 0.03 * wc[3], wc[1] - 0.012 * wc[3], 0.06 * wc[3], 0.024 * wc[3], 2, '#d8d0b8'); }
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
// ---------- the thing: too tall for the room, grey, bone-thin; it only exists on the screen ----------
const THING_C = '#b9b9bf', THING_EDGE = '#2a2a2e', SKIN_C = '#cfcfd4';
// its joints. o.at [x,z] its feet; o.sit 0..1 in your chair; o.lean 0..1 its face pushed at the lens; o.fold 0..1 folded back into the closet;
// o.hand: a world point for its right hand (your shoulder), else it hangs; o.step: walking phase
function thingJoints(t, o = {}) {
  const [x, z] = o.at || [0.15, 1.45], sit = ease(clamp(o.sit || 0)), fold = ease(clamp(o.fold || 0)), sw = o.step != null ? Math.sin(o.step) * 0.12 : 0;
  const J = {};
  const hipY = lerp(1.38, 0.58, sit) * (1 - 0.55 * fold), shY = lerp(2.08, 1.5, sit) * (1 - 0.5 * fold), zz = z - 0.25 * fold;
  J.hip = { L: [x - 0.12, hipY, zz], R: [x + 0.12, hipY, zz] };
  J.knee = { L: [x - 0.16, lerp(0.74, 1.02, sit), zz + lerp(0.1 + sw, 0.55, sit)], R: [x + 0.16, lerp(0.74, 1.0, sit), zz + lerp(0.1 - sw, 0.55, sit)] };
  J.foot = { L: [x - 0.15, 0.03, zz + lerp(sw * 1.4, 0.62, sit)], R: [x + 0.15, 0.03, zz + lerp(-sw * 1.4, 0.62, sit)] };
  if (fold > 0) for (const s of ['L', 'R']) J.knee[s] = V3.lerp(J.knee[s], [J.knee[s][0], hipY + 0.3, zz + 0.25], fold);
  J.pelvis = [x, hipY, zz]; J.chest = [x, lerp(hipY, shY, 0.72), zz + 0.02]; J.sh = { L: [x - 0.21, shY, zz + 0.02], R: [x + 0.21, shY, zz + 0.02] };
  J.neck = [x + 0.02, shY + 0.14, zz + 0.06];
  // the head: bent forward and over against the ceiling (standing), upright-ish sitting, or pushed right up to the lens
  let head = [x + 0.14, lerp(2.18, 1.88, sit), zz + 0.26], tilt = lerp(-1.15, -0.35, sit);
  if (fold > 0) { head = V3.lerp(head, [x + 0.1, 1.2, zz + 0.1], fold); }
  if (o.lean > 0) { const k = ease(clamp(o.lean)); head = V3.lerp(head, o.leanTo || [0.06, 1.2, 2.4], k); tilt = lerp(tilt, -0.18, k); }
  J.head = head; J.tilt = tilt + Math.sin(t * 0.9) * 0.03;
  // the arms: the left hangs past its knee; the right reaches for your shoulder in three long bones
  J.armL = [J.sh.L, [x - 0.33, lerp(1.45, 1.05, sit), zz + 0.06], [x - 0.36, lerp(0.85, 0.82, sit), zz + lerp(0.1, 0.5, sit)]];
  if (o.hand) { const h = o.hand, s = J.sh.R, d = V3.sub(h, s);
    J.armR = [s, V3.add(V3.lerp(s, h, 0.35), [0.2, 0.32, 0.02]), V3.add(V3.lerp(s, h, 0.72), [0.08, 0.16, 0]), h]; }
  else J.armR = [J.sh.R, [x + 0.33, lerp(1.45, 1.05, sit), zz + 0.06], [x + 0.36, lerp(0.85, 0.82, sit), zz + lerp(0.1, 0.5, sit)]];
  return J;
}
// the body: drawn before you (it is behind you); its right hand comes after you (on your shoulder)
function thing5(t, o = {}) {
  const J = thingJoints(t, o), col = o.col || THING_C, edge = o.edge || THING_EDGE;
  ctx.save(); ctx.globalAlpha *= clamp(o.alpha ?? 1); glow(o.glowCol || 'rgba(255,255,255,0.14)', 12);
  for (const s of ['L', 'R']) { bone3(J.hip[s], J.knee[s], col, edge, 0.07); bone3(J.knee[s], J.foot[s], col, edge, 0.055); }
  noGlow(); for (const s of ['L', 'R']) knuckle3(J.knee[s], col, edge, 0.045);
  // the torso: narrow, ribs showing
  const q = [V3.add(J.sh.L, [-0.03, 0.02, 0]), V3.add(J.sh.R, [0.03, 0.02, 0]), V3.add(J.pelvis, [0.1, 0, 0]), V3.add(J.pelvis, [-0.1, 0, 0])].map(prj);
  if (q.every(Boolean)) { ctx.beginPath(); q.forEach((p, i) => i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath(); ctx.fillStyle = col; ctx.fill(); ctx.lineWidth = 2.5; ctx.strokeStyle = edge; ctx.stroke();
    for (let i = 1; i <= 6; i++) { const u = i / 8, a = V3.lerp(V3.lerp(J.sh.L, J.pelvis, u), J.chest, 0.15), b = V3.lerp(V3.lerp(J.sh.R, J.pelvis, u), J.chest, 0.15), m = V3.lerp(V3.lerp(J.neck, J.pelvis, u), J.chest, 0.1);
      const pa = prj(a), pb = prj(b), pm = prj(m); if (pa && pb && pm) { ctx.save(); ctx.globalAlpha *= 0.55; ctx.beginPath(); ctx.moveTo(pa[0], pa[1]); ctx.quadraticCurveTo(pm[0], pm[1] - 6, pb[0], pb[1]); ctx.strokeStyle = edge; ctx.lineWidth = 1.6; ctx.stroke(); ctx.restore(); } }
    const s0 = prj(J.neck), s1 = prj(J.pelvis); if (s0 && s1) { ctx.save(); ctx.globalAlpha *= 0.6; ln(s0[0], s0[1], s1[0], s1[1], 2, edge); ctx.restore(); } }
  limb(J.armL, col, edge, t, false);
  // the neck: a long bent stalk of vertebrae up to the head
  const n0 = prj(J.neck), hp = prj(J.head), mid = prj(V3.add(V3.lerp(J.neck, J.head, 0.5), [0, 0.1, 0]));
  if (n0 && hp && mid) { ctx.beginPath(); ctx.moveTo(n0[0], n0[1]); ctx.quadraticCurveTo(mid[0], mid[1], hp[0], hp[1]); ctx.strokeStyle = edge; ctx.lineWidth = 0.075 * (n0[3] + hp[3]) / 2 + 4; ctx.stroke(); ctx.strokeStyle = col; ctx.lineWidth = 0.075 * (n0[3] + hp[3]) / 2; ctx.stroke();
    for (let i = 1; i < 7; i++) { const u = i / 7, a = 1 - u, bx = a * a * n0[0] + 2 * a * u * mid[0] + u * u * hp[0], by = a * a * n0[1] + 2 * a * u * mid[1] + u * u * hp[1]; circ(bx, by, 0.022 * lerp(n0[3], hp[3], u), '#909096'); } }
  if (!o.hand) limb(J.armR, col, edge, t, false);
  thingFace(t, J, o);
  ctx.restore();
  return J;
}
function thing5Hand(t, o = {}) { if (!o.hand) return; const J = thingJoints(t, o); ctx.save(); ctx.globalAlpha *= clamp(o.alpha ?? 1); limb(J.armR, o.col || THING_C, o.edge || THING_EDGE, t, true, o.grip); ctx.restore(); }
function limb(pts, col, edge, t, grip, closed) {
  for (let i = 0; i < pts.length - 1; i++) bone3(pts[i], pts[i + 1], col, edge, 0.05 - i * 0.008);
  for (let i = 1; i < pts.length - 1; i++) knuckle3(pts[i], col, edge, 0.035);
  const a = prj(pts[pts.length - 2]), b = prj(pts[pts.length - 1]); if (a && b) claw2(b[0], b[1], Math.atan2(b[1] - a[1], b[0] - a[0]), b[3] * 1.7, { grip: closed ?? grip, col, edge, t });
}
// its face: a long pale skull, two hollow eyes, no mouth. Red eyes when it is dangerous.
function thingFace(t, J, o) {
  const p = prj(J.head); if (!p) return; const s = p[3] * 0.36 * (o.faceScale || 1), col = SKIN_C, edge = THING_EDGE;
  ctx.save(); ctx.translate(p[0], p[1]); ctx.rotate(J.tilt); glow('rgba(255,255,255,0.18)', 14);
  const sk = () => { ctx.beginPath(); ctx.moveTo(0, -0.5 * s); ctx.bezierCurveTo(0.3 * s, -0.5 * s, 0.32 * s, -0.05 * s, 0.2 * s, 0.25 * s); ctx.bezierCurveTo(0.12 * s, 0.45 * s, 0.05 * s, 0.56 * s, -0.02 * s, 0.55 * s);
    ctx.bezierCurveTo(-0.1 * s, 0.53 * s, -0.2 * s, 0.35 * s, -0.25 * s, 0.15 * s); ctx.bezierCurveTo(-0.32 * s, -0.12 * s, -0.27 * s, -0.5 * s, 0, -0.5 * s); };
  sk(); ctx.fillStyle = col; ctx.fill(); noGlow(); ctx.lineWidth = 3; ctx.strokeStyle = edge; ctx.stroke();
  ctx.save(); sk(); ctx.clip();
  const g = ctx.createLinearGradient(0, -0.5 * s, 0, 0.56 * s); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.5)'); ctx.fillStyle = g; ctx.fillRect(-0.4 * s, -0.6 * s, 0.8 * s, 1.2 * s);
  ctx.globalAlpha = 0.4; ell(-0.17 * s, 0.22 * s, 0.06 * s, 0.17 * s, 0.15, '#55555b'); ell(0.15 * s, 0.2 * s, 0.05 * s, 0.16 * s, -0.15, '#55555b');
  ctx.globalAlpha = 0.85; ctx.strokeStyle = edge; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.moveTo(0.05 * s, -0.5 * s); ctx.lineTo(0.09 * s, -0.38 * s); ctx.lineTo(0.06 * s, -0.3 * s); ctx.lineTo(0.12 * s, -0.24 * s); ctx.stroke();
  ctx.globalAlpha = 0.9; ell(-0.02 * s, 0.2 * s, 0.012 * s, 0.035 * s, 0.1, '#1a1a1c'); ell(0.03 * s, 0.2 * s, 0.012 * s, 0.035 * s, -0.1, '#1a1a1c');
  ctx.restore();
  // two deep, long eye holes; red light far inside when it is dangerous
  for (const [ex, a] of [[-0.11, 0.25], [0.11, -0.25]]) { ell(ex * s, -0.05 * s, 0.075 * s, 0.11 * s, a, '#050506');
    if (o.red > 0) { ctx.save(); ctx.globalAlpha *= clamp(o.red); redGlow(24 + 10 * Math.sin(t * 5)); ell(ex * s, -0.03 * s, 0.03 * s, 0.045 * s, a, C.red); noGlow(); ctx.restore(); } }
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

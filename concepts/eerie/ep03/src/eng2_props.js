// ---------- EP03: the bathroom, built in 3D so the mirror obeys the law of reflection ----------
// World in metres. x: to the right as you face the mirror, y: up, z: out of the mirror into the room. The glass is the plane z = 0.
// The mirror shows the room reflected through that plane (z -> -z). Seen from in front, left and right stay where they are and only depth flips:
// the watch on your left wrist is on the same side of the picture in the reflection, which makes it your reflection's right wrist.
const MIR = { x0: -0.6, x1: 0.6, y0: 1.05, y1: 2.0 };          // the glass
const ROOM = { x0: -1.25, x1: 1.25, y1: 2.45, z1: 3.3 };       // floor y = 0, mirror wall z = 0, door wall z = z1
const DOOR = { x0: -0.15, x1: 0.65, h: 2.05 };                // the door, in the wall behind you
const CTR = { x0: -0.85, x1: 0.85, y: 0.88, z: 0.55 };          // the counter under the mirror
const SINK = { x: 0, z: 0.3, rx: 0.25, rz: 0.16 };
const ME = { x: -0.05, z: 0.72 };                              // where you stand at the sink
const CAMS = {
  ots: { x: 0.5, y: 1.75, z: 2.0, yaw: 0.2, pitch: -0.05, f: 1250 },     // over your right shoulder, at the mirror
  door: { x: 0.45, y: 1.62, z: 3.15, yaw: 0.06, pitch: -0.06, f: 1000 }, // from the doorway: you face the camera, the mirror behind you
  otsL: { x: -0.8, y: 1.85, z: 2.35, yaw: -0.3, pitch: -0.1, f: 1250 },   // over your left shoulder
  rev: { x: 0.3, y: 2.3, z: 0.05, yaw: Math.PI - 0.06, pitch: -0.45, f: 720 }   // from above the mirror, looking back into the room
};
let CAM = null;
function setCam(c) { CAM = { ...c, cyw: Math.cos(c.yaw || 0), syw: Math.sin(c.yaw || 0), cp: Math.cos(c.pitch || 0), sp: Math.sin(c.pitch || 0) }; }
const lerpCam = (a, b, k) => { const o = {}; for (const key of ['x', 'y', 'z', 'yaw', 'pitch', 'f']) o[key] = lerp(a[key], b[key], k); return o; };
setCam(CAMS.ots);
const V3 = { add: (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], sub: (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], mul: (a, k) => [a[0] * k, a[1] * k, a[2] * k],
  dot: (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2], len: a => Math.hypot(a[0], a[1], a[2]), lerp: (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)] };
V3.norm = a => V3.mul(a, 1 / (V3.len(a) || 1));
const MIRROR = p => [p[0], p[1], -p[2]];
// camera space: right, up, depth (forward is -z at yaw 0; positive yaw turns left, positive pitch looks up)
function toCam(p) {
  const dx = p[0] - CAM.x, dy = p[1] - CAM.y, dz = p[2] - CAM.z;
  const xc = dx * CAM.cyw - dz * CAM.syw, f0 = -dx * CAM.syw - dz * CAM.cyw;
  return [xc, dy * CAM.cp - f0 * CAM.sp, f0 * CAM.cp + dy * CAM.sp];
}
const camToScr = c => { const s = CAM.f / c[2]; return [W / 2 + c[0] * s, H / 2 - c[1] * s, c[2], s]; };
function prj(p) { const c = toCam(p); return c[2] < 0.03 ? null : camToScr(c); }
const camPos = () => [CAM.x, CAM.y, CAM.z];
// a flat polygon in the world, clipped at the near plane
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
// a circle lying in a plane: centre, two axis vectors
function ringPts(c, u, v, n = 28) { const out = []; for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; out.push(V3.add(c, V3.add(V3.mul(u, Math.cos(a)), V3.mul(v, Math.sin(a))))); } return out; }

// ---------- the room ----------
const WALL_C = '#111113', SIDE_C = '#0c0c0d', FLOOR_C = '#161616', CEIL_C = '#070707', EDGE_C = '#2c2c2e', TILE_C = '#1d1d20';
// m: 1 to draw the reflected room (inside the mirror). o.door: 0 closed .. 1 wide open
function room3(m, o = {}) {
  const T = m ? MIRROR : (p => p), z1 = ROOM.z1, { x0, x1, y1 } = ROOM;
  const P = a => polyW(a.map(T), null, null);
  // door wall (behind you; in the mirror it is the far wall)
  polyW([[x0, 0, z1], [x1, 0, z1], [x1, y1, z1], [x0, y1, z1]].map(T), WALL_C, EDGE_C, 2);
  for (let y = 0.3; y < 1.25; y += 0.3) lnW(T([x0, y, z1]), T([x1, y, z1]), 1.5, TILE_C);
  // floor, ceiling, side walls
  polyW([[x0, 0, 0], [x1, 0, 0], [x1, 0, z1], [x0, 0, z1]].map(T), FLOOR_C, EDGE_C, 2);
  for (let x = x0 + 0.42; x < x1; x += 0.42) lnW(T([x, 0, 0]), T([x, 0, z1]), 1.5, '#222');
  for (let z = 0.42; z < z1; z += 0.42) lnW(T([x0, 0, z]), T([x1, 0, z]), 1.5, '#222');
  polyW([[x0, y1, 0], [x1, y1, 0], [x1, y1, z1], [x0, y1, z1]].map(T), CEIL_C, EDGE_C, 2);
  for (const x of [x0, x1]) { polyW([[x, 0, 0], [x, 0, z1], [x, y1, z1], [x, y1, 0]].map(T), SIDE_C, EDGE_C, 2);
    for (let y = 0.3; y < 1.25; y += 0.3) lnW(T([x, y, 0]), T([x, y, z1]), 1.5, TILE_C); }
  // the door: frame, and the door itself swinging into the room on its hinge (x0 side)
  const op = o.door ?? 0, dz = z1 - 0.005;
  if (op > 0.01) polyW([[DOOR.x0, 0, dz], [DOOR.x1, 0, dz], [DOOR.x1, DOOR.h, dz], [DOOR.x0, DOOR.h, dz]].map(T), '#000', null);   // the dark hall beyond
  if (o.inDoor) o.inDoor();   // whatever stands in the doorway
  const a = op * 1.45, w = DOOR.x1 - DOOR.x0, ex = DOOR.x0 + w * Math.cos(a), ez = dz - w * Math.sin(a);
  polyW([[DOOR.x0, 0.01, dz], [ex, 0.01, ez], [ex, DOOR.h - 0.01, ez], [DOOR.x0, DOOR.h - 0.01, dz]].map(T), '#1f1f22', '#4a4a4e', 3);
  const kn = [lerp(DOOR.x0, ex, 0.88), 1.0, lerp(dz, ez, 0.88) - 0.02]; const kp = prj(T(kn)); if (kp) circ(kp[0], kp[1], 0.03 * kp[3], '#6a6a6e');
  polyW([[DOOR.x0 - 0.06, 0, dz], [DOOR.x0, 0, dz], [DOOR.x0, DOOR.h, dz], [DOOR.x1, DOOR.h, dz], [DOOR.x1, 0, dz], [DOOR.x1 + 0.06, 0, dz], [DOOR.x1 + 0.06, DOOR.h + 0.06, dz], [DOOR.x0 - 0.06, DOOR.h + 0.06, dz]].map(T), '#2a2a2d', '#55555a', 2);
}
// the mirror wall around the glass (real room only)
function mirrorWall() {
  const { x0, x1, y1 } = ROOM;
  polyW([[x0, 0, 0], [x1, 0, 0], [x1, y1, 0], [x0, y1, 0]], WALL_C, EDGE_C, 2);
  for (let y = 0.3; y < 1.0; y += 0.3) lnW([x0, y, 0], [x1, y, 0], 1.5, TILE_C);
  for (let x = x0 + 0.3; x < x1; x += 0.3) lnW([x, 0, 0], [x, 0.9, 0], 1.5, TILE_C);
}
const glassPts = () => [[MIR.x0, MIR.y0, 0], [MIR.x1, MIR.y0, 0], [MIR.x1, MIR.y1, 0], [MIR.x0, MIR.y1, 0]];
function clipGlass() { const sp = glassPts().map(prj); if (sp.some(q => !q)) return false; ctx.beginPath(); ctx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath(); ctx.clip(); return true; }
function mirrorFrame(o = {}) {
  polyW([[MIR.x0 - 0.03, MIR.y0 - 0.03, 0.005], [MIR.x1 + 0.03, MIR.y0 - 0.03, 0.005], [MIR.x1 + 0.03, MIR.y1 + 0.03, 0.005], [MIR.x0 - 0.03, MIR.y1 + 0.03, 0.005]], null, '#8a8a8e', 5);
  // the light bar over the mirror
  const lit = o.light ?? 1;
  ctx.save(); glow(`rgba(255,250,235,${0.8 * lit})`, 40); polyW([[-0.45, 2.06, 0.02], [0.45, 2.06, 0.02], [0.45, 2.12, 0.07], [-0.45, 2.12, 0.07]], `rgba(${Math.round(lerp(60, 250, lit))},${Math.round(lerp(60, 248, lit))},${Math.round(lerp(60, 238, lit))},1)`, null); ctx.restore();
}
// the glass itself: a faint cold tint and two highlight streaks, over whatever the mirror shows
function glassSheen(o = {}) {
  const sp = glassPts().map(prj); if (sp.some(q => !q)) return;
  ctx.save(); ctx.globalAlpha = 0.06; ctx.fillStyle = '#b8c8d0'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const a = sp[3], b = sp[1];
  ctx.save(); ctx.globalAlpha = 0.045; for (const [k, w] of [[0.28, 70], [0.36, 26]]) { const x = lerp(a[0], b[0], k); ln(x - 260, a[1] - 40, x + 260, b[1] + 40, w, '#fff', 'butt'); } ctx.restore();
}
function counter3(m) {
  const T = m ? MIRROR : (p => p), { x0, x1, y, z } = CTR;
  polyW([[x0, 0, z], [x1, 0, z], [x1, y, z], [x0, y, z]].map(T), '#1b1b1d', '#3c3c40', 2);           // cabinet front
  for (const x of [-0.42, 0, 0.42]) lnW(T([x, 0.08, z + 0.002]), T([x, y - 0.08, z + 0.002]), 2, '#333');
  polyW([[x0, y, 0], [x1, y, 0], [x1, y, z], [x0, y, z]].map(T), '#2e2e31', '#5a5a5e', 2);           // top
  // basin: an ellipse cut into the top, and its dark inside
  polyW(ringPts([SINK.x, y + 0.002, SINK.z], [SINK.rx, 0, 0], [0, 0, SINK.rz]).map(T), '#c9c9cc', null);
  polyW(ringPts([SINK.x, y + 0.003, SINK.z + 0.01], [SINK.rx * 0.82, 0, 0], [0, 0, SINK.rz * 0.78]).map(T), '#8d8d92', null);
  const dr = prj(T([SINK.x, y + 0.004, SINK.z + 0.02])); if (dr) circ(dr[0], dr[1], 0.018 * dr[3], '#3a3a3e');
  // tap: up from the back of the basin, then out over it
  const t0 = T([0, y, 0.07]), t1 = T([0, y + 0.16, 0.07]), t2 = T([0, y + 0.16, 0.17]);
  const q0 = prj(t0), q1 = prj(t1), q2 = prj(t2);
  if (q0 && q1 && q2) { ln(q0[0], q0[1], q1[0], q1[1], 0.03 * q1[3], '#d8d8dc'); ln(q1[0], q1[1], q2[0], q2[1], 0.026 * q2[3], '#d8d8dc');
    const h0 = prj(T([-0.06, y + 0.12, 0.05])), h1 = prj(T([0.06, y + 0.12, 0.05])); if (h0 && h1) ln(h0[0], h0[1], h1[0], h1[1], 0.022 * h0[3], '#bdbdc2'); }   // the handle
}
function waterStream(m, k = 1) {
  if (k <= 0) return; const T = m ? MIRROR : (p => p);
  const a = prj(T([0, CTR.y + 0.15, 0.17])), b = prj(T([0, CTR.y + 0.01, 0.2])); if (!a || !b) return;
  ctx.save(); ctx.globalAlpha *= 0.7 * k; glow('rgba(220,235,255,0.6)', 10); ln(a[0], a[1], b[0], b[1], 0.012 * a[3], '#e6f0ff', 'butt'); ctx.restore();
}

// ---------- people ----------
// a pose: { x, z, yaw (0 = facing the mirror), lean (rad), look (0..1 head down), roll (-1..1 head tilt), L/R: hand in body coords [right, up, forward],
//          step (walk phase), dir (walk), fing: 'point'|'flat' on R }
const STAND = { L: [-0.22, 0.8, 0.02], R: [0.22, 0.8, 0.02] };
const WASH = { L: [-0.07, 0.98, 0.42], R: [0.07, 0.98, 0.42], lean: 0.2, look: 1 };
function poseOf(p) { return { x: ME.x, z: ME.z, yaw: 0, lean: 0, look: 0, roll: 0, ...STAND, ...p }; }
function skeleton(ps) {
  const yaw = ps.yaw || 0, F = [-Math.sin(yaw), 0, -Math.cos(yaw)], R = [Math.cos(yaw), 0, -Math.sin(yaw)];
  const Wd = (lx, ly, lz) => [ps.x + R[0] * lx + F[0] * lz, ly, ps.z + R[2] * lx + F[2] * lz];
  const hipY = 0.95, la = ps.lean || 0;
  const up = (lx, ly, lz = 0) => { const dy = ly - hipY; return Wd(lx, hipY + dy * Math.cos(la) - lz * Math.sin(la), lz * Math.cos(la) + dy * Math.sin(la)); };
  const look = ps.look || 0, roll = ps.roll || 0;
  const head = up(0.05 * roll, 1.63 - 0.035 * look - 0.012 * Math.abs(roll), 0.045 * look);
  const j = { look, F, R, head, neck: up(0, 1.47), chest: up(0, 1.36), pelvis: up(0, 1.02), sh: { L: up(-0.19, 1.42), R: up(0.19, 1.42) } };
  j.hand = { L: Wd(...ps.L), R: Wd(...ps.R) };
  // elbows: two equal bones, bent outwards, down and back
  j.elb = {};
  for (const [s, sg] of [['L', -1], ['R', 1]]) { const S = j.sh[s], Hh = j.hand[s], d = V3.sub(Hh, S), L = V3.len(d), B = 0.31;
    const mid = V3.lerp(S, Hh, 0.5); let bend = V3.add(V3.mul(R, sg * 0.7), V3.add([0, -0.55, 0], V3.mul(F, -0.45)));
    const dn = V3.norm(d); bend = V3.norm(V3.sub(bend, V3.mul(dn, V3.dot(bend, dn))));
    j.elb[s] = L >= 2 * B ? mid : V3.add(mid, V3.mul(bend, Math.sqrt(B * B - L * L / 4))); }
  // legs, with a walk cycle
  const ph = ps.step || 0, sw = ps.walk ? 0.22 : 0;
  j.hip = { L: Wd(-0.09, 0.95, 0), R: Wd(0.09, 0.95, 0) };
  j.foot = { L: Wd(-0.1, 0.04 + Math.max(0, Math.sin(ph)) * 0.06 * (sw > 0), Math.cos(ph) * sw + 0.03), R: Wd(0.1, 0.04 + Math.max(0, -Math.sin(ph)) * 0.06 * (sw > 0), -Math.cos(ph) * sw + 0.03) };
  j.knee = { L: V3.add(V3.lerp(j.hip.L, j.foot.L, 0.5), V3.mul(F, 0.03)), R: V3.add(V3.lerp(j.hip.R, j.foot.R, 0.5), V3.mul(F, 0.03)) };
  return j;
}
// draw a body. o.mirror: draw its reflection; o.col; o.scars: red marks across the back (0..1); o.watch (default on)
function body3(ps, o = {}) {
  let j = skeleton(ps);
  if (o.mirror) { const M = MIRROR, mm = q => ({ L: M(q.L), R: M(q.R) });
    j = { ...j, look: j.look, F: [j.F[0], 0, -j.F[2]], R: [j.R[0], 0, -j.R[2]], head: M(j.head), neck: M(j.neck), chest: M(j.chest), pelvis: M(j.pelvis), sh: mm(j.sh), hand: mm(j.hand), elb: mm(j.elb), hip: mm(j.hip), foot: mm(j.foot), knee: mm(j.knee) }; }
  const col = o.col || C.fig, cp = camPos();
  const parts = [];
  const cap = (a, b, w, c = col) => parts.push({ d: (toCam(a)[2] + toCam(b)[2]) / 2, f: () => { const p = prj(a), q = prj(b); if (p && q) ln(p[0], p[1], q[0], q[1], w * (p[3] + q[3]) / 2, c); } });
  for (const s of ['L', 'R']) { cap(j.hip[s], j.knee[s], 0.13); cap(j.knee[s], j.foot[s], 0.12); }
  // torso: a rounded block from chest to pelvis
  parts.push({ d: toCam(j.chest)[2] + 0.02, f: () => { const p = prj(j.chest), q = prj(j.pelvis); if (!p || !q) return; ln(p[0], p[1], q[0], q[1], 0.29 * (p[3] + q[3]) / 2, col);
    const sl = prj(j.sh.L), sr = prj(j.sh.R); if (sl && sr) ln(sl[0], sl[1], sr[0], sr[1], 0.1 * (sl[3] + sr[3]) / 2, col);
    // scars across the back, seen only when the back faces the camera
    const back = V3.dot(j.F, V3.norm(V3.sub(cp, j.chest)));
    if (o.scars && back < -0.25) scars3(j, o.scars * clamp((-back - 0.25) / 0.3)); } });
  cap(j.neck, j.chest, 0.08);
  for (const s of ['L', 'R']) { cap(j.sh[s], j.elb[s], 0.095); cap(j.elb[s], j.hand[s], 0.085);
    parts.push({ d: toCam(j.hand[s])[2] - 0.001, f: () => { const p = prj(j.hand[s]); if (p) circ(p[0], p[1], 0.05 * p[3], col);
      if (s === 'L' && o.watch !== false) watch3(j); } }); }
  parts.push({ d: toCam(j.head)[2], f: () => head3(j, col, o) });
  parts.sort((a, b) => b.d - a.d);
  ctx.save(); glow(o.glow || 'rgba(255,255,255,0.22)', 14); for (const p of parts) p.f(); ctx.restore();
  return j;
}
function head3(j, col, o) {
  const p = prj(j.head); if (!p) return; const r = 0.11 * p[3];
  circ(p[0], p[1], r, col); noGlow();
  // which way the face points, against the line to the camera: 1 facing us, -1 facing away
  const fd = V3.dot(j.F, V3.norm(V3.sub(camPos(), j.head)));
  ctx.save(); ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.clip();
  // hair: a darker cap; from behind it covers most of the head, from the front only the top
  const side = prj(V3.add(j.head, V3.mul(j.F, 0.05))), sx = side ? (side[0] - p[0]) : 0;
  const up = lerp(0.0, 0.78, (fd + 1) / 2) * r;
  circ(p[0] - sx * 0.9 * (1 - fd * fd), p[1] - up, r * 1.02, o.hair || '#8e8e92'); ctx.restore();
  if (fd > 0.15) { const a = clamp((fd - 0.15) / 0.3);
    for (const sg of [-1, 1]) { const e = prj(V3.add(j.head, V3.add(V3.mul(j.F, 0.1), V3.add(V3.mul(j.R, sg * 0.042), [0, 0.005 - 0.05 * (j.look || 0), 0])))); if (!e) continue;
      ctx.save(); ctx.globalAlpha *= a; ell(e[0], e[1], 0.014 * e[3], (o.blink ? 0.003 : 0.018) * e[3], 0, o.eye || '#000'); ctx.restore(); } }
}
function watch3(j) {
  const a = prj(V3.lerp(j.hand.L, j.elb.L, 0.2)), b = prj(V3.lerp(j.hand.L, j.elb.L, 0.3)); if (!a || !b) return;
  const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l, w = 0.06 * a[3];
  ctx.save(); noGlow(); ln(a[0] + nx * w, a[1] + ny * w, a[0] - nx * w, a[1] - ny * w, 0.032 * a[3], '#141414', 'butt');
  circ(a[0], a[1], 0.022 * a[3], '#141414'); circ(a[0], a[1], 0.014 * a[3], '#9a9a9a'); ctx.restore();
}
// claw marks over the back: many, in rows of three, some fresh (red), some healed (dark)
function scars3(j, k) {
  const R = j.R, U = [0, 1, 0], B = V3.mul(j.F, -0.165);
  const at = (u, v) => prj(V3.add(V3.lerp(j.chest, j.pelvis, v), V3.add(V3.mul(R, u), B)));
  ctx.save(); ctx.globalAlpha *= k; ctx.lineCap = 'round';
  // a grid of claw marks (three parallel cuts each) over the whole back, slanting both ways
  let n = 0;
  for (let row = 0; row < 6; row++) for (let col = 0; col < 3; col++) { n++;
    const u0 = -0.11 + col * 0.09 + (hash(n * 3.7) - 0.5) * 0.05, v0 = 0.04 + row * 0.15 + (hash(n * 1.9) - 0.5) * 0.06, sl = (row + col) % 2 ? 1 : -1;
    const du = sl * (0.05 + hash(n * 5.1) * 0.04), dv = 0.07 + hash(n * 2.3) * 0.05, fresh = hash(n * 9.1) < 0.55;
    for (let m = 0; m < 3; m++) { const a = at(u0 + m * 0.02, v0 + m * 0.012), b = at(u0 + du + m * 0.02, Math.min(1, v0 + dv + m * 0.012)); if (!a || !b) continue;
      if (fresh) { redGlow(6); ln(a[0], a[1], b[0], b[1], 0.009 * a[3], C.red); noGlow(); } else ln(a[0], a[1], b[0], b[1], 0.008 * a[3], '#8a3434'); } }
  ctx.restore();
}

// ---------- the thing in the doorway (it exists only in the mirror) ----------
// feet at (x, z) on the mirror side; it faces the glass. o.reach: [x,y,z] where its right hand goes (through the glass), o.k how far along
const THING_C = '#9a9a9f';
function thing3(x, z, o = {}) {
  const t = o.t || 0, sway = Math.sin(t * 1.3) * 0.01, col = o.col || THING_C;
  const sc = o.sc ?? 1, P = (dx, y, dz = 0) => [x + dx + sway * (y / 2), y * sc, z + dz];
  const head = P(0.02, 1.95), neck0 = P(0.01, 1.78), sh = { L: P(-0.15, 1.72), R: P(0.15, 1.73) }, hip = { L: P(-0.06, 1.0), R: P(0.06, 1.0) };
  const segs = [];
  const cap = (a, b, w) => { const p = prj(a), q = prj(b); if (p && q) ln(p[0], p[1], q[0], q[1], w * (p[3] + q[3]) / 2, col); };
  ctx.save(); glow('rgba(255,255,255,0.18)', 16);
  for (const s of ['L', 'R']) { const kx = s === 'L' ? -0.08 : 0.08; cap(hip[s], P(kx, 0.52, 0.02), 0.055); cap(P(kx, 0.52, 0.02), P(kx * 1.1, 0.02, 0.04), 0.05); }
  cap(P(0, 1.7), P(0, 1.05), 0.15); cap(sh.L, sh.R, 0.07); cap(neck0, head, 0.05);
  const arm = (s, hand) => { const S = sh[s], E = V3.lerp(S, hand, 0.5); E[0] += (s === 'L' ? -0.05 : 0.05); cap(S, E, 0.045); cap(E, hand, 0.04); fingers3(hand, V3.norm(V3.sub(hand, E)), col); };
  arm('L', P(-0.22, 0.6, 0.02));
  if (!o.reach) arm('R', P(0.22, 0.58, 0.02));
  // head: a long skull, tilted, with two dark hollows and no mouth
  const hp = prj(head); if (hp) { ctx.save(); ctx.translate(hp[0], hp[1]); ctx.rotate(0.22 + Math.sin(t * 0.7) * 0.03); ell(0, 0, 0.075 * hp[3], 0.11 * hp[3], 0, col); noGlow();
    for (const sg of [-1, 1]) ell(sg * 0.03 * hp[3], -0.005 * hp[3], 0.017 * hp[3], 0.026 * hp[3], 0, o.eyes || '#050505'); ctx.restore(); }
  ctx.restore();
  return { sh, P };
}
function fingers3(hand, dir, col, len = 0.17) {
  const p = prj(hand); if (!p) return; const q = prj(V3.add(hand, V3.mul(dir, 0.1))); const a0 = q ? Math.atan2(q[1] - p[1], q[0] - p[0]) : Math.PI / 2;
  for (let i = 0; i < 4; i++) { const a = a0 + (i - 1.5) * 0.22, L = len * p[3] * (i === 1 || i === 2 ? 1.1 : 0.9);
    ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.quadraticCurveTo(p[0] + Math.cos(a) * L * 0.6, p[1] + Math.sin(a) * L * 0.6 + 4, p[0] + Math.cos(a) * L, p[1] + Math.sin(a) * L);
    ctx.lineWidth = Math.max(2, 0.016 * p[3]); ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.stroke(); }
}
// its arm through the glass: from its shoulder (mirror side) to the point on the glass, then on into the room to your wrist
function greyArm(shoulder, G, wrist, k = 1, inside = true) {
  const pts = inside ? [shoulder, V3.lerp(shoulder, G, 0.5), G] : [G, V3.lerp(G, wrist, k)];
  ctx.save(); glow('rgba(255,255,255,0.2)', 12);
  for (let i = 0; i < pts.length - 1; i++) { const p = prj(pts[i]), q = prj(pts[i + 1]); if (p && q) ln(p[0], p[1], q[0], q[1], 0.045 * (p[3] + q[3]) / 2, THING_C); }
  ctx.restore();
}
// fingers closed around your wrist
function gripWrist(wrist, k = 1) {
  const p = prj(wrist); if (!p) return; const r = 0.05 * p[3];
  ctx.save(); glow('rgba(255,255,255,0.2)', 10); ctx.lineCap = 'round';
  for (let i = 0; i < 4; i++) { const y = p[1] - r * 0.9 + i * r * 0.6; ctx.beginPath(); ctx.moveTo(p[0] - r * 1.4, y); ctx.quadraticCurveTo(p[0], y + r * 0.5 * k, p[0] + r * 1.4 * k, y - r * 0.2);
    ctx.lineWidth = Math.max(2.5, 0.016 * p[3]); ctx.strokeStyle = THING_C; ctx.stroke(); }
  ctx.restore();
}
// rings spreading over the glass where something passes through it
function glassRipple(G, t0, t) {
  const d = t - t0; if (d < 0 || d > 1.6) return;
  for (let i = 0; i < 3; i++) { const k = d * 0.9 - i * 0.2; if (k <= 0 || k > 1) continue;
    const pts = ringPts(G, [0.04 + 0.22 * easeOut(k), 0, 0], [0, 0.04 + 0.22 * easeOut(k), 0], 36);
    ctx.save(); ctx.globalAlpha *= 0.55 * (1 - k); polyW(pts, null, '#dfe8ef', 3); ctx.restore(); }
}

// ---------- fog on the glass, and what is written in it ----------
// letters on the glass in glass coordinates (x right, y up, metres), drawn as you read them from the room
const RUN_BOX = { x: -0.13, y: 1.5, h: 0.25, w: 0.17, gap: 0.065 };
const LETTERS = {
  R: [[[0, 0], [0, 1]], [[0, 1], [0.55, 1], [0.8, 0.94], [0.92, 0.8], [0.9, 0.64], [0.75, 0.53], [0.5, 0.5], [0, 0.5]], [[0.42, 0.5], [0.95, 0]]],
  U: [[[0, 1], [0, 0.32], [0.08, 0.1], [0.25, 0.01], [0.5, -0.01], [0.75, 0.01], [0.92, 0.1], [1, 0.32], [1, 1]]],
  N: [[[0, 0], [0, 1], [1, 0], [1, 1]]]
};
// all strokes of the word in order, in glass coordinates, with their lengths
function runStrokes() {
  if (runStrokes.c) return runStrokes.c; const out = [];
  'RUN'.split('').forEach((ch, i) => { const x0 = RUN_BOX.x + i * (RUN_BOX.w + RUN_BOX.gap);
    for (const s of LETTERS[ch]) { const pts = s.map(([u, v]) => [x0 + u * RUN_BOX.w, RUN_BOX.y + v * RUN_BOX.h]); let L = 0; for (let k = 1; k < pts.length; k++) L += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]); out.push({ ch: i, pts, L }); } });
  return (runStrokes.c = out);
}
// how much of each letter is written: p[i] 0..1 per letter. Returns the fingertip (glass point) of the stroke being drawn, if any
function runTip(p) {
  let tip = null;
  for (let i = 0; i < 3; i++) { const ss = runStrokes().filter(s => s.ch === i), tot = ss.reduce((a, s) => a + s.L, 0); let left = clamp(p[i]) * tot;
    if (p[i] <= 0 || p[i] >= 1) continue;
    for (const s of ss) { if (left <= s.L) { let l = left; for (let k = 1; k < s.pts.length; k++) { const d = Math.hypot(s.pts[k][0] - s.pts[k - 1][0], s.pts[k][1] - s.pts[k - 1][1]);
          if (l <= d) { const u = l / d; tip = [lerp(s.pts[k - 1][0], s.pts[k][0], u), lerp(s.pts[k - 1][1], s.pts[k][1], u)]; break; } l -= d; } break; }
      left -= s.L; } }
  return tip;
}
let fogC = null;
// fog: amount 0..1 over the glass; p: letters written; drip: 0..1 how far the drops have run
function fog3(t, amt, p = [0, 0, 0], drip = 0, wipe = null) {
  if (amt <= 0) return;
  if (!fogC) { fogC = document.createElement('canvas'); fogC.width = W; fogC.height = H; }
  const fx = fogC.getContext('2d'); fx.setTransform(1, 0, 0, 1, 0, 0); fx.globalCompositeOperation = 'source-over'; fx.clearRect(0, 0, W, H);
  // the fog layer in screen space, built from the glass outline (the current canvas transform is the camera push; apply it too)
  fx.setTransform(ctx.getTransform());
  const sp = glassPts().map(prj); if (sp.some(q => !q)) return;
  fx.beginPath(); fx.moveTo(sp[0][0], sp[0][1]); for (const q of sp.slice(1)) fx.lineTo(q[0], q[1]); fx.closePath();
  const cx = (sp[0][0] + sp[2][0]) / 2, cy = (sp[0][1] + sp[2][1]) / 2;
  const g = fx.createRadialGradient(cx, cy + 120, 40, cx, cy, 900); g.addColorStop(0, `rgba(205,214,220,${0.62 * amt})`); g.addColorStop(1, `rgba(190,200,206,${0.42 * amt})`);
  fx.fillStyle = g; fx.fill();
  if (grainC) { fx.save(); fx.clip(); fx.globalAlpha = 0.18 * amt; fx.globalCompositeOperation = 'destination-out'; fx.drawImage(grainC[2], 0, 0, W, H); fx.restore(); }
  // wipe the strokes out of the fog, as far as they are written
  fx.globalCompositeOperation = 'destination-out'; fx.lineCap = 'round'; fx.lineJoin = 'round'; fx.shadowColor = 'rgba(0,0,0,1)'; fx.shadowBlur = 6;
  for (let i = 0; i < 3; i++) { const ss = runStrokes().filter(s => s.ch === i), tot = ss.reduce((a, s) => a + s.L, 0); let left = clamp(p[i]) * tot;
    for (const s of ss) { if (left <= 0) break; let l = left; fx.beginPath();
      for (let k = 0; k < s.pts.length; k++) { const q = prj([s.pts[k][0], s.pts[k][1], 0]);
        if (k === 0) { fx.moveTo(q[0], q[1]); continue; }
        const d = Math.hypot(s.pts[k][0] - s.pts[k - 1][0], s.pts[k][1] - s.pts[k - 1][1]);
        if (l < d) { const u = l / d, e = prj([lerp(s.pts[k - 1][0], s.pts[k][0], u), lerp(s.pts[k - 1][1], s.pts[k][1], u), 0]); fx.lineTo(e[0], e[1]); break; }
        fx.lineTo(q[0], q[1]); l -= d; }
      fx.lineWidth = 0.038 * prj([RUN_BOX.x, RUN_BOX.y, 0])[3]; fx.stroke(); left -= s.L; } }
  fx.fillStyle = '#000'; if (wipe) for (const [x, y, r] of wipe) { const q = prj([x, y, 0]); if (q) { fx.beginPath(); fx.arc(q[0], q[1], (r || 0.08) * q[3], 0, Math.PI * 2); fx.fill(); } }
  // drops running down from the bottom of the letters
  if (drip > 0) for (let i = 0; i < 9; i++) { const x = RUN_BOX.x + 0.01 + hash(i * 4.3) * (3 * RUN_BOX.w + 2 * RUN_BOX.gap), y0 = RUN_BOX.y + 0.01, y1 = y0 - (0.04 + hash(i * 7.9) * 0.14) * clamp(drip * (0.6 + hash(i)));
    const a = prj([x, y0, 0]), b = prj([x, y1, 0]); fx.lineWidth = 0.009 * a[3]; fx.beginPath(); fx.moveTo(a[0], a[1]); fx.lineTo(b[0], b[1]); fx.stroke(); }
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(fogC, 0, 0); ctx.restore();
}
// the towel over the mirror; bump 0..1 pushes it out from behind, at bx,by on the glass
function towel3(t, k = 1, bump = 0, bx = 0, by = 1.5) {
  if (k <= 0) return;
  const top = MIR.y1 + 0.06, bot = lerp(top, MIR.y0 - 0.12, k), x0 = MIR.x0 - 0.06, x1 = MIR.x1 + 0.06;
  const sp = polyW([[x0, bot, 0.03], [x1, bot, 0.03], [x1, top, 0.03], [x0, top, 0.03]], '#b9b9bd', null);
  ctx.save(); ctx.globalAlpha *= 0.35; for (let i = 1; i < 9; i++) { const x = lerp(x0, x1, i / 9) + Math.sin(i * 2.1) * 0.02; lnW([x, top, 0.032], [x + 0.01, bot, 0.032], 3, '#7c7c80'); } ctx.restore();
  lnW([x0, bot, 0.033], [x1, bot, 0.033], 4, '#d6d6da'); lnW([x0 - 0.04, top, 0.035], [x1 + 0.04, top, 0.035], 6, '#9a9a9e');
  if (bump > 0 && k > 0.95) { const c = prj([bx, by, 0.03]); if (c) { const r = (0.12 + 0.05 * bump) * c[3];
    const g = ctx.createRadialGradient(c[0] - r * 0.3, c[1] - r * 0.3, r * 0.1, c[0], c[1], r); g.addColorStop(0, `rgba(240,240,244,${0.9 * bump})`); g.addColorStop(0.7, `rgba(120,120,126,${0.5 * bump})`); g.addColorStop(1, 'rgba(120,120,126,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(c[0], c[1], r, 0, Math.PI * 2); ctx.fill(); } }
}

// ---------- the whole bathroom shot ----------
// o.me: your pose; o.refl: the pose your reflection copies (default: yours); o.reflOff: draw no reflection; o.door; o.thing {x,z,reach,...}
// o.fog/o.run/o.drip; o.water; o.inMirror(): extra things drawn inside the glass; o.front(): extra things in the room, in front of the counter
// o.scars: on the reflection; o.meScars; o.towel/o.bump
function bathroom(t, o = {}) {
  setCam(o.cam || CAMS.ots);
  const camZ = CAM.z;
  // the real room: the walls you can see from here
  if (CAM.cyw < 0) {   // looking back into the room (away from the mirror)
    room3(0, { door: o.realDoor ?? 0, inDoor: o.inRealDoor });
    if (o.me) body3(o.me, { scars: o.meScars });
    counter3(0);
    if (o.front) o.front();
    return;
  }
  // side walls, floor and ceiling of the real room, then the mirror wall
  { const { x0, x1, y1 } = ROOM, z1 = ROOM.z1;
    polyW([[x0, 0, 0], [x1, 0, 0], [x1, 0, z1], [x0, 0, z1]], FLOOR_C, EDGE_C, 2);
    for (let x = x0 + 0.42; x < x1; x += 0.42) lnW([x, 0, 0], [x, 0, z1], 1.5, '#222');
    for (let z = 0.42; z < z1; z += 0.42) lnW([x0, 0, z], [x1, 0, z], 1.5, '#222');
    polyW([[x0, y1, 0], [x1, y1, 0], [x1, y1, z1], [x0, y1, z1]], CEIL_C, EDGE_C, 2);
    for (const x of [x0, x1]) { polyW([[x, 0, 0], [x, 0, z1], [x, y1, z1], [x, y1, 0]], SIDE_C, EDGE_C, 2); for (let y = 0.3; y < 1.25; y += 0.3) lnW([x, y, 0], [x, y, z1], 1.5, TILE_C); } }
  mirrorWall();
  // inside the glass
  ctx.save();
  if (clipGlass()) {
    ctx.fillStyle = '#000'; ctx.fillRect(-W, -H, 3 * W, 3 * H);
    const th = o.thing;
    room3(1, { door: o.door ?? 0, inDoor: th && th.inDoor ? () => thing3(th.x, th.z, th) : null });
    if (th && !th.inDoor) thing3(th.x, th.z, th);
    if (o.behind) o.behind();
    if (!o.reflOff && (o.refl || o.me)) body3(o.refl || o.me, { mirror: true, col: o.reflCol || '#dcdcde', scars: o.scars, blink: o.reflBlink });
    if (o.inMirror) o.inMirror();
    counter3(1); waterStream(1, o.water || 0);
    ctx.save(); ctx.globalAlpha = 0.14; ctx.fillStyle = '#000'; ctx.fillRect(-W, -H, 3 * W, 3 * H); ctx.restore();   // a mirror gives back a little less light
    glassSheen();
    if (o.glassFx) o.glassFx();
    fog3(t, o.fog || 0, o.run || [0, 0, 0], o.drip || 0, o.wipe);
  }
  ctx.restore();
  mirrorFrame({ light: o.light ?? 1 });
  if (o.towel) towel3(t, o.towel, o.bump || 0, o.bx, o.by);
  counter3(0); waterStream(0, o.water || 0);
  if (o.behindMe) o.behindMe();
  if (o.me && !o.meOff && o.me.z < camZ - 0.2) body3(o.me, { scars: o.meScars });
  if (o.front) o.front();
}


// 9-11 November 1989: the border opens, the ghost stations come back to life.
// shots:
//   bornholmer (7.1 s) - night, the steel Bösebrücke at Bornholmer Straße: a crowd streams across under sodium
//                        lamps towards the floodlit West, the border barrier raised; from 3.4 s the camera tilts
//                        and pans down to the S-Bahn tracks in the cutting and the dark, sealed ghost platform
//   stop       (7.2 s) - dark sealed platform at Jannowitzbrücke: headlights approach, the train brakes and,
//                        for the first time in 28 years, stops (~5.0 s); the fluorescent tubes flicker on
//   sign       (2.2 s) - close-up: a cardboard destination sign taped inside the train's front window,
//                        hand-lettered in marker (procedural strokes): JANNOWITZBRÜCKE / WESTBERLIN
//   ticket     (3.0 s) - close-up under a warm lamp: a BVG ticket printed 2,70 DM slides across the counter,
//                        a hand drops the coins (2 DM, 50 Pf, 20 Pf)
//   crowd      (4.6 s) - from inside the carriage: the doors slide open onto a platform packed with people
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries, mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';
import { AMBER, tileTex, concreteTex, rng, lerp } from './lib.js';
import { makeComposer, glow, beam, normalFromHeight, smooth, flicker } from './look.js';

// ---------------------------------------------------------------- helpers
function ctex(THREE, w, h, draw, rep = [1, 1]) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}
function seg(THREE, mesh, a, b) {
  const d = new THREE.Vector3().subVectors(b, a); const L = d.length();
  mesh.position.copy(a).add(b).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.multiplyScalar(1 / L));
  mesh.scale.set(1, L, 1);
}
function makeDust(THREE, N, xr, yr, zr, size, seed, color = 0xffe2c0) {
  const r = rng(seed), pos = new Float32Array(N * 3), seeds = new Float32Array(N);
  for (let i = 0; i < N; i++) { pos[i * 3] = lerp(xr[0], xr[1], r()); pos[i * 3 + 1] = lerp(yr[0], yr[1], r()); pos[i * 3 + 2] = lerp(zr[0], zr[1], r()); seeds[i] = r() * 100; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const c = document.createElement('canvas'); c.width = c.height = 32; const x = c.getContext('2d'); const gr = x.createRadialGradient(16, 16, 0, 16, 16, 16); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0, 0, 32, 32);
  const pts = new THREE.Points(g, new THREE.PointsMaterial({ size, map: new THREE.CanvasTexture(c), color, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false }));
  return { pts, base: pos.slice(), seeds };
}
function driftDust(d, t, a = 0.15) {
  const p = d.pts.geometry.attributes.position;
  for (let i = 0; i < p.count; i++) { const s = d.seeds[i];
    p.array[i * 3] = d.base[i * 3] + Math.sin(t * 0.13 + s) * a;
    p.array[i * 3 + 1] = d.base[i * 3 + 1] + Math.sin(t * 0.09 + s * 1.7) * a * 0.8;
    p.array[i * 3 + 2] = d.base[i * 3 + 2] + Math.cos(t * 0.11 + s) * a; }
  p.needsUpdate = true;
}

// ---- crowd: merged low-poly people in a few variants, drawn as InstancedMeshes (origin at the feet, facing +z)
function personGeo(THREE, kind) {
  const parts = [];
  const P = (geo, x, y, z, rx = 0, ry = 0, rz = 0, sx = 1, sy = 1, sz = 1) => {
    const m = new THREE.Matrix4().compose(new THREE.Vector3(x, y, z), new THREE.Quaternion().setFromEuler(new THREE.Euler(rx, ry, rz)), new THREE.Vector3(sx, sy, sz));
    const g = geo.toNonIndexed ? geo.toNonIndexed() : geo; g.applyMatrix4(m); parts.push(g);
  };
  const woman = kind === 'woman';
  const prof = (woman ? [[0, 0.5], [0.3, 0.5], [0.26, 0.8], [0.21, 1.1], [0.22, 1.3], [0.23, 1.4], [0.2, 1.47], [0.1, 1.51], [0, 1.52]]
    : [[0, 0.52], [0.28, 0.52], [0.265, 0.75], [0.235, 1.0], [0.23, 1.2], [0.25, 1.36], [0.24, 1.44], [0.14, 1.5], [0.06, 1.53], [0, 1.53]]).map(([r, y]) => new THREE.Vector2(r, y));
  P(new THREE.LatheGeometry(prof, 14), 0, 0, 0, 0, 0, 0, 1, 1, 0.7);
  for (const sx of [-1, 1]) {
    P(new THREE.CylinderGeometry(0.065, 0.055, 0.56, 7), sx * 0.1, 0.28, 0);
    P(new THREE.BoxGeometry(0.1, 0.07, 0.24), sx * 0.1, 0.035, 0.05);
  }
  P(new THREE.CylinderGeometry(0.05, 0.06, 0.08, 8), 0, 1.57, 0);
  P(new THREE.SphereGeometry(0.105, 12, 10), 0, 1.69, 0.01, 0, 0, 0, 0.9, 1.1, 1);
  if (kind === 'hat') { P(new THREE.CylinderGeometry(0.1, 0.115, 0.1, 12), 0, 1.81, 0); P(new THREE.CylinderGeometry(0.18, 0.18, 0.012, 14), 0, 1.77, 0); }
  if (kind === 'cap') P(new THREE.SphereGeometry(0.115, 12, 6, 0, Math.PI * 2, 0, Math.PI / 2), 0, 1.72, 0.0, 0, 0, 0, 1, 0.8, 1.05);
  if (woman) P(new THREE.SphereGeometry(0.13, 12, 8, 0, Math.PI * 2, 0, Math.PI * 0.7), 0, 1.71, -0.02, 0, 0, 0, 1, 1.2, 1);
  // arms
  const raise = kind === 'wave' || kind === 'both';
  P(new THREE.CapsuleGeometry(0.06, 0.52, 3, 7), 0.27, 1.15, 0.02, 0, 0, 0.1);                       // left arm down
  if (kind === 'both') P(new THREE.CapsuleGeometry(0.06, 0.55, 3, 7), 0.3, 1.78, 0.05, 0, 0, -0.35); // left arm up
  if (raise) { P(new THREE.CapsuleGeometry(0.06, 0.55, 3, 7), -0.3, 1.8, 0.04, 0.15, 0, 0.3); P(new THREE.SphereGeometry(0.06, 8, 6), -0.42, 2.12, 0.08); }
  else P(new THREE.CapsuleGeometry(0.06, 0.52, 3, 7), -0.27, 1.15, 0.02, 0, 0, -0.1);
  if (kind === 'bag') P(new THREE.BoxGeometry(0.1, 0.3, 0.38), 0.33, 0.72, 0);
  const g = mergeGeometries(parts.map(p => { const q = p.index ? p.toNonIndexed() : p; for (const k of Object.keys(q.attributes)) if (k !== 'position' && k !== 'normal') q.deleteAttribute(k); return q; }));
  const gi = mergeVertices(g, 1e-4); gi.computeVertexNormals();
  return gi;
}
const KINDS = ['hat', 'plain', 'woman', 'cap', 'wave', 'both', 'bag'];
function makeCrowd(THREE, list, mat) {
  // list: [{kind, x, y, z, ry, s, ...}]
  const byKind = {}; list.forEach(p => (byKind[p.kind] ||= []).push(p));
  const meshes = [];
  for (const k of Object.keys(byKind)) {
    const im = new THREE.InstancedMesh(personGeo(THREE, k), mat, byKind[k].length);
    im.castShadow = true; im.receiveShadow = true; im.userData.people = byKind[k];
    const col = new THREE.Color();
    byKind[k].forEach((p, i) => { const v = p.tone ?? 0.25; col.setRGB(v, v * 0.97, v * 0.93); im.setColorAt(i, col); });
    im.frustumCulled = false;
    meshes.push(im);
  }
  return meshes;
}
const _m4 = { };
function placeCrowd(THREE, meshes, fn) {
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), pos = new THREE.Vector3(), sc = new THREE.Vector3();
  for (const im of meshes) {
    im.userData.people.forEach((p, i) => {
      const o = fn(p);                                      // {x,y,z,ry,rx,rz,s,sy}
      e.set(o.rx ?? 0, o.ry ?? 0, o.rz ?? 0); q.setFromEuler(e); pos.set(o.x, o.y, o.z); sc.set(o.s, o.s * (o.sy ?? 1), o.s);
      m.compose(pos, q, sc); im.setMatrixAt(i, m);
    });
    im.instanceMatrix.needsUpdate = true;
  }
}

// gripping hand: wrist at origin, along +y, palm +z, fingers curl to +z
function makeHand(THREE, skin, sleeve, curl = 1) {
  const g = new THREE.Group();
  const add = (geo, mat, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; g.add(m); return m; };
  add(new THREE.CylinderGeometry(0.058, 0.062, 0.12, 14), sleeve, 0, -0.06, 0);
  add(new RoundedBoxGeometry(0.084, 0.1, 0.034, 3, 0.014), skin, 0, 0.042, 0);
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const fseg = (a, b, r) => { const m = add(new THREE.CylinderGeometry(r, r, 1, 8), skin, 0, 0, 0); seg(THREE, m, a, b); add(new THREE.SphereGeometry(r, 8, 6), skin, b.x, b.y, b.z); };
  [[-0.03, 0.0092, 0.9], [-0.01, 0.0102, 1.0], [0.01, 0.0098, 0.96], [0.03, 0.0086, 0.8]].forEach(([fx, r, l]) => {
    const p0 = V(fx, 0.09, 0), p1 = V(fx, 0.09 + 0.042 * l, 0.012 * curl), p2 = p1.clone().add(V(0, 0.03 * l * (1 - 0.6 * curl), 0.028 * l * curl)), p3 = p2.clone().add(V(0, 0.02 * l * (1 - 1.2 * curl), 0.02 * l * curl));
    add(new THREE.SphereGeometry(r * 1.1, 8, 6), skin, p0.x, p0.y, p0.z); fseg(p0, p1, r); fseg(p1, p2, r * 0.95); fseg(p2, p3, r * 0.88);
  });
  fseg(V(0.04, 0.02, 0.01), V(0.058, 0.055, 0.03), 0.012); fseg(V(0.058, 0.055, 0.03), V(0.045, 0.085, 0.045), 0.011);
  return g;
}

// ---- handwriting: single-stroke block capitals, drawn with a jittery marker
const GLYPHS = {
  A: [['M', 0, 1, 'L', 0.3, 0, 'L', 0.6, 1], ['M', 0.12, 0.64, 'L', 0.49, 0.64]],
  B: [['M', 0, 1, 'L', 0, 0, 'L', 0.3, 0, 'Q', 0.56, 0, 0.56, 0.24, 'Q', 0.56, 0.47, 0.3, 0.47, 'L', 0, 0.47], ['M', 0.28, 0.47, 'Q', 0.62, 0.47, 0.62, 0.73, 'Q', 0.62, 1, 0.3, 1, 'L', 0, 1]],
  C: [['M', 0.6, 0.15, 'Q', 0.48, 0, 0.32, 0, 'Q', 0, 0, 0, 0.5, 'Q', 0, 1, 0.32, 1, 'Q', 0.5, 1, 0.6, 0.84]],
  E: [['M', 0.55, 0, 'L', 0, 0, 'L', 0, 1, 'L', 0.56, 1], ['M', 0, 0.49, 'L', 0.42, 0.49]],
  I: [['M', 0.06, 0, 'L', 0.06, 1]],
  J: [['M', 0.48, 0, 'L', 0.48, 0.72, 'Q', 0.48, 1, 0.24, 1, 'Q', 0.05, 1, 0, 0.8]],
  K: [['M', 0, 0, 'L', 0, 1], ['M', 0.55, 0, 'L', 0.02, 0.58], ['M', 0.18, 0.42, 'L', 0.6, 1]],
  L: [['M', 0, 0, 'L', 0, 1, 'L', 0.5, 1]],
  N: [['M', 0, 1, 'L', 0, 0, 'L', 0.58, 1, 'L', 0.58, 0]],
  O: [['M', 0.32, 0, 'Q', 0, 0, 0, 0.5, 'Q', 0, 1, 0.32, 1, 'Q', 0.64, 1, 0.64, 0.5, 'Q', 0.64, 0, 0.3, 0.02]],
  R: [['M', 0, 1, 'L', 0, 0, 'L', 0.3, 0, 'Q', 0.58, 0, 0.58, 0.25, 'Q', 0.58, 0.5, 0.3, 0.5, 'L', 0, 0.5], ['M', 0.24, 0.5, 'L', 0.6, 1]],
  S: [['M', 0.56, 0.13, 'Q', 0.46, 0, 0.29, 0, 'Q', 0.03, 0, 0.03, 0.24, 'Q', 0.03, 0.44, 0.3, 0.5, 'Q', 0.6, 0.56, 0.6, 0.77, 'Q', 0.6, 1, 0.3, 1, 'Q', 0.1, 1, 0, 0.86]],
  T: [['M', 0, 0, 'L', 0.62, 0], ['M', 0.31, 0, 'L', 0.31, 1]],
  U: [['M', 0, 0, 'L', 0, 0.7, 'Q', 0, 1, 0.3, 1, 'Q', 0.6, 1, 0.6, 0.7, 'L', 0.6, 0]],
  'Ü': [['M', 0, 0, 'L', 0, 0.7, 'Q', 0, 1, 0.3, 1, 'Q', 0.6, 1, 0.6, 0.7, 'L', 0.6, 0], ['M', 0.14, -0.2, 'L', 0.16, -0.15], ['M', 0.44, -0.2, 'L', 0.46, -0.15]],
  W: [['M', 0, 0, 'L', 0.19, 1, 'L', 0.4, 0.32, 'L', 0.61, 1, 'L', 0.8, 0]],
  Z: [['M', 0, 0, 'L', 0.58, 0, 'L', 0, 1, 'L', 0.6, 1]],
  '-': [['M', 0.0, 0.5, 'L', 0.38, 0.5]],
  ' ': [],
};
function glyphPolys(ch) {
  return (GLYPHS[ch] || []).map(cmds => {
    const pts = []; let i = 0, cx = 0, cy = 0;
    while (i < cmds.length) {
      const c = cmds[i];
      if (c === 'M' || c === 'L') { cx = cmds[i + 1]; cy = cmds[i + 2]; if (c === 'L') { const [px, py] = pts[pts.length - 1]; for (let k = 1; k <= 4; k++) pts.push([lerp(px, cx, k / 4), lerp(py, cy, k / 4)]); } else pts.push([cx, cy]); i += 3; }
      else { const qx = cmds[i + 1], qy = cmds[i + 2], x = cmds[i + 3], y = cmds[i + 4]; for (let k = 1; k <= 8; k++) { const u = k / 8; pts.push([(1 - u) * (1 - u) * cx + 2 * (1 - u) * u * qx + u * u * x, (1 - u) * (1 - u) * cy + 2 * (1 - u) * u * qy + u * u * y]); } cx = x; cy = y; i += 5; }
    }
    return pts;
  });
}
function glyphWidth(ch) { if (ch === ' ') return 0.45; let m = 0; for (const p of glyphPolys(ch)) for (const [x] of p) m = Math.max(m, x); return m; }
function handwrite(g, text, x0, y0, size, seed, opt = {}) {
  const r = rng(seed); let x = x0;
  const slant = opt.slant ?? 0.1;
  for (const ch of text) {
    const sc = size * (0.94 + r() * 0.12), rot = (r() - 0.5) * 0.08, yo = (r() - 0.5) * size * 0.06 + Math.sin(x * 0.01) * size * 0.03;
    const polys = glyphPolys(ch);
    for (const p of polys) {
      const pts = p.map(([u, v]) => { const jx = (r() - 0.5) * 0.025, jy = (r() - 0.5) * 0.025; const px = (u + jx) * sc * 0.82, py = (v + jy) * sc;
        return [x + px * Math.cos(rot) - py * Math.sin(rot) + (sc - py) * slant, y0 + yo + px * Math.sin(rot) + py * Math.cos(rot)]; });
      // marker: a wide pass, then a darker slightly narrower core, ink pooling at the start
      for (const [w, a] of [[sc * 0.13, 0.55], [sc * 0.1, 0.85]]) {
        g.strokeStyle = `rgba(16,16,20,${a})`; g.lineWidth = w * (opt.weight ?? 1); g.lineCap = 'round'; g.lineJoin = 'round';
        g.beginPath(); pts.forEach(([px, py], k) => k ? g.lineTo(px, py) : g.moveTo(px, py)); g.stroke();
      }
      g.fillStyle = 'rgba(8,8,10,0.6)'; g.beginPath(); g.arc(pts[0][0], pts[0][1], sc * 0.07 * (opt.weight ?? 1), 0, 7); g.fill();
    }
    x += (glyphWidth(ch) * 0.82 + 0.3) * sc + (r() - 0.5) * size * 0.05;
  }
  return x;
}
function measure(text, size) { let w = 0; for (const ch of text) w += (glyphWidth(ch) * 0.82 + 0.3) * size; return w; }

// ---------------------------------------------------------------- scene
export async function setup(THREE, renderer, W, H) {
  const shot = new URLSearchParams(location.search).get('shot') || 'stop';
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x030303);
  const camera = new THREE.PerspectiveCamera(38, W / H, 0.02, 900);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.8, metalness: 0, ...o });
  const r = rng(1989);
  const ctx = { THREE, scene, camera, shot };
  const skinMat = std({ color: 0xb08f78, roughness: 0.6 });

  if (shot === 'bornholmer') {
    // ================= Bösebrücke, night of 9 November 1989
    scene.background = new THREE.Color(0x07080b);
    scene.fog = new THREE.FogExp2(0x0b0c10, 0.012);
    const STREET = 8;
    // sky glow over the West + a few clouds
    const sky = new THREE.Mesh(new THREE.SphereGeometry(400, 32, 16), new THREE.MeshBasicMaterial({ side: THREE.BackSide, fog: false, map: ctex(THREE, 512, 256, (g, w, h) => {
      const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#040507'); gr.addColorStop(0.42, '#0d0f14'); gr.addColorStop(0.5, '#2a2620'); gr.addColorStop(0.56, '#08090b'); gr.addColorStop(1, '#030303');
      g.fillStyle = gr; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 60; i++) { g.fillStyle = `rgba(80,80,90,${0.03 + r() * 0.05})`; g.beginPath(); g.ellipse(r() * w, h * 0.15 + r() * h * 0.3, 20 + r() * 60, 4 + r() * 10, 0, 0, 7); g.fill(); }
    }) }));
    scene.add(sky);
    // cutting with the S-Bahn tracks (tracks run along x), retaining walls at z = +-26
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(600, 52), std({ map: concreteTex(THREE, [60, 6], 61, 70), roughness: 0.95 })); ground.rotation.x = -Math.PI / 2; scene.add(ground);
    const wallM = std({ map: concreteTex(THREE, [40, 1], 62, 95), roughness: 0.9 });
    for (const sz of [-1, 1]) { const w = new THREE.Mesh(new THREE.PlaneGeometry(600, STREET), wallM); w.position.set(0, STREET / 2, sz * 26); w.rotation.y = sz > 0 ? Math.PI : 0; scene.add(w); }
    const streetM = std({ map: concreteTex(THREE, [30, 30], 63, 60), roughness: 0.85 });
    for (const sz of [-1, 1]) { const s = new THREE.Mesh(new THREE.PlaneGeometry(600, 200), streetM); s.rotation.x = -Math.PI / 2; s.position.set(0, STREET, sz * (26 + 100)); s.receiveShadow = true; scene.add(s); }
    const railM = std({ color: 0x8a8a8a, metalness: 0.9, roughness: 0.3 });
    const sleeperM = std({ color: 0x2a2724 });
    const trackZ = [-20, -15.5, -9.5, -1.5, 6, 11, 17];
    const sl = new THREE.InstancedMesh(new THREE.BoxGeometry(0.25, 0.16, 2.5), sleeperM, trackZ.length * 400); let k = 0; const m4 = new THREE.Matrix4();
    for (const tz of trackZ) { for (const o of [-0.72, 0.72]) { const rl = new THREE.Mesh(new THREE.BoxGeometry(600, 0.14, 0.07), railM); rl.position.set(0, 0.22, tz + o); scene.add(rl); }
      for (let i = 0; i < 400; i++) { m4.makeTranslation(-150 + i * 0.75, 0.08, tz); sl.setMatrixAt(k++, m4); } }
    scene.add(sl);
    // ballast strips
    for (const tz of trackZ) { const b = new THREE.Mesh(new THREE.BoxGeometry(600, 0.1, 3.4), std({ map: concreteTex(THREE, [80, 1], 64, 80) })); b.position.set(0, 0.03, tz); scene.add(b); }
    // the sealed ghost station: island platform between tracks at -9.5 and -1.5, east of the bridge (+x)
    const platM = std({ map: concreteTex(THREE, [30, 2], 65, 105), roughness: 0.9 });
    const PX0 = 12, PX1 = 150, PZ = -5.5;
    const plat = new THREE.Mesh(new THREE.BoxGeometry(PX1 - PX0, 0.95, 5.2), platM); plat.position.set((PX0 + PX1) / 2, 0.475, PZ); plat.receiveShadow = true; scene.add(plat);
    for (const sz of [-1, 1]) { const e = new THREE.Mesh(new THREE.BoxGeometry(PX1 - PX0, 0.02, 0.3), std({ color: 0xbab5aa })); e.position.set((PX0 + PX1) / 2, 0.96, PZ + sz * 2.45); scene.add(e); }
    const steelM = std({ color: 0x26262a, metalness: 0.6, roughness: 0.5 });
    for (let x = 44; x < PX1 - 2; x += 8) { const c = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.14, 3.2, 10), steelM); c.position.set(x, 0.95 + 1.6, PZ); c.castShadow = true; scene.add(c);
      const arm = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.25, 5.6), steelM); arm.position.set(x, 4.1, PZ); scene.add(arm); }
    const roof = new THREE.Mesh(new THREE.BoxGeometry(PX1 - 42, 0.15, 6.2), std({ color: 0x1d1d1f, roughness: 0.7 })); roof.position.set((42 + PX1) / 2, 4.3, PZ); roof.rotation.x = 0.0; roof.castShadow = true; scene.add(roof);
    const roofEdge = new THREE.Mesh(new THREE.BoxGeometry(PX1 - 42, 0.45, 0.08), std({ color: 0x3a3a3a })); roofEdge.position.set((42 + PX1) / 2, 4.15, PZ - 3.1); scene.add(roofEdge);
    // old station name boards, dead lamps, boarded kiosk, weeds
    const nameTex = ctex(THREE, 1024, 160, (g, w, h) => { g.fillStyle = '#d8d3c6'; g.fillRect(0, 0, w, h); g.fillStyle = '#18291c'; g.fillRect(0, 0, w, 14); g.fillRect(0, h - 14, w, 14);
      g.fillStyle = '#121212'; g.font = 'bold 86px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('Bornholmer Straße', w / 2, h / 2 + 4);
      for (let i = 0; i < 400; i++) { g.fillStyle = `rgba(60,50,40,${r() * 0.25})`; g.fillRect(r() * w, r() * h, 3 + r() * 10, 2 + r() * 4); } });
    for (const x of [24, 62]) { const sb = new THREE.Mesh(new THREE.PlaneGeometry(4, 0.62), std({ map: nameTex, roughness: 0.7 })); sb.position.set(x, 3.0, PZ - 0.06); sb.scale.setScalar(1.4); sb.rotation.y = Math.PI; scene.add(sb);
      const sb2 = sb.clone(); sb2.rotation.y = 0; sb2.position.z = PZ + 0.06; scene.add(sb2);
      for (const dx of [-1.7, 1.7]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.4, 8), steelM); p.position.set(x + dx, 2.05, PZ); scene.add(p); } }
    // dead platform lamps
    for (let x = 16; x < 44; x += 7) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.08, 3.6, 8), steelM); p.position.set(x, 2.75, PZ + 1.4); scene.add(p);
      const gl = new THREE.Mesh(new THREE.SphereGeometry(0.22, 12, 8), std({ color: 0x5a5a58, roughness: 0.3 })); gl.position.set(x, 4.6, PZ + 1.4); scene.add(gl); }
    const kiosk = new THREE.Mesh(new THREE.BoxGeometry(3, 2.4, 2), std({ map: ctex(THREE, 256, 256, (g, w, h) => { g.fillStyle = '#4a4238'; g.fillRect(0, 0, w, h); for (let x = 0; x < w; x += 22) { g.fillStyle = `rgba(0,0,0,${0.2 + r() * 0.3})`; g.fillRect(x, 0, 3, h); } }) }));
    kiosk.position.set(48, 0.95 + 1.2, PZ); scene.add(kiosk);
    const weedM = std({ color: 0x5a5c50, roughness: 1 });
    const weeds = new THREE.InstancedMesh(new THREE.SphereGeometry(0.3, 7, 5), weedM, 160);
    for (let i = 0; i < 160; i++) { const x = PX0 + r() * (PX1 - PX0), z = PZ + (r() - 0.5) * 4.6; const s = 0.5 + r(); m4.compose(new THREE.Vector3(x, 0.95, z), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, r() * 3, 0)), new THREE.Vector3(s * (0.6 + r()), s * 0.45, s)); weeds.setMatrixAt(i, m4); }
    scene.add(weeds);
    // border fence + wall along the cutting (the station lay inside the border strip)
    const wallW = new THREE.Mesh(new THREE.BoxGeometry(400, 3.6, 0.25), std({ map: concreteTex(THREE, [100, 1], 66, 150), roughness: 0.9 })); wallW.position.set(200 + 14, 1.8, 22.5); scene.add(wallW);
    const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 400, 12), std({ map: concreteTex(THREE, [100, 1], 66, 150) })); pipe.rotation.z = Math.PI / 2; pipe.position.set(214, 3.7, 22.5); scene.add(pipe);
    // ---- the bridge: deck along z over the cutting, curved steel trusses each side
    const DX = 9.5, ZL = 34;
    const deckM = std({ map: concreteTex(THREE, [4, 16], 67, 70), roughness: 0.75 });
    const deck = new THREE.Mesh(new THREE.BoxGeometry(DX * 2, 0.6, ZL * 2 + 0.2), deckM); deck.position.set(0, STREET - 0.3, 0); deck.receiveShadow = true; deck.castShadow = true; scene.add(deck);
    const under = new THREE.Mesh(new THREE.BoxGeometry(DX * 2 - 1, 1.4, ZL * 2), std({ color: 0x18181a, metalness: 0.4, roughness: 0.6 })); under.position.set(0, STREET - 1.3, 0); scene.add(under);
    for (const sx of [-1, 1]) { const kerb = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.18, ZL * 2), std({ map: concreteTex(THREE, [1, 20], 68, 95) })); kerb.position.set(sx * (DX - 1.6), STREET + 0.09, 0); kerb.receiveShadow = true; scene.add(kerb); }
    const truss = std({ color: 0x3a3c40, metalness: 0.65, roughness: 0.45 });
    const beamBox = (a, b, w = 0.42) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, 1, w), truss); seg(THREE, m, a, b); m.castShadow = true; scene.add(m); return m; };
    const topY = z => STREET + 1.2 + 7.5 * (1 - (z / ZL) ** 2);
    const V = (x, y, z) => new THREE.Vector3(x, y, z);
    for (const sx of [-1, 1]) {
      const x = sx * DX; const N = 12;
      for (let i = 0; i < N; i++) {
        const z0 = -ZL + (i / N) * ZL * 2, z1 = -ZL + ((i + 1) / N) * ZL * 2;
        beamBox(V(x, topY(z0), z0), V(x, topY(z1), z1), 0.6);                       // top chord
        beamBox(V(x, STREET + 0.4, z0), V(x, STREET + 0.4, z1), 0.7);                // bottom chord
        beamBox(V(x, STREET + 0.4, z1), V(x, topY(z1), z1), 0.32);                  // verticals
        beamBox(V(x, STREET + 0.4, i < N / 2 ? z0 : z1), V(x, topY(i < N / 2 ? z1 : z0), i < N / 2 ? z1 : z0), 0.26); // diagonals
      }
      beamBox(V(x, STREET + 0.4, -ZL), V(x, topY(-ZL), -ZL), 0.4);
      // railing
      const rail = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.06, ZL * 2), truss); rail.position.set(sx * (DX - 0.35), STREET + 1.2, 0); scene.add(rail);
    }
    // overhead cross bracing between the trusses in the middle part
    for (let i = 3; i <= 9; i++) { const z = -ZL + (i / 12) * ZL * 2; if (topY(z) - STREET > 6.3) beamBox(V(-DX, topY(z) - 0.2, z), V(DX, topY(z) - 0.2, z), 0.25); }
    // ---- street lamps (sodium) on the bridge and the approach
    const lamps = [];
    const lampZ = [-44, -24, -4, 16];
    let li = 0;
    for (const z of lampZ) for (const sx of [-1, 1]) {
      if (z === 16 && sx < 0) continue;
      const x = sx * (DX - 1.2);
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.1, 8, 8), steelM); pole.position.set(x, STREET + 4, z); scene.add(pole);
      const arm = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.08, 0.08), steelM); arm.position.set(x - sx * 0.7, STREET + 8, z); scene.add(arm);
      const head = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.18, 0.35), steelM); head.position.set(x - sx * 1.35, STREET + 7.95, z); scene.add(head);
      const lp = V(x - sx * 1.35, STREET + 7.8, z);
      const bulb = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.05, 0.25), new THREE.MeshBasicMaterial({ color: new THREE.Color(3, 1.7, 0.6) })); bulb.position.copy(lp); scene.add(bulb);
      const h = glow(THREE, AMBER, 4.5, 0.75); h.position.copy(lp); scene.add(h);
      const bm = beam(THREE, AMBER, 8, 5, 0.035); bm.position.copy(lp); scene.add(bm);
      if (li < 6) { const pl = new THREE.SpotLight(AMBER, 70, 30, 1.0, 0.7, 1.5); pl.position.copy(lp); pl.target.position.set(lp.x, STREET, lp.z); if (li < 2) { pl.castShadow = true; pl.shadow.mapSize.set(1024, 1024); pl.shadow.bias = -0.0005; } scene.add(pl, pl.target); lamps.push(pl); }
      li++;
    }
    // ---- the barrier, raised, and the control hut at the eastern end
    const boomTex = ctex(THREE, 256, 16, (g, w, h) => { for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? '#1a1a1a' : '#e8e4da'; g.fillRect(i * 32, 0, 32, h); } });
    const boomG = new THREE.Group(); boomG.position.set(DX - 1.0, STREET + 1.05, -33); scene.add(boomG);
    const boom = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.22, 9), std({ map: boomTex, roughness: 0.5 })); boom.material.map.repeat.set(1, 1); boom.geometry.translate(0, 0, 0); boom.position.set(-4.5, 0, 0); boom.rotation.y = Math.PI / 2; boomG.add(boom);
    boomG.rotation.z = -1.2;
    const boomLamp = new THREE.PointLight(0xffe0b0, 25, 14, 1.6); boomLamp.position.set(DX + 2.5, STREET + 3, -35); scene.add(boomLamp);
    const bpost = new THREE.Mesh(new THREE.BoxGeometry(0.4, 1.1, 0.4), std({ color: 0x777770 })); bpost.position.set(DX - 1.0, STREET + 0.55, -33); scene.add(bpost);
    const hut = new THREE.Mesh(new THREE.BoxGeometry(2.4, 2.6, 2.4), std({ color: 0x8c8a82, roughness: 0.8 })); hut.position.set(-DX - 4, STREET + 1.3, -38); hut.castShadow = true; scene.add(hut);
    const hutWin = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 0.8), new THREE.MeshBasicMaterial({ color: new THREE.Color(1.6, 1.2, 0.7) })); hutWin.position.set(-DX - 2.79, STREET + 1.7, -38); hutWin.rotation.y = Math.PI / 2; scene.add(hutWin);
    // ---- floodlit West at the far end: TV lights and haze
    const westGlow = glow(THREE, 0xfff0dc, 40, 0.55); westGlow.position.set(0, STREET + 4, 75); scene.add(westGlow);
    const flood = new THREE.SpotLight(0xfff0e0, 900, 140, 0.35, 0.6, 1.4); flood.position.set(0, STREET + 10, 80); flood.target.position.set(0, STREET, -10); scene.add(flood, flood.target);
    for (const sx of [-1, 1]) { const fg = glow(THREE, 0xffffff, 3, 1); fg.position.set(sx * 6, STREET + 6, 62); scene.add(fg); }
    // city blocks silhouettes on both sides
    const blockM = std({ color: 0x0d0d0f, roughness: 1 });
    const winM = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.3, 0.9, 0.5) });
    for (let i = 0; i < 26; i++) { const sxz = i % 2 ? 1 : -1; const bw = 10 + r() * 14, bh = 12 + r() * 14;
      const b = new THREE.Mesh(new THREE.BoxGeometry(bw, bh, 12), blockM); const bx = sxz * (22 + r() * 40), bz = -80 + i * 9 + (r() - 0.5) * 6; if (Math.abs(bz) < 30) continue; b.position.set(bx, STREET + bh / 2, bz); scene.add(b);
      for (let j = 0; j < 6; j++) if (r() < 0.5) { const wm = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 1.4), winM); wm.position.set(bx - sxz * (bw / 2 + 0.02), STREET + 3 + r() * (bh - 5), bz + (r() - 0.5) * 9); wm.rotation.y = sxz > 0 ? -Math.PI / 2 : Math.PI / 2; scene.add(wm); } }
    scene.add(new THREE.HemisphereLight(0x6a7488, 0x0a0908, 0.22));
    // border-strip floodlights on tall poles along the cutting: cold light on the dead station
    for (const [x, z] of [[34, 21], [78, 21], [122, 21], [22, -24]]) {
      const hidden = z < 0;                 // a light from the street above the cutting, fixture out of frame
      const lp = V(x, hidden ? 13 : 11.8, hidden ? -27 : z - 0.6);
      if (!hidden) { const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.16, 12, 8), steelM); pole.position.set(x, 6, z); scene.add(pole); }
      if (!hidden) { const lm = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.5, 0.3), new THREE.MeshBasicMaterial({ color: new THREE.Color(2.4, 2.4, 2.5) })); lm.position.copy(lp); scene.add(lm);
        const g = glow(THREE, 0xe8eeff, 5, 0.7); g.position.copy(lp); scene.add(g); }
      const sp = new THREE.SpotLight(0xdfe6ff, hidden ? 220 : 320, 60, 0.75, 0.6, 1.4); sp.position.copy(lp); sp.target.position.set(x + (z < 0 ? 4 : 6), 0, PZ); scene.add(sp, sp.target);
      if (!hidden) { const bm = beam(THREE, 0xdfe6ff, 16, 7, 0.03); bm.position.copy(lp); bm.lookAt(x + 6, 0, PZ); bm.rotateX(-Math.PI / 2); scene.add(bm); }
    }
    const moon = new THREE.DirectionalLight(0x9aa4c0, 0.25); moon.position.set(60, 80, 40); scene.add(moon);
    // ---- the crowd streaming West (+z) across the bridge and along the approach road
    const ppl = [];
    for (let i = 0; i < 420; i++) {
      const kind = KINDS[Math.floor(r() * KINDS.length)];
      ppl.push({ kind: r() < 0.12 ? (r() < 0.5 ? 'wave' : 'both') : kind, x: (r() - 0.5) * (DX * 2 - 2.2), z0: r() * 130, v: 1.0 + r() * 0.6, s: 0.9 + r() * 0.17, ph: r() * 10, tone: 0.05 + r() * 0.11, sway: (r() - 0.5) * 0.3 });
    }
    const crowdMat = std({ color: 0xffffff, roughness: 0.9 });
    const crowd = makeCrowd(THREE, ppl, crowdMat); crowd.forEach(m => scene.add(m));
    // a trickle of people towards the cutting rail (looking down at the dark station)
    const post = makeComposer(THREE, renderer, scene, camera, W, H, { bloom: 0.75, bloomRadius: 0.6, bloomThreshold: 0.7, exposure: 1.4 });
    Object.assign(ctx, { crowd, STREET, lamps, ZL, PZ }, post);
    return ctx;
  }

  if (shot === 'ticket') {
    // ================= ticket counter close-up
    scene.background = new THREE.Color(0x050403);
    scene.fog = new THREE.FogExp2(0x050403, 0.25);
    const counter = new THREE.Mesh(new THREE.BoxGeometry(2, 0.05, 1.2), std({ map: ctex(THREE, 512, 256, (g, w, h) => { g.fillStyle = '#4c4b48'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 6000; i++) { const v = 60 + r() * 50; g.fillStyle = `rgba(${v},${v},${v - 3},0.25)`; g.fillRect(r() * w, r() * h, 2, 2); }
      for (let i = 0; i < 30; i++) { g.strokeStyle = `rgba(200,190,170,${0.05 + r() * 0.08})`; g.lineWidth = 1; g.beginPath(); const x = r() * w, y = r() * h; g.moveTo(x, y); g.lineTo(x + 60 + r() * 120, y + (r() - 0.5) * 20); g.stroke(); } }), roughness: 0.35, metalness: 0.1 }));
    counter.position.y = -0.025; counter.receiveShadow = true; scene.add(counter);
    // glass partition with the money slot
    const glassM = new THREE.MeshStandardMaterial({ color: 0xc8ccc8, roughness: 0.08, metalness: 0.1, transparent: true, opacity: 0.12, depthWrite: false });
    const glassP = new THREE.Mesh(new THREE.PlaneGeometry(2, 0.9), glassM); glassP.position.set(0, 0.5, -0.32); scene.add(glassP);
    const frameM = std({ color: 0x2c2b28, metalness: 0.5, roughness: 0.4 });
    const fr = new THREE.Mesh(new THREE.BoxGeometry(2, 0.04, 0.05), frameM); fr.position.set(0, 0.06, -0.32); scene.add(fr);
    const trough = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.02, 0.36), std({ color: 0x8a8a84, metalness: 0.8, roughness: 0.3 })); trough.position.set(0.0, -0.005, -0.32); trough.receiveShadow = true; scene.add(trough);
    // clerk's side: dark booth, a sign
    const back = new THREE.Mesh(new THREE.PlaneGeometry(3, 2), std({ color: 0x1a1816 })); back.position.set(0, 0.6, -1.0); scene.add(back);
    const signT = ctex(THREE, 512, 128, (g, w, h) => { g.fillStyle = '#1c2a20'; g.fillRect(0, 0, w, h); g.fillStyle = '#e4dfd2'; g.font = 'bold 64px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('FAHRKARTEN', w / 2, h / 2 + 3); });
    const sign = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.22), std({ map: signT })); sign.position.set(-0.2, 0.75, -0.9); scene.add(sign);
    // the ticket
    const tTex = ctex(THREE, 512, 288, (g, w, h) => {
      g.fillStyle = '#d9d3c2'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 3000; i++) { g.fillStyle = `rgba(120,100,70,${r() * 0.08})`; g.fillRect(r() * w, r() * h, 2, 2); }
      g.strokeStyle = '#3a3226'; g.lineWidth = 3; g.strokeRect(12, 12, w - 24, h - 24);
      for (let y = 22; y < h - 20; y += 6) { g.fillStyle = 'rgba(150,120,80,0.12)'; g.fillRect(16, y, w - 32, 2); }
      g.fillStyle = '#1e1a14'; g.font = 'bold 50px "DejaVu Sans"'; g.fillText('BVG', 30, 70);
      g.font = '17px "DejaVu Sans Condensed"'; g.fillText('Berliner Verkehrs-Betriebe', 30, 96);
      g.font = 'bold 30px "DejaVu Sans Condensed"'; g.fillText('Fahrschein', 280, 58); g.font = '19px "DejaVu Sans Condensed"'; g.fillText('Einzelfahrt  U-Bahn · Bus', 280, 86);
      g.font = 'bold 80px "DejaVu Sans Condensed"'; g.fillText('2,70 DM', 30, 200);
      g.font = '18px "DejaVu Sans Mono"'; g.fillText('Nr. 0418 7735', 30, 250); g.fillText('Erwachsene', 330, 250);
      // date stamp from the validator
      g.save(); g.translate(412, 160); g.rotate(-0.08); g.strokeStyle = 'rgba(40,40,70,0.8)'; g.lineWidth = 3; g.strokeRect(-70, -32, 140, 64);
      g.fillStyle = 'rgba(40,40,70,0.82)'; g.font = 'bold 24px "DejaVu Sans Mono"'; g.textAlign = 'center'; g.fillText('11.11.89', 0, -2); g.font = '16px "DejaVu Sans Mono"'; g.fillText('14:07  U8', 0, 22); g.restore();
    });
    const ticket = new THREE.Mesh(new THREE.BoxGeometry(0.105, 0.0008, 0.059), [std({ color: 0xcfc4a4 }), std({ color: 0xcfc4a4 }), std({ map: tTex, roughness: 0.85 }), std({ color: 0xcfc4a4 }), std({ color: 0xcfc4a4 }), std({ color: 0xcfc4a4 })]);
    ticket.castShadow = true; ticket.receiveShadow = true; scene.add(ticket);
    // coins: 2 DM, 50 Pf, 20 Pf
    const coinTex = (label, sub, base) => ctex(THREE, 256, 256, (g, w, h) => { g.fillStyle = base; g.fillRect(0, 0, w, h);
      const gr = g.createRadialGradient(100, 90, 10, 128, 128, 128); gr.addColorStop(0, 'rgba(255,255,255,0.25)'); gr.addColorStop(1, 'rgba(0,0,0,0.25)'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
      g.strokeStyle = 'rgba(0,0,0,0.35)'; g.lineWidth = 6; g.beginPath(); g.arc(128, 128, 112, 0, 7); g.stroke();
      g.fillStyle = 'rgba(30,25,15,0.55)'; g.font = 'bold 92px "DejaVu Serif"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(label, 128, 112);
      g.font = 'bold 26px "DejaVu Serif"'; g.fillText(sub, 128, 186); });
    const coinN = (label) => normalFromHeight(THREE, 128, 128, (g, w, h) => { g.fillStyle = '#555'; g.fillRect(0, 0, w, h); g.strokeStyle = '#fff'; g.lineWidth = 4; g.beginPath(); g.arc(64, 64, 56, 0, 7); g.stroke();
      g.fillStyle = '#fff'; g.font = 'bold 46px "DejaVu Serif"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(label, 64, 56); }, 2.0);
    const coins = [];
    for (const [d, label, sub, base, metal] of [[0.0268, '2', 'DEUTSCHE MARK', '#b9b8b2', 0xc8c8c4], [0.02, '50', 'PFENNIG', '#bdbbb4', 0xc4c2bc], [0.0215, '20', 'PFENNIG', '#c9a35a', 0xd2a95a]]) {
      const top = std({ map: coinTex(label, sub, base), normalMap: coinN(label), metalness: 0.9, roughness: 0.32, color: 0xffffff });
      const edge = std({ color: metal, metalness: 1, roughness: 0.35 });
      const c = new THREE.Mesh(new THREE.CylinderGeometry(d / 2, d / 2, 0.0021, 40), [edge, top, top]); c.castShadow = true; c.receiveShadow = true; scene.add(c); coins.push(c);
    }
    // customer's hand + clerk's fingers
    const sleeve = std({ color: 0x3e3a35, roughness: 0.95 });
    const glove = std({ color: 0x2e2621, roughness: 0.42, metalness: 0.05 });   // November: leather gloves
    const hand = makeHand(THREE, glove, sleeve, 0.55); scene.add(hand);
    const clerk = new THREE.Group();
    // warm lamp
    const lampP = new THREE.Vector3(0.15, 0.62, 0.05);
    const lamp = new THREE.SpotLight(AMBER, 2.4, 3, 0.65, 0.6, 1.6); lamp.position.copy(lampP); lamp.target.position.set(0, 0, -0.05);
    lamp.castShadow = true; lamp.shadow.mapSize.set(1024, 1024); lamp.shadow.bias = -0.0002; lamp.shadow.camera.near = 0.1; scene.add(lamp, lamp.target);
    const shade = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.16, 24, 1, true), std({ color: 0x1e1e1c, metalness: 0.5, side: THREE.DoubleSide })); shade.position.copy(lampP).add(new THREE.Vector3(0, 0.06, 0)); scene.add(shade);
    const halo = glow(THREE, AMBER, 0.5, 0.8); halo.position.copy(lampP); scene.add(halo);
    const fill = new THREE.PointLight(0x9aa4b8, 0.15, 3, 2); fill.position.set(-0.6, 0.4, 0.6); scene.add(fill);
    scene.add(new THREE.HemisphereLight(0x8890a0, 0x0a0806, 0.05));
    const dust = makeDust(THREE, 120, [-0.5, 0.5], [0.05, 0.7], [-0.4, 0.4], 0.0018, 7); scene.add(dust.pts);
    const post = makeComposer(THREE, renderer, scene, camera, W, H, { bloom: 0.6, bloomRadius: 0.5, bloomThreshold: 0.7, exposure: 1.1, dof: { focus: 0.4, aperture: 0.02, maxblur: 0.01 } });
    Object.assign(ctx, { ticket, coins, hand, clerk, dust }, post);
    return ctx;
  }

  // ================= U-Bahn station Jannowitzbrücke (stop / sign / crowd)
  scene.fog = new THREE.FogExp2(0x060505, shot === 'crowd' ? 0.03 : 0.035);
  const L = 110, HT = 4.6, TRK = 0;               // track centre at x=0, platform on +x side
  const PW = 5.5, PX = 1.6;                        // platform from x=PX to PX+PW, top at y=1.0
  const tileN = normalFromHeight(THREE, 256, 256, (g, w, h) => { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; for (let y = 0; y < h; y += 16) for (let x = 0; x < w; x += 32) g.fillRect(x + 1, y + 1, 30, 14); }, 2.5, [40, 2]);
  const tileM = std({ map: tileTex(THREE, { repeat: [40, 2], tile: 32, grout: 3, base: 150, vary: 22, dirt: 0.6, seed: 89 }), normalMap: tileN, roughness: 0.45 });
  // track-side wall (x = -2.4) and platform back wall (x = PX+PW)
  const wallX = [-2.4, PX + PW];
  for (const [i, x] of wallX.entries()) { const w = new THREE.Mesh(new THREE.PlaneGeometry(L, HT), tileM); w.position.set(x, HT / 2, 0); w.rotation.y = i === 0 ? Math.PI / 2 : -Math.PI / 2; w.receiveShadow = true; scene.add(w); }
  // a darker tile band at eye height
  const bandM = std({ map: tileTex(THREE, { repeat: [40, 0.4], tile: 32, grout: 3, base: 70, vary: 14, dirt: 0.2, seed: 90 }), roughness: 0.4 });
  for (const [i, x] of wallX.entries()) { const b = new THREE.Mesh(new THREE.PlaneGeometry(L, 0.4), bandM); b.position.set(x + (i === 0 ? 0.01 : -0.01), 2.5, 0); b.rotation.y = i === 0 ? Math.PI / 2 : -Math.PI / 2; scene.add(b); }
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(PX + PW + 2.4, L), std({ map: concreteTex(THREE, [3, 30], 91, 85) })); ceil.rotation.x = Math.PI / 2; ceil.position.set((PX + PW - 2.4) / 2, HT, 0); scene.add(ceil);
  const bed = new THREE.Mesh(new THREE.PlaneGeometry(4, L + 300), std({ map: concreteTex(THREE, [2, 160], 92, 45) })); bed.rotation.x = -Math.PI / 2; bed.position.set(-0.4, 0, -150); scene.add(bed);
  const railM = std({ color: 0x9a9a9a, metalness: 0.9, roughness: 0.3 });
  for (const o of [-0.72, 0.72]) { const rl = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.14, L + 300), railM); rl.position.set(TRK + o, 0.22, -150); scene.add(rl); }
  const slp = new THREE.InstancedMesh(new THREE.BoxGeometry(2.4, 0.14, 0.25), std({ color: 0x1e1c1a }), 520);
  { const m4 = new THREE.Matrix4(); for (let i = 0; i < 520; i++) { m4.makeTranslation(TRK, 0.08, 55 - i * 0.78); slp.setMatrixAt(i, m4); } } scene.add(slp);
  const platM = std({ map: concreteTex(THREE, [3, 40], 93, 118), roughness: 0.6 });
  const plat = new THREE.Mesh(new THREE.BoxGeometry(PW, 1.0, L), platM); plat.position.set(PX + PW / 2, 0.5, 0); plat.receiveShadow = true; scene.add(plat);
  const edge = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.012, L), std({ color: 0xdcd6c6, roughness: 0.5 })); edge.position.set(PX + 0.2, 1.006, 0); scene.add(edge);
  // tunnel beyond the station (-z) and behind (+z)
  const tunM = std({ map: concreteTex(THREE, [50, 2], 94, 55), roughness: 0.95 });
  for (const zc of [-L / 2 - 150, L / 2 + 150]) {
    const w1 = new THREE.Mesh(new THREE.PlaneGeometry(300, HT), tunM); w1.position.set(-2.4, HT / 2, zc); w1.rotation.y = Math.PI / 2; scene.add(w1);
    const w2 = new THREE.Mesh(new THREE.PlaneGeometry(300, HT), tunM); w2.position.set(1.8, HT / 2, zc); w2.rotation.y = -Math.PI / 2; scene.add(w2);
    const c = new THREE.Mesh(new THREE.PlaneGeometry(4.2, 300), tunM); c.rotation.x = Math.PI / 2; c.position.set(-0.3, HT, zc); scene.add(c);
    const e = new THREE.Mesh(new THREE.PlaneGeometry(PW + 0.2, HT), tunM); e.position.set(PX + 0.2 + PW / 2, HT / 2, Math.sign(zc) * L / 2); e.rotation.y = zc < 0 ? 0 : Math.PI; scene.add(e);
  }
  // columns on the platform
  const colM = std({ color: 0x3c3c3a, metalness: 0.5, roughness: 0.5 });
  for (let z = -L / 2 + 6; z < L / 2; z += 7) { const c = new THREE.Mesh(new THREE.BoxGeometry(0.34, HT - 1, 0.34), colM); c.position.set(PX + 2.6, 1 + (HT - 1) / 2, z); c.castShadow = true; c.receiveShadow = true; scene.add(c); }
  // station name in the wall across the track and on the back wall
  const nameT = ctex(THREE, 1024, 150, (g, w, h) => { g.fillStyle = '#d9d4c5'; g.fillRect(0, 0, w, h); g.strokeStyle = '#1b1b1b'; g.lineWidth = 8; g.strokeRect(6, 6, w - 12, h - 12);
    g.fillStyle = '#141414'; g.font = 'bold 92px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('JANNOWITZBRÜCKE', w / 2, h / 2 + 5);
    for (let i = 0; i < 500; i++) { g.fillStyle = `rgba(70,60,45,${r() * 0.22})`; g.fillRect(r() * w, r() * h, 3 + r() * 9, 2 + r() * 4); } });
  const nameM = std({ map: nameT, roughness: 0.5 });
  for (const z of [-34, -10, 14, 38]) { const n = new THREE.Mesh(new THREE.PlaneGeometry(4.4, 0.64), nameM); n.position.set(-2.38, 2.55, z); n.rotation.y = Math.PI / 2; scene.add(n);
    const n2 = new THREE.Mesh(new THREE.PlaneGeometry(4.4, 0.64), nameM); n2.position.set(PX + PW - 0.02, 2.55, z + 3.5); n2.rotation.y = -Math.PI / 2; scene.add(n2); }
  // posters long faded, a bench
  const benchM = std({ color: 0x3a3632, roughness: 0.6 });
  for (const z of [-20, 4, 26]) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.06, 2.2), benchM); b.position.set(PX + PW - 0.5, 1.45, z); scene.add(b);
    for (const dz of [-0.9, 0.9]) { const l = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.45, 0.06), benchM); l.position.set(PX + PW - 0.5, 1.22, z + dz); scene.add(l); } }
  // fluorescent tubes in housings along the platform (off at first)
  const tubes = [];
  const tubeOn = new THREE.Color(2.2, 2.1, 1.9);
  const housingM = std({ color: 0x2e2e2c, metalness: 0.4, roughness: 0.5 });
  let lightN = 0;
  for (let z = -48, i = 0; z <= 48; z += 6, i++) {
    for (const x of [PX + 1.1, PX + 4.1]) {
      const hsg = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.08, 1.6), housingM); hsg.position.set(x, HT - 0.12, z); scene.add(hsg);
      const tb = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.5, 8), new THREE.MeshBasicMaterial({ color: 0x151515 })); tb.rotation.x = Math.PI / 2; tb.position.set(x, HT - 0.19, z); scene.add(tb);
      const h = glow(THREE, 0xfff4e4, 1.6, 0.5); h.position.set(x, HT - 0.22, z); h.scale.set(2.4, 0.8, 1); h.material.opacity = 0; scene.add(h);
      const ent = { tb, h, z, seed: i * 2 + (x > 3 ? 1 : 0), light: null };
      if (x < 3 && Math.abs(z - (shot === 'crowd' ? 0 : -6)) < 26 && lightN < 7) { const pl = new THREE.PointLight(shot === 'crowd' ? AMBER : 0xffe9cc, 0, 14, 1.5); pl.position.set(x + 0.8, HT - 0.35, z); scene.add(pl); ent.light = pl; lightN++; }
      tubes.push(ent);
    }
  }
  scene.add(new THREE.HemisphereLight(0x7c8696, 0x090807, shot === 'stop' ? 0.12 : 0.03));
  if (shot === 'stop') {   // a single caged emergency bulb kept burning in the sealed station
    const ep = new THREE.Vector3(PX + PW - 0.4, 3.2, -14);
    const eb = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(2.2, 1.5, 0.8) })); eb.position.copy(ep); scene.add(eb);
    const eg = glow(THREE, AMBER, 0.9, 0.7); eg.position.copy(ep); scene.add(eg);
    const el = new THREE.PointLight(AMBER, 2.5, 14, 1.6); el.position.copy(ep); scene.add(el);
  }

  // ---- the U8 train (Großprofil): flat front, headlights low, destination window, lit interior
  const train = new THREE.Group(); scene.add(train);
  const bodyM = std({ color: 0xa69a6c, roughness: 0.45, metalness: 0.25 });
  const darkM = std({ color: 0x141414, roughness: 0.5 });
  const CW2 = 2.65, CH2 = 3.25, CL = 16;
  const winTex = ctex(THREE, 512, 128, (g, w, h) => { g.fillStyle = '#c9b597'; g.fillRect(0, 0, w, h); const rr = rng(4);
    for (let i = 0; i < 12; i++) { if (rr() < 0.25) continue; const x = 18 + i * 42 + rr() * 8, s = 0.75 + rr() * 0.35; g.fillStyle = '#0a0a0a'; g.beginPath(); g.arc(x, 60 - 12 * s, 12 * s, 0, 7); g.fill(); g.beginPath(); g.ellipse(x, 128, 22 * s, 56 * s, 0, 0, 7); g.fill(); } });
  const winM = new THREE.MeshBasicMaterial({ map: winTex, color: new THREE.Color(1.15, 1.05, 0.9) });
  for (let c = 0; c < 3; c++) {
    const z0 = c * (CL + 0.6);
    const car = new THREE.Mesh(new RoundedBoxGeometry(CW2, CH2, CL, 3, 0.12), bodyM); car.position.set(0, 0.55 + CH2 / 2, z0 + CL / 2); car.castShadow = true; train.add(car);
    const skirt = new THREE.Mesh(new THREE.BoxGeometry(CW2 - 0.1, 0.5, CL - 1), darkM); skirt.position.set(0, 0.45, z0 + CL / 2); train.add(skirt);
    for (const sx of [-1, 1]) {
      for (let k = 0; k < 4; k++) { const wz = z0 + 1.6 + k * 4.2; const wnd = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 0.95), winM); wnd.position.set(sx * (CW2 / 2 + 0.005), 2.45, wz + 1.3); wnd.rotation.y = sx * Math.PI / 2; train.add(wnd);
        const door = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 2.0), darkM); door.position.set(sx * (CW2 / 2 + 0.006), 1.75, wz - 0.75); door.rotation.y = sx * Math.PI / 2; if (!(c === 0 && sx > 0 && k === 1 && shot === 'crowd')) train.add(door); }
    }
    for (const sx of [-1, 1]) { const ilight = new THREE.PointLight(0xffe0b0, 0, 6, 2); ilight.position.set(sx * 1.8, 2.3, z0 + CL / 2); train.add(ilight); train.userData.ilights = (train.userData.ilights || []).concat(ilight); }
  }
  // front face (at z = 0, facing -z)
  const front = new THREE.Group(); train.add(front);
  const fwin = new THREE.Mesh(new THREE.PlaneGeometry(1.9, 1.0), std({ color: 0x0b0c0d, roughness: 0.4, metalness: 0.3, transparent: true, opacity: 0.3, depthWrite: false })); fwin.position.set(0, 2.55, -0.065); fwin.rotation.y = Math.PI; front.add(fwin);
  const fdest = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 0.24), new THREE.MeshBasicMaterial({ map: ctex(THREE, 512, 96, (g, w, h) => { g.fillStyle = '#0a0a0a'; g.fillRect(0, 0, w, h); g.fillStyle = '#e8dcc0'; g.font = 'bold 60px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('U8', 60, h / 2 + 2); g.font = 'bold 48px "DejaVu Sans Condensed"'; g.fillText('Leinestraße', 300, h / 2 + 2); }), color: new THREE.Color(1.3, 1.2, 1.1) }));
  fdest.position.set(0, 3.28, -0.012); fdest.rotation.y = Math.PI; front.add(fdest);
  const head = new THREE.SpotLight(0xfff1dc, 0, 90, 0.33, 0.5, 1.1); head.position.set(0, 1.2, -0.3); head.target.position.set(0, 0.8, -40); head.castShadow = false; train.add(head, head.target);
  const headBeam = beam(THREE, 0xfff2de, 30, 3.4, 0.03); headBeam.rotation.x = Math.PI / 2; headBeam.position.set(0, 1.2, -0.2); train.add(headBeam);
  const hl = [];
  for (const o of [-0.85, 0.85]) { const lens = new THREE.Mesh(new THREE.CircleGeometry(0.11, 20), new THREE.MeshBasicMaterial({ color: new THREE.Color(3, 2.9, 2.6) })); lens.position.set(o, 1.15, -0.015); lens.rotation.y = Math.PI; train.add(lens);
    const hg = glow(THREE, 0xfff6e8, 1.6, 0.9); hg.position.set(o, 1.15, -0.2); train.add(hg); hl.push(hg); }
  // coupler, wipers, a number
  const coup = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.25, 0.5), darkM); coup.position.set(0, 0.75, -0.2); train.add(coup);
  // the handwritten sign taped inside the front window
  const signT = ctex(THREE, 1024, 512, (g, w, h) => {
    // cardboard
    g.fillStyle = '#c7b48e'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 9000; i++) { const v = r(); g.fillStyle = v > 0.5 ? `rgba(230,215,180,${r() * 0.12})` : `rgba(90,70,40,${r() * 0.1})`; g.fillRect(r() * w, r() * h, 1 + r() * 3, 1 + r() * 3); }
    for (let y = 0; y < h; y += 9) { g.fillStyle = 'rgba(80,60,30,0.04)'; g.fillRect(0, y, w, 3); }   // corrugation
    g.fillStyle = 'rgba(70,55,30,0.18)'; g.fillRect(0, h * 0.48, w, 4);                                // fold
    // pencil guide line + marker letters
    g.strokeStyle = 'rgba(60,60,60,0.25)'; g.lineWidth = 1.5; g.beginPath(); g.moveTo(40, 225); g.lineTo(w - 40, 218); g.stroke();
    const t1 = 'JANNOWITZBRÜCKE', s1 = Math.min(118, 900 / measure(t1, 1)); handwrite(g, t1, (w - measure(t1, s1)) / 2 - 10, 95, s1, 11, { slant: 0.08 });
    const t2 = 'WESTBERLIN', s2 = Math.min(150, 880 / measure(t2, 1)); const x2 = (w - measure(t2, s2)) / 2; const xe = handwrite(g, t2, x2, 300, s2, 23, { slant: 0.1, weight: 1.1 });
    // underline
    const rr = rng(5); g.strokeStyle = 'rgba(14,14,18,0.85)'; g.lineWidth = 12; g.lineCap = 'round'; g.beginPath(); g.moveTo(x2 - 10, 462); for (let k = 1; k <= 12; k++) g.lineTo(lerp(x2 - 10, xe - 20, k / 12), 462 - k * 1.2 + (rr() - 0.5) * 5); g.stroke();
  });
  const signM = std({ map: signT, roughness: 0.95 });
  const card = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.6, 8, 4), signM); card.position.set(0.08, 2.5, -0.03); card.rotation.set(0, Math.PI, 0.025); train.add(card);
  { const pa = card.geometry.attributes.position; for (let i = 0; i < pa.count; i++) { const x = pa.getX(i), y = pa.getY(i); pa.setZ(i, 0.012 * Math.sin(x * 2.6) * Math.cos(y * 3)); } card.geometry.computeVertexNormals(); }
  const tapeM = std({ color: 0xd8d2bc, roughness: 0.4, transparent: true, opacity: 0.75 });
  for (const [x, y, rz] of [[-0.5, 0.29, 0.6], [0.52, 0.27, -0.5], [-0.52, -0.27, -0.55], [0.5, -0.29, 0.6]]) { const tp = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.045), tapeM); tp.position.set(0.08 - x, 2.5 + y, -0.045); tp.rotation.set(0, Math.PI, rz); train.add(tp); }
  // cab interior behind the sign (dim), glass reflections

  const cabLamp = new THREE.PointLight(0xffe6c4, 0, 4, 2); cabLamp.position.set(0.4, 3.4, -0.9); train.add(cabLamp);
  const glass = new THREE.Mesh(new THREE.PlaneGeometry(1.9, 1.0), new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.3, metalness: 0.0, transmission: 0, transparent: true, opacity: 0.08, depthWrite: false }));
  glass.position.set(0, 2.55, -0.07); glass.rotation.y = Math.PI; train.add(glass);
  const streak = new THREE.Mesh(new THREE.PlaneGeometry(1.9, 1.0), new THREE.MeshBasicMaterial({ map: ctex(THREE, 512, 256, (g, w, h) => { g.clearRect(0, 0, w, h);
    for (let i = 0; i < 4; i++) { const x = 60 + i * 120 + r() * 40; const gr = g.createLinearGradient(x, 0, x + 80, 0); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.5, `rgba(255,250,240,${0.08 + r() * 0.08})`); gr.addColorStop(1, 'rgba(255,255,255,0)');
      g.save(); g.translate(x, 0); g.transform(1, 0, -0.5, 1, 0, 0); g.fillStyle = gr; g.fillRect(-40, 0, 120, h); g.restore(); } }), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
  streak.position.set(0, 2.55, -0.075); streak.rotation.y = Math.PI; train.add(streak);
  // window frame
  for (const [w, h, x, y] of [[2.05, 0.08, 0, 3.08], [2.05, 0.08, 0, 2.02], [0.08, 1.1, -1.0, 2.55], [0.08, 1.1, 1.0, 2.55]]) { const f = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.1), darkM); f.position.set(x, y, -0.05); train.add(f); }
  train.position.set(TRK, 0, -400);
  train.rotation.y = shot === 'crowd' ? 0 : Math.PI;     // front faces +z (towards the camera) when it drives in

  // ---- the crowd on the platform (crowd shot): dense, warm lit
  let crowd = null;
  if (shot === 'crowd') {
    const ppl = [];
    for (let i = 0; i < 230; i++) {
      const x = PX + 0.55 + Math.pow(r(), 0.8) * (PW - 0.8), z = (r() - 0.5) * 22;
      if (Math.abs(x - (PX + 2.6)) < 0.3 && Math.abs(((z + 1000) % 7) - 3.5) < 0.3) continue;
      const kind = r() < 0.22 ? (r() < 0.6 ? 'wave' : 'both') : KINDS[Math.floor(r() * 4)];
      ppl.push({ kind, x, z, s: 0.92 + r() * 0.16, ry: -Math.PI / 2 + (r() - 0.5) * 1.2, ph: r() * 10, tone: 0.05 + r() * 0.16 });
    }
    // the very front row, pressing towards the door
    for (let i = 0; i < 9; i++) ppl.push({ kind: i % 3 === 0 ? 'wave' : KINDS[i % 4], x: PX + 0.45 + r() * 0.3, z: -2.2 + i * 0.55 + r() * 0.2, s: 0.95 + r() * 0.1, ry: -Math.PI / 2 + (r() - 0.5) * 0.5, ph: r() * 10, tone: 0.06 + r() * 0.12 });
    crowd = makeCrowd(THREE, ppl, std({ color: 0xffffff, roughness: 0.85 }));
    crowd.forEach(m => scene.add(m));
    // carriage interior around the camera (car 0 sits at z 0..16; doors on +x)
    const inner = new THREE.Group(); train.add(inner);
    const iw = std({ color: 0xbdb5a2, roughness: 0.6 });
    const floorI = new THREE.Mesh(new THREE.PlaneGeometry(CW2 - 0.15, CL - 0.3), std({ color: 0x4a4540, roughness: 0.8 })); floorI.rotation.x = -Math.PI / 2; floorI.position.set(0, 1.05, CL / 2); inner.add(floorI);
    const ceilI = new THREE.Mesh(new THREE.PlaneGeometry(CW2 - 0.15, CL - 0.3), iw); ceilI.rotation.x = Math.PI / 2; ceilI.position.set(0, 3.45, CL / 2); inner.add(ceilI);
    // walls inside with window holes: panels below/above windows, piers between
    const dz0 = 1.6 + 1 * 4.2 - 0.75;                      // door centre z (k=1)
    for (const sx of [-1, 1]) {
      const spans = sx > 0 ? [[0.15, dz0 - 0.68], [dz0 + 0.68, CL - 0.15]] : [[0.15, CL - 0.15]];
      for (const [za, zb] of spans) {
        const wl = new THREE.Mesh(new THREE.PlaneGeometry(zb - za, 0.95), iw); wl.position.set(sx * (CW2 / 2 - 0.08), 1.5, (za + zb) / 2); wl.rotation.y = -sx * Math.PI / 2; inner.add(wl);
        const wu = new THREE.Mesh(new THREE.PlaneGeometry(zb - za, 0.5), iw); wu.position.set(sx * (CW2 / 2 - 0.08), 3.2, (za + zb) / 2); wu.rotation.y = -sx * Math.PI / 2; inner.add(wu);
      }
      // window posts
      for (let z = 0.4; z < CL; z += 2.1) if (sx < 0 || Math.abs(z - dz0) > 0.9) { const pst = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.95, 0.12), iw); pst.position.set(sx * (CW2 / 2 - 0.09), 2.45, z); inner.add(pst); }
    }
    // seats (longitudinal benches) and grab poles
    const seatM = std({ color: 0x6a5a48, roughness: 0.7 });
    for (const [z0, z1] of [[0.4, dz0 - 0.9], [dz0 + 0.9, dz0 + 3.3]]) for (const sx of [-1]) { const s = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.12, z1 - z0), seatM); s.position.set(sx * 0.95, 1.5, (z0 + z1) / 2); inner.add(s);
      const bk = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.5, z1 - z0), seatM); bk.position.set(sx * 1.2, 1.85, (z0 + z1) / 2); inner.add(bk); }
    const poleM = std({ color: 0xd0d0cc, metalness: 1, roughness: 0.2 });
    for (const z of [dz0 - 0.75, dz0 + 0.75]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 2.4, 10), poleM); p.position.set(0.95, 2.25, z); inner.add(p); }
    const rail2 = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, CL - 1, 8), poleM); rail2.rotation.x = Math.PI / 2; rail2.position.set(0.7, 3.1, CL / 2); inner.add(rail2);
    for (const z of [2, 6, 10]) { const lt = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.03, 2.5), new THREE.MeshBasicMaterial({ color: new THREE.Color(1.8, 1.7, 1.5) })); lt.position.set(0, 3.43, z); inner.add(lt); }
    // the door leaves (slide along z)
    const leafM = std({ color: 0xa69a6c, roughness: 0.45, metalness: 0.25 });
    const leaves = [];
    for (const s of [-1, 1]) { const lf = new THREE.Group(); inner.add(lf);
      const pnl = new THREE.Mesh(new THREE.BoxGeometry(0.05, 2.0, 0.65), leafM); pnl.position.set(0, 0, 0); lf.add(pnl);
      const gl = new THREE.Mesh(new THREE.PlaneGeometry(0.45, 0.9), new THREE.MeshStandardMaterial({ color: 0x223, roughness: 0.05, transparent: true, opacity: 0.25 })); gl.position.set(-0.03, 0.35, 0); gl.rotation.y = -Math.PI / 2; lf.add(gl);
      const rub = new THREE.Mesh(new THREE.BoxGeometry(0.07, 2.0, 0.04), darkM); rub.position.set(0, 0, -s * 0.33); lf.add(rub);
      lf.position.set(CW2 / 2 - 0.03, 1.05 + 1.0, dz0 + s * 0.325); lf.userData.s = s; leaves.push(lf); }
    // door frame on the inside
    for (const dz of [-0.68, 0.68]) { const f = new THREE.Mesh(new THREE.BoxGeometry(0.12, 2.05, 0.06), darkM); f.position.set(CW2 / 2 - 0.08, 2.07, dz0 + dz); inner.add(f); }
    const fTop = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.08, 1.42), darkM); fTop.position.set(CW2 / 2 - 0.08, 3.1, dz0); inner.add(fTop);
    ctx.leaves = leaves; ctx.dz0 = dz0;
    const inLight = new THREE.PointLight(0xffe2b8, 3, 6, 1.8); inLight.position.set(-0.3, 3.1, dz0); inner.add(inLight);
  }

  const dust = makeDust(THREE, 900, [-2.2, PX + PW], [0.3, HT - 0.2], [-45, 30], 0.02, 12); scene.add(dust.pts);
  const post = makeComposer(THREE, renderer, scene, camera, W, H, {
    bloom: 0.8, bloomRadius: 0.65, bloomThreshold: 0.65, exposure: 1.05,
    dof: shot === 'sign' ? { focus: 1.6, aperture: 0.004, maxblur: 0.01 } : shot === 'crowd' ? { focus: 3, aperture: 0.0016, maxblur: 0.006 } : null,
  });
  Object.assign(ctx, { train, tubes, tubeOn, head, headBeam, hl, card, cabLamp, crowd, dust, PX, PW }, post);
  return ctx;
}

function setTubes(ctx, f) {
  for (const tb of ctx.tubes) {
    const v = f(tb);
    tb.tb.material.color.setRGB(0.08 + v * 2.1, 0.08 + v * 2.0, 0.08 + v * 1.85);
    tb.h.material.opacity = 0.5 * v;
    if (tb.light) tb.light.intensity = 9 * v * (ctx.shot === 'crowd' ? 0.8 : 1);
  }
}

export function update(ctx, t) {
  const { THREE, camera, shot } = ctx;
  const V = (x, y, z) => new THREE.Vector3(x, y, z);

  if (shot === 'bornholmer') {
    const { STREET, ZL } = ctx;
    // crowd walks west (+z); positions wrap far beyond the West end, hidden in haze
    placeCrowd(THREE, ctx.crowd, p => {
      const span = 130; let z = -75 + ((p.z0 + p.v * t) % span);
      const ph = (p.z0 + p.v * t) * 3.2 + p.ph;
      const onBridge = Math.abs(z) < ZL;
      const x = p.x * (onBridge ? 1 : 1.25) + Math.sin(ph * 0.21) * 0.15;
      return { x, y: STREET + 0.18 * (onBridge ? 1 : 0) * (Math.abs(x) > 6.8 ? 1 : 0) + Math.abs(Math.sin(ph)) * 0.035, z, ry: p.sway * 0.4, rz: Math.sin(ph) * 0.025, s: p.s, sy: 1 };
    });
    // camera: on the eastern approach, high on the embankment; holds on the bridge, then at 3.4 s tilts and pans down
    const a = smooth((t - 3.3) / 2.9);
    const cp = V(lerp(27, 25, a) - 0.3 * t, lerp(STREET + 9, STREET + 6, a), lerp(-46, -38, a) + 0.35 * t);
    camera.position.copy(cp);
    const look = V(lerp(-3, 19, a), lerp(STREET + 1.8, 1.2, a), lerp(4, -5, a));
    camera.lookAt(look);
    camera.fov = lerp(36, 40, a); camera.updateProjectionMatrix();
    return;
  }

  if (shot === 'ticket') {
    driftDust(ctx.dust, t, 0.02);
    const { ticket, coins, hand, clerk } = ctx;
    // the clerk pushes the ticket under the glass towards the customer
    const ts = smooth((t + 0.3) / 1.2);
    ticket.position.set(lerp(0.02, -0.035, ts), 0.0006, lerp(-0.3, -0.01, ts)); ticket.rotation.set(0, lerp(0.15, -0.06, ts), 0);
    const ch = smooth((t - 0.85) / 0.6);
    clerk.position.set(lerp(0.02, 0.0, ts) - 0.01, 0.012, lerp(-0.38, -0.06, ts) - 0.07 - 0.25 * ch); clerk.rotation.set(-Math.PI / 2 + 0.1, 0, 0);
    clerk.visible = ch < 0.98;
    // the customer's hand comes in from the right with the coins and lets them drop
    const hin = smooth((t - 0.3) / 0.7), hout = smooth((t - 1.9) / 0.8);
    const hp = V(lerp(0.36, 0.2, hin) + 0.25 * hout, 0.06 + 0.005 * Math.sin(t * 3), lerp(0.12, 0.06, hin) + 0.1 * hout);
    hand.position.copy(hp); hand.rotation.set(0.25, 0, Math.PI / 2 + 0.35); hand.rotateX(-0.2);
    const rest = [V(0.055, 0.00105, 0.035), V(0.09, 0.00105, 0.06), V(0.03, 0.00105, 0.075)];
    coins.forEach((c, i) => {
      const td = 1.15 + i * 0.16;                       // release times
      const inHand = V(hp.x - 0.12 + i * 0.008, hp.y - 0.028 + i * 0.002, hp.z - 0.005 + i * 0.008);
      if (t < td) { c.position.copy(inHand); c.rotation.set(0.6, 0, 0.3); }
      else {
        const d = t - td, fall = Math.sqrt(2 * (inHand.y - rest[i].y) / 9.81);
        if (d < fall) { c.position.set(lerp(inHand.x, rest[i].x, d / fall), inHand.y - 0.5 * 9.81 * d * d, lerp(inHand.z, rest[i].z, d / fall)); c.rotation.set(0.6 + d * 14, 0, 0.3); }
        else { const e = d - fall; const wob = Math.exp(-e * 7) * 0.25 * Math.cos(e * 40); c.position.copy(rest[i]); c.position.y += Math.abs(wob) * 0.004; c.rotation.set(wob, i * 1.3, wob * 0.5); }
      }
    });
    const k = smooth(t / 3.6);
    camera.position.set(lerp(-0.03, 0.0, k), lerp(0.19, 0.165, k), lerp(0.21, 0.18, k));
    camera.lookAt(lerp(0.015, 0.03, k), 0.0, lerp(-0.03, 0.0, k));
    camera.fov = 40; camera.updateProjectionMatrix();
    if (ctx.bokeh) ctx.bokeh.uniforms.focus.value = camera.position.distanceTo(V(0.0, 0, 0.0));
    return;
  }

  // ---- station shots
  driftDust(ctx.dust, t);
  const { train } = ctx;
  let headOn = 1, ilight = 1;
  if (shot === 'stop') {
    // braking curve: arrives at ~9 m/s, stops with the front at z = -2 at t = 5.0
    const ts = 5.0, zs = -2, a = 1.9;            // deceleration from t = 0.3
    const v0 = a * (ts - 0.3);
    const zAt = tt => tt >= ts ? zs : zs - 0.5 * a * (ts - tt) ** 2 - (tt < 0.3 ? v0 * (0.3 - tt) : 0);
    train.position.z = zAt(t);
    // a tiny settle when it stops
    const settle = t > ts ? Math.exp(-(t - ts) * 5) * Math.sin((t - ts) * 14) * 0.03 : 0;
    train.position.z += settle; train.rotation.x = settle * 0.05;
    const on = tb => flicker(t, 5.35 + Math.abs(tb.z + 6) * 0.018 + (tb.seed % 3) * 0.06, tb.seed);
    setTubes(ctx, on);
    const k = smooth(t / 8);
    camera.position.set(lerp(2.6, 2.75, k), lerp(1.85, 1.75, k), lerp(9, 7.5, k));
    camera.lookAt(lerp(0.2, 0.0, k), lerp(1.7, 1.9, k), -30);
    camera.fov = 40; camera.updateProjectionMatrix();
    ilight = 0.9;
  } else if (shot === 'sign') {
    train.position.z = -2;
    setTubes(ctx, tb => 0.95 + 0.05 * Math.sin(t * 7 + tb.seed));
    const k = smooth(t / 3.2);
    // close on the front window, slow push and slight arc
    camera.position.set(lerp(-0.85, -0.45, k), lerp(2.35, 2.45, k), -2 + lerp(1.55, 1.25, k));
    camera.lookAt(-0.08, 2.5, -2);
    camera.fov = 36; camera.updateProjectionMatrix();
    if (ctx.bokeh) ctx.bokeh.uniforms.focus.value = camera.position.distanceTo(V(-0.08, 2.5, -1.97));
    headOn = 0.6;
  } else if (shot === 'crowd') {
    train.position.z = -ctx.dz0;                // door centred at z = 0
    setTubes(ctx, tb => 0.95 + 0.05 * Math.sin(t * 7 + tb.seed));
    const o = smooth((t - 0.6) / 1.1);
    ctx.leaves.forEach(lf => { lf.position.z = ctx.dz0 + lf.userData.s * (0.325 + 0.62 * o); lf.position.x = 2.65 / 2 - 0.03 - 0.03 * Math.min(1, o * 4); });
    placeCrowd(THREE, ctx.crowd, p => {
      const sw = Math.sin(t * 1.3 + p.ph) * 0.03, lean = o * 0.06 * (p.x < 2.6 ? 1 : 0.4);
      return { x: p.x - lean * 0.5, y: 1.0 + (p.kind === 'wave' || p.kind === 'both' ? Math.abs(Math.sin(t * 2.2 + p.ph)) * 0.03 : 0), z: p.z, ry: p.ry, rz: sw + lean, s: p.s };
    });
    const k = smooth(t / 5.5);
    camera.position.set(lerp(-1.05, -0.8, k), lerp(2.6, 2.55, k), lerp(0.5, 0.3, k));
    camera.lookAt(5, lerp(2.35, 2.4, k), lerp(-0.4, -0.2, k));
    camera.fov = 50; camera.updateProjectionMatrix();
    if (ctx.bokeh) ctx.bokeh.uniforms.focus.value = 3.0;
    headOn = 0.5;
  }
  ctx.head.intensity = 22 * headOn; ctx.headBeam.material.uniforms.opacity.value = 0.03 * headOn; ctx.hl.forEach(h => h.material.opacity = 0.9 * headOn);
  (train.userData.ilights || []).forEach(l => l.intensity = 2.0 * ilight);
  ctx.cabLamp.intensity = shot === 'sign' ? 1.6 : 0;
}

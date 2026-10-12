// France 2026: "intermediate weapons" explainer as clean product-style objects in a dark studio. Stylised, not to scale
// detail; nothing here is a technical diagram. Three plinths along x: LBD launcher (x=-3.2), tear-gas launcher (x=0),
// dispersal / stun grenade (x=3.2). No people, no injuries.
// shots (?shot=name or name:seconds):
//   lineup      (8 s)  low dolly along the three plinths; amber rim lights switch on one by one; INTERMEDIATE WEAPONS.
//   lbd         (6 s)  slow orbit on the LBD; a rubber projectile leaves the muzzle along a dotted amber path.
//   gas         (6 s)  the tear-gas launcher; a canister arcs out and lands trailing a pale smoke ribbon.
//   grenade     (6 s)  the grenade; at 2 s it opens into an exploded radial burst of rubber pellets (abstract, slow).
//   close_range (6 s)  top-down-ish: launcher muzzle and a short amber distance bracket, "CLOSE RANGE".
//   suspended   (6 s)  the grenade under a spot; a glass case lowers over it, the light turns cold, SUSPENDED · 7 OCT.
import { AMBER } from './lib.js';
import { glow, beam } from './look.js';
import { AMBER_HI, path, clamp01, sstep, fontsReady, finishPost, ctex, timing, label, ease } from './france_lib.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export async function setup(THREE, renderer, W, H) {
  const { name, k } = timing(6);
  const shot = name || 'lineup';
  await fontsReady();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050506);
  scene.fog = new THREE.FogExp2(0x050506, 0.035);
  const camera = new THREE.PerspectiveCamera(shot === 'lineup' ? 28 : 32, W / H, 0.02, 200);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.5, metalness: 0.2, ...o });
  const gun = std({ color: 0x4a4e52, roughness: 0.34, metalness: 0.7 });
  const poly = std({ color: 0x2c2e31, roughness: 0.6, metalness: 0.1 });
  const rubber = std({ color: 0x2b2b2b, roughness: 0.9 });
  const yellow = std({ color: 0xb08a2a, roughness: 0.6 });
  const can = std({ color: 0x5a5d5a, roughness: 0.45, metalness: 0.6 });
  const add = (geo, mat, x, y, z, parent, rx = 0, ry = 0, rz = 0) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.rotation.set(rx, ry, rz); m.castShadow = m.receiveShadow = true; parent.add(m); return m; };
  const RB = (w, h, d, r = 0.01) => new RoundedBoxGeometry(w, h, d, 3, r);
  const cyl = (r, l, n = 28) => new THREE.CylinderGeometry(r, r, l, n);

  // ------------------------------------------------------------------ floor + plinths
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), std({ color: 0x0d0d0e, roughness: 0.32, metalness: 0.5 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  const plinthMat = std({ color: 0x2a2a2d, roughness: 0.6, metalness: 0.2 });
  const PX = [-3.2, 0, 3.2], PY = 0.62;
  for (const x of PX) {
    add(RB(1.9, PY, 1.0, 0.02), plinthMat, x, PY / 2, 0, scene);
    const edge = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.006, 0.006), new THREE.MeshBasicMaterial({ color: 0x8a6a40 })); edge.position.set(x, PY, 0.5); scene.add(edge);
  }

  // ------------------------------------------------------------------ LBD launcher (stylised, single-shot 40 mm)
  const lbd = new THREE.Group(); lbd.position.set(PX[0], PY + 0.2, 0); scene.add(lbd);
  add(cyl(0.032, 0.42), gun, 0.24, 0.05, 0, lbd, 0, 0, Math.PI / 2);                       // barrel
  add(cyl(0.038, 0.04), gun, 0.44, 0.05, 0, lbd, 0, 0, Math.PI / 2);                       // muzzle ring
  add(RB(0.3, 0.1, 0.07, 0.015), poly, -0.04, 0.03, 0, lbd);                                // receiver
  add(RB(0.06, 0.15, 0.05, 0.015), poly, -0.06, -0.08, 0, lbd, 0, 0, 0.25);                 // grip
  add(RB(0.04, 0.09, 0.04, 0.01), poly, 0.07, -0.05, 0, lbd, 0, 0, 0.1);                    // fore grip
  add(RB(0.32, 0.07, 0.05, 0.02), poly, -0.33, 0.0, 0, lbd, 0, 0, 0.1);                     // stock
  add(RB(0.05, 0.13, 0.06, 0.015), rubber, -0.49, -0.02, 0, lbd, 0, 0, 0.1);                 // butt pad
  add(RB(0.09, 0.05, 0.05, 0.01), gun, 0.02, 0.12, 0, lbd);                                  // optic
  add(cyl(0.02, 0.03, 16), std({ color: 0x3a2a14, roughness: 0.2, metalness: 0.6, emissive: 0x5a3010, emissiveIntensity: 0.6 }), 0.07, 0.12, 0, lbd, 0, 0, Math.PI / 2);
  lbd.rotation.y = -0.35; lbd.scale.setScalar(1.35);
  const lbdMuzzle = new THREE.Vector3(0.46, 0.05, 0).applyMatrix4(new THREE.Matrix4().compose(lbd.position, lbd.quaternion, lbd.scale));
  // projectile: foam/rubber nose on a short body
  const proj = new THREE.Group(); scene.add(proj);
  add(cyl(0.02, 0.04, 20), std({ color: 0x3a3c3e, metalness: 0.4, roughness: 0.4 }), 0, 0, 0, proj, 0, 0, Math.PI / 2);
  add(new THREE.SphereGeometry(0.021, 20, 12, 0, Math.PI * 2, 0, Math.PI / 2), std({ color: 0x6a5a40, roughness: 0.9 }), 0.02, 0, 0, proj, 0, 0, -Math.PI / 2);
  proj.scale.setScalar(1.35); proj.visible = false;

  // ------------------------------------------------------------------ tear-gas launcher (stylised 56 mm, shoulder)
  const gl = new THREE.Group(); gl.position.set(PX[1], PY + 0.22, 0); scene.add(gl);
  add(cyl(0.045, 0.46), gun, 0.26, 0.06, 0, gl, 0, 0, Math.PI / 2);
  add(cyl(0.052, 0.05), gun, 0.5, 0.06, 0, gl, 0, 0, Math.PI / 2);
  add(cyl(0.05, 0.08), poly, 0.02, 0.06, 0, gl, 0, 0, Math.PI / 2);                         // breech
  add(RB(0.22, 0.09, 0.07, 0.015), poly, -0.12, 0.02, 0, gl);
  add(RB(0.06, 0.16, 0.05, 0.015), poly, -0.1, -0.09, 0, gl, 0, 0, 0.25);
  add(RB(0.36, 0.06, 0.05, 0.02), poly, -0.38, -0.01, 0, gl, 0, 0, 0.06);
  add(RB(0.05, 0.14, 0.07, 0.015), rubber, -0.56, -0.02, 0, gl, 0, 0, 0.06);
  add(RB(0.12, 0.03, 0.03, 0.01), gun, 0.2, 0.125, 0, gl);                                   // sight rail
  gl.rotation.y = -0.3; gl.scale.setScalar(1.3);
  const glMuzzle = new THREE.Vector3(0.53, 0.06, 0).applyMatrix4(new THREE.Matrix4().compose(gl.position, gl.quaternion, gl.scale));
  // canister lying in front of it + the flying one
  const canister = (parent) => { const g = new THREE.Group(); parent.add(g);
    add(cyl(0.028, 0.15), can, 0, 0, 0, g); add(cyl(0.029, 0.02), yellow, 0, 0.05, 0, g); add(cyl(0.022, 0.012), gun, 0, 0.081, 0, g); return g; };
  const canRest = canister(scene); canRest.position.set(PX[1] + 0.35, PY + 0.03, 0.3); canRest.rotation.z = Math.PI / 2; canRest.rotation.y = 0.4; canRest.scale.setScalar(1.3);
  const canFly = canister(scene); canFly.scale.setScalar(1.3); canFly.visible = false;
  // smoke ribbon (points)
  const smokeN = 160; const smokeGeo = new THREE.BufferGeometry(); smokeGeo.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(smokeN * 3), 3));
  const puffTex = ctex(THREE, 128, 128, (g) => { const grd = g.createRadialGradient(64, 64, 0, 64, 64, 64); grd.addColorStop(0, 'rgba(255,255,255,0.55)'); grd.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = grd; g.fillRect(0, 0, 128, 128); });
  const smoke = new THREE.Points(smokeGeo, new THREE.PointsMaterial({ map: puffTex, size: 0.5, transparent: true, depthWrite: false, opacity: 0.35, color: 0xcfc8bb, sizeAttenuation: true }));
  smoke.frustumCulled = false; scene.add(smoke);

  // ------------------------------------------------------------------ grenade (stylised dispersal grenade)
  const gr = new THREE.Group(); gr.position.set(PX[2], PY, 0); scene.add(gr);
  const grBody = new THREE.Group(); gr.add(grBody);
  const prof = [[0, 0], [0.06, 0], [0.075, 0.015], [0.078, 0.11], [0.07, 0.13], [0.03, 0.14], [0, 0.14]].map(([r, y]) => new THREE.Vector2(r, y));
  const shellA = add(new THREE.LatheGeometry(prof, 40), std({ color: 0x2c2e2c, roughness: 0.7, metalness: 0.2 }), 0, 0, 0, grBody);
  const band = add(new THREE.CylinderGeometry(0.0795, 0.0795, 0.02, 40, 1, true), yellow, 0, 0.07, 0, grBody);
  const fuse = add(cyl(0.016, 0.06, 16), gun, 0, 0.17, 0, grBody);
  const lever = add(RB(0.016, 0.13, 0.03, 0.006), gun, 0.03, 0.135, 0, grBody, 0, 0, -0.2);
  const ring = add(new THREE.TorusGeometry(0.02, 0.004, 8, 24), gun, -0.03, 0.2, 0, grBody, Math.PI / 2, 0, 0);
  grBody.scale.setScalar(2.0);
  // pellets for the exploded burst
  const pellets = [];
  const pm = std({ color: 0x3a3a3a, roughness: 0.8 });
  for (let i = 0; i < 18; i++) { const a = i / 18 * Math.PI * 2; const m = add(new THREE.SphereGeometry(0.018, 14, 10), pm, 0, 0.14, 0, gr); m.userData.dir = new THREE.Vector3(Math.cos(a), 0.12 * Math.sin(i * 2.3), Math.sin(a)); m.visible = false; pellets.push(m); }
  const burstRing = new THREE.Mesh(new THREE.RingGeometry(0.98, 1.0, 96), new THREE.MeshBasicMaterial({ color: AMBER_HI, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false }));
  burstRing.rotation.x = -Math.PI / 2; burstRing.position.y = 0.141; gr.add(burstRing);
  // glass case for "suspended"
  const glass = new THREE.Mesh(new RoundedBoxGeometry(0.75, 0.8, 0.75, 3, 0.012), new THREE.MeshPhysicalMaterial({ color: 0xdfe6ea, roughness: 0.05, metalness: 0, transparent: true, opacity: 0.14, depthWrite: false, side: THREE.DoubleSide }));
  const glassEdges = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(0.75, 0.8, 0.75)), new THREE.LineBasicMaterial({ color: 0xd9dfe2, transparent: true, opacity: 0.5 }));
  const caseG = new THREE.Group(); caseG.add(glass, glassEdges); caseG.position.set(PX[2], PY + 0.4, 0); caseG.visible = false; scene.add(caseG);

  // ------------------------------------------------------------------ amber paths / brackets
  const dotPath = (pts, n = 70) => { const curve = new THREE.CatmullRomCurve3(pts); const g = new THREE.Group(); scene.add(g); const ms = [];
    for (let i = 0; i < n; i++) { const p = curve.getPoint(i / (n - 1)); const m = new THREE.Mesh(new THREE.SphereGeometry(0.008, 8, 6), new THREE.MeshBasicMaterial({ color: AMBER_HI, transparent: true, opacity: 0 })); m.position.copy(p); g.add(m); ms.push(m); }
    return { curve, ms }; };
  const lbdPath = dotPath([lbdMuzzle.clone(), lbdMuzzle.clone().add(new THREE.Vector3(1.2, 0.02, -0.4)), lbdMuzzle.clone().add(new THREE.Vector3(3.0, 0.0, -1.1)), lbdMuzzle.clone().add(new THREE.Vector3(6.0, -0.15, -2.2))]);
  const gasPts = []; for (let i = 0; i <= 20; i++) { const s = i / 20; gasPts.push(glMuzzle.clone().add(new THREE.Vector3(s * 5.5, Math.sin(s * Math.PI) * 0.9 - s * (PY + 0.25), -s * 1.6))); }
  const gasPath = dotPath(gasPts, 90);
  // close-range bracket on the floor in front of the gas launcher
  const brM = new THREE.MeshBasicMaterial({ color: AMBER_HI, transparent: true, opacity: 0 });
  const bracket = new THREE.Group(); scene.add(bracket);
  { const L = 0.9; const a = new THREE.Mesh(new THREE.BoxGeometry(L, 0.006, 0.012), brM); a.position.x = L / 2; bracket.add(a);
    for (const x of [0, L]) { const t = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.006, 0.12), brM); t.position.x = x; bracket.add(t); }
    const tgt = new THREE.Mesh(new THREE.RingGeometry(0.05, 0.065, 48), brM); tgt.rotation.x = -Math.PI / 2; tgt.position.set(L + 0.12, 0, 0); bracket.add(tgt);
    bracket.position.copy(glMuzzle).add(new THREE.Vector3(0.05, -0.17, 0.02)); bracket.rotation.y = -0.3 * 1; }

  // ------------------------------------------------------------------ lights
  scene.add(new THREE.HemisphereLight(0x8e94a0, 0x080706, 0.55));
  const spots = PX.map((x) => { const s = new THREE.SpotLight(0xfff1df, 0, 12, 0.2, 0.7, 1.4); s.position.set(x + 0.4, 4.2, 1.6); s.target.position.set(x, PY, 0); s.castShadow = true; s.shadow.mapSize.set(1024, 1024); s.shadow.bias = -0.0004; scene.add(s, s.target); return s; });
  const rims = PX.map((x) => { const r = new THREE.SpotLight(AMBER, 0, 3.4, 0.3, 0.5, 2.0); r.position.set(x - 0.6, PY + 1.2, -2.6); r.target.position.set(x, PY + 0.25, 0); scene.add(r, r.target); return r; });
  const beams = PX.map((x) => { const b = beam(THREE, 0xfff0dc, 4.0, 0.9, 0.035); b.position.set(x + 0.4, 4.2, 1.6); b.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), new THREE.Vector3(-0.4, PY - 4.2, -1.6).normalize()); scene.add(b); return b; });
  const cold = new THREE.SpotLight(0xbfd2e6, 0, 10, 0.35, 0.6, 1.3); cold.position.set(PX[2] - 0.3, 4.0, 1.4); cold.target.position.set(PX[2], PY, 0); scene.add(cold, cold.target);
  const flash = new THREE.PointLight(AMBER, 0, 4, 1.5); flash.position.set(PX[2], PY + 0.4, 0.3); scene.add(flash);

  // ------------------------------------------------------------------ labels
  const L = {};
  const fill = new THREE.DirectionalLight(0xdfe4ea, 0.5); fill.position.set(2, 3, 6); scene.add(fill);
  const wash = new THREE.SpotLight(0xffc890, 14, 14, 0.9, 1.0, 1.5); wash.position.set(0, 3.5, 1.5); wash.target.position.set(0, 0.6, -4.5); scene.add(wash, wash.target);
  { const cyc = new THREE.Mesh(new THREE.CylinderGeometry(8, 8, 8, 64, 1, true, Math.PI * 0.5 + 0.6, Math.PI - 1.2), std({ color: 0x141416, roughness: 0.9, side: THREE.BackSide }));
    cyc.position.set(0, 3.9, 3.5); scene.add(cyc); }
  const mk = (id, text, sub, pos, o = {}) => { const l = label(THREE, text, { size: 0.03, sub, ...o }); l.material.opacity = 0; l.position.copy(pos); scene.add(l); L[id] = l; return l; };
  mk('title', 'INTERMEDIATE WEAPONS', null, new THREE.Vector3(0, 2.35, -0.6), { anchor: 'center', size: 0.05, gap: 0 });
  mk('lbd', 'LBD', 'rubber-projectile launcher', new THREE.Vector3(PX[0] - 0.2, PY + 0.62, 0), { size: 0.042 });
  mk('gas', 'TEAR-GAS LAUNCHER', 'fires gas canisters', new THREE.Vector3(PX[1] - 0.2, PY + 0.62, 0), { size: 0.042 });
  mk('gr', 'DISPERSAL / STUN GRENADE', 'some scatter rubber pellets', new THREE.Vector3(PX[2] - 0.1, PY + 0.66, 0), { size: 0.042 });
  mk('close', 'CLOSE RANGE', null, new THREE.Vector3(glMuzzle.x + 0.5, PY + 0.02, glMuzzle.z + 0.25), { size: 0.034, anchor: 'center', gap: 0 });
  mk('susp', 'SUSPENDED', 'at lycée protests · 7 Oct', new THREE.Vector3(PX[2] + 0.5, PY + 0.95, 0), { size: 0.052 });

  const LP = {   // per-shot label anchors (world), chosen so the type sits in clear space on that shot's framing
    lbd: { lbd: [PX[0] - 0.55, PY + 0.02, 0.45] }, gas: { gas: [PX[1] - 0.5, PY + 0.02, 0.5] }, grenade: { gr: [PX[2] - 0.45, PY + 0.02, 0.48] },
    suspended: { susp: [PX[2] + 0.42, PY + 0.55, 0.3], gr: [PX[2] - 0.45, PY + 0.02, 0.48] },
    lineup: { lbd: [PX[0] - 0.3, PY + 0.75, 0.0], gas: [PX[1] - 0.3, PY + 0.62, 0.0], gr: [PX[2] - 1.65, PY + 1.12, 0.0], title: [-1.9, 2.05, -0.2] },
  }[shot] ?? {};
  for (const [id, p] of Object.entries(LP)) L[id].position.set(...p);
  const dofF = { lbd: 2.3, gas: 2.6, grenade: 1.9, close_range: 2.6, suspended: 2.3 }[shot];
  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.7, bloomRadius: 0.5, bloomThreshold: 0.72, dof: dofF ? { focus: dofF, aperture: 0.0025, maxblur: 0.008 } : null });
  return { THREE, scene, camera, shot, k, spots, rims, fill, wash, beams, cold, flash, L, proj, lbdPath, gasPath, canFly, smoke, smokeGeo, pellets, burstRing, grBody, gr, caseG, brM, glMuzzle, ...post };
}

const CAMS = {
  lineup: [[0, [-5.0, 1.15, 2.0, -3.0, 0.9, 0]], [3.2, [-3.4, 1.45, 6.4, -1.2, 0.9, -0.1]], [8, [0.0, 1.55, 11.4, 0.0, 0.95, 0]]],
  lbd: [[0, [-2.0, 1.25, 1.9, -3.1, 0.82, 0]], [6, [-3.9, 1.18, 2.1, -2.9, 0.84, -0.1]]],
  gas: [[0, [-1.6, 1.2, 2.6, 0.6, 0.95, -0.3]], [6, [-1.4, 1.45, 3.4, 1.6, 0.85, -0.5]]],
  grenade: [[0, [3.9, 1.35, 1.6, 3.2, 0.8, 0]], [6, [2.5, 1.25, 1.75, 3.2, 0.8, 0]]],
  close_range: [[0, [0.2, 2.7, 1.9, 0.6, 0.62, 0]], [6, [0.5, 2.45, 1.7, 0.7, 0.62, 0]]],
  suspended: [[0, [2.0, 1.15, 2.0, 3.2, 0.95, 0]], [6, [2.3, 1.1, 1.75, 3.25, 0.98, 0]]],
};

export function update(ctx, tt) {
  const { camera, shot, spots, rims, beams, L } = ctx;
  const t = tt / ctx.k;
  const c = path(CAMS[shot] ?? CAMS.lineup)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  const on = [0, 0, 0], rim = [0, 0, 0];
  for (const l of Object.values(L)) l.material.opacity = 0;
  ctx.proj.visible = false; ctx.canFly.visible = false; ctx.smoke.visible = false; ctx.caseG.visible = false; ctx.brM.opacity = 0;
  ctx.lbdPath.ms.forEach(m => m.material.opacity = 0); ctx.gasPath.ms.forEach(m => m.material.opacity = 0);
  ctx.pellets.forEach(p => p.visible = false); ctx.burstRing.material.opacity = 0; ctx.cold.intensity = 0; ctx.flash.intensity = 0;

  if (shot === 'lineup') {
    for (let i = 0; i < 3; i++) { const a = 0.8 + i * 1.6; on[i] = sstep(a, a + 0.5, t); rim[i] = sstep(a + 0.2, a + 0.9, t); }
    L.title.material.opacity = sstep(5.6, 6.6, t);
    L.lbd.material.opacity = sstep(1.3, 2.0, t) * 0.9; L.gas.material.opacity = sstep(2.9, 3.6, t) * 0.9; L.gr.material.opacity = sstep(4.5, 5.2, t) * 0.9;
  } else if (shot === 'lbd') {
    on[0] = 1; rim[0] = 1; on[1] = 0.15;
    L.lbd.material.opacity = sstep(0.4, 1.1, t);
    const p = clamp01((t - 1.8) / 1.6);
    ctx.lbdPath.ms.forEach((m, i) => { const s = i / (ctx.lbdPath.ms.length - 1); m.material.opacity = s < p ? 0.85 * (1 - 0.5 * s) : 0; });
    if (t > 1.8) { ctx.proj.visible = true; const pt = ctx.lbdPath.curve.getPoint(Math.min(1, p)); ctx.proj.position.copy(pt); const tan = ctx.lbdPath.curve.getTangent(Math.min(0.999, p)); ctx.proj.rotation.y = -Math.atan2(tan.z, tan.x); }
  } else if (shot === 'gas') {
    on[1] = 1; rim[1] = 1; on[0] = 0.12; on[2] = 0.12;
    L.gas.material.opacity = sstep(0.4, 1.1, t);
    const p = clamp01((t - 1.6) / 2.4);
    ctx.gasPath.ms.forEach((m, i) => { const s = i / (ctx.gasPath.ms.length - 1); m.material.opacity = s < p ? 0.8 : 0; });
    if (t > 1.6) { ctx.canFly.visible = true; const pt = ctx.gasPath.curve.getPoint(p); ctx.canFly.position.copy(pt); ctx.canFly.rotation.set(t * 5, 0.3, t * 3);
      ctx.smoke.visible = true; const a = ctx.smokeGeo.attributes.position; const n = a.count;
      for (let i = 0; i < n; i++) { const s = i / n * p; const q = ctx.gasPath.curve.getPoint(s); const age = (p - s) * 2.4; a.setXYZ(i, q.x + Math.sin(i * 7.1) * 0.08 * age, q.y + age * 0.25, q.z + Math.cos(i * 3.7) * 0.08 * age); }
      a.needsUpdate = true; ctx.smoke.material.size = 0.22; ctx.smoke.material.opacity = 0.22; }
  } else if (shot === 'grenade') {
    on[2] = 1; rim[2] = 1; on[1] = 0.12;
    L.gr.material.opacity = sstep(0.4, 1.1, t) * (1 - sstep(4.6, 5.2, t) * 0);
    const p = ease((t - 2.0) / 2.6);
    ctx.pellets.forEach((m, i) => { m.visible = t > 2.0; m.position.set(m.userData.dir.x * p * 0.75, 0.14 + m.userData.dir.y * p, m.userData.dir.z * p * 0.75); });
    ctx.burstRing.material.opacity = (t > 2.0 ? 0.7 * (1 - sstep(2.0, 4.8, t) * 0.6) : 0); ctx.burstRing.scale.setScalar(0.05 + p * 0.78);
    ctx.flash.intensity = t > 2.0 ? 6 * Math.exp(-(t - 2.0) * 3) : 0;
    ctx.grBody.position.y = 0; ctx.grBody.rotation.y = t * 0.15;
  } else if (shot === 'close_range') {
    on[1] = 1; rim[1] = 0.8;
    ctx.brM.opacity = 0.9 * sstep(1.2, 2.0, t); L.close.material.opacity = sstep(1.8, 2.5, t);
  } else if (shot === 'suspended') {
    const off = sstep(2.0, 3.2, t);
    on[2] = 1 - 0.8 * off; rim[2] = 1 - off; ctx.cold.intensity = 30 * off;
    ctx.caseG.visible = true; ctx.caseG.position.y = 0.62 + 0.4 + (1 - ease((t - 0.8) / 1.6)) * 1.6;
    L.gr.material.opacity = sstep(0.3, 0.9, t) * (1 - sstep(2.0, 2.6, t));
    L.susp.material.opacity = sstep(3.0, 3.5, t);
  }
  spots.forEach((s, i) => { s.intensity = 90 * on[i]; ctx.beams[i].material.uniforms.opacity.value = (shot === 'lineup' ? 0.03 : 0.0) * on[i]; });
  rims.forEach((r, i) => r.intensity = 60 * rim[i]); ctx.fill.intensity = 1.3; ctx.wash.intensity = 70;
}

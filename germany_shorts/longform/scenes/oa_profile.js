// "Odd Ages" channel profile picture: a head-and-shoulders portrait of a fun history character (Rocketbox + lib_human.js),
// square, built for YouTube's circular crop, on a bold gradient with coloured rim lights. Bright, high-key, game-like.
// shots (?shot=):  A | B | C | D   (append "_dbg" to log head/eye positions)
//   A  Viking (Male_Adult_05, grey beard): horned helmet, fur collar, wide-eyed "whoa!", electric blue.
//   B  Pirate (Male_Adult_08): black tricorn with gold trim, red coat, cheeky one-brow grin, sunny orange.
//   C  Elizabethan lady (Female_Adult_01): big white ruff, pearls in her hair, delighted smile, magenta.
//   D  Victorian gentleman (Male_Adult_03): top hat, gold monocle, "wait, what?" raised brow, teal.
import { loadHuman, POSES } from './lib_human.js';
import { ctex, shotArgs } from './france_lib.js';

const V = {
  A: { avatar: 'Male_Adult_05', tex: 'm009', bg: ['#38b6ff', '#0a3fd6'], rimL: 0x7ff3ff, rimR: 0xffffff, body: 0x6a4a34,
    expr: { EyeWideLeft: 1, EyeWideRight: 1, BrowInnerUp: 0.9, BrowOuterUpLeft: 1, BrowOuterUpRight: 1, AU_UpperLidRaiser: 0.7,
      JawOpen: 0.22, MouthFunnel: 0.55, MouthPucker: 0.15, MouthLowerDownLeft: 0.2, MouthLowerDownRight: 0.2,
      AU_InnerBrowRaiser: 1, AU_OuterBrowRaiser: 1, AU_JawDrop: 0.2, AU_LipFunneler: 0.45 }, turn: 14, tilt: -3 },
  B: { avatar: 'Male_Adult_08', tex: 'm014', bg: ['#ffd23a', '#ff5a1f'], rimL: 0xfff1b0, rimR: 0xffffff, body: 0x9a1c1c, dist: 1.3,
    expr: { MouthSmileLeft: 1, MouthSmileRight: 0.6, CheekSquintLeft: 0.6, CheekSquintRight: 0.3, EyeSquintRight: 0.45, EyeSquintLeft: 0.15,
      BrowOuterUpLeft: 1, BrowInnerUp: 0.25, BrowDownRight: 0.35, MouthDimpleLeft: 0.4,
      AU_L_LipCornerPuller: 1, AU_R_LipCornerPuller: 0.6, HB_MouthSmile: 0.5, AU_L_CheekRaiser: 0.6, AU_L_OuterBrowRaiser: 1, AU_R_Squint: 0.35, AU_Dimpler: 0.3 }, turn: -16, tilt: 4 },
  C: { avatar: 'Female_Adult_01', tex: 'f001', bg: ['#ff5fa8', '#8a1fe0'], rimL: 0xffd0f0, rimR: 0xffffff, body: 0x1d6b4a, dist: 1.2, exposure: 0.8,
    expr: { MouthSmileLeft: 0.9, MouthSmileRight: 0.9, CheekSquintLeft: 0.45, CheekSquintRight: 0.45, EyeWideLeft: 0.45, EyeWideRight: 0.45,
      BrowInnerUp: 0.5, BrowOuterUpLeft: 0.6, BrowOuterUpRight: 0.6,
      AU_LipCornerPuller: 0.7, HB_MouthSmile: 0.4, AU_CheekRaiser: 0.5, AU_InnerBrowRaiser: 0.4, AU_OuterBrowRaiser: 0.6 }, turn: 12, tilt: -5 },
  D: { avatar: 'Male_Adult_03', tex: 'm004', bg: ['#2fe0c0', '#00756b'], rimL: 0xc8fff4, rimR: 0xffffff, body: 0x2a2a30, dist: 1.36,
    expr: { BrowOuterUpRight: 1, BrowInnerUp: 0.35, EyeWideRight: 1, AU_R_UpperLidRaiser: 0.6, EyeSquintLeft: 0.45,
      MouthPressLeft: 0.3, MouthLeft: 0.25, MouthRollUpper: 0.15,
      AU_R_OuterBrowRaiser: 1, AU_R_UpperLidRaiser: 1, AU_L_Squint: 0.8, BrowDownLeft: 1, AU_LipPressor: 0.3, AU_L_LipCornerPuller: 0.6, MouthSmileLeft: 0.4 }, turn: -12, tilt: 3 },
};

const X = [1, 0, 0], Y = [0, 1, 0], Z = [0, 0, 1];

export async function setup(THREE, renderer, W, H) {
  const { name: raw } = shotArgs('A');
  const dbg = raw.includes('_dbg'); const id = raw.replace('_dbg', ''); const v = V[id] || V.A;
  renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = v.exposure ?? 1.0;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  scene.background = ctex(THREE, 1024, 1024, (g, w, h) => {
    const grd = g.createRadialGradient(w * 0.5, h * 0.42, w * 0.05, w * 0.5, h * 0.5, w * 0.72);
    grd.addColorStop(0, v.bg[0]); grd.addColorStop(1, v.bg[1]); g.fillStyle = grd; g.fillRect(0, 0, w, h);
    // faint sunburst rays: reads as "fun" without competing with the face
    g.globalAlpha = 0.07; g.fillStyle = '#ffffff'; g.translate(w / 2, h * 0.42);
    for (let i = 0; i < 18; i++) { g.rotate(Math.PI * 2 / 18); g.beginPath(); g.moveTo(0, 0); g.lineTo(w, -w * 0.09); g.lineTo(w, w * 0.09); g.fill(); }
  });

  // ---- character ----
  const h = await loadHuman(THREE, { avatar: v.avatar, tex: v.tex });
  h.mats.head.sheen = 0.08; h.mats.head.roughness = 0.58;
  h.mats.head.normalScale.set(1.1, 1.1);
  h.tint('body', v.body);
  h.root.rotation.y = v.turn * Math.PI / 180;
  scene.add(h.root);
  // turn the head back toward camera so the eyes look straight down the lens
  const headFix = [['Bip01_Neck', Y, -v.turn * 0.45], ['Bip01_Head', Y, -v.turn * 0.5], ['Bip01_Head', Z, v.tilt]];
  h.pose(POSES.stand, 1, headFix); h.expr(v.expr, 1); h.syncHead();

  const eyeL = new THREE.Vector3(), eyeR = new THREE.Vector3();
  h.bones.Bip01_LEye.getWorldPosition(eyeL); h.bones.Bip01_REye.getWorldPosition(eyeR);
  const eyeMid = eyeL.clone().add(eyeR).multiplyScalar(0.5);
  const hg = h.headGroup; hg.updateMatrixWorld(true);
  const eyeLocal = hg.worldToLocal(eyeMid.clone()), eyeRLocal = hg.worldToLocal(eyeR.clone());
  if (dbg) console.log('eyeMid world', eyeMid.toArray().map(n => n.toFixed(3)), 'eye in head frame', eyeLocal.toArray().map(n => n.toFixed(3)), 'R eye', eyeRLocal.toArray().map(n => n.toFixed(3)));

  // ---- props ----
  const P = buildProps(THREE, id, eyeLocal, eyeRLocal);
  if (P.head) hg.add(P.head);
  if (P.body) { P.body.position.add(new THREE.Vector3(0, 0, 0)); h.root.add(P.body); P.body.userData.eye = eyeLocal; }
  scene.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  // shoulders-level props are placed relative to the eyes in root space
  if (P.body) { const e = h.root.worldToLocal(eyeMid.clone()); P.body.position.set(e.x, e.y, e.z); }

  // ---- lights: high-key studio, soft key, big fill, two coloured rims ----
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a7a70, 1.6));
  const key = new THREE.SpotLight(0xfff4e8, 60, 10, 0.45, 0.9, 2);
  key.position.set(eyeMid.x + 0.9, eyeMid.y + 1.0, eyeMid.z + 2.0); key.target.position.copy(eyeMid);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0003; key.shadow.normalBias = 0.01; key.shadow.radius = 6;
  scene.add(key, key.target);
  const fill = new THREE.PointLight(0xfff0f0, 4, 6, 2); fill.position.set(eyeMid.x - 1.0, eyeMid.y - 0.1, eyeMid.z + 1.4); scene.add(fill);
  const under = new THREE.PointLight(0xffffff, 1.2, 4, 2); under.position.set(eyeMid.x, eyeMid.y - 0.7, eyeMid.z + 1.0); scene.add(under);
  for (const [sx, col] of [[-1, v.rimL], [1, v.rimR]]) {
    const r = new THREE.SpotLight(col, 45, 6, 0.5, 0.6, 2);
    r.position.set(eyeMid.x + sx * 1.1, eyeMid.y + 0.5, eyeMid.z - 1.3); r.target.position.set(eyeMid.x, eyeMid.y - 0.05, eyeMid.z); scene.add(r, r.target);
  }

  // ---- camera: head & shoulders, face ~40 % of the circle ----
  const camera = new THREE.PerspectiveCamera(19, W / H, 0.05, 50);
  const target = eyeMid.clone().add(new THREE.Vector3(0, P.lift ?? 0.0, 0));
  camera.position.set(target.x, target.y + 0.02, target.z + (v.dist ?? 1.42)); camera.lookAt(target);
  return { scene, camera, h };
}
export function update() {}

// ---------------------------------------------------------------------------------------------------------------
// props, in metres; head props in the head frame (origin = head bone pivot, +y up, +z forward); body props centred on the eyes
function buildProps(THREE, id, eye, eyeR) {
  const out = { head: new THREE.Group(), body: new THREE.Group(), lift: 0 };
  const topY = eye.y + 0.105;            // approx top of skull above the head pivot
  const cz = eye.z - 0.075;              // approx skull centre front-back
  if (id === 'A') {
    const metal = new THREE.MeshStandardMaterial({ color: 0xb9c0c8, metalness: 0.85, roughness: 0.32 });
    const bronze = new THREE.MeshStandardMaterial({ color: 0xc8892e, metalness: 0.9, roughness: 0.35 });
    const dome = new THREE.Mesh(new THREE.SphereGeometry(0.112, 64, 32, 0, Math.PI * 2, 0, Math.PI / 2), metal);
    dome.scale.set(0.97, 1.0, 1.1); dome.position.set(0, eye.y + 0.03, cz); out.head.add(dome);
    const band = new THREE.Mesh(new THREE.CylinderGeometry(0.1155, 0.1155, 0.032, 64, 1, true), bronze);
    band.scale.set(1, 1, 1.12); band.position.set(0, eye.y + 0.037, cz); out.head.add(band);
    const ridge = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.012, 0.25), bronze); ridge.position.set(0, eye.y + 0.03 + 0.119, cz); out.head.add(ridge);
    const ridge2 = new THREE.Mesh(new THREE.TorusGeometry(0.114, 0.006, 8, 64, Math.PI), bronze); ridge2.position.set(0, eye.y + 0.03, cz); ridge2.scale.set(1, 1.08, 1); out.head.add(ridge2);
    const nose = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.045, 0.01), bronze); nose.position.set(0, eye.y + 0.03, cz + 0.13); out.head.add(nose);
    const hornMat = new THREE.MeshStandardMaterial({ color: 0xf1e6cc, roughness: 0.45 });
    for (const s of [-1, 1]) {
      const path = new THREE.CatmullRomCurve3([new THREE.Vector3(s * 0.1, 0, 0), new THREE.Vector3(s * 0.16, 0.03, 0.01), new THREE.Vector3(s * 0.19, 0.09, 0.02), new THREE.Vector3(s * 0.175, 0.15, 0.0)]);
      const horn = new THREE.Mesh(taperTube(THREE, path, 0.026, 0.003), hornMat);
      horn.position.set(0, eye.y + 0.07, cz); out.head.add(horn);
    }
    // fur collar round the shoulders
    out.body.add(fur(THREE, 0x5a3a22, 0.15, 0.05, -0.245, 0.0));
    out.lift = 0.035;
  }
  if (id === 'B') {
    const felt = new THREE.MeshStandardMaterial({ color: 0x1b1714, roughness: 0.85, side: THREE.DoubleSide });
    const gold = new THREE.MeshStandardMaterial({ color: 0xf2b630, metalness: 0.9, roughness: 0.3 });
    const crown = new THREE.Mesh(new THREE.SphereGeometry(0.108, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), felt);
    crown.scale.set(1.18, 1.38, 1.26); crown.position.set(0, eye.y + 0.015, cz); out.head.add(crown);
    const brimG = new THREE.RingGeometry(0.1, 0.2, 144, 6); brimG.rotateX(-Math.PI / 2);
    const pos = brimG.attributes.position, edge = [];
    const r0 = 0.1, rw = 0.1;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i), z = pos.getZ(i), r = Math.hypot(x, z), th = Math.atan2(x, z);
      const t = Math.max(0, (r - r0) / rw), side = 0.5 - 0.5 * Math.cos(3 * th);          // 0 at the three corners, 1 mid-side
      const rr = r0 + (r - r0) * (1 - 0.45 * side * t);
      pos.setXYZ(i, Math.sin(th) * rr, Math.pow(t, 1.25) * 0.105 * (0.18 + 0.82 * side), Math.cos(th) * rr * 1.08);
    }
    brimG.computeVertexNormals();
    const brim = new THREE.Mesh(brimG, felt); brim.position.set(0, eye.y + 0.02, cz); out.head.add(brim);
    // gold trim along the brim edge
    const pts = []; for (let k = 0; k <= 180; k++) { const th = k / 180 * Math.PI * 2, side = 0.5 - 0.5 * Math.cos(3 * th), rr = r0 + rw * (1 - 0.45 * side);
      pts.push(new THREE.Vector3(Math.sin(th) * rr, 0.105 * (0.18 + 0.82 * side), Math.cos(th) * rr * 1.08)); }
    const trim = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, true), 360, 0.005, 8, true), gold);
    trim.position.copy(brim.position); out.head.add(trim);
    out.head.rotation.z = 0.12; out.head.rotation.x = -0.05;
    // white lace jabot at the throat: a pleated cone hanging down
    const jg = new THREE.ConeGeometry(0.05, 0.12, 64, 6, true); const jp = jg.attributes.position;
    for (let i = 0; i < jp.count; i++) { const x = jp.getX(i), z = jp.getZ(i), y = jp.getY(i), th = Math.atan2(x, z), k = 1 + 0.25 * Math.abs(Math.sin(th * 9)) * (0.06 - y) / 0.12;
      jp.setXYZ(i, x * k, y, z * k); }
    jg.computeVertexNormals(); jg.rotateX(Math.PI);
    const jab = new THREE.Mesh(jg, new THREE.MeshStandardMaterial({ color: 0xfbf7ee, roughness: 0.8, side: THREE.DoubleSide }));
    jab.scale.set(1, 1, 0.45); jab.position.set(0, -0.255, 0.035); jab.rotation.x = -0.15; out.body.add(jab);
    out.lift = 0.03;
  }
  if (id === 'C') {
    // Elizabethan ruff: a pleated torus round the neck
    const g = new THREE.TorusGeometry(0.115, 0.06, 40, 220);
    const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), y = p.getY(i), z = p.getZ(i), phi = Math.atan2(y, x), R = Math.hypot(x, y);
      const k = 1 + 0.32 * Math.pow(Math.abs(Math.sin(phi * 30)), 0.6);
      const cx = Math.cos(phi) * 0.115, cy = Math.sin(phi) * 0.115;
      p.setXYZ(i, cx + (x - cx) * k, cy + (y - cy) * k, z * (0.75 + 0.25 * k));
    }
    g.computeVertexNormals(); g.rotateX(Math.PI / 2);
    const ruff = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0xece4d4, roughness: 0.85 }));
    ruff.scale.set(1.05, 0.9, 1.0); ruff.position.set(0, -0.175, -0.045); ruff.rotation.x = 0.12; out.body.add(ruff);
    // pearls: a band over the hair and drop earrings
    const pearl = new THREE.MeshPhysicalMaterial({ color: 0xfff8ee, roughness: 0.18, clearcoat: 1, sheen: 0.6, sheenColor: new THREE.Color(0xffd6e8) });
    const n = 30; const band = new THREE.InstancedMesh(new THREE.SphereGeometry(0.0085, 16, 12), pearl, n); const m = new THREE.Matrix4();
    for (let i = 0; i < n; i++) { const a = -1.25 + 2.5 * i / (n - 1); m.makeTranslation(Math.sin(a) * 0.098, eye.y + 0.035 + Math.cos(a) * 0.05, cz + 0.005 + Math.cos(a) * 0.085); band.setMatrixAt(i, m); }
    out.head.add(band);
    const jewel = new THREE.Mesh(new THREE.OctahedronGeometry(0.016), new THREE.MeshPhysicalMaterial({ color: 0xd0103a, roughness: 0.1, metalness: 0.2, clearcoat: 1 }));
    jewel.position.set(0, eye.y + 0.035 + 0.05, cz + 0.005 + 0.093); out.head.add(jewel);
    out.lift = 0.0;
  }
  if (id === 'D') {
    const silk = new THREE.MeshPhysicalMaterial({ color: 0x141418, roughness: 0.35, sheen: 0.6, sheenColor: new THREE.Color(0x6a6a80) });
    const hatY = eye.y + 0.045;
    const crown = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.095, 0.15, 64), silk); crown.scale.z = 1.15; crown.position.set(0, hatY + 0.075, cz); out.head.add(crown);
    const brimG = new THREE.CylinderGeometry(0.155, 0.155, 0.008, 64); const brim = new THREE.Mesh(brimG, silk); brim.scale.z = 1.12; brim.position.set(0, hatY + 0.004, cz); out.head.add(brim);
    const bandM = new THREE.MeshStandardMaterial({ color: 0x7a1420, roughness: 0.6 });
    const band = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.03, 64, 1, true), bandM); band.scale.z = 1.15; band.position.set(0, hatY + 0.025, cz); out.head.add(band);
    out.head.rotation.z = -0.1;
    // monocle on his right eye + chain
    const gold = new THREE.MeshStandardMaterial({ color: 0xf0b838, metalness: 0.95, roughness: 0.25 });
    const mono = new THREE.Group();
    mono.add(new THREE.Mesh(new THREE.TorusGeometry(0.02, 0.0026, 12, 48), gold));
    const glass = new THREE.Mesh(new THREE.CircleGeometry(0.0195, 48), new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.02, transparent: true, opacity: 0.12, clearcoat: 1 }));
    mono.add(glass);
    mono.position.set(eyeR.x + 0.004, eyeR.y - 0.006, eyeR.z + 0.036); out.head.add(mono);
    const chain = new THREE.CatmullRomCurve3([new THREE.Vector3(eyeR.x - 0.012, eyeR.y - 0.015, eyeR.z + 0.02), new THREE.Vector3(eyeR.x - 0.05, eyeR.y - 0.09, eyeR.z + 0.0), new THREE.Vector3(eyeR.x - 0.06, eyeR.y - 0.2, eyeR.z - 0.02)]);
    out.head.add(new THREE.Mesh(new THREE.TubeGeometry(chain, 40, 0.0012, 6), gold));
    // bow tie
    const bow = new THREE.MeshStandardMaterial({ color: 0x7a1420, roughness: 0.5 });
    for (const s of [-1, 1]) { const w = new THREE.Mesh(new THREE.ConeGeometry(0.03, 0.05, 4), bow); w.rotation.z = s * Math.PI / 2; w.position.set(s * 0.026, -0.205, 0.06); w.scale.set(1, 1, 0.4); out.body.add(w); }
    const knot = new THREE.Mesh(new THREE.SphereGeometry(0.012, 12, 8), bow); knot.position.set(0, -0.205, 0.065); out.body.add(knot);
    out.lift = 0.055;
  }
  return out;
}

// tube whose radius tapers from r0 to r1 along the path (horns)
function taperTube(THREE, path, r0, r1, seg = 48, rad = 20) {
  const g = new THREE.TubeGeometry(path, seg, 1, rad, false);
  const p = g.attributes.position, c = new THREE.Vector3();
  for (let i = 0; i <= seg; i++) {
    const u = i / seg; path.getPointAt(u, c); const r = r0 + (r1 - r0) * Math.pow(u, 0.9);
    for (let j = 0; j <= rad; j++) { const k = i * (rad + 1) + j; p.setXYZ(k, c.x + (p.getX(k) - c.x) * r, c.y + (p.getY(k) - c.y) * r, c.z + (p.getZ(k) - c.z) * r); }
  }
  g.computeVertexNormals(); return g;
}

// chunky fur collar: noisy torus with a streaky texture
function fur(THREE, color, R, r, y, z) {
  const g = new THREE.TorusGeometry(R, r, 32, 160); const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) { const n = 1 + 0.18 * Math.sin(i * 12.9898) * Math.sin(i * 0.37) + 0.1 * Math.sin(i * 3.1); p.setXYZ(i, p.getX(i) * (1 + (n - 1) * 0.15), p.getY(i) * (1 + (n - 1) * 0.15), p.getZ(i) * n); }
  g.computeVertexNormals(); g.rotateX(Math.PI / 2);
  const tex = ctex(THREE, 512, 512, (gg, w, h) => { gg.fillStyle = '#' + new THREE.Color(color).getHexString(); gg.fillRect(0, 0, w, h);
    for (let i = 0; i < 9000; i++) { const v = Math.random(); gg.strokeStyle = v > 0.5 ? 'rgba(255,230,200,0.18)' : 'rgba(30,15,5,0.25)'; gg.lineWidth = 1.5; const x = Math.random() * w, yy = Math.random() * h; gg.beginPath(); gg.moveTo(x, yy); gg.lineTo(x + Math.random() * 4 - 2, yy + 10 + Math.random() * 14); gg.stroke(); } }, { repeat: [10, 2] });
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ map: tex, roughness: 0.95 }));
  m.scale.set(1.3, 1, 1.05); m.position.set(0, y, z - 0.06); return m;
}

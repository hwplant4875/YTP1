// Friedrichstraße station border checkpoint, March 1974 (Czesław Kukuczka).
// Tasteful: no blood, only shadow, a muzzle flash and a falling silhouette / dropped briefcase.
// shots:
//   bomb   (7.3 s) - embassy office at night: close on a hand gripping a briefcase with a crude fake bomb
//                    (taped tubes, cheap ticking alarm clock, wires) under a single desk lamp; slow pull back
//                    reveals the man in a coat behind the desk, venetian-blind shadows on the wall
//   agree  (2.2 s) - passport-control booth window: an official's hand slams a stamp onto an open passport
//   shot   (4.9 s) - checkpoint corridor: the man walks towards the bright door to the West; a hidden officer
//                    steps out of a dark alcove; muzzle flash at 1.6 s (2 frames); the man drops, briefcase falls
//   steps  (3.0 s) - low on the floor behind the dropped briefcase: the empty corridor, the West door a few
//                    steps away, its light flickering
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { AMBER, tileTex, concreteTex, rng, lerp } from './lib.js';
import { makeComposer, glow, beam, normalFromHeight, smooth } from './look.js';

const DOOR_Z = -17, CW = 1.8, CH = 3.1;    // corridor half width, height
const T_SHOT = 1.6;

// ---------------------------------------------------------------- helpers
function ctex(THREE, w, h, draw, rep = [1, 1]) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}
const UP = [0, 1, 0];
function seg(THREE, mesh, a, b) {
  const d = new THREE.Vector3().subVectors(b, a); const L = d.length();
  mesh.position.copy(a).add(b).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(...UP), d.multiplyScalar(1 / L));
  mesh.scale.set(1, L, 1);
}
// two-bone IK: root a, target c, bone lengths l1/l2, pole direction -> joint position
function ik(THREE, a, c, l1, l2, pole) {
  const d0 = new THREE.Vector3().subVectors(c, a); let d = d0.length();
  d = Math.min(Math.max(d, 1e-3), l1 + l2 - 1e-3);
  const dir = d0.normalize();
  const x = (l1 * l1 - l2 * l2 + d * d) / (2 * d); const h = Math.sqrt(Math.max(0, l1 * l1 - x * x));
  const p = pole.clone().addScaledVector(dir, -pole.dot(dir)).normalize();
  return a.clone().addScaledVector(dir, x).addScaledVector(p, h);
}

// civilian man in a 1970s coat; limbs are posed every frame with IK. Faces +z. Origin at the feet.
function makeMan(THREE, { coatMat, skinMat, hairMat, trouserMat, shoeMat, hat = false, hatMat = null }) {
  const root = new THREE.Group();
  const body = new THREE.Group(); root.add(body);
  const add = (parent, geo, mat, x = 0, y = 0, z = 0) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; parent.add(m); return m; };
  const prof = [[0.0, -0.44], [0.29, -0.44], [0.278, -0.2], [0.245, 0.05], [0.225, 0.2], [0.24, 0.36], [0.255, 0.48], [0.235, 0.56], [0.15, 0.6], [0.07, 0.63], [0, 0.63]]
    .map(([r, y]) => new THREE.Vector2(r, y));
  add(body, new THREE.LatheGeometry(prof, 32), coatMat).scale.set(1, 1, 0.68);
  // turned-up collar and lapels
  const col = add(body, new THREE.CylinderGeometry(0.1, 0.13, 0.12, 20, 1, true), coatMat, 0, 0.64, -0.01); col.material = coatMat;
  for (const sx of [-1, 1]) { const lp = add(body, new THREE.BoxGeometry(0.07, 0.34, 0.02), coatMat, sx * 0.07, 0.38, 0.165); lp.rotation.set(-0.12, 0, sx * 0.32); }
  const btn = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.4 });
  for (let i = 0; i < 3; i++) add(body, new THREE.SphereGeometry(0.012, 8, 6), btn, 0.03, 0.18 - i * 0.16, 0.168 - i * 0.004);
  add(body, new THREE.CylinderGeometry(0.05, 0.06, 0.09, 12), skinMat, 0, 0.68, 0);
  const head = new THREE.Group(); head.position.set(0, 0.79, 0.01); body.add(head);
  add(head, new THREE.SphereGeometry(0.1, 24, 18), skinMat).scale.set(0.9, 1.12, 1.0);
  const hair = add(head, new THREE.SphereGeometry(0.106, 24, 12, 0, Math.PI * 2, 0, Math.PI * 0.55), hairMat, 0, 0.015, -0.008); hair.scale.set(0.92, 1.1, 1.02);
  add(head, new THREE.BoxGeometry(0.022, 0.04, 0.03), skinMat, 0, 0.0, 0.097).rotation.x = -0.25;       // nose
  for (const sx of [-1, 1]) add(head, new THREE.SphereGeometry(0.022, 8, 6), skinMat, sx * 0.09, 0.0, 0).scale.set(0.5, 1, 0.8);
  if (hat) {
    add(head, new THREE.CylinderGeometry(0.1, 0.118, 0.1, 20), hatMat, 0, 0.115, 0);
    add(head, new THREE.CylinderGeometry(0.185, 0.185, 0.012, 24), hatMat, 0, 0.07, 0.0);
  }
  // limbs
  const limbs = {};
  const mk = (r, mat) => { const m = add(root, new THREE.CylinderGeometry(r, r * 0.92, 1, 12), mat); return m; };
  const joint = (r, mat) => add(root, new THREE.SphereGeometry(r, 12, 8), mat);
  for (const s of ['L', 'R']) {
    limbs['ua' + s] = mk(0.062, coatMat); limbs['fa' + s] = mk(0.055, coatMat); limbs['el' + s] = joint(0.058, coatMat);
    limbs['th' + s] = mk(0.075, trouserMat); limbs['sh' + s] = mk(0.06, trouserMat); limbs['kn' + s] = joint(0.064, trouserMat);
    const shoe = add(root, new THREE.BoxGeometry(0.1, 0.08, 0.27), shoeMat); limbs['shoe' + s] = shoe;
    limbs['hand' + s] = makeHand(THREE, skinMat, coatMat); root.add(limbs['hand' + s]);
  }
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const man = {
    root, body, head, limbs,
    // pose: {hipY, lean, yaw, handL, handR (root-local), palmL, palmR (direction the palm faces), footL, footR, elbowPole}
    pose(p) {
      body.position.set(0, p.hipY ?? 0.95, p.hipZ ?? 0); body.rotation.set(p.lean ?? 0, 0, p.roll ?? 0);
      head.rotation.set(p.headPitch ?? 0, p.headYaw ?? 0, 0);
      body.updateMatrix();
      for (const s of ['L', 'R']) {
        const sx = s === 'L' ? 1 : -1;
        const S = V(sx * 0.215, 0.5, 0).applyMatrix4(body.matrix);
        const Hd = p['hand' + s];
        const E = ik(THREE, S, Hd, 0.3, 0.27, p['elbowPole' + s] ?? V(sx * 0.4, -0.2, -1));
        seg(THREE, limbs['ua' + s], S, E); seg(THREE, limbs['fa' + s], E, Hd); limbs['el' + s].position.copy(E);
        const hand = limbs['hand' + s]; hand.position.copy(Hd);
        const yAx = Hd.clone().sub(E).normalize();
        const zAx = (p['palm' + s] ?? V(-sx, 0, 0)).clone(); zAx.addScaledVector(yAx, -zAx.dot(yAx)).normalize();
        const xAx = new THREE.Vector3().crossVectors(yAx, zAx);
        hand.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(xAx, yAx, zAx));
        // legs
        const Hp = V(sx * 0.1, 0, 0).applyMatrix4(body.matrix);
        const F = p['foot' + s];
        const K = ik(THREE, Hp, V(F.x, F.y + 0.07, F.z), 0.46, 0.46, V(0, 0, 1));
        const A = V(F.x, F.y + 0.07, F.z);
        seg(THREE, limbs['th' + s], Hp, K); seg(THREE, limbs['sh' + s], K, A); limbs['kn' + s].position.copy(K);
        limbs['shoe' + s].position.set(F.x, F.y + 0.04, F.z + 0.06); limbs['shoe' + s].rotation.set(p['footPitch' + s] ?? 0, 0, 0);
      }
    },
  };
  return man;
}
// gripping hand: wrist at origin, hand extends along +y, palm faces +z, fingers curl towards +z
function makeHand(THREE, skin, sleeve) {
  const g = new THREE.Group();
  const add = (geo, mat, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; g.add(m); return m; };
  add(new THREE.CylinderGeometry(0.06, 0.063, 0.06, 14), sleeve, 0, -0.03, 0);           // cuff
  const palm = add(new RoundedBoxGeometry(0.084, 0.1, 0.036, 3, 0.014), skin, 0, 0.042, 0.0);
  const fseg = (a, b, r) => { const m = add(new THREE.CylinderGeometry(r, r, 1, 8), skin, 0, 0, 0); seg(THREE, m, a, b); const j = add(new THREE.SphereGeometry(r, 8, 6), skin, b.x, b.y, b.z); return m; };
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  [[-0.03, 0.0095, 0.92], [-0.01, 0.0105, 1.0], [0.01, 0.01, 0.97], [0.03, 0.0088, 0.82]].forEach(([fx, r, l]) => {
    const p0 = V(fx, 0.088, 0), p1 = V(fx, 0.088 + 0.04 * l, 0.012), p2 = V(fx, 0.09 + 0.045 * l, 0.045 * l), p3 = V(fx, 0.075 + 0.02 * l, 0.06 * l);
    add(new THREE.SphereGeometry(r * 1.1, 8, 6), skin, p0.x, p0.y, p0.z);
    fseg(p0, p1, r); fseg(p1, p2, r * 0.95); fseg(p2, p3, r * 0.9);
  });
  const t0 = V(0.04, 0.02, 0.01), t1 = V(0.055, 0.055, 0.03), t2 = V(0.035, 0.085, 0.05);
  fseg(t0, t1, 0.012); fseg(t1, t2, 0.011);
  return g;
}

// walking gait at distance d (m) along +z of the man's root
function gait(THREE, d, opt = {}) {
  const stride = 0.72, ph = d / stride * Math.PI;
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const foot = (i) => { const f = ph + i * Math.PI; const c = Math.cos(f); return V(i ? -0.1 : 0.1, Math.max(0, c) * 0.1, 0.24 * Math.sin(f)); };
  return {
    hipY: 0.94 + 0.018 * Math.cos(2 * ph), lean: 0.05,
    footL: foot(0), footR: foot(1),
    handL: V(0.27, 0.62, -0.17 * Math.sin(ph)), handR: opt.carry ? V(-0.26, 0.63, 0.02 + 0.04 * Math.sin(ph)) : V(-0.27, 0.62, 0.17 * Math.sin(ph)),
    palmL: V(-1, 0, 0), palmR: V(1, 0, 0), roll: 0.02 * Math.sin(ph),
  };
}

// the fake bomb: briefcase standing on its edge, tubes taped to the front, alarm clock, wires
function makeBomb(THREE, std, clockFaceTex) {
  const g = new THREE.Group();
  const leather = std({ map: ctex(THREE, 256, 256, (x, w, h) => { const r = rng(4); x.fillStyle = '#4a3423'; x.fillRect(0, 0, w, h);
    for (let i = 0; i < 3000; i++) { const v = r(); x.fillStyle = `rgba(${v > 0.5 ? 90 : 20},${v > 0.5 ? 66 : 14},${v > 0.5 ? 44 : 8},0.18)`; x.fillRect(r() * w, r() * h, 2, 2); }
    for (let i = 0; i < 30; i++) { x.strokeStyle = 'rgba(160,130,100,0.25)'; x.lineWidth = 1; x.beginPath(); const a = r() * w, b = r() * h; x.moveTo(a, b); x.lineTo(a + r() * 40 - 20, b + r() * 10); x.stroke(); }
  }), roughness: 0.55 });
  const brass = std({ color: 0xc9a25a, metalness: 1, roughness: 0.3 });
  const W = 0.46, H = 0.34, D = 0.11;
  const box = new THREE.Mesh(new THREE.BoxGeometry(W, H, D, 2, 2, 2), leather); box.position.y = H / 2; box.castShadow = box.receiveShadow = true; g.add(box);
  const seam = new THREE.Mesh(new THREE.BoxGeometry(W + 0.006, 0.012, D + 0.006), std({ color: 0x2a1c12 })); seam.position.y = H - 0.05; g.add(seam);
  for (const sx of [-1, 1]) { const l = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.03, 0.012), brass); l.position.set(sx * 0.14, H - 0.05, D / 2 + 0.006); g.add(l); }
  // handle
  const hc = new THREE.CatmullRomCurve3([[-0.08, 0], [-0.075, 0.035], [-0.04, 0.05], [0.04, 0.05], [0.075, 0.035], [0.08, 0]].map(([x, y]) => new THREE.Vector3(x, H + y, 0)));
  const handle = new THREE.Mesh(new THREE.TubeGeometry(hc, 24, 0.012, 8), leather); handle.castShadow = true; g.add(handle);
  // three tubes wrapped in paper, strapped with tape
  const paper = std({ map: ctex(THREE, 128, 64, (x, w, h) => { x.fillStyle = '#b8ad96'; x.fillRect(0, 0, w, h); x.fillStyle = 'rgba(60,50,40,0.5)'; x.font = 'bold 18px "DejaVu Sans Condensed"'; x.fillText('ACHTUNG', 10, 40); }), roughness: 0.9 });
  for (let i = 0; i < 3; i++) { const c = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.026, 0.36, 16), paper); c.rotation.z = Math.PI / 2; c.position.set(0, 0.07 + i * 0.052, D / 2 + 0.028); c.castShadow = true; g.add(c); }
  const tape = std({ color: 0x777066, roughness: 0.6 });
  for (const tx of [-0.13, 0.13]) { const t = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.185, 0.062), tape); t.position.set(tx, 0.122, D / 2 + 0.026); g.add(t); }
  // alarm clock
  const clock = new THREE.Group(); clock.position.set(0.0, 0.2, D / 2 + 0.085); g.add(clock);
  const tin = std({ color: 0x8c8c88, metalness: 0.85, roughness: 0.35 });
  const caseM = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.04, 32), tin); caseM.rotation.x = Math.PI / 2; caseM.castShadow = true; clock.add(caseM);
  const face = new THREE.Mesh(new THREE.CircleGeometry(0.052, 32), std({ map: clockFaceTex, roughness: 0.4 })); face.position.z = 0.0205; clock.add(face);
  const glass = new THREE.Mesh(new THREE.SphereGeometry(0.06, 24, 8, 0, Math.PI * 2, 0, 0.5), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.05, metalness: 0.2, transparent: true, opacity: 0.12 }));
  glass.rotation.x = Math.PI / 2; glass.position.z = -0.03; clock.add(glass);
  for (const sx of [-1, 1]) { const b = new THREE.Mesh(new THREE.SphereGeometry(0.03, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), tin); b.position.set(sx * 0.04, 0.062, 0); b.rotation.z = -sx * 0.5; clock.add(b); }
  const hammer = new THREE.Mesh(new THREE.BoxGeometry(0.006, 0.03, 0.006), tin); hammer.position.set(0, 0.075, 0); clock.add(hammer);
  for (const sx of [-1, 1]) { const f = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.004, 0.03, 6), tin); f.position.set(sx * 0.04, -0.065, 0); f.rotation.z = sx * 0.4; clock.add(f); }
  const handM = new THREE.MeshStandardMaterial({ color: 0x111111 });
  const hHour = new THREE.Mesh(new THREE.BoxGeometry(0.005, 0.03, 0.002), handM); hHour.geometry.translate(0, 0.013, 0); hHour.position.z = 0.023; clock.add(hHour);
  const hMin = new THREE.Mesh(new THREE.BoxGeometry(0.004, 0.044, 0.002), handM); hMin.geometry.translate(0, 0.02, 0); hMin.position.z = 0.024; clock.add(hMin);
  const hSec = new THREE.Mesh(new THREE.BoxGeometry(0.0015, 0.046, 0.002), std({ color: 0xb08040 })); hSec.geometry.translate(0, 0.016, 0); hSec.position.z = 0.025; clock.add(hSec);
  hHour.rotation.z = -2.4; hMin.rotation.z = -0.9;
  // wires
  const wireMats = [0x1b1b1b, 0x8a6a3a, 0x5a5a5a].map(c => std({ color: c, roughness: 0.4 }));
  const wires = [
    [[0.05, 0.22, D / 2 + 0.07], [0.14, 0.27, D / 2 + 0.06], [0.2, 0.25, D / 2 + 0.03], [0.17, H - 0.05, D / 2 + 0.01]],
    [[-0.05, 0.2, D / 2 + 0.07], [-0.15, 0.24, D / 2 + 0.07], [-0.2, 0.15, D / 2 + 0.05], [-0.17, 0.07, D / 2 + 0.05]],
    [[0.03, 0.15, D / 2 + 0.07], [0.09, 0.08, D / 2 + 0.07], [0.19, 0.06, D / 2 + 0.06], [0.24, 0.12, D / 2], [0.23, 0.29, 0]],
    [[-0.02, 0.26, D / 2 + 0.07], [-0.08, 0.32, D / 2 + 0.05], [-0.12, H - 0.05, D / 2 + 0.008]],
  ];
  wires.forEach((pts, i) => { const tb = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map(p => new THREE.Vector3(...p))), 40, 0.0045, 6), wireMats[i % 3]); tb.castShadow = true; g.add(tb); });
  return { group: g, hSec, hMin, H, D };
}

// ---------------------------------------------------------------- scene
export async function setup(THREE, renderer, W, H) {
  const shotArg = (new URLSearchParams(location.search).get('shot') || 'shot').split('|');
  const shot = shotArg[0];
  window.DBGCAM = shotArg[1] && shotArg[1].includes(',') ? shotArg[1].split(',').map(Number) : null;
  window.HIDE = shotArg[2] || '';
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x030303);
  const camera = new THREE.PerspectiveCamera(36, W / H, 0.02, 200);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.8, metalness: 0, ...o });
  const r = rng(74);

  const coatMat = std({ color: 0x5c5852, roughness: 0.95 });
  const skinMat = std({ color: 0xb08f78, roughness: 0.6 });
  const hairMat = std({ color: 0x1d1a17, roughness: 0.8 });
  const trouserMat = std({ color: 0x2b2a28, roughness: 0.9 });
  const shoeMat = std({ color: 0x0d0c0b, roughness: 0.35 });
  const clockFace = ctex(THREE, 256, 256, (g, w, h) => {
    g.fillStyle = '#e8e0cc'; g.fillRect(0, 0, w, h); g.fillStyle = '#151515'; g.font = 'bold 30px "DejaVu Sans"'; g.textAlign = 'center'; g.textBaseline = 'middle';
    for (let i = 1; i <= 12; i++) { const a = i / 12 * Math.PI * 2; g.fillText(String(i), 128 + Math.sin(a) * 98, 128 - Math.cos(a) * 98); }
    for (let i = 0; i < 60; i++) { const a = i / 60 * Math.PI * 2; g.fillRect(128 + Math.sin(a) * 118 - 1, 128 - Math.cos(a) * 118 - 1, 3, 3); }
    g.font = '14px "DejaVu Serif"'; g.fillText('RUHLA', 128, 168);
  });

  const ctx = { THREE, scene, camera, shot };

  if (shot === 'bomb') {
    // ================= embassy office
    scene.fog = new THREE.FogExp2(0x050403, 0.06);
    const room = new THREE.Group(); scene.add(room);
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(10, 10), std({ map: ctex(THREE, 256, 256, (g, w, h) => {
      g.fillStyle = '#4a3a2c'; g.fillRect(0, 0, w, h);
      for (let y = 0; y < h; y += 32) { const o = (y / 32 % 2) * 64; for (let x = -64; x < w; x += 128) { const v = 60 + r() * 30; g.fillStyle = `rgb(${v + 14},${v},${v - 12})`; g.fillRect(x + o + 1, y + 1, 126, 30); } }
    }, [6, 6]), roughness: 0.6 }));
    floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; room.add(floor);
    // back wall with wainscot and a window with venetian blinds
    const wallTex = ctex(THREE, 512, 512, (g, w, h) => { g.fillStyle = '#7d766a'; g.fillRect(0, 0, w, h);
      for (let x = 0; x < w; x += 24) { g.fillStyle = 'rgba(0,0,0,0.05)'; g.fillRect(x, 0, 10, h); }
      for (let i = 0; i < 2000; i++) { g.fillStyle = `rgba(30,25,20,${r() * 0.06})`; g.fillRect(r() * w, r() * h, 3, 3); } }, [3, 1]);
    const wallM = std({ map: wallTex, roughness: 0.9 });
    const wz = -2.2;
    const wl = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 3.2), wallM); wl.position.set(-2.6, 1.6, wz); wl.receiveShadow = true; room.add(wl);
    const wr = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 3.2), wallM); wr.position.set(2.6, 1.6, wz); wr.receiveShadow = true; room.add(wr);
    const wb = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 0.9), wallM); wb.position.set(0, 0.45, wz); wb.receiveShadow = true; room.add(wb);
    const wt = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 0.6), wallM); wt.position.set(0, 2.9, wz); wt.receiveShadow = true; room.add(wt);
    const side = new THREE.Mesh(new THREE.PlaneGeometry(6, 3.2), wallM); side.position.set(-2.4, 1.6, 0.5); side.rotation.y = Math.PI / 2; side.receiveShadow = true; room.add(side);
    const wood = std({ color: 0x3a2a1c, roughness: 0.5 });
    const frameM = std({ color: 0x2a2018, roughness: 0.6 });
    for (const [w, h, x, y] of [[2.5, 0.08, 0, 0.9], [2.5, 0.08, 0, 2.6], [0.08, 1.8, -1.2, 1.75], [0.08, 1.8, 1.2, 1.75], [0.06, 1.7, 0, 1.75]]) {
      const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.12), frameM); b.position.set(x, y, wz); b.castShadow = true; room.add(b);
    }
    const sill = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.04, 0.3), frameM); sill.position.set(0, 0.92, wz + 0.1); room.add(sill);
    // night outside: dim city glow
    const night = new THREE.Mesh(new THREE.PlaneGeometry(6, 4), new THREE.MeshBasicMaterial({ map: ctex(THREE, 256, 128, (g, w, h) => {
      const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#0b0c10'); gr.addColorStop(1, '#2a2622'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(255,190,120,${0.3 + r() * 0.5})`; g.fillRect(r() * w, h * 0.55 + r() * h * 0.4, 2, 2); } }) }));
    night.position.set(0, 1.6, wz - 1.6); room.add(night);
    // blinds (slats) - they cut the streetlight into stripes
    const slatM = std({ color: 0x9a948a, roughness: 0.5, metalness: 0.2, side: THREE.DoubleSide });
    for (let y = 0.98; y < 2.55; y += 0.055) { const s = new THREE.Mesh(new THREE.BoxGeometry(2.36, 0.004, 0.045), slatM); s.position.set(0, y, wz + 0.04); s.rotation.x = 0.55; s.castShadow = true; s.receiveShadow = true; room.add(s); }
    const street = new THREE.SpotLight(0xdfe4ff, 9, 14, 0.38, 0.25, 1.0); street.position.set(-1.6, 4.8, wz - 3.2); street.target.position.set(0.6, 0.5, 0.8);
    street.castShadow = true; street.shadow.mapSize.set(2048, 2048); street.shadow.bias = -0.0004; room.add(street, street.target);
    // a framed print on the wall, a coat stand silhouette
    const pic = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.7, 0.03), frameM); pic.position.set(-2.0, 1.75, wz + 0.02); room.add(pic);
    const picIn = new THREE.Mesh(new THREE.PlaneGeometry(0.45, 0.6), std({ map: ctex(THREE, 128, 160, (g, w, h) => { g.fillStyle = '#8a8070'; g.fillRect(0, 0, w, h); g.fillStyle = '#3a342c'; g.beginPath(); g.moveTo(0, h); g.lineTo(w * 0.3, h * 0.45); g.lineTo(w * 0.55, h * 0.7); g.lineTo(w * 0.8, h * 0.35); g.lineTo(w, h); g.fill(); }) }));
    picIn.position.set(-2.0, 1.75, wz + 0.04); room.add(picIn);
    // desk
    const deskY = 0.76;
    const top = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.05, 0.85), std({ map: ctex(THREE, 512, 256, (g, w, h) => { g.fillStyle = '#4b3524'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 80; i++) { g.strokeStyle = `rgba(${20 + r() * 30},${12 + r() * 20},8,${0.2 + r() * 0.3})`; g.lineWidth = 1 + r() * 2; g.beginPath(); const y = r() * h; g.moveTo(0, y); g.bezierCurveTo(w * 0.3, y + r() * 20 - 10, w * 0.6, y + r() * 20 - 10, w, y + r() * 10 - 5); g.stroke(); } }), roughness: 0.35 }));
    top.position.set(0, deskY - 0.025, 0); top.receiveShadow = true; top.castShadow = true; room.add(top);
    for (const sx of [-1, 1]) { const pd = new THREE.Mesh(new THREE.BoxGeometry(0.42, deskY - 0.05, 0.8), wood); pd.position.set(sx * 0.62, (deskY - 0.05) / 2, 0); pd.castShadow = true; pd.receiveShadow = true; room.add(pd);
      for (let k = 0; k < 3; k++) { const kn = new THREE.Mesh(new THREE.SphereGeometry(0.012, 8, 6), std({ color: 0x9c7a44, metalness: 1, roughness: 0.3 })); kn.position.set(sx * 0.62, 0.15 + k * 0.2, 0.41); room.add(kn); } }
    // desk lamp (single practical light)
    const lampM = std({ color: 0x2b2b29, metalness: 0.7, roughness: 0.35 });
    const lb = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.1, 0.025, 24), lampM); lb.position.set(-0.55, deskY + 0.012, 0.22); room.add(lb);
    const arm1 = new THREE.Mesh(new THREE.CylinderGeometry(0.01, 0.01, 1, 8), lampM); seg(THREE, arm1, new THREE.Vector3(-0.55, deskY, 0.22), new THREE.Vector3(-0.52, deskY + 0.4, 0.14)); room.add(arm1);
    const arm2 = new THREE.Mesh(new THREE.CylinderGeometry(0.01, 0.01, 1, 8), lampM); seg(THREE, arm2, new THREE.Vector3(-0.52, deskY + 0.4, 0.14), new THREE.Vector3(-0.3, deskY + 0.47, 0.3)); room.add(arm2);
    const shade = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.17, 28, 1, true), std({ color: 0x232321, metalness: 0.6, roughness: 0.4, side: THREE.DoubleSide }));
    shade.position.set(-0.27, deskY + 0.43, 0.33); shade.rotation.set(0.35, 0, 0.75); shade.castShadow = true; room.add(shade);
    const bulbP = new THREE.Vector3(-0.235, deskY + 0.39, 0.32);
    const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.03, 12, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(3, 2.2, 1.3) })); bulb.position.copy(bulbP); room.add(bulb);
    const halo = glow(THREE, AMBER, 0.3, 0.5); halo.position.copy(bulbP); room.add(halo);
    const lamp = new THREE.SpotLight(AMBER, 1.9, 5, 0.8, 0.6, 1.6); lamp.position.copy(bulbP); lamp.target.position.set(0.12, deskY + 0.1, 0.1);
    lamp.castShadow = true; lamp.shadow.mapSize.set(1024, 1024); lamp.shadow.bias = -0.0003; lamp.shadow.camera.near = 0.05; room.add(lamp, lamp.target);
    const fill = new THREE.SpotLight(AMBER, 0.5, 3, 0.45, 0.8, 1.5); fill.position.set(0.15, 0.82, 0.2); fill.target.position.set(0.18, 1.6, -0.62); room.add(fill, fill.target);
    scene.add(new THREE.HemisphereLight(0x8890a0, 0x0a0806, 0.06));
    // desk props: papers, telephone, ashtray
    const paperM = std({ color: 0xcfc8b8, roughness: 0.9 });
    for (let i = 0; i < 3; i++) { const pp = new THREE.Mesh(new THREE.BoxGeometry(0.21, 0.002, 0.3), paperM); pp.position.set(-0.45 + i * 0.03, deskY + 0.002 + i * 0.002, 0.2); pp.rotation.y = 0.2 - i * 0.15; pp.receiveShadow = true; room.add(pp); }
    const phoneM = std({ color: 0x141414, roughness: 0.25 });
    const ph = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.08, 0.22), phoneM); ph.position.set(0.6, deskY + 0.04, -0.15); ph.rotation.y = -0.3; ph.castShadow = true; room.add(ph);
    const rcv = new THREE.Mesh(new THREE.CapsuleGeometry(0.025, 0.17, 4, 10), phoneM); rcv.rotation.set(0, -0.3, Math.PI / 2); rcv.position.set(0.6, deskY + 0.1, -0.15); room.add(rcv);
    const dial = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.01, 20), std({ color: 0x8a8a86, metalness: 0.6 })); dial.position.set(0.62, deskY + 0.082, -0.1); dial.rotation.x = 0.4; room.add(dial);
    const ash = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.05, 0.025, 20), std({ color: 0x777, metalness: 0.4, roughness: 0.3 })); ash.position.set(0.35, deskY + 0.013, 0.25); room.add(ash);
    // the bomb
    const bomb = makeBomb(THREE, std, clockFace); bomb.group.position.set(0.12, deskY, 0.12); bomb.group.rotation.y = -0.18; room.add(bomb.group);
    // the man behind the desk
    const man = makeMan(THREE, { coatMat, skinMat, hairMat, trouserMat, shoeMat });
    man.root.position.set(0.18, 0, -0.62); room.add(man.root);
    // dust in the lamp light
    const dust = makeDust(THREE, 500, [-1, 1.2], [0.8, 2.0], [-0.6, 1.2], 0.012, 21); room.add(dust.pts);
    const post = makeComposer(THREE, renderer, scene, camera, W, H, { bloom: 0.8, bloomRadius: 0.6, bloomThreshold: 0.6, exposure: 1.1, dof: { focus: 0.6, aperture: 0.006, maxblur: 0.012 } });
    Object.assign(ctx, { bomb, man, deskY, dust, lamp }, post);
    return ctx;
  }

  // ================= checkpoint corridor
  scene.fog = new THREE.FogExp2(0x070605, 0.05);
  const tileN = normalFromHeight(THREE, 256, 256, (g, w, h) => { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; for (let y = 0; y < h; y += 16) for (let x = 0; x < w; x += 32) g.fillRect(x + 1, y + 1, 30, 14); }, 2.5, [24, 2]);
  const tileM = std({ map: tileTex(THREE, { repeat: [24, 2], tile: 32, grout: 3, base: 190, vary: 14, dirt: 0.35, seed: 8 }), normalMap: tileN, roughness: 0.5 });
  const plasterM = std({ map: concreteTex(THREE, [6, 1], 41, 132), roughness: 0.95 });
  const LEN = 24, ZC = DOOR_Z + LEN / 2;
  for (const sx of [-1, 1]) {
    const t = new THREE.Mesh(new THREE.PlaneGeometry(LEN, 1.9), tileM); t.position.set(sx * CW, 0.95, ZC); t.rotation.y = -sx * Math.PI / 2; t.receiveShadow = true; scene.add(t);
    const p = new THREE.Mesh(new THREE.PlaneGeometry(LEN, CH - 1.9), plasterM); p.position.set(sx * CW, 1.9 + (CH - 1.9) / 2, ZC); p.rotation.y = -sx * Math.PI / 2; p.receiveShadow = true; scene.add(p);
    const band = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.06, LEN), std({ color: 0x3a3a38, roughness: 0.4 })); band.position.set(sx * (CW - 0.01), 1.9, ZC); scene.add(band);
  }
  const floorTex = ctex(THREE, 256, 256, (g, w, h) => { for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { const v = ((x + y) % 2 ? 72 : 92) + r() * 8; g.fillStyle = `rgb(${v},${v - 2},${v - 5})`; g.fillRect(x * 32, y * 32, 32, 32); }
    for (let i = 0; i < 1500; i++) { g.fillStyle = `rgba(20,18,15,${r() * 0.15})`; g.fillRect(r() * w, r() * h, 2 + r() * 5, 1 + r() * 3); } }, [3.6 / 2.4, LEN / 2.4]);
  const floorRough = ctex(THREE, 256, 256, (g, w, h) => { g.fillStyle = '#666'; g.fillRect(0, 0, w, h); for (let i = 0; i < 60; i++) { g.fillStyle = `rgba(${r() > 0.5 ? 255 : 0},${0},0,0.2)`; g.beginPath(); g.ellipse(r() * w, r() * h, 10 + r() * 50, 5 + r() * 20, r() * 3, 0, 7); g.fill(); } }, [2, 10]);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(CW * 2, LEN), std({ map: floorTex, roughness: 0.92, metalness: 0.0 }));
  floor.rotation.x = -Math.PI / 2; floor.position.z = ZC; floor.receiveShadow = true; scene.add(floor);
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(CW * 2, LEN), std({ map: concreteTex(THREE, [2, 12], 43, 90) })); ceil.rotation.x = Math.PI / 2; ceil.position.set(0, CH, ZC); scene.add(ceil);
  const back = new THREE.Mesh(new THREE.PlaneGeometry(CW * 2, CH), plasterM); back.position.set(0, CH / 2, ZC + LEN / 2); back.rotation.y = Math.PI; scene.add(back);
  // ceiling ducts and conduit
  const pipeM = std({ color: 0x4a4a48, metalness: 0.6, roughness: 0.5 });
  for (const [x, y, rr] of [[1.45, CH - 0.15, 0.06], [1.25, CH - 0.12, 0.03], [-1.5, CH - 0.1, 0.035]]) { const pp = new THREE.Mesh(new THREE.CylinderGeometry(rr, rr, LEN, 10), pipeM); pp.rotation.x = Math.PI / 2; pp.position.set(x, y, ZC); scene.add(pp); }

  // ---- end wall with the door to the West
  const DX = 0.15, DW = 1.15, DH = 2.25;
  const endM = std({ map: concreteTex(THREE, [2, 2], 47, 120), roughness: 0.9 });
  const ew = (w, h, x, y) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.3), endM); m.position.set(x, y, DOOR_Z - 0.15); m.receiveShadow = true; m.castShadow = true; scene.add(m); };
  ew(CW + DX - DW / 2, CH, (-CW + DX - DW / 2) / 2, CH / 2);
  ew(CW - DX - DW / 2, CH, (CW + DX + DW / 2) / 2, CH / 2);
  ew(DW, CH - DH, DX, DH + (CH - DH) / 2);
  const steel = std({ color: 0x5a5a56, metalness: 0.6, roughness: 0.45 });
  const frameMat = std({ color: 0x2e2e2c, metalness: 0.5, roughness: 0.5 });
  for (const [w, h, x, y] of [[0.08, DH, DX - DW / 2 - 0.04, DH / 2], [0.08, DH, DX + DW / 2 + 0.04, DH / 2], [DW + 0.16, 0.08, DX, DH + 0.04]]) { const f = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.34), frameMat); f.position.set(x, y, DOOR_Z - 0.15); scene.add(f); }
  // door leaf, hinged on the right, standing ajar towards the West
  const hinge = new THREE.Group(); hinge.position.set(DX + DW / 2, 0, DOOR_Z - 0.3); scene.add(hinge);
  const leaf = new THREE.Mesh(new THREE.BoxGeometry(DW, DH - 0.02, 0.07), steel); leaf.position.set(-DW / 2, DH / 2, 0); leaf.castShadow = true; leaf.receiveShadow = true; hinge.add(leaf);
  for (const yy of [0.5, 1.75]) { const pnl = new THREE.Mesh(new THREE.BoxGeometry(DW - 0.2, 0.7, 0.01), std({ color: 0x4a4a46, metalness: 0.5, roughness: 0.5 })); pnl.position.set(-DW / 2, yy, 0.04); hinge.add(pnl); }
  const bar = new THREE.Mesh(new THREE.BoxGeometry(DW - 0.3, 0.05, 0.05), std({ color: 0x9a9a94, metalness: 1, roughness: 0.3 })); bar.position.set(-DW / 2, 1.05, 0.09); hinge.add(bar);
  hinge.rotation.y = -1.4;
  // the West: overexposed light beyond the door
  const westM = new THREE.MeshBasicMaterial({ color: new THREE.Color(5, 4.6, 4.0), fog: false });
  const west = new THREE.Mesh(new THREE.PlaneGeometry(5, 4), westM); west.position.set(DX, 1.5, DOOR_Z - 2.2); scene.add(west);
  const westSides = new THREE.Mesh(new THREE.BoxGeometry(2.2, 3.0, 2.0), std({ color: 0xd8d4cc, side: THREE.BackSide, emissive: 0xffffff, emissiveIntensity: 0.6 })); westSides.position.set(DX, 1.5, DOOR_Z - 1.3); scene.add(westSides);
  const sun = new THREE.SpotLight(0xfff1dc, 22, 30, 0.42, 0.5, 1.3); sun.position.set(DX - 0.15, 1.6, DOOR_Z - 1.4); sun.target.position.set(0.1, 0, DOOR_Z + 12);
  sun.castShadow = true; sun.shadow.mapSize.set(1024, 1024); sun.shadow.bias = -0.0005; sun.shadow.camera.near = 0.3; scene.add(sun, sun.target);
  const doorGlow = glow(THREE, 0xfff0dc, 2.2, 0.5); doorGlow.position.set(DX - 0.2, 1.3, DOOR_Z - 0.4); scene.add(doorGlow);
  const rays = beam(THREE, 0xfff0dc, 11, 2.2, 0.07); rays.position.set(DX - 0.15, 1.5, DOOR_Z - 0.3); rays.rotation.x = -Math.PI / 2 - 0.08; rays.rotation.z = Math.PI; scene.add(rays);
  rays.rotation.set(-Math.PI / 2 + 0.04, 0, 0);
  // sign over the door
  const signTex = ctex(THREE, 512, 96, (g, w, h) => { g.fillStyle = '#1a1a19'; g.fillRect(0, 0, w, h); g.fillStyle = '#d9d4c6'; g.font = 'bold 54px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('AUSGANG', w / 2, h / 2 + 3); });
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.2), std({ map: signTex, roughness: 0.5 })); sign.position.set(DX, DH + 0.35, DOOR_Z + 0.01); scene.add(sign);

  // ---- passport-control booths on the left
  const boothM = std({ color: 0x4b4842, roughness: 0.6 });
  const glassM = new THREE.MeshStandardMaterial({ color: 0x9aa09c, roughness: 0.25, metalness: 0.0, transparent: true, opacity: 0.12, depthWrite: false });
  const booths = [];
  const lampCount = [];
  for (const zc of [-2.0, -4.9]) {
    const bg = new THREE.Group(); bg.position.set(-CW + 0.65, 0, zc); scene.add(bg); booths.push(bg);
    const B = (w, h, d, x, y, z, m = boothM) => { const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); b.position.set(x, y, z); b.castShadow = true; b.receiveShadow = true; bg.add(b); return b; };
    B(1.2, 1.05, 0.06, 0, 0.525, -1.1); B(1.2, 1.05, 0.06, 0, 0.525, 1.1);   // side walls lower
    B(0.06, 1.05, 2.26, 0.6, 0.525, 0);                                     // front (to passage) lower
    B(1.32, 0.08, 2.4, 0, 2.4, 0, frameMat);                                // roof
    B(0.08, 0.06, 2.3, 0.62, 1.08, 0, frameMat);                            // counter on the passage side
    B(0.3, 0.035, 0.9, 0.73, 1.06, 0.3, boothM);                            // outside shelf
    for (const z of [-1.1, -0.15, 0.75, 1.1]) B(0.05, 1.3, 0.05, 0.6, 1.75, z, frameMat);
    for (const z of [-1.1, 1.1]) for (const x of [-0.6, 0.6]) B(0.05, 1.3, 0.05, x, 1.75, z, frameMat);
    // glass panes (with a small speaking window cut-out in the front one)
    const gp = (w, h, x, y, z, ry) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), glassM); m.position.set(x, y, z); m.rotation.y = ry; bg.add(m); };
    gp(0.9, 1.3, 0.6, 1.75, -0.62, Math.PI / 2); gp(0.35, 1.3, 0.6, 1.75, 0.93, Math.PI / 2); gp(0.9, 0.95, 0.6, 1.93, 0.3, Math.PI / 2);
    gp(1.2, 1.3, 0, 1.75, -1.1, 0); gp(1.2, 1.3, 0, 1.75, 1.1, 0);
    const sl = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 0.16), std({ map: ctex(THREE, 512, 80, (g, w, h) => { g.fillStyle = '#d6d1c3'; g.fillRect(0, 0, w, h); g.fillStyle = '#1a1a1a'; g.font = 'bold 50px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('PASSKONTROLLE', w / 2, h / 2 + 2); }), roughness: 0.6 }));
    sl.position.set(0.665, 2.3, 0.0); sl.rotation.y = Math.PI / 2; bg.add(sl);
    // back panel with a shelf of binders and a wall calendar (hides the tiles behind the booth)
    B(0.03, 2.3, 2.16, -0.58, 1.2, 0, std({ color: 0x2c2a26, roughness: 0.8 }));
    B(0.25, 0.025, 1.6, -0.45, 1.42, 0.1, std({ color: 0x3a342c }));
    { const rb = rng(zc * -13 + 5); for (let z = -0.65; z < 0.85; z += 0.065 + rb() * 0.02) { const v = 0.25 + rb() * 0.35; B(0.22, 0.26 + rb() * 0.05, 0.05, -0.46, 1.565, z, std({ color: new THREE.Color(v, v * 0.98, v * 0.92), roughness: 0.7 })).castShadow = false; } }
    const cal = new THREE.Mesh(new THREE.PlaneGeometry(0.3, 0.42), std({ map: ctex(THREE, 128, 180, (g, w, h) => { g.fillStyle = '#cfc8b6'; g.fillRect(0, 0, w, h); g.fillStyle = '#2a2a2a'; g.font = 'bold 22px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.fillText('MÄRZ 1974', w / 2, 30);
      g.font = '12px "DejaVu Sans"'; for (let i = 0; i < 31; i++) g.fillText(String(i + 1), 14 + (i % 7) * 17, 60 + Math.floor(i / 7) * 22); }) }));
    cal.position.set(-0.56, 1.95, -0.4); cal.rotation.y = Math.PI / 2; bg.add(cal);
    // inside: desk and green-shaded lamp
    B(0.55, 0.05, 2.1, 0.25, 1.0, 0, std({ color: 0x4a4640, roughness: 0.45 }));
    const lp = new THREE.Vector3(0.1, 1.55, 0.6);
    const shd = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.12, 20, 1, true), std({ color: 0x2c3a2c, side: THREE.DoubleSide, metalness: 0.3 })); shd.position.copy(lp).add(new THREE.Vector3(0, 0.06, 0)); bg.add(shd);
    const bb = new THREE.Mesh(new THREE.SphereGeometry(0.035, 10, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(3, 2.2, 1.3) })); bb.position.copy(lp); bg.add(bb);
    const hl = glow(THREE, AMBER, 0.6, 0.8); hl.position.copy(lp); bg.add(hl);
    const pl = new THREE.PointLight(AMBER, 2.2, 4, 1.8); pl.position.copy(lp).add(new THREE.Vector3(0, -0.1, 0)); bg.add(pl);
  }
  // ---- ceiling lamps in wire cages
  const cageM = std({ color: 0x222220, metalness: 0.6, roughness: 0.5 });
  const lamps = [];
  for (const z of [-1.0, -6.4, -11.6]) {
    const p = new THREE.Vector3(0.2, CH - 0.35, z);
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(2.5, 1.8, 1.0) })); b.position.copy(p); scene.add(b);
    const cage = new THREE.Mesh(new THREE.SphereGeometry(0.11, 8, 6), new THREE.MeshBasicMaterial({ color: 0x1a1a18, wireframe: true })); cage.position.copy(p); scene.add(cage);
    const base = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.05, 16), cageM); base.position.set(p.x, CH - 0.2, z); scene.add(base);
    const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.01, 0.01, 0.2), cageM); rod.position.set(p.x, CH - 0.1, z); scene.add(rod);
    const h = glow(THREE, AMBER, 1.0, 0.7); h.position.copy(p); scene.add(h);
    const pl = new THREE.PointLight(AMBER, 3.2, 7, 1.6); pl.position.copy(p).add(new THREE.Vector3(0, -0.15, 0)); scene.add(pl);
    lamps.push({ b, h, pl, z });
  }
  // ---- alcove in the right wall (where the officer waits), with a closed service door
  const alZ = -7.4;
  const alDark = new THREE.Mesh(new THREE.BoxGeometry(0.6, 2.4, 1.2), std({ color: 0x101010, side: THREE.BackSide })); alDark.position.set(CW + 0.3, 1.2, alZ); scene.add(alDark);
  const alCover = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 2.4), std({ color: 0x050505 })); alCover.position.set(CW - 0.002, 1.2, alZ); alCover.rotation.y = -Math.PI / 2; alCover.visible = false; scene.add(alCover);
  // hide the tile behind the alcove opening: punch by placing a dark box in front
  const jamb = std({ color: 0x2e2e2c, roughness: 0.6 });
  for (const dz of [-0.62, 0.62]) { const j = new THREE.Mesh(new THREE.BoxGeometry(0.2, 2.45, 0.08), jamb); j.position.set(CW - 0.05, 1.22, alZ + dz); j.castShadow = true; scene.add(j); }
  const lint = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.08, 1.32), jamb); lint.position.set(CW - 0.05, 2.45, alZ); scene.add(lint);
  const alcoveBack = new THREE.Mesh(new THREE.PlaneGeometry(1.16, 2.4), std({ color: 0x0c0c0b, roughness: 0.9 })); alcoveBack.position.set(CW - 0.01, 1.2, alZ); alcoveBack.rotation.y = -Math.PI / 2; scene.add(alcoveBack);
  // radiator and a bench on the right wall
  const rad = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.6, 1.2), std({ color: 0x6a6a64, metalness: 0.4, roughness: 0.5 })); rad.position.set(CW - 0.1, 0.45, -3.2); rad.castShadow = true; scene.add(rad);
  for (let k = 0; k < 12; k++) { const fin = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.58, 0.02), std({ color: 0x55554f, metalness: 0.4 })); fin.position.set(CW - 0.1, 0.45, -3.75 + k * 0.1); scene.add(fin); }
  const ash = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.7, 16), std({ color: 0x3a3a38, metalness: 0.5, roughness: 0.4 })); ash.position.set(CW - 0.3, 0.35, -12.6); ash.castShadow = true; scene.add(ash);
  // ---- poster frames on the tiled wall
  const posterTex = ctex(THREE, 256, 360, (g, w, h) => { g.fillStyle = '#c9c2b0'; g.fillRect(0, 0, w, h); g.fillStyle = '#222'; g.font = 'bold 30px "DejaVu Sans Condensed"'; g.textAlign = 'center';
    g.fillText('ZOLL-', w / 2, 60); g.fillText('ERKLÄRUNG', w / 2, 96); g.font = '15px "DejaVu Sans"'; for (let i = 0; i < 12; i++) g.fillRect(30, 130 + i * 16, 150 + (i * 37) % 50, 4); });
  const poster = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.7), std({ map: posterTex, roughness: 0.8 })); poster.position.set(CW - 0.01, 1.5, -10.0); poster.rotation.y = -Math.PI / 2; scene.add(poster);
  scene.add(new THREE.HemisphereLight(0x8a90a0, 0x0a0907, 0.05));

  // ---- people
  const man = makeMan(THREE, { coatMat, skinMat, hairMat, trouserMat, shoeMat });
  scene.add(man.root);
  const bomb = makeBomb(THREE, std, clockFace); scene.add(bomb.group);
  const darkM = std({ color: 0x0a0a0a, roughness: 0.9 });
  const officer = makeMan(THREE, { coatMat: darkM, skinMat: std({ color: 0x5a4a40 }), hairMat: darkM, trouserMat: darkM, shoeMat: darkM, hat: true, hatMat: darkM });
  scene.add(officer.root);
  const pistol = new THREE.Group();
  { const pm = std({ color: 0x111111, metalness: 0.7, roughness: 0.4 });
    const a = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.035, 0.17), pm); a.position.z = 0.06; pistol.add(a);
    const gr = new THREE.Mesh(new THREE.BoxGeometry(0.028, 0.09, 0.04), pm); gr.position.set(0, -0.045, 0.0); gr.rotation.x = 0.25; pistol.add(gr); }
  scene.add(pistol);
  const muzzle = new THREE.PointLight(0xffd29a, 0, 16, 1.4); scene.add(muzzle);
  const muzzleGlow = glow(THREE, 0xffd8a8, 0.9, 1); muzzleGlow.material.opacity = 0; scene.add(muzzleGlow);
  // passport + stamp
  const passTex = ctex(THREE, 512, 360, (g, w, h) => {
    g.fillStyle = '#d8d2c0'; g.fillRect(0, 0, w, h);
    g.strokeStyle = 'rgba(120,110,95,0.35)'; g.lineWidth = 1; for (let y = 6; y < h; y += 7) { g.beginPath(); g.moveTo(0, y); g.bezierCurveTo(w * 0.3, y + 3, w * 0.6, y - 3, w, y); g.stroke(); }
    g.fillStyle = '#5b554b'; g.fillRect(28, 60, 120, 150);
    g.fillStyle = '#2b2824'; g.beginPath(); g.ellipse(88, 120, 34, 42, 0, 0, 7); g.fill(); g.fillRect(40, 165, 96, 45);
    g.fillStyle = '#3a352e'; g.font = '16px "DejaVu Sans"'; for (let i = 0; i < 7; i++) g.fillRect(170, 70 + i * 22, 60 + (i * 31) % 60, 3);
    g.font = 'bold 18px "DejaVu Serif"'; g.fillText('PASZPORT', 30, 40);
    g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(w / 2 - 2, 0, 4, h);
    g.fillStyle = 'rgba(60,55,48,0.5)'; for (let i = 0; i < 9; i++) g.fillRect(w / 2 + 30, 40 + i * 30, 180 - (i * 23) % 70, 2);
  });
  const passport = new THREE.Group(); scene.add(passport);
  { const pg = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.006, 0.175), [std({ color: 0x2a2f2a }), std({ color: 0x2a2f2a }), std({ map: passTex, roughness: 0.85 }), std({ color: 0x2a2f2a }), std({ color: 0x2a2f2a }), std({ color: 0x2a2f2a })]);
    pg.receiveShadow = true; passport.add(pg);
    const cover = new THREE.Mesh(new THREE.BoxGeometry(0.262, 0.004, 0.186), std({ color: 0x1f2a22, roughness: 0.6 })); cover.position.y = -0.004; passport.add(cover); }
  const stampTex = ctex(THREE, 256, 160, (g, w, h) => {
    g.clearRect(0, 0, w, h); const ink = 'rgba(20,24,48,0.88)'; g.strokeStyle = ink; g.fillStyle = ink; g.lineWidth = 7; g.strokeRect(10, 10, w - 20, h - 20); g.lineWidth = 3; g.strokeRect(22, 22, w - 44, h - 44);
    g.textAlign = 'center'; g.font = 'bold 22px "DejaVu Sans Condensed"'; g.fillText('DDR · AUSREISE', w / 2, 55); g.font = 'bold 17px "DejaVu Sans Condensed"'; g.fillText('GÜST BHF. FRIEDRICHSTR.', w / 2, 85);
    g.font = 'bold 26px "DejaVu Sans Mono"'; g.fillText('29.03.74', w / 2, 124);
    // ink unevenness
    const rr = rng(9); g.globalCompositeOperation = 'destination-out'; for (let i = 0; i < 500; i++) { g.fillStyle = `rgba(0,0,0,${rr() * 0.6})`; g.fillRect(rr() * w, rr() * h, 2 + rr() * 6, 2 + rr() * 3); }
  });
  stampTex.wrapS = stampTex.wrapT = THREE.ClampToEdgeWrapping;
  const imprint = new THREE.Mesh(new THREE.PlaneGeometry(0.09, 0.056), new THREE.MeshStandardMaterial({ map: stampTex, transparent: true, opacity: 0, roughness: 0.8, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 }));
  imprint.rotation.x = -Math.PI / 2; scene.add(imprint);
  const stamp = new THREE.Group(); scene.add(stamp);
  { const woodM = std({ color: 0x4e4438, roughness: 0.5 });
    const base = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.022, 0.065), woodM); base.position.y = 0.018; base.castShadow = true; stamp.add(base);
    const rub = new THREE.Mesh(new THREE.BoxGeometry(0.094, 0.008, 0.06), std({ color: 0x151826 })); rub.position.y = 0.004; stamp.add(rub);
    const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.022, 0.06, 14), woodM); neck.position.y = 0.06; neck.castShadow = true; stamp.add(neck);
    const knob = new THREE.Mesh(new THREE.SphereGeometry(0.03, 16, 12), woodM); knob.position.y = 0.1; knob.scale.set(1, 0.85, 1); knob.castShadow = true; stamp.add(knob);
    // the official's fist around the handle (+x side = towards the passage) and his uniform sleeve
    const fist = new THREE.Group(); stamp.add(fist); stamp.userData.fist = fist;
    const F = (geo, mat, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; fist.add(m); return m; };
    F(new RoundedBoxGeometry(0.07, 0.07, 0.092, 3, 0.022), skinMat, -0.012, 0.1, 0).rotation.z = 0.25;            // palm and back of the hand round the handle
    for (let i = 0; i < 4; i++) {                                                                                    // curled fingers, seen from the front
      const f = F(new RoundedBoxGeometry(0.034, 0.02, 0.026, 2, 0.009), skinMat, 0.03, 0.118 - i * 0.0005, -0.036 + i * 0.024);
      f.rotation.set(0, 0, -0.5); f.scale.set(1, 1 + (i === 1 || i === 2 ? 0.1 : 0), 1);
      const tip = F(new RoundedBoxGeometry(0.022, 0.03, 0.023, 2, 0.009), skinMat, 0.04, 0.094, -0.036 + i * 0.024); tip.rotation.z = 0.15;
    }
    const th = F(new THREE.CapsuleGeometry(0.012, 0.045, 4, 10), skinMat, 0.012, 0.13, 0.05); th.rotation.set(-0.4, 0, 1.0);
    const sleeveM = std({ color: 0x55574f, roughness: 0.9 });
    const sl = F(new THREE.CylinderGeometry(0.05, 0.058, 1, 16), sleeveM, 0, 0, 0); seg(THREE, sl, new THREE.Vector3(-0.045, 0.14, 0), new THREE.Vector3(-0.55, 0.42, 0.06));
    const cuff = F(new THREE.CylinderGeometry(0.052, 0.052, 0.025, 16), std({ color: 0x3a3c36 }), 0, 0, 0); seg(THREE, cuff, new THREE.Vector3(-0.06, 0.148, 0.001), new THREE.Vector3(-0.085, 0.163, 0.002)); cuff.scale.y = 0.03; }
  const pad = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.018, 0.08), std({ color: 0x2a2a2a, metalness: 0.5, roughness: 0.4 })); scene.add(pad);

  // dust in the door light
  const dust = makeDust(THREE, 900, [-CW, CW], [0.1, CH - 0.2], [DOOR_Z, -1], 0.018, 33); scene.add(dust.pts);

  const post = makeComposer(THREE, renderer, scene, camera, W, H, {
    bloom: 0.35, bloomRadius: 0.3, bloomThreshold: 0.9, exposure: 1.0,
    dof: shot === 'agree' ? { focus: 0.6, aperture: 0.03, maxblur: 0.012 } : shot === 'steps' ? { focus: 2.5, aperture: 0.0012, maxblur: 0.005 } : null,
  });
  Object.assign(ctx, { man, bomb, officer, pistol, muzzle, muzzleGlow, passport, imprint, stamp, pad, sun, westM, doorGlow, rays, lamps, dust, booths }, post);
  return ctx;
}

function makeDust(THREE, N, xr, yr, zr, size, seed) {
  const r = rng(seed), pos = new Float32Array(N * 3), seeds = new Float32Array(N);
  for (let i = 0; i < N; i++) { pos[i * 3] = lerp(xr[0], xr[1], r()); pos[i * 3 + 1] = lerp(yr[0], yr[1], r()); pos[i * 3 + 2] = lerp(zr[0], zr[1], r()); seeds[i] = r() * 100; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const c = document.createElement('canvas'); c.width = c.height = 32; const x = c.getContext('2d'); const gr = x.createRadialGradient(16, 16, 0, 16, 16, 16); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0, 0, 32, 32);
  const pts = new THREE.Points(g, new THREE.PointsMaterial({ size, map: new THREE.CanvasTexture(c), color: 0xffe2c0, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false }));
  return { pts, base: pos.slice(), seeds };
}
function driftDust(d, t) {
  const p = d.pts.geometry.attributes.position;
  for (let i = 0; i < p.count; i++) { const s = d.seeds[i];
    p.array[i * 3] = d.base[i * 3] + Math.sin(t * 0.13 + s) * 0.12;
    p.array[i * 3 + 1] = d.base[i * 3 + 1] + Math.sin(t * 0.09 + s * 1.7) * 0.1;
    p.array[i * 3 + 2] = d.base[i * 3 + 2] + Math.cos(t * 0.11 + s) * 0.12; }
  p.needsUpdate = true;
}
// light from the West: steady with slight flicker (strong flicker in 'steps')
function doorLight(ctx, v) {
  ctx.sun.intensity = 22 * v; ctx.westM.color.setRGB(1.5 * v, 1.42 * v, 1.3 * v); ctx.doorGlow.material.opacity = 0.5 * v; ctx.rays.material.uniforms.opacity.value = 0.035 * v;
}
function flick(t, amt) {
  const k = Math.floor(t * 24);
  const n = Math.abs(Math.sin(k * 91.17) * 43758.5453) % 1;
  const dip = n > 0.86 ? (n - 0.86) / 0.14 : 0;
  return 1 - amt * dip - 0.04 * Math.sin(t * 17) * Math.sin(t * 5.3);
}

export function update(ctx, t) {
  update2(ctx, t);
  for (const n of (window.HIDE || '').split(':')) if (n && ctx[n]) { if (ctx[n].isObject3D) ctx[n].visible = false; else if (ctx[n].pts) ctx[n].pts.visible = false; else if (ctx[n].group) ctx[n].group.visible = false; else if (ctx[n].root) ctx[n].root.visible = false; }
  if (window.DBGCAM) { const c = window.DBGCAM; ctx.camera.position.set(c[0], c[1], c[2]); ctx.camera.lookAt(c[3], c[4], c[5]); }
}
function update2(ctx, t) {
  const { THREE, camera, shot } = ctx;
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  if (ctx.dust) driftDust(ctx.dust, t);

  if (shot === 'bomb') {
    const { bomb, man, deskY } = ctx;
    // clock ticks once per second
    bomb.hSec.rotation.z = -Math.floor(t) / 60 * Math.PI * 2 - 1.1 - Math.min(1, (t % 1) * 12) * 0 ; bomb.hSec.rotation.z = -(Math.floor(t) + Math.min(1, (t % 1) * 10)) / 60 * Math.PI * 2 - 1.1;
    bomb.hMin.rotation.z = -0.9 - t * 0.002;
    // hand on the handle (in the man's root space); slight nervous tension
    const bp = bomb.group.position;
    const handle = V(bp.x, deskY + bomb.H + 0.045, bp.z).sub(man.root.position);
    const breathe = Math.sin(t * 1.6) * 0.008;
    man.pose({
      hipY: 0.95, lean: 0.12 + breathe, headPitch: 0.42, headYaw: -0.05,
      handR: handle.clone().add(V(0.0, 0.0, 0)), palmR: V(0, 0, -1), elbowPoleR: V(-1, 0.2, -0.6),
      handL: V(0.24, 0.66, 0.15), palmL: V(-1, 0, 0), elbowPoleL: V(1, 0, -1),
      footL: V(0.12, 0, 0.02), footR: V(-0.12, 0, -0.04),
    });
    // camera: ECU on hand + clock, slow pull back and rise to reveal the man
    const k = smooth(Math.min(1, t / 8.2));
    const tgt = V(lerp(bp.x + 0.0, 0.12, k), lerp(deskY + 0.24, 1.18, k), lerp(bp.z + 0.05, -0.3, k));
    camera.position.set(lerp(bp.x + 0.16, 0.5, k), lerp(deskY + 0.3, 1.3, k), lerp(bp.z + 0.62, 2.45, k));
    camera.lookAt(tgt);
    camera.fov = lerp(30, 36, k); camera.updateProjectionMatrix();
    if (ctx.bokeh) { ctx.bokeh.uniforms.focus.value = camera.position.distanceTo(lerp(0, 1, k) > 0.5 ? V(0.18, 1.2, -0.55) : V(bp.x, deskY + 0.25, bp.z + 0.06)) ; ctx.bokeh.uniforms.focus.value = lerp(camera.position.distanceTo(V(bp.x, deskY + 0.25, bp.z + 0.1)), camera.position.distanceTo(V(0.18, 1.3, -0.55)), smooth((t - 3) / 4)); ctx.bokeh.uniforms.aperture.value = lerp(0.006, 0.002, k); }
    ctx.lamp.intensity = 1.9 * (0.97 + 0.03 * Math.sin(t * 7.3));
    return;
  }

  const { man, bomb, officer, pistol, muzzle, muzzleGlow } = ctx;
  doorLight(ctx, flick(t, shot === 'steps' ? 0.55 : 0.12));
  ctx.lamps.forEach((l, i) => { const v = 0.93 + 0.07 * Math.sin(t * 9 + i * 3) * Math.sin(t * 2.7 + i); l.pl.intensity = 3.2 * v; l.h.material.opacity = 0.7 * v; });
  muzzle.intensity = 0; muzzleGlow.material.opacity = 0; if (ctx.finish) ctx.finish.uniforms.flash.value = 0;
  ctx.passport.visible = ctx.stamp.visible = ctx.imprint.visible = ctx.pad.visible = false;
  officer.root.visible = true; pistol.visible = true; man.root.visible = true;

  // the man's walk + fall (shared by 'shot'; 'steps' shows only the briefcase where it ended)
  const Z0 = -7.6, SPEED = 1.25, tf = T_SHOT + 0.05;
  const walkT = Math.min(t, tf);
  const z = Z0 - SPEED * walkT;
  man.root.position.set(0.05, 0, z); man.root.rotation.set(0, Math.PI, 0);
  const pose = gait(THREE, SPEED * walkT, { carry: true });
  const handPos = new THREE.Vector3();
  if (t < tf) {
    man.pose(pose);
  } else {
    const d = t - tf;
    const a = smooth(d / 0.32);                 // knees give
    const fall = Math.min(1, Math.max(0, (d - 0.18) / 0.55)); const fe = fall * fall;  // topple forward, accelerating
    man.pose({ ...pose, hipY: lerp(pose.hipY, 0.62, a), lean: lerp(0.05, 0.5, a), handR: V(-0.24, lerp(0.63, 0.5, a), 0.12 * a), handL: V(0.26, lerp(0.62, 0.45, a), 0.15 * a), headPitch: -0.3 * a,
      footL: V(0.1, 0, pose.footL.z), footR: V(-0.1, 0, pose.footR.z) });
    man.root.rotation.x = -fe * 1.25;
    man.root.position.y = 0;
  }
  // briefcase: carried in the right hand, released 0.12 s after the shot, drops and tips over
  man.root.updateMatrixWorld(true);
  const tb = shot === 'steps' ? t + 6 : t;
  const rel = tf + 0.1;
  const BW = 0.46;
  bomb.group.rotation.order = 'YXZ';
  if (tb < rel) {
    const hp = man.limbs.handR.getWorldPosition(new THREE.Vector3());
    bomb.group.position.set(hp.x - 0.02, hp.y - bomb.H - 0.08, hp.z); bomb.group.rotation.set(0, Math.PI / 2 + 0.05, 0.02 * Math.sin(t * 5));
    handPos.copy(hp);
  } else {
    const hp0 = (() => { const p0 = gait(THREE, SPEED * tf, { carry: true }); return V(0.05 + 0.26, 0.63 - bomb.H - 0.08, Z0 - SPEED * tf - 0.02); })();
    const d = tb - rel;
    const yDrop = Math.max(0, hp0.y - 0.5 * 9.81 * d * d);
    const land = Math.sqrt(2 * hp0.y / 9.81);
    const slide = Math.min(d, land) * 0.9 + (d > land ? 0.25 * (1 - Math.exp(-(d - land) * 6)) : 0);
    const tip = d > land ? smooth((d - land) / 0.35) : 0;
    bomb.group.position.set(hp0.x + 0.05 * tip, yDrop, hp0.z - slide);
    bomb.group.rotation.set(-tip * Math.PI / 2, Math.PI / 2 + 0.05 + 0.35 * tip, 0);
    // falling flat onto its back: lift so the box rests on its broad side, clock facing up
    bomb.group.position.y = yDrop + tip * bomb.D / 2;
  }

  if (shot === 'shot' || shot === 'steps') {
    // the officer steps out of the alcove and raises his arm
    const step = smooth((t - 0.5) / 0.7), raise = smooth((t - 0.95) / 0.5);
    officer.root.position.set(lerp(2.1, 1.3, step), 0, -7.2 + 0.05 * step); officer.root.rotation.set(0, Math.PI + lerp(0.1, 0.47, step), 0);
    const recoil = t > T_SHOT ? Math.exp(-(t - T_SHOT) * 10) * 0.06 : 0;
    officer.pose({ hipY: 0.94, lean: 0.02, headPitch: 0.05, footL: V(0.12, 0, 0.12 * step), footR: V(-0.12, 0, -0.15 * step),
      handL: V(lerp(0.25, 0.08, raise), lerp(0.6, 1.36 + recoil, raise), lerp(0.05, 0.58 - recoil, raise)), palmL: V(-1, 0, 0), elbowPoleL: V(1, -0.6, 0),
      handR: V(-0.25, 0.62, 0.02), palmR: V(1, 0, 0) });
    officer.root.updateMatrixWorld(true);
    const hp = officer.limbs.handL.getWorldPosition(new THREE.Vector3());
    pistol.position.copy(hp); pistol.lookAt(man.root.position.clone().add(V(0, 1.2, 0))); pistol.rotateX(0); pistol.translateY(0.04); pistol.translateZ(0.02);
    pistol.visible = raise > 0.3;
    // muzzle flash: exactly 2 frames at 30 fps
    if (t >= T_SHOT - 1e-4 && t < T_SHOT + 2 / 30 - 1e-4) {
      const mp = pistol.localToWorld(V(0, 0, 0.2));
      muzzle.position.copy(mp); muzzle.intensity = t < T_SHOT + 1 / 30 ? 9 : 4;
      muzzleGlow.position.copy(mp); muzzleGlow.material.opacity = 1; muzzleGlow.scale.setScalar(t < T_SHOT + 1 / 30 ? 1.1 : 0.6);
      if (ctx.finish) ctx.finish.uniforms.flash.value = t < T_SHOT + 1 / 30 ? 0.05 : 0.015;
    }
  }

  if (shot === 'shot') {
    const k = t / 6;
    camera.position.set(lerp(0.42, 0.34, k), lerp(1.5, 1.45, k), lerp(-2.9, -3.7, k));
    camera.lookAt(lerp(0.12, 0.16, k), 1.25, DOOR_Z);
    camera.fov = 40; camera.updateProjectionMatrix();
    if (ctx.bokeh) ctx.bokeh.uniforms.focus.value = camera.position.distanceTo(man.root.position);
    // after the fall the camera breathes; a tiny jolt at the shot
    if (t > T_SHOT && t < T_SHOT + 0.25) { const j = Math.exp(-(t - T_SHOT) * 18) * 0.012; camera.position.x += j * Math.sin(t * 90); camera.position.y += j * Math.cos(t * 77); }
  } else if (shot === 'steps') {
    // empty corridor: only the briefcase lies where it fell
    man.root.visible = false; officer.root.visible = false; pistol.visible = false;
    const bp = bomb.group.position;
    const k = t / 5;
    camera.position.set(lerp(0.02, 0.06, k), lerp(0.42, 0.4, k), bp.z + lerp(1.75, 1.45, k));
    camera.lookAt(lerp(0.14, 0.15, k), lerp(0.62, 0.64, k), DOOR_Z);
    camera.fov = 42; camera.updateProjectionMatrix();
    if (ctx.bokeh) ctx.bokeh.uniforms.focus.value = camera.position.distanceTo(bp) + 0.1;
  } else if (shot === 'agree') {
    man.root.visible = false; officer.root.visible = false; pistol.visible = false; bomb.group.visible = false;
    ctx.passport.visible = ctx.stamp.visible = ctx.imprint.visible = ctx.pad.visible = true;
    const bg = ctx.booths[0];                              // booth at x=-1.15, z=-2
    const bx = bg.position.x, bz = bg.position.z, deskY = 1.025;
    const pp = V(bx + 0.33, deskY + 0.006, bz + 0.2);
    ctx.passport.position.copy(pp); ctx.passport.rotation.set(0, Math.PI / 2 - 0.1, 0);
    ctx.pad.position.set(bx + 0.24, deskY + 0.009, bz + 0.42);
    // stamp path: from the pad, hover, slam down, hold, lift
    const tDown = 0.72, tUp = 1.08;
    let sp, tilt = 0;
    const hit = V(pp.x + 0.0, deskY + 0.009, pp.z - 0.045);
    if (t < tDown - 0.16) { const a = smooth((t + 0.2) / (tDown + 0.04)); sp = V(lerp(bx + 0.24, hit.x, a), lerp(deskY + 0.1, deskY + 0.2, a) + 0.003 * Math.sin(t * 23), lerp(bz + 0.42, hit.z, a)); tilt = 0.25 * (1 - a); }
    else if (t < tDown) { const a = (t - (tDown - 0.16)) / 0.16; const y0 = deskY + 0.2; sp = V(hit.x, lerp(y0, hit.y, a * a), hit.z); }
    else if (t < tUp) { sp = hit.clone(); sp.y -= 0.002 * Math.exp(-(t - tDown) * 30); }
    else { const a = smooth((t - tUp) / 0.55); sp = V(lerp(hit.x, hit.x - 0.12, a), lerp(hit.y, deskY + 0.24, a), lerp(hit.z, hit.z + 0.12, a)); tilt = 0.15 * a; }
    ctx.stamp.position.copy(sp); ctx.stamp.rotation.set(0, 0, tilt);
    ctx.imprint.position.set(hit.x, deskY + 0.0105, hit.z); ctx.imprint.rotation.set(-Math.PI / 2, 0, Math.PI / 2 - 0.08);
    ctx.imprint.material.opacity = t >= tDown ? 0.92 : 0;
    const k = t / 3;
    const shake = t > tDown && t < tDown + 0.25 ? Math.exp(-(t - tDown) * 22) * 0.006 * Math.cos((t - tDown) * 90) : 0;
    camera.position.set(hit.x + lerp(0.52, 0.46, k), deskY + lerp(0.3, 0.27, k) + shake, hit.z + lerp(0.2, 0.15, k));
    camera.lookAt(hit.x - 0.04, deskY + 0.08, hit.z + 0.01);
    camera.fov = 36; camera.updateProjectionMatrix();
    if (ctx.bokeh) ctx.bokeh.uniforms.focus.value = camera.position.distanceTo(hit);
  }
}

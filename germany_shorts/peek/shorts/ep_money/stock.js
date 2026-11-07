// One stock, peeked inside: a block of share cubes (1 cube = 100 million shares) and its price tag.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export const CUBE = 1, CGAP = 0.1, CP = CUBE + CGAP;

function edgeCanvas() {
  const S = 256;
  const c = document.createElement('canvas'); c.width = c.height = S;
  const g = c.getContext('2d');
  g.fillStyle = '#000'; g.fillRect(0, 0, S, S);
  // soft inner glow plus a crisp frame along the face edge
  const r = g.createRadialGradient(S / 2, S / 2, S * 0.2, S / 2, S / 2, S * 0.72);
  r.addColorStop(0, 'rgba(255,255,255,0.0)'); r.addColorStop(1, 'rgba(255,255,255,0.10)');
  g.fillStyle = r; g.fillRect(0, 0, S, S);
  g.strokeStyle = '#fff'; g.lineWidth = 7;
  g.beginPath(); g.roundRect(14, 14, S - 28, S - 28, 22); g.stroke();
  g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = 16;
  g.beginPath(); g.roundRect(14, 14, S - 28, S - 28, 22); g.stroke();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return t;
}

export function buildBlock({ nx = 9, ny = 9, nz = 3, color = 0x17694a, glow = 0x56f5a2 } = {}) {
  const geo = new RoundedBoxGeometry(CUBE, CUBE, CUBE, 3, 0.12);
  const edge = edgeCanvas();
  const mat = new THREE.MeshPhysicalMaterial({ color, roughness: 0.22, metalness: 0.0, clearcoat: 1, clearcoatRoughness: 0.08, emissive: glow, emissiveMap: edge, emissiveIntensity: 0.4, envMapIntensity: 1.6 });
  const n = nx * ny * nz;
  const mesh = new THREE.InstancedMesh(geo, mat, n);
  mesh.castShadow = true; mesh.receiveShadow = true; mesh.frustumCulled = false;
  const gc = new THREE.Color(glow);
  mesh.userData.bloomMat = new THREE.MeshBasicMaterial({ map: edge, color: new THREE.Color(gc.r * 0.9, gc.g * 0.9, gc.b * 0.9) });
  const W = nx * CP - CGAP, H = ny * CP - CGAP, D = nz * CP - CGAP;
  const cells = [];
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) for (let k = 0; k < nz; k++)
    cells.push({ i, j, k, p: new THREE.Vector3(-W / 2 + CUBE / 2 + i * CP, CUBE / 2 + j * CP, -D / 2 + CUBE / 2 + k * CP) });
  // the few cubes that change hands get their own gold mesh
  const hotMat = new THREE.MeshPhysicalMaterial({ color: 0x8a5a00, roughness: 0.25, clearcoat: 1, clearcoatRoughness: 0.1, emissive: 0xffc23a, emissiveMap: edge, emissiveIntensity: 1.0 });
  const hot = new THREE.InstancedMesh(geo, hotMat, 8);
  hot.castShadow = true; hot.frustumCulled = false; hot.count = 0;
  hot.userData.bloomMat = new THREE.MeshBasicMaterial({ map: edge, color: new THREE.Color(1.6, 1.0, 0.25) });
  const root = new THREE.Group();
  root.add(mesh, hot);
  const B = { root, mesh, hot, cells, nx, ny, nz, W, H, D, mat };
  setBlock(B, {});
  return B;
}

const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _s = new THREE.Vector3(), _p = new THREE.Vector3();
// scaleOf(cell) -> cube scale (the re-pricing wave); hotCells: [{cell, offset: Vector3}] drawn gold
export function setBlock(B, { scaleOf = null, hotCells = [], lift = 0 }) {
  const hotSet = new Set(hotCells.map(h => h.cell));
  B.cells.forEach((c, n) => {
    const s = hotSet.has(c) ? 1e-5 : (scaleOf ? scaleOf(c) : 1);
    _p.copy(c.p); _p.y = c.p.y * (scaleOf ? (s > 1e-4 ? s : 1) : 1) + lift;
    _s.setScalar(Math.max(1e-5, s));
    _m.compose(_p, _q.identity(), _s);
    B.mesh.setMatrixAt(n, _m);
  });
  B.mesh.instanceMatrix.needsUpdate = true;
  hotCells.forEach((h, n) => {
    _p.copy(h.cell.p).add(h.offset || new THREE.Vector3());
    _s.setScalar(h.scale ?? 1);
    _m.compose(_p, _q.identity(), _s);
    B.hot.setMatrixAt(n, _m);
  });
  B.hot.count = hotCells.length;
  B.hot.instanceMatrix.needsUpdate = true;
}

// ---------------------------------------------------------------------------
// The price tag: a white card on a string, printed with the share price.
export function buildTag({ w = 4.4, h = 2.5 } = {}) {
  const s = new THREE.Shape();
  const r = 0.28, cut = 0.9;            // rounded right end, angled left end with the hole
  s.moveTo(-w / 2 + cut, h / 2);
  s.lineTo(w / 2 - r, h / 2); s.quadraticCurveTo(w / 2, h / 2, w / 2, h / 2 - r);
  s.lineTo(w / 2, -h / 2 + r); s.quadraticCurveTo(w / 2, -h / 2, w / 2 - r, -h / 2);
  s.lineTo(-w / 2 + cut, -h / 2);
  s.lineTo(-w / 2, -h / 2 + cut * 0.75); s.lineTo(-w / 2, h / 2 - cut * 0.75);
  s.lineTo(-w / 2 + cut, h / 2);
  const hole = new THREE.Path(); hole.absarc(-w / 2 + 0.55, 0, 0.17, 0, Math.PI * 2, true);
  s.holes.push(hole);
  const geo = new THREE.ExtrudeGeometry(s, { depth: 0.05, bevelEnabled: true, bevelThickness: 0.012, bevelSize: 0.012, bevelSegments: 2, curveSegments: 24 });
  geo.translate(0, 0, -0.025);
  const c = document.createElement('canvas'); c.width = 1100; c.height = 625;
  const map = new THREE.CanvasTexture(c); map.colorSpace = THREE.SRGBColorSpace; map.anisotropy = 8;
  map.repeat.set(1 / w, 1 / h); map.offset.set(0.5, 0.5);
  const face = new THREE.MeshStandardMaterial({ map, roughness: 0.75 });
  const side = new THREE.MeshStandardMaterial({ color: 0xe8e4da, roughness: 0.8 });
  const card = new THREE.Mesh(geo, [face, side]);
  card.castShadow = true;
  const root = new THREE.Group();
  root.add(card);
  // string from the hole up to the attachment point
  const strMat = new THREE.MeshStandardMaterial({ color: 0xd8d2c4, roughness: 0.9 });
  const str = new THREE.Mesh(new THREE.BufferGeometry(), strMat);
  const T = { root, card, c, map, key: '', w, h, hole: new THREE.Vector3(-w / 2 + 0.55, 0, 0), str };
  return T;
}

// old: crossed-out price (or null); now: current price; k: 0..1 strike progress
export function paintTag(T, { now = '$200', old = null, strike = 1, nowColor = '#111' }) {
  const key = [now, old, strike.toFixed(2), nowColor].join('|');
  if (key === T.key) return;
  T.key = key;
  const g = T.c.getContext('2d'), W = T.c.width, H = T.c.height;
  g.fillStyle = '#f4f1ea'; g.fillRect(0, 0, W, H);
  // paper grain
  for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(0,0,0,${0.02 + 0.03 * ((i * 7919) % 13) / 13})`; g.fillRect((i * 6151) % W, (i * 3571) % H, 2, 1); }
  // canvas y is flipped against the shape's v (v up); draw normally and flip the texture via flipY default
  const left = 0.26 * W;
  g.textAlign = 'center'; g.textBaseline = 'middle';
  if (old) {
    g.fillStyle = '#8a8a8a'; g.font = '150px YTS';
    const ox = left + (W - left) / 2, oy = H * 0.27;
    g.fillText(old, ox, oy);
    const tw = g.measureText(old).width;
    g.strokeStyle = '#e0262b'; g.lineWidth = 16; g.lineCap = 'round';
    g.beginPath(); g.moveTo(ox - tw / 2 - 10, oy + 6); g.lineTo(ox - tw / 2 - 10 + (tw + 20) * strike, oy + 6 - 18 * strike); g.stroke();
    g.fillStyle = nowColor; g.font = '250px YTS';
    g.fillText(now, ox, H * 0.66);
  } else {
    g.fillStyle = nowColor; g.font = '270px YTS';
    g.fillText(now, left + (W - left) / 2, H * 0.53);
  }
  T.map.needsUpdate = true;
}

// hang the tag: attach point (world, in the tag root's parent space) -> string to the hole
export function hangTag(T, attach, pos, rotY = 0, swing = 0) {
  T.root.position.copy(pos);
  T.root.rotation.set(0, rotY, swing);
  T.root.updateMatrixWorld(true);
  const holeW = T.hole.clone().applyMatrix4(T.root.matrixWorld);
  const mid = attach.clone().lerp(holeW, 0.5); mid.y -= 0.25;
  const curve = new THREE.QuadraticBezierCurve3(attach.clone(), mid, holeW);
  T.str.geometry.dispose();
  T.str.geometry = new THREE.TubeGeometry(curve, 24, 0.025, 6, false);
}

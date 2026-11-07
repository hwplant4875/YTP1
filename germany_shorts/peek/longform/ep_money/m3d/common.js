// Shared pieces for the 3D scenes (beats 3-10): a bright paper studio, $100-bundle stacks built from the
// opening's own bill art, logo plates, price tags, candlesticks, keyframed perspective cameras.
import * as THREE from 'three';
import { money, COL } from '../js/objects.js';
import { clamp, smoother } from '../js/iso.js';

export const W = 1920, H = 1080;
export const BT = 0.010922, BW = 0.156, BD = 0.0663;     // one $10,000 bundle (m)
export const RED = '#FF6B57', GREEN = '#3FCB9B';
export const RED3 = 0xE2604C, GREEN3 = 0x2FAE84;

export function tex(canvas, rep = [1, 1]) {
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]);
  return t;
}
export async function img(src) { const i = new Image(); i.src = src; await i.decode(); return i; }
export function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }

// a paper studio: warm sky light, one soft sun with real shadows, matte floor, fog into the paper colour
export function studio(s, o = {}) {
  s.background = new THREE.Color(o.bg ?? COL.paper);
  s.fog = new THREE.Fog(o.bg ?? COL.paper, o.near ?? 10, o.far ?? 26);
  s.add(new THREE.HemisphereLight(0xfff8ec, 0xb9a98c, o.hemi ?? 1.25));
  const sun = new THREE.DirectionalLight(0xfff1dc, o.sun ?? 2.4);
  sun.position.set(...(o.sunPos ?? [-5, 9, 6])); sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096); sun.shadow.radius = 4; sun.shadow.bias = -0.0004;
  const e = o.shadow ?? 8;
  Object.assign(sun.shadow.camera, { left: -e, right: e, top: e, bottom: -e, near: 1, far: 40 });
  if (o.target) { sun.target.position.set(...o.target); s.add(sun.target); }
  s.add(sun);
  if (o.floor !== false) {
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(120, 120), new THREE.MeshStandardMaterial({ color: o.floorCol ?? 0xEFE5D2, roughness: 0.95 }));
    floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; s.add(floor);
  }
  return sun;
}

// money materials (cached): each bundle reads as its own brick
let MM = null;
export function moneyMats() {
  if (MM) return MM;
  const M = money();
  const seam = (src) => { const cv = canvas(src.width, src.height), g = cv.getContext('2d');
    g.drawImage(src, 0, 0); g.fillStyle = 'rgba(40,60,30,0.55)'; g.fillRect(0, src.height - 9, src.width, 9); g.fillRect(0, 0, 8, src.height); g.fillRect(src.width - 8, 0, 8, src.height);
    g.fillStyle = 'rgba(255,255,240,0.35)'; g.fillRect(0, 0, src.width, 5); return cv; };
  const topC = canvas(M.top.width, M.top.height), g = topC.getContext('2d');
  g.drawImage(M.top, 0, 0); g.strokeStyle = 'rgba(40,60,30,0.6)'; g.lineWidth = 14; g.strokeRect(0, 0, topC.width, topC.height);
  MM = { top: tex(topC), long: tex(seam(M.long)), end: tex(seam(M.end)), bill: M };
  return MM;
}
export function cashMats() {
  const m = moneyMats(), mat = (map) => new THREE.MeshStandardMaterial({ map, roughness: 0.82 });
  return [mat(m.end), mat(m.end), mat(m.top), mat(m.top), mat(m.long), mat(m.long)];
}
// a stack of bundles as one box; side UVs repeat once per bundle
export function stackGeo(h, nx = 2, nz = 1) {
  const g = new THREE.BoxGeometry(BW * nx, h, BD * nz);
  const uv = g.attributes.uv, n = h / BT;
  for (const f of [0, 1, 4, 5]) for (let k = 0; k < 4; k++) { const i = f * 4 + k; uv.setXY(i, uv.getX(i) * (f < 2 ? nz : nx), uv.getY(i) * n); }
  for (const f of [2, 3]) for (let k = 0; k < 4; k++) { const i = f * 4 + k; uv.setXY(i, uv.getX(i) * nx, uv.getY(i) * nz); }
  g.translate(0, h / 2, 0);
  return g;
}
export function tint(mats, hot) { for (const m of [].concat(mats)) m.color.setRGB(1, 1 - 0.55 * hot, 1 - 0.62 * hot); }

// a cream plate with a real logo printed on its face
export function logoPlate(logo, w, h, d = 0.06, bg = '#FBF7EE') {
  const cv = canvas(1600, Math.round(1600 * h / w)), g = cv.getContext('2d');
  g.fillStyle = bg; g.fillRect(0, 0, cv.width, cv.height);
  const lw = cv.width * 0.8, lh = lw * logo.height / logo.width, k = Math.min(1, cv.height * 0.62 / lh);
  g.drawImage(logo, (cv.width - lw * k) / 2, (cv.height - lh * k) / 2, lw * k, lh * k);
  const face = new THREE.MeshStandardMaterial({ map: tex(cv), roughness: 0.6 });
  const side = new THREE.MeshStandardMaterial({ color: 0xE9DFCB, roughness: 0.7 });
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), [side, side, side, side, face, side]);
  m.castShadow = m.receiveShadow = true;
  return m;
}
// a flat label card in the world (text drawn with Jost / YTSans), single-sided, lit
export function card(lines, o = {}) {
  const w = o.w ?? 1024, h = o.h ?? 512, cv = canvas(w, h), g = cv.getContext('2d');
  if (o.bg) { g.fillStyle = o.bg; g.fillRect(0, 0, w, h); }
  for (const L of lines) { g.font = L.font; g.fillStyle = L.color ?? COL.ink; g.textAlign = L.align ?? 'center'; g.textBaseline = 'alphabetic'; if (L.ls) g.letterSpacing = L.ls; g.fillText(L.text, L.x ?? w / 2, L.y); g.letterSpacing = '0px'; }
  const mat = new THREE.MeshStandardMaterial({ map: tex(cv), transparent: !o.bg, roughness: 0.7, side: THREE.DoubleSide, depthWrite: !!o.bg });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(o.sx ?? 1, (o.sx ?? 1) * h / w), mat);
  return m;
}

// keyframed camera: [t, pos, target, fov]; smootherstep between keys, plus a slow hand-held drift
export function camKeys(cam, K, t, drift = 1) {
  let a = K[0], b = K[K.length - 1];
  if (t <= K[0][0]) b = a;
  else if (t >= K[K.length - 1][0]) a = b;
  else for (let i = 0; i < K.length - 1; i++) if (t >= K[i][0] && t <= K[i + 1][0]) { a = K[i]; b = K[i + 1]; break; }
  const u = a === b ? 0 : smoother((t - a[0]) / (b[0] - a[0]));
  const L = (p, q) => p.map((v, i) => v + (q[i] - v) * u);
  const p = L(a[1], b[1]), g = L(a[2], b[2]);
  p[0] += 0.04 * drift * Math.sin(t * 0.37); p[1] += 0.025 * drift * Math.sin(t * 0.29 + 1);
  cam.position.set(...p); cam.lookAt(...g);
  cam.fov = (a[3] ?? 32) + ((b[3] ?? 32) - (a[3] ?? 32)) * u; cam.updateProjectionMatrix();
}
export function newCam() { return new THREE.PerspectiveCamera(32, W / H, 0.02, 200); }
export const ease = { clamp, smoother };

// world point -> screen pixel (for 2D labels that follow 3D objects)
export function toScreen(cam, v) {
  const p = v.clone().project(cam);
  return [(p.x + 1) / 2 * W, (1 - p.y) / 2 * H, p.z];
}

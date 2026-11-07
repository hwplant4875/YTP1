// Beat 3 (0:31-1:06) as a 3D money chart: the stock market as a field of $100-bundle columns, one per
// company, in a bright paper studio with a free perspective camera. At "fell" the top 4.4% of every
// column shears off; Qualcomm and Arm step forward on logo plinths and lose their tops; Nvidia's
// column towers in the middle. Deterministic: everything is a function of t.
import * as THREE from 'three';
import { cue } from '../js/cue.js';
import { money, COL } from '../js/objects.js';
import { bigText, clamp, smoother, easeOut, easeIn, mulberry32 } from '../js/iso.js';

const W = 1920, H = 1080, BT = 0.010922;           // bundle thickness (m)
const BW = 0.156, BD = 0.0663;                      // bundle footprint (m)
const c = (w, n) => cue('b03', w, n);

function tex(canvas, rep = [1, 1]) {
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]);
  return t;
}
async function img(src) { const i = new Image(); i.src = src; await i.decode(); return i; }

// a stack of bundles as one box; side UVs repeat once per bundle so the paper edges and straps line up
function stackGeo(h, nx = 2, nz = 1) {
  const g = new THREE.BoxGeometry(BW * nx, h, BD * nz);
  const uv = g.attributes.uv, n = h / BT;
  // faces: +x, -x, +y, -y, +z, -z (4 verts each)
  for (const f of [0, 1, 4, 5]) for (let k = 0; k < 4; k++) {
    const i = f * 4 + k;
    uv.setXY(i, uv.getX(i) * (f < 2 ? nz : nx), uv.getY(i) * n);
  }
  for (const f of [2, 3]) for (let k = 0; k < 4; k++) { const i = f * 4 + k; uv.setXY(i, uv.getX(i) * nx, uv.getY(i) * nz); }
  g.translate(0, h / 2, 0);
  return g;
}

export class Market3D {
  constructor(gl, ov) { this.gl = gl; this.ov = ov; this.ctx = ov.getContext('2d'); }
  async init() {
    const r = this.r = new THREE.WebGLRenderer({ canvas: this.gl, antialias: true, preserveDrawingBuffer: true });
    r.setSize(W, H, false); r.setPixelRatio(1);
    r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap;
    r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.05;
    const s = this.s = new THREE.Scene();
    s.background = new THREE.Color(COL.paper);
    s.fog = new THREE.Fog(COL.paper, 10, 26);
    this.cam = new THREE.PerspectiveCamera(32, W / H, 0.05, 80);

    s.add(new THREE.HemisphereLight(0xfff8ec, 0xb9a98c, 1.25));
    const sun = this.sun = new THREE.DirectionalLight(0xfff1dc, 2.4);
    sun.position.set(-5, 9, 6); sun.castShadow = true;
    sun.shadow.mapSize.set(4096, 4096); sun.shadow.radius = 4; sun.shadow.bias = -0.0004;
    Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8, near: 1, far: 34 });
    s.add(sun);

    const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.MeshStandardMaterial({ color: 0xEFE5D2, roughness: 0.95 }));
    floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; s.add(floor);

    // money materials from the opening's own bill art, so the cash matches the first 30 s
    const M = money();
    const seam = (src) => { const cv = document.createElement('canvas'); cv.width = src.width; cv.height = src.height; const g = cv.getContext('2d');
      g.drawImage(src, 0, 0); g.fillStyle = 'rgba(40,60,30,0.55)'; g.fillRect(0, src.height - 9, src.width, 9); g.fillRect(0, 0, 8, src.height); g.fillRect(src.width - 8, 0, 8, src.height);
      g.fillStyle = 'rgba(255,255,240,0.35)'; g.fillRect(0, 0, src.width, 5); return cv; };
    const topC = (() => { const cv = document.createElement('canvas'); cv.width = M.top.width; cv.height = M.top.height; const g = cv.getContext('2d');
      g.drawImage(M.top, 0, 0); g.strokeStyle = 'rgba(40,60,30,0.6)'; g.lineWidth = 14; g.strokeRect(0, 0, cv.width, cv.height); return cv; })();
    const top = tex(topC), long = tex(seam(M.long)), end = tex(seam(M.end));
    const mat = (map, color = 0xffffff) => new THREE.MeshStandardMaterial({ map, color, roughness: 0.82 });
    this.mats = () => [mat(end), mat(end), mat(top), mat(top), mat(long), mat(long)];
    const shared = this.mats();

    // the field: ~500 companies, a few giants, most small (seeded)
    const rnd = mulberry32(5005);
    this.cols = [];
    const NX = 25, NZ = 20, DX = 0.37, DZ = 0.25;
    const field = new THREE.Group(); s.add(field);
    const slices = [];
    for (let i = 0; i < NX; i++) for (let j = 0; j < NZ; j++) {
      const x = (i - (NX - 1) / 2) * DX + (rnd() - 0.5) * 0.03, z = (j - (NZ - 1) / 2) * DZ - 2.2 + (rnd() - 0.5) * 0.02;
      const big = Math.pow(rnd(), 7);
      let h = 0.08 + rnd() * 0.3 + big * 1.1;
      const nv = i === 12 && j === NZ - 1;
      if (nv) h = 2.3;                                   // Nvidia: the tallest column
      const body = new THREE.Mesh(stackGeo(h * 0.956, 2, 3), nv ? this.mats() : shared);
      body.position.set(x, 0, z); body.castShadow = body.receiveShadow = true; field.add(body);
      const sl = new THREE.Mesh(stackGeo(h * 0.044, 2, 3), this.mats());
      sl.position.set(x, h * 0.956, z); sl.castShadow = true; field.add(sl);
      const tech = (Math.abs(i - 12) < 5 && Math.abs(j - 9) < 4);
      slices.push({ m: sl, x, z, h, y0: h * 0.956, d: rnd(), spin: rnd() - 0.5, tech, nv });
    }
    this.slices = slices;
    this.nv = slices.find(q => q.nv);

    // logo plinths: Nvidia at its column, Qualcomm and Arm stepping out in front of the field
    const logos = { nv: await img('../assets/logos/nvidia.svg'), qc: await img('../assets/logos/qualcomm.svg'), arm: await img('../assets/logos/arm.png') };
    this.plate = (logo, w, hgt) => {
      const cv = document.createElement('canvas'); cv.width = 1600; cv.height = Math.round(1600 * hgt / w);
      const g = cv.getContext('2d');
      g.fillStyle = '#FBF7EE'; g.fillRect(0, 0, cv.width, cv.height);
      const lw = cv.width * 0.8, lh = lw * logo.height / logo.width, k = Math.min(1, cv.height * 0.62 / lh);
      g.drawImage(logo, (cv.width - lw * k) / 2, (cv.height - lh * k) / 2, lw * k, lh * k);
      const face = new THREE.MeshStandardMaterial({ map: tex(cv), roughness: 0.6 });
      const side = new THREE.MeshStandardMaterial({ color: 0xE9DFCB, roughness: 0.7 });
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, hgt, 0.06), [side, side, side, side, face, side]);
      m.castShadow = m.receiveShadow = true;
      return m;
    };
    const nvPlate = this.plate(logos.nv, 0.62, 0.15); nvPlate.position.set(this.nv.x, 0.075, this.nv.z + 0.17); s.add(nvPlate);

    this.front = [];
    for (const [k, x, h, loss, name] of [['qc', -0.75, 0.62, 0.0949, 'qc'], ['arm', 0.75, 0.5, 0.1308, 'arm']]) {
      const g = new THREE.Group(); g.position.set(x, 0, 0.6); s.add(g);
      const base = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.08, 0.6), new THREE.MeshStandardMaterial({ color: 0xE6DBC6, roughness: 0.9 }));
      base.position.y = 0.04; base.castShadow = base.receiveShadow = true; g.add(base);
      const body = new THREE.Mesh(stackGeo(h * (1 - loss), 4, 4), this.mats()); body.position.y = 0.08; body.castShadow = body.receiveShadow = true; g.add(body);
      const top = new THREE.Mesh(stackGeo(h * loss, 4, 4), this.mats()); top.position.y = 0.08 + h * (1 - loss); top.castShadow = true; g.add(top);
      const plate = this.plate(logos[k], 0.78, 0.2); plate.position.set(0, 0.16, 0.36); plate.rotation.x = -0.18; g.add(plate);
      this.front.push({ g, top, y0: top.position.y, h, loss, name });
    }

    this.T = { here: cue('b03', "Here's"), sp: c('S'), fell: c('fell'), nas: c('Nasdaq'), analysts: c('Analysts'), chips: c('chips.'),
      two: c('Two'), qc: c('Qualcomm'), arm: c('Arm,'), dis: c('disappointed'), whole: c('whole'), ai: c('AI'), end: cue('b04', 'To') };
  }

  camera(t) {
    const T = this.T;
    // [time, pos, target, fov]
    const K = [
      [T.here - 0.1, [0.8, 14, 9.0], [0, 0, -2.2], 32],
      [T.sp - 0.3, [-6.2, 4.4, 4.6], [0.0, 0.3, -2.0], 34],
      [T.fell + 2.2, [-4.2, 2.6, 3.4], [0.4, 0.4, -2.2], 34],
      [T.nas + 2.5, [3.6, 3.0, 3.2], [0.0, 0.5, -2.4], 32],
      [T.chips, [2.2, 2.4, 4.4], [0.0, 0.7, -0.6], 34],
      [T.qc + 0.2, [0.1, 1.35, 3.7], [0.0, 0.42, 0.4], 36],
      [T.dis + 1.4, [0.25, 1.15, 3.2], [0.0, 0.4, 0.5], 36],
      [T.whole + 0.4, [-1.2, 3.6, 6.6], [0.0, 0.5, -1.4], 34],
      [T.end, [0.0, 6.0, 8.2], [0.0, 0.4, -1.8], 32],
    ];
    let a = K[0], b = K[K.length - 1];
    for (let i = 0; i < K.length - 1; i++) if (t >= K[i][0] && t <= K[i + 1][0]) { a = K[i]; b = K[i + 1]; break; }
    if (t > K[K.length - 1][0]) a = b;
    const u = a === b ? 0 : smoother((t - a[0]) / (b[0] - a[0]));
    const L = (p, q) => p.map((v, i) => v + (q[i] - v) * u);
    const p = L(a[1], b[1]), g = L(a[2], b[2]);
    // a slow hand-held drift so no frame is ever dead still
    p[0] += 0.04 * Math.sin(t * 0.37); p[1] += 0.025 * Math.sin(t * 0.29 + 1);
    this.cam.position.set(...p); this.cam.lookAt(...g);
    this.cam.fov = a[3] + (b[3] - a[3]) * u; this.cam.updateProjectionMatrix();
  }

  render(t) {
    const T = this.T;
    this.camera(t);
    // focus + context: while Qualcomm and Arm are named, the rest of the market fades into the paper
    const foc = clamp((t - T.two + 0.3) / 0.8) * (1 - clamp((t - T.whole) / 1.0));
    this.s.fog.near = 10 - 6.8 * foc; this.s.fog.far = 26 - 16 * foc;
    // field slices: flash coral, then shear off and fall (staggered), gone into the floor
    for (const q of this.slices) {
      const t0 = T.fell + 0.05 + q.d * 0.7, f = t - t0;
      const mats = q.m.material;
      const hot = f > 0 ? clamp(f / 0.12) : 0;
      for (const m of mats) m.color.setRGB(1, 1 - 0.55 * hot, 1 - 0.62 * hot);
      if (f <= 0.15) { q.m.position.set(q.x, q.y0, q.z); q.m.rotation.set(0, 0, 0); q.m.visible = true; continue; }
      const ff = f - 0.15, y = q.y0 - 4.9 * ff * ff;
      q.m.visible = y > -0.05;
      q.m.position.set(q.x + q.spin * 0.15 * ff, Math.max(y, -0.05), q.z + 0.05 * ff);
      q.m.rotation.set(q.spin * 2.2 * ff, 0, q.spin * 1.6 * ff);
    }
    // Qualcomm and Arm: rise into place as they are named, then lose their tops
    for (const [k, F] of this.front.entries()) {
      const tn = k === 0 ? T.qc : T.arm, rise = easeOut(clamp((t - tn + 0.35) / 0.7));
      F.g.position.y = -1.6 * (1 - rise); F.g.visible = rise > 0;
      const t0 = T.dis - 0.1 + k * 0.25, f = t - t0;
      const hot = f > 0 ? clamp(f / 0.12) : 0;
      for (const m of F.top.material) m.color.setRGB(1, 1 - 0.55 * hot, 1 - 0.62 * hot);
      if (f <= 0.15) { F.top.position.set(0, F.y0, 0); F.top.rotation.set(0, 0, 0); F.top.visible = true; }
      else { const ff = f - 0.15; F.top.position.set((k ? 0.25 : -0.25) * ff, F.y0 - 4.9 * ff * ff, 0.1 * ff); F.top.rotation.set(0.6 * ff, 0, (k ? -1 : 1) * 1.4 * ff); F.top.visible = F.top.position.y > -0.2; }
    }
    this.r.render(this.s, this.cam);

    // big key text (YouTube Sans), one highlight colour; losses in coral
    const g = this.ctx; g.clearRect(0, 0, W, H);
    const RED = '#FF6B57';
    const spA = 1 - clamp((t - T.analysts) / 0.4);
    if (t > T.sp - 0.1 && spA > 0) {
      bigText(g, 'S&P 500', 120, 190, { size: 120, p: clamp((t - T.sp + 0.1) / 0.45), a: spA, align: 'left' });
      bigText(g, [['-4.4%', RED]], 120, 190 + 140, { size: 140, p: clamp((t - T.fell - 0.25) / 0.45), a: spA, align: 'left' });
    }
    if (t > T.nas - 0.1 && spA > 0) {
      bigText(g, 'NASDAQ', W - 120, 190, { size: 120, p: clamp((t - T.nas + 0.1) / 0.45), a: spA, align: 'right' });
      bigText(g, [['-5.5%', RED]], W - 120, 190 + 140, { size: 140, p: clamp((t - c('half') + 0.1) / 0.45), a: spA, align: 'right' });
    }
    const fA = 1 - clamp((t - T.whole) / 0.4);
    if (t > T.dis && fA > 0) {
      bigText(g, [['-9.5%', RED]], 330, 300, { size: 130, p: clamp((t - T.dis - 0.2) / 0.45), a: fA });
      bigText(g, [['-13.1%', RED]], W - 330, 300, { size: 130, p: clamp((t - T.dis - 0.45) / 0.45), a: fA });
    }
  }
}

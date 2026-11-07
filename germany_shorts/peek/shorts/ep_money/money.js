// Cash: a stylised $100 note (our own design, not a copy of the real note), banded $10,000 bundles,
// a tower of bundles that evaporates from the top, glowing dust and loose fluttering bills.
import * as THREE from 'three';

export function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

// one bundle = 100 notes; 1 scene unit = 10 cm
export const BILL = { L: 1.56, W: 0.663, T: 0.11 };

export function billCanvas(seed = 7) {
  const W = 1024, H = Math.round(1024 * BILL.W / BILL.L);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d');
  const rnd = mulberry32(seed);
  const pg = g.createLinearGradient(0, 0, W, H);
  pg.addColorStop(0, '#e2e8d8'); pg.addColorStop(0.5, '#d5dfcb'); pg.addColorStop(1, '#cbd6c0');
  g.fillStyle = pg; g.fillRect(0, 0, W, H);
  // paper fibres
  for (let i = 0; i < 2600; i++) {
    g.fillStyle = `rgba(${60 + rnd() * 40},${90 + rnd() * 40},${70 + rnd() * 30},${0.05 + rnd() * 0.07})`;
    g.fillRect(rnd() * W, rnd() * H, 1 + rnd() * 3, 1);
  }
  const ink = '#2f4d3c';
  // guilloche bands top and bottom
  g.lineWidth = 1;
  for (const y0 of [34, H - 34]) {
    for (let k = 0; k < 9; k++) {
      g.strokeStyle = `rgba(47,77,60,${0.22 + 0.03 * k})`;
      g.beginPath();
      for (let x = 30; x <= W - 30; x += 3) {
        const y = y0 + 7 * Math.sin(x / 11 + k * 0.7) * Math.cos(x / 47 + k);
        x === 30 ? g.moveTo(x, y) : g.lineTo(x, y);
      }
      g.stroke();
    }
  }
  // frame
  g.strokeStyle = ink; g.lineWidth = 3;
  g.beginPath(); g.roundRect(16, 16, W - 32, H - 32, 10); g.stroke();
  g.lineWidth = 1.2; g.beginPath(); g.roundRect(26, 26, W - 52, H - 52, 8); g.stroke();
  // oval medallion (fine rings, no portrait)
  const ox = 360, oy = H / 2, rx = 112, ry = 140;
  const og = g.createRadialGradient(ox, oy, 10, ox, oy, ry);
  og.addColorStop(0, '#c8d3bd'); og.addColorStop(1, '#b8c6ad');
  g.fillStyle = og; g.beginPath(); g.ellipse(ox, oy, rx, ry, 0, 0, Math.PI * 2); g.fill();
  for (let k = 0; k < 34; k++) {
    g.strokeStyle = `rgba(47,77,60,${0.18 + 0.4 * (k % 3 === 0)})`; g.lineWidth = 1;
    g.beginPath(); g.ellipse(ox, oy, rx * (1 - k / 40), ry * (1 - k / 40), 0, 0, Math.PI * 2); g.stroke();
  }
  g.lineWidth = 4; g.strokeStyle = ink; g.beginPath(); g.ellipse(ox, oy, rx + 8, ry + 8, 0, 0, Math.PI * 2); g.stroke();
  // rosette on the left
  g.save(); g.translate(120, H / 2);
  for (let k = 0; k < 18; k++) { g.rotate(Math.PI / 9); g.strokeStyle = 'rgba(47,77,60,0.35)'; g.beginPath(); g.ellipse(0, 0, 60, 18, 0, 0, Math.PI * 2); g.stroke(); }
  g.restore();
  // blue security ribbon
  const bx = 600;
  g.fillStyle = '#3d74d9'; g.fillRect(bx, 26, 22, H - 52);
  g.fillStyle = 'rgba(255,255,255,0.75)'; g.font = 'bold 11px Georgia';
  for (let y = 40; y < H - 30; y += 26) g.fillText('100', bx + 2, y);
  // numerals
  g.fillStyle = ink; g.font = 'bold 74px Georgia'; g.fillText('100', 48, 110);
  g.font = 'bold 60px Georgia'; g.fillText('100', W - 168, 98);
  const cg = g.createLinearGradient(W - 330, H - 190, W - 60, H - 60);
  cg.addColorStop(0, '#b0743c'); cg.addColorStop(0.5, '#d8a465'); cg.addColorStop(1, '#8a5a2c');
  g.fillStyle = cg; g.font = 'bold 150px Georgia'; g.fillText('100', W - 330, H - 52);
  g.fillStyle = ink; g.font = 'bold 26px Georgia'; g.textAlign = 'center';
  g.fillText('ONE HUNDRED', 760, 74);
  g.textAlign = 'left';
  // aged edges
  const vg = g.createRadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, W * 0.62);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(40,50,30,0.22)');
  g.fillStyle = vg; g.fillRect(0, 0, W, H);
  return c;
}

// ---------------------------------------------------------------------------
// Bundle faces. The $10,000 strap (mustard, as real $100 straps are) is printed into the faces.
const BAND = 0.34 / 1.56;                      // strap width as a share of the bundle length
const PAPER = '#c3cdb8';

function edgeLines(g, x, y, w, h, rnd, tone = 0) {
  g.fillStyle = PAPER; g.fillRect(x, y, w, h);
  const n = Math.max(6, Math.round(h * 1.2));
  for (let j = 0; j < n; j++) {
    const yy = y + (j + rnd() * 0.6) * h / n;
    g.fillStyle = `rgba(${70 + rnd() * 40},${90 + rnd() * 40},${70 + rnd() * 30},${0.10 + rnd() * 0.22})`;
    g.fillRect(x, yy, w, Math.max(0.6, h / n * 0.45));
  }
  // top and bottom bills catch less light
  const sg = g.createLinearGradient(0, y, 0, y + h);
  sg.addColorStop(0, 'rgba(255,255,255,0.10)'); sg.addColorStop(0.15, 'rgba(0,0,0,0)'); sg.addColorStop(0.85, 'rgba(0,0,0,0)'); sg.addColorStop(1, 'rgba(20,30,20,0.25)');
  g.fillStyle = sg; g.fillRect(x, y, w, h);
  if (tone) { g.fillStyle = `rgba(0,0,0,${tone})`; g.fillRect(x, y, w, h); }
}
function strap(g, x, y, w, h) {
  g.fillStyle = '#a8812f'; g.fillRect(x, y, w, h);
  g.fillStyle = 'rgba(255,240,200,0.12)'; g.fillRect(x, y, w, Math.max(1, h * 0.12));
  g.fillStyle = 'rgba(60,40,0,0.25)'; g.fillRect(x, y + h * 0.88, w, h * 0.12);
}

// long side of one bundle (L x T), with the strap in the middle
function longCanvas(seed = 5) {
  const W = 512, H = 40, rnd = mulberry32(seed);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d');
  edgeLines(g, 0, 0, W, H, rnd);
  strap(g, W * (0.5 - BAND / 2), 0, W * BAND, H);
  return c;
}
function shortCanvas(seed = 6) {
  const W = 256, H = 44, rnd = mulberry32(seed);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d');
  edgeLines(g, 0, 0, W, H, rnd);
  return c;
}
// top of one bundle: a note with the strap across it
function topCanvas(seed = 7) {
  const c = billCanvas(seed);
  const g = c.getContext('2d');
  const W = c.width, H = c.height;
  const x = W * (0.5 - BAND / 2), w = W * BAND;
  strap(g, x, 0, w, H);
  g.save(); g.translate(x + w / 2, H / 2); g.rotate(-Math.PI / 2);
  g.fillStyle = '#3b2a0e'; g.font = 'bold 54px Georgia'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText('$10,000', 0, 3);
  g.restore();
  return c;
}

// core tiles: the same faces drawn many times with small offsets, so a single box reads as a stack
const TILE_LAYERS = 8;
function coreLongCanvas(nx, seed) {
  const cw = 256, ch = 18, rnd = mulberry32(seed);
  const c = document.createElement('canvas'); c.width = nx * cw; c.height = TILE_LAYERS * ch;
  const g = c.getContext('2d');
  g.fillStyle = '#6d7566'; g.fillRect(0, 0, c.width, c.height);
  for (let l = 0; l < TILE_LAYERS; l++) for (let i = 0; i < nx; i++) {
    const ox = (rnd() - 0.5) * 5, y = l * ch;
    const x = i * cw + 1 + ox, w = cw - 2.5;
    edgeLines(g, x, y + 0.3, w, ch - 0.6, rnd, rnd() * 0.03);
    strap(g, x + w * (0.5 - BAND / 2), y + 0.3, w * BAND, ch - 0.6);
  }
  return c;
}
function coreShortCanvas(nz, seed) {
  const cw = 112, ch = 18, rnd = mulberry32(seed);
  const c = document.createElement('canvas'); c.width = nz * cw; c.height = TILE_LAYERS * ch;
  const g = c.getContext('2d');
  g.fillStyle = '#6d7566'; g.fillRect(0, 0, c.width, c.height);
  for (let l = 0; l < TILE_LAYERS; l++) for (let k = 0; k < nz; k++) {
    const ox = (rnd() - 0.5) * 4;
    edgeLines(g, k * cw + 1 + ox, l * ch + 0.3, cw - 2.5, ch - 0.6, rnd, rnd() * 0.03);
  }
  return c;
}
function coreTopCanvas(nx, nz, seed) {
  const bw = 256, bh = Math.round(256 * BILL.W / BILL.L), rnd = mulberry32(seed);
  const c = document.createElement('canvas'); c.width = nx * bw; c.height = nz * bh;
  const g = c.getContext('2d');
  g.fillStyle = '#1b2019'; g.fillRect(0, 0, c.width, c.height);
  const top = topCanvas();
  for (let i = 0; i < nx; i++) for (let k = 0; k < nz; k++) {
    g.save(); g.translate(i * bw + bw / 2 + (rnd() - 0.5) * 4, k * bh + bh / 2 + (rnd() - 0.5) * 3); g.rotate((rnd() - 0.5) * 0.03);
    g.drawImage(top, -bw / 2 + 1, -bh / 2 + 1, bw - 2, bh - 2);
    g.restore();
  }
  return c;
}

const tex = (c, srgb = true) => { const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
const paper = (map, rough = 0.86) => new THREE.MeshStandardMaterial({ map, roughness: rough, metalness: 0 });

let _mats = null;
export function cashMaterials() {
  if (_mats) return _mats;
  const bill = tex(billCanvas());
  const top = paper(tex(topCanvas()));
  const bottom = paper(tex(topCanvas(11)));
  const long = paper(tex(longCanvas()));
  const short = paper(tex(shortCanvas()));
  const loose = new THREE.MeshStandardMaterial({ map: bill, roughness: 0.8, metalness: 0, side: THREE.DoubleSide });
  _mats = { bill, top, bottom, long, short, loose, cores: new Map() };
  return _mats;
}
function coreTextures(nx, nz) {
  const M = cashMaterials();
  const k = nx + 'x' + nz;
  if (!M.cores.has(k)) M.cores.set(k, { long: coreLongCanvas(nx, 101), short: coreShortCanvas(nz, 202), top: coreTopCanvas(nx, nz, 303) });
  return M.cores.get(k);
}

export function bundleGeometry() {
  return new THREE.BoxGeometry(BILL.L, BILL.T, BILL.W);
}

// ---------------------------------------------------------------------------
// A tower of bundles that burns away from the top down, deterministically.
// Below the burning front the tower is one textured box (cheap); the top `win` layers are real bundles.
export const GAP = { x: 0.03, y: 0.004, z: 0.03 };
export const PITCH = BILL.T + GAP.y;

export function buildTower({ nx = 4, nz = 6, layers = 100, seed = 2800, t0 = 0.12, span = 1.9, noise = 0.3, fade = 0.22, win = 0 } = {}) {
  const M = cashMaterials();
  const rnd = mulberry32(seed);
  const root = new THREE.Group();
  const W = nx * (BILL.L + GAP.x) - GAP.x, D = nz * (BILL.W + GAP.z) - GAP.z;
  const info = [];
  for (let l = 0; l < layers; l++) for (let i = 0; i < nx; i++) for (let k = 0; k < nz; k++) {
    const p = new THREE.Vector3(
      -W / 2 + BILL.L / 2 + i * (BILL.L + GAP.x) + (rnd() - 0.5) * 0.03,
      BILL.T / 2 + l * PITCH,
      -D / 2 + BILL.W / 2 + k * (BILL.W + GAP.z) + (rnd() - 0.5) * 0.03);
    const h = layers > 1 ? l / (layers - 1) : 1;
    const edge = (i === 0 || i === nx - 1 || k === 0 || k === nz - 1);
    info.push({ p, ry: (rnd() - 0.5) * 0.035, h, n: rnd(), edge, l, sp: new THREE.Vector3(rnd() - 0.5, rnd(), rnd() - 0.5) });
  }
  // the box core
  const CT = coreTextures(nx, nz);
  const longT = tex(CT.long), shortT = tex(CT.short), topT = tex(CT.top);
  for (const t of [longT, shortT]) { t.wrapS = THREE.ClampToEdgeWrapping; t.wrapT = THREE.RepeatWrapping; }
  const longM = paper(longT), shortM = paper(shortT), topM = paper(topT);
  const core = new THREE.Mesh(new THREE.BoxGeometry(W, 1, D), [shortM, shortM, topM, topM, longM, longM]);
  core.castShadow = true; core.receiveShadow = true;
  root.add(core);
  let pool = null;
  if (win > 0) {
    pool = new THREE.InstancedMesh(bundleGeometry(), [M.short, M.short, M.top, M.bottom, M.long, M.long], win * nx * nz);
    pool.castShadow = true; pool.receiveShadow = true;
    pool.setColorAt(0, new THREE.Color(1, 1, 1));
    pool.frustumCulled = false;
    root.add(pool);
  }
  const tw = { root, core, pool, info, nx, nz, layers, W, D, height: layers * PITCH, t0, span, noise, fade, win, longT, shortT };
  setTower(tw, -1);
  return tw;
}

export function vanishTime(tw, it) { return tw.t0 + (1 - it.h) * tw.span + it.n * tw.noise; }

const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _s = new THREE.Vector3(), _e = new THREE.Euler(), _c = new THREE.Color(), _p = new THREE.Vector3();
// state of one bundle at time t: k = 0 intact ... 1 gone
function bundleK(tw, it, t) { return t < 0 ? 0 : clamp01((t - vanishTime(tw, it)) / tw.fade); }
const clamp01 = x => Math.min(1, Math.max(0, x));

export function setTower(tw, t) {
  const { layers, nx, nz, win } = tw;
  const per = nx * nz;
  // top layer that still has something left
  let top = layers - 1;
  while (top >= 0) {
    let alive = false;
    for (let j = 0; j < per; j++) if (bundleK(tw, tw.info[top * per + j], t) < 1) { alive = true; break; }
    if (alive) break;
    top--;
  }
  // layers fully intact form the core; with no pool the core is the whole tower and shrinks layer by layer
  let coreLayers;
  if (win > 0) coreLayers = Math.max(0, top - win + 1);
  else {
    coreLayers = 0;
    for (let l = 0; l <= top; l++) {
      let gone = false;
      for (let j = 0; j < per; j++) if (bundleK(tw, tw.info[l * per + j], t) > 0.5) { gone = true; break; }
      if (gone) break;
      coreLayers = l + 1;
    }
  }
  const ch = coreLayers * PITCH - GAP.y;
  tw.core.visible = coreLayers > 0;
  if (coreLayers > 0) {
    tw.core.scale.y = ch; tw.core.position.y = ch / 2;
    tw.longT.repeat.set(1, coreLayers / TILE_LAYERS); tw.shortT.repeat.set(1, coreLayers / TILE_LAYERS);
  }
  if (!tw.pool) return { top, coreLayers };
  const pool = tw.pool;
  let n = 0;
  for (let l = coreLayers; l <= top && l < coreLayers + win; l++) {
    for (let j = 0; j < per; j++) {
      const it = tw.info[l * per + j];
      const k = bundleK(tw, it, t);
      if (k >= 1) { _m.makeScale(1e-5, 1e-5, 1e-5); pool.setMatrixAt(n, _m); _c.setRGB(1, 1, 1); pool.setColorAt(n, _c); n++; continue; }
      const s = 1 - k * k * (3 - 2 * k);
      const kick = k * k;
      _e.set(kick * 1.2 * (it.sp.x), it.ry + kick * 1.5 * (it.n - 0.5), kick * 1.2 * it.sp.z); _q.setFromEuler(_e);
      _s.set(Math.max(1e-4, s), Math.max(1e-4, s * (1 - 0.5 * k)), Math.max(1e-4, s));
      _p.copy(it.p); _p.x += it.sp.x * kick * 0.9; _p.y += kick * (0.4 + it.sp.y * 0.8); _p.z += it.sp.z * kick * 0.9;
      _m.compose(_p, _q, _s);
      pool.setMatrixAt(n, _m);
      const glow = 1 + 2.4 * Math.sin(Math.PI * Math.min(1, k * 1.15));
      _c.setRGB(glow, glow, glow * 0.85);
      pool.setColorAt(n, _c);
      n++;
    }
  }
  pool.count = n;
  pool.instanceMatrix.needsUpdate = true;
  if (pool.instanceColor) pool.instanceColor.needsUpdate = true;
  return { top, coreLayers };
}

// glowing dust that each bundle turns into
export function buildDust(tw, { perBundle = 5, seed = 77, every = 1 } = {}) {
  const rnd = mulberry32(seed);
  const src = tw.info.filter((_, j) => j % every === 0);
  const N = src.length * perBundle;
  const pos = new Float32Array(N * 3), vel = new Float32Array(N * 3), born = new Float32Array(N), life = new Float32Array(N), size = new Float32Array(N), hue = new Float32Array(N);
  let i = 0;
  for (const it of src) {
    const tv = vanishTime(tw, it);
    for (let k = 0; k < perBundle; k++, i++) {
      pos[i * 3] = it.p.x + (rnd() - 0.5) * BILL.L; pos[i * 3 + 1] = it.p.y + (rnd() - 0.5) * BILL.T; pos[i * 3 + 2] = it.p.z + (rnd() - 0.5) * BILL.W;
      const out = new THREE.Vector2(it.p.x, it.p.z).normalize();
      const sp = 0.3 + rnd() * 1.1;
      vel[i * 3] = out.x * sp + (rnd() - 0.5) * 0.8; vel[i * 3 + 1] = 0.5 + rnd() * 1.6; vel[i * 3 + 2] = out.y * sp + (rnd() - 0.5) * 0.8;
      born[i] = tv + rnd() * 0.18; life[i] = 1.1 + rnd() * 1.3; size[i] = 0.5 + rnd(); hue[i] = rnd();
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('aVel', new THREE.BufferAttribute(vel, 3));
  geo.setAttribute('aBorn', new THREE.BufferAttribute(born, 1));
  geo.setAttribute('aLife', new THREE.BufferAttribute(life, 1));
  geo.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
  geo.setAttribute('aHue', new THREE.BufferAttribute(hue, 1));
  const mat = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uScale: { value: 1 }, uBright: { value: 2.2 } },
    vertexShader: `attribute vec3 aVel; attribute float aBorn, aLife, aSize, aHue; uniform float uTime, uScale; varying float vA; varying float vH;
      void main(){ float age = uTime - aBorn; vA = 0.0; vH = aHue;
        if (age < 0.0 || age > aLife) { gl_Position = vec4(2.0,2.0,2.0,1.0); gl_PointSize = 0.0; return; }
        float k = age / aLife; vA = (1.0 - k) * smoothstep(0.0, 0.08, age);
        vec3 p = position + aVel * age * (1.0 - 0.35 * k) + vec3(sin(age*3.0 + aHue*20.0), 0.0, cos(age*2.6 + aHue*13.0)) * 0.25 * age;
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        gl_Position = projectionMatrix * mv;
        gl_PointSize = uScale * aSize * (0.9 + 0.6 * k) / -mv.z; }`,
    fragmentShader: `uniform float uBright; varying float vA; varying float vH;
      void main(){ vec2 d = gl_PointCoord - 0.5; float r = length(d); if (r > 0.5) discard;
        float a = smoothstep(0.5, 0.0, r) * vA;
        vec3 col = mix(vec3(0.75, 1.0, 0.55), vec3(1.0, 0.85, 0.45), vH);
        gl_FragColor = vec4(col * uBright * a, a); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false,
  });
  const pts = new THREE.Points(geo, mat);
  pts.frustumCulled = false;
  return { points: pts, mat };
}

// loose single notes that peel off and flutter down
export function buildLooseBills(tw, { count = 90, seed = 909 } = {}) {
  const M = cashMaterials();
  const rnd = mulberry32(seed);
  const geo = new THREE.PlaneGeometry(BILL.L, BILL.W, 6, 1);
  const p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i); p.setZ(i, 0.06 * Math.cos(x / BILL.L * Math.PI)); }
  geo.computeVertexNormals();
  const mesh = new THREE.InstancedMesh(geo, M.loose, count);
  mesh.castShadow = true;
  mesh.frustumCulled = false;
  const edges = tw.info.filter(it => it.edge && it.h > 0.15);
  const bills = [];
  for (let i = 0; i < count; i++) {
    const it = edges[Math.floor(rnd() * edges.length)];
    bills.push({
      p0: it.p.clone(), born: vanishTime(tw, it) + rnd() * 0.15,
      v: new THREE.Vector3((rnd() - 0.5) * 2.2 + Math.sign(it.p.x) * 0.6, 0.6 + rnd() * 1.4, (rnd() - 0.5) * 2.2 + Math.sign(it.p.z) * 0.6),
      spin: new THREE.Vector3((rnd() - 0.5) * 6, (rnd() - 0.5) * 4, (rnd() - 0.5) * 6), ph: rnd() * 6.28,
    });
  }
  return { mesh, bills };
}

export function setLooseBills(L, t, floorY) {
  const { mesh, bills } = L;
  for (let i = 0; i < bills.length; i++) {
    const b = bills[i];
    const age = t - b.born;
    if (age < 0) { _m.makeScale(1e-5, 1e-5, 1e-5); mesh.setMatrixAt(i, _m); continue; }
    // drag-limited fall with a side-to-side sway, like real paper
    const drag = 1 - Math.exp(-age * 1.6);
    _p.copy(b.p0).addScaledVector(b.v, drag / 1.6);
    _p.y += -0.55 * age;
    _p.x += 0.35 * Math.sin(age * 2.3 + b.ph); _p.z += 0.35 * Math.cos(age * 1.9 + b.ph);
    _p.y = Math.max(floorY + 0.012, _p.y);
    const landed = _p.y <= floorY + 0.013;
    _e.set(landed ? -Math.PI / 2 : b.spin.x * age + Math.sin(age * 3 + b.ph) * 0.6, b.spin.y * age, landed ? 0 : b.spin.z * age);
    _q.setFromEuler(_e); _s.set(1, 1, 1);
    _m.compose(_p, _q, _s); mesh.setMatrixAt(i, _m);
  }
  mesh.instanceMatrix.needsUpdate = true;
}

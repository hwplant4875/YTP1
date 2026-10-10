// "On a Real Map" preview: Hannibal's march, New Carthage -> Alps -> Turin, on real terrain.
// Terrain: one warped grid (dense around the pass), heights and colour blended from three tile levels.
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

const D = '/map/data/';
const LV = ['outer', 'base', 'alps', 'near'];
const mercY = lat => Math.log(Math.tan(Math.PI / 4 + lat * Math.PI / 360));
const lerp = (a, b, t) => a + (b - a) * t;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = t => t * t * (3 - 2 * t);
const easeOut = t => 1 - Math.pow(1 - t, 3);
const easeOutBack = t => { const c = 1.9; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };

// piecewise curve through keys [t, v] with smooth (monotone cubic) interpolation
function curve(keys) {
  const n = keys.length, m = new Array(n).fill(0);
  const d = [];
  for (let i = 0; i < n - 1; i++) d.push((keys[i + 1][1] - keys[i][1]) / (keys[i + 1][0] - keys[i][0]));
  for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
  for (let i = 0; i < n - 1; i++) { // Fritsch-Carlson clamp
    if (d[i] === 0) { m[i] = m[i + 1] = 0; continue; }
    const a = m[i] / d[i], b = m[i + 1] / d[i], s = a * a + b * b;
    if (s > 9) { const k = 3 / Math.sqrt(s); m[i] = k * a * d[i]; m[i + 1] = k * b * d[i]; }
  }
  return t => {
    if (t <= keys[0][0]) return keys[0][1];
    if (t >= keys[n - 1][0]) return keys[n - 1][1];
    let i = 0; while (t > keys[i + 1][0]) i++;
    const h = keys[i + 1][0] - keys[i][0], s = (t - keys[i][0]) / h;
    const h00 = 2 * s ** 3 - 3 * s ** 2 + 1, h10 = s ** 3 - 2 * s ** 2 + s, h01 = -2 * s ** 3 + 3 * s ** 2, h11 = s ** 3 - s ** 2;
    return h00 * keys[i][1] + h10 * h * m[i] + h01 * keys[i + 1][1] + h11 * h * m[i + 1];
  };
}
const interp = (x, xs, ys) => { if (x <= xs[0]) return ys[0]; for (let i = 1; i < xs.length; i++) if (x <= xs[i]) return lerp(ys[i - 1], ys[i], (x - xs[i - 1]) / (xs[i] - xs[i - 1])); return ys[ys.length - 1]; };

// ---------- timeline (seconds) ----------
// columns: t, head progress, camera target fraction, distance km, pitch deg, azimuth deg (0 = looking north)
const K = [
  [0.0, 0.000, 0.46, 2050, 74, 36],
  [3.5, 0.000, 0.30, 1500, 66, 36],
  [6.2, 0.000, 0.000, 230, 44, 28],
  [8.5, 0.020, 0.020, 250, 42, 28],
  [12.5, 0.240, 0.240, 300, 40, 26],
  [16.5, 0.470, 0.470, 290, 40, 22],
  [19.5, 0.560, 0.555, 220, 33, 14],
  [22.5, 0.742, 0.742, 250, 37, 50],
  [25.5, 0.830, 0.835, 115, 30, 70],
  [28.5, 0.905, 0.905, 42, 22, 80],
  [31.0, 0.929, 0.930, 21, 17, 96],
  [33.2, 0.935, 0.936, 27, 15, 112],
  [35.6, 1.000, 0.985, 125, 31, 72],
  [40.0, 1.000, 0.640, 2750, 78, 36],
];
const col = j => curve(K.map(k => [k[0], k[j]]));
const P = col(1), TQ = col(2), DIST = col(3), PITCH = col(4), AZ = col(5);
export const DURATION = 40;

const CAPTIONS = [
  [0.3, 5.6, 'How far did Hannibal', 'actually march?'],
  [6.0, 10.6, '218 BC. 102,000 men', 'and 37 war elephants.'],
  [10.9, 17.0, 'Destination: Rome.', 'The long way round.'],
  [17.3, 21.2, 'First, the Pyrenees.', ''],
  [21.5, 25.2, 'The Rhône. Elephants', 'ferried across on rafts.'],
  [25.5, 30.8, 'Then the Alps,', 'in the first snow.'],
  [31.1, 34.6, 'Over the pass.', 'Italy below.'],
  [35.0, 40.0, '1,500 km on foot.', 'That\'s London to Rome.'],
];

async function loadF16(url, w, h, THREE) {
  const buf = await (await fetch(url)).arrayBuffer();
  const tex = new THREE.DataTexture(new Uint16Array(buf), w, h, THREE.RedFormat, THREE.HalfFloatType);
  tex.minFilter = tex.magFilter = THREE.LinearFilter; tex.flipY = false; tex.needsUpdate = true;
  return tex;
}
function loadImg(url, THREE, renderer) {
  return new Promise(res => new THREE.TextureLoader().load(url, t => {
    t.flipY = false; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = renderer.capabilities.getMaxAnisotropy();
    t.minFilter = THREE.LinearMipmapLinearFilter; t.generateMipmaps = true; t.needsUpdate = true; res(t);
  }));
}

// sample spacing concentrated around the Alps and the pass (inverse CDF of a density)
function warped(n, a, b, dens) {
  const M = 20000, xs = [], cdf = [0];
  for (let i = 0; i <= M; i++) xs.push(a + (b - a) * i / M);
  for (let i = 1; i <= M; i++) cdf.push(cdf[i - 1] + dens((xs[i] + xs[i - 1]) / 2));
  const out = []; let j = 0;
  for (let k = 0; k < n; k++) {
    const target = cdf[M] * k / (n - 1);
    while (j < M && cdf[j + 1] < target) j++;
    const f = (target - cdf[j]) / Math.max(1e-9, cdf[j + 1] - cdf[j]);
    out.push(xs[j] + (xs[Math.min(j + 1, M)] - xs[j]) * clamp(f));
  }
  out[0] = a; out[n - 1] = b; return out;
}

const terrainVS = `
  uniform sampler2D dem0, dem1, dem2, dem3; uniform vec4 box0, box1, box2, box3; uniform vec2 mer0, mer1, mer2, mer3;
  uniform float LON0, LAT0, KX, KZ, EXAG;
  varying vec2 vLL; varying vec3 vW; varying float vH;
  float mercY(float lat){ return log(tan(0.78539816 + radians(lat)*0.5)); }
  vec2 uvOf(vec2 ll, vec4 b, vec2 m){ return vec2((ll.x-b.x)/(b.z-b.x), (m.x - mercY(ll.y))/(m.x-m.y)); }
  float inW(vec2 ll, vec4 b, float g){ vec2 a = smoothstep(b.xy, b.xy+g, ll) * (1.0-smoothstep(b.zw-g, b.zw, ll)); return a.x*a.y; }
  void main(){
    vec2 ll = position.xy;
    float h = texture2D(dem0, uvOf(ll, box0, mer0)).r;
    float w1 = inW(ll, box1, 0.6), w2 = inW(ll, box2, 0.08), w3 = inW(ll, box3, 0.03);
    if (w1 > 0.0) h = mix(h, texture2D(dem1, uvOf(ll, box1, mer1)).r, w1);
    if (w2 > 0.0) h = mix(h, texture2D(dem2, uvOf(ll, box2, mer2)).r, w2);
    if (w3 > 0.0) h = mix(h, texture2D(dem3, uvOf(ll, box3, mer3)).r, w3);
    vH = h; vLL = ll;
    vec3 p = vec3((ll.x-LON0)*KX, max(h, 0.0)/1000.0*EXAG, -(ll.y-LAT0)*KZ);
    vW = p;
    gl_Position = projectionMatrix * viewMatrix * vec4(p, 1.0);
  }`;
const terrainFS = `
  uniform sampler2D img0, img1, img2, img3, dem0, dem1, dem2, dem3; uniform vec4 box0, box1, box2, box3; uniform vec2 mer0, mer1, mer2, mer3;
  uniform vec2 tx0, tx1, tx2, tx3, km0, km1, km2, km3;
  uniform float EXAG, snowAmt, hazeK, time; uniform vec3 camPos, sunDir, hazeCol; uniform vec4 fullBox;
  varying vec2 vLL; varying vec3 vW; varying float vH;
  float mercY(float lat){ return log(tan(0.78539816 + radians(lat)*0.5)); }
  vec2 uvOf(vec2 ll, vec4 b, vec2 m){ return vec2((ll.x-b.x)/(b.z-b.x), (m.x - mercY(ll.y))/(m.x-m.y)); }
  float inW(vec2 ll, vec4 b, float g){ vec2 a = smoothstep(b.xy, b.xy+g, ll) * (1.0-smoothstep(b.zw-g, b.zw, ll)); return a.x*a.y; }
  vec2 grad(sampler2D d, vec2 uv, vec2 tx, vec2 km){
    float hx = texture2D(d, uv+vec2(tx.x,0.0)).r - texture2D(d, uv-vec2(tx.x,0.0)).r;
    float hz = texture2D(d, uv+vec2(0.0,tx.y)).r - texture2D(d, uv-vec2(0.0,tx.y)).r;
    return vec2(hx/(2.0*km.x*1000.0), hz/(2.0*km.y*1000.0));
  }
  void main(){
    vec2 ll = vLL;
    vec2 u0 = uvOf(ll, box0, mer0), u1 = uvOf(ll, box1, mer1), u2 = uvOf(ll, box2, mer2), u3 = uvOf(ll, box3, mer3);
    float w1 = inW(ll, box1, 0.6), w2 = inW(ll, box2, 0.08), w3 = inW(ll, box3, 0.03);
    vec3 c = texture2D(img0, u0).rgb; vec2 g = grad(dem0, u0, tx0, km0);
    float h = texture2D(dem0, u0).r;
    if (w1 > 0.0) { c = mix(c, texture2D(img1, u1).rgb, w1); g = mix(g, grad(dem1, u1, tx1, km1), w1); h = mix(h, texture2D(dem1,u1).r, w1); }
    if (w2 > 0.0) { c = mix(c, texture2D(img2, u2).rgb, w2); g = mix(g, grad(dem2, u2, tx2, km2), w2); h = mix(h, texture2D(dem2,u2).r, w2); }
    if (w3 > 0.0) { c = mix(c, texture2D(img3, u3).rgb, w3); g = mix(g, grad(dem3, u3, tx3, km3), w3); h = mix(h, texture2D(dem3,u3).r, w3); }
    vec3 n = normalize(vec3(-g.x*EXAG, 1.0, -g.y*EXAG));
    float diff = max(dot(n, sunDir), 0.0);
    // land: satellite colour, lightly re-lit so the relief reads in 3D
    vec3 land = c * 1.18;
    land = mix(vec3(dot(land, vec3(0.3,0.59,0.11))), land, 1.12);
    land *= 0.50 + 0.80*diff;
    // snow above the snow line on gentle slopes
    float snow = smoothstep(2450.0, 2900.0, h + 150.0*sin(ll.x*90.0)*sin(ll.y*70.0)) * smoothstep(0.5, 0.85, n.y) * snowAmt * 0.9;
    land = mix(land, vec3(0.80,0.84,0.90)*(0.48 + 0.45*diff), snow);
    // sea: coloured by depth (hides the imagery's coastal seams), with a soft sun glint
    float depth = clamp(-h/2600.0, 0.0, 1.0);
    vec3 sea = mix(vec3(0.05,0.21,0.28), vec3(0.008,0.035,0.08), sqrt(depth));
    vec3 V = normalize(camPos - vW);
    float spec = pow(max(dot(reflect(-sunDir, vec3(0,1,0)), V), 0.0), 60.0);
    sea += vec3(1.0,0.85,0.6) * spec * 0.25;
    float isLand = smoothstep(-2.0, 6.0, h);
    vec3 col = mix(sea, land, isLand);
    // atmosphere
    float dist = length(camPos - vW);
    float haze = 1.0 - exp(-dist*hazeK);
    col = mix(col, hazeCol, haze*0.7);
    // fade the edges of the data box into darkness
    vec2 e = min(ll - fullBox.xy, fullBox.zw - ll);
    float edge = smoothstep(0.0, 4.0, min(e.x, e.y));
    col = mix(hazeCol, col, edge);
    gl_FragColor = vec4(col, 1.0);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }`;

const FinishShader = {
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, fade: { value: 1 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader: `uniform sampler2D tDiffuse; uniform float time, fade; varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + time*37.1)*43758.5453); }
    void main(){ vec2 c = vUv-0.5; vec3 col = texture2D(tDiffuse, vUv).rgb;
      col = mix(vec3(dot(col, vec3(0.3,0.59,0.11))), col, 1.06);
      col = pow(col, vec3(1.04));
      col *= 1.0 - 0.42*smoothstep(0.12, 0.75, dot(c*vec2(1.25,1.0), c*vec2(1.25,1.0))*2.2);
      col += (hash(vUv*vec2(1080.0,1920.0)) - 0.5)*0.022;
      gl_FragColor = vec4(col*fade, 1.0); }`,
};

export async function setup(THREE, renderer, W, H) {
  const meta = await (await fetch(D + 'levels_meta.json')).json();
  const R = await (await fetch(D + 'route.json')).json();
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(52, W / H, 0.05, 20000);
  const U = {
    LON0: { value: R.LON0 }, LAT0: { value: R.LAT0 }, KX: { value: R.KX }, KZ: { value: R.KZ }, EXAG: { value: R.EXAG },
    snowAmt: { value: 0 }, hazeK: { value: 0.0004 }, time: { value: 0 }, camPos: { value: new THREE.Vector3() },
    sunDir: { value: new THREE.Vector3(-0.55, 0.62, 0.56).normalize() }, hazeCol: { value: new THREE.Color(0.62, 0.70, 0.80) },
    fullBox: { value: new THREE.Vector4(...meta.outer.box) },
  };
  for (let i = 0; i < 4; i++) {
    const L = meta[LV[i]], [lon0, lat0, lon1, lat1] = L.box;
    U['dem' + i] = { value: await loadF16(D + LV[i] + '_dem.f16', L.w, L.h, THREE) };
    U['img' + i] = { value: await loadImg(D + LV[i] + '_img.jpg', THREE, renderer) };
    U['box' + i] = { value: new THREE.Vector4(lon0, lat0, lon1, lat1) };
    U['mer' + i] = { value: new THREE.Vector2(mercY(lat1), mercY(lat0)) };
    U['tx' + i] = { value: new THREE.Vector2(1 / L.w, 1 / L.h) };
    U['km' + i] = { value: new THREE.Vector2((lon1 - lon0) * R.KX / L.w, (lat1 - lat0) * R.KZ / L.h) };
  }
  // warped lon/lat grid
  const N = 1500, [blon0, blat0, blon1, blat1] = meta.outer.box;
  const g = (x, c, s) => Math.exp(-(((x - c) / s) ** 2));
  const lons = warped(N, blon0, blon1, x => (x > -2 && x < 9 ? 1 : 0.35) + 3 * g(x, 6.9, 1.1) + 26 * g(x, 7.03, 0.22));
  const lats = warped(N, blat0, blat1, y => (y > 37 && y < 46.5 ? 1 : 0.35) + 3 * g(y, 44.75, 0.75) + 26 * g(y, 44.71, 0.13));
  const pos = new Float32Array(N * N * 3);
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) { const k = (j * N + i) * 3; pos[k] = lons[i]; pos[k + 1] = lats[j]; }
  const idx = new Uint32Array((N - 1) * (N - 1) * 6); let q = 0;
  for (let j = 0; j < N - 1; j++) for (let i = 0; i < N - 1; i++) {
    const a = j * N + i, b = a + 1, c = a + N, d = c + 1;
    idx[q++] = a; idx[q++] = b; idx[q++] = c; idx[q++] = b; idx[q++] = d; idx[q++] = c;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setIndex(new THREE.BufferAttribute(idx, 1));
  geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e5);
  const terrain = new THREE.Mesh(geo, new THREE.ShaderMaterial({ uniforms: U, vertexShader: terrainVS, fragmentShader: terrainFS }));
  terrain.frustumCulled = false; scene.add(terrain);

  // sea skirt beyond the data box
  const sea = new THREE.Mesh(new THREE.PlaneGeometry(30000, 30000), new THREE.MeshBasicMaterial({ color: new THREE.Color(0.62, 0.70, 0.80) }));
  sea.rotation.x = -Math.PI / 2; sea.position.y = -0.4; scene.add(sea);

  // sky dome
  const sky = new THREE.Mesh(new THREE.SphereGeometry(15000, 32, 16), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    vertexShader: `varying vec3 vD; void main(){ vD = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader: `varying vec3 vD; void main(){ float y = max(vD.y, 0.0);
      vec3 c = mix(vec3(0.62,0.70,0.80), vec3(0.20,0.36,0.62), pow(y, 0.45));
      c = mix(c, vec3(0.62,0.70,0.80), exp(-y*30.0));
      gl_FragColor = vec4(c, 1.0);
      #include <colorspace_fragment>
    }` }));
  scene.add(sky);

  // route: glow + core fat lines, revealed progressively
  const P3 = R.xyz.map(p => new THREE.Vector3(p[0], p[1] + 0.12, p[2]));
  const flat = []; P3.forEach(p => flat.push(p.x, p.y, p.z));
  const mkLine = (width, color, opacity) => {
    const lg = new LineGeometry(); lg.setPositions(flat);
    const lm = new LineMaterial({ color, linewidth: width, transparent: true, opacity, worldUnits: false, depthTest: true });
    lm.resolution.set(W, H);
    const l = new Line2(lg, lm); l.computeLineDistances(); l.frustumCulled = false; scene.add(l); return l;
  };
  const glowL = mkLine(30, 0xff9a2e, 0.22), midL = mkLine(14, 0xffb347, 0.45), core = mkLine(6.5, 0xfff1c9, 1.0);
  const lines = [glowL, midL, core];

  // head glow sprite
  const gc = document.createElement('canvas'); gc.width = gc.height = 256; const gg = gc.getContext('2d');
  const grd = gg.createRadialGradient(128, 128, 0, 128, 128, 128);
  grd.addColorStop(0, 'rgba(255,255,240,1)'); grd.addColorStop(0.12, 'rgba(255,220,150,0.9)');
  grd.addColorStop(0.35, 'rgba(255,150,50,0.28)'); grd.addColorStop(1, 'rgba(255,120,30,0)');
  gg.fillStyle = grd; gg.fillRect(0, 0, 256, 256);
  const head = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(gc), blending: THREE.AdditiveBlending, depthTest: false, depthWrite: false, transparent: true }));
  scene.add(head);

  const { composer, finish } = (() => {
    const composer = new EffectComposer(renderer); composer.setSize(W, H);
    composer.addPass(new RenderPass(scene, camera));
    composer.addPass(new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.4, 0.5, 0.9));
    composer.addPass(new OutputPass());
    const finish = new ShaderPass(FinishShader); composer.addPass(finish);
    return { composer, finish };
  })();
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;

  return { THREE, scene, camera, composer, finish, U, R, P3, lines, head, sky, W, H, v: new THREE.Vector3() };
}

function routeAt(ctx, f) {
  const { R, P3 } = ctx; const fr = R.frac;
  let lo = 0, hi = fr.length - 1;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (fr[m] < f) lo = m; else hi = m; }
  const t = clamp((f - fr[lo]) / Math.max(1e-9, fr[hi] - fr[lo]));
  return { p: P3[lo].clone().lerp(P3[hi], t), i: lo + t, elev: lerp(R.elev[lo], R.elev[hi], t) };
}

export function update(ctx, t) {
  const { THREE, camera, U, lines, head } = ctx;
  const p = clamp(P(t), 0, 1), tq = clamp(TQ(t), 0, 1), dist = DIST(t);
  const pitch = PITCH(t) * Math.PI / 180, az = AZ(t) * Math.PI / 180;
  const tgt = routeAt(ctx, tq).p;
  // gentle drift so no frame is ever static
  const drift = 0.6 * Math.sin(t * 0.35) * Math.PI / 180;
  const f = new THREE.Vector3(Math.sin(az + drift), 0, -Math.cos(az + drift));
  camera.position.copy(tgt).addScaledVector(f, -dist * Math.cos(pitch)); camera.position.y = tgt.y + dist * Math.sin(pitch);
  camera.near = Math.max(0.02, dist * 0.004); camera.far = dist * 12 + 3000; camera.updateProjectionMatrix();
  camera.lookAt(tgt);
  ctx.sky.position.copy(camera.position); ctx.sky.scale.setScalar(camera.far * 0.85 / 15000);
  U.camPos.value.copy(camera.position);
  U.hazeK.value = 1 / (dist * 5.5 + 40);
  U.snowAmt.value = 0.25 + 0.75 * ease(clamp((t - 24) / 4));
  U.time.value = t;
  const r = routeAt(ctx, p);
  ctx.head.position.copy(r.p); const hs = dist * 0.055 * (1 + 0.08 * Math.sin(t * 6));
  head.scale.set(hs, hs, 1); head.visible = t > 5.6;
  head.material.opacity = clamp((t - 5.6) / 0.6);
  const n = Math.floor(r.i);
  for (const l of lines) l.geometry.instanceCount = Math.max(0, n);
  ctx.finish.uniforms.fade.value = clamp(t / 0.6) * clamp((DURATION - t) / 0.5);
  ctx.state = { p, dist, elev: r.elev };
}

// ---------- 2D overlay ----------
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function project(ctx, v) { const q = v.clone().project(ctx.camera); return [(q.x + 1) / 2 * ctx.W, (1 - q.y) / 2 * ctx.H, q.z]; }
const fmt = n => Math.round(n).toLocaleString('en-US');

export function overlay(ctx, g, t) {
  const { W, H, R } = ctx, { p, elev } = ctx.state;
  g.textBaseline = 'alphabetic';
  // top gradient for legibility
  const tg = g.createLinearGradient(0, 0, 0, 760); tg.addColorStop(0, 'rgba(0,0,0,0.55)'); tg.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = tg; g.fillRect(0, 0, W, 760);
  const bg = g.createLinearGradient(0, H - 700, 0, H); bg.addColorStop(0, 'rgba(0,0,0,0)'); bg.addColorStop(1, 'rgba(0,0,0,0.6)');
  g.fillStyle = bg; g.fillRect(0, H - 700, W, 700);

  // place pins (pop in when the head reaches them)
  for (const m of R.marks) {
    const age = t - (m.frac === 0 ? 6.2 : tAtFrac(m.frac));
    if (age < 0) continue;
    if (t > 36 && m.id === 'Traversette') continue;
    const [x, y, z] = project(ctx, new ctx.THREE.Vector3(...R.xyz[m.i]).setY(R.xyz[m.i][1] + 0.05));
    if (z > 1 || x < -200 || x > W + 200 || y < 0 || y > H) continue;
    const s = easeOutBack(clamp(age / 0.55));
    const recent = 1 - 0.35 * clamp((age - 3.5) / 1.5);
    g.save(); g.globalAlpha = clamp(age / 0.25) * recent;
    // stem + dot
    const stem = 92 * s;
    g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 3; g.beginPath(); g.moveTo(x, y); g.lineTo(x, y - stem); g.stroke();
    g.fillStyle = '#fff'; g.beginPath(); g.arc(x, y, 9 * s, 0, 7); g.fill();
    g.fillStyle = '#ffb347'; g.beginPath(); g.arc(x, y, 5 * s, 0, 7); g.fill();
    // label pill
    g.font = '34px YTSans'; const tw = g.measureText(m.label).width;
    const bw = tw + 44, bh = 62, bx = clamp(x - bw / 2, 30, W - 30 - bw), by = y - stem - bh;
    g.translate(x, y - stem); g.scale(s, s); g.translate(-x, -(y - stem));
    g.shadowColor = 'rgba(0,0,0,0.45)'; g.shadowBlur = 18; g.shadowOffsetY = 4;
    g.fillStyle = 'rgba(255,255,255,0.96)'; rr(g, bx, by, bw, bh, 31); g.fill(); g.shadowColor = 'transparent';
    g.fillStyle = '#121212'; g.textAlign = 'center'; g.fillText(m.label, bx + bw / 2, by + 44);
    g.restore();
  }

  // kicker + caption
  g.textAlign = 'center';
  const kA = clamp(t / 0.5) * clamp((DURATION - t) / 0.4);
  g.globalAlpha = kA; g.font = '30px YTSans'; g.fillStyle = '#ffb347';
  g.letterSpacing = '8px'; g.fillText('HANNIBAL  ·  ON A REAL MAP', W / 2, 250); g.letterSpacing = '0px';
  g.globalAlpha = 1;
  for (const [a, b, l1, l2] of CAPTIONS) {
    if (t < a || t > b) continue;
    const ia = easeOut(clamp((t - a) / 0.45)), oa = 1 - clamp((t - (b - 0.35)) / 0.35);
    g.save(); g.globalAlpha = ia * oa; g.translate(0, (1 - ia) * 28);
    g.shadowColor = 'rgba(0,0,0,0.65)'; g.shadowBlur = 24; g.shadowOffsetY = 3;
    g.fillStyle = '#fff'; g.font = '78px YTSans';
    g.fillText(l1, W / 2, 360); if (l2) g.fillText(l2, W / 2, 452);
    g.restore();
  }

  // HUD stats panel
  const hudA = easeOut(clamp((t - 6.4) / 0.6)) * clamp((DURATION - t) / 0.5);
  if (hudA > 0) {
    const day = interp(p, [0, 0.31, 0.54, 0.742, 0.86, 1], [0, 38, 77, 112, 140, 158]);
    const army = interp(p, [0, 0.535, 0.545, 0.738, 0.748, 0.86, 1], [102000, 102000, 59000, 59000, 46000, 46000, 26000]);
    const km = p * 1500;
    const x0 = 60, y0 = H - 400, w = W - 120, h = 196;
    g.save(); g.globalAlpha = hudA; g.translate(0, (1 - hudA) * 40);
    g.shadowColor = 'rgba(0,0,0,0.4)'; g.shadowBlur = 30;
    g.fillStyle = 'rgba(12,14,18,0.72)'; rr(g, x0, y0, w, h, 34); g.fill(); g.shadowColor = 'transparent';
    g.strokeStyle = 'rgba(255,255,255,0.12)'; g.lineWidth = 2; rr(g, x0, y0, w, h, 34); g.stroke();
    const cols = [['DISTANCE', fmt(km), 'km'], ['ALTITUDE', fmt(Math.round(elev / 10) * 10), 'm'], ['ARMY', fmt(army), ''], ['ELEPHANTS', '37', '']];
    const cw = w / 4;
    cols.forEach(([lab, val, unit], i) => {
      const cx = x0 + cw * i + cw / 2;
      g.textAlign = 'center'; g.font = '24px Pret'; g.fillStyle = 'rgba(255,255,255,0.6)'; g.letterSpacing = '3px';
      g.fillText(lab, cx, y0 + 66); g.letterSpacing = '0px';
      g.font = '56px YTSans'; g.fillStyle = i === 2 && armyFlash(t) > 0 ? mixCol(armyFlash(t)) : '#fff';
      g.fillText(val, cx - (unit ? 18 : 0), y0 + 140);
      if (unit) { g.font = '26px Pret'; g.fillStyle = '#ffb347'; g.textAlign = 'left'; g.fillText(unit, cx + g.measureText(val).width / 2 + 4 - 18 + 30, y0 + 140); }
      if (i) { g.fillStyle = 'rgba(255,255,255,0.1)'; g.fillRect(x0 + cw * i, y0 + 40, 2, h - 80); }
    });
    // army loss tags
    for (const [ta, txt] of DROPS) {
      const a = t - ta; if (a < 0 || a > 2.2) continue;
      g.globalAlpha = hudA * clamp(a / 0.2) * (1 - clamp((a - 1.6) / 0.6));
      g.font = '40px YTSans'; g.fillStyle = '#ff5a4e'; g.textAlign = 'center';
      g.fillText(txt, x0 + cw * 2.5, y0 - 26 - a * 26);
    }
    g.restore();
  }

  // elevation profile through the Alps
  const eA = easeOut(clamp((t - 25.2) / 0.6)) * (1 - clamp((t - 35.2) / 0.6));
  if (eA > 0) {
    const x0 = 60, y0 = H - 640, w = W - 120, h = 210, f0 = 0.80;
    g.save(); g.globalAlpha = eA; g.translate(0, (1 - eA) * 30);
    g.fillStyle = 'rgba(12,14,18,0.6)'; rr(g, x0, y0, w, h, 28); g.fill();
    const fr = R.frac, el = R.elev, i0 = fr.findIndex(f => f >= f0);
    const X = f => x0 + 40 + (f - f0) / (1 - f0) * (w - 80), Y = e => y0 + h - 34 - e / 3200 * (h - 70);
    const ip = Math.floor(ctx.state ? routeAt(ctx, p).i : 0);
    // full profile faint, travelled part bright
    const path = (to) => { g.beginPath(); g.moveTo(X(fr[i0]), Y(0)); for (let i = i0; i <= to; i += 2) g.lineTo(X(fr[i]), Y(el[i])); g.lineTo(X(fr[to]), Y(0)); g.closePath(); };
    path(el.length - 1); g.fillStyle = 'rgba(255,255,255,0.08)'; g.fill();
    if (ip > i0) {
      path(ip); const gr = g.createLinearGradient(0, y0, 0, y0 + h); gr.addColorStop(0, 'rgba(255,179,71,0.75)'); gr.addColorStop(1, 'rgba(255,179,71,0.05)');
      g.fillStyle = gr; g.fill();
      const hx = X(fr[ip]), hy = Y(el[ip]);
      g.fillStyle = '#fff'; g.beginPath(); g.arc(hx, hy, 8, 0, 7); g.fill();
      g.font = '34px YTSans'; g.textAlign = hx > x0 + w - 220 ? 'right' : 'left';
      g.fillText(fmt(Math.round(elev / 10) * 10) + ' m', hx + (g.textAlign === 'right' ? -16 : 16), Math.max(y0 + 44, hy - 14));
    }
    g.font = '22px Pret'; g.fillStyle = 'rgba(255,255,255,0.55)'; g.textAlign = 'left'; g.letterSpacing = '3px';
    g.fillText('ELEVATION', x0 + 30, y0 + 40); g.letterSpacing = '0px';
    g.restore();
  }
  g.globalAlpha = 1;
}

// time at which the head reaches route fraction f (numeric inverse of P)
const _tf = new Map();
function tAtFrac(f) {
  if (_tf.has(f)) return _tf.get(f);
  let t = 0; while (t < DURATION && P(t) < f - 1e-4) t += 0.01;
  _tf.set(f, t); return t;
}
const DROPS = [];

function armyFlash(t) { for (const [ta] of DROPS) { const a = t - ta; if (a >= 0 && a < 1.2) return 1 - a / 1.2; } return 0; }
function mixCol(k) { const r = 255, gg = Math.round(255 - 165 * k), b = Math.round(255 - 177 * k); return `rgb(${r},${gg},${b})`; }
// army drops happen when the head passes the Pyrenees and the Rhône; the Alps losses roll continuously
DROPS.push([tAtFrac(0.537), '−43,000'], [tAtFrac(0.74), '−13,000']);

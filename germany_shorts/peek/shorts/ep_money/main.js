// PEEK. Short: where did $2.8 trillion go in one day? (neutral, economics only)
// One deterministic timeline: window.render(t) draws the frame for time t (seconds).
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { mulberry32, buildTower, setTower, buildDust, buildLooseBills, setLooseBills } from './money.js';
import { TextLayer } from './text.js';
import { buildEarth, setEarth, ISS_ALT, STACK } from './earth.js';
import { buildBlock, setBlock, buildTag, paintTag, hangTag, CP } from './stock.js';

const q = new URLSearchParams(location.search);
const W = +q.get('w') || 1080, H = +q.get('h') || 1920;
window.DUR = 44;

// ---------- renderer ----------
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.45;
const BG = 0x03050a;
const bgTex = (() => {
  const c = document.createElement('canvas'); c.width = 540; c.height = 960;
  const g = c.getContext('2d');
  const r = g.createRadialGradient(270, 430, 0, 270, 430, 640);
  r.addColorStop(0, '#18202e'); r.addColorStop(0.45, '#0a0e16'); r.addColorStop(1, '#020306');
  g.fillStyle = r; g.fillRect(0, 0, 540, 960);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
scene.background = bgTex;
const fog = new THREE.Fog(BG, 34, 80);
scene.fog = fog;

const camera = new THREE.PerspectiveCamera(30, W / H, 0.1, 300);

// ---------- studio: glossy dark floor, one spotlight pool ----------
const FLOOR_Y = 0;
const mirror = new Reflector(new THREE.PlaneGeometry(200, 200), { textureWidth: W / 2, textureHeight: H / 2, color: 0x2e2e2e, clipBias: 0.003 });
mirror.rotation.x = -Math.PI / 2; mirror.position.y = FLOOR_Y;
// three's Reflector overlay-blends the reflection, which shifts colours (mustard turns red); multiply instead
mirror.material.fragmentShader = mirror.material.fragmentShader.replace('blendOverlay( base.rgb, color )', 'base.rgb * color');
mirror.material.uniforms.color.value.setRGB(0.28, 0.28, 0.28);
mirror.material.needsUpdate = true;
scene.add(mirror);
const veilTex = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 1024;
  const g = c.getContext('2d');
  const r = g.createRadialGradient(512, 512, 0, 512, 512, 512);
  r.addColorStop(0, 'rgba(14,16,21,0.66)'); r.addColorStop(0.22, 'rgba(10,12,16,0.80)'); r.addColorStop(0.55, 'rgba(4,5,8,0.96)'); r.addColorStop(1, 'rgba(2,3,5,1)');
  g.fillStyle = r; g.fillRect(0, 0, 1024, 1024);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
const veil = new THREE.Mesh(new THREE.PlaneGeometry(90, 90), new THREE.MeshBasicMaterial({ map: veilTex, transparent: true, depthWrite: false }));
veil.rotation.x = -Math.PI / 2; veil.position.y = FLOOR_Y + 0.002;
scene.add(veil);
const shadowCatcher = new THREE.Mesh(new THREE.PlaneGeometry(90, 90), new THREE.ShadowMaterial({ opacity: 0.6 }));
shadowCatcher.rotation.x = -Math.PI / 2; shadowCatcher.position.y = FLOOR_Y + 0.004; shadowCatcher.receiveShadow = true;
scene.add(shadowCatcher);

const key = new THREE.SpotLight(0xfff0dc, 5200, 0, 0.42, 0.85, 2);
key.position.set(5, 30, 16);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.bias = -0.0004; key.shadow.normalBias = 0.03; key.shadow.radius = 6;
key.shadow.camera.near = 10; key.shadow.camera.far = 80;
scene.add(key, key.target);
const rim = new THREE.DirectionalLight(0xcfe0ff, 1.5);
rim.position.set(-10, 8, -10);
scene.add(rim);
const rim2 = new THREE.DirectionalLight(0xffe2c8, 0.8);
rim2.position.set(10, 5, -7);
scene.add(rim2);

// ---------- the cash: a skyline of $100-bill towers; the hero tower stands in front ----------
export const BLOOM = 1;
const ONLY = q.get('only');
const CITY = [{ x: 0, z: 0, layers: 104, win: 30, dust: 4, every: 1, seed: 1 }];
{
  // rows behind the hero, lower in front and taller toward the back, like a skyline
  const rnd = mulberry32(4242);
  const ROWS = [
    { z: 0.5, xs: [-9.5, 9.5, -19, 19], lo: 38, hi: 58 },
    { z: -10, xs: [-14, -4.6, 4.6, 14, -23.5, 23.5], lo: 52, hi: 80 },
    { z: -20.5, xs: [-19, -9.5, 0, 9.5, 19, -28.5, 28.5], lo: 64, hi: 100 },
    { z: -31, xs: [-23.5, -14, -4.6, 4.6, 14, 23.5], lo: 76, hi: 118 },
    { z: -41.5, xs: [-19, -9.5, 0, 9.5, 19], lo: 88, hi: 130 },
  ];
  for (const R of ROWS) for (const x0 of R.xs) {
    const x = x0 + (rnd() - 0.5) * 1.0, z = R.z - rnd() * 1.2;
    const dist = Math.hypot(x, z);
    const layers = Math.round(R.lo + rnd() * (R.hi - R.lo));
    CITY.push({ x, z, layers, win: dist < 15 ? 20 : 0, dust: dist < 22 ? 2 : 1, every: dist < 22 ? 1 : 3, seed: 10 + CITY.length });
  }
}
const cash = new THREE.Group();
scene.add(cash);
const towers = CITY.filter((T, i) => !ONLY || i === 0).map(T => {
  const dist = Math.hypot(T.x, T.z);
  const tw = buildTower({ nx: 4, nz: 6, layers: T.layers, seed: T.seed * 1000 + 7, t0: 0.12 + dist * 0.012, span: 1.7 + T.layers * 0.002, noise: T.win ? 0.3 : 0.12, win: T.win });
  tw.root.position.set(T.x, FLOOR_Y, T.z);
  tw.T = T;
  cash.add(tw.root);
  const d = buildDust(tw, { perBundle: T.dust, every: T.every, seed: T.seed * 31 });
  d.points.position.copy(tw.root.position);
  d.points.layers.enable(BLOOM);
  cash.add(d.points);
  tw.dust = d;
  return tw;
});
const hero = towers[0];
const loose = buildLooseBills(hero, { count: 110 });
loose.mesh.position.copy(hero.root.position);
cash.add(loose.mesh);

// ---------- Earth ----------
const manager = new THREE.LoadingManager();
const texReady = new Promise((res, rej) => { manager.onLoad = res; manager.onError = u => rej(new Error('texture failed: ' + u)); });
const loader = new THREE.TextureLoader(manager);
const E = buildEarth(loader, { dayUrl: 'assets/earth_day_3840.jpg', nightUrl: 'assets/earth_night_3840.jpg' });
scene.add(E.root);

// ---------- one stock: 243 share cubes (1 cube = 100 million shares) and a price tag ----------
const B = buildBlock({ nx: 9, ny: 9, nz: 3 });
scene.add(B.root);
const TAG = buildTag();
scene.add(TAG.root, TAG.str);

// which set of objects each shot shows
const SETS = {
  studio: [cash, mirror, veil, shadowCatcher],
  space: [E.root],
  stock: [B.root, TAG.root, TAG.str, mirror, veil, shadowCatcher],
};
let mirrorOn = true, curFog = fog, curBg = bgTex;
function show(name) {
  for (const [k, arr] of Object.entries(SETS)) for (const o of arr) o.visible = (k === name);
  mirrorOn = name === 'studio' || name === 'stock';
  curFog = name === 'space' ? null : fog;
  curBg = name === 'space' ? SPACE_BG : bgTex;
  scene.fog = curFog; scene.background = curBg;
  key.visible = name !== 'space';
  rim.intensity = name === 'space' ? 0.0 : 1.5; rim2.intensity = name === 'space' ? 0.0 : 0.8;
  sunLight.visible = name === 'space';
}
const SPACE_BG = new THREE.Color(0x000002);
const sunLight = new THREE.DirectionalLight(0xfff4e6, 2.2);
sunLight.position.copy(E.sun.value).multiplyScalar(100);
scene.add(sunLight);

// ---------- post: selective bloom (only things on the BLOOM layer glow) ----------
const bloomLayer = new THREE.Layers(); bloomLayer.set(BLOOM);
const darkMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
const saved = new Map();
const darken = o => { if ((o.isMesh || o.isPoints || o.isLine || o.isSprite) && !bloomLayer.test(o.layers)) { saved.set(o, o.material); o.material = o.userData.bloomMat || (Array.isArray(o.material) ? o.material.map(() => darkMat) : darkMat); } };
const restore = o => { if (saved.has(o)) { o.material = saved.get(o); saved.delete(o); } };

const bloomComposer = new EffectComposer(renderer);
bloomComposer.renderToScreen = false;
bloomComposer.setPixelRatio(1); bloomComposer.setSize(W, H);
bloomComposer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 1.1, 0.5, 0.0);
bloomComposer.addPass(bloom);

const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 });
const composer = new EffectComposer(renderer, rt);
composer.setPixelRatio(1); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
const mix = new ShaderPass({
  uniforms: { baseTexture: { value: null }, bloomTexture: { value: bloomComposer.renderTarget2.texture }, uBloom: { value: 1.0 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
  fragmentShader: 'uniform sampler2D baseTexture, bloomTexture; uniform float uBloom; varying vec2 vUv; void main(){ gl_FragColor = texture2D(baseTexture, vUv) + uBloom * texture2D(bloomTexture, vUv); }',
}, 'baseTexture');
mix.needsSwap = true;
composer.addPass(mix);
composer.addPass(new OutputPass());
const finish = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, uTime: { value: 0 }, uVig: { value: 0.4 }, uGrain: { value: 0.02 }, uFlash: { value: 0 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform float uTime, uVig, uGrain, uFlash; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + uTime*61.7) * 43758.5453); }
    void main(){ vec4 c = texture2D(tDiffuse, vUv);
      vec2 d = vUv - 0.5; d.x *= 0.5625; float v = smoothstep(0.75, 0.18, length(d));
      c.rgb *= mix(1.0 - uVig, 1.0, v);
      c.rgb += (h(vUv * vec2(1080.0,1920.0)) - 0.5) * uGrain;
      c.rgb = mix(c.rgb, vec3(1.0), uFlash);
      gl_FragColor = c; }`,
});
composer.addPass(finish);

function draw() {
  const bg = scene.background; scene.background = null; scene.fog = null; mirror.visible = false;
  scene.traverse(darken);
  bloomComposer.render();
  scene.traverse(restore);
  scene.background = bg; scene.fog = curFog; mirror.visible = mirrorOn;
  composer.render();
}

// ---------- text ----------
const text = new TextLayer(document.getElementById('ov'), W, H);

// ---------- helpers ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const easeOut = k => 1 - Math.pow(1 - clamp(k), 3);
const easeInOut = k => { k = clamp(k); return k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; };
const seg = (t, a, b) => clamp((t - a) / (b - a));
function setNearFar(n, f) {
  if (camera.near !== n || camera.far !== f) { camera.near = n; camera.far = f; camera.updateProjectionMatrix(); }
}
function setFov(v) { if (camera.fov !== v) { camera.fov = v; camera.updateProjectionMatrix(); } }
function shake(t, amp) {
  return new THREE.Vector3(
    amp * (Math.sin(t * 91.0) * 0.6 + Math.sin(t * 57.3 + 1.3) * 0.4),
    amp * (Math.sin(t * 77.0 + 0.7) * 0.6 + Math.sin(t * 43.1 + 2.1) * 0.4), 0);
}

// ---------- shots ----------
// Shot A (0 - 2.8 s): the cover. A skyline of cash; from 0.12 s it burns away from the top down.
function shotCover(t) {
  show('studio'); fog.near = +(q.get('fn') ?? 44); fog.far = +(q.get('ff') ?? 78); setNearFar(0.5, 300); setFov(30);
  for (const tw of towers) {
    setTower(tw, t);
    tw.dust.mat.uniforms.uTime.value = t;
    tw.dust.mat.uniforms.uScale.value = 520;
  }
  setLooseBills(loose, t, FLOOR_Y);
  const push = easeInOut(seg(t, 0.0, 2.8));
  const C = { px: +(q.get('px') ?? 4), py: +(q.get('py') ?? 38), pz: +(q.get('pz') ?? 31), ly: +(q.get('ly') ?? 2.5), lz: +(q.get('lz') ?? -9) };
  const camPos = new THREE.Vector3(lerp(C.px, C.px * 0.6, push), lerp(C.py, C.py * 0.92, push), lerp(C.pz, C.pz * 0.9, push));
  camPos.add(shake(t, 0.06 * Math.exp(-Math.max(0, t - 0.12) * 5) * (t > 0.1 ? 1 : 0)));
  camera.position.copy(camPos);
  camera.lookAt(0, C.ly, C.lz);
  key.position.set(7, 40, 20); key.angle = +(q.get('ka') ?? 0.42); key.penumbra = 0.9; key.intensity = +(q.get('ki') ?? 9000);
  key.target.position.set(0, 4, -3);
  finish.uniforms.uFlash.value = t > 0.10 ? 0.22 * Math.exp(-(t - 0.10) * 14) : 0;
  const pop = 1 + 0.06 * Math.exp(-Math.max(0, t - 0.12) * 6) * (t > 0.1 ? 1 : 0);
  text.set('n', { text: '$2.8', y: 250, size: 300, color: '#FFD23F', scale: pop });
  text.set('u', { text: 'TRILLION', y: 535, size: 150, color: '#ffffff', scale: pop });
}

// Shot B (2.8 - 7.4 s): the same money as one stack of $100 notes, rising from the U.S. past the space station.
let lastN = 0;
function shotSpace(t) {
  show('space'); setFov(35);
  const k = easeInOut(seg(t, 0.1, 3.1));
  const h = STACK * k;
  const z = easeInOut(seg(t, 0.0, 3.3));
  const dist = 48 * Math.pow(128 / 48, z) * (1 + 0.03 * seg(t, 3.3, 4.6));
  const el = THREE.MathUtils.degToRad(lerp(15, 20, z)), az = THREE.MathUtils.degToRad(lerp(-9, 5, seg(t, 0, 4.6)));
  const tgt = new THREE.Vector3(0, lerp(2.5, 14, z), 0);
  camera.position.set(tgt.x + dist * Math.sin(az) * Math.cos(el), tgt.y + dist * Math.sin(el), tgt.z + dist * Math.cos(az) * Math.cos(el));
  camera.lookAt(tgt);
  setNearFar(1, 4000);
  setEarth(E, { h, camera, ringOp: easeOut(seg(t, 0.2, 0.9)) });
  const n = Math.min(7, Math.floor(h / ISS_ALT + 1e-6));
  if (n >= 1) {
    // each new multiple pops a little
    let tn = 0.1; for (let j = 0; j < 60; j++) { const tt = t - j / 30; if (tt < 0) break; const kk = easeInOut(seg(tt, 0.1, 3.1)); if (Math.floor(STACK * kk / ISS_ALT + 1e-6) < n) { tn = j / 30; break; } }
    text.set('x', { text: n + '\u00D7', y: 250, size: 330, color: '#FFD23F', scale: 1 + 0.12 * Math.exp(-tn * 9) });
  }
  // the station gets its name next to it
  camera.updateMatrixWorld();
  const sp = E.iss.getWorldPosition(new THREE.Vector3()).project(camera);
  const sx = (sp.x * 0.5 + 0.5) * W, sy = (-sp.y * 0.5 + 0.5) * H;
  const la = easeOut(seg(t, 0.5, 0.9));
  // label sits above the station, between the column and the Shorts button column (x <= 900)
  const cx = Math.min(900 - 135, Math.max(W / 2 + 165, sx + 40));
  text.set('iss', { text: 'SPACE\nSTATION', y: sy - 170, x: 2 * cx - W, size: 62, color: '#ffffff', opacity: la });
}

// Shot E (11.2 - 15.4 s): inside one stock. The price on the tag falls from $200 to $181.
function shotStock(t) {
  show('stock'); fog.near = 60; fog.far = 120; setNearFar(0.5, 300); setFov(30);
  setBlock(B, {});
  const az = THREE.MathUtils.degToRad(lerp(33, 39, seg(t, 0, 4.2))), el = THREE.MathUtils.degToRad(18);
  const dist = lerp(45, 42, easeInOut(seg(t, 0, 4.2)));
  const tgt = new THREE.Vector3(0.9, 6.3, 0);
  camera.position.set(tgt.x + dist * Math.sin(az) * Math.cos(el), tgt.y + dist * Math.sin(el), tgt.z + dist * Math.cos(az) * Math.cos(el));
  camera.lookAt(tgt);
  key.position.set(-6, 34, 22); key.angle = 0.5; key.penumbra = 0.9; key.intensity = 6500; key.target.position.set(0, 4, 0);
  // the tag hangs off the top front-right corner and turns to face the camera
  const attach = new THREE.Vector3(B.W / 2 - 0.45, B.H + 0.05, B.D / 2 - 0.45);
  const sw = 0.05 * Math.sin(t * 2.1) * Math.exp(-t * 0.4);
  hangTag(TAG, attach, new THREE.Vector3(B.W / 2 - 0.2, B.H - 3.0, B.D / 2 + 1.5), az - 0.12, sw);
  const k = seg(t, 1.2, 1.7);
  if (t < 1.2) paintTag(TAG, { now: '$200' });
  else paintTag(TAG, { old: '$200', now: '$181', strike: easeOut(k), nowColor: '#e0262b' });
  const a = easeOut(seg(t, 2.2, 2.5));
  text.set('loss', { text: '-$447B', y: 250, size: 270, color: '#FF4040', opacity: a, scale: 0.9 + 0.1 * a });
}

const SHOTS = [
  [0, 2.8, shotCover],
  [2.8, 7.4, shotSpace],
  [11.2, 15.4, shotStock],
];

window.render = async function (t) {
  text.begin();
  let s = SHOTS[0];
  for (const x of SHOTS) if (t >= x[0]) s = x;
  s[2](t - s[0], t);
  finish.uniforms.uTime.value = Math.floor(t * 30) / 30;
  draw();
  text.end();
};

(async () => {
  try {
    await document.fonts.load('100px YTS');
    await document.fonts.ready;
    await texReady;
    await window.render(0);
    window.READY = true;
  } catch (e) { window.ERROR = String(e && e.stack || e); }
})();

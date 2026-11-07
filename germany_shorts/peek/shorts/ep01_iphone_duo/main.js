// PEEK. Short 01: why the $1,999 folding iPhone keeps cracking in the same spot.
// One deterministic timeline: window.render(t) draws the frame for time t (seconds).
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { PHONE, buildPhone, setFold, paintScreen, crackGlowTexture } from './phone.js';
import { TextLayer } from './text.js';
import { buildGrid } from './grid.js';

const q = new URLSearchParams(location.search);
const W = +q.get('w') || 1080, H = +q.get('h') || 1920;
window.DUR = 49;

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
scene.environmentIntensity = 0.5;
const BG = 0x020203;
const bgTex = (() => {
  const c = document.createElement('canvas'); c.width = 540; c.height = 960;
  const g = c.getContext('2d');
  const r = g.createRadialGradient(270, 520, 0, 270, 520, 620);
  r.addColorStop(0, '#1a1f2b'); r.addColorStop(0.5, '#090b10'); r.addColorStop(1, '#020203');
  g.fillStyle = r; g.fillRect(0, 0, 540, 960);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
scene.background = bgTex;
const fog = new THREE.Fog(BG, 30, 52);
scene.fog = fog;

const camera = new THREE.PerspectiveCamera(26, W / H, 0.1, 200);

// ---------- studio: dark floor, one spotlight pool ----------
// glossy black floor: a dim mirror under a dark gradient veil, plus a soft contact shadow
const FLOOR_Y = -2.75;
const mirror = new Reflector(new THREE.PlaneGeometry(120, 120), { textureWidth: W / 2, textureHeight: H / 2, color: 0x343434, clipBias: 0.003 });
mirror.rotation.x = -Math.PI / 2; mirror.position.y = FLOOR_Y;
scene.add(mirror);
const veilTex = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 1024;
  const g = c.getContext('2d');
  const r = g.createRadialGradient(512, 512, 0, 512, 512, 512);
  r.addColorStop(0, 'rgba(14,15,19,0.70)'); r.addColorStop(0.2, 'rgba(10,11,14,0.82)'); r.addColorStop(0.5, 'rgba(4,4,6,0.96)'); r.addColorStop(1, 'rgba(2,2,3,1)');
  g.fillStyle = r; g.fillRect(0, 0, 1024, 1024);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
const veil = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshBasicMaterial({ map: veilTex, transparent: true, depthWrite: false }));
veil.rotation.x = -Math.PI / 2; veil.position.y = FLOOR_Y + 0.002;
scene.add(veil);
const shadowCatcher = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.ShadowMaterial({ opacity: 0.55 }));
shadowCatcher.rotation.x = -Math.PI / 2; shadowCatcher.position.y = FLOOR_Y + 0.004; shadowCatcher.receiveShadow = true;
scene.add(shadowCatcher);

const key = new THREE.SpotLight(0xfff1e2, 1400, 0, 0.32, 0.95, 2);
key.position.set(2.5, 16, 7);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02; key.shadow.radius = 8;
key.shadow.camera.near = 4; key.shadow.camera.far = 40;
scene.add(key, key.target);
const rim = new THREE.DirectionalLight(0xcfe0ff, 1.6);
rim.position.set(-8, 5, -9);
scene.add(rim);
const rim2 = new THREE.DirectionalLight(0xffe2c8, 0.9);
rim2.position.set(9, 3, -6);
scene.add(rim2);

// ---------- phone ----------
const phone = buildPhone();
scene.add(phone.root);

const grid = buildGrid(FLOOR_Y);
scene.add(grid.root);
grid.glows.forEach(g => g.layers.enable(1));

// which set of objects each shot shows
const SETS = {
  studio: [phone.root, mirror, veil, shadowCatcher],
  grid: [grid.root],
};
function show(name) {
  for (const [k, arr] of Object.entries(SETS)) for (const o of arr) o.visible = (k === name);
  mirrorOn = name === 'studio';
}
let mirrorOn = true;

// ---------- post: selective bloom (only things on the BLOOM layer glow) ----------
export const BLOOM = 1;
const bloomLayer = new THREE.Layers(); bloomLayer.set(BLOOM);
phone.glow.layers.enable(BLOOM);
const darkMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
const saved = new Map();
const darken = o => { if ((o.isMesh || o.isPoints || o.isLine) && !bloomLayer.test(o.layers)) { saved.set(o, o.material); o.material = Array.isArray(o.material) ? o.material.map(() => darkMat) : darkMat; } };
const restore = o => { if (saved.has(o)) { o.material = saved.get(o); saved.delete(o); } };

const bloomComposer = new EffectComposer(renderer);
bloomComposer.renderToScreen = false;
bloomComposer.setPixelRatio(1); bloomComposer.setSize(W, H);
bloomComposer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 1.25, 0.55, 0.0);
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
  uniforms: { tDiffuse: { value: null }, uTime: { value: 0 }, uVig: { value: 0.38 }, uGrain: { value: 0.02 }, uFlash: { value: 0 } },
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
  scene.background = bg; scene.fog = fog; mirror.visible = mirrorOn;
  composer.render();
}

// ---------- text ----------
const text = new TextLayer(document.getElementById('ov'), W, H);

// ---------- helpers ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const smooth = k => { k = clamp(k); return k * k * (3 - 2 * k); };
const easeOut = k => 1 - Math.pow(1 - clamp(k), 3);
const easeInOut = k => { k = clamp(k); return k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; };
const seg = (t, a, b) => clamp((t - a) / (b - a));

function setNearFar(n, f) {
  if (camera.near !== n || camera.far !== f) { camera.near = n; camera.far = f; camera.updateProjectionMatrix(); }
}

// deterministic camera shake (sum of sines, no randomness)
function shake(t, amp) {
  return new THREE.Vector3(
    amp * (Math.sin(t * 91.0) * 0.6 + Math.sin(t * 57.3 + 1.3) * 0.4),
    amp * (Math.sin(t * 77.0 + 0.7) * 0.6 + Math.sin(t * 43.1 + 2.1) * 0.4),
    0);
}

// ---------- shots ----------
// Shot A (0 - 2.8 s): the cover. Open phone tilted toward us, crack along the lower crease, "$1,999".
function shotCover(t) {
  show('studio'); fog.near = 30; fog.far = 52; setNearFar(0.5, 200); key.angle = 0.32; key.intensity = 1400; key.position.set(2.5, 16, 7);
  setFold(phone, 0.16);
  phone.root.position.set(0, -0.2, 0);
  phone.root.rotation.set(-0.42, 0.0, 0.0);
  phone.root.rotateY(-0.10);
  phone.root.rotateZ(0.03);
  // crack is already there at frame 0 (cover); at 0.12 s it bursts further
  const burst = easeOut(seg(t, 0.10, 0.55));
  phone.setCrack(0.86 + 0.14 * burst, 0.4 + 1.6 * Math.exp(-Math.max(0, t - 0.12) * 4.0) * (t > 0.1 ? 1 : 0), 1);
  const push = easeInOut(seg(t, 0.3, 2.8));
  const camPos = new THREE.Vector3(lerp(0.0, 0.2, push), lerp(2.6, 2.1, push), lerp(27.0, 23.5, push));
  camPos.add(shake(t, 0.11 * Math.exp(-Math.max(0, t - 0.12) * 5) * (t > 0.1 ? 1 : 0)));
  camera.position.copy(camPos);
  camera.lookAt(0, -0.75, 0);
  if (q.get('cam') === 'close') { camera.position.set(0.4, 0.3, 6); camera.lookAt(0, -0.6, 0); }
  key.target.position.set(0, -0.5, 0);
  finish.uniforms.uFlash.value = t > 0.10 ? 0.35 * Math.exp(-(t - 0.10) * 14) : 0;
  text.set('price', { text: '$1,999', y: 215, size: 270, color: '#FFD23F', scale: 1 + 0.08 * Math.exp(-Math.max(0, t - 0.12) * 6) * (t > 0.1 ? 1 : 0) });
}

// Shot C (8.6 - 12.7 s): pull back from one cracked phone to a whole field of them. Only a few are broken.
function shotGrid(t) {
  show('grid'); fog.near = 400; fog.far = 600;
  key.position.set(10, 60, 30); key.angle = 0.9; key.intensity = 9000; key.target.position.set(0, FLOOR_Y, 0);
  const k = easeInOut(seg(t, 0.15, 2.9));
  const d = 7.2 * Math.pow(150 / 7.2, k) * (1 + 0.05 * seg(t, 2.9, 4.2));
  const el = lerp(1.25, 1.0, k), az = lerp(-0.15, -0.5, k);
  const tgt = new THREE.Vector3(lerp(0, 0.0, k), FLOOR_Y, lerp(0, 0.0, k));
  camera.position.set(tgt.x + d * Math.cos(el) * Math.sin(az), tgt.y + d * Math.sin(el), tgt.z + d * Math.cos(el) * Math.cos(az));
  camera.lookAt(tgt);
  setNearFar(Math.max(0.1, d * 0.3), d + 250);
  grid.glowMat.color.setScalar(3.0 + 3.0 * k);
  grid.haloMat.color.setScalar(1.1 * k * k);
  grid.screenMat.emissiveIntensity = lerp(0.55, 0.32, k);
  const a = easeOut(seg(t, 0.55, 0.85));
  text.set('quote', { text: '\u201CA SMALL\nNUMBER\u201D', y: 210, size: 190, color: '#ffffff', opacity: a, scale: 0.9 + 0.1 * a });
}

const SHOTS = [
  [0, 2.8, shotCover],
  [8.6, 12.7, shotGrid],
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
    await window.render(0);
    window.READY = true;
  } catch (e) { window.ERROR = String(e && e.stack || e); }
})();

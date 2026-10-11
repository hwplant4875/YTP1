// Shorts end card: the ORBIS x-ray globe (amber), framed for any aspect ratio, sitting in the upper half so the
// wordmark text (ASS overlay) fits below it. Slow push-in and spin.
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { makeGlobe } from './logo_orbis.js';

const P = { solid: 0x140a03, strata: [0x3a1f08, 0x5a300c, 0x8a4c14], rim: [1.0, 0.72, 0.35], bg: '#050302', bg2: '#22130a', line: 0xffe2b8 };

export async function setup(THREE, renderer, W, H) {
  const scene = new THREE.Scene();
  const c = document.createElement('canvas'); c.width = 512; c.height = Math.round(512 * H / W);
  const g = c.getContext('2d'), grd = g.createRadialGradient(256, c.height * 0.36, 10, 256, c.height * 0.4, c.height * 0.55);
  grd.addColorStop(0, P.bg2); grd.addColorStop(1, P.bg); g.fillStyle = grd; g.fillRect(0, 0, c.width, c.height);
  scene.background = new THREE.CanvasTexture(c); scene.background.colorSpace = THREE.SRGBColorSpace;
  const camera = new THREE.PerspectiveCamera(24, W / H, 0.1, 100);
  const globe = makeGlobe(THREE, P); globe.rotation.set(0.38, 0.62, -0.1); scene.add(globe);
  const composer = new EffectComposer(renderer); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.6, 0.5, 0.5));
  composer.addPass(new OutputPass());
  // distance so the globe (radius 1) spans ~62% of the frame width
  const halfW = Math.tan(12 * Math.PI / 180) * W / H;
  const dist = 1 / (0.62 * halfW);
  return { scene, camera, composer, globe, dist, halfH: Math.tan(12 * Math.PI / 180) };
}

export function update(ctx, t) {
  const k = 1 - Math.exp(-t / 1.2);
  const d = ctx.dist * (1.12 - 0.12 * k);
  // look below the globe so it sits at ~34% from the top
  const off = d * ctx.halfH * 0.32;
  ctx.camera.position.set(0.19 * d, 0.15 * d - 0.0 + off * 0, d);
  ctx.camera.lookAt(0, -off, 0);
  ctx.globe.rotation.y = 0.62 + t * 0.12;
}

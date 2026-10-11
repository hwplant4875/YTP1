// STRATA brand mark: a 3D letter S cut into rock strata; the layers slip apart like a fault line
// and one seam glows amber. shots: core (square profile) | wide
import { rng } from './lib.js';
import { makeComposer } from './look.js';
import { TTFLoader } from 'three/addons/loaders/TTFLoader.js';
import { Font } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

export async function setup(THREE, renderer, W, H) {
  const shot = new URLSearchParams(location.search).get('shot') || 'core';
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050506);
  const camera = new THREE.PerspectiveCamera(22, W / H, 0.1, 200);
  renderer.localClippingEnabled = true;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const json = await new Promise((res, rej) => new TTFLoader().load('/scenes/data/fonts/' + (new URLSearchParams(location.search).get('font') || 'PlayfairDisplay-Bold.ttf'), res, undefined, rej));
  const font = new Font(json);
  const geo = new TextGeometry('S', { font, size: 4, depth: 0.9, curveSegments: 24, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.04, bevelSegments: 4 });
  geo.computeBoundingBox(); const bb = geo.boundingBox;
  geo.translate(-(bb.min.x + bb.max.x) / 2, -(bb.min.y + bb.max.y) / 2, -(bb.min.z + bb.max.z) / 2);
  geo.computeBoundingBox(); const y0 = geo.boundingBox.min.y, y1 = geo.boundingBox.max.y;

  const stoneTex = (seed, base, grain) => {
    const r = rng(seed), c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d');
    g.fillStyle = `rgb(${base},${base},${base + 2})`; g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 9000; i++) { const v = base + (r() - 0.5) * grain; g.fillStyle = `rgba(${v},${v - 2},${v - 6},0.5)`; g.fillRect(r() * 512, r() * 512, 1 + r() * 2, 1 + r() * 2); }
    for (let i = 0; i < 0; i++) { g.strokeStyle = `rgba(0,0,0,${0.06 + r() * 0.1})`; g.lineWidth = 0.6 + r() * 1.6; const y = r() * 512; g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= 512; x += 16) g.lineTo(x, y + Math.sin(x * 0.02 + i) * 3); g.stroke(); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(0.35, 0.35); return t;
  };
  // fractions of the letter height from top: [from, to, tone(-1 = glowing seam), slip x]
  const cuts = [[0.00, 0.31, 150, -0.14], [0.31, 0.515, 124, 0.0], [0.515, 0.545, -1, 0.0], [0.545, 0.76, 104, 0.14], [0.76, 1.0, 86, 0.24]];
  const GAP = 0.09, group = new THREE.Group(); scene.add(group);
  const H0 = y1 - y0;
  cuts.forEach(([a, b, tone, slip], i) => {
    const top = y1 - a * H0 - (i ? GAP / 2 : 0), bot = y1 - b * H0 + (i < cuts.length - 1 ? GAP / 2 : 0);
    const planes = [new THREE.Plane(new THREE.Vector3(0, -1, 0), top), new THREE.Plane(new THREE.Vector3(0, 1, 0), -bot)];
    const mat = tone < 0
      ? new THREE.MeshStandardMaterial({ color: 0xffa64a, emissive: 0xff9a3a, emissiveIntensity: 2.2, roughness: 0.5, clippingPlanes: planes, clipShadows: true, side: THREE.FrontSide })
      : new THREE.MeshStandardMaterial({ map: stoneTex(i + 2, tone, 34), roughness: 0.55, metalness: 0.15, clippingPlanes: planes, clipShadows: true, side: THREE.FrontSide });
    const m = new THREE.Mesh(geo, mat); m.position.x = slip; m.castShadow = m.receiveShadow = true;
    group.add(m);
  });
  const seamY = y1 - 0.5425 * H0;
  const pl = new THREE.PointLight(0xffa64a, 9, 6, 1.4); pl.position.set(0, seamY, 1.4); group.add(pl);
  const key = new THREE.DirectionalLight(0xfff1e0, 2.0); key.position.set(-7, 9, 5); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); scene.add(key);
  const rim = new THREE.DirectionalLight(0xc8d6ea, 2.6); rim.position.set(8, 2, -3); scene.add(rim);
  scene.add(new THREE.HemisphereLight(0x8090a0, 0x000000, 0.25));
  const fill = new THREE.DirectionalLight(0xffffff, 0.9); fill.position.set(0, 1, 10); scene.add(fill);
  group.rotation.y = -0.12; group.rotation.x = 0.02;
  camera.position.set(0, 0.4, shot === 'core' ? 19 : 24); camera.lookAt(0, 0, 0);
  const post = makeComposer(THREE, renderer, scene, camera, W, H, { bloom: 0.55, bloomRadius: 0.55, bloomThreshold: 0.82, exposure: 1.0 });
  return { scene, camera, group, shot, ...post };
}

export function update(ctx, t) { ctx.group.rotation.y = -0.12 + Math.sin(t * 0.4) * 0.06; }

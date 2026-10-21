// Shared 3D studio stage for RageStyles graphics: HDRI lighting, glossy floor, soft shadows, bloom.
import * as THREE from 'three';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
export { THREE };

export async function makeStage({ w = 1080, h = 1920, hdri = 'studio_small_09', envIntensity = 0.55, bloom = 0.35, fog = 0x050505, accent = 0xff2a2a } = {}) {
  const canvas = new OffscreenCanvas(w, h);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(w, h, false); renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(fog);
  scene.fog = new THREE.Fog(fog, 9, 26);
  const pm = new THREE.PMREMGenerator(renderer);
  const hdr = await new RGBELoader().loadAsync(`/@work/3d/${hdri}/${hdri}.hdr`);
  scene.environment = pm.fromEquirectangular(hdr).texture; scene.environmentIntensity = envIntensity;
  hdr.dispose();

  const camera = new THREE.PerspectiveCamera(32, w / h, 0.05, 100);

  // floor: dark, slightly glossy, fades into fog
  const floor = new THREE.Mesh(new THREE.CircleGeometry(30, 64), new THREE.MeshStandardMaterial({ color: 0x0b0b0c, roughness: 0.42, metalness: 0.0 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);

  // key light (warm, shadows), rim lights (accent red + cool)
  const key = new THREE.DirectionalLight(0xfff1e0, 2.6); key.position.set(-3, 7, 4); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 6; key.shadow.bias = -0.0004;
  Object.assign(key.shadow.camera, { left: -5, right: 5, top: 5, bottom: -5, near: 1, far: 20 });
  scene.add(key);
  const rimA = new THREE.SpotLight(accent, 60, 18, 0.5, 0.6); rimA.position.set(4, 3.5, -3); scene.add(rimA);
  const rimB = new THREE.SpotLight(0x8fb4ff, 30, 18, 0.5, 0.6); rimB.position.set(-4.5, 3, -2.5); scene.add(rimB);
  // soft pool of light on the floor
  const pool = new THREE.SpotLight(0xffffff, 40, 14, 0.45, 0.9); pool.position.set(0, 7, 0.5); scene.add(pool); scene.add(pool.target);

  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(1); composer.setSize(w, h);
  composer.addPass(new RenderPass(scene, camera));
  const bloomPass = new UnrealBloomPass(new THREE.Vector2(w / 2, h / 2), bloom, 0.6, 0.82); composer.addPass(bloomPass);
  composer.addPass(new OutputPass());

  const gltf = new GLTFLoader();
  const S = {
    THREE, renderer, scene, camera, composer, canvas, key, rimA, rimB, pool, floor, bloomPass,
    load: async id => { const g = await gltf.loadAsync(`/@work/3d/${id}/${id}.gltf`); g.scene.traverse(o => { if (o.isMesh) { o.castShadow = o.receiveShadow = true; } }); return g.scene; },
    render: () => { composer.render(); return canvas; },
  };
  return S;
}

// ---------- procedural props ----------
const mat = {
  steel: () => new THREE.MeshStandardMaterial({ color: 0xc8ccd2, metalness: 1, roughness: 0.32 }),
  chrome: () => new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 1, roughness: 0.12 }),
  iron: () => new THREE.MeshStandardMaterial({ color: 0x2c2c31, metalness: 0.85, roughness: 0.36 }),
  rubber: () => new THREE.MeshStandardMaterial({ color: 0x111112, metalness: 0, roughness: 0.75 }),
  dark: () => new THREE.MeshStandardMaterial({ color: 0x050505, metalness: 0.2, roughness: 0.6 }),
  paint: c => new THREE.MeshStandardMaterial({ color: c, metalness: 0.4, roughness: 0.35 }),
};
export { mat };

// stainless two-door fridge, ~0.76 x 1.78 x 0.72 m, origin at floor center
export function fridge() {
  const g = new THREE.Group();
  const W = .76, H = 1.78, D = .72;
  const body = new THREE.Mesh(new RoundedBoxGeometry(W, H, D, 4, .035), mat.steel()); body.position.y = H / 2; g.add(body);
  // brushed look: subtle vertical anisotropy via slightly darker side panels
  const side = new THREE.MeshStandardMaterial({ color: 0x9a9ea5, metalness: 1, roughness: .42 });
  const sideL = new THREE.Mesh(new THREE.BoxGeometry(.004, H - .06, D - .08), side); sideL.position.set(-W / 2 - .001, H / 2, 0); g.add(sideL);
  const sideR = sideL.clone(); sideR.position.x = W / 2 + .001; g.add(sideR);
  // door gap (freezer on top 1/3)
  const gap = new THREE.Mesh(new THREE.BoxGeometry(W - .02, .012, .02), mat.dark()); gap.position.set(0, H * .64, D / 2 + .002); g.add(gap);
  const gapT = new THREE.Mesh(new THREE.BoxGeometry(W - .02, .01, .02), mat.dark()); gapT.position.set(0, H - .03, D / 2 + .002); g.add(gapT);
  // handles
  const hm = mat.chrome();
  const mkHandle = (y, len) => {
    const hg = new THREE.Group();
    const bar = new THREE.Mesh(new THREE.CylinderGeometry(.013, .013, len, 20), hm); hg.add(bar);
    for (const s of [-1, 1]) { const st = new THREE.Mesh(new THREE.CylinderGeometry(.009, .009, .05, 12), hm); st.rotation.x = Math.PI / 2; st.position.set(0, s * (len / 2 - .03), -.025); hg.add(st); }
    hg.position.set(W / 2 - .09, y, D / 2 + .05); hg.traverse(o => o.castShadow = true); return hg;
  };
  g.add(mkHandle(H * .64 - .36, .5), mkHandle(H * .64 + .2, .3));
  // dispenser panel
  const disp = new THREE.Mesh(new RoundedBoxGeometry(.2, .3, .02, 2, .01), new THREE.MeshStandardMaterial({ color: 0x0c0c0e, metalness: .3, roughness: .2 }));
  disp.position.set(-.12, H * .48, D / 2 + .008); g.add(disp);
  // feet
  for (const x of [-1, 1]) for (const z of [-1, 1]) { const f = new THREE.Mesh(new THREE.CylinderGeometry(.02, .02, .03, 10), mat.dark()); f.position.set(x * (W / 2 - .06), .015, z * (D / 2 - .06)); g.add(f); }
  g.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  body.position.y += .03; [sideL, sideR, gap, gapT, disp].forEach(m => m.position.y += .03);
  g.userData.height = H + .03;
  return g;
}

// olympic barbell with plates; plates: list of plate radii per side (from inside out)
export function barbell(plates = Array(8).fill(.225)) {
  const g = new THREE.Group();
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(.014, .014, 1.31, 32), mat.chrome()); shaft.rotation.z = Math.PI / 2; g.add(shaft);
  // knurl bands (slightly darker)
  for (const s of [-1, 1]) {
    const k = new THREE.Mesh(new THREE.CylinderGeometry(.0145, .0145, .42, 32), new THREE.MeshStandardMaterial({ color: 0x9ea2a8, metalness: 1, roughness: .55 }));
    k.rotation.z = Math.PI / 2; k.position.x = s * .38; g.add(k);
    const collar = new THREE.Mesh(new THREE.CylinderGeometry(.038, .038, .03, 32), mat.chrome()); collar.rotation.z = Math.PI / 2; collar.position.x = s * .67; g.add(collar);
    const sleeve = new THREE.Mesh(new THREE.CylinderGeometry(.025, .025, .42, 32), mat.chrome()); sleeve.rotation.z = Math.PI / 2; sleeve.position.x = s * (.685 + .21); g.add(sleeve);
    let x = .7;
    plates.forEach((r, i) => {
      const th = r > .2 ? .058 : .035;
      const p = plate(r, th); p.position.x = s * (x + th / 2); p.rotation.y = s > 0 ? 0 : Math.PI; g.add(p); x += th + .002;
    });
  }
  g.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  return g;
}

// iron plate with raised rim and hub, faces +x
export function plate(r = .225, th = .058) {
  const g = new THREE.Group();
  const prof = [[.026, -th / 2], [.06, -th / 2], [.07, -th / 2 + .008], [r - .03, -th / 2 + .008], [r - .02, -th / 2], [r, -th / 2 + .006], [r, th / 2 - .006], [r - .02, th / 2], [r - .03, th / 2 - .008], [.07, th / 2 - .008], [.06, th / 2], [.026, th / 2]]
    .map(([a, b]) => new THREE.Vector2(a, b));
  const lathe = new THREE.Mesh(new THREE.LatheGeometry(prof, 72), mat.iron()); lathe.rotation.z = Math.PI / 2; g.add(lathe);
  return g;
}

// simple squat stand pair
export function stands(span = 1.2, height = 1.45) {
  const g = new THREE.Group(); const m = mat.paint(0x1c1c1f);
  for (const s of [-1, 1]) {
    const post = new THREE.Mesh(new THREE.BoxGeometry(.075, height, .075), m); post.position.set(s * span / 2, height / 2, 0); g.add(post);
    const base = new THREE.Mesh(new THREE.BoxGeometry(.12, .05, .6), m); base.position.set(s * span / 2, .025, 0); g.add(base);
    const hook = new THREE.Mesh(new THREE.BoxGeometry(.08, .03, .12), mat.paint(0xbb1111)); hook.position.set(s * span / 2, height - .1, .07); g.add(hook);
  }
  g.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  return g;
}

// stylised artist's mannequin (feet at origin, facing +z). h = height in m, bulk = width multiplier (1 = average man)
export function mannequin(h = 1.75, bulk = 1, material = null) {
  const m = material || new THREE.MeshPhysicalMaterial({ color: 0xe9e6e1, roughness: .38, metalness: 0, clearcoat: .6, clearcoatRoughness: .25 });
  const joint = new THREE.MeshStandardMaterial({ color: 0x1a1a1c, roughness: .4, metalness: .6 });
  const g = new THREE.Group(); const s = h / 1.75, b = bulk;
  const cap = (r, len, mat = m) => new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 8, 24), mat);
  const sph = (r, mat = joint) => new THREE.Mesh(new THREE.SphereGeometry(r, 24, 16), mat);
  const add = (o, x, y, z, rz = 0, rx = 0) => { o.position.set(x, y, z); o.rotation.z = rz; o.rotation.x = rx; g.add(o); return o; };
  // legs
  for (const sx of [-1, 1]) {
    add(cap(.065 * b * s, .36 * s), sx * .1 * b * s, .25 * s, 0);
    add(sph(.055 * b * s), sx * .1 * b * s, .5 * s, 0);
    add(cap(.08 * b * s, .34 * s), sx * .1 * b * s, .74 * s, 0);
    const foot = add(new THREE.Mesh(new THREE.BoxGeometry(.09 * b * s, .05 * s, .22 * s), m), sx * .1 * b * s, .03 * s, .05 * s);
  }
  // pelvis, torso (V-taper grows with bulk), chest
  add(new THREE.Mesh(new THREE.SphereGeometry(.15 * s, 24, 16), m), 0, .95 * s, 0).scale.set(1.25 * b, .7, .8 * Math.sqrt(b));
  const torso = add(new THREE.Mesh(new THREE.CylinderGeometry(.19 * s * b ** 1.15, .13 * s * b, .42 * s, 32), m), 0, 1.2 * s, 0); torso.scale.z = .62 * Math.sqrt(b);
  add(sph(.05 * s), 0, 1.0 * s, 0);
  // shoulders + arms (slightly abducted)
  for (const sx of [-1, 1]) {
    const sxp = sx * (.2 * s * b ** 1.15 + .04 * s);
    add(new THREE.Mesh(new THREE.SphereGeometry(.075 * s * b, 24, 16), m), sxp, 1.38 * s, 0);
    add(cap(.055 * s * b, .24 * s), sxp + sx * .04 * s * b, 1.2 * s, 0, sx * .18);
    add(sph(.045 * s * b), sxp + sx * .075 * s * b, 1.04 * s, 0);
    add(cap(.045 * s * b, .22 * s), sxp + sx * .1 * s * b, .88 * s, 0, sx * .1);
    add(new THREE.Mesh(new THREE.SphereGeometry(.05 * s * Math.sqrt(b), 16, 12), m), sxp + sx * .12 * s * b, .72 * s, 0);
  }
  // neck + head
  add(cap(.05 * s * Math.sqrt(b), .06 * s), 0, 1.5 * s, 0);
  add(new THREE.Mesh(new THREE.SphereGeometry(.105 * s, 32, 24), m), 0, 1.64 * s, 0).scale.set(.9, 1.1, 1);
  g.traverse(o => { if (o.isMesh) { o.castShadow = o.receiveShadow = true; } });
  return g;
}

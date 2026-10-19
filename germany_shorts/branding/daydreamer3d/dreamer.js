// Daydreamer mascot, 3D cartoon. shot=plain|cap ; view=hero|thumb
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export async function setup(THREE, renderer, W, H) {
  const q = new URLSearchParams(location.search).get('shot') || 'plain';
  const [variant, view] = q.split(',');
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.05;
  const scene = new THREE.Scene();
  // dusk-lilac gradient backdrop
  const c = document.createElement('canvas'); c.width = 4; c.height = 512; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, '#2a2350'); gr.addColorStop(0.55, '#5b4a86'); gr.addColorStop(1, '#c98a8a');
  g.fillStyle = gr; g.fillRect(0, 0, 4, 512); const bg = new THREE.CanvasTexture(c); bg.colorSpace = THREE.SRGBColorSpace; scene.background = bg;
  const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; scene.environmentIntensity = 0.35;

  const cam = new THREE.PerspectiveCamera(view === 'thumb' ? 28 : 30, W / H, 0.1, 100);

  const DREAM = 0xffd347;
  const skin = new THREE.MeshPhysicalMaterial({ color: DREAM, roughness: 0.38, clearcoat: 0.5, clearcoatRoughness: 0.4, sheen: 0.3, sheenColor: new THREE.Color(0xffe6a0) });
  const ink = new THREE.MeshPhysicalMaterial({ color: 0x1d1428, roughness: 0.15, clearcoat: 1 });
  const white = new THREE.MeshStandardMaterial({ color: 0xfffaf0, roughness: 0.5 });
  const capMat = new THREE.MeshPhysicalMaterial({ color: 0x6f7cf0, roughness: 0.8, sheen: 1, sheenColor: new THREE.Color(0xb8c0ff) });

  // ground: soft round stage of grass-ish pastel + a few flowers (spring nap)
  const ground = new THREE.Mesh(new THREE.CircleGeometry(6, 64), new THREE.MeshStandardMaterial({ color: 0x5a4a8a, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
  const flowerCols = [0xffffff, 0xff9fb8, 0xffd27a, 0xa9c4ff];
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 26; i++) {
    const a = rnd() * 6.283, r = 1.4 + rnd() * 3.5; const f = new THREE.Group();
    const m = new THREE.MeshStandardMaterial({ color: flowerCols[i % 4], roughness: 0.6 });
    for (let k = 0; k < 5; k++) { const p = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 8), m); p.position.set(Math.cos(k * 1.256) * 0.07, 0.12, Math.sin(k * 1.256) * 0.07); f.add(p); }
    const ctr = new THREE.Mesh(new THREE.SphereGeometry(0.045, 12, 8), new THREE.MeshStandardMaterial({ color: 0xffa040 })); ctr.position.y = 0.13; f.add(ctr);
    const st = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.12), new THREE.MeshStandardMaterial({ color: 0x5aa060 })); st.position.y = 0.06; f.add(st);
    f.position.set(Math.cos(a) * r, 0, Math.sin(a) * r - 0.5); f.traverse(o => o.castShadow = true); scene.add(f);
  }
  // floating soft clouds behind
  const cloudM = new THREE.MeshStandardMaterial({ color: 0xf3e9ff, roughness: 1, transparent: true, opacity: 0.9 });
  for (const [x, y, z, s] of [[-3.2, 3.6, -4, 1], [3.4, 4.2, -5, 1.3], [0.6, 5.2, -7, 0.9]]) {
    const cl = new THREE.Group();
    for (const [dx, dy, r] of [[-0.5, 0, 0.45], [0.5, 0, 0.45], [0, 0.25, 0.6], [0, -0.05, 0.5]]) { const b = new THREE.Mesh(new THREE.SphereGeometry(r, 24, 16), cloudM); b.position.set(dx, dy, 0); cl.add(b); }
    cl.position.set(x, y, z); cl.scale.setScalar(s); scene.add(cl);
  }

  // ---- character ----
  const fig = new THREE.Group(); scene.add(fig);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.55, 64, 48), skin); head.position.y = 2.35; fig.add(head);
  const limb = (len, r) => { const gg = new THREE.CapsuleGeometry(r, len, 8, 20); gg.translate(0, -len / 2 - r, 0); return new THREE.Mesh(gg, skin); };
  const body = limb(0.85, 0.11); body.position.y = 1.86; fig.add(body);
  const armL = limb(0.62, 0.075), armR = limb(0.62, 0.075);
  armL.position.set(-0.1, 1.74, 0); armR.position.set(0.1, 1.74, 0); armL.rotation.z = -0.35; armR.rotation.z = 1.95; fig.add(armL, armR);
  const legL = limb(0.72, 0.08), legR = limb(0.72, 0.08);
  legL.position.set(-0.1, 0.88, 0); legR.position.set(0.1, 0.88, 0); legL.rotation.z = -0.08; legR.rotation.z = 0.08; fig.add(legL, legR);
  for (const l of [legL, legR]) { const ft = new THREE.Mesh(new THREE.SphereGeometry(0.12, 20, 14), skin); ft.scale.set(1, 0.6, 1.4); ft.position.set(0, -0.86, 0.06); l.add(ft); }
  for (const a of [armL, armR]) { const h = new THREE.Mesh(new THREE.SphereGeometry(0.1, 20, 14), skin); h.position.y = -0.77; a.add(h); }
  // face: glossy ink eyes (slightly sleepy for cap) + mouth + blush
  const eyeY = variant === 'cap' ? 0.0 : 0.05;
  for (const s of [-1, 1]) {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.075, 24, 16), ink); e.scale.set(1, variant === 'cap' ? 0.55 : 1.3, 0.5);
    e.position.set(s * 0.19, eyeY, 0.53); head.add(e);
    const hl = new THREE.Mesh(new THREE.SphereGeometry(0.022, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    hl.position.set(s * 0.19 + 0.025, eyeY + (variant === 'cap' ? 0.015 : 0.04), 0.565); head.add(hl);
    
    const bl = new THREE.Mesh(new THREE.CircleGeometry(0.07, 24), new THREE.MeshBasicMaterial({ color: 0xff8f7a, transparent: true, opacity: 0.55 }));
    bl.position.set(s * 0.33, -0.11, 0.0); bl.lookAt(new THREE.Vector3(s * 0.33, -0.11, 0).multiplyScalar(2)); 
    const n = new THREE.Vector3(s * 0.33, -0.11, 0.42).normalize(); bl.position.copy(n.clone().multiplyScalar(0.552)); bl.lookAt(n.clone().multiplyScalar(2)); head.add(bl);
  }
  const mouth = new THREE.Mesh(new THREE.TorusGeometry(0.09, 0.02, 10, 24, Math.PI), ink);
  mouth.position.set(0, -0.15, 0.53); mouth.rotation.z = Math.PI; mouth.rotation.x = -0.25; head.add(mouth);

  if (variant === 'cap') {
    // floppy nightcap: tube along a bent curve with tapering radius
    const curve = new THREE.CatmullRomCurve3([new THREE.Vector3(0, 0.25, 0), new THREE.Vector3(0.05, 0.7, -0.05), new THREE.Vector3(0.35, 0.95, -0.05), new THREE.Vector3(0.75, 0.75, 0.0), new THREE.Vector3(0.88, 0.45, 0.05)]);
    const segs = 60, rad = 14, pts = curve.getSpacedPoints(segs), fr = curve.computeFrenetFrames(segs, false);
    const posA = [], idx = [];
    for (let i = 0; i <= segs; i++) { const t = i / segs, r = 0.56 * Math.pow(1 - t, 1.25) + 0.02;
      for (let j = 0; j <= rad; j++) { const a = j / rad * Math.PI * 2; const v = pts[i].clone().addScaledVector(fr.normals[i], Math.cos(a) * r).addScaledVector(fr.binormals[i], Math.sin(a) * r); posA.push(v.x, v.y, v.z); } }
    for (let i = 0; i < segs; i++) for (let j = 0; j < rad; j++) { const a = i * (rad + 1) + j, b = a + rad + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
    const capG = new THREE.BufferGeometry(); capG.setAttribute('position', new THREE.Float32BufferAttribute(posA, 3)); capG.setIndex(idx); capG.computeVertexNormals();
    const cap = new THREE.Mesh(capG, capMat); cap.material.side = THREE.DoubleSide; head.add(cap); cap.castShadow = true;
    const band = new THREE.Mesh(new THREE.TorusGeometry(0.53, 0.085, 16, 48), white); band.rotation.x = Math.PI / 2 - 0.08; band.position.y = 0.26; head.add(band);
    const pom = new THREE.Mesh(new THREE.SphereGeometry(0.12, 24, 16), white); pom.position.set(0.9, 0.4, 0.06); head.add(pom);
    head.rotation.z = 0.06;
  }
  fig.traverse(o => { if (o.isMesh) o.castShadow = true; });
  fig.rotation.y = -0.18;

  // lights: warm sun key, lilac fill, warm rim
  const key = new THREE.DirectionalLight(0xfff3dc, 2.6); key.position.set(-3, 6, 4); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4 }); key.shadow.radius = 6; scene.add(key);
  scene.add(new THREE.HemisphereLight(0xb9a8ff, 0x3a2a50, 0.9));
  const rim = new THREE.DirectionalLight(0xffb070, 2.2); rim.position.set(3, 3, -4); scene.add(rim);

  if (view === 'thumb') { fig.position.x = -1.15; }
  const composer = new EffectComposer(renderer); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, cam));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.25, 0.6, 0.85));
  composer.addPass(new OutputPass());
  return { scene, camera: cam, composer, view, fig };
}
export function update(c, t) {
  if (c.view === 'thumb') { c.camera.position.set(0, 2.0, 7.2); c.camera.lookAt(0, 1.75, 0); }
  else { c.camera.position.set(0.5, 1.8, 8.2); c.camera.lookAt(0, 1.5, 0); }
}

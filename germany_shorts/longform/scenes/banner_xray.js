// X-Ray Europe channel banner (2560x1440): a European street skyline cut open, with what lies underneath
// (metro station, catacomb vaults, a bunker, an escape tunnel) drawn as x-ray shells.
// The content sits in the 423px-high band YouTube shows on desktop and mobile.
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const RIM = [0.45, 0.9, 1.0], CORE = [0.05, 0.35, 0.55];

export async function setup(THREE, renderer, W, H) {
  const scene = new THREE.Scene();
  const c = document.createElement('canvas'); c.width = 16; c.height = 512;
  const g = c.getContext('2d'), grd = g.createLinearGradient(0, 0, 0, 512);
  grd.addColorStop(0, '#02050a'); grd.addColorStop(0.42, '#0a1f2e'); grd.addColorStop(0.47, '#0d2a3b');
  grd.addColorStop(0.5, '#051019'); grd.addColorStop(1, '#010306');
  g.fillStyle = grd; g.fillRect(0, 0, 16, 512);
  scene.background = new THREE.CanvasTexture(c); scene.background.colorSpace = THREE.SRGBColorSpace;

  const camera = new THREE.PerspectiveCamera(14, W / H, 1, 400);
  camera.position.set(2, 4, 75); camera.lookAt(0, 0.2, 0);

  const uni = { scan: { value: 0 } };
  const xray = (k = 1) => new THREE.ShaderMaterial({
    uniforms: { ...uni, k: { value: k } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    vertexShader: `varying vec3 vN; varying vec3 vV; varying vec3 vW;
      void main(){ vec4 mv = modelViewMatrix*vec4(position,1.0); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz);
        vW = (modelMatrix*vec4(position,1.0)).xyz; gl_Position = projectionMatrix*mv; }`,
    fragmentShader: `uniform float scan; uniform float k; varying vec3 vN; varying vec3 vV; varying vec3 vW;
      void main(){ float f = pow(1.0-abs(dot(normalize(vN),normalize(vV))), 2.0);
        float band = exp(-pow((vW.x-scan)*0.9,2.0));
        vec3 col = vec3(${CORE})*0.05 + vec3(${RIM})*(f*0.38 + band*0.25*f) + vec3(1.0)*band*0.04;
        gl_FragColor = vec4(col*k, 1.0); }`,
  });
  const edgeMat = new THREE.LineBasicMaterial({ color: 0xbff4ff, transparent: true, opacity: 0.32, blending: THREE.AdditiveBlending });
  const add = (geo, x, y, z = 0, rot = [0, 0, 0], k = 1) => {
    const m = new THREE.Mesh(geo, xray(k)); m.position.set(x, y, z); m.rotation.set(...rot);
    const e = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 20), edgeMat); e.position.copy(m.position); e.rotation.copy(m.rotation);
    scene.add(m, e); return m;
  };
  const GY = 0.95;                    // ground line
  const amber = [];                   // warm lights placed underground (ties to the videos' amber look)

  // ---- underground, left: metro station vault with a train
  add(new THREE.CylinderGeometry(1.25, 1.25, 7.5, 40, 1, true, 0, Math.PI), -9.6, -0.9, 0, [0, 0, Math.PI / 2]);
  add(new THREE.BoxGeometry(7.5, 0.18, 2.6), -9.6, -0.95, 0);
  for (let i = 0; i < 3; i++) add(new THREE.BoxGeometry(2.0, 0.75, 0.75), -11.8 + i * 2.15, -0.5, 0.45, [0, 0, 0], 1.3);
  add(new THREE.BoxGeometry(0.7, GY + 0.9, 0.7), -12.4, (GY - 0.9) / 2 + 0.05, -0.6);       // entrance shaft
  for (let i = 0; i < 6; i++) add(new THREE.BoxGeometry(0.5, 0.08, 0.6), -12.4, GY - 0.25 - i * 0.28, 0.1 + i * 0.0, [0, 0, 0], 0.8);
  // ---- underground, centre-left: old tram tunnel tube running into depth
  // ---- underground, right: catacomb vaults
  for (let i = 0; i < 6; i++) add(new THREE.CylinderGeometry(0.55, 0.55, 1.4, 24, 1, true, 0, Math.PI), 6.6 + i * 1.12, -1.35, 0, [0, 0, Math.PI / 2], 0.9);
  for (let i = 0; i < 7; i++) add(new THREE.BoxGeometry(0.22, 0.55, 1.4), 6.04 + i * 1.12, -1.62, 0, [0, 0, 0], 0.8);
  // ---- bunker block
  add(new THREE.BoxGeometry(2.6, 1.0, 2.0), 9.6, -0.15, -0.5, [0, 0, 0], 1.1);
  add(new THREE.BoxGeometry(1.9, 0.55, 1.4), 9.6, -0.15, -0.5, [0, 0, 0], 0.8);
  add(new THREE.BoxGeometry(0.5, GY + 0.35, 0.5), 11.2, (GY + 0.35) / 2 - 0.35 + 0.0, -0.5);
  // ---- long escape tunnel across the whole width, timber frames and bulbs
  add(new THREE.BoxGeometry(30, 0.42, 0.42), 0, -2.05, 0.6, [0, 0, 0], 0.9);
  for (let x = -14; x <= 14; x += 0.9) add(new THREE.BoxGeometry(0.05, 0.42, 0.44), x, -2.05, 0.6, [0, 0, 0], 0.7);
  for (let x = -13.5; x <= 13.5; x += 2.7) amber.push([x, -1.9, 0.6, 0.22]);
  for (const p of [[-11.8, -0.15, 0.45, 0.32], [-7.6, -0.15, 0.45, 0.32], [9.6, -0.15, 0.6, 0.3]]) amber.push(p);

  // ---- street level: skyline silhouettes (solid, not x-ray) with a few lit windows
  const city = new THREE.MeshBasicMaterial({ color: 0x050d14 });
  const cityEdge = new THREE.LineBasicMaterial({ color: 0x5fa8c8, transparent: true, opacity: 0.35 });
  const bld = (geo, x, y, z = -2) => { const m = new THREE.Mesh(geo, city); m.position.set(x, y, z); scene.add(m);
    const e = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 30), cityEdge); e.position.copy(m.position); scene.add(e); return m; };
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let x = -15; x < 15;) {
    const w = 0.7 + rnd() * 1.3, h = 0.5 + rnd() * 1.4;
    {   // keep the centre low so the wordmark breathes
      const hh = h;
      bld(new THREE.BoxGeometry(w * 0.95, hh, 1.2), x + w / 2, GY + hh / 2, -2 - rnd() * 2);
      if (rnd() < 0.7) bld(new THREE.ConeGeometry(w * 0.55, 0.45, 4, 1), x + w / 2, GY + hh + 0.22, -2.5).rotation.y = Math.PI / 4;
      for (let k = 0; k < 3; k++) if (rnd() < 0.35) amber.push([x + w * (0.25 + 0.5 * rnd()), GY + hh * (0.25 + 0.6 * rnd()), 0, 0.06]);
    }
    x += w;
  }
  // landmarks: Berlin TV tower (right), a cathedral dome (left), a gothic spire
  bld(new THREE.CylinderGeometry(0.09, 0.16, 4.2, 12), 7.4, GY + 2.1, -3);
  bld(new THREE.SphereGeometry(0.42, 24, 16), 7.4, GY + 2.9, -3);
  bld(new THREE.CylinderGeometry(0.01, 0.04, 1.1, 6), 7.4, GY + 3.85, -3);
  bld(new THREE.SphereGeometry(1.0, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), -7.8, GY + 1.25, -3.5);
  bld(new THREE.BoxGeometry(2.4, 1.25, 1.6), -7.8, GY + 0.62, -3.5);
  bld(new THREE.ConeGeometry(0.35, 2.6, 4), -12.6, GY + 2.3, -3).rotation.y = Math.PI / 4;
  bld(new THREE.BoxGeometry(0.75, 1.1, 0.75), -12.6, GY + 0.55, -3);

  // ground line and soil strata
  const lineMat = (o) => new THREE.LineBasicMaterial({ color: 0x9fe6ff, transparent: true, opacity: o, blending: THREE.AdditiveBlending });
  const hline = (y, o, z = 1.5) => scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-20, y, z), new THREE.Vector3(20, y, z)]), lineMat(o)));
  hline(GY, 0.9); hline(GY - 0.03, 0.3);
  for (let i = 1; i < 9; i++) hline(GY - i * 0.42 - (i % 3) * 0.07, 0.05);

  // amber lights as soft sprites
  const sc = document.createElement('canvas'); sc.width = sc.height = 64;
  const sg = sc.getContext('2d'), rg = sg.createRadialGradient(32, 32, 0, 32, 32, 32);
  rg.addColorStop(0, 'rgba(255,190,110,1)'); rg.addColorStop(0.25, 'rgba(255,150,60,0.5)'); rg.addColorStop(1, 'rgba(255,120,30,0)');
  sg.fillStyle = rg; sg.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(sc);
  for (const [x, y, z, s] of amber) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true }));
    sp.position.set(x, y, z); sp.scale.set(s * 3, s * 3, 1); scene.add(sp);
  }

  const composer = new EffectComposer(renderer); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.6, 0.5, 0.5));
  composer.addPass(new OutputPass());
  return { scene, camera, composer, uni };
}

export function update(ctx, t) { ctx.uni.scan.value = -14 + t * 7; }

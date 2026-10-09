// ORBIS channel mark: an x-ray globe with a wedge cut away, showing layered shells and a warm core.
// shots: cyan (default), amber
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const PAL = {
  cyan: { solid: 0x04121b, strata: [0x0c3346, 0x12506a, 0x1d7090], rim: [0.45, 0.9, 1.0], bg: '#03080d', bg2: '#0b2534', line: 0xbff4ff },
  amber: { solid: 0x140a03, strata: [0x3a1f08, 0x5a300c, 0x8a4c14], rim: [1.0, 0.72, 0.35], bg: '#080503', bg2: '#2a1606', line: 0xffe2b8 },
};

export function xrayMat(THREE, rim, k = 1) {
  return new THREE.ShaderMaterial({
    uniforms: { rim: { value: new THREE.Vector3(...rim) }, k: { value: k } },
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.FrontSide,
    vertexShader: `varying vec3 vN; varying vec3 vV; varying vec3 vW;
      void main(){ vec4 mv = modelViewMatrix*vec4(position,1.0); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz);
        vW = (modelMatrix*vec4(position,1.0)).xyz; gl_Position = projectionMatrix*mv; }`,
    fragmentShader: `uniform vec3 rim; uniform float k; varying vec3 vN; varying vec3 vV; varying vec3 vW;
      void main(){ float f = pow(1.0-abs(dot(normalize(vN),normalize(vV))), 2.0);
        float lines = smoothstep(0.9,1.0,0.5+0.5*sin(vW.y*70.0))*0.12;
        gl_FragColor = vec4(rim*(0.02 + f*0.55 + lines*0.15)*k, 1.0); }`,
  });
}

// globe group: radius 1, wedge (quarter) removed facing the camera
export function makeGlobe(THREE, P, opt = {}) {
  const grp = new THREE.Group();
  const cut = opt.cut ?? Math.PI / 2, start = cut / 2;          // wedge centred on +z
  const phiStart = Math.PI / 2 + start, phiLen = Math.PI * 2 - cut; // three.js phi=0 is -x... rotate to face camera
  const lineMat = new THREE.LineBasicMaterial({ color: P.line, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending });
  const shells = [[1.0, 1.0], [0.72, 0.7], [0.46, 0.55]];
  for (const [r, k] of shells) {
    const geo = new THREE.SphereGeometry(r, 72, 48, phiStart, phiLen);
    grp.add(new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: P.solid, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 })));
    grp.add(new THREE.Mesh(geo, xrayMat(THREE, P.rim, k)));
  }
  // cut faces: half-discs in the two wedge planes, with strata rings
  for (const side of [-1, 1]) {
    const face = new THREE.Group();
    for (let i = 0; i < shells.length; i++) {
      const r0 = shells[i + 1] ? shells[i + 1][0] : 0.0, r1 = shells[i][0];
      const rg = new THREE.RingGeometry(r0, r1, 64, 1, -Math.PI / 2, Math.PI);
      const col = new THREE.Color(P.strata[i]);
      face.add(new THREE.Mesh(rg, new THREE.MeshBasicMaterial({ color: col, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 })));
      const arc = []; for (let j = 0; j <= 64; j++) { const a = -Math.PI / 2 + j / 64 * Math.PI; arc.push(new THREE.Vector3(Math.cos(a) * r1, Math.sin(a) * r1, 0)); }
      face.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(arc), lineMat));
    }
    face.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, -1, 0), new THREE.Vector3(0, 1, 0)]), lineMat));
    // plane contains the y axis; rotate so its outward side points along the wedge edge
    face.rotation.y = side * start - Math.PI / 2 * side + (side > 0 ? 0 : 0);
    face.rotation.y = side > 0 ? -(Math.PI / 2 - start) : (Math.PI / 2 - start) + Math.PI;
    grp.add(face);
  }
  // graticule on the outer shell, skipping the wedge
  const inWedge = (a) => { const d = Math.atan2(Math.sin(a), Math.cos(a)); return Math.abs(d) < start; }; // a measured from +z
  for (let lat = -60; lat <= 60; lat += 30) {
    const y = Math.sin(lat * Math.PI / 180), rr = Math.cos(lat * Math.PI / 180);
    let seg = [];
    for (let j = 0; j <= 180; j++) {
      const a = j / 180 * Math.PI * 2;
      if (inWedge(a)) { if (seg.length > 1) grp.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(seg), lineMat)); seg = []; continue; }
      seg.push(new THREE.Vector3(Math.sin(a) * rr * 1.003, y * 1.003, Math.cos(a) * rr * 1.003));
    }
    if (seg.length > 1) grp.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(seg), lineMat));
  }
  for (let lon = 0; lon < 360; lon += 30) {
    const a = lon * Math.PI / 180; if (inWedge(a)) continue;
    const pts = []; for (let j = 0; j <= 90; j++) { const t = -Math.PI / 2 + j / 90 * Math.PI; pts.push(new THREE.Vector3(Math.sin(a) * Math.cos(t) * 1.003, Math.sin(t) * 1.003, Math.cos(a) * Math.cos(t) * 1.003)); }
    grp.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), lineMat));
  }
  // warm core
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d'), rg = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  rg.addColorStop(0, 'rgba(255,214,150,1)'); rg.addColorStop(0.2, 'rgba(255,160,70,0.55)'); rg.addColorStop(1, 'rgba(255,120,30,0)');
  g.fillStyle = rg; g.fillRect(0, 0, 128, 128);
  const core = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false, transparent: true, opacity: 0.8 }));
  core.scale.set(0.5, 0.5, 1); grp.add(core);
  return grp;
}

export async function setup(THREE, renderer, W, H) {
  const shot = new URLSearchParams(location.search).get('shot') || 'cyan';
  const P = PAL[shot] || PAL.cyan;
  const scene = new THREE.Scene();
  const c = document.createElement('canvas'); c.width = c.height = 512;
  const g = c.getContext('2d'), grd = g.createRadialGradient(256, 230, 10, 256, 256, 380);
  grd.addColorStop(0, P.bg2); grd.addColorStop(1, P.bg); g.fillStyle = grd; g.fillRect(0, 0, 512, 512);
  scene.background = new THREE.CanvasTexture(c); scene.background.colorSpace = THREE.SRGBColorSpace;
  const camera = new THREE.PerspectiveCamera(24, W / H, 0.1, 100);
  camera.position.set(1.05, 0.85, 5.5); camera.lookAt(0, 0, 0);
  const globe = makeGlobe(THREE, P); globe.rotation.set(0.38, 0.62, -0.1); scene.add(globe);
  const composer = new EffectComposer(renderer); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.6, 0.5, 0.5));
  composer.addPass(new OutputPass());
  return { scene, camera, composer, globe };
}

export function update(ctx, t) { ctx.globe.rotation.y = 0.62 + t * 0.05; }

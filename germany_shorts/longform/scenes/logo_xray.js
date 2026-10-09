// X-Ray Europe channel mark: a beveled 3D "X" rendered as an x-ray (fresnel shell, inner edges, scan band).
// shots: cyan (default), amber
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const PAL = {
  cyan: { rim: [0.45, 0.9, 1.0], core: [0.05, 0.35, 0.55], bg: '#03080d', bg2: '#0b2534', edge: 0xbff4ff },
  amber: { rim: [1.0, 0.72, 0.35], core: [0.5, 0.22, 0.04], bg: '#080503', bg2: '#2a1606', edge: 0xffe2b8 },
};

function xShape(THREE) {
  // X built from two crossing bars, traced as one outline
  const w = 0.5, L = 2.0;
  const s = new THREE.Shape();
  const k = w / Math.SQRT2;
  const pts = [[-L + k, L], [0, k * 2], [L - k, L], [L, L - k], [k * 2, 0], [L, -L + k], [L - k, -L], [0, -k * 2], [-L + k, -L], [-L, -L + k], [-k * 2, 0], [-L, L - k]];
  pts.forEach(([x, y], i) => (i ? s.lineTo(x, y) : s.moveTo(x, y)));
  s.closePath();
  return s;
}

export async function setup(THREE, renderer, W, H) {
  const shot = new URLSearchParams(location.search).get('shot') || 'cyan';
  const P = PAL[shot] || PAL.cyan;
  const scene = new THREE.Scene();
  const c = document.createElement('canvas'); c.width = c.height = 512;
  const g = c.getContext('2d');
  const grd = g.createRadialGradient(256, 230, 10, 256, 256, 380);
  grd.addColorStop(0, P.bg2); grd.addColorStop(1, P.bg);
  g.fillStyle = grd; g.fillRect(0, 0, 512, 512);
  scene.background = new THREE.CanvasTexture(c); scene.background.colorSpace = THREE.SRGBColorSpace;

  const camera = new THREE.PerspectiveCamera(30, W / H, 0.1, 100);
  camera.position.set(2.4, 1.4, 13.5); camera.lookAt(0, 0, 0);

  const geo = new THREE.ExtrudeGeometry(xShape(THREE), { depth: 0.9, bevelEnabled: true, bevelThickness: 0.14, bevelSize: 0.1, bevelSegments: 6, curveSegments: 4 });
  geo.center();
  const uni = { rim: { value: new THREE.Vector3(...P.rim) }, core: { value: new THREE.Vector3(...P.core) }, scan: { value: 0.15 } };
  const xray = new THREE.ShaderMaterial({
    uniforms: uni, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    vertexShader: `varying vec3 vN; varying vec3 vV; varying vec3 vW;
      void main(){ vec4 mv = modelViewMatrix*vec4(position,1.0); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz);
        vW = (modelMatrix*vec4(position,1.0)).xyz; gl_Position = projectionMatrix*mv; }`,
    fragmentShader: `uniform vec3 rim; uniform vec3 core; uniform float scan; varying vec3 vN; varying vec3 vV; varying vec3 vW;
      void main(){ float f = pow(1.0-abs(dot(normalize(vN),normalize(vV))), 2.2);
        float lines = 0.5+0.5*sin(vW.y*60.0); lines = smoothstep(0.85,1.0,lines)*0.18;
        float band = exp(-pow((vW.y-scan)*5.0,2.0));
        vec3 col = core*0.06 + rim*(f*0.42 + lines*0.3) + vec3(1.0)*band*(0.05+f*0.25);
        gl_FragColor = vec4(col, 1.0); }`,
  });
  const x = new THREE.Mesh(geo, xray);
  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 12), new THREE.LineBasicMaterial({ color: P.edge, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending }));
  const grp = new THREE.Group(); grp.add(x, edges); grp.rotation.set(-0.08, -0.32, 0.0);
  scene.add(grp);

  // faint measurement rings behind, like a scanner reticle
  const ringMat = new THREE.LineBasicMaterial({ color: P.edge, transparent: true, opacity: 0.12 });
  for (const r of [2.95, 3.25]) {
    const pts = []; for (let i = 0; i <= 256; i++) { const a = i / 256 * Math.PI * 2; pts.push(new THREE.Vector3(Math.cos(a) * r, Math.sin(a) * r, -1.2)); }
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), ringMat));
  }
  const tickPts = [];
  for (let i = 0; i < 72; i++) { const a = i / 72 * Math.PI * 2, r0 = 3.25, r1 = i % 6 ? 3.36 : 3.5; tickPts.push(new THREE.Vector3(Math.cos(a) * r0, Math.sin(a) * r0, -1.2), new THREE.Vector3(Math.cos(a) * r1, Math.sin(a) * r1, -1.2)); }
  scene.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(tickPts), ringMat));

  const composer = new EffectComposer(renderer); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.55, 0.5, 0.55));
  composer.addPass(new OutputPass());
  return { scene, camera, composer, uni };
}

export function update(ctx, t) { ctx.uni.scan.value = -1.6 + (t % 4) * 0.9; }

// Earth at real scale (1 unit = 100 km) with a column of $100 notes rising from the U.S.
// 28 billion notes x 0.109 mm = 3,058 km; the space station flies at ~420 km.
import * as THREE from 'three';
import { mulberry32 } from './money.js';

export const R = 63.71;            // Earth radius, 100 km units
export const ISS_ALT = 4.2;        // 420 km
export const STACK = 30.58;        // 3,058 km

// lat/lon (deg) to a point on the unit sphere in three's SphereGeometry UV convention
export function latLon(lat, lon) {
  const a = THREE.MathUtils.degToRad(lat), b = THREE.MathUtils.degToRad(lon);
  return new THREE.Vector3(Math.cos(a) * Math.cos(b), Math.sin(a), -Math.cos(a) * Math.sin(b));
}

export function buildEarth(loader, { dayUrl, nightUrl, base = [39, -98] } = {}) {
  const root = new THREE.Group();
  const globe = new THREE.Group();
  globe.position.set(0, -R, 0);
  // turn the globe so the column's base point (central U.S.) sits at the world origin, column along +Y
  globe.quaternion.setFromUnitVectors(latLon(base[0], base[1]), new THREE.Vector3(0, 1, 0));
  root.add(globe);

  const tDay = loader.load(dayUrl); tDay.colorSpace = THREE.SRGBColorSpace; tDay.anisotropy = 8;
  const tNight = loader.load(nightUrl); tNight.colorSpace = THREE.SRGBColorSpace; tNight.anisotropy = 8;
  const sun = { value: new THREE.Vector3(-0.6, -0.05, -0.8).normalize() };
  const earthMat = new THREE.ShaderMaterial({
    uniforms: { tDay: { value: tDay }, tNight: { value: tNight }, uSun: sun, uLights: { value: 1.0 } },
    vertexShader: `varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main(){ vUv = uv; vec4 wp = modelMatrix * vec4(position, 1.0); vN = normalize(mat3(modelMatrix) * normal); vV = normalize(cameraPosition - wp.xyz);
        gl_Position = projectionMatrix * viewMatrix * wp; }`,
    fragmentShader: `uniform sampler2D tDay, tNight; uniform vec3 uSun; uniform float uLights; varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main(){ vec3 n = normalize(vN); float d = dot(n, uSun);
        float day = smoothstep(-0.12, 0.22, d);
        vec3 dc = texture2D(tDay, vUv).rgb * (0.06 + 1.25 * max(d, 0.0));
        vec3 nl = texture2D(tNight, vUv).rgb; nl = pow(nl, vec3(1.35)) * vec3(1.0, 0.78, 0.5) * 1.6 * uLights;
        vec3 col = mix(nl + vec3(0.004, 0.006, 0.012), dc, day);
        float f = pow(1.0 - max(dot(n, normalize(vV)), 0.0), 2.6);
        col += vec3(0.25, 0.55, 1.0) * f * (0.08 + 0.9 * smoothstep(-0.25, 0.35, d));
        gl_FragColor = vec4(col, 1.0); }`,
  });
  const earth = new THREE.Mesh(new THREE.SphereGeometry(R, 192, 96), earthMat);
  globe.add(earth);
  // in the bloom pass only the city lights glow
  earth.userData.bloomMat = new THREE.ShaderMaterial({
    uniforms: { tNight: { value: tNight }, uSun: sun, uLights: earthMat.uniforms.uLights },
    vertexShader: earthMat.vertexShader,
    fragmentShader: `uniform sampler2D tNight; uniform vec3 uSun; uniform float uLights; varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main(){ float d = dot(normalize(vN), uSun); float night = 1.0 - smoothstep(-0.12, 0.22, d);
        vec3 nl = texture2D(tNight, vUv).rgb; nl = max(pow(nl, vec3(1.6)) - 0.05, 0.0) * vec3(1.0, 0.75, 0.45) * 1.4 * uLights;
        gl_FragColor = vec4(nl * night, 1.0); }`,
  });

  // thin blue atmosphere: brightest right at the limb, fading outward (computed from each ray's closest approach)
  const RA = R * 1.03;
  const atmos = new THREE.Mesh(new THREE.SphereGeometry(RA, 128, 64), new THREE.ShaderMaterial({
    uniforms: { uSun: sun, uC: { value: new THREE.Vector3(0, -R, 0) }, uR: { value: R }, uR2: { value: RA } },
    vertexShader: `varying vec3 vW; void main(){ vec4 wp = modelMatrix * vec4(position, 1.0); vW = wp.xyz; gl_Position = projectionMatrix * viewMatrix * wp; }`,
    fragmentShader: `uniform vec3 uSun, uC; uniform float uR, uR2; varying vec3 vW;
      void main(){ vec3 d = normalize(vW - cameraPosition); vec3 oc = uC - cameraPosition; float tc = dot(oc, d);
        vec3 cp = cameraPosition + d * tc; float b = length(cp - uC);
        float h = clamp((b - uR) / (uR2 - uR), 0.0, 1.0);
        float i = exp(-h * 4.5) * (1.0 - h);
        float lit = 0.22 + 0.78 * smoothstep(-0.3, 0.3, dot(normalize(cp - uC), uSun));
        gl_FragColor = vec4(vec3(0.30, 0.60, 1.0) * i * 1.25 * lit, 1.0); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.BackSide, toneMapped: false,
  }));
  atmos.position.set(0, -R, 0);
  root.add(atmos);

  // stars
  const rnd = mulberry32(5150);
  const NS = 2600, sp = new Float32Array(NS * 3), ss = new Float32Array(NS);
  for (let i = 0; i < NS; i++) {
    const u = rnd() * 2 - 1, a = rnd() * Math.PI * 2, r = Math.sqrt(1 - u * u);
    sp.set([r * Math.cos(a) * 1500, u * 1500, r * Math.sin(a) * 1500], i * 3);
    ss[i] = rnd() < 0.06 ? 2.6 + rnd() * 1.4 : 1.0 + rnd() * 1.1;
  }
  const sg = new THREE.BufferGeometry();
  sg.setAttribute('position', new THREE.BufferAttribute(sp, 3)); sg.setAttribute('aS', new THREE.BufferAttribute(ss, 1));
  const stars = new THREE.Points(sg, new THREE.ShaderMaterial({
    vertexShader: `attribute float aS; varying float vS; void main(){ vS = aS; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); gl_PointSize = aS; }`,
    fragmentShader: `varying float vS; void main(){ float r = length(gl_PointCoord - 0.5); if (r > 0.5) discard; float a = smoothstep(0.5, 0.1, r) * min(1.0, vS * 0.35); gl_FragColor = vec4(vec3(0.85, 0.9, 1.0) * a, 1.0); }`,
    transparent: true, depthWrite: false, toneMapped: false,
  }));
  stars.frustumCulled = false;
  root.add(stars);

  // the column of notes: a glowing beam whose width stays a few pixels at any distance
  const colMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.2, 2.0, 1.1), toneMapped: false });
  const column = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 1, 16, 1, false), colMat);
  column.layers.enable(1);
  root.add(column);
  const tipMat = new THREE.SpriteMaterial({ map: glowSprite(), color: new THREE.Color(3.0, 2.6, 1.4), blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false });
  const tip = new THREE.Sprite(tipMat);
  tip.layers.enable(1);
  root.add(tip);

  // one tick for every space-station height along the column
  const ticks = [];
  const tickMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.4, 2.4, 2.4), toneMapped: false });
  for (let k = 1; k <= 7; k++) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), tickMat);
    m.layers.enable(1);
    m.position.set(0, k * ISS_ALT, 0);
    root.add(m); ticks.push(m);
  }

  // the space station's orbit: a thin dashed ring 420 km up, and a small station on it
  const ringR = R + ISS_ALT;
  const ringMat = new THREE.ShaderMaterial({
    uniforms: { uOp: { value: 0 } },
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `uniform float uOp; varying vec2 vUv; void main(){ float dash = step(0.45, fract(vUv.x * 360.0)); gl_FragColor = vec4(vec3(0.75, 0.88, 1.0) * 1.6 * dash * uOp, 1.0); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false,
  });
  const ring = new THREE.Mesh(new THREE.TorusGeometry(ringR, 0.05, 6, 1440), ringMat);
  ring.position.set(0, -R, 0);
  root.add(ring);
  const iss = buildISS();
  const glint = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowSprite(), color: new THREE.Color(1.2, 1.4, 1.8), blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }));
  glint.layers.enable(1); glint.scale.setScalar(0.8); glint.material.opacity = 0.6; iss.add(glint);
  const issAng = 0.055;   // a little to the right of the column along the orbit
  iss.position.set(ringR * Math.sin(issAng), -R + ringR * Math.cos(issAng), 0);
  iss.rotation.z = -issAng;
  root.add(iss);

  const E = { root, globe, earth, atmos, stars, issAng, column, tip, ticks, ring, ringMat, iss, sun, earthMat };
  return E;
}

// stack height h (units) at time t is set by the shot; sizes follow the camera so they stay readable
const _v = new THREE.Vector3();
export function setEarth(E, { h, camera, lit = 7, ringOp = 1, px = 1 }) {
  const dist = camera.position.distanceTo(_v.set(0, Math.max(0.01, h * 0.5), 0));
  const pxU = 2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * dist / 1920;   // world units per screen pixel
  const r = Math.max(0.004, 2.6 * px * pxU);
  E.column.visible = h > 0.001;
  E.column.scale.set(r, Math.max(0.001, h), r);
  E.column.position.set(0, h / 2, 0);
  E.tip.position.set(0, h, 0);
  E.tip.scale.setScalar(70 * pxU);
  E.ticks.forEach((m, i) => {
    const on = (i + 1) * ISS_ALT <= h + 1e-6 && i < lit;
    m.visible = on;
    m.scale.set(28 * pxU, 3.2 * pxU, 28 * pxU);
  });
  E.iss.scale.setScalar(Math.max(0.05, 150 * pxU));
  E.ringMat.uniforms.uOp.value = ringOp;
  return pxU;
}

function glowSprite() {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d');
  const r = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(0.18, 'rgba(255,240,200,0.75)'); r.addColorStop(0.5, 'rgba(255,210,120,0.18)'); r.addColorStop(1, 'rgba(255,200,100,0)');
  g.fillStyle = r; g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

// a simple station silhouette (truss, four solar wings, modules), 1 unit wide
function buildISS() {
  const g = new THREE.Group();
  const metal = new THREE.MeshStandardMaterial({ color: 0xe9edf3, roughness: 0.4, metalness: 0.3, emissive: 0x9aa3b0, emissiveIntensity: 0.55 });
  const panel = new THREE.MeshStandardMaterial({ color: 0x3a5a9e, roughness: 0.3, metalness: 0.3, emissive: 0x2a4b8f, emissiveIntensity: 0.9 });
  const truss = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.035, 0.035), metal);
  g.add(truss);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
    const w = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.006, 0.36), panel);
    w.position.set(sx * (0.36 + (sz > 0 ? 0 : 0.13)), 0, sz * 0.21);
    g.add(w);
  }
  const mod = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.38, 12), metal);
  mod.rotation.x = Math.PI / 2; g.add(mod);
  const mod2 = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.026, 0.2, 12), metal);
  mod2.position.set(0.0, 0, 0); mod2.rotation.z = Math.PI / 2; g.add(mod2);
  const rad = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.004, 0.16), metal);
  rad.position.set(0.12, 0, -0.1); g.add(rad);
  g.traverse(o => { if (o.isMesh) o.layers.enable(0); });
  return g;
}

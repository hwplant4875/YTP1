// Cinematic finishing for every 3D shot: bloom, depth of field, and a finishing shader
// (noir grade that keeps only warm amber saturated, film grain, vignette, slight lens fringe).
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const FinishShader = {
  uniforms: {
    tDiffuse: { value: null }, time: { value: 0 }, grain: { value: 0.06 }, vignette: { value: 0.55 },
    fringe: { value: 0.0018 }, keepWarm: { value: 1.0 }, fade: { value: 1.0 }, flash: { value: 0.0 },
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform float time, grain, vignette, fringe, keepWarm, fade, flash; varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + time*61.7) * 43758.5453); }
    void main(){
      vec2 c = vUv - 0.5;
      float r2 = dot(c,c);
      vec2 off = c * fringe * (1.0 + 4.0*r2);
      vec3 col = vec3(texture2D(tDiffuse, vUv + off).r, texture2D(tDiffuse, vUv).g, texture2D(tDiffuse, vUv - off).b);
      // noir grade: desaturate everything except warm amber hues
      float l = dot(col, vec3(0.299,0.587,0.114));
      float warm = clamp((col.r - col.b) * 3.0, 0.0, 1.0) * keepWarm;
      col = mix(vec3(l) * vec3(1.0,0.985,0.96), col, 0.18 + 0.82*warm);
      // soft S-curve and lifted blacks like old film stock
      col = col*col*(3.0-2.0*col)*0.85 + col*0.15;
      col = col*0.96 + 0.012;
      col *= 1.0 - vignette * smoothstep(0.08, 0.62, r2*1.6);
      col += (hash(vUv*vec2(1920.0,1080.0)) - 0.5) * grain;
      col = mix(col, vec3(1.0,0.97,0.92), flash);
      gl_FragColor = vec4(col * fade, 1.0);
    }`,
};

export function makeComposer(THREE, renderer, scene, camera, W, H, opt = {}) {
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = opt.exposure ?? 1.0;
  const composer = new EffectComposer(renderer);
  composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), opt.bloom ?? 0.75, opt.bloomRadius ?? 0.7, opt.bloomThreshold ?? 0.62);
  composer.addPass(bloom);
  let bokeh = null;
  if (opt.dof) {
    bokeh = new BokehPass(scene, camera, { focus: opt.dof.focus ?? 8, aperture: opt.dof.aperture ?? 0.0012, maxblur: opt.dof.maxblur ?? 0.006 });
    composer.addPass(bokeh);
  }
  composer.addPass(new OutputPass());
  const finish = new ShaderPass(FinishShader);
  composer.addPass(finish);
  return { composer, bloom, bokeh, finish };
}

// soft round glow (camera-facing) for bulbs and headlights
export function glow(THREE, color, size, strength = 1) {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d');
  const grd = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grd.addColorStop(0, `rgba(255,255,255,${strength})`); grd.addColorStop(0.18, `rgba(255,255,255,${0.45 * strength})`);
  grd.addColorStop(0.5, `rgba(255,255,255,${0.08 * strength})`); grd.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grd; g.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(c);
  const m = new THREE.SpriteMaterial({ map: tex, color, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, fog: false });
  const s = new THREE.Sprite(m); s.scale.set(size, size, 1);
  return s;
}

// fake volumetric light: an open cone with alpha fading along its length
export function beam(THREE, color, length, radius, opacity = 0.12) {
  const geo = new THREE.ConeGeometry(radius, length, 48, 1, true);
  geo.translate(0, -length / 2, 0);
  const mat = new THREE.ShaderMaterial({
    uniforms: { color: { value: new THREE.Color(color) }, opacity: { value: opacity }, len: { value: length } },
    vertexShader: `varying float vY; varying vec3 vN; varying vec3 vV;
      void main(){ vY = position.y; vec4 mv = modelViewMatrix*vec4(position,1.0); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix*mv; }`,
    fragmentShader: `uniform vec3 color; uniform float opacity, len; varying float vY; varying vec3 vN; varying vec3 vV;
      void main(){ float along = clamp(1.0 + vY/len, 0.0, 1.0); float edge = pow(abs(dot(vN, vV)), 1.6);
        gl_FragColor = vec4(color, opacity * along * along * edge); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  });
  return new THREE.Mesh(geo, mat);
}

// normal map from a height-drawing callback (white = raised)
export function normalFromHeight(THREE, w, h, draw, strength = 2.0, repeat = [1, 1]) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const src = g.getImageData(0, 0, w, h).data;
  const out = g.createImageData(w, h);
  const H = (x, y) => src[(((y + h) % h) * w + ((x + w) % w)) * 4] / 255;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const dx = (H(x - 1, y) - H(x + 1, y)) * strength, dy = (H(x, y - 1) - H(x, y + 1)) * strength;
    const n = Math.hypot(dx, dy, 1); const i = (y * w + x) * 4;
    out.data[i] = (dx / n * 0.5 + 0.5) * 255; out.data[i + 1] = (dy / n * 0.5 + 0.5) * 255; out.data[i + 2] = (1 / n * 0.5 + 0.5) * 255; out.data[i + 3] = 255;
  }
  g.putImageData(out, 0, 0);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat);
  return t;
}

// East German border guard: long coat, peaked cap, rifle slung on the shoulder.
// Returns { group, head } so shots can turn the head to follow a train.
export function borderGuard(THREE, mat) {
  const grp = new THREE.Group();
  const M = (geo, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = true; grp.add(m); return m; };
  // greatcoat: lathe profile from hem to collar
  const prof = [[0.0, 0.42], [0.33, 0.42], [0.31, 0.6], [0.26, 0.9], [0.22, 1.12], [0.24, 1.3], [0.26, 1.42], [0.22, 1.5], [0.12, 1.55], [0.0, 1.56]]
    .map(([r, y]) => new THREE.Vector2(r, y));
  const coat = M(new THREE.LatheGeometry(prof, 28), 0, 0, 0); coat.scale.set(1, 1, 0.72);
  M(new THREE.CylinderGeometry(0.235, 0.235, 0.06, 24), 0, 1.06, 0).scale.set(1, 1, 0.74);          // belt
  for (const sx of [-1, 1]) {
    M(new THREE.CylinderGeometry(0.07, 0.06, 0.42, 12), sx * 0.11, 0.21, 0);                     // boots
    const arm = M(new THREE.CapsuleGeometry(0.062, 0.5, 4, 10), sx * 0.28, 1.17, 0.02); arm.rotation.z = sx * 0.1;
  }
  M(new THREE.CylinderGeometry(0.055, 0.07, 0.1, 12), 0, 1.6, 0);                                 // neck
  const head = new THREE.Group(); head.position.set(0, 1.66, 0); grp.add(head);
  const H = (geo, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); head.add(m); return m; };
  H(new THREE.SphereGeometry(0.105, 20, 16), 0, 0.03, 0).scale.set(0.92, 1.08, 1.0);
  H(new THREE.CylinderGeometry(0.135, 0.115, 0.075, 24), 0, 0.14, 0);                            // cap crown
  const front = H(new THREE.BoxGeometry(0.2, 0.08, 0.04), 0, 0.17, 0.1); front.rotation.x = -0.2; // raised front
  const visor = H(new THREE.CylinderGeometry(0.1, 0.1, 0.012, 20, 1, false, -Math.PI / 2, Math.PI), 0, 0.105, 0.05); visor.rotation.x = 0.25;
  // rifle on a sling over the right shoulder, muzzle up
  const rifle = new THREE.Group(); rifle.position.set(0.2, 1.18, -0.14); rifle.rotation.z = -0.28; grp.add(rifle);
  const R = (geo, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); rifle.add(m); return m; };
  R(new THREE.BoxGeometry(0.05, 0.62, 0.06), 0, 0, 0);
  R(new THREE.CylinderGeometry(0.012, 0.012, 0.3, 8), 0, 0.45, 0);
  R(new THREE.BoxGeometry(0.04, 0.14, 0.05), 0, -0.05, 0.05).rotation.x = 0.4;                    // magazine
  return { group: grp, head };
}

export const smooth = t => t <= 0 ? 0 : t >= 1 ? 1 : t * t * t * (t * (6 * t - 15) + 10);
// deterministic flicker: 1 = on. warm-up flicker like an old bulb catching
export function flicker(t, onAt, seed = 1) {
  if (t < onAt) return 0;
  const d = t - onAt;
  if (d > 0.9) return 0.94 + 0.06 * Math.sin(t * 13 + seed) * Math.sin(t * 3.1 + seed * 2);
  const k = Math.floor(d * 22 + seed * 7);
  const r = Math.abs(Math.sin(k * 12.9898 + seed * 78.233) * 43758.5453) % 1;
  return r > 0.45 ? 0.6 + 0.4 * r : 0.05;
}

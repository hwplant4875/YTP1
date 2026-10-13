// Shared helpers for the France long-form scenes (france_map.js, france_lycee.js).
// People here are FACELESS mannequins by rule: smooth round heads, no eyes / nose / mouth / ears / brows / painted detail.
export const AMBER_HI = 0xffb25c;   // channel highlight
export const CREAM = '#efe6d2';

// shot name may carry a length: "spread:20" stretches the 6 s timeline to 20 s
export function shotArgs(def) {
  const raw = new URLSearchParams(location.search).get('shot') || def;
  const [name, len] = raw.split(':');
  return { name, len: len ? +len : null };
}

// hermite camera path through timed keys [t, [x,y,z, tx,ty,tz]]; holds at the ends
export function path(keys) {
  const n = keys.length;
  const tan = keys.map((k, i) => {
    const a = keys[Math.max(0, i - 1)], b = keys[Math.min(n - 1, i + 1)], dt = b[0] - a[0];
    return k[1].map((_, j) => (i === 0 || i === n - 1) ? 0 : dt > 0 ? (b[1][j] - a[1][j]) / dt : 0);
  });
  return (t) => {
    if (t <= keys[0][0]) return keys[0][1].slice();
    if (t >= keys[n - 1][0]) return keys[n - 1][1].slice();
    let i = 0; while (keys[i + 1][0] < t) i++;
    const [t0, p0] = keys[i], [t1, p1] = keys[i + 1], h = t1 - t0, s = (t - t0) / h;
    const h00 = 2 * s ** 3 - 3 * s ** 2 + 1, h10 = s ** 3 - 2 * s ** 2 + s, h01 = -2 * s ** 3 + 3 * s ** 2, h11 = s ** 3 - s ** 2;
    return p0.map((v, j) => h00 * v + h10 * h * tan[i][j] + h01 * p1[j] + h11 * h * tan[i + 1][j]);
  };
}
export const clamp01 = (x) => x < 0 ? 0 : x > 1 ? 1 : x;
export const sstep = (a, b, x) => { const t = clamp01((x - a) / (b - a)); return t * t * (3 - 2 * t); };

export async function fontsReady() {
  try { await Promise.all(['600 40px Inter', '500 40px Inter', '700 40px Inter', '800 40px "Inter Display"'].map(f => document.fonts.load(f))); } catch (e) { /* system font fallback */ }
}

// cream text label as a constant-screen-size sprite. anchor 'left' puts the text to the right of the point.
export function label(THREE, text, { size = 0.028, sub = null, color = CREAM, subColor = '#a9c4e8', weight = 600, anchor = 'left', opacity = 1, tracking = 0.14, gap = 20 } = {}) {
  const c = document.createElement('canvas'); const g = c.getContext('2d');
  const fs = 64, fs2 = 50;
  const font = `${weight} ${fs}px Inter, "DejaVu Sans", sans-serif`, font2 = `500 ${fs2}px Inter, "DejaVu Sans", sans-serif`;
  const T = text.toUpperCase();
  const spaced = (s, f, track) => { g.font = f; let w = 0; for (const ch of s) w += g.measureText(ch).width + track; return w - track; };
  const w1 = spaced(T, font, fs * tracking), w2 = sub ? spaced(sub, font2, fs2 * 0.06) : 0;
  const pad = 24, W = Math.ceil(Math.max(w1, w2) + pad * 2), H = sub ? 170 : 100;
  c.width = W * 2 + gap * 2; c.height = H;   // double width so the anchor point sits at the canvas centre
  const x0 = anchor === 'left' ? c.width / 2 + gap : anchor === 'right' ? c.width / 2 - gap - Math.max(w1, w2) : c.width / 2 - Math.max(w1, w2) / 2;
  const draw = (s, f, track, x, y, col) => { g.font = f; g.fillStyle = col; g.textBaseline = 'middle'; for (const ch of s) { g.fillText(ch, x, y); x += g.measureText(ch).width + track; } };
  g.shadowColor = 'rgba(0,0,0,0.85)'; g.shadowBlur = 14;
  draw(T, font, fs * tracking, x0, sub ? 50 : H / 2, color);
  if (sub) draw(sub, font2, fs2 * 0.06, x0, 122, subColor);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  const m = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false, depthWrite: false, sizeAttenuation: false, fog: false, opacity, toneMapped: false });
  const s = new THREE.Sprite(m);
  s.scale.set(size * c.width / c.height, size, 1);
  s.renderOrder = 20;
  return s;
}

// ------------------------------------------------------------------ faceless mannequins
// All parts are smooth primitives. The head is a plain ellipsoid. Origin at the feet, facing +z.
// opts: { height, build: 'student'|'teacher'|'police', hood, backpack, seated, sign, armsUp, mat, accent, rot }
export function figure(THREE, mats, o = {}) {
  const g = new THREE.Group();
  const s = (o.height ?? 1.7) / 1.7;
  const body = mats.body, skin = mats.head ?? mats.body, dark = mats.dark ?? mats.body;
  const M = (geo, m, x, y, z, rx = 0, ry = 0, rz = 0, parent = g) => {
    const me = new THREE.Mesh(geo, m); me.position.set(x, y, z); me.rotation.set(rx, ry, rz); me.castShadow = true; me.receiveShadow = true; parent.add(me); return me;
  };
  const seated = !!o.seated, police = o.build === 'police';
  const hipY = seated ? 0.46 : 0.86;
  // legs
  for (const sx of [-1, 1]) {
    if (seated) {
      M(new THREE.CapsuleGeometry(0.075, 0.36, 4, 10), dark, sx * 0.1, hipY, 0.2, Math.PI / 2);            // thigh forward
      M(new THREE.CapsuleGeometry(0.068, 0.36, 4, 10), dark, sx * 0.1, 0.24, 0.4);                         // shin down
      M(new THREE.BoxGeometry(0.11, 0.07, 0.24), dark, sx * 0.1, 0.035, 0.46);                             // shoe
    } else {
      M(new THREE.CapsuleGeometry(0.075, 0.68, 4, 10), dark, sx * 0.1, 0.46, 0);
      M(new THREE.BoxGeometry(0.11, 0.07, 0.24), police ? dark : (mats.shoe ?? dark), sx * 0.1, 0.035, 0.05);
    }
  }
  // torso: lathe profile (hoodie / jacket / police jacket with padding)
  const prof = police
    ? [[0, 0], [0.2, 0], [0.24, 0.12], [0.27, 0.35], [0.29, 0.52], [0.24, 0.6], [0.1, 0.64], [0, 0.65]]
    : [[0, 0], [0.18, 0], [0.2, 0.1], [0.215, 0.32], [0.23, 0.5], [0.18, 0.58], [0.08, 0.62], [0, 0.63]];
  const torso = M(new THREE.LatheGeometry(prof.map(([r, y]) => new THREE.Vector2(r, y)), 24), body, 0, hipY - 0.04, 0);
  torso.scale.set(1, 1, 0.7);
  const shY = hipY + 0.5;
  // arms
  const armUp = o.armsUp ?? 0;
  for (const sx of [-1, 1]) {
    const arm = new THREE.Group(); arm.position.set(sx * 0.24, shY, 0); g.add(arm);
    const up = (armUp === 2 || (armUp === 1 && sx > 0)) ? 1 : 0;
    arm.rotation.z = sx * (up ? 2.75 : seated ? 0.1 : 0.12);
    arm.rotation.x = seated ? -0.9 : (o.armFwd ?? 0);
    M(new THREE.CapsuleGeometry(0.06, 0.48, 4, 10), body, 0, -0.27, 0, 0, 0, 0, arm);
    M(new THREE.SphereGeometry(0.055, 12, 10), skin, 0, -0.56, 0, 0, 0, 0, arm);                          // mitten hand
    if (police && sx < 0 && o.shield !== false) { /* shield is added below in world space */ }
  }
  // neck + faceless head
  M(new THREE.CylinderGeometry(0.05, 0.06, 0.09, 12), skin, 0, shY + 0.1, 0);
  const head = M(new THREE.SphereGeometry(0.115, 28, 20), skin, 0, shY + 0.24, 0.0);
  head.scale.set(0.9, 1.08, 0.98);
  if (o.hood) {                                   // hood: a slightly larger shell sitting on the back of the head
    const hood = M(new THREE.SphereGeometry(0.135, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.62), body, 0, shY + 0.25, -0.025, -0.5);
    hood.scale.set(0.95, 1.08, 1.0);
  }
  if (o.hair) {                                   // hair cap (simple shell, no features)
    const hair = M(new THREE.SphereGeometry(0.122, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.5), mats.hair ?? dark, 0, shY + 0.255, -0.01, -0.25);
    hair.scale.set(0.92, 1.05, 1.0);
  }
  if (police) {                                   // riot helmet with a dark visor shell: no face underneath
    const helm = M(new THREE.SphereGeometry(0.15, 28, 18, 0, Math.PI * 2, 0, Math.PI * 0.58), dark, 0, shY + 0.25, 0);
    helm.scale.set(1, 1.0, 1.05);
    const visor = M(new THREE.SphereGeometry(0.155, 28, 12, -Math.PI * 0.42, Math.PI * 0.84, Math.PI * 0.38, Math.PI * 0.3), mats.visor ?? dark, 0, shY + 0.25, 0);
    visor.scale.set(1, 1, 1.06);
    M(new THREE.CylinderGeometry(0.29, 0.29, 0.04, 20), dark, 0, hipY + 0.02, 0).scale.set(1, 1, 0.7);       // belt
    if (o.shield !== false) {
      const sh = M(new THREE.BoxGeometry(0.56, 0.95, 0.025), mats.shield ?? dark, -0.08, hipY + 0.12, 0.3, 0, 0.15, 0);
      sh.castShadow = true;
    }
  }
  if (o.backpack) {
    const bp = M(new THREE.CapsuleGeometry(0.15, 0.18, 4, 12), mats.pack ?? dark, 0, hipY + 0.33, -0.2);
    bp.scale.set(1.05, 1, 0.62);
    for (const sx of [-1, 1]) M(new THREE.TorusGeometry(0.1, 0.018, 6, 16, Math.PI), mats.pack ?? dark, sx * 0.12, hipY + 0.47, -0.07, 0, Math.PI / 2, 0);
  }
  if (o.sign) {                                    // placard held overhead on a stick (texture supplied by the caller)
    const st = M(new THREE.CylinderGeometry(0.014, 0.014, 0.9, 6), mats.stick ?? dark, 0.26, shY + 0.35, 0.06);
    const p = M(new THREE.BoxGeometry(0.7, 0.46, 0.012), o.sign, 0.26, shY + 0.92, 0.07);
  }
  g.scale.setScalar(s);
  if (o.rot) g.rotation.y = o.rot;
  g.userData.head = head;
  return g;
}

// ------------------------------------------------------------------ shared finishing for the newer France scenes
// makeComposer (bloom, optional DOF, noir grade) + a crisp label layer: every constant-size sprite (label()) is moved to
// layer 1 and drawn after bloom/DOF so the type stays sharp.
import { makeComposer } from './look.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
// v2 look: natural colour instead of the house noir grade (which kept only amber saturated). Swaps the finishing
// shader's grade line, everything else (grain, vignette, fringe, film curve) stays as in look.js.
export function naturalGrade(post, sat = 0.92) {
  const m = post.finish.material;
  m.fragmentShader = m.fragmentShader.replace(/float warm = [^;]*;\s*col = mix\([^;]*;/,
    `col = mix(vec3(l), col, ${sat.toFixed(2)});`);
  m.needsUpdate = true;
  return post;
}
export function finishPost(THREE, renderer, scene, camera, W, H, opt = {}) {
  const post = naturalGrade(makeComposer(THREE, renderer, scene, camera, W, H, { bloom: 0.8, bloomRadius: 0.6, bloomThreshold: 0.6, exposure: 1.0, ...opt }));
  post.finish.uniforms.vignette.value = opt.vignette ?? 0.55;
  const labelCam = camera.clone(); labelCam.layers.set(1);
  scene.traverse(o => { if (o.isSprite && o.material.sizeAttenuation === false) o.layers.set(1); });
  const lp = new RenderPass(scene, labelCam); lp.clear = false; lp.clearDepth = true;
  const lpRender = lp.render.bind(lp);
  lp.render = (...args) => { const bg = scene.background, fog = scene.fog; scene.background = null; lpRender(...args); scene.background = bg; scene.fog = fog; };
  post.composer.insertPass(lp, post.composer.passes.length - 2);
  const sync = () => { labelCam.position.copy(camera.position); labelCam.quaternion.copy(camera.quaternion); labelCam.fov = camera.fov; labelCam.updateProjectionMatrix(); };
  return { ...post, labelCam, sync };
}
// call after adding late sprites (labels created after finishPost)
export function toLabelLayer(obj) { obj.traverse(o => { if (o.isSprite && o.material.sizeAttenuation === false) o.layers.set(1); }); }

// canvas texture (sRGB, clamped) from a draw callback
export function ctex(THREE, w, h, draw, { repeat = null, aniso = 8 } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = aniso;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat); }
  return t;
}
// letter-spaced text on a 2D canvas context
export function spacedText(g, s, x, y, track = 0, align = 'left') {
  let w = 0; for (const ch of s) w += g.measureText(ch).width + track; w -= track;
  let cx = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
  for (const ch of s) { g.fillText(ch, cx, y); cx += g.measureText(ch).width + track; }
  return w;
}
// a dark studio floor that fades into the fog: soft radial pool of light baked into the texture
export function studioFloor(THREE, { size = 80, tone = 26, pool = 0.18, grid = 0 } = {}) {
  const tex = ctex(THREE, 1024, 1024, (g, w, h) => {
    g.fillStyle = `rgb(${tone},${tone},${tone - 2})`; g.fillRect(0, 0, w, h);
    const grd = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
    grd.addColorStop(0, `rgba(255,236,210,${pool})`); grd.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = grd; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 26000; i++) { const v = Math.random() * 40; g.fillStyle = `rgba(${v},${v},${v},0.06)`; g.fillRect(Math.random() * w, Math.random() * h, 2, 2); }
    if (grid) { g.strokeStyle = `rgba(230,220,200,${grid})`; g.lineWidth = 1; for (let k = 0; k <= w; k += w / 32) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k, h); g.stroke(); g.beginPath(); g.moveTo(0, k); g.lineTo(w, k); g.stroke(); } }
  });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.55, metalness: 0.2 }));
  m.rotation.x = -Math.PI / 2; m.receiveShadow = true; return m;
}
// shot timing: "name:seconds" stretches the authored base length
export function timing(base) { const { name, len } = shotArgs(''); const k = len ? len / base : 1; return { name, k }; }
// smooth ease on [0,1]
export const ease = (x) => { x = clamp01(x); return x * x * x * (x * (6 * x - 15) + 10); };

// "Data Marble Race" v3: 16 countries, marble size scaled by population, colourful themed track, photo-finish slow motion.
// Physics is precomputed in sim.mjs (race.json); this file only draws it.
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const easeOut = t => 1 - Math.pow(1 - t, 3);
const easeInOut = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const easeOutBack = t => { const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const POP = p => p >= 1000 ? (p / 1000).toFixed(2).replace(/0$/, '') + 'B' : (p >= 10 ? Math.round(p) : p.toFixed(1)) + 'M';
let META = { key: 'pop', subtitle: 'Marble size = Population', label: 'population', prefix: 'pop. ' };
const FMT = v => META.key === 'area' ? (v >= 1 ? v.toFixed(1) + 'M km²' : Math.round(v * 1000) + 'K km²') : META.key === 'gdp' ? '$' + v.toFixed(v >= 10 ? 1 : 2) + 'T' : POP(v);
const DSP = r => r.disp ?? FMT(r.pop);
// Shorts UI covers x > 900 below y 1035 and everything below y 1540; keep graphics out of it
const SAFE_CX = 490;

// timeline: video starts mid-fall; the winner's finish plays in slow motion (keep in sync with audio/mix.py)
export const TIMING = { LEAD: -0.8, PRE: 1.0, POST: 0.35, RATE: 0.3, END: 2.8 };
export function timeline(R) {
  const tw = Math.min(...R.res.map(r => r.finish)), last = Math.max(...R.res.map(r => r.finish));
  const A = tw - TIMING.PRE, B = tw + TIMING.POST, tA = A + TIMING.LEAD, span = (B - A) / TIMING.RATE;
  const simAt = t => t < tA ? t - TIMING.LEAD : t < tA + span ? A + (t - tA) * TIMING.RATE : B + (t - tA - span);
  const videoAt = s => s < A ? s + TIMING.LEAD : s < B ? tA + (s - A) / TIMING.RATE : tA + span + (s - B);
  return { tw, last, A, B, tA, span, simAt, videoAt, duration: videoAt(last) + TIMING.END };
}
export let DURATION = 50;

// section colour themes (index = sec in sim.mjs)
const SEC = ['#dfe6f5', '#35d9ff', '#ff4fa3', '#ffd23f', '#a66bff', '#6dff7a', '#ffffff', '#ff8a3d', '#ffc04a'];
const RAINBOW = ['#ff4d6d', '#ff9f1c', '#ffd23f', '#3ee07a', '#35b7ff', '#a66bff'];

const FinishShader = {
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, fade: { value: 1 }, slow: { value: 0 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader: `uniform sampler2D tDiffuse; uniform float time, fade, slow; varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + time*37.1)*43758.5453); }
    void main(){ vec2 c = vUv-0.5; vec3 col = texture2D(tDiffuse, vUv).rgb;
      float v = dot(c*vec2(1.3,1.0), c*vec2(1.3,1.0));
      col *= 1.0 - (0.38 + 0.3*slow)*smoothstep(0.1, 0.7, v*2.2);
      col = mix(col, col*vec3(1.05,1.0,0.92), slow*0.5);
      col += (hash(vUv*vec2(1080.0,1920.0)) - 0.5)*0.014;
      gl_FragColor = vec4(col*fade, 1.0); }`,
};

export async function setup(THREE, renderer, W, H) {
  const R = await (await fetch('/marble/' + (new URLSearchParams(location.search).get('shot') || 'race.json'))).json();
  if (R.meta) META = R.meta;
  const TL = timeline(R); DURATION = TL.duration;
  const T = R.track, N = R.res.length, F = R.frames.length;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b1020);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const camera = new THREE.PerspectiveCamera(38, W / H, 1, 400);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  scene.add(new THREE.HemisphereLight(0xbfd4ff, 0x20182a, 0.55));
  const key = new THREE.DirectionalLight(0xfff2e0, 2.3);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -14, right: 14, top: 22, bottom: -22, near: 1, far: 80 });
  key.shadow.bias = -0.0004; key.shadow.radius = 4;
  scene.add(key, key.target);
  const rim = new THREE.DirectionalLight(0x7aa7ff, 0.9); rim.position.set(-10, 6, -6); scene.add(rim);

  // back board: dark navy with a soft colour wash per section and a fine grid
  const top = 15, boardH = -T.bottom + 30, PX = 24; // px per world unit
  const bc = document.createElement('canvas'); bc.width = 20 * PX; bc.height = Math.ceil(boardH * PX); const bg = bc.getContext('2d');
  bg.fillStyle = '#10162a'; bg.fillRect(0, 0, bc.width, bc.height);
  const secs = T.sections.map(s => s);
  const gy = y => (top - y) * PX;
  secs.forEach((s, i) => {
    const y0 = gy(s.y + 3), y1 = gy(i + 1 < secs.length ? secs[i + 1].y + 3 : T.bottom);
    const gr = bg.createLinearGradient(0, y0, 0, y1); const c = SEC[s.sec] === '#ffffff' ? '#35b7ff' : SEC[s.sec];
    gr.addColorStop(0, c + '00'); gr.addColorStop(0.25, c + '2a'); gr.addColorStop(0.75, c + '22'); gr.addColorStop(1, c + '00');
    bg.fillStyle = gr; bg.fillRect(0, y0, bc.width, y1 - y0);
  });
  bg.strokeStyle = 'rgba(255,255,255,0.05)'; bg.lineWidth = 1.5;
  for (let x = 0; x <= bc.width; x += PX * 2) { bg.beginPath(); bg.moveTo(x, 0); bg.lineTo(x, bc.height); bg.stroke(); }
  for (let y = 0; y <= bc.height; y += PX * 2) { bg.beginPath(); bg.moveTo(0, y); bg.lineTo(bc.width, y); bg.stroke(); }
  // little light dots scattered on the board for depth
  for (let i = 0; i < 260; i++) { const x = Math.random() * bc.width, y = Math.random() * bc.height; bg.fillStyle = `rgba(255,255,255,${0.04 + Math.random() * 0.08})`; bg.beginPath(); bg.arc(x, y, 1 + Math.random() * 1.5, 0, 7); bg.fill(); }
  const boardTex = new THREE.CanvasTexture(bc); boardTex.colorSpace = THREE.SRGBColorSpace; boardTex.anisotropy = 8;
  const board = new THREE.Mesh(new THREE.PlaneGeometry(20, boardH), new THREE.MeshStandardMaterial({ map: boardTex, roughness: 0.9, metalness: 0 }));
  board.position.set(0, top - boardH / 2, -0.75); board.receiveShadow = true; scene.add(board);
  const back = new THREE.Mesh(new THREE.PlaneGeometry(200, 400), new THREE.MeshBasicMaterial({ color: 0x080b16 }));
  back.position.set(0, -60, -6); scene.add(back);

  // track pieces, coloured per section with a faint glow
  const mats = {};
  const railMat = sec => mats[sec] ?? (mats[sec] = new THREE.MeshPhysicalMaterial({ color: SEC[sec], emissive: SEC[sec], emissiveIntensity: 0.18, roughness: 0.32, clearcoat: 0.7, clearcoatRoughness: 0.2 }));
  const sideMat = new THREE.MeshPhysicalMaterial({ color: 0x2a3552, roughness: 0.5, metalness: 0.2 });
  const seg = (a, b, th, depth, mat) => {
    const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy);
    const m = new THREE.Mesh(new RoundedBoxGeometry(L + th, th, depth, 3, th * 0.45), mat);
    m.position.set((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0); m.rotation.z = Math.atan2(dy, dx);
    m.castShadow = m.receiveShadow = true; scene.add(m); return m;
  };
  for (const w of T.walls) {
    const side = w.kind === 'side', th = side ? 0.5 : 0.22;
    if (!side && w.pts.length > 3) { // smooth wave rail: one tube along the polyline, offset below the rolling surface
      const pts = w.pts.map((p, i) => { const q = w.pts[Math.min(i + 1, w.pts.length - 1)], o = w.pts[Math.max(i - 1, 0)]; const dx = q[0] - o[0], dy = q[1] - o[1], L = Math.hypot(dx, dy); let nx = -dy / L, ny = dx / L; if (ny > 0) { nx = -nx; ny = -ny; } return new THREE.Vector3(p[0] + nx * 0.11, p[1] + ny * 0.11, 0); });
      const curve = new THREE.CatmullRomCurve3(pts);
      const shape = new THREE.Shape(); shape.absarc(0, 0, 0.11, 0, Math.PI * 2);
      const geo = new THREE.ExtrudeGeometry(new THREE.Shape([new THREE.Vector2(-0.65, -0.11), new THREE.Vector2(0.65, -0.11), new THREE.Vector2(0.65, 0.11), new THREE.Vector2(-0.65, 0.11)]), { steps: 400, extrudePath: curve, bevelEnabled: false });
      const m = new THREE.Mesh(geo, railMat(w.sec)); m.castShadow = m.receiveShadow = true; scene.add(m);
      continue;
    }
    const pts = w.slot === undefined ? w.pts : (() => { // leave a visible slot in the rail where the flipper arm dips through
      const [a, b] = w.pts, f = x => [x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])];
      return [a, f(w.slot + 0.3), null, f(w.slot - 0.3), b];
    })();
    for (let i = 0; i < pts.length - 1; i++) {
      const a = pts[i], b = pts[i + 1]; if (!a || !b) continue;
      const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy); let nx = -dy / L, ny = dx / L;
      if (side) { nx = Math.abs(a[0]) < 0.01 ? 0 : (a[0] < 0 ? -1 : 1); ny = 0; } else if (ny > 0) { nx = -nx; ny = -ny; }
      const o = th / 2;
      seg([a[0] + nx * o, a[1] + ny * o], [b[0] + nx * o, b[1] + ny * o], th, 1.3, side ? (Math.abs(a[0]) < 0.01 ? railMat(3) : sideMat) : railMat(w.sec));
    }
  }
  // pegs: rainbow rows
  const pegMats = RAINBOW.map(c => new THREE.MeshPhysicalMaterial({ color: c, emissive: c, emissiveIntensity: 0.25, metalness: 0.3, roughness: 0.25, clearcoat: 1 }));
  for (const p of T.pegs) {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(p.r, p.r, 1.3, 32), pegMats[(p.c ?? 0) % pegMats.length]);
    m.rotation.x = Math.PI / 2; m.position.set(p.x, p.y, 0); m.castShadow = true; scene.add(m);
  }
  // bumpers: glossy pink pucks with a white ring that flash when hit
  const bumpers = T.bumpers.map((b, j) => {
    const g = new THREE.Group(); g.position.set(b.x, b.y, 0);
    const mat = new THREE.MeshPhysicalMaterial({ color: RAINBOW[j % 2 ? 0 : 5], emissive: RAINBOW[j % 2 ? 0 : 5], emissiveIntensity: 0.25, roughness: 0.25, clearcoat: 1 });
    const body = new THREE.Mesh(new THREE.CylinderGeometry(b.r, b.r, 1.25, 48), mat); body.rotation.x = Math.PI / 2;
    const ringMat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 0.4 });
    const ring = new THREE.Mesh(new THREE.TorusGeometry(b.r * 0.72, 0.07, 12, 48), ringMat); ring.position.z = 0.64;
    const cap = new THREE.Mesh(new THREE.CircleGeometry(b.r * 0.3, 32), ringMat); cap.position.z = 0.64;
    for (const m of [body, ring]) { m.castShadow = true; g.add(m); } g.add(cap);
    scene.add(g); return { g, mat, ringMat };
  });
  const spinMat = new THREE.MeshPhysicalMaterial({ color: SEC[7], emissive: SEC[7], emissiveIntensity: 0.15, roughness: 0.35, clearcoat: 0.8 });
  const hubMat = new THREE.MeshPhysicalMaterial({ color: 0xffc04a, metalness: 1, roughness: 0.22 });
  const flipMat = new THREE.MeshPhysicalMaterial({ color: 0xff1f4b, emissive: 0xff1f4b, emissiveIntensity: 0.55, roughness: 0.3, clearcoat: 1 });
  const spinners = T.spinners.map(sp => {
    const g = new THREE.Group(); g.position.set(sp.x, sp.y, 0);
    if (sp.arms === 1) { // the flipper: one red arm on a gold hub, hinged in the floor
      const arm = new THREE.Mesh(new RoundedBoxGeometry(sp.len, sp.w, 0.9, 3, 0.11), flipMat); arm.position.x = sp.len / 2;
      const tip = new THREE.Mesh(new THREE.CylinderGeometry(sp.w * 0.62, sp.w * 0.62, 0.95, 24), hubMat); tip.rotation.x = Math.PI / 2; tip.position.x = sp.len - 0.05;
      const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 1.35, 32), hubMat); hub.rotation.x = Math.PI / 2;
      for (const m of [arm, tip, hub]) { m.castShadow = true; g.add(m); }
      scene.add(g); return g;
    }
    const a = new THREE.Mesh(new RoundedBoxGeometry(sp.len, sp.w, 1.1, 3, 0.1), spinMat);
    const b = new THREE.Mesh(new RoundedBoxGeometry(sp.w, sp.len, 1.1, 3, 0.1), spinMat);
    const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.32, 1.3, 32), hubMat); hub.rotation.x = Math.PI / 2;
    for (const m of [a, b, hub]) { m.castShadow = true; g.add(m); }
    scene.add(g); return g;
  });
  const L = T.lips, lipMat = new THREE.MeshPhysicalMaterial({ color: 0xff2d55, roughness: 0.3, clearcoat: 1, emissive: 0x400010 });
  const mkLip = s => { const g = new THREE.Group(); const m = seg([s * L.outer, L.y], [s * L.inner, L.y - 0.5], 0.24, 1.35, lipMat); scene.remove(m); g.add(m); scene.add(g); return g; };
  const lips = [mkLip(-1), mkLip(1)];
  // finish line: chequered strip with a glow strip
  const fc = document.createElement('canvas'); fc.width = 64; fc.height = 512; const fg = fc.getContext('2d');
  for (let y = 0; y < 16; y++) for (let x = 0; x < 2; x++) { fg.fillStyle = (x + y) % 2 ? '#111' : '#fff'; fg.fillRect(x * 32, y * 32, 32, 32); }
  const fl = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 4), new THREE.MeshStandardMaterial({ map: new THREE.CanvasTexture(fc), roughness: 0.6, emissive: 0xffffff, emissiveIntensity: 0.15 }));
  fl.position.set(T.finishX, T.finishY + 1.6, -0.7); scene.add(fl);

  const tl = new THREE.TextureLoader(), flags = {};
  const marbles = await Promise.all(R.res.map(r => new Promise(res => tl.load(`/marble/flags/${r.code}.png`, tex => {
    flags[r.code] = tex.image;
    tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
    tex.wrapS = THREE.RepeatWrapping; tex.repeat.set(2, 1); tex.offset.set(0.25, 0);
    const mat = new THREE.MeshPhysicalMaterial({ map: tex, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 0.9 });
    const m = new THREE.Mesh(new THREE.SphereGeometry(r.r, 64, 32), mat);
    m.castShadow = true; scene.add(m); res(m);
  }))));

  // bumper hit times (for the flash)
  const bumpHits = T.bumpers.map(() => []);
  for (let k = 0; k < F; k++) T.bumpers.forEach((b, j) => {
    for (let i = 0; i < N; i++) { const p = R.frames[k][i]; if (Math.hypot(p[0] - b.x, p[1] - b.y) < b.r + R.res[i].r + 0.06) { const h = bumpHits[j]; if (!h.length || k / R.fps - h[h.length - 1] > 0.25) h.push(k / R.fps); } }
  });

  // leader changes (held at least 0.5 s), for the "takes the lead" toast
  const leadAt = k => { let b = -1; R.frames[k].forEach((p, i) => { if (R.res[i].finish !== null && k / R.fps > R.res[i].finish) return; if (b < 0 || p[1] < R.frames[k][b][1]) b = i; }); return b; };
  const leads = []; let cur = -1, cand = -1, since = 0;
  for (let k = Math.round(4 * R.fps); k < Math.round(TL.tw * R.fps); k++) {
    const l = leadAt(k);
    if (l !== cand) { cand = l; since = k; }
    if (cand !== cur && k - since >= R.fps * 0.5) { if (cur >= 0) leads.push({ s: since / R.fps, i: cand }); cur = cand; }
  }

  // flipper hits on a marble running 1st or 2nd (sim time), for the "knocked back" toast
  const flips = [];
  for (const [ts, i] of (T.sweeps || [])) {
    const k = Math.min(F - 1, Math.round(ts * R.fps)), st = R.res.map((r, j) => [r.finish !== null && r.finish <= ts ? -1e6 + r.finish : R.frames[k][j][1], j]).sort((a, b) => a[0] - b[0]).map(o => o[1]);
    const done = R.res.filter(r => r.finish !== null && r.finish <= ts).length;
    if (st.indexOf(i) - done <= 1 && st.indexOf(i) >= done && (!flips.length || ts - flips[flips.length - 1].s > 1.2)) flips.push({ s: ts, i });
  }

  // smoothed camera path: follow the leader, pulled toward the pack, low-pass filtered
  const camY = new Float32Array(F), camX = new Float32Array(F);
  for (let k = 0; k < F; k++) {
    const live = R.frames[k].map((p, i) => [p, i]).filter(([p, i]) => !(R.res[i].finish !== null && k / R.fps > R.res[i].finish + 0.5)).sort((a, b) => a[0][1] - b[0][1]);
    const lead = live.length ? live[0][0] : [T.finishX, T.finishY - 3], med = live.length ? live[Math.floor(live.length / 3)][0] : lead;
    camY[k] = Math.min(-3, lead[1] * 0.7 + med[1] * 0.3 + 3.5);
    camX[k] = clamp(lead[0] * 0.6 + med[0] * 0.4, -2.2, 2.2);
  }
  const smooth = (a, rad) => { const o = new Float32Array(F); for (let k = 0; k < F; k++) { let s = 0, w = 0; for (let j = -rad; j <= rad; j++) { const q = clamp(k + j, 0, F - 1), ww = Math.exp(-(j * j) / (2 * (rad / 2.2) ** 2)); s += a[q] * ww; w += ww; } o[k] = s / w; } return o; };
  const sm = smooth(camY, 50), smx = smooth(camX, 70);
  // the two leaders' mean position near the finish, for the slow-motion close-up
  const order = R.res.map((r, i) => [r.finish, i]).sort((a, b) => a[0] - b[0]);
  const pipCam = new THREE.PerspectiveCamera(30, 1, 1, 200);

  const composer = new EffectComposer(renderer); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.3, 0.45, 0.88));
  composer.addPass(new OutputPass());
  const finish = new ShaderPass(FinishShader); composer.addPass(finish);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
  return { THREE, scene, camera, composer, finish, R, T, TL, marbles, spinners, lips, bumpers, bumpHits, leads, flips, order, camY: sm, camX: smx, pipCam, key, flags, W, H, rows: {} };
}

export function update(ctx, t) {
  const { R, TL, camera, marbles, spinners, lips, key } = ctx;
  const s = clamp(TL.simAt(t), 0, (R.frames.length - 1) / R.fps), kf = s * R.fps, k0 = Math.floor(kf), k1 = Math.min(k0 + 1, R.frames.length - 1), fr = kf - k0;
  const f0 = R.frames[k0], f1 = R.frames[k1];
  f0.forEach((p, i) => { const q = f1[i]; marbles[i].position.set(lerp(p[0], q[0], fr), lerp(p[1], q[1], fr), 0); marbles[i].rotation.set(0, 0, lerp(p[2], q[2], fr)); });
  const sp0 = R.spin[k0], sp1 = R.spin[k1];
  spinners.forEach((g, i) => g.rotation.z = lerp(sp0[i], sp1[i], fr));
  const open = lerp(sp0[spinners.length], sp1[spinners.length], fr) * (ctx.T.lips.openTo - ctx.T.lips.inner);
  lips[0].position.x = -open; lips[1].position.x = open;
  ctx.bumpers.forEach((b, j) => { let e = 0; for (const h of ctx.bumpHits[j]) if (h <= s) e = Math.max(e, Math.exp(-(s - h) / 0.18)); b.mat.emissiveIntensity = 0.25 + 1.6 * e; b.ringMat.emissiveIntensity = 0.4 + 2.5 * e; b.g.scale.setScalar(1 + 0.08 * e); });
  let cy = lerp(ctx.camY[k0], ctx.camY[k1], fr), cx = lerp(ctx.camX[k0], ctx.camX[k1], fr), cz = 31;
  // photo finish: ease the camera in onto the two leaders while time slows
  const slow = clamp((t - TL.tA + 0.5) / 0.6) * (1 - clamp((t - (TL.tA + TL.span) - 0.2) / 0.8));
  if (slow > 0) {
    const a = marbles[ctx.order[0][1]].position, b = marbles[ctx.order[1][1]].position, e = easeInOut(slow);
    cx = lerp(cx, (a.x + b.x) / 2 + 1.0, e); cy = lerp(cy, (a.y + b.y) / 2 - 0.5, e); cz = lerp(31, 17, e);
  }
  const sway = Math.sin(t * 0.4) * 0.8 * (1 - slow);
  camera.position.set(cx + sway, cy + 1.6, cz); camera.lookAt(cx + sway * 0.4, cy, 0);
  key.position.set(8, cy + 14, 18); key.target.position.set(0, cy, 0);
  ctx.finish.uniforms.fade.value = clamp((DURATION - t) / 0.8); // no fade-in: marbles are already moving on frame 1
  ctx.finish.uniforms.slow.value = slow;
  ctx.k = k0; ctx.s = s; ctx.slow = slow;
}

// picture-in-picture view of the size gate while the camera follows the leaders
const PIP = { x: 400, y: 1020, w: 440, h: 440 };
function pipAlpha(ctx, tt) {
  const T = ctx.T, win = ctx.TL.tw;
  return clamp((tt - (T.firstThrough - 1.2)) / 0.4) * (1 - clamp((tt - Math.min(T.lipT + 2.6, win - 0.5)) / 0.4));
}
export function post(ctx, renderer, t) {
  const a = pipAlpha(ctx, ctx.s);
  if (a <= 0.02) return;
  const { W, H, T, pipCam } = ctx, L = T.lips;
  const s = 0.7 + 0.3 * easeOut(a), w = PIP.w * s, h = PIP.h * s, x = PIP.x + (PIP.w - w) / 2, y = PIP.y + (PIP.h - h) / 2;
  pipCam.position.set(0.4, L.y + 1.6, 13); pipCam.lookAt(0, L.y + 0.4, 0);
  renderer.setScissorTest(true); renderer.setScissor(x, H - y - h, w, h); renderer.setViewport(x, H - y - h, w, h);
  renderer.render(ctx.scene, pipCam);
  renderer.setScissorTest(false); renderer.setViewport(0, 0, W, H);
}

// ---------- overlay ----------
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function flagDot(g, img, x, y, r) {
  g.save(); g.beginPath(); g.arc(x, y, r, 0, 7); g.clip();
  const s = (2 * r) / img.height; g.drawImage(img, x - img.width * s / 2, y - r, img.width * s, 2 * r); g.restore();
  g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 3; g.beginPath(); g.arc(x, y, r, 0, 7); g.stroke();
}
function standings(ctx, k) {
  const { R } = ctx, tt = k / R.fps;
  return R.res.map((r, i) => ({ i, key: r.finish !== null && r.finish <= tt ? -1e6 + r.finish : R.frames[k][i][1] }))
    .sort((a, b) => a.key - b.key).map(o => o.i);
}

export function overlay(ctx, g, t) {
  const { W, H, R, TL, camera, marbles, flags } = ctx, k = ctx.k, tt = ctx.s;
  g.textBaseline = 'alphabetic';
  const tg = g.createLinearGradient(0, 0, 0, 640); tg.addColorStop(0, 'rgba(5,8,16,0.85)'); tg.addColorStop(1, 'rgba(5,8,16,0)');
  g.fillStyle = tg; g.fillRect(0, 0, W, 640);

  // name tags over the leaders and the big marbles
  g.font = '28px Jua'; g.textAlign = 'center';
  const st = standings(ctx, k);
  const top3 = new Set(st.slice(0, 3));
  const lastIdx = ctx.order[ctx.order.length - 1][1];
  R.res.forEach((r, i) => {
    if (!(top3.has(i) || r.r > 0.55 || (ctx.slow > 0.3 && (i === ctx.order[0][1] || i === ctx.order[1][1]))) || (r.finish !== null && r.finish < tt - 0.3 && i !== lastIdx)) return;
    const v = marbles[i].position.clone(); v.y += r.r + 0.35; const q = v.project(camera);
    const x = (q.x + 1) / 2 * W, y = (1 - q.y) / 2 * H;
    if (y < 380 || y > H - 40) return;
    const label = r.name, w = g.measureText(label).width + 24;
    g.globalAlpha = 0.9; g.fillStyle = 'rgba(8,10,18,0.72)'; rr(g, x - w / 2, y - 30, w, 34, 17); g.fill();
    g.fillStyle = '#fff'; g.fillText(label, x, y - 6); g.globalAlpha = 1;
  });

  // title: big readable subtitle above the question, both shrink a little after 4 s
  const a0 = easeOut(clamp(t / 0.25)), sh = easeOut(clamp((t - 4) / 0.7));
  g.textAlign = 'center'; g.globalAlpha = a0;
  g.shadowColor = 'rgba(0,0,0,0.7)'; g.shadowBlur = 20;
  g.font = `${Math.round(lerp(66, 54, sh))}px Jua`; { const fs = Math.round(lerp(66, 54, sh) * Math.min(1, 940 / g.measureText(META.subtitle).width)); g.font = `${fs}px Jua`; } g.fillStyle = '#ffc04a'; g.fillText(META.subtitle, W / 2, lerp(226, 204, sh));
  g.font = `${Math.round(lerp(84, 60, sh))}px YTSans`; g.fillStyle = '#fff'; g.fillText('Which country wins?', W / 2, lerp(322, 282, sh));
  g.shadowColor = 'transparent'; g.globalAlpha = 1;

  // live leaderboard (top 5) with smooth row moves
  const bx = 70, by = lerp(400, 330, easeOut(clamp((t - 4) / 0.7))), rowH = 64;
  g.fillStyle = 'rgba(8,10,18,0.7)'; rr(g, bx, by, 330, rowH * 5 + 24, 24); g.fill();
  // flash the first row when the lead changes
  const lastLead = ctx.leads.filter(l => l.s <= tt).pop();
  const flash = lastLead ? Math.exp(-(tt - lastLead.s) / 0.35) : 0;
  if (flash > 0.02) { g.fillStyle = `rgba(255,192,74,${0.35 * flash})`; rr(g, bx + 6, by + 8, 318, rowH, 18); g.fill(); }
  for (let pos = 0; pos < st.length; pos++) {
    const i = st[pos], r = R.res[i];
    const row = ctx.rows[i] ?? (ctx.rows[i] = { y: pos });
    row.y = lerp(row.y, pos, 0.22);
    if (row.y > 4.6) continue;
    const y = by + 12 + row.y * rowH, a = clamp(4.9 - row.y);
    g.globalAlpha = a;
    g.font = '30px YTSans'; g.textAlign = 'left'; g.fillStyle = pos === 0 ? '#ffc04a' : 'rgba(255,255,255,0.7)';
    g.fillText(String(pos + 1), bx + 22, y + 42);
    flagDot(g, flags[r.code], bx + 82, y + 32, 20);
    g.font = '28px YTSans'; g.fillStyle = '#fff'; g.fillText(r.name, bx + 114, y + 33);
    g.font = '500 21px Fredoka'; g.fillStyle = 'rgba(255,255,255,0.6)'; g.fillText((r.disp ? '' : META.prefix) + DSP(r), bx + 114, y + 56);
    if (r.finish !== null && r.finish <= tt) { g.fillStyle = '#3ddc84'; g.font = '26px YTSans'; g.textAlign = 'right'; g.fillText('✓', bx + 312, y + 42); }
  }
  g.globalAlpha = 1;
  // "takes the lead" toast under the board
  if (lastLead && tt - lastLead.s < 1.6 && tt < TL.tw) {
    const u = tt - lastLead.s, a = easeOutBack(clamp(u / 0.3)) * (1 - clamp((u - 1.3) / 0.3)), r = R.res[lastLead.i];
    g.save(); g.globalAlpha = clamp(a); g.translate(bx, by + rowH * 5 + 44); g.scale(0.85 + 0.15 * clamp(a), 0.85 + 0.15 * clamp(a));
    g.font = '30px Jua'; const label = `${r.name} takes the lead!`, w = g.measureText(label).width + 84;
    g.fillStyle = '#ffc04a'; rr(g, 0, 0, w, 54, 27); g.fill();
    flagDot(g, flags[r.code], 30, 27, 17);
    g.fillStyle = '#1a1205'; g.textAlign = 'left'; g.fillText(label, 58, 37); g.restore();
  }

  // flipper toast: red pill under the board, wins over the lead toast while it shows
  const lastFlip = ctx.flips.filter(f => f.s <= tt).pop();
  if (lastFlip && tt - lastFlip.s < 1.8) {
    const u = tt - lastFlip.s, a = easeOutBack(clamp(u / 0.25)) * (1 - clamp((u - 1.5) / 0.3)), r = R.res[lastFlip.i];
    g.save(); g.globalAlpha = clamp(a); g.translate(bx, by + rowH * 5 + 108); g.scale(0.8 + 0.2 * clamp(a), 0.8 + 0.2 * clamp(a));
    g.font = '30px Jua'; const label = `${r.name} got flipped back!`, w = g.measureText(label).width + 84;
    g.fillStyle = '#ff2d55'; rr(g, 0, 0, w, 54, 27); g.fill();
    flagDot(g, flags[r.code], 30, 27, 17);
    g.fillStyle = '#fff'; g.textAlign = 'left'; g.fillText(label, 58, 37); g.restore();
  }

  // LIVE tag on the picture-in-picture
  const pa = pipAlpha(ctx, tt);
  if (pa > 0.02) {
    const s = 0.7 + 0.3 * easeOut(pa), w = PIP.w * s, h = PIP.h * s, x = PIP.x + (PIP.w - w) / 2, y = PIP.y + (PIP.h - h) / 2;
    g.save(); g.globalAlpha = pa; g.strokeStyle = '#fff'; g.lineWidth = 6; rr(g, x, y, w, h, 18); g.stroke();
    const blink = 0.55 + 0.45 * Math.cos(t * Math.PI * 2 * 0.9);
    g.shadowColor = 'rgba(0,0,0,0.75)'; g.shadowBlur = 12;
    g.globalAlpha = pa * blink; g.fillStyle = '#ff2d2d'; g.beginPath(); g.arc(x + 40, y + 42, 11, 0, 7); g.fill();
    g.globalAlpha = pa; g.fillStyle = '#fff'; g.font = '32px YTSans'; g.textAlign = 'left'; g.fillText('LIVE', x + 60, y + 54);
    g.restore();
  }
  // slow-motion badge during the photo finish
  if (ctx.slow > 0.02 && tt < TL.B + 0.2) {
    g.save(); g.globalAlpha = ctx.slow; g.textAlign = 'center'; g.shadowColor = 'rgba(0,0,0,0.7)'; g.shadowBlur = 18;
    g.font = '58px YTSans'; g.fillStyle = '#fff'; g.fillText('PHOTO FINISH', SAFE_CX, 1380);
    g.font = '34px Jua'; g.fillStyle = '#ffc04a'; g.fillText(`${R.res[ctx.order[0][1]].name} vs ${R.res[ctx.order[1][1]].name}`, SAFE_CX, 1432);
    g.restore();
  }
  // winner card
  const win = ctx.order[0], second = ctx.order[1], last = ctx.order[ctx.order.length - 1];
  const wt = TL.videoAt(win[0]);
  if (t > wt) {
    fireworks(g, W, t - wt);
    const a = easeOutBack(clamp((t - wt) / 0.6)), fade = 1 - clamp((t - wt - 6.5) / 0.5);
    if (fade > 0) {
      const r = R.res[win[1]];
      g.save(); g.globalAlpha = fade; g.translate(SAFE_CX, 1060); g.scale(a, a);
      g.shadowColor = 'rgba(0,0,0,0.5)'; g.shadowBlur = 40; g.fillStyle = 'rgba(255,255,255,0.97)'; rr(g, -350, -170, 700, 360, 40); g.fill(); g.shadowColor = 'transparent';
      flagDot(g, ctx.flags[r.code], 0, -80, 62);
      g.textAlign = 'center'; g.fillStyle = '#111'; const wtxt = r.name.toUpperCase() + ' WINS'; g.font = '72px YTSans'; const fsz = Math.min(72, 72 * 640 / g.measureText(wtxt).width); g.font = `${Math.floor(fsz)}px YTSans`; g.fillText(wtxt, 0, 60);
      g.font = '36px Jua'; g.fillStyle = '#666'; g.fillText(`by ${(second[0] - win[0]).toFixed(2)}s over ${R.res[second[1]].name}`, 0, 118);
      g.font = '30px Jua'; g.fillStyle = '#999'; g.fillText([META.label, DSP(r)].filter(Boolean).join(' '), 0, 160);
      g.restore();
    }
  }
  if (tt > last[0] - 0.2) {
    const a = easeOut(clamp((tt - last[0] + 0.2) / 0.5)), r = R.res[last[1]];
    const biggest = R.res.every(o => o.pop <= r.pop);
    banner(g, W, a, `${r.name.toUpperCase()} FINISHED LAST`, biggest ? `The biggest marble: ${DSP(r)}${META.key === 'pop' ? ' people' : ''}` : [META.label, DSP(r)].filter(Boolean).join(' '), '#ffc04a');
  }
}

function banner(g, W, a, big, small, color, cx = SAFE_CX) {
  g.save(); g.globalAlpha = a; g.translate(0, (1 - a) * 30);
  g.font = '64px YTSans'; const bw = Math.max(g.measureText(big).width, (g.font = '46px Jua', g.measureText(small).width)) + 80;
  g.fillStyle = 'rgba(8,10,18,0.72)'; rr(g, cx - bw / 2, 1316, bw, 166, 30); g.fill();
  g.textAlign = 'center'; g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 22;
  g.font = '64px YTSans'; g.fillStyle = color; g.fillText(big, cx, 1390);
  g.font = '46px Jua'; g.fillStyle = '#fff'; g.fillText(small, cx, 1452);
  g.restore();
}
// ---------- winner fireworks + confetti (pure function of time since the win, so every frame is independent) ----------
const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const FW_COLORS = ['#ffd34a', '#ff5a7a', '#5ad1ff', '#7dff9a', '#ffffff', '#ff9a3c', '#c58bff'];
const BURSTS = [ // [start s, x, y, color index, size]
  [0.05, 540, 820, 0, 1.15], [0.30, 250, 700, 1, 0.9], [0.45, 830, 690, 2, 0.95], [0.85, 190, 1420, 3, 0.8], [1.0, 900, 1440, 4, 0.85],
  [1.45, 420, 560, 5, 0.9], [1.7, 700, 600, 6, 0.9], [2.2, 540, 760, 0, 1.0], [2.6, 280, 1300, 2, 0.75], [2.9, 820, 1280, 1, 0.75],
];
const glowCache = {};
function glow(col) { // soft round sprite: white core, coloured halo
  if (glowCache[col]) return glowCache[col];
  const c = document.createElement('canvas'); c.width = c.height = 64; const q = c.getContext('2d');
  const rg = q.createRadialGradient(32, 32, 0, 32, 32, 32);
  rg.addColorStop(0, 'rgba(255,255,255,1)'); rg.addColorStop(0.12, 'rgba(255,255,255,0.95)'); rg.addColorStop(0.3, col + 'cc'); rg.addColorStop(1, col + '00');
  q.fillStyle = rg; q.fillRect(0, 0, 64, 64); return (glowCache[col] = c);
}
function fireworks(g, W, dt) {
  if (dt > 6.2) return;
  g.save(); g.globalCompositeOperation = 'lighter';
  BURSTS.forEach(([t0, bx, by, ci, size], b) => {
    const u = dt - t0; if (u < 0 || u > 2.0) return;
    const col = FW_COLORS[ci], n = 96, life = 1 - clamp(u / 2.0);
    // flash at the core
    if (u < 0.18) { const fa = 1 - u / 0.18, rg = g.createRadialGradient(bx, by, 0, bx, by, 160 * size); rg.addColorStop(0, `rgba(255,255,240,${0.55 * fa})`); rg.addColorStop(1, 'rgba(255,255,240,0)'); g.fillStyle = rg; g.fillRect(bx - 170, by - 170, 340, 340); }
    for (let i = 0; i < n; i++) {
      const h1 = hash(b * 97 + i), h2 = hash(b * 31 + i * 7.3), h3 = hash(b * 13 + i * 3.1);
      const ang = (i / n) * Math.PI * 2 + h1 * 0.25, sp = (520 + 300 * h2) * size, k = 2.6;
      const pos = s => { const d = (1 - Math.exp(-k * s)) / k; return [bx + Math.cos(ang) * sp * d, by + Math.sin(ang) * sp * d + 160 * s * s]; };
      const [x, y] = pos(u);
      const tw = 0.55 + 0.45 * Math.sin(u * 38 + i * 2.1); // late twinkle
      const a = life * (u > 1.1 ? tw : 1);
      // fading trail made of a few segments, then a glowing head
      g.lineCap = 'round'; g.strokeStyle = col;
      for (let sgm = 0; sgm < 4; sgm++) {
        const [ax, ay] = pos(Math.max(0, u - 0.035 * (sgm + 1))), [cx, cy] = pos(Math.max(0, u - 0.035 * sgm));
        g.globalAlpha = a * 0.7 * (1 - sgm / 4); g.lineWidth = (4.5 - sgm) * size; g.beginPath(); g.moveTo(ax, ay); g.lineTo(cx, cy); g.stroke();
      }
      const sz = (30 + 16 * h2) * size * (0.6 + 0.4 * life);
      g.globalAlpha = a; g.drawImage(glow(col), x - sz / 2, y - sz / 2, sz, sz);
    }
  });
  g.restore();
  // confetti rain from the top
  g.save();
  const CN = 110;
  for (let i = 0; i < CN; i++) {
    const h1 = hash(i * 5.7 + 1), h2 = hash(i * 9.1 + 2), h3 = hash(i * 2.3 + 3), u = dt - h3 * 0.9;
    if (u < 0) continue;
    const y = -40 + u * (330 + 220 * h2), x = h1 * W + Math.sin(u * (2 + 2 * h2) + i) * 40;
    if (y > 1960) continue;
    const a = clamp((6.2 - dt) / 0.8);
    g.globalAlpha = a; g.fillStyle = FW_COLORS[i % FW_COLORS.length];
    g.translate(x, y); g.rotate(u * (3 + 4 * h1) + i); g.scale(1, Math.cos(u * (5 + 6 * h2) + i));
    g.fillRect(-9, -5, 18, 10); g.setTransform(1, 0, 0, 1, 0, 0);
  }
  g.restore();
}

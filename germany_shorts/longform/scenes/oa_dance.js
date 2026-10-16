// Odd Ages #1: the Strasbourg dancing plague, July 1518. Bright, saturated, game-like 3D with Rocketbox humans.
// World: a cobbled square ringed by colourful half-timbered houses; the pink sandstone cathedral spire rises to the north
// (-z). Frau Troffea (Female_Adult_01) dances; crowds are clones of six avatars recoloured into period wool, women in
// skirts and white coifs, men in caps and hats.
// shots (?shot=name:seconds, camera moves are normalised to the length):
//   crowd_low crowd_faces lone_high spire feet troffea_face collapse getup dozens council stage worse aerial square_wide
//   fallen historian why_sky lone_end
import { loadHuman, POSES } from './lib_human.js';
import { ctex, shotArgs, path } from './france_lib.js';
import { glow } from './look.js';

const X = [1, 0, 0], Y = [0, 1, 0], Z = [0, 0, 1];
const D2R = Math.PI / 180;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ss = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
function rng(seed) { let s = seed * 9301 + 49297; return () => { s = (s * 9301 + 49297) % 233280; return s / 233280; }; }

const CAST = [
  { avatar: 'Female_Adult_01', tex: 'f001', f: true },
  { avatar: 'Female_Adult_05', tex: 'f005', f: true },
  { avatar: 'Female_Adult_07', tex: 'f007', f: true },
  { avatar: 'Male_Adult_02', tex: 'm003', f: false },
  { avatar: 'Male_Adult_05', tex: 'm009', f: false },
  { avatar: 'Male_Adult_08', tex: 'm014', f: false },
  { avatar: 'Male_Adult_03', tex: 'm004', f: false },
];
const WOOL = [0xa8322a, 0x2f5fa8, 0xc9902a, 0x3f7a3a, 0x7a4a2a, 0x8a8f96, 0x6b2f6e, 0xb8642a, 0x2a7a78, 0xd8c8a0];
const SKIRT = [0x9a2a24, 0x2a4f8f, 0x4f6b2a, 0x7a3f26, 0x5a2d62, 0xb07a2a, 0x2a6a68];

// dance pose in the character's frame; e = energy 0..1; returns [pose list, root bob]
function dance(t, seed, e = 1, style = 0) {
  const r = rng(seed); const sp = 1.05 + r() * 0.55, a = r() * 6, b = r() * 6, c = r() * 6;
  const ph = t * sp * Math.PI * 2 + seed;
  const upL = 0.5 + 0.5 * Math.sin(ph * 0.5 + a), upR = 0.5 + 0.5 * Math.sin(ph * 0.5 + b + (style ? 0 : 2));
  const kL = Math.max(0, Math.sin(ph)), kR = Math.max(0, Math.sin(ph + Math.PI));
  const L = [
    ['Bip01_Pelvis', Z, 6 * Math.sin(ph * 0.5) * e],
    ['Bip01_Spine', Z, -7 * Math.sin(ph * 0.5 + 0.4) * e], ['Bip01_Spine1', X, (-5 * Math.abs(Math.sin(ph)) + 3) * e],
    ['Bip01_L_UpperArm', Z, -18 + 125 * upL * e], ['Bip01_R_UpperArm', Z, 18 - 125 * upR * e],
    ['Bip01_L_UpperArm', X, -25 * Math.sin(ph * 0.5 + c) * e], ['Bip01_R_UpperArm', X, 25 * Math.sin(ph * 0.5 + c) * e],
    ['Bip01_L_Forearm', X, -(15 + 55 * (0.5 + 0.5 * Math.sin(ph + c))) * e], ['Bip01_R_Forearm', X, -(15 + 55 * (0.5 + 0.5 * Math.sin(ph + c + 1.3))) * e],
    ['Bip01_L_Thigh', X, -38 * kL * e], ['Bip01_L_Calf', X, 62 * kL * e], ['Bip01_R_Thigh', X, -38 * kR * e], ['Bip01_R_Calf', X, 62 * kR * e],
    ['Bip01_Head', Z, 12 * Math.sin(ph * 0.5 + 1) * e], ['Bip01_Head', X, (-10 + 8 * Math.sin(ph * 0.5)) * e],
  ];
  return [L, 0.035 * Math.max(kL, kR) * e];
}
const FACES = [
  { BrowInnerUp: 1, EyeWideLeft: 0.6, EyeWideRight: 0.6, MouthStretchLeft: 0.5, MouthStretchRight: 0.5, JawOpen: 0.3, AU_InnerBrowRaiser: 0.8, AU_JawDrop: 0.15 },
  { BrowInnerUp: 0.9, BrowDownLeft: 0.3, BrowDownRight: 0.3, EyeSquintLeft: 0.5, EyeSquintRight: 0.5, MouthFrownLeft: 0.6, MouthFrownRight: 0.6, JawOpen: 0.35, AU_LipStretcher: 0.4 },
  { BrowInnerUp: 1, EyeBlinkLeft: 0.35, EyeBlinkRight: 0.35, JawOpen: 0.4, MouthFunnel: 0.2, AU_InnerBrowRaiser: 1, AU_LidDroop: 0.3 },
  { EyeWideLeft: 1, EyeWideRight: 1, BrowInnerUp: 0.8, BrowOuterUpLeft: 0.8, BrowOuterUpRight: 0.8, JawOpen: 0.25, MouthStretchLeft: 0.6, MouthStretchRight: 0.6, AU_UpperLidRaiser: 0.8 },
];

export async function setup(THREE, renderer, W, H) {
  const { name: shot, len: LEN0 } = shotArgs('crowd_low');
  const LEN = LEN0 || 3;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.12;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  const golden = ['why_sky', 'lone_end'].includes(shot);
  const sky = golden ? ['#ffb36b', '#ff7a59', '#6a4fb0'] : ['#bfe6ff', '#5fb4ff', '#1f6fe0'];
  scene.background = ctex(THREE, 64, 512, (g, w, h) => { const gr = g.createLinearGradient(0, h, 0, 0); gr.addColorStop(0, sky[0]); gr.addColorStop(0.45, sky[1]); gr.addColorStop(1, sky[2]); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  scene.fog = new THREE.Fog(golden ? 0xffb07a : 0xcfe8ff, 60, 260);
  const world = new THREE.Group(); scene.add(world);

  // ---------------- lights ----------------
  const hemi = new THREE.HemisphereLight(golden ? 0xffc9a0 : 0xcfe6ff, golden ? 0x6a4a3a : 0x9a8670, golden ? 1.4 : 1.9); scene.add(hemi);
  const sun = new THREE.DirectionalLight(golden ? 0xffa060 : 0xfff1dc, golden ? 3.2 : 3.6);
  sun.position.set(golden ? -30 : 14, golden ? 17 : 30, golden ? -14 : 12); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -18, right: 18, top: 18, bottom: -18, near: 1, far: 90 });
  sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.03; scene.add(sun, sun.target);

  // ---------------- square, houses, cathedral ----------------
  buildTown(THREE, world, golden);

  // ---------------- people ----------------
  const P = [];   // {h, x, z, ry, seed, e, face, hero}
  async function person(ci, o = {}) {
    const c = CAST[ci], r = rng((o.seed ?? P.length) + 11);
    const tint = o.tint ?? WOOL[Math.floor(r() * WOOL.length)], tint2 = o.tint2 ?? (c.f ? tint : WOOL[Math.floor(r() * WOOL.length)]);
    const h = await loadHuman(THREE, { avatar: c.avatar, tex: c.tex, morph: !!o.face, recolor: tint, recolor2: tint2, shadows: !!o.shadow, texSize: o.hero ? 2048 : 1024 });
    h.root.position.set(o.x ?? 0, 0, o.z ?? 0); h.root.rotation.y = o.ry ?? 0; world.add(h.root);
    h.pose(POSES.stand); const eye = h.eyeLocal();
    costume(THREE, h, c.f, eye, r, o);
    if (!o.shadow) { const b = blob(THREE); b.position.set(0, 0.012, 0); h.root.add(b); }
    const p = { h, ci, seed: o.seed ?? P.length * 7 + 3, e: o.e ?? (0.75 + r() * 0.25), face: o.face, fx: FACES[(o.seed ?? P.length) % FACES.length], dance: o.dance ?? true, x: o.x ?? 0, z: o.z ?? 0, ry: o.ry ?? 0, spin: (o.spin !== undefined ? o.spin : null) ?? (r() - 0.5) * 0.6 };
    P.push(p); return p;
  }
  // crowd ring layout: n dancers scattered in a disc of radius R (keeping a hole of radius r0 around (cx, cz))
  async function crowd(n, R, { cx = 0, cz = 0, r0 = 0, seed = 1, faceNear = null, shadowN = 0, gap = 0.95, faceTo = null } = {}) {
    const r = rng(seed); const pts = [];
    let guard = 0;
    while (pts.length < n && guard++ < n * 50) {
      const a = r() * Math.PI * 2, d = r0 + Math.sqrt(r()) * (R - r0), x = cx + Math.cos(a) * d, z = cz + Math.sin(a) * d;
      if (pts.every(p => (p[0] - x) ** 2 + (p[1] - z) ** 2 > gap ** 2)) pts.push([x, z]);
    }
    let k = 0;
    for (const [x, z] of pts) {
      const near = faceNear ? Math.hypot(x - faceNear[0], z - faceNear[1]) < faceNear[2] : false;
      const ry = faceTo ? Math.atan2(faceTo[0] - x, faceTo[1] - z) + (r() - 0.5) * 1.2 : r() * Math.PI * 2;
      await person(k % CAST.length === 0 ? 1 + (k % 6) : k % CAST.length, { x, z, ry, spin: faceTo ? 0 : undefined, seed: seed * 100 + k, face: near, shadow: k < shadowN });
      k++;
    }
  }

  const camera = new THREE.PerspectiveCamera(40, W / H, 0.05, 900);
  let cam, dof = null, hero = null, extra = () => {};
  const troffea = async (o = {}) => (hero = await person(0, { x: 0, z: 0, ry: 0, face: true, shadow: true, hero: true, tint: 0xf2ece0, tint2: 0xb4231d, skirt: 0xb4231d, seed: 5, e: 1, ...o }));

  if (shot === 'crowd_low') {
    await crowd(64, 5.6, { seed: 3, faceNear: [0, 3.4, 2.6], shadowN: 12, cz: 0, r0: 0, gap: 0.76, faceTo: [0, 9] });
    cam = path([[0, [0.3, 2.3, 7.4, 0, 1.25, 0]], [1, [0.1, 2.0, 6.1, 0, 1.35, -0.5]]]);
    camera.fov = 56;
  } else if (shot === 'crowd_faces') {
    const m = await person(3, { x: 0, z: 0, ry: 0.15, face: true, shadow: true, hero: true, seed: 22, e: 0.45, tint: 0xc9902a, tint2: 0x5a3a22, hat: 'cap', hatColor: 0x2f5fa8 });
    m.fx = { BrowInnerUp: 1, AU_InnerBrowRaiser: 1, EyeWideLeft: 0.7, EyeWideRight: 0.7, JawOpen: 0.35, MouthStretchLeft: 0.55, MouthStretchRight: 0.55, AU_JawDrop: 0.1 };
    await crowd(26, 6, { cz: -3.5, r0: 1.2, seed: 4 });
    cam = path([[0, [0.12, 1.66, 1.15, 0, 1.62, 0]], [1, [0.05, 1.65, 0.9, 0, 1.62, 0]]]); camera.fov = 36; dof = { focus: 0.95, aperture: 0.03 };
  } else if (shot === 'lone_high') {
    await troffea({ z: 2 });
    for (const [x, z, ry, ci] of [[-7, -6, 0.6, 4], [7.5, -4, -0.8, 2], [-6.8, 7, 2.3, 5]]) await person(ci, { x, z, ry, dance: false, seed: x * 3 | 0 });
    cam = path([[0, [2.5, 5.5, 10.5, 0, 1.6, -2]], [1, [1.8, 4.6, 8.8, 0, 1.4, -1]]]); camera.fov = 44;
  } else if (shot === 'spire') {
    await troffea({ z: -2, ry: 0.4 });
    cam = path([[0, [1.4, 0.9, 5.5, -0.5, 2.0, -6]], [0.35, [1.3, 0.95, 5.2, -2, 14, -50]], [1, [1.1, 1.0, 4.6, -12, 70, -95]]]); camera.fov = 54;
  } else if (shot === 'feet') {
    await troffea({ z: 0, e: 1 });
    blood(THREE, world);
    cam = path([[0, [0.75, 0.22, 1.35, 0, 0.15, 0]], [1, [0.45, 0.2, 1.0, 0, 0.15, 0]]]); camera.fov = 38; dof = { focus: 1.2, aperture: 0.03 };
  } else if (shot === 'troffea_face') {
    await troffea({ e: 0.35 });
    hero.fx = { BrowInnerUp: 1, AU_InnerBrowRaiser: 0.8, MouthFrownLeft: 0.7, MouthFrownRight: 0.7, EyeSquintLeft: 0.2, EyeSquintRight: 0.2, JawOpen: 0.12, MouthStretchLeft: 0.3, MouthStretchRight: 0.3, EyeLookUpLeft: 0.1, EyeLookUpRight: 0.1 };
    cam = path([[0, [-0.35, 1.58, 1.0, 0, 1.57, 0]], [1, [-0.1, 1.58, 0.82, 0, 1.57, 0]]]); camera.fov = 32; dof = { focus: 0.85, aperture: 0.035 };
    for (const [x, z, ci] of [[-2.5, -4, 4], [2.2, -5, 2]]) await person(ci, { x, z, ry: 0.2, dance: false, seed: ci + 40 });
  } else if (shot === 'collapse' || shot === 'getup') {
    await troffea({ z: 0, ry: shot === 'collapse' ? -0.9 : 0.25 });
    if (shot === 'collapse') { hero.kneel = (u) => ss(0.15, 0.55, u); hero.fx = FACES[2]; cam = path([[0, [2.2, 1.0, 2.6, 0, 0.8, 0]], [1, [1.8, 0.9, 2.15, 0, 0.65, 0]]]); camera.fov = 40; }
    else { hero.fx = FACES[0]; cam = path([[0, [0.6, 0.35, 2.6, 0, 1.35, 0]], [1, [0.2, 0.35, 2.1, 0, 1.45, 0]]]); camera.fov = 48; }
    for (const [x, z, ci] of [[-3, -5, 5], [3.5, -6, 1], [-5, -2, 3]]) await person(ci, { x, z, ry: 0.3, dance: false, seed: ci + 50 });
  } else if (shot === 'dozens') {
    await crowd(30, 7.5, { seed: 7, shadowN: 8 });
    for (const [x, z, ry, ci] of [[-9.5, -3, 1.4, 4], [-9.5, 2, 1.2, 6], [9.5, 0, -1.4, 2], [9.2, 4, -1.7, 5]]) await person(ci, { x, z, ry, dance: false, seed: ci + 60 });
    cam = path([[0, [0, 2.0, 12, 0, 1.2, 0]], [1, [0, 6.5, 11, 0, 0.8, -1]]]); camera.fov = 45;
  } else if (shot === 'council') {
    const a = await person(6, { x: -0.2, z: 0, ry: 0.3, face: true, shadow: true, hero: true, dance: false, tint: 0x6e1420, tint2: 0x1c1c22, hat: 'beret', hatColor: 0x14141a, seed: 70 });
    const b = await person(4, { x: 0.3, z: -0.8, ry: -0.45, face: true, shadow: true, hero: true, dance: false, tint: 0x1f3f6e, tint2: 0x22222a, hat: 'tall', hatColor: 0x2a2a30, seed: 71 });
    a.fx = { MouthSmileLeft: 0.9, MouthSmileRight: 0.6, AU_L_LipCornerPuller: 0.8, BrowOuterUpRight: 1, AU_R_OuterBrowRaiser: 1, BrowDownLeft: 0.4, EyeSquintLeft: 0.3, CheekSquintLeft: 0.4 };
    b.fx = { BrowInnerUp: 0.6, BrowOuterUpLeft: 0.5, BrowOuterUpRight: 0.5, MouthPressLeft: 0.4, MouthPressRight: 0.4, AU_LipPressor: 0.3 };
    a.pose = [['Bip01_R_UpperArm', Z, -35], ['Bip01_R_UpperArm', X, -40], ['Bip01_R_Forearm', X, -95], ['Bip01_R_Forearm', Y, -40], ['Bip01_Head', Z, -6]];
    await crowd(10, 6, { cz: -9, seed: 8 });
    cam = path([[0, [0.25, 1.6, 2.0, 0.08, 1.6, -0.4]], [1, [0.12, 1.6, 1.7, 0.08, 1.6, -0.4]]]); camera.fov = 40; dof = { focus: 1.8, aperture: 0.015 };
  } else if (shot === 'stage') {
    const st = stage(THREE); st.position.set(0, 0, -8.5); world.add(st);
    const f = await person(5, { x: -1.2, z: -8.6, ry: 0.1, face: true, dance: false, shadow: true, tint: 0x2a7a78, tint2: 0x3a2a1a, hat: 'feather', hatColor: 0xb8262a, seed: 80 });
    const d = await person(3, { x: 1.3, z: -8.7, ry: -0.15, face: true, dance: false, shadow: true, tint: 0xc9902a, tint2: 0x4a2a1a, hat: 'cap', hatColor: 0x2f5fa8, seed: 81 });
    for (const q of [f, d]) { q.h.root.position.y = 0.9; }
    f.music = 'fiddle'; d.music = 'drum'; f.fx = { MouthSmileLeft: 0.7, MouthSmileRight: 0.7, AU_LipCornerPuller: 0.6, EyeSquintLeft: 0.3, EyeSquintRight: 0.3 }; d.fx = { BrowInnerUp: 0.5, MouthSmileLeft: 0.4, MouthSmileRight: 0.4 };
    instruments(THREE, f, d);
    await crowd(26, 6.5, { cz: -1, seed: 9, shadowN: 6 });
    cam = path([[0, [-3.5, 2.4, 8.5, 0, 1.6, -6]], [1, [-1.8, 2.2, 6.8, 0, 1.7, -7]]]); camera.fov = 46;
  } else if (shot === 'worse') {
    await crowd(64, 10, { seed: 10, faceNear: [0, 0, 2.2], shadowN: 10 });
    cam = (u) => { const a = 0.6 - u * 0.7; return [Math.sin(a) * 6.5, 2.6, Math.cos(a) * 6.5, 0, 1.4, 0]; }; camera.fov = 48;
  } else if (shot === 'aerial') {
    await crowd(160, 11.5, { seed: 12, gap: 0.8 });
    const st = stage(THREE); st.position.set(0, 0, -13.5); world.add(st);
    cam = (u) => { const a = 0.3 + u * 0.35; return [Math.sin(a) * 0.01, 23 - u * 3, Math.cos(a) * 0.01 + 0.5, 0, 0, 0]; };
    camera.fov = 52; extra = (u) => { camera.up.set(Math.sin(0.3 + u * 0.35), 0, -Math.cos(0.3 + u * 0.35)); };
  } else if (shot === 'square_wide') {
    await crowd(120, 14, { seed: 13, shadowN: 0 });
    const st = stage(THREE); st.position.set(0, 0, -15.5); world.add(st);
    cam = path([[0, [9, 12, 14, 0, 1, -5]], [1, [7.5, 10.5, 12, 0, 1, -6]]]); camera.fov = 48;
  } else if (shot === 'fallen') {
    const m = await person(3, { x: 0, z: 0, ry: 0, face: true, shadow: true, hero: true, dance: false, tint: 0xb8642a, tint2: 0x4a3a2a, seed: 90, hat: 'none' });
    m.lying = true; m.fx = { EyeBlinkLeft: 0.75, EyeBlinkRight: 0.75, BrowInnerUp: 0.7, JawOpen: 0.25, MouthFrownLeft: 0.3, MouthFrownRight: 0.3 };
    await crowd(18, 5.5, { r0: 1.5, seed: 14, shadowN: 6 });
    cam = path([[0, [-0.75, 0.6, -1.75, 0, 0.18, -0.75]], [1, [-0.55, 0.5, -1.45, 0, 0.18, -0.75]]]); camera.fov = 44; dof = { focus: 1.0, aperture: 0.02 };
  } else if (shot === 'historian') {
    world.visible = false; sun.visible = false; hemi.intensity = 0.25; scene.background = new THREE.Color(0x1a120c); scene.fog = null;
    desk(THREE, scene);
    cam = path([[0, [0.0, 1.45, 0.75, 0, 0.82, 0]], [1, [0.0, 1.3, 0.55, 0, 0.82, -0.02]]]); camera.fov = 40; dof = { focus: 0.75, aperture: 0.02 };
  } else if (shot === 'why_sky') {
    await crowd(16, 6, { cz: -2, seed: 15 });
    cam = path([[0, [-2, 1.4, 12, -12, 40, -95]], [1, [-1.6, 1.4, 10.5, -14, 80, -95]]]); camera.fov = 52;
  } else if (shot === 'lone_end') {
    await troffea({ z: 0, ry: 0.2 });
    cam = path([[0, [0.4, 1.4, 3.2, 0, 1.2, 0]], [1, [1.5, 4.5, 9.5, 0, 0.9, 0]]]); camera.fov = 44;
  }
  camera.updateProjectionMatrix();

  // post: background blur only on close-ups (cost)
  let composer = null;
  if (dof) {
    const { EffectComposer } = await import('three/addons/postprocessing/EffectComposer.js');
    const { RenderPass } = await import('three/addons/postprocessing/RenderPass.js');
    const { BokehPass } = await import('three/addons/postprocessing/BokehPass.js');
    const { OutputPass } = await import('three/addons/postprocessing/OutputPass.js');
    composer = new EffectComposer(renderer); composer.setSize(W, H);
    composer.addPass(new RenderPass(scene, camera));
    composer.addPass(new BokehPass(scene, camera, { focus: dof.focus, aperture: dof.aperture, maxblur: 0.012 }));
    composer.addPass(new OutputPass());
  }
  return { scene, camera, cam, P, LEN, extra, composer };
}

export function update(ctx, t) {
  const { camera, cam, P, LEN } = ctx; const u = clamp(t / LEN);
  const c = cam(u); camera.position.set(c[0], c[1], c[2]); ctx.extra(u); camera.lookAt(c[3], c[4], c[5]);
  for (const p of P) {
    const h = p.h; let list = [], bob = 0;
    h.root.position.set(p.x, h.root.position.y > 0.5 ? h.root.position.y : 0, p.z);
    if (p.dance) { [list, bob] = dance(t, p.seed, p.e); h.root.rotation.y = p.ry + p.spin * t; }
    else if (p.music) list = musician(t, p.music);
    else if (!p.lying) list = [['Bip01_Spine1', X, Math.sin(t * 2 + p.seed) * 1.5], ['Bip01_Head', Y, Math.sin(t * 0.7 + p.seed) * 6]];
    if (p.kneel) {   // drop to the knees, arms hanging, head down
      const k = p.kneel(u); list = list.map(([n, a, d]) => [n, a, d * (1 - k)]);
      list.push(['Bip01_L_Thigh', X, -12 * k], ['Bip01_R_Thigh', X, -8 * k], ['Bip01_L_Calf', X, 92 * k], ['Bip01_R_Calf', X, 92 * k],
        ['Bip01_Spine1', X, 24 * k], ['Bip01_Head', X, 26 * k], ['Bip01_L_UpperArm', Z, -12 * k], ['Bip01_R_UpperArm', Z, 12 * k], ['Bip01_L_UpperArm', X, -15 * k], ['Bip01_R_UpperArm', X, -15 * k]);
      bob = -0.43 * k;
    }
    if (p.lying) {
      h.root.rotation.set(-Math.PI / 2, 0, 0.0); h.root.position.set(p.x, 0.13, p.z + 0.9);
      list = [['Bip01_L_UpperArm', Z, 10], ['Bip01_R_UpperArm', Z, -60], ['Bip01_R_Forearm', X, -30], ['Bip01_Head', Y, -55], ['Bip01_L_Thigh', X, -25], ['Bip01_L_Calf', X, 40], ['Bip01_Head', X, 8]];
    }
    h.pose(POSES.stand, 1, [...list, ...(p.pose || [])]);
    if (!p.lying && h.root.position.y < 0.5) h.root.position.y = bob;
    if (p.face) {
      // dancers pant: the jaw works with the beat
      const pant = p.dance ? 0.12 * (0.5 + 0.5 * Math.sin(t * 7 + p.seed)) : 0;
      h.expr({ ...p.fx, JawOpen: (p.fx.JawOpen || 0) + pant }, 1);
    }
    h.syncAll();
  }
}

// ------------------------------------------------------------------------------------------------ props & costumes
function costume(THREE, h, female, eye, r, o) {
  const cloth = (c, rough = 0.9) => new THREE.MeshStandardMaterial({ color: c, roughness: rough, side: THREE.DoubleSide });
  const cz = eye.z - 0.075;
  if (female) {
    // long skirt from the hips, flared
    const col = o.skirt ?? SKIRT[Math.floor(r() * SKIRT.length)];
    const g = new THREE.CylinderGeometry(0.19, 0.36, 0.86, 40, 4, true); const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), y = p.getY(i), a = Math.atan2(x, z), k = 1 + 0.07 * Math.sin(a * 18) * (0.5 - y); p.setX(i, x * k); p.setZ(i, z * k * 0.92); }
    g.computeVertexNormals();
    if (!costume.folds) costume.folds = ctex(THREE, 256, 64, (c, w, hh) => { c.fillStyle = '#fff'; c.fillRect(0, 0, w, hh); for (let x = 0; x < w; x++) { const v = 190 + 65 * Math.sin(x / w * Math.PI * 18) ** 2; c.fillStyle = `rgb(${v},${v},${v})`; c.fillRect(x, 0, 1, hh); } c.fillStyle = 'rgba(0,0,0,0.25)'; c.fillRect(0, hh - 5, w, 5); });
    const skm = new THREE.MeshStandardMaterial({ color: col, map: costume.folds, roughness: 0.95, side: THREE.DoubleSide });
    const sk = new THREE.Mesh(g, skm); sk.position.set(0, -0.38, 0.0); h.pelvisGroup.add(sk);
    const apron = new THREE.Mesh(new THREE.PlaneGeometry(0.32, 0.6), cloth(0xf2ead8)); apron.position.set(0, -0.32, 0.215); apron.rotation.x = -0.18; if (r() > 0.4) h.pelvisGroup.add(apron);
    // white coif over the hair
    const cg = new THREE.SphereGeometry(0.104, 40, 24, 0, Math.PI * 2, 0, Math.PI * 0.7); const cp = cg.attributes.position;
    for (let i = 0; i < cp.count; i++) { const x = cp.getX(i), y = cp.getY(i), z = cp.getZ(i), a = Math.atan2(x, z); cp.setXYZ(i, x * (1 + 0.04 * Math.sin(a * 7)), y, z * (1 + 0.04 * Math.sin(a * 7))); }
    cg.computeVertexNormals();
    const coif = new THREE.Mesh(cg, cloth(0xf7f3ea, 0.85));
    coif.scale.set(1.06, 1.0, 1.14); coif.position.set(0, eye.y + 0.035, cz - 0.03); coif.rotation.x = -0.45; h.headGroup.add(coif);
    h.mats.hair.visible = false;   // the coif covers the hair

  } else {
    const kind = o.hat ?? ['cap', 'beret', 'none', 'tall', 'cap', 'none'][Math.floor(r() * 6)];
    const hc = o.hatColor ?? WOOL[Math.floor(r() * WOOL.length)];
    if (kind === 'cap' || kind === 'feather') {
      const cap = new THREE.Mesh(new THREE.SphereGeometry(0.112, 28, 14, 0, Math.PI * 2, 0, Math.PI / 2), cloth(hc)); cap.scale.set(1.05, 0.75, 1.16); cap.position.set(0, eye.y + 0.05, cz); h.headGroup.add(cap);
      const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.012, 32), cloth(hc)); brim.scale.z = 1.12; brim.position.set(0, eye.y + 0.05, cz); h.headGroup.add(brim);
      if (kind === 'feather') { const f = new THREE.Mesh(new THREE.ConeGeometry(0.018, 0.26, 10), cloth(0xfff6e0)); f.position.set(0.08, eye.y + 0.15, cz - 0.04); f.rotation.z = -0.6; h.headGroup.add(f); }
    } else if (kind === 'beret') {
      const b = new THREE.Mesh(new THREE.SphereGeometry(0.135, 28, 14), cloth(hc)); b.scale.set(1.0, 0.32, 1.05); b.position.set(0.02, eye.y + 0.1, cz); b.rotation.z = -0.15; h.headGroup.add(b);
    } else if (kind === 'tall') {
      const t = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.112, 0.17, 28), cloth(hc)); t.scale.z = 1.12; t.position.set(0, eye.y + 0.11, cz); h.headGroup.add(t);
      const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.01, 28), cloth(hc)); brim.scale.z = 1.12; brim.position.set(0, eye.y + 0.03, cz); h.headGroup.add(brim);
    }
  }
  h.root.traverse(m => { if (m.isMesh && !m.isSkinnedMesh) { m.castShadow = !!o.shadow; m.receiveShadow = true; } });
}

function blob(THREE) {
  if (!blob.mat) blob.mat = new THREE.MeshBasicMaterial({ map: ctex(THREE, 64, 64, (g, w, h) => { const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(0,0,0,0.45)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); }), transparent: true, depthWrite: false });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.9), blob.mat); m.rotation.x = -Math.PI / 2; return m;
}

function musician(t, kind) {
  const b = Math.sin(t * 9);
  if (kind === 'fiddle') return [['Bip01_L_UpperArm', Z, 20], ['Bip01_L_UpperArm', X, -55], ['Bip01_L_Forearm', X, -100], ['Bip01_L_Forearm', Y, 60],
    ['Bip01_R_UpperArm', Z, -20 + 12 * b], ['Bip01_R_UpperArm', X, -45], ['Bip01_R_Forearm', X, -70 + 20 * b], ['Bip01_Head', Z, -14], ['Bip01_Spine1', Z, 4 * Math.sin(t * 4.5)]];
  const d = Math.abs(Math.sin(t * 6));
  return [['Bip01_L_UpperArm', Z, -10], ['Bip01_R_UpperArm', Z, 10], ['Bip01_L_UpperArm', X, -40], ['Bip01_R_UpperArm', X, -40],
    ['Bip01_L_Forearm', X, -70 - 25 * d], ['Bip01_R_Forearm', X, -70 - 25 * (1 - d)], ['Bip01_L_Forearm', Y, 40], ['Bip01_R_Forearm', Y, -40], ['Bip01_Head', X, 4 * d]];
}

function instruments(THREE, f, d) {
  const wood = new THREE.MeshStandardMaterial({ color: 0x8a4a1c, roughness: 0.45 });
  // fiddle held at the neck of the fiddler (in his head frame, under the chin on his left)
  const fid = new THREE.Group();
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.1, 20, 12), wood); body.scale.set(1, 0.35, 1.7); fid.add(body);
  const neck = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.02, 0.22), new THREE.MeshStandardMaterial({ color: 0x2a1a10 })); neck.position.z = 0.25; fid.add(neck);
  fid.position.set(0.11, -0.04, 0.06); fid.rotation.set(0.2, -0.9, 0.5); f.h.headGroup.add(fid);
  const drum = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.28, 28), new THREE.MeshStandardMaterial({ color: 0xc23a2a, roughness: 0.6 }));
  drum.rotation.x = 0.25; drum.position.set(0, 0.0, 0.34); d.h.pelvisGroup.add(drum);
  const skin = new THREE.Mesh(new THREE.CircleGeometry(0.2, 28), new THREE.MeshStandardMaterial({ color: 0xf2e6c8, roughness: 0.7 })); skin.rotation.x = -Math.PI / 2; skin.position.y = 0.141; drum.add(skin);
}

function stage(THREE) {
  const g = new THREE.Group();
  const plank = ctex(THREE, 512, 512, (c, w, h) => { for (let i = 0; i < 8; i++) { const v = 120 + Math.random() * 40; c.fillStyle = `rgb(${v + 40},${v},${v - 50})`; c.fillRect(0, i * 64, w, 62); c.fillStyle = 'rgba(40,20,5,0.6)'; c.fillRect(0, i * 64 + 62, w, 2); } }, { repeat: [2, 1] });
  const top = new THREE.Mesh(new THREE.BoxGeometry(6, 0.12, 3.2), new THREE.MeshStandardMaterial({ map: plank, roughness: 0.8 })); top.position.y = 0.86; top.castShadow = top.receiveShadow = true; g.add(top);
  const post = new THREE.MeshStandardMaterial({ color: 0x6a4020, roughness: 0.8 });
  for (const x of [-2.8, 0, 2.8]) for (const z of [-1.4, 1.4]) { const p = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.86, 0.16), post); p.position.set(x, 0.43, z); g.add(p); }
  // striped bunting above the stage
  const cols = [0xd8342a, 0xf2c230, 0x2f6fd0, 0x2f9a4a];
  for (let i = 0; i < 14; i++) { const f = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.34, 3), new THREE.MeshStandardMaterial({ color: cols[i % 4], side: THREE.DoubleSide })); f.rotation.x = Math.PI; f.position.set(-3 + i * 0.46, 3.0 - 0.25 * Math.sin(i / 13 * Math.PI), -1.5); g.add(f); }
  for (const x of [-3.1, 3.1]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 3.3, 8), post); p.position.set(x, 1.65, -1.5); g.add(p); }
  return g;
}

function blood(THREE, world) {
  const tex = ctex(THREE, 256, 256, (g, w, h) => { for (let i = 0; i < 9; i++) { g.fillStyle = `rgba(${90 + Math.random() * 40},8,10,${0.5 + Math.random() * 0.3})`; g.beginPath(); g.ellipse(70 + Math.random() * 120, 70 + Math.random() * 120, 4 + Math.random() * 14, 2 + Math.random() * 6, Math.random() * 3, 0, 7); g.fill(); } });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.4), new THREE.MeshStandardMaterial({ map: tex, transparent: true, roughness: 0.25, depthWrite: false }));
  m.rotation.x = -Math.PI / 2; m.position.set(0, 0.006, 0.1); world.add(m);
}

function desk(THREE, scene) {
  const g = new THREE.Group(); scene.add(g);
  const wood = new THREE.MeshStandardMaterial({ color: 0x5a3216, roughness: 0.6 });
  const top = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.06, 1.0), wood); top.position.y = 0.75; top.receiveShadow = true; g.add(top);
  const page = ctex(THREE, 1024, 768, (c, w, h) => {
    c.fillStyle = '#efe0bc'; c.fillRect(0, 0, w, h); const gr = c.createRadialGradient(w / 2, h / 2, h * 0.2, w / 2, h / 2, w * 0.7); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(90,50,10,0.35)'); c.fillStyle = gr; c.fillRect(0, 0, w, h);
    c.fillStyle = 'rgba(40,25,15,0.85)'; c.font = 'bold 64px serif'; c.fillText('Anno 1518', 70, 110); c.fillStyle = '#9a1a12'; c.fillRect(70, 130, 60, 60);
    c.fillStyle = 'rgba(40,25,15,0.75)';
    for (let side = 0; side < 2; side++) for (let l = 0; l < 14; l++) { let x = 70 + side * 500; const y = 230 + l * 36; while (x < 440 + side * 500) { const ww = 12 + Math.random() * 46; c.fillRect(x, y, ww, 9); x += ww + 9; } }
    c.fillStyle = 'rgba(60,30,10,0.25)'; c.fillRect(w / 2 - 3, 0, 6, h);
  });
  const book = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.05, 0.46), [wood, wood, new THREE.MeshStandardMaterial({ map: page, roughness: 0.9 }), wood, wood, wood]);
  book.position.set(0, 0.8, 0); book.rotation.y = 0.05; book.receiveShadow = true; g.add(book);
  const candle = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.2, 16), new THREE.MeshStandardMaterial({ color: 0xf2e6c8 })); candle.position.set(0.42, 0.88, -0.18); g.add(candle);
  const flame = glow(THREE, 0xffb050, 0.18, 1); flame.position.set(0.42, 1.0, -0.18); g.add(flame);
  const L = new THREE.PointLight(0xffb060, 6, 4, 2); L.position.set(0.42, 1.05, -0.12); L.castShadow = true; g.add(L);
  const k = new THREE.SpotLight(0xffd8a0, 8, 5, 0.6, 0.8, 2); k.position.set(-0.6, 1.9, 0.6); k.target.position.set(0, 0.8, 0); g.add(k, k.target);
  const quill = new THREE.Mesh(new THREE.ConeGeometry(0.012, 0.32, 8), new THREE.MeshStandardMaterial({ color: 0xfaf4e6 })); quill.rotation.set(0, 0, 1.2); quill.position.set(0.3, 0.84, 0.16); g.add(quill);
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(6, 4), new THREE.MeshStandardMaterial({ color: 0x4a3020, roughness: 1 })); wall.position.set(0, 1.5, -1.2); g.add(wall);
}

// ------------------------------------------------------------------------------------------------ town
function buildTown(THREE, world, golden) {
  const cob = ctex(THREE, 1024, 1024, (g, w, h) => {
    g.fillStyle = '#5a5048'; g.fillRect(0, 0, w, h); const n = 24, s = w / n;
    for (let r = 0; r < n; r++) for (let c = -1; c < n; c++) {
      const x = c * s + (r % 2) * s / 2, y = r * s, v = 112 + Math.random() * 40, wob = () => (Math.random() - 0.5) * 5, tt = Math.random() * 16;
      g.fillStyle = `rgb(${v + 14 + tt},${v + 4},${v - 8 - tt / 2})`; g.beginPath();
      g.roundRect(x + 2 + wob(), y + 2 + wob(), s - 4 + wob(), s - 4 + wob(), 6); g.fill();
      g.fillStyle = 'rgba(255,250,235,0.07)'; g.fillRect(x + 8, y + 8, s * 0.5, s * 0.25);
    }
  }, { repeat: [90, 90] });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(260, 260), new THREE.MeshStandardMaterial({ map: cob, roughness: 0.8 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; world.add(floor);

  const PLASTER = ['#f4e8c8', '#f2c9b8', '#cfe3d0', '#f3dc8a', '#c9d9ee', '#f7efe2', '#e9b9a0', '#d8e7b0'];
  const facade = (seed, floors) => ctex(THREE, 512, 512 * floors / 3, (g, w, h) => {
    const r = rng(seed); g.fillStyle = PLASTER[seed % PLASTER.length]; g.fillRect(0, 0, w, h);
    const fh = h / floors, beam = '#4a2a16';
    g.fillStyle = '#9a8a78'; g.fillRect(0, h - fh, w, fh);                         // stone ground floor
    for (let i = 0; i < 400; i++) { g.fillStyle = `rgba(0,0,0,${r() * 0.05})`; g.fillRect(r() * w, r() * (h - fh), 6, 6); }
    g.fillStyle = beam;
    for (let f = 0; f < floors - 1; f++) {
      const y0 = f * fh; g.fillRect(0, y0, w, 12); g.fillRect(0, y0 + fh - 12, w, 12);
      for (let k = 0; k <= 4; k++) g.fillRect(k * (w - 14) / 4, y0, 14, fh);
      g.lineWidth = 11; g.strokeStyle = beam;
      for (let k = 0; k < 4; k++) { if ((k + f + seed) % 2) continue; const x0 = k * (w - 14) / 4 + 7, x1 = (k + 1) * (w - 14) / 4 + 7; g.beginPath(); g.moveTo(x0, y0 + fh * 0.55); g.lineTo(x1, y0 + 12); g.moveTo(x1, y0 + fh * 0.55); g.lineTo(x0, y0 + 12); g.stroke(); }
      for (let k = 0; k < 4; k++) if ((k + f) % 2 === 0 || r() > 0.5) {   // windows with small panes
        const x = k * (w - 14) / 4 + 30, ww = (w - 14) / 4 - 46, y = y0 + fh * 0.2, hh = fh * 0.5;
        g.fillStyle = beam; g.fillRect(x - 6, y - 6, ww + 12, hh + 12); g.fillStyle = '#7fb0d8'; g.fillRect(x, y, ww, hh);
        g.fillStyle = 'rgba(255,255,255,0.35)'; g.fillRect(x + 4, y + 4, ww * 0.35, hh * 0.3);
        g.fillStyle = beam; g.fillRect(x + ww / 2 - 2, y, 4, hh); g.fillRect(x, y + hh / 2 - 2, ww, 4);
        if (r() > 0.6) { g.fillStyle = ['#c0392b', '#2e7d4f', '#2f5fa8'][Math.floor(r() * 3)]; g.fillRect(x - 26, y - 6, 18, hh + 12); g.fillRect(x + ww + 8, y - 6, 18, hh + 12); }
        g.fillStyle = beam;
      }
    }
    const y0 = h - fh; g.fillStyle = '#3a2412'; g.fillRect(w * 0.38, y0 + fh * 0.2, w * 0.24, fh * 0.8);   // door
    g.fillStyle = '#5a3a1e'; g.fillRect(w * 0.08, y0 + fh * 0.3, w * 0.2, fh * 0.35); g.fillRect(w * 0.72, y0 + fh * 0.3, w * 0.2, fh * 0.35);
  });
  const roofTex = ctex(THREE, 256, 256, (g, w, h) => { g.fillStyle = '#b4482c'; g.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 16) for (let x = (y / 16 % 2) * 8; x < w; x += 16) { const v = Math.random() * 30; g.fillStyle = `rgb(${160 + v},${60 + v / 2},${40})`; g.fillRect(x, y, 15, 14); } }, { repeat: [3, 3] });
  const roofM = new THREE.MeshStandardMaterial({ map: roofTex, roughness: 0.8 });
  let seed = 1;
  const house = (x, z, ry, w = 6) => {
    const floors = 3 + (seed % 2), fh = 3.0, hgt = floors * fh, d = 8;
    const fm = new THREE.MeshStandardMaterial({ map: facade(seed++, floors), roughness: 0.92 });
    const side = new THREE.MeshStandardMaterial({ color: 0xe8dcc0, roughness: 0.95 });
    const b = new THREE.Mesh(new THREE.BoxGeometry(w, hgt, d), [side, side, side, side, fm, side]);
    b.position.set(0, hgt / 2, -d / 2); b.castShadow = b.receiveShadow = true;
    const roofH = w * 0.9;
    const rg = new THREE.BufferGeometry(); const hw = w / 2 + 0.25, hd = d / 2 + 0.3;
    const v = [-hw, 0, hd, hw, 0, hd, 0, roofH, hd, -hw, 0, -hd, hw, 0, -hd, 0, roofH, -hd];
    rg.setAttribute('position', new THREE.Float32BufferAttribute(v, 3));
    rg.setAttribute('uv', new THREE.Float32BufferAttribute([0, 0, 1, 0, 0.5, 1, 0, 0, 1, 0, 0.5, 1], 2));
    rg.setIndex([0, 1, 2, 4, 3, 5, 0, 2, 5, 0, 5, 3, 1, 4, 5, 1, 5, 2]); rg.computeVertexNormals();
    const roof = new THREE.Mesh(rg, roofM); roof.position.set(0, hgt, -d / 2); roof.castShadow = true;
    const gable = new THREE.Mesh(new THREE.ShapeGeometry(new THREE.Shape([new THREE.Vector2(-w / 2, 0), new THREE.Vector2(w / 2, 0), new THREE.Vector2(0, roofH * 0.97)])), new THREE.MeshStandardMaterial({ color: PLASTER[(seed + 3) % PLASTER.length], roughness: 0.9 }));
    gable.position.set(0, hgt, 0.01);
    const grp = new THREE.Group(); grp.add(b, roof, gable); grp.position.set(x, 0, z); grp.rotation.y = ry; world.add(grp);
  };
  const S = 17;  // half size of the square
  for (let i = -2; i <= 2; i++) { house(i * 6.4, -S, 0); house(i * 6.4, S, Math.PI); house(-S, i * 6.4, Math.PI / 2); house(S, i * 6.4, -Math.PI / 2); }
  // street gap to the north is implied; the cathedral rises behind the north row
  // Strasbourg cathedral: pink sandstone west front with three portals, a rose window and lancet galleries,
  // the single north tower with its octagon and openwork spire
  const facadeT = ctex(THREE, 1024, 1536, (g, w, h) => {
    g.fillStyle = '#d88f7c'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 6000; i++) { g.fillStyle = `rgba(${110 + Math.random() * 60},40,40,0.07)`; g.fillRect(Math.random() * w, Math.random() * h, 5, 5); }
    const dark = 'rgba(80,25,30,0.55)', mid = 'rgba(120,40,40,0.35)';
    g.fillStyle = mid; for (const x of [0, 0.25, 0.75, 1]) g.fillRect(x * w - 18, 0, 36, h);            // buttresses
    const arch = (x, y, ww, hh) => { g.beginPath(); g.moveTo(x, y + hh); g.lineTo(x, y + ww * 0.6); g.quadraticCurveTo(x, y, x + ww / 2, y - ww * 0.25); g.quadraticCurveTo(x + ww, y, x + ww, y + ww * 0.6); g.lineTo(x + ww, y + hh); g.fill(); };
    g.fillStyle = dark; arch(w * 0.38, h * 0.72, w * 0.24, h * 0.28); arch(w * 0.07, h * 0.78, w * 0.14, h * 0.22); arch(w * 0.79, h * 0.78, w * 0.14, h * 0.22);
    g.fillStyle = 'rgba(90,30,60,0.8)'; g.beginPath(); g.arc(w / 2, h * 0.45, w * 0.16, 0, 7); g.fill();
    g.strokeStyle = 'rgba(240,200,180,0.5)'; g.lineWidth = 6; for (let k = 0; k < 16; k++) { const a = k / 16 * Math.PI * 2; g.beginPath(); g.moveTo(w / 2, h * 0.45); g.lineTo(w / 2 + Math.cos(a) * w * 0.16, h * 0.45 + Math.sin(a) * w * 0.16); g.stroke(); }
    g.fillStyle = dark; for (let k = 0; k < 7; k++) arch(w * 0.06 + k * w * 0.13, h * 0.12, w * 0.07, h * 0.16);       // lancet gallery
    for (const x of [0.06, 0.82]) for (let k = 0; k < 2; k++) arch(w * (x + k * 0.07), h * 0.38, w * 0.05, h * 0.2);
  });
  const sm = new THREE.MeshStandardMaterial({ color: 0xd88f7c, roughness: 0.9 });
  const fm = new THREE.MeshStandardMaterial({ map: facadeT, roughness: 0.9 });
  const cath = new THREE.Group(); cath.position.set(-6, 0, -95); world.add(cath);
  const block = new THREE.Mesh(new THREE.BoxGeometry(36, 66, 12), [sm, sm, sm, sm, fm, sm]); block.position.y = 33; cath.add(block);
  const nave = new THREE.Mesh(new THREE.BoxGeometry(26, 34, 70), sm); nave.position.set(0, 17, -40); cath.add(nave);
  const roof = new THREE.Mesh(new THREE.CylinderGeometry(0.01, 15, 14, 4, 1), new THREE.MeshStandardMaterial({ color: 0x6a7a8a, roughness: 0.7 })); roof.rotation.set(Math.PI / 2, Math.PI / 4, 0); roof.scale.set(1, 4.8, 0.6); roof.position.set(0, 40, -40); cath.add(roof);
  const octT = ctex(THREE, 512, 512, (g, w, h) => { g.fillStyle = '#d88f7c'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(80,25,30,0.6)'; for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(20 + k * 125, 470); g.lineTo(20 + k * 125, 140); g.quadraticCurveTo(70 + k * 125, 30, 120 + k * 125, 140); g.lineTo(120 + k * 125, 470); g.fill(); } }, { repeat: [2, 1] });
  const oct = new THREE.Mesh(new THREE.CylinderGeometry(6.2, 6.8, 30, 8), new THREE.MeshStandardMaterial({ map: octT, roughness: 0.9 })); oct.position.set(-11, 66 + 15, 0); cath.add(oct);
  const spT = ctex(THREE, 256, 1024, (g, w, h) => { g.fillStyle = '#d88f7c'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(60,20,25,0.55)'; for (let y = 30; y < h; y += 60) { g.fillRect(0, y, w, 10); for (let x = 10; x < w; x += 40) g.fillRect(x, y + 18, 16, 26); } });
  const spire = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 6.2, 52, 8, 1, false), new THREE.MeshStandardMaterial({ map: spT, roughness: 0.9 })); spire.position.set(-11, 66 + 30 + 26, 0); cath.add(spire);
  for (const dx of [-1, 1]) for (const dz of [-1, 1]) { const t = new THREE.Mesh(new THREE.ConeGeometry(1.4, 10, 6), sm); t.position.set(-11 + dx * 5.2, 66 + 30 + 4, dz * 5.2); cath.add(t); }
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.5, 5, 8), sm); tip.position.set(-11, 66 + 30 + 54, 0); cath.add(tip);
  const plat = new THREE.Mesh(new THREE.BoxGeometry(14, 2, 14), sm); plat.position.set(-11, 66, 0); cath.add(plat);
  cath.traverse(m => { if (m.isMesh) m.castShadow = false; });
}

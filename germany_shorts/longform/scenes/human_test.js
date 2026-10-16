// Character test for the STRATA 3D shorts: one realistic Rocketbox human (lib_human.js) in a simple
// historical setting, an old European street at dusk: cobbles, plastered facades with warm lit windows, gas lamps.
// shots (?shot=):  debug | medium | face   (append "_sphere" for the minimalist sphere-head fallback)
//   medium (4 s) waist-up, slow push-in; neutral -> shock at 0.8-1.6 s, hands come up.
//   face   (4 s) face close-up, slow drift; neutral -> shock at 0.6-1.4 s.
//   suffix "_fast": no depth of field (about 2x faster on the CPU renderer).
//   debug|<json pose list>  full body, for tuning poses.
// Speed (4-core CPU, SwiftShader): 1080x1920 with DOF about 3.0 s/frame; 1080x1920 _fast about 2.1 s/frame;
// 720x1280 with DOF about 1.5 s/frame; 720x1280 _fast about 1.0 s/frame.
import { loadHuman, EXPR, POSES } from './lib_human.js';
import { path, sstep, ctex, shotArgs, finishPost } from './france_lib.js';
import { glow } from './look.js';

export async function setup(THREE, renderer, W, H) {
  const { name: raw } = shotArgs('medium');
  const fast = raw.includes('_fast'); const sphereHead = raw.includes('_sphere'); let shot = raw.replace('_sphere', '').replace('_fast', '');
  let dbgPose = null; if (shot.startsWith('debug|')) { dbgPose = JSON.parse(shot.slice(6)); shot = 'debug'; }
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  const SKY = 0x24304a;
  scene.background = new THREE.Color(SKY);
  scene.fog = new THREE.Fog(SKY, 10, 45);

  // ---- street: cobbles ----
  const cob = ctex(THREE, 1024, 1024, (g, w, h) => {
    g.fillStyle = '#2c2925'; g.fillRect(0, 0, w, h);
    const n = 16, s = w / n;
    for (let r = 0; r < n; r++) for (let c = -1; c < n; c++) {
      const x = c * s + (r % 2) * s / 2, y = r * s, v = 62 + Math.random() * 40;
      g.fillStyle = `rgb(${v + 6},${v},${v - 8})`;
      g.beginPath(); g.ellipse(x + s / 2, y + s / 2, s * 0.45, s * 0.41, Math.random() * 0.4, 0, 7); g.fill();
      g.fillStyle = 'rgba(255,240,220,0.07)'; g.beginPath(); g.ellipse(x + s * 0.44, y + s * 0.4, s * 0.26, s * 0.18, 0, 0, 7); g.fill();
    }
  }, { repeat: [40, 40] });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.MeshStandardMaterial({ map: cob, roughness: 0.42, metalness: 0.1 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);

  // ---- facades: colour texture + matching emissive map for the lit windows ----
  const winLit = (seed, fl, k) => ((seed * 7 + fl * 3 + k * 5) % 7) < 3;
  const facadeTex = (base, seed, emissive) => ctex(THREE, 512, 1024, (g, cw, ch) => {
    g.fillStyle = emissive ? '#000' : base; g.fillRect(0, 0, cw, ch);
    if (!emissive) {
      for (let i = 0; i < 5000; i++) { g.fillStyle = `rgba(0,0,0,${Math.random() * 0.06})`; g.fillRect(Math.random() * cw, Math.random() * ch, 3, 3); }
      g.fillStyle = 'rgba(0,0,0,0.3)'; g.fillRect(0, ch * 0.8, cw, ch * 0.2);          // darker ground floor
      g.fillStyle = 'rgba(255,255,255,0.08)'; for (let fl = 1; fl < 5; fl++) g.fillRect(0, fl * 205 - 20, cw, 8);  // cornices
    }
    for (let fl = 0; fl < 4; fl++) for (let k = 0; k < 3; k++) {
      const x = 52 + k * 160, y = 60 + fl * 205, lit = winLit(seed, fl, k);
      if (!emissive) { g.fillStyle = 'rgba(0,0,0,0.4)'; g.fillRect(x - 9, y - 9, 108, 158); }
      if (emissive && !lit) continue;
      const grd = g.createLinearGradient(0, y, 0, y + 140);
      grd.addColorStop(0, lit ? '#ffcf86' : '#151b26'); grd.addColorStop(1, lit ? '#e8913e' : '#0d1119');
      g.fillStyle = grd; g.fillRect(x, y, 90, 140);
      g.fillStyle = emissive ? '#000' : 'rgba(40,28,20,0.95)'; g.fillRect(x + 42, y, 6, 140); g.fillRect(x, y + 62, 90, 6);
    }
    // ground-floor shop door
    if (!emissive) { g.fillStyle = '#1a1512'; g.fillRect(190, 860, 130, 164); }
  });
  const cols = ['#8a7a66', '#9b8770', '#76695e', '#a39079', '#7f7468', '#8e8070'];
  const house = (x, z, ry, i, w = 5.2) => {
    const hgt = 14 + (i % 3) * 1.6;
    const mat = new THREE.MeshStandardMaterial({ map: facadeTex(cols[i % 6], i, false), roughness: 0.92,
      emissive: 0xffffff, emissiveMap: facadeTex(null, i, true), emissiveIntensity: 1.5 });
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, hgt, 4), [0, 0, 0, 0, mat, 0].map(v => v === 0 ? new THREE.MeshStandardMaterial({ color: cols[i % 6], roughness: 0.95 }) : v));
    m.position.set(x, hgt / 2, z); m.rotation.y = ry; m.receiveShadow = true; scene.add(m);
  };
  // the street runs away from camera along -z; houses line both sides, a row closes it at the far end
  for (let i = 0; i < 8; i++) { house(-7.5, 4 - i * 5.3, Math.PI / 2, i); house(7.5, 4 - i * 5.3, -Math.PI / 2, i + 3); }
  for (let i = 0; i < 4; i++) house(-7.8 + i * 5.2, -40, 0, i + 5);

  // gas lamps along both kerbs
  const ironM = new THREE.MeshStandardMaterial({ color: 0x1b1d1d, metalness: 0.6, roughness: 0.45 });
  for (let i = 0; i < 5; i++) for (const sx of [-1, 1]) {
    const x = sx * 4.6, z = -3 - i * 8 - (sx > 0 ? 4 : 0);
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.1, 4, 10), ironM); pole.position.set(x, 2, z); scene.add(pole);
    const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.18, 14, 10), new THREE.MeshBasicMaterial({ color: 0xffe1b0, fog: false })); lamp.position.set(x, 4.1, z); scene.add(lamp);
    const g = glow(THREE, 0xffb468, 2.4, 0.9); g.position.copy(lamp.position); scene.add(g);
    if (i < 2) { const L = new THREE.PointLight(0xffa860, 30, 14, 2); L.position.set(x, 4.0, z); scene.add(L); }
  }

  // ---- lights ----
  scene.add(new THREE.HemisphereLight(0x8ea6d0, 0x3a2e24, 0.8));
  const key = new THREE.SpotLight(0xffe0bc, 150, 20, 0.5, 0.7, 2);
  key.position.set(2.6, 3.4, 3.6); key.target.position.set(0, 1.45, 0);
  key.castShadow = true; key.shadow.mapSize.set(1024, 1024); key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02;
  scene.add(key, key.target);
  const rim = new THREE.SpotLight(0x9cc0ff, 90, 14, 0.4, 0.5, 2); rim.position.set(-1.6, 2.7, -3.8); rim.target.position.set(0, 1.5, 0);
  scene.add(rim, rim.target);
  const fill = new THREE.PointLight(0xffd8c0, 2.5, 6, 2); fill.position.set(-1.4, 1.6, 1.8); scene.add(fill);

  // ---- the man ----
  const h = await loadHuman(THREE, { avatar: 'Male_Adult_03', tex: 'm004' });
  h.root.rotation.y = -0.22; scene.add(h.root);
  if (sphereHead) h.setSphereHead(true);

  const camera = new THREE.PerspectiveCamera(32, W / H, 0.05, 200);
  const cams = {
    debug: path([[0, [0, 1.0, 5.2, 0, 0.95, 0]], [4, [0, 1.0, 5.2, 0, 0.95, 0]]]),
    medium: path([[0, [0.55, 1.42, 3.0, -0.05, 1.32, 0]], [4, [0.38, 1.45, 2.45, -0.04, 1.38, 0]]]),
    face: path([[0, [0.2, 1.66, 1.02, -0.02, 1.62, 0]], [4, [0.12, 1.665, 0.84, -0.02, 1.625, 0]]]),
  };
  if (shot === 'debug') camera.fov = 34;
  camera.updateProjectionMatrix();
  const focus = { debug: 5.2, medium: 2.6, face: 0.9 }[shot] || 2.6;
  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.55, bloomRadius: 0.5, bloomThreshold: 0.75, exposure: 1.05, vignette: 0.45,
    dof: (shot === 'debug' || fast) ? null : { focus, aperture: shot === "face" ? 0.03 : 0.012, maxblur: 0.014 } });
  return { scene, camera, h, cam: cams[shot] || cams.medium, shot, dbgPose, composer: post.composer, finish: post.finish, sync: post.sync };
}

export function update(ctx, t) {
  const { h, camera, shot } = ctx;
  const p = ctx.cam(t); camera.position.set(p[0], p[1], p[2]); camera.lookAt(p[3], p[4], p[5]);
  ctx.sync && ctx.sync();
  if (ctx.dbgPose) { h.pose(ctx.dbgPose, 1); h.update(t); return; }
  const a = shot === 'face' ? sstep(0.6, 1.4, t) : sstep(0.8, 1.6, t);
  // stand -> shock: both poses are world-space deltas, so a weighted sum of the two lists blends between them
  if (shot === 'debug') h.pose(POSES.stand, 1);
  else h.pose([...POSES.stand.map(([n, x, d]) => [n, x, d * (1 - a)]), ...POSES.shock.map(([n, x, d]) => [n, x, d * a])], 1);
  h.expr(EXPR.shock, a);
  h.update(t, { blinkAt: [0.4, 3.3] });
}

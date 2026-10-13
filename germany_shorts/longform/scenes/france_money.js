// France 2026: money, as physical objects in a dark studio.
// shots (?shot=name or name:seconds):
//   repair_need (8 s)  25 coin stacks, one per year 2026 -> 2050, rise one after another as the camera dollies
//                      along the row (Senate: about €1.5 bn a year, about €40 bn by 2050).
//   damage_bill (7 s)  bundles of banknotes (no real design: cream paper, amber band) drop into a pile on a pallet;
//                      label "≥ €30 MILLION · government estimate".
//   fine        (7 s)  ten faceless pupils in a row; a €10,000 tag drops on a string in front of each in turn,
//                      though only one figure stands by a broken window pane (the "rioters pay" bill).
const AMBER = 0x34d399;   // v2: subject colour instead of the channel amber
import { glow } from './look.js';
import { path, clamp01, sstep, fontsReady, finishPost, ctex, spacedText, timing, label, ease, studioFloor, figure } from './france_lib.js';
const AMBER_HI = 0x6ee7b7;
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export async function setup(THREE, renderer, W, H) {
  const { name, k: k0 } = timing(8);
  const shot = name || 'repair_need';
  const k = shot === 'repair_need' ? k0 : k0 * 8 / 7;
  await fontsReady();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060607);
  scene.fog = new THREE.FogExp2(0x060607, 0.045);
  const camera = new THREE.PerspectiveCamera(32, W / H, 0.02, 200);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.6, metalness: 0.1, ...o });
  let seed = 21; const R = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  const ctx = { THREE, scene, camera, shot, k };
  scene.add(studioFloor(THREE, { size: 80, tone: 20, pool: 0.1 }));
  scene.add(new THREE.HemisphereLight(0x8e94a0, 0x080706, 0.35));
  const key = new THREE.SpotLight(0xf1f4fa, 80, 30, 0.55, 0.7, 1.3); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0003; scene.add(key, key.target);
  const rim = new THREE.SpotLight(AMBER, 40, 20, 0.6, 0.6, 1.4); scene.add(rim, rim.target);
  const fill = new THREE.DirectionalLight(0xdfe4ea, 0.45); fill.position.set(4, 3, 8); scene.add(fill);

  if (shot === 'repair_need') {
    const N = 25, PER = 15, dx = 0.62;
    const coin = new THREE.CylinderGeometry(0.22, 0.22, 0.045, 40);
    const coinM = std({ color: 0xc9a25a, roughness: 0.3, metalness: 0.85 });
    const inst = new THREE.InstancedMesh(coin, coinM, N * PER); inst.castShadow = inst.receiveShadow = true; scene.add(inst); ctx.inst = inst;
    ctx.coins = []; for (let i = 0; i < N; i++) for (let j = 0; j < PER; j++) ctx.coins.push({ i, j, x: (i - 12) * dx, y: 0.0225 + j * 0.047, rx: (R() - 0.5) * 0.04, ox: (R() - 0.5) * 0.02, oz: (R() - 0.5) * 0.02 });
    for (let i = 0; i < N; i += 4) { const yr = 2026 + i; const t = ctex(THREE, 256, 64, (g, w, h) => { g.fillStyle = '#a49b8b'; g.font = '600 40px Inter, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(String(yr), w / 2, h / 2); });
      const m = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.15), new THREE.MeshBasicMaterial({ map: t, transparent: true })); m.rotation.x = -Math.PI / 2; m.position.set((i - 12) * dx, 0.005, 0.45); scene.add(m); }
    { const t = ctex(THREE, 256, 64, (g, w, h) => { g.fillStyle = '#a49b8b'; g.font = '600 40px Inter, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('2050', w / 2, h / 2); });
      const m = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.15), new THREE.MeshBasicMaterial({ map: t, transparent: true })); m.rotation.x = -Math.PI / 2; m.position.set(12 * dx, 0.005, 0.45); scene.add(m); }
    const l1 = label(THREE, '€1.5 BN', { size: 0.045, sub: 'needed every year', anchor: 'left' }); l1.position.set(-12 * dx + 0.3, 0.95, 0); l1.material.opacity = 0; scene.add(l1);
    const l2 = label(THREE, '≈ €40 BN', { size: 0.06, sub: 'by 2050 · Senate estimate', anchor: 'right', color: '#34d399', subColor: '#e3e8ef' }); l2.position.set(12 * dx - 0.3, 1.2, 0); l2.material.opacity = 0; scene.add(l2);
    ctx.labs = [l1, l2]; ctx.dx = dx;
    key.position.set(0, 7, 5); key.target.position.set(0, 0.3, 0); rim.position.set(-3, 2, -5); rim.target.position.set(0, 0.3, 0); rim.intensity = 12;
  } else if (shot === 'damage_bill') {
    const pallet = new THREE.Group(); scene.add(pallet);
    const wood = std({ color: 0x8a7050, roughness: 0.9 });
    for (let i = 0; i < 7; i++) { const m = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.03, 0.2), wood); m.position.set(0, 0.14, -0.9 + i * 0.3); m.castShadow = m.receiveShadow = true; pallet.add(m); }
    for (const x of [-1.1, 0, 1.1]) { const m = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.12, 2.0), wood); m.position.set(x, 0.06, 0); m.castShadow = true; pallet.add(m); }
    const noteT = ctex(THREE, 512, 256, (g, w, h) => { g.fillStyle = '#d9dcd0'; g.fillRect(0, 0, w, h); for (let y = 6; y < h; y += 7) { g.fillStyle = `rgba(120,110,90,${0.25 + 0.2 * Math.sin(y)})`; g.fillRect(0, y, w, 2); }
      g.fillStyle = '#34d399'; g.fillRect(w * 0.42, 0, w * 0.16, h); g.fillStyle = '#2a2420'; g.font = '700 46px Inter, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.save(); g.translate(w / 2, h / 2); g.rotate(-Math.PI / 2); g.fillText('€', 0, 0); g.restore(); });
    const brickGeo = new RoundedBoxGeometry(0.5, 0.12, 0.24, 2, 0.01);
    const bm = std({ map: noteT, roughness: 0.85, color: 0x9a9384 });
    const side = std({ color: 0x8f887a, roughness: 0.9 });
    ctx.bricks = [];
    const nx = 4, nz = 7, ny = 7;
    for (let y = 0; y < ny; y++) for (let z = 0; z < nz; z++) for (let x = 0; x < nx; x++) {
      if (y > 3 && (x === 0 || x === nx - 1 || z < y - 3 || z > nz - 1 - (y - 3))) continue;
      const m = new THREE.Mesh(brickGeo, [side, side, bm, side, side, side]); const tx = (x - (nx - 1) / 2) * 0.52, tz = (z - (nz - 1) / 2) * 0.26, ty = 0.22 + y * 0.125;
      m.castShadow = m.receiveShadow = true; m.rotation.y = (R() - 0.5) * 0.06; scene.add(m);
      ctx.bricks.push({ m, tx, ty, tz, d: y * 0.3 + R() * 0.25 });
    }
    const l = label(THREE, '≥ €30 MILLION', { size: 0.055, sub: 'damage · government estimate', anchor: 'left', color: '#34d399', subColor: '#e3e8ef' }); l.position.set(1.3, 1.3, 0); l.material.opacity = 0; scene.add(l); ctx.lab = l;
    key.position.set(-2, 6, 4); key.target.position.set(0, 0.5, 0); key.intensity = 35; rim.position.set(2.5, 2, -3); rim.target.position.set(0, 0.6, 0);
  } else {
    const hoodies = [0x4a4f57, 0x6b2f2f, 0x2e3a4e, 0x55604a, 0x8a8478, 0x2a2a2c, 0x7a5a3a, 0x3d4b5a, 0x5e5450, 0x9a9488].map(c => std({ color: c, roughness: 0.9 }));
    const skin = std({ color: 0xcfc7bb, roughness: 0.55 }), pants = std({ color: 0x2b2f38, roughness: 0.85 }), shoe = std({ color: 0x1c1c1e });
    const tagT = ctex(THREE, 512, 256, (g, w, h) => { g.fillStyle = '#34d399'; g.fillRect(0, 0, w, h); g.fillStyle = '#1a1410'; g.beginPath(); g.arc(40, h / 2, 16, 0, 7); g.fill();
      g.font = '800 92px "Inter Display", Inter, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('€10,000', w / 2 + 20, h / 2 + 4); });
    const tagM = std({ map: tagT, roughness: 0.5, emissive: new THREE.Color(0x34d399), emissiveMap: tagT, emissiveIntensity: 0.08 });
    ctx.tags = [];
    for (let i = 0; i < 10; i++) {
      const x = (i - 4.5) * 0.95;
      const f = figure(THREE, { body: hoodies[i], head: skin, dark: pants, shoe, pack: hoodies[(i + 4) % 10], hair: pants }, { hood: i % 3 === 0, hair: i % 3 !== 0, backpack: i % 2 === 0, height: 1.62 + R() * 0.16 });
      f.position.set(x, 0, (R() - 0.5) * 0.3); f.rotation.y = (R() - 0.5) * 0.3; scene.add(f); f.traverse(o => { if (o.isMesh) o.castShadow = true; });
      const tg = new THREE.Group(); tg.position.set(x, 3.2, 0.45); scene.add(tg);
      const str = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.004, 1, 6), std({ color: 0xd8cfbd })); str.geometry.translate(0, -0.5, 0); tg.add(str);
      const card = new THREE.Mesh(new RoundedBoxGeometry(0.62, 0.31, 0.01, 2, 0.01), tagM); card.castShadow = true; tg.add(card);
      ctx.tags.push({ tg, str, card, i });
    }
    // the one window pane that actually got broken, behind figure 6
    const pane = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 1.4), new THREE.MeshStandardMaterial({ map: ctex(THREE, 256, 256, (g, w, h) => { g.fillStyle = 'rgba(160,170,175,0.25)'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(240,240,236,0.9)'; g.lineWidth = 2; for (let k2 = 0; k2 < 12; k2++) { let x = 128, y = 120, a = k2 / 12 * 6.28; g.beginPath(); g.moveTo(x, y); for (let s = 0; s < 7; s++) { a += (R() - 0.5) * 0.5; x += Math.cos(a) * 20; y += Math.sin(a) * 20; g.lineTo(x, y); } g.stroke(); } }), transparent: true, side: THREE.DoubleSide }));
    pane.position.set(1.4, 1.5, -1.6); scene.add(pane);
    const frame = new THREE.Mesh(new THREE.BoxGeometry(1.3, 1.5, 0.05), std({ color: 0x3a3c3e, metalness: 0.5 })); frame.position.set(1.4, 1.5, -1.66); scene.add(frame);
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(14, 4), std({ color: 0x2a2826, roughness: 0.95 })); wall.position.set(0, 2, -1.7); wall.receiveShadow = true; scene.add(wall);
    key.position.set(-2, 6, 6); key.target.position.set(0, 1, 0); key.intensity = 40; rim.position.set(0, 3, -3); rim.target.position.set(0, 1.4, 0); rim.intensity = 20;
  }
  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.6, bloomRadius: 0.55, bloomThreshold: 0.75,
    dof: shot === 'repair_need' ? null : { focus: shot === 'fine' ? 6.6 : 4.6, aperture: 0.001, maxblur: 0.005 } });
  return Object.assign(ctx, post);
}

const CAMS = {
  repair_need: [[0, [-8.8, 0.7, 2.6, -6.6, 0.35, 0]], [4.0, [-4.0, 1.3, 6.5, -2.0, 0.45, 0]], [8, [0.4, 1.9, 16.5, 0.2, 0.55, 0]]],
  damage_bill: [[0, [2.6, 1.8, 4.4, 0.2, 0.6, 0]], [7, [1.8, 2.2, 4.0, 0.4, 0.7, 0]]],
  fine: [[0, [-3.6, 1.5, 6.8, -1.2, 1.5, 0]], [7, [2.2, 1.6, 6.6, 0.9, 1.5, 0]]],
};

export function update(ctx, tt) {
  const { THREE, camera, shot } = ctx;
  const t = tt / ctx.k;
  const c = path(CAMS[shot] ?? CAMS.repair_need)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  if (shot === 'repair_need') {
    const M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), s = new THREE.Vector3(1, 1, 1), p = new THREE.Vector3();
    ctx.coins.forEach((C, n) => { const a = 0.5 + C.i * 0.22 + C.j * 0.012; const u = ease((t - a) / 0.35); const vis = u > 0.001;
      p.set(C.x + C.ox, C.y + (1 - u) * 1.2, C.oz); e.set(C.rx, 0, 0); q.setFromEuler(e); s.setScalar(vis ? 1 : 0.0001); M.compose(p, q, s); ctx.inst.setMatrixAt(n, M); });
    ctx.inst.instanceMatrix.needsUpdate = true;
    ctx.labs[0].material.opacity = sstep(1.0, 1.8, t); ctx.labs[1].material.opacity = sstep(6.2, 7.0, t);
  } else if (shot === 'damage_bill') {
    ctx.bricks.forEach(B => { const u = ease((t - 0.3 - B.d) / 0.5); B.m.position.set(B.tx, B.ty + (1 - u) * 2.5, B.tz); B.m.visible = u > 0.001; });
    ctx.lab.material.opacity = sstep(3.6, 4.4, t);
  } else {
    ctx.tags.forEach(T => { const a = 0.6 + T.i * 0.42; const u = clamp01((t - a) / 0.55); const drop = 1 - Math.pow(1 - u, 3); const bounce = u >= 1 ? Math.sin((t - a - 0.55) * 9) * Math.exp(-(t - a - 0.55) * 4) * 0.04 : 0;
      const len = 0.25 + 1.1 * drop; T.str.scale.y = len; T.card.position.y = -len - 0.15 + bounce; T.tg.rotation.z = bounce * 0.8; T.tg.visible = u > 0; });
  }
}

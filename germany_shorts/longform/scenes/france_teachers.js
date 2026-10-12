// France 2026: the 3,024 supply teachers, and the pupils without classes. Faceless figures, instanced.
// shots (?shot=name or name:seconds):
//   standby     (8 s)  a vast dark depot: rows of faceless teacher figures (≈ 1 per 10) standing still; overhead lights
//                      switch on row by row in amber from 1.5 s, then the front rows step forward (beats 111-112).
//   drop        (8 s)  a dark table-top of school blocks glowing red and orange; small faceless figures descend
//                      on thin amber light threads onto them; camera orbits (beat 116, "why weren't they there?").
//   empty_field (7 s)  30,000 pupils without classes: a field of empty desks and chairs receding into fog, cold
//                      light, one desk in the foreground under an amber pool (beat 119).
import { AMBER } from './lib.js';
import { glow, beam } from './look.js';
import { AMBER_HI, path, clamp01, sstep, fontsReady, finishPost, ctex, timing, label, ease, figure } from './france_lib.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

// one merged geometry per figure material slot (body / head / dark) for instancing
function figureGeos(THREE, opts) {
  const mats = { body: { id: 'body' }, head: { id: 'head' }, dark: { id: 'dark' }, shoe: { id: 'dark' }, hair: { id: 'dark' }, pack: { id: 'dark' } };
  const f = figure(THREE, mats, opts); f.updateMatrixWorld(true);
  const buckets = { body: [], head: [], dark: [] };
  f.traverse(o => { if (!o.isMesh) return; let g = o.geometry.index ? o.geometry.toNonIndexed() : o.geometry.clone();
    for (const k of Object.keys(g.attributes)) if (!['position', 'normal'].includes(k)) g.deleteAttribute(k);
    g.applyMatrix4(o.matrixWorld); buckets[o.material.id].push(g); });
  return Object.fromEntries(Object.entries(buckets).filter(([, v]) => v.length).map(([k, v]) => [k, mergeGeometries(v)]));
}

export async function setup(THREE, renderer, W, H) {
  const { name, k: k0 } = timing(8);
  const shot = name || 'standby';
  const k = shot === 'empty_field' ? k0 * 8 / 7 : k0;
  await fontsReady();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060607);
  scene.fog = new THREE.FogExp2(0x060607, shot === 'empty_field' ? 0.045 : shot === 'drop' ? 0.03 : 0.04);
  const camera = new THREE.PerspectiveCamera(shot === 'drop' ? 30 : 34, W / H, 0.05, 400);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.75, metalness: 0.05, ...o });
  let seed = 33; const R = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  const ctx = { THREE, scene, camera, shot, k };
  scene.add(new THREE.HemisphereLight(0x8e94a0, 0x080706, 0.3));

  if (shot === 'standby') {
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), std({ color: 0x1d1d1f, roughness: 0.35, metalness: 0.4 })); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
    const geos = figureGeos(THREE, { height: 1.74, hair: true });
    const mats = { body: std({ color: 0x5a5148 }), head: std({ color: 0xcfc7bb, roughness: 0.55 }), dark: std({ color: 0x24262b }) };
    const tints = [0x5a5148, 0x3d4b5a, 0x6b5a4a, 0x4a4f57, 0x7a7266, 0x55604a];
    const ROWS = 14, COLS = 22, sx = 1.25, sz = 1.6;
    const N = ROWS * COLS;
    const inst = {}; for (const [kk, g] of Object.entries(geos)) { inst[kk] = new THREE.InstancedMesh(g, mats[kk], N); inst[kk].castShadow = true; inst[kk].receiveShadow = true; scene.add(inst[kk]); }
    ctx.inst = inst; ctx.people = [];
    const col = new THREE.Color();
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) { const i = r * COLS + c; ctx.people.push({ x: (c - (COLS - 1) / 2) * sx + (R() - 0.5) * 0.2, z: -r * sz + (R() - 0.5) * 0.2, r, ry: (R() - 0.5) * 0.2, s: 0.95 + R() * 0.1 });
      inst.body.setColorAt(i, col.setHex(tints[Math.floor(R() * tints.length)])); }
    inst.body.instanceColor.needsUpdate = true;
    // overhead lamps per row
    ctx.lamps = []; for (let r = 0; r < ROWS; r += 2) { const z = -r * sz - 0.8;
      const bar = new THREE.Mesh(new THREE.BoxGeometry(COLS * sx, 0.06, 0.12), new THREE.MeshBasicMaterial({ color: 0x2a2620 })); bar.position.set(0, 6, z); scene.add(bar);
      const s = new THREE.SpotLight(0xffc27a, 0, 18, 1.2, 0.7, 1.3); s.position.set(0, 5.8, z); s.target.position.set(0, 0, z); scene.add(s, s.target);
      ctx.lamps.push({ bar, s, r }); }
    const sign = label(THREE, 'ON THE PAYROLL', { size: 0.042, sub: 'not assigned to any class', anchor: 'center', gap: 0, subColor: '#e9dfca' }); sign.position.set(0, 2.9, 3.2); sign.material.opacity = 0; scene.add(sign); ctx.sign = sign;
    const front = new THREE.DirectionalLight(0xc9d2e0, 0.35); front.position.set(3, 6, 12); scene.add(front);
  } else if (shot === 'drop') {
    const table = new THREE.Mesh(new THREE.CircleGeometry(30, 96), std({ color: 0x3a3936, roughness: 0.6, metalness: 0.1, map: ctex(THREE, 1024, 1024, (g, w, h) => { g.fillStyle = '#4a4844'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(233,223,202,0.12)'; g.lineWidth = 2; for (let x = 0; x <= w; x += 32) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); g.beginPath(); g.moveTo(0, x); g.lineTo(w, x); g.stroke(); } }) })); table.rotation.x = -Math.PI / 2; table.receiveShadow = true; scene.add(table);
    const schools = [];
    const sm = { red: std({ color: 0x5a2a22, emissive: new THREE.Color(0xd8281c), emissiveIntensity: 0.28, roughness: 0.6 }), orange: std({ color: 0x5a3a20, emissive: new THREE.Color(0xff6a14), emissiveIntensity: 0.22, roughness: 0.6 }), grey: std({ color: 0x2c2c2e, roughness: 0.7 }) };
    for (let i = 0; i < 140; i++) { const a = R() * Math.PI * 2, rr = 1.5 + Math.sqrt(R()) * 11; const x = Math.cos(a) * rr, z = Math.sin(a) * rr;
      const kind = i < 20 ? 'red' : i < 70 ? 'orange' : 'grey'; const w = 0.6 + R() * 0.5, h = 0.25 + R() * 0.2;
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, w * 0.6), sm[kind]); m.position.set(x, h / 2, z); m.rotation.y = R() * 3; m.castShadow = m.receiveShadow = true; scene.add(m); schools.push({ x, z, h, kind }); }
    const targets = schools.filter(s => s.kind !== 'grey');
    const geos = figureGeos(THREE, { height: 1.7, hair: true });
    const fm = { body: std({ color: 0x8a8070 }), head: std({ color: 0xd8d0c4, roughness: 0.5 }), dark: std({ color: 0x2a2a2e }) };
    const N = targets.length * 2;
    const inst = {}; for (const [kk, g] of Object.entries(geos)) { inst[kk] = new THREE.InstancedMesh(g, fm[kk], N); inst[kk].castShadow = true; scene.add(inst[kk]); }
    ctx.inst = inst; ctx.drops = [];
    const threadM = new THREE.MeshBasicMaterial({ color: AMBER_HI, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false });
    for (let i = 0; i < N; i++) { const T = targets[i % targets.length]; const ox = (i >= targets.length ? 0.18 : -0.18);
      const th = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 1, 6), threadM); th.geometry.translate(0, 0.5, 0); scene.add(th);
      ctx.drops.push({ x: T.x + ox * 1.6, z: T.z, y0: T.h, t0: 1.0 + R() * 4.5, th, s: 0.32 }); }
    const key = new THREE.SpotLight(0xfff1df, 500, 60, 0.6, 0.8, 1.2); key.position.set(-8, 22, 10); key.target.position.set(0, 0, 0); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); scene.add(key, key.target);
    const l = label(THREE, '3,024', { size: 0.06, sub: 'supply teachers sent to red and orange lycées', anchor: 'center', gap: 0, color: '#ffb25c', subColor: '#e9dfca' }); l.position.set(0, 4.2, 0); l.material.opacity = 0; scene.add(l); ctx.lab = l; scene.add(new THREE.HemisphereLight(0xb0b6c0, 0x1a1816, 0.5));
  } else {
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), std({ color: 0x4a4844, roughness: 0.55, metalness: 0.15 })); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
    // desk + chair merged geometry, instanced
    const parts = [];
    const B = (w, h, d, x, y, z) => { const g = new THREE.BoxGeometry(w, h, d); g.translate(x, y, z); parts.push(g); };
    B(1.2, 0.03, 0.5, 0, 0.75, 0); for (const sx of [-0.56, 0.56]) for (const sz2 of [-0.21, 0.21]) B(0.03, 0.74, 0.03, sx, 0.37, sz2);
    B(0.4, 0.03, 0.4, -0.3, 0.45, 0.55); B(0.4, 0.34, 0.03, -0.3, 0.68, 0.76); B(0.4, 0.03, 0.4, 0.3, 0.45, 0.55); B(0.4, 0.34, 0.03, 0.3, 0.68, 0.76);
    for (const cx of [-0.3, 0.3]) for (const ax of [-0.17, 0.17]) for (const az of [-0.17, 0.17]) B(0.025, 0.45, 0.025, cx + ax, 0.225, 0.55 + az);
    const geo = mergeGeometries(parts.map(g => g.toNonIndexed()));
    const COLS = 60, ROWS = 70, N = COLS * ROWS;
    const inst = new THREE.InstancedMesh(geo, std({ color: 0xa8a297, roughness: 0.6 }), N); inst.castShadow = true; inst.receiveShadow = true; scene.add(inst);
    const M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), p = new THREE.Vector3(), s = new THREE.Vector3(1, 1, 1);
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) { p.set((c - COLS / 2) * 1.8, 0, -r * 1.7); e.set(0, (R() - 0.5) * 0.08, 0); q.setFromEuler(e); M.compose(p, q, s); inst.setMatrixAt(r * COLS + c, M); }
    // the foreground desk (separate mesh, warm)
    const hero = new THREE.Mesh(geo, std({ color: 0x8a6c4c, roughness: 0.55 })); hero.position.set(0.9, 0, 3.4); hero.rotation.y = 0.05; hero.castShadow = true; scene.add(hero);
    const paper = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.005, 0.21), std({ color: 0xece7da })); paper.position.set(1.0, 0.77, 3.4); scene.add(paper);
    const pool = new THREE.SpotLight(AMBER, 0, 8, 0.32, 0.7, 1.4); pool.position.set(0.9, 5, 4.0); pool.target.position.set(0.9, 0, 3.4); pool.castShadow = true; scene.add(pool, pool.target); ctx.pool = pool;
    const poolBeam = beam(THREE, 0xffb060, 5, 1.4, 0.05); poolBeam.position.set(0.9, 5, 4.0); scene.add(poolBeam); ctx.poolBeam = poolBeam;
    const cold = new THREE.DirectionalLight(0xb9c6d8, 2.4); cold.position.set(-20, 18, 12); cold.castShadow = false; scene.add(cold); scene.add(new THREE.HemisphereLight(0x9aa6b8, 0x1a1816, 0.6));
  }
  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.65, bloomRadius: 0.6, bloomThreshold: 0.7,
    dof: shot === 'empty_field' ? { focus: 4.4, aperture: 0.0012, maxblur: 0.006 } : shot === 'standby' ? { focus: 9, aperture: 0.0008, maxblur: 0.004 } : null });
  return Object.assign(ctx, post);
}

const CAMS = {
  standby: [[0, [-5.0, 2.0, 9.5, 0, 1.4, -8]], [8, [-2.2, 2.6, 7.2, 0, 1.4, -8]]],
  drop: [[0, [7.5, 6.5, 10.5, 0, 0.6, 0]], [8, [10.5, 5.2, 4.5, 0, 0.6, 0]]],
  empty_field: [[0, [-1.2, 1.25, 7.4, 1.0, 0.8, -6]], [7, [0.2, 1.15, 6.6, 1.2, 0.8, -6]]],
};

export function update(ctx, tt) {
  const { THREE, camera, shot } = ctx;
  const t = tt / ctx.k;
  const c = path(CAMS[shot] ?? CAMS.standby)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  const M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), p = new THREE.Vector3(), s = new THREE.Vector3();
  if (shot === 'standby') {
    ctx.lamps.forEach(L => { const a = 1.5 + L.r * 0.18; const on = sstep(a, a + 0.25, t); L.s.intensity = 70 * on; L.bar.material.color.setHex(on > 0.5 ? 0xffd9a0 : 0x2a2620); });
    ctx.people.forEach((P, i) => { const step = P.r < 4 ? ease((t - 4.2 - P.r * 0.15) / 2.6) * 1.6 : 0; const bob = step > 0 && step < 1.6 ? Math.abs(Math.sin(t * 7 + i)) * 0.03 : 0;
      p.set(P.x, bob, P.z + step); e.set(0, P.ry, 0); q.setFromEuler(e); s.setScalar(P.s); M.compose(p, q, s); for (const m of Object.values(ctx.inst)) m.setMatrixAt(i, M); });
    for (const m of Object.values(ctx.inst)) m.instanceMatrix.needsUpdate = true;
    ctx.sign.material.opacity = sstep(2.4, 3.2, t);
  } else if (shot === 'drop') {
    ctx.drops.forEach((D, i) => { const u = ease((t - D.t0) / 1.4); const y = D.y0 + (1 - u) * 9;
      p.set(D.x, u > 0 ? y : -50, D.z); e.set(0, i, 0); q.setFromEuler(e); s.setScalar(D.s); M.compose(p, q, s); for (const m of Object.values(ctx.inst)) m.setMatrixAt(i, M);
      D.th.position.set(D.x, y + D.s * 1.8, D.z); D.th.scale.y = u > 0 && u < 1 ? (1 - u) * 9 + 0.5 : 0.001; D.th.visible = u > 0 && u < 0.999; });
    for (const m of Object.values(ctx.inst)) m.instanceMatrix.needsUpdate = true;
    ctx.lab.material.opacity = sstep(4.5, 5.3, t);
  } else {
    const on = sstep(1.0, 2.4, t); ctx.pool.intensity = 30 * on; ctx.poolBeam.material.uniforms.opacity.value = 0.05 * on;
  }
}

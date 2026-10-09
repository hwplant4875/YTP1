// Cold open, cinematic version: a sealed East Berlin station under West Berlin trains.
// shots:
//   lightsup   - dark platform, bulbs flicker on one by one, slow push in
//   guard      - low angle, the lamp over the guard catches, dust in the beam
//   cab        - driver's view: tunnel, then the ghost station slides past
//   passby     - platform level, the train streams past, the guard's head follows it
//   guardclose - tight on the guard while window light strobes across him
//   leave      - tail lights shrink into the tunnel, the bulbs dim
//   drift      - slow drift down the empty platform (title background)
import { AMBER, tileTex, concreteTex, textTex, rng, lerp } from './lib.js';
import { makeComposer, glow, beam, normalFromHeight, borderGuard, smooth, flicker } from './look.js';

const L = 120, HW = 8, HT = 5.4, TRACK = -2.1;

export async function setup(THREE, renderer, W, H) {
  const shot = new URLSearchParams(location.search).get('shot') || 'lightsup';
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020202);
  scene.fog = new THREE.FogExp2(0x060504, 0.03);
  const camera = new THREE.PerspectiveCamera(38, W / H, 0.05, 400);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.8, metalness: 0, ...o });

  // ---- tiles with real grout relief
  const tileN = normalFromHeight(THREE, 256, 256, (g, w, h) => {
    g.fillStyle = '#000'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff';
    for (let y = 0; y < h; y += 32) for (let x = 0; x < w; x += 64) g.fillRect(x + 2, y + 2, 60, 28);
  }, 3, [30, 3]);
  const wallMat = std({ map: tileTex(THREE, { repeat: [30, 3], tile: 32 }), normalMap: tileN, roughness: 0.35 });
  const floorRough = (() => { const r = rng(5); const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
    g.fillStyle = '#bbb'; g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 60; i++) { g.fillStyle = `rgba(20,20,20,${0.3 + r() * 0.5})`; g.beginPath(); g.ellipse(r() * 256, r() * 256, 8 + r() * 40, 4 + r() * 20, r() * 3, 0, 7); g.fill(); }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(2, 20); return t; })();
  for (const sx of [-1, 1]) {
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(L, HT), wallMat);
    wall.position.set(sx * HW, HT / 2, 0); wall.rotation.y = -sx * Math.PI / 2; wall.receiveShadow = true; scene.add(wall);
    const p = new THREE.Mesh(new THREE.BoxGeometry(3.6, 1, L), std({ map: concreteTex(THREE, [2, 30], 5 + sx, 105), roughnessMap: floorRough, roughness: 0.55 }));
    p.position.set(sx * (HW - 1.8), 0.5, 0); p.receiveShadow = true; scene.add(p);
    const edge = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.02, L), std({ color: 0xd2cdbf, roughness: 0.5 }));
    edge.position.set(sx * (HW - 3.45), 1.011, 0); scene.add(edge);
  }
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(HW * 2, L), std({ map: concreteTex(THREE, [3, 20], 11, 60) }));
  ceil.rotation.x = Math.PI / 2; ceil.position.y = HT; scene.add(ceil);
  const bed = new THREE.Mesh(new THREE.PlaneGeometry(HW * 2, L + 400), std({ map: concreteTex(THREE, [4, 120], 9, 45) }));
  bed.rotation.x = -Math.PI / 2; scene.add(bed);
  const rail = std({ color: 0xa0a0a0, metalness: 1, roughness: 0.25 });
  for (const tx of [-2.1, 2.1]) for (const o of [-0.72, 0.72]) {
    const r = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.14, L + 400), rail); r.position.set(tx + o, 0.22, 0); scene.add(r);
  }
  const sl = new THREE.InstancedMesh(new THREE.BoxGeometry(2.4, 0.14, 0.25), std({ color: 0x1c1b19 }), 1000);
  const m4 = new THREE.Matrix4(); let k = 0;
  for (const tx of [-2.1, 2.1]) for (let i = 0; i < 500; i++) { m4.makeTranslation(tx, 0.08, -260 + i * 1.04); sl.setMatrixAt(k++, m4); }
  scene.add(sl);
  // tunnel tubes beyond both ends
  const tun = std({ map: concreteTex(THREE, [60, 2], 31, 55), roughness: 0.95 });
  for (const zc of [-L / 2 - 150, L / 2 + 150]) {
    for (const sx of [-1, 1]) { const w = new THREE.Mesh(new THREE.PlaneGeometry(300, HT), tun); w.position.set(sx * 4.6, HT / 2, zc); w.rotation.y = -sx * Math.PI / 2; scene.add(w); }
    const c = new THREE.Mesh(new THREE.PlaneGeometry(9.2, 300), tun); c.rotation.x = Math.PI / 2; c.position.set(0, HT, zc); scene.add(c);
    for (const sx of [-1, 1]) { const e = new THREE.Mesh(new THREE.PlaneGeometry(HW - 4.6, HT), tun); e.position.set(sx * (4.6 + (HW - 4.6) / 2), HT / 2, Math.sign(zc) * L / 2); e.rotation.y = zc < 0 ? 0 : Math.PI; scene.add(e); }
  }
  // columns and beams
  const steel = std({ color: 0x2e2e2d, metalness: 0.7, roughness: 0.45 });
  for (let z = -L / 2 + 4; z < L / 2; z += 6.5) {
    const c = new THREE.Mesh(new THREE.BoxGeometry(0.3, HT, 0.3), steel); c.position.set(0, HT / 2, z); c.castShadow = true; scene.add(c);
    const b = new THREE.Mesh(new THREE.BoxGeometry(HW * 2, 0.32, 0.26), steel); b.position.set(0, HT - 0.16, z); scene.add(b);
  }
  const sign = std({ map: textTex(THREE, 'ROSENTHALER PLATZ'), roughness: 0.6 });
  for (const sx of [-1, 1]) for (const z of [-30, 0, 30]) {
    const b = new THREE.Mesh(new THREE.PlaneGeometry(4.2, 0.66), sign); b.position.set(sx * (HW - 0.02), 2.9, z); b.rotation.y = -sx * Math.PI / 2; scene.add(b);
  }

  // ---- bulbs: the only warm light in the world
  scene.add(new THREE.HemisphereLight(0x7c8696, 0x090807, 0.05));
  const lamps = [];
  const bulbMat = new THREE.MeshBasicMaterial({ color: 0xffd6a0 });
  let li = 0;
  for (let z = -48; z <= 48; z += 12) for (const sx of [-1, 1]) {
    const x = sx * (HW - 2.0), y = HT - 0.55;
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.07, 12, 8), bulbMat.clone()); b.position.set(x, y, z); scene.add(b);
    const shade = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.18, 20, 1, true), std({ color: 0x222222, side: THREE.DoubleSide })); shade.position.set(x, y + 0.1, z); scene.add(shade);
    const wire = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.45), steel); wire.position.set(x, HT - 0.22, z); scene.add(wire);
    const h = glow(THREE, AMBER, 1.6, 0.9); h.position.set(x, y - 0.02, z); scene.add(h);
    const bm = beam(THREE, AMBER, 4.2, 1.5, 0.05); bm.position.set(x, y, z); scene.add(bm);
    const pl = new THREE.PointLight(AMBER, 0, 11, 1.7); pl.position.set(x, y - 0.1, z); scene.add(pl);
    lamps.push({ bulb: b, halo: h, beam: bm, light: pl, z, sx, seed: li++, onAt: 0 });
  }

  // ---- guards
  const gmat = std({ color: 0x0d0d0d, roughness: 0.95 });
  const g1 = borderGuard(THREE, gmat); g1.group.position.set(-(HW - 2.1), 1, -8); g1.group.rotation.y = Math.PI / 2 - 0.2; scene.add(g1.group);
  const g2 = borderGuard(THREE, gmat); g2.group.position.set(-(HW - 1.5), 1, -20); g2.group.rotation.y = Math.PI / 2 + 0.3; scene.add(g2.group);
  // key light over guard 1, casting a long shadow
  const key = new THREE.SpotLight(AMBER, 0, 14, 0.75, 0.55, 1.4);
  key.position.set(-(HW - 2.2), HT - 0.7, -10.0); key.target.position.set(-(HW - 2.1), 0, -7.0);
  key.castShadow = true; key.shadow.mapSize.set(1024, 1024); key.shadow.bias = -0.0005; scene.add(key, key.target);
  const keyBulb = new THREE.Mesh(new THREE.SphereGeometry(0.07, 12, 8), bulbMat.clone()); keyBulb.position.copy(key.position); scene.add(keyBulb);
  const keyHalo = glow(THREE, AMBER, 1.8, 0.9); keyHalo.position.copy(key.position); scene.add(keyHalo);
  const keyBeam = beam(THREE, AMBER, 4.4, 1.7, 0.07); keyBeam.position.copy(key.position); scene.add(keyBeam);

  // dust drifting through the light
  const N = 1400, r = rng(17), pos = new Float32Array(N * 3), seeds = new Float32Array(N);
  for (let i = 0; i < N; i++) { pos[i * 3] = -HW + r() * HW * 2; pos[i * 3 + 1] = 0.8 + r() * 4.4; pos[i * 3 + 2] = -50 + r() * 100; seeds[i] = r() * 100; }
  const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const dot = (() => { const c = document.createElement('canvas'); c.width = c.height = 32; const g = c.getContext('2d'); const gr = g.createRadialGradient(16, 16, 0, 16, 16, 16); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 32, 32); return new THREE.CanvasTexture(c); })();
  const dust = new THREE.Points(dg, new THREE.PointsMaterial({ size: 0.035, map: dot, color: 0xffcf9a, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false }));
  scene.add(dust);
  const dustBase = pos.slice();

  // ---- West Berlin train: rounded cars, warm-lit interiors, passengers in silhouette
  const { RoundedBoxGeometry } = await import('three/addons/geometries/RoundedBoxGeometry.js');
  const train = new THREE.Group();
  const body = std({ color: 0x8d8a83, roughness: 0.4, metalness: 0.35 });
  const inner = new THREE.MeshBasicMaterial({ color: 0xc9b597 });
  const paxTex = (() => { const c = document.createElement('canvas'); c.width = 512; c.height = 128; const g = c.getContext('2d'); const rr = rng(3);
    for (let i = 0; i < 9; i++) { if (rr() < 0.35) continue; const x = 20 + i * 54 + rr() * 10, s = 0.8 + rr() * 0.35; g.fillStyle = '#000';
      g.beginPath(); g.arc(x, 58 - 10 * s, 13 * s, 0, 7); g.fill(); g.beginPath(); g.ellipse(x, 128, 26 * s, 58 * s, 0, 0, 7); g.fill();
      if (rr() < 0.3) { g.fillRect(x - 30, 70, 34, 26); } }   // a newspaper
    const t = new THREE.CanvasTexture(c); return t; })();
  const paxMat = new THREE.MeshBasicMaterial({ map: paxTex, transparent: true, color: 0x000000, alphaTest: 0.1 });
  for (let i = 0; i < 4; i++) {
    const car = new THREE.Mesh(new RoundedBoxGeometry(2.3, 2.95, 12.6, 4, 0.22), body); car.position.set(0, 1.88, i * 13); car.castShadow = true; train.add(car);
    for (const sx of [-1, 1]) {
      const strip = new THREE.Mesh(new THREE.PlaneGeometry(11.4, 0.85), inner); strip.position.set(sx * 1.165, 2.3, i * 13); strip.rotation.y = sx * Math.PI / 2; train.add(strip);
      const pax = new THREE.Mesh(new THREE.PlaneGeometry(11.0, 0.8), paxMat); pax.position.set(sx * 1.17, 2.27, i * 13); pax.rotation.y = sx * Math.PI / 2; train.add(pax);
      for (let w = -5; w <= 5; w += 2.5) { const post = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.9, 0.16), body); post.position.set(sx * 1.17, 2.3, i * 13 + w); train.add(post); }
      const wl = new THREE.PointLight(0xffe2b8, 1.4, 5, 2); wl.position.set(sx * 1.6, 2.3, i * 13); train.add(wl);
    }
  }
  const front = -6.35;
  const head = new THREE.SpotLight(0xfff2de, 0, 80, 0.38, 0.5, 1.1); head.position.set(0, 1.3, front - 0.1); head.target.position.set(0, 1.0, front - 40); train.add(head, head.target);
  const headBeam = beam(THREE, 0xfff2de, 26, 3.2, 0.025); headBeam.rotation.x = -Math.PI / 2; headBeam.position.set(0, 1.3, front - 0.1); train.add(headBeam);
  for (const o of [-0.68, 0.68]) { const hg = glow(THREE, 0xfff6e8, 0.7, 0.8); hg.position.set(o, 1.15, front - 0.12); train.add(hg); }
  for (const o of [-0.7, 0.7]) { const tg = glow(THREE, 0xff3b1f, 0.7, 0.9); tg.position.set(o, 1.2, 3 * 13 + 6.35 + 0.1); train.add(tg); }
  train.rotation.y = Math.PI;                       // front faces +z
  train.position.set(TRACK, 0, -400);
  scene.add(train);

  // headlight carried by the camera for the driver's view
  const camLight = new THREE.SpotLight(0xfff1dc, 0, 70, 0.45, 0.7, 1.0); scene.add(camLight, camLight.target);
  const camBeam = beam(THREE, 0xfff2de, 22, 3.0, 0.02); scene.add(camBeam); camBeam.visible = false;

  const post = makeComposer(THREE, renderer, scene, camera, W, H, {
    bloom: 0.9, bloomRadius: 0.8, bloomThreshold: 0.55, exposure: 1.15,
    dof: shot === 'guardclose' ? { focus: 4.2, aperture: 0.004, maxblur: 0.012 } : shot === 'guard' ? { focus: 6.2, aperture: 0.0018, maxblur: 0.008 } : null,
  });
  return { THREE, scene, camera, train, lamps, key, keyBulb, keyHalo, keyBeam, g1, g2, dust, dustBase, seeds, camLight, camBeam, shot, ...post };
}

function setLamp(l, v) {
  l.light.intensity = 7 * v; l.halo.material.opacity = v; l.beam.material.uniforms.opacity.value = 0.05 * v;
  l.bulb.material.color.setRGB(0.15 + 0.85 * v, 0.12 + 0.72 * v, 0.08 + 0.55 * v);
}

export function update(ctx, t) {
  const { THREE, camera, train, lamps, shot, g1 } = ctx;
  // dust drifts
  const p = ctx.dust.geometry.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const s = ctx.seeds[i];
    p.array[i * 3] = ctx.dustBase[i * 3] + Math.sin(t * 0.13 + s) * 0.25;
    p.array[i * 3 + 1] = ctx.dustBase[i * 3 + 1] + Math.sin(t * 0.09 + s * 1.7) * 0.2 - ((t * 0.03 + s) % 1) * 0.1;
    p.array[i * 3 + 2] = ctx.dustBase[i * 3 + 2] + Math.cos(t * 0.11 + s) * 0.25;
  }
  p.needsUpdate = true;

  let lampsOn = 1, keyOn = 1;
  ctx.camLight.intensity = 0; ctx.camBeam.visible = false;
  g1.head.rotation.y = 0;

  if (shot === 'lightsup') {
    // bulbs catch one after another from the far end towards us
    lamps.forEach(l => setLamp(l, flicker(t, 0.6 + (48 - l.z) / 96 * 4.2 + (l.sx > 0 ? 0.25 : 0), l.seed)));
    keyOn = flicker(t, 2.4, 9);
    const k = smooth(t / 9);
    camera.position.set(lerp(5.4, 5.0, k), lerp(2.2, 2.0, k), lerp(30, 18, k));
    camera.lookAt(lerp(-1.5, -2.5, k), 1.7, -20);
    train.position.z = -400;
    lampsOn = -1;
  } else if (shot === 'guard') {
    keyOn = flicker(t, 0.8, 4);
    lamps.forEach(l => setLamp(l, l.z > -30 && l.z < 20 ? 0.0 : 0.7 * flicker(t, 2.2, l.seed)));
    lampsOn = -1;
    const k = smooth(t / 7);
    camera.position.set(lerp(-5.5, -5.6, k), lerp(1.35, 1.5, k), lerp(-1.0, -2.6, k));
    camera.lookAt(-5.9, lerp(2.05, 2.2, k), -8.4);
    train.position.z = -400;
  } else if (shot === 'cab') {
    // driving in, braking from ~40 to 15 km/h as the station opens up
    const v0 = 11, v1 = 4.2, tb = 6, z0 = -L / 2 - 95;
    const z = t < tb ? z0 + v0 * t : z0 + v0 * tb + v1 * (t - tb) + (v0 - v1) * 2 * (1 - Math.exp(-(t - tb) / 2));
    const shake = 0.012 * Math.sin(t * 31) + 0.008 * Math.sin(t * 47.3);
    camera.position.set(TRACK + shake, 2.45 + shake * 0.6, z);
    camera.lookAt(TRACK + Math.sin(t * 0.4) * 0.12, 2.2, z + 30);
    ctx.camLight.intensity = 45;
    const dir = new THREE.Vector3(); camera.getWorldDirection(dir);
    ctx.camLight.position.copy(camera.position).add(new THREE.Vector3(0, -1.0, 0));
    ctx.camLight.target.position.copy(camera.position).addScaledVector(dir, 25);
    ctx.camBeam.visible = true; ctx.camBeam.position.copy(ctx.camLight.position); ctx.camBeam.lookAt(ctx.camLight.target.position); ctx.camBeam.rotateX(-Math.PI / 2);
    train.position.z = -400;
    // the guard turns to watch the cab go by
    const dz = z - (-8);
    g1.head.rotation.y = Math.max(-1.1, Math.min(1.1, Math.atan2(dz, 4.1) * -0.9));
  } else if (shot === 'passby') {
    const k = t / 8;
    train.position.z = lerp(-95, 60, k);
    camera.position.set(-4.0, 1.25, 5.5); camera.lookAt(-5.8, 1.9, -9);
    const front = train.position.z + 6.35;
    g1.head.rotation.y = Math.max(-1.2, Math.min(1.2, Math.atan2(front - (-8), 3.5) * -1));
  } else if (shot === 'guardclose') {
    train.position.z = lerp(-60, 50, t / 6);
    camera.position.set(-4.9, 1.72, -5.2); camera.lookAt(-5.9, 2.4, -8);
    const front = train.position.z + 6.35;
    g1.head.rotation.y = Math.max(-1.2, Math.min(1.2, Math.atan2(front - (-8), 3.5) * -1));
  } else if (shot === 'leave') {
    train.position.z = lerp(10, -170, smooth(t / 7) * 0.4 + (t / 7) * 0.6);
    camera.position.set(4.8, 2.0, 22); camera.lookAt(-2, 1.6, -40);
    lamps.forEach(l => setLamp(l, 0.85 * (1 - 0.6 * smooth((t - 3) / 4)) * (0.94 + 0.06 * Math.sin(t * 9 + l.seed))));
    lampsOn = -1; keyOn = 1 - 0.5 * smooth((t - 3) / 4);
  } else if (shot === 'drift') {
    const k = smooth(t / 10);
    camera.position.set(5.2, 2.3, lerp(10, 2, k)); camera.lookAt(-3, 1.9, lerp(-20, -30, k));
    train.position.z = -400;
  }
  if (lampsOn === 1) lamps.forEach(l => setLamp(l, 0.92 + 0.08 * Math.sin(t * 9 + l.seed) * Math.sin(t * 2.3 + l.seed)));
  // train headlight only when the train is in play
  train.children.forEach(c => { if (c.isSpotLight) c.intensity = train.position.z > -300 ? 35 : 0; });
  ctx.key.intensity = 26 * keyOn; ctx.keyHalo.material.opacity = keyOn; ctx.keyBeam.material.uniforms.opacity.value = 0.07 * keyOn;
  ctx.keyBulb.material.color.setRGB(0.15 + 0.85 * keyOn, 0.12 + 0.72 * keyOn, 0.08 + 0.55 * keyOn);
}

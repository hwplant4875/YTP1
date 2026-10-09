// A sealed East Berlin U-Bahn station, 1961-1989: dim amber lamps, armed guards,
// a West Berlin train rolling through without stopping.
// params via ?shot=: "platform" (default), "guard", "thumb"
import { AMBER, tileTex, concreteTex, textTex, person, ease, lerp, canvasTex, rng } from './lib.js';
import { makeComposer, glow } from './look.js';

function canvasTexP(THREE, seed) {
  const r = rng(seed);
  return canvasTex(THREE, 256, 352, (g, w, h) => {
    const v = 150 + r() * 40;
    g.fillStyle = `rgb(${v},${v - 4},${v - 12})`; g.fillRect(0, 0, w, h);
    g.fillStyle = `rgba(40,38,34,${0.5 + r() * 0.3})`;
    g.fillRect(20, 30, w - 40, 120 + r() * 60);                       // faded picture block
    g.font = 'bold 34px "DejaVu Serif", serif'; g.textAlign = 'center';
    g.fillText(['BERLIN', 'KINO', 'SEIFE', 'TABAK'][Math.floor(r() * 4)], w / 2, h - 110);
    g.font = '18px "DejaVu Serif", serif'; g.fillText('1961', w / 2, h - 70);
    for (let i = 0; i < 400; i++) { g.fillStyle = `rgba(90,85,78,${r() * 0.25})`; g.fillRect(r() * w, r() * h, 2 + r() * 8, 1 + r() * 3); }
    g.fillStyle = 'rgba(30,28,25,0.25)'; g.fillRect(0, h * (0.5 + r() * 0.4), w, h);   // water stain
  });
}

export async function setup(THREE, renderer, W, H) {
  const shot = new URLSearchParams(location.search).get('shot') || window.SHOT || 'platform';
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050505);
  scene.fog = new THREE.FogExp2(0x0a0908, 0.035);
  const camera = new THREE.PerspectiveCamera(42, W / H, 0.1, 400);

  const L = 120, HW = 8, HT = 5.4;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.85, metalness: 0.0, ...o });
  const railMatT = std({ color: 0x777777, metalness: 0.9, roughness: 0.35 });

  // bare concrete tunnel running on past both ends of the station
  const tun = std({ map: concreteTex(THREE, [60, 2], 31, 60), roughness: 0.95 });
  for (const zc of [-L / 2 - 150, L / 2 + 150]) {
    for (const sx of [-1, 1]) { const w = new THREE.Mesh(new THREE.PlaneGeometry(300, HT), tun); w.position.set(sx * 4.6, HT / 2, zc); w.rotation.y = -sx * Math.PI / 2; scene.add(w); }
    const c = new THREE.Mesh(new THREE.PlaneGeometry(9.2, 300), tun); c.rotation.x = Math.PI / 2; c.position.set(0, HT, zc); scene.add(c);
    const f = new THREE.Mesh(new THREE.PlaneGeometry(9.2, 300), std({ map: concreteTex(THREE, [3, 80], 32, 45) })); f.rotation.x = -Math.PI / 2; f.position.set(0, 0.01, zc); scene.add(f);
    for (const tx of [-2.1, 2.1]) for (const o of [-0.72, 0.72]) { const r = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.14, 300), railMatT); r.position.set(tx + o, 0.22, zc); scene.add(r); }
    // end walls of the station box so the tiles do not show from the tunnel
    for (const sx of [-1, 1]) { const e = new THREE.Mesh(new THREE.PlaneGeometry(HW - 4.6, HT), tun); e.position.set(sx * (4.6 + (HW - 4.6) / 2), HT / 2, Math.sign(zc) * L / 2); e.rotation.y = zc < 0 ? 0 : Math.PI; scene.add(e); }
  }
  // the border line painted across the tunnel wall, where West Berlin ends
  const lineMat = new THREE.MeshBasicMaterial({ color: 0xcfcfc8 });
  for (const sx of [-1, 1]) { const ln = new THREE.Mesh(new THREE.PlaneGeometry(0.25, HT * 0.8), lineMat); ln.position.set(sx * 4.58, HT * 0.45, -L / 2 - 90); ln.rotation.y = -sx * Math.PI / 2; scene.add(ln); }

  // walls, floor, ceiling
  const wallMat = std({ map: tileTex(THREE, { repeat: [30, 3] }), roughness: 0.55 });
  for (const sx of [-1, 1]) {
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(L, HT), wallMat);
    wall.position.set(sx * HW, HT / 2, 0); wall.rotation.y = -sx * Math.PI / 2; scene.add(wall);
  }
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(HW * 2, L), std({ map: concreteTex(THREE, [3, 20], 11, 70) }));
  ceil.rotation.x = Math.PI / 2; ceil.position.y = HT; scene.add(ceil);
  const concrete = std({ map: concreteTex(THREE, [2, 30], 5, 110) });
  // platforms (side platforms, 1 m high)
  for (const sx of [-1, 1]) {
    const p = new THREE.Mesh(new THREE.BoxGeometry(3.6, 1, L), concrete);
    p.position.set(sx * (HW - 1.8), 0.5, 0); scene.add(p);
    const edge = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.02, L), std({ color: 0xd8d4c8, roughness: 0.6 }));
    edge.position.set(sx * (HW - 3.6 + 0.2), 1.011, 0); scene.add(edge);
  }
  // track bed, rails, sleepers
  const bed = new THREE.Mesh(new THREE.PlaneGeometry(HW * 2, L), std({ map: concreteTex(THREE, [4, 40], 9, 55) }));
  bed.rotation.x = -Math.PI / 2; scene.add(bed);
  const railMat = std({ color: 0x9a9a9a, metalness: 0.9, roughness: 0.35 });
  const sleeperMat = std({ color: 0x2a2826 });
  for (const tx of [-2.1, 2.1]) {
    for (const o of [-0.72, 0.72]) {
      const r = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.14, L), railMat); r.position.set(tx + o, 0.22, 0); scene.add(r);
    }
    const sl = new THREE.InstancedMesh(new THREE.BoxGeometry(2.4, 0.14, 0.25), sleeperMat, 160);
    const m = new THREE.Matrix4();
    for (let i = 0; i < 160; i++) { m.makeTranslation(tx, 0.08, -L / 2 + i * 0.75); sl.setMatrixAt(i, m); }
    scene.add(sl);
  }
  // riveted steel columns between the tracks
  const colMat = std({ color: 0x3b3b3a, metalness: 0.6, roughness: 0.5 });
  for (let z = -L / 2 + 4; z < L / 2; z += 6.5) {
    const c = new THREE.Mesh(new THREE.BoxGeometry(0.32, HT, 0.32), colMat); c.position.set(0, HT / 2, z); scene.add(c);
    const beam = new THREE.Mesh(new THREE.BoxGeometry(HW * 2, 0.35, 0.3), colMat); beam.position.set(0, HT - 0.18, z); scene.add(beam);
  }
  // station name boards, left as they were in 1961
  const sign = std({ map: textTex(THREE, 'ROSENTHALER PLATZ'), roughness: 0.7 });
  for (const sx of [-1, 1]) for (const z of [-30, 0, 30]) {
    const b = new THREE.Mesh(new THREE.PlaneGeometry(4.2, 0.66), sign);
    b.position.set(sx * (HW - 0.02), 2.9, z); b.rotation.y = -sx * Math.PI / 2; scene.add(b);
  }
  // posters nobody has changed since 1961, faded to grey
  const posterTex = (seed) => canvasTexP(THREE, seed);
  for (const sx of [-1, 1]) for (const z of [-42, -18, 12, 38]) {
    const pmesh = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 2.2), std({ map: posterTex(z * sx + 100), roughness: 0.9 }));
    pmesh.position.set(sx * (HW - 0.03), 2.6, z); pmesh.rotation.y = -sx * Math.PI / 2; scene.add(pmesh);
  }

  // bricked-up stair exits at the platform ends
  const brick = std({ map: concreteTex(THREE, [2, 2], 21, 90) });
  for (const sx of [-1, 1]) {
    const w = new THREE.Mesh(new THREE.BoxGeometry(3.6, HT - 1, 0.4), brick); w.position.set(sx * (HW - 1.8), 1 + (HT - 1) / 2, -L / 2 + 6); scene.add(w);
  }

  // the only warm light in the world: a few bare amber bulbs
  scene.add(new THREE.HemisphereLight(0x8a8f99, 0x0b0a09, 0.12));
  const bulbMat = new THREE.MeshBasicMaterial({ color: AMBER });
  const lamps = [];
  for (let z = -48; z <= 48; z += 16) {
    for (const sx of [-1, 1]) {
      const b = new THREE.Mesh(new THREE.SphereGeometry(0.09, 12, 8), bulbMat); b.position.set(sx * (HW - 1.8), HT - 0.5, z); scene.add(b);
      const wire = new THREE.Mesh(new THREE.CylinderGeometry(0.01, 0.01, 0.4), colMat); wire.position.set(sx * (HW - 1.8), HT - 0.25, z); scene.add(wire);
    }
    const pl = new THREE.PointLight(AMBER, 9, 22, 1.6); pl.position.set(0, HT - 0.6, z); scene.add(pl); lamps.push(pl);
  }

  // border guards on the far platform
  const guardMat = std({ color: 0x1c1c1b, roughness: 0.9 });
  const guards = [];
  for (const [x, z, ry] of [[-(HW - 2.0), -6, 0.6], [-(HW - 1.4), -14, 1.2]]) {
    const g = person(THREE, guardMat, { rifle: true }); g.position.set(x, 1, z); g.rotation.y = ry; scene.add(g); guards.push(g);
  }

  // West Berlin train, 4 cars, lit windows, headlights
  const train = new THREE.Group();
  const body = std({ color: 0xb9b6ae, roughness: 0.5, metalness: 0.2 });
  const win = new THREE.MeshBasicMaterial({ color: 0xe8e2d0 });
  for (let i = 0; i < 4; i++) {
    const car = new THREE.Mesh(new THREE.BoxGeometry(2.3, 2.9, 12.6), body); car.position.set(0, 1.85, i * 13); train.add(car);
    for (let k = 0; k < 5; k++) for (const sx of [-1, 1]) {
      const w = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 0.8), win);
      w.position.set(sx * 1.16, 2.3, i * 13 - 5 + k * 2.5); w.rotation.y = sx * Math.PI / 2; train.add(w);
    }
  }
  const head = new THREE.SpotLight(0xfff3e0, 60, 70, 0.5, 0.6, 1.2);
  head.position.set(0, 1.4, -6.5); head.target.position.set(0, 1.0, -40); train.add(head, head.target);
  for (const o of [-0.7, 0.7]) {
    const hl = new THREE.Mesh(new THREE.CircleGeometry(0.13, 16), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    hl.position.set(o, 1.2, -6.31); hl.rotation.y = Math.PI; train.add(hl);
  }
  train.rotation.y = Math.PI;
  train.position.set(-2.1, 0, -200);
  scene.add(train);

  // headlight carried by the camera for the driver's-view shots
  const camLight = new THREE.SpotLight(0xfff1dc, 0, 60, 0.42, 0.7, 1.1);
  scene.add(camLight, camLight.target);
  // key light for the poster shot: one amber bulb right above the guard
  const key = new THREE.PointLight(AMBER, shot === 'poster' ? 14 : 0, 8, 1.6);
  key.position.set(-6.6, 3.5, -8.6); scene.add(key);
  if (shot === 'poster') { const kb = new THREE.Mesh(new THREE.SphereGeometry(0.1, 12, 8), bulbMat); kb.position.copy(key.position); scene.add(kb); }
  scene.traverse(o => { if (o.isMesh && o.material === bulbMat) { const h = glow(THREE, AMBER, 1.4, 0.85); h.position.copy(o.position); scene.add(h); } });
  const post = makeComposer(THREE, renderer, scene, camera, W, H, { bloom: 0.85, bloomRadius: 0.75, bloomThreshold: 0.58, exposure: 1.1 });
  return { THREE, scene, camera, train, guards, lamps, shot, camLight, ...post };
}

export function update(ctx, t) {
  const L = 120;
  const { camera, train, lamps, shot } = ctx;
  // bulbs breathe a little, like old wiring
  lamps.forEach((l, i) => { l.intensity = 9 * (0.9 + 0.1 * Math.sin(t * 7 + i * 1.7) * Math.sin(t * 2.3 + i)); });
  ctx.train.visible = shot !== 'cab' && shot !== 'border';
  if (shot === 'cab') {
    // driver's view: dark tunnel, then the ghost station slides past at walking pace
    const z = -L / 2 - 60 + t * 4.2;
    camera.position.set(-2.1, 2.45, z); camera.lookAt(-2.1 + Math.sin(t * 0.3) * 0.15, 2.2, z + 30);
  } else if (shot === 'border') {
    const z = -L / 2 - 118 + t * 4.2;
    camera.position.set(-1.6, 2.3, z); camera.lookAt(-4.6, 2.0, z + 14);
  }
  if (shot === 'cab' || shot === 'border') {
    const dir = new ctx.THREE.Vector3(); camera.getWorldDirection(dir);
    ctx.camLight.intensity = 170;
    ctx.camLight.position.copy(camera.position).add(new ctx.THREE.Vector3(0, -0.9, 0));
    ctx.camLight.target.position.copy(camera.position).addScaledVector(dir, 20);
    return;
  }
  if (shot === 'poster') {
    camera.fov = 34; camera.updateProjectionMatrix();
    camera.position.set(-3.4, 1.35, 1.2); camera.lookAt(-6.0, 2.05, -6.5);
    train.position.z = -75 + t * 2;
    return;
  }
  if (shot === 'guard') {
    camera.position.set(lerp(-1.0, -0.4, ease(t / 8)), 2.2, lerp(2, -1, ease(t / 8)));
    camera.lookAt(-6.2, 1.9, -8);
    train.position.z = lerp(-180, 120, t / 8);
  } else if (shot === 'thumb') {
    camera.position.set(-5.2, 2.0, 2.5); camera.lookAt(-6.4, 1.75, -12);
    train.position.z = -70;
  } else {
    // slow dolly down the empty platform while the train rolls through without stopping
    camera.position.set(5.8, 2.5, lerp(26, 14, ease(t / 10)));
    camera.lookAt(-1.5, 1.8, -20);
    train.position.z = lerp(-170, 40, Math.min(t / 10, 1));
  }
}

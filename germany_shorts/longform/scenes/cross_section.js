// Cut-away of Berlin 1961-1989: the Wall on the street, a sealed station underneath,
// a West Berlin train passing through it. Used for the thumbnail and the explainer shots.
// shots: thumb | reveal (camera sinks from street level into the ground) | pass
import { AMBER, tileTex, concreteTex, textTex, person, ease, lerp, rng } from './lib.js';

export async function setup(THREE, renderer, W, H) {
  const shot = window.SHOT || new URLSearchParams(location.search).get('shot') || 'thumb';
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x07080a);
  scene.fog = new THREE.Fog(0x07080a, 120, 260);
  const camera = new THREE.PerspectiveCamera(28, W / H, 0.5, 600);
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.9, ...o });

  // --- earth block with the station cavity cut out (x along the tunnel, y up, z towards camera)
  const LEN = 70, DEP = 14, TOP = 0, CAV_Y0 = -9.5, CAV_Y1 = -3.2, CAV_Z0 = -5, CAV_Z1 = 5;
  const earthTex = (() => {
    const r = rng(4);
    const c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d');
    g.fillStyle = '#5e554a'; g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 9000; i++) { const v = 55 + r() * 60; g.fillStyle = `rgba(${v + 8},${v + 4},${v},0.5)`; g.fillRect(r() * 512, r() * 512, 1 + r() * 3, 1 + r() * 3); }
    for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(80,74,66,${0.2 + r() * 0.3})`; g.beginPath(); g.ellipse(r() * 512, r() * 512, 3 + r() * 9, 2 + r() * 6, r() * 3, 0, 7); g.fill(); }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(6, 2); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const earth = std({ map: earthTex, color: 0xffffff });
  const box = (w, h, d, x, y, z, m) => { const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); b.position.set(x, y, z); scene.add(b); return b; };
  box(LEN, TOP - CAV_Y1, 20, 0, (TOP + CAV_Y1) / 2, -5, earth);                       // above the cavity
  box(LEN, CAV_Y0 + DEP, 20, 0, (CAV_Y0 - DEP) / 2, -5, earth);                       // below
  box(LEN, CAV_Y1 - CAV_Y0, 30 / 2 + CAV_Z0, 0, (CAV_Y0 + CAV_Y1) / 2, (-15 + CAV_Z0) / 2, earth); // behind
  // concrete tunnel shell (thin frame around the cavity, visible on the cut face)
  const shell = std({ map: concreteTex(THREE, [8, 1], 2, 95) });
  box(LEN, 0.5, CAV_Z1 - CAV_Z0 + 1, 0, CAV_Y1 + 0.25, 0, shell);
  box(LEN, 0.5, CAV_Z1 - CAV_Z0 + 1, 0, CAV_Y0 - 0.25, 0, shell);
  box(LEN, CAV_Y1 - CAV_Y0, 0.5, 0, (CAV_Y0 + CAV_Y1) / 2, CAV_Z0 - 0.25, shell);

  // --- the station inside
  const tiles = std({ map: tileTex(THREE, { repeat: [24, 2] }), roughness: 0.5 });
  const back = new THREE.Mesh(new THREE.PlaneGeometry(LEN, CAV_Y1 - CAV_Y0), tiles);
  back.position.set(0, (CAV_Y0 + CAV_Y1) / 2, CAV_Z0 + 0.01); scene.add(back);
  const plat = std({ map: concreteTex(THREE, [10, 1], 6, 115) });
  box(LEN, 1, 3.4, 0, CAV_Y0 + 0.5, CAV_Z0 + 1.7, plat);
  box(LEN, 0.03, 0.3, 0, CAV_Y0 + 1.01, CAV_Z0 + 3.25, std({ color: 0xd8d4c8 }));
  const sign = std({ map: textTex(THREE, 'ROSENTHALER PLATZ') });
  for (const x of [-16, 16]) { const s = new THREE.Mesh(new THREE.PlaneGeometry(4.4, 0.7), sign); s.position.set(x, CAV_Y0 + 3.4, CAV_Z0 + 0.03); scene.add(s); }
  const rail = std({ color: 0x8a8a8a, metalness: 0.9, roughness: 0.3 });
  for (const z of [1.2, 2.6]) box(LEN, 0.12, 0.07, 0, CAV_Y0 + 0.2, z, rail);

  // one amber lamp over the guard: the only warm light in the frame
  const lampX = -2;
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 8), new THREE.MeshBasicMaterial({ color: AMBER }));
  bulb.position.set(lampX, CAV_Y1 - 0.6, CAV_Z0 + 1.6); scene.add(bulb);
  const lamp = new THREE.PointLight(AMBER, 28, 16, 1.4); lamp.position.copy(bulb.position); scene.add(lamp);
  const lamp2 = new THREE.PointLight(AMBER, 6, 10, 1.6); lamp2.position.set(20, CAV_Y1 - 0.6, CAV_Z0 + 1.6); scene.add(lamp2);
  const guardMat = std({ color: 0x111111 });
  const guard = person(THREE, guardMat, { rifle: true }); guard.position.set(lampX + 0.6, CAV_Y0 + 1, CAV_Z0 + 1.4); guard.rotation.y = 0.35; scene.add(guard);
  const guard2 = person(THREE, guardMat, { rifle: true }); guard2.position.set(21, CAV_Y0 + 1, CAV_Z0 + 1.2); guard2.rotation.y = -0.5; scene.add(guard2);

  // the West Berlin train in the station, not stopping
  const train = new THREE.Group();
  const body = std({ color: 0x9d9a93, roughness: 0.45, metalness: 0.25 });
  const win = new THREE.MeshBasicMaterial({ color: 0xdcd6c4 });
  for (let i = 0; i < 4; i++) {
    const car = new THREE.Mesh(new THREE.BoxGeometry(12.6, 2.9, 2.3), body); car.position.set(i * 13, 1.85, 0); train.add(car);
    for (let k = 0; k < 5; k++) { const w = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 0.8), win); w.position.set(i * 13 - 5 + k * 2.5, 2.3, 1.16); train.add(w); }
  }
  const hl = new THREE.SpotLight(0xfff1dc, 80, 40, 0.45, 0.6, 1.2); hl.position.set(-6.4, 1.4, 0); hl.target.position.set(-30, 1, 0); train.add(hl, hl.target);
  train.position.set(-8, CAV_Y0, 1.9); scene.add(train);

  // --- street level: the Wall, death strip lamps, a watchtower, dark buildings
  const wallMat = std({ map: concreteTex(THREE, [14, 1], 8, 150), roughness: 0.8 });
  const wall = new THREE.Group();
  for (let x = -LEN / 2; x < LEN / 2; x += 1.2) {
    const seg = new THREE.Mesh(new THREE.BoxGeometry(1.18, 3.6, 0.2), wallMat); seg.position.set(x + 0.6, 1.8, 0); wall.add(seg);
  }
  const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, LEN, 16), wallMat); pipe.rotation.z = Math.PI / 2; pipe.position.y = 3.7; wall.add(pipe);
  wall.position.z = 3; scene.add(wall);
  const ground = std({ map: concreteTex(THREE, [10, 4], 12, 70) });
  box(LEN, 0.1, 20, 0, 0.05, -5, ground);
  const tower = new THREE.Group();
  const tm = std({ color: 0x8c8a85 });
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.7, 8, 16), tm); shaft.position.y = 4; tower.add(shaft);
  const cab = new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.4, 1.8, 8), tm); cab.position.y = 8.9; tower.add(cab);
  const glass = new THREE.Mesh(new THREE.CylinderGeometry(1.42, 1.42, 0.7, 8, 1, true), new THREE.MeshBasicMaterial({ color: 0x2a2d30 })); glass.position.y = 9.1; tower.add(glass);
  tower.position.set(10, 0, -4); scene.add(tower);
  for (let x = -30; x <= 30; x += 12) {
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 6), tm); pole.position.set(x, 3, -1.5); scene.add(pole);
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.15, 0.3), new THREE.MeshBasicMaterial({ color: 0xcfd6dc })); head.position.set(x, 6, -1.4); scene.add(head);
    const sl = new THREE.SpotLight(0xbfcad6, 25, 18, 0.8, 0.7, 1.5); sl.position.set(x, 6, -1.4); sl.target.position.set(x, 0, 1); scene.add(sl, sl.target);
  }
  const bld = std({ color: 0x3a3a3c });
  const r = rng(9);
  for (let x = -LEN / 2; x < LEN / 2; x += 7) {
    const h = 10 + r() * 10; box(6, h, 8, x + 3, h / 2, -12, bld);
  }
  scene.add(new THREE.HemisphereLight(0x6f7a88, 0x0a0907, 0.35));
  const moon = new THREE.DirectionalLight(0x9fb0c8, 0.5); moon.position.set(-20, 40, 30); scene.add(moon);
  // soft cold fill on the cut face so the earth layers read
  const fill = new THREE.DirectionalLight(0xa9a59c, 1.8); fill.position.set(10, 2, 60); fill.target.position.set(0, -6, 0); scene.add(fill, fill.target);

  return { scene, camera, train, lamp, shot };
}

export function update(ctx, t) {
  const { camera, train, lamp, shot } = ctx;
  lamp.intensity = 28 * (0.92 + 0.08 * Math.sin(t * 6.1) * Math.sin(t * 1.7));
  if (shot === 'reveal') {
    // start on the street looking at the Wall, then sink through the ground into the station
    const k = ease(t / 9);
    camera.position.set(lerp(-6, 2, k), lerp(4, -3.5, k), lerp(26, 30, k));
    camera.lookAt(lerp(-2, 0, k), lerp(3, -5.5, k), 0);
    train.position.x = lerp(-60, 30, t / 12);
  } else if (shot === 'pass') {
    camera.position.set(0, -4.2, 26); camera.lookAt(0, -6.2, 0);
    train.position.x = lerp(-70, 40, t / 8);
  } else {
    camera.position.set(-24, 9, 44); camera.lookAt(-1, -4.4, 0);
    train.position.x = 9;
  }
}

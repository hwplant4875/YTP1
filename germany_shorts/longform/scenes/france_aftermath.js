// France 2026: aftermath only (no people, no flames at full blaze): charred surfaces, smoke, a few dying embers.
// shots (?shot=name or name:seconds):
//   nantes     (8 s)  dawn, outside a 1960s lycée: the entrance hall is burned out, glass doors gone, soot plumes up the
//                     façade, a melted bin, smoke still rising; slow push toward the black doorway where embers glow.
//   marseille  (8 s)  dusk street: a burned-out fire truck (generic, no markings), smoke column, and a bus-stop
//                     display reading "NETWORK SUSPENDED" in amber LEDs; lateral dolly.
//   ransacked  (7 s)  inside a classroom after an attack: desks overturned, papers, a broken window, soot on the
//                     ceiling; cold daylight through the window, amber light on the scorched wall.
const AMBER = 0xffa64a;   // v2: subject colour instead of the channel amber
import { glow, beam } from './look.js';
import { path, clamp01, sstep, fontsReady, finishPost, ctex, spacedText, timing, ease } from './france_lib.js';
const AMBER_HI = 0xff8a3d;
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export async function setup(THREE, renderer, W, H) {
  const { name, k: k0 } = timing(8);
  const shot = name || 'nantes';
  const k = shot === 'ransacked' ? k0 * 8 / 7 : k0;
  await fontsReady();
  const scene = new THREE.Scene();
  const bg = { nantes: 0x2a2d33, marseille: 0x241f22, ransacked: 0x0e0e0f }[shot];
  scene.background = new THREE.Color(bg);
  scene.fog = new THREE.FogExp2(bg, shot === 'ransacked' ? 0.05 : 0.035);
  const camera = new THREE.PerspectiveCamera(34, W / H, 0.05, 300);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.85, metalness: 0, ...o });
  let seed = 41; const R = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  const add = (geo, mat, x, y, z, rx = 0, ry = 0, rz = 0, parent = scene) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.rotation.set(rx, ry, rz); m.castShadow = m.receiveShadow = true; parent.add(m); return m; };
  const ctx = { THREE, scene, camera, shot, k };

  // soot-stained concrete: plumes rising from the bottom centre(s) of the texture
  const sootTex = (w, h, plumes, base = '#8a867e', rep = null) => ctex(THREE, w, h, (g) => {
    g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 20000; i++) { const v = 90 + R() * 70; g.fillStyle = `rgba(${v},${v},${v - 4},0.12)`; g.fillRect(R() * w, R() * h, 1 + R() * 3, 1 + R() * 3); }
    for (const [px, py, pw, ph] of plumes) for (let k2 = 0; k2 < 40; k2++) {
      const x = px + (R() - 0.5) * pw * (0.3 + k2 / 40), y = py - R() * ph, r = pw * (0.15 + R() * 0.35) * (1 - (py - y) / ph * 0.4);
      const grd = g.createRadialGradient(x, y, 0, x, y, r); grd.addColorStop(0, 'rgba(8,7,6,0.35)'); grd.addColorStop(1, 'rgba(8,7,6,0)'); g.fillStyle = grd; g.beginPath(); g.ellipse(x, y, r * 0.8, r * 1.3, 0, 0, 7); g.fill(); }
    for (const [px, py, pw] of plumes) { const grd = g.createRadialGradient(px, py, 0, px, py, pw * 0.7); grd.addColorStop(0, 'rgba(5,4,4,0.95)'); grd.addColorStop(1, 'rgba(5,4,4,0)'); g.fillStyle = grd; g.fillRect(px - pw, py - pw, pw * 2, pw * 2); }
  }, rep ? { repeat: rep } : {});
  const puff = ctex(THREE, 256, 256, (g) => { for (let i = 0; i < 18; i++) { const x = 128 + (R() - 0.5) * 90, y = 128 + (R() - 0.5) * 90, r = 40 + R() * 60; const grd = g.createRadialGradient(x, y, 0, x, y, r); grd.addColorStop(0, 'rgba(255,255,255,0.22)'); grd.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = grd; g.fillRect(0, 0, 256, 256); } });
  const smoke = (origin, n, spread, rise, color, op) => { const arr = []; for (let i = 0; i < n; i++) { const m = new THREE.SpriteMaterial({ map: puff, color, transparent: true, opacity: 0, depthWrite: false, fog: true });
      const s = new THREE.Sprite(m); s.userData = { o: origin.clone(), ph: R(), sp: spread, rise, op, rot: (R() - 0.5) * 0.4, dx: (R() - 0.5) * 2 }; scene.add(s); arr.push(s); } return arr; };
  const embers = (center, n, area) => { const g = new THREE.BufferGeometry(); const p = []; for (let i = 0; i < n; i++) p.push(center.x + (R() - 0.5) * area[0], center.y + R() * area[1], center.z + (R() - 0.5) * area[2]);
    g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); const pts = new THREE.Points(g, new THREE.PointsMaterial({ color: 0xff8a30, size: 0.05, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false })); scene.add(pts); return pts; };
  const charred = std({ color: 0x141210, roughness: 1 });
  const ash = std({ color: 0x2c2926, roughness: 1 });

  if (shot === 'nantes') {
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(120, 80), std({ map: ctex(THREE, 512, 512, (g, w, h) => { g.fillStyle = '#4a4946'; g.fillRect(0, 0, w, h); for (let i = 0; i < 20000; i++) { const v = 50 + R() * 50; g.fillStyle = `rgba(${v},${v},${v},0.35)`; g.fillRect(R() * w, R() * h, 2, 2); } }, { repeat: [30, 20] }), roughness: 0.75, metalness: 0.1 }));
    ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
    // wet patches from the hoses
    for (let i = 0; i < 6; i++) { const m = new THREE.Mesh(new THREE.CircleGeometry(1 + R() * 2, 32), std({ color: 0x1c1d1f, roughness: 0.08, metalness: 0.6 })); m.rotation.x = -Math.PI / 2; m.position.set((R() - 0.5) * 10, 0.004, 2 + R() * 6); m.scale.y = 0.6; scene.add(m); }
    // façade: 30 m long, 10 m tall, entrance block in the middle protruding
    const fac = sootTex(2048, 1024, [[1024, 1024, 520, 900]], '#8d8a82');
    const facM = std({ map: fac, roughness: 0.92 });
    const facGeo = (x0, x1, y0, y1) => { const g = new THREE.BoxGeometry(x1 - x0, y1 - y0, 0.4); const uv = g.attributes.uv;
      for (let i = 0; i < uv.count; i++) { uv.setXY(i, ((uv.getX(i) * (x1 - x0)) + x0 + 15) / 30, ((uv.getY(i) * (y1 - y0)) + y0) / 10); } return g; };
    add(facGeo(-15, -3.5, 0, 10), facM, -9.25, 5, -0.2); add(facGeo(3.5, 15, 0, 10), facM, 9.25, 5, -0.2); add(facGeo(-3.5, 3.5, 3.2, 10), facM, 0, 6.6, -0.2);
    // ribbon windows (dark), some broken with black interiors above the entrance
    for (let f = 0; f < 3; f++) for (let i = 0; i < 12; i++) { const x = -13.5 + i * 2.45; if (Math.abs(x) < 3 && f === 0) continue;
      const near = Math.abs(x) < 4 && f < 2; const win = add(new THREE.PlaneGeometry(2.0, 1.4), near ? charred : std({ color: 0x23272b, roughness: 0.15, metalness: 0.6 }), x, 2.0 + f * 3.1, 0.01); }
    // soot plume decals above the doorway and two first-floor windows
    const plumeT = ctex(THREE, 512, 1024, (g, w, h) => { for (let k2 = 0; k2 < 90; k2++) { const y = h - Math.pow(R(), 0.8) * h * 0.95, spread = 0.25 + 0.75 * (h - y) / h;
        const x = w / 2 + (R() - 0.5) * w * 0.55 * spread, r = w * (0.08 + R() * 0.16) * (0.6 + spread); const a = 0.85 * (0.4 + 0.6 * y / h);
        const grd = g.createRadialGradient(x, y, 0, x, y, r); grd.addColorStop(0, `rgba(10,9,8,${a})`); grd.addColorStop(1, 'rgba(10,9,8,0)'); g.fillStyle = grd; g.fillRect(0, 0, w, h); } });
    const plumeM = new THREE.MeshStandardMaterial({ map: plumeT, transparent: true, depthWrite: false, roughness: 1 });
    for (const [x, y, w, h] of [[0, 6.2, 9, 7.5], [-2.45, 6.6, 3.2, 4.2], [2.45, 6.8, 3.0, 4.0]]) { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), plumeM); m.position.set(x, y, 0.025); m.renderOrder = 2; scene.add(m); }
    // entrance: canopy + void where the glass hall was
    const canopy = add(new THREE.BoxGeometry(8, 0.35, 3.2), std({ map: sootTex(512, 256, [[256, 256, 300, 250]], '#77736b'), roughness: 0.95 }), 0, 3.4, 1.4);
    for (const x of [-3.6, 3.6]) add(new THREE.BoxGeometry(0.35, 3.25, 0.35), std({ map: sootTex(128, 256, [[64, 256, 80, 200]], '#77736b') }), x, 1.62, 2.8);
    const hall = add(new THREE.BoxGeometry(7, 3.2, 6), std({ color: 0x050505, roughness: 1, side: THREE.BackSide }), 0, 1.6, -3.0);
    const hallFloor = add(new THREE.PlaneGeometry(7, 6), ash, 0, 0.01, -3.0, -Math.PI / 2);
    // door frames, twisted, glass shards
    const frameM = std({ color: 0x1d1b19, metalness: 0.5, roughness: 0.6 });
    for (let i = 0; i <= 4; i++) { const m = add(new THREE.BoxGeometry(0.08, 3.0, 0.1), frameM, -3.2 + i * 1.6, 1.5, 0.05, 0, 0, (R() - 0.5) * 0.12); }
    add(new THREE.BoxGeometry(6.6, 0.1, 0.12), frameM, 0, 3.0, 0.05, 0, 0, 0.02);
    const glassM = new THREE.MeshPhysicalMaterial({ color: 0xbfc6c8, roughness: 0.1, transparent: true, opacity: 0.35, side: THREE.DoubleSide });
    for (let i = 0; i < 60; i++) { const s = 0.05 + R() * 0.2; const m = add(new THREE.CircleGeometry(s, 3), glassM, (R() - 0.5) * 7, 0.012, 0.5 + R() * 3.5, -Math.PI / 2, 0, R() * 6); }
    // debris: charred chairs, a melted bin, a fallen sign
    for (let i = 0; i < 9; i++) add(new THREE.BoxGeometry(0.3 + R() * 0.6, 0.06 + R() * 0.2, 0.3 + R() * 0.6), charred, (R() - 0.5) * 6, 0.08, -0.5 - R() * 4, 0, R() * 3, (R() - 0.5) * 0.4);
    const bin = add(new THREE.CylinderGeometry(0.32, 0.4, 0.55, 14), charred, 2.4, 0.27, 2.2, 0.15, 0, 0.25);
    const sign = ctex(THREE, 1024, 160, (g, w, h) => { g.fillStyle = '#d8d2c4'; g.font = '700 110px Inter, sans-serif'; g.textBaseline = 'middle'; spacedText(g, 'LYCÉE', 40, h / 2, 40);
      const grd = g.createLinearGradient(0, 0, w, 0); grd.addColorStop(0.3, 'rgba(10,9,8,0)'); grd.addColorStop(0.75, 'rgba(10,9,8,0.9)'); g.globalCompositeOperation = 'source-atop'; g.fillStyle = grd; g.fillRect(0, 0, w, h); });
    const signM = add(new THREE.PlaneGeometry(4.2, 0.65), new THREE.MeshStandardMaterial({ map: sign, transparent: true, roughness: 0.6 }), -0.2, 4.25, 3.02);
    // smoke from the hall + embers inside
    ctx.smoke = smoke(new THREE.Vector3(0, 2.6, 1.2), 60, 2.6, 9, 0x8f8a84, 0.22);
    ctx.emb = embers(new THREE.Vector3(0, 0.05, -3), 140, [6, 0.4, 5]);
    const ember = new THREE.PointLight(AMBER, 6, 8, 1.6); ember.position.set(0, 0.6, -2.5); scene.add(ember); ctx.ember = ember;
    // amber beat: the embers deep in the gutted hall flare up, light spilling out over the ash and the tape
    ctx.hallGlow = [[-1.6, 0.4, -4.5, 2.2], [1.2, 0.3, -3.6, 1.8], [0.0, 0.7, -5.6, 3.0]].map(([x, y, z, sz]) => { const g = glow(THREE, AMBER, sz, 1); g.position.set(x, y, z); g.material.opacity = 0; scene.add(g); return g; });
    ctx.spill = new THREE.SpotLight(0xff9a40, 0, 16, 0.7, 0.8, 1.2); ctx.spill.position.set(0, 1.2, -4.5); ctx.spill.target.position.set(0, 0, 4); scene.add(ctx.spill, ctx.spill.target);
    // tape across the doorway (cream tape, no text)
    const tapeM = std({ color: 0xd9c38a, roughness: 0.6 });
    add(new THREE.BoxGeometry(7.6, 0.08, 0.01), tapeM, 0, 1.1, 2.9, 0, 0, 0.03); add(new THREE.BoxGeometry(7.6, 0.08, 0.01), tapeM, 0, 0.7, 2.95, 0, 0, -0.02);
    // dawn light: cold sky + low warm sun grazing from the left
    scene.add(new THREE.HemisphereLight(0xa9b4c6, 0x3a342e, 2.1));
    const sun = new THREE.DirectionalLight(0xffc89a, 4.2); sun.position.set(-30, 8, 18); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
    Object.assign(sun.shadow.camera, { left: -20, right: 20, top: 15, bottom: -5 }); sun.shadow.bias = -0.0005; scene.add(sun);
  } else if (shot === 'marseille') {
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(120, 80), std({ map: ctex(THREE, 512, 512, (g, w, h) => { g.fillStyle = '#353536'; g.fillRect(0, 0, w, h); for (let i = 0; i < 26000; i++) { const v = 30 + R() * 60; g.fillStyle = `rgba(${v},${v},${v},0.3)`; g.fillRect(R() * w, R() * h, 2, 2); } }, { repeat: [24, 16] }), roughness: 0.6, metalness: 0.2 }));
    ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
    const scorch = new THREE.Mesh(new THREE.CircleGeometry(4.5, 48), new THREE.MeshStandardMaterial({ map: ctex(THREE, 256, 256, (g) => { const grd = g.createRadialGradient(128, 128, 10, 128, 128, 128); grd.addColorStop(0, 'rgba(6,5,5,0.95)'); grd.addColorStop(1, 'rgba(6,5,5,0)'); g.fillStyle = grd; g.fillRect(0, 0, 256, 256); }), transparent: true, depthWrite: false }));
    scorch.rotation.x = -Math.PI / 2; scorch.position.set(0, 0.006, 0); scorch.scale.set(1.6, 1, 1); scene.add(scorch);
    // burned-out truck (generic: cab + box body + ladder frame), all charred, tyres burned off
    const truck = new THREE.Group(); truck.rotation.y = 0.18; scene.add(truck);
    const rust = std({ color: 0x3a2a22, roughness: 0.95, metalness: 0.2 }); const burnt = std({ map: sootTex(512, 256, [[200, 256, 300, 260], [420, 256, 200, 200]], '#4a2e26'), roughness: 0.95, metalness: 0.2 });
    add(new RoundedBoxGeometry(2.3, 2.4, 2.4, 3, 0.08), burnt, 3.0, 1.75, 0, 0, 0, 0, truck);        // cab
    add(new THREE.BoxGeometry(5.2, 2.0, 2.4), burnt, -0.9, 1.55, 0, 0, 0, 0, truck);                 // body
    add(new THREE.BoxGeometry(2.2, 0.9, 2.36), std({ color: 0x050505, side: THREE.DoubleSide }), 3.05, 2.3, 0.02, 0, 0, 0, truck); // empty windscreen hole
    for (let i = 0; i < 9; i++) add(new THREE.BoxGeometry(0.06, 0.06, 1.6), rust, -3.0 + i * 0.6, 2.75, 0, 0, 0, 0, truck);
    for (const z of [-1.21, 1.21]) { for (let i = 0; i < 4; i++) add(new THREE.BoxGeometry(1.15, 1.5, 0.02), std({ color: 0x1a1412, roughness: 0.9, metalness: 0.4 }), -2.85 + i * 1.3, 1.5, z, 0, 0, 0, truck);
      add(new THREE.BoxGeometry(1.0, 0.75, 0.02), std({ color: 0x030303 }), 3.05, 2.3, z * 1.0, 0, 0, 0, truck); }
    for (const z of [-0.8, 0.8]) add(new THREE.BoxGeometry(5.6, 0.07, 0.07), rust, -0.7, 2.75, z, 0, 0, 0.05, truck);
    for (const x of [-2.6, -0.4, 3.0]) for (const z of [-1.15, 1.15]) add(new THREE.TorusGeometry(0.42, 0.06, 8, 20), rust, x, 0.48, z, 0, 0, 0, truck);   // bare rims
    add(new THREE.BoxGeometry(7.6, 0.35, 2.0), rust, 0.0, 0.62, 0, 0, 0, 0, truck);
    truck.traverse(o => { if (o.isMesh) o.position.y -= 0.12; });
    // street: buildings with balconies, a bus shelter with LED display
    const fac = (seedC) => ctex(THREE, 512, 512, (g, w, h) => { g.fillStyle = '#b9ab92'; g.fillRect(0, 0, w, h); for (let i = 0; i < 6000; i++) { const v = 150 + R() * 60; g.fillStyle = `rgba(${v},${v - 10},${v - 30},0.12)`; g.fillRect(R() * w, R() * h, 3, 3); }
      for (let y = 0; y < 4; y++) for (let x = 0; x < 4; x++) { g.fillStyle = R() < 0.12 ? '#c79a5a' : '#2a2a2c'; g.fillRect(x * 128 + 34, y * 128 + 20, 60, 92); g.fillStyle = '#5a5248'; g.fillRect(x * 128 + 26, y * 128 + 110, 76, 8); } }, { repeat: [2, 2] });
    for (let i = 0; i < 6; i++) add(new THREE.BoxGeometry(9, 16 + R() * 6, 6), std({ map: fac(i), roughness: 0.9 }), -24 + i * 9.4, 9, -12);
    const shelter = new THREE.Group(); shelter.position.set(-7.4, 0, 3.0); shelter.rotation.y = 0.5; scene.add(shelter);
    add(new THREE.BoxGeometry(3.2, 0.08, 1.4), std({ color: 0x3a3c3e, metalness: 0.5 }), 0, 2.5, 0, 0, 0, 0, shelter);
    for (const x of [-1.55, 1.55]) add(new THREE.BoxGeometry(0.08, 2.5, 0.08), std({ color: 0x3a3c3e, metalness: 0.5 }), x, 1.25, -0.6, 0, 0, 0, shelter);
    add(new THREE.BoxGeometry(3.1, 2.0, 0.03), new THREE.MeshPhysicalMaterial({ color: 0xc9d0d4, transparent: true, opacity: 0.18, roughness: 0.1 }), 0, 1.3, -0.62, 0, 0, 0, shelter);
    const ledT = ctex(THREE, 1024, 192, (g, w, h) => { g.fillStyle = '#060504'; g.fillRect(0, 0, w, h); g.fillStyle = '#ffb25c'; g.font = '700 76px "DejaVu Sans Mono", monospace'; g.textBaseline = 'middle';
      g.fillText('NETWORK SUSPENDED', 30, h / 2); g.fillStyle = 'rgba(0,0,0,0.5)'; for (let x = 0; x < w; x += 6) g.fillRect(x, 0, 2, h); for (let y = 0; y < h; y += 6) g.fillRect(0, y, w, 2); });
    const led = add(new THREE.PlaneGeometry(1.9, 0.36), new THREE.MeshBasicMaterial({ map: ledT, toneMapped: false }), 0, 2.2, 0.0, 0, 0, 0, shelter); led.castShadow = false;
    add(new THREE.BoxGeometry(2.0, 0.44, 0.08), std({ color: 0x2a2b2d, metalness: 0.4 }), 0, 2.2, -0.05, 0, 0, 0, shelter);
    const ledGlow = glow(THREE, AMBER, 2.6, 0.5); ledGlow.position.set(0, 2.2, 0.15); shelter.add(ledGlow);
    ctx.smoke = smoke(new THREE.Vector3(0.3, 3, -0.3), 70, 2.0, 16, 0x6f6b66, 0.3);
    ctx.emb = embers(new THREE.Vector3(0, 0.3, 0), 60, [6, 1.4, 2.2]);
    const ember = new THREE.PointLight(AMBER, 5, 6, 1.6); ember.position.set(-0.5, 1.2, 0); scene.add(ember); ctx.ember = ember;
    scene.add(new THREE.HemisphereLight(0x9a9db0, 0x3a322c, 1.3));
    const dusk = new THREE.DirectionalLight(0xffa86a, 2.6); dusk.position.set(25, 10, -10); dusk.castShadow = true; dusk.shadow.mapSize.set(2048, 2048); Object.assign(dusk.shadow.camera, { left: -15, right: 15, top: 10, bottom: -5 }); scene.add(dusk);
    const lamp = new THREE.SpotLight(0xff9a3a, 160, 24, 0.8, 0.6, 1.3); lamp.position.set(4, 7, 6); lamp.target.position.set(1, 0, 0); scene.add(lamp, lamp.target);
  } else {
    // classroom interior, ransacked
    const room = new THREE.Group(); scene.add(room);
    const wallT = sootTex(1024, 512, [[700, 512, 420, 500]], '#a39c8d', null);
    const fl = add(new THREE.PlaneGeometry(10, 8), std({ map: ctex(THREE, 512, 512, (g, w, h) => { for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { const v = (x + y) % 2 ? 104 : 88; g.fillStyle = `rgb(${v},${v - 4},${v - 14})`; g.fillRect(x * 64, y * 64, 64, 64); } }, { repeat: [3, 2] }), roughness: 0.5 }), 0, 0, 0, -Math.PI / 2);
    add(new THREE.PlaneGeometry(10, 3.2), std({ map: wallT, roughness: 0.95 }), 0, 1.6, -4);
    const lw = add(new THREE.PlaneGeometry(8, 3.2), std({ map: sootTex(1024, 512, [[300, 512, 300, 400]], '#a39c8d'), roughness: 0.95 }), -5, 1.6, 0, 0, Math.PI / 2, 0);
    add(new THREE.PlaneGeometry(10, 8), std({ map: sootTex(512, 512, [[300, 300, 400, 300]], '#8f8a80') }), 0, 3.2, 0, Math.PI / 2);
    // window wall (right) with a broken pane letting cold light in
    for (const [y, h] of [[0.5, 1.0], [2.9, 0.6]]) add(new THREE.PlaneGeometry(8, h), std({ color: 0x9a9488 }), 5, y, 0, 0, -Math.PI / 2, 0);
    for (let i = 0; i <= 5; i++) add(new THREE.BoxGeometry(0.08, 1.6, 0.08), std({ color: 0x55585a, metalness: 0.6 }), 4.98, 1.8, -4 + i * 1.6);
    const pane = ctex(THREE, 512, 512, (g, w, h) => { g.fillStyle = 'rgba(190,200,205,0.18)'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(245,245,240,0.85)'; g.lineWidth = 2;
      for (let k2 = 0; k2 < 14; k2++) { let x = 260, y = 240, a = k2 / 14 * 6.28; g.beginPath(); g.moveTo(x, y); for (let s = 0; s < 9; s++) { a += (R() - 0.5) * 0.5; x += Math.cos(a) * 28; y += Math.sin(a) * 28; g.lineTo(x, y); } g.stroke(); }
      g.globalCompositeOperation = 'destination-out'; g.beginPath(); g.ellipse(260, 240, 110, 90, 0.4, 0, 7); g.fill(); });
    for (let i = 0; i < 5; i++) add(new THREE.PlaneGeometry(1.5, 1.55), new THREE.MeshStandardMaterial({ map: i === 2 ? pane : null, color: 0xbfc8cc, transparent: true, opacity: i === 2 ? 1 : 0.22, roughness: 0.1, side: THREE.DoubleSide, depthWrite: false }), 4.97, 1.8, -3.2 + i * 1.6, 0, -Math.PI / 2, 0);
    // overturned desks + chairs, papers, a blackened board
    const deskTop = std({ color: 0x8a6c4c, roughness: 0.6 }), metal = std({ color: 0x55585a, metalness: 0.6, roughness: 0.45 }), chairM = std({ color: 0x3f4a52 });
    const desk = (x, z, rx, ry, rz, y = 0.4) => { const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.set(rx, ry, rz); scene.add(g); add(new THREE.BoxGeometry(1.3, 0.03, 0.5), deskTop, 0, 0.36, 0, 0, 0, 0, g); for (const sx of [-0.6, 0.6]) for (const sz of [-0.21, 0.21]) add(new THREE.BoxGeometry(0.03, 0.72, 0.03), metal, sx, 0, sz, 0, 0, 0, g); };
    desk(-1.5, -1.0, Math.PI / 2, 0.3, 0, 0.25); desk(0.6, -2.2, 0, 0.5, Math.PI, 0.76); desk(1.8, 0.4, 0.2, -0.4, 1.4, 0.4); desk(-0.4, 1.2, 0, 0.1, 0, 0.36); desk(-2.8, 1.8, Math.PI / 2, 1.2, 0.2, 0.25); desk(2.6, -1.4, 0.1, 1.0, 0, 0.36);
    for (let i = 0; i < 8; i++) { const g = new THREE.Group(); g.position.set((R() - 0.5) * 7, 0.2, (R() - 0.5) * 6); g.rotation.set((R() - 0.5) * 3, R() * 6, (R() - 0.5) * 3); scene.add(g); add(new THREE.BoxGeometry(0.4, 0.03, 0.4), chairM, 0, 0, 0, 0, 0, 0, g); add(new THREE.BoxGeometry(0.4, 0.35, 0.03), chairM, 0, 0.18, -0.2, 0, 0, 0, g); }
    for (let i = 0; i < 70; i++) add(new THREE.PlaneGeometry(0.21, 0.3), std({ color: R() < 0.3 ? 0x6a655c : 0xe8e2d4, side: THREE.DoubleSide }), (R() - 0.5) * 8, 0.004 + R() * 0.01, (R() - 0.5) * 7, -Math.PI / 2, 0, R() * 6);
    add(new THREE.PlaneGeometry(3.6, 1.2), charred, -4.97, 1.6, -0.5, 0, Math.PI / 2, 0);
    for (let i = 0; i < 40; i++) add(new THREE.CircleGeometry(0.03 + R() * 0.12, 3), new THREE.MeshPhysicalMaterial({ color: 0xbfc6c8, transparent: true, opacity: 0.4, side: THREE.DoubleSide }), 3.5 + R() * 1.4, 0.01, -0.5 + (R() - 0.5) * 2.5, -Math.PI / 2, 0, R() * 6);
    ctx.smoke = smoke(new THREE.Vector3(0, 2.4, -2), 18, 4, 1.2, 0x8a8680, 0.18);
    ctx.emb = embers(new THREE.Vector3(-4.6, 0.05, -2.8), 30, [0.6, 0.15, 1.2]);
    const ember = new THREE.PointLight(AMBER, 5, 5, 1.6); ember.position.set(-4.2, 0.5, -2.6); scene.add(ember); ctx.ember = ember;
    scene.add(new THREE.HemisphereLight(0x8a96a8, 0x1a1816, 1.0));
    const day = new THREE.SpotLight(0xc9d6e6, 160, 20, 0.6, 0.6, 1.2); day.position.set(9, 2.3, -0.2); day.target.position.set(-1, 0, 0); day.castShadow = false; scene.add(day, day.target); const fire = new THREE.PointLight(AMBER, 14, 7, 1.5); fire.position.set(-3.8, 1.0, -2.0); scene.add(fire);
    const shaft = beam(THREE, 0xdfe8f2, 9, 1.4, 0.05); shaft.position.set(5.2, 2.2, -0.2); shaft.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), new THREE.Vector3(-6.2, -2.2, 0.2).normalize()); scene.add(shaft);
  }
  ctx.smokeOp = 1;
  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.6, bloomRadius: 0.55, bloomThreshold: 0.75,
    dof: { focus: { nantes: 12, marseille: 11, ransacked: 5 }[shot], aperture: 0.0007, maxblur: 0.004 } });
  return Object.assign(ctx, post);
}

const CAMS = {
  nantes: [[0, [-6.5, 2.2, 17, 0, 2.6, 0]], [8, [-3.6, 1.9, 11.5, 0, 2.0, -0.5]]],
  marseille: [[0, [-6.0, 1.4, 11.5, -1.5, 1.8, 0]], [8, [-2.6, 1.45, 11.8, 0.2, 1.9, 0]]],
  ransacked: [[0, [-3.8, 1.6, 3.6, 0.6, 0.9, -1.6]], [7, [-2.6, 1.55, 3.4, 0.9, 0.85, -1.8]]],
};

export function update(ctx, tt) {
  const { camera, shot } = ctx;
  const t = tt / ctx.k;
  const c = path(CAMS[shot] ?? CAMS.nantes)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  for (const s of ctx.smoke) { const u = s.userData; const p = ((t * 0.06 + u.ph) % 1);
    s.position.set(u.o.x + (u.dx + Math.sin(p * 6 + u.ph * 9) * 0.3) * u.sp * p + p * 1.5, u.o.y + p * u.rise, u.o.z + Math.cos(u.ph * 20) * u.sp * 0.4 * p);
    const sc = (1.2 + p * 5) * (shot === 'ransacked' ? 0.8 : 1); s.scale.set(sc, sc, 1); s.material.rotation = u.rot * t;
    s.material.opacity = u.op * Math.sin(p * Math.PI) * (shot === 'nantes' ? 0.8 : 1); }
  const a = ctx.emb.geometry.attributes.position; ctx.emb.material.opacity = 0.55 + 0.45 * Math.sin(t * 7) * Math.sin(t * 3.3);
  const fl = 0.75 + 0.25 * Math.sin(t * 9) * Math.sin(t * 4.1);
  ctx.ember.intensity = (shot === 'ransacked' ? 4 : 6) * fl;
  if (shot === 'nantes') { const on = sstep(2.0, 4.5, t); ctx.ember.intensity = (6 + 34 * on) * fl; ctx.spill.intensity = 60 * on * fl;
    ctx.hallGlow.forEach((g, i) => { g.material.opacity = on * (0.4 + 0.2 * Math.sin(t * (5 + i) + i)); }); }
}

// Ghost station watch: East German border guards in a sealed East Berlin U-Bahn station,
// West Berlin trains rolling through without stopping. All shots share one station.
// shots (?shot=):
//   guardroom (14.8 s) - dark platform, two guards in the gloom; push in to a narrow slit in the tiled wall
//                        where two pairs of eyes catch the light; cut inside the locked guard room: two guards
//                        side by side peering out, the slit's light striping their faces, duty roster on the wall;
//                        8.0 s the door behind them opens, an inspecting officer backlit in the doorway;
//                        12.5 s pull back through an observation window: a civilian watcher in the dark next door.
//   boots     (8.2 s)  - low behind a guard's boots and grounded rifle, rising over his shoulder while a lit
//                        West Berlin train rolls in slowly out of the tunnel, headlight throwing his shadow.
//   windows   (13.6 s) - guard POV: the train slides past at walking pace an arm's length away; inside, warm-lit
//                        West Berliners: a man reading DER ABEND (~3.6 s), a man asleep against the glass (~5 s),
//                        a man staring straight back (~6.6 s, his head follows us); ~9.2 s a door handle passes
//                        within reach, the guard's gloved hand rises, twitches, clenches.
//   eachother (3.6 s)  - two guards on the platform, the near one glances sideways at the other; the train's
//                        tail lights shrink into the tunnel.
//   nostop    (8.2 s)  - camera on the platform edge: headlight floods the station from behind, a train tears
//                        past (window streaks), guard in the background; tail lights recede, bulbs sag, dark again.
import { AMBER, tileTex, concreteTex, textTex, canvasTex, rng, lerp } from './lib.js';
import { makeComposer, glow, beam, normalFromHeight, borderGuard, smooth, flicker } from './look.js';

const HW = 8, HT = 5.4, L = 120, TL = -2.75;
const CAR = 15.5, GAP = 0.6, CW = 2.66, FL = 1.05, NC = 3;
const TRAIN_LEN = NC * CAR + (NC - 1) * GAP;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const seg = (t, a, b) => smooth((t - a) / (b - a));

export async function setup(THREE, renderer, W, H) {
  const raw = (new URLSearchParams(location.search).get('shot') || 'guardroom').split('|');
  const shot = raw[0];
  if (raw[1]) { const v = raw[1].split(',').map(Number); window.DBG = { p: v.slice(0, 3), l: v.slice(3, 6) }; }   // debug camera
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020202);
  scene.fog = new THREE.FogExp2(0x060504, shot === 'guardroom' ? 0.035 : 0.03);
  const camera = new THREE.PerspectiveCamera(40, W / H, 0.03, 400);
  scene.add(camera);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.8, metalness: 0, ...o });
  const { RoundedBoxGeometry } = await import('three/addons/geometries/RoundedBoxGeometry.js');
  const box = (w, h, d, mat, x, y, z, parent = scene) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.position.set(x, y, z); parent.add(m); return m; };
  // capsule between two points
  const Y = new THREE.Vector3(0, 1, 0);
  const limb = (a, b, r, mat, parent) => {
    const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), d = B.clone().sub(A), len = d.length();
    const m = new THREE.Mesh(new THREE.CapsuleGeometry(r, Math.max(0.001, len), 4, 10), mat);
    m.position.copy(A).addScaledVector(d, 0.5); m.quaternion.setFromUnitVectors(Y, d.normalize()); parent.add(m); return m;
  };

  // ======================= STATION =======================
  const tileN = normalFromHeight(THREE, 256, 256, (g, w, h) => {
    g.fillStyle = '#000'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff';
    for (let y = 0; y < h; y += 32) for (let x = 0; x < w; x += 64) g.fillRect(x + 2, y + 2, 60, 28);
  }, 3, [1, 1]);
  const wallMat = std({ map: tileTex(THREE, { repeat: [1, 1], tile: 32 }), normalMap: tileN, roughness: 0.35 });
  // wall piece on the plane x = side*HW, tiles laid out in world units (4 m x 1.8 m per texture)
  const wallPiece = (side, z0, z1, y0, y1, mat = wallMat) => {
    const g = new THREE.PlaneGeometry(z1 - z0, y1 - y0);
    const m = new THREE.Mesh(g, mat); m.position.set(side * HW * 0.99999, (y0 + y1) / 2, (z0 + z1) / 2); m.rotation.y = -side * Math.PI / 2;
    scene.add(m); m.updateMatrixWorld();
    const p = g.attributes.position, uv = g.attributes.uv, v = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i).applyMatrix4(m.matrixWorld); uv.setXY(i, v.z / 4, v.y / 1.8); }
    m.receiveShadow = true; return m;
  };
  const SL = { z0: -0.75, z1: 0.75, y0: 2.63, y1: 2.78 };  // the guard room slit
  wallPiece(1, -L / 2, L / 2, 0, HT);
  wallPiece(-1, -L / 2, SL.z0, 0, HT); wallPiece(-1, SL.z1, L / 2, 0, HT);
  wallPiece(-1, SL.z0, SL.z1, 0, SL.y0); wallPiece(-1, SL.z0, SL.z1, SL.y1, HT);

  const floorRough = (() => { const r = rng(5); const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
    g.fillStyle = '#bbb'; g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 60; i++) { g.fillStyle = `rgba(60,60,60,${0.15 + r() * 0.2})`; g.beginPath(); g.ellipse(r() * 256, r() * 256, 8 + r() * 40, 4 + r() * 20, r() * 3, 0, 7); g.fill(); }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(2, 20); return t; })();
  for (const sx of [-1, 1]) {
    const p = new THREE.Mesh(new THREE.BoxGeometry(3.6, 1, L), std({ map: concreteTex(THREE, [2, 30], 5 + sx, 105), roughnessMap: floorRough, roughness: 0.55 }));
    p.position.set(sx * (HW - 1.8), 0.5, 0); p.receiveShadow = true; scene.add(p);
    const edge = box(0.3, 0.02, L, std({ color: 0xd2cdbf, roughness: 0.5 }), sx * (HW - 3.75), 1.011, 0); edge.receiveShadow = true;
  }
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(HW * 2, L), std({ map: concreteTex(THREE, [3, 20], 11, 60) }));
  ceil.rotation.x = Math.PI / 2; ceil.position.y = HT; scene.add(ceil);
  const bed = new THREE.Mesh(new THREE.PlaneGeometry(HW * 2, L + 400), std({ map: concreteTex(THREE, [4, 120], 9, 45) }));
  bed.rotation.x = -Math.PI / 2; scene.add(bed);
  const railM = std({ color: 0xa0a0a0, metalness: 1, roughness: 0.25 });
  for (const tx of [TL, -TL]) for (const o of [-0.72, 0.72]) box(0.07, 0.14, L + 400, railM, tx + o, 0.22, 0);
  const sl = new THREE.InstancedMesh(new THREE.BoxGeometry(2.4, 0.14, 0.25), std({ color: 0x1c1b19 }), 1000);
  { const m4 = new THREE.Matrix4(); let k = 0; for (const tx of [TL, -TL]) for (let i = 0; i < 500; i++) { m4.makeTranslation(tx, 0.08, -260 + i * 1.04); sl.setMatrixAt(k++, m4); } }
  scene.add(sl);
  const tun = std({ map: concreteTex(THREE, [60, 2], 31, 55), roughness: 0.95 });
  for (const zc of [-L / 2 - 150, L / 2 + 150]) {
    for (const sx of [-1, 1]) { const w = new THREE.Mesh(new THREE.PlaneGeometry(300, HT), tun); w.position.set(sx * 4.6, HT / 2, zc); w.rotation.y = -sx * Math.PI / 2; scene.add(w); }
    const c = new THREE.Mesh(new THREE.PlaneGeometry(9.2, 300), tun); c.rotation.x = Math.PI / 2; c.position.set(0, HT, zc); scene.add(c);
    for (const sx of [-1, 1]) { const e = new THREE.Mesh(new THREE.PlaneGeometry(HW - 4.6, HT), tun); e.position.set(sx * (4.6 + (HW - 4.6) / 2), HT / 2, Math.sign(zc) * L / 2); e.rotation.y = zc < 0 ? 0 : Math.PI; scene.add(e); }
  }
  const steel = std({ color: 0x2e2e2d, metalness: 0.7, roughness: 0.45 });
  for (let z = -L / 2 + 4; z < L / 2; z += 6.5) {
    box(0.3, HT, 0.3, steel, 0, HT / 2, z); box(HW * 2, 0.32, 0.26, steel, 0, HT - 0.16, z);
  }
  const sign = std({ map: textTex(THREE, 'ROSENTHALER PLATZ'), roughness: 0.6 });
  for (const [sx, z] of [[-1, -30], [-1, 30], [-1, -16], [1, -30], [1, 0], [1, 30]]) {
    const b = new THREE.Mesh(new THREE.PlaneGeometry(4.2, 0.66), sign); b.position.set(sx * (HW - 0.02), 3.3, z); b.rotation.y = -sx * Math.PI / 2; scene.add(b);
  }
  // faded posters
  const posterTex = (seed) => { const r = rng(seed); return canvasTex(THREE, 256, 352, (g, w, h) => {
    const v = 150 + r() * 40; g.fillStyle = `rgb(${v},${v - 4},${v - 12})`; g.fillRect(0, 0, w, h);
    g.fillStyle = `rgba(40,38,34,${0.5 + r() * 0.3})`; g.fillRect(20, 30, w - 40, 120 + r() * 60);
    g.font = 'bold 34px "DejaVu Serif", serif'; g.textAlign = 'center';
    g.fillText(['BERLIN', 'KINO', 'SEIFE', 'TABAK'][Math.floor(r() * 4)], w / 2, h - 110);
    g.font = '18px "DejaVu Serif", serif'; g.fillText('1961', w / 2, h - 70);
    for (let i = 0; i < 400; i++) { g.fillStyle = `rgba(90,85,78,${r() * 0.25})`; g.fillRect(r() * w, r() * h, 2 + r() * 8, 1 + r() * 3); }
    g.fillStyle = 'rgba(30,28,25,0.25)'; g.fillRect(0, h * (0.5 + r() * 0.4), w, h);
  }); };
  for (const [sx, z] of [[-1, -24], [-1, -9], [-1, 12], [-1, 22], [1, -20], [1, 12], [1, -40], [-1, 38]]) {
    const pm = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.9), std({ map: posterTex(z * 7 + sx * 3 + 50), roughness: 0.9 }));
    pm.position.set(sx * (HW - 0.03), 2.5, z); pm.rotation.y = -sx * Math.PI / 2; scene.add(pm);
  }
  // steel service door to the guard post, painted sign
  const doorTex = canvasTex(THREE, 128, 256, (g, w, h) => {
    g.fillStyle = '#5a5c58'; g.fillRect(0, 0, w, h); const r = rng(77);
    for (let i = 0; i < 300; i++) { g.fillStyle = `rgba(30,30,28,${r() * 0.3})`; g.fillRect(r() * w, r() * h, 1 + r() * 5, 1 + r() * 9); }
    g.strokeStyle = 'rgba(20,20,20,0.6)'; g.lineWidth = 3; g.strokeRect(10, 10, w - 20, h - 20);
    g.fillStyle = '#d9d4c6'; g.fillRect(18, 70, w - 36, 30); g.fillStyle = '#1a1a1a'; g.font = 'bold 15px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.fillText('KEIN ZUTRITT', w / 2, 91);
  });
  const sdoor = new THREE.Mesh(new THREE.PlaneGeometry(0.95, 2.05), std({ map: doorTex, roughness: 0.5, metalness: 0.4 }));
  sdoor.position.set(-HW + 0.02, 2.025, -3.0); sdoor.rotation.y = Math.PI / 2; scene.add(sdoor);
  box(0.04, 0.04, 0.14, railM, -HW + 0.06, 2.0, -2.65);

  // ---- lamps (bulb + shade + glow + beam), a pool of point lights assigned per shot
  scene.add(new THREE.HemisphereLight(0x7c8696, 0x090807, 0.1));
  const bulbMat = new THREE.MeshBasicMaterial({ color: 0xffd6a0 });
  const lamps = []; let li = 0;
  for (let z = -54; z <= 54; z += 12) for (const sx of [-1, 1]) {
    const x = sx * (HW - 2.0), y = HT - 0.55;
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.07, 12, 8), bulbMat.clone()); b.position.set(x, y, z); scene.add(b);
    const shade = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.18, 20, 1, true), std({ color: 0x222222, side: THREE.DoubleSide })); shade.position.set(x, y + 0.1, z); scene.add(shade);
    box(0.016, 0.45, 0.016, steel, x, HT - 0.22, z);
    const h = glow(THREE, AMBER, 1.6, 0.9); h.position.set(x, y - 0.02, z); scene.add(h);
    const bm = beam(THREE, AMBER, 4.2, 1.5, 0.05); bm.position.set(x, y, z); scene.add(bm);
    lamps.push({ bulb: b, halo: h, beam: bm, light: null, x, y, z, sx, seed: li++ });
  }
  const focus = { teaser: [-6, 0], guardroom: [-6, 0], boots: [-6, -26], windows: [-6, -20], eachother: [-6, 26], nostop: [-6, -10] }[shot] || [-6, 0];
  const nLamp = shot === 'guardroom' ? 4 : shot === 'windows' ? 5 : 6;
  [...lamps].sort((a, b) => Math.hypot(a.x - focus[0], a.z - focus[1]) - Math.hypot(b.x - focus[0], b.z - focus[1])).slice(0, nLamp).forEach(l => {
    l.light = new THREE.PointLight(AMBER, 0, 11, 1.7); l.light.position.set(l.x, l.y - 0.1, l.z); scene.add(l.light);
  });

  // dust
  const N = 1400, r0 = rng(17), pos = new Float32Array(N * 3), seeds = new Float32Array(N);
  for (let i = 0; i < N; i++) { pos[i * 3] = -HW + r0() * HW * 2; pos[i * 3 + 1] = 0.8 + r0() * 4.4; pos[i * 3 + 2] = focus[1] - 30 + r0() * 60; seeds[i] = r0() * 100; }
  const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const dotT = (() => { const c = document.createElement('canvas'); c.width = c.height = 32; const g = c.getContext('2d'); const gr = g.createRadialGradient(16, 16, 0, 16, 16, 16); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 32, 32); return new THREE.CanvasTexture(c); })();
  const dust = new THREE.Points(dg, new THREE.PointsMaterial({ size: 0.035, map: dotT, color: 0xffcf9a, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false }));
  scene.add(dust);
  const dustBase = pos.slice();

  // ======================= PEOPLE =======================
  const M = {
    coat: std({ color: 0x3b3e38, roughness: 0.92 }), belt: std({ color: 0x0e0d0c, roughness: 0.5 }),
    boot: std({ color: 0x080808, roughness: 0.28, metalness: 0.2 }), skin: std({ color: 0x6a5c54, roughness: 0.72 }),
    visor: std({ color: 0x050505, roughness: 0.2, metalness: 0.3 }), glove: std({ color: 0x121110, roughness: 0.55 }),
    gun: std({ color: 0x1a1a1a, roughness: 0.4, metalness: 0.6 }), wood: std({ color: 0x5e3318, roughness: 0.55 }),
    eyeW: new THREE.MeshStandardMaterial({ color: 0x0c0a09, roughness: 0.08, metalness: 0.0 }), dark: std({ color: 0x0a0807, roughness: 0.6 }),
  };
  // sculpted head: a sphere pushed into a face (brow, sockets, nose, cheekbones, jaw, chin), face toward +z
  const skullGeo = (() => {
    const g = new THREE.SphereGeometry(0.1, 48, 36), p = g.attributes.position, v = new THREE.Vector3();
    const G = (x, y, cx, cy, sx, sy) => Math.exp(-((x - cx) ** 2) / (2 * sx * sx) - ((y - cy) ** 2) / (2 * sy * sy));
    for (let i = 0; i < p.count; i++) {
      v.fromBufferAttribute(p, i);
      let { x, y, z } = v; y *= 1.13; x *= 0.9;
      const jaw = smooth((-y - 0.015) / 0.09); x *= 1 - 0.28 * jaw; if (z < 0) z *= 1 - 0.25 * jaw; else z *= 1 - 0.06 * jaw;
      if (z < 0) { z *= 1.06; }
      const f = smooth(z / 0.06);                     // front mask
      let d = 0;
      d += 0.007 * G(x, y, 0, 0.05, 0.055, 0.012);                                   // brow ridge
      d -= 0.009 * (G(x, y, 0.034, 0.024, 0.015, 0.011) + G(x, y, -0.034, 0.024, 0.015, 0.011)); // eye sockets
      d += 0.026 * G(x, y, 0, -0.012, 0.009, 0.014) + 0.012 * G(x, y, 0, 0.018, 0.006, 0.02); // nose tip + bridge
      d += 0.006 * (G(x, y, 0.05, -0.005, 0.016, 0.014) + G(x, y, -0.05, -0.005, 0.016, 0.014)); // cheekbones
      d += 0.004 * G(x, y, 0, -0.045, 0.02, 0.006) - 0.003 * G(x, y, 0, -0.052, 0.022, 0.003); // lips, mouth line
      d += 0.006 * G(x, y, 0, -0.088, 0.02, 0.012);                                   // chin
      z += d * f;
      p.setXYZ(i, x, y, z);
    }
    g.computeVertexNormals(); return g;
  })();
  // painted face shading on the sphere UVs (front of the head is u = 0.25): sockets, brows, nose shadow, lips, stubble, hairline
  const faceTex = (() => {
    const c = document.createElement('canvas'); c.width = 512; c.height = 256; const g = c.getContext('2d'); const r = rng(808);
    g.fillStyle = '#e6e2de'; g.fillRect(0, 0, 512, 256);
    for (let i = 0; i < 3000; i++) { const v = 200 + r() * 50; g.fillStyle = `rgba(${v},${v - 8},${v - 14},0.25)`; g.fillRect(r() * 512, r() * 256, 2, 2); }
    const blob = (x, y, rx, ry, col, a) => { g.save(); g.translate(x, y); g.scale(1, ry / rx); const gr = g.createRadialGradient(0, 0, 0, 0, 0, rx);
      gr.addColorStop(0, `rgba(${col},${a})`); gr.addColorStop(1, `rgba(${col},0)`); g.fillStyle = gr; g.beginPath(); g.arc(0, 0, rx, 0, 7); g.fill(); g.restore(); };
    for (const ex of [96, 160]) {
      blob(ex, 110, 26, 16, '40,26,20', 0.75);          // socket shadow
      blob(ex, 112, 12, 5, '15,10,8', 0.9);             // lash line / lids
      g.fillStyle = 'rgba(30,22,18,0.85)'; g.save(); g.translate(ex, 94); g.rotate(ex < 128 ? 0.1 : -0.1); g.fillRect(-15, -3, 30, 5); g.restore();   // brows
      blob(ex + (ex < 128 ? -8 : 8), 132, 22, 14, '90,50,40', 0.25);                                     // cheek shading
    }
    blob(128, 140, 12, 7, '50,30,24', 0.3);          // under-nose shadow
    blob(138, 125, 7, 18, '60,36,28', 0.35);          // nose side shadow
    g.fillStyle = 'rgba(70,40,36,0.45)'; g.fillRect(116, 159, 24, 2); blob(128, 164, 12, 4, '90,60,50', 0.2);   // lips
    for (let i = 0; i < 1600; i++) { const x = 88 + r() * 80, y = 150 + r() * 60; if (Math.abs(x - 128) < 16 && y < 170) continue; g.fillStyle = 'rgba(40,30,26,0.18)'; g.fillRect(x, y, 1.5, 1.5); } // stubble
    const hg = g.createLinearGradient(0, 40, 0, 80); hg.addColorStop(0, 'rgba(25,18,14,1)'); hg.addColorStop(1, 'rgba(25,18,14,0)');
    g.fillStyle = hg; g.fillRect(0, 0, 512, 80); g.fillStyle = 'rgba(25,18,14,1)'; g.fillRect(256, 0, 256, 150); // hair top and back
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const faceMats = new Map();
  const faceOf = (m) => { if (!faceMats.has(m)) { const f = m.clone(); f.map = faceTex; f.color = m.color.clone().multiplyScalar(1.15); faceMats.set(m, f); } return faceMats.get(m); };
  const addFace = (head, mats, o = {}) => {
    const H = (geo, mat, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); head.add(m); return m; };
    H(skullGeo, faceOf(mats.skin), 0, o.y0 ?? 0.02, 0).castShadow = true;
    const y0 = (o.y0 ?? 0.02) + 0.005;
    for (const sx of [-1, 1]) {
      H(new THREE.SphereGeometry(0.02, 10, 8), mats.skin, sx * 0.088, y0 + 0.0, -0.01).scale.set(0.4, 1.1, 0.75);   // ears
      if (o.closed) H(new THREE.SphereGeometry(0.0125, 10, 8), mats.skin, sx * 0.034, y0 + 0.022, 0.08).scale.set(1.15, 0.8, 1);
      else {
        H(new THREE.SphereGeometry(0.009, 12, 10), M.eyeW, sx * 0.034, y0 + 0.021, 0.074).scale.set(1.1, 0.55, 1);
      }
          }
    if (o.mouthOpen) H(new THREE.SphereGeometry(0.01, 8, 6), M.dark, 0, y0 - 0.058, 0.088).scale.set(1.3, 0.7, 0.5);
  };
  // East German border guard: borderGuard() from look.js, re-dressed (skin, boots, posable arms with gloves)
  const makeGuard = ({ rifle = 'slung' } = {}) => {
    const g = borderGuard(THREE, M.coat);
    const ch = [...g.group.children];
    ch[1].material = M.belt; ch[2].material = M.boot; ch[4].material = M.boot; ch[6].material = M.skin;
    g.head.children[0].material = M.skin; g.head.children[3].material = M.visor;
    g.group.remove(ch[3]); g.group.remove(ch[5]);
    const slung = ch[8]; slung.children.forEach(c => c.material = M.gun); slung.visible = rifle === 'slung'; g.slung = slung;
    g.head.children[0].visible = false; addFace(g.head, M, { y0: 0.03 });
    { const hr = new THREE.Mesh(new THREE.SphereGeometry(0.106, 16, 10, 0, Math.PI * 2, 0, 1.6), M.dark); hr.position.set(0, 0.04, -0.015); hr.rotation.x = -0.9; g.head.add(hr); }
    for (const sx of [-1, 1]) { const toe = box(0.1, 0.07, 0.15, M.boot, sx * 0.11, 0.035, 0.07, g.group); toe.castShadow = true; }
    const col = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.13, 0.08, 16), M.coat); col.position.set(0, 1.55, 0); col.scale.z = 0.8; g.group.add(col);
    const arms = {};
    for (const sx of [-1, 1]) {
      const sh = new THREE.Group(); sh.position.set(sx * 0.265, 1.44, 0.02); sh.rotation.z = sx * 0.1; g.group.add(sh);
      const up = new THREE.Mesh(new THREE.CapsuleGeometry(0.064, 0.22, 4, 10), M.coat); up.position.y = -0.16; up.castShadow = true; sh.add(up);
      const el = new THREE.Group(); el.position.y = -0.3; sh.add(el);
      const fo = new THREE.Mesh(new THREE.CapsuleGeometry(0.057, 0.2, 4, 10), M.coat); fo.position.y = -0.13; fo.castShadow = true; el.add(fo);
      const hand = new THREE.Group(); hand.position.y = -0.3; el.add(hand);
      const palm = box(0.045, 0.1, 0.085, M.glove, 0, -0.05, 0.005, hand); palm.castShadow = true;
      arms[sx < 0 ? 'R' : 'L'] = { sh, el, hand };
    }
    g.arms = arms;
    g.group.traverse(o => { if (o.isMesh) o.castShadow = true; });
    return g;
  };
  // AK-pattern MPi-KM, muzzle up, origin at the butt
  const makeRifle = () => {
    const r = new THREE.Group();
    box(0.04, 0.27, 0.1, M.wood, 0, 0.135, 0, r).scale.set(1, 1, 1);
    box(0.045, 0.25, 0.07, M.gun, 0, 0.39, 0.015, r);
    box(0.034, 0.1, 0.04, M.wood, 0, 0.29, 0.07, r).rotation.x = 0.35;
    const mag = box(0.03, 0.2, 0.05, M.gun, 0, 0.44, 0.085, r); mag.rotation.x = -0.45;
    box(0.048, 0.2, 0.06, M.wood, 0, 0.62, 0.01, r);
    const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.011, 0.32, 8), M.gun); bar.position.set(0, 0.86, 0.01); r.add(bar);
    const gas = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.22, 8), M.gun); gas.position.set(0, 0.68, -0.03); r.add(gas);
    box(0.012, 0.04, 0.03, M.gun, 0, 0.98, 0.02, r);
    box(0.008, 0.6, 0.012, M.belt, 0.0, 0.45, -0.06, r);
    r.traverse(o => { if (o.isMesh) o.castShadow = true; });
    return r;
  };

  // West Berliners: low-poly people with coats, hats, faces. origin on the floor under the hips, facing +z
  const pmat = {};
  const coatM = (c) => pmat[c] || (pmat[c] = std({ color: c, roughness: 0.88 }));
  const skinP = std({ color: 0x7e7068, roughness: 0.7, emissive: 0x1a120c, emissiveIntensity: 0.3 });
  const stareSkin = std({ color: 0x6e6058, roughness: 0.7, emissive: 0x140c08, emissiveIntensity: 0.4 });
  const hairM = (c) => pmat['h' + c] || (pmat['h' + c] = std({ color: c, roughness: 0.8 }));
  const civilian = (o) => {
    const { coat = 0x3b3a38, hat = 'fedora', hatCol = 0x1e1d1b, pose = 'lap', standing = false, closed = false, scale = 1, hair = 0x2a2018, female = false, mouthOpen = false } = o;
    const mats = { skin: skinP };
    const g = new THREE.Group(); const cm = coatM(coat);
    const dy = standing ? 0.47 : 0;
    const M2 = (geo, mat, x, y, z, p = g) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); p.add(m); return m; };
    // legs
    for (const sx of [-1, 1]) {
      if (standing) { limb([sx * 0.1, 0.95, 0], [sx * 0.1, 0.1, 0], 0.07, coatM(0x1f1f1f), g); M2(new THREE.BoxGeometry(0.1, 0.07, 0.26), M.boot, sx * 0.1, 0.035, 0.05); }
      else {
        limb([sx * 0.1, 0.5, -0.02], [sx * 0.11, 0.5, 0.4], 0.075, female ? cm : coatM(0x222220), g);
        limb([sx * 0.11, 0.48, 0.42], [sx * 0.11, 0.1, 0.44], female ? 0.05 : 0.06, coatM(female ? 0x2a2420 : 0x222220), g);
        M2(new THREE.BoxGeometry(0.09, 0.07, 0.24), M.boot, sx * 0.11, 0.035, 0.5);
      }
    }
    // coat: lathe from hem to collar
    const prof = (standing ? [[0, 0.5], [0.27, 0.5], [0.25, 0.8], [0.22, 1.05], [0.21, 1.2], [0.23, 1.38], [0.24, 1.46], [0.2, 1.52], [0.1, 1.56], [0, 1.57]]
      : [[0, 0.44], [0.22, 0.46], [0.22, 0.6], [0.2, 0.75], [0.22, 0.92], [0.23, 0.99], [0.19, 1.05], [0.1, 1.09], [0, 1.1]]).map(([a, b]) => new THREE.Vector2(a, b));
    const torso = M2(new THREE.LatheGeometry(prof, 22), cm, 0, 0, 0); torso.scale.set(1, 1, 0.66);
    const col = M2(new THREE.CylinderGeometry(0.085, 0.12, 0.08, 14), cm, 0, 1.08 + dy, 0); col.scale.z = 0.8;
    const zf = (y) => 0.66 * (standing ? 0.235 : 0.215);
    M2(new THREE.BoxGeometry(0.012, standing ? 0.95 : 0.5, 0.01), M.dark, 0.015, (standing ? 0.98 : 0.74) + 0, zf() + 0.004);       // front opening
    for (let k = 0; k < 3; k++) M2(new THREE.SphereGeometry(0.011, 6, 4), M.dark, 0.045, 0.9 + dy - k * 0.12, zf() + 0.006);         // buttons
    for (const sx of [-1, 1]) { const lp = M2(new THREE.BoxGeometry(0.07, 0.2, 0.012), M.dark, sx * 0.05, 0.97 + dy, zf() + 0.002); lp.rotation.z = sx * 0.35; lp.material = coatM(0x1a1816); }
    if (o.scarfNeck) { M2(new THREE.TorusGeometry(0.075, 0.03, 8, 16), coatM(o.scarfNeck), 0, 1.07 + dy, 0.0).rotation.x = Math.PI / 2; }
    M2(new THREE.CylinderGeometry(0.05, 0.055, 0.08, 10), skinP, 0, 1.13 + dy, 0);
    // head
    const head = new THREE.Group(); head.position.set(0, 1.24 + dy, 0.01); g.add(head);
    addFace(head, mats, { closed, mouthOpen });
    if (hat !== 'scarf') { const hr = M2(new THREE.SphereGeometry(0.104, 16, 10, 0, Math.PI * 2, 0, 1.5), hairM(hair), 0, 0.035, -0.012, head); hr.rotation.x = -0.85; }
    const hm = hairM(hatCol);
    if (hat === 'fedora') {
      M2(new THREE.CylinderGeometry(0.09, 0.108, 0.1, 18), hm, 0, 0.135, -0.005, head);
      M2(new THREE.CylinderGeometry(0.175, 0.175, 0.012, 22), hm, 0, 0.09, -0.005, head);
      M2(new THREE.CylinderGeometry(0.109, 0.109, 0.025, 18), M.dark, 0, 0.1, -0.005, head);
    } else if (hat === 'cap') {
      M2(new THREE.SphereGeometry(0.118, 16, 8, 0, Math.PI * 2, 0, 1.2), hm, 0, 0.055, -0.01, head).scale.set(1, 0.6, 1.08);
      M2(new THREE.BoxGeometry(0.16, 0.012, 0.07), hm, 0, 0.085, 0.11, head).rotation.x = 0.25;
    } else if (hat === 'scarf') {
      const s = M2(new THREE.SphereGeometry(0.118, 16, 12, 0, Math.PI * 2, 0, 2.1), hm, 0, 0.03, -0.018, head); s.rotation.x = -1.0;
      M2(new THREE.SphereGeometry(0.04, 8, 6), hm, 0, -0.1, -0.05, head);
    }
    // arms
    const S = (sx) => [sx * 0.2, 1.0 + dy, 0];
    for (const sx of [-1, 1]) {
      let E, Hd;
      if (pose === 'paper') { E = [sx * 0.27, 0.8 + dy, 0.16]; Hd = [sx * 0.29, 0.99 + dy, 0.36]; }
      else if (pose === 'crossed') { E = [sx * 0.22, 0.76 + dy, 0.1]; Hd = [-sx * 0.1, 0.84 + dy, 0.2]; }
      else if (pose === 'hang') { E = [sx * 0.24, 0.72 + dy, 0.02]; Hd = [sx * 0.25, 0.45 + dy, 0.06]; }
      else { E = [sx * 0.23, 0.74 + dy, 0.08]; Hd = [sx * 0.13, 0.6 + dy, 0.33]; }
      limb(S(sx), E, 0.058, cm, g); limb(E, Hd, 0.05, cm, g);
      M2(new THREE.SphereGeometry(0.042, 10, 8), skinP, ...Hd).scale.set(0.8, 1, 1.2);
    }
    if (pose === 'paper') {
      const paper = new THREE.Group(); paper.position.set(0, 0.97 + dy, 0.4); g.add(paper);
      for (const side of [-1, 1]) {
        const pl = new THREE.Mesh(new THREE.PlaneGeometry(0.36, 0.52), side < 0 ? paperL : paperR);
        pl.position.set(side * 0.17, 0, -side * 0.0 + 0.04 * 0); pl.rotation.y = side * -0.28; pl.position.z = -0.045; paper.add(pl);
      }
    }
    g.scale.setScalar(scale);
    g.userData.head = head;
    return g;
  };
  const paperTex = (side) => canvasTex(THREE, 360, 520, (g, w, h) => {
    const r = rng(side > 0 ? 41 : 42);
    g.fillStyle = '#e4dccb'; g.fillRect(0, 0, w, h); g.fillStyle = '#1b1a18';
    if (side > 0) {
      g.font = 'bold 64px "DejaVu Serif"'; g.textAlign = 'center'; g.fillText('DER ABEND', w / 2, 66);
      g.fillRect(14, 80, w - 28, 3); g.font = '13px "DejaVu Serif"'; g.fillText('Berlin, Dienstag, 14. November 1972 · 30 Pf', w / 2, 98); g.fillRect(14, 106, w - 28, 2);
      g.font = 'bold 34px "DejaVu Sans Condensed"'; g.fillText('Neue Gespräche', w / 2, 146); g.fillText('über den Transit', w / 2, 182);
      g.fillStyle = '#5b5750'; g.fillRect(20, 200, 190, 130); g.fillStyle = '#1b1a18';
    } else {
      g.font = 'bold 26px "DejaVu Sans Condensed"'; g.textAlign = 'left'; g.fillText('Sport', 20, 40); g.fillRect(14, 50, w - 28, 2);
      g.fillStyle = '#5b5750'; g.fillRect(150, 70, 190, 120); g.fillStyle = '#1b1a18';
    }
    for (let c = 0; c < 3; c++) for (let y = side > 0 ? 345 : 210; y < h - 14; y += 9) {
      if (side > 0 && c === 0 && y < 345) continue;
      const lw = 96 - (r() < 0.12 ? 40 : 0); g.fillStyle = `rgba(27,26,24,${0.55 + r() * 0.2})`; g.fillRect(18 + c * 112, y, lw, 4);
    }
    if (side > 0) for (let y = 210; y < 330; y += 9) g.fillRect(222, y, 120, 4);
    else for (let y = 70; y < 190; y += 9) g.fillRect(18, y, 120, 4);
  });
  const paperR = std({ map: paperTex(1), roughness: 0.9, side: THREE.DoubleSide, emissive: 0x4a3e2c, emissiveIntensity: 0.25 });
  const paperL = std({ map: paperTex(-1), roughness: 0.9, side: THREE.DoubleSide, emissive: 0x4a3e2c, emissiveIntensity: 0.25 });

  // ======================= TRAIN =======================
  const T = {
    body: std({ color: 0xbfa060, roughness: 0.42, metalness: 0.25 }), door: std({ color: 0xae9050, roughness: 0.45, metalness: 0.25 }),
    roof: std({ color: 0x5f5e5a, roughness: 0.6, metalness: 0.3 }), under: std({ color: 0x141414, roughness: 0.8 }),
    inner: std({ color: 0xb4aea0, roughness: 0.7, emissive: 0x2a241a, emissiveIntensity: 0.35 }),
    seat: std({ color: 0x5e4436, roughness: 0.85, emissive: 0x1a1008, emissiveIntensity: 0.4 }),
    floor: std({ color: 0x3a3631, roughness: 0.9 }), chrome: std({ color: 0xd0d0d0, metalness: 1, roughness: 0.22 }),
    strip: new THREE.MeshBasicMaterial({ color: 0xa89880 }), rubber: std({ color: 0x0c0c0c, roughness: 0.7 }),
    glass: new THREE.MeshStandardMaterial({ color: 0x9aa3a6, transparent: true, opacity: 0.06, roughness: 0.7, metalness: 0.0, depthWrite: false, side: THREE.DoubleSide }),
    wind: std({ color: 0x0a0b0c, roughness: 0.1, metalness: 0.7 }),
  };
  const destTex = canvasTex(THREE, 512, 96, (g, w, h) => { g.fillStyle = '#121212'; g.fillRect(0, 0, w, h); g.fillStyle = '#f4e6c8'; g.font = 'bold 54px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.fillText('8  Leinestraße', w / 2, 66); });
  const train = new THREE.Group();
  const doorsU = [-3.5, -12.0], bays = [[-2.75, -0.25], [-11.25, -4.25], [-15.25, -12.75]];
  const rp = rng(91);
  const coats = [0x2e2c2a, 0x3a3029, 0x262a33, 0x403830, 0x34302c, 0x2a2826, 0x463c32];
  const special = {};
  for (let i = 0; i < NC; i++) {
    const c = new THREE.Group(); c.position.z = -i * (CAR + GAP); train.add(c);
    const zc = -CAR / 2;
    for (const sx of [-1, 1]) {
      const xo = sx * (CW / 2 - 0.025);
      box(0.05, 1.4, CAR, T.body, xo, 1.15, zc, c);
      box(0.05, 0.13, CAR, T.body, xo, 2.915, zc, c);
      box(0.012, 0.05, CAR, T.rubber, sx * (CW / 2 + 0.002), 1.83, zc, c);
      for (const [a, b] of bays) {
        const n = Math.max(1, Math.round((b - a) / 1.75));
        for (let k = 0; k <= n; k++) box(0.06, 1.0, 0.1, T.body, xo, 2.35, a + (b - a) * k / n, c);
      }
      for (const u of doorsU) for (const lf of [-1, 1]) {
        const zl = u + lf * 0.325, xd = sx * (CW / 2 + 0.006);
        box(0.05, 1.45, 0.64, T.door, xd, 1.175, zl, c);
        box(0.05, 0.28, 0.64, T.door, xd, 2.84, zl, c);
        box(0.05, 0.8, 0.08, T.door, xd, 2.3, zl + 0.28, c); box(0.05, 0.8, 0.08, T.door, xd, 2.3, zl - 0.28, c);
        box(0.06, 2.55, 0.02, T.rubber, xd, 1.72, u, c);
        const hdl = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.36, 8), T.chrome); hdl.position.set(sx * (CW / 2 + 0.07), 2.08, u - lf * 0.09); c.add(hdl);
        for (const yy of [1.92, 2.24]) box(0.06, 0.02, 0.02, T.chrome, sx * (CW / 2 + 0.045), yy, u - lf * 0.09, c);
      }
      const gl = new THREE.Mesh(new THREE.PlaneGeometry(CAR, 1.0), T.glass); gl.position.set(sx * (CW / 2 + 0.004), 2.35, zc); gl.rotation.y = sx * Math.PI / 2; c.add(gl);
      // benches
      for (const [a, b] of bays) {
        const len = b - a - 0.1, zz = (a + b) / 2;
        box(0.45, 0.1, len, T.seat, sx * (CW / 2 - 0.28), FL + 0.42, zz, c);
        box(0.03, 0.38, len, T.inner, sx * (CW / 2 - 0.5), FL + 0.21, zz, c);
        box(0.08, 0.42, len, T.seat, sx * (CW / 2 - 0.1), FL + 0.68, zz, c);
      }
      for (const u of doorsU) for (const lf of [-1, 1]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.9, 8), T.chrome); p.position.set(sx * (CW / 2 - 0.5), FL + 0.95, u + lf * 0.75); c.add(p); }
      const gr = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, CAR - 0.4, 8), T.chrome); gr.rotation.x = Math.PI / 2; gr.position.set(sx * 0.6, 2.8, zc); c.add(gr);
      box(0.05, 0.05, CAR - 0.8, T.strip, sx * 0.42, 2.95, zc, c);
    }
    for (const e of [0, -CAR]) box(CW, 2.55, 0.05, T.body, 0, 1.725, e, c);
    const roof = new THREE.Mesh(new RoundedBoxGeometry(CW, 0.45, CAR, 3, 0.18), T.roof); roof.position.set(0, 3.2, zc); c.add(roof);
    const ic = new THREE.Mesh(new THREE.PlaneGeometry(CW - 0.1, CAR - 0.1), T.inner); ic.rotation.x = Math.PI / 2; ic.position.set(0, 2.97, zc); c.add(ic);
    box(CW - 0.1, 0.05, CAR - 0.1, T.floor, 0, FL - 0.025, zc, c);
    box(CW - 0.2, 0.35, CAR - 0.6, T.under, 0, 0.275, zc, c);
    for (const u of [-2.4, -13.1]) box(2.0, 0.32, 2.4, T.under, 0, 0.4, u, c);
    if (i < NC - 1) box(CW - 0.6, 2.3, GAP, T.rubber, 0, 1.75, -CAR - GAP / 2, c);
    // passengers
    const list = [];
    if (i === 0) {
      list.push({ u: -1.3, sx: 1, o: { coat: 0x34302c, hat: 'cap', pose: 'lap' } });
      list.push({ u: -5.28, sx: 1, o: { coat: 0x3e342b, hat: 'fedora', pose: 'paper' }, tag: 'paper' });
      list.push({ u: -6.96, sx: 1, o: { coat: 0x2b3140, hat: 'fedora', pose: 'crossed', scarfNeck: 0x4a4038, closed: true, mouthOpen: true, hatCol: 0x3a3632 }, tag: 'sleep' });
      list.push({ u: -8.88, sx: 1, o: { coat: 0x2e2c2a, hat: 'none', hair: 0x1a1410, pose: 'lap' }, tag: 'stare' });
      list.push({ u: -10.3, sx: 1, o: { coat: 0x463c32, hat: 'scarf', hatCol: 0x4a3c30, pose: 'lap', female: true } });
      list.push({ u: -13.6, sx: 1, o: { coat: 0x3a3029, hat: 'scarf', hatCol: 0x2a2826, pose: 'crossed', female: true } });
      list.push({ u: -14.7, sx: -1, o: { coat: 0x2b3140, hat: 'cap', pose: 'lap' } });
    } else {
      for (const [a, b] of bays) for (let u = a + 0.45; u < b - 0.3; u += 0.62 + rp() * 0.5) for (const sx of [-1, 1]) {
        if (rp() < 0.55) continue;
        const hats = ['fedora', 'cap', 'scarf', 'none'], h = hats[Math.floor(rp() * 4)];
        list.push({ u, sx, o: { coat: coats[Math.floor(rp() * coats.length)], hat: h, female: h === 'scarf', pose: rp() < 0.3 ? 'crossed' : rp() < 0.2 ? 'paper' : 'lap', hatCol: rp() < 0.5 ? 0x1e1d1b : 0x4a4038, scale: 0.95 + rp() * 0.1, scarfNeck: rp() < 0.3 ? 0x5a4a3c : null } });
      }
    }
    for (const p of list) {
      const m = civilian(p.o); m.position.set(p.sx * (CW / 2 - 0.4), FL, p.u); m.rotation.y = p.sx > 0 ? -Math.PI / 2 : Math.PI / 2; c.add(m);
      if (p.tag === 'sleep') { const h = m.userData.head; h.rotation.z = 0.42; h.rotation.x = 0.25; h.position.x += 0.05; }
      if (p.tag) special[p.tag] = m;
      if (p.tag === 'stare') m.traverse(o => { if (o.isMesh && o.material === skinP) o.material = stareSkin; });
    }
  }
  // cab front (local z = 0) and tail (local z = -TRAIN_LEN)
  for (const [zf, front] of [[0.03, true], [-TRAIN_LEN - 0.03, false]]) {
    const s = front ? 1 : -1;
    const ws = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 0.85), T.wind); ws.position.set(0, 2.35, zf); ws.rotation.y = front ? 0 : Math.PI; train.add(ws);
    const ds = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.2), new THREE.MeshBasicMaterial({ map: destTex, color: 0xbbbbbb })); ds.position.set(0, 2.88, zf + s * 0.005); ds.rotation.y = front ? 0 : Math.PI; train.add(ds);
    for (const o of [-0.8, 0.8]) {
      const lamp = new THREE.Mesh(new THREE.CircleGeometry(0.1, 16), new THREE.MeshBasicMaterial({ color: front ? 0xffffff : 0xff5a28 })); lamp.position.set(o, 1.25, zf + s * 0.01); lamp.rotation.y = front ? 0 : Math.PI; train.add(lamp);
      const gw = glow(THREE, front ? 0xfff6e8 : 0xff5a28, front ? 1.1 : 0.8, 0.9); gw.position.set(o, 1.25, zf + s * 0.05); train.add(gw);
    }
  }
  const head = new THREE.SpotLight(0xfff2de, 0, 90, 0.36, 0.5, 1.0); head.position.set(0, 1.3, 0.2); head.target.position.set(0, 1.0, 40); train.add(head, head.target);
  const headBeam = beam(THREE, 0xfff2de, 26, 3.2, 0.03); headBeam.rotation.x = Math.PI / 2; headBeam.position.set(0, 1.3, 0.15); train.add(headBeam);
  // interior light pool (moves with the slots nearest the camera)
  const tLights = [];
  for (let k = 0; k < 4; k++) { const pl = new THREE.PointLight(0xffd9a6, 0, 6.5, 1.3); train.add(pl); tLights.push(pl); }
  // motion streaks for the fast pass
  const streakTex = canvasTex(THREE, 512, 64, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.5, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const streakMat = new THREE.MeshBasicMaterial({ map: streakTex, color: 0xffcf96, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false });
  for (const sx of [-1, 1]) for (const [yy, hh] of [[2.35, 0.9], [2.95, 0.12]]) { const st = new THREE.Mesh(new THREE.PlaneGeometry(TRAIN_LEN, hh), streakMat); st.position.set(sx * (CW / 2 + 0.05), yy, -TRAIN_LEN / 2); st.rotation.y = sx * Math.PI / 2; train.add(st); }
  train.position.set(TL, 0, -400);
  scene.add(train);

  // ======================= GUARD ROOM =======================
  const paint = canvasTex(THREE, 256, 256, (g, w, h) => {
    const r = rng(61); g.fillStyle = '#8a8c80'; g.fillRect(0, 0, w, h); g.fillStyle = '#4f5a4c'; g.fillRect(0, h * 0.55, w, h * 0.45);
    g.fillStyle = '#2e2f2a'; g.fillRect(0, h * 0.55 - 3, w, 4);
    for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(30,28,24,${r() * 0.12})`; g.fillRect(r() * w, r() * h, 1 + r() * 6, 1 + r() * 14); }
  });
  paint.repeat.set(1, 1); paint.wrapS = paint.wrapT = THREE.ClampToEdgeWrapping;
  const roomM = std({ map: paint, roughness: 0.85 });
  const conc = std({ map: concreteTex(THREE, [1, 1], 44, 95), roughness: 0.95 });
  const rooms = new THREE.Group(); scene.add(rooms);
  const rb = (x0, x1, y0, y1, z0, z1, mat = roomM) => { const m = box(x1 - x0, y1 - y0, z1 - z0, mat, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, rooms); m.castShadow = m.receiveShadow = true; return m; };
  const XF = -8.25, XB = -10.2, ZA = -4.15, ZB = 4.75, YC = 3.4;
  // front wall around the slit (concrete core behind the tiles)
  rb(XF, -8.0, 1, SL.y0, ZA, ZB, conc); rb(XF, -8.0, SL.y1, YC, ZA, ZB, conc);
  rb(XF, -8.0, SL.y0, SL.y1, ZA, SL.z0, conc); rb(XF, -8.0, SL.y0, SL.y1, SL.z1, ZB, conc);
  rb(XB - 0.15, XB, 1, YC, ZA, ZB); rb(XB - 0.15, -8.0, YC, YC + 0.1, ZA, ZB, conc);
  rb(XB, XF, 0.95, 1.0, ZA, ZB, std({ map: concreteTex(THREE, [1, 2], 45, 70) }));
  rb(XB, XF, 1, YC, ZA - 0.15, ZA); rb(XB, XF, 1, YC, ZB, ZB + 0.15);
  const DX0 = -9.1, DX1 = -8.35, DY = 3.0, ZD = -1.6;   // door in the end wall
  rb(XB, DX0, 1, YC, ZD - 0.15, ZD); rb(DX1, XF, 1, YC, ZD - 0.15, ZD); rb(DX0, DX1, DY, YC, ZD - 0.15, ZD);
  const WX0 = -8.95, WX1 = -8.38, WY0 = 2.3, WY1 = 2.85, ZW = 2.2;   // observation window to the next room
  rb(XB, WX0, 1, YC, ZW, ZW + 0.15); rb(WX1, XF, 1, YC, ZW, ZW + 0.15); rb(WX0, WX1, 1, WY0, ZW, ZW + 0.15); rb(WX0, WX1, WY1, YC, ZW, ZW + 0.15);
  const obsGlass = new THREE.Mesh(new THREE.PlaneGeometry(WX1 - WX0, WY1 - WY0), new THREE.MeshStandardMaterial({ color: 0x8a9496, transparent: true, opacity: 0.1, roughness: 0.35, metalness: 0.1, depthWrite: false, side: THREE.DoubleSide }));
  obsGlass.position.set((WX0 + WX1) / 2, (WY0 + WY1) / 2, ZW + 0.12); rooms.add(obsGlass);
  // window frame
  const frameM = std({ color: 0x1c1c1a, roughness: 0.6, metalness: 0.4 });
  for (const [w, h, x, y] of [[WX1 - WX0 + 0.06, 0.04, (WX0 + WX1) / 2, WY0], [WX1 - WX0 + 0.06, 0.04, (WX0 + WX1) / 2, WY1], [0.04, WY1 - WY0, WX0, (WY0 + WY1) / 2], [0.04, WY1 - WY0, WX1, (WY0 + WY1) / 2]])
    box(w, h, 0.2, frameM, x, y, ZW + 0.075, rooms);
  // door leaf, hinged at DX0
  const doorG = new THREE.Group(); doorG.position.set(DX0, 1, ZD - 0.03); rooms.add(doorG);
  const leaf = box(DX1 - DX0 - 0.01, DY - 1 - 0.01, 0.05, std({ color: 0x4a4d47, roughness: 0.6, metalness: 0.3 }), (DX1 - DX0) / 2, (DY - 1) / 2, 0, doorG); leaf.castShadow = true;
  box(0.12, 0.03, 0.05, railM, DX1 - DX0 - 0.1, 1.0, 0.05, doorG);
  // lit corridor behind the door
  const corr = new THREE.Mesh(new THREE.PlaneGeometry(XF - XB, YC - 1), new THREE.MeshBasicMaterial({ color: 0x8c6c4c, fog: false }));
  corr.position.set((XB + XF) / 2, (YC + 1) / 2, ZA + 0.01); rooms.add(corr);
  const corrGlow = glow(THREE, AMBER, 3.0, 0.7); corrGlow.position.set(-8.72, 2.6, ZA + 0.2); rooms.add(corrGlow);
  const doorSpot = new THREE.SpotLight(0xffc48a, 0, 9, 0.55, 0.6, 1.2);
  doorSpot.position.set(-8.72, 2.75, ZA + 0.3); doorSpot.target.position.set(-8.9, 1.5, 1.2); doorSpot.castShadow = true; doorSpot.shadow.mapSize.set(1024, 1024); doorSpot.shadow.bias = -0.0008;
  rooms.add(doorSpot, doorSpot.target);
  // light through the slit: projected band so only a strip of the platform's light enters
  const SD = 7.0, SA = 0.16;
  const slitSpot = new THREE.SpotLight(0xffb873, 0, 16, SA, 0.1, 0);
  slitSpot.position.set(-8 + SD, 2.732, 0.0); slitSpot.target.position.set(-9.8, 2.69, 0.0);
  slitSpot.castShadow = true; slitSpot.shadow.mapSize.set(1024, 1024); slitSpot.shadow.bias = -0.0006; slitSpot.shadow.camera.near = 0.5;
  slitSpot.map = canvasTex(THREE, 512, 512, (g, w, h) => { g.fillStyle = '#000'; g.fillRect(0, 0, w, h);
    // the slit seen from the light: 1.5 x 0.14 m at 2.6 m inside a cone of half-width tan(0.42)*2.6
    const hx = 1.5 / (2 * Math.tan(SA) * SD) * w / 2, hy = 0.4 * (SL.y1 - SL.y0) / (2 * Math.tan(SA) * SD) * h / 2;
    g.fillStyle = '#fff'; g.filter = 'blur(1px)'; g.fillRect(w / 2 - hx, h / 2 - hy, 2 * hx, 2 * hy); }, [1, 1]);
  slitSpot.map.wrapS = slitSpot.map.wrapT = THREE.ClampToEdgeWrapping; slitSpot.map.colorSpace = THREE.NoColorSpace;
  scene.add(slitSpot, slitSpot.target);
  // a dim bulb in the room
  const roomBulb = new THREE.PointLight(AMBER, 0, 2.4, 1.6); roomBulb.position.set(-9.6, 3.15, -0.6); rooms.add(roomBulb);
  const rbm = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8), bulbMat.clone()); rbm.position.copy(roomBulb.position); rooms.add(rbm);
  const rbg = glow(THREE, AMBER, 0.5, 0.6); rbg.position.copy(roomBulb.position); rooms.add(rbg);
  box(0.01, 0.25, 0.01, steel, -9.6, 3.28, -0.6, rooms);
  // duty roster on a clipboard, telephone
  const roster = canvasTex(THREE, 256, 360, (g, w, h) => {
    const r = rng(23); g.fillStyle = '#ddd6c4'; g.fillRect(0, 0, w, h); g.fillStyle = '#1a1a1a';
    g.font = 'bold 22px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.fillText('DIENSTPLAN', w / 2, 34);
    g.font = '12px "DejaVu Sans"'; g.fillText('GÜst Rosenthaler Platz · KW 46', w / 2, 52);
    g.lineWidth = 1; g.strokeStyle = '#333';
    for (let i = 0; i <= 12; i++) { g.beginPath(); g.moveTo(12, 64 + i * 22); g.lineTo(w - 12, 64 + i * 22); g.stroke(); }
    for (const x of [12, 70, 160, w - 12]) { g.beginPath(); g.moveTo(x, 64); g.lineTo(x, 64 + 264); g.stroke(); }
    g.font = 'italic 14px "DejaVu Serif"'; g.textAlign = 'left';
    const names = ['Krüger', 'Weber', 'Lange', 'Schulz', 'Neumann', 'Hoffmann', 'Richter', 'Wolf', 'Braun', 'Zimmer', 'Kühn', 'Vogel'];
    const sh = ['06–14', '14–22', '22–06'];
    for (let i = 0; i < 12; i++) { g.fillText(sh[Math.floor(r() * 3)], 18, 80 + i * 22); g.fillText('Gefr. ' + names[i], 76, 80 + i * 22); g.fillText(['Posten 1', 'Posten 2', 'Streife'][Math.floor(r() * 3)], 166, 80 + i * 22); }
    g.strokeStyle = 'rgba(30,30,90,0.8)'; g.lineWidth = 2; g.beginPath(); g.moveTo(150, 120); g.lineTo(240, 205); g.stroke();
    g.font = 'italic bold 16px "DejaVu Serif"'; g.fillStyle = 'rgba(30,30,90,0.85)'; g.fillText('geändert!', 150, 345);
  });
  const clip = new THREE.Group(); clip.position.set(-9.6, 2.2, ZD + 0.02); rooms.add(clip);
  box(0.3, 0.42, 0.012, std({ color: 0x5a3c22, roughness: 0.7 }), 0, 0, 0, clip);
  const sheet = new THREE.Mesh(new THREE.PlaneGeometry(0.26, 0.36), std({ map: roster, roughness: 0.9 })); sheet.position.set(0, -0.02, 0.008); clip.add(sheet);
  box(0.12, 0.035, 0.02, railM, 0, 0.19, 0.012, clip);
  const phone = new THREE.Group(); phone.position.set(XB + 0.02, 2.3, 1.2); rooms.add(phone);
  box(0.12, 0.22, 0.16, std({ color: 0x151515, roughness: 0.3 }), 0.06, 0, 0, phone);
  box(0.06, 0.05, 0.22, std({ color: 0x151515, roughness: 0.3 }), 0.13, 0.13, 0, phone);
  // the two guards on post, side by side at the slit
  const inA = makeGuard({ rifle: 'slung' }), inB = makeGuard({ rifle: 'slung' });
  inA.group.position.set(-9.15, 1, 0.4); inB.group.position.set(-8.9, 1, -0.6);
  inA.group.rotation.y = Math.PI / 2 + 0.08; inB.group.rotation.y = Math.PI / 2 - 0.06;
  rooms.add(inA.group, inB.group);
  const officer = makeGuard({ rifle: 'none' }); officer.group.position.set(-8.72, 1, -2.5); rooms.add(officer.group);
  officer.arms.L.sh.rotation.x = -0.25; officer.arms.L.el.rotation.x = -1.3;
  const watcher = civilian({ coat: 0x2e2c2a, hat: 'fedora', standing: true, pose: 'hang', hatCol: 0x141312 });
  watcher.position.set(-8.92, 1, 3.3); watcher.rotation.y = Math.PI + 0.1; rooms.add(watcher);
  const watchLight = new THREE.PointLight(0xffb070, 0, 1.6, 2); watchLight.position.set(-8.66, 2.5, 2.5); rooms.add(watchLight);
  // a tape recorder on a shelf in the watcher's room
  const tape = new THREE.Group(); tape.position.set(-10.0, 2.1, 3.0); rooms.add(tape);
  box(0.3, 0.06, 0.4, std({ color: 0x232321, roughness: 0.5 }), 0, -0.07, 0, tape);
  box(0.28, 0.12, 0.34, std({ color: 0x3a3a36, roughness: 0.4, metalness: 0.3 }), 0, 0.02, 0, tape);
  for (const zz of [-0.08, 0.08]) { const reel = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.015, 20), std({ color: 0x777777, metalness: 0.7, roughness: 0.3 })); reel.position.set(0, 0.09, zz); tape.add(reel); }

  // ======================= PLATFORM GUARDS =======================
  const key = new THREE.SpotLight(AMBER, 0, 9, 0.7, 0.6, 1.4); key.position.set(-6.0, HT - 0.65, -6.0); key.target.position.set(-6.2, 1, -6.4);
  key.castShadow = true; key.shadow.mapSize.set(1024, 1024); key.shadow.bias = -0.0005; scene.add(key, key.target); key.visible = ['guardroom', 'eachother', 'boots', 'nostop'].includes(shot);
  if (shot === 'eachother') { key.position.set(-6.8, HT - 0.65, 20.3); key.target.position.set(-7.0, 1, 20.6); }
  if (shot === 'boots') { key.position.set(-4.4, 1.7, -17.6); key.target.position.set(-5.8, 0.9, -21); key.angle = 0.5; }
  if (shot === 'nostop') { key.position.set(-6.0, HT - 0.65, -6); key.target.position.set(-6.4, 1, -6.4); }
  const fill = new THREE.PointLight(0xffb070, 0, 3.2, 1.5); fill.position.set(-6.2, 2.9, 19.6); scene.add(fill); fill.visible = shot === 'eachother';
  const gA = makeGuard({ rifle: 'slung' }), gB = makeGuard({ rifle: 'slung' });
  scene.add(gA.group, gB.group);
  const gRifle = makeRifle(); scene.add(gRifle); gRifle.visible = false;
  // POV glove for the windows shot (child of the camera)
  const pov = new THREE.Group(); camera.add(pov); pov.visible = false;
  const sleeve = new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 0.34, 4, 12), M.coat); sleeve.rotation.x = -1.2; sleeve.position.set(0.0, -0.08, 0.18); pov.add(sleeve);
  const cuff = new THREE.Mesh(new THREE.CylinderGeometry(0.068, 0.068, 0.05, 14), M.coat); cuff.rotation.x = -1.2; cuff.position.set(0, 0.0, 0.0); pov.add(cuff);
  const palmG = box(0.085, 0.1, 0.035, M.glove, 0, 0.065, -0.02, pov); palmG.rotation.x = -0.2;
  const fingers = [];
  for (let k = 0; k < 4; k++) {
    const f = new THREE.Group(); f.position.set(-0.03 + k * 0.02, 0.115, -0.03); pov.add(f);
    const s1 = new THREE.Mesh(new THREE.CapsuleGeometry(0.011, 0.04, 3, 6), M.glove); s1.position.y = 0.025; f.add(s1);
    const j = new THREE.Group(); j.position.y = 0.05; f.add(j);
    const s2 = new THREE.Mesh(new THREE.CapsuleGeometry(0.01, 0.03, 3, 6), M.glove); s2.position.y = 0.02; j.add(s2);
    fingers.push({ f, j, len: k === 3 ? 0.8 : 1 });
  }
  const thumb = new THREE.Group(); thumb.position.set(-0.045, 0.04, -0.02); pov.add(thumb);
  const th = new THREE.Mesh(new THREE.CapsuleGeometry(0.012, 0.045, 3, 6), M.glove); th.position.y = 0.03; thumb.add(th); thumb.rotation.z = 0.7;

  // ======================= PER-SHOT SET-UP =======================
  const inRoom = shot === 'guardroom' || shot === 'teaser';
  rooms.visible = true;
  train.visible = !inRoom;
  if (!inRoom) { slitSpot.visible = false; doorSpot.visible = false; roomBulb.visible = false; watchLight.visible = false; }
  if (shot !== 'boots') head.castShadow = false; else { head.castShadow = true; head.shadow.mapSize.set(1024, 1024); head.shadow.bias = -0.0005; head.shadow.camera.near = 1; }
  if (shot === 'guardroom') { tLights.forEach(l => l.visible = false); head.visible = false; }
  if (shot === 'eachother') { tLights.forEach(l => l.visible = false); head.visible = false; }
  const strobe = new THREE.PointLight(0xffd29a, 0, 7, 1.2); strobe.position.set(-4.0, 2.5, 0.3); scene.add(strobe); strobe.visible = shot === 'teaser';
  const bok = shot === 'boots' ? { focus: 1.4, aperture: 0.004, maxblur: 0.01 } : null;
  const post = makeComposer(THREE, renderer, scene, camera, W, H, { bloom: 0.85, bloomRadius: 0.8, bloomThreshold: shot === 'windows' ? 0.75 : 0.58, exposure: 1.15, dof: bok });
  return { THREE, scene, camera, shot, lamps, dust, dustBase, seeds, train, head, headBeam, tLights, streakMat, special,
    key, strobe, fill, inA, inB, officer, doorG, doorSpot, slitSpot, roomBulb, rbm, rbg, watchLight, corrGlow, gA, gB, gRifle, pov, fingers, thumb, ...post };
}

function setLamp(l, v) {
  if (l.light) l.light.intensity = 11 * v; l.halo.material.opacity = v; l.beam.material.uniforms.opacity.value = 0.05 * v;
  l.bulb.material.color.setRGB(0.15 + 0.85 * v, 0.12 + 0.72 * v, 0.08 + 0.55 * v);
}
const placeGuard = (g, x, z, ry) => { g.group.position.set(x, 1, z); g.group.rotation.y = ry; };

export function update(ctx, t) {
  const { THREE, camera, shot, train, lamps, gA, gB } = ctx;
  const p = ctx.dust.geometry.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const s = ctx.seeds[i];
    p.array[i * 3] = ctx.dustBase[i * 3] + Math.sin(t * 0.13 + s) * 0.25;
    p.array[i * 3 + 1] = ctx.dustBase[i * 3 + 1] + Math.sin(t * 0.09 + s * 1.7) * 0.2 - ((t * 0.03 + s) % 1) * 0.1;
    p.array[i * 3 + 2] = ctx.dustBase[i * 3 + 2] + Math.cos(t * 0.11 + s) * 0.25;
  }
  p.needsUpdate = true;
  let lampLevel = (l) => 0.92 + 0.08 * Math.sin(t * 9 + l.seed) * Math.sin(t * 2.3 + l.seed);
  let fov = 40, headOn = 0, streak = 0;
  const breathe = (g, ph) => { g.group.children[0].scale.x = 1 + 0.012 * Math.sin(t * 1.6 + ph); };
  gA.group.visible = gB.group.visible = true;

  if (shot === 'guardroom') {
    ctx.slitSpot.intensity = t < 5.6 ? 9 : 12;
    // outside the cut the two guards press their eyes to the slit
    const atSlit = t < 5.6;
    ctx.inA.group.position.set(atSlit ? -8.56 : -9.15, 1, atSlit ? 0.36 : 0.4); ctx.inB.group.position.set(atSlit ? -8.55 : -8.9, 1, atSlit ? -0.42 : -0.6);
    ctx.roomBulb.intensity = t < 5.6 ? 0.35 : 0.3; ctx.rbg.material.opacity = 0.5;
    placeGuard(gA, -6.5, -5.2, Math.PI / 2 + 0.7); placeGuard(gB, -6.0, -7.2, Math.PI / 2 + 0.1); ctx.key.intensity = 12;
    gA.head.rotation.y = 0.2 * Math.sin(t * 0.4); breathe(gA, 0); breathe(gB, 2);
    // guards on post: tiny head shifts; after the door opens they glance back
    const back = (a, b) => seg(t, a, b) * (1 - 0.7 * seg(t, 11.6, 12.6));
    ctx.inA.head.rotation.y = 0.05 * Math.sin(t * 0.7) - 0.9 * back(8.8, 9.7);
    ctx.inB.head.rotation.y = -0.04 * Math.sin(t * 0.5 + 1) - 1.1 * back(8.6, 9.5);
    ctx.inA.head.rotation.x = 0.04 * Math.sin(t * 0.33);
    breathe(ctx.inA, 0.5); breathe(ctx.inB, 1.5);
    // inspection
    const open = seg(t, 8.0, 9.1);
    ctx.doorG.rotation.y = -1.45 * open;
    ctx.doorSpot.intensity = 3 * open; ctx.corrGlow.material.opacity = 0.18 * open;
    const step = seg(t, 9.0, 10.6);
    ctx.officer.group.position.set(-8.72, 1, -2.4 + 0.65 * step);
    ctx.officer.head.rotation.y = 0.2 * seg(t, 10.5, 12);
    ctx.watchLight.intensity = 0;
    if (t < 5.6) {
      // platform: guards in the gloom, then push in on the slit where two pairs of eyes catch the light
      const k1 = seg(t, 0, 5.8), k0 = seg(t, 0.8, 4.4);
      camera.position.set(lerp(-4.9, -6.75, k1), lerp(2.15, 2.72, k1), lerp(3.4, 0.45, k1));
      camera.lookAt(lerp(-6.3, -8.2, k0), lerp(1.85, 2.7, k0), lerp(-6.3, -0.02, k0));
      fov = lerp(40, 22, seg(t, 2.6, 5.6));
    } else if (t < 12.5) {
      const k = (t - 5.6) / 6.9;
      camera.position.set(lerp(-8.42, -8.45, k), lerp(2.58, 2.56, k), lerp(1.95, 1.85, k));
      camera.lookAt(lerp(-9.25, -9.3, k), 2.45, -1.6);
      fov = 44;
    } else {
      const k = seg(t, 12.5, 15.6);
      camera.position.set(lerp(-8.45, -8.66, seg(t, 12.5, 14.0)), lerp(2.56, 2.6, k), lerp(1.85, 4.45, k));
      camera.lookAt(lerp(-9.3, -9.2, k), 2.45, -1.6);
      fov = lerp(44, 40, k);
    }
    ctx.train.position.z = -400;
  } else if (shot === 'teaser') {
    // tight on a guard's eyes in the slit while a train's window light strobes across his face
    ctx.inA.group.position.set(-8.56, 1, 0.36); ctx.inB.group.position.set(-8.55, 1, -0.42);
    ctx.roomBulb.intensity = 0.0;
    const trainX = 8 * t;                                     // window band position (m), 1.75 m pitch
    const ph = ((trainX % 1.75) + 1.75) % 1.75;
    const win = smooth(ph / 0.18) * (1 - smooth((ph - 1.45) / 0.18));
    const gapDark = (t > 0.9 && t < 1.15) ? 0.15 : 1;          // car gap
    const sv = win * gapDark;
    ctx.slitSpot.intensity = 0.8 + 11 * sv; ctx.strobe.intensity = 0.05 + 0.5 * sv;
    ctx.strobe.position.z = 0.3 + (ph - 0.75) * 2.4;
    ctx.inA.head.rotation.y = -0.35 + 0.25 * seg(t, 0, 2.6); ctx.inA.head.rotation.x = 0.03;
    const k = seg(t, 0, 3.0);
    camera.position.set(lerp(-7.3, -7.5, k), lerp(2.63, 2.67, k), lerp(1.0, 0.85, k));
    camera.lookAt(-8.6, 2.7, 0.36);
    fov = lerp(15, 12.5, k);
    placeGuard(gA, -6.5, -5.2, Math.PI / 2 + 0.7); placeGuard(gB, -6.0, -7.2, Math.PI / 2 + 0.1);
    lampLevel = (l) => 0.5;
  } else if (shot === 'boots') {
    placeGuard(gA, -5.6, -20, Math.PI - 0.4); breathe(gA, 0); ctx.key.intensity = 5 * (1 - 0.7 * seg(t, 4, 7));
    placeGuard(gB, -6.6, -34, Math.PI / 2 + 0.6);
    const a = ctx.gA.arms.R; a.sh.rotation.set(0, 0, -0.17); a.el.rotation.set(-0.12, 0, 0); a.hand.rotation.set(0, 0, 0);
    ctx.gRifle.visible = true;
    const hw = new THREE.Vector3(); a.hand.updateWorldMatrix(true, false); a.hand.getWorldPosition(hw);
    ctx.gRifle.position.set(hw.x, 1.0, hw.z + 0.03); ctx.gRifle.rotation.set(0, Math.PI - 0.4, 0.04);
    gA.head.rotation.y = -0.15 + 0.2 * seg(t, 3.5, 7);
    gA.slung.visible = false;
    // train rolls in slowly
    const F = -80 + 6.5 * (t - 0.5);
    train.rotation.y = 0; train.position.set(TL, 0, F);
    headOn = 1;
    const k = seg(t, 0, 7.4);
    camera.position.set(lerp(-4.75, -5.15, k), lerp(1.22, 2.8, k), lerp(-18.1, -18.5, k));
    camera.lookAt(lerp(-5.7, -3.6, k), lerp(1.35, 2.1, k), lerp(-20.6, -45, k));
    fov = lerp(44, 38, k);
    ctx.bokeh.uniforms.focus.value = lerp(2.0, 2.0, k); ctx.bokeh.uniforms.aperture.value = lerp(0.004, 0.0012, k);
  } else if (shot === 'windows') {
    placeGuard(gA, -5.0, -20, Math.PI / 2); gA.group.visible = false;
    placeGuard(gB, -6.3, -29, Math.PI / 2 - 0.3); breathe(gB, 1);
    const v = 1.2, F0 = -19.04;
    train.rotation.y = 0; train.position.set(TL, 0, F0 + v * t);
    const lean = seg(t, 9.6, 11.6);
    const pan = 1.1 * seg(t, 5.2, 7.4) - 1.1 * seg(t, 8.2, 10.2);
    camera.position.set(-5.75 + 0.5 * lean, 2.62 - 0.05 * lean + 0.008 * Math.sin(t * 1.3), -20 + 0.1 * Math.sin(t * 0.4));
    camera.lookAt(-2.75, 2.2 - 0.3 * lean, -20.9 + pan + 0.4 * lean);
    fov = 36 - 9 * seg(t, 5.0, 6.6) * (1 - seg(t, 7.8, 9.2));
    // the starer's head keeps finding us
    const st = ctx.special.stare;
    if (st) {
      const hd = st.userData.head; hd.quaternion.identity(); train.updateMatrixWorld(true); camera.updateMatrixWorld(true);
      hd.lookAt(camera.position); const qT = hd.quaternion.clone();
      hd.quaternion.identity().slerp(qT, 0.15 + 0.85 * seg(t, 4.4, 5.6));
    }
    // glove: rises into frame, fingers twitch toward the handle, then clench and drop
    ctx.pov.visible = true;
    const up = seg(t, 9.0, 10.2) * (1 - seg(t, 12.6, 13.8));
    ctx.pov.position.set(0.2, lerp(-0.62, -0.27, up), -0.62);
    ctx.pov.rotation.set(-0.2, 0.3, -0.25);
    const tw = t > 10.2 && t < 11.8 ? 0.25 * Math.max(0, Math.sin((t - 10.2) * 11)) * Math.sin((t - 10.2) * 2) : 0;
    const cl = seg(t, 11.8, 12.3);
    ctx.fingers.forEach((f, k) => { f.f.rotation.x = -(0.25 + tw * (1 + k * 0.3) + 1.3 * cl) * f.len; f.j.rotation.x = -(0.3 + tw + 1.4 * cl); });
    ctx.thumb.rotation.x = -0.6 * cl;
  } else if (shot === 'eachother') {
    placeGuard(gA, -5.25, 18.3, -0.1); placeGuard(gB, -7.2, 20.6, Math.PI - 0.5); ctx.key.intensity = 14; ctx.fill.intensity = 4 * (0.3 + 0.7 * seg(t, 0.4, 1.4));
    breathe(gA, 0); breathe(gB, 2);
    const glance = seg(t, 0.6, 1.6) * (1 - seg(t, 3.0, 4.0));
    gA.head.rotation.y = -0.85 * glance; gA.head.rotation.x = 0.05 * glance;
    gB.head.rotation.y = -0.5 + 0.55 * seg(t, 1.9, 2.7);
    train.rotation.y = 0; train.position.set(TL, 0, 50 + TRAIN_LEN + 9 * t);
    const k = seg(t, 0, 5);
    camera.position.set(lerp(-5.75, -5.6, k), 2.55, lerp(15.6, 16.0, k));
    camera.lookAt(lerp(-5.0, -5.15, k), 2.25, 30);
    fov = 36;
  } else if (shot === 'nostop') {
    placeGuard(gA, -6.4, -6.4, Math.PI / 2 + 0.3); breathe(gA, 0); gB.group.visible = false; ctx.key.intensity = 12 * (1 - 0.6 * seg(t, 5.4, 7.6));
    const tf = 1.5, v = 16;
    const F = 5 + 0.0 - v * (t - tf);           // front passes the camera (z=5) at tf
    train.rotation.y = Math.PI; train.position.set(TL, 0, F + 0.0);
    gA.head.rotation.y = clamp(Math.atan2(F - (-6.4), 3.5) * 0.9, -1.1, 1.1) * (t > 1 ? 1 : 0.0);
    headOn = 1;
    streak = clamp((t - tf + 0.8) * 2, 0, 1) * (1 - seg(t, tf + TRAIN_LEN / v - 0.2, tf + TRAIN_LEN / v + 0.2));
    const shake = 0.012 * Math.sin(t * 37) * streak + 0.006 * Math.sin(t * 53) * streak;
    camera.position.set(-5.45, 1.28 + shake, 5 + 0.15 * t);
    camera.lookAt(-3.7 + shake, 1.95, -40);
    fov = 44;
    const dark = seg(t, 5.4, 7.6);
    lampLevel = (l) => (1 - 0.55 * dark) * (0.92 + 0.08 * Math.sin(t * 9 + l.seed)) * (dark > 0 && l.seed % 5 === 2 ? flicker(t, 6.4, l.seed) : 1);
  }
  lamps.forEach(l => setLamp(l, lampLevel(l)));
  if (shot === 'windows') lamps.forEach(l => { if (l.sx > 0) { l.halo.visible = false; l.beam.visible = false; l.bulb.visible = false; } });
  if (window.DBG) { camera.position.set(...window.DBG.p); camera.lookAt(...window.DBG.l); fov = 30; }
  if (camera.fov !== fov) { camera.fov = fov; camera.updateProjectionMatrix(); }
  // train lights
  ctx.head.intensity = (shot === 'boots' ? 14 : 30) * headOn; ctx.headBeam.material.uniforms.opacity.value = shot === 'boots' ? 0.012 : 0.03; ctx.headBeam.visible = headOn > 0;
  ctx.streakMat.opacity = 0.75 * streak;
  if (train.visible && ctx.tLights[0].visible) {
    train.updateMatrixWorld();
    const lc = train.worldToLocal(camera.position.clone());
    const sp = 3, j0 = Math.floor((lc.z + 1.5) / -sp) - 2;   // slot j at local z = -1.5 - sp*j
    for (let j = j0; j < j0 + 6; j++) {
      const L4 = ctx.tLights[((j % 4) + 4) % 4];
      const zl = -1.5 - sp * j, d = Math.abs(zl - lc.z);
      if (d >= 6) continue;
      const inTrain = zl < 0 && zl > -TRAIN_LEN;
      L4.position.set(0, 2.75, zl); L4.intensity = inTrain ? 2.5 * (1 - smooth(d / 6)) : 0;
    }
    for (const L4 of ctx.tLights) { const d = Math.abs(L4.position.z - lc.z); if (d >= 6) L4.intensity = 0; }
  }
}

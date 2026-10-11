// The signalman's escape (1980): Dieter Wendt, an East Berlin U-Bahn signal technician, fakes a signal fault in
// the tunnel near Jannowitzbrücke, flags down a West Berlin U8 train and rides it lying on the floor into the West.
// The tunnel runs along z; the technician works on the left (wall) side, x < 0. Shots 2-6 look towards +z.
// shots:
//   tunnel  (5.8 s) - slow push down a pitch-dark double-track tunnel, a few faint lamps, mist, a far amber signal
//   tech    (8.5 s) - the technician (overalls, cap, hand lamp) walks along the track, back/three-quarter view; he stops
//                     and lifts his lamp to a signal head; the camera ends close on the signal lamps and relay box
//   plan    (8.2 s) - close on the open relay box: his gloved hand pulls a fuse (~3.9 s), a spark, the relay lamp dies,
//                     camera tilts up to the signal head, whose amber/white lamps flicker and go dark (~4.5-5.6 s)
//   allowed (8.0 s) - past the dead signal he walks deeper into the tunnel; his lamp finds the enamel
//                     "Jannowitzbrücke" sign and the hectometre plate on the wall (~3.9-5.5 s)
//   flag    (5.1 s) - over his shoulder: headlights far down the tunnel grow, he steps to the track swinging his lamp,
//                     the train comes on fast and brakes hard at 4.4 s with sparks at the wheels
//   door    (6.0 s) - the train stands right in front of him, headlights glaring; the cab door swings open and the
//                     driver leans out waving him in
//   west    (7.8 s) - inside the car, camera on the floor beside him lying flat, legs of standing passengers, tunnel
//                     lamps flashing past; at ~2.6 s the train bursts into a bright West Berlin station (Moritzplatz),
//                     white light floods the carriage
//   rare    (9.2 s) - dark tunnel at a sealed ghost platform: barbed wire, a lone guard, a searchlight sweeping;
//                     the camera retreats into darkness
//   deep    (6.1 s) - slow crane up over a branching tunnel junction, many tracks fading into dark portals, amber lamps
import { AMBER, concreteTex, tileTex, canvasTex, rng, lerp } from './lib.js';
import { makeComposer, glow, beam, normalFromHeight, borderGuard, smooth, flicker } from './look.js';

const HW = 4.4, HT = 4.1, TL = -2.0, TRK = [-2.0, 2.0], WALKX = -3.72;
const WARM = 0xffc98a;
let RB = null;   // RoundedBoxGeometry class

// ---------------------------------------------------------------- helpers
const hash = (a, b = 0) => { const s = Math.sin(a * 127.1 + b * 311.7) * 43758.5453; return s - Math.floor(s); };
const clamp01 = v => v < 0 ? 0 : v > 1 ? 1 : v;
const seg = (t, a, b) => clamp01((t - a) / (b - a));

function stdF(THREE) { return (o) => new THREE.MeshStandardMaterial({ roughness: 0.85, metalness: 0, ...o }); }
function add(parent, mesh, x = 0, y = 0, z = 0) { mesh.position.set(x, y, z); parent.add(mesh); return mesh; }

function softDot(THREE) {
  const c = document.createElement('canvas'); c.width = c.height = 32; const g = c.getContext('2d');
  const gr = g.createRadialGradient(16, 16, 0, 16, 16, 16); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 32, 32); return new THREE.CanvasTexture(c);
}

function mistTex(THREE, seed) {
  const r = rng(seed);
  const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
  for (let i = 0; i < 60; i++) {
    const x = 50 + r() * 156, y = 70 + r() * 116, rad = 20 + r() * 60;
    const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, `rgba(255,255,255,${0.05 + r() * 0.07})`); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  }
  const t = new THREE.CanvasTexture(c); return t;
}
function mist(THREE, scene, x, y, z, size, op = 0.08, seed = 1, color = 0x9c8d7c) {
  const m = new THREE.SpriteMaterial({ map: mistTex(THREE, seed), color, transparent: true, opacity: op, depthWrite: false });
  const s = new THREE.Sprite(m); s.scale.set(size * 1.6, size, 1); s.position.set(x, y, z); scene.add(s);
  s.userData = { base: new THREE.Vector3(x, y, z), seed }; return s;
}

function dustCloud(THREE, scene, box, n = 900, seed = 17, size = 0.03, op = 0.5) {
  const r = rng(seed), pos = new Float32Array(n * 3), seeds = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    pos[i * 3] = lerp(box[0], box[1], r()); pos[i * 3 + 1] = lerp(box[2], box[3], r()); pos[i * 3 + 2] = lerp(box[4], box[5], r()); seeds[i] = r() * 100;
  }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const pts = new THREE.Points(geo, new THREE.PointsMaterial({ size, map: softDot(THREE), color: 0xffd9a8, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false }));
  scene.add(pts);
  return { pts, base: pos.slice(), seeds };
}
function driftDust(d, t) {
  const p = d.pts.geometry.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const s = d.seeds[i];
    p.array[i * 3] = d.base[i * 3] + Math.sin(t * 0.13 + s) * 0.22;
    p.array[i * 3 + 1] = d.base[i * 3 + 1] + Math.sin(t * 0.09 + s * 1.7) * 0.18;
    p.array[i * 3 + 2] = d.base[i * 3 + 2] + Math.cos(t * 0.11 + s) * 0.22;
  }
  p.needsUpdate = true;
}

// ---------------------------------------------------------------- textures
function wallTex(THREE, seed = 3, tone = 92) {
  const r = rng(seed);
  return canvasTex(THREE, 1024, 512, (g, w, h) => {
    g.fillStyle = `rgb(${tone},${tone - 1},${tone - 4})`; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 9000; i++) { const v = tone - 35 + r() * 70; g.fillStyle = `rgba(${v},${v},${v - 3},${0.06 + r() * 0.1})`; g.fillRect(r() * w, r() * h, 1 + r() * 3, 1 + r() * 3); }
    // formwork board lines
    for (let y = 22; y < h; y += 34 + r() * 6) { g.fillStyle = `rgba(25,24,22,${0.18 + r() * 0.15})`; g.fillRect(0, y, w, 1.5 + r() * 1.5); }
    for (let x = 0; x < w; x += 180 + r() * 120) { g.fillStyle = 'rgba(25,24,22,0.12)'; g.fillRect(x, 0, 2, h); }
    // water streaks and calcite running down
    for (let i = 0; i < 70; i++) {
      const x = r() * w, len = 80 + r() * 400, wd = 2 + r() * 14;
      const gr = g.createLinearGradient(0, 0, 0, len); const dark = r() < 0.7;
      gr.addColorStop(0, dark ? `rgba(18,16,13,${0.25 + r() * 0.3})` : `rgba(200,198,190,${0.12 + r() * 0.12})`); gr.addColorStop(1, 'rgba(18,16,13,0)');
      g.fillStyle = gr; g.fillRect(x, 0, wd, len);
    }
    // soot near the ceiling, brake dust near the floor
    let gr = g.createLinearGradient(0, 0, 0, h * 0.35); gr.addColorStop(0, 'rgba(10,9,8,0.65)'); gr.addColorStop(1, 'rgba(10,9,8,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h * 0.35);
    gr = g.createLinearGradient(0, h * 0.7, 0, h); gr.addColorStop(0, 'rgba(30,22,16,0)'); gr.addColorStop(1, 'rgba(30,22,16,0.7)'); g.fillStyle = gr; g.fillRect(0, h * 0.7, w, h * 0.3);
    for (let i = 0; i < 400; i++) { g.fillStyle = `rgba(15,13,11,${0.02 + r() * 0.04})`; g.beginPath(); g.ellipse(r() * w, r() * h, 6 + r() * 30, 4 + r() * 18, r() * 3, 0, 7); g.fill(); }
  });
}
function wallNormal(THREE, rep) {
  const r = rng(41);
  return normalFromHeight(THREE, 256, 128, (g, w, h) => {
    g.fillStyle = '#888'; g.fillRect(0, 0, w, h);
    for (let y = 5; y < h; y += 8.5) { g.fillStyle = '#333'; g.fillRect(0, y, w, 1); }
    for (let i = 0; i < 300; i++) { const v = 100 + r() * 80; g.fillStyle = `rgba(${v},${v},${v},0.5)`; g.fillRect(r() * w, r() * h, 1 + r() * 3, 1 + r() * 2); }
  }, 2.2, rep);
}

function enamelTex(THREE, lines, { w = 1024, h = 256, font = 'bold 120px "DejaVu Sans Condensed", sans-serif', sub = null, seed = 5 } = {}) {
  const r = rng(seed);
  return canvasTex(THREE, w, h, (g) => {
    g.fillStyle = '#16181c'; g.fillRect(0, 0, w, h);
    const rr = 34; g.fillStyle = '#e6e2d6';
    g.beginPath(); g.roundRect(10, 10, w - 20, h - 20, rr); g.fill();
    g.strokeStyle = '#16181c'; g.lineWidth = 9; g.beginPath(); g.roundRect(26, 26, w - 52, h - 52, rr - 12); g.stroke();
    g.fillStyle = '#16181c'; g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(lines, w / 2, sub ? h * 0.42 : h / 2 + 6);
    if (sub) { g.font = 'bold 54px "DejaVu Sans Condensed", sans-serif'; g.fillText(sub, w / 2, h * 0.78); }
    // chipped enamel and rust
    for (let i = 0; i < 26; i++) {
      const x = r() < 0.5 ? r() * w : (r() < 0.5 ? 15 + r() * 30 : w - 45 + r() * 30), y = r() < 0.6 ? (r() < 0.5 ? 14 + r() * 26 : h - 40 + r() * 26) : r() * h, s = 3 + r() * 12;
      g.fillStyle = 'rgba(70,46,26,0.8)'; g.beginPath(); g.ellipse(x, y, s * 1.5, s, r() * 3, 0, 7); g.fill();
      g.fillStyle = 'rgba(20,18,16,0.95)'; g.beginPath(); g.ellipse(x, y, s * 0.8, s * 0.55, r() * 3, 0, 7); g.fill();
    }
    for (let i = 0; i < 40; i++) { const x = r() * w; const gr = g.createLinearGradient(0, h * 0.6, 0, h); gr.addColorStop(0, 'rgba(60,40,20,0)'); gr.addColorStop(1, 'rgba(60,40,20,0.35)'); g.fillStyle = gr; g.fillRect(x, h * 0.6, 2 + r() * 5, h * 0.4); }
    for (let i = 0; i < 3000; i++) { g.fillStyle = `rgba(30,28,24,${r() * 0.07})`; g.fillRect(r() * w, r() * h, 2, 2); }
  });
}

function hectoTex(THREE) {
  return canvasTex(THREE, 192, 320, (g, w, h) => {
    g.fillStyle = '#e8e4d8'; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#111'; g.lineWidth = 10; g.strokeRect(8, 8, w - 16, h - 16);
    g.fillStyle = '#111'; g.font = 'bold 120px "DejaVu Sans", sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText('8', w / 2, h * 0.3); g.fillText('6', w / 2, h * 0.72);
    g.fillRect(30, h / 2 - 3, w - 60, 6);
    const r = rng(8); for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(40,30,20,${r() * 0.12})`; g.fillRect(r() * w, r() * h, 3, 3); }
  });
}

function plateTex(THREE, text, { w = 256, h = 96, bg = '#e6e2d6', fg = '#111', size = 56 } = {}) {
  return canvasTex(THREE, w, h, (g) => {
    g.fillStyle = bg; g.fillRect(0, 0, w, h); g.strokeStyle = fg; g.lineWidth = 6; g.strokeRect(5, 5, w - 10, h - 10);
    g.fillStyle = fg; g.font = `bold ${size}px "DejaVu Sans Condensed", sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
    const ls = text.split('\n'); ls.forEach((l, i) => g.fillText(l, w / 2, h / 2 + (i - (ls.length - 1) / 2) * size * 1.05 + 3));
  });
}

// ---------------------------------------------------------------- the technician (and other people)
// articulated figure, origin at the feet, facing +z. Returns joints so shots can pose and walk it.
function worker(THREE, { suit = 0x464b50, skin = 0x8a7c72, cap = 'work', lamp = false, shadow = true, coat = false, skirt = false, hat = true } = {}) {
  const std = stdF(THREE);
  const cloth = std({ color: suit, roughness: 0.93 });
  const clothD = std({ color: new THREE.Color(suit).multiplyScalar(0.7), roughness: 0.95 });
  const skinM = std({ color: skin, roughness: 0.65 });
  const boot = std({ color: 0x141312, roughness: 0.55 });
  const glove = std({ color: 0x2a2622, roughness: 0.8 });
  const hair = std({ color: 0x1c1915, roughness: 0.9 });
  const capM = std({ color: cap === 'driver' ? 0x1b1d22 : 0x26292c, roughness: 0.8 });
  const root = new THREE.Group();
  const M = (geo, mat, parent, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = shadow; m.receiveShadow = true; parent.add(m); return m; };
  const hips = new THREE.Group(); hips.position.y = 0.93; root.add(hips);
  M(new THREE.SphereGeometry(1, 18, 12), cloth, hips, 0, 0.02, 0).scale.set(0.175, 0.13, 0.125);
  const spine = new THREE.Group(); spine.position.y = 0.05; hips.add(spine);
  const prof = (coat
    ? [[0, -0.42], [0.25, -0.42], [0.22, -0.1], [0.18, 0.08], [0.19, 0.22], [0.205, 0.36], [0.21, 0.45], [0.19, 0.51], [0.11, 0.57], [0, 0.58]]
    : [[0, -0.02], [0.168, -0.02], [0.172, 0.08], [0.182, 0.2], [0.2, 0.34], [0.207, 0.44], [0.19, 0.51], [0.11, 0.57], [0, 0.58]]).map(([r, y]) => new THREE.Vector2(r, y));
  const torso = M(new THREE.LatheGeometry(prof, 26), cloth, spine, 0, 0, 0); torso.scale.set(1, 1, 0.66);
  if (!coat) {
    M(new THREE.CylinderGeometry(0.176, 0.176, 0.05, 24), clothD, spine, 0, 0.06, 0).scale.set(1, 1, 0.69);       // belt
    M(new THREE.BoxGeometry(0.11, 0.12, 0.02), clothD, spine, -0.08, 0.36, 0.125);                                 // chest pockets
    M(new THREE.BoxGeometry(0.11, 0.12, 0.02), clothD, spine, 0.08, 0.36, 0.125);
    M(new THREE.BoxGeometry(0.3, 0.012, 0.01), clothD, spine, 0, 0.43, -0.135);                                    // back yoke seam
    const strapM = std({ color: 0x1d1b19, roughness: 0.95 });
    const strap = M(new THREE.BoxGeometry(0.045, 0.78, 0.012), strapM, spine, 0.0, 0.22, -0.138); strap.rotation.z = -0.62;   // bag strap across the back
    const strapF = M(new THREE.BoxGeometry(0.045, 0.78, 0.012), strapM, spine, 0.0, 0.22, 0.138); strapF.rotation.z = -0.62;
    const bag = M(new RB(0.1, 0.24, 0.3, 2, 0.03), std({ color: 0x2b2722, roughness: 0.75 }), hips, -0.22, -0.06, 0.0); bag.rotation.z = 0.08;
  } else M(new THREE.BoxGeometry(0.02, 0.8, 0.01), clothD, spine, 0, 0.08, 0.13);                                   // coat closure
  M(new THREE.TorusGeometry(0.072, 0.038, 8, 20), clothD, spine, 0, 0.575, -0.005).rotation.x = Math.PI / 2;              // collar
  M(new THREE.CylinderGeometry(0.052, 0.058, 0.12, 14), skinM, spine, 0, 0.61, 0);
  const head = new THREE.Group(); head.position.set(0, 0.645, 0.012); spine.add(head);
  M(new THREE.SphereGeometry(1, 22, 16), skinM, head, 0, 0.085, 0).scale.set(0.088, 0.108, 0.098);
  M(new THREE.SphereGeometry(1, 16, 12), skinM, head, 0, 0.025, 0.02).scale.set(0.07, 0.058, 0.078);                // jaw
  M(new THREE.BoxGeometry(0.022, 0.038, 0.03), skinM, head, 0, 0.07, 0.098);                                         // nose
  for (const s of [-1, 1]) M(new THREE.SphereGeometry(1, 10, 8), skinM, head, s * 0.088, 0.075, -0.005).scale.set(0.012, 0.024, 0.018);
  M(new THREE.SphereGeometry(1, 16, 12), hair, head, 0, 0.1, -0.014).scale.set(0.092, 0.085, 0.096);               // hair
  if (hat) {
    if (cap === 'driver') {
      M(new THREE.CylinderGeometry(0.118, 0.098, 0.07, 24), capM, head, 0, 0.175, 0);
      const v = M(new THREE.CylinderGeometry(0.1, 0.1, 0.01, 20, 1, false, -Math.PI / 2, Math.PI), boot, head, 0, 0.14, 0.03); v.rotation.x = 0.25;
      M(new THREE.CylinderGeometry(0.1, 0.1, 0.012, 24), boot, head, 0, 0.145, 0);
    } else {
      M(new THREE.CylinderGeometry(0.1, 0.098, 0.065, 24), capM, head, 0, 0.16, -0.005);
      M(new THREE.SphereGeometry(1, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), capM, head, 0, 0.19, -0.005).scale.set(0.1, 0.035, 0.1);
      const v = M(new THREE.CylinderGeometry(0.095, 0.095, 0.012, 20, 1, false, -Math.PI / 2, Math.PI), capM, head, 0, 0.135, 0.045); v.rotation.x = 0.18; v.scale.set(1, 1, 1.25);
    }
  }
  const sh = [], el = [], hand = [], th = [], kn = [], bt = [];
  for (const s of [-1, 1]) {   // index 0 = right side (x < 0), 1 = left
    const a = new THREE.Group(); a.position.set(s * 0.2, 0.47, 0); spine.add(a);
    M(new THREE.SphereGeometry(0.062, 14, 10), cloth, a, 0, -0.01, 0);
    M(new THREE.CapsuleGeometry(0.056, 0.2, 4, 12), cloth, a, 0, -0.15, 0);
    const e = new THREE.Group(); e.position.y = -0.29; a.add(e);
    M(new THREE.CapsuleGeometry(0.049, 0.19, 4, 12), cloth, e, 0, -0.13, 0);
    M(new THREE.CylinderGeometry(0.052, 0.05, 0.05, 12), clothD, e, 0, -0.245, 0);
    const hd = new THREE.Group(); hd.position.y = -0.275; e.add(hd);
    M(new THREE.SphereGeometry(1, 12, 10), glove, hd, 0, -0.05, 0.005).scale.set(0.042, 0.06, 0.028);
    M(new THREE.CapsuleGeometry(0.014, 0.04, 3, 6), glove, hd, -s * 0.035, -0.04, 0.02).rotation.z = s * 0.5;
    sh.push(a); el.push(e); hand.push(hd);
    const tg = new THREE.Group(); tg.position.set(s * 0.093, -0.01, 0); hips.add(tg);
    M(new THREE.CapsuleGeometry(0.077, 0.3, 4, 12), skirt ? clothD : cloth, tg, 0, -0.21, 0);
    const k = new THREE.Group(); k.position.y = -0.44; tg.add(k);
    M(new THREE.CapsuleGeometry(skirt ? 0.045 : 0.064, 0.32, 4, 12), skirt ? skinM : cloth, k, 0, -0.2, 0);
    if (!skirt) M(new THREE.CylinderGeometry(0.068, 0.072, 0.05, 12), clothD, k, 0, -0.39, 0);
    const b = new THREE.Group(); b.position.y = -0.43; k.add(b);
    M(new RB(0.1, 0.085, 0.26, 2, 0.03), boot, b, 0, -0.012, 0.05);
    th.push(tg); kn.push(k); bt.push(b);
  }
  if (skirt) { const sk = M(new THREE.CylinderGeometry(0.2, 0.27, 0.5, 20, 1, true), clothD, hips, 0, -0.2, 0); sk.scale.set(1, 1, 0.75); sk.material.side = THREE.DoubleSide; }
  for (const s of [-1, 1]) sh[s < 0 ? 0 : 1].rotation.z = s * 0.07;
  const f = { root, hips, spine, head, sh, el, hand, th, kn, bt };
  if (lamp) f.lamp = handLamp(THREE, std);
  return f;
}

// hand lamp: hangs from the hand, warm spot pointing forward-down
function handLamp(THREE, std) {
  const g = new THREE.Group();
  const metal = std({ color: 0x3b3a37, metalness: 0.6, roughness: 0.45 });
  const handle = new THREE.Mesh(new THREE.TorusGeometry(0.045, 0.008, 8, 20, Math.PI), metal); handle.position.y = -0.06; handle.rotation.y = Math.PI / 2; g.add(handle);
  const body = new THREE.Mesh(new RB(0.12, 0.15, 0.11, 2, 0.02), metal); body.position.y = -0.135; body.castShadow = true; g.add(body);
  const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.03, 20), metal); rim.rotation.x = Math.PI / 2; rim.position.set(0, -0.13, 0.065); g.add(rim);
  const lens = new THREE.Mesh(new THREE.CircleGeometry(0.046, 20), new THREE.MeshBasicMaterial({ color: 0xffe2b0 })); lens.position.set(0, -0.13, 0.081); g.add(lens);
  const halo = glow(THREE, WARM, 0.55, 0.95); halo.position.set(0, -0.13, 0.11); g.add(halo);
  const spot = new THREE.SpotLight(WARM, 0, 16, 0.62, 0.6, 1.5);
  spot.position.set(0, -0.13, 0.08); g.add(spot);
  spot.target.position.set(0, -0.75, 2.0); g.add(spot.target);
  const bm = beam(THREE, WARM, 3.2, 1.25, 0.035); bm.position.set(0, -0.13, 0.08); g.add(bm);
  bm.lookAt(0, -0.75, 2.0); bm.rotateX(-Math.PI / 2);   // cone axis along the light
  const fill = new THREE.PointLight(WARM, 0, 3.0, 1.6); fill.position.set(0, -0.05, 0.25); g.add(fill);
  return { group: g, spot, halo, lens, beam: bm, fill };
}
function setLamp(L, v, spotI = 20) {
  L.spot.intensity = spotI * v; L.halo.material.opacity = v; L.fill.intensity = 1.2 * v;
  L.lens.material.color.setRGB(0.2 + 0.8 * v, 0.16 + 0.73 * v, 0.1 + 0.6 * v); L.beam.material.uniforms.opacity.value = 0.035 * v;
}

function walkPose(f, ph, amt = 1) {
  for (let i = 0; i < 2; i++) {
    const p = ph + i * Math.PI;
    const a = -0.42 * Math.sin(p) * amt, k = (0.07 + 0.85 * Math.pow(Math.max(0, Math.cos(p)), 1.5)) * amt;
    f.th[i].rotation.x = a; f.kn[i].rotation.x = k; f.bt[i].rotation.x = -(a + k) * 0.85 + 0.12 * Math.max(0, Math.cos(p)) * amt;
    f.sh[i].rotation.x = 0.32 * Math.sin(p) * amt; f.el[i].rotation.x = -0.18 - 0.2 * Math.max(0, -Math.sin(p)) * amt;
  }
  f.hips.position.y = 0.925 + 0.018 * Math.cos(2 * ph) * amt;
  f.hips.rotation.y = 0.07 * Math.sin(ph) * amt; f.spine.rotation.y = -0.1 * Math.sin(ph) * amt;
  f.hips.rotation.z = 0.025 * Math.sin(ph) * amt;
  f.spine.rotation.x = 0.06;
}
function standPose(f, t = 0) {
  for (let i = 0; i < 2; i++) { f.th[i].rotation.set(0, 0, (i ? 1 : -1) * 0.03); f.kn[i].rotation.x = 0.05; f.bt[i].rotation.x = -0.05; f.sh[i].rotation.x = 0.02; f.el[i].rotation.x = -0.15; }
  f.hips.position.y = 0.925 + 0.004 * Math.sin(t * 1.3); f.hips.rotation.set(0, 0, 0); f.spine.rotation.set(0.03 + 0.008 * Math.sin(t * 1.3), 0, 0);
}
// keep a lamp hanging level under a hand: counter the arm chain (x rotations only) and add a pendulum
function hangLamp(f, i, swing = 0) {
  const L = f.lamp.group; L.rotation.set(-(f.sh[i].rotation.x + f.el[i].rotation.x + f.spine.rotation.x) + swing, 0, -(f.sh[i].rotation.z));
}

// ---------------------------------------------------------------- tunnel pieces
function buildTunnel(THREE, scene, { z0 = -260, z1 = 260, gapRight = null, lamps = [] } = {}) {
  const std = stdF(THREE);
  const L = z1 - z0, zc = (z0 + z1) / 2;
  const rep = [L / 8, 1];
  const wm = std({ map: wallTex(THREE, 3, 128), normalMap: wallNormal(THREE, rep), roughness: 0.92 }); wm.map.repeat.set(...rep);
  const wallSeg = (sx, a, b) => {
    const m = std({ map: wm.map.clone(), normalMap: wm.normalMap.clone(), roughness: 0.92 }); m.map.repeat.set((b - a) / 8, 1); m.normalMap.repeat.set((b - a) / 8, 1);
    m.map.needsUpdate = m.normalMap.needsUpdate = true;
    const w = new THREE.Mesh(new THREE.PlaneGeometry(b - a, HT), m); w.position.set(sx * HW, HT / 2, (a + b) / 2); w.rotation.y = -sx * Math.PI / 2; w.receiveShadow = true; scene.add(w);
  };
  wallSeg(-1, z0, z1);
  if (gapRight) { wallSeg(1, z0, gapRight[0]); wallSeg(1, gapRight[1], z1); } else wallSeg(1, z0, z1);
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(HW * 2, L), std({ map: concreteTex(THREE, [3, L / 6], 11, 52), roughness: 0.95 }));
  ceil.rotation.x = Math.PI / 2; ceil.position.set(0, HT, zc); scene.add(ceil);
  const floorT = concreteTex(THREE, [4, L / 4], 9, 58);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(HW * 2, L), std({ map: floorT, roughness: 0.9 })); floor.rotation.x = -Math.PI / 2; floor.position.z = zc; floor.receiveShadow = true; scene.add(floor);
  // ballast-free track: sleepers in concrete, rails, third rail with cover board
  const railM = std({ color: 0x8a8a88, metalness: 1, roughness: 0.3 });
  const darkM = std({ color: 0x1a1918, roughness: 0.8 });
  const woodM = std({ color: 0x2b2722, roughness: 0.9 });
  for (const tx of TRK) {
    for (const o of [-0.72, 0.72]) {
      add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.14, L), railM), tx + o, 0.2, zc).receiveShadow = true;
      add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.03, L), darkM), tx + o, 0.125, zc);
    }
    const ox = tx + Math.sign(tx) * 1.38;   // third rail on the wall side of each track
    add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.1, L), railM), ox, 0.3, zc);
    add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.03, L), woodM), ox + Math.sign(tx) * 0.04, 0.4, zc).receiveShadow = true;
  }
  const sl = new THREE.InstancedMesh(new THREE.BoxGeometry(2.3, 0.12, 0.24), std({ color: 0x2e2c29, roughness: 0.95 }), Math.ceil(L / 0.75) * 2 + 4);
  const ins = new THREE.InstancedMesh(new THREE.BoxGeometry(0.12, 0.3, 0.12), darkM, Math.ceil(L / 5) * 2 + 4);
  const m4 = new THREE.Matrix4(); let k = 0, ki = 0;
  for (const tx of TRK) {
    for (let z = z0; z < z1; z += 0.75) { m4.makeTranslation(tx, 0.06, z); sl.setMatrixAt(k++, m4); }
    for (let z = z0; z < z1; z += 5) { m4.makeTranslation(tx + Math.sign(tx) * 1.42, 0.2, z); ins.setMatrixAt(ki++, m4); }
  }
  sl.count = k; ins.count = ki; sl.receiveShadow = true; scene.add(sl, ins);
  // centre row of riveted steel columns and the girder above them
  const steel = std({ color: 0x2c2d2e, metalness: 0.6, roughness: 0.55 });
  const nC = Math.ceil(L / 4.5) + 1;
  const web = new THREE.InstancedMesh(new THREE.BoxGeometry(0.05, HT, 0.24), steel, nC), fl = new THREE.InstancedMesh(new THREE.BoxGeometry(0.3, HT, 0.035), steel, nC * 2);
  let kc = 0, kf = 0;
  for (let z = z0 + 2; z < z1; z += 4.5) {
    if (gapRight && z > gapRight[0] - 2 && z < gapRight[1] + 2) { /* columns stay in the station too */ }
    m4.makeTranslation(0, HT / 2, z); web.setMatrixAt(kc++, m4);
    for (const o of [-0.12, 0.12]) { m4.makeTranslation(0, HT / 2, z + o); fl.setMatrixAt(kf++, m4); }
  }
  web.count = kc; fl.count = kf; web.castShadow = fl.castShadow = true; scene.add(web, fl);
  add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.38, L), steel), 0, HT - 0.19, zc);
  // cable runs on both walls: brackets every 1.2 m, six cables, a pipe higher up
  const cableM = std({ color: 0x151515, roughness: 0.55 });
  const nB = Math.ceil(L / 1.2) * 2 + 4;
  const br = new THREE.InstancedMesh(new THREE.BoxGeometry(0.14, 0.62, 0.025), std({ color: 0x4a4844, metalness: 0.5, roughness: 0.6 }), nB);
  let kb = 0;
  for (const sx of [-1, 1]) {
    for (let z = z0; z < z1; z += 1.2) {
      if (sx > 0 && gapRight && z > gapRight[0] && z < gapRight[1]) continue;
      m4.makeTranslation(sx * (HW - 0.07), 1.82, z); br.setMatrixAt(kb++, m4);
    }
    const segs = sx > 0 && gapRight ? [[z0, gapRight[0]], [gapRight[1], z1]] : [[z0, z1]];
    for (const [a, b] of segs) {
      for (let c = 0; c < 6; c++) {
        const r = 0.016 + (c % 3) * 0.006;
        const cb = new THREE.Mesh(new THREE.CylinderGeometry(r, r, b - a, 8), cableM); cb.rotation.x = Math.PI / 2;
        cb.position.set(sx * (HW - 0.13 - (c % 2) * 0.05), 1.55 + c * 0.11, (a + b) / 2); cb.receiveShadow = true; scene.add(cb);
      }
      const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, b - a, 12), std({ color: 0x2a2826, metalness: 0.4, roughness: 0.6 })); pipe.rotation.x = Math.PI / 2;
      pipe.position.set(sx * (HW - 0.12), 3.35, (a + b) / 2); scene.add(pipe);
    }
  }
  br.count = kb; scene.add(br);
  // bulkhead lamps
  const out = [];
  lamps.forEach(([sx, z, lit, withLight], i) => out.push(wallLamp(THREE, scene, std, sx, z, lit, withLight, i)));
  return out;
}

function wallLamp(THREE, scene, std, sx, z, lit, withLight, seed) {
  const g = new THREE.Group(); g.position.set(sx * (HW - 0.02), 3.0, z); g.rotation.y = -sx * Math.PI / 2; scene.add(g);
  const metal = std({ color: 0x2a2928, metalness: 0.5, roughness: 0.6 });
  add(g, new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.05, 20), metal), 0, 0, 0.025).rotation.x = Math.PI / 2;
  const dome = add(g, new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshBasicMaterial({ color: 0xffc27a })), 0, 0, 0.05); dome.rotation.x = Math.PI / 2;
  for (const a of [0, Math.PI / 2]) { const c = add(g, new THREE.Mesh(new THREE.TorusGeometry(0.105, 0.007, 6, 16, Math.PI), metal), 0, 0, 0.05); c.rotation.y = Math.PI / 2; c.rotation.x = a; }
  const halo = glow(THREE, AMBER, 1.1, 0.9); halo.position.set(0, 0, 0.18); g.add(halo);
  let light = null;
  if (withLight) { light = new THREE.PointLight(AMBER, 0, 24, 1.3); light.position.set(0, -0.2, 0.5); g.add(light); }
  return { g, dome, halo, light, lit, seed, z, sx };
}
function setWallLamp(l, v) {
  l.halo.material.opacity = v * 0.9; l.dome.material.color.setRGB(0.12 + 0.88 * v, 0.1 + 0.66 * v, 0.06 + 0.42 * v);
  if (l.light) l.light.intensity = 45.0 * v;
}

// signal head: three lamps with hoods on a black backplate, faces +z
function signalHead(THREE, std) {
  const g = new THREE.Group();
  const black = std({ color: 0x101010, roughness: 0.5, metalness: 0.2 });
  const plate = new THREE.Mesh(new RB(0.4, 0.9, 0.06, 3, 0.08), black); g.add(plate);
  const box = new THREE.Mesh(new RB(0.24, 0.8, 0.22, 2, 0.04), black); box.position.z = -0.13; g.add(box);
  const lamps = [];
  const cols = [0xffb347, 0xfff1d8, 0xffb347];
  [0.27, 0, -0.27].forEach((y, i) => {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.085, 0.014, 8, 24), std({ color: 0x2a2a2a, metalness: 0.7, roughness: 0.35 })); ring.position.set(0, y, 0.035); g.add(ring);
    const lensM = new THREE.MeshStandardMaterial({ color: 0x1a1612, roughness: 0.15, emissive: cols[i], emissiveIntensity: 0 });
    const lens = new THREE.Mesh(new THREE.SphereGeometry(0.075, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), lensM); lens.rotation.x = Math.PI / 2; lens.position.set(0, y, 0.03); lens.scale.set(1, 0.45, 1); g.add(lens);
    const hood = new THREE.Mesh(new THREE.CylinderGeometry(0.095, 0.095, 0.17, 20, 1, true, -Math.PI / 2 - 0.6, Math.PI + 1.2), new THREE.MeshStandardMaterial({ color: 0x0e0e0e, roughness: 0.6, side: THREE.DoubleSide }));
    hood.rotation.x = Math.PI / 2; hood.position.set(0, y, 0.115); g.add(hood);
    const halo = glow(THREE, cols[i], 0.42, 1.0); halo.position.set(0, y, 0.12); g.add(halo);
    lamps.push({ lensM, halo });
  });
  const num = new THREE.Mesh(new THREE.PlaneGeometry(0.3, 0.12), std({ map: plateTex(THREE, 'Jb 14', { size: 50, bg: '#8f8b80' }), roughness: 0.6 })); num.position.set(0, -0.56, 0.01); g.add(num);
  return { g, lamps };
}
function setSignal(sig, a, b, c) {
  [a, b, c].forEach((v, i) => { sig.lamps[i].lensM.emissiveIntensity = 1.1 * v; sig.lamps[i].halo.material.opacity = 0.6 * v; });
}

// relay cabinet, mounted on the left wall, opening towards +x
function relayBox(THREE, std) {
  const g = new THREE.Group();
  const grey = std({ color: 0x5b5d5c, metalness: 0.35, roughness: 0.55 });
  const inside = std({ map: canvasTex(THREE, 256, 384, (c, w, h) => {
    c.fillStyle = '#7a7871'; c.fillRect(0, 0, w, h);
    const r = rng(12);
    for (let i = 0; i < 26; i++) { c.strokeStyle = ['#1a1a1a', '#3a3a3a', '#77736a', '#2c2c2c'][i % 4]; c.lineWidth = 2 + r() * 2; c.beginPath(); const x = 20 + r() * 216; c.moveTo(x, 0); c.bezierCurveTo(x + 20, 120, x - 30, 250, 20 + r() * 216, h); c.stroke(); }
    for (let y = 300; y < 370; y += 22) { c.fillStyle = '#222'; c.fillRect(16, y, 224, 14); for (let x = 20; x < 236; x += 12) { c.fillStyle = '#9b968a'; c.fillRect(x, y + 3, 7, 8); } }
    for (let i = 0; i < 1500; i++) { c.fillStyle = `rgba(30,25,20,${r() * 0.1})`; c.fillRect(r() * w, r() * h, 3, 3); }
  }), roughness: 0.7 });
  const W = 0.72, H = 1.0, D = 0.32;
  add(g, new THREE.Mesh(new THREE.BoxGeometry(W, H, 0.02), inside), 0, 0, -D / 2 + 0.01);
  for (const s of [-1, 1]) add(g, new THREE.Mesh(new THREE.BoxGeometry(0.02, H, D), grey), s * (W / 2 - 0.01), 0, 0);
  for (const s of [-1, 1]) add(g, new THREE.Mesh(new THREE.BoxGeometry(W, 0.02, D), grey), 0, s * (H / 2 - 0.01), 0);
  add(g, new THREE.Mesh(new THREE.BoxGeometry(W + 0.06, 0.04, D + 0.05), grey), 0, H / 2 + 0.02, 0.01);   // rain lip
  // relays: grey cases with glass fronts
  const relM = std({ color: 0x3a3c3e, roughness: 0.35, metalness: 0.3 });
  const glassM = new THREE.MeshStandardMaterial({ color: 0x9a9a9a, roughness: 0.1, metalness: 0.5, transparent: true, opacity: 0.35 });
  for (let i = 0; i < 5; i++) for (let j = 0; j < 2; j++) {
    const x = -0.26 + i * 0.13, y = 0.33 - j * 0.2;
    add(g, new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.17, 0.2), relM), x, y, -0.05);
    add(g, new THREE.Mesh(new THREE.PlaneGeometry(0.09, 0.14), glassM), x, y, 0.051);
    add(g, new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.06, 0.01), std({ color: 0xb8b2a2, metalness: 0.7, roughness: 0.3 })), x, y - 0.02, 0.045);
  }
  // fuse rail: white ceramic fuse carriers, one of them gets pulled
  add(g, new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.05, 0.04), std({ color: 0x2b2b2b, metalness: 0.6 })), 0, -0.07, -0.08);
  const cer = std({ color: 0xd9d4c6, roughness: 0.4 });
  const fuses = [];
  for (let i = 0; i < 7; i++) {
    const fg = new THREE.Group(); fg.position.set(-0.27 + i * 0.09, -0.07, -0.05); g.add(fg);
    const c = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.026, 0.09, 16), cer); c.rotation.x = Math.PI / 2; c.position.z = 0.04; fg.add(c);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.025, 16), std({ color: 0x1a1a1a, roughness: 0.5 })); cap.rotation.x = Math.PI / 2; cap.position.z = 0.09; fg.add(cap);
    fuses.push(fg);
  }
  // indicator lamp and a little terminal row
  const indM = new THREE.MeshBasicMaterial({ color: 0xffb347 });
  const ind = add(g, new THREE.Mesh(new THREE.SphereGeometry(0.018, 12, 8), indM), 0.25, -0.24, 0.0);
  const indHalo = glow(THREE, AMBER, 0.22, 1.0); indHalo.position.set(0.25, -0.24, 0.03); g.add(indHalo);
  add(g, new THREE.Mesh(new THREE.PlaneGeometry(0.14, 0.06), std({ map: plateTex(THREE, 'Fahrt', { size: 54 }) })), 0.08, -0.24, -0.06);
  // wire loom hanging out of the bottom
  for (let i = 0; i < 5; i++) {
    const c = new THREE.CatmullRomCurve3([new THREE.Vector3(-0.2 + i * 0.07, -0.46, -0.08), new THREE.Vector3(-0.18 + i * 0.07, -0.62, -0.05), new THREE.Vector3(-0.15 + i * 0.05, -0.85, -0.12)]);
    add(g, new THREE.Mesh(new THREE.TubeGeometry(c, 12, 0.012, 6), std({ color: 0x151515, roughness: 0.5 })));
  }
  // door, hinged on the -x edge (towards -z in the world when mounted)
  const door = new THREE.Group(); door.position.set(-W / 2, 0, D / 2); g.add(door);
  const dp = add(door, new THREE.Mesh(new THREE.BoxGeometry(W, H, 0.025), grey), W / 2, 0, 0.0125); dp.castShadow = true;
  const paper = add(door, new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.56), std({ map: canvasTex(THREE, 256, 340, (c, w, h) => {
    c.fillStyle = '#cfc6ae'; c.fillRect(0, 0, w, h); c.strokeStyle = '#3a342a'; c.lineWidth = 2;
    const r = rng(4);
    for (let i = 0; i < 18; i++) { c.beginPath(); c.moveTo(20, 40 + i * 15); c.lineTo(60 + r() * 160, 40 + i * 15); c.stroke(); }
    for (let i = 0; i < 6; i++) c.strokeRect(30 + (i % 3) * 70, 200 + Math.floor(i / 3) * 50, 40, 30);
    c.fillStyle = '#3a342a'; c.font = 'bold 22px "DejaVu Sans Condensed"'; c.fillText('Schaltplan Sig. Jb 14', 18, 26);
  }), roughness: 0.9 })), W / 2, 0.05, -0.002); paper.rotation.y = Math.PI;
  const label = add(door, new THREE.Mesh(new THREE.PlaneGeometry(0.34, 0.1), std({ map: plateTex(THREE, 'Relais 14', { size: 48 }) })), W / 2, 0.36, 0.027);
  add(door, new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.12, 0.03), std({ color: 0x222, metalness: 0.7 })), W - 0.06, 0, 0.035);
  return { g, door, fuses, ind, indM, indHalo };
}

// ---------------------------------------------------------------- the West Berlin U8 train
function buildTrain(THREE, { cars = 3 } = {}) {
  const std = stdF(THREE);
  const g = new THREE.Group();
  const paint = std({ color: 0xa48f58, roughness: 0.42, metalness: 0.3 });
  const paintD = std({ color: 0x7c6b42, roughness: 0.5, metalness: 0.3 });
  const darkM = std({ color: 0x151515, roughness: 0.6, metalness: 0.4 });
  const glass = std({ color: 0x050607, roughness: 0.05, metalness: 0.8 });
  const inner = new THREE.MeshBasicMaterial({ color: 0xbfa98a });
  const paxTex = (() => { const c = document.createElement('canvas'); c.width = 512; c.height = 128; const gg = c.getContext('2d'); const rr = rng(3);
    for (let i = 0; i < 9; i++) { if (rr() < 0.4) continue; const x = 20 + i * 54 + rr() * 10, s = 0.8 + rr() * 0.35; gg.fillStyle = '#000';
      gg.beginPath(); gg.arc(x, 58 - 10 * s, 13 * s, 0, 7); gg.fill(); gg.beginPath(); gg.ellipse(x, 128, 26 * s, 58 * s, 0, 0, 7); gg.fill(); }
    return new THREE.CanvasTexture(c); })();
  const paxMat = new THREE.MeshBasicMaterial({ map: paxTex, transparent: true, color: 0x000000, alphaTest: 0.1 });
  const CL = 15.5, GAP = 0.7;
  const wheels = [];
  for (let i = 0; i < cars; i++) {
    const zc = -CL / 2 - i * (CL + GAP);
    const body = new THREE.Mesh(new RB(2.65, 2.55, CL, 4, 0.2), paint); body.position.set(0, 2.2, zc); body.castShadow = true; body.receiveShadow = true; g.add(body);
    add(g, new THREE.Mesh(new RB(2.3, 0.18, CL - 0.6, 2, 0.06), paintD), 0, 3.5, zc);
    add(g, new THREE.Mesh(new THREE.BoxGeometry(2.45, 0.28, CL - 1.2), darkM), 0, 0.84, zc);
    add(g, new THREE.Mesh(new THREE.BoxGeometry(2.67, 0.05, CL - 0.3), paintD), 0, 1.72, zc);     // waist line
    for (const bz of [-5.3, 5.3]) {
      add(g, new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.3, 2.5), darkM), 0, 0.62, zc + bz);
      for (const wx of [-0.72, 0.72]) for (const wz of [-0.95, 0.95]) {
        const w = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.1, 22), darkM); w.rotation.z = Math.PI / 2; w.position.set(wx, 0.6, zc + bz + wz); g.add(w);
        if (i === 0) wheels.push(new THREE.Vector3(wx, 0.24, zc + bz + wz));
      }
    }
    for (const sx of [-1, 1]) {
      const strip = new THREE.Mesh(new THREE.PlaneGeometry(CL - 1.6, 0.78), inner); strip.position.set(sx * 1.329, 2.38, zc); strip.rotation.y = sx * Math.PI / 2; g.add(strip);
      const pax = new THREE.Mesh(new THREE.PlaneGeometry(CL - 2, 0.76), paxMat); pax.position.set(sx * 1.333, 2.36, zc); pax.rotation.y = sx * Math.PI / 2; g.add(pax);
      for (let w = -CL / 2 + 1; w <= CL / 2 - 0.8; w += 1.15) add(g, new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.82, 0.12), paint), sx * 1.336, 2.38, zc + w);
      add(g, new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.06, CL - 1.4), paintD), sx * 1.337, 2.8, zc);
      add(g, new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.06, CL - 1.4), paintD), sx * 1.337, 1.97, zc);
      for (const dz of [-4.6, 0.4, 5.2]) {   // sliding double doors
        if (i === 0 && dz > 5) continue;
        add(g, new THREE.Mesh(new THREE.BoxGeometry(0.03, 2.0, 1.3), paintD), sx * 1.34, 1.95, zc + dz);
        add(g, new THREE.Mesh(new THREE.BoxGeometry(0.035, 1.9, 0.02), darkM), sx * 1.341, 1.95, zc + dz);
      }
    }
  }
  // front end
  const F = new THREE.Group(); g.add(F);
  for (const sx of [-1, 1]) {
    add(F, new THREE.Mesh(new THREE.PlaneGeometry(0.98, 0.86), glass), sx * 0.6, 2.58, 0.004);
    add(F, new THREE.Mesh(new THREE.BoxGeometry(1.04, 0.05, 0.03), darkM), sx * 0.6, 3.03, 0.01);
    add(F, new THREE.Mesh(new THREE.BoxGeometry(1.04, 0.05, 0.03), darkM), sx * 0.6, 2.13, 0.01);
  }
  add(F, new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.92, 0.03), darkM), 0, 2.58, 0.01);
  for (const sx of [-1, 1]) { const wp = add(F, new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.7, 0.02), darkM), sx * 0.6 + 0.2, 2.42, 0.03); wp.rotation.z = 0.5; }   // wipers
  const numTex = plateTex(THREE, '2741', { w: 192, h: 64, size: 44, bg: '#a48f58', fg: '#1a1a1a' });
  add(F, new THREE.Mesh(new THREE.PlaneGeometry(0.36, 0.12), std({ map: numTex, roughness: 0.5 })), -0.75, 1.88, 0.006);
  for (let i = 0; i < 5; i++) add(F, new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.02, 0.02), darkM), 0, 1.22 + i * 0.06, 0.01);   // grille
  const destTex = canvasTex(THREE, 512, 96, (c, w, h) => { c.fillStyle = '#0b0b0b'; c.fillRect(0, 0, w, h); c.fillStyle = '#f2ead8'; c.font = 'bold 60px "DejaVu Sans Condensed"'; c.textBaseline = 'middle';
    c.fillText('8', 24, h / 2 + 3); c.fillRect(70, 14, 4, h - 28); c.fillText('Leinestraße', 96, h / 2 + 3); });
  add(F, new THREE.Mesh(new THREE.PlaneGeometry(1.45, 0.27), new THREE.MeshBasicMaterial({ map: destTex, color: 0xd9d2c0 })), 0, 3.22, 0.005);
  add(F, new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.2, 0.18), darkM), 0, 1.0, 0.08);           // anticlimber
  add(F, new THREE.Mesh(new THREE.BoxGeometry(2.66, 0.04, 0.03), paintD), 0, 1.72, 0.01);
  const cpl = add(F, new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.55, 12), darkM), 0, 0.8, 0.28); cpl.rotation.x = Math.PI / 2;
  add(F, new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.24, 0.12), darkM), 0, 0.8, 0.58);
  const headGlows = [], lensMats = [];
  for (const sx of [-1, 1]) {
    const hsg = add(F, new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.1, 24), std({ color: 0x8a8a88, metalness: 1, roughness: 0.25 })), sx * 0.86, 1.36, 0.05); hsg.rotation.x = Math.PI / 2;
    const lm = new THREE.MeshBasicMaterial({ color: 0xfff6e6 }); lensMats.push(lm);
    add(F, new THREE.Mesh(new THREE.CircleGeometry(0.12, 24), lm), sx * 0.86, 1.36, 0.102);
    const hg = glow(THREE, 0xfff3e0, 2.2, 1.0); hg.position.set(sx * 0.86, 1.36, 0.3); F.add(hg); headGlows.push(hg);
    const hg2 = glow(THREE, 0xffe6c4, 7.0, 0.35); hg2.position.set(sx * 0.86, 1.36, 0.4); F.add(hg2); headGlows.push(hg2);
  }
  const headSpot = new THREE.SpotLight(0xfff2de, 0, 110, 0.42, 0.55, 1.05); headSpot.position.set(0, 1.4, 0.4); headSpot.target.position.set(0, 0.6, 40); F.add(headSpot, headSpot.target);
  const beams = [];
  for (const sx of [-1, 1]) { const b = beam(THREE, 0xfff2de, 30, 3.2, 0.03); b.rotation.x = -Math.PI / 2; b.position.set(sx * 0.86, 1.36, 0.15); F.add(b); beams.push(b); }
  // cab side door on the +x side, hinged at its front edge, swings outward
  const opening = add(g, new THREE.Mesh(new THREE.PlaneGeometry(0.78, 1.9), new THREE.MeshBasicMaterial({ map: canvasTex(THREE, 64, 128, (c, w, h) => {
    const gr = c.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#2a2016'); gr.addColorStop(0.5, '#5a4128'); gr.addColorStop(1, '#1a130c'); c.fillStyle = gr; c.fillRect(0, 0, w, h); }) })), 1.329, 2.0, -0.95);
  opening.rotation.y = Math.PI / 2;
  const door = new THREE.Group(); door.position.set(1.345, 0, -1.35); g.add(door);   // hinged at its rear edge
  add(door, new THREE.Mesh(new THREE.BoxGeometry(0.04, 1.95, 0.8), paint), 0, 2.0, 0.4).castShadow = true;
  add(door, new THREE.Mesh(new THREE.PlaneGeometry(0.55, 0.62), glass), 0.022, 2.45, 0.4).rotation.y = Math.PI / 2;
  add(door, new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.03, 0.18), darkM), 0.03, 1.85, 0.68);
  const cabLight = new THREE.PointLight(0xffc68a, 0, 3.5, 1.5); cabLight.position.set(0.9, 2.4, -1.1); g.add(cabLight);
  g.userData = { CL };
  return { group: g, door, headSpot, headGlows, beams, lensMats, wheels, opening, cabLight };
}
function setHeadlights(T, v) {
  T.headSpot.intensity = 90 * v; T.headGlows.forEach((h, i) => h.material.opacity = (i % 2 ? 0.35 : 1) * v);
  T.beams.forEach(b => b.material.uniforms.opacity.value = 0.03 * v); T.lensMats.forEach(m => m.color.setRGB(0.2 + 0.8 * v, 0.2 + 0.76 * v, 0.2 + 0.7 * v));
}

// brake sparks: deterministic particle spray from the front bogie wheels
function sparks(THREE, scene, n = 900) {
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  const pts = new THREE.Points(geo, new THREE.PointsMaterial({ size: 0.16, map: softDot(THREE), color: 0xffc070, transparent: true, opacity: 1, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
  pts.frustumCulled = false; scene.add(pts);
  const light = new THREE.PointLight(0xffa040, 0, 9, 1.4); scene.add(light);
  return { pts, n, light };
}
// emit(t) -> world position of a wheel contact (array), vel = train velocity vector (z), on = intensity 0..1
function updateSparks(S, t, wheelsAt, vz, on) {
  const p = S.pts.geometry.attributes.position; const P = 0.3;
  for (let k = 0; k < S.n; k++) {
    const b = (k / S.n) * P, c = Math.floor((t - b) / P), age = (t - b) - c * P;
    const life = 0.18 + 0.22 * hash(k, c);
    const w = wheelsAt[Math.floor(hash(k, c + 7) * wheelsAt.length) % wheelsAt.length];
    if (on <= 0.01 || age > life || hash(k, c + 3) > on) { p.array[k * 3 + 1] = -50; continue; }
    const sx = Math.sign(w.x - (-2.0)) || 1;
    const vx = sx * (1.0 + 3.2 * hash(k, c + 1)), vy = 0.6 + 3.0 * hash(k, c + 2), vzz = vz * (0.6 + 0.5 * hash(k, c + 4)) + (hash(k, c + 5) - 0.5) * 2;
    p.array[k * 3] = w.x + vx * age; p.array[k * 3 + 1] = w.y + vy * age - 4.9 * age * age; p.array[k * 3 + 2] = w.z + vzz * age;
    if (p.array[k * 3 + 1] < 0.05) p.array[k * 3 + 1] = 0.05;
  }
  p.needsUpdate = true;
  S.light.intensity = on * (14 + 8 * Math.sin(t * 53) * Math.sin(t * 31));
  if (wheelsAt.length) S.light.position.set(wheelsAt[0].x, 0.5, wheelsAt[0].z);
}

// ---------------------------------------------------------------- setup
export async function setup(THREE, renderer, W, H) {
  const shot = new URLSearchParams(location.search).get('shot') || 'tunnel';
  RB = (await import('three/addons/geometries/RoundedBoxGeometry.js')).RoundedBoxGeometry;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020202);
  scene.fog = new THREE.FogExp2(0x070605, 0.04);
  const camera = new THREE.PerspectiveCamera(40, W / H, 0.05, 600);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = stdF(THREE);
  const ctx = { THREE, scene, camera, shot, mists: [] };
  ctx.hemi = new THREE.HemisphereLight(0x8a93a3, 0x0c0b0a, 0.12); scene.add(ctx.hemi);

  if (['tunnel', 'tech', 'plan', 'allowed', 'flag', 'door'].includes(shot)) {
    scene.fog.density = 0.024; ctx.hemi.intensity = 0.9;
    // lamps: [side, z, lit, has PointLight]
    const lampSets = {
      tunnel: [[1, 4, 0.35, true], [-1, -16, 0.6, true], [1, -40, 0.5, true], [-1, -66, 0.45, true], [1, -95, 0.4, false], [-1, -130, 0.35, false]],
      tech: [[1, -16, 0.55, true], [1, 22, 0.45, true], [-1, 40, 0.4, false], [-1, -40, 0.4, false]],
      plan: [[1, -6, 0.5, true], [-1, 9, 0.55, true]],
      allowed: [[1, 2, 0.45, true], [-1, 26, 0.55, true], [1, 52, 0.4, false]],
      flag: [[1, -2, 0.45, true], [-1, 30, 0.5, true], [1, 62, 0.4, true], [-1, 100, 0.35, false]],
      door: [[1, 4, 0.5, true], [1, 30, 0.4, false], [-1, -12, 0.4, false]],
    };
    ctx.lamps = buildTunnel(THREE, scene, { z0: -260, z1: 260, lamps: lampSets[shot] });
    // the signal and its relay box near Jannowitzbrücke
    const sig = signalHead(THREE, std);
    sig.g.position.set(-3.55, 2.72, 0); sig.g.rotation.y = Math.PI; scene.add(sig.g);
    const arm = add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.86, 0.08, 0.08), std({ color: 0x1a1a1a, metalness: 0.4 })), -3.98, 2.72, 0.16);
    add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.06, 0.4), std({ color: 0x151515 })), -3.55, 3.2, 0.1);
    ctx.sig = sig;
    const rb = relayBox(THREE, std); rb.g.position.set(-HW + 0.17, 1.45, -1.9); rb.g.rotation.y = Math.PI / 2; scene.add(rb.g); ctx.rb = rb;
    // conduit from box up to the signal
    const cc = new THREE.CatmullRomCurve3([new THREE.Vector3(-HW + 0.1, 1.95, -1.9), new THREE.Vector3(-HW + 0.08, 2.5, -1.2), new THREE.Vector3(-HW + 0.1, 2.72, -0.2)]);
    add(scene, new THREE.Mesh(new THREE.TubeGeometry(cc, 16, 0.025, 8), std({ color: 0x1b1b1b, roughness: 0.5 })));
    // the enamel station sign and hectometre plate further on
    const sign = add(scene, new THREE.Mesh(new THREE.PlaneGeometry(1.9, 0.48), std({ map: enamelTex(THREE, 'Jannowitzbrücke', { sub: '◄ 300 m', seed: 9 }), roughness: 0.25, metalness: 0.1 })), -HW + 0.015, 2.6, 8.2);
    sign.rotation.y = Math.PI / 2;
    for (const dz of [-0.9, 0.9]) add(scene, new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.02, 8), std({ color: 0x222 })), -HW + 0.03, 2.6, 8.2 + dz).rotation.z = Math.PI / 2;
    const hm = add(scene, new THREE.Mesh(new THREE.PlaneGeometry(0.22, 0.36), std({ map: hectoTex(THREE), roughness: 0.4 })), -HW + 0.015, 1.15, 4.6); hm.rotation.y = Math.PI / 2;
    // a second, distant signal (amber) for depth
    const s2 = signalHead(THREE, std); s2.g.position.set(-3.55, 2.72, -95); scene.add(s2.g); setSignal(s2, 0.9, 0, 0); ctx.sig2 = s2;
    const s3 = signalHead(THREE, std); s3.g.position.set(-3.55, 2.72, 120); s3.g.rotation.y = Math.PI; scene.add(s3.g); setSignal(s3, 0.8, 0, 0); ctx.sig3 = s3;
    s2.g.scale.setScalar(1.3); s3.g.scale.setScalar(1.3);

    if (shot !== 'tunnel') {
      const f = worker(THREE, { lamp: true }); scene.add(f.root); ctx.f = f;
      f.hand[1].add(f.lamp.group); f.lamp.group.position.set(0, -0.06, 0.01);
      f.lamp.spot.castShadow = true; f.lamp.spot.shadow.mapSize.set(1024, 1024); f.lamp.spot.shadow.bias = -0.0006; f.lamp.spot.shadow.camera.near = 0.1;
    }
    if (shot === 'flag' || shot === 'door') {
      const T = buildTrain(THREE, { cars: 3 }); T.group.rotation.y = Math.PI; T.group.position.set(TL, 0, 300); scene.add(T.group); ctx.T = T;
      if (shot === 'door') {
        const d = worker(THREE, { suit: 0x2a2c30, cap: 'driver', shadow: false }); ctx.driver = d; T.group.add(d.root);
        d.root.position.set(0.98, 0.98, -1.0); d.root.rotation.y = Math.PI / 2;
      }
      ctx.sp = sparks(THREE, scene);
    }
    const dbox = { tunnel: [-4, 4, 0.3, 4, -60, 2], tech: [-4.3, 0, 0.2, 3.6, -16, 4], plan: [-4.3, -1.5, 0.3, 3.4, -4, 1], allowed: [-4.3, 0, 0.2, 3.8, -4, 14],
      flag: [-4.3, 1, 0.2, 3.8, 4, 40], door: [-4.3, 0, 0.2, 3.8, 4, 16] }[shot];
    ctx.dust = dustCloud(THREE, scene, dbox, 900, 17, shot === 'plan' ? 0.012 : 0.025, 0.45);
    // mist banks around the lamps and down the tunnel
    const r = rng(5);
    for (let i = 0; i < 16; i++) ctx.mists.push(mist(THREE, scene, lerp(-3, 3, r()), 1.0 + r() * 2.4, (shot === 'tunnel' ? -150 : -40) + i * (shot === 'tunnel' ? 10 : 9), 5 + r() * 4, 0.05 + r() * 0.04, i + 1));
  } else if (shot === 'west') {
    await buildWest(THREE, scene, ctx, std);
  } else if (shot === 'rare') {
    buildRare(THREE, scene, ctx, std);
  } else if (shot === 'deep') {
    buildDeep(THREE, scene, ctx, std);
  }

  const dof = { tech: null, plan: { focus: 1.7, aperture: 0.006, maxblur: 0.01 }, door: null, west: { focus: 2.2, aperture: 0.004, maxblur: 0.01 } }[shot] ?? null;
  const post = makeComposer(THREE, renderer, scene, camera, W, H, { bloom: shot === 'west' ? 0.55 : 0.85, bloomRadius: 0.75, bloomThreshold: shot === 'west' ? 0.8 : 0.55, exposure: shot === 'west' ? 0.95 : 1.2, dof });
  Object.assign(ctx, post);
  return ctx;
}

// ---------------------------------------------------------------- shot 7: inside the car, into West Berlin
async function buildWest(THREE, scene, ctx, std) {
  scene.fog = new THREE.FogExp2(0x070605, 0.008);
  const car = new THREE.Group(); scene.add(car);
  const XI = 1.25, LEN = 16, TOP = 2.2;
  const panel = std({ color: 0x8a8476, roughness: 0.6 });
  const panelD = std({ color: 0x4a4740, roughness: 0.6 });
  const metal = std({ color: 0xa9a9a6, metalness: 0.9, roughness: 0.25 });
  const floorTex = canvasTex(THREE, 256, 256, (g, w, h) => { g.fillStyle = '#3d3b37'; g.fillRect(0, 0, w, h); const r = rng(2);
    for (let y = 0; y < h; y += 16) { g.fillStyle = '#2d2b28'; g.fillRect(0, y, w, 5); }
    for (let i = 0; i < 1200; i++) { g.fillStyle = `rgba(${r() < 0.5 ? 20 : 120},${r() < 0.5 ? 18 : 110},16,${r() * 0.12})`; g.fillRect(r() * w, r() * h, 2 + r() * 4, 2 + r() * 3); } }, [3, 18]);
  const floorN = normalFromHeight(THREE, 128, 128, (g, w, h) => { g.fillStyle = '#fff'; g.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 8) { g.fillStyle = '#000'; g.fillRect(0, y, w, 3); } }, 1.5, [3, 18]);
  const fl = add(car, new THREE.Mesh(new THREE.PlaneGeometry(XI * 2, LEN), std({ map: floorTex, normalMap: floorN, roughness: 0.75 }))); fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true;
  // walls with window openings (so outside light comes through as moving patches)
  const box = (w, h, d, x, y, z, m, cast = true) => { const b = add(car, new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m), x, y, z); b.castShadow = cast; b.receiveShadow = true; return b; };
  const doors = [-4.6, 4.6];
  for (const sx of [-1, 1]) {
    const x = sx * (XI + 0.04);
    box(0.08, 0.92, LEN, x, 0.46, 0, panel);
    box(0.08, TOP - 1.85, LEN, x, (1.85 + TOP) / 2, 0, panel);
    for (let z = -LEN / 2; z <= LEN / 2 + 0.01; z += 1.25) box(0.08, 0.95, 0.14, x, 1.4, z, panel);
    // windows: thin glass
    add(car, new THREE.Mesh(new THREE.PlaneGeometry(LEN, 0.93), new THREE.MeshStandardMaterial({ color: 0x0b0d0e, roughness: 0.05, metalness: 0.2, transparent: true, opacity: 0.18 })), x + sx * 0.035, 1.4, 0).rotation.y = -sx * Math.PI / 2;
    // longitudinal benches between the doors
    for (const [a, b] of [[-LEN / 2 + 0.2, -5.5], [-3.7, 3.7], [5.5, LEN / 2 - 0.2]]) {
      const zc = (a + b) / 2, l = b - a;
      box(0.46, 0.1, l, sx * (XI - 0.25), 0.45, zc, std({ color: 0x5a5146, roughness: 0.8 }));
      box(0.08, 0.45, l, sx * (XI - 0.06), 0.72, zc, std({ color: 0x5a5146, roughness: 0.8 }));
      box(0.4, 0.4, l, sx * (XI - 0.28), 0.2, zc, panelD);
      for (const zz of [a + 0.05, b - 0.05]) { const p = add(car, new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, TOP, 10), metal), sx * (XI - 0.5), TOP / 2, zz); p.castShadow = true; }
    }
    const rail = add(car, new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, LEN, 8), metal), sx * 0.75, 1.95, 0); rail.rotation.x = Math.PI / 2;
  }
  box(XI * 2 + 0.2, 0.06, LEN, 0, TOP + 0.03, 0, std({ color: 0xc9c4b6, roughness: 0.7 }));
  box(XI * 2 + 0.2, TOP, 0.08, 0, TOP / 2, -LEN / 2 - 0.04, panel);
  box(XI * 2 + 0.2, TOP, 0.08, 0, TOP / 2, LEN / 2 + 0.04, panel);
  // end door window into the next car, dim
  add(car, new THREE.Mesh(new THREE.PlaneGeometry(0.6, 1.0), new THREE.MeshBasicMaterial({ color: 0x2a2218 })), 0, 1.4, -LEN / 2 + 0.005);
  // ceiling light boxes
  const lampM = new THREE.MeshBasicMaterial({ color: 0xf3e6cc });
  ctx.ceilLamps = lampM;
  for (const sx of [-1, 1]) for (let z = -LEN / 2 + 1.2; z < LEN / 2; z += 2.6) add(car, new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.04, 1.6), lampM), sx * 0.5, TOP - 0.02, z);
  ctx.inLights = [];
  for (const z of [-5, 0.5, 5]) { const l = new THREE.PointLight(0xffe7c2, 0, 7, 1.5); l.position.set(0, TOP - 0.15, z); car.add(l); ctx.inLights.push(l); }

  // him, lying face down in the aisle, head towards the camera
  const f = worker(THREE, { lamp: true }); ctx.f = f; car.add(f.root);
  f.hand[1].add(f.lamp.group); setLamp(f.lamp, 0);
  f.root.rotation.x = Math.PI / 2; f.root.position.set(-0.12, 0.15, 1.2);
  f.root.rotation.z = 0.05;
  for (let i = 0; i < 2; i++) { f.th[i].rotation.set(0.04, 0, (i ? 1 : -1) * 0.1); f.kn[i].rotation.x = 0.12; f.bt[i].rotation.x = 1.15; }
  // arms bent up beside the head, elbows out, lying flat on the floor
  f.sh[0].rotation.set(0.1, 0, -2.55); f.el[0].rotation.set(0, 0, 1.35);
  f.sh[1].rotation.set(0.1, 0, 2.55); f.el[1].rotation.set(0, 0, -1.35);
  f.head.rotation.set(0, 1.15, 0);
  f.spine.rotation.set(0, 0, 0); f.hips.rotation.set(0, 0, 0);
  car.remove(f.root); car.add(f.root);
  f.hand[1].remove(f.lamp.group); car.add(f.lamp.group); f.lamp.group.position.set(0.45, 0.2, 1.6); f.lamp.group.rotation.set(0, 0.5, 0);
  // passengers
  const pax = [];
  const P = (x, z, ry, o) => { const p = worker(THREE, o); p.root.position.set(x, 0, z); p.root.rotation.y = ry; car.add(p.root); standPose(p); pax.push(p); return p; };
  const a = P(0.58, 1.05, -2.4, { suit: 0x2c2b29, coat: true, cap: 'work', hat: false }); a.sh[0].rotation.x = -0.1;
  const b = P(-0.75, 0.2, 1.0, { suit: 0x6b665d, skirt: true, coat: true, hat: false });
  const c = P(0.6, -1.6, -2.6, { suit: 0x3a3a40, coat: true, hat: true, cap: 'driver' });
  const d = P(-0.5, -3.4, 0.6, { suit: 0x55524c, hat: false });
  const e = P(0.4, -6.0, -2.8, { suit: 0x2a2a2a, coat: true, hat: false });
  // hands on the overhead rail
  [a, c, e].forEach(p => { p.sh[1].rotation.x = -2.9; p.el[1].rotation.x = -0.2; });
  // seated passengers
  const seated = (x, z, ry, o) => { const p = worker(THREE, o); p.root.position.set(x, 0.0, z); p.root.rotation.y = ry; car.add(p.root);
    p.hips.position.y = 0.52; for (let i = 0; i < 2; i++) { p.th[i].rotation.x = -1.45; p.kn[i].rotation.x = 1.5; p.bt[i].rotation.x = 0; p.sh[i].rotation.x = -0.45; p.el[i].rotation.x = -0.9; } return p; };
  seated(-0.86, -2.0, Math.PI / 2, { suit: 0x403d38, coat: true, hat: false });
  seated(0.86, -0.4, -Math.PI / 2, { suit: 0x6e6a62, skirt: true, hat: false });
  seated(-0.86, 5.6, Math.PI / 2, { suit: 0x2e2e2e, hat: false });
  seated(0.86, -4.2, -Math.PI / 2, { suit: 0x504a40, coat: true, hat: false });
  // a briefcase and a shopping bag on the floor
  add(car, new THREE.Mesh(new RB(0.42, 0.3, 0.1, 2, 0.02), std({ color: 0x2a1f16, roughness: 0.5 })), 0.95, 0.15, 2.3).rotation.y = 0.3;
  add(car, new THREE.Mesh(new RB(0.3, 0.36, 0.18, 2, 0.04), std({ color: 0x9a9384, roughness: 0.9 })), -0.65, 0.18, -0.6);
  ctx.pax = pax;

  // outside world: moves along +z as the train drives towards -z
  const out = new THREE.Group(); scene.add(out); ctx.out = out;
  const v0 = 12, tb = 2.2;
  const S = t => t < tb ? v0 * t : v0 * tb + v0 * 1.7 * (1 - Math.exp(-(t - tb) / 1.7));
  ctx.S = S;
  const A = -8 - S(2.6);    // station leading edge (outside coords) reaches the car front at t = 2.6
  ctx.A = A;
  const STL = 110;
  const twall = std({ map: wallTex(THREE, 6, 70), roughness: 0.95 }); twall.map.repeat.set(6, 1);
  // tunnel walls and roof before the station (they shade the car from the station lights)
  for (const sx of [-1, 1]) {
    const w = add(out, new THREE.Mesh(new THREE.BoxGeometry(0.3, 4, 300), twall), sx * 2.1, 1.0, A + 150); w.castShadow = true; w.receiveShadow = true;
    const w2 = add(out, new THREE.Mesh(new THREE.BoxGeometry(0.3, 4, 100), twall), sx * 2.1, 1.0, A - STL - 50); w2.castShadow = true;
  }
  const roof = add(out, new THREE.Mesh(new THREE.BoxGeometry(6, 0.3, 300), twall), 0, 3.0, A + 150); roof.castShadow = true;
  const roof2 = add(out, new THREE.Mesh(new THREE.BoxGeometry(6, 0.3, 100), twall), 0, 3.0, A - STL - 50); roof2.castShadow = true;
  // tunnel lamps flashing past
  ctx.tlamps = [];
  for (let z = A + 4; z < A + 260; z += 7.5) for (const sx of [-1, 1]) {
    if (sx < 0 && Math.round(z) % 2) continue;
    const h = glow(THREE, AMBER, 0.9, 0.95); h.position.set(sx * 1.92, 1.55, z); out.add(h);
    const b = add(out, new THREE.Mesh(new THREE.SphereGeometry(0.06, 10, 8), new THREE.MeshBasicMaterial({ color: 0xffd09a })), sx * 1.94, 1.55, z);
    ctx.tlamps.push(z);
  }
  // one shadowed spot rides with whichever tunnel lamp is passing the windows
  const ls = new THREE.SpotLight(0xffb870, 0, 9, 0.9, 0.6, 1.3); ls.castShadow = true; ls.shadow.mapSize.set(1024, 1024); ls.shadow.bias = -0.0008;
  scene.add(ls, ls.target); ctx.ls = ls;
  // the station: Moritzplatz, bright, white tiles, adverts, people waiting
  const st = new THREE.Group(); out.add(st); st.position.z = A - STL / 2;
  const tiles = std({ map: tileTex(THREE, { repeat: [40, 4], tile: 32, base: 226, vary: 10, dirt: 0.08, seed: 21 }), roughness: 0.3 });
  const plat = add(st, new THREE.Mesh(new THREE.BoxGeometry(7, 1, STL), std({ map: concreteTex(THREE, [3, 40], 22, 168), roughness: 0.6 })), 1.45 + 3.5, -0.56, 0); plat.receiveShadow = true;
  add(st, new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.02, STL), std({ color: 0xf0ede2 })), 1.6, -0.05, 0);
  add(st, new THREE.Mesh(new THREE.PlaneGeometry(STL, 5), tiles), 8.9, 1.9, 0).rotation.y = -Math.PI / 2;
  add(st, new THREE.Mesh(new THREE.PlaneGeometry(STL, 5), tiles), -5.4, 1.9, 0).rotation.y = Math.PI / 2;
  const ceilS = add(st, new THREE.Mesh(new THREE.PlaneGeometry(15, STL), std({ color: 0xd8d6cf, roughness: 0.8 })), 1.75, 4.0, 0); ceilS.rotation.x = Math.PI / 2;
  const tubeM = new THREE.MeshBasicMaterial({ color: 0xffffff });
  for (const x of [-2.5, 3.2, 6.6]) add(st, new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.06, STL - 4), tubeM), x, 3.95, 0);
  for (let z = -STL / 2 + 4; z < STL / 2; z += 7) {
    add(st, new THREE.Mesh(new THREE.BoxGeometry(0.4, 4.6, 0.4), tiles), 4.6, 1.7, z).castShadow = false;
  }
  // adverts and station name plates on the back wall
  const ads = [
    ['WANNSEE', 'Sommer in Berlin'], ['Berliner Bank', 'Ihr Geld in guten Händen'], ['KINO', 'Heute 20 Uhr'], ['Zigaretten', 'extra mild'],
  ];
  ads.forEach(([h1, h2], i) => {
    const tex = canvasTex(THREE, 256, 340, (g, w, h) => {
      g.fillStyle = ['#e9e3d2', '#20242a', '#c9b48a', '#f2efe8'][i]; g.fillRect(0, 0, w, h);
      g.fillStyle = ['#202020', '#f0ebe0', '#1a1a1a', '#202020'][i];
      if (i === 0) { g.beginPath(); g.arc(w / 2, 120, 60, 0, 7); g.fill(); g.fillStyle = '#e9e3d2'; g.fillRect(0, 150, w, 8); g.fillRect(0, 168, w, 6); g.fillStyle = '#202020'; }
      if (i === 2) { g.fillRect(30, 40, w - 60, 140); }
      if (i === 3) { g.fillRect(90, 50, 76, 150); g.fillStyle = '#f2efe8'; g.fillRect(96, 60, 64, 20); g.fillStyle = '#202020'; }
      g.font = 'bold 40px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.fillText(h1, w / 2, 250);
      g.font = '24px "DejaVu Serif"'; g.fillText(h2, w / 2, 292);
    });
    for (let z = -STL / 2 + 6 + i * 9; z < STL / 2 - 4; z += 36) {
      const p = add(st, new THREE.Mesh(new THREE.PlaneGeometry(1.5, 2.0), std({ map: tex, roughness: 0.5 })), 8.88, 1.6, z); p.rotation.y = -Math.PI / 2;
    }
  });
  const nameTex = canvasTex(THREE, 1024, 180, (g, w, h) => { g.fillStyle = '#e8e6df'; g.fillRect(0, 0, w, h); g.fillStyle = '#1b1f26'; g.fillRect(14, 14, w - 28, h - 28);
    g.fillStyle = '#f4f2ea'; g.font = 'bold 110px "DejaVu Sans Condensed"'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('Moritzplatz', w / 2, h / 2 + 4); });
  for (let z = -STL / 2 + 12; z < STL / 2; z += 22) {
    add(st, new THREE.Mesh(new THREE.PlaneGeometry(3.6, 0.64), new THREE.MeshBasicMaterial({ map: nameTex, color: 0xe0ddd4 })), 8.87, 2.9, z).rotation.y = -Math.PI / 2;
    add(st, new THREE.Mesh(new THREE.PlaneGeometry(3.6, 0.64), new THREE.MeshBasicMaterial({ map: nameTex, color: 0xe0ddd4 })), -5.38, 2.9, z + 9).rotation.y = Math.PI / 2;
  }
  // people waiting on the platform
  const rr = rng(33);
  for (let i = 0; i < 9; i++) {
    const p = worker(THREE, { suit: [0x2b2b2b, 0x5d5850, 0x3c3b38, 0x77716a, 0x232323][i % 5], coat: rr() < 0.7, skirt: rr() < 0.35, hat: rr() < 0.3, cap: 'driver', shadow: false });
    standPose(p); p.root.position.set(2.6 + rr() * 3.4, -0.06, -STL / 2 + 8 + i * 11 + rr() * 4); p.root.rotation.y = -Math.PI / 2 + (rr() - 0.5) * 1.2; st.add(p.root);
  }
  // station light: a bright directional key from the platform side; the tunnel roof/walls shade it until the station arrives
  const sun = new THREE.DirectionalLight(0xf4f1ea, 0); sun.position.set(9, 6.5, 0); sun.target.position.set(0, 0, 0);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -12, right: 12, top: 12, bottom: -12, near: 0.5, far: 40 }); sun.shadow.bias = -0.0006;
  scene.add(sun, sun.target); ctx.sun = sun;
  const fillW = new THREE.PointLight(0xf2f0ea, 0, 14, 1.2); fillW.position.set(3.0, 1.6, 0); scene.add(fillW); ctx.fillW = fillW;
  ctx.dust = dustCloud(THREE, scene, [-1.2, 1.2, 0.05, 2.1, -8, 5], 500, 23, 0.012, 0.4);
  ctx.car = car;
}

// ---------------------------------------------------------------- shot 8: the ghost platform
function buildRare(THREE, scene, ctx, std) {
  scene.fog = new THREE.FogExp2(0x060505, 0.035);
  const z0 = -66, z1 = -22;
  ctx.lamps = buildTunnel(THREE, scene, { z0: -220, z1: 120, gapRight: [z0, z1], lamps: [[-1, -8, 0.3, false], [-1, -90, 0.3, false]] });
  const PW = 4.2, X0 = HW - 1.0, X1 = X0 + PW;   // platform from x=3.4 to 7.6
  const tiles = std({ map: tileTex(THREE, { repeat: [16, 2], base: 150, vary: 22, dirt: 0.9, seed: 8 }), roughness: 0.45 });
  const L = z1 - z0, zc = (z0 + z1) / 2;
  const plat = add(scene, new THREE.Mesh(new THREE.BoxGeometry(PW, 1.0, L), std({ map: concreteTex(THREE, [2, 12], 5, 88), roughness: 0.8 })), X0 + PW / 2, 0.5, zc); plat.receiveShadow = true;
  add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.02, L), std({ color: 0xbab5a8 })), X0 + 0.15, 1.01, zc);
  const bw = add(scene, new THREE.Mesh(new THREE.PlaneGeometry(L, HT), tiles), X1, HT / 2, zc); bw.rotation.y = -Math.PI / 2; bw.receiveShadow = true;
  const ceil = add(scene, new THREE.Mesh(new THREE.PlaneGeometry(PW + 1, L), std({ map: concreteTex(THREE, [2, 10], 12, 50) })), X0 + PW / 2, HT, zc); ceil.rotation.x = Math.PI / 2;
  for (const z of [z0, z1]) { const e = add(scene, new THREE.Mesh(new THREE.PlaneGeometry(PW + 1.1, HT), std({ map: wallTex(THREE, 4, 80) })), X0 + PW / 2 - 0.5, HT / 2, z); e.rotation.y = z === z0 ? 0 : Math.PI; }
  // station name on the wall, faded
  const nm = enamelTex(THREE, 'Jannowitzbrücke', { seed: 14 });
  for (const z of [-55, -33]) add(scene, new THREE.Mesh(new THREE.PlaneGeometry(3.2, 0.8), std({ map: nm, roughness: 0.5 })), X1 - 0.01, 2.7, z).rotation.y = -Math.PI / 2;
  // a bricked-up stair opening
  const brick = std({ map: canvasTex(THREE, 256, 256, (g, w, h) => { g.fillStyle = '#4a4744'; g.fillRect(0, 0, w, h); const r = rng(6);
    for (let y = 0; y < h; y += 16) for (let x = (y / 16) % 2 ? -16 : 0; x < w; x += 32) { const v = 70 + r() * 40; g.fillStyle = `rgb(${v},${v - 4},${v - 8})`; g.fillRect(x + 1, y + 1, 30, 14); } }, [2, 2]) });
  add(scene, new THREE.Mesh(new THREE.PlaneGeometry(3, 2.6), brick), X1 - 0.02, 2.3, -44).rotation.y = -Math.PI / 2;
  // columns on the platform
  const steel = std({ color: 0x2a2b2c, metalness: 0.6, roughness: 0.5 });
  for (let z = z0 + 4; z < z1; z += 6) add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.3, HT - 1, 0.3), steel), X0 + 2.0, 1 + (HT - 1) / 2, z).castShadow = true;
  // barbed wire coils along the platform edge
  const wireM = std({ color: 0x6a6a68, metalness: 0.8, roughness: 0.4 });
  const pts = [];
  for (let i = 0; i <= 1600; i++) { const u = i / 1600, a = u * Math.PI * 2 * 90; pts.push(new THREE.Vector3(X0 + 0.45 + Math.cos(a) * 0.3, 1.32 + Math.sin(a) * 0.3, z0 + 1 + u * (L - 2) + Math.sin(a) * 0.06)); }
  const coil = add(scene, new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 3000, 0.008, 4), wireM)); coil.castShadow = true;
  for (let z = z0 + 2; z < z1; z += 3) add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.05, 1.0, 0.05), wireM), X0 + 0.45, 1.5, z);
  // dim platform bulbs
  ctx.pl = [];
  for (const z of [-58, -44, -30]) {
    const b = add(scene, new THREE.Mesh(new THREE.SphereGeometry(0.06, 10, 8), new THREE.MeshBasicMaterial({ color: 0xffd09a })), X0 + 2.0, HT - 0.5, z);
    const h = glow(THREE, AMBER, 1.3, 0.9); h.position.copy(b.position); scene.add(h);
    const l = new THREE.PointLight(AMBER, 3.0, 9, 1.6); l.position.copy(b.position); scene.add(l);
    const bm = beam(THREE, AMBER, 3.4, 1.3, 0.05); bm.position.copy(b.position); scene.add(bm);
    ctx.pl.push({ b, h, l, bm });
  }
  // the guard
  const gm = std({ color: 0x0e0e0e, roughness: 0.95 });
  const gd = borderGuard(THREE, gm); gd.group.position.set(X0 + 1.4, 1.0, -40); gd.group.rotation.y = -Math.PI / 2 + 0.35; scene.add(gd.group); ctx.guard = gd;
  // searchlight on a stand at the platform end, sweeping across the tracks
  const sl = new THREE.Group(); sl.position.set(X0 + 0.9, 2.3, -27); scene.add(sl);
  add(scene, new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.06, 1.3, 10), steel), X0 + 0.9, 1.65, -27);
  const yoke = new THREE.Group(); sl.add(yoke);
  const drum = add(yoke, new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.25, 0.42, 24), steel)); drum.rotation.x = Math.PI / 2;
  const lensS = add(yoke, new THREE.Mesh(new THREE.CircleGeometry(0.2, 24), new THREE.MeshBasicMaterial({ color: 0xfff4e2 })), 0, 0, 0.215);
  const sg = glow(THREE, 0xfff1dc, 2.4, 1.0); sg.position.set(0, 0, 0.35); yoke.add(sg);
  const sspot = new THREE.SpotLight(0xfff0d8, 220, 70, 0.11, 0.35, 1.0); sspot.position.set(0, 0, 0.25); yoke.add(sspot); sspot.target.position.set(0, 0, 20); yoke.add(sspot.target);
  sspot.castShadow = true; sspot.shadow.mapSize.set(1024, 1024); sspot.shadow.bias = -0.0005;
  const sb = beam(THREE, 0xfff2de, 45, 2.6, 0.11); sb.rotation.x = -Math.PI / 2; sb.position.set(0, 0, 0.25); yoke.add(sb);
  ctx.search = { yoke, sg, sspot, sb };
  ctx.dust = dustCloud(THREE, scene, [-4, 7, 0.3, 4, -60, 10], 1400, 19, 0.035, 0.5);
  const r = rng(9);
  for (let i = 0; i < 12; i++) ctx.mists.push(mist(THREE, scene, lerp(-3, 6, r()), 1.2 + r() * 2, -70 + i * 6, 6 + r() * 3, 0.06, i + 3));
}

// ---------------------------------------------------------------- shot 9: the junction
function buildDeep(THREE, scene, ctx, std) {
  scene.fog = new THREE.FogExp2(0x060504, 0.022);
  const HH = 9;
  const floor = add(scene, new THREE.Mesh(new THREE.PlaneGeometry(120, 120), std({ map: concreteTex(THREE, [20, 20], 9, 50), roughness: 0.95 })), 0, 0, -20); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true;
  const ceil = add(scene, new THREE.Mesh(new THREE.PlaneGeometry(120, 120), std({ map: concreteTex(THREE, [12, 12], 11, 45) })), 0, HH, -20); ceil.rotation.x = Math.PI / 2;
  const railM = std({ color: 0x9a9a98, metalness: 1, roughness: 0.28 });
  const slM = std({ color: 0x2c2a27, roughness: 0.95 });
  const conc = std({ map: wallTex(THREE, 12, 84), roughness: 0.92 });
  // track paths: two tracks enter from the camera side and fan out into seven tunnel mouths
  const R = 46, N = 7;
  const paths = [];
  for (let i = 0; i < N; i++) {
    const u = (i - (N - 1) / 2) / ((N - 1) / 2), ang = u * 0.62;
    const px = Math.sin(ang) * R, pz = -Math.cos(ang) * R + 6;
    const sx = i < N / 2 ? -2 : 2;
    const c = new THREE.CubicBezierCurve3(new THREE.Vector3(sx, 0, 30), new THREE.Vector3(sx, 0, 6), new THREE.Vector3(px - Math.sin(ang) * 20, 0, pz + Math.cos(ang) * 20), new THREE.Vector3(px, 0, pz));
    const tail = new THREE.LineCurve3(new THREE.Vector3(px, 0, pz), new THREE.Vector3(px + Math.sin(ang) * 140, 0, pz - Math.cos(ang) * 140));
    paths.push({ c, tail, ang, px, pz });
  }
  // sample rails and sleepers as instances
  const segs = [];
  const sample = (curve, step) => { const L = curve.getLength(), n = Math.ceil(L / step); for (let k = 0; k < n; k++) { const p = curve.getPointAt(k / n), q = curve.getPointAt(Math.min(1, (k + 1) / n)); segs.push([p, q]); } };
  paths.forEach(p => { sample(p.c, 0.6); sample(p.tail, 0.6); });
  const railI = new THREE.InstancedMesh(new THREE.BoxGeometry(0.07, 0.14, 1), railM, segs.length * 2);
  const slI = new THREE.InstancedMesh(new THREE.BoxGeometry(2.3, 0.12, 0.24), slM, segs.length);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3(), pos = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0);
  let k = 0, ks = 0;
  for (const [p, qq] of segs) {
    const d = qq.clone().sub(p); const len = d.length(); if (len < 1e-4) continue;
    const yaw = Math.atan2(d.x, d.z); q.setFromAxisAngle(up, yaw);
    const side = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
    for (const o of [-0.72, 0.72]) { pos.copy(p).addScaledVector(d, 0.5).addScaledVector(side, o); pos.y = 0.2; sc.set(1, 1, len + 0.02); m4.compose(pos, q, sc); railI.setMatrixAt(k++, m4); }
    pos.copy(p); pos.y = 0.06; sc.set(1, 1, 1); m4.compose(pos, q, sc); slI.setMatrixAt(ks++, m4);
  }
  railI.count = k; slI.count = ks; slI.receiveShadow = railI.receiveShadow = true; scene.add(railI, slI);
  // tunnel mouths: portal frames, tubes behind them, wall panels between
  ctx.jl = [];
  const portals = [];
  paths.forEach((p, i) => {
    const g = new THREE.Group(); g.position.set(p.px, 0, p.pz); g.rotation.y = -p.ang; scene.add(g);   // local -z = into the tunnel
    const TW = 5.0, TH = 4.6, TL2 = 150;
    const inner = std({ map: wallTex(THREE, 20 + i, 70), roughness: 0.95, side: THREE.BackSide }); inner.map.repeat.set(TL2 / 8, 1);
    const tube = add(g, new THREE.Mesh(new THREE.BoxGeometry(TW, TH, TL2), inner), 0, TH / 2, -TL2 / 2);
    // portal frame
    add(g, new THREE.Mesh(new THREE.BoxGeometry(TW + 1.4, 0.9, 0.8), conc), 0, TH + 0.45, 0);
    for (const s of [-1, 1]) add(g, new THREE.Mesh(new THREE.BoxGeometry(0.7, TH, 0.8), conc), s * (TW / 2 + 0.35), TH / 2, 0);
    // wall above
    add(g, new THREE.Mesh(new THREE.BoxGeometry(TW + 1.4, HH - TH - 0.9, 0.6), conc), 0, (HH + TH + 0.9) / 2, -0.1);
    // amber lamp over each mouth, and lamps receding inside
    const b = add(g, new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 8), new THREE.MeshBasicMaterial({ color: 0xffd09a })), 0, TH + 1.25, 0.6);
    const h = glow(THREE, AMBER, 2.0, 0.9); h.position.copy(b.position); g.add(h);
    const l = new THREE.PointLight(AMBER, 0, 14, 1.5); l.position.set(0, TH + 1.0, 1.2); g.add(l);
    const bm = beam(THREE, AMBER, 5.4, 2.2, 0.045); bm.position.copy(b.position); g.add(bm);
    ctx.jl.push({ l, h, seed: i });
    for (let d = 14; d < 130; d += 16 + (i % 3) * 3) {
      const hh = glow(THREE, AMBER, 1.0, 0.75); hh.position.set((d / 16) % 2 ? -TW / 2 + 0.2 : TW / 2 - 0.2, 3.3, -d); g.add(hh);
      if (d < 20 && i % 2 === 0) { const ll = new THREE.PointLight(AMBER, 2.2, 8, 1.6); ll.position.copy(hh.position); g.add(ll); }
    }
    portals.push(g);
    // the label plate above each mouth: track number
    const pl = add(g, new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.45), std({ map: plateTex(THREE, String(i + 1), { w: 128, h: 96, size: 64 }), roughness: 0.4 })), 0, TH + 0.45, 0.41);
  });
  for (let i = 0; i < N - 1; i++) {
    const a = portals[i], b = portals[i + 1];
    const pa = new THREE.Vector3(3.2, 0, 0).applyMatrix4(a.matrixWorld.compose(a.position, a.quaternion, new THREE.Vector3(1, 1, 1)));
    const pb = new THREE.Vector3(-3.2, 0, 0).applyMatrix4(b.matrixWorld.compose(b.position, b.quaternion, new THREE.Vector3(1, 1, 1)));
    const mid = pa.clone().add(pb).multiplyScalar(0.5), len = pa.distanceTo(pb);
    if (len > 0.1) { const w = add(scene, new THREE.Mesh(new THREE.BoxGeometry(len + 0.2, HH, 0.6), conc), mid.x, HH / 2, mid.z); w.rotation.y = -Math.atan2(pb.z - pa.z, pb.x - pa.x); }
  }
  // outer walls of the hall
  for (const s of [-1, 1]) add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.6, HH, 60), conc), s * 32, HH / 2, 0);
  // column grid
  const steel = std({ color: 0x2b2c2d, metalness: 0.6, roughness: 0.5 });
  for (let x = -24; x <= 24; x += 8) for (let z = -26; z <= 18; z += 9) {
    if (Math.abs(x) < 4 && z > 0) continue;
    const ok = paths.every(p => { const d = p.c.getSpacedPoints(30).reduce((m, v) => Math.min(m, Math.hypot(v.x - x, v.z - z)), 99); return d > 2.2; });
    if (!ok) continue;
    const c = add(scene, new THREE.Mesh(new THREE.BoxGeometry(0.45, HH, 0.45), steel), x, HH / 2, z); c.castShadow = true;
  }
  // hanging lamps over the hall
  const hl = [[-6, -6], [7, -12], [0, 8], [-14, -16]];
  hl.forEach(([x, z], i) => {
    add(scene, new THREE.Mesh(new THREE.CylinderGeometry(0.01, 0.01, 2.2), steel), x, HH - 1.1, z);
    const b = add(scene, new THREE.Mesh(new THREE.SphereGeometry(0.08, 10, 8), new THREE.MeshBasicMaterial({ color: 0xffd09a })), x, HH - 2.3, z);
    const shade = add(scene, new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.22, 20, 1, true), std({ color: 0x222, side: THREE.DoubleSide })), x, HH - 2.18, z);
    const h = glow(THREE, AMBER, 1.6, 0.9); h.position.copy(b.position); scene.add(h);
    const bm = beam(THREE, AMBER, 6.5, 2.6, 0.05); bm.position.copy(b.position); scene.add(bm);
    if (i < 3) { const l = new THREE.PointLight(AMBER, 0, 16, 1.4); l.position.copy(b.position); scene.add(l); ctx.jl.push({ l, h, seed: 10 + i }); }
  });
  ctx.dust = dustCloud(THREE, scene, [-14, 14, 0.3, 8, -30, 22], 1600, 29, 0.05, 0.45);
  const r = rng(13);
  for (let i = 0; i < 14; i++) ctx.mists.push(mist(THREE, scene, lerp(-25, 25, r()), 0.8 + r() * 3, -38 + r() * 30, 9 + r() * 6, 0.06, i + 7));
}

// ---------------------------------------------------------------- update
export function update(ctx, t) {
  const { THREE, camera, shot, f } = ctx;
  if (ctx.dust) driftDust(ctx.dust, t);
  ctx.mists.forEach(m => { const b = m.userData.base; m.position.set(b.x + Math.sin(t * 0.12 + m.userData.seed) * 0.6, b.y + Math.sin(t * 0.08 + m.userData.seed * 2) * 0.15, b.z); m.material.rotation = t * 0.02 * (m.userData.seed % 2 ? 1 : -1); });
  if (ctx.lamps) ctx.lamps.forEach(l => setWallLamp(l, l.lit * (0.92 + 0.08 * Math.sin(t * 7 + l.seed) * Math.sin(t * 2.3 + l.seed * 3))));
  if (ctx.sig) setSignal(ctx.sig, 0.95, 0.9, 0);

  if (shot === 'tunnel') {
    const k = smooth(t / 8);
    camera.fov = 42; camera.updateProjectionMatrix();
    camera.position.set(lerp(-1.75, -1.6, k), lerp(1.8, 1.65, k), lerp(14, 2, k) - t * 0.25);
    camera.lookAt(lerp(-1.9, -1.5, k), 1.6, -100);
    camera.rotation.z += 0.004 * Math.sin(t * 0.4);
    // one lamp stutters
    const l = ctx.lamps[1]; setWallLamp(l, l.lit * (t > 2.0 && t < 2.7 ? flicker(t, 2.0, 3) : 1));
    setSignal(ctx.sig, 0, 0, 0);
  } else if (shot === 'tech') {
    // walks from z=-15 towards the signal, stops at z=-3.1 around 5.4 s, lifts the lamp
    const v = 1.25, ts1 = 4.6, zStart = -3.0 - v * (ts1 + 1), ts = ts1 + 1;
    const u = Math.min(Math.max(t - ts1, 0), 2);
    const dist = t < ts1 ? v * t : v * ts1 + v * (u - u * u / 4);
    const z = zStart + dist;
    const moving = t < ts1 ? 1 : 1 - u / 2;
    f.root.position.set(WALKX, 0, z); f.root.rotation.y = 0.05;
    walkPose(f, dist / 1.4 * Math.PI * 2, 0.15 + 0.85 * moving);
    if (moving < 0.99) { const s = 1 - moving; for (let i = 0; i < 2; i++) { f.th[i].rotation.x *= moving; f.kn[i].rotation.x = lerp(0.05, f.kn[i].rotation.x, moving); f.bt[i].rotation.x *= moving; } }
    // lamp arm: carried low and forward, later raised towards the signal head
    const lift = smooth(seg(t, 5.4, 6.8));
    f.sh[1].rotation.x = lerp(-0.3 + 0.06 * Math.sin(dist * 4.5), -2.1, lift); f.el[1].rotation.x = lerp(-0.75, -0.45, lift); f.sh[1].rotation.z = lerp(0.12, 0.1, lift);
    f.head.rotation.x = lerp(0.12, -0.42, smooth(seg(t, 4.8, 6.4))); f.head.rotation.y = lerp(0, 0.18, smooth(seg(t, 4.8, 6.4)));
    hangLamp(f, 1, (1 - lift) * 0.12 * Math.sin(dist * 4.5));
    if (lift > 0) { f.lamp.group.rotation.x = lerp(f.lamp.group.rotation.x, f.lamp.group.rotation.x - 0.5, lift); f.lamp.group.rotation.y = -0.5 * lift; }
    setLamp(f.lamp, 1);
    // camera: follows behind and to the track side, then pushes past to the signal head and relay box
    const k1 = smooth(seg(t, 0, 5.2)), k2 = smooth(seg(t, 4.2, 9.5));
    const fz = z;
    const pFollow = new THREE.Vector3(-2.45, 1.7, fz - 4.3), lFollow = new THREE.Vector3(-3.55, 1.05, fz + 4);
    const pEnd = new THREE.Vector3(-1.35, 1.75, -5.6), lEnd = new THREE.Vector3(-3.7, 2.0, -1.3);
    camera.position.lerpVectors(pFollow, pEnd, k2); camera.position.y += 0.015 * Math.sin(t * 1.7);
    const look = new THREE.Vector3().lerpVectors(lFollow, lEnd, k2); camera.lookAt(look);
    camera.fov = lerp(40, 34, k2); camera.updateProjectionMatrix();
    setSignal(ctx.sig, 0.95, 0.9, 0);
  } else if (shot === 'plan') {
    // he stands at the open relay box (lamp held up in his left hand), right hand pulls a fuse at ~3.9 s
    f.root.position.set(-3.45, 0, -1.6); f.root.rotation.y = -Math.PI / 2 + 0.05; standPose(f, t);
    f.spine.rotation.x = 0.1; f.head.rotation.set(lerp(0.3, -0.35, smooth(seg(t, 4.3, 5.2))), lerp(-0.25, 0.2, smooth(seg(t, 4.3, 5.2))), 0);
    if (f.lamp.group.parent !== f.hand[1]) { f.hand[1].add(f.lamp.group); f.lamp.group.position.set(0, -0.06, 0.01); }
    const raise = smooth(seg(t, 4.4, 5.3));
    f.sh[1].rotation.set(lerp(-1.1, -1.9, raise), 0, 0.25); f.el[1].rotation.x = lerp(-0.7, -0.4, raise);
    f.lamp.group.rotation.set(-(f.sh[1].rotation.x + f.el[1].rotation.x + f.spine.rotation.x) - lerp(0.25, 0.8, raise), lerp(-0.5, -0.2, raise), 0);
    // right arm: reach (2.3-3.6), grip, pull (3.85-4.25), hold
    const reach = smooth(seg(t, 2.3, 3.6)), pull = smooth(seg(t, 3.85, 4.25));
    f.sh[0].rotation.set(lerp(0.0, -1.32, reach) + 0.28 * pull, 0, lerp(-0.07, 0.05, reach));
    f.el[0].rotation.x = lerp(-0.2, -0.12, reach) - 0.5 * pull;
    setLamp(f.lamp, 1, 7);
    // fuse #3 slides out with the hand
    const fu = ctx.rb.fuses[3]; fu.position.z = -0.05 + 0.13 * pull; fu.rotation.x = 0.25 * pull;
    ctx.rb.door.rotation.y = -1.9;
    const dead = t > 4.18;
    // the signal dies: amber and white flicker out after the fuse leaves
    const fl = (seed, a) => t < a ? 1 : t > a + 1.3 ? 0 : (hash(Math.floor((t - a) * 20), seed) > 0.3 + (t - a) * 0.5 ? 0.85 : 0.04);
    setSignal(ctx.sig, fl(1, 4.6), fl(2, 4.75), 0);
    const ind = dead ? 0 : 1; ctx.rb.indM.color.setRGB(0.1 + 0.9 * ind, 0.08 + 0.62 * ind, 0.05 + 0.23 * ind); ctx.rb.indHalo.material.opacity = ind;
    // spark at the contact
    if (!ctx.spk) { ctx.spk = glow(THREE, 0xffd7a0, 0.5, 1); ctx.rb.g.add(ctx.spk); ctx.spk.position.set(-0.27 + 3 * 0.09, -0.07, 0.03); }
    ctx.spk.material.opacity = t > 4.12 && t < 4.3 ? (1 - (t - 4.12) / 0.18) * (0.6 + 0.4 * Math.sin(t * 200)) : 0;
    // camera: close on the box from his right, then tilts up to the signal head as it dies
    const k = smooth(seg(t, 4.0, 5.0));
    camera.position.set(lerp(-2.75, -2.6, k), lerp(1.5, 1.45, k), lerp(-3.05, -3.25, k) + 0.1 * t / 8);
    const look = new THREE.Vector3(lerp(-4.0, -3.6, k), lerp(1.38, 2.6, k), lerp(-1.85, -0.1, k));
    camera.lookAt(look);
    camera.fov = lerp(38, 42, k); camera.updateProjectionMatrix();
    if (ctx.bokeh) ctx.bokeh.uniforms.focus.value = camera.position.distanceTo(look);
  } else if (shot === 'allowed') {
    setSignal(ctx.sig, 0, 0, 0); ctx.rb.door.rotation.y = 0;
    const lookF = tt => smooth(seg(tt, 3.4, 4.3)) * (1 - smooth(seg(tt, 6.0, 7.0)));
    let dist = 0; for (let q = 0; q < t; q += 0.02) dist += 0.02 * 1.3 * (1 - 0.75 * lookF(q));
    const z = -1.2 + dist;
    f.root.position.set(WALKX, 0, z); f.root.rotation.y = 0.04;
    walkPose(f, dist / 1.4 * Math.PI * 2, 1 - 0.5 * lookF(t));
    // looks up at the enamel sign and lifts the lamp to it as he passes
    const look = lookF(t);
    f.head.rotation.y = 0.55 * look; f.head.rotation.x = -0.35 * look;
    f.sh[1].rotation.x = lerp(-0.3, -1.95, look) + 0.05 * Math.sin(t * 6); f.el[1].rotation.x = lerp(-0.75, -0.35, look); f.sh[1].rotation.z = lerp(0.12, 0.0, look);
    hangLamp(f, 1, 0.1 * Math.sin(t * 5.8) * (1 - look));
    f.lamp.group.rotation.x -= 0.6 * look; f.lamp.group.rotation.y = -0.38 * look;
    setLamp(f.lamp, 1);
    // camera starts on the dead signal and dollies after him
    const k = smooth(seg(t, 0, 8));
    camera.position.set(lerp(-2.3, -2.45, k), lerp(2.25, 2.05, k), lerp(-4.2, 2.4, k));
    const tgt = new THREE.Vector3(lerp(-3.4, -3.9, k), lerp(1.9, 2.15, smooth(seg(t, 0.5, 3.5))), lerp(1.5, 9.5, smooth(seg(t, 0.3, 5.0))));
    camera.lookAt(tgt);
    camera.fov = 40; camera.updateProjectionMatrix();
  } else if (shot === 'flag') {
    setSignal(ctx.sig, 0, 0, 0);
    const T = ctx.T;
    // train front position (z), heading -z
    const tb = 4.4, v0 = 24, dec = 10;
    let zf, vz;
    if (t < tb) { zf = 150 - v0 * t; vz = -v0; } else { const d = t - tb, tt = Math.min(d, v0 / dec); zf = 150 - v0 * tb - (v0 * tt - 0.5 * dec * tt * tt); vz = -(v0 - dec * tt); }
    T.group.position.set(TL, 0, zf);
    setHeadlights(T, smooth(seg(t, 0.2, 1.0)));
    // he steps to the track side and swings the lamp across the track
    const step = smooth(seg(t, 0.6, 1.6));
    f.root.position.set(lerp(-3.85, -3.62, step), 0, 10 + 0.3 * step); f.root.rotation.y = lerp(0.05, 0.2, step);
    standPose(f, t);
    const ph = (t - 0.5) * 1.05 * Math.PI * 2;
    if (step < 1 && step > 0) walkPose(f, step * Math.PI * 2, 0.5 * Math.sin(step * Math.PI));
    const up = smooth(seg(t, 0.8, 1.6));
    const swing = Math.sin(ph) * up;
    f.sh[1].rotation.set(lerp(-0.2, -1.5, up), 0, 0.07 + 0.75 * swing); f.el[1].rotation.x = lerp(-0.4, -0.15, up);
    f.spine.rotation.z = 0.04 * swing; f.head.rotation.set(0.05, -0.1, 0);
    f.lamp.group.rotation.set(-(f.sh[1].rotation.x + f.el[1].rotation.x + f.spine.rotation.x), 0, -f.sh[1].rotation.z * 0.7);
    setLamp(f.lamp, 1);
    // the other arm braces / waves
    f.sh[0].rotation.set(lerp(0, -0.3, up), 0, -0.15 * up);
    // brake sparks from the front bogie
    const br = t > tb ? 1 : 0;
    const wheelsW = T.wheels.slice(0, 8).map(w => new THREE.Vector3(TL - w.x, w.y, zf - w.z));
    updateSparks(ctx.sp, t, wheelsW, vz * 0.4, br * (vz < -0.5 ? 1 : 0));
    // camera: over his shoulder, a gentle push; shakes as the train arrives
    const k = smooth(seg(t, 0, 6));
    const near = clamp01(1 - (zf - 10) / 50);
    const shake = near * 0.02 * (Math.sin(t * 37) + Math.sin(t * 53.7));
    camera.position.set(lerp(-2.6, -2.75, k) + shake, lerp(1.55, 1.5, k) + shake * 0.5, lerp(5.6, 6.4, k));
    camera.lookAt(lerp(-2.6, -2.8, k), 1.65, 40);
    camera.fov = 44; camera.updateProjectionMatrix();
  } else if (shot === 'door') {
    setSignal(ctx.sig, 0, 0, 0);
    const T = ctx.T; T.group.position.set(TL, 0, 14.6 + 0.12 * Math.exp(-t * 3) * Math.sin(t * 9));
    setHeadlights(T, 1); T.headSpot.intensity = 14; T.beams.forEach(b => b.material.uniforms.opacity.value = 0.012); T.headGlows.forEach((h, i) => { if (i % 2) h.material.opacity = 0.15; });
    updateSparks(ctx.sp, t, [], 0, 0);
    f.root.position.set(-4.0, 0, 9.6); f.root.rotation.y = 0.22; standPose(f, t);
    f.sh[1].rotation.set(-0.35, 0, 0.1); f.el[1].rotation.x = -0.5; hangLamp(f, 1, 0.05 * Math.sin(t * 2));
    f.head.rotation.set(-0.05, 0.25 * smooth(seg(t, 1.4, 2.4)), 0);
    f.sh[0].rotation.set(-0.2 * smooth(seg(t, 0.5, 1.2)), 0, -0.12);
    setLamp(f.lamp, 1);
    // cab door swings open 1.0-2.0 s; driver leans out and waves him in
    const open = smooth(seg(t, 1.0, 2.0));
    T.door.rotation.y = 1.75 * open;
    T.cabLight.intensity = 3 * open;
    const d = ctx.driver; standPose(d, t);
    const lean = smooth(seg(t, 1.6, 2.6));
    d.root.position.x = lerp(1.0, 1.36, lean);
    d.spine.rotation.x = lerp(0.0, 0.42, lean); d.head.rotation.set(-0.1, -0.35 * lean, 0);
    const wave = smooth(seg(t, 2.4, 2.9));
    const beck = Math.sin((t - 2.6) * 7.0);
    d.sh[0].rotation.set(lerp(0, -1.55, wave), 0, lerp(-0.07, 0.25 + 0.3 * beck * wave, wave)); d.el[0].rotation.x = lerp(-0.2, -0.3 - 0.9 * (0.5 + 0.5 * beck), wave);
    d.sh[1].rotation.set(-0.5, 0, 0.2); d.el[1].rotation.x = -0.6;
    // camera low along the wall side, slow push
    const k = smooth(seg(t, 0, 9));
    const kk = smooth(seg(t, 0.5, 7.5));
    camera.position.set(lerp(-3.5, -3.3, kk), lerp(1.55, 1.75, kk), lerp(4.4, 6.9, kk));
    camera.lookAt(lerp(-3.2, -3.45, kk), lerp(2.05, 2.35, kk), 16.5);
    camera.fov = lerp(42, 33, kk); camera.updateProjectionMatrix();
  } else if (shot === 'west') {
    const S = ctx.S(t), v = t < 2.2 ? 12 : 12 * Math.exp(-(t - 2.2) / 1.7);
    ctx.out.position.z = S;
    // how much station light reaches us: the station's leading edge passes the car front at 2.6 s
    const lead = ctx.A + S;     // world z of the station's leading edge
    const inSt = clamp01((lead + 8) / 16);
    ctx.sun.intensity = 7.5 * smooth(seg(lead, -9, -2));
    ctx.fillW.intensity = 14 * inSt;
    ctx.hemi.intensity = 0.1 + 0.55 * inSt;
    ctx.ceilLamps.color.setRGB(0.95, 0.9, 0.8);
    ctx.inLights.forEach((l, i) => l.intensity = 2.2 * (0.95 + 0.05 * Math.sin(t * 50 + i)));
    // passing tunnel lamp drives the shadowed spot
    const ls = ctx.ls; let best = null;
    for (const z of ctx.tlamps) { const wz = z + S; if (wz > -9 && wz < 9 && (best === null || Math.abs(wz - 1) < Math.abs(best - 1))) best = wz; }
    if (best !== null && lead < -8) { ls.position.set(1.9, 1.6, best); ls.target.position.set(-1.0, 0.0, best + 1.0); ls.intensity = 18 * clamp01(1 - Math.abs(best - 1) / 9); }
    else ls.intensity = 0;
    // passengers sway with the train
    const sway = 0.03 * Math.sin(t * 2.1) * (v / 12) + (t > 2.2 && t < 5 ? -0.04 * Math.exp(-(t - 2.2)) : 0);
    ctx.pax.forEach((p, i) => { p.root.rotation.z = sway * (i % 2 ? 1 : -1) * 0.6; p.spine.rotation.x = 0.03 + sway * 0.8; });
    f.root.position.y = 0.14 + 0.004 * Math.sin(t * 23) * (v / 12);
    // camera on the floor beside his head, vibrating, slight push and tilt up as the light floods in
    const k = smooth(seg(t, 0, 9));
    const vib = (v / 12) * 0.006 * (Math.sin(t * 41) + Math.sin(t * 67.3));
    camera.position.set(0.42 + vib, 0.3 + vib, lerp(4.3, 4.0, k));
    camera.lookAt(lerp(-0.35, -0.3, k), lerp(0.62, 0.78, k), -2.5);
    camera.fov = 52; camera.updateProjectionMatrix();
    if (ctx.bokeh) ctx.bokeh.uniforms.focus.value = 2.6;
    ctx.renderer && 0;
  } else if (shot === 'rare') {
    // searchlight sweeps across the tracks; camera retreats into the dark
    const s = ctx.search;
    const a = Math.sin(t * 0.55 - 0.6);
    s.yoke.rotation.set(0.12 + 0.05 * Math.sin(t * 0.9), Math.PI + 0.25 + a * 0.75, 0);
    const k = smooth(seg(t, 0, 11));
    camera.position.set(lerp(-1.1, -1.25, k), lerp(1.75, 1.55, k), lerp(-8, 6, k));
    camera.lookAt(lerp(3.6, 3.2, k), lerp(1.8, 1.7, k), -42);
    camera.fov = 40; camera.updateProjectionMatrix();
    ctx.guard.head.rotation.y = 0.4 * Math.sin(t * 0.55 - 1.2);
    const dim = 1 - 0.55 * smooth(seg(t, 6.5, 9.8));
    ctx.pl.forEach((p, i) => { const v = dim * (0.92 + 0.08 * Math.sin(t * 9 + i)); p.l.intensity = 3.0 * v; p.h.material.opacity = 0.9 * v; p.bm.material.uniforms.opacity.value = 0.05 * v; });
  } else if (shot === 'deep') {
    const k = smooth(seg(t, 0, 8.5));
    camera.position.set(lerp(-1.5, 1.2, k), lerp(0.9, 6.8, k), lerp(22, 9, k));
    camera.lookAt(lerp(-0.5, 0.5, k), lerp(1.6, 1.0, k), -40);
    camera.fov = 44; camera.updateProjectionMatrix();
    ctx.jl.forEach(j => { const v = 0.9 + 0.1 * Math.sin(t * 6 + j.seed * 2) * Math.sin(t * 1.7 + j.seed); j.l.intensity = 5.5 * v; j.h.material.opacity = 0.9 * v; });
  }
}

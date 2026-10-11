// France 2026: the "STRATA lycée", a 1960s concrete secondary school shown as a dollhouse cutaway.
// 1 unit = 1 m. Building runs along x (-18..18), back wall at z = -8, the cut (front façade) at z = 0, yard and gate at z > 0.
// Three floors x four rooms:
//   F0: toilet block | entrance hall | classroom | classroom (chairs up)
//   F1: CROWDED class of 36 | EMPTY teacher's desk | lesson with a teacher | classroom
//   F2: LEAK (stained ceiling, missing tile, bucket, rat) | HEAT (thermometer, low sun) | peeling class | dark room, cracked window
// All people are faceless mannequins (france_lib.figure).
// shots (?shot=):
//   cut              (8 s) night, 3/4 view. 0-1.4 intact façade, 1.4-5.6 an amber slice line sweeps left to right and
//                          the façade falls away, revealing the lit rooms. Slow push-in throughout.
//   crowded          (6 s) high angle into the class of 36; desks light amber one by one (0.6-4.2 s), 36 at the end.
//   empty_desk       (6 s) low across the pupils' heads to the teacher's desk; an amber pool of light fades up on the
//                          empty desk and chair (1.0-2.6 s), dust in the beam.
//   leak             (7 s) stained ceiling, a missing tile, drips into a bucket and a puddle, the fallen tile, a rat
//                          crossing along the wall (2-6 s). Amber rim light on the drips and bucket.
//   heat             (6 s) wall thermometer climbs from 24 to 38 °C (0.6-4.4 s) in low amber sun through the windows.
//   toilets          (6 s) broken toilet block: hanging stall door, cracked mirror, taped "HORS SERVICE", flickering tube,
//                          puddle; amber light picks out the taped stall.
//   outside_blockade (7 s) street level at the gate: wheelie bins and barriers piled against it, pallets, pupils with
//                          banners; sodium street light. Slow lateral dolly.
import { AMBER, canvasTex, rng, tileTex } from './lib.js';
import { makeComposer, glow, beam } from './look.js';
import { AMBER_HI, shotArgs, path, clamp01, sstep, fontsReady, figure } from './france_lib.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const RX = [-18, -9, 0, 9];          // room x0 (rooms are 9 m wide)
const FY = (f) => f * 3.4 + 0.3;      // floor top of storey f
const DEPTH = 8;                      // room depth (z from -8 to 0)

export async function setup(THREE, renderer, W, H) {
  const { name: shot } = shotArgs('cut');
  await fontsReady();
  const scene = new THREE.Scene();
  const outside = shot === 'outside_blockade';
  scene.background = new THREE.Color(0x07080a);
  scene.fog = outside ? new THREE.FogExp2(0x0a0b0d, 0.028) : shot === 'cut' ? new THREE.FogExp2(0x07080a, 0.008) : new THREE.FogExp2(0x07080a, 0.02);
  const camera = new THREE.PerspectiveCamera(shot === 'cut' ? 30 : 38, W / H, 0.05, 400);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.localClippingEnabled = true;
  const R = rng(1960);
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.88, metalness: 0, ...o });
  const add = (geo, mat, x, y, z, parent = scene) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; parent.add(m); return m; };
  const box = (w, h, d, mat, x, y, z, parent) => add(new THREE.BoxGeometry(w, h, d), mat, x, y, z, parent);

  // ------------------------------------------------------------------ textures
  const T = (w, h, draw, rep = [1, 1]) => canvasTex(THREE, w, h, draw, rep);
  const concreteExt = T(1024, 1024, (g, w, h) => {
    g.fillStyle = 'rgb(128,126,120)'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 16000; i++) { const v = 90 + R() * 80; g.fillStyle = `rgba(${v},${v},${v - 4},${0.1 + R() * 0.15})`; g.fillRect(R() * w, R() * h, 1 + R() * 3, 1 + R() * 3); }
    for (let i = 0; i < 120; i++) { const x = R() * w, len = 60 + R() * 500, a = 0.08 + R() * 0.25; const grd = g.createLinearGradient(0, 0, 0, len);
      grd.addColorStop(0, `rgba(40,36,30,${a})`); grd.addColorStop(1, 'rgba(40,36,30,0)'); g.save(); g.translate(0, R() * h * 0.6); g.fillStyle = grd; g.fillRect(x, 0, 2 + R() * 9, len); g.restore(); }
    g.strokeStyle = 'rgba(60,58,54,0.7)'; g.lineWidth = 3; for (let x = 0; x <= w; x += 256) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); }   // panel joints
    for (let i = 0; i < 14; i++) { g.strokeStyle = `rgba(30,28,26,${0.4 + R() * 0.4})`; g.lineWidth = 1.2; g.beginPath(); let x = R() * w, y = R() * h; g.moveTo(x, y);
      for (let k = 0; k < 9; k++) { x += (R() - 0.5) * 40; y += R() * 30; g.lineTo(x, y); } g.stroke(); }
  });
  const wallTex = (peel, stains, seed) => {
    const r = rng(seed);
    return T(1024, 700, (g, w, h) => {
      const dado = h * (1 - 1.15 / 3.0);
      g.fillStyle = '#a69f90'; g.fillRect(0, 0, w, dado); g.fillStyle = '#6c7468'; g.fillRect(0, dado, w, h - dado);
      g.fillStyle = '#5d6158'; g.fillRect(0, dado - 4, w, 8);
      for (let i = 0; i < 9000; i++) { const v = r() * 40 - 20; g.fillStyle = `rgba(${100 + v},${96 + v},${88 + v},0.06)`; g.fillRect(r() * w, r() * h, 2 + r() * 4, 2 + r() * 4); }
      for (let i = 0; i < 30; i++) { const x = r() * w; g.fillStyle = 'rgba(60,54,44,0.08)'; g.fillRect(x, dado + 10, 2 + r() * 20, h); }   // scuffs on the dado
      for (let i = 0; i < stains; i++) { const x = r() * w, y = r() * 80, rad = 50 + r() * 140;
        const grd = g.createRadialGradient(x, y, rad * 0.3, x, y, rad); grd.addColorStop(0, 'rgba(120,96,58,0.18)'); grd.addColorStop(0.8, 'rgba(96,72,40,0.35)'); grd.addColorStop(1, 'rgba(96,72,40,0)');
        g.fillStyle = grd; g.beginPath(); g.ellipse(x, y, rad, rad * 1.4, 0, 0, 7); g.fill();
        g.fillStyle = 'rgba(90,70,40,0.25)'; g.fillRect(x - 4, y, 6, 120 + r() * 200); }
      for (let i = 0; i < peel; i++) {             // peeling paint: plaster showing through, dark rim, light curled edge
        const cx = r() * w, cy = r() * h * 0.85, rad = 14 + r() * 60;
        g.beginPath(); const n = 14;
        for (let k = 0; k <= n; k++) { const a = k / n * Math.PI * 2, rr = rad * (0.45 + r() * 0.8); g.lineTo(cx + Math.cos(a) * rr * 1.3, cy + Math.sin(a) * rr); }
        g.closePath(); g.fillStyle = '#aaa395'; g.fill(); g.strokeStyle = 'rgba(50,44,36,0.55)'; g.lineWidth = 2.5; g.stroke();
        g.strokeStyle = 'rgba(250,246,232,0.6)'; g.lineWidth = 1.2; g.beginPath(); g.arc(cx, cy - rad * 0.2, rad * 0.9, 3.6, 4.6); g.stroke();
        for (let k = 0; k < 6; k++) { g.fillStyle = 'rgba(120,112,98,0.6)'; g.fillRect(cx + (r() - 0.5) * rad * 3, cy + (r() - 0.5) * rad * 2, 2 + r() * 5, 2 + r() * 4); }
      }
    });
  };
  const lino = T(512, 512, (g, w, h) => {
    for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { const v = (x + y) % 2 ? 112 : 92; const j = R() * 10; g.fillStyle = `rgb(${v + j},${v - 4 + j},${v - 14 + j})`; g.fillRect(x * 64, y * 64, 64, 64); }
    for (let i = 0; i < 4000; i++) { g.fillStyle = `rgba(40,36,30,${R() * 0.12})`; g.fillRect(R() * w, R() * h, 1 + R() * 3, 1 + R() * 2); }
    for (let i = 0; i < 40; i++) { g.strokeStyle = `rgba(30,26,22,${0.2 + R() * 0.3})`; g.lineWidth = 1 + R() * 2; g.beginPath(); const x = R() * w, y = R() * h; g.moveTo(x, y); g.lineTo(x + (R() - 0.5) * 80, y + (R() - 0.5) * 20); g.stroke(); }
  });
  const ceilTex = (stained, seed) => { const r = rng(seed); return T(512, 512, (g, w, h) => {
    g.fillStyle = '#aaa597'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 6000; i++) { g.fillStyle = `rgba(90,86,76,${r() * 0.12})`; g.fillRect(r() * w, r() * h, 1, 1); }
    g.strokeStyle = '#8c8a84'; g.lineWidth = 5; for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(i * 128, 0); g.lineTo(i * 128, h); g.stroke(); g.beginPath(); g.moveTo(0, i * 128); g.lineTo(w, i * 128); g.stroke(); }
    for (let i = 0; i < stained; i++) { const x = r() * w, y = r() * h, rad = 30 + r() * 90;
      for (let k = 0; k < 3; k++) { g.strokeStyle = `rgba(110,80,40,${0.35 - k * 0.08})`; g.lineWidth = 3 + k * 2; g.beginPath(); g.ellipse(x, y, rad * (1 - k * 0.22), rad * (0.8 - k * 0.15), r(), 0, 7); g.stroke(); }
      const grd = g.createRadialGradient(x, y, 0, x, y, rad); grd.addColorStop(0, 'rgba(130,96,50,0.45)'); grd.addColorStop(1, 'rgba(130,96,50,0.05)'); g.fillStyle = grd; g.beginPath(); g.ellipse(x, y, rad, rad * 0.8, 0, 0, 7); g.fill(); }
  }, [3, 3]); };
  const board = T(1024, 340, (g, w, h) => {
    g.fillStyle = '#1f2a24'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(200,210,200,${0.03 + R() * 0.05})`; g.beginPath(); g.ellipse(R() * w, R() * h, 40 + R() * 160, 10 + R() * 40, R(), 0, 7); g.fill(); }
    g.fillStyle = 'rgba(232,232,222,0.85)'; g.font = 'italic 34px "DejaVu Serif"';
    g.fillText('Mardi 6 octobre', 40, 60); g.font = '30px "DejaVu Sans"';
    g.fillText('f(x) = 3x² − 2x + 1', 60, 130); g.fillText("f'(x) = 6x − 2", 60, 180); g.fillText('Δ = b² − 4ac', 520, 130);
    g.fillText('Ex. 4 p. 112', 520, 230);
  });
  const glassTex = (cracked, seed) => { const r = rng(seed); return T(512, 256, (g, w, h) => {
    g.fillStyle = 'rgba(160,170,175,0.25)'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 6; i++) { g.fillStyle = 'rgba(255,255,255,0.08)'; g.save(); g.translate(r() * w, 0); g.rotate(0.5); g.fillRect(0, -50, 20 + r() * 30, h * 2); g.restore(); }
    if (cracked) { const cx = w * (0.3 + r() * 0.4), cy = h * (0.3 + r() * 0.4); g.strokeStyle = 'rgba(245,245,240,0.9)'; g.lineWidth = 1.6;
      for (let k = 0; k < 11; k++) { let x = cx, y = cy, a = k / 11 * Math.PI * 2 + r() * 0.3; g.beginPath(); g.moveTo(x, y);
        for (let s = 0; s < 8; s++) { a += (r() - 0.5) * 0.5; x += Math.cos(a) * 18; y += Math.sin(a) * 18; g.lineTo(x, y); } g.stroke(); }
      for (let k = 1; k < 4; k++) { g.beginPath(); g.ellipse(cx, cy, k * 22, k * 18, 0, 0, 7); g.lineWidth = 0.8; g.stroke(); } }
  }); };
  const signTex = (lines, { w = 512, h = 256, bg = '#f1ede2', fg = '#141414', font = 'bold 64px "DejaVu Sans Condensed"', tape = true, paint = false } = {}) => T(w, h, (g) => {
    g.fillStyle = bg; g.fillRect(0, 0, w, h);
    if (paint) for (let i = 0; i < 400; i++) { g.fillStyle = `rgba(120,110,95,${R() * 0.08})`; g.fillRect(R() * w, R() * h, 3 + R() * 8, 2 + R() * 5); }
    g.fillStyle = fg; g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle';
    lines.forEach((s, i) => { g.save(); g.translate(w / 2 + (paint ? (R() - 0.5) * 12 : 0), h / 2 + (i - (lines.length - 1) / 2) * (h / (lines.length + 0.6))); g.rotate(paint ? (R() - 0.5) * 0.05 : 0); g.fillText(s, 0, 0); g.restore(); });
    if (tape) { g.fillStyle = 'rgba(220,210,170,0.75)'; g.fillRect(-10, 6, 90, 26); g.fillRect(w - 80, 6, 90, 26); }
  });

  // ------------------------------------------------------------------ materials
  const M = {
    conc: std({ map: concreteExt, roughness: 0.92 }),
    concDark: std({ map: concreteExt, color: 0x8a8884, roughness: 0.95 }),
    cut: std({ color: 0xb9b1a2, roughness: 0.95 }),                   // section poche: the sliced concrete
    floor: std({ map: lino, roughness: 0.55 }),
    metal: std({ color: 0x55585a, metalness: 0.6, roughness: 0.45 }),
    deskTop: std({ color: 0xb08d62, roughness: 0.6 }),
    chair: std({ color: 0x3f4a52, roughness: 0.6 }),
    board: std({ map: board, roughness: 0.8 }),
    tube: new THREE.MeshBasicMaterial({ color: 0xf2f6f8 }),
    fixture: std({ color: 0xcfd2d0, roughness: 0.5 }),
    head: std({ color: 0xcfc7bb, roughness: 0.55 }),                  // mannequin tone: smooth, no features
    pants: std({ color: 0x2b2f38, roughness: 0.85 }),
    shoe: std({ color: 0x1c1c1e, roughness: 0.7 }),
    paper: std({ color: 0xece7da, roughness: 0.9 }),
    frame: std({ color: 0x7a7c7a, metalness: 0.7, roughness: 0.4 }),
    dark: std({ color: 0x0d0e10, roughness: 1 }),
  };
  const hoodies = [0x4a4f57, 0x6b2f2f, 0x2e3a4e, 0x55604a, 0x8a8478, 0x2a2a2c, 0x7a5a3a, 0x3d4b5a, 0x5e5450, 0x9a9488].map(c => std({ color: c, roughness: 0.9 }));
  const packs = [0x1f2226, 0x3b2a22, 0x2a3440, 0x5a2222, 0x40463c].map(c => std({ color: c, roughness: 0.8 }));
  const wallMats = {}; const wallMat = (key, peel, stains, seed) => wallMats[key] ??= std({ map: wallTex(peel, stains, seed), roughness: 0.9 });

  // merge a group's meshes into one mesh per material (keeps the draw-call count sane in software GL)
  const bake = (grp) => {
    grp.updateMatrixWorld(true);
    const inv = new THREE.Matrix4().copy(grp.matrixWorld).invert();
    const buckets = new Map();
    grp.traverse(o => { if (!o.isMesh) return;
      let g = o.geometry.index ? o.geometry.toNonIndexed() : o.geometry.clone();
      for (const k of Object.keys(g.attributes)) if (!['position', 'normal', 'uv'].includes(k)) g.deleteAttribute(k);
      if (!g.attributes.uv) g.setAttribute('uv', new THREE.Float32BufferAttribute(new Float32Array(g.attributes.position.count * 2), 2));
      g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv, o.matrixWorld));
      if (!buckets.has(o.material)) buckets.set(o.material, []); buckets.get(o.material).push(g); });
    const out = new THREE.Group(); out.position.copy(grp.position); out.rotation.copy(grp.rotation); out.scale.copy(grp.scale);
    for (const [m, gs] of buckets) { const me = new THREE.Mesh(mergeGeometries(gs), m); me.castShadow = me.receiveShadow = true; out.add(me); }
    return out;
  };

  // ------------------------------------------------------------------ props
  const deskGeo = { top: new THREE.BoxGeometry(0.5, 0.03, 1.3), leg: new THREE.BoxGeometry(0.03, 0.72, 0.03), rail: new THREE.BoxGeometry(0.03, 0.03, 1.2) };
  const desk = (parent, x, z, y0) => {     // double pupil desk, long side along z
    const g = new THREE.Group(); g.position.set(x, y0, z); parent.add(g);
    add(deskGeo.top, M.deskTop, 0, 0.745, 0, g);
    for (const sx of [-0.21, 0.21]) for (const sz of [-0.6, 0.6]) add(deskGeo.leg, M.metal, sx, 0.36, sz, g);
    add(deskGeo.rail, M.metal, 0.21, 0.2, 0, g);
    return g;
  };
  const chair = (parent, x, z, y0, up = false) => {
    const g = new THREE.Group(); g.position.set(x, y0, z); parent.add(g);
    box(0.4, 0.03, 0.4, M.chair, 0, 0.45, 0, g); box(0.03, 0.32, 0.38, M.chair, 0.2, 0.7, 0, g);
    for (const sx of [-0.17, 0.17]) for (const sz of [-0.17, 0.17]) box(0.025, 0.45, 0.025, M.metal, sx, 0.225, sz, g);
    if (up) { g.rotation.z = Math.PI; g.position.y = y0 + 0.75 + 0.48; }
    return g;
  };
  const pupil = (parent, x, z, y0, i, opts = {}) => {
    const f = figure(THREE, { body: hoodies[i % hoodies.length], head: M.head, dark: M.pants, shoe: M.shoe, pack: packs[i % packs.length], hair: M.pants },
      { seated: true, hood: i % 3 === 0, hair: i % 3 !== 0 && i % 2 === 0, height: 1.62 + (i % 5) * 0.04, ...opts });
    f.position.set(x, y0, z); f.rotation.y = -Math.PI / 2 + ((i * 37) % 11 - 5) * 0.03; parent.add(f);
    return f;
  };
  const backpackFloor = (parent, x, z, y0, i) => { const b = add(new THREE.CapsuleGeometry(0.14, 0.16, 4, 10), packs[i % packs.length], x, y0 + 0.2, z, parent); b.scale.set(1, 1, 0.6); b.rotation.set(0.3, i, 0.2); };

  // ------------------------------------------------------------------ building shell
  const LEN = 36;
  // floor slabs + roof, with the cut face in section colour
  for (let f = 0; f <= 3; f++) {
    const y = f * 3.4 + 0.15;
    const s = new THREE.Mesh(new THREE.BoxGeometry(LEN + 0.6, 0.3, DEPTH + 0.6), [M.concDark, M.concDark, M.conc, M.concDark, M.cut, M.concDark]);
    s.position.set(0, y, -DEPTH / 2 + 0.0); s.castShadow = s.receiveShadow = true; scene.add(s);
  }
  // roof parapet and rooftop plant
  box(LEN + 0.6, 0.6, 0.25, M.conc, 0, 10.5 + 0.3, -DEPTH - 0.18); box(0.25, 0.6, DEPTH + 0.6, M.conc, -LEN / 2 - 0.18, 10.8, -DEPTH / 2); box(0.25, 0.6, DEPTH + 0.6, M.conc, LEN / 2 + 0.18, 10.8, -DEPTH / 2);
  box(3, 1.2, 2.4, M.concDark, -10, 11.1, -5.2); box(2, 0.9, 1.6, M.metal, 7, 10.95, -5.8);
  // end walls (the cut face of each shows in section colour)
  for (const sx of [-1, 1]) { const w = new THREE.Mesh(new THREE.BoxGeometry(0.3, 10.2, DEPTH + 0.3), [M.conc, M.conc, M.conc, M.conc, M.cut, M.conc]); w.position.set(sx * (LEN / 2 + 0.15), 5.1 + 0.3, -DEPTH / 2 - 0.15); w.castShadow = w.receiveShadow = true; scene.add(w); }

  const lights = [];      // per-room ceiling lights { light, tubes, room }
  const rooms = {};
  const glassMats = [glassTex(false, 1), glassTex(true, 2), glassTex(false, 3)].map(t => new THREE.MeshStandardMaterial({ map: t, transparent: true, roughness: 0.15, metalness: 0.3, color: 0xbfc8cc, depthWrite: false, side: THREE.DoubleSide }));

  function shellRoom(f, i, { wall, ceilMat, lightOn = true, lightColor = 0xe6eef3, cracked = false, tiles = false }) {
    const x0 = RX[i], y0 = FY(f), cx = x0 + 4.5, hgt = 3.1;
    const g = new THREE.Group(); scene.add(g);
    // floor
    const fl = new THREE.Mesh(new THREE.PlaneGeometry(9, DEPTH), tiles ? tiles.floor : M.floor); fl.rotation.x = -Math.PI / 2; fl.position.set(cx, y0 + 0.002, -DEPTH / 2); fl.receiveShadow = true; g.add(fl);
    if (!tiles) { fl.material = M.floor; fl.geometry.attributes.uv.array.forEach((v, k, a) => { a[k] = v * (k % 2 ? DEPTH / 2.4 : 9 / 2.4); }); }
    // ceiling (suspended tiles)
    const ce = new THREE.Mesh(new THREE.PlaneGeometry(9, DEPTH), ceilMat); ce.rotation.x = Math.PI / 2; ce.position.set(cx, y0 + hgt - 0.05, -DEPTH / 2); g.add(ce);
    // back wall with ribbon window: spandrel below, lintel above, mullions, glass
    const wm = wall;
    const backLow = add(new THREE.PlaneGeometry(9, 1.0), wm, cx, y0 + 0.5, -DEPTH + 0.01, g);
    const backHigh = add(new THREE.PlaneGeometry(9, 0.45), wm, cx, y0 + hgt - 0.275, -DEPTH + 0.01, g);
    setUV(backLow, 9 / 4.5, 1.0 / 3.1, 0); setUV(backHigh, 9 / 4.5, 0.45 / 3.1, 2.65 / 3.1);
    box(9, 0.06, 0.32, M.fixture, cx, y0 + 1.02, -DEPTH + 0.1, g);    // sill
    for (let k = 0; k <= 6; k++) box(0.07, 1.6, 0.1, M.frame, x0 + 0.05 + k * 1.483, y0 + 1.85, -DEPTH - 0.02, g);
    box(9, 0.06, 0.1, M.frame, cx, y0 + 1.05, -DEPTH - 0.02, g); box(9, 0.06, 0.1, M.frame, cx, y0 + 2.62, -DEPTH - 0.02, g);
    for (let k = 0; k < 6; k++) { const gl = new THREE.Mesh(new THREE.PlaneGeometry(1.42, 1.55), glassMats[cracked && k === 2 ? 1 : (k % 2 ? 2 : 0)]); gl.position.set(x0 + 0.79 + k * 1.483, y0 + 1.84, -DEPTH - 0.03); g.add(gl); }
    // side walls (shared partitions drawn from both rooms as thin planes, plus a solid core between rooms)
    for (const [sx, xx] of [[1, x0 + 0.1], [-1, x0 + 8.9]]) {
      const p = add(new THREE.PlaneGeometry(DEPTH, hgt), wm, xx, y0 + hgt / 2, -DEPTH / 2, g); p.rotation.y = sx * Math.PI / 2; setUV(p, DEPTH / 4.5, 1, 0);
    }
    if (i < 3) { const core = new THREE.Mesh(new THREE.BoxGeometry(0.2, 3.1, DEPTH), [M.cut, M.cut, M.cut, M.cut, M.cut, M.cut]); core.position.set(x0 + 9, y0 + 1.55, -DEPTH / 2); scene.add(core); }
    // cut face of the suspended ceiling void
    box(9, 0.25, 0.02, M.cut, cx, y0 + hgt + 0.12, -0.01, g);
    // fluorescent fixtures
    const tubes = [];
    for (const fx of [-2.2, 2.2]) for (const fz of [-5.6, -2.4]) {
      box(1.3, 0.06, 0.3, M.fixture, cx + fx, y0 + hgt - 0.08, fz, g);
      const tb = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.2, 8), M.tube.clone()); tb.rotation.z = Math.PI / 2; tb.position.set(cx + fx, y0 + hgt - 0.13, fz); g.add(tb); tubes.push(tb);
      if (!lightOn) tb.material.color.setHex(0x2a2c2e);
    }
    const L = new THREE.PointLight(lightColor, lightOn ? 7 : 0, 11, 2); L.position.set(cx, y0 + hgt - 0.5, -4.2); scene.add(L);
    lights.push({ light: L, tubes, f, i, base: lightOn ? 7 : 0 });
    return { g, x0, y0, cx, hgt, L, tubes };
  }
  function setUV(mesh, sx, sy, oy) { const uv = mesh.geometry.attributes.uv; for (let k = 0; k < uv.count; k++) uv.setXY(k, uv.getX(k) * sx, uv.getY(k) * sy + oy); }

  // standard classroom furniture: board on the left wall, teacher desk, 6 rows x 3 double desks facing -x
  function classroom(room, { n = 24, teacher = false, teacherDesk = true, chairsUp = false, seed = 1, skip = [], omit = () => false } = {}) {
    const { g, x0, y0 } = room;
    const bd = add(new THREE.PlaneGeometry(3.6, 1.2), M.board, x0 + 0.12, y0 + 1.6, -4.0, g); bd.rotation.y = Math.PI / 2;
    box(0.06, 1.3, 3.75, M.frame, x0 + 0.1, y0 + 1.6, -4.0, g); box(0.12, 0.04, 3.6, M.frame, x0 + 0.17, y0 + 0.98, -4.0, g);
    if (teacherDesk) {
      const td = new THREE.Group(); td.position.set(x0 + 1.55, y0, -4.0); g.add(td);
      box(0.75, 0.04, 1.5, M.deskTop, 0, 0.76, 0, td); box(0.7, 0.66, 0.03, M.deskTop, -0.0, 0.42, -0.72, td); box(0.7, 0.66, 0.03, M.deskTop, 0, 0.42, 0.72, td);
      box(0.03, 0.5, 1.44, M.deskTop, 0.34, 0.5, 0, td);    // modesty panel facing the class
      room.teacherDesk = td;
      const tc = chair(g, x0 + 0.95, -4.0, y0); tc.rotation.y = Math.PI; room.teacherChair = tc;
    }
    const rows = [3.0, 3.95, 4.9, 5.85, 6.8, 7.75], cols = [-6.5, -4.1, -1.7];
    const seats = [];
    for (const rx of rows) for (const cz of cols) { if (omit(rx, cz)) continue; desk(g, x0 + rx, cz, y0); for (const s of [-0.33, 0.33]) seats.push([x0 + rx + 0.48, cz + s]); }
    const r = rng(seed); const order = seats.map((s, k) => [r(), k]).sort((a, b) => a[0] - b[0]).map(a => a[1]);
    const filled = new Set(order.filter(k => !skip.includes(k)).slice(0, n));
    const studs = new THREE.Group(); g.add(studs);
    seats.forEach(([sx, sz], k) => {
      const c = chair(g, sx, sz, y0, chairsUp && !filled.has(k));
      if (chairsUp && !filled.has(k)) { c.position.x = sx - 0.48; }
      if (filled.has(k)) { pupil(studs, sx + 0.02, sz, y0, k + seed * 7); if (r() < 0.45) backpackFloor(g, sx + 0.1, sz + (sz > -4 ? 0.3 : -0.3), y0, k); }
      if (!chairsUp || filled.has(k)) if (r() < 0.6) { const b = box(0.21, 0.012, 0.3, M.paper, sx - 0.55, y0 + 0.767, sz, g); b.rotation.y = (r() - 0.5) * 0.4; }
    });
    if (teacher) { const tf = figure(THREE, { body: std({ color: 0x5a5148 }), head: M.head, dark: M.pants, shoe: M.shoe, hair: M.pants }, { height: 1.75, hair: true, armsUp: 1 }); tf.position.set(x0 + 0.9, y0, -2.9); tf.rotation.y = Math.PI / 2 + 0.5; g.add(tf); }
    room.studs = studs; room.seats = seats; room.filled = filled;
    return room;
  }

  // ------------------------------------------------------------------ rooms
  const ceilPlain = std({ map: ceilTex(1, 11), roughness: 0.95 });
  const ceilStained = std({ map: ceilTex(7, 12), roughness: 0.95 });
  const ceilMid = std({ map: ceilTex(3, 13), roughness: 0.95 });
  // F1
  rooms.crowd = classroom(shellRoom(1, 0, { wall: wallMat('a', 6, 2, 21), ceilMat: ceilMid }), { n: 36, seed: 3 });
  rooms.empty = classroom(shellRoom(1, 1, { wall: wallMat('b', 10, 3, 22), ceilMat: ceilPlain }), { n: 28, seed: 4 });
  rooms.lesson = classroom(shellRoom(1, 2, { wall: wallMat('c', 5, 1, 23), ceilMat: ceilPlain }), { n: 30, teacher: true, seed: 5 });
  rooms.f1d = classroom(shellRoom(1, 3, { wall: wallMat('d', 14, 4, 24), ceilMat: ceilMid, cracked: true }), { n: 0, chairsUp: true, seed: 6 });
  // F2
  rooms.leak = classroom(shellRoom(2, 0, { wall: wallMat('e', 22, 8, 25), ceilMat: ceilStained, cracked: true }), { n: 12, seed: 7, omit: (rx, cz) => cz !== -1.7 && rx < 6.5 });
  rooms.heat = classroom(shellRoom(2, 1, { wall: wallMat('f', 8, 3, 26), ceilMat: ceilMid, lightOn: false }), { n: 30, seed: 8 });
  rooms.peel = classroom(shellRoom(2, 2, { wall: wallMat('g', 40, 6, 27), ceilMat: ceilStained }), { n: 22, teacher: true, seed: 9 });
  rooms.f2d = shellRoom(2, 3, { wall: wallMat('h', 30, 9, 28), ceilMat: ceilStained, lightOn: false, cracked: true });
  classroom(rooms.f2d, { n: 0, chairsUp: true, seed: 10 });
  // F0
  const toiletWall = std({ map: tileTex(THREE, { tile: 22, grout: 3, base: 196, vary: 22, dirt: 0.9, repeat: [2, 1], seed: 31 }), roughness: 0.35 });
  const toiletFloor = std({ map: tileTex(THREE, { tile: 26, grout: 3, base: 120, vary: 30, dirt: 0.4, repeat: [6, 6], seed: 32 }), roughness: 0.4 });
  rooms.wc = shellRoom(0, 0, { wall: toiletWall, ceilMat: ceilStained, tiles: { floor: toiletFloor }, lightColor: 0xd9f0e6 });
  rooms.hall = shellRoom(0, 1, { wall: wallMat('i', 12, 2, 29), ceilMat: ceilPlain });
  rooms.f0c = classroom(shellRoom(0, 2, { wall: wallMat('j', 9, 2, 30), ceilMat: ceilPlain }), { n: 18, seed: 11 });
  rooms.f0d = classroom(shellRoom(0, 3, { wall: wallMat('k', 12, 3, 31), ceilMat: ceilMid, lightOn: false }), { n: 0, chairsUp: true, seed: 12 });

  // --- crowded: per-desk amber glow strips for the count-up
  const deskGlow = [];
  {
    const { x0, y0 } = rooms.crowd;
    const gm = () => new THREE.MeshBasicMaterial({ color: AMBER_HI, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, fog: false });
    const seats = rooms.crowd.seats;
    // order the 36 seats front-to-back so the count reads as a sweep
    const idx = seats.map((s, k) => k).sort((a, b) => (seats[a][0] - seats[b][0]) * 10 + (seats[b][1] - seats[a][1]));
    for (const k of idx) {
      const [sx, sz] = seats[k];
      const strip = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.6), gm()); strip.rotation.x = -Math.PI / 2; strip.position.set(sx - 0.48, y0 + 0.77, sz); scene.add(strip);
      const halo = glow(THREE, AMBER, 1.1, 0.8); halo.position.set(sx - 0.2, y0 + 1.2, sz); halo.material.opacity = 0; scene.add(halo);
      deskGlow.push({ strip, halo });
    }
  }

  // --- empty desk: amber spot + dust motes
  const emptySpot = new THREE.SpotLight(0xffb36a, 0, 9, 0.42, 0.65, 1.3);
  { const td = rooms.empty.teacherDesk; const wp = new THREE.Vector3(); td.getWorldPosition(wp);
    emptySpot.position.set(wp.x + 0.6, wp.y + 2.95, wp.z + 0.4); emptySpot.target.position.set(wp.x - 0.1, wp.y + 0.5, wp.z); emptySpot.castShadow = true; emptySpot.shadow.mapSize.set(1024, 1024); emptySpot.shadow.bias = -0.0005;
    scene.add(emptySpot, emptySpot.target); }
  const emptyBeam = beam(THREE, 0xffb36a, 2.8, 1.05, 0); emptyBeam.position.copy(emptySpot.position); emptyBeam.lookAt(emptySpot.target.position); emptyBeam.rotateX(-Math.PI / 2); scene.add(emptyBeam);
  const motes = (() => {
    const n = 220, pos = new Float32Array(n * 3), r = rng(5);
    for (let k = 0; k < n; k++) { pos[k * 3] = (r() - 0.5) * 1.4; pos[k * 3 + 1] = r() * 2.4; pos[k * 3 + 2] = (r() - 0.5) * 1.6; }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const p = new THREE.Points(g, new THREE.PointsMaterial({ color: 0xffd2a0, size: 0.018, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
    const wp = new THREE.Vector3(); rooms.empty.teacherDesk.getWorldPosition(wp); p.position.set(wp.x + 0.2, wp.y + 0.6, wp.z); scene.add(p); return p;
  })();

  // --- leak room: hole in the ceiling, fallen tile, bucket, drips, puddle, rat
  const leak = {};
  {
    const { x0, y0, hgt } = rooms.leak, cy = y0 + hgt - 0.05;
    const hx = x0 + 4.1, hz = -4.3;                         // the missing tile
    const hole = add(new THREE.PlaneGeometry(0.6, 0.6), M.dark, hx, cy - 0.003, hz, rooms.leak.g); hole.rotation.x = Math.PI / 2;
    const pipe = add(new THREE.CylinderGeometry(0.06, 0.06, 2.4, 10), std({ color: 0x6d5a48, metalness: 0.5, roughness: 0.5 }), hx, cy + 0.15, hz, rooms.leak.g); pipe.rotation.z = Math.PI / 2;
    const hang = add(new THREE.BoxGeometry(0.6, 0.015, 0.6), std({ map: ceilStained.map, color: 0xb8ab96 }), hx + 0.15, cy - 0.2, hz + 0.32, rooms.leak.g); hang.rotation.set(0.9, 0, 0.15);   // half-detached tile
    // fallen tile in two pieces with debris
    const tileM = std({ color: 0xcfc7b4, roughness: 0.95 });
    const p1 = add(new THREE.BoxGeometry(0.42, 0.015, 0.6), tileM, hx - 0.5, y0 + 0.02, hz + 0.7, rooms.leak.g); p1.rotation.set(0.04, 0.6, 0.05);
    const p2 = add(new THREE.BoxGeometry(0.22, 0.015, 0.5), tileM, hx - 0.05, y0 + 0.05, hz + 0.95, rooms.leak.g); p2.rotation.set(-0.12, -0.3, 0.2);
    for (let k = 0; k < 26; k++) { const s = 0.02 + R() * 0.05; const d = add(new THREE.BoxGeometry(s, s * 0.5, s), tileM, hx - 0.4 + (R() - 0.5) * 1.3, y0 + s * 0.25, hz + 0.6 + (R() - 0.5) * 1.1, rooms.leak.g); d.rotation.y = R() * 3; }
    // bucket under the second drip
    const bx = x0 + 5.6, bz = -5.4;
    const bucketM = std({ color: 0x8a8d90, metalness: 0.6, roughness: 0.35, side: THREE.DoubleSide });
    add(new THREE.CylinderGeometry(0.17, 0.13, 0.3, 28, 1, true), bucketM, bx, y0 + 0.15, bz, rooms.leak.g);
    add(new THREE.CylinderGeometry(0.13, 0.13, 0.01, 28), bucketM, bx, y0 + 0.005, bz, rooms.leak.g);
    const handle = add(new THREE.TorusGeometry(0.17, 0.006, 6, 28, Math.PI), M.metal, bx, y0 + 0.3, bz, rooms.leak.g); handle.rotation.y = 0.5;
    const water = add(new THREE.CircleGeometry(0.155, 28), std({ color: 0x29323a, roughness: 0.05, metalness: 0.4 }), bx, y0 + 0.22, bz, rooms.leak.g); water.rotation.x = -Math.PI / 2;
    // stain above the bucket: a separate darker overlay on the ceiling
    const stainM = new THREE.MeshBasicMaterial({ map: T(256, 256, (g) => { const grd = g.createRadialGradient(128, 128, 10, 128, 128, 126); grd.addColorStop(0, 'rgba(70,46,18,0.85)'); grd.addColorStop(0.7, 'rgba(90,62,24,0.5)'); grd.addColorStop(0.92, 'rgba(60,40,14,0.7)'); grd.addColorStop(1, 'rgba(60,40,14,0)'); g.fillStyle = grd; g.fillRect(0, 0, 256, 256); }), transparent: true, depthWrite: false, color: 0xffffff });
    for (const [sx, sz, sr] of [[bx, bz, 1.3], [hx, hz, 1.8], [x0 + 2.4, -6.6, 1.0]]) { const st = new THREE.Mesh(new THREE.PlaneGeometry(sr, sr), stainM); st.rotation.x = Math.PI / 2; st.position.set(sx, cy - 0.006, sz); rooms.leak.g.add(st); }
    // puddle under the hole
    const pud = add(new THREE.CircleGeometry(0.8, 40), std({ color: 0x1a1e22, roughness: 0.04, metalness: 0.6, transparent: true, opacity: 0.85 }), hx - 0.1, y0 + 0.006, hz - 0.2, rooms.leak.g); pud.rotation.x = -Math.PI / 2; pud.scale.set(1.2, 0.8, 1);
    // drips (two streams) + ripple rings
    const dropM = std({ color: 0xcfe0ea, roughness: 0.05, metalness: 0.2, emissive: 0x3a2a14, transparent: true, opacity: 0.9 });
    leak.drops = [];
    for (const [dx, dz, top, bot, rate] of [[hx, hz - 0.2, cy, y0 + 0.01, 1.05], [bx, bz, cy, y0 + 0.22, 0.8]]) for (let k = 0; k < 3; k++) {
      const d = add(new THREE.SphereGeometry(0.018, 10, 8), dropM, dx, top, dz, rooms.leak.g); leak.drops.push({ d, top, bot, rate, ph: k / 3 + R() * 0.1 });
    }
    const ringM = () => new THREE.MeshBasicMaterial({ color: 0xffd0a0, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending });
    leak.rings = [[hx, hz - 0.2, y0 + 0.012, 1.05], [bx, bz, y0 + 0.225, 0.8]].map(([x, z, y, rate]) => { const m = new THREE.Mesh(new THREE.RingGeometry(0.9, 1.0, 40), ringM()); m.rotation.x = -Math.PI / 2; m.position.set(x, y, z); rooms.leak.g.add(m); return { m, rate }; });
    // amber light on the problem
    leak.spot = new THREE.SpotLight(0xffb066, 0, 10, 0.5, 0.6, 1.2); leak.spot.position.set(x0 + 6.5, y0 + 2.8, -1.2); leak.spot.target.position.set(bx - 0.6, y0 + 0.4, bz + 0.6); leak.spot.castShadow = true; leak.spot.shadow.mapSize.set(1024, 1024); leak.spot.shadow.bias = -0.0005;
    scene.add(leak.spot, leak.spot.target);
    leak.holeGlow = glow(THREE, AMBER, 0.9, 0.7); leak.holeGlow.position.set(hx, cy - 0.05, hz); scene.add(leak.holeGlow);
    // rat (fine to have features: it is a rat)
    const ratM = std({ color: 0x2e2a27, roughness: 0.75 });
    const rat = new THREE.Group();
    const body = add(new THREE.SphereGeometry(0.1, 16, 12), ratM, 0, 0.065, 0, rat); body.scale.set(1.6, 0.75, 0.8);
    const head = add(new THREE.ConeGeometry(0.055, 0.14, 12), ratM, 0.19, 0.06, 0, rat); head.rotation.z = -Math.PI / 2;
    for (const s of [-1, 1]) add(new THREE.SphereGeometry(0.025, 8, 6), ratM, 0.15, 0.115, s * 0.035, rat);
    const tail = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(-0.15, 0.04, 0), new THREE.Vector3(-0.3, 0.02, 0.06), new THREE.Vector3(-0.45, 0.01, -0.02), new THREE.Vector3(-0.58, 0.02, 0.05)]), 16, 0.008, 5), ratM);
    rat.add(tail); rat.position.set(x0 + 8.2, y0, -7.7); scene.add(rat); leak.rat = rat; leak.ratY = y0; leak.ratX = x0 + 8.2;
  }

  // --- heat room: thermometer + low sun through the windows
  const heat = {};
  {
    const { x0, y0 } = rooms.heat;
    const th = new THREE.Group(); th.position.set(x0 + 8.86, y0 + 1.55, -2.6); th.rotation.y = -Math.PI / 2; scene.add(th);
    const scale = T(160, 640, (g, w, h) => {
      g.fillStyle = '#e8e2d2'; g.fillRect(0, 0, w, h); g.strokeStyle = '#3a3a3a'; g.fillStyle = '#2a2a2a'; g.font = 'bold 26px "DejaVu Sans Condensed"'; g.textAlign = 'right';
      for (let c = 0; c <= 50; c += 2) { const y = 560 - c * 10; g.lineWidth = c % 10 ? 2 : 4; g.beginPath(); g.moveTo(c % 10 ? 110 : 98, y); g.lineTo(130, y); g.stroke(); if (c % 10 === 0) g.fillText(String(c), 92, y + 9); }
      g.font = 'bold 30px "DejaVu Sans"'; g.textAlign = 'center'; g.fillText('°C', 80, 620);
    });
    box(0.28, 1.1, 0.03, std({ color: 0x6a4a2e, roughness: 0.6 }), 0, 0, -0.02, th);
    add(new THREE.PlaneGeometry(0.22, 0.88), std({ map: scale, roughness: 0.7 }), 0, 0.02, 0.0, th);
    add(new THREE.CylinderGeometry(0.016, 0.016, 0.82, 16), std({ color: 0xe8f0f4, transparent: true, opacity: 0.35, roughness: 0.05 }), 0.05, 0.04, 0.03, th);
    const bulb = add(new THREE.SphereGeometry(0.03, 16, 12), new THREE.MeshBasicMaterial({ color: 0xff6a2a }), 0.05, -0.39, 0.03, th);
    const liq = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.009, 1, 10).translate(0, 0.5, 0), new THREE.MeshBasicMaterial({ color: 0xff7a30 })); liq.position.set(0.05, -0.37, 0.03); th.add(liq);
    heat.liq = liq; heat.th = th;
    // thermometer scale: y at value c = (560 - c*10)/640 of the plane (0.88 high, centred at 0.02)
    heat.yAt = (c) => 0.02 + 0.44 - (560 - c * 10) / 640 * 0.88 + 0.37;
    heat.glow = glow(THREE, 0xff9a4a, 0.7, 0.9); heat.glow.position.set(x0 + 8.8, y0 + 1.2, -2.6); scene.add(heat.glow);
    // low sun through the back windows
    heat.sun = new THREE.SpotLight(0xffa850, 0, 40, 0.5, 0.5, 1.0); heat.sun.position.set(x0 + 1.5, y0 + 4.2, -16); heat.sun.target.position.set(x0 + 6, y0 + 0.2, -2.5);
    heat.sun.castShadow = true; heat.sun.shadow.mapSize.set(1024, 1024); heat.sun.shadow.bias = -0.0004; scene.add(heat.sun, heat.sun.target);
    heat.beams = [];
    for (let k = 0; k < 5; k++) { const b = beam(THREE, 0xffb060, 9, 0.75, 0); b.position.set(x0 + 1.4 + k * 1.5, y0 + 2.0, -DEPTH - 0.2); b.lookAt(x0 + 4.0 + k * 1.3, y0 - 0.5, -1.0); b.rotateX(-Math.PI / 2); scene.add(b); heat.beams.push(b); }
    // two pupils fanning themselves with a sheet
    const studs = rooms.heat.studs.children;
    [3, 11].forEach(k => { const s = studs[k]; if (!s) return; const fan = box(0.2, 0.28, 0.006, M.paper, 0.32, 1.12, 0.18, s); fan.rotation.y = 0.8; heat.fan = (heat.fan || []).concat([fan]); });
  }

  // --- toilet block
  const wc = {};
  {
    const { x0, y0, g } = rooms.wc;
    const partM = std({ color: 0x5b6a63, roughness: 0.5 });
    const porc = std({ color: 0xe9e8e2, roughness: 0.25 });
    for (let k = 0; k < 5; k++) {
      const sx = x0 + 1.6 + k * 1.35;
      if (k < 4) box(0.04, 2.0, 1.55, partM, sx + 1.35, y0 + 1.1, -DEPTH + 0.78, g);   // partitions
      const bowl = add(new THREE.LatheGeometry([[0, 0], [0.15, 0], [0.19, 0.25], [0.21, 0.4], [0.18, 0.42]].map(([a, b]) => new THREE.Vector2(a, b)), 20), porc, sx + 0.675, y0, -DEPTH + 0.35, g); bowl.scale.set(1, 1, 1.3);
      box(0.36, 0.4, 0.16, porc, sx + 0.675, y0 + 0.6, -DEPTH + 0.1, g);
      // doors: one hanging off its hinge, one taped shut
      const door = new THREE.Group(); door.position.set(sx + 0.04, y0 + 0.12, -DEPTH + 1.56); g.add(door);
      const dm = box(1.27, 1.85, 0.035, partM, 0.635, 0.925, 0, door);
      if (k === 1) { door.rotation.set(0.0, -1.2, 0.28); door.position.y += 0.05; wc.hang = door; }
      else if (k === 3) { wc.taped = door; door.rotation.y = 0; }
      else door.rotation.y = -0.15 - R() * 0.5;
    }
    box(0.04, 2.0, 1.55, partM, x0 + 1.6, y0 + 1.1, -DEPTH + 0.78, g);
    // the broken toilet in stall 2 (cracked lid on the floor)
    const lid = box(0.36, 0.03, 0.42, porc, x0 + 1.6 + 1.35 + 0.4, y0 + 0.02, -DEPTH + 1.0, g); lid.rotation.y = 0.7;
    // taped sign on stall 4
    const sign = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.32), std({ map: signTex(['HORS', 'SERVICE'], { font: 'bold 92px "DejaVu Sans Condensed"' }), roughness: 0.8 }));
    sign.position.set(0.635, 1.25, 0.03); sign.rotation.z = 0.06; wc.taped.add(sign);
    const tapeM = std({ color: 0xd9c070, roughness: 0.6 });
    for (const a of [0.55, -0.55]) { const tp = box(1.5, 0.06, 0.004, tapeM, 0.635, 0.95, 0.04, wc.taped); tp.rotation.z = a; }
    // sinks + mirror on the left wall, one mirror cracked
    for (let k = 0; k < 3; k++) {
      const z = -6.2 + k * 1.4;
      const sink = add(new THREE.CylinderGeometry(0.24, 0.18, 0.16, 20, 1, false, 0, Math.PI), porc, x0 + 0.12, y0 + 0.85, z, g); sink.rotation.y = 0;
      box(0.06, 0.2, 0.04, M.metal, x0 + 0.16, y0 + 1.0, z, g);
      const mir = add(new THREE.PlaneGeometry(0.7, 0.55), std({ map: glassTex(k === 1, 40 + k), color: 0x9aa5ab, metalness: 0.9, roughness: 0.08 }), x0 + 0.115, y0 + 1.55, z, g); mir.rotation.y = Math.PI / 2;
    }
    const pud = add(new THREE.CircleGeometry(1.1, 40), std({ color: 0x1c2024, roughness: 0.03, metalness: 0.6, transparent: true, opacity: 0.8 }), x0 + 2.4, y0 + 0.006, -5.3, g); pud.rotation.x = -Math.PI / 2; pud.scale.set(1.4, 0.7, 1);
    wc.spot = new THREE.SpotLight(0xffb066, 0, 10, 0.42, 0.6, 1.2); wc.spot.position.set(x0 + 6.6, y0 + 2.9, -2.2); wc.spot.target.position.set(x0 + 5.8, y0 + 1.1, -DEPTH + 1.5);
    wc.spot.castShadow = true; wc.spot.shadow.mapSize.set(1024, 1024); wc.spot.shadow.bias = -0.0005; scene.add(wc.spot, wc.spot.target);
  }
  // --- entrance hall: lockers, notice board, stair
  {
    const { x0, y0, g } = rooms.hall;
    const lockM = std({ color: 0x6a7470, metalness: 0.4, roughness: 0.5 });
    for (let k = 0; k < 10; k++) { const l = box(0.48, 1.8, 0.45, lockM, x0 + 1.0 + k * 0.5, y0 + 0.9, -DEPTH + 0.25, g); if (k === 3) { const d = box(0.46, 1.7, 0.02, lockM, x0 + 1.0 + k * 0.5 + 0.2, y0 + 0.9, -DEPTH + 0.62, g); d.rotation.y = -0.9; } }
    for (let k = 0; k < 9; k++) box(1.6, 0.17, 0.3, M.concDark, x0 + 7.6, y0 + 0.085 + k * 0.17, -6.6 + k * 0.3, g);
  }

  // ------------------------------------------------------------------ front façade (removed by the cut)
  const cutPlane = new THREE.Plane(new THREE.Vector3(1, 0, 0), 30);     // visible where x > -constant
  const facade = new THREE.Group(); scene.add(facade);
  {
    const fm = std({ map: concreteExt, roughness: 0.9, clippingPlanes: [cutPlane], side: THREE.DoubleSide });
    const frm = std({ color: 0x6f716f, metalness: 0.6, roughness: 0.4, clippingPlanes: [cutPlane] });
    const glassF = new THREE.MeshStandardMaterial({ color: 0x9fb0b8, transparent: true, opacity: 0.32, roughness: 0.1, metalness: 0.5, clippingPlanes: [cutPlane], depthWrite: false });
    for (let f = 0; f < 3; f++) {
      const y0 = FY(f);
      const low = new THREE.Mesh(new THREE.BoxGeometry(LEN + 0.6, 1.0, 0.25), fm); low.position.set(0, y0 + 0.5, 0.2); facade.add(low);
      const high = new THREE.Mesh(new THREE.BoxGeometry(LEN + 0.6, 0.75, 0.25), fm); high.position.set(0, y0 + 2.75 + 0.0, 0.2); facade.add(high);
      for (let k = 0; k <= 30; k++) { const m = new THREE.Mesh(new THREE.BoxGeometry(0.08, 1.6, 0.12), frm); m.position.set(-LEN / 2 + k * 1.2, y0 + 1.85, 0.25); facade.add(m); }
      const gl = new THREE.Mesh(new THREE.PlaneGeometry(LEN, 1.6), glassF); gl.position.set(0, y0 + 1.85, 0.22); facade.add(gl);
    }
    facade.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
    // "LIBERTÉ · ÉGALITÉ · FRATERNITÉ" and LYCÉE lettering above the entrance (on the façade, so it is cut too)
    const letters = new THREE.Mesh(new THREE.PlaneGeometry(9, 0.5), new THREE.MeshStandardMaterial({ map: signTex(['LIBERTÉ · ÉGALITÉ · FRATERNITÉ'], { w: 2048, h: 114, bg: '#00000000', fg: '#d9d2c2', font: '600 74px Inter', tape: false }), transparent: true, clippingPlanes: [cutPlane] }));
    letters.position.set(-4.5, FY(1) - 0.05 + 0.0, 0.34); facade.add(letters);
    const lycee = new THREE.Mesh(new THREE.PlaneGeometry(3.2, 0.6), new THREE.MeshStandardMaterial({ map: signTex(['LYCÉE'], { w: 1024, h: 192, bg: '#00000000', fg: '#e6dfcf', font: '800 150px "Inter Display"', tape: false }), transparent: true, clippingPlanes: [cutPlane] }));
    lycee.position.set(-4.5, FY(2) - 0.05, 0.34); facade.add(lycee);
  }
  // cut line (amber laser) and sparks
  const cutLine = new THREE.Group(); scene.add(cutLine);
  const cutCore = new THREE.Mesh(new THREE.BoxGeometry(0.05, 10.6, 0.5), new THREE.MeshBasicMaterial({ color: 0xffd9a8, fog: false })); cutCore.position.y = 5.4; cutLine.add(cutCore);
  const cutHalo = []; for (let k = 0; k < 7; k++) { const s = glow(THREE, AMBER, 3.2, 0.8); s.position.set(0, 0.8 + k * 1.6, 0.4); cutLine.add(s); cutHalo.push(s); }
  const cutLight = new THREE.PointLight(AMBER, 0, 14, 1.4); cutLight.position.set(0, 5, 1.6); cutLine.add(cutLight);
  cutLine.position.z = 0.2; cutLine.visible = false;

  // ------------------------------------------------------------------ outside: yard, fence, gate, street
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(200, 120), std({ map: T(512, 512, (g, w, h) => { g.fillStyle = '#3a3a3a'; g.fillRect(0, 0, w, h); for (let i = 0; i < 20000; i++) { const v = 40 + R() * 50; g.fillStyle = `rgba(${v},${v},${v},0.35)`; g.fillRect(R() * w, R() * h, 1 + R() * 2, 1 + R() * 2); } }, [40, 24]), roughness: 0.85 }));
  ground.rotation.x = -Math.PI / 2; ground.position.set(0, 0, 20); ground.receiveShadow = true; scene.add(ground);
  // yard markings
  for (const [x, z, w, d] of [[-6, 4.5, 12, 0.08], [6, 4.5, 12, 0.08]]) { const l = new THREE.Mesh(new THREE.PlaneGeometry(w, d), std({ color: 0xb8b2a0 })); l.rotation.x = -Math.PI / 2; l.position.set(x, 0.005, z); scene.add(l); }
  // fence with a gate at x = 0, z = 9
  const fence = new THREE.Group(); scene.add(fence);
  {
    const fm = std({ color: 0x2f3433, metalness: 0.6, roughness: 0.5 });
    for (const [a, b] of [[-26, -2.2], [2.2, 26]]) {
      for (let x = a; x <= b; x += 0.14) box(0.025, 2.0, 0.025, fm, x, 1.0, 9, fence);
      box(b - a, 0.05, 0.05, fm, (a + b) / 2, 1.95, 9, fence); box(b - a, 0.05, 0.05, fm, (a + b) / 2, 0.2, 9, fence);
    }
    for (const x of [-2.25, 2.25]) box(0.22, 2.6, 0.22, std({ color: 0x5d5a55, map: concreteExt }), x, 1.3, 9, fence);
    for (const sx of [-1, 1]) { const leaf = new THREE.Group(); leaf.position.set(sx * 2.1, 0, 9); fence.add(leaf);
      for (let k = 0; k <= 14; k++) box(0.03, 2.0, 0.03, fm, -sx * k * 0.14, 1.05, 0, leaf);
      box(2.0, 0.06, 0.06, fm, -sx * 1.0, 1.95, 0, leaf); box(2.0, 0.06, 0.06, fm, -sx * 1.0, 0.25, 0, leaf); box(2.0, 0.05, 0.05, fm, -sx * 1.0, 1.1, 0, leaf); }
    // chain on the gate
    for (let k = 0; k < 9; k++) { const l = add(new THREE.TorusGeometry(0.035, 0.008, 6, 12), M.metal, -0.12 + (k % 3) * 0.08, 1.15 - Math.floor(k / 3) * 0.06, 9.05, fence); l.rotation.y = k % 2 ? Math.PI / 2 : 0; }
  }
  const fenceBaked = bake(fence); scene.remove(fence); scene.add(fenceBaked);
  // street lamp (sodium) by the gate
  const lampPos = new THREE.Vector3(3.6, 5.6, 11.2);
  { const pm = std({ color: 0x2a2c2d, metalness: 0.5, roughness: 0.5 }); box(0.14, 5.7, 0.14, pm, 3.6, 2.85, 11.9); box(0.12, 0.12, 0.9, pm, 3.6, 5.7, 11.5); box(0.4, 0.12, 0.25, pm, lampPos.x, lampPos.y, lampPos.z); }
  const lampBulb = glow(THREE, 0xffa040, 1.6, 1); lampBulb.position.copy(lampPos).add(new THREE.Vector3(0, -0.1, 0)); scene.add(lampBulb);
  const sodium = new THREE.SpotLight(0xff9a3a, outside ? 160 : 40, 30, 0.85, 0.55, 1.3); sodium.position.copy(lampPos); sodium.target.position.set(0.5, 0, 8.4);
  sodium.castShadow = outside; sodium.shadow.mapSize.set(2048, 2048); sodium.shadow.bias = -0.0004; scene.add(sodium, sodium.target);
  const sodiumBeam = beam(THREE, 0xffa04a, 6.5, 3.4, outside ? 0.05 : 0.02); sodiumBeam.position.copy(lampPos); scene.add(sodiumBeam);

  // blockade at the gate
  const blockade = new THREE.Group(); scene.add(blockade);
  if (outside || shot === 'cut') {
    const r = rng(77);
    const binBody = [0x3d4440, 0x4a4d50, 0x2f3a35].map(c => std({ color: c, roughness: 0.6 }));
    const lids = [0xd8b02a, 0x6b2a2a, 0x3a5a3a, 0xd8b02a].map(c => std({ color: c, roughness: 0.5 }));
    const bin = (x, z, ry, tilt, k) => {
      const b = new THREE.Group(); b.position.set(x, 0, z); b.rotation.set(tilt, ry, 0); blockade.add(b);
      const body = add(new THREE.BoxGeometry(0.6, 0.95, 0.72), binBody[k % 3], 0, 0.52, 0, b); body.geometry.attributes.position.array.forEach((v, i, a) => { if (i % 3 !== 1 && a[i + 1 - (i % 3)] < 0) a[i] *= 0.86; });
      body.geometry.computeVertexNormals();
      const lid = add(new THREE.BoxGeometry(0.66, 0.05, 0.8), lids[k % 4], 0, 1.02, 0.02, b); if (k % 3 === 1) { lid.rotation.x = -1.2; lid.position.set(0, 1.25, -0.35); }
      for (const s of [-1, 1]) { const w = add(new THREE.CylinderGeometry(0.1, 0.1, 0.06, 14), M.dark, s * 0.28, 0.1, -0.3, b); w.rotation.z = Math.PI / 2; }
      return b;
    };
    bin(-1.1, 9.55, 0.1, 0, 0); bin(-0.35, 9.6, -0.15, 0, 1); bin(0.45, 9.55, 0.2, 0, 2); bin(1.2, 9.6, -0.05, 0, 3);
    bin(-0.7, 10.3, 1.4, -1.45, 4).position.y = 0.38; bin(0.8, 10.4, 2.2, 0.0, 5);
    const top = bin(-0.1, 9.75, 0.3, 0.25, 6); top.position.y = 1.05;
    const top2 = bin(0.9, 9.8, -0.4, -0.3, 7); top2.position.y = 1.05; top2.rotation.z = 0.35;
    // Vauban crowd barriers leaning against the gate, one toppled
    const vm = std({ color: 0x8c9091, metalness: 0.7, roughness: 0.35 });
    const barrier = (x, z, ry, rx, rz) => { const b = new THREE.Group(); b.position.set(x, 0, z); b.rotation.set(rx, ry, rz); blockade.add(b);
      box(2.0, 0.04, 0.04, vm, 0, 1.1, 0, b); box(2.0, 0.04, 0.04, vm, 0, 0.2, 0, b);
      for (const s of [-1, 1]) { box(0.04, 1.1, 0.04, vm, s * 1.0, 0.65, 0, b); const f = box(0.04, 0.04, 0.5, vm, s * 0.95, 0.05, 0, b); }
      for (let k = 1; k < 13; k++) box(0.015, 0.9, 0.015, vm, -1 + k * 0.154, 0.65, 0, b); return b; };
    barrier(-3.4, 9.5, 0.05, -0.12, 0); barrier(3.3, 9.6, -0.1, -0.1, 0); barrier(-1.8, 10.9, 0.6, -1.4, 0).position.y = 0.05; barrier(1.9, 10.6, -0.3, 0.2, 0.25);
    // pallets
    const wood = std({ color: 0x8a7050, roughness: 0.9 });
    const pallet = (x, y, z, ry, rx) => { const p = new THREE.Group(); p.position.set(x, y, z); p.rotation.set(rx, ry, 0); blockade.add(p);
      for (let k = 0; k < 7; k++) box(1.2, 0.022, 0.1, wood, 0, 0.13, -0.4 + k * 0.133, p); for (const s of [-0.5, 0, 0.5]) box(0.1, 0.1, 0.9, wood, s, 0.06, 0, p); return p; };
    pallet(-2.4, 0, 10.2, 0.4, 0); pallet(-2.3, 0.15, 10.15, 0.2, 0); pallet(2.6, 0.5, 9.75, -0.2, -1.2);
  }
  const blockBaked = bake(blockade); scene.remove(blockade); scene.add(blockBaked);
  // pupils outside with banners (faceless)
  const crowd = new THREE.Group(); scene.add(crowd);
  if (outside) {
    const r = rng(9);
    const placards = [['MOINS', "D'ÉLÈVES", 'PAR CLASSE'], ['DES PROFS,', 'PAS DES', 'PROMESSES'], ['LYCÉE', 'EN LUTTE'], ['ON VEUT', 'ÉTUDIER'], ['36 PAR', 'CLASSE ?']]
      .map(ls => std({ map: signTex(ls, { w: 512, h: 340, bg: '#ece6d6', fg: '#16161a', font: 'bold 62px "DejaVu Sans Condensed"', tape: false, paint: true }), roughness: 0.9 }));
    const spots = [[-4.6, 11.6, 0.3], [-3.2, 12.4, 0.1], [-1.8, 11.9, -0.1], [-0.4, 12.8, 0.05], [1.4, 12.1, -0.2], [2.8, 12.9, -0.35], [4.6, 12.0, -0.5], [-5.8, 13.2, 0.4], [2.2, 13.9, -0.2], [-2.6, 14.0, 0.2], [3.6, 14.2, -0.3], [5.8, 13.6, -0.6], [-4.4, 15.2, 0.3], [4.9, 15.5, -0.4]];
    spots.forEach(([x, z, ry], k) => {
      const hasSign = [0, 2, 4, 7, 10].includes(k);
      const f = figure(THREE, { body: hoodies[(k * 3) % hoodies.length], head: M.head, dark: M.pants, shoe: M.shoe, pack: packs[k % packs.length], hair: M.pants, stick: std({ color: 0x8a7050 }) },
        { hood: k % 2 === 0, hair: k % 2 === 1, backpack: k % 3 !== 2, height: 1.62 + r() * 0.16, sign: hasSign ? placards[[0, 2, 4, 7, 10].indexOf(k)] : null, armsUp: hasSign ? 0 : (k === 5 ? 2 : k === 9 ? 1 : 0) });
      f.position.set(x, 0, z); f.rotation.y = Math.PI + ry; crowd.add(f);
    });
    // banner (bedsheet) tied along the fence
    const ban = new THREE.Mesh(new THREE.PlaneGeometry(5.6, 1.1, 24, 4), std({ map: signTex(['LYCÉE BLOQUÉ'], { w: 1400, h: 280, bg: '#e9e3d4', fg: '#141416', font: 'bold 150px "DejaVu Sans Condensed"', tape: false, paint: true }), roughness: 0.95, side: THREE.DoubleSide }));
    const bp = ban.geometry.attributes.position; for (let k = 0; k < bp.count; k++) { const x = bp.getX(k), y = bp.getY(k); bp.setZ(k, Math.sin(x * 1.3) * 0.06 + (y < 0 ? Math.sin(x * 2.1) * 0.04 : 0)); bp.setY(k, y - Math.cos(x / 2.8 * Math.PI / 2) * 0.0 - (1 - Math.abs(x) / 2.8) * 0.12); }
    ban.geometry.computeVertexNormals(); ban.position.set(-6.4, 1.25, 9.06); ban.castShadow = true; scene.add(ban);
  }
  const crowdBaked = outside ? bake(crowd) : crowd; if (outside) { scene.remove(crowd); scene.add(crowdBaked); }

  // bake the seated pupils per room (big draw-call saving)
  for (const k of Object.keys(rooms)) { const rm = rooms[k]; if (!rm.studs || rm.studs.children.length === 0) continue;
    if (k === 'heat') continue;    // keeps the fans attached
    const b = bake(rm.studs); rm.studs.parent.add(b); rm.studs.parent.remove(rm.studs); rm.studs = b; }

  // ------------------------------------------------------------------ global light
  scene.add(new THREE.HemisphereLight(0x5d6878, 0x0b0a09, outside ? 0.4 : 0.18));
  const moon = new THREE.DirectionalLight(0x8fa0b8, outside ? 0.5 : 0.7); moon.position.set(-30, 40, 40); scene.add(moon);
  const yardFill = new THREE.DirectionalLight(0xa9b0b8, shot === 'cut' ? 0.8 : 0.0); yardFill.position.set(10, 8, 40); scene.add(yardFill);

  for (const [l, sh] of [[emptySpot, 'empty_desk'], [leak.spot, 'leak'], [heat.sun, 'heat'], [wc.spot, 'toilets']]) l.castShadow = shot === sh;
  // which façade state per shot
  facade.visible = shot === 'cut' || outside;
  cutPlane.constant = 30;
  // interior shots don't need the street furniture in shadow passes
  const dofFocus = { crowded: 6.8, empty_desk: 5.4, leak: 6.0, heat: 4.8, toilets: 5.6, outside_blockade: 9.8 }[shot];
  const post = makeComposer(THREE, renderer, scene, camera, W, H, { bloom: shot === 'cut' ? 0.7 : 0.6, bloomRadius: 0.6, bloomThreshold: 0.8, exposure: 0.95,
    dof: dofFocus ? { focus: dofFocus, aperture: 0.0009, maxblur: 0.004 } : null });
  return { THREE, scene, camera, shot, rooms, lights, deskGlow, emptySpot, emptyBeam, motes, leak, heat, wc, cutPlane, cutLine, cutHalo, cutLight, facade, sodium, ...post };
}

const CAMS = {
  // [t, [px,py,pz, tx,ty,tz]]
  cut: [[0, [-30, 9, 34, -2, 5.2, -4]], [8, [-22, 8, 26, -1, 5.0, -4]]],
  crowded: [[0, [-10.2, 6.45, 1.9, -14.0, 3.9, -4.2]], [6, [-10.6, 6.35, 1.3, -14.2, 3.9, -4.3]]],
  empty_desk: [[0, [-3.4, 6.35, -0.5, -7.5, 4.3, -4.0]], [6, [-3.8, 6.3, -0.8, -7.5, 4.3, -4.0]]],
  leak: [[0, [-9.8, 8.9, 0.9, -13.4, 8.4, -4.9]], [7, [-10.3, 8.8, 0.4, -13.5, 8.4, -5.0]]],
  heat: [[0, [-4.4, 8.75, -0.2, -0.4, 8.35, -3.4]], [6, [-4.0, 8.7, -0.5, -0.4, 8.4, -3.2]]],
  toilets: [[0, [-10.2, 2.0, 2.4, -13.8, 1.3, -5.6]], [6, [-10.8, 1.9, 1.8, -13.6, 1.3, -5.7]]],
  outside_blockade: [[0, [-5.0, 2.7, 19.0, -0.3, 1.2, 9.4]], [7, [-3.4, 2.6, 18.4, 0.2, 1.2, 9.4]]],
};

export function update(ctx, t) {
  const { camera, shot } = ctx;
  const c = path(CAMS[shot] ?? CAMS.cut)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]);

  // fluorescent flicker in the toilets and one dying tube in the leak room
  for (const L of ctx.lights) {
    let k = 1;
    if (L.f === 0 && L.i === 0) { const s = Math.sin(t * 37.0) * Math.sin(t * 13.3 + 1.2); k = s > 0.82 ? 0.15 : 0.85 + 0.15 * Math.sin(t * 50); }
    L.light.intensity = L.base * k * ({ cut: 2.6, crowded: 1.3, leak: 1.3, outside_blockade: 1.6 }[shot] ?? 1);
    L.tubes.forEach((tb, j) => { if (L.base === 0) return; const kk = (L.f === 2 && L.i === 0 && j === 1) ? (Math.sin(t * 23) > 0.6 ? 0.2 : 1) : k; tb.material.color.setScalar(0.2 + 0.6 * kk); });
  }

  // ---------------- cut
  if (shot === 'cut') {
    const sx = -19.5 + 39 * sstep(1.4, 5.6, t);
    ctx.cutPlane.constant = -sx;
    const on = t > 1.3 && t < 5.8 ? 1 : 0;
    ctx.cutLine.visible = on > 0; ctx.cutLine.position.x = sx;
    ctx.cutHalo.forEach((h, k) => { h.material.opacity = 0.7 + 0.3 * Math.sin(t * 20 + k); });
    ctx.cutLight.intensity = 60 * on;
  }
  // ---------------- crowded: count-up 1..36
  if (shot === 'crowded') {
    ctx.deskGlow.forEach((d, k) => {
      const t0 = 0.6 + k * 0.1; const a = sstep(t0, t0 + 0.12, t);
      const flash = Math.exp(-Math.max(0, t - t0) * 4) * a;
      d.strip.material.opacity = 0.32 * a + 0.5 * flash; d.halo.material.opacity = 0.18 * a + 0.5 * flash;
    });
  } else ctx.deskGlow.forEach(d => { d.strip.material.opacity = 0; d.halo.material.opacity = 0; });
  // ---------------- empty desk
  const eOn = shot === 'empty_desk' ? sstep(1.0, 2.6, t) : 0;
  ctx.emptySpot.intensity = 45 * eOn; ctx.emptyBeam.material.uniforms.opacity.value = 0.09 * eOn; ctx.motes.material.opacity = 0.8 * eOn;
  ctx.motes.rotation.y = t * 0.05; ctx.motes.position.y += 0;
  // ---------------- leak
  const L = ctx.leak;
  L.spot.intensity = shot === 'leak' ? 40 * sstep(0.3, 1.6, t) : 0;
  L.holeGlow.material.opacity = shot === 'leak' ? 0.35 * sstep(0.3, 1.6, t) : 0;
  L.drops.forEach(d => { const p = ((t * d.rate + d.ph) % 1 + 1) % 1; const fall = p < 0.25 ? 0 : (p - 0.25) / 0.75; const y = d.top - (d.top - d.bot) * fall * fall;
    d.d.position.y = y; d.d.scale.set(1, p < 0.25 ? 0.6 + p * 3 : 1.8, 1); d.d.visible = p < 0.98; });
  L.rings.forEach(r => { const p = ((t * r.rate + 0.0) % 1 + 1) % 1; r.m.scale.setScalar(0.02 + p * 0.22); r.m.material.opacity = shot === 'leak' ? 0.6 * (1 - p) : 0; });
  { const p = clamp01((t - 2.0) / 4.0); L.rat.position.x = L.ratX - p * 7.6; L.rat.rotation.y = Math.PI; L.rat.position.y = L.ratY + Math.abs(Math.sin(t * 22)) * 0.012 * (p > 0 && p < 1 ? 1 : 0); L.rat.visible = shot !== 'leak' || (t > 1.9 && t < 6.2); }
  // ---------------- heat
  const H = ctx.heat;
  const temp = shot === 'heat' ? 24 + 14 * sstep(0.6, 4.4, t) : 31;
  H.liq.scale.y = 0.06 + 0.01375 * temp;
  const hOn = shot === 'heat' ? 1 : 0;
  H.sun.intensity = 110 * hOn * (0.7 + 0.3 * sstep(0.6, 4.4, t)); H.beams.forEach((b, k) => b.material.uniforms.opacity.value = 0.03 * hOn * (0.6 + 0.4 * Math.sin(k * 1.7 + t * 0.6)));
  H.glow.material.opacity = 0.45 * hOn * sstep(2.5, 4.4, t);
  (H.fan || []).forEach((f, k) => { f.rotation.y = 0.8 + Math.sin(t * 9 + k * 2) * 0.5; });
  // ---------------- toilets
  ctx.wc.spot.intensity = shot === 'toilets' ? 20 * sstep(0.8, 2.2, t) : 0;
}

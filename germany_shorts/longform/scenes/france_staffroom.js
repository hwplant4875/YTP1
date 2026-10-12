// France 2026: the teachers' room (salle des profs) after hours. Faceless by construction: there are no people at all.
// Room: x -5..5, z -4..4, back wall z = -4 with the staff board (name tags) and pigeonholes. 1 unit = 1 m.
// shots (?shot=name or name:seconds):
//   staffroom (8 s)  low dolly along the empty staff table toward the staff board; several name tags are blank and
//                    one by one pick up an amber glow (unfilled posts). Coffee cups, a cold radiator, blinds.
//   tags_fall (7 s)  close on the staff board: tags come loose and drop out of their slots, leaving amber-lit gaps
//                    (post cuts in the 2027 budget).
import { AMBER } from './lib.js';
import { glow, beam } from './look.js';
import { AMBER_HI, path, clamp01, sstep, fontsReady, finishPost, ctex, spacedText, timing, ease } from './france_lib.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

export async function setup(THREE, renderer, W, H) {
  const { name, k: k0 } = timing(8);
  const shot = name || 'staffroom';
  const k = shot === 'tags_fall' ? k0 * 8 / 7 : k0;
  await fontsReady();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x07080a);
  scene.fog = new THREE.FogExp2(0x07080a, 0.05);
  const camera = new THREE.PerspectiveCamera(shot === 'tags_fall' ? 34 : 36, W / H, 0.02, 100);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.8, metalness: 0.02, ...o });
  let seed = 3; const R = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  const add = (geo, mat, x, y, z, ry = 0) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.rotation.y = ry; m.castShadow = m.receiveShadow = true; scene.add(m); return m; };
  const ctx = { THREE, scene, camera, shot, k };

  // ------------------------------------------------------------------ room shell
  const wallT = ctex(THREE, 1024, 512, (g, w, h) => { g.fillStyle = '#a39c8d'; g.fillRect(0, 0, w, h * 0.66); g.fillStyle = '#6a6e64'; g.fillRect(0, h * 0.66, w, h * 0.34);
    for (let i = 0; i < 9000; i++) { const v = R() * 40 - 20; g.fillStyle = `rgba(${100 + v},${96 + v},${88 + v},0.07)`; g.fillRect(R() * w, R() * h, 3, 3); }
    for (let i = 0; i < 10; i++) { const x = R() * w; const grd = g.createLinearGradient(0, 0, 0, 200); grd.addColorStop(0, 'rgba(110,86,50,0.25)'); grd.addColorStop(1, 'rgba(110,86,50,0)'); g.fillStyle = grd; g.fillRect(x, 0, 30 + R() * 60, 200); } }, { repeat: [2, 1] });
  const wallM = std({ map: wallT, roughness: 0.92 });
  const floorT = ctex(THREE, 512, 512, (g, w, h) => { for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { const v = (x + y) % 2 ? 96 : 84; g.fillStyle = `rgb(${v},${v - 6},${v - 14})`; g.fillRect(x * 64, y * 64, 64, 64); }
    for (let i = 0; i < 3000; i++) { g.fillStyle = `rgba(30,26,22,${R() * 0.12})`; g.fillRect(R() * w, R() * h, 2, 2); } }, { repeat: [5, 4] });
  const fl = new THREE.Mesh(new THREE.PlaneGeometry(10, 8), std({ map: floorT, roughness: 0.45 })); fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true; scene.add(fl);
  const back = new THREE.Mesh(new THREE.PlaneGeometry(10, 3), wallM); back.position.set(0, 1.5, -4); back.receiveShadow = true; scene.add(back);
  const left = new THREE.Mesh(new THREE.PlaneGeometry(8, 3), wallM); left.position.set(-5, 1.5, 0); left.rotation.y = Math.PI / 2; left.receiveShadow = true; scene.add(left);
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(10, 8), std({ color: 0x9a968c })); ceil.rotation.x = Math.PI / 2; ceil.position.y = 3; scene.add(ceil);
  // right wall: window with blinds (cold night light)
  const rw = new THREE.Group(); scene.add(rw);
  { const m = wallM; const a = new THREE.Mesh(new THREE.PlaneGeometry(8, 0.9), m); a.position.set(5, 0.45, 0); a.rotation.y = -Math.PI / 2; rw.add(a);
    const b = new THREE.Mesh(new THREE.PlaneGeometry(8, 0.5), m); b.position.set(5, 2.75, 0); b.rotation.y = -Math.PI / 2; rw.add(b);
    for (let z = -3.8; z < 3.9; z += 0.09) { const sl = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.05, 0.085), std({ color: 0xc9c4b8 })); }
    const blinds = []; for (let y = 0.95; y < 2.5; y += 0.06) { const sl = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.012, 7.6), std({ color: 0xbdb7aa, roughness: 0.6 })); sl.position.set(4.95, y, 0); sl.rotation.z = 0.6; sl.castShadow = true; rw.add(sl); } }
  const radiator = add(new THREE.BoxGeometry(1.6, 0.6, 0.1), std({ color: 0xb9b3a6, roughness: 0.5 }), -2.2, 0.45, -3.92);

  // ------------------------------------------------------------------ staff table + chairs + clutter
  const wood = std({ color: 0x8a6c4c, roughness: 0.55 }); const metal = std({ color: 0x55585a, metalness: 0.6, roughness: 0.45 });
  const table = add(new THREE.BoxGeometry(1.4, 0.05, 5.2), wood, 0.6, 0.75, 0.6);
  for (const x of [-0.05, 1.25]) for (const z of [-1.8, 3.0]) add(new THREE.BoxGeometry(0.05, 0.75, 0.05), metal, x, 0.375, z);
  const chairG = new THREE.Group();
  const chair = (x, z, ry) => { const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = ry; chairG.add(g);
    const s = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.04, 0.42), std({ color: 0x3f4a52 })); s.position.y = 0.46; g.add(s);
    const b = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.36, 0.03), std({ color: 0x3f4a52 })); b.position.set(0, 0.72, -0.2); g.add(b);
    for (const sx of [-0.18, 0.18]) for (const sz of [-0.18, 0.18]) { const l = new THREE.Mesh(new THREE.BoxGeometry(0.025, 0.46, 0.025), metal); l.position.set(sx, 0.23, sz); g.add(l); } };
  for (let i = 0; i < 6; i++) { chair(-0.35, -1.4 + i * 0.85, Math.PI / 2 + (R() - 0.5) * 0.4); chair(1.55, -1.4 + i * 0.85, -Math.PI / 2 + (R() - 0.5) * 0.4); }
  chairG.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } }); scene.add(chairG);
  const cup = std({ color: 0xd8d2c4, roughness: 0.4 });
  for (const [x, z] of [[0.3, -0.6], [1.0, 0.9], [0.45, 2.1], [0.9, -1.5]]) add(new THREE.CylinderGeometry(0.04, 0.035, 0.09, 18), cup, x, 0.82, z);
  for (const [x, z, r] of [[0.7, 0.1, 0.2], [0.4, 1.4, -0.3], [0.95, 2.6, 0.5]]) add(new THREE.BoxGeometry(0.3, 0.012, 0.21), std({ color: 0xece7da }), x, 0.782, z, r);
  add(new THREE.BoxGeometry(0.5, 0.06, 0.35), std({ color: 0x2e3a4e }), 0.5, 0.81, -0.2, 0.15);   // a stack of copies
  // coffee machine on a counter by the left wall
  add(new THREE.BoxGeometry(0.6, 0.9, 2.4), std({ color: 0x6b655c }), -4.6, 0.45, 1.6);
  add(new THREE.BoxGeometry(0.35, 0.45, 0.35), std({ color: 0x1d1e20, metalness: 0.5, roughness: 0.4 }), -4.55, 1.12, 1.0);
  const led = glow(THREE, 0xff5a2a, 0.06, 1); led.position.set(-4.36, 1.2, 1.0); scene.add(led);

  // ------------------------------------------------------------------ staff board: 6 rows x 12 name tags, + pigeonholes
  const board = new THREE.Group(); board.position.set(0.9, 1.75, -3.94); scene.add(board);
  const BW = 3.9, BH = 1.55;
  add(new THREE.BoxGeometry(BW + 0.12, BH + 0.12, 0.04), std({ color: 0x5a544a, metalness: 0.3 }), board.position.x, board.position.y, -3.97);
  const cork = new THREE.Mesh(new THREE.PlaneGeometry(BW, BH), std({ map: ctex(THREE, 512, 256, (g, w, h) => { g.fillStyle = '#6e5639'; g.fillRect(0, 0, w, h); for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${40 + R() * 60},${30 + R() * 40},${20},0.3)`; g.fillRect(R() * w, R() * h, 2, 2); } }), roughness: 0.95 }));
  cork.position.z = 0.015; board.add(cork);
  const header = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 0.16), new THREE.MeshBasicMaterial({ map: ctex(THREE, 512, 52, (g, w, h) => { g.fillStyle = '#efe7d6'; g.fillRect(0, 0, w, h); g.fillStyle = '#1a1a1a'; g.font = '700 30px Inter, sans-serif'; g.textBaseline = 'middle'; spacedText(g, 'ÉQUIPE PÉDAGOGIQUE', 16, h / 2 + 1, 4); }), toneMapped: true }));
  header.position.set(-BW / 2 + 0.9, BH / 2 - 0.13, 0.03); board.add(header);
  const tagTex = (filled, s) => ctex(THREE, 256, 96, (g, w, h) => { g.fillStyle = filled ? '#ece6d8' : '#e9e4d8'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(0,0,0,0.12)'; g.fillRect(0, h - 6, w, 6);
    if (filled) { g.fillStyle = 'rgba(30,30,32,0.75)'; g.fillRect(18, 26, 90 + (s % 5) * 18, 14); g.fillStyle = 'rgba(30,30,32,0.4)'; g.fillRect(18, 52, 60 + (s % 3) * 20, 10); } });
  const filledMats = [0, 1, 2, 3, 4, 5, 6].map(s => std({ map: tagTex(true, s), roughness: 0.7 }));
  const blankMat = std({ map: tagTex(false, 0), roughness: 0.7, emissive: new THREE.Color(AMBER_HI), emissiveIntensity: 0 });
  const tagGeo = new RoundedBoxGeometry(0.27, 0.1, 0.008, 2, 0.003);
  const tags = [];
  const blanks = new Set([4, 9, 15, 22, 27, 33, 40, 46, 51, 58, 63, 69]);
  const falls = new Set([2, 7, 13, 18, 25, 30, 37, 44, 49, 55, 61, 66, 70]);
  const slotM = std({ color: 0x3a2c1c, roughness: 1 });
  for (let r = 0; r < 6; r++) for (let c = 0; c < 12; c++) {
    const i = r * 12 + c; const x = -BW / 2 + 0.24 + c * 0.312, y = BH / 2 - 0.36 - r * 0.2;
    const slot = new THREE.Mesh(new THREE.PlaneGeometry(0.29, 0.12), slotM); slot.position.set(x, y, 0.017); board.add(slot);
    const isBlank = blanks.has(i);
    const m = new THREE.Mesh(tagGeo, isBlank ? blankMat : filledMats[i % 7]); m.position.set(x, y, 0.026); m.castShadow = true; board.add(m);
    const pin = new THREE.Mesh(new THREE.SphereGeometry(0.008, 8, 6), std({ color: 0xb03a2a })); pin.position.set(x, y + 0.035, 0.034); board.add(pin);
    tags.push({ m, pin, isBlank, falls: falls.has(i), x, y, i, ord: [...falls].indexOf(i) });
  }
  ctx.tags = tags; ctx.blankMat = blankMat;
  // gap glows where tags fall
  ctx.gapGlows = tags.filter(t => t.falls).map(t => { const s = glow(THREE, AMBER, 0.5, 0.9); s.position.set(board.position.x + t.x, board.position.y + t.y, -3.9); s.material.opacity = 0; scene.add(s); return { s, t }; });
  // pigeonholes to the left of the board
  { const ph = new THREE.Group(); ph.position.set(-3.0, 1.2, -3.78); scene.add(ph);
    const pm = std({ color: 0x8a7a62, roughness: 0.7 });
    for (let r = 0; r <= 5; r++) { const b = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.02, 0.4), pm); b.position.set(0, r * 0.28, 0); ph.add(b); }
    for (let c = 0; c <= 6; c++) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.02, 1.4, 0.4), pm); b.position.set(-0.9 + c * 0.3, 0.7, 0); ph.add(b); }
    for (let r = 0; r < 5; r++) for (let c = 0; c < 6; c++) if (R() < 0.45) { const p = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.02 + R() * 0.06, 0.3), std({ color: 0xe2dccd })); p.position.set(-0.75 + c * 0.3, r * 0.28 + 0.04, 0.02); ph.add(p); }
    ph.traverse(o => { if (o.isMesh) o.castShadow = o.receiveShadow = true; }); }

  // ------------------------------------------------------------------ light
  scene.add(new THREE.HemisphereLight(0x7f8a9c, 0x0d0c0a, 0.4));
  const moon = new THREE.SpotLight(0x9fb2cc, 50, 16, 0.7, 0.8, 1.4); moon.position.set(7, 2.6, 0.5); moon.target.position.set(0, 0.6, 0); moon.castShadow = true; moon.shadow.mapSize.set(2048, 2048); moon.shadow.bias = -0.0004; scene.add(moon, moon.target);
  // one fluorescent fixture left on over the board
  const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.2, 8), new THREE.MeshBasicMaterial({ color: 0xf2f6f8 })); tube.rotation.z = Math.PI / 2; tube.position.set(0.9, 2.92, -2.8); scene.add(tube);
  const boardLight = new THREE.SpotLight(0xe8eef2, 3.5, 8, 0.75, 0.9, 1.6); boardLight.position.set(0.9, 2.9, -2.6); boardLight.target.position.set(0.9, 1.6, -4); boardLight.castShadow = true; boardLight.shadow.mapSize.set(1024, 1024); scene.add(boardLight, boardLight.target);
  const amberPt = new THREE.PointLight(AMBER, 0, 3.5, 1.8); amberPt.position.set(0.9, 1.75, -2.9); scene.add(amberPt); ctx.amberPt = amberPt;
  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.6, bloomRadius: 0.55, bloomThreshold: 0.75,
    dof: { focus: shot === 'tags_fall' ? 1.9 : 6.0, aperture: 0.0012, maxblur: 0.005 } });
  return Object.assign(ctx, post);
}

const CAMS = {
  staffroom: [[0, [3.4, 1.3, 3.9, 0.4, 1.4, -3.5]], [8, [2.4, 1.45, 1.6, 0.6, 1.55, -3.9]]],
  tags_fall: [[0, [1.5, 1.8, -1.8, 0.8, 1.68, -4]], [7, [1.25, 1.72, -2.1, 0.75, 1.66, -4]]],
};

export function update(ctx, tt) {
  const { camera, shot } = ctx;
  const t = tt / ctx.k;
  const c = path(CAMS[shot] ?? CAMS.staffroom)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  let hot = 0;
  if (shot === 'staffroom') {
    const g = sstep(2.2, 4.5, t); ctx.blankMat.emissiveIntensity = 0.55 * g; hot = g;
    ctx.gapGlows.forEach(G => G.s.material.opacity = 0);
    ctx.tags.forEach(T => { T.m.visible = true; });
  } else {
    ctx.blankMat.emissiveIntensity = 0.0;
    ctx.tags.forEach((T) => { if (!T.falls) return; const a = 1.0 + T.ord * 0.32; const p = clamp01((t - a) / 1.1);
      T.m.position.set(T.x + p * 0.05, T.y - 2.2 * p * p, 0.026 + p * 0.25); T.m.rotation.set(p * 1.2, 0, p * (T.i % 2 ? 1.6 : -1.3)); T.m.visible = T.m.position.y > -1.8;
      T.pin.visible = p < 0.05; });
    ctx.gapGlows.forEach(G => { const a = 1.0 + G.t.ord * 0.32; G.s.material.opacity = 0.75 * sstep(a + 0.1, a + 0.6, t); hot = Math.max(hot, sstep(a, a + 0.6, t)); });
  }
  ctx.amberPt.intensity = (shot === "tags_fall" ? 0.7 : 2.0) * hot;
}

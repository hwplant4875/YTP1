// Tunnel 29 (1962): an escape tunnel dug from a West Berlin factory, under Bernauer Straße and the death strip,
// up into a cellar in East Berlin. West is +x, East is -x.
// shots:
//   street   - night, street level: the Wall, searchlights, the factory; slow push in
//   reveal   - camera sinks from the street through the ground and finds the tunnel far below
//   section  - wide cut-away, slow dolly; figures crawl from the East cellar to the West shaft
//   crawl    - point of view crawling through the tunnel, bulbs and timber props passing
//   dig      - close on a digger at the clay face, scraping by lamplight
//   water    - the tunnel floods: water rising, bulbs reflected
//   camera   - a film camera on a tripod in the tunnel, backlit, waiting
//   cellar   - the East cellar: a hole in the floor glows from below, a head rises out of it
//   thumb    - thumbnail framing of the cut-away
import { AMBER, concreteTex, rng, lerp, person } from './lib.js';
import { makeComposer, glow, beam, normalFromHeight, borderGuard, smooth, flicker } from './look.js';

const DEPTH = -7, TH = 1.15, TW = 0.95;          // tunnel floor y, height, width
const XW = 26, XE = -24;                          // West shaft x, East cellar x

export async function setup(THREE, renderer, W, H) {
  const shot = new URLSearchParams(location.search).get('shot') || 'section';
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050506);
  const inside = ['crawl', 'dig', 'water', 'camera'].includes(shot);
  const cellar = shot === 'cellar';
  scene.fog = cellar ? new THREE.FogExp2(0x060505, 0.05) : inside ? new THREE.FogExp2(0x070605, 0.11) : new THREE.Fog(0x050506, 70, 200);
  const camera = new THREE.PerspectiveCamera(inside || cellar ? 50 : 30, W / H, 0.03, 600);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.9, metalness: 0, ...o });
  const r = rng(29);

  // ---- materials
  const clayTex = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d');
    g.fillStyle = '#6b5e4e'; g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 14000; i++) { const v = 60 + r() * 70; g.fillStyle = `rgba(${v + 12},${v + 6},${v - 4},0.45)`; g.fillRect(r() * 512, r() * 512, 1 + r() * 3, 1 + r() * 3); }
    for (let i = 0; i < 70; i++) { g.strokeStyle = `rgba(40,34,28,${0.2 + r() * 0.3})`; g.lineWidth = 1 + r() * 3; g.beginPath();
      const x = r() * 512, y = r() * 512; g.moveTo(x, y); g.lineTo(x + (r() - 0.5) * 60, y + (r() - 0.5) * 20); g.stroke(); }   // spade marks
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const clayN = normalFromHeight(THREE, 256, 256, (g, w, h) => {
    g.fillStyle = '#777'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 400; i++) { const v = r() * 255; g.fillStyle = `rgba(${v},${v},${v},0.5)`; g.beginPath(); g.ellipse(r() * w, r() * h, 2 + r() * 14, 1 + r() * 6, r() * 3, 0, 7); g.fill(); }
  }, 2.5);
  const clay = (rep) => { const m = std({ map: clayTex.clone(), normalMap: clayN.clone(), roughness: 0.95 }); m.map.repeat.set(...rep); m.normalMap.repeat.set(...rep); m.map.needsUpdate = m.normalMap.needsUpdate = true; return m; };
  const woodTex = (() => {
    const c = document.createElement('canvas'); c.width = 64; c.height = 256; const g = c.getContext('2d');
    g.fillStyle = '#7a6448'; g.fillRect(0, 0, 64, 256);
    for (let i = 0; i < 40; i++) { g.strokeStyle = `rgba(40,30,20,${0.2 + r() * 0.4})`; g.lineWidth = 1 + r() * 2; g.beginPath(); const x = r() * 64; g.moveTo(x, 0); g.bezierCurveTo(x + 6, 80, x - 6, 170, x + 3, 256); g.stroke(); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const wood = std({ map: woodTex, roughness: 0.85 });
  const dark = std({ color: 0x0d0d0d, roughness: 0.7 });

  // ---- the tunnel: clay box open at the front for the cut-away, props every 1.4 m
  const LEN = XW - XE;
  const tunnel = new THREE.Group(); scene.add(tunnel);
  const tb = (w, h, d, x, y, z, m) => { const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); b.position.set(x, y, z); b.receiveShadow = true; b.castShadow = true; tunnel.add(b); return b; };
  const cx = (XW + XE) / 2;
  tb(LEN, 0.25, TW + 0.5, cx, DEPTH - 0.125, 0, clay([LEN / 3, 1]));                         // floor
  tb(LEN, 0.25, TW + 0.5, cx, DEPTH + TH + 0.125, 0, clay([LEN / 3, 1]));                    // roof
  tb(LEN, TH, 0.25, cx, DEPTH + TH / 2, -TW / 2 - 0.125, clay([LEN / 3, 1]));               // back wall
  if (inside) tb(LEN, TH, 0.25, cx, DEPTH + TH / 2, TW / 2 + 0.125, clay([LEN / 3, 1]));    // front wall only when we're in it
  // floor boards and a rail for the sand cart
  for (let x = XE + 0.5; x < XW - 0.5; x += 0.42) tb(0.38, 0.03, TW * 0.8, x, DEPTH + 0.015, 0, wood);
  const props = new THREE.InstancedMesh(new THREE.BoxGeometry(0.1, TH, 0.1), wood, 400);
  const caps = new THREE.InstancedMesh(new THREE.BoxGeometry(0.1, 0.1, TW + 0.1), wood, 200);
  const m4 = new THREE.Matrix4(); let ip = 0, ic = 0;
  for (let x = XE + 1; x < XW - 1; x += 1.4) {
    for (const z of [-TW / 2 + 0.05, TW / 2 - 0.05]) { m4.makeRotationZ((r() - 0.5) * 0.05); m4.setPosition(x + (r() - 0.5) * 0.08, DEPTH + TH / 2, z); props.setMatrixAt(ip++, m4); }
    m4.makeTranslation(x, DEPTH + TH - 0.05, 0); caps.setMatrixAt(ic++, m4);
  }
  props.count = ip; caps.count = ic; props.castShadow = caps.castShadow = true; tunnel.add(props, caps);
  // electric cable and bulbs along the roof
  const cable = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, LEN), dark); cable.rotation.z = Math.PI / 2; cable.position.set(cx, DEPTH + TH - 0.14, -0.3); tunnel.add(cable);
  const bulbs = [], lights = [];
  const bulbMat = new THREE.MeshBasicMaterial({ color: AMBER });
  for (let x = XE + 2, i = 0; x < XW - 1; x += 3.2, i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.035, 10, 8), bulbMat); b.position.set(x, DEPTH + TH - 0.22, -0.3); tunnel.add(b);
    const halo = glow(THREE, AMBER, inside ? 0.38 : 1.6, 0.9); halo.position.copy(b.position); tunnel.add(halo);
    bulbs.push({ x, b, halo, seed: i * 1.7 });
  }

  // ---- shafts: West (factory cellar, a ladder) and East (cellar floor)
  for (let y = DEPTH; y < -0.6; y += 0.35) tb(0.5, 0.04, 0.04, XW + 0.6, y, -0.45, wood);
  for (const z of [-0.6, -0.3]) tb(0.04, -DEPTH, 0.04, XW + 0.6 + (z + 0.45) * 0.4, DEPTH / 2, -0.45, wood);

  // ---- earth block (cut face toward camera), with the tunnel and shafts as dark cavities in front of it
  const earthTex = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d');
    const grd = g.createLinearGradient(0, 0, 0, 512); grd.addColorStop(0, '#6a5e50'); grd.addColorStop(0.3, '#7d6e5c'); grd.addColorStop(1, '#5a4f44');
    g.fillStyle = grd; g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 9000; i++) { const v = 50 + r() * 60; g.fillStyle = `rgba(${v + 8},${v + 4},${v},0.45)`; g.fillRect(r() * 512, r() * 512, 1 + r() * 3, 1 + r() * 3); }
    for (let i = 0; i < 50; i++) { g.fillStyle = `rgba(90,82,72,${0.2 + r() * 0.3})`; g.beginPath(); g.ellipse(r() * 512, r() * 512, 3 + r() * 10, 2 + r() * 6, r() * 3, 0, 7); g.fill(); }
    for (let y = 60; y < 512; y += 70 + r() * 40) { g.fillStyle = `rgba(30,26,22,0.25)`; g.fillRect(0, y, 512, 2 + r() * 4); }   // strata
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(5, 1); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  earthTex.repeat.set(1 / 22, 1 / 16); earthTex.offset.set(0.5, 1);    // world units: one tile = 22 m x 16 m
  const earth = std({ map: earthTex });
  const BL = 110, BOT = -16, ZF = TW / 2 + 0.25;
  const CW = [XW - 0.3, XW + 4], CE = [XE - 4, XE + 1.2];                 // cellar spans (x)
  if (!inside && shot !== 'street') {
    // one continuous cut face with the cavities as holes, so the strata line up across the whole section
    const face = new THREE.Shape([new THREE.Vector2(-BL / 2, BOT), new THREE.Vector2(BL / 2, BOT), new THREE.Vector2(BL / 2, 0), new THREE.Vector2(-BL / 2, 0)]);
    // a single hole tracing tunnel, both shafts and both cellars (overlapping holes break triangulation)
    const P = [[XE - 0.2, DEPTH], [XW + 1.2, DEPTH], [XW + 1.2, -3.4], [CW[1], -3.4], [CW[1], -0.05], [CW[0], -0.05], [CW[0], -3.4], [XW, -3.4],
               [XW, DEPTH + TH], [XE + 0.6, DEPTH + TH], [XE + 0.6, -3.4], [CE[1], -3.4], [CE[1], -0.05], [CE[0], -0.05], [CE[0], -3.4], [XE - 0.2, -3.4]];
    face.holes.push(new THREE.Path(P.reverse().map(([x, y]) => new THREE.Vector2(x, y))));
    const fm = new THREE.Mesh(new THREE.ShapeGeometry(face), earth); fm.position.z = ZF; fm.receiveShadow = true; scene.add(fm);
    // depth behind the face and the shaft walls
    const back = new THREE.Mesh(new THREE.PlaneGeometry(BL, -BOT), std({ color: 0x1a1714 })); back.position.set(0, BOT / 2, -14); scene.add(back);
    const sw = (x0, x1, y0, y1) => { const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, 0.1), clay([1, 3])); m.position.set((x0 + x1) / 2, (y0 + y1) / 2, -TW / 2 - 0.2); m.receiveShadow = true; scene.add(m); };
    sw(XW, XW + 1.2, DEPTH + TH, -3.3); sw(XE - 0.2, XE + 0.6, DEPTH + TH, -3.3);
    // a cap over the cut so the top edge reads as a clean slab of street
    const lip = new THREE.Mesh(new THREE.BoxGeometry(BL, 0.14, 0.14), std({ color: 0x2b2a28 })); lip.position.set(0, -0.07, ZF - 0.07); scene.add(lip);
  }
  // cellars: West factory cellar and East house cellar (rooms cut open at the front)
  const conc = std({ map: concreteTex(THREE, [2, 1], 5, 78), color: 0x6a6a6a, roughness: 0.95 });
  const room = (x0, x1, gap) => {
    const g = new THREE.Group(); scene.add(g);
    const b = (w, h, d, x, y, z, m) => { const q = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); q.position.set(x, y, z); q.receiveShadow = true; g.add(q); return q; };
    const D = 3 + ZF, zc = (ZF - 3) / 2;
    if (gap) {   // floor with an opening over the shaft: [gx0, gx1] x [gz0, ZF]
      const [gx0, gx1, gz0] = gap;
      b(gx0 - x0, 0.2, D, (x0 + gx0) / 2, -3.5, zc, conc); b(x1 - gx1, 0.2, D, (gx1 + x1) / 2, -3.5, zc, conc);
      b(gx1 - gx0, 0.2, gz0 + 3, (gx0 + gx1) / 2, -3.5, (gz0 - 3) / 2, conc);
    } else b(x1 - x0, 0.2, D, (x0 + x1) / 2, -3.5, zc, conc);
    b(x1 - x0, 0.2, D, (x0 + x1) / 2, 0.05, zc, conc); b(x1 - x0, 3.6, 0.2, (x0 + x1) / 2, -1.7, -3, conc);
    b(0.2, 3.6, D, x0, -1.7, zc, conc); b(0.2, 3.6, D, x1, -1.7, zc, conc);
    return g;
  };
  if (!inside && shot !== 'street') { room(CW[0], CW[1], [XW, XW + 1.2, -0.75]); room(CE[0], CE[1], [XE - 0.2, XE + 0.6, -0.75]); }
  // East cellar: a hole in the floor, light coming up through it
  const holeGlow = glow(THREE, AMBER, 2.2, 0.0); holeGlow.position.set(XE + 0.2, -3.1, 0); scene.add(holeGlow);
  const holeLight = new THREE.PointLight(AMBER, 0, 6, 1.5); holeLight.position.set(XE + 0.2, -3.6, 0); scene.add(holeLight);
  const holeBeam = beam(THREE, AMBER, 3, 0.9, 0.0); holeBeam.rotation.x = Math.PI; holeBeam.position.set(XE + 0.2, -3.2, 0); scene.add(holeBeam);

  // ---- street level: Bernauer Straße at night
  const ground = std({ map: concreteTex(THREE, [12, 3], 12, 64) });
  const gz0 = shot === 'street' ? 40 : ZF; const gb = new THREE.Mesh(new THREE.BoxGeometry(BL, 0.12, gz0 + 30), ground); gb.position.set(0, -0.06, (gz0 - 30) / 2); gb.receiveShadow = true; scene.add(gb);
  const wallMat = std({ map: concreteTex(THREE, [12, 1], 8, 150), roughness: 0.8 });
  const wall = new THREE.Group();
  for (let z = -40; z < 20; z += 1.2) { const s = new THREE.Mesh(new THREE.BoxGeometry(0.2, 3.6, 1.21), wallMat); s.position.set(0, 1.8, z); s.castShadow = true; wall.add(s); }
  const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 60, 16), wallMat); pipe.rotation.x = Math.PI / 2; pipe.position.set(0, 3.7, -10); wall.add(pipe);
  wall.position.x = 6; scene.add(wall);
  // death strip: raked sand, lamp posts, a watchtower, a second fence
  const sand = std({ color: 0x8b8478, roughness: 1 }); const st = new THREE.Mesh(new THREE.BoxGeometry(12, 0.02, 60), sand); st.position.set(-1, 0.13, -10); scene.add(st);
  const fence = std({ color: 0x5a5a5a, metalness: 0.4, roughness: 0.6 });
  for (let z = -40; z < 20; z += 2.5) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.6), fence); p.position.set(-7.5, 1.3, z); scene.add(p); }
  const tm = std({ color: 0x8c8a85 });
  const tower = new THREE.Group(); tower.position.set(-3, 0, -9); scene.add(tower);
  const sh_ = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 7.5, 16), tm); sh_.position.y = 3.75; tower.add(sh_);
  const cab = new THREE.Mesh(new THREE.CylinderGeometry(1.25, 1.25, 1.7, 8), tm); cab.position.y = 8.3; tower.add(cab);
  const tg = new THREE.Mesh(new THREE.CylinderGeometry(1.27, 1.27, 0.6, 8, 1, true), new THREE.MeshBasicMaterial({ color: 0x2a2d30 })); tg.position.y = 8.5; tower.add(tg);
  const search = new THREE.SpotLight(0xdfe6ee, 260, 70, 0.13, 0.4, 1.2); search.position.set(-3, 9.4, -8); scene.add(search, search.target);
  search.castShadow = true;
  const searchBeam = beam(THREE, 0xdfe6ee, 30, 3.6, 0.05); scene.add(searchBeam);
  for (let z = -36; z <= 16; z += 13) {
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 6), tm); pole.position.set(-5.5, 3, z); scene.add(pole);
    const sl = new THREE.SpotLight(0xbfcad6, 30, 16, 0.85, 0.7, 1.5); sl.position.set(-5.5, 6, z); sl.target.position.set(-2, 0, z); scene.add(sl, sl.target);
    const hd = glow(THREE, 0xcfd8e0, 1.2, 0.6); hd.position.set(-5.5, 6, z); scene.add(hd);
  }
  for (let z = -30; z <= 12; z += 14) {
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.09, 6.5), tm); pole.position.set(13, 3.25, z); scene.add(pole);
    const arm = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.08, 0.08), tm); arm.position.set(12.3, 6.5, z); scene.add(arm);
    const l = new THREE.SpotLight(0xffb060, 70, 26, 0.9, 0.6, 1.4); l.position.set(11.6, 6.4, z); l.target.position.set(7, 0, z); scene.add(l, l.target);
    const hd = glow(THREE, 0xffb060, 1.6, 0.8); hd.position.set(11.6, 6.4, z); scene.add(hd);
  }
  // buildings: West factory (one warm window) and East tenements (dark, windows bricked)
  const bld = std({ color: 0x38383a, roughness: 0.95 });
  const factory = new THREE.Mesh(new THREE.BoxGeometry(14, 9, 12), bld); factory.position.set(XW + 2, 4.5, -10); scene.add(factory);
  const win = new THREE.MeshBasicMaterial({ color: AMBER }); const ww = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.9), win); ww.position.set(XW - 3.2, 1.6, -3.99); scene.add(ww);
  const wwGlow = glow(THREE, AMBER, 3, 0.5); wwGlow.position.set(XW - 3.2, 1.6, -3.9); scene.add(wwGlow);
  for (let x = -BL / 2 + 4; x < -8; x += 8) { const h = 12 + r() * 6; const b = new THREE.Mesh(new THREE.BoxGeometry(7.6, h, 10), bld); b.position.set(x, h / 2, -10); scene.add(b); }
  for (let x = 14; x < BL / 2; x += 9) { if (Math.abs(x - XW - 2) < 9) continue; const h = 10 + r() * 6; const b = new THREE.Mesh(new THREE.BoxGeometry(8, h, 10), bld); b.position.set(x, h / 2, -12); scene.add(b); }

  // ---- people
  const figMat = std({ color: 0x141312, roughness: 0.8 });
  const crawlers = [];
  for (let i = 0; i < 5; i++) {
    const p = person(THREE, figMat, { height: 1.62, cap: false });
    p.rotation.z = -Math.PI / 2;               // lying along +x, head first toward the West
    p.scale.setScalar(0.92);
    p.traverse(o => { o.castShadow = true; });
    tunnel.add(p); crawlers.push({ p, off: i * 2.6 });
  }
  const digger = person(THREE, figMat, { height: 1.7, cap: false });
  digger.rotation.z = Math.PI / 2;   // prone, head toward the East face
  digger.traverse(o => { o.castShadow = true; });
  scene.add(digger);
  const spade = new THREE.Group(); scene.add(spade);
  const handle = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.7), wood); handle.position.y = 0.35; spade.add(handle);
  const blade = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.2, 0.01), std({ color: 0x8a8a8a, metalness: 0.9, roughness: 0.35 })); blade.position.y = -0.08; spade.add(blade);
  // the clay face for the digging shot, and a ladder sticking out of the East hole
  const face = new THREE.Mesh(new THREE.BoxGeometry(0.3, TH, TW), clay([0.5, 0.5])); face.position.set(XE + 3.85, DEPTH + TH / 2, 0); face.visible = shot === 'dig'; scene.add(face);
  const ladder = new THREE.Group(); ladder.position.set(XE + 0.2, -3.4, -0.3); ladder.rotation.z = -0.15; scene.add(ladder);
  for (const dz of [-0.2, 0.2]) { const rl = new THREE.Mesh(new THREE.BoxGeometry(0.05, 2.6, 0.05), wood); rl.position.set(0, -0.5, dz); ladder.add(rl); }
  for (let y = -1.6; y < 0.8; y += 0.3) { const rg = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.04, 0.4), wood); rg.position.set(0, y, 0); ladder.add(rg); }
  // film camera on a tripod (NBC)
  const cam = new THREE.Group(); scene.add(cam);
  const cbody = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.2, 0.15), dark); cbody.position.y = 0.74; cam.add(cbody);
  const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.05, 0.14, 20), dark); lens.rotation.z = Math.PI / 2; lens.position.set(-0.21, 0.75, 0); cam.add(lens);
  const hood = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.13, 0.13), dark); hood.position.set(-0.3, 0.75, 0); cam.add(hood);
  for (const [x, y] of [[-0.05, 0.93], [0.13, 0.93]]) { const reel = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.04, 28), dark); reel.rotation.x = Math.PI / 2; reel.position.set(x, y, 0); cam.add(reel); }
  const head = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.06, 12), dark); head.position.y = 0.61; cam.add(head);
  for (const a of [0, 2.1, 4.2]) { const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.66), dark); leg.position.set(Math.cos(a) * 0.1, 0.3, Math.sin(a) * 0.1); leg.rotation.set(-Math.sin(a) * 0.32, 0, Math.cos(a) * 0.32); cam.add(leg); }
  cam.traverse(o => { o.castShadow = true; });
  // water surface for the flood
  const waterMat = new THREE.MeshStandardMaterial({ color: 0x24211d, roughness: 0.35, metalness: 0.15, transparent: true, opacity: 0.9 });
  const water = new THREE.Mesh(new THREE.PlaneGeometry(LEN, TW, 200, 4), waterMat); water.rotation.x = -Math.PI / 2; water.position.set(cx, DEPTH - 1, 0); scene.add(water);
  // dust and drips
  const N = 500, dpos = new Float32Array(N * 3), seeds = [];
  for (let i = 0; i < N; i++) seeds.push([r(), r(), r(), r()]);
  const dgeo = new THREE.BufferGeometry(); dgeo.setAttribute('position', new THREE.BufferAttribute(dpos, 3));
  const dotTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 32; const g = c.getContext('2d');
    const grd = g.createRadialGradient(16, 16, 0, 16, 16, 16); grd.addColorStop(0, 'rgba(255,255,255,1)'); grd.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grd; g.fillRect(0, 0, 32, 32); return new THREE.CanvasTexture(c); })();
  const dust = new THREE.Points(dgeo, new THREE.PointsMaterial({ color: 0xcfb48a, size: inside ? 0.007 : 0.03, map: dotTex, transparent: true, opacity: 0.5, depthWrite: false, blending: THREE.AdditiveBlending })); scene.add(dust);

  // ---- light
  scene.add(new THREE.HemisphereLight(0x5c6676, 0x080706, inside ? 0.05 : 0.6));
  const moon = new THREE.DirectionalLight(0x9fb0c8, inside ? 0 : 0.45); moon.position.set(-20, 40, 30); scene.add(moon);
  const fill = new THREE.DirectionalLight(0xb3aea4, inside ? 0 : 4.2); fill.position.set(10, 0, 60); fill.target.position.set(0, -6, 0); scene.add(fill, fill.target);
  // a handful of real point lights travel with the action; the rest of the bulbs are glow only
  for (let i = 0; i < 6; i++) { const l = new THREE.PointLight(AMBER, 0, inside ? 6 : 5, 1.6); if (i < 2) { l.castShadow = true; l.shadow.mapSize.set(1024, 1024); l.shadow.bias = -0.002; } scene.add(l); lights.push(l); }
  const handLamp = new THREE.PointLight(0xffc27a, 0, 4, 1.4); handLamp.castShadow = true; handLamp.shadow.mapSize.set(1024, 1024); scene.add(handLamp);

  const post = makeComposer(THREE, renderer, scene, camera, W, H, {
    bloom: inside ? 0.9 : 0.8, bloomRadius: 0.75, bloomThreshold: shot === 'water' ? 0.8 : inside ? 0.55 : 0.6, exposure: inside ? 1.15 : 1.05,
    dof: shot === 'dig' ? { focus: 1.3, aperture: 0.006, maxblur: 0.01 } : shot === 'camera' ? { focus: 1.6, aperture: 0.004, maxblur: 0.01 } : null,
  });
  return { THREE, scene, camera, shot, inside, bulbs, lights, handLamp, crawlers, digger, spade, cam, water, dust, dpos, seeds,
           search, searchBeam, holeGlow, holeLight, holeBeam, tunnel, ...post };
}

export function update(ctx, t) {
  const { THREE, camera, shot, bulbs, lights, handLamp, crawlers, digger, spade, cam, water, dust, dpos, seeds, search, searchBeam } = ctx;
  // bulbs breathe a little on the generator; keep the real point lights on the bulbs nearest to the camera's target
  let focusX = camera.position.x;
  for (const b of bulbs) { const k = 0.9 + 0.1 * Math.sin(t * 7 + b.seed) * Math.sin(t * 2.3 + b.seed); b.halo.material.opacity = k; b.k = k; }
  // searchlight sweeps the death strip
  const sw = Math.sin(t * 0.45) * 14 - 8;
  search.target.position.set(-1, 0, sw); search.target.updateMatrixWorld();
  searchBeam.position.copy(search.position);
  searchBeam.lookAt(search.target.position); searchBeam.rotateX(-Math.PI / 2);

  digger.visible = spade.visible = cam.visible = false;
  for (const c of crawlers) c.p.visible = false;
  water.position.y = DEPTH - 1;
  handLamp.intensity = 0;

  if (shot === 'street') {
    const k = smooth(t / 10);
    camera.position.set(lerp(30, 22, k), lerp(2.2, 2.6, k), lerp(18, 13, k));
    camera.lookAt(lerp(0, 2, k), 2.6, -8);
  } else if (shot === 'reveal' || shot === 'thumb' || shot === 'section') {
    if (shot === 'reveal') {
      const k = smooth(t / 9);
      camera.position.set(lerp(14, 2, k), lerp(5, -4.5, k), lerp(26, 52, k));
      camera.lookAt(lerp(4, 1, k), lerp(2.5, -4.6, k), 0);
    } else if (shot === 'thumb') {
      camera.position.set(-10, 3.5, 46); camera.lookAt(1, -3.6, 0);
    } else {
      const k = t / 14;
      camera.position.set(lerp(-14, 10, k), -1.5, 40); camera.lookAt(lerp(-12, 12, k), -3.6, 0);
    }
    // escapees crawl from the East cellar toward the West shaft
    for (const c of crawlers) {
      const x = XE + 1 + ((t * 0.9 + c.off) % (XW - XE - 2));
      c.p.visible = shot !== 'reveal' || t > 4;
      c.p.position.set(x, DEPTH + 0.2, 0.05);
      c.p.rotation.x = Math.sin(t * 5 + c.off) * 0.08;
    }
    ctx.holeGlow.material.opacity = 0.7; ctx.holeLight.intensity = 6; ctx.holeBeam.material.uniforms.opacity.value = 0.05;
    focusX = camera.position.x;
  } else if (shot === 'crawl') {
    const x = XE + 3 + t * 0.55;
    camera.position.set(x, DEPTH + 0.42 + Math.abs(Math.sin(t * 2.6)) * 0.05, 0.05 * Math.sin(t * 1.3));
    camera.lookAt(x + 3, DEPTH + 0.5 + Math.sin(t * 1.1) * 0.04, 0);
    camera.rotation.z += Math.sin(t * 2.6) * 0.015;
    // the person ahead of you
    const c = crawlers[0]; c.p.visible = true; c.p.position.set(x + 3.4 + Math.sin(t * 1.3) * 0.05, DEPTH + 0.2, 0); c.p.rotation.x = Math.sin(t * 5) * 0.1;
    focusX = x + 2;
  } else if (shot === 'dig') {
    const fx = XE + 4;   // working face
    // from behind the digger's boots, looking past him at the lit clay face
    // first person at the clay face: the spade bites in from below frame, a lamp swings beside you
    const s = Math.pow(Math.max(0, Math.sin(t * 2.2)), 3);
    camera.position.set(fx + 1.05, DEPTH + 0.48 + s * 0.015, 0.05); camera.lookAt(fx - 0.2, DEPTH + 0.5, 0);
    spade.visible = true;
    spade.position.set(fx + 0.38 - s * 0.16, DEPTH + 0.36 + s * 0.04, 0.12); spade.rotation.set(0.15, 0, 1.35 + s * 0.1);
    handLamp.position.set(fx + 0.7, DEPTH + 0.85 + Math.sin(t * 1.3) * 0.03, -0.28); handLamp.intensity = 3.2 * flicker(t, 0, 3);
    focusX = fx;
  } else if (shot === 'water') {
    const x = XE + 13.2;   // between two bulbs so none flares the lens
    camera.position.set(x, DEPTH + 0.45 + smooth(t / 8) * 0.12, 0.12); camera.lookAt(x + 3, DEPTH + 0.3, 0);
    water.position.y = DEPTH + 0.05 + smooth(t / 8) * 0.38;
    const g = water.geometry.attributes.position; for (let i = 0; i < g.count; i++) g.setZ(i, Math.sin(g.getX(i) * 6 + t * 3) * 0.006); g.needsUpdate = true;
    focusX = x;
  } else if (shot === 'camera') {
    const x = XE + 2 + 3.2 * 12 + 1.6;   // halfway between bulbs: the one behind the camera backlights it
    cam.visible = true; cam.position.set(x, DEPTH + 0.03, 0.05); cam.rotation.y = 0;
    camera.position.set(x + 1.9 - t * 0.06, DEPTH + 0.62, 0.3); camera.lookAt(x - 0.6, DEPTH + 0.62, -0.05);
    const c = crawlers[1]; c.p.visible = t > 2; c.p.position.set(x - 4 + (t - 2) * 0.8, DEPTH + 0.2, 0);
    focusX = x - 1;
  } else if (shot === 'cellar') {
    const k = smooth(t / 8);
    camera.position.set(XE - 2.7, lerp(-0.5, -0.9, k), lerp(0.5, 0.4, k)); camera.lookAt(XE + 0.2, -3.45, -0.25);
    ctx.holeGlow.material.opacity = 0.2 + 0.8 * smooth((t - 1) / 2);
    ctx.holeLight.intensity = 10 * smooth((t - 1) / 2);
    ctx.holeBeam.material.uniforms.opacity.value = 0.12 * smooth((t - 1) / 2);
    focusX = XE;
  }
  // assign the real lights to the bulbs closest to where we look
  const near = [...bulbs].sort((a, b) => Math.abs(a.x - focusX) - Math.abs(b.x - focusX));
  lights.forEach((l, i) => { const b = near[i]; if (!b) { l.intensity = 0; return; } l.position.copy(b.b.position); l.intensity = (ctx.inside ? 3.2 : 2.2) * b.k; });
  // dust motes / drips around the focus
  for (let i = 0; i < seeds.length; i++) {
    const [a, b, c, d] = seeds[i];
    const drip = i % 7 === 0 && ctx.inside;
    const y = drip ? DEPTH + TH - ((t * 1.8 + d * 3) % 1.2) : DEPTH + 0.1 + b * (TH - 0.2) + Math.sin(t * 0.4 + d * 9) * 0.04;
    dpos[i * 3] = focusX - 4 + a * 8 + Math.sin(t * 0.3 + c * 6) * 0.05; dpos[i * 3 + 1] = y; dpos[i * 3 + 2] = (c - 0.5) * TW * 0.9;
  }
  dust.geometry.attributes.position.needsUpdate = true;
  dust.visible = ctx.inside || shot === 'section';
}

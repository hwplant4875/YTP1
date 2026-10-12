// France 2026: the state. Stylised, generic massing of two Paris landmarks at night (no logos, no people) and an
// illustrative intelligence note on a desk.
// shots (?shot=name or name:seconds):
//   assemblee (7 s)  the Palais Bourbon portico (12 columns, pediment, wide steps) lit from below at night across an
//                    empty quay; slow crane up; the portico lights warm to amber at 2-4 s (budget day, beat 47).
//   matignon  (7 s)  the prime minister's residence: a classical courtyard façade with a mansard roof and a flag;
//                    slow push from the gate; a single first-floor window warms to amber (beats 102-103).
//   dossier   (8 s)  a note on a desk under a lamp: grey text lines, black redaction bars; an amber highlighter
//                    marks "outsiders" six times, then "LFI" once (beats 106-107). Tagged ILLUSTRATION.
import { AMBER } from './lib.js';
import { glow, beam } from './look.js';
import { AMBER_HI, path, clamp01, sstep, fontsReady, finishPost, ctex, spacedText, timing, label, ease } from './france_lib.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export async function setup(THREE, renderer, W, H) {
  const { name, k: k0 } = timing(7);
  const shot = name || 'assemblee';
  const k = shot === 'dossier' ? k0 * 7 / 8 : k0;
  await fontsReady();
  const scene = new THREE.Scene();
  const night = shot !== 'dossier';
  scene.background = new THREE.Color(night ? 0x0a0c12 : 0x070707);
  scene.fog = new THREE.FogExp2(night ? 0x0d1016 : 0x070707, night ? 0.012 : 0.1);
  const camera = new THREE.PerspectiveCamera(shot === 'dossier' ? 30 : 32, W / H, 0.02, 600);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.8, metalness: 0, ...o });
  let seed = 9; const R = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  const add = (geo, mat, x, y, z, rx = 0, ry = 0, rz = 0, parent = scene) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.rotation.set(rx, ry, rz); m.castShadow = m.receiveShadow = true; parent.add(m); return m; };
  const ctx = { THREE, scene, camera, shot, k };
  const stone = std({ map: ctex(THREE, 512, 512, (g, w, h) => { g.fillStyle = '#c9bea6'; g.fillRect(0, 0, w, h); for (let i = 0; i < 14000; i++) { const v = 170 + R() * 60; g.fillStyle = `rgba(${v},${v - 8},${v - 26},0.15)`; g.fillRect(R() * w, R() * h, 2, 2); }
    g.strokeStyle = 'rgba(90,80,64,0.35)'; g.lineWidth = 2; for (let y = 0; y < h; y += 64) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); } }, { repeat: [6, 3] }), roughness: 0.9 });
  const pediment = (w, h, d, mat) => { const s = new THREE.Shape(); s.moveTo(-w / 2, 0); s.lineTo(w / 2, 0); s.lineTo(0, h); s.closePath(); const g = new THREE.ExtrudeGeometry(s, { depth: d, bevelEnabled: false }); g.translate(0, 0, -d / 2); return new THREE.Mesh(g, mat); };
  const winM = (lit) => std({ color: lit ? 0x3a2c1c : 0x14161a, roughness: 0.2, metalness: 0.5, emissive: new THREE.Color(lit ? 0xffb36a : 0x000000), emissiveIntensity: lit ? 0.35 : 0 });

  if (shot === 'assemblee') {
    const ground = add(new THREE.PlaneGeometry(300, 200), std({ color: 0x2a2a2c, roughness: 0.4, metalness: 0.3 }), 0, 0, 0, -Math.PI / 2); ground.castShadow = false;
    // steps
    for (let i = 0; i < 10; i++) add(new THREE.BoxGeometry(46 - i * 0.3, 0.3, 14 - i * 0.6), stone, 0, 0.15 + i * 0.3, -i * 0.3);
    const base = 3.0;
    // portico: 12 columns
    const colM = stone; const colGeo = new THREE.CylinderGeometry(0.75, 0.85, 17, 24);
    for (let i = 0; i < 12; i++) { const x = -19.25 + i * 3.5; add(colGeo, colM, x, base + 8.5 + 0.4, 2.5); add(new THREE.BoxGeometry(2.0, 0.4, 2.0), stone, x, base + 0.2, 2.5); add(new THREE.BoxGeometry(2.0, 0.6, 2.0), stone, x, base + 17.7, 2.5); }
    add(new THREE.BoxGeometry(44, 2.6, 4.4), stone, 0, base + 19.3, 2.4);          // entablature
    add(new THREE.BoxGeometry(45, 0.5, 4.8), stone, 0, base + 20.85, 2.4);
    const ped = pediment(44, 6.5, 4.0, stone); ped.position.set(0, base + 21.1, 2.4); ped.castShadow = true; scene.add(ped);
    add(new THREE.BoxGeometry(48, 26, 10), stone, 0, base + 13, -5);               // main block behind
    // wings
    for (const s of [-1, 1]) { add(new THREE.BoxGeometry(30, 20, 14), stone, s * 39, base + 10 - 3, -6); for (let r = 0; r < 2; r++) for (let i = 0; i < 6; i++) add(new THREE.PlaneGeometry(1.8, 3.6), winM(R() < 0.3), s * 39 + (i - 2.5) * 4.6, base + 5 + r * 8, 1.01); }
    // tall doors/windows behind the columns, lit warm
    ctx.porticoWins = []; for (let i = 0; i < 11; i++) { const m = add(new THREE.PlaneGeometry(1.8, 6.0), winM(true), -17.5 + i * 3.5, base + 4.0, 0.01); ctx.porticoWins.push(m); }
    // tricolour on a pole at the top (red stays warm under the grade)
    const flag = new THREE.Group(); flag.position.set(0, base + 27.6, 2.4); scene.add(flag);
    add(new THREE.CylinderGeometry(0.08, 0.08, 6, 8), std({ color: 0x8a8a8a, metalness: 0.6 }), 0, 3, 0, 0, 0, 0, flag);
    const fg = new THREE.PlaneGeometry(3.6, 2.4, 20, 4); const fp = fg.attributes.position; for (let i = 0; i < fp.count; i++) { const x = fp.getX(i) + 1.8; fp.setZ(i, Math.sin(x * 1.6) * 0.18 * x / 3.6); }
    fg.computeVertexNormals(); const ft = ctex(THREE, 300, 200, (g) => { g.fillStyle = '#28356e'; g.fillRect(0, 0, 100, 200); g.fillStyle = '#efefef'; g.fillRect(100, 0, 100, 200); g.fillStyle = '#c8242e'; g.fillRect(200, 0, 100, 200); });
    add(fg, std({ map: ft, side: THREE.DoubleSide, roughness: 0.8 }), 1.8, 4.6, 0, 0, 0, 0, flag);
    // uplights from the steps
    ctx.up = []; for (let i = 0; i < 6; i++) { const s = new THREE.SpotLight(0xffd6a0, 0, 40, 0.5, 0.7, 1.2); s.position.set(-17.5 + i * 7, 1, 12); s.target.position.set(-17.5 + i * 7, 18, 2); scene.add(s, s.target); ctx.up.push(s); }
    scene.add(new THREE.HemisphereLight(0x5d6a86, 0x0c0b0a, 0.45));
    const moon = new THREE.DirectionalLight(0x8c9cbc, 0.5); moon.position.set(-40, 60, 60); scene.add(moon);
    // quay lamps
    for (let i = 0; i < 7; i++) { const x = -42 + i * 14; add(new THREE.CylinderGeometry(0.12, 0.16, 5, 10), std({ color: 0x1c1c1c, metalness: 0.5 }), x, 2.5, 26); const b = glow(THREE, 0xffc070, 2.2, 1); b.position.set(x, 5.3, 26); scene.add(b);
      const l = new THREE.PointLight(0xffa850, 20, 18, 1.6); l.position.set(x, 5.2, 26); scene.add(l); }
  } else if (shot === 'matignon') {
    const ground = add(new THREE.PlaneGeometry(200, 200), std({ map: ctex(THREE, 512, 512, (g, w, h) => { g.fillStyle = '#5a554c'; g.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 32) for (let x = 0; x < w; x += 32) { const v = 70 + R() * 30; g.fillStyle = `rgb(${v},${v - 4},${v - 12})`; g.fillRect(x + 2, y + 2, 28, 28); } }, { repeat: [40, 40] }), roughness: 0.6, metalness: 0.15 }), 0, 0, 0, -Math.PI / 2);
    ground.castShadow = false;
    const Wd = 44, Hb = 14;
    add(new THREE.BoxGeometry(Wd, Hb, 12), stone, 0, Hb / 2, -6);
    add(new THREE.BoxGeometry(14, Hb + 1.5, 2), stone, 0, (Hb + 1.5) / 2, 0.8);              // central avant-corps
    const ped = pediment(14.6, 2.6, 2.4, stone); ped.position.set(0, Hb + 1.5, 0.8); scene.add(ped);
    add(new THREE.BoxGeometry(Wd + 0.8, 0.6, 12.8), stone, 0, Hb + 0.3, -6);
    // mansard roof with dormers
    const roofM = std({ color: 0x2c3036, roughness: 0.5, metalness: 0.4 });
    const roof = new THREE.Mesh(new THREE.CylinderGeometry(4.5, 6.4, 4.5, 4, 1), roofM); roof.rotation.y = Math.PI / 4; roof.scale.set(Wd / 9.05, 1, 12 / 9.05); roof.position.set(0, Hb + 2.85, -6); roof.castShadow = true; scene.add(roof);
    for (let i = 0; i < 9; i++) { const x = -18 + i * 4.5; if (Math.abs(x) < 1) continue; add(new THREE.BoxGeometry(1.4, 1.8, 1.0), stone, x, Hb + 2.2, -0.4); add(new THREE.PlaneGeometry(0.8, 1.2), winM(R() < 0.2), x, Hb + 2.1, 0.11); }
    // windows: ground floor arched (rects here), first floor tall with balconette
    ctx.office = null;
    for (let f = 0; f < 2; f++) for (let i = 0; i < 11; i++) { const x = -20 + i * 4; const zf = Math.abs(x) <= 6 ? 1.81 : 0.01;
      const lit = (f === 1 && i === 5) ? 'office' : R() < 0.35;
      const m = add(new THREE.PlaneGeometry(1.7, f ? 4.2 : 4.6), winM(lit === 'office' ? false : lit), x, f ? 9.4 : 3.4, zf); if (lit === 'office') ctx.office = m;
      add(new THREE.BoxGeometry(2.1, 0.25, 0.3), stone, x, (f ? 9.4 : 3.4) + (f ? 2.3 : 2.5), zf + 0.1);
      if (f) add(new THREE.BoxGeometry(2.0, 0.08, 0.5), std({ color: 0x1a1a1a, metalness: 0.6 }), x, 7.4, zf + 0.25); }
    ctx.office.material = std({ color: 0x2a2018, roughness: 0.2, metalness: 0.4, emissive: new THREE.Color(AMBER_HI), emissiveIntensity: 0.15 });
    const officeGlow = glow(THREE, AMBER, 6, 0.7); officeGlow.position.set(0, 9.4, 2.4); officeGlow.material.opacity = 0; scene.add(officeGlow); ctx.officeGlow = officeGlow;
    // flag over the door
    const fg = new THREE.PlaneGeometry(2.4, 1.6, 16, 3); const fp = fg.attributes.position; for (let i = 0; i < fp.count; i++) { const x = fp.getX(i) + 1.2; fp.setZ(i, Math.sin(x * 2) * 0.12 * x / 2.4); } fg.computeVertexNormals();
    const ft = ctex(THREE, 300, 200, (g) => { g.fillStyle = '#28356e'; g.fillRect(0, 0, 100, 200); g.fillStyle = '#efefef'; g.fillRect(100, 0, 100, 200); g.fillStyle = '#c8242e'; g.fillRect(200, 0, 100, 200); });
    const pole = add(new THREE.CylinderGeometry(0.05, 0.05, 3.2, 8), std({ color: 0x9a9a9a, metalness: 0.6 }), 0, 13.2, 2.6, 0.6, 0, 0);
    add(fg, std({ map: ft, side: THREE.DoubleSide }), 1.15, 13.6, 3.6, 0.15, 0, -0.1);
    // courtyard: gate posts and lanterns, gravel, two guard boxes (empty)
    for (const s of [-1, 1]) { add(new THREE.BoxGeometry(1.2, 4, 1.2), stone, s * 6, 2, 30); const b = glow(THREE, 0xffc070, 1.8, 1); b.position.set(s * 6, 4.6, 30); scene.add(b); const l = new THREE.PointLight(0xffa850, 16, 14, 1.6); l.position.set(s * 6, 4.6, 30.8); scene.add(l);
      add(new THREE.BoxGeometry(1.4, 2.6, 1.4), std({ color: 0x2a2c30 }), s * 9, 1.3, 27); }
    ctx.up = []; for (let i = 0; i < 5; i++) { const s = new THREE.SpotLight(0xffd6a0, 0, 30, 0.6, 0.7, 1.2); s.position.set(-16 + i * 8, 0.5, 9); s.target.position.set(-16 + i * 8, 10, 0); scene.add(s, s.target); ctx.up.push(s); }
    scene.add(new THREE.HemisphereLight(0x5d6a86, 0x0c0b0a, 0.45));
    const moon = new THREE.DirectionalLight(0x8c9cbc, 0.45); moon.position.set(-40, 60, 60); scene.add(moon);
  } else {
    // desk, lamp, the note
    const desk = add(new THREE.PlaneGeometry(10, 10), std({ map: ctex(THREE, 1024, 1024, (g, w, h) => { g.fillStyle = '#2a1e16'; g.fillRect(0, 0, w, h); for (let i = 0; i < 300; i++) { g.strokeStyle = `rgba(${60 + R() * 30},${40 + R() * 20},${26},0.45)`; g.lineWidth = 1 + R() * 3; g.beginPath(); const y = R() * h; g.moveTo(0, y); g.bezierCurveTo(w * 0.3, y + 8, w * 0.6, y - 8, w, y + 3); g.stroke(); } }), roughness: 0.45 }), 0, 0, 0, -Math.PI / 2);
    const words = [];
    const PW = 1100, PH = 1556;
    const lines = [];
    { let y = 330; for (let i = 0; i < 26; i++) { const segs = []; let x = 110; while (x < PW - 160) { const wd = 40 + R() * 110; segs.push([x, wd]); x += wd + 18; } lines.push({ y, segs }); y += 44; if (i % 7 === 6) y += 26; } }
    const out = [[2, 3], [5, 1], [9, 4], [13, 2], [17, 5], [21, 2]]; const lfi = [24, 3];
    const red = [[4, 2, 4], [8, 0, 3], [11, 3, 5], [15, 1, 2], [19, 3, 6], [23, 0, 2]];
    const draw = (g, w, h) => { g.fillStyle = '#ece6d8'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 4000; i++) { g.fillStyle = `rgba(120,110,90,${R() * 0.05})`; g.fillRect(R() * w, R() * h, 2, 2); }
      g.fillStyle = '#1c1c1c'; g.font = '700 46px "DejaVu Serif", serif'; g.fillText('NOTE', 110, 150); g.font = '400 26px "DejaVu Serif", serif'; g.fillStyle = '#3a3a3a'; g.fillText('Objet : mobilisation lycéenne — secteur nord-est', 110, 200);
      g.fillStyle = '#7a1e1e'; g.font = '700 22px Inter, sans-serif'; g.strokeStyle = '#7a1e1e'; g.lineWidth = 3; g.strokeRect(PW - 330, 110, 220, 46); g.fillText('ILLUSTRATION', PW - 310, 142);
      lines.forEach((L, li) => L.segs.forEach(([x, wd], si) => {
        const o = out.findIndex(([a, b]) => a === li && b === si);
        if (o >= 0) { g.fillStyle = '#1c1c1c'; g.font = '400 30px "DejaVu Serif", serif'; g.fillText('outsiders', x, L.y + 8); words.push({ x, y: L.y, w: g.measureText('outsiders').width, k: o }); return; }
        if (lfi[0] === li && lfi[1] === si) { g.fillStyle = '#1c1c1c'; g.font = '400 30px "DejaVu Serif", serif'; g.fillText('LFI', x, L.y + 8); words.push({ x, y: L.y, w: g.measureText('LFI').width, k: 6 }); return; }
        if (red.some(([a, b, n]) => a === li && si >= b && si < b + n)) { g.fillStyle = '#0b0b0b'; g.fillRect(x - 6, L.y - 18, wd + 24, 32); return; }
        g.fillStyle = 'rgba(40,40,40,0.55)'; g.fillRect(x, L.y - 8, wd, 12); })); };
    const pageT = ctex(THREE, PW, PH, draw);
    const pw = 2.1, ph = pw * PH / PW;
    const page = add(new THREE.PlaneGeometry(pw, ph), std({ map: pageT, roughness: 0.9 }), 0, 0.012, 0, -Math.PI / 2, 0, 0.08);
    const under = add(new THREE.PlaneGeometry(pw, ph), std({ color: 0xd8d1c2 }), 0.05, 0.006, -0.04, -Math.PI / 2, 0, 0.12);
    const folder = add(new RoundedBoxGeometry(pw + 0.3, 0.02, ph + 0.25, 2, 0.01), std({ color: 0x6a5a40, roughness: 0.8 }), 0.1, -0.005, 0, 0, -0.06, 0);
    // highlighter strokes: amber, additive quads placed over each word (page local -> world via the page's matrix)
    page.updateMatrixWorld(true);
    const hm = new THREE.MeshBasicMaterial({ color: 0xff9a2a, transparent: true, opacity: 0.6, depthWrite: false });
    ctx.marks = words.map((wd) => { const u = (wd.x - 8) / PW, v = (wd.y - 22) / PH, uw = (wd.w + 16) / PW, vh = 34 / PH;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), hm.clone()); m.geometry.translate(0.5, -0.5, 0);
      m.position.set((u - 0.5) * pw, (0.5 - v) * ph, 0.003); m.userData = { w: uw * pw, h: vh * ph, k: wd.k }; m.scale.set(0.0001, vh * ph, 1); page.add(m); return m; });
    // pen
    const pen = new THREE.Group(); add(new THREE.CylinderGeometry(0.03, 0.03, 0.9, 16), std({ color: 0xffb25c, roughness: 0.4 }), 0, 0, 0, 0, 0, Math.PI / 2, pen); add(new THREE.CylinderGeometry(0.031, 0.031, 0.25, 16), std({ color: 0x1a1a1a }), -0.5, 0, 0, 0, 0, Math.PI / 2, pen);
    pen.position.set(1.5, 0.04, 0.6); pen.rotation.y = 0.6; scene.add(pen);
    // lamp light
    scene.add(new THREE.HemisphereLight(0x8e94a0, 0x0a0806, 0.25));
    const lamp = new THREE.SpotLight(0xffe2b8, 5, 8, 0.55, 0.8, 1.5); lamp.position.set(-1.3, 2.6, -1.0); lamp.target.position.set(0, 0, 0); lamp.castShadow = true; lamp.shadow.mapSize.set(2048, 2048); scene.add(lamp, lamp.target);
    const shade = add(new THREE.ConeGeometry(0.35, 0.35, 24, 1, true), std({ color: 0x1d1d1f, side: THREE.DoubleSide, metalness: 0.5 }), -1.3, 2.75, -1.0); const bulb = glow(THREE, 0xffd29a, 0.6, 1); bulb.position.set(-1.3, 2.6, -1.0); scene.add(bulb);
  }
  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.65, bloomRadius: 0.6, bloomThreshold: 0.7,
    dof: shot === 'dossier' ? { focus: 3.3, aperture: 0.002, maxblur: 0.007 } : null });
  return Object.assign(ctx, post);
}

const CAMS = {
  assemblee: [[0, [-22, 3.2, 84, 0, 13, 0]], [7, [-13, 9, 74, 0, 14.5, 0]]],
  matignon: [[0, [3, 3.0, 46, 0, 8.5, 0]], [7, [1.5, 4.5, 30, 0, 9.0, 0]]],
  dossier: [[0, [0.35, 3.6, 1.7, -0.05, 0, -0.25]], [8, [0.12, 3.0, 1.45, 0.02, 0, -0.1]]],
};

export function update(ctx, tt) {
  const { camera, shot } = ctx;
  const t = tt / ctx.k;
  const c = path(CAMS[shot] ?? CAMS.assemblee)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  if (shot === 'assemblee') {
    const w = sstep(2.0, 4.0, t);
    ctx.up.forEach(s => { s.intensity = 70 * (0.6 + 0.4 * w); s.color.setHex(0xffd6a0).lerp(new THREE_COLOR(0xffa64a), w); });
    ctx.porticoWins.forEach(m => m.material.emissiveIntensity = 0.2 + 0.35 * w);
  } else if (shot === 'matignon') {
    ctx.up.forEach(s => s.intensity = 45);
    const w = sstep(2.2, 4.2, t); ctx.office.material.emissiveIntensity = 0.15 + 1.6 * w; ctx.officeGlow.material.opacity = 0.6 * w;
  } else if (shot === 'dossier') {
    ctx.marks.forEach((m) => { const kk = m.userData.k; const a = kk < 6 ? 1.2 + kk * 0.6 : 5.6; const p = ease((t - a) / 0.45); m.scale.x = Math.max(0.0001, p * m.userData.w); });
  }
}
// tiny colour helper so update() does not need THREE in scope
function THREE_COLOR(hex) { return { r: ((hex >> 16) & 255) / 255, g: ((hex >> 8) & 255) / 255, b: (hex & 255) / 255, isColor: true }; }

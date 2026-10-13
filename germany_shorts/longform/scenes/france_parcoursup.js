// France 2026: the university-admissions platform, as a generic UI (no real logo or name on screen).
// shots (?shot=name or name:seconds):
//   dashboard (7 s)  a laptop on a desk in a dark bedroom at night; the screen lists ten applications, all "WAITING";
//                    slow push into the screen while an amber cursor bar walks down the list.
//   cascade   (8 s)  100 application cards hang in a curved wall; they flip one after another to their result;
//                    18 of them land on "NO OFFER" (dark, amber edge), the rest on a pale "OFFER". Camera drifts left.
const AMBER = 0x2dd4bf;   // v2: subject colour instead of the channel amber
import { glow } from './look.js';
import { path, clamp01, sstep, fontsReady, finishPost, ctex, spacedText, timing, label, ease } from './france_lib.js';
const AMBER_HI = 0x5eead4;
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const rr = (g, x, y, w, h, r) => { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); };
const PROG = ['LAW · Paris', 'MEDICINE · Créteil', 'BTS · Commerce', 'IUT · Computing', 'HISTORY · Nanterre', 'NURSING · Paris', 'ECONOMICS · Lyon', 'BIOLOGY · Orsay', 'PREP CLASS · Paris', 'DESIGN · Lille'];

function drawDash(g, w, h, cur) {
  g.fillStyle = '#121315'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#1b1c1f'; g.fillRect(0, 0, w, 90); g.fillStyle = '#e3e8ef'; g.font = '700 34px Inter, sans-serif'; g.fillText('ADMISSIONS PLATFORM', 40, 58);
  g.fillStyle = 'rgba(233,223,202,0.45)'; g.font = '500 24px Inter, sans-serif'; g.fillText('My applications · main round', 40, 140);
  g.fillStyle = '#2dd4bf'; g.font = '700 24px Inter, sans-serif'; g.textAlign = 'right'; g.fillText('10 / 10', w - 40, 140); g.textAlign = 'left';
  for (let i = 0; i < 10; i++) {
    const y = 175 + i * 82;
    g.fillStyle = i === cur ? '#2a2620' : '#18191b'; rr(g, 36, y, w - 72, 70, 10); g.fill();
    if (i === cur) { g.fillStyle = '#2dd4bf'; g.fillRect(36, y, 8, 70); }
    g.fillStyle = 'rgba(233,223,202,0.5)'; g.font = '600 20px Inter, sans-serif'; g.fillText(`CHOICE ${i + 1}`, 64, y + 28);
    g.fillStyle = '#e3e8ef'; g.font = '600 28px Inter, sans-serif'; g.fillText(PROG[i], 64, y + 58);
    g.strokeStyle = 'rgba(233,223,202,0.35)'; g.lineWidth = 2; rr(g, w - 250, y + 18, 190, 36, 18); g.stroke();
    g.fillStyle = 'rgba(233,223,202,0.6)'; g.font = '700 18px Inter, sans-serif'; g.textAlign = 'center'; g.fillText('WAITING', w - 155, y + 43); g.textAlign = 'left';
  }
}

export async function setup(THREE, renderer, W, H) {
  const { name, k: k0 } = timing(7);
  const shot = name || 'cascade';
  const k = shot === 'cascade' ? k0 * 7 / 8 : k0;
  await fontsReady();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060607);
  scene.fog = new THREE.FogExp2(0x060607, shot === 'cascade' ? 0.045 : 0.09);
  const camera = new THREE.PerspectiveCamera(32, W / H, 0.02, 200);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.6, metalness: 0.1, ...o });
  const ctx = { THREE, scene, camera, shot, k };
  scene.add(new THREE.HemisphereLight(0x8e94a0, 0x080706, 0.3));

  if (shot === 'dashboard') {
    const c = document.createElement('canvas'); c.width = 1024; c.height = 1024 * 0.64 | 0; const g = c.getContext('2d');
    const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; ctx.scr = { g, tex, w: c.width, h: c.height };
    drawDash(g, c.width, c.height, -1);
    const lap = new THREE.Group(); scene.add(lap);
    const alu = std({ color: 0x3b3c3f, metalness: 0.8, roughness: 0.3 });
    const base = new THREE.Mesh(new RoundedBoxGeometry(1.5, 0.03, 1.0, 3, 0.012), alu); base.position.y = 0.015; base.castShadow = true; lap.add(base);
    const kb = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 0.45), std({ color: 0x141416 })); kb.rotation.x = -Math.PI / 2; kb.position.set(0, 0.031, -0.1); lap.add(kb);
    const lid = new THREE.Group(); lid.position.set(0, 0.03, -0.5); lid.rotation.x = -0.28; lap.add(lid);
    const lb = new THREE.Mesh(new RoundedBoxGeometry(1.5, 0.96, 0.02, 3, 0.01), alu); lb.position.y = 0.48; lid.add(lb);
    const scr = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 0.875), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false })); scr.position.set(0, 0.49, 0.011); lid.add(scr);
    lap.position.set(0, 0.75, 0);
    const desk = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.05, 1.6), std({ color: 0x3a2e24, roughness: 0.55 })); desk.position.set(0, 0.725, 0.1); desk.receiveShadow = true; scene.add(desk);
    // clutter: books, mug, lamp off, posters in the dark
    const book = (x, z, r, c, h) => { const b = new THREE.Mesh(new THREE.BoxGeometry(0.42, h, 0.3), std({ color: c })); b.position.set(x, 0.75 + h / 2, z); b.rotation.y = r; b.castShadow = true; scene.add(b); };
    book(-1.15, 0.2, 0.3, 0x5a4a3a, 0.05); book(-1.12, 0.2, 0.15, 0x3a4a5a, 0.04); book(-1.13, 0.21, 0.4, 0x6a3a3a, 0.035);
    const mug = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.045, 0.11, 24), std({ color: 0xb8b0a2 })); mug.position.set(0.95, 0.805, 0.25); scene.add(mug);
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(10, 5), std({ color: 0x2a2826, roughness: 0.95 })); wall.position.set(0, 2.2, -1.2); wall.receiveShadow = true; scene.add(wall);
    const post = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.85), std({ color: 0x4a443c })); post.position.set(-1.3, 1.9, -1.19); scene.add(post);
    const screenLight = new THREE.SpotLight(0xd9e2ff, 6, 4, 1.0, 0.9, 1.6); screenLight.position.set(0, 1.25, -0.4); screenLight.target.position.set(0, 0.75, 0.8); scene.add(screenLight, screenLight.target);
    const window = new THREE.SpotLight(0x8fa0bc, 10, 10, 0.5, 0.8, 1.4); window.position.set(3, 3, 1); window.target.position.set(0, 0.8, 0); scene.add(window, window.target);
    const lampA = new THREE.PointLight(AMBER, 3, 3, 1.8); lampA.position.set(-1.4, 1.4, 0.5); scene.add(lampA);
  } else {
    const N = 100, cols = 20, rows = 5;
    const noSet = new Set(); { let s = 5; const R = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); while (noSet.size < 18) noSet.add(Math.floor(R() * N)); }
    const front = ctex(THREE, 256, 340, (g, w, h) => { g.fillStyle = '#1c1d20'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(233,223,202,0.5)'; g.fillRect(24, 30, 120, 12); g.fillRect(24, 54, 80, 10);
      g.strokeStyle = 'rgba(233,223,202,0.4)'; g.lineWidth = 3; rr(g, 24, h - 80, w - 48, 46, 23); g.stroke(); g.fillStyle = 'rgba(233,223,202,0.7)'; g.font = '700 24px Inter, sans-serif'; g.textAlign = 'center'; g.fillText('WAITING', w / 2, h - 49); });
    const offer = ctex(THREE, 256, 340, (g, w, h) => { g.fillStyle = '#cfc6b6'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(30,30,30,0.45)'; g.fillRect(24, 30, 120, 12); g.fillRect(24, 54, 80, 10);
      g.fillStyle = '#2a2a2a'; g.font = '800 40px Inter, sans-serif'; g.textAlign = 'center'; g.fillText('OFFER', w / 2, h - 44); });
    const none = ctex(THREE, 256, 340, (g, w, h) => { g.fillStyle = '#0d0d0e'; g.fillRect(0, 0, w, h); g.strokeStyle = '#f87171'; g.lineWidth = 8; g.strokeRect(6, 6, w - 12, h - 12);
      g.fillStyle = '#f87171'; g.font = '800 40px Inter, sans-serif'; g.textAlign = 'center'; g.fillText('NO', w / 2, h / 2 - 6); g.fillText('OFFER', w / 2, h / 2 + 40); });
    const geo = new RoundedBoxGeometry(0.5, 0.66, 0.015, 2, 0.01);
    const mFront = std({ map: front }), mOffer = std({ map: offer }), mNone = std({ map: none, emissive: new THREE.Color(AMBER_HI), emissiveMap: none, emissiveIntensity: 0 });
    const edge = std({ color: 0x18181a });
    const cards = [];
    for (let i = 0; i < N; i++) {
      const c = i % cols, r = Math.floor(i / cols);
      const a = (c - (cols - 1) / 2) * 0.085;
      const g = new THREE.Group(); g.position.set(Math.sin(a) * 9, 0.6 + r * 0.8, -Math.cos(a) * 9 + 9); g.rotation.y = -a; scene.add(g);
      const isNo = noSet.has(i);
      // box material groups: +x,-x,+y,-y,+z,-z
      const mesh = new THREE.Mesh(geo, [edge, edge, edge, edge, mFront, isNo ? mNone : mOffer]); mesh.castShadow = true; g.add(mesh);
      const hal = isNo ? glow(THREE, AMBER, 1.2, 0.8) : null; if (hal) { hal.material.opacity = 0; hal.position.z = -0.25; g.add(hal); }
      cards.push({ g, mesh, isNo, hal, d: c * 0.07 + r * 0.12 + ((i * 53) % 7) * 0.05 });
    }
    ctx.cards = cards; ctx.mNone = mNone;
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), std({ color: 0x0b0b0c, roughness: 0.3, metalness: 0.6 })); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
    const key = new THREE.SpotLight(0xf1f4fa, 50, 30, 0.6, 0.8, 1.3); key.position.set(2, 8, 9); key.target.position.set(0, 2, 0); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); scene.add(key, key.target);
    const fill = new THREE.DirectionalLight(0xdfe4ea, 0.35); fill.position.set(-4, 3, 8); scene.add(fill);
    const l = label(THREE, '18%', { size: 0.07, sub: 'no offer in the main round', anchor: 'center', gap: 0, color: '#f87171', subColor: '#e3e8ef' }); l.position.set(0, 4.7, 0.3); l.material.opacity = 0; scene.add(l); ctx.lab = l;
  }
  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.6, bloomRadius: 0.55, bloomThreshold: 0.75,
    dof: shot === 'dashboard' ? { focus: 1.6, aperture: 0.002, maxblur: 0.007 } : { focus: 10.5, aperture: 0.0008, maxblur: 0.004 } });
  return Object.assign(ctx, post);
}

const CAMS = {
  dashboard: [[0, [0.6, 1.4, 2.4, 0, 1.08, -0.4]], [7, [0.12, 1.26, 1.55, 0, 1.17, -0.45]]],
  cascade: [[0, [2.0, 2.9, 11.6, 0.6, 2.6, 0]], [8, [-1.4, 3.1, 10.6, -0.4, 2.7, 0]]],
};

export function update(ctx, tt) {
  const { camera, shot } = ctx;
  const t = tt / ctx.k;
  const c = path(CAMS[shot] ?? CAMS.cascade)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  if (shot === 'dashboard') {
    const cur = t < 1.2 ? -1 : Math.min(4, Math.floor((t - 1.2) / 0.6));
    if (cur !== ctx._cur) { drawDash(ctx.scr.g, ctx.scr.w, ctx.scr.h, cur); ctx.scr.tex.needsUpdate = true; ctx._cur = cur; }
  } else {
    let any = 0;
    ctx.cards.forEach((C) => { const a = 0.6 + C.d * 1.6; const p = ease((t - a) / 0.6); C.mesh.rotation.y = p * Math.PI; C.g.position.y += 0; C.mesh.position.z = Math.sin(p * Math.PI) * 0.15;
      if (C.isNo) { const on = sstep(a + 0.4, a + 0.9, t); C.hal.material.opacity = 0.45 * on; any = Math.max(any, on); } });
    ctx.mNone.emissiveIntensity = 0.5;
    ctx.lab.material.opacity = sstep(5.2, 6.0, t);
  }
}

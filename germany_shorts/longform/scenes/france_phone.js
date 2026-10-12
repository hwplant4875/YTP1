// France 2026: phones. A generic vertical-video / social-post UI (no real app, logo, handle or name), drawn on canvas.
// shots (?shot=name or name:seconds):
//   posts   (7 s)  two phones float side by side, each with a generic post (blank avatar, grey text bars, a photo of a
//                  school gate) dated 21 SEPT; at 3.5 s an amber underline sweeps under the dates (beat 19-20).
//   viral   (9 s)  hero phone playing a vertical video of blurred faceless pupils, caption "they do less for us";
//                  the view counter climbs to 1.5M while copies of the phone multiply into a glowing wall behind
//                  as the camera pulls back (beats 21-23).
//   anon    (6 s)  a phone lying on a dark table: an anonymous account (blank avatar, "?") posts a call for
//                  SAT 17 OCT, topics FUEL · HOUSING · DISCRIMINATION; the date sits in a dashed amber outline;
//                  share bubbles drift up (beat 132).
import { AMBER } from './lib.js';
import { glow } from './look.js';
import { AMBER_HI, path, clamp01, sstep, fontsReady, finishPost, ctex, spacedText, timing, ease } from './france_lib.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const SW = 540, SH = 1170;     // screen canvas
const rr = (g, x, y, w, h, r) => { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); };

function drawVideo(g, views, cap) {
  // blurred, faceless group of eight pupils on a night street (soft blobs only)
  const bg = g.createLinearGradient(0, 0, 0, SH); bg.addColorStop(0, '#1d1c1f'); bg.addColorStop(0.6, '#2a2622'); bg.addColorStop(1, '#141313'); g.fillStyle = bg; g.fillRect(0, 0, SW, SH);
  const lamp = g.createRadialGradient(400, 260, 10, 400, 260, 380); lamp.addColorStop(0, 'rgba(255,170,90,0.55)'); lamp.addColorStop(1, 'rgba(255,170,90,0)'); g.fillStyle = lamp; g.fillRect(0, 0, SW, SH);
  g.filter = 'blur(10px)';
  const cols = ['#4a4f57', '#6b2f2f', '#2e3a4e', '#55604a', '#8a8478', '#3d4b5a', '#7a5a3a', '#5e5450'];
  for (let i = 0; i < 8; i++) { const x = 40 + i * 62 + (i % 2) * 14, y = 560 + (i % 3) * 30, s = 1 + (i % 2) * 0.12;
    g.fillStyle = cols[i]; rr(g, x - 44 * s, y, 88 * s, 420, 40); g.fill();
    g.fillStyle = '#8c857a'; g.beginPath(); g.ellipse(x, y - 40 * s, 36 * s, 42 * s, 0, 0, 7); g.fill(); }
  g.filter = 'none';
  // gradient for legibility
  const sh = g.createLinearGradient(0, SH * 0.55, 0, SH); sh.addColorStop(0, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(0,0,0,0.75)'); g.fillStyle = sh; g.fillRect(0, SH * 0.55, SW, SH * 0.45);
  // right-hand action column (generic circles)
  for (let i = 0; i < 4; i++) { g.fillStyle = 'rgba(240,235,225,0.9)'; g.beginPath(); g.arc(SW - 50, 600 + i * 120, 26, 0, 7); g.fill(); g.fillStyle = 'rgba(240,235,225,0.75)'; g.font = '600 20px Inter, sans-serif'; g.textAlign = 'center'; g.fillText(['', '', '', ''][i], SW - 50, 650 + i * 120); }
  // caption + counter
  g.textAlign = 'left'; g.fillStyle = '#4a4744'; g.beginPath(); g.arc(54, SH - 232, 24, 0, 7); g.fill(); g.fillStyle = 'rgba(242,236,224,0.8)'; g.fillRect(92, SH - 244, 190, 22);
  if (cap > 0) { g.globalAlpha = cap; g.font = '600 38px Inter, sans-serif'; g.fillText('"they do less for us"', 30, SH - 165); g.globalAlpha = 1; }
  g.fillStyle = 'rgba(0,0,0,0.55)'; rr(g, 24, 70, 300, 64, 32); g.fill();
  g.fillStyle = '#ffb25c'; g.font = '800 40px "Inter Display", Inter, sans-serif'; g.fillText('▶ ' + views, 48, 116);
  // progress bar
  g.fillStyle = 'rgba(255,255,255,0.25)'; g.fillRect(0, SH - 8, SW, 8); g.fillStyle = '#ffb25c'; g.fillRect(0, SH - 8, SW * 0.62, 8);
}
function drawPost(g, variant) {
  g.fillStyle = '#121214'; g.fillRect(0, 0, SW, SH);
  g.fillStyle = '#1c1c1f'; g.fillRect(0, 0, SW, 110); g.fillStyle = 'rgba(240,235,225,0.5)'; for (let i = 0; i < 3; i++) g.fillRect(30 + i * 180, 50, 120, 10);
  // avatar (blank), name bars, date
  g.fillStyle = '#4a4744'; g.beginPath(); g.arc(70, 190, 36, 0, 7); g.fill();
  g.fillStyle = 'rgba(240,235,225,0.75)'; g.fillRect(124, 166, variant ? 170 : 210, 18); g.fillStyle = 'rgba(240,235,225,0.35)'; g.fillRect(124, 198, 120, 14);
  g.fillStyle = '#e9dfca'; g.font = '700 30px Inter, sans-serif'; g.textAlign = 'right'; g.fillText('21 SEPT', SW - 30, 202); g.textAlign = 'left';
  // text lines
  g.fillStyle = 'rgba(240,235,225,0.55)'; for (let i = 0; i < 3; i++) g.fillRect(30, 260 + i * 36, i === 2 ? 260 : 470, 16);
  // photo: school gate with bins at night
  const y0 = 380, h = 520; const bg = g.createLinearGradient(0, y0, 0, y0 + h); bg.addColorStop(0, '#26252a'); bg.addColorStop(1, '#3a332b'); g.fillStyle = bg; g.fillRect(30, y0, SW - 60, h);
  const lamp = g.createRadialGradient(variant ? 140 : 400, y0 + 80, 5, variant ? 140 : 400, y0 + 80, 300); lamp.addColorStop(0, 'rgba(255,170,90,0.6)'); lamp.addColorStop(1, 'rgba(255,170,90,0)'); g.fillStyle = lamp; g.fillRect(30, y0, SW - 60, h);
  g.fillStyle = '#4e4b45'; g.fillRect(30, y0 + 200, SW - 60, 60);   // building band
  g.strokeStyle = '#191a1b'; g.lineWidth = 5; for (let x = 40; x < SW - 30; x += 16) { g.beginPath(); g.moveTo(x, y0 + 300); g.lineTo(x, y0 + 440); g.stroke(); }
  g.fillStyle = '#191a1b'; g.fillRect(30, y0 + 300, SW - 60, 8); g.fillRect(30, y0 + 432, SW - 60, 8);
  const bins = ['#3d4440', '#2f3a35', '#4a4d50', '#3d4440']; for (let i = 0; i < 4; i++) { g.fillStyle = bins[i]; g.fillRect(140 + i * 66, y0 + 370 - (i % 2) * 6, 56, 100); g.fillStyle = '#c9a22a'; g.fillRect(136 + i * 66, y0 + 362 - (i % 2) * 6, 64, 10); }
  g.fillStyle = '#121214'; g.fillRect(30, y0 + h - 30, SW - 60, 30);
  // reactions row
  g.fillStyle = 'rgba(240,235,225,0.5)'; for (let i = 0; i < 4; i++) { g.beginPath(); g.arc(60 + i * 120, 960, 16, 0, 7); g.fill(); g.fillRect(84 + i * 120, 954, 40, 12); }
  g.fillStyle = 'rgba(240,235,225,0.25)'; for (let i = 0; i < 4; i++) g.fillRect(30, 1020 + i * 30, 400 - i * 60, 12);
}
function drawAnon(g, t) {
  g.fillStyle = '#0f0f11'; g.fillRect(0, 0, SW, SH);
  const glowG = g.createRadialGradient(SW / 2, 560, 10, SW / 2, 560, 420); glowG.addColorStop(0, 'rgba(255,178,92,0.18)'); glowG.addColorStop(1, 'rgba(255,178,92,0)'); g.fillStyle = glowG; g.fillRect(0, 0, SW, SH);
  g.fillStyle = '#3a3836'; g.beginPath(); g.arc(70, 150, 38, 0, 7); g.fill(); g.fillStyle = '#9a948a'; g.font = '700 44px Inter, sans-serif'; g.textAlign = 'center'; g.fillText('?', 70, 166);
  g.textAlign = 'left'; g.fillStyle = 'rgba(240,235,225,0.75)'; g.font = '600 28px Inter, sans-serif'; g.fillText('anonymous account', 126, 145); g.fillStyle = 'rgba(240,235,225,0.35)'; g.fillRect(126, 166, 120, 12);
  g.textAlign = 'center'; g.fillStyle = '#e9dfca'; g.font = '700 40px Inter, sans-serif'; spacedText(g, 'SATURDAY', SW / 2, 410, 8, 'center');
  g.font = '800 230px "Inter Display", Inter, sans-serif'; g.fillStyle = '#ffb25c'; g.fillText('17', SW / 2, 640);
  g.font = '700 46px Inter, sans-serif'; g.fillStyle = '#e9dfca'; spacedText(g, 'OCTOBER', SW / 2, 730, 10, 'center');
  // dashed outline
  g.strokeStyle = '#ffb25c'; g.lineWidth = 6; g.setLineDash([22, 16]); g.lineDashOffset = -t * 40; rr(g, 70, 330, SW - 140, 450, 30); g.stroke(); g.setLineDash([]);
  g.font = '600 30px Inter, sans-serif'; g.fillStyle = 'rgba(240,235,225,0.8)'; ['FUEL', 'HOUSING', 'DISCRIMINATION'].forEach((s, i) => { const w = g.measureText(s).width + 40, x = [80, 205, 290][i] + (i === 2 ? -40 : 0);
    const y = i < 2 ? 850 : 912; const xx = i < 2 ? [100, 260][i] : SW / 2 - w / 2; g.strokeStyle = 'rgba(240,235,225,0.5)'; g.lineWidth = 2; rr(g, xx, y - 36, w, 52, 26); g.stroke(); g.textAlign = 'left'; g.fillText(s, xx + 20, y); });
  g.fillStyle = 'rgba(240,235,225,0.25)'; for (let i = 0; i < 3; i++) g.fillRect(40, 1000 + i * 34, 440 - i * 90, 12);
}

export async function setup(THREE, renderer, W, H) {
  const { name, k } = timing(7);
  const shot = name || 'viral';
  await fontsReady();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060607);
  scene.fog = new THREE.FogExp2(0x060607, shot === 'viral' ? 0.05 : 0.08);
  const camera = new THREE.PerspectiveCamera(30, W / H, 0.02, 200);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const body = new THREE.MeshStandardMaterial({ color: 0x1b1c1f, roughness: 0.28, metalness: 0.85 });
  const glass = new THREE.MeshStandardMaterial({ color: 0x050506, roughness: 0.08, metalness: 0.3 });
  const mkScreen = (draw) => { const c = document.createElement('canvas'); c.width = SW; c.height = SH; const g = c.getContext('2d'); draw(g); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return { c, g, t }; };
  const phone = (scr) => {
    const grp = new THREE.Group();
    const b = new THREE.Mesh(new RoundedBoxGeometry(0.76, 1.6, 0.075, 6, 0.07), body); b.castShadow = true; b.receiveShadow = true; grp.add(b);
    const f = new THREE.Mesh(new RoundedBoxGeometry(0.74, 1.58, 0.01, 6, 0.06), glass); f.position.z = 0.034; grp.add(f);
    const s = new THREE.Mesh(new THREE.PlaneGeometry(0.69, 1.495), new THREE.MeshBasicMaterial({ map: scr.t, toneMapped: false })); s.position.z = 0.0405; grp.add(s);
    const cam = new THREE.Mesh(new THREE.CircleGeometry(0.012, 20), new THREE.MeshBasicMaterial({ color: 0x000000 })); cam.position.set(0, 0.72, 0.041); grp.add(cam);
    return grp;
  };
  const ctx = { THREE, scene, camera, shot, k };
  scene.add(new THREE.HemisphereLight(0x8e94a0, 0x080706, 0.35));
  const key = new THREE.SpotLight(0xfff0dc, 40, 20, 0.5, 0.8, 1.4); key.position.set(-2.5, 4, 3.5); key.castShadow = true; key.shadow.mapSize.set(1024, 1024); scene.add(key, key.target);
  const rim = new THREE.SpotLight(AMBER, shot === 'anon' ? 8 : 30, 12, 0.6, 0.6, 1.4); rim.position.set(2.8, 1.6, -2.5); scene.add(rim, rim.target);

  if (shot === 'viral') {
    const scr = mkScreen((g) => drawVideo(g, '0', 0)); ctx.scr = scr;
    const hero = phone(scr); hero.position.set(0, 1.2, 0); hero.rotation.y = -0.18; scene.add(hero); ctx.hero = hero;
    // wall of copies (share the same screen texture)
    const copies = []; const sm = new THREE.MeshBasicMaterial({ map: scr.t, toneMapped: false, transparent: true, opacity: 1 });
    const cb = new THREE.MeshStandardMaterial({ color: 0x141518, roughness: 0.4, metalness: 0.7 });
    const bGeo = new RoundedBoxGeometry(0.76, 1.6, 0.06, 3, 0.07), sGeo = new THREE.PlaneGeometry(0.69, 1.495);
    let n = 0;
    for (let row = -3; row <= 3; row++) for (let col = -9; col <= 9; col++) {
      if (Math.abs(col) <= 1 && Math.abs(row) <= 1) continue;
      const g = new THREE.Group(); const r = Math.hypot(col * 0.95, row * 1.8);
      const ang = col * 0.11; g.position.set(Math.sin(ang) * 12, 1.2 + row * 1.85, -2.5 - (1 - Math.cos(ang)) * 12 - Math.abs(row) * 0.3); g.rotation.y = -ang;
      const bb = new THREE.Mesh(bGeo, cb); g.add(bb); const ss = new THREE.Mesh(sGeo, sm); ss.position.z = 0.031; g.add(ss);
      g.userData.d = r + ((n * 37) % 10) * 0.08; g.scale.setScalar(0.001); scene.add(g); copies.push(g); n++;
    }
    ctx.copies = copies;
    const halo = glow(THREE, AMBER, 7, 0.6); halo.position.set(0, 1.2, -1.2); halo.material.opacity = 0.35; scene.add(halo); ctx.halo = halo;
    rim.target.position.set(0, 1.2, 0); key.target.position.set(0, 1.2, 0);
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: 0x0b0b0c, roughness: 0.25, metalness: 0.7 })); floor.rotation.x = -Math.PI / 2; floor.position.y = -0.8; floor.receiveShadow = true; scene.add(floor);
  } else if (shot === 'posts') {
    const A = mkScreen((g) => drawPost(g, 0)), B = mkScreen((g) => drawPost(g, 1));
    const p1 = phone(A), p2 = phone(B); p1.position.set(-0.55, 1.2, 0); p1.rotation.set(0.04, 0.22, 0.04); p2.position.set(0.55, 1.18, -0.15); p2.rotation.set(0.02, -0.2, -0.05);
    scene.add(p1, p2); ctx.p1 = p1; ctx.p2 = p2;
    // amber underline bars (3D, in front of the date on each screen)
    const um = new THREE.MeshBasicMaterial({ color: AMBER_HI, toneMapped: false });
    ctx.unders = [p1, p2].map((p) => { const u = new THREE.Mesh(new THREE.PlaneGeometry(0.17, 0.008), um); u.position.set(0.345 - 0.03 - 0.085, 0.7475 - 210 / SH * 1.495, 0.042); u.geometry.translate(0.085, 0, 0); u.position.x -= 0.085; p.add(u); u.scale.x = 0.001; return u; });
    const ug = [p1, p2].map((p) => { const s = glow(THREE, AMBER, 0.35, 0.8); s.position.set(0.2, 0.7475 - 210 / SH * 1.495, 0.05); s.material.opacity = 0; p.add(s); return s; }); ctx.ug = ug;
    key.target.position.set(0, 1.2, 0); rim.target.position.set(0, 1.2, 0);
  } else if (shot === 'anon') {
    const scr = mkScreen((g) => drawAnon(g, 0)); ctx.scr = scr;
    const p = phone(scr); p.rotation.x = -Math.PI / 2; p.rotation.z = 0.25; p.position.set(0, 0.045, 0); scene.add(p); ctx.hero = p;
    const tableT = ctex(THREE, 1024, 1024, (g, w, h) => { g.fillStyle = '#1a1714'; g.fillRect(0, 0, w, h); for (let i = 0; i < 260; i++) { g.strokeStyle = `rgba(${40 + Math.random() * 30},${32 + Math.random() * 20},${24},0.5)`; g.lineWidth = 1 + Math.random() * 3; g.beginPath(); const y = Math.random() * h; g.moveTo(0, y); g.bezierCurveTo(w * 0.3, y + 10, w * 0.6, y - 10, w, y + 4); g.stroke(); } }, { repeat: [2, 2] });
    const table = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), new THREE.MeshStandardMaterial({ map: tableT, roughness: 0.55, metalness: 0.05 })); table.rotation.x = -Math.PI / 2; table.receiveShadow = true; scene.add(table);
    const screenLight = new THREE.PointLight(0xffd2a0, 3, 2.5, 2); screenLight.position.set(0, 0.35, 0); scene.add(screenLight);
    key.position.set(-1.5, 3.5, 1.5); key.target.position.set(0, 0, 0); key.intensity = 14; rim.position.set(1.5, 0.6, -1.5); rim.target.position.set(0, 0, 0);
    // share bubbles (rounded quads drifting up)
    const bt = ctex(THREE, 256, 96, (g, w, h) => { g.fillStyle = 'rgba(28,28,30,0.92)'; rr(g, 2, 2, w - 4, h - 4, 44); g.fill(); g.strokeStyle = 'rgba(255,178,92,0.8)'; g.lineWidth = 3; rr(g, 2, 2, w - 4, h - 4, 44); g.stroke();
      g.fillStyle = '#ffb25c'; g.beginPath(); g.arc(48, h / 2, 20, 0, 7); g.fill(); g.fillStyle = 'rgba(240,235,225,0.6)'; g.fillRect(84, 36, 130, 10); g.fillRect(84, 54, 90, 8); });
    ctx.bubbles = [];
    for (let i = 0; i < 14; i++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(0.27, 0.1), new THREE.MeshBasicMaterial({ map: bt, transparent: true, opacity: 0, depthWrite: false, toneMapped: false }));
      m.userData = { a: i * 2.39, r: 0.75 + (i % 4) * 0.2, t0: 1.2 + i * 0.28 }; scene.add(m); ctx.bubbles.push(m); }
  }
  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.55, bloomRadius: 0.55, bloomThreshold: 0.78,
    dof: shot === 'viral' ? { focus: 3.2, aperture: 0.0012, maxblur: 0.006 } : shot === 'anon' ? { focus: 2.2, aperture: 0.0025, maxblur: 0.008 } : { focus: 3.0, aperture: 0.0012, maxblur: 0.005 } });
  return Object.assign(ctx, post);
}

const CAMS = {
  posts: [[0, [-0.4, 1.32, 4.4, 0, 1.2, 0]], [7, [0.25, 1.26, 3.9, 0.02, 1.2, 0]]],
  viral: [[0, [0.15, 1.25, 3.3, 0, 1.2, 0]], [3.0, [0.2, 1.3, 3.6, 0, 1.2, 0]], [9, [0.9, 1.6, 7.2, 0, 1.25, -1.5]]],
  anon: [[0, [0.3, 3.0, 1.5, 0, 0, 0]], [6, [0.12, 2.55, 1.2, 0, 0, -0.02]]],
};

export function update(ctx, tt) {
  const { camera, shot } = ctx;
  const t = tt / ctx.k;
  const c = path(CAMS[shot] ?? CAMS.viral)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  if (shot === 'viral') {
    const p = ease((t - 1.0) / 6.5);
    const v = 1.5e6 * Math.pow(p, 2.2);
    const s = v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : v >= 1e3 ? Math.round(v / 1e3) + 'K' : String(Math.round(v));
    drawVideo(ctx.scr.g, s + ' views', sstep(0.8, 1.6, t)); ctx.scr.t.needsUpdate = true;
    const R = 2 + 14 * ease((t - 2.5) / 5.5);
    ctx.copies.forEach(g => { const a = clamp01((R - g.userData.d) / 1.2); g.scale.setScalar(Math.max(0.001, ease(a))); });
    ctx.halo.material.opacity = 0.25 + 0.35 * sstep(3, 8, t);
    ctx.hero.rotation.y = -0.18 + 0.12 * sstep(0, 9, t);
  } else if (shot === 'posts') {
    const u = ease((t - 3.4) / 0.9);
    ctx.unders.forEach((m, i) => { const uu = ease((t - 3.4 - i * 0.25) / 0.9); m.scale.x = Math.max(0.001, uu); });
    ctx.ug.forEach((s, i) => { s.material.opacity = 0.5 * sstep(3.6 + i * 0.25, 4.2 + i * 0.25, t); });
    ctx.p1.position.y = 1.2 + Math.sin(t * 0.8) * 0.015; ctx.p2.position.y = 1.18 + Math.sin(t * 0.7 + 1) * 0.015;
  } else if (shot === 'anon') {
    drawAnon(ctx.scr.g, t); ctx.scr.t.needsUpdate = true;
    ctx.bubbles.forEach((b) => { const { a, r, t0 } = b.userData; const p = clamp01((t - t0) / 2.6); b.material.opacity = p > 0 ? Math.sin(p * Math.PI) * 0.95 : 0;
      b.position.set(Math.cos(a) * r * (0.8 + p * 0.5), 0.12 + p * 0.9, Math.sin(a) * r * 0.7 * (0.8 + p * 0.5)); b.lookAt(camera.position); });
  }
}

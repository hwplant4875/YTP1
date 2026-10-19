// Low-poly PS1 / DS style scenes for IF TOON "Remember Everything". shot = bed|class|close ; mode = ps1|ds
export async function setup(THREE, renderer, W, H) {
  const q = new URLSearchParams(location.search).get('shot') || 'bed,ps1';
  const [shot, mode] = q.split(','); const DS = mode === 'ds';
  renderer.toneMapping = THREE.NoToneMapping;
  const scene = new THREE.Scene();
  const bgc = DS ? (shot==='class'?0xbfe3ff:0x30406a) : 0x0a0d1c;
  scene.background = new THREE.Color(bgc);
  scene.fog = new THREE.Fog(bgc, DS ? 9 : 4.5, DS ? 22 : 11);
  const cam = new THREE.PerspectiveCamera(DS ? 50 : 58, W / H, 0.1, 60);
  const snap = DS ? [128, 96] : [160, 120];
  const tex = (w, h, draw) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); g.imageSmoothingEnabled = false; draw(g, w, h);
    const t = new THREE.CanvasTexture(c); t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; t.colorSpace = THREE.SRGBColorSpace; return t; };
  const jit = m => { m.onBeforeCompile = s => { s.vertexShader = s.vertexShader.replace('#include <project_vertex>', `#include <project_vertex>
      vec2 res = vec2(${snap[0]}.0, ${snap[1]}.0); gl_Position.xy = floor(gl_Position.xy / gl_Position.w * res + 0.5) / res * gl_Position.w;`); }; return m; };
  const mat = (o) => jit(DS ? new THREE.MeshToonMaterial(o) : new THREE.MeshLambertMaterial(o));
  const box = (w, h, d, o, x, y, z, p = scene) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(o)); m.position.set(x, y, z); p.add(m); return m; };
  const noise = (base, amt, w = 32, h = 32, lines = 0) => tex(w, h, (g) => { for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const v = (Math.random() - 0.5) * amt; const c = base.map(b => Math.max(0, Math.min(255, b + v))); g.fillStyle = `rgb(${c})`; g.fillRect(x, y, 1, 1); }
    if (lines) { g.fillStyle = 'rgba(0,0,0,0.25)'; for (let y = 0; y < h; y += lines) g.fillRect(0, y, w, 1); } });
  // ---------- person ----------
  const faceTex = (expr) => tex(32, 32, (g) => { g.fillStyle = '#f0c8a0'; g.fillRect(0, 0, 32, 32); g.fillStyle = '#2a1a14';
    g.fillRect(6, 9, 7, 2); g.fillRect(19, 9, 7, 2); // brows
    if (expr === 'glow') { g.fillStyle = '#7ff7ff'; g.fillRect(7, 12, 5, 4); g.fillRect(20, 12, 5, 4); g.fillStyle = '#ffffff'; g.fillRect(8, 13, 2, 2); g.fillRect(21, 13, 2, 2); }
    else { g.fillStyle = '#ffffff'; g.fillRect(7, 12, 5, 4); g.fillRect(20, 12, 5, 4); g.fillStyle = '#20140e'; g.fillRect(9, 12, 3, 4); g.fillRect(22, 12, 3, 4); }
    g.fillStyle = '#c9906c'; g.fillRect(15, 15, 2, 5); g.fillStyle = '#8a3a30'; g.fillRect(12, 23, 8, 2); g.fillStyle = '#e8a890'; g.fillRect(3, 18, 4, 2); g.fillRect(25, 18, 4, 2); });
  function person(x, z, ry, { shirt = 0x2f6fd8, expr = 'n', sit = false, hair = 0x2a1a14 } = {}) {
    const p = new THREE.Group(); p.position.set(x, 0, z); p.rotation.y = ry; scene.add(p);
    const skin = { color: 0xf0c8a0 };
    const ly = sit ? 0.45 : 0;
    if (sit) { box(0.17, 0.16, 0.5, { color: 0x2a3550 }, -0.11, 0.48, 0.2, p); box(0.17, 0.16, 0.5, { color: 0x2a3550 }, 0.11, 0.48, 0.2, p); box(0.16, 0.45, 0.16, { color: 0x2a3550 }, -0.11, 0.22, 0.45, p); box(0.16, 0.45, 0.16, { color: 0x2a3550 }, 0.11, 0.22, 0.45, p); }
    else { box(0.17, 0.8, 0.18, { color: 0x2a3550 }, -0.11, 0.4, 0, p); box(0.17, 0.8, 0.18, { color: 0x2a3550 }, 0.11, 0.4, 0, p); }
    const ty = sit ? 0.56 : 0.8;
    const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.2, 0.62, 6), mat({ color: shirt, flatShading: true })); torso.position.set(0, ty + 0.31, 0); p.add(torso);
    box(0.13, 0.55, 0.13, { color: shirt }, -0.32, ty + 0.3, 0, p).rotation.z = 0.12; box(0.13, 0.55, 0.13, { color: shirt }, 0.32, ty + 0.3, 0, p).rotation.z = -0.12;
    box(0.11, 0.11, 0.11, skin, -0.35, ty + 0.0, 0, p); box(0.11, 0.11, 0.11, skin, 0.35, ty + 0.0, 0, p);
    box(0.1, 0.1, 0.1, skin, 0, ty + 0.66, 0, p);
    // head: low-poly box with face texture on front
    const fm = mat({ map: faceTex(expr) }), sm = mat({ color: 0xf0c8a0 });
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.42, 0.36), [sm, sm, sm, sm, fm, sm]); head.position.set(0, ty + 0.92, 0); p.add(head);
    box(0.42, 0.14, 0.4, { color: hair }, 0, ty + 1.15, -0.01, p); box(0.42, 0.3, 0.1, { color: hair }, 0, ty + 1.0, -0.19, p);
    box(0.06, 0.24, 0.36, { color: hair }, -0.2, ty + 1.03, 0, p); box(0.06, 0.24, 0.36, { color: hair }, 0.2, ty + 1.03, 0, p);
    return p; }
  // memory panels: floating pixel "photos"
  const memTex = (i) => tex(24, 18, (g) => { const pals = [['#ffcf6a', '#e86a3a', '#3a2a5a'], ['#7fd0ff', '#3a6ad8', '#1a2a4a'], ['#a8e86a', '#3a9a4a', '#1a3a2a'], ['#ff9ad0', '#c83a8a', '#3a1a3a']];
    const P = pals[i % 4]; g.fillStyle = P[0]; g.fillRect(0, 0, 24, 9); g.fillStyle = P[1]; g.fillRect(0, 9, 24, 9); g.fillStyle = P[2];
    g.fillRect(4 + (i * 5) % 12, 6, 4, 8); g.fillStyle = '#f0c8a0'; g.fillRect(4 + (i * 5) % 12, 3, 4, 3); g.fillStyle = '#ffffff'; g.fillRect(0, 0, 24, 1); g.fillRect(0, 17, 24, 1); g.fillRect(0, 0, 1, 18); g.fillRect(23, 0, 1, 18); });
  function memories(cx, cy, cz, n, rad) { const out = []; for (let i = 0; i < n; i++) { const a = Math.PI * (0.92 + 1.16 * i / (n - 1)), r = rad * (0.7 + (i % 3) * 0.2);
      const m = new THREE.Mesh(new THREE.PlaneGeometry(0.48, 0.36), jit(new THREE.MeshBasicMaterial({ map: memTex(i), side: THREE.DoubleSide, fog: true })));
      m.position.set(cx + Math.cos(a) * r, cy + Math.sin(i * 1.7) * 0.5 + (i % 2) * 0.3, cz + Math.sin(a) * r); m.lookAt(cx, cy, cz); scene.add(m); out.push(m); } return out; }
  // ---------- sets ----------
  const wall = noise(DS ? [150, 170, 210] : [70, 78, 110], 18, 32, 32), floorT = noise(DS ? [150, 110, 80] : [80, 60, 50], 22, 32, 32, 8);
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(6, 6); wall.wrapS = wall.wrapT = THREE.RepeatWrapping; wall.repeat.set(4, 2);
  const fl = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), mat({ map: floorT })); fl.rotation.x = -Math.PI / 2; scene.add(fl);
  const bw = new THREE.Mesh(new THREE.PlaneGeometry(14, 5), mat({ map: wall })); bw.position.set(0, 2.5, -3); scene.add(bw);
  const lw = new THREE.Mesh(new THREE.PlaneGeometry(14, 5), mat({ map: wall })); lw.position.set(-3.5, 2.5, 0); lw.rotation.y = Math.PI / 2; scene.add(lw);
  const amb = new THREE.AmbientLight(0xffffff, DS ? 1.1 : 0.35); scene.add(amb);
  const key = new THREE.DirectionalLight(DS ? 0xfff2dd : 0x9fb4ff, DS ? 1.6 : 1.1); key.position.set(2, 4, 3); scene.add(key);
  let lookAt;
  if (shot === 'bed') {
    box(2.0, 0.35, 1.2, { color: 0x6a4a3a }, 0.3, 0.18, -2.2); box(2.0, 0.18, 1.2, { color: DS ? 0xe8eef8 : 0x9aa6c8 }, 0.3, 0.44, -2.2); box(0.5, 0.15, 0.9, { color: 0xffffff }, -0.5, 0.58, -2.2);
    box(0.5, 0.5, 0.5, { color: 0x5a3a2a }, 1.65, 0.25, -2.5); box(0.22, 0.12, 0.08, { color: 0x111111 }, 1.65, 0.56, -2.4);
    const win = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 1.0), jit(new THREE.MeshBasicMaterial({ map: tex(16, 12, g => { g.fillStyle = DS ? '#3a5aa8' : '#101a3a'; g.fillRect(0, 0, 16, 12); g.fillStyle = '#fff6c8'; g.fillRect(11, 2, 2, 2); [[2, 3], [6, 1], [4, 7], [9, 6], [13, 8]].forEach(([x, y]) => { g.fillStyle = '#ffffff'; g.fillRect(x, y, 1, 1); }); g.fillStyle = '#6a4a3a'; g.fillRect(7, 0, 2, 12); g.fillRect(0, 5, 16, 2); }), fog: false })));
    win.position.set(-0.6, 2.0, -2.98); scene.add(win);
    const pl = new THREE.PointLight(0x7ff7ff, DS ? 1.2 : 2.2, 6, 1.5); pl.position.set(0.3, 2.4, -1.2); scene.add(pl);
    person(0.3, -1.9, 0, { shirt: 0xf2b51e, expr: 'glow', sit: true }).position.y = 0.1;
    memories(0.3, 1.7, -1.9, 14, 1.5);
    cam.position.set(0.9, 1.5, 0.9); lookAt = [0.2, 1.35, -1.9];
  } else if (shot === 'class') {
    const board = new THREE.Mesh(new THREE.PlaneGeometry(4, 1.6), mat({ map: tex(64, 26, g => { g.fillStyle = '#1e3a2a'; g.fillRect(0, 0, 64, 26); g.fillStyle = '#d8e8d8'; for (let y = 3; y < 24; y += 3) for (let x = 3; x < 60; x += 1) if (Math.random() < 0.55) g.fillRect(x, y, 1, 1); }) }));
    board.position.set(0.2, 1.75, -2.97); scene.add(board);
    for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) { const x = -1.8 + c * 1.25, z = -0.8 + r * 1.3; box(0.8, 0.06, 0.5, { color: 0xb08050 }, x, 0.72, z - 0.35); box(0.06, 0.7, 0.06, { color: 0x555555 }, x - 0.35, 0.36, z - 0.35); box(0.06, 0.7, 0.06, { color: 0x555555 }, x + 0.35, 0.36, z - 0.35);
      if (!(r === 1 && c === 1) && !(r === 0 && (c === 1 || c === 2))) person(x, z, Math.PI, { shirt: [0x3a7ad8, 0xd84a3a, 0x4ab86a, 0x8a5ad8][(r + c) % 4], sit: true, hair: [0x2a1a14, 0x6a3a1a, 0x111111][(r * 4 + c) % 3] }); }
    const hero = person(-0.55, 0.5, Math.PI, { shirt: 0xf2b51e, sit: true, expr: 'glow' });
    const hl = new THREE.PointLight(0x7ff7ff, DS ? 2 : 4, 3, 1.5); hl.position.set(-0.55, 1.7, -0.3); scene.add(hl);
    // hero has the open notebook glowing
    const nb = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.3), jit(new THREE.MeshBasicMaterial({ color: 0x9ff8ff, fog: false }))); nb.rotation.x = -Math.PI / 2; nb.position.set(-0.55, 0.76, 0.15); scene.add(nb);
    const t = person(1.9, -2.3, 0, { shirt: 0x6a6a7a }); 
    cam.position.set(1.6, 2.1, -2.5); lookAt = [-0.5, 1.0, 0.7];
  } else { // close: face close-up with memories, thumbnail angle
    const pl = new THREE.PointLight(0x7ff7ff, DS ? 3 : 7, 5, 1.5); pl.position.set(0, 1.6, 0.6); scene.add(pl);
    person(0, -0.5, 0, { shirt: 0xf2b51e, expr: 'glow' }); memories(0, 1.6, -0.5, 18, 1.6);
    cam.position.set(0.0, 1.75, 0.75); lookAt = [0, 1.68, -0.5];
  }
  cam.lookAt(...lookAt);
  return { scene, camera: cam };
}
export function update(c, t) {}

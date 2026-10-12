// France 2026: stylised stand-off outside a lycée at dusk. A line of riot police (faceless: helmets with dark visors,
// shields) faces a crowd of faceless pupils across 12 m of street, tear-gas haze drifting between. No contact, no injuries.
// Street runs along x; police line at z = -6, pupils around z = +6, lycée gate/fence behind the pupils at z = +11.
// shots (?shot=name or name:seconds):
//   standoff     (7 s)  low behind the pupils' backs and placards, slow push toward the shield line; haze lit amber
//                       from a sodium lamp behind the police (beat: amber haze swells 2-4 s).
//   behind_line  (7 s)  reverse angle: behind the police helmets and shoulders, lateral track; the pupils far off in
//                       the haze, an amber street light picking out the shields' edges.
import { AMBER } from './lib.js';
import { glow, beam } from './look.js';
import { AMBER_HI, path, clamp01, sstep, fontsReady, finishPost, ctex, timing, figure } from './france_lib.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

export async function setup(THREE, renderer, W, H) {
  const { name, k } = timing(7);
  const shot = name || 'standoff';
  await fontsReady();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b0c0e);
  scene.fog = new THREE.FogExp2(0x15151a, 0.045);
  const camera = new THREE.PerspectiveCamera(32, W / H, 0.05, 300);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.85, metalness: 0, ...o });
  let seed = 7; const R = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  const bake = (grp) => {           // one mesh per material
    grp.updateMatrixWorld(true); const buckets = new Map();
    grp.traverse(o => { if (!o.isMesh) return; let g = o.geometry.index ? o.geometry.toNonIndexed() : o.geometry.clone();
      for (const kk of Object.keys(g.attributes)) if (!['position', 'normal', 'uv'].includes(kk)) g.deleteAttribute(kk);
      if (!g.attributes.uv) g.setAttribute('uv', new THREE.Float32BufferAttribute(new Float32Array(g.attributes.position.count * 2), 2));
      g.applyMatrix4(o.matrixWorld); if (!buckets.has(o.material)) buckets.set(o.material, []); buckets.get(o.material).push(g); });
    const out = new THREE.Group(); for (const [m, gs] of buckets) { const me = new THREE.Mesh(mergeGeometries(gs), m); me.castShadow = me.receiveShadow = true; out.add(me); } return out;
  };

  // ------------------------------------------------------------------ street
  const asphalt = ctex(THREE, 1024, 1024, (g, w, h) => { g.fillStyle = '#2b2b2c'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 40000; i++) { const v = 30 + R() * 60; g.fillStyle = `rgba(${v},${v},${v},0.3)`; g.fillRect(R() * w, R() * h, 1 + R() * 2, 1 + R() * 2); }
    for (let i = 0; i < 12; i++) { g.fillStyle = 'rgba(10,10,10,0.25)'; g.beginPath(); g.ellipse(R() * w, R() * h, 40 + R() * 120, 20 + R() * 60, R() * 3, 0, 7); g.fill(); } }, { repeat: [12, 6] });
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(120, 60), std({ map: asphalt, roughness: 0.7, metalness: 0.15 })); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
  // lane markings
  for (let x = -40; x < 40; x += 4) { const m = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 0.14), std({ color: 0x9c978b })); m.rotation.x = -Math.PI / 2; m.position.set(x, 0.004, 0); scene.add(m); }
  // kerbs + pavements
  for (const z of [-9, 9.5]) { const kb = new THREE.Mesh(new THREE.BoxGeometry(120, 0.15, 3.0), std({ color: 0x55534e })); kb.position.set(0, 0.075, z + Math.sign(z) * 1.5); kb.receiveShadow = true; scene.add(kb); }
  // buildings both sides (simple blocks with lit / dark windows)
  const winTex = (lit) => ctex(THREE, 512, 512, (g, w, h) => { g.fillStyle = '#3a3936'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < 4; y++) for (let x = 0; x < 4; x++) { const on = R() < lit; g.fillStyle = on ? `rgb(${190 + R() * 50},${150 + R() * 40},${90 + R() * 30})` : '#141518'; g.fillRect(x * 128 + 28, y * 128 + 22, 72, 84); g.fillStyle = 'rgba(0,0,0,0.3)'; g.fillRect(x * 128 + 28, y * 128 + 22, 72, 6); } }, { repeat: [3, 2] });
  const bA = std({ map: winTex(0.15), emissive: 0xffffff, emissiveMap: winTex(0.15), emissiveIntensity: 0.0 });
  for (let i = 0; i < 9; i++) {
    const w = 8 + R() * 6, h = 12 + R() * 10;
    const b1 = new THREE.Mesh(new THREE.BoxGeometry(w, h, 8), bA); b1.position.set(-40 + i * 10, h / 2, -15); scene.add(b1);
  }
  // the lycée behind the pupils: low concrete block + fence + gate
  const conc = std({ color: 0x6d6a64, roughness: 0.95 });
  const lyc = new THREE.Mesh(new THREE.BoxGeometry(40, 9, 10), std({ map: winTex(0.05), roughness: 0.9 })); lyc.position.set(0, 4.5, 19); scene.add(lyc);
  const fence = new THREE.Group(); const fm = std({ color: 0x2f3433, metalness: 0.6, roughness: 0.5 });
  for (let x = -20; x <= 20; x += 0.16) { if (Math.abs(x) < 2) continue; const b = new THREE.Mesh(new THREE.BoxGeometry(0.03, 2.0, 0.03), fm); b.position.set(x, 1.0, 11.2); fence.add(b); }
  for (const y of [0.2, 1.95]) { const r = new THREE.Mesh(new THREE.BoxGeometry(40, 0.05, 0.05), fm); r.position.set(0, y, 11.2); fence.add(r); }
  for (const x of [-2.1, 2.1]) { const p = new THREE.Mesh(new THREE.BoxGeometry(0.25, 2.6, 0.25), conc); p.position.set(x, 1.3, 11.2); fence.add(p); }
  scene.add(bake(fence));
  // bins at the gate
  const binM = [0x3d4440, 0x2f3a35].map(c => std({ color: c, roughness: 0.6 })); const lidM = std({ color: 0xd8b02a, roughness: 0.5 });
  for (const [x, z, r] of [[-1.2, 11.9, 0.1], [-0.4, 12.0, -0.2], [0.5, 11.9, 0.15], [1.3, 12.0, -0.1]]) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.95, 0.72), binM[Math.round(x * 3) & 1]); b.position.set(x, 0.5, z); b.rotation.y = r; b.castShadow = true; scene.add(b); const l = new THREE.Mesh(new THREE.BoxGeometry(0.66, 0.05, 0.8), lidM); l.position.set(x, 1.0, z); l.rotation.y = r; scene.add(l); }

  // ------------------------------------------------------------------ police line (faceless: dark visor shells)
  const pm = { body: std({ color: 0x1d2128, roughness: 0.7 }), head: std({ color: 0x1d2128 }), dark: std({ color: 0x121418, roughness: 0.6 }),
    visor: std({ color: 0x0a0b0d, roughness: 0.1, metalness: 0.8 }), shield: new THREE.MeshPhysicalMaterial({ color: 0x9aa3a8, roughness: 0.15, transparent: true, opacity: 0.55, metalness: 0.1 }) };
  const police = new THREE.Group(); scene.add(police);
  for (let i = 0; i < 11; i++) { const f = figure(THREE, pm, { build: 'police', height: 1.82 + R() * 0.06 }); f.position.set(-7.5 + i * 1.5 + (R() - 0.5) * 0.2, 0, -6 + (R() - 0.5) * 0.3); police.add(f); }
  for (let i = 0; i < 7; i++) { const f = figure(THREE, pm, { build: 'police', height: 1.84, shield: false }); f.position.set(-6 + i * 2, 0, -7.6 + R() * 0.3); police.add(f); }
  // police van behind
  const van = new THREE.Group(); { const vm = std({ color: 0x2a2f38, roughness: 0.5, metalness: 0.3 }); const b = new THREE.Mesh(new THREE.BoxGeometry(5.6, 2.4, 2.1), vm); b.position.y = 1.5; van.add(b);
    const cab = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.6, 2.0), std({ color: 0x0c0d10, roughness: 0.1, metalness: 0.5 })); cab.position.set(2.6, 1.6, 0); van.add(cab);
    for (const x of [-1.8, 1.8]) for (const z of [-1, 1]) { const w = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 0.3, 18), std({ color: 0x0b0b0b })); w.rotation.x = Math.PI / 2; w.position.set(x, 0.4, z); van.add(w); } }
  van.position.set(4.5, 0, -10.2); scene.add(van);
  const vanB = van.clone(); vanB.position.set(-6, 0, -10.6); vanB.rotation.y = 0.1; scene.add(vanB);

  // ------------------------------------------------------------------ pupils (faceless)
  const hoodies = [0x4a4f57, 0x6b2f2f, 0x2e3a4e, 0x55604a, 0x8a8478, 0x2a2a2c, 0x7a5a3a, 0x3d4b5a].map(c => std({ color: c, roughness: 0.9 }));
  const skin = std({ color: 0xcfc7bb, roughness: 0.55 }); const pants = std({ color: 0x2b2f38 }); const shoe = std({ color: 0x1c1c1e });
  const signTex = (lines) => ctex(THREE, 512, 340, (g, w, h) => { g.fillStyle = '#ece6d6'; g.fillRect(0, 0, w, h); g.fillStyle = '#16161a'; g.font = 'bold 66px "DejaVu Sans Condensed", sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    lines.forEach((s, i) => g.fillText(s, w / 2, h / 2 + (i - (lines.length - 1) / 2) * 80)); });
  const signs = [['ON VEUT', 'DES PROFS'], ['LYCÉE', 'EN LUTTE'], ['PAS TOUCHE', 'À NOS', 'LYCÉENS'], ['NOTRE', 'AVENIR']].map(l => std({ map: signTex(l), roughness: 0.9 }));
  const card = std({ color: 0xb9ab8e, roughness: 0.95 });
  const crowd = new THREE.Group(); scene.add(crowd);
  for (let i = 0; i < 34; i++) {
    const row = Math.floor(i / 9), x = -7 + (i % 9) * 1.7 + (R() - 0.5) * 0.8, z = 5.0 + row * 1.4 + (R() - 0.5) * 0.6;
    const sg = [2, 6, 12, 20].indexOf(i);
    const f = figure(THREE, { body: hoodies[i % 8], head: skin, dark: pants, shoe, pack: hoodies[(i + 3) % 8], hair: pants, stick: std({ color: 0x8a7050 }) },
      { hood: i % 3 === 0, hair: i % 3 !== 0, backpack: i % 2 === 0, height: 1.6 + R() * 0.18, armsUp: (i === 4 || i === 15) ? 1 : 0 });
    if (sg >= 0) {     // placard: printed side faces the police (+z local), plain card on the back
      const st = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.9, 6), std({ color: 0x8a7050 })); st.position.set(0.26, 1.71, 0.06); f.add(st);
      const fr = new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.46), signs[sg]); fr.position.set(0.26, 2.28, 0.08); f.add(fr);
      const bk = new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.46), card); bk.position.set(0.26, 2.28, 0.07); bk.rotation.y = Math.PI; f.add(bk);
    }
    f.position.set(x, 0, z); f.rotation.y = Math.PI + (R() - 0.5) * 0.4; crowd.add(f);
  }
  const crowdBaked = bake(crowd); scene.remove(crowd); scene.add(crowdBaked);
  const policeBaked = bake(police); scene.remove(police); scene.add(policeBaked);

  // ------------------------------------------------------------------ haze (soft sprites)
  const puff = ctex(THREE, 256, 256, (g) => { const grd = g.createRadialGradient(128, 128, 0, 128, 128, 128); grd.addColorStop(0, 'rgba(255,255,255,0.5)'); grd.addColorStop(0.6, 'rgba(255,255,255,0.15)'); grd.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = grd; g.fillRect(0, 0, 256, 256); });
  const haze = [];
  for (let i = 0; i < 38; i++) { const m = new THREE.SpriteMaterial({ map: puff, color: 0xd8cfc0, transparent: true, opacity: 0.12, depthWrite: false });
    const s = new THREE.Sprite(m); const sc = 3 + R() * 5; s.scale.set(sc * 1.6, sc, 1); s.position.set(-14 + R() * 28, 0.6 + R() * 2.2, -4 + R() * 7); s.userData = { x: s.position.x, v: 0.15 + R() * 0.25, ph: R() * 6 }; scene.add(s); haze.push(s); }

  // ------------------------------------------------------------------ light
  scene.add(new THREE.HemisphereLight(0x6f7a8c, 0x0c0b0a, 0.45));
  const moon = new THREE.DirectionalLight(0x9aa8bc, 0.45); moon.position.set(-20, 30, 10); scene.add(moon);
  const lamps = [];
  for (const [x, z, col, I] of [[2.5, -9.6, 0xff9a3a, 260], [-9, -9.6, 0xff9a3a, 180], [9, 9.8, 0xff9a3a, 160], [-6, 9.8, 0xffa850, 120]]) {
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.09, 7, 10), std({ color: 0x2a2c2d, metalness: 0.5 })); pole.position.set(x, 3.5, z); scene.add(pole);
    const s = new THREE.SpotLight(col, I, 26, 0.95, 0.6, 1.4); s.position.set(x, 6.8, z * 0.88); s.target.position.set(x, 0, z * 0.5); s.castShadow = I > 150; s.shadow.mapSize.set(1024, 1024); s.shadow.bias = -0.0005; scene.add(s, s.target);
    const bulb = glow(THREE, 0xffb060, 1.8, 1); bulb.position.set(x, 6.75, z * 0.88); scene.add(bulb);
    const bm = beam(THREE, 0xffa04a, 7, 3.6, 0.045); bm.position.set(x, 6.8, z * 0.88); scene.add(bm);
    lamps.push(s);
  }
  // amber back light behind the police (for silhouettes in standoff) and behind the pupils (for behind_line)
  const backP = new THREE.SpotLight(AMBER, 0, 40, 0.7, 0.7, 1.2); backP.position.set(0, 3.2, -15); backP.target.position.set(0, 1.2, 0); scene.add(backP, backP.target);
  const backS = new THREE.SpotLight(AMBER, 0, 40, 0.7, 0.7, 1.2); backS.position.set(0, 3.2, 16); backS.target.position.set(0, 1.2, 0); scene.add(backS, backS.target);
  const beacon = glow(THREE, 0x8fb4ff, 1.2, 1); beacon.position.set(4.5 + 1.2, 2.85, -10.2); scene.add(beacon);

  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.75, bloomRadius: 0.6, bloomThreshold: 0.6, exposure: 1.05,
    dof: { focus: shot === 'standoff' ? 15 : 4.5, aperture: 0.0006, maxblur: 0.004 } });
  return { THREE, scene, camera, shot, k, haze, backP, backS, beacon, ...post };
}

const CAMS = {
  standoff: [[0, [-1.3, 2.3, 10.9, 0.2, 1.2, -6]], [7, [-0.7, 2.15, 9.9, 0.2, 1.2, -6]]],
  behind_line: [[0, [-3.4, 2.35, -9.25, -1.2, 1.25, 6]], [7, [-0.6, 2.3, -9.2, 1.0, 1.25, 6]]],
};

export function update(ctx, tt) {
  const { camera, shot } = ctx;
  const t = tt / ctx.k;
  const c = path(CAMS[shot] ?? CAMS.standoff)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  const swell = sstep(1.5, 3.8, t);
  ctx.backP.intensity = shot === 'standoff' ? 40 + 90 * swell : 15;
  ctx.backS.intensity = shot === 'behind_line' ? 40 + 80 * swell : 10;
  ctx.haze.forEach((s, i) => { s.position.x = s.userData.x + Math.sin(t * 0.3 + s.userData.ph) * 0.6 + t * s.userData.v; s.material.opacity = (0.05 + 0.05 * swell) * (0.7 + 0.3 * Math.sin(t * 0.5 + s.userData.ph)); s.material.color.setHex(i % 3 ? 0xe0d2bf : 0xffc58a); });
  ctx.beacon.material.opacity = 0.35 + 0.65 * (Math.sin(t * 9) > 0.3 ? 1 : 0);
}

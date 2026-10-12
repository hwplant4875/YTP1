// France 2026: school time. Two shots in one studio.
// shots (?shot=name or name:seconds):
//   lost_lessons (7 s)  a wall timetable (5 days x 10 slots of subject tiles) in a dim corridor; from 1.6 s one tile
//                       in ten flips over to a blank, amber-edged gap (10% of lycée teaching hours not delivered).
//   hours        (8 s)  two stacks of hour slabs build up side by side (1 slab = 20 h): France 60 slabs = 1,200 h,
//                       OECD average 48 = 960 h. The top 12 French slabs (the extra 240 h) glow amber. Crane up.
import { AMBER } from './lib.js';
import { glow } from './look.js';
import { AMBER_HI, path, clamp01, sstep, fontsReady, finishPost, ctex, spacedText, timing, label, ease, studioFloor } from './france_lib.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const SUBJ = [['MATHS', '#5b6e7a'], ['FRANÇAIS', '#7a5b5b'], ['HIST-GÉO', '#6f6a52'], ['ANGLAIS', '#56705d'], ['PHYSIQUE', '#5d5b78'], ['SVT', '#4f6d6a'], ['PHILO', '#77634f'], ['EPS', '#66605a'], ['ESPAGNOL', '#6d5a6b'], ['SES', '#5a6a55']];

export async function setup(THREE, renderer, W, H) {
  const { name, k: k0 } = timing(7);
  const shot = name || 'hours';
  const k = shot === 'hours' ? k0 * 7 / 8 : k0;
  await fontsReady();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060607);
  scene.fog = new THREE.FogExp2(0x060607, shot === 'hours' ? 0.03 : 0.05);
  const camera = new THREE.PerspectiveCamera(32, W / H, 0.05, 200);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const std = (o) => new THREE.MeshStandardMaterial({ roughness: 0.7, metalness: 0.05, ...o });
  const ctx = { THREE, scene, camera, shot, k };
  scene.add(new THREE.HemisphereLight(0x8e94a0, 0x0a0908, 0.35));

  if (shot === 'lost_lessons') {
    // corridor wall (painted dado) + cork board
    const wallT = ctex(THREE, 1024, 512, (g, w, h) => { g.fillStyle = '#9d978a'; g.fillRect(0, 0, w, h * 0.62); g.fillStyle = '#5f675d'; g.fillRect(0, h * 0.62, w, h * 0.38);
      for (let i = 0; i < 9000; i++) { const v = Math.random() * 40 - 20; g.fillStyle = `rgba(${100 + v},${96 + v},${88 + v},0.06)`; g.fillRect(Math.random() * w, Math.random() * h, 3, 3); } }, { repeat: [3, 1] });
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(24, 6), std({ map: wallT, roughness: 0.9 })); wall.position.set(0, 3, -0.05); wall.receiveShadow = true; scene.add(wall);
    const fl = new THREE.Mesh(new THREE.PlaneGeometry(24, 10), std({ color: 0x3b3833, roughness: 0.5 })); fl.rotation.x = -Math.PI / 2; fl.position.z = 4; fl.receiveShadow = true; scene.add(fl);
    const boardW = 4.6, boardH = 3.2, bx = 0, by = 2.3;
    const frame = new THREE.Mesh(new RoundedBoxGeometry(boardW + 0.16, boardH + 0.16, 0.06, 3, 0.02), std({ color: 0x55504a, metalness: 0.4, roughness: 0.4 })); frame.position.set(bx, by, 0.0); frame.castShadow = true; scene.add(frame);
    const backT = ctex(THREE, 512, 512, (g, w, h) => { g.fillStyle = '#1e1d1b'; g.fillRect(0, 0, w, h); });
    const back = new THREE.Mesh(new THREE.PlaneGeometry(boardW, boardH), std({ map: backT })); back.position.set(bx, by, 0.032); scene.add(back);
    // header row
    const days = ['LUN', 'MAR', 'MER', 'JEU', 'VEN'];
    const colW = (boardW - 0.7) / 5, rowH = (boardH - 0.4) / 10;
    days.forEach((d, i) => { const t = ctex(THREE, 256, 64, (g, w, h) => { g.fillStyle = '#d9cfbd'; g.font = '700 38px Inter, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; spacedText(g, d, w / 2, h / 2, 6, 'center'); });
      const m = new THREE.Mesh(new THREE.PlaneGeometry(colW * 0.9, 0.2), new THREE.MeshBasicMaterial({ map: t, transparent: true })); m.position.set(bx - boardW / 2 + 0.6 + colW * (i + 0.5), by + boardH / 2 - 0.2, 0.04); scene.add(m); });
    for (let r = 0; r < 10; r++) { const t = ctex(THREE, 128, 64, (g, w, h) => { g.fillStyle = '#a49b8b'; g.font = '600 30px Inter, sans-serif'; g.textAlign = 'right'; g.textBaseline = 'middle'; g.fillText(`${8 + r}h`, w - 8, h / 2); });
      const m = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.2), new THREE.MeshBasicMaterial({ map: t, transparent: true })); m.position.set(bx - boardW / 2 + 0.28, by + boardH / 2 - 0.4 - rowH * (r + 0.5), 0.04); scene.add(m); }
    const tileGeo = new RoundedBoxGeometry(colW * 0.92, rowH * 0.86, 0.03, 2, 0.008);
    const subjMat = {};
    const gap = std({ color: 0x0c0c0d, roughness: 0.9, emissive: new THREE.Color(AMBER_HI), emissiveIntensity: 0 });
    const tiles = [];
    let seed = 11; const R = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
    const gone = new Set([3, 12, 17, 35, 41]);    // 5 of 50 = 10%
    for (let d = 0; d < 5; d++) for (let r = 0; r < 10; r++) {
      const idx = d * 10 + r; if (d === 2 && r >= 6) continue;     // Wednesday afternoon free
      const [nm, col] = SUBJ[Math.floor(R() * SUBJ.length)];
      const mat = subjMat[nm] ??= std({ map: ctex(THREE, 256, 96, (g, w, h) => { g.fillStyle = col; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(255,255,255,0.07)'; g.fillRect(0, 0, w, h / 2);
        g.fillStyle = '#efe7d8'; g.font = '700 34px Inter, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(nm, w / 2, h / 2 + 2); }), roughness: 0.55 });
      const t = new THREE.Group(); t.position.set(bx - boardW / 2 + 0.6 + colW * (d + 0.5), by + boardH / 2 - 0.4 - rowH * (r + 0.5), 0.06); scene.add(t);
      const front = new THREE.Mesh(tileGeo, mat); front.castShadow = true; t.add(front);
      const backT2 = new THREE.Mesh(tileGeo, gap); backT2.rotation.y = Math.PI; backT2.position.z = -0.001; t.add(backT2);
      const isGone = gone.has(idx);
      let edge = null;
      if (isGone) { edge = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(colW * 0.92, rowH * 0.86)), new THREE.LineBasicMaterial({ color: AMBER_HI, transparent: true, opacity: 0, toneMapped: false })); edge.position.copy(t.position); edge.position.z = 0.045; scene.add(edge); }
      tiles.push({ t, isGone, edge, ord: [...gone].indexOf(idx) });
    }
    ctx.tiles = tiles; ctx.gapMat = gap;
    const key = new THREE.SpotLight(0xfff1df, 26, 14, 0.42, 0.7, 1.5); key.position.set(-1.8, 5.5, 4.5); key.target.position.set(0, 2.3, 0); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); scene.add(key, key.target);
    const tube = new THREE.RectAreaLight ? null : null;
    const amberPt = new THREE.PointLight(AMBER, 0, 3, 1.8); amberPt.position.set(0, 2.3, 0.8); scene.add(amberPt); ctx.amberPt = amberPt;
  } else {
    scene.add(studioFloor(THREE, { size: 60, tone: 22, pool: 0.12 }));
    const slabGeo = new RoundedBoxGeometry(1.6, 0.085, 1.0, 2, 0.012);
    const fr = std({ color: 0x5a5650, roughness: 0.45, metalness: 0.3 });
    const frHot = std({ color: 0x3a2a1a, roughness: 0.4, metalness: 0.2, emissive: new THREE.Color(AMBER_HI), emissiveIntensity: 0 });
    const oe = std({ color: 0x3b3c3f, roughness: 0.5, metalness: 0.3 });
    const mk = (n, x, matFn) => { const arr = []; for (let i = 0; i < n; i++) { const m = new THREE.Mesh(slabGeo, matFn(i)); m.position.set(x, 0.05 + i * 0.1, 0); m.castShadow = m.receiveShadow = true; m.visible = false; scene.add(m); arr.push(m); } return arr; };
    ctx.fr = mk(60, -1.1, (i) => i >= 48 ? frHot : fr); ctx.oe = mk(48, 1.1, () => oe); ctx.frHot = frHot;
    // 960 h reference line across both stacks
    const ln = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.012, 0.012), new THREE.MeshBasicMaterial({ color: 0xe9dfca, transparent: true, opacity: 0 })); ln.position.set(0, 0.05 + 48 * 0.1 - 0.04, 0.55); scene.add(ln); ctx.ln = ln;
    const lfr = label(THREE, 'FRANCE', { size: 0.036, sub: '≈ 1,200 hours / year', anchor: 'right' }); lfr.position.set(-1.95, 2.6, 0.5); lfr.material.opacity = 0; scene.add(lfr);
    const loe = label(THREE, 'OECD AVERAGE', { size: 0.036, sub: '960 hours / year', anchor: 'left', subColor: '#e9dfca' }); loe.position.set(1.95, 2.6, 0.5); loe.material.opacity = 0; scene.add(loe);
    const lx = label(THREE, '+240 h', { size: 0.05, anchor: 'right', color: '#ffb25c' }); lx.position.set(-1.95, 0.05 + 54 * 0.1, 0.5); lx.material.opacity = 0; scene.add(lx);
    ctx.labs = { lfr, loe, lx };
    const key = new THREE.SpotLight(0xfff1df, 120, 30, 0.5, 0.7, 1.3); key.position.set(-3, 9, 6); key.target.position.set(0, 2.5, 0); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); scene.add(key, key.target);
    const rim = new THREE.SpotLight(AMBER, 25, 20, 0.5, 0.6, 1.3); rim.position.set(-2, 7, -6); rim.target.position.set(-1.1, 4, 0); scene.add(rim, rim.target);
    const fill = new THREE.DirectionalLight(0xdfe4ea, 0.5); fill.position.set(4, 3, 8); scene.add(fill);
    const hotPt = new THREE.PointLight(AMBER, 0, 5, 1.6); hotPt.position.set(-1.1, 5.4, 1.2); scene.add(hotPt); ctx.hotPt = hotPt;
  }
  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.65, bloomRadius: 0.55, bloomThreshold: 0.72,
    dof: shot === 'lost_lessons' ? { focus: 7.2, aperture: 0.0008, maxblur: 0.004 } : null });
  return Object.assign(ctx, post);
}

const CAMS = {
  lost_lessons: [[0, [-1.8, 2.0, 8.4, 0, 2.3, 0]], [7, [-0.6, 2.2, 7.0, 0.1, 2.3, 0]]],
  hours: [[0, [2.6, 1.2, 7.0, 0, 1.0, 0]], [4.8, [1.4, 3.2, 11.0, 0, 2.9, 0]], [8, [0.9, 3.7, 13.2, -0.1, 3.25, 0]]],
};

export function update(ctx, tt) {
  const { camera, shot } = ctx;
  const t = tt / ctx.k;
  const c = path(CAMS[shot] ?? CAMS.hours)(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  if (shot === 'lost_lessons') {
    let hot = 0;
    ctx.tiles.forEach((T) => { if (!T.isGone) return; const a = 1.6 + T.ord * 0.45; const p = ease((t - a) / 0.7);
      T.t.rotation.y = p * Math.PI; T.t.position.z = 0.06 + Math.sin(p * Math.PI) * 0.12; T.edge.material.opacity = 0.95 * sstep(a + 0.5, a + 0.9, t); hot = Math.max(hot, p); });
    ctx.gapMat.emissiveIntensity = 0.18 * hot;
    ctx.amberPt.intensity = 2.5 * hot;
  } else {
    const p = ease((t - 0.3) / 4.2);
    const nf = Math.round(60 * p), no = Math.round(48 * Math.min(1, p * 60 / 48));
    ctx.fr.forEach((m, i) => { m.visible = i < nf; });
    ctx.oe.forEach((m, i) => { m.visible = i < no; });
    const hot = sstep(4.6, 5.4, t);
    ctx.frHot.emissiveIntensity = 0.45 * hot; ctx.hotPt.intensity = 4 * hot;
    ctx.ln.material.opacity = 0.8 * sstep(4.4, 5.0, t);
    ctx.labs.lfr.material.opacity = sstep(1.0, 1.8, t); ctx.labs.loe.material.opacity = sstep(1.2, 2.0, t); ctx.labs.lx.material.opacity = sstep(5.2, 5.9, t);
  }
}

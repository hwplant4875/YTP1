// France 2026: a physical 3D calendar rail. Day tiles (14 Sept -> 8 Nov 2026) stand on a long dark ledge; a second,
// distant tile marks the April 2027 presidential election. Key dates lift forward and their type glows amber.
// 1 unit ~ one tile. North/up irrelevant; the rail runs along +x.
// shots (?shot=name or name:seconds):
//   teaser   (6 s)  cold open: fast lateral slide down the rail, 13 / 17 / 23 / 27 Oct and 5 Nov flick amber in turn.
//   sept17   (5 s)  close, low: the 17 SEPT tile lifts, caption "TEACHERS' STRIKE", 18 SEPT stays dim beside it.
//   oct1     (5 s)  1 OCT pulses amber twice (budget day, most violent day), caption "2027 BUDGET".
//   oct6     (4 s)  locked-off: the 6 OCT tile flies out of the rail toward the lens and lands centre frame.
//   wall     (5 s)  chapter 7 reveal: wide crane over Oct-Nov, a cream NOW line at 11 Oct.
//   oct13    (5 s)  13 OCT lights: "NATIONAL STRIKE · PUPILS + TEACHERS".
//   oct17    (6 s)  17 OCT in a dashed outline ("ONLINE CALL · NOT A UNION DATE"), then a holiday band unrolls 17 Oct -> 2 Nov.
//   oct23_27 (6 s)  pan 23 -> 27 Oct: "CONSULTATION CLOSES", then "BILL AT THE SENATE".
//   nov5     (6 s)  an "END OCT · DECISIONS PROMISED" bracket, then 5 NOV lights: "5 UNION CONFEDERATIONS STRIKE".
//   apr2027  (7 s)  pull back and away: the rail runs off into the dark to a lone APR 2027 tile, "PRESIDENTIAL ELECTION".
const AMBER = 0x3b82f6;   // v2: subject colour instead of the channel amber
import { glow } from './look.js';
import { path, clamp01, sstep, fontsReady, finishPost, ctex, spacedText, timing, label } from './france_lib.js';
const AMBER_HI = 0x60a5fa;
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const START = Date.UTC(2026, 8, 14);          // Mon 14 Sept 2026
const NDAYS = 56;                              // -> Sun 8 Nov
const STEP = 1.06;                             // tile pitch
const MONTH_GAP = 0.7;                         // extra space before the 1st of a month
const DOW = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
const MON = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEPT', 'OCT', 'NOV', 'DEC'];
const APR_X_GAP = 26;                          // empty rail before the Apr 2027 tile

const EVENTS = {     // 'm-d' -> caption lines
  '9-17': ["TEACHERS' STRIKE"], '9-18': ['FIRST BLOCKADE'], '10-1': ['2027 BUDGET'], '10-6': ['NATIONWIDE', 'MARCH'],
  '10-13': ['NATIONAL STRIKE', 'PUPILS + TEACHERS'], '10-17': ['ONLINE CALL', 'NOT A UNION DATE'], '10-23': ['CONSULTATION', 'CLOSES'],
  '10-27': ['BILL AT THE', 'SENATE'], '11-5': ['UNIONS STRIKE', 'TOGETHER'],
};

export async function setup(THREE, renderer, W, H) {
  const { name, k } = timing(6);
  const shot = name || 'wall';
  await fontsReady();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060607);
  scene.fog = new THREE.FogExp2(0x060607, shot === 'apr2027' ? 0.022 : 0.045);
  const camera = new THREE.PerspectiveCamera(30, W / H, 0.05, 400);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // ------------------------------------------------------------------ tiles
  const days = [];
  let x = 0;
  for (let i = 0; i < NDAYS; i++) {
    const d = new Date(START + i * 864e5); const m = d.getUTCMonth(), dd = d.getUTCDate(), dw = d.getUTCDay();
    if (dd === 1 && i > 0) x += MONTH_GAP;
    days.push({ i, m, dd, dw, key: `${m + 1}-${dd}`, x }); x += STEP;
  }
  const railEnd = x;
  const apr = { m: 3, dd: 0, dw: -1, key: 'apr', x: railEnd + APR_X_GAP, apr: true };
  const tileGeo = new RoundedBoxGeometry(0.94, 1.24, 0.14, 4, 0.05);
  const W2 = 384, H2 = 512;
  const faceTex = (d, glowOnly) => ctex(THREE, W2, H2, (g, w, h) => {
    if (!glowOnly) {
      const grd = g.createLinearGradient(0, 0, 0, h); grd.addColorStop(0, d.dw === 0 || d.dw === 6 ? '#1b1b1d' : '#242427'); grd.addColorStop(1, '#151517');
      g.fillStyle = grd; g.fillRect(0, 0, w, h);
      for (let n = 0; n < 1600; n++) { g.fillStyle = `rgba(255,255,255,${Math.random() * 0.025})`; g.fillRect(Math.random() * w, Math.random() * h, 2, 2); }
    } else { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); }
    const ev = EVENTS[d.key];
    const col = glowOnly ? '#ffffff' : (ev ? '#c4bcad' : '#9d968a');
    g.fillStyle = col; g.textAlign = 'center'; g.textBaseline = 'alphabetic';
    if (d.apr) {
      g.font = '700 150px "Inter Display", Inter, sans-serif'; g.fillText('APR', w / 2, 250);
      g.font = '600 64px Inter, sans-serif'; spacedText(g, '2027', w / 2, 330, 14, 'center');
    } else {
      g.font = '600 38px Inter, sans-serif'; spacedText(g, DOW[d.dw], w / 2, 86, 9, 'center');
      g.font = `700 ${ev ? 210 : 200}px "Inter Display", Inter, sans-serif`; g.fillText(String(d.dd), w / 2, 300);
      g.font = '600 34px Inter, sans-serif'; spacedText(g, MON[d.m], w / 2, 360, 9, 'center');
    }
    if (ev || d.apr) {
      g.fillStyle = glowOnly ? '#ffffff' : '#60a5fa'; g.fillRect(w / 2 - 70, 392, 140, 5);
      g.strokeStyle = glowOnly ? 'rgba(255,255,255,0.9)' : 'rgba(96,165,250,0.0)'; g.lineWidth = 8; g.strokeRect(10, 10, w - 20, h - 20);
    }
  });
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1c, roughness: 0.45, metalness: 0.3 });
  const tiles = [];
  const all = [...days, apr];
  for (const d of all) {
    const ev = !!EVENTS[d.key] || d.apr;
    const face = new THREE.MeshStandardMaterial({ map: faceTex(d, false), roughness: 0.5, metalness: 0.1, emissive: new THREE.Color(AMBER_HI), emissiveIntensity: 0,
      emissiveMap: ev ? faceTex(d, true) : null });
    const mats = [bodyMat, bodyMat, bodyMat, bodyMat, face, bodyMat];
    const m = new THREE.Mesh(tileGeo, mats); m.castShadow = m.receiveShadow = true;
    const grp = new THREE.Group(); grp.position.set(d.x, 0.74, 0); grp.add(m); scene.add(grp);
    const halo = glow(THREE, AMBER, 3.2, 0.9); halo.material.opacity = 0; halo.position.set(0, 0, -0.3); grp.add(halo);
    tiles.push({ d, grp, mesh: m, face, halo, ev });
  }
  const byKey = Object.fromEntries(tiles.map(t => [t.d.key, t]));

  // ledge / rail the tiles stand in, plus a far dotted continuation to April
  const ledgeMat = new THREE.MeshStandardMaterial({ color: 0x121214, roughness: 0.35, metalness: 0.5 });
  const ledge = new THREE.Mesh(new THREE.BoxGeometry(railEnd + 1.2, 0.12, 0.7), ledgeMat); ledge.position.set(railEnd / 2 - 0.55, 0.06, 0.05); ledge.receiveShadow = true; scene.add(ledge);
  const lip = new THREE.Mesh(new THREE.BoxGeometry(railEnd + 1.2, 0.02, 0.02), new THREE.MeshBasicMaterial({ color: 0x5d6673 })); lip.position.set(railEnd / 2 - 0.55, 0.125, 0.4); scene.add(lip);
  const aprLedge = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.12, 0.7), ledgeMat); aprLedge.position.set(apr.x, 0.06, 0.05); scene.add(aprLedge);
  const dots = new THREE.Group(); scene.add(dots);
  for (let xx = railEnd + 0.8; xx < apr.x - 1.0; xx += 0.6) { const dd = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.02, 0.02), new THREE.MeshBasicMaterial({ color: 0x7d8796, transparent: true, opacity: 0.8 })); dd.position.set(xx, 0.06, 0.4); dots.add(dd); }
  // floor
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(600, 60), new THREE.MeshStandardMaterial({ color: 0x0c0c0d, roughness: 0.3, metalness: 0.6 }));
  floor.rotation.x = -Math.PI / 2; floor.position.set(40, -0.001, 0); floor.receiveShadow = true; scene.add(floor);
  // month headers on the floor in front of the rail
  for (const d of days) if (d.dd === 1 || d.i === 0) {
    const t = ctex(THREE, 1024, 160, (g, w, h) => { g.fillStyle = '#d3dae4'; g.font = '700 96px Inter, sans-serif'; g.textBaseline = 'middle'; spacedText(g, ['', '', '', '', '', '', '', '', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER'][d.m] + ' 2026', 8, h / 2, 26); });
    const p = new THREE.Mesh(new THREE.PlaneGeometry(4.8, 0.75), new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity: 0.3, depthWrite: false }));
    p.rotation.x = -Math.PI / 2; p.position.set(d.x - 0.45 + 2.4, 0.005, 1.15); scene.add(p);
  }
  // holiday band (17 Oct -> 2 Nov), unrolls along the floor
  const hx0 = byKey['10-17'].d.x - 0.47, hx1 = byKey['11-2'].d.x + 0.47;
  const bandT = ctex(THREE, 4096, 128, (g, w, h) => {
    g.fillStyle = 'rgba(96,165,250,0.10)'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(96,165,250,0.75)'; g.fillRect(0, 0, w, 5); g.fillRect(0, h - 5, w, 5);
    g.fillStyle = 'rgba(191,219,254,0.9)'; g.font = '700 60px Inter, sans-serif'; g.textBaseline = 'middle'; spacedText(g, 'AUTUMN SCHOOL HOLIDAYS', 40, h / 2 + 3, 16);
  });
  const band = new THREE.Mesh(new THREE.PlaneGeometry(1, 0.5), new THREE.MeshBasicMaterial({ map: bandT, transparent: true, depthWrite: false, opacity: 0 }));
  band.rotation.x = -Math.PI / 2; band.position.set(hx0, 0.006, 0.78); band.renderOrder = 3; scene.add(band);
  // dashed outline around 17 Oct (unofficial date)
  const dash = new THREE.Group(); { const t17 = byKey['10-17'];
    const dm = new THREE.MeshBasicMaterial({ color: AMBER_HI, transparent: true, opacity: 0 });
    const per = [[-0.56, -0.72, 0.56, -0.72], [0.56, -0.72, 0.56, 0.72], [0.56, 0.72, -0.56, 0.72], [-0.56, 0.72, -0.56, -0.72]];
    for (const [ax, ay, bx, by] of per) { const len = Math.hypot(bx - ax, by - ay), n = Math.round(len / 0.14);
      for (let q = 0; q < n; q += 2) { const s0 = q / n, s1 = (q + 1) / n; const seg = new THREE.Mesh(new THREE.BoxGeometry(Math.abs(bx - ax) * (s1 - s0) || 0.025, Math.abs(by - ay) * (s1 - s0) || 0.025, 0.01), dm);
        seg.position.set(ax + (bx - ax) * (s0 + s1) / 2, ay + (by - ay) * (s0 + s1) / 2, 0.09); dash.add(seg); } }
    t17.grp.add(dash); dash.userData.m = dm; }
  // END OCT bracket
  const brM = new THREE.MeshBasicMaterial({ color: 0xe9dfca, transparent: true, opacity: 0 });
  const bx0 = byKey['10-26'].d.x - 0.47, bx1 = byKey['10-31'].d.x + 0.47;
  const bracket = new THREE.Group(); scene.add(bracket);
  const bb = (w, h, x, y) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.02), brM); m.position.set(x, y, 0); bracket.add(m); };
  bb(bx1 - bx0, 0.03, (bx0 + bx1) / 2, 1.62); bb(0.03, 0.18, bx0, 1.53); bb(0.03, 0.18, bx1, 1.53);
  // NOW line at 11 Oct / 12 Oct boundary
  const nowX = (byKey['10-11'].d.x + byKey['10-12'].d.x) / 2;
  const nowM = new THREE.MeshBasicMaterial({ color: 0xf2e8d4, transparent: true, opacity: 0 });
  const now = new THREE.Mesh(new THREE.BoxGeometry(0.02, 2.0, 0.02), nowM); now.position.set(nowX, 1.0, 0.45); scene.add(now);

  // captions: in-world cards above the tile, plus a constant-size label for legibility
  const captions = {};
  for (const [key, lines] of Object.entries(EVENTS)) {
    const t = byKey[key]; if (!t) continue;
    const l = label(THREE, lines[0], { size: 0.042, sub: lines[1] ?? null, anchor: 'center', subColor: '#e3e8ef', gap: 0 });
    l.material.opacity = 0; l.position.set(0, 0.9, 0.1); t.grp.add(l); captions[key] = l;
  }
  { const l = label(THREE, 'PRESIDENTIAL ELECTION', { size: 0.032, anchor: 'center', gap: 0 }); l.material.opacity = 0; l.position.set(0, 1.2, 0.1); byKey.apr.grp.add(l); captions.apr = l; }
  { const l = label(THREE, 'END OCT', { size: 0.026, sub: 'DECISIONS PROMISED', anchor: 'center', subColor: '#e3e8ef', gap: 0 }); l.material.opacity = 0; l.position.set((bx0 + bx1) / 2, 2.05, 0); scene.add(l); captions.endoct = l; }
  { const l = label(THREE, 'NOW', { size: 0.022, anchor: 'center', gap: 0, color: '#f2e8d4' }); l.material.opacity = 0; l.position.set(nowX, 2.2, 0.45); scene.add(l); captions.now = l; }

  // ------------------------------------------------------------------ light
  scene.add(new THREE.HemisphereLight(0x8b8f99, 0x0a0908, 0.35));
  const key = new THREE.SpotLight(0xf1f4fa, 0, 40, 0.5, 0.7, 1.2); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0003; scene.add(key, key.target);
  const rim = new THREE.DirectionalLight(0xb7c0cc, 0.5); rim.position.set(-10, 8, -12); scene.add(rim);
  const front = new THREE.DirectionalLight(0xf1f4fa, 0.55); front.position.set(4, 5, 14); scene.add(front);
  const hot = new THREE.PointLight(AMBER, 0, 6, 1.6); scene.add(hot);

  const post = finishPost(THREE, renderer, scene, camera, W, H, { bloom: 0.6, bloomRadius: 0.5, bloomThreshold: 0.7,
    dof: shot === 'apr2027' || shot === 'wall' || shot === 'teaser' ? null : { focus: { oct6: 3.4, sept17: 3.6, oct1: 3.9, oct13: 3.9 }[shot] ?? 5.0, aperture: 0.0016, maxblur: 0.006 } });
  return { THREE, scene, camera, shot, k, tiles, byKey, captions, band, hx0, hx1, dash, brM, nowM, key, hot, post, ...post };
}

// camera keys per shot, relative to a tile's x
const X = (ctx, key) => ctx.byKey[key].d.x;
function cams(ctx) {
  const x = (k) => X(ctx, k);
  return {
    teaser: [[0, [x('10-10') - 1, 1.5, 6.5, x('10-12'), 0.8, 0]], [6, [x('11-6') + 1, 1.4, 6.2, x('11-6') + 1.4, 0.8, 0]]],
    sept17: [[0, [x('9-17') - 1.6, 0.9, 4.2, x('9-17') + 0.2, 0.95, 0]], [5, [x('9-17') - 0.9, 1.05, 3.6, x('9-17') + 0.25, 1.0, 0]]],
    oct1: [[0, [x('10-1') + 2.2, 1.3, 4.6, x('10-1') - 0.1, 1.0, 0]], [5, [x('10-1') + 1.4, 1.2, 3.9, x('10-1') - 0.1, 1.05, 0]]],
    oct6: [[0, [x('10-6'), 1.05, 5.0, x('10-6'), 1.05, 0]], [4, [x('10-6'), 1.05, 4.85, x('10-6'), 1.05, 0]]],
    wall: [[0, [x('10-8'), 1.7, 5.6, x('10-15'), 0.95, 0]], [5, [x('10-11'), 1.9, 7.4, x('10-19'), 0.95, 0]]],
    oct13: [[0, [x('10-11') - 0.4, 1.2, 4.9, x('10-13'), 1.0, 0]], [5, [x('10-12'), 1.15, 4.1, x('10-13'), 1.05, 0]]],
    oct17: [[0, [x('10-14'), 2.4, 6.4, x('10-18'), 0.9, 0]], [3, [x('10-16'), 2.2, 6.2, x('10-20'), 0.9, 0]], [6, [x('10-24'), 4.0, 14.5, x('10-25'), 0.5, 0]]],
    oct23_27: [[0, [x('10-21'), 1.3, 5.2, x('10-23'), 1.0, 0]], [2.0, [x('10-21') + 0.4, 1.3, 5.0, x('10-23') + 0.2, 1.0, 0]], [3.6, [x('10-26'), 1.3, 5.0, x('10-27'), 1.0, 0]], [6, [x('10-26') + 0.3, 1.25, 4.6, x('10-27'), 1.0, 0]]],
    nov5: [[0, [x('10-27'), 2.0, 7.2, x('10-29'), 1.1, 0]], [2.6, [x('10-30'), 1.8, 6.6, x('11-1'), 1.0, 0]], [6, [x('11-4'), 1.3, 5.0, x('11-5'), 1.0, 0]]],
    apr2027: [[0, [x('11-3'), 1.5, 5.5, x('11-6'), 0.9, 0]], [3.0, [x('11-8') + 6, 3.8, 13, x('11-8') + 14, 0.8, 0]], [7, [ctx.byKey.apr.d.x - 7, 2.4, 9.5, ctx.byKey.apr.d.x - 0.5, 0.9, 0]]],
  };
}

export function update(ctx, tt) {
  const { camera, shot, tiles, byKey, captions } = ctx;
  const t = tt / ctx.k;
  ctx._c ??= path(cams(ctx)[shot] ?? cams(ctx).wall);
  const c = ctx._c(t);
  camera.position.set(c[0], c[1], c[2]); camera.lookAt(c[3], c[4], c[5]); ctx.sync();
  ctx.key.position.set(c[3] - 2, 9, 5); ctx.key.target.position.set(c[3], 0.6, 0);
  ctx.key.intensity = 120;

  // default: all tiles at rest
  const lit = {};       // key -> [lift 0..1, glow 0..1]
  const set = (k, lift, g) => { lit[k] = [Math.max(lit[k]?.[0] ?? 0, lift), Math.max(lit[k]?.[1] ?? 0, g)]; };
  const cap = {};
  if (shot === 'teaser') {
    ['10-13', '10-17', '10-23', '10-27', '11-5'].forEach((kk, i) => { const a = 0.9 + i * 0.95; const on = sstep(a, a + 0.25, t); const fl = Math.exp(-Math.max(0, t - a) * 2.5) * on; set(kk, on * 0.35, 0.45 * on + 0.8 * fl); });
  } else if (shot === 'sept17') {
    const on = sstep(1.0, 1.8, t); set('9-17', on, on); cap['9-17'] = sstep(1.6, 2.3, t);
  } else if (shot === 'oct1') {
    const on = sstep(0.8, 1.4, t); const p = 0.55 + 0.45 * Math.max(Math.exp(-Math.max(0, t - 1.0) * 3), Math.exp(-Math.max(0, t - 2.4) * 3) * (t > 2.4 ? 1 : 0));
    set('10-1', on, on * p); cap['10-1'] = sstep(1.4, 2.1, t);
  } else if (shot === 'oct6') {
    const p = sstep(0.4, 1.5, t); set('10-6', 0, 0.3 + 0.7 * sstep(1.2, 1.7, t)); lit['10-6'].fly = p; 
  } else if (shot === 'wall') {
    ctx.nowM.opacity = 0.9 * sstep(1.2, 2.2, t); captions.now.material.opacity = sstep(1.5, 2.4, t);
    ['10-13', '10-17', '10-23', '10-27', '11-5'].forEach((kk, i) => { const a = 2.0 + i * 0.35; set(kk, 0, 0.35 * sstep(a, a + 0.4, t)); });
  } else if (shot === 'oct13') {
    const on = sstep(0.9, 1.6, t); set('10-13', on, on); cap['10-13'] = sstep(1.5, 2.2, t);
  } else if (shot === 'oct17') {
    const on = sstep(0.6, 1.3, t); set('10-17', on * 0.6, on * 0.55); cap['10-17'] = sstep(1.0, 1.7, t) * (1 - sstep(3.0, 3.4, t));
    ctx.dash.userData.m.opacity = on;
    const u = sstep(3.0, 5.0, t); ctx.band.material.opacity = sstep(2.9, 3.2, t) * 0.95; ctx.band.scale.x = Math.max(0.001, (ctx.hx1 - ctx.hx0) * u); ctx.band.position.x = ctx.hx0 + (ctx.hx1 - ctx.hx0) * u / 2;
    ctx.band.material.map.repeat.set(Math.max(0.001, u), 1);
  } else if (shot === 'oct23_27') {
    const a = sstep(0.6, 1.3, t), b = sstep(3.3, 4.0, t); set('10-23', a, a * (1 - 0.5 * b)); set('10-27', b, b); cap['10-23'] = sstep(1.1, 1.8, t) * (1 - sstep(3.0, 3.4, t)); cap['10-27'] = sstep(3.8, 4.5, t);
  } else if (shot === 'nov5') {
    ctx.brM.opacity = 0.9 * sstep(0.5, 1.2, t) * (1 - 0.6 * sstep(3, 4, t)); captions.endoct.material.opacity = sstep(0.8, 1.5, t) * (1 - sstep(2.6, 3.1, t));
    const b = sstep(3.4, 4.1, t); set('11-5', b, b); cap['11-5'] = sstep(3.9, 4.6, t);
  } else if (shot === 'apr2027') {
    const on = sstep(4.6, 5.6, t); set('apr', on, on); cap.apr = sstep(5.3, 6.1, t);
    ['10-13', '10-17', '10-23', '10-27', '11-5'].forEach(kk => set(kk, 0, 0.3));
  }
  let hotPos = null, hotI = 0;
  for (const T of tiles) {
    const [lift, g] = lit[T.d.key] ?? [0, 0];
    const fly = lit[T.d.key]?.fly ?? 0;
    T.grp.position.z = lift * 0.45 + fly * 1.7; T.grp.position.y = 0.74 + lift * 0.08 + fly * 0.31;
    T.grp.rotation.x = -0.08 * lift; T.grp.rotation.y = fly ? (1 - fly) * 0.6 : 0;
    if (fly) T.grp.rotation.z = (1 - fly) * 0.25;
    T.face.emissiveIntensity = (T.ev ? 1.0 : 0) * g;
    T.halo.material.opacity = 0.4 * g; T.halo.scale.setScalar(2.4 + 0.4 * g);
    if (g > hotI) { hotI = g; hotPos = T.grp.position.clone(); }
  }
  ctx.hot.intensity = 2.2 * hotI; if (hotPos) ctx.hot.position.set(hotPos.x, 2.2, hotPos.z + 1.6);
  for (const [kk, l] of Object.entries(captions)) if (!['endoct', 'now'].includes(kk)) l.material.opacity = cap[kk] ?? 0;
  if (shot !== 'nov5') { ctx.brM.opacity = 0; captions.endoct.material.opacity = 0; }
  if (shot !== 'wall') { ctx.nowM.opacity = 0; captions.now.material.opacity = 0; }
  if (shot !== 'oct17') ctx.dash.userData.m.opacity = 0;
}

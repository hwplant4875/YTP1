// RageStyles #5 — "RONNIE'S LIGHT WEIGHT IN REAL LIFE"
import { W, H, clamp, ease, prog, env, impulse, shake, lerp, noise1 } from '/engine/fx.js';
import { loadVO, groups, drawGroups, srcTime, placeholder, fmt, cueList } from '/engine/kit.js';
import { makeStage, fridge, barbell, stands, mat, THREE } from '/engine/stage3d.js';

// line starts (timeline seconds)
const T = { l1: 2.05, l2: 5.25, l3: 9.0, l4: 11.25, l5: 14.5, l6: 19.35, l7: 20.9 };
export const duration = 23.6;
const RED = '#ff2a2a', YEL = '#FFD400';

let VO, caps = [], clips = {}, A, B, imgs = {};
const fr = [];
let bar, car, sled, carBox;

export async function setup(R) {
  VO = await loadVO('s05/vo', ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7']);
  const hl = { l1: ['EIGHT', 'HUNDRED', 'POUNDS'], l2: ['THREE', 'REFRIGERATORS', 'TWO'], l3: ['TWENTYTHREE', 'HUNDRED'], l4: ['CAR', 'EIGHT'],
    l5: ['MORBIDLY', 'OBESE', 'BMI'], l6: ['MUSCLE'], l7: ['EIGHT', 'OLYMPIAS'] };
  for (const k of Object.keys(T)) caps.push(...groups(VO[k].fw, T[k], { hl: hl[k] || [] }));
  for (const [k, dir] of Object.entries({ hook: 'clips/s05_hook', squat: 'clips/s05_squat', press: 'clips/s05_press', stage: 'clips/s05_stage' })) {
    try { clips[k] = await R.clip(dir); } catch (e) { clips[k] = null; }
  }

  // --- 3D stage A: barbell + fridges ---
  A = await makeStage({ hdri: 'studio_small_09', envIntensity: .9, bloom: .28 });
  // softbox reflections for the stainless steel (off camera)
  const sb = new THREE.Mesh(new THREE.PlaneGeometry(6, 2.2), new THREE.MeshBasicMaterial({ color: 0xffffff }));
  sb.position.set(0, 3.2, 6); sb.lookAt(0, 1, 0); sb.material.color.setScalar(3.2); A.scene.add(sb);
  bar = barbell(); bar.position.set(0, 1.36, -1.6); A.scene.add(bar);
  const st = stands(1.2, 1.45); st.position.z = -1.6; A.scene.add(st);
  for (let i = 0; i < 3; i++) { const f = fridge(); f.position.set((i - 1) * .84, 30, .6); f.rotation.y = (i - 1) * -.04; A.scene.add(f); fr.push(f); }

  // --- 3D stage B: 45° leg press + car ---
  B = await makeStage({ hdri: 'studio_small_03', envIntensity: .8, bloom: .3 });
  const sb2 = sb.clone(); sb2.material = sb.material.clone(); B.scene.add(sb2);
  const lp = new THREE.Group(); B.scene.add(lp);
  const frameM = mat.paint(0x1b1b1e), redM = mat.paint(0xc01818);
  const ang = Math.PI / 4, dir = new THREE.Vector3(0, Math.sin(ang), -Math.cos(ang));
  for (const x of [-.75, .75]) {   // rails
    const rail = new THREE.Mesh(new THREE.BoxGeometry(.09, .09, 4.2), frameM); rail.position.set(x, 1.5, -1.3); rail.rotation.x = ang; lp.add(rail);
    const leg = new THREE.Mesh(new THREE.BoxGeometry(.1, 2.9, .1), frameM); leg.position.set(x, 1.45, -2.75); lp.add(leg);
    const foot = new THREE.Mesh(new THREE.BoxGeometry(.14, .06, 4.6), frameM); foot.position.set(x, .03, -1.1); lp.add(foot);
  }
  const seat = new THREE.Mesh(new THREE.BoxGeometry(.8, .12, .9), mat.rubber()); seat.position.set(0, .5, 1.25); seat.rotation.x = -.35; lp.add(seat);
  const back = new THREE.Mesh(new THREE.BoxGeometry(.8, .9, .12), mat.rubber()); back.position.set(0, .82, 1.75); back.rotation.x = -.5; lp.add(back);
  sled = new THREE.Group(); lp.add(sled);
  const plateM = new THREE.Mesh(new THREE.BoxGeometry(1.9, .08, 2.4), frameM); sled.add(plateM);
  const foot = new THREE.Mesh(new THREE.BoxGeometry(1.0, .7, .06), redM); foot.position.set(0, -.38, 1.15); sled.add(foot);
  sled.rotation.x = ang;
  sled.userData.base = new THREE.Vector3(0, 1.25, -.95);
  car = await B.load('covered_car');
  carBox = new THREE.Box3().setFromObject(car); const cs = carBox.getSize(new THREE.Vector3());
  const k = 2.35 / Math.max(cs.x, cs.z); car.scale.setScalar(k);
  carBox = new THREE.Box3().setFromObject(car);
  const carWrap = new THREE.Group(); carWrap.add(car);
  const c0 = carBox.getCenter(new THREE.Vector3()); car.position.set(-c0.x, -carBox.min.y, -c0.z);
  if (cs.x > cs.z) car.rotation.y = Math.PI / 2;   // nose up the slope
  sled.add(carWrap); carWrap.position.y = .04; sled.userData.car = carWrap;
  B.pool.position.set(1.5, 7, 1); B.pool.target.position.set(0, 1.6, -1.2); B.pool.intensity = 90; B.key.intensity = 3.4;
  for (const m of lp.children) if (m.geometry && m.geometry.parameters && m.geometry.parameters.depth === 4.2) m.material = redM;
  [A, B].forEach(S => S.scene.traverse(o => { if (o.isMesh) { o.castShadow = o.receiveShadow = true; } }));

  imgs.trophy = null;
}

// ---------- audio cues ----------
export function cues() {
  const c = cueList(), a = c.add;
  a('clips/s05_hook/audio.wav', 0, -1, { norm: true, fade: .08, len: 2.05 });
  a('sfx:flash', 0, -8); a('synth:sub', 0.02, -2);
  a('sfx:tape_stop', 1.95, -8); a('sfx:sub_hit', 2.05, -4); a('sfx:glitch', 2.02, -12);
  for (const [k, t] of Object.entries(T)) a(`/home/user/rs_work/s05/vo/${k}_f.wav`, t, 0, { duck: true, norm: true });
  a('sfx:whoosh_deep', 3.2, -6); a('sfx:braam', 3.55, -4); a('synth:sub', 3.58, -3);
  a('sfx:whoosh_fast', 5.1, -8);
  [5.64, 6.02, 6.4].forEach((t, i) => { a('sfx:thud_heavy', t, -2); a('sfx:impact_metal', t, -10 - i); a('synth:sub', t, -6); });
  a('sfx:snap_zoom', 7.42, -8); a('sfx:sub_hit', 7.5, -6); a('sfx:impact_metal', 8.15, -9);
  a('sfx:whoosh_fast', 8.85, -6); a('sfx:riser', 9.4, -14, { len: 1.5 });
  for (let i = 0; i < 12; i++) a('sfx:tick', 9.96 + i * .075, -16);
  a('sfx:sub_hit', 10.9, -4); a('sfx:whoosh_deep', 11.1, -7);
  a('sfx:car_land', 11.62, -1); a('synth:sub', 11.79, -2); a('sfx:crowd_ooh', 11.95, -14);
  for (let i = 0; i < 8; i++) a('sfx:chain_rattle', 12.46 + i * .23, -12);
  a('sfx:ding', 14.28, -12); a('sfx:swipe', 14.45, -6); a('sfx:pop', 14.55, -10); a('sfx:pop', 15.82, -10);
  a('sfx:swipe', 17.3, -6); a('sfx:riser', 17.6, -12, { len: 1.0 }); a('sfx:glitch', 18.6, -4); a('sfx:sub_hit', 18.62, -3);
  a('sfx:record_scratch', 19.3, -6); a('sfx:whoosh_fast', 19.3, -8); a('sfx:flash', 20.15, -6); a('sfx:braam', 20.17, -5); a('synth:sub', 20.17, -2);
  for (let i = 0; i < 8; i++) a('sfx:pop', 20.9 + i * .09, -11 + i * .4);
  a('sfx:heartbeat', 22.4, -6); a('sfx:riser', 22.2, -10, { len: 1.35 });
  return c.list.filter(x => !x.file.includes('record_scratch'));
}

// ---------- helpers ----------
const caption = (R, t, o = {}) => drawGroups(R, caps, t, { y: H * .655, size: 92, ...o });
function dust(R, x, y, t, t0, n = 26, spread = 260) {
  const p = t - t0; if (p < 0 || p > 1.2) return;
  const g = R.g; g.save(); g.globalCompositeOperation = 'screen';
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI + noise1(i * 3.1) * .2, sp = (.4 + .6 * Math.abs(noise1(i * 7.7))) * spread;
    const r = ease.out(clamp(p / 1.0)) * sp, px = x + Math.cos(a) * r * (i % 2 ? 1 : -1), py = y - Math.abs(Math.sin(a)) * r * .25;
    const al = (1 - clamp(p / 1.2)) * .22, sz = 30 + 70 * p;
    const gr = g.createRadialGradient(px, py, 0, px, py, sz); gr.addColorStop(0, `rgba(200,195,185,${al})`); gr.addColorStop(1, 'rgba(200,195,185,0)');
    g.fillStyle = gr; g.fillRect(px - sz, py - sz, sz * 2, sz * 2);
  }
  g.restore();
}
const toScreen = (S, v) => { const p = v.clone().project(S.camera); return [(p.x + 1) / 2 * W, (1 - p.y) / 2 * H]; };

// big stat number with tag, e.g. 800 LBS
function bigStat(R, num, unit, x, y, t, t0, o = {}) {
  const p = clamp((t - t0) / .22); if (p <= 0) return;
  const sc = 1 + 1.6 * Math.pow(1 - ease.outExpo(p), 2) - 0.0 * p;
  const { size = 330, sub = null } = o;
  R.text(num, x, y, { size, font: 'Anton', grad: [[0, '#ffffff'], [.6, '#f0f0f0'], [1, '#b9b9b9']], glow: 50, glowColor: 'rgba(0,0,0,.9)', scale: sc, alpha: Math.min(1, p * 2) });
  const uw = R.measure(unit, size * .3, 'Anton') + 44;
  const up = clamp((t - t0 - .12) / .2); if (up > 0) {
    R.box(x - uw / 2, y + size * .5, uw, size * .36, { fill: RED, r: 10, alpha: up, glow: 30, glowColor: 'rgba(255,0,0,.5)' });
    R.text(unit, x, y + size * .5 + size * .19, { size: size * .3, font: 'Anton', color: '#fff', alpha: up, track: 4 });
  }
  if (sub) R.text(sub, x, y - size * .72, { size: 58, font: 'Mont', weight: 800, color: '#fff', alpha: clamp((t - t0 - .2) / .2), track: 6, glow: 20 });
}
// kicker label at the top (source / context)
function kicker(R, str, t, t0, t1) {
  const a = env(t, t0, .2, t1 - t0 - .4, .2); if (a <= 0) return;
  const w = R.measure(str, 40, 'Mont', 800, 4) + 60;
  R.box(W / 2 - w / 2, 250, w, 74, { fill: 'rgba(10,10,10,.55)', stroke: 'rgba(255,255,255,.25)', sw: 2, r: 37, alpha: a });
  R.text(str, W / 2, 288, { size: 40, font: 'Mont', weight: 800, color: '#fff', alpha: a, track: 4 });
}

async function footage(R, name, t, start, o = {}) {
  const c = clips[name];
  if (!c) { placeholder(R, name.toUpperCase() + ' FOOTAGE', t); return; }
  const st = srcTime(t, start, o.time || {});
  const img = await c.at(st);
  const sh = o.shake ? shake(t, o.shake) : { x: 0, y: 0, r: 0 };
  R.draw(img, { zoom: (o.zoom || 1), fx: o.fx ?? .5, fy: o.fy ?? .5, x: sh.x / W, y: sh.y / H, rot: sh.r, filter: o.filter || 'contrast(1.08) saturate(1.1)' });
}

// ---------- shots ----------
async function shotHook(R, t) {   // 0 – 2.05: LIGHT WEIGHT BABY
  const punch = 1.18 - .18 * ease.outExpo(clamp(t / .35)) + .06 * prog(t, .35, 1.7, ease.inOut);
  await footage(R, 'hook', t, 0, { zoom: punch, shake: 6 + 14 * impulse(t, 0, 5) });
  R.flash(impulse(t, 0, 7) * .9);
  R.flash(.18 * impulse(t, .9, 6));
  R.text('LIGHT WEIGHT', W / 2, H * .66, { size: 150, font: 'Anton', color: '#fff', stroke: '#000', sw: 22, glow: 30, scale: .7 + .3 * ease.outBack(clamp((t - .15) / .2), 2.4), alpha: clamp((t - .15) * 8) });
  R.text('BABY!', W / 2, H * .66 + 160, { size: 170, font: 'Anton', color: YEL, stroke: '#000', sw: 24, glow: 30, scale: .7 + .3 * ease.outBack(clamp((t - .68) / .2), 2.6), alpha: clamp((t - .68) * 8), rot: -.03 });
}
async function shotFreeze(R, t) {   // 2.05 – 3.3: freeze + desat + "THAT LIGHT WEIGHT…"
  const c = clips.hook; const last = c ? (c.n - 1) / c.fps : 0;
  const z = 1.0 + .08 * prog(t, 2.05, 1.25, ease.out);
  if (c) R.draw(await c.at(Math.min(2.03, last)), { zoom: z, filter: 'grayscale(1) contrast(1.35) brightness(.7)' }); else placeholder(R, 'HOOK FREEZE', t);
  R.flash(.35, RED, 'multiply'); R.flash(.12, RED, 'screen');
  R.rgbSplit(10 * impulse(t, 2.05, 5));
  R.flash(impulse(t, 2.05, 9) * .7);
  caption(R, t);
}
async function shotBar(R, t) {   // 3.3 – 5.25: barbell hero, 800 LBS slam on "eight"
  const S = A, p = prog(t, 3.3, 1.95, ease.inOut);
  const imp = impulse(t, 3.58, 6);
  const sh = shake(t, .025 * imp + .002, 20);
  S.camera.fov = 30; S.camera.updateProjectionMatrix();
  S.camera.position.set(lerp(2.0, 2.4, p) + sh.x, lerp(1.0, 1.15, p) + sh.y, lerp(-.5, 1.1, p));
  S.camera.lookAt(lerp(.95, .25, p), lerp(1.55, 1.62, p), -1.6);
  bar.rotation.x = 0; fr.forEach(f => f.visible = false);
  R.g.drawImage(S.render(), 0, 0);
  R.zoomBlur(.06 * imp);
  R.flash(imp * .5);
  bigStat(R, '800', 'LBS', W / 2, H * .2, t, 3.58, { sub: 'THE "LIGHT WEIGHT"' });
  caption(R, t);
}
async function shotFridges(R, t) {   // 5.25 – 7.45: three fridges drop
  const S = A; fr.forEach(f => f.visible = true);
  const lands = [5.64, 6.02, 6.4];
  let imp = 0; lands.forEach(l => imp += impulse(t, l, 7));
  const p = prog(t, 5.25, 2.2, ease.inOut);
  const sh = shake(t, .03 * imp, 22);
  S.camera.fov = 36; S.camera.updateProjectionMatrix();
  S.camera.position.set(lerp(-1.6, 1.4, p) + sh.x, lerp(1.4, 1.7, p) + sh.y, lerp(6.6, 6.0, p));
  S.camera.lookAt(0, 1.75, .4);
  fr.forEach((f, i) => {
    const l = lands[i], fall = .34, h0 = 5.5;
    if (t < l - fall) { f.position.y = 30; return; }
    if (t < l) { const q = (t - (l - fall)) / fall; f.position.y = h0 * (1 - q * q); f.scale.set(1, 1.04, 1); }
    else { const q = t - l; f.position.y = Math.max(0, .06 * Math.exp(-q * 9) * Math.abs(Math.sin(q * 26))); const sq = .07 * Math.exp(-q * 12) * Math.cos(q * 34); f.scale.set(1 + sq * .5, 1 - sq, 1 + sq * .5); }
  });
  bar.rotation.x = 0;
  R.g.drawImage(S.render(), 0, 0);
  // motion streak on falling fridges
  lands.forEach((l, i) => { if (t > l - .34 && t < l) R.motionBlur(0, 60, 6); });
  lands.forEach((l, i) => { const [x, y] = toScreen(S, new THREE.Vector3((i - 1) * .84, 0, .95)); dust(R, x, y, t, l); });
  R.flash(imp * .18);
  // counter
  const cnt = lands.filter(l => t >= l).length;
  if (cnt) {
    const last = lands[cnt - 1];
    bigStat(R, fmt(270 * cnt), 'LBS', W / 2, H * .15, t, last, { size: 220 });
    // fridge pips
    for (let i = 0; i < 3; i++) {
      const on = i < cnt, x = W / 2 + (i - 1) * 90, y = H * .15 + 200;
      R.box(x - 30, y, 60, 90, { fill: on ? '#e8e8e8' : 'rgba(255,255,255,.12)', r: 8, alpha: clamp((t - 5.3) * 4) });
      if (on) R.box(x - 30, y + 30, 60, 4, { fill: '#333', r: 0 });
    }
  }
  R.text('1 FRIDGE ≈ 270 LBS', W / 2, H * .15 + 335, { size: 40, font: 'Mont', weight: 600, color: 'rgba(255,255,255,.7)', alpha: clamp((t - 5.7) * 3), track: 6 });
  caption(R, t);
}
async function shotSquat(R, t) {   // 7.45 – 8.9: real squat, rep counter
  const z = 1.25 - .15 * ease.outExpo(clamp((t - 7.45) / .3));
  await footage(R, 'squat', t, 7.45, { zoom: z, shake: 3 + 10 * impulse(t, 7.5, 6), time: { speed: .85 } });
  R.flash(impulse(t, 7.45, 9) * .8);
  R.vignette(.6);
  const reps = t >= 8.12 ? 2 : t >= 7.92 ? 1 : 0;
  if (reps) {
    R.box(W - 330, 380, 260, 150, { fill: 'rgba(0,0,0,.55)', r: 20, stroke: RED, sw: 4 });
    R.text('REPS', W - 200, 418, { size: 34, font: 'Mont', weight: 800, color: '#bbb', track: 6 });
    R.text(`${reps}`, W - 200, 485, { size: 90, font: 'Anton', color: '#fff', scale: 1 + .4 * impulse(t, reps === 1 ? 7.92 : 8.12, 10) });
  }
  kicker(R, '800 LBS SQUAT', t, 7.5, 8.9);
  caption(R, t);
}
async function shotPress(R, t) {   // 8.9 – 11.2: leg press footage + 2,300 counter
  const z = 1.1 + .08 * prog(t, 8.9, 2.3);
  await footage(R, 'press', t, 8.9, { zoom: z, shake: 3 + 6 * impulse(t, 10.9, 6) });
  R.motionBlur(-220 * impulse(t, 8.9, 10), 0, 8);
  R.vignette(.6);
  const n = 2300 * ease.out(clamp((t - 9.96) / .92));
  if (t >= 9.96) bigStat(R, fmt(n), 'LBS', W / 2, H * .24, t, 9.96, { size: 250, sub: 'LEG PRESS' });
  R.flash(impulse(t, 10.9, 8) * .5);
  caption(R, t);
}
async function shotCar(R, t) {   // 11.2 – 14.45: car lands on leg press sled, 8 reps
  const S = B; const land = 11.79;
  const imp = impulse(t, land, 6);
  const p = prog(t, 11.2, 3.25, ease.inOut);
  const sh = shake(t, .04 * imp, 20);
  S.camera.fov = 38; S.camera.updateProjectionMatrix();
  S.camera.position.set(lerp(7.8, 7.0, p) + sh.x, lerp(3.0, 3.3, p) + sh.y, lerp(3.2, 2.0, p));
  S.camera.lookAt(0, 2.3, -1.0);
  // reps: sled travels 0.55 m along the rail, 8 reps from 12.46
  let travel = 0; const r0 = 12.46, per = .23;
  if (t > r0 && t < r0 + per * 8) { const q = ((t - r0) % per) / per; travel = .55 * Math.sin(q * Math.PI); }
  const base = sled.userData.base, dir = new THREE.Vector3(0, Math.SQRT1_2, -Math.SQRT1_2);
  sled.position.copy(base).addScaledVector(dir, travel);
  const cw = sled.userData.car;
  if (t < land - .4) cw.position.y = 12; else if (t < land) { const q = (t - (land - .4)) / .4; cw.position.y = .04 + 6 * (1 - q * q); }
  else { const q = t - land; cw.position.y = .04 + .08 * Math.exp(-q * 8) * Math.abs(Math.sin(q * 22)); }
  R.g.drawImage(S.render(), 0, 0);
  if (t > land - .4 && t < land) R.motionBlur(0, 80, 6);
  const [dx, dy] = toScreen(S, new THREE.Vector3(0, 1.5, -1.2)); dust(R, dx, dy, t, land, 30, 300);
  R.flash(imp * .35);
  if (t >= land) bigStat(R, 'A WHOLE CAR', '2,300 LBS', W / 2, H * .14, t, land, { size: 170 });
  const reps = Math.min(8, Math.floor(Math.max(0, t - r0) / per + (t > r0 ? 1 : 0)));
  if (t > r0) {
    R.box(W / 2 - 170, H * .14 + 200, 340, 130, { fill: 'rgba(0,0,0,.55)', r: 20, stroke: RED, sw: 4 });
    R.text(`× ${reps}`, W / 2, H * .14 + 267, { size: 96, font: 'Anton', color: reps === 8 ? YEL : '#fff', scale: 1 + .25 * impulse(t, r0 + (reps - 1) * per, 12) });
  }
  caption(R, t);
}
async function shotBMI(R, t) {   // 14.45 – 19.35: BMI gauge graphic
  const g = R.g; const t0 = 14.45;
  // backdrop: dark studio gradient + soft red glow
  const gr = g.createRadialGradient(W / 2, H * .42, 50, W / 2, H * .42, H * .7); gr.addColorStop(0, '#202024'); gr.addColorStop(1, '#050506');
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
  // faint grid
  g.save(); g.globalAlpha = .06; g.strokeStyle = '#fff'; g.lineWidth = 1;
  const off = (t * 20) % 60; for (let x = -60; x < W + 60; x += 60) { g.beginPath(); g.moveTo(x + off, 0); g.lineTo(x + off, H); g.stroke(); }
  for (let y = 0; y < H; y += 60) { g.beginPath(); g.moveTo(0, y + off); g.lineTo(W, y + off); g.stroke(); } g.restore();
  // stat cards
  const card = (lbl, val, x, y, ta) => {
    const a = clamp((t - ta) / .25); if (a <= 0) return; const dy = (1 - ease.outBack(a)) * 60;
    R.box(x - 220, y - 95 + dy, 440, 190, { fill: 'rgba(255,255,255,.06)', stroke: 'rgba(255,255,255,.18)', sw: 2, r: 26, alpha: a });
    R.text(lbl, x, y - 45 + dy, { size: 34, font: 'Mont', weight: 800, color: '#9a9aa0', track: 6, alpha: a });
    R.text(val, x, y + 30 + dy, { size: 100, font: 'Anton', color: '#fff', alpha: a });
  };
  card('HEIGHT', `5'11"`, W / 2 - 250, 470, t0 + .03);
  card('WEIGHT', '~300 LBS', W / 2 + 250, 470, t0 + 1.33);
  // gauge
  const ga = clamp((t - (t0 + 2.85)) / .3); if (ga > 0) {
    const cx = W / 2, cy = 1130, r = 360, a0 = Math.PI * 1.0, a1 = Math.PI * 2.0;
    const zones = [[16, 18.5, '#3aa0ff', 'UNDER'], [18.5, 25, '#27d17f', 'NORMAL'], [25, 30, '#ffc21a', 'OVER'], [30, 35, '#ff7a1a', 'OBESE'], [35, 45, '#ff2a2a', 'MORBID']];
    const toA = v => a0 + (clamp((v - 16) / (45 - 16))) * (a1 - a0);
    g.save(); g.globalAlpha = ga; g.translate(0, (1 - ease.out(ga)) * 80);
    g.lineWidth = 64; g.lineCap = 'butt';
    zones.forEach(([s, e, col, lbl]) => {
      g.beginPath(); g.arc(cx, cy, r, toA(s) + .012, toA(e) - .012); g.strokeStyle = col; g.shadowColor = col; g.shadowBlur = 18; g.stroke(); g.shadowBlur = 0;
      const m = (toA(s) + toA(e)) / 2; R.text(lbl, cx + Math.cos(m) * (r + 78), cy + Math.sin(m) * (r + 78), { size: 30, font: 'Mont', weight: 800, color: col, rot: m + Math.PI / 2, track: 3 });
    });
    // needle: swings to 41.3 on "morbidly"
    const sw = ease.outElastic(clamp((t - (t0 + 3.62)) / .9));
    const v = lerp(22, 41.3, sw) + (t > t0 + 4.6 ? noise1(t * 30) * .3 : 0);
    const na = toA(v);
    g.save(); g.translate(cx, cy); g.rotate(na); g.shadowColor = 'rgba(0,0,0,.8)'; g.shadowBlur = 20;
    g.beginPath(); g.moveTo(0, -14); g.lineTo(r - 20, 0); g.lineTo(0, 14); g.closePath(); g.fillStyle = '#fff'; g.fill(); g.restore();
    g.beginPath(); g.arc(cx, cy, 34, 0, Math.PI * 2); g.fillStyle = '#fff'; g.fill(); g.beginPath(); g.arc(cx, cy, 16, 0, Math.PI * 2); g.fillStyle = '#111'; g.fill();
    g.restore();
    R.text('BMI', cx, cy + 120, { size: 44, font: 'Mont', weight: 800, color: '#9a9aa0', track: 10, alpha: ga });
    R.text(v.toFixed(1), cx, cy + 210, { size: 130, font: 'Anton', color: v > 35 ? RED : '#fff', alpha: ga });
  }
  // stamp
  const sa = clamp((t - (t0 + 4.12)) / .14);
  if (sa > 0) {
    const sc = 1.8 - .8 * ease.out(sa);
    g.save(); g.translate(W / 2, 1600); g.rotate(-.09); g.scale(sc, sc); g.globalAlpha = sa;
    g.lineWidth = 10; g.strokeStyle = RED; g.strokeRect(-380, -85, 760, 170);
    g.restore();
    R.text('MORBIDLY OBESE', W / 2, 1600, { size: 110, font: 'Anton', color: RED, rot: -.09, scale: sc, alpha: sa, track: 2 });
  }
  R.rgbSplit(14 * impulse(t, t0 + 4.12, 7)); R.flash(impulse(t, t0 + 4.12, 10) * .4, RED);
  R.vignette(.6);
}
async function shotMuscle(R, t) {   // 19.35 – 20.9: EXCEPT IT WAS ALL MUSCLE
  const hit = 20.17;
  const z = 1.05 + .05 * prog(t, 19.35, .8) + .22 * (1 - Math.exp(-Math.max(0, t - hit) * 10)) - .1 * prog(t, hit + .2, .6, ease.out);
  await footage(R, 'stage', t, 19.35, { zoom: z, shake: 2 + 16 * impulse(t, hit, 5), fy: .4, filter: `contrast(1.15) saturate(1.15) brightness(${1 + .4 * impulse(t, hit, 6)})` });
  R.zoomBlur(.1 * impulse(t, hit, 7));
  R.flash(impulse(t, hit, 8) * .85); R.flash(impulse(t, 19.35, 12) * .6);
  R.bloom(.25 + .4 * impulse(t, hit, 5));
  R.vignette(.55);
  caption(R, t, { size: 104 });
}
async function shotTrophies(R, t) {   // 20.9 – 23.6: 8 trophies + "and he still called it..."
  const c = clips.stage;
  if (c) R.draw(await c.at(srcTime(t, 19.35, {})), { zoom: 1.25, filter: 'blur(14px) brightness(.38) saturate(.7)' }); else placeholder(R, 'STAGE BG', t);
  R.flash(.25, RED, 'multiply');
  const years = [1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005];
  years.forEach((y, i) => {
    const ta = 20.9 + i * .09, a = clamp((t - ta) / .18); if (a <= 0) return;
    const col = i % 4, row = Math.floor(i / 4), x = W / 2 + (col - 1.5) * 225, yy = 640 + row * 330;
    const s = .6 + .4 * ease.outBack(a, 2.2);
    trophy(R, x, yy, s, a, t);
    R.text(String(y), x, yy + 135, { size: 42, font: 'Anton', color: '#e9c46a', alpha: a, track: 2 });
  });
  const ta = clamp((t - 21.0) / .25);
  R.text('8× MR. OLYMPIA', W / 2, 420, { size: 120, font: 'Anton', grad: [[0, '#fff1c1'], [.5, '#f2c14e'], [1, '#a8741a']], glow: 40, alpha: ta, scale: .8 + .2 * ease.outBack(ta) });
  R.leak(.35 * ta, t);
  // fade to the loop point
  const fo = prog(t, 23.25, .35);
  caption(R, t, { y: H * .68 });
  R.fill('#000', fo * .85);
}
function trophy(R, x, y, s, a, t) {
  const g = R.g; g.save(); g.translate(x, y); g.scale(s, s); g.globalAlpha = a;
  const gold = g.createLinearGradient(-70, -110, 70, 110); gold.addColorStop(0, '#fff3c4'); gold.addColorStop(.35, '#f2c14e'); gold.addColorStop(.7, '#b8801f'); gold.addColorStop(1, '#ffe08a');
  g.shadowColor = 'rgba(255,190,60,.6)'; g.shadowBlur = 30; g.fillStyle = gold;
  // cup
  g.beginPath(); g.moveTo(-62, -100); g.lineTo(62, -100); g.bezierCurveTo(62, -20, 30, 10, 12, 18); g.lineTo(12, 50); g.lineTo(-12, 50); g.lineTo(-12, 18); g.bezierCurveTo(-30, 10, -62, -20, -62, -100); g.fill();
  // handles
  g.lineWidth = 12; g.strokeStyle = gold; g.shadowBlur = 0;
  g.beginPath(); g.arc(-62, -62, 30, Math.PI * .5, Math.PI * 1.5); g.stroke(); g.beginPath(); g.arc(62, -62, 30, -Math.PI * .5, Math.PI * .5); g.stroke();
  // base
  g.fillStyle = gold; g.fillRect(-40, 50, 80, 14); g.fillStyle = '#2a1d08'; g.fillRect(-52, 64, 104, 36); g.fillStyle = gold; g.fillRect(-52, 64, 104, 5);
  // shine sweep
  const sx = ((t * 1.3) % 2) * 260 - 130; const sh = g.createLinearGradient(sx - 30, 0, sx + 30, 0); sh.addColorStop(0, 'rgba(255,255,255,0)'); sh.addColorStop(.5, 'rgba(255,255,255,.55)'); sh.addColorStop(1, 'rgba(255,255,255,0)');
  g.globalCompositeOperation = 'source-atop'; g.fillStyle = sh; g.fillRect(-90, -110, 180, 220);
  g.restore();
}

export async function draw(R, t) {
  if (t < 2.05) await shotHook(R, t);
  else if (t < 3.3) await shotFreeze(R, t);
  else if (t < 5.25) await shotBar(R, t);
  else if (t < 7.45) await shotFridges(R, t);
  else if (t < 8.9) await shotSquat(R, t);
  else if (t < 11.2) await shotPress(R, t);
  else if (t < 14.45) await shotCar(R, t);
  else if (t < 19.35) await shotBMI(R, t);
  else if (t < 20.9) await shotMuscle(R, t);
  else await shotTrophies(R, t);
  // global finish
  R.grain(.05, t);
  // transition flashes at cuts
  for (const c of [3.3, 5.25, 11.2, 14.45]) R.flash(impulse(t, c, 14) * .55);
  // channel bug
}

// RageStyles #3 — "SCALE SHOCK": normal guy → bodybuilder → strongmen → giant
import { W, H, clamp, ease, prog, env, impulse, shake, lerp } from '/engine/fx.js';
import { loadVO, groups, drawGroups, srcTime, placeholder, cueList } from '/engine/kit.js';
import { makeStage, THREE } from '/engine/stage3d.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';

const T = { l1: .15, l2: 2.6, l3: 5.3, l4: 6.65, l5: 8.5, l6: 11.6, l7: 14.7, l8: 18.9, l9: 21.35 };
export const duration = 23.6;
const RED = '#ff2a2a', YEL = '#FFD400';
const FT = .3048;
// people: height (m), bulk, name, stat line, photo, entrance time
const P = [
  { h: 1.753, b: 1.0, name: 'AVERAGE GUY', stat: `5'9"`, sub: '~200 LBS', photo: null, t: 6.65, x: 0 },
  { h: 1.753, b: 1.32, name: 'JAY CUTLER', stat: `5'9"`, sub: '270 LBS ON STAGE', photo: 'jay_2014_loaded.jpg', fx: .36, fy: .25, t: 8.5, x: 0.95 },
  { h: 2.03, b: 1.42, name: 'BRIAN SHAW', stat: `6'8"`, sub: '400 LBS', photo: 'shaw_ac2017.jpg', fx: .5, fy: .22, t: 11.6, x: 1.9 },
  { h: 2.06, b: 1.5, name: 'HAFTHOR BJORNSSON', stat: `6'9"`, sub: '460 LBS PEAK', photo: 'thor_ac2017b.jpg', fx: .5, fy: .2, t: 14.7, x: 2.85 },
  { h: 2.18, b: 1.2, name: 'OLIVIER RICHTERS', stat: `7'2"`, sub: 'THE DUTCH GIANT', photo: null, t: 18.9, x: 3.8 },
];
let VO, caps = [], clips = {}, imgs = {}, S, mixers = [], figs = [], ruler = [];

export async function setup(R) {
  VO = await loadVO('s03/vo', Object.keys(T));
  const hl = { l1: ['SMALL', 'OLYMPIA'], l2: ['DWARFS'], l3: ['LINE'], l4: ['FIVENINE'], l5: ['TWOSEVENTY'], l6: ['SIXEIGHT', 'FOUR', 'HUNDRED'],
    l7: ['SIXNINE', 'FOURSIXTY'], l8: ['SEVENFOOTTWO', 'GIANT'], l9: ['NOT'] };
  for (const k of Object.keys(T)) caps.push(...groups(VO[k].fw, T[k], { hl: hl[k] || [] }));
  try { clips.shaw = await R.clip('clips/s03_shaw'); } catch (e) { clips.shaw = null; }
  for (const f of ['jay_2007_handshake.jpg', ...P.filter(p => p.photo).map(p => p.photo)]) imgs[f] = await R.image(`/@work/photos/${f}`);

  S = await makeStage({ hdri: 'studio_small_09', envIntensity: .85, bloom: .18 });
  S.floor.material.color.set(0x050506); S.floor.material.roughness = .55; S.floor.material.envMapIntensity = .15; S.pool.intensity = 9;
  const g = await new GLTFLoader().loadAsync('/@work/3d/xbot/xbot.glb');
  const box = new THREE.Box3().setFromObject(g.scene); const h0 = box.max.y - box.min.y;
  const idle = g.animations.find(a => /idle/i.test(a.name));
  P.forEach((p, i) => {
    const m = SkeletonUtils.clone(g.scene); const k = p.h / h0;
    m.scale.set(k * p.b, k, k * Math.sqrt(p.b)); m.position.x = p.x; S.scene.add(m);
    m.traverse(o => { if (o.isMesh) { o.castShadow = true;
      o.material = /joint/i.test(o.name) ? new THREE.MeshStandardMaterial({ color: i ? 0x0c0c0e : 0x55585e, metalness: .9, roughness: .3 })
        : new THREE.MeshPhysicalMaterial({ color: i === 0 ? 0x9a9da3 : i === 4 ? 0x3a1414 : 0x26272b, metalness: .25, roughness: .33, clearcoat: 1, clearcoatRoughness: .12 }); } });
    const mx = new THREE.AnimationMixer(m); mx.clipAction(idle).play(); mixers.push(mx); figs.push(m);
  });
  // height ruler: thin glowing lines at 5', 6', 7'
  for (const ft of [5, 6, 7]) {
    const ln = new THREE.Mesh(new THREE.BoxGeometry(9, .006, .006), new THREE.MeshBasicMaterial({ color: ft === 7 ? 0xff2a2a : 0x666666, transparent: true, opacity: .55 }));
    ln.position.set(1.9, ft * FT, -.6); S.scene.add(ln); ruler.push({ ft, ln });
  }
}

export function cues() {
  const c = cueList(), a = c.add;
  for (const [k, t] of Object.entries(T)) a(`/home/user/rs_work/s03/vo/${k}_f.wav`, t, 0, { duck: true });
  a('clips/s03_shaw/audio.wav', 0, -14, { len: 2.4, fade: .2 });
  a('sfx:flash', 0, -8); a('synth:sub', 0.02, -3); a('sfx:crowd_ooh', 1.6, -12);
  a('sfx:whoosh_fast', 2.5, -7); a('sfx:snap_zoom', 3.9, -9); a('sfx:sub_hit', 4.0, -6);
  a('sfx:whoosh_deep', 5.2, -6); a('sfx:rumble', 5.3, -14, { len: 1.4 });
  P.forEach((p, i) => { a('sfx:impact_metal', p.t + .05, -10 - (i === 0 ? 4 : 0)); a('synth:sub', p.t + .05, -4 + i * .5); a('sfx:swipe', p.t + .25, -8); a('sfx:pop', p.t + .55, -12); });
  a('sfx:braam', 18.88, -3); a('sfx:rumble', 19.0, -8, { len: 1.6 }); a('sfx:crowd_ooh', 20.2, -10);
  a('sfx:whoosh_deep', 21.2, -7); a('sfx:riser', 21.6, -12, { len: 1.6 }); a('sfx:sub_hit', 23.1, -6);
  return c.list;
}

const caption = (R, t, o = {}) => drawGroups(R, caps, t, { y: H * .655, size: 92, ...o });

async function shotHook(R, t) {   // Shaw shaking a bodybuilder's hand
  const c = clips.shaw;
  if (!c) placeholder(R, 'SHAW FOOTAGE', t);
  else {
    const z = 1.32 - .2 * ease.outExpo(clamp(t / .35)) + .06 * prog(t, .35, 2.1);
    const sh = shake(t, 3 + 12 * impulse(t, 0, 5));
    R.draw(await c.at(srcTime(t, 0, { speed: .65 })), { zoom: z, fx: .72, fy: .35, x: sh.x / W, y: sh.y / H, filter: 'contrast(1.12) saturate(1.1) brightness(1.08)' });
  }
  R.flash(impulse(t, 0, 7) * .9);
  R.vignette(.55);
  // size arrow on Shaw
  const a = clamp((t - 1.0) / .3);
  if (a > 0) {
    R.box(W * .69, H * .17, 6, H * .5 * ease.outExpo(a), { fill: YEL, r: 3, glow: 20, glowColor: YEL });
    R.text(`6'8"`, W * .69 + 30, H * .17 + 40, { size: 70, font: 'Anton', color: YEL, align: 'left', alpha: a, stroke: '#000', sw: 10 });
  }
  caption(R, t);
}
async function shotHandshake(R, t) {   // Jay Cutler next to a normal guy (photo)
  const img = imgs['jay_2007_handshake.jpg'];
  const p = prog(t, 2.6, 2.7, ease.inOut);
  R.draw(img, { zoom: lerp(1.0, 1.12, p), fx: lerp(.42, .58, p), fy: .45, filter: 'contrast(1.08) saturate(1.05)' });
  R.motionBlur(240 * impulse(t, 2.6, 10), 0, 8);
  R.vignette(.6);
  // labels
  const la = clamp((t - 3.0) / .25), lb = clamp((t - 3.95) / .25);
  if (la > 0) { R.box(80, 420, 360, 84, { fill: 'rgba(0,0,0,.6)', r: 42, alpha: la, stroke: 'rgba(255,255,255,.3)', sw: 2 }); R.text('NORMAL GUY', 260, 462, { size: 44, font: 'Mont', weight: 800, alpha: la, track: 3 }); }
  if (lb > 0) { R.box(W - 470, 420, 390, 84, { fill: RED, r: 42, alpha: lb, glow: 30, glowColor: 'rgba(255,0,0,.5)' }); R.text('PRO BODYBUILDER', W - 275, 462, { size: 42, font: 'Mont', weight: 800, alpha: lb, track: 2 }); }
  R.flash(impulse(t, 3.95, 9) * .3);
  R.text('PHOTO: robbden / CC BY 2.0', W - 40, H - 330, { size: 22, font: 'Mont', weight: 600, color: 'rgba(255,255,255,.55)', align: 'right' });
  caption(R, t);
}

// lineup camera path: follow the newest figure, then pull back
function cameraFor(t) {
  let idx = -1; P.forEach((p, i) => { if (t >= p.t - .15) idx = i; });
  const focusX = idx < 0 ? 0 : P[idx].x;
  return { idx, focusX };
}
async function shotLineup(R, t) {
  const { idx } = cameraFor(t);
  mixers.forEach((m, i) => m.setTime(t * .9 + i * .8));
  // figure entrances: rise from below floor with overshoot
  figs.forEach((f, i) => {
    const a = clamp((t - P[i].t) / .45);
    f.visible = t >= P[i].t - .02;
    f.position.y = -P[i].h * (1 - ease.outBack(a, 1.2));
  });
  // camera: deterministic pan between pair centres, giant tilt, then wide pull-back
  const ctr = i => i <= 0 ? P[0].x : (P[i].x + P[i - 1].x) / 2;
  let cx0 = ctr(0);
  P.forEach((p, i) => { if (i) cx0 = lerp(cx0, ctr(i), prog(t, p.t - .2, .6, ease.inOut)); });
  const wide = prog(t, 21.3, 1.4, ease.inOut);
  const giant = prog(t, 18.7, .6, ease.inOut) * (1 - wide);
  const dist = lerp(lerp(6.8, 7.6, giant), 18, wide);
  const cx = lerp(cx0, 1.9, wide);
  let imp = 0; P.forEach(p => imp += impulse(t, p.t + .05, 6)); imp += 1.5 * impulse(t, 18.9, 3);
  const sh = shake(t, .03 * imp, 18);
  S.camera.fov = 28; S.camera.updateProjectionMatrix();
  S.camera.position.set(cx + .25 * (1 - wide) + sh.x, lerp(1.0, 1.4, wide) + sh.y, dist);
  S.camera.lookAt(cx, lerp(lerp(1.2, 1.3, giant), 1.75, wide), 0);
  R.g.drawImage(S.render(), 0, 0);
  R.flash(impulse(t, 5.3, 10) * .6);
  // ruler labels (project)
  for (const { ft } of ruler) {
    const v = new THREE.Vector3(cx - .95 - 2.3 * wide, ft * FT, -.6).project(S.camera);
    const x = (v.x + 1) / 2 * W, y = (1 - v.y) / 2 * H;
    R.text(`${ft} FT`, Math.max(60, x), y - 22, { alpha: 1 - wide, size: 30, font: 'Mont', weight: 800, color: ft === 7 ? RED : '#888', align: 'left', track: 3 });
  }
  // labels above heads
  P.forEach((p, i) => {
    const a = clamp((t - p.t - .25) / .3); if (a <= 0) return;
    const head = new THREE.Vector3(p.x, p.h + .12, 0).project(S.camera);
    const x = (head.x + 1) / 2 * W, y = (1 - head.y) / 2 * H;
    const small = wide > .5;
    if (!small && i !== idx && i !== idx - 1) return;
    if (!small && i === idx - 1) { R.text(p.stat, x, y - 40, { size: 60, font: 'Anton', color: '#bbb', stroke: '#000', sw: 9, alpha: 1 - wide }); return; }
    const fade = a * (small ? 1 : clamp(1 - (t - 21.25) / .15));
    if (small) {
      R.text(p.stat, x, y - 30, { size: 46, font: 'Anton', color: i === 4 ? RED : '#fff', alpha: fade * wide, stroke: '#000', sw: 8 });
      R.text(String(i + 1), x, y - 90, { size: 40, font: 'Anton', color: YEL, alpha: fade * wide, stroke: '#000', sw: 8 });
      return;
    }
    const r = 78, py = y - 150;
    if (p.photo) {   // round photo badge
      const img = imgs[p.photo]; const g = R.g; g.save(); g.globalAlpha = fade;
      g.beginPath(); g.arc(x, py, r, 0, Math.PI * 2); g.closePath(); g.shadowColor = 'rgba(0,0,0,.8)'; g.shadowBlur = 30; g.fillStyle = '#111'; g.fill(); g.shadowBlur = 0; g.clip();
      const sc = (r * 2.6) / Math.min(img.width, img.height), dw = img.width * sc, dh = img.height * sc;
      g.drawImage(img, x - dw * p.fx, py - dh * p.fy, dw, dh); g.restore();
      R.g.save(); R.g.globalAlpha = fade; R.g.beginPath(); R.g.arc(x, py, r, 0, Math.PI * 2); R.g.lineWidth = 6; R.g.strokeStyle = i === 4 ? RED : '#fff'; R.g.stroke(); R.g.restore();
    }
    R.text(p.name, x, py + (p.photo ? r + 40 : 0), { size: 46, font: 'Anton', color: '#fff', alpha: fade, stroke: '#000', sw: 9, track: 2, maxW: 520 });
    R.text(p.stat, x, py + (p.photo ? r + 110 : 72), { size: 84, font: 'Anton', color: i === 4 ? RED : YEL, alpha: fade, stroke: '#000', sw: 12, scale: 1 + .3 * impulse(t, p.t + .3, 9) });
    R.text(p.sub, x, py + (p.photo ? r + 170 : 132), { size: 32, font: 'Mont', weight: 800, color: '#ddd', alpha: fade, stroke: '#000', sw: 7, track: 3 });
  });
  if (t < 6.75) {   // "let's line them up": empty stage + title slam
    const a = clamp((t - 5.45) / .18) * (1 - clamp((t - 6.55) / .15));
    R.text("LET'S LINE", W / 2, 520, { size: 130, font: 'Anton', color: '#fff', stroke: '#000', sw: 14, alpha: a, scale: 1 + 1.2 * Math.pow(1 - ease.outExpo(clamp((t - 5.45) / .3)), 2) });
    R.text('THEM UP', W / 2, 670, { size: 170, font: 'Anton', color: YEL, stroke: '#000', sw: 16, glow: 40, alpha: a * clamp((t - 5.7) / .15), rot: -.03 });
  }
  if (t > 21.3) {
    const a = clamp((t - 21.4) / .3);
    R.text('WHO ARE YOU', W / 2, 330, { size: 110, font: 'Anton', color: '#fff', alpha: a, stroke: '#000', sw: 14, scale: .8 + .2 * ease.outBack(a) });
    R.text('NOT FIGHTING?', W / 2, 450, { size: 120, font: 'Anton', color: YEL, alpha: clamp((t - 21.75) / .3), stroke: '#000', sw: 14, rot: -.03 });
    R.text('COMMENT 1–5', W / 2, 555, { size: 40, font: 'Mont', weight: 800, color: '#fff', alpha: clamp((t - 22.1) / .3), track: 6 });
  }
  R.vignette(.55);
  if (t < 21.3 && t > 6.6) caption(R, t);
}

export async function draw(R, t) {
  if (t < 2.6) await shotHook(R, t);
  else if (t < 5.3) await shotHandshake(R, t);
  else await shotLineup(R, t);
  R.grain(.05, t);
  for (const c of [2.6, 5.3]) R.flash(impulse(t, c, 14) * .55);
}

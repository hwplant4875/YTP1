// RageStyles #2 — "THEN vs NOW": Ronnie, Jay, Arnold. Prime vs today, the price paid, "was it worth it?"
import { W, H, clamp, ease, prog, impulse, shake, lerp, noise1 } from '/engine/fx.js';
import { loadVO, groups, drawGroups, srcTime, placeholder, cueList } from '/engine/kit.js';
import { namePlate, yearSlam } from '/engine/cards.js';
import { makeStage, THREE } from '/engine/stage3d.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const T = { l1: .35, l2: 4.5, l3: 8.4, l4: 10.6, l5: 12.7, l6: 16.0, l7: 18.9, l8: 23.1 };
export const duration = 25.6;
const RED = '#ff2a2a', YEL = '#FFD400', ICE = '#7fd4ff';
const WARM = 'sepia(.35) saturate(1.25) contrast(1.12) brightness(1.03)';
const COLD = 'saturate(.75) contrast(1.08) brightness(.96)';
const CREDIT = {
  ronnie_fibo2014: 'Health Gauge / CC BY 2.0', jay_2007_handshake: 'robbden / CC BY 2.0', jay_2014_loaded: 'Morten Skovgaard / CC BY 2.0',
  jay_2016: 'Paula R. Lively / CC BY 2.0', arnold_2026_summit: 'Bernhard Holub / CC BY-SA 4.0', arnold_1974: 'Madison Square Garden / PD',
};
let VO, caps = [], clips = {}, imgs = {}, S, bot, mixer, marks = [];

export async function setup(R) {
  VO = await loadVO('s02/vo', Object.keys(T));
  const hl = { l1: ['EIGHT', 'BIGGEST'], l2: ['THIRTEEN', 'SURGERIES', 'BACK'], l3: ['ALL', 'AGAIN'], l4: ['FOUR'], l5: ['TANK'], l6: ['SEVEN', 'ORIGINAL'],
    l7: ['SEVENTYNINE', 'PACEMAKER'], l8: ['WORTH'] };
  for (const k of Object.keys(T)) caps.push(...groups(VO[k].fw, T[k], { hl: hl[k] || [] }));
  try { clips.prime = await R.clip('clips/s05_stage'); } catch (e) { clips.prime = null; }
  for (const k of Object.keys(CREDIT)) imgs[k] = await R.image(`/@work/photos/${k}.jpg`);

  // 3D: back view of a figure, surgery sites glow red
  S = await makeStage({ hdri: 'studio_small_09', envIntensity: .7, bloom: .45 });
  S.floor.material.color.set(0x040405); S.floor.material.envMapIntensity = .1; S.pool.intensity = 6;
  const g = await new GLTFLoader().loadAsync('/@work/3d/xbot/xbot.glb');
  bot = g.scene; const box = new THREE.Box3().setFromObject(bot); const k = 1.8 / (box.max.y - box.min.y);
  bot.scale.set(k * 1.45, k, k * 1.2); S.scene.add(bot);
  bot.traverse(o => { if (o.isMesh) { o.castShadow = true;
    o.material = /joint/i.test(o.name) ? new THREE.MeshStandardMaterial({ color: 0x0b0b0d, metalness: .9, roughness: .3 })
      : new THREE.MeshPhysicalMaterial({ color: 0x2a2b30, metalness: .2, roughness: .35, clearcoat: 1, clearcoatRoughness: .1 }); } });
  mixer = new THREE.AnimationMixer(bot); mixer.clipAction(g.animations.find(a => /idle/i.test(a.name))).play();
  const bone = n => { let b = null; bot.traverse(o => { if (o.isBone && o.name.endsWith(n)) b = o; }); return b; };
  marks = { hips: bone('Hips'), spine2: bone('Spine2'), neck: bone('Neck'), head: bone('Head'), lul: bone('LeftUpLeg'), rul: bone('RightUpLeg') };
}

export function cues() {
  const c = cueList(), a = c.add;
  for (const [k, t] of Object.entries(T)) a(`/home/user/rs_work/s02/vo/${k}_f.wav`, t, 0, { duck: true });
  a('clips/s05_stage/audio.wav', 0, -16, { len: 2.4, fade: .4 });
  a('sfx:flash', 0, -8); a('synth:sub', .02, -3); a('sfx:tape_stop', 2.35, -11);
  a('sfx:glitch', 2.45, -9); a('sfx:sub_hit', 2.5, -6); for (let i = 0; i < 10; i++) a('synth:tick', 2.5 + i * .06, -16);
  a('sfx:whoosh_deep', 4.4, -6); a('sfx:heartbeat', 4.6, -12, { len: 3.6 });
  for (let i = 0; i < 13; i++) a('synth:tick', T.l2 + .97 + i * .075, -12);
  a('sfx:bass_drop', T.l2 + 2.39, -6); a('sfx:impact_metal', T.l2 + 2.96, -10);
  a('sfx:whoosh_fast', 8.3, -8); a('sfx:rumble', 8.4, -16, { len: 2 });
  a('sfx:flash', 10.55, -8); a('synth:sub', 10.6, -4); for (let i = 0; i < 4; i++) a('sfx:pop', 11.2 + i * .14, -12);
  a('sfx:swipe', 12.6, -7); a('sfx:sub_hit', 12.75, -7); a('sfx:impact_metal', T.l5 + 2.41, -9);
  a('sfx:whoosh_deep', 15.9, -6); a('sfx:braam', 16.0, -6); a('sfx:snap_zoom', 17.0, -10);
  a('sfx:glitch', 18.85, -8); a('sfx:sub_hit', 18.9, -6); for (let i = 0; i < 16; i++) a('synth:tick', T.l7 + .3 + i * .05, -15);
  a('sfx:heartbeat', T.l7 + 2.3, -9, { len: 2 }); a('sfx:ding', T.l7 + 2.54, -14);
  a('sfx:whoosh_fast', 23.0, -7); a('sfx:sub_hit', T.l8 + .88, -5); a('sfx:riser', 23.6, -14, { len: 1.6 }); a('sfx:sub_hit', 25.3, -8);
  return c.list;
}

const caption = (R, t, o = {}) => drawGroups(R, caps, t, { y: H * .655, size: 92, ...o });
// cover-fit an image inside a rect
function drawIn(R, img, x, y, w, h, { fx = .5, fy = .5, zoom = 1, filter = 'none', alpha = 1 } = {}) {
  if (!img) return; const g = R.g; g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); g.globalAlpha = alpha; g.filter = filter;
  const s = Math.max(w / img.width, h / img.height) * zoom, dw = img.width * s, dh = img.height * s;
  const ox = clamp(x + w / 2 - dw * fx, x + w - dw, x), oy = clamp(y + h / 2 - dh * fy, y + h - dh, y);
  g.drawImage(img, ox, oy, dw, dh); g.restore();
}
const tint = (R, x, y, w, h, col, a, comp = 'soft-light') => { const g = R.g; g.save(); g.globalCompositeOperation = comp; g.globalAlpha = a; g.fillStyle = col; g.fillRect(x, y, w, h); g.restore(); };
function tag(R, txt, x, y, a, col = '#fff', bg = 'rgba(0,0,0,.65)') {
  if (a <= 0) return; const w = R.measure(txt, 46, 'Anton') + 56;
  R.box(x, y - 34, w, 68, { fill: bg, r: 12, alpha: a, stroke: col, sw: 3 });
  R.text(txt, x + w / 2, y + 2, { size: 46, font: 'Anton', color: col, alpha: a, track: 3 });
}
const credit = (R, k, y = H - 330, a = 1) => R.text('PHOTO: ' + CREDIT[k], W - 40, y, { size: 22, font: 'Mont', weight: 600, color: 'rgba(255,255,255,.5)', align: 'right', alpha: a });
// split: then (top) / now (bottom), divider slides in from bottom
function split(R, t, t0, drawThen, drawNow, { thenTag, nowTag, nowCredit }) {
  const s = ease.outExpo(clamp((t - t0) / .45)); const mid = lerp(H, H / 2, s);
  drawThen(0, 0, W, mid); if (s > 0) drawNow(0, mid, W, H - mid);
  if (s > 0) { R.box(0, mid - 5, W, 10, { fill: '#fff', glow: 30, glowColor: 'rgba(255,255,255,.8)' }); R.motionBlur(0, 140 * impulse(t, t0, 9), 6); }
  tag(R, thenTag, 50, 120, clamp((t - t0 + .3) / .2), YEL);
  tag(R, nowTag, 50, mid + 90, clamp((t - t0 - .3) / .2), ICE);
  if (nowCredit && s > .5) credit(R, nowCredit, H - 40);
}

async function shotRonnie(R, t) {   // 0 – 4.5: prime Ronnie, then split to 2014
  const c = clips.prime;
  const z = 1.25 - .18 * ease.outExpo(clamp(t / .4)) + .05 * prog(t, .4, 4);
  const thenFrame = c ? await c.at(srcTime(t, 0, { speed: .62 })) : null;
  const sh = shake(t, 4 + 14 * impulse(t, 0, 5));
  split(R, t, 2.5,
    (x, y, w, h) => { if (thenFrame) drawIn(R, thenFrame, x + sh.x, y + sh.y, w, h, { zoom: z - .15, fx: .36, fy: .2, filter: WARM }); else placeholder(R, 'PRIME', t); tint(R, x, y, w, h, '#ff9a3c', .25); },
    (x, y, w, h) => { drawIn(R, imgs.ronnie_fibo2014, x, y, w, h, { zoom: 1.15 + .05 * prog(t, 2.5, 2), fx: .5, fy: .32, filter: COLD }); tint(R, x, y, w, h, '#2a6cff', .3); },
    { thenTag: 'PRIME', nowTag: '2014', nowCredit: 'ronnie_fibo2014' });
  R.flash(impulse(t, 0, 7) * .9); R.flash(impulse(t, 2.5, 12) * .5);
  // big year roll on the split
  const ya = clamp((t - 2.45) / .12) * (1 - clamp((t - 3.4) / .25));
  if (ya > 0) yearSlam(R, Math.round(lerp(2000, 2014, ease.out(clamp((t - 2.5) / .6)))), W / 2, H / 2, t, 2.45, { size: 200 });
  if (t < 2.5) namePlate(R, 'RONNIE COLEMAN', '8× MR. OLYMPIA', W / 2, 330, t, .2, { size: 104 });
  R.vignette(.55);
  if (t < 2.45 || t > 3.4) caption(R, t);
}

async function shotSurgery(R, t) {   // 4.5 – 8.4: 13 surgeries on a 3D body
  const l = t - T.l2;
  mixer.setTime(2.2 + l * .5);
  const orbit = lerp(.55, -.15, ease.inOut(clamp(l / 3.9)));
  const dist = lerp(3.9, 3.0, ease.inOut(clamp(l / 3.9)));
  const sh = shake(t, .02 * impulse(t, T.l2 + 2.39, 5), 16);
  S.camera.fov = 32; S.camera.updateProjectionMatrix();
  S.camera.position.set(Math.sin(Math.PI + orbit) * dist + sh.x, 1.35 + sh.y, Math.cos(Math.PI + orbit) * dist);
  S.camera.lookAt(0, 1.18, 0);
  bot.updateMatrixWorld(true);
  R.g.drawImage(S.render(), 0, 0);
  // surgery sites: 8 back (hips→upper spine), 3 neck, 2 hip
  const wp = b => b.getWorldPosition(new THREE.Vector3());
  const hp = wp(marks.hips), sp = wp(marks.spine2), nk = wp(marks.neck), hd = wp(marks.head);
  const back = [...Array(8)].map((_, i) => hp.clone().lerp(sp, .15 + i * .12));
  const neck = [...Array(3)].map((_, i) => nk.clone().lerp(hd, -.1 + i * .3));
  const hips = [marks.lul, marks.rul].map(b => wp(b).add(new THREE.Vector3(0, .06, 0)));
  const pts = [...back.map(p => ['BACK', p]), ...neck.map(p => ['NECK', p]), ...hips.map(p => ['HIP', p])];
  const order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
  const scr = p => { const q = p.clone(); q.z -= .14; const v = q.project(S.camera); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]; };
  const t0 = T.l2 + .97; let n = 0;
  R.g.save(); R.g.globalCompositeOperation = 'lighter';
  order.forEach((idx, i) => {
    const ti = t0 + i * .075; if (t < ti) return; n++;
    const [, p] = pts[idx]; const [x, y] = scr(p); const a = clamp((t - ti) / .12);
    const pulse = .7 + .3 * Math.sin((t - ti) * 9);
    const gr = R.g.createRadialGradient(x, y, 0, x, y, 70 * pulse); gr.addColorStop(0, `rgba(255,60,40,${.95 * a})`); gr.addColorStop(.25, `rgba(255,30,20,${.5 * a})`); gr.addColorStop(1, 'rgba(255,0,0,0)');
    R.g.fillStyle = gr; R.g.beginPath(); R.g.arc(x, y, 70 * pulse, 0, Math.PI * 2); R.g.fill();
    R.g.fillStyle = `rgba(255,240,230,${a})`; R.g.beginPath(); R.g.arc(x, y, 7, 0, Math.PI * 2); R.g.fill();
  });
  R.g.restore();
  // counter
  const ca = clamp((t - t0 + .1) / .2);
  if (ca > 0) {
    R.text(String(n), W / 2, 330, { size: 300, font: 'Anton', color: RED, stroke: '#000', sw: 20, glow: 40, glowColor: 'rgba(255,0,0,.6)', alpha: ca, scale: 1 + .12 * impulse(t, t0 + n * .075, 12) });
    R.text('SURGERIES', W / 2, 520, { size: 70, font: 'Anton', color: '#fff', alpha: ca, track: 12 });
  }
  // breakdown chips on "Eight on his back"
  [['BACK', '×8', T.l2 + 2.39], ['NECK', '×3', T.l2 + 2.75], ['HIP', '×2', T.l2 + 3.0]].forEach(([lbl, v, ti], i) => {
    const a = clamp((t - ti) / .2); if (a <= 0) return; const x = 120 + i * 300, y = 640 + (1 - ease.outBack(a)) * 40;
    R.box(x, y - 50, 260, 100, { fill: i === 0 ? RED : 'rgba(0,0,0,.6)', stroke: RED, sw: 3, r: 18, alpha: a });
    R.text(lbl, x + 90, y + 4, { size: 44, font: 'Anton', color: '#fff', alpha: a, track: 3 });
    R.text(v, x + 200, y + 4, { size: 54, font: 'Anton', color: i === 0 ? '#fff' : RED, alpha: a });
  });
  R.flash(impulse(t, T.l2 + 2.39, 8) * .35, RED);
  R.vignette(.6);
  caption(R, t, { y: H * .82 });
}

async function shotAgain(R, t) {   // 8.4 – 10.6: "he'd do it all again"
  const p = prog(t, 8.4, 2.2, ease.inOut);
  R.draw(imgs.ronnie_fibo2014, { zoom: lerp(1.25, 1.5, p), fx: .5, fy: .3, filter: 'grayscale(.6) contrast(1.15) brightness(.85)' });
  tint(R, 0, 0, W, H, '#000', .35, 'source-over');
  const a = clamp((t - 8.75) / .3);
  R.text('WOULD HE DO IT', W / 2, 360, { size: 84, font: 'Anton', color: '#fff', alpha: a, stroke: '#000', sw: 10, track: 4 });
  R.text('AGAIN?', W / 2, 470, { size: 120, font: 'Anton', color: YEL, alpha: a, stroke: '#000', sw: 12, scale: .85 + .15 * ease.outBack(a) });
  const ya = clamp((t - (T.l3 + .5)) / .15);
  if (ya > 0) R.text('YES.', W / 2, 1450, { size: 230, font: 'Anton', color: RED, stroke: '#000', sw: 16, glow: 40, glowColor: 'rgba(255,0,0,.5)', alpha: ya, scale: 1 + 1.2 * Math.pow(1 - ease.outExpo(ya), 2), rot: -.04 });
  R.flash(impulse(t, T.l3 + .5, 10) * .3);
  credit(R, 'ronnie_fibo2014', H - 40);
  R.vignette(.6); R.grain(.06, t);
  caption(R, t);
}

async function shotJay(R, t) {   // 10.6 – 16.0: Jay prime flex, then split 2007 vs 2016
  if (t < T.l5) {
    const p = prog(t, T.l4, 2.1);
    const sh = shake(t, 10 * impulse(t, T.l4, 6));
    R.draw(imgs.jay_2014_loaded, { zoom: 1.18 - .08 * ease.outExpo(clamp((t - T.l4) / .4)) + .05 * p, fx: .48, fy: .3, x: sh.x / W, y: sh.y / H, filter: WARM });
    R.flash(impulse(t, T.l4, 8) * .8);
    namePlate(R, 'JAY CUTLER', null, W / 2, 330, t, T.l4 + .05, { size: 120 });
    // 4 olympia years
    ['2006', '2007', '2009', '2010'].forEach((y, i) => {
      const a = clamp((t - (T.l4 + .6 + i * .14)) / .18); if (a <= 0) return;
      const x = W / 2 + (i - 1.5) * 230, yy = 520;
      R.box(x - 100, yy - 50, 200, 100, { fill: 'rgba(0,0,0,.6)', stroke: YEL, sw: 3, r: 16, alpha: a });
      R.text(y, x, yy + 4, { size: 54, font: 'Anton', color: YEL, alpha: a, scale: 1 + .4 * (1 - ease.outBack(a)) });
    });
    credit(R, 'jay_2014_loaded', H - 40);
    R.vignette(.5); caption(R, t);
    return;
  }
  split(R, t, T.l5,
    (x, y, w, h) => { drawIn(R, imgs.jay_2007_handshake, x, y, w, h, { zoom: 1.35, fx: .7, fy: .3, filter: WARM }); tint(R, x, y, w, h, '#ff9a3c', .22); },
    (x, y, w, h) => { drawIn(R, imgs.jay_2016, x, y, w, h, { zoom: 1.0 + .06 * prog(t, T.l5, 3.3), fx: .22, fy: .4, filter: COLD }); tint(R, x, y, w, h, '#2a6cff', .25); },
    { thenTag: '2007', nowTag: '2016', nowCredit: 'jay_2016' });
  credit(R, 'jay_2007_handshake', H / 2 - 22);
  const ta = clamp((t - (T.l5 + 2.41)) / .14);
  if (ta > 0) R.text('STILL A TANK', W / 2, H / 2 + 6, { size: 120, font: 'Anton', color: YEL, stroke: '#000', sw: 14, glow: 30, alpha: ta, scale: 1 + 1.5 * Math.pow(1 - ease.outExpo(ta), 2), rot: -.03 });
  R.flash(impulse(t, T.l5 + 2.41, 10) * .35);
  R.vignette(.5);
  if (ta <= 0) caption(R, t);
}

async function shotArnold(R, t) {   // 16.0 – 23.1: 1974 → 2026, age counter, pacemaker ECG
  if (t < T.l7) {
    const p = prog(t, T.l6, 2.9);
    R.draw(imgs.arnold_1974, { zoom: 1.35 - .25 * ease.outExpo(clamp((t - T.l6) / .5)) + .04 * p, fx: .5, fy: .3, filter: 'grayscale(1) contrast(1.25) brightness(1.05)' });
    tint(R, 0, 0, W, H, '#ffb060', .25);
    R.flash(impulse(t, T.l6, 7) * .9);
    yearSlam(R, 1974, W / 2, 360, t, T.l6 + .05, { size: 230 });
    const a = clamp((t - 17.0) / .2);
    if (a > 0) { R.text('7×', W / 2 - 250, 1450, { size: 180, font: 'Anton', color: YEL, stroke: '#000', sw: 14, alpha: a, scale: 1 + (1 - ease.outBack(a)) }); R.text('MR. OLYMPIA', W / 2 + 90, 1450, { size: 90, font: 'Anton', color: '#fff', stroke: '#000', sw: 10, alpha: a, align: 'center' }); }
    R.vignette(.55); R.grain(.09, t);
    if (a <= 0) caption(R, t);
    return;
  }
  // 2026
  const l = t - T.l7;
  R.draw(imgs.arnold_2026_summit, { zoom: 1.12 + .08 * prog(t, T.l7, 4.2), fx: .48, fy: .3, filter: COLD });
  tint(R, 0, 0, W, H, '#2a6cff', .25);
  R.flash(impulse(t, T.l7, 10) * .6); R.rgbSplit(16 * impulse(t, T.l7, 8));
  tag(R, '2026', 50, 120, clamp(l / .2), ICE);
  credit(R, 'arnold_2026_summit', H - 40);
  // age counter 27 → 79 on "Seventy-nine"
  const age = Math.round(lerp(27, 79, ease.out(clamp((l - .3) / .85))));
  const aa = clamp((l - .2) / .2);
  if (aa > 0) {
    R.text('AGE', W - 120, 300, { size: 44, font: 'Mont', weight: 800, color: '#ccc', track: 10, alpha: aa, align: 'right' });
    R.text(String(age), W - 110, 450, { size: 200, font: 'Anton', color: age > 70 ? '#fff' : '#bbb', stroke: '#000', sw: 14, alpha: aa, align: 'right', scale: 1 + .15 * impulse(t, T.l7 + 1.15, 10) });
  }
  // ECG strip with pacemaker spikes
  const ea = clamp((l - 2.2) / .3);
  if (ea > 0) {
    const g = R.g, y0 = 1560, x0 = 60, x1 = W - 60;
    R.box(x0 - 20, y0 - 150, x1 - x0 + 40, 300, { fill: 'rgba(0,0,0,.55)', r: 24, alpha: ea, stroke: 'rgba(255,60,60,.35)', sw: 2 });
    g.save(); g.globalAlpha = ea; g.beginPath(); g.rect(x0, y0 - 140, x1 - x0, 280); g.clip();
    const head = x0 + (x1 - x0) * clamp((l - 2.2) / 1.6);
    g.lineWidth = 6; g.strokeStyle = RED; g.shadowColor = RED; g.shadowBlur = 20; g.lineJoin = 'round'; g.beginPath();
    for (let x = x0; x <= head; x += 3) {
      const ph = ((x - x0) % 300) / 300; let y = 0;
      if (ph > .30 && ph < .32) y = -110;                   // pacemaker spike
      else if (ph > .36 && ph < .40) y = 20; else if (ph > .40 && ph < .44) y = -95; else if (ph > .44 && ph < .48) y = 40;
      else if (ph > .6 && ph < .72) y = -18 * Math.sin((ph - .6) / .12 * Math.PI);
      y += noise1(x * .05) * 2; x === x0 ? g.moveTo(x, y0 + y) : g.lineTo(x, y0 + y);
    }
    g.stroke(); g.fillStyle = '#fff'; g.beginPath(); g.arc(head, y0, 9, 0, Math.PI * 2); g.fill(); g.restore();
    R.text('PACEMAKER', x0 + 10, y0 - 100, { size: 40, font: 'Anton', color: RED, alpha: ea, align: 'left', track: 6 });
    R.text('♥', x1 - 30, y0 - 96, { size: 56, color: RED, alpha: ea * (.6 + .4 * Math.sin(l * 9)), align: 'right' });
  }
  R.vignette(.5);
  caption(R, t, { y: H * .6 });
}

async function shotEnd(R, t) {   // 23.1 – 25.6: three before/after rows, "WAS IT WORTH IT?"
  const g = R.g; g.fillStyle = '#060607'; g.fillRect(0, 0, W, H);
  const rows = [['ronnie_fibo2014', 'ronnie_fibo2014', 'RONNIE'], ['jay_2007_handshake', 'jay_2016', 'JAY'], ['arnold_1974', 'arnold_2026_summit', 'ARNOLD']];
  const top = 640, rh = 360, gap = 18;
  rows.forEach(([a, b, name], i) => {
    const ra = ease.outExpo(clamp((t - 23.15 - i * .1) / .4)); if (ra <= 0) return;
    const y = top + i * (rh + gap), dx = (1 - ra) * (i % 2 ? W : -W);
    if (i === 0 && clips.prime) { /* prime frame for Ronnie's "then" */ }
    const thenImg = i === 0 ? null : imgs[a];
    if (thenImg) drawIn(R, thenImg, 40 + dx, y, W / 2 - 50, rh, { fx: i === 1 ? .7 : .5, fy: .3, zoom: i === 1 ? 1.3 : 1.1, filter: i === 2 ? 'grayscale(1) contrast(1.2)' : WARM });
    else if (R._primeFrame) drawIn(R, R._primeFrame, 40 + dx, y, W / 2 - 50, rh, { fy: .35, filter: WARM });
    drawIn(R, imgs[b], W / 2 + 10 + dx, y, W / 2 - 50, rh, { fx: i === 1 ? .22 : .5, fy: .3, zoom: 1.15, filter: COLD });
    R.box(40 + dx, y, W - 80, rh, { fill: 'rgba(0,0,0,0)', stroke: 'rgba(255,255,255,.25)', sw: 2, r: 6 });
    R.text(name, W / 2 + dx, y + rh / 2, { size: 64, font: 'Anton', color: '#fff', stroke: '#000', sw: 10, track: 4 });
  });
  const a = clamp((t - (T.l8 + .85)) / .15);
  R.text('WAS IT', W / 2, 330, { size: 120, font: 'Anton', color: '#fff', stroke: '#000', sw: 12, alpha: clamp((t - 23.2) / .2) });
  if (a > 0) R.text('WORTH IT?', W / 2, 480, { size: 160, font: 'Anton', color: YEL, stroke: '#000', sw: 14, glow: 40, alpha: a, scale: 1 + 1.4 * Math.pow(1 - ease.outExpo(a), 2), rot: -.03 });
  const ca = clamp((t - 24.6) / .25);
  if (ca > 0) R.text('YES OR NO? COMMENT ↓', W / 2, 1780, { size: 50, font: 'Mont', weight: 800, color: '#fff', alpha: ca, track: 3 });
  R.flash(impulse(t, T.l8 + .88, 10) * .3);
  R.vignette(.45);
}

export async function draw(R, t) {
  if (clips.prime && !R._primeFrame) R._primeFrame = await clips.prime.at(1.2);
  if (t < T.l2) await shotRonnie(R, t);
  else if (t < T.l3) await shotSurgery(R, t);
  else if (t < T.l4) await shotAgain(R, t);
  else if (t < T.l6) await shotJay(R, t);
  else if (t < T.l8) await shotArnold(R, t);
  else await shotEnd(R, t);
  R.grain(.05, t);
  for (const c of [T.l2, T.l3, T.l4, T.l6, T.l7, T.l8]) R.flash(impulse(t, c, 14) * .5);
}

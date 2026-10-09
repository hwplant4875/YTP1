// RageStyles #1 — "BODYBUILDERS IN A SUIT": stage/physique shot → hard "suit mode" switch, 5 men, vote at the end
import { W, H, clamp, ease, prog, impulse, shake, lerp } from '/engine/fx.js';
import { loadVO, groups, drawGroups, srcTime, placeholder, cueList } from '/engine/kit.js';
import { namePlate } from '/engine/cards.js';

const T = { l1: .3, l2: 3.0, l3: 5.7, l4: 8.3, l5: 11.8, l6: 14.55, l7: 17.8, l8: 18.85, l9: 21.0, l10: 24.9, l11: 28.6 };
export const duration = 32.0;
const RED = '#ff2a2a', YEL = '#FFD400';
const WARM = 'sepia(.3) saturate(1.2) contrast(1.12)';
const SHARP = 'contrast(1.12) saturate(1.08) brightness(1.03)';
const CREDIT = {
  suit_arnold_1: 'Junta de Andalucía / CC BY-SA 4.0', suit_lou_1: 'Toglenn / CC BY-SA 4.0', stage_lou_1: 'Luigi Novi / CC BY 3.0',
  suit_terry_1: 'John B. Mueller / CC BY 2.5', stage_terry_1: 'Gage Skidmore / CC BY-SA 2.0', suit_cena_1: 'Daniel Benavides / CC BY 2.0',
  stage_cena_1: 'Mmsnapplez / CC BY-SA 4.0', suit_rock_1: 'Eva Rinaldi / CC BY-SA 2.0', suit_rock_2: 'Eva Rinaldi / CC BY-SA 2.0',
  suit_cena_2: 'Daltoncitys / CC BY-SA 4.0', suit_lou_2: 'Gage Skidmore / CC BY-SA 2.0', arnold_1974: 'Madison Square Garden / PD',
};
// each person: stage shot → suit shot at tSuit (absolute), camera focus for both
const P = [
  { n: 1, name: 'ARNOLD', sub: '7× MR. OLYMPIA', t0: T.l3, tSuit: T.l4, stage: ['arnold_1974', { fx: .5, fy: .28, zoom: 1.0 }, 'grayscale(1) contrast(1.25)'], suit: ['suit_arnold_1', { fx: .8, fy: .3, zoom: 1.05 }] },
  { n: 2, name: 'LOU FERRIGNO', sub: 'THE ORIGINAL HULK', t0: T.l5, tSuit: T.l6, stage: ['stage_lou_1', { fx: .5, fy: .3, zoom: 1.05 }], suit: ['suit_lou_1', { fx: .45, fy: .35, zoom: 1.0 }] },
  { n: 3, name: 'TERRY CREWS', sub: null, t0: T.l7, tSuit: T.l8, stage: ['stage_terry_1', { fx: .5, fy: .35, zoom: 1.0, framed: true }], suit: ['suit_terry_1', { fx: .38, fy: .3, zoom: 1.0 }] },
  { n: 4, name: 'JOHN CENA', sub: null, t0: T.l9, tSuit: T.l9 + 1.52, stage: ['stage_cena_1', { fx: .45, fy: .25, zoom: 1.0 }], suit: ['suit_cena_1', { fx: .38, fy: .3, zoom: 1.35 }] },
  { n: 5, name: 'THE ROCK', sub: null, t0: T.l10, tSuit: T.l10 + 1.36, stage: ['suit_rock_2', { fx: .5, fy: .3, zoom: 1.0 }, SHARP], suit: ['suit_rock_1', { fx: .5, fy: .3, zoom: 1.08 }] },
];
let VO, caps = [], clips = {}, imgs = {};

export async function setup(R) {
  VO = await loadVO('s01/vo', Object.keys(T));
  const hl = { l1: ['FOUR', 'HUNDRED', 'SUIT'], l2: ['STRETCH'], l3: ['SEVENTIME'], l4: ['SCARIEST', 'BLAZER'], l5: ['HULK'], l6: ['RED', 'MERCY'],
    l8: ['SUIT', 'ENERGY'], l9: ['SHOULDERS'], l10: ['VAULT', 'PINSTRIPES'], l11: ['BEST'] };
  for (const k of Object.keys(T)) caps.push(...groups(VO[k].fw, T[k], { hl: hl[k] || [] }));
  try { clips.shaw = await R.clip('clips/s03_shaw'); } catch (e) { clips.shaw = null; }
  for (const k of Object.keys(CREDIT)) imgs[k] = await R.image(`/@work/photos/${k}.jpg`);
}

export function cues() {
  const c = cueList(), a = c.add;
  for (const [k, t] of Object.entries(T)) a(`/home/user/rs_work/s01/vo/${k}_f.wav`, t, 0, { duck: true });
  a('clips/s03_shaw/audio.wav', 0, -16, { len: 3, fade: .3 });
  a('sfx:flash', 0, -9); a('sfx:snap_zoom', T.l1 + .4, -9); a('sfx:sub_hit', T.l1 + 2.0, -7); a('sfx:crowd_ooh', T.l1 + 2.1, -14);
  [0, .8, 1.6].forEach(d => a('sfx:swipe', T.l2 + d, -9)); a('sfx:impact_metal', T.l2 + 1.83, -9); a('sfx:pop', T.l2 + 2.17, -13);
  P.forEach(p => {
    a('sfx:whoosh_deep', p.t0 - .12, -8); a('sfx:pop', p.t0 + .35, -13);
    a('sfx:whoosh_fast', p.tSuit - .1, -7); a('sfx:flash', p.tSuit, -10); a('synth:sub', p.tSuit, -6); a('sfx:snap_zoom', p.tSuit + .02, -11);
  });
  a('sfx:glitch', T.l6 + 2.52, -12); a('sfx:impact_metal', T.l10 + 1.89, -9);
  a('sfx:whoosh_deep', T.l11 - .1, -7); for (let i = 0; i < 5; i++) a('sfx:pop', T.l11 + .2 + i * .12, -12);
  a('sfx:riser', T.l11 + .8, -14, { len: 1.8 }); a('sfx:ding', T.l11 + 1.66, -12);
  return c.list;
}

const caption = (R, t, o = {}) => drawGroups(R, caps, t, { y: H * .655, size: 92, ...o });
function drawIn(R, img, x, y, w, h, { fx = .5, fy = .5, zoom = 1, filter = 'none', alpha = 1 } = {}) {
  if (!img) return; const g = R.g; g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); g.globalAlpha = alpha; g.filter = filter;
  const s = Math.max(w / img.width, h / img.height) * zoom, dw = img.width * s, dh = img.height * s;
  const ox = clamp(x + w / 2 - dw * fx, x + w - dw, x), oy = clamp(y + h / 2 - dh * fy, y + h - dh, y);
  g.drawImage(img, ox, oy, dw, dh); g.restore();
}
const tint = (R, col, a, comp = 'soft-light') => { const g = R.g; g.save(); g.globalCompositeOperation = comp; g.globalAlpha = a; g.fillStyle = col; g.fillRect(0, 0, W, H); g.restore(); };
const credit = (R, k, a = 1) => CREDIT[k] && R.text('PHOTO: ' + CREDIT[k], W - 40, H - 40, { size: 22, font: 'Mont', weight: 600, color: 'rgba(255,255,255,.55)', align: 'right', alpha: a });
// full-frame photo with push-in, optional "framed" (landscape shown whole over a blurred copy)
function photo(R, key, cam, t, t0, filter, kick = 0) {
  const img = imgs[key]; const p = prog(t, t0, 3.5);
  const z = (cam.zoom || 1) * (1 + .06 * p + .22 * Math.pow(1 - ease.outExpo(clamp((t - t0) / .35)), 2) * (kick ? 1 : .4));
  const sh = shake(t, 9 * impulse(t, t0, 6), 22);
  if (cam.framed) {
    drawIn(R, img, 0, 0, W, H, { zoom: 1.2, fx: cam.fx, fy: cam.fy, filter: 'blur(26px) brightness(.45)' });
    const h = W / img.width * img.height * 1.25 * z; drawIn(R, img, sh.x, H * .42 - h / 2 + sh.y, W, h, { fx: cam.fx, fy: cam.fy, filter, zoom: 1.0 });
  } else drawIn(R, img, sh.x, sh.y, W, H, { ...cam, zoom: z, filter });
}
function suitSwitch(R, t, ts) {   // white diagonal sweep + flash + "SUIT MODE" stamp
  const s = clamp((t - ts + .12) / .24);
  if (s > 0 && s < 1) { const g = R.g; g.save(); g.translate(W / 2, H / 2); g.rotate(-.35); const x = lerp(-W * 1.3, W * 1.3, ease.inOut(s));
    g.fillStyle = 'rgba(255,255,255,.92)'; g.shadowColor = '#fff'; g.shadowBlur = 80; g.fillRect(x - 90, -H, 180, H * 2); g.restore(); }
  R.flash(impulse(t, ts, 9) * .7); R.rgbSplit(18 * impulse(t, ts, 9));
  const a = clamp((t - ts) / .12) * (1 - clamp((t - ts - 1.1) / .25));
  if (a > 0) {
    R.box(W / 2 - 220, 236, 440, 90, { fill: RED, r: 14, alpha: a, glow: 30, glowColor: 'rgba(255,0,0,.6)' });
    R.text('SUIT MODE: ON', W / 2, 283, { size: 54, font: 'YTS', weight: 900, alpha: a, track: 3, scale: 1 + .6 * Math.pow(1 - ease.outExpo(clamp((t - ts) / .25)), 2) });
  }
}

async function shotHook(R, t) {   // Brian Shaw in a suit at the Olympia
  const c = clips.shaw;
  if (c) {
    const z = 1.45 - .3 * ease.outExpo(clamp(t / .4)) + .1 * prog(t, .4, 2.6);
    const sh = shake(t, 3 + 14 * impulse(t, 0, 5) + 10 * impulse(t, T.l1 + 2.0, 7));
    R.draw(await c.at(srcTime(t, 0, { speed: .55 })), { zoom: z, fx: .8, fy: .3, x: sh.x / W, y: sh.y / H, filter: SHARP });
  } else placeholder(R, 'SHAW', t);
  R.flash(impulse(t, 0, 7) * .9); R.flash(impulse(t, T.l1 + 2.0, 9) * .4);
  const a = clamp((t - (T.l1 + .05)) / .15);
  if (a > 0) R.text('400 LBS', W / 2, 400, { size: 210, font: 'Anton', color: YEL, stroke: '#000', sw: 16, glow: 40, alpha: a, scale: 1 + 1.3 * Math.pow(1 - ease.outExpo(a), 2), rot: -.03 });
  const b = clamp((t - (T.l1 + 2.0)) / .12);
  if (b > 0) R.text('IN A SUIT', W / 2, 560, { size: 120, font: 'YTS', weight: 900, color: '#fff', stroke: '#000', sw: 12, alpha: b, scale: 1 + (1 - ease.outBack(b)) });
  R.text('BRIAN SHAW', W / 2, H * .79, { size: 48, font: 'YTS', weight: 900, color: '#fff', alpha: clamp((t - .6) / .3), track: 8, stroke: '#000', sw: 8 });
  R.vignette(.55);
  if (a <= 0) caption(R, t);
}
async function shotMontage(R, t) {   // "some men don't wear suits. they stretch them."
  const cuts = [['suit_rock_1', .5, .3, 1.15], ['suit_cena_2', .7, .35, 1.6], ['suit_lou_2', .48, .3, 1.1]];
  const i = Math.min(2, Math.floor((t - T.l2) / .8)), [k, fx, fy, z] = cuts[i], t0 = T.l2 + i * .8;
  photo(R, k, { fx, fy, zoom: z }, t, t0, SHARP, 1);
  R.motionBlur(260 * impulse(t, t0, 12), 0, 8);
  const st = T.l2 + 1.83, a = clamp((t - st) / .12);
  if (a > 0) {   // "STRETCH" — horizontally stretched slam
    const g = R.g; g.save(); g.translate(W / 2, H * .42); g.scale(1 + .5 * ease.outElastic(clamp((t - st) / .6)), 1); g.translate(-W / 2, -H * .42);
    R.text('STRETCH', W / 2, H * .42, { size: 190, font: 'Anton', color: YEL, stroke: '#000', sw: 16, glow: 40, alpha: a }); g.restore();
  }
  credit(R, k); R.vignette(.5);
  if (a <= 0) caption(R, t);
}
async function shotPerson(R, t, p) {
  const isSuit = t >= p.tSuit;
  if (!isSuit) { const [k, cam, f] = p.stage; photo(R, k, cam, t, p.t0, f || WARM, 1); if (!f) tint(R, '#ff9a3c', .2); credit(R, k); }
  else { const [k, cam, f] = p.suit; photo(R, k, cam, t, p.tSuit, f || SHARP, 1); credit(R, k); }
  suitSwitch(R, t, p.tSuit);
  // rank number + name plate on entry
  const ra = clamp((t - p.t0) / .2);
  if (ra > 0 && !(t > p.tSuit - .05 && t < p.tSuit + 1.3)) {
    R.text(String(p.n), 120, 300, { size: 220, font: 'Anton', color: YEL, stroke: '#000', sw: 16, glow: 30, alpha: ra, scale: 1 + .8 * Math.pow(1 - ease.outExpo(ra), 2), rot: -.06 });
  }
  if (t < p.tSuit) namePlate(R, p.name, p.sub, W / 2 + 60, 300, t, p.t0 + .1, { size: 96 });
  R.vignette(.5);
  caption(R, t);
}
async function shotEnd(R, t) {   // vote grid
  const g = R.g; g.fillStyle = '#070708'; g.fillRect(0, 0, W, H);
  const tiles = P.map(p => p.suit[0]), cams = P.map(p => p.suit[1]);
  const tw = 470, th = 380, x0 = (W - tw * 2 - 30) / 2, y0 = 560;
  tiles.forEach((k, i) => {
    const a = ease.outBack(clamp((t - T.l11 - .15 - i * .12) / .35), 1.3); if (a <= 0) return;
    const col = i % 2, row = Math.floor(i / 2);
    let x = x0 + col * (tw + 30), y = y0 + row * (th + 22); if (i === 4) x = (W - tw) / 2;
    const s = .9 + .1 * a; g.save(); g.globalAlpha = clamp(a); g.translate(x + tw / 2, y + th / 2); g.scale(s, s); g.translate(-(x + tw / 2), -(y + th / 2));
    drawIn(R, imgs[k], x, y, tw, th, { fx: cams[i].fx, fy: cams[i].fy, zoom: cams[i].zoom * (i === 0 ? 1.7 : 1.1), filter: SHARP });
    R.box(x, y, tw, th, { fill: 'rgba(0,0,0,0)', stroke: 'rgba(255,255,255,.35)', sw: 3, r: 8 });
    R.text(String(i + 1), x + 52, y + 70, { size: 96, font: 'Anton', color: YEL, stroke: '#000', sw: 10 });
    R.text(P[i].name, x + tw / 2, y + th - 34, { size: 40, font: 'YTS', weight: 900, color: '#fff', stroke: '#000', sw: 8 });
    g.restore();
  });
  const ha = clamp((t - T.l11) / .2), ba = clamp((t - (T.l11 + .54)) / .14);
  R.text('WHO WEARS IT', W / 2, 240, { size: 104, font: 'YTS', weight: 900, color: '#fff', stroke: '#000', sw: 10, alpha: ha });
  if (ba > 0) R.text('BEST?', W / 2, 380, { size: 170, font: 'Anton', color: YEL, stroke: '#000', sw: 14, glow: 40, alpha: ba, scale: 1 + 1.3 * Math.pow(1 - ease.outExpo(ba), 2), rot: -.03 });
  const ca = clamp((t - (T.l11 + 1.7)) / .25);
  if (ca > 0) R.text('COMMENT 1–5 ↓', W / 2, 500, { size: 52, font: 'YTS', weight: 900, color: '#fff', alpha: ca, track: 4 });
  R.vignette(.4);
}

export async function draw(R, t) {
  if (t < T.l2) await shotHook(R, t);
  else if (t < T.l3) await shotMontage(R, t);
  else if (t < T.l11) { let p = P[0]; for (const q of P) if (t >= q.t0 - .001) p = q; await shotPerson(R, t, p); }
  else await shotEnd(R, t);
  R.grain(.05, t);
  for (const c of [T.l2, T.l3, T.l5, T.l7, T.l9, T.l10, T.l11]) R.flash(impulse(t, c, 14) * .5);
}

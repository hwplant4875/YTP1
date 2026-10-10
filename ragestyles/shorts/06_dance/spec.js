// RageStyles #6 — "300 LBS AND HE DID THE SPLITS": Ronnie Coleman's 2003 Olympia posing routine, archive look
import { W, H, clamp, ease, prog, impulse, shake, lerp } from '/engine/fx.js';
import { loadVO, groups, drawGroups, srcTime, placeholder, cueList } from '/engine/kit.js';
import { yearSlam } from '/engine/cards.js';

const T = { l1: .3, l2: 4.1, l3: 6.6, l4: 8.9, l5: 10.8, l6: 12.75, l7: 15.1, l8: 16.6 };
export const duration = 19.4;
const RED = '#ff2a2a', YEL = '#FFD400';
const LOOK = 'contrast(1.1) saturate(1.05) brightness(1.04)';
let VO, caps = [], C = {};

export async function setup(R) {
  VO = await loadVO('s06/vo', Object.keys(T));
  const hl = { l1: ['THREE', 'HUNDRED', 'SPLITS'], l2: ['2003', 'THOUSAND', 'THREE'], l3: ['FLEX'], l4: ['DANCED'], l5: ['STRUTTED', 'SPUN'],
    l6: ['FLOOR', 'GYMNAST'], l7: ['SIX'], l8: ['BIGGER', 'MOVES'] };
  for (const k of Object.keys(T)) caps.push(...groups(VO[k].fw, T[k], { hl: hl[k] || [] }));
  for (const k of ['split', 'flex', 'stand', 'strut', 'spin', 'floor', 'arms']) { try { C[k] = await R.clip(`clips/s06_${k}`); } catch (e) { C[k] = null; } }
}

export function cues() {
  const c = cueList(), a = c.add;
  for (const [k, t] of Object.entries(T)) a(`/home/user/rs_work/s06/vo/${k}_f.wav`, t, 0, { duck: true });
  a('sfx:tape_stop', 0, -14); a('sfx:crowd_ooh', .2, -14, { len: 3 });
  a('sfx:snap_zoom', T.l1 + .7, -11); a('sfx:impact_metal', T.l1 + 2.85, -9); a('synth:sub', T.l1 + 2.85, -8); a('sfx:crowd_ooh', T.l1 + 3.0, -11);
  a('sfx:glitch', T.l2 - .05, -12); a('sfx:sub_hit', T.l2 + .1, -9);
  a('sfx:tick', T.l3 + .4, -16); a('sfx:tick', T.l3 + 1.0, -16); a('sfx:tick', T.l3 + 1.6, -16);
  a('sfx:tape_stop', T.l4 + .9, -13); a('sfx:flash', T.l4 + 1.2, -9); a('synth:sub', T.l4 + 1.2, -6); a('sfx:crowd_ooh', T.l4 + 1.3, -12, { len: 2.5 });
  a('sfx:whoosh_fast', T.l5 + .17, -9); a('sfx:whoosh_deep', T.l5 + .99, -8);
  a('sfx:whoosh_fast', T.l6 + .1, -8); a('sfx:thud_heavy', T.l6 + .3, -8); a('sfx:impact_metal', T.l6 + 1.43, -9); a('sfx:crowd_ooh', T.l6 + 1.5, -11);
  for (let i = 0; i < 6; i++) a('sfx:pop', T.l7 + .1 + i * .1, -13); a('sfx:ding', T.l7 + .64, -12);
  a('sfx:whoosh_deep', T.l8 - .1, -8); a('sfx:riser', T.l8 + .4, -15, { len: 2 }); a('sfx:sub_hit', T.l8 + 1.73, -9);
  return c.list;
}

const caption = (R, t, o = {}) => drawGroups(R, caps, t, { y: H * .655, size: 92, ...o });
// archive overlay: scanlines, soft chroma shift, REC/PLAY tag + date
function archive(R, t, label = 'PLAY ▶') {
  const g = R.g; g.save(); g.globalAlpha = .07; g.fillStyle = '#000';
  for (let y = (t * 60) % 6; y < H; y += 6) g.fillRect(0, y, W, 2); g.restore();
  R.rgbSplit(2.5);
  R.text(label, 70, 150, { size: 40, font: 'Mont', weight: 800, align: 'left', color: 'rgba(255,255,255,.85)', track: 4 });
  R.text('OCT 2003', W - 70, 150, { size: 40, font: 'Mont', weight: 800, align: 'right', color: 'rgba(255,255,255,.85)', track: 4 });
}
// full-width 4:3 picture over a blurred copy (keeps the whole stage visible)
function framed(R, img, cy = H * .45, zoom = 1, sh = { x: 0, y: 0 }) {
  if (!img) return;
  R.draw(img, { zoom: 1.1, filter: 'blur(30px) brightness(.35) saturate(1.2)' });
  const w = W * zoom, h = w * img.height / img.width, g = R.g;
  g.save(); g.shadowColor = 'rgba(0,0,0,.8)'; g.shadowBlur = 60; g.filter = LOOK;
  g.drawImage(img, (W - w) / 2 + sh.x, cy - h / 2 + sh.y, w, h); g.restore();
}
// 180° arc between the two feet of a split
function splitArc(R, t, t0, cx, cy, r) {
  const a = clamp((t - t0) / .45); if (a <= 0) return; const g = R.g, e = ease.outExpo(a);
  g.save(); g.lineWidth = 10; g.strokeStyle = YEL; g.shadowColor = YEL; g.shadowBlur = 25; g.setLineDash([26, 16]);
  g.beginPath(); g.arc(cx, cy, r, Math.PI, Math.PI + Math.PI * e, false); g.stroke(); g.setLineDash([]);
  g.lineWidth = 6; g.beginPath(); g.moveTo(cx - r, cy); g.lineTo(cx + r, cy); g.stroke(); g.restore();
  R.text('180°', cx, cy - r - 40, { size: 120, font: 'Anton', color: YEL, stroke: '#000', sw: 12, alpha: clamp((t - t0 - .2) / .2), scale: 1 + .6 * Math.pow(1 - ease.outExpo(clamp((t - t0 - .2) / .3)), 2) });
}

async function shotHook(R, t) {   // the split, frozen on "splits"
  const fr = T.l1 + 2.85;
  const st = t < fr ? srcTime(t, 0, { in: .3, speed: .55 }) : 1.95;
  const sh = shake(t, 10 * impulse(t, fr, 7) + 6 * impulse(t, 0, 6));
  const z = t < fr ? 1.22 + .04 * prog(t, 0, fr) : 1.26 + .04 * ease.outExpo(clamp((t - fr) / .3));
  if (C.split) framed(R, await C.split.at(st), H * .47, z, sh); else placeholder(R, 'SPLIT', t);
  if (t >= fr) { R.g.save(); R.g.globalCompositeOperation = 'saturation'; R.g.globalAlpha = .6; R.g.fillStyle = '#000'; R.g.fillRect(0, 0, W, H); R.g.restore(); splitArc(R, t, fr + .05, W / 2, H * .47 + .29 * W * z * .75, .33 * W * z); }
  R.flash(impulse(t, 0, 7) * .8); R.flash(impulse(t, fr, 10) * .6);
  const a = clamp((t - (T.l1 + .4)) / .15);
  if (a > 0) R.text('~300 LBS', W / 2, 330, { size: 190, font: 'Anton', color: '#fff', stroke: '#000', sw: 14, glow: 30, alpha: a, scale: 1 + 1.2 * Math.pow(1 - ease.outExpo(a), 2), rot: -.03 });
  archive(R, t, t >= fr ? 'PAUSE ❚❚' : 'PLAY ▶');
  R.vignette(.45);
  caption(R, t, { y: H * .76 });
}
async function shotOlympia(R, t) {   // most-muscular close-up + 2003
  const sh = shake(t, 5 * impulse(t, T.l2, 6));
  if (C.flex) R.draw(await C.flex.at(srcTime(t, T.l2, { speed: .8 })), { zoom: 1.08 + .05 * prog(t, T.l2, 2.5), fx: .48, fy: .35, x: sh.x / W, y: sh.y / H, filter: LOOK });
  R.motionBlur(0, 200 * impulse(t, T.l2, 12), 8);
  yearSlam(R, 2003, W / 2, 380, t, T.l2 + .55, { size: 250, color: YEL });
  const a = clamp((t - (T.l2 + .8)) / .25);
  if (a > 0) R.text('MR. OLYMPIA · LAS VEGAS', W / 2, 520, { size: 46, font: 'YTS', weight: 900, color: '#fff', stroke: '#000', sw: 8, alpha: a, track: 4 });
  archive(R, t); R.vignette(.5); caption(R, t);
}
async function shotStand(R, t) {   // "most giants just stand there and flex"
  if (C.stand) R.draw(await C.stand.at(srcTime(t, T.l3, { speed: .7 })), { zoom: 1.15, fx: .5, fy: .45, filter: 'grayscale(.85) contrast(1.05) brightness(.8)' });
  ['STAND.', 'FLEX.', 'REPEAT.'].forEach((w, i) => {
    const a = clamp((t - (T.l3 + .4 + i * .6)) / .12); if (a <= 0) return;
    R.text(w, W / 2, 330 + i * 120, { size: 96, font: 'YTS', weight: 900, color: i === 2 ? '#888' : '#ddd', alpha: a, track: 6 });
  });
  archive(R, t); R.vignette(.6); caption(R, t);
}
async function shotDance(R, t) {   // strut → "DANCED" slam → spin
  const hit = T.l4 + 1.2, spin = T.l5 + .99;
  if (t < spin) {
    const st = t < hit ? srcTime(t, T.l3 + 2.3, { speed: .5 }) : srcTime(t, hit, { in: .45, speed: 1.0 });
    const z = 1.12 + .25 * Math.pow(1 - ease.outExpo(clamp((t - hit) / .35)), 2) * (t >= hit ? 1 : 0);
    const sh = shake(t, 14 * impulse(t, hit, 6));
    if (C.strut) R.draw(await C.strut.at(st), { zoom: z, fx: .48, fy: .45, x: sh.x / W, y: sh.y / H, filter: t < hit ? 'grayscale(.6) brightness(.85)' : LOOK });
    R.flash(impulse(t, hit, 9) * .7);
    const a = clamp((t - hit) / .12) * (1 - clamp((t - T.l5 - .1) / .2));
    if (a > 0) R.text('DANCED.', W / 2, 400, { size: 200, font: 'Anton', color: YEL, stroke: '#000', sw: 16, glow: 40, alpha: a, scale: 1 + 1.3 * Math.pow(1 - ease.outExpo(a), 2), rot: -.04 });
  } else {
    const sh = shake(t, 6 * impulse(t, spin, 7));
    if (C.spin) R.draw(await C.spin.at(srcTime(t, spin, { in: .2, speed: 1.1 })), { zoom: 1.2, fx: .55, fy: .45, x: sh.x / W, y: sh.y / H, filter: LOOK });
    R.zoomBlur(.08 * impulse(t, spin, 10));
  }
  R.motionBlur(220 * impulse(t, T.l5 + .17, 12), 0, 8);
  archive(R, t); R.vignette(.5); caption(R, t);
}
async function shotFloor(R, t) {   // drops to the floor, split, "like a gymnast"
  const hit = T.l6 + 1.43;
  const st = t < hit ? srcTime(t, T.l6, { in: .05, speed: .45 }) : srcTime(hit, T.l6, { in: .05, speed: .45 });
  const sh = shake(t, 9 * impulse(t, T.l6 + .3, 7));
  if (C.floor) framed(R, await C.floor.at(Math.min(st, 3.3)), H * .47, 1.22 + .05 * prog(t, T.l6, 2.3), sh);
  if (t >= hit) { R.g.save(); R.g.globalCompositeOperation = 'saturation'; R.g.globalAlpha = .55; R.g.fillStyle = '#000'; R.g.fillRect(0, 0, W, H); R.g.restore(); }
  R.flash(impulse(t, T.l6, 12) * .5); R.flash(impulse(t, hit, 10) * .5);
  const a = clamp((t - hit) / .12);
  if (a > 0) R.text('GYMNAST MODE', W / 2, 360, { size: 140, font: 'Anton', color: YEL, stroke: '#000', sw: 14, glow: 30, alpha: a, scale: 1 + 1.2 * Math.pow(1 - ease.outExpo(a), 2), rot: -.03 });
  archive(R, t, t >= hit ? 'PAUSE ❚❚' : 'PLAY ▶'); R.vignette(.45);
  caption(R, t, { y: H * .76 });
}
async function shotTitle(R, t) {   // celebration + 6 trophies
  if (C.arms) R.draw(await C.arms.at(srcTime(t, T.l7, { in: .5, speed: .9 })), { zoom: 1.12, fx: .5, fy: .42, filter: LOOK });
  R.g.save(); R.g.fillStyle = 'rgba(0,0,0,.35)'; R.g.fillRect(0, 0, W, H); R.g.restore();
  for (let i = 0; i < 6; i++) {
    const a = ease.outBack(clamp((t - T.l7 - .1 - i * .1) / .25), 1.6); if (a <= 0) continue;
    const x = W / 2 + (i - 2.5) * 160, y = 420;
    R.text('🏆', x, y, { size: 110 * a, alpha: clamp(a) });
    R.text(String(1998 + i), x, y + 90, { size: 34, font: 'YTS', weight: 900, color: i === 5 ? YEL : '#ddd', alpha: clamp(a) });
  }
  const ta = clamp((t - (T.l7 + .64)) / .15);
  if (ta > 0) R.text('TITLE #6', W / 2, 640, { size: 150, font: 'Anton', color: YEL, stroke: '#000', sw: 14, glow: 40, alpha: ta, scale: 1 + 1.2 * Math.pow(1 - ease.outExpo(ta), 2) });
  archive(R, t); R.vignette(.5); caption(R, t);
}
async function shotEnd(R, t) {   // replay of the split + question
  const st = srcTime(t, T.l8, { in: .3, speed: .7 });
  if (C.split) framed(R, await C.split.at(Math.min(st, 3.1)), H * .5, 1.2 + .06 * prog(t, T.l8, 2.8));
  const a = clamp((t - T.l8) / .2), b = clamp((t - (T.l8 + 1.27)) / .15);
  R.text('NAME ONE BIGGER MAN', W / 2, 300, { size: 92, font: 'YTS', weight: 900, color: '#fff', stroke: '#000', sw: 10, alpha: a });
  if (b > 0) R.text('WHO MOVES LIKE THIS', W / 2, 430, { size: 104, font: 'Anton', color: YEL, stroke: '#000', sw: 12, glow: 30, alpha: b, scale: 1 + (1 - ease.outBack(b)) });
  const c = clamp((t - (T.l8 + 2.0)) / .25);
  if (c > 0) R.text('COMMENT ↓', W / 2, 1480, { size: 56, font: 'YTS', weight: 900, color: '#fff', alpha: c, track: 6 });
  archive(R, t, 'REPLAY ↺'); R.vignette(.45);
}

export async function draw(R, t) {
  if (t < T.l2) await shotHook(R, t);
  else if (t < T.l3) await shotOlympia(R, t);
  else if (t < T.l4) await shotStand(R, t);
  else if (t < T.l6) await shotDance(R, t);
  else if (t < T.l7) await shotFloor(R, t);
  else if (t < T.l8) await shotTitle(R, t);
  else await shotEnd(R, t);
  R.grain(.06, t);
  for (const c of [T.l2, T.l3, T.l4, T.l6, T.l7, T.l8]) R.flash(impulse(t, c, 14) * .5);
}

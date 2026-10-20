// vertical (1080x1920) scenes for the hummingbird shorts b01-b03. Hook parts get short-local time; clip parts get the
// long-form scene time, so at(id, phrase) keeps every move on the narration. Content lives in y 450..1600.
import fs from 'fs';
import { K, f1, clamp, sm, eo, pop, lerp, big, tag, fade, xfade, count, cross } from '/tmp/claude-0/sp2/eng2.mjs';
import { at } from '/tmp/claude-0/hb2/tl.mjs';
import { birdSolid, birdInside, wings, placeB, toB, PT, C, fly, perched, branch, flowerT, heartIcon, birdHeart, kid, gauge, readout, card, ecg, arrow, bobB, timer } from '/tmp/claude-0/hb2/ha.mjs';
import { lungs } from '/tmp/claude-0/hb2/s1.mjs';
import { prong, moon, zzz, thermo } from '/tmp/claude-0/hb2/s2.mjs';
export const N = K.navy, W = 1080, H = 1920;
const HA = {};
export const hat = (sid, phrase) => { HA[sid] ??= JSON.parse(fs.readFileSync(`/tmp/claude-0/hbs/audio/h_${sid}.json`));
  const s = HA[sid].characters.join(''), i = s.indexOf(phrase); if (i < 0) throw new Error(`hook phrase ${sid}: ${phrase}`); return 0.05 + HA[sid].character_start_times_seconds[i]; };
// battery icon, level 0..1
export const battery = (x, y, s, lv) => { const col = lv > 0.5 ? '#2fd47a' : lv > 0.2 ? K.yellow : K.red;
  return `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(s * 100) / 100})"><rect x="-150" y="-70" width="300" height="140" rx="26" fill="#fff" stroke="${N}" stroke-width="12"/><rect x="150" y="-30" width="26" height="60" rx="8" fill="${N}"/>
  <rect x="-132" y="-52" width="${f1(Math.max(6, 264 * lv))}" height="104" rx="14" fill="${col}"/></g>`; };

// ───────── b01 SUPER HEART ─────────
const b01h = t => { // x-ray hummingbird, camera pushes in on the beating heart; it swells on "huge"
  const th = hat('b01', 'huge'), z = eo(0, 1.6, t), sc = lerp(1.15, 1.85, z), cx = 540 - (PT.heart[0] - 600) * sc, cy = 1060;
  const hk = 1 + 0.45 * sm(th - 0.1, th + 0.4, t) + 0.14 * Math.pow(Math.max(0, Math.sin(t * 14)), 2);
  const [hx, hy] = toB(cx, cy, sc, ...PT.heart);
  let s = placeB(cx, cy, sc, birdInside({ heartK: hk, glow: 'heart' }));
  const k = pop(hat('b01', 'heart') - 0.1, t);
  if (k > 0) s += `<circle cx="${f1(hx)}" cy="${f1(hy)}" r="${f1((70 + 40 * sm(th - 0.1, th + 0.4, t)) * k + 5 * Math.sin(t * 9))}" fill="none" stroke="${K.yellow}" stroke-width="12" stroke-dasharray="22 14"/>`;
  s += tag(hx - 40, hy - 40, 250, 620, 'HEART', t, hat('b01', 'heart'), { col: K.red, txt: '#fff', size: 80 });
  s += big(540, 1520, 'HUGE!', t, th, { size: 150, fill: K.yellow, stroke: N, sw: 18 });
  return s; };
const b01a = t => { const t12 = at('h09', 'twelve hundred'), ty = at('h09', 'Yours');
  const A = () => { const beat = 1 + 0.16 * Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 5)), 3);
    return birdHeart(540, 820, 3.4, beat) + ecg(70, 1010, 1180, t, 5, { amp: 90 }) + readout(540, 1400, count(1200, t, t12, 1.4) || ' ', 'BEATS A MINUTE', { size: 150 }); };
  const B = () => { const beat = 1 + 0.16 * Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 5)), 3), sb = 1 + 0.12 * Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 1.17)), 3);
    let s = `<path d="M540 520 L540 1500" stroke="#fff" stroke-width="8" stroke-dasharray="4 22" stroke-linecap="round"/>`;
    s += `<text x="275" y="610" font-family="Black" font-size="76" fill="${N}" text-anchor="middle">BIRD</text><text x="805" y="610" font-family="Black" font-size="76" fill="${N}" text-anchor="middle">YOU</text>`;
    s += birdHeart(275, 880, 2.5, beat) + ecg(40, 510, 1170, t, 5, { amp: 70, w: 8 }) + readout(275, 1380, '1,200', '', { size: 130 });
    s += kid(805, 1090, 1.35) + heartIcon(805, 860, 0.34 * sb) + ecg(570, 1040, 1170, t, 1.17, { amp: 60, col: '#fff', w: 8 }) + readout(805, 1380, '70', '', { size: 130 });
    s += `<text x="540" y="1500" font-family="Black" font-size="56" fill="${N}" text-anchor="middle">BEATS A MINUTE</text>`;
    return s; };
  return t < ty - 0.3 ? A() : xfade(t, ty - 0.3, 0.5, A, B); };
const b01b = t => { const tr = at('h10', 'Even resting'), tn = at('h10', 'two hundred and fifty');
  const br = (Math.sin(t * Math.PI * 2 * 3.2) + 1) / 2;
  let s = branch(40, 1040, 900) + perched(540, 770, 0.9, { puff: 0.25 * br });
  s += lungs(540, 1230, 0.85, br);
  s += fade(540, 510, 'RESTING', t, tr, { size: 80, fill: '#fff', stroke: N, sw: 12 });
  if (t > tn - 0.2) s += readout(540, 1490, count(250, t, tn - 0.2, 1.2), 'BREATHS A MINUTE', { size: 130 });
  return s; };

// ───────── b02 NIGHT MODE ─────────
const b02h = t => { // sleepy bird on a branch at night; on "shuts" it puffs up, eyes close and its battery drains
  const ts = hat('b02', 'shuts'), sl = sm(ts - 0.4, ts + 0.8, t), lv = lerp(1, 0.06, eo(ts - 0.2, ts + 1.6, t));
  let s = moon(190, 600, 80) + branch(20, 1060, 1110, 26) + perched(540, 970, 1.05, { puff: sl, closed: sl });
  if (sl > 0.5) s += zzz(700, 770, t);
  s += battery(540, 1420, 1.25, lv);
  if (lv < 0.25 && Math.sin(t * 10) > 0) s += `<rect x="335" y="1320" width="410" height="200" rx="40" fill="none" stroke="${K.red}" stroke-width="10"/>`;
  return s; };
const b02a = t => { const tc = at('h20', "can't eat"), tf = at('h20', 'run out of fuel'), tt = at('h20', 'deep sleep'), tor = at('h20', 'torpor');
  const sl = sm(tt - 0.3, tt + 1.2, t);
  let s = moon(190, 600, 80) + branch(20, 1060, 960, 26) + perched(540, 820, 1.0, { puff: sl, closed: sl });
  if (t < tf - 0.2) s += `<g opacity="${f1(1 - sm(tf - 0.5, tf - 0.2, t))}">${flowerT(540, 1230, 1.5, { rot: 0, stem: 0, col: '#7a6a8a', col2: '#5a4a6a' })}${cross(540, 1300, 220, t, tc + 0.1)}</g>`;
  if (t > tf - 0.3) { const k = sm(tf - 0.3, tf, t) * (1 - sm(tt - 0.4, tt, t)), v = lerp(0.6, 0.05, eo(tf, tf + 2, t));
    if (k > 0) s += `<g opacity="${f1(k)}">${gauge(540, 1290, 190, v, { lab: 'FUEL', lo: 'E', hi: 'F', red: 0.25, rev: 1 })}</g>`; }
  if (sl > 0.5) s += zzz(700, 620, t);
  if (t > tt) s += big(540, 1270, 'TORPOR', t, tor, { size: 170, fill: '#fff', stroke: N, sw: 18 }) + fade(540, 1430, 'DEEP SLEEP', t, tt, { size: 84, fill: '#9fc4ff' });
  return s; };
const b02b = t => { const th = at('h21', 'Its heart slows'), toff = at('h21', 'switches itself off'), tm = at('h21', 'In the morning'), tw = at('h21', 'warms back up');
  const dawn = sm(tm - 0.3, tm + 1.2, t), wake = sm(tw, tw + 0.8, t), go = sm(tw + 1.0, tw + 2.4, t);
  let s = dawn > 0 ? `<defs><linearGradient id="dw2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffc46b"/><stop offset="1" stop-color="#ff8f45"/></linearGradient></defs><rect x="0" y="0" width="${W}" height="${H}" fill="url(#dw2)" opacity="${f1(dawn)}"/>` : '';
  if (dawn > 0) s += `<circle cx="190" cy="600" r="${f1(80 * dawn)}" fill="#ffe27a" stroke="#fff" stroke-width="10"/>`;
  s += branch(20, 1060, 890, 26);
  const puff = 1 - wake;
  s += go > 0 ? fly(lerp(540, 1500, go), 760 - 520 * go, 0.85, t, { rate: 7, amp: 55 }) : perched(540, 760, 0.85, { puff, closed: puff });
  if (puff > 0.5 && dawn < 0.6) s += zzz(790, 800, t);
  const lv = lerp(0.85, 0.3, eo(0.2, 2.2, t)) + 0.55 * wake;
  s += thermo(190, 1250, Math.min(0.85, lv), lv < 0.5 ? '#3ca8ff' : K.red);
  const bpm = t < th ? 1200 : Math.round(lerp(1200, 50, eo(th + 0.3, th + 3.0, t)) + wake * 1150);
  const bps = bpm / 60 / (bpm > 300 ? 4 : 1);
  s += card(330, 1000, 700, 480, '#fff', 0.92) + ecg(360, 1000, 1370, t, Math.max(0.6, bps), { amp: 70 });
  s += readout(680, 1140, Math.min(1200, bpm).toLocaleString('en-US'), 'BEATS A MINUTE', { size: 120 });
  const lab = t > tm ? ['GOOD MORNING!', tm + 0.3, K.yellow] : t > toff ? ['ALMOST OFF', toff, '#fff'] : ['COOL DOWN', 0.4, '#9fc4ff'];
  s += big(540, 480, lab[0], t, lab[1], { size: 100, fill: lab[2], stroke: N, sw: 14 });
  return s; };

// ───────── b03 FORKED TONGUE ─────────
// tongue tip: beak from the top, the tongue opens into a Y; same drawing as the long-form, laid out for 9:16
const tongueCol = (t, { split, dip, op, wet }, x0 = 120, x1 = 960, surf = 1260, top = 480) => {
  const cx = (x0 + x1) / 2;
  let s = `<rect x="${x0}" y="${top}" width="${x1 - x0}" height="${1600 - top}" rx="40" fill="#ff7f97" opacity=".35" stroke="${N}" stroke-width="10"/>`;
  let wv = `M${x0 + 5} ${surf}`; for (let x = x0 + 5; x <= x1 - 5; x += 20) wv += ` L${x} ${f1(surf + 8 * Math.sin(x / 40 + t * 3))}`;
  const pool = `${wv} L${x1 - 5} 1560 Q${x1 - 5} 1595 ${x1 - 40} 1595 L${x0 + 40} 1595 Q${x0 + 5} 1595 ${x0 + 5} 1560Z`;
  s += `<path d="${pool}" fill="#ffc83a" stroke="${N}" stroke-width="6"/>`;
  const fork = 840 + 240 * dip, len = 270, spread = 26 * split * Math.PI / 180;
  const tl = [cx - Math.sin(spread) * len, fork + Math.cos(spread) * len], tr = [cx + Math.sin(spread) * len, fork + Math.cos(spread) * len];
  s += `<path d="M${cx} ${top + 120} L${cx} ${f1(fork + 10)}" stroke="${C.tongue}" stroke-width="60" stroke-linecap="round"/>`;
  s += `<path d="M${cx - 60} ${top - 10} L${cx + 60} ${top - 10} L${cx + 18} ${top + 150} L${cx - 18} ${top + 150}Z" fill="${C.beak}" stroke="${N}" stroke-width="7" stroke-linejoin="round"/>`;
  s += prong(cx - 8 * split, fork, tl[0], tl[1], -1, op, wet) + prong(cx + 8 * split, fork, tr[0], tr[1], 1, op, wet);
  s += `<circle cx="${cx}" cy="${f1(fork)}" r="30" fill="${C.tongue}"/>`;
  if (dip > 0.05) s += `<path d="${pool}" fill="#ffc83a" opacity=".35"/>`;
  return { s, tr, fork };
};
const b03h = t => { // x-ray head drinking; the tongue slides out and a magnifier shows its split tip
  const tt = hat('b03', 'tongue'), tsp = hat('b03', 'split'), ext = 0.6 + 0.9 * eo(tt - 0.3, tt + 0.6, t);
  const cx = 240, cy = 840, sc = 1.7;
  let s = placeB(cx, cy, sc, birdInside({ tongue: ext, hyoid: 1 }) + wings(0, { still: -60, blur: 0, bones: 1 }));
  const [px, py] = toB(cx, cy, sc, 992 + ext * 40, 199), g = 1;
  if (g > 0) { const bx = 540, by = 1340, R = 240, split = eo(tsp - 0.1, tsp + 0.6, t);
    s += `<circle cx="${f1(px)}" cy="${f1(py)}" r="30" fill="none" stroke="#fff" stroke-width="8"/><path d="M${f1(px - 10)} ${f1(py + 30)} L${bx + 120} ${by - R + 20}" stroke="#fff" stroke-width="8" stroke-dasharray="14 12"/>`;
    const sp = 30 * split * Math.PI / 180, L = 230, f0 = [-160, 0], a = [f0[0] + Math.cos(sp) * L, -Math.sin(sp) * L], b = [f0[0] + Math.cos(sp) * L, Math.sin(sp) * L];
    const body = `<rect x="-300" y="-300" width="600" height="600" fill="#ffe9c2"/><path d="M-320 0 L${f0[0]} 0" stroke="${C.tongue}" stroke-width="64" stroke-linecap="round"/>` +
      `<path d="M${f0[0]} 0 L${f1(a[0])} ${f1(a[1])}" stroke="${C.tongue}" stroke-width="48" stroke-linecap="round"/><path d="M${f0[0]} 0 L${f1(b[0])} ${f1(b[1])}" stroke="${C.tongue}" stroke-width="48" stroke-linecap="round"/><circle cx="${f0[0]}" cy="0" r="32" fill="${C.tongue}"/>` +
      `<path d="M-300 -14 L${f0[0]} -14" stroke="#ffb3c6" stroke-width="8" stroke-linecap="round"/>`;
    s += `<g transform="translate(${bx} ${by}) scale(${f1(g * 100) / 100})"><defs><clipPath id="mg3"><circle r="${R}"/></clipPath></defs><circle r="${R + 14}" fill="${N}"/><g clip-path="url(#mg3)">${body}</g><circle r="${R}" fill="none" stroke="#fff" stroke-width="10"/></g>`;
  }
  s += tag(px, py, 800, 530, 'TONGUE', t, tt + 0.05, { col: C.tongue, txt: '#fff' });
  return s; };
const b03a = t => { const td = at('h13', 'dips into nectar'), to = at('h13', 'open up'), tsh = at('h13', 'snap shut'), tb = at('h13', 'pull it back');
  const dip = sm(td - 0.3, td + 0.5, t) * (1 - sm(tb - 0.1, tb + 0.8, t)), op = sm(to - 0.1, to + 0.5, t) * (1 - sm(tsh - 0.1, tsh + 0.25, t)), wet = t > tsh - 0.1 ? sm(tsh - 0.1, tsh + 0.3, t) : 0;
  const { s: col, tr, fork } = tongueCol(t, { split: 1, dip, op, wet });
  let s = col;
  s += tag(900, 1450, 820, 1520, 'NECTAR', t, td, { col: K.yellow, line: false, size: 64 });
  s += tag(tr[0] + 40, (fork + tr[1]) / 2, 820, 700, 'BRUSHES', t, to + 0.1, { col: '#fff', size: 64 });
  if (t > tsh) s += big(270, 700, 'SNAP!', t, tsh, { size: 120, fill: K.yellow, stroke: N, sw: 14, rot: -8 });
  if (t > tb) s += arrow(250, 1060, 250, 840, { w: 22, head: 60 });
  return s; };
const b03b = t => { const tn = at('h14', 'fifteen licks');
  const cx = 360, cy = 820, sc = 1.15, lick = (Math.sin(t * Math.PI * 2 * 4) + 1) / 2;
  const [bx, by] = toB(cx, cy, sc, 992, 199);
  let s = flowerT(bx + 6, by + 4, 1.15, { rot: -62, stem: 0 });
  s += placeB(cx, cy, sc, birdInside({ tongue: 0.6 + 1.4 * lick }) + wings(t, { rate: 7, amp: 50, blur: 3, bones: 1 }));
  const a = (t * 2) % 1 * Math.PI * 2;
  s += `<g transform="translate(250 1360) scale(0.85)"><circle r="120" fill="#fff" stroke="${N}" stroke-width="10"/><rect x="-24" y="-160" width="48" height="34" rx="8" fill="${N}"/><path d="M0 0 L${f1(Math.sin(a) * 90)} ${f1(-Math.cos(a) * 90)}" stroke="${K.red}" stroke-width="12" stroke-linecap="round"/><circle r="12" fill="${N}"/></g>`;
  if (t > tn - 0.3) s += readout(690, 1380, count(15, t, tn - 0.3, 0.8), 'LICKS A SECOND', { size: 200 });
  s += big(540, 1140, 'FAST!', t, 0.3, { size: 110, fill: '#fff', stroke: N, sw: 14 });
  return s; };

export const VS1 = { b01: [b01h, b01a, b01b], b02: [b02h, b02a, b02b], b03: [b03h, b03a, b03b] };

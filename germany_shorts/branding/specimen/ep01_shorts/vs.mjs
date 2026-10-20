// vertical (1080x1920) scenes for the shark shorts. Each short: [hook(t), part1(t), ...]; part times are the long-form
// scene's local time, so at(id, phrase) keeps every move on the narration. Content lives in y 480..1600, x < 900 for UI.
import fs from 'fs';
import { K, f1, clamp, sm, eo, pop, lerp, seed, rnd, big, tag, place, toScr, sharkSolid, sharkInside, sharkXray, bob, PT, ICON, icon, cross, count, SHARK, fade, xfade } from '/tmp/claude-0/sp2/eng2.mjs';
import { at } from '/tmp/claude-0/sp2/tl2.mjs';
import { track, bodyMap, topShark, topFish } from '/tmp/claude-0/sp2/topshark.mjs';
import { splash } from '/tmp/claude-0/sp2/s2.mjs';
const MAP = JSON.parse(fs.readFileSync('/tmp/claude-0/sp/map.json'));
const W = 1080, H = 1920, N = K.navy;
// hook word timing (narration starts 0.05 s into the short)
const HA = {}; const hat = (sid, phrase) => { HA[sid] ??= JSON.parse(fs.readFileSync(`/tmp/claude-0/shs/audio/h_${sid}.json`));
  const s = HA[sid].characters.join(''), i = s.indexOf(phrase); if (i < 0) throw new Error(`hook phrase ${sid}: ${phrase}`); return 0.05 + HA[sid].character_start_times_seconds[i]; };
const LIVER = 'M445 238 C480 226 620 222 712 236 C690 262 640 284 560 286 C500 288 460 270 445 238Z';
const tooth = (x, y, s, rot = 0, c = '#fff') => `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(rot)}) scale(${f1(s * 100) / 100})"><path d="M-30 0 L-4 -80 L4 -80 L30 0Z" fill="${c}" stroke="${N}" stroke-width="5" stroke-linejoin="round"/></g>`;
const dent = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${s})"><path d="M-30 -22 C-8 -30 20 -22 36 0 C20 22 -8 30 -30 22 C-22 8 -22 -8 -30 -22Z" fill="#dfe6f0" stroke="${N}" stroke-width="3"/><path d="M-18 -10 L24 -3 M-18 10 L24 3" stroke="#8a97ad" stroke-width="3"/></g>`;
const wave = (wl, t) => `<path d="M-20 ${wl} ${Array.from({ length: 30 }, (_, i) => `L${i * 40} ${f1(wl + 8 * Math.sin(i * 0.5 + t * 2.5))}`).join(' ')}" stroke="#fff" stroke-width="6" fill="none"/>`;
const flash = (t, t0, d = 0.25) => t > t0 && t < t0 + d ? `<rect width="${W}" height="${H}" fill="#fff" opacity="${f1(0.55 * (1 - (t - t0) / d))}"/>` : '';
const shake = (t, t0, a = 14) => t > t0 && t < t0 + 0.4 ? a * Math.exp(-(t - t0) * 8) * Math.sin((t - t0) * 70) : 0;

// ───────── s01 ZERO BONES ─────────
const s01h = t => { // vertical shark, an x-ray scan beam sweeps down and reveals the cartilage skeleton
  const cx = 540, cy = 1060, sc = 1.15, by = lerp(470, 1660, eo(0, 2.3, t));
  let s = `<defs><clipPath id="sc1"><rect x="0" y="0" width="${W}" height="${f1(by)}"/></clipPath></defs>`;
  s += place(cx, cy, sc, sharkSolid('#dfe6f0', N, 6), { rot: -90 });
  s += `<g clip-path="url(#sc1)"><rect x="0" y="470" width="${W}" height="${f1(Math.max(0, by - 470))}" fill="#0b2a4d" opacity=".55"/>${place(cx, cy, sc, sharkXray(5), { rot: -90 })}</g>`;
  s += `<rect x="0" y="${f1(by - 26)}" width="${W}" height="52" fill="${K.cyan}" opacity=".35"/><path d="M0 ${f1(by)} L${W} ${f1(by)}" stroke="${K.cyan}" stroke-width="8"/>`;
  const tz = hat('s01', 'zero');
  if (t > tz) s += `<g transform="translate(830 ${f1(1180)}) rotate(-12) scale(${f1(pop(tz, t) * 100) / 100})"><rect x="-150" y="-80" width="300" height="160" rx="20" fill="none" stroke="${K.red}" stroke-width="14"/><text y="48" font-family="Black" font-size="130" fill="${K.red}" text-anchor="middle">0</text></g>`;
  return s; };
const s01a = t => { const tn = at('n03', "That's the same");
  const A = () => { const cx = 540, cy = 900, sc = 1.0;
    return place(cx, cy + bob(t), sc, sharkXray(5)) + tag(...toScr(cx, cy, sc, ...PT.spine), 540, 1300, 'CARTILAGE', t, at('n03', 'cartilage'), { col: N, txt: '#fff', size: 80 }); };
  const B = () => { const hx = 500, hy = 1040, hs = 2.3, tw = at('n03', 'wiggle'), wig = t > tw ? 9 * Math.sin((t - tw) * 22) * Math.exp(-(t - tw) * 0.9) : 0;
    let s = `<g transform="translate(${hx} ${hy}) scale(${hs})">${ICON.head()}<g transform="rotate(${f1(wig)} -40 -40)"><ellipse cx="-40" cy="-40" rx="26" ry="40" fill="#ffc29a" stroke="${N}" stroke-width="7"/><path d="M-44 -62 Q-28 -40 -44 -18" stroke="${N}" stroke-width="5" fill="none"/></g></g>`;
    s += tag(hx + 145 * hs, hy, 790, 620, 'NOSE', t, at('n03', 'nose'), { col: K.yellow, size: 80 });
    s += tag(hx - 40 * hs, hy - 40 * hs, 250, 620, 'EAR', t, at('n03', 'ears'), { col: K.yellow, size: 80 });
    if (t > tw) s += big(540, 1500, 'WIGGLE IT!', t, tw, { size: 110, fill: '#fff', stroke: N, sw: 14 });
    else s += fade(540, 1500, 'CARTILAGE', t, tn - 0.3, { size: 110, fill: N, stroke: '#fff', sw: 14, d: 0.7 });
    return s; };
  return t < tn - 0.6 ? A() : xfade(t, tn - 0.6, 0.6, A, B); };
// top-view shark weaving up the screen after a darting fish
const TRV = track([[540, 2500], [540, 1900], [300, 1600], [780, 1300], [300, 1050], [760, 800], [700, 560], [420, 620], [330, 860], [600, 1000], [820, 760], [560, 380], [540, -600]]);
const s01b = t => { const sc = 0.68, v = 560, tc = 6.0, lunge = 140 * eo(4.6, tc, t), sh = 1150 + v * t + lunge;
  const m = bodyMap(TRV, sh, sc, t * Math.PI * 2 * 1.9, 46 + 16 * sm(4.4, 5.2, t));
  let s = '';
  for (let i = 1; i <= 6; i++) { const p = TRV.at(sh - 1000 * sc - i * 60), age = i / 6; s += `<circle cx="${f1(p[0])}" cy="${f1(p[1])}" r="${f1(14 + age * 40)}" fill="none" stroke="#fff" stroke-width="4" opacity="${f1(0.35 * (1 - age))}"/>`; }
  if (t < tc) { const lead = 420 - 390 * eo(4.6, tc, t) + 30 * Math.sin(t * 3), fs = sh + lead, p = TRV.at(fs), d = TRV.dir(fs), j = 28 * Math.sin(t * 7); s += topFish(p[0] - d[1] * j, p[1] + d[0] * j, d, t, 1.3); }
  s += topShark(m, { sw: 6 / sc * 0.55, bite: t > tc ? Math.exp(-(t - tc) * 4) : 0 });
  s += big(270, 1480, 'LIGHT', t, at('n04', 'lighter'), { size: 120, fill: K.yellow, stroke: N, sw: 12 }) + big(790, 1480, 'BENDY', t, at('n04', 'bend'), { size: 120, fill: K.yellow, stroke: N, sw: 12, rot: -6 });
  s += big(540, 1610, 'FAST TURNS', t, at('n04', 'turn quickly'), { size: 90 });
  return s; };

// ───────── s02 TEETH CONVEYOR ─────────
// jaw as a wheel: the front tooth stands on top, spare rows wait folded around the left of the gum; step = teeth replaced
const JX = 540, JY = 1180, JR = 300, DA = 30;
const belt = (t, step, arrow = 0) => { const n = Math.floor(step), ph = step - n, roll = sm(0.3, 0.95, ph), fall = clamp(ph / 0.55);
  let s = `<circle cx="${JX}" cy="${JY}" r="${JR}" fill="#e88f9b" stroke="${N}" stroke-width="9"/><circle cx="${JX}" cy="${JY}" r="${JR - 70}" fill="#f4ecdc" stroke="${N}" stroke-width="7"/>`;
  s += `<text x="${JX}" y="${JY + 30}" font-family="Black" font-size="84" fill="${N}" text-anchor="middle" opacity=".55">JAW</text>`;
  for (let k = 7; k >= 1; k--) { const a = -90 - DA * (k - roll), r = a * Math.PI / 180, sz = lerp(2.3, 1.2, clamp((k - roll) / 6)), lean = -48 * clamp((k - roll) / 2);
    if (a < -300) continue; s += tooth(JX + (JR - 10) * Math.cos(r), JY + (JR - 10) * Math.sin(r), sz, a + 90 + lean); }
  if (fall < 1) { const x = JX + 260 * fall, y = JY - JR + 10 - 260 * fall + 1300 * fall * fall; s += `<g opacity="${f1(1 - sm(0.75, 1, fall))}">${tooth(x, y, 2.3, 110 * fall, '#fff')}</g>`; }
  if (arrow > 0) { const o = (t * 90) % 360; s += `<g opacity="${f1(arrow)}"><path d="M${JX - JR - 60} ${JY + 140} A${JR + 70} ${JR + 70} 0 0 1 ${JX - 120} ${JY - JR - 60}" fill="none" stroke="${K.yellow}" stroke-width="26" stroke-linecap="round" stroke-dasharray="60 34" stroke-dashoffset="${f1(-o)}"/><path d="M${JX - 140} ${JY - JR - 110} L${JX - 50} ${JY - JR - 64} L${JX - 136} ${JY - JR - 8}Z" fill="${K.yellow}" stroke="${N}" stroke-width="6"/></g>`; }
  return s; };
const s02h = t => { const tl = hat('s02', 'loses') - 0.1;
  let s = belt(t, t < tl ? 0.999 : 1 + eo(tl, tl + 1.4, t) * 0.999);
  s += tag(JX, JY - JR - 150, 820, 620, 'FRONT TOOTH', t, -1, { col: '#fff', size: 64 });
  if (t > tl + 0.1) s += big(830, 1620, 'OUT!', t, tl + 0.15, { size: 130, fill: K.red, stroke: '#fff', sw: 14 });
  return s; };
const s02a = t => { const tF = at('n07', 'falls out') - 0.15, tM = at('n07', 'moves up'), tB = at('n07', 'conveyor belt');
  const step = 2 + (t < tF ? -0.001 : t < tB ? eo(tF, tM + 0.8, t) * 0.999 : 1 + (t - tB) / 1.3);
  let s = belt(t, step, sm(tB - 0.2, tB + 0.4, t));
  if (t > tM - 0.2 && t < tB) s += tag(JX - 40, JY - JR - 120, 250, 600, 'NEXT ONE', t, tM - 0.2, { col: K.green, txt: '#fff', size: 72 });
  if (t > tF && t < tB) s += fade(830, 1620, 'OUT!', t, tF + 0.2, { size: 130, fill: K.red, stroke: '#fff', sw: 14, d: 0.3 });
  s += fade(540, 1640, 'CONVEYOR BELT', t, tB, { size: 100, fill: K.yellow, stroke: N, sw: 14, d: 0.35 });
  return s; };
const fossil = `<path d="M-120 40 L-14 -230 Q0 -244 14 -230 L120 40 Q60 70 0 60 Q-60 70 -120 40Z" fill="#b08a5e" stroke="${N}" stroke-width="8" stroke-linejoin="round"/><path d="M-120 40 Q0 120 120 40 L110 80 Q0 160 -110 80Z" fill="#8a6a46" stroke="${N}" stroke-width="7"/>${Array.from({ length: 9 }, (_, i) => { const u = i / 9, x = -120 + 106 * u, y = 40 - 270 * u; return `<path d="M${f1(x)} ${f1(y)} l-12 -8 l10 -10" fill="none" stroke="${N}" stroke-width="4"/><path d="M${f1(-x)} ${f1(y)} l12 -8 l-10 -10" fill="none" stroke="${N}" stroke-width="4"/>`; }).join('')}`;
const s02b = t => { let s = ''; seed(8);
  for (let i = 0; i < 60; i++) { const x = 110 + rnd() * 860, t0 = 0.05 + rnd() * 3.4, rot = rnd() * 360, end = rnd() * 50 - 25, pile = 1600 - Math.floor(rnd() * 4) * 46 - (Math.abs(x - 540) < 280 ? rnd() * 130 : 0);
    const k = clamp((t - t0) / 0.6), y = lerp(500, pile, k * k); if (t > t0) s += tooth(x, y, 1.2, lerp(rot, end, k)); }
  const tf = at('n08', 'fossils');
  if (t < tf - 0.1) s += big(540, 900, 'THOUSANDS', t, at('n08', 'thousands'), { size: 150, stroke: N, sw: 14 });
  if (t > tf - 0.1) { const k = pop(tf - 0.1, t); s += `<rect width="${W}" height="${H}" fill="${N}" opacity="${f1(0.6 * sm(tf - 0.1, tf + 0.2, t))}"/><g transform="translate(540 1130) rotate(${f1(-6 + 3 * Math.sin(t * 2))}) scale(${f1(k * 1.6 * 100) / 100})">${fossil}</g>`;
    s += big(540, 1530, 'FOSSIL', t, tf + 0.25, { size: 150, fill: K.yellow, stroke: N, sw: 14 }); }
  return s; };

// ───────── s03 SKIN ─────────
const strokeArrow = (cx, cy, sc, k, dir, col, jit = 0) => { const ax0 = cx + 380 * sc, ax1 = cx - 380 * sc, ay = cy - 30 * sc, a = dir > 0 ? ax1 : ax0, b = dir > 0 ? ax0 : ax1, e = lerp(a, b, k);
  return `<path d="M${f1(a)} ${f1(ay + jit)} L${f1(e)} ${f1(ay - jit)}" stroke="${col}" stroke-width="24" stroke-linecap="round"/><path d="M${f1(e + dir * 30)} ${f1(ay)} l${-dir * 55} -42 l0 84Z" fill="${col}"/>` + hand(e, ay - 20 + jit, dir); };
const hand = (x, y, dir) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${dir > 0 ? 1.5 : -1.5} 1.5)"><path d="M-70 -20 Q-74 -60 -40 -62 L30 -62 Q46 -62 46 -50 Q46 -40 30 -40 L60 -40 Q74 -40 74 -28 Q74 -16 60 -16 L64 -16 Q76 -16 76 -4 Q76 8 62 8 L58 8 Q70 8 70 20 Q70 30 56 30 L-30 30 Q-70 30 -70 -20Z" fill="#ffd9b8" stroke="${N}" stroke-width="6" stroke-linejoin="round"/><path d="M-70 -30 L-130 -40 L-130 34 L-70 24" fill="#5b8bd9" stroke="${N}" stroke-width="6" stroke-linejoin="round"/></g>`;
const s03h = t => { const cx = 540, cy = 1000, sc = 1.0, k = 0.35 + 0.65 * eo(0, 1.6, t), jit = 4 * Math.sin(t * 60), sx = shake(t, 1.6, 10);
  let s = place(cx + sx, cy + bob(t, 4), sc, sharkSolid('#dfe6f0', N, 6)) + strokeArrow(cx, cy, sc, k, 1, K.red, jit);
  s += big(540, 1400, 'OUCH!', t, 1.6, { size: 140, fill: K.red, stroke: '#fff', sw: 14 });
  return s; };
const s03a = t => { const tb = at('n06', 'Because'); let s = '';
  if (t < tb - 0.15) { const cx = 540, cy = 1000, sc = 1.0, t1 = at('n06', 'Stroke a shark'), t2 = at('n06', 'Stroke it the other');
    s += place(cx, cy + bob(t, 4), sc, sharkSolid('#dfe6f0', N, 6));
    if (t < t2) { s += strokeArrow(cx, cy, sc, eo(t1, t1 + 1.4, t), -1, K.green); s += big(540, 1400, 'SMOOTH', t, at('n06', 'smooth'), { size: 140, fill: K.green, stroke: N, sw: 14 }); }
    else { s += strokeArrow(cx, cy, sc, eo(t2, t2 + 1.4, t), 1, K.red, 4 * Math.sin(t * 60)); s += big(540, 1400, 'ROUGH!', t, at('n06', 'sandpaper'), { size: 140, fill: K.red, stroke: N, sw: 14 }); }
  } else { const cx = 520, cy = 1000, R = 380, z = 0.8 + 0.35 * eo(tb, tb + 2, t);
    s += `<defs><clipPath id="mg6v"><circle cx="${cx}" cy="${cy}" r="${R}"/></clipPath></defs><circle cx="${cx}" cy="${cy}" r="${R + 22}" fill="${N}"/><g clip-path="url(#mg6v)"><rect x="${cx - R}" y="${cy - R}" width="${2 * R}" height="${2 * R}" fill="#9fb3cc"/><g transform="translate(${cx} ${cy}) scale(${f1(z * 100) / 100})">`;
    for (let r = -6; r <= 6; r++) for (let c = -7; c <= 7; c++) s += dent(c * 74 + (r % 2 ? 37 : 0), r * 54, 1.25);
    const tf = at('n06', 'slide through');
    if (t > tf - 0.3) for (let i = 0; i < 7; i++) { const y = -270 + i * 90, ph = ((t - tf) * 360 + i * 90) % 900 - 450; s += `<path d="M${f1(ph - 140)} ${y} L${f1(ph + 140)} ${y}" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity="${f1(sm(tf - 0.3, tf + 0.2, t))}"/>`; }
    s += `</g></g><path d="M${cx + R * 0.7} ${cy + R * 0.7} L${cx + R * 1.0} ${cy + R * 1.0}" stroke="${N}" stroke-width="44" stroke-linecap="round"/>`;
    s += tag(cx + 60, cy - 60, 540, 560, 'DENTICLES', t, at('n06', 'denticles'), { col: K.yellow, size: 80 });
    s += big(540, 1500, 'TINY TEETH!', t, at('n06', 'little teeth'), { size: 120, fill: K.yellow, stroke: N, sw: 14 }); }
  return s; };

// ───────── s04 LIVER ─────────
const glowLiver = (cx, cy, sc, g, t, rot = 0) => { const [lx, ly] = PT.liver, p = 1 + 0.05 * Math.sin(t * 6) * g;
  return place(cx, cy, sc, `<g transform="translate(${lx} ${ly}) scale(${f1(p * 100) / 100}) translate(${-lx} ${-ly})"><path d="${LIVER}" fill="${K.yellow}" stroke="#fff" stroke-width="${f1(7 * g)}"/></g>`, { rot }); };
const s04h = t => { const cx = 540, cy = 1060, sc = 1.15;
  let s = place(cx, cy, sc, sharkInside({}, N, 5), { rot: -90 }) + glowLiver(cx, cy, sc, 1, t, -90);
  const [lx, ly] = PT.liver, a = -Math.PI / 2, X = cx + ((lx - 500) * Math.cos(a) - (ly - 215) * Math.sin(a)) * sc, Y = cy + ((lx - 500) * Math.sin(a) + (ly - 215) * Math.cos(a)) * sc;
  s += tag(X, Y, 850, Y - 120, '?', t, -1, { col: K.yellow, size: 110 });
  return s; };
const s04a = t => { const cx = 540, cy = 980, sc = 1.0, y = cy + bob(t, 5), tl = at('n10', "It's the liver"), tq = at('n10', 'a quarter');
  let s = place(cx, y, sc, sharkInside({}, N, 5.5)) + (t > tl ? glowLiver(cx, y, sc, sm(tl, tl + 0.4, t), t) : '');
  const P = n => toScr(cx, y, sc, ...PT[n]), th = at('n10', 'not the heart'), ts = at('n10', 'not the stomach');
  if (t < tl) { s += tag(...P('heart'), 790, 640, 'HEART', t, Math.max(0.1, th - 0.3), { col: K.red, txt: '#fff', size: 72 }) + cross(...P('heart'), 60, t, th + 0.4);
    s += tag(...P('stomach'), 290, 640, 'STOMACH', t, ts, { col: K.purple, txt: '#fff', size: 72 }) + cross(...P('stomach'), 60, t, ts + 0.5); }
  s += tag(...P('liver'), 540, 1290, 'LIVER', t, tl, { col: K.yellow, size: 100 });
  if (t > tq) { const k = pop(tq, t), a = Math.PI * 0.5 * eo(tq + 0.2, tq + 0.9, t);
    s += `<g transform="translate(250 1480) scale(${f1(k * 0.8 * 100) / 100})"><circle r="120" fill="#fff" stroke="${N}" stroke-width="9"/><path d="M0 0 L0 -120 A120 120 0 0 1 ${f1(120 * Math.sin(a))} ${f1(-120 * Math.cos(a))}Z" fill="${K.yellow}" stroke="${N}" stroke-width="6"/></g>`;
    s += big(400, 1460, '1/4 OF ITS', t, tq + 0.3, { size: 84, stroke: N, sw: 12, anchor: 'start' }) + big(400, 1550, 'WEIGHT', t, tq + 0.3, { size: 84, fill: K.yellow, stroke: N, sw: 12, anchor: 'start' }); }
  return s; };
const s04b = t => { const tf = at('n11', 'so the liver'), tm = at('n11', 'Most fish'); let s = '';
  if (t < tf - 0.15) { const gx = 540, gy = 1000, k = eo(at('n11', 'full of oil'), at('n11', 'full of oil') + 2.5, t);
    s += `<path d="M${gx - 260} ${gy - 340} L${gx - 220} ${gy + 330} L${gx + 220} ${gy + 330} L${gx + 260} ${gy - 340}" fill="#bfe8ff" fill-opacity=".55" stroke="#fff" stroke-width="12" stroke-linejoin="round"/>`;
    seed(11); for (let i = 0; i < 18; i++) { const x = gx - 180 + rnd() * 360, y0 = gy + 280 - rnd() * 100, y = lerp(y0, gy - 230 + rnd() * 40, clamp(k * 1.3 - rnd() * 0.3)); s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(14 + rnd() * 10)}" fill="${K.yellow}" stroke="${N}" stroke-width="3"/>`; }
    if (k > 0.8) s += `<rect x="${gx - 250}" y="${gy - 300}" width="500" height="${f1(90 * sm(0.8, 1, k))}" fill="${K.yellow}" opacity=".9"/>`;
    s += tag(gx + 200, gy - 250, 760, 560, 'OIL', t, at('n11', 'Oil is lighter'), { col: K.yellow, size: 80 }) + tag(gx + 180, gy + 150, 700, 1480, 'WATER', t, at('n11', 'than water'), { col: '#fff', size: 80 });
  } else if (t < tm - 0.15) { const wl = 1000, cx = 540, sc = 1.0, y = wl - 20 + 10 * Math.sin(t * 1.8);
    s += `<rect x="0" y="${wl}" width="${W}" height="${H - wl}" fill="${K.deep}" opacity=".45"/>`;
    s += place(cx, y, sc, `<path d="${SHARK}" fill="#fff" stroke="${N}" stroke-width="6"/><path d="${LIVER}" fill="${K.yellow}" stroke="${N}" stroke-width="4"/><circle cx="905" cy="190" r="9" fill="${N}"/>`) + wave(wl, t);
    s += tag(...toScr(cx, y, sc, ...PT.liver), 540, 1400, 'LIVER = FLOAT', t, at('n11', 'pool float') - 0.3, { col: K.yellow, size: 84 });
    const k = pop(at('n11', 'pool float'), t); if (k > 0) s += `<g transform="translate(540 620) rotate(${f1(8 * Math.sin(t * 2))}) scale(${f1(k * 100) / 100})"><circle r="120" fill="none" stroke="${K.red}" stroke-width="62"/><circle r="120" fill="none" stroke="#fff" stroke-width="62" stroke-dasharray="94 94"/><circle r="151" fill="none" stroke="${N}" stroke-width="6"/><circle r="89" fill="none" stroke="${N}" stroke-width="6"/></g>`;
  } else { const ts = at('n11', "Sharks don't have one"), tu = at('n11', 'They use their liver');
    s += `<g transform="translate(540 720) scale(1.9)">${ICON.fish()}<g opacity="${f1(sm(tm + 0.5, tm + 0.9, t))}"><circle cx="18" cy="6" r="24" fill="#bfefff" stroke="${N}" stroke-width="4"/><circle cx="10" cy="-2" r="6" fill="#fff"/></g></g>`;
    s += tag(540, 720, 790, 560, 'AIR BUBBLE', t, at('n11', 'a bubble of air'), { col: '#fff', size: 64 });
    if (t > ts - 0.1) { s += place(540, 1250, 0.8, `<path d="${SHARK}" fill="#fff" stroke="${N}" stroke-width="8"/><path d="${LIVER}" fill="${K.yellow}" stroke="${N}" stroke-width="6" opacity="${f1(sm(tu, tu + 0.3, t))}"/><circle cx="905" cy="190" r="10" fill="${N}"/>`);
      s += big(540, 1010, 'NO BUBBLE', t, ts, { size: 100, fill: K.red, stroke: '#fff', sw: 12 }) + tag(...toScr(540, 1250, 0.8, ...PT.liver), 540, 1520, 'LIVER', t, tu, { col: K.yellow, size: 80 }); } }
  return s; };

// ───────── s05 BITE FORCE ─────────
// front view of open jaws: arched gum bands with serrated teeth; o = half gap
const jaws = (cx, cy, w, o, h = 150) => { let s = '';
  for (const sg of [-1, 1]) { const P = u => [cx - w + 2 * w * u, cy + sg * (o + h * (1 - (2 * u - 1) ** 2))], pts = Array.from({ length: 21 }, (_, i) => P(i / 20)), d = 'M' + pts.map(p => `${f1(p[0])} ${f1(p[1])}`).join(' L');
    let teeth = ''; for (let i = 1; i < 10; i++) { const u = i / 10, [x, y] = P(u), sz = 1 - 0.55 * Math.abs(2 * u - 1), tw = 38 * sz, th = 92 * sz;
      teeth += `<path d="M${f1(x - tw)} ${f1(y - sg * 20)} L${f1(x)} ${f1(y - sg * (20 + th))} L${f1(x + tw)} ${f1(y - sg * 20)}Z" fill="#fff" stroke="${N}" stroke-width="5" stroke-linejoin="round"/>`; }
    s += teeth + `<path d="${d}" fill="none" stroke="${N}" stroke-width="78" stroke-linecap="round"/><path d="${d}" fill="none" stroke="#e88f9b" stroke-width="62" stroke-linecap="round"/>`; }
  return s; };
const bar = (cx, cy, bend, w = 380) => { const a = bend * 28; return `<g transform="translate(${cx} ${cy})"><g transform="rotate(${f1(-a)})"><rect x="${-w}" y="-28" width="${w}" height="56" rx="10" fill="#b7c3d3" stroke="${N}" stroke-width="7"/></g><g transform="rotate(${f1(a)})"><rect x="0" y="-28" width="${w}" height="56" rx="10" fill="#b7c3d3" stroke="${N}" stroke-width="7"/></g><circle r="34" fill="#9aa8bb" stroke="${N}" stroke-width="7"/></g>`; };
const sparks = (cx, cy, d) => { if (d < 0 || d > 0.6) return ''; let s = ''; seed(5); for (let i = 0; i < 14; i++) { const a = rnd() * Math.PI * 2, r0 = 40 + d * 600 * (0.6 + rnd() * 0.6); s += `<path d="M${f1(cx + Math.cos(a) * r0)} ${f1(cy + Math.sin(a) * r0)} l${f1(Math.cos(a) * 50)} ${f1(Math.sin(a) * 50)}" stroke="${K.yellow}" stroke-width="10" stroke-linecap="round" opacity="${f1(1 - d / 0.6)}"/>`; } return s; };
const s05h = t => { const tb = hat('s05', 'bite') - 0.05, cl = sm(tb - 0.12, tb, t), o = lerp(200, 30, cl), sx = shake(t, tb, 18);
  let s = `<g transform="translate(${f1(sx)} 0)">` + bar(540, 1050, sm(tb, tb + 0.15, t)) + jaws(540, 1050, 420, o) + '</g>' + sparks(540, 1050, t - tb) + flash(t, tb);
  if (t < tb) s += big(540, 1560, 'HOW HARD?', t, -1, { size: 120, fill: '#fff', stroke: N, sw: 14 }); else s += big(540, 1560, 'CRUNCH!', t, tb, { size: 140, fill: K.red, stroke: '#fff', sw: 14 });
  return s; };
const s05a = t => { const te = at('n09', 'eighteen thousand'), th = at('n09', 'A strong human'), tx = at('n09', 'eighteen times'); let s = '';
  if (t < te - 0.3) { const ch = 0.5 + 0.5 * Math.sin(t * 7); s += jaws(540, 1050, 380, lerp(30, 170, ch)) + big(540, 1560, 'HOW HARD?', t, -1, { size: 120, fill: '#fff', stroke: N, sw: 14 }); return s; }
  const base = 1420, scale = 820 / 18000, xs = 740, xh = 330, bw = 260, hs = 18000 * eo(te - 0.3, te + 1.4, t), hh = 1000 * eo(th, th + 0.6, t);
  s += `<path d="M120 ${base} L960 ${base}" stroke="#fff" stroke-width="12" stroke-linecap="round"/><rect x="${xs - bw / 2}" y="${f1(base - hs * scale)}" width="${bw}" height="${f1(hs * scale)}" rx="18" fill="${K.red}" stroke="${N}" stroke-width="9"/>`;
  s += big(xs, base - hs * scale - 40, hs >= 17950 ? '18,000' : Math.round(hs).toLocaleString('en-US'), t, te - 0.3, { size: 92, stroke: N, sw: 12 }) + big(xs, base + 95, 'SHARK', t, te - 0.3, { size: 80, fill: K.yellow, stroke: N, sw: 12 });
  if (t > th) s += `<rect x="${xh - bw / 2}" y="${f1(base - Math.max(hh * scale, 2))}" width="${bw}" height="${f1(Math.max(hh * scale, 2))}" rx="12" fill="#fff" stroke="${N}" stroke-width="9"/>` + big(xh, base - hh * scale - 40, Math.round(hh).toLocaleString('en-US'), t, th, { size: 92, stroke: N, sw: 12 }) + big(xh, base + 95, 'YOU', t, th, { size: 80, fill: K.yellow, stroke: N, sw: 12 });
  s += big(330, 760, '×18', t, tx, { size: 230, fill: K.yellow, stroke: N, sw: 18 });
  return s; };
const s05b = t => { const tb = at('n07b', 'bite off') - 0.05, tw = at('n07b', 'swallow'), cl = sm(tb - 0.12, tb, t) * (1 - sm(tb + 0.25, tb + 0.5, t)), o = lerp(210, 40, cl);
  const sw = eo(tw, tw + 0.8, t), mx = 540, my = 1060 + 330 * sw, msc = (1 - 0.7 * sw) * (t > tb ? 0.62 : 1);
  let s = big(540, 560, 'NO CHEWING!', t, 0, { size: 120, fill: K.yellow, stroke: N, sw: 16 });
  s += `<g opacity="${f1(1 - sm(0.6, 1, sw))}" transform="translate(${mx} ${f1(my)}) scale(${f1(msc * 100) / 100})"><path d="M-210 -90 Q0 -150 210 -90 Q250 0 210 90 Q0 140 -210 90 Q-250 0 -210 -90Z" fill="#e8746b" stroke="${N}" stroke-width="9"/><path d="M-120 -40 Q0 -70 120 -40 M-140 30 Q0 0 140 30" stroke="#f6b3a8" stroke-width="16" fill="none" stroke-linecap="round"/></g>`;
  s += jaws(540, 1060, 420, o) + flash(t, tb, 0.18);
  s += big(540, 1560, 'GULP!', t, tw + 0.1, { size: 150, fill: '#fff', stroke: N, sw: 16 });
  return s; };

// ───────── s06 BREACH ─────────
const WL6 = 1250;
const flyShark = (x, y, rot, sc = 0.64) => `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(rot)}) scale(${sc}) translate(-985 -212)"><path d="${SHARK}" fill="#fff" stroke="${N}" stroke-width="${f1(7 / sc)}"/><circle cx="905" cy="190" r="12" fill="${N}"/></g>`;
const water6 = (t, inner) => `<rect x="0" y="${WL6}" width="${W}" height="${H - WL6}" fill="${K.deep}" opacity=".55"/>` + inner + `<rect x="0" y="${WL6}" width="${W}" height="${H - WL6}" fill="${K.deep}" opacity=".25"/>` + wave(WL6, t);
// rise from the deep, break the surface at tb, ballistic arc (slow-mo), back in at tr
const breach = (t, t0, tb, { slo = 0.55, freeze = 1e9 } = {}) => { const G = 1500, VY = 1000, VX = 450; let x, y, rot;
  const tt = Math.min(t, freeze);
  if (tt < tb) { const k = Math.pow(clamp((tt - t0) / (tb - t0)), 1.5); x = lerp(260, 300, k); y = lerp(1900, WL6 - 30, k); rot = -84; }
  else { const d = (tt - tb) * slo; x = 300 + VX * d; y = WL6 - 30 - VY * d + 0.5 * G * d * d; rot = Math.atan2(-VY + G * d, VX) * 180 / Math.PI; }
  const tr = tb + 2 * VY / G / slo, xr = 300 + VX * 2 * VY / G;
  let s = flyShark(x, y, rot);
  if (tt < tb) for (let i = 0; i < 5; i++) s += `<path d="M${f1(x - 120 + i * 60)} ${f1(y + 330)} l0 ${f1(140 + 40 * (i % 2))}" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity=".5"/>`;
  return { s, splash: splash(300, WL6, t - tb, 1.3, 15) + splash(xr, WL6, t - tr, 0.8, 27) }; };
const s06h = t => { const tb = 0.75, fr = 1.95, b = breach(t, -3.5, tb, { freeze: fr });
  let s = water6(t, b.s) + b.splash;
  if (t > fr) s += `<rect width="${W}" height="${H}" fill="${N}" opacity=".18"/>` + big(820, 860, '?!', t, fr, { size: 220, fill: K.yellow, stroke: N, sw: 16 });
  return s; };
const s06a = t => { const tc = at('n15', 'Off the coast'); let s = '';
  if (t < tc - 0.15) { const cx = 540, cy = 1060, r = 360, t0 = at('n15', 'swish'), v = 40 * eo(t0, at('n15', 'forty') + 0.8, t) + (t > at('n15', 'forty') + 0.8 ? Math.sin(t * 14) * 0.7 : 0);
    const a0 = Math.PI * 1.1, a1 = -Math.PI * 0.1, ang = x => lerp(a0, a1, x / 50), av = ang(Math.max(0, v));
    s += `<path d="M${f1(cx + r * Math.cos(a0))} ${f1(cy - r * Math.sin(a0))} A${r} ${r} 0 1 1 ${f1(cx + r * Math.cos(a1))} ${f1(cy - r * Math.sin(a1))}" fill="none" stroke="#fff" stroke-width="56" opacity=".3"/>`;
    if (v > 0.2) s += `<path d="M${f1(cx + r * Math.cos(a0))} ${f1(cy - r * Math.sin(a0))} A${r} ${r} 0 ${a0 - av > Math.PI ? 1 : 0} 1 ${f1(cx + r * Math.cos(av))} ${f1(cy - r * Math.sin(av))}" fill="none" stroke="${K.yellow}" stroke-width="56"/>`;
    s += `<path d="M${cx} ${cy} L${f1(cx + (r - 80) * Math.cos(av))} ${f1(cy - (r - 80) * Math.sin(av))}" stroke="${N}" stroke-width="24" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="40" fill="${N}"/>`;
    s += big(cx, cy + 260, Math.max(0, Math.round(v)) + ' KM/H', t, -1, { size: 150, stroke: N, sw: 14 });
    s += `<g transform="rotate(${f1(t > t0 ? 7 * Math.sin((t - t0) * 9) * Math.exp(-(t - t0) * 0.5) : 0)} 700 620)">${place(540, 620, 0.42, sharkSolid('#fff', N, 16))}</g>`;
    return s; }
  const t0 = at('n15', 'shoot up'), tb = at('n15', 'fly right out'), b = breach(t, t0 - 0.6, tb);
  const ks = eo(tb - 0.35, tb + 0.45, t), kd = eo(tb + 0.45, tb + 1.2, t), sx = 520 + 200 * ks, sy = WL6 - 18 - 220 * Math.sin(Math.PI * ks) + 260 * kd;
  s += water6(t, b.s + `<g opacity="${f1(1 - sm(0.5, 1, kd))}" transform="translate(${f1(sx)} ${f1(sy)}) rotate(${f1(-25 * Math.sin(Math.PI * ks) + 40 * kd)}) scale(-1.0 1.0)">${ICON.seal()}</g>`) + b.splash;
  s += big(540, 1420, '2 TONS', t, at('n15', 'Two tons'), { size: 150, stroke: N, sw: 14 }) + big(540, 1560, 'IN THE AIR!', t, at('n15', 'in the air'), { size: 120, fill: K.yellow, stroke: N, sw: 14 });
  return s; };

// ───────── s07 ELECTRIC SENSE ─────────
const HCX = -432, HCY = 1036, HSC = 2.4;
const snout = (t, pk, ek) => { let s = place(HCX, HCY, HSC, sharkSolid('#dfe6f0', N, 3.5)); seed(20);
  for (let i = 0; i < 46; i++) { const bx = 925 + rnd() * 55, by = 198 + rnd() * 26 - (bx - 925) * 0.12; if (bx > 978) continue; const [X, Y] = toScr(HCX, HCY, HSC, bx, by);
    s += `<circle cx="${f1(X)}" cy="${f1(Y)}" r="${f1(6 + 5 * ek * Math.max(0, Math.sin(t * 8 + i)))}" fill="${ek > 0.5 ? K.yellow : N}" opacity="${f1(pk)}"/>`; }
  return s; };
const zap = (t, x0, y0, x1, y1, sd) => { seed(sd + Math.floor(t * 12)); let d = `M${x0} ${y0}`; for (let i = 1; i < 7; i++) { const u = i / 7; d += ` L${f1(lerp(x0, x1, u) + (rnd() - 0.5) * 60)} ${f1(lerp(y0, y1, u) + (rnd() - 0.5) * 60)}`; } return `<path d="${d} L${x1} ${y1}" stroke="${K.yellow}" stroke-width="10" fill="none" stroke-linejoin="round"/><path d="${d} L${x1} ${y1}" stroke="#fff" stroke-width="4" fill="none"/>`; };
const s07h = t => { const te = hat('s07', 'electricity'); let s = snout(t, 1, t > te - 0.2 ? 1 : 0);
  const [X, Y] = toScr(HCX, HCY, HSC, 955, 205);
  if (t > te - 0.2) { s += zap(t, 1000, 640, X + 20, Y - 20, 3) + zap(t, 1000, 1500, X + 20, Y + 30, 9); s += icon('bolt', 860, 640, 1.4, t, te - 0.2); }
  s += big(540, 1560, t > te - 0.2 ? 'ZAP!' : 'LOOK CLOSER', t, -1, { size: 120, fill: t > te - 0.2 ? K.yellow : '#fff', stroke: N, sw: 14 });
  return s; };
const s07a = t => { const te = at('n20', 'Every living'); let s = '';
  if (t < te - 0.15) { const td = at('n20', 'dots'), tf = at('n20', 'feel electricity');
    s += snout(t, Math.max(0.35, sm(td, td + 0.6, t)), sm(tf, tf + 0.4, t));
    s += tag(...toScr(HCX, HCY, HSC, 955, 205), 300, 640, 'PORES', t, at('n20', 'tiny pores'), { col: '#fff', size: 80 });
    s += big(540, 1560, 'FULL OF JELLY', t, at('n20', 'filled with jelly'), { size: 110, fill: '#fff', stroke: N, sw: 14 });
    if (t > tf) s = s.replace(/FULL OF JELLY/, 'ZAP SENSE!');
    if (t > tf) s += icon('bolt', 860, 640, 1.4, t, tf);
    return s; }
  const sy = 1250, fx = 720, ek = sm(te, te + 0.5, t), tc = at('n20', "can't hide"), u = eo(at('n20', 'So even'), tc + 0.6, t);
  s += `<rect x="0" y="${sy}" width="${W}" height="${H - sy}" fill="${K.sand}"/><path d="M0 ${sy} ${Array.from({ length: 16 }, (_, i) => `L${i * 80} ${sy + 10 * Math.sin(i)}`).join(' ')}" stroke="${N}" stroke-width="6" fill="none"/>`;
  for (let i = 0; i < 4; i++) { const r = ((t * 120 + i * 80) % 320); s += `<ellipse cx="${fx}" cy="${sy + 60}" rx="${f1(r * 1.3)}" ry="${f1(r)}" fill="none" stroke="${K.yellow}" stroke-width="8" opacity="${f1(ek * (1 - r / 320))}"/>`; }
  s += `<g transform="translate(${fx} ${sy + 70}) scale(1.6)"><path d="M-90 0 C-50 -55 50 -55 90 0" fill="#c9a86a" stroke="${N}" stroke-width="6"/><circle cx="-40" cy="-22" r="10" fill="#fff" stroke="${N}" stroke-width="4"/><circle cx="-40" cy="-22" r="4" fill="${N}"/></g>`;
  s += place(lerp(80, fx - 330, u), lerp(620, 960, u), 0.62, sharkSolid('#fff', N, 11), { rot: lerp(10, 32, u) });
  s += tag(fx, sy + 40, 780, 1520, 'HIDDEN FISH', t, at('n20', 'a fish hiding'), { col: '#fff', size: 72 });
  s += big(540, 620, 'FOUND YOU!', t, tc, { size: 140, fill: K.yellow, stroke: N, sw: 14 });
  return s; };
const s07b = t => { const st = [['SMELL', 'smell', at('n25', 'it smells'), K.cyan], ['FEEL', 'wave', at('n25', 'feels the movement'), '#fff'], ['SEE', 'eye', at('n25', 'it sees'), '#fff'], ['ZAP!', 'bolt', at('n25', 'uses electricity'), K.yellow]];
  const cur = st.reduce((a, x, i) => t > x[2] ? i : a, -1); let s = '';
  st.forEach(([n, ic, tn, c], i) => { const x = 300 + (i % 2) * 480, y = 640 + Math.floor(i / 2) * 400, on = i === cur, k = pop(tn, t);
    if (k <= 0) { s += `<rect x="${x - 170}" y="${y - 170}" width="340" height="340" rx="40" fill="#fff" opacity=".14"/><text x="${x}" y="${y + 40}" font-family="Black" font-size="120" fill="#fff" opacity=".35" text-anchor="middle">${i + 1}</text>`; return; }
    s += `<g transform="translate(${x} ${y}) scale(${f1((on ? 1.08 : 0.92) * k * 100) / 100})"><rect x="-170" y="-170" width="340" height="340" rx="40" fill="${on ? N : '#2f6fa8'}" stroke="${on ? K.yellow : '#fff'}" stroke-width="10"/><g transform="translate(0 -30) scale(${ic === 'eye' ? 1.1 : 0.9})">${ICON[ic](c)}</g><text y="130" font-family="Black" font-size="64" fill="#fff" text-anchor="middle">${n}</text></g>`; });
  const u = eo(st[0][2] - 0.5, st[3][2] + 1, t), px = 800, tc = at('n25', 'aim the bite') - 0.5, ly = 1430;
  const fx = px + 700 * Math.pow(clamp((t - tc) / 0.7), 1.6), fy = ly + (t > tc ? 24 * Math.sin((t - tc) * 30) : 0), sx = lerp(-80, px - 250, u) + 1000 * Math.pow(clamp((t - tc - 0.15) / 0.8), 1.7);
  s += place(sx, ly, 0.36, sharkSolid('#fff', N, 16)) + `<g transform="translate(${f1(fx)} ${f1(fy)}) rotate(${t > tc ? f1(12 * Math.sin((t - tc) * 30)) : 0}) scale(-.7 .7)">${ICON.fish()}</g>`;
  return s; };

// ───────── s08 EYES ─────────
const ECX = -816, ECY = 1080, ESC = 3.2;
const headEye = (t, roll, bite) => { let g = `<path d="${SHARK}" fill="#fff" stroke="${N}" stroke-width="3" stroke-linejoin="round"/>`;
  g += [0, 1, 2, 3, 4].map(i => `<path d="M${716 + i * 17} 178 C${722 + i * 17} 210 ${720 + i * 17} 240 ${712 + i * 17} 258" stroke="${N}" stroke-width="3" fill="none" opacity=".5"/>`).join('');
  const jo = 6 + 34 * bite;
  g += `<path d="M880 236 C905 ${f1(236 + jo * 0.6)} 935 ${f1(236 + jo)} 972 ${f1(228 + jo * 0.6)} L980 226 C950 232 915 234 880 236Z" fill="#3a0f1e" stroke="${N}" stroke-width="3"/>`;
  for (let i = 0; i < 6; i++) { const x = 900 + i * 12; g += `<path d="M${x} 234 l5 ${f1(6 + jo * 0.15)} l5 -${f1(6 + jo * 0.15)}Z" fill="#fff"/>`; }
  g += `<defs><clipPath id="ey8"><circle cx="905" cy="190" r="14"/></clipPath></defs><circle cx="905" cy="190" r="14" fill="${N}"/><g clip-path="url(#ey8)"><circle cx="${f1(905 + 30 * (1 - roll) + 3 * roll)}" cy="190" r="14" fill="#f2f2ea"/></g><circle cx="905" cy="190" r="14" fill="none" stroke="${N}" stroke-width="3"/>`;
  let s = place(ECX, ECY, ESC, g); const [ex, ey] = toScr(ECX, ECY, ESC, 905, 190);
  if (roll > 0 && roll < 1) s += `<path d="M${f1(ex + 90)} ${f1(ey - 80)} A110 110 0 0 0 ${f1(ex - 90)} ${f1(ey - 80)}" stroke="${K.yellow}" stroke-width="14" fill="none" stroke-linecap="round" opacity="${f1(Math.sin(Math.PI * roll))}"/>`;
  return { s, ex, ey }; };
const s08h = t => { const tr = hat('s08', 'roll'), tb = hat('s08', 'bites'), roll = eo(tr, tr + 0.6, t), bite = sm(tb - 0.2, tb + 0.1, t);
  const h = headEye(t, roll, bite); let s = h.s;
  s += `<circle cx="${f1(h.ex)}" cy="${f1(h.ey)}" r="${f1(90 + 10 * Math.sin(t * 6))}" fill="none" stroke="${K.yellow}" stroke-width="10" stroke-dasharray="24 16"/>`;
  s += big(540, 1560, 'EYES?!', t, -1, { size: 130, fill: K.yellow, stroke: N, sw: 14 });
  return s; };
const s08a = t => { const tr = at('n23', 'And right when'); let s = '';
  if (t < tr - 0.15) { const cx = 540, cy = 1000, R = 330, rk = sm(at('n23', 'mirror'), at('n23', 'mirror') + 0.5, t);
    s += `<circle cx="${cx}" cy="${cy}" r="${R}" fill="#16304f" stroke="#fff" stroke-width="12"/><path d="M${cx - R * 0.5} ${cy - R * 0.866} A${R} ${R} 0 0 0 ${cx - R * 0.5} ${cy + R * 0.866}" stroke="#e6f6ff" stroke-width="40" fill="none" stroke-linecap="round"/><ellipse cx="${cx + R - 90}" cy="${cy}" rx="80" ry="110" fill="#bfe8ff" opacity=".8" stroke="${N}" stroke-width="6"/>`;
    for (let i = -2; i <= 2; i++) { const yy = cy + i * 55, ph = ((t * 0.6 + i * 0.13) % 1 + 1) % 1, xb = cx - R + 40, xin = lerp(1100, xb, Math.min(1, ph * 2));
      s += `<path d="M1100 ${yy} L${f1(xin)} ${yy}" stroke="${K.yellow}" stroke-width="10" stroke-linecap="round" opacity=".9"/>`;
      if (ph > 0.5) s += `<path d="M${xb} ${yy} L${f1(lerp(xb, 1100, (ph - 0.5) * 2))} ${f1(yy - i * 30 * (ph - 0.5))}" stroke="#fff" stroke-width="8" stroke-dasharray="20 14" opacity="${f1(rk)}"/>`; }
    s += tag(cx - R + 20, cy - 160, 260, 600, 'MIRROR', t, at('n23', 'mirror'), { col: '#fff', size: 80 }) + big(540, 1500, 'SEES IN THE DARK', t, at('n23', 'dark water'), { size: 96, fill: K.yellow, stroke: N, sw: 12 });
    return s; }
  const tro = at('n23', 'rolls its eyes'), roll = eo(tro, tro + 0.7, t), tb = at('n23', 'it bites blind'), bite = sm(tb - 0.3, tb, t) * (1 - sm(tb + 0.6, tb + 1.0, t));
  const h = headEye(t, roll, bite); s += h.s + tag(h.ex, h.ey - 60, 540, 600, 'EYES ROLL BACK', t, tro, { col: '#fff', size: 76 });
  s += big(540, 1560, 'BITES BLIND!', t, tb, { size: 140, fill: K.red, stroke: '#fff', sw: 16 }) + flash(t, tb, 0.2);
  return s; };

// screen point of a long-form shark point inside place(..., {rot})
const rotScr = (cx, cy, sc, x, y, rot) => { const a = rot * Math.PI / 180, dx = (x - 500) * sc, dy = (y - 215) * sc; return [cx + dx * Math.cos(a) - dy * Math.sin(a), cy + dx * Math.sin(a) + dy * Math.cos(a)]; };
const ring = (x, y, t, c = K.yellow) => { let s = ''; for (let i = 0; i < 3; i++) { const u = (t * 0.9 + i / 3) % 1; s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(40 + 140 * u)}" fill="none" stroke="${c}" stroke-width="8" opacity="${f1(1 - u)}"/>`; } return s; };

// ───────── s09 SPIRAL VALVE ─────────
const s09h = t => { const cx = 540, cy = 1060, sc = 1.15, [X, Y] = rotScr(cx, cy, sc, ...PT.valve, -90);
  let s = place(cx, cy, sc, sharkInside({}, N, 5), { rot: -90 }) + ring(X, Y, t, K.purple) + `<circle cx="${f1(X)}" cy="${f1(Y)}" r="${f1(36 + 6 * Math.sin(t * 7))}" fill="${K.purple}" stroke="#fff" stroke-width="7"/>`;
  return s + tag(X, Y, 850, Y - 160, '???', t, -1, { col: K.purple, txt: '#fff', size: 100 }); };
const s09a = t => { const tg = at('n19', "And here's a gross"); let s = '';
  if (t < tg - 0.15) { const tv = at('n19', 'something really weird'), vx = 540, y0 = 680, y1 = 1440, vw = 320, turns = 6, k = 0.3 + 0.7 * eo(tv - 0.4, tv + 1.4, t);
    s += `<rect x="${vx - vw / 2}" y="${y0}" width="${vw}" height="${y1 - y0}" rx="${vw / 2}" fill="#f3e8ff" stroke="${N}" stroke-width="10"/>`;
    let back = '', front = ''; const h = (y1 - y0 - 160) / turns;
    for (let i = 0; i < turns; i++) { const y = y0 + 80 + i * h;
      back += `<path d="M${vx + vw / 2 - 22} ${f1(y)} C${vx} ${f1(y + h * 0.2)} ${vx - vw / 2 + 22} ${f1(y + h * 0.3)} ${vx - vw / 2 + 22} ${f1(y + h * 0.5)}" stroke="#c9b4ec" stroke-width="24" fill="none" stroke-linecap="round"/>`;
      front += `<path d="M${vx - vw / 2 + 22} ${f1(y + h * 0.5)} C${vx - vw / 2 + 22} ${f1(y + h * 0.7)} ${vx} ${f1(y + h * 0.8)} ${vx + vw / 2 - 22} ${f1(y + h)}" stroke="${K.purple}" stroke-width="28" fill="none" stroke-linecap="round"/>`; }
    s += `<defs><clipPath id="v9"><rect x="${vx - vw / 2 - 20}" y="${y0}" width="${vw + 40}" height="${f1((y1 - y0) * k)}"/></clipPath></defs><g clip-path="url(#v9)">${back}${front}</g>`;
    const tf = at('n19', 'so food spins');
    if (t > tf - 0.3) { const u = ((t - tf + 0.3) * 0.16) % 1, y = y0 + 80 + u * (y1 - y0 - 160), x = vx - Math.cos(u * turns * 2 * Math.PI) * (vw / 2 - 44); s += `<circle cx="${f1(x)}" cy="${f1(y)}" r="34" fill="${K.yellow}" stroke="${N}" stroke-width="7"/>`; }
    const to = at('n19', 'Instead of a long tube');
    if (t > to && t < tf + 0.5) { const k2 = pop(to, t); s += `<g transform="translate(870 1060) scale(${f1(k2 * 100) / 100})"><rect x="-50" y="-300" width="100" height="600" rx="50" fill="#ffd2c4" stroke="${N}" stroke-width="8"/></g>` + big(870, 1420, 'OURS', t, to, { size: 64, stroke: N, sw: 10 }); }
    s += big(540, 600, 'SPIRAL VALVE', t, at('n19', 'spiral valve'), { size: 110, fill: '#fff', stroke: N, sw: 14 });
    s += big(540, 1580, 'CORKSCREW!', t, at('n19', 'corkscrew'), { size: 120, fill: K.yellow, stroke: N, sw: 14 });
    return s; }
  const tp = at('n19', 'push their stomach'), out = sm(tp, tp + 1, t) * (1 - sm(at('n19', 'pull it back'), at('n19', 'pull it back') + 1, t));
  s += place(ECX, ECY, ESC, sharkSolid('#fff', N, 3)); const [mx, my] = toScr(ECX, ECY, ESC, 975, 232);
  if (out > 0.01) s += `<g transform="translate(${f1(mx - 30)} ${f1(my)}) rotate(40) scale(${f1(out * 120) / 100})"><path d="M0 0 C120 -60 300 -40 320 40 C330 120 160 140 0 30Z" fill="${K.purple}" stroke="${N}" stroke-width="9"/></g>`;
  s += big(540, 640, 'EWW!', t, at('n19', 'gross one'), { size: 200, fill: K.green, stroke: N, sw: 16, rot: -6 });
  s += tag(mx + 120 * out, my + 200 * out, 600, 1540, 'ITS STOMACH', t, tp + 0.4, { col: K.purple, txt: '#fff', size: 80 });
  return s; };

// ───────── s10 KEEP SWIMMING ─────────
const GCX = -160, GCY = 1000, GSC = 2.0;
const gills = (t, speed, wk, gk = 1) => { const y = GCY + bob(t, 4) * speed; let s = place(GCX, y, GSC, sharkSolid('#fff', N, 4));
  s += place(GCX, y, GSC, [0, 1, 2, 3, 4].map(i => `<path d="M${716 + i * 17} 178 C${722 + i * 17} 210 ${720 + i * 17} 240 ${712 + i * 17} 258" stroke="${K.red}" stroke-width="7" fill="none" opacity="${f1(gk)}" stroke-linecap="round"/>`).join(''));
  if (wk > 0) { seed(16); for (let i = 0; i < 30; i++) { const ph = rnd(), yo = rnd() * 36 - 18, u = (ph + t * 0.3 * speed) % 1, bx = lerp(1040, 680, u), by = 232 + yo + (u > 0.55 ? (u - 0.55) * 70 : 0), [X, Y] = toScr(GCX, y, GSC, bx, by);
      s += `<circle cx="${f1(X)}" cy="${f1(Y)}" r="11" fill="${u > 0.62 ? '#fff' : K.cyan}" stroke="${N}" stroke-width="3" opacity="${f1(wk * (0.3 + 0.7 * speed))}"/>`; } }
  return s; };
const stopSign = (x, y, k) => `<g transform="translate(${x} ${y}) scale(${f1(k * 100) / 100})"><path d="M-110 -265 L110 -265 L265 -110 L265 110 L110 265 L-110 265 L-265 110 L-265 -110Z" transform="scale(.6)" fill="${K.red}" stroke="#fff" stroke-width="14"/><text y="38" font-family="Black" font-size="104" fill="#fff" text-anchor="middle">STOP</text></g>`;
const s10h = t => { const ts = hat('s10', 'stops'), st = sm(ts, ts + 0.8, t), sink = 160 * eo(ts + 0.3, ts + 2.2, t);
  let s = `<g transform="translate(0 ${f1(sink)}) rotate(${f1(8 * sm(ts + 0.3, ts + 2, t))} 540 1000)">${gills(t, 1 - st, 1, 0.6)}</g>`;
  s += stopSign(780, 650, pop(ts, t)) + big(540, 1580, t > ts ? '...?' : 'SWIM!', t, -1, { size: 130, fill: K.yellow, stroke: N, sw: 14 });
  return s; };
const s10a = t => { const ts = at('n16', 'If it stops'), st = sm(ts, ts + 1, t), wk = sm(at('n16', 'Water goes in'), at('n16', 'Water goes in') + 0.4, t);
  let s = gills(t, 1 - st, Math.max(0.4, wk));
  s += tag(...toScr(GCX, GCY, GSC, 750, 178), 300, 660, 'GILLS', t, Math.max(0.2, at('n16', 'over the gills') - 0.2), { col: K.red, txt: '#fff', size: 80 });
  s += big(760, 700, 'O₂', t, at('n16', 'pull oxygen'), { size: 170, fill: K.cyan, stroke: N, sw: 14 });
  if (t < ts) s += big(540, 1580, 'KEEP SWIMMING', t, at('n16', 'keep swimming'), { size: 100, fill: K.yellow, stroke: N, sw: 14 });
  else s += stopSign(780, 660, pop(ts, t)) + big(540, 1580, "CAN'T BREATHE!", t, at('n16', "can't breathe"), { size: 100, fill: K.red, stroke: '#fff', sw: 14 });
  return s; };

// ───────── s11 WARM SHARK ─────────
const thermal = (cx, cy, sc, w, rot = 0) => place(cx, cy, sc, `<defs><radialGradient id="th11" cx=".45" cy=".55" r=".5"><stop offset="0" stop-color="#fff6c0"/><stop offset=".3" stop-color="#ffcf3a"/><stop offset=".6" stop-color="#ff5a2a"/><stop offset="1" stop-color="#3a3cc8"/></radialGradient><clipPath id="c11"><path d="${SHARK}"/></clipPath></defs><path d="${SHARK}" fill="#3a3cc8"/><rect width="1000" height="400" fill="url(#th11)" clip-path="url(#c11)" opacity="${f1(w)}"/><path d="${SHARK}" fill="none" stroke="#fff" stroke-width="${f1(6 / sc)}"/>`, { rot });
const thermo = (x, y0, y1, lv) => `<rect x="${x - 40}" y="${y1 - 40}" width="80" height="${y0 - y1 + 40}" rx="40" fill="#fff" stroke="${N}" stroke-width="8"/><circle cx="${x}" cy="${y0 + 40}" r="80" fill="${K.red}" stroke="${N}" stroke-width="8"/><rect x="${x - 22}" y="${f1(lerp(y0 - 100, y1, lv))}" width="44" height="${f1(y0 + 40 - lerp(y0 - 100, y1, lv))}" fill="${K.red}"/>`;
const ocean = `<rect x="0" y="0" width="${W}" height="${H}" fill="#2a2e9e" opacity=".55"/>`;
const s11h = t => ocean + thermal(470, 1060, 1.12, 1, -90) + thermo(870, 1320, 760, 0.5 + 0.4 * eo(0.2, 2.2, t)) + big(870, 680, '+14°C', t, -1, { size: 90, fill: '#ffcf3a', stroke: N, sw: 12 });
const s11a = t => { const tw = at('n18', 'But a great white'), t14 = at('n18', 'fourteen degrees'), tf = at('n18', 'fast muscles'); let s = ocean;
  if (t < tw - 0.15) { s += big(540, 640, 'MOST FISH', t, -1, { size: 120, stroke: N, sw: 14 }) + `<g transform="translate(540 1000) scale(2.8)">${ICON.fish('#5a8cff')}</g>` + big(540, 1420, 'COLD', t, at('n18', 'as cold'), { size: 170, fill: K.cyan, stroke: N, sw: 14 });
    seed(4); for (let i = 0; i < 8; i++) { const x = 140 + rnd() * 800, y = 760 + rnd() * 520, k = pop(at('n18', 'water around') + i * 0.05, t); if (k > 0) s += `<g transform="translate(${f1(x)} ${f1(y)}) scale(${f1(k * 0.5)})"><path d="M0 -60 L0 60 M-52 -30 L52 30 M-52 30 L52 -30" stroke="#dff6ff" stroke-width="14" stroke-linecap="round"/></g>`; }
    return s; }
  const w = sm(tw, tw + 1.5, t), lv = eo(t14, t14 + 1.4, t);
  s += thermal(540, 980 + bob(t, 5), 1.0, w) + big(540, 640, 'WARM', t, tw + 0.5, { size: 170, fill: '#ffcf3a', stroke: N, sw: 14 });
  s += `<g transform="translate(220 1360) rotate(90)">${thermo(0, 0, -600, lv)}</g>` + big(540, 1250, '+14°C', t, t14, { size: 110, fill: '#fff', stroke: N, sw: 12 });
  s += big(540, 1580, 'WARM = FAST!', t, tf, { size: 120, fill: K.yellow, stroke: N, sw: 14 });
  return s; };

// ───────── s12 OLDER THAN TREES ─────────
const s12h = t => { const tt = hat('s12', 'trees'); let s = `<rect x="0" y="480" width="${W}" height="560" fill="#c9a87a" opacity=".85"/><path d="M0 1040 ${Array.from({ length: 15 }, (_, i) => `L${i * 80} ${f1(1040 - 40 * Math.abs(Math.sin(i * 1.7)))}`).join(' ')} L1080 1040Z" fill="#a8835a"/>`;
  s += `<rect x="0" y="1040" width="${W}" height="${H - 1040}" fill="${K.deep}" opacity=".5"/>` + wave(1040, t) + place(lerp(420, 640, sm(0, 3.5, t)), 1300, 0.62, sharkSolid('#fff', N, 11));
  if (t > tt - 0.1) s += icon('tree', 540, 760, 1.3, t, tt - 0.1) + cross(540, 760, 170, t, tt + 0.3);
  s += big(540, 1620, 'NO TREES YET', t, -1, { size: 100, fill: K.yellow, stroke: N, sw: 14 });
  return s; };
const s12a = t => { const ts = at('n27', 'Sharks have been'), tt = at('n27', 'older than trees'), td = at('n27', 'dinosaurs'), x0 = 170;
  let s = `<path d="M${x0} 1560 L${x0} 600" stroke="#fff" stroke-width="14" stroke-linecap="round"/><path d="M${x0 - 34} 610 L${x0} 540 L${x0 + 34} 610Z" fill="#fff"/>` + big(x0, 500, 'NOW', t, -1, { size: 60, stroke: N, sw: 10 });
  const row = (y, label, sub, k0, art) => { if (t < k0) return ''; return `<circle cx="${x0}" cy="${y}" r="22" fill="${K.yellow}" stroke="${N}" stroke-width="6"/>` + art + big(x0 + 60, y - 36, label, t, k0, { size: 76, stroke: N, sw: 12, anchor: 'start' }) + big(x0 + 60, y + 40, sub, t, k0 + 0.15, { size: 54, fill: K.yellow, stroke: N, sw: 10, anchor: 'start' }); };
  s += row(1460, 'SHARKS', '400M+ YEARS', ts, place(840, 1440, 0.36, sharkSolid('#fff', N, 18)));
  s += row(1150, 'TREES', 'LATER', tt, icon('tree', 860, 1110, 0.9, t, tt));
  s += row(840, 'DINOSAURS', 'MUCH LATER', td, icon('dino', 840, 820, 0.8, t, td));
  s += big(540, 1650, 'OLDER THAN TREES!', t, tt + 0.5, { size: 84, fill: K.yellow, stroke: N, sw: 12 });
  return s; };

// ───────── s13 BORN READY ─────────
const baby = (x, y, sc, t, grin = 1) => { const [jx, jy] = [930, 236]; let g = sharkSolid('#fff', N, 6 / sc * 0.6);
  if (grin > 0) { g += `<path d="M860 236 Q920 ${f1(236 + 28 * grin)} 978 228" fill="#3a0f1e" stroke="${N}" stroke-width="4"/>`; for (let i = 0; i < 8; i++) g += `<path d="M${868 + i * 13} ${f1(236 - i * 0.6)} l6 ${f1(10 * grin)} l6 -${f1(10 * grin)}Z" fill="#fff" stroke="${N}" stroke-width="1.5"/>`; }
  return place(x, y, sc, g); };
const s13h = t => { const tr = hat('s13', 'ready'), tc = hat('s13', 'hunt') + 0.1, u = eo(0, 3.2, t), fx = 860 + 30 * Math.sin(t * 5), fy = 980 + 20 * Math.sin(t * 3);
  let s = baby(lerp(330, 430, u), 1060, 0.78, t, 1) + `<g transform="translate(${f1(fx)} ${f1(fy)}) scale(-0.7 0.7)">${ICON.fish()}</g>`;
  s += `<g transform="translate(${f1(fx)} ${f1(fy)}) rotate(${f1(t * 40)})" opacity="${f1(Math.max(0.6, sm(tc - 0.3, tc, t)))}"><circle r="90" fill="none" stroke="${K.red}" stroke-width="10"/><path d="M-130 0 L-60 0 M60 0 L130 0 M0 -130 L0 -60 M0 60 L0 130" stroke="${K.red}" stroke-width="10" stroke-linecap="round"/></g>`;
  s += tag(...toScr(lerp(330, 430, u), 1060, 0.78, 560, 230), 330, 1460, 'BABY', t, -1, { col: K.yellow, size: 84 });
  return s; };
const s13a = t => { const ts = at('n26', 'swim off'), tm = at('n26', 'more than a meter'), tt = at('n26', 'full set'), to = at('n26', 'on their own'); let s = '';
  const u = eo(ts, ts + 3, t), bx = lerp(560, 1700, u * u), sc = 0.66;
  if (t < tt - 0.1) { const k = pop(tm, t); s += `<g opacity="${f1(k > 0 ? 1 : 0)}"><path d="M${560 - 1000 * sc / 2} 1270 L${560 + 1000 * sc / 2} 1270" stroke="#fff" stroke-width="12" stroke-linecap="round"/><path d="M${560 - 330} 1240 L${560 - 330} 1300 M${560 + 330} 1240 L${560 + 330} 1300" stroke="#fff" stroke-width="12" stroke-linecap="round"/></g>` + big(540, 1380, '1 M+', t, tm, { size: 120, fill: K.yellow, stroke: N, sw: 12 }); }
  s += baby(bx - 20, 1000, sc, t, sm(tt - 0.2, tt + 0.2, t));
  if (t > tt - 0.1 && t < ts + 0.4) { const k = pop(tt - 0.1, t) * (1 - sm(ts, ts + 0.4, t)), g = sharkSolid('#fff', N, 2) + `<path d="M860 236 Q920 264 978 228" fill="#3a0f1e" stroke="${N}" stroke-width="2"/>` + Array.from({ length: 8 }, (_, i) => `<path d="M${868 + i * 13} ${f1(236 - i * 0.6)} l6 10 l6 -10Z" fill="#fff" stroke="${N}" stroke-width="1"/>`).join('');
    s += `<g transform="translate(540 1340) scale(${f1(k * 100) / 100}) translate(-540 -1340)"><defs><clipPath id="mg13"><circle cx="540" cy="1340" r="210"/></clipPath></defs><circle cx="540" cy="1340" r="230" fill="${N}"/><g clip-path="url(#mg13)"><rect x="300" y="1100" width="480" height="480" fill="#9fd0f0"/>${place(-750, 1287, 3.0, g)}</g></g>`; }
  if (t < to) s += big(540, 640, 'FULL SET', t, tt, { size: 110, stroke: N, sw: 14 }) + big(540, 760, 'OF TEETH', t, tt + 0.2, { size: 110, fill: K.yellow, stroke: N, sw: 14 });
  else { s += big(540, 660, 'ON ITS OWN!', t, to, { size: 120, fill: K.yellow, stroke: N, sw: 14 });
    s += big(540, 1400, 'NO PARENTS', t, at('n26', 'No parents'), { size: 100, stroke: N, sw: 14 }) + big(540, 1540, 'NO LESSONS', t, at('n26', 'No lessons'), { size: 100, stroke: N, sw: 14 }); }
  return s; };

// ───────── s14 NICOLE'S TRIP ─────────
const MS = 0.72, MX = 540 - (268 + 1516) / 2 * MS, MY = 1000 - (756 + 558) / 2 * MS - 30;
const mapV = (t, ko, kb) => { const dr = (d, k, c) => k <= 0 ? '' : `<path d="${d}" pathLength="1" stroke="${c}" stroke-width="${f1(16 / MS)}" fill="none" stroke-linecap="round" stroke-dasharray="${f1(k * 1000) / 1000} 2"/>`;
  let s = `<defs><clipPath id="cm14"><rect x="0" y="470" width="${W}" height="1170" rx="0"/></clipPath></defs><g clip-path="url(#cm14)"><g transform="translate(${f1(MX)} ${f1(MY)}) scale(${MS})"><path d="${MAP.land}" fill="${K.sand}" stroke="${N}" stroke-width="5" stroke-linejoin="round"/>${dr(MAP.out, ko, '#fff')}${dr(MAP.back, kb, K.yellow)}</g></g><path d="M0 470 L${W} 470 M0 1640 L${W} 1640" stroke="#fff" stroke-width="6" opacity=".6"/>`;
  const P = ([x, y]) => [MX + x * MS, MY + y * MS], [sx, sy] = P(MAP.sa), [ax, ay] = P(MAP.au);
  s += `<circle cx="${f1(sx)}" cy="${f1(sy)}" r="22" fill="${K.red}" stroke="#fff" stroke-width="7"/>`; if (ko > 0.97) s += `<circle cx="${f1(ax)}" cy="${f1(ay)}" r="22" fill="${K.red}" stroke="#fff" stroke-width="7"/>`;
  return { s, sx, sy, ax, ay }; };
const s14h = t => { const tk = hat('s14', 'twenty'), m = mapV(t, eo(0, 1.6, t), eo(1.4, 3.0, t));
  let s = m.s + tag(m.sx, m.sy, 300, 1200, 'NICOLE', t, -1, { col: K.yellow, size: 84 });
  s += `<rect x="190" y="1380" width="700" height="170" rx="40" fill="${N}" opacity=".88"/>` + big(540, 1500, (t < tk ? '0' : count(20000, t, tk, 1.0)) + ' KM', t, -1, { size: 110, stroke: N, sw: 0 });
  return s; };
const s14a = t => { const to = at('n13', 'She swam'), tb = at('n13', 'and back again'), tk = at('n13', 'About twenty'), m = mapV(t, eo(to, to + 2.6, t), eo(tb, tb + 2.4, t));
  let s = m.s + (t < tk - 0.1 ? tag(m.sx, m.sy, 300, 1200, 'NICOLE', t, at('n13', 'Nicole'), { col: K.yellow, size: 84 }) : '');
  s += tag(m.sx, m.sy, 300, 620, 'SOUTH AFRICA', t, at('n13', 'South Africa'), { size: 60 }) + tag(m.ax, m.ay, 780, 620, 'AUSTRALIA', t, at('n13', 'Australia'), { size: 60 });
  if (t > at('n13', 'tracker') - 0.1 && t < tk) { const k = pop(at('n13', 'tracker') - 0.1, t); s += `<g transform="translate(800 1480) scale(${f1(k * 100) / 100})"><rect x="-70" y="-40" width="140" height="80" rx="16" fill="#fff" stroke="${N}" stroke-width="7"/><path d="M0 -40 L0 -110" stroke="${N}" stroke-width="7"/><circle cy="-115" r="12" fill="${K.red}"/>${ring(0, -115, t, '#fff')}</g>` + big(800, 1620, 'TRACKER', t, at('n13', 'tracker'), { size: 60, stroke: N, sw: 10 }); }
  if (t > tk - 0.1) s += `<rect x="140" y="1330" width="800" height="300" rx="40" fill="${N}" opacity="${f1(0.88 * sm(tk - 0.1, tk + 0.2, t))}"/>` + big(540, 1460, count(20000, t, tk, 1.2) + ' KM', t, tk, { size: 120 }) + big(540, 1580, 'IN UNDER 9 MONTHS', t, at('n13', 'nine months'), { size: 66, fill: K.yellow });
  return s; };

export const VS = { s01: [s01h, s01a, s01b], s02: [s02h, s02a, s02b], s03: [s03h, s03a], s04: [s04h, s04a, s04b], s05: [s05h, s05a, s05b], s06: [s06h, s06a], s07: [s07h, s07a, s07b], s08: [s08h, s08a], s09: [s09h, s09a], s10: [s10h, s10a], s11: [s11h, s11a], s12: [s12h, s12a], s13: [s13h, s13a], s14: [s14h, s14a] };

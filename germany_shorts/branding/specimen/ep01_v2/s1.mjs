import { K, W, H, f1, clamp, sm, eo, pop, lerp, seed, rnd, big, tag, place, toScr, sharkSolid, sharkInside, sharkXray, sharkOpen, bob, PT, icon, ICON, cross, count, SHARK } from './eng2.mjs';
import { at } from './tl2.mjs';

// 01 opened shark, frame 0 complete
export function n01(t) {
  const cx = 960, cy = 560, sc = 1.42, y = cy + bob(t), T = at('n01', 'Today'), cut = lerp(812, 1000, eo(T, T + 1.6, t));
  let s = `<g transform="translate(${f1(cx - 520 * sc)} ${f1(y - 215 * sc)}) scale(${sc})">${sharkOpen(0, 0, 1, { cut, id: 'o1', skin: '#ffffff', stroke: K.navy, sw: 5.5 })}</g>`;
  const P = n => toScr(cx, y, sc, ...PT[n]);
  s += tag(...P('spine'), 700, 170, 'SPINE', t, -1) + tag(...P('liver'), 760, 960, 'LIVER', t, -1, { col: K.yellow }) + tag(...P('heart'), 1330, 960, 'HEART', t, -1, { col: K.red, txt: '#fff' });
  const q = at('n01', 'wondered');
  s += big(1560, 230, '?', t, q, { size: 260, fill: K.yellow, stroke: K.navy, sw: 10 });
  return s;
}

// 02 size: 6 m vs a car, 2 tons vs a rhino
export function n02(t) {
  const tw = at('n02', 'And it can weigh');
  let s = '';
  if (t < tw - 0.15) {
    const sc = 1.5, cx = 960, cy = 360;
    s += place(cx, cy + bob(t, 5), sc, sharkSolid('#ffffff', K.navy, 6));
    const x0 = cx - 485 * sc, x1 = cx + 485 * sc, ry = 650, rk = eo(at('n02', 'six meters'), at('n02', 'six meters') + 0.8, t);
    s += `<path d="M${f1(x0)} ${ry} L${f1(lerp(x0, x1, rk))} ${ry}" stroke="#fff" stroke-width="10" stroke-linecap="round"/>`;
    if (rk > 0) s += `<path d="M${f1(x0)} ${ry - 26} L${f1(x0)} ${ry + 26} M${f1(lerp(x0, x1, rk))} ${ry - 26} L${f1(lerp(x0, x1, rk))} ${ry + 26}" stroke="#fff" stroke-width="10" stroke-linecap="round"/>`;
    s += big((x0 + x1) / 2, ry + 95, '6 M', t, at('n02', 'six meters') + 0.5, { size: 120, fill: K.navy, stroke: '#fff', sw: 18 });
    const tc = at('n02', 'car'), carW = 4.5 / 6 * (x1 - x0), cs = carW / 470;
    s += icon('car', x0 + carW / 2, 900, cs * 0.8, t, tc);
    s += big(x0 + carW + 230, 900, 'CAR', t, tc + 0.2, { size: 110 });
  } else {
    // seesaw
    const cx = 960, py = 760, ang = 6 * Math.exp(-(t - tw) * 1.6) * Math.cos((t - tw) * 5);
    s += `<path d="M${cx - 90} ${py + 170} L${cx} ${py} L${cx + 90} ${py + 170}Z" fill="${K.navy}"/>`;
    s += `<g transform="rotate(${f1(ang)} ${cx} ${py})"><rect x="${cx - 760}" y="${py - 22}" width="1520" height="34" rx="17" fill="#fff" stroke="${K.navy}" stroke-width="7"/>
      ${place(cx - 420, py - 120, 0.62, sharkSolid('#ffffff', K.navy, 10))}<g transform="translate(${cx + 430} ${py - 115}) scale(1.25)">${ICON.rhino()}</g></g>`;
    s += big(cx, 230, '2 TONS', t, at('n02', 'two tons'), { size: 190 });
    s += tag(cx + 430, py - 210, cx + 430, 420, 'RHINO', t, at('n02', 'rhino'), { line: false });
  }
  return s;
}

// 03 zero bones → cartilage → your nose and ears
export function n03(t) {
  const tn = at('n03', "That's the same");
  let s = '';
  if (t < tn - 0.15) {
    const cx = 960, cy = 610, sc = 1.38;
    s += place(cx, cy + bob(t), sc, sharkXray(5));
    s += big(cx, 210, '0 BONES', t, at('n03', 'zero bones'), { size: 200 });
    s += tag(...toScr(cx, cy, sc, ...PT.spine), 1180, 960, 'CARTILAGE', t, at('n03', 'cartilage'), { col: K.navy, txt: '#fff' });
  } else {
    const hx = 960, hy = 560, hs = 2.3, tw = at('n03', 'wiggle'), wig = t > tw ? 9 * Math.sin((t - tw) * 22) * Math.exp(-(t - tw) * 0.9) : 0;
    s += `<g transform="translate(${hx} ${hy}) scale(${hs})">${ICON.head()}<g transform="rotate(${f1(wig)} -40 -40)"><ellipse cx="-40" cy="-40" rx="26" ry="40" fill="#ffc29a" stroke="${K.navy}" stroke-width="7"/><path d="M-44 -62 Q-28 -40 -44 -18" stroke="${K.navy}" stroke-width="5" fill="none"/></g></g>`;
    s += tag(hx + 145 * hs, hy + 0 * hs, 1640, 380, 'NOSE', t, at('n03', 'nose'), { col: K.yellow });
    s += tag(hx - 40 * hs, hy - 40 * hs, 360, 300, 'EAR', t, at('n03', 'ears'), { col: K.yellow });
    s += big(960, 960, 'CARTILAGE', t, tn, { size: 130, fill: K.navy, stroke: '#fff', sw: 16 });
  }
  return s;
}

// 04 light + bendy: the shark makes a tight U-turn
export function n04(t) {
  const u = ((t * 0.3) % 1), a = Math.PI * 2 * u, R = 260, cx = 960, cy = 500;
  let s = `<circle cx="${cx}" cy="${cy}" r="${R}" fill="none" stroke="#fff" stroke-width="6" stroke-dasharray="4 26" stroke-linecap="round" opacity=".6"/>`;
  const x = cx + Math.cos(a) * R, y = cy + Math.sin(a) * R, rot = a * 180 / Math.PI + 90;
  s += place(x, y, 0.62, sharkSolid('#ffffff', K.navy, 11), { rot });
  s += big(330, 250, 'LIGHT', t, at('n04', 'lighter'), { size: 150, fill: K.yellow, stroke: K.navy, sw: 14 });
  s += big(1590, 250, 'BENDY', t, at('n04', 'bend'), { size: 150, fill: K.yellow, stroke: K.navy, sw: 14, rot: -6 });
  s += big(960, 1010, 'FAST TURNS', t, at('n04', 'turn quickly'), { size: 110 });
  return s;
}

// 05 backbone rings like a tree → 70+ years
export function n05(t) {
  const cx = 640, cy = 560, R = 280, tr = at('n05', 'It grows rings');
  let s = `<circle cx="${cx}" cy="${cy}" r="${R}" fill="#f4ecdc" stroke="${K.navy}" stroke-width="10"/><circle cx="${cx}" cy="${cy}" r="${R * 0.16}" fill="${K.navy}" opacity=".85"/>`;
  for (let i = 1; i <= 9; i++) { const k = sm(tr + i * 0.12, tr + i * 0.12 + 0.2, t); if (k > 0) s += `<circle cx="${cx}" cy="${cy}" r="${f1(R * 0.16 + R * 0.82 * i / 9.6)}" fill="none" stroke="#b08a5a" stroke-width="7" opacity="${f1(k)}"/>`; }
  s += tag(cx, cy - R, cx, 150, 'BACKBONE', t, -1, { col: '#fff' });
  const tt = at('n05', 'tree');
  if (t > tt) { const k = pop(tt, t); s += `<g transform="translate(1380 420) scale(${f1(k * 0.85)})"><path d="M-180 120 L-150 -60 L150 -60 L180 120Z" fill="#8a5a2b" stroke="${K.navy}" stroke-width="8"/><ellipse cx="0" cy="-60" rx="150" ry="58" fill="#e8c48e" stroke="${K.navy}" stroke-width="8"/>
      ${[0.25, 0.5, 0.75].map(r => `<ellipse cx="0" cy="-60" rx="${150 * r}" ry="${58 * r}" fill="none" stroke="#b08a5a" stroke-width="6"/>`).join('')}</g>`; }
  const ty = at('n05', 'seventy');
  if (t > at('n05', 'Scientists count') - 0.1) s += big(1380, 780, t > ty ? '70+' : count(70, t, at('n05', 'Scientists count'), ty - at('n05', 'Scientists count')), t, at('n05', 'Scientists count'), { size: 230, fill: '#fff', stroke: K.navy, sw: 16 });
  s += big(1380, 960, 'YEARS', t, ty + 0.2, { size: 110, fill: K.yellow, stroke: K.navy, sw: 12 });
  return s;
}

// 06 skin: smooth one way, rough the other → denticles
const dent = (x, y, s) => `<g transform="translate(${f1(x)} ${f1(y)}) scale(${s})"><path d="M-30 -22 C-8 -30 20 -22 36 0 C20 22 -8 30 -30 22 C-22 8 -22 -8 -30 -22Z" fill="#dfe6f0" stroke="${K.navy}" stroke-width="3"/><path d="M-18 -10 L24 -3 M-18 10 L24 3" stroke="#8a97ad" stroke-width="3"/></g>`;
export function n06(t) {
  const tb = at('n06', 'Because'); let s = '';
  if (t < tb - 0.15) {
    const cx = 960, cy = 520, sc = 1.45;
    s += place(cx, cy + bob(t, 4), sc, sharkSolid('#dfe6f0', K.navy, 6));
    const t1 = at('n06', 'Stroke a shark'), t2 = at('n06', 'Stroke it the other');
    const ax0 = cx + 380 * sc, ax1 = cx - 380 * sc, ay = cy - 30;
    if (t > t1 && t < t2) { const k = eo(t1, t1 + 1.4, t); s += `<path d="M${f1(ax0)} ${ay} L${f1(lerp(ax0, ax1, k))} ${ay}" stroke="${K.green}" stroke-width="26" stroke-linecap="round"/><path d="M${f1(lerp(ax0, ax1, k) - 40)} ${ay} l60 -45 l0 90Z" fill="${K.green}"/>`;
      s += big(960, 900, 'SMOOTH', t, at('n06', 'smooth'), { size: 160, fill: K.green, stroke: K.navy, sw: 14 }); }
    if (t >= t2) { const k = eo(t2, t2 + 1.4, t), jit = 4 * Math.sin(t * 60); s += `<path d="M${f1(ax1)} ${ay + jit} L${f1(lerp(ax1, ax0, k))} ${ay - jit}" stroke="${K.red}" stroke-width="26" stroke-linecap="round"/><path d="M${f1(lerp(ax1, ax0, k) + 40)} ${ay} l-60 -45 l0 90Z" fill="${K.red}"/>`;
      s += big(960, 900, 'ROUGH!', t, at('n06', 'sandpaper'), { size: 160, fill: K.red, stroke: K.navy, sw: 14 }); }
  } else {
    const cx = 760, cy = 540, R = 380, z = 0.8 + 0.35 * eo(tb, tb + 2, t);
    s += `<defs><clipPath id="mg6"><circle cx="${cx}" cy="${cy}" r="${R}"/></clipPath></defs><circle cx="${cx}" cy="${cy}" r="${R + 22}" fill="${K.navy}"/><g clip-path="url(#mg6)"><rect x="${cx - R}" y="${cy - R}" width="${2 * R}" height="${2 * R}" fill="#9fb3cc"/><g transform="translate(${cx} ${cy}) scale(${f1(z * 100) / 100})">`;
    for (let r = -6; r <= 6; r++) for (let c = -7; c <= 7; c++) s += dent(c * 74 + (r % 2 ? 37 : 0), r * 54, 1.25);
    const tf = at('n06', 'slide through');
    if (t > tf - 0.3) for (let i = 0; i < 7; i++) { const y = -270 + i * 90, ph = ((t - tf) * 360 + i * 90) % 900 - 450; s += `<path d="M${f1(ph - 140)} ${y} L${f1(ph + 140)} ${y}" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity="${f1(sm(tf - 0.3, tf + 0.2, t))}"/>`; }
    s += `</g></g><path d="M${cx + R * 0.7} ${cy + R * 0.7} L${cx + R * 1.05} ${cy + R * 1.05}" stroke="${K.navy}" stroke-width="44" stroke-linecap="round"/>`;
    s += tag(cx + 120, cy - 60, 1480, 300, 'DENTICLES', t, at('n06', 'denticles'), { col: K.yellow });
    s += big(1480, 620, 'TINY', t, at('n06', 'tiny scales'), { size: 130 }) + big(1480, 770, 'TEETH!', t, at('n06', 'little teeth'), { size: 150, fill: K.yellow, stroke: K.navy, sw: 14 });
  }
  return s;
}

// 07 300 teeth in rows → conveyor belt
const tooth = (x, y, s, rot = 0, c = '#fff') => `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(rot)}) scale(${f1(s * 100) / 100})"><path d="M-30 0 L-4 -80 L4 -80 L30 0Z" fill="${c}" stroke="${K.navy}" stroke-width="5" stroke-linejoin="round"/></g>`;
export function n07(t) {
  const tf = at('n07', 'When a front'); let s = '';
  if (t < tf - 0.15) {
    const cx = 960, cy = 560, open = eo(at('n07', 'open the mouth'), at('n07', 'open the mouth') + 0.8, t);
    const ry = 60 + 260 * open;
    s += `<ellipse cx="${cx}" cy="${cy}" rx="560" ry="${f1(ry + 70)}" fill="#e88f9b" stroke="${K.navy}" stroke-width="10"/><ellipse cx="${cx}" cy="${cy}" rx="470" ry="${f1(ry)}" fill="#3a0f1e"/>`;
    const tr = at('n07', 'lined up in rows');
    for (let row = 2; row >= 0; row--) { const rk = row === 0 ? 1 : sm(tr + row * 0.3, tr + row * 0.3 + 0.4, t); if (rk <= 0) continue; const sc = 1 - row * 0.22, rx = 470 - row * 60, rr = ry - row * 30;
      for (let i = 0; i < 13; i++) { const a = Math.PI * (0.08 + 0.84 * i / 12), x = cx - Math.cos(a) * rx, y = cy - Math.sin(a) * rr * 0.92;
        s += tooth(x, y + 0, sc * 1.1, 180 - (a * 180 / Math.PI - 90) * 0.6 + 180, row ? '#e9e2d4' : '#fff');
        const yb = cy + Math.sin(a) * rr * 0.92; s += tooth(x, yb, sc, (a * 180 / Math.PI - 90) * 0.6, row ? '#e9e2d4' : '#fff'); } }
    s += big(cx, 130, count(300, t, at('n07', 'three hundred'), 0.9) ? '≈' + count(300, t, at('n07', 'three hundred'), 0.9) + ' TEETH' : '', t, at('n07', 'three hundred'), { size: 130, stroke: K.navy, sw: 14 });
    s += tag(cx - 300, cy - ry * 0.55, 240, 980, 'ROWS', t, tr + 0.6, { col: K.yellow });
  } else {
    // conveyor: jaw cross-section arc, teeth roll forward, front tooth drops
    const cx = 720, cy = 900, R = 520;
    s += `<path d="M${cx - R - 50} ${cy} A${R + 50} ${R + 50} 0 0 1 ${cx + R + 50} ${cy}" fill="none" stroke="#e88f9b" stroke-width="130"/><path d="M${cx - R - 50} ${cy} A${R + 50} ${R + 50} 0 0 1 ${cx + R + 50} ${cy}" fill="none" stroke="${K.navy}" stroke-width="8"/>`;
    const N = 6, sp = 0.05 + 0.18 * sm(tf, tf + 1, t);
    for (let i = 0; i < N; i++) { let u = ((i / N) + (t - tf) * sp) % 1; if (u < 0) u += 1;
      const ang = Math.PI * (0.94 - 0.84 * u), x = cx + Math.cos(ang) * R, y = cy - Math.sin(ang) * R, fall = u > 0.93 ? (u - 0.93) / 0.07 : 0, fold = (1 - u) * 75;
      s += `<g opacity="${f1(1 - fall)}">${tooth(x, y + fall * 160, 0.9 + 1.0 * u, -(ang * 180 / Math.PI - 90) - fold + fall * 50)}</g>`; }
    s += tag(cx + Math.cos(Math.PI * 0.12) * R, cy - Math.sin(Math.PI * 0.12) * R - 120, 1620, 200, 'FRONT', t, tf + 0.3, { col: '#fff' });
    s += tag(cx + Math.cos(Math.PI * 0.85) * R - 20, cy - Math.sin(Math.PI * 0.85) * R - 60, 300, 220, 'NEW', t, at('n07', 'the one behind'), { col: K.green, txt: '#fff' });
    s += big(1640, 560, 'CONVEYOR', t, at('n07', 'conveyor belt'), { size: 100, fill: K.yellow, stroke: K.navy, sw: 14 }) + big(1640, 680, 'BELT', t, at('n07', 'conveyor belt') + 0.25, { size: 100, fill: K.yellow, stroke: K.navy, sw: 14 });
  }
  return s;
}

// 07b top teeth cut, bottom teeth hold, no chewing
export function n07b(t) {
  const tc = at('n07b', "And sharks don't chew");
  let s = '';
  const k1 = pop(at('n07b', 'The top teeth'), t), k2 = pop(at('n07b', 'The bottom teeth'), t);
  const fade = 1 - 0.65 * sm(tc - 0.2, tc + 0.3, t);
  if (k1 > 0) { let ser = ''; for (let i = 1; i < 9; i++) { const u = i / 9; ser += `<path d="M${f1(-150 + 140 * u)} ${f1(-300 * u)} l-16 -6 M${f1(150 - 140 * u)} ${f1(-300 * u)} l16 -6" stroke="${K.navy}" stroke-width="6"/>`; }
    s += `<g opacity="${f1(fade)}" transform="translate(560 680) scale(${f1(k1 * 1.15)})"><path d="M-150 0 L-10 -300 L10 -300 L150 0Z" fill="#fff" stroke="${K.navy}" stroke-width="9" stroke-linejoin="round"/>${ser}</g>`; }
  if (k2 > 0) s += `<g opacity="${f1(fade)}" transform="translate(1360 680) scale(${f1(k2 * 1.15)})"><path d="M-70 0 L-6 -320 L6 -320 L70 0Z" fill="#fff" stroke="${K.navy}" stroke-width="9" stroke-linejoin="round"/></g>`;
  s += big(560, 830, 'TOP', t, at('n07b', 'The top teeth'), { size: 90 }) + big(1360, 830, 'BOTTOM', t, at('n07b', 'The bottom teeth'), { size: 90 });
  s += tag(560, 450, 560, 170, 'CUT', t, at('n07b', 'for cutting'), { col: K.red, txt: '#fff', line: false }) + tag(1360, 450, 1360, 170, 'HOLD', t, at('n07b', 'for holding'), { col: K.yellow, line: false });
  if (t > tc) s += `<rect x="0" y="380" width="${W}" height="320" fill="${K.navy}" opacity="${f1(0.75 * sm(tc, tc + 0.2, t))}"/>` + big(960, 540, 'NO CHEWING!', t, tc + 0.1, { size: 170, fill: K.yellow });
  return s;
}

// 08 thousands of teeth → fossils
export function n08(t) {
  let s = ''; seed(8);
  for (let i = 0; i < 70; i++) { const x = 160 + rnd() * 1600, t0 = 0.2 + rnd() * 3.5, rot = rnd() * 360, pile = 900 - Math.floor(rnd() * 5) * 34 - (Math.abs(x - 960) < 500 ? rnd() * 90 : 0);
    const k = clamp((t - t0) / 0.7), y = lerp(-80, pile, k * k); if (t > t0) s += tooth(x, y, 0.75, rot * (1 - k) + (k >= 1 ? (rnd() * 40 - 20) : 0)); }
  const tf = at('n08', 'fossils');
  if (t < tf) s += big(960, 330, 'THOUSANDS', t, at('n08', 'thousands'), { size: 180, stroke: K.navy, sw: 14 });
  if (t > tf) { const k = pop(tf, t); s += `<rect width="${W}" height="${H}" fill="${K.navy}" opacity="${f1(0.55 * sm(tf, tf + 0.3, t))}"/><g transform="translate(960 660) scale(${f1(k * 2.0)})"><path d="M-110 0 L-10 -220 L10 -220 L110 0 Q0 30 -110 0Z" fill="#a8835a" stroke="${K.navy}" stroke-width="6"/><path d="M-60 -40 L40 -120" stroke="#7a5a38" stroke-width="5"/></g>`;
    s += big(960, 900, 'FOSSIL', t, tf + 0.3, { size: 150, fill: K.yellow, stroke: K.navy, sw: 14 }); }
  return s;
}

// 09 bite force: you vs shark
export function n09(t) {
  const tm = at('n09', 'computer model'), te = at('n09', 'eighteen thousand'), th = at('n09', 'A strong human'), tx = at('n09', 'eighteen times');
  let s = '';
  if (t < te - 0.3) {
    // jaw wireframe being tested
    const k = sm(tm - 0.2, tm + 0.6, t), cl = 0.5 + 0.5 * Math.sin(t * 3);
    s += big(960, 230, 'HOW STRONG?', t, 0.3, { size: 150 });
    s += `<g opacity="${f1(Math.max(0.25, k))}" transform="translate(960 640)">`;
    for (let j = 0; j < 2; j++) { const sgn = j ? 1 : -1, off = sgn * (40 + 60 * cl); let g = '';
      for (let i = 0; i < 14; i++) { const x = -420 + i * 60; g += `<path d="M${x} ${off} L${x + 30} ${off + sgn * 70} L${x + 60} ${off}" fill="none" stroke="#fff" stroke-width="5"/>`; }
      s += `<path d="M-460 ${off} Q0 ${off + sgn * 200} 460 ${off}" fill="none" stroke="${K.cyan}" stroke-width="8"/>${g}`; }
    s += `</g>`;
  } else {
    const base = 930, scale = 680 / 18000, xs = 1220, xh = 620, bw = 300;
    const hs = 18000 * eo(te - 0.3, te + 1.4, t), hh = 1000 * eo(th, th + 0.6, t);
    s += `<path d="M300 ${base} L1620 ${base}" stroke="#fff" stroke-width="10" stroke-linecap="round"/>`;
    s += `<rect x="${xs - bw / 2}" y="${f1(base - hs * scale)}" width="${bw}" height="${f1(hs * scale)}" rx="16" fill="${K.red}" stroke="${K.navy}" stroke-width="8"/>`;
    s += big(xs, base - hs * scale - 70, Math.round(hs / 100) * 100 >= 18000 ? '18,000' : Math.round(hs).toLocaleString('en-US'), t, te - 0.3, { size: 100 });
    s += big(xs, base + 70, 'SHARK', t, te - 0.3, { size: 80, fill: K.navy, stroke: '#fff', sw: 10 });
    if (t > th) { s += `<rect x="${xh - bw / 2}" y="${f1(base - Math.max(hh * scale, 2))}" width="${bw}" height="${f1(Math.max(hh * scale, 2))}" rx="12" fill="#fff" stroke="${K.navy}" stroke-width="8"/>`;
      s += big(xh, base - hh * scale - 70, Math.round(hh).toLocaleString('en-US'), t, th, { size: 100 }) + big(xh, base + 70, 'YOU', t, th, { size: 80, fill: K.navy, stroke: '#fff', sw: 10 }); }
    s += big(560, 320, '×18', t, tx, { size: 260, fill: K.yellow, stroke: K.navy, sw: 18 });
  }
  return s;
}
